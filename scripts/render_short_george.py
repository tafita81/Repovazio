#!/usr/bin/env python3
"""
NARRAÇÃO HUMANA v2 — Arquitetura de Grupos Semânticos
======================================================
PROBLEMA ANTERIOR: frases isoladas → Chatterbox sem contexto → leitura mecânica
SOLUÇÃO: grupos de 2-3 frases juntas → Chatterbox lê a cena completa → emoção real

Como narrador humano:
  - Lê o parágrafo inteiro antes de falar
  - Usa o contexto anterior para calibrar emoção
  - Faz pausas ENTRE cenas, não entre palavras
  - CAPS = sílaba enfatizada naturalmente
"""
import os, sys, json, subprocess, requests, time, re, asyncio

VIDEO_ID = int(os.environ.get("VIDEO_ID", "683"))
VOICE_VERSION = os.environ.get("VOICE_VERSION", "B")
SB_URL  = "https://tpjvalzwkqwttvmszvie.supabase.co"
SB_KEY  = os.environ.get("SUPABASE_SERVICE_KEY", "")
XI_KEY  = os.environ.get("ELEVENLABS_API_KEY", "")
GEORGE  = "JBFqnCBsd6RMkjVDRZzb"
WORKDIR = f"/tmp/short_{VIDEO_ID}"
os.makedirs(WORKDIR, exist_ok=True)
GEORGE_REF = f"{WORKDIR}/george_ref.wav"
GEORGE_SRC = "https://tpjvalzwkqwttvmszvie.supabase.co/storage/v1/object/public/videos/mp4s/v683_george_1779065193.mp4"

def log(m): print(m, flush=True)
def dur(p):
    r = subprocess.run(["ffprobe","-v","quiet","-print_format","json","-show_format",p],
        capture_output=True, text=True)
    return float(json.loads(r.stdout)["format"]["duration"])
measure_dur = dur  # alias para compatibilidade
def silence(secs, sr, path):
    """Gera silêncio com torchaudio (evita problemas com ffmpeg lavfi)"""
    import torch
    n_samples = int(float(secs) * int(sr))
    silent = torch.zeros(1, max(1, n_samples))
    torchaudio.save(path, silent, int(sr))
def upscale(src, dst):
    subprocess.run(["ffmpeg","-y","-i",src,"-vf","scale=1080:1920:flags=lanczos","-q:v","2",dst],
        capture_output=True)
    return dst if os.path.exists(dst) else src

def is_valid_img(content):
    return len(content) > 5000 and content[:3] in (b'\xff\xd8\xff', b'\x89PN', b'\x89PG')

def dl_img(url, timeout=20):
    try:
        r = requests.get(url, timeout=timeout, headers={"User-Agent":"Mozilla/5.0"})
        return r.content if r.status_code == 200 and is_valid_img(r.content) else None
    except: return None

def sb_patch(id_, data):
    requests.patch(f"{SB_URL}/rest/v1/content_pipeline?id=eq.{id_}",
        headers={"apikey":SB_KEY,"Authorization":f"Bearer {SB_KEY}",
                 "Content-Type":"application/json","Prefer":"return=minimal"},
        json=data, timeout=60)

log(f"\nψ NARRAÇÃO HUMANA v2 — #{VIDEO_ID}")

# ── 1. SCRIPT ──────────────────────────────────────────────────────────
row = requests.get(f"{SB_URL}/rest/v1/content_pipeline?id=eq.{VIDEO_ID}&select=id,title,script,youtube_title,youtube_description,youtube_tags,related_video_id,series_slug,ep_number",
    headers={"apikey":SB_KEY,"Authorization":f"Bearer {SB_KEY}"}, timeout=60).json()
if not row or not row[0].get("script"):
    log("❌ Script não encontrado"); sys.exit(1)

TITULO = row[0]["title"]
SCRIPT_RAW = row[0]["script"].strip()
YT_TITLE   = row[0].get("youtube_title") or TITULO
YT_DESC    = row[0].get("youtube_description") or ""
YT_TAGS    = row[0].get("youtube_tags") or ""
YT_LONG_ID = row[0].get("related_video_id") or ""
SERIE_SLUG = row[0].get("series_slug") or ""
EP_NUMBER  = row[0].get("ep_number") or 1

# Se tiver Long ID, injetar link específico na descrição (YouTube linking algorithm)
if YT_LONG_ID and "youtube.com/watch" not in YT_DESC:
    LONG_LINK = f"https://youtube.com/watch?v={YT_LONG_ID}"
    YT_DESC = YT_DESC.replace("https://youtube.com/@psidanielacoelho",
                               LONG_LINK + "\n\n👉 Canal completo: https://youtube.com/@psidanielacoelho")

