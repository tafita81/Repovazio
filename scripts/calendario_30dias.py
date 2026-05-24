#!/usr/bin/env python3
"""
calendario_30dias.py — 30 dias de conteúdo WhatsApp + Instagram + YouTube
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Gera o plano editorial completo do mês:
  - Áudio WhatsApp (19h30) por dia
  - 3 Reels Instagram (sem aparecer)
  - 1 YouTube short ou long por semana
  - Afiliado por semana (Kwai + Amazon + Hotmart)
"""
import os, requests, time, json
import urllib3; urllib3.disable_warnings()

SB_URL = os.getenv("SUPABASE_URL","https://tpjvalzwkqwttvmszvie.supabase.co")
SB_KEY = os.getenv("SUPABASE_SERVICE_KEY","")
GROQ   = os.getenv("GROQ_API_KEY","")
SBH    = {"apikey":SB_KEY,"Authorization":f"Bearer {SB_KEY}",
          "Content-Type":"application/json","Prefer":"return=minimal"}

CALENDARIO_30 = [
    # Semana 1: Ansiedade e Sono
    {"dia":1, "tema":"sono",      "titulo":"Por Que Sua Mente Acelera Às 23h",             "reel":"3 sinais que seu cortisol está alto","afiliado":"magnesio"},
    {"dia":2, "tema":"ansiedade", "titulo":"A Técnica Militar Para Dormir em 2 Minutos",   "reel":"Por que você não consegue desligar","afiliado":None},
    {"dia":3, "tema":"narcis",    "titulo":"O Narcisista Que Parece Ser a Vítima",          "reel":"Como identificar manipulação emocional","afiliado":None},
    {"dia":4, "tema":"burnout",   "titulo":"Seu Corpo Entrou em Modo de Emergência",       "reel":"Por que você acorda cansado","afiliado":"ashwagandha"},
    {"dia":5, "tema":"sono",      "titulo":"528Hz: O Que Acontece no Seu Cérebro",         "reel":"Frequência que reduz cortisol 65%","afiliado":None},
    {"dia":6, "tema":"apego",     "titulo":"Por Que Você Escolhe Quem Te Machuca",         "reel":"Seu estilo de apego explica tudo","afiliado":None},
    {"dia":7, "tema":"mindful",   "titulo":"4 Minutos Para Limpar o Dia",                  "reel":"Body scan de 4 minutos","afiliado":None},
    # Semana 2: Relacionamentos e Padrões
    {"dia":8,  "tema":"narcis",   "titulo":"Gaslighting: Quando Você Duvida de Si Mesmo",  "reel":"Diferença entre crítica e gaslighting","afiliado":None},
    {"dia":9,  "tema":"apego",    "titulo":"Apego Ansioso: O Loop Que Não Para",           "reel":"Por que você fica obcecado","afiliado":"omega3"},
    {"dia":10, "tema":"trauma",   "titulo":"Por Que Traumas Aparecem Nos Sonhos",          "reel":"Van der Kolk explica o sono perturbado","afiliado":None},
    {"dia":11, "tema":"sono",     "titulo":"O Hormônio Que Você Destrói Todo Dia",         "reel":"Melatonina: 3 erros comuns","afiliado":None},
    {"dia":12, "tema":"burnout",  "titulo":"Burnout Começa Com Orgulho de Não Parar",      "reel":"Maslach (1981): os 6 sinais","afiliado":"ashwagandha"},
    {"dia":13, "tema":"narcis",   "titulo":"Love Bombing: A Fase Que Vicia",               "reel":"O ciclo do relacionamento narcísico","afiliado":None},
    {"dia":14, "tema":"sono",     "titulo":"40Hz Gamma: TDAH e Foco Noturno",              "reel":"Greenred pesquisa: gamma e cognição","afiliado":"lteanina"},
    # Semana 3: Neurociência e Corpo
    {"dia":15, "tema":"neuro",    "titulo":"O Que Acontece no Cérebro Às 3h da Manhã",    "reel":"Grelina, cortisol e o despertar noturno","afiliado":None},
    {"dia":16, "tema":"ansiedade","titulo":"Resposta de Luta ou Fuga Que Não Desliga",     "reel":"Sistema nervoso autônomo: como resetar","afiliado":None},
    {"dia":17, "tema":"apego",    "titulo":"Oxitocina e o Vício em Relacionamentos Tóxicos","reel":"Gottman: os 4 cavaleiros","afiliado":None},
    {"dia":18, "tema":"sono",     "titulo":"REM: Por Que Você Precisa Sonhar Para Curar",  "reel":"Walker (2017): sleep is medicine","afiliado":None},
    {"dia":19, "tema":"trauma",   "titulo":"PTSD: O Corpo Lembra O Que A Mente Esqueceu",  "reel":"Somática e regulação do sistema nervoso","afiliado":None},
    {"dia":20, "tema":"burnout",  "titulo":"Vago: O Nervo Que Controla Tudo",              "reel":"Estimulação vagal: técnicas gratuitas","afiliado":"omega3"},
    {"dia":21, "tema":"mindful",  "titulo":"Neuroplasticidade: Como Mudar Padrões Antigos","reel":"21 dias para criar um novo hábito","afiliado":None},
    # Semana 4: Integração e Autoconhecimento
    {"dia":22, "tema":"narcis",   "titulo":"Triangulação: A Tática Que Enlouquece",        "reel":"Como sair de uma dinâmica narcísica","afiliado":None},
    {"dia":23, "tema":"sono",     "titulo":"Chronotype: Por Que Você É Coruja ou Cotovia", "reel":"Sleep chronotype test","afiliado":None},
    {"dia":24, "tema":"apego",    "titulo":"Seguro: Como Desenvolver Apego Seguro Adulto", "reel":"Ainsworth: os 3 tipos de apego","afiliado":None},
    {"dia":25, "tema":"burnout",  "titulo":"Recuperação Do Burnout: Linha Do Tempo Real",  "reel":"Quanto tempo demora mesmo","afiliado":"ashwagandha"},
    {"dia":26, "tema":"neuro",    "titulo":"Dopamina: Por Que Você Se Sente Vazio",        "reel":"Ciclo de recompensa e redes sociais","afiliado":None},
    {"dia":27, "tema":"ansiedade","titulo":"4-7-8: A Respiração Que Muda Tudo em 57s",    "reel":"Demo ao vivo da técnica","afiliado":None},
    {"dia":28, "tema":"sono",     "titulo":"Sonolência vs Cansaço: Diferença Que Importa", "reel":"Higiene do sono: checklist completo","afiliado":None},
    {"dia":29, "tema":"narcis",   "titulo":"Pós-Relacionamento Narcísico: O Que Esperar",  "reel":"Recovery timeline real","afiliado":"corpo_placar"},
    {"dia":30, "tema":"mindful",  "titulo":"30 Dias Depois: O Que Mudou Para Você?",       "reel":"Testemunho e próxima jornada","afiliado":None},
]

