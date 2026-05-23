#!/usr/bin/env python3
"""
live_universal.py — Stream 24/7 universal para qualquer idioma/canal
Configura pelo env LANG_CODE e YOUTUBE_STREAM_KEY_{LANG}

Uso:
  LANG_CODE=DE YOUTUBE_STREAM_KEY_DE=xxx python3 live_universal.py
  LANG_CODE=JP YOUTUBE_STREAM_KEY_JP=xxx python3 live_universal.py
"""
import os, time, subprocess, pathlib, requests, textwrap, hashlib, threading
from datetime import datetime, timezone, timedelta

LANG_CODE  = os.getenv("LANG_CODE", "EN").upper()
KEY_NAME   = f"YOUTUBE_STREAM_KEY_{LANG_CODE}"
STREAM_KEY = os.getenv(KEY_NAME, os.getenv("YOUTUBE_STREAM_KEY", ""))
GROQ_KEY   = os.getenv("GROQ_API_KEY", "")
RTMP_URL   = f"rtmp://a.rtmp.youtube.com/live2/{STREAM_KEY}"
W, H = 1280, 720
TMP = pathlib.Path(f"/tmp/live_{LANG_CODE.lower()}")
TMP.mkdir(exist_ok=True)

# ── CONTEÚDO POR IDIOMA ────────────────────────────────────────────────────
CONTENT = {
    "EN": {
        "hz_label": "Hz SLEEP", "live_label": "LIVE",
        "brand": "Sarah Mitchell · Behavioral Research & Psychology",
        "streams": {
            "sleep":  ("528Hz DEEP SLEEP", "#050515", "#818CF8", [
                ("Anxious Attachment & Sleep", "Anxious attachment hyperactivates the amygdala during sleep — explaining 3am rumination. Biology, not weakness. — Ainsworth"),
                ("528Hz & Healing", "528Hz frequency linked to reduced stress hormones in peer-reviewed research. — NCBI 2019"),
                ("Narcissism Recovery", "Leaving a narcissistic relationship takes 3.5 years on average for nervous system recalibration. — Malkin/Harvard"),
                ("Cortisol & Insomnia", "Chronic anxiety elevates cortisol, which suppresses melatonin. The cycle explaining 40% of anxious insomnia. — Sapolsky"),
                ("Trauma & REM", "Unprocessed trauma disrupts REM cycles. The body rehearses threats during sleep. — van der Kolk"),
            ]),
            "prime":  ("963Hz LIBERATION", "#120008", "#FB7185", [
                ("Anxious Attachment", "62% of adults have insecure attachment. Most never knew. — Global Ainsworth Data"),
                ("Gaslighting Signs", "When you trust their reality more than yours, gaslighting already worked. — Freyd/Oregon"),
                ("Impostor Syndrome", "The more competent you are, the more you know what you don't know. Metacognition, not weakness."),
                ("Validation Addiction", "Likes activate the same reward circuit as cocaine. Variable ratio — the most addictive. — Skinner/Alter"),
                ("Covert Narcissism", "The most dangerous narcissist doesn't seem arrogant. They seem like the biggest victim. — Malkin/Harvard"),
            ]),
        }
    },
    "DE": {
        "hz_label": "Hz SCHLAF", "live_label": "LIVE",
        "brand": "Sarah Mitchell · Verhaltensforschung & Psychologie",
        "streams": {
            "sleep": ("528Hz TIEFER SCHLAF", "#050515", "#818CF8", [
                ("Ängstliche Bindung & Schlaf", "Ängstliche Bindung überaktiviert die Amygdala im Schlaf — erklärt nächtliches Grübeln um 3 Uhr. Biologie, keine Schwäche. — Ainsworth"),
                ("528Hz & Heilung", "528Hz-Frequenz wurde in Peer-Review-Forschung mit reduzierten Stresshormonen in Verbindung gebracht. — NCBI 2019"),
                ("Narzissmus-Genesung", "Das Verlassen einer narzisstischen Beziehung dauert durchschnittlich 3,5 Jahre für die Neukalibrierung. — Malkin/Harvard"),
                ("Kortisol & Schlaflosigkeit", "Chronische Angst erhöht Kortisol und unterdrückt Melatonin. Der Kreislauf hinter 40% der Schlaflosigkeit. — Sapolsky"),
                ("Gaslighting erkennen", "Wenn Sie ihrer Version der Realität mehr vertrauen als Ihrer eigenen, hat Gaslighting bereits funktioniert. — Freyd"),
            ]),
            "prime": ("963Hz BEFREIUNG", "#120008", "#FB7185", [
                ("Narzissmus Zeichen", "Der gefährlichste Narzisst wirkt nicht arrogant. Er wirkt wie das größte Opfer. — Malkin/Harvard"),
                ("ADHS & Prokrastination", "Prokrastination aktiviert den anterioren cingulären Kortex — dieselbe Region wie bei Schmerz. — Sirois"),
                ("Impostor-Syndrom", "Je kompetenter Sie sind, desto mehr wissen Sie, was Sie nicht wissen. Metakognition, nicht Schwäche."),
                ("Selbstmitgefühl", "8 Wochen Selbstmitgefühl-Praxis erhöht das Volumen des präfrontalen Kortex messbar. — Neff"),
                ("Emotionale Regulation", "Unterdrückung hält das Nervensystem aktiviert. Verarbeitung reduziert die Intensität. — Gross/Stanford"),
            ]),
        }
    },
    "FR": {
        "hz_label": "Hz SOMMEIL", "live_label": "EN DIRECT",
        "brand": "Sarah Mitchell · Recherche Comportementale & Psychologie",
        "streams": {
            "sleep": ("528Hz SOMMEIL PROFOND", "#050515", "#818CF8", [
                ("Attachement anxieux & Sommeil", "L'attachement anxieux hyperactive l'amygdale pendant le sommeil — expliquant les ruminations à 3h. Biologie, pas faiblesse. — Ainsworth"),
                ("528Hz & Guérison", "La fréquence 528Hz a été associée à des hormones de stress réduites dans des recherches évaluées. — NCBI 2019"),
                ("Récupération du narcissisme", "Quitter une relation narcissique prend en moyenne 3,5 ans pour recalibrer le système nerveux. — Malkin/Harvard"),
                ("Cortisol & Insomnie", "L'anxiété chronique élève le cortisol, qui supprime la mélatonine. Le cycle expliquant 40% des insomnies. — Sapolsky"),
                ("Gaslighting identification", "Quand vous faites plus confiance à leur réalité qu'à la vôtre, le gaslighting a déjà fonctionné. — Freyd"),
            ]),
            "prime": ("963Hz LIBÉRATION", "#120008", "#FB7185", [
                ("Narcissisme covert", "Le narcissiste le plus dangereux ne semble pas arrogant. Il semble être la plus grande victime. — Malkin/Harvard"),
                ("Syndrome de l'imposteur", "Plus vous êtes compétent, plus vous savez ce que vous ne savez pas. Métacognition, pas faiblesse."),
                ("Autocompassion", "8 semaines de pratique de l'autocompassion augmentent le volume du cortex préfrontal. — Neff/Germer"),
                ("Validation addiction", "Les likes activent le même circuit de récompense que la cocaïne. Renforcement variable. — Skinner/Alter"),
                ("Trauma & corps", "Le trauma n'est pas qu'un souvenir — c'est une réorganisation du système nerveux. — van der Kolk"),
            ]),
        }
    },
    "JA": {
        "hz_label": "Hz 睡眠", "live_label": "LIVE",
        "brand": "Sarah Mitchell · 行動研究・心理学",
        "streams": {
            "sleep": ("528Hz 深い眠り", "#050515", "#818CF8", [
                ("不安型愛着と睡眠", "不安型愛着は睡眠中に扁桃体を過活性化させる。夜中の3時の反芻の原因。弱さではなく生物学。 — Ainsworth"),
                ("528Hzと癒し", "528Hz周波数は査読研究でストレスホルモンの低下と関連している。 — NCBI 2019"),
                ("ナルシシズム回復", "ナルシシスティックな関係を離れた後、神経系の再校正に平均3.5年かかる。 — Malkin/Harvard"),
                ("コルチゾールと不眠", "慢性的な不安はコルチゾールを上昇させ、メラトニンを抑制する。不眠の40%を説明する循環。 — Sapolsky"),
                ("ガスライティング識別", "彼らの現実をあなた自身より信頼する時、ガスライティングはすでに機能している。 — Freyd"),
            ]),
            "prime": ("963Hz 解放", "#120008", "#FB7185", [
                ("隠れナルシシズム", "最も危険なナルシストは傲慢に見えない。最大の被害者に見える。 — Malkin/Harvard"),
                ("インポスター症候群", "有能であればあるほど、知らないことを知っている。弱さではなくメタ認知。"),
                ("自己compassion", "8週間の自己compassion実践で前頭前野皮質の体積が測定可能に増加する。 — Neff/Germer"),
                ("検証中毒", "いいねはコカインと同じ報酬回路を活性化する。変動比率強化。 — Skinner/Alter"),
                ("感情調整", "感情の抑圧は神経系を活性化したままにする。処理することで強度が減少する。 — Gross/Stanford"),
            ]),
        }
    },
    "KO": {
        "hz_label": "Hz 수면", "live_label": "LIVE",
        "brand": "Sarah Mitchell · 행동 연구 & 심리학",
        "streams": {
            "sleep": ("528Hz 깊은 잠", "#050515", "#818CF8", [
                ("불안형 애착과 수면", "불안형 애착은 수면 중 편도체를 과활성화시킨다. 새벽 3시 반추의 원인. 약함이 아닌 생물학. — Ainsworth"),
                ("528Hz와 치유", "528Hz 주파수는 동료 검토 연구에서 스트레스 호르몬 감소와 연관되었다. — NCBI 2019"),
                ("나르시시즘 회복", "나르시시스틱한 관계를 떠난 후 신경계 재조정에 평균 3.5년이 걸린다. — Malkin/Harvard"),
                ("코르티솔과 불면증", "만성 불안은 코르티솔을 높이고 멜라토닌을 억제한다. 불면증 40%를 설명하는 순환. — Sapolsky"),
                ("가스라이팅 식별", "당신 자신보다 그들의 현실을 더 신뢰할 때, 가스라이팅은 이미 작동했다. — Freyd"),
            ]),
            "prime": ("963Hz 해방", "#120008", "#FB7185", [
                ("은밀한 나르시시즘", "가장 위험한 나르시시스트는 오만해 보이지 않는다. 가장 큰 피해자처럼 보인다. — Malkin/Harvard"),
                ("사기꾼 증후군", "유능할수록 모르는 것을 더 많이 안다. 약함이 아닌 메타인지."),
                ("자기 연민", "8주간의 자기 연민 실천으로 전전두피질 부피가 측정 가능하게 증가한다. — Neff/Germer"),
                ("인정 중독", "좋아요는 코카인과 같은 보상 회로를 활성화한다. 변동 비율 강화. — Skinner/Alter"),
                ("감정 조절", "감정 억압은 신경계를 활성화 상태로 유지한다. 처리하면 강도가 감소한다. — Gross"),
            ]),
        }
    },
}

