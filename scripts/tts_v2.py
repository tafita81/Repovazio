#!/usr/bin/env python3
"""
tts_v2.py — Gera audio TTS para videos sem audio
Usa Edge TTS (Microsoft PT-BR, gratis, sem SSL issues no GitHub Actions)
"""
import os, asyncio, requests, time
import edge_tts
from supabase import create_client

SB_URL = os.environ["SUPABASE_URL"]
SB_KEY = os.environ["SUPABASE_KEY"]
SB_ANON = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InRwanZhbHp3a3F3dHR2bXN6dmllIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NzYwMzUyOTMsImV4cCI6MjA5MTYxMTI5M30.UEgUo0Mw15ihQZykLAY5QApRzgTXkfIewZFzIgwao3Q"
sb = create_client(SB_URL, SB_KEY)

VOZES = ["pt-BR-FranciscaNeural", "pt-BR-ThalitaMultilingualNeural"]

def get_videos_sem_audio():
    r = sb.table("content_pipeline").select(
        "id,title,script,duracao_min,pub_order"
    ).eq("status", "video_ready").is_("audio_url", None).order("pub_order").limit(5).execute()
    return r.data or []

async def gerar_tts(script, video_id, voz="pt-BR-FranciscaNeural"):
    path = f"/tmp/tts_{video_id}.mp3"
    tts = edge_tts.Communicate(script, voice=voz, rate="-5%")
    await tts.save(path)
    return path

def upload_audio(path, video_id):
    fname = f"audios/v{video_id}.mp3"
    with open(path, "rb") as f:
        audio_bytes = f.read()
    r = requests.post(
        f"{SB_URL}/storage/v1/object/videos/{fname}",
        headers={"apikey": SB_ANON, "Authorization": f"Bearer {SB_ANON}",
                 "Content-Type": "audio/mpeg", "x-upsert": "true"},
        data=audio_bytes
    )
    if r.status_code in [200, 201]:
        url = f"{SB_URL}/storage/v1/object/public/videos/{fname}"
        print(f"    ✓ Audio upload: {url}")
        return url
    print(f"    ⚠ Audio upload erro: {r.status_code}")
    return None

def main():
    print("=== TTS V2 — Edge TTS PT-BR ===")
    videos = get_videos_sem_audio()
    print(f"Videos sem audio: {len(videos)}")
    
    for v in videos:
        vid_id = v["id"]
        script = v.get("script","")
        if not script:
            print(f"  #{vid_id}: sem script")
            continue
        
        print(f"\n  #{vid_id} {v.get('title','')[:50]}")
        print(f"    {len(script)} chars")
        
        try:
            path = asyncio.run(gerar_tts(script, vid_id))
            audio_url = upload_audio(path, vid_id)
            if audio_url:
                sb.table("content_pipeline").update({
                    "audio_url": audio_url
                }).eq("id", vid_id).execute()
                print(f"    ✓ audio_url salvo")
        except Exception as e:
            print(f"    ERRO: {e}")

if __name__ == "__main__":
    main()
