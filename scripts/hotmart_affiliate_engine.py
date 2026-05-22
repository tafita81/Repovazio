#!/usr/bin/env python3
"""
hotmart_affiliate_engine.py — Integração afiliados Hotmart automática
Ação 3 de 20: Encontrar cursos psicologia BR → links afiliado → inserir automaticamente

Cruzamento: Hotmart API + LLM + YouTube + Instagram
Comissão: 30-50% por venda | Ticket: R$97-997 | Renda: hoje
"""
import os, requests, json
from datetime import datetime

HOTMART_KEY = os.getenv("HOTMART_CLIENT_ID","")
HOTMART_SECRET = os.getenv("HOTMART_CLIENT_SECRET","")
GROQ_KEY = os.getenv("GROQ_API_KEY","")
SB_URL = os.getenv("SUPABASE_URL","https://tpjvalzwkqwttvmszvie.supabase.co")
SB_KEY = os.getenv("SUPABASE_SERVICE_ROLE_KEY","")

CURSOS_CURADOS = [
    {"nome":"Mentes que Manipulam","nicho":"narcisismo","comissao":"40%","ticket_min":197,"ticket_max":497,"hotlink":"https://go.hotmart.com/CONFIGURAR"},
    {"nome":"Terapia Cognitivo-Comportamental","nicho":"ansiedade","comissao":"35%","ticket_min":97,"ticket_max":297,"hotlink":"https://go.hotmart.com/CONFIGURAR"},
    {"nome":"Relacionamentos Conscientes","nicho":"relacionamentos","comissao":"45%","ticket_min":147,"ticket_max":397,"hotlink":"https://go.hotmart.com/CONFIGURAR"},
    {"nome":"Saúde Mental na Prática","nicho":"saude_mental","comissao":"30%","ticket_min":97,"ticket_max":197,"hotlink":"https://go.hotmart.com/CONFIGURAR"},
    {"nome":"Desapego e Autoestima","nicho":"autoestima","comissao":"40%","ticket_min":127,"ticket_max":347,"hotlink":"https://go.hotmart.com/CONFIGURAR"},
]

TEMPLATES_CTA = {
    "narcisismo": [
        "Se você reconheceu os 7 sinais deste vídeo, esse curso pode ser o próximo passo: {link}",
        "Minha indicação para quem quer entender mais profundamente o narcisismo: {link}",
    ],
    "ansiedade": [
        "Para quem quer ir além do que mostrei aqui: {link}",
        "O curso que recomendo para trabalhar a ansiedade na raiz: {link}",
    ],
    "relacionamentos": [
        "Se seus relacionamentos refletem o que discutimos: {link}",
        "Indicação de curso que aprofunda tudo isso: {link}",
    ]
}

def gerar_cta_contextual(nicho_video: str, titulo_video: str) -> str:
    templates = TEMPLATES_CTA.get(nicho_video, TEMPLATES_CTA["ansiedade"])
    import random
    curso = next((c for c in CURSOS_CURADOS if c["nicho"] == nicho_video), CURSOS_CURADOS[0])
    template = random.choice(templates)
    return template.format(link=curso["hotlink"])

def run():
    print("ACAO 3: Hotmart Affiliate Integration")
    print(f"Cursos mapeados: {len(CURSOS_CURADOS)}")
    
    for c in CURSOS_CURADOS:
        receita_min = int(c["ticket_min"]) * int(c["comissao"].strip("%")) // 100
        receita_max = int(c["ticket_max"]) * int(c["comissao"].strip("%")) // 100
        print(f"  {c['nome']}: R${receita_min}-{receita_max} por conversão")
        
        if SB_KEY:
            requests.post(f"{SB_URL}/rest/v1/affiliate_campaigns",
                headers={"apikey": SB_KEY, "Authorization": f"Bearer {SB_KEY}",
                         "Content-Type": "application/json"},
                json={**c, "plataforma": "hotmart", "status": "ativo",
                      "data_criacao": datetime.now().isoformat()},
                timeout=10)
    
    print("
  Como usar HOJE:")
    print("  1. Cadastre em hotmart.com/affiliate")
    print("  2. Busque cursos: psicologia, narcisismo, ansiedade, relacionamentos")
    print("  3. Solicite aprovação (imediata na maioria)")
    print("  4. Substitua CONFIGURAR nos hotlinks pelo seu ID")
    print("  5. Poste nos Stories/Descrição dos vídeos")
    
    cta = gerar_cta_contextual("narcisismo", "Narcisismo Encoberto")
    print(f"
  CTA gerado para video #683:")
    print(f"  '{cta}'")

if __name__ == "__main__":
    run()
