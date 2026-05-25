#!/usr/bin/env python3
"""
live_24h_manager.py — Estratégia Meditative Mind (6 MILHÕES de inscritos)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
CASE REAL #1 — Meditative Mind (6M inscritos, maior canal do mundo):
  → Usa "Black Screen Sleep Music" — tela PRETA para dormir
  → Quem dorme com YouTube ligado NÃO quer luz na tela
  → Economia de bateria no celular (AMOLED = preto = 0 energia)
  → Tags oficiais do canal: #BlackScreenSleep #SleepMeditation
  → Cresceu de 0 → 6M com essa estratégia simples

CASE REAL #2 — Jason Stephenson (3M inscritos):
  → Fundo muito escuro + texto suave + narração calma
  → Evita imagens brilhantes para não acordar o ouvinte

CASE REAL #3 — Greenred Productions (2.2M inscritos):
  → Foco/estudo: cores vibrantes (verde, azul) + onda animada
  → Sono: escuro, sem estimulação visual

ESTRATÉGIA FINAL POR BLOCO:
  22h-06h SONO:       TELA PRETA + "528 Hz" suave (como Meditative Mind)
  06h-09h FOCO:       Azul/verde vibrante + "40 Hz" grande (acorda e energiza)
  09h-12h PSICOLOGIA: Roxo dramático + Daniela + texto dark
  12h-15h PRODUÇÃO:   Azul profundo + "40 Hz" + deep work
  15h-18h ANSIEDADE:  Lavanda suave + "432 Hz" (relaxamento)
  18h-21h PRIME TIME: Vermelho/roxo + Daniela + CTA máximo
  21h-22h CURA:       Verde escuro + "174 Hz" (preparo sono)
"""
import os, time, subprocess, pathlib, sys, requests
from datetime import datetime, timezone, timedelta
import urllib3; urllib3.disable_warnings()

STREAM_KEY = os.getenv("YOUTUBE_STREAM_KEY","")
GROQ_KEY   = os.getenv("GROQ_API_KEY","")
RTMP_PRI   = f"rtmp://a.rtmp.youtube.com/live2/{STREAM_KEY}"
RTMP_BCK   = f"rtmp://b.rtmp.youtube.com/live2/{STREAM_KEY}?backup=1"
TMP        = pathlib.Path("/tmp/mm"); TMP.mkdir(exist_ok=True)
FONT_B     = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
FONT_L     = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"

