#!/usr/bin/env python3
"""
youtube_live_24_7.py
Stream contínuo 24/7 de psicologia para YouTube
Pipeline: Groq gera texto → Pollinations gera imagem → FFmpeg → RTMP YouTube

Identidade: Daniela Coelho · Pesquisa e Conteúdo em Psicologia
SEM título profissional até jan/2027
"""
import os, time, subprocess, pathlib, requests, textwrap, json
from datetime import datetime

STREAM_KEY  = os.getenv("YOUTUBE_STREAM_KEY", "")
GROQ_KEY    = os.getenv("GROQ_API_KEY", "")
RTMP_URL    = f"rtmp://a.rtmp.youtube.com/live2/{STREAM_KEY}"
TMP         = pathlib.Path("/tmp/live")
TMP.mkdir(exist_ok=True)

TEMAS = [
    "narcisismo encoberto em relacionamentos",
    "apego ansioso e como identificar",
    "neurociência da ansiedade: o que acontece no cérebro",
    "síndrome do impostor em pessoas competentes",
    "burnout vs cansaço: diferenças reais",
    "gaslighting: sinais que você está sendo manipulado",
    "fronteiras emocionais saudáveis",
    "vício em validação e aprovação",
    "perfeccionismo como forma de ansiedade",
    "depressão silenciosa: quando você funciona mas não está bem",
    "trauma de desenvolvimento na infância",
    "solidão epidêmica: por que nos sentimos sozinhos",
    "autocompaixão baseada em ciência",
    "raiva: o que fazer com ela",
    "procrastinação como regulação emocional",
    "por que é difícil fazer amigos na vida adulta",
    "amor próprio vs autoindulgência",
    "críticas e por que doem tanto",
]

FRASES_FIXAS = [
    "O cérebro não distingue rejeição social de ameaça física.",
    "Padrões aprendidos podem ser desaprendidos.",
    "Nomeie a emoção antes de agir — reduz a intensidade.",
    "Autocompaixão não é fraqueza. É neurociência.",
    "Feito é melhor que perfeito. Sempre.",
    "Sua história não é seu diagnóstico.",
    "Regulação emocional é habilidade, não caráter.",
    "O corpo guarda as marcas. Mas o corpo também cura.",
]

def gerar_insight(tema):
    """Gera insight de psicologia via Groq"""
    if not GROQ_KEY:
        return f"Psicologia baseada em evidências: {tema}. Daniela Coelho · Pesquisa e Conteúdo em Psicologia"
    
    try:
        r = requests.post("https://api.groq.com/openai/v1/chat/completions",
            headers={"Authorization": f"Bearer {GROQ_KEY}", "Content-Type": "application/json"},
            json={"model": "llama-3.3-70b-versatile",
                  "messages": [{"role": "user", "content":
                    f"Escreva UMA frase poderosa e baseada em ciência sobre: {tema}.\n"
                    f"Máximo 120 caracteres. Sem aspas. Sem hashtags.\n"
                    f"Cite um pesquisador real (ex: van der Kolk, Gross, Neff, Ainsworth).\n"
                    f"Tom: revelador, não óbvio."}],
                  "max_tokens": 80, "temperature": 0.8},
            timeout=15)
        if r.status_code == 200:
            return r.json()["choices"][0]["message"]["content"].strip()
    except: pass
    return FRASES_FIXAS[hash(tema) % len(FRASES_FIXAS)]

def gerar_imagem(tema, seed):
    """Gera imagem via Pollinations FLUX"""
    prompt = (f"masterpiece, best quality, kawaii chibi anime illustration, "
              f"peaceful psychology concept about {tema}, soft purple tones, "
              f"minimalist background ### lowres, bad anatomy, text, watermark, nsfw, blurry")
    url = f"https://image.pollinations.ai/prompt/{requests.utils.quote(prompt[:400])}"
    url += f"?model=flux&width=1280&height=720&seed={seed}&nologo=true"
    try:
        r = requests.get(url, timeout=45)
        if r.status_code == 200 and len(r.content) > 10000:
            return r.content
    except: pass
    return None

