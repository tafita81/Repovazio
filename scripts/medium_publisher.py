#!/usr/bin/env python3
# medium_publisher.py
# Publica artigos no Medium via API oficial
# Medium tem API limitada — requer integration token do usuario
# Pegar token em: medium.com/me/settings > Integration Tokens

import os, json, requests

MEDIUM_TOKEN = os.getenv("MEDIUM_TOKEN", "")

def get_user_id():
    r = requests.get("https://api.medium.com/v1/me",
        headers={"Authorization": f"Bearer {MEDIUM_TOKEN}", "Content-Type": "application/json"})
    if r.status_code == 200:
        return r.json()["data"]["id"]
    print(f"Erro Medium API: {r.status_code} {r.text}")
    return None

def publish_article(titulo, conteudo, tags):
    uid = get_user_id()
    if not uid:
        return None
    payload = {
        "title": titulo,
        "contentFormat": "markdown",
        "content": conteudo,
        "tags": tags[:5],
        "publishStatus": "public"
    }
    r = requests.post(f"https://api.medium.com/v1/users/{uid}/posts",
        headers={"Authorization": f"Bearer {MEDIUM_TOKEN}", "Content-Type": "application/json"},
        json=payload)
    if r.status_code == 201:
        url = r.json()["data"]["url"]
        print(f"Publicado: {url}")
        return url
    print(f"Erro: {r.status_code} {r.text}")
    return None

# Artigos prontos para publicar
ARTIGOS = [
    {
        "titulo": "Narcisismo Encoberto: O Que a Neurociência Revela Sobre a Manipulação Invisível",
        "arquivo": "output/medium_article_narcisismo_encoberto.md",
        "tags": ["psychology", "narcissism", "mental health", "relationships", "neuroscience"]
    },
    {
        "titulo": "Apego Ansioso: Por Que Você Sempre Sente Que Vai Perder Quem Ama",
        "arquivo": "output/medium_article_apego_ansioso.md",
        "tags": ["psychology", "attachment", "anxiety", "relationships", "neuroscience"]
    },
    {
        "titulo": "O Que Acontece no Cérebro de Quem Tem Transtorno de Ansiedade",
        "arquivo": "output/medium_article_neurociencia_ansiedade.md",
        "tags": ["anxiety", "neuroscience", "psychology", "brain", "mental health"]
    },
    {
        "titulo": "Síndrome do Impostor: Por Que Pessoas Competentes Se Sentem Fraudes",
        "arquivo": "output/medium_article_impostor.md",
        "tags": ["impostor syndrome", "psychology", "career", "self-esteem", "mental health"]
    },
    {
        "titulo": "Trauma de Desenvolvimento: Quando a Infância Deixa Marcas que a Memória Não Alcança",
        "arquivo": "output/medium_article_trauma_desenvolvimento.md",
        "tags": ["trauma", "childhood", "neuroscience", "psychology", "healing"]
    }
]

def run():
    if not MEDIUM_TOKEN:
        print("MEDIUM_TOKEN nao configurado")
        print("Pegar em: medium.com/me/settings > Integration Tokens")
        return
    for art in ARTIGOS:
        try:
            with open(art["arquivo"]) as f:
                conteudo = f.read()
            url = publish_article(art["titulo"], conteudo, art["tags"])
            if url:
                print(f"OK: {art['titulo'][:40]}")
        except Exception as e:
            print(f"Erro {art['arquivo']}: {e}")

if __name__ == "__main__":
    run()
