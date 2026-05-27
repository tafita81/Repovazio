"""
audio_pro_pipeline.py — Edge TTS + pós-processamento profissional ESTÚDIO
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

PROBLEMA: Edge TTS sozinho soa news anchor, não sleep meditation
SOLUÇÃO: pós-processamento estilo Pedro Engler / Sleep Cove studio chain

PIPELINE FFmpeg (sequencial):
  1. asetrate=42000  → pitch DOWN -5% (mais grave, profundo)
  2. atempo=0.93     → slow -7% adicional (rate efetivo -12% acumulado)
  3. lowshelf -3dB   → menos agudos, mais corpo
  4. equalizer 200Hz +2dB → boost peito da voz
  5. lowpass 8500    → corta sibilantes (chiado de S/T)
  6. acompressor     → suaviza picos, voz consistente
  7. aecho subtle    → reverb cavernoso (sensação de profundidade)
  8. Frase a frase com silêncio 1.2-2s entre (anti-corrida)
  9. Mescla com binaural+brown rain

RESULTADO: voz Edge TTS soando como gravação de estúdio profissional
"""
import os, asyncio, edge_tts, subprocess, pathlib, requests

OUT = pathlib.Path("/tmp/audio_pro"); OUT.mkdir(exist_ok=True)
SUPABASE_URL = "https://tpjvalzwkqwttvmszvie.supabase.co"
SUPABASE_KEY = os.getenv("SUPABASE_SERVICE_KEY")

# VOZES MASCULINAS — escolhidas para imitar top podcasts mundiais
VOICES = {
    "PT": "pt-BR-AntonioNeural",     # Antonio + pós-proc = estilo Pedro Engler
    "EN": "en-GB-RyanNeural",        # britânico = estilo Sleep Cove (Chris)
    "ES": "es-ES-AlvaroNeural",      # masculino calmo = estilo Alan Disavia
    "JA": "ja-JP-KeitaNeural",       # masculino contemplativo
}

# Texto em FRASES SEPARADAS (cada uma vira clip individual com silêncio depois)
PHRASES = {
"PT": [
    ("Feche os olhos.", 1.5),
    ("Respire fundo.", 1.5),
    ("Deixe o ar entrar.", 1.2),
    ("E sair.", 2.0),
    ("Naturalmente.", 2.0),
    ("Cada respiração te leva mais fundo.", 1.8),
    ("Seus pés relaxam.", 1.5),
    ("Suas pernas pesam.", 1.5),
    ("Seu peito se solta.", 1.5),
    ("Seus ombros descem.", 1.5),
    ("Não há nada que precise ser feito agora.", 2.0),
    ("Apenas respirar.", 3.0),
],
"EN": [
    ("Close your eyes.", 1.5),
    ("Breathe deeply.", 1.5),
    ("Let the air enter.", 1.2),
    ("And leave.", 2.0),
    ("Naturally.", 2.0),
    ("Each breath takes you deeper.", 1.8),
    ("Your feet relax.", 1.5),
    ("Your legs grow heavy.", 1.5),
    ("Your chest softens.", 1.5),
    ("Your shoulders drop.", 1.5),
    ("There is nothing you need to do now.", 2.0),
    ("Only breathing.", 3.0),
],
"ES": [
    ("Cierra los ojos.", 1.5),
    ("Respira profundo.", 1.5),
    ("Deja entrar el aire.", 1.2),
    ("Y salir.", 2.0),
    ("Naturalmente.", 2.0),
    ("Cada respiración te lleva más profundo.", 1.8),
    ("Tus pies se relajan.", 1.5),
    ("Tus piernas pesan.", 1.5),
    ("Tu pecho se suelta.", 1.5),
    ("Tus hombros bajan.", 1.5),
    ("No hay nada que necesites hacer ahora.", 2.0),
    ("Solo respirar.", 3.0),
],
"JA": [
    ("目を閉じてください。", 1.8),
    ("深く息を吸って。", 1.5),
    ("空気を入れて。", 1.2),
    ("そして出して。", 2.0),
    ("自然に。", 2.0),
    ("一呼吸ごとに、もっと深くへ。", 1.8),
    ("足が緩み。", 1.5),
    ("脚が重くなり。", 1.5),
    ("胸が柔らかくなり。", 1.5),
    ("肩が下がります。", 1.5),
    ("今、何もする必要はありません。", 2.0),
    ("ただ呼吸するだけ。", 3.0),
],
}

# ════════════════════════════════════════════════════════════════════════════
# CADEIA DE PROCESSAMENTO ÁUDIO PROFISSIONAL
# ════════════════════════════════════════════════════════════════════════════
AUDIO_FILTER_PRO = (
    # 1. Pitch down + slow (Sleep Cove style depth)
    "asetrate=44100*0.94,"
    "atempo=1.0,"
    # 2. EQ para corpo de voz mais grave
    "lowshelf=g=-2:f=300,"           # corta agudos sutis
    "equalizer=f=180:width_type=h:width=80:g=2,"  # boost 180Hz (peito)
    "lowpass=f=9000,"                 # remove S/T agressivos
    # 3. Compressor suave (consistência)
    "acompressor=threshold=0.1:ratio=3:attack=10:release=200:makeup=2,"
    # 4. Reverb sutil (sensação cavernosa profunda)
    "aecho=0.6:0.5:60:0.25,"
    # 5. Normaliza volume final
    "loudnorm=I=-18:LRA=8:TP=-2"
)

