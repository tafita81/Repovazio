#!/usr/bin/env python3
"""
render_video_v9.py — psicologia.doc V9 MOTION AI
Image: Gemini Flash Image (primário, precisa de key válida)
       Pillow chibi (fallback automático — psych2go style, SEM stick figures)
Veo:   3.x para cenas-chave quando disponível

CORREÇÕES COMPLETAS:
  ✅ Gemini: gemini-2.5-flash-image (modelo correto)
  ✅ Pillow chibi REAL: olhos grandes, corpo, braços, texto — NÃO creme sólido
  ✅ FFmpeg: sem fontweight (não existe), sem font não instalada
  ✅ Texto lower third: "Saude Mental" (corrigido, não "Metal")
  ✅ RATE_REAL dinâmico (len(script)/dur_audio — NUNCA hardcoded)
  ✅ SEM Psicóloga no lower third até jan/2027
  ✅ 🔔 Inscreva-se agora nos últimos 4s
  ✅ Ken Burns suave para cenas estáticas
  ✅ crf=25 Shorts, crf=22 Longs
"""
import os, sys, json, time, base64, asyncio, subprocess
import re, requests, traceback
from pathlib import Path
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor, as_completed
from PIL import Image, ImageDraw, ImageFont

# ── CONFIG ────────────────────────────────────────────────────────────────────
SB_URL      = "https://tpjvalzwkqwttvmszvie.supabase.co"
SB_KEY      = os.environ.get("SUPABASE_SERVICE_KEY", "")
GROQ_KEY    = os.environ.get("GROQ_API_KEY", "")
GEMINI_KEY  = os.environ.get("GEMINI_API_KEY", "")
GEMINI_KEY2 = os.environ.get("GEMINI_API_KEY_2", "")
NVIDIA_KEY  = os.environ.get("NVIDIA_API_KEY", "")

VIDEO_ID = int(sys.argv[1]) if len(sys.argv) > 1 else 683
TS       = int(time.time())
WORK_DIR = Path(f"/tmp/v9_{VIDEO_ID}_{TS}")
WORK_DIR.mkdir(parents=True, exist_ok=True)

TTS_VOICE   = "pt-BR-AntonioNeural"
LOWER_THIRD = "Daniela Coelho | Saude Mental | @psidanielacoelho"  # CORRETO: Mental
CRF_SHORT   = 25
CRF_LONG    = 22
VEO_BUDGET  = 8

GEMINI_MODELS_IMG = [
    "gemini-2.5-flash-image",
    "gemini-3.1-flash-image-preview",
]
VEO_MODELS = [
    "veo-3.1-generate-preview",
    "veo-3.0-generate-preview",
    "veo-2.0-generate-001",
]
ANTI_PLAGIO = (
    "original character design not based on any existing IP, "
    "no text, no logos, no brand marks"
)
PSYCH2GO_BASE = (
    "Psych2Go animation style, kawaii chibi anime character, "
    "cream white background, pastel warm colors, big round expressive eyes, "
    "clean soft lines, psychology channel aesthetic"
)

# Paleta psicologia.doc / Psych2Go
BG_COLOR    = (245, 240, 232)   # creme
SKIN_COLOR  = (255, 220, 185)
HAIR_COLOR  = (60, 40, 20)
OUTFIT_COLOR= (124, 58, 237)    # violeta marca
EYES_COLOR  = (30, 30, 30)
BLUSH_COLOR = (255, 180, 180)

# ── SUPABASE ──────────────────────────────────────────────────────────────────
def sb_get(table, qs=""):
    r = requests.get(f"{SB_URL}/rest/v1/{table}?{qs}",
        headers={"apikey":SB_KEY,"Authorization":f"Bearer {SB_KEY}"}, timeout=30)
    r.raise_for_status(); return r.json()

def sb_patch(table, id_, data):
    r = requests.patch(f"{SB_URL}/rest/v1/{table}?id=eq.{id_}",
        headers={"apikey":SB_KEY,"Authorization":f"Bearer {SB_KEY}",
                 "Content-Type":"application/json","Prefer":"return=representation"},
        json=data, timeout=30)
    r.raise_for_status(); return r.json()

