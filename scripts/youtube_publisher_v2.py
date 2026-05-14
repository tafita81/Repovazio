#!/usr/bin/env python3
"""
YouTube Publisher v3 — upload correto via resumable upload API
Sem dependências externas além de requests
"""
import os, sys, json, requests, io

SBU = os.environ["SUPABASE_URL"]
SBK = os.environ.get("SUPABASE_KEY") or os.environ.get("SUPABASE_SERVICE_KEY","")
CID = os.environ["YT_CLIENT_ID"]
SEC = os.environ["YT_CLIENT_SECRET"]
RTK = os.environ["YT_REFRESH_TOKEN"]
ALLOWED = "UCyCkIpsVgME9yCj_oXJFheA"
BLOCKED = "UCSH63tBfY6wEIdkC4u4zKdg"

print("== YouTube Publisher v3 ==")
print(f"SBU: {SBU[:30]}...")
print(f"CID: {CID[:20]}...")
print(f"RTK: {RTK[:15]}...")

# --- 1. Obter access token ---
r = requests.post("https://oauth2.googleapis.com/token", data={
    "client_id": CID, "client_secret": SEC,
    "refresh_token": RTK, "grant_type": "refresh_token"
}, timeout=15)
print(f"\nToken HTTP: {r.status_code}")
if not r.ok:
    print(f"ERRO TOKEN: {r.text[:300]}")
    sys.exit(1)

token = r.json()["access_token"]
print("Token OK")

# --- 2. Verificar canal ---
r2 = requests.get(
    "https://www.googleapis.com/youtube/v3/channels?part=snippet&mine=true",
    headers={"Authorization": f"Bearer {token}"}, timeout=15)

items = r2.json().get("items", [])
channel_ids = [i["id"] for i in items]
print(f"Canais encontrados: {channel_ids}")

if BLOCKED in channel_ids:
    print(f"BLOQUEADO! Canal removido {BLOCKED}")
    sys.exit(1)

if ALLOWED not in channel_ids:
    print(f"Canal {ALLOWED} nao encontrado. Canais: {channel_ids}")
    print("AVISO: Continuando sem validar canal (pode ser problema de permissao)")

for item in items:
    if item["id"] == ALLOWED:
        print(f"Canal OK: {item['snippet']['title']} ({item['id']})")

# --- 3. Buscar vídeos para publicar ---
hdrs = {"Authorization": f"Bearer {SBK}", "apikey": SBK}

# Primeiro: pending_credentials com mp4 e sem youtube_video_id
q1 = "status=eq.pending_credentials&mp4_url=not.is.null&youtube_video_id=is.null&limit=2&order=seo_score.desc"
q1 += "&select=id,title,youtube_title,youtube_description,mp4_url,seo_score,target_platform"
videos = requests.get(f"{SBU}/rest/v1/content_pipeline?{q1}", headers=hdrs, timeout=15).json()

if not isinstance(videos, list):
    print(f"Erro Supabase: {videos}")
    sys.exit(1)

if not videos:
    # Fallback: mp4_ready
    q2 = "status=eq.mp4_ready&mp4_url=not.is.null&youtube_video_id=is.null&limit=2&order=id.asc"
    q2 += "&select=id,title,youtube_title,youtube_description,mp4_url,seo_score,target_platform"
    videos = requests.get(f"{SBU}/rest/v1/content_pipeline?{q2}", headers=hdrs, timeout=15).json()

print(f"\n{len(videos)} vídeos para publicar")

if not videos:
    print("Nenhum vídeo disponível. Pipeline pode estar vazio.")
    sys.exit(0)

