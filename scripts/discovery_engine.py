#!/usr/bin/env python3
"""
discovery_engine.py — Motor Autônomo de Expansão do Cérebro Quântico
Descobre APIs em tempo real de 8 diretórios e auto-popula o Supabase

Uso:
  python3 scripts/discovery_engine.py --all          # todas categorias
  python3 scripts/discovery_engine.py --cat Health   # categoria específica
  python3 scripts/discovery_engine.py --query tts    # busca por termo
  python3 scripts/discovery_engine.py --rapidapi     # varre RapidAPI free
  python3 scripts/discovery_engine.py --hf           # top models HuggingFace

Meta:
  Roda via GitHub Actions a cada 24h → brain sempre atualizado
"""

import requests, json, os, time, sys
from typing import Optional

SB_URL = os.getenv("SUPABASE_URL", "https://tpjvalzwkqwttvmszvie.supabase.co")
SB_KEY = os.getenv("SUPABASE_SERVICE_ROLE_KEY", "")

HEADERS_SB = lambda: {
    "apikey": SB_KEY,
    "Authorization": f"Bearer {SB_KEY}",
    "Content-Type": "application/json",
    "Prefer": "resolution=ignore-duplicates"
}

# ══════════════════════════════════════════════════════════════════
# CATÁLOGO COMPLETO: 51 categorias do public-apis
# ══════════════════════════════════════════════════════════════════
ALL_CATEGORIES = [
    "Animals","Anime","Anti-Malware","Art & Design","Authentication & Authorization",
    "Blockchain","Books","Business","Calendar","Cloud Storage & File Sharing",
    "Continuous Integration","Cryptocurrency","Currency Exchange","Data Validation",
    "Development","Dictionaries","Documents & Productivity","Email","Entertainment",
    "Environment","Events","Finance","Food & Drink","Games & Comics","Geocoding",
    "Government","Health","Jobs","Machine Learning","Music","News","Open Data",
    "Open Source Projects","Patent","Personality","Phone","Photography","Programming",
    "Science & Math","Security","Shopping","Social","Sports & Fitness","Test Data",
    "Text Analysis","Tracking","Transportation","URL Shorteners","Vehicle","Video","Weather"
]

# ══════════════════════════════════════════════════════════════════
# FONTE 1: public-apis.org (1400+ APIs)
# ══════════════════════════════════════════════════════════════════
def discover_publicapis(category: str = None, auth_filter: str = "null") -> list:
    """Busca APIs do diretório public-apis"""
    url = "https://api.publicapis.org/entries"
    params = {"https": "true"}
    if category: params["category"] = category
    if auth_filter: params["auth"] = auth_filter
    
    try:
        r = requests.get(url, params=params, timeout=15)
        if r.status_code == 200:
            entries = r.json().get("entries", [])
            # Converter para formato api_brain
            apis = []
            for e in entries:
                apis.append({
                    "name":       e.get("API", "")[:100],
                    "category":   e.get("Category", "Unknown")[:80],
                    "endpoint":   e.get("Link", "")[:500],
                    "auth_type":  "none" if e.get("Auth") == "" else e.get("Auth","apiKey"),
                    "description":e.get("Description","")[:500],
                    "relevance":  2,
                    "source":     "public-apis",
                    "tags":       ["no-auth"] if e.get("Auth") == "" else []
                })
            return apis
    except Exception as ex:
        print(f"  ⚠️  public-apis erro: {ex}")
    return []

# ══════════════════════════════════════════════════════════════════
# FONTE 2: publicapis.dev (1400+ APIs com JSON limpo)
# ══════════════════════════════════════════════════════════════════
def discover_publicapis_dev(category: str = None) -> list:
    """Busca APIs de publicapis.dev"""
    base = "https://publicapis.dev"
    url = f"{base}/category/{category.lower().replace(' ', '-')}" if category else f"{base}/all"
    try:
        r = requests.get(url, timeout=15)
        if r.status_code == 200:
            data = r.json()
            entries = data.get("apis", data) if isinstance(data, dict) else data
            apis = []
            for e in entries if isinstance(entries, list) else []:
                if isinstance(e, dict):
                    apis.append({
                        "name":       str(e.get("name",""))[:100],
                        "category":   str(e.get("category","Unknown"))[:80],
                        "endpoint":   str(e.get("url", e.get("link","")))[:500],
                        "auth_type":  "none" if not e.get("auth") else "apiKey",
                        "description":str(e.get("description",""))[:500],
                        "relevance":  2,
                        "source":     "publicapis.dev",
                        "tags":       ["no-auth"] if not e.get("auth") else []
                    })
            return apis
    except Exception as ex:
        print(f"  ⚠️  publicapis.dev erro: {ex}")
    return []