log(f"  Título YT: {YT_TITLE[:55]}")
log(f"  Série: {SERIE_SLUG} E{EP_NUMBER:02d} | Long ID: {YT_LONG_ID or 'pendente'}")
log(f"  Título: {TITULO[:55]}")
log(f"  Script: {len(SCRIPT_RAW)} chars")

# ── 2. GRUPOS SEMÂNTICOS POR VÍDEO ─────────────────────────────────────
# Cada grupo = lista de (texto_para_tts, exaggeration, cfg_weight, pausa_depois_s)
# O texto de cada grupo inclui MÚLTIPLAS frases juntas para dar contexto ao Chatterbox
# A pausa é inserida via ffmpeg ENTRE grupos (não dentro)

def montar_grupos(vid, script):
    """Agrupa frases do script em cenas semânticas com parâmetros emocionais."""
    linhas = [l.strip() for l in script.split('\n') if l.strip()]
    
    # Parâmetros base (Versão B: enhanced dramatic)
    P = {
        "HOOK":      (0.88, 0.15, 1.2),   # abertura + twist dramático
        "TENSAO":    (0.85, 0.16, 1.0),   # conflito / manipulação
        "REVELACAO": (0.90, 0.12, 1.1),   # "Isso tem NOME" / virada
        "DESENV":    (0.78, 0.22, 0.7),   # explicação / contexto
        "CTA":       (0.70, 0.30, 0.0),   # call to action (final)
    }
    
    # Padrão: dividir em 4-5 grupos semânticos naturais
    # Hook (1-2 linhas) | Tensão (1-2) | Revelação (1-2) | Desenv (2-3) | CTA (2)
    n = len(linhas)
    
    if n <= 5:
        # Script curto: apenas 3 grupos
        grupos = [
            ("\n".join(linhas[:2]), *P["HOOK"]),
            ("\n".join(linhas[2:n-2]), *P["REVELACAO"]),
            ("\n".join(linhas[n-2:]), *P["CTA"]),
        ]
    elif n <= 7:
        # Script médio: 4 grupos
        grupos = [
            ("\n".join(linhas[:2]), *P["HOOK"]),
            ("\n".join(linhas[2:4]), *P["TENSAO"]),
            ("\n".join(linhas[4:n-2]), *P["REVELACAO"]),
            ("\n".join(linhas[n-2:]), *P["CTA"]),
        ]
    else:
        # Script longo (9+ linhas): 5 grupos
        grupos = [
            ("\n".join(linhas[:2]), *P["HOOK"]),
            ("\n".join(linhas[2:4]), *P["TENSAO"]),
            ("\n".join(linhas[4:5]), *P["REVELACAO"]),
            ("\n".join(linhas[5:n-2]), *P["DESENV"]),
            ("\n".join(linhas[n-2:]), *P["CTA"]),
        ]
    
    # Filtrar grupos vazios
    return [(t.strip(), e, c, p) for (t, e, c, p) in grupos if t.strip()]

GRUPOS = montar_grupos(VIDEO_ID, SCRIPT_RAW)

log(f"\n  {len(GRUPOS)} grupos semânticos:")
for i, (txt, exag, cfg, pau) in enumerate(GRUPOS, 1):
    preview = txt.replace('\n', ' / ')[:60]
    log(f"    [{i}] exag={exag:.2f} cfg={cfg:.2f} +{pau:.1f}s | {preview}")

# ── 3. REFERÊNCIA GEORGE ───────────────────────────────────────────────
log(f"\n🎙️  Baixando referência George...")
if not os.path.exists(GEORGE_REF):
    r = requests.get(GEORGE_SRC, timeout=120, headers={"User-Agent":"Mozilla/5.0"})
    if r.status_code == 200:
        src = f"{WORKDIR}/george_src.mp4"
        with open(src, 'wb') as f: f.write(r.content)
        subprocess.run(["ffmpeg","-y","-i",src,"-ss","2","-t","14",
            "-vn","-ar","22050","-ac","1",
            "-af","highpass=f=80,lowpass=f=8000,volume=1.3", GEORGE_REF],
            capture_output=True)
        log(f"  ✅ {dur(GEORGE_REF):.1f}s extraídos")
    else:
        log(f"  ❌ {r.status_code}"); sys.exit(1)
else:
    log("  ✅ Em cache")

# ── 4. VOZ ─────────────────────────────────────────────────────────────
log(f"\n🎤  Gerando narração em {len(GRUPOS)} grupos...")
AUDIO = None
VOICE_USED = "Chatterbox/George_clone_semantic"
SR = 24000  # sample rate Chatterbox

