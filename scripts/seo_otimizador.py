#!/usr/bin/env python3
"""
seo_otimizador.py — Cerebro V14
Otimiza automaticamente títulos, descrições e tags
para máximo SEO no YouTube, Google e redes sociais
"""
import os, json, time, requests, re
from supabase import create_client

SB_URL = os.environ["SUPABASE_URL"]
SB_KEY = os.environ["SUPABASE_KEY"]
sb = create_client(SB_URL, SB_KEY)

GROQ_KEY  = os.environ.get("GROQ_API_KEY","")
OPENAI_KEY = os.environ.get("OPENAI_API_KEY","")

# VOLUMES DE BUSCA BR 2026
KEYWORDS_VOLUME = {
    "ansiedade": 200000, "depressao": 150000, "tdah": 110000,
    "burnout": 80000, "narcisismo": 74000, "autoconhecimento": 70000,
    "apego ansioso": 65000, "trauma": 60000, "relacionamento toxico": 58000,
    "inteligencia emocional": 55000, "gaslighting": 45000,
    "borderline": 40000, "luto": 40000, "autossabotagem": 35000,
    "dependencia emocional": 30000, "feridas infancia": 25000,
    "pessoas altamente sensiveis": 20000, "lideranca toxica": 15000,
}

# KEYWORDS POR SÉRIE
SERIE_KEYWORDS = {
    "Ansiedade e Panico": ["ansiedade", "ansiedade social", "crise de panico", "ansiedade o que e", "sintomas ansiedade"],
    "Apego Ansioso":      ["apego ansioso", "medo abandono", "estilos de apego", "apego ansioso cura"],
    "Mentes Narcisistas": ["narcisismo", "narcisista", "abuso narcisista", "narcisismo encoberto"],
    "Trauma Invisivel":   ["trauma", "trauma invisivel", "trauma infancia adulto", "cptsd"],
    "Burnout":            ["burnout", "esgotamento profissional", "burnout sintomas", "burnout cura"],
    "Gaslighting":        ["gaslighting", "gaslighting o que e", "frases gaslighting", "gaslighting relacionamento"],
    "Borderline":         ["borderline", "tpb", "transtorno personalidade borderline", "borderline sintomas"],
    "Depressao":          ["depressao", "depressao o que e", "sintomas depressao", "depressao nao e fraqueza"],
    "TDAH no Adulto":     ["tdah adulto", "tdah mulher", "tdah nao diagnosticado", "tdah sintomas adulto"],
    "Narcisismo":         ["narcisismo", "narcisista como identificar", "abuso narcisista recuperacao"],
    "Luto e Perda":       ["luto", "como superar luto", "fases do luto", "luto e perda"],
    "Autossabotagem":     ["autossabotagem", "como parar autossabotagem", "sindrome impostor"],
    "Autoconhecimento":   ["autoconhecimento", "como se conhecer", "autoconhecimento o que e"],
    "Inteligencia Emocional": ["inteligencia emocional", "como desenvolver IE", "IE no trabalho"],
    "Relacionamentos Toxicos": ["relacionamento toxico", "como sair relacionamento toxico", "love bombing"],
    "Dependencia Emocional":   ["dependencia emocional", "como superar dependencia", "amor ou dependencia"],
    "Feridas da Infancia":     ["feridas infancia", "crianca interior", "trauma infancia adulto"],
    "Pessoas Altamente Sensiveis": ["pessoa altamente sensivel", "PAS", "alta sensibilidade"],
    "Lideranca Toxica":   ["lideranca toxica", "chefe toxico", "trabalho toxico"],
}

