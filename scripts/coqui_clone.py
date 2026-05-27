"""
coqui_clone.py — Clonagem voz CC0 (Phil Chenevert) → Coqui XTTS v2
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

LEGAL: usa voz Phil Chenevert (LibriVox, dedicada ao domínio público).
       Output comercializável (Coqui FAQ confirma).

QUALIDADE: zero-shot clone igual ElevenLabs, suporta 16 idiomas.
"""
import os, subprocess, pathlib, requests

# Aceita TOS automaticamente (evita prompt interativo)
os.environ["COQUI_TOS_AGREED"] = "1"

OUT = pathlib.Path("/tmp/coqui_out"); OUT.mkdir(exist_ok=True)
SUPABASE_URL = "https://tpjvalzwkqwttvmszvie.supabase.co"
SUPABASE_KEY = os.getenv("SUPABASE_SERVICE_KEY")

# ════════════════════════════════════════════════════════════════════════════
# REFERÊNCIA: Phil Chenevert lendo Around the World in 80 Days (LibriVox CC0)
# ════════════════════════════════════════════════════════════════════════════
REF_URL = "https://archive.org/download/around_world_80_days_pc_1404_librivox/aroundtheworldin80days_01_verne_64kb.mp3"
REF_MP3 = OUT / "phil_ref.mp3"
REF_WAV = OUT / "phil_ref.wav"

print("📥 Baixando referência Phil Chenevert (LibriVox)...")
r = requests.get(REF_URL, timeout=180, stream=True)
with open(REF_MP3, "wb") as f:
    for chunk in r.iter_content(chunk_size=65536):
        f.write(chunk)
print(f"   ✅ {REF_MP3.stat().st_size//1024} KB baixado")

# Trim 20s limpo (pula intro LibriVox ~18s)
print("✂️  Cortando 20s clean (skip intro LibriVox)...")
subprocess.run(["ffmpeg","-y","-i", str(REF_MP3),
    "-ss","00:00:20","-t","20",  # 20s a partir do segundo 20
    "-ac","1","-ar","22050",      # XTTS prefere mono 22050Hz
    "-c:a","pcm_s16le", str(REF_WAV)],
    capture_output=True, check=True)
print(f"   ✅ Referência: {REF_WAV.stat().st_size//1024} KB")

# ════════════════════════════════════════════════════════════════════════════
# CARREGAR XTTS v2 (primeira vez baixa modelo ~1.8GB, depois cache)
# ════════════════════════════════════════════════════════════════════════════
print("\n🧠 Carregando Coqui XTTS v2 (CPU)...")
from TTS.api import TTS
tts = TTS("tts_models/multilingual/multi-dataset/xtts_v2", gpu=False, progress_bar=False)
print("   ✅ Modelo carregado")

# Textos por idioma — frases naturais, pontuação cria pausas no XTTS
SAMPLES = {
    "pt": "Feche os olhos. Respire fundo. Deixe o ar entrar, e sair, naturalmente. Cada respiração te leva mais fundo. Seus pés relaxam. Suas pernas pesam. Seu peito se solta. Não há nada que você precise fazer agora.",
    "en": "Close your eyes. Breathe deeply. Let the air enter, and leave, naturally. Each breath takes you deeper. Your feet relax. Your legs grow heavy. Your chest softens. There is nothing you need to do now.",
    "es": "Cierra los ojos. Respira profundo. Deja entrar el aire, y salir, naturalmente. Cada respiración te lleva más profundo. Tus pies se relajan. Tus piernas pesan. Tu pecho se suelta. No hay nada que necesites hacer ahora.",
    "ja": "目を閉じてください。深く息を吸ってください。空気を入れて、そして出して、自然に。一呼吸ごとに、もっと深くへ。足が緩み、脚が重くなり、胸が柔らかくなります。今、何もする必要はありません。",
}

# Cama ambiente (binaural 528Hz + chuva brown noise)
print("\n🎵 Gerando cama ambiente...")
bed = OUT / "bed.aac"
subprocess.run(["ffmpeg","-y",
    "-f","lavfi","-i","sine=frequency=528:duration=60",
    "-f","lavfi","-i","sine=frequency=532:duration=60",
    "-f","lavfi","-i","anoisesrc=color=brown:duration=60",
    "-filter_complex",
    "[0:a]volume=0.04[l];[1:a]volume=0.04[r];"
    "[l][r]amerge=inputs=2[bin];"
    "[2:a]highpass=f=150,lowpass=f=3500,volume=0.05[rain];"
    "[bin][rain]amix=inputs=2:duration=longest:normalize=0[out]",
    "-map","[out]","-c:a","aac","-b:a","160k","-ar","44100", str(bed)],
    capture_output=True, timeout=120)

# Gerar cada idioma
uploaded = []
import time
for lang, text in SAMPLES.items():
    t0 = time.time()
    print(f"\n🎙️  {lang} — clonando voz Phil + gerando '{text[:35]}...'")
    
    raw_wav = OUT / f"raw_{lang}.wav"
    try:
        tts.tts_to_file(
            text=text,
            speaker_wav=str(REF_WAV),
            language=lang,
            file_path=str(raw_wav),
            speed=0.85  # 15% mais lento para sleep
        )
    except Exception as e:
        print(f"   ❌ Erro XTTS: {e}")
        continue
    
    dt = time.time() - t0
    print(f"   ⏱️  Gerado em {dt:.1f}s | {raw_wav.stat().st_size//1024} KB")
    
    # Mesclar voz clonada + cama ambiente
    final = OUT / f"sample_{lang}_clone.mp3"
    subprocess.run(["ffmpeg","-y",
        "-i", str(raw_wav),
        "-stream_loop","-1","-i", str(bed),
        "-filter_complex",
        "[0:a]volume=1.0,afade=t=in:d=2,afade=t=out:st=999:d=3[s];"
        "[1:a]volume=0.25[a];"
        "[s][a]amix=inputs=2:duration=first[out]",
        "-map","[out]","-c:a","libmp3lame","-b:a","192k","-ar","44100", str(final)],
        capture_output=True, timeout=60)
    
    if final.exists() and SUPABASE_KEY:
        with open(final, "rb") as f:
            r = requests.post(
                f"{SUPABASE_URL}/storage/v1/object/samples/sample_{lang}_clone.mp3",
                headers={
                    "apikey": SUPABASE_KEY,
                    "Authorization": f"Bearer {SUPABASE_KEY}",
                    "Content-Type": "audio/mpeg",
                    "x-upsert": "true"
                }, data=f.read()
            )
            if r.status_code in (200, 201):
                url = f"{SUPABASE_URL}/storage/v1/object/public/samples/sample_{lang}_clone.mp3"
                uploaded.append((lang, url))
                print(f"   🌐 {url}")

print(f"\n✨ {len(uploaded)} clones prontos:")
for lang, u in uploaded:
    print(f"   {lang}: {u}")