# P1: ElevenLabs George (script completo se disponível)
SCRIPT_TTS = "\n\n".join(t for t, *_ in GRUPOS)  # \n\n = pausa de parágrafo natural
if XI_KEY:
    log("  [P1] ElevenLabs George...")
    try:
        r = requests.post(f"https://api.elevenlabs.io/v1/text-to-speech/{GEORGE}",
            headers={"xi-api-key":XI_KEY,"Content-Type":"application/json"},
            json={"text":SCRIPT_TTS,"model_id":"eleven_multilingual_v2",
                  "voice_settings":{"stability":0.20,"similarity_boost":0.85,
                                    "style":0.70,"use_speaker_boost":True}},
            timeout=180)
        if r.status_code == 200:
            AUDIO = f"{WORKDIR}/audio_xi.mp3"
            with open(AUDIO,'wb') as f: f.write(r.content)
            log(f"  ✅ ElevenLabs George: {len(r.content)//1024}KB")
            VOICE_USED = "ElevenLabs/George"
        else:
            log(f"  ❌ ElevenLabs {r.status_code}: {r.json().get('detail',{}).get('code','')}")
    except Exception as e: log(f"  ⚠️ {e}")

# P2: Chatterbox — GRUPOS SEMÂNTICOS com silêncio PRÉ+PÓS estratégico
# Fórmula viral (Psych2Go 28M views): gancho → PAUSA LONGA → twist curto → pausa → revelação → CTA
if AUDIO is None:
    log("  [P2] Chatterbox GRUPOS VIRAIS — silêncio PRÉ+PÓS...")
    try:
        import torchaudio
        from chatterbox.mtl_tts import ChatterboxMultilingualTTS

        log("  Carregando modelo...")
        model = ChatterboxMultilingualTTS.from_pretrained(device="cpu")
        SR = model.sr
        log(f"  ✅ Modelo | SR={SR}Hz")

        def gen_wav(txt, exag, cfg):
            return model.generate(txt, audio_prompt_path=GEORGE_REF,
                language_id="pt", exaggeration=exag, cfg_weight=cfg)

        def mksil(secs, path):
            # pcm_s16le = silêncio 100% limpo, sem ruído de codec
            subprocess.run(["ffmpeg","-y","-f","lavfi",
                "-i",f"anullsrc=r={SR}:cl=mono",
                "-t",str(secs),"-ar",str(SR),
                "-acodec","pcm_s16le","-f","wav", path],
                capture_output=True)
            return path if os.path.exists(path) and os.path.getsize(path) > 100 else None

        linhas = [l.strip() for l in SCRIPT_RAW.split("\n") if l.strip()]
        n = len(linhas)

        def tipo(l):
            t = l.lower()
            # CTA: sempre no final
            if any(k in t for k in ["salva","canal","assistir","mais tarde","não perder","completo"]): return "CTA"
            # REVELACAO: momento de nomeação
            if any(k in t for k in ["isso tem nome","isso se chama","tem nome","isso é","chama-se"]): return "REVELACAO"
            # CHORO: linha de máxima emoção (personagem vive a dor)
            if any(k in t for k in ["chora","lágrimas","soluçava","desmoronou","não conseguia","não aguentava","quebrou","colapsou"]): return "CHORO"
            # IMPACTO: linha curta + pontada emocional
            if len(l) < 35: return "IMPACTO"
            # PAUSA: suspense ou revelação parcial
            if "..." in l or l.endswith("?") or l.endswith("—"): return "PAUSA"
            # GANCHO: abertura de cena com personagem
            if any(k in t for k in ["você conhece","conheça","imagine","pense em","conhece a","conhece o"]): return "GANCHO"
            return "NORMAL"

        # Grupos: (texto, exag, cfg, sil_pre_s, sil_pos_s)
        grupos = []
        i = 0
        while i < n:
            l = linhas[i]
            t = tipo(l)
            if t == "IMPACTO":
                # Drama máximo: pausa longa antes + depois → peso cinematográfico
                grupos.append((l, 0.96, 0.09, 1.0, 1.6))
                i += 1
            elif t == "CHORO":
                # Dor real: voz mais carregada, mais lenta, pausa após
                grupos.append((l, 0.95, 0.08, 0.5, 1.8))
                i += 1
            elif t == "REVELACAO":
                # Momento de nomeação: entonação ascendente, pausa dramática
                grupos.append((l, 0.93, 0.10, 0.7, 1.4))
                i += 1
            elif t == "GANCHO":
                # Abertura: voz próxima, íntima, convida o espectador
                grupos.append((l, 0.88, 0.12, 0.0, 0.8))
                i += 1
            elif t == "CTA":
                grupos.append(("\n".join(linhas[i:]), 0.74, 0.26, 0.9, 0.0))
                i = n
            elif t == "PAUSA":
                # Suspense: pausa antes para antecipar + pausa depois
                grupos.append((l, 0.87, 0.13, 0.4, 1.1))
                i += 1
            else:
                # NORMAL: agrupar 2 em 2 para contexto natural
                if i+1 < n and tipo(linhas[i+1]) == "NORMAL":
                    grupos.append(("\n".join([linhas[i], linhas[i+1]]), 0.82, 0.17, 0.0, 0.65))
                    i += 2
                else:
                    grupos.append((l, 0.81, 0.15, 0.0, 0.75))
                    i += 1

        log(f"  {len(grupos)} grupos:")
        for gi,(gt,ge,gc,gpre,gpos) in enumerate(grupos,1):
            log(f"    [{gi}] pre={gpre:.1f}s pos={gpos:.1f}s exag={ge:.2f} cfg={gc:.2f} | {gt.replace(chr(10),' / ')[:50]}")

        seg_files = []
        for gi,(gt,ge,gc,gpre,gpos) in enumerate(grupos,1):
            if gpre > 0:
                sp = mksil(gpre, f"{WORKDIR}/spre_{gi:02d}.wav")
                if sp: seg_files.append(sp)
            gpath = f"{WORKDIR}/grp_{gi:02d}.wav"
            wav = gen_wav(gt, ge, gc)
            torchaudio.save(gpath, wav, SR)
            d_g = dur(gpath)

            # FADE: 30ms in + 60ms out — elimina click + noise ao fim
            gpath_fade = f"{WORKDIR}/grp_{gi:02d}_fade.wav"
            fade_out_start = max(0.0, d_g - 0.06)
            r_fade = subprocess.run([
                "ffmpeg","-y","-i",gpath,
                "-af",f"afade=t=in:st=0:d=0.03,afade=t=out:st={fade_out_start:.4f}:d=0.06",
                gpath_fade
            ], capture_output=True, text=True, timeout=30)

            # NOISE GATE POR SEGMENTO: garante silêncio digital nas bordas de cada fala
            gpath_clean = f"{WORKDIR}/grp_{gi:02d}_clean.wav"
            if os.path.exists(gpath_fade) and os.path.getsize(gpath_fade) > 100:
                subprocess.run([
                    "ffmpeg","-y","-i",gpath_fade,
                    "-af","agate=threshold=0.028:ratio=8000:attack=1:release=60",
                    gpath_clean
                ], capture_output=True, timeout=30)
            final_seg = gpath_clean if os.path.exists(gpath_clean) and os.path.getsize(gpath_clean) > 100 else (
                        gpath_fade if os.path.exists(gpath_fade) and os.path.getsize(gpath_fade) > 100 else gpath)
            log(f"    [{gi}] ✅ {d_g:.1f}s (fade in/out aplicado)")
            seg_files.append(final_seg)
            if gpos > 0:
                sp2 = mksil(gpos, f"{WORKDIR}/spos_{gi:02d}.wav")
                if sp2: seg_files.append(sp2)

        seg_files = [s for s in seg_files if s and os.path.exists(s) and os.path.getsize(s) > 100]
        if not seg_files: raise RuntimeError("Nenhum segmento")

        concat_f = f"{WORKDIR}/concat_cb.txt"
        with open(concat_f,"w") as f:
            for s in seg_files: f.write(f"file '{s}'\n")
        raw = f"{WORKDIR}/cb_raw.wav"
        mp3_out = f"{WORKDIR}/audio_cb.mp3"
        # Sem volume extra: manter nível original para o noise gate funcionar
        rc = subprocess.run(["ffmpeg","-y","-f","concat","-safe","0",
            "-i",concat_f,"-ar","44100","-ac","1",raw],
            capture_output=True, text=True, timeout=120)
        if rc.returncode != 0:
            log(f"  ⚠️ concat err: {rc.stderr[-100:]}")
            seg_only = [s for s in seg_files if "pre_" not in s and "pos_" not in s]
            with open(concat_f,"w") as f:
                for s in seg_only: f.write(f"file '{s}'\n")
            subprocess.run(["ffmpeg","-y","-f","concat","-safe","0",
                "-i",concat_f,"-ar","44100","-ac","1",raw], capture_output=True, timeout=120)
        # PIPELINE DE LIMPEZA FINAL — 3 passes:
        # Pass 1: afftdn (FFT denoiser) — remove noise espectral inteligentemente
        # Pass 2: silenceremove — remove silêncio nas bordas
        # Pass 3: agate suave — fecha gaps digitais residuais
        denoised_wav = f"{WORKDIR}/cb_denoised.wav"
        subprocess.run(["ffmpeg","-y","-i",raw,
            "-af",(
                "highpass=f=80,"              # remove rumble
                "afftdn=nf=-35:nt=w:om=o,"   # FFT denoiser (chave principal)
                "agate=threshold=0.015:ratio=100:attack=5:release=100,"  # gate suave
                "volume=1.05"                 # compensar atenuação do denoiser
            ),
            "-ar","44100","-ac","1", denoised_wav],
            capture_output=True, timeout=90)
        src_for_mp3 = denoised_wav if os.path.exists(denoised_wav) and os.path.getsize(denoised_wav) > 1000 else raw
        subprocess.run(["ffmpeg","-y","-i",src_for_mp3,
            "-codec:a","libmp3lame","-b:a","256k","-q:a","0", mp3_out],
            capture_output=True, timeout=60)
        if os.path.exists(mp3_out) and os.path.getsize(mp3_out) > 5000:
            AUDIO = mp3_out
            log(f"  ✅ Chatterbox GRUPOS: {dur(AUDIO):.2f}s")
        else:
            raise RuntimeError("MP3 vazio")
    except Exception as e:
        log(f"  ⚠️ Chatterbox: {type(e).__name__}: {str(e)[:200]}")
        VOICE_USED = "AntonioNeural/fallback"

