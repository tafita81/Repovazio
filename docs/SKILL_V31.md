---
name: psicologia-doc-v27
description: Use esta SKILL sempre que o usuário mencionar: psicologia.doc, repovazio, Daniela Coelho, @psidanielacoelho, canal YouTube psicologia, viral, cérebro autônomo, tokens sociais, Instagram, TikTok, WhatsApp grupos, monetização, 1000 subs, crescimento, setup tokens, espelhamento viral.
version: 31.0
date: 2026-05-21
---

# SKILL — psicologia.doc V31 — APIs COMPLETAS + 400 VÍDEOS

---

## ⚠️ REGRA DE OURO

```
NUNCA liberar vídeo sem testar #683 primeiro.
1. GitHub Action video_id=683, voice_version=B
2. Verificar áudio: RMS trough=-inf, silêncio limpo
3. Verificar imagens: cada frame reflete a frase sendo dita
4. SÓ após aprovação: disparar os demais
```

---

## INFRA CORE

```
Supabase: tpjvalzwkqwttvmszvie | Vercel: repovazio.vercel.app | GitHub: tafita81/Repovazio
Canal ATIVO:   UCyCkIpsVgME9yCj_oXJFheA · @psidanielacoelho · psidanielacoelho1982@gmail.com
Canal ⛔ BLOQUEADO: UCSH63tBfY6wEIdkC4u4zKdg — REMOVIDO 2026-05-07, NUNCA publicar
Script Short V31: scripts/render_short_george.py
Script Long V31:  scripts/render_long_15min.py
Workflow Short: .github/workflows/render-short-george.yml (45min timeout)
Workflow Long:  .github/workflows/render-long-15min.yml (120min timeout)
Painel 400: https://repovazio.vercel.app/painel-400.html
```

---

## 🎤 APIs DE VOZ — COMPLETO (ATUALIZADO MAI/2026)

### P1 — PADRÃO ATUAL: Chatterbox Multilingual (MIT, grátis, ilimitado)

```python
# GitHub: resemble-ai/chatterbox (MIT License)
# pip install chatterbox-tts torch --index-url https://download.pytorch.org/whl/cpu
from chatterbox.tts import ChatterboxMultilingualTTS
model = ChatterboxMultilingualTTS.from_pretrained(device="cpu")
wav = model.generate(texto, audio_prompt_path=GEORGE_REF,
    language_id="pt", exaggeration=0.96, cfg_weight=0.09)

# Referência George (14s limpos):
GEORGE_REF = "https://tpjvalzwkqwttvmszvie.supabase.co/storage/v1/object/public/videos/mp4s/v683_george_1779065193.mp4"
```

### P2 — Qwen3-TTS (Alibaba, Apache 2.0, PT-BR, grátis, ilimitado)

```python
# GitHub: QwenLM/Qwen3-TTS (0.6B e 1.7B params, Apache 2.0)
# Suporta: PT, EN, ZH, JA, KO, DE, FR, RU, ES, IT
# Voice cloning com 3s de áudio + instruction control
# 97ms latency (streaming), supera ElevenLabs em qualidade
# pip install torch transformers qwen-tts
# HuggingFace: Qwen/Qwen3-TTS-0.6B | Qwen/Qwen3-TTS-1.7B

from transformers import AutoModelForSpeechSeq2Seq
# Alternativa via Pollinations: https://gen.pollinations.ai/audio
# Alternativa via HF Inference API: api-inference.huggingface.co
```

### P3 — Kokoro TTS (MIT, 82M params, PT-BR, offline)

```python
# GitHub: hexgrad/kokoro (MIT License)
# 54 vozes, 9 idiomas incluindo pt-BR
# pip install kokoro-onnx soundfile
from kokoro_onnx import Kokoro
kokoro = Kokoro("kokoro-v1.0.onnx", "voices.bin")
samples, sample_rate = kokoro.create(texto, voice="bf_emma", lang="pt-br")
```

### P4 — ElevenLabs George (JBFqnCBsd6RMkjVDRZzb) — quota variável

