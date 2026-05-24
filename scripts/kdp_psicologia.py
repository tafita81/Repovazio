#!/usr/bin/env python3
"""
kdp_psicologia.py — Livro Amazon KDP auto-gerado (Groq + Pollinations)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
ESTRATÉGIA:
  Gera livros de psicologia populares para Amazon KDP (royalty 70%)
  Tema sempre relacionado ao canal: narcisismo, apego, sono, burnout
  Preço: R$9,90–R$19,90 Kindle / R$29,90–R$59,90 impresso
  Volume: 80–120 páginas (aceito no KDP)

FLUXO:
  1. Groq gera estrutura do livro (capítulos, conteúdo)
  2. Pollinations gera capa (1600x2560)
  3. Script formata em DOCX pronto para KDP
  4. Salva no Supabase fila de publicação

TEMAS VIRAIS CONFIRMADOS:
  - Narcisista Encoberto: Guia de Sobrevivência (>50K cópias niche)
  - Apego Ansioso: Como Libertar (>30K)
  - Por Que Acordo Às 3h: Ciência do Sono (novo)
  - Burnout Invisível: Antes do Colapso (>25K)
"""
import os, requests, json, time, pathlib
import urllib3; urllib3.disable_warnings()

SB_URL = os.getenv("SUPABASE_URL","https://tpjvalzwkqwttvmszvie.supabase.co")
SB_KEY = os.getenv("SUPABASE_SERVICE_KEY","")
GROQ   = os.getenv("GROQ_API_KEY","")
SBH    = {"apikey":SB_KEY,"Authorization":f"Bearer {SB_KEY}",
          "Content-Type":"application/json","Prefer":"return=minimal"}
TMP    = pathlib.Path("/tmp/kdp"); TMP.mkdir(exist_ok=True)

LIVROS_PIPELINE = [
    {
        "titulo":    "Narcisista Encoberto: O Guia de Sobrevivência",
        "subtitulo": "Como Identificar, Escapar e Curar Após o Abuso Encoberto",
        "tema":      "narcissism",
        "autor":     "Daniela Coelho",
        "preco_ebook": 9.90,
        "preco_fisico": 39.90,
        "paginas":   100,
        "capitulos": [
            "O Narcisista Que Você Não Viu Chegar",
            "O Gaslighting e Por Que Você Duvida de Você Mesmo",
            "Os 7 Sinais de Abuso Encoberto",
            "O Ciclo de Idealizacão, Desvalorização e Descarte",
            "Por Que Você Ficou: Neurociência do Trauma Bond",
            "O Processo de Cura: Da Dor à Autonomia",
            "Construindo Limites Saudáveis",
            "Amando Novamente Após o Narcisismo",
        ],
    },
    {
        "titulo":    "Apego Ansioso: Como Libertar",
        "subtitulo": "Entendendo Seus Padrões de Relacionamento e Construindo Conexões Seguras",
        "tema":      "attachment",
        "autor":     "Daniela Coelho",
        "preco_ebook": 9.90,
        "preco_fisico": 34.90,
        "paginas":   90,
        "capitulos": [
            "Ainsworth e a Teoria do Apego",
            "Os 4 Estilos de Apego Explicados",
            "Sinais de Apego Ansioso no Cotidiano",
            "Por Que Escolhemos Parceiros Indisponíveis",
            "A Neurociência da Regulação Emocional",
            "Construindo Segurança Interna",
            "O Caminho para o Apego Seguro",
        ],
    },
    {
        "titulo":    "Por Que Acordo Às 3h da Manhã",
        "subtitulo": "A Ciência do Sono, Cortisol e Trauma — e Como Dormir Profundamente de Novo",
        "tema":      "sleep",
        "autor":     "Daniela Coelho",
        "preco_ebook": 9.90,
        "preco_fisico": 34.90,
        "paginas":   85,
        "capitulos": [
            "A Biologia do Sono: Walker e a Revolução do REM",
            "Cortisol: O Hormônio Que Rouba Seu Descanso",
            "Acordar Às 3h: O Que Seu Corpo Está Tentando Dizer",
            "Trauma e Sono: A Conexão Ignorada",
            "Binaural 528Hz: A Ciência Por Trás do Áudio",
            "O Protocolo de 21 Dias Para Dormir Melhor",
            "Sono e Saúde Mental: Conexão Definitiva",
        ],
    },
]