def utc_hour(): return datetime.now(timezone.utc).hour

def select_stream_by_hour(streams):
    h = utc_hour()
    keys = list(streams.keys())
    return keys[0] if h in range(0, 12) else keys[-1]

def gen_audio(hz, hz_right=None, mins=30):
    if hz_right is None: hz_right = hz + 4
    out = TMP / f"aud_{hz}_{mins}.aac"
    if out.exists() and out.stat().st_size > 50000: return out
    dur = mins * 60
    cmd = ["ffmpeg", "-y",
        "-f", "lavfi", "-i", f"sine=frequency={hz}:duration={dur}",
        "-f", "lavfi", "-i", f"sine=frequency={hz_right}:duration={dur}",
        "-f", "lavfi", "-i", f"anoisesrc=color=pink:duration={dur}",
        "-filter_complex",
        "[0:a]volume=0.035[l];[1:a]volume=0.035[r];[2:a]volume=0.004[p];"
        "[l][r]amerge=inputs=2[bin];[bin][p]amix=inputs=2:duration=longest[out]",
        "-map", "[out]", "-c:a", "aac", "-b:a", "192k", "-ar", "44100", str(out)]
    subprocess.run(cmd, capture_output=True, timeout=120)
    return out if out.exists() else None

def get_img(tema, color, seed):
    p = (f"masterpiece, ultra HD cinematic dark {color} background, {tema} psychology concept, "
         f"aurora borealis healing particles, no text no people, calming 8k")
    url = f"https://image.pollinations.ai/prompt/{requests.utils.quote(p[:380])}?model=flux&width={W}&height={H}&seed={seed}&nologo=true"
    try:
        r = requests.get(url, timeout=60)
        if r.status_code == 200 and len(r.content) > 10000: return r.content
    except: pass
    return None

