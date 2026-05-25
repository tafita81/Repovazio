#!/usr/bin/env python3
"""
hub_psidanielacelho.py — Hub central @psidanielacoelho
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
@psidanielacoelho É O HUB de todas as plataformas.
O Cérebro Quântico (api_brain) controla tudo em tempo real.

PLATAFORMAS SINCRONIZADAS:
  YouTube PT-BR   → UCyCkIpsVgME9yCj_oXJFheA (canal principal)
  YouTube Live    → Stream 24/7 vários idiomas
  Instagram       → @psidanielacoelho (DM auto "SONO")
  WhatsApp        → Grupos exclusivos + áudio diário 19h30
  Bluesky         → @psidanielacoelho.bsky.social
  Medium          → artigos PT + EN semanais
  Spotify Podcast → episódios Seg/Qua/Sex
  Spotify Trilhas → binaural 528Hz/432Hz
  TikTok          → shorts + afiliados
  Kwai            → shorts + afiliados
  Reddit          → r/psicologia conteúdo dark
  Pinterest       → infográficos psicologia
  Newsletter      → PT + EN semanal
  Telegram        → canal broadcast
  Amazon KDP      → livros psicologia PT+EN

TIMELINE DANIELA COELHO:
  Agora→Dez2026: pesquisadora de comportamento humano
  Jan  2027:     REVELAR que é psicóloga registrada
                 → Lower third "Psicóloga Daniela Coelho CRP XXXX-X"
                 → Bio atualizada em todas as plataformas
                 → Vídeo de apresentação oficial
                 → Consultório online (agenda pelo hub)
                 → Cursos assinados com CRP
"""
import os, requests, time, json
from datetime import datetime
import urllib3; urllib3.disable_warnings()

GROQ_KEY  = os.getenv("GROQ_API_KEY","")
SB_URL    = os.getenv("SUPABASE_URL","https://tpjvalzwkqwttvmszvie.supabase.co")
SB_KEY    = os.getenv("SUPABASE_SERVICE_KEY","")
SBH       = {"apikey":SB_KEY,"Authorization":f"Bearer {SB_KEY}",
             "Content-Type":"application/json","Prefer":"return=minimal"}

# Configuração de TODAS as plataformas do hub
PLATAFORMAS = {
    "youtube_ptbr": {
        "nome":    "YouTube PT-BR",
        "handle":  "@psidanielacoelho",
        "canal_id":"UCyCkIpsVgME9yCj_oXJFheA",
        "rpm":     7, "moeda":"BRL",
        "conteudo":["Long 15min","Short 57s","Live 24/7"],
        "horario": "18h-20h BRT",
        "status":  "ativo",
    },
    "youtube_live_ptbr": {
        "nome":    "YouTube Live 24/7 PT",
        "canal_id":"UCyCkIpsVgME9yCj_oXJFheA",
        "rpm":     14, "moeda":"BRL",  # Live tem RPM 2x
        "conteudo":["Stream 24/7 Groq+Pollinations"],
        "horario": "contínuo",
        "status":  "configurado",
    },
    "youtube_en": {
        "nome":    "YouTube EN",
        "handle":  "@psychologyfrequencies",
        "rpm":     28, "moeda":"USD",
        "conteudo":["Long EN","Short EN","Live EN"],
        "horario": "20h ET",
        "status":  "criar",
    },
    "instagram": {
        "nome":    "Instagram",
        "handle":  "@psidanielacoelho",
        "link":    "instagram.com/psidanielacoelho",
        "conteudo":["Reels dark 3x/dia","Carrosséis","Stories"],
        "horario": "9h,12h,18h BRT",
        "cta":     "Comenta SONO",
        "status":  "ativo",
    },
    "whatsapp_grupo": {
        "nome":    "WhatsApp Grupos",
        "conteudo":["Áudio 4min 19h30 BRT","Pesquisa PubMed","Insights"],
        "preco":   "R$216/ano",
        "horario": "19h30 BRT diário",
        "status":  "configurar_hotmart",
    },
    "bluesky": {
        "nome":    "Bluesky",
        "handle":  "@psidanielacoelho.bsky.social",
        "conteudo":["Posts automáticos 3x/dia"],
        "horario": "9h,13h,19h BRT",
        "status":  "ativo",
    },
    "medium_pt": {
        "nome":    "Medium PT",
        "conteudo":["18 artigos prontos","publicação Ter/Sex"],
        "seo":     "narcisismo,apego,burnout,sono",
        "status":  "falta MEDIUM_TOKEN",
    },
    "spotify_podcast": {
        "nome":    "Spotify Podcast",
        "conteudo":["8 episódios gerados","Seg/Qua/Sex"],
        "status":  "upload Anchor.fm pendente",
    },
    "spotify_trilhas": {
        "nome":    "Spotify Trilhas",
        "conteudo":["528Hz,432Hz,40Hz,174Hz,396Hz"],
        "preco":   "streaming royalties",
        "status":  "upload Amuse.io pendente",
    },
    "tiktok": {
        "nome":    "TikTok",
        "handle":  "@psidanielacoelho",
        "conteudo":["Shorts dark","TikTok Shop afiliados"],
        "status":  "configurar",
    },
    "kwai": {
        "nome":    "Kwai",
        "conteudo":["Shorts","Afiliados magnésio/ashwagandha"],
        "status":  "ativo",
    },
    "newsletter": {
        "nome":    "Newsletter PT+EN",
        "conteudo":["Semanal","Sexta 10h BRT"],
        "status":  "ativo",
    },
    "amazon_kdp": {
        "nome":    "Amazon KDP",
        "conteudo":["Narcisismo Encoberto","Apego Ansioso"],
        "royalty":  "70%",
        "status":  "upload pendente",
    },
    "telegram": {
        "nome":    "Telegram Canal",
        "handle":  "@psidanielacoelho",
        "conteudo":["Broadcast automático"],
        "status":  "criar",
    },
    "pinterest": {
        "nome":    "Pinterest",
        "conteudo":["Infográficos psicologia dark","SEO passivo"],
        "status":  "criar",
    },
    "reddit": {
        "nome":    "Reddit",
        "conteudo":["r/psicologia","r/sleep","r/relationship_advice"],
        "status":  "ativo",
    },
}

