# Guia: Canais Multilingue — psicologia.doc

> Canal-mae ATIVO: @psidanicoelho (UCSH63tBfY6wEIdkC4u4zKdg) · tafita81@gmail.com
> Live de teste: https://youtube.com/@psidanicoelho/live
>
> Toda a engenharia ja esta pronta. Para cada idioma falta APENAS: criar o canal + colar a stream key num Secret do GitHub. No proximo ciclo de cron (~6h) o idioma entra no ar sozinho.

## Como funciona
- Cada idioma tem um workflow `.github/workflows/youtube-live-<lang>.yml` em cron a cada ~6h (timeout 6h, auto-renova).
- O script `scripts/live_universal.py` gera binaural beats (528Hz sono / 963Hz dia) + slides com insights traduzidos e empurra via RTMP.
- O workflow le o secret `YOUTUBE_STREAM_KEY_<LANG>`. Enquanto o secret nao existir, o workflow roda mas NAO transmite (no-op silencioso). Assim que existir, sobe sozinho.

## Passo a passo (repetir por canal)
1. CRIAR O CANAL: YouTube -> avatar -> "Trocar de conta" -> "Criar canal" (brand account na mesma conta tafita81@gmail.com).
2. NOME + HANDLE: defina conforme a tabela abaixo.
3. ATIVAR LIVE: YouTube Studio -> Criar -> Transmitir ao vivo. ATENCAO: na 1a ativacao o YouTube pede verificacao por telefone e impoe ESPERA DE 24h. Ative todos no mesmo dia para o relogio correr em paralelo.
4. LIVE PERSISTENTE + STREAM KEY: crie uma transmissao recorrente/persistente (latencia baixa) e copie a CHAVE DE TRANSMISSAO permanente.
5. SECRET NO GITHUB: repo tafita81/Repovazio -> Settings -> Secrets and variables -> Actions -> New repository secret -> nome EXATO `YOUTUBE_STREAM_KEY_<LANG>` -> cole a chave -> Save.

Pronto. Na proxima janela de cron daquele idioma a live sobe automaticamente.

## Tabela mestre (ordem por CPM)

| # | CPM | Idioma | Nome do canal | Handle | Secret | Cron UTC | Titulo da live |
|---|-----|--------|---------------|--------|--------|----------|----------------|
| 1 | US$28 | EN | Psychology Frequencies | @psychologyfrequencies | YOUTUBE_STREAM_KEY_EN | ativo ~6h | 528Hz SLEEP \| Anxiety & Narcissism \| Psychology LIVE 24/7 |
| 2 | US$18 | DE | Psychologie Frequenzen | @psychologiefrequenzen | YOUTUBE_STREAM_KEY_DE | ativo ~6h | 528Hz SCHLAF \| Angst und Narzissmus \| Psychologie LIVE |
| 3 | US$15 | JA | サイコロジー周波数 | @psychfreqjp | YOUTUBE_STREAM_KEY_JA | ativo ~6h | 528Hz 睡眠 \| 不安とナルシシズム \| 心理学ライブ |
| 4 | US$14 | FR | Psychologie Frequences | @psychologiefrequences | YOUTUBE_STREAM_KEY_FR | ativo ~6h | 528Hz SOMMEIL \| Anxiete et Narcissisme \| EN DIRECT |
| 5 | US$12 | IT | Psicologia Frequenze | @psicologiafrequenze | YOUTUBE_STREAM_KEY_IT | ativo ~6h | 528Hz SONNO \| Ansia e Narcisismo \| IN DIRETTA |
| 6 | US$12 | KO | 심리학 주파수 | @psychfreqkr | YOUTUBE_STREAM_KEY_KO | ativo ~6h | 528Hz 수면 \| 불안과 자기애 \| 심리학 라이브 |
| 7 | US$10 | ZH | 心理学频率 | @psychfreqzh | YOUTUBE_STREAM_KEY_ZH | 0 5,11,17,23 | 528Hz 深度睡眠 \| 焦虑与自恋 \| 心理学直播 |
| 8 | US$9 | ES | Psicologia Frecuencias | @psicologiafrecuencias | YOUTUBE_STREAM_KEY_ES | ativo ~6h | 528Hz DORMIR \| Ansiedad y Narcisismo \| EN VIVO |
| 9 | US$6 | AR | تردد علم النفس | @psychfreqar | YOUTUBE_STREAM_KEY_AR | ativo ~6h | 528Hz نوم \| القلق والنرجسية \| مباشر |
| 10 | US$5 | RU | Психология Частот | @psychfreqru | YOUTUBE_STREAM_KEY_RU | 0 3,9,15,21 | 528Hz СОН \| Тревога и Нарциссизм \| LIVE |
| 11 | US$4 | HI | मनोविज्ञान आवृत्ति | @psychfreqhi | YOUTUBE_STREAM_KEY_HI | 0 2,8,14,20 | 528Hz नींद \| चिंता और नार्सिसिज़्म \| LIVE |

PT (@psidanicoelho) ja esta ATIVO usando o secret `YOUTUBE_STREAM_KEY`.

## Recomendacao por esforco/retorno
Comece por EN (US$28 CPM, ~22M buscas/mes) e DE/JA. Os de maior populacao (ZH 1.4B, HI 1.4B) tem CPM menor mas volume gigante — bons para volume de inscritos.

## Limitacao conhecida — renderizacao de fonte (HONESTO)
O `live_universal.py` usa `ffmpeg drawtext` SEM `fontfile` -> usa a fonte padrao (DejaVu), que NAO tem glifos CJK (JA/KO/ZH), Devanagari (HI) nem arabe (AR). Nesses idiomas o texto do slide aparece como caixas vazias (tofu). Idiomas que renderizam 100%: PT, EN, ES, FR, DE, IT, RU (latim + cirilico).
- Correcao definitiva: adicionar `fontfile=` apropriado por script em `make_slide` (Noto Sans CJK / Noto Sans Devanagari / Noto Naskh Arabic). Os workflows ja instalam `fonts-noto-cjk`/`fonts-noto-core` para quando esse ajuste for feito.
- Observacao: o audio (binaural 528/963Hz) e os titulos da live na tabela ja saem corretos em todos os idiomas — a limitacao e so o texto sobreposto no video.

## Status atual da engenharia
- 11 workflows youtube-live-* ativos com cron (en/es/de/fr/it/ja/ko/ar + hi/ru/zh novos).
- `live_universal.py` com 12 idiomas no CONTENT.
- Falta apenas a acao manual: criar canais + cadastrar os 11 secrets `YOUTUBE_STREAM_KEY_<LANG>`.
