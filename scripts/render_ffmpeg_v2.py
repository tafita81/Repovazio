#!/usr/bin/env python3
"""
render_ffmpeg_v2.py — Ken Burns + Audio → MP4 Final
Pega imagens (Pillow/Flux) + audio → renderiza MP4 Short/Long
ZERO texto na tela. ZERO subtitulos. ZERO overlay.
Apenas lower third e watermark sao permitidos.
"""
import os, json, time, requests, subprocess, tempfile
from supabase import create_client

SB_URL = os.environ["SUPABASE_URL"]
SB_KEY = os.environ["SUPABASE_KEY"]
sb = create_client(SB_URL, SB_KEY)

SB_ANON = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InRwanZhbHp3a3F3dHR2bXN6dmllIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NzYwMzUyOTMsImV4cCI6MjA5MTYxMTI5M30.UEgUo0Mw15ihQZykLAY5QApRzgTXkfIewZFzIgwao3Q"

VIOLET = "0x7C3AED"  # lower third cor

def get_videos_video_ready():
    """Busca videos com imagem pronta aguardando render MP4"""
    r = sb.table("content_pipeline").select(
        "id,title,audio_url,duracao_min,metadata,pub_order"
    ).eq("status", "video_ready").is_("mp4_url", None).order("pub_order").limit(3).execute()
    return r.data or []

def baixar_arquivo(url, path):
    """Baixa arquivo de URL publica"""
    r = requests.get(url, headers={"apikey": SB_ANON}, timeout=60)
    if r.status_code == 200:
        with open(path, "wb") as f:
            f.write(r.content)
        return True
    # Tentar sem header
    r2 = requests.get(url, timeout=60)
    if r2.status_code == 200:
        with open(path, "wb") as f:
            f.write(r2.content)
        return True
    print(f"    ERRO download {url}: {r.status_code}")
    return False

