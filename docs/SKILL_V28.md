---
name: psicologia-doc-v28
description: Use esta SKILL sempre que o usuário mencionar: psicologia.doc, repovazio, Daniela Coelho, @psidanielacoelho, canal YouTube psicologia, viral, render, vídeo, V8, padrão eterno, chibi, Gemini, Pollinations, Groq, caption, lower third, animação, monetização, 1000 subs, crescimento, shorts, longs, render_video_v8_standard.
version: 28.0
date: 2026-05-16
---

# SKILL — psicologia.doc V28 PADRÃO ETERNO (16/mai/2026)

## INFRA CORE (imutável)
- **Supabase:** `tpjvalzwkqwttvmszvie` | **GitHub:** `tafita81/Repovazio` | **Vercel:** `repovazio.vercel.app`
- **Canal ATIVO:** `@psidanielacoelho` · `UCyCkIpsVgME9yCj_oXJFheA` · login: `psidanielacoelho1982@gmail.com`
- **Canal BLOQUEADO PERMANENTEMENTE:** `UCSH63tBfY6wEIdkC4u4zKdg` (tafita81@gmail.com) — NUNCA publicar
- **GH_PAT:** `ghp_[REDACTED - usar secret GH_PAT no GitHub Actions]`
- **DB tabela principal:** `content_pipeline`

---

## PADRÃO ETERNO V8 — COMO CADA VÍDEO É CONSTRUÍDO

**Referência:** `v683_viral_v8_1778892031.mp4` (6.3MB) — o melhor vídeo, baseado nele para SEMPRE.
**Script:** `scripts/render_video_v8_standard.py`
**Workflow:** `.github/workflows/render-padrao-eterno.yml` (dispatch manual + 3x/dia automático)

### Pipeline completo (ordem exata, para sempre):

```
1. GROQ (Llama 3.3 70B) — 1 chamada gera 20 prompts:
   - frase_pt:    trecho PT-BR do roteiro desta cena
   - dur_chars:   quantos chars esta cena representa (timing preciso)
   - prompt:      inglês para Gemini/Pollinations gerar imagem chibi
   - caption_pt:  frase-chave (max 25 chars) — badge no topo da imagem
   - Última cena SEMPRE: "INSCREVA-SE AGORA 🔔"

2. IMAGENS CHIBI (4 workers paralelo):
   Primary:  Pollinations.ai Flux (grátis, sem API key, sem limite)
   Fallback: Gemini 2.0 Flash Exp (key normal do AI Studio)
   Último:   Pillow chibi programático (fallback honesto, nunca stick figures)

3. PILLOW add_overlay() em CADA imagem:
   ┌──────────────────────────────────────────────┐
   │ [BADGE BRANCO]  CAPTION_PT DA CENA  (TOPO)  │
   │                                              │
   │         [imagem chibi kawaii]                │
   │         fundo creme #F5F0E8                  │
   │         estilo Psych2Go                      │
   │                                              │
   │ ██ psi  Daniela Coelho           (BASE)      │
   │ ██      Saude Mental | @psidanielacoelho     │
   │ ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ (barra ▌)   │
   └──────────────────────────────────────────────┘
   Lower third: SEM "Psicóloga" até jan/2027
   Badge topo: fundo branco, borda sutil, texto escuro maiúsculo, arredondado

4. EDGE TTS pt-BR-AntonioNeural
   - RATE_REAL = len(script) / dur_audio  (NUNCA hardcoded)
   - Reutiliza audio_url existente do DB quando disponível

5. TIMING DINÂMICO:
   - dur_cena = dur_chars / RATE_REAL
   - mínimo 0.5s por cena

6. ffconcat → FFmpeg:
   - Shorts crf=25 → ~3-6MB | Longs crf=22 → ~15-20MB
   - 25fps, libx264, aac 128k, yuv420p, -movflags +faststart

7. Upload Supabase Storage → update content_pipeline.video_url → status pending_credentials
```

### Modelos Gemini para IMAGEM (2026):
```
✅ gemini-2.0-flash-exp                  → FREE, funciona com key normal
✅ gemini-2.0-flash-exp-image-generation → alias explícito para imagem
⚠️ gemini-2.5-flash-image               → requer permissão especial (403 com key normal)
❌ gemini-3.1-flash-image-preview        → não existe ainda (não usar)
```

