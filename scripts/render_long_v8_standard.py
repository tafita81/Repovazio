#!/usr/bin/env python3
"""
render_long_v8_standard.py — LONGS 15-25min | PADRÃO ETERNO psicologia.doc
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
IDÊNTICO ao Short V8 em ritmo e estilo:
  - ~3 segundos por imagem (igual Short #683)
  - 20 imagens únicas AI (pool) cicladas em ~N_SEGS segmentos
  - Caption muda a cada segmento — "palavra a palavra"
  - Lower third, badge, fundo creme — tudo idêntico ao Short

ESTRATÉGIA:
  1. Groq gera 20 prompts AI + N_SEGS captions (uma por ~40 chars)
  2. Gera 20 imagens chibi únicas (Pollinations → Gemini → Pillow)
  3. Aplica overlay em cada imagem do pool
  4. Divide script em N_SEGS segmentos de ~40 chars
  5. Cada segmento usa image[i % 20] do pool
  6. Caption específica por segmento (muda a cada ~3s)
  7. ffconcat → render crf=22 → ~15-20MB
"""
import os, sys, json, re, time, base64, asyncio, subprocess, requests, urllib.parse
from PIL import Image, ImageDraw
from concurrent.futures import ThreadPoolExecutor, as_completed

# ── CONFIG ────────────────────────────────────────────────────────
VIDEO_ID    = int(sys.argv[1]) if len(sys.argv) > 1 else int(os.environ.get("VIDEO_ID","693"))
SB_URL      = "https://tpjvalzwkqwttvmszvie.supabase.co"
SB_KEY      = os.environ.get("SUPABASE_SERVICE_KEY","")
GROQ_KEY    = os.environ.get("GROQ_API_KEY","")
GEMINI_KEYS = [k for k in [
    os.environ.get("GEMINI_API_KEY",""),
    os.environ.get("GEMINI_API_KEY_2",""),
] if k]

W, H    = 1080, 1920
N_IMGS  = 20            # imagens únicas geradas (pool — igual ao Short)
CHARS_POR_SEG = 41      # ~41 chars/segmento = ~3s por imagem (igual Short)
CRF     = 22            # qualidade Long (~15-20MB)
WORKDIR = f"/tmp/vlong_{VIDEO_ID}"
os.makedirs(WORKDIR, exist_ok=True)

# Cores padrão eterno (idêntico ao Short)
VERM  = (220,  50,  50)
GOLD  = (255, 210,  50)
BRAN  = (255, 255, 255)
LILAS = (185, 170, 225)

GEMINI_MODELS = [
    "gemini-2.0-flash-exp",
    "gemini-2.0-flash-exp-image-generation",
    "gemini-2.5-flash-image",
]

_gkey_idx = [0]
def gemini_key():
    return GEMINI_KEYS[_gkey_idx[0] % len(GEMINI_KEYS)] if GEMINI_KEYS else None
def rotate_key():
    _gkey_idx[0] += 1

print(f"{'='*60}")
print(f"  ψ V8 LONG STANDARD — Video #{VIDEO_ID}")
print(f"  {N_IMGS} imagens únicas + captions palavra a palavra")
print(f"  ~3s/imagem (igual Short #683)")
print(f"{'='*60}")

# ── SUPABASE ──────────────────────────────────────────────────────
def sb_get(table, qs):
    r = requests.get(f"{SB_URL}/rest/v1/{table}?{qs}",
        headers={"apikey":SB_KEY,"Authorization":f"Bearer {SB_KEY}"}, timeout=30)
    r.raise_for_status(); return r.json()

def sb_patch(table, id_, data):
    r = requests.patch(f"{SB_URL}/rest/v1/{table}?id=eq.{id_}",
        headers={"apikey":SB_KEY,"Authorization":f"Bearer {SB_KEY}",
                 "Content-Type":"application/json","Prefer":"return=minimal"},
        json=data, timeout=30)
    r.raise_for_status()

def sb_upload(path, data, ctype):
    r = requests.post(f"{SB_URL}/storage/v1/object/videos/{path}",
        headers={"apikey":SB_KEY,"Authorization":f"Bearer {SB_KEY}",
                 "Content-Type":ctype,"x-upsert":"true"},
        data=data, timeout=600)
    r.raise_for_status()
    return f"{SB_URL}/storage/v1/object/public/videos/{path}"

