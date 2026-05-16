#!/usr/bin/env python3
"""
render_video_v8.py — RENDER UNIVERSAL PARA QUALQUER VIDEO
Uso: python3 render_video_v8.py <VIDEO_ID>

Funciona para QUALQUER video da tabela content_pipeline:
1. Pega script + topic do Supabase
2. Groq gera 20 scene prompts contextuais em 1 chamada
3. Gemini 2.5 Flash Image gera 20 imagens chibi em 30s (4 workers paralelos)
4. Edge TTS gera audio (AntonioNeural, rate calculado dinamicamente)
5. ffconcat timing preciso por frase
6. FFmpeg render crf=25 (3-4MB por video)
7. Upload Supabase + update DB
$0/mes, funciona para 200+ videos.
"""
import os, sys, json, math, re, time, base64, asyncio, subprocess, requests
from PIL import Image, ImageDraw
from concurrent.futures import ThreadPoolExecutor, as_completed

# ─── CONFIGURACAO ─────────────────────────────────────────────────
VIDEO_ID    = int(sys.argv[1]) if len(sys.argv) > 1 else int(os.environ.get("VIDEO_ID","683"))
SB_URL      = os.environ.get("SUPABASE_URL","")
SB_KEY      = os.environ.get("SUPABASE_KEY","")
GROQ_KEY    = os.environ.get("GROQ_API_KEY","")
NVIDIA_KEY  = os.environ.get("NVIDIA_API_KEY","")
GEMINI_KEYS = [k for k in [
    os.environ.get("GEMINI_API_KEY",""),
    os.environ.get("GEMINI_API_KEY_2",""),
] if k]

W, H = 1080, 1920
WORKDIR = f"/tmp/v8_{VIDEO_ID}"
os.makedirs(WORKDIR, exist_ok=True)
print(f"=== RENDER UNIVERSAL V8 | VIDEO #{VIDEO_ID} | $0/mes ===")

# ─── SUPABASE: LER VIDEO ──────────────────────────────────────────
def get_video():
    r = requests.get(f"{SB_URL}/rest/v1/content_pipeline",
        params={"select":"id,title,script,topic,platform","id":f"eq.{VIDEO_ID}"},
        headers={"apikey":SB_KEY,"Authorization":f"Bearer {SB_KEY}"})
    data = r.json()
    if not data: sys.exit(f"Video {VIDEO_ID} nao encontrado no DB")
    return data[0]

video = get_video()
SCRIPT_TTS = video.get("script","").strip()
TOPIC      = video.get("topic", video.get("title","psychology"))
PLATFORM   = video.get("platform","youtube_shorts")
print(f"Topic: {TOPIC} | Script: {len(SCRIPT_TTS)} chars | Platform: {PLATFORM}")

if len(SCRIPT_TTS) < 50:
    sys.exit(f"Script muito curto ({len(SCRIPT_TTS)} chars) para video #{VIDEO_ID}")

