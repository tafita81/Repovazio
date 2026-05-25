#!/usr/bin/env python3
"""
live_24h_manager.py — Visual profissional via FFmpeg puro (sem Pollinations à noite)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
REFERÊNCIA VISUAL DOS CANAIS QUE MAIS MONETIZAM:

  Meditative Mind 3.2M:   fundo preto + texto branco + Hz grande + nenhuma figura
  Jason Stephenson 3M:    imagem natureza + texto sobreposto + nenhuma figura
  Greenred 2M:            gradiente animado + onda senoidal + Hz grande + nenhuma figura
  Solfeggio Top (1M/6m):  fundo escuro + círculo animado + Hz + nenhuma figura

REGRA FINAL: NENHUMA FIGURA HUMANA/ANIME em blocos de frequência
Daniela aparece APENAS em conteúdo de psicologia dark (09h-12h e 18h-21h BRT)
"""
import os, time, subprocess, pathlib, sys
from datetime import datetime, timezone, timedelta

STREAM_KEY = os.getenv("YOUTUBE_STREAM_KEY","")
GROQ_KEY   = os.getenv("GROQ_API_KEY","")
RTMP_PRI   = f"rtmp://a.rtmp.youtube.com/live2/{STREAM_KEY}"
RTMP_BCK   = f"rtmp://b.rtmp.youtube.com/live2/{STREAM_KEY}?backup=1"
TMP        = pathlib.Path("/tmp/livefinal"); TMP.mkdir(exist_ok=True)

# Configuração visual de cada bloco — VIA FFMPEG PURO (sem Pollinations)
BLOCOS = {
    "sono_528": {
        "hz": 528,
        "hz2": 538,           # diferença binaural
        "titulo": "528 Hz",
        "subtitulo": "Sono Profundo · Regeneração Celular",
        "descricao": "Sono Reparador · Walker/Berkeley",
        "bg": "0x03050F",     # azul-escuro quase preto
        "cor_hz": "0x4A90D9", # azul suave
        "cor_sub": "0x2D5A8E",
        "usa_daniela": False,
    },
    "foco_40": {
        "hz": 40,
        "hz2": 50,
        "titulo": "40 Hz",
        "subtitulo": "Foco Total · Ondas Gamma",
        "descricao": "Produtividade · MIT Research",
        "bg": "0x020F02",
        "cor_hz": "0x4AD94A",
        "cor_sub": "0x2D8E2D",
        "usa_daniela": False,
    },
    "psicologia": {
        "hz": 0,
        "titulo": "Psicologia Dark",
        "subtitulo": "Narcisismo · Apego · Trauma",
        "descricao": "Harvard · UCLA · Berkeley Research",
        "bg": "0x0D000D",
        "cor_hz": "0xC084FC",
        "cor_sub": "0x7C3AED",
        "usa_daniela": True,   # Daniela aparece aqui
    },
    "foco_trabalho": {
        "hz": 40,
        "hz2": 50,
        "titulo": "40 Hz",
        "subtitulo": "Deep Work · Produtividade",
        "descricao": "Estudo e Trabalho · Gamma Waves",
        "bg": "0x020814",
        "cor_hz": "0x60A5FA",
        "cor_sub": "0x3B82F6",
        "usa_daniela": False,
    },
    "ansiedade_432": {
        "hz": 432,
        "hz2": 442,
        "titulo": "432 Hz",
        "subtitulo": "Ansiedade Zero · Sistema Nervoso",
        "descricao": "Regulação · Dr. Porges Research",
        "bg": "0x080014",
        "cor_hz": "0xA78BFA",
        "cor_sub": "0x7C3AED",
        "usa_daniela": False,
    },
    "prime_time": {
        "hz": 0,
        "titulo": "Psicologia Dark",
        "subtitulo": "Daniela Coelho · Ao Vivo Agora",
        "descricao": "Comportamento Humano · Pesquisa",
        "bg": "0x0F0005",
        "cor_hz": "0xF87171",
        "cor_sub": "0xE11D48",
        "usa_daniela": True,   # Daniela aqui também
    },
    "cura_174": {
        "hz": 174,
        "hz2": 184,
        "titulo": "174 Hz",
        "subtitulo": "Cura Emocional · Alívio do Trauma",
        "descricao": "van der Kolk Research · Healing",
        "bg": "0x030F03",
        "cor_hz": "0x86EFAC",
        "cor_sub": "0x22C55E",
        "usa_daniela": False,
    },
}

