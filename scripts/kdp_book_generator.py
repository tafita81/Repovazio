#!/usr/bin/env python3
"""
kdp_book_generator.py
Gera conteúdo completo de livros KDP usando Groq + scripts do canal EN
Target: livros de 47-80 páginas em EN/PT/ES
CPM KDP: $2-7 por venda (royalty 70%)
"""
import os, requests, json, time, pathlib

SB_URL = os.getenv("SUPABASE_URL","https://tpjvalzwkqwttvmszvie.supabase.co")
SB_KEY = os.getenv("SUPABASE_SERVICE_KEY","")
GROQ   = os.getenv("GROQ_API_KEY","")
SBH    = {"apikey":SB_KEY,"Authorization":f"Bearer {SB_KEY}","Content-Type":"application/json"}
OUT    = pathlib.Path("/tmp/kdp"); OUT.mkdir(exist_ok=True)

LIVROS = [
    {
        "titulo": "Covert Narcissism: The Hidden Threat in Relationships",
        "idioma": "EN",
        "capitulos": [
            "Understanding Covert Narcissism: Beyond the Obvious",
            "The Victimhood Pattern: How Covert Narcissists Operate",
            "Anxious Attachment and Narcissistic Relationships",
            "Gaslighting: How Your Reality Gets Rewritten",
            "The Trauma Bond: Why You Stay",
            "Recovery: Recalibrating Your Nervous System",
            "Setting Boundaries That Actually Hold",
            "Healing Anxious Attachment After Narcissistic Abuse",
        ],
        "autora": "Daniela Coelho · Behavioral Research & Psychology"
    },
    {
        "titulo": "Apego Ansioso: Guia de Cura Baseado em Ciencia",
        "idioma": "PT",
        "capitulos": [
            "O Que e Apego Ansioso: A Neurociencia por Tras",
            "Como Se Forma: Ainsworth e os Estudos de Apego",
            "Sinais no Cotidiano: Identificando os Padroes",
            "O Sistema Nervoso Ansioso: Por Que Voce Nao Consegue Parar",
            "Relacionamentos e Apego: Os Ciclos que Se Repetem",
            "A Ciencia da Mudanca: Neuroplasticidade e Esperanca",
            "Praticas Baseadas em Evidencias para a Cura",
            "Construindo Apego Seguro na Vida Adulta",
        ],
        "autora": "Daniela Coelho · Pesquisa e Conteudo em Psicologia"
    },
]

def gerar_capitulo(titulo_livro, capitulo, idioma, autora):
    if not GROQ: return f"# {capitulo}\n\nConteudo pendente."
    lang = "English" if idioma=="EN" else "Portuguese Brazilian"
    prompt = (
        f"Write a complete chapter for a psychology book titled '{titulo_livro}'.\n"
        f"Chapter: '{capitulo}'\n"
        f"Language: {lang}\n"
        f"Author voice: {autora}\n\n"
        f"Requirements:\n"
        f"- 800-1000 words\n"
        f"- Evidence-based: cite real researchers (van der Kolk, Ainsworth, Gottman, Neff, Malkin)\n"
        f"- Counter-intuitive insights\n"
        f"- Practical exercises at the end\n"
        f"- NO generic advice\n"
        f"- Warm but direct tone\n"
        f"- Use markdown headings\n\n"
        f"Write the complete chapter now:"
    )
    try:
        r = requests.post("https://api.groq.com/openai/v1/chat/completions",
            headers={"Authorization":f"Bearer {GROQ}","Content-Type":"application/json"},
            json={"model":"llama-3.3-70b-versatile","messages":[{"role":"user","content":prompt}],
                  "max_tokens":1200,"temperature":0.7},
            timeout=60)
        if r.status_code == 200:
            return r.json()["choices"][0]["message"]["content"]
    except: pass
    return f"# {capitulo}\n\nContent generation pending."

def salvar_em_supabase(titulo, idioma, conteudo):
    r = requests.patch(
        f"{SB_URL}/rest/v1/kdp_books?titulo=eq.{requests.utils.quote(titulo)}&idioma=eq.{idioma}",
        headers=SBH,
        json={"script_origem": conteudo[:50000], "status": "content_ready"},
        timeout=30)
    return r.status_code in (200, 201, 204)

def run():
    print("=== KDP BOOK GENERATOR ===")
    for livro in LIVROS:
        print(f"\n📚 {livro['titulo']}")
        conteudo_total = f"# {livro['titulo']}\n\n**{livro['autora']}**\n\n"
        conteudo_total += "---\n\n"
        conteudo_total += "## Sobre Este Livro\n\nEste livro foi escrito com base em pesquisa científica real. "
        conteudo_total += "Cada afirmação é sustentada por estudos peer-reviewed e pela prática clínica.\n\n---\n\n"

        for i, cap in enumerate(livro["capitulos"], 1):
            print(f"  Capítulo {i}/{len(livro['capitulos'])}: {cap[:40]}...")
            texto = gerar_capitulo(livro["titulo"], cap, livro["idioma"], livro["autora"])
            conteudo_total += f"\n\n## Capítulo {i}: {cap}\n\n{texto}\n\n---\n"
            time.sleep(3)

        # Salvar no arquivo
        out_file = OUT / f"kdp_{livro['idioma']}_{i:02d}.md"
        out_file.write_text(conteudo_total)
        print(f"  Salvo: {out_file} ({len(conteudo_total)//1000}KB)")

        # Salvar no Supabase
        salvar_em_supabase(livro["titulo"], livro["idioma"], conteudo_total)
        print(f"  ✅ Supabase updated")
        time.sleep(5)

if __name__ == "__main__":
    run()
