#!/usr/bin/env python3
"""
viral_content_engine.py — Engine de conteúdo viral de altíssima qualidade
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
O que fazem os maiores canais de psicologia do mundo:
  1. Pesquisa científica real (PubMed, Harvard, Stanford)
  2. Hook nas primeiras 3 segundos (visual + texto impactante)
  3. Pacing rápido: 1 nova informação a cada 15-30 segundos
  4. Miniaturas com alto CTR: rosto + número + cor contrastante
  5. Título com keyword de alto volume + urgência
  6. Pinned comment com CTA nas primeiras 5 minutos
  7. Cards no minuto 3, 7, 12 com próximo vídeo
  8. End screen últimos 20 segundos
  9. Publicação no prime time do país-alvo
  10. Resposta a todos os comentários nas primeiras 2h

MÉTRICAS QUE IMPORTAM:
  - CTR (taxa de clique na thumbnail): meta >8%
  - AVD (duração média de visualização): meta >50% do vídeo
  - Engajamento: likes/views meta >4%
  - Comentários: meta >0.5% das views
"""
import os, requests, time
import urllib3; urllib3.disable_warnings()

GROQ_KEY = os.getenv("GROQ_API_KEY","")
SB_URL   = os.getenv("SUPABASE_URL","https://tpjvalzwkqwttvmszvie.supabase.co")
SB_KEY   = os.getenv("SUPABASE_SERVICE_KEY","")
SBH      = {"apikey":SB_KEY,"Authorization":f"Bearer {SB_KEY}",
            "Content-Type":"application/json","Prefer":"return=minimal"}

# Temas com MAIOR volume de busca confirmado (dados Google Trends)
TEMAS_VIRAIS = [
    {"kw":"narcisismo encoberto","vol_br":90500,"vol_us":165000,"dificuldade":"media"},
    {"kw":"gaslighting","vol_br":74000,"vol_us":550000,"dificuldade":"baixa"},
    {"kw":"apego ansioso","vol_br":60500,"vol_us":110000,"dificuldade":"media"},
    {"kw":"síndrome do impostor","vol_br":49500,"vol_us":201000,"dificuldade":"baixa"},
    {"kw":"burnout","vol_br":201000,"vol_us":823000,"dificuldade":"alta"},
    {"kw":"insônia ansiedade","vol_br":74000,"vol_us":165000,"dificuldade":"media"},
    {"kw":"trauma emocional","vol_br":40500,"vol_us":110000,"dificuldade":"media"},
    {"kw":"related disorders psicologia","vol_br":33000,"vol_us":90000,"dificuldade":"baixa"},
]

def groq_gerar_titulo_viral(tema, idioma="PT"):
    if not GROQ_KEY: return f"{tema['kw'].title()} — O Que A Ciência Diz"
    prompt = (
        f"Gere 5 títulos virais para YouTube sobre '{tema['kw']}'.\n"
        f"Idioma: {'PT-BR' if idioma=='PT' else 'English'}\n"
        f"Volume de busca: {tema['vol_br' if idioma=='PT' else 'vol_us']:,}/mês\n"
        f"FÓRMULAS que funcionam:\n"
        f"  - Número + Sinais + Que + Maioria + Ignora\n"
        f"  - Por Que + Você + Verbo + Quem + Machuca\n"
        f"  - Harvard Descobriu Que + Afirmação Contraintuitiva\n"
        f"  - O Que Ninguém Te Conta Sobre + Tema\n"
        f"  - Você Tem + Tema + Se + Comportamento Específico\n"
        f"MAX 60 chars por título. Um por linha. Sem numeração."
    )
    try:
        r = requests.post("https://api.groq.com/openai/v1/chat/completions",
            headers={"Authorization":f"Bearer {GROQ_KEY}","Content-Type":"application/json"},
            json={"model":"llama-3.3-70b-versatile",
                  "messages":[{"role":"user","content":prompt}],
                  "max_tokens":200,"temperature":0.9},
            timeout=12, verify=False)
        if r.status_code == 200:
            return r.json()["choices"][0]["message"]["content"].strip()
    except: pass
    return tema["kw"]

def gerar_pinned_comment(tema, link_produto):
    if not GROQ_KEY: return f"Comenta SONO para receber algo especial sobre {tema['kw']} 👇 {link_produto}"
    prompt = (
        f"Gere um pinned comment para YouTube sobre '{tema['kw']}'.\n"
        f"Objetivo: direcionar para produto R$29,90.\n"
        f"Link: {link_produto}\n"
        f"Estilo: natural, como Daniela falaria (pesquisadora de comportamento humano).\n"
        f"CTA: 'Comenta SONO que te envio algo especial 👇'\n"
        f"MAX 3 linhas. Não mencionar psicóloga."
    )
    try:
        r = requests.post("https://api.groq.com/openai/v1/chat/completions",
            headers={"Authorization":f"Bearer {GROQ_KEY}","Content-Type":"application/json"},
            json={"model":"llama-3.3-70b-versatile",
                  "messages":[{"role":"user","content":prompt}],
                  "max_tokens":100,"temperature":0.8},
            timeout=10, verify=False)
        if r.status_code == 200:
            return r.json()["choices"][0]["message"]["content"].strip()
    except: pass
    return f"Comenta SONO que te envio algo especial 🌙\n{link_produto}"

def run():
    print("=== VIRAL CONTENT ENGINE ===")
    print("  Estratégia dos maiores canais: pesquisa real + hook + pacing + SEO\n")
    for tema in TEMAS_VIRAIS[:4]:
        print(f"  📊 {tema['kw']} — {tema['vol_br']:,} buscas/mês BR | {tema['vol_us']:,} US")
        titulos = groq_gerar_titulo_viral(tema, "PT")
        print(f"  Títulos PT:\n{titulos}")
        pinned = gerar_pinned_comment(tema, "repovazio.vercel.app/app-vendas")
        print(f"  Pinned: {pinned[:80]}...")
        if SB_KEY:
            requests.post(f"{SB_URL}/rest/v1/video_seo",
                headers={**SBH,"Prefer":"return=minimal"},
                json={"video_id":f"viral_{tema['kw'].replace(' ','_')}_{int(time.time())}",
                      "titulo_principal":titulos.split('\n')[0][:100] if titulos else tema['kw'],
                      "status":"ready"},
                timeout=8, verify=False)
        print()
        time.sleep(1.5)

if __name__=="__main__": run()
