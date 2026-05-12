#!/usr/bin/env python3
"""
gerar_scripts.py — Cerebro V14
Gera scripts com durações CORRETAS para monetizacao YouTube
Long: ~15 min (4.200-4.800 palavras PT-BR = 14-16min em voz)
Short: ~54s (140-165 palavras PT-BR = 50-58s em voz)
"""
import os, json, random, time
from supabase import create_client

# ─── REGRAS IMUTAVEIS ─────────────────────────────────────────────────────────
LONG_WORDS_TARGET = 4500   # ~15min em voz PT-BR
LONG_WORDS_MIN    = 4000   # ~13.3min
LONG_WORDS_MAX    = 5000   # ~16.7min
SHORT_WORDS_TARGET = 155   # ~54s em voz PT-BR
SHORT_WORDS_MIN    = 135   # ~47s
SHORT_WORDS_MAX    = 170   # ~59.5s

# Velocidade media PT-BR: ~300 palavras/minuto narrado pausado

# ─── ESTRUTURA LONG (15 min) ──────────────────────────────────────────────────
LONG_STRUCTURE = {
    "intro_hook": {
        "palavras": 180,
        "instrucao": "GANCHO VIRAL: pergunta perturbadora ou afirmacao chocante sobre o tema. Ja no primeiro paragrafo: 'Voce ja sentiu...' ou 'A ciencia descobriu que...' ou 'Por que quando você...' — usar SEGUNDA PESSOA. Nao revelar a resposta ainda."
    },
    "problema_pessoal": {
        "palavras": 350,
        "instrucao": "Conectar com a experiencia emocional do espectador. 'Isso ja aconteceu com voce?' Descrever o sentimento sem nomear ainda. Criar identificacao maxima."
    },
    "contexto_cientifico": {
        "palavras": 450,
        "instrucao": "Apresentar o fenomeno com base cientifica. 'Estudos mostram...', 'Pesquisadores da Universidade de...', 'Em 2023, um estudo publicado em...'. Citar fonte real mas generica. Tornar a ciencia acessivel."
    },
    "causas_raiz": {
        "palavras": 600,
        "instrucao": "3-4 causas profundas. Cada uma com: (1) nome marcante, (2) explicacao emocional, (3) exemplo concreto do cotidiano brasileiro. Usar subtitulos impliciticos no script como [CAUSA 1], [CAUSA 2]."
    },
    "como_aparece_vida": {
        "palavras": 550,
        "instrucao": "5-7 sinais/comportamentos concretos. O espectador deve pensar 'isso sou eu!' a cada item. Linguagem do cotidiano. Exemplos de relacionamentos, trabalho, familia."
    },
    "o_que_acontece_cerebro": {
        "palavras": 400,
        "instrucao": "Neurociencia simplificada: o que acontece no cerebro/corpo. Mencionar cortisol, amigdala, sistema nervoso de forma acessivel. 'Seu cerebro entende isso como...' 'O que acontece quimicamente e...'"
    },
    "historias_casos": {
        "palavras": 500,
        "instrucao": "2 historias curtas de personas (nomes brasileiros ficticios: Maria, Joao, Ana, Pedro). Mostrar o problema em acao. Gerar identificacao emocional forte. Sem resolucao ainda."
    },
    "o_que_fazer": {
        "palavras": 600,
        "instrucao": "5-7 estrategias praticas baseadas em ciencia. Cada uma: (1) nome da tecnica, (2) por que funciona (breve), (3) como fazer hoje. Linguagem de acao: 'Quando isso acontecer, faca...'"
    },
    "mudanca_progressiva": {
        "palavras": 350,
        "instrucao": "Mostrar que a mudanca e gradual e possivel. Timeline realista: 'Nas primeiras 2 semanas voce vai notar...', 'Em 2 meses...'. Esperanca baseada em realidade."
    },
    "conclusao_cta": {
        "palavras": 220,
        "instrucao": "Resumo emocional poderoso. CTA natural: 'Se esse video te ajudou, passa pra frente pra alguem que precisa ouvir isso.' E: 'Nos proximos episodios vamos ver...' — criar curiosidade para serie."
    }
}

# ─── ESTRUTURA SHORT (50-58s) ─────────────────────────────────────────────────
SHORT_STRUCTURE = {
    "hook_1s": "PRIMEIRA FRASE impacto maximo: afirmacao chocante ou pergunta que para o scroll",
    "problema_10s": "Identificar a dor em 2-3 frases. 'Sabe quando voce...' Criar identificacao imediata",
    "revelacao_20s": "A resposta/explicacao. 'A ciencia chama isso de...' 'O que acontece e...' — NOVO ANGULO",
    "impacto_10s": "Aprofundar o impacto. Por que isso importa? O que muda com esse saber?",
    "acao_10s": "Uma acao concreta. 'Da proxima vez que isso acontecer...' ou 'Tente hoje...'",
    "cta_3s": "CTA nao-intrusivo: 'Mais sobre isso no canal' ou 'Continua na serie [NOME]'",
}

