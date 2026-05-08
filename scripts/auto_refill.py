#!/usr/bin/env python3
"""
Auto-Refill: aciona cerebro-autonomo se houver poucos `script_ready`.
Garante que o cron tts-pipeline.yml sempre tem trabalho.
"""
import os, json, time, urllib.request

SBU = os.environ["SUPABASE_URL"].rstrip("/")
SBK = os.environ["SUPABASE_SERVICE_KEY"]
H = {"apikey": SBK, "Authorization": f"Bearer {SBK}"}

PLATFORMS = ["youtube_long", "youtube_shorts", "instagram_reels", "tiktok_short", "pinterest_pin"]
THRESHOLD_PER_PLATFORM = 2  # se ficar abaixo de 2, aciona cerebro

def http(url, method="GET", body=None, headers=None):
    h = dict(headers or {})
    data = None
    if body: data = json.dumps(body).encode(); h["Content-Type"] = "application/json"
    h["User-Agent"] = "auto-refill/1.0"
    req = urllib.request.Request(url, data=data, method=method, headers=h)
    try:
        with urllib.request.urlopen(req, timeout=120) as r:
            return r.status, r.read().decode()
    except Exception as e:
        return 0, str(e)

def main():
    # Conta script_ready por plataforma
    s, raw = http(f"{SBU}/rest/v1/content_pipeline?status=eq.script_ready&select=target_platform", headers=H)
    rows = json.loads(raw) if s == 200 else []
    by_platform = {p: 0 for p in PLATFORMS}
    for r in rows:
        tp = r.get("target_platform")
        if tp in by_platform: by_platform[tp] += 1

    print(f"[refill] script_ready by platform: {by_platform}")

    # Plataformas que precisam refill
    need_refill = [p for p, c in by_platform.items() if c < THRESHOLD_PER_PLATFORM]
    if not need_refill:
        print(f"[refill] all platforms have >= {THRESHOLD_PER_PLATFORM} script_ready, skip")
        return

    print(f"[refill] need refill: {need_refill}")
    # Aciona cerebro-autonomo (ele decide o que gerar)
    s, body = http(f"{SBU}/functions/v1/cerebro-autonomo", method="POST",
                   body={"reason": "auto-refill", "platforms_needed": need_refill},
                   headers=H)
    print(f"[refill] cerebro-autonomo response: {s} {body[:300]}")

if __name__ == "__main__":
    main()