# P3: AntonioNeural fallback
if AUDIO is None:
    log("  [P3] AntonioNeural fallback...")
    async def _gen():
        import edge_tts
        c = edge_tts.Communicate(SCRIPT_TTS, voice="pt-BR-AntonioNeural", rate="-12%")
        await c.save(f"{WORKDIR}/audio_ant.mp3")
    asyncio.run(_gen())
    AUDIO = f"{WORKDIR}/audio_ant.mp3"
    log(f"  ✅ AntonioNeural: {dur(AUDIO):.2f}s")

DUR_AUDIO = dur(AUDIO)
log(f"\n  ✅ Narração final: {DUR_AUDIO:.2f}s | {VOICE_USED}")

# Safety cap 62s (sem atempo normal — só em caso extremo)
if DUR_AUDIO > 62.0:
    at = DUR_AUDIO / 60.0
    cap = f"{WORKDIR}/audio_cap.mp3"
    subprocess.run(["ffmpeg","-y","-i",AUDIO,"-filter:a",f"atempo={at:.4f}",
        "-q:a","2", cap], capture_output=True, timeout=60)
    if os.path.exists(cap): AUDIO=cap; DUR_AUDIO=dur(AUDIO)
    log(f"  ⬇️ Cap aplicado: {DUR_AUDIO:.1f}s")

