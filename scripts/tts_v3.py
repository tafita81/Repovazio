#!/usr/bin/env python3
"""
tts_v3.py — Cerebro V3 CINEMATOGRAFICO
Voz: ElevenLabs Sarah, contemplativa, 0.88x, pausas estrategicas
Padrao: documentario psicologico cinematografico premium
"""
import os, asyncio, requests, time, subprocess, re
from supabase import create_client

SB_URL = os.environ["SUPABASE_URL"]
SB_KEY = os.environ["SUPABASE_KEY"]
sb = create_client(SB_URL, SB_KEY)
SB_ANON = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InRwanZhbHp3a3F3dHR2bXN6dmllIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NzYwMzUyOTMsImV4cCI6MjA5MTYxMTI5M30.UEgUo0Mw15ihQZykLAY5QApRzgTXkfIewZFzIgwao3Q"

EL_KEY = os.environ.get("ELEVENLABS_API_KEY","")
# Sarah — voz mais natural e controlada disponivel
# Rachel (21m00Tcm4TlvDq8ikWAM) — opcao alternativa mais grave
VOICE_ID = "EXAVITQu4vr4xnSDxMaL"  # Sarah multilingual
MODEL    = "eleven_multilingual_v2"

def adicionar_pausas_cinematograficas(script: str) -> str:
    """
    Adiciona pausas estrategicas para o estilo contemplativo.
    Baseado no padrao: 'Existe... uma razao... pela qual voce nunca consegue parar.'
    """
    texto = script
    # Pausa antes de revelacoes (apos virgula + verbo importante)
    revelacoes = [" porque", " porem", " contudo", " entretanto", " na verdade",
                  " o que", " isso significa", " isso quer dizer", " a questao",
                  " o motivo", " a razao", " o problema", " a verdade"]
    for p in revelacoes:
        texto = texto.replace(p, f"...{p}")
    # Pausa antes de numeros (sinais, razoes, formas)
    texto = re.sub(r'(\.\s+)([A-Z])', r'.

', texto)
    # Limitar ... multiplos
    texto = re.sub(r'\.{4,}', '...', texto)
    return texto

def gerar_elevenlabs(script: str, video_id: int) -> str | None:
    if not EL_KEY:
        print("    ElevenLabs key ausente"); return None
    script_com_pausas = adicionar_pausas_cinematograficas(script)
    try:
        r = requests.post(
            f"https://api.elevenlabs.io/v1/text-to-speech/{VOICE_ID}",
            headers={"xi-api-key": EL_KEY, "Content-Type": "application/json"},
            json={
                "text": script_com_pausas,
                "model_id": MODEL,
                "language_code": "pt",
                "voice_settings": {
                    "stability": 0.52,        # controle emocional alto
                    "similarity_boost": 0.80,  # fidelidade a voz
                    "style": 0.12,            # MUITO BAIXO = calma, nao entusiasmada
                    "use_speaker_boost": True
                },
                "output_format": "mp3_44100_192"
            }, timeout=180)
        print(f"    ElevenLabs: {r.status_code}")
        if r.status_code == 200:
            raw = f"/tmp/el_raw_{video_id}.mp3"
            with open(raw,"wb") as f: f.write(r.content)
            # Aplicar 0.88x para voz contemplativa (como nos canais de referencia)
            slow = f"/tmp/el_{video_id}.mp3"
            resultado = subprocess.run([
                "ffmpeg","-y","-i",raw,
                "-filter:a","atempo=0.88",
                "-codec:a","libmp3lame","-b:a","192k",
                slow
            ], capture_output=True, timeout=60)
            if resultado.returncode == 0 and os.path.exists(slow):
                print(f"    OK Sarah 0.88x: {os.path.getsize(slow):,}B")
                return slow
            else:
                print(f"    slowdown falhou, usando raw"); return raw
        try: print(f"    erro: {r.json().get('detail','')[:150]}")
        except: print(f"    erro: {r.text[:150]}")
    except Exception as e:
        print(f"    EL exc: {e}")
    return None

async def gerar_edge(script: str, video_id: int) -> str | None:
    try:
        import edge_tts
        raw = f"/tmp/edge_raw_{video_id}.mp3"
        tts = edge_tts.Communicate(script, voice="pt-BR-ThalitaMultilingualNeural", rate="-12%")
        await tts.save(raw)
        slow = f"/tmp/edge_{video_id}.mp3"
        subprocess.run([
            "ffmpeg","-y","-i",raw,
            "-filter:a","atempo=0.90",
            "-codec:a","libmp3lame","-b:a","192k",slow
        ], capture_output=True, timeout=60)
        p = slow if os.path.exists(slow) else raw
        print(f"    Edge TTS 0.90x: {os.path.getsize(p):,}B")
        return p
    except Exception as e:
        print(f"    Edge falhou: {e}"); return None

def upload_audio(path: str, video_id: int) -> str | None:
    fname = f"audios/v{video_id}_cinem.mp3"
    with open(path,"rb") as f: data = f.read()
    r = requests.post(f"{SB_URL}/storage/v1/object/videos/{fname}",
        headers={"apikey":SB_ANON,"Authorization":f"Bearer {SB_ANON}",
                 "Content-Type":"audio/mpeg","x-upsert":"true"}, data=data)
    if r.status_code in [200,201]:
        return f"{SB_URL}/storage/v1/object/public/videos/{fname}"
    print(f"    upload err: {r.status_code}"); return None

def main():
    print("=== TTS V3 CINEMATOGRAFICO — ElevenLabs 0.88x contemplativo ===")
    print(f"ElevenLabs: {'OK' if EL_KEY else 'AUSENTE fallback Edge'}")
    r = sb.table("content_pipeline").select(
        "id,title,script,duracao_min,pub_order"
    ).eq("status","mp4_ready").is_("audio_url",None).order("pub_order").limit(5).execute()
    videos = r.data or []
    print(f"Videos sem audio: {len(videos)}")
    for v in videos:
        vid_id = v["id"]
        script = (v.get("script") or "").strip()
        if not script: print(f"  #{vid_id}: sem script"); continue
        print(f"\n  #{vid_id} {v.get('title','')[:50]}")
        path = gerar_elevenlabs(script, vid_id)
        if not path: path = asyncio.run(gerar_edge(script, vid_id))
        if not path: print("    todos TTS falharam"); continue
        url = upload_audio(path, vid_id)
        if url:
            vname = f"ElevenLabs_Sarah_0.88x_{MODEL}" if "el_" in path else "Edge_Thalita_0.90x"
            sb.table("content_pipeline").update(
                {"audio_url":url,"voice_name":vname}
            ).eq("id",vid_id).execute()
            print(f"    OK audio ({vname})")

if __name__ == "__main__":
    main()
