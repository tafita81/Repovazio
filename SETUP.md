# ψ SETUP.md — Configuração Completa psicologia.doc


## 🔴 CRÍTICO: Regenerar YT_REFRESH_TOKEN (expirado!)

**Erro detectado:** `invalid_grant — Token has been expired or revoked`

### Passo a passo para renovar o token:

**Opção A — Google OAuth Playground (mais fácil):**
1. Acesse: https://developers.google.com/oauthplayground
2. Clique no ícone ⚙️ (canto superior direito)
3. Marque "Use your own OAuth credentials"
4. Insira:
   - OAuth Client ID: (mesmo do YT_CLIENT_ID no GitHub)
   - OAuth Client Secret: (mesmo do YT_CLIENT_SECRET)
5. Feche as configurações
6. No campo "Select & authorize APIs":
   - Cole: `https://www.googleapis.com/auth/youtube.upload`
   - Clique "Authorize APIs"
7. Faça login com a conta `psidanielacoelho1982@gmail.com`
8. Aceite as permissões
9. Clique "Exchange authorization code for tokens"
10. **Copie o `refresh_token`** que aparece na resposta

**Atualizar o GitHub Secret:**
1. Acesse: https://github.com/tafita81/Repovazio/settings/secrets/actions
2. Clique em `YT_REFRESH_TOKEN`
3. Cole o novo refresh_token
4. Clique "Update secret"

**Redisparar o Publisher:**
```bash
# Depois de atualizar o secret:
curl -X POST \
  -H "Authorization: Bearer GH_PAT" \
  -H "Accept: application/vnd.github+json" \
  "https://api.github.com/repos/tafita81/Repovazio/actions/workflows/youtube-publisher.yml/dispatches" \
  -d '{"ref":"main"}'
```

**Verificar no YouTube Studio:**
- https://studio.youtube.com/channel/UCyCkIpsVgME9yCj_oXJFheA


## 🔴 PASSO 1: Deletar Edge Functions Orphan (BLOQUEADOR CRÍTICO)

Acesse: https://app.supabase.com/project/tpjvalzwkqwttvmszvie/functions

**Deletar as seguintes 48 funções** (clique na função → "Delete"):

### Lote A — Commits debug (deletar todos):
github-commit, commit-learn, commit-skills, commit-chat, commit-route,
commit-from-chunks, commit-route-final, commit-from-cache, commit-chatia,
commit-chatia-v3, store-v6-p1, commit-v8-route, commit-executor-v7,
commit-ia-v6, test-b64-len, commit-ia-executor, exec-sql

### Lote B — v9/v10 debug:
deploy-v9, commit-v9-runner, do-commit-v9, trigger-commit, do-commit-v10,
commit-v10-final, add-browser, run-now, trigger, v10-trigger, v10-commit-pat,
v10-p0, fix-and-upgrade, commit-v9d, v10-final-commit, fix-monitor-now,
test-pat, v10-chunk-test, commit-v10-now, v10-commit-real, v10-go,
commit-v10-final2

### Lote C — v11/v12 debug:
read-file, upgrade-chat-upload, fix-chat-upload2, fix-browser-route,
v10-assemble-commit, assemble-and-commit-v10, assemble-v10,
v12-assemble-commit, v11-assemble-commit, v11-fix-parts, fix-cron-route,
v11-final-commit, v11-debug, v11-commit-chunks, v11-fix-together,
v12-all-inserter, v12-ins-01, v12-micro-p0, v12-insert-p4p9, v12-kv-store,
v12-insert-p7, v12-insert-p7-exact, v12-p7-native, v12-p7-v2, v12-p7-final,
v12-p8-fn, create-vercel-project, debug-sbk, debug-secret-key, debug-envs,
github-yaml-view, github-secrets-setup-all

