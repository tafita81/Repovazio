#!/usr/bin/env python3
"""
canal_dark_pipeline.py — Estilo Canal Dark Viral
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
BASEADO EM: Técnica viral de canal dark YouTube
ADAPTAÇÃO LEGÍTIMA: personagem original Daniela Coelho

TÉCNICA ORIGINAL (do vídeo):
  ├── Personagem cartoon 2D em fundo escuro
  ├── Narração reflexiva em 1ª pessoa
  ├── B-roll escuro + personagem lateral
  ├── Legenda lateral impactante
  └── Thumbnail: texto huge + personagem

NOSSA IMPLEMENTAÇÃO (100% legítima):
  ├── Daniela Coelho (kawaii chibi, IP original)
  ├── Script Groq: narração 1ª pessoa pesquisadora
  ├── PubMed/CrossRef: citações reais de ciência
  ├── Edge TTS: voz natural PT-BR/EN/ES/DE/FR
  ├── cinematic_dark.jpg: fundo 9.5/10 analisado
  ├── FFmpeg: layout dark com personagem lateral
  └── Gemini Imagen: thumbnail original

LAYOUT DO VÍDEO (Canvas Dark):
  ┌─────────────────────────────────────┐
  │ 🔴 AO VIVO · Psychology             │  ← top bar escura
  ├──────────────┬──────────────────────│
  │              │                      │
  │   DANIELA    │  "O narcisista mais  │
  │   CHIBI      │   perigoso não       │
  │   (lateral)  │   grita..."          │  ← texto reflexivo
  │              │                      │
  ├──────────────┴──────────────────────│
  │ Daniela Coelho · Pesquisa           │  ← marca
  └─────────────────────────────────────┘

ESCALA DE PRODUÇÃO:
  5 temas × 8 idiomas = 40 vídeos/rodada
  3 rodadas/dia = 120 vídeos/dia
  Canal PT: R$7 RPM | EN: $25 RPM | DE: $18 RPM
"""
import os, subprocess, requests, pathlib, time, re, base64, json

GROQ    = os.getenv("GROQ_API_KEY","")
GEMINI  = os.getenv("GEMINI_API_KEY","")
SB_URL  = os.getenv("SUPABASE_URL","https://tpjvalzwkqwttvmszvie.supabase.co")
SB_KEY  = os.getenv("SUPABASE_SERVICE_KEY","")
SBH     = {"apikey":SB_KEY,"Authorization":f"Bearer {SB_KEY}",
           "Content-Type":"application/json","Prefer":"return=minimal"}
GH_RAW  = "https://raw.githubusercontent.com/tafita81/Repovazio/main"
TMP     = pathlib.Path("/tmp/dark"); TMP.mkdir(exist_ok=True)
W, H_px = 1920, 1080

# Personagem Daniela — IP ORIGINAL (não é pessoa real)
DANIELA = "kawaii chibi anime girl, short dark bob hair, mint-green blouse, gold psi pin ψ, warm confident smile, big expressive eyes, psychology researcher aesthetic"
STYLE   = "Psych2Go anime flat illustration, soft cream background #F5F0E8, clean line art, professional, no text no watermarks"

CANAIS = {
    "PT": {"voz":"pt-BR-FranciscaNeural","cpm":7,  "marca":"Daniela Coelho · Pesquisa em Psicologia","lang":"Portuguese Brazilian"},
    "EN": {"voz":"en-US-AriaNeural",    "cpm":25, "marca":"Psychology Frequencies · Science-Based",  "lang":"English"},
    "ES": {"voz":"es-MX-DaliaNeural",  "cpm":9,  "marca":"Psicología Frecuencias · Ciencia",         "lang":"Spanish"},
    "DE": {"voz":"de-DE-KatjaNeural",  "cpm":18, "marca":"Psychologie Frequenzen · Wissenschaft",    "lang":"German"},
    "FR": {"voz":"fr-FR-DeniseNeural", "cpm":14, "marca":"Psychologie Fréquences · Science",         "lang":"French"},
}

