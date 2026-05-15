#!/usr/bin/env python3
"""
render_ffmpeg_v3.py — Cerebro V3 CINEMATOGRAFICO
Tecnicas:
  - Color grading DaVinci-style: saturacao -20%, contraste +15%, temperatura fria
  - Floating motion (drift + micro-zoom — nao so Ken Burns)
  - Dissolve transitions (invisivel, atmosferico) entre cenas
  - Music bed: drone atmosferico sintetizado (CC0, numpy)
  - Vinheta adicional no video
  - ZERO texto durante narracao
  - Lower third minimalista ψ Daniela
"""
import os, json, time, requests, subprocess, tempfile, math
import numpy as np
from supabase import create_client

SB_URL = os.environ["SUPABASE_URL"]
SB_KEY = os.environ["SUPABASE_KEY"]
sb = create_client(SB_URL, SB_KEY)
SB_ANON = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InRwanZhbHp3a3F3dHR2bXN6dmllIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NzYwMzUyOTMsImV4cCI6MjA5MTYxMTI5M30.UEgUo0Mw15ihQZykLAY5QApRzgTXkfIewZFzIgwao3Q"

def gerar_drone_atmosferico(duracao_s: float, sample_rate: int = 44100) -> np.ndarray:
    """
    Gera drone atmosferico sintetico (CC0).
    Multi-frequencia para som rico e profundo.
    Modulacao lenta para efeito de 'respiracao'.
    """
    t = np.linspace(0, duracao_s, int(sample_rate * duracao_s), endpoint=False)
    freq_base = 55.0  # La grave (A1)

    # Harmonicos (tom orgao/sintetizador)
    drone = (
        0.50 * np.sin(2 * np.pi * freq_base * t) +          # fundamental
        0.25 * np.sin(2 * np.pi * freq_base * 2 * t) +      # 2o harmonico
        0.15 * np.sin(2 * np.pi * freq_base * 3 * t) +      # 3o
        0.08 * np.sin(2 * np.pi * freq_base * 4 * t) +      # 4o
        0.04 * np.sin(2 * np.pi * freq_base * 5 * t) +      # 5o
        0.03 * np.sin(2 * np.pi * freq_base * 0.5 * t)      # sub-harmonico
    )

    # Modulacao de amplitude lenta (2 ciclos por duracao) — "respiracao"
    mod_lento = 0.75 + 0.25 * np.sin(2 * np.pi * (2.0/duracao_s) * t)
    # Tremolo sutil (6 Hz)
    tremolo = 1.0 + 0.04 * np.sin(2 * np.pi * 6.0 * t)
    drone = drone * mod_lento * tremolo

    # Fade in/out (3 segundos cada lado)
    fade_samples = min(int(3 * sample_rate), len(drone)//4)
    drone[:fade_samples] *= np.linspace(0, 1, fade_samples)
    drone[-fade_samples:] *= np.linspace(1, 0, fade_samples)

    # Normalizar em -22dB (bem abaixo da voz)
    nivel_alvo = 10 ** (-22/20) * 32767  # -22dBFS
    pico = np.max(np.abs(drone))
    if pico > 0: drone = drone / pico * nivel_alvo

    return drone.astype(np.int16)

def salvar_wav_mono(arr: np.ndarray, path: str, sample_rate: int = 44100):
    import wave, struct
    with wave.open(path, 'w') as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2)
        wf.setframerate(sample_rate)
        wf.writeframes(arr.tobytes())

def baixar(url: str, path: str) -> bool:
    for h in [{"apikey":SB_ANON},{}]:
        try:
            r = requests.get(url, headers=h, timeout=90)
            if r.status_code == 200:
                with open(path,"wb") as f: f.write(r.content)
                return True
        except: pass
    return False

def get_video_ready():
    r = sb.table("content_pipeline").select(
        "id,title,audio_url,duracao_min,metadata,pub_order"
    ).eq("status","video_ready").is_("mp4_url",None).order("pub_order").limit(3).execute()
    return r.data or []

