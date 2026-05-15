#!/usr/bin/env python3
"""
render_flat_v4.py — Cerebro V4 — Estilo School of Life + Kurzgesagt
DNA Visual:
  - Fundos coloridos e quentes (NAO ESCUROS)
  - Personagens 2D flat com rosto expressivo (olhos + boca)
  - Elementos de cena ricos (sol, nuvens, plantas, objetos)
  - Paletas vibrantes por emocao
  - Composicoes variadas por cena
  - Estilo ilustrativo educativo premium
"""
import os, json, time, requests, base64, random, math
from PIL import Image, ImageDraw
import numpy as np
from supabase import create_client

SB_URL = os.environ["SUPABASE_URL"]
SB_KEY = os.environ["SUPABASE_KEY"]
sb = create_client(SB_URL, SB_KEY)
SB_ANON = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InRwanZhbHp3a3F3dHR2bXN6dmllIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NzYwMzUyOTMsImV4cCI6MjA5MTYxMTI5M30.UEgUo0Mw15ihQZykLAY5QApRzgTXkfIewZFzIgwao3Q"
NVIDIA_KEY = os.environ.get("NVIDIA_API_KEY","")

# PALETAS VIBRANTES (School of Life / Kurzgesagt)
PALETAS = {
    "narcis":  {"bg":(255,235,210), "char":(220,80,60),  "acc":(120,40,20), "sky":(255,200,150)},
    "manipu":  {"bg":(255,235,210), "char":(220,80,60),  "acc":(120,40,20), "sky":(255,200,150)},
    "toxico":  {"bg":(255,235,210), "char":(220,80,60),  "acc":(120,40,20), "sky":(255,200,150)},
    "trauma":  {"bg":(225,230,255), "char":(90,100,200), "acc":(40,50,130), "sky":(180,190,240)},
    "ansio":   {"bg":(255,248,220), "char":(240,160,30), "acc":(180,100,0), "sky":(255,230,150)},
    "medo":    {"bg":(255,248,220), "char":(240,160,30), "acc":(180,100,0), "sky":(255,230,150)},
    "cura":    {"bg":(220,248,220), "char":(60,170,60),  "acc":(20,100,20), "sky":(150,230,150)},
    "supera":  {"bg":(220,248,220), "char":(60,170,60),  "acc":(20,100,20), "sky":(150,230,150)},
    "amor":    {"bg":(255,220,230), "char":(220,80,120), "acc":(160,30,70), "sky":(255,180,200)},
    "autoest": {"bg":(215,240,255), "char":(50,140,220), "acc":(10,80,160), "sky":(150,210,255)},
    "solidao": {"bg":(230,225,245), "char":(120,90,180), "acc":(70,40,120), "sky":(190,180,220)},
    "padrao":  {"bg":(255,245,220), "char":(240,160,50), "acc":(180,90,0),  "sky":(255,220,150)},
}

TONS_PELE = [
    (255,218,185), (245,198,160), (225,175,130),
    (200,148,100), (175,115,75),  (150,90,55),
    (120,70,40),   (95,50,25),
]

def detectar_tema(titulo, script):
    t = (titulo + " " + script[:300]).lower()
    for tema in PALETAS:
        if tema in t: return tema
    return "padrao"

