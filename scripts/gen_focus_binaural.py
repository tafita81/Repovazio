#!/usr/bin/env python3
"""
gen_focus_binaural.py — Formato Greenred Productions (2M subs, $15K/mês)
Focus/Study com binaural beats animados
Duração: 1-3h | CPM: $6-15 | Retencao: estudantes ficam horas
"""
import os, subprocess, requests, pathlib, time

IDIOMA = os.getenv("CANAL_IDIOMA","EN")
TMP    = pathlib.Path(f"/tmp/focus_{IDIOMA}"); TMP.mkdir(exist_ok=True)
W, H   = 1920, 1080
DUR    = 3600  # 1 hora

CONFIGS = {
"EN": {"hz":40,"hz_right":80,"titulo":"40Hz FOCUS MUSIC ⚡ ADHD Concentration, Study, Work | Gamma Binaural Beats","tags":"40hz gamma waves,adhd focus music,study music,concentration,binaural beats focus,gamma waves","texto":"40Hz Gamma · ADHD Focus · Working Memory"},
"PT": {"hz":40,"hz_right":80,"titulo":"40Hz MÚSICA DE FOCO ⚡ TDAH, Estudo e Trabalho | Binaural Gamma","tags":"40hz ondas gamma,tdah foco,música estudo,concentração,binaural beats foco","texto":"40Hz Gamma · Foco TDAH · Memória de Trabalho"},
"ES": {"hz":40,"hz_right":80,"titulo":"40Hz MÚSICA DE ENFOQUE ⚡ TDAH, Estudio y Trabajo | Binaural Gamma","tags":"40hz ondas gamma,tdah enfoque,musica estudio,concentracion,binaural beats","texto":"40Hz Gamma · Enfoque TDAH · Memoria de Trabajo"},
"DE": {"hz":40,"hz_right":80,"titulo":"40Hz FOKUS MUSIK ⚡ ADHS Konzentration, Studium, Arbeit | Gamma Binaural","tags":"40hz gamma wellen,adhs fokus,lernmusik,konzentration,binaural beats","texto":"40Hz Gamma · ADHS Fokus · Arbeitsgedächtnis"},
"JA": {"hz":40,"hz_right":80,"titulo":"40Hz 集中力音楽 ⚡ ADHD 勉強・仕事用 | ガンマバイノーラル","tags":"40hz ガンマ波,adhd 集中,勉強音楽,集中力,バイノーラルビート","texto":"40Hz ガンマ · ADHD フォーカス · ワーキングメモリ"},
"FR": {"hz":40,"hz_right":80,"titulo":"40Hz MUSIQUE DE CONCENTRATION ⚡ TDAH, Études | Binaural Gamma","tags":"40hz ondes gamma,tdah concentration,musique etude,binaural beats","texto":"40Hz Gamma · Concentration TDAH · Mémoire de Travail"},
"KO": {"hz":40,"hz_right":80,"titulo":"40Hz 집중력 음악 ⚡ ADHD 공부·업무용 | 감마 바이노럴","tags":"40hz 감마파,adhd 집중,공부 음악,집중력,바이노럴 비트","texto":"40Hz 감마 · ADHD 집중 · 작업 기억"},
"IT": {"hz":40,"hz_right":80,"titulo":"40Hz MUSICA DI CONCENTRAZIONE ⚡ ADHD, Studio | Binaural Gamma","tags":"40hz onde gamma,adhd concentrazione,musica studio,binaural beats","texto":"40Hz Gamma · Concentrazione ADHD · Memoria di Lavoro"},
"ZH": {"hz":40,"hz_right":80,"titulo":"40Hz 专注力音乐 ⚡ ADHD学习·工作 | 伽马双耳节拍","tags":"40hz伽马波,adhd专注,学习音乐,集中力,双耳节拍","texto":"40Hz 伽马 · ADHD专注 · 工作记忆"},
"AR": {"hz":40,"hz_right":80,"titulo":"40Hz موسيقى التركيز ⚡ اضطراب انتباه، دراسة | بيناورال غاما","tags":"40hz موجات غاما,اضطراب انتباه,موسيقى دراسة,تركيز","texto":"40Hz غاما · تركيز ADHD · الذاكرة العاملة"},
"RU": {"hz":40,"hz_right":80,"titulo":"40Гц МУЗЫКА ДЛЯ КОНЦЕНТРАЦИИ ⚡ СДВГ, Учёба | Гамма Бинауральные","tags":"40гц гамма волны,сдвг концентрация,музыка для учёбы,бинауральные ритмы","texto":"40Гц Гамма · Концентрация СДВГ · Рабочая Память"},
"HI": {"hz":40,"hz_right":80,"titulo":"40Hz फोकस म्यूजिक ⚡ ADHD, पढ़ाई और काम | गामा बाइनॉरल","tags":"40hz गामा तरंगें,adhd फोकस,पढ़ाई संगीत,एकाग्रता","texto":"40Hz गामा · ADHD फोकस · कार्यशील स्मृति"},
}

