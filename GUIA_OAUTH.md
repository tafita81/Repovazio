# Guia: Criar o Refresh Token OAuth (destrava o agente de stream keys)

> O agente `provision_stream_keys.py` ja faz tudo sozinho (cria stream key, grava secret, cria/vincula broadcast, sobe ao vivo). A UNICA coisa que ele nao pode fazer e o consentimento OAuth no navegador — Google exige humano, 1x por canal. Este guia e esse passo.

## POR QUE O TOKEN MORREU (leia primeiro)
Se a Tela de Permissao OAuth estiver em modo **Testing**, o Google **expira o refresh token em 7 dias** -> erro `invalid_grant`. Foi quase certamente isso. A correcao definitiva e publicar o app em **Production** (Fase A). Sem isso, morre de novo em uma semana.

---

## FASE A — Impedir que morra de novo (5 min, 1 vez so)
1. Abra `console.cloud.google.com` e selecione o **projeto** dono do Client ID `552651753048-...`.
2. **APIs e Servicos -> Biblioteca** -> busque **"YouTube Data API v3"** -> **Ativar**.
3. **APIs e Servicos -> Tela de permissao OAuth**:
   - Tipo de usuario: **External**.
   - Em **Status de publicacao** clique **"PUBLICAR APP"** -> confirme **"Em producao"** (remove a expiracao de 7 dias).
4. **APIs e Servicos -> Credenciais** -> abra seu **OAuth 2.0 Client ID** -> em **URIs de redirecionamento autorizados** clique **Adicionar URI** e cole exatamente:
   ```
   https://developers.google.com/oauthplayground
   ```
   -> **Salvar**.

---

## FASE B — Gerar o refresh token (3 min, repete por canal)
5. Abra `https://developers.google.com/oauthplayground`.
6. Clique na **engrenagem (settings)** no canto superior direito -> marque **"Use your own OAuth credentials"** -> cole **Client ID** e **Client Secret** -> feche.
7. Na coluna esquerda, no campo **"Input your own scopes"**, cole:
   ```
   https://www.googleapis.com/auth/youtube.force-ssl
   ```
   -> clique **"Authorize APIs"**.
8. Login em **tafita81@gmail.com** -> **escolha o canal certo** (se aparecer seletor de marca, selecione **@psidanicoelho** para o canal principal) -> **Permitir / Allow**.
9. No **Step 2** clique **"Exchange authorization code for tokens"**.
10. Copie o valor do campo **"Refresh token"** (comeca com `1//...`). Esse e o token.

> Se "Refresh token" vier vazio: va em `myaccount.google.com/permissions`, remova o acesso antigo do app e refaca 7-9 (forca o consentimento e devolve token novo).

---

## FASE C — Salvar no GitHub (1 min)
11. `github.com/tafita81/Repovazio` -> **Settings** -> **Secrets and variables -> Actions**.
12. Ache **`YOUTUBE_REFRESH_TOKEN`** -> lapis **(Update)** -> cole o token -> **Update secret**.
    - Para canal de outro idioma: **"New repository secret"** com nome `YOUTUBE_REFRESH_TOKEN_EN` (ou `_DE`, `_JA`, etc.).

---

## FASE D — Ligar o agente
13. Aba **Actions** -> workflow **"Agente: Provisionar Stream Keys"** -> **Run workflow**. (Ou avise o assistente que dispara.)
    - O agente entao: cria a stream key -> grava `YOUTUBE_STREAM_KEY[_<LANG>]` -> cria e vincula broadcast publico (auto-start) -> canal entra ao vivo.

---

## OBSERVACOES
- **Token e por canal.** Para cada canal multilingue novo: 1) crie o canal no YouTube; 2) ative transmissao ao vivo (1a vez espera 24h do YouTube); 3) refaca a Fase B selecionando AQUELE canal; 4) salve como `YOUTUBE_REFRESH_TOKEN_<LANG>`.
- **Canal PT (@psidanicoelho)** ja tem live ativa via RTMP; atualizar o `YOUTUBE_REFRESH_TOKEN` reativa o que depende de OAuth (nao a live em si).
- **Escopo** `youtube.force-ssl` cobre criar/vincular live (`liveStreams` + `liveBroadcasts`).
- **Ordem por CPM** (qual canal priorizar): EN > DE > JA > FR > IT > KO > ZH > ES > AR > RU > HI. Ver `GUIA_CANAIS_MULTILINGUE.md`.

## Diagnostico rapido
- Workflow **"Probe OAuth"** (aba Actions -> Run workflow) testa se os tokens estao vivos e grava o resultado em `ia_cache` (`agent:probe_oauth`). Use sempre que um token parar de funcionar.