def gerar_metadados_seo(video: dict) -> dict:
    """Gera título, descrição e tags otimizadas para SEO"""
    if not GROQ_KEY:
        return {}
    
    titulo_atual = video.get("title","")
    serie = video.get("metadata",{}).get("serie","")
    ordem = int(video.get("metadata",{}).get("ordem",1) or 1)
    script = (video.get("script","") or "")[:500]
    seo_kw = video.get("metadata",{}).get("seo_keyword","")
    keywords_serie = SERIE_KEYWORDS.get(serie, [seo_kw] if seo_kw else [])
    kw_principal = keywords_serie[0] if keywords_serie else titulo_atual[:30]
    
    prompt = f"""Você é especialista em SEO para YouTube Brasil 2026.
Otimize os metadados deste vídeo para máximo ranqueamento no YouTube e Google.

VÍDEO:
Título atual: {titulo_atual}
Série: {serie} (EP{ordem:02d})
Keyword principal: {kw_principal}
Keywords da série: {', '.join(keywords_serie[:5])}
Trecho do script: {script[:200]}...

REGRAS SEO 2026:
1. Título: keyword EXATA nas primeiras 3 palavras | máx 60 chars | gatilho emocional | ex: "Apego Ansioso: você tem e não sabe"
2. Descrição linha 1-2: keyword + promessa (indexado pelo Google como snippet)
3. Descrição total: 400-500 palavras com keywords naturais + chapters + links
4. Tags: exatamente 15 tags relevantes
5. NUNCA usar "pesquisadora de comportamento humano" ou "CRP"

Responda APENAS em JSON válido:
{{
  "titulo_seo": "...",
  "descricao_seo": "...",
  "tags": ["tag1","tag2",...],
  "hashtags_instagram": ["#tag1","#tag2","#tag3","#tag4","#tag5"],
  "caption_tiktok": "...(150 chars max)...",
  "descricao_pin": "...(200 chars)..."
}}"""
    
    try:
        r = requests.post("https://api.groq.com/openai/v1/chat/completions",
            headers={"Authorization":f"Bearer {GROQ_KEY}","Content-Type":"application/json"},
            json={"model":"llama-3.3-70b-versatile","messages":[{"role":"user","content":prompt}],"max_tokens":1500},
            timeout=25)
        resp_text = r.json()["choices"][0]["message"]["content"].strip()
        # Extrair JSON
        json_match = resp_text[resp_text.find("{"):resp_text.rfind("}")+1]
        return json.loads(json_match)
    except Exception as e:
        print(f"SEO geração erro: {e}")
        return {}

def processar_videos_sem_seo():
    """Processa vídeos que ainda não têm metadados SEO otimizados"""
    videos = sb.table("content_pipeline").select("id,title,script,metadata").filter(
        "metadata->>'seo_otimizado'", "neq", "true"
    ).in_("status", ["pending_generation","script_ready","mp4_ready","video_ready"]).order(
        "id", desc=False
    ).limit(20).execute()
    
    total = 0
    for v in (videos.data or []):
        if not v.get("title"):
            continue
        meta = v.get("metadata", {}) or {}
        serie = meta.get("serie","")
        if not serie:
            continue
        
        print(f"  SEO #{v['id']}: {v['title'][:50]}")
        seo = gerar_metadados_seo(v)
        
        if seo.get("titulo_seo"):
            new_meta = {**meta, **seo, "seo_otimizado": True, "seo_em": int(time.time())}
            update = {"metadata": new_meta}
            if seo.get("titulo_seo") and len(seo["titulo_seo"]) > 10:
                update["title"] = seo["titulo_seo"]  # Atualizar com título SEO
            sb.table("content_pipeline").update(update).eq("id", v["id"]).execute()
            total += 1
            time.sleep(1.5)  # Rate limit
    
    return total

def gerar_capitulos_youtube(script: str, duracao_segundos: int = 900) -> str:
    """Gera capítulos do YouTube baseados no script"""
    if not GROQ_KEY or not script:
        return ""
    
    try:
        r = requests.post("https://api.groq.com/openai/v1/chat/completions",
            headers={"Authorization":f"Bearer {GROQ_KEY}","Content-Type":"application/json"},
            json={"model":"llama-3.3-70b-versatile","messages":[{"role":"user","content":
                f"Crie 8-10 capítulos YouTube para um vídeo de {duracao_segundos//60} minutos. Script: {script[:800]}...\nFormato: 00:00 Nome | 02:30 Nome | etc. APENAS os capítulos, nada mais."}],
                "max_tokens":200},
            timeout=15)
        return r.json()["choices"][0]["message"]["content"].strip()
    except:
        return ""

def main():
    print("=== SEO OTIMIZADOR — Cerebro V14 ===")
    total = processar_videos_sem_seo()
    print(f"✓ {total} vídeos otimizados para SEO")
    
    # Registrar evolução
    sb.table("cerebro_evolucao").insert({
        "versao":"v14","tipo":"seo_otimizacao",
        "descricao":f"SEO auto: {total} videos otimizados",
        "mudancas":{"videos_seo":total}
    }).execute()

if __name__ == "__main__":
    main()