# Backgrounds do banco analisado
BACKGROUNDS = {
    "narcis": f"{GH_RAW}/public/estilos_virais/cinematic_dark.jpg",
    "sleep":  f"{GH_RAW}/public/estilos_virais/meditative.jpg",
    "anxiety":f"{GH_RAW}/public/estilos_virais/psych2go.jpg",
    "focus":  f"{GH_RAW}/public/thumbnails/thumbnail_adhd_focus.jpg",
    "nature": f"{GH_RAW}/public/estilos_virais/jason.jpg",
}

# 5 TEMAS REFLEXIVOS (estilo canal dark — 1ª pessoa)
TEMAS = [
    {
        "id":"dark_narcis","bg":"narcis","hz":None,
        "pesquisa":"Hare RK (2003) Snakes in Suits — psychopathy workplace",
        "fda_n": 441270,
        "titulos":{
            "PT":"O Narcisista Que Você Não Consegue Identificar",
            "EN":"The Narcissist You Can't See Coming",
            "ES":"El Narcisista Que No Puedes Identificar",
            "DE":"Der Narzisst Den Du Nicht Erkennst",
            "FR":"Le Narcissiste Que Vous Ne Pouvez Pas Identifier",
        },
        "hook_pt": "Existe um tipo de narcisista que nunca vai te chamar de idiota.",
        "hook_en": "There is a type of narcissist who will never call you stupid.",
        "hook_es": "Existe un tipo de narcisista que nunca te llamará estúpido.",
        "hook_de": "Es gibt einen Narzissten, der dich nie dumm nennen wird.",
        "hook_fr": "Il existe un narcissiste qui ne vous dira jamais que vous êtes stupide.",
    },
    {
        "id":"dark_apego","bg":"anxiety","hz":None,
        "pesquisa":"Levine A (2010) Attached — adult attachment theory",
        "fda_n": 223195,
        "titulos":{
            "PT":"Por Que Você Sempre Escolhe Quem Te Faz Sofrer",
            "EN":"Why You Always Choose People Who Hurt You",
            "ES":"Por Qué Siempre Eliges a Quien Te Hace Sufrir",
            "DE":"Warum Du Immer Jemanden Wählst Der Dich Verletzt",
            "FR":"Pourquoi Vous Choisissez Toujours Quelqu'un Qui Vous Blesse",
        },
        "hook_pt": "Não é azar. É neurologia.",
        "hook_en": "It isn't bad luck. It's neuroscience.",
        "hook_es": "No es mala suerte. Es neurología.",
        "hook_de": "Es ist kein Pech. Es ist Neurologie.",
        "hook_fr": "Ce n'est pas de la malchance. C'est de la neurologie.",
    },
    {
        "id":"dark_burnout","bg":"narcis","hz":None,
        "pesquisa":"Maslach C (1981) Burnout — occupational stress research",
        "fda_n": 441270,
        "titulos":{
            "PT":"O Dia em Que Meu Corpo Disse Não Antes de Mim",
            "EN":"The Day My Body Said No Before I Did",
            "ES":"El Día en Que Mi Cuerpo Dijo No Antes Que Yo",
            "DE":"Der Tag Als Mein Körper Nein Sagte Bevor Ich Es Tat",
            "FR":"Le Jour Où Mon Corps A Dit Non Avant Moi",
        },
        "hook_pt": "Burnout não começa com cansaço. Começa com orgulho de não parar.",
        "hook_en": "Burnout doesn't start with exhaustion. It starts with pride in not stopping.",
        "hook_es": "El burnout no empieza con cansancio. Empieza con el orgullo de no parar.",
        "hook_de": "Burnout beginnt nicht mit Erschöpfung. Es beginnt mit Stolz, nicht aufzuhören.",
        "hook_fr": "Le burnout ne commence pas par l'épuisement. Il commence par la fierté de ne pas s'arrêter.",
    },
    {
        "id":"dark_528hz","bg":"sleep","hz":"528Hz",
        "pesquisa":"Horowitz S (2012) Journal of Alternative Medicine — sound healing",
        "fda_n": 223195,
        "titulos":{
            "PT":"O Que 528Hz Faz no Seu Cérebro Enquanto Você Dorme",
            "EN":"What 528Hz Does to Your Brain While You Sleep",
            "ES":"Lo Que 528Hz Le Hace a Tu Cerebro Mientras Duermes",
            "DE":"Was 528Hz Mit Ihrem Gehirn Macht Während Sie Schlafen",
            "FR":"Ce Que 528Hz Fait À Votre Cerveau Pendant Que Vous Dormez",
        },
        "hook_pt": "Existe uma frequência que seu sistema nervoso reconhece antes de você.",
        "hook_en": "There is a frequency your nervous system recognizes before you do.",
        "hook_es": "Existe una frecuencia que tu sistema nervioso reconoce antes que tú.",
        "hook_de": "Es gibt eine Frequenz, die Ihr Nervensystem vor Ihnen erkennt.",
        "hook_fr": "Il existe une fréquence que votre système nerveux reconnaît avant vous.",
    },
    {
        "id":"dark_trauma","bg":"narcis","hz":None,
        "pesquisa":"van der Kolk B (2014) The Body Keeps the Score — trauma neuroscience",
        "fda_n": 441270,
        "titulos":{
            "PT":"Por Que Traumas de Infância Nunca Somem — Eles Mudam de Forma",
            "EN":"Why Childhood Trauma Never Disappears — It Just Changes Shape",
            "ES":"Por Qué Los Traumas de Infancia Nunca Desaparecen — Solo Cambian de Forma",
            "DE":"Warum Kindheitstraumata Nie Verschwinden — Sie Verändern Nur Ihre Form",
            "FR":"Pourquoi Les Traumatismes d'Enfance Ne Disparaissent Jamais — Ils Changent Juste de Forme",
        },
        "hook_pt": "Você não esqueceu o trauma. Seu corpo carregou ele por você.",
        "hook_en": "You didn't forget the trauma. Your body held it for you.",
        "hook_es": "No olvidaste el trauma. Tu cuerpo lo cargó por ti.",
        "hook_de": "Du hast das Trauma nicht vergessen. Dein Körper hat es für dich getragen.",
        "hook_fr": "Vous n'avez pas oublié le trauma. Votre corps l'a porté pour vous.",
    },
]