# ══════════════════════════════════════════════════════════════════
# FONTE 3: public-api-lists (GitHub JSON) — 1000+ APIs
# ══════════════════════════════════════════════════════════════════
def discover_public_api_lists() -> list:
    """Busca APIs do public-api-lists GitHub"""
    url = "https://public-api-lists.github.io/public-api-lists/apis.json"
    try:
        r = requests.get(url, timeout=20)
        if r.status_code == 200:
            data = r.json()
            entries = data.get("apis", data.get("entries", []))
            apis = []
            for e in entries if isinstance(entries, list) else []:
                if isinstance(e, dict) and e.get("name"):
                    apis.append({
                        "name":       str(e.get("name",""))[:100],
                        "category":   str(e.get("category","Unknown"))[:80],
                        "endpoint":   str(e.get("url",""))[:500],
                        "auth_type":  "none" if e.get("free") else "apiKey",
                        "description":str(e.get("description",""))[:500],
                        "relevance":  2,
                        "source":     "public-api-lists",
                        "tags":       ["no-auth"] if e.get("free") else []
                    })
            return apis
    except Exception as ex:
        print(f"  ⚠️  public-api-lists erro: {ex}")
    return []

# ══════════════════════════════════════════════════════════════════
# FONTE 4: HuggingFace (500K+ modelos) — top por downloads
# ══════════════════════════════════════════════════════════════════
def discover_huggingface(pipeline_tag: str = None, limit: int = 50) -> list:
    """Busca top modelos HuggingFace por categoria"""
    url = "https://huggingface.co/api/models"
    params = {"sort": "downloads", "direction": -1, "limit": limit}
    if pipeline_tag: params["pipeline_tag"] = pipeline_tag
    
    try:
        r = requests.get(url, params=params, timeout=15)
        if r.status_code == 200:
            models = r.json()
            apis = []
            for m in models:
                model_id = m.get("modelId","")
                tags = m.get("tags",[])
                pipeline = m.get("pipeline_tag","")
                apis.append({
                    "name":       model_id[:100],
                    "category":   "Machine Learning",
                    "subcategory":pipeline or "Model",
                    "endpoint":   f"https://api-inference.huggingface.co/models/{model_id}",
                    "auth_type":  "Bearer",
                    "auth_notes": "token grátis huggingface.co",
                    "description":f"HuggingFace: {model_id} | {pipeline} | {m.get('downloads',0):,} downloads",
                    "relevance":  3 if m.get("downloads",0) > 100000 else 2,
                    "source":     "huggingface",
                    "tags":       (tags[:5] if tags else []) + ["hf"]
                })
            return apis
    except Exception as ex:
        print(f"  ⚠️  HuggingFace erro: {ex}")
    return []

# ══════════════════════════════════════════════════════════════════
# FONTE 5: APIs.guru (2000+ OpenAPI specs)
# ══════════════════════════════════════════════════════════════════
def discover_apis_guru(limit: int = 200) -> list:
    """Busca providers do APIs.guru"""
    try:
        r = requests.get("https://api.apis.guru/v2/list.json", timeout=20)
        if r.status_code == 200:
            providers = r.json()
            apis = []
            for provider, data in list(providers.items())[:limit]:
                for version, spec in data.get("versions",{}).items():
                    info = spec.get("info",{})
                    apis.append({
                        "name":       info.get("title", provider)[:100],
                        "category":   "Development",
                        "subcategory":"OpenAPI",
                        "endpoint":   spec.get("swaggerUrl","")[:500],
                        "auth_type":  "apiKey",
                        "description":info.get("description","")[:300] or f"OpenAPI spec: {provider}",
                        "relevance":  1,
                        "source":     "apis-guru",
                        "tags":       ["openapi", provider.split(".")[0]]
                    })
                    break  # só 1 versão por provider
            return apis
    except Exception as ex:
        print(f"  ⚠️  APIs.guru erro: {ex}")
    return []