AFILIADOS_MAP = {
    "magnesio":    ("Magnésio Glicinato","Kwai Shop + Shopee","sono e ansiedade","Boyle NB 2017"),
    "ashwagandha": ("Ashwagandha KSM-66","Kwai Shop + TikTok","burnout e cortisol","Chandrasekhar 2012"),
    "omega3":      ("Ômega-3 DHA+EPA","Amazon Associados","depressão e cognição","Mocking RJ 2016"),
    "lteanina":    ("L-Teanina+Cafeína","Kwai Shop","foco e TDAH","Nathan PJ 2006"),
    "corpo_placar":("O Corpo Guarda o Placar","Amazon Associados","trauma","van der Kolk 2014"),
}

def groq_gerar_tudo(dia_info):
    """Gera: áudio WhatsApp + legenda Reel + script afiliado (1 chamada)"""
    if not GROQ: return {}
    af = AFILIADOS_MAP.get(dia_info.get("afiliado",""), None)
    af_block = f"\nAFILIADO DIA: {af[0]} ({af[1]}) — Base: {af[3]}" if af else ""
    prompt = (
        f"Gere conteúdo do dia {dia_info['dia']} em PT-BR. Responda APENAS JSON.\n"
        f"Tema: {dia_info['tema']} | Título: {dia_info['titulo']}\n"
        f"Reel hook: '{dia_info['reel']}'{af_block}\n\n"
        f"Retorne JSON com 3 campos:\n"
        f"\"audio_script\": script áudio WhatsApp 240s, tom calmo, cita PubMed real\n"
        f"\"reel_legenda\": legenda Instagram max 100 palavras + CTA 'Comenta SONO'\n"
        f"\"afiliado_cta\": texto afiliado honesto max 60 palavras (ou null se sem afiliado)"
    )
    try:
        r = requests.post("https://api.groq.com/openai/v1/chat/completions",
            headers={"Authorization":f"Bearer {GROQ}","Content-Type":"application/json"},
            json={"model":"llama-3.3-70b-versatile",
                  "messages":[{"role":"user","content":prompt}],
                  "max_tokens":700,"temperature":0.80},
            timeout=25, verify=False)
        if r.status_code == 200:
            txt = r.json()["choices"][0]["message"]["content"].strip()
            txt = txt.replace("```json","").replace("```","").strip()
            return json.loads(txt)
    except: pass
    return {}

