#!/usr/bin/env python3
"""
render_cinematic_v3.py — Cerebro V3 CINEMATOGRAFICO
Estilo: documentario psicologico premium (dark documentary)
DNA visual baseado nos 3 videos de referencia:
  - 60-75% espaco negativo (escuridao)
  - Gradiente profundo #0B1020 a #121A30
  - Silhueta humana abstrata (nao cartoon)
  - Glow emocional azul/roxo
  - Particulas flutuantes
  - Iluminacao rim light
  - ZERO texto nas imagens
"""
import os, json, time, requests, base64, random, math
from PIL import Image, ImageDraw, ImageFilter
import numpy as np
from supabase import create_client

SB_URL = os.environ["SUPABASE_URL"]
SB_KEY = os.environ["SUPABASE_KEY"]
sb = create_client(SB_URL, SB_KEY)
SB_ANON = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InRwanZhbHp3a3F3dHR2bXN6dmllIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NzYwMzUyOTMsImV4cCI6MjA5MTYxMTI5M30.UEgUo0Mw15ihQZykLAY5QApRzgTXkfIewZFzIgwao3Q"
NVIDIA_KEY = os.environ.get("NVIDIA_API_KEY","")

# PALETA CINEMATOGRAFICA (do documento de referencia)
COR_FUNDO_INI   = (18, 26, 48)     # #121A30 introspecção
COR_FUNDO_FIM   = (11, 16, 32)     # #0B1020 vazio existencial
COR_CONSCIENCIA = (0, 194, 255)    # #00C2FF consciencia/descubrimento
COR_ABSTRATO    = (124, 77, 255)   # #7C4DFF abstração mental
COR_ALERTA      = (255, 90, 90)    # #FF5A5A tensão/perigo emocional
COR_DESCOBERTA  = (255, 209, 102)  # #FFD166 descoberta/insight
COR_SILHUETA    = (8, 12, 22)      # quase preto com toque azul

GLOW_POR_TEMA = {
    "narcis": COR_ALERTA,    "manipu": COR_ALERTA,    "toxico": COR_ALERTA,
    "gaslight": COR_ALERTA,  "abuso": COR_ALERTA,
    "trauma": COR_ABSTRATO,  "ansio": COR_ABSTRATO,   "medo": COR_ABSTRATO,
    "cura": COR_CONSCIENCIA, "supera": COR_CONSCIENCIA, "amor": COR_CONSCIENCIA,
    "burnout": COR_DESCOBERTA, "esgota": COR_DESCOBERTA,
    "padrao": COR_CONSCIENCIA,
}

def detectar_tema(titulo, script):
    t = (titulo + " " + script[:300]).lower()
    for tema in GLOW_POR_TEMA:
        if tema in t:
            return tema
    return "padrao"

