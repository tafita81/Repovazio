#!/usr/bin/env python3
"""
render_remotion_short.py — V31
Gerador de props Remotion para PsychShort.
Combina Chatterbox TTS + Pollinations imagens + Remotion animação.

Fluxo:
1. Busca script do Supabase
2. Classifica grupos semânticos (GANCHO/IMPACTO/REVELACAO/CHORO/PAUSA/CTA/NORMAL)
3. Gera áudio com Chatterbox (ou EdgeTTS como fallback)
4. Busca/gera imagens sincronizadas por frase
5. Calcula timing de frames por grupo (baseado na duração do áudio)
6. Gera props.json para o Remotion
7. Remotion renderiza com React animations
8. Upload do MP4 final para Supabase Storage
"""

import os, sys, json, re, asyncio, subprocess, tempfile, math
import requests

# ══════════════════════════════════════════════════════════════════
# CONFIG
# ══════════════════════════════════════════════════════════════════
VIDEO_ID   = int(os.environ.get("VIDEO_ID", "683"))
SB_URL     = "https://tpjvalzwkqwttvmszvie.supabase.co"
SB_KEY     = os.environ.get("SUPABASE_SERVICE_ROLE_KEY", "")
WORKDIR    = tempfile.mkdtemp(prefix=f"remotion_{VIDEO_ID}_")
FPS        = 30
TOTAL_DUR  = 58.0  # segundos (Short)
TOTAL_FRAMES = int(TOTAL_DUR * FPS)  # 1740

def log(m): print(m, flush=True)

def sb_get(table, params=""):
    return requests.get(f"{SB_URL}/rest/v1/{table}?{params}",
        headers={"apikey": SB_KEY, "Authorization": f"Bearer {SB_KEY}"}, timeout=15).json()

def sb_patch(vid, data):
    requests.patch(f"{SB_URL}/rest/v1/content_pipeline?id=eq.{vid}",
        headers={"apikey": SB_KEY, "Authorization": f"Bearer {SB_KEY}",
                 "Content-Type": "application/json", "Prefer": "return=minimal"},
        json=data, timeout=15)

# ══════════════════════════════════════════════════════════════════
# 1. BUSCAR SCRIPT
# ══════════════════════════════════════════════════════════════════
log(f"\n⚡ REMOTION SHORT V31 — #{VIDEO_ID}")
rows = sb_get("content_pipeline", f"id=eq.{VIDEO_ID}&select=id,title,script,series_slug,ep_number,youtube_title")
if not rows:
    log("❌ Vídeo não encontrado"); sys.exit(1)

row = rows[0]
TITULO     = row["title"]
SCRIPT_RAW = row.get("script","").strip()
SERIE_SLUG = row.get("series_slug","")
EP_NUMBER  = row.get("ep_number", 1)
log(f"  Série: {SERIE_SLUG} E{EP_NUMBER:02d} | Script: {len(SCRIPT_RAW)} chars")

# ══════════════════════════════════════════════════════════════════
# 2. CLASSIFICAR GRUPOS SEMÂNTICOS
# ══════════════════════════════════════════════════════════════════
def classify(line: str) -> str:
    t = line.lower().strip()
    if any(k in t for k in ["salva","canal","assistir","mais tarde","não perder","vídeo completo"]):
        return "CTA"
    if any(k in t for k in ["isso tem nome","isso se chama","tem nome","chama-se"]):
        return "REVELACAO"
    if any(k in t for k in ["chora","lágrimas","soluçava","desmoronou","não conseguia","colapsou"]):
        return "CHORO"
    if len(line) < 35:
        return "IMPACTO"
    if "..." in line or line.endswith("?") or line.endswith("—"):
        return "PAUSA"
    if any(k in t for k in ["você conhece","conheça","imagine","pense em"]):
        return "GANCHO"
    return "NORMAL"

