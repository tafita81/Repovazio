#!/usr/bin/env python3
"""
live_24h_manager.py — Anti-travamento: 480p / bitrate adaptativo
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
PERFIS DE QUALIDADE:
  SONO (22h-06h):  360p  · 300kbps  · tela PRETA (zero brilho)
  OUTROS blocos:   480p  · 800kbps  · visual colorido

POR QUE NÃO TRAVA:
  360p  = resolução mínima aceita pelo YouTube Live
  480p  = leve, funciona em 3G/4G fraco
  bufsize pequeno = FFmpeg não acumula frames atrasados
  reconnect = retenta automaticamente se cair
  thread_queue_size = evita overflow de buffer em internet lenta
"""
import os, time, subprocess, pathlib, sys
from datetime import datetime, timezone, timedelta

STREAM_KEY = os.getenv("YOUTUBE_STREAM_KEY","")
GROQ_KEY   = os.getenv("GROQ_API_KEY","")
RTMP_PRI   = f"rtmp://a.rtmp.youtube.com/live2/{STREAM_KEY}"
RTMP_BCK   = f"rtmp://b.rtmp.youtube.com/live2/{STREAM_KEY}?backup=1"
TMP        = pathlib.Path("/tmp/lv"); TMP.mkdir(exist_ok=True)
FONT_B     = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
FONT_L     = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"

BLOCOS = {
    "sono_528":     {"hz":528,"hz2":538,"preta":True},
    "foco_40":      {"hz":40,"hz2":50,"preta":False,"bg":"010C01","c1":"00FF66","c2":"00AA44","label":"40 Hz","sub":"Foco Total Ondas Gamma"},
    "psicologia":   {"hz":0,"hz2":0,"preta":False,"bg":"08000F","c1":"CC00FF","c2":"880099","label":"PSICOLOGIA","sub":"Dark Psychology Daniela Coelho"},
    "foco_trabalho":{"hz":40,"hz2":50,"preta":False,"bg":"010814","c1":"0088FF","c2":"0055AA","label":"40 Hz","sub":"Produtividade Deep Work"},
    "ansiedade_432":{"hz":432,"hz2":442,"preta":False,"bg":"060010","c1":"9955FF","c2":"6633CC","label":"432 Hz","sub":"Ansiedade Zero"},
    "prime_time":   {"hz":0,"hz2":0,"preta":False,"bg":"0F0000","c1":"FF2200","c2":"AA1100","label":"PRIME TIME","sub":"Psicologia Dark Ao Vivo"},
    "cura_174":     {"hz":174,"hz2":184,"preta":False,"bg":"010C02","c1":"00DD55","c2":"009933","label":"174 Hz","sub":"Cura Emocional"},
}
AGENDA = [(22,6,"sono_528"),(6,9,"foco_40"),(9,12,"psicologia"),
          (12,15,"foco_trabalho"),(15,18,"ansiedade_432"),(18,21,"prime_time"),(21,22,"cura_174")]

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

# ── PRETO ABSOLUTO 360p — zero travamento, zero brilho ──────────────────
def stream_preto_360p(hz, hz2, duracao=60):
    """
    360p (640x360) · 30kbps vídeo · binaural 128kbps áudio
    Y=0 U=128 V=128 em cada pixel → preto matemático absoluto.
    bufsize=60k → libera frames rapidinho mesmo em 3G fraco.
    thread_queue_size=512 → não trava se internet hesitar.
    reconnect_streamed=1 → retenta RTMP automaticamente.
    """
    for rtmp in [RTMP_PRI, RTMP_BCK]:
        cmd = [
            "ffmpeg","-y",
            # Opções de reconexão automática
            "-reconnect","1",
            "-reconnect_streamed","1",
            "-reconnect_delay_max","5",
            # Fonte de vídeo: preto matemático 640x360
            "-f","lavfi",
            "-i","nullsrc=size=640x360:rate=15",   # 15fps (metade) = menos CPU
            # Fonte de áudio: binaural
            "-f","lavfi","-i",f"sine=frequency={hz}:sample_rate=44100",
            "-f","lavfi","-i",f"sine=frequency={hz2}:sample_rate=44100",
            # Processar: preto puro + merge binaural stereo
            "-filter_complex",
            "geq=0:128:128[v];[1:a][2:a]join=inputs=2:channel_layout=stereo,volume=0.22[a]",
            "-map","[v]","-map","[a]",
            # Vídeo: 360p, 30kbps, ultrafast, preto puro
            "-c:v","libx264",
            "-preset","ultrafast",
            "-tune","stillimage",
            "-crf","51",
            "-b:v","30k","-maxrate","30k","-bufsize","60k",
            "-pix_fmt","yuv420p",
            "-r","15","-g","30",             # 15fps, GOP=30
            "-thread_queue_size","512",      # buffer interno
            # Áudio: 128kbps stereo
            "-c:a","aac","-b:a","128k","-ar","44100","-ac","2",
            "-t",str(duracao),"-f","flv",rtmp
        ]
        try:
            r = subprocess.run(cmd, capture_output=True, timeout=duracao+30)
            if r.returncode == 0: return True
        except Exception as e:
            print(f"  RTMP erro: {e}")
    return False

