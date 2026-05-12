---
name: psicologia-doc-v32
description: Use esta SKILL sempre que o usuário mencionar: psicologia.doc, repovazio, Daniela Coelho, @psidanielacoelho, canal YouTube psicologia, viral, cérebro autônomo, tokens sociais, Instagram, TikTok, WhatsApp grupos, monetização, 1000 subs, crescimento, setup tokens, espelhamento viral, dashboard, hub, brand, identidade visual.
version: 32.0
date: 2026-05-12
---

# SKILL psicologia.doc V32 ETERNAL BRAIN (12/mai/2026)

## INFRA CORE
| Asset | ID/URL |
|---|---|
| Supabase | tpjvalzwkqwttvmszvie |
| Vercel | repovazio.vercel.app |
| GitHub | tafita81/Repovazio |
| Canal ATIVO | @psidanielacoelho · UCyCkIpsVgME9yCj_oXJFheA · psidanielacoelho1982@gmail.com |
| Canal BLOQUEADO | UCSH63tBfY6wEIdkC4u4zKdg — NUNCA publicar |

## IDENTIDADE VISUAL (Brand System V1 — ETERNO)
- **Conceito:** "Documentary Meets Emotion" — único no mundo no nicho psicologia BR
- **Símbolo:** ψ (Psi) redesenhado exclusivo — propriedade intelectual psicologia.doc
- **Paleta obrigatória:**
  - `#06060F` Deep Void (background principal)
  - `#5B21B6` Amethyst (cor da marca)
  - `#7C3AED` Violet (acento primário)
  - `#E11D48` Crimson (acento emocional)
  - `#F59E0B` Neural Gold (acento científico)
  - `#0D9488` Data Teal (acento séries)
  - `#F0F4FF` Mind Frost (texto principal)
  - `#C4B5FD` Mist (texto secundário)
- **Tipografia:** Display=Georgia serif · UI=DM Sans · Dados=DM Mono
- **4 tipos de thumbnail:** viral(roxo) · crime(crimson) · fact(teal) · gold(âmbar)
- **Assets online:** repovazio.vercel.app/brand/thumb-generator.html · youtube-banner.html · instagram-templates.html

## PIPELINE STATUS (V32 — 12/mai/2026)
| Status | Qtd |
|---|---|
| published | 0 (15 resetados — canal errado) |
| mp4_ready | 1 |
| script_ready | 2 |
| ready_tts | ~27 |
| pending_generation | 115 |
| archived | 126 |

## PIPELINE FLUX+KEN BURNS (V2 — CORRETO)
- **Método:** scripts/video_gen_v2.py + render-mp4-v2.yml
- **Stack:** Groq Llama 3.3 70B (segmentação) + Flux.1 Schnell NVIDIA (imagens ZERO texto) + Edge TTS + ffmpeg Ken Burns 30fps H.264 1080p
- **DEPRECATED:** render-mp4.yml v8 (Playwright+HTML com texto na tela) — NÃO USAR
- **Status fluxo correto:** script_ready → TTS → mp4_ready → render-mp4-v2 → published
- **Cerebro v14:** status mp4_ready (não video_ready) → render V2 pega automaticamente

## SISTEMA PSYCH2GO QUANTICO V2 (scripts/video_gen_v2.py)
- `PSYCH2GO_PALETTES` — dicionário de paleta por emoção (10 emoções mapeadas)
- `PSYCH2GO_CHAR_DIVERSITY` — 8 personagens BR rotativos (diversidade étnica/gênero/idade)
- `PSYCH2GO_SHOT_PROMPTS` — 6 shot types (close_face/medium/wide/silhouette/hands_close/profile)
- `build_psych2go_prompt()` — construtor de prompt quântico com expressão facial precisa por emoção
- Prompt base: "flat vector 2D illustration, Psych2Go educational animation style..."
- Negative: "ZERO text ZERO words ZERO letters ZERO numbers ZERO watermarks ZERO signs"
- 5 retries com seed variation por imagem

## DASHBOARD V11 (repovazio.vercel.app/dashboard)
- 17 páginas: dashboard/conteudo/series/ranking/monetizacao/cerebro/gerador/variacoes/revelacao/playlist/cases/canais/whatsapp/logs/daniela/config/hub
- Hub Central (/dashboard?page=hub): links para admin, infra, pipeline, canal
- app/page.js → redirect("/dashboard") — home principal
- Hub Master HTML: repovazio.vercel.app/hub.html (dados ao vivo via /api/growth)

## VIRAL MIRROR (tabela viral_videos_reference)
- 18 vídeos · 1.8M–28M views
- Top: Psych2Go "Covert Narcissist" 28M, "Abandonment" 22M, "Childhood Trauma" 19M
- Função `get_viral_mirror_instruction(topic)` injetada em cada roteiro

## FÓRMULAS VIRAIS (95–99% confidence)
1. `N Sinais + [condição invisível/secreta]` — CTR 8-12%
2. `Não é X, é Y — Redefinição de Identidade` — CTR 10-15%
3. `Paradoxo Amor/Destruição` — CTR 11-16%
4. `Revelação de Perigo Oculto` — CTR 12-18% (maior, 28M)
5. `A Verdade Desconfortável/Científica` — CTR 9-13%

## LLM ROUTER V2
1. NVIDIA DeepSeek V4 Pro (DEFAULT, grátis)
2. NVIDIA Llama 3.3 70B (fallback)
3. Groq Llama 3.3 70B (fallback 2)
4. OpenAI gpt-4o-mini (pago, emergência)

## TTS ENGINE
- **Primário:** Edge TTS Microsoft (grátis, ilimitado) — AntonioNeural, FranciscaNeural, ThalitaMultilingualNeural
- **Secundário:** ElevenLabs Sarah EXAVITQu4vr4xnSDxMaL (40K chars/mês)

## CREDENCIAIS STATUS
- OK: NVIDIA, GROQ, OpenAI, ElevenLabs, GH_PAT, Supabase
- BLOQUEIO CRÍTICO: YOUTUBE_REFRESH_TOKEN (único bloqueio para publicação automática)
  - Fix: developers.google.com/oauthplayground → Client ID/Secret nas Vercel env vars
  - Login: psidanielacoelho1982@gmail.com · Escopos: youtube + yt-analytics.readonly
- Falta: INSTAGRAM_ACCESS_TOKEN, TIKTOK_ACCESS_TOKEN, WHATSAPP_TOKEN
- EFs Supabase: 98/100 limite — deploy bloqueado (requer Personal Access Token para deletar órfãs)

## PLANO CRESCIMENTO 0→MILHÕES
- **Fase 1 (dias 1-30):** Google Ads R$200 · vídeo âncora narcisismo · 0→100 subs · Afiliados Zenklub
- **Fase 2 (dias 31-60):** Orgânico viral · séries · Shorts diários · 100→1K subs · AdSense elegível
- **Fase 3 (dias 61-90):** Curso R$97 + WhatsApp grupos · 1K→10K subs · R$800/mês
- **Meta 2027:** Daniela Coelho pública · Consultas · Patrocínios · R$50K/mês

## LINKS ESSENCIAIS
- Dashboard: repovazio.vercel.app/dashboard
- Hub Master: repovazio.vercel.app/hub.html
- Brand Assets: repovazio.vercel.app/brand/
- Vídeos Prontos: repovazio.vercel.app/videos-prontos.html
- Growth Engine: repovazio.vercel.app/growth.html
- Cérebro Monitor: repovazio.vercel.app/cerebro.html
- Admin: repovazio.vercel.app/admin.html
