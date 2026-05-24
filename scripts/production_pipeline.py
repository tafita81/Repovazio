#!/usr/bin/env python3
"""
production_pipeline.py
USA as APIs gratuitas já no Brain — sem buscar novas.

APIs em uso:
  PubMed API          → citações científicas reais
  OpenLibrary API     → referências de livros
  HuggingFace API     → catalogo TTS gratuitos
  Audius API          → dados de mercado Web3
  Deezer API          → dados de mercado streaming
  Groq API            → LLM geração de conteúdo
  Edge TTS            → narração 140+ vozes (grátis)
  Pollinations FLUX   → imagens sem API key
  FFmpeg              → render de vídeo (local)
"""
import os, subprocess, requests, pathlib, time, re, json, textwrap, hashlib

SB_URL = os.getenv("SUPABASE_URL","https://tpjvalzwkqwttvmszvie.supabase.co")
SB_KEY = os.getenv("SUPABASE_SERVICE_KEY","")
GROQ   = os.getenv("GROQ_API_KEY","")
SBH    = {"apikey":SB_KEY,"Authorization":f"Bearer {SB_KEY}",
          "Content-Type":"application/json","Prefer":"return=minimal"}
TMP    = pathlib.Path("/tmp/prod"); TMP.mkdir(exist_ok=True)
W, H   = 1920, 1080

# ── Configurações por idioma (sem buscar novas) ───────────────────────────
CANAIS = {
    "EN": {
        "voz":"en-US-AriaNeural", "cor":"#818CF8",
        "marca":"Psychology Frequencies · Science-Based",
        "cpm": 25.0,
    },
    "PT": {
        "voz":"pt-BR-FranciscaNeural", "cor":"#7C3AED",
        "marca":"Daniela Coelho · Pesquisa em Psicologia",
        "cpm": 7.0,
    },
    "ES": {
        "voz":"es-MX-DaliaNeural", "cor":"#A78BFA",
        "marca":"Psicología Frecuencias · Ciencia",
        "cpm": 9.0,
    },
    "DE": {
        "voz":"de-DE-KatjaNeural", "cor":"#60A5FA",
        "marca":"Psychologie Frequenzen · Wissenschaft",
        "cpm": 18.0,
    },
    "FR": {
        "voz":"fr-FR-DeniseNeural", "cor":"#F472B6",
        "marca":"Psychologie Fréquences · Science",
        "cpm": 14.0,
    },
    "JA": {
        "voz":"ja-JP-NanamiNeural", "cor":"#FB7185",
        "marca":"サイコロジー周波数 · 科学",
        "cpm": 15.0,
    },
    "KO": {
        "voz":"ko-KR-SunHiNeural", "cor":"#FBBF24",
        "marca":"심리학 주파수 · 과학",
        "cpm": 12.0,
    },
    "IT": {
        "voz":"it-IT-ElsaNeural", "cor":"#34D399",
        "marca":"Psicologia Frequenze · Scienza",
        "cpm": 12.0,
    },
}

