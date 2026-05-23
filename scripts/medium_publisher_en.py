#!/usr/bin/env python3
"""medium_publisher_en.py — publica artigos EN no Medium"""
import os, requests, base64

MEDIUM_TOKEN = os.getenv("MEDIUM_TOKEN", "")
GH_PAT       = os.getenv("GH_PAT", os.getenv("GITHUB_TOKEN", ""))
REPO         = os.getenv("GITHUB_REPOSITORY", "tafita81/Repovazio")

# Bio sem título profissional até 2027
BIO_EN = "Daniela Coelho · Behavioral Research & Psychology Content · @psidanielacoelho"

ARTIGOS_EN = [
    {"file": "output/en_article_covert_narcissism.md",
     "titulo": "Covert Narcissism: 5 Signs Nobody Talks About (And Why Science Explains Them)",
     "tags": ["psychology","mental-health","narcissism","relationships","behavioral-science"]},
    {"file": "output/en_article_anxious_attachment.md",
     "titulo": "Anxious Attachment: Why We Sabotage the Relationships We Most Want",
     "tags": ["psychology","attachment","relationships","mental-health","neuroscience"]},
    {"file": "output/en_article_impostor_syndrome.md",
     "titulo": "Impostor Syndrome: Why Competent People Feel Like Frauds",
     "tags": ["psychology","career","impostor-syndrome","mental-health","self-awareness"]},
    {"file": "output/en_article_burnout.md",
     "titulo": "Burnout vs. Tiredness: The Real Differences Science Documents",
     "tags": ["burnout","mental-health","psychology","work","neuroscience"]},
    {"file": "output/en_article_boundaries.md",
     "titulo": "Emotional Boundaries: Protection vs. Isolation — What Research Shows",
     "tags": ["psychology","relationships","boundaries","mental-health","emotional-intelligence"]},
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
    if r.status_code == 200: return r.json()["data"]["id"]
    print(f"Medium auth falhou: {r.status_code}")
    return None

def publicar(user_id, titulo, content, tags):
    footer = f"\n\n---\n*{BIO_EN}*"
    r = requests.post(f"https://api.medium.com/v1/users/{user_id}/posts",
        headers={"Authorization": f"Bearer {MEDIUM_TOKEN}", "Content-Type": "application/json"},
        json={"title": titulo, "contentFormat": "markdown",
              "content": content + footer, "tags": tags[:5],
              "publishStatus": "public"}, timeout=30)
    if r.status_code in (200, 201): return r.json()["data"].get("url", "publicado")
    return f"Erro {r.status_code}: {r.text[:200]}"

def run():
    if not MEDIUM_TOKEN:
        print("MEDIUM_TOKEN ausente.")
        print("medium.com/me/settings → Integration Tokens → GitHub Secret: MEDIUM_TOKEN")
        return
    uid = get_user_id()
    if not uid: return
    
    print(f"Publicando {len(ARTIGOS_EN)} artigos EN...")
    for i, art in enumerate(ARTIGOS_EN):
        content = get_file(art["file"])
        if not content: continue
        url = publicar(uid, art["titulo"], content, art["tags"])
        ok = "medium.com" in url
        print(f"  [{i+1}] {'✅' if ok else '❌'} {art['titulo'][:55]}")
        import time; time.sleep(5)

if __name__ == "__main__":
    run()
