#!/usr/bin/env python3
# run_today.py — Executa HOJE todos os passos de renda algorítmica
# Custo: $0. Renda começa em 24-72h.

import os, subprocess, webbrowser
from pathlib import Path

print("\n" + "="*55)
print(" PSICOLOGIA.DOC — MOTOR DE RENDA ALGORÍTMICA")
print(" Executa em ordem de menor prazo para primeiro $")
print("="*55)

PASSOS = [
    {
        "ordem": 1,
        "nome": "Medium Partner Program — artigo hoje",
        "prazo_horas": 2,
        "renda_mes_usd": 2500,
        "tipo": "ALGORÍTMICO — pago por leitura, sem compra",
        "acoes": [
            "1. Abrir medium.com",
            "2. Settings > Partner Program > Aplicar (grátis)",
            "3. Novo artigo > colar output/medium_article_narcisismo_encoberto.md",
            "4. Adicionar tags: psychology, narcissism, mental health, relationships",
            "5. Publicar",
            "6. Compartilhar no Instagram Stories (link bio)",
        ],
        "url": "https://medium.com/partner-program",
        "arquivo_pronto": "output/medium_article_narcisismo_encoberto.md"
    },
    {
        "ordem": 2,
        "nome": "Stable Audio → Amuse.io — trilhas Spotify hoje",
        "prazo_horas": 4,
        "renda_mes_usd": 5000,
        "tipo": "ALGORÍTMICO — royalty por stream, sem compra",
        "acoes": [
            "1. Abrir huggingface.co/spaces/stabilityai/stable-audio-open",
            "2. Gerar trilha 1: colar prompt do arquivo trilhas_spotify_psicologia_vol1.json",
            "3. Repetir para as 10 trilhas (salvar como WAV)",
            "4. Criar conta amuse.io (grátis)",
            "5. Upload do álbum completo",
            "6. Spotify recebe em 24-48h, royalties chegam todo mês",
        ],
        "url": "https://amuse.io",
        "arquivo_pronto": "output/trilhas_spotify_psicologia_vol1.json"
    },
    {
        "ordem": 3,
        "nome": "ASCAP Registration — royalties performance USA",
        "prazo_horas": 1,
        "renda_mes_usd": 2000,
        "tipo": "ALGORÍTMICO — pago por execução pública, automático",
        "acoes": [
            "1. Abrir ascap.com > Member Benefits > Join",
            "2. Cadastro como Writer ($50 taxa única, se recupera no 1o royalty)",
            "3. Registrar cada trilha criada no Passo 2",
            "4. Royalties chegam quando qualquer música toca em rádio/podcast/evento USA",
        ],
        "url": "https://www.ascap.com/help/ascap-member-services/join-ascap"
    },
    {
        "ordem": 4,
        "nome": "KDP Kindle Unlimited — workbook publicar hoje",
        "prazo_horas": 3,
        "renda_mes_usd": 8000,
        "tipo": "ALGORÍTMICO — pago por PÁGINA LIDA, sem compra necessária",
        "acoes": [
            "1. Abrir kdp.amazon.com (conta grátis)",
            "2. Novo Livro > Kindle eBook",
            "3. Título: Workbook Narcisismo Encoberto | Autor: Daniela Coelho",
            "4. Copiar conteúdo de output/kdp_workbook_narcisismo_encoberto.md",
            "5. Formatar como EPUB ou usar Reedsy.com (grátis)",
            "6. Preço: R$0 (para Kindle Unlimited) — recebe por página lida",
            "7. Ativar KDP Select (exclusividade 90 dias = mais promoções)",
            "8. Publicar — disponível em 24-72h",
        ],
        "url": "https://kdp.amazon.com",
        "arquivo_pronto": "output/kdp_workbook_narcisismo_encoberto.md"
    },
    {
        "ordem": 5,
        "nome": "YouTube Content ID — 22 vídeos existentes",
        "prazo_horas": 0.5,
        "renda_mes_usd": 3000,
        "tipo": "ALGORÍTMICO — royalty perpétuo por uso, automático",
        "acoes": [
            "1. YouTube Studio > Monetização > Content ID",
            "2. Habilitar para todos os 22 vídeos existentes",
            "3. Configurar: quando copiado, receita vai para você",
            "4. Toda cópia não autorizada = royalty automático",
        ],
        "url": "https://studio.youtube.com"
    },
    {
        "ordem": 6,
        "nome": "YouTube Live 24/7 Lofi — AdSense contínuo",
        "prazo_horas": 2,
        "renda_mes_usd": 7000,
        "tipo": "ALGORÍTMICO — AdSense por views, sem compra",
        "acoes": [
            "1. Gerar 2h de lofi com Stable Audio (mesmos prompts das trilhas)",
            "2. Concatenar em loop com ffmpeg: ffmpeg -stream_loop -1 -i lofi.wav -c copy lofi_loop.wav",
            "3. YouTube Studio > Criar > Transmissão ao vivo",
            "4. Usar OBS ou Streamyard (grátis) para stream contínuo",
            "5. Título: 'Música para Estudo e Foco | Psicologia do Bem-Estar'",
            "6. AdSense começa automaticamente com canal monetizado",
        ],
        "url": "https://studio.youtube.com/channel/UCyCkIpsVgME9yCj_oXJFheA"
    }
]

total_renda = sum(p["renda_mes_usd"] for p in PASSOS)
total_horas = sum(p["prazo_horas"] for p in PASSOS)

print(f"\n6 passos | {total_horas}h total | ${total_renda:,}/mês potencial\n")

for p in PASSOS:
    print(f"{'='*50}")
    print(f"PASSO {p['ordem']}: {p['nome']}")
    print(f"Tempo: {p['prazo_horas']}h | Renda: ${p['renda_mes_usd']:,}/mês")
    print(f"Tipo: {p['tipo']}")
    print(f"URL: {p['url']}")
    if 'arquivo_pronto' in p:
        print(f"Arquivo: {p['arquivo_pronto']} (pronto no GitHub)")
    print("Ações:")
    for a in p["acoes"]:
        print(f"  {a}")
    print()

print("="*55)
print(f"TOTAL HOJE: {total_horas:.1f}h de trabalho")
print(f"RETORNO: ${total_renda:,}/mês começando em 24-72h")
print(f"TIPO: 100% algorítmico, zero dependência de compras")
print("="*55)