def sb_upload(storage_path, file_path, ctype="video/mp4"):
    with open(file_path,"rb") as f: data = f.read()
    r = requests.post(f"{SB_URL}/storage/v1/object/{storage_path}",
        headers={"apikey":SB_KEY,"Authorization":f"Bearer {SB_KEY}",
                 "Content-Type":ctype,"x-upsert":"true"},
        data=data, timeout=300)
    r.raise_for_status()
    return f"{SB_URL}/storage/v1/object/public/{storage_path}"

# ── TTS ───────────────────────────────────────────────────────────────────────
async def _tts_async(text, path):
    import edge_tts
    await edge_tts.Communicate(text, TTS_VOICE).save(path)

def generate_tts(script, out_path):
    asyncio.run(_tts_async(script, str(out_path)))

def get_audio_duration(path):
    r = subprocess.run(
        ["ffprobe","-v","quiet","-print_format","json","-show_streams",str(path)],
        capture_output=True, text=True)
    for s in json.loads(r.stdout).get("streams",[]):
        if s.get("codec_type") == "audio":
            return float(s.get("duration",60))
    return 60.0

# ── GROQ ──────────────────────────────────────────────────────────────────────
def generate_scene_prompts(script, paragraphs):
    n = len(paragraphs)
    user = f"""Script PT-BR canal psicologia:
{script}

Para cada um dos {n} parágrafos, gere JSON. Retorne EXATAMENTE array JSON com {n} objetos:
[{{"img":"english chibi image prompt","veo":"8s motion clip prompt","key":true/false,"emotion":"neutral","caption":"caption PT máx 20 chars"}}]

key=true para max {VEO_BUDGET} cenas-chave (hook/revelação/clímax).
emotion: neutral|surprised|concerned|happy|focused|dramatic

RETORNE APENAS O ARRAY JSON."""

    try:
        r = requests.post("https://api.groq.com/openai/v1/chat/completions",
            headers={"Authorization":f"Bearer {GROQ_KEY}","Content-Type":"application/json"},
            json={"model":"llama-3.3-70b-versatile",
                  "messages":[{"role":"user","content":user}],
                  "temperature":0.5,"max_tokens":4096},
            timeout=60)
        r.raise_for_status()
        content = r.json()["choices"][0]["message"]["content"].strip()
        m = re.search(r'\[[\s\S]*\]', content)
        if m: return json.loads(m.group())
    except Exception as e:
        print(f"   ⚠️ Groq: {e}")

    emotions = ["neutral","concerned","dramatic","surprised","empathetic","focused","happy","sad"]
    return [{"img":f"kawaii chibi {emotions[i%8]} psychology",
             "veo":f"chibi character {emotions[i%8]} gesture, explains psychology",
             "key": i < min(VEO_BUDGET, n//3),
             "emotion": emotions[i%8],
             "caption": paragraphs[i][:18]+"..." if len(paragraphs[i])>18 else paragraphs[i]}
            for i in range(n)]

# ── PILLOW CHIBI (fallback sem API externa) ───────────────────────────────────
def pillow_chibi(text, emotion, idx, w=1080, h=1920):
    """
    Gera imagem chibi psych2go-style com Pillow.
    NÃO é stick figure — personagem chibi com proporções corretas.
    Fallback quando Gemini/NVIDIA não disponível.
    """
    # Cores por emoção
    emotion_colors = {
        "concerned":  (200, 80, 80),
        "dramatic":   (140, 30, 200),
        "surprised":  (230, 150, 0),
        "happy":      (50, 180, 80),
        "focused":    (30, 120, 220),
        "empathetic": (220, 100, 180),
        "sad":        (80, 100, 200),
        "neutral":    (124, 58, 237),
    }
    accent = emotion_colors.get(emotion, (124, 58, 237))
    
    img = Image.new("RGB", (w, h), BG_COLOR)
    d   = ImageDraw.Draw(img)
    
    # Fundo com suave gradiente diagonal
    for i in range(0, h, 3):
        c = tuple(min(255, int(BG_COLOR[k] + (255-BG_COLOR[k]) * (1 - i/h) * 0.12)) for k in range(3))
        d.line([(0,i),(w,i)], fill=c)
    
    # Decorações de fundo (círculos suaves, estilo psych2go)
    for cx_, cy_, cr, op in [(180,300,80,.15),(900,500,60,.12),(80,900,50,.1),(1000,1100,70,.12)]:
        overlay = Image.new("RGBA",(w,h),(0,0,0,0))
        od = ImageDraw.Draw(overlay)
        a = int(255*op)
        od.ellipse([cx_-cr,cy_-cr,cx_+cr,cy_+cr], fill=(*accent,a))
        img.paste(Image.alpha_composite(img.convert("RGBA"),overlay).convert("RGB"))
        d = ImageDraw.Draw(img)
    
    # ── PERSONAGEM CHIBI ──────────────────────────────────────────────────────
    cx = w // 2
    
    # CABEÇA (grande — 45% da altura do personagem)
    head_y = int(h * 0.15)
    head_r = int(w * 0.20)
    
    # Sombra da cabeça
    d.ellipse([cx-head_r+8, head_y+8, cx+head_r+8, head_y+head_r*2+8], fill=(200,190,180))
    
    # CABELO (por trás)
    hair_ext = int(head_r * 0.2)
    d.ellipse([cx-head_r-hair_ext, head_y-hair_ext,
               cx+head_r+hair_ext, head_y+head_r*2-hair_ext*2], fill=HAIR_COLOR)
    
    # CABEÇA (rosto)
    d.ellipse([cx-head_r, head_y, cx+head_r, head_y+head_r*2], 
              fill=SKIN_COLOR, outline=(220,200,170), width=3)
    
    # Franja sobre o rosto
    d.rectangle([cx-head_r, head_y-hair_ext, cx+head_r, head_y+int(head_r*0.45)],
                fill=HAIR_COLOR)
    d.ellipse([cx-head_r, head_y, cx+head_r, head_y+int(head_r*0.9)], fill=SKIN_COLOR)
    
    # OLHOS (grandes, chibi)
    ey = head_y + int(head_r * 0.90)
    es = int(head_r * 0.28)
    for ex in [cx - int(head_r*0.42), cx + int(head_r*0.42)]:
        # Branco do olho
        d.ellipse([ex-es, ey-es, ex+es, ey+int(es*1.25)], fill="white", outline=(200,200,200), width=1)
        # Íris (cor por emoção)
        d.ellipse([ex-int(es*0.65), ey-int(es*0.55), ex+int(es*0.65), ey+int(es*0.75)], fill=accent)
        # Pupila
        d.ellipse([ex-int(es*0.32), ey-int(es*0.35), ex+int(es*0.32), ey+int(es*0.42)], fill=EYES_COLOR)
        # Brilho no olho
        d.ellipse([ex-int(es*0.35), ey-int(es*0.52), ex-int(es*0.12), ey-int(es*0.25)], fill="white")
    
    # Sobrancelhas por emoção
    brow_y = ey - es - 15
    if emotion in ("concerned","sad","dramatic"):
        d.line([cx-int(head_r*0.55), brow_y-8, cx-int(head_r*0.25), brow_y+3], fill=HAIR_COLOR, width=4)
        d.line([cx+int(head_r*0.25), brow_y+3, cx+int(head_r*0.55), brow_y-8], fill=HAIR_COLOR, width=4)
    elif emotion in ("surprised","happy"):
        d.arc([cx-int(head_r*0.55), brow_y-12, cx-int(head_r*0.2), brow_y+5], 180, 360, fill=HAIR_COLOR, width=3)
        d.arc([cx+int(head_r*0.2), brow_y-12, cx+int(head_r*0.55), brow_y+5], 180, 360, fill=HAIR_COLOR, width=3)
    else:
        d.line([cx-int(head_r*0.55), brow_y, cx-int(head_r*0.22), brow_y], fill=HAIR_COLOR, width=4)
        d.line([cx+int(head_r*0.22), brow_y, cx+int(head_r*0.55), brow_y], fill=HAIR_COLOR, width=4)
    
    # Blush
    blush_y = ey + int(es * 0.7)
    for bx in [cx - int(head_r*0.58), cx + int(head_r*0.58)]:
        d.ellipse([bx-22, blush_y-8, bx+22, blush_y+14], fill=BLUSH_COLOR)
    
    # Boca
    mouth_y = ey + int(head_r * 0.6)
    if emotion in ("happy","surprised"):
        d.arc([cx-22, mouth_y-16, cx+22, mouth_y+16], start=10, end=170, fill=EYES_COLOR, width=3)
        if emotion == "surprised":
            d.ellipse([cx-15, mouth_y-8, cx+15, mouth_y+16], fill="white", outline=EYES_COLOR, width=2)
    elif emotion in ("concerned","sad"):
        d.arc([cx-22, mouth_y-8, cx+22, mouth_y+18], start=190, end=350, fill=EYES_COLOR, width=3)
    else:
        d.arc([cx-18, mouth_y-12, cx+18, mouth_y+12], start=15, end=165, fill=EYES_COLOR, width=3)
    
    # ── CORPO ─────────────────────────────────────────────────────────────────
    body_top  = head_y + head_r * 2 - 15
    body_w    = int(head_r * 1.35)
    body_h    = int(head_r * 1.45)
    body_bot  = body_top + body_h
    
    # Corpo oval (saia/roupa)
    d.ellipse([cx-body_w, body_top, cx+body_w, body_bot],
              fill=accent, outline=(max(0,accent[0]-30),max(0,accent[1]-30),max(0,accent[2]-30)), width=3)
    
    # Detalhe gola
    d.ellipse([cx-int(head_r*0.5), body_top-5, cx+int(head_r*0.5), body_top+int(head_r*0.35)],
              fill=(255,255,255), outline=accent, width=2)
    
    # BRAÇOS
    arm_y  = body_top + int(body_h * 0.25)
    arm_len= int(head_r * 0.65)
    arm_w  = int(head_r * 0.28)
    
    # Braço esquerdo (apontando levemente)
    d.ellipse([cx-body_w-arm_len+10, arm_y, cx-body_w+arm_w-10, arm_y+arm_len*2],
              fill=accent, outline=(max(0,accent[0]-30),max(0,accent[1]-30),max(0,accent[2]-30)), width=2)
    # Mão esquerda
    d.ellipse([cx-body_w-arm_len+3, arm_y+arm_len+20, cx-body_w+arm_w-18, arm_y+arm_len*2+25],
              fill=SKIN_COLOR, outline=(210,190,160), width=2)
    
    # Braço direito
    d.ellipse([cx+body_w-arm_w+10, arm_y, cx+body_w+arm_len-10, arm_y+arm_len*2],
              fill=accent, outline=(max(0,accent[0]-30),max(0,accent[1]-30),max(0,accent[2]-30)), width=2)
    # Mão direita
    d.ellipse([cx+body_w+arm_w-15, arm_y+arm_len+20, cx+body_w+arm_len+3, arm_y+arm_len*2+25],
              fill=SKIN_COLOR, outline=(210,190,160), width=2)
    
    # PERNAS
    leg_w   = int(head_r * 0.28)
    leg_h   = int(head_r * 0.90)
    leg_top2 = body_bot - 25
    
    for lx in [cx - int(head_r*0.42), cx + int(head_r*0.42)]:
        # Perna
        d.rectangle([lx-leg_w//2, leg_top2, lx+leg_w//2, leg_top2+leg_h],
                    fill=SKIN_COLOR, outline=(210,190,160), width=2)
        # Sapato
        d.ellipse([lx-leg_w//2-5, leg_top2+leg_h-10, lx+leg_w//2+15, leg_top2+leg_h+25],
                  fill=HAIR_COLOR)
    
    # ── TEXTO DA CENA ─────────────────────────────────────────────────────────
    text_box_y = int(h * 0.70)
    padding = 40
    
    # Caixa de texto com sombra
    d.rectangle([(80+4, text_box_y+4), (w-80+4, h-100+4)], fill=(200,195,188))
    d.rectangle([(80, text_box_y), (w-80, h-100)],
                fill="white", outline=accent, width=4)
    
    # Ícone violeta no topo da caixa
    d.rectangle([(80, text_box_y), (w-80, text_box_y+6)], fill=accent)
    
    # Texto com wrap
    try:
        font_b = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 34)
        font_n = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 29)
    except:
        font_b = font_n = ImageFont.load_default()
    
    max_chars = 30
    words = text.split()
    lines = []
    curr  = ""
    for word in words:
        trial = (curr + " " + word).strip()
        if len(trial) <= max_chars:
            curr = trial
        else:
            if curr: lines.append(curr)
            curr = word
    if curr: lines.append(curr)
    
    for li, line in enumerate(lines[:5]):
        ty = text_box_y + 22 + li * 42
        bbox = d.textbbox((0,0), line, font=font_n)
        tw = bbox[2]-bbox[0]
        d.text(((w-tw)//2, ty), line, font=font_n, fill=(30,30,30))
    
    # Número da cena (debug)
    d.text((w-70, 40), f"#{idx+1}", font=font_n, fill=(180,170,160))
    
    out = WORK_DIR / f"pillow_{idx:03d}.png"
    img.save(str(out))
    return out

# ── GEMINI IMAGE ──────────────────────────────────────────────────────────────
def gemini_generate_image(prompt, key):
    full = f"{PSYCH2GO_BASE}, {prompt}. {ANTI_PLAGIO}"
    for model in GEMINI_MODELS_IMG:
        try:
            url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={key}"
            r   = requests.post(url,
                headers={"Content-Type":"application/json"},
                json={"contents":[{"parts":[{"text":full}]}],
                      "generationConfig":{"responseModalities":["IMAGE","TEXT"]}},
                timeout=60)
            if r.status_code == 429: time.sleep(5); continue
            if r.status_code != 200:
                print(f"      {model}: HTTP {r.status_code}")
                continue
            for part in r.json().get("candidates",[{}])[0].get("content",{}).get("parts",[]):
                if "inlineData" in part:
                    return base64.b64decode(part["inlineData"]["data"])
        except Exception as e:
            print(f"      {model}: {str(e)[:50]}")
    raise ValueError("Gemini Image indisponível")

# ── VEO 3.x ───────────────────────────────────────────────────────────────────
def veo_generate_clip(veo_prompt, ref_b64, key, duration_s=8):
    for model in VEO_MODELS:
        try:
            url  = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateVideo?key={key}"
            body = {
                "prompt": {"text": f"{PSYCH2GO_BASE}, {veo_prompt}. {ANTI_PLAGIO}"},
                "image": {"imageBytes": ref_b64, "mimeType": "image/png"},
                "generationConfig": {"durationSeconds": duration_s, "aspectRatio": "9:16",
                                     "numberOfVideos": 1, "personGeneration": "ALLOW_ADULT"}
            }
            r = requests.post(url, json=body, timeout=60)
            if r.status_code in (400,403,404): continue
            if r.status_code not in (200,202): continue
            op = r.json()
            op_name = op.get("name","")
            if not op_name:
                return _extract_video(op)
            poll = f"https://generativelanguage.googleapis.com/v1beta/{op_name}?key={key}"
            for i in range(48):
                time.sleep(5)
                pd = requests.get(poll, timeout=30).json()
                if pd.get("done"):
                    return _extract_video(pd.get("response",pd))
        except: pass
    raise ValueError("Veo indisponível")

def _extract_video(resp):
    for s in (resp.get("generatedSamples") or resp.get("videos") or []):
        uri = s.get("video",{}).get("uri") or s.get("uri","")
        if uri:
            vr = requests.get(uri, timeout=120)
            if vr.ok: return vr.content
        b64 = s.get("video",{}).get("videoBytes") or s.get("videoBytes","")
        if b64: return base64.b64decode(b64)
    return None

# ── CLIPS ─────────────────────────────────────────────────────────────────────
def build_from_image_bytes(img_bytes, duration, idx):
    """Gemini imagem → Ken Burns → MP4"""
    p   = WORK_DIR / f"img_{idx:03d}.png"
    out = WORK_DIR / f"clip_{idx:03d}.mp4"
    p.write_bytes(img_bytes)
    df  = max(1, int(duration*30))
    z   = "min(zoom+0.0012,1.25)" if idx%2==0 else "if(lte(zoom,1.0),1.25,max(1.0,zoom-0.0012))"
    vf  = (f"scale=1200:2133,zoompan=z='{z}':d={df}:"
           f"x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':s=1080x1920:fps=30")
    subprocess.run(["ffmpeg","-y","-loop","1","-i",str(p),
        "-vf",vf,"-t",str(duration),
        "-c:v","libx264","-pix_fmt","yuv420p","-r","30",str(out)],
        check=True, capture_output=True, timeout=120)
    return out

def build_from_pillow(pillow_path, duration, idx):
    """Pillow chibi PNG → Ken Burns → MP4"""
    out = WORK_DIR / f"clip_{idx:03d}.mp4"
    df  = max(1, int(duration*30))
    z   = "min(zoom+0.0010,1.18)" if idx%2==0 else "if(lte(zoom,1.0),1.18,max(1.0,zoom-0.0010))"
    vf  = (f"scale=1200:2133,zoompan=z='{z}':d={df}:"
           f"x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':s=1080x1920:fps=30")
    subprocess.run(["ffmpeg","-y","-loop","1","-i",str(pillow_path),
        "-vf",vf,"-t",str(duration),
        "-c:v","libx264","-pix_fmt","yuv420p","-r","30",str(out)],
        check=True, capture_output=True, timeout=120)
    return out

def build_motion_clip(video_bytes, target_dur, idx):
    """Veo MP4 → trim → 1080×1920"""
    raw = WORK_DIR / f"veo_{idx:03d}.mp4"
    out = WORK_DIR / f"clip_{idx:03d}.mp4"
    raw.write_bytes(video_bytes)
    vf  = ("scale=1080:1920:force_original_aspect_ratio=decrease,"
           "pad=1080:1920:(ow-iw)/2:(oh-ih)/2:color=#F5F0E8")
    subprocess.run(["ffmpeg","-y","-stream_loop","-1","-i",str(raw),
        "-vf",vf,"-t",str(target_dur),
        "-c:v","libx264","-pix_fmt","yuv420p","-r","30",str(out)],
        check=True, capture_output=True, timeout=120)
    return out

# ── OVERLAYS + ÁUDIO ──────────────────────────────────────────────────────────
def finalize_video(concat_path, audio_path, out_path, total_dur, is_long):
    """
    Lower third SEM Psicóloga + progress bar + 🔔 Inscreva-se nos últimos 4s
    CORRIGIDO: sem fontweight=bold (não existe no ffmpeg)
    """
    crf = CRF_LONG if is_long else CRF_SHORT
    end = max(0.0, total_dur - 4.0)
    lt  = LOWER_THIRD.replace("'", "\\'")
    
    vf = (
        f"drawtext=text='{lt}'"
        f":fontsize=26:fontcolor=white"
        f":x=(w-text_w)/2:y=h-75"
        f":box=1:boxcolor=black@0.65:boxborderw=8,"
        f"drawbox=x=0:y=h-10"
        f":w='min(iw\\,iw*t/{total_dur:.3f})':h=10"
        f":color=0x7C3AED:t=fill,"
        f"drawtext=text='Inscreva-se agora'"
        f":fontsize=40:fontcolor=0x7C3AED"
        f":x=(w-text_w)/2:y=h/2+200"
        f":box=1:boxcolor=white@0.88:boxborderw=16"
        f":enable='gte(t\\,{end:.3f})'"
    )
    
    result = subprocess.run([
        "ffmpeg","-y",
        "-i",str(concat_path),"-i",str(audio_path),
        "-vf",vf,
        "-c:v","libx264","-crf",str(crf),"-preset","fast",
        "-c:a","aac","-b:a","128k",
        "-pix_fmt","yuv420p","-shortest",
        str(out_path)
    ], capture_output=True, timeout=600)
    
    if result.returncode != 0:
        err = result.stderr.decode(errors="replace")[-400:]
        print(f"FFmpeg stderr:\n{err}")
        raise subprocess.CalledProcessError(result.returncode, "ffmpeg")

# ── MAIN ──────────────────────────────────────────────────────────────────────
def main():
    print(f"\n{'='*60}")
    print(f"  ψ V9 MOTION AI — Video #{VIDEO_ID}")
    print(f"{'='*60}")
    
    rows = sb_get("content_pipeline", f"id=eq.{VIDEO_ID}&select=id,title,script,audio_url,status")
    if not rows: sys.exit(f"❌ Vídeo {VIDEO_ID} não encontrado")
    row = rows[0]
    title, script = row["title"], row["script"]
    print(f"\n📄 {title}")
    print(f"   {len(script)} chars | {row['status']}")
    
    is_long  = len(script) > 4000
    n_scenes = 50 if is_long else 20
    
    # Áudio
    audio_path = WORK_DIR / "audio.mp3"
    if row.get("audio_url"):
        print(f"\n🎙️  Áudio existente...")
        ar = requests.get(row["audio_url"], timeout=60); ar.raise_for_status()
        audio_path.write_bytes(ar.content)
    else:
        print(f"\n🎙️  Gerando TTS AntonioNeural...")
        generate_tts(script, audio_path)
        ap = sb_upload(f"videos/audios/v{VIDEO_ID}_v9_{TS}.mp3", audio_path, "audio/mpeg")
        sb_patch("content_pipeline", VIDEO_ID, {"audio_url": ap})
    
    dur_audio = get_audio_duration(audio_path)
    rate_real = len(script) / dur_audio
    print(f"\n⏱️  {dur_audio:.1f}s | RATE_REAL={rate_real:.2f} chars/s (dinâmico)")
    
    paragraphs = [p.strip() for p in script.split("\n") if p.strip()]
    actual_n   = min(len(paragraphs), n_scenes)
    scene_durs = [max(1.5, min(len(p)/rate_real, 15.0)) for p in paragraphs[:actual_n]]
    print(f"   {actual_n} cenas | ~{sum(scene_durs):.0f}s estimado")
    
    # Prompts Groq
    print(f"\n🧠 Groq: {actual_n} prompts...")
    scenes = generate_scene_prompts(script, paragraphs[:actual_n])
    key_n  = sum(1 for s in scenes if s.get("key"))
    print(f"   {key_n} key (Veo) | {actual_n-key_n} normal (Gemini→Pillow)")
    
    # Tentar referência Gemini
    ref_b64 = None
    gemini_keys = [k for k in [GEMINI_KEY, GEMINI_KEY2] if k]
    if gemini_keys:
        print(f"\n🎨 Tentando referência Gemini...")
        for k in gemini_keys:
            try:
                rb = gemini_generate_image(
                    "psychology channel host chibi, kawaii anime girl, dark hair, "
                    "friendly smile, white cream background, full body, neutral pose", k)
                ref_b64 = base64.b64encode(rb).decode()
                print(f"   ✅ Referência Gemini: {len(rb)//1024}KB")
                break
            except Exception as e:
                print(f"   Key {k[:20]}: {e}")
    
    # Classificar índices
    veo_indices = []
    vrem = VEO_BUDGET
    for i, s in enumerate(scenes[:actual_n]):
        if s.get("key") and vrem > 0 and ref_b64:
            veo_indices.append(i); vrem -= 1
    gem_indices = [i for i in range(actual_n) if i not in veo_indices]
    
    clips     = [None] * actual_n
    veo_count = 0
    gem_count = 0
    pil_count = 0
    
    # Cenas Gemini/Pillow em paralelo
    print(f"\n🖼️  {len(gem_indices)} cenas (Gemini → Pillow fallback, 4 workers)...")
    
    def render_scene(idx):
        s   = scenes[idx] if idx < len(scenes) else {}
        p   = s.get("img", f"kawaii chibi {s.get('emotion','neutral')}")
        emo = s.get("emotion","neutral")
        txt = paragraphs[idx] if idx < len(paragraphs) else ""
        
        k = gemini_keys[idx % len(gemini_keys)] if gemini_keys else ""
        if k:
            try:
                img_bytes = gemini_generate_image(p, k)
                clip = build_from_image_bytes(img_bytes, scene_durs[idx], idx)
                return idx, clip, "gemini"
            except: pass
        
        # Pillow chibi (NÃO stick figure)
        pil_path = pillow_chibi(txt, emo, idx)
        clip = build_from_pillow(pil_path, scene_durs[idx], idx)
        return idx, clip, "pillow"
    
    with ThreadPoolExecutor(max_workers=4) as ex:
        futs = {ex.submit(render_scene, i): i for i in gem_indices}
        done = 0
        for fut in as_completed(futs):
            idx, clip, src = fut.result()
            clips[idx] = clip
            if src=="gemini": gem_count += 1
            else: pil_count += 1
            done += 1
            sys.stdout.write(f"\r   ✅ {done}/{len(gem_indices)} (Gemini:{gem_count} Pillow:{pil_count})")
            sys.stdout.flush()
    print()
    
    # Veo sequencial
    if veo_indices:
        print(f"\n🎬 {len(veo_indices)} cenas Veo...")
        for idx in veo_indices:
            s = scenes[idx] if idx < len(scenes) else {}
            try:
                gk  = GEMINI_KEY or GEMINI_KEY2
                vid = veo_generate_clip(s.get("veo","chibi explains"), ref_b64, gk)
                clips[idx] = build_motion_clip(vid, scene_durs[idx], idx)
                veo_count += 1
            except Exception as e:
                print(f"   [{idx+1}] Veo: {e} → Pillow")
                pp = pillow_chibi(paragraphs[idx] if idx<len(paragraphs) else "", s.get("emotion","neutral"), idx)
                clips[idx] = build_from_pillow(pp, scene_durs[idx], idx)
                pil_count += 1
    
    print(f"\n   ✅ Veo:{veo_count} | Gemini:{gem_count} | Pillow chibi:{pil_count}")
    
    # Concatenar
    print(f"\n🔗 Concatenando {actual_n} clips...")
    ctxt = WORK_DIR / "input.txt"
    with open(ctxt,"w") as f:
        for c in clips:
            if c: f.write(f"file '{c}'\n")
    concat_mp4 = WORK_DIR / "concat.mp4"
    subprocess.run([
        "ffmpeg","-y","-f","concat","-safe","0","-i",str(ctxt),
        "-c:v","libx264","-pix_fmt","yuv420p","-r","30",str(concat_mp4)
    ], check=True, capture_output=True, timeout=300)
    
    # Overlays + áudio
    print(f"🎨 Overlays + áudio...")
    out_name = f"v{VIDEO_ID}_v9_{TS}.mp4"
    out_path = WORK_DIR / out_name
    finalize_video(concat_mp4, audio_path, out_path, dur_audio, is_long)
    
    mb = out_path.stat().st_size / 1024 / 1024
    print(f"   ✅ {mb:.1f}MB | {dur_audio:.1f}s | crf={CRF_LONG if is_long else CRF_SHORT}")
    
    print(f"\n☁️  Upload Supabase...")
    pub_url = sb_upload(f"videos/mp4s/{out_name}", out_path)
    sb_patch("content_pipeline", VIDEO_ID, {
        "video_url": pub_url, "status": "pending_credentials",
        "metadata": json.dumps({
            "render_version": "v9",
            "image_backend": "pillow_chibi_psych2go" if gem_count==0 else "gemini+pillow",
            "veo_clips": veo_count, "gemini_clips": gem_count, "pillow_clips": pil_count,
            "total_clips": actual_n,
            "duration_s": round(dur_audio,2), "rate_real": round(rate_real,3),
            "file_mb": round(mb,2),
            "rendered_at": datetime.utcnow().isoformat(),
            "lower_third": LOWER_THIRD,
        })
    })
    
    print(f"\n{'='*60}")
    print(f"  ✅ V9 COMPLETO — #{VIDEO_ID}")
    print(f"  🎬 {pub_url}")
    print(f"  Veo:{veo_count} | Gemini:{gem_count} | Pillow:{pil_count} | {dur_audio:.1f}s | {mb:.1f}MB")
    print(f"{'='*60}")

if __name__ == "__main__":
    try: main()
    except Exception as e:
        print(f"\n❌ ERRO: {e}"); traceback.print_exc(); sys.exit(1)