lines = [l.strip() for l in SCRIPT_RAW.split("\n") if l.strip()]
# Agrupar linhas: CTA fica junto, IMPACTO fica sozinho, demais agrupam 2 a 2
groups_raw = []
i = 0
while i < len(lines):
    tp = classify(lines[i])
    if tp == "CTA":
        # Juntar todas as linhas de CTA
        cta_lines = [lines[i]]
        while i+1 < len(lines) and classify(lines[i+1]) == "CTA":
            i += 1; cta_lines.append(lines[i])
        groups_raw.append((" ".join(cta_lines), "CTA"))
        i += 1
    elif tp in ("IMPACTO", "REVELACAO", "CHORO", "GANCHO", "PAUSA"):
        groups_raw.append((lines[i], tp))
        i += 1
    else:  # NORMAL — agrupar 2 linhas
        if i+1 < len(lines) and classify(lines[i+1]) == "NORMAL":
            groups_raw.append((lines[i] + " " + lines[i+1], "NORMAL"))
            i += 2
        else:
            groups_raw.append((lines[i], "NORMAL"))
            i += 1

log(f"  {len(groups_raw)} grupos semânticos: {[g[1] for g in groups_raw]}")

# ══════════════════════════════════════════════════════════════════
# 3. GERAR ÁUDIO — Chatterbox (P1) ou EdgeTTS (P2)
# ══════════════════════════════════════════════════════════════════
AUDIO_PATH = f"{WORKDIR}/narration.mp3"
GEORGE_REF = f"{WORKDIR}/george_ref.wav"

def download_george_ref():
    ref_url = "https://tpjvalzwkqwttvmszvie.supabase.co/storage/v1/object/public/videos/mp4s/v683_george_1779065193.mp4"
    try:
        r = requests.get(ref_url, timeout=30, stream=True)
        mp4_path = f"{WORKDIR}/george_src.mp4"
        with open(mp4_path,"wb") as f:
            for chunk in r.iter_content(8192): f.write(chunk)
        subprocess.run(["ffmpeg","-y","-i",mp4_path,"-ss","2","-t","14",
            "-vn","-ar","22050","-ac","1",
            "-af","highpass=f=80,lowpass=f=8000,volume=1.3", GEORGE_REF],
            capture_output=True, timeout=30)
        return os.path.exists(GEORGE_REF) and os.path.getsize(GEORGE_REF) > 1000
    except: return False

# Gerar áudio por grupo com parâmetros semânticos
PARAMS = {
    "GANCHO":    (0.88, 0.12),
    "IMPACTO":   (0.96, 0.09),
    "REVELACAO": (0.93, 0.10),
    "CHORO":     (0.95, 0.08),
    "PAUSA":     (0.87, 0.13),
    "CTA":       (0.74, 0.26),
    "NORMAL":    (0.82, 0.17),
}

