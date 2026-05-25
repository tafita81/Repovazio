#!/usr/bin/env python3
"""
seo_global_stream.py — SEO máximo para aparecer no Google/Yahoo nas streams
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Como streams aparecem no Google:
  1. Título com keyword trending no momento → indexado em <5min
  2. Descrição: primeiras 160 chars = meta description (snippet no Google)
  3. Tags do YouTube = keywords de indexação
  4. Thumbnail CTR alto → mais cliques → sinal de ranking
  5. Chapters/timestamps → featured snippets
  6. Pinned comment no início → indexado separadamente
  7. Engagement rate (likes/comentários/compartilhamentos) no primeiro 30min

Google indexa streams AO VIVO em tempo real — janela de oportunidade!
Yahoo Search usa Google data — mesma estratégia funciona.
"""
import os, requests, json, time
import urllib3; urllib3.disable_warnings()

GROQ_KEY  = os.getenv("GROQ_API_KEY","")
SB_URL    = os.getenv("SUPABASE_URL","https://tpjvalzwkqwttvmszvie.supabase.co")
SB_KEY    = os.getenv("SUPABASE_SERVICE_KEY","")
SBH       = {"apikey":SB_KEY,"Authorization":f"Bearer {SB_KEY}",
             "Content-Type":"application/json","Prefer":"return=minimal"}

# Temas com volume de busca comprovado (Google Trends + TubeBuddy data)
TEMAS_SEO = [
    {
        "keyword_principal": "narcisismo encoberto",
        "volume_mensal_br": 90500,
        "titulo_template": "Narcisismo Encoberto: {subtitulo} | AGORA AO VIVO",
        "subtitulos": [
            "Os 8 Sinais Que Você Nunca Viu",
            "Por Que Você Não Percebe Que Está Nesse Relacionamento",
            "A Ciência Por Trás do Gaslighting",
        ],
        "tags": ["narcisismo","narcisismo encoberto","gaslighting","relacionamento toxicos",
                 "como identificar narcisista","narcissistic abuse","psicologia dark",
                 "Daniela Coelho","narcisismo sinais","apego ansioso","trauma bond",
                 "Harvard psychology","covert narcissism","psicologia"],
    },
    {
        "keyword_principal": "insônia ansiedade",
        "volume_mensal_br": 74000,
        "titulo_template": "Por Que Você Acorda Às 3h: {subtitulo} | SCIENCE LIVE",
        "subtitulos": [
            "Cortisol e o Seu Sono Explicados",
            "O Que Seu Corpo Está Tentando Te Dizer",
            "Solução Em 4 Minutos Baseada em Pesquisa",
        ],
        "tags": ["insônia","acordar às 3h","cortisol e sono","ansiedade noturna",
                 "como dormir melhor","sleep science","Matthew Walker","psicologia do sono",
                 "binaural sleep","528hz","ansiedade","Daniela Coelho"],
    },
    {
        "keyword_principal": "burnout sintomas",
        "volume_mensal_br": 60500,
        "titulo_template": "Burnout Antes do Colapso: {subtitulo} | LIVE",
        "subtitulos": [
            "3 Fases Que Ninguém Te Contou",
            "Maslach e a Ciência do Esgotamento",
            "Como Identificar Antes de Ser Tarde",
        ],
        "tags": ["burnout","esgotamento mental","sindrome de burnout","burnout sintomas",
                 "estresse crônico","saúde mental","Christina Maslach","psicologia trabalho",
                 "como evitar burnout","Daniela Coelho","mental health"],
    },
    {
        "keyword_principal": "apego ansioso",
        "volume_mensal_br": 49500,
        "titulo_template": "Apego Ansioso: {subtitulo} | AO VIVO",
        "subtitulos": [
            "Por Que Você Escolhe Quem Te Machuca",
            "Ainsworth e a Teoria do Apego Explicada",
            "Como Desenvolver Apego Seguro",
        ],
        "tags": ["apego ansioso","apego evitante","teoria do apego","Ainsworth",
                 "relacionamentos","ansiedade relacionamento","apego seguro",
                 "como parar de escolher relacionamentos toxicos","Daniela Coelho"],
    },
]

