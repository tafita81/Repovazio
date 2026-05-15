#!/usr/bin/env python3
"""tts_v2.py Cerebro V15 — ElevenLabs Sarah PT-BR (voz realista indetectavel)"""
import os, asyncio, requests, time
from supabase import create_client

SB_URL = os.environ["SUPABASE_URL"]
SB_KEY = os.environ["SUPABASE_KEY"]
sb = create_client(SB_URL, SB_KEY)
SB_ANON = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InRwanZhbHp3a3F3dHR2bXN6dmllIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NzYwMzUyOTMsImV4cCI6MjA5MTYxMTI5M30.UEgUo0Mw15ihQZykLAY5QApRzgTXkfIewZFzIgwao3Q"
ELEVENLABS_KEY = os.environ.get("ELEVENLABS_API_KEY","")
# Sarah EXAVITQu4vr4xnSDxMaL - voz mais natural e emocional
# Rachel 21m00Tcm4TlvDq8ikWAM - segunda opcao
VOICE_ID = "EXAVITQu4vr4xnSDxMaL"
MODEL    = "eleven_multilingual_v2"

def gerar_elevenlabs(script, video_id):
    if not ELEVENLABS_KEY:
        print("    ElevenLabs key ausente")
        return None
    try:
        r = requests.post(
            f"https://api.elevenlabs.io/v1/text-to-speech/{VOICE_ID}",
            headers={"xi-api-key": ELEVENLABS_KEY, "Content-Type": "application/json"},
            json={
                "text": script,
                "model_id": MODEL,
                "language_code": "pt",
                "voice_settings": {
                    "stability": 0.35,
                    "similarity_boost": 0.85,
                    "style": 0.60,
                    "use_speaker_boost": True
                },
                "output_format": "mp3_44100_192"
            },
            timeout=180
        )
        print(f"    ElevenLabs: {r.status_code}")
        if r.status_code == 200:
            path = f"/tmp/el_{video_id}.mp3"
            with open(path,"wb") as f: f.write(r.content)
            print(f"    OK ElevenLabs Sarah: {os.path.getsize(path):,} bytes")
            return path
        else:
            try: detail = r.json().get("detail","")
            except: detail = r.text[:200]
            print(f"    ElevenLabs erro: {detail}")
    except Exception as e:
        print(f"    ElevenLabs exception: {e}")
    return None

async def gerar_edge_fallback(script, video_id):
    try:
        import edge_tts
        path = f"/tmp/edge_{video_id}.mp3"
        tts = edge_tts.Communicate(script, voice="pt-BR-ThalitaMultilingualNeural", rate="-3%")
        await tts.save(path)
        print(f"    Edge TTS fallback: {os.path.getsize(path):,} bytes")
        return path
    except Exception as e:
        print(f"    Edge TTS falhou: {e}")
    return None

def upload_audio(path, video_id):
    fname = f"audios/v{video_id}.mp3"
    with open(path,"rb") as f: data = f.read()
    r = requests.post(
        f"{SB_URL}/storage/v1/object/videos/{fname}",
        headers={"apikey":SB_ANON,"Authorization":f"Bearer {SB_ANON}",
                 "Content-Type":"audio/mpeg","x-upsert":"true"},
        data=data)
    if r.status_code in [200,201]:
        return f"{SB_URL}/storage/v1/object/public/videos/{fname}"
    print(f"    upload audio erro: {r.status_code}")
    return None

def get_sem_audio():
    r = sb.table("content_pipeline").select(
        "id,title,script,duracao_min,pub_order"
    ).eq("status","video_ready").is_("audio_url",None).order("pub_order").limit(5).execute()
    return r.data or []

def main():
    print("=== TTS V15 ElevenLabs Sarah PT-BR ===")
    print(f"ElevenLabs: {'OK' if ELEVENLABS_KEY else 'AUSENTE fallback Edge TTS'}")
    videos = get_sem_audio()
    print(f"Videos sem audio: {len(videos)}")
    for v in videos:
        vid_id = v["id"]
        script = (v.get("script") or "").strip()
        if not script: continue
        print(f"\n  #{vid_id} {v.get('title','')[:50]}")
        path = gerar_elevenlabs(script, vid_id)
        if not path:
            path = asyncio.run(gerar_edge_fallback(script, vid_id))
        if not path: continue
        url = upload_audio(path, vid_id)
        if url:
            vname = f"ElevenLabs_Sarah_{MODEL}" if "el_" in path else "Edge_Thalita"
            sb.table("content_pipeline").update({"audio_url":url,"voice_name":vname}).eq("id",vid_id).execute()
            print(f"    OK audio salvo ({vname})")

if __name__ == "__main__":
    main()
