#!/usr/bin/env python3
"""
thumbnail_ab_rotator.py — A/B test automático via YouTube Data API
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

ROTAÇÃO INTELIGENTE:
  - Pega o vídeo/live mais recente do canal
  - Aplica thumbnail seguinte na sequência (A → B → C → A...)
  - Loga métricas em Supabase para análise CTR posterior
  - Roda a cada 24h via GitHub Actions

PUBLIC ALGORITHM SIGNALS YOUTUBE (May 2026, documentado):
  1. CTR thumbnail — 4-12% é bom, >12% viral
  2. Average View Duration (AVD) — meta >50% para boost
  3. Session Watch Time — viewer não fechou app após seu vídeo
  4. Velocidade primeiras 24h — views/hora vs baseline canal
  5. Engagement (like+comment+share) / view
  6. Subscriber rate (subs ganhos/views)
"""
import os, requests, json, time
from datetime import datetime

YT_REFRESH = os.getenv("YT_REFRESH_TOKEN")
YT_CLIENT_ID = os.getenv("YT_CLIENT_ID")
YT_CLIENT_SECRET = os.getenv("YT_CLIENT_SECRET")
CHANNEL_ID = os.getenv("YT_CHANNEL_ID", "UCSH63tBfY6wEIdkC4u4zKdg")
SUPABASE_URL = "https://tpjvalzwkqwttvmszvie.supabase.co"
SUPABASE_KEY = os.getenv("SUPABASE_SERVICE_KEY")
REPO_CDN = "https://raw.githubusercontent.com/tafita81/Repovazio/main/assets/thumbs"

def get_access_token():
    r = requests.post("https://oauth2.googleapis.com/token", data={
        "client_id": YT_CLIENT_ID, "client_secret": YT_CLIENT_SECRET,
        "refresh_token": YT_REFRESH, "grant_type": "refresh_token"
    })
    return r.json().get("access_token")

def detect_lang_from_title(title):
    """Heurística simples: detecta idioma do título para escolher thumb"""
    title_lower = title.lower()
    if any(x in title for x in ["睡眠","眠り","技法","サイン","量子認知","ダニエラ"]): return "JA"
    if any(x in title for x in ["수면","기법","신호","양자","다니엘라"]): return "KO"
    if any(x in title for x in ["نوم","علم","تقنيات","علامات","الإدراك"]): return "AR"
    if any(x in title_lower for x in ["sommeil","techniques","signes","cognition quantique","hypnose"]): return "FR"
    if any(x in title_lower for x in ["schlaf","techniken","zeichen","quantenkognition","hypnose"]): return "DE"
    if any(x in title_lower for x in ["sonno","tecniche","segnali","cognizione quantica","ipnosi"]): return "IT"
    if any(x in title_lower for x in ["sueño","técnicas","señales","cognición cuántica","hipnosis"]): return "ES"
    if any(x in title_lower for x in ["dormir","técnicas","sinais","cognição quântica","hipnose","psicologia"]): return "PT"
    if any(x in title_lower for x in ["sleep","tricks","signs","quantum cognition","hypnosis","dark psy"]): return "EN"
    return "PT"

def get_next_variant(supabase, video_id):
    """Busca qual variante (0/1/2) usar agora para o video — rotação A/B/C"""
    headers = {"apikey": SUPABASE_KEY, "Authorization": f"Bearer {SUPABASE_KEY}"}
    r = requests.get(f"{supabase}/rest/v1/thumb_rotation?video_id=eq.{video_id}&select=last_variant",
                     headers=headers)
    if r.status_code == 200 and r.json():
        last = r.json()[0]["last_variant"]
        return (last + 1) % 3
    return 0

def save_rotation(supabase, video_id, lang, variant, palette):
    headers = {"apikey": SUPABASE_KEY, "Authorization": f"Bearer {SUPABASE_KEY}",
               "Content-Type":"application/json", "Prefer":"resolution=merge-duplicates"}
    requests.post(f"{supabase}/rest/v1/thumb_rotation", headers=headers, json={
        "video_id": video_id, "lang": lang, "last_variant": variant,
        "palette": palette, "applied_at": datetime.utcnow().isoformat()
    })

def upload_thumbnail(token, video_id, image_url):
    """Sets thumbnail via YouTube Data API v3"""
    img = requests.get(image_url).content
    r = requests.post(
        f"https://www.googleapis.com/upload/youtube/v3/thumbnails/set?videoId={video_id}",
        headers={"Authorization": f"Bearer {token}", "Content-Type": "image/jpeg"},
        data=img
    )
    return r.status_code == 200

def rotate():
    token = get_access_token()
    if not token: print("❌ OAuth falhou"); return

    # Lista últimos 10 vídeos+lives do canal
    r = requests.get("https://www.googleapis.com/youtube/v3/search", params={
        "part":"snippet","channelId":CHANNEL_ID,"order":"date","maxResults":10,
        "type":"video","key": YT_CLIENT_ID
    }, headers={"Authorization": f"Bearer {token}"})

    items = r.json().get("items", [])
    print(f"📺 {len(items)} vídeos/lives encontrados\n")

    palettes = ["gold-black","crimson-black","purple-gold"]
    applied = 0

    for item in items:
        vid_id = item["id"]["videoId"]
        title  = item["snippet"]["title"]
        lang   = detect_lang_from_title(title)
        variant = get_next_variant(SUPABASE_URL, vid_id)
        palette = palettes[variant]

        thumb_url = f"{REPO_CDN}/thumb_{lang.lower()}_{palette}_{variant}.jpg"
        ok = upload_thumbnail(token, vid_id, thumb_url)
        if ok:
            save_rotation(SUPABASE_URL, vid_id, lang, variant, palette)
            applied += 1
            print(f"  ✅ {title[:50]:50} | {lang} v{variant} ({palette})")
        else:
            print(f"  ⚠️  {title[:50]:50} | falhou")
        time.sleep(2)

    print(f"\n✨ {applied} thumbnails atualizadas (próxima rotação em 24h)")

if __name__ == "__main__":
    rotate()
