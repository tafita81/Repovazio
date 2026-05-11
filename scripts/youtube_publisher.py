#!/usr/bin/env python3
"""
youtube_publisher.py — Publicador automático no YouTube
Canal: UCyCkIpsVgME9yCj_oXJFheA (@psidanielacoelho)
Busca mp4_ready do Supabase + faz upload via YouTube Data API v3
"""
import os, json, requests, time
from datetime import datetime, timezone

SBU = os.getenv("SBU","https://tpjvalzwkqwttvmszvie.supabase.co")
SBK = os.getenv("SBK","")
YT_CLIENT_ID = os.getenv("YT_CLIENT_ID","")
YT_SECRET    = os.getenv("YT_CLIENT_SECRET","")
YT_REFRESH   = os.getenv("YT_REFRESH_TOKEN","")
H_SB = {"apikey":SBK,"Authorization":f"Bearer {SBK}","Content-Type":"application/json"}

def log(msg): print(f"[{datetime.now().strftime('%H:%M:%S')}] {msg}")

def sb(method, path, data=None):
    r = requests.request(method, SBU+"/rest/v1/"+path,
        headers=H_SB, json=data, timeout=15)
    try: return r.json()
    except: return {}

def get_access_token():
    if not YT_REFRESH:
        log("❌ Sem YOUTUBE_REFRESH_TOKEN"); return None
    r = requests.post("https://oauth2.googleapis.com/token", data={
        "client_id":YT_CLIENT_ID,"client_secret":YT_SECRET,
        "refresh_token":YT_REFRESH,"grant_type":"refresh_token"
    }, timeout=15)
    if r.ok: return r.json().get("access_token")
    log(f"❌ Token error: {r.status_code} {r.text[:100]}"); return None

def build_metadata(pipeline):
    """Monta metadados SEO otimizados para o vídeo"""
    title = pipeline.get("title","Psicologia com Daniela Coelho")
    meta  = pipeline.get("metadata") or {}
    serie = meta.get("serie","")
    ep    = meta.get("episodio","")
    topico = meta.get("topico","")
    viral  = meta.get("viral_pattern","")

    # Tags de alto volume
    base_tags = ["psicologia","saúde mental","autoconhecimento","desenvolvimento pessoal","bem-estar","mente","emoções","terapia"]
    topic_tags = {
        "narcisismo":["narcisismo","narcisista","manipulação emocional","gaslighting","relacionamento tóxico"],
        "apego":["apego ansioso","apego evitativo","estilo de apego","medo de abandono","relacionamento"],
        "ansiedade":["ansiedade","ansiedade generalizada","ataque de pânico","transtorno de ansiedade"],
        "trauma":["trauma","C-PTSD","trauma de infância","cura emocional"],
        "burnout":["burnout","esgotamento","estresse crônico","síndrome de burnout"],
        "autossabotagem":["autossabotagem","autoestima","crenças limitantes"],
        "depressao":["depressão","depressão mascarada","tristeza","humor"],
    }.get(topico or serie, [])
    if serie: base_tags.append(f"série {serie}")

    # Descrição SEO
    desc = f"""🧠 {title}

Daniela Coelho | Psicologia Aplicada ao Cotidiano BR

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📌 O QUE VOCÊ VAI APRENDER NESSE VÍDEO:
{viral or 'Tópicos de psicologia aplicados ao dia a dia'}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
⏱️ TIMESTAMPS
00:00 - Introdução
03:00 - O que a ciência diz
08:00 - Casos reais
14:00 - Como aplicar na sua vida
18:00 - Conclusão e próximos passos

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🔔 Inscreva-se para conteúdo semanal de psicologia real:
https://www.youtube.com/@psidanielacoelho

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
#psicologia #saudemental #autoconhecimento #danielacoelho
"""
    if serie and ep:
        desc += f"\n📺 Parte {ep} da Série: {serie.title()}"

    return {
        "title": title[:100],
        "description": desc[:5000],
        "tags": list(set(base_tags + topic_tags))[:30],
        "categoryId": "26",  # Howto & Style
        "defaultLanguage": "pt",
        "defaultAudioLanguage": "pt-BR"
    }

