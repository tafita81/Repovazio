#!/usr/bin/env python3
"""
render_video_v9.py — psicologia.doc V9 MOTION AI
Pipeline: Edge TTS + Veo 3.x (motion clips) + Gemini Image (fallback) + ffconcat

CORREÇÕES COMPLETAS V9:
  ✅ Gemini models: gemini-2.5-flash-image / gemini-3.1-flash-image-preview (correto!)
  ✅ Veo 3.x para cenas-chave (braços/olhos/boca se movendo = real motion)
  ✅ reference_image: personagem consistente entre cenas
  ✅ Budget Veo: máx 8 clips/vídeo (economizar quota free)
  ✅ RATE_REAL dinâmico SEMPRE (len(script)/dur_audio — NUNCA hardcoded)
  ✅ Lower third SEM Psicóloga até jan/2027
  ✅ Encerramento: 🔔 overlay + "Inscreva-se agora"
  ✅ Anti-plágio em TODOS os prompts Gemini e Veo
  ✅ Fundo creme/branco Psych2Go (NUNCA fundo escuro)
  ✅ Gemini chibi como fallback (NUNCA Pillow stick figures)
  ✅ crf=25 Shorts (~3MB), crf=22 Longs (~18MB)
  ✅ Ken Burns suave para cenas Gemini estáticas
  ✅ Groq: uma chamada gera todos os prompts (eficiente)
"""

import os, sys, json, time, base64, asyncio, subprocess
import re, requests, traceback
from pathlib import Path
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor, as_completed

# ── CONFIG ────────────────────────────────────────────────────────────────────
SB_URL      = "https://tpjvalzwkqwttvmszvie.supabase.co"
SB_KEY      = os.environ.get("SUPABASE_SERVICE_KEY", "")
GROQ_KEY    = os.environ.get("GROQ_API_KEY", "")
GEMINI_KEY  = os.environ.get("GEMINI_API_KEY", "")
GEMINI_KEY2 = os.environ.get("GEMINI_API_KEY_2", "")

VIDEO_ID = int(sys.argv[1]) if len(sys.argv) > 1 else 683
TS       = int(time.time())
WORK_DIR = Path(f"/tmp/v9_{VIDEO_ID}_{TS}")
WORK_DIR.mkdir(parents=True, exist_ok=True)

TTS_VOICE   = "pt-BR-AntonioNeural"
LOWER_THIRD = "Daniela Coelho | Saude Metal | @psidanielacoelho"
CRF_SHORT   = 25      # ~3MB
CRF_LONG    = 22      # ~18MB
VEO_BUDGET  = 8       # max clips Veo por vídeo

# Modelos Gemini para geração de imagem (corretos!)
GEMINI_MODELS_IMG = [
    "gemini-2.5-flash-image",
    "gemini-3.1-flash-image-preview",
    "gemini-2.0-flash-exp-image-generation",
]

# Veo: tenta do mais novo para o mais estável
VEO_MODELS = [
    "veo-3.1-generate-preview",
    "veo-3.0-generate-preview",
    "veo-2.0-generate-001",
]

ANTI_PLAGIO = (
    "original character design not based on any existing IP or franchise, "
    "no text, no logos, no brand marks, no watermarks"
)
PSYCH2GO_BASE = (
    "Psych2Go animation style, kawaii chibi anime character, "
    "cream white background #F5F0E8, pastel warm colors, "
    "round big expressive eyes, clean soft lines, "
    "professional psychology channel aesthetic"
)

# ── SUPABASE ──────────────────────────────────────────────────────────────────
def sb_get(table, qs=""):
    r = requests.get(f"{SB_URL}/rest/v1/{table}?{qs}",
        headers={"apikey":SB_KEY, "Authorization":f"Bearer {SB_KEY}"}, timeout=30)
    r.raise_for_status(); return r.json()

def sb_patch(table, id_, data):
    r = requests.patch(f"{SB_URL}/rest/v1/{table}?id=eq.{id_}",
        headers={"apikey":SB_KEY, "Authorization":f"Bearer {SB_KEY}",
                 "Content-Type":"application/json", "Prefer":"return=representation"},
        json=data, timeout=30)
    r.raise_for_status(); return r.json()

