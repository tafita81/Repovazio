#!/usr/bin/env python3
"""
live_global_master.py
Sistema de live 24/7 multi-idioma — 12 canais, 12 mercados, 1 script.
Seleciona idioma pelo env CANAL_IDIOMA e executa o stream correto.

Canais mapeados:
  EN → Psychology Frequencies       CPM $28 — USA/UK/AU/CA
  DE → Psychologie Frequenzen       CPM $18 — Deutschland  
  JA → サイコロジー周波数              CPM $15 — Japan
  FR → Psychologie Fréquences       CPM $14 — France
  KO → 심리학 주파수                  CPM $12 — Korea
  IT → Psicologia Frequenze         CPM $12 — Italia
  ZH → 心理学频率                     CPM $10 — China/Taiwan
  ES → Psicología Frecuencias       CPM $9  — México/España
  PT → Daniela Coelho               CPM $7  — Brasil
  AR → تردد علم النفس               CPM $6  — Arabia/MENA
  RU → Психология Частот            CPM $5  — Russia/CIS
  HI → मनोविज्ञान आवृत्ति             CPM $4  — India
"""
import os, time, subprocess, pathlib, requests, textwrap, hashlib, threading
from datetime import datetime, timezone, timedelta

# Config por idioma
IDIOMA  = os.getenv("CANAL_IDIOMA", "EN")
SK_ENV  = f"YOUTUBE_STREAM_KEY_{IDIOMA}"
SK      = os.getenv(SK_ENV, os.getenv("YOUTUBE_STREAM_KEY",""))
GROQ    = os.getenv("GROQ_API_KEY","")
HORAS   = int(os.getenv("HORAS","6"))
W, H    = 1280, 720
TMP     = pathlib.Path(f"/tmp/live_{IDIOMA.lower()}"); TMP.mkdir(exist_ok=True)