def gen_audio():
    # Tentar Chatterbox
    try:
        import torch
        from chatterbox.tts import ChatterboxMultilingualTTS
        log("  🎤 Chatterbox Multilingual")
        has_ref = download_george_ref()
        model = ChatterboxMultilingualTTS.from_pretrained(device="cpu")
        segs = []
        for text, tp in groups_raw:
            exag, cfg = PARAMS.get(tp, (0.82, 0.17))
            kwargs = {"language_id": "pt", "exaggeration": exag, "cfg_weight": cfg}
            if has_ref: kwargs["audio_prompt_path"] = GEORGE_REF
            wav = model.generate(text, **kwargs)
            seg_path = f"{WORKDIR}/seg_{len(segs):03d}.wav"
            import soundfile as sf
            sf.write(seg_path, wav.squeeze().numpy(), 22050)
            # Noise gate por segmento
            gate_path = f"{WORKDIR}/seg_{len(segs):03d}_gate.wav"
            subprocess.run(["ffmpeg","-y","-i",seg_path,
                "-af","afade=t=in:st=0:d=0.03,afade=t=out:st={:.3f}:d=0.06,agate=threshold=0.028:ratio=8000:attack=1:release=60".format(
                    max(0, float(subprocess.run(["ffprobe","-v","error","-show_entries",
                        "format=duration","-of","default=noprint_wrappers=1:nokey=1",seg_path],
                        capture_output=True,text=True).stdout.strip() or "1") - 0.06)
                ),
                gate_path], capture_output=True, timeout=60)
            segs.append(gate_path if os.path.exists(gate_path) else seg_path)

        # Concatenar com silêncios dramáticos
        concat_f = f"{WORKDIR}/concat.txt"
        SILENCE_MAP = {"IMPACTO": (0.9,1.4), "CHORO": (0.5,1.8), "REVELACAO": (0.7,1.4),
                       "GANCHO": (0.0,0.8), "CTA": (0.9,0.0), "PAUSA": (0.4,1.1), "NORMAL": (0.0,0.65)}
        sil_path = lambda s,t: (lambda p: (subprocess.run(["ffmpeg","-y","-f","lavfi",
            "-i",f"anullsrc=r=22050:cl=mono","-t",str(t),"-ar","22050","-acodec","pcm_s16le","-f","wav",p],
            capture_output=True, timeout=10), p)[1])(f"{WORKDIR}/sil_{s}_{t:.2f}.wav") if t > 0.01 else None

        with open(concat_f,"w") as f:
            for idx, (text, tp) in enumerate(groups_raw):
                pre, post = SILENCE_MAP.get(tp, (0,0.65))
                if pre > 0.01:
                    p = sil_path(f"pre{idx}", pre)
                    if p: f.write(f"file '{p}'\n")
                f.write(f"file '{segs[idx]}'\n")
                if post > 0.01:
                    p = sil_path(f"post{idx}", post)
                    if p: f.write(f"file '{p}'\n")

        raw = f"{WORKDIR}/raw.wav"
        subprocess.run(["ffmpeg","-y","-f","concat","-safe","0","-i",concat_f,"-ar","44100","-ac","1",raw],
            capture_output=True, timeout=120)
        # Gate final duplo
        subprocess.run(["ffmpeg","-y","-i",raw,
            "-af","highpass=f=80,agate=threshold=0.028:ratio=8000:attack=2:release=50",
            "-codec:a","libmp3lame","-b:a","256k","-q:a","0", AUDIO_PATH],
            capture_output=True, timeout=60)
        return True
    except Exception as e:
        log(f"  ⚠️ Chatterbox falhou: {e} → EdgeTTS")

    # Fallback EdgeTTS
    try:
        import edge_tts
        full_text = " ".join(t for t,_ in groups_raw)
        async def do_tts():
            c = edge_tts.Communicate(full_text, voice="pt-BR-ThalitaMultilingualNeural", rate="+28%")
            await c.save(AUDIO_PATH)
        asyncio.run(do_tts())
        log("  ✅ ThalitaMultilingualNeural EdgeTTS")
        return os.path.exists(AUDIO_PATH)
    except Exception as e:
        log(f"  ❌ EdgeTTS: {e}"); return False

audio_ok = gen_audio()

# Medir duração real do áudio
def measure_dur(path):
    try:
        r = subprocess.run(["ffprobe","-v","error","-show_entries","format=duration",
            "-of","default=noprint_wrappers=1:nokey=1",path], capture_output=True,text=True,timeout=10)
        return float(r.stdout.strip())
    except: return TOTAL_DUR

audio_dur = measure_dur(AUDIO_PATH) if audio_ok else TOTAL_DUR
log(f"  🎵 Áudio: {audio_dur:.2f}s")

