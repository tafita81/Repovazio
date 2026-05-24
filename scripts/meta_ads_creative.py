#!/usr/bin/env python3
"""
meta_ads_creative.py
Gera criativos para Meta Ads (Facebook/Instagram) automaticamente.

Modelo: $877K/mês com marca anônima — zero rosto, 100% produto + ads.
Daniela Coelho = identidade de marca, sem revelar Rafael.

Formatos gerados:
  - Hook (3 segundos que param o scroll)
  - Body copy (problema → solução → CTA)
  - Headline + descrição
  - Script para Reels/Stories
  - Texto para carrossel (5 cards)

APIs usadas: Groq (LLM) + ZenQuotes + PubMed + OpenFDA + WikiData
"""
import os, requests, time, json

GROQ = os.getenv("GROQ_API_KEY", "")
SB_URL = os.getenv("SUPABASE_URL", "https://tpjvalzwkqwttvmszvie.supabase.co")
SB_KEY = os.getenv("SUPABASE_SERVICE_KEY", "")
SBH = {"apikey": SB_KEY, "Authorization": f"Bearer {SB_KEY}",
       "Content-Type": "application/json", "Prefer": "return=minimal"}

PRODUTOS = [
    {
        "nome": "Curso Apego Ansioso",
        "preco": "R$97",
        "dor": "Você se apega demais e as pessoas acabam indo embora",
        "solucao": "Identifique seu padrão de apego e mude em 21 dias",
        "url": "daniela.psicologia.doc/apego",
        "keywords": ["apego ansioso", "relacionamento", "abandono", "ciúme"],
    },
    {
        "nome": "Guia Narcisismo Encoberto",
        "preco": "R$47",
        "dor": "Você não consegue identificar quando está sendo manipulado",
        "solucao": "12 sinais que indicam narcisismo encoberto no seu relacionamento",
        "url": "daniela.psicologia.doc/narcisismo",
        "keywords": ["narcisismo", "manipulação", "gaslighting", "relacionamento tóxico"],
    },
    {
        "nome": "Protocolo Burnout",
        "preco": "R$67",
        "dor": "Você descansa mas não recupera, trabalha mas não progride",
        "solucao": "Protocolo científico para sair do burnout em 30 dias",
        "url": "daniela.psicologia.doc/burnout",
        "keywords": ["burnout", "esgotamento", "trabalho", "estresse"],
    },
    {
        "nome": "Ebook 528Hz Sono",
        "preco": "R$27",
        "dor": "Você não consegue desligar a cabeça para dormir",
        "solucao": "Como usar frequências sonoras para dormir profundamente",
        "url": "daniela.psicologia.doc/sono",
        "keywords": ["insônia", "sono", "528hz", "meditação"],
    },
]

IDIOMAS = {
    "PT": "português brasileiro",
    "EN": "English",
    "ES": "español",
}

def pubmed_cit(query):
    try:
        r = requests.get(
            f"https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi?db=pubmed&term={requests.utils.quote(query)}&retmax=1&retmode=json",
            timeout=7)
        pmids = r.json().get("esearchresult", {}).get("idlist", [])
        if pmids:
            r2 = requests.get(
                f"https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esummary.fcgi?db=pubmed&id={pmids[0]}&retmode=json",
                timeout=7)
            doc = r2.json().get("result", {}).get(pmids[0], {})
            a = (doc.get("authors", [{}]) or [{}])[0].get("name", "")
            return f"{a} ({doc.get('pubdate','')[:4]})"
    except: pass
    return "Research (NCBI)"

def groq(prompt, max_tokens=400):
    if not GROQ: return None
    try:
        r = requests.post(
            "https://api.groq.com/openai/v1/chat/completions",
            headers={"Authorization": f"Bearer {GROQ}", "Content-Type": "application/json"},
            json={"model": "llama-3.3-70b-versatile",
                  "messages": [{"role": "user", "content": prompt}],
                  "max_tokens": max_tokens, "temperature": 0.80},
            timeout=20)
        if r.status_code == 200:
            return r.json()["choices"][0]["message"]["content"].strip()
    except: pass
    return None

def gerar_criativo(produto, idioma="PT"):
    lang = IDIOMAS.get(idioma, "português brasileiro")
    cit = pubmed_cit(" ".join(produto["keywords"][:2]))

    # Hook (para o scroll em 3 segundos)
    hook_prompt = (
        f"Crie um hook para anúncio Meta Ads em {lang}. "
        f"Produto: {produto['nome']} ({produto['preco']}). "
        f"Dor: {produto['dor']}. "
        f"Regras: máx 15 palavras, começa com número ou fato chocante, "
        f"provoca curiosidade sem ser clickbait, usa dado científico de {cit}. "
        f"Retorna APENAS o hook, sem explicação."
    )

    # Body copy (problema → agitação → solução → CTA)
    body_prompt = (
        f"Escreva body copy para anúncio Meta Ads em {lang}. "
        f"Produto: {produto['nome']} ({produto['preco']}). "
        f"Dor: {produto['dor']}. Solução: {produto['solucao']}. "
        f"Estrutura: 1 linha problema, 1 linha agitação (piora), 1 linha revelação, "
        f"1 linha solução, CTA com URL {produto['url']}. "
        f"Total: 80-100 palavras. Tom: especialista empático, não vendedor. "
        f"Cite {cit} naturalmente. Retorna apenas o texto do anúncio."
    )

    # Carrossel 5 cards
    carousel_prompt = (
        f"Crie títulos para carrossel de 5 cards em {lang} sobre: {produto['nome']}. "
        f"Cada card = 1 sinal ou insight sobre {produto['dor']}. "
        f"Card 1: hook impactante. Cards 2-4: sinais específicos. Card 5: CTA. "
        f"Formato: CARD 1: [título]\nCARD 2: [título] etc. Máx 8 palavras por card."
    )

    hook = groq(hook_prompt, 60)
    time.sleep(1.2)
    body = groq(body_prompt, 200)
    time.sleep(1.2)
    carousel = groq(carousel_prompt, 150)

    criativo = {
        "produto": produto["nome"],
        "preco": produto["preco"],
        "idioma": idioma,
        "citacao": cit,
        "hook": hook,
        "body_copy": body,
        "carousel_titles": carousel,
        "url": produto["url"],
        "keywords": produto["keywords"],
    }
    return criativo

def salvar(criativo):
    if not SB_KEY: return
    requests.post(f"{SB_URL}/rest/v1/meta_ads_creatives", headers=SBH,
        json={
            "produto": criativo["produto"],
            "idioma": criativo["idioma"],
            "hook": criativo.get("hook", "")[:500],
            "body_copy": criativo.get("body_copy", "")[:2000],
            "carousel_titles": criativo.get("carousel_titles", "")[:1000],
            "url": criativo["url"],
            "status": "pending_test",
        }, timeout=8)

def run():
    print("=== META ADS CREATIVE GENERATOR ===")
    print("Modelo: $877K/mês — marca anônima, zero rosto\n")
    total = 0
    for produto in PRODUTOS:
        for idioma in ["PT", "EN"]:  # PT e EN prioritários
            print(f"  {produto['nome'][:30]} [{idioma}]...")
            criativo = gerar_criativo(produto, idioma)
            if criativo.get("hook"):
                print(f"    Hook: {criativo['hook'][:60]}")
                salvar(criativo)
                total += 1
            time.sleep(2)
    print(f"\n✅ {total} criativos gerados e salvos no Supabase")
    print("→ Próximo passo: Meta Ads Library → testar hooks")

if __name__ == "__main__":
    run()
