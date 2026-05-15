---
name: psicologia-doc-v28
description: Use esta SKILL sempre que o usuário mencionar qualquer um destes termos: psicologia.doc, repovazio, Daniela Coelho, @psidanielacoelho, canal YouTube psicologia, narcisismo, apego ansioso, trauma, viral, cérebro autônomo, tokens sociais, Instagram, TikTok, WhatsApp grupos, monetização, 1000 subs, crescimento, setup tokens, espelhamento viral, quantum, score, critérios, hacks algoritmo, PNL hipnose, publicação, semana, série, playlist, render, script, edge TTS, short, long, galeria, calendário, publication_calendar, content_pipeline, pub_order, enhance_script, build-ranking, publication order. Esta skill contém TUDO do projeto psicologia.doc — não iniciar nenhuma tarefa sem consultá-la primeiro.
version: 28.0
date: 2026-05-15
---

# psicologia.doc V28 — Sistema Completo @psidanielacoelho

## INFRA CORE
- **Supabase:** tpjvalzwkqwttvmszvie | AK: SB_KEY_REDACTED
- **GitHub:** tafita81/Repovazio | PAT: ghp_***REDACTED***
- **Vercel:** repovazio.vercel.app | prj_rypXLpuS41CQt7sQYk5MM8kRQArr | team_zr9vAef0Zz3njNAiGm3v5Y3h
- **Canal ATIVO:** UCyCkIpsVgME9yCj_oXJFheA | @psidanielacoelho (psidanielacoelho1982@gmail.com)
- **Canal BLOQUEADO PERMANENTEMENTE:** UCSH63tBfY6wEIdkC4u4zKdg — NUNCA publicar

## PIPELINE V2 ($0/mes)
- **LLM chain:** NVIDIA DeepSeek V4 Pro -> Qwen3.5/Llama4 -> Groq Llama 3.3 70B -> OpenAI GPT-4o-mini
- **TTS validas PT-BR:** ThalitaMultilingualNeural, FranciscaNeural, AntonioNeural
- **Render:** Ken Burns 30fps H.264 1080p | CRF18 | -preset slow | AAC 192kbps | -14 LUFS
- **Workflow render:** render-mp4-v2.yml
- **Build sequencial:** build-ranking-sequential.yml (cron 30min, score gate 95/100)
- **Score:** score_pipeline_real(id) >= 95/100
- **Storage LIMITE:** 900 MB | bucket videos | alerta 850 MB

## DURACOES DEFINITIVAS (conf=100, permanente 11/mai/2026)
- **LONG:** 13.000-14.000 chars = 15min exatos | NUNCA acima de 14.000
- **SHORT:** 725-841 chars = 50-58s
- Psych2Go 28M=15min, Charisma 18M=15min | AdSense 60% de 15min = mesmo ganho de 45% de 20min

## 20 SERIES ETERNAS (tabela series_eternas)
Prioridade 1: Narcisismo(28M Psych2Go), Apego Ansioso(22M)
Prioridade 2: Trauma(19M), Relacionamentos(11M), Ansiedade(15M)
Prioridade 3: Depressao(18M), Burnout(12M), Luto(9M), Autoestima(15M)
Prioridade 4: Dinheiro(8M), Inteligencia Emocional(7M), Vicios(6M), Motivacao(11M), Ansiedade Social(15M)
Prioridade 5: Trauma Geracional(8M), Familia(9M), Personalidade(5M)
Prioridade 6: Neurociencia(6M), Parentalidade(7M), Psicologia Forense(4M)

