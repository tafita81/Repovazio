#!/usr/bin/env python3
"""
auto_setup_live.py
1. Usa OAuth code OU refresh token existente
2. Obtém access token
3. Cria broadcast + stream → pega stream key
4. Adiciona como GitHub Secret
5. Inicia live 24/7 automaticamente
"""
import os, json, time, subprocess, requests, base64, pathlib, threading, textwrap, hashlib
from datetime import datetime, timezone, timedelta

# Credenciais
YT_CLIENT_ID     = os.getenv("YT_CLIENT_ID", "")
YT_CLIENT_SECRET = os.getenv("YT_CLIENT_SECRET", "")
YT_REFRESH_TOKEN = os.getenv("YT_REFRESH_TOKEN", "")
AUTH_CODE        = os.getenv("AUTH_CODE", "").strip()
GH_PAT           = os.getenv("GH_PAT", os.getenv("GITHUB_TOKEN", ""))
GROQ_KEY         = os.getenv("GROQ_API_KEY", "")
REPO             = os.getenv("GITHUB_REPOSITORY", "tafita81/Repovazio")
HORAS            = int(os.getenv("HORAS", "6"))

GH_H = {"Authorization": f"token {GH_PAT}", "Accept": "application/vnd.github.v3+json"}

def get_access_token():
    """Obtém access token via auth code OU refresh token"""
    if AUTH_CODE:
        print(f"  Usando auth code: {AUTH_CODE[:8]}...")
        r = requests.post("https://oauth2.googleapis.com/token", data={
            "code":          AUTH_CODE,
            "client_id":     YT_CLIENT_ID,
            "client_secret": YT_CLIENT_SECRET,
            "redirect_uri":  "urn:ietf:wg:oauth:2.0:oob",
            "grant_type":    "authorization_code",
        }, timeout=20)
    elif YT_REFRESH_TOKEN:
        print(f"  Usando refresh token...")
        r = requests.post("https://oauth2.googleapis.com/token", data={
            "refresh_token": YT_REFRESH_TOKEN,
            "client_id":     YT_CLIENT_ID,
            "client_secret": YT_CLIENT_SECRET,
            "grant_type":    "refresh_token",
        }, timeout=20)
    else:
        print("Nenhuma credencial YouTube disponível.")
        return None, None
    
    if r.status_code != 200:
        print(f"Erro OAuth: {r.status_code} — {r.text[:300]}")
        return None, None
    
    data = r.json()
    return data.get("access_token"), data.get("refresh_token", YT_REFRESH_TOKEN)

def add_github_secret(name, value):
    """Adiciona secret no GitHub via API com criptografia sodium"""
    try:
        from nacl import encoding, public
        rk = requests.get(f"https://api.github.com/repos/{REPO}/actions/secrets/public-key",
            headers=GH_H, timeout=10)
        pk_data = rk.json()
        pk = public.PublicKey(pk_data["key"].encode(), encoding.Base64Encoder())
        encrypted = base64.b64encode(public.SealedBox(pk).encrypt(value.encode())).decode()
        r = requests.put(
            f"https://api.github.com/repos/{REPO}/actions/secrets/{name}",
            headers=GH_H,
            json={"encrypted_value": encrypted, "key_id": pk_data["key_id"]},
            timeout=30)
        ok = r.status_code in (201, 204)
        print(f"  {'✅' if ok else '❌'} GitHub Secret: {name}")
        return ok
    except Exception as e:
        print(f"  ❌ GitHub Secret {name}: {e}")
        return False

