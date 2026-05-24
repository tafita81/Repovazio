#!/usr/bin/env python3
"""
estrategia_5dias.py — Ramp-up de 5 dias para ganhar tração (do transcript)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
BASEADO EM TRANSCRIPT: "Pelos próximos 5 dias, 3 posts/dia: 9h, 12h, 18h"

MATH DO TRANSCRIPT (adaptado):
  5 vendas/dia × R$29,90 = R$149,50/dia = R$4.485/mês  (conservador)
  10 vendas/dia × R$29,90 = R$299/dia = R$8.970/mês     (crescendo)
  20 vendas/dia × R$29,90 = R$598/dia = R$17.940/mês    (viral)
  + WhatsApp R$216/ano por assinante (receita recorrente)
"""
import os, requests, time, json
import urllib3; urllib3.disable_warnings()

SB_URL = os.getenv("SUPABASE_URL","https://tpjvalzwkqwttvmszvie.supabase.co")
SB_KEY = os.getenv("SUPABASE_SERVICE_KEY","")
GROQ   = os.getenv("GROQ_API_KEY","")
SBH    = {"apikey":SB_KEY,"Authorization":f"Bearer {SB_KEY}",
          "Content-Type":"application/json","Prefer":"return=minimal"}

PLANO_5_DIAS = [
    {
        "dia": 1,
        "foco": "viralizar",
        "posts": [
            {"horario":"09:00","tipo":"viralizar","tema":"narcisismo",    "cta":"Salva e manda pra quem precisa"},
            {"horario":"12:00","tipo":"vender",   "tema":"sono",          "cta":"Comenta SONO que eu te mando algo especial"},
            {"horario":"18:00","tipo":"viralizar","tema":"burnout",       "cta":"Salva se você se identificou"},
        ],
        "meta_seguidores": 50,
        "meta_vendas": 3,
    },
    {
        "dia": 2,
        "foco": "engajamento",
        "posts": [
            {"horario":"09:00","tipo":"viralizar","tema":"apego",         "cta":"Comenta seu estilo de apego"},
            {"horario":"12:00","tipo":"vender",   "tema":"app",           "cta":"Comenta SONO para receber o link"},
            {"horario":"18:00","tipo":"coringa",  "tema":"mindset",       "cta":"Salva esse post"},
        ],
        "meta_seguidores": 100,
        "meta_vendas": 5,
    },
    {
        "dia": 3,
        "foco": "venda",
        "posts": [
            {"horario":"09:00","tipo":"vender",   "tema":"narcisismo",    "cta":"Comenta SONO que eu te ajudo"},
            {"horario":"12:00","tipo":"viralizar","tema":"sono",          "cta":"Salva e manda para alguém"},
            {"horario":"18:00","tipo":"vender",   "tema":"burnout",       "cta":"Comenta SONO 👇"},
        ],
        "meta_seguidores": 200,
        "meta_vendas": 8,
    },
    {
        "dia": 4,
        "foco": "viral_maximo",
        "posts": [
            {"horario":"09:00","tipo":"viralizar","tema":"discipline",    "cta":"Salva para quando precisar"},
            {"horario":"12:00","tipo":"vender",   "tema":"apego",         "cta":"Comenta SONO"},
            {"horario":"18:00","tipo":"viralizar","tema":"narcisismo",    "cta":"Manda para quem precisa ver"},
        ],
        "meta_seguidores": 350,
        "meta_vendas": 12,
    },
    {
        "dia": 5,
        "foco": "conversao",
        "posts": [
            {"horario":"09:00","tipo":"vender",   "tema":"sono",          "cta":"Comenta SONO — link na bio"},
            {"horario":"12:00","tipo":"coringa",  "tema":"burnout",       "cta":"Salva e compartilha"},
            {"horario":"18:00","tipo":"vender",   "tema":"app",           "cta":"Comenta SONO agora 👇"},
        ],
        "meta_seguidores": 500,
        "meta_vendas": 20,
    },
]

def groq_gerar_post(post_info, dia):
    if not GROQ: return f"Post dia {dia} {post_info['horario']}"
    prompt = (
        f"Gere legenda Instagram PT-BR para post dark de psicologia.\n"
        f"Dia {dia} | Horário: {post_info['horario']} | Tipo: {post_info['tipo']}\n"
        f"Tema: {post_info['tema']}\n"
        f"CTA: {post_info['cta']}\n"
        f"Max 50 palavras. Impactante. Tom {post_info['tipo']}.\n"
        f"Retorne APENAS a legenda com CTA no final."
    )
    try:
        r = requests.post("https://api.groq.com/openai/v1/chat/completions",
            headers={"Authorization":f"Bearer {GROQ}","Content-Type":"application/json"},
            json={"model":"llama-3.3-70b-versatile",
                  "messages":[{"role":"user","content":prompt}],
                  "max_tokens":80,"temperature":0.85},
            timeout=12, verify=False)
        if r.status_code == 200:
            return r.json()["choices"][0]["message"]["content"].strip()
    except: pass
    return post_info["cta"]

def salvar_plano(dia_info, posts_gerados):
    if not SB_KEY: return
    for p, leg in zip(dia_info["posts"], posts_gerados):
        requests.post(f"{SB_URL}/rest/v1/social_posts",
            headers={**SBH,"Prefer":"return=minimal"},
            json={"plataforma":"instagram","tema":p["tema"],
                  "hook":f"Dia {dia_info['dia']} {p['horario']}",
                  "legenda":leg[:400],"cta":p["cta"],
                  "status":"ready"},
            timeout=8, verify=False)

def run():
    print("=== ESTRATÉGIA 5 DIAS — Ramp-up (do transcript) ===\n")
    print(f"  3 posts/dia: 9h (viralizar) | 12h (vender) | 18h (coringa)\n")
    for dia in PLANO_5_DIAS:
        print(f"  📅 DIA {dia['dia']} — foco: {dia['foco'].upper()}")
        print(f"     Meta: {dia['meta_seguidores']} seguidores | {dia['meta_vendas']} vendas")
        posts_gerados = []
        for p in dia["posts"]:
            leg = groq_gerar_post(p, dia["dia"])
            posts_gerados.append(leg)
            print(f"     {p['horario']} [{p['tipo']}] {p['tema']}: ✅")
        salvar_plano(dia, posts_gerados)
        time.sleep(1)

    print(f"\n  MATH DO TRANSCRIPT:")
    print(f"   5 vendas/dia R$29,90 = R$4.485/mês (conservador)")
    print(f"  20 vendas/dia R$29,90 = R$17.940/mês (viral)")
    print(f"  + WhatsApp recorrente = receita composta")

if __name__=="__main__": run()