def make_slide(img_p, hz_str, tema, insight, tc, brand, idx, total, out):
    lines = textwrap.wrap(insight, 40)[:2]
    l1 = (lines[0] if lines else "").replace("'", r"\'")
    l2 = (lines[1] if len(lines) > 1 else "").replace("'", r"\'")
    brand_e = brand.replace("'", r"\'")
    hz_e = hz_str.replace("'", r"\'")
    pw = max(4, int(W * idx / max(total, 1)))
    
    vf = (
        f"scale={W}:{H}:force_original_aspect_ratio=increase,crop={W}:{H},"
        f"colorchannelmixer=rr=0.65:gg=0.65:bb=0.65,"
        f"drawbox=y=0:color=black@0.88:width=iw:height=65:t=fill,"
        f"drawbox=y=ih-68:color=black@0.92:width=iw:height=68:t=fill,"
        f"drawbox=y=ih-4:color={tc}@0.85:width={pw}:height=4:t=fill,"
        f"drawbox=x=12:y=16:color=#EF4444:width=10:height=10:t=fill,"
        f"drawtext=text='{hz_e}':fontsize=18:fontcolor={tc}:x=30:y=12:bold=1:shadowcolor=black:shadowx=1:shadowy=1,"
        f"drawtext=text='{tema[:35]}':fontsize=14:fontcolor={tc}@0.85:x=(w-text_w)/2:y=h*0.35:shadowcolor=black:shadowx=1:shadowy=1,"
        f"drawtext=text='{l1}':fontsize=24:fontcolor=white:x=(w-text_w)/2:y=h*0.42:bold=1:shadowcolor=#000:shadowx=2:shadowy=2,"
    )
    if l2:
        vf += f"drawtext=text='{l2}':fontsize=24:fontcolor=white:x=(w-text_w)/2:y=h*0.42+36:bold=1:shadowcolor=#000:shadowx=2:shadowy=2,"
    vf += f"drawtext=text='{brand_e}':fontsize=11:fontcolor=#94A3B8:x=(w-text_w)/2:y=h-42"
    
    cmd = ["ffmpeg", "-y", "-loop", "1", "-i", str(img_p), "-vf", vf,
           "-t", "60", "-c:v", "libx264", "-preset", "fast", "-tune", "stillimage",
           "-pix_fmt", "yuv420p", "-r", "30", "-an", str(out)]
    subprocess.run(cmd, capture_output=True, timeout=180)
    return out.exists() and out.stat().st_size > 10000

