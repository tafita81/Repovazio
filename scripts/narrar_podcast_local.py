#!/usr/bin/env python3
"""
narrar_podcast_local.py
Narra os 8 episódios do podcast no SEU computador (Mac/Linux)
usando Edge TTS (gratuito, ilimitado, voz Microsoft).

COMO USAR:
  1. pip install edge-tts
  2. python3 narrar_podcast_local.py
  3. MP3s gerados na pasta ./mp3/
  4. Upload no Anchor FM -> Spotify grátis
"""
import asyncio, edge_tts, os, re
from pathlib import Path

VOZ = "pt-BR-FranciscaNeural"   # voz feminina natural — troque por AntonioNeural se preferir masculina
OUT  = Path("./mp3")
OUT.mkdir(exist_ok=True)

ROTEIROS = [
    ("ep01_narcisismo_encoberto",
     """A pessoa mais narcisista que você conhece provavelmente não é aquela que fala demais de si mesma.
     É aquela que parece humilde demais.
     Oi, eu sou a Daniela Coelho, e hoje vamos falar sobre narcisismo encoberto — o tipo que ninguém vê.
     Craig Malkin, de Harvard, passou anos estudando esse padrão.
     O narcisismo encoberto se manifesta por hipersensibilidade ao reconhecimento, não pela busca direta de atenção.
     No cérebro, a amígdala dispara com mais facilidade nessas pessoas.
     Qualquer percepção de não ser especial o suficiente ativa uma resposta de estresse real.
     Cinco sinais que a maioria não percebe: eles são sempre a maior vítima de qualquer situação.
     Eles dão para depois cobrar. Inveja disfarçada de preocupação.
     Nunca pedem diretamente — são mestres na comunicação passiva.
     E o isolamento gradual — você vai percebendo que saiu menos, falou menos com seus amigos.
     O que fazer? Pare de confundir sensibilidade com controle.
     Reconecte com o que você quer. Observe o padrão, não o episódio isolado.
     Eu sou Daniela Coelho. Obrigada por estar aqui."""),
    
    ("ep02_apego_ansioso",
     """Você já ficou verificando o celular esperando uma mensagem de alguém que gosta?
     Já mandou uma segunda mensagem só pra ver quando a primeira ficou sem resposta?
     Isso não é fraqueza. É apego ansioso — e tem neurociência por trás.
     Mary Ainsworth, nos anos 60, descobriu que bebês com cuidadores inconsistentes desenvolvem
     um padrão muito específico: buscam conforto mas não conseguem confiar quando ele chega.
     O cérebro aprende que o amor existe, mas não pode ser contado.
     Cinco sinais: autossabotagem preventiva, testes invisíveis para ver se o outro fica,
     fusão como segurança, sensibilidade extrema a expressões faciais, e ruminação interminável.
     O que ajuda: nomear o padrão sem se identificar com ele.
     Construir tolerância à incerteza gradualmente.
     E terapia com abordagem de apego — EFT de Sue Johnson tem as melhores evidências.
     Apego ansioso não é destino. É padrão. E padrões podem mudar.
     Eu sou Daniela Coelho."""),
]

async def narrar(episodio, texto, voz=VOZ):
    out = OUT / f"{episodio}.mp3"
    if out.exists():
        print(f"  ⏭  {episodio}.mp3 já existe")
        return
    
    # Limpar texto
    texto_limpo = re.sub(r'\[.*?\]', ' ', texto)  # remove [pausa] etc
    texto_limpo = ' '.join(texto_limpo.split())       # normaliza espaços
    
    print(f"  🔊 Narrando {episodio}...")
    communicate = edge_tts.Communicate(texto_limpo, voz, rate="+5%", volume="+5%")
    await communicate.save(str(out))
    size_kb = out.stat().st_size // 1024
    print(f"  ✅ {out.name} ({size_kb} KB)")

async def main():
    print(f"=== NARRAÇÃO PODCAST — {len(ROTEIROS)} episódios ===")
    print(f"Voz: {VOZ}")
    print(f"Saída: {OUT.resolve()}\n")
    
    for ep, texto in ROTEIROS:
        await narrar(ep, texto)
        await asyncio.sleep(1)
    
    mp3s = list(OUT.glob("*.mp3"))
    print(f"\n✅ {len(mp3s)} arquivos MP3 prontos para Anchor FM!")
    print("\nPRÓXIMOS PASSOS:")
    print("1. anchor.fm → New Episode → Upload Audio")
    print("2. Título: Ep.01 — [tema]")
    print("3. Publicar → distribui Spotify automaticamente (48h)")

if __name__ == "__main__":
    asyncio.run(main())