# ─── GROQ: GERAR 20 SCENE PROMPTS CONTEXTUAIS ─────────────────────
def gerar_prompts_groq():
    """Uma chamada Groq gera 20 prompts Gemini contextuais ao roteiro."""
    if not GROQ_KEY:
        return gerar_prompts_fallback()
    
    system = """You are a creative director for a psychology YouTube channel.
Generate exactly 20 image scene prompts for an AI-generated chibi kawaii animation video.
Each prompt must be in English and describe ONE scene image.

Rules for EVERY prompt:
- Style: "chibi anime flat design illustration, kawaii psychology animation, vertical 9:16 portrait, clean line art"
- Background: "soft warm cream white background with subtle pastel decorations"
- NO text in image: "no text, no words, no letters"
- Copyright safe: "original character design not based on any existing IP or trademark"
- Characters: Use "chibi anime girl with short brown hair and pink blouse" for female protagonist, "chibi anime boy with dark slicked hair and navy shirt" for male antagonist
- Make each scene visually reflect the specific phrase/concept

Return ONLY a JSON array with exactly 20 objects:
[{"frase_pt":"phrase in portuguese","dur_chars":N,"prompt":"english gemini prompt","caption_pt":"SHORT PT caption max 25 chars"}]"""

    # Dividir script em ~20 frases
    frases = re.split(r'(?<=[.!?])\s+|(?<=\n)\n', SCRIPT_TTS.strip())
    frases = [f.strip() for f in frases if len(f.strip()) > 5]
    
    user_msg = f"""Script topic: {TOPIC}
Script (PT-BR, {len(SCRIPT_TTS)} chars):
{SCRIPT_TTS}

Divide into exactly 20 scenes. The last scene MUST end with "Inscreva-se agora" (subscribe CTA).
Return JSON array of 20 objects."""

    headers = {"Authorization":f"Bearer {GROQ_KEY}","Content-Type":"application/json"}
    payload = {
        "model":"llama-3.3-70b-versatile",
        "messages":[{"role":"system","content":system},{"role":"user","content":user_msg}],
        "temperature":0.7,"max_tokens":4000,"response_format":{"type":"json_object"}
    }
    
    for attempt in range(3):
        try:
            r = requests.post("https://api.groq.com/openai/v1/chat/completions",
                headers=headers, json=payload, timeout=45)
            if r.status_code == 200:
                content = r.json()["choices"][0]["message"]["content"]
                data = json.loads(content)
                # Pegar o array (pode estar em chave ou diretamente)
                if isinstance(data, list): scenes = data
                elif isinstance(data, dict):
                    scenes = next((v for v in data.values() if isinstance(v,list)),None)
                    if not scenes: raise ValueError("Nao encontrou array no JSON")
                
                # Garantir exatamente 20 cenas
                while len(scenes) < 20:
                    scenes.append(scenes[-1].copy())
                scenes = scenes[:20]
                
                print(f"Groq gerou {len(scenes)} prompts ✅")
                return scenes
        except Exception as e:
            print(f"  Groq tentativa {attempt+1}: {e}")
            time.sleep(3)
    
    print("Groq falhou, usando fallback")
    return gerar_prompts_fallback()

def gerar_prompts_fallback():
    """Fallback: divide script em 20 partes iguais com prompts genericos."""
    parts = re.split(r'[.!?]+', SCRIPT_TTS)
    parts = [p.strip() for p in parts if len(p.strip()) > 5]
    
    STYLE = "chibi anime flat design illustration, kawaii psychology animation, vertical 9:16, cream white background, no text, original character not based on any IP"
    CHAR_F = "chibi anime girl short brown hair pink blouse beige skin large brown eyes rosy cheeks"
    CHAR_M = "chibi anime boy dark slicked hair light skin navy blue shirt charming smile"
    
    prompts_base = [
        f"{CHAR_F} shocked surprised expression hands on cheeks large question mark floating, {STYLE}",
        f"three {STYLE} chibi characters in a row one highlighted with subtle sinister circle, {STYLE}",
        f"large megaphone with big red X crossing it out silence symbol, {STYLE}",
        f"{CHAR_M} finger to lips shushing gesture whisper speech bubbles, {STYLE}",
        f"{CHAR_F} and {CHAR_M} side by side golden wedding ring between them subtle cracked heart, {STYLE}",
        f"{CHAR_M} smug smile golden star sparkles orbiting flawless perfect, {STYLE}",
        f"{CHAR_F} dizzy confused expression spiral swirling stress lines around head, {STYLE}",
        f"large STOP hand gesture multiple chibi silhouettes behind warning feel, {STYLE}",
        f"red badge number 1 {CHAR_F} talking animated speech bubble completely empty erased, {STYLE}",
        f"{CHAR_M} turned away arms crossed pointing blame arrow toward sad {CHAR_F}, {STYLE}",
        f"orange badge number 2 golden trophy {CHAR_M} claiming it smugly sad {CHAR_F} beside, {STYLE}",
        f"purple badge number 3 {CHAR_F} exhausted drooping heavy weights pressing down, {STYLE}",
        f"professional chibi woman white lab coat brain diagram energy draining arrows, {STYLE}",
        f"large bold green checkmark circle glowing {CHAR_F} raising fist empowerment, {STYLE}",
        f"large red heart thick black X crossed out broken heart pieces scattered, {STYLE}",
        f"{CHAR_M} holding smiling theater mask sinister shadow behind friendly mask, {STYLE}",
        f"chibi hands holding glowing smartphone share arrow send motion lines, {STYLE}",
        f"{CHAR_F} joyful arms wide open floating pink red hearts flower petals celebration, {STYLE}",
        f"chibi anime girl warm loving eye symbol ear symbol golden light warmth, {STYLE}",
        f"giant golden bell musical notes rainbow confetti {CHAR_F} arms raised joy subscribe, {STYLE}",
    ]
    
    scene_count = len(parts)
    chars_per_scene = len(SCRIPT_TTS) // 20
    
    scenes = []
    for i in range(20):
        frase = parts[min(i, len(parts)-1)] if parts else f"cena {i+1}"
        scenes.append({
            "frase_pt": frase[:60],
            "dur_chars": chars_per_scene,
            "prompt": prompts_base[i],
            "caption_pt": f"CENA {i+1}"
        })
    
    # Ultima cena sempre CTA
    scenes[-1]["caption_pt"] = "INSCREVA-SE AGORA"
    return scenes