# ── CARREGAR DADOS ────────────────────────────────────────────────
rows = sb_get("content_pipeline",
    f"id=eq.{VIDEO_ID}&select=id,title,script,topic,audio_url")
if not rows: sys.exit(f"❌ Vídeo {VIDEO_ID} não encontrado")

video      = rows[0]
script_tts = video.get("script","").strip()
topic      = video.get("topic", video.get("title","psychology"))
n_segs     = max(N_IMGS, round(len(script_tts) / CHARS_POR_SEG))

print(f"\n📄 {video.get('title','')}")
print(f"   {len(script_tts)} chars | {n_segs} segmentos de ~{CHARS_POR_SEG} chars")
print(f"   {N_IMGS} imagens únicas cicladas em {n_segs} segmentos")

if len(script_tts) < 500:
    sys.exit("Script muito curto para Long — use render_video_v8_standard.py")

# ── GROQ: 20 PROMPTS DE IMAGEM + N_SEGS CAPTIONS ─────────────────
def gerar_prompts_groq():
    """
    Uma chamada Groq retorna:
    - 20 prompts de imagem (para gerar o pool de 20 chibi únicos)
    - N_SEGS captions curtas (uma por segmento, max 25 chars)
    """
    if not GROQ_KEY:
        return gerar_fallback()

    system = f"""You are a creative director for @psidanielacoelho psychology channel.
Generate EXACTLY {N_IMGS} unique chibi image prompts for a pool of illustrations,
plus {n_segs} short caption labels for each speech segment.

Chibi prompts:
- Cover the full emotional arc of the video topic
- Style: "chibi anime flat design, kawaii psychology, cream background #F5F0E8, no text, original design"
- Each prompt must depict a DIFFERENT scene/emotion

Captions:
- One per segment, max 25 chars in Portuguese
- Should match the spoken text of that moment
- Last caption: "INSCREVA-SE AGORA 🔔"

Return ONLY valid JSON:
{{
  "image_prompts": ["prompt1", "prompt2", ... (exactly {N_IMGS})],
  "captions": ["caption1", "caption2", ... (exactly {n_segs})]
}}"""

    # Dividir script em N_SEGS segmentos para dar contexto ao Groq
    seg_size = len(script_tts) // n_segs
    segs_sample = []
    for i in range(min(n_segs, 30)):  # amostra de 30 segmentos
        start = i * seg_size
        segs_sample.append(script_tts[start:start+seg_size])

    user_msg = f"""Topic: {topic}
Script length: {len(script_tts)} chars, {n_segs} segments
First 30 segment samples:
{json.dumps(segs_sample, ensure_ascii=False)}

Generate {N_IMGS} image prompts + {n_segs} captions.
Image prompts must cover the full emotional/conceptual arc.
Captions must match each segment context."""

    for attempt in range(3):
        try:
            r = requests.post("https://api.groq.com/openai/v1/chat/completions",
                headers={"Authorization":f"Bearer {GROQ_KEY}","Content-Type":"application/json"},
                json={"model":"llama-3.3-70b-versatile",
                      "messages":[{"role":"system","content":system},
                                   {"role":"user","content":user_msg}],
                      "temperature":0.7,"max_tokens":8000},
                timeout=90)
            if r.status_code == 200:
                text = r.json()["choices"][0]["message"]["content"]
                match = re.search(r'\{.*\}', text, re.DOTALL)
                if match:
                    data = json.loads(match.group())
                    prompts  = data.get("image_prompts", [])
                    captions = data.get("captions", [])
                    if len(prompts) >= N_IMGS and len(captions) >= n_segs:
                        prompts  = prompts[:N_IMGS]
                        captions = captions[:n_segs]
                        captions[-1] = "INSCREVA-SE AGORA 🔔"
                        print(f"   ✅ Groq: {len(prompts)} prompts + {len(captions)} captions")
                        return prompts, captions
        except Exception as e:
            print(f"   Groq tentativa {attempt+1}: {e}")
            time.sleep(5)

    print("   ⚠️ Groq falhou → fallback")
    return gerar_fallback()

