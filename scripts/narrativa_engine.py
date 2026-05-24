#!/usr/bin/env python3
"""
narrativa_engine.py — Equivalente ao "Narrativa" (ferramenta interna do Marcos)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
BASEADO EM: Aula "Elite Dark Academy" — Marcos + Rainer

CONCEITOS DO TRANSCRIPT IMPLEMENTADOS:
  1. VÍDEO-CHAVE: Encontrar tema + estrutura de título que viraliza
  2. CANAIS EM ASCENSÃO: Poucos inscritos + muitas views = oportunidade
  3. PERSONAGEM CONSISTENTE: Daniela Coelho em todas as cenas (IP original)
  4. NICHOS IMERSIVOS: "Passei 24h em X", "Voltei no tempo para Y"
  5. ESTRUTURAS VALIDADAS: 5 variações de título por nicho
  6. FORMATOS: Narrativo / Imersivo / ASMR / Dark reflexivo
  7. NICHOS LUCRATIVOS: Psicologia + Geopolítica + Arqueologia + Ecologia Verde

ESTRUTURAS DE TÍTULO VALIDADAS (do transcript):
  Padrão Imersivo:   "Passei 24 horas em [LUGAR/SITUAÇÃO IMPOSSÍVEL]"
  Padrão Temporal:   "Voltei no tempo para descobrir [REVELAÇÃO]"
  Padrão Revelação:  "O [FENÔMENO] que [CONSEQUÊNCIA SURPREENDENTE]"
  Padrão Persona:    "Se eu acordasse [SITUAÇÃO IMPOSSÍVEL], eu faria..."
  Padrão Pergunta:   "Por que [FENÔMENO] acontece quando [GATILHO]"

NICHOS × CPMS (tabela do transcript):
  Psicologia dark    $20 CPM  — narcisismo, trauma, apego
  Geopolítica        $28 CPM  — tensões, petróleo, guerras, estratégia
  Arqueologia        $22 CPM  — civilizações perdidas, descobertas
  Ecologia verde     $18 CPM  — tecnologia limpa, futuro do planeta
  Neurociência       $25 CPM  — como o cérebro funciona, TDAH, sono

DANIELA COELHO — personagem consistente em TODAS as cenas:
  Mesma aparência, mesma posição, mesmo estilo visual
  Adapta expressão conforme emoção da cena (sério, curioso, surpreso)
"""
import os, requests, pathlib, time, json, base64
import urllib3; urllib3.disable_warnings()

SB_URL   = os.getenv("SUPABASE_URL","https://tpjvalzwkqwttvmszvie.supabase.co")
SB_KEY   = os.getenv("SUPABASE_SERVICE_KEY","")
GROQ     = os.getenv("GROQ_API_KEY","")
GEMINI   = os.getenv("GEMINI_API_KEY","AIzaSyDzCea_65Al-vy342xslBSVmKPv0qzTuXY")
SBH      = {"apikey":SB_KEY,"Authorization":f"Bearer {SB_KEY}",
            "Content-Type":"application/json","Prefer":"return=minimal"}
TMP      = pathlib.Path("/tmp/narrativa"); TMP.mkdir(exist_ok=True)