def run():
    cfg = CONFIGS.get(IDIOMA, CONFIGS["EN"])
    hz = cfg["hz"]; hz_r = cfg["hz_right"]
    print(f"=== GREENRED FORMAT | {IDIOMA} | {hz}Hz Focus ===")
    
    # Áudio binaural 1h
    ao = TMP/f"binaural_{hz}hz_1h.aac"
    if not (ao.exists() and ao.stat().st_size > 100000):
        print("  Gerando áudio binaural 1h...")
        subprocess.run([
            "ffmpeg","-y",
            "-f","lavfi","-i",f"sine=frequency={hz}:duration={DUR}",
            "-f","lavfi","-i",f"sine=frequency={hz_r}:duration={DUR}",
            "-f","lavfi","-i",f"sine=frequency=10:duration={DUR}",
            "-f","lavfi","-i",f"anoisesrc=color=brown:duration={DUR}",
            "-filter_complex",
            f"[0:a]volume=0.04[l];[1:a]volume=0.04[r];"
            f"[2:a]volume=0.008[base];[3:a]volume=0.003[noise];"
            "[l][r]amerge=inputs=2[bin];[bin][base][noise]amix=inputs=3[out]",
            "-map","[out]","-c:a","aac","-b:a","192k","-ar","44100",str(ao)
        ], capture_output=True, timeout=300)
    
    # Imagem base (animação geométrica estilo Greenred)
    prompt = (f"masterpiece, 8K, dark background, glowing sacred geometry mandala, "
              f"purple blue green colors, focus concentration concept, rotating slightly, "
              f"mathematical precision, no text no people, meditative aesthetic")
    url = f"https://image.pollinations.ai/prompt/{requests.utils.quote(prompt)}?model=flux&width={W}&height={H}&seed=4001&nologo=true"
    try:
        ri = requests.get(url, timeout=60)
        if ri.status_code == 200: (TMP/"bg.jpg").write_bytes(ri.content)
    except: pass
    
    if not (TMP/"bg.jpg").exists():
        subprocess.run(["ffmpeg","-y","-f","lavfi","-i",f"color=c=0x050510:s={W}x{H}","-frames:v","1",str(TMP/"bg.jpg")],capture_output=True)
    
    texto_esc = cfg["texto"].replace("'",r"\'")
    hz_texto = f"{hz}Hz GAMMA"
    out = TMP/f"focus_{IDIOMA}_{hz}hz_1h.mp4"
    
    vf = (
        f"scale={W}:{H}:force_original_aspect_ratio=increase,crop={W}:{H},"
        f"colorchannelmixer=rr=0.7:gg=0.7:bb=0.7,"
        f"drawbox=y=0:color=black@0.7:width=iw:height=110:t=fill,"
        f"drawbox=y=ih-90:color=black@0.7:width=iw:height=90:t=fill,"
        f"drawtext=text='{hz_texto}':fontsize=64:fontcolor=#34D399:x=(w-text_w)/2:y=10:bold=1:shadowcolor=#000:shadowx=3:shadowy=3,"
        f"drawtext=text='BINAURAL BEATS':fontsize=24:fontcolor=#6EE7B7@0.9:x=(w-text_w)/2:y=82,"
        f"drawtext=text='{texto_esc}':fontsize=22:fontcolor=white@0.8:x=(w-text_w)/2:y=h-65,"
        f"drawtext=text='MIT Research · Gamma Waves · Working Memory':fontsize=16:fontcolor=#64748B:x=(w-text_w)/2:y=h-35"
    )
    
    print(f"  Renderizando 1h de vídeo focus...")
    subprocess.run([
        "ffmpeg","-y","-loop","1","-i",str(TMP/"bg.jpg"),"-i",str(ao),
        "-vf",vf,"-t",str(DUR),
        "-c:v","libx264","-preset","veryfast","-tune","stillimage",
        "-b:v","1000k","-pix_fmt","yuv420p","-r","24",
        "-c:a","aac","-b:a","192k","-shortest",str(out)
    ], capture_output=True, timeout=1800)
    
    if out.exists():
        print(f"  ✅ {out} ({out.stat().st_size//1024//1024}MB)")
        print(f"     Título: {cfg['titulo']}")

if __name__ == "__main__":
    run()
