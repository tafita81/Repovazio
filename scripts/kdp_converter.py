#!/usr/bin/env python3
"""
kdp_converter.py — Converte workbook markdown para PDF/EPUB para KDP Amazon
Publica como ebook Kindle Direct Publishing
Renda: royalties 35-70% por venda, globalmente, em 48h
"""
import os, subprocess, requests, base64
from pathlib import Path

GH_PAT = os.getenv("GH_PAT", "")
REPO = os.getenv("GITHUB_REPOSITORY", "tafita81/Repovazio")

LIVROS_KDP = [
    {
        "arquivo": "output/kdp_workbook_narcisismo_encoberto.md",
        "titulo": "Narcisismo Encoberto: Guia Prático de Reconhecimento e Proteção",
        "autor": "Daniela Coelho",
        "preco_usd": 6.99,
        "categorias": ["Self-Help / Abuse", "Psychology / Personality"],
        "keywords": ["narcissism", "covert narcissism", "toxic relationships", "psychology", "emotional healing"],
    }
]

def get_workbook_github(arquivo):
    if not GH_PAT: return None
    r = requests.get(f"https://api.github.com/repos/{REPO}/contents/{arquivo}",
        headers={"Authorization": f"token {GH_PAT}"}, timeout=15)
    if r.status_code == 200:
        return base64.b64decode(r.json()["content"]).decode("utf-8")
    return None

def md_para_pdf(conteudo_md, titulo, autor, output_path):
    """Converte markdown para PDF profissional via Pandoc + LaTeX"""
    md_file = "/tmp/workbook_temp.md"
    with open(md_file, "w", encoding="utf-8") as f:
        f.write(f"---\ntitle: {titulo}\nauthor: {autor}\ndate: {__import__('datetime').date.today()}\n---\n\n")
        f.write(conteudo_md)
    
    # Tentar pandoc (se disponível)
    try:
        result = subprocess.run([
            "pandoc", md_file, "-o", output_path,
            "--pdf-engine=xelatex",
            f"--metadata=title:{titulo}",
            f"--metadata=author:{autor}",
            "-V", "geometry:margin=1in",
            "-V", "fontsize=12pt",
        ], capture_output=True, timeout=120)
        if result.returncode == 0:
            return True, "pandoc"
    except FileNotFoundError:
        pass
    
    # Fallback: reportlab
    try:
        from reportlab.lib.pagesizes import A4
        from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
        from reportlab.lib.styles import getSampleStyleSheet
        
        doc = SimpleDocTemplate(output_path, pagesize=A4)
        styles = getSampleStyleSheet()
        story = []
        
        story.append(Paragraph(titulo, styles["Title"]))
        story.append(Paragraph(f"por {autor}", styles["Normal"]))
        story.append(Spacer(1, 20))
        
        for linha in conteudo_md.split("\n"):
            if linha.startswith("# "):
                story.append(Paragraph(linha[2:], styles["Heading1"]))
            elif linha.startswith("## "):
                story.append(Paragraph(linha[3:], styles["Heading2"]))
            elif linha.strip():
                story.append(Paragraph(linha.replace("**", "<b>").replace("*", "<i>"), styles["Normal"]))
            else:
                story.append(Spacer(1, 8))
        
        doc.build(story)
        return True, "reportlab"
    except Exception as e:
        return False, str(e)

def run():
    print(f"=== KDP CONVERTER ===")
    out_dir = Path(os.getenv("GITHUB_WORKSPACE", ".")) / "output" / "kdp"
    out_dir.mkdir(parents=True, exist_ok=True)
    
    for livro in LIVROS_KDP:
        print(f"Processando: {livro['titulo'][:50]}")
        
        conteudo = get_workbook_github(livro["arquivo"])
        if not conteudo:
            print(f"  Arquivo não encontrado: {livro['arquivo']}")
            continue
        
        pdf_path = str(out_dir / f"{livro['titulo'].replace(' ','_')[:40]}.pdf")
        ok, engine = md_para_pdf(conteudo, livro["titulo"], livro["autor"], pdf_path)
        
        if ok:
            print(f"  ✅ PDF gerado ({engine}): {pdf_path}")
        else:
            print(f"  ❌ Falha: {engine}")
        
        print(f"\n=== PUBLICAR NO KDP AMAZON ===")
        print(f"1. kdp.amazon.com → Paperback/Ebook → Add new title")
        print(f"2. Título: {livro['titulo']}")
        print(f"3. Autor: {livro['autor']}")
        print(f"4. Categorias: {', '.join(livro['categorias'])}")
        print(f"5. Keywords: {', '.join(livro['keywords'])}")
        print(f"6. Preço: ${livro['preco_usd']} USD → royalties 70% = ${livro['preco_usd']*0.7:.2f}/venda")
        print(f"7. Upload PDF → Publish → Live em 24-72h")

if __name__ == "__main__":
    run()
