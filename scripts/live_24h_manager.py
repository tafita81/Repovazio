#!/usr/bin/env python3
"""
live_24h_manager.py — DEFINITIVO
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
SONO (22h-06h BRT):
  Vídeo: color=black SEM filtro algum → ZERO texto, ZERO imagem, ZERO brilho
  Áudio: 528Hz canal esq + 538Hz canal dir (binaural stereo real)
  Qualidade: 360p·30kbps·15fps → não trava em celular/internet ruim

OUTROS BLOCOS (acordado):
  Vídeo: frame colorido via FFmpeg drawtext (SEM Pollinations, SEM menina)
  Áudio: binaural ou tom suave
"""
import os, time, subprocess, pathlib, sys
from datetime import datetime, timezone, timedelta

STREAM_KEY = os.getenv("YOUTUBE_STREAM_KEY", "")
RTMP_A  = f"rtmp://a.rtmp.youtube.com/live2/{STREAM_KEY}"
RTMP_B  = f"rtmp://b.rtmp.youtube.com/live2/{STREAM_KEY}?backup=1"
TMP     = pathlib.Path("/tmp/lv"); TMP.mkdir(exist_ok=True)
FONT_B  = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
FONT_L  = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"

# Blocos — preta=True → tela COMPLETAMENTE PRETA sem nada
BLOCOS = {
    "sono":    {"hz":528,"hz2":538,"preta":True},
    "foco":    {"hz":40,"hz2":50,"preta":False,"bg":"010C01","c1":"00FF66","label":"40 Hz","sub":"Foco Total"},
    "psico":   {"hz":0,"hz2":0,"preta":False,"bg":"08000F","c1":"CC00FF","label":"PSICOLOGIA","sub":"Dark Psychology"},
    "prod":    {"hz":40,"hz2":50,"preta":False,"bg":"010814","c1":"0088FF","label":"40 Hz","sub":"Produtividade"},
    "ansi":    {"hz":432,"hz2":442,"preta":False,"bg":"060010","c1":"9955FF","label":"432 Hz","sub":"Ansiedade Zero"},
    "prime":   {"hz":0,"hz2":0,"preta":False,"bg":"0F0000","c1":"FF6600","label":"PRIME TIME","sub":"Psicologia Dark"},
    "cura":    {"hz":174,"hz2":184,"preta":False,"bg":"010C02","c1":"00DD55","label":"174 Hz","sub":"Cura Emocional"},
}
AGENDA = [
    (22, 6,  "sono"),
    (6,  9,  "foco"),
    (9,  12, "psico"),
    (12, 15, "prod"),
    (15, 18, "ansi"),
    (18, 21, "prime"),
    (21, 22, "cura"),
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
    return "prime"

def ffmpeg(cmd, duracao):
    """Roda FFmpeg; tenta RTMP A, fallback RTMP B."""
    for rtmp in [RTMP_A, RTMP_B]:
        full = cmd + ["-t", str(duracao), "-f", "flv", rtmp]
        try:
            r = subprocess.run(full, capture_output=True, timeout=duracao + 30)
            if r.returncode == 0:
                return True
        except Exception as e:
            print(f"  erro: {e}")
    return False

def stream_sono(duracao=60):
    """
    TELA PRETA ABSOLUTA — color=black SEM filtro de vídeo.
    Nenhum drawtext, nenhuma imagem, nenhum pixel diferente de zero.
    """
    base = [
        "ffmpeg", "-y",
        # ── Vídeo: preto puro 360p 15fps ──────────────────────
        "-f", "lavfi", "-i", "color=black:size=640x360:rate=15",
        # ── Áudio: binaural 528Hz/538Hz stereo ────────────────
        "-f", "lavfi", "-i", "sine=frequency=528:sample_rate=44100",
        "-f", "lavfi", "-i", "sine=frequency=538:sample_rate=44100",
        "-filter_complex",
        "[1:a][2:a]join=inputs=2:channel_layout=stereo,volume=0.2[a]",
        "-map", "0:v", "-map", "[a]",
        # ── Codec: preto comprime a 30kbps sem ruído ──────────
        "-c:v", "libx264", "-preset", "ultrafast",
        "-tune", "stillimage",
        "-crf", "51", "-b:v", "30k", "-maxrate", "30k", "-bufsize", "60k",
        "-pix_fmt", "yuv420p", "-r", "15", "-g", "30",
        "-c:a", "aac", "-b:a", "128k", "-ar", "44100", "-ac", "2",
    ]
    return ffmpeg(base, duracao)

def stream_colorido(bloco_nome, duracao=60):
    """Frame colorido via FFmpeg drawtext — sem Pollinations, sem anime."""
    b   = BLOCOS[bloco_nome]
    out = str(TMP / f"{bloco_nome}.jpg")
    hora = datetime.now().strftime("%H:%M")
    c1  = b["c1"]
    bg  = b["bg"]

    vf = (
        f"drawbox=w=iw:h=ih:color=0x{bg}:t=fill,"
        f"drawbox=x=0:y=0:w=iw:h=5:color=0x{c1}:t=fill,"
        f"drawbox=x=0:y=355:w=iw:h=5:color=0x{c1}:t=fill,"
        f"drawtext=text='{b['label']}':fontsize=88:fontcolor=0x{c1}:"
        f"x=(w-text_w)/2:y=120:fontfile={FONT_B},"
        f"drawtext=text='{b['sub']}':fontsize=26:fontcolor=0x{c1}CC:"
        f"x=(w-text_w)/2:y=228:fontfile={FONT_L},"
        f"drawtext=text='AO VIVO {hora} BRT @psidanielacoelho':"
        f"fontsize=16:fontcolor=0x{c1}88:x=(w-text_w)/2:y=268:fontfile={FONT_L}"
    )
    subprocess.run(
        ["ffmpeg", "-y", "-f", "lavfi", "-i", "color=size=854x360:rate=1",
         "-vf", vf, "-frames:v", "1", "-q:v", "2", out],
        capture_output=True, timeout=20
    )

    hz  = b["hz"]; hz2 = b["hz2"]
    if hz > 0:
        audio = [
            "-f","lavfi","-i",f"sine=frequency={hz}:sample_rate=44100",
            "-f","lavfi","-i",f"sine=frequency={hz2}:sample_rate=44100",
            "-filter_complex","[1:a][2:a]join=inputs=2:channel_layout=stereo,volume=0.2[a]",
            "-map","0:v","-map","[a]",
            "-c:a","aac","-b:a","128k","-ar","44100","-ac","2",
        ]
    else:
        audio = [
            "-f","lavfi","-i","sine=frequency=60:sample_rate=44100",
            "-filter_complex","[1:a]volume=0.05[a]",
            "-map","0:v","-map","[a]",
            "-c:a","aac","-b:a","64k","-ar","44100","-ac","2",
        ]

    base = (
        ["ffmpeg","-y","-re","-loop","1","-i",out]
        + audio
        + ["-c:v","libx264","-preset","ultrafast","-tune","zerolatency",
           "-b:v","800k","-maxrate","800k","-bufsize","1600k",
           "-pix_fmt","yuv420p","-r","24","-g","48"]
    )
    return ffmpeg(base, duracao)

def run():
    if not STREAM_KEY:
        print("ERRO: YOUTUBE_STREAM_KEY nao configurado")
        sys.exit(1)

    print("=== LIVE 24H — Preto absoluto durante sono ===")
    print("  22-06h: color=black ZERO texto ZERO imagem")
    print("  Outros: colorido sem Pollinations sem anime")
    print()

    while True:
        bloco = bloco_atual()
        b     = BLOCOS[bloco]
        h_brt = hora_brt()

        if b["preta"]:
            print(f"  {h_brt:02d}h [PRETO TOTAL] 528Hz/538Hz — tela vazia")
            stream_sono(60)
        else:
            print(f"  {h_brt:02d}h [{bloco}] {b['label']} {b['sub']}")
            stream_colorido(bloco, 60)

        time.sleep(2)

if __name__ == "__main__":
    run()