## 10 PLAYLISTS YOUTUBE (PT + EN + ES)
1. Narcisismo, Manipulacao e Gaslighting / Narcissism, Manipulation & Gaslighting / Narcisismo, Manipulacion y Gaslighting
2. Apego Ansioso e Medo do Abandono / Anxious Attachment & Fear of Abandonment / Apego Ansioso y Miedo al Abandono
3. Trauma de Infancia e Cura / Childhood Trauma & Healing / Trauma Infantil y Sanacion (inclui Familia, Trauma Geracional, Parentalidade)
4. Relacionamentos Toxicos e Padroes / Toxic Relationships & Patterns / Relaciones Toxicas y Patrones
5. Ansiedade, Panico e Pensamentos / Anxiety, Panic & Intrusive Thoughts / Ansiedad, Panico y Pensamientos (inclui Ansiedade Social)
6. Depressao e Burnout Silenciosos / Silent Depression & Burnout / Depresion Silenciosa y Burnout
7. Luto, Perda e Reconstrucao / Grief, Loss & Rebuilding / Duelo, Perdida y Reconstruccion
8. Autoestima, Autossabotagem e Motivacao / Self-Esteem, Self-Sabotage & Motivation / Autoestima, Autosabotaje y Motivacion (inclui Motivacao)
9. Psicologia do Dinheiro e Sucesso / Money Psychology & Success / Psicologia del Dinero y Exito
10. Psicologia e Saude Mental / Psychology & Mental Health / Psicologia y Salud Mental (IE, Vicios, Personalidade, Neurociencia, Forense)

## CALENDARIO S1->S52+infinito (tabela publication_calendar)
- Total: 155 slots | S1=16/mai/2026 -> S52=mai/2027
- Padrao: Sabado 18h (SHORT) + Segunda 12h (LONG) + Quarta 18h (SHORT/LONG)
- Pos-S52: Cerebro gera infinitamente (pub_order 156+)

## 68 CRITERIOS COMPLETOS (tabela criterios_definitivos)

### BLOCO A - ROTEIRO/SCRIPT (1-17)
1. Formula Viral #1: N Sinais De [condicao oculta] CTR 8-12%
2. Formula Viral #2: Voce Nao E X, E Y CTR 10-15%
3. Formula Viral #3: Paradoxo Amor/Destruicao CTR 11-16%
4. [MAIOR] Formula Viral #4: Perigo Oculto Disfarcado CTR 12-18%
5. Formula Viral #5: A Verdade Desconfortavel CTR 9-13%
6. Estrutura minuto-a-minuto 15min (0:00 hook -> 14:00 CTA+cliffhanger)
7. Open Loops: 4-6 por LONG, 1 por SHORT | retencao 72%
8. Pattern Interrupts: a cada 45-90s | min 3 por LONG
9. [OBRIGATORIO] Referencia Cientifica PMID: DSM-5/Bowlby/van der Kolk/PMID real
10. [OBRIGATORIO] Anti-Plagio: Casos ficticios com nome+profissao (Maria/Carlos/Ana/Pedro/Joao/Lucas/Sofia/Rafael)
11. Hook Paradoxal nos primeiros 3s | NUNCA saudacao
12. Validacao Emocional nos primeiros 30s (LONG)
13. CTA Final 600 chars + Cliffhanger (LONG)
14. Pergunta para Comentarios Fixados (mid-video)
15. Binge Architecture: Episodio N de 155, serie [NOME]
16. Funil SHORT->LONG: ultimas linhas apontam para versao completa
17. [IMUTAVEL] Duracao: LONG 13.000-14.000 chars / SHORT 725-841 chars

### BLOCO B - SEO E ALGORITMO (18-24)
18. Titulo SEO: primeiras 3 palavras = termo mais buscado | 60-70 chars
19. [OBRIGATORIO] Titulos Trilingues: PT-BR (padrao) + EN + ES
20. Descricao 150 chars: template [Voce tem X]? Daniela explica [N sinais]. Assista ate o final.
21. Hashtags: #psicologia #saudemental #apegoansioso #narcisismo #trauma + tema especifico
22. [OBRIGATORIO] Tags Piramide: 15-20 tags (3 broad + 5 mid + 7+ long-tail + EN + ES)
23. Chapters/Timestamps: +23% watch time + rich results Google (LONG)
24. Timing: Sabado 18h / Segunda 12h / Quarta 18h BRT

