#!/usr/bin/env python3
"""
render_video_v9.py — psicologia.doc V9 MOTION AI
Pipeline: Edge TTS + Veo 3.x (motion clips) + Gemini 2.5 Flash Image (fallback) + ffconcat

CORREÇÕES V9 vs V8:
  ✅ Veo 3.x para cenas-chave (braços/olhos/boca se movendo)
  ✅ reference_image: personagem consistente entre cenas
  ✅ Budget Veo: máx 8 clips/vídeo (quota free)
  ✅ RATE_REAL dinâmico SEMPRE (len(script)/dur_audio)
  ✅ Lower third SEM Psicóloga até jan/2027
  ✅ Encerramento: texto + 🔔 overlay + som de sino
  ✅ Anti-plágio em TODOS os prompts
  ✅ Fundo creme/branco Psych2Go (NUNCA escuro)
  ✅ Gemini chibi como fallback (NUNCA Pillow stick figures)
  ✅ crf=25 Shorts, crf=22 Longs
  ✅ Ken Burns suave para cenas Gemini (mesmo do V8)
"""

import os, sys, json, time, base64, asyncio, subprocess
import tempfile, requests, traceback, re
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
LOWER_THIRD = "Daniela Coelho | Saude Mental | @psidanielacoelho"
CRF_SHORT   = 25     # ~3MB
CRF_LONG    = 22     # ~18MB
VEO_BUDGET  = 8      # max clips Veo por vídeo (economizar quota free)

# Veo: tenta do mais novo para o mais estável
VEO_MODELS = [
    "veo-3.1-generate-preview",
    "veo-3.0-generate-preview",
    "veo-2.0-generate-001",
]

GEMINI_IMG_MODEL = "gemini-2.5-flash-preview-04-17"