RATE_REAL = len(SCRIPT_TTS.replace('\n',' ')) / DUR_AUDIO
linhas_all = [l for l in SCRIPT_RAW.split('\n') if l.strip()]
DURS = [max(1.2, round(len(l)/RATE_REAL, 3)) for l in linhas_all]
diff = DUR_AUDIO - sum(DURS); DURS[0] = round(DURS[0]+diff, 3)
frases = linhas_all   # alias para compatibilidade com seção de imagens
N = len(frases)


# ── 5. PROMPTS OTIMIZADOS PARA AUDIÊNCIA 72% MULHERES 25-35 BR ─────
log(f"\n🖼️  ETAPA 2 — Imagens (prompts audiência mulheres BR 25-35)")

STYLE = ("kawaii chibi anime illustration, 9:16 portrait, "
         "masterpiece, best quality, vivid expressive colors, "
         "Brazilian woman characters, relatable authentic emotions, "
         "detailed backgrounds, cinematic lighting")
NEG  = "### lowres, bad anatomy, text, watermark, nsfw, ugly, blurry, realistic, western cartoon"

# Sara otimizada para audiência BR feminina 25-35
SARA = ("female protagonist age 28, curly dark brown hair, warm olive skin, "
        "everyday clothes — yellow cardigan or simple white blouse, "
        "expressive eyes showing confusion/pain, relatable Brazilian woman look")
DANIELA = ("female psychology host age 35, dark straight bob hair, mint blouse, "
           "ψ psychology pin, confident warm authoritative expression, "
           "direct eye contact with viewer, empowering presence")
MARCOS  = ("male antagonist age 34, well-dressed navy blazer, "
           "charming disarming smile hiding manipulative intent, "
           "handsome but with cold calculating eyes, deceptive warmth")
ANA     = ("female expert Dr age 42, white coat, reading glasses, "
           "Brazilian professional appearance, scientific authority, clipboard")

# ══════════════════════════════════════════════════════════════════
# PSYCH2GO IMAGE SYSTEM V32
# 8 CENAS ÚNICAS por vídeo — cada posição tem ambiente diferente
# Personagem + Cena = história visual sem repetição
# ══════════════════════════════════════════════════════════════════

