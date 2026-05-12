#!/usr/bin/env python3
"""Script Gen V5 - Pollinations.ai LLM primary (no auth, no rate limit, no Cloudflare)"""
import os, json, urllib.request, urllib.parse, time, sys, re

SBU = os.environ.get("SUPABASE_URL")
SBK = os.environ.get("SUPABASE_SERVICE_KEY")
GROQ_KEY = os.environ.get("GROQ_API_KEY", "")
CEREBRAS_KEY = os.environ.get("CEREBRAS_API_KEY", "")

# User-Agent para evitar bloqueio Cloudflare
UA = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0 Safari/537.36"

def call_pollinations(prompt, model="openai-large"):
    """Pollinations.ai - 100% gratis, ilimitado, sem auth"""
    try:
        # POST endpoint
        url = "https://text.pollinations.ai/"
        body = json.dumps({
            "messages": [{"role":"user","content":prompt}],
            "model": model,  # openai-large=gpt-4o, openai=gpt-4o-mini, mistral, llama
            "private": True,
            "seed": int(time.time())
        }).encode()
        req = urllib.request.Request(url, data=body, method="POST",
            headers={"Content-Type":"application/json", "User-Agent":UA, "Accept":"text/plain"})
        with urllib.request.urlopen(req, timeout=120) as r:
            text = r.read().decode()
            if len(text) > 200 and not text.startswith("{"):
                return text, "pollinations", model
            # Tentar JSON
            try:
                d = json.loads(text)
                t = d.get("choices",[{}])[0].get("message",{}).get("content","") or d.get("content","")
                if len(t) > 200:
                    return t, "pollinations", model
            except: pass
    except Exception as e:
        print(f"    Pollinations error: {str(e)[:200]}")
    return None, None, None

def call_pollinations_get(prompt, model="openai"):
    """Pollinations GET endpoint - mais simples"""
    try:
        # GET com prompt na URL
        p_enc = urllib.parse.quote(prompt[:6000])  # limite URL
        url = f"https://text.pollinations.ai/{p_enc}?model={model}&private=true"
        req = urllib.request.Request(url, headers={"User-Agent":UA})
        with urllib.request.urlopen(req, timeout=120) as r:
            text = r.read().decode()
            if len(text) > 200:
                return text, "pollinations_get", model
    except Exception as e:
        print(f"    PollinationsGET error: {str(e)[:200]}")
    return None, None, None

def call_groq(prompt):
    if not GROQ_KEY: return None, None, None
    try:
        req = urllib.request.Request(
            "https://api.groq.com/openai/v1/chat/completions",
            data=json.dumps({
                "model": "llama-3.3-70b-versatile",
                "messages": [{"role":"user","content":prompt}],
                "max_tokens": 3500,
                "temperature": 0.75
            }).encode(),
            method="POST",
            headers={
                "Authorization": f"Bearer {GROQ_KEY}",
                "Content-Type": "application/json",
                "User-Agent": UA,
                "Accept": "application/json"
            }
        )
        with urllib.request.urlopen(req, timeout=90) as r:
            d = json.loads(r.read().decode())
            text = d["choices"][0]["message"]["content"]
            if len(text) > 200:
                return text, "groq", "llama-3.3-70b-versatile"
    except urllib.error.HTTPError as e:
        print(f"    Groq HTTP {e.code}: {e.read().decode()[:200]}")
    except Exception as e:
        print(f"    Groq err: {e}")
    return None, None, None

def call_cerebras(prompt):
    if not CEREBRAS_KEY: return None, None, None
    try:
        req = urllib.request.Request(
            "https://api.cerebras.ai/v1/chat/completions",
            data=json.dumps({
                "model": "llama-3.3-70b",
                "messages": [{"role":"user","content":prompt}],
                "max_tokens": 3500,
                "temperature": 0.75
            }).encode(),
            method="POST",
            headers={
                "Authorization": f"Bearer {CEREBRAS_KEY}",
                "Content-Type": "application/json",
                "User-Agent": UA
            }
        )
        with urllib.request.urlopen(req, timeout=90) as r:
            d = json.loads(r.read().decode())
            text = d["choices"][0]["message"]["content"]
            if len(text) > 200:
                return text, "cerebras", "llama-3.3-70b"
    except Exception as e:
        print(f"    Cerebras err: {e}")
    return None, None, None

