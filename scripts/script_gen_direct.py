#!/usr/bin/env python3
"""Script Gen V4 - Multi-LLM gratis fallback chain + foco TOP 10"""
import os, json, urllib.request, urllib.parse, time, sys, re

SBU = os.environ.get("SUPABASE_URL")
SBK = os.environ.get("SUPABASE_SERVICE_KEY")
GROQ_KEY = os.environ.get("GROQ_API_KEY", "")
CEREBRAS_KEY = os.environ.get("CEREBRAS_API_KEY", "")
NVIDIA_KEY = os.environ.get("NVIDIA_API_KEY", "")
OPENROUTER_KEY = os.environ.get("OPENROUTER_API_KEY", "")
OPENAI_KEY = os.environ.get("OPENAI_API_KEY", "")

LLMS = []
if CEREBRAS_KEY:
    LLMS.append({"nome":"cerebras", "url":"https://api.cerebras.ai/v1/chat/completions", "key":CEREBRAS_KEY, "model":"llama-3.3-70b"})
if GROQ_KEY:
    LLMS.append({"nome":"groq", "url":"https://api.groq.com/openai/v1/chat/completions", "key":GROQ_KEY, "model":"llama-3.3-70b-versatile"})
if NVIDIA_KEY:
    LLMS.append({"nome":"nvidia", "url":"https://integrate.api.nvidia.com/v1/chat/completions", "key":NVIDIA_KEY, "model":"meta/llama-3.3-70b-instruct"})
if OPENROUTER_KEY:
    LLMS.append({"nome":"openrouter", "url":"https://openrouter.ai/api/v1/chat/completions", "key":OPENROUTER_KEY, "model":"deepseek/deepseek-r1:free"})
if OPENAI_KEY:
    LLMS.append({"nome":"openai", "url":"https://api.openai.com/v1/chat/completions", "key":OPENAI_KEY, "model":"gpt-4o-mini"})

print(f"LLMs disponiveis: {len(LLMS)}")
for l in LLMS:
    print(f"  - {l['nome']}: {l['model']}")

def sb_req(method, path, body=None, params=None):
    url = f"{SBU}/rest/v1{path}"
    if params:
        url += "?" + urllib.parse.urlencode(params)
    headers = {"apikey":SBK, "Authorization":f"Bearer {SBK}", "Content-Type":"application/json", "Prefer":"return=representation"}
    data = json.dumps(body).encode() if body else None
    req = urllib.request.Request(url, data=data, method=method, headers=headers)
    try:
        with urllib.request.urlopen(req, timeout=30) as r:
            t = r.read().decode()
            return json.loads(t) if t else None
    except urllib.error.HTTPError as e:
        print(f"  HTTP {e.code}: {e.read().decode()[:200]}")
        return None
    except Exception as e:
        print(f"  ERR: {e}")
        return None

def call_llm(prompt, max_tokens=3500):
    """Tenta cada LLM na ordem ate um funcionar"""
    for llm in LLMS:
        try:
            print(f"    Tentando {llm['nome']}...")
            req = urllib.request.Request(
                llm["url"],
                data=json.dumps({
                    "model": llm["model"],
                    "messages": [{"role":"user","content":prompt}],
                    "max_tokens": max_tokens,
                    "temperature": 0.75
                }).encode(),
                method="POST",
                headers={
                    "Authorization": f"Bearer {llm['key']}",
                    "Content-Type": "application/json"
                }
            )
            with urllib.request.urlopen(req, timeout=90) as r:
                d = json.loads(r.read().decode())
                text = d["choices"][0]["message"]["content"]
                if len(text) > 200:
                    print(f"    ✓ {llm['nome']} respondeu ({len(text)} chars)")
                    return text, llm['nome'], llm['model']
        except urllib.error.HTTPError as e:
            err = e.read().decode()[:200]
            print(f"    ✗ {llm['nome']} HTTP {e.code}: {err}")
        except Exception as e:
            print(f"    ✗ {llm['nome']} ERR: {e}")
    return None, None, None

def carregar_memoria():
    padroes = sb_req("GET", "/padroes_virais", params={"select":"chave,conteudo", "ativo":"eq.true"}) or []
    regras = sb_req("GET", "/regras_eternas", params={"select":"codigo,regra,categoria", "prioridade":"eq.10"}) or []
    return padroes, regras