### BLOCO C - IMAGENS E THUMBNAIL (25-32)
25. Thumbnail Quantica: espelhar layout psicologico do viral de referencia
26. Estilo Psych2Go: personagem humanoide sem rosto + numero grande + fundo solido
27. Paleta por Serie: Narcisismo=vermelho+preto | Apego/Trauma=roxo+branco | Ansiedade=azul+branco | Autoestima=amarelo+preto
28. 5 Elementos obrigatorios: numero destaque + expressao extrema + texto 3-5 palavras bold + contraste + elemento paradoxal
29. Teste A/B: 2 thumbnails em 48h | manter maior CTR
30. Mudanca visual 30-45s: Ken Burns + texto sincronizado + barra progresso
31. Texto na tela por cor: alerta=vermelho, alivio=verde, revelacao=amarelo
32. Render: 1920x1080 H.264 CRF18 30fps | Shorts 1080x1920 | -14 LUFS

### BLOCO D - AUDIO (33-35)
33. TTS: ThalitaMultilingualNeural/FranciscaNeural | rate variavel | 130-140 pal/min | pausas 0.8-1.2s antes revelacoes
34. Musica CC0: lo-fi -22dB narrativa / -15dB CTA | freemusicarchive.org, ccmixter.org
35. Silencio Estrategico: 2-3s antes de revelacao = +40% retencao no ponto

### BLOCO E - DISTRIBUICAO E ENGAJAMENTO (36-37)
36. End Screen CTA Duplo: proximo video nomeado + inscricao | CTR 12-18%
37. Comentarios 2h: fixar pergunta + responder todos -> +35% alcance organico

### BLOCO F - MONETIZACAO (38-41)
38. Mid-Roll apos Cliffhanger: 4:30 / 8:00 / 11:30 | skip rate -40% | RPM R$4-6/mil views
39. Fase 0->1K: Google Ads R$600 | video ancora Narcisismo espelho 28M
40. Fase 1K->10K: 3 videos/semana + Shorts diarios + SEO organico | 10K em 90-180d
41. Fase 10K+: Patrocinio R$800-3K + Ebook R$37-97 + Curso R$197-497 + AdSense R$15K-50K/mes

### BLOCO G - ANALYTICS (42-43)
42. Feedback Loop 48h: CTR>4% | Retencao>35% LONG / >55% SHORT
43. Topicos Explosivos: Dark Psychology +67% | narcisismo encoberto | CPTSD

### BLOCO H - CRITERIOS QUANTICOS (44-47)
44. Quantum Ref: todo video espelha 1 dos 18 virais (1.8M-28M) | tabela viral_videos_reference
45. Playlist + Serie + Pub_Order definidos ANTES do render
46. Score Gate: >=95/100 | 4 blocos: Script(25)+SEO(25)+Viral(30)+Distrib(20)
47. Storage <=900 MB monitorado a cada render

### BLOCO I - PNL NEUROLINGUSTICA (48-54)
48. [OBRIGATORIO] Pressuposi??es: Quando voce percebe que tem X... (nao "se voce tem X") CTR +40%
49. [OBRIGATORIO] Yes-Set Cialdini: 3 acordos mentais antes do CTA -> inscricao +85%
50. [OBRIGATORIO] Pacing & Leading: espelhar realidade -> conduzir ao insight | rapport instantaneo
51. [OBRIGATORIO] Reframe Identitario: Voce nao e X, e Y | compartilhamento +200% | 1-2x por video
52. Future Pacing: Imagine como vai ser quando... | apos 6min LONG / 40s SHORT
53. Milton Model: linguagem vaga = projecao universal + casos ficticios especificos
54. Comandos Embutidos: Conforme voce CONTINUA ASSISTINDO... | 2-3x LONG, 1x SHORT

### BLOCO J - ENGENHARIA DE ATENCAO (55-63)
55. [OBRIGATORIO] Recompensa Variavel (Skinner): insights em ritmo IMPROVISIVEL | Psych2Go retencao 72%
56. [OBRIGATORIO] Efeito Zeigarnik: loops abertos = abas mentais que nao fecham
57. [OBRIGATORIO] Curiosity Gap (Loewenstein): tensao saber/querer saber | titulo + thumbnail + hook
58. Dopamine Drip: micro-recompensas | sinal 3 surpreendente, mas espera o 7 | Huberman + Hormozi
59. Identity Lock (Gary Vee): Pessoas que entendem isso estao um passo a frente
60. Ameaca Social (Cialdini): maioria nunca percebe | max 2x por video
61. Reciprocidade: dar insight ANTES do CTA | paradoxalmente aumenta conversao | MrBeast
62. [OBRIGATORIO] Escalonamento de Stakes (MrBeast): cada 2min algo mais urgente | sinal 1->10 crescendo
63. Pattern Interrupt Hipnotico (Derren Brown): Aguarda. Isso e importante. | a cada 45-90s