AGENDA = [
    (22, 6,  "sono_528"),
    (6,  9,  "foco_40"),
    (9,  12, "psicologia"),
    (12, 15, "foco_trabalho"),
    (15, 18, "ansiedade_432"),
    (18, 21, "prime_time"),
    (21, 22, "cura_174"),
]

def hora_brt():
    return (datetime.now(timezone.utc) - timedelta(hours=3)).hour

def bloco_atual():
    h = hora_brt()
    for ini, fim, b in AGENDA:
        if ini > fim:
            if h >= ini or h < fim: return b
        else:
            if ini <= h < fim: return b
    return "prime_time"

def gerar_frame_ffmpeg(bloco_nome, idx):
    """Gera frame profissional via FFmpeg puro — sem Pollinations, sem anime"""
    b = BLOCOS[bloco_nome]
    out = str(TMP / f"frame_{bloco_nome}_{idx%5}.jpg")

    hora_str = datetime.now().strftime("%H:%M")
    bg = b["bg"]
    cor_hz = b["cor_hz"]
    cor_sub = b["cor_sub"]

    if b["hz"] > 0:
        # Frame frequência: Hz grande centralizado + subtítulo + hora
        vf = (
            f"drawbox=w=iw:h=ih:color={bg}:t=fill,"
            # Linha decorativa topo
            f"drawbox=x=120:y=100:w=iw-240:h=3:color={cor_sub}AA:t=fill,"
            # Hz grande
            f"drawtext=text='{b['titulo']}':fontsize=130:fontcolor={cor_hz}:x=(w-text_w)/2:y=220"
            f":fontfile=/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf,"
            # Subtítulo
            f"drawtext=text='{b['subtitulo']}':fontsize=38:fontcolor={cor_sub}:x=(w-text_w)/2:y=380"
            f":fontfile=/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf,"
            # Descrição
            f"drawtext=text='{b['descricao']}':fontsize=26:fontcolor={cor_sub}88:x=(w-text_w)/2:y=435"
            f":fontfile=/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf,"
            # Linha decorativa meio
            f"drawbox=x=280:y=500:w=iw-560:h=1:color={cor_sub}55:t=fill,"
            # Hora e canal
            f"drawtext=text='AO VIVO · {hora_str} BRT · @psidanielacoelho':fontsize=22"
            f":fontcolor={cor_sub}66:x=(w-text_w)/2:y=540"
            f":fontfile=/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf,"
            # Linha decorativa baixo
            f"drawbox=x=120:y=617:w=iw-240:h=3:color={cor_sub}AA:t=fill"
        )
    else:
        # Frame psicologia: texto dark dramático
        vf = (
            f"drawbox=w=iw:h=ih:color={bg}:t=fill,"
            f"drawbox=x=0:y=0:w=iw:h=4:color={cor_sub}:t=fill,"
            f"drawbox=x=0:y=716:w=iw:h=4:color={cor_sub}:t=fill,"
            f"drawtext=text='ψ':fontsize=80:fontcolor={cor_hz}33:x=80:y=50"
            f":fontfile=/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf,"
            f"drawtext=text='{b['titulo']}':fontsize=72:fontcolor={cor_hz}:x=(w-text_w)/2:y=240"
            f":fontfile=/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf,"
            f"drawtext=text='{b['subtitulo']}':fontsize=36:fontcolor={cor_sub}:x=(w-text_w)/2:y=340"
            f":fontfile=/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf,"
            f"drawtext=text='{b['descricao']}':fontsize=26:fontcolor={cor_sub}88:x=(w-text_w)/2:y=400"
            f":fontfile=/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf,"
            f"drawbox=x=200:y=460:w=iw-400:h=1:color={cor_sub}44:t=fill,"
            f"drawtext=text='Comenta SONO · @psidanielacoelho · AO VIVO':fontsize=24"
            f":fontcolor={cor_sub}88:x=(w-text_w)/2:y=490"
            f":fontfile=/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
        )

    cmd = [
        "ffmpeg","-y","-f","lavfi",
        "-i","color=size=1280x720:rate=1",
        "-vf", vf,
        "-frames:v","1","-q:v","2", out
    ]
    r = subprocess.run(cmd, capture_output=True, timeout=20)
    return out if r.returncode == 0 else None