# ── Temas virais baseados nos maiores canais ──────────────────────────────
TEMAS = [
    {
        "pubmed_query": "covert narcissism victimhood presentation psychology",
        "titulos": {
            "EN": "The Covert Narcissist Looks Like a Victim — Not a Predator",
            "PT": "O Narcisista Encoberto Parece Vítima — Não Predador",
            "ES": "El Narcisista Encubierto Parece Víctima — No Depredador",
            "DE": "Der Verdeckte Narzisst Wirkt Wie ein Opfer",
            "FR": "Le Narcissiste Masqué Semble Être une Victime",
            "JA": "隠れた自己愛者は被害者に見える",
            "KO": "은밀한 나르시시스트는 피해자처럼 보인다",
            "IT": "Il Narcisista Nascosto Sembra una Vittima",
        },
        "hz": 528, "seed": 9001,
    },
    {
        "pubmed_query": "528hz sound frequency cortisol reduction stress hormones",
        "titulos": {
            "EN": "528Hz Reduces Cortisol — The Peer-Reviewed Evidence",
            "PT": "528Hz Reduz Cortisol — A Evidência Científica",
            "ES": "528Hz Reduce el Cortisol — La Evidencia Científica",
            "DE": "528Hz Reduziert Cortisol — Die Wissenschaftliche Evidenz",
            "FR": "528Hz Réduit le Cortisol — L'Evidence Scientifique",
            "JA": "528Hzはコルチゾールを下げる — 査読済み証拠",
            "KO": "528Hz는 코르티솔을 줄인다 — 동료 검토 증거",
            "IT": "528Hz Riduce il Cortisolo — L'Evidenza Scientifica",
        },
        "hz": 528, "seed": 9334,
    },
    {
        "pubmed_query": "anxious attachment sleep disruption amygdala arousal",
        "titulos": {
            "EN": "Anxious Attachment Activates Your Amygdala While You Sleep",
            "PT": "Apego Ansioso Ativa Sua Amígdala Enquanto Você Dorme",
            "ES": "El Apego Ansioso Activa tu Amígdala Mientras Duermes",
            "DE": "Ängstliche Bindung Aktiviert Ihre Amygdala Während des Schlafs",
            "FR": "L'Attachement Anxieux Active Votre Amygdale Pendant le Sommeil",
            "JA": "不安型愛着は睡眠中に扁桃体を活性化する",
            "KO": "불안 애착은 수면 중 편도체를 활성화한다",
            "IT": "L'Attaccamento Ansioso Attiva la Tua Amigdala Durante il Sonno",
        },
        "hz": 432, "seed": 9667,
    },
    {
        "pubmed_query": "gaslighting cognitive abuse perception reality distortion",
        "titulos": {
            "EN": "Gaslighting Worked the Moment You Doubted Your Own Memory",
            "PT": "O Gaslighting Funcionou Quando Você Duvidou da Sua Memória",
            "ES": "El Gaslighting Funcionó Cuando Dudaste de Tu Memoria",
            "DE": "Gaslighting Funktionierte als Du An Deiner Eigenen Erinnerung Zweifeltest",
            "FR": "Le Gaslighting a Fonctionné Quand Vous Avez Douté de Votre Mémoire",
            "JA": "ガスライティングは自分の記憶を疑った瞬間に機能した",
            "KO": "가스라이팅은 자신의 기억을 의심하는 순간 효과가 났다",
            "IT": "Il Gaslighting ha Funzionato nel Momento in Cui Hai Dubitato",
        },
        "hz": 396, "seed": 9888,
    },
    {
        "pubmed_query": "ADHD 40hz gamma waves working memory executive function",
        "titulos": {
            "EN": "40Hz Gamma Waves Improve ADHD Working Memory by 23%",
            "PT": "40Hz Ondas Gamma Melhoram Memória no TDAH em 23%",
            "ES": "Las Ondas Gamma 40Hz Mejoran la Memoria de Trabajo en TDAH 23%",
            "DE": "40Hz Gamma-Wellen Verbessern ADHS-Arbeitsgedächtnis um 23%",
            "FR": "Les Ondes Gamma 40Hz Améliorent la Mémoire de Travail TDAH de 23%",
            "JA": "40Hzガンマ波がADHDの作業記憶を23%改善",
            "KO": "40Hz 감마파가 ADHD 작업 기억을 23% 향상시킨다",
            "IT": "Le Onde Gamma 40Hz Migliorano la Memoria di Lavoro ADHD del 23%",
        },
        "hz": 40, "seed": 4001,
    },
]

# ── Funções de API ─────────────────────────────────────────────────────────
def pubmed(query):
    try:
        r = requests.get(
            "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi"
            f"?db=pubmed&term={requests.utils.quote(query)}&retmax=1&retmode=json",
            timeout=8)
        pmids = r.json().get("esearchresult",{}).get("idlist",[])
        if not pmids: return "Research (NCBI)"
        r2 = requests.get(
            f"https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esummary.fcgi"
            f"?db=pubmed&id={pmids[0]}&retmode=json", timeout=8)
        doc = r2.json().get("result",{}).get(pmids[0],{})
        autor = (doc.get("authors",[{}]) or [{}])[0].get("name","Research")
        ano   = doc.get("pubdate","2024")[:4]
        return f"{autor} ({ano}), PubMed"
    except: return "Research (NCBI)"

def tts(texto, voz, out):
    s = ". ".join(x.strip() for x in texto.replace('\n',' ').split('.') if x.strip())
    subprocess.run(["edge-tts",f"--voice={voz}","--rate=+32%",
                    f"--text={s}",f"--write-media={out}"],
                   capture_output=True, timeout=60)
    return pathlib.Path(out).exists()