print("Gerando 20 scene prompts via Groq...")
SCENES = gerar_prompts_groq()

# ─── GEMINI: GERAR IMAGENS AI ─────────────────────────────────────
GEMINI_MODELS = ["gemini-2.5-flash-image","gemini-3.1-flash-image-preview"]
_gemini_key_idx = [0]

def gemini_key():
    if not GEMINI_KEYS: return None
    return GEMINI_KEYS[_gemini_key_idx[0] % len(GEMINI_KEYS)]

def rotate_gemini_key():
    _gemini_key_idx[0] += 1

def gen_gemini_image(prompt, idx):
    key = gemini_key()
    if not key: return None
    for mdl in GEMINI_MODELS:
        url = f"https://generativelanguage.googleapis.com/v1beta/models/{mdl}:generateContent?key={key}"
        payload = {"contents":[{"parts":[{"text":prompt}]}],"generationConfig":{"responseModalities":["IMAGE","TEXT"]}}
        try:
            r = requests.post(url, json=payload, timeout=60)
            if r.status_code == 429:
                rotate_gemini_key()
                time.sleep(5)
                continue
            if r.status_code == 200:
                for cand in r.json().get("candidates",[]):
                    for part in cand.get("content",{}).get("parts",[]):
                        if "inlineData" in part:
                            raw = base64.b64decode(part["inlineData"]["data"])
                            tmp = f"{WORKDIR}/raw_{idx:02d}.jpg"
                            with open(tmp,"wb") as f: f.write(raw)
                            img = Image.open(tmp).convert("RGB")
                            aw,ah = img.size
                            if aw/ah > 9/16:
                                nw=int(ah*9/16); img=img.crop(((aw-nw)//2,0,(aw+nw)//2,ah))
                            elif aw/ah < 9/16:
                                nh=int(aw*16/9); img=img.crop((0,(ah-nh)//2,aw,(ah+nh)//2))
                            img = img.resize((W,H),Image.LANCZOS)
                            out = f"{WORKDIR}/ai_{idx:02d}.jpg"
                            img.save(out,"JPEG",quality=92)
                            return out
        except Exception as e:
            pass
    return None

VERM=(220,50,50);AM=(255,210,50);BR=(255,255,255)

def pillow_fallback(idx, caption):
    """Fallback Pillow se Gemini falhar."""
    PALS = [(15,12,30),(200,20,20),(8,18,75),(220,100,20),(55,8,8),(200,160,10),
            (160,30,30),(35,35,75),(0,130,120),(65,15,95),(15,150,70),(220,170,0)]
    ct = PALS[idx % len(PALS)]; cb = tuple(max(0,c-40) for c in ct)
    img = Image.new("RGB",(W,H)); draw = ImageDraw.Draw(img)
    for y in range(H):
        t=y/H; c=tuple(int(ct[i]*(1-t)+cb[i]*t) for i in range(3))
        draw.line([(0,y),(W,y)],fill=c)
    draw.text((W//2-80,H//2-20),caption[:20],fill=BR)
    out = f"{WORKDIR}/fb_{idx:02d}.jpg"; img.save(out,"JPEG",quality=85)
    return out

def add_overlay(img_path, caption):
    """Lower third + badge caption no topo."""
    img = Image.open(img_path).convert("RGB"); draw = ImageDraw.Draw(img)
    lt_h = 95
    draw.rectangle([0,H-lt_h,W,H],fill=(8,6,18))
    draw.rectangle([0,H-lt_h,5,H],fill=VERM)
    draw.text((22,H-lt_h+12),"psi",fill=AM)
    draw.text((62,H-lt_h+10),"Daniela Coelho",fill=BR)
    draw.text((62,H-lt_h+40),"Saude Mental  |  @psidanielacoelho",fill=(185,170,225))
    draw.rectangle([0,H-4,W,H],fill=VERM)
    if caption:
        cap = caption[:28]
        cap_w = min(len(cap)*14+44, W-60); cx = W//2; cap_y = 56
        draw.rounded_rectangle([cx-cap_w//2,cap_y-24,cx+cap_w//2,cap_y+24],radius=15,fill=(245,245,255))
        draw.rounded_rectangle([cx-cap_w//2,cap_y-24,cx+cap_w//2,cap_y+24],radius=15,outline=(200,200,220),width=2)
        draw.text((cx-cap_w//2+22,cap_y-10),cap,fill=(20,15,45))
    img.save(img_path,"JPEG",quality=95)
    return img_path

def generate_scene(args):
    i, scene = args
    prompt = scene.get("prompt","")
    caption = scene.get("caption_pt","")
    print(f"  Cena {i+1:02d} AI...")
    path = gen_gemini_image(prompt, i)
    if path:
        add_overlay(path, caption)
        print(f"  ✅ [{i+1:02d}] {os.path.getsize(path)//1024}KB")
        return path
    else:
        fb = pillow_fallback(i, caption)
        add_overlay(fb, caption)
        print(f"  ⚠️ [{i+1:02d}] FALLBACK")
        return fb

t0 = time.time()
imgs = [None]*20
with ThreadPoolExecutor(max_workers=4) as ex:
    futures = {ex.submit(generate_scene,(i,s)):i for i,s in enumerate(SCENES)}
    for fut in as_completed(futures): imgs[futures[fut]] = fut.result()
gen_t = time.time()-t0
n_ai = sum(1 for p in imgs if p and "ai_" in p)
print(f"\n{n_ai}/20 AI em {gen_t:.1f}s")

# ─── EDGE TTS: AUDIO ─────────────────────────────────────────────
def gerar_audio():
    import edge_tts
    async def _gen():
        c = edge_tts.Communicate(SCRIPT_TTS, voice="pt-BR-AntonioNeural")
        await c.save(f"{WORKDIR}/audio.mp3")
    asyncio.run(_gen())
    probe = subprocess.run(["ffprobe","-v","quiet","-print_format","json","-show_format",
        f"{WORKDIR}/audio.mp3"],capture_output=True,text=True)
    dur = float(json.loads(probe.stdout)["format"]["duration"])
    return dur

print("Gerando audio Edge TTS...")
DUR_AUDIO = gerar_audio()
RATE_REAL  = len(SCRIPT_TTS) / DUR_AUDIO
print(f"Audio: {DUR_AUDIO:.1f}s | Rate: {RATE_REAL:.3f} chars/s")

# ─── TIMING DINAMICO ─────────────────────────────────────────────
# Calcular duração de cada cena pelo numero de chars
total_chars_cenas = sum(s.get("dur_chars", len(SCRIPT_TTS)//20) for s in SCENES)
soma = 0
durs = []
for s in SCENES:
    chars = s.get("dur_chars", len(SCRIPT_TTS)//20)
    dur = round(chars / RATE_REAL, 3)
    durs.append(max(0.5, dur))  # minimo 0.5s por cena
    soma += dur
print(f"Soma cenas: {soma:.1f}s | Gap: {DUR_AUDIO-soma:.1f}s")

# ─── FFCONCAT ────────────────────────────────────────────────────
concat_file = f"{WORKDIR}/concat.txt"
with open(concat_file,"w") as f:
    for img, dur in zip(imgs, durs):
        if img: f.write(f"file '{img}'\nduration {dur:.3f}\n")
    if imgs[-1]: f.write(f"file '{imgs[-1]}'\n")

# ─── RENDER ─────────────────────────────────────────────────────
print("Renderizando...")
out_mp4 = f"{WORKDIR}/video.mp4"
cmd = ["ffmpeg","-y",
    "-f","concat","-safe","0","-i",concat_file,
    "-i",f"{WORKDIR}/audio.mp3",
    "-c:v","libx264","-pix_fmt","yuv420p",
    "-c:a","aac","-b:a","128k",
    "-shortest","-r","25","-crf","25",  # crf=25 = ~3MB por video
    "-vf","scale=1080:1920:force_original_aspect_ratio=decrease,pad=1080:1920:(ow-iw)/2:(oh-ih)/2,setsar=1",
    "-movflags","+faststart",
    out_mp4]
res = subprocess.run(cmd, capture_output=True, text=True, timeout=480)
if res.returncode != 0:
    print("ERRO FFMPEG:"); print(res.stderr[-2000:]); sys.exit(1)

sz = os.path.getsize(out_mp4)
probe2 = subprocess.run(["ffprobe","-v","quiet","-print_format","json","-show_format",
    out_mp4],capture_output=True,text=True)
dur2 = float(json.loads(probe2.stdout)["format"]["duration"])
print(f"MP4: {sz//1024}KB | {dur2:.1f}s")

# ─── UPLOAD AUDIO NOVO ───────────────────────────────────────────
ts = int(time.time())
fname_audio = f"audios/v{VIDEO_ID}_v8_{ts}.mp3"
with open(f"{WORKDIR}/audio.mp3","rb") as f: adata = f.read()
r_au = requests.post(f"{SB_URL}/storage/v1/object/videos/{fname_audio}",
    headers={"apikey":SB_KEY,"Authorization":f"Bearer {SB_KEY}",
             "Content-Type":"audio/mpeg","x-upsert":"true"},
    data=adata, timeout=120)
audio_url = f"{SB_URL}/storage/v1/object/public/videos/{fname_audio}" if r_au.status_code in[200,201] else None

# ─── UPLOAD VIDEO ────────────────────────────────────────────────
fname_mp4 = f"mp4s/v{VIDEO_ID}_v8_{ts}.mp4"
with open(out_mp4,"rb") as f: vdata = f.read()
mp4_url = None
for attempt in range(5):
    r3 = requests.post(f"{SB_URL}/storage/v1/object/videos/{fname_mp4}",
        headers={"apikey":SB_KEY,"Authorization":f"Bearer {SB_KEY}",
                 "Content-Type":"video/mp4","x-upsert":"true"},
        data=vdata, timeout=420)
    if r3.status_code in [200,201]:
        mp4_url = f"{SB_URL}/storage/v1/object/public/videos/{fname_mp4}"
        print(f"Video upload OK"); break
    time.sleep(6)

# ─── UPDATE DB ───────────────────────────────────────────────────
if mp4_url:
    patch = {
        "mp4_url": mp4_url,
        "status": "pending_credentials",
        "metadata": {
            "render_version": "v8_universal",
            "n_ai_scenes": n_ai,
            "audio_dur_s": round(DUR_AUDIO, 1),
            "video_dur_s": round(dur2, 1),
            "file_kb": sz//1024,
            "gen_time_s": round(gen_t, 1),
            "groq_prompts": True
        }
    }
    if audio_url: patch["audio_url"] = audio_url
    r4 = requests.patch(f"{SB_URL}/rest/v1/content_pipeline?id=eq.{VIDEO_ID}",
        headers={"apikey":SB_KEY,"Authorization":f"Bearer {SB_KEY}",
                 "Content-Type":"application/json","Prefer":"return=minimal"},
        data=json.dumps(patch), timeout=30)
    print(f"DB: HTTP {r4.status_code} — {mp4_url[-55:]}")

print(f"=== CONCLUIDO #{VIDEO_ID} | {sz//1024}KB | {dur2:.1f}s | {n_ai}/20 AI ===")