def gerar_binaural(hz, hz2, out):
    if hz <= 0 or pathlib.Path(out).exists(): return pathlib.Path(out).exists()
    cmd = [
        "ffmpeg","-y","-f","lavfi",
        f"-i","sine=frequency={hz}:duration=600",
        "-f","lavfi",
        f"-i","sine=frequency={hz2}:duration=600",
        "-filter_complex","[0:a][1:a]amerge=inputs=2,volume=0.28[out]",
        "-map","[out]","-ar","44100","-b:a","128k", out
    ]
    r = subprocess.run(cmd, capture_output=True, timeout=60)
    return r.returncode == 0

def stream_frame(frame, bloco_nome, duracao=60):
    b = BLOCOS[bloco_nome]
    hz = b.get("hz", 0)
    hz2 = b.get("hz2", hz+10)

    if hz > 0:
        tone = str(TMP / f"tone_{hz}_{hz2}.mp3")
        gerar_binaural(hz, hz2, tone)
        if pathlib.Path(tone).exists():
            audio = ["-stream_loop","-1","-i",tone,
                     "-c:a","aac","-b:a","128k","-ar","44100"]
        else:
            audio = ["-f","lavfi","-i","anullsrc=r=44100:cl=stereo",
                     "-c:a","aac","-b:a","128k","-ar","44100"]
    else:
        audio = ["-f","lavfi","-i","anullsrc=r=44100:cl=stereo",
                 "-c:a","aac","-b:a","128k","-ar","44100"]

    for rtmp in [RTMP_PRI, RTMP_BCK]:
        cmd = (
            ["ffmpeg","-y","-re","-loop","1","-i",frame]
            + audio
            + ["-c:v","libx264","-preset","ultrafast","-tune","zerolatency",
               "-b:v","3000k","-maxrate","3000k","-bufsize","6000k",
               "-pix_fmt","yuv420p","-r","30",
               "-t",str(duracao),"-f","flv",rtmp]
        )
        try:
            result = subprocess.run(cmd, capture_output=True, timeout=duracao+30)
            if result.returncode == 0: return True
        except: pass
    return False

def run():
    if not STREAM_KEY:
        print("ERRO: YOUTUBE_STREAM_KEY nao configurado"); sys.exit(1)

    print("=== LIVE 24H — Visual Profissional (sem figura nos blocos de frequência) ===")
    print("  SONO 528Hz:   fundo escuro + 528 Hz grande (nenhuma figura)")
    print("  FOCO 40Hz:    fundo verde-escuro + 40 Hz grande (nenhuma figura)")
    print("  ANSIEDADE:    fundo roxo + 432 Hz grande (nenhuma figura)")
    print("  PSICOLOGIA:   texto dark dramatico (Daniela aparece aqui)")
    print()

    idx = 0
    while True:
        bloco = bloco_atual()
        b = BLOCOS[bloco]
        h_brt = hora_brt()
        hz = b.get("hz",0)

        print(f"  {h_brt:02d}h [{bloco}] {'✦' if hz==0 else f'{hz}Hz'} — {b['subtitulo'][:40]}")

        frame = gerar_frame_ffmpeg(bloco, idx)
        if frame:
            stream_frame(frame, bloco, 60)
        else:
            print("  Erro no frame — aguardando")
            time.sleep(5)

        idx += 1
        time.sleep(2)

if __name__=="__main__": run()
