#!/usr/bin/env python3
"""
render_long_v8_standard.py — LONGS 15min | PADRÃO ETERNO psicologia.doc
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
IDÊNTICO ao render_video_v8_standard.py (Shorts), com adaptações para Long:
  - N_CENAS = 50 (vs 20 nos Shorts)
  - CRF = 22  (vs 25 nos Shorts → ~15-20MB para 15min)
  - Scripts: 10K-16K chars (vs ~800 nos Shorts)
  - Estrutura com CAPÍTULOS (5 partes × 10 cenas cada)
  - Mesma imagem, overlay, áudio, timing — PADRÃO ETERNO intacto

VISUAL (idêntico ao Short #683):
  - Chibi kawaii Psych2Go style, fundo creme #F5F0E8
  - Caption badge no TOPO por cena
  - Lower third: psi | Daniela Coelho | Saude Mental | @psidanielacoelho
  - SEM Psicóloga até jan/2027

$0/mês — funciona para 200+ vídeos/mês
"""
import os, sys, json, re, time, base64, asyncio, subprocess, requests, urllib.parse
from PIL import Image, ImageDraw
from concurrent.futures import ThreadPoolExecutor, as_completed

# ── CONFIG ────────────────────────────────────────────────────────
VIDEO_ID   = int(sys.argv[1]) if len(sys.argv) > 1 else int(os.environ.get("VIDEO_ID","693"))
SB_URL     = "https://tpjvalzwkqwttvmszvie.supabase.co"
SB_KEY     = os.environ.get("SUPABASE_SERVICE_KEY","")
GROQ_KEY   = os.environ.get("GROQ_API_KEY","")
GEMINI_KEYS = [k for k in [
    os.environ.get("GEMINI_API_KEY",""),
    os.environ.get("GEMINI_API_KEY_2",""),
] if k]

W, H    = 1080, 1920
N_CENAS = 50          # ← LONG: 50 cenas (Shorts usam 20)
CRF     = 22          # ← LONG: qualidade maior (Shorts usam 25)
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
print(f"  ψ V8 LONG STANDARD — Video #{VIDEO_ID} | {N_CENAS} cenas")
print(f"  psicologia.doc @psidanielacoelho | 15min+")
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

print(f"\n📄 {video.get('title','')}")
print(f"   {len(script_tts)} chars | ~{len(script_tts)//14:.0f}s estimado")

if len(script_tts) < 500:
    sys.exit(f"Script curto ({len(script_tts)} chars) — use render_video_v8_standard.py para Shorts")

# ── GROQ: 50 PROMPTS COM CAPÍTULOS ───────────────────────────────
def gerar_prompts_groq():
    """
    Groq gera 50 prompts estruturados em 5 CAPÍTULOS (10 cenas cada):
      Cap 1: Introdução / Gancho (cenas 1-10)
      Cap 2: Desenvolvimento (cenas 11-20)
      Cap 3: Aprofundamento (cenas 21-30)
      Cap 4: Solução / Insights (cenas 31-40)
      Cap 5: Conclusão + CTA (cenas 41-50)
    """
    if not GROQ_KEY:
        return gerar_prompts_fallback()

    system = f"""You are a creative director for a Brazilian psychology YouTube channel (@psidanielacoelho).
Generate exactly {N_CENAS} image scene prompts for a {N_CENAS//10}-chapter long-form psychology video (~15 minutes).

Structure ({N_CENAS} scenes total):
  Chapter 1 (scenes 1-10):  Hook + Introduction — grab attention, present the problem
  Chapter 2 (scenes 11-20): Development — deepen the concept, real examples
  Chapter 3 (scenes 21-30): Deep Dive — science, mechanisms, hidden patterns
  Chapter 4 (scenes 31-40): Solution / Insights — what to do, how to recognize, protect yourself
  Chapter 5 (scenes 41-50): Conclusion + CTA — empowerment, subscribe, share

Rules for EVERY prompt:
- Style: "chibi anime flat design illustration, kawaii psychology animation, vertical 9:16 portrait, clean line art"
- Background: "soft warm cream white background #F5F0E8 with subtle pastel decorations"
- NO text: "no text, no words, no letters, no logos"
- Copyright safe: "original character design not based on any existing IP or trademark"
- Last scene MUST be subscribe CTA: golden bell, confetti, girl celebrating

Return ONLY a JSON array with exactly {N_CENAS} objects:
[{{"chapter":N,"frase_pt":"phrase in portuguese","dur_chars":N,"prompt":"english prompt","caption_pt":"SHORT PT max 25 chars"}}]"""

    user_msg = f"""Script topic: {topic}
Script (PT-BR, {len(script_tts)} chars):
{script_tts[:8000]}{'...[truncado]' if len(script_tts) > 8000 else ''}

Divide into exactly {N_CENAS} scenes across 5 chapters.
Total dur_chars must sum to approximately {len(script_tts)}.
Last scene: subscribe CTA.
Return JSON array of {N_CENAS} objects."""

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
                # Extrair JSON do texto
                match = re.search(r'\[.*\]', text, re.DOTALL)
                if match:
                    scenes = json.loads(match.group())
                    while len(scenes) < N_CENAS: scenes.append(scenes[-1].copy())
                    scenes = scenes[:N_CENAS]
                    scenes[-1]["caption_pt"] = "INSCREVA-SE AGORA 🔔"
                    print(f"   ✅ Groq gerou {len(scenes)} prompts ({N_CENAS//10} capítulos)")
                    return scenes
        except Exception as e:
            print(f"   Groq tentativa {attempt+1}: {e}")
            time.sleep(5)

    print("   ⚠️ Groq falhou → usando prompts fallback")
    return gerar_prompts_fallback()

