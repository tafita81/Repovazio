#!/usr/bin/env python3
"""
tiktok_shop_engine.py — Motor de conteúdo TikTok Shop

Baseado no modelo: R$5.600 em 7 dias sem mostrar rosto.
Plataforma: TikTok Shop Brasil + TikTok Shop Internacional.

FUNIL:
  1. Gerar hooks virais com dados PubMed (autoridade científica)
  2. Criar vídeo animado 9:16 (Robonil gratuito)
  3. Postar como UGC sem rosto — Daniela Coelho como persona
  4. Produto físico via TikTok Shop afiliado OU digital (Hotmart/Gumroad)

TIPOS DE VÍDEO QUE FUNCIONAM:
  - Modelo se movimentando SEM falar (puro visual + texto)
  - Review de produto com close da embalagem
  - "POV: você descobre que..." (chibi reage)
  - Antes/depois (split screen)
  - Contador regressivo ("3 sinais que...")
"""
import os, requests, pathlib, subprocess, time

TMP = pathlib.Path("/tmp/tiktok_shop"); TMP.mkdir(exist_ok=True)
GROQ = os.getenv("GROQ_API_KEY", "")
SB_URL = os.getenv("SUPABASE_URL", "")
SB_KEY = os.getenv("SUPABASE_SERVICE_KEY", "")
SBH = {"apikey": SB_KEY, "Authorization": f"Bearer {SB_KEY}",
       "Content-Type": "application/json", "Prefer": "return=minimal"}
GH_RAW = "https://raw.githubusercontent.com/tafita81/Repovazio/main"

# Hooks virais por tipo (baseados em análise de vídeos 1M+ views)
FORMULAS_HOOK = [
    "POV: você acabou de descobrir que {insight_psicologia}",
    "{numero} sinais de que seu sistema nervoso está em colapso",
    "Neurociência explica por que você {comportamento_comum}",
    "Testei por {dias} dias. Resultado: {resultado_impactante}",
    "Se você faz isso {comportamento}, você tem {padrão_psicologico}",
    "A razão científica por que você {emoção_comum} à noite",
]

INSIGHTS_PSICOLOGIA = [
    ("você se sabota quando está perto da felicidade", "self-sabotage psychology"),
    ("escolhe pessoas emocionalmente indisponíveis", "anxious attachment avoidant"),
    ("seu cérebro interpreta rejeição como dor física", "rejection social pain brain"),
    ("você ainda está processando traumas de anos atrás", "childhood trauma nervous system"),
    ("estresse crônico encolhe literalmente seu hipocampo", "chronic stress hippocampus shrinkage"),
    ("solidão é tão prejudicial quanto fumar 15 cigarros por dia", "loneliness mortality risk"),
    ("28% das pessoas têm burnout sem saber", "burnout prevalence symptoms"),
    ("seu apego ansioso foi formado antes dos 5 anos", "early attachment formation"),
]

def pubmed(query):
    try:
        r = requests.get(
            f"https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi?db=pubmed&term={requests.utils.quote(query)}&retmax=1&retmode=json",
            timeout=7)
        pmids = r.json().get("esearchresult", {}).get("idlist", [])
        if pmids:
            r2 = requests.get(
                f"https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esummary.fcgi?db=pubmed&id={pmids[0]}&retmode=json",
                timeout=7)
            doc = r2.json().get("result", {}).get(pmids[0], {})
            a = (doc.get("authors", [{}]) or [{}])[0].get("name", "")
            return f"{a} ({doc.get('pubdate', '')[:4]}), PubMed"
    except: pass
    return "Research (NCBI)"

def gerar_hook(insight, cit, idioma="PT"):
    if not GROQ: return f"Neurociência explica: {insight[:50]}"
    lang = "português brasileiro" if idioma == "PT" else "English"
    try:
        r = requests.post("https://api.groq.com/openai/v1/chat/completions",
            headers={"Authorization": f"Bearer {GROQ}", "Content-Type": "application/json"},
            json={"model": "llama-3.3-70b-versatile",
                  "messages": [{"role": "user", "content":
                    f"Crie um hook TikTok viral em {lang} sobre: {insight}\n"
                    f"Pesquisa real: {cit}\n"
                    f"Regras: máx 12 palavras, começa com número ou POV ou 'Neurociência', "
                    f"para o scroll imediatamente, usa dado científico.\n"
                    f"Retorna APENAS o hook."}],
                  "max_tokens": 50, "temperature": 0.85},
            timeout=15)
        if r.status_code == 200:
            return r.json()["choices"][0]["message"]["content"].strip()
    except: pass
    return f"Neurociência explica: {insight[:50]}"