# ── CONTEÚDO POR IDIOMA ───────────────────────────────────────────────────
CONTEUDO = {
"EN": {
  "titulo_live": "🔴 528Hz SLEEP | Anxiety & Narcissism Healing | Psychology LIVE 24/7",
  "marca": "Psychology Frequencies · Evidence-Based Science",
  "cor": "#818CF8", "hz": 528,
  "insights": [
    ("Anxious Attachment & Sleep", "62% of adults have anxious attachment. It hyperactivates the amygdala during sleep — causing 3am rumination. Not weakness. Biology. — Ainsworth"),
    ("Covert Narcissism", "The most dangerous narcissist doesn't seem arrogant. They seem like the biggest victim. — Malkin, Harvard"),
    ("528Hz Science", "528Hz has been linked to reduced stress hormones in NCBI peer-reviewed research. Combined with 4Hz binaural, it induces delta sleep."),
    ("Gaslighting", "When you trust their version of reality more than yours, the gaslighting already worked. — Freyd, Oregon"),
    ("Cortisol & Insomnia", "Chronic anxiety raises cortisol, suppresses melatonin. 40% of anxious people have measurable sleep disruption. — Sapolsky, Stanford"),
    ("Trauma & REM", "Unprocessed trauma disrupts REM cycles. The body rehearses threats while you sleep. — van der Kolk"),
  ]
},
"ES": {
  "titulo_live": "🔴 528Hz DORMIR PROFUNDO | Ansiedad y Narcisismo | Psicología EN VIVO",
  "marca": "Psicología Frecuencias · Ciencia Basada en Evidencia",
  "cor": "#A78BFA", "hz": 528,
  "insights": [
    ("Apego ansioso y sueño", "El 62% de los adultos tienen apego ansioso. Hiperactivia la amígdala durante el sueño — causando rumiación a las 3am. No es debilidad. Es biología. — Ainsworth"),
    ("Narcisismo encubierto", "El narcisista más peligroso no parece arrogante. Parece la mayor víctima de la sala. — Malkin, Harvard"),
    ("Ciencia 528Hz", "528Hz se ha vinculado a la reducción de hormonas de estrés en investigación revisada por pares del NCBI. Con binaural 4Hz induce sueño delta."),
    ("Gaslighting", "Cuando confías más en su versión de la realidad que en la tuya, el gaslighting ya funcionó. — Freyd, Oregon"),
    ("Cortisol e insomnio", "La ansiedad crónica eleva el cortisol y suprime la melatonina. El 40% de los ansiosos tienen disrupciones del sueño. — Sapolsky"),
    ("Trauma y REM", "El trauma no procesado interrumpe los ciclos REM. El cuerpo ensaya amenazas mientras duermes. — van der Kolk"),
  ]
},
"DE": {
  "titulo_live": "🔴 528Hz SCHLAF | Angst und Narzissmus Heilung | Psychologie LIVE",
  "marca": "Psychologie Frequenzen · Evidenzbasierte Wissenschaft",
  "cor": "#60A5FA", "hz": 528,
  "insights": [
    ("Ängstliche Bindung und Schlaf", "62% der Erwachsenen haben ängstliche Bindung. Sie überaktiviert die Amygdala während des Schlafs. Nicht Schwäche. Biologie. — Ainsworth"),
    ("Verdeckter Narzissmus", "Der gefährlichste Narzisst wirkt nicht arrogant. Er wirkt wie das größte Opfer im Raum. — Malkin, Harvard"),
    ("528Hz Wissenschaft", "528Hz wurde in NCBI-Forschung mit reduzierten Stresshormonen in Verbindung gebracht. Mit 4Hz binaural induziert es Delta-Schlaf."),
    ("Gaslighting", "Wenn du ihrer Version der Realität mehr vertraust als deiner eigenen, hat Gaslighting bereits funktioniert. — Freyd, Oregon"),
    ("Cortisol und Schlaflosigkeit", "Chronische Angst erhöht Cortisol und unterdrückt Melatonin. 40% der Ängstlichen haben messbare Schlafstörungen. — Sapolsky"),
  ]
},
"FR": {
  "titulo_live": "🔴 528Hz SOMMEIL | Anxiété et Narcissisme | Psychologie EN DIRECT",
  "marca": "Psychologie Fréquences · Science Fondée sur les Preuves",
  "cor": "#F472B6", "hz": 528,
  "insights": [
    ("Attachement anxieux et sommeil", "62% des adultes ont un attachement anxieux. Il hyperactive l'amygdale pendant le sommeil. Pas une faiblesse. De la biologie. — Ainsworth"),
    ("Narcissisme masqué", "Le narcissiste le plus dangereux ne semble pas arrogant. Il semble être la plus grande victime. — Malkin, Harvard"),
    ("Science 528Hz", "Le 528Hz a été lié à la réduction des hormones de stress dans des recherches de l'NCBI. Avec binaural 4Hz, il induit le sommeil delta."),
    ("Gaslighting", "Quand vous faites confiance à leur version de la réalité plus qu'à la vôtre, le gaslighting a déjà fonctionné. — Freyd, Oregon"),
  ]
},
"IT": {
  "titulo_live": "🔴 528Hz SONNO | Ansia e Narcisismo Guarigione | Psicologia IN DIRETTA",
  "marca": "Psicologia Frequenze · Scienza Basata su Evidenze",
  "cor": "#34D399", "hz": 528,
  "insights": [
    ("Attaccamento ansioso e sonno", "Il 62% degli adulti ha un attaccamento ansioso. Iperattiva l'amigdala durante il sonno. Non debolezza. Biologia. — Ainsworth"),
    ("Narcisismo celato", "Il narcisista più pericoloso non sembra arrogante. Sembra la vittima più grande della stanza. — Malkin, Harvard"),
    ("Scienza 528Hz", "Il 528Hz è stato collegato alla riduzione degli ormoni dello stress in ricerche NCBI peer-reviewed. Con binaural 4Hz induce sonno delta."),
  ]
},
"JA": {
  "titulo_live": "🔴 528Hz 睡眠音楽 | 不安と自己愛性 | 心理学ライブ 24/7",
  "marca": "サイコロジー周波数 · 科学的根拠に基づく",
  "cor": "#FB7185", "hz": 528,
  "insights": [
    ("不安型愛着と睡眠", "成人の62%が不安型愛着を持っています。睡眠中に扁桃体を過活性化させ、午前3時の反芻思考を引き起こします。弱さではなく、生物学的な反応です。— Ainsworth"),
    ("隠れたナルシシズム", "最も危険なナルシストは傲慢に見えません。部屋で最大の被害者に見えます。— Malkin, ハーバード大学"),
    ("528Hzの科学", "528HzはNCBIの査読研究でストレスホルモンの減少と関連付けられています。4Hzバイノーラルと組み合わせるとデルタ睡眠を誘発します。"),
  ]
},
"KO": {
  "titulo_live": "🔴 528Hz 수면 음악 | 불안과 자기애성 | 심리학 라이브 24/7",
  "marca": "심리학 주파수 · 증거 기반 과학",
  "cor": "#FBBF24", "hz": 528,
  "insights": [
    ("불안 애착과 수면", "성인의 62%가 불안 애착을 가지고 있습니다. 수면 중 편도체를 과활성화시켜 새벽 3시 반추 사고를 유발합니다. 약함이 아닌 생물학입니다. — Ainsworth"),
    ("은밀한 자기애", "가장 위험한 나르시시스트는 오만하게 보이지 않습니다. 방에서 가장 큰 피해자처럼 보입니다. — Malkin, Harvard"),
    ("528Hz 과학", "528Hz는 NCBI 동료 검토 연구에서 스트레스 호르몬 감소와 연관되었습니다."),
  ]
},
"PT": {
  "titulo_live": "🔴 528Hz SONO PROFUNDO | Ansiedade e Narcisismo | Psicologia AO VIVO",
  "marca": "Daniela Coelho · Pesquisa e Conteúdo em Psicologia",
  "cor": "#818CF8", "hz": 528,
  "insights": [
    ("Apego ansioso e sono", "62% dos adultos têm apego ansioso. Ele hiperativa a amígdala durante o sono — causando ruminação às 3h. Não é fraqueza. É biologia. — Ainsworth"),
    ("Narcisismo encoberto", "O narcisista mais perigoso não parece arrogante. Parece a maior vítima da sala. — Malkin, Harvard"),
    ("Ciência 528Hz", "528Hz foi associado à redução de hormônios de estresse em pesquisa revisada por pares do NCBI. Com binaural 4Hz induz sono delta."),
    ("Gaslighting", "Quando você confia mais na versão da realidade deles do que na sua, o gaslighting já funcionou. — Freyd, Oregon"),
    ("Cortisol e insônia", "Ansiedade crônica eleva cortisol e suprime melatonina. 40% dos ansiosos têm disrupcão do sono. — Sapolsky, Stanford"),
  ]
},
"ZH": {
  "titulo_live": "🔴 528Hz 深度睡眠 | 焦虑与自恋症恢复 | 心理学直播 24/7",
  "marca": "心理学频率 · 基于科学的内容",
  "cor": "#38BDF8", "hz": 528,
  "insights": [
    ("焦虑依恋与睡眠", "62%的成年人有焦虑型依恋。它在睡眠中过度激活杏仁核，导致凌晨3点反刍思维。这不是软弱，而是生理反应。— Ainsworth"),
    ("隐性自恋", "最危险的自恋者看起来并不傲慢。他们看起来像是房间里最大的受害者。— Malkin, 哈佛大学"),
    ("528Hz科学", "528Hz在NCBI同行评审研究中与应激激素减少有关。与4Hz双耳节拍结合可诱导δ睡眠波。"),
  ]
},
"AR": {
  "titulo_live": "🔴 528Hz نوم عميق | القلق والنرجسية | علم النفس مباشر",
  "marca": "تردد علم النفس · علم قائم على الأدلة",
  "cor": "#A78BFA", "hz": 528,
  "insights": [
    ("القلق في النوم", "62٪ من البالغين لديهم تعلق قلق. يفرط في تنشيط اللوزة أثناء النوم. ليس ضعفاً. بيولوجيا. — Ainsworth"),
    ("النرجسية الخفية", "أخطر النرجسي لا يبدو متعجرفاً. يبدو كأكبر ضحية في الغرفة. — Malkin، هارفارد"),
    ("علم 528Hz", "ارتبط 528Hz بانخفاض هرمونات التوتر في أبحاث NCBI المحكّمة."),
  ]
},
"RU": {
  "titulo_live": "🔴 528Гц СОН | Тревога и Нарциссизм | Психология ПРЯМОЙ ЭФИР",
  "marca": "Психология Частот · Научно-обоснованный контент",
  "cor": "#F87171", "hz": 528,
  "insights": [
    ("Тревожная привязанность и сон", "62% взрослых имеют тревожную привязанность. Она гиперактивирует миндалину во время сна — вызывая руминацию в 3 часа ночи. Не слабость. Биология. — Ainsworth"),
    ("Скрытый нарциссизм", "Самый опасный нарцисс не выглядит высокомерным. Он выглядит как самая большая жертва. — Malkin, Гарвард"),
    ("Наука 528 Гц", "528 Гц связан со снижением гормонов стресса в рецензируемых исследованиях NCBI."),
  ]
},
"HI": {
  "titulo_live": "🔴 528Hz गहरी नींद | चिंता और मनोविज्ञान | लाइव 24/7",
  "marca": "मनोविज्ञान आवृत्ति · विज्ञान आधारित सामग्री",
  "cor": "#FCD34D", "hz": 528,
  "insights": [
    ("चिंतित लगाव और नींद", "62% वयस्कों में चिंतित लगाव होता है। यह नींद के दौरान एमिग्डाला को अति-सक्रिय करता है। कमजोरी नहीं, जीव विज्ञान है। — Ainsworth"),
    ("गुप्त नार्सिसिज्म", "सबसे खतरनाक नार्सिसिस्ट अहंकारी नहीं दिखता। वह कमरे का सबसे बड़ा पीड़ित दिखता है। — Malkin, Harvard"),
    ("528Hz विज्ञान", "NCBI की सहकर्मी-समीक्षित शोध में 528Hz को तनाव हार्मोन में कमी से जोड़ा गया है।"),
  ]
},
}