def groq_gerar_capitulo(livro, capitulo, num):
    if not GROQ: return f"# {capitulo}\n\nConteúdo do capítulo {num}.\n\n"
    prompt = (
        f"Escreva o capítulo '{capitulo}' do livro '{livro['titulo']}'\n"
        f"Autor: {livro['autor']} — pesquisadora de comportamento humano\n"
        f"Tom: científico mas acessível. Citar pesquisadores reais (Harvard, PubMed, UCLA)\n"
        f"PROIBIDO: psicóloga/psicólogo. Usar: pesquisadora de comportamento humano\n"
        f"Tamanho: ~600 palavras. Parágrafos de 3-4 linhas.\n"
        f"Retorne o conteúdo formatado em Markdown. Começe com ## {capitulo}"
    )
    try:
        r = requests.post("https://api.groq.com/openai/v1/chat/completions",
            headers={"Authorization":f"Bearer {GROQ}","Content-Type":"application/json"},
            json={"model":"llama-3.3-70b-versatile",
                  "messages":[{"role":"user","content":prompt}],
                  "max_tokens":800,"temperature":0.75},
            timeout=25, verify=False)
        if r.status_code == 200:
            return r.json()["choices"][0]["message"]["content"].strip()
    except: pass
    return f"## {capitulo}\n\nConteúdo baseado em pesquisa científica atual.\n\n"

def gerar_capa_url(livro):
    prompt = (
        f"masterpiece, book cover art, dark psychology, "
        f"kawaii chibi anime woman researcher, dramatic lighting, "
        f"dark background #06060F, purple and red glow, "
        f"professional book cover, no text ### text, watermark, nsfw, blurry"
    )
    seed = hash(livro["titulo"]) % 90000 + 9001
    return f"https://image.pollinations.ai/prompt/{requests.utils.quote(prompt)}?seed={seed}&width=1600&height=2560&nologo=true"

def salvar_fila(livro, conteudo_path):
    if not SB_KEY: return
    requests.post(f"{SB_URL}/rest/v1/social_posts",
        headers={**SBH,"Prefer":"return=minimal"},
        json={"plataforma":"amazon_kdp","tema":livro["tema"],
              "hook":livro["titulo"],"legenda":livro["subtitulo"][:200],
              "status":"pending"},
        timeout=8, verify=False)

def run():
    print("=== KDP PSICOLOGIA — Livros Amazon Auto-gen ===\n")
    for livro in LIVROS_PIPELINE[:1]:  # 1 livro por run para não travar
        print(f"  📚 Gerando: {livro['titulo']}")
        print(f"     R${livro['preco_ebook']} Kindle | R${livro['preco_fisico']} Físico")
        linhas = [f"# {livro['titulo']}\n_{livro['subtitulo']}_\n\n**Autora:** {livro['autor']}\n\n---\n\n"]
        for i, cap in enumerate(livro["capitulos"], 1):
            print(f"     Cap {i}: {cap[:40]}...", end="\r")
            conteudo = groq_gerar_capitulo(livro, cap, i)
            linhas.append(conteudo + "\n\n---\n\n")
            time.sleep(1.5)
        md_path = TMP / f"kdp_{livro['tema']}.md"
        md_path.write_text("\n".join(linhas), encoding="utf-8")
        capa_url = gerar_capa_url(livro)
        salvar_fila(livro, str(md_path))
        print(f"\n  ✅ Livro gerado: {md_path.name} ({md_path.stat().st_size//1024}KB)")
        print(f"  🖼️  Capa: {capa_url[:70]}...")
        print(f"  📈 Royalty 70%: R${livro['preco_ebook']*0.7:.2f}/venda Kindle")
    print(f"\n  Próximo passo: enviar para kdp.amazon.com")

if __name__=="__main__": run()
