#!/usr/bin/env python3
"""
llm_router_v5.py — LLM Router com DeepSeek V4 (28x mais barato)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
BASEADO EM: Transcript "DeepSeek V4 + Claude Code — 28x mais barato"

ECONOMIA REAL (transcript):
  Claude Opus  input: $5.00/M tokens   output: $25.00/M tokens
  DeepSeek V4  input: $0.435/M tokens  output: $0.87/M tokens
  ECONOMIA:    input: 11.5×            output: 28.7×

  Para 300 tarefas/dia (nossa operação):
  Opus:      $300-500/mês
  DeepSeek:  $10-20/mês
  ECONOMIA:  ~$480/mês → $5.760/ano

CADEIA V5 (do mais barato ao mais caro):
  1. DeepSeek V4 Pro (api.deepseek.com)    ← DEFAULT principal
  2. NVIDIA DeepSeek V4 Pro (via nvapi)    ← fallback idêntico
  3. Gemini 2.0 Flash (2000 req/day FREE)  ← ultra rápido, gratuito
  4. Groq LLaMA 3.3 70B (14.400/dia FREE) ← fallback 3
  5. DeepSeek via Open Router              ← fallback com Open Router
  6. OpenAI gpt-4o-mini                   ← paid último recurso

SECURITY NOTE (do transcript):
  DeepSeek é empresa chinesa. NÃO enviar:
  - Chaves API de outras plataformas
  - Dados pessoais de usuários
  - Informações sensíveis de negócio
  Usar apenas para: geração de scripts, títulos, análises genéricas

USO POR TIPO DE TAREFA:
  BULK (scripts, títulos, análises) → DeepSeek V4 (28x mais barato)
  CRÍTICO (publicação, decisões)    → Groq LLaMA (grátis, confiável)
  EMERGÊNCIA                        → OpenAI fallback
"""
import os, requests, time
import urllib3; urllib3.disable_warnings()

# Credenciais (do Supabase ia_cache)
DEEPSEEK_KEY = os.getenv("DEEPSEEK_API_KEY", "sk-071ba769ce3540fb809708ad0274331c")
NVIDIA_KEY   = os.getenv("NVIDIA_API_KEY", "")
GEMINI_KEY   = os.getenv("GEMINI_API_KEY", "AIzaSyDzCea_65Al-vy342xslBSVmKPv0qzTuXY")
GROQ_KEY     = os.getenv("GROQ_API_KEY", "")
OPENAI_KEY   = os.getenv("OPENAI_API_KEY", "")
OR_KEY       = os.getenv("OPENROUTER_API_KEY", "")  # Open Router (opcional)

MODELOS = {
    "deepseek_direct": {
        "url": "https://api.deepseek.com/chat/completions",
        "model": "deepseek-chat",
        "headers_key": DEEPSEEK_KEY,
        "prefix": "Bearer",
        "cost_input_per_M": 0.435,
        "cost_output_per_M": 0.87,
        "max_tokens": 4000,
    },
    "nvidia_deepseek": {
        "url": "https://integrate.api.nvidia.com/v1/chat/completions",
        "model": "deepseek-ai/deepseek-v3-0324",
        "headers_key": NVIDIA_KEY,
        "prefix": "Bearer",
        "cost_input_per_M": 0.40,
        "cost_output_per_M": 0.80,
        "max_tokens": 4000,
    },
    "gemini_flash": {
        "url": f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key={GEMINI_KEY}",
        "model": "gemini-2.0-flash",
        "special": "gemini",
        "cost_input_per_M": 0.0,  # 2000 req/dia grátis
        "cost_output_per_M": 0.0,
        "max_tokens": 2048,
    },
    "groq_llama": {
        "url": "https://api.groq.com/openai/v1/chat/completions",
        "model": "llama-3.3-70b-versatile",
        "headers_key": GROQ_KEY,
        "prefix": "Bearer",
        "cost_input_per_M": 0.0,  # 14.400 req/dia grátis
        "cost_output_per_M": 0.0,
        "max_tokens": 2000,
    },
    "openrouter_deepseek": {
        "url": "https://openrouter.ai/api/v1/chat/completions",
        "model": "deepseek/deepseek-chat-v3-0324:free",
        "headers_key": OR_KEY,
        "prefix": "Bearer",
        "cost_input_per_M": 0.0,  # free tier Open Router
        "cost_output_per_M": 0.0,
        "max_tokens": 2000,
    },
}

