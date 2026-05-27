#!/usr/bin/env python3
"""
live_black_screen.py — TELA PRETA TOTAL + Psicologia para Dormir
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

INOVAÇÃO MUNDIAL:
  - Frame 100% preto (#000000) — zero luz no dispositivo
  - Áudio psicologia + binaurais gerados por IA
  - Watch time 6-8h por viewer (ninguém desliga dormindo)
  - Bitrate vídeo: 150kbps (preto puro = quase zero dado)
  - Bitrate áudio: 192kbps (qualidade máxima)

MATEMÁTICA:
  50 viewers × 7h sono × 7 noites = 2.450 watch hours/semana
  Threshold YPP = 4.000h → bate em ~11 dias com 50 viewers noturnos

Canal: @psidanicoelho (UCSH63tBfY6wEIdkC4u4zKdg)
"""
import os, time, subprocess, pathlib, requests, textwrap, threading, tempfile
from datetime import datetime, timezone, timedelta
import asyncio, edge_tts

LANG_CODE  = os.getenv("LANG_CODE", "PT").upper()
STREAM_KEY = os.getenv("YOUTUBE_STREAM_KEY", "")
GROQ_KEY   = os.getenv("GROQ_API_KEY", "")
RTMP_URL   = f"rtmp://a.rtmp.youtube.com/live2/{STREAM_KEY}"
TMP = pathlib.Path(f"/tmp/black_{LANG_CODE.lower()}"); TMP.mkdir(exist_ok=True)

TZ_OFFSETS = {
    "PT": -3, "EN": -5, "ES": -4, "FR": 1,
    "DE": 1,  "IT": 1,  "JA": 9, "KO": 9, "AR": 3
}

VOICES = {
    "PT": "pt-BR-AntonioNeural",
    "EN": "en-US-GuyNeural",
    "ES": "es-ES-AlvaroNeural",
    "FR": "fr-FR-HenriNeural",
    "DE": "de-DE-ConradNeural",
    "IT": "it-IT-DiegoNeural",
    "JA": "ja-JP-KeitaNeural",
    "KO": "ko-KR-InJoonNeural",
    "AR": "ar-SA-HamedNeural",
}

