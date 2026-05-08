# psicologia.doc — Pipeline 24/7 Setup

Sistema autônomo que gera **5 vídeos/dia** (1 por rede social) em qualidade cinematográfica
**100% grátis e ilimitado**, rodando 24/7 no GitHub Actions sem nenhuma dependência da página aberta.

## Arquitetura

```
┌─────────────────────────────────────────────────────────────────────┐
│  CRON SCHEDULE (UTC) — workflow tts-pipeline.yml                    │
│   09h → youtube_long         (06h BRT, vídeo 10-17 min)             │
│   13h → youtube_shorts       (10h BRT, vídeo 30-60s)                │
│   17h → instagram_reels      (14h BRT, vídeo 30-60s)                │
│   21h → tiktok_short         (18h BRT, vídeo 30-60s)                │
│   01h → pinterest_pin        (22h BRT, vídeo 50-90s)                │
└─────────────────────┬───────────────────────────────────────────────┘
                      │
                      ▼
┌─────────────────────────────────────────────────────────────────────┐
│  scripts/tts_edge.py — Geração de áudio cinematográfico             │
│    1. SQL: pega próximo `script_ready` da plataforma                │
│    2. Quebra script em parágrafos                                   │
│    3. Groq Llama 3.3 70B classifica emoção (6 categorias)           │
│    4. Edge TTS Microsoft (GRÁTIS ILIMITADO):                        │
│         INTRO_CALMO    → Francisca rate-5%                          │
│         ALERTA_TENSO   → Antonio   rate+8%                          │
│         EMPATIA        → Francisca rate-10%                         │
│         ANALITICO_FRIO → Antonio   rate+0%                          │
│         ESPERANCA      → Thalita   rate+0%                          │
│         CTA_URGENTE    → Antonio   rate+12%                         │
│         HOOK_ENERGICO  → Brenda    rate+5%                          │
│    5. ffmpeg concat + EBU R128 -16 LUFS                             │
│    6. Upload Supabase Storage                                       │
│    7. video-generator EF → HTML cinematográfico                     │
│    8. workflow_dispatch render-mp4.yml                              │
└─────────────────────┬───────────────────────────────────────────────┘
                      │
                      ▼
┌─────────────────────────────────────────────────────────────────────┐
│  .github/workflows/render-mp4.yml v8.2 — Render cinematográfico     │
│    Playwright captura HTML em 30fps                                 │
│    Long: 1920x1080, Shorts: 1080x1920                               │
│    H.264 CRF 18 + AAC stereo 48k 192kbps                            │
└─────────────────────┬───────────────────────────────────────────────┘
                      │
                      ▼
┌─────────────────────────────────────────────────────────────────────┐
│  scripts/distribute.py — Publicador (cron a cada 30 min)            │
│    Pega `mp4_ready` por plataforma → tenta publicar                 │
│    Se faltar OAuth → status `pending_credentials`                   │
└─────────────────────────────────────────────────────────────────────┘
```

## Componentes 100% grátis usados

| Recurso | Custo | Limite | Função |
|---|---|---|---|
| **GitHub Actions** | $0 | **Ilimitado** (repo público) | Roda workflows |
| **Edge TTS (Microsoft)** | $0 | **Ilimitado** | TTS PT-BR neural multi-voz |
| **Groq Llama 3.3 70B** | $0 | 14.4k req/dia | Classifica emoção dinâmica |
| **Supabase free** | $0 | 500MB DB + 1GB Storage | DB + Storage temporário |
| **Vercel free** | $0 | 100GB bandwidth/mês | Galeria pública |

## Status atual: ✅ TTS + Render funcionando 100% sem créditos

**Validado em produção (8 mai 2026):**
- Pipeline 78 (Shorts): 23.4s, 1080×1920, 30fps H.264, AAC stereo 48k → 4.7MB MP4 em 3 min
- Áudio: Edge TTS multi-voz (Francisca + Antonio) com 3 emoções classificadas pela Groq
- Custo: $0,00

## ⚠️ Falta para publicação 100% autônoma

A geração roda 24/7 sozinha. **Para publicar automaticamente nas 5 redes**, precisa de OAuth.
Cada plataforma exige UMA configuração inicial pelo usuário (uma única vez).

