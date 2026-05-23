#!/usr/bin/env python3
"""medium_publisher.py — publica os 5 artigos no Medium via API"""
import os, json, requests, base64

MEDIUM_TOKEN = os.getenv("MEDIUM_TOKEN", "")
GH_PAT       = os.getenv("GH_PAT", os.getenv("GITHUB_TOKEN", ""))
REPO         = os.getenv("GITHUB_REPOSITORY", "tafita81/Repovazio")

ARTIGOS = [
    {"file": "output/medium_article_narcisismo_encoberto.md",
     "titulo": "Narcisismo Encoberto: 5 Sinais Que Ninguém Percebe (e a Ciência Explica Por Quê)",
     "tags": ["psicologia","saude-mental","narcisismo","relacoes","autoconhecimento"]},
    {"file": "output/medium_article_apego_ansioso.md",
     "titulo": "Apego Ansioso: Por Que Sabotamos os Relacionamentos Que Mais Queremos",
     "tags": ["psicologia","apego","relacoes","saude-mental","comportamento"]},
    {"file": "output/medium_article_neurociencia_ansiedade.md",
     "titulo": "Neurociência da Ansiedade: O Que Acontece no Seu Cérebro (e Por Que Isso Muda Tudo)",
     "tags": ["neurociencia","ansiedade","psicologia","cerebro","saude-mental"]},
    {"file": "output/medium_article_impostor.md",
     "titulo": "Síndrome do Impostor: Por Que Pessoas Competentes Se Sentem Fraudes",
     "tags": ["psicologia","carreira","autoconhecimento","saude-mental","performance"]},
    {"file": "output/medium_article_trauma_desenvolvimento.md",
     "titulo": "Trauma de Desenvolvimento: Como a Infância Molda o Adulto Que Você É",
     "tags": ["trauma","psicologia","infancia","saude-mental","relacoes"]},
]

def get_file(path):
    if not GH_PAT: return None
    r = requests.get(f"https://api.github.com/repos/{REPO}/contents/{path}",
        headers={"Authorization": f"token {GH_PAT}"}, timeout=15)
    if r.status_code == 200:
        return base64.b64decode(r.json()["content"]).decode("utf-8")
    return None

def get_user_id():
    r = requests.get("https://api.medium.com/v1/me",
        headers={"Authorization": f"Bearer {MEDIUM_TOKEN}"}, timeout=10)
    if r.status_code == 200:
        return r.json()["data"]["id"]
    print(f"Medium auth falhou: {r.status_code}")
    return None

def publicar(user_id, titulo, content, tags):
    r = requests.post(f"https://api.medium.com/v1/users/{user_id}/posts",
        headers={"Authorization": f"Bearer {MEDIUM_TOKEN}",
                 "Content-Type": "application/json"},
        json={"title": titulo, "contentFormat": "markdown",
              "content": content, "tags": tags[:5],
              "publishStatus": "public"}, timeout=30)
    if r.status_code in (200, 201):
        return r.json()["data"].get("url", "publicado")
    return f"Erro {r.status_code}: {r.text[:200]}"

def run():
    if not MEDIUM_TOKEN:
        print("MEDIUM_TOKEN ausente.")
        print("Ação: medium.com/me/settings → Integration Tokens → gerar")
        print("Depois: GitHub → Settings → Secrets → MEDIUM_TOKEN")
        return
    
    uid = get_user_id()
    if not uid: return
    
    print(f"Publicando {len(ARTIGOS)} artigos no Medium...")
    resultados = []
    
    for i, art in enumerate(ARTIGOS):
        print(f"  [{i+1}/{len(ARTIGOS)}] {art['titulo'][:55]}")
        content = get_file(art["file"])
        if not content:
            print(f"       ❌ Arquivo não encontrado")
            continue
        url = publicar(uid, art["titulo"], content, art["tags"])
        ok = "medium.com" in url
        print(f"       {'✅' if ok else '❌'} {url[:70]}")
        resultados.append({"titulo": art["titulo"][:50], "url": url, "ok": ok})
        import time; time.sleep(5)
    
    ok_count = sum(1 for r in resultados if r["ok"])
    print(f"\nPublicados: {ok_count}/{len(ARTIGOS)}")

if __name__ == "__main__":
    run()