```python
# Usar se ELEVENLABS_API_KEY válida com quota
# stability=0.20, similarity_boost=0.85, style=0.70, speed=1.0
# ~32K chars/mês free tier (reseta ~Jun/2026)
```

### P5 — Edge TTS (Microsoft, grátis, ilimitado, sem API key)

```python
# pip install edge-tts
# Vozes BR: ThalitaMultilingualNeural (mais emocional — PADRÃO LONG)
#           FranciscaNeural (forte entonação)
#           AntonioNeural (fallback emergência)
import edge_tts
c = edge_tts.Communicate(texto, voice="pt-BR-ThalitaMultilingualNeural", rate="+32%")
await c.save("output.mp3")
```

### P6 — Pollinations Audio (grátis, sem key)

```python
# Endpoint: https://gen.pollinations.ai/audio
# Vozes: alloy, echo, fable, onyx, nova, shimmer, coral, verse, ballad, ash, sage
import requests
r = requests.post("https://gen.pollinations.ai/audio", json={
    "model": "openai-audio", "voice": "nova",
    "input": texto, "response_format": "mp3"
})
```

### P7 — F5-TTS (MIT, zero-shot cloning)

```python
# GitHub: SWivid/F5-TTS (MIT License)
# Clonagem zero-shot com 5-10s de referência
# pip install f5-tts
# Suporta português com sample de referência
```

### P8 — IndexTTS (Bilibili, Apache 2.0, zero-shot)

```python
# GitHub: index-tts/IndexTTS (Apache 2.0)
# Bilibili research, zero-shot cloning, multilingual
# pip install indextts
```

### P9 — VoxCPM 1.5 (MIT, voice cloning avançado)

```python
# GitHub: VoxCPM/VoxCPM (MIT License)
# Clone automático + transcrição automática
# Exige ~8GB VRAM mas suporta CPU fallback
```

### P10 — OmniVoice (600+ idiomas, multilingual extremo)

```python
# GitHub: OmniVoice/OmniVoice
# 600+ idiomas/dialetos — maior cobertura linguística
# Use para localização futura
```

---

## 🖼️ APIs DE IMAGEM — COMPLETO

### P1 — Pollinations FLUX (PADRÃO, grátis, sem key)

```python
# Endpoint: https://image.pollinations.ai/prompt/{prompt}
# Modelos: flux, flux-realism, flux-anime, flux-3d, gptimage, seedream, kontext
# Tier free: 1 req/15s (anônimo) | Seed: 1 req/5s (registro grátis)
import urllib.parse
url = f"https://image.pollinations.ai/prompt/{urllib.parse.quote(prompt)}"
url += "?width=576&height=1024&model=flux&seed=42&nologo=true"

# Unified endpoint (NOVO 2026):
url = f"https://gen.pollinations.ai/image/{urllib.parse.quote(prompt)}"
```

### P2 — ZSky AI (grátis, ilimitado, 1080p, sem key)

```python
# https://zsky.ai/api/v1/image/generate (sem API key no free tier)
import requests
r = requests.post("https://zsky.ai/api/v1/image/generate", json={
    "prompt": prompt, "resolution": "1080p", "style": "cinematic"
})
# Inclui watermark ZSky no free tier
```

### P3 — HuggingFace Inference (grátis, rate limited)

```python
# https://api-inference.huggingface.co/models/{model}
# Modelos: black-forest-labs/FLUX.1-schnell, stabilityai/stable-diffusion-xl
import requests
headers = {"Authorization": f"Bearer {HF_TOKEN}"}
r = requests.post(
    "https://api-inference.huggingface.co/models/black-forest-labs/FLUX.1-schnell",
    headers=headers, json={"inputs": prompt}
)
```

### P4 — Pixazo (grátis, FLUX/SDXL, registro gratuito)

```python
# https://pixazo.ai/api — registro grátis, sem cartão
# Modelos free: Flux Schnell, SD1.5, SDXL
```

### P5 — Puter.js (grátis, ilimitado, sem key — user-pays model)