SERIES_TEMAS = {
    "Apego Ansioso": [
        "Por que voce fica checando o celular esperando mensagem",
        "O que acontece no seu cerebro quando alguem demora a responder",
        "Por que relacionamentos saudaveis parecem chatos no inicio",
        "Como o apego ansioso sabotageia suas amizades tambem",
        "A diferenca entre amor e vicio em aprovacao",
        "Por que voce sente culpa quando coloca limites",
        "Como o apego ansioso se forma na infancia",
        "Sinais de que voce tem apego ansioso no trabalho tambem",
        "Por que voce sempre escolhe pessoas emocionalmente indisponiveis",
        "Como curar o apego ansioso: o que a ciencia realmente diz",
    ],
    "Mentes Narcisistas": [
        "7 frases que narcisistas usam para fazer voce se sentir louco",
        "Por que voce fica viciado em uma pessoa narcisista",
        "Como narcisistas escolhem suas vitimas — o perfil exato",
        "O ciclo idealizacao-desvalorizacao-descarte explicado",
        "Por que e tao dificil sair de um relacionamento com narcisista",
        "Narcisismo encoberto: os sinais que a maioria ignora",
        "Como narcisistas usam seus filhos como armas",
        "A diferenca entre confianca saudavel e narcisismo",
        "Como se recuperar do abuso narcisista",
        "Narcisismo no trabalho: como identificar o chefe toxico",
    ],
    "Trauma Invisivel": [
        "Traumas que voce nem sabe que tem",
        "Como o trauma de abandono muda seu cerebro",
        "Por que pessoas traumatizadas repetem padroes toxicos",
        "Trauma complexo: quando o perigo era em casa",
        "Como o corpo guarda o trauma — o que a ciencia diz",
        "PTSD silencioso: os sintomas que ninguem reconhece",
        "Por que voce se sente entorpecido emocionalmente",
        "A ciencia do por que lembrancas traumaticas nao desaparecem",
        "Como se reconectar com seu corpo apos trauma",
        "A diferenca entre trauma resolvido e trauma suprimido",
    ],
    "Ansiedade e Panico": [
        "A diferenca entre ansiedade normal e transtorno",
        "Por que crises de panico acontecem do nada",
        "Como a ansiedade afeta seu sistema digestivo",
        "Ansiedade social: o que acontece no cerebro",
        "Por que voce catastrophiza mesmo sabendo que e irracional",
        "A ciencia da procrastinacao ansiosa",
        "Como ansiedade e depressao se retroalimentam",
        "Por que evitar situacoes piora a ansiedade",
        "Tecnicas de regulacao nervosa que realmente funcionam",
        "Ansiedade e relacionamentos: por que voce afasta as pessoas",
    ],
    "Burnout": [
        "Os 5 estagios do burnout que a maioria ignora",
        "Por que burnout nao e preguica — a ciencia prova",
        "Como burnout destroi relacionamentos",
        "Burnout silencioso: quando voce nem sabe que esta la",
        "A diferenca entre estresse e burnout",
        "Como o trabalho remoto piorou o burnout",
        "Por que perfeccionistas tem mais burnout",
        "Como se recuperar do burnout: linha do tempo real",
        "Burnout materno: o esgotamento que ninguem fala",
        "Como prevenir burnout antes que seja tarde",
    ],
}

print("GERAR_SCRIPTS — Cerebro V14")
print(f"Long: {LONG_WORDS_TARGET} palavras (~{LONG_WORDS_TARGET//300}min) | Short: {SHORT_WORDS_TARGET} palavras (~{SHORT_WORDS_TARGET*60//300}s)")

SB_URL = os.environ.get("SUPABASE_URL","")
SB_KEY = os.environ.get("SUPABASE_KEY","")
if SB_URL and SB_KEY:
    sb = create_client(SB_URL, SB_KEY)
    # Inserir 10 novos temas na fila
    for serie, temas in SERIES_TEMAS.items():
        for tema in temas[:2]:  # 2 por serie = 10 novos
            existing = sb.table("content_pipeline").select("id").ilike("title",f"%{tema[:30]}%").execute()
            if not existing.data:
                formato = "short_60s" if random.random() < 0.3 else "youtube_long"
                palavras = SHORT_WORDS_TARGET if "short" in formato else LONG_WORDS_TARGET
                sb.table("content_pipeline").insert({
                    "title": tema,
                    "status": "pending_generation",
                    "score": 0,
                    "metadata": {
                        "serie": serie,
                        "formato": formato,
                        "target_palavras": palavras,
                        "target_segundos": 54 if "short" in formato else 900,
                        "cerebro_v14": True,
                        "render_method": "flux_kenburns_v2",
                    }
                }).execute()
                print(f"  + {serie[:20]}: {tema[:50]}")
print("Concluido")
