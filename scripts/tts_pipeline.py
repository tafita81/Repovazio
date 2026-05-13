#!/usr/bin/env python3
"""TTS Pipeline V2 - Edge TTS gratis + filtro robusto TOP 10"""
import os, sys, json, asyncio, urllib.request, urllib.parse, time, re

SBU = os.environ.get("SUPABASE_URL", "https://tpjvalzwkqwttvmszvie.supabase.co")
SBK = os.environ.get("SUPABASE_SERVICE_KEY") or os.environ.get("SUPABASE_KEY") or os.environ.get("SUPABASE_ANON_KEY")

if not SBK:
    print("ERRO: SUPABASE key nao configurado")
    print(f"  SUPABASE_URL={SBU[:30] if SBU else None}")
    sys.exit(1)

print(f"Supabase URL: {SBU[:50]}")
print(f"Supabase Key: {SBK[:20]}...")

try:
    import edge_tts
except ImportError:
    os.system(f"{sys.executable} -m pip install edge-tts --quiet")
    import edge_tts

VOZES_PT_BR = {
    "melancolico":"pt-BR-FranciscaNeural",
    "tenso":"pt-BR-AntonioNeural",
    "urgente":"pt-BR-AntonioNeural",
    "contemplativo":"pt-BR-FranciscaNeural",
    "calmo":"pt-BR-FranciscaNeural",
    "default":"pt-BR-FranciscaNeural"
}

def sb_req(method, path, body=None, params=None):
    url = f"{SBU}/rest/v1{path}"
    if params: url += "?" + urllib.parse.urlencode(params)
    headers = {"apikey":SBK, "Authorization":f"Bearer {SBK}",
               "Content-Type":"application/json", "Prefer":"return=representation"}
    data = json.dumps(body).encode() if body else None
    req = urllib.request.Request(url, data=data, method=method, headers=headers)
    try:
        with urllib.request.urlopen(req, timeout=30) as r:
            t = r.read().decode()
            return json.loads(t) if t else None
    except urllib.error.HTTPError as e:
        print(f"  SB HTTP {e.code}: {e.read().decode()[:200]}")
        return None
    except Exception as e:
        print(f"  SB ERR: {e}")
        return None

def upload_storage(bucket, path, file_bytes):
    url = f"{SBU}/storage/v1/object/{bucket}/{path}"
    req = urllib.request.Request(
        url, data=file_bytes, method="POST",
        headers={"apikey":SBK, "Authorization":f"Bearer {SBK}",
                 "Content-Type":"audio/mpeg", "x-upsert":"true"}
    )
    try:
        with urllib.request.urlopen(req, timeout=60) as r:
            r.read()
            return f"{SBU}/storage/v1/object/public/{bucket}/{path}"
    except urllib.error.HTTPError as e:
        if e.code in (400, 409):
            req2 = urllib.request.Request(url, data=file_bytes, method="PUT",
                headers={"apikey":SBK, "Authorization":f"Bearer {SBK}",
                         "Content-Type":"audio/mpeg"})
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

async def gerar_audio(texto, voz, output_path):
    try:
        texto_limpo = re.sub(r'[*_#`]', '', texto)
        texto_limpo = texto_limpo.replace('\n\n\n', '\n\n')
        communicate = edge_tts.Communicate(texto_limpo, voz, rate="-5%", pitch="+0Hz")
        await communicate.save(output_path)
        return True
    except Exception as e:
        print(f"  Edge TTS error: {e}")
        return False

async def processar(v):
    vid = v["id"]
    title = v.get("title", "") or ""
    script = v.get("script") or ""
    meta = v.get("metadata") or {}
    
    print(f"\n#{vid}: {title[:55]}")
    print(f"  script chars: {len(script)}")
    
    # VALIDACAO ROBUSTA
    if not script or len(script) < 100:
        print(f"  ✗ Script vazio ou muito curto")
        return False
    
    emocao = meta.get("emocao", "default")
    voz = VOZES_PT_BR.get(emocao, VOZES_PT_BR["default"])
    print(f"  emocao={emocao} | voz={voz}")
    
    output_path = f"/tmp/audio_{vid}.mp3"
    print(f"  Edge TTS gerando audio PT-BR...")
    ok = await gerar_audio(script, voz, output_path)
    if not ok or not os.path.exists(output_path):
        print(f"  ✗ Falha gerar audio")
        return False
    
    size = os.path.getsize(output_path)
    print(f"  ✓ Audio: {size/1024:.1f} KB")
    
    with open(output_path, "rb") as f:
        audio_bytes = f.read()
    
    storage_path = f"audios/v{vid}.mp3"
    print(f"  Upload Storage...")
    audio_url = upload_storage("videos", storage_path, audio_bytes)
    if not audio_url:
        print(f"  ✗ Upload falhou")
        return False
    
    print(f"  ✓ Upload OK")
    
    update = {
        "status": "audio_ready",
        "metadata": {
            **meta,
            "audio_url": audio_url,
            "audio_voz": voz,
            "audio_tamanho_bytes": size,
            "tts_provider": "edge_tts_microsoft",
            "tts_custo": "$0.00",
            "audio_gerado_em": time.strftime("%Y-%m-%dT%H:%M:%SZ"),
            "stack_gratuita_audio": True
        }
    }
    
    r = sb_req("PATCH", "/content_pipeline", body=update, params={"id":f"eq.{vid}"})
    if r is not None:
        print(f"  ✓ #{vid} -> audio_ready")
        try: os.remove(output_path)
        except: pass
        return True
    return False

async def main():
    print("=== TTS Pipeline V2 - Edge TTS PT-BR Default Eterno ===\n")
    
    # 1. TENTAR TOP 10 EXPLICITO
    print("Buscando TOP 10 (IDs 682-691)...")
    videos = sb_req("GET", "/content_pipeline",
        params={
            "select":"id,title,script,metadata",
            "id":"in.(682,683,684,685,686,687,688,689,690,691)",
            "status":"eq.script_ready",
            "order":"id.asc"
        })
    
    if not videos:
        print("TOP 10 nao encontrados em script_ready. Buscando audio_ready com problemas...")
        # Tentar fila geral
        videos = sb_req("GET", "/content_pipeline",
            params={
                "select":"id,title,script,metadata",
                "status":"eq.script_ready",
                "script":"not.is.null",
                "order":"id.desc",
                "limit":"10"
            })
    
    if not videos:
        print("Fila vazia.")
        return
    
    print(f"Processando {len(videos)} videos:")
    for v in videos:
        print(f"  - #{v['id']}: {(v.get('title') or '')[:50]} ({len(v.get('script') or '')} chars)")
    
    sucesso = 0
    for v in videos:
        try:
            ok = await processar(v)
            if ok: sucesso += 1
        except Exception as e:
            print(f"  ✗ EXCECAO: {e}")
        await asyncio.sleep(2)
    
    print(f"\n=== {sucesso}/{len(videos)} audios gerados | Custo: $0.00 ===")

if __name__ == "__main__":
    asyncio.run(main())
