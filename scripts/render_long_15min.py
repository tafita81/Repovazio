#!/usr/bin/env python3
"""
render_long_15min.py — LONG 15MIN QUÂNTICO V2
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
PADRÃO 3 SEGUNDOS (Psych2Go style):
  ✅ 300 cenas × 3s = 900s = 15:00 EXATOS
  ✅ 100 imgs únicas Pollinations FLUX
  ✅ Cada imagem aparece 3× com Ken Burns (zoom 0% / 4% / 8%)
  ✅ Cena nova a cada 3s = padrão Psych2Go comprovado
  ✅ 5 atos narrativos + mid-rolls 03/06/09/12min
  ✅ Script: 300 segmentos × ~40 chars = 12.000 chars = 15min exatos
  ✅ RATE_ADJ = "+0%" (naturalmente 15min, sem ajuste)
  ✅ 27 min geração (dentro dos 90min GitHub Actions)
"""
import os, sys, json, subprocess, requests, time, urllib.parse, asyncio, re
from PIL import Image, ImageDraw, ImageFilter, ImageEnhance

VIDEO_ID = int(os.environ.get("VIDEO_ID","683"))
SB_URL   = "https://tpjvalzwkqwttvmszvie.supabase.co"
SB_KEY   = os.environ.get("SUPABASE_SERVICE_KEY","")
W, H     = 1080, 1920
CRF      = 22
FPS      = 25
TARGET_S = 900      # 15:00 exatos
IMG_INTERVAL = 3    # 3 segundos por aparência (Psych2Go style)
N_APPEAR = TARGET_S // IMG_INTERVAL   # 300 aparências totais
N_UNIQUE = N_APPEAR // 3              # 100 imagens únicas
N_VARIATIONS = 3                      # cada imagem aparece 3× (zoom 0/4/8%)
RATE_ADJ = "+0%"                      # 12.000 chars / 13.3 = 902s ≈ 15min
WORKDIR  = f"/tmp/v{VIDEO_ID}_long15"
os.makedirs(WORKDIR, exist_ok=True)

VERM=(220,50,50); GOLD=(255,210,50); BRAN=(255,255,255)
LILAS=(185,170,225); DARK=(8,6,18)
def log(m): print(m, flush=True)

# ── PERSONAGENS ─────────────────────────────────────────────
DANIELA = "kawaii chibi anime girl, short dark bob hair, mint-green blouse, gold psi pin, warm knowing smile, big expressive eyes"
SARA    = "kawaii chibi anime girl, wavy auburn hair, round glasses, yellow cardigan, emotional big expressive eyes"
MARCOS  = "kawaii chibi anime man, styled dark hair, navy blazer, charming calculating smile, subtle sinister aura"
JULIA   = "kawaii chibi anime girl, curly dark hair, orange sweater, warm protective caring expression"
ANA     = "kawaii chibi anime woman, dark bun, white lab coat, clipboard, calm authoritative expression"
LUCAS   = "kawaii chibi anime man, navy hoodie, tousled hair, introspective thoughtful expression"
STYLE   = ("Psych2Go anime flat illustration, soft cream background #F5F0E8, "
           "pastel colors, clean line art, original character design, no text, no watermarks")

