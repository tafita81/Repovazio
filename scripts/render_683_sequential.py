#!/usr/bin/env python3
"""
render_683_sequential.py — POLLINATIONS SEQUENCIAL GARANTIDO
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Gera imagens UMA POR VEZ (sequencial) para evitar rate limit.
Pollinations Flux → cada imagem ~400-500KB → arquivo final ~6-8MB.
Supera o V8 Final (6.27MB) com Pollinations de qualidade.
"""
import os, sys, json, subprocess, requests, time, io, warnings
from PIL import Image, ImageDraw
import urllib.parse
warnings.filterwarnings("ignore")

VIDEO_ID   = 683
SB_URL     = "https://tpjvalzwkqwttvmszvie.supabase.co"
SB_KEY     = os.environ.get("SUPABASE_SERVICE_KEY","")
W, H       = 1080, 1920
CRF        = 18
WORKDIR    = "/tmp/v683_seq"
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
row = requests.get(
    f"{SB_URL}/rest/v1/content_pipeline?id=eq.{VIDEO_ID}&select=id,script",
    headers={"apikey":SB_KEY,"Authorization":f"Bearer {SB_KEY}"},timeout=30).json()[0]
SCRIPT = row["script"].strip()
PARAS  = [p.strip() for p in SCRIPT.split('\n\n') if p.strip()]
N      = len(PARAS)

print(f"{'='*60}")
print(f"  ψ RENDER SEQUENCIAL — Pollinations Garantido")
print(f"  {N} cenas | objetivo: superar V8 Final 6.27MB")
print(f"{'='*60}\n")

# Captions
CAPTIONS = []
for p in PARAS:
    cap = p[:28].split('.')[0].split(',')[0].split('?')[0].strip()
    CAPTIONS.append(cap[:28])
if CAPTIONS: CAPTIONS[-1] = "INSCREVA-SE AGORA 🔔"

