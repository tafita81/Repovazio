#!/usr/bin/env python3
"""
TTS Pipeline V1 - Edge TTS Microsoft 100% gratis
Voz: pt-BR-FranciscaNeural (warm, narrative, default eterno)
Stack: Edge TTS + Supabase Storage + Postgres
Custo: $0.00 por audio
"""
import os, sys, json, asyncio, urllib.request, urllib.parse, time, re
from pathlib import Path

SBU = os.environ.get("SUPABASE_URL", "https://tpjvalzwkqwttvmszvie.supabase.co")
SBK = os.environ.get("SUPABASE_SERVICE_KEY") or os.environ.get("SUPABASE_KEY")

if not SBK:
    print("ERRO: SUPABASE_SERVICE_KEY nao configurado")
    sys.exit(1)

try:
    import edge_tts
except ImportError:
    print("Instalando edge_tts...")
    os.system(f"{sys.executable} -m pip install edge-tts --quiet")
    import edge_tts

# Vozes pt-BR por emocao (default eterno PT-BR)
VOZES_PT_BR = {
    "melancolico":   "pt-BR-FranciscaNeural",
    "tenso":         "pt-BR-AntonioNeural",
    "urgente":       "pt-BR-AntonioNeural",
    "contemplativo": "pt-BR-FranciscaNeural",
    "calmo":         "pt-BR-FranciscaNeural",
    "default":       "pt-BR-FranciscaNeural"
}

def sb_request(method, path, body=None, params=None, headers_extra=None):
    url = f"{SBU}/rest/v1{path}"
    if params:
        url += "?" + urllib.parse.urlencode(params)
    headers = {
        "apikey": SBK,
        "Authorization": f"Bearer {SBK}",
        "Content-Type": "application/json",
        "Prefer": "return=representation"
    }
    if headers_extra:
        headers.update(headers_extra)
    data = json.dumps(body).encode() if body else None
    req = urllib.request.Request(url, data=data, method=method, headers=headers)
    try:
        with urllib.request.urlopen(req, timeout=30) as r:
            text = r.read().decode()
            return json.loads(text) if text else None
    except urllib.error.HTTPError as e:
        print(f"  SB HTTP {e.code}: {e.read().decode()[:200]}")
        return None
    except Exception as e:
        print(f"  SB ERR: {e}")
        return None

def upload_storage(bucket, path, file_bytes):
    """Upload do MP3 para Supabase Storage"""
    url = f"{SBU}/storage/v1/object/{bucket}/{path}"
    req = urllib.request.Request(
        url,
        data=file_bytes,
        method="POST",
        headers={
            "apikey": SBK,
            "Authorization": f"Bearer {SBK}",
            "Content-Type": "audio/mpeg",
            "x-upsert": "true"
        }
    )
    try:
        with urllib.request.urlopen(req, timeout=60) as r:
            r.read()
            public_url = f"{SBU}/storage/v1/object/public/{bucket}/{path}"
            return public_url
    except urllib.error.HTTPError as e:
        # Tentar PUT se POST falhar (arquivo ja existe)
        if e.code in (400, 409):
            req2 = urllib.request.Request(
                url, data=file_bytes, method="PUT",
                headers={
                    "apikey": SBK,
                    "Authorization": f"Bearer {SBK}",
                    "Content-Type": "audio/mpeg"
                }
            )
            try:
                with urllib.request.urlopen(req2, timeout=60) as r:
                    r.read()
                    return f"{SBU}/storage/v1/object/public/{bucket}/{path}"
            except Exception as e2:
                print(f"  Upload PUT err: {e2}")
        else:
            print(f"  Upload HTTP {e.code}: {e.read().decode()[:200]}")
    except Exception as e:
        print(f"  Upload ERR: {e}")
    return None

async def gerar_audio_edge_tts(texto, voz, output_path):
    """Edge TTS Microsoft - 100% gratis"""
    try:
        # Limpar texto: remover caracteres especiais que confundem TTS
        texto_limpo = re.sub(r'[*_#`]', '', texto)
        texto_limpo = texto_limpo.replace('\n\n\n', '\n\n')
        
        communicate = edge_tts.Communicate(texto_limpo, voz, rate="-5%", pitch="+0Hz")
        await communicate.save(output_path)
        return True
    except Exception as e:
        print(f"  Edge TTS error: {e}")
        return False

