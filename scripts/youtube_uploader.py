#!/usr/bin/env python3
"""
youtube_uploader.py
Upload automático de vídeos para o YouTube usando OAuth2.
Processa a fila do Supabase: en_channel_queue + shorts_pipeline.
"""
import os, requests, json, pathlib

SB_URL = os.getenv("SUPABASE_URL","https://tpjvalzwkqwttvmszvie.supabase.co")
SB_KEY = os.getenv("SUPABASE_SERVICE_KEY","")
YT_CID = os.getenv("YOUTUBE_CLIENT_ID","")
YT_SEC = os.getenv("YOUTUBE_CLIENT_SECRET","")
YT_REF = os.getenv("YOUTUBE_REFRESH_TOKEN","")
SBH    = {"apikey":SB_KEY,"Authorization":f"Bearer {SB_KEY}","Content-Type":"application/json"}

def get_access_token():
    if not YT_REF: return None
    r = requests.post("https://oauth2.googleapis.com/token", data={
        "refresh_token":YT_REF,"client_id":YT_CID,
        "client_secret":YT_SEC,"grant_type":"refresh_token"
    }, timeout=20)
    return r.json().get("access_token") if r.status_code == 200 else None

def upload_video(token, video_path, titulo, descricao, tags):
    """Upload via YouTube Data API v3 — resumable upload"""
    # Step 1: initiate
    metadata = {
        "snippet": {
            "title": titulo[:100],
            "description": descricao[:5000],
            "tags": tags[:500].split(",") if isinstance(tags,str) else tags,
            "categoryId": "27",  # Education
            "defaultLanguage": "pt",
        },
        "status": {"privacyStatus": "public", "selfDeclaredMadeForKids": False},
    }
    r1 = requests.post(
        "https://www.googleapis.com/upload/youtube/v3/videos"
        "?uploadType=resumable&part=snippet,status",
        headers={"Authorization": f"Bearer {token}",
                 "Content-Type": "application/json",
                 "X-Upload-Content-Type": "video/mp4"},
        json=metadata, timeout=30)
    
    if r1.status_code not in (200,201):
        print(f"  Init err: {r1.status_code}")
        return None
    
    upload_url = r1.headers.get("Location")
    if not upload_url: return None
    
    # Step 2: upload
    with open(video_path, "rb") as f:
        data = f.read()
    
    r2 = requests.put(upload_url,
        headers={"Content-Type": "video/mp4",
                 "Content-Length": str(len(data))},
        data=data, timeout=600)
    
    if r2.status_code in (200,201):
        vid_id = r2.json().get("id","")
        print(f"  ✅ Uploaded: https://youtu.be/{vid_id}")
        return vid_id
    
    print(f"  Upload err: {r2.status_code}")
    return None

def run():
    print("=== YOUTUBE UPLOADER ===")
    token = get_access_token()
    if not token:
        print("Sem OAuth token. Autorizar em:")
        print("https://accounts.google.com/o/oauth2/auth"
              "?client_id=552651753048-p26lb7afjs5f75nvfrmmf4eb1ps4sc98.apps.googleusercontent.com"
              "&redirect_uri=urn:ietf:wg:oauth:2.0:oob"
              "&scope=https://www.googleapis.com/auth/youtube.upload"
              "&response_type=code&access_type=offline&prompt=consent"
              "&login_hint=tafita81@gmail.com")
        return
    
    print(f"Token OK: {token[:20]}...")
    
    # Buscar vídeos prontos na fila
    r = requests.get(f"{SB_URL}/rest/v1/en_channel_queue?status=eq.mp4_ready&limit=5",
        headers=SBH, timeout=10)
    videos = r.json() if r.status_code == 200 else []
    print(f"Vídeos prontos para upload: {len(videos)}")
    
    for v in videos:
        mp4 = v.get("script_en","")  # path do mp4 salvo
        if not mp4 or not pathlib.Path(mp4).exists():
            continue
        vid_id = upload_video(token, mp4, v["titulo_en"],
            "Psychology content based on peer-reviewed research.\n\nDaniela Coelho · Psychology Research & Content",
            "psychology,mental health,anxiety,narcissism,528hz,healing")
        if vid_id:
            requests.patch(f"{SB_URL}/rest/v1/en_channel_queue?id=eq.{v['id']}",
                headers=SBH, json={"status":"published","canal_destino":vid_id}, timeout=10)

if __name__ == "__main__":
    run()
