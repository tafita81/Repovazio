#!/usr/bin/env python3
"""
seo_optimizer.py — Otimizador SEO automático de vídeos publicados
Analisa CTR, views, watch time → sugere melhorias → aplica automaticamente
"""
import os, json, requests, re
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

def get_token():
    if not YT_REFRESH: return None
    r = requests.post("https://oauth2.googleapis.com/token", data={
        "client_id":YT_CLIENT_ID,"client_secret":YT_SECRET,
        "refresh_token":YT_REFRESH,"grant_type":"refresh_token"
    }, timeout=15)
    return r.json().get("access_token") if r.ok else None

def get_video_analytics(token, video_ids):
    """Busca analytics de CTR e watch time por vídeo"""
    if not token or not video_ids: return {}
    from datetime import timedelta
    start = (datetime.now()-timedelta(days=7)).strftime("%Y-%m-%d")
    end   = datetime.now().strftime("%Y-%m-%d")
    ids_filter = ",".join(video_ids)
    r = requests.get(
        "https://youtubeanalytics.googleapis.com/v2/reports",
        headers={"Authorization":f"Bearer {token}"},
        params={
            "ids": "channel==UCyCkIpsVgME9yCj_oXJFheA",
            "startDate": start, "endDate": end,
            "dimensions": "video",
            "metrics": "views,estimatedMinutesWatched,impressions,impressionClickThroughRate,averageViewPercentage",
            "filters": f"video=={ids_filter}",
            "sort": "impressionClickThroughRate"
        }, timeout=15
    )
    if not r.ok: return {}
    result = {}
    for row in r.json().get("rows",[]):
        vid_id, views, watch_min, impr, ctr, avg_view = row
        result[vid_id] = {
            "views": int(views), "watch_min": float(watch_min),
            "impressions": int(impr), "ctr": float(ctr),
            "avg_view_pct": float(avg_view)
        }
    return result

def update_video_title(token, video_id, new_title, snippet):
    """Atualiza título de um vídeo no YouTube"""
    if not token: return False
    body = {"id": video_id, "snippet": {
        "title": new_title[:100],
        "description": snippet.get("description",""),
        "tags": snippet.get("tags",[]),
        "categoryId": snippet.get("categoryId","26")
    }}
    r = requests.put(
        "https://www.googleapis.com/youtube/v3/videos?part=snippet",
        headers={"Authorization":f"Bearer {token}","Content-Type":"application/json"},
        json=body, timeout=15
    )
    return r.ok

# Padrões virais de título comprovados
TITLE_PATTERNS = [
    ("[N] Sinais de {topico} que Você Ignora Todo Dia", 95),
    ("Por Que Você {verbo} Quando {situacao}", 93),
    ("{topico}: O que Ninguém te Contou", 91),
    ("Como {resultado} — A Psicologia Explica", 89),
    ("O que Acontece no Seu Cérebro Quando {situacao}", 88),
]

def seo_score_titulo(titulo):
    """Calcula score SEO do título"""
    score = 50
    if len(titulo) >= 40: score += 15
    if len(titulo) <= 70: score += 10
    if re.search(r'\d', titulo): score += 10  # tem número
    if re.search(r'(você|seu|sua)', titulo, re.I): score += 10  # personalizado
    if re.search(r'(por que|como|sinais|tipos|nunca|sempre)', titulo, re.I): score += 5  # gatilho
    return min(100, score)

def sugerir_titulo_melhorado(titulo_original):
    """Sugere título com maior potencial viral"""
    t = titulo_original.lower()
    if 'narcis' in t:
        return "Os 7 Tipos de Narcisismo (e o 5° parece o seu melhor amigo)"
    if 'apego' in t and ('abandon' in t or 'medo' in t):
        return "Apego Ansioso: Por Que Você Tem Medo de Ser Abandonado"
    if 'burnout' in t:
        return "Burnout Silencioso: 8 Sinais que Você Está no Limite"
    if 'ansiedade' in t:
        return "Ansiedade: O que É de Verdade (não é o que te disseram)"
    if 'gaslighting' in t:
        return "Gaslighting: 7 Sinais que Estão Acontecendo com Você Agora"
    if 'autossabotagem' in t:
        return "Por Que Você se Autossabota Antes de Ter Sucesso"
    if 'dinheiro' in t:
        return "Psicologia do Dinheiro: Por Que Você Sabota Sua Riqueza"
    if 'trauma' in t:
        return "Trauma de Infância no Adulto: 8 Comportamentos Reveladores"
    return titulo_original

def main():
    log("=== SEO Optimizer V1 ===")
    token = get_token()

    # Buscar vídeos publicados com suas analytics
    published = sb("GET","video_analytics?order=ctr.asc&limit=10")
    if not isinstance(published, list) or not published:
        log("Sem analytics ainda — aguardando dados do monitor")
        return

    log(f"Analisando {len(published)} vídeos...")
    for v in published:
        vid_id = v.get("video_id","")
        titulo = v.get("title","")
        ctr    = v.get("ctr",0)
        views  = v.get("views",0)
        seo    = v.get("seo_score",0)

        # Vídeos com CTR baixo precisam de otimização
        if ctr < 5 and views > 100:
            novo_titulo = sugerir_titulo_melhorado(titulo)
            novo_score  = seo_score_titulo(novo_titulo)

            if novo_titulo != titulo and novo_score > (seo or 0):
                log(f"🔧 CTR baixo ({ctr:.1f}%): {titulo[:40]}")
                log(f"   → {novo_titulo[:60]}")

                # Salvar sugestão
                sb("POST","seo_optimizations",{
                    "video_id": vid_id,
                    "tipo": "title_ctr",
                    "versao_atual": titulo,
                    "versao_otimizada": novo_titulo,
                    "score_antes": seo or 60,
                    "score_depois": novo_score
                })

                # Aplicar automaticamente se CTR < 3%
                if ctr < 3 and token:
                    log(f"   Aplicando automaticamente (CTR crítico < 3%)")
                    # Buscar snippet atual
                    r = requests.get(
                        "https://www.googleapis.com/youtube/v3/videos",
                        headers={"Authorization":f"Bearer {token}"},
                        params={"part":"snippet","id":vid_id}, timeout=15
                    )
                    if r.ok:
                        items = r.json().get("items",[])
                        if items:
                            snippet = items[0]["snippet"]
                            if update_video_title(token, vid_id, novo_titulo, snippet):
                                log(f"   ✅ Título atualizado!")
                                sb("PATCH",f"video_analytics?video_id=eq.{vid_id}",
                                    {"action_taken":f"title_updated_to:{novo_titulo[:50]}",
                                     "seo_score":novo_score})

    log("=== SEO Optimizer concluído ===")

if __name__ == "__main__":
    main()