# ══════════════════════════════════════════════════════════════════
# INSERIR NO SUPABASE
# ══════════════════════════════════════════════════════════════════
def insert_to_brain(apis: list, verbose: bool = False) -> dict:
    """Insere APIs no banco — ignora duplicatas pelo nome"""
    if not SB_KEY:
        print("⚠️  SUPABASE_SERVICE_ROLE_KEY não definida")
        return {"inserted":0, "total":len(apis)}
    
    inserted = 0
    errors = 0
    batch_size = 50
    
    for i in range(0, len(apis), batch_size):
        batch = apis[i:i+batch_size]
        # Filtrar campos inválidos
        clean = []
        for a in batch:
            if a.get("name") and a.get("endpoint"):
                clean.append({k:v for k,v in a.items() if v is not None})
        
        if not clean: continue
        
        r = requests.post(
            f"{SB_URL}/rest/v1/api_brain",
            headers={**HEADERS_SB(), "Prefer":"return=minimal,resolution=ignore-duplicates"},
            json=clean,
            timeout=30
        )
        if r.status_code in (200,201):
            inserted += len(clean)
            if verbose: print(f"  ✅ Inseridos {inserted} até agora...")
        else:
            errors += 1
            if verbose: print(f"  ❌ Erro batch {i//batch_size}: {r.status_code}")
        
        time.sleep(0.5)  # rate limiting
    
    return {"inserted": inserted, "errors": errors, "total": len(apis)}

# ══════════════════════════════════════════════════════════════════
# MOTOR PRINCIPAL
# ══════════════════════════════════════════════════════════════════
def run(mode: str = "all", category: str = None, query: str = None):
    print(f"\n🧠 QUANTUM BRAIN DISCOVERY ENGINE")
    print(f"   Modo: {mode} | Cat: {category} | Query: {query}")
    print("=" * 60)
    
    all_apis = []
    
    if mode in ("all", "publicapis"):
        cats = [category] if category else ALL_CATEGORIES[:10]  # 10 por vez
        for cat in cats:
            print(f"  📡 public-apis: {cat}...")
            apis = discover_publicapis(cat, auth_filter="null")
            all_apis.extend(apis)
            time.sleep(1)
    
    if mode in ("all", "hf", "huggingface"):
        hf_tasks = ["text-generation","text-classification","text-to-speech",
                    "automatic-speech-recognition","image-to-image","text-to-image",
                    "translation","feature-extraction","fill-mask"]
        for task in hf_tasks[:3]:  # 3 tasks por run para não timeout
            print(f"  🤗 HuggingFace: {task}...")
            apis = discover_huggingface(pipeline_tag=task, limit=20)
            all_apis.extend(apis)
            time.sleep(1)
    
    if mode in ("all", "apis_guru"):
        print(f"  📋 APIs.guru...")
        apis = discover_apis_guru(limit=100)
        all_apis.extend(apis)
    
    print(f"\n  Descobertas: {len(all_apis)} APIs")
    print(f"  Inserindo no Supabase...")
    
    result = insert_to_brain(all_apis, verbose=True)
    print(f"\n✅ Resultado: {result}")
    
    # Contar total atual
    r = requests.get(f"{SB_URL}/rest/v1/api_brain?select=count",
        headers=HEADERS_SB(), timeout=10)
    print(f"📊 Total no banco: {r.headers.get('content-range','?')}")

if __name__ == "__main__":
    import argparse
    p = argparse.ArgumentParser()
    p.add_argument("--all", action="store_true")
    p.add_argument("--cat", type=str)
    p.add_argument("--hf", action="store_true")
    p.add_argument("--guru", action="store_true")
    p.add_argument("--query", type=str)
    args = p.parse_args()
    
    if args.hf:      run("hf")
    elif args.guru:  run("apis_guru")
    elif args.cat:   run("publicapis", category=args.cat)
    else:            run("all")