# Visual por bloco — baseado no Meditative Mind e cases reais
BLOCOS = {
    # ── SONO: TELA PRETA (estratégia Meditative Mind 6M) ──────────────────
    "sono_528": {
        "hz":528, "hz2":538,
        # Fundo PRETO ABSOLUTO — como Meditative Mind usa
        "bg":"0x000000",
        # Texto muito suave — mal visível, só para identificar
        "cor_hz":"0x1A3A5C",      # azul muito escuro
        "cor_sub":"0x0D1E2E",     # quase invisível
        "label":"528 Hz",
        "sub":"Sono Profundo · Black Screen",
        "tag":"🌙 AO VIVO · @psidanielacoelho",
        "usa_daniela": False,
        "tela_preta": True,       # ← modo Meditative Mind
    },
    # ── FOCO: VIBRANTE (Greenred Productions 2.2M) ────────────────────────
    "foco_40": {
        "hz":40, "hz2":50,
        "bg":"0x020C02",
        "cor_hz":"0x00FF66",      # verde neon — energizante
        "cor_sub":"0x00AA44",
        "label":"40 Hz",
        "sub":"Ondas Gamma · Foco Total · Deep Work",
        "tag":"⚡ AO VIVO · @psidanielacoelho",
        "usa_daniela": False,
        "tela_preta": False,
    },
    # ── PSICOLOGIA DARK: Daniela ──────────────────────────────────────────
    "psicologia": {
        "hz":0, "hz2":0,
        "bg":"0x08000F",
        "cor_hz":"0xAA00FF",      # roxo vivo
        "cor_sub":"0x6600CC",
        "label":"PSICOLOGIA DARK",
        "sub":"Narcisismo · Apego · Trauma · Daniela Coelho",
        "tag":"😶 AO VIVO · Comenta SONO · @psidanielacoelho",
        "usa_daniela": True,
        "tela_preta": False,
    },
    # ── PRODUTIVIDADE: azul profundo ──────────────────────────────────────
    "foco_trabalho": {
        "hz":40, "hz2":50,
        "bg":"0x010814",
        "cor_hz":"0x0088FF",      # azul royal
        "cor_sub":"0x0055AA",
        "label":"40 Hz",
        "sub":"Produtividade · Deep Work · Burnout Science",
        "tag":"🧠 AO VIVO · @psidanielacoelho",
        "usa_daniela": False,
        "tela_preta": False,
    },
    # ── ANSIEDADE: lavanda suave ──────────────────────────────────────────
    "ansiedade_432": {
        "hz":432, "hz2":442,
        "bg":"0x06000F",
        "cor_hz":"0x9955FF",      # violeta
        "cor_sub":"0x6633CC",
        "label":"432 Hz",
        "sub":"Ansiedade Zero · Sistema Nervoso · Dr. Porges",
        "tag":"💜 AO VIVO · @psidanielacoelho",
        "usa_daniela": False,
        "tela_preta": False,
    },
    # ── PRIME TIME: vermelho dramático ────────────────────────────────────
    "prime_time": {
        "hz":0, "hz2":0,
        "bg":"0x0F0000",
        "cor_hz":"0xFF2200",      # vermelho vivo
        "cor_sub":"0xAA1100",
        "label":"PRIME TIME",
        "sub":"Psicologia Dark · Ao Vivo Agora · Daniela Coelho",
        "tag":"🔥 AO VIVO · Comenta SONO · @psidanielacoelho",
        "usa_daniela": True,
        "tela_preta": False,
    },
    # ── CURA: verde escuro (preparo para sono) ────────────────────────────
    "cura_174": {
        "hz":174, "hz2":184,
        "bg":"0x010C02",
        "cor_hz":"0x00DD55",      # verde suave
        "cor_sub":"0x009933",
        "label":"174 Hz",
        "sub":"Cura Emocional · Alívio do Trauma · van der Kolk",
        "tag":"🌿 AO VIVO · @psidanielacoelho",
        "usa_daniela": False,
        "tela_preta": False,
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

def gerar_frame(bloco_nome, idx):
    b    = BLOCOS[bloco_nome]
    out  = str(TMP / f"f_{bloco_nome}_{idx%3}.jpg")
    hora = datetime.now().strftime("%H:%M")
    bg   = b["bg"]
    c1   = b["cor_hz"].replace("0x","")
    c2   = b["cor_sub"].replace("0x","")

    if b.get("tela_preta"):
        # ── MODO MEDITATIVE MIND: TELA PRETA ──────────────────────────────
        # Fundo PRETO. Apenas Hz muito suave no centro.
        # Exatamente como o Meditative Mind que chegou a 6M de inscritos.
        vf = (
            f"drawbox=w=iw:h=ih:color={bg}:t=fill,"
            # Hz suavíssimo — quase não aparece (propositalmente)
            f"drawtext=text='{b['label']}':fontsize=48:fontcolor=0x{c1}:"
            f"x=(w-text_w)/2:y=(h-text_h)/2-20:fontfile={FONT_B},"
            # Subtítulo invisível quase
            f"drawtext=text='{b['sub']}':fontsize=16:fontcolor=0x{c2}:"
            f"x=(w-text_w)/2:y=(h-text_h)/2+40:fontfile={FONT_L},"
            # Ponto vivo quase invisível
            f"drawtext=text='● AO VIVO':fontsize=12:fontcolor=0x110000:"
            f"x=20:y=20:fontfile={FONT_L}"
        )
    else:
        # ── MODO COLORIDO VIBRANTE (foco, psicologia, ansiedade) ──────────
        vf = (
            f"drawbox=w=iw:h=ih:color={bg}:t=fill,"
            # Barra top
            f"drawbox=x=0:y=0:w=iw:h=6:color=0x{c1}:t=fill,"
            # Barra bottom
            f"drawbox=x=0:y=714:w=iw:h=6:color=0x{c1}:t=fill,"
            # Label grande
            f"drawtext=text='{b['label']}':fontsize=120:fontcolor=0x{c1}:"
            f"x=(w-text_w)/2:y=210:fontfile={FONT_B},"
            # Subtítulo
            f"drawtext=text='{b['sub']}':fontsize=30:fontcolor=0x{c1}CC:"
            f"x=(w-text_w)/2:y=360:fontfile={FONT_L},"
            # Linha divisória
            f"drawbox=x=160:y=420:w=960:h=2:color=0x{c2}:t=fill,"
            # Tag + hora
            f"drawtext=text='{b['tag']}   {hora} BRT':fontsize=20:fontcolor=0x{c2}:"
            f"x=(w-text_w)/2:y=440:fontfile={FONT_L},"
            # Dot AO VIVO
            f"drawbox=x=26:y=22:w=10:h=10:color=0xFF2200:t=fill,"
            f"drawtext=text='AO VIVO':fontsize=16:fontcolor=0xFF2200:x=45:y=20:fontfile={FONT_B}"
        )

    cmd = ["ffmpeg","-y","-f","lavfi","-i","color=size=1280x720:rate=1",
           "-vf",vf,"-frames:v","1","-q:v","2",out]
    r = subprocess.run(cmd, capture_output=True, timeout=20)
    if r.returncode == 0: return out
    # Fallback mínimo se falhar
    cmd2 = ["ffmpeg","-y","-f","lavfi","-i",f"color=c={bg}:size=1280x720:rate=1",
            "-frames:v","1",out]
    subprocess.run(cmd2, capture_output=True, timeout=10)
    return out

def stream_com_audio(frame, bloco_nome, duracao=60):
    b   = BLOCOS[bloco_nome]
    hz  = b["hz"]
    hz2 = b["hz2"]

    if hz > 0:
        # Binaural real inline — hz esquerdo, hz2 direito
        audio = [
            "-f","lavfi","-i",f"sine=frequency={hz}:sample_rate=44100",
            "-f","lavfi","-i",f"sine=frequency={hz2}:sample_rate=44100",
            "-filter_complex","[1:a][2:a]join=inputs=2:channel_layout=stereo,volume=0.22[a]",
            "-map","0:v","-map","[a]",
            "-c:a","aac","-b:a","192k","-ar","44100",
        ]
    else:
        # Psicologia: silêncio elegante (tom grave quase inaudível)
        audio = [
            "-f","lavfi","-i","sine=frequency=60:sample_rate=44100",
            "-filter_complex","[1:a]volume=0.04[a]",
            "-map","0:v","-map","[a]",
            "-c:a","aac","-b:a","128k","-ar","44100",
        ]

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
            r = subprocess.run(cmd, capture_output=True, timeout=duracao+30)
            if r.returncode == 0: return True
        except Exception as e:
            print(f"  RTMP erro: {e}")
    return False

def run():
    if not STREAM_KEY:
        print("ERRO: YOUTUBE_STREAM_KEY nao configurado"); sys.exit(1)

    print("=== LIVE 24H — Estratégia Meditative Mind (6M inscritos) ===")
    print("  SONO  22-06h: TELA PRETA (modo Meditative Mind)")
    print("  FOCO  06-09h: Verde neon vibrante")
    print("  PSICO 09-12h: Roxo dramático")
    print("  PROD  12-15h: Azul royal")
    print("  ANSI  15-18h: Violeta suave")
    print("  PRIME 18-21h: Vermelho intenso")
    print("  CURA  21-22h: Verde escuro")
    print()

    idx = 0
    while True:
        bloco = bloco_atual()
        b     = BLOCOS[bloco]
        hz    = b["hz"]
        h_brt = hora_brt()
        modo  = "TELA PRETA" if b.get("tela_preta") else f"{hz}Hz" if hz else "DARK"

        print(f"  {h_brt:02d}h BRT [{bloco}] {modo} — {b['sub'][:40]}")

        frame = gerar_frame(bloco, idx)
        ok    = stream_com_audio(frame, bloco, 60)
        if not ok: print("  Stream falhou — reiniciando")

        idx += 1
        time.sleep(2)

if __name__=="__main__": run()
