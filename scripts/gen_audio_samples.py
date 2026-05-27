"""
gen_audio_samples.py — Gera samples de áudio nas 9 línguas + uploads p/ Supabase
Roda no GitHub Actions (Edge TTS funciona lá, ao contrário do sandbox local)
"""
import os, asyncio, edge_tts, subprocess, pathlib, requests

OUT = pathlib.Path("/tmp/samples"); OUT.mkdir(exist_ok=True)
SUPABASE_URL = "https://tpjvalzwkqwttvmszvie.supabase.co"
SUPABASE_KEY = os.getenv("SUPABASE_SERVICE_KEY")

SAMPLES = {
"PT": ("pt-BR-AntonioNeural",
 "Feche os olhos agora... respire fundo, devagar... sinta o ar entrando... e saindo. "
 "Eu sou Daniela Coelho. Técnica um. O Efeito Espelho. Tanya Chartrand de Duke comprovou em 1999 "
 "que imitação sutil libera ocitocina. Narcisistas usam isso para te capturar nos primeiros minutos."),
"EN": ("en-US-GuyNeural",
 "Close your eyes now... breathe in deeply, slowly... feel the air entering... and leaving. "
 "I am Daniela Coelho. Technique one. The Mirror Effect. Tanya Chartrand at Duke proved in 1999 "
 "that subtle mimicry releases oxytocin. Narcissists use this to capture you in the first minutes."),
"ES": ("es-ES-AlvaroNeural",
 "Cierra los ojos ahora... respira hondo, despacio... siente el aire entrando... y saliendo. "
 "Soy Daniela Coelho. Técnica uno. El Efecto Espejo. Tanya Chartrand de Duke comprobó en 1999."),
"JA": ("ja-JP-KeitaNeural",
 "今、目を閉じてください... 深く、ゆっくりと息を吸って... 私は行動研究者ダニエラ・コエーリョです。"
 "テクニック一。ミラー効果。デューク大学のターニャ・チャートランドが千九百九十九年に証明しました。"),
}

async def gen_tts(text, voice, out, rate="-12%"):
    c = edge_tts.Communicate(text, voice, rate=rate)
    await c.save(str(out))

# Cama ambiente (binaural + chuva) — 60s loop
print("🎵 Gerando cama ambiente...")
bed = OUT / "bed.aac"
subprocess.run(["ffmpeg","-y",
    "-f","lavfi","-i","sine=frequency=528:duration=60",
    "-f","lavfi","-i","sine=frequency=532:duration=60",
    "-f","lavfi","-i","anoisesrc=color=pink:duration=60",
    "-filter_complex",
    "[0:a]volume=0.05[l];[1:a]volume=0.05[r];"
    "[l][r]amerge=inputs=2[bin];"
    "[2:a]highpass=f=200,lowpass=f=4000,volume=0.025[rain];"
    "[bin][rain]amix=inputs=2:duration=longest:normalize=0[out]",
    "-map","[out]","-c:a","aac","-b:a","160k","-ar","44100", str(bed)],
    capture_output=True, timeout=120)

# Gerar samples + upload
uploaded = []
for lang, (voice, text) in SAMPLES.items():
    print(f"\n🎙️  {lang} ({voice})")
    speech = OUT / f"speech_{lang.lower()}.mp3"
    asyncio.run(gen_tts(text, voice, speech))
    
    final = OUT / f"sample_{lang.lower()}.mp3"
    subprocess.run(["ffmpeg","-y",
        "-i", str(speech),
        "-stream_loop","-1","-i", str(bed),
        "-filter_complex",
        "[0:a]volume=1.0[s];[1:a]volume=0.25[a];[s][a]amix=inputs=2:duration=first[out]",
        "-map","[out]","-c:a","libmp3lame","-b:a","192k","-ar","44100", str(final)],
        capture_output=True, timeout=60)
    
    if final.exists():
        size = final.stat().st_size
        print(f"   ✅ {size//1024} KB")
        
        # Upload para Supabase storage (bucket samples, público)
        if SUPABASE_KEY:
            with open(final, "rb") as f:
                r = requests.post(
                    f"{SUPABASE_URL}/storage/v1/object/samples/sample_{lang.lower()}.mp3",
                    headers={
                        "apikey": SUPABASE_KEY,
                        "Authorization": f"Bearer {SUPABASE_KEY}",
                        "Content-Type": "audio/mpeg",
                        "x-upsert": "true"
                    },
                    data=f.read()
                )
                if r.status_code in (200, 201):
                    url = f"{SUPABASE_URL}/storage/v1/object/public/samples/sample_{lang.lower()}.mp3"
                    uploaded.append(url)
                    print(f"   🌐 {url}")
                else:
                    print(f"   ⚠️  Upload falhou: {r.status_code} {r.text[:100]}")

print(f"\n✨ {len(uploaded)} amostras prontas")
for u in uploaded: print(f"   {u}")