### BLOCO K - SEO MUNDIAL (64-68)
64. VideoObject Schema.org: rich results Google | +35% CTR organico
65. YouTube SEO trilingue: tags EN+ES + localizacao em 3 idiomas via YouTube Studio
66. [OBRIGATORIO] Legendas SRT PT+EN+ES: YouTube indexa texto | 3x superficie indexacao
67. [OBRIGATORIO] Engenharia de Compartilhamento: 1 frase por video projetada para ser ENVIADA
68. Thumbnail OCR: texto visivel indexado pelo Google Images

## MASTER PROMPT DOS 37 HACKS
- Tabela: master_prompts | Nome: 37_hacks_daniela_v1 (V2 com PNL e Atencao)
- Usado em: enhance_script.py em TODAS as chamadas LLM como system_prompt
- Funcoes SQL: get_master_prompt_37hacks() | build_37hacks_prompt(p_id)

## SCORE V4 - FUNCAO score_pipeline_real(id)
| Bloco | Pts | Criterios |
|-------|-----|-----------|
| Script | 25 | existe(10) + comprimento LONG 13k-14k / SHORT 725-841 (15) |
| SEO Algoritmo | 25 | titulo viral(10) + seo>=99(5) + tags>=15(5) + trilingue EN+ES(5) |
| Qualidade Viral | 30 | ref PMID(15) + hook 200chars(5) + open loops(5) + casos ficticios(5) |
| Distribuicao | 20 | pub_order(5) + playlist(5) + quantum_ref(5) + duracao correta(5) |
| GATE | 95/100 | abaixo = enhance_script melhora, max 5 tentativas |

## CASOS FICTICIOS OBRIGATORIOS (anti-plagio)
Maria(trauma/professora) | Carlos(narcisismo/gerente) | Ana(ansiedade/designer) | Pedro(impostor/dev) | Joao(luto/medico) | Lucas(burnout/advogado) | Sofia(apego/nutricionista) | Rafael(perfeccionismo/empresario)

## REFERENCIAS CIENTIFICAS OBRIGATORIAS
DSM-5 | John Bowlby (teoria apego) | Bessel van der Kolk (trauma) | Brene Brown (vergonha) | Ramani Durvasula (narcisismo) | Kubler-Ross (luto) | + PMID ou Journal especifico

## GUIA PUBLICACAO MANUAL - checklist
Antes: MP4 pronto | score>=95 | PNL checklist | casos ficticios | ref cientifica | thumbnail
YouTube Studio: titulo PT+EN+ES | descricao 150 chars | 15-20 tags | chapters LONG | playlist | thumbnail personalizada | horario agendado | legendas SRT | tela final
Primeiras 2h: comentario fixado + responder todos + curtir todos + NAO apagar negativos 24h

## ORDEM PUBLICACAO S1-S6 (critica - referencia original)
#1 Sab 16/mai 18h SHORT Narcisismo | #2 Seg 18/mai 12h SHORT Apego | #3 Qua 20/mai 18h LONG Narcisismo
#4 Sab 23/mai 12h SHORT Depressao | #5 Seg 25/mai 18h LONG Apego | #6 Qua 27/mai 12h SHORT Ansiedade
#7 Sab 30/mai 18h LONG Trauma | #8 Seg 01/jun 12h SHORT Autoestima | #9 Qua 03/jun 18h SHORT Autoestima
#10 Sab 06/jun 12h LONG Trauma | #11 Seg 08/jun 18h SHORT Relacionamentos | #12 Qua 10/jun 12h LONG Relacionamentos
#13 Sab 13/jun 18h LONG Trauma | #14 Seg 15/jun 12h SHORT Apego | #15 Qua 17/jun 18h LONG Relacionamentos
#16 Sab 20/jun 12h LONG Dinheiro | #17 Seg 22/jun 18h LONG Apego