### Prompt padrão imagem (anti-plágio obrigatório em TODOS):
```
"Psych2Go animation style, kawaii chibi anime character,
cream white background #F5F0E8, pastel warm colors,
round big expressive eyes, clean soft lines. [PROMPT CENA].
Original character design not based on any existing IP or franchise,
no text, no logos, no watermarks, no brand marks."
```

---

## PERSONAGEM DANIELA COELHO — PADRÃO VISUAL ETERNO

- Chibi kawaii anime girl, cabelo escuro, sorriso cálido e profissional
- Roupa casual-profissional (blusa colorida)
- **Fundo SEMPRE creme #F5F0E8** (NUNCA escuro)
- Estilo Psych2Go — flat design, linha limpa, olhos grandes expressivos
- 20 imagens únicas por vídeo (uma por cena Groq)
- Sempre adicionar anti-plágio no prompt

---

## LOWER THIRD — PADRÃO ETERNO (Pillow permanente)

```python
LOWER_THIRD = "Daniela Coelho | Saude Mental | @psidanielacoelho"
# SEM Psicóloga até jan/2027
```

Cores Pillow (exatas, para sempre):
```python
VERM = (220, 50, 50)    # vermelho barra
GOLD = (255, 210, 50)   # dourado "psi"
BRAN = (255, 255, 255)  # branco nome
LILAS= (185, 170, 225)  # lilás subtítulo
BG   = (8,   6,  18)    # fundo escuro
```

---

## ÁUDIO — PADRÃO ETERNO

- Voz: **`pt-BR-AntonioNeural`** (Edge TTS, $0, ilimitado, sem API key)
- Vozes PT-BR válidas 2025+: AntonioNeural, FranciscaNeural, ThalitaMultilingualNeural
- Brenda: removida pela Microsoft em 2025 — NÃO usar

---

## SCRIPTS E WORKFLOWS

| Arquivo | Função |
|---------|--------|
| `scripts/render_video_v8_standard.py` | **PADRÃO ETERNO** — usar para TODOS os vídeos |
| `scripts/render_video_v9.py` | V9 com animações FFmpeg (respiração, olhos, etc.) |
| `.github/workflows/render-padrao-eterno.yml` | Dispatch manual + batch 3x/dia |
| `.github/workflows/render-video-v9-universal.yml` | V9 com animações FFmpeg |

**Para gerar qualquer vídeo:**
```
GitHub Actions → render-padrao-eterno.yml → inputs: video_id = <ID>
```

**Batch automático:** 3x/dia (6h, 12h, 18h UTC) — pega próximo `audio_ready` da fila

---

## CALENDÁRIO PUBLICAÇÃO MAIO 2026 (começa 16/mai Sáb)

| Dia | Data | Hora BR | Vídeo | Plataformas |
|-----|------|---------|-------|-------------|
| Sáb | 16/mai | 19h | #683 Narcisismo encoberto | YT→IG→TK→WA |
| Dom | 17/mai | 18h | #701 Depressão Silenciosa | YT→IG→TK→WA |
| Seg | 18/mai | 19h | #682 Celular 80x trauma | YT→IG→TK→WA |
| Ter | 19/mai | 18h30 | #689 Perfeccionista | YT→IG→TK→WA |
| Qua | 20/mai | 18h | #684 Sofia ansiedade | YT→IG→TK→WA |
| Qui | 21/mai | 19h | #688 Lucas apagamento | YT→IG→TK→WA |
| Sex | 22/mai | 18h | #707 Motivação | YT→IG→TK→WA |
| Sáb | 23/mai | 19h | #708 Lei do Silêncio | YT→IG→TK→WA |
| Dom | 24/mai | 18h30 | #685 Autossabotagem | YT→IG→TK→WA |
| Seg | 25/mai | 19h | #687 Isabela abstinência | YT→IG→TK→WA |
| Ter | 26/mai | 18h | #643 Feridas infância | YT→IG→TK→WA |
| **Qua** | **27/mai** | **18h+20h** | **#644 Short + #693 LONG Gaslighting 24min** | YT |
| Qui | 28/mai | 19h | #91 Apego Ansioso P4 | YT→IG→TK→WA |
| **Sex** | **29/mai** | **18h+20h** | **#89 Short + #695 LONG Rel. Tóxico 22min** | YT |
| **Sáb** | **30/mai** | **19h** | **#706 LONG Narcisista 17min** | YT→IG→WA |
| Dom | 31/mai | 10h+ | Analytics + Carrossel IG + Recap | - |

**Sequência diária:** YouTube (18-20h BR) → Instagram +5min → TikTok +30min → WhatsApp +1h

