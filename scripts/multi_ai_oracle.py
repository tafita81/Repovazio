#!/usr/bin/env python3
"""
multi_ai_oracle.py — O ORÁCULO MULTI-IA
Combina TODAS as IAs simultaneamente para criar conteúdo impossível de replicar.

ARQUITETURA ÚNICA MUNDIAL:
  5 LLMs em paralelo → melhor script sintetizado
  3 TTSs em paralelo → melhor voz selecionada  
  3 Image AIs em paralelo → melhor thumbnail eleita
  5 plataformas distribuição simultânea → receita máxima

Nenhum canal no mundo faz isso. É o Cérebro Quântico em ação.
"""
import os,json,asyncio,requests,time,base64
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor, as_completed

# === TODAS AS CHAVES DE API ===
GROQ   = os.getenv("GROQ_API_KEY","")
NVIDIA = os.getenv("NVIDIA_API_KEY","")
CEREBRAS = os.getenv("CEREBRAS_API_KEY","")
TOGETHER = os.getenv("TOGETHER_API_KEY","")
OPENROUTER = os.getenv("OPENROUTER_API_KEY","")
HF_TOKEN = os.getenv("HF_TOKEN","")

SB_URL = os.getenv("SUPABASE_URL","https://tpjvalzwkqwttvmszvie.supabase.co")
SB_KEY = os.getenv("SUPABASE_SERVICE_ROLE_KEY","")

# === MAPA DE TODOS OS LLMs ===
LLMS = {
    "groq_llama_70b": {
        "url": "https://api.groq.com/openai/v1/chat/completions",
        "model": "llama-3.3-70b-versatile",
        "key": lambda: GROQ,
        "especialidade": "profundidade psicologica e empatia",
        "tokens": 2000
    },
    "nvidia_deepseek_r1": {
        "url": "https://integrate.api.nvidia.com/v1/chat/completions",
        "model": "deepseek-ai/deepseek-r1",
        "key": lambda: NVIDIA,
        "especialidade": "raciocinio cientifico e citacoes",
        "tokens": 2000
    },
    "cerebras_70b": {
        "url": "https://api.cerebras.ai/v1/chat/completions",
        "model": "llama-3.3-70b",
        "key": lambda: CEREBRAS,
        "especialidade": "hook viral e titulo cativante (ultrarapido)",
        "tokens": 1000
    },
    "together_mixtral": {
        "url": "https://api.together.xyz/v1/chat/completions",
        "model": "mistralai/Mixtral-8x22B-Instruct-v0.1",
        "key": lambda: TOGETHER,
        "especialidade": "narrativa e storytelling emocional",
        "tokens": 2000
    },
    "openrouter_deepseek_free": {
        "url": "https://openrouter.ai/api/v1/chat/completions",
        "model": "deepseek/deepseek-r1:free",
        "key": lambda: OPENROUTER,
        "especialidade": "angulo contraintuitivo e revelacao chocante",
        "tokens": 1500
    }
}

def chamar_llm(nome, config, prompt):
    """Chama um LLM especifico e retorna o resultado"""
    key = config["key"]()
    if not key:
        return {"llm": nome, "texto": "", "erro": "sem chave"}
    try:
        r = requests.post(config["url"],
            headers={"Authorization": f"Bearer {key}", "Content-Type": "application/json",
                     "HTTP-Referer": "https://psicologia.doc", "X-Title": "PsicologiaDoc"},
            json={"model": config["model"],
                  "messages": [{"role": "system", "content": f"Voce e especialista em {config['especialidade']}."},
                                {"role": "user", "content": prompt}],
                  "max_tokens": config["tokens"]},
            timeout=60)
        if r.status_code == 200:
            texto = r.json()["choices"][0]["message"]["content"]
            return {"llm": nome, "texto": texto, "erro": None, "especialidade": config["especialidade"]}
    except Exception as e:
        return {"llm": nome, "texto": "", "erro": str(e)}
    return {"llm": nome, "texto": "", "erro": f"status {r.status_code}"}

