#!/usr/bin/env python3
"""
gen_sleep_8h.py — Gera vídeos de 8h de sono (modelo Meditative Mind 3.2M subs)

FÓRMULA: imagem natureza 1920x1080 + 528Hz binaural + texto flutuante minimal
DURAÇÃO: 8 horas exatas = máximo watch time por usuário que dorme com ligado
CPM: $8-20 (wellness + psychology keywords)
Watch time médio por usuário: 6-8 horas

Idiomas: EN/ES/DE/FR/IT/JA/KO/PT/ZH/AR/RU/HI
"""
import os, subprocess, requests, pathlib, time

IDIOMA = os.getenv("CANAL_IDIOMA","EN")
GROQ   = os.getenv("GROQ_API_KEY","")
TMP    = pathlib.Path(f"/tmp/sleep8h_{IDIOMA}"); TMP.mkdir(exist_ok=True)
W, H   = 1920, 1080
DURACAO_H = 8

# Títulos e textos por idioma — exatamente como os maiores canais fazem
CONFIG = {
"EN": {
  "titulo":   "528Hz DEEP SLEEP MUSIC ✨ Heal Anxiety, Release Narcissism Trauma | 8 Hours",
  "subtitulo":"528Hz Solfeggio + Delta Binaural 4Hz",
  "texto1":   "Let your nervous system heal while you sleep",
  "texto2":   "528Hz · Delta Waves · Anxiety Relief",
  "tags":     "528hz sleep music,healing frequency,anxiety relief sleep,binaural beats,delta waves,sleep meditation,narcissism recovery,trauma healing,deep sleep",
  "descricao": "8 Hours of 528Hz healing frequency combined with delta binaural beats (4Hz) for deep, restorative sleep. Based on research linking 528Hz to reduced stress hormones (NCBI, 2019).\n\nLeave playing while you sleep. Your nervous system heals during deep rest.\n\n#528hz #sleepmusic #healingfrequency #anxiety #deepsleep",
},
"PT": {
  "titulo":   "528Hz SONO PROFUNDO ✨ Curar Ansiedade, Apego e Trauma | 8 Horas",
  "subtitulo":"528Hz Solfeggio + Binaural Delta 4Hz",
  "texto1":   "Deixe seu sistema nervoso curar enquanto você dorme",
  "texto2":   "528Hz · Ondas Delta · Alívio da Ansiedade",
  "tags":     "528hz dormir,frequência cura,ansiedade sono,binaural beats,ondas delta,meditação sono,narcisismo cura,trauma sono profundo",
  "descricao": "8 horas de frequência 528Hz com binaural delta (4Hz) para sono profundo e reparador. Baseado em pesquisa que liga 528Hz à redução de hormônios de estresse (NCBI, 2019).\n\nDeixe tocando enquanto dorme.\n\n#528hz #sonoetranquilo #frequenciacura #ansiedade",
},
"ES": {
  "titulo":   "528Hz SUEÑO PROFUNDO ✨ Sanar Ansiedad y Trauma Narcisista | 8 Horas",
  "subtitulo":"528Hz Solfeggio + Binaural Delta 4Hz",
  "texto1":   "Deja que tu sistema nervioso sane mientras duermes",
  "texto2":   "528Hz · Ondas Delta · Alivio de Ansiedad",
  "tags":     "528hz dormir,frecuencia curacion,ansiedad sueno,binaural beats,ondas delta,narcisismo curacion",
  "descricao": "8 horas de frecuencia 528Hz con binaural delta (4Hz) para sueño profundo. Basado en investigación NCBI 2019.\n\n#528hz #suenoprofundo #frecuenciacuracion",
},
"DE": {
  "titulo":   "528Hz TIEFER SCHLAF ✨ Angst und Trauma heilen | 8 Stunden",
  "subtitulo":"528Hz Solfeggio + Delta Binaural 4Hz",
  "texto1":   "Lass dein Nervensystem heilen während du schläfst",
  "texto2":   "528Hz · Delta-Wellen · Angstlinderung",
  "tags":     "528hz schlaf,heilfrequenz,angst schlaf,binaural beats,delta wellen,trauma heilung schlaf",
  "descricao": "8 Stunden 528Hz Heilfrequenz mit Delta-Binaural (4Hz). NCBI-Forschung zeigt Reduktion von Stresshormonen.\n\n#528hz #tieferschlaf #heilfrequenz",
},
"JA": {
  "titulo":   "528Hz 深睡眠音楽 ✨ 不安とトラウマを癒す | 8時間",
  "subtitulo":"528Hz ソルフェジオ + デルタバイノーラル 4Hz",
  "texto1":   "眠りながら神経系を癒しましょう",
  "texto2":   "528Hz · デルタ波 · 不安緩和",
  "tags":     "528hz 睡眠,癒しの周波数,不安 睡眠,バイノーラルビート,デルタ波",
  "descricao": "528Hzヒーリング周波数とデルタバイノーラル(4Hz)による8時間の深い睡眠音楽。NCBI研究でストレスホルモン減少が確認されています。\n\n#528hz #睡眠音楽 #癒し",
},
"FR": {
  "titulo":   "528Hz SOMMEIL PROFOND ✨ Guérir l'Anxiété et le Trauma | 8 Heures",
  "subtitulo":"528Hz Solfège + Binaural Delta 4Hz",
  "texto1":   "Laissez votre système nerveux guérir pendant que vous dormez",
  "texto2":   "528Hz · Ondes Delta · Soulagement de l'Anxiété",
  "tags":     "528hz sommeil,frequence guerison,anxiete sommeil,binaural beats,ondes delta",
  "descricao": "8 heures de fréquence 528Hz avec binaural delta (4Hz). Recherche NCBI confirme la réduction des hormones de stress.\n\n#528hz #sommeilprofond #guerison",
},
"KO": {
  "titulo":   "528Hz 깊은 수면 음악 ✨ 불안과 트라우마 치유 | 8시간",
  "subtitulo":"528Hz 솔페지오 + 델타 바이노럴 4Hz",
  "texto1":   "잠자는 동안 신경계를 치유하세요",
  "texto2":   "528Hz · 델타파 · 불안 완화",
  "tags":     "528hz 수면,치유 주파수,불안 수면,바이노럴 비트,델타파",
  "descricao": "8시간의 528Hz 치유 주파수와 델타 바이노럴 비트(4Hz). NCBI 연구로 스트레스 호르몬 감소 확인.\n\n#528hz #수면음악 #치유",
},
"IT": {
  "titulo":   "528Hz SONNO PROFONDO ✨ Guarire Ansia e Trauma Narcisistico | 8 Ore",
  "subtitulo":"528Hz Solfeggio + Binaural Delta 4Hz",
  "texto1":   "Lascia che il tuo sistema nervoso guarisca mentre dormi",
  "texto2":   "528Hz · Onde Delta · Sollievo dall'Ansia",
  "tags":     "528hz sonno,frequenza guarigione,ansia sonno,binaural beats,onde delta",
  "descricao": "8 ore di frequenza 528Hz con binaural delta (4Hz). Ricerca NCBI conferma riduzione degli ormoni dello stress.\n\n#528hz #sonnoprofondo #guarigione",
},
"ZH": {
  "titulo":   "528Hz 深度睡眠音乐 ✨ 治愈焦虑和自恋创伤 | 8小时",
  "subtitulo":"528Hz 索尔菲吉奥 + 德尔塔双耳节拍 4Hz",
  "texto1":   "让您的神经系统在睡眠中愈合",
  "texto2":   "528Hz · 德尔塔波 · 焦虑缓解",
  "tags":     "528hz睡眠,治愈频率,焦虑睡眠,双耳节拍,德尔塔波",
  "descricao": "8小时528Hz治愈频率配合德尔塔双耳节拍(4Hz)。NCBI研究证实可降低应激激素。\n\n#528hz #深度睡眠 #治愈",
},
"RU": {
  "titulo":   "528Гц ГЛУБОКИЙ СОН ✨ Исцелить Тревогу и Нарциссическую Травму | 8 Часов",
  "subtitulo":"528Гц Солфеджио + Бинауральные Дельта 4Гц",
  "texto1":   "Пусть ваша нервная система исцелится во время сна",
  "texto2":   "528Гц · Дельта-волны · Снятие тревоги",
  "tags":     "528гц сон,частота исцеления,тревога сон,бинауральные ритмы",
  "descricao": "8 часов 528Гц с бинауральными дельта-ритмами (4Гц). Исследования NCBI подтверждают снижение гормонов стресса.\n\n#528гц #глубокийсон #исцеление",
},
"AR": {
  "titulo":   "528Hz نوم عميق ✨ شفاء القلق وصدمة النرجسية | 8 ساعات",
  "subtitulo":"528Hz سولفيجيو + ثنائي الأذن دلتا 4Hz",
  "texto1":   "دع جهازك العصبي يشفى أثناء نومك",
  "texto2":   "528Hz · موجات دلتا · تخفيف القلق",
  "tags":     "528hz نوم,تردد شفاء,قلق نوم,ثنائي الأذن,موجات دلتا",
  "descricao": "8 ساعات من تردد 528Hz مع ثنائي الأذن دلتا (4Hz). أثبت بحث NCBI تقليل هرمونات التوتر.\n\n#528hz #نوم_عميق #شفاء",
},
"HI": {
  "titulo":   "528Hz गहरी नींद ✨ चिंता और नार्सिसिज्म ट्रॉमा ठीक करें | 8 घंटे",
  "subtitulo":"528Hz सॉल्फेजियो + डेल्टा बाइनॉरल 4Hz",
  "texto1":   "सोते समय अपने तंत्रिका तंत्र को ठीक होने दें",
  "texto2":   "528Hz · डेल्टा वेव्स · चिंता राहत",
  "tags":     "528hz नींद,उपचार आवृत्ति,चिंता नींद,बाइनॉरल बीट्स",
  "descricao": "8 घंटे का 528Hz उपचार आवृत्ति डेल्टा बाइनॉरल (4Hz) के साथ। NCBI शोध तनाव हार्मोन में कमी की पुष्टि करता है।\n\n#528hz #गहरीनींद #उपचार",
},
}