## VIRAL REFERENCES TOP (tabela viral_videos_reference)
#1: Psych2Go 28M Covert Narcissist | #2: Psych2Go 22M Abandonment | #3: Psych2Go 19M Childhood Trauma
#4: Charisma 18M Toxic Parents | #5: Psych2Go 15M Social Anxiety | #6: Improvement Pill 15M Lazy
#7: Charisma 12M Narcissists Reveal | #8: DoctorRamani 9M Abandonment | #9-18: 1.8M-8M range

## PLANO DE CRESCIMENTO
0->1K (S1-S17): Google Ads R$600 | targeting BR+PT 18-45 | video ancora narcisismo espelho 28M
1K->10K (S18-S26): AdSense ativo | 3 videos/semana + Shorts diarios | SEO organico | 10K em 90-180d
10K+ (S34+): Patrocinio R$800-3K + Ebook R$37-97 + Curso R$197-497 + AdSense R$15K-50K/mes
100K subs: Canais EN+ES separados | R$50K/mes | Eternamente autonomo

## LINKS
Galeria S1-S52: https://tpjvalzwkqwttvmszvie.supabase.co/storage/v1/object/public/videos/galeria-completa.html
Dashboard: https://repovazio.vercel.app/admin.html
Videos: https://repovazio.vercel.app/videos-prontos.html
Setup tokens: https://repovazio.vercel.app/setup-tokens.html

## CREDENCIAIS STATUS
OK: NVIDIA, GROQ, OpenAI, ElevenLabs, GH_PAT, Vercel, Supabase
Pendente (setup-tokens.html): INSTAGRAM_ACCESS_TOKEN, TIKTOK_ACCESS_TOKEN, WHATSAPP_TOKEN
YouTube OAuth: psidanielacoelho1982@gmail.com

## BLOCO L - VISUAL MUNDIAL (78 criterios total — os 10 mais importantes)

### L-VISUAL OBRIGATORIO EM 100% DOS VIDEOS

REGRA MESTRE: TODA thumbnail, TODA imagem no video, TODA escolha de cor e texto
DEVE seguir os padroes comprovados dos maiores canais mundiais de psicologia.
NAO existe video sem padrao visual de nivel mundial. Se nao tiver, refaz.

---

**69 - THUMBNAIL PADRAO PSYCH2GO (28M subs) — PRINCIPAL OBRIGATORIO:**
ESTRUTURA: personagem humanoide SEM ROSTO (corpo expressivo) no centro/esquerda
+ fundo solido COR UNICA saturada (sem gradiente) + numero extra-large amarelo/branco
+ texto 3-5 palavras bold branco. Personagem ocupa 50-60% do frame.
Cores por serie: roxo #7C3AED (trauma/apego) | vermelho #E11D48 (narcisismo) |
azul #2563EB (ansiedade) | amarelo #F59E0B (autoestima).
CTR validado: 8-12%. Ferramenta: Canva. OBRIGATORIO em 100% dos videos.

**70 - THUMBNAIL CHARISMA ON COMMAND (18M) — para urgencia/perigo:**
Rosto humano real com expressao extrema (choque/medo) no lado direito
+ fundo dividido (metade escura esquerda + foto direita)
+ texto grande na area escura. CTR 10-15%.
Usar em: narcisismo, gaslighting, love bombing, manipulacao.

**71 - THUMBNAIL IMPROVEMENT PILL (15M) — minimalismo:**
Fundo escuro #1a1a2e + personagem stick figure ou icone simples
+ texto extra-bold branco/amarelo ocupando 40% do frame. Zero decorativo.
CTR 7-10%. Usar em: autossabotagem, motivacao, procrastinacao.

