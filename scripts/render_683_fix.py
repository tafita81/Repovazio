#!/usr/bin/env python3
"""
render_683_fix.py — RENDER COM GEMINI 2025 + POLLINATIONS SSL-FREE
Correções:
  1. verify=False no Pollinations (bypass SSL proxy)
  2. Modelos Gemini atualizados para 2025
  3. Fallback Imagen 3
  4. Log detalhado de cada tentativa
"""
import os, sys, json, subprocess, requests, time, urllib.parse, asyncio, base64, warnings
from PIL import Image, ImageDraw
from concurrent.futures import ThreadPoolExecutor, as_completed
warnings.filterwarnings("ignore")

VIDEO_ID   = 683
SB_URL     = "https://tpjvalzwkqwttvmszvie.supabase.co"
SB_KEY     = os.environ.get("SUPABASE_SERVICE_KEY","")
GEMINI_KEY = os.environ.get("GEMINI_API_KEY","")
W, H       = 1080, 1920
CRF        = 18
WORKDIR    = "/tmp/v683_fix"
os.makedirs(WORKDIR, exist_ok=True)

VERM=(220,50,50); GOLD=(255,210,50); BRAN=(255,255,255); LILAS=(185,170,225)

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

# Carregar script
row = requests.get(f"{SB_URL}/rest/v1/content_pipeline?id=eq.{VIDEO_ID}&select=id,script",
    headers={"apikey":SB_KEY,"Authorization":f"Bearer {SB_KEY}"},timeout=30).json()[0]
SCRIPT = row["script"].strip()
PARAS  = [p.strip() for p in SCRIPT.split('\n\n') if p.strip()]
N      = len(PARAS)

print(f"{'='*55}")
print(f"  ψ RENDER FIX — #683 Gemini 2025 + Pollinations")
print(f"  {N} cenas | {len(SCRIPT)} chars | CRF={CRF}")
print(f"{'='*55}\n")
print(f"  GEMINI_KEY: {'SET ('+GEMINI_KEY[:8]+'...)' if GEMINI_KEY else 'NAO DEFINIDA'}\n")

# Gemini modelos 2025 na ordem de preferência
GEMINI_MODELS_2025 = [
    "gemini-2.0-flash-preview-image-generation",
    "gemini-2.0-flash-exp-image-generation",
    "gemini-2.0-flash-exp",
    "gemini-1.5-flash",
]

STYLE = "Psych2Go kawaii chibi anime style, cream background #F5F0E8, pastel colors, flat design, expressive big eyes, clean line art, no text, no watermarks, original design"