def upload_video(token, mp4_url, metadata):
    """Faz upload de um vídeo para o YouTube via URL"""
    if not mp4_url.startswith("http"):
        log(f"❌ URL inválida: {mp4_url}"); return None

    log(f"Baixando MP4: {mp4_url[:60]}...")
    r_mp4 = requests.get(mp4_url, stream=True, timeout=60)
    if not r_mp4.ok:
        log(f"❌ Erro download MP4: {r_mp4.status_code}"); return None
    video_data = r_mp4.content
    log(f"MP4 baixado: {len(video_data)//1024//1024}MB")

    # Metadata do vídeo
    body = {
        "snippet": {
            "title": metadata["title"],
            "description": metadata["description"],
            "tags": metadata["tags"],
            "categoryId": metadata["categoryId"],
            "defaultLanguage": metadata.get("defaultLanguage","pt"),
            "defaultAudioLanguage": metadata.get("defaultAudioLanguage","pt-BR")
        },
        "status": {
            "privacyStatus": "public",
            "selfDeclaredMadeForKids": False,
            "madeForKids": False
        }
    }

    # Upload multipart
    log("Iniciando upload YouTube...")
    headers = {
        "Authorization": f"Bearer {token}",
        "X-Upload-Content-Type": "video/mp4",
        "X-Upload-Content-Length": str(len(video_data)),
        "Content-Type": "application/json"
    }
    r_init = requests.post(
        "https://www.googleapis.com/upload/youtube/v3/videos?uploadType=resumable&part=snippet,status",
        headers=headers, json=body, timeout=15
    )
    if not r_init.ok:
        log(f"❌ Init upload falhou: {r_init.status_code} {r_init.text[:200]}")
        return None

    upload_url = r_init.headers.get("Location","")
    log(f"Upload URL obtida: OK")

    # Upload do vídeo
    r_upload = requests.put(
        upload_url,
        headers={"Authorization":f"Bearer {token}","Content-Type":"video/mp4"},
        data=video_data, timeout=300
    )
    if r_upload.ok:
        video_id = r_upload.json().get("id","")
        log(f"✅ Upload OK: https://youtu.be/{video_id}")
        return video_id
    log(f"❌ Upload falhou: {r_upload.status_code} {r_upload.text[:200]}")
    return None

def set_thumbnail(token, video_id, thumbnail_url):
    """Define thumbnail do vídeo"""
    if not thumbnail_url: return
    try:
        r_thumb = requests.get(thumbnail_url, timeout=15)
        if not r_thumb.ok: return
        r = requests.post(
            f"https://www.googleapis.com/upload/youtube/v3/thumbnails/set?videoId={video_id}&uploadType=media",
            headers={"Authorization":f"Bearer {token}","Content-Type":"image/jpeg"},
            data=r_thumb.content, timeout=30
        )
        if r.ok: log(f"✅ Thumbnail definida")
    except Exception as e:
        log(f"Thumbnail erro: {e}")

def main():
    log("=== YouTube Publisher V1 ===")
    token = get_access_token()
    if not token:
        log("⚠️ Sem token válido — publicação manual necessária")
        log("Acesse: https://studio.youtube.com")
        return

    # Buscar vídeos mp4_ready
    videos = sb("GET", "content_pipeline?status=eq.mp4_ready&order=id.asc&limit=3")
    if not isinstance(videos, list) or not videos:
        log("Nenhum mp4_ready encontrado"); return

    log(f"Encontrados {len(videos)} vídeos para publicar")

    for v in videos:
        vid_id = v["id"]
        title  = v.get("title","?")[:50]
        mp4_url = v.get("mp4_url","")

        log(f"\nPublicando: {title}")
        if not mp4_url:
            log(f"❌ Sem mp4_url — pulando")
            continue

        # Montar metadados
        meta = build_metadata(v)

        # Upload
        yt_id = upload_video(token, mp4_url, meta)
        if yt_id:
            # Definir thumbnail
            thumb = v.get("thumbnail_url","")
            if thumb: set_thumbnail(token, yt_id, thumb)

            # Atualizar no Supabase
            yt_url = f"https://youtu.be/{yt_id}"
            sb("PATCH", f"content_pipeline?id=eq.{vid_id}", {
                "status": "published",
                "youtube_url": yt_url,
                "published_at": datetime.now(timezone.utc).isoformat(),
                "metadata": {**(v.get("metadata") or {}), "youtube_id": yt_id}
            })
            log(f"✅ Publicado: {yt_url}")
            time.sleep(5)  # Rate limiting
        else:
            log(f"❌ Falha no upload de: {title}")

if __name__ == "__main__":
    main()