**Manter:** daniela-chat, daniela-app, daniela-admin, youtube-api,
cerebro-autonomo, video-generator, youtube-publisher, render-trigger,
social-publisher, analytics-collector, intelligence-engine, cases-researcher,
cases-bootstrap, videos-page-publisher, piloto-prepare, connectors-api,
app-runtime, audit-youtube, gh-commit, github-secrets-setup,
github-workflow-status, github-run-logs, github-step-log, github-workflow-yaml,
github-workflow-fix, render-one, mp4-upload, github-commits, github-job-log

---

## 🔴 PASSO 2: Publicar os 16 Vídeos no YouTube

1. Acesse: https://github.com/tafita81/Repovazio/actions/workflows/274395908
2. Clique em **"Run workflow"** → **"Run workflow"** (branch: main)
3. Aguarde ~5 minutos
4. Verifique em: https://studio.youtube.com/channel/UCyCkIpsVgME9yCj_oXJFheA

**Canal correto:** UCyCkIpsVgME9yCj_oXJFheA (@psidanielacoelho)
**NUNCA publicar em:** UCSH63tBfY6wEIdkC4u4zKdg (canal BLOQUEADO)

---

## 🟡 PASSO 3: OAuth Instagram (Meta)

### 3.1 Criar App Meta
1. Acesse: https://developers.facebook.com/apps/
2. "Criar App" → Tipo: "Negócios"
3. Adicionar produto: **Instagram Graph API**
4. Em "Configurações" → "Básico" → copiar:
   - App ID → `META_APP_ID`
   - Segredo do App → `META_APP_SECRET`

### 3.2 Obter token de longa duração
1. "Ferramentas" → "Explorador da API do Graph"
2. Selecionar app → gerar token com permissões:
   `instagram_basic, instagram_content_publish, pages_read_engagement`
3. Trocar por token de longa duração (60 dias):
   ```
   curl "https://graph.facebook.com/v19.0/oauth/access_token?
     grant_type=fb_exchange_token&
     client_id={APP_ID}&
     client_secret={APP_SECRET}&
     fb_exchange_token={SHORT_TOKEN}"
   ```
4. Salvar no Supabase:
   ```sql
   INSERT INTO ia_cache (cache_key, value) VALUES
   ('secret:META_APP_ID','SEU_APP_ID'),
   ('secret:META_APP_SECRET','SEU_APP_SECRET'),
   ('secret:META_ACCESS_TOKEN','SEU_TOKEN_LONGA_DURACAO'),
   ('secret:META_INSTAGRAM_ACCOUNT_ID','SEU_ID_CONTA_IG')
   ON CONFLICT (cache_key) DO UPDATE SET value=EXCLUDED.value;
   ```

### 3.3 Obter Instagram Account ID
```
curl "https://graph.facebook.com/v19.0/me/accounts?access_token={TOKEN}"
```
Copiar o `id` da página → depois:
```
curl "https://graph.facebook.com/v19.0/{PAGE_ID}?fields=instagram_business_account&access_token={TOKEN}"
```

---

## 🟡 PASSO 4: OAuth TikTok

### 4.1 Criar App TikTok
1. Acesse: https://developers.tiktok.com/apps/
2. "Create app" → categoria: "Social"
3. Adicionar produto: **Content Posting API**
4. Copiar: Client Key e Client Secret

### 4.2 Obter tokens
```bash
# Passo 1: Gerar URL de autorização
curl "https://www.tiktok.com/v2/auth/authorize/
  ?client_key=CLIENT_KEY
  &response_type=code
  &scope=video.upload,video.publish
  &redirect_uri=https://repovazio.vercel.app/tiktok-callback
  &state=psicologia_doc"

# Passo 2: Trocar code por token
curl -X POST "https://open.tiktokapis.com/v2/oauth/token/" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "client_key=CLIENT_KEY&client_secret=CLIENT_SECRET&code=CODE&grant_type=authorization_code&redirect_uri=REDIRECT_URI"
```