# ── BANCO DE ESTRUTURAS DE TÍTULO VALIDADAS ────────────────────────────────
ESTRUTURAS = {
    "imersivo": [
        "Passei 24 horas {lugar_impossivel} e {revelacao}",
        "Vivi 7 dias {situacao_extrema} — o que aprendi sobre {tema_psico}",
        "Entrei {lugar_proibido} para descobrir {segredo_psicologico}",
        "Me disfarçei de {persona} por 30 dias. O resultado foi {revelacao_chocante}",
        "Testei {metodo_cientifico} por 60 dias. Meu {indicador} mudou {porcentagem}",
    ],
    "temporal": [
        "Voltei no tempo para entender por que {fenomeno_psicologico} existe",
        "Como {pesquisador_famoso} descobriu {conceito} que mudou tudo",
        "Em {ano}, {pesquisador} percebeu algo sobre {tema} que ninguém acreditou",
        "O experimento de {ano} que provou que {verdade_contraintuitiva}",
        "Antes de {marco_historico}, ninguém sabia que {revelacao_psicologica}",
    ],
    "revelacao": [
        "O {fenomeno} que parece {coisa_boa} mas na verdade é {problema_oculto}",
        "Por que {comportamento_comum} é sinal de {problema_psicologico_oculto}",
        "O que {profissao} não te conta sobre {tema_cotidiano}",
        "A pesquisa de {universidade} confirmou: {verdade_surpreendente}",
        "{porcentagem}% das pessoas fazem {comportamento} sem perceber que {consequencia}",
    ],
    "dark_reflexivo": [
        "Se eu acordasse amanhã sem {coisa_preciosa}, eu {acao_contraintuitiva}",
        "O narcisista que {comportamento_que_parece_bom}",
        "Burnout não começa com {causa_obvia}. Começa com {causa_oculta}",
        "Você não {diagnostico_errado}. Você {diagnostico_real_cientifico}",
        "A razão pela qual você sempre {padrao_autodestrutivo} tem nome",
    ],
    "geopolitica": [
        "Por que o {recurso} sobe quando {evento_geopolitico}",
        "O país que {acao_surpreendente} e ninguém percebeu",
        "Como {nacao} mudou o {aspecto_global} em {periodo} sem fazer barulho",
        "A estratégia de {pais} que {resultado_inesperado} no mundo",
        "Por que {conflito_atual} é sobre {causa_oculta} e não {causa_obvia}",
    ],
    "arqueologia": [
        "A civilização de {periodo} que {conquista_impressionante} antes de sumir",
        "O que encontraram em {lugar} que muda tudo que sabemos sobre {era}",
        "Como Noé — perdão — como {figura_historica} realmente {acao_historica}",
        "A descoberta em {local} que {universidades} tentaram esconder",
        "Voltei no tempo para descobrir como {figura_historica} realmente vivia",
    ],
}

# ── CANAIS REFERÊNCIA POR NICHO (estratégia do transcript) ─────────────────
CANAIS_REFERENCIA = {
    "psicologia": {
        "subs_alvo": "10K-500K",
        "keywords": ["narcisismo","trauma","apego ansioso","burnout","gaslight"],
        "formato": "dark_reflexivo",
        "cpm_usd": 20,
        "exemplos_titulo": [
            "O Narcisista Que Você Não Consegue Identificar",
            "Por Que Seu Corpo Grava o Trauma Antes de Você",
            "Burnout Não Começa Com Cansaço — Começa Com Orgulho",
        ]
    },
    "geopolitica": {
        "subs_alvo": "5K-200K",
        "keywords": ["petróleo","conflito","estratégia","economia global","tensão"],
        "formato": "geopolitica",
        "cpm_usd": 28,
        "exemplos_titulo": [
            "Por Que o Petróleo Sobe Quando Existe Tensão no Oriente Médio",
            "O País Que Mudou a Economia Global Sem Fazer Barulho",
            "Como a China Conquistou a África Sem Disparar um Tiro",
        ]
    },
    "arqueologia": {
        "subs_alvo": "1K-100K",
        "keywords": ["civilização perdida","descoberta","Egypt","mistério","história"],
        "formato": "arqueologia",
        "cpm_usd": 22,
        "exemplos_titulo": [
            "Como Noé Realmente Dormia na Arca — Voltei no Tempo",
            "A Civilização de 3000 AC Que Construiu Algo Impossível",
            "O Que Encontraram no Egito Que Muda Tudo Que Sabemos",
        ]
    },
    "neurociencia": {
        "subs_alvo": "5K-300K",
        "keywords": ["cérebro","neuroplasticidade","dopamina","serotonina","cognição"],
        "formato": "revelacao",
        "cpm_usd": 25,
        "exemplos_titulo": [
            "O Que Acontece no Seu Cérebro 5 Segundos Antes de Tomar Uma Decisão",
            "Por Que Dopamina Não É Prazer — É Antecipação",
            "A Pesquisa de Harvard: 37 Minutos Por Dia Muda Sua Neurologia",
        ]
    },
}

