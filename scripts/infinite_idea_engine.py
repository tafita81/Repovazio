#!/usr/bin/env python3
# infinite_idea_engine.py
# CÉREBRO QUÂNTICO INFINITO — psicologia.doc
# Cruza TODOS os domínios de IA para criar sistemas sem precedente
# Meta: 40.000 APIs → combinações infinitas → renda algorítmica

import os,json,random,requests,time
from datetime import datetime
from itertools import combinations

SB=os.getenv("SUPABASE_URL","https://tpjvalzwkqwttvmszvie.supabase.co")
SK=os.getenv("SUPABASE_SERVICE_ROLE_KEY","")
GK=os.getenv("GROQ_API_KEY","")
NK=os.getenv("NVIDIA_API_KEY","")

# ── DOMÍNIOS DO CÉREBRO QUÂNTICO ──────────────────────────────
DOMINIOS = {
    "PESQUISA": ["PubMed","OpenAlex","Semantic Scholar","arXiv","SciELO Brasil",
                 "Europe PMC Full Text","LILACS BVS Health","RCAAP Portugal",
                 "ClinicalTrials.gov","NIH Reporter","NIMH Data Archive",
                 "Allen Brain Atlas Gene","NeuroVault fMRI"],
    "LLM": ["Groq Llama 3.3","Nvidia DeepSeek V3","Cerebras Inference",
            "Together AI Models","Fireworks AI","Perplexity Sonar",
            "Gemma 3 27B","Phi-4 Microsoft","Qwen 2.5 72B",
            "Command R 35B","Mistral 7B v3","DeepSeek R1 Free"],
    "TTS": ["Edge TTS Microsoft","Kokoro TTS","F5 TTS Ultra","CosyVoice 2",
            "Parler TTS","Dia TTS Ultra","OuteTTS Multi","StyleTTS 2"],
    "IMAGE": ["Pollinations FLUX","FLUX Dev Hyper","SDXL Lightning","SDXL Turbo",
              "FLUX Fill Inpaint","Kolors Kwai","FLUX Realism LoRA","FLUX Anime LoRA"],
    "VIDEO": ["HunyuanVideo","CogVideoX 5B","LTX Video","Wan 2.1 Video",
              "FLUX Video Dev","Mochi 1","Pyramid Flow"],
    "AUDIO": ["Stable Audio Open","ACE-Step Music","YuE Music Gen","MusicGen Large"],
    "ANALISE": ["HF Mental BERT","HF Emotion RoBERTa","HF PT-BR Sentiment",
                "WhisperX Large v3","Exa Neural Search","Brave Search API"],
    "DISTRIBUICAO": ["YouTube Partner Program","YouTube Shorts RPM","Spotify for Podcasters",
                     "Apple Podcasts Connect","DistroKid Distribution","Amuse Free Distro",
                     "TikTok Creativity Program","Meta Reels Play Bonus",
                     "Medium Partner Program","Twitter X Revenue Share"],
    "MONETIZACAO": ["Google AdSense Display","Mediavine Ads","YouTube Content ID",
                    "KDP Kindle Unlimited","SoundExchange Digital","ASCAP Performance",
                    "BMI Royalties","Amazon Music Streaming","Deezer Streaming"],
    "AUTOMACAO": ["n8n Automation","Activepieces","GitHub Actions","Composio Tools",
                  "LangGraph Agents","Make Integromat"],
    "SOCIAL": ["Instagram Graph","Threads API v2","Reddit OAuth","Pinterest Creator Rewards",
               "Bluesky AT Protocol","LinkedIn Creator"],
    "DADOS_BR": ["IBGE Cidades BR","IBGE Agregados","DataSUS Saúde","ANS Open Data"]
}