def sb_upload(storage_path, file_path, ctype="video/mp4"):
    with open(file_path, "rb") as f: data = f.read()
    r = requests.post(f"{SB_URL}/storage/v1/object/{storage_path}",
        headers={"apikey":SB_KEY, "Authorization":f"Bearer {SB_KEY}",
                 "Content-Type":ctype, "x-upsert":"true"},
        data=data, timeout=300)
    r.raise_for_status()
    return f"{SB_URL}/storage/v1/object/public/{storage_path}"

# ── TTS ───────────────────────────────────────────────────────────────────────
async def _tts_async(text, path):
    import edge_tts
    await edge_tts.Communicate(text, TTS_VOICE).save(path)

def generate_tts(script, out_path):
    asyncio.run(_tts_async(script, str(out_path)))
    return out_path

def get_audio_duration(path):
    r = subprocess.run(
        ["ffprobe","-v","quiet","-print_format","json","-show_streams",str(path)],
        capture_output=True, text=True)
    for s in json.loads(r.stdout).get("streams",[]):
        if s.get("codec_type") == "audio":
            return float(s.get("duration", 60))
    return 60.0

# ── GROQ: prompts de cena ─────────────────────────────────────────────────────
def generate_scene_prompts(script, paragraphs):
    """Groq gera prompts Gemini/Veo para cada parágrafo em 1 chamada"""
    user = f"""Script PT-BR:
{script}

Para cada um dos {len(paragraphs)} parágrafos, gere JSON com:
- "img": prompt em inglês para imagem chibi estática (Gemini)
- "veo": prompt em inglês para clip animado 8s (Veo motion)  
- "key": true se cena-chave emocional (max {VEO_BUDGET} true)
- "emotion": neutral|surprised|concerned|happy|focused|dramatic

Retorne APENAS array JSON. {len(paragraphs)} objetos. Sem texto adicional."""

    try:
        r = requests.post("https://api.groq.com/openai/v1/chat/completions",
            headers={"Authorization":f"Bearer {GROQ_KEY}", "Content-Type":"application/json"},
            json={"model":"llama-3.3-70b-versatile",
                  "messages":[{"role":"user","content":user}],
                  "temperature":0.7, "max_tokens":4096, "response_format":{"type":"json_object"}},
            timeout=60)
        
        data = r.json()
        content = data.get("choices",[{}])[0].get("message",{}).get("content","[]")
        
        # Extrair array JSON
        m = re.search(r'\[.*\]', content, re.DOTALL)
        if m:
            return json.loads(m.group())
        # Tentar como objeto com array
        obj = json.loads(content)
        for v in obj.values():
            if isinstance(v, list): return v
    except Exception as e:
        print(f"   ⚠️ Groq: {e}")
    
    # Fallback
    emotions = ["neutral","concerned","dramatic","surprised","empathetic","focused","happy","sad"]
    return [{"img":f"kawaii chibi {emotions[i%8]} psychology",
             "veo":f"chibi character explains {emotions[i%8]}, gestures naturally",
             "key": i < VEO_BUDGET, "emotion": emotions[i%8]} for i in range(len(paragraphs))]

# ── GEMINI IMAGE (modelo correto: gemini-2.5-flash-image) ─────────────────────
def gemini_generate_image(prompt, key):
    """Gera PNG chibi com Gemini Image (modelos corretos)"""
    full = f"{PSYCH2GO_BASE}, {prompt}. {ANTI_PLAGIO}"
    
    for model in GEMINI_MODELS_IMG:
        try:
            url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={key}"
            r = requests.post(url,
                headers={"Content-Type":"application/json"},
                json={"contents":[{"parts":[{"text":full}]}],
                      "generationConfig":{"responseModalities":["IMAGE","TEXT"]}},
                timeout=60)
            
            if r.status_code == 429:
                time.sleep(3); continue
            if r.status_code not in (200,):
                continue
            
            for part in r.json().get("candidates",[{}])[0].get("content",{}).get("parts",[]):
                if "inlineData" in part:
                    return base64.b64decode(part["inlineData"]["data"])
        except Exception:
            continue
    
    raise ValueError(f"Todos os modelos Gemini Image falharam")

