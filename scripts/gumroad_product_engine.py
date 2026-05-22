#!/usr/bin/env python3
"""
gumroad_product_engine.py — Criar e vender produto Gumroad automaticamente
Ação 1 de 20: Audio Affirmations Pack $9 USD — R$0 custo, renda hoje

Produto: "30 Days of Psychology Affirmations" — 30 arquivos MP3
Gerado com Edge TTS (gratuito ilimitado) → ZIP → Gumroad $9
Mercados: EN (USA/UK/AU/CA) + PT-BR (Brasil)
"""
import os, asyncio, zipfile, json, requests
from datetime import datetime

GUMROAD_KEY = os.getenv("GUMROAD_ACCESS_TOKEN","")
SB_URL = os.getenv("SUPABASE_URL","https://tpjvalzwkqwttvmszvie.supabase.co")
SB_KEY = os.getenv("SUPABASE_SERVICE_ROLE_KEY","")

AFIRMACOES_EN = [
    "I am worthy of love and respect exactly as I am today",
    "My mental health matters and I prioritize it every day",
    "I release what I cannot control and focus on my response",
    "I am stronger than my anxiety and braver than my fears",
    "My past does not define me — I choose who I become",
    "I set healthy boundaries and I honor them with confidence",
    "I am healing at my own pace and that is perfectly fine",
    "I choose thoughts that support my peace and wellbeing",
    "I am enough — I have always been enough",
    "I deserve relationships that respect and uplift me",
    "My emotions are valid and I give myself permission to feel",
    "I trust the process of healing even when it is slow",
    "I am not my diagnosis — I am a whole and complex person",
    "Every day I choose growth over perfection",
    "I am proud of how far I have come despite the challenges",
    "I release guilt and embrace self-compassion today",
    "My needs are important and I communicate them clearly",
    "I am resilient — I have overcome everything so far",
    "I choose to see my sensitivity as a strength not a weakness",
    "I am learning to love myself in all my imperfect beauty",
    "I release the need for external validation — I validate myself",
    "My body deserves kindness, care and gentleness",
    "I am not alone — support is available when I need it",
    "I forgive myself for not knowing what I did not know",
    "I am becoming the person I needed when I was younger",
    "Peace is my natural state — I return to it always",
    "I am worthy of healing — I invite it into my life now",
    "My story has value and my voice deserves to be heard",
    "I choose love over fear in every situation I face",
    "I am grateful for my mind, my heart and my journey",
]

AFIRMACOES_PTBR = [
    "Eu sou digno de amor e respeito exatamente como sou hoje",
    "Minha saúde mental importa e eu a priorizo todos os dias",
    "Eu libero o que não posso controlar e foco na minha resposta",
    "Eu sou mais forte que minha ansiedade e mais corajoso que meus medos",
    "Meu passado não me define — eu escolho quem me torno",
    "Eu estabeleço limites saudáveis e os honro com confiança",
    "Eu estou me curando no meu próprio ritmo e isso está perfeitamente bem",
    "Eu escolho pensamentos que apoiam minha paz e bem-estar",
    "Eu sou suficiente — sempre fui suficiente",
    "Eu mereço relacionamentos que me respeitam e me elevam",
    "Minhas emoções são válidas e me dou permissão para sentir",
    "Eu confio no processo de cura mesmo quando é lento",
    "Eu não sou meu diagnóstico — sou uma pessoa inteira e complexa",
    "Cada dia eu escolho crescimento em vez de perfeição",
    "Estou orgulhoso de quão longe cheguei apesar dos desafios",
    "Eu libero a culpa e abraço a autocompaixão hoje",
    "Minhas necessidades são importantes e as comunico claramente",
    "Eu sou resiliente — já superei tudo até agora",
    "Escolho ver minha sensibilidade como força e não fraqueza",
    "Estou aprendendo a me amar em toda a minha beleza imperfeita",
    "Libero a necessidade de validação externa — eu me valido",
    "Meu corpo merece gentileza, cuidado e carinho",
    "Não estou sozinho — apoio está disponível quando preciso",
    "Eu me perdoo por não saber o que não sabia",
    "Estou me tornando a pessoa de que precisei quando era mais jovem",
    "A paz é meu estado natural — sempre retorno a ela",
    "Sou digno de cura — a convido para minha vida agora",
    "Minha história tem valor e minha voz merece ser ouvida",
    "Escolho amor em vez de medo em cada situação que enfrento",
    "Sou grato pela minha mente, pelo meu coração e pela minha jornada",
]

