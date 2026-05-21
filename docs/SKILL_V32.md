---
name: psicologia-doc-v27
description: Use esta SKILL sempre que o usuário mencionar: psicologia.doc, repovazio, Daniela Coelho, @psidanielacoelho, canal YouTube psicologia, viral, cérebro autônomo, tokens sociais, Instagram, TikTok, WhatsApp grupos, monetização, 1000 subs, crescimento, setup tokens, espelhamento viral.
version: 32.0
date: 2026-05-21
---

# SKILL — psicologia.doc V32 — CONHECIMENTO COMPLETO + TODOS OS LINKS

---

## ⚠️ REGRA DE OURO

```
NUNCA liberar vídeo sem testar #683 PRIMEIRO.
1. GitHub Action video_id=683, voice_version=B
2. RMS trough=-inf (silêncio digital perfeito)
3. Cada frame reflete a frase sendo dita
4. SÓ após aprovação: disparar os demais
```

---

## 🏗️ INFRA CORE

```
Supabase:   tpjvalzwkqwttvmszvie  →  https://app.supabase.com/project/tpjvalzwkqwttvmszvie
Vercel:     repovazio.vercel.app   →  https://vercel.com/tafita81/repovazio
GitHub:     tafita81/Repovazio    →  https://github.com/tafita81/Repovazio

Canal ATIVO:   UCyCkIpsVgME9yCj_oXJFheA
               @psidanielacoelho
               psidanielacoelho1982@gmail.com
               https://youtube.com/@psidanielacoelho

Canal ⛔ BLOQUEADO: UCSH63tBfY6wEIdkC4u4zKdg — REMOVIDO 2026-05-07, NUNCA publicar

Scripts:
  Short V31:  scripts/render_short_george.py
  Long  V31:  scripts/render_long_15min.py

Workflows:
  Short:  .github/workflows/render-short-george.yml   (45min timeout)
  Long:   .github/workflows/render-long-15min.yml     (120min timeout)

Páginas Vercel:
  Hub:          https://repovazio.vercel.app/hub.html
  Vídeos:       https://repovazio.vercel.app/videos-prontos.html
  Painel 400:   https://repovazio.vercel.app/painel-400.html
  Setup Tokens: https://repovazio.vercel.app/setup-tokens.html

Docs GitHub:
  SKILL V32:    https://github.com/tafita81/Repovazio/blob/main/docs/SKILL_V31.md
  Painel 400:   https://github.com/tafita81/Repovazio/blob/main/public/painel-400.html
```

---

## 📚 DIRETÓRIOS DE APIS PÚBLICAS (MEGA-LISTAS)

### Os 7 Maiores Diretórios

```
1. public-apis (GitHub) — 1.400+ APIs  ⭐ MAIS FAMOSO
   https://github.com/public-apis/public-apis
   - Categorias: animais, arte, clima, finanças, saúde, música, ciência, etc.
   - JSON API própria: https://api.publicapis.org/entries
   - Busca por categoria: https://api.publicapis.org/entries?category=Science

2. publicapis.dev — 1.400+ APIs navegáveis (MELHOR UI)
   https://publicapis.dev
   - Colaborativa, filtrável por auth/HTTPS/CORS
   - Atualizada pela comunidade

3. public-apis.io — 1.000+ APIs categorizadas
   https://public-apis.io
   - Inclui: filmes, anime, clima, música, jogos, câmbio, esportes, ciência

4. publicapis.io — 1.000+ com exemplos de código
   https://publicapis.io
   - Inclui chaves de API, exemplos de código e documentação

5. public-api-lists (GitHub) — 48 categorias
   https://github.com/public-api-lists/public-api-lists
   - JSON API gratuita própria
   - Inclui APIs brasileiras de dados públicos

6. mixedanalytics — ~200 APIs SEM AUTH (sem chave)
   https://mixedanalytics.com/blog/list-actually-free-open-no-auth-needed-apis/
   - Foco: APIs que não exigem nenhuma autenticação
   - Ideal para testes rápidos

7. RapidAPI Marketplace — 40.000+ APIs
   https://rapidapi.com
   - Maior marketplace do mundo
   - Inclui tiers gratuitos para maioria
   - Hub de dev: https://rapidapi.com/hub

EXTRA — Diretórios especializados:
  Free LLM APIs:     https://freellm.net
  Free LLM (GitHub): https://github.com/open-free-llm-api/awesome-freellm-apis
  Free AI Tools:     https://github.com/ShaikhWarsi/free-ai-tools
  No-Cost AI:        https://github.com/zebbern/no-cost-ai
  Awesome Free LLM:  https://github.com/amardeeplakshkar/awesome-free-llm-apis
  Awesome Free LLM2: https://github.com/mnfst/awesome-free-llm-apis
```

---

## 🎤 APIS DE VOZ — COMPLETO COM LINKS

### HIERARQUIA DE PRIORIDADE

```
P1 → Chatterbox Multilingual (PADRÃO — MIT, grátis, ilimitado)
P2 → Qwen3-TTS (PRÓXIMO UPGRADE — Apache 2.0, PT-BR, ilimitado)
P3 → Kokoro TTS (offline, MIT, leve)
P4 → ElevenLabs George (quota mensal)
P5 → Edge TTS ThalitaMultilingualNeural (Long — grátis, ilimitado)
P6 → Pollinations Audio (sem key)
P7 → F5-TTS (zero-shot, MIT)
P8 → IndexTTS Bilibili (Apache 2.0)
P9 → VoxCPM 1.5 (MIT)
P10 → OmniVoice (600+ idiomas)
P11 → Kokoro ONNX (browser/offline)
P12 → Piper TTS (offline, rápido)
```

### P1 — Chatterbox Multilingual ✅ PADRÃO ATUAL