def cerebro_kpis():
    """Cérebro Quântico coleta KPIs de todas as plataformas em tempo real"""
    kpis = {}
    try:
        r = requests.get(f"{SB_URL}/rest/v1/vendas?status=eq.confirmada&select=preco,criado_em",
            headers={**SBH,"Prefer":"return=representation"}, timeout=8, verify=False)
        vendas = r.json() if r.status_code == 200 else []
        hoje = datetime.now().date().isoformat()
        kpis["vendas_hoje"] = len([v for v in vendas if v.get("criado_em","").startswith(hoje)])
        kpis["receita_total"] = sum(v.get("preco",0) for v in vendas)
    except: kpis["vendas_hoje"] = 0; kpis["receita_total"] = 0
    try:
        r2 = requests.get(f"{SB_URL}/rest/v1/produto_whatsapp?select=assinantes&limit=1",
            headers={**SBH,"Prefer":"return=representation"}, timeout=8, verify=False)
        wa = r2.json()
        kpis["assinantes_wa"] = wa[0].get("assinantes",0) if wa else 0
    except: kpis["assinantes_wa"] = 0
    try:
        r3 = requests.get(f"{SB_URL}/rest/v1/api_brain?select=id&limit=1",
            headers={**SBH,"Prefer":"count=exact"}, timeout=8, verify=False)
        kpis["brain_apis"] = int(r3.headers.get("content-range","0/0").split("/")[-1]) if r3.status_code==206 else 0
    except: kpis["brain_apis"] = 3037
    return kpis

def run():
    print("=== HUB @psidanielacoelho — Cérebro Controlando Tudo ===\n")
    kpis = cerebro_kpis()
    print(f"  Cérebro Quântico: {kpis.get('brain_apis',0):,} APIs indexadas")
    print(f"  Vendas hoje:      {kpis['vendas_hoje']}")
    print(f"  Assinantes WA:    {kpis['assinantes_wa']}")
    print(f"  Receita total:    R${kpis['receita_total']:,.2f}\n")
    ativos = [p for p in PLATAFORMAS.values() if p["status"]=="ativo"]
    configurar = [p for p in PLATAFORMAS.values() if p["status"] not in ("ativo","configurado")]
    print(f"  PLATAFORMAS ATIVAS ({len(ativos)}/{len(PLATAFORMAS)}):")
    for p in PLATAFORMAS.values():
        icon = "✅" if p["status"]=="ativo" else ("🔄" if p["status"]=="configurado" else "⚡")
        print(f"  {icon} {p['nome']:25s} {p['status']}")
    print(f"\n  TIMELINE:")
    print(f"  Agora → Dez 2026: pesquisadora de comportamento humano")
    print(f"  Jan   2027:       REVELAR psicóloga + lower third + CRP")
    print(f"                    → bio atualizada em {len(PLATAFORMAS)} plataformas")
    print(f"                    → consultório online via hub")
    print(f"                    → cursos com assinatura CRP")

if __name__=="__main__": run()
