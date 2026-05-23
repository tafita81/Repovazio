#!/usr/bin/env python3
# elevenlabs_trilhas.py
# Gera trilhas psicologia narradas com ElevenLabs
# Voice: Sarah (multilingual) — 32K chars/mes gratis
# Distribui para Supabase Storage → Amuse → Spotify

import os, json, requests, time
from datetime import datetime

EL_KEY = os.getenv("ELEVENLABS_API_KEY","")
GK     = os.getenv("GROQ_API_KEY","")
SB     = os.getenv("SUPABASE_URL","https://tpjvalzwkqwttvmszvie.supabase.co")
SK     = os.getenv("SUPABASE_KEY","")

VOICE_ID = "EXAVITQu4vr4xnSDxMaL"  # Sarah — voz padrao psicologia.doc

TRILHAS_SCRIPTS = [
    {
        "titulo": "Regulação do Sistema Nervoso — Guia Prático",
        "script": "Respire fundo. Inspire por quatro segundos. Segure por quatro. Expire por seis. "
                  "Seu sistema nervoso está aprendendo que você está segura. "
                  "Essa trilha foi criada para acompanhar exercícios de regulação do sistema nervoso autônomo. "
                  "Quando o ritmo da respiração se alinha com a música, o córtex pré-frontal reconecta "
                  "com a amígdala. Você retorna ao equilíbrio. Permita-se estar aqui.",
        "tags": ["nervous-system","regulation","calm","therapy","pt-br"]
    },
    {
        "titulo": "Autocompaixão — A Voz Que Você Merece Ouvir",
        "script": "Você não precisa ser perfeita para merecer cuidado. "
                  "Kristin Neff, pesquisadora de Harvard, descobriu que a autocompaixão ativa "
                  "os mesmos circuitos neurais que a compaixão por outros — com um efeito adicional: "
                  "reduz o cortisol em até vinte e três por cento. "
                  "Esta trilha é para os momentos em que você foi dura demais consigo mesma. "
                  "Coloque a mão no coração. Sinta o calor. Você está aqui.",
        "tags": ["self-compassion","healing","self-love","pt-br","wellness"]
    },
    {
        "titulo": "Ansiedade — Retorno ao Momento Presente",
        "script": "A ansiedade vive no futuro. O presente é o único lugar onde ela não pode te alcançar. "
                  "Olhe ao seu redor. Nomeie cinco coisas que você pode ver. "
                  "Quatro que pode tocar. Três que pode ouvir. Dois cheiros. Um sabor. "
                  "Seu sistema nervoso está recalibrando. "
                  "Pesquisas de Steven Porges mostram que esse exercício ativa o nervo vago "
                  "e restaura o estado parassimpático em menos de três minutos. "
                  "Você está voltando. Você está aqui.",
        "tags": ["anxiety","mindfulness","grounding","present","pt-br"]
    }
]

def gerar_audio(texto, titulo):
    if not EL_KEY:
        print(f"  ELEVENLABS_API_KEY nao configurado")
        return None
    url = f"https://api.elevenlabs.io/v1/text-to-speech/{VOICE_ID}"
    payload = {
        "text": texto,
        "model_id": "eleven_multilingual_v2",
        "voice_settings": {"stability": 0.7, "similarity_boost": 0.8, "style": 0.4}
    }
    r = requests.post(url, headers={"xi-api-key": EL_KEY, "Content-Type": "application/json"},
                      json=payload, timeout=90)
    if r.status_code == 200:
        fname = f"/tmp/{titulo.replace(' ','_')[:30]}.mp3"
        with open(fname, "wb") as f:
            f.write(r.content)
        print(f"  Audio gerado: {fname} ({len(r.content)/1024:.0f}KB)")
        return fname
    print(f"  Erro ElevenLabs: {r.status_code} {r.text[:100]}")
    return None

def salvar_supabase(titulo, tags, audio_path):
    if not SK or not audio_path:
        return
    with open(audio_path,"rb") as f:
        audio_bytes = f.read()
    fname = f"trilhas/{titulo.replace(' ','_')[:40]}_{datetime.now().strftime('%Y%m%d')}.mp3"
    r = requests.post(
        f"{SB}/storage/v1/object/videos/{fname}",
        headers={"apikey": SK, "Authorization": f"Bearer {SK}",
                 "Content-Type": "audio/mpeg", "x-upsert": "true"},
        data=audio_bytes, timeout=60)
    if r.status_code in (200,201):
        url = f"{SB}/storage/v1/object/public/videos/{fname}"
        print(f"  Storage: {url}")
        requests.post(f"{SB}/rest/v1/content_pipeline",
            headers={"apikey":SK,"Authorization":f"Bearer {SK}","Content-Type":"application/json",
                     "Prefer":"return=minimal"},
            json={"titulo":titulo,"tipo":"trilha_audio","status":"pronto",
                  "audio_url":url,"tags":tags,"criado_em":datetime.now().isoformat()},
            timeout=10)

def run():
    print(f"ELEVENLABS TRILHAS — {datetime.now():%Y-%m-%d %H:%M}")
    r = requests.get(f"https://api.elevenlabs.io/v1/user/subscription",
                     headers={"xi-api-key": EL_KEY})
    if r.status_code == 200:
        info = r.json()
        used = info.get("character_count",0)
        limit = info.get("character_limit",32000)
        print(f"ElevenLabs: {used}/{limit} chars usados ({100*used//limit}%)")
    for t in TRILHAS_SCRIPTS:
        chars = len(t["script"])
        print(f"
{t['titulo'][:40]} ({chars} chars)")
        audio = gerar_audio(t["script"], t["titulo"])
        if audio:
            salvar_supabase(t["titulo"], t["tags"], audio)
        time.sleep(3)
    print("
Trilhas geradas. Proxima etapa: upload Amuse.io para Spotify.")

if __name__ == "__main__":
    run()