def gen_audio(hz, dur_min=30):
    hz_r = hz + 4  # binaural beat
    ao = TMP/f"audio_{hz}hz.aac"
    if ao.exists() and ao.stat().st_size > 50000: return ao
    dur = dur_min * 60
    subprocess.run([
        "ffmpeg","-y",
        "-f","lavfi","-i",f"sine=frequency={hz}:duration={dur}",
        "-f","lavfi","-i",f"sine=frequency={hz_r}:duration={dur}",
        "-f","lavfi","-i",f"sine=frequency=174:duration={dur}",
        "-f","lavfi","-i",f"anoisesrc=color=pink:duration={dur}",
        "-filter_complex",
        "[0:a]volume=0.038[l];[1:a]volume=0.038[r];[2:a]volume=0.012[b];[3:a]volume=0.004[p];"
        "[l][r]amerge=inputs=2[bin];[bin][b][p]amix=inputs=3[out]",
        "-map","[out]","-c:a","aac","-b:a","192k","-ar","44100",str(ao)
    ], capture_output=True, timeout=120)
    return ao if ao.exists() else None

def get_img(tema, seed):
    p = (f"masterpiece, ultra HD cinematic dark background, {tema} psychology healing, "
         f"deep space aurora particles, extremely calming serene, no text no people, 8k "
         f"### text watermark nsfw blurry people logos")
    url = f"https://image.pollinations.ai/prompt/{requests.utils.quote(p[:380])}?model=flux&width={W}&height={H}&seed={seed}&nologo=true"
    try:
        r = requests.get(url, timeout=60)
        if r.status_code == 200 and len(r.content) > 10000: return r.content
    except: pass
    return None