def call_llm_chain(prompt):
    """Tenta cada LLM na ordem ate um funcionar"""
    # Ordem: Pollinations (sem auth, ilimitado) -> Groq -> Cerebras
    for fn, name in [
        (call_pollinations, "pollinations_post"),
        (call_pollinations_get, "pollinations_get"),
        (call_groq, "groq"),
        (call_cerebras, "cerebras"),
    ]:
        print(f"    Tentando {name}...")
        text, provider, model = fn(prompt) if fn != call_pollinations_get else fn(prompt, "openai")
        if text and len(text) > 200:
            print(f"    ✓ {provider} respondeu ({len(text)} chars)")
            return text, provider, model
    return None, None, None

def sb_req(method, path, body=None, params=None):
    url = f"{SBU}/rest/v1{path}"
    if params: url += "?" + urllib.parse.urlencode(params)
    headers = {"apikey":SBK, "Authorization":f"Bearer {SBK}",
               "Content-Type":"application/json", "Prefer":"return=representation"}
    data = json.dumps(body).encode() if body else None
    req = urllib.request.Request(url, data=data, method=method, headers=headers)
    try:
        with urllib.request.urlopen(req, timeout=30) as r:
            t = r.read().decode()
            return json.loads(t) if t else None
    except urllib.error.HTTPError as e:
        print(f"  SB HTTP {e.code}: {e.read().decode()[:200]}")
        return None
    except Exception as e:
        print(f"  SB ERR: {e}")
        return None

def carregar_memoria():
    padroes = sb_req("GET", "/padroes_virais", params={"select":"chave,conteudo","ativo":"eq.true"}) or []
    regras = sb_req("GET", "/regras_eternas", params={"select":"codigo,regra,categoria","prioridade":"eq.10"}) or []
    return padroes, regras

def build_prompt(tema, formato, emocao, personagem, regras):
    is_long = "15" in formato or "long" in formato.lower()
    duracao = "12-15 minutos (1000 palavras)" if is_long else "55-60 segundos (130 palavras max)"
    regras_str = "\n".join([f"- {r['codigo']}: {r['regra'][:160]}" for r in regras[:8]])
    
    estrutura = ("""
ESTRUTURA 4 ATOS (15min) ENGENHARIA DE ATENCAO:
ATO 1 (0-3min) FERIDA: super hook + amplificacao + promessa+mapa
ATO 2 (3-8min) ANATOMIA: mecanismo + caso real + MID-VIDEO HOOK em 7-8min
ATO 3 (8-13min) TRANSFORMACAO: virada + framework 3-5 passos + segundo caso
ATO 4 (13-15min) LEGADO: sintese + identidade coletiva + teaser

RETENTION HOOKS a cada 90s
""" if is_long else """
ESTRUTURA 7 ATOS (60s):
ATO 1 (0-5s) HOOK: cena especifica
ATO 2 (5-15s) AMPLIFICACAO: dado real
ATO 3 (15-25s) CASO REAL: nome+idade+profissao
ATO 4 (25-35s) VIRADA CIENTIFICA
ATO 5 (35-45s) CUSTO REAL
ATO 6 (45-55s) CAMINHO: insight
ATO 7 (55-60s) ANCORAGEM
""")
    return f"""Voce e o cerebro psicologia.doc - canal BR mirando 1M subs.
Referencia: Psych2Go 28M, Therapy in a Nutshell 68% retencao.

TEMA: {tema}
FORMATO: {formato} | {duracao}
EMOCAO: {emocao}
PERSONAGEM: {personagem}

REGRAS ABSOLUTAS:
{regras_str}

- Audio sempre PT-BR
- Nome BR (Marina/Lucas/Sofia/Rafael) em todos idiomas
- Situacao UNIVERSAL
- Dado com fonte real (universidade+ano)
- Hook = cena especifica + sensacao fisica
- Zero pedido de like
- Zero julgamento
{estrutura}
GERE EXATAMENTE NESTE FORMATO:
TITULO: titulo viral PT-BR
DESCRICAO_YT: 150 palavras com keywords
TAGS: 15 tags separadas por virgula
SCRIPT:
roteiro completo narrado pt-BR
CENAS_VISUAIS:
descricao por cena para Flux ZERO TEXTO

GERE AGORA:"""