# ── DETECÇÃO AUTOMÁTICA DE PERSONAGEM E CENA ────────────────
def detect_scene(text, img_idx, n_unique):
    """Gera prompt Pollinations baseado no conteúdo do segmento"""
    t = text.lower()
    pos = img_idx / n_unique  # 0.0 → 1.0 ao longo do vídeo

    # Posição no arco narrativo (5 atos)
    if pos < 0.13:
        ato = "GANCHO"; mood = "dramatic entrance hook opening, impactful visual"
    elif pos < 0.35:
        ato = "PROBLEMA"; mood = "conflict tension emotional problem revealed"
    elif pos < 0.60:
        ato = "CIENCIA"; mood = "educational analytical scientific discovery"
    elif pos < 0.80:
        ato = "VIRADA"; mood = "breakthrough turning point hope emerging"
    else:
        ato = "CTA"; mood = "warm empowering celebration gratitude"

    # Personagem por conteúdo
    if any(k in t for k in ["daniela","pergunta","você está","olha pra"]):
        char, cname = DANIELA, "Daniela"
    elif any(k in t for k in ["dra","ana ","harvard","estudo","pesquisa","neurolog","cérebro","dopamina","cortisol"]):
        char, cname = ANA, "Dra Ana"
    elif any(k in t for k in ["julia","amiga ","disse a"]):
        char, cname = JULIA, "Julia"
    elif any(k in t for k in ["marcos","narcis","manipul","gaslighting","ele disse"]):
        char, cname = MARCOS, "Marcos"
    elif any(k in t for k in ["lucas"]):
        char, cname = LUCAS, "Lucas"
    elif pos > 0.85:
        char, cname = DANIELA, "Daniela"
    else:
        char, cname = SARA, "Sara"

    # Cena específica por keywords
    for kw, scene in [
        (["sinal 1","primeiro sinal"],
         f"Large glowing badge ONE in center, {char} beside it with serious expression, {mood}"),
        (["sinal 2","segundo sinal"],
         f"Large glowing badge TWO in center, {char} beside it with concerned expression, {mood}"),
        (["sinal 3","terceiro sinal"],
         f"Large glowing badge THREE in center, {char} beside it with urgent expression, {mood}"),
        (["harvard","94%","92%","estudo mostra"],
         f"{ANA} holding clipboard with Harvard logo and percentage statistic, research data visible, {mood}"),
        (["cérebro","neurolog","cortisol","dopamina","amígdala"],
         f"{ANA} pointing at glowing detailed brain diagram showing neural pathways, {mood}"),
        (["gaslighting","não aconteceu","está exagerando","é você que"],
         f"{SARA} and {MARCOS} in tense confrontation, Marcos pointing dismissively, Sara shrinking, {mood}"),
        (["chora","lágrima","chora","dor profunda","sofreu"],
         f"{SARA} with visible tears streaming, small rain cloud above, deeply emotional, {mood}"),
        (["ferramenta","passo a passo","como fazer","técnica","exercício"],
         f"{DANIELA} holding golden glowing step-by-step guide or toolkit, instructive and warm, {mood}"),
        (["inscreva","🔔","sino","notif","próximo vídeo"],
         f"Giant golden glowing notification bell with sparkles, {DANIELA} {SARA} {JULIA} celebrating together, confetti, {mood}"),
        (["se recuperou","3 meses","depois","transformação","mudou"],
         f"{SARA} standing tall and bright, before-and-after transformation, hope and healing, {mood}"),
    ]:
        if any(k in t for k in kw):
            return scene, cname, ato

    # Cena genérica por posição
    if pos < 0.05:
        return f"{SARA} alone at night, anxious expression, small question marks floating, hook scene, {mood}", cname, ato
    elif pos > 0.88:
        return f"{DANIELA} making warm direct eye contact with viewer, hand on heart, golden light, most intimate moment, {mood}", cname, ato
    else:
        return f"{char} with expression matching {ato.lower()} narrative mood, clear emotional story, {mood}", cname, ato

# ── KEN BURNS — 3 VARIAÇÕES POR IMAGEM ──────────────────────
def make_variants(src_path, base_idx):
    """Gera 3 variações Ken Burns por imagem (zoom 0%, 4%, 8%)"""
    variants = []
    try:
        orig = Image.open(src_path).convert("RGB")
        w, h = orig.size
        for v, zoom in enumerate([0.0, 0.04, 0.08]):
            if zoom == 0.0:
                variants.append(src_path)
            else:
                dw = int(w * zoom / 2); dh = int(h * zoom / 2)
                cropped = orig.crop([dw, dh, w-dw, h-dh])
                resized = cropped.resize((w, h), Image.LANCZOS)
                vpath = f"{WORKDIR}/v{base_idx:03d}_{v}.jpg"
                resized.save(vpath, "JPEG", quality=94)
                variants.append(vpath)
    except Exception as e:
        log(f"  Variante erro: {e}")
        variants = [src_path] * 3
    return variants

# ── SUPABASE ────────────────────────────────────────────────
def sb_get_script():
    SCRIPT_ENV = os.environ.get("SCRIPT_LONG","")
    if SCRIPT_ENV and len(SCRIPT_ENV) > 500:
        return SCRIPT_ENV
    r = requests.get(
        f"{SB_URL}/rest/v1/content_pipeline?id=eq.{VIDEO_ID}&select=script,title",
        headers={"apikey":SB_KEY,"Authorization":f"Bearer {SB_KEY}"}, timeout=30)
    rows = r.json()
    if rows and rows[0].get("script"):
        return rows[0]["script"]
    raise ValueError(f"Script não encontrado para video_id={VIDEO_ID}")

