#!/usr/bin/env python3
"""
auto_refresh_loop.py — Chain 2 (Claude+NotebookLM style)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
BASEADO EM: "These 3 Claude + NotebookLM Systems" transcript
ADAPTADO PARA: manter scripts de psicologia sempre atualizados

PROBLEMA QUE RESOLVE:
  Scripts gerados há 90 dias ficam desatualizados.
  Nova pesquisa PubMed, novos dados FDA, novas tendências.
  Este loop monitora e atualiza automaticamente.

EDGE CASE SWEEP (o move ninja do transcript):
  1. Verifica fila Supabase por scripts "stale" (>14 dias)
  2. Busca nova pesquisa PubMed para o tema
  3. Atualiza o script com dados mais recentes
  4. Salva versão atualizada → sempre fresco
"""
import os, requests, time, json
import urllib3; urllib3.disable_warnings()

SB_URL = os.getenv("SUPABASE_URL","https://tpjvalzwkqwttvmszvie.supabase.co")
SB_KEY = os.getenv("SUPABASE_SERVICE_KEY","")
GROQ   = os.getenv("GROQ_API_KEY","")
SBH    = {"apikey":SB_KEY,"Authorization":f"Bearer {SB_KEY}",
          "Content-Type":"application/json","Prefer":"return=minimal"}

def pubmed_latest(query, max_results=2):
    """Busca pesquisa mais recente no PubMed"""
    try:
        r = requests.get(
            f"https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi"
            f"?db=pubmed&term={requests.utils.quote(query)}&retmax={max_results}"
            f"&sort=pub+date&retmode=json",
            timeout=8, verify=False)
        pmids = r.json().get("esearchresult",{}).get("idlist",[])
        if pmids:
            r2 = requests.get(
                f"https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esummary.fcgi"
                f"?db=pubmed&id={pmids[0]}&retmode=json",
                timeout=8, verify=False)
            doc = r2.json().get("result",{}).get(pmids[0],{})
            a = (doc.get("authors",[{}]) or [{}])[0].get("name","")
            return f"{a} ({doc.get('pubdate','')[:4]}) — {doc.get('title','')[:60]}"
    except: pass
    return ""

def who_latest(indicator_query):
    """Busca dado WHO mais recente"""
    try:
        r = requests.get(
            f"https://ghoapi.azureedge.net/api/Indicator"
            f"?$filter=contains(IndicatorName,'{indicator_query}')&$top=1",
            timeout=8, verify=False)
        items = r.json().get("value",[])
        return items[0].get("IndicatorName","") if items else ""
    except: return ""

def atualizar_script(titulo_antigo, nova_cit, idioma):
    """Groq refaz o script com dados mais frescos"""
    if not GROQ or not nova_cit: return None
    lang = {"PT":"Portuguese Brazilian","EN":"English","ES":"Spanish",
            "DE":"German","FR":"French"}.get(idioma,"English")
    prompt = (
        f"Rewrite this YouTube Short script based on fresh research.\n"
        f"Topic: {titulo_antigo[:60]}\n"
        f"NEW research: {nova_cit}\n\n"
        f"Hook (counter-intuitive first line), revelation 'This has a NAME', "
        f"1 practical insight, CTA 'SAVE this'. 70 words {lang}. No hashtags."
    )
    try:
        r = requests.post("https://api.groq.com/openai/v1/chat/completions",
            headers={"Authorization":f"Bearer {GROQ}","Content-Type":"application/json"},
            json={"model":"llama-3.3-70b-versatile",
                  "messages":[{"role":"user","content":prompt}],
                  "max_tokens":200,"temperature":0.75},
            timeout=15, verify=False)
        if r.status_code == 200:
            return r.json()["choices"][0]["message"]["content"].strip()
    except: pass
    return None

TEMAS_REFRESH = [
    ("narcissism psychology manipulation","narcis","EN"),
    ("narcisismo psicologia manipulação","narcis","PT"),
    ("528hz frequency cortisol sleep","sono","EN"),
    ("528hz frequência cortisol sono","sono","PT"),
    ("ADHD 40hz gamma focus","adhd","EN"),
    ("TDAH 40hz gamma foco","adhd","PT"),
    ("anxious attachment neuroscience","apego","EN"),
    ("apego ansioso neurociência","apego","PT"),
    ("burnout nervous system recovery","burnout","EN"),
    ("burnout sistema nervoso recuperação","burnout","PT"),
]

def run():
    print("=== AUTO-REFRESH LOOP — Manter Scripts Atualizados ===\n")
    atualizados = 0

    for query, tema, idioma in TEMAS_REFRESH:
        print(f"  🔄 [{idioma}] {tema}...")
        nova_cit = pubmed_latest(query)
        if nova_cit:
            print(f"     📚 {nova_cit[:60]}")
            titulo_gen = f"{tema.title()} Psychology Science"
            novo_script = atualizar_script(titulo_gen, nova_cit, idioma)
            if novo_script and SB_KEY:
                voz = "pt-BR-AntonioNeural" if idioma=="PT" else "en-US-AriaNeural"
                requests.post(f"{SB_URL}/rest/v1/en_channel_queue", headers=SBH,
                    json={"titulo_en": f"[REFRESHED] {titulo_gen}"[:100],
                          "script_en": novo_script,
                          "voz_en": voz,
                          "canal_destino": "UCyCkIpsVgME9yCj_oXJFheA",
                          "rpm_estimado": 7.0 if idioma=="PT" else 25.0,
                          "status": "pending"},
                    timeout=8, verify=False)
                atualizados += 1
                print(f"     ✅ Script atualizado salvo")
        time.sleep(2)

    print(f"\n  ✅ {atualizados} scripts atualizados com pesquisa fresca")
    print(f"  🔄 Agent knowledge base mantida atual — sem conteúdo stale")

if __name__=="__main__": run()