def make_slide(img_p, cfg, tema, insight, idx, total, out):
    hz   = cfg["hz"]; tc = cfg["cor"]
    mk   = cfg["marca"].replace("'",r"\'")
    tema_e = tema.replace("'",r"\'")
    lines = textwrap.wrap(insight, 42)[:2]
    l1 = (lines[0] if lines else "").replace("'",r"\'")
    l2 = (lines[1] if len(lines)>1 else "").replace("'",r"\'")
    pw = max(4, int(W * idx / max(total,1)))
    hora = datetime.now(timezone.utc).strftime("%H:%M UTC")
    vf = (
        f"scale={W}:{H}:force_original_aspect_ratio=increase,crop={W}:{H},"
        f"colorchannelmixer=rr=0.65:gg=0.65:bb=0.65,"
        f"drawbox=y=0:color=black@0.88:width=iw:height=66:t=fill,"
        f"drawbox=y=ih-70:color=black@0.92:width=iw:height=70:t=fill,"
        f"drawbox=y=ih-4:color={tc}@0.85:width={pw}:height=4:t=fill,"
        f"drawbox=x=12:y=16:color=#EF4444:width=10:height=10:t=fill,"
        f"drawtext=text='{hz}Hz':fontsize=22:fontcolor={tc}:x=30:y=12:bold=1:shadowcolor=black:shadowx=1:shadowy=1,"
        f"drawtext=text='LIVE':fontsize=13:fontcolor=#EF4444:x=30:y=38:bold=1,"
        f"drawtext=text='{tema_e}':fontsize=16:fontcolor={tc}@0.9:x=(w-text_w)/2:y=h*0.34:shadowcolor=black:shadowx=1:shadowy=1,"
        f"drawtext=text='{l1}':fontsize=25:fontcolor=white:x=(w-text_w)/2:y=h*0.41:bold=1:shadowcolor=#000:shadowx=2:shadowy=2,"
    )
    if l2: vf += f"drawtext=text='{l2}':fontsize=25:fontcolor=white:x=(w-text_w)/2:y=h*0.41+37:bold=1:shadowcolor=#000:shadowx=2:shadowy=2,"
    vf += (
        f"drawtext=text='{hora}':fontsize=12:fontcolor=#475569:x=w-90:y=20,"
        f"drawtext=text='{mk}':fontsize=12:fontcolor=#94A3B8:x=(w-text_w)/2:y=h-45"
    )
    subprocess.run([
        "ffmpeg","-y","-loop","1","-i",str(img_p),"-vf",vf,
        "-t","60","-c:v","libx264","-preset","fast","-tune","stillimage",
        "-pix_fmt","yuv420p","-r","30","-an",str(out)
    ], capture_output=True, timeout=180)
    return out.exists() and out.stat().st_size > 10000

