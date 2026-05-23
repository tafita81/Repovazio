#!/usr/bin/env python3
"""
cerebro_crescimento_infinito.py — Cerebro V14
Sistema de geração infinita de conteúdo + WhatsApp
Roda a cada semana via GitHub Actions
"""
import os, json, time, requests, random
from supabase import create_client
from datetime import datetime, timedelta

SB_URL = os.environ["SUPABASE_URL"]
SB_KEY = os.environ["SUPABASE_KEY"]
sb = create_client(SB_URL, SB_KEY)

GROQ_KEY   = os.environ.get("GROQ_API_KEY","")
WA_TOKEN   = os.environ.get("WHATSAPP_TOKEN","")
WA_PHONE   = os.environ.get("WHATSAPP_PHONE_ID","")
OPENAI_KEY = os.environ.get("OPENAI_API_KEY","")

# ── FÓRMULAS DE TÍTULOS VIRAIS ─────────────────────────────────────
FORMULAS_TITULO = [
    "{N} sinais de {tema} que você {acao_surpreendente}",
    "Por que você {comportamento} quando tem {tema} — a ciência explica",
    "O que acontece no seu cérebro quando {situacao_tema}",
    "{Tema}: a resposta que você procurava sem saber",
    "Como {tema} está {destruindo/criando} {area_vida} sem você perceber",
    "{N} perguntas sobre {tema} que a ciência finalmente respondeu",
    "Você tem {tema} e chama de {nome_errado}",
    "A verdade sobre {tema} que ninguém tem coragem de falar",
    "{Tema} em {N} minutos: tudo que você precisa saber",
    "Depois desse vídeo sobre {tema} você nunca vai ser o mesmo",
]

# ── SAZONALIDADE BR ────────────────────────────────────────────────
SAZONALIDADE = {
    1:  ["autossabotagem metas", "trauma ano novo", "depressao janeiro"],
    2:  ["amor toxico", "dependencia emocional valentines", "apego ansioso relacionamentos"],
    3:  ["burnout feminino", "autoestima mulher", "saude mental mulher"],
    4:  ["familia e feridas infancia", "ansiedade pascoa"],
    5:  ["burnout materno", "dia das maes saude mental", "ferida materna"],
    6:  ["depressao inverno", "isolamento apego", "ansiedade frio"],
    7:  ["ansiedade social ferias", "relacionamentos verao"],
    8:  ["tdah volta aulas adulto", "ansiedade produtividade"],
    9:  ["setembro amarelo depressao", "saude mental setembro"],
    10: ["outubro rosa burnout feminino", "saude mental trabalho mulher"],
    11: ["novembro azul saude mental masculina", "narcisismo masculino"],
    12: ["luto festas familia", "ansiedade fim de ano", "narcisismo natal familia"],
}

def gerar_titulo_viral(serie: str, ordem: int, formula_idx: int = None) -> str:
    """Gera título viral para o próximo episódio de uma série"""
    if not GROQ_KEY:
        return f"{serie}: episódio {ordem} — o que você ainda não sabe"
    
    formula = FORMULAS_TITULO[formula_idx or (ordem % len(FORMULAS_TITULO))]
    mes_atual = datetime.now().month
    sazo = SAZONALIDADE.get(mes_atual, [])
    sazo_hint = f"Sazonalidade atual (mês {mes_atual}): {', '.join(sazo[:2])}" if sazo else ""
    
    prompt = f"""Gere um título viral para YouTube sobre a série "{serie}", episódio {ordem}.
Fórmula base: {formula}
{sazo_hint}
Regras:
- Máximo 70 caracteres
- Segunda pessoa (você)
- Gera curiosidade irresistível
- SEO: inclua palavra-chave principal da série
- NÃO use "pesquisadora de comportamento humano", "CRP" ou termos médicos
- Responda APENAS com o título, sem aspas"""
    
    try:
        r = requests.post("https://api.groq.com/openai/v1/chat/completions",
            headers={"Authorization": f"Bearer {GROQ_KEY}", "Content-Type": "application/json"},
            json={"model": "llama-3.3-70b-versatile", "messages": [{"role":"user","content":prompt}], "max_tokens": 100},
            timeout=15)
        return r.json()["choices"][0]["message"]["content"].strip().strip('"')
    except:
        return f"{serie}: episódio {ordem}"