```python
# Repositório:     https://github.com/resemble-ai/chatterbox
# PyPI:            https://pypi.org/project/chatterbox-tts/
# Licença: MIT | Custo: $0 | Limite: ilimitado | PT-BR: ✅
# 63.75% preferem ao ElevenLabs em testes cegos
# 23 idiomas incluindo PT-BR
# Modelos: Chatterbox base + Chatterbox Multilingual + Chatterbox Turbo

pip install chatterbox-tts torch --index-url https://download.pytorch.org/whl/cpu

from chatterbox.tts import ChatterboxMultilingualTTS
model = ChatterboxMultilingualTTS.from_pretrained(device="cpu")
wav = model.generate(texto,
    audio_prompt_path=GEORGE_REF,   # referência 14s
    language_id="pt",
    exaggeration=0.96,              # drama máximo
    cfg_weight=0.09)                # fala lenta

# Self-hosted server (OpenAI-compatible API):
# https://github.com/devnen/Chatterbox-TTS-Server
# Docker: docker compose up -d

# Referência George (14s áudio limpo):
GEORGE_REF = "https://tpjvalzwkqwttvmszvie.supabase.co/storage/v1/object/public/videos/mp4s/v683_george_1779065193.mp4"
```

### P2 — Qwen3-TTS (Alibaba — Apache 2.0) 🔥 PRÓXIMO UPGRADE

```python
# Repositório:     https://github.com/QwenLM/Qwen3-TTS
# HuggingFace 0.6B: https://huggingface.co/Qwen/Qwen3-TTS-0.6B
# HuggingFace 1.7B: https://huggingface.co/Qwen/Qwen3-TTS-1.7B
# Paper:           https://arxiv.org/abs/2501.xxxxx
# Licença: Apache 2.0 | PT-BR: ✅ | Latência: 97ms | Custo: $0
# Clonagem com 3s de áudio | 10 idiomas | supera ElevenLabs
# Idiomas: PT, EN, ZH, JA, KO, DE, FR, RU, ES, IT
# Modo Voice Design: instruções em linguagem natural

pip install torch transformers
from transformers import AutoModelForSpeechSeq2Seq
# Demo online: https://qwen3tts.com
```

### P3 — Kokoro TTS (MIT, 82M params, offline)

```python
# Repositório:   https://github.com/hexgrad/kokoro
# ONNX version:  https://github.com/thewh1teagle/kokoro-onnx
# Browser demo:  https://offlinetts.com
# PyPI:          https://pypi.org/project/kokoro-onnx/
# Licença: MIT | PT-BR: ✅ | 54 vozes | 9 idiomas | $0

pip install kokoro-onnx soundfile
from kokoro_onnx import Kokoro
kokoro = Kokoro("kokoro-v1.0.onnx", "voices.bin")
samples, sr = kokoro.create(texto, voice="bf_emma", lang="pt-br")
```

### P4 — ElevenLabs George (JBFqnCBsd6RMkjVDRZzb)

```python
# Dashboard:    https://elevenlabs.io/app
# API Docs:     https://elevenlabs.io/docs/api-reference
# Voice ID:     JBFqnCBsd6RMkjVDRZzb (George)
# Custo: 32K chars/mês free tier (reseta mensalmente)
# stability=0.20, similarity_boost=0.85, style=0.70, speed=1.0
```

### P5 — Microsoft Edge TTS (grátis, ilimitado, sem key)

```python
# GitHub:       https://github.com/rany2/edge-tts
# PyPI:         https://pypi.org/project/edge-tts/
# Vozes PT-BR:  ThalitaMultilingualNeural (PADRÃO LONG)
#               FranciscaNeural (forte entonação)
#               AntonioNeural (emergência)
# Custo: $0 | Limite: ilimitado | Sem key

pip install edge-tts
import edge_tts, asyncio
async def gen():
    c = edge_tts.Communicate(texto, voice="pt-BR-ThalitaMultilingualNeural", rate="+32%")
    await c.save("output.mp3")
asyncio.run(gen())

# Listar todas as vozes PT-BR:
# edge-tts --list-voices | grep pt-BR
```

### P6 — Pollinations Audio (grátis, sem key)

```python
# API Docs:     https://github.com/pollinations/pollinations/blob/main/APIDOCS.md
# Endpoint:     https://gen.pollinations.ai/audio
# Developer:    https://enter.pollinations.ai
# Vozes:        alloy, echo, fable, onyx, nova, shimmer, coral, verse, ballad, ash, sage
# Custo: $0 | Sem key anônimo (1 req/15s) | Registro grátis = 1 req/5s

import requests
r = requests.post("https://gen.pollinations.ai/audio", json={
    "model": "openai-audio",
    "voice": "nova",                # onyx = masculino, nova = feminino
    "input": texto,
    "response_format": "mp3"
})
with open("audio.mp3", "wb") as f: f.write(r.content)
```

### P7 — F5-TTS (MIT, zero-shot cloning)

```python
# Repositório:  https://github.com/SWivid/F5-TTS
# HuggingFace:  https://huggingface.co/SWivid/F5-TTS
# Demo Space:   https://huggingface.co/spaces/mrfakename/E2-F5-TTS
# Licença: MIT | Zero-shot cloning 5-10s | PT-BR com sample
pip install f5-tts
```

### P8 — IndexTTS (Bilibili, Apache 2.0)

```python
# Repositório:  https://github.com/index-tts/IndexTTS
# HuggingFace:  https://huggingface.co/IndexTeam/IndexTTS
# Licença: Apache 2.0 | Zero-shot | Multilingual
pip install indextts
```

### P9 — VoxCPM 1.5 (MIT, clonagem avançada)

```python
# Repositório:  https://github.com/VoxCPM/VoxCPM
# Transcrição automática + clone automático
# ~8GB VRAM (CPU fallback disponível)
```

### P10 — OmniVoice (600+ idiomas)

```python
# Repositório:  https://github.com/OmniVoice/OmniVoice
# 600+ idiomas/dialetos — maior cobertura do mundo
```

### P11 — Piper TTS (offline, rápido, MIT)

```python
# Repositório:  https://github.com/rhasspy/piper
# Binários:     https://github.com/rhasspy/piper/releases
# Vozes PT-BR:  https://huggingface.co/rhasspy/piper-voices
# Custo: $0 | Offline | CPU-only | Muito rápido
```

### P12 — Estúdios Multi-Engine (open source)

```python
# TTS-Story (12 engines):    https://github.com/Xerophayze/TTS-Story
# VoiceBox (7 engines):      https://github.com/jamiepine/voicebox
# Voice Cloning Benchmark:   https://github.com/savg92/voice-cloning
# Chatterbox Server UI:      https://github.com/devnen/Chatterbox-TTS-Server
# OpenAudio (self-hosted):   https://github.com/monocle-h2020/openaudio
```

---

## 🖼️ APIS DE IMAGEM — COMPLETO COM LINKS