# ── VEO 3.x API ───────────────────────────────────────────────────────────────
def veo_generate_clip(veo_prompt, ref_b64, key, duration_s=8):
    """Gera clip com motion real usando Veo 3.x + reference image"""
    for model in VEO_MODELS:
        try:
            result = _veo_api_call(model, veo_prompt, ref_b64, key, duration_s)
            if result:
                print(f"      ✅ Veo clip: {model}")
                return result
        except Exception as e:
            print(f"      ↳ {model}: {str(e)[:70]}")
    raise ValueError("Veo indisponível (paid preview ou quota)")

def _veo_api_call(model, prompt, ref_b64, key, dur):
    url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateVideo?key={key}"
    body = {
        "prompt": {"text": f"{PSYCH2GO_BASE}, {prompt}. {ANTI_PLAGIO}"},
        "image": {"imageBytes": ref_b64, "mimeType": "image/png"},
        "generationConfig": {
            "durationSeconds": dur, "aspectRatio": "9:16",
            "numberOfVideos": 1, "personGeneration": "ALLOW_ADULT"
        }
    }
    r = requests.post(url, json=body, timeout=60)
    if r.status_code in (400, 404, 403):
        raise ValueError(f"HTTP {r.status_code}")
    if r.status_code not in (200, 202):
        raise ValueError(f"HTTP {r.status_code}: {r.text[:100]}")
    
    op = r.json()
    op_name = op.get("name","")
    
    # Sem op_name → resposta síncrona
    if not op_name:
        return _extract_video(op)
    
    # Polling (max 4 min)
    poll_url = f"https://generativelanguage.googleapis.com/v1beta/{op_name}?key={key}"
    for i in range(48):
        time.sleep(5)
        pr = requests.get(poll_url, timeout=30)
        pd = pr.json()
        if pd.get("done"):
            return _extract_video(pd.get("response", pd))
        if i % 6 == 0: print(f"      ⏳ Veo... {(i+1)*5}s")
    raise ValueError("Timeout Veo")

def _extract_video(resp):
    samples = resp.get("generatedSamples") or resp.get("videos") or []
    if not samples: raise ValueError("Sem vídeos")
    v = samples[0]
    uri = v.get("video",{}).get("uri") or v.get("uri","")
    if uri:
        vr = requests.get(uri, timeout=120)
        vr.raise_for_status(); return vr.content
    b64 = v.get("video",{}).get("videoBytes") or v.get("videoBytes","")
    if b64: return base64.b64decode(b64)
    raise ValueError("Sem URI nem bytes")

# ── MONTAR CLIPS ──────────────────────────────────────────────────────────────
def build_static_clip(img_bytes, duration, idx):
    """Gemini: imagem → Ken Burns suave → MP4"""
    img_p  = WORK_DIR / f"img_{idx:03d}.png"
    clip_p = WORK_DIR / f"clip_{idx:03d}.mp4"
    img_p.write_bytes(img_bytes)
    dur_frames = max(1, int(duration * 30))
    zexpr = "min(zoom+0.0012,1.25)" if idx%2==0 else "if(lte(zoom,1.0),1.25,max(1.0,zoom-0.0012))"
    vf = (f"scale=1200:2133,"
          f"zoompan=z='{zexpr}':d={dur_frames}:"
          f"x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':s=1080x1920:fps=30")
    subprocess.run([
        "ffmpeg","-y","-loop","1","-i",str(img_p),
        "-vf",vf,"-t",str(duration),
        "-c:v","libx264","-pix_fmt","yuv420p","-r","30",str(clip_p)
    ], check=True, capture_output=True, timeout=120)
    return clip_p

