#!/usr/bin/env python3
"""
render_contextual_v5.py — Cerebro V5 — O PADRAO ETERNO
Inovacao central: CENAS CONTEXTUAIS — cada imagem reflete o que o texto diz
Estilos mesclados: School of Life (personagens expressivos) + profundidade cinematografica
Sem branding. Apenas conteudo visual que CONTA A HISTORIA.

Leonardo AI (gratuito, 150 geracoes/dia) com fallback Pillow contextual.
"""
import os, json, time, requests, base64, random, math
from PIL import Image, ImageDraw
import numpy as np
from supabase import create_client

SB_URL = os.environ["SUPABASE_URL"]
SB_KEY = os.environ["SUPABASE_KEY"]
sb = create_client(SB_URL, SB_KEY)
NVIDIA_KEY    = os.environ.get("NVIDIA_API_KEY","")
LEONARDO_KEY  = os.environ.get("LEONARDO_API_KEY","")

# SISTEMA CONTEXTUAL — detecta o tema de CADA paragrafo
# e gera uma cena visual que REPRESENTA aquele conteudo
CONTEXTOS = {
    # NARCISISMO / MANIPULACAO
    "narcis":    {"scene":"espelho",      "pal":"coral",    "emotion":"arrogan",  "n_chars":1},
    "manipu":    {"scene":"controle",     "pal":"dark_red", "emotion":"tense",    "n_chars":2},
    "gaslight":  {"scene":"confusao",     "pal":"dark_red", "emotion":"confused", "n_chars":2},
    "toxico":    {"scene":"afastamento",  "pal":"dark_red", "emotion":"sad",      "n_chars":2},
    # TRAUMA / ANSIEDADE
    "trauma":    {"scene":"solidao",      "pal":"dusty",    "emotion":"sad",      "n_chars":1},
    "ansio":     {"scene":"espiral",      "pal":"amber",    "emotion":"worried",  "n_chars":1},
    "panico":    {"scene":"espiral",      "pal":"amber",    "emotion":"worried",  "n_chars":1},
    "medo":      {"scene":"sombra",       "pal":"blue",     "emotion":"fear",     "n_chars":1},
    "depressao": {"scene":"solidao",      "pal":"blue",     "emotion":"sad",      "n_chars":1},
    # RELACIONAMENTOS
    "amor":      {"scene":"conexao",      "pal":"pink",     "emotion":"happy",    "n_chars":2},
    "relacao":   {"scene":"dois_juntos",  "pal":"peach",    "emotion":"neutral",  "n_chars":2},
    "abandono":  {"scene":"afastamento",  "pal":"blue",     "emotion":"sad",      "n_chars":2},
    "apego":     {"scene":"agarrado",     "pal":"amber",    "emotion":"worried",  "n_chars":2},
    # CURA / CRESCIMENTO
    "cura":      {"scene":"luz",          "pal":"green",    "emotion":"happy",    "n_chars":1},
    "supera":    {"scene":"vitoria",      "pal":"golden",   "emotion":"proud",    "n_chars":1},
    "esperanca": {"scene":"horizonte",    "pal":"golden",   "emotion":"hopeful",  "n_chars":1},
    "evolui":    {"scene":"crescimento",  "pal":"green",    "emotion":"happy",    "n_chars":1},
    # AUTOCONHECIMENTO
    "autoest":   {"scene":"confiante",    "pal":"golden",   "emotion":"proud",    "n_chars":1},
    "limite":    {"scene":"barreira",     "pal":"teal",     "emotion":"firm",     "n_chars":1},
    "solidao":   {"scene":"solidao",      "pal":"grey",     "emotion":"sad",      "n_chars":1},
    "reflexao":  {"scene":"reflexao",     "pal":"lavender", "emotion":"thinking", "n_chars":1},
    "padrao":    {"scene":"reflexao",     "pal":"warm",     "emotion":"neutral",  "n_chars":1},
}

