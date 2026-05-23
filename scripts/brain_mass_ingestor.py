#!/usr/bin/env python3
"""
brain_mass_ingestor.py
Entra em cada link de API conhecido, extrai metadados e insere no banco.
Meta: 1000 APIs por execucao. Roda a cada hora via GitHub Actions.
Fontes: APIs.guru + Public-APIs + HuggingFace Hub + GitHub + Gov APIs
"""
import os, json, requests, time, hashlib, re
from datetime import datetime

SB  = os.getenv("SUPABASE_URL", "https://tpjvalzwkqwttvmszvie.supabase.co")
SK  = os.getenv("SUPABASE_SERVICE_KEY", "")
GK  = os.getenv("GROQ_API_KEY", "")
HF  = os.getenv("HF_TOKEN", "")
GH  = os.getenv("GH_PAT", "")

def sbh():
    return {"apikey":SK,"Authorization":f"Bearer {SK}","Content-Type":"application/json"}

def total_apis():
    r = requests.get(f"{SB}/rest/v1/api_brain?select=count",
                     headers={**sbh(),"Prefer":"count=exact"}, timeout=5)
    return int(r.headers.get("Content-Range","0/0").split("/")[-1])

def inserir_batch(apis):
    if not apis or not SK: return 0
    ok = 0
    for i in range(0, len(apis), 50):
        batch = apis[i:i+50]
        r = requests.post(f"{SB}/rest/v1/api_brain",
            headers={**sbh(),"Prefer":"resolution=ignore-duplicates"},
            json=batch, timeout=30)
        if r.status_code in (200,201,204):
            ok += len(batch)
        time.sleep(0.3)
    return ok

# ── FONTE 1: APIs.guru — 2529 APIs com URLs reais ──────────────
def ingerir_apis_guru():
    print("  [APIs.guru] Buscando...")
    r = requests.get("https://api.apis.guru/v2/list.json", timeout=45)
    if r.status_code != 200: return []
    data = r.json()
    apis = []
    for api_name, api_info in data.items():
        try:
            versions = api_info.get("versions", {})
            categories = api_info.get("categories", ["general"])
            for ver_key, vdata in versions.items():
                info = vdata.get("info", {})
                title = (info.get("title","") or api_name)[:100]
                desc = (info.get("description","") or "")[:300].replace("\n"," ")
                url = (vdata.get("swaggerUrl","") or
                       vdata.get("swaggerYamlUrl","") or
                       info.get("x-origin",[{}])[0].get("url","") if info.get("x-origin") else "")[:500]
                cat = categories[0] if categories else "general"
                tags_raw = categories[:5] + ["apis-guru","auto"]
                apis.append({
                    "name": title, "category": cat[:50],
                    "subcategory": api_name.split(".")[0][:50],
                    "endpoint": url or f"https://{api_name}",
                    "auth_type": "apiKey",
                    "description": desc or f"API {title} via APIs.guru",
                    "relevance": 2, "use_case": f"Descoberta APIs.guru — {cat}",
                    "source": "apis-guru",
                    "tags": [t.lower()[:30].replace(" ","-") for t in tags_raw]
                })
                break
        except: pass
    print(f"  [APIs.guru] {len(apis)} APIs processadas")
    return apis

# ── FONTE 2: Public-APIs GitHub — 1494 APIs gratuitas ──────────
def ingerir_public_apis():
    print("  [Public-APIs] Buscando...")
    r = requests.get("https://raw.githubusercontent.com/public-apis/public-apis/master/README.md", timeout=30)
    if r.status_code != 200: return []
    apis = []
    current_cat = "general"
    for line in r.text.split("\n"):
        if line.startswith("### "):
            current_cat = line.replace("### ","").strip()
        elif line.startswith("| [") and "http" in line:
            try:
                parts = line.split("|")
                if len(parts) >= 5:
                    name_part = parts[1].strip()
                    name = name_part[name_part.find("[")+1:name_part.find("]")]
                    desc = parts[2].strip()[:200]
                    auth_raw = parts[3].strip().lower()
                    url = ""
                    if "(" in name_part and ")" in name_part:
                        url = name_part[name_part.find("(")+1:name_part.find(")")]
                    auth_type = "none" if auth_raw in ["","no","unknown"] else ("apiKey" if "apikey" in auth_raw or "key" in auth_raw else "OAuth")
                    apis.append({
                        "name": name[:100], "category": current_cat[:50],
                        "subcategory": current_cat[:50],
                        "endpoint": url[:500],
                        "auth_type": auth_type,
                        "description": desc or f"API gratuita: {name}",
                        "relevance": 3 if auth_type == "none" else 2,
                        "use_case": f"API publica — {current_cat}",
                        "source": "public-apis",
                        "tags": ["public-api","free","auto",current_cat.lower()[:20].replace(" ","-")]
                    })
            except: pass
    print(f"  [Public-APIs] {len(apis)} APIs processadas")
    return apis