def groq_gerar_video_key(nicho, formato, idioma="PT"):
    """Gera um 'vídeo-chave' — o vídeo que vai viralizar com estrutura validada"""
    if not GROQ: return None
    structs = ESTRUTURAS.get(formato, ESTRUTURAS["dark_reflexivo"])
    lang = {"PT":"Portuguese Brazilian","EN":"English","ES":"Spanish",
            "DE":"German","FR":"French"}.get(idioma,"English")
    canal = CANAIS_REFERENCIA.get(nicho, CANAIS_REFERENCIA["psicologia"])

    prompt = (
        f"Generate 5 VIRAL YouTube video titles for the '{nicho}' niche in {lang}.\n"
        f"Format: {formato}\n"
        f"Target CPM: ${canal['cpm_usd']}\n"
        f"Keywords to include: {', '.join(canal['keywords'][:3])}\n\n"
        f"Title structure templates (use and adapt these):\n"
        + "\n".join(f"- {s}" for s in structs[:3]) +
        f"\n\nReference titles that performed well:\n"
        + "\n".join(f"- {t}" for t in canal['exemplos_titulo']) +
        f"\n\nRULES:\n"
        f"- Counter-intuitive revelation (danger that looks safe)\n"
        f"- Real researcher or institution in title or script\n"
        f"- NOT a list (not '5 things about X')\n"
        f"- Short, punchy, 8-12 words max\n"
        f"- Return only the 5 titles, one per line, no numbering"
    )
    try:
        r = requests.post("https://api.groq.com/openai/v1/chat/completions",
            headers={"Authorization":f"Bearer {GROQ}","Content-Type":"application/json"},
            json={"model":"llama-3.3-70b-versatile",
                  "messages":[{"role":"user","content":prompt}],
                  "max_tokens":300,"temperature":0.88},
            timeout=15, verify=False)
        if r.status_code == 200:
            return r.json()["choices"][0]["message"]["content"].strip()
    except: pass
    return None

def groq_gerar_script_imersivo(titulo, nicho, idioma="PT"):
    """Script estilo imersivo (como o Marcos mostra no transcript)"""
    if not GROQ: return None
    lang = {"PT":"Portuguese Brazilian","EN":"English","ES":"Spanish",
            "DE":"German","FR":"French"}.get(idioma,"English")
    prompt = (
        f"Write a 75-word IMMERSIVE YouTube channel script in {lang}.\n"
        f"Title: {titulo}\n"
        f"Niche: {nicho}\n\n"
        f"STYLE: First person, as if experiencing it live (NOT a narrator)\n"
        f"FORMAT:\n"
        f"- Line 1: You're already IN the scene (no preamble)\n"
        f"- Line 2-3: Discovery that surprises you\n"
        f"- Line 4: Scientific/historical fact that explains it\n"
        f"- Line 5: What this means for the viewer\n"
        f"- Line 6: CTA: 'Save this' or 'Follow for more'\n\n"
        f"NO hashtags. NO lists. Pure immersive storytelling."
    )
    try:
        r = requests.post("https://api.groq.com/openai/v1/chat/completions",
            headers={"Authorization":f"Bearer {GROQ}","Content-Type":"application/json"},
            json={"model":"llama-3.3-70b-versatile",
                  "messages":[{"role":"user","content":prompt}],
                  "max_tokens":220,"temperature":0.87},
            timeout=15, verify=False)
        if r.status_code == 200:
            return r.json()["choices"][0]["message"]["content"].strip()
    except: pass
    return None

