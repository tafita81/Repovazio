#!/usr/bin/env python3
"""
firecrawl_free.py — Equivalente gratuito ao Firecrawl (transcript 6)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
BASEADO EM: Transcript "5 MCPs que uso na vida real"

O QUE É O FIRECRAWL:
  Scraper + LLM que retorna páginas como markdown semântico.
  Vantagem: não depende de estrutura CSS (layout pode mudar).
  Desvantagem: pago ($16+/mês) e $5 crédito por 1000 páginas.

NOSSA IMPLEMENTAÇÃO GRATUITA:
  1. requests.get() → HTML raw
  2. BeautifulSoup → extrai texto limpo (sem CSS/JS)
  3. Converte para Markdown (similar ao Firecrawl)
  4. DeepSeek V4 (via router_v5) → análise semântica
  5. Retorna dados estruturados em JSON

CASOS DE USO NO PROJETO:
  - Scraping de páginas de afiliados (Amazon, Hotmart, Shopee)
  - Monitorar canais virais no YouTube (títulos, views)
  - Extrair pesquisas do PubMed, CrossRef, WHO
  - Verificar preços de produtos dos afiliados

DIFERENÇA DO PLAYWRIGHT:
  Playwright: abre navegador real → pesado, lento, requer Chrome
  Este: HTTP puro → leve, rápido, sem dependência
  Use este 90% das vezes. Playwright só para JS-heavy.
"""
import os, re, requests
import urllib3; urllib3.disable_warnings()

try:
    from html.parser import HTMLParser
except: pass

SB_URL = os.getenv("SUPABASE_URL","https://tpjvalzwkqwttvmszvie.supabase.co")
SB_KEY = os.getenv("SUPABASE_SERVICE_KEY","")

class HTMLToMarkdown(HTMLParser):
    """Parser simples HTML → Markdown (sem dependências externas)"""
    def __init__(self):
        super().__init__()
        self.result = []
        self.skip   = False
        self.skip_tags = {"script","style","nav","footer","iframe","noscript"}

    def handle_starttag(self, tag, attrs):
        if tag in self.skip_tags: self.skip = True
        if tag == "h1": self.result.append("\n# ")
        elif tag in ("h2","h3"): self.result.append("\n## ")
        elif tag in ("h4","h5","h6"): self.result.append("\n### ")
        elif tag == "p": self.result.append("\n")
        elif tag == "li": self.result.append("\n- ")
        elif tag == "br": self.result.append("\n")
        elif tag == "strong": self.result.append("**")
        elif tag == "em": self.result.append("_")

    def handle_endtag(self, tag):
        if tag in self.skip_tags: self.skip = False
        if tag == "strong": self.result.append("**")
        elif tag == "em": self.result.append("_")

    def handle_data(self, data):
        if not self.skip:
            clean = data.strip()
            if clean: self.result.append(clean + " ")

    def get_markdown(self):
        text = "".join(self.result)
        text = re.sub(r'\n{3,}', '\n\n', text)
        return text.strip()[:8000]  # máx 8K chars

def scrape_to_markdown(url, timeout=15):
    """Scrape URL → markdown semântico (equivalente ao Firecrawl)"""
    try:
        r = requests.get(url, timeout=timeout, verify=False,
            headers={"User-Agent": "Mozilla/5.0 (compatible; PsychBot/1.0)"})
        if r.status_code != 200:
            return None, f"HTTP {r.status_code}"
        parser = HTMLToMarkdown()
        parser.feed(r.text)
        md = parser.get_markdown()
        return md, None
    except Exception as e:
        return None, str(e)

def semantic_extract(url, query, retornar_json=False):
    """
    Equivalente ao Firecrawl: scrape + análise semântica via DeepSeek.
    
    Exemplo:
      semantic_extract("https://site.com", "qual o preço do magnésio?")
      → "R$ 89,90 o frasco de 60 cápsulas"
    """
    md, err = scrape_to_markdown(url)
    if not md:
        return f"Erro ao scraping: {err}"

    try:
        from scripts.llm_router_v5 import completar
    except:
        try:
            import sys; sys.path.insert(0,'scripts')
            from llm_router_v5 import completar
        except:
            completar = None

    if not completar:
        # Fallback: retorna markdown bruto
        return md[:2000]

    formato = "Return as JSON with keys: answer, confidence (0-1), source_text" if retornar_json else "Return a direct, concise answer in Portuguese."

    prompt = (
        f"Analyze this web page content and answer the question.\n"
        f"Question: {query}\n"
        f"Page content (Markdown):\n{md[:4000]}\n\n"
        f"{formato}"
    )
    return completar(prompt, tarefa="analise", max_tokens=300, temperature=0.3)

URLS_MONITORAR = [
    {"nome":"PubMed Narcisismo","url":"https://pubmed.ncbi.nlm.nih.gov/?term=narcissism+psychology","query":"latest research on narcissism published this year"},
    {"nome":"WHO Mental Health","url":"https://www.who.int/news-room/fact-sheets/detail/mental-disorders","query":"prevalence of mental disorders worldwide statistics"},
    {"nome":"Shopee Magnésio","url":"https://shopee.com.br/search?keyword=magnesio+glicinato","query":"preço e avaliação do magnésio glicinato mais vendido"},
]

def run():
    print("=== FIRECRAWL FREE — Scraping Semântico ===\n")
    for item in URLS_MONITORAR[:2]:  # teste com 2 primeiros
        print(f"  🌐 {item['nome']}")
        resultado = semantic_extract(item["url"], item["query"])
        if resultado:
            print(f"     ✅ {resultado[:120]}...")
        else:
            print(f"     ⚠️  sem resultado")
        import time; time.sleep(3)

if __name__=="__main__": run()