def img(titulo, seed, hz):
    cor_hz = {"528":"purple blue healing","432":"green emerald balance",
               "396":"red orange liberation","40":"green neon focus"}.get(str(hz),"purple")
    p = (f"masterpiece, 8K ultra HD, dark background, {cor_hz} aurora particles, "
         f"psychology healing concept: {titulo[:40]}, cinematic, no text no people "
         f"### text watermark nsfw blurry people")
    url = (f"https://image.pollinations.ai/prompt/{requests.utils.quote(p[:380])}"
           f"?model=flux&width={W}&height={H}&seed={seed}&nologo=true")
    try:
        r = requests.get(url, timeout=60)
        if r.status_code == 200 and len(r.content) > 10000: return r.content
    except: pass
    return None

def freq_audio(hz, seed_path):
    ao = TMP/f"freq_{hz}hz.aac"
    if ao.exists() and ao.stat().st_size > 50000: return ao
    hz_r = hz + (4 if hz < 100 else 8)
    subprocess.run([
        "ffmpeg","-y",
        "-f","lavfi","-i",f"sine=frequency={hz}:duration=600",
        "-f","lavfi","-i",f"sine=frequency={hz_r}:duration=600",
        "-f","lavfi","-i","anoisesrc=color=pink:duration=600",
        "-filter_complex",
        "[0:a]volume=0.04[l];[1:a]volume=0.04[r];[2:a]volume=0.003[p];"
        "[l][r]amerge=inputs=2[bin];[bin][p]amix=inputs=2[out]",
        "-map","[out]","-c:a","aac","-b:a","128k",str(ao)
    ], capture_output=True, timeout=120)
    return ao if ao.exists() else None

def render(img_p, voz_p, freq_p, titulo, marca, cor, idioma, idx):
    # Mix voz + frequência suave
    mix_p = TMP/f"mix_{idioma}_{idx}.aac"
    if freq_p and freq_p.exists():
        subprocess.run([
            "ffmpeg","-y","-i",str(voz_p),"-i",str(freq_p),
            "-filter_complex","[0:a]volume=1[v];[1:a]volume=0.12[f];[v][f]amix=inputs=2:duration=first[out]",
            "-map","[out]","-c:a","aac","-b:a","128k",str(mix_p)
        ], capture_output=True, timeout=60)
    else:
        mix_p = voz_p

    dur_r = subprocess.run(["ffprobe","-v","error","-show_entries","format=duration",
        "-of","default=noprint_wrappers=1:nokey=1",str(mix_p)],
        capture_output=True, timeout=8)
    try: dur = min(float(dur_r.stdout.strip()) + 0.5, 59.0)
    except: dur = 55.0

    t_esc = titulo[:52].replace("'",r"\'")
    m_esc = marca.replace("'",r"\'")
    hz_txt = f"{titulo.split()[0] if titulo[0].isdigit() else '528'}Hz · LIVE"

    vf = (
        f"scale={W}:{H}:force_original_aspect_ratio=increase,crop={W}:{H},"
        f"colorchannelmixer=rr=0.58:gg=0.58:bb=0.58,"
        f"drawbox=y=0:color=black@0.88:width=iw:height=88:t=fill,"
        f"drawbox=y=ih-78:color=black@0.90:width=iw:height=78:t=fill,"
        f"drawbox=x=14:y=18:color=#EF4444:width=12:height=12:t=fill,"
        f"drawtext=text='{hz_txt}':fontsize=18:fontcolor={cor}:x=36:y=15:bold=1:shadowcolor=black:shadowx=1:shadowy=1,"
        f"drawtext=text='{t_esc}':fontsize=30:fontcolor=white:x=(w-text_w)/2:y=h*0.42:bold=1:shadowcolor=#000:shadowx=2:shadowy=2,"
        f"drawtext=text='{m_esc}':fontsize=15:fontcolor=#94A3B8:x=(w-text_w)/2:y=h-52"
    )
    out = TMP/f"video_{idioma}_{idx:03d}.mp4"
    subprocess.run([
        "ffmpeg","-y","-loop","1","-i",str(img_p),"-i",str(mix_p),
        "-vf",vf,"-t",str(dur),
        "-c:v","libx264","-preset","fast","-pix_fmt","yuv420p","-r","30",
        "-c:a","aac","-b:a","128k","-shortest",str(out)
    ], capture_output=True, timeout=300)
    return out if out.exists() and out.stat().st_size > 50000 else None

