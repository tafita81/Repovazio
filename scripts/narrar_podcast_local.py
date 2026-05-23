#!/usr/bin/env python3
"""
narrar_podcast_local.py
Narra os 8 episódios no seu Mac usando Edge TTS (gratuito, ilimitado).

USO:
  pip install edge-tts
  python3 narrar_podcast_local.py
  → MP3s gerados em ./mp3/
  → Upload no Anchor FM → Spotify automático
"""
import asyncio, edge_tts, os, re
from pathlib import Path

VOZ = "pt-BR-FranciscaNeural"   # feminina — troque por AntonioNeural para masculina
OUT  = Path("./mp3")
OUT.mkdir(exist_ok=True)

# Identidade correta — SEM título profissional até 2027
ASSINATURA = "Daniela Coelho · Pesquisa e Conteúdo em Psicologia · @psidanielacoelho"

EPISODIOS = [
    ("ep01_narcisismo_encoberto",
"""A pessoa mais narcisista que você conhece provavelmente não é aquela que fala demais de si mesma.
É aquela que parece humilde demais.
Oi, eu sou a Daniela Coelho, e hoje vamos falar sobre narcisismo encoberto — o tipo que ninguém vê.
Craig Malkin, pesquisador de Harvard, passou anos estudando esse padrão.
O narcisismo encoberto se manifesta por hipersensibilidade ao reconhecimento, não pela busca direta de atenção.
No cérebro, a amígdala dispara com mais facilidade nessas pessoas.
Qualquer percepção de não ser especial o suficiente ativa uma resposta de estresse real.
Cinco sinais que a maioria não percebe.
Primeiro: eles são sempre a maior vítima de qualquer situação.
Segundo: dão para depois cobrar — generosidade como investimento.
Terceiro: inveja disfarçada de preocupação — parece cuidado, não é.
Quarto: nunca pedem diretamente — são mestres na comunicação passiva.
Quinto: o isolamento gradual — você vai percebendo que saiu menos, falou menos com amigos.
O que fazer? Pare de confundir sensibilidade com necessidade de controle.
Reconecte com o que você quer. Observe o padrão, não o episódio.
Eu sou Daniela Coelho. Obrigada por estar aqui."""),

    ("ep02_apego_ansioso",
"""Você já ficou verificando o celular esperando uma mensagem de alguém que gosta?
Já mandou uma segunda mensagem só pra ver quando a primeira ficou sem resposta?
Isso não é fraqueza. É apego ansioso — e tem neurociência por trás.
Mary Ainsworth descobriu nos anos 60 que bebês com cuidadores inconsistentes desenvolvem um padrão específico.
Buscam conforto mas não conseguem confiar quando ele chega.
O cérebro aprende uma lição: o amor existe, mas não pode ser contado.
Daniel Siegel da UCLA mostra como esses padrões se inscrevem nas redes neurais.
A amígdala fica hiperativa para sinais de rejeição.
Uma mensagem não respondida ativa o mesmo alarme de ameaça de sobrevivência.
Cinco sinais: autossabotagem preventiva, testes invisíveis, fusão como segurança,
sensibilidade extrema a microexpressões, e ruminação interminável.
O que ajuda: nomear o padrão sem se identificar com ele.
Construir tolerância à incerteza gradualmente.
Apego ansioso não é destino. É padrão. Padrões mudam.
Eu sou Daniela Coelho."""),

    ("ep03_burnout",
"""Todo mundo diz que está no limite.
Mas burnout de verdade não é cansaço que passa com um fim de semana.
Christina Maslach, pesquisadora de Berkeley, mapeou três dimensões.
Exaustão emocional. Despersonalização — cinismo crescente. Redução da realização.
A diferença real do cansaço normal?
Com cansaço, você volta das férias recuperado. Com burnout, volta igual.
Cinco marcadores: recuperação que não acontece, cinismo crescente,
desconexão emocional, erros incomuns, e sintomas físicos sem causa clara.
Burnout não se resolve com mais força de vontade.
Foi exatamente isso que o criou.
Três passos: reconhecer que é sério, reduzir a carga agora, priorizar o sono.
Burnout é o sinal de que algo no sistema precisa mudar.
Eu sou Daniela Coelho."""),

    ("ep04_gaslighting",
"""O termo vem de um filme de 1944 — Gaslight — onde um marido faz a esposa duvidar da própria percepção.
Cinco padrões que muitas pessoas não reconhecem.
Negação de realidade: isso nunca aconteceu, você está lembrando errado.
Trivialização: você é muito sensível, está exagerando.
Desvio: quando você aborda um problema, a conversa muda de direção.
Invalidação seletiva: suas emoções são sempre as erradas.
Isolamento progressivo: semear dúvidas sobre as pessoas próximas a você.
Jennifer Freyd, da Universidade de Oregon, pesquisa o trauma de traição.
Quando a fonte do dano é também a fonte de cuidado, é difícil reconhecer o abuso.
Três passos concretos: documentar, reconectar com pessoas de confiança, buscar apoio.
Reconhecer gaslighting não é sobre culpar. É sobre ver com clareza.
Eu sou Daniela Coelho."""),

    ("ep05_depressao_sorridente",
"""A pessoa mais bem-humorada que você conhece pode estar carregando algo que ninguém vê.
Depressão sorridente, distimia mascarada, depressão funcional de alta performance.
Martin Seligman diferencia bem-estar subjetivo de funcionamento psicológico.
É possível funcionar bem enquanto o bem-estar subjetivo está comprometido.
Cinco marcadores: prazer embotado — as coisas boas acontecem mas não chegam.
Exaustão crônica desproporcional. Irritabilidade escondida.
Pensamentos de para quê. Desconexão do corpo.
O que ajuda: nomear, falar com profissional, e micro-ativações de prazer deliberadas.
A pesquisa de Lewinsohn mostra que aumentar atividades prazerosas muda o estado emocional,
mesmo antes de a motivação chegar.
Se você está bem mas não está bem — isso importa. Você importa.
Eu sou Daniela Coelho."""),

    ("ep06_fronteiras",
"""Coloca um limite virou conselho universal.
Mas fronteira emocional de verdade é muito mais sutil que a versão pop sugere.
Nedra Tawwab define: fronteiras são expectativas e necessidades que te ajudam a se sentir seguro.
São comunicação, não punição.
Como distinguir fronteira de muro?
Fronteiras têm linguagem. Muros são silêncio ou corte sem explicação.
Fronteiras são flexíveis. Muros são rígidos independente do contexto.
Fronteiras preservam relação. Muros encerram a possibilidade de conexão.
Fronteiras vêm de valores. Muros vêm de dor.
Fronteiras são comunicadas. Muros deixam as pessoas adivinhando.
Fronteiras reais não distanciam. Aproximam as pessoas certas, da forma certa.
Eu sou Daniela Coelho."""),

    ("ep07_validacao",
"""Você já postou algo e ficou verificando as curtidas nos primeiros minutos?
Isso não é fraqueza de caráter. É dopamina.
O sistema de recompensa do cérebro foi moldado pela evolução para responder a aprovação social.
Para primatas vivendo em grupos, aprovação significava inclusão. Rejeição significava morte.
David Rock documenta que ameaças ao status ativam as mesmas regiões de ameaças físicas.
Redes sociais amplificam isso: curtidas em intervalos variáveis são o esquema mais viciante que existe.
Cinco marcadores: dificuldade de decidir sem consultar, humor dependente de feedback,
dificuldade de discordar, superperformance para ser visto, releituras obsessivas.
Três coisas que ajudam: autoestima baseada em valores, não performance.
Ações sem audiência deliberadamente. Delay nos estímulos sociais.
Precisar de aprovação é humano. Depender dela é um sinal.
Eu sou Daniela Coelho."""),

    ("ep08_perfeccionismo",
"""Sou um pouco perfeccionista é uma das respostas mais usadas em entrevistas de emprego.
Como se fosse um defeito charmoso.
Mas perfeccionismo clínico não tem nada de charmoso. É ansiedade com um custo altíssimo.
Paul Hewitt e Gordon Flett distinguem três tipos.
O mais destruidor: perfeccionismo socialmente prescrito — a crença de que outros exigem perfeição de você.
Brené Brown é direta: perfeccionismo não é sobre fazer o melhor. É sobre ganhar aprovação.
Como distinguir excelência saudável de perfeccionismo patológico?
Excelência permite versão boa o suficiente. Perfeccionismo não entrega enquanto não estiver perfeito.
Excelência aprende com erros. Perfeccionismo é devastado por eles.
Excelência termina. Perfeccionismo procrastina infinitamente.
Feito é melhor que perfeito não é preguiça. É saúde.
Essa foi a primeira temporada do Mente em Foco. Oito episódios. Obrigada.
Eu sou Daniela Coelho."""),
]