```javascript
// CDN: <script src="https://cdn.puter.com/puter.js"></script>
// Modelos: GPT Image, DALL-E 3, Gemini 2.5 Flash, Flux.1, SD3, SDXL
const img = await puter.ai.txt2img("prompt aqui");
```

### P6 — Banco Supabase PRIMÁRIO (125+ imagens kawaii, <2s)

```python
SB_URL = "https://tpjvalzwkqwttvmszvie.supabase.co"
TABLE  = "image_bank"
# Personagens: daniela, sara, marcos, julia, ana
# Consultar: requests.get(f"{SB_URL}/rest/v1/image_bank?character_slug=eq.{char}")
```

---

## 🎬 APIs DE VÍDEO — COMPLETO

### P1 — Pipeline interno (PADRÃO — Ken Burns + FFmpeg)

```python
# Script: scripts/render_short_george.py (Short 58s)
# Script: scripts/render_long_15min.py (Long 15min)
# Ken Burns: zoom 0/4/8% via Pillow + FFmpeg
# Custo: $0, ilimitado
```

### P2 — ZSky AI Video (grátis, 1080p + áudio, sem key)

```python
# https://zsky.ai/api/v1/video/generate
import requests
r = requests.post("https://zsky.ai/api/v1/video/generate", json={
    "prompt": prompt, "duration": 5, "resolution": "1080p", "audio": True
})
# Watermark ZSky no free tier | Uso comercial incluído
# Retorna MP4 direto ou callback via webhook
```

### P3 — Wan2.1 / CogVideoX (HuggingFace, open source)

```python
# HuggingFace Spaces: https://huggingface.co/spaces/Wan-AI/Wan2.1
# CogVideoX: THUDM/CogVideoX-5b (Apache 2.0)
# Geração de vídeo a partir de texto ou imagem
```

### P4 — Open-Generative-AI (MIT, auto-hospedado, 200+ modelos)

```python
# GitHub: Anil-matcha/Open-Generative-AI (MIT License)
# Flux, Midjourney-style, Kling, Sora-style, Veo-style
# Self-hosted Next.js + API Muapi
```

---

## 🤖 APIs DE LLM — COMPLETO (RANKING POR CUSTO/QUALIDADE)

### Stack LLMRouter V4 (pipeline atual)

```python
PROVIDERS = {
    "nvidia":  ("https://integrate.api.nvidia.com/v1",       "deepseek-ai/deepseek-v4-pro"),
    "nvidia2": ("https://integrate.api.nvidia.com/v1",       "meta/llama-3.3-70b-instruct"),
    "groq":    ("https://api.groq.com/openai/v1",            "llama-3.3-70b-versatile"),
    "openai":  ("https://api.openai.com/v1",                  "gpt-4o-mini"),
}
# Fallback automático: nvidia → nvidia2 → groq → openai
```

### APIs LLM Gratuitas Permanentes (mai/2026)