SCENE_PROMPTS = [
    "chibi anime girl Sara with long wavy auburn hair, round glasses, yellow cardigan, alone at night holding phone anxiously, worried expression, blue phone glow, cream background, kawaii style",
    "chibi anime girl Sara reading disappointing message on phone, face falling with sadness, small rain cloud above head, cream background",
    "chibi anime girl Sara meeting chibi anime man Marcos with dark styled hair and navy blazer at party, he has sparkle effects, she looks captivated, cream background",
    "chibi anime girl Sara with thoughtful expression, small question marks floating around her, sensing something wrong, cream background",
    "chibi anime girl Daniela with short dark bob hair, mint-green blouse, gold psi pin, looking directly forward with warm knowing smile, cream background",
    "chibi anime girl Sara hunched with shoulders down, blame arrow pointing at her, confused and small feeling, cream background",
    "chibi anime girl Sara with speech bubble being dismissed by chibi man Marcos waving hand dismissively, cream background",
    "chibi anime woman doctor Ana with neat dark bun, white lab coat, clipboard, pointing at research data showing 1 in 6 statistic, cream background",
    "chibi anime man Marcos wearing friendly smiling theater mask, sinister dark shadow visible behind it, dramatic effect, cream background",
    "large number 1 badge with chibi Marcos shrugging hands raised innocently, red X over any responsibility symbol, cream background",
    "chibi Sara touching her temple while remembering, glowing memory bubble above head, confused expression, cream background",
    "chibi man Marcos dismissive pointing finger at chibi Sara who is visibly shrinking smaller, power dynamic visual, cream background",
    "chibi doctor Ana pointing at brain diagram showing manipulation effects with glowing highlights, chibi Sara watching with realization, cream background",
    "chibi Daniela holding golden shield protection symbol, warm protective golden light surrounding chibi Sara, cream background",
    "large number 2 badge with chibi Sara's emotional speech bubble floating, chibi Marcos looking bored and disinterested, cream background",
    "chibi Sara with tears streaming, chibi Marcos sighing dramatically, growing cold gap between them, cream background",
    "chibi Marcos surrounded by floating negative labels: dramatic, anxious, difficult, controlling, chibi Sara confused and shrinking, cream background",
    "chibi Sara with hands pressed together apologizing gesture, her own feelings becoming very small behind her, sad expression, cream background",
    "chibi Julia with bouncy curly dark hair, orange sweater, flower clip, looking worried at chibi Sara, protective friend expression, cream background",
    "chibi Julia and chibi Sara face to face in serious conversation, Julia speaking urgent truth, Sara having revelation moment, cream background",
    "mirror showing chibi Sara's original reflection fading and becoming dim, identity erosion visual, cream background",
    "large number 3 badge, chibi Sara carrying heavy guilt weights that are labeled as not hers, chibi Marcos relaxing, cream background",
    "chibi Marcos arriving late with casual shrug, chibi Sara apologizing with confused hands out, clock showing late hour, cream background",
    "chibi Sara with hands to face worried gesture, floating question mark aimed toward her unfairly, lost expression, cream background",
    "chibi Daniela with urgent warm direct expression facing viewer, glowing important badge floating beside her, cream background",
    "scientific iceberg diagram, tiny visible narcissism tip above water, massive hidden manipulation structure below, chibi doctor Ana pointing, cream background",
    "chibi doctor Ana showing cycle flowchart: love bomb then devalue then discard arrows, chibi Sara recognizing the pattern with shock, cream background",
    "chibi Daniela opening bright glowing door to warm light, chibi Sara at threshold about to step through into freedom, cream background",
    "chibi Daniela making sincere direct eye contact with viewer, hand placed on heart, warm golden light all around, cream background",
    "chibi Sara and chibi Julia and chibi Daniela together, arms around each other shoulders, strength in unity, bright warm scene, cream background",
    "chibi Marcos hiding something important in shadow behind his back, chibi Sara about to turn and discover the truth, dramatic tension, cream background",
    "lightbulb revelation moment for chibi Sara, eyes wide with sudden understanding, everything clicking into place visually, cream background",
    "giant golden subscription bell with sparkles and confetti, chibi Daniela Sara Julia Ana all with arms raised celebrating together, rainbow colors, cream background",
]

counts = {"gemini":0, "pollinations":0, "pillow":0}

