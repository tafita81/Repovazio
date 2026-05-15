#!/usr/bin/env python3
"""
render_quantum_v2.py — Cerebro V14.2 CORRIGIDO
REGRAS IMUTAVEIS: Long=15min | Short=50-58s | ZERO texto nas imagens | ZERO texto na tela
"""
import os, sys, json, time, requests, base64, random, math
from supabase import create_client
from PIL import Image, ImageDraw

SB_URL = os.environ["SUPABASE_URL"]
SB_KEY = os.environ["SUPABASE_KEY"]
sb = create_client(SB_URL, SB_KEY)

NVIDIA_KEY = os.environ.get("NVIDIA_API_KEY", "")
GROQ_KEY   = os.environ.get("GROQ_API_KEY", "")

REGRAS = {
    "long_target": 900, "long_min": 840, "long_max": 960,
    "short_target": 54, "short_min": 50, "short_max": 58,
    "gate_render": 90, "batch_size": 5,
}

# PALETAS POR EMOCAO (Psych2Go style — pastel 2D)
PALETAS = {
    "ansioso":       {"bg": (255, 243, 163), "char": (200, 180, 100), "accent": (230, 200, 50)},
    "melancolico":   {"bg": (176, 196, 222), "char": (100, 130, 170), "accent": (80, 100, 150)},
    "tenso":         {"bg": (255, 200, 180), "char": (210, 100, 80),  "accent": (180, 60, 40)},
    "urgente":       {"bg": (255, 220, 150), "char": (200, 140, 40),  "accent": (180, 100, 0)},
    "esperanca":     {"bg": (178, 216, 178), "char": (80, 160, 80),   "accent": (40, 120, 40)},
    "empatia":       {"bg": (255, 220, 200), "char": (200, 130, 90),  "accent": (160, 80, 50)},
    "contemplativo": {"bg": (232, 193, 232), "char": (160, 90, 160),  "accent": (120, 50, 120)},
    "calmo":         {"bg": (168, 216, 234), "char": (60, 140, 180),  "accent": (30, 100, 140)},
    "alivio":        {"bg": (200, 240, 200), "char": (60, 180, 60),   "accent": (20, 120, 20)},
}

PERSONAGENS_EN = [
    "Brazilian woman 25-30, medium brown skin, dark wavy hair",
    "Brazilian man 28-35, light olive skin, short dark hair",
    "Brazilian woman 35-45, Black skin, natural afro hair",
    "Brazilian young woman 20-25, tan skin, long straight hair",
    "Brazilian man 30-40, dark skin, friendly face",
]

SHOT_TYPES = [
    "extreme close-up face, filling entire frame, massive expressive eyes",
    "medium shot from waist up, centered, neutral background",
    "portrait shot head and shoulders, direct gaze at viewer",
    "close-up chest and head, 3/4 angle, expressive",
]

def detectar_emocao(titulo, script):
    t = (titulo + " " + script[:300]).lower()
    if any(x in t for x in ["ansio","panico","medo","abandono","apego"]): return "ansioso"
    if any(x in t for x in ["trauma","dor","ferida","abuso","negligencia"]): return "melancolico"
    if any(x in t for x in ["narcis","manipu","toxico","abusivo","gaslight"]): return "tenso"
    if any(x in t for x in ["burnout","esgota","cansa","depressao"]): return "urgente"
    if any(x in t for x in ["cura","supera","evolui","cresci","esperanca"]): return "esperanca"
    if any(x in t for x in ["limites","autoestima","valoriza","amor"]): return "empatia"
    return "contemplativo"

def gerar_prompt_quantico(titulo, script, emocao):
    personagem = random.choice(PERSONAGENS_EN)
    shot = random.choice(SHOT_TYPES)
    paleta_desc = {
        "ansioso": "pale yellow #FFF3A3 pastel", "melancolico": "dusty blue #B0C4DE pastel",
        "tenso": "warm coral red #FF8C6B pastel", "urgente": "amber #FFB347 pastel",
        "esperanca": "soft mint green #B2D8B2 pastel", "empatia": "warm peach #FFD1BD pastel",
        "contemplativo": "soft lavender #E8C1E8 pastel",
    }.get(emocao, "soft lavender #E8C1E8 pastel")
    expressoes = {
        "ansioso": "wide anxious eyes, worried expression",
        "melancolico": "sad thoughtful expression, downcast eyes",
        "tenso": "alert suspicious expression, narrowed eyes, tense jaw",
        "urgente": "urgent concerned expression, raised eyebrows, intense",
        "esperanca": "warm hopeful smile, soft gentle eyes",
        "empatia": "compassionate warm smile, kind eyes",
        "contemplativo": "thoughtful pensive expression, slightly tilted head",
    }
    expr = expressoes.get(emocao, "thoughtful expressive face")
    return (
        f"flat 2D vector art illustration, educational animation style, "
        f"{shot}, {personagem}, {expr}, "
        f"solid {paleta_desc} background, bold clean outlines, "
        f"Psych2Go style, single character centered, emotional educational, "
        f"NO text NO words NO letters NO numbers NO logos NO watermarks "
        f"NO brand marks ZERO text in image ZERO writing"
    )