```python
FREE_LLM_APIS = {
    # Sem cartão de crédito, permanentes
    "groq": {
        "base_url": "https://api.groq.com/openai/v1",
        "models": ["llama-3.3-70b-versatile", "llama-4-maverick", "deepseek-r1-distill-llama-70b"],
        "limits": "14.400 req/dia (varia por modelo)",
        "speed": "315 tokens/s (mais rápido disponível)",
        "key": "GROQ_API_KEY (grátis em console.groq.com)",
    },
    "nvidia_nim": {
        "base_url": "https://integrate.api.nvidia.com/v1",
        "models": ["deepseek-v4-pro", "meta/llama-3.3-70b", "qwen3-coder", "mistral-large"],
        "limits": "40 req/min, sem limite diário de tokens",
        "key": "NVIDIA_API_KEY (grátis em build.nvidia.com, exige telefone)",
    },
    "google_ai_studio": {
        "base_url": "https://generativelanguage.googleapis.com/v1beta/openai/",
        "models": ["gemini-2.5-flash", "gemini-2.5-pro", "gemini-3-flash", "gemma-3"],
        "limits": "1.500 req/dia (Gemini 2.5 Flash), 250K tokens/min",
        "key": "GEMINI_API_KEY (grátis em aistudio.google.com, sem cartão)",
    },
    "openrouter": {
        "base_url": "https://openrouter.ai/api/v1",
        "models": ["meta-llama/llama-3.3-70b-instruct:free", "deepseek/deepseek-r1:free",
                   "qwen/qwen3-235b:free", "mistralai/mistral-7b-instruct:free"],
        "limits": "50 req/dia (sem compra), 1.000 req/dia (com $10 único)",
        "key": "OPENROUTER_API_KEY (grátis em openrouter.ai)",
    },
    "cerebras": {
        "base_url": "https://api.cerebras.ai/v1",
        "models": ["llama-3.3-70b", "deepseek-r1", "openai/gpt-oss-120b"],
        "limits": "1M tokens/dia (MUITO generoso)",
        "key": "CEREBRAS_API_KEY (grátis em cloud.cerebras.ai)",
    },
    "mistral": {
        "base_url": "https://api.mistral.ai/v1",
        "models": ["mistral-small-latest", "codestral-2501", "mistral-large"],
        "limits": "1B tokens/mês",
        "key": "MISTRAL_API_KEY (grátis em console.mistral.ai)",
    },
    "cloudflare": {
        "base_url": "https://api.cloudflare.com/client/v4/accounts/{id}/ai/v1",
        "models": ["llama-3.3-70b", "deepseek-r1", "gpt-oss-120b", "qwen3-coder"],
        "limits": "10K neurons/dia",
        "key": "CF_API_TOKEN (grátis em dash.cloudflare.com)",
    },
    "pollinations_llm": {
        "base_url": "https://gen.pollinations.ai/v1",
        "models": ["openai-large", "claude", "gemini", "deepseek", "qwen3-coder"],
        "limits": "sem chave para uso básico (1 req/15s anônimo)",
        "key": "Sem key (ou registrar em auth.pollinations.ai para mais)",
    },
    "github_models": {
        "base_url": "https://models.inference.ai.azure.com",
        "models": ["gpt-5", "gpt-4.1", "gpt-4o", "o4-mini", "Llama-3.3-70B"],
        "limits": "50 chat + 2K completions/mês (Copilot free tier)",
        "key": "GITHUB_TOKEN (grátis em github.com/settings/tokens)",
    },
    "huggingface": {
        "base_url": "https://api-inference.huggingface.co/v1",
        "models": ["meta-llama/Llama-3.3-70B-Instruct", "Qwen/Qwen3-235B-A22B"],
        "limits": "2 req/min anônimo, 1.000 req/hora com key grátis",
        "key": "HF_TOKEN (grátis em huggingface.co/settings/tokens)",
    },
    "sambanova": {
        "base_url": "https://api.sambanova.ai/v1",
        "models": ["Meta-Llama-3.1-405B", "DeepSeek-R1-671B", "Qwen3-235B"],
        "limits": "$5 free por 3 meses (alto volume)",
        "key": "SAMBANOVA_API_KEY (grátis em cloud.sambanova.ai)",
    },
}
```

---

## 📺 YOUTUBE API — COMPLETO

### YouTube Data API v3 (oficial, grátis)

```python
# Quota: 10.000 unidades/dia (grátis)
# Upload = 1.600 unidades → 6 vídeos/dia por projeto
# Solução: criar múltiplos projetos Google Cloud (cada um = 10K/dia)

YOUTUBE_API = {
    "base_url": "https://www.googleapis.com/youtube/v3",
    "upload_url": "https://www.googleapis.com/upload/youtube/v3/videos",
    "analytics_url": "https://youtubeanalytics.googleapis.com/v2",
    "quota_por_dia": 10000,
    "custo_upload": 1600,  # unidades por vídeo
    "custo_lista": 1,      # unidades por item
    "max_uploads_dia": 6,  # com quota padrão
    "auth": "OAuth2 (psidanielacoelho1982@gmail.com) — PENDENTE",
    "canal_id": "UCyCkIpsVgME9yCj_oXJFheA",
}

# PENDENTE: YouTube OAuth workflow
# 1. Gerar credentials.json em console.cloud.google.com
# 2. Habilitar YouTube Data API v3
# 3. OAuth consent screen → tipo externo
# 4. Salvar refresh_token como GitHub Secret YOUTUBE_REFRESH_TOKEN
# 5. Canal: psidanielacoelho1982@gmail.com

# Linking Short → Long (YouTube Studio):
# Short: youtube_studio → Detalhes → "Vídeo relacionado" → ID do Long
# Ambos devem ter keywords da série no título e descrição
```