### P1 — Pollinations FLUX ✅ PADRÃO

```python
# Repositório:  https://github.com/pollinations/pollinations
# API Docs:     https://github.com/pollinations/pollinations/blob/main/APIDOCS.md
# Dev Console:  https://enter.pollinations.ai
# Auth:         https://auth.pollinations.ai  (Seed tier = 1 req/5s)
# Custo: $0 | Modelos: flux, flux-realism, flux-anime, gptimage, seedream, kontext
# Tier free: 1 req/15s (anônimo) | Seed: 1 req/5s (registro gratuito)

import urllib.parse, requests

# Endpoint clássico:
url = f"https://image.pollinations.ai/prompt/{urllib.parse.quote(prompt)}"
url += "?width=576&height=1024&model=flux&seed=42&nologo=true"

# Unified endpoint (NOVO 2026):
url = f"https://gen.pollinations.ai/image/{urllib.parse.quote(prompt)}"

# Image-to-image (kontext model):
url += "&model=kontext&image=URL_DA_IMAGEM_REFERENCIA"

r = requests.get(url, timeout=30)
# Verificar magic bytes antes de salvar:
def is_valid_img(content):
    return len(content)>5000 and content[:3] in (b'\xff\xd8\xff',b'\x89PN',b'\x89PG')
```

### P2 — Banco Supabase Interno ✅ PRIMÁRIO

```python
# URL:      https://tpjvalzwkqwttvmszvie.supabase.co
# Tabela:   image_bank  (125+ imagens kawaii, <2s de carregamento)
# Personagens: daniela, sara, marcos, julia, ana
SB_URL = "https://tpjvalzwkqwttvmszvie.supabase.co"
r = requests.get(f"{SB_URL}/rest/v1/image_bank?character_slug=eq.daniela&limit=10",
    headers={"apikey": SB_KEY, "Authorization": f"Bearer {SB_KEY}"})
```

### P3 — ZSky AI (grátis, 1080p, sem key)

```python
# Site:     https://zsky.ai
# API Blog: https://zsky.ai/blog/ai-image-generator-api-free
# Custo: $0 free tier | Watermark ZSky | Uso comercial incluído

r = requests.post("https://zsky.ai/api/v1/image/generate", json={
    "prompt": prompt, "resolution": "1080p", "style": "cinematic"
})
```

### P4 — HuggingFace Inference API

```python
# Site:       https://huggingface.co/inference-api
# Docs:       https://huggingface.co/docs/api-inference
# Models:     https://huggingface.co/models?pipeline_tag=text-to-image
# Custo: $0 com HF_TOKEN | 1K req/hora com chave grátis
# Modelos: FLUX.1-schnell, SDXL, SD3, kandinsky-2.2

import requests
HF_TOKEN = "hf_..."  # https://huggingface.co/settings/tokens
r = requests.post(
    "https://api-inference.huggingface.co/models/black-forest-labs/FLUX.1-schnell",
    headers={"Authorization": f"Bearer {HF_TOKEN}"},
    json={"inputs": prompt}
)
```

### P5 — Puter.js (grátis, ilimitado, sem key — user-pays)

```javascript
// Site:     https://puter.com
// Dev:      https://developer.puter.com/tutorials/free-unlimited-image-generation-api/
// GitHub:   https://github.com/HeyPuter/puter
// CDN:      <script src="https://cdn.puter.com/puter.js"></script>
// Modelos:  GPT Image, DALL-E 3, Gemini 2.5 Flash, Flux.1, SD3, SDXL

const img = await puter.ai.txt2img("kawaii anime girl psychology");
document.body.appendChild(img);
```

### P6 — Pixazo (registro grátis, FLUX/SDXL)

```python
# Site:  https://pixazo.ai/api
# Plano: grátis sem cartão de crédito
# Modelos free: Flux Schnell, SD1.5, SDXL
```

### P7 — Stability AI (créditos grátis)

```python
# Site:   https://stability.ai
# API:    https://platform.stability.ai/docs/api-reference
# Grátis: 25 créditos/mês free tier
# Modelos: SDXL, SD3 Medium, Stable Image Core
```

### P8 — Open-Generative-AI (MIT, self-hosted, 200+ modelos)

```python
# GitHub:   https://github.com/Anil-matcha/Open-Generative-AI
# Modelos:  Flux, Kling, Sora-style, Veo-style, Midjourney-style
# Self-hosted Next.js + API Muapi
```

---

## 🎬 APIS DE VÍDEO — COMPLETO COM LINKS

### P1 — Pipeline Interno Ken Burns ✅ PADRÃO ($0, ilimitado)

```python
# Short 58s: https://github.com/tafita81/Repovazio/blob/main/scripts/render_short_george.py
# Long 15min: https://github.com/tafita81/Repovazio/blob/main/scripts/render_long_15min.py
# Ken Burns: zoom 0/4/8% via Pillow + FFmpeg
# Custo: $0, ilimitado, sem watermark
```

### P2 — ZSky AI Video (grátis, 1080p + áudio, sem key)

```python
# Site:       https://zsky.ai
# API Blog:   https://zsky.ai/blog/ai-video-api-free-2026
# Custo: $0 free tier | 1080p | Áudio incluído | Uso comercial
# Watermark ZSky no free tier | Webhook callback disponível

import requests
r = requests.post("https://zsky.ai/api/v1/video/generate", json={
    "prompt": "kawaii anime girl talking about psychology",
    "duration": 5, "resolution": "1080p",
    "audio": True, "style": "cinematic"
})
with open("video.mp4", "wb") as f: f.write(r.content)
```

### P3 — Wan2.1 (HuggingFace, open source)

```python
# HuggingFace Space: https://huggingface.co/spaces/Wan-AI/Wan2.1
# GitHub:            https://github.com/Wan-Video/Wan2.1
# Geração texto→vídeo, alta qualidade
```

### P4 — CogVideoX (THUDM, Apache 2.0)

```python
# GitHub:     https://github.com/THUDM/CogVideo
# HuggingFace: https://huggingface.co/THUDM/CogVideoX-5b
# Licença: Apache 2.0 | Texto→vídeo | Open source
```

### P5 — LTX-Video (LightriX, open source)

```python
# GitHub:     https://github.com/Lightricks/LTX-Video
# HuggingFace: https://huggingface.co/Lightricks/LTX-Video
# Rápido, qualidade alta
```

