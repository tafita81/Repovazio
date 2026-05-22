#!/usr/bin/env python3
"""
affiliate_ugc_engine.py — Workflow EXATO do vídeo Higfield+Claude
Replica passo a passo o que foi mostrado.

IMPORTANTE: Vídeos gerados por IA devem ser declarados com #publi #ad
conforme exigência do CONAR (Brasil) e termos das plataformas.
"""

import os, json, time, requests
from datetime import datetime

GROQ_KEY     = os.getenv("GROQ_API_KEY", "")
NVIDIA_KEY   = os.getenv("NVIDIA_API_KEY", "")
HEYGEN_KEY   = os.getenv("HEYGEN_API_KEY", "")
DID_KEY      = os.getenv("DID_API_KEY", "")
HIGFIELD_KEY = os.getenv("HIGFIELD_API_KEY", "")
SB_URL       = os.getenv("SUPABASE_URL", "https://tpjvalzwkqwttvmszvie.supabase.co")
SB_KEY       = os.getenv("SUPABASE_SERVICE_ROLE_KEY", "")

# ══════════════════════════════════════════════════════════════════
# PROMPT EXATO DO VÍDEO — passo 1: pesquisa de nichos
# ══════════════════════════════════════════════════════════════════
PROMPT_NICHOS = """Aja como estrategista de elite em marketing de afiliados, especializado em plataformas de conteúdo de formato curto como TikTok, Instagram e Pinterest.

Encontre 5 categorias de produtos que estão em alta no momento no Brasil e que têm forte potencial de monetização via afiliados.

Para cada categoria, forneça:
- Por que essa categoria tem bom desempenho especificamente em plataformas   de vídeo curto
- O tipo de público que compra esse produto
- Faixa estimada de comissão de afiliados ou potencial de ganhos
- O estilo de vídeo com melhor conversão (UGC, storytelling, problema/solução,   demonstração, visuais gerados por IA etc.)
- Os tipos de hooks que costumam performar melhor
- Se o nicho é melhor para compras por impulso de baixo ticket ou comissões   de alto ticket
- Quão saturado o nicho está atualmente
- O ângulo de conteúdo mais fácil para iniciantes entrarem no mercado

Depois, classifique as 5 categorias com base em:
1. Potencial de ganhos
2. Facilidade de criar conteúdo viral
3. Amigável para iniciantes
4. Escalabilidade a longo prazo

Foca em categorias que estão performando bem ativamente em 2026, não em nichos de afiliados ultrapassados. Mantenha a análise prática e focada em oportunidades realistas de ganhar dinheiro em vez de conselhos genéricos.

Responda em JSON com esta estrutura:
{
  "nichos": [
    {
      "ranking": 1,
      "categoria": "nome",
      "potencial_ganhos": "alto/medio/baixo",
      "ticket": "baixo/alto",
      "saturacao": "baixa/media/alta",
      "facilidade_iniciante": 8,
      "plataformas_afiliado": ["Shopee", "Hotmart"],
      "comissao_range": "5-20%",
      "estilo_video": "UGC autêntico",
      "hooks_top": ["hook 1", "hook 2"],
      "marcas_pagam_bem": ["Marca A", "Marca B"],
      "por_que_funciona": "explicação curta"
    }
  ],
  "veredito": "qual escolher e por quê"
}"""

# ══════════════════════════════════════════════════════════════════
# PROMPT EXATO DO VÍDEO — passo 2: encontrar produto top
# ══════════════════════════════════════════════════════════════════
PROMPT_PRODUTO_TPL = """Você é expert em marketing de afiliados no Brasil.
Nicho: {nicho}
Marca sugerida: {marca}

Encontre o produto MAIS VENDIDO dessa marca nesse nicho que:
1. Tem comissão de afiliado acima da média
2. Avaliações acima de 4.5 estrelas
3. Está viralizando em 2026
4. Tem imagem de produto disponível no site oficial

Responda em JSON:
{{
  "produto": "nome completo",
  "marca": "marca",
  "preco": "R$ XX",
  "comissao": "X%",
  "site_oficial": "url",
  "imagem_url": "url imagem",
  "beneficios_principais": ["b1", "b2", "b3"],
  "publico_comprador": "descrição",
  "por_que_viral": "motivo",
  "hooks_sugeridos": ["hook 1", "hook 2", "hook 3"]
}}"""