def run():
    if not STREAM_KEY:
        print(f"Secret {KEY_NAME} not set in GitHub Secrets.")
        print(f"After creating YouTube channel: add {KEY_NAME} = [stream key]")
        return
    
    lang_data = CONTENT.get(LANG_CODE, CONTENT["EN"])
    streams   = lang_data["streams"]
    brand     = lang_data["brand"]
    
    sk  = select_stream_by_hour(streams)
    hz_str, color, tc, content = streams[sk]
    hz_num = int(hz_str.split("Hz")[0].split(" ")[-1].replace("Hz","").strip().split(" ")[0]
                 .replace("TIEFER", "").replace("SCHLAF","").replace("PROFOND","").replace("PROFUNDO","")
                 .replace("DEEP","").strip()) if "Hz" in hz_str else 528
    
    print(f"=== 🌍 LIVE {LANG_CODE} | {hz_str} ===")
    print(f"    {brand}")
    
    audio = gen_audio(hz_num)
    slides, concat_f = [], TMP / f"pl_{LANG_CODE.lower()}.txt"
    
    for i in range(3):
        tema, insight = content[i % len(content)]
        seed = int(hashlib.md5(f"{LANG_CODE}_{sk}_{i}".encode()).hexdigest()[:8], 16)
        img_data = get_img(tema, color, seed)
        if not img_data: continue
        img_p = TMP / f"bg_{sk}_{seed}.jpg"; img_p.write_bytes(img_data)
        sl = TMP / f"sl_{sk}_{i}.mp4"
        if make_slide(img_p, hz_str, tema, insight, tc, brand, i, len(content), sl):
            slides.append(sl)
            print(f"  ✅ [{i+1}] {tema[:40]}")
        time.sleep(2)
    
    if not slides: print("No slides."); return
    with open(concat_f, "w") as f: [f.write(f"file '{s.resolve()}'\n") for s in slides]
    
    audio_src = ["-stream_loop", "-1", "-i", str(audio)] if audio and audio.exists() \
                else ["-f", "lavfi", "-i", f"sine=frequency={hz_num}:duration=999999"]
    
    proc = subprocess.Popen([
        "ffmpeg", "-y",
        "-f", "concat", "-safe", "0", "-stream_loop", "-1", "-i", str(concat_f),
        *audio_src,
        "-c:v", "libx264", "-preset", "veryfast", "-tune", "stillimage",
        "-b:v", "3000k", "-maxrate", "3000k", "-bufsize", "6000k",
        "-g", "60", "-pix_fmt", "yuv420p",
        "-c:a", "aac", "-b:a", "192k", "-ar", "44100", "-ac", "2",
        "-f", "flv", RTMP_URL
    ])
    
    def bg(start=3):
        idx=start
        while proc.poll() is None:
            time.sleep(55)
            tema, insight = content[idx % len(content)]
            seed = int(hashlib.md5(f"{LANG_CODE}_{sk}_{idx}".encode()).hexdigest()[:8], 16)
            img_data = get_img(tema, color, seed)
            if img_data:
                img_p = TMP/f"bg_{sk}_{seed}.jpg"; img_p.write_bytes(img_data)
                sl = TMP/f"sl_{sk}_{idx}.mp4"
                if make_slide(img_p, hz_str, tema, insight, tc, brand, idx%len(content), len(content), sl):
                    with open(concat_f, "a") as f: f.write(f"file '{sl.resolve()}'\n")
                    print(f"  + {tema[:35]}")
            for old in sorted(TMP.glob(f"sl_{sk}_*.mp4"))[:-6]: old.unlink(missing_ok=True)
            idx += 1
    
    threading.Thread(target=bg, daemon=True).start()
    try: proc.wait()
    except KeyboardInterrupt: proc.terminate()

if __name__ == "__main__":
    run()