### 4.3 Salvar no Supabase
```sql
INSERT INTO ia_cache (cache_key, value) VALUES
('secret:TIKTOK_CLIENT_KEY','SEU_CLIENT_KEY'),
('secret:TIKTOK_CLIENT_SECRET','SEU_CLIENT_SECRET'),
('secret:TIKTOK_ACCESS_TOKEN','SEU_ACCESS_TOKEN'),
('secret:TIKTOK_OPEN_ID','SEU_OPEN_ID')
ON CONFLICT (cache_key) DO UPDATE SET value=EXCLUDED.value;
```

---

## 🟡 PASSO 5: OAuth Pinterest

### 5.1 Criar App
1. Acesse: https://developers.pinterest.com/apps/
2. "Create app" → Product: "Ads API" ou "Organic"
3. Copiar App ID e App Secret

### 5.2 Obter token
```
https://www.pinterest.com/oauth/?
  client_id=APP_ID&
  redirect_uri=https://repovazio.vercel.app/pinterest-callback&
  response_type=code&
  scope=boards:read,pins:read,pins:write
```

```sql
INSERT INTO ia_cache (cache_key, value) VALUES
('secret:PINTEREST_APP_ID','SEU_APP_ID'),
('secret:PINTEREST_APP_SECRET','SEU_APP_SECRET'),
('secret:PINTEREST_ACCESS_TOKEN','SEU_TOKEN')
ON CONFLICT (cache_key) DO UPDATE SET value=EXCLUDED.value;
```

---

## 🟡 PASSO 6: Upload Banner YouTube Studio

1. Acesse: https://repovazio.vercel.app/brand.html
2. Clique em "↓ Download Banner" → baixa SVG 2560×1440
3. Converter para PNG (use: https://convertio.co/svg-png/ em 2560×1440)
4. YouTube Studio → https://studio.youtube.com/channel/UCyCkIpsVgME9yCj_oXJFheA
5. "Personalização" → "Arte do canal" → "Fazer upload do banner"
6. Recortar para cada tamanho mostrado → Salvar

---

## 🟡 PASSO 7: Criar Grupos WhatsApp (8 temas)

Criar um grupo para cada tema e atualizar o banco:
```sql
UPDATE whatsapp_groups_temas SET invite_link = 'https://chat.whatsapp.com/SEU_LINK'
WHERE tema = 'NOME_DO_TEMA';
```

Temas: ansiedade, apego_ansioso, narcisismo, trauma, burnout, autoestima, relacionamentos_toxicos, psicologia_dinheiro

---

## 🟢 PASSO 8: Google Discovery Ads (Crescimento Fase 1)

1. Acesse: https://ads.google.com
2. "Nova campanha" → Objetivo: "Consideração da marca e produto"
3. Tipo: "Discovery"
4. Orçamento: **R$250/mês** (R$8,30/dia)
5. Localização: Brasil
6. Palavras-chave (correspondência ampla):
   - apego ansioso
   - gaslighting o que é
   - narcisismo sinais
   - trauma psicologia
   - ansiedade como tratar
7. URL destino: https://www.youtube.com/channel/UCyCkIpsVgME9yCj_oXJFheA
8. Anúncio: usar thumbnails de /brand.html

**Meta**: 50-120 inscritos na semana 1 → 1K em 4-6 semanas

---

## ✅ Verificação Final

Após completar todos os passos, testar:
```sql
-- Verificar tokens configurados
SELECT cache_key, LEFT(value,20) as preview 
FROM ia_cache 
WHERE cache_key LIKE 'secret:META%' 
   OR cache_key LIKE 'secret:TIKTOK%'
   OR cache_key LIKE 'secret:PINTEREST%'
   OR cache_key LIKE 'secret:YOUTUBE%';
```

```bash
# Verificar distribuição funcionando
curl -X POST https://api.github.com/repos/tafita81/Repovazio/actions/workflows/273407183/dispatches \
  -H "Authorization: Bearer GH_PAT" \
  -H "Accept: application/vnd.github+json" \
  -d '{"ref":"main"}'
```

---

*Gerado automaticamente por psicologia.doc V41 — 2026-05-14*