def criar_youtube_live(access_token):
    """Cria broadcast + stream no YouTube via API"""
    YT_H = {"Authorization": f"Bearer {access_token}", "Content-Type": "application/json"}
    agora    = datetime.now(timezone.utc)
    start_t  = (agora + timedelta(minutes=2)).strftime("%Y-%m-%dT%H:%M:%S.000Z")
    
    TITULOS_LIVE = [
        "🔴 528Hz SONO PROFUNDO | Ansiedade, Apego e Trauma | Psicologia LIVE",
        "🔴 528Hz SLEEP | Anxiety & Attachment Healing | Psychology LIVE 24/7",
        "🔴 963Hz ANSIEDADE | Gaslighting e Narcisismo | Daniela Coelho LIVE",
    ]
    
    # Criar broadcast
    rb = requests.post(
        "https://www.googleapis.com/youtube/v3/liveBroadcasts?part=snippet,status,contentDetails",
        headers=YT_H,
        json={
            "snippet": {
                "title": TITULOS_LIVE[0],
                "scheduledStartTime": start_t,
                "description": (
                    "🌙 528Hz — frequência de transformação para sono profundo.\n\n"
                    "Baseado em pesquisa de van der Kolk, Ainsworth, Sapolsky, Malkin/Harvard.\n\n"
                    "Daniela Coelho · Pesquisa e Conteúdo em Psicologia\n"
                    "💬 daniela-ia.vercel.app\n"
                    "⚠️ Conteúdo educacional. Não substitui acompanhamento profissional."
                ),
            },
            "status": {"privacyStatus": "public", "selfDeclaredMadeForKids": False},
            "contentDetails": {"enableAutoStart": True, "enableDvr": True, "recordFromStart": True},
        }, timeout=30)
    
    if rb.status_code not in (200, 201):
        print(f"  ❌ Broadcast: {rb.status_code} — {rb.text[:300]}")
        return None, None
    
    broadcast_id = rb.json()["id"]
    print(f"  ✅ Broadcast: {broadcast_id}")
    
    # Criar stream
    rs = requests.post(
        "https://www.googleapis.com/youtube/v3/liveStreams?part=snippet,cdn,contentDetails",
        headers=YT_H,
        json={
            "snippet": {"title": "psicologia-doc-live"},
            "cdn": {"ingestionType": "rtmp", "resolution": "720p", "frameRate": "30fps"},
            "contentDetails": {"isReusable": True},
        }, timeout=30)
    
    if rs.status_code not in (200, 201):
        print(f"  ❌ Stream: {rs.status_code} — {rs.text[:300]}")
        return None, None
    
    stream_data  = rs.json()
    stream_id    = stream_data["id"]
    stream_key   = stream_data["cdn"]["ingestionInfo"]["streamName"]
    rtmp_address = stream_data["cdn"]["ingestionInfo"]["ingestionAddress"]
    print(f"  ✅ Stream: {stream_id}")
    print(f"  ✅ Key: {stream_key[:8]}...{stream_key[-4:]}")
    
    # Vincular
    requests.post(
        f"https://www.googleapis.com/youtube/v3/liveBroadcasts/bind"
        f"?id={broadcast_id}&part=id,contentDetails&streamId={stream_id}",
        headers=YT_H, timeout=30)
    
    return stream_key, rtmp_address