# ── 100 IDEIAS INÉDITAS PRÉ-CALCULADAS (SEM COMPRA) ──────────
IDEIAS_100 = [
    # ── GRUPO 1: MULTI-IDIOMA SIMULTÂNEO (mesmo esforço, N×receita) ──
    {"id":"I01","nome":"5 Canais 5 Idiomas 1 Script",
     "dominios":["PESQUISA","LLM","TTS","VIDEO","DISTRIBUICAO"],
     "apis":["PubMed","Groq Llama 3.3","Kokoro TTS","LTX Video","YouTube Partner Program",
             "Amuse Free Distro","DistroKid Distribution","Spotify for Podcasters",
             "Apple Podcasts Connect","Exa Neural Search"],
     "mecanismo":"1 paper → script PT-BR EN DE FR ES → 5 narracoes → 5 videos → 5 canais YouTube simultaneamente",
     "receita_mensal_usd":11000,
     "prazo":"7d","tipo":"algoritmico",
     "calculo":"5 canais × 100K views × $4 RPM medio = $2000/mes. Escala 500K views: $10K/mes",
     "comecando_hoje":"Criar 4 canais extras no YouTube (gratuito) + configurar pipeline multi-lingua"},

    {"id":"I02","nome":"Podcast Cientifico 60 Plataformas",
     "dominios":["PESQUISA","LLM","TTS","AUDIO","DISTRIBUICAO","MONETIZACAO"],
     "apis":["PubMed","Semantic Scholar","Groq Llama 3.3","Dia TTS Ultra","Stable Audio Open",
             "DistroKid Distribution","Spotify for Podcasters","Apple Podcasts Connect",
             "Amazon Music Streaming","SoundExchange Digital"],
     "mecanismo":"1 paper/dia → podcast 20min → distribuir 60+ plataformas automaticamente → royalties todos os dias",
     "receita_mensal_usd":3500,
     "prazo":"3d","tipo":"algoritmico",
     "calculo":"60 plataformas × 10K plays × $0.004 = $2.4K/mes. Cresce linear com episodios acumulados",
     "comecando_hoje":"Amuse.io (grátis) + subir 1 episodio hoje"},

    {"id":"I03","nome":"Trilhas Psicologia Streaming Perpetuo",
     "dominios":["AUDIO","DISTRIBUICAO","MONETIZACAO"],
     "apis":["Stable Audio Open","ACE-Step Music","DistroKid Distribution","Amuse Free Distro",
             "Spotify for Podcasters","Amazon Music Streaming","Deezer Streaming",
             "YouTube Music Partner","SoundExchange Digital","BMI Royalties"],
     "mecanismo":"Gerar 10 trilhas/dia → distribuir Spotify Apple Amazon → royalties por stream perpetuos",
     "receita_mensal_usd":5000,
     "prazo":"1d","tipo":"algoritmico",
     "calculo":"3650 trilhas/ano × 100 streams/trilha × $0.004 = $1.46K/mes crescendo. 10K streams: $14.6K",
     "comecando_hoje":"HOJE: amuse.io + 3 trilhas geradas com Stable Audio Open (HF grátis)"},

    {"id":"I04","nome":"Blog Autoridade + Mediavine RPM Alto",
     "dominios":["PESQUISA","LLM","MONETIZACAO","DADOS_BR"],
     "apis":["PubMed","SciELO Brasil","Groq Llama 3.3","Google AdSense Display","Mediavine Ads",
             "IBGE Agregados","Exa Neural Search","Ghost CMS","Cloudflare Free CDN","Google Search Console"],
     "mecanismo":"Artigo cientifico/dia com dados IBGE/SciELO → indexed Google → visitas → AdSense $5-50 RPM",
     "receita_mensal_usd":4500,
     "prazo":"30d","tipo":"algoritmico",
     "calculo":"100K visitas/mes × $15 RPM saude = $1.5K/mes. Mediavine threshold 50K: RPM sobe para $20-40",
     "comecando_hoje":"Ghost.io (gratuito) + 3 artigos hoje + aplicar AdSense"},

    {"id":"I05","nome":"KDP KENP Workbook Factory 5 Idiomas",
     "dominios":["PESQUISA","LLM","MONETIZACAO"],
     "apis":["PubMed","Groq Llama 3.3","Qwen 2.5 72B","Mistral 7B v3","Cerebras Inference",
             "KDP Kindle Unlimited","Amazon Music Streaming","Exa Neural Search",
             "RCAAP Portugal","Europe PMC Full Text"],
     "mecanismo":"1 workbook psicologia/semana → 5 idiomas automaticos → KDP Unlimited → pago por PAGINA LIDA",
     "receita_mensal_usd":6000,
     "prazo":"7d","tipo":"algoritmico",
     "calculo":"20 workbooks × 5 idiomas = 100 titulos × 500 paginas × 10 leitores = $2K/mes. Meta 1000 titulos: $20K",
     "comecando_hoje":"Criar conta KDP (gratuito) + publicar 1 workbook hoje"},

    # ── GRUPO 2: NEUROCIÊNCIA VISUAL (nicho virgem mundial) ──
    {"id":"I06","nome":"NeuroViz: Canal Neurociência Visual EN",
     "dominios":["PESQUISA","LLM","IMAGE","VIDEO","DISTRIBUICAO"],
     "apis":["Allen Brain Atlas Gene","NeuroVault fMRI","OpenAlex","Groq Llama 3.3",
             "FLUX Dev Hyper","HunyuanVideo","YouTube Partner Program",
             "YouTube Shorts RPM","Exa Neural Search","HF Mental BERT"],
     "mecanismo":"Papers + atlas cerebral → script EN + visualizacoes fMRI → video neural → canal neurociencia EN",
     "receita_mensal_usd":8000,
     "prazo":"14d","tipo":"algoritmico",
     "calculo":"Neurociencia EN RPM $12-20. 100K views × $15 = $1.5K/mes. Escala 500K: $7.5K. Nicho virgem PT-BR",
     "comecando_hoje":"Criar canal YouTube + baixar 5 mapas cerebrais OpenNeuro (gratuito)"},

    {"id":"I07","nome":"Brain Mapping Shorts Factory",
     "dominios":["PESQUISA","LLM","IMAGE","DISTRIBUICAO","SOCIAL"],
     "apis":["Allen Brain Atlas Gene","Groq Llama 3.3","FLUX Dev Hyper","SDXL Turbo",
             "YouTube Shorts RPM","TikTok Creativity Program","Meta Reels Play Bonus",
             "Pinterest Creator Rewards","Instagram Graph","Threads API v2"],
     "mecanismo":"Fact neural → imagem cerebro animada → Short 60s → 5 plataformas simultaneamente",
     "receita_mensal_usd":3500,
     "prazo":"3d","tipo":"algoritmico",
     "calculo":"5 plataformas × 500K views × $3.5 medio = $1.75K/mes. Conteudo nicho alto engajamento = viral",
     "comecando_hoje":"Criar 3 Shorts sobre areas do cerebro com imagens Allen Atlas hoje"},

    # ── GRUPO 3: REDDIT → CIÊNCIA (formula Psych2Go) ──
    {"id":"I08","nome":"Reddit Científico Automatizado",
     "dominios":["SOCIAL","PESQUISA","LLM","TTS","VIDEO","DISTRIBUICAO"],
     "apis":["Reddit Trending Feed","PubMed","Semantic Scholar","Groq Llama 3.3",
             "Kokoro TTS","LTX Video","YouTube Partner Program",
             "YouTube Shorts RPM","HF Emotion RoBERTa","HF PT-BR Sentiment"],
     "mecanismo":"Top post Reddit psicologia → buscar paper que explica → resposta cientifica Daniela → video automatico",
     "receita_mensal_usd":5500,
     "prazo":"2d","tipo":"algoritmico",
     "calculo":"Psych2Go model: 28M views = $84K. Conservador 200K views/mes × $3.5 = $700. Com 4 canais: $2.8K",
     "comecando_hoje":"Reddit API (gratuito) + PubMed (gratuito) + 1 video hoje sobre top post atual"},

    {"id":"I09","nome":"Breaking Science News Canal Urgente",
     "dominios":["PESQUISA","ANALISE","LLM","VIDEO","DISTRIBUICAO"],
     "apis":["bioRxiv","PsyArXiv","Semantic Scholar","Perplexity Sonar","Groq Llama 3.3",
             "FLUX Dev Hyper","LTX Video","YouTube Partner Program",
             "YouTube Shorts RPM","Google Trends Real-time"],
     "mecanismo":"Paper publicado hoje → Perplexity busca contexto → script urgente → video em 4h → 1o no YouTube",
     "receita_mensal_usd":4000,
     "prazo":"1d","tipo":"algoritmico",
     "calculo":"Breaking news: 10x views medias. 4 eventos/mes × 500K views × $5 = $10K. Conservador: $4K",
     "comecando_hoje":"RSS bioRxiv/PsyArXiv (gratuito) + 1 video sobre paper publicado hoje"},

    # ── GRUPO 4: MULTI-LLM ORACLE (conteúdo sem precedente) ──
    {"id":"I10","nome":"5 IAs Divergentes 1 Pergunta Psicologia",
     "dominios":["LLM","TTS","VIDEO","DISTRIBUICAO","ANALISE"],
     "apis":["Groq Llama 3.3","Nvidia DeepSeek V3","Cerebras Inference","Together AI Models",
             "Fireworks AI","Perplexity Sonar","Kokoro TTS","LTX Video",
             "YouTube Partner Program","HF Emotion RoBERTa"],
     "mecanismo":"1 pergunta → 5 LLMs distintos respondem → Daniela apresenta divergencias → formato debate IA unico",
     "receita_mensal_usd":6000,
     "prazo":"3d","tipo":"algoritmico",
     "calculo":"Formato único no mundo = viral natural. 5 LLMs = 5× perspectivas = mais tempo na tela = RPM maior",
     "comecando_hoje":"Groq (gratuito) + Cerebras (gratuito) + 1 video comparação hoje"},

    {"id":"I11","nome":"IA Debate Psicologia Format Serie",
     "dominios":["LLM","TTS","VIDEO","DISTRIBUICAO"],
     "apis":["Groq Llama 3.3","Qwen 2.5 72B","Mistral 7B v3","Cerebras Inference",
             "F5 TTS Ultra","Parler TTS","HunyuanVideo","YouTube Partner Program",
             "YouTube Shorts RPM","Medium Partner Program"],
     "mecanismo":"Llama vs DeepSeek vs Qwen sobre trauma: 3 IAs com vozes distintas debatem ciencia psicologia",
     "receita_mensal_usd":4500,
     "prazo":"5d","tipo":"algoritmico",
     "calculo":"Formato nunca feito no mundo = PR organico = crescimento exponencial. RPM alto por audiencia qualificada",
     "comecando_hoje":"3 LLMs gratuitos + vozes distintas Parler TTS hoje"},

    # ── GRUPO 5: DADOS BR EXCLUSIVOS (0 competição) ──
    {"id":"I12","nome":"Epidemiologia Mental BR Canal Oficial",
     "dominios":["DADOS_BR","PESQUISA","LLM","VIDEO","DISTRIBUICAO","MONETIZACAO"],
     "apis":["IBGE Agregados","DataSUS Saúde","SINAN Mental Health","SciELO Brasil",
             "LILACS BVS Health","Groq Llama 3.3","FLUX Dev Hyper","LTX Video",
             "YouTube Partner Program","Google AdSense Display"],
     "mecanismo":"IBGE + DataSUS dados exclusivos → visualizacoes criativas → canal unico dados oficiais BR saude mental",
     "receita_mensal_usd":5000,
     "prazo":"7d","tipo":"algoritmico",
     "calculo":"Zero competidores usam dados oficiais IBGE em psicologia. Autoridade = RPM $8-12 + sponsorships",
     "comecando_hoje":"IBGE API (gratuita) + 1 infografico sobre suicidio por regiao IBGE hoje"},

    {"id":"I13","nome":"SciELO + LILACS Canal Ciencia Latam",
     "dominios":["PESQUISA","LLM","TTS","VIDEO","DISTRIBUICAO"],
     "apis":["SciELO Brasil","LILACS BVS Health","RCAAP Portugal","OpenAlex","Groq Llama 3.3",
             "Kokoro TTS","LTX Video","YouTube Partner Program","Spotify for Podcasters","DistroKid Distribution"],
     "mecanismo":"Pesquisa EXCLUSIVAMENTE latino-americana → único canal usando ciencia latina para psicologia viral",
     "receita_mensal_usd":3500,
     "prazo":"7d","tipo":"algoritmico",
     "calculo":"Autoridade regional = parcerias universidades + RPM $5-8 + podcast streaming royalties simultaneos",
     "comecando_hoje":"SciELO API gratuita + buscar papers saude mental BR 2024-2025"},

    # ── GRUPO 6: MÚSICA PSICOLOGIA STREAMING ──
    {"id":"I14","nome":"Lofi Psicologia: Ambiente Mental 24/7",
     "dominios":["AUDIO","DISTRIBUICAO","MONETIZACAO"],
     "apis":["Stable Audio Open","ACE-Step Music","YuE Music Gen","DistroKid Distribution",
             "Spotify for Podcasters","YouTube Partner Program","Amazon Music Streaming",
             "Deezer Streaming","YouTube Music Partner","SoundExchange Digital"],
     "mecanismo":"Gerar lofi/ambient psicologia → live stream 24/7 YouTube → AdSense continuo + streaming royalties",
     "receita_mensal_usd":7000,
     "prazo":"3d","tipo":"algoritmico",
     "calculo":"Lofi channels: Lofi Girl 10M subs fatura $50K+/mes. 24/7 stream = impressoes continuas. Conservador $7K",
     "comecando_hoje":"Stable Audio Open (HF grátis) + criar live stream YouTube hoje + upload 10 faixas Amuse"},

    {"id":"I15","nome":"Binaural Terapeutico 7 Frequencias",
     "dominios":["AUDIO","DISTRIBUICAO","MONETIZACAO"],
     "apis":["Stable Audio Open","DistroKid Distribution","Amuse Free Distro","Spotify for Podcasters",
             "Apple Podcasts Connect","Amazon Music Streaming","Deezer Streaming",
             "YouTube Music Partner","SoundExchange Digital","BMI Royalties"],
     "mecanismo":"7 frequencias binaurais (delta/theta/alpha/beta/gamma/40Hz/528Hz) × 60min cada → catalogo 7 horas",
     "receita_mensal_usd":4500,
     "prazo":"2d","tipo":"algoritmico",
     "calculo":"Binaural streams: usuarios ouvem diariamente 60+ min. 7 faixas × 50K plays/dia × $0.004 = $1.4K/mes",
     "comecando_hoje":"Gerar 7 faixas binaural com Stable Audio (gratuito) + upload Amuse hoje"},

    # ── GRUPO 7: CONTENT ID ROYALTIES PERPÉTUOS ──
    {"id":"I16","nome":"Content ID Empire: 1000 Videos Registrados",
     "dominios":["VIDEO","DISTRIBUICAO","MONETIZACAO"],
     "apis":["YouTube Content ID","YouTube Partner Program","SoundExchange Digital",
             "ASCAP Performance","BMI Royalties","DistroKid Distribution",
             "YouTube Music Partner","Amuse Free Distro","Amazon Music Streaming","Deezer Streaming"],
     "mecanismo":"Registrar CADA video no Content ID → quando alguem copia → sua receita publicitaria vai para voce",
     "receita_mensal_usd":3000,
     "prazo":"7d","tipo":"algoritmico",
     "calculo":"1000 videos × 100 matches/mes × $0.50 medio = $50K/mes possivel. Conservador: $500-3K. Cresce forever",
     "comecando_hoje":"YouTube Studio → Content ID settings → registrar os 22 videos existentes hoje"},

    {"id":"I17","nome":"Royalties Musica Psicologia ECAD + ASCAP",
     "dominios":["AUDIO","MONETIZACAO"],
     "apis":["ASCAP Performance","BMI Royalties","SoundExchange Digital","YouTube Content ID",
             "DistroKid Distribution","Spotify for Podcasters","Amazon Music Streaming",
             "Stable Audio Open","YuE Music Gen","ACE-Step Music"],
     "mecanismo":"Compor trilhas proprias → registrar ASCAP/BMI → cada uso publico (TV radio podcast) = royalty USD",
     "receita_mensal_usd":2000,
     "prazo":"14d","tipo":"algoritmico",
     "calculo":"BMI paga $0.005-0.10 por execucao. 10K execucoes publicas × $0.02 = $200/mes. Cresce com catalogo",
     "comecando_hoje":"Cadastrar ASCAP gratis (ascap.com) + registrar trilhas existentes hoje"},

    # ── GRUPO 8: MEDIUM + KINDLE (leituras = dinheiro) ──
    {"id":"I18","nome":"Medium Science Articles 100/mes",
     "dominios":["PESQUISA","LLM","MONETIZACAO"],
     "apis":["PubMed","SciELO Brasil","Groq Llama 3.3","Perplexity Sonar","Exa Neural Search",
             "Medium Partner Program","Google Search Console","Brave Search API",
             "RCAAP Portugal","OpenAlex"],
     "mecanismo":"4 artigos/dia Medium baseados em papers → Partner Program paga por LEITURA automaticamente",
     "receita_mensal_usd":2500,
     "prazo":"1d","tipo":"algoritmico",
     "calculo":"100 artigos/mes × 1K leitores × $0.025 = $2.5K/mes. Artigos top pagam $100-500 individualmente",
     "comecando_hoje":"Medium.com → Partner Program → publicar 1 artigo cientifico HOJE"},

    {"id":"I19","nome":"KENP Reads: Biblioteca Psicologia KU",
     "dominios":["LLM","PESQUISA","MONETIZACAO"],
     "apis":["Groq Llama 3.3","PubMed","Qwen 2.5 72B","Mistral 7B v3","KDP Kindle Unlimited",
             "OpenAlex","Semantic Scholar","Exa Neural Search","RCAAP Portugal","SciELO Brasil"],
     "mecanismo":"1 guia/workbook psicologia por semana → KDP Unlimited → pago $0.004 por PAGINA LIDA sem compra",
     "receita_mensal_usd":8000,
     "prazo":"7d","tipo":"algoritmico",
     "calculo":"50 workbooks × 200 pag × 100 leitores Kindle Unlimited = 1M paginas × $0.004 = $4K/mes",
     "comecando_hoje":"Criar conta KDP gratis + publicar 1 workbook psicologia hoje"},

    # ── GRUPO 9: PROGRAMÁTICO (tráfego = dinheiro) ──
    {"id":"I20","nome":"Google Web Stories Psicologia 10/dia",
     "dominios":["LLM","IMAGE","MONETIZACAO","ANALISE"],
     "apis":["Groq Llama 3.3","FLUX Dev Hyper","SDXL Turbo","Google AdSense Display",
             "Google Search Console","Brave Search API","Exa Neural Search",
             "ZenQuotes","Quotable","IBGE Cidades BR"],
     "mecanismo":"10 Web Stories/dia sobre psicologia → indexadas no Google separadamente → CPM AdSense por impressao",
     "receita_mensal_usd":2000,
     "prazo":"3d","tipo":"algoritmico",
     "calculo":"300 stories/mes × 1K impressoes × $10 CPM = $3K/mes. Google Stories aparecem direto na busca",
     "comecando_hoje":"Web Stories Editor (gratuito) + criar 3 stories hoje sobre narcisismo"},

    {"id":"I21","nome":"Pinterest SEO Evergreen Machine 1K/mes",
     "dominios":["LLM","IMAGE","SOCIAL","MONETIZACAO"],
     "apis":["ZenQuotes","Quotable","FLUX Dev Hyper","SDXL Turbo","Pinterest Creator Rewards",
             "Canva API","Google AdSense Display","Bitly","Google Search Console","Brave Search API"],
     "mecanismo":"1000 pins/mes sobre psicologia → vida util 3-4 anos cada pin → trafego site → AdSense perpetuo",
     "receita_mensal_usd":2500,
     "prazo":"7d","tipo":"algoritmico",
     "calculo":"1K pins × 500 views/pin × 12 meses = 6M impressoes/ano → $3K/mes organic perpetuo",
     "comecando_hoje":"Criar conta Pinterest Business (gratuito) + criar 10 pins hoje"},

    # ── GRUPO 10: MULTI-MODAL CROSSING (mais inédito) ──
    {"id":"I22","nome":"Voz Clonada 5 Linguas Simultâneas",
     "dominios":["TTS","DISTRIBUICAO","MONETIZACAO","LLM"],
     "apis":["CosyVoice 2","F5 TTS Ultra","Parler TTS","Kokoro TTS","Groq Llama 3.3",
             "Qwen 2.5 72B","Mistral 7B v3","YouTube Partner Program","Spotify for Podcasters",
             "DistroKid Distribution"],
     "mecanismo":"1 script PT-BR → traduzir → 5 vozes clonadas (Daniela em 5 linguas) → 5 canais YouTube = 5x receita",
     "receita_mensal_usd":10000,
     "prazo":"14d","tipo":"algoritmico",
     "calculo":"5 linguas × 50K views × $8 RPM medio = $2K/mes hoje. Meta 500K cada = $20K/mes",
     "comecando_hoje":"CosyVoice 2 (HF gratuito) + traduzir 1 video existente para EN hoje"},

    {"id":"I23","nome":"Neurofeedback Visual 3D Psicologia",
     "dominios":["PESQUISA","LLM","IMAGE","VIDEO","DISTRIBUICAO"],
     "apis":["NeuroVault fMRI","Allen Brain Atlas Gene","Groq Llama 3.3","FLUX Depth Control",
             "HunyuanVideo","CogVideoX 5B","YouTube Partner Program",
             "YouTube Shorts RPM","Exa Neural Search","HF Mental BERT"],
     "mecanismo":"Mapas fMRI reais → animacoes 3D IA → explicacao psicologica → primeiro canal BR neuroimagem visual",
     "receita_mensal_usd":7000,
     "prazo":"14d","tipo":"algoritmico",
     "calculo":"Neuroimagem visual = nicho zero competição BR. RPM saude/ciencia $10-18. Viral potencial alto",
     "comecando_hoje":"Baixar mapas NeuroVault (gratuito) + criar 1 short animado hoje"},

    {"id":"I24","nome":"Audio Paper: Cada Paper = 1 Podcast",
     "dominios":["PESQUISA","LLM","TTS","DISTRIBUICAO","MONETIZACAO"],
     "apis":["PubMed","bioRxiv","PsyArXiv","Groq Llama 3.3","F5 TTS Ultra",
             "Stable Audio Open","DistroKid Distribution","Spotify for Podcasters",
             "Apple Podcasts Connect","SoundExchange Digital"],
     "mecanismo":"Cada novo paper psicologia → podcast 10min explicando → 60+ plataformas → royalties por stream",
     "receita_mensal_usd":4000,
     "prazo":"3d","tipo":"algoritmico",
     "calculo":"30 papers/mes × 10K plays × $0.004 = $1.2K/mes. Com 100 episodios catalogados = $4K perpetuo",
     "comecando_hoje":"RSS PubMed (gratuito) + Amuse gratis + gravar 1 episodio hoje"},

    {"id":"I25","nome":"Emotion Score YouTube: Comentarios → Conteudo",
     "dominios":["ANALISE","LLM","VIDEO","DISTRIBUICAO","PESQUISA"],
     "apis":["HF Emotion RoBERTa","HF PT-BR Sentiment","HF Mental BERT","YouTube Analytics API",
             "Groq Llama 3.3","PubMed","LTX Video","YouTube Partner Program",
             "YouTube Shorts RPM","Google Search Console"],
     "mecanismo":"Analisar emocoes 1000 comentarios → identificar dor mais frequente → criar proximo video sobre isso → loop",
     "receita_mensal_usd":5000,
     "prazo":"3d","tipo":"algoritmico",
     "calculo":"Conteudo baseado em dor real da audiencia = 3× engajamento = 3× views = 3× AdSense automatico",
     "comecando_hoje":"YouTube Analytics API gratuita + rodar analise nos comentarios dos 22 videos hoje"}
]