def criar_overlay_tiktok(img_p, hook, produto, hashtags, out_p, duracao=9):
    """
    Monta vídeo TikTok 9:16 com:
    - Ken Burns animation (Robonil free)
    - Hook no topo (para o scroll)
    - Produto + CTA no rodapé
    """
    hook_e = hook[:55].replace("'", r"\'")
    prod_e = produto[:35].replace("'", r"\'")
    tags_e = hashtags[:55].replace("'", r"\'")

    # Ken Burns zoom in (efeito câmera natural)
    vf_anim = (
        "scale=8000:-1,"
        f"zoompan=z='min(zoom+0.0012,1.4)':d={duracao*25}:"
        "x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':fps=25:s=1080x1920,"
    )
    vf_overlay = (
        "colorchannelmixer=rr=0.72:gg=0.72:bb=0.72,"
        "drawbox=y=0:color=black@0.82:width=iw:height=175:t=fill,"
        "drawbox=y=ih-200:color=black@0.88:width=iw:height=200:t=fill,"
        "drawbox=y=165:color=#EF4444:width=iw:height=4:t=fill,"
        # Ícone ⚡ antes do hook
        "drawtext=text='⚡':fontsize=32:fontcolor=#FBBF24:x=20:y=20,"
        f"drawtext=text='{hook_e}':fontsize=34:fontcolor=white:x=70:y=15:"
        "bold=1:shadowcolor=#000:shadowx=2:shadowy=2:line_spacing=6,"
        # Badge "SCIENCE" no canto
        "drawbox=x=iw-120:y=0:color=#7C3AED:width=120:height=44:t=fill,"
        "drawtext=text='SCIENCE':fontsize=15:fontcolor=white:x=iw-105:y=14:bold=1,"
        # Produto
        f"drawtext=text='📦 {prod_e}':fontsize=26:fontcolor=#FCD34D:"
        "x=(w-text_w)/2:y=ih-175:bold=1,"
        # Hashtags
        f"drawtext=text='{tags_e}':fontsize=17:fontcolor=#94A3B8:"
        "x=(w-text_w)/2:y=ih-130,"
        # CTA
        "drawtext=text='🛒 Clique no link':fontsize=24:fontcolor=white:"
        "x=(w-text_w)/2:y=ih-80:bold=1"
    )
    vf = vf_anim + vf_overlay

    subprocess.run(["ffmpeg", "-y", "-loop", "1", "-i", str(img_p),
        "-vf", vf, "-t", str(duracao),
        "-c:v", "libx264", "-preset", "fast", "-pix_fmt", "yuv420p",
        "-r", "25", "-an", str(out_p)],
        capture_output=True, timeout=180)
    return out_p.exists() and out_p.stat().st_size > 50000

def run():
    print("=== TIKTOK SHOP CONTENT ENGINE ===\n")
    total = 0
    for insight, query in INSIGHTS_PSICOLOGIA[:5]:
        cit = pubmed(query)
        print(f"\n  💡 {insight[:45]}...")
        print(f"     Ref: {cit[:50]}")
        for idioma in ["PT", "EN"]:
            hook = gerar_hook(insight, cit, idioma)
            print(f"     [{idioma}] Hook: {hook[:55]}")
            # Baixar imagem psych (chibi anime — 8.5/10)
            img_p = TMP / f"base_psych_{idioma}.jpg"
            if not img_p.exists():
                r = requests.get(f"{GH_RAW}/public/estilos_virais/psych2go.jpg", timeout=15)
                if r.status_code == 200:
                    img_p.write_bytes(r.content)
            if img_p.exists():
                out = TMP / f"tt_{idioma}_{total:03d}.mp4"
                produto_nome = "Diário Psicologia"
                tags = "#psicologia #saúdemental #terapia #fyp" if idioma == "PT" else "#psychology #mentalhealth #therapy #fyp"
                ok = criar_overlay_tiktok(img_p, hook, produto_nome, tags, out, 9)
                if ok:
                    total += 1
                    print(f"     ✅ {out.name} ({out.stat().st_size//1024}KB)")
                    if SB_KEY:
                        requests.post(f"{SB_URL}/rest/v1/tiktok_shop_queue", headers=SBH,
                            json={"produto": produto_nome, "hook": hook[:200],
                                  "hashtags": tags, "idioma": idioma, "insight": insight[:200],
                                  "citacao": cit[:200], "status": "mp4_ready"},
                            timeout=8)
            time.sleep(1.5)
        time.sleep(3)
    print(f"\n{'='*48}")
    print(f"  ✅ {total} vídeos TikTok gerados")
    print(f"  📊 Dados reais de PubMed = autoridade científica")
    print(f"  🎭 Daniela Coelho = persona anônima")
    print(f"  📱 Formato: 9:16, 9 segundos, hook stop-scroll")

if __name__ == "__main__":
    run()
