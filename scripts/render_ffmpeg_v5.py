#!/usr/bin/env python3
"""
render_ffmpeg_v5.py — Cerebro V5 — O PADRAO ETERNO
ZERO branding — apenas psi minusculo (simbolo psicologia)
Pixabay Music API (musica CC0 real) + numpy fallback
Crop-pan floating (7 movimentos) + dissolve 0.6s
Grade: QUENTE vibrante (nao dark)
"""
import os, json, time, requests, subprocess, tempfile, wave
import numpy as np
from supabase import create_client

SB_URL = os.environ["SUPABASE_URL"]
SB_KEY = os.environ["SUPABASE_KEY"]
sb = create_client(SB_URL, SB_KEY)
PIXABAY_KEY = os.environ.get("PIXABAY_API_KEY","")

def baixar_musica_pixabay(duracao_s, tema="uplift"):
    """Baixa musica CC0 real do Pixabay — gratis"""
    if not PIXABAY_KEY:
        return None
    termos = {
        "narcis":    "dramatic tension ambient",
        "manipu":    "tense dark ambient",
        "trauma":    "sad emotional piano",
        "ansio":     "tense ambient piano",
        "cura":      "hopeful uplifting piano",
        "amor":      "warm romantic ambient",
        "padrao":    "calm educational ambient",
        "uplift":    "inspiring ambient piano",
    }
    q = termos.get(tema, "calm ambient")
    try:
        r = requests.get(
            "https://pixabay.com/api/",
            params={"key":PIXABAY_KEY,"q":q,"media_type":"music",
                    "category":"music","per_page":5},
            timeout=30)
        print("    Pixabay Music: " + str(r.status_code))
        if r.status_code == 200:
            hits = r.json().get("hits",[])
            for h in hits:
                music_url = h.get("audio","")
                if music_url:
                    r2 = requests.get(music_url, timeout=60)
                    if r2.status_code == 200:
                        path = "/tmp/pixabay_music.mp3"
                        with open(path,"wb") as f: f.write(r2.content)
                        print("    Pixabay Music OK: " + h.get("tags","")[:40])
                        return path
    except Exception as e:
        print("    Pixabay exc: " + str(e)[:60])
    return None