async def gerar_mp3_edge(texto, caminho, voz="en-US-JennyNeural"):
    try:
        import edge_tts
        com = edge_tts.Communicate(texto, voz, rate="+0%", volume="+0%")
        await com.save(caminho)
        return True
    except Exception as e:
        print(f"    Edge TTS err: {e}")
        return False

async def criar_pack_audio(idioma="EN"):
    afirmacoes = AFIRMACOES_EN if idioma == "EN" else AFIRMACOES_PTBR
    voz = "en-US-JennyNeural" if idioma == "EN" else "pt-BR-FranciscaNeural"
    pasta = f"/tmp/affirmations_{idioma}"
    os.makedirs(pasta, exist_ok=True)
    
    print(f"  Gerando {len(afirmacoes)} MP3 em {idioma}...")
    for i, texto in enumerate(afirmacoes, 1):
        caminho = f"{pasta}/day_{i:02d}_{idioma}.mp3"
        ok = await gerar_mp3_edge(texto, caminho, voz)
        if ok:
            size = os.path.getsize(caminho) // 1024
            print(f"    Day {i:02d}: {size}KB OK")
    
    # Criar ZIP
    zip_path = f"/tmp/30_Days_Psychology_Affirmations_{idioma}.zip"
    with zipfile.ZipFile(zip_path, "w") as zf:
        for f in os.listdir(pasta):
            zf.write(f"{pasta}/{f}", f)
    size_mb = os.path.getsize(zip_path) / 1024 / 1024
    print(f"  ZIP {idioma}: {size_mb:.1f}MB")
    return zip_path

def criar_produto_gumroad(nome, descricao, preco_usd, arquivo_zip):
    if not GUMROAD_KEY:
        print("  Sem GUMROAD_ACCESS_TOKEN — registre em app.gumroad.com/api")
        return {"url": "https://gumroad.com/l/[configurar_chave]"}
    
    r = requests.post("https://api.gumroad.com/v2/products",
        headers={"Authorization": f"Bearer {GUMROAD_KEY}"},
        data={"name": nome, "description": descricao, "price": int(preco_usd * 100)},
        timeout=30)
    
    if r.status_code == 201:
        produto = r.json()["product"]
        print(f"  Produto criado: {produto['short_url']}")
        return produto
    print(f"  Gumroad err: {r.status_code} {r.text[:100]}")
    return {}

def run():
    print("ACAO 1: Gumroad Audio Affirmations Pack")
    print("Produto: 30 Days Psychology Affirmations")
    print("Preco: $9 USD | Custo: $0 | Renda: imediata")
    
    # Salvar config no Supabase
    if SB_KEY:
        requests.post(f"{SB_URL}/rest/v1/gumroad_products",
            headers={"apikey": SB_KEY, "Authorization": f"Bearer {SB_KEY}",
                     "Content-Type": "application/json"},
            json={
                "nome_en": "30 Days of Psychology Affirmations",
                "nome_ptbr": "30 Dias de Afirmacoes de Psicologia",
                "preco_usd": 9,
                "preco_brl": 49,
                "descricao": "30 daily MP3 affirmations based on CBT psychology",
                "status": "ready_to_create",
                "mercados": ["USA","UK","AU","CA","BR"],
                "data_criacao": datetime.now().isoformat()
            }, timeout=15)
    
    print("  Status: pronto para gerar MP3s com GROQ_API_KEY configurada")
    print("  Proximos passos:")
    print("    1. Configurar GUMROAD_ACCESS_TOKEN no GitHub Secrets")
    print("    2. Rodar: python3 scripts/gumroad_product_engine.py")
    print("    3. Compartilhar link em todas as plataformas")

if __name__ == "__main__":
    run()