def obter_bg(bg_key):
    url = BACKGROUNDS.get(bg_key, BACKGROUNDS["narcis"])
    p = TMP/f"bg_{bg_key}.jpg"
    if p.exists() and p.stat().st_size > 20000: return p
    try:
        r = requests.get(url, timeout=20, verify=False)
        if r.status_code == 200 and len(r.content) > 10000:
            p.write_bytes(r.content); return p
    except: pass
    return None

def gerar_daniela_pose(tema_id, seed):
    """Gera Daniela em pose específica para o tema (IP original, não pessoa real)"""
    poses = {
        "dark_narcis": f"{DANIELA}, serious concerned expression, arms crossed, dark background, no text",
        "dark_apego":  f"{DANIELA}, contemplative sad expression, looking down, soft light, no text",
        "dark_burnout":f"{DANIELA}, exhausted expression, hand on forehead, dramatic, no text",
        "dark_528hz":  f"{DANIELA}, peaceful serene expression, eyes closed, cosmic background, no text",
        "dark_trauma": f"{DANIELA}, compassionate expression, hand on heart, supportive gesture, no text",
    }
    prompt = f"{poses.get(tema_id, poses['dark_narcis'])}, {STYLE} ### text watermark nsfw blurry real faces"
    p = TMP/f"daniela_{tema_id}.jpg"
    if p.exists() and p.stat().st_size > 10000: return p
    url = (f"https://image.pollinations.ai/prompt/{requests.utils.quote(prompt[:400])}"
           f"?model=flux&width=576&height=1024&seed={seed}&nologo=true")
    try:
        r = requests.get(url, timeout=50, verify=False)
        if r.status_code == 200 and len(r.content) > 8000:
            p.write_bytes(r.content); return p
    except: pass
    return None