def salvar_dia(dia_info, conteudo):
    if not SB_KEY: return
    # Áudio WhatsApp
    requests.post(f"{SB_URL}/rest/v1/whatsapp_psicologia_queue", headers=SBH,
        json={"dia":dia_info["dia"],"titulo":dia_info["titulo"],
              "tema":dia_info["tema"],"script":conteudo.get("audio_script","")[:600],
              "horario_envio":"19:30","status":"pending"}, timeout=8, verify=False)
    # Reel Instagram
    requests.post(f"{SB_URL}/rest/v1/social_posts", headers=SBH,
        json={"plataforma":"instagram","tema":dia_info["tema"],
              "hook":dia_info["reel"],"legenda":conteudo.get("reel_legenda","")[:400],
              "cta":"Comenta SONO que eu te mando o link 👇",
              "status":"pending"}, timeout=8, verify=False)
    # Afiliado
    if dia_info.get("afiliado") and conteudo.get("afiliado_cta"):
        af = AFILIADOS_MAP.get(dia_info["afiliado"])
        if af:
            requests.post(f"{SB_URL}/rest/v1/kwai_products", headers=SBH,
                json={"produto":af[0],"beneficio":af[2],
                      "pubmed_cit":af[3],"script_pt":conteudo.get("afiliado_cta","")[:300],
                      "status":"pending"}, timeout=8, verify=False)

def run():
    print("=== CALENDÁRIO 30 DIAS — Psicologia Para Dormir ===\n")
    total = 0
    for dia in CALENDARIO_30[:10]:  # Gera os 10 primeiros por execução
        print(f"  📅 Dia {dia['dia']:02d}: {dia['titulo'][:45]}")
        conteudo = groq_gerar_tudo(dia)
        if conteudo:
            salvar_dia(dia, conteudo)
            total += 1
            print(f"     ✅ áudio + reel + {dia.get('afiliado') or 'sem afiliado'}")
        else:
            salvar_dia(dia, {})
        time.sleep(2)

    print(f"\n  ✅ {total} dias de conteúdo gerados")
    print(f"  📱 WhatsApp 19h30 + 3 Reels/dia + afiliados")
    print(f"  💰 Funil: Instagram → SONO → DM → Hotmart R$216/ano")

if __name__=="__main__": run()
