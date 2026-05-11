#!/usr/bin/env python3
"""
youtube_monitor.py — Monitoramento 24/7 do canal + Growth Engine
Canal: UCyCkIpsVgME9yCj_oXJFheA (@psidanielacoelho)
"""
import os, json, requests, sys, time, re
from datetime import datetime, timezone

# ── Credenciais ──────────────────────────────────────────────
SBU          = os.getenv("SBU","https://tpjvalzwkqwttvmszvie.supabase.co")
SBK          = os.getenv("SBK","")
YT_CLIENT_ID = os.getenv("YT_CLIENT_ID","")
YT_SECRET    = os.getenv("YT_CLIENT_SECRET","")
YT_REFRESH   = os.getenv("YT_REFRESH_TOKEN","")
CHANNEL_ID   = os.getenv("YT_CHANNEL_ID","UCyCkIpsVgME9yCj_oXJFheA")
ACTION       = os.getenv("ACTION","full")

H_SB = {"apikey":SBK,"Authorization":f"Bearer {SBK}","Content-Type":"application/json"}

def sb(method, path, data=None):
    r = requests.request(method, SBU+"/rest/v1/"+path,
        headers=H_SB, json=data, timeout=15)
    try: return r.json()
    except: return {}

def log(msg, tipo="info"):
    print(f"[{datetime.now().strftime('%H:%M:%S')}] {msg}")
    sb("POST","cerebro_logs",{"type":tipo,"message":msg[:200],
        "details":{"ts":datetime.now(timezone.utc).isoformat()}})

# ── OAuth: obter access_token ────────────────────────────────
def get_access_token():
    if not YT_REFRESH:
        log("SEM YOUTUBE_REFRESH_TOKEN — monitoramento limitado","warn")
        return None
    r = requests.post("https://oauth2.googleapis.com/token", data={
        "client_id":YT_CLIENT_ID,"client_secret":YT_SECRET,
        "refresh_token":YT_REFRESH,"grant_type":"refresh_token"
    }, timeout=15)
    if r.ok:
        token = r.json().get("access_token")
        log(f"Access token OK: {token[:20]}...")
        return token
    log(f"Erro token: {r.status_code} {r.text[:200]}","error")
    return None

# ── Buscar stats do canal ────────────────────────────────────
def fetch_channel_stats(token):
    if not token: return None
    r = requests.get(
        "https://www.googleapis.com/youtube/v3/channels",
        headers={"Authorization":f"Bearer {token}"},
        params={"part":"statistics,snippet","id":CHANNEL_ID},
        timeout=15
    )
    if not r.ok:
        log(f"Erro channel stats: {r.status_code}","error"); return None
    items = r.json().get("items",[])
    if not items: return None
    stats = items[0]["statistics"]
    subs  = int(stats.get("subscriberCount",0))
    views = int(stats.get("viewCount",0))
    vids  = int(stats.get("videoCount",0))
    log(f"Canal: {subs} subs | {views:,} views | {vids} vídeos")
    return {"subscribers":subs,"total_views":views,"total_videos":vids}

# ── Buscar vídeos do canal ────────────────────────────────────
def fetch_channel_videos(token, max_results=20):
    if not token: return []
    r = requests.get(
        "https://www.googleapis.com/youtube/v3/search",
        headers={"Authorization":f"Bearer {token}"},
        params={"part":"snippet","channelId":CHANNEL_ID,
                "type":"video","maxResults":max_results,
                "order":"date"},
        timeout=15
    )
    if not r.ok: return []
    return r.json().get("items",[])

# ── Stats por vídeo ──────────────────────────────────────────
def fetch_video_stats(token, video_ids):
    if not token or not video_ids: return {}
    ids_str = ",".join(video_ids)
    r = requests.get(
        "https://www.googleapis.com/youtube/v3/videos",
        headers={"Authorization":f"Bearer {token}"},
        params={"part":"statistics,contentDetails","id":ids_str},
        timeout=15
    )
    if not r.ok: return {}
    result = {}
    for item in r.json().get("items",[]):
        vid_id = item["id"]
        st = item.get("statistics",{})
        result[vid_id] = {
            "views":   int(st.get("viewCount",0)),
            "likes":   int(st.get("likeCount",0)),
            "comments":int(st.get("commentCount",0)),
        }
    return result

# ── Analytics Report (watch time, impressions, CTR) ──────────
def fetch_analytics(token):
    if not token: return None
    today = datetime.now().strftime("%Y-%m-%d")
    from datetime import timedelta
    start = (datetime.now()-timedelta(days=28)).strftime("%Y-%m-%d")
    r = requests.get(
        "https://youtubeanalytics.googleapis.com/v2/reports",
        headers={"Authorization":f"Bearer {token}"},
        params={
            "ids": f"channel=={CHANNEL_ID}",
            "startDate": start, "endDate": today,
            "metrics": "views,estimatedMinutesWatched,impressions,impressionClickThroughRate,averageViewPercentage",
            "dimensions": "day",
            "sort": "-day",
        },
        timeout=15
    )
    if not r.ok:
        log(f"Analytics erro: {r.status_code} — {r.text[:100]}","warn")
        return None
    data = r.json()
    rows = data.get("rows",[])
    if not rows: return None
    # Agregar 28 dias
    total_views = sum(int(row[1]) for row in rows)
    total_min   = sum(float(row[2]) for row in rows)
    total_impr  = sum(int(row[3]) for row in rows)
    avg_ctr     = sum(float(row[4]) for row in rows)/max(len(rows),1)
    avg_view_pct= sum(float(row[5]) for row in rows)/max(len(rows),1)
    log(f"Analytics 28d: {total_views:,} views | CTR {avg_ctr:.1f}% | Avg view {avg_view_pct:.0f}%")
    return {
        "views_28d": total_views,
        "watch_time_hrs": round(total_min/60, 1),
        "impressions_28d": total_impr,
        "ctr_28d": round(avg_ctr, 2),
        "avg_view_pct": round(avg_view_pct, 1),
    }