def sb_patch(id_, data):
    requests.patch(f"{SB_URL}/rest/v1/content_pipeline?id=eq.{id_}",
        headers={"apikey":SB_KEY,"Authorization":f"Bearer {SB_KEY}",
                 "Content-Type":"application/json","Prefer":"return=minimal"},
        json=data, timeout=30).raise_for_status()

def sb_upload(path, data, ctype):
    r = requests.post(f"{SB_URL}/storage/v1/object/videos/{path}",
        headers={"apikey":SB_KEY,"Authorization":f"Bearer {SB_KEY}",
                 "Content-Type":ctype,"x-upsert":"true"},
        data=data, timeout=600)
    r.raise_for_status()
    return f"{SB_URL}/storage/v1/object/public/videos/{path}"

# ── SPLIT: 300 SEGMENTOS × ~40 CHARS ────────────────────────
def split_script_300(raw_script):
    """Divide script em 300 segmentos curtos (~40 chars = ~3s de fala)"""
    text = re.sub(r'\s+', ' ', raw_script.strip())
    total = len(text)
    target_seg_len = total / N_APPEAR  # chars por segmento

    # Split por frase primeiro
    sentences = re.split(r'(?<=[.!?])\s+', text)
    sentences = [s.strip() for s in sentences if s.strip()]

    # Depois por vírgula se frases ainda muito longas
    fine = []
    for s in sentences:
        if len(s) > target_seg_len * 1.8:
            parts = re.split(r'(?<=,)\s+', s)
            fine.extend([p.strip() for p in parts if p.strip()])
        else:
            fine.append(s)
    sentences = fine

    # Merge para atingir N_APPEAR segmentos
    segments = []
    current = ""
    for s in sentences:
        if current and len(current) + len(s) + 1 > target_seg_len * 1.4 and len(current) > target_seg_len * 0.4:
            segments.append(current.strip())
            current = s
        else:
            current = (current + " " + s).strip() if current else s
    if current:
        segments.append(current.strip())

    # Ajuste fino para N_APPEAR exato
    while len(segments) < N_APPEAR:
        longest = max(range(len(segments)), key=lambda i: len(segments[i]))
        seg = segments[longest]
        mid = len(seg)//2
        cut = seg.rfind(' ', max(0,mid-20), mid+20)
        if cut < 1: cut = mid
        segments[longest] = seg[:cut].strip()
        segments.insert(longest+1, seg[cut:].strip())

    while len(segments) > N_APPEAR:
        min_sum = float('inf'); merge_at = 0
        for i in range(len(segments)-1):
            s = len(segments[i]) + len(segments[i+1])
            if s < min_sum: min_sum = s; merge_at = i
        segments[merge_at] = (segments[merge_at] + " " + segments[merge_at+1]).strip()
        segments.pop(merge_at+1)

    log(f"  Split: {len(sentences)} frases → {len(segments)} segmentos de ~{sum(len(s) for s in segments)//len(segments)} chars")
    return segments

# ── UTILITÁRIOS ──────────────────────────────────────────────
def measure_dur(path):
    p = subprocess.run(["ffprobe","-v","quiet","-print_format","json","-show_format",path],
        capture_output=True, text=True)
    return float(json.loads(p.stdout)["format"]["duration"])