# ── VISUAL COLORIDO 480p — leve, funciona em 4G ─────────────────────────
def gerar_frame_480p(bloco_nome):
    b = BLOCOS[bloco_nome]
    out = str(TMP / f"f_{bloco_nome}.jpg")
    hora = datetime.now().strftime("%H:%M")
    # 854x480 (480p)
    vf = (
        f"scale=854:480,"
        f"drawbox=w=iw:h=ih:color=0x{b['bg']}:t=fill,"
        f"drawbox=x=0:y=0:w=iw:h=4:color=0x{b['c1']}:t=fill,"
        f"drawbox=x=0:y=476:w=iw:h=4:color=0x{b['c1']}:t=fill,"
        f"drawtext=text='{b['label']}':fontsize=80:fontcolor=0x{b['c1']}:"
        f"x=(w-text_w)/2:y=140:fontfile={FONT_B},"
        f"drawtext=text='{b['sub']}':fontsize=22:fontcolor=0x{b['c1']}CC:"
        f"x=(w-text_w)/2:y=238:fontfile={FONT_L},"
        f"drawtext=text='AO VIVO {hora} BRT @psidanielacoelho':"
        f"fontsize=15:fontcolor=0x{b['c2']}:x=(w-text_w)/2:y=278:fontfile={FONT_L}"
    )
    subprocess.run(
        ["ffmpeg","-y","-f","lavfi","-i","color=size=854x480:rate=1",
         "-vf",vf,"-frames:v","1","-q:v","2",out],
        capture_output=True, timeout=20
    )
    return out

def stream_visual_480p(bloco_nome, duracao=60):
    b   = BLOCOS[bloco_nome]
    hz  = b["hz"]; hz2 = b["hz2"]
    out = gerar_frame_480p(bloco_nome)

    if hz > 0:
        audio = ["-f","lavfi","-i",f"sine=frequency={hz}:sample_rate=44100",
                 "-f","lavfi","-i",f"sine=frequency={hz2}:sample_rate=44100",
                 "-filter_complex","[1:a][2:a]join=inputs=2:channel_layout=stereo,volume=0.22[a]",
                 "-map","0:v","-map","[a]","-c:a","aac","-b:a","128k","-ar","44100"]
    else:
        audio = ["-f","lavfi","-i","sine=frequency=60:sample_rate=44100",
                 "-filter_complex","[1:a]volume=0.04[a]",
                 "-map","0:v","-map","[a]","-c:a","aac","-b:a","64k","-ar","44100"]

    for rtmp in [RTMP_PRI, RTMP_BCK]:
        cmd = (
            ["ffmpeg","-y",
             "-reconnect","1","-reconnect_streamed","1","-reconnect_delay_max","5",
             "-re","-loop","1","-i",out]
            + audio
            + [
                "-c:v","libx264","-preset","ultrafast","-tune","zerolatency",
                "-b:v","800k","-maxrate","800k","-bufsize","1600k",
                "-pix_fmt","yuv420p","-r","24","-g","48",
                "-thread_queue_size","512",
                "-t",str(duracao),"-f","flv",rtmp
            ]
        )
        try:
            r = subprocess.run(cmd, capture_output=True, timeout=duracao+30)
            if r.returncode == 0: return True
        except: pass
    return False

def run():
    if not STREAM_KEY:
        print("ERRO: YOUTUBE_STREAM_KEY nao configurado"); sys.exit(1)
    print("=== LIVE 24H — Anti-travamento: 360p/480p adaptativo ===")
    print("  SONO  22-06h: 360p·30kbps·15fps — preto ABSOLUTO, não trava")
    print("  OUTROS blocos: 480p·800kbps·24fps — colorido, fluido")
    print()

    while True:
        bloco = bloco_atual()
        b     = BLOCOS[bloco]
        h_brt = hora_brt()

        if b.get("preta"):
            hz = b["hz"]; hz2 = b["hz2"]
            print(f"  {h_brt:02d}h [PRETO 360p·30k] {hz}Hz/{hz2}Hz binaural")
            ok = stream_preto_360p(hz, hz2, 60)
        else:
            print(f"  {h_brt:02d}h [COR 480p·800k] {b.get('label','')} — {b.get('sub','')[:25]}")
            ok = stream_visual_480p(bloco, 60)

        if not ok: print("  Stream falhou — tentando próxima iteração")
        time.sleep(2)

if __name__=="__main__": run()