# Ambiente por posição no vídeo (Psych2Go usa ambientes distintos)
SCENE_ENV = [
    # 0: Abertura — personagem em ambiente cotidiano
    "interior home setting, warm morning light, cozy bedroom or kitchen, character in daily routine, establishing shot wide angle",
    # 1: O problema — close-up emocional tenso
    "extreme close-up emotional face, tense jaw, glossy eyes holding back tears, harsh sharp lighting, tight frame",
    # 2: Conflito — dinâmica entre personagens
    "two characters in tense moment, one dominant looming over other, atmospheric distance between them, dramatic side lighting",
    # 3: Revelação científica — ambiente acadêmico
    "library or study room, open book with highlighted text, researcher or therapist with clipboard, soft blue academic light",
    # 4: Visualização interna — abstrata/surrealista
    "surreal dreamlike mental landscape, character inside symbolic space, floating thoughts represented visually, violet haze",
    # 5: O custo — contraste temporal
    "before-after split visual metaphor, character energy depleted, calendar or clock showing time passed, grey desaturated mood",
    # 6: Insight — momento de percepção
    "character in quiet contemplative moment, soft dawn light, hand on heart, realization expression, warm amber tones",
    # 7: Esperança — cena de cura
    "healing and recovery scene, soft golden hour outdoor light, character looking forward, green park or window with sunlight",
    # 8: CTA — personagem falando para câmera
    "direct eye contact with camera, warm invitation expression, pointing gesture toward viewer, save and subscribe visual cues",
]

def tipo_emocional(frase):
    t = frase.lower()
    if any(k in t for k in ["salva","vídeo completo","canal","assistir","não perder"]): return "CTA"
    if any(k in t for k in ["isso tem nome","isso se chama","chama-se","tem nome"]): return "REVELACAO"
    if any(k in t for k in ["chora","lágrimas","soluçava","desmoronou","não conseguia","colapsou"]): return "CHORO"
    if any(k in t for k in ["harvard","pesquisa","estudo","neurociência","neurológ","química","dopamina","cortisol","amígdala"]): return "CIENCIA"
    if any(k in t for k in ["você conhece","conheça","imagine","pense em","hoje ela","naquele dia","era uma"]): return "GANCHO"
    if any(k in t for k in ["perigoso","calculista","manipula","controla","grita","humilha"]): return "VILAO"
    if any(k in t for k in ["sente","sentia","chorando","confusa","culpada","apagada","esgotada","não aguentava"]): return "DOR"
    if any(k in t for k in ["no vídeo","completo","mostro","aprenda","quer entender"]): return "CTA"
    return "NORMAL"

def prompt_for_frase(frase, idx, N):
    t = frase.lower()
    te = tipo_emocional(frase)
    
    # Cena por posição (garante diversidade visual)
    # idx começa em 1; scene_pos de 0 a 8
    scene_pos = min(idx - 1, len(SCENE_ENV) - 1)
    # Para vídeos > 9 frases: ciclar com variação
    if idx > len(SCENE_ENV):
        scene_pos = (idx - 1) % len(SCENE_ENV)
    base_scene = SCENE_ENV[scene_pos]
    
    # Personagem principal baseado no tipo emocional + posição
    if te == "CTA" or idx == N:
        char = DANIELA + ", warm direct gaze into camera, friendly inviting"
    elif te == "VILAO":
        char = MARCOS + ", menacing cold calculating expression"
    elif te == "CHORO" or te == "DOR":
        char = SARA + ", deeply emotional vulnerable expression"
    elif te == "CIENCIA":
        char = ANA + ", authoritative researcher pose, pointing at data"
    elif te == "REVELACAO":
        char = ANA + ", dramatic revelation expression, discovery moment"
    elif te == "GANCHO":
        # Abertura: usar o personagem da história
        char = SARA + ", caught in ordinary moment unaware of pattern"
    elif idx <= N // 3:
        char = MARCOS + ", charming but something feels off"
    elif idx <= 2 * N // 3:
        char = SARA + ", emotional processing journey"
    else:
        char = DANIELA + ", empowering healing presence"
    
    # Contexto específico da frase no prompt
    frase_ctx = frase[:50].lower().replace('"', '').replace("'", "")
    
    return (
        f"masterpiece, best quality, {STYLE}, "
        f"{char}, "
        f"{base_scene}, "
        f"scene context: {frase_ctx}, "
        f"vertical 9:16 portrait format, "
        f"Psych2Go animation style, flat illustration, "
        f"emotionally resonant, viral psychology content "
        f"{NEG}"
    )

PROMPTS = [prompt_for_frase(f, i, N) for i, f in enumerate(frases, 1)]

PROMPTS = [prompt_for_frase(f, i, N) for i, f in enumerate(frases, 1)]

# Buscar banco
banco_map = {}
try:
    rb = requests.get(f"{SB_URL}/rest/v1/image_bank?select=character_slug,scene_type,image_url&limit=300",
        headers={"apikey":SB_KEY,"Authorization":f"Bearer {SB_KEY}"}, timeout=60)
    for img in rb.json():
        k = f"{img['character_slug']}_{img['scene_type']}"
        banco_map.setdefault(k, []).append(img['image_url'])
    log(f"  🏦 Banco: {sum(len(v) for v in banco_map.values())} imagens")
