#!/usr/bin/env python3
# elevenlabs_trilhas.py  (REESCRITO 2026-05: agora 100% GRATIS via Microsoft Edge TTS)
# Gera trilhas de psicologia narradas. Custo: $0. Chars: ilimitado. Zero credito pago.
# Voz padrao: pt-BR-FranciscaNeural (calma). Alt: pt-BR-AntonioNeural / pt-BR-ThalitaMultilingualNeural
# Distribui para Supabase Storage -> (manual) Amuse.io -> Spotify
import os, asyncio, subprocess, sys
from datetime import datetime

SB    = os.getenv("SUPABASE_URL", "https://tpjvalzwkqwttvmszvie.supabase.co")
SK    = os.getenv("SUPABASE_KEY", "") or os.getenv("SUPABASE_SERVICE_KEY", "")
VOICE = os.getenv("TRILHA_VOICE", "pt-BR-FranciscaNeural")
RATE  = os.getenv("TRILHA_RATE", "-8%")   # ritmo calmo p/ relaxamento

TRILHAS_SCRIPTS = [
    {
        "titulo": "Regulacao do Sistema Nervoso - Guia Pratico",
        "script": "Respire fundo. Inspire por quatro segundos. Segure por quatro. Expire por seis. "
                  "Seu sistema nervoso esta aprendendo que voce esta segura. "
                  "Esta trilha foi criada para acompanhar exercicios de regulacao do sistema nervoso autonomo. "
                  "Quando o ritmo da respiracao se alinha com a musica, o cortex pre-frontal reconecta "
                  "com a amigdala. Voce retorna ao equilibrio. Permita-se estar aqui.",
        "tags": ["nervous-system", "regulation", "calm", "therapy", "pt-br"]
    },
    {
        "titulo": "Autocompaixao - A Voz Que Voce Merece Ouvir",
        "script": "Voce nao precisa ser perfeita para merecer cuidado. "
                  "Kristin Neff, pesquisadora de Harvard, descobriu que a autocompaixao ativa "
                  "os mesmos circuitos neurais que a compaixao por outros, com um efeito adicional: "
                  "reduz o cortisol em ate vinte e tres por cento. "
                  "Esta trilha e para os momentos em que voce foi dura demais consigo mesma. "
                  "Coloque a mao no coracao. Sinta o calor. Voce esta aqui.",
        "tags": ["self-compassion", "healing", "self-love", "pt-br", "wellness"]
    },
    {
        "titulo": "Ansiedade - Retorno ao Momento Presente",
        "script": "A ansiedade vive no futuro. O presente e o unico lugar onde ela nao pode te alcancar. "
                  "Olhe ao seu redor. Nomeie cinco coisas que voce pode ver. "
                  "Quatro que pode tocar. Tres que pode ouvir. Dois cheiros. Um sabor. "
                  "Seu sistema nervoso esta recalibrando. "
                  "Pesquisas de Steven Porges mostram que esse exercicio ativa o nervo vago "
                  "e restaura o estado parassimpatico em menos de tres minutos. "
                  "Voce esta voltando. Voce esta aqui.",
        "tags": ["anxiety", "mindfulness", "grounding", "present", "pt-br"]
    }
]

def _ensure_edge_tts():
    try:
        import edge_tts  # noqa: F401
        return True
    except ImportError:
        subprocess.run([sys.executable, "-m", "pip", "install", "--quiet", "edge-tts"], check=False)
        try:
            import edge_tts  # noqa: F401
            return True
        except ImportError:
            return False

def gerar_audio(texto, titulo):
    if not _ensure_edge_tts():
        print("  edge-tts indisponivel (pip falhou)")
        return None
    import edge_tts
    fname = "/tmp/" + titulo.replace(" ", "_")[:30] + ".mp3"
    async def _go():
        await edge_tts.Communicate(texto, VOICE, rate=RATE).save(fname)
    try:
        asyncio.run(_go())
    except Exception as e:
        print("  Erro Edge TTS: " + str(e))
        return None
    if os.path.exists(fname) and os.path.getsize(fname) > 0:
        print("  Audio gerado (Edge TTS gratis): " + fname + " (" + str(os.path.getsize(fname) // 1024) + "KB)")
        return fname
    print("  Falha: arquivo vazio")
    return None

def salvar_supabase(titulo, tags, audio_path):
    if not SK or not audio_path:
        print("  (Storage pulado: sem SUPABASE_KEY)")
        return
    import requests
    with open(audio_path, "rb") as f:
        audio_bytes = f.read()
    fname = "trilhas/" + titulo.replace(" ", "_")[:40] + "_" + datetime.now().strftime("%Y%m%d") + ".mp3"
    r = requests.post(
        SB + "/storage/v1/object/videos/" + fname,
        headers={"apikey": SK, "Authorization": "Bearer " + SK,
                 "Content-Type": "audio/mpeg", "x-upsert": "true"},
        data=audio_bytes, timeout=60)
    if r.status_code in (200, 201):
        url = SB + "/storage/v1/object/public/videos/" + fname
        print("  Storage: " + url)
        requests.post(SB + "/rest/v1/content_pipeline",
            headers={"apikey": SK, "Authorization": "Bearer " + SK,
                     "Content-Type": "application/json", "Prefer": "return=minimal"},
            json={"titulo": titulo, "tipo": "trilha_audio", "status": "pronto",
                  "audio_url": url, "tags": tags, "criado_em": datetime.now().isoformat()},
            timeout=10)
    else:
        print("  Erro Storage: " + str(r.status_code) + " " + r.text[:100])

def run():
    print("TRILHAS (Edge TTS GRATIS) - " + datetime.now().strftime("%Y-%m-%d %H:%M"))
    print("Voz: " + VOICE + " | custo: $0 | chars: ilimitado")
    for t in TRILHAS_SCRIPTS:
        print("\n" + t["titulo"][:40] + " (" + str(len(t["script"])) + " chars)")
        audio = gerar_audio(t["script"], t["titulo"])
        if audio:
            salvar_supabase(t["titulo"], t["tags"], audio)
    print("\nTrilhas geradas (custo zero). Proxima etapa: upload Amuse.io para Spotify.")

if __name__ == "__main__":
    run()