### P6 — Open-Generative-AI (MIT, 200+ modelos)

```python
# GitHub: https://github.com/Anil-matcha/Open-Generative-AI
# Inclui: Kling, Sora-style, Veo-style
# Self-hosted
```

---

## 🤖 APIS DE LLM — COMPLETO COM LINKS (12 gratuitas)

### Stack LLMRouter V4 (pipeline atual)

```python
PROVIDERS = {
    "nvidia":   ("https://integrate.api.nvidia.com/v1",       "deepseek-ai/deepseek-v4-pro"),    # DEFAULT
    "nvidia2":  ("https://integrate.api.nvidia.com/v1",       "meta/llama-3.3-70b-instruct"),
    "groq":     ("https://api.groq.com/openai/v1",            "llama-3.3-70b-versatile"),
    "openai":   ("https://api.openai.com/v1",                  "gpt-4o-mini"),
}
```

### Todas as APIs LLM Gratuitas Permanentes

```python
# 1. GROQ — Mais rápido (315 tokens/s)
#    Site:     https://console.groq.com
#    Docs:     https://console.groq.com/docs/openai
#    Modelos:  llama-3.3-70b-versatile, llama-4-maverick, deepseek-r1
#    Limite:   14.400 req/dia | Sem cartão
#    Key:      GROQ_API_KEY

# 2. NVIDIA NIM — Mais modelos (46+)
#    Site:     https://build.nvidia.com
#    Docs:     https://docs.api.nvidia.com
#    Modelos:  deepseek-v4-pro, llama-3.3-70b, qwen3-coder, mistral-large
#    Limite:   40 req/min | Exige telefone
#    Key:      NVIDIA_API_KEY

# 3. GOOGLE AI STUDIO — Mais generoso (1.500 req/dia)
#    Site:     https://aistudio.google.com
#    Docs:     https://ai.google.dev/api
#    Modelos:  gemini-2.5-flash, gemini-2.5-pro, gemini-3-flash, gemma-3
#    Limite:   1.500 req/dia, 250K tokens/min | Sem cartão
#    Key:      GEMINI_API_KEY

# 4. OPENROUTER — 11+ modelos free
#    Site:     https://openrouter.ai
#    Docs:     https://openrouter.ai/docs
#    Modelos:  llama-3.3-70b:free, deepseek-r1:free, qwen3-235b:free
#    Limite:   50 req/dia (sem compra) | 1K req/dia ($10 único)
#    Key:      OPENROUTER_API_KEY

# 5. CEREBRAS — 1M tokens/dia
#    Site:     https://cloud.cerebras.ai
#    Docs:     https://inference-docs.cerebras.ai
#    Modelos:  llama-3.3-70b, deepseek-r1, gpt-oss-120b
#    Limite:   1M tokens/dia | Sem cartão
#    Key:      CEREBRAS_API_KEY

# 6. MISTRAL — 1B tokens/mês
#    Site:     https://console.mistral.ai
#    Docs:     https://docs.mistral.ai
#    Modelos:  mistral-small-latest, codestral-2501, mistral-large
#    Limite:   1B tokens/mês | Sem cartão
#    Key:      MISTRAL_API_KEY

# 7. CLOUDFLARE WORKERS AI — 10K neurons/dia
#    Site:     https://dash.cloudflare.com/?to=/:account/ai
#    Docs:     https://developers.cloudflare.com/workers-ai/
#    Modelos:  llama-3.3-70b, deepseek-r1, gpt-oss-120b, qwen3-coder
#    Limite:   10K neurons/dia | Sem cartão
#    Key:      CF_API_TOKEN + CF_ACCOUNT_ID

# 8. POLLINATIONS LLM — Sem key para uso básico
#    Site:     https://pollinations.ai
#    Docs:     https://github.com/pollinations/pollinations/blob/main/APIDOCS.md
#    Endpoint: https://gen.pollinations.ai/v1  (OpenAI-compatible)
#    Modelos:  openai-large, claude, gemini, deepseek, qwen3-coder
#    Limite:   1 req/15s anônimo | Registro gratuito = 1 req/5s
#    Key:      Sem key (opcional: auth.pollinations.ai)

# 9. GITHUB MODELS — GPT-5, GPT-4o, o4-mini
#    Site:     https://github.com/marketplace/models
#    Docs:     https://docs.github.com/en/github-models
#    Endpoint: https://models.inference.ai.azure.com
#    Modelos:  gpt-5, gpt-4.1, gpt-4o, o4-mini, Llama-3.3-70B
#    Limite:   50 chat + 2K completions/mês (Copilot free)
#    Key:      GITHUB_TOKEN (github.com/settings/tokens)

# 10. HUGGINGFACE — 1K req/hora
#     Site:     https://huggingface.co
#     Docs:     https://huggingface.co/docs/api-inference
#     Endpoint: https://api-inference.huggingface.co/v1
#     Modelos:  Llama-3.3-70B-Instruct, Qwen3-235B-A22B
#     Limite:   1K req/hora com key grátis | 2 req/min anônimo
#     Key:      HF_TOKEN (huggingface.co/settings/tokens)

# 11. SAMBANOVA — $5 free / 3 meses
#     Site:     https://cloud.sambanova.ai
#     Docs:     https://docs.sambanova.ai
#     Modelos:  Meta-Llama-3.1-405B, DeepSeek-R1-671B, Qwen3-235B
#     Limite:   Muito generoso por 3 meses
#     Key:      SAMBANOVA_API_KEY

# 12. OVH Kepler AI — 2 req/min sem key
#     Endpoint: https://oai.endpoints.kepler.ai.cloud.ovh.net/v1
#     Modelos:  40+ modelos open-weight da EU
#     Sem signup | OpenAI-compatible
#     Key:      Sem key

# EXTRA — LLM7.io (sem chave)
#     Site:     https://llm7.io
#     Sem signup | Acesso a vários modelos

# EXTRA — Pollinations via Python (sem key)
from openai import OpenAI
client = OpenAI(base_url="https://gen.pollinations.ai/v1", api_key="dummy")
resp = client.chat.completions.create(
    model="openai-large",
    messages=[{"role":"user","content":"Gere um script de psicologia em PT-BR"}]
)
```

---

## 📺 YOUTUBE API — COMPLETO COM LINKS