# ── FONTE 3: HuggingFace Hub — 500K modelos por categoria ──────
HF_TASKS = [
    "text-generation","text2text-generation","text-classification",
    "token-classification","question-answering","summarization",
    "translation","sentence-similarity","feature-extraction",
    "text-to-speech","automatic-speech-recognition",
    "text-to-image","image-to-image","image-classification",
    "text-to-video","text-to-audio","audio-classification",
    "zero-shot-classification","fill-mask","conversational"
]

def ingerir_huggingface(limit_per_task=50):
    print("  [HuggingFace] Buscando modelos por tarefa...")
    headers = {"Authorization": f"Bearer {HF}"} if HF else {}
    apis = []
    for task in HF_TASKS:
        try:
            r = requests.get(
                f"https://huggingface.co/api/models?pipeline_tag={task}&limit={limit_per_task}&sort=downloads&direction=-1",
                headers=headers, timeout=20)
            if r.status_code != 200: continue
            models = r.json()
            for m in models:
                model_id = m.get("id","")
                if not model_id: continue
                downloads = m.get("downloads",0)
                likes = m.get("likes",0)
                name = model_id.split("/")[-1][:100]
                endpoint = f"https://api-inference.huggingface.co/models/{model_id}"
                desc = f"HF {task.replace('-',' ')} | {downloads:,} downloads | {likes} likes"
                relevance = 3 if downloads > 100000 else 2 if downloads > 10000 else 1
                apis.append({
                    "name": f"HF {name}"[:100],
                    "category": "Machine Learning",
                    "subcategory": task.replace("-"," ").title()[:50],
                    "endpoint": endpoint,
                    "auth_type": "Bearer",
                    "description": desc[:300],
                    "relevance": relevance,
                    "use_case": f"HuggingFace {task} — {model_id}",
                    "source": "huggingface",
                    "tags": ["huggingface","hf",task[:20],"auto","ml"]
                })
            time.sleep(0.5)
        except Exception as e:
            print(f"    [{task}] err: {e}")
    print(f"  [HuggingFace] {len(apis)} modelos processados")
    return apis

# ── FONTE 4: GitHub Topics — APIs por linguagem/framework ──────
GH_TOPICS = [
    "rest-api","graphql-api","open-api","api","sdk","python-api",
    "nodejs-api","nlp","machine-learning","deep-learning",
    "speech-recognition","text-to-speech","image-generation",
    "psychology","mental-health","neuroscience","healthcare-api",
    "music-api","audio-api","video-api","podcast-api","streaming-api",
    "finance-api","news-api","social-media-api","data-api","ai-api"
]

def ingerir_github_topics():
    print("  [GitHub Topics] Buscando repos de API...")
    if not GH: return []
    headers = {"Authorization": f"token {GH}", "Accept": "application/vnd.github.v3+json"}
    apis = []
    for topic in GH_TOPICS[:15]:  # Limitar para nao esgotar rate limit
        try:
            r = requests.get(
                f"https://api.github.com/search/repositories?q=topic:{topic}+is:public&sort=stars&per_page=20",
                headers=headers, timeout=20)
            if r.status_code != 200: continue
            repos = r.json().get("items", [])
            for repo in repos:
                name = repo.get("name","")
                desc = (repo.get("description","") or "")[:300]
                url = repo.get("homepage","") or repo.get("html_url","")
                stars = repo.get("stargazers_count",0)
                lang = repo.get("language","") or "general"
                apis.append({
                    "name": name[:100],
                    "category": "Development",
                    "subcategory": topic.replace("-"," ").title()[:50],
                    "endpoint": url[:500] or f"https://github.com/{repo.get('full_name','')}",
                    "auth_type": "apiKey",
                    "description": desc or f"GitHub {topic}: {name}",
                    "relevance": 3 if stars > 1000 else 2 if stars > 100 else 1,
                    "use_case": f"GitHub topic:{topic} {stars} stars",
                    "source": "github-topics",
                    "tags": ["github",topic[:20],"auto","open-source"]
                })
            time.sleep(1)  # Respeitar rate limit GitHub
        except: pass
    print(f"  [GitHub Topics] {len(apis)} repos processados")
    return apis

# ── FONTE 5: Groq IA — gerar APIs por categoria ────────────────
CATEGORIAS_IA = [
    "Audio Processing","Video Analysis","Natural Language Processing",
    "Computer Vision","Speech Recognition","Emotion Detection",
    "Mental Health Tech","Neuroscience Data","Psychology Research",
    "Music Generation","Podcast Tools","Newsletter Platforms",
    "Content Distribution","SEO Tools","Analytics Platforms",
    "Social Media Management","Email Marketing","SMS Marketing",
    "Payment Processing","Subscription Management","Affiliate Marketing",
    "E-commerce","Print on Demand","Digital Publishing",
    "Video Hosting","Podcast Hosting","Music Streaming",
    "Book Publishing","Course Platforms","Community Building"
]