def add_overlay(img_path, caption, ato_color):
    img  = Image.open(img_path).convert("RGB")
    draw = ImageDraw.Draw(img)
    draw.rectangle([0,H-100,W,H], fill=DARK)
    draw.rectangle([0,H-100,6,H], fill=VERM)
    draw.rectangle([0,H-4,W,H], fill=VERM)
    draw.text((22,H-90), "ψ", fill=GOLD)
    draw.text((62,H-88), "Daniela Coelho", fill=BRAN)
    draw.text((62,H-58), "Saúde Mental  |  @psidanielacoelho", fill=LILAS)
    if caption:
        cap = caption[:28].upper()
        bw  = min(len(cap)*14+50, W-60); cx = W//2
        draw.rounded_rectangle([cx-bw//2,38,cx+bw//2,80],
            radius=14, fill=(250,248,255), outline=(210,200,235), width=2)
        draw.text((cx-bw//2+20,48), cap, fill=(20,15,45))
    img.save(img_path, "JPEG", quality=95)

def gen_pillow(idx):
    img = Image.new("RGB",(W,H),(245,240,232))
    draw = ImageDraw.Draw(img)
    cols=[(150,80,210),(200,100,60),(60,120,200),(200,60,100),(60,180,100)]
    for y in range(H):
        t=y/H; draw.line([(0,y),(W,y)],fill=(int(245+(230-245)*t),int(240+(225-240)*t),int(232+(215-232)*t)))
    for ci,cx in enumerate([W//3,2*W//3]):
        c=cols[(idx+ci)%len(cols)]; cy=H//2-80
        draw.ellipse([cx-80,cy-190,cx+80,cy+30],fill=(255,220,185))
        draw.ellipse([cx-84,cy-240,cx+84,cy-80],fill=(40,28,12))
        draw.rounded_rectangle([cx-68,cy+25,cx+68,cy+230],radius=20,fill=c)
    out=f"{WORKDIR}/ai_{idx:03d}.jpg"; img.save(out,"JPEG",quality=88)
    return out

# ── MAIN ──────────────────────────────────────────────────────
log(f"{'='*60}")
log(f"  ψ LONG 15MIN QUÂNTICO V2 — VIDEO #{VIDEO_ID}")
log(f"  {N_APPEAR} aparências × {IMG_INTERVAL}s = {TARGET_S}s = 15:00 EXATOS")
log(f"  {N_UNIQUE} imgs únicas × {N_VARIATIONS} Ken Burns = {N_APPEAR} cenas")
log(f"  Cena nova a cada {IMG_INTERVAL}s (padrão Psych2Go)")
log(f"  Mid-rolls: 03:00 | 06:00 | 09:00 | 12:00")
log(f"{'='*60}\n")

# ── ETAPA 0: SCRIPT ─────────────────────────────────────────
log("📖 ETAPA 0 — Carregando e dividindo script...")
raw_script = sb_get_script()
log(f"  Script: {len(raw_script)} chars")
SEGMENTOS = split_script_300(raw_script)
SCRIPT_TTS = ". ".join(SEGMENTOS)
log(f"  {len(SEGMENTOS)} segmentos | TTS: {len(SCRIPT_TTS)} chars")
log(f"  Estimado: {len(SCRIPT_TTS)/13.3:.0f}s = {len(SCRIPT_TTS)/13.3/60:.2f}min")

# ── ETAPA 1: ÁUDIO TTS ──────────────────────────────────────
log(f"\n🎙️  ETAPA 1 — Áudio 15min (AntonioNeural {RATE_ADJ})...")

async def gen_audio():
    import edge_tts
    path = f"{WORKDIR}/audio_long.mp3"
    c = edge_tts.Communicate(SCRIPT_TTS, voice="pt-BR-AntonioNeural", rate=RATE_ADJ)
    await c.save(path)
    return path

asyncio.run(gen_audio())
AUDIO_PATH = f"{WORKDIR}/audio_long.mp3"
DUR_FINAL  = measure_dur(AUDIO_PATH)
RATE_REAL  = len(SCRIPT_TTS) / DUR_FINAL
log(f"  ✅ {DUR_FINAL:.1f}s = {DUR_FINAL/60:.2f}min | RATE={RATE_REAL:.2f} chars/s")

# ── ETAPA 2: DURAÇÕES POR SEGMENTO ──────────────────────────
# Cada segmento exibe por tempo proporcional (baseado em chars)
DURS = [max(0.2, round(len(s)/RATE_REAL, 3)) for s in SEGMENTOS]
log(f"\n  Média por segmento: {sum(DURS)/len(DURS):.2f}s | min: {min(DURS):.2f}s | max: {max(DURS):.2f}s")

# ── ETAPA 3: GERAR 100 IMAGENS ÚNICAS ───────────────────────
# Segmentos 0,1,2 → imagem 0 | segmentos 3,4,5 → imagem 1 | etc.
log(f"\n🎨 ETAPA 3 — Gerando {N_UNIQUE} imgs Pollinations FLUX (~27 min)...")
log(f"  Cada img mostrada {N_VARIATIONS}× com Ken Burns zoom 0/4/8%")

UNIQUE_IMGS = [None] * N_UNIQUE
ATOS_MAP    = []
counts      = {"poll":0,"pillow":0}
t0          = time.time()

for img_idx in range(N_UNIQUE):
    # Pegar o segmento representativo deste grupo (o do meio)
    seg_idx = img_idx * N_VARIATIONS + 1   # segmento do meio do grupo
    seg = SEGMENTOS[min(seg_idx, len(SEGMENTOS)-1)]

    cena_desc, char_name, ato = detect_scene(seg, img_idx, N_UNIQUE)
    ATOS_MAP.append(ato)

    full = (f"masterpiece, best quality, kawaii chibi anime illustration, "
            f"{cena_desc}, {STYLE} "
            f"### lowres, bad anatomy, text, watermark, nsfw, blurry, ugly")
    enc  = urllib.parse.quote(full[:800])
    seed = 3333 + img_idx * 97
    out  = f"{WORKDIR}/ai_{img_idx:03d}.jpg"
    ok   = False

    for attempt in range(4):
        try:
            url = (f"https://image.pollinations.ai/prompt/{enc}"
                   f"?width=576&height=1024&seed={seed+attempt}"
                   f"&nologo=true&model=flux&enhance=true")
            r = requests.get(url, timeout=90)
            if r.status_code == 402:
                log(f"  [{img_idx+1}] Rate limit, 30s..."); time.sleep(30); continue
            if r.status_code == 200 and 'image' in r.headers.get('content-type',''):
                if len(r.content) > 40000:
                    with open(f"{WORKDIR}/raw_{img_idx:03d}.jpg",'wb') as f: f.write(r.content)
                    img = Image.open(f"{WORKDIR}/raw_{img_idx:03d}.jpg").convert("RGB")
                    img = img.resize((W,H), Image.LANCZOS)
                    img.save(out,"JPEG",quality=95)
                    cap = seg[:25].split('.')[0].strip()
                    add_overlay(out, cap, ato)
                    elapsed = time.time()-t0
                    sz = os.path.getsize(out)//1024
                    log(f"  [{img_idx+1:03d}/{N_UNIQUE}] 🌐 {sz}KB | {elapsed/60:.1f}min | [{ato}] {char_name}: {seg[:40]}...")
                    UNIQUE_IMGS[img_idx]=out; counts["poll"]+=1; ok=True; break
        except Exception as e:
            log(f"  [{img_idx+1}] err {attempt+1}: {str(e)[:40]}")
        if attempt < 3: time.sleep(8)

    if not ok:
        out = gen_pillow(img_idx)
        add_overlay(out, seg[:25], ato)
        UNIQUE_IMGS[img_idx]=out; counts["pillow"]+=1
        log(f"  [{img_idx+1:03d}/{N_UNIQUE}] ✏️  pillow | [{ato}] {seg[:40]}...")

    if img_idx < N_UNIQUE-1: time.sleep(4)

gen_t = time.time()-t0
log(f"\n  ✅ {counts['poll']}/{N_UNIQUE} Pollinations | {counts['pillow']} Pillow | {gen_t/60:.1f}min")

# ── ETAPA 4: KEN BURNS VARIANTS + FFCONCAT ──────────────────
log(f"\n📝 ETAPA 4 — Ken Burns + ffconcat ({N_APPEAR} aparências × {IMG_INTERVAL}s)...")

# Gerar 3 variantes por imagem
ALL_VARIANTS = []
for img_idx, src in enumerate(UNIQUE_IMGS):
    if src:
        vs = make_variants(src, img_idx)
    else:
        vs = [UNIQUE_IMGS[0]] * 3 if UNIQUE_IMGS[0] else [gen_pillow(0)] * 3
    ALL_VARIANTS.append(vs)
    if (img_idx+1) % 20 == 0:
        log(f"  Variantes: {img_idx+1}/{N_UNIQUE}")

# Montar ffconcat: segmento i → imagem i//3, variante i%3
concat = f"{WORKDIR}/concat.txt"
with open(concat,'w') as f:
    for seg_idx, (seg, dur) in enumerate(zip(SEGMENTOS, DURS)):
        img_idx = seg_idx // N_VARIATIONS        # qual imagem única
        var_idx = seg_idx %  N_VARIATIONS        # qual variante (0/1/2)
        img_path = ALL_VARIANTS[img_idx][var_idx]
        f.write(f"file '{img_path}'\nduration {dur:.3f}\n")
    # última linha obrigatória
    last = ALL_VARIANTS[-1][0]
    f.write(f"file '{last}'\n")

# ── ETAPA 5: RENDER ─────────────────────────────────────────
ts  = int(time.time())
OUT = f"{WORKDIR}/v{VIDEO_ID}_long15_{ts}.mp4"
log(f"\n🎬 ETAPA 5 — Renderizando {DUR_FINAL:.0f}s Long (15min)...")

cmd = ["ffmpeg","-y","-f","concat","-safe","0","-i",concat,
       "-i",AUDIO_PATH,
       "-c:v","libx264","-pix_fmt","yuv420p","-crf",str(CRF),
       "-c:a","aac","-b:a","128k","-shortest",
       "-r",str(FPS),
       "-vf","scale=1080:1920:force_original_aspect_ratio=decrease,"
             "pad=1080:1920:(ow-iw)/2:(oh-ih)/2:color=0xF5F0E8,setsar=1",
       "-movflags","+faststart",OUT]
res = subprocess.run(cmd, capture_output=True, text=True, timeout=1200)
if res.returncode != 0:
    log(f"ERRO:\n{res.stderr[-800:]}"); sys.exit(1)

sz   = os.path.getsize(OUT)
dur2 = measure_dur(OUT)
ok15 = abs(dur2 - TARGET_S) <= 30
log(f"  {'✅' if ok15 else '⚠️ '} {sz/1024/1024:.1f}MB | {dur2:.0f}s = {dur2/60:.2f}min")

# ── ETAPA 6: CHAPTERS YOUTUBE ────────────────────────────────
chapters = "\n".join([
    "00:00 ⚡ O Que É Narcisismo Encoberto?",
    "03:00 🚨 Os 3 Sinais Que Você Está Ignorando",
    "06:00 🧠 A Ciência Por Trás da Manipulação",
    "09:00 💡 Como Identificar e Se Proteger",
    "12:00 ❤️ Você Não Está Sozinha — A Transformação",
])
log(f"\n📌 CHAPTERS:\n{chapters}")

# ── ETAPA 7: UPLOAD ──────────────────────────────────────────
log(f"\n☁️  ETAPA 7 — Upload Supabase...")
with open(OUT,'rb') as f: vdata=f.read()
video_url=None
for att in range(5):
    try:
        video_url = sb_upload(f"mp4s/v{VIDEO_ID}_long15_{ts}.mp4", vdata, "video/mp4")
        log(f"  ✅ {video_url}"); break
    except Exception as e:
        log(f"  Tentativa {att+1}: {e}"); time.sleep(15)

if video_url:
    sb_patch(VIDEO_ID, {
        "video_url": video_url, "status": "pending_credentials",
        "metadata": json.dumps({
            "version":"long_15min_v2_3s_quantum",
            "dur_s": round(dur2,1), "target_s": TARGET_S,
            "img_interval_s": IMG_INTERVAL,
            "n_appear": N_APPEAR, "n_unique": N_UNIQUE,
            "n_variations": N_VARIATIONS,
            "poll": counts["poll"], "pillow": counts["pillow"],
            "file_mb": round(sz/1024/1024,1),
            "chapters": chapters,
            "mid_rolls_at": ["03:00","06:00","09:00","12:00"],
        })
    })

log(f"\n{'='*60}")
log(f"  ψ LONG 15MIN V2 — RESULTADO FINAL")
log(f"  ⏱️  {dur2:.0f}s = {dur2/60:.2f}min (target: 15:00)")
log(f"  🌐 {counts['poll']}/{N_UNIQUE} Pollinations FLUX")
log(f"  📸 {N_APPEAR} cenas × {IMG_INTERVAL}s = 300 cortes totais")
log(f"  ✂️  Cena nova a cada {IMG_INTERVAL}s (padrão Psych2Go)")
log(f"  💰 Mid-rolls: 03:00 | 06:00 | 09:00 | 12:00")
log(f"  💾 {sz/1024/1024:.1f}MB")
log(f"  🎬 {video_url or 'UPLOAD FALHOU'}")
log(f"{'='*60}\n")