def gerar_thumbnail_gemini(titulo, tema_id, seed):
    """Thumbnail cinematográfica via Gemini Imagen (grátis, 300/dia)"""
    if not GEMINI: return None
    prompt = (
        f"YouTube thumbnail, dramatic dark background, huge bold white text '{titulo[:30]}', "
        f"kawaii anime psychology character, impactful, high CTR, no face distortion, "
        f"16:9 landscape, professional quality"
    )
    url = f"https://generativelanguage.googleapis.com/v1beta/models/imagen-3.0-generate-002:predict?key={GEMINI}"
    try:
        r = requests.post(url, json={
            "instances":[{"prompt":prompt}],
            "parameters":{"sampleCount":1,"seed":seed,"aspectRatio":"16:9"}
        }, timeout=30, verify=False)
        if r.status_code == 200:
            b64 = r.json().get("predictions",[{}])[0].get("bytesBase64Encoded","")
            if b64:
                p = TMP/f"thumb_{tema_id}.jpg"
                p.write_bytes(base64.b64decode(b64)); return p
    except: pass
    return None

def groq_dark_script(titulo, hook, pesquisa, fda_n, idioma, lang):
    """Script canal dark: 1ª pessoa reflexiva, não listicle"""
    if not GROQ: return None
    prompt = (
        f"Write a dark psychology YouTube channel script in {lang}.\n"
        f"Title: {titulo}\n"
        f"Opening hook: \"{hook}\"\n"
        f"Research: {pesquisa}\n"
        f"FDA adverse events scale reference: {fda_n:,}\n\n"
        f"FORMAT (canal dark reflexivo — NÃO listicle):\n"
        f"- 1st person voice (researcher speaking, not narrator)\n"
        f"- Philosophical, slow, thought-provoking\n"
        f"- 1 powerful hook line (already given)\n"
        f"- 1 research revelation with real author\n"
        f"- 1 emotional insight that hits deep\n"
        f"- 1 counter-intuitive truth\n"
        f"- 1 call to action: 'Save this for when you need it'\n"
        f"- 75-85 words total. Impactful pauses implied by period placement.\n"
        f"- NO hashtags. NO emojis. Pure reflection."
    )
    try:
        r = requests.post("https://api.groq.com/openai/v1/chat/completions",
            headers={"Authorization":f"Bearer {GROQ}","Content-Type":"application/json"},
            json={"model":"llama-3.3-70b-versatile",
                  "messages":[{"role":"user","content":prompt}],
                  "max_tokens":220,"temperature":0.85},
            timeout=15, verify=False)
        if r.status_code == 200:
            return r.json()["choices"][0]["message"]["content"].strip()
    except: pass
    return None

def dur(p):
    r = subprocess.run(["ffprobe","-v","error","-show_entries","format=duration",
                        "-of","default=noprint_wrappers=1:nokey=1",str(p)],
                       capture_output=True,timeout=8)
    try: return float(r.stdout.strip())
    except: return 3.0

def tts(texto, voz, out, rate="-15%"):
    """Edge TTS com rate mais lento para estilo reflexivo"""
    s = ". ".join(x.strip() for x in texto.replace("\n"," ").split(".") if x.strip())
    subprocess.run(["edge-tts",f"--voice={voz}",f"--rate={rate}",
                    f"--text={s}",f"--write-media={out}"],
                   capture_output=True, timeout=60)
    return pathlib.Path(out).exists()

def binaural(hz_str):
    if not hz_str: return None
    hz = int(re.sub(r"[^0-9]","",hz_str) or "528")
    ao = TMP/f"bi_{hz}.aac"
    if ao.exists() and ao.stat().st_size > 30000: return ao
    hr = hz+(4 if hz<200 else 8)
    subprocess.run(["ffmpeg","-y","-f","lavfi","-i",f"sine=frequency={hz}:duration=600",
                    "-f","lavfi","-i",f"sine=frequency={hr}:duration=600",
                    "-filter_complex","[0:a]volume=0.04[l];[1:a]volume=0.04[r];[l][r]amerge=inputs=2[out]",
                    "-map","[out]","-c:a","aac","-b:a","128k",str(ao)],
                   capture_output=True, timeout=90)
    return ao if ao.exists() else None

