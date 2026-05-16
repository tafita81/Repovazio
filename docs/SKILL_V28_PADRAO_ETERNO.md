---
name: psicologia-doc-v28
description: Use esta SKILL sempre que o usuário mencionar: psicologia.doc, repovazio, Daniela Coelho, @psidanielacoelho, canal YouTube psicologia, viral, cérebro autônomo, Instagram, TikTok, WhatsApp grupos, monetização, subs, crescimento, render video, V8, Gemini, Veo, 200 vídeos.
version: 28.1
date: 2026-05-15
---

# psicologia.doc V28.1 — PIPELINE ETERNO $0 PARA 200+ VÍDEOS

## INFRA CORE
- Supabase: `tpjvalzwkqwttvmszvie` | Vercel: `repovazio.vercel.app` | GitHub: `tafita81/Repovazio`
- Canal ATIVO: `@psidanielacoelho` · `UCyCkIpsVgME9yCj_oXJFheA`
- Canal BLOQUEADO PERMANENTE: `UCSH63tBfY6wEIdkC4u4zKdg` — NUNCA publicar
- Dashboard: repovazio.vercel.app/admin.html | Vídeos: repovazio.vercel.app/videos-prontos.html

---

## PIPELINE V8 — PADRÃO ETERNO (USAR PARA TODOS OS VÍDEOS)

### Stack $0/mês para sempre:
```
Groq (1 chamada) → gera 20 prompts contextuais por script
Gemini 2.5 Flash Image (4 workers paralelos, 2 chaves) → 20 imgs chibi em 30s
Edge TTS AntonioNeural (gratuito ilimitado) → áudio 54-62s
ffconcat timing DINÂMICO (rate = chars/dur_audio, NUNCA hardcode)
FFmpeg crf=25 → 3MB por vídeo (vs crf=18 = 6MB)
Upload Supabase Storage
```

### Scripts definitivos:
- **Universal**: `scripts/render_video_v8.py <VIDEO_ID>` — funciona para QUALQUER video
- **Workflow manual**: `render-video-v8-universal.yml` (dispatch com video_id input)
- **Workflow batch**: `render-batch-v8.yml` — roda 3x/dia (6h,12h,18h UTC), pega fila automática

### Triggerar render de qualquer vídeo:
```bash
# Via GitHub Actions dispatch:
POST /repos/tafita81/Repovazio/actions/workflows/render-video-v8-universal.yml/dispatches
{"ref":"main","inputs":{"video_id":"683"}}

# Fila automática roda sozinha 3x/dia pegando audio_ready
```

### Limites gratuitos (suficientes para 200+ vídeos):
| Recurso | Limite Free | Capacidade |
|---------|-------------|-----------|
| GitHub Actions | 2.000 min/mês | ~1.000 renders/mês |
| Gemini Flash Image | ilimitado (free tier) | infinito |
| Edge TTS Microsoft | ilimitado | infinito |
| Supabase Storage | 1GB | 333 vídeos (crf=25, 3MB/vídeo) |
| Groq LLM | ~14.400 req/dia | infinito |

### PROMPT ANTI-PLÁGIO (obrigatório em todo prompt Gemini):
```
"chibi anime flat design illustration, kawaii psychology animation, 
vertical 9:16 portrait, clean line art, soft warm cream white background, 
original character design NOT based on any existing IP or trademark, 
no text, no words, no letters"
```

### Personagens consistentes:
- **Renata (feminina)**: "chibi anime girl, short brown hair bob cut, warm beige skin tone, pink blouse, large expressive brown eyes, rosy cheeks"
- **Lucas (masculino)**: "chibi anime boy, slick dark hair, light skin, navy blue shirt, charming smile"

### Overlay obrigatório (Pillow):
- Lower third: "Daniela Coelho | Saude Mental | @psidanielacoelho" (SEM "Psicóloga" até jan/2027)
- Badge caption no topo com palavra-chave da cena

### Regras de script:
- Comprimento: 650-750 chars (54-57s de áudio AntonioNeural a 11.04 chars/s)
- Encerramento SEMPRE: "Inscreva-se agora" + sino (fim com sentido)
- Rate dinâmico: RATE_REAL = len(script) / dur_audio (probar após gerar audio)

### Garantia de monetização:
✅ Imagens 100% originais Gemini (não reprodução)
✅ Personagens ficcionais genéricos (sem IP de terceiros)
✅ Edge TTS licenciado Microsoft (uso comercial)
✅ Tema psicologia = advertiser-friendly
✅ Sem música de fundo (evita copyright claims)
✅ Canal correto configurado (@psidanielacoelho)

---

## PRÓXIMA EVOLUÇÃO: V9 VEO 3.1 (MOVIMENTO REAL)
- Modelo: `veo-3.1-generate-preview` via Gemini API (mesmas chaves)
- Gera vídeos 8s com braços, olhos, boca se movendo
- Aceita até 3 reference_images para consistência de personagem
- Pipeline V9: Gemini image (ref) → Veo 3.1 anima → ffconcat → overlay
- Status: paid preview mai/2026 | Free: 10 vídeos/mês via Google Vids

---

## FILA E MONITORAMENTO

```sql
-- Verificar fila de render pendente
SELECT * FROM get_render_queue(10);

-- Contar vídeos por status
SELECT status, COUNT(*) FROM content_pipeline GROUP BY status;

-- Forçar um vídeo para a fila
UPDATE content_pipeline SET status='audio_ready' WHERE id=XXX;
```

---

## CREDENCIAIS

```
GEMINI_KEY_1: [ver ia_cache secret:GEMINI_API_KEY]
GEMINI_KEY_2: [ver ia_cache secret:GEMINI_API_KEY_2]
GROQ_KEY: [ver ia_cache secret:GROQ_API_KEY]
GH_PAT: [ver ia_cache secret:GH_PAT]
SB_ANON: [ver ia_cache secret:SUPABASE_ANON_KEY]
```

GitHub Secrets: SUPABASE_SERVICE_KEY, GEMINI_API_KEY, GEMINI_API_KEY_2, GROQ_API_KEY

---

## VIRAL MIRROR & FÓRMULAS

Tabela: `viral_videos_reference` (18 refs, 1.8M–28M views)
Top: Psych2Go "Covert Narcissist" 28M, "Abandonment" 22M, "Childhood Trauma" 19M

Fórmulas (95-99% confiança):
1. "N Sinais + [condição oculta]" — CTR 8-12%
2. "Não é X, é Y" — CTR 10-15%
3. "Paradoxo Amor/Destruição" — CTR 11-16%
4. "Revelação Perigo Oculto" — CTR 12-18% (MAIOR, 28M)

## LLM ROUTER
1. NVIDIA deepseek-ai/deepseek-v4-pro (DEFAULT)
2. NVIDIA meta/llama-3.3-70b-instruct (fallback)
3. Groq llama-3.3-70b-versatile (reset 0h UTC)
4. Groq llama-3.1-8b-instant (reserva)

## PLANO CRESCIMENTO
- 0→1K subs: Google Ads ~R$600 + vídeo âncora narcisismo (espelho 28M)
- 1K→10K: Shorts diários + SEO orgânico + série numerada
- 100K: R$15K-50K/mês (AdSense + patrocínios + curso digital)