async def processar_video(video):
    vid = video["id"]
    title = video.get("title", "")
    script = video.get("script", "")
    meta = video.get("metadata") or {}
    emocao = meta.get("emocao", "default")
    voz = VOZES_PT_BR.get(emocao, VOZES_PT_BR["default"])
    
    print(f"\n#{vid}: {title[:55]}")
    print(f"  emocao={emocao} | voz={voz} | script={len(script)} chars")
    
    if len(script) < 100:
        print(f"  ✗ Script muito curto")
        return False
    
    # Gerar audio
    output_path = f"/tmp/audio_{vid}.mp3"
    print(f"  Gerando audio com Edge TTS (PT-BR, default eterno)...")
    ok = await gerar_audio_edge_tts(script, voz, output_path)
    if not ok or not os.path.exists(output_path):
        print(f"  ✗ Falha gerar audio")
        return False
    
    file_size = os.path.getsize(output_path)
    print(f"  ✓ Audio gerado: {file_size/1024:.1f} KB")
    
    # Upload Supabase Storage
    with open(output_path, "rb") as f:
        audio_bytes = f.read()
    
    storage_path = f"audios/v{vid}.mp3"
    print(f"  Fazendo upload para Supabase Storage...")
    audio_url = upload_storage("videos", storage_path, audio_bytes)
    
    if not audio_url:
        print(f"  ✗ Falha upload")
        return False
    
    print(f"  ✓ Upload OK: {audio_url}")
    
    # Atualizar Supabase
    update_data = {
        "status": "audio_ready",
        "metadata": {
            **meta,
            "audio_url": audio_url,
            "audio_voz": voz,
            "audio_tamanho_bytes": file_size,
            "tts_provider": "edge_tts_microsoft",
            "tts_custo": "$0.00",
            "audio_gerado_em": time.strftime("%Y-%m-%dT%H:%M:%SZ"),
            "stack_gratuita_audio": True
        }
    }
    
    r = sb_request("PATCH", "/content_pipeline", body=update_data,
                   params={"id": f"eq.{vid}"})
    if r is not None:
        print(f"  ✓ #{vid} marcado como audio_ready")
        # Cleanup
        try: os.remove(output_path)
        except: pass
        return True
    else:
        print(f"  ✗ Falha update Supabase")
        return False

async def main():
    print("=== TTS Pipeline V1 - Edge TTS 100% Gratis ===")
    print(f"Default eterno: PT-BR (FranciscaNeural/AntonioNeural)")
    print(f"Custo total: $0.00\n")
    
    # Buscar TOP 10 prioritarios primeiro
    print("Buscando TOP 10 prioritarios (IDs 682-691)...")
    videos = sb_request("GET", "/content_pipeline",
        params={
            "select": "id,title,script,metadata",
            "id": "in.(682,683,684,685,686,687,688,689,690,691)",
            "status": "eq.script_ready"
        })
    
    if not videos:
        print("TOP 10 ja processados. Buscando fila normal...")
        videos = sb_request("GET", "/content_pipeline",
            params={
                "select": "id,title,script,metadata",
                "status": "eq.script_ready",
                "order": "id.desc",
                "limit": "5"
            })
    
    if not videos:
        print("Fila vazia.")
        return
    
    print(f"\nProcessando {len(videos)} videos:\n")
    
    sucesso = 0
    for video in videos:
        try:
            ok = await processar_video(video)
            if ok: sucesso += 1
        except Exception as e:
            print(f"  ✗ Erro: {e}")
        
        # Rate limit suave
        await asyncio.sleep(2)
    
    print(f"\n=== TOTAL: {sucesso}/{len(videos)} audios gerados ===")
    print(f"Custo: $0.00 (Edge TTS Microsoft ilimitado)")

if __name__ == "__main__":
    asyncio.run(main())