def iniciar_live(stream_key, rtmp_address):
    """Inicia a live 24/7 usando o stream key obtido"""
    import sys
    sys.path.insert(0, str(pathlib.Path(__file__).parent))
    
    rtmp_url = f"{rtmp_address}/{stream_key}"
    TMP = pathlib.Path("/tmp/live_auto")
    TMP.mkdir(exist_ok=True)
    
    # Gerar áudio 528Hz
    audio_out = TMP / "audio_528hz.aac"
    subprocess.run([
        "ffmpeg", "-y",
        "-f", "lavfi", "-i", "sine=frequency=528:duration=3600",
        "-f", "lavfi", "-i", "sine=frequency=532:duration=3600",
        "-f", "lavfi", "-i", "sine=frequency=174:duration=3600",
        "-f", "lavfi", "-i", "anoisesrc=color=pink:duration=3600",
        "-filter_complex",
        "[0:a]volume=0.035[l];[1:a]volume=0.035[r];[2:a]volume=0.012[b];[3:a]volume=0.004[p];"
        "[l][r]amerge=inputs=2[bin];[bin][b][p]amix=inputs=3[out]",
        "-map", "[out]", "-c:a", "aac", "-b:a", "192k", "-ar", "44100",
        str(audio_out)
    ], capture_output=True, timeout=120)
    
    # Gerar imagem base via Pollinations
    print("  Gerando imagem base...")
    prompt = "masterpiece, ultra HD dark purple background, aurora borealis particles, 528hz healing frequency concept, no text no people, extremely calming"
    img_url = f"https://image.pollinations.ai/prompt/{requests.utils.quote(prompt)}?model=flux&width=1280&height=720&seed=9528&nologo=true"
    try:
        ri = requests.get(img_url, timeout=60)
        img_path = TMP / "bg.jpg"
        img_path.write_bytes(ri.content)
    except:
        # Criar imagem fallback preta
        subprocess.run(["ffmpeg", "-y", "-f", "lavfi", "-i", "color=c=black:s=1280x720",
            "-frames:v", "1", str(TMP / "bg.jpg")], capture_output=True)
        img_path = TMP / "bg.jpg"
    
    # Criar slide com overlay
    slide = TMP / "slide.mp4"
    vf = (
        "scale=1280:720,"
        "drawbox=y=0:color=black@0.85:width=iw:height=65:t=fill,"
        "drawbox=y=ih-68:color=black@0.90:width=iw:height=68:t=fill,"
        "drawbox=x=12:y=16:color=#EF4444:width=10:height=10:t=fill,"
        "drawtext=text='528Hz SONO PROFUNDO':fontsize=20:fontcolor=#818CF8:x=32:y=12:bold=1:shadowcolor=black:shadowx=1:shadowy=1,"
        "drawtext=text='AO VIVO':fontsize=13:fontcolor=#EF4444:x=32:y=36:bold=1,"
        "drawtext=text='O apego ansioso hiperativa a amigdala durante o sono.':fontsize=22:fontcolor=white:x=(w-text_w)/2:y=h*0.42:bold=1:shadowcolor=#000:shadowx=2:shadowy=2,"
        "drawtext=text='Ainsworth / Siegel, UCLA':fontsize=15:fontcolor=#818CF8:x=(w-text_w)/2:y=h*0.42+36:shadowcolor=#000:shadowx=1:shadowy=1,"
        "drawtext=text='Daniela Coelho . Pesquisa e Conteudo em Psicologia':fontsize=13:fontcolor=#94A3B8:x=(w-text_w)/2:y=h-45,"
        "drawtext=text='daniela-ia.vercel.app':fontsize=12:fontcolor=#818CF8:x=(w-text_w)/2:y=h-25"
    )
    subprocess.run(["ffmpeg", "-y", "-loop", "1", "-i", str(img_path), "-vf", vf,
        "-t", "60", "-c:v", "libx264", "-preset", "fast", "-tune", "stillimage",
        "-pix_fmt", "yuv420p", "-r", "30", "-an", str(slide)],
        capture_output=True, timeout=120)
    
    playlist = TMP / "pl.txt"
    with open(playlist, "w") as f:
        f.write(f"file '{slide.resolve()}'\n")
    
    print(f"  Iniciando stream → YouTube...")
    audio_src = ["-stream_loop", "-1", "-i", str(audio_out)] if audio_out.exists() \
                else ["-f", "lavfi", "-i", "sine=frequency=528:duration=999999"]
    
    proc = subprocess.Popen([
        "ffmpeg", "-y",
        "-f", "concat", "-safe", "0", "-stream_loop", "-1", "-i", str(playlist),
        *audio_src,
        "-c:v", "libx264", "-preset", "veryfast", "-tune", "stillimage",
        "-b:v", "3000k", "-maxrate", "3000k", "-bufsize", "6000k",
        "-g", "60", "-pix_fmt", "yuv420p",
        "-c:a", "aac", "-b:a", "192k", "-ar", "44100", "-ac", "2",
        "-f", "flv", rtmp_url
    ])
    
    timeout_s = HORAS * 3600
    print(f"  ✅ Live iniciada! Duração: {HORAS}h")
    print(f"  Monitorar: https://studio.youtube.com")
    
    try:
        proc.wait(timeout=timeout_s)
    except:
        proc.terminate()

def run():
    print("=== AUTO SETUP LIVE YOUTUBE ===\n")
    
    print("1. Obtendo access token...")
    access_token, new_refresh = get_access_token()
    if not access_token:
        print("\n❌ Não foi possível obter access token.")
        print("\nEnvie o código de autorização:")
        print("1. Abra: https://accounts.google.com/o/oauth2/auth"
              "?client_id=552651753048-p26lb7afjs5f75nvfrmmf4eb1ps4sc98.apps.googleusercontent.com"
              "&redirect_uri=urn:ietf:wg:oauth:2.0:oob"
              "&scope=https://www.googleapis.com/auth/youtube"
              "&response_type=code&access_type=offline&prompt=consent")
        print("2. Login: psidanielacoelho1982@gmail.com")
        print("3. Copie o código")
        print("4. Actions → YouTube Auto Setup → Run → cole o código em auth_code")
        return
    
    print(f"  ✅ Access token: {access_token[:20]}...")
    
    # Salvar novo refresh token se veio do auth code
    if new_refresh and new_refresh != YT_REFRESH_TOKEN:
        add_github_secret("YOUTUBE_REFRESH_TOKEN", new_refresh)
    
    print("\n2. Criando live no YouTube...")
    stream_key, rtmp_address = criar_youtube_live(access_token)
    
    if not stream_key:
        print("❌ Não foi possível criar a live")
        return
    
    print("\n3. Salvando stream key no GitHub...")
    add_github_secret("YOUTUBE_STREAM_KEY",    stream_key)
    add_github_secret("YOUTUBE_STREAM_KEY_EN", stream_key)
    
    print("\n4. Iniciando live 24/7...")
    iniciar_live(stream_key, rtmp_address)

if __name__ == "__main__":
    run()