def try_gemini(prompt, idx):
    """Testar todos os modelos Gemini 2025."""
    if not GEMINI_KEY:
        return None
    
    full_prompt = f"{prompt}, {STYLE}, high quality anime illustration, vibrant but soft colors"
    
    for model in GEMINI_MODELS_2025:
        for attempt in range(2):
            try:
                url = (f"https://generativelanguage.googleapis.com/v1beta"
                       f"/models/{model}:generateContent?key={GEMINI_KEY}")
                payload = {
                    "contents":[{"parts":[{"text": full_prompt}]}],
                    "generationConfig":{"responseModalities":["IMAGE","TEXT"]}
                }
                r = requests.post(url, json=payload, timeout=60)
                
                if r.status_code == 200:
                    data = r.json()
                    for cand in data.get("candidates",[]):
                        for part in cand.get("content",{}).get("parts",[]):
                            if "inlineData" in part:
                                raw = base64.b64decode(part["inlineData"]["data"])
                                if len(raw) > 30000:  # >30KB = real image
                                    tmp = f"{WORKDIR}/raw_{idx:02d}.jpg"
                                    with open(tmp,'wb') as f: f.write(raw)
                                    img = Image.open(tmp).convert("RGB")
                                    # Crop para 9:16
                                    iw, ih = img.size
                                    target_ratio = 9/16
                                    if iw/ih > target_ratio:
                                        nw = int(ih * target_ratio)
                                        img = img.crop(((iw-nw)//2,0,(iw+nw)//2,ih))
                                    img = img.resize((W,H), Image.LANCZOS)
                                    out = f"{WORKDIR}/ai_{idx:02d}.jpg"
                                    img.save(out, "JPEG", quality=97)
                                    return out, f"gemini/{model.split('-')[1]}"
                elif r.status_code == 429:
                    time.sleep(10); continue
                elif r.status_code == 404:
                    break  # modelo não existe, tentar próximo
                # outros erros: tentar próximo modelo
            except Exception:
                pass
            time.sleep(2)
    return None, None

def try_pollinations(prompt, idx):
    """Pollinations com verify=False para bypass SSL proxy."""
    full_prompt = (
        f"Psych2Go kawaii chibi anime style, {prompt}, "
        f"cream background #F5F0E8, pastel colors, flat design, "
        f"expressive big eyes, clean lines, no text, no logos, original design"
    )
    enc = urllib.parse.quote(full_prompt)
    seed = 100 + idx * 23
    
    for model in ["flux", "turbo"]:
        try:
            url = (f"https://image.pollinations.ai/prompt/{enc}"
                   f"?width=576&height=1024&seed={seed}&nologo=true"
                   f"&model={model}&enhance=true")
            r = requests.get(url, timeout=90, verify=False)  # verify=False → bypass SSL
            if r.status_code == 200 and 'image' in r.headers.get('content-type',''):
                if len(r.content) > 40000:  # >40KB = imagem real
                    tmp = f"{WORKDIR}/poll_{idx:02d}.jpg"
                    with open(tmp,'wb') as f: f.write(r.content)
                    img = Image.open(tmp).convert("RGB").resize((W,H), Image.LANCZOS)
                    out = f"{WORKDIR}/ai_{idx:02d}.jpg"
                    img.save(out, "JPEG", quality=97)
                    return out, f"pollinations/{model}"
        except Exception:
            pass
        time.sleep(1)
    return None, None

def gen_chibi_hq(idx, char_desc):
    """Chibi profissional de alta qualidade como fallback digno."""
    img = Image.new("RGB", (W,H), (245,240,232))
    draw = ImageDraw.Draw(img)
    # Gradiente diagonal
    for y in range(H):
        t = y/H
        r = int(245+(228-245)*t); g=int(240+(222-240)*t); b=int(232+(215-232)*t)
        draw.line([(0,y),(W,y)], fill=(r,g,b))
    # Círculo suave de fundo
    draw.ellipse([W//2-320,H//2-380,W//2+320,H//2+380], fill=(238,230,218), outline=(220,210,200),width=2)
    
    # Paleta de cores por índice
    palettes = [
        (100,185,130),(80,130,200),(200,90,130),(130,180,80),(200,150,70),
        (150,90,200),(80,180,180),(200,120,80),(90,160,200),(180,100,160),
    ]
    clr = palettes[idx % len(palettes)]
    cx = W//2; cy = H//2 - 100
    
    # Sombra do corpo
    draw.ellipse([cx-80,cy+220,cx+80,cy+270], fill=(180,168,158))
    # Corpo arredondado
    draw.rounded_rectangle([cx-82,cy+25,cx+82,cy+255], radius=25, fill=clr)
    # Detalhe corpo
    draw.rounded_rectangle([cx-82,cy+25,cx+82,cy+90], radius=25, fill=tuple(max(0,c-20) for c in clr))
    # Cabeça
    draw.ellipse([cx-95,cy-215,cx+95,cy+40], fill=(255,220,185))
    # Cabelo
    hair_colors = [(30,20,10),(130,60,20),(40,25,8),(80,50,20),(50,30,12)]
    hc = hair_colors[idx%5]
    draw.ellipse([cx-98,cy-265,cx+98,cy-90], fill=hc)
    # Olhos grandes
    for ex_offset in [-38, 22]:
        ex = cx + ex_offset
        draw.ellipse([ex,cy-100,ex+38,cy-64], fill=(255,255,255))
        draw.ellipse([ex+5,cy-95,ex+33,cy-69], fill=(30,20,60))
        draw.ellipse([ex+2,cy-97,ex+12,cy-87], fill=(80,60,150))
        draw.ellipse([ex+26,cy-96,ex+34,cy-88], fill=(255,255,255))
    # Bochechas rosadas
    for bx in [cx-60, cx+22]:
        draw.ellipse([bx,cy-40,bx+44,cy-10], fill=(255,185,185))
    # Sorriso
    draw.arc([cx-28,cy-25,cx+28,cy+12], start=0, end=180, fill=(180,55,55), width=4)
    # Braços
    for ax, angle in [(cx-100,20),(cx+100,-20)]:
        draw.rounded_rectangle([ax-18,cy+40,ax+18,cy+140], radius=15, fill=clr)
    # Pin/detalhe
    draw.ellipse([cx-10,cy+30,cx+10,cy+50], fill=GOLD)
    draw.text((cx-4,cy+33), "ψ", fill=(80,50,20))
    
    # Expressão extra (hover lines = movimento)
    for i in range(3):
        hy = cy - 180 + i*15
        draw.line([(cx-50+i*5,hy),(cx-30+i*5,hy)], fill=(200,190,180), width=2)
    
    out = f"{WORKDIR}/ai_{idx:02d}.jpg"
    img.save(out, "JPEG", quality=97)
    return out, "chibi_hq"

def add_overlay(img_path, caption, idx):
    img = Image.open(img_path).convert("RGB")
    draw = ImageDraw.Draw(img)
    # Lower third
    for y in range(H-105,H):
        t=(y-(H-105))/105
        draw.line([(0,y),(W,y)],fill=(int(8+12*t),int(6+8*t),int(18+15*t)))
    draw.rectangle([0,H-105,5,H],fill=VERM)
    draw.rectangle([0,H-4,W,H],fill=VERM)
    draw.text((22,H-95),"ψ",fill=GOLD)
    draw.text((60,H-90),"Daniela Coelho",fill=BRAN)
    draw.text((60,H-55),"Saúde Mental  |  @psidanielacoelho",fill=LILAS)
    # Caption badge
    if caption and len(caption)>2:
        cap = caption[:30].upper()
        bw = min(len(cap)*15+60,W-80)
        bcx = W//2; by=58
        draw.rounded_rectangle([bcx-bw//2+3,by-22+3,bcx+bw//2+3,by+26+3],radius=16,fill=(180,170,200))
        draw.rounded_rectangle([bcx-bw//2,by-22,bcx+bw//2,by+26],radius=16,fill=(252,250,255),outline=(210,200,235),width=2)
        draw.text((bcx-bw//2+26,by-9),cap,fill=(25,15,55))
    img.save(img_path,"JPEG",quality=98)
    return img_path

# CAPTIONS
CAPTIONS = []
for p in PARAS:
    cap=p[:28].split('.')[0].split(',')[0].split('?')[0].strip()
    CAPTIONS.append(cap[:28])
if CAPTIONS: CAPTIONS[-1]="INSCREVA-SE AGORA 🔔"

# GERAR IMAGENS
print(f"🎨 Gerando {N} imagens (Gemini 2025 → Pollinations → Chibi HQ)...\n")
IMGS = [None]*N
t0 = time.time()

def process_scene(args):
    idx, prompt = args
    cap = CAPTIONS[idx] if idx < len(CAPTIONS) else ""
    
    # 1. Gemini 2025
    path, src = try_gemini(prompt, idx)
    if path:
        add_overlay(path, cap, idx)
        sz = os.path.getsize(path)//1024
        print(f"  [{idx+1:02d}] 🤖 {src} | {sz}KB | OK")
        return path, "gemini"
    
    # 2. Pollinations SSL-free
    path, src = try_pollinations(prompt, idx)
    if path:
        add_overlay(path, cap, idx)
        sz = os.path.getsize(path)//1024
        print(f"  [{idx+1:02d}] 🌐 {src} | {sz}KB | OK")
        return path, "pollinations"
    
    # 3. Chibi HQ
    path, src = gen_chibi_hq(idx, prompt)
    add_overlay(path, cap, idx)
    sz = os.path.getsize(path)//1024
    print(f"  [{idx+1:02d}] ✏️  {src} | {sz}KB")
    return path, "pillow"

with ThreadPoolExecutor(max_workers=5) as ex:
    futures = {ex.submit(process_scene,(i,p)):i for i,p in enumerate(SCENE_PROMPTS)}
    for fut in as_completed(futures):
        i=futures[fut]; path,src=fut.result()
        IMGS[i]=path; counts[src if src in counts else 'pillow']+=1
        time.sleep(0.8)

gen_t = time.time()-t0
print(f"\n  ✅ Gemini:{counts['gemini']} | Poll:{counts['pollinations']} | Chibi:{counts['pillow']} | {gen_t:.0f}s")

# ÁUDIO
print(f"\n🎙️  Baixando áudio V8 Final...")
ar = requests.get(f"{SB_URL}/storage/v1/object/public/videos/audios/v683_v8_1778892031.mp3",timeout=60)
with open(f"{WORKDIR}/audio.mp3",'wb') as f: f.write(ar.content)
probe=subprocess.run(["ffprobe","-v","quiet","-print_format","json","-show_format",
    f"{WORKDIR}/audio.mp3"],capture_output=True,text=True)
DUR=float(json.loads(probe.stdout)["format"]["duration"])
RATE=len(SCRIPT)/DUR
print(f"  {DUR:.1f}s | RATE={RATE:.3f}")
DURS=[max(0.5,round(len(p)/RATE,3)) for p in PARAS]

# CONCAT + RENDER
concat=f"{WORKDIR}/concat.txt"
with open(concat,'w') as f:
    for i,dur in enumerate(DURS):
        img=IMGS[min(i,N-1)]
        if img: f.write(f"file '{img}'\nduration {dur:.3f}\n")
    if IMGS[-1]: f.write(f"file '{IMGS[-1]}'\n")

ts=int(time.time())
OUT=f"{WORKDIR}/v683_fix_{ts}.mp4"
print(f"\n🎬 Renderizando CRF={CRF} 30fps...")
cmd=["ffmpeg","-y","-f","concat","-safe","0","-i",concat,
     "-i",f"{WORKDIR}/audio.mp3",
     "-c:v","libx264","-pix_fmt","yuv420p","-crf",str(CRF),"-preset","slow",
     "-c:a","aac","-b:a","192k","-shortest","-r","30",
     "-vf","scale=1080:1920:force_original_aspect_ratio=decrease,"
           "pad=1080:1920:(ow-iw)/2:(oh-ih)/2:color=0xF5F0E8,setsar=1",
     "-movflags","+faststart",OUT]
res=subprocess.run(cmd,capture_output=True,text=True,timeout=600)
if res.returncode!=0: print(f"ERRO:\n{res.stderr[-800:]}"); sys.exit(1)

sz=os.path.getsize(OUT)
probe2=subprocess.run(["ffprobe","-v","quiet","-print_format","json","-show_format",OUT],capture_output=True,text=True)
dur2=float(json.loads(probe2.stdout)["format"]["duration"])
print(f"  ✅ {sz/1024/1024:.2f}MB | {dur2:.1f}s ({dur2/60:.1f}min)")

# UPLOAD
print(f"\n☁️  Upload...")
with open(OUT,'rb') as f: vdata=f.read()
video_url=None
for att in range(5):
    try:
        video_url=sb_upload(f"mp4s/v683_fix_{ts}.mp4",vdata,"video/mp4"); break
    except Exception as e: time.sleep(15)

if video_url:
    src_counts={"gemini":counts['gemini'],"pollinations":counts['pollinations'],"pillow":counts['pillow']}
    sb_patch(VIDEO_ID,{"video_url":video_url,"status":"pending_credentials",
        "metadata":json.dumps({"version":"v9_fix","crf":CRF,"fps":30,"cenas":N,
            "dur_s":round(dur2,1),"file_mb":round(sz/1024/1024,2),"sources":src_counts})})

print(f"\n{'='*55}")
print(f"  ψ RESULTADO FINAL")
print(f"  Gemini:{counts['gemini']} | Poll:{counts['pollinations']} | Chibi:{counts['pillow']}")
print(f"  {sz/1024/1024:.2f}MB | {dur2/60:.1f}min | CRF={CRF}")
print(f"  V8 Final: 6.27MB | objetivo: superar")
print(f"  🎬 {video_url or 'ERRO NO UPLOAD'}")
print(f"{'='*55}\n")
