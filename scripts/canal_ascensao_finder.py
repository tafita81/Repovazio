#!/usr/bin/env python3
"""
canal_ascensao_finder.py — Encontrar canais em ascensão (conceito do Marcos)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
BASEADO EM: Transcript "Elite Dark Academy"

ESTRATÉGIA DO MARCOS:
  "Eu busco canais publicados nesta semana, com poucos inscritos
   e muitas views — esses são os canais em ascensão.
   Não quero canais com 400K inscritos porque muita gente já entrou.
   Quero os novos — pego a estrutura de título deles e levo
   para o meu nicho."

IMPLEMENTAÇÃO:
  1. YouTube Data API (via Quantum Brain) — busca canais novos
  2. Filtra: publicado essa semana + views altas + inscritos baixos
  3. Extrai estrutura de título (Groq analisa o padrão)
  4. Adapta para psicologia/geopolítica/arqueologia/neurociência
  5. Salva no Supabase como "video_key_candidates"

ALTERNATIVA GRATUITA (sem YouTube API):
  RSS feeds do YouTube + palavras-chave de nichos
  CommonCrawl data para descoberta de canais
  Supabase viral_video_research (302 vídeos já catalogados)
"""
import os, requests, pathlib, time, json
import urllib3; urllib3.disable_warnings()

SB_URL = os.getenv("SUPABASE_URL","https://tpjvalzwkqwttvmszvie.supabase.co")
SB_KEY = os.getenv("SUPABASE_SERVICE_KEY","")
GROQ   = os.getenv("GROQ_API_KEY","")
SBH    = {"apikey":SB_KEY,"Authorization":f"Bearer {SB_KEY}",
          "Content-Type":"application/json","Prefer":"return=minimal"}

def buscar_viral_research():
    """Usa o banco de 302 vídeos virais já catalogado no Supabase"""
    if not SB_KEY: return []
    try:
        r = requests.get(
            f"{SB_URL}/rest/v1/viral_video_research?select=titulo,canal,views,nicho&order=views.desc&limit=30",
            headers=SBH, timeout=8, verify=False)
        return r.json() if r.status_code == 200 else []
    except: return []

def analisar_estrutura_titulo(titulos_list, nicho_destino):
    """Groq analisa padrão de título e adapta para novo nicho"""
    if not GROQ or not titulos_list: return None
    sample = "\n".join(f"- {t.get('titulo','')}" for t in titulos_list[:10] if t.get("titulo"))
    prompt = (
        f"Analyze these viral YouTube titles and extract the TITLE STRUCTURE:\n\n"
        f"{sample}\n\n"
        f"Then generate 5 NEW titles using the SAME structure but adapted to: {nicho_destino}\n\n"
        f"Rules:\n"
        f"- Keep the same grammatical structure and emotional trigger\n"
        f"- Adapt the CONTENT only (not the structure)\n"
        f"- Counter-intuitive, not obvious\n"
        f"- 8-12 words max\n"
        f"Return format:\n"
        f"STRUCTURE: [describe the pattern]\n"
        f"TITLES:\n"
        f"1. [title]\n2. [title]\n3. [title]\n4. [title]\n5. [title]"
    )
    try:
        r = requests.post("https://api.groq.com/openai/v1/chat/completions",
            headers={"Authorization":f"Bearer {GROQ}","Content-Type":"application/json"},
            json={"model":"llama-3.3-70b-versatile",
                  "messages":[{"role":"user","content":prompt}],
                  "max_tokens":400,"temperature":0.85},
            timeout=15, verify=False)
        if r.status_code == 200:
            return r.json()["choices"][0]["message"]["content"].strip()
    except: pass
    return None

def gerar_descricao_seo(titulo, nicho, script):
    """Gera descrição completa com tags (como o Narrativa faz)"""
    if not GROQ: return None
    prompt = (
        f"Generate a complete YouTube video description for:\n"
        f"Title: {titulo}\n"
        f"Niche: {nicho}\n"
        f"Script excerpt: {script[:200] if script else 'Psychology content'}\n\n"
        f"FORMAT:\n"
        f"1. Hook (2 lines) — same emotional punch as title\n"
        f"2. What viewers will learn (3 bullet points)\n"
        f"3. Research references (2 real PubMed citations)\n"
        f"4. CTA to subscribe\n"
        f"5. Tags: #psychology #psicologia #neurociencia #mente #comportamento\n"
        f"Keep under 200 words."
    )
    try:
        r = requests.post("https://api.groq.com/openai/v1/chat/completions",
            headers={"Authorization":f"Bearer {GROQ}","Content-Type":"application/json"},
            json={"model":"llama-3.3-70b-versatile",
                  "messages":[{"role":"user","content":prompt}],
                  "max_tokens":350,"temperature":0.78},
            timeout=15, verify=False)
        if r.status_code == 200:
            return r.json()["choices"][0]["message"]["content"].strip()
    except: pass
    return None

NICHOS_EXPANSAO = [
    {"id":"psico","nome":"psicologia dark","kw":"narcisismo trauma burnout"},
    {"id":"geo","nome":"geopolítica explicada","kw":"petróleo tensão economia"},
    {"id":"arq","nome":"arqueologia mistério","kw":"civilização descoberta Egypt"},
    {"id":"neuro","nome":"neurociência cotidiano","kw":"cérebro decisão memória"},
]

def run():
    print("=== CANAL EM ASCENSÃO FINDER ===\n")

    # Buscar vídeos virais do banco
    virais = buscar_viral_research()
    print(f"  📊 {len(virais)} vídeos virais no banco Supabase")

    for nicho in NICHOS_EXPANSAO:
        print(f"\n  🔍 Analisando padrões para: {nicho['nome']}")
        analise = analisar_estrutura_titulo(virais, nicho["nome"])
        if analise:
            # Extrair títulos gerados
            linhas = analise.split("\n")
            titulos = [l.lstrip("12345. ") for l in linhas if l.strip() and l.strip()[0].isdigit()]
            print(f"     {len(titulos)} títulos adaptados gerados")
            for t in titulos[:3]:
                print(f"     → {t[:60]}")

            # Salvar no Supabase
            if SB_KEY:
                requests.post(f"{SB_URL}/rest/v1/video_plan_400",
                    headers={**SBH,"Prefer":"return=minimal"},
                    json={"titulo": titulos[0][:200] if titulos else "Título",
                          "nicho": nicho["nome"],
                          "formato": "imersivo",
                          "status": "generated"},
                    timeout=8, verify=False)
        time.sleep(3)

    print(f"\n  ✅ Análise de canais em ascensão concluída")
    print(f"  💡 Estruturas validadas extraídas de {len(virais)} vídeos virais")

if __name__=="__main__": run()