def dividir_cenas(script, dur_min):
    paras = [p.strip() for p in script.split("\n") if p.strip()]
    if not paras: paras = [script]
    n = 5 if dur_min < 3 else min(14, max(7, len(paras)))
    chunk = max(1, len(paras)//n)
    cenas = []
    for i in range(0, len(paras), chunk):
        cenas.append(" ".join(paras[i:i+chunk]))
        if len(cenas) >= n: break
    return cenas or [script]

def desenhar_sol(draw, W, H, cor_sol=(255,220,50), tamanho=80):
    """Sol com raios — elemento School of Life / Kurzgesagt"""
    x, y = int(W*0.88), int(H*0.10)
    # Raios
    for ang in range(0, 360, 30):
        rad = math.radians(ang)
        x1 = x + int((tamanho+8)*math.cos(rad))
        y1 = y + int((tamanho+8)*math.sin(rad))
        x2 = x + int((tamanho+22)*math.cos(rad))
        y2 = y + int((tamanho+22)*math.sin(rad))
        draw.line([x1,y1,x2,y2], fill=cor_sol, width=4)
    draw.ellipse([x-tamanho,y-tamanho,x+tamanho,y+tamanho], fill=cor_sol)

def desenhar_nuvens(draw, W, H, cor=(255,255,255)):
    """Nuvens simples estilo flat"""
    clouds = [(int(W*0.2), int(H*0.12)), (int(W*0.55), int(H*0.07)), (int(W*0.75), int(H*0.15))]
    for cx, cy in clouds:
        r = 28
        draw.ellipse([cx-r,cy-r,cx+r,cy+r], fill=cor)
        draw.ellipse([cx-r+20,cy-r+8,cx+r+20,cy+r+8], fill=cor)
        draw.ellipse([cx-r+10,cy-r-8,cx+r+10,cy+r-8], fill=cor)

def desenhar_plantas(draw, W, H, cor_caule=(80,140,60), cor_folha=(60,180,60)):
    """Plantas decorativas — educativo e amigavel"""
    posicoes = [(int(W*0.05), H), (int(W*0.92), H), (int(W*0.15), H)]
    for px, py in posicoes:
        # Caule
        draw.rectangle([px-5, py-80, px+5, py], fill=cor_caule)
        # Folhas
        for dy, dx in [(-70, 25), (-50, -25), (-35, 20)]:
            draw.ellipse([px+dx-20, py+dy-15, px+dx+20, py+dy+15], fill=cor_folha)

def desenhar_chao(draw, W, H, cor_bg, cor_char):
    """Linha do chao estilo School of Life"""
    cor_chao = tuple(max(0, int(c*0.85)) for c in cor_bg)
    draw.rectangle([0, int(H*0.72), W, H], fill=cor_chao)

def desenhar_personagem(draw, cx, cy, pele, cor_char, cor_acc, seed, expressao="neutro"):
    """
    Personagem flat 2D com ROSTO — estilo School of Life
    Expressoes: neutro, feliz, triste, surpreso, reflexivo
    """
    random.seed(seed*13)
    pele_esc = tuple(max(0, c-30) for c in pele)
    cabelo_c = TONS_PELE[(seed*3) % len(TONS_PELE)]
    # Tons de cabelo (mais escuros que a pele)
    cabelo_c = tuple(max(0, c-60) for c in pele)

    altura = 220  # altura total do personagem

    # PERNAS
    draw.rounded_rectangle([cx-30, cy+60, cx-6, cy+120], radius=10, fill=pele_esc)
    draw.rounded_rectangle([cx+6, cy+60, cx+30, cy+120], radius=10, fill=pele_esc)

    # SAPATOS
    cor_sapato = tuple(max(0, c-40) for c in cor_char)
    draw.ellipse([cx-38, cy+108, cx-2, cy+130], fill=cor_sapato)
    draw.ellipse([cx+2, cy+108, cx+38, cy+130], fill=cor_sapato)

    # CORPO (camisa/roupa)
    draw.rounded_rectangle([cx-45, cy-10, cx+45, cy+70], radius=18, fill=cor_char)

    # BRACO ESQ
    pose = seed % 5
    if pose == 0:  # Neutro
        draw.rounded_rectangle([cx-72, cy+5, cx-45, cy+60], radius=10, fill=pele, width=0)
        draw.rounded_rectangle([cx+45, cy+5, cx+72, cy+60], radius=10, fill=pele, width=0)
    elif pose == 1:  # Apontando
        draw.rounded_rectangle([cx-72, cy-20, cx-45, cy+30], radius=10, fill=pele)
        draw.rounded_rectangle([cx+45, cy+10, cx+72, cy+60], radius=10, fill=pele)
    elif pose == 2:  # Bracos abertos
        draw.rounded_rectangle([cx-90, cy+8, cx-45, cy+52], radius=10, fill=pele)
        draw.rounded_rectangle([cx+45, cy+8, cx+90, cy+52], radius=10, fill=pele)
    elif pose == 3:  # Mao no queixo (reflexivo)
        draw.rounded_rectangle([cx-68, cy-5, cx-45, cy+40], radius=10, fill=pele)
        draw.rounded_rectangle([cx+45, cy+12, cx+68, cy+55], radius=10, fill=pele)
        draw.ellipse([cx-70, cy-20, cx-40, cy+10], fill=pele)  # mao no queixo
    else:  # Uma mao acima
        draw.rounded_rectangle([cx-72, cy+8, cx-45, cy+60], radius=10, fill=pele)
        draw.rounded_rectangle([cx+45, cy-35, cx+72, cy+25], radius=10, fill=pele)

    # PESCOCO
    draw.rounded_rectangle([cx-15, cy-30, cx+15, cy+0], radius=7, fill=pele)

    # CABECA
    hr = 52
    hy = cy - hr - 30

    # Cabelo
    draw.ellipse([cx-hr-8, hy-hr-15, cx+hr+8, hy+20], fill=cabelo_c)
    # Rosto
    draw.ellipse([cx-hr, hy-hr, cx+hr, hy+hr], fill=pele)

    # ROSTO COM EXPRESSAO (diferencial do dark V3!)
    eye_y = hy - 8
    # Olhos (sempre expressivos)
    draw.ellipse([cx-22, eye_y-10, cx-6, eye_y+10], fill=(30,30,30))
    draw.ellipse([cx+6, eye_y-10, cx+22, eye_y+10], fill=(30,30,30))
    # Brilho nos olhos
    draw.ellipse([cx-18, eye_y-8, cx-13, eye_y-3], fill=(255,255,255))
    draw.ellipse([cx+10, eye_y-8, cx+15, eye_y-3], fill=(255,255,255))

    # Boca por expressao
    if expressao == "feliz" or pose == 2:
        draw.arc([cx-18, hy+5, cx+18, hy+28], 0, 180, fill=(60,30,10), width=4)
    elif expressao == "triste" or pose == 3:
        draw.arc([cx-16, hy+12, cx+16, hy+30], 180, 360, fill=(60,30,10), width=4)
    elif expressao == "surpreso" or pose == 1:
        draw.ellipse([cx-12, hy+8, cx+12, hy+28], fill=(60,30,10))
    else:  # neutro
        draw.line([cx-14, hy+18, cx+14, hy+18], fill=(60,30,10), width=3)

    # Sobrancelhas por expressao
    if pose == 2 or expressao == "feliz":
        draw.arc([cx-22, eye_y-22, cx-6, eye_y-8], 180, 360, fill=(60,30,10), width=3)
        draw.arc([cx+6, eye_y-22, cx+22, eye_y-8], 180, 360, fill=(60,30,10), width=3)
    elif pose == 3 or expressao == "reflexivo":
        draw.line([cx-22, eye_y-16, cx-6, eye_y-12], fill=(60,30,10), width=3)
        draw.line([cx+6, eye_y-12, cx+22, eye_y-16], fill=(60,30,10), width=3)

def desenhar_balao_fala(draw, cx, cy, cor_acc, cena_idx):
    """Balao de fala opcional — estilo educativo"""
    if cena_idx % 3 != 0: return  # so aparece em algumas cenas
    bx, by = cx + 65, cy - 100
    draw.rounded_rectangle([bx-5, by-15, bx+70, by+25], radius=10, fill=(255,255,255), outline=cor_acc, width=2)
    # Ponteiro do balao
    draw.polygon([(bx+5,by+25), (bx-5,by+15), (bx+20,by+25)], fill=(255,255,255))
    draw.polygon([(bx+5,by+25), (bx-5,by+15), (bx+20,by+25)], outline=cor_acc, fill=None)

def gerar_cena_flat(titulo, trecho, cena_idx, total_cenas, video_id, dur_min):
    """
    Gera cena flat 2D estilo School of Life + Kurzgesagt.
    COLORIDA, EXPRESSIVA, COM PERSONAGENS COM ROSTO.
    """
    is_short = dur_min < 3
    W, H = (1080, 1920) if is_short else (1920, 1080)

    random.seed(cena_idx * 31 + video_id * 7)
    np.random.seed(cena_idx * 13 + video_id)

    tema = detectar_tema(titulo, trecho)
    pal = PALETAS.get(tema, PALETAS["padrao"])
    bg_c = pal["bg"]
    char_c = pal["char"]
    acc_c = pal["acc"]
    sky_c = pal["sky"]

    # FUNDO: gradiente ceu
    arr = np.zeros((H, W, 3), dtype=np.uint8)
    for y in range(H):
        t = y / H
        # Gradiente do ceu para o chao
        for c in range(3):
            arr[y,:,c] = int(sky_c[c] * (1-t*0.3) + bg_c[c] * t)

    img = Image.fromarray(arr, "RGB")
    draw = ImageDraw.Draw(img)

    # CHAO
    desenhar_chao(draw, W, H, bg_c, char_c)

    # ELEMENTOS DE CENA (variam por cena)
    # Sol
    if cena_idx % 4 != 2:
        cor_sol = (255, 220, 50) if tema in ["cura","supera","amor","autoest"] else (255, 180, 40)
        desenhar_sol(draw, W, H, cor_sol, tamanho=int(W*0.038))

    # Nuvens
    if cena_idx % 3 != 1:
        desenhar_nuvens(draw, W, H)

    # Plantas
    if cena_idx % 2 == 0:
        cor_c = tuple(max(0, c-20) for c in char_c)
        cor_f = tuple(max(0, c+20) for c in char_c)
        desenhar_plantas(draw, W, H, cor_c, cor_f)

    # Elementos geometricos decorativos (estilo Kurzgesagt)
    for _ in range(8):
        ex = random.randint(0, W)
        ey = random.randint(int(H*0.05), int(H*0.65))
        er = random.randint(8, 30)
        ec = tuple(max(0, int(c*0.80 + random.randint(-20,20))) for c in bg_c)
        forma = random.randint(0, 2)
        if forma == 0:
            draw.ellipse([ex-er,ey-er,ex+er,ey+er], fill=ec)
        elif forma == 1:
            draw.rectangle([ex-er,ey-er,ex+er,ey+er], fill=ec)
        else:
            draw.polygon([(ex,ey-er),(ex-er,ey+er),(ex+er,ey+er)], fill=ec)

    # PERSONAGENS (1 ou 2 por cena)
    pele = TONS_PELE[cena_idx % len(TONS_PELE)]
    composicao = cena_idx % 7

    if composicao == 4 and total_cenas > 3:
        # DOIS PERSONAGENS (discussao, relacionamento)
        pele2 = TONS_PELE[(cena_idx+3) % len(TONS_PELE)]
        char2 = tuple(min(255, c+50) for c in char_c)
        acc2 = tuple(max(0, c-20) for c in acc_c)
        cx1 = int(W*0.33)
        cx2 = int(W*0.67)
        cy  = int(H*0.55)
        desenhar_personagem(draw, cx1, cy, pele, char_c, acc_c, cena_idx, "reflexivo")
        desenhar_personagem(draw, cx2, cy, pele2, char2, acc2, cena_idx+4, "surpreso")
    else:
        # UM PERSONAGEM — posicao varia
        posicoes_x = [int(W*0.5), int(W*0.38), int(W*0.62), int(W*0.30), int(W*0.70), int(W*0.5), int(W*0.45)]
        cx = posicoes_x[composicao]
        cy = int(H*0.54)
        expressoes = ["neutro","feliz","reflexivo","triste","neutro","feliz","reflexivo"]
        expr = expressoes[composicao]
        desenhar_personagem(draw, cx, cy, pele, char_c, acc_c, cena_idx, expr)
        # Balao de fala em algumas cenas
        desenhar_balao_fala(draw, cx, cy, acc_c, cena_idx)

    path = "/tmp/cena_flat_" + str(video_id) + "_" + str(cena_idx) + ".jpg"
    img.save(path, "JPEG", quality=94)
    return path

def gerar_prompt_flat(titulo, trecho, cena_idx, tema):
    """Prompt NVIDIA para estilo School of Life / Kurzgesagt"""
    pal = PALETAS.get(tema, PALETAS["padrao"])
    cor_desc = {
        "narcis":"warm coral red and cream background",
        "trauma":"soft lavender blue background",
        "ansio":"warm golden yellow background",
        "cura":"fresh green and white background",
        "amor":"warm pink and rose background",
        "autoest":"sky blue and white background",
        "padrao":"warm cream yellow background",
    }
    cd = cor_desc.get(tema, "warm colorful background")
    cenas_desc = [
        "person sitting thoughtfully at a table",
        "person standing and explaining gesturing",
        "two people having a conversation",
        "person walking through a colorful environment",
        "person reading a book in nature",
        "person looking at the horizon hopeful",
        "person helping another person",
    ]
    cd_cena = cenas_desc[cena_idx % len(cenas_desc)]
    return (
        "flat 2D vector illustration animation educational style, "
        + cd_cena + ", "
        + cd + ", warm sunlight, clear blue sky, "
        "simple geometric characters with expressive faces and visible eyes and smile, "
        "clean bold outlines, educational animation style like School of Life or Kurzgesagt, "
        "bright warm colorful palette, simple environment with trees and sun, "
        "friendly approachable illustration, "
        "NO TEXT NO WORDS NO LETTERS NO NUMBERS NO LOGOS NO WATERMARKS"
    )

def tentar_nvidia(prompt, video_id, cena_idx):
    if not NVIDIA_KEY: return None
    endpoints = [
        ("https://integrate.api.nvidia.com/v1/images/generations",
         {"model":"black-forest-labs/flux-schnell","prompt":prompt,
          "n":1,"size":"1344x768","response_format":"b64_json"}),
        ("https://ai.api.nvidia.com/v1/genai/black-forest-labs/flux-schnell",
         {"prompt":prompt,"width":1344,"height":768,"num_inference_steps":4,
          "guidance_scale":3.5,"num_images":1,"seed":random.randint(1,999999)}),
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
                with open(p,"wb") as f: f.write(base64.b64decode(b64))
                print("    NVIDIA OK: " + str(len(b64)//1024) + "KB")
                return p
        except Exception as e:
            print("    NVIDIA exc: " + str(e)[:80])
    return None

def upload_img(path, video_id, cena_idx):
    fname = "v4/flat_" + str(video_id) + "_" + str(cena_idx) + "_" + str(int(time.time())) + ".jpg"
    with open(path,"rb") as f: data = f.read()
    try:
        sb.storage.from_("videos").upload(fname, data,
            file_options={"content-type":"image/jpeg","x-upsert":"true"})
        return SB_URL + "/storage/v1/object/public/videos/" + fname
    except:
        r = requests.post(SB_URL+"/storage/v1/object/videos/"+fname,
            headers={"apikey":SB_KEY,"Authorization":"Bearer "+SB_KEY,
                     "Content-Type":"image/jpeg","x-upsert":"true"}, data=data)
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
    print("    tema=" + tema + " | " + str(len(cenas)) + " cenas flat 2D")
    urls = []
    for i, trecho in enumerate(cenas):
        print("    cena " + str(i+1) + "/" + str(len(cenas)) + "...")
        prompt = gerar_prompt_flat(title, trecho, i, tema)
        img = tentar_nvidia(prompt, vid_id, i)
        fonte = "nvidia"
        if not img:
            img = gerar_cena_flat(title, trecho, i, len(cenas), vid_id, dur)
            fonte = "pillow_flat"
        url = upload_img(img, vid_id, i)
        if url:
            urls.append(url)
            print("      cena " + str(i+1) + " (" + fonte + ") OK")
        time.sleep(0.3)
    if not urls: print("    sem imagens"); return False
    sb.table("content_pipeline").update({
        "status":"video_ready","mp4_url":None,
        "metadata":(v.get("metadata") or {}) | {
            "quantum_images":urls,"quantum_image":urls[0],
            "n_cenas":len(urls),"tema":tema,
            "render_method":"flat_2d_school_of_life_kurzgesagt_v4",
            "processado_em":int(time.time()),
        }
    }).eq("id",vid_id).execute()
    print("    video_ready " + str(len(urls)) + " cenas flat")
    return True

def main():
    print("=== RENDER FLAT V4 — School of Life + Kurzgesagt ===")
    print("Estilo: colorido, vibrante, personagens com rosto, cenas ricas")
    print("NVIDIA: " + ("OK" if NVIDIA_KEY else "ausente, Pillow flat fallback"))
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