def build_prompt(tema, formato, emocao, personagem, regras):
    is_long = "15" in formato or "long" in formato.lower()
    duracao = "12-15 minutos (1000 palavras)" if is_long else "55-60 segundos (130 palavras max)"
    regras_str = "\n".join([f"- {r['codigo']}: {r['regra'][:180]}" for r in regras[:10]])
    
    estrutura = ("""
ESTRUTURA 4 ATOS (15min) - ENGENHARIA DE ATENCAO:
ATO 1 (0-3min) FERIDA: super hook + amplificacao + promessa+mapa
ATO 2 (3-8min) ANATOMIA: mecanismo + caso real + MID-VIDEO HOOK em 7-8min
ATO 3 (8-13min) TRANSFORMACAO: virada + framework 3-5 passos + segundo caso
ATO 4 (13-15min) LEGADO: sintese + identidade coletiva + teaser proximo

RETENTION HOOKS a cada 90s: 45s/90s/150s/270s/360s/480s(MID)/600s/720s/840s/900s
""" if is_long else """
ESTRUTURA 7 ATOS (60s):
ATO 1 (0-5s) HOOK: cena especifica
ATO 2 (5-15s) AMPLIFICACAO: dado real com fonte
ATO 3 (15-25s) CASO REAL: nome+idade+profissao
ATO 4 (25-35s) VIRADA CIENTIFICA: mecanismo
ATO 5 (35-45s) CUSTO REAL: consequencia
ATO 6 (45-55s) CAMINHO: insight especifico
ATO 7 (55-60s) ANCORAGEM: identificacao coletiva
""")
    return f"""Voce e o cerebro autonomo psicologia.doc - canal brasileiro mirando 1M subs em 2027.
Referencia: Psych2Go (28M views), Therapy in a Nutshell (68%), Kati Morton (71%).

TEMA: {tema}
FORMATO: {formato} | {duracao}
EMOCAO: {emocao}
PERSONAGEM: {personagem}

REGRAS ABSOLUTAS MEMORIA ETERNA:
{regras_str}

ESTRATEGIA SUCESSO GLOBAL:
- Audio sempre PT-BR (default eterno)
- Nome BR (Marina/Lucas/Sofia/Rafael/Isabela/Lara) em todos os idiomas
- Situacao UNIVERSAL ressoa em qualquer cultura
- Dado cientifico com fonte real (universidade+pesquisador+ano)
- Hook = cena especifica + sensacao fisica nos primeiros 5s
- Zero pedido direto de like/inscricao
- Zero julgamento - validar antes de explicar
{estrutura}
GERE EXATAMENTE NESTE FORMATO:
TITULO: titulo viral PT-BR
DESCRICAO_YT: 150 palavras com keywords
TAGS: 15 tags separadas por virgula
SCRIPT:
roteiro completo narrado pt-BR autentico
CENAS_VISUAIS:
descricao por cena para gerar imagem Flux ZERO TEXTO

GERE AGORA - roteiro completo de producao:"""

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
    print("=== Script Gen V4 - Multi-LLM Gratis + TOP 10 ===\n")
    
    if not LLMS:
        print("ERRO: Nenhum LLM configurado")
        sys.exit(1)
    
    padroes, regras = carregar_memoria()
    print(f"Memoria: {len(padroes)} padroes, {len(regras)} regras absolutas\n")
    
    # PEGAR EXPLICITAMENTE OS TOP 10 (IDs 682-691)
    print("Buscando TOP 10 prioritarios...")
    videos = sb_req("GET", "/content_pipeline",
        params={"select":"id,title,metadata", "id":"in.(682,683,684,685,686,687,688,689,690,691)",
                "status":"eq.pending_generation"})
    
    if not videos or len(videos) == 0:
        print("TOP 10 ja processados ou nao encontrados. Tentando fila normal...")
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
        texto, provider, modelo = call_llm(prompt)
        
        if not texto:
            print(f"  ✗ Nenhum LLM disponivel\n")
            continue
        
        p = parse(texto)
        if len(p["script"]) < 200:
            print(f"  ✗ Script curto: {len(p['script'])} chars\n")
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
            print(f"  ✓ Script gerado: {len(p['script'])} chars, {len(p['tags'])} tags")
            print(f"  ✓ Titulo: {p['titulo'][:60]}")
        else:
            print(f"  ✗ Falha salvar")
        print()
        
        time.sleep(2)
    
    print(f"\n=== {sucesso}/{len(videos)} scripts gerados | Custo: $0.00 ===")

if __name__ == "__main__":
    main()