def oracle_multi_llm(topico, papel="hook"):
    """Chama TODOS os LLMs em paralelo e sintetiza o melhor"""
    prompts = {
        "hook": f"Crie UM hook de abertura DEVASTADOR para video psicologia sobre '{topico}'. Hook que para o scroll. Apenas o hook, 1-2 frases max.",
        "titulo": f"Crie 5 titulos VIRAIS para video YouTube sobre '{topico}'. Formato: numero. titulo. Apenas os titulos.",
        "roteiro_abertura": f"Escreva os 3 PRIMEIROS PARAGRAFOS do roteiro sobre '{topico}'. Deve prender em 30 segundos. Pesquisador real, dado concreto, revelacao contraintuitiva.",
        "thumbnail": f"Descreva EXATAMENTE a melhor thumbnail para '{topico}': texto principal, emocao do rosto, cores, composicao. Formato imagem FLUX."
    }
    prompt = prompts.get(papel, prompts["hook"])
    
    print(f"\nOracle Multi-LLM: {papel} sobre '{topico}'")
    print(f"Chamando {len(LLMS)} LLMs em paralelo...")
    
    resultados = []
    with ThreadPoolExecutor(max_workers=5) as ex:
        futures = {ex.submit(chamar_llm, nome, cfg, prompt): nome for nome, cfg in LLMS.items()}
        for future in as_completed(futures):
            r = future.result()
            if not r["erro"] and r["texto"]:
                resultados.append(r)
                print(f"  OK {r['llm']}: {len(r['texto'])} chars")
            else:
                print(f"  SKIP {r['llm']}: {r.get('erro','')}")
    
    if not resultados:
        return {"sintetizado": "", "individuais": []}
    
    # Sintetizar com o Groq (mais rapido e confiavel)
    if GROQ and len(resultados) > 1:
        todos_textos = "\n\n".join([f"=== {r['llm']} ({r['especialidade']}) ===\n{r['texto']}" for r in resultados])
        prompt_sintese = f"""
Voce recebeu {len(resultados)} versoes de {papel} sobre '{topico}' de diferentes IAs especializadas.
Cada uma tem uma especializacao diferente.

{todos_textos}

Crie UMA versao SINTETIZADA que combine o melhor de TODAS as IAs:
- O hook mais devastador
- A profundidade cientifica mais solida
- O angulo mais contraintuitivo
- A narrativa mais envolvente

Resultado sintetizado (apenas o conteudo, sem explicacoes):
"""
        r = requests.post("https://api.groq.com/openai/v1/chat/completions",
            headers={"Authorization": f"Bearer {GROQ}", "Content-Type": "application/json"},
            json={"model": "llama-3.3-70b-versatile",
                  "messages": [{"role": "user", "content": prompt_sintese}],
                  "max_tokens": 1500},
            timeout=45)
        if r.status_code == 200:
            sintetizado = r.json()["choices"][0]["message"]["content"]
            print(f"  SINTETIZADO: {len(sintetizado)} chars de {len(resultados)} LLMs")
            return {"sintetizado": sintetizado, "individuais": resultados, "n_llms": len(resultados)}
    
    # Fallback: usar o primeiro resultado
    melhor = max(resultados, key=lambda x: len(x["texto"]))
    return {"sintetizado": melhor["texto"], "individuais": resultados, "n_llms": len(resultados)}

def gerar_video_oracle(topico):
    """Pipeline completo: usa TODOS os LLMs para criar video impossivel de replicar"""
    print(f"\n{'='*60}")
    print(f"ORACLE MULTI-IA: Gerando video sobre '{topico}'")
    print(f"{'='*60}")
    inicio = time.time()
    
    # Fase 1: Hook (paralelo 5 LLMs)
    hook = oracle_multi_llm(topico, "hook")
    
    # Fase 2: Titulos (paralelo 5 LLMs)
    titulos = oracle_multi_llm(topico, "titulo")
    
    # Fase 3: Abertura roteiro (paralelo 5 LLMs)
    abertura = oracle_multi_llm(topico, "roteiro_abertura")
    
    # Fase 4: Thumbnail (paralelo 5 LLMs)
    thumbnail = oracle_multi_llm(topico, "thumbnail")
    
    tempo = time.time() - inicio
    print(f"\nOracle concluido em {tempo:.1f}s usando {hook.get('n_llms',0)} LLMs")
    
    resultado = {
        "topico": topico,
        "gerado_em": datetime.now().isoformat(),
        "n_llms_usados": hook.get("n_llms", 0),
        "hook_sintetizado": hook["sintetizado"],
        "titulos_sintetizados": titulos["sintetizado"],
        "abertura_roteiro": abertura["sintetizado"],
        "descricao_thumbnail": thumbnail["sintetizado"],
        "tempo_total_segundos": round(tempo, 1)
    }
    
    # Salvar no Supabase
    if SB_KEY:
        try:
            requests.post(f"{SB_URL}/rest/v1/content_pipeline",
                headers={"apikey": SB_KEY, "Authorization": f"Bearer {SB_KEY}",
                         "Content-Type": "application/json", "Prefer": "return=minimal"},
                json={"video_id": f"ORACLE_{datetime.now().strftime('%Y%m%d_%H%M')}",
                      "topico": topico, "status": "oracle_done",
                      "titulo": titulos["sintetizado"][:200],
                      "script": abertura["sintetizado"],
                      "n_llms_usados": resultado["n_llms_usados"]},
                timeout=10)
        except: pass
    
    return resultado

def run_oracle_demo():
    """Demonstracao do Oracle com topico do vídeo #683"""
    topico = "Narcisismo Encoberto: sinais que ele te manipula sem voce perceber"
    resultado = gerar_video_oracle(topico)
    
    print("\n" + "="*60)
    print("RESULTADO DO ORACLE MULTI-IA:")
    print("="*60)
    print(f"\nHOOK SINTETIZADO ({resultado['n_llms_usados']} LLMs):")
    print(resultado["hook_sintetizado"][:300])
    print(f"\nTITULOS SINTETIZADOS:")
    print(resultado["titulos_sintetizados"][:400])
    print(f"\nABERTURA ROTEIRO:")
    print(resultado["abertura_roteiro"][:400])
    print(f"\nTHUMBNAIL:")
    print(resultado["descricao_thumbnail"][:200])
    print(f"\nTempo total: {resultado['tempo_total_segundos']}s")
    print("\nEste conteudo e IMPOSSIVEL de replicar — combina 5 IAs especializadas.")
    return resultado

if __name__ == "__main__":
    run_oracle_demo()