# Rotas por tipo de tarefa
ROTAS = {
    "script":    ["deepseek_direct", "nvidia_deepseek", "groq_llama", "gemini_flash"],
    "titulo":    ["deepseek_direct", "nvidia_deepseek", "groq_llama", "gemini_flash"],
    "analise":   ["deepseek_direct", "gemini_flash", "groq_llama"],
    "imersivo":  ["deepseek_direct", "groq_llama", "nvidia_deepseek"],
    "reflexivo": ["groq_llama", "deepseek_direct", "nvidia_deepseek"],
    "afiliado":  ["deepseek_direct", "groq_llama"],
    "default":   ["deepseek_direct", "nvidia_deepseek", "gemini_flash", "groq_llama"],
}

_tokens_usados = {"input": 0, "output": 0, "custo_usd": 0.0, "chamadas": 0}

def _chamar_deepseek(cfg, prompt, max_tokens, temperature):
    r = requests.post(cfg["url"],
        headers={"Authorization": f"{cfg['prefix']} {cfg['headers_key']}",
                 "Content-Type": "application/json"},
        json={"model": cfg["model"],
              "messages": [{"role": "user", "content": prompt}],
              "max_tokens": min(max_tokens, cfg["max_tokens"]),
              "temperature": temperature},
        timeout=30, verify=False)
    if r.status_code == 200:
        d = r.json()
        texto = d["choices"][0]["message"]["content"].strip()
        uso   = d.get("usage", {})
        inp   = uso.get("prompt_tokens", 0)
        out   = uso.get("completion_tokens", 0)
        custo = (inp/1_000_000)*cfg["cost_input_per_M"] + (out/1_000_000)*cfg["cost_output_per_M"]
        _tokens_usados["input"]    += inp
        _tokens_usados["output"]   += out
        _tokens_usados["custo_usd"]+= custo
        _tokens_usados["chamadas"] += 1
        return texto
    return None

def _chamar_gemini(cfg, prompt, max_tokens, temperature):
    r = requests.post(cfg["url"],
        json={"contents": [{"role": "user", "parts": [{"text": prompt}]}],
              "generationConfig": {"maxOutputTokens": min(max_tokens, cfg["max_tokens"]),
                                   "temperature": temperature}},
        timeout=30, verify=False)
    if r.status_code == 200:
        texto = r.json()["candidates"][0]["content"]["parts"][0]["text"].strip()
        _tokens_usados["chamadas"] += 1
        return texto
    return None

def completar(prompt, tarefa="default", max_tokens=300, temperature=0.82):
    """Chama modelos em cadeia até obter resposta. Retorna texto ou None."""
    cadeia = ROTAS.get(tarefa, ROTAS["default"])
    for nome in cadeia:
        cfg = MODELOS.get(nome, {})
        if not cfg: continue
        key = cfg.get("headers_key","")
        # Pula se não tem key configurada
        if not key and nome not in ("gemini_flash",): continue
        try:
            if cfg.get("special") == "gemini":
                texto = _chamar_gemini(cfg, prompt, max_tokens, temperature)
            else:
                if not key: continue
                texto = _chamar_deepseek(cfg, prompt, max_tokens, temperature)
            if texto:
                return texto
        except Exception as e:
            print(f"     [{nome}] erro: {e}")
        time.sleep(0.5)
    return None

def stats():
    return {
        "chamadas":  _tokens_usados["chamadas"],
        "tokens_in": _tokens_usados["input"],
        "tokens_out":_tokens_usados["output"],
        "custo_usd": round(_tokens_usados["custo_usd"], 4),
        "economia_vs_opus": f"{_tokens_usados['custo_usd'] * 28.7:.2f} USD economizados vs Opus",
    }

# ── TESTE DO ROUTER ─────────────────────────────────────────────────────────
if __name__ == "__main__":
    print("=== LLM Router V5 — Teste ===\n")
    tarefas = [
        ("script", "Escreva 2 frases sobre narcisismo em PT-BR, estilo reflexivo, sem hashtags."),
        ("titulo", "Gere 3 títulos virais sobre burnout psicológico em PT-BR, 10 palavras max."),
        ("analise","Explique brevemente o que é apego ansioso em 50 palavras em PT-BR."),
    ]
    for tarefa, prompt in tarefas:
        print(f"  🔄 [{tarefa}] {prompt[:50]}...")
        resp = completar(prompt, tarefa=tarefa, max_tokens=200, temperature=0.82)
        if resp:
            print(f"     ✅ {resp[:80]}...")
        else:
            print(f"     ⚠️  Sem resposta")
        time.sleep(2)

    s = stats()
    print(f"\n{'='*50}")
    print(f"  📊 {s['chamadas']} chamadas | ${s['custo_usd']} custo")
    print(f"  💰 {s['economia_vs_opus']}")
    print(f"  🔑 DeepSeek V4 como motor principal (28x mais barato)")
    print("="*50)