# PALETAS para cada tipo de cena
PALETAS = {
    "coral":   {"bg":(255,235,215), "sky":(255,215,190), "char":(210,80,60),  "acc":(160,40,20)},
    "dark_red":{"bg":(255,225,220), "sky":(245,200,190), "char":(180,50,40),  "acc":(120,20,10)},
    "dusty":   {"bg":(225,225,240), "sky":(210,210,235), "char":(100,95,180), "acc":(60,55,130)},
    "amber":   {"bg":(255,248,220), "sky":(255,235,190), "char":(235,155,30), "acc":(175,95,0)},
    "blue":    {"bg":(220,232,250), "sky":(200,218,245), "char":(65,115,200), "acc":(30,65,150)},
    "pink":    {"bg":(255,228,235), "sky":(255,210,225), "char":(215,80,115), "acc":(160,30,65)},
    "peach":   {"bg":(255,238,225), "sky":(255,225,210), "char":(225,130,80), "acc":(170,70,20)},
    "green":   {"bg":(225,248,225), "sky":(210,240,210), "char":(55,168,60),  "acc":(20,108,25)},
    "golden":  {"bg":(255,248,215), "sky":(255,238,190), "char":(215,175,30), "acc":(160,115,0)},
    "teal":    {"bg":(220,245,243), "sky":(200,238,235), "char":(30,160,155), "acc":(10,110,105)},
    "grey":    {"bg":(235,235,242), "sky":(220,220,235), "char":(130,130,155),"acc":(80,80,110)},
    "lavender":{"bg":(240,232,255), "sky":(228,218,250), "char":(145,90,215), "acc":(90,40,160)},
    "warm":    {"bg":(255,245,222), "sky":(255,232,200), "char":(235,155,50), "acc":(175,90,0)},
}

TONS_PELE = [
    (255,218,185),(245,198,160),(225,175,130),(200,148,100),
    (175,115,75),(150,90,55),(120,70,40),(95,50,25),
]

def detectar_contexto(titulo, texto):
    """Detecta o contexto de CADA paragrafo para gerar cena correspondente"""
    t = (titulo + " " + texto).lower()
    for ctx in CONTEXTOS:
        if ctx in t:
            return CONTEXTOS[ctx], ctx
    return CONTEXTOS["padrao"], "padrao"