def run():
    if IDIOMA not in CONTEUDO:
        print(f"Idioma {IDIOMA} não mapeado. Disponíveis: {list(CONTEUDO.keys())}")
        return
    if not SK:
        print(f"YOUTUBE_STREAM_KEY_{IDIOMA} não configurado.")
        print(f"Criar canal YouTube e adicionar stream key como secret {SK_ENV}")
        return
    
    cfg      = CONTEUDO[IDIOMA]
    content  = cfg["insights"]
    rtmp_url = f"rtmp://a.rtmp.youtube.com/live2/{SK}"
    
    print(f"=== LIVE {IDIOMA} | {cfg['titulo_live'][:50]}... ===")
    print(f"    CPM alvo: veja tabela canais_globais no Supabase")
    print(f"    Hz: {cfg['hz']}")
    
    audio = gen_audio(cfg["hz"])
    slides, pl_f = [], TMP/"playlist.txt"
    
    for i in range(min(4, len(content))):
        tema, ins = content[i % len(content)]
        seed = int(hashlib.md5(f"{IDIOMA}{i}".encode()).hexdigest()[:8], 16)
        img_data = get_img(tema, seed)
        if not img_data: continue
        img_p = TMP/f"bg_{seed}.jpg"; img_p.write_bytes(img_data)
        sl = TMP/f"sl_{IDIOMA}_{i}.mp4"
        if make_slide(img_p, cfg, tema, ins, i, len(content), sl):
            slides.append(sl)
            print(f"  ✅ [{i+1}] {tema[:40]}")
        time.sleep(2)
    
    if not slides: return
    with open(pl_f,"w") as f: [f.write(f"file '{s.resolve()}'\n") for s in slides]
    
    asrc = ["-stream_loop","-1","-i",str(audio)] if audio and audio.exists() \
           else ["-f","lavfi","-i",f"sine=frequency={cfg['hz']}:duration=999999"]
    
    proc = subprocess.Popen([
        "ffmpeg","-y",
        "-f","concat","-safe","0","-stream_loop","-1","-i",str(pl_f),
        *asrc,
        "-c:v","libx264","-preset","veryfast","-tune","stillimage",
        "-b:v","3500k","-maxrate","3500k","-bufsize","7000k",
        "-g","60","-pix_fmt","yuv420p",
        "-c:a","aac","-b:a","192k","-ar","44100","-ac","2",
        "-f","flv", rtmp_url
    ])
    
    def bg(start=4):
        idx=start
        while proc.poll() is None:
            time.sleep(55)
            tema,ins = content[idx%len(content)]
            seed = int(hashlib.md5(f"{IDIOMA}{idx}".encode()).hexdigest()[:8],16)
            img_d = get_img(tema,seed)
            if img_d:
                ip=TMP/f"bg_{seed}.jpg"; ip.write_bytes(img_d)
                sl=TMP/f"sl_{IDIOMA}_{idx}.mp4"
                if make_slide(ip,cfg,tema,ins,idx%len(content),len(content),sl):
                    with open(pl_f,"a") as f: f.write(f"file '{sl.resolve()}'\n")
            for old in sorted(TMP.glob(f"sl_{IDIOMA}_*.mp4"))[:-6]: old.unlink(missing_ok=True)
            idx+=1
    
    threading.Thread(target=bg,daemon=True).start()
    print(f"\n✅ LIVE {IDIOMA} ATIVA! studio.youtube.com")
    try: proc.wait(timeout=HORAS*3600)
    except: proc.terminate()

if __name__=="__main__":
    import hashlib
    run()