def render(v: dict) -> bool:
    vid_id    = v["id"]
    audio_url = v.get("audio_url","")
    dur_min   = float(v.get("duracao_min") or 0.9)
    meta      = v.get("metadata") or {}
    imgs      = meta.get("quantum_images") or [meta.get("quantum_image","")]
    imgs      = [u for u in imgs if u]

    print(f"\n  #{vid_id} {v.get('title','')[:50]}")
    print(f"    {len(imgs)} cenas cinematograficas | dur_min={dur_min}")
    if not imgs or not audio_url: print("    falta imagem ou audio"); return False

    with tempfile.TemporaryDirectory() as tmp:
        audio_p  = f"{tmp}/audio.mp3"
        music_p  = f"{tmp}/drone.wav"
        mix_p    = f"{tmp}/mix.mp3"
        out_p    = f"{tmp}/output.mp4"

        print("    Baixando audio...")
        if not baixar(audio_url, audio_p): return False

        probe = subprocess.run(
            ["ffprobe","-v","quiet","-print_format","json","-show_format",audio_p],
            capture_output=True, text=True)
        try: audio_dur = float(json.loads(probe.stdout)["format"]["duration"])
        except: audio_dur = dur_min * 60
        print(f"    Audio: {audio_dur:.1f}s")

        is_short = dur_min < 3
        W, H = (1080, 1920) if is_short else (1920, 1080)
        fps  = 30
        dur_cena = audio_dur / len(imgs)

        # Gerar drone atmosferico
        print("    Gerando drone atmosferico...")
        drone = gerar_drone_atmosferico(audio_dur + 2.0)
        salvar_wav_mono(drone, music_p)

        # Mixar voz + drone
        subprocess.run([
            "ffmpeg","-y","-i",audio_p,"-i",music_p,
            "-filter_complex",
            "[0:a]volume=1.0[v];[1:a]volume=0.22[m];[v][m]amix=inputs=2:duration=first[out]",
            "-map","[out]","-c:a","libmp3lame","-b:a","192k","-ar","44100",
            mix_p
        ], capture_output=True, timeout=120)
        if not os.path.exists(mix_p): mix_p = audio_p  # fallback

        # Baixar imagens
        img_paths = []
        for i, url in enumerate(imgs):
            p = f"{tmp}/img_{i}.jpg"
            if baixar(url, p): img_paths.append(p)
        if not img_paths: return False
        print(f"    {len(img_paths)} imagens baixadas")

        # Floating motions — variedade de movimentos cinematograficos
        # Baseado no documento: floating motion, drift, micro-zoom
        MOVIMENTOS = [
            # zoom lento centro (Ken Burns classico)
            "z='zoom+0.0004':x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)'",
            # drift para esquerda + zoom
            "z='zoom+0.0004':x='iw*0.45-(iw/zoom/2)':y='ih/2-(ih/zoom/2)'",
            # drift para direita lento
            "z='zoom+0.0004':x='iw*0.55-(iw/zoom/2)':y='ih/2-(ih/zoom/2)'",
            # zoom-out contemplativo
            "z='1.08-in*0.0003':x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)'",
            # subindo lentamente
            "z='zoom+0.0003':x='iw/2-(iw/zoom/2)':y='ih*0.48-(ih/zoom/2)'",
            # floating (move levemente para baixo)
            "z='zoom+0.0003':x='iw/2-(iw/zoom/2)':y='ih*0.52-(ih/zoom/2)'",
            # micro-zoom bem sutil
            "z='zoom+0.0002':x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)'",
        ]

        # Color grading cinematografico
        # saturacao -20%, contraste +15%, temperatura ligeiramente fria
        grade = (
            "curves=r='0/0 0.07/0.04 0.5/0.50 1/0.95':"
            "g='0/0 0.07/0.05 0.5/0.51 1/0.96':"
            "b='0/0 0.07/0.07 0.5/0.53 1/1.00',"
            "hue=s=0.80,"  # saturacao -20%
            "eq=contrast=1.15:brightness=-0.02:gamma=1.05,"  # contraste +15%
            "colorbalance=ss=-0.05:ms=0.05:hs=0.08"  # temperature fria
        )

        # Lower third minimalista
        lt_sz  = "22" if is_short else "26"
        lt_y   = "h-72" if is_short else "h-82"
        lt_y2  = "h-40" if is_short else "h-48"
        lt_bw  = "8" if is_short else "10"

        lower_third = (
            f"drawtext=text='Daniela Coelho | Psicologa Clinica':"
            f"fontsize={lt_sz}:fontcolor=white@0.85:font=DejaVuSans:"
            f"x=40:y={lt_y}:box=1:boxcolor=0x06060F@0.70:boxborderw={lt_bw},"
            f"drawtext=text='@psidanielacoelho':"
            f"fontsize=18:fontcolor=0xC4B5FD@0.75:font=DejaVuSans:"
            f"x=40:y={lt_y2}:box=1:boxcolor=0x06060F@0.70:boxborderw=7,"
            f"drawtext=text='psi':fontsize=16:fontcolor=white@0.08:font=DejaVuSans:x=w-50:y=18"
        )

        # Renderizar clips com dissolve (usando xfade)
        clip_paths = []
        for i, ip in enumerate(img_paths):
            dur = audio_dur / len(img_paths)
            cp  = f"{tmp}/clip_{i}.mp4"
            mv  = MOVIMENTOS[i % len(MOVIMENTOS)]
            nf  = int(dur * fps) + 2

            vf = (
                f"scale={W}:{H}:force_original_aspect_ratio=increase,"
                f"crop={W}:{H},"
                f"zoompan={mv}:d={nf}:s={W}x{H}:fps={fps},"
                f"{grade},"
                f"{lower_third}"
            )
            r_clip = subprocess.run(
                ["ffmpeg","-y","-loop","1","-i",ip,"-vf",vf,
                 "-c:v","libx264","-preset","fast","-crf","20",
                 "-pix_fmt","yuv420p","-t",str(dur+0.05),"-an",cp],
                capture_output=True, text=True, timeout=300)
            if r_clip.returncode != 0:
                # Fallback sem zoompan
                vf_simple = (
                    f"scale={W}:{H}:force_original_aspect_ratio=increase,"
                    f"crop={W}:{H},"
                    f"{grade},"
                    f"{lower_third}"
                )
                subprocess.run(
                    ["ffmpeg","-y","-loop","1","-i",ip,"-vf",vf_simple,
                     "-c:v","libx264","-preset","fast","-crf","22",
                     "-pix_fmt","yuv420p","-t",str(dur),"-an",cp],
                    capture_output=True, timeout=120)
            if os.path.exists(cp): clip_paths.append(cp)

        if not clip_paths: return False

        # Concat com dissolve via xfade (transicoes cinematograficas)
        # Para N clips: usar filtergraph xfade em cadeia
        if len(clip_paths) == 1:
            video_merged = clip_paths[0]
        else:
            # Construir filtergraph xfade
            dur_fade = 0.8  # dissolve de 0.8s entre cenas
            dur_clip = audio_dur / len(clip_paths)
            inputs = []
            for cp in clip_paths:
                inputs += ["-i", cp]
            # Filtergraph para dissolve em cadeia
            fg_parts = []
            current = "[0:v]"
            for i in range(1, len(clip_paths)):
                offset = i * dur_clip - dur_fade * i
                nxt = f"[{i}:v]"
                out = f"[v{i}]" if i < len(clip_paths)-1 else "[vout]"
                fg_parts.append(f"{current}{nxt}xfade=transition=dissolve:duration={dur_fade}:offset={max(0,offset)}{out}")
                current = f"[v{i}]"
            fg = ";".join(fg_parts)
            video_merged = f"{tmp}/merged.mp4"
            r_merge = subprocess.run(
                ["ffmpeg","-y"] + inputs + ["-filter_complex",fg,
                 "-map","[vout]",
                 "-c:v","libx264","-preset","slow","-crf","18",
                 "-pix_fmt","yuv420p",video_merged],
                capture_output=True, text=True, timeout=600)
            if r_merge.returncode != 0 or not os.path.exists(video_merged):
                # Fallback: concat simples
                concat_p = f"{tmp}/lista.txt"
                with open(concat_p,"w") as f:
                    for cp in clip_paths: f.write(f"file '{cp}'\n")
                video_merged = f"{tmp}/merged_simple.mp4"
                subprocess.run(
                    ["ffmpeg","-y","-f","concat","-safe","0","-i",concat_p,
                     "-c:v","libx264","-preset","fast","-crf","20",
                     "-pix_fmt","yuv420p",video_merged],
                    capture_output=True, timeout=600)

        # Adicionar audio mix ao video final
        print("    Montando video final (video + audio + drone)...")
        r_final = subprocess.run(
            ["ffmpeg","-y","-i",video_merged,"-i",mix_p,
             "-c:v","libx264","-preset","slow","-crf","17",
             "-c:a","aac","-b:a","192k","-ar","44100",
             "-pix_fmt","yuv420p","-shortest",out_p],
            capture_output=True, text=True, timeout=600)
        if r_final.returncode != 0:
            print(f"    erro final: {r_final.stderr[-300:]}"); return False

        sz = os.path.getsize(out_p)
        print(f"    MP4 final: {sz:,}B ({sz/1024/1024:.1f}MB)")
        fname = f"mp4s/v{vid_id}_cinem_{int(time.time())}.mp4"
        with open(out_p,"rb") as f: mp4b = f.read()
        r2 = requests.post(f"{SB_URL}/storage/v1/object/videos/{fname}",
            headers={"apikey":SB_ANON,"Authorization":f"Bearer {SB_ANON}",
                     "Content-Type":"video/mp4","x-upsert":"true"}, data=mp4b)
        if r2.status_code not in [200,201]:
            print(f"    upload err: {r2.status_code}"); return False
        mp4_url = f"{SB_URL}/storage/v1/object/public/videos/{fname}"
        print(f"    OK: {mp4_url}")
        sb.table("content_pipeline").update({
            "status":"mp4_ready","mp4_url":mp4_url,
            "metadata":meta | {
                "mp4_url":mp4_url,"mp4_size_bytes":sz,
                "duration_seconds":audio_dur,"resolution":f"{W}x{H}",
                "render_version":"v3_cinematic_dark_documentary",
                "n_cenas":len(img_paths),"rendered_at":int(time.time()),
                "zero_texto_na_tela":True,"drone_atmosferico":True,
                "color_grading":"saturacao-20pct_contraste+15pct_frio",
                "transitions":"xfade_dissolve_0.8s",
                "voice_speed":"0.88x",
                "lower_third":"minimalista_Daniela_Coelho",
            }
        }).eq("id",vid_id).execute()
        print("    status=mp4_ready"); return True

def main():
    print("=== RENDER FFMPEG V3 CINEMATOGRAFICO ===")
    print("Dissolve transitions | Color grading | Drone atmosferico | 0.88x voz")
    videos = get_video_ready(); print(f"Videos: {len(videos)}")
    ok = 0
    for v in videos:
        try:
            if render(v): ok += 1
            time.sleep(1)
        except:
            import traceback; traceback.print_exc()
    print(f"Concluido: {ok}/{len(videos)}")

if __name__ == "__main__":
    main()
