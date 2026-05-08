"""
llm_router.py - Fallback chain for free LLMs (psicologia.doc pipeline)

DEFAULT: Nvidia Build DeepSeek V4 Pro (1.6T MoE, FREE ILIMITADO 2026)
Tries in order (configurable via prefer_engine kwarg):
1. Nvidia DeepSeek V4 Pro       - DEFAULT, 1.6T MoE, 128k ctx, FREE
2. Nvidia Qwen 3.5 397B         - top tier MoE, FREE
3. Nvidia Llama 4 Maverick      - Meta latest, FREE
4. Nvidia Llama 3.3 70B         - Nvidia hosted, FREE
5. Groq Llama 3.3 70B           - 250ms quando todos Nvidia caem, FREE
6. OpenAI gpt-4o-mini           - last resort, PAID (raro)

All engines speak OpenAI-compatible chat completions API.
DeepSeek V4 Pro suporta: 128k context, JSON mode, response_format, max_tokens 8000+
"""
import os, json, time, urllib.request, urllib.error


class LLMRouter:
    # ENGINES 2026 - DeepSeek V4 Pro FIRST. NVIDIA_API_KEY libera 4 modelos top.
    # Order: smartest-first (DeepSeek V4 Pro 1.6T) -> diversified Nvidia -> Groq fast backup -> OpenAI paid
    ENGINES = [
        # 1. DEFAULT/PRIMARY: Nvidia DeepSeek V4 Pro - 1.6T MoE, 128k ctx, smartest free model
        ("nvidia_deepseek_v4",   "NVIDIA_API_KEY", "https://integrate.api.nvidia.com/v1", "deepseek-ai/deepseek-v4-pro"),
        # 2. Nvidia Qwen 3.5 397B MoE - top tier reasoning
        ("nvidia_qwen35",        "NVIDIA_API_KEY", "https://integrate.api.nvidia.com/v1", "qwen/qwen3.5-397b-a17b"),
        # 3. Nvidia Llama 4 Maverick - Meta latest 2026
        ("nvidia_llama4",        "NVIDIA_API_KEY", "https://integrate.api.nvidia.com/v1", "meta/llama-4-maverick-17b-128e-instruct"),
        # 4. Nvidia Llama 3.3 70B - solid backup
        ("nvidia_llama33",       "NVIDIA_API_KEY", "https://integrate.api.nvidia.com/v1", "meta/llama-3.3-70b-instruct"),
        # 5. Groq Llama 3.3 70B - 250ms ultra-fast (only when all Nvidia fail)
        ("groq",                 "GROQ_API_KEY",   "https://api.groq.com/openai/v1",      "llama-3.3-70b-versatile"),
        # 6. OpenAI gpt-4o-mini - LAST RESORT (paid, raramente atingido)
        ("openai_mini",          "OPENAI_API_KEY", "https://api.openai.com/v1",           "gpt-4o-mini"),
    ]

    # DeepSeek V4 Pro capabilities (uses higher max_tokens, JSON mode, longer timeout)
    DEEPSEEK_MAX_TOKENS = 8000
    DEFAULT_MAX_TOKENS = 4000

    def __init__(self, prefer_engine=None):
        self.prefer_engine = prefer_engine
        self.last_engine_used = None
        self.last_latency_ms = None

    def chat(self, messages, max_tokens=None, temperature=0.7, response_format=None, timeout=90, system=None):
        """
        Main chat method with full fallback chain.
        - max_tokens: defaults to 8000 for DeepSeek V4 Pro, 4000 for others
        - response_format: dict like {"type": "json_object"} for JSON mode
        - system: optional system prompt prepended to messages
        - timeout: 90s default (DeepSeek V4 Pro is slower but smarter)
        """
        if system:
            sys_msg = {"role": "system", "content": system}
            if not messages or messages[0].get("role") != "system":
                messages = [sys_msg] + list(messages)

        engines = list(self.ENGINES)
        if self.prefer_engine:
            engines.sort(key=lambda e: 0 if e[0] == self.prefer_engine else 1)

        last_err = None
        for name, env_key, base_url, model in engines:
            api_key = os.environ.get(env_key)
            if not api_key:
                continue

            # Use higher max_tokens for DeepSeek V4 Pro (it can handle it)
            mt = max_tokens or (self.DEEPSEEK_MAX_TOKENS if "deepseek" in model else self.DEFAULT_MAX_TOKENS)

            try:
                t0 = time.time()
                payload = {
                    "model": model,
                    "messages": messages,
                    "max_tokens": mt,
                    "temperature": temperature,
                }
                if response_format:
                    payload["response_format"] = response_format

                req = urllib.request.Request(
                    f"{base_url}/chat/completions",
                    data=json.dumps(payload).encode(),
                    headers={
                        "Authorization": f"Bearer {api_key}",
                        "Content-Type": "application/json",
                        "User-Agent": "psicologia-doc-llm-router/2.0",
                    },
                    method="POST",
                )
                with urllib.request.urlopen(req, timeout=timeout) as resp:
                    data = json.loads(resp.read().decode())
                    self.last_engine_used = name
                    self.last_latency_ms = int((time.time() - t0) * 1000)
                    content = data["choices"][0]["message"]["content"]
                    if not content and data["choices"][0]["message"].get("reasoning_content"):
                        content = data["choices"][0]["message"]["reasoning_content"]
                    return {
                        "content": content,
                        "engine": name,
                        "model": model,
                        "latency_ms": self.last_latency_ms,
                        "usage": data.get("usage", {}),
                    }
            except urllib.error.HTTPError as e:
                err_body = ""
                try:
                    err_body = e.read().decode()[:200]
                except Exception:
                    pass
                last_err = f"{name}: HTTP {e.code} {err_body}"
                print(f"[LLMRouter] {last_err}", flush=True)
                continue
            except Exception as e:
                last_err = f"{name}: {type(e).__name__}: {str(e)[:150]}"
                print(f"[LLMRouter] {last_err}", flush=True)
                continue

        raise RuntimeError(f"All engines failed. Last error: {last_err}")

    def classify_emotion(self, paragraph):
        """Classify a single paragraph emotion (uses DeepSeek V4 Pro by default)"""
        prompt = (
            "Classifique este paragrafo em UMA categoria emocional para narracao em audio: "
            "INTRO_CALMO, ALERTA_TENSO, EMPATIA_ACOLHEDOR, ANALITICO_FRIO, ESPERANCA_CRESCENTE, CTA_URGENTE. "
            "Responda APENAS a categoria (uma palavra com underscore).\n\n"
            f"Paragrafo: {paragraph}"
        )
        result = self.chat(
            messages=[{"role": "user", "content": prompt}],
            max_tokens=20,
            temperature=0.2,
        )
        return result["content"].strip().upper()

    def classify_emotions_batch(self, paragraphs, system=None):
        """Classify multiple paragraphs in one call (DeepSeek V4 Pro JSON mode)"""
        items = "\n".join(f"{i+1}. {p}" for i, p in enumerate(paragraphs))
        prompt = (
            "Classifique CADA paragrafo abaixo em UMA categoria emocional. "
            "Categorias validas: INTRO_CALMO, ALERTA_TENSO, EMPATIA_ACOLHEDOR, ANALITICO_FRIO, ESPERANCA_CRESCENTE, CTA_URGENTE. "
            "Responda em JSON com formato {\"emotions\": [\"CAT1\", \"CAT2\", ...]} preservando a ordem.\n\n"
            f"Paragrafos:\n{items}"
        )
        result = self.chat(
            messages=[{"role": "user", "content": prompt}],
            max_tokens=200 + len(paragraphs) * 20,
            temperature=0.2,
            response_format={"type": "json_object"},
            system=system,
        )
        try:
            parsed = json.loads(result["content"])
            return parsed.get("emotions", [])
        except Exception:
            # Fallback: parse line by line
            lines = [ln.strip().upper() for ln in result["content"].splitlines() if ln.strip()]
            return lines[:len(paragraphs)]

    # Legacy alias for backward compat with tts_edge.py
    def classify_emotions_groq(self, paragraphs, system=None):
        """DEPRECATED alias - now uses full chain (DeepSeek V4 Pro first)"""
        return self.classify_emotions_batch(paragraphs, system=system)


if __name__ == "__main__":
    # Quick test
    router = LLMRouter()
    print("Testing LLMRouter chain...")
    r = router.chat(messages=[{"role": "user", "content": "Diga apenas: OK"}], max_tokens=10)
    print(f"Engine: {r['engine']}, Model: {r['model']}, Latency: {r['latency_ms']}ms")
    print(f"Response: {r['content']}")