### 1. YouTube (canal NOVO — não usar o canal antigo bloqueado)

1. Crie OAuth Client em https://console.cloud.google.com/apis/credentials  
   → Application type: Desktop app
2. Habilite YouTube Data API v3
3. Use OAuth Playground https://developers.google.com/oauthplayground/  
   → Authorize com escopo `https://www.googleapis.com/auth/youtube.upload`  
   → Pegue **refresh_token**
4. Salve em ia_cache (Supabase):
   ```sql
   INSERT INTO ia_cache (cache_key, value) VALUES
   ('secret:YT_CLIENT_ID',     '<seu-client-id>'),
   ('secret:YT_CLIENT_SECRET', '<seu-client-secret>'),
   ('secret:YT_REFRESH_TOKEN', '<seu-refresh-token>');
   ```
5. Rode: `curl -s https://tpjvalzwkqwttvmszvie.supabase.co/functions/v1/github-secrets-setup-all`  
   (sincroniza secrets do Supabase pro GitHub Actions)

### 2. Instagram Reels

1. Tenha Conta Business no Instagram, conectada a uma Facebook Page que você administra
2. Em https://developers.facebook.com/apps → criar app tipo "Business"
3. Adicionar produto "Instagram Graph API"
4. OAuth com escopos: `instagram_basic, instagram_content_publish, pages_read_engagement, pages_show_list`
5. Pegar Long-lived Access Token (60 dias) em https://developers.facebook.com/tools/debug/accesstoken/
6. Pegar IG_USER_ID com `GET /me/accounts?access_token=…` → `instagram_business_account.id`
7. Salvar em ia_cache:
   ```sql
   INSERT INTO ia_cache (cache_key, value) VALUES
   ('secret:IG_USER_ID',      '<seu-ig-business-id>'),
   ('secret:IG_ACCESS_TOKEN', '<long-lived-token>');
   ```

### 3. TikTok

1. https://developers.tiktok.com/ → criar app (selecionar categoria business/creator)
2. Adicionar produto "Content Posting API"
3. OAuth com escopos: `video.upload, video.publish`
4. Pegar refresh_token (válido 365 dias) e access_token (válido 24h)
5. Salvar em ia_cache → secret:TT_ACCESS_TOKEN, secret:TT_CLIENT_KEY

⚠️ TikTok exige aprovação do app pra escopo `video.publish` (pode demorar ~5 dias).

### 4. Pinterest

1. https://developers.pinterest.com/apps → criar app
2. OAuth com escopos: `boards:read, pins:read, pins:write`
3. Criar 1 board (ex: "Psicologia Profunda") e pegar BOARD_ID
4. Salvar:
   ```sql
   INSERT INTO ia_cache (cache_key, value) VALUES
   ('secret:PIN_ACCESS_TOKEN', '<token>'),
   ('secret:PIN_BOARD_ID',     '<board-id>');
   ```

## Quando o `script_ready` acabar

O cerebro-autonomo (cron Supabase a cada 2h) gera novos scripts.
Se quiser forçar geração imediata:
```
curl -X POST https://tpjvalzwkqwttvmszvie.supabase.co/functions/v1/cerebro-autonomo
```

## Monitoramento ao vivo

- GitHub Actions: https://github.com/tafita81/Repovazio/actions
- Galeria pública: https://repovazio.vercel.app/videos-prontos.html
- DB pipeline: SQL `SELECT id,title,status,target_platform,mp4_url FROM content_pipeline WHERE status NOT IN ('archived','published') ORDER BY id DESC LIMIT 20;`

## Custos mensais reais (5 vídeos/dia, 30 dias = 150 vídeos)

| Item | Uso | Custo |
|---|---|---|
| Edge TTS chars | ~750k (5×5k médio) | **$0** |
| Groq tokens | ~750k (150×5k) | **$0** (free 14k req/dia) |
| GitHub Actions min | ~450 min | **$0** (ilimitado público) |
| Supabase Storage | ~6GB acumulado | precisa rotação semanal |
| YouTube/IG/TT/Pin upload | unlimited free APIs | **$0** |
| **TOTAL** | 150 vídeos/mês | **$0,00** |