def render_video(v):
    vid_id = v["id"]
    title = v.get("title","")
    audio_url = v.get("audio_url","")
    duracao_min = float(v.get("duracao_min") or 0.9)
    meta = v.get("metadata") or {}
    img_url = meta.get("quantum_image","")
    emocao = meta.get("emocao","contemplativo")
    
    print(f"\n  #{vid_id} {title[:50]}")
    print(f"    duracao_min={duracao_min} | emocao={emocao}")
    
    if not img_url or not audio_url:
        print(f"    ⚠ falta img_url={bool(img_url)} audio_url={bool(audio_url)}")
        return False
    
    with tempfile.TemporaryDirectory() as tmp:
        img_path = f"{tmp}/img.jpg"
        audio_path = f"{tmp}/audio.mp3"
        out_path = f"{tmp}/video.mp4"
        
        print(f"    Baixando imagem...")
        if not baixar_arquivo(img_url, img_path):
            return False
            
        print(f"    Baixando audio...")
        if not baixar_arquivo(audio_url, audio_path):
            return False
        
        # Detectar duracao real do audio
        probe = subprocess.run(
            ["ffprobe", "-v", "quiet", "-print_format", "json", "-show_format", audio_path],
            capture_output=True, text=True
        )
        try:
            audio_dur = float(json.loads(probe.stdout)["format"]["duration"])
        except:
            audio_dur = duracao_min * 60
        
        print(f"    Audio: {audio_dur:.1f}s")
        
        # Resolucao por tipo
        is_short = duracao_min < 3
        if is_short:
            W, H = 1080, 1920  # Short vertical
        else:
            W, H = 1920, 1080  # Long horizontal
        
        # Ken Burns: zoom 100->110% ao longo do video
        # ZERO texto na tela - so lower third e watermark psi
        zoom_speed = 0.0005
        fps = 30
        total_frames = int(audio_dur * fps)
        
        # Filtro de video completo:
        # 1. Escalar imagem para resolucao correta
        # 2. Ken Burns suave
        # 3. Lower third: retangulo roxo + texto "Daniela Coelho | @psidanielacoelho"
        # 4. Watermark psi no canto (usando unicode psi como texto pequeno)
        
        vf = (
            f"scale={W}:{H}:force_original_aspect_ratio=increase,"
            f"crop={W}:{H},"
            f"zoompan=z=\'min(zoom+{zoom_speed},1.1)\':"
            f"x=\'iw/2-(iw/zoom/2)\':"
            f"y=\'ih/2-(ih/zoom/2)\':"
            f"d={total_frames}:s={W}x{H}:fps={fps},"
            # Lower third - box no rodape
            f"drawtext=text=\'Daniela Coelho \| Psicologa Clinica\':"
            f"fontsize={'28' if is_short else '36'}:fontcolor=white:font=DejaVuSans-Bold:"
            f"x={'30' if is_short else '40'}:y=h-{'60' if is_short else '70'}:"
            f"box=1:boxcolor=0x7C3AED@0.80:boxborderw={'12' if is_short else '15'},"
            f"drawtext=text=\'@psidanielacoelho\':"
            f"fontsize={'22' if is_short else '28'}:fontcolor=0xC4B5FD:font=DejaVuSans:"
            f"x={'30' if is_short else '40'}:y=h-{'28' if is_short else '32'}:"
            f"box=1:boxcolor=0x7C3AED@0.80:boxborderw=8,"
            # Watermark psi
            f"drawtext=text=\'psi\':"
            f"fontsize={'22' if is_short else '28'}:fontcolor=white@0.15:font=DejaVuSans:"
            f"x=w-60:y=20"
        )
        
        cmd = [
            "ffmpeg", "-y",
            "-loop", "1", "-i", img_path,
            "-i", audio_path,
            "-vf", vf,
            "-c:v", "libx264", "-preset", "slow", "-crf", "18",
            "-c:a", "aac", "-b:a", "192k", "-ar", "44100",
            "-pix_fmt", "yuv420p",
            "-t", str(audio_dur),
            "-shortest",
            out_path
        ]
        
        print(f"    Renderizando MP4 {W}x{H}...")
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
        
        if result.returncode != 0:
            print(f"    FFMPEG ERRO: {result.stderr[-500:]}")
            return False
        
        mp4_size = os.path.getsize(out_path)
        print(f"    MP4 gerado: {mp4_size:,} bytes ({mp4_size/1024/1024:.1f} MB)")
        
        # Upload MP4 para Supabase
        fname = f"mp4s/v{vid_id}_{int(time.time())}.mp4"
        with open(out_path, "rb") as f:
            mp4_bytes = f.read()
        
        try:
            sb.storage.from_("videos").upload(
                fname, mp4_bytes,
                file_options={"content-type": "video/mp4", "x-upsert": "true"}
            )
            mp4_url = f"{SB_URL}/storage/v1/object/public/videos/{fname}"
            print(f"    ✓ Upload OK: {mp4_url}")
        except Exception as e:
            # Tentar upload via requests com anon key
            r = requests.post(
                f"{SB_URL}/storage/v1/object/videos/{fname}",
                headers={"apikey": SB_ANON, "Authorization": f"Bearer {SB_ANON}",
                         "Content-Type": "video/mp4", "x-upsert": "true"},
                data=mp4_bytes
            )
            if r.status_code in [200, 201]:
                mp4_url = f"{SB_URL}/storage/v1/object/public/videos/{fname}"
                print(f"    ✓ Upload anon OK: {mp4_url}")
            else:
                print(f"    ⚠ Upload erro: {r.status_code} {r.text[:200]}")
                return False
        
        # Atualizar banco
        sb.table("content_pipeline").update({
            "status": "mp4_ready",
            "mp4_url": mp4_url,
            "metadata": (v.get("metadata") or {}) | {
                "mp4_url": mp4_url,
                "mp4_size_bytes": mp4_size,
                "duration_seconds": audio_dur,
                "resolution": f"{W}x{H}",
                "render_version": "v2_kenburns_pillow",
                "rendered_at": int(time.time()),
                "zero_texto_na_tela": True,
                "lower_third": "Daniela Coelho | @psidanielacoelho",
                "watermark": "psi 15% opacity corner"
            }
        }).eq("id", vid_id).execute()
        
        print(f"    ✓ status=mp4_ready salvo")
        return True

def main():
    print("=== RENDER FFMPEG V2 — Ken Burns + Audio → MP4 ===")
    print("REGRA: ZERO texto na tela | so lower third e watermark psi")
    
    videos = get_videos_video_ready()
    print(f"Videos video_ready aguardando render: {len(videos)}")
    
    ok = 0
    for v in videos:
        try:
            if render_video(v):
                ok += 1
            time.sleep(2)
        except Exception as e:
            import traceback
            print(f"  ERRO #{v.get('id')}: {e}")
            traceback.print_exc()
    
    print(f"\nConcluido: {ok}/{len(videos)} videos renderizados")

if __name__ == "__main__":
    main()