def dividir_cenas(script, dur_min):
    paras = [p.strip() for p in script.split("\n") if p.strip()]
    if not paras:
        paras = [script]
    n = 5 if dur_min < 3 else min(16, max(7, len(paras)))
    chunk = max(1, len(paras) // n)
    cenas = []
    for i in range(0, len(paras), chunk):
        cenas.append(" ".join(paras[i:i+chunk]))
        if len(cenas) >= n:
            break
    return cenas or [script]

def gerar_ruido(arr, intensidade=0.015):
    """Grain cinematografico sutil."""
    noise = np.random.normal(0, intensidade * 255, arr.shape).astype(np.int16)
    return np.clip(arr.astype(np.int16) + noise, 0, 255).astype(np.uint8)

def gerar_glow_radial(arr, cx, cy, W, H, cor_glow, intensidade):
    """Glow emocional radial — elemento focal principal."""
    result = arr.astype(np.float32)
    max_dist = math.sqrt(W**2 + H**2) * 0.45
    # Usar vetorizacao numpy
    ys = np.arange(H)
    xs = np.arange(W)
    xx, yy = np.meshgrid(xs, ys)
    dist = np.sqrt((xx - cx)**2 + (yy - cy)**2)
    fator = np.clip(1 - dist / max_dist, 0, 1) ** 2.5 * intensidade
    for c_idx, c_val in enumerate(cor_glow):
        result[:,:,c_idx] += fator * c_val
    return np.clip(result, 0, 255).astype(np.uint8)

def gerar_vinheta(arr, W, H):
    """Vinheta cinematografica — escurece as bordas."""
    cx, cy = W // 2, H // 2
    xs = np.arange(W)
    ys = np.arange(H)
    xx, yy = np.meshgrid(xs, ys)
    dist = np.sqrt((xx - cx)**2 + (yy - cy)**2)
    max_r = math.sqrt(cx**2 + cy**2)
    fator = np.clip(1 - (dist / max_r) ** 1.8 * 0.72, 0.12, 1.0)
    result = arr.astype(np.float32)
    for c in range(3):
        result[:,:,c] *= fator
    return np.clip(result, 0, 255).astype(np.uint8)

def gerar_particulas(draw, W, H, seed):
    """Particulas flutuantes — movimento subconsciente."""
    random.seed(seed)
    n = random.randint(40, 80)
    for _ in range(n):
        x = random.randint(0, W)
        y = random.randint(0, H)
        r = random.uniform(0.5, 3.0)
        op = random.uniform(0.04, 0.20)
        v = int(op * 220)
        cor = (v, v, v)
        if random.random() < 0.25:  # elongada (movimento)
            dx = random.randint(3, 18)
            draw.line([x-dx, y, x+dx, y], fill=cor, width=max(1,int(r)))
        else:
            draw.ellipse([x-r, y-r, x+r, y+r], fill=cor)

def gerar_silhueta(draw, cx, cy, altura, composicao):
    """Silhueta humana abstrata — estilo documentario premium. SEM CARTOON."""
    cor = COR_SILHUETA
    comp = composicao % 6

    if comp == 0:  # Sentado pensativo (cabeca inclinada, curvado)
        draw.rounded_rectangle([cx-38, cy-altura//9, cx+38, cy+22], radius=20, fill=cor)
        draw.rounded_rectangle([cx-44, cy+10, cx+44, cy+altura//2], radius=22, fill=cor)
        draw.rounded_rectangle([cx-58, cy+altura//3, cx+2, cy+altura//2+22], radius=14, fill=cor)
        draw.rounded_rectangle([cx-2, cy+altura//3, cx+58, cy+altura//2+22], radius=14, fill=cor)
        draw.ellipse([cx-30, cy-altura//4-30, cx+30, cy-altura//4+30], fill=cor)

    elif comp == 1:  # Em pe, de costas (olhando para longe)
        lar = max(48, altura//6)
        draw.rounded_rectangle([cx-lar//2, cy-altura//2, cx+lar//2, cy+altura//4], radius=lar//4, fill=cor)
        draw.ellipse([cx-lar//4, cy-altura//2-lar//3, cx+lar//4, cy-altura//2+lar//4], fill=cor)
        draw.rounded_rectangle([cx-lar//3, cy+altura//4, cx-2, cy+altura//2], radius=8, fill=cor)
        draw.rounded_rectangle([cx+2, cy+altura//4, cx+lar//3, cy+altura//2], radius=8, fill=cor)
        draw.rounded_rectangle([cx-lar, cy-altura//3, cx-lar//2+5, cy+altura//6], radius=10, fill=cor)
        draw.rounded_rectangle([cx+lar//2-5, cy-altura//3, cx+lar, cy+altura//6], radius=10, fill=cor)

    elif comp == 2:  # Sentado na borda (pernas penduradas)
        lar = max(42, altura//6)
        draw.rounded_rectangle([cx-lar, cy-lar, cx+lar, cy+lar//2], radius=lar//3, fill=cor)
        draw.ellipse([cx-lar//2, cy-lar*2, cx+lar//2, cy-lar], fill=cor)
        draw.rounded_rectangle([cx-lar//2, cy+lar//2, cx-3, cy+lar*2], radius=10, fill=cor)
        draw.rounded_rectangle([cx+3, cy+lar//2, cx+lar//2, cy+lar*2], radius=10, fill=cor)

    elif comp == 3:  # Figura eterea (dissolving)
        lar = max(38, altura//7)
        draw.rounded_rectangle([cx-lar, cy-altura//2, cx+lar, cy+altura//3], radius=lar//3, fill=cor)
        draw.ellipse([cx-lar//2, cy-altura//2-lar//2, cx+lar//2, cy-altura//2+lar//2], fill=cor)

    elif comp == 4:  # Dois corpos distantes
        lar = max(28, altura//8)
        draw.rounded_rectangle([cx-altura//2-lar, cy-lar*2, cx-altura//2+lar, cy+lar], radius=lar//3, fill=cor)
        draw.ellipse([cx-altura//2-lar//2, cy-lar*3, cx-altura//2+lar//2, cy-lar*2], fill=cor)
        draw.rounded_rectangle([cx+altura//4-lar, cy-lar*2-8, cx+altura//4+lar, cy+lar+8], radius=lar//3, fill=cor)
        draw.ellipse([cx+altura//4-lar//2, cy-lar*3-8, cx+altura//4+lar//2, cy-lar*2-8], fill=cor)

    else:  # Apenas metade visivel (entrando no frame)
        lar = max(48, altura//6)
        x_start = max(0, cx - altura//4)
        draw.rounded_rectangle([x_start, cy-lar, cx+lar, cy+lar], radius=lar//4, fill=cor)
        draw.ellipse([cx-lar//3-5, cy-lar*2, cx+lar//3-5, cy-lar], fill=cor)

def gerar_cena_cinematografica(titulo, trecho, cena_idx, total_cenas, video_id, dur_min):
    """Gera frame dark documentary cinematografico."""
    is_short = dur_min < 3
    W, H = (1080, 1920) if is_short else (1920, 1080)

    random.seed(cena_idx * 31 + video_id * 7)
    np.random.seed(cena_idx * 13 + video_id)

    # 1. FUNDO — gradiente escuro profundo
    arr = np.zeros((H, W, 3), dtype=np.uint8)
    for y in range(H):
        t = y / H
        for c in range(3):
            arr[y, :, c] = int(COR_FUNDO_INI[c] * (1-t) + COR_FUNDO_FIM[c] * t)

    # 2. Grain cinematografico (camada base)
    arr = gerar_ruido(arr, intensidade=0.018)

    # 3. Determinar cor de glow pelo tema
    tema = detectar_tema(titulo, trecho)
    cor_glow = GLOW_POR_TEMA.get(tema, COR_CONSCIENCIA)

    # 4. Glow principal
    glow_posicoes = [
        (int(W*0.25), int(H*0.28)),
        (int(W*0.75), int(H*0.25)),
        (int(W*0.50), int(H*0.20)),
        (int(W*0.70), int(H*0.58)),
        (int(W*0.30), int(H*0.52)),
    ]
    gx, gy = glow_posicoes[cena_idx % len(glow_posicoes)]
    intensidade = random.uniform(0.06, 0.13)
    arr = gerar_glow_radial(arr, gx, gy, W, H, cor_glow, intensidade)

    # 5. Segundo glow mais fraco (profundidade)
    gx2, gy2 = W - gx, H - gy
    arr = gerar_glow_radial(arr, gx2, gy2, W, H, COR_ABSTRATO, intensidade * 0.35)

    # 6. Converter para PIL
    img = Image.fromarray(arr, "RGB")
    draw = ImageDraw.Draw(img)

    # 7. Particulas flutuantes
    gerar_particulas(draw, W, H, cena_idx * video_id + cena_idx)

    # 8. Silhueta humana abstrata
    altura_silh = int(H * random.uniform(0.38, 0.52))
    posicoes = [
        (int(W*0.40), int(H*0.58)),
        (int(W*0.60), int(H*0.62)),
        (int(W*0.35), int(H*0.65)),
        (int(W*0.65), int(H*0.55)),
        (int(W*0.50), int(H*0.68)),
        (int(W*0.30), int(H*0.60)),
    ]
    sx, sy = posicoes[cena_idx % len(posicoes)]
    gerar_silhueta(draw, sx, sy, altura_silh, cena_idx)

    # 9. Rim light — luz suave nas bordas da silhueta (cinematico)
    rim_x = sx + altura_silh//4 if cena_idx % 2 == 0 else sx - altura_silh//4
    rim_cor = tuple(min(100, int(c * 0.12)) for c in cor_glow)
    for dy in range(-altura_silh//2, altura_silh//2, 10):
        px, py = rim_x, sy + dy
        if 0 <= px < W and 0 <= py < H:
            r_rim = random.uniform(1, 4)
            draw.ellipse([px-r_rim, py-r_rim, px+r_rim, py+r_rim], fill=rim_cor)

    # 10. Vinheta + grain final
    arr = np.array(img)
    arr = gerar_vinheta(arr, W, H)
    arr = gerar_ruido(arr, intensidade=0.008)

    path = "/tmp/cena_cinem_" + str(video_id) + "_" + str(cena_idx) + ".jpg"
    Image.fromarray(arr, "RGB").save(path, "JPEG", quality=94)
    return path

def tentar_nvidia(prompt, video_id, cena_idx):
    if not NVIDIA_KEY:
        return None
    endpoints = [
        ("https://integrate.api.nvidia.com/v1/images/generations",
         {"model":"black-forest-labs/flux-schnell","prompt":prompt,
          "n":1,"size":"1344x768","response_format":"b64_json"}),
        ("https://ai.api.nvidia.com/v1/genai/black-forest-labs/flux-schnell",
         {"prompt":prompt,"width":1344,"height":768,"num_inference_steps":4,
          "guidance_scale":3.5,"num_images":1,"seed":random.randint(1,999999)}),
        ("https://ai.api.nvidia.com/v1/genai/stabilityai/stable-diffusion-xl",
         {"prompt":prompt,"width":1344,"height":768,"num_inference_steps":25,
          "guidance_scale":8.0,"seed":random.randint(1,999999)}),
    ]
    for ep, payload in endpoints:
        try:
            r = requests.post(ep,
                headers={"Authorization":"Bearer "+NVIDIA_KEY,"Content-Type":"application/json"},
                json=payload, timeout=90)
            print("    NVIDIA " + ep.split("/")[-1] + ": " + str(r.status_code))
            if r.status_code != 200:
                try: print("      " + str(r.json().get("detail",""))[:100])
                except: print("      " + r.text[:100])
                continue
            data = r.json()
            b64 = (data.get("artifacts",[{}])[0].get("base64","") or
                   data.get("data",[{}])[0].get("b64_json",""))
            if b64:
                p = "/tmp/nv_" + str(video_id) + "_" + str(cena_idx) + ".jpg"
                with open(p,"wb") as f:
                    f.write(base64.b64decode(b64))
                print("    NVIDIA OK: " + str(len(b64)//1024) + "KB")
                return p
        except Exception as e:
            print("    NVIDIA exc: " + str(e))
    return None

def gerar_prompt_cinematico(titulo, trecho, cena_idx, tema):
    glow_desc = {
        "narcis":"crimson red emotional danger glow",
        "abuso":"crimson red emotional danger glow",
        "trauma":"deep violet purple melancholic glow",
        "ansio":"deep violet purple melancholic glow",
        "cura":"ethereal blue cyan hopeful glow",
        "padrao":"soft blue introspective glow",
    }
    gd = glow_desc.get(tema, "soft blue introspective glow")
    comps = [
        "lone silhouette sitting contemplative head bowed knees drawn",
        "solitary figure standing with back turned gazing into darkness",
        "lone person sitting at edge feet dangling philosophical",
        "abstract dissolving human silhouette ethereal atmospheric",
        "two distant silhouettes separated by vast empty dark space",
        "partial silhouette emerging from darkness at edge of frame",
    ]
    comp = comps[cena_idx % len(comps)]
    return (
        "ultra cinematic existential psychology documentary frame, "
        "deep navy black gradient background, "
        "massive negative space 70 percent darkness and shadow, "
        + comp + ", "
        "subtle floating particles atmospheric fog, "
        "volumetric " + gd + ", "
        "rim lighting on edges only deep shadows, "
        "human silhouette symbolic minimalistic no face no details, "
        "no cartoon no meme no bright colors no text no words no letters no numbers, "
        "premium educational psychology documentary cinematography, "
        "single emotional focal point cinematic depth, "
        "palette dark navy deep purple subtle accent only, "
        "emotionally immersive intelligent melancholy"
    )

def upload_img(path, video_id, cena_idx):
    fname = "v3/cinem_" + str(video_id) + "_" + str(cena_idx) + "_" + str(int(time.time())) + ".jpg"
    with open(path,"rb") as f:
        data = f.read()
    try:
        sb.storage.from_("videos").upload(fname, data,
            file_options={"content-type":"image/jpeg","x-upsert":"true"})
        return SB_URL + "/storage/v1/object/public/videos/" + fname
    except:
        r = requests.post(
            SB_URL + "/storage/v1/object/videos/" + fname,
            headers={"apikey":SB_ANON,"Authorization":"Bearer "+SB_ANON,
                     "Content-Type":"image/jpeg","x-upsert":"true"},
            data=data
        )
        if r.status_code in [200,201]:
            return SB_URL + "/storage/v1/object/public/videos/" + fname
    return None

def get_pendentes():
    r = sb.table("content_pipeline").select(
        "id,title,script,audio_url,metadata,duracao_min,pub_order"
    ).eq("status","mp4_ready").is_("mp4_url",None).order("pub_order").limit(5).execute()
    return r.data or []

def processar(v):
    vid_id = v["id"]
    title  = v.get("title","")
    script = v.get("script","") or ""
    dur    = float(v.get("duracao_min") or 0.9)
    print("\n  #" + str(vid_id) + " " + title[:55])
    tema  = detectar_tema(title, script)
    cenas = dividir_cenas(script, dur)
    print("    tema=" + tema + " | " + str(len(cenas)) + " cenas cinematograficas")
    urls = []
    for i, trecho in enumerate(cenas):
        print("    cena " + str(i+1) + "/" + str(len(cenas)) + "...")
        prompt = gerar_prompt_cinematico(title, trecho, i, tema)
        img = tentar_nvidia(prompt, vid_id, i)
        fonte = "nvidia"
        if not img:
            img = gerar_cena_cinematografica(title, trecho, i, len(cenas), vid_id, dur)
            fonte = "pillow_cinematico"
        url = upload_img(img, vid_id, i)
        if url:
            urls.append(url)
            print("      cena " + str(i+1) + " (" + fonte + ") OK")
        time.sleep(0.3)
    if not urls:
        print("    sem imagens"); return False
    sb.table("content_pipeline").update({
        "status":"video_ready","mp4_url":None,
        "metadata":(v.get("metadata") or {}) | {
            "quantum_images":urls,"quantum_image":urls[0],
            "n_cenas":len(urls),"tema":tema,
            "render_method":"cinematic_v3_dark_documentary",
            "processado_em":int(time.time()),
        }
    }).eq("id",vid_id).execute()
    print("    video_ready " + str(len(urls)) + " cenas cinematograficas")
    return True

def main():
    print("=== RENDER CINEMATICO V3 — Dark Documentary Premium ===")
    nvidia_status = "OK" if NVIDIA_KEY else "ausente, Pillow cinematico"
    print("NVIDIA: " + nvidia_status)
    videos = get_pendentes()
    print("Videos: " + str(len(videos)))
    ok = 0
    for v in videos:
        try:
            if processar(v): ok += 1
            time.sleep(1)
        except:
            import traceback; traceback.print_exc()
    print("Concluido: " + str(ok) + "/" + str(len(videos)))

if __name__ == "__main__":
    main()