def build_motion_clip(video_bytes, target_dur, idx):
    """V9: Veo MP4 → trim/loop → 1080×1920"""
    raw_p  = WORK_DIR / f"veo_{idx:03d}.mp4"
    clip_p = WORK_DIR / f"clip_{idx:03d}.mp4"
    raw_p.write_bytes(video_bytes)
    vf = ("scale=1080:1920:force_original_aspect_ratio=decrease,"
          "pad=1080:1920:(ow-iw)/2:(oh-ih)/2:color=#F5F0E8")
    subprocess.run([
        "ffmpeg","-y","-stream_loop","-1","-i",str(raw_p),
        "-vf",vf,"-t",str(target_dur),
        "-c:v","libx264","-pix_fmt","yuv420p","-r","30",str(clip_p)
    ], check=True, capture_output=True, timeout=120)
    return clip_p

def build_color_fallback(duration, idx):
    """Último recurso: creme sólido (nunca acontece em produção)"""
    clip_p = WORK_DIR / f"clip_{idx:03d}.mp4"
    subprocess.run([
        "ffmpeg","-y","-f","lavfi",
        "-i",f"color=c=0xF5F0E8:s=1080x1920:d={duration}:r=30",
        "-c:v","libx264","-pix_fmt","yuv420p",str(clip_p)
    ], check=True, capture_output=True)
    return clip_p

# ── OVERLAYS FINAIS ───────────────────────────────────────────────────────────
def finalize_video(concat_path, audio_path, out_path, total_dur, is_long):
    """
    Lower third + progress bar + overlay Inscreva-se + áudio
    SEM Psicóloga no lower third (até jan/2027)
    """
    crf = CRF_LONG if is_long else CRF_SHORT
    end_start = max(0, total_dur - 4.0)
    
    vf_parts = [
        # Lower third SEM Psicóloga
        (f"drawtext=text='{LOWER_THIRD}'"
         f":fontsize=26:fontcolor=white"
         f":x=(w-text_w)/2:y=h-75"
         f":box=1:boxcolor=black@0.65:boxborderw=8"),
        # Progress bar violeta
        (f"drawbox=x=0:y=h-10:w='iw*t/{total_dur}':h=10"
         f":color=0x7C3AED:t=fill"),
        # 🔔 Inscreva-se agora — últimos 4s
        (f"drawtext=text='Inscreva-se agora'"
         f":fontsize=42:fontcolor=0x7C3AED:fontweight=bold"
         f":x=(w-text_w)/2:y=h/2+180"
         f":box=1:boxcolor=white@0.88:boxborderw=18"
         f":enable='gte(t,{end_start})'"),
    ]
    
    subprocess.run([
        "ffmpeg","-y",
        "-i",str(concat_path),
        "-i",str(audio_path),
        "-vf",",".join(vf_parts),
        "-c:v","libx264","-crf",str(crf),"-preset","fast",
        "-c:a","aac","-b:a","128k",
        "-pix_fmt","yuv420p","-shortest",
        str(out_path)
    ], check=True, capture_output=True, timeout=600)