def gerar_imagem_pillow(emocao, video_id):
    """Fallback: gera personagem Psych2Go-style com Pillow (ZERO dependencia externa)"""
    paleta = PALETAS.get(emocao, PALETAS["contemplativo"])
    bg = paleta["bg"]
    char_color = paleta["char"]
    accent = paleta["accent"]
    
    W, H = 1344, 768
    img = Image.new("RGB", (W, H), bg)
    draw = ImageDraw.Draw(img)
    
    # Gradiente suave no fundo
    for y in range(H):
        alpha = y / H
        r = int(bg[0] * (1 - alpha * 0.1))
        g = int(bg[1] * (1 - alpha * 0.1))
        b = int(bg[2] * (1 - alpha * 0.05))
        draw.line([(0, y), (W, y)], fill=(r, g, b))
    
    # Personagem humanóide SEM ROSTO (Psych2Go style)
    cx, cy = W // 2, H // 2
    
    # Corpo (torso)
    draw.ellipse([cx-70, cy-20, cx+70, cy+160], fill=char_color, outline=(*accent, 255), width=4)
    
    # Cabeça — círculo branco/pastel SEM ROSTO
    head_r = 90
    head_color = tuple(min(255, int(c * 1.3)) for c in char_color)
    draw.ellipse([cx-head_r, cy-head_r*2-20, cx+head_r, cy-20], 
                 fill=head_color, outline=(*accent, 255), width=4)
    
    # Cabelo estilizado
    hair_color = tuple(max(0, c-40) for c in char_color)
    draw.ellipse([cx-head_r+5, cy-head_r*2-30, cx+head_r-5, cy-head_r-10], 
                 fill=hair_color)
    draw.rectangle([cx-head_r+5, cy-head_r*2-15, cx+head_r-5, cy-head_r+10],
                   fill=hair_color)
    
    # Braços
    # Esquerdo
    draw.ellipse([cx-140, cy+30, cx-60, cy+120], fill=char_color, outline=(*accent,255), width=3)
    # Direito  
    draw.ellipse([cx+60, cy+30, cx+140, cy+120], fill=char_color, outline=(*accent,255), width=3)
    
    # Pernas (parte inferior)
    draw.ellipse([cx-60, cy+140, cx+10, cy+220], fill=char_color, outline=(*accent,255), width=3)
    draw.ellipse([cx-10, cy+140, cx+60, cy+220], fill=char_color, outline=(*accent,255), width=3)
    
    # Expressão por emoção — apenas elementos abstratos ACIMA da cabeça
    if emocao in ["ansioso", "urgente"]:
        # Linhas de tensão em volta da cabeça
        for angle in range(0, 360, 45):
            rad = math.radians(angle)
            x1 = cx + int(head_r * 1.1 * math.cos(rad))
            y1 = (cy - head_r - 20) + int(head_r * 1.1 * math.sin(rad))
            x2 = cx + int(head_r * 1.4 * math.cos(rad))
            y2 = (cy - head_r - 20) + int(head_r * 1.4 * math.sin(rad))
            draw.line([x1, y1, x2, y2], fill=accent, width=3)
    elif emocao in ["esperanca", "alivio"]:
        # Estrelinhas positivas
        for dx, dy in [(-head_r*1.5, -head_r*2.5), (head_r*1.5, -head_r*2.5), (0, -head_r*3)]:
            star_x, star_y = int(cx+dx), int(cy+dy)
            draw.ellipse([star_x-12, star_y-12, star_x+12, star_y+12], fill=accent)
    elif emocao in ["melancolico", "tenso"]:
        # Nuvem escura acima
        draw.ellipse([cx-60, cy-head_r*3-30, cx+60, cy-head_r*2-10], fill=accent)
    
    # Elementos decorativos no fundo
    for i in range(8):
        x = random.randint(50, W-50)
        y = random.randint(50, H-50)
        r = random.randint(5, 20)
        alpha_color = tuple(min(255, int(c * 0.7)) for c in accent)
        draw.ellipse([x-r, y-r, x+r, y+r], fill=alpha_color, width=0)
    
    # Sombra do personagem no chão
    draw.ellipse([cx-80, cy+215, cx+80, cy+240], fill=tuple(max(0,c-30) for c in bg))
    
    # Salvar
    path = f"/tmp/quantum_img_{video_id}.jpg"
    img.save(path, "JPEG", quality=92)
    return path