def gerar_audio_8h(hz=528, hz_right=532, hz_base=174):
    """8 horas de áudio — a chave do modelo Meditative Mind"""
    ao = TMP/f"audio_8h_{hz}hz.aac"
    if ao.exists() and ao.stat().st_size > 5_000_000:
        print(f"  ♻️  Áudio 8h já existe: {ao.stat().st_size//1024//1024}MB")
        return ao
    dur = 8 * 3600  # 8 horas em segundos
    print(f"  🎵 Gerando {dur//3600}h de áudio {hz}Hz + binaural {hz_right-hz}Hz...")
    subprocess.run([
        "ffmpeg","-y",
        "-f","lavfi","-i",f"sine=frequency={hz}:duration={dur}",
        "-f","lavfi","-i",f"sine=frequency={hz_right}:duration={dur}",
        "-f","lavfi","-i",f"sine=frequency={hz_base}:duration={dur}",
        "-f","lavfi","-i",f"anoisesrc=color=pink:duration={dur}",
        "-filter_complex",
        "[0:a]volume=0.038[l];[1:a]volume=0.038[r];"
        "[2:a]volume=0.010[b];[3:a]volume=0.003[p];"
        "[l][r]amerge=inputs=2[binaural];"
        "[binaural][b][p]amix=inputs=3:duration=longest[out]",
        "-map","[out]","-c:a","aac","-b:a","192k","-ar","44100",str(ao)
    ], capture_output=True, timeout=600)
    if ao.exists():
        print(f"  ✅ Áudio: {ao.stat().st_size//1024//1024}MB")
    return ao if ao.exists() else None