def dividir_cenas_com_contexto(titulo, script, dur_min):
    """Divide em cenas E detecta o contexto de cada uma"""
    paras = [p.strip() for p in script.split("\n") if p.strip()]
    if not paras: paras = [script]
    n = 5 if dur_min < 3 else min(14, max(7, len(paras)))
    chunk = max(1, len(paras)//n)
    cenas = []
    for i in range(0, len(paras), chunk):
        trecho = " ".join(paras[i:i+chunk])
        ctx, ctx_name = detectar_contexto(titulo, trecho)
        cenas.append({"texto": trecho, "ctx": ctx, "ctx_name": ctx_name})
        if len(cenas) >= n: break
    return cenas or [{"texto": script, "ctx": CONTEXTOS["padrao"], "ctx_name": "padrao"}]

# ════════════════════════════════════════════════════════
# GERADORES DE CENAS CONTEXTUAIS (Pillow)
# Cada funcao gera uma cena que VISUALMENTE representa o contexto
# ════════════════════════════════════════════════════════

def cor_segura(c):
    return tuple(max(0, min(255, v)) for v in c)

def fundo_gradiente(W, H, sky_c, bg_c, chao_c):
    arr = np.zeros((H, W, 3), dtype=np.uint8)
    for y in range(H):
        t = min(1.0, y/H)
        for c in range(3):
            arr[y,:,c] = int(min(255, max(0, sky_c[c]*(1-t*0.25) + bg_c[c]*t)))
    img = Image.fromarray(arr, "RGB")
    draw = ImageDraw.Draw(img)
    draw.rectangle([0, int(H*0.75), W, H], fill=cor_segura(chao_c))
    return img, draw

def desenhar_cabeca_com_rosto(draw, cx, cy, r, pele, emocao):
    """Cabeca com expressao emocional clara"""
    cabelo_c = cor_segura(tuple(max(0,c-60) for c in pele))
    draw.ellipse([cx-r-6, cy-r-14, cx+r+6, cy+r//3], fill=cabelo_c)
    draw.ellipse([cx-r, cy-r, cx+r, cy+r], fill=pele)
    ey = cy - r//5
    # Olhos
    draw.ellipse([cx-r//2-2, ey-r//5, cx-r//6, ey+r//5], fill=(30,25,25))
    draw.ellipse([cx+r//6, ey-r//5, cx+r//2+2, ey+r//5], fill=(30,25,25))
    draw.ellipse([cx-r//2+2, ey-r//5+2, cx-r//6-2, ey-r//5+6], fill=(245,245,245))
    draw.ellipse([cx+r//6+2, ey-r//5+2, cx+r//2-2, ey-r//5+6], fill=(245,245,245))
    # Boca / sobrancelhas por emocao
    if emocao in ["happy","hopeful","proud"]:
        draw.arc([cx-r//3, ey+r//4, cx+r//3, ey+r//2], 0, 180, fill=(50,25,15), width=3)
        draw.arc([cx-r//2, ey-r//3, cx-r//6, ey-r//7], 180, 360, fill=(50,25,15), width=2)
        draw.arc([cx+r//6, ey-r//3, cx+r//2, ey-r//7], 180, 360, fill=(50,25,15), width=2)
    elif emocao in ["sad","fear"]:
        draw.arc([cx-r//3, ey+r//4+4, cx+r//3, ey+r//2+4], 180, 360, fill=(50,25,15), width=3)
        draw.line([cx-r//2, ey-r//5-2, cx-r//6, ey-r//5+4], fill=(50,25,15), width=2)
        draw.line([cx+r//6, ey-r//5+4, cx+r//2, ey-r//5-2], fill=(50,25,15), width=2)
    elif emocao in ["worried","confused"]:
        draw.ellipse([cx-r//6, ey+r//4, cx+r//6, ey+r//2], fill=(50,25,15))
        draw.arc([cx-r//2, ey-r//4, cx-r//8, ey-r//9], 0, 180, fill=(50,25,15), width=2)
        draw.arc([cx+r//8, ey-r//4, cx+r//2, ey-r//9], 0, 180, fill=(50,25,15), width=2)
    elif emocao == "tense":
        draw.line([cx-r//3, ey+r//3+2, cx+r//3, ey+r//3+2], fill=(50,25,15), width=3)
        draw.line([cx-r//2, ey-r//4+2, cx-r//8, ey-r//8], fill=(50,25,15), width=2)
        draw.line([cx+r//8, ey-r//8, cx+r//2, ey-r//4+2], fill=(50,25,15), width=2)
    elif emocao == "thinking":
        draw.line([cx-r//3, ey+r//3+2, cx+r//4, ey+r//3+2], fill=(50,25,15), width=3)
        draw.line([cx-r//2, ey-r//6, cx-r//8, ey-r//6], fill=(50,25,15), width=2)
        draw.line([cx+r//8, ey-r//6, cx+r//2, ey-r//6], fill=(50,25,15), width=2)
    elif emocao in ["firm","arrogan"]:
        draw.line([cx-r//3, ey+r//3+2, cx+r//3, ey+r//3+2], fill=(50,25,15), width=3)
        draw.line([cx-r//2, ey-r//8, cx-r//8, ey-r//5], fill=(50,25,15), width=2)
        draw.line([cx+r//8, ey-r//5, cx+r//2, ey-r//8], fill=(50,25,15), width=2)
    else:
        draw.line([cx-r//4, ey+r//3+2, cx+r//4, ey+r//3+2], fill=(50,25,15), width=3)

def desenhar_corpo(draw, cx, cy_corpo, largura, altura, char_c, pele, pose="neutro"):
    """Corpo com pose contextual"""
    w = largura; h = altura
    pele_esc = cor_segura(tuple(max(0,c-30) for c in pele))
    sapato_c = cor_segura(tuple(max(0,c-50) for c in char_c))
    # Sapatos
    draw.ellipse([cx-w//2-8, cy_corpo+h-15, cx-4, cy_corpo+h+12], fill=sapato_c)
    draw.ellipse([cx+4, cy_corpo+h-15, cx+w//2+8, cy_corpo+h+12], fill=sapato_c)
    # Pernas
    draw.rounded_rectangle([cx-w//2+2, cy_corpo+h//2, cx-4, cy_corpo+h], radius=w//5, fill=pele_esc)
    draw.rounded_rectangle([cx+4, cy_corpo+h//2, cx+w//2-2, cy_corpo+h], radius=w//5, fill=pele_esc)
    # Corpo (camisa)
    draw.rounded_rectangle([cx-w//2, cy_corpo, cx+w//2, cy_corpo+h//2+10], radius=w//4, fill=char_c)
    # Pescoco
    draw.rounded_rectangle([cx-w//8, cy_corpo-w//4, cx+w//8, cy_corpo+4], radius=w//8, fill=pele)
    # Bracos por pose
    if pose == "abertos":
        draw.rounded_rectangle([cx-w-4, cy_corpo+6, cx-w//2, cy_corpo+h//3], radius=w//6, fill=pele)
        draw.rounded_rectangle([cx+w//2, cy_corpo+6, cx+w+4, cy_corpo+h//3], radius=w//6, fill=pele)
    elif pose == "cruzados":
        draw.rounded_rectangle([cx-w//2-2, cy_corpo+h//6, cx+4, cy_corpo+h//3+4], radius=w//8, fill=pele)
        draw.rounded_rectangle([cx-4, cy_corpo+h//5, cx+w//2+2, cy_corpo+h//3+8], radius=w//8, fill=pele)
    elif pose == "mao_cima":
        draw.rounded_rectangle([cx-w-4, cy_corpo-h//4, cx-w//2, cy_corpo+h//5], radius=w//6, fill=pele)
        draw.rounded_rectangle([cx+w//2, cy_corpo+6, cx+w+4, cy_corpo+h//3], radius=w//6, fill=pele)
    elif pose == "parado":
        draw.rounded_rectangle([cx-w//2, cy_corpo+h//8, cx-w//2+w//3, cy_corpo+h//3+5], radius=w//8, fill=pele)
        draw.rounded_rectangle([cx-w//5, cy_corpo+h//8, cx+w//2, cy_corpo+h//3+5], radius=w//8, fill=pele)
    else:  # neutro
        draw.rounded_rectangle([cx-w-2, cy_corpo+8, cx-w//2, cy_corpo+h//2+5], radius=w//6, fill=pele)
        draw.rounded_rectangle([cx+w//2, cy_corpo+8, cx+w+2, cy_corpo+h//2+5], radius=w//6, fill=pele)

def personagem_completo(draw, cx, cy_base, escala, pele, char_c, emocao, pose="neutro"):
    """Personagem completo posicionado em cy_base (pos Y dos pes)"""
    r = int(38*escala); h_corpo = int(120*escala); w_corpo = int(80*escala)
    cy_cabeca = cy_base - h_corpo - r*2 - 12
    cy_corpo  = cy_base - h_corpo - 8
    desenhar_corpo(draw, cx, cy_corpo, w_corpo, h_corpo, char_c, pele, pose)
    desenhar_cabeca_com_rosto(draw, cx, cy_cabeca, r, pele, emocao)

def elementos_decorativos(draw, W, H, sky_c, bg_c, cena_type):
    """Elementos visuais que REFORÇAM o contexto da cena"""
    if cena_type == "espiral":
        # Linhas em espiral ao redor (ansiedade)
        for i in range(0, 300, 20):
            rad = math.radians(i); r = 80 + i*0.6
            x = int(W*0.75 + r*math.cos(rad)); y = int(H*0.35 + r*math.sin(rad))
            if 0<x<W and 0<y<H*0.7:
                cr = tuple(min(255, max(0, c+30)) for c in sky_c)
                draw.ellipse([x-5,y-5,x+5,y+5], fill=cr)
    elif cena_type == "espelho":
        # Retangulo espelho a esquerda
        mx = int(W*0.22); my1 = int(H*0.2); my2 = int(H*0.8)
        mw = int(W*0.08)
        cl = cor_segura(tuple(min(255, c+40) for c in sky_c))
        draw.rounded_rectangle([mx-mw, my1, mx+mw, my2], radius=15, fill=cl, outline=(200,200,215), width=3)
        draw.rounded_rectangle([mx-mw//2, my1+8, mx+mw//2, my2-8], radius=10, fill=(230,240,255))
    elif cena_type == "luz":
        # Raios de luz saindo de cima
        lx, ly = int(W*0.55), int(H*0.05)
        for ang in range(-30, 31, 10):
            rad = math.radians(90-ang)
            x2 = int(lx + 350*math.cos(rad)); y2 = int(ly + 350*math.sin(rad))
            cl = cor_segura(tuple(min(255, c+50) for c in sky_c))
            draw.line([lx,ly,x2,y2], fill=cl, width=max(2, int(8-abs(ang)//10)))
    elif cena_type in ["vitoria","crescimento"]:
        # Estrelas / brilhos
        for _ in range(12):
            sx = random.randint(int(W*0.3), W-20); sy = random.randint(10, int(H*0.5))
            sr = random.randint(4,10)
            cl = cor_segura(tuple(min(255, c+60) for c in sky_c))
            draw.ellipse([sx-sr, sy-sr, sx+sr, sy+sr], fill=cl)
            draw.line([sx-sr*2,sy, sx+sr*2,sy], fill=cl, width=2)
            draw.line([sx,sy-sr*2, sx,sy+sr*2], fill=cl, width=2)
    elif cena_type == "sombra":
        # Sombra escura agressiva
        for i in range(0, 80, 8):
            cl = cor_segura(tuple(max(0, c-20-i//2) for c in bg_c))
            draw.ellipse([int(W*0.65)-i, int(H*0.2)-i//2, int(W*0.85)+i, int(H*0.75)+i//2], fill=cl)
    elif cena_type in ["conexao","dois_juntos"]:
        # Linhas de conexao entre personagens
        cx1, cx2 = int(W*0.33), int(W*0.67)
        cy = int(H*0.48)
        cl = cor_segura(tuple(min(255, c+40) for c in sky_c))
        for dy in range(-20, 21, 10):
            draw.line([cx1+60, cy+dy, cx2-60, cy+dy], fill=cl, width=2)
    elif cena_type == "afastamento":
        # Linha divisoria entre os dois
        lx = W//2; cl = cor_segura(tuple(max(0, c-15) for c in bg_c))
        draw.rectangle([lx-3, int(H*0.1), lx+3, int(H*0.8)], fill=cl)
    # Sol ou lua
    if cena_type not in ["sombra","solidao"]:
        sx, sy = int(W*0.88), int(H*0.10)
        sr = int(W*0.04)
        cl = cor_segura(tuple(min(255, c+30) for c in sky_c))
        for ang in range(0,360,30):
            rad=math.radians(ang)
            draw.line([sx+int((sr+5)*math.cos(rad)), sy+int((sr+5)*math.sin(rad)),
                       sx+int((sr+16)*math.cos(rad)), sy+int((sr+16)*math.sin(rad))],
                      fill=(255,215,40), width=3)
        draw.ellipse([sx-sr,sy-sr,sx+sr,sy+sr], fill=(255,220,50))
    # Nuvens
    if cena_type not in ["espiral","sombra"]:
        for cx2,cy2 in [(int(W*0.2),int(H*0.10)),(int(W*0.55),int(H*0.06))]:
            r=int(W*0.025); cl=(255,255,255)
            draw.ellipse([cx2-r,cy2-r,cx2+r,cy2+r], fill=cl)
            draw.ellipse([cx2-r+r,cy2-r+r//2,cx2+r+r,cy2+r+r//2], fill=cl)
            draw.ellipse([cx2+r//3,cy2-r-r//3,cx2+r+r//2,cy2+r//3], fill=cl)

def gerar_cena_contextual(titulo, texto, cena_info, video_id, cena_idx, dur_min):
    """
    Gera cena que REPRESENTA VISUALMENTE o conteudo do texto.
    O espectador ve o que o narrador esta dizendo.
    """
    is_short = dur_min < 3
    W, H = (1080, 1920) if is_short else (1920, 1080)
    random.seed(cena_idx*31 + video_id*7)
    np.random.seed(cena_idx*13 + video_id)

    ctx = cena_info["ctx"]
    cena_type = ctx["scene"]
    pal_name  = ctx["pal"]
    emocao    = ctx["emotion"]
    n_chars   = ctx["n_chars"]
    pal = PALETAS.get(pal_name, PALETAS["warm"])

    chao_c = cor_segura(tuple(max(0, int(c*0.88)) for c in pal["bg"]))
    img, draw = fundo_gradiente(W, H, pal["sky"], pal["bg"], chao_c)

    # Elementos decorativos contextuais
    elementos_decorativos(draw, W, H, pal["sky"], pal["bg"], cena_type)

    # Personagens
    pele1 = TONS_PELE[cena_idx % len(TONS_PELE)]
    esc   = 1.0 if not is_short else 0.95
    cy_base = int(H * 0.78)

    POSES_POR_CENA = {
        "espelho":     "cruzados",
        "espiral":     "neutro",
        "luz":         "abertos",
        "vitoria":     "mao_cima",
        "crescimento": "mao_cima",
        "confiante":   "abertos",
        "barreira":    "parado",
        "solidao":     "neutro",
        "reflexao":    "cruzados",
        "controle":    "cruzados",
        "afastamento": "cruzados",
        "conexao":     "abertos",
        "dois_juntos": "neutro",
        "sombra":      "neutro",
        "confusao":    "neutro",
        "horizonte":   "abertos",
        "agarrado":    "cruzados",
    }
    pose = POSES_POR_CENA.get(cena_type, "neutro")

    if n_chars == 2 and cena_type in ["controle","afastamento","conexao","dois_juntos","confusao","agarrado"]:
        pele2 = TONS_PELE[(cena_idx+3) % len(TONS_PELE)]
        char2 = cor_segura(tuple(min(255, c+40) for c in pal["char"]))
        emocao2 = {"controle":"tense","afastamento":"sad","conexao":"happy",
                   "dois_juntos":"neutral","confusao":"confused","agarrado":"worried"}.get(cena_type, emocao)
        if is_short:
            personagem_completo(draw, int(W*0.33), cy_base, esc*0.88, pele1, pal["char"], emocao, pose)
            personagem_completo(draw, int(W*0.67), cy_base, esc*0.88, pele2, char2, emocao2, pose)
        else:
            personagem_completo(draw, int(W*0.33), cy_base, esc, pele1, pal["char"], emocao, pose)
            personagem_completo(draw, int(W*0.67), cy_base, esc, pele2, char2, emocao2, pose)
    else:
        if is_short:
            personagem_completo(draw, W//2, cy_base, esc, pele1, pal["char"], emocao, pose)
        else:
            posicoes = [int(W*0.42), int(W*0.32), int(W*0.62), int(W*0.50)]
            cx = posicoes[cena_idx % len(posicoes)]
            personagem_completo(draw, cx, cy_base, esc, pele1, pal["char"], emocao, pose)

    path = "/tmp/ctx_" + str(video_id) + "_" + str(cena_idx) + ".jpg"
    img.save(path, "JPEG", quality=94)
    return path

def gerar_prompt_leonardo(titulo, texto, cena_info, cena_idx):
    """Prompt para Leonardo AI — estilo School of Life + profundidade"""
    ctx = cena_info["ctx"]
    scene_descs = {
        "espelho":     "person looking at their reflection in a tall mirror",
        "espiral":     "person surrounded by swirling circles and question marks",
        "luz":         "person bathed in warm golden light arms open",
        "vitoria":     "person celebrating arms raised triumphant",
        "solidao":     "lone person small figure in vast empty space",
        "reflexao":    "person sitting alone head bowed in thought",
        "controle":    "two people one pulling strings controlling other",
        "afastamento": "two people walking away from each other",
        "conexao":     "two people close together warm connection",
        "sombra":      "person with dark shadow behind them",
        "confiante":   "confident person standing tall open posture",
        "barreira":    "person with hand raised stop gesture firm",
        "confusao":    "confused person with question marks around head",
        "crescimento": "person growing taller with plants and stars",
        "horizonte":   "person looking at golden horizon hopeful",
    }
    scene = scene_descs.get(ctx["scene"], "person in thoughtful emotional scene")
    paletas = {
        "coral":"warm coral peach background","dark_red":"warm red background",
        "dusty":"soft lavender blue background","amber":"golden amber warm background",
        "blue":"sky blue calming background","pink":"soft rose pink background",
        "peach":"warm peach background","green":"fresh mint green background",
        "golden":"golden yellow bright background","teal":"teal calm background",
        "grey":"muted grey lavender background","lavender":"soft purple background",
        "warm":"warm cream yellow background",
    }
    pal_desc = paletas.get(ctx["pal"], "warm colorful background")
    return (
        "flat 2D vector art illustration educational style, medium shot, "
        + scene + ", "
        + pal_desc + ", "
        "simple geometric character with expressive face clear eyes and visible emotion, "
        "School of Life animation style, clean bold outlines, bright warm colors, "
        "sun and simple environment, friendly approachable educational psychology content, "
        "high quality flat illustration NO TEXT NO WORDS NO LETTERS NO LOGOS"
    )

def tentar_leonardo(prompt, video_id, cena_idx):
    """Leonardo AI — 150 geracoes gratis por dia"""
    if not LEONARDO_KEY: return None
    try:
        # Passo 1: criar geracao
        r = requests.post("https://cloud.leonardo.ai/api/rest/v1/generations",
            headers={"Authorization":"Bearer "+LEONARDO_KEY,"Content-Type":"application/json"},
            json={
                "prompt": prompt,
                "modelId": "b24e16ff-06e3-43eb-8d33-4416c2d75876",  # Leonardo Diffusion XL
                "width": 1344, "height": 768,
                "num_images": 1, "presetStyle": "ILLUSTRATION",
                "guidance_scale": 7, "num_inference_steps": 15,
                "photoReal": False, "alchemy": False,
            }, timeout=60)
        print("    Leonardo: " + str(r.status_code))
        if r.status_code not in [200,201]:
            try: print("      " + str(r.json())[:150])
            except: print("      " + r.text[:150])
            return None
        gen_id = r.json().get("sdGenerationJob",{}).get("generationId","")
        if not gen_id: return None
        # Passo 2: aguardar resultado
        for _ in range(20):
            time.sleep(3)
            r2 = requests.get("https://cloud.leonardo.ai/api/rest/v1/generations/"+gen_id,
                headers={"Authorization":"Bearer "+LEONARDO_KEY}, timeout=30)
            if r2.status_code == 200:
                imgs = r2.json().get("generations_by_pk",{}).get("generated_images",[])
                if imgs and imgs[0].get("status") in ["COMPLETE", None]:
                    img_url = imgs[0].get("url","")
                    if img_url:
                        r3 = requests.get(img_url, timeout=30)
                        if r3.status_code == 200:
                            p = "/tmp/leo_" + str(video_id) + "_" + str(cena_idx) + ".jpg"
                            with open(p,"wb") as f: f.write(r3.content)
                            print("    Leonardo OK: " + str(os.path.getsize(p)//1024) + "KB")
                            return p
    except Exception as e:
        print("    Leonardo exc: " + str(e)[:80])
    return None

def tentar_nvidia(prompt, video_id, cena_idx):
    if not NVIDIA_KEY: return None
    try:
        r = requests.post("https://integrate.api.nvidia.com/v1/images/generations",
            headers={"Authorization":"Bearer "+NVIDIA_KEY,"Content-Type":"application/json"},
            json={"model":"black-forest-labs/flux-schnell","prompt":prompt,
                  "n":1,"size":"1344x768","response_format":"b64_json"}, timeout=90)
        print("    NVIDIA: " + str(r.status_code))
        if r.status_code == 200:
            b64 = r.json().get("data",[{}])[0].get("b64_json","")
            if b64:
                p = "/tmp/nv_" + str(video_id) + "_" + str(cena_idx) + ".jpg"
                with open(p,"wb") as f: f.write(base64.b64decode(b64))
                return p
    except Exception as e:
        print("    NVIDIA exc: " + str(e)[:60])
    return None

def upload_img(path, video_id, cena_idx):
    fname = "v5/ctx_" + str(video_id) + "_" + str(cena_idx) + "_" + str(int(time.time())) + ".jpg"
    with open(path,"rb") as f: data = f.read()
    try:
        sb.storage.from_("videos").upload(fname, data, file_options={"content-type":"image/jpeg","x-upsert":"true"})
        return SB_URL+"/storage/v1/object/public/videos/"+fname
    except:
        r = requests.post(SB_URL+"/storage/v1/object/videos/"+fname,
            headers={"apikey":SB_KEY,"Authorization":"Bearer "+SB_KEY,"Content-Type":"image/jpeg","x-upsert":"true"}, data=data)
        if r.status_code in [200,201]: return SB_URL+"/storage/v1/object/public/videos/"+fname
    return None

def get_pendentes():
    r = sb.table("content_pipeline").select(
        "id,title,script,audio_url,metadata,duracao_min,pub_order"
    ).eq("status","mp4_ready").is_("mp4_url",None).order("pub_order").limit(5).execute()
    return r.data or []

def processar(v):
    vid_id = v["id"]; title = v.get("title","")
    script = v.get("script","") or ""; dur = float(v.get("duracao_min") or 0.9)
    print("\n  #" + str(vid_id) + " " + title[:55])
    cenas = dividir_cenas_com_contexto(title, script, dur)
    print("    " + str(len(cenas)) + " cenas contextuais")
    ctx_summary = " | ".join(c["ctx_name"] for c in cenas[:5])
    print("    Contextos: " + ctx_summary)
    urls = []
    for i, cena_info in enumerate(cenas):
        print("    cena " + str(i+1) + "/" + str(len(cenas)) + " (" + cena_info["ctx_name"] + ")...")
        prompt = gerar_prompt_leonardo(title, cena_info["texto"], cena_info, i)
        img = tentar_leonardo(prompt, vid_id, i); fonte = "leonardo"
        if not img: img = tentar_nvidia(prompt, vid_id, i); fonte = "nvidia"
        if not img: img = gerar_cena_contextual(title, cena_info["texto"], cena_info, vid_id, i, dur); fonte = "pillow"
        url = upload_img(img, vid_id, i)
        if url:
            urls.append(url)
            print("      cena " + str(i+1) + " (" + fonte + ") OK")
        time.sleep(0.3)
    if not urls: return False
    ctx_names = [c["ctx_name"] for c in cenas]
    sb.table("content_pipeline").update({
        "status":"video_ready","mp4_url":None,
        "metadata":(v.get("metadata") or {})|{
            "quantum_images":urls,"quantum_image":urls[0],
            "n_cenas":len(urls),"contextos":ctx_names,
            "render_method":"contextual_v5_padrao_eterno",
            "processado_em":int(time.time()),
        }
    }).eq("id",vid_id).execute()
    print("    video_ready " + str(len(urls)) + " cenas contextual")
    return True

def main():
    print("=== RENDER CONTEXTUAL V5 — O PADRAO ETERNO ===")
    print("Cenas refletem o TEXTO | School of Life + profundidade")
    print("Leonardo: "+("OK" if LEONARDO_KEY else "ausente")+" | NVIDIA: "+("OK" if NVIDIA_KEY else "ausente"))
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