---

## VÍDEO ÂNCORA — #683 NARCISISMO ENCOBERTO

**Título:** "Narcisismo encoberto: 3 sinais que você está ignorando agora mesmo"
**V8 Final (MELHOR — usar este):**
```
https://tpjvalzwkqwttvmszvie.supabase.co/storage/v1/object/public/videos/mp4s/v683_viral_v8_1778892031.mp4
```
- 6.3MB | 62.4s | 20 cenas chibi Gemini AI | Lower third correto
- Script: 829 chars | Audio existente: `v683_v8_1778892031.mp3`
- Publica HOJE 16/mai às 19h → YouTube @psidanielacoelho

---

## VIRAL MIRROR — REFERÊNCIAS ETERNAS

Top refs (1.8M–28M views):
- Psych2Go "Covert Narcissist" **28M** ← espelho do #683
- Psych2Go "Abandonment Issues" 22M
- Psych2Go "Childhood Trauma" 19M

Fórmulas virais (confidence 95-99%):
1. `N Sinais + [condição invisível/secreta]` — CTR 8-12%
2. `Não é X, é Y — Redefinição` — CTR 10-15%
3. `Paradoxo Amor/Destruição` — CTR 11-16%
4. `Revelação de Perigo Oculto` — CTR 12-18% (MAIOR, 28M)
5. `A Verdade Desconfortável/Científica` — CTR 9-13%

Tabela: `viral_videos_reference` | Função: `get_viral_mirror_instruction(topic)`

---

## LLM ROUTER V4

1. NVIDIA `deepseek-ai/deepseek-v4-pro` ✅ DEFAULT
2. NVIDIA `meta/llama-3.3-70b-instruct` ✅ fallback
3. Groq `llama-3.3-70b-versatile` ✅ reset 0h UTC
4. OpenAI `gpt-4o-mini` 💰 pago (último recurso)

---

## PLAYLISTS YOUTUBE (criar antes de publicar)

1. 🎭 Narcisismo: Reconheça e Proteja-se (âncora 28M)
2. 💔 Relacionamentos Tóxicos
3. 🔗 Série Completa: Apego Ansioso
4. 🧠 Traumas da Infância
5. 😰 Ansiedade e Autossabotagem
6. 🏢 Trabalho Tóxico
7. ✨ Saúde Mental: Ciência (Longs)

---

## CREDENCIAIS — STATUS (16/mai/2026)

✅ OK: NVIDIA, GROQ, ElevenLabs, GH_PAT, Vercel, Supabase
✅ Gemini: usar `gemini-2.0-flash-exp` (key normal funciona)
❌ FALTA configurar (setup-tokens.html):
- `INSTAGRAM_ACCESS_TOKEN` + `INSTAGRAM_BUSINESS_ACCOUNT_ID`
- `TIKTOK_ACCESS_TOKEN` + `TIKTOK_CLIENT_KEY`
- `WHATSAPP_TOKEN` + `WHATSAPP_PHONE_ID`

---

## PLANO CRESCIMENTO 0 → R$50K/mês

- **Mai/Jun** → 1.000 subs (Google Ads R$600 + âncora #683 narcisismo espelho 28M)
- **Jul** → 4K horas watch → MONETIZAÇÃO AdSense
- **Ago** → 10K-30K subs (viral + Longs 3x/sem)
- **Set** → Curso digital R$197 + Sponsorship → R$5K-12K/mês
- **Out** → 60K-100K subs → R$15K-30K/mês
- **Nov** → 100K+ → R$35K-55K/mês (AdSense + Curso + WA + IG + TikTok)

---

## ESTADO (16/mai/2026)

- Canal: 0 subs — vídeo #683 publica HOJE 19h (primeiro!)
- Vídeo #683: ✅ PRONTO — V8 Final Gemini AI 6.3MB
- Renders disparados: #701, #682, #689, #684, #688
- Longs em fila: #693 (24min), #695 (22min), #706 (17min)
- Meta: 1.000 subs até jun/2026

---

## LINKS

- Hub principal: https://repovazio.vercel.app/hub.html
- Vídeos prontos: https://repovazio.vercel.app/videos-prontos.html
- Setup tokens: https://repovazio.vercel.app/setup-tokens.html
- GitHub Actions: https://github.com/tafita81/Repovazio/actions
- YouTube Studio: https://studio.youtube.com (psidanielacoelho1982@gmail.com)