def gerar_imagem_natureza(seed):
    """Imagem natureza HD — como Meditative Mind usa"""
    prompts = [
        "masterpiece, 8K ultra HD photo, magical dark forest with bioluminescent mushrooms and fireflies, deep purple and blue tones, extremely peaceful, ethereal atmosphere, no text no people",
        "masterpiece, 8K ultra HD photo, deep ocean view from underwater, rays of light penetrating dark blue water, bioluminescent creatures, mystical and calming, no text no people",
        "masterpiece, 8K ultra HD, night sky milky way with aurora borealis, purple and blue colors, cosmic and serene, stars and galaxies, no text no people",
        "masterpiece, 8K ultra HD, zen garden at night under full moon, lotus flowers floating, mist and fog, Japanese aesthetic, dark and peaceful, no text no people",
    ]
    prompt = prompts[seed % len(prompts)]
    url = (f"https://image.pollinations.ai/prompt/{requests.utils.quote(prompt[:450])}"
           f"?model=flux&width=1920&height=1080&seed={seed}&nologo=true&enhance=true")
    try:
        ri = requests.get(url, timeout=120)
        if ri.status_code == 200 and len(ri.content) > 50000:
            return ri.content
    except: pass
    return None

def gerar_video_8h(cfg, seed=9001):
    """Gera o vídeo de 8h — modelo exato Meditative Mind"""
    print(f"\n🎬 Gerando vídeo 8h: {cfg['titulo'][:60]}...")
    
    # 1. Imagem base
    img_data = gerar_imagem_natureza(seed)
    if not img_data:
        print("  Imagem falhou")
        return None
    img_p = TMP/f"bg_{seed}.jpg"; img_p.write_bytes(img_data)
    print(f"  ✅ Imagem: {len(img_data)//1024}KB")
    
    # 2. Áudio 8h
    audio = gerar_audio_8h()
    if not audio: return None
    
    # 3. Vídeo com overlay minimal (estilo Meditative Mind)
    titulo_esc   = cfg['titulo'][:50].replace("'", r"\'")
    subtitulo_esc= cfg['subtitulo'].replace("'", r"\'")
    texto1_esc   = cfg['texto1'].replace("'", r"\'")
    texto2_esc   = cfg['texto2'].replace("'", r"\'")
    
    vf = (
        # Imagem de fundo com leve escurecimento
        f"scale={W}:{H}:force_original_aspect_ratio=increase,crop={W}:{H},"
        f"colorchannelmixer=rr=0.7:gg=0.7:bb=0.7,"
        # Barra superior suave
        f"drawbox=y=0:color=black@0.6:width=iw:height=120:t=fill,"
        # Barra inferior suave
        f"drawbox=y=ih-100:color=black@0.6:width=iw:height=100:t=fill,"
        # Hz em destaque (como Meditative Mind faz)
        f"drawtext=text='528Hz':fontsize=72:fontcolor=#F59E0B:x=(w-text_w)/2:y=15:bold=1:shadowcolor=#000:shadowx=3:shadowy=3,"
        f"drawtext=text='{subtitulo_esc}':fontsize=22:fontcolor=#FCD34D@0.9:x=(w-text_w)/2:y=98,"
        # Texto central flutuante (aparece suavemente)
        f"drawtext=text='{texto1_esc}':fontsize=28:fontcolor=white@0.85:x=(w-text_w)/2:y=h*0.85:shadowcolor=#000:shadowx=2:shadowy=2,"
        f"drawtext=text='{texto2_esc}':fontsize=20:fontcolor=#818CF8@0.8:x=(w-text_w)/2:y=h-58"
    )
    
    out = TMP/f"sleep8h_{IDIOMA}_{seed}.mp4"
    dur = DURACAO_H * 3600
    
    print(f"  🎬 Renderizando {DURACAO_H}h de vídeo...")
    result = subprocess.run([
        "ffmpeg","-y",
        "-loop","1","-i",str(img_p),
        "-i",str(audio),
        "-vf",vf,
        "-t",str(dur),
        "-c:v","libx264","-preset","veryfast",
        "-tune","stillimage",
        "-b:v","1500k","-maxrate","1500k","-bufsize","3000k",
        "-pix_fmt","yuv420p","-r","24",
        "-c:a","aac","-b:a","192k","-shortest",
        str(out)
    ], capture_output=True, timeout=7200)  # 2h timeout
    
    if out.exists() and out.stat().st_size > 1_000_000:
        print(f"  ✅ Vídeo 8h gerado: {out.stat().st_size//1024//1024}MB")
        return {"path": str(out), "titulo": cfg["titulo"],
                "descricao": cfg["descricao"], "tags": cfg["tags"]}
    print(f"  ❌ Falhou: {result.stderr[-200:]}")
    return None

def run():
    if IDIOMA not in CONFIG:
        print(f"Idioma {IDIOMA} não mapeado")
        return
    cfg = CONFIG[IDIOMA]
    resultado = gerar_video_8h(cfg, seed=9001)
    if resultado:
        print(f"\n✅ PRONTO PARA UPLOAD:")
        print(f"   Arquivo: {resultado['path']}")
        print(f"   Título:  {resultado['titulo']}")

if __name__ == "__main__":
    run()
