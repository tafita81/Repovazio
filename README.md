# GitHub Bootstrap Publisher (Mobile-Friendly)

 Este pacote publica automaticamente o **payload.zip** (seu app final) em **um novo repositório** no GitHub.

## Passo a passo no iPhone (GitHub App ou Safari)
1. **Crie um repositório vazio** (no app do GitHub: + → New repository).
2. Toque em **Add file → Upload files** e envie todo o conteúdo deste ZIP (incluindo `.github/workflows/...` e `payload.zip`).
3. Vá em **Settings → Secrets and variables → Actions** e crie o secret **GH_PAT** (Personal Access Token com escopo `repo`).  
   - No iPhone, abra `github.com/settings/tokens` no Safari para gerar o token e copie.
4. Abra a aba **Actions** → **Publish Payload to New GitHub Repo** → **Run workflow**.
   - Você pode **deixar os campos vazios**: o *owner* será autodetectado, o nome padrão será `globalsupplements-broker` e visibilidade `public`.
5. Em ~1 min, o repositório final estará publicado (o link aparece no log da Action).

> Depois, só conectar à **Render** (Deploy Hook + preDeploy) ou **Fly.io** conforme o `README-PROD.md` dentro do payload.