def gerar_episodios_proxima_fase(serie: str):
    """Gera EP11-EP20 quando série completa os primeiros 10"""
    # Verificar qual a maior ordem atual
    r = sb.table("content_pipeline").select("metadata").eq(
        "metadata->>serie", serie
    ).not_.is_("metadata->>ordem", None).execute()
    
    ordens = [int(v["metadata"]["ordem"]) for v in (r.data or []) if v["metadata"].get("ordem")]
    max_ordem = max(ordens) if ordens else 10
    
    if max_ordem < 10:
        return 0
    
    # Verificar se já tem EP11+
    tem_11_plus = any(o > 10 for o in ordens)
    if tem_11_plus:
        return 0
    
    # Gerar EP11-EP20
    novos = 0
    for i in range(11, 21):
        titulo = gerar_titulo_viral(serie, i)
        # Alternar long/short
        formato = "short_60s" if i % 4 == 0 else "youtube_long"
        target = 54 if formato == "short_60s" else 4500
        
        existing = sb.table("content_pipeline").select("id").ilike("title", f"%{titulo[:30]}%").execute()
        if existing.data:
            continue
            
        sb.table("content_pipeline").insert({
            "title": titulo,
            "status": "pending_generation",
            "score": 0,
            "metadata": {
                "serie": serie,
                "episodio": f"S{i:02d}",
                "ordem": i,
                "formato": formato,
                "target_palavras": target if formato == "youtube_long" else None,
                "target_segundos": target if formato == "short_60s" else 900,
                "cerebro_v14": True,
                "render_method": "flux_kenburns_v2",
                "geracao": "automatica_fase_2"
            }
        }).execute()
        novos += 1
        print(f"  + {serie} EP{i:02d}: {titulo}")
        time.sleep(0.5)
    
    return novos

def gerar_conteudo_sazonal():
    """Gera conteúdo sazonal baseado no mês atual"""
    mes = datetime.now().month
    temas = SAZONALIDADE.get(mes, [])
    if not temas:
        return 0
    
    novos = 0
    for tema in temas:
        titulo = gerar_titulo_viral(tema, 1, 0)
        
        # Detectar série
        serie = "Mente e Emocoes"
        t = tema.lower()
        if "burnout" in t: serie = "Burnout"
        elif "ansiedade" in t: serie = "Ansiedade e Panico"
        elif "depressao" in t: serie = "Depressao"
        elif "apego" in t: serie = "Apego Ansioso"
        elif "narcisismo" in t: serie = "Narcisismo"
        elif "trauma" in t or "ferida" in t: serie = "Trauma Invisivel"
        elif "luto" in t: serie = "Luto e Perda"
        
        existing = sb.table("content_pipeline").select("id").ilike("title", f"%{tema[:20]}%").execute()
        if existing.data:
            continue
        
        sb.table("content_pipeline").insert({
            "title": titulo,
            "status": "pending_generation",
            "score": 0,
            "metadata": {
                "serie": serie,
                "formato": "youtube_long",
                "target_palavras": 4500,
                "target_segundos": 900,
                "seo_keyword": tema,
                "cerebro_v14": True,
                "render_method": "flux_kenburns_v2",
                "geracao": "automatica_sazonal",
                "sazonalidade": f"mes_{mes}"
            }
        }).execute()
        novos += 1
        print(f"  + Sazonal: {titulo}")
    
    return novos

def postar_whatsapp_video(video: dict):
    """Posta novo vídeo em todos os grupos WhatsApp relevantes"""
    if not WA_TOKEN or not WA_PHONE:
        print("  WhatsApp: credenciais não configuradas")
        return 0
    
    serie = video.get("metadata", {}).get("serie", "")
    titulo = video.get("title", "")
    yt_url = video.get("youtube_url", "")
    
    if not yt_url:
        return 0
    
    # Buscar grupo da série
    r = sb.table("whatsapp_grupos").select("*").eq("serie", serie).execute()
    if not r.data:
        return 0
    
    grupo = r.data[0]
    grupo_id = grupo.get("grupo_id")
    config = grupo.get("config", {})
    
    if not grupo_id:
        return 0
    
    # Montar mensagem
    cta = config.get("cta_video", "Novo vídeo no canal!")
    pergunta = random.choice(config.get("perguntas_semanais", ["O que você achou?"]))
    msg = f"{cta}\n\n🎬 *{titulo}*\n{yt_url}\n\n💬 {pergunta}"
    
    # Delay humanizado (30-90 minutos após publicação)
    time.sleep(random.randint(60, 180))
    
    try:
        resp = requests.post(
            f"https://graph.facebook.com/v18.0/{WA_PHONE}/messages",
            headers={"Authorization": f"Bearer {WA_TOKEN}", "Content-Type": "application/json"},
            json={"messaging_product": "whatsapp", "to": grupo_id,
                  "type": "text", "text": {"body": msg}},
            timeout=15)
        
        if resp.status_code == 200:
            sb.table("whatsapp_grupos").update({
                "mensagens_enviadas": grupo["mensagens_enviadas"] + 1,
                "ultimo_post": datetime.now().isoformat()
            }).eq("id", grupo["id"]).execute()
            print(f"  ✓ WhatsApp [{serie}]: mensagem enviada")
            return 1
    except Exception as e:
        print(f"  WhatsApp erro: {e}")
    return 0