```python
# YouTube Data API v3 (oficial)
# Console:    https://console.cloud.google.com
# Habilitar:  https://console.cloud.google.com/apis/library/youtube.googleapis.com
# Docs:       https://developers.google.com/youtube/v3
# Analytics:  https://developers.google.com/youtube/analytics
# Quota:      10.000 unidades/dia GRÁTIS
# Upload:     1.600 unidades → 6 vídeos/dia por projeto
#
# ESTRATÉGIA MULTI-PROJETO:
# Criar 3+ projetos Google Cloud → 30K unidades/dia → 18 uploads/dia
# Cada projeto = email diferente ou mesmo email
#
# OAuth pendente: psidanielacoelho1982@gmail.com
# Canal ID: UCyCkIpsVgME9yCj_oXJFheA

YOUTUBE_CONFIG = {
    "base_url":      "https://www.googleapis.com/youtube/v3",
    "upload_url":    "https://www.googleapis.com/upload/youtube/v3/videos",
    "analytics_url": "https://youtubeanalytics.googleapis.com/v2",
    "channel_id":    "UCyCkIpsVgME9yCj_oXJFheA",
    "canal_url":     "https://youtube.com/@psidanielacoelho",
    "quota_dia":     10000,
    "custo_upload":  1600,
    "max_uploads":   6,  # por projeto por dia
    "auth_pendente": "psidanielacoelho1982@gmail.com",
}

# Alternativas sem quota:
# yt-dlp:                    https://github.com/yt-dlp/yt-dlp
# youtube-transcript-api:    https://github.com/jdepoix/youtube-transcript-api
# pytube:                    https://github.com/pytube/pytube
# Supadata (sem quota):      https://supadata.ai/youtube-api
# SociaVault (sem quota):    https://sociavault.com
```

---

## 🔧 REPOSITÓRIOS GITHUB ESSENCIAIS

```python
REPOS = {
    # === NOSSO PROJETO ===
    "repovazio":          "https://github.com/tafita81/Repovazio",

    # === TTS ===
    "chatterbox":         "https://github.com/resemble-ai/chatterbox",
    "chatterbox-server":  "https://github.com/devnen/Chatterbox-TTS-Server",
    "qwen3-tts":          "https://github.com/QwenLM/Qwen3-TTS",
    "kokoro":             "https://github.com/hexgrad/kokoro",
    "kokoro-onnx":        "https://github.com/thewh1teagle/kokoro-onnx",
    "f5-tts":             "https://github.com/SWivid/F5-TTS",
    "indextts":           "https://github.com/index-tts/IndexTTS",
    "piper":              "https://github.com/rhasspy/piper",
    "tts-story":          "https://github.com/Xerophayze/TTS-Story",
    "voicebox":           "https://github.com/jamiepine/voicebox",
    "voice-cloning":      "https://github.com/savg92/voice-cloning",

    # === LLM FREE ===
    "awesome-free-llm":   "https://github.com/amardeeplakshkar/awesome-free-llm-apis",
    "free-llm-dir":       "https://github.com/open-free-llm-api/awesome-freellm-apis",
    "no-cost-ai":         "https://github.com/zebbern/no-cost-ai",
    "free-ai-tools":      "https://github.com/ShaikhWarsi/free-ai-tools",
    "awesome-free-llm2":  "https://github.com/mnfst/awesome-free-llm-apis",
    "vibheksoni-free-ai": "https://github.com/vibheksoni/free-ai",

    # === IMAGEM / VÍDEO ===
    "pollinations":       "https://github.com/pollinations/pollinations",
    "open-gen-ai":        "https://github.com/Anil-matcha/Open-Generative-AI",
    "stable-diffusion":   "https://github.com/AUTOMATIC1111/stable-diffusion-webui",
    "wan2.1":             "https://github.com/Wan-Video/Wan2.1",
    "cogvideo":           "https://github.com/THUDM/CogVideo",
    "ltx-video":          "https://github.com/Lightricks/LTX-Video",

    # === YOUTUBE / SOCIAL ===
    "yt-dlp":             "https://github.com/yt-dlp/yt-dlp",
    "yt-transcript":      "https://github.com/jdepoix/youtube-transcript-api",
    "pytube":             "https://github.com/pytube/pytube",

    # === DIRETÓRIOS DE APIS ===
    "public-apis":        "https://github.com/public-apis/public-apis",
    "public-api-lists":   "https://github.com/public-api-lists/public-api-lists",
}

# Diretórios web (não GitHub):
DIRECTORIES = {
    "publicapis.dev":     "https://publicapis.dev",
    "public-apis.io":     "https://public-apis.io",
    "publicapis.io":      "https://publicapis.io",
    "mixedanalytics":     "https://mixedanalytics.com/blog/list-actually-free-open-no-auth-needed-apis/",
    "rapidapi":           "https://rapidapi.com",
    "freellm.net":        "https://freellm.net",
}
```

---

## 📊 400 VÍDEOS — ESTRUTURA COMPLETA

### Resumo

```
20 séries × 10 episódios × 2 formatos = 400 vídeos
  200 Shorts (58s)  → gancho + curiosity gap → drive para o Long
  200 Longs (15min) → script Psych2Go completo → mid-rolls

Tabela Supabase: video_plan_400
IDs pipeline existentes:
  Shorts: 682-712 (9 renderizados)
  Longs:  713-721 (9 scripts prontos, #713 renderizando)
```

### As 20 Séries com Personagens

