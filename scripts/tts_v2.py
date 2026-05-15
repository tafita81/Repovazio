#!/usr/bin/env python3
"""tts_v2.py V15.1 — ElevenLabs Sarah PT-BR — busca mp4_ready sem audio"""
import os, asyncio, requests, time
from supabase import create_client

SB_URL = os.environ["SUPABASE_URL"]
SB_KEY = os.environ["SUPABASE_KEY"]
sb = create_client(SB_URL, SB_KEY)
SB_ANON = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InRwanZhbHp3a3F3dHR2bXN6dmllIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NzYwMzUyOTMsImV4cCI6MjA5MTYxMTI5M30.UEgUo0Mw15ihQZykLAY5QApRzgTXkfIewZFzIgwao3Q"
EL_KEY = os.environ.get("ELEVENLABS_API_KEY","")
VOICE_ID = "EXAVITQu4vr4xnSDxMaL"  # Sarah — mais natural e emocional
MODEL    = "eleven_multilingual_v2"

def gerar_elevenlabs(script, video_id):
    if not EL_KEY:
        print("    ElevenLabs key ausente")
        return None
    try:
        r = requests.post(
            f"https://api.elevenlabs.io/v1/text-to-speech/{VOICE_ID}",
            headers={"xi-api-key": EL_KEY, "Content-Type": "application/json"},
            json={
                "text": script, "model_id": MODEL, "language_code": "pt",
                "voice_settings": {
                    "stability": 0.35, "similarity_boost": 0.85,
                    "style": 0.60, "use_speaker_boost": True
                },
                "output_format": "mp3_44100_192"
            }, timeout=180)
        print(f"    ElevenLabs: {r.status_code}")
        if r.status_code == 200:
            p = f"/tmp/el_{video_id}.mp3"
            with open(p,"wb") as f: f.write(r.content)
            print(f"    OK Sarah: {os.path.getsize(p):,}B")
            return p
        try: print(f"    erro: {r.json().get('detail','')[:150]}")
        except: print(f"    erro: {r.text[:150]}")
    except Exception as e:
        print(f"    EL exception: {e}")
    return None

async def gerar_edge(script, video_id):
    try:
        import edge_tts
        p = f"/tmp/edge_{video_id}.mp3"
        tts = edge_tts.Communicate(script, voice="pt-BR-ThalitaMultilingualNeural", rate="-3%")
        await tts.save(p)
        print(f"    Edge TTS fallback: {os.path.getsize(p):,}B")
        return p
    except Exception as e:
        print(f"    Edge falhou: {e}")
    return None

def upload_audio(path, video_id):
    fname = f"audios/v{video_id}.mp3"
    with open(path,"rb") as f: data = f.read()
    r = requests.post(f"{SB_URL}/storage/v1/object/videos/{fname}",
        headers={"apikey":SB_ANON,"Authorization":f"Bearer {SB_ANON}",
                 "Content-Type":"audio/mpeg","x-upsert":"true"}, data=data)
    if r.status_code in [200,201]:
        return f"{SB_URL}/storage/v1/object/public/videos/{fname}"
    print(f"    upload erro: {r.status_code}")
    return None

def main():
    print("=== TTS V15.1 ElevenLabs Sarah PT-BR ===")
    print(f"ElevenLabs: {'OK' if EL_KEY else 'AUSENTE - Edge TTS fallback'}")
    # Buscar mp4_ready SEM audio (passo 1 do pipeline)
    r = sb.table("content_pipeline").select(
        "id,title,script,duracao_min,pub_order"
    ).eq("status","mp4_ready").is_("audio_url",None).order("pub_order").limit(5).execute()
    videos = r.data or []
    print(f"Videos sem audio: {len(videos)}")
    for v in videos:
        vid_id = v["id"]
        script = (v.get("script") or "").strip()
        if not script:
            print(f"  #{vid_id}: sem script")
            continue
        print(f"\n  #{vid_id} {v.get('title','')[:50]}")
        print(f"    {len(script)} chars | {len(script.split())} palavras")
        path = gerar_elevenlabs(script, vid_id)
        if not path:
            path = asyncio.run(gerar_edge(script, vid_id))
        if not path:
            print("    todos TTS falharam")
            continue
        url = upload_audio(path, vid_id)
        if url:
            vname = f"ElevenLabs_Sarah_{MODEL}" if "el_" in path else "Edge_Thalita"
            sb.table("content_pipeline").update(
                {"audio_url":url,"voice_name":vname}
            ).eq("id",vid_id).execute()
            print(f"    OK audio_url salvo ({vname})")

if __name__ == "__main__":
    main()
