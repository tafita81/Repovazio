#!/usr/bin/env python3
"""
research_monitor.py — Monitor Automático de Pesquisa Científica
Cruzamento: PubMed (no-auth) + OpenAlex (no-auth) + Semantic Scholar (no-auth) + LLM + TTS + YouTube

IDEIA ÚNICA: Nenhum canal de psicologia BR publica conteúdo baseado em
pesquisa NOVA. Este sistema monitora PubMed/OpenAlex diariamente e gera
vídeo sobre o paper mais relevante publicado nos últimos 7 dias.
Primeiro canal BR a cobrir breaking science em psicologia.

Roda via GitHub Action todo dia às 6h UTC.
"""

import requests, json, os, time
from datetime import datetime, timedelta

GROQ_KEY = os.getenv("GROQ_API_KEY","")
SB_URL   = os.getenv("SUPABASE_URL","https://tpjvalzwkqwttvmszvie.supabase.co")
SB_KEY   = os.getenv("SUPABASE_SERVICE_ROLE_KEY","")

TOPICS = [
    "narcissistic personality disorder treatment",
    "anxiety cognitive behavioral therapy brazil",
    "relationship trauma attachment style",
    "borderline personality disorder intervention",
    "depression mindfulness effectiveness"
]

def buscar_pubmed(query: str, dias: int = 7) -> list:
    """Busca papers recentes no PubMed — gratuito, sem auth"""
    desde = (datetime.now() - timedelta(days=dias)).strftime("%Y/%m/%d")
    
    # Busca IDs
    r = requests.get("https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi", params={
        "db": "pubmed", "term": query,
        "mindate": desde, "maxdate": datetime.now().strftime("%Y/%m/%d"),
        "retmax": 5, "retmode": "json", "sort": "pub_date"
    }, timeout=15)
    
    if r.status_code != 200: return []
    ids = r.json().get("esearchresult",{}).get("idlist",[])
    if not ids: return []
    
    # Busca detalhes
    r2 = requests.get("https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esummary.fcgi", params={
        "db": "pubmed", "id": ",".join(ids), "retmode": "json"
    }, timeout=15)
    
    if r2.status_code != 200: return []
    result = r2.json().get("result",{})
    
    papers = []
    for uid in ids:
        p = result.get(uid,{})
        if p.get("title"):
            papers.append({
                "pmid": uid,
                "titulo_en": p.get("title",""),
                "autores": [a.get("name","") for a in p.get("authors",[])[:3]],
                "revista": p.get("source",""),
                "data": p.get("pubdate",""),
                "url": f"https://pubmed.ncbi.nlm.nih.gov/{uid}/"
            })
    return papers

def buscar_semantic_scholar(query: str) -> list:
    """Busca papers no Semantic Scholar — gratuito, sem auth"""
    r = requests.get("https://api.semanticscholar.org/graph/v1/paper/search", params={
        "query": query, "limit": 5,
        "fields": "title,authors,year,abstract,venue,openAccessPdf",
        "publicationDateOrYear": f"{datetime.now().year}"
    }, timeout=15)
    
    if r.status_code != 200: return []
    papers = []
    for p in r.json().get("data",[]):
        if p.get("title") and p.get("abstract"):
            papers.append({
                "titulo_en": p["title"],
                "autores": [a.get("name","") for a in p.get("authors",[])[:3]],
                "ano": p.get("year",""),
                "abstract": p.get("abstract","")[:500],
                "pdf": p.get("openAccessPdf",{}).get("url","")
            })
    return papers

def gerar_script_baseado_em_paper(paper: dict) -> dict:
    """Transforma paper científico em roteiro viral PT-BR"""
    if not GROQ_KEY: return {}
    
    prompt = f"""
Você é Daniela Coelho, psicóloga brasileira que explica ciência de forma acessível.

Um novo paper científico foi publicado:
Título (EN): {paper.get('titulo_en','')}
Autores: {', '.join(paper.get('autores',[]))}
Resumo: {paper.get('abstract','')}

Crie um roteiro em bullet points para vídeo YouTube de 12 minutos em PT-BR.
Tom: íntimo, não-vitimização, baseado em ciência real, acessível.
NÃO traduza o título literalmente — crie um título viral em PT-BR.

Responda em JSON:
{{
  "titulo_ptbr": "título viral em português",
  "hook": "frase de abertura de impacto",
  "por_que_isso_importa": "explicação em 2 linhas para o brasileiro médio",
  "roteiro_bullets": ["• ponto1", "• ponto2"],
  "pesquisadores": "citação correta: nome e instituição",
  "cta": "chamada para ação final"
}}
"""
    
    r = requests.post("https://api.groq.com/openai/v1/chat/completions",
        headers={"Authorization": f"Bearer {GROQ_KEY}", "Content-Type": "application/json"},
        json={"model": "llama-3.3-70b-versatile", "messages": [{"role":"user","content":prompt}],
              "max_tokens": 2000, "response_format": {"type": "json_object"}},
        timeout=60)
    
    if r.status_code == 200:
        return json.loads(r.json()["choices"][0]["message"]["content"])
    return {}

def run():
    print("RESEARCH MONITOR — Psicologia.doc")
    print("="*50)
    
    todos_papers = []
    for topic in TOPICS[:2]:  # 2 topics por run para não sobrecarregar
        print(f"Buscando: {topic}")
        papers_pm = buscar_pubmed(topic)
        papers_ss = buscar_semantic_scholar(topic)
        todos_papers.extend(papers_pm + papers_ss)
        time.sleep(1)
    
    if not todos_papers:
        print("Nenhum paper novo encontrado hoje")
        return
    
    # Pegar o mais relevante (com abstract disponível)
    paper_top = next((p for p in todos_papers if p.get("abstract")), todos_papers[0])
    print(f"Paper top: {paper_top.get('titulo_en','')[:80]}")
    
    # Gerar script
    script = gerar_script_baseado_em_paper(paper_top)
    if script:
        print(f"Titulo PT-BR: {script.get('titulo_ptbr','')}")
        
        # Salvar no Supabase
        if SB_KEY:
            requests.post(f"{SB_URL}/rest/v1/research_monitor",
                headers={"apikey": SB_KEY, "Authorization": f"Bearer {SB_KEY}",
                         "Content-Type": "application/json"},
                json={**script, "paper_fonte": paper_top.get("titulo_en",""),
                      "data": datetime.now().isoformat(), "status": "script_pronto"},
                timeout=15)
    
    print("Done!")

if __name__ == "__main__":
    run()