def imagen3_personagem(nicho, expressao, seed):
    """Daniela consistente adaptada ao nicho"""
    EXPRESSOES = {
        "surpresa":      "wide eyes, surprised expression, mouth slightly open",
        "reflexivo":     "contemplative gaze, slightly tilted head, soft smile",
        "serio":         "serious confident expression, direct gaze",
        "curioso":       "curious expression, raised eyebrow, slight smile",
        "arqueologico":  "adventurous expression, wearing explorer hat, excited",
        "geopolitico":   "analytical expression, pointing at map behind her",
    }
    expr = EXPRESSOES.get(expressao, EXPRESSOES["reflexivo"])
    prompt = (
        f"kawaii chibi anime girl character, short dark bob hair, mint-green blouse, "
        f"gold psi pin ψ, {expr}, psychology researcher aesthetic, "
        f"flat anime illustration, soft cream background #F5F0E8, "
        f"clean line art, no text, no watermarks, consistent character design"
    )
    p = TMP/f"daniela_{nicho}_{expressao}.jpg"
    if p.exists() and p.stat().st_size > 8000: return p
    url = (f"https://image.pollinations.ai/prompt/{requests.utils.quote(prompt[:400])}"
           f"?model=flux&width=576&height=1024&seed={seed}&nologo=true")
    try:
        r = requests.get(url, timeout=50, verify=False)
        if r.status_code == 200 and len(r.content) > 8000:
            p.write_bytes(r.content); return p
    except: pass
    return None

def salvar_video_key(titulo, script, nicho, formato, idioma, cpm):
    if not SB_KEY: return
    requests.post(f"{SB_URL}/rest/v1/en_channel_queue", headers=SBH,
        json={"titulo_en": titulo[:100], "script_en": script,
              "voz_en": "pt-BR-FranciscaNeural" if idioma=="PT" else "en-US-AriaNeural",
              "canal_destino": "UCyCkIpsVgME9yCj_oXJFheA",
              "rpm_estimado": float(cpm), "status": "pending"},
        timeout=8, verify=False)

def run():
    print("=" * 60)
    print("  NARRATIVA ENGINE — Equivalente ao 'Narrativa' do Marcos")
    print("  Estruturas Validadas + Personagem Consistente + 5 Nichos")
    print("=" * 60)

    total = 0
    seeds = [5001, 5002, 5003, 5004, 5005]

    for i, (nicho, cfg) in enumerate(CANAIS_REFERENCIA.items()):
        print(f"\n📺 NICHO: {nicho.upper()} (${cfg['cpm_usd']} CPM)")
        formato = cfg["formato"]
        cpm = cfg["cpm_usd"]

        # Gerar 5 títulos validados (Narrativa faz isso)
        for idioma in ["PT","EN"]:
            titulos_raw = groq_gerar_video_key(nicho, formato, idioma)
            if not titulos_raw: continue
            titulos = [t.strip() for t in titulos_raw.strip().split("\n") if t.strip()][:5]
            print(f"  [{idioma}] {len(titulos)} vídeos-chave gerados")

            for j, titulo in enumerate(titulos[:2]):  # 2 por nicho para não exceder quota
                script = groq_gerar_script_imersivo(titulo, nicho, idioma)
                if not script: continue
                salvar_video_key(titulo, script, nicho, formato, idioma, cpm)
                total += 1
                print(f"    ✅ {titulo[:55]}")
                time.sleep(1.5)

        # Daniela com expressão do nicho
        expr_map = {"psicologia":"reflexivo","geopolitica":"geopolitico",
                    "arqueologia":"arqueologico","neurociencia":"curioso"}
        expressao = expr_map.get(nicho, "reflexivo")
        daniela = imagen3_personagem(nicho, expressao, seeds[i])
        if daniela:
            print(f"  🎨 Daniela [{expressao}]: {daniela.stat().st_size//1024}KB")
        time.sleep(3)

    print(f"\n{'='*60}")
    print(f"  ✅ {total} vídeos-chave gerados em 4 nichos")
    print(f"  📊 CPMs: Geopolítica $28 > Neurociência $25 > Psicologia $20")
    print(f"  🎭 Personagem Daniela consistente em cada nicho")
    print(f"  🔑 Estruturas validadas de canais em ascensão")
    print("="*60)

if __name__=="__main__": run()