async def gen_tts(text, voice, out, rate="-15%"):
    """Edge TTS — sem reticências, pontuação natural"""
    c = edge_tts.Communicate(text, voice, rate=rate)
    await c.save(str(out))

def process_phrase(speech_mp3, out_aac):
    """Aplica cadeia profissional FFmpeg em UMA frase"""
    subprocess.run(["ffmpeg","-y",
        "-i", str(speech_mp3),
        "-af", AUDIO_FILTER_PRO,
        "-c:a","aac","-b:a","192k","-ar","44100", str(out_aac)],
        capture_output=True, timeout=30)
    return out_aac.exists()

def make_silence(seconds, out_aac):
    """Silêncio puro em AAC"""
    subprocess.run(["ffmpeg","-y",
        "-f","lavfi","-i", f"anullsrc=r=44100:cl=stereo",
        "-t", str(seconds),
        "-c:a","aac","-b:a","192k", str(out_aac)],
        capture_output=True, timeout=15)
    return out_aac.exists()

# Cama ambiente (binaural + chuva brown)
print("🎵 Gerando cama ambiente brown noise...")
bed = OUT / "bed.aac"
subprocess.run(["ffmpeg","-y",
    "-f","lavfi","-i","sine=frequency=528:duration=90",
    "-f","lavfi","-i","sine=frequency=532:duration=90",
    "-f","lavfi","-i","anoisesrc=color=brown:duration=90",
    "-filter_complex",
    "[0:a]volume=0.04[l];[1:a]volume=0.04[r];"
    "[l][r]amerge=inputs=2[bin];"
    "[2:a]highpass=f=150,lowpass=f=3500,volume=0.05[rain];"
    "[bin][rain]amix=inputs=2:duration=longest:normalize=0[out]",
    "-map","[out]","-c:a","aac","-b:a","160k","-ar","44100", str(bed)],
    capture_output=True, timeout=120)

uploaded = []
for lang, phrases in PHRASES.items():
    voice = VOICES[lang]
    print(f"\n🎙️  {lang} ({voice}) — {len(phrases)} frases")
    
    # Gerar e processar cada frase
    phrase_files = []
    for i, (text, pause_after) in enumerate(phrases):
        raw = OUT / f"{lang}_p{i}_raw.mp3"
        processed = OUT / f"{lang}_p{i}_pro.aac"
        silence = OUT / f"{lang}_p{i}_sil.aac"
        
        asyncio.run(gen_tts(text, voice, raw, rate="-15%"))
        if not raw.exists(): continue
        
        process_phrase(raw, processed)
        make_silence(pause_after, silence)
        
        phrase_files.append(processed)
        phrase_files.append(silence)
        print(f"   {i+1}/{len(phrases)}: \"{text[:35]}\" + {pause_after}s pausa")
    
    # Concatenar todas as frases
    concat_list = OUT / f"{lang}_concat.txt"
    with open(concat_list, "w") as f:
        for pf in phrase_files:
            if pf.exists():
                f.write(f"file '{pf.resolve()}'\n")
    
    concat_audio = OUT / f"{lang}_full.aac"
    subprocess.run(["ffmpeg","-y","-f","concat","-safe","0",
                    "-i", str(concat_list),
                    "-c:a","aac","-b:a","192k", str(concat_audio)],
                   capture_output=True, timeout=60)
    
    # Mesclar com cama ambiente
    final = OUT / f"sample_{lang.lower()}_pro.mp3"
    subprocess.run(["ffmpeg","-y",
        "-i", str(concat_audio),
        "-stream_loop","-1","-i", str(bed),
        "-filter_complex",
        "[0:a]volume=1.0,afade=t=in:d=3,afade=t=out:st=999:d=4[s];"
        "[1:a]volume=0.28[a];"
        "[s][a]amix=inputs=2:duration=first[out]",
        "-map","[out]","-c:a","libmp3lame","-b:a","192k","-ar","44100", str(final)],
        capture_output=True, timeout=90)
    
    if final.exists():
        size = final.stat().st_size
        print(f"   ✅ Final: {size//1024} KB | duração: ~{sum(p[1] for p in phrases) + len(phrases)*2}s")
        
        if SUPABASE_KEY:
            with open(final, "rb") as f:
                up = requests.post(
                    f"{SUPABASE_URL}/storage/v1/object/samples/sample_{lang.lower()}_pro.mp3",
                    headers={
                        "apikey": SUPABASE_KEY,
                        "Authorization": f"Bearer {SUPABASE_KEY}",
                        "Content-Type": "audio/mpeg",
                        "x-upsert": "true"
                    }, data=f.read()
                )
                if up.status_code in (200,201):
                    url = f"{SUPABASE_URL}/storage/v1/object/public/samples/sample_{lang.lower()}_pro.mp3"
                    uploaded.append((lang, url))
                    print(f"   🌐 {url}")

print(f"\n✨ {len(uploaded)} amostras PROFISSIONAIS prontas:")
for lang, u in uploaded: print(f"   {lang}: {u}")