# ── MAIN ──────────────────────────────────────────────────────────────────────
def main():
    print(f"\n{'='*60}")
    print(f"  ψ V9 MOTION AI — Video #{VIDEO_ID}")
    print(f"{'='*60}")
    
    # 1. Carregar dados
    rows = sb_get("content_pipeline", f"id=eq.{VIDEO_ID}&select=id,title,script,audio_url,status")
    if not rows: sys.exit(f"❌ Vídeo {VIDEO_ID} não encontrado")
    row = rows[0]
    title, script = row["title"], row["script"]
    audio_url_existing = row.get("audio_url")
    
    print(f"\n📄 {title}")
    print(f"   {len(script)} chars | status: {row['status']}")
    
    is_long  = len(script) > 4000
    n_scenes = 50 if is_long else 20
    
    # 2. Áudio
    audio_path = WORK_DIR / "audio.mp3"
    if audio_url_existing:
        print(f"\n🎙️  Usando áudio existente...")
        ar = requests.get(audio_url_existing, timeout=60)
        ar.raise_for_status(); audio_path.write_bytes(ar.content)
    else:
        print(f"\n🎙️  Gerando TTS AntonioNeural...")
        generate_tts(script, audio_path)
        ts_ = int(time.time())
        pub = sb_upload(f"videos/audios/v{VIDEO_ID}_v9_{ts_}.mp3", audio_path, "audio/mpeg")
        sb_patch("content_pipeline", VIDEO_ID, {"audio_url": pub})
    
    # 3. Timing DINÂMICO (NUNCA hardcoded)
    dur_audio = get_audio_duration(audio_path)
    rate_real = len(script) / dur_audio
    print(f"\n⏱️  {dur_audio:.1f}s | RATE_REAL={rate_real:.2f} chars/s (dinâmico)")
    
    # 4. Parágrafos e durações
    paragraphs = [p.strip() for p in script.split("\n") if p.strip()]
    actual_n   = min(len(paragraphs), n_scenes)
    scene_durs = [max(1.5, min(len(p)/rate_real, 15.0)) for p in paragraphs[:actual_n]]
    print(f"   {actual_n} cenas | ~{sum(scene_durs):.1f}s estimado")
    
    # 5. Prompts Groq
    print(f"\n🧠 Groq: gerando {actual_n} prompts de cena...")
    scenes = generate_scene_prompts(script, paragraphs[:actual_n])
    key_n  = sum(1 for s in scenes if s.get("key"))
    print(f"   {key_n} key (Veo) + {actual_n-key_n} normal (Gemini)")
    
    # 6. Referência de personagem (Gemini)
    print(f"\n🎨 Gerando referência de personagem (Gemini Image)...")
    ref_b64 = None
    gemini_keys = [k for k in [GEMINI_KEY, GEMINI_KEY2] if k]
    
    master_prompt = (
        "psychology channel host chibi character, kawaii anime girl, dark hair, "
        "friendly smile, professional casual outfit, front-facing neutral pose, "
        "full body visible, white cream background"
    )
    for k in gemini_keys:
        try:
            ref_bytes = gemini_generate_image(master_prompt, k)
            ref_path  = WORK_DIR / "reference.png"
            ref_path.write_bytes(ref_bytes)
            ref_b64   = base64.b64encode(ref_bytes).decode()
            print(f"   ✅ Referência: {len(ref_bytes)//1024}KB")
            break
        except Exception as e:
            print(f"   ⚠️  {k[:20]}...: {e}")
    
    if not ref_b64: print("   ⚠️  Sem referência — Veo usará apenas texto")
    
    # 7. Identificar cenas Veo e Gemini
    veo_indices    = []
    veo_remaining  = VEO_BUDGET
    for i, s in enumerate(scenes[:actual_n]):
        if s.get("key") and veo_remaining > 0 and ref_b64:
            veo_indices.append(i); veo_remaining -= 1
    gemini_indices = [i for i in range(actual_n) if i not in veo_indices]
    
    clips      = [None] * actual_n
    veo_count  = 0
    gem_count  = 0
    
    # 8a. Gemini em paralelo (4 workers)
    print(f"\n🖼️  {len(gemini_indices)} cenas Gemini (paralelo, 4 workers)...")
    
    def render_gemini(idx):
        s   = scenes[idx] if idx < len(scenes) else {}
        img = s.get("img", f"kawaii chibi {s.get('emotion','neutral')}")
        k   = gemini_keys[idx % len(gemini_keys)] if gemini_keys else ""
        if not k:
            return idx, build_color_fallback(scene_durs[idx], idx), "fallback"
        try:
            b = gemini_generate_image(img, k)
            return idx, build_static_clip(b, scene_durs[idx], idx), "gemini"
        except Exception as e:
            print(f"   [{idx+1:02d}] Gemini: {str(e)[:50]} → fallback")
            return idx, build_color_fallback(scene_durs[idx], idx), "fallback"
    
    with ThreadPoolExecutor(max_workers=4) as ex:
        futs = {ex.submit(render_gemini, i): i for i in gemini_indices}
        done = 0
        for fut in as_completed(futs):
            idx, clip_p, src = fut.result()
            clips[idx] = clip_p
            if src == "gemini": gem_count += 1
            done += 1
            sys.stdout.write(f"\r   ✅ {done}/{len(gemini_indices)}")
            sys.stdout.flush()
    print()
    
    # 8b. Veo sequencial
    if veo_indices:
        print(f"\n🎬 {len(veo_indices)} cenas Veo (motion, sequencial)...")
        for idx in veo_indices:
            s     = scenes[idx] if idx < len(scenes) else {}
            vp    = s.get("veo", "chibi character explains psychology, natural gestures")
            print(f"   [{idx+1:02d}] Veo → {vp[:50]}...")
            try:
                gk  = GEMINI_KEY or GEMINI_KEY2
                vid = veo_generate_clip(vp, ref_b64, gk, duration_s=8)
                clips[idx] = build_motion_clip(vid, scene_durs[idx], idx)
                veo_count += 1
            except Exception as e:
                print(f"   ⚠️  {str(e)[:60]} → Gemini fallback")
                try:
                    k   = GEMINI_KEY or GEMINI_KEY2
                    b   = gemini_generate_image(s.get("img","kawaii chibi"), k)
                    clips[idx] = build_static_clip(b, scene_durs[idx], idx)
                    gem_count += 1
                except:
                    clips[idx] = build_color_fallback(scene_durs[idx], idx)
    
    print(f"\n   ✅ {veo_count} Veo motion + {gem_count} Gemini static")
    
    # 9. Concatenar
    print(f"\n🔗 Concatenando {len(clips)} clips...")
    concat_txt = WORK_DIR / "input.txt"
    with open(concat_txt,"w") as f:
        for c in clips:
            if c: f.write(f"file '{c}'\n")
    
    concat_raw = WORK_DIR / "concat.mp4"
    subprocess.run([
        "ffmpeg","-y","-f","concat","-safe","0",
        "-i",str(concat_txt),
        "-c:v","libx264","-pix_fmt","yuv420p","-r","30",str(concat_raw)
    ], check=True, capture_output=True, timeout=300)
    
    # 10. Overlays + áudio final
    print(f"🎨 Overlays (lower third, progress, 🔔 inscreva-se, áudio)...")
    out_name = f"v{VIDEO_ID}_v9_{TS}.mp4"
    out_path = WORK_DIR / out_name
    finalize_video(concat_raw, audio_path, out_path, dur_audio, is_long)
    
    mb = out_path.stat().st_size / 1024 / 1024
    print(f"   ✅ {mb:.1f}MB | {dur_audio:.1f}s | crf={CRF_LONG if is_long else CRF_SHORT}")
    
    # 11. Upload + DB
    print(f"\n☁️  Upload Supabase...")
    pub_url = sb_upload(f"videos/mp4s/{out_name}", out_path)
    sb_patch("content_pipeline", VIDEO_ID, {
        "video_url": pub_url,
        "status": "pending_credentials",
        "metadata": json.dumps({
            "render_version": "v9",
            "veo_clips": veo_count,
            "gemini_clips": gem_count,
            "total_clips": actual_n,
            "duration_s": round(dur_audio, 2),
            "rate_real": round(rate_real, 3),
            "file_mb": round(mb, 2),
            "rendered_at": datetime.utcnow().isoformat(),
            "lower_third": LOWER_THIRD,
            "has_reference_image": ref_b64 is not None,
            "gemini_models_tried": GEMINI_MODELS_IMG[:2],
        })
    })
    
    print(f"\n{'='*60}")
    print(f"  ✅ V9 COMPLETO — Video #{VIDEO_ID}")
    print(f"  🎬 {pub_url}")
    print(f"  📊 Veo: {veo_count} | Gemini: {gem_count} | {dur_audio:.1f}s | {mb:.1f}MB")
    print(f"{'='*60}\n")

if __name__ == "__main__":
    try: main()
    except Exception as e:
        print(f"\n❌ ERRO: {e}"); traceback.print_exc(); sys.exit(1)