# 33 prompts detalhados para Pollinations
PROMPTS = [
    "chibi anime girl auburn wavy hair round glasses pale yellow cardigan anxious at night holding smartphone worried face blue glow cream background kawaii flat design no text",
    "chibi anime girl auburn hair round glasses yellow cardigan reading phone message disappointed face small rain cloud soft sad cream background kawaii",
    "chibi anime characters auburn hair glasses yellow cardigan AND dark styled hair navy blazer meeting at party sparkle effects captivated expression cream background kawaii",
    "chibi anime girl auburn hair round glasses yellow cardigan thoughtful expression floating question marks around her unease cream background kawaii flat design",
    "chibi anime girl short dark bob hair mint green blouse small psi symbol gold pin warm reassuring smile looking at viewer cream background kawaii flat design professional",
    "chibi anime girl auburn hair round glasses yellow cardigan sad hunched posture blame arrow pointing at her victim cream background kawaii",
    "chibi anime characters auburn hair glasses AND dark navy blazer dismissive gesture boy girl shrinking smaller power imbalance cream background kawaii",
    "chibi anime woman dark neat bun white lab coat clipboard authoritative warm expression research data cream background kawaii flat design",
    "chibi anime man dark styled hair navy blazer holding friendly smiling theater mask sinister dark shadow behind him cream background kawaii dramatic",
    "chibi anime man dark navy blazer shrugging hands raised innocently large number 1 badge floating red X symbol cream background kawaii",
    "chibi anime girl auburn hair round glasses yellow cardigan touching temple remembering glowing thought bubble confused cream background kawaii",
    "chibi anime characters auburn hair glasses AND dark navy blazer dismissive finger pointing girl shrinking smaller power dynamics cream background kawaii",
    "chibi anime characters white lab coat dark bun AND auburn hair glasses yellow cardigan brain diagram glowing highlights realization cream background kawaii",
    "chibi anime girl short dark bob hair mint green blouse holding golden shield warm protective golden light surrounding another chibi girl cream background kawaii",
    "chibi anime characters large number 2 badge auburn hair glasses emotional speech bubble dark navy blazer boy bored expression cream background kawaii",
    "chibi anime characters auburn hair glasses yellow cardigan AND dark navy blazer girl crying boy sighing dramatically cold gap between them cream background kawaii",
    "chibi anime characters dark navy blazer surrounded by negative label floating tags auburn hair girl confused shrinking cream background kawaii",
    "chibi anime girl auburn hair round glasses yellow cardigan hands pressed together apologizing gesture sad small cream background kawaii",
    "chibi anime girl bouncy curly dark hair small flower clip orange sweater worried protective friend expression cream background kawaii",
    "chibi anime characters curly dark hair orange sweater AND auburn hair round glasses face to face serious conversation revelation cream background kawaii",
    "chibi anime girl auburn hair round glasses yellow cardigan looking at mirror with fading reflection identity erasure sad cream background kawaii",
    "chibi anime characters large number 3 badge auburn hair girl carrying heavy guilt weight not hers dark blazer boy relaxed cream background kawaii",
    "chibi anime characters auburn hair glasses yellow cardigan AND dark navy blazer boy arriving late casual shrug girl apologizing confused wall clock cream background kawaii",
    "chibi anime girl auburn hair round glasses yellow cardigan hands to face worried unfair question mark floating cream background kawaii",
    "chibi anime girl short dark bob hair mint green blouse psi pin urgent warm direct expression facing viewer golden glow cream background kawaii",
    "chibi anime woman dark bun white lab coat pointing at scientific iceberg diagram narcissism tip above water massive hidden structure cream background kawaii",
    "chibi anime characters white lab coat dark bun AND auburn hair glasses yellow cardigan cycle flowchart love bomb devalue discard arrows shock cream background kawaii",
    "chibi anime characters short dark bob mint blouse AND auburn hair glasses yellow cardigan bright glowing door to freedom hope warmth cream background kawaii",
    "chibi anime girl short dark bob hair mint green blouse psi pin sincere direct eye contact with viewer hand on heart golden light cream background kawaii professional",
    "chibi anime characters dark bob mint blouse AND auburn hair glasses AND curly dark hair orange sweater three girls arms around each other unity cream background kawaii",
    "chibi anime man dark styled hair navy blazer hiding something important in shadow dramatic tension girl about to discover truth cream background kawaii",
    "chibi anime girl auburn hair round glasses yellow cardigan lightbulb revelation moment eyes wide understanding everything clicking cream background kawaii",
    "chibi anime characters celebration scene giant golden bell sparkles rainbow confetti four characters arms raised joyfully festive cream background kawaii",
]

def gen_pollinations(prompt, idx, seed_offset=0):
    """Pollinations com múltiplas tentativas e retry inteligente."""
    # Adicionar estilo profissional
    full = (
        f"Psych2Go anime chibi kawaii style illustration, {prompt}, "
        f"white cream background #F5F0E8, pastel soft colors, flat design, "
        f"expressive big eyes, clean line art, professional animation quality, "
        f"no text, no watermarks, no logos, original character design"
    )
    enc = urllib.parse.quote(full)
    seed = (42 + idx * 31 + seed_offset * 100) % 99999

    for model in ["flux", "turbo", "flux-realism"]:
        for attempt in range(3):
            try:
                url = (f"https://image.pollinations.ai/prompt/{enc}"
                       f"?width=576&height=1024&seed={seed+attempt}"
                       f"&nologo=true&model={model}&enhance=true")
                r = requests.get(url, timeout=90, verify=False)
                if r.status_code == 200:
                    ct = r.headers.get('content-type','')
                    if 'image' in ct and len(r.content) > 30000:
                        img = Image.open(io.BytesIO(r.content)).convert("RGB")
                        img = img.resize((W,H), Image.LANCZOS)
                        out = f"{WORKDIR}/ai_{idx:02d}.jpg"
                        img.save(out, "JPEG", quality=98)  # 98 = qualidade máxima
                        return out, model, len(r.content)//1024
                elif r.status_code == 402:
                    print(f"  [{idx+1:02d}] ⏳ rate limit, aguardando 30s...")
                    time.sleep(30)
                    continue
            except Exception as e:
                if attempt < 2: time.sleep(5)
        time.sleep(2)  # Pausa entre modelos
    return None, None, 0