# ══════════════════════════════════════════════════════════════════
# PROMPT EXATO DO VÍDEO — passo 3: gerar vídeo UGC com Higfield
# ══════════════════════════════════════════════════════════════════
PROMPT_VIDEO_TPL = """Leia a descrição do produto {produto} da {marca} e a imagem fornecida acima para entender exatamente os benefícios, textura e proposta visual do produto.

Em seguida, use o Connector Higfield para criar um vídeo UGC natural de afiliado com duração de 15 segundos em formato vertical 9x16.

Você deve usar o modelo Sidence 2.0 para garantir movimentos humanos ultra realistas, naturais e cinematográficos.

O vídeo deve ter estética Clean Beauty Premium, iluminação suave e realista, aparência orgânica e emocionalmente autêntica. O tom deve transmitir autocuidado, resultado real e confiança natural.

O vídeo deve seguir exatamente este fluxo:

1. (0-3s) HOOK: "{hook}" — câmera selfie frontal, garota de ~25 anos,    sentada na cama à noite, segurando o produto próximo ao rosto.    Aparência cansada, com pequenas marcas visíveis, fala de forma    genuína e íntima como vídeo espontâneo de rotina.

2. (3-8s) PROBLEMA: Take cinematográfico noturno, olhando celular na    cama, demonstrando frustração com a pele/situação. Toca o rosto    suavemente enquanto a luz azul do celular ilumina parcialmente.

3. (8-12s) APLICAÇÃO: Aplicando o produto naturalmente diante do espelho    ou câmera frontal. Mostra textura real do produto, aplicação em    movimentos suaves e naturais.

4. (12-15s) RESULTADO: Expressão de satisfação, pele visivelmente melhor    mas ainda natural (não perfeita), confiança. Produto visível.

Objetivo: criar um vídeo que pareça conteúdo espontâneo de TikTok/Reels, transmitindo autocuidado genuíno e melhora visual usando {produto}.

IMPORTANTE: Este é conteúdo criado por IA. O criador deve adicionar #publi #ad e identificação "conteúdo gerado por IA" conforme CONAR/FTC."""

# ══════════════════════════════════════════════════════════════════
# FUNÇÕES
# ══════════════════════════════════════════════════════════════════

def chamar_llm(prompt: str) -> dict:
    """Chama LLM (Groq → Nvidia → fallback)"""
    providers = []
    if GROQ_KEY:
        providers.append({
            "url": "https://api.groq.com/openai/v1/chat/completions",
            "headers": {"Authorization": f"Bearer {GROQ_KEY}"},
            "model": "llama-3.3-70b-versatile"
        })
    if NVIDIA_KEY:
        providers.append({
            "url": "https://integrate.api.nvidia.com/v1/chat/completions",
            "headers": {"Authorization": f"Bearer {NVIDIA_KEY}"},
            "model": "deepseek-ai/deepseek-r1-distill-llama-70b"
        })

    for p in providers:
        try:
            r = requests.post(
                p["url"],
                headers={**p["headers"], "Content-Type": "application/json"},
                json={
                    "model": p["model"],
                    "messages": [{"role":"user","content":prompt}],
                    "max_tokens": 3000,
                    "response_format": {"type": "json_object"}
                },
                timeout=90
            )
            if r.status_code == 200:
                return json.loads(r.json()["choices"][0]["message"]["content"])
        except Exception as ex:
            print(f"  ⚠️  {ex}")
    return {}

def gerar_video_higfield(prompt_video: str, imagem_produto: str = None) -> dict:
    """Gera vídeo via Higfield API (quando conectado via MCP no Claude Desktop)"""
    if not HIGFIELD_KEY:
        return {"status": "PENDENTE — configure HIGFIELD_API_KEY no GitHub Secret"}

    url = "https://api.hixsfield.ai/v1/videos/generate"
    payload = {
        "prompt": prompt_video,
        "model": "sidence-2.0",
        "aspect_ratio": "9:16",
        "duration": 15,
        "style": "ugc_authentic"
    }
    if imagem_produto:
        payload["reference_image_url"] = imagem_produto

    r = requests.post(
        url,
        headers={"Authorization": f"Bearer {HIGFIELD_KEY}", "Content-Type": "application/json"},
        json=payload,
        timeout=180
    )
    return r.json() if r.status_code == 200 else {"error": r.text, "status": r.status_code}

def gerar_video_heygen(script: str) -> dict:
    """Alternativa: HeyGen quando Higfield não disponível"""
    if not HEYGEN_KEY:
        return {"status": "sem_heygen_key"}
    url = "https://api.heygen.com/v2/video/generate"
    r = requests.post(
        url,
        headers={"X-Api-Key": HEYGEN_KEY, "Content-Type": "application/json"},
        json={
            "video_inputs": [{
                "character": {"type": "avatar", "avatar_id": "Angela-inTshirt-20220820"},
                "voice": {"type": "text", "input_text": script[:500], "voice_id": "pt_BR_female"},
                "background": {"type": "color", "value": "#F5F5F5"}
            }],
            "dimension": {"width": 720, "height": 1280}
        },
        timeout=120
    )
    return r.json() if r.status_code == 200 else {"error": r.text}

def salvar_campanha(dados: dict):
    if not SB_KEY: return
    requests.post(
        f"{SB_URL}/rest/v1/affiliate_campaigns",
        headers={"apikey": SB_KEY, "Authorization": f"Bearer {SB_KEY}",
                 "Content-Type": "application/json", "Prefer": "return=minimal"},
        json=dados, timeout=15
    )