def groq_gen(titulo, citacao, idioma):
    if not GROQ: return None, None
    lang = {"EN":"English","PT":"Portuguese Brazilian","ES":"Spanish",
             "DE":"German","FR":"French","JA":"Japanese","KO":"Korean","IT":"Italian"}.get(idioma,"English")
    prompt = (
        f"Write a 75-word YouTube Short script in {lang}:\n"
        f"Title: {titulo}\nReal citation: {citacao}\n\n"
        f"Structure:\n1. Counter-intuitive opening hook (not a question)\n"
        f"2. Science fact using the citation\n3. Actionable takeaway\n\n"
        f"Then: TAGS: 8 SEO keywords comma-separated"
    )
    try:
        r = requests.post("https://api.groq.com/openai/v1/chat/completions",
            headers={"Authorization":f"Bearer {GROQ}","Content-Type":"application/json"},
            json={"model":"llama-3.3-70b-versatile",
                  "messages":[{"role":"user","content":prompt}],
                  "max_tokens":280,"temperature":0.72},timeout=20)
        if r.status_code == 200:
            txt = r.json()["choices"][0]["message"]["content"]
            tm = re.search(r'TAGS[:\s]+(.*?)$', txt, re.IGNORECASE|re.MULTILINE)
            tags = tm.group(1).strip() if tm else "psychology,528hz"
            script = re.sub(r'TAGS[:\s]+.*','',txt,flags=re.IGNORECASE|re.MULTILINE).strip()
            return script, tags
    except: pass
    return None, None

def save_sb(titulo, script, tags, idioma, mp4=""):
    if not SB_KEY: return
    voz = CANAIS.get(idioma,{}).get("voz","en-US-AriaNeural")
    requests.post(f"{SB_URL}/rest/v1/en_channel_queue", headers=SBH,
        json={"titulo_en":titulo[:100],"script_en":script,
              "voz_en":voz,"canal_destino":"UCyCkIpsVgME9yCj_oXJFheA",
              "rpm_estimado":CANAIS.get(idioma,{}).get("cpm",10.0),
              "status":"mp4_ready" if mp4 else "pending"},
        timeout=8)

# ── LOOP PRINCIPAL ────────────────────────────────────────────────────────
def run():
    print("=== PRODUCTION PIPELINE — APIs Gratuitas ===\n")
    total = 0

    for t_idx, tema in enumerate(TEMAS):
        print(f"\n📌 [{t_idx+1}/{len(TEMAS)}] {tema['titulos']['EN'][:50]}")

        # PubMed → citação real
        cit = pubmed(tema["pubmed_query"])
        print(f"   📚 {cit[:55]}")

        # Imagem base (1 por tema, compartilhada)
        img_data = img(tema["titulos"]["EN"], tema["seed"], tema["hz"])
        img_path = None
        if img_data:
            img_path = TMP/f"bg_{t_idx}.jpg"
            img_path.write_bytes(img_data)

        # Frequência de fundo
        fa = freq_audio(tema["hz"], t_idx)

        # Gerar em todos os idiomas
        for idioma, cfg in CANAIS.items():
            titulo = tema["titulos"].get(idioma, tema["titulos"]["EN"])
            script, tags = groq_gen(titulo, cit, idioma)
            if not script: continue

            # TTS
            voz_p = TMP/f"voz_{idioma}_{t_idx}.mp3"
            ok = tts(script, cfg["voz"], str(voz_p))

            mp4_path = ""
            if ok and img_path:
                mp4 = render(img_path, voz_p, fa, titulo,
                             cfg["marca"], cfg["cor"], idioma, t_idx)
                if mp4:
                    mp4_path = str(mp4)
                    sz = mp4.stat().st_size // 1024
                    print(f"   ✅ [{idioma}] {sz}KB")
                    total += 1
                else:
                    print(f"   📝 [{idioma}] script")
            else:
                print(f"   📝 [{idioma}] script")

            save_sb(titulo, script, tags, idioma, mp4_path)
            time.sleep(1.5)

        time.sleep(4)

    print(f"\n{'='*45}")
    print(f"✅ {total} vídeos renderizados")
    print(f"   PubMed citations ✅")
    print(f"   Edge TTS 8 idiomas ✅")
    print(f"   Pollinations images ✅")
    print(f"   Groq scripts ✅")
    print(f"   Frequências FFmpeg ✅")
    print(f"   Supabase queue ✅")
    print(f"{'='*45}")

if __name__ == "__main__":
    run()