**72 - ESTILO HUBERMAN LAB (20M+) — credibilidade cientifica:**
Fundo preto ou azul escuro profissional + foto profissional de Daniela
ou icone cerebral/neuronal + texto clean branco sem serifa
+ selo de credibilidade (DSM-5, "CIENCIA COMPROVA"). CTR 6-9% mas retencao 45%+.
Usar em: neurociencia, inteligencia emocional, dopamina.

**73 - MRBEAST RULE #1 — thumbnail SEMPRE entrega a promessa do titulo:**
Imagem representa EXATAMENTE o que o titulo promete. NUNCA imagem generica.
TESTE: mostrar thumbnail sem titulo — espectador adivinha o tema em 3 segundos.
CTR 2x maior que thumbnails genericas. OBRIGATORIO 100%.

**74 - IMAGENS DENTRO DO VIDEO — Ken Burns padrao Psych2Go:**
Imagens 2D ilustradas (nao fotos — evita copyright) + personagens sem rosto
expressando a emocao + Ken Burns 100%->110% zoom lento + mudanca a cada 30-45s
+ texto overlay sincronizado com TTS + cor de fundo por emocao do trecho:
neutro=#1a1a2e | tensao=#3d0000 | alivio=#0d1a0d | revelacao=#1a1a00.
Implementado em video_gen_v2.py.

**75 - TEXTO OVERLAY SINCRONIZADO COM TTS:**
DM Sans ou Montserrat Bold 52-64px + fade-in 0.3s + posicao 80% do frame (baixo)
+ cor por emocao: alerta=#E11D48 | alivio=#10B981 | revelacao=#F59E0B | ciencia=#2563EB.
Max 6 palavras por overlay. SEMPRE outline/sombra para legibilidade. Retencao 72%.

**76 - SHORTS VISUAL 1080x1920 — padrao TikTok/Reels:**
Hook visual nos 0.5s iniciais + legenda sempre visivel (20-30% tela inferior, bold, fundo semitransparente)
+ corte a cada 3-5s + zoom-in progressivo 100%->115% + thumbnail do Long nos ultimos 3s.
NUNCA barras pretas laterais — usar zoom/crop para preencher vertical.

**77 - PALETA EMOCIONAL COMPLETA POR SERIE:**
Narcisismo: #E11D48+#1a0005 (vermelho+preto) | Apego: #7C3AED+#0a0015 (violeta+preto)
Trauma: #8B5CF6+#0d0020 | Relacionamentos: #0D9488+#001a18 | Ansiedade: #2563EB+#00051a
Depressao/Burnout: #64748B+#0a0a15 | Luto: #6B7280+#0f0f0f
Autoestima: #D97706+#1a0e00 | Dinheiro: #F59E0B+#1a0f00
Aplicar EM TUDO: thumbnail + overlay + barra progresso + lower third.

**78 - LOWER THIRD DANIELA COELHO — branding como Psych2Go:**
"Daniela Coelho | Psicologa Clinica . @psidanielacoelho"
Retangulo roxo #7C3AED 70% opacidade + texto branco DM Sans + icone psi esquerda.
400x60px bottom-left. Slide-in 0.5s. Aparece em 0:30-1:00 e end screen.
Watermark psi 10% opacidade canto superior direito durante todo o video.
Psych2Go usa lower third em 100% dos videos = brand recall 89% entre inscritos.

---

TOTAL: 78 criterios | Blocos A-L | Score gate 95/100 | 100% de todos os videos S1->S52->infinito

## BLOCO M — OCEANO AZUL + IDENTIDADE VISUAL DA MARCA (criterios 79-84)

### 79 — OCEANO AZUL: Posicionamento Único no Brasil e no Mundo
O mercado de psicologia BR é OCEANO VERMELHO de canais genéricos.
psicologia.doc opera no OCEANO AZUL com visual ÚNICO:
- Psych2Go = cartoon 2D simplista (canal EN)
- BrainCraft = cientifico frio sem emocao (EN)
- Canais BR = talking heads sem identidade visual
- psicologia.doc = UNICO canal PT-BR com visual de documentario Netflix Explained + emocao

RESULTADO: zero competicao direta no Brasil. Potencial global EN+ES sem redesign.
NUNCA abandonar este posicionamento. NUNCA imitar o visual dos outros.