def gerar_imagem_nvidia(prompt, video_id):
    """Tenta NVIDIA API com debug completo"""
    if not NVIDIA_KEY:
        print(f"    ⚠ NVIDIA_KEY vazia")
        return None
    
    # Endpoint correto NVIDIA AI Foundation (2025)
    endpoints = [
        "https://ai.api.nvidia.com/v1/genai/black-forest-labs/flux-schnell",
        "https://integrate.api.nvidia.com/v1/images/generations",
    ]
    
    for endpoint in endpoints:
        try:
            if "genai" in endpoint:
                payload = {
                    "prompt": prompt,
                    "width": 1344, "height": 768,
                    "num_inference_steps": 4,
                    "guidance_scale": 3.5,  # CORRIGIDO: era 0.0
                    "num_images": 1,
                    "seed": random.randint(1, 999999)
                }
            else:
                payload = {
                    "model": "black-forest-labs/flux-schnell",
                    "prompt": prompt,
                    "n": 1, "size": "1344x768",
                    "response_format": "b64_json"
                }
            
            resp = requests.post(
                endpoint,
                headers={"Authorization": f"Bearer {NVIDIA_KEY}", "Content-Type": "application/json"},
                json=payload, timeout=90
            )
            
            print(f"    NVIDIA [{endpoint.split('/')[-2:]}] status={resp.status_code}")
            
            if resp.status_code != 200:
                print(f"    NVIDIA erro body: {resp.text[:300]}")
                continue
            
            data = resp.json()
            # Tentar extrair base64
            b64 = None
            if "artifacts" in data:
                b64 = data["artifacts"][0].get("base64", "")
            elif "data" in data:
                b64 = data["data"][0].get("b64_json", "")
            
            if b64:
                img_bytes = base64.b64decode(b64)
                path = f"/tmp/nvidia_img_{video_id}.jpg"
                with open(path, "wb") as f:
                    f.write(img_bytes)
                print(f"    ✅ NVIDIA ok: {len(img_bytes):,} bytes")
                return path
            else:
                print(f"    NVIDIA sem base64: {list(data.keys())}")
                
        except Exception as e:
            print(f"    NVIDIA exception: {e}")
    
    return None

def upload_imagem(path, video_id):
    """Faz upload da imagem para Supabase storage"""
    with open(path, "rb") as f:
        img_bytes = f.read()
    fname = f"v2/img_{video_id}_{int(time.time())}.jpg"
    try:
        sb.storage.from_("videos").upload(
            fname, img_bytes,
            file_options={"content-type": "image/jpeg", "x-upsert": "true"}
        )
        return f"{SB_URL}/storage/v1/object/public/videos/{fname}"
    except Exception as e:
        print(f"    Upload erro: {e}")
        return None

def get_videos_pendentes():
    r = sb.table("content_pipeline").select(
        "id,title,script,audio_url,metadata,score"
    ).eq("status", "mp4_ready").is_("mp4_url", None).order("pub_order").limit(REGRAS["batch_size"]).execute()
    return r.data or []

def processar_video(v):
    vid_id = v["id"]
    title  = v.get("title", "")
    script = v.get("script", "") or ""
    audio  = v.get("audio_url", "")
    
    print(f"\n  #{vid_id} {title[:55]}")
    
    if not audio:
        print(f"    ⚠ sem audio_url — pulando")
        return False
    
    emocao = detectar_emocao(title, script)
    print(f"    emoção: {emocao}")
    
    prompt = gerar_prompt_quantico(title, script, emocao)
    
    # 1. Tentar NVIDIA
    img_path = gerar_imagem_nvidia(prompt, vid_id)
    fonte = "nvidia_flux"
    
    # 2. Fallback: Pillow 2D Psych2Go style
    if not img_path:
        print(f"    → usando fallback Pillow (Psych2Go 2D style)")
        img_path = gerar_imagem_pillow(emocao, vid_id)
        fonte = "pillow_psych2go"
    
    # Upload
    img_url = upload_imagem(img_path, vid_id)
    if not img_url:
        print(f"    ⚠ upload falhou")
        return False
    
    print(f"    ✓ imagem ({fonte}): {img_url}")
    
    # Atualizar banco
    sb.table("content_pipeline").update({
        "status": "video_ready",
        "mp4_url": None,
        "metadata": (v.get("metadata") or {}) | {
            "quantum_image": img_url,
            "emocao": emocao,
            "render_method": f"flux_kenburns_{fonte}",
            "prompt_quantico": prompt[:200],
            "processado_em": int(time.time()),
            "cerebro_v14": True,
        }
    }).eq("id", vid_id).execute()
    print(f"    ✓ video_ready salvo")
    return True

def main():
    print("=== RENDER QUANTICO V2 — Cerebro V14.2 ===")
    print(f"NVIDIA_KEY: {'OK' if NVIDIA_KEY else 'AUSENTE'}")
    print(f"Regras: long={REGRAS['long_target']}s | short={REGRAS['short_target']}s")
    
    videos = get_videos_pendentes()
    print(f"Encontrados {len(videos)} vídeos para render")
    
    ok = 0
    for v in videos:
        try:
            if processar_video(v):
                ok += 1
            time.sleep(1)
        except Exception as e:
            print(f"  ERRO #{v.get('id')}: {e}")
    
    print(f"\nConcluido: {ok}/{len(videos)} vídeos processados")
    
    try:
        sb.table("cerebro_evolucao").insert({
            "versao": "v14.2",
            "tipo": "render_quantico",
            "descricao": f"Batch render V2 corrigido: {ok}/{len(videos)} ok",
            "mudancas": {"batch": ok, "total": len(videos)}
        }).execute()
    except: pass

if __name__ == "__main__":
    main()
