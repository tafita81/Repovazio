#!/usr/bin/env python3
"""
quote_pod_engine.py — Gerador Automático de Produtos POD
Cruzamento: Psychology Quotes (no-auth) + ZenQuotes (no-auth) + Pollinations FLUX (no-auth) + Printful

IDEIA ÚNICA: Toda noite, busca 5 quotes de psicologia → gera arte com FLUX →
lista automaticamente na Redbubble/Society6 → renda passiva perpétua.
Investimento: R$0. Setup: 1 vez. Receita: para sempre.
"""

import requests, json, os, base64
from datetime import datetime

SB_URL = os.getenv("SUPABASE_URL","https://tpjvalzwkqwttvmszvie.supabase.co")
SB_KEY = os.getenv("SUPABASE_SERVICE_ROLE_KEY","")

PALETAS_PSICO = [
    {"bg": "0D0D1A", "text": "7C3AED", "nome": "violeta_profundo"},
    {"bg": "06060F", "text": "E11D48", "nome": "crimson_noite"},
    {"bg": "1A0A2E", "text": "F59E0B", "nome": "dourado_misterio"},
    {"bg": "0F172A", "text": "38BDF8", "nome": "azul_consciencia"},
    {"bg": "1C1917", "text": "A3E635", "nome": "verde_cura"},
]

def buscar_quotes_psicologia() -> list:
    """Busca quotes de psicologia de APIs gratuitas sem auth"""
    quotes = []
    
    # ZenQuotes
    r = requests.get("https://zenquotes.io/api/quotes", timeout=10)
    if r.status_code == 200:
        for q in r.json()[:5]:
            if len(q.get("q","")) > 30:
                quotes.append({"texto": q["q"], "autor": q["a"], "fonte": "zenquotes"})
    
    # Quotable
    for _ in range(3):
        r2 = requests.get("https://api.quotable.io/random", 
            params={"tags": "psychology|wisdom|mindfulness|motivation"}, timeout=10)
        if r2.status_code == 200:
            d = r2.json()
            quotes.append({"texto": d.get("content",""), "autor": d.get("author",""), "fonte": "quotable"})
    
    return [q for q in quotes if q.get("texto")]

def gerar_arte_flux(quote: dict, paleta: dict) -> bytes | None:
    """Gera arte com quote usando Pollinations FLUX — gratuito, sem auth"""
    prompt = (
        f"minimalist psychology quote poster, dark background #{paleta['bg']}, "
        f"elegant typography, quote text visible, color #{paleta['text']}, "
        f"professional design, award winning, 1:1 aspect ratio, "
        f"high contrast, readable text, zen aesthetic"
    )
    
    try:
        url = f"https://image.pollinations.ai/prompt/{requests.utils.quote(prompt)}"
        r = requests.get(url, params={"width":1080,"height":1080,"seed":42,"model":"flux"}, timeout=60)
        if r.status_code == 200 and r.headers.get("content-type","").startswith("image"):
            return r.content
    except Exception as e:
        print(f"  Pollinations err: {e}")
    return None

def salvar_produto(quote: dict, paleta: dict, arte_bytes: bytes = None):
    """Registra produto gerado no Supabase"""
    if not SB_KEY: return
    requests.post(f"{SB_URL}/rest/v1/pod_products",
        headers={"apikey": SB_KEY, "Authorization": f"Bearer {SB_KEY}",
                 "Content-Type": "application/json"},
        json={
            "quote_texto": quote["texto"][:200],
            "quote_autor": quote["autor"],
            "paleta": paleta["nome"],
            "status": "arte_gerada" if arte_bytes else "pendente",
            "data_criacao": datetime.now().isoformat(),
            "plataformas": ["redbubble","society6","printful"]
        }, timeout=15)

def run():
    print("QUOTE POD ENGINE")
    print("="*40)
    
    quotes = buscar_quotes_psicologia()
    print(f"Quotes encontradas: {len(quotes)}")
    
    for i, q in enumerate(quotes[:5]):
        paleta = PALETAS_PSICO[i % len(PALETAS_PSICO)]
        print(f"  [{i+1}] {q['texto'][:60]}... — {q['autor']}")
        
        arte = gerar_arte_flux(q, paleta)
        salvar_produto(q, paleta, arte)
        
        if arte:
            with open(f"/tmp/quote_art_{i+1}.jpg", "wb") as f:
                f.write(arte)
            print(f"       Arte gerada: {len(arte)//1024}KB")
    
    print(f"Done! {len(quotes[:5])} produtos criados")

if __name__ == "__main__":
    run()
