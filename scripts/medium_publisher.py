#!/usr/bin/env python3
"""medium_publisher.py — 12 artigos PT no Medium"""
import os, requests, base64, time

MEDIUM_TOKEN = os.getenv("MEDIUM_TOKEN", "")
GH_PAT = os.getenv("GH_PAT", os.getenv("GITHUB_TOKEN", ""))
REPO  = os.getenv("GITHUB_REPOSITORY", "tafita81/Repovazio")
BIO   = "Daniela Coelho · Pesquisa e Conteúdo em Psicologia · @psidanielacoelho"

ARTIGOS = [
    {"file":"output/medium_article_narcisismo_encoberto.md","titulo":"Narcisismo Encoberto: 5 Sinais Que Ninguém Percebe","tags":["psicologia","narcisismo","relacoes","saude-mental","autoconhecimento"]},
    {"file":"output/medium_article_apego_ansioso.md","titulo":"Apego Ansioso: Por Que Sabotamos o Que Mais Queremos","tags":["psicologia","apego","relacoes","saude-mental","comportamento"]},
    {"file":"output/medium_article_neurociencia_ansiedade.md","titulo":"Neurociência da Ansiedade: O Que Acontece no Seu Cérebro","tags":["neurociencia","ansiedade","psicologia","cerebro","saude-mental"]},
    {"file":"output/medium_article_impostor.md","titulo":"Síndrome do Impostor: Por Que Competentes Se Sentem Fraudes","tags":["psicologia","carreira","autoconhecimento","saude-mental","performance"]},
    {"file":"output/medium_article_trauma_desenvolvimento.md","titulo":"Trauma de Desenvolvimento: Como a Infância Molda o Adulto","tags":["trauma","psicologia","infancia","saude-mental","relacoes"]},
    {"file":"output/medium_article_gaslighting.md","titulo":"Gaslighting: Como Identificar Quando a Realidade Parece Escorregadia","tags":["psicologia","gaslighting","relacoes","saude-mental","trauma"]},
    {"file":"output/medium_article_validacao.md","titulo":"Vício em Validação: Por Que Precisamos de Aprovação o Tempo Todo","tags":["psicologia","redes-sociais","autoestima","saude-mental","comportamento"]},
    {"file":"output/medium_article_critica.md","titulo":"Por Que Críticas Doem Tanto","tags":["psicologia","neurociencia","feedback","saude-mental","autoconhecimento"]},
    {"file":"output/medium_article_amigos.md","titulo":"Por Que É Tão Difícil Fazer Amigos na Vida Adulta","tags":["psicologia","amizade","solidao","relacoes","saude-mental"]},
    {"file":"output/medium_article_amor_proprio.md","titulo":"Amor Próprio Não É O Que as Redes Sociais Vendem","tags":["psicologia","autocompaixao","saude-mental","autoestima","comportamento"]},
    {"file":"output/medium_article_raiva.md","titulo":"Raiva Não É O Problema — O Que Você Faz Com Ela É","tags":["psicologia","emocoes","raiva","saude-mental","neurociencia"]},
    {"file":"output/medium_article_procrastinacao.md","titulo":"Procrastinação Não É Preguiça — É Regulação Emocional","tags":["psicologia","procrastinacao","produtividade","saude-mental","comportamento"]},
]

def get_file(path):
    if not GH_PAT: return None
    r = requests.get(f"https://api.github.com/repos/{REPO}/contents/{path}",
        headers={"Authorization": f"token {GH_PAT}"}, timeout=15)
    return base64.b64decode(r.json()["content"]).decode() if r.status_code == 200 else None

def uid():
    r = requests.get("https://api.medium.com/v1/me",
        headers={"Authorization": f"Bearer {MEDIUM_TOKEN}"}, timeout=10)
    return r.json()["data"]["id"] if r.status_code == 200 else None

def publicar(user_id, titulo, content, tags):
    r = requests.post(f"https://api.medium.com/v1/users/{user_id}/posts",
        headers={"Authorization": f"Bearer {MEDIUM_TOKEN}", "Content-Type": "application/json"},
        json={"title": titulo, "contentFormat": "markdown",
              "content": content + f"\n\n---\n*{BIO}*",
              "tags": tags[:5], "publishStatus": "public"}, timeout=30)
    return r.json().get("data", {}).get("url", f"Erro {r.status_code}") if r.status_code in (200,201) else f"Erro {r.status_code}"

def run():
    if not MEDIUM_TOKEN:
        print("Adicione MEDIUM_TOKEN nas GitHub Secrets")
        print("medium.com/me/settings → Integration Tokens → criar token")
        return
    user_id = uid()
    if not user_id: return
    for i, art in enumerate(ARTIGOS):
        content = get_file(art["file"])
        if not content: print(f"[{i+1}] ❌ arquivo não encontrado"); continue
        url = publicar(user_id, art["titulo"], content, art["tags"])
        ok = "medium.com" in url
        print(f"[{i+1}] {'✅' if ok else '❌'} {art['titulo'][:55]}")
        time.sleep(5)

if __name__ == "__main__":
    run()