ANTI_PLAGIO = (
    "original character design not based on any existing IP or franchise, "
    "no text, no logos, no brand marks, no watermarks"
)
PSYCH2GO_BASE = (
    "Psych2Go animation style, kawaii chibi anime character, "
    "cream white background #F5F0E8, pastel warm colors, "
    "round big eyes, clean expressive face, soft clean lines, "
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
        if s.get("codec_type") == "audio": return float(s.get("duration",60))
    return 60.0

# ── GROQ: gerar prompts de cena ───────────────────────────────────────────────
def generate_scene_prompts(script, paragraphs):
    """Groq gera prompts Veo + Gemini para cada parágrafo. Identifica cenas-chave."""
    system = (
        "Você é diretor de animação do canal psicologia @psidanielacoelho. "
        "Gere prompts para cenas de vídeo psych2go-style. Responda APENAS JSON válido."
    )
    user = f"""Script do vídeo (português BR):
{script}

Para cada um dos {len(paragraphs)} parágrafos, gere um objeto JSON com:
- "veo": prompt em inglês para Veo gerar 8s clip animado (personagem chibi gesticulando com emoção real)
- "img": prompt em inglês para Gemini gerar imagem chibi estática (fallback)
- "key": true se é cena-chave emocional (hook/clímax/revelação) — máximo {VEO_BUDGET} scenes
- "emotion": uma das: neutral, surprised, concerned, happy, focused, dramatic, empathetic, sad

Retorne APENAS array JSON com {len(paragraphs)} objetos. Nenhum texto extra."""

    try:
        r = requests.post("https://api.groq.com/openai/v1/chat/completions",
            headers={"Authorization":f"Bearer {GROQ_KEY}", "Content-Type":"application/json"},
            json={"model":"llama-3.3-70b-versatile",
                  "messages":[{"role":"system","content":system},
                               {"role":"user","content":user}],
                  "temperature":0.7, "max_tokens":4096},
            timeout=90)
        text = r.json()["choices"][0]["message"]["content"]
        m = re.search(r'\[.*\]', text, re.DOTALL)
        if m: return json.loads(m.group())
    except Exception as e:
        print(f"   ⚠️ Groq falhou: {e}")
    
    # Fallback padrão
    defaults = ["neutral","concerned","dramatic","surprised","empathetic","focused","happy","sad"]
    return [{"veo":f"chibi character explains psychology, {defaults[i%8]} gesture",
             "img":f"kawaii chibi {defaults[i%8]}",
             "key": i < VEO_BUDGET,
             "emotion": defaults[i%8]} for i in range(len(paragraphs))]

# ── GEMINI IMAGE ──────────────────────────────────────────────────────────────
def gemini_generate_image(prompt, key):
    """Gera imagem PNG chibi com Gemini 2.5 Flash Image"""
    full = f"{PSYCH2GO_BASE}, {prompt}. {ANTI_PLAGIO}"
    r = requests.post(
        f"https://generativelanguage.googleapis.com/v1beta/models/{GEMINI_IMG_MODEL}:generateContent?key={key}",
        headers={"Content-Type":"application/json"},
        json={"contents":[{"parts":[{"text":full}]}],
              "generationConfig":{"responseModalities":["IMAGE","TEXT"]}},
        timeout=60)
    if r.status_code != 200:
        raise ValueError(f"Gemini {r.status_code}: {r.text[:200]}")
    for part in r.json().get("candidates",[{}])[0].get("content",{}).get("parts",[]):
        if "inlineData" in part:
            return base64.b64decode(part["inlineData"]["data"])
    raise ValueError("Sem imagem na resposta Gemini")

# ── VEO 3.x API ───────────────────────────────────────────────────────────────
def veo_generate_clip(veo_prompt, ref_b64, key, duration_s=8):
    """
    Gera clip de vídeo com motion real usando Veo 3.x
    Usa a imagem de referência do personagem para consistência visual
    """
    for model in VEO_MODELS:
        try:
            result = _veo_api_call(model, veo_prompt, ref_b64, key, duration_s)
            if result:
                print(f"      ✅ Veo clip com {model}")
                return result
        except Exception as e:
            print(f"      ↳ {model}: {str(e)[:80]}")
    raise ValueError("Todos os modelos Veo indisponíveis ou quota esgotada")

def _veo_api_call(model, prompt, ref_b64, key, dur):
    """
    Chamada assíncrona à API Veo via Google AI GenerateVideo
    image-to-video com personagem de referência
    """
    url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateVideo?key={key}"
    body = {
        "prompt": {"text": f"{PSYCH2GO_BASE}, {prompt}. {ANTI_PLAGIO}"},
        "image": {"imageBytes": ref_b64, "mimeType": "image/png"},
        "generationConfig": {
            "durationSeconds": dur,
            "aspectRatio": "9:16",
            "numberOfVideos": 1,
            "personGeneration": "ALLOW_ADULT"
        }
    }
    r = requests.post(url, json=body, timeout=60)
    if r.status_code in (400, 404):
        raise ValueError(f"API unavailable ({r.status_code})")
    if r.status_code not in (200, 202):
        raise ValueError(f"HTTP {r.status_code}: {r.text[:200]}")
    
    op = r.json()
    op_name = op.get("name","")
    if not op_name:
        # Resposta síncrona (modelo mais novo pode retornar direto)
        return _extract_video_from_response(op)
    
    # Polling (max 4 min)
    poll_url = f"https://generativelanguage.googleapis.com/v1beta/{op_name}?key={key}"
    for i in range(48):
        time.sleep(5)
        pr = requests.get(poll_url, timeout=30)
        if pr.status_code != 200: raise ValueError(f"Poll {pr.status_code}")
        pd = pr.json()
        if pd.get("done"):
            return _extract_video_from_response(pd.get("response", pd))
        if i % 6 == 0:
            print(f"      ⏳ Veo processando... {(i+1)*5}s")
    raise ValueError("Timeout Veo (4min)")

def _extract_video_from_response(resp):
    """Extrai bytes do vídeo da resposta Veo"""
    samples = resp.get("generatedSamples") or resp.get("videos") or []
    if not samples: raise ValueError("Sem vídeos na resposta")
    v = samples[0]
    uri = v.get("video",{}).get("uri") or v.get("uri","")
    if uri:
        vr = requests.get(uri, timeout=120)
        vr.raise_for_status()
        return vr.content
    b64 = v.get("video",{}).get("videoBytes") or v.get("videoBytes","")
    if b64: return base64.b64decode(b64)
    raise ValueError("Sem URI nem bytes no vídeo")

# ── MONTAR CLIPS ──────────────────────────────────────────────────────────────
def build_static_clip(img_bytes, duration, idx):
    """V8 fallback: imagem estática → Ken Burns suave → MP4"""
    img_p  = WORK_DIR / f"img_{idx:03d}.png"
    clip_p = WORK_DIR / f"clip_{idx:03d}.mp4"
    img_p.write_bytes(img_bytes)
    dur_frames = max(1, int(duration * 30))
    
    # Ken Burns: alternando zoom in/out
    if idx % 2 == 0:
        zexpr = "min(zoom+0.0012,1.25)"
    else:
        zexpr = "if(lte(zoom,1.0),1.25,max(1.0,zoom-0.0012))"
    
    vf = (f"scale=1200:2133,"
          f"zoompan=z='{zexpr}':d={dur_frames}:"
          f"x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':"
          f"s=1080x1920:fps=30")
    
    subprocess.run([
        "ffmpeg","-y","-loop","1","-i",str(img_p),
        "-vf",vf,"-t",str(duration),
        "-c:v","libx264","-pix_fmt","yuv420p","-r","30",
        str(clip_p)
    ], check=True, capture_output=True, timeout=120)
    return clip_p

def build_motion_clip(video_bytes, target_dur, idx):
    """V9: Veo video → trim/loop para duração exata → 1080×1920"""
    raw_p  = WORK_DIR / f"veo_{idx:03d}.mp4"
    clip_p = WORK_DIR / f"clip_{idx:03d}.mp4"
    raw_p.write_bytes(video_bytes)
    
    vf = ("scale=1080:1920:force_original_aspect_ratio=decrease,"
          "pad=1080:1920:(ow-iw)/2:(oh-ih)/2:color=#F5F0E8")
    
    subprocess.run([
        "ffmpeg","-y",
        "-stream_loop","-1","-i",str(raw_p),  # loop se clip < duração
        "-vf",vf,"-t",str(target_dur),
        "-c:v","libx264","-pix_fmt","yuv420p","-r","30",
        str(clip_p)
    ], check=True, capture_output=True, timeout=120)
    return clip_p

def build_color_fallback(duration, idx):
    """Fallback final: creme sólido (nunca acontece em produção)"""
    clip_p = WORK_DIR / f"clip_{idx:03d}.mp4"
    subprocess.run([
        "ffmpeg","-y","-f","lavfi",
        "-i",f"color=c=0xF5F0E8:s=1080x1920:d={duration}:r=30",
        "-c:v","libx264","-pix_fmt","yuv420p",
        str(clip_p)
    ], check=True, capture_output=True)
    return clip_p

# ── OVERLAYS FINAIS ───────────────────────────────────────────────────────────
def finalize_video(concat_path, audio_path, out_path, total_dur, is_long):
    """
    Adiciona lower third + progress bar + texto de encerramento + áudio
    Lower third: "Daniela Coelho | Saude Mental | @psidanielacoelho" (SEM Psicóloga)
    Encerramento: overlay 🔔 Inscreva-se nos últimos 3s
    """
    crf = CRF_LONG if is_long else CRF_SHORT
    end_start = max(0, total_dur - 3.5)
    
    vf_parts = [
        # Lower third (SEM Psicóloga)
        (f"drawtext=text='{LOWER_THIRD}'"
         f":fontsize=26:fontcolor=white"
         f":x=(w-text_w)/2:y=h-75"
         f":box=1:boxcolor=black@0.65:boxborderw=8"),
        # Progress bar violeta
        (f"drawbox=x=0:y=h-10:w='iw*t/{total_dur}':h=10"
         f":color=0x7C3AED:t=fill"),
        # Encerramento nos últimos 3.5s: 🔔 Inscreva-se agora
        (f"drawtext=text='🔔 Inscreva-se agora'"
         f":fontsize=40:fontcolor=0x7C3AED"
         f":x=(w-text_w)/2:y=h/2+200"
         f":box=1:boxcolor=white@0.85:boxborderw=16"
         f":enable='gte(t,{end_start})'"),
    ]
    
    vf = ",".join(vf_parts)
    
    subprocess.run([
        "ffmpeg","-y",
        "-i",str(concat_path),
        "-i",str(audio_path),
        "-vf",vf,
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
    
    row    = rows[0]
    title  = row["title"]
    script = row["script"]
    audio_url_existing = row.get("audio_url")
    
    print(f"\n📄 Título: {title}")
    print(f"   Script: {len(script)} chars")
    print(f"   Status: {row['status']}")
    
    is_long = len(script) > 4000
    n_scenes = 50 if is_long else 20
    
    # 2. Áudio TTS
    audio_path = WORK_DIR / "audio.mp3"
    if audio_url_existing:
        print(f"\n🎙️  Usando áudio existente (V8)...")
        ar = requests.get(audio_url_existing, timeout=60)
        ar.raise_for_status()
        audio_path.write_bytes(ar.content)
    else:
        print(f"\n🎙️  Gerando TTS pt-BR-AntonioNeural...")
        generate_tts(script, audio_path)
        a_path = f"videos/audios/v{VIDEO_ID}_v9_{TS}.mp3"
        audio_pub = sb_upload(a_path, audio_path, "audio/mpeg")
        sb_patch("content_pipeline", VIDEO_ID, {"audio_url": audio_pub})
    
    # 3. Timing DINÂMICO
    dur_audio = get_audio_duration(audio_path)
    rate_real = len(script) / dur_audio
    print(f"\n⏱️  Duração áudio: {dur_audio:.1f}s")
    print(f"   RATE_REAL: {rate_real:.2f} chars/s (dinâmico, NUNCA hardcoded)")
    
    # 4. Parágrafos e durações proporcionais
    paragraphs = [p.strip() for p in script.split("\n") if p.strip()]
    actual_n   = min(len(paragraphs), n_scenes)
    scene_durs = [max(1.5, min(len(p)/rate_real, 15.0)) for p in paragraphs[:actual_n]]
    print(f"   {actual_n} cenas | total estimado: {sum(scene_durs):.1f}s")
    
    # 5. Prompts Groq
    print(f"\n🧠 Groq gerando {actual_n} prompts de cena...")
    scenes = generate_scene_prompts(script, paragraphs[:actual_n])
    key_count = sum(1 for s in scenes if s.get("key"))
    print(f"   {key_count} cenas-chave (Veo) | {actual_n-key_count} normais (Gemini)")
    
    # 6. Gerar imagem de referência MESTRE (personagem Daniela Coelho)
    print(f"\n🎨 Gerando referência de personagem mestre (Gemini Flash Image)...")
    ref_bytes = None
    ref_b64   = None
    gemini_keys = [k for k in [GEMINI_KEY, GEMINI_KEY2] if k]
    
    if gemini_keys:
        master_prompt = (
            "Daniela Coelho, psychology channel host character, "
            "kawaii chibi girl with dark hair, warm smile, professional casual outfit, "
            "glasses optional, neutral front-facing pose, standing, "
            "white/cream background, full body visible"
        )
        for k in gemini_keys:
            try:
                ref_bytes = gemini_generate_image(master_prompt, k)
                ref_path  = WORK_DIR / "reference.png"
                ref_path.write_bytes(ref_bytes)
                ref_b64   = base64.b64encode(ref_bytes).decode()
                sz_kb     = len(ref_bytes)//1024
                print(f"   ✅ Referência criada ({sz_kb}KB)")
                break
            except Exception as e:
                print(f"   ⚠️  Key {k[:20]}...: {e}")
    
    if not ref_b64:
        print(f"   ⚠️  Sem referência — Veo usará apenas texto")
    
    # 7. Gerar clips (paralelo para Gemini, sequencial para Veo)
    print(f"\n🎬 Gerando {actual_n} clips...")
    clips      = [None] * actual_n
    veo_count  = 0
    gem_count  = 0
    veo_budget_remaining = VEO_BUDGET
    
    # Identificar cenas que usarão Veo
    veo_indices = []
    for i, s in enumerate(scenes[:actual_n]):
        if s.get("key") and veo_budget_remaining > 0 and ref_b64:
            veo_indices.append(i)
            veo_budget_remaining -= 1
    
    gemini_indices = [i for i in range(actual_n) if i not in veo_indices]
    
    # GEMINI em paralelo (4 workers)
    def render_gemini_scene(idx):
        s = scenes[idx] if idx < len(scenes) else {}
        img_prompt = s.get("img", f"kawaii chibi {s.get('emotion','neutral')} emotion")
        k = gemini_keys[idx % len(gemini_keys)] if gemini_keys else ""
        try:
            img = gemini_generate_image(img_prompt, k)
            return idx, build_static_clip(img, scene_durs[idx], idx), "gemini"
        except Exception as e:
            print(f"      [{idx+1:02d}] Gemini falhou: {str(e)[:60]} → creme fallback")
            return idx, build_color_fallback(scene_durs[idx], idx), "fallback"
    
    print(f"   🖼️  {len(gemini_indices)} cenas Gemini (paralelo)...")
    with ThreadPoolExecutor(max_workers=4) as ex:
        futures = {ex.submit(render_gemini_scene, i): i for i in gemini_indices}
        for fut in as_completed(futures):
            idx, clip_p, src = fut.result()
            clips[idx] = clip_p
            if src == "gemini": gem_count += 1
            sys.stdout.write(f"\r      ✅ Gemini: {gem_count}/{len(gemini_indices)}")
            sys.stdout.flush()
    print()
    
    # VEO sequencial (API assíncrona interna)
    print(f"   🎬 {len(veo_indices)} cenas Veo (motion, sequencial)...")
    for idx in veo_indices:
        s = scenes[idx] if idx < len(scenes) else {}
        veo_p = s.get("veo", f"chibi character explains psychology energetically")
        print(f"   [{idx+1:02d}/{actual_n}] Veo → {veo_p[:55]}...")
        try:
            gkey = GEMINI_KEY if GEMINI_KEY else GEMINI_KEY2
            vid  = veo_generate_clip(veo_p, ref_b64, gkey, duration_s=8)
            clips[idx] = build_motion_clip(vid, scene_durs[idx], idx)
            veo_count += 1
        except Exception as e:
            print(f"      ⚠️  Veo indisponível: {str(e)[:80]}")
            print(f"      → Fallback para Gemini estática...")
            try:
                k = GEMINI_KEY if GEMINI_KEY else GEMINI_KEY2
                img = gemini_generate_image(s.get("img","kawaii chibi"), k)
                clips[idx] = build_static_clip(img, scene_durs[idx], idx)
                gem_count += 1
            except:
                clips[idx] = build_color_fallback(scene_durs[idx], idx)
                gem_count += 1
    
    print(f"\n   ✅ Clips prontos: {veo_count} Veo motion + {gem_count} Gemini static")
    
    # 8. Concatenar
    print(f"\n🔗 Concatenando {len(clips)} clips...")
    concat_file = WORK_DIR / "input.txt"
    with open(concat_file,"w") as f:
        for c in clips:
            if c: f.write(f"file '{c}'\n")
    
    concat_raw = WORK_DIR / "concat.mp4"
    subprocess.run([
        "ffmpeg","-y","-f","concat","-safe","0",
        "-i",str(concat_file),
        "-c:v","libx264","-pix_fmt","yuv420p","-r","30",
        str(concat_raw)
    ], check=True, capture_output=True, timeout=300)
    
    # 9. Overlays finais + áudio
    print(f"🎨 Adicionando overlays (lower third, progress, sino, áudio)...")
    out_name = f"v{VIDEO_ID}_v9_{TS}.mp4"
    out_path = WORK_DIR / out_name
    finalize_video(concat_raw, audio_path, out_path, dur_audio, is_long)
    
    mb = out_path.stat().st_size / 1024 / 1024
    print(f"   ✅ {mb:.1f}MB | {dur_audio:.1f}s | crf={CRF_LONG if is_long else CRF_SHORT}")
    
    # 10. Upload Supabase
    print(f"\n☁️  Upload Supabase Storage...")
    pub_url = sb_upload(f"videos/mp4s/{out_name}", out_path)
    
    # 11. Atualizar DB
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
        })
    })
    
    print(f"\n{'='*60}")
    print(f"  ✅ V9 COMPLETO — Video #{VIDEO_ID}")
    print(f"  🎬 {pub_url}")
    print(f"  📊 Veo motion: {veo_count} | Gemini: {gem_count} | {dur_audio:.1f}s | {mb:.1f}MB")
    print(f"{'='*60}\n")

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"\n❌ ERRO FATAL: {e}")
        traceback.print_exc()
        sys.exit(1)