def parse(texto):
    titulo, desc, tags, script, cenas, mode = "", "", "", "", "", ""
    for line in texto.split("\n"):
        s = line.strip()
        if re.match(r"^T[IÍ]TULO:", s, re.I):
            titulo = re.sub(r"^T[IÍ]TULO:\s*", "", s, flags=re.I).strip()
        elif re.match(r"^DESCRI[CÇ]AO_YT:", s, re.I):
            desc = re.sub(r"^DESCRI[CÇ]AO_YT:\s*", "", s, flags=re.I).strip()
            mode = "desc"
        elif re.match(r"^TAGS:", s, re.I):
            tags = re.sub(r"^TAGS:\s*", "", s, flags=re.I).strip()
            mode = ""
        elif re.match(r"^SCRIPT:", s, re.I):
            mode = "script"
        elif re.match(r"^CENAS", s, re.I):
            mode = "cenas"
        else:
            if mode=="desc": desc += " " + line.strip()
            elif mode=="script": script += line + "\n"
            elif mode=="cenas": cenas += line + "\n"
    return {
        "titulo": titulo or "Video psicologia.doc",
        "descricao": desc.strip(),
        "tags": [t.strip() for t in tags.split(",") if t.strip()][:15],
        "script": script.strip(),
        "cenas": cenas.strip()
    }

def main():
    print("=== Script Gen V5 - Pollinations.ai Primary + TOP 10 ===\n")
    
    padroes, regras = carregar_memoria()
    print(f"Memoria: {len(padroes)} padroes, {len(regras)} regras absolutas\n")
    
    # TOP 10 explicito
    print("Buscando TOP 10 prioritarios (IDs 682-691)...")
    videos = sb_req("GET", "/content_pipeline",
        params={"select":"id,title,metadata", "id":"in.(682,683,684,685,686,687,688,689,690,691)",
                "status":"eq.pending_generation"})
    
    if not videos:
        print("TOP 10 ja processados ou nao encontrados.")
        videos = sb_req("GET", "/content_pipeline",
            params={"select":"id,title,metadata", "status":"eq.pending_generation",
                    "order":"id.desc", "limit":"5"})
    
    if not videos:
        print("Fila vazia.")
        return
    
    print(f"Processando {len(videos)} videos:\n")
    sucesso = 0
    for v in videos:
        vid = v["id"]
        meta = v.get("metadata") or {}
        tema = meta.get("tema", v["title"])
        emocao = meta.get("emocao", "contemplativo")
        formato = meta.get("formato", "short_60s")
        personagem = meta.get("personagem", "Personagem brasileiro")
        
        print(f"#{vid}: {v['title'][:60]}")
        print(f"  formato={formato} | emocao={emocao}")
        
        prompt = build_prompt(tema, formato, emocao, personagem, regras)
        texto, provider, modelo = call_llm_chain(prompt)
        
        if not texto:
            print(f"  ✗ Nenhum LLM funcionou\n")
            continue
        
        p = parse(texto)
        if len(p["script"]) < 200:
            print(f"  ✗ Script curto: {len(p['script'])} chars\n")
            # Tentar usar texto cru se nao parseou
            if len(texto) > 300:
                p["script"] = texto[:3000]
                p["titulo"] = v["title"]
                print(f"  Usando texto cru: {len(p['script'])} chars")
            else:
                continue
        
        update = {
            "title": p["titulo"][:200],
            "script": p["script"],
            "status": "script_ready",
            "metadata": {
                **meta,
                "descricao_yt": p["descricao"],
                "tags_yt": p["tags"],
                "cenas_visuais": p["cenas"],
                "llm_provider": provider,
                "llm_modelo": modelo,
                "llm_custo": "$0.00",
                "stack_gratuita": True,
                "gerado_em": time.strftime("%Y-%m-%dT%H:%M:%SZ"),
                "memoria_eterna_aplicada": True
            }
        }
        
        r = sb_req("PATCH", "/content_pipeline", body=update, params={"id":f"eq.{vid}"})
        if r is not None:
            sucesso += 1
            print(f"  ✓ Script gerado: {len(p['script'])} chars, provider={provider}")
            print(f"  ✓ Titulo: {p['titulo'][:60]}")
        else:
            print(f"  ✗ Falha salvar")
        print()
        time.sleep(3)
    
    print(f"\n=== {sucesso}/{len(videos)} scripts gerados | Custo: $0.00 ===")

if __name__ == "__main__":
    main()
