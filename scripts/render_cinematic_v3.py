#!/usr/bin/env python3
"""
render_cinematic_v3.py — Cerebro V3 CINEMATOGRAFICO
Estilo: documentario psicologico premium (Einzelganger / Pursuit of Wonder)
DNA Visual:
  - 60-75% espaco negativo
  - Gradiente profundo #0B1020 → #121A30
  - Silhueta humana abstrata (nao cartoon)
  - Glow emocional azul/roxo
  - Particulas flutuantes
  - Iluminacao cinematografica falsa (rim light)
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

# PALETA CINEMATOGRAFICA DEFINITIVA (do documento de referencia)
PALETA = {
    "vazio":       (11, 16, 32),    # #0B1020 — fundo profundo
    "intro":       (18, 26, 48),    # #121A30 — introspecção
    "consciencia": (0, 194, 255),   # #00C2FF — luz da consciencia
    "abstrato":    (124, 77, 255),  # #7C4DFF — abstração mental
    "alerta":      (255, 90, 90),   # #FF5A5A — tensão emocional
    "clareza":     (255, 255, 255), # #FFFFFF — revelação
    "descoberta":  (255, 209, 102), # #FFD166 — descoberta
}

# Composicoes por emocao (qual glow usar)
GLOW_POR_EMOCAO = {
    "narcis": "alerta",     "manipu": "alerta",  "toxico": "alerta",
    "trauma": "abstrato",   "dor":    "abstrato", "abuso": "abstrato",
    "ansio":  "descoberta", "medo":   "descoberta",
    "cura":   "consciencia","supera": "consciencia", "amor": "consciencia",
    "padrao": "consciencia",
}

def detectar_tema(titulo: str, script: str) -> str:
    t = (titulo + " " + script[:300]).lower()
    for tema in GLOW_POR_EMOCAO:
        if tema in t: return tema
    return "padrao"

def dividir_cenas(script: str, dur_min: float) -> list:
    paras = [p.strip() for p in script.split("\n") if p.strip()]
    if not paras: paras = [script]
    n = 5 if dur_min < 3 else min(16, max(7, len(paras)))
    chunk = max(1, len(paras)//n)
    cenas = []
    for i in range(0, len(paras), chunk):
        cenas.append(" ".join(paras[i:i+chunk]))
        if len(cenas) >= n: break
    return cenas or [script]

def gerar_ruido_atmosferico(arr: np.ndarray, intensidade: float = 0.015) -> np.ndarray:
    """Adiciona grain cinematografico sutil"""
    noise = np.random.normal(0, intensidade * 255, arr.shape).astype(np.int16)
    resultado = arr.astype(np.int16) + noise
    return np.clip(resultado, 0, 255).astype(np.uint8)

def gerar_particulas(draw: ImageDraw, W: int, H: int, seed: int, cor_glow: tuple):
    """Particulas flutuantes — movimento subconsciente"""
    random.seed(seed * 7)
    for _ in range(random.randint(35, 70)):
        x = random.randint(0, W)
        y = random.randint(0, H)
        r = random.uniform(0.5, 3.0)
        opacidade = random.uniform(0.04, 0.18)
        # Particulas brancas ou da cor do glow
        if random.random() < 0.3:
            cor = tuple(int(c * opacidade) for c in cor_glow) + (int(opacidade * 200),)
        else:
            v = int(opacidade * 220)
            cor = (v, v, v, int(opacidade * 180))
        # Algumas particulas sao elongadas (movimento)
        if random.random() < 0.25:
            dx = random.randint(3, 15)
            draw.line([x-dx, y, x+dx, y], fill=cor[:3], width=max(1, int(r)))
        else:
            draw.ellipse([x-r, y-r, x+r, y+r], fill=cor[:3])

def gerar_silhueta_humana(draw: ImageDraw, cx: int, cy: int, altura: int,
                           composicao: int, cor_borda: tuple, opacidade: float):
    """
    Silhueta humana abstrata — estilo documentario (nao cartoon).
    SEM ROSTO, SEM DETALHES EXCESSIVOS.
    Composicoes variam por cena:
    0: sentado pensativo (fetal)
    1: em pe olhando longe (costa ao espectador)
    2: sentado na borda (reflexao)
    3: deitado (depressao/descanso)
    4: em pe de frente (abstrato)
    5: dois corpos distantes
    6: silhueta saindo do frame
    """
    # Cor da silhueta: escura, quase preta, com toque de azul profundo
    cor = (8, 12, 22)
    borda = tuple(int(c * 0.35) for c in cor_borda)  # rim light suave

    comp = composicao % 7

    if comp == 0:  # Sentado pensativo (cabeca inclinada, joelhos dobrados)
        # Corpo curvado
        draw.ellipse([cx-35, cy-altura//8, cx+35, cy+20], fill=cor, outline=borda, width=2)
        draw.rounded_rectangle([cx-40, cy+10, cx+40, cy+altura//2], radius=20, fill=cor, outline=borda, width=2)
        # Pernas dobradas
        draw.rounded_rectangle([cx-55, cy+altura//3, cx+5, cy+altura//2+20], radius=12, fill=cor)
        draw.rounded_rectangle([cx-5, cy+altura//3, cx+55, cy+altura//2+20], radius=12, fill=cor)
        # Cabeca inclinada para frente
        draw.ellipse([cx-28, cy-altura//4-28, cx+28, cy-altura//4+28],
                     fill=cor, outline=borda, width=2)

    elif comp == 1:  # Em pe, de costas
        lar = max(50, altura//5)
        # Corpo
        draw.rounded_rectangle([cx-lar//2, cy-altura//2, cx+lar//2, cy+altura//4],
                                radius=lar//4, fill=cor, outline=borda, width=2)
        # Cabeca (pequena de costas)
        draw.ellipse([cx-lar//4, cy-altura//2-lar//3, cx+lar//4, cy-altura//2+lar//4],
                     fill=cor, outline=borda, width=1)
        # Pernas
        draw.rounded_rectangle([cx-lar//3, cy+altura//4, cx-2, cy+altura//2],
                                radius=8, fill=cor)
        draw.rounded_rectangle([cx+2, cy+altura//4, cx+lar//3, cy+altura//2],
                                radius=8, fill=cor)
        # Bracos ao lado
        draw.rounded_rectangle([cx-lar, cy-altura//3, cx-lar//2+5, cy+altura//6],
                                radius=10, fill=cor, outline=borda, width=1)
        draw.rounded_rectangle([cx+lar//2-5, cy-altura//3, cx+lar, cy+altura//6],
                                radius=10, fill=cor, outline=borda, width=1)

    elif comp == 2:  # Sentado na borda (pernas penduradas)
        lar = max(45, altura//5)
        draw.rounded_rectangle([cx-lar, cy-lar, cx+lar, cy+lar//2], radius=lar//3, fill=cor, outline=borda, width=2)
        # Cabeca
        draw.ellipse([cx-lar//2, cy-lar*2, cx+lar//2, cy-lar], fill=cor, outline=borda, width=2)
        # Pernas penduradas
        draw.rounded_rectangle([cx-lar//2, cy+lar//2, cx-3, cy+lar*2], radius=10, fill=cor)
        draw.rounded_rectangle([cx+3, cy+lar//2, cx+lar//2, cy+lar*2], radius=10, fill=cor)

    elif comp == 3:  # Deitado (horizontal)
        draw.ellipse([cx-20, cy-20, cx+20, cy+20], fill=cor, outline=borda, width=2)  # cabeca
        draw.rounded_rectangle([cx+10, cy-15, cx+altura//2, cy+15], radius=12, fill=cor)  # corpo
        draw.rounded_rectangle([cx+altura//3, cy+5, cx+altura//2+30, cy+20], radius=8, fill=cor)  # pernas

    elif comp == 4:  # Abstrato — forma dissolving
        lar = max(40, altura//6)
        # Figura mais eterea, menos definida
        for i in range(4):
            off_x = i * 3
            off_y = i * 2
            opac = int(255 * (0.6 - i * 0.12))
            c = tuple(min(255, v + off_x * 2) for v in cor) + (opac,)
            img_lay = Image.new("RGBA", (1, 1))  # dummy
            draw.rounded_rectangle(
                [cx-lar+off_x, cy-altura//2+off_y, cx+lar-off_x, cy+altura//3-off_y],
                radius=lar//3, fill=cor, outline=borda, width=max(1, 2-i)
            )
        draw.ellipse([cx-lar//2, cy-altura//2-lar//2, cx+lar//2, cy-altura//2+lar//2],
                     fill=cor, outline=borda, width=1)

    elif comp == 5:  # Dois corpos distantes
        lar = max(30, altura//7)
        # Figura 1 (esquerda, menor — distante)
        draw.rounded_rectangle([cx-altura//2-lar, cy-lar*2, cx-altura//2+lar, cy+lar],
                                radius=lar//3, fill=cor)
        draw.ellipse([cx-altura//2-lar//2, cy-lar*3, cx-altura//2+lar//2, cy-lar*2],
                     fill=cor)
        # Figura 2 (direita, maior — proxima)
        draw.rounded_rectangle([cx+altura//4-lar, cy-lar*2-10, cx+altura//4+lar, cy+lar+10],
                                radius=lar//3, fill=cor, outline=borda, width=2)
        draw.ellipse([cx+altura//4-lar//2, cy-lar*3-10, cx+altura//4+lar//2, cy-lar*2-10],
                     fill=cor, outline=borda, width=2)

    else:  # comp 6: Silhueta saindo do frame (so parte visivel)
        lar = max(50, altura//5)
        # Apenas metade do corpo visivel (saindo pela esquerda)
        x_start = max(0, cx - altura//3)
        draw.rounded_rectangle([x_start, cy-lar, cx+lar, cy+lar],
                                radius=lar//4, fill=cor, outline=borda, width=2)
        draw.ellipse([cx-lar//3-5, cy-lar*2, cx+lar//3-5, cy-lar],
                     fill=cor, outline=borda, width=1)

def gerar_glow_emocional(img_arr: np.ndarray, cx: int, cy: int,
                          W: int, H: int, cor_glow: tuple, intensidade: float):
    """Glow radial cinematografico — elemento focal principal"""
    # Criar layer de glow com gradiente radial
    glow = np.zeros((H, W, 3), dtype=np.float32)
    max_dist = math.sqrt(W**2 + H**2) * 0.45

    for y in range(0, H, 2):  # skip pixels para performance
        for x in range(0, W, 2):
            dist = math.sqrt((x-cx)**2 + (y-cy)**2)
            if dist < max_dist:
                fator = (1 - dist/max_dist) ** 2.5 * intensidade
                glow[y, x] = [c * fator for c in cor_glow]
                glow[y+1, x] = glow[y, x]
                glow[y, x+1] = glow[y, x]
                glow[y+1, x+1] = glow[y, x]

    # Blur para suavizar
    from PIL import Image as PILImage
    glow_img = PILImage.fromarray(np.clip(glow, 0, 255).astype(np.uint8))
    glow_blur = glow_img.filter(ImageFilter.GaussianBlur(radius=60))
    glow_arr = np.array(glow_blur).astype(np.float32)

    # Blend com additive
    resultado = img_arr.astype(np.float32) + glow_arr * 0.65
    return np.clip(resultado, 0, 255).astype(np.uint8)

def gerar_vinheta(arr: np.ndarray, W: int, H: int) -> np.ndarray:
    """Vinheta cinematografica — escurece as bordas"""
    vignette = np.ones((H, W), dtype=np.float32)
    cx, cy = W//2, H//2
    max_r = math.sqrt(cx**2 + cy**2)
    for y in range(H):
        for x in range(W):
            dist = math.sqrt((x-cx)**2 + (y-cy)**2)
            fator = 1 - (dist/max_r) ** 1.8 * 0.7
            vignette[y, x] = max(0.15, fator)
    vignette_rgb = np.stack([vignette]*3, axis=-1)
    return (arr.astype(np.float32) * vignette_rgb).astype(np.uint8)

def gerar_cena_cinematografica(titulo: str, script_trecho: str,
                                cena_idx: int, total_cenas: int,
                                video_id: int, dur_min: float) -> str:
    """
    Gera frame cinematografico dark documentary.
    Regras:
    - 60-75% espaco negativo (escuridao)
    - Silhueta humana abstrata (NAO cartoon)
    - Glow emocional sutil
    - Particulas flutuantes
    - Ruido/grain cinematografico
    - ZERO texto
    """
    is_short = dur_min < 3
    W, H = (1080, 1920) if is_short else (1920, 1080)

    random.seed(cena_idx * 31 + video_id * 7)
    np.random.seed(cena_idx * 13 + video_id)

    # 1. FUNDO — gradiente profundo
    fundo_cor_ini = PALETA["intro"]     # #121A30
    fundo_cor_fim = PALETA["vazio"]     # #0B1020
    arr = np.zeros((H, W, 3), dtype=np.uint8)
    for y in range(H):
        t = y / H
        cor = tuple(int(fundo_cor_ini[i] * (1-t) + fundo_cor_fim[i] * t) for i in range(3))
        arr[y, :] = cor

    # 2. GRAIN cinematografico (antes de tudo)
    arr = gerar_ruido_atmosferico(arr, intensidade=0.018)

    # Converter para PIL para operacoes de desenho
    img = Image.fromarray(arr, 'RGB')
    draw = ImageDraw.Draw(img)

    # 3. Determinar tema e cor de glow
    tema = detectar_tema(titulo, script_trecho)
    nome_glow = GLOW_POR_EMOCAO.get(tema, "consciencia")
    cor_glow = PALETA[nome_glow]

    # 4. GLOW principal — posicao varia por cena
    glows = [
        (int(W*0.25), int(H*0.30)),   # alto esquerda
        (int(W*0.75), int(H*0.25)),   # alto direita
        (int(W*0.50), int(H*0.20)),   # centro alto
        (int(W*0.70), int(H*0.60)),   # centro direita baixo
        (int(W*0.30), int(H*0.55)),   # centro esquerda
    ]
    gx, gy = glows[cena_idx % len(glows)]
    arr = np.array(img)
    intensidade_glow = random.uniform(0.06, 0.14)
    arr = gerar_glow_emocional(arr, gx, gy, W, H, cor_glow, intensidade_glow)

    # Segundo glow mais fraco (profundidade)
    gx2 = W - gx; gy2 = H - gy
    arr = gerar_glow_emocional(arr, gx2, gy2, W, H,
                                PALETA["abstrato"], intensidade_glow * 0.4)

    img = Image.fromarray(arr, 'RGB')
    draw = ImageDraw.Draw(img)

    # 5. PARTICULAS
    gerar_particulas(draw, W, H, cena_idx * video_id, cor_glow)

    # 6. SILHUETA HUMANA — 25-40% da area, posicao varia
    # Regra: silhueta ocupa 25-40%, resto e espaco negativo
    altura_silh = int(H * random.uniform(0.38, 0.52))
    composicoes_pos = [
        (int(W*0.40), int(H*0.58)),   # centro-esquerda baixo
        (int(W*0.60), int(H*0.62)),   # centro-direita
        (int(W*0.35), int(H*0.65)),   # esquerda baixo
        (int(W*0.65), int(H*0.55)),   # direita
        (int(W*0.50), int(H*0.68)),   # centro
        (int(W*0.30), int(H*0.60)),   # esquerda
        (int(W*0.55), int(H*0.70)),   # centro-baixo
    ]
    sx, sy = composicoes_pos[cena_idx % len(composicoes_pos)]
    gerar_silhueta_humana(draw, sx, sy, altura_silh, cena_idx, cor_glow, 0.3)

    # 7. RIM LIGHT — luz nas bordas da silhueta (cinematico)
    # Simulado via linha de glow ao lado da silhueta
    rim_x = sx + altura_silh//4 if cena_idx % 2 == 0 else sx - altura_silh//4
    for dy in range(-altura_silh//2, altura_silh//2, 8):
        px, py = rim_x, sy + dy
        if 0 <= px < W and 0 <= py < H:
            r_rim = random.uniform(1, 4)
            intensidade_rim = random.uniform(0.05, 0.15)
            cor_rim = tuple(int(c * intensidade_rim) for c in cor_glow)
            draw.ellipse([px-r_rim, py-r_rim, px+r_rim, py+r_rim], fill=cor_rim)

    # 8. NEBULOSA / ATMOSFERA — camada de fog sutil (parte inferior)
    for y in range(int(H*0.70), H):
        t = (y - H*0.70) / (H*0.30)
        alfa = int(t * 25)
        for x in range(0, W, 3):
            px = draw.bitmap if hasattr(draw,'bitmap') else None
            r_fog = random.randint(0, 3)
            if r_fog == 0:
                cor_fog = tuple(min(255, c + 5) for c in PALETA["intro"])
                draw.point([x, y], fill=cor_fog)

    # 9. VINHETA final
    arr = np.array(img)
    arr = gerar_vinheta(arr, W, H)

    # 10. Grain final adicional (grain em cima de tudo)
    arr = gerar_ruido_atmosferico(arr, intensidade=0.008)

    path = f"/tmp/cena_cinem_{video_id}_{cena_idx}.jpg"
    Image.fromarray(arr, 'RGB').save(path, "JPEG", quality=94)
    return path

def tentar_nvidia_cinematico(prompt: str, video_id: int, cena_idx: int) -> str | None:
    """NVIDIA com prompt cinematografico premium"""
    if not NVIDIA_KEY: return None
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
                headers={"Authorization":f"Bearer {NVIDIA_KEY}","Content-Type":"application/json"},
                json=payload, timeout=90)
            print(f"    NVIDIA {ep.split('/')[-1]}: {r.status_code}")
            if r.status_code != 200:
                try: print(f"      {r.json().get('detail',r.text[:100])}")
                except: print(f"      {r.text[:100]}")
                continue
            data = r.json()
            b64 = (data.get("artifacts",[{}])[0].get("base64","") or
                   data.get("data",[{}])[0].get("b64_json",""))
            if b64:
                p = f"/tmp/nv_{video_id}_{cena_idx}.jpg"
                with open(p,"wb") as f: f.write(base64.b64decode(b64))
                print(f"    NVIDIA OK: {len(b64)//1024}KB"); return p
        except Exception as e:
            print(f"    NVIDIA exc: {e}")
    return None

def gerar_prompt_cinematico(titulo: str, trecho: str, cena_idx: int, tema: str) -> str:
    glows = {"alerta":"crimson red danger glow","abstrato":"deep purple violet glow",
             "consciencia":"ethereal blue cyan glow","descoberta":"golden amber discovery glow",
             "padrao":"soft blue introspective glow"}
    glow_desc = glows.get(tema, "soft blue glow")
    composicoes = [
        "lone silhouette sitting contemplative head bowed",
        "solitary figure standing with back turned gazing into darkness",
        "lone person sitting at edge feet dangling existential",
        "silhouette in reclining philosophical pose",
        "abstract dissolving human form ethereal",
        "two distant silhouettes separated vast empty space",
        "partial silhouette emerging from darkness",
    ]
    comp = composicoes[cena_idx % len(composicoes)]
    return (
        f"ultra cinematic existential psychology documentary frame, "
        f"deep navy black gradient background #0B1020 to #121A30, "
        f"minimalist premium motion graphics, psychological storytelling, "
        f"massive negative space 70 percent darkness, {comp}, "
        f"subtle floating particles atmospheric, volumetric {glow_desc}, "
        f"rim lighting edges only, deep shadows, emotional contrast, "
        f"human silhouette symbolic minimalistic no face no details, "
        f"no cartoon no meme no bright colors no text no words no letters, "
        f"visuals inspired by premium educational psychology documentary, "
        f"single emotional focal point, cinematic depth of field, "
        f"color palette dark navy blue deep purple subtle accent, "
        f"emotionally immersive intelligent melancholy atmosphere"
    )

def upload_img(path: str, video_id: int, cena_idx: int) -> str | None:
    fname = f"v3/cinem_{video_id}_{cena_idx}_{int(time.time())}.jpg"
    with open(path,"rb") as f: data = f.read()
    try:
        sb.storage.from_("videos").upload(fname, data,
            file_options={"content-type":"image/jpeg","x-upsert":"true"})
        return f"{SB_URL}/storage/v1/object/public/videos/{fname}"
    except:
        r = requests.post(f"{SB_URL}/storage/v1/object/videos/{fname}",
            headers={"apikey":SB_ANON,"Authorization":f"Bearer {SB_ANON}",
                     "Content-Type":"image/jpeg","x-upsert":"true"}, data=data)
        if r.status_code in [200,201]:
            return f"{SB_URL}/storage/v1/object/public/videos/{fname}"
    return None

def get_pendentes():
    r = sb.table("content_pipeline").select(
        "id,title,script,audio_url,metadata,duracao_min,pub_order"
    ).eq("status","mp4_ready").is_("mp4_url",None).order("pub_order").limit(5).execute()
    return r.data or []

def processar(v: dict) -> bool:
    vid_id = v["id"]; title = v.get("title","")
    script = v.get("script","") or ""
    dur = float(v.get("duracao_min") or 0.9)
    print(f"\n  #{vid_id} {title[:55]}")

    tema = detectar_tema(title, script)
    cenas = dividir_cenas(script, dur)
    print(f"    tema={tema} | {len(cenas)} cenas cinematograficas")

    urls = []
    for i, trecho in enumerate(cenas):
        print(f"    cena {i+1}/{len(cenas)}...")
        prompt = gerar_prompt_cinematico(title, trecho, i, tema)
        img = tentar_nvidia_cinematico(prompt, vid_id, i)
        fonte = "nvidia"
        if not img:
            img = gerar_cena_cinematografica(title, trecho, i, len(cenas), vid_id, dur)
            fonte = "pillow_cinematico"
        url = upload_img(img, vid_id, i)
        if url:
            urls.append(url)
            print(f"      cena {i+1} ({fonte}) OK")
        time.sleep(0.3)

    if not urls: print("    sem imagens"); return False
    sb.table("content_pipeline").update({
        "status":"video_ready","mp4_url":None,
        "metadata":(v.get("metadata") or {}) | {
            "quantum_images":urls,"quantum_image":urls[0],
            "n_cenas":len(urls),"tema":tema,
            "render_method":"cinematic_v3_dark_documentary",
            "processado_em":int(time.time()),
        }
    }).eq("id",vid_id).execute()
    print(f"    video_ready {len(urls)} cenas cinematograficas"); return True

def main():
    print("=== RENDER CINEMATICO V3 — Dark Documentary Premium ===")
    print(f"NVIDIA: {'OK' if NVIDIA_KEY else 'ausente, Pillow cinematico'}")
    videos = get_pendentes(); print(f"Videos: {len(videos)}")
    ok = 0
    for v in videos:
        try:
            if processar(v): ok += 1
            time.sleep(1)
        except:
            import traceback; traceback.print_exc()
    print(f"Concluido: {ok}/{len(videos)}")

if __name__ == "__main__":
    main()