# Conteúdo noturno por idioma — otimizado para sono/reflexão pré-sono
SLEEP_CONTENT = {
    "PT": {
        "title": "Psicologia para Dormir 🖤 Tela Preta | Daniela Coelho",
        "scripts": [
            "Enquanto você fecha os olhos agora, seu cérebro começa a processar as emoções do dia. "
            "Van der Kolk descobriu que o sono é quando o trauma se reorganiza. "
            "Você não precisa resolver tudo hoje. O silêncio já é cura.",

            "O apego ansioso cria hipervigilância noturna. "
            "Seu sistema nervoso aprende que o silêncio é seguro. "
            "Ainsworth mostrou que segurança é aprendida — e você está aprendendo agora, neste momento.",

            "Narcisismo encoberto se alimenta da sua exaustão. "
            "À noite, longe do caos, sua mente começa a ver com clareza. "
            "Malkin da Harvard diz: a recuperação começa no silêncio.",

            "Três sinais de que você está processando trauma enquanto dorme: "
            "sonhos vívidos, acordar às três da manhã, sensação de peso no peito ao despertar. "
            "Van der Kolk chama isso de cura em andamento.",

            "Cortisol alto bloqueia melatonina. "
            "Sapolsky descobriu que o simples ato de respirar devagar por quatro segundos "
            "já começa a reverter o ciclo do estresse. Respire. Você está seguro agora.",
        ]
    },
    "EN": {
        "title": "Sleep Psychology 🖤 Black Screen | Dark Thoughts Before Sleep",
        "scripts": [
            "As you close your eyes now, your brain begins processing today's emotions. "
            "Van der Kolk found that sleep is when trauma reorganizes itself. "
            "You don't need to solve everything tonight. The silence itself is healing.",

            "Anxious attachment creates nighttime hypervigilance. "
            "Your nervous system is learning that silence is safe. "
            "Ainsworth showed that security is learned — and you are learning it right now.",

            "Covert narcissism feeds on your exhaustion. "
            "At night, away from the chaos, your mind begins to see clearly. "
            "Malkin at Harvard says recovery begins in silence.",

            "Three signs you are processing trauma during sleep: "
            "vivid dreams, waking at 3am, feeling heavy upon waking. "
            "Van der Kolk calls this healing in progress.",

            "High cortisol blocks melatonin. "
            "Sapolsky found that simply breathing slowly for four seconds "
            "already begins reversing the stress cycle. Breathe. You are safe now.",
        ]
    },
    "ES": {
        "title": "Psicología para Dormir 🖤 Pantalla Negra | Daniela Coelho",
        "scripts": [
            "Mientras cierras los ojos ahora, tu cerebro comienza a procesar las emociones del día. "
            "Van der Kolk descubrió que el sueño es cuando el trauma se reorganiza. "
            "No necesitas resolver todo hoy. El silencio ya es curación.",

            "El apego ansioso crea hipervigilancia nocturna. "
            "Tu sistema nervioso aprende que el silencio es seguro. "
            "Ainsworth mostró que la seguridad se aprende — y tú estás aprendiendo ahora.",

            "El narcisismo encubierto se alimenta de tu agotamiento. "
            "Por la noche, lejos del caos, tu mente comienza a ver con claridad. "
            "Malkin de Harvard dice: la recuperación comienza en el silencio.",

            "El cortisol alto bloquea la melatonina. "
            "Sapolsky descubrió que simplemente respirar lento por cuatro segundos "
            "ya comienza a revertir el ciclo del estrés. Respira. Estás seguro ahora.",
        ]
    },
    "FR": {
        "title": "Psychologie du Sommeil 🖤 Écran Noir | Daniela Coelho",
        "scripts": [
            "Alors que vous fermez les yeux maintenant, votre cerveau commence à traiter les émotions de la journée. "
            "Van der Kolk a découvert que le sommeil est le moment où le traumatisme se réorganise. "
            "Vous n'avez pas besoin de tout résoudre ce soir. Le silence lui-même est guérison.",

            "L'attachement anxieux crée une hypervigilance nocturne. "
            "Votre système nerveux apprend que le silence est sûr. "
            "Ainsworth a montré que la sécurité s'apprend — et vous l'apprenez maintenant.",

            "Le narcissisme masqué se nourrit de votre épuisement. "
            "La nuit, loin du chaos, votre esprit commence à voir clairement. "
            "Malkin de Harvard dit: la guérison commence dans le silence.",
        ]
    },
    "DE": {
        "title": "Schlafpsychologie 🖤 Schwarzer Bildschirm | Daniela Coelho",
        "scripts": [
            "Während Sie jetzt die Augen schließen, beginnt Ihr Gehirn, die Emotionen des Tages zu verarbeiten. "
            "Van der Kolk fand heraus, dass Schlaf der Moment ist, in dem Trauma sich neu organisiert. "
            "Sie müssen heute Abend nicht alles lösen. Die Stille selbst ist Heilung.",

            "Ängstliche Bindung erzeugt nächtliche Hypervigilanz. "
            "Ihr Nervensystem lernt, dass Stille sicher ist. "
            "Ainsworth zeigte, dass Sicherheit erlernt wird — und Sie lernen es gerade jetzt.",

            "Verdeckter Narzissmus nährt sich von Ihrer Erschöpfung. "
            "Nachts, weg vom Chaos, beginnt Ihr Geist klar zu sehen. "
            "Malkin von Harvard sagt: Heilung beginnt in der Stille.",
        ]
    },
    "IT": {
        "title": "Psicologia del Sonno 🖤 Schermo Nero | Daniela Coelho",
        "scripts": [
            "Mentre chiudi gli occhi ora, il tuo cervello inizia a elaborare le emozioni della giornata. "
            "Van der Kolk ha scoperto che il sonno è il momento in cui il trauma si riorganizza. "
            "Non hai bisogno di risolvere tutto stasera. Il silenzio stesso è guarigione.",

            "L'attaccamento ansioso crea ipervigilanza notturna. "
            "Il tuo sistema nervoso impara che il silenzio è sicuro. "
            "Ainsworth ha dimostrato che la sicurezza si apprende — e tu la stai imparando adesso.",
        ]
    },
    "JA": {
        "title": "眠りの心理学 🖤 黒い画面 | 行動研究者ダニエラ",
        "scripts": [
            "目を閉じる今、あなたの脳は今日の感情を処理し始めています。"
            "ヴァン・デア・コークは、睡眠がトラウマが再編成される時だと発見しました。"
            "今夜すべてを解決する必要はありません。沈黙それ自体が癒しです。",

            "不安型愛着は夜間の過覚醒を生み出します。"
            "あなたの神経系は沈黙が安全だということを学んでいます。"
            "エインズワースは安全感は学ばれるものだと示しました。今、あなたはそれを学んでいます。",
        ]
    },
    "KO": {
        "title": "수면 심리학 🖤 검은 화면 | 다니엘라 코엘류",
        "scripts": [
            "지금 눈을 감으면서 당신의 뇌는 오늘의 감정을 처리하기 시작합니다. "
            "반 데어 코크는 수면이 트라우마가 재편되는 시간임을 발견했습니다. "
            "오늘 밤 모든 것을 해결할 필요는 없습니다. 침묵 자체가 치유입니다.",

            "불안 애착은 야간 과각성을 만듭니다. "
            "당신의 신경계는 침묵이 안전하다는 것을 배우고 있습니다. "
            "에인스워스는 안전감이 배워지는 것임을 보여주었습니다.",
        ]
    },
    "AR": {
        "title": "علم نفس النوم 🖤 شاشة سوداء | دانييلا كويلو",
        "scripts": [
            "بينما تغمض عينيك الآن، يبدأ دماغك في معالجة مشاعر اليوم. "
            "اكتشف فان دير كولك أن النوم هو الوقت الذي يعيد فيه الصدمة تنظيم نفسها. "
            "لا تحتاج إلى حل كل شيء الليلة. الصمت نفسه شفاء.",

            "التعلق القلق يخلق فرط اليقظة الليلية. "
            "جهازك العصبي يتعلم أن الصمت آمن. "
            "أثبتت أينسورث أن الأمان يُتعلم — وأنت تتعلمه الآن.",
        ]
    },
}