def gerar_apis_groq(categoria, n=30):
    if not GK: return []
    prompt = (
        f"Liste {n} APIs publicas reais e verificaveis na categoria: {categoria}. "
        "Para cada uma inclua: nome exato, URL do endpoint principal, "
        "tipo de auth (none/apiKey/OAuth/Bearer), descricao curta em ingles. "
        "Formato JSON array: "
        '[{"name":"...","endpoint":"https://...","auth_type":"...","desc":"..."}]. '
        "Apenas JSON valido, sem markdown."
    )
    try:
        r = requests.post("https://api.groq.com/openai/v1/chat/completions",
            headers={"Authorization":f"Bearer {GK}","Content-Type":"application/json"},
            json={"model":"llama-3.3-70b-versatile",
                  "messages":[{"role":"user","content":prompt}],
                  "max_tokens":2000,
                  "response_format":{"type":"json_object"}},
            timeout=45)
        if r.status_code != 200: return []
        raw = r.json()["choices"][0]["message"]["content"]
        data = json.loads(raw)
        items = data if isinstance(data, list) else data.get("apis", data.get("list", []))
        apis = []
        for item in items:
            if not isinstance(item, dict): continue
            apis.append({
                "name": str(item.get("name","?"))[:100],
                "category": categoria[:50],
                "subcategory": categoria[:50],
                "endpoint": str(item.get("endpoint",""))[:500],
                "auth_type": str(item.get("auth_type","apiKey")),
                "description": str(item.get("desc",""))[:300],
                "relevance": 2,
                "use_case": f"Gerada por IA — {categoria}",
                "source": "ia-groq",
                "tags": ["groq-generated","ai","auto",categoria.lower()[:20].replace(" ","-")]
            })
        return apis
    except: return []

# ═══════════════════════════════════════════════════════════════
# MOTOR PRINCIPAL — roda a cada hora
# ═══════════════════════════════════════════════════════════════
def run():
    inicio = datetime.now()
    total_antes = total_apis()
    print(f"BRAIN MASS INGESTOR — {inicio:%Y-%m-%d %H:%M}")
    print(f"APIs atuais: {total_antes} | Meta: 40.000 | Gap: {40000-total_antes}")
    print("="*55)

    inseridas_total = 0

    # RODADA 1: APIs.guru (todas as 2529 de uma vez se ainda nao estao)
    if total_antes < 5000:
        print("\n[1/5] Ingerindo APIs.guru...")
        apis = ingerir_apis_guru()
        ok = inserir_batch(apis)
        inseridas_total += ok
        print(f"  +{ok} inseridas")

    # RODADA 2: Public-APIs
    if total_antes < 5000:
        print("\n[2/5] Ingerindo Public-APIs...")
        apis = ingerir_public_apis()
        ok = inserir_batch(apis)
        inseridas_total += ok
        print(f"  +{ok} inseridas")

    # RODADA 3: HuggingFace Hub — 50 modelos por tarefa (19 tarefas = ~950)
    print("\n[3/5] Ingerindo HuggingFace Hub...")
    apis = ingerir_huggingface(limit_per_task=50)
    ok = inserir_batch(apis)
    inseridas_total += ok
    print(f"  +{ok} inseridas")

    # RODADA 4: GitHub Topics
    print("\n[4/5] Ingerindo GitHub Topics...")
    apis = ingerir_github_topics()
    ok = inserir_batch(apis)
    inseridas_total += ok
    print(f"  +{ok} inseridas")

    # RODADA 5: Groq IA — 3 categorias por hora, 30 APIs cada = +90/hora
    print("\n[5/5] Gerando APIs com Groq IA...")
    import random
    cats = random.sample(CATEGORIAS_IA, min(3, len(CATEGORIAS_IA)))
    for cat in cats:
        apis = gerar_apis_groq(cat, 30)
        ok = inserir_batch(apis)
        inseridas_total += ok
        print(f"  [{cat}] +{ok} inseridas")
        time.sleep(2)

    total_depois = total_apis()
    duracao = (datetime.now() - inicio).seconds
    print(f"\n{'='*55}")
    print(f"RESULTADO: +{total_depois - total_antes} novas APIs")
    print(f"Total agora: {total_depois} | Meta: 40.000")
    print(f"Restante: {40000 - total_depois} | Duracao: {duracao}s")
    print(f"Previsao 40K: {max(0, 40000-total_depois) // max(1,total_depois-total_antes)} horas")
    if total_depois >= 40000:
        print("META ATINGIDA!")

if __name__ == "__main__":
    run()
