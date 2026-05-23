#!/usr/bin/env python3
"""
trilhas_spotify_uploader.py
Prepara trilhas de psicologia para distribuição Spotify via Amuse.io (gratuito)
Mantém 100% dos royalties no plano básico.
"""
import os, json, time, requests
from pathlib import Path

GH_PAT = os.getenv("GH_PAT", "")
GROQ_KEY = os.getenv("GROQ_API_KEY", "")

ALBUM_INFO = {
    "nome": "Mente em Paz — Trilhas de Psicologia Vol.1",
    "artista": "Daniela Coelho",
    "genero": "Ambient / New Age",
    "data_lancamento": "2025-06-01",
    "total_faixas": 10,
}

TRILHAS = [
    {"numero": 1, "nome": "Regulação Emocional", "descricao": "Ambient para meditação e terapia", "duracao": "3:42"},
    {"numero": 2, "nome": "Apego Seguro", "descricao": "Piano suave para reflexão", "duracao": "4:15"},
    {"numero": 3, "nome": "Fronteiras Saudáveis", "descricao": "Sons da natureza + ambient", "duracao": "3:58"},
    {"numero": 4, "nome": "Trauma e Cura", "descricao": "Instrumental terapêutico profundo", "duracao": "5:22"},
    {"numero": 5, "nome": "Autocompaixão", "descricao": "Meditação guiada musical", "duracao": "4:01"},
    {"numero": 6, "nome": "Ansiedade Dissolve", "descricao": "Frequências de calma 432Hz", "duracao": "6:10"},
    {"numero": 7, "nome": "Presença Plena", "descricao": "Mindfulness com chuva", "duracao": "4:33"},
    {"numero": 8, "nome": "Narcisismo — Libertação", "descricao": "Processo de cura emocional", "duracao": "3:47"},
    {"numero": 9, "nome": "Vínculos Saudáveis", "descricao": "Conexão e confiança", "duracao": "4:19"},
    {"numero": 10, "nome": "Renascimento", "descricao": "Síntese e esperança", "duracao": "5:05"},
]

def gerar_trilha_suno_prompt(trilha):
    """Gera prompt para Suno AI criar a trilha (Suno tem tier gratuito)"""
    return {
        "faixa": trilha["numero"],
        "nome": trilha["nome"],
        "suno_prompt": f"ambient meditation music, psychology therapy background, {trilha['descricao']}, no lyrics, peaceful, healing frequencies, 432hz tuning, professional studio quality",
        "udio_prompt": f"therapeutic ambient music for mental health, {trilha['descricao']}, instrumental only, calm and healing, for psychology practice",
    }

def run():
    print(f"=== TRILHAS SPOTIFY — {ALBUM_INFO['nome']} ===")
    out_dir = Path(os.getenv("GITHUB_WORKSPACE", ".")) / "output" / "trilhas"
    out_dir.mkdir(parents=True, exist_ok=True)
    
    # Gerar guia completo
    guia = {
        "album": ALBUM_INFO,
        "trilhas": [],
        "instrucoes_amuse": [
            "1. Acesse: amuse.io e crie conta gratuita",
            "2. New Release → Album",
            f"3. Nome: {ALBUM_INFO['nome']}",
            f"4. Artista: {ALBUM_INFO['artista']}",
            f"5. Gênero: {ALBUM_INFO['genero']}",
            "6. Upload cada faixa MP3 (mínimo 1:30, máximo 10min)",
            "7. Cover art: 3000x3000px JPG mínimo",
            "8. Distribuir: Spotify, Apple Music, Deezer (todos grátis no Amuse)",
            "9. Review: 7-14 dias → disponível em todas as plataformas",
            "10. Royalties: Amuse repassa 100% no plano básico",
        ],
        "instrucoes_suno": [
            "1. Acesse: suno.com (criar conta gratuita)",
            "2. Para cada faixa, use o 'suno_prompt' abaixo",
            "3. Gerar → Download MP3",
            "4. Renomear conforme número da faixa",
        ],
    }
    
    for t in TRILHAS:
        entry = {**t, "prompts": gerar_trilha_suno_prompt(t)}
        guia["trilhas"].append(entry)
        print(f"  Faixa {t['numero']:02d}: {t['nome']} ({t['duracao']}) — {t['descricao']}")
    
    out_json = out_dir / "trilhas_guia_completo.json"
    with open(out_json, "w", encoding="utf-8") as f:
        json.dump(guia, f, ensure_ascii=False, indent=2)
    print(f"\n  Guia salvo: {out_json}")
    
    # Estimar royalties
    streams_mes_conservador = 1000
    royalty_por_stream = 0.003  # média Spotify
    receita_mes = streams_mes_conservador * royalty_por_stream
    print(f"\n  Estimativa conservadora: {streams_mes_conservador} streams/mês × ${royalty_por_stream} = ${receita_mes:.0f}/mês")
    print(f"  Com 10K streams: ${10000*royalty_por_stream:.0f}/mês")

if __name__ == "__main__":
    run()