def engajar_grupos_semana():
    """Posta conteúdo semanal em todos os grupos (segunda, quarta, sexta)"""
    if not WA_TOKEN or not WA_PHONE:
        return
    
    dia = datetime.now().weekday()  # 0=segunda, 2=quarta, 4=sexta
    if dia not in [0, 2, 4]:
        return
    
    tipos_por_dia = {
        0: "pergunta_reflexiva",
        2: "dado_cientifico",
        4: "exercicio_pratico"
    }
    tipo = tipos_por_dia[dia]
    
    grupos = sb.table("whatsapp_grupos").select("*").execute()
    for grupo in (grupos.data or []):
        if not grupo.get("grupo_id"):
            continue
        config = grupo.get("config", {})
        
        if tipo == "pergunta_reflexiva":
            perguntas = config.get("perguntas_semanais", ["Como você está esta semana?"])
            msg = f"🧠 *Reflexão de segunda*\n\n{random.choice(perguntas)}\n\nResponda aqui no grupo — sua experiência pode ajudar alguém 💙"
        elif tipo == "dado_cientifico":
            msg = f"🔬 *Curiosidade científica*\n\nSabia que estudos mostram que reconhecer padrões de {grupo['serie']} é o primeiro passo para mudá-los?\n\nAssistiu os episódios da série? 🎬"
        else:
            msg = f"✅ *Exercício de sexta*\n\nDedique 5 minutos hoje para:\n• Identificar um padrão de {grupo['serie']} na sua semana\n• Escrever como ele apareceu\n• Pensar numa reação diferente\n\nPartilhe se quiser 💙"
        
        # Delay humanizado entre grupos
        time.sleep(random.randint(120, 480))
        try:
            requests.post(
                f"https://graph.facebook.com/v18.0/{WA_PHONE}/messages",
                headers={"Authorization": f"Bearer {WA_TOKEN}", "Content-Type": "application/json"},
                json={"messaging_product": "whatsapp", "to": grupo["grupo_id"],
                      "type": "text", "text": {"body": msg}},
                timeout=15)
            print(f"  ✓ WA semanal [{grupo['serie']}]")
        except Exception as e:
            print(f"  WA erro [{grupo['serie']}]: {e}")

def main():
    print(f"=== CRESCIMENTO INFINITO — Cerebro V14 ===")
    print(f"Data: {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    
    # 1. Verificar séries que completaram EP10 → gerar EP11-EP20
    series = sb.table("content_pipeline").select("metadata->>serie").not_.is_("metadata->>serie", None).execute()
    series_unicas = list(set(v["serie"] for v in (series.data or []) if v.get("serie")))
    
    total_novos = 0
    print(f"\n1. Expandindo séries ({len(series_unicas)} séries)...")
    for serie in series_unicas:
        novos = gerar_episodios_proxima_fase(serie)
        if novos > 0:
            total_novos += novos
            print(f"   {serie}: +{novos} episódios gerados")
    
    # 2. Conteúdo sazonal do mês
    print(f"\n2. Gerando conteúdo sazonal (mês {datetime.now().month})...")
    sazonais = gerar_conteudo_sazonal()
    print(f"   +{sazonais} temas sazonais")
    
    # 3. Engajamento semanal WhatsApp
    print(f"\n3. WhatsApp — engajamento semanal...")
    engajar_grupos_semana()
    
    # 4. Verificar vídeos publicados recentemente → postar no WA
    print(f"\n4. Verificando vídeos recém-publicados para WhatsApp...")
    recentes = sb.table("content_pipeline").select("*").eq(
        "status", "published"
    ).gte("updated_at", (datetime.now() - timedelta(hours=2)).isoformat()).execute()
    
    wa_posts = 0
    for video in (recentes.data or []):
        wa_posts += postar_whatsapp_video(video)
    
    # 5. Registrar evolução
    sb.table("cerebro_evolucao").insert({
        "versao": "v14",
        "tipo": "crescimento_infinito",
        "descricao": f"Ciclo crescimento: +{total_novos} ep novos, +{sazonais} sazonais, {wa_posts} WA posts",
        "mudancas": {"novos_episodios": total_novos, "sazonais": sazonais, "wa_posts": wa_posts}
    }).execute()
    
    print(f"\n✅ Concluído: {total_novos} episódios + {sazonais} sazonais + {wa_posts} WA posts")

if __name__ == "__main__":
    main()