### Alternativas YouTube (sem quota)

```python
YOUTUBE_ALTERNATIVES = {
    "yt-dlp": {
        "github": "yt-dlp/yt-dlp",
        "uso": "Download/análise de vídeos, sem API key",
        "pip": "pip install yt-dlp",
        "cmd": "yt-dlp --get-info [URL]",
    },
    "pytube": {
        "pip": "pip install pytube",
        "uso": "Metadata de vídeos públicos sem API key",
    },
    "youtube-transcript-api": {
        "pip": "pip install youtube-transcript-api",
        "uso": "Transcrições de vídeos sem API key",
    },
}
```

---

## 🔧 REPOSITÓRIOS GITHUB ESSENCIAIS

```python
REPOS = {
    # TTS
    "chatterbox":         "resemble-ai/chatterbox",          # PADRÃO ATUAL
    "qwen3-tts":          "QwenLM/Qwen3-TTS",                # PRÓXIMO UPGRADE
    "kokoro":             "hexgrad/kokoro",                   # Leve, offline
    "f5-tts":             "SWivid/F5-TTS",                   # Zero-shot PT
    "indextts":           "index-tts/IndexTTS",               # Bilibili, Apache
    "chatterbox-server":  "devnen/Chatterbox-TTS-Server",     # OpenAI-compatible
    "tts-story":          "Xerophayze/TTS-Story",             # 12 engines, API
    "voicebox":           "jamiepine/voicebox",               # 7 engines unified

    # LLM FREE
    "awesome-free-llm":   "amardeeplakshkar/awesome-free-llm-apis",
    "free-llm-directory": "open-free-llm-api/awesome-freellm-apis",
    "no-cost-ai":         "zebbern/no-cost-ai",              # 80+ serviços
    "free-ai-tools":      "ShaikhWarsi/free-ai-tools",        # Tabela atualizada

    # IMAGEM/VÍDEO
    "pollinations":       "pollinations/pollinations",         # PADRÃO IMAGEM
    "open-generative-ai": "Anil-matcha/Open-Generative-AI",   # 200+ modelos
    "stable-diffusion":   "AUTOMATIC1111/stable-diffusion-webui", # self-hosted

    # PIPELINE
    "repovazio":          "tafita81/Repovazio",               # NOSSO REPO
    "yt-dlp":             "yt-dlp/yt-dlp",                   # YouTube utils
}
```

---

## 📊 400 VÍDEOS — ESTRUTURA COMPLETA

```
20 séries × 10 episódios × 2 formatos = 400 vídeos
- 200 Shorts (58s) → gancho + curiosity gap → drive para o Long
- 200 Longs (15min) → Psych2Go completo → mid-rolls (3/6/9/12min)

Tabela Supabase: video_plan_400
IDs pipeline existentes: 
  Shorts: 682-712 (9 prontos)
  Longs:  713-721 (9 scripts prontos, #713 renderizando)
```

### Workflow de publicação Short + Long (YouTube)

```
1. Renderizar Long (15min) via render-long-15min.yml
2. Publicar Long primeiro → copiar YouTube ID
3. UPDATE content_pipeline SET related_video_id='[ID_YT]' WHERE id=[LONG_ID]
4. Renderizar Short com o Long ID (descrição embute link automático)
5. Publicar Short via YouTube OAuth
6. YouTube Studio → Short → "Vídeo relacionado" → ID do Long
7. YouTube exibe o Long embaixo de todo Short da série automaticamente
```

### Personagens por série