```python
SERIES = {
    # slug: (personagem, descrição, hashtags)
    "narcisismo":    ("Laís",   "32a professora", "#narcisismo #relacionamentotoxico"),
    "apego":         ("Rafael", "28a designer",   "#apegoansioso #apego"),
    "gaslighting":   ("Ana",    "34a advogada",   "#gaslighting #manipulacao"),
    "infancia":      ("Você",   "infância difícil","#traumadeinfancia #familia"),
    "ansiedade":     ("Sofia",  "28a analista",   "#ansiedade #ansiedadealtofuncional"),
    "depressao":     ("Carla",  "33a consultora", "#depressaosilenciosa"),
    "limites":       ("Clara",  "30a diz sim",    "#limites #limitessaudaveis"),
    "autoestima":    ("Marcos", "29a se sabota",  "#autoestima #autossabotagem"),
    "relacionamentos":("Camila","repete padrão",  "#relacionamentotoxico"),
    "codependencia": ("Paula",  "precisa salvar", "#codependencia"),
    "impostor":      ("Marina", "recém promovida","#sindromedoimpostor"),
    "abandono":      ("Leo",    "medo de ser deixado","#medodeabandono"),
    "cura":          ("Todos",  "jornada não linear","#cura #curaemocional"),
    "amorporprio":   ("Você",   "cresceu demais", "#amorporprio"),
    "trauma":        ("Lucas",  "corpo parou",    "#trauma #TEPT"),
    "manipulacao":   ("Ana",    "1 ano terapia",  "#manipulacao #narcisismo"),
    "cerebro":       ("Lucas",  "4 anos colapso", "#neurociencia #cerebro"),
    "vicoemocional": ("Camila", "química do amor","#vicoemocional"),
    "familia":       ("Você",   "sempre problema","#familiadisfuncional"),
    "resiliencia":   ("Todos",  "fundo do poço",  "#resiliencia"),
}
```

### Arco de 10 Episódios (LOCKED)

```
E01 GANCHO       → O Problema Que Ninguém Nomeia (viral máximo)
E02 PROBLEMA     → Por Que É Mais Sério (profundidade)
E03 CIENCIA      → O Que a Ciência Diz (autoridade + pesquisadores)
E04 CUSTO        → O Custo Invisível (urgência)
E05 VIRADA       → A Virada (esperança + mid-roll E03/06/09)
E06 FERRAMENTA   → O Que Realmente Funciona (valor prático)
E07 PRATICA      → Como Colocar em Prática Hoje (ação)
E08 RECAIDA      → Quando Você Regride (normalização)
E09 TRANSFORMACAO→ Como Fica Depois da Cura (aspiração)
E10 FINAL        → Fechamento + Próxima Série (cliffhanger)
```

### Workflow de Publicação Short ↔ Long

```
1. Renderizar Long → publicar → copiar YouTube ID
2. UPDATE content_pipeline SET related_video_id='[YT_ID]' WHERE id=[LONG_ID]
3. Renderizar Short (script já embute link do Long na descrição)
4. Publicar Short
5. YouTube Studio → Short → "Vídeo relacionado" → ID do Long
6. YouTube detecta keywords + related_video → exibe Long embaixo do Short
7. Horário: 18-20h BR | Canal: UCyCkIpsVgME9yCj_oXJFheA
```

---

## 🎭 PIPELINE ÁUDIO V31 — PARÂMETROS DEFINITIVOS

```python
# Tipos e parâmetros (exag, cfg, sil_pre_s, sil_pos_s)
TIPOS_AUDIO = {
    "IMPACTO":    (0.96, 0.09, 1.0, 1.6),  # < 35 chars: "Ele CHORA."
    "CHORO":      (0.95, 0.08, 0.5, 1.8),  # dor real, voz carregada
    "REVELACAO":  (0.93, 0.10, 0.7, 1.4),  # "Isso tem NOME."
    "GANCHO":     (0.88, 0.12, 0.0, 0.8),  # abertura com personagem
    "PAUSA":      (0.87, 0.13, 0.4, 1.1),  # "..." suspense
    "CTA":        (0.74, 0.26, 0.9, 0.0),  # SALVA agora
    "NORMAL":     (0.82, 0.17, 0.0, 0.65), # narrativa padrão
}

# Noise gate por segmento (NOVO V31)
GATE_SEGMENTO = "agate=threshold=0.028:ratio=8000:attack=1:release=60"
# Gate final duplo
GATE_FINAL    = "highpass=f=80,agate=threshold=0.028:ratio=8000:attack=2:release=50"
# Fade in/out (sem click)
FADE_IN_MS, FADE_OUT_MS = 30, 60
# Silêncio limpo (zeros digitais absolutos)
SILENCE_CODEC = "pcm_s16le"

# Verificação obrigatória (deve retornar -inf):
# ffmpeg -i audio.wav -af "astats=metadata=1" -f null - 2>&1 | grep "RMS trough"
```

---

## 🖼️ SINCRONIZAÇÃO IMAGEM-ÁUDIO V31

```python
# Cada imagem = exatamente a cena da frase sendo dita

DANIELA = "kawaii chibi anime girl, short dark bob hair, mint-green blouse, gold psi pin, warm smile"
SARA    = "kawaii chibi anime girl, wavy auburn hair, round glasses, yellow cardigan, emotional eyes"
MARCOS  = "kawaii chibi anime man, styled dark hair, navy blazer, charming calculating smile"
JULIA   = "kawaii chibi anime girl, curly dark hair, orange sweater, warm caring expression"
ANA     = "kawaii chibi anime woman, dark bun, white lab coat, clipboard, authoritative calm"
STYLE   = "Psych2Go anime flat illustration, soft cream background #F5F0E8, pastel colors, clean line art, no text, no watermarks"

def prompt_for_frase(frase):
    t = frase.lower()
    if any(k in t for k in ["grita","perigoso","calculista","controle","manipulador"]):
        return MARCOS + " villainous, dark aura, sinister smile, " + STYLE
    elif any(k in t for k in ["chora","triste","culpada","errada","machucada","desmoronou"]):
        return SARA + " crying, confused, hurt, emotional, " + STYLE
    elif any(k in t for k in ["salva","canal","assiste","sino","vídeo completo"]):
        return DANIELA + " pointing to camera, warm smile, golden bell 🔔, " + STYLE
    elif any(k in t for k in ["harvard","ciência","pesquisa","estudo","neurológ"]):
        return ANA + " pointing at whiteboard, scientific diagram, " + STYLE
    elif any(k in t for k in ["isso tem nome","isso se chama","mecanismo","padrão"]):
        return ANA + " with labeled diagram, writing on board, " + STYLE
    elif any(k in t for k in ["você conhece","conheça","imagine"]):
        return DANIELA + " warm, storyteller pose, inviting, " + STYLE
    else:
        return DANIELA + " speaking directly, eye contact, engaged, " + STYLE
```

---

## 📋 SCRIPTS PSYCH2GO V31 (PADRÃO)

