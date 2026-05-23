#!/usr/bin/env python3
"""newsletter_engine_en.py — newsletter semanal inglês para Substack"""
import os, json, requests, pathlib
from datetime import datetime

GROQ_KEY = os.getenv("GROQ_API_KEY", "")
BIO_EN = "Daniela Coelho · Behavioral Research & Psychology Content"

def get_paper():
    try:
        r = requests.get(
            "https://api.osf.io/v2/preprints/?provider=psyarxiv&ordering=-date_created&page[size]=5",
            timeout=10)
        if r.status_code == 200:
            items = r.json().get("data", [])
            if items:
                a = items[0].get("attributes", {})
                return {"title": a.get("title", "Recent psychology research")[:100],
                        "description": (a.get("description","") or "")[:400]}
    except: pass
    return {"title": "Emotion Regulation and Psychological Well-being", "description": "Recent research on cognitive reappraisal strategies."}

def gerar(paper):
    if not GROQ_KEY: return None
    semana = datetime.now().strftime("%B %d, %Y")
    prompt = f"""You are Daniela Coelho — a behavioral researcher and psychology content creator.
Write this week's Substack newsletter ({semana}) based on this paper:
Title: {paper['title']}
Abstract: {paper['description'][:300]}

FORMAT (markdown):
## 🧠 Mind Matters — Week of {semana}

### Research of the Week
[Summarize the paper accessibly, 150 words, cite the study]

### Concept in Focus: [central concept from the paper]
[Deep explanation, 200 words, real-world examples]

### In Practice
[3 concrete applications, 150 words total]

### To Reflect On
[1 powerful reflective question + 1 real researcher quote]

---
*Next week: [related next topic]*
*{BIO_EN}*

TONE: smart, warm, evidence-based. American English. No jargon overload."""
    
    try:
        r = requests.post("https://api.groq.com/openai/v1/chat/completions",
            headers={"Authorization": f"Bearer {GROQ_KEY}", "Content-Type": "application/json"},
            json={"model": "llama-3.3-70b-versatile",
                  "messages": [{"role": "user", "content": prompt}],
                  "max_tokens": 1200, "temperature": 0.75}, timeout=60)
        if r.status_code == 200:
            return r.json()["choices"][0]["message"]["content"]
    except Exception as e:
        print(f"Groq: {e}")
    return None

def run():
    print(f"=== NEWSLETTER EN — {datetime.now():%Y-%m-%d} ===")
    paper = get_paper()
    print(f"  Paper: {paper['title'][:60]}")
    newsletter = gerar(paper)
    if newsletter:
        out = pathlib.Path(os.getenv("GITHUB_WORKSPACE",".")) / "output" / "newsletter"
        out.mkdir(parents=True, exist_ok=True)
        f = out / f"newsletter_en_{datetime.now():%Y_W%V}.md"
        with open(f, "w") as fp: fp.write(newsletter)
        print(f"  Salva: {f.name}")
        print("  → copiar no Substack (EN) → publicar")
    else:
        print("  Groq indisponível neste ambiente")

if __name__ == "__main__":
    run()