```python
SERIES_CHARS = {
    "narcisismo":("Laís","32a professora"),
    "apego":("Rafael","28a designer"),
    "gaslighting":("Ana/Pedro","30a advogada"),
    "infancia":("Você","infância difícil"),
    "ansiedade":("Sofia","28a analista"),
    "depressao":("Carla","33a consultora"),
    "limites":("Clara","30a sempre diz sim"),
    "autoestima":("Marcos","29a se sabota"),
    "relacionamentos":("Camila","repete o padrão"),
    "codependencia":("Paula","precisa salvar"),
    "impostor":("Marina","35a recém promovida"),
    "abandono":("Leo","faz tudo para não ser deixado"),
    "cura":("Todos","jornada não linear"),
    "amorporprio":("Você","cresceu sendo demais"),
    "trauma":("Lucas","corpo que parou"),
    "manipulacao":("Ana","1 ano de terapia para entender"),
    "cerebro":("Lucas","4 anos até o colapso"),
    "vicoemocional":("Camila","química do amor que dói"),
    "familia":("Você","sempre foi o problema"),
    "resiliencia":("Todos","depois do fundo do poço"),
}
```

---

## 🎭 PIPELINE ÁUDIO V31 — PARÂMETROS DEFINITIVOS

```python
# Tipos semânticos e parâmetros
TIPOS_AUDIO = {
    "IMPACTO":    (0.96, 0.09, 1.0, 1.6),  # < 35 chars, pausa máxima
    "CHORO":      (0.95, 0.08, 0.5, 1.8),  # dor real, voz carregada
    "REVELACAO":  (0.93, 0.10, 0.7, 1.4),  # "Isso tem NOME."
    "GANCHO":     (0.88, 0.12, 0.0, 0.8),  # abertura de cena
    "PAUSA":      (0.87, 0.13, 0.4, 1.1),  # "..." suspense
    "CTA":        (0.74, 0.26, 0.9, 0.0),  # SALVA agora
    "NORMAL":     (0.82, 0.17, 0.0, 0.65), # narrativa padrão
}
# (exaggeration, cfg_weight, sil_pre_s, sil_pos_s)

# Noise gate por segmento (NOVO V31)
GATE_POR_SEGMENTO = "agate=threshold=0.028:ratio=8000:attack=1:release=60"
# Gate final duplo
GATE_FINAL = "highpass=f=80,agate=threshold=0.028:ratio=8000:attack=2:release=50"
# Fade in/out
FADE_IN_MS, FADE_OUT_MS = 30, 60
# Silêncio limpo (zeros digitais)
SILENCE_CODEC = "pcm_s16le"

# Verificação obrigatória
# ffmpeg -i audio.wav -af "astats=metadata=1" -f null - 2>&1 | grep "RMS trough"
# ESPERADO: "RMS trough dB: -inf" ✅
```

---

## 🖼️ SINCRONIZAÇÃO IMAGEM-ÁUDIO V31

```python
# Cada imagem = exatamente a cena da frase sendo dita
def prompt_for_frase(frase, idx, N):
    t = frase.lower()
    if any(k in t for k in ["grita","perigoso","calculista","controle","manipulador"]): 
        char = MARCOS + " villainous, dark aura, sinister smile"
    elif any(k in t for k in ["chora","triste","culpada","errada","machucada","confusa","desmoronou"]):
        char = SARA + " crying, confused, hurt, emotional"
    elif any(k in t for k in ["salva","canal","assiste","sino","vídeo completo","próxima"]):
        char = DANIELA + " pointing to camera, warm smile, golden bell 🔔"
    elif any(k in t for k in ["harvard","ciência","pesquisa","estudo","neurológ","pesquisador"]):
        char = ANA + " pointing at whiteboard, scientific diagram, authoritative"
    elif any(k in t for k in ["isso tem nome","isso se chama","chama-se","mecanismo","padrão"]):
        char = ANA + " with labeled diagram, writing on board"
    elif any(k in t for k in ["afastar","sair","terminar","ir embora","largar"]):
        char = SARA + " trying to leave, being held back"
    elif any(k in t for k in ["você conhece","conheça","imagine","pense em"]):
        char = DANIELA + " warm, inviting, storyteller pose"
    else:
        char = DANIELA + " speaking directly, engaged, eye contact"
    scene = frase[:60].lower()
    return f"{char}, {STYLE}, scene: {scene}, vertical 9:16, close-up, no text"

DANIELA = "kawaii chibi anime girl, short dark bob hair, mint-green blouse, gold psi pin, warm smile"
SARA    = "kawaii chibi anime girl, wavy auburn hair, round glasses, yellow cardigan, emotional eyes"
MARCOS  = "kawaii chibi anime man, styled dark hair, navy blazer, charming calculating smile"
ANA     = "kawaii chibi anime woman, dark bun, white lab coat, clipboard, authoritative calm"
STYLE   = "Psych2Go anime flat illustration, soft cream background #F5F0E8, pastel, clean line art"
```