```
ESTRUTURA OBRIGATÓRIA:
1. "Você conhece [Nome]? [Cena específica de dor real]" (GANCHO)
2. Revelação parcial → entrega 70% do valor (CHORO/REVELACAO)
3. "Isso tem NOME." (REVELACAO)
4. Curiosity gap: "No vídeo completo eu mostro [X ESPECÍFICO]" (NORMAL)
5. "SALVA agora para não perder." (CTA)

PESQUISADORES REAIS OBRIGATÓRIOS:
  - Craig Malkin (Harvard) → narcisismo
  - Bessel van der Kolk (Harvard) → trauma
  - Mary Ainsworth (Johns Hopkins) → apego
  - John Gottman (UWashington) → relacionamentos
  - Daniel Siegel (UCLA) → neurociência, integração
  - Brené Brown (UTexas) → vulnerabilidade, vergonha
  - Kristin Neff (UTexas) → self-compassion
  - Lindsay Gibson → família emocionalmente imatura
  - Robin Stern (Yale) → gaslighting
  - Helen Fisher (Rutgers) → química do amor, vício emocional
  - Pauline Clance → síndrome do impostor
  - Valerie Young (Harvard) → tipos de impostor
  - Herbert Benson (Harvard) → estresse crônico
  - Amy Arnsten (Yale) → estresse e córtex pré-frontal
  - Stephen Porges → teoria polivagal
  - Jennifer Freyd → traição de confiança
  - Mark Hyman → depressão e inflamação
  - Kelly Brogan → psiquiatria integrativa
```

---

## 🔐 CREDENCIAIS STATUS

```
✅ ATIVAS:
  GH_PAT              → github.com (tafita81)
  SUPABASE_SERVICE_KEY → supabase.com/project/tpjvalzwkqwttvmszvie
  SUPABASE_ANON_KEY    → mesmo projeto
  GROQ_API_KEY         → console.groq.com
  NVIDIA_API_KEY       → build.nvidia.com
  OPENAI_API_KEY       → platform.openai.com
  HF_TOKEN             → huggingface.co/settings/tokens

⚠️ QUOTA VARIÁVEL:
  ELEVENLABS_API_KEY   → quota pode estar esgotada → usar Chatterbox

❌ FALTANDO (criar grátis):
  GEMINI_API_KEY       → aistudio.google.com (1.500 req/dia)
  YOUTUBE_OAUTH        → console.cloud.google.com (psidanielacoelho1982@gmail.com)
  INSTAGRAM_TOKEN      → developers.facebook.com
  TIKTOK_TOKEN         → developers.tiktok.com
  CEREBRAS_API_KEY     → cloud.cerebras.ai (1M tokens/dia)
  OPENROUTER_API_KEY   → openrouter.ai

COMO CRIAR GEMINI KEY (grátis):
  1. https://aistudio.google.com
  2. "Get API key" → "Create API key"
  3. Copiar key → GitHub Settings → Secrets → GEMINI_API_KEY

COMO CRIAR YOUTUBE OAUTH:
  1. https://console.cloud.google.com → Novo projeto
  2. APIs → Habilitar YouTube Data API v3
  3. Credenciais → OAuth 2.0 → Tipo: Aplicativo Web
  4. URI redirect: http://localhost:8080
  5. Baixar credentials.json → executar flow OAuth
  6. Salvar refresh_token como YOUTUBE_REFRESH_TOKEN
```

---

## 💡 APIS PSICOLOGIA / SAÚDE MENTAL / QUOTES

```python
# APIs relevantes do diretório public-apis para o pipeline:

APIS_RELEVANTES = {
    # Frases/Citações (para enriquecer scripts)
    "quotable":    "https://api.quotable.io/random?tags=motivational",
    "zenquotes":   "https://zenquotes.io/api/random",   # sem key
    "quotegarden": "https://quote-garden.herokuapp.com/api/v3/quotes/random",

    # Saúde Mental
    "opentdb":     "https://opentdb.com/api.php?amount=10&category=17",  # trivia/ciência

    # Clima (para contexto de vídeo)
    "openweather": "https://api.openweathermap.org/data/2.5/weather",

    # Dados Brasileiros Públicos
    "ibge":        "https://servicodados.ibge.gov.br/api/v1/",
    "brasil.io":   "https://brasil.io/api/",

    # Análise de Texto / NLP (para scripts)
    "meaningcloud": "https://api.meaningcloud.com/sentiment-2.1",  # sentiment
    "twinword":    "https://api.twinword.com/api/text/sentiment/",

    # Pesquisa / Academico
    "semantic_scholar": "https://api.semanticscholar.org/graph/v1/",  # sem key
    "pubmed":      "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/",  # sem key
    "crossref":    "https://api.crossref.org/works",  # sem key, papers científicos
    "openalex":    "https://api.openalex.org/works",  # sem key, 250M papers

    # Busca de notícias (viral research)
    "newsapi":     "https://newsapi.org/v2/",   # 100 req/dia free
    "gnews":       "https://gnews.io/api/v4/",  # 100 req/dia free
    "guardian":    "https://content.guardianapis.com/search",  # sem key para leitura

    # Google Trends (viral research)
    "pytrends":    "pip install pytrends  # sem key, não oficial",
}

# Como usar para o pipeline:
# 1. Buscar quotes de pesquisadores reais para enriquecer scripts
# 2. Buscar papers sobre narcisismo/apego/trauma no OpenAlex/PubMed
# 3. Monitorar trending topics de psicologia via Google Trends
# 4. Análise de sentimento dos scripts para calibrar emoção
```

---

## 📊 ESTADO ATUAL DOS 400 VÍDEOS