except Exception as e:
    log(f"  ⚠️ Banco: {e}")

IMGS = []
banco_cnt = poll_cnt = 0

# Lista plana de todas as URLs do banco para fallback aleatório
all_banco_urls = [u for urls in banco_map.values() for u in urls]

# Psych2Go Image Strategy:
# 1. Pollinations FLUX primeiro (imagem única por frase, seed única, cena específica)
# 2. Banco específico por key (fallback rápido)
# 3. Banco aleatório com GARANTIA DE NÃO REPETIR (evitar mesma imagem consecutiva)

used_banco_idxs = set()  # evitar repetição no banco

for idx, (frase, prompt) in enumerate(zip(frases, PROMPTS), 1):
    fpath = f"{WORKDIR}/img_{idx:02d}.jpg"
    up    = f"{WORKDIR}/img_up_{idx:02d}.jpg"
    found = False

    # ─── 1. POLLINATIONS FLUX — imagem única por frase ───────────────
    # Seed única: posição × video_id × timestamp → sem repetição entre vídeos
    import time as _t
    seed = (VIDEO_ID * 1000 + idx * 197 + int(_t.time()) % 10000) % 2147483647
    purl = (
        f"https://image.pollinations.ai/prompt/"
        f"{requests.utils.quote(prompt[:600])}"
        f"?width=576&height=1024&seed={seed}&nologo=true&model=flux"
    )
    data = dl_img(purl, timeout=45)
    if data and is_valid_img(data):
        with open(fpath,'wb') as f: f.write(data)
        IMGS.append(upscale(fpath, up)); poll_cnt += 1; found = True
        log(f"  [{idx:02d}/{N}] 🎨 FLUX {len(data)//1024}KB | pos={idx-1} {SCENE_ENV[min(idx-1,8)][:40]}")

    # ─── 2. Banco key específica (fallback) ──────────────────────────
    if not found:
        te = tipo_emocional(frase)
        key_map = {
            "CIENCIA": "ana_ciencia", "REVELACAO": "ana_ciencia",
            "CHORO": "sara_problema", "DOR": "sara_problema",
            "VILAO": "marcos_problema",
            "GANCHO": "daniela_cta", "CTA": "daniela_cta",
        }
        key = key_map.get(te)
        if key and banco_map.get(key):
            candidates = [(bi, url) for bi, url in enumerate(banco_map[key]) if bi not in used_banco_idxs]
            if not candidates:
                candidates = list(enumerate(banco_map[key]))  # reset se esgotou
            bi, burl = candidates[seed % len(candidates)]
            data = dl_img(burl)
            if data and is_valid_img(data):
                with open(fpath,'wb') as f: f.write(data)
                IMGS.append(upscale(fpath, up)); banco_cnt += 1; found = True
                used_banco_idxs.add(bi)
                log(f"  [{idx:02d}/{N}] 🏦 {key}")

    # ─── 3. Banco aleatório SEM REPETIR ──────────────────────────────
    if not found and all_banco_urls:
        # Escolher índice não usado ainda
        available = [i for i in range(len(all_banco_urls)) if i not in used_banco_idxs]
        if not available:
            available = list(range(len(all_banco_urls)))
            used_banco_idxs.clear()
        bi = available[seed % len(available)]
        data = dl_img(all_banco_urls[bi])
        if data and is_valid_img(data):
            with open(fpath,'wb') as f: f.write(data)
            IMGS.append(upscale(fpath, up)); banco_cnt += 1; found = True
            used_banco_idxs.add(bi)
            log(f"  [{idx:02d}/{N}] 🏦 rnd#{bi}")

    # ─── 4. Fallback seguro ───────────────────────────────────────────
    if not found:
        IMGS.append(IMGS[-1] if IMGS else None)
        log(f"  [{idx:02d}/{N}] ⚠️ duplicando anterior")

log(f"  ✅ {banco_cnt} banco | {poll_cnt} Pollinations FLUX | {banco_cnt+poll_cnt}/{N}")

# ── 6. RENDER ────────────────────────────────────────────────────────
log(f"\n🎬 ETAPA 3 — FFMPEG render")
OVERLAY = (
    "drawtext=fontfile=/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf:"
    "text='ψ @psidanielacoelho':fontcolor=white:fontsize=26:"
    "borderw=2:bordercolor=black:x=20:y=h-48"
)
concat_txt = f"{WORKDIR}/concat.txt"
imgs_validos = [(img, dur) for img, dur in zip(IMGS, DURS)
                if img and os.path.exists(img) and os.path.getsize(img) > 1000]