### 80 — IDENTIDADE VISUAL COMPLETA (criada 12/mai/2026, ATIVA)
SIMBOLO: psi (simbolo oficial de psicologia) redesenhado exclusivo
- Corpo vertical + dois bracos curvos + barra horizontal
- SVG disponivel em: repovazio.vercel.app/brand/

PALETA OFICIAL (imutavel):
- #06060F Deep Void (background principal de tudo)
- #5B21B6 Amethyst (cor da marca / logo)
- #7C3AED Violet (acento principal / CTAs / UI)
- #E11D48 Crimson (emocao / urgencia / narcisismo)
- #F59E0B Neural Gold (dados / ciencia / numeros)
- #0D9488 Data Teal (series / episodios)
- #F0F4FF Mind Frost (texto principal sobre fundo escuro)
- #C4B5FD Mist (texto secundario / subtitulos)

TIPOGRAFIA OFICIAL:
- Georgia serif: titulos / display / thumbnails / headlines
- DM Sans: UI / labels / descricoes
- DM Mono: dados / stats / handles (@psidanielacoelho) / timestamps

TAGLINE: "A ciencia que explica quem voce e."
CONCEITO: "Documentary Meets Emotion" / "Mentes em Evidencia"

### 81 — 4 TIPOS DE THUMBNAIL (templates em /brand/thumb-generator.html)
VIRAL (roxo #7C3AED): apego ansioso, relacionamentos, cura
CRIME (crimson #E11D48): narcisismo, gaslighting, manipulacao, perigo
FACT (teal #0D9488): dados cientificos, estudos, neurociencia
GOLD (amber #F59E0B): burnout, autoestima, dinheiro, series

ELEMENTOS FIXOS em TODOS os thumbnails:
- Linha lateral colorida 6px (acento da serie)
- Padrao neural SVG (constelacao, opacity 0.08)
- Handle @psidanielacoelho (canto superior esquerdo)
- Simbolo psi (canto superior direito, cor do acento)
- Titulo em Georgia serif bold (inferior)
- Gradiente inferior 60% preto para legibilidade
- Legivel em 100x56px no mobile

### 82 — 7 REGRAS ANTI-BLOQUEIO DA IDENTIDADE VISUAL
1. ZERO rostos famosos — persona psicóloga sem rosto real
2. Imagens 100% originais via Flux.1 Schnell (nunca stock)
3. Estatísticas REAIS (OMS, Harvard, DSM-5) citadas no vídeo
4. Persona credível (Daniela Coelho, Psicóloga Clínica)
5. Sem clickbait — título cumpre promessa (MrBeast rule)
6. Sem imitacao de marcas — visual 100% proprio
7. Conteúdo psicológico legítimo baseado em ciência real

### 83 — EXPANSÃO GLOBAL PT+EN+ES
Fase atual (0→25K): PT-BR como base
Fase futura (25K+): psychology.doc (EN) + psicologia.doc (ES)
Mesma identidade visual — apenas troca de idioma no texto
Paleta + símbolo ψ + tipografia = universal, sem alteração

### 84 — PADRÃO NEURAL DE FUNDO (marca visual diferenciadora)
Todas as produções usam rede de conselações com pontos e linhas em baixa opacidade:
- Thumbnails: opacity 0.08
- Banners YouTube: opacity 0.12
- Posts Instagram: opacity 0.10
- Cor: roxo #7C3AED nos pontos, vermelho #E11D48 nos halos
- Cria identidade imediata mesmo sem textos
- Sensação de "mapa mental/neural" alinhada ao conceito psicologia
- Diferenciação radical de TODOS os outros canais

### LINKS DE BRAND ATIVOS
Thumbnails: https://repovazio.vercel.app/brand/thumb-generator.html
Banner YT: https://repovazio.vercel.app/brand/youtube-banner.html
Instagram: https://repovazio.vercel.app/brand/instagram-templates.html

---
TOTAL DEFINITIVO: 84 criterios | Blocos A-M | $0/mes | S1->S52->infinito