# SEO EN — mercado americano (RPM $25)
TEMAS_SEO_EN = [
    {
        "keyword_principal": "covert narcissist",
        "volume_mensal_us": 165000,
        "titulo_template": "Covert Narcissist: {subtitulo} | LIVE NOW",
        "subtitulos": [
            "8 Signs You're Missing",
            "Harvard Research Explains",
            "Why You Stay — Science",
        ],
        "tags": ["covert narcissist","narcissistic abuse","gaslighting signs",
                 "covert narcissism","how to spot a narcissist","psychology facts",
                 "Craig Malkin","narcissistic personality disorder","dark psychology",
                 "trauma bonding","mental health","relationship advice"],
    },
    {
        "keyword_principal": "anxiety sleep",
        "volume_mensal_us": 110000,
        "titulo_template": "Why You Wake at 3AM: {subtitulo} | SCIENCE LIVE",
        "subtitulos": [
            "The Cortisol Truth",
            "Matthew Walker Explains",
            "Sleep Anxiety Fix in 4 Minutes",
        ],
        "tags": ["anxiety sleep","insomnia anxiety","why do i wake up at 3am",
                 "cortisol and sleep","sleep science","Matthew Walker","sleep psychology",
                 "528hz sleep","binaural beats","how to sleep better","mental health"],
    },
]

def groq_gerar_descricao(tema, lang="PT"):
    if not GROQ_KEY: return tema["keyword_principal"]
    kw = tema["keyword_principal"]
    idioma = "PT-BR" if lang == "PT" else "English"
    prompt = (
        f"SEO expert. Gere descrição YouTube para live de psicologia.\n"
        f"Keyword: '{kw}' | Idioma: {idioma}\n"
        f"Regras:\n"
        f"- Primeiras 160 chars = meta description (Google snippet)\n"
        f"- Incluir keyword nas primeiras 2 linhas\n"
        f"- Timestamps: 00:00 Intro, 02:00 Pesquisa, 05:00 Sinais, 10:00 Solução\n"
        f"- Links: repovazio.vercel.app/app-vendas | repovazio.vercel.app/psicologia-para-dormir\n"
        f"- Hashtags no final: 3 máximo\n"
        f"Max 500 chars. PROIBIDO: psicóloga."
    )
    try:
        r = requests.post("https://api.groq.com/openai/v1/chat/completions",
            headers={"Authorization":f"Bearer {GROQ_KEY}","Content-Type":"application/json"},
            json={"model":"llama-3.3-70b-versatile",
                  "messages":[{"role":"user","content":prompt}],
                  "max_tokens":200,"temperature":0.7},
            timeout=15, verify=False)
        if r.status_code == 200:
            return r.json()["choices"][0]["message"]["content"].strip()
    except: pass
    return kw

def gerar_metadata_completo(tema, lang="PT", subtitulo_idx=0):
    subtitulo = tema["subtitulos"][subtitulo_idx % len(tema["subtitulos"])]
    titulo = tema["titulo_template"].replace("{subtitulo}", subtitulo)
    descricao = groq_gerar_descricao(tema, lang)
    tags = tema["tags"]
    return {
        "titulo": titulo[:100],
        "descricao": descricao,
        "tags": tags[:15],
        "keyword": tema["keyword_principal"],
        "lang": lang,
    }

def salvar_supabase(meta):
    if not SB_KEY: return
    requests.post(f"{SB_URL}/rest/v1/video_seo",
        headers={**SBH,"Prefer":"return=minimal"},
        json={"video_id":f"live_{meta['lang']}_{int(time.time())}",
              "titulo_principal":meta["titulo"],
              "descricao":meta["descricao"][:2000],
              "tags":json.dumps(meta["tags"]),
              "status":"ready"},
        timeout=8, verify=False)

def run():
    print("=== SEO GLOBAL — Google/Yahoo Indexação ===")
    print("  Estratégia: keyword trending + CTR alto + chapters + engagement")
    print()
    todos = []
    for i, tema in enumerate(TEMAS_SEO):
        meta = gerar_metadata_completo(tema, "PT", i)
        todos.append(meta)
        print(f"  [{meta['lang']}] {meta['titulo'][:55]}")
        print(f"        Tags: {', '.join(meta['tags'][:5])}...")
        salvar_supabase(meta)
        time.sleep(1.5)
    for i, tema in enumerate(TEMAS_SEO_EN):
        meta = gerar_metadata_completo(tema, "EN", i)
        todos.append(meta)
        print(f"  [{meta['lang']}] {meta['titulo'][:55]}")
        print(f"        Tags: {', '.join(meta['tags'][:5])}...")
        salvar_supabase(meta)
        time.sleep(1.5)
    print(f"\n  {len(todos)} sets de metadata SEO gerados e salvos")
    print(f"  Google indexa streams AO VIVO em <5min após início")
    print(f"  Keyword searches que geram views orgânicas em EUA/BR")

if __name__=="__main__": run()
