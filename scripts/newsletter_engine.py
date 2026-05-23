#!/usr/bin/env python3
"""
newsletter_engine.py
Newsletter semanal de psicologia para Substack (paid subs $9/mês)
Groq gera conteúdo a partir de papers PsyArXiv + tendências
"""
import os, json, requests, time
from datetime import datetime, timedelta

GROQ_KEY = os.getenv("GROQ_API_KEY", "")
SUBSTACK_EMAIL = os.getenv("SUBSTACK_EMAIL", "")  # email de login Substack
SUBSTACK_PASS  = os.getenv("SUBSTACK_PASS", "")   # senha Substack (opcional)

SECOES_NEWSLETTER = [
    "Pesquisa da Semana",
    "Conceito em Foco",
    "Na Prática",
    "Para Refletir",
]

def buscar_paper_psyarxiv():
    """Busca paper recente no PsyArXiv (grátis, sem auth)"""
    try:
        r = requests.get(
            "https://api.osf.io/v2/preprints/?provider=psyarxiv&ordering=-date_created&page[size]=5",
            timeout=15)
        if r.status_code == 200:
            items = r.json().get("data", [])
            if items:
                paper = items[0]
                attrs = paper.get("attributes", {})
                return {
                    "title": attrs.get("title", "Estudo recente"),
                    "description": attrs.get("description", "")[:500],
                    "date": attrs.get("date_created", "")[:10],
                }
    except: pass
    return {"title": "Neurociência da Regulação Emocional", "description": "Pesquisa recente sobre estratégias cognitivas.", "date": datetime.now().strftime("%Y-%m-%d")}

def gerar_newsletter(paper):
    if not GROQ_KEY:
        return None
    
    semana = datetime.now().strftime("%d/%m/%Y")
    prompt = f"""Você é Daniela Coelho, pesquisadora de comportamento humano criadora da newsletter "Mente em Foco".
Escreva a edição dessa semana ({semana}) baseada neste paper:

Título: {paper['title']}
Resumo: {paper['description'][:300]}

FORMATO (markdown para Substack):
## 🧠 Mente em Foco — Semana de {semana}

### Pesquisa da Semana
[Resuma o paper em linguagem acessível, 150 palavras. Cite o estudo.]

### Conceito em Foco: [escolha um conceito central do paper]
[Explique em profundidade, 200 palavras, com exemplos do dia a dia.]

### Na Prática
[3 aplicações concretas do conceito, 150 palavras total.]

### Para Refletir
[1 pergunta reflexiva poderosa + 1 citação de pesquisador real.]

---
*Próxima semana: [próximo tema relacionado]*
*Se esse conteúdo te ajudou, encaminhe para alguém.*

TOM: newsletter inteligente de pesquisadora de comportamento humano com quem se pode confiar. PT-BR fluente.
Sem jargão excessivo. Com profundidade real."""

    try:
        r = requests.post("https://api.groq.com/openai/v1/chat/completions",
            headers={"Authorization": f"Bearer {GROQ_KEY}", "Content-Type": "application/json"},
            json={"model": "llama-3.3-70b-versatile",
                  "messages": [{"role": "user", "content": prompt}],
                  "max_tokens": 1200, "temperature": 0.75},
            timeout=60)
        if r.status_code == 200:
            return r.json()["choices"][0]["message"]["content"]
    except Exception as e:
        print(f"Groq: {e}")
    return None

def run():
    import pathlib
    print(f"=== NEWSLETTER ENGINE — {datetime.now():%Y-%m-%d} ===")
    
    # Buscar paper do PsyArXiv
    print("1. Buscando paper PsyArXiv...")
    paper = buscar_paper_psyarxiv()
    print(f"   Paper: {paper['title'][:60]}")
    
    # Gerar newsletter
    print("2. Gerando com Groq...")
    newsletter = gerar_newsletter(paper)
    
    if newsletter:
        out_dir = pathlib.Path(os.getenv("GITHUB_WORKSPACE", ".")) / "output" / "newsletter"
        out_dir.mkdir(parents=True, exist_ok=True)
        semana = datetime.now().strftime("%Y_W%V")
        out = out_dir / f"newsletter_{semana}.md"
        with open(out, "w") as f:
            f.write(newsletter)
        print(f"   Newsletter salva: {out.name}")
        print(f"
=== PUBLICAR NO SUBSTACK ===")
        print(f"1. substack.com → New Post → cole o markdown")
        print(f"2. Publish → Email subscribers")
        print(f"3. Habilitar paid subscriptions: $9/mês")
    else:
        print("   Groq indisponível neste ambiente")

if __name__ == "__main__":
    run()