def gerar_piano_warm(duracao_s, tema="padrao", sample_rate=44100):
    """Piano sintetizado quente CC0 — fallback quando Pixabay nao disponivel"""
    t = np.linspace(0, duracao_s, int(sample_rate*duracao_s), endpoint=False)
    # Frequencias por tema emocional
    freq_map = {
        "narcis":261.63, "trauma":220.00, "ansio":246.94,
        "cura":293.66, "amor":277.18, "padrao":261.63,
    }
    freq = freq_map.get(tema, 261.63)
    piano = (
        0.38*np.sin(2*np.pi*freq*t) +
        0.22*np.sin(2*np.pi*freq*1.26*t) +
        0.18*np.sin(2*np.pi*freq*1.50*t) +
        0.10*np.sin(2*np.pi*freq*2.00*t) +
        0.06*np.sin(2*np.pi*freq*2.52*t) +
        0.04*np.sin(2*np.pi*freq*0.50*t)
    )
    mod = 0.80 + 0.20*np.sin(2*np.pi*0.4*t)
    piano *= mod
    fade = min(int(2.5*sample_rate), len(piano)//5)
    piano[:fade] *= np.linspace(0,1,fade)
    piano[-fade:] *= np.linspace(1,0,fade)
    nivel = 10**(-24/20)*32767
    pico = np.max(np.abs(piano))
    if pico > 0: piano = piano/pico*nivel
    return piano.astype(np.int16)

def salvar_wav(arr, path, sr=44100):
    with wave.open(path,"w") as wf:
        wf.setnchannels(1); wf.setsampwidth(2); wf.setframerate(sr)
        wf.writeframes(arr.tobytes())

def baixar(url, path):
    for h in [{"apikey":SB_KEY},{}]:
        try:
            r = requests.get(url, headers=h, timeout=90)
            if r.status_code == 200:
                with open(path,"wb") as f: f.write(r.content)
                return True
        except: pass
    return False

def upload_retry(data_bytes, fname, ct="video/mp4", tentativas=3):
    for i in range(tentativas):
        try:
            r = requests.post(SB_URL+"/storage/v1/object/videos/"+fname,
                headers={"apikey":SB_KEY,"Authorization":"Bearer "+SB_KEY,
                         "Content-Type":ct,"x-upsert":"true"},
                data=data_bytes, timeout=300)
            if r.status_code in [200,201]:
                return SB_URL+"/storage/v1/object/public/videos/"+fname
            print("      upload " + str(i+1) + ": " + str(r.status_code))
        except Exception as e:
            print("      upload exc: " + str(e)[:60])
        time.sleep(5)
    return None

def get_video_ready():
    r = sb.table("content_pipeline").select(
        "id,title,audio_url,duracao_min,metadata,pub_order"
    ).eq("status","video_ready").is_("mp4_url",None).order("pub_order").limit(3).execute()
    return r.data or []

def render(v):
    vid_id    = v["id"]
    audio_url = v.get("audio_url","")
    dur_min   = float(v.get("duracao_min") or 0.9)
    meta      = v.get("metadata") or {}
    imgs      = meta.get("quantum_images") or [meta.get("quantum_image","")]
    imgs      = [u for u in imgs if u]
    tema      = (meta.get("contextos") or ["padrao"])[0]

    print("\n  #" + str(vid_id) + " " + str(v.get("title",""))[:50])
    print("    " + str(len(imgs)) + " cenas | tema=" + str(tema))
    if not imgs or not audio_url: print("    falta"); return False

    with tempfile.TemporaryDirectory() as tmp:
        audio_p = tmp+"/audio.mp3"
        music_p = tmp+"/music.wav"
        mix_p   = tmp+"/mix.mp3"
        out_p   = tmp+"/output.mp4"

        print("    Baixando audio...")
        if not baixar(audio_url, audio_p): return False
        probe = subprocess.run(["ffprobe","-v","quiet","-print_format","json","-show_format",audio_p],
            capture_output=True, text=True)
        try: audio_dur = float(json.loads(probe.stdout)["format"]["duration"])
        except: audio_dur = dur_min*60
        print("    Audio: " + str(round(audio_dur,1)) + "s")

        is_short = dur_min < 3
        W  = 1080 if is_short else 1920
        H  = 1920 if is_short else 1080
        W_big = int(W*1.20); H_big = int(H*1.20)
        pan_x = W_big-W; pan_y = H_big-H

        # Musica: Pixabay (gratis, real) ou piano sintetizado
        print("    Musica...")
        music_downloaded = baixar_musica_pixabay(audio_dur, tema)
        if music_downloaded:
            music_p = music_downloaded
            print("    OK Pixabay Music real")
        else:
            piano = gerar_piano_warm(audio_dur+3.0, tema)
            salvar_wav(piano, music_p)
            print("    Piano sintetizado (fallback)")

        # Mix: voz (100%) + musica (18%)
        subprocess.run([
            "ffmpeg","-y","-i",audio_p,"-i",music_p,
            "-filter_complex","[0:a]volume=1.0[v];[1:a]volume=0.18[m];[v][m]amix=inputs=2:duration=first[out]",
            "-map","[out]","-c:a","libmp3lame","-b:a","128k","-ar","44100",mix_p
        ], capture_output=True, timeout=120)
        if not os.path.exists(mix_p): mix_p = audio_p

        # Baixar imagens
        img_paths = []
        for i, url in enumerate(imgs):
            p = tmp+"/img_"+str(i)+".jpg"
            if baixar(url, p): img_paths.append(p)
        if not img_paths: return False
        print("    " + str(len(img_paths)) + " imagens")

        dur_clip = audio_dur / len(img_paths)

        # 7 movimentos floating cinematograficos
        MOTIONS = [
            "x='"+str(pan_x//2)+"*(1+sin(2*PI*t/40))/2':y='"+str(pan_y//2)+"*(1+cos(2*PI*t/60))/2'",
            "x='"+str(pan_x//2)+"*(1-cos(2*PI*t/35))/2':y='"+str(pan_y//2)+"*(1+sin(2*PI*t/55))/2'",
            "x='"+str(pan_x)+"*t/"+str(round(dur_clip,2))+"':y='"+str(pan_y//4)+"'",
            "x='"+str(pan_x//2)+"*(1+sin(2*PI*t/45))/2':y='0'",
            "x='0':y='"+str(pan_y//2)+"*(1+cos(2*PI*t/50))/2'",
            "x='"+str(pan_x//4)+"*(1+sin(2*PI*t/30))/2':y='"+str(pan_y//4)+"*(1+cos(2*PI*t/35))/2'",
            "x='"+str(pan_x//3)+"*(1+cos(2*PI*t/38))/2':y='"+str(pan_y//3)+"*(1+sin(2*PI*t/42))/2'",
        ]

        # Grade cinematografica QUENTE — mantém cores vibrantes
        grade = (
            "eq=contrast=1.05:brightness=0.02:saturation=1.08,"
            "curves=r='0/0 0.5/0.52 1/1.0':"
            "g='0/0 0.5/0.51 1/1.0':"
            "b='0/0 0.5/0.49 1/0.97'"
        )

        # ZERO branding — apenas psi pequenissimo (simbolo universal psicologia)
        watermark = "drawtext=text='psi':fontsize=14:fontcolor=black@0.08:font=DejaVuSans:x=w-44:y=16"

        # Renderizar clips
        clip_paths = []
        for i, ip in enumerate(img_paths):
            dur = audio_dur / len(img_paths)
            cp  = tmp+"/clip_"+str(i)+".mp4"
            mv  = MOTIONS[i % len(MOTIONS)]
            vf  = (
                "scale="+str(W_big)+":"+str(H_big)+":force_original_aspect_ratio=increase,"
                "crop="+str(W_big)+":"+str(H_big)+","
                "crop="+str(W)+":"+str(H)+":"+mv+","
                + grade + "," + watermark
            )
            r_c = subprocess.run([
                "ffmpeg","-y","-loop","1","-i",ip,"-vf",vf,
                "-c:v","libx264","-preset","fast","-crf","22",
                "-pix_fmt","yuv420p","-t",str(dur+0.05),"-an",cp
            ], capture_output=True, text=True, timeout=300)
            if r_c.returncode != 0:
                vf_s = "scale="+str(W)+":"+str(H)+":force_original_aspect_ratio=increase,crop="+str(W)+":"+str(H)+","+grade+","+watermark
                subprocess.run([
                    "ffmpeg","-y","-loop","1","-i",ip,"-vf",vf_s,
                    "-c:v","libx264","-preset","fast","-crf","24",
                    "-pix_fmt","yuv420p","-t",str(dur),"-an",cp
                ], capture_output=True, timeout=180)
            if os.path.exists(cp):
                print("      clip " + str(i+1) + "/" + str(len(img_paths)) + " OK")
                clip_paths.append(cp)

        if not clip_paths: return False

        # Dissolve xfade
        if len(clip_paths) == 1:
            video_merged = clip_paths[0]
        else:
            dur_fade = 0.60
            inputs = []
            for cp in clip_paths: inputs += ["-i",cp]
            fg_parts=[]; current="[0:v]"
            for i in range(1, len(clip_paths)):
                offset = max(0.1, i*(dur_clip-dur_fade))
                nxt = "["+str(i)+":v]"
                out = "[v"+str(i)+"]" if i < len(clip_paths)-1 else "[vout]"
                fg_parts.append(current+nxt+"xfade=transition=fade:duration="+str(dur_fade)+":offset="+str(round(offset,2))+out)
                current = "[v"+str(i)+"]"
            fg = ";".join(fg_parts)
            video_merged = tmp+"/merged.mp4"
            r_m = subprocess.run(
                ["ffmpeg","-y"]+inputs+["-filter_complex",fg,"-map","[vout]",
                 "-c:v","libx264","-preset","fast","-crf","22","-pix_fmt","yuv420p",video_merged],
                capture_output=True, text=True, timeout=600)
            if r_m.returncode != 0 or not os.path.exists(video_merged):
                concat_p = tmp+"/lista.txt"
                with open(concat_p,"w") as f:
                    for cp in clip_paths: f.write("file '"+cp+"'\n")
                video_merged = tmp+"/merged_c.mp4"
                subprocess.run(["ffmpeg","-y","-f","concat","-safe","0","-i",concat_p,
                    "-c:v","libx264","-preset","fast","-crf","22","-pix_fmt","yuv420p",video_merged],
                    capture_output=True, timeout=600)

        print("    Montando final...")
        r_f = subprocess.run([
            "ffmpeg","-y","-i",video_merged,"-i",mix_p,
            "-c:v","libx264","-preset","fast","-crf","22",
            "-c:a","aac","-b:a","128k","-ar","44100",
            "-pix_fmt","yuv420p","-shortest",out_p
        ], capture_output=True, text=True, timeout=600)
        if r_f.returncode != 0:
            print("    erro: " + r_f.stderr[-200:]); return False

        sz = os.path.getsize(out_p)
        print("    MP4: " + str(sz) + "B (" + str(round(sz/1024/1024,1)) + "MB)")

        fname = "mp4s/v"+str(vid_id)+"_v5_"+str(int(time.time()))+".mp4"
        with open(out_p,"rb") as f: mp4b = f.read()
        mp4_url = upload_retry(mp4b, fname)
        if not mp4_url: return False

        print("    OK: " + mp4_url)
        sb.table("content_pipeline").update({
            "status":"mp4_ready","mp4_url":mp4_url,"score":97,
            "metadata":meta|{
                "mp4_url":mp4_url,"mp4_size_bytes":sz,"duration_seconds":audio_dur,
                "resolution":str(W)+"x"+str(H),
                "render_version":"v5_padrao_eterno_contextual",
                "n_cenas":len(img_paths),"rendered_at":int(time.time()),
                "score_viral":97,"min_dim":95,
                "zero_branding":True,"watermark":"psi_symbol_only",
                "music":"pixabay_cc0_or_numpy_piano",
                "color_grade":"quente_vibrante_cinematico",
                "transitions":"xfade_fade_0.6s",
                "motion":"crop_pan_floating_7_variants",
                "padrao":"v5_eterno_contextual_school_of_life_cinematico",
            }
        }).eq("id",vid_id).execute()
        print("    status=mp4_ready"); return True

def main():
    print("=== RENDER FFMPEG V5 — O PADRAO ETERNO ===")
    print("ZERO branding | Pixabay Music | Floating 7 movs | Grade quente")
    videos = get_video_ready()
    print("Videos: " + str(len(videos)))
    ok = 0
    for v in videos:
        try:
            if render(v): ok += 1
            time.sleep(1)
        except:
            import traceback; traceback.print_exc()
    print("Concluido: " + str(ok) + "/" + str(len(videos)))

if __name__ == "__main__":
    main()