---

## 📋 SCRIPTS PSYCH2GO V31 (PADRÃO)

```
Estrutura obrigatória:
1. "Você conhece [Nome]?" → cena específica de dor real
2. Revelação parcial → entrega valor (70%)
3. "Isso tem NOME." → label científico
4. Curiosity gap: "No vídeo completo eu mostro [X ESPECÍFICO]"
5. "SALVA agora para não perder."

Personagens reais por série (ver SERIES_CHARS acima)
Pesquisadores reais: Malkin/Harvard, van der Kolk, Ainsworth,
  Gottman/UWashington, Brené Brown/UTexas, Siegel/UCLA,
  Kristin Neff (self-compassion), Lindsay Gibson, Robin Stern/Yale,
  Helen Fisher/Rutgers, Pauline Clance, Valerie Young/Harvard
```

---

## 🔐 CREDENCIAIS STATUS

```
✅ GH_PAT, Vercel, Supabase, Groq, NVIDIA, OpenAI
✅ HF_TOKEN (HuggingFace — grátis)
⚠️ ELEVENLABS_API_KEY (quota esgotada → Chatterbox é padrão)
❌ FALTA: YouTube OAuth (psidanielacoelho1982@gmail.com)
❌ FALTA: GEMINI_API_KEY (criar em aistudio.google.com — grátis)
❌ FALTA: INSTAGRAM_TOKEN, TIKTOK_TOKEN
```

---

## 📊 ESTADO ATUAL DOS 400 VÍDEOS

```
Shorts renderizados (9/200):
  #683 Narcisismo (Laís) ✅
  #682 Vício Emocional (Rafael) ✅
  #684 Ansiedade (Sofia) ✅
  #688 Neurociência (Lucas) ✅
  #689 Impostor (Marina) ✅
  #701 Depressão (Carla) ✅
  #710 Gaslighting (Juliana) ✅
  #711 Vício/Ex (Camila) ✅
  #712 Família (Você) ✅

Longs em produção (scripts prontos 9/200):
  #713 Narcisismo → renderizando
  #714 Vício Emocional S01
  #715 Ansiedade
  #716 Neurociência
  #717 Impostor
  #718 Depressão
  #719 Gaslighting
  #720 Vício Emocional S02
  #721 Feridas de Infância

Status Supabase: video_plan_400 (400 registros)
```

---

## 💰 ESTRATÉGIA R$50K/MÊS

```
RPM psicologia BR: R$10-16 | Para R$50K: 3.5M views/mês
Mês 1-2:  1K subs (0→1K via Shorts virais + paid ads)
Mês 3-4:  10K subs → R$3K/mês
Mês 7-8:  100K subs → R$15K/mês
Mês 9-10: 300K subs → R$50K/mês

Shorts → crescimento de inscritos (gratuito via algoritmo)
Longs  → monetização via mid-rolls em E03/E06/E09 (3/6/9min)
Horário: 18-20h BR | Canal: UCyCkIpsVgME9yCj_oXJFheA
```

---

## 🔗 LINKS

```
Hub:           https://repovazio.vercel.app/hub.html
Vídeos prontos: https://repovazio.vercel.app/videos-prontos.html
Painel 400:    https://repovazio.vercel.app/painel-400.html
Skill doc:     https://github.com/tafita81/Repovazio/blob/main/docs/SKILL_V31.md
```