def gerar_prompts_fallback():
    """50 prompts chibi estruturados em 5 capítulos."""
    chars_por_cena = max(1, len(script_tts) // N_CENAS)
    STYLE = ("chibi anime flat design illustration, kawaii psychology animation, "
             "vertical 9:16, soft cream white background #F5F0E8, "
             "no text, no words, original character not based on any existing IP")
    GIRL  = "chibi anime girl short dark hair professional casual blouse warm smile"
    BOY   = "chibi anime boy dark hair navy shirt confident expression"

    # Templates por capítulo
    chap_templates = {
        1: [  # Hook/Introdução
            f"{GIRL} shocked surprised hands on cheeks large question mark floating, {STYLE}",
            f"three chibi characters silhouettes with hidden sinister glow around one, {STYLE}",
            f"large warning sign exclamation mark {GIRL} alarmed expression, {STYLE}",
            f"{BOY} finger to lips shushing whisper secrets shadows, {STYLE}",
            f"newspaper headline chibi characters reading shocked, {STYLE}",
            f"spotlight on {GIRL} surrounded by darkness dramatic reveal, {STYLE}",
            f"chibi brain with puzzle pieces fitting together discovery, {STYLE}",
            f"magnifying glass revealing hidden truth {GIRL} investigating, {STYLE}",
            f"calendar clock timer urgency {GIRL} attentive listening, {STYLE}",
            f"chapter 1 badge {GIRL} arms crossed confident serious, {STYLE}",
        ],
        2: [  # Desenvolvimento
            f"badge number 1 {GIRL} speech bubble empty erased invisible, {STYLE}",
            f"{BOY} turned away blame arrow {GIRL} sad confused, {STYLE}",
            f"badge number 2 golden trophy {BOY} claiming {GIRL} beside, {STYLE}",
            f"badge number 3 {GIRL} exhausted heavy weights pressing down, {STYLE}",
            f"mirror reflection distorted {GIRL} confused identity, {STYLE}",
            f"checklist items one by one {GIRL} recognizing patterns, {STYLE}",
            f"before after comparison chibi transformation growth, {STYLE}",
            f"scale balance justice truth on one side lie on other, {STYLE}",
            f"{BOY} mask held up friendly outside sinister shadow behind, {STYLE}",
            f"emotional waves ocean {GIRL} overwhelmed but standing, {STYLE}",
        ],
        3: [  # Aprofundamento / Ciência
            f"professional chibi doctor lab coat brain diagram neuroscience, {STYLE}",
            f"chibi brain highlighted red stress zones cortisol arrows, {STYLE}",
            f"research book open chibi scientist studying psychology, {STYLE}",
            f"DNA strand psychology trauma generational patterns chibi, {STYLE}",
            f"chibi characters connected by invisible puppet strings manipulation, {STYLE}",
            f"iceberg metaphor visible small hidden massive darkness, {STYLE}",
            f"timeline childhood adult connection dots psyche, {STYLE}",
            f"neuron synapses glowing connection healing brain chibi, {STYLE}",
            f"statistics chart showing relationship patterns chibi teacher, {STYLE}",
            f"chibi psychologist therapy session couch plant warm light, {STYLE}",
        ],
        4: [  # Solução
            f"green checkmark {GIRL} raising fist empowerment liberation, {STYLE}",
            f"shield protection heart {GIRL} defending herself strong, {STYLE}",
            f"toolkit box healing tools chibi self-care items, {STYLE}",
            f"{GIRL} mirror healthy reflection clear identity restored, {STYLE}",
            f"boundary wall {GIRL} standing behind it confident safe, {STYLE}",
            f"checklist affirmation {GIRL} checking items feeling better, {STYLE}",
            f"support group chibi characters holding hands circle warmth, {STYLE}",
            f"growth plant sprouting from dark soil into sunshine chibi, {STYLE}",
            f"{GIRL} journal writing self-reflection healing path, {STYLE}",
            f"sunrise new day {GIRL} arms open fresh start freedom, {STYLE}",
        ],
        5: [  # Conclusão + CTA
            f"{GIRL} joyful arms wide open floating pink hearts flower petals, {STYLE}",
            f"chibi warm golden light embrace self-love acceptance, {STYLE}",
            f"community friends chibi together support network, {STYLE}",
            f"{GIRL} holding phone showing video to friend sharing, {STYLE}",
            f"star rating five stars {GIRL} thumbs up recommend, {STYLE}",
            f"megaphone announcement {GIRL} excited sharing knowledge, {STYLE}",
            f"comment bubble {GIRL} reading positive responses happy, {STYLE}",
            f"notification bell ringing sparkles subscribe, {STYLE}",
            f"{GIRL} warm smile eye symbol ear symbol golden light, {STYLE}",
            f"giant golden bell musical notes rainbow confetti {GIRL} arms raised joy subscribe, {STYLE}",
        ]
    }

    captions_by_chapter = {
        1: ["Você reconheceria?","O que está oculto?","Atenção!","Segredos...","Descoberta",
            "Revelação","Como funciona?","Investigando","Preste atenção","Capítulo 1"],
        2: ["Sinal 1","Ele te culpa","Sinal 2","Sinal 3","Quem sou eu?",
            "Reconhecendo","Antes e depois","A verdade","A máscara","Emoções"],
        3: ["A ciência explica","Seu cérebro","Pesquisas","Padrões","Manipulação",
            "O iceberg","Sua história","Cura cerebral","Os números","Terapia"],
        4: ["Você pode!","Proteja-se","Suas ferramentas","Sua identidade","Seus limites",
            "Checklist","Apoio","Crescimento","Reflita","Novo começo"],
        5: ["Você merece!","Amor próprio","Comunidade","Compartilha!","Avalie!",
            "Espalhe!","Comentários","Inscreva-se!","Te vê. Te ouve.","INSCREVA-SE AGORA 🔔"],
    }

    scenes = []
    for cap in range(1, 6):
        for i in range(10):
            global_i = (cap-1)*10 + i
            scenes.append({
                "chapter": cap,
                "frase_pt": f"Capítulo {cap} - Cena {i+1}",
                "dur_chars": chars_por_cena,
                "prompt": chap_templates[cap][i],
                "caption_pt": captions_by_chapter[cap][i]
            })

    scenes[-1]["caption_pt"] = "INSCREVA-SE AGORA 🔔"
    return scenes

print(f"\n🧠 Groq: gerando {N_CENAS} prompts ({N_CENAS//10} capítulos)...")
SCENES = gerar_prompts_groq()

# ── GERAR IMAGEM: Pollinations → Gemini → Pillow ─────────────────
def gen_image(prompt, idx):
    """Idêntico ao Short mas com seed específico por capítulo."""
    chapter = SCENES[idx].get("chapter", (idx // 10) + 1)

    full_prompt = (
        "Psych2Go animation style, kawaii chibi anime character, "
        "cream white background #F5F0E8, pastel warm colors, "
        f"round big expressive eyes, clean soft lines. {prompt}. "
        "Original character design not based on any existing IP, "
        "no text, no logos, no watermarks, no brand marks."
    )

    # 1. Pollinations.ai Flux
    try:
        enc = urllib.parse.quote(full_prompt)
        seed = 100 + chapter * 10 + idx
        url = (f"https://image.pollinations.ai/prompt/{enc}"
               f"?width=576&height=1024&seed={seed}&nologo=true&model=flux")
        r = requests.get(url, timeout=90)
        if r.status_code == 402:
            time.sleep(20)
            r = requests.get(url, timeout=90)
        if r.status_code == 200 and r.headers.get('content-type','').startswith('image'):
            tmp = f"{WORKDIR}/raw_{idx:02d}.jpg"
            with open(tmp,"wb") as f: f.write(r.content)
            img = Image.open(tmp).convert("RGB").resize((W,H), Image.LANCZOS)
            out = f"{WORKDIR}/ai_{idx:02d}.jpg"
            img.save(out,"JPEG",quality=92)
            return out
    except Exception:
        pass

    # 2. Gemini fallback
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
                                out = f"{WORKDIR}/ai_{idx:02d}.jpg"
                                img.save(out,"JPEG",quality=92)
                                return out
            except Exception:
                continue

    return None

def pillow_fallback(idx, caption):
    """Chibi kawaii programático — padrão eterno."""
    img = Image.new("RGB",(W,H),(245,240,232))
    draw = ImageDraw.Draw(img)
    for y in range(H):
        t=y/H; r=int(245+(235-245)*t); g=int(240+(228-240)*t); b=int(232+(220-232)*t)
        draw.line([(0,y),(W,y)],fill=(r,g,b))
    cx,cy = W//2,H//2
    draw.ellipse([cx-120,cy-220,cx+120,cy+40],fill=(255,220,180))
    draw.ellipse([cx-125,cy-270,cx+125,cy-100],fill=(60,40,20))
    draw.ellipse([cx-60,cy-100,cx-20,cy-60],fill=(30,20,10))
    draw.ellipse([cx+20,cy-100,cx+60,cy-60],fill=(30,20,10))
    draw.ellipse([cx-55,cy-95,cx-45,cy-85],fill=(255,255,255))
    draw.ellipse([cx+25,cy-95,cx+35,cy-85],fill=(255,255,255))
    draw.arc([cx-40,cy-30,cx+40,cy+20],start=0,end=180,fill=(200,80,80),width=5)
    draw.rounded_rectangle([cx-100,cy+40,cx+100,cy+300],radius=20,fill=(130,80,200))
    draw.ellipse([cx-110,cy-60,cx-60,cy-20],fill=(255,180,180))
    draw.ellipse([cx+60,cy-60,cx+110,cy-20],fill=(255,180,180))
    out = f"{WORKDIR}/fb_{idx:02d}.jpg"
    img.save(out,"JPEG",quality=85)
    return out

# ── OVERLAY PILLOW — PADRÃO ETERNO (idêntico ao Short) ───────────
def add_overlay(img_path, caption_pt, chapter=None):
    """
    PADRÃO ETERNO:
    - Badge branco no TOPO com caption_pt
    - Para Longs: também mostra indicador de capítulo (se disponível)
    - Lower third base: psi | Daniela Coelho | Saude Mental | @psidanielacoelho
    """
    img = Image.open(img_path).convert("RGB")
    draw = ImageDraw.Draw(img)

    # ── LOWER THIRD (base) — idêntico ao Short ───────────────────
    lt_h = 95
    draw.rectangle([0,H-lt_h,W,H],fill=(8,6,18))
    draw.rectangle([0,H-lt_h,5,H],fill=VERM)
    draw.text((22,H-lt_h+12),"psi",fill=GOLD)
    draw.text((62,H-lt_h+10),"Daniela Coelho",fill=BRAN)
    draw.text((62,H-lt_h+40),"Saude Mental  |  @psidanielacoelho",fill=LILAS)
    draw.rectangle([0,H-4,W,H],fill=VERM)

    # ── CAPTION BADGE TOPO — idêntico ao Short ───────────────────
    if caption_pt:
        cap = caption_pt[:28].upper()
        cap_w = min(len(cap)*14+44, W-60)
        cx = W//2; cap_y = 56
        draw.rounded_rectangle([cx-cap_w//2,cap_y-24,cx+cap_w//2,cap_y+24],
                                radius=15, fill=(245,245,255))
        draw.rounded_rectangle([cx-cap_w//2,cap_y-24,cx+cap_w//2,cap_y+24],
                                radius=15, outline=(200,200,220), width=2)
        draw.text((cx-cap_w//2+22,cap_y-10), cap, fill=(20,15,45))

    # ── INDICADOR DE CAPÍTULO (exclusivo Longs) ───────────────────
    if chapter and chapter > 0:
        chap_labels = {
            1: "INTRODUÇÃO", 2: "DESENVOLVIMENTO",
            3: "APROFUNDAMENTO", 4: "SOLUÇÃO", 5: "CONCLUSÃO"
        }
        label = chap_labels.get(chapter, f"CAP {chapter}")
        # Badge pequeno vermelho canto superior direito
        cw = len(label)*9 + 20
        draw.rounded_rectangle([W-cw-10, 110, W-10, 142], radius=8, fill=VERM)
        draw.text((W-cw-4, 116), label, fill=BRAN)

    img.save(img_path,"JPEG",quality=95)
    return img_path

# ── GERAR 50 CENAS (4 workers paralelo) ──────────────────────────
def generate_scene(args):
    i, scene = args
    prompt  = scene.get("prompt","")
    caption = scene.get("caption_pt","")
    chapter = scene.get("chapter", (i//10)+1)
    cap_num = i+1
    print(f"   [{cap_num:02d}/{N_CENAS}] Cap{chapter} — Gerando imagem...")
    path = gen_image(prompt, i)
    if path:
        add_overlay(path, caption, chapter)
        sz = os.path.getsize(path)//1024
        print(f"   [{cap_num:02d}/{N_CENAS}] ✅ AI ({sz}KB)")
        return path, True
    else:
        fb = pillow_fallback(i, caption)
        add_overlay(fb, caption, chapter)
        print(f"   [{cap_num:02d}/{N_CENAS}] ⚠️  Fallback chibi")
        return fb, False

print(f"\n🎨 Gerando {N_CENAS} imagens chibi (4 workers paralelo)...")
t0 = time.time()
imgs = [None]*N_CENAS
n_ai = n_fb = 0

with ThreadPoolExecutor(max_workers=4) as ex:
    futures = {ex.submit(generate_scene,(i,s)):i for i,s in enumerate(SCENES)}
    for fut in as_completed(futures):
        i = futures[fut]
        path, is_ai = fut.result()
        imgs[i] = path
        if is_ai: n_ai += 1
        else: n_fb += 1
        time.sleep(1)  # rate limit suave

gen_t = time.time()-t0
print(f"\n   ✅ {n_ai}/{N_CENAS} AI | {n_fb} fallback | {gen_t:.1f}s")

# ── EDGE TTS: ÁUDIO ───────────────────────────────────────────────
print(f"\n🎙️  Áudio...")

async def _tts():
    import edge_tts
    c = edge_tts.Communicate(script_tts, voice="pt-BR-AntonioNeural")
    await c.save(f"{WORKDIR}/audio.mp3")

if video.get("audio_url"):
    print(f"   Usando áudio existente do DB...")
    ar = requests.get(video["audio_url"], timeout=120)
    ar.raise_for_status()
    with open(f"{WORKDIR}/audio.mp3","wb") as f: f.write(ar.content)
else:
    print(f"   Gerando com Edge TTS AntonioNeural...")
    asyncio.run(_tts())

probe = subprocess.run(
    ["ffprobe","-v","quiet","-print_format","json","-show_format",
     f"{WORKDIR}/audio.mp3"],
    capture_output=True,text=True)
DUR_AUDIO = float(json.loads(probe.stdout)["format"]["duration"])

# RATE_REAL: NUNCA hardcoded
RATE_REAL = len(script_tts) / DUR_AUDIO
print(f"   {DUR_AUDIO:.1f}s ({DUR_AUDIO/60:.1f}min) | RATE_REAL={RATE_REAL:.3f} chars/s")

# ── TIMING DINÂMICO (idêntico ao Short) ──────────────────────────
durs = []
for scene in SCENES:
    chars = scene.get("dur_chars", len(script_tts)//N_CENAS)
    durs.append(max(0.5, round(chars/RATE_REAL, 3)))

soma = sum(durs)
print(f"   Soma cenas: {soma:.1f}s | Gap: {DUR_AUDIO-soma:.1f}s")

# ── FFCONCAT ─────────────────────────────────────────────────────
concat_file = f"{WORKDIR}/concat.txt"
with open(concat_file,"w") as f:
    for img,dur in zip(imgs,durs):
        if img: f.write(f"file '{img}'\nduration {dur:.3f}\n")
    if imgs[-1]: f.write(f"file '{imgs[-1]}'\n")

# ── RENDER FFMPEG ─────────────────────────────────────────────────
print(f"\n🎬 Renderizando LONG (crf={CRF}, ~15-20MB)...")
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
res = subprocess.run(cmd,capture_output=True,text=True,timeout=3600)
if res.returncode != 0:
    print(f"ERRO FFMPEG:\n{res.stderr[-2000:]}")
    sys.exit(1)

sz = os.path.getsize(out_mp4)
probe2 = subprocess.run(
    ["ffprobe","-v","quiet","-print_format","json","-show_format",out_mp4],
    capture_output=True,text=True)
dur2 = float(json.loads(probe2.stdout)["format"]["duration"])
print(f"   ✅ {sz//1024//1024}MB ({sz//1024}KB) | {dur2:.1f}s ({dur2/60:.1f}min)")

# ── UPLOAD SUPABASE ───────────────────────────────────────────────
print(f"\n☁️  Upload Supabase Storage...")

if not video.get("audio_url"):
    with open(f"{WORKDIR}/audio.mp3","rb") as f: adata = f.read()
    audio_url = sb_upload(f"audios/v{VIDEO_ID}_long_v8std_{ts}.mp3",adata,"audio/mpeg")
    sb_patch("content_pipeline",VIDEO_ID,{"audio_url":audio_url})

with open(out_mp4,"rb") as f: vdata = f.read()
video_url = None
for attempt in range(5):
    try:
        video_url = sb_upload(f"mp4s/v{VIDEO_ID}_long_v8std_{ts}.mp4",vdata,"video/mp4")
        print(f"   ✅ Upload OK")
        break
    except Exception as e:
        print(f"   Tentativa {attempt+1}: {e}")
        time.sleep(10)

# ── UPDATE DB ─────────────────────────────────────────────────────
if video_url:
    sb_patch("content_pipeline",VIDEO_ID,{
        "video_url": video_url,
        "status": "pending_credentials",
        "metadata": json.dumps({
            "render_version": "v8_long_standard",
            "n_cenas": N_CENAS,
            "n_chapters": N_CENAS//10,
            "n_ai_scenes": n_ai,
            "n_fallback_scenes": n_fb,
            "audio_dur_s": round(DUR_AUDIO,1),
            "video_dur_s": round(dur2,1),
            "video_dur_min": round(dur2/60,1),
            "file_mb": round(sz/1024/1024,1),
            "crf": CRF,
            "rate_real": round(RATE_REAL,3),
            "gen_time_s": round(gen_t,1),
            "lower_third": "Daniela Coelho | Saude Mental | @psidanielacoelho",
        })
    })

print(f"\n{'='*60}")
print(f"  ✅ LONG V8 STANDARD — #{VIDEO_ID}")
print(f"  🎬 {video_url}")
print(f"  {n_ai}/{N_CENAS} AI | {sz//1024//1024}MB | {dur2/60:.1f}min")
print(f"{'='*60}\n")
