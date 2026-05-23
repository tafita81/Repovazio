#!/usr/bin/env python3
"""
medium_publisher.py — publica artigos no Medium via API
Token: medium.com/me/settings → Integration Tokens (2 min)
"""
import os, json, requests

MEDIUM_TOKEN = os.getenv("MEDIUM_TOKEN", "")
REPO = os.getenv("GITHUB_REPOSITORY", "tafita81/Repovazio")
GH_PAT = os.getenv("GH_PAT", "")

ARTIGOS = [
    {"file": "output/medium_article_narcisismo_encoberto.md",
     "titulo": "Narcisismo Encoberto: 5 Sinais Que Ninguém Percebe (e a Ciência Explica Por Quê)",
     "tags": ["psicologia", "relações", "saúde mental", "autoconhecimento", "narcisismo"]},
    {"file": "output/medium_article_impostor.md",
     "titulo": "Síndrome do Impostor: O Que Harvard Descobriu Sobre a Autodúvida",
     "tags": ["psicologia", "carreira", "saúde mental", "autoconhecimento"]},
    {"file": "output/medium_article_trauma_desenvolvimento.md",
     "titulo": "Trauma de Desenvolvimento: Como Experiências da Infância Moldam o Adulto",
     "tags": ["trauma", "psicologia", "infância", "saúde mental", "relações"]},
]

def get_file_github(path):
    import base64
    if not GH_PAT: return None
    r = requests.get(f"https://api.github.com/repos/{REPO}/contents/{path}",
        headers={"Authorization": f"token {GH_PAT}"}, timeout=15)
    if r.status_code == 200:
        return base64.b64decode(r.json()["content"]).decode("utf-8")
    return None

def get_user_id():
    r = requests.get("https://api.medium.com/v1/me",
        headers={"Authorization": f"Bearer {MEDIUM_TOKEN}"}, timeout=10)
    return r.json()["data"]["id"] if r.status_code == 200 else None

def publicar(user_id, titulo, conteudo, tags):
    r = requests.post(f"https://api.medium.com/v1/users/{user_id}/posts",
        headers={"Authorization": f"Bearer {MEDIUM_TOKEN}", "Content-Type": "application/json"},
        json={"title": titulo, "contentFormat": "markdown",
              "content": conteudo, "tags": tags, "publishStatus": "public"},
        timeout=30)
    if r.status_code in (200, 201):
        d = r.json()["data"]
        return d.get("url", "publicado")
    return f"Erro {r.status_code}: {r.text[:200]}"

def run():
    if not MEDIUM_TOKEN:
        print("MEDIUM_TOKEN não configurado!")
        print("Ação: medium.com/me/settings → Integration Tokens → gerar token")
        print("Depois: Adicionar como GitHub Secret MEDIUM_TOKEN")
        return
    
    user_id = get_user_id()
    if not user_id:
        print("Erro ao autenticar no Medium")
        return
    
    print(f"Publicando {len(ARTIGOS)} artigos...")
    for i, art in enumerate(ARTIGOS):
        content = get_file_github(art["file"])
        if not content:
            print(f"  Arquivo não encontrado: {art['file']}")
            continue
        
        url = publicar(user_id, art["titulo"], content, art["tags"])
        print(f"  [{i+1}] {'✅' if 'medium.com' in url else '❌'} {art['titulo'][:50]}")
        print(f"       {url}")
        import time; time.sleep(3)

if __name__ == "__main__":
    run()