# Upload áudio para Supabase Storage
AUDIO_SB_URL = ""
if audio_ok:
    try:
        with open(AUDIO_PATH,"rb") as f:
            content = f.read()
        fname = f"audio/v{VIDEO_ID}_remotion.mp3"
        r = requests.put(
            f"{SB_URL}/storage/v1/object/videos/{fname}",
            headers={"apikey": SB_KEY, "Authorization": f"Bearer {SB_KEY}",
                     "Content-Type": "audio/mpeg", "x-upsert": "true"},
            data=content, timeout=60
        )
        if r.status_code < 300:
            AUDIO_SB_URL = f"{SB_URL}/storage/v1/object/public/videos/{fname}"
            log(f"  ✅ Áudio: {AUDIO_SB_URL}")
    except Exception as e:
        log(f"  ⚠️ Upload áudio: {e}")

# ══════════════════════════════════════════════════════════════════
# 4. CALCULAR TIMING DE FRAMES POR GRUPO
# ══════════════════════════════════════════════════════════════════
# Distribuir frames proporcionalmente ao tamanho de cada grupo
# com silêncio dramático já embutido no áudio
def calc_group_frames(groups_raw, total_frames, fps):
    """Estima o start_frame de cada grupo baseado na duração do texto."""
    SILENCE_MAP = {
        "GANCHO": (0, 25), "IMPACTO": (27, 42), "REVELACAO": (21, 36),
        "CHORO": (15, 54), "CTA": (27, 0), "PAUSA": (12, 33), "NORMAL": (0, 20),
    }
    # Calcular "peso" de cada segmento (chars + silêncio)
    weights = []
    for text, tp in groups_raw:
        base = len(text) * 1.5  # ~1.5 frames por char (30fps, ~20 chars/s)
        pre_f, post_f = SILENCE_MAP.get(tp, (0, 20))
        weights.append(base + pre_f + post_f)
    
    total_w = sum(weights)
    available_frames = total_frames - 30 - 10  # Reservar intro e outro
    
    result = []
    current = 30  # Começa no frame 30 (após intro ψ)
    for i, (text, tp) in enumerate(groups_raw):
        result.append({
            "text": text,
            "type": tp,
            "startFrame": current,
        })
        frames_for_this = int((weights[i] / total_w) * available_frames)
        current += frames_for_this
    
    return result

groups_with_frames = calc_group_frames(groups_raw, TOTAL_FRAMES, FPS)
log(f"  ⏱ Timing: {[(g['type'], g['startFrame']) for g in groups_with_frames]}")

# ══════════════════════════════════════════════════════════════════
# 5. BUSCAR/GERAR IMAGENS SINCRONIZADAS
# ══════════════════════════════════════════════════════════════════
CHARACTER_MAP = {
    "GANCHO":    "daniela",
    "NORMAL":    "daniela",
    "IMPACTO":   "marcos",
    "CHORO":     "sara",
    "REVELACAO": "ana",
    "PAUSA":     "sara",
    "CTA":       "daniela",
}

def dl_img(prompt, idx, char):
    """Gera imagem via Pollinations ou banco Supabase."""
    # Tentar banco Supabase primeiro
    try:
        bank = requests.get(
            f"{SB_URL}/rest/v1/image_bank?character_slug=eq.{char}&limit=5",
            headers={"apikey": SB_KEY, "Authorization": f"Bearer {SB_KEY}"},
            timeout=10
        ).json()
        if bank and bank[0].get("image_url"):
            log(f"    📦 Banco: {char}")
            return bank[idx % len(bank)]["image_url"]
    except: pass
    
    # Fallback Pollinations
    import urllib.parse
    pollen_prompt = f"kawaii chibi anime, {char}, {prompt[:60]}, Psych2Go style, dark background, 9:16"
    url = f"https://image.pollinations.ai/prompt/{urllib.parse.quote(pollen_prompt)}"
    url += f"?width=576&height=1024&model=flux&seed={VIDEO_ID + idx}&nologo=true"
    log(f"    🌸 Pollinations: {url[:60]}...")
    return url

