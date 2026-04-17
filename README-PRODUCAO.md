# 🚀 Guia de Deploy — psicologia.doc em Produção

## O que foi otimizado nesta versão

### 🔐 Segurança
- Next.js atualizado de 14.2.0 → **15.3.1** (corrige vulnerabilidade crítica)
- Headers de segurança no Netlify (X-Frame-Options, HSTS, CSP)
- Rate limiting na API de analytics
- Supabase client sem singleton leak em serverless

### ⚡ Performance
- `npm ci` em vez de `npm install` (builds determinísticos)
- Cache de assets estáticos (1 ano)
- Preconnect para fontes e Supabase

### 📣 Viral & Social
- Open Graph completo (Facebook, WhatsApp, LinkedIn)
- Twitter Cards otimizados
- Pinterest Rich Pins
- Botão de compartilhamento WhatsApp no Dashboard
- Schema.org para SEO

### 🎨 UX
- Dashboard completamente refeito (design dark, gradientes)
- Relógio animado com gradient
- Métricas em cards
- Tabela de registros com scroll
- Estados de loading, erro e retry
- Auto-refresh a cada 30 segundos
- Responsivo para mobile

---

## Passo a Passo: Deploy no Netlify

### 1. Conectar repositório ao Netlify

1. Acesse [app.netlify.com](https://app.netlify.com)
2. Clique em **"Add new site" → "Import an existing project"**
3. Conecte seu GitHub e selecione o repositório
4. Configurações de build:
   - **Build command**: `npm ci && npm run build`
   - **Publish directory**: `.next`
   - **Node version**: `20`

### 2. Configurar variáveis de ambiente

No painel do Netlify: **Site settings → Environment variables**

```
NEXT_PUBLIC_SUPABASE_URL     = https://xxxx.supabase.co
SUPABASE_SERVICE_KEY         = eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

> ⚠️ NUNCA coloque as chaves no código ou no repositório público!

### 3. Configurar GitHub Actions (deploy automático)

Adicione estes secrets no GitHub:
**Settings → Secrets and variables → Actions**

```
NETLIFY_AUTH_TOKEN     = (gere em app.netlify.com/user/applications)
NETLIFY_SITE_ID        = (encontre em Site settings → General → Site ID)
NEXT_PUBLIC_SUPABASE_URL = https://xxxx.supabase.co
SUPABASE_SERVICE_KEY     = eyJ...
```

Agora cada push na branch `main` faz deploy automático! ✅

### 4. Domínio customizado (opcional)

Em **Site settings → Domain management**:
1. Clique em "Add custom domain"
2. Digite seu domínio (ex: `psicologia.doc`)
3. Aponte o DNS conforme instruções do Netlify
4. HTTPS é automático via Let's Encrypt

---

## Estrutura do Projeto Otimizado

```
├── app/
│   ├── layout.js          # SEO + meta tags (Open Graph, Twitter, Pinterest)
│   ├── page.js            # Página principal
│   ├── Dashboard.jsx      # Dashboard completo com viral features
│   └── api/
│       └── analytics/
│           └── route.js   # API com rate limiting + error handling
├── lib/
│   └── supabaseServer.js  # Client Supabase otimizado para serverless
├── .github/
│   └── workflows/
│       └── deploy.yml     # CI/CD automático para Netlify
├── netlify.toml           # Config Netlify com headers de segurança
└── package.json           # Next.js 15 + deps atualizadas
```

---

## Monetização — Próximos Passos

### Fase 1: Base (agora)
- ✅ Dashboard funcionando
- ✅ Supabase conectado
- ✅ Compartilhamento WhatsApp

### Fase 2: Crescimento (semana 1-2)
- [ ] Landing page com headline viral
- [ ] Formulário de captura de email
- [ ] Integração Mailchimp/Brevo para newsletter
- [ ] Pixel do Meta para remarketing

### Fase 3: Monetização (semana 3-4)
- [ ] Stripe para assinaturas
- [ ] Plano gratuito vs pago
- [ ] Programa de afiliados
- [ ] Grupo VIP WhatsApp para pagantes

---

## Suporte

Se encontrar problemas:
1. Verifique os logs em **Netlify → Deploys → [último deploy] → Deploy log**
2. Verifique as variáveis de ambiente
3. Teste localmente: `npm run dev`