```
SHORTS RENDERIZADOS (9/200):
  #683 Narcisismo (Laís)              ✅ https://tpjvalzwkqwttvmszvie.supabase.co/storage/v1/object/public/videos/mp4s/v683_cb_vB_1779287869.mp4
  #682 Vício Emocional (Rafael)       ✅ https://tpjvalzwkqwttvmszvie.supabase.co/storage/v1/object/public/videos/mp4s/v682_cb_vB_1779336187.mp4
  #684 Ansiedade (Sofia)              ✅ https://tpjvalzwkqwttvmszvie.supabase.co/storage/v1/object/public/videos/mp4s/v684_cb_vB_1779336256.mp4
  #688 Neurociência (Lucas)           ✅ https://tpjvalzwkqwttvmszvie.supabase.co/storage/v1/object/public/videos/mp4s/v688_cb_vB_1779336197.mp4
  #689 Síndrome do Impostor (Marina)  ✅ https://tpjvalzwkqwttvmszvie.supabase.co/storage/v1/object/public/videos/mp4s/v689_cb_vB_1779336216.mp4
  #701 Depressão Silenciosa (Carla)   ✅ https://tpjvalzwkqwttvmszvie.supabase.co/storage/v1/object/public/videos/mp4s/v701_cb_vB_1779336191.mp4
  #710 Gaslighting (Juliana)          ✅ https://tpjvalzwkqwttvmszvie.supabase.co/storage/v1/object/public/videos/mp4s/v710_cb_vB_1779336044.mp4
  #711 Vício/Ex (Camila)              ✅ https://tpjvalzwkqwttvmszvie.supabase.co/storage/v1/object/public/videos/mp4s/v711_cb_vB_1779336293.mp4
  #712 Família (Você)                 ✅ https://tpjvalzwkqwttvmszvie.supabase.co/storage/v1/object/public/videos/mp4s/v712_cb_vB_1779336183.mp4

LONGS COM SCRIPT (9/200):
  #713 Narcisismo      → renderizando (run 26206616893)
  #714 Vício Emocional S01
  #715 Ansiedade
  #716 Neurociência
  #717 Impostor
  #718 Depressão
  #719 Gaslighting
  #720 Vício Emocional S02
  #721 Feridas de Infância

PRÓXIMA AÇÃO:
  1. Disparar Longs #714-#721 quando #713 aprovar
  2. Configurar YouTube OAuth
  3. Publicar #683 Long + Short em sequência
```

---

## 📈 REFERÊNCIAS VIRAIS (VIRAL MIRROR)

```python
# Tabela Supabase: viral_videos_reference
# Top referências por views:

VIRAL_REFS = [
    ("Psych2Go Covert Narcissist",       "28M views", "youtube.com/watch?v=..."),
    ("Psych2Go Abandonment",             "22M views"),
    ("Psych2Go Childhood Trauma",        "19M views"),
    ("Psych2Go Gaslighting",             "15M views"),
    ("Huberman Anxiety Protocol",        "12M views"),
    ("Psych2Go Signs of Trauma",         "10M views"),
    ("Ali Abdaal Impostor Syndrome",     "8M views"),
]

# Fórmulas de título viral (baseadas nas refs):
FORMULAS = {
    "N sinais + condição invisível":   "CTR 8-12%  → 'X Sinais de [Y] Que Ninguém Percebe'",
    "Não é X, é Y":                   "CTR 10-15% → 'Não é Preguiça, É [Condição Real]'",
    "Revelação perigo oculto":         "CTR 12-18% → '[X] Que Parece [Y] Mas É [Z]'",
    "Você conhece [Nome]":             "CTR 15-20% → Hook Psych2Go estilo",
}
```

---

## 💰 ESTRATÉGIA R$50K/MÊS

```
RPM psicologia BR: R$10-16 (AdSense)
Meta: 3.5M views/mês × R$15 = R$52.500/mês

ROADMAP:
  Mês 1-2:  0→1K subs (Shorts virais + ads pagos mínimos)
  Mês 3-4:  10K subs → R$3K/mês
  Mês 5-6:  50K subs → R$10K/mês
  Mês 7-8:  100K subs → R$20K/mês
  Mês 9-10: 300K subs → R$50K/mês ✅

FONTES DE RECEITA:
  1. AdSense mid-rolls Longs (E03/E06/E09 = 3/6/9min) → principal
  2. Shorts → crescimento de inscritos (gratuito via algoritmo)
  3. Cursos/ebook futuro → R$50-200 ticket
  4. Afiliados psicologia → R$15-50/conversão

CUSTO ATUAL: R$0/mês (tudo gratuito)
```

---

## 🔗 TODOS OS LINKS IMPORTANTES

```
NOSSO PROJETO:
  GitHub:         https://github.com/tafita81/Repovazio
  Vercel:         https://repovazio.vercel.app
  Supabase:       https://app.supabase.com/project/tpjvalzwkqwttvmszvie
  Canal YT:       https://youtube.com/@psidanielacoelho
  Hub:            https://repovazio.vercel.app/hub.html
  Painel 400:     https://repovazio.vercel.app/painel-400.html

CONSOLES / DASHBOARDS:
  GitHub Actions: https://github.com/tafita81/Repovazio/actions
  Groq Console:   https://console.groq.com
  NVIDIA Build:   https://build.nvidia.com
  AI Studio:      https://aistudio.google.com
  OpenRouter:     https://openrouter.ai/models?q=free
  Cerebras:       https://cloud.cerebras.ai
  HuggingFace:    https://huggingface.co/models
  ElevenLabs:     https://elevenlabs.io/app
  YouTube Studio: https://studio.youtube.com
  GCloud Console: https://console.cloud.google.com

APIs SEM KEY:
  Pollinations:   https://image.pollinations.ai/prompt/[PROMPT]
  Pollinations Gen: https://gen.pollinations.ai
  ZSky AI:        https://zsky.ai/api/v1
  Quotable:       https://api.quotable.io/random
  ZenQuotes:      https://zenquotes.io/api/random
  OpenAlex:       https://api.openalex.org/works
  CrossRef:       https://api.crossref.org/works
  PubMed:         https://eutils.ncbi.nlm.nih.gov/entrez/eutils/
  Brasil.io:      https://brasil.io/api/

DIRETÓRIOS DE APIS:
  public-apis:    https://github.com/public-apis/public-apis
  publicapis.dev: https://publicapis.dev
  public-apis.io: https://public-apis.io
  publicapis.io:  https://publicapis.io
  public-api-lists: https://github.com/public-api-lists/public-api-lists
  mixedanalytics: https://mixedanalytics.com/blog/list-actually-free-open-no-auth-needed-apis/
  rapidapi:       https://rapidapi.com
  freellm.net:    https://freellm.net
  no-cost-ai:     https://github.com/zebbern/no-cost-ai

DOCS CHAVES:
  Pollinations API Docs: https://github.com/pollinations/pollinations/blob/main/APIDOCS.md
  Qwen3-TTS GitHub:      https://github.com/QwenLM/Qwen3-TTS
  Chatterbox GitHub:     https://github.com/resemble-ai/chatterbox
  YouTube API:           https://developers.google.com/youtube/v3
  Edge TTS GitHub:       https://github.com/rany2/edge-tts
```