# ── Salvar snapshot ──────────────────────────────────────────
def save_snapshot(channel, analytics):
    if not channel: return
    # Buscar snapshot anterior para calcular delta
    prev = sb("GET","channel_snapshots?order=snapshot_at.desc&limit=1")
    prev_subs  = prev[0]["subscribers"]  if prev else 0
    prev_views = prev[0]["total_views"]  if prev else 0
    delta_subs  = channel["subscribers"] - prev_subs
    delta_views = channel["total_views"] - prev_views

    # Projeção dias para 1K
    days_to_1k = None
    if delta_subs > 0:
        subs_left  = max(0, 1000 - channel["subscribers"])
        days_to_1k = round(subs_left / (delta_subs/1), 1)  # delta/dia

    payload = {**channel, **(analytics or {}),
        "delta_subs": delta_subs, "delta_views": delta_views,
        "days_to_1k_est": days_to_1k,
        "snapshot_at": datetime.now(timezone.utc).isoformat()
    }
    sb("POST","channel_snapshots", payload)
    log(f"Snapshot salvo: Δsubs={delta_subs:+d} | dias→1K={days_to_1k}")

# ── Salvar analytics por vídeo ────────────────────────────────
def save_video_analytics(token, videos, stats):
    if not videos: return
    for v in videos[:10]:
        vid_id = v["id"]["videoId"]
        title  = v["snippet"]["title"]
        vst    = stats.get(vid_id,{})
        views  = vst.get("views",0)
        revenue_est = round(views * 0.012 * 12 / 1000, 2)  # CPM R$12

        # SEO score
        seo_score = 70
        if len(title) > 40: seo_score += 10
        if re.search(r'\d', title): seo_score += 5
        if re.search(r'(por que|como|sinais|tipos|você|seu|sua)', title, re.I): seo_score += 10
        if re.search(r'narcis|apego|burnout|ansiedade|trauma', title, re.I): seo_score += 5

        payload = {
            "video_id": vid_id, "title": title,
            "views": views, "likes": vst.get("likes",0),
            "comments": vst.get("comments",0),
            "revenue_est_r": revenue_est,
            "seo_score": min(100, seo_score),
            "needs_title_opt": seo_score < 85,
            "is_viral_cand": views > 5000,
            "checked_at": datetime.now(timezone.utc).isoformat()
        }
        sb("POST","video_analytics", payload)
        log(f"  [{vid_id}] {title[:40]} — {views} views | SEO {seo_score}")

# ── Otimização automática de SEO ─────────────────────────────
def run_seo_optimizer():
    log("=== SEO OPTIMIZER ===")
    # Buscar vídeos com seo_score baixo
    low_seo = sb("GET","video_analytics?needs_title_opt=eq.true&limit=5")
    for v in (low_seo if isinstance(low_seo,list) else []):
        title = v.get("title","")
        # Sugerir otimização
        new_title = title
        if "narcis" in title.lower() and len(title)<50:
            new_title = "Os 7 Tipos de Narcisismo (e o 5° você não imagina)"
        elif "apego" in title.lower():
            new_title = "Apego Ansioso: Por Que Você Tem Medo de Ser Abandonado"
        elif "burnout" in title.lower():
            new_title = "Burnout Silencioso: 8 Sinais que Você Está no Limite"
        if new_title != title:
            sb("POST","seo_optimizations",{
                "video_id": v["video_id"],
                "tipo": "title",
                "versao_atual": title,
                "versao_otimizada": new_title,
                "score_antes": v.get("seo_score",60),
                "score_depois": 91
            })
            log(f"SEO sugerido: {title[:30]} → {new_title[:30]}")

# ── Relatório de Crescimento ─────────────────────────────────
def growth_report(channel, analytics):
    subs = channel.get("subscribers",0) if channel else 0
    fase = "FASE 1 (0→100)" if subs < 100 else "FASE 2 (100→500)" if subs < 500 else "FASE 3 (500→1K)"
    pct  = round(subs/1000*100, 1)
    log(f"=== GROWTH REPORT ===")
    log(f"Subs: {subs}/1000 ({pct}%) — {fase}")
    if analytics:
        log(f"CTR 28d: {analytics.get('ctr_28d',0)}% | Watch time: {analytics.get('watch_time_hrs',0)}h")
    prox_meta = 100 if subs < 100 else 500 if subs < 500 else 1000
    faltam = prox_meta - subs
    log(f"Faltam {faltam} subs para próxima meta ({prox_meta})")

# ── MAIN ─────────────────────────────────────────────────────
def main():
    log(f"=== YouTube Monitor V1 | ACTION={ACTION} ===")
    token = get_access_token()

    if ACTION in ("monitor","full","status"):
        channel   = fetch_channel_stats(token)
        analytics = fetch_analytics(token)
        save_snapshot(channel, analytics)
        if token:
            videos = fetch_channel_videos(token, max_results=15)
            vid_ids = [v["id"]["videoId"] for v in videos if "videoId" in v.get("id",{})]
            stats   = fetch_video_stats(token, vid_ids)
            save_video_analytics(token, videos, stats)
            growth_report(channel, analytics)

    if ACTION in ("optimize","full"):
        run_seo_optimizer()

    log("=== Monitor finalizado ===")

if __name__ == "__main__":
    main()
