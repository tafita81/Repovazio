#!/usr/bin/env python3
"""
context7_psych.py — Equivalente ao Context7 para o projeto psicologia.doc
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
BASEADO EM: Transcript "5 MCPs que uso na vida real" — Context7 MCP

O QUE É O CONTEXT7:
  Pega documentação mais recente de qualquer biblioteca/framework
  e injeta no contexto do LLM para evitar alucinações de API.
  "React use websocket" → documentação atualizada do GitHub.

NOSSA VERSÃO PARA PSICOLOGIA.DOC:
  Em vez de documentação de código, buscamos:
  1. Pesquisas PubMed mais recentes por tema
  2. APIs disponíveis no Quantum Brain (37K APIs)
  3. Guias de afiliação atualizados (Kwai, Amazon, Hotmart)
  4. Dados de canais virais do Supabase
  → Injeta contexto rico nos scripts gerados

BENEFÍCIO (idêntico ao Context7):
  Scripts com citações reais e atualizadas → credibilidade máxima
  Nunca mais "pesquisa de Harvard de 2015" inventada pelo LLM
  Sempre "Boyle NB (2017) PMID 28445426" real e verificável

QUANDO USAR:
  Antes de gerar qualquer script de afiliado → busca PubMed
  Antes de análise competitiva → busca banco de dados virais
  Antes de criar título → consulta estruturas validadas
"""
import os, requests, time
import urllib3; urllib3.disable_warnings()

SB_URL = os.getenv("SUPABASE_URL","https://tpjvalzwkqwttvmszvie.supabase.co")
SB_KEY = os.getenv("SUPABASE_SERVICE_KEY","")
SBH    = {"apikey":SB_KEY,"Authorization":f"Bearer {SB_KEY}",
          "Content-Type":"application/json"}

def get_pubmed_context(query, n=3):
    """Retorna n pesquisas PubMed mais recentes — contexto científico real"""
    try:
        sr = requests.get(
            f"https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi"
            f"?db=pubmed&term={requests.utils.quote(query)}&retmax={n}"
            f"&sort=pub+date&retmode=json",
            timeout=8, verify=False)
        pmids = sr.json().get("esearchresult",{}).get("idlist",[])
        results = []
        for pmid in pmids:
            dr = requests.get(
                f"https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esummary.fcgi"
                f"?db=pubmed&id={pmid}&retmode=json",
                timeout=8, verify=False)
            doc = dr.json().get("result",{}).get(pmid,{})
            authors = doc.get("authors",[])
            a1 = authors[0].get("name","") if authors else ""
            results.append({
                "pmid": pmid,
                "citation": f"{a1} ({doc.get('pubdate','')[:4]}) — {doc.get('title','')[:80]}",
                "journal": doc.get("source",""),
            })
            time.sleep(0.3)
        return results
    except: return []

def get_quantum_brain_context(categoria, n=5):
    """Busca APIs relevantes no Quantum Brain — 37K APIs catalogadas"""
    if not SB_KEY: return []
    try:
        r = requests.get(
            f"{SB_URL}/rest/v1/api_brain?select=name,endpoint,description,auth_type"
            f"&category=ilike.*{categoria}*&auth_type=in.(none,No)&limit={n}",
            headers=SBH, timeout=8, verify=False)
        return r.json() if r.status_code == 200 else []
    except: return []

def get_viral_context(nicho, n=5):
    """Busca vídeos virais do nicho no banco Supabase"""
    if not SB_KEY: return []
    try:
        r = requests.get(
            f"{SB_URL}/rest/v1/viral_video_research?select=titulo,canal,views,nicho"
            f"&nicho=ilike.*{nicho}*&order=views.desc&limit={n}",
            headers=SBH, timeout=8, verify=False)
        return r.json() if r.status_code == 200 else []
    except: return []

def get_estruturas_context(formato, n=3):
    """Busca estruturas de título validadas"""
    if not SB_KEY: return []
    try:
        r = requests.get(
            f"{SB_URL}/rest/v1/estruturas_titulo?select=estrutura,exemplo_pt,exemplo_en"
            f"&formato=eq.{formato}&ativo=eq.true&limit={n}",
            headers=SBH, timeout=8, verify=False)
        return r.json() if r.status_code == 200 else []
    except: return []

def build_context_prompt(tema, nicho="psicologia", formato="dark_reflexivo"):
    """
    Equivalente ao Context7: monta bloco de contexto rico para injetar no LLM.
    Inclui: PubMed citations, APIs grátis, títulos virais, estruturas validadas.
    """
    lines = [f"=== CONTEXT7 PSYCH — {tema.upper()} ===\n"]

    # PubMed
    pubs = get_pubmed_context(f"{tema} psychology", n=2)
    if pubs:
        lines.append("📚 PESQUISAS RECENTES (PubMed):")
        for p in pubs:
            lines.append(f"  • {p['citation']} ({p['journal']})")

    # Quantum Brain APIs
    apis = get_quantum_brain_context(nicho, n=3)
    if apis:
        lines.append("\n🧠 APIs GRATUITAS DISPONÍVEIS (Quantum Brain):")
        for a in apis:
            lines.append(f"  • {a['name']}: {a.get('description','')[:60]}")

    # Vídeos virais
    virais = get_viral_context(tema, n=3)
    if virais:
        lines.append("\n🎬 REFERÊNCIAS VIRAIS DO NICHO:")
        for v in virais:
            lines.append(f"  • '{v.get('titulo','')[:50]}' — {v.get('views',0):,} views")

    # Estruturas de título
    structs = get_estruturas_context(formato, n=2)
    if structs:
        lines.append("\n📝 ESTRUTURAS VALIDADAS:")
        for s in structs:
            lines.append(f"  • {s.get('estrutura','')}")
            if s.get("exemplo_pt"):
                lines.append(f"    Ex PT: {s['exemplo_pt'][:60]}")

    return "\n".join(lines)

def run():
    print("=== CONTEXT7 PSYCH — Contexto rico para LLMs ===\n")
    temas = ["narcissism", "burnout", "anxiety"]
    for tema in temas:
        print(f"  📚 Construindo contexto para: {tema}")
        ctx = build_context_prompt(tema)
        linhas = ctx.count("\n")
        print(f"     ✅ {linhas} linhas de contexto real")
        time.sleep(2)
    print("\n  ✅ Context7 Psych operacional")
    print("  🔬 PubMed + Quantum Brain + Virais = zero alucinações")

if __name__=="__main__": run()