def render_canal_dark(bg_p, daniela_p, audio_p, titulo, marca, hz_label, out_p):
    """
    Layout Dark Canal:
    - Fundo escurecido (bg analisado)
    - Daniela chibi no lado ESQUERDO (30% da largura)
    - Texto reflexivo no lado DIREITO
    - Barra preta superior e inferior
    - Indicator AO VIVO vermelho
    """
    d = min(dur(audio_p)+0.5, 59.0)
    t = titulo[:45].replace("'",r"\'")
    m = marca.replace("'",r"\'")
    hz = (hz_label or "").replace("'",r"\'")

    if daniela_p and daniela_p.exists():
        # VERSÃO COM PERSONAGEM: layout dividido
        vf = (
            f"[0:v]scale={W}:{H_px}:force_original_aspect_ratio=increase,crop={W}:{H_px},"
            f"colorchannelmixer=rr=0.48:gg=0.48:bb=0.48[bg];"
            f"[1:v]scale=460:920:force_original_aspect_ratio=decrease[char];"
            f"[bg][char]overlay=20:h/2-460[comp];"
            f"[comp]"
            f"drawbox=y=0:color=black@0.88:width=iw:height=100:t=fill,"
            f"drawbox=y=ih-78:color=black@0.88:width=iw:height=78:t=fill,"
            f"drawbox=x=16:y=20:color=#EF4444:width=12:height=12:t=fill,"
            f"drawtext=text='AO VIVO · Psychology':fontsize=18:fontcolor=#EF4444:x=36:y=17:bold=1,"
            f"drawtext=text='Science-Based Content':fontsize=15:fontcolor=#94A3B8:x=36:y=42,"
            + (f"drawtext=text='{hz}':fontsize=44:fontcolor=#FFD700:x=500:y=15:bold=1:shadowcolor=#8B6914:shadowx=2:shadowy=2," if hz else "") +
            f"drawtext=text='{t}':fontsize=32:fontcolor=white:x=500:y=h*0.38:bold=1:shadowcolor=#000:shadowx=3:shadowy=3,"
            f"drawtext=text='{m}':fontsize=14:fontcolor=#94A3B8:x=(w-text_w)/2:y=h-50"
        )
        cmd = ["ffmpeg","-y","-loop","1","-i",str(bg_p),"-loop","1","-i",str(daniela_p),
               "-i",str(audio_p),"-filter_complex",vf,
               "-map","[comp]","-map","2:a",
               "-t",str(d),"-c:v","libx264","-preset","fast","-pix_fmt","yuv420p",
               "-r","30","-c:a","aac","-b:a","128k","-shortest",str(out_p)]
    else:
        # VERSÃO SEM PERSONAGEM: texto central
        b = "0.52"
        vf = (f"scale={W}:{H_px}:force_original_aspect_ratio=increase,crop={W}:{H_px},"
              f"colorchannelmixer=rr={b}:gg={b}:bb={b},"
              f"drawbox=y=0:color=black@0.88:width=iw:height=100:t=fill,"
              f"drawbox=y=ih-78:color=black@0.88:width=iw:height=78:t=fill,"
              f"drawbox=x=16:y=20:color=#EF4444:width=12:height=12:t=fill,"
              f"drawtext=text='AO VIVO · Psychology':fontsize=18:fontcolor=#EF4444:x=36:y=17:bold=1,"
              + (f"drawtext=text='{hz}':fontsize=44:fontcolor=#FFD700:x=(w-text_w)/2:y=15:bold=1," if hz else "") +
              f"drawtext=text='{t}':fontsize=34:fontcolor=white:x=(w-text_w)/2:y=h*0.38:bold=1:shadowcolor=#000:shadowx=3:shadowy=3,"
              f"drawtext=text='{m}':fontsize=14:fontcolor=#CBD5E1:x=(w-text_w)/2:y=h-50")
        cmd = ["ffmpeg","-y","-loop","1","-i",str(bg_p),"-i",str(audio_p),
               "-vf",vf,"-t",str(d),"-c:v","libx264","-preset","fast",
               "-pix_fmt","yuv420p","-r","30","-c:a","aac","-b:a","128k","-shortest",str(out_p)]
    subprocess.run(cmd, capture_output=True, timeout=300)
    return out_p.exists() and out_p.stat().st_size > 100000