def criar_slide_ffmpeg(img_path, texto, duracao=30):
    """Cria clip com texto overlay via FFmpeg"""
    out = TMP / f"slide_{int(time.time())}.mp4"
    
    # Quebrar texto em linhas
    linhas = textwrap.wrap(texto, width=45)
    texto_formatado = "\n".join(linhas[:3])
    
    # Overlay: texto + marca
    marca = "Daniela Coelho · Pesquisa e Conteúdo em Psicologia"
    
    vf = (
        f"scale=1280:720,"
        f"drawbox=y=ih-90:color=black@0.7:width=iw:height=90:t=fill,"
        f"drawtext=text='{texto_formatado}':fontsize=28:fontcolor=white:"
        f"x=(w-text_w)/2:y=(h-text_h)/2-20:shadowcolor=black:shadowx=2:shadowy=2,"
        f"drawtext=text='{marca}':fontsize=16:fontcolor=#C4B5FD:"
        f"x=(w-text_w)/2:y=h-55"
    )
    
    cmd = [
        "ffmpeg", "-y",
        "-loop", "1", "-i", str(img_path),
        "-vf", vf,
        "-t", str(duracao),
        "-c:v", "libx264", "-preset", "fast",
        "-pix_fmt", "yuv420p",
        "-r", "30",
        "-an",  # sem áudio por enquanto
        str(out)
    ]
    
    result = subprocess.run(cmd, capture_output=True, timeout=120)
    return out if out.exists() and out.stat().st_size > 10000 else None

def stream_loop():
    """Loop principal da live"""
    if not STREAM_KEY:
        print("YOUTUBE_STREAM_KEY não configurado.")
        print("YouTube Studio → Go Live → Stream Key")
        print("GitHub: tafita81/Repovazio → Settings → Secrets → YOUTUBE_STREAM_KEY")
        return
    
    print(f"=== YOUTUBE LIVE 24/7 ===")
    print(f"Daniela Coelho · Pesquisa e Conteúdo em Psicologia")
    print(f"Iniciando: {datetime.now():%Y-%m-%d %H:%M}")
    print()
    
    idx = 0
    concat_list = TMP / "playlist.txt"
    slides = []
    
    # Pré-gerar alguns slides
    print("Gerando slides iniciais...")
    for i in range(3):
        tema = TEMAS[i % len(TEMAS)]
        seed = 9001 + i * 77
        
        print(f"  Slide {i+1}/3: {tema[:40]}")
        insight = gerar_insight(tema)
        img_data = gerar_imagem(tema, seed)
        
        if img_data:
            img_path = TMP / f"img_{seed}.jpg"
            img_path.write_bytes(img_data)
            
            slide = criar_slide_ffmpeg(img_path, insight, duracao=30)
            if slide:
                slides.append(slide)
                print(f"    ✅ {slide.name}")
        
        time.sleep(3)
    
    if not slides:
        print("Nenhum slide gerado. Verifique conexão.")
        return
    
    # Escrever playlist
    with open(concat_list, "w") as f:
        for s in slides:
            f.write(f"file '{s.resolve()}'\n")
    
    print(f"\nIniciando stream para YouTube ({len(slides)} slides)...")
    
    # FFmpeg → RTMP YouTube
    cmd_stream = [
        "ffmpeg", "-y",
        "-f", "concat", "-safe", "0", "-stream_loop", "-1",
        "-i", str(concat_list),
        # Áudio silencioso (necessário para YouTube Live)
        "-f", "lavfi", "-i", "anullsrc=channel_layout=stereo:sample_rate=44100",
        "-c:v", "libx264", "-preset", "veryfast",
        "-b:v", "2500k", "-maxrate", "2500k", "-bufsize", "5000k",
        "-pix_fmt", "yuv420p", "-g", "60",
        "-c:a", "aac", "-b:a", "128k", "-ar", "44100",
        "-shortest",
        "-f", "flv", RTMP_URL
    ]
    
    print("Stream iniciado! Verificar em YouTube Studio → Go Live")
    print(f"URL: {RTMP_URL[:50]}...")
    
    # Rodar stream e gerar novos slides em paralelo
    proc = subprocess.Popen(cmd_stream)
    
    slide_idx = 3
    while proc.poll() is None:
        time.sleep(25)  # Gerar próximo slide antes do atual acabar
        
        tema = TEMAS[slide_idx % len(TEMAS)]
        seed = 9001 + slide_idx * 77
        
        insight = gerar_insight(tema)
        img_data = gerar_imagem(tema, seed)
        
        if img_data:
            img_path = TMP / f"img_{seed}.jpg"
            img_path.write_bytes(img_data)
            slide = criar_slide_ffmpeg(img_path, insight, duracao=30)
            if slide:
                # Adicionar à playlist
                with open(concat_list, "a") as f:
                    f.write(f"file '{slide.resolve()}'\n")
        
        slide_idx += 1
        
        # Limpar slides antigos (manter últimos 10)
        slides_dir = list(TMP.glob("slide_*.mp4"))
        if len(slides_dir) > 10:
            for old in sorted(slides_dir)[:-10]:
                old.unlink(missing_ok=True)

if __name__ == "__main__":
    stream_loop()