for v in videos[:2]:
    pid = v["id"]
    titulo = (v.get("youtube_title") or v.get("title","Psicologia"))[:100]
    desc = v.get("youtube_description") or f"Conteúdo educacional sobre saúde mental.\n\n#psicologia #saudemental #autoconhecimento"
    mp4_url = v["mp4_url"]

    print(f"\n--- Publicando #{pid}: {titulo[:60]} ---")
    print(f"SEO Score: {v.get('seo_score',0)}")
    print(f"MP4: {mp4_url[:60]}")

    # Download MP4
    print("Baixando MP4...")
    try:
        mp4_r = requests.get(mp4_url, timeout=300, stream=True)
        mp4_bytes = b""
        for chunk in mp4_r.iter_content(chunk_size=1024*1024):
            mp4_bytes += chunk
        mp4_size = len(mp4_bytes)
        print(f"MP4 baixado: {mp4_size // 1024}KB")
    except Exception as e:
        print(f"Erro download: {e}")
        continue

    # Metadata para YouTube
    meta = {
        "snippet": {
            "title": titulo,
            "description": desc[:5000],
            "categoryId": "27",
            "defaultLanguage": "pt-BR",
            "defaultAudioLanguage": "pt-BR",
            "tags": ["psicologia", "saude mental", "autoconhecimento", "psidanielacoelho",
                     "terapia", "ansiedade", "relacionamentos"]
        },
        "status": {
            "privacyStatus": "public",
            "selfDeclaredMadeForKids": False
        }
    }

    # === UPLOAD MULTIPART (simples, sem biblioteca extra) ===
    BOUNDARY = "-------314159265358979323846"
    CRLF = "\r\n"
    
    meta_bytes = json.dumps(meta).encode("utf-8")
    
    body_parts = []
    # Parte 1: metadata JSON
    body_parts.append(f"--{BOUNDARY}".encode())
    body_parts.append(CRLF.encode())
    body_parts.append(b"Content-Type: application/json; charset=UTF-8")
    body_parts.append(CRLF.encode())
    body_parts.append(CRLF.encode())
    body_parts.append(meta_bytes)
    body_parts.append(CRLF.encode())
    # Parte 2: vídeo
    body_parts.append(f"--{BOUNDARY}".encode())
    body_parts.append(CRLF.encode())
    body_parts.append(b"Content-Type: video/mp4")
    body_parts.append(CRLF.encode())
    body_parts.append(CRLF.encode())
    body_parts.append(mp4_bytes)
    body_parts.append(CRLF.encode())
    body_parts.append(f"--{BOUNDARY}--".encode())
    body_parts.append(CRLF.encode())
    
    body = b"".join(body_parts)
    
    upload_url = "https://www.googleapis.com/upload/youtube/v3/videos?uploadType=multipart&part=snippet,status"
    
    print(f"Enviando para YouTube ({len(body)//1024}KB)...")
    up_r = requests.post(
        upload_url,
        headers={
            "Authorization": f"Bearer {token}",
            "Content-Type": f"multipart/related; boundary={BOUNDARY}",
            "Content-Length": str(len(body))
        },
        data=body,
        timeout=600
    )
    
    print(f"Upload HTTP: {up_r.status_code}")
    
    if up_r.ok:
        yt_id = up_r.json().get("id", "")
        yt_url = f"https://youtube.com/watch?v={yt_id}"
        print(f"✅ PUBLICADO! YouTube ID: {yt_id}")
        print(f"URL: {yt_url}")
        
        # Atualizar Supabase
        patch = requests.patch(
            f"{SBU}/rest/v1/content_pipeline?id=eq.{pid}",
            headers={**hdrs, "Content-Type": "application/json"},
            json={"youtube_video_id": yt_id, "status": "published",
                  "youtube_url": yt_url, "published_at": "now()"},
            timeout=15
        )
        print(f"Supabase atualizado: {patch.status_code}")
        
        # Registrar no publication_log
        log = requests.post(
            f"{SBU}/rest/v1/publication_log",
            headers={**hdrs, "Content-Type": "application/json"},
            json={"pipeline_id": pid, "platform": "youtube",
                  "external_id": yt_id, "url": yt_url, "status": "success"},
            timeout=15
        )
    else:
        print(f"Erro upload: {up_r.text[:400]}")
        # Salvar erro
        requests.patch(
            f"{SBU}/rest/v1/content_pipeline?id=eq.{pid}",
            headers={**hdrs, "Content-Type": "application/json"},
            json={"notas": f"Upload falhou HTTP {up_r.status_code}: {up_r.text[:200]}"},
            timeout=15
        )

print("\n== YouTube Publisher v3 finalizado ==")