def gen_binaural(hz=528, mins=30):
    """Gera áudio binaural (Hz esquerda + Hz+4 direita) + ruído rosa suave"""
    out = TMP / f"binaural_{hz}.aac"
    if out.exists() and out.stat().st_size > 50000: return out
    dur = mins * 60
    cmd = ["ffmpeg", "-y",
        "-f","lavfi","-i",f"sine=frequency={hz}:duration={dur}",
        "-f","lavfi","-i",f"sine=frequency={hz+4}:duration={dur}",
        "-f","lavfi","-i",f"anoisesrc=color=pink:duration={dur}",
        "-filter_complex",
        "[0:a]volume=0.04[l];[1:a]volume=0.04[r];"
        "[l][r]amerge=inputs=2[bin];[2:a]volume=0.003[p];"
        "[bin][p]amix=inputs=2:duration=longest[out]",
        "-map","[out]","-c:a","aac","-b:a","192k","-ar","44100", str(out)]
    subprocess.run(cmd, capture_output=True, timeout=120)
    return out if out.exists() else None

async def gen_tts(text, voice, outpath):
    """Edge TTS: gera fala em arquivo mp3"""
    communicate = edge_tts.Communicate(text, voice, rate="+0%")
    await communicate.save(str(outpath))

def gen_speech_segment(text, lang, idx):
    """Gera segmento TTS + binaural mesclados"""
    voice = VOICES.get(lang, "en-US-GuyNeural")
    speech_f = TMP / f"speech_{idx}.mp3"
    mixed_f  = TMP / f"mixed_{idx}.aac"

    # Gera TTS
    asyncio.run(gen_tts(text, voice, speech_f))
    if not speech_f.exists(): return None

    # Mescla TTS + binaural suave
    binaural = gen_binaural(528, 5)
    if binaural and binaural.exists():
        cmd = ["ffmpeg","-y",
            "-i", str(speech_f),
            "-stream_loop","-1","-i", str(binaural),
            "-filter_complex","[0:a]volume=1.0[s];[1:a]volume=0.15[b];[s][b]amix=inputs=2:duration=first[out]",
            "-map","[out]","-c:a","aac","-b:a","192k","-ar","44100", str(mixed_f)]
    else:
        cmd = ["ffmpeg","-y","-i",str(speech_f),"-c:a","aac","-b:a","192k", str(mixed_f)]

    subprocess.run(cmd, capture_output=True, timeout=60)
    return mixed_f if mixed_f.exists() else None

def create_black_frame():
    """Cria frame preto puro 1280x720"""
    frame = TMP / "black_frame.jpg"
    if not frame.exists():
        cmd = ["ffmpeg","-y","-f","lavfi","-i","color=c=black:size=1280x720:rate=1",
               "-frames:v","1", str(frame)]
        subprocess.run(cmd, capture_output=True)
    return frame

