#!/usr/bin/env python3
"""
instagram_reels_producer.py — Reels sem aparecer (estratégia do transcript)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
BASEADO EM: "Publique 3 Reels/dia sem aparecer. CTA: 'Comenta SONO'"

ESTRATÉGIA DO TRANSCRIPT:
  - Perfil Instagram: pais/adultos com ansiedade e insônia
  - 3 reels/dia sem aparecer (IA gera, voz IA, edita CapCut)
  - CTA: "Comenta SONO que eu te envio o link"
  - DM manual no início → depois automatizar com ManyChat/ChatBot

NOSSO PIPELINE:
  scripts/narrativa_engine.py → gera 5 títulos virais
  scripts/render_v3_mega.py   → renderiza vídeo 9:16
  Instagram API              → publica (quando autorizado)
  ManyChat                   → responde automático "SONO" → link Hotmart

NICHOS PARA REELS (30 tipos validados):
  - Rotina do sono: dificuldade de desacelerar à noite
  - Sinais de ansiedade que você ignora
  - Narcisismo no relacionamento (detectar)
  - Burnout antes de explodir
  - Por que você acorda às 3h da manhã
  - Apego ansioso: reconhecer o padrão
  - Erros comuns antes de dormir (cortisol)
  - Técnicas de respiração para ansiedade noturna
"""
import os, requests, time
import urllib3; urllib3.disable_warnings()

SB_URL = os.getenv("SUPABASE_URL","https://tpjvalzwkqwttvmszvie.supabase.co")
SB_KEY = os.getenv("SUPABASE_SERVICE_KEY","")
GROQ   = os.getenv("GROQ_API_KEY","")
SBH    = {"apikey":SB_KEY,"Authorization":f"Bearer {SB_KEY}",
          "Content-Type":"application/json","Prefer":"return=minimal"}

CTA_PADRAO = "Comenta SONO que eu te mando o link 👇"
LINK_VENDAS = "repovazio.vercel.app/psicologia-para-dormir"

TEMAS_REELS = [
    {"tema":"sono",    "hook":"Por que você acorda às 3h da manhã toda noite",          "tipo":"revelacao"},
    {"tema":"ansiedade","hook":"5 sinais que sua ansiedade está destruindo seu sono",    "tipo":"lista"},
    {"tema":"narcis",  "hook":"O narcisista que você não consegue dormir depois de ver","tipo":"dark"},
    {"tema":"burnout", "hook":"Seu corpo pediu para parar antes de você saber",         "tipo":"reflexivo"},
    {"tema":"apego",   "hook":"Por que você fica ansioso quando alguém some",           "tipo":"revelacao"},
    {"tema":"sono",    "hook":"O erro que 94% das pessoas cometem antes de dormir",     "tipo":"revelacao"},
    {"tema":"cortisol","hook":"O hormônio que você produz toda noite sem perceber",     "tipo":"cientifico"},
    {"tema":"narcis",  "hook":"Gaslighting: quando você começa a duvidar de si mesmo",  "tipo":"dark"},
    {"tema":"trauma",  "hook":"Por que traumas aparecem nos sonhos",                    "tipo":"reflexivo"},
    {"tema":"mindful", "hook":"4 minutos que podem mudar sua noite inteira",            "tipo":"tecnica"},
]

def groq_legenda_reel(tema, hook):
    """Gera legenda completa do Reel com CTA estratégico"""
    if not GROQ: return None
    prompt = (
        f"Write an Instagram Reel caption in Brazilian Portuguese.\n"
        f"Hook (already filmed): \"{hook}\"\n"
        f"Topic: {tema}\n\n"
        f"FORMAT:\n"
        f"Line 1: gancho (copy do hook, impactante)\n"
        f"Line 2-3: revelação psicológica real (PubMed reference)\n"
        f"Line 4: CTA explícito: '{CTA_PADRAO}'\n"
        f"Line 5: emojis relevantes\n"
        f"Tags: #psicologia #ansiedade #sono #saúdemental #danielacoelho\n\n"
        f"Max 100 words. Conversational, not clinical."
    )
    try:
        r = requests.post("https://api.groq.com/openai/v1/chat/completions",
            headers={"Authorization":f"Bearer {GROQ}","Content-Type":"application/json"},
            json={"model":"llama-3.3-70b-versatile",
                  "messages":[{"role":"user","content":prompt}],
                  "max_tokens":200,"temperature":0.85},
            timeout=15, verify=False)
        if r.status_code == 200:
            return r.json()["choices"][0]["message"]["content"].strip()
    except: pass
    return None

def salvar_reel(tema, hook, legenda):
    if not SB_KEY or not legenda: return
    requests.post(f"{SB_URL}/rest/v1/social_posts", headers=SBH,
        json={"plataforma":"instagram","tema":tema,"hook":hook[:200],
              "legenda":legenda[:500],"cta":CTA_PADRAO,
              "link_produto":LINK_VENDAS,"status":"pending"},
        timeout=8, verify=False)

def run():
    print("=== INSTAGRAM REELS PRODUCER ===\n")
    print(f"  Estratégia: 3 reels/dia sem aparecer")
    print(f"  CTA: '{CTA_PADRAO}'\n")
    total = 0
    for t in TEMAS_REELS[:5]:
        leg = groq_legenda_reel(t["tema"], t["hook"])
        if leg:
            salvar_reel(t["tema"], t["hook"], leg)
            print(f"  ✅ [{t['tema']}] {t['hook'][:45]}")
            total += 1
        time.sleep(2)
    print(f"\n  ✅ {total} legendas de Reels geradas")
    print(f"  📱 Publica 3/dia → comentários → DM → Hotmart")

if __name__=="__main__": run()