async def narrar(ep, texto):
    out = OUT / f"{ep}.mp3"
    if out.exists():
        print(f"  ⏭  {ep}.mp3 já existe ({out.stat().st_size//1024}KB)")
        return
    texto_limpo = re.sub(r"\[.*?\]", " ", texto)
    texto_limpo = " ".join(texto_limpo.split())
    print(f"  🔊 {ep}...")
    communicate = edge_tts.Communicate(texto_limpo, VOZ, rate="+5%", volume="+5%")
    await communicate.save(str(out))
    kb = out.stat().st_size // 1024
    print(f"  ✅ {ep}.mp3 ({kb} KB)")

async def main():
    print(f"=== NARRAÇÃO PODCAST — Daniela Coelho\nVoz: {VOZ}\n")
    for ep, texto in EPISODIOS:
        await narrar(ep, texto)
        await asyncio.sleep(0.5)
    mp3s = list(OUT.glob("*.mp3"))
    print(f"\n✅ {len(mp3s)} MP3s prontos → upload Anchor FM → Spotify")
    print("\nPRÓXIMOS PASSOS:")
    print("1. anchor.fm → New Episode → Upload Audio")
    print("2. Título: Ep.01 — Narcisismo Encoberto: O Tipo Que Ninguém Vê")
    print("3. Publicar → distribui Spotify em 48h (gratuito)")
    print(f"\nAssinatura: {ASSINATURA}")

if __name__ == "__main__":
    asyncio.run(main())
