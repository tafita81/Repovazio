#!/usr/bin/env python3
"""
tts_v4.py — Cerebro V4 — Estilo School of Life / Kurzgesagt
Voz: George (ElevenLabs) — masculina, calma, intelectual, indetectavel como IA
Fallback: Daniel (jornalistica clara) → Adam (grave narrativa) → Edge Thalita
"""
import os, asyncio, requests, time, subprocess
from supabase import create_client

SB_URL = os.environ["SUPABASE_URL"]
SB_KEY = os.environ["SUPABASE_KEY"]
sb = create_client(SB_URL, SB_KEY)
SB_ANON = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InRwanZhbHp3a3F3dHR2bXN6dmllIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NzYwMzUyOTMsImV4cCI6MjA5MTYxMTI5M30.UEgUo0Mw15ihQZykLAY5QApRzgTXkfIewZFzIgwao3Q"
EL_KEY = os.environ.get("ELEVENLABS_API_KEY","")
MODEL   = "eleven_multilingual_v2"

# Vozes masculinas em ordem de preferencia
# George: warm british intellectual (School of Life)
# Daniel: authoritative clear news presenter
# Adam: deep american narrative
VOICES = [
    ("George", "JBFqnCBsd6RMkjVDRZzb"),
    ("Daniel", "onwK4e9ZLuTAKqWW03F9"),
    ("Adam",   "pNInz6obpgDQGcFmaJgB"),
]

def gerar_elevenlabs(script, video_id):
    if not EL_KEY: return None, None
    for voz_nome, voz_id in VOICES:
        try:
            r = requests.post(
                "https://api.elevenlabs.io/v1/text-to-speech/" + voz_id,
                headers={"xi-api-key": EL_KEY, "Content-Type": "application/json"},
                json={
                    "text": script,
                    "model_id": MODEL,
                    "language_code": "pt",
                    "voice_settings": {
                        "stability": 0.42,        # alguma variacao = mais humano
                        "similarity_boost": 0.82,
                        "style": 0.28,            # expressivo mas controlado
                        "use_speaker_boost": True
                    },
                    "output_format": "mp3_44100_192"
                }, timeout=180)
            print("    " + voz_nome + " (" + voz_id[:8] + "...): " + str(r.status_code))
            if r.status_code == 200:
                path = "/tmp/el_" + str(video_id) + ".mp3"
                with open(path,"wb") as f: f.write(r.content)
                print("    OK " + voz_nome + ": " + str(os.path.getsize(path)) + "B")
                return path, voz_nome
            try: print("    err: " + str(r.json().get("detail",""))[:120])
            except: print("    err: " + r.text[:120])
        except Exception as e:
            print("    exc " + voz_nome + ": " + str(e)[:80])
    return None, None

async def gerar_edge(script, video_id):
    try:
        import edge_tts
        # ThalitaMultilingualNeural e o melhor disponivel no Edge para PT-BR
        path = "/tmp/edge_" + str(video_id) + ".mp3"
        tts = edge_tts.Communicate(script, voice="pt-BR-ThalitaMultilingualNeural", rate="-5%")
        await tts.save(path)
        print("    Edge TTS Thalita fallback: " + str(os.path.getsize(path)) + "B")
        return path
    except Exception as e:
        print("    Edge falhou: " + str(e))
    return None

def upload_audio(path, video_id, voz_nome):
    fname = "audios/v" + str(video_id) + "_v4.mp3"
    with open(path,"rb") as f: data = f.read()
    r = requests.post(
        SB_URL + "/storage/v1/object/videos/" + fname,
        headers={"apikey": SB_KEY, "Authorization": "Bearer " + SB_KEY,
                 "Content-Type": "audio/mpeg", "x-upsert": "true"}, data=data)
    if r.status_code in [200,201]:
        return SB_URL + "/storage/v1/object/public/videos/" + fname
    print("    upload err: " + str(r.status_code))
    return None

def main():
    print("=== TTS V4 — Voz Masculina George (School of Life / Kurzgesagt) ===")
    print("ElevenLabs: " + ("OK" if EL_KEY else "AUSENTE"))
    r = sb.table("content_pipeline").select(
        "id,title,script,duracao_min,pub_order"
    ).eq("status","mp4_ready").is_("audio_url",None).order("pub_order").limit(5).execute()
    videos = r.data or []
    print("Videos sem audio: " + str(len(videos)))
    for v in videos:
        vid_id = v["id"]
        script = (v.get("script") or "").strip()
        if not script: continue
        print("\n  #" + str(vid_id) + " " + str(v.get("title",""))[:50])
        path, voz = gerar_elevenlabs(script, vid_id)
        if not path:
            path = asyncio.run(gerar_edge(script, vid_id))
            voz = "Edge_Thalita_fallback"
        if not path: continue
        url = upload_audio(path, vid_id, voz)
        if url:
            sb.table("content_pipeline").update(
                {"audio_url": url, "voice_name": voz + "_" + MODEL}
            ).eq("id", vid_id).execute()
            print("    OK audio (" + str(voz) + ")")

if __name__ == "__main__":
    main()