def gerar_fallback():
    STYLE = ("chibi anime flat design illustration, kawaii psychology, "
             "cream white background #F5F0E8, no text, original character not based on any IP")
    GIRL  = "chibi anime girl short dark hair professional warm smile"
    BOY   = "chibi anime boy dark hair navy shirt"

    prompts = [
        f"{GIRL} shocked surprised question mark floating, {STYLE}",
        f"three chibi figures one sinister glow subtle, {STYLE}",
        f"large warning sign {GIRL} alarmed, {STYLE}",
        f"{BOY} shushing secrets whisper, {STYLE}",
        f"magnifying glass hidden truth discovery, {STYLE}",
        f"chibi brain spotlight revelation, {STYLE}",
        f"{GIRL} and {BOY} cracked heart between them, {STYLE}",
        f"{BOY} smug golden star flawless perfect, {STYLE}",
        f"{GIRL} dizzy confused spiral stress, {STYLE}",
        f"STOP sign bold multiple silhouettes, {STYLE}",
        f"empty speech bubble erased invisible voice, {STYLE}",
        f"{BOY} blame arrow sad {GIRL} side, {STYLE}",
        f"professional chibi lab coat brain diagram, {STYLE}",
        f"green checkmark {GIRL} fist empowerment, {STYLE}",
        f"shield protection {GIRL} standing strong, {STYLE}",
        f"{BOY} mask friendly outside sinister shadow, {STYLE}",
        f"growth plant sprouting sunshine healing, {STYLE}",
        f"sunrise {GIRL} arms open freedom new day, {STYLE}",
        f"community chibi hands circle warmth support, {STYLE}",
        f"giant golden bell confetti {GIRL} celebrating subscribe, {STYLE}",
    ]

    # Captions cíclicas baseadas em posição no script
    cap_bank = [
        "Você reconhece?","O que é isso?","Atenção!","Segredos...",
        "Descoberta","Revelação","Como funciona?","Investigando",
        "O sinal","Cuidado!","Invisível","A culpa","A ciência",
        "Você pode!","Proteja-se","A máscara","Cura","Liberdade",
        "Apoio","Compartilha!","Empatia","Reflexão","Padrão oculto",
        "Isso muda tudo","Você não está só","Por que acontece?",
        "O que fazer?","Passo a passo","Resultado","INSCREVA-SE AGORA 🔔"
    ]
    captions = [cap_bank[i % len(cap_bank)] for i in range(n_segs)]
    captions[-1] = "INSCREVA-SE AGORA 🔔"
    return prompts[:N_IMGS], captions

print(f"\n🧠 Groq: gerando {N_IMGS} prompts + {n_segs} captions...")
IMAGE_PROMPTS, CAPTIONS = gerar_prompts_groq()

