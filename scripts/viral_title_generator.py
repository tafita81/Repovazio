#!/usr/bin/env python3
"""
viral_title_generator.py
Gera títulos virais otimizados para cada idioma usando Groq.
Atualiza banco de títulos no Supabase toda semana.
"""
import os, requests, time

GROQ = os.getenv("GROQ_API_KEY","")
SB_URL = os.getenv("SUPABASE_URL","https://tpjvalzwkqwttvmszvie.supabase.co")
SB_KEY = os.getenv("SUPABASE_SERVICE_KEY","")
SBH = {"apikey":SB_KEY,"Authorization":f"Bearer {SB_KEY}","Content-Type":"application/json"}

IDIOMAS = {
    "EN": ("English","$25-50 CPM USA/UK/AU","528hz sleep anxiety narcissism gaslighting trauma"),
    "PT": ("Portuguese Brazilian","$5-12 CPM Brasil","528hz dormir ansiedade narcisismo gaslighting trauma"),
    "ES": ("Spanish","$8-15 CPM México/España","528hz dormir ansiedad narcisismo gaslighting trauma"),
    "DE": ("German","$15-25 CPM Deutschland","528hz schlaf angst narzissmus gaslighting trauma"),
    "FR": ("French","$12-20 CPM France","528hz sommeil anxiété narcissisme gaslighting trauma"),
    "JA": ("Japanese","$12-18 CPM Japan","528hz 睡眠 不安 ナルシシズム ガスライティング トラウマ"),
    "KO": ("Korean","$10-15 CPM Korea","528hz 수면 불안 나르시시즘 가스라이팅 트라우마"),
    "IT": ("Italian","$10-15 CPM Italy","528hz sonno ansia narcisismo gaslighting trauma"),
    "ZH": ("Chinese","$8-12 CPM","528hz 睡眠 焦虑 自恋 煤气灯 创伤"),
}

def gerar_titulos(idioma_code, lang, cpm, keywords):
    if not GROQ: return []
    prompt = (
        f"Generate 10 viral YouTube titles in {lang} for a psychology channel.\n"
        f"Topics: {keywords}\n"
        f"Rules:\n"
        f"- Start with number, 'Why', 'The', or 'How'\n"
        f"- Counter-intuitive insight\n"
        f"- Max 70 characters\n"
        f"- High CTR potential\n"
        f"Return JSON array: [\"title1\",\"title2\",...]\n"
        f"Only JSON, no other text."
    )
    try:
        r = requests.post("https://api.groq.com/openai/v1/chat/completions",
            headers={"Authorization":f"Bearer {GROQ}","Content-Type":"application/json"},
            json={"model":"llama-3.3-70b-versatile",
                  "messages":[{"role":"user","content":prompt}],
                  "max_tokens":400,"temperature":0.9},
            timeout=30)
        if r.status_code == 200:
            import json
            text = r.json()["choices"][0]["message"]["content"]
            text = text[text.find("["):text.rfind("]")+1]
            return json.loads(text)
    except: pass
    return []

def salvar_supabase(idioma, titulos):
    for t in titulos:
        requests.post(f"{SB_URL}/rest/v1/youtube_title_variants",
            headers=SBH,
            json={"idioma":idioma,"titulo":t,"ctr_estimado":0,"status":"pending"},
            timeout=10)

def run():
    print("=== VIRAL TITLE GENERATOR ===")
    for code, (lang, cpm, kw) in IDIOMAS.items():
        print(f"  [{code}] {lang}...")
        titulos = gerar_titulos(code, lang, cpm, kw)
        if titulos:
            salvar_supabase(code, titulos)
            print(f"    ✅ {len(titulos)} títulos → Supabase")
            for t in titulos[:3]:
                print(f"      → {t[:60]}")
        time.sleep(3)

if __name__ == "__main__":
    run()