log(f"  Imagens válidas: {len(imgs_validos)}/{len(IMGS)}")
if not imgs_validos:
    log("❌ Nenhuma imagem válida — tentando fallback com última disponível")
    # Fallback: usar qualquer imagem que existe
    for img in IMGS:
        if img and os.path.exists(img) and os.path.getsize(img) > 500:
            imgs_validos = [(img, DUR_AUDIO)]
            break
    if not imgs_validos:
        log("❌ Sem imagens — abortando"); sys.exit(1)

with open(concat_txt,'w') as f:
    for img, dur in imgs_validos:
        f.write(f"file '{img}'\nduration {dur:.3f}\n")
    f.write(f"file '{imgs_validos[-1][0]}'\n")

# Verificar que concat_txt tem conteúdo
with open(concat_txt) as f:
    ct = f.read()
log(f"  concat.txt: {len(ct)} chars, {ct.count('file')} entradas")
if len(ct) < 20:
    log("❌ concat.txt vazio — abortando"); sys.exit(1)

OUT = f"{WORKDIR}/output.mp4"
r = subprocess.run([
    "ffmpeg","-y",
    "-f","concat","-safe","0","-i",concat_txt,
    "-i",AUDIO,
    "-vf",f"{OVERLAY},format=yuv420p",
    "-c:v","libx264","-crf","22","-preset","fast",
    "-c:a","aac","-b:a","128k",
    "-shortest","-movflags","+faststart","-r","25",OUT
], capture_output=True,text=True,timeout=300)
if r.returncode != 0:
    log(f"❌ ffmpeg: {r.stderr[-300:]}"); sys.exit(1)

DUR_FINAL = measure_dur(OUT)
SZ = os.path.getsize(OUT)/1024/1024
log(f"  ✅ {DUR_FINAL:.2f}s | {SZ:.2f}MB")

# ── 7. UPLOAD ────────────────────────────────────────────────────────
log(f"\n☁️  ETAPA 4 — Upload")
ts = int(time.time())
fname = f"v{VIDEO_ID}_cb_v{VOICE_VERSION}_{ts}.mp4"
with open(OUT,'rb') as f: data=f.read()
video_url = None
for att in range(5):
    r = requests.post(f"{SB_URL}/storage/v1/object/videos/mp4s/{fname}",
        headers={"apikey":SB_KEY,"Authorization":f"Bearer {SB_KEY}",
                 "Content-Type":"video/mp4","x-upsert":"true"},
        data=data,timeout=300)
    if r.status_code in (200,201):
        video_url = f"{SB_URL}/storage/v1/object/public/videos/mp4s/{fname}"
        log(f"  ✅ {video_url}")
        break
    log(f"  Att {att+1}: {r.status_code}"); time.sleep(15)

if video_url:
    sb_patch(VIDEO_ID, {
        "video_url": video_url, "status": "pending_credentials",
        "youtube_title": YT_TITLE,
        "youtube_description": YT_DESC,
        "youtube_tags": YT_TAGS or f"#{SERIE_SLUG} #psicologia #saudemental #relacionamentos",
        "metadata": json.dumps({
            "dur_s": round(DUR_FINAL,1), "file_mb": round(SZ,2),
            "voice": VOICE_USED,
            "n_frases": N, "imgs_banco": banco_cnt, "imgs_poll": poll_cnt,
            "serie_slug": SERIE_SLUG, "ep_number": EP_NUMBER,
            "yt_long_id": YT_LONG_ID,
            "version": "v30_series_linked",
            "audience": "72pct_women_25_35_BR",
            "audio_params": {
                "exag_impacto": 0.92, "cfg_impacto": 0.10,
                "sil_pre_imp": 0.9, "sil_pos_imp": 1.4,
                "noise_gate": "agate=threshold=0.018:ratio=1000:attack=3:release=150",
                "fade_in_ms": 20, "fade_out_ms": 30
            }
        })
    })

log(f"\nψ RESULTADO PERFEITO:")
log(f"  ⏱️  {DUR_FINAL:.2f}s | 💾 {SZ:.2f}MB")
log(f"  🎤 {VOICE_USED} | emoção dinâmica por frase")
log(f"  🖼️  {banco_cnt} banco + {poll_cnt} Pollinations")
log(f"  🎬 {video_url or '❌ upload falhou'}")
log(f"  📺 Título YT: {YT_TITLE[:70]}")
log(f"  🔗 Long ID: {YT_LONG_ID or 'configurar via YouTube Studio quando publicar'}")
log(f"  📋 Série: {SERIE_SLUG.upper()} E{EP_NUMBER:02d}")
if YT_LONG_ID:
    log(f"  ✅ YouTube vai mostrar Long ao lado do Short automaticamente")
else:
    log(f"  ⚠️ Após publicar: YouTube Studio → Detalhes → Vídeo relacionado → colar ID do Long")