images_data = []
for i, group in enumerate(groups_with_frames):
    char = CHARACTER_MAP.get(group["type"], "daniela")
    img_url = dl_img(group["text"], i, char)
    images_data.append({
        "url": img_url,
        "startFrame": group["startFrame"],
        "character": char,
    })

# ══════════════════════════════════════════════════════════════════
# 6. GERAR PROPS.JSON PARA REMOTION
# ══════════════════════════════════════════════════════════════════
props = {
    "videoId": VIDEO_ID,
    "title": TITULO,
    "audioUrl": AUDIO_SB_URL or "",
    "groups": groups_with_frames,
    "images": images_data,
    "seriesSlug": SERIE_SLUG,
    "epNumber": EP_NUMBER,
}

props_path = f"{WORKDIR}/props.json"
with open(props_path, "w", encoding="utf-8") as f:
    json.dump(props, f, ensure_ascii=False, indent=2)

log(f"\n📋 Props Remotion:\n{json.dumps(props, ensure_ascii=False, indent=2)[:500]}...")

# ══════════════════════════════════════════════════════════════════
# 7. RENDERIZAR COM REMOTION
# ══════════════════════════════════════════════════════════════════
OUTPUT_MP4 = f"{WORKDIR}/short_v{VIDEO_ID}.mp4"

log(f"\n🎬 Renderizando com Remotion React...")
render_cmd = [
    "npx", "remotion", "render",
    "remotion/src/index.tsx",   # entry point
    "PsychShort",               # composition ID
    OUTPUT_MP4,
    "--props", props_path,
    "--codec", "h264",
    "--fps", str(FPS),
    "--width", "576",
    "--height", "1024",
    "--frames", f"0-{TOTAL_FRAMES - 1}",
    "--log", "verbose",
]

result = subprocess.run(render_cmd, capture_output=False, timeout=600)
if result.returncode != 0:
    log("❌ Remotion render falhou — verificar logs")
    sys.exit(1)

if not os.path.exists(OUTPUT_MP4) or os.path.getsize(OUTPUT_MP4) < 10000:
    log("❌ MP4 inválido ou vazio"); sys.exit(1)

size_mb = os.path.getsize(OUTPUT_MP4) / 1024 / 1024
log(f"  ✅ Remotion render concluído: {size_mb:.2f}MB")

# ══════════════════════════════════════════════════════════════════
# 8. UPLOAD PARA SUPABASE
# ══════════════════════════════════════════════════════════════════
with open(OUTPUT_MP4, "rb") as f:
    content = f.read()

fname = f"mp4s/v{VIDEO_ID}_remotion.mp4"
r = requests.put(
    f"{SB_URL}/storage/v1/object/videos/{fname}",
    headers={"apikey": SB_KEY, "Authorization": f"Bearer {SB_KEY}",
             "Content-Type": "video/mp4", "x-upsert": "true"},
    data=content, timeout=120
)

if r.status_code >= 300:
    log(f"  ❌ Upload falhou: {r.text}"); sys.exit(1)

video_url = f"{SB_URL}/storage/v1/object/public/videos/{fname}"
log(f"  ✅ Uploaded: {video_url}")

sb_patch(VIDEO_ID, {
    "video_url": video_url,
    "status": "pending_credentials",
    "metadata": json.dumps({
        "version": "remotion_v31",
        "dur_s": audio_dur,
        "file_mb": round(size_mb, 2),
        "n_groups": len(groups_raw),
        "n_images": len(images_data),
        "voice": "Chatterbox_or_Thalita",
        "engine": "Remotion_React",
        "fps": FPS,
        "frames": TOTAL_FRAMES,
    })
})

log(f"""
ψ RESULTADO REMOTION:
  ⏱  {audio_dur:.2f}s | 💾 {size_mb:.2f}MB
  🎬 {video_url}
  ⚡ React Remotion V31 — animações superiores ao Psych2Go
""")