# ── GERAR POOL DE 20 IMAGENS ÚNICAS ──────────────────────────────
def gen_image(prompt, idx):
    """Idêntico ao Short — Pollinations → Gemini → Pillow."""
    full_prompt = (
        "Psych2Go animation style, kawaii chibi anime character, "
        "cream white background #F5F0E8, pastel warm colors, "
        f"round big expressive eyes, clean soft lines. {prompt}. "
        "Original character design not based on any existing IP, "
        "no text, no logos, no watermarks."
    )

    # 1. Pollinations.ai
    try:
        enc = urllib.parse.quote(full_prompt)
        url = (f"https://image.pollinations.ai/prompt/{enc}"
               f"?width=576&height=1024&seed={200+idx}&nologo=true&model=flux")
        r = requests.get(url, timeout=90)
        if r.status_code == 402:
            time.sleep(20)
            r = requests.get(url, timeout=90)
        if r.status_code == 200 and r.headers.get('content-type','').startswith('image'):
            tmp = f"{WORKDIR}/raw_{idx:02d}.jpg"
            with open(tmp,"wb") as f: f.write(r.content)
            img = Image.open(tmp).convert("RGB").resize((W,H),Image.LANCZOS)
            out = f"{WORKDIR}/pool_{idx:02d}.jpg"
            img.save(out,"JPEG",quality=92)
            return out, True
    except Exception:
        pass

    # 2. Gemini
    key = gemini_key()
    if key:
        for model in GEMINI_MODELS:
            try:
                url2 = (f"https://generativelanguage.googleapis.com/v1beta"
                        f"/models/{model}:generateContent?key={key}")
                r2 = requests.post(url2,
                    json={"contents":[{"parts":[{"text":full_prompt}]}],
                          "generationConfig":{"responseModalities":["IMAGE","TEXT"]}},
                    timeout=90)
                if r2.status_code == 429: rotate_key(); time.sleep(5); continue
                if r2.status_code == 200:
                    for cand in r2.json().get("candidates",[]):
                        for part in cand.get("content",{}).get("parts",[]):
                            if "inlineData" in part:
                                raw = base64.b64decode(part["inlineData"]["data"])
                                tmp = f"{WORKDIR}/raw_{idx:02d}.jpg"
                                with open(tmp,"wb") as f: f.write(raw)
                                img = Image.open(tmp).convert("RGB")
                                aw,ah = img.size; t = 9/16
                                if aw/ah > t:
                                    nw=int(ah*t); img=img.crop(((aw-nw)//2,0,(aw+nw)//2,ah))
                                elif aw/ah < t:
                                    nh=int(aw/t); img=img.crop((0,(ah-nh)//2,aw,(ah+nh)//2))
                                img = img.resize((W,H),Image.LANCZOS)
                                out = f"{WORKDIR}/pool_{idx:02d}.jpg"
                                img.save(out,"JPEG",quality=92)
                                return out, True
            except Exception:
                continue

    # 3. Pillow fallback
    img = Image.new("RGB",(W,H),(245,240,232))
    draw = ImageDraw.Draw(img)
    for y in range(H):
        t=y/H; rv=int(245+(235-245)*t); gv=int(240+(228-240)*t); bv=int(232+(220-232)*t)
        draw.line([(0,y),(W,y)],fill=(rv,gv,bv))
    cx,cy = W//2,H//2
    # Variar aparência do personagem por idx
    cores_roupa = [(130,80,200),(80,130,200),(200,80,130),(80,200,130),(200,150,80)]
    cor = cores_roupa[idx % len(cores_roupa)]
    draw.ellipse([cx-120,cy-220,cx+120,cy+40],fill=(255,220,180))
    draw.ellipse([cx-125,cy-270,cx+125,cy-100],fill=(60,40,20))
    draw.ellipse([cx-60,cy-100,cx-20,cy-60],fill=(30,20,10))
    draw.ellipse([cx+20,cy-100,cx+60,cy-60],fill=(30,20,10))
    draw.ellipse([cx-55,cy-95,cx-45,cy-85],fill=(255,255,255))
    draw.ellipse([cx+25,cy-95,cx+35,cy-85],fill=(255,255,255))
    draw.arc([cx-40,cy-30,cx+40,cy+20],start=0,end=180,fill=(200,80,80),width=5)
    draw.rounded_rectangle([cx-100,cy+40,cx+100,cy+300],radius=20,fill=cor)
    draw.ellipse([cx-110,cy-60,cx-60,cy-20],fill=(255,180,180))
    draw.ellipse([cx+60,cy-60,cx+110,cy-20],fill=(255,180,180))
    out = f"{WORKDIR}/pool_{idx:02d}.jpg"
    img.save(out,"JPEG",quality=85)
    return out, False

# ── OVERLAY PADRÃO ETERNO (base — sem caption, aplicada depois) ──
def add_base_overlay(img_path):
    """Lower third permanente — idêntico ao Short."""
    img = Image.open(img_path).convert("RGB")
    draw = ImageDraw.Draw(img)
    lt_h = 95
    draw.rectangle([0,H-lt_h,W,H],fill=(8,6,18))
    draw.rectangle([0,H-lt_h,5,H],fill=VERM)
    draw.text((22,H-lt_h+12),"psi",fill=GOLD)
    draw.text((62,H-lt_h+10),"Daniela Coelho",fill=BRAN)
    draw.text((62,H-lt_h+40),"Saude Mental  |  @psidanielacoelho",fill=LILAS)
    draw.rectangle([0,H-4,W,H],fill=VERM)
    img.save(img_path,"JPEG",quality=95)
    return img_path

def make_frame(pool_path, caption, seg_idx):
    """
    Cria frame final para um segmento:
    - Copia a imagem do pool
    - Adiciona caption badge específico desta cena
    (lower third já está no pool)
    """
    frame_path = f"{WORKDIR}/frame_{seg_idx:04d}.jpg"
    img = Image.open(pool_path).convert("RGB")
    draw = ImageDraw.Draw(img)

    # Caption badge no TOPO — muda a cada segmento (palavra a palavra)
    if caption:
        cap = caption[:28].upper()
        cap_w = min(len(cap)*14+44, W-60)
        cx = W//2; cap_y = 56
        draw.rounded_rectangle([cx-cap_w//2,cap_y-24,cx+cap_w//2,cap_y+24],
                                radius=15, fill=(245,245,255))
        draw.rounded_rectangle([cx-cap_w//2,cap_y-24,cx+cap_w//2,cap_y+24],
                                radius=15, outline=(200,200,220), width=2)
        draw.text((cx-cap_w//2+22,cap_y-10), cap, fill=(20,15,45))

    img.save(frame_path,"JPEG",quality=90)
    return frame_path

# GERAR POOL
print(f"\n🎨 Gerando {N_IMGS} imagens únicas (pool)...")
t0 = time.time()
POOL = [None]*N_IMGS
n_ai = n_fb = 0

def gen_pool_img(args):
    i, prompt = args
    print(f"   [{i+1:02d}/{N_IMGS}] Gerando imagem pool...")
    path, is_ai = gen_image(prompt, i)
    add_base_overlay(path)  # lower third permanente
    sz = os.path.getsize(path)//1024
    print(f"   [{i+1:02d}/{N_IMGS}] {'✅ AI' if is_ai else '⚠️  Fallback'} ({sz}KB)")
    return path, is_ai

with ThreadPoolExecutor(max_workers=4) as ex:
    futures = {ex.submit(gen_pool_img,(i,p)):i for i,p in enumerate(IMAGE_PROMPTS)}
    for fut in as_completed(futures):
        i = futures[fut]
        path, is_ai = fut.result()
        POOL[i] = path
        if is_ai: n_ai += 1
        else: n_fb += 1
        time.sleep(2)

gen_t = time.time()-t0
print(f"\n   ✅ {n_ai}/{N_IMGS} AI | {n_fb} fallback | {gen_t:.1f}s")

# ── ÁUDIO ─────────────────────────────────────────────────────────
print(f"\n🎙️  Áudio...")

async def _tts():
    import edge_tts
    c = edge_tts.Communicate(script_tts, voice="pt-BR-AntonioNeural")
    await c.save(f"{WORKDIR}/audio.mp3")

if video.get("audio_url"):
    print("   Usando áudio existente do DB...")
    ar = requests.get(video["audio_url"], timeout=120)
    ar.raise_for_status()
    with open(f"{WORKDIR}/audio.mp3","wb") as f: f.write(ar.content)
else:
    asyncio.run(_tts())

probe = subprocess.run(
    ["ffprobe","-v","quiet","-print_format","json","-show_format",
     f"{WORKDIR}/audio.mp3"],
    capture_output=True, text=True)
DUR_AUDIO = float(json.loads(probe.stdout)["format"]["duration"])

# RATE_REAL: NUNCA hardcoded
RATE_REAL = len(script_tts) / DUR_AUDIO
print(f"   {DUR_AUDIO:.1f}s ({DUR_AUDIO/60:.1f}min) | RATE_REAL={RATE_REAL:.3f} chars/s")

# ── TIMING: N_SEGS SEGMENTOS COM DURAÇÃO PROPORCIONAL ─────────────
# Cada segmento dura proporcional aos seus chars (igual ao Short)
seg_size = len(script_tts) // n_segs
durs = []
for i in range(n_segs):
    chars = seg_size if i < n_segs-1 else len(script_tts) - i*seg_size
    durs.append(max(0.5, round(chars/RATE_REAL, 3)))

soma = sum(durs)
secs_media = soma/n_segs
print(f"   {n_segs} segmentos | {secs_media:.1f}s/segmento | soma={soma:.1f}s")

# ── GERAR FRAMES (ciclar pool + caption por segmento) ─────────────
print(f"\n🖼️  Gerando {n_segs} frames (caption palavra a palavra)...")
FRAMES = []
for i in range(n_segs):
    pool_idx = i % N_IMGS           # cicla o pool de 20 imagens
    caption  = CAPTIONS[i] if i < len(CAPTIONS) else ""
    frame    = make_frame(POOL[pool_idx], caption, i)
    FRAMES.append(frame)
    if (i+1) % 50 == 0:
        print(f"   {i+1}/{n_segs} frames gerados...")

print(f"   ✅ {len(FRAMES)} frames prontos")

# ── FFCONCAT ─────────────────────────────────────────────────────
concat_file = f"{WORKDIR}/concat.txt"
with open(concat_file,"w") as f:
    for frame, dur in zip(FRAMES, durs):
        f.write(f"file '{frame}'\nduration {dur:.3f}\n")
    if FRAMES: f.write(f"file '{FRAMES[-1]}'\n")

# ── RENDER FFMPEG ─────────────────────────────────────────────────
print(f"\n🎬 Renderizando (crf={CRF}, ~15-20MB)...")
ts = int(time.time())
out_mp4 = f"{WORKDIR}/v{VIDEO_ID}_long_v8std_{ts}.mp4"

cmd = [
    "ffmpeg","-y",
    "-f","concat","-safe","0","-i",concat_file,
    "-i",f"{WORKDIR}/audio.mp3",
    "-c:v","libx264","-pix_fmt","yuv420p",
    "-c:a","aac","-b:a","128k",
    "-shortest","-r","25","-crf",str(CRF),
    "-vf","scale=1080:1920:force_original_aspect_ratio=decrease,"
          "pad=1080:1920:(ow-iw)/2:(oh-ih)/2:color=0xF5F0E8,setsar=1",
    "-movflags","+faststart",
    out_mp4
]
res = subprocess.run(cmd, capture_output=True, text=True, timeout=3600)
if res.returncode != 0:
    print(f"ERRO FFMPEG:\n{res.stderr[-2000:]}")
    sys.exit(1)

sz    = os.path.getsize(out_mp4)
probe2 = subprocess.run(
    ["ffprobe","-v","quiet","-print_format","json","-show_format",out_mp4],
    capture_output=True, text=True)
dur2  = float(json.loads(probe2.stdout)["format"]["duration"])
print(f"   ✅ {sz//1024//1024}MB ({sz//1024}KB) | {dur2:.1f}s ({dur2/60:.1f}min)")

# ── UPLOAD + UPDATE DB ─────────────────────────────────────────────
print(f"\n☁️  Upload Supabase...")
if not video.get("audio_url"):
    with open(f"{WORKDIR}/audio.mp3","rb") as f: adata = f.read()
    audio_url = sb_upload(f"audios/v{VIDEO_ID}_long_{ts}.mp3",adata,"audio/mpeg")
    sb_patch("content_pipeline",VIDEO_ID,{"audio_url":audio_url})

with open(out_mp4,"rb") as f: vdata = f.read()
video_url = None
for attempt in range(5):
    try:
        video_url = sb_upload(f"mp4s/v{VIDEO_ID}_long_v8std_{ts}.mp4",vdata,"video/mp4")
        print("   ✅ Upload OK")
        break
    except Exception as e:
        print(f"   Tentativa {attempt+1}: {e}")
        time.sleep(10)

if video_url:
    sb_patch("content_pipeline",VIDEO_ID,{
        "video_url": video_url,
        "status": "pending_credentials",
        "metadata": json.dumps({
            "render_version": "v8_long_standard",
            "n_imgs_pool": N_IMGS,
            "n_segments": n_segs,
            "chars_por_seg": CHARS_POR_SEG,
            "secs_por_seg": round(secs_media,2),
            "n_ai": n_ai, "n_fallback": n_fb,
            "audio_dur_s": round(DUR_AUDIO,1),
            "video_dur_s": round(dur2,1),
            "video_dur_min": round(dur2/60,1),
            "file_mb": round(sz/1024/1024,1),
            "crf": CRF, "rate_real": round(RATE_REAL,3),
        })
    })

print(f"\n{'='*60}")
print(f"  ✅ LONG V8 — #{VIDEO_ID}")
print(f"  🎬 {video_url}")
print(f"  {n_ai}/{N_IMGS} AI | {sz//1024//1024}MB | {dur2/60:.1f}min")
print(f"  ~{secs_media:.1f}s/imagem | {n_segs} segmentos caption")
print(f"{'='*60}\n")