def gen_chibi_hq(idx):
    """Chibi Pillow de alta qualidade."""
    img = Image.new("RGB",(W,H),(245,240,232)); draw = ImageDraw.Draw(img)
    for y in range(H):
        t=y/H; r=int(245+(228-245)*t); g=int(240+(222-240)*t); b=int(232+(215-232)*t)
        draw.line([(0,y),(W,y)],fill=(r,g,b))
    draw.ellipse([W//2-320,H//2-380,W//2+320,H//2+380],fill=(238,230,218))
    clrs=[(100,185,130),(80,130,200),(200,90,130),(130,180,80),(200,150,70),(150,90,200),(80,180,180)]
    clr=clrs[idx%len(clrs)]; cx=W//2; cy=H//2-100
    draw.ellipse([cx-80,cy+220,cx+80,cy+265],fill=(175,165,155))
    draw.rounded_rectangle([cx-82,cy+25,cx+82,cy+255],radius=25,fill=clr)
    draw.ellipse([cx-95,cy-215,cx+95,cy+40],fill=(255,220,185))
    draw.ellipse([cx-98,cy-265,cx+98,cy-90],fill=(35,22,8))
    for ex in [cx-38,cx+22]:
        draw.ellipse([ex,cy-100,ex+38,cy-64],fill=(255,255,255))
        draw.ellipse([ex+5,cy-95,ex+33,cy-69],fill=(30,20,60))
        draw.ellipse([ex+26,cy-97,ex+34,cy-89],fill=(255,255,255))
    for bx in [cx-58,cx+22]: draw.ellipse([bx,cy-40,bx+44,cy-10],fill=(255,185,185))
    draw.arc([cx-28,cy-25,cx+28,cy+12],start=0,end=180,fill=(180,55,55),width=4)
    draw.text((cx-8,cy+32),"ψ",fill=GOLD)
    out=f"{WORKDIR}/ai_{idx:02d}.jpg"; img.save(out,"JPEG",quality=97)
    return out

def add_overlay(img_path, caption):
    img=Image.open(img_path).convert("RGB"); draw=ImageDraw.Draw(img)
    for y in range(H-105,H):
        t=(y-(H-105))/105
        draw.line([(0,y),(W,y)],fill=(int(8+12*t),int(6+8*t),int(18+15*t)))
    draw.rectangle([0,H-105,5,H],fill=VERM); draw.rectangle([0,H-4,W,H],fill=VERM)
    draw.text((22,H-95),"ψ",fill=GOLD); draw.text((60,H-90),"Daniela Coelho",fill=BRAN)
    draw.text((60,H-55),"Saúde Mental  |  @psidanielacoelho",fill=LILAS)
    if caption and len(caption)>2:
        cap=caption[:30].upper(); bw=min(len(cap)*15+60,W-80); bcx=W//2; by=60
        draw.rounded_rectangle([bcx-bw//2+3,by-22+3,bcx+bw//2+3,by+26+3],radius=16,fill=(180,170,200))
        draw.rounded_rectangle([bcx-bw//2,by-22,bcx+bw//2,by+26],radius=16,fill=(252,250,255),outline=(210,200,235),width=2)
        draw.text((bcx-bw//2+26,by-9),cap,fill=(25,15,55))
    img.save(img_path,"JPEG",quality=98)

# GERAÇÃO SEQUENCIAL
print(f"🎨 Gerando {N} imagens SEQUENCIALMENTE (Pollinations garantido)...\n")
IMGS = []; counts = {"poll":0, "chibi":0}; total_kb = 0
t0 = time.time()

for idx, prompt in enumerate(PROMPTS):
    cap = CAPTIONS[idx] if idx < len(CAPTIONS) else ""

    path, model, kb = gen_pollinations(prompt, idx)
    if path:
        add_overlay(path, cap)
        final_kb = os.path.getsize(path)//1024
        total_kb += final_kb
        print(f"  [{idx+1:02d}/{N}] 🌐 {model} | {kb}KB → {final_kb}KB")
        counts["poll"] += 1
    else:
        path = gen_chibi_hq(idx)
        add_overlay(path, cap)
        final_kb = os.path.getsize(path)//1024
        total_kb += final_kb
        print(f"  [{idx+1:02d}/{N}] ✏️  chibi | {final_kb}KB")
        counts["chibi"] += 1
    IMGS.append(path)
    time.sleep(1.5)  # Pausa entre imagens para evitar rate limit

gen_t = time.time()-t0
avg_kb = total_kb//N
print(f"\n  ✅ Poll:{counts['poll']} | Chibi:{counts['chibi']} | {gen_t:.0f}s")
print(f"  Média por imagem: {avg_kb}KB | Total imagens: {total_kb}KB\n")

# Áudio
print("🎙️  Baixando áudio V8 Final...")
ar=requests.get(f"{SB_URL}/storage/v1/object/public/videos/audios/v683_v8_1778892031.mp3",timeout=60)
with open(f"{WORKDIR}/audio.mp3",'wb') as f: f.write(ar.content)
probe=subprocess.run(["ffprobe","-v","quiet","-print_format","json","-show_format",
    f"{WORKDIR}/audio.mp3"],capture_output=True,text=True)
DUR=float(json.loads(probe.stdout)["format"]["duration"])
RATE=len(SCRIPT)/DUR; DURS=[max(0.5,round(len(p)/RATE,3)) for p in PARAS]
print(f"  {DUR:.1f}s | RATE={RATE:.3f}")

# ffconcat
concat=f"{WORKDIR}/concat.txt"
with open(concat,'w') as f:
    for i,dur in enumerate(DURS):
        img=IMGS[min(i,N-1)]
        if img: f.write(f"file '{img}'\nduration {dur:.3f}\n")
    if IMGS[-1]: f.write(f"file '{IMGS[-1]}'\n")

ts=int(time.time()); OUT=f"{WORKDIR}/v683_seq_{ts}.mp4"
print(f"\n🎬 Renderizando CRF={CRF} 30fps...")
cmd=["ffmpeg","-y","-f","concat","-safe","0","-i",concat,
     "-i",f"{WORKDIR}/audio.mp3",
     "-c:v","libx264","-pix_fmt","yuv420p","-crf",str(CRF),"-preset","slow",
     "-c:a","aac","-b:a","192k","-shortest","-r","30",
     "-vf","scale=1080:1920:force_original_aspect_ratio=decrease,"
           "pad=1080:1920:(ow-iw)/2:(oh-ih)/2:color=0xF5F0E8,setsar=1",
     "-movflags","+faststart",OUT]
res=subprocess.run(cmd,capture_output=True,text=True,timeout=600)
if res.returncode!=0: print(f"ERRO:{res.stderr[-400:]}"); sys.exit(1)

sz=os.path.getsize(OUT)
probe2=subprocess.run(["ffprobe","-v","quiet","-print_format","json","-show_format",OUT],
    capture_output=True,text=True)
dur2=float(json.loads(probe2.stdout)["format"]["duration"])
print(f"  ✅ {sz/1024/1024:.2f}MB | {dur2:.1f}s")
print(f"  V8 Final: 6.27MB | {'✅ SUPEROU' if sz > 6.27*1024*1024 else '❌ ainda menor'}")

# Upload
print(f"\n☁️  Upload...")
with open(OUT,'rb') as f: vdata=f.read()
video_url=None
for att in range(5):
    try: video_url=sb_upload(f"mp4s/v683_seq_{ts}.mp4",vdata,"video/mp4"); break
    except: time.sleep(15)

if video_url:
    sb_patch(VIDEO_ID,{"video_url":video_url,"status":"pending_credentials",
        "metadata":json.dumps({"version":"sequential_pollinations","crf":CRF,
            "poll":counts["poll"],"chibi":counts["chibi"],"avg_kb_per_img":avg_kb,
            "dur_s":round(dur2,1),"file_mb":round(sz/1024/1024,2)})})

print(f"\n{'='*60}")
print(f"  ψ RESULTADO SEQUENCIAL")
print(f"  Poll:{counts['poll']}/{N} | {sz/1024/1024:.2f}MB | {dur2/60:.1f}min")
print(f"  🎬 {video_url or 'ERRO'}")
print(f"{'='*60}\n")
