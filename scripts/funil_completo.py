#!/usr/bin/env python3
"""
funil_completo.py — Funil de vendas completo multi-plataforma
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Gera para cada vídeo:
  - Título A/B testável (2 variações)
  - Descrição YouTube SEO completa
  - Tags relevantes
  - CTA com link do produto WhatsApp
  - Pin do primeiro comentário
  - Legenda TikTok/Kwai (versão curta)
"""
import os, requests, time, json
import urllib3; urllib3.disable_warnings()

SB_URL = os.getenv("SUPABASE_URL","https://tpjvalzwkqwttvmszvie.supabase.co")
SB_KEY = os.getenv("SUPABASE_SERVICE_KEY","")
GROQ   = os.getenv("GROQ_API_KEY","")
SBH    = {"apikey":SB_KEY,"Authorization":f"Bearer {SB_KEY}",
          "Content-Type":"application/json","Prefer":"return=minimal"}

LINK_PRODUTO = "repovazio.vercel.app/psicologia-para-dormir"
LINK_WA      = "wa.me/?text=SONO"

VIDEOS_SEO = [
    {"id":"narcis1","titulo":"O Narcisista Que Você Não Vê Vir","tema":"narcisismo","keywords":["narcisismo","psicologia","manipulação","gaslighting"]},
    {"id":"burnout1","titulo":"Burnout Não Começa Com Cansaço","tema":"burnout","keywords":["burnout","esgotamento","saúde mental","cortisol"]},
    {"id":"sono1","titulo":"Por Que Você Acorda Às 3h da Manhã","tema":"sono","keywords":["insônia","sono","3h manhã","cortisol sono"]},
    {"id":"apego1","titulo":"Por Que Você Escolhe Quem Te Machuca","tema":"apego","keywords":["apego ansioso","relacionamento tóxico","psicologia","teoria apego"]},
    {"id":"528hz","titulo":"528Hz Enquanto Você Dorme — Reduz Cortisol","tema":"binaural","keywords":["528hz","frequência","binaural","cortisol sono","solfeggio"]},
]

def groq_seo_completo(video):
    if not GROQ: return None
    prompt = (
        f"Gere SEO completo para YouTube em PT-BR. Responda APENAS JSON válido.\n"
        f"Título: {video['titulo']}\nTema: {video['tema']}\n"
        f"Keywords: {', '.join(video['keywords'])}\n"
        f"Link produto: {LINK_PRODUTO}\n\n"
        f"JSON com os campos:\n"
        f"\"titulo_a\": variação A do título (mantém a essência)\n"
        f"\"titulo_b\": variação B mais impactante (diferente estrutura)\n"
        f"\"descricao\": descrição 200 palavras com SEO, CTA para '{LINK_PRODUTO}', cita pesquisa real\n"
        f"\"tags\": array 15 tags YouTube relevantes\n"
        f"\"comentario_fixado\": texto do 1o comentário fixado com link do grupo\n"
        f"\"legenda_tiktok\": versão curta 50 palavras para TikTok/Kwai com CTA 'Link na bio'"
    )
    try:
        r = requests.post("https://api.groq.com/openai/v1/chat/completions",
            headers={"Authorization":f"Bearer {GROQ}","Content-Type":"application/json"},
            json={"model":"llama-3.3-70b-versatile",
                  "messages":[{"role":"user","content":prompt}],
                  "max_tokens":800,"temperature":0.78},
            timeout=25, verify=False)
        if r.status_code == 200:
            txt = r.json()["choices"][0]["message"]["content"].strip()
            txt = txt.replace("```json","").replace("```","").strip()
            return json.loads(txt)
    except: pass
    return None

def salvar_seo(video, seo):
    if not SB_KEY or not seo: return
    requests.post(f"{SB_URL}/rest/v1/video_seo", headers=SBH,
        json={"video_id":video["id"],"titulo_principal":video["titulo"],
              "titulo_a":seo.get("titulo_a","")[:200],"titulo_b":seo.get("titulo_b","")[:200],
              "descricao":seo.get("descricao","")[:2000],
              "tags":json.dumps(seo.get("tags",[])),
              "comentario_fixado":seo.get("comentario_fixado","")[:300],
              "legenda_tiktok":seo.get("legenda_tiktok","")[:200],
              "status":"ready"}, timeout=8, verify=False)

def run():
    print("=== FUNIL COMPLETO — SEO YouTube + TikTok + CTA ===\n")
    total = 0
    for v in VIDEOS_SEO:
        print(f"  🎬 {v['titulo'][:45]}")
        seo = groq_seo_completo(v)
        if seo:
            salvar_seo(v, seo)
            total += 1
            print(f"     ✅ A/B títulos + descrição SEO + {len(seo.get('tags',[]))} tags")
        time.sleep(2)
    print(f"\n  ✅ {total} vídeos com SEO completo")
    print(f"  🔗 CTA → {LINK_PRODUTO}")

if __name__=="__main__": run()