# ══════════════════════════════════════════════════════════════════
# WORKFLOW PRINCIPAL — replica o vídeo passo a passo
# ══════════════════════════════════════════════════════════════════
def run():
    print("\n⚡ AFFILIATE UGC ENGINE — Workflow Higfield+Claude")
    print("=" * 60)

    # PASSO 1: Pesquisar nichos (prompt exato do vídeo)
    print("\n📊 Passo 1: Pesquisando nichos lucrativos Brasil 2026...")
    resultado = chamar_llm(PROMPT_NICHOS)
    if not resultado:
        print("❌ Configure GROQ_API_KEY ou NVIDIA_API_KEY")
        return

    nichos = resultado.get("nichos", [])
    print(f"✅ {len(nichos)} nichos encontrados")
    print(f"   Veredito: {resultado.get('veredito', '')[:100]}")

    # PASSO 2: Pegar nicho #1 e encontrar produto
    nicho_top = nichos[0] if nichos else {}
    marcas = nicho_top.get("marcas_pagam_bem", ["Simplee"])
    marca_escolhida = marcas[0] if marcas else "Simplee"

    print(f"\n🎯 Nicho: {nicho_top.get('categoria','')} | Marca: {marca_escolhida}")
    print(f"   Comissão estimada: {nicho_top.get('comissao_range','')}")

    prompt_prod = PROMPT_PRODUTO_TPL.format(
        nicho=nicho_top.get("categoria",""),
        marca=marca_escolhida
    )
    print("\n🛍️  Passo 2: Encontrando produto campeão de vendas...")
    produto = chamar_llm(prompt_prod)
    print(f"✅ Produto: {produto.get('produto','?')}")
    print(f"   Comissão: {produto.get('comissao','?')}")
    print(f"   Por que viral: {produto.get('por_que_viral','?')}")

    # PASSO 3: Gerar prompt do vídeo (prompt exato do vídeo)
    hooks = produto.get("hooks_sugeridos", nicho_top.get("hooks_top", []))
    hook_escolhido = hooks[0] if hooks else "Comprei achando que era furada e esse produto fez o que o de R$200 não fez"

    prompt_video = PROMPT_VIDEO_TPL.format(
        produto=produto.get("produto",""),
        marca=produto.get("marca",""),
        hook=hook_escolhido
    )

    print(f"\n🎬 Passo 3: Gerando vídeo UGC...")
    print(f"   Hook: {hook_escolhido}")

    # Tentar Higfield → fallback HeyGen
    if HIGFIELD_KEY:
        video = gerar_video_higfield(prompt_video, produto.get("imagem_url",""))
        gerador = "Higfield Sidence 2.0"
    elif HEYGEN_KEY:
        video = gerar_video_heygen(hook_escolhido)
        gerador = "HeyGen"
    else:
        video = {"status": "Configure HIGFIELD_API_KEY ou HEYGEN_API_KEY"}
        gerador = "Pendente"

    print(f"   Gerador: {gerador}")
    print(f"   Status: {video.get('status', video.get('video_id','?'))}")

    # PASSO 4: Caption para postar
    caption = f"""{hook_escolhido} 😱

{chr(10).join(f'✅ {b}' for b in produto.get('beneficios_principais',[])[:2])}

Link na bio ⬆️ para pegar o seu!

#publi #ad #conteúdoIA #{nicho_top.get('categoria','').replace(' ','').lower()} #shopee #amazon"""

    print(f"\n📱 Passo 4: Caption pronta para postar:")
    print(caption)

    # Salvar no Supabase
    salvar_campanha({
        "nicho": nicho_top.get("categoria",""),
        "produto": produto.get("produto",""),
        "marca": produto.get("marca",""),
        "comissao": produto.get("comissao",""),
        "plataforma": (nicho_top.get("plataformas_afiliado",["Shopee"])+[""])[0],
        "hook": hook_escolhido,
        "prompt_video": prompt_video[:500],
        "video_status": "generated" if HIGFIELD_KEY or HEYGEN_KEY else "pending",
        "video_url": video.get("video_url",""),
        "data_criacao": datetime.now().isoformat()
    })

    print("\n✅ Campanha salva no Supabase")
    print("\n" + "="*60)
    print("📋 RESUMO DA CAMPANHA:")
    print(f"  Nicho: {nicho_top.get('categoria','')}")
    print(f"  Produto: {produto.get('produto','')}")
    print(f"  Preço: {produto.get('preco','')}")
    print(f"  Comissão: {produto.get('comissao','')}")
    print(f"  Publicar: TikTok + Instagram Reels + YouTube Shorts")
    print(f"  Caption: #publi #ad obrigatório (CONAR)")

if __name__ == "__main__":
    run()