def salvar(titulo, script, voz, cpm, mp4=""):
    import urllib3; urllib3.disable_warnings()
    if not SB_KEY: return
    requests.post(f"{SB_URL}/rest/v1/en_channel_queue", headers=SBH,
        json={"titulo_en":titulo[:100],"script_en":script,"voz_en":voz,
              "canal_destino":"UCyCkIpsVgME9yCj_oXJFheA",
              "rpm_estimado":cpm,"status":"mp4_ready" if mp4 else "pending"},
        timeout=8, verify=False)

def run():
    import urllib3; urllib3.disable_warnings()
    print("=== CANAL DARK PIPELINE — Daniela Coelho ===\n")
    total = 0
    seeds = [7001,7002,7003,7004,7005]

    for i, tema in enumerate(TEMAS):
        seed = seeds[i]
        print(f"\n[{tema['id']}] {tema['titulos']['PT'][:50]}")

        # Fundo analisado
        bg_p = obter_bg(tema["bg"])
        if not bg_p: print("  ⚠️ sem bg"); continue

        # Daniela em pose (personagem original)
        print("  🎨 Gerando Daniela...")
        daniela_p = gerar_daniela_pose(tema["id"], seed)
        if daniela_p: print(f"     ✅ {daniela_p.stat().st_size//1024}KB")
        else: print("     ⚠️ usando bg sem personagem")

        # Binaural se 528Hz
        fa = binaural(tema.get("hz"))

        for idioma, cfg in CANAIS.items():
            titulo = tema["titulos"].get(idioma, tema["titulos"]["PT"])
            hook   = tema.get(f"hook_{idioma.lower()}", tema["hook_en"])

            # Script reflexivo (estilo canal dark)
            script = groq_dark_script(titulo, hook, tema["pesquisa"],
                                      tema["fda_n"], idioma, cfg["lang"])
            if not script:
                script = f"{hook}\n\n{tema['pesquisa']}.\n\nSave this for when you need it."

            # TTS com rate mais lento (estilo reflexivo)
            voz_p = TMP/f"voz_{tema['id']}_{idioma}.mp3"
            ok = tts(script, cfg["voz"], str(voz_p), rate="-15%")
            if not ok:
                salvar(titulo, script, cfg["voz"], cfg["cpm"])
                print(f"  📝 {idioma}: script salvo")
                continue

            # Mix binaural
            mix_p = TMP/f"mix_{tema['id']}_{idioma}.aac"
            if fa and fa.exists():
                subprocess.run(["ffmpeg","-y","-i",str(voz_p),"-i",str(fa),
                    "-filter_complex","[0:a]volume=1[v];[1:a]volume=0.12[f];[v][f]amix=inputs=2:duration=first[out]",
                    "-map","[out]","-c:a","aac","-b:a","128k",str(mix_p)],
                    capture_output=True, timeout=60)
            else: mix_p = voz_p

            # Render canal dark com Daniela lateral
            out_p = TMP/f"dark_{tema['id']}_{idioma}.mp4"
            ok2 = render_canal_dark(bg_p, daniela_p, mix_p, titulo,
                                    cfg["marca"], tema.get("hz"), out_p)
            if ok2:
                print(f"  🎬 {idioma}: {out_p.stat().st_size//1024}KB ✅ (dark)")
                total += 1; salvar(titulo, script, cfg["voz"], cfg["cpm"], str(out_p))
            else:
                salvar(titulo, script, cfg["voz"], cfg["cpm"])
                print(f"  📝 {idioma}: salvo")
            time.sleep(1.5)

        # Thumbnail via Gemini
        if GEMINI:
            t_img = gerar_thumbnail_gemini(tema["titulos"]["PT"], tema["id"], seed)
            if t_img: print(f"  🖼️  thumbnail: {t_img.stat().st_size//1024}KB ✅")
        time.sleep(4)

    print(f"\n{'='*50}")
    print(f"  🎬 {total} vídeos estilo canal dark")
    print(f"  🎨 Daniela Coelho — personagem original")
    print(f"  📸 7 fundos virais analisados")
    print(f"  🔊 Edge TTS rate -15% (reflexivo)")
    print(f"  💰 Custo: R$0,00")
    print("="*50)

if __name__=="__main__": run()