def run():
    if not STREAM_KEY:
        print("ERRO: YOUTUBE_STREAM_KEY não configurado"); return

    data     = SLEEP_CONTENT.get(LANG_CODE, SLEEP_CONTENT["EN"])
    scripts  = data["scripts"]
    title    = data["title"]
    print(f"=== 🖤 BLACK SCREEN LIVE {LANG_CODE} ===")
    print(f"    {title}")

    black = create_black_frame()
    audio_files = []

    # Gera todos os segmentos de áudio
    for i, text in enumerate(scripts):
        print(f"  🎙️ [{i+1}/{len(scripts)}] Gerando áudio...")
        af = gen_speech_segment(text, LANG_CODE, i)
        if af: audio_files.append(af)
        time.sleep(1)

    if not audio_files:
        print("ERRO: nenhum áudio gerado"); return

    # Cria playlist de áudio concatenada
    concat_audio = TMP / "concat_audio.txt"
    with open(concat_audio, "w") as f:
        for i in range(99):  # loop ~99x para duração máxima de 6h
            for af in audio_files:
                f.write(f"file '{af.resolve()}'\n")

    # Stream tela preta + áudio para YouTube
    # Bitrate de vídeo mínimo (preto puro = quase 0 dados reais)
    print(f"\n🔴 Iniciando stream para YouTube...")
    print(f"   URL RTMP: {RTMP_URL[:40]}...")

    proc = subprocess.Popen([
        "ffmpeg", "-y",
        # Vídeo: frame preto em loop
        "-loop","1","-i", str(black),
        # Áudio: segmentos concatenados em loop
        "-f","concat","-safe","0","-i", str(concat_audio),
        # Video encoding: mínimo bitrate (preto = comprime para quase 0)
        "-c:v","libx264","-preset","ultrafast","-tune","stillimage",
        "-b:v","150k","-maxrate","200k","-bufsize","400k",
        "-g","30","-pix_fmt","yuv420p","-r","5",
        # Audio: qualidade máxima
        "-c:a","aac","-b:a","192k","-ar","44100","-ac","2",
        # Formato stream
        "-f","flv", RTMP_URL
    ], capture_output=False)

    # Background: regenera áudio continuamente com novos tópicos (via Groq)
    def refresh_audio():
        idx = len(scripts)
        while proc.poll() is None:
            time.sleep(300)  # a cada 5min gera novo script
            if not GROQ_KEY: continue
            try:
                lang_prompts = {
                    "PT": f"Gere 3 frases calmas sobre psicologia do sono para ouvir dormindo. Cite van der Kolk ou Ainsworth. Voz suave. Máx 60 palavras. SEM 'psicóloga'.",
                    "EN": f"Generate 3 calm psychology sleep insights to listen to while sleeping. Cite van der Kolk or Ainsworth. Soft voice. Max 60 words.",
                    "ES": f"Genera 3 ideas calmadas sobre psicología del sueño para escuchar durmiendo. Cita a van der Kolk o Ainsworth. Máx 60 palabras.",
                    "FR": f"Générez 3 insights calmes sur la psychologie du sommeil. Citez van der Kolk ou Ainsworth. Maximum 60 mots.",
                    "DE": f"Erstellen Sie 3 ruhige Schlafpsychologie-Einblicke zum Einschlafen. Zitieren Sie van der Kolk oder Ainsworth. Max 60 Wörter.",
                    "IT": f"Genera 3 insight calmi di psicologia del sonno da ascoltare dormendo. Cita van der Kolk o Ainsworth. Max 60 parole.",
                    "JA": f"眠りながら聞く睡眠心理学の穏やかな3つの洞察を生成してください。ヴァン・デア・コークを引用。60語以内。",
                    "KO": f"잠자는 동안 들을 수면 심리학 인사이트 3가지를 생성하세요. 반 데어 코크 인용. 최대 60단어.",
                    "AR": f"أنشئ 3 رؤى هادئة عن علم نفس النوم للاستماع أثناء النوم. اقتبس من فان دير كولك. أقصاه 60 كلمة.",
                }
                prompt = lang_prompts.get(LANG_CODE, lang_prompts["EN"])
                r = requests.post("https://api.groq.com/openai/v1/chat/completions",
                    headers={"Authorization":f"Bearer {GROQ_KEY}","Content-Type":"application/json"},
                    json={"model":"llama-3.3-70b-versatile","messages":[{"role":"user","content":prompt}],
                          "max_tokens":120,"temperature":0.7},
                    timeout=12, verify=False)
                if r.status_code == 200:
                    new_text = r.json()["choices"][0]["message"]["content"].strip()
                    af = gen_speech_segment(new_text, LANG_CODE, idx)
                    if af:
                        with open(concat_audio, "a") as f:
                            f.write(f"file '{af.resolve()}'\n")
                        print(f"  🆕 Novo segmento {idx}")
                    idx += 1
            except: pass

    threading.Thread(target=refresh_audio, daemon=True).start()

    try: proc.wait()
    except KeyboardInterrupt: proc.terminate()
    print("Stream encerrado.")

if __name__ == "__main__":
    run()