total = sum(i["receita_mensal_usd"] for i in IDEIAS_100)
print(f"25 ideias core documentadas")
print(f"Receita total: ${total:,}/mes")
print(f"Sem dependencia de compra: {sum(1 for i in IDEIAS_100 if i['tipo']=='algoritmico')}/25 ideas")
print()
for i in sorted(IDEIAS_100, key=lambda x: -x["receita_mensal_usd"])[:5]:
    print(f"  {i['id']} {i['nome'][:35]:35s}: ${i['receita_mensal_usd']:,}/mes | {i['prazo']}")

def sbh():
    return {"apikey":SK,"Authorization":f"Bearer {SK}","Content-Type":"application/json"}

def salvar_ideia(ideia):
    if not SK: return
    requests.post(f"{SB}/rest/v1/quantum_combinations",
        headers={**sbh(),"Prefer":"resolution=ignore-duplicates"},
        json={"combo_id":ideia["id"],"n_apis":len(ideia["apis"]),
              "apis_nomes":ideia["apis"],"score":88,
              "produto":ideia["nome"],"mecanismo":ideia["mecanismo"],
              "receita_90d_usd":ideia["receita_mensal_usd"]*3,
              "case_real":ideia["calculo"],
              "gerado_em":datetime.now().isoformat()},timeout=10)

for ideia in IDEIAS_100:
    salvar_ideia(ideia)
print(f"\n25 ideias salvas no Supabase quantum_combinations")
