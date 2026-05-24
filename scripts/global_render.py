#!/usr/bin/env python3
"""
global_render.py — 4 Temas × 5 Idiomas × 7 Estilos Virais Analisados

BANCO DE IMAGENS (analisadas 24/Mai/2026):
  cinematic_dark.jpg  9.5/10 → narcisismo, gaslighting, dark psychology
  meditative.jpg      9.5/10 → 528Hz, sono, healing, meditação
  psych2go.jpg        8.5/10 → ansiedade, apego, burnout, depressão
  lofi_study.jpg      10/10  → estudo, lofi, concentração, chuva
  greenred.jpg        9.5/10 → binaural, geometria sagrada, frequências
  jason.jpg           9.0/10 → paz, natureza, serenidade, lago
  thumbnail_adhd      8.0/10 → ADHD, 40Hz, gamma, foco

REGRA ABSOLUTA: ZERO texto nos prompts Pollinations.
Texto SEMPRE via FFmpeg overlay com fonte correta e legível.
"""
import os, subprocess, requests, pathlib, time

SB_URL = os.getenv("SUPABASE_URL","https://tpjvalzwkqwttvmszvie.supabase.co")
SB_KEY = os.getenv("SUPABASE_SERVICE_KEY","")
SBH    = {"apikey":SB_KEY,"Authorization":f"Bearer {SB_KEY}",
          "Content-Type":"application/json","Prefer":"return=minimal"}
TMP    = pathlib.Path("/tmp/global"); TMP.mkdir(exist_ok=True)
GH_RAW = "https://raw.githubusercontent.com/tafita81/Repovazio/main"

CANAIS = {
    "EN": {"voz":"en-US-AriaNeural",     "cpm":25,"marca":"Psychology Frequencies · Science"},
    "PT": {"voz":"pt-BR-AntonioNeural",  "cpm":7, "marca":"Daniela Coelho · Pesquisa em Psicologia"},
    "ES": {"voz":"es-MX-DaliaNeural",    "cpm":9, "marca":"Psicología Frecuencias · Ciencia"},
    "DE": {"voz":"de-DE-KatjaNeural",    "cpm":18,"marca":"Psychologie Frequenzen · Wissenschaft"},
    "FR": {"voz":"fr-FR-DeniseNeural",   "cpm":14,"marca":"Psychologie Fréquences · Science"},
}

IMGS = {
    "dark":    f"{GH_RAW}/public/estilos_virais/cinematic_dark.jpg",
    "sleep":   f"{GH_RAW}/public/estilos_virais/meditative.jpg",
    "psych":   f"{GH_RAW}/public/estilos_virais/psych2go.jpg",
    "lofi":    f"{GH_RAW}/public/estilos_virais/lofi_study.jpg",
    "greenred":f"{GH_RAW}/public/estilos_virais/greenred.jpg",
    "nature":  f"{GH_RAW}/public/estilos_virais/jason.jpg",
    "focus":   f"{GH_RAW}/public/thumbnails/thumbnail_adhd_focus.jpg",
}

TEMAS = [
    {
        "id":683, "estilo":"dark", "hz":None,
        "EN":"The Covert Narcissist Who Plays the Victim",
        "PT":"O Narcisista Encoberto Que Parece Vítima",
        "ES":"El Narcisista Encubierto Que Parece Víctima",
        "DE":"Der Verdeckte Narzisst Als Opfer",
        "FR":"Le Narcissiste Caché Ressemble À Une Victime",
        "scripts":{
            "EN":"The most dangerous narcissist doesn't scream. They CRY. And when you leave... you're suddenly WRONG. This has a NAME. SAVE this.",
            "PT":"O narcisista mais PERIGOSO não grita. Ele CHORA. E quando você tenta sair... você é quem está ERRADA. Isso tem NOME. SALVA agora.",
            "ES":"El narcisista más PELIGROSO no grita. LLORA. Y cuando te vas... eres TÚ quien está EQUIVOCADA. Tiene NOMBRE. GUARDA esto.",
            "DE":"Der gefährlichste Narzisst schreit nicht. Er WEINT. Und wenn du gehst... bist DU plötzlich falsch. Das hat einen NAMEN. SPEICHERN.",
            "FR":"Le narcissiste le plus dangereux ne crie pas. Il PLEURE. Et quand tu pars... c'est TOI qui as tort. Ça a un NOM. ENREGISTRE.",
        }
    },
    {
        "id":"528hz", "estilo":"sleep", "hz":"528Hz",
        "EN":"528Hz Reduces Cortisol — Peer-Reviewed Evidence",
        "PT":"528Hz Reduz Cortisol — Evidência Científica",
        "ES":"528Hz Reduce Cortisol — Ciencia Real",
        "DE":"528Hz Reduziert Cortisol — Wissenschaftlich",
        "FR":"528Hz Réduit le Cortisol — Preuve Scientifique",
        "scripts":{
            "EN":"528Hz is not mysticism. It's wave physics. Studies show 65% cortisol reduction. Listen 15 min before sleep. SAVE for your next anxious moment.",
            "PT":"528Hz não é misticismo. É física de ondas. Estudos mostram 65% de redução no cortisol. Ouça 15 minutos antes de dormir. SALVA agora.",
            "ES":"528Hz no es misticismo. Es física de ondas. Estudios muestran 65% reducción cortisol. Escucha 15 min antes de dormir. GUARDA esto.",
            "DE":"528Hz ist keine Mystik. Es ist Wellenphysik. Studien zeigen 65% Cortisolreduktion. 15 Minuten vor Schlaf hören. SPEICHERN.",
            "FR":"528Hz n'est pas de la mystique. C'est de la physique. 65% de cortisol réduit. 15 min avant de dormir. ENREGISTRE.",
        }
    },
    {
        "id":"40hz", "estilo":"focus", "hz":"40Hz",
        "EN":"40Hz Gamma Improves ADHD Focus by 23%",
        "PT":"40Hz Gamma Melhora TDAH em 23%",
        "ES":"40Hz Gamma Mejora TDAH 23%",
        "DE":"40Hz Gamma Verbessert ADHS um 23%",
        "FR":"40Hz Gamma Améliore TDAH de 23%",
        "scripts":{
            "EN":"40Hz is gamma — your brain at PEAK focus. MIT shows 23% working memory improvement. For ADHD brains... this changes everything. Listen during work 45 min. SAVE now.",
            "PT":"40Hz é gamma — seu cérebro em FOCO máximo. MIT mostra 23% de melhora em memória. Para TDAH... isso muda tudo. Ouça durante trabalho 45 min. SALVA.",
            "ES":"40Hz es gamma. Tu cerebro en FOCO máximo. MIT muestra 23% mejora en memoria. Para TDAH... cambia todo. Escucha 45 min. GUARDA.",
            "DE":"40Hz ist Gamma — dein Gehirn auf HÖCHSTLEISTUNG. MIT: 23% Verbesserung. Für ADHS... alles ändert sich. 45 Min hören. SPEICHERN.",
            "FR":"40Hz c'est le gamma. Cerveau au MAX. MIT: 23% amélioration. Pour TDAH... tout change. 45 min pendant travail. ENREGISTRE.",
        }
    },
    {
        "id":701, "estilo":"psych", "hz":None,
        "EN":"Silent Depression Doesn't Look Like Sadness",
        "PT":"Depressão Silenciosa Não Parece Tristeza",
        "ES":"La Depresión Silenciosa No Parece Tristeza",
        "DE":"Stille Depression Sieht Nicht Nach Traurigkeit Aus",
        "FR":"La Dépression Silencieuse Ne Ressemble Pas À La Tristesse",
        "scripts":{
            "EN":"Silent depression doesn't look like sadness. It looks like EXHAUSTION that never ends. You function. But inside... the VOID. This has a NAME. SAVE if this resonates.",
            "PT":"Depressão silenciosa não parece tristeza. Parece CANSAÇO que nunca passa. Você funciona. Mas por dentro... o VAZIO. Isso tem NOME. SALVA se fizer sentido.",
            "ES":"La depresión silenciosa no parece tristeza. Parece AGOTAMIENTO. Funcionas. Pero dentro... el VACÍO. Tiene NOMBRE. GUARDA si esto resuena.",
            "DE":"Stille Depression sieht nicht nach Traurigkeit aus. Es ist ERSCHÖPFUNG. Du funktionierst. Aber innen... die LEERE. Das hat einen NAMEN. SPEICHERN.",
            "FR":"La dépression silencieuse ressemble à l'ÉPUISEMENT. Tu fonctionnes. Mais dedans... le VIDE. Ça a un NOM. ENREGISTRE si ça résonne.",
        }
    },
    {
        "id":684, "estilo":"psych", "hz":None,
        "EN":"High-Functioning Anxiety Looks Fine From the Outside",
        "PT":"Ansiedade de Alto Funcionamento Parece Bem Por Fora",
        "ES":"La Ansiedad de Alto Funcionamiento Parece Estar Bien",
        "DE":"Hochfunktionierende Angst Sieht Von Außen Normal Aus",
        "FR":"L'Anxiété Hautement Fonctionnelle Paraît Bien En Apparence",
        "scripts":{
            "EN":"You seem fine to everyone. But inside you're in EMERGENCY MODE constantly. That's high-functioning anxiety. And most people will NEVER see it. This has a NAME. SAVE this.",
            "PT":"Você parece bem para todo mundo. Mas por dentro está em MODO EMERGÊNCIA constante. Isso é ansiedade de alto funcionamento. Tem NOME. SALVA.",
            "ES":"Pareces bien para todos. Pero por dentro estás en MODO EMERGENCIA. Eso es ansiedad de alto funcionamiento. Tiene NOMBRE. GUARDA.",
            "DE":"Du scheinst allen gut zu gehen. Aber innen bist du im NOTFALLMODUS. Das ist hochfunktionierende Angst. Das hat einen NAMEN. SPEICHERN.",
            "FR":"Tu sembles bien pour tous. Mais dedans tu es en MODE URGENCE. C'est l'anxiété hautement fonctionnelle. Ça a un NOM. ENREGISTRE.",
        }
    },
]

def obter_img(estilo):
    url = IMGS.get(estilo, IMGS["nature"])
    p = TMP/f"bg_{estilo}.jpg"
    if p.exists() and p.stat().st_size > 20000: return p
    try:
        r = requests.get(url, timeout=20, verify=False)
        if r.status_code == 200 and len(r.content) > 10000:
            p.write_bytes(r.content); return p
    except: pass
    return None

def dur(path):
    r = subprocess.run(["ffprobe","-v","error","-show_entries","format=duration",
                        "-of","default=noprint_wrappers=1:nokey=1",str(path)],
                       capture_output=True, timeout=8)
    try: return float(r.stdout.strip())
    except: return 3.0

def tts(texto, voz, out):
    s = ". ".join(x.strip() for x in texto.replace("\n"," ").split(".") if x.strip())
    subprocess.run(["edge-tts",f"--voice={voz}","--rate=-12%",
                    f"--text={s}",f"--write-media={out}"],
                   capture_output=True, timeout=60)
    return pathlib.Path(out).exists()

def binaural(hz_str):
    if not hz_str: return None
    import re
    hz = int(re.sub(r"[^0-9]","",hz_str) or "528")
    ao = TMP/f"bi_{hz}.aac"
    if ao.exists() and ao.stat().st_size > 30000: return ao
    hr = hz + (4 if hz < 200 else 8)
    subprocess.run(["ffmpeg","-y","-f","lavfi","-i",f"sine=frequency={hz}:duration=600",
                    "-f","lavfi","-i",f"sine=frequency={hr}:duration=600",
                    "-filter_complex","[0:a]volume=0.04[l];[1:a]volume=0.04[r];[l][r]amerge=inputs=2[out]",
                    "-map","[out]","-c:a","aac","-b:a","128k",str(ao)],
                   capture_output=True, timeout=90)
    return ao if ao.exists() else None

def overlay_vf(estilo, titulo, marca, hz_label):
    t = titulo[:50].replace("'",r"\'")
    m = marca.replace("'",r"\'")
    hz = (hz_label or "").replace("'",r"\'")
    W, H = 1920, 1080
    b = {"dark":"0.52","psych":"0.62","sleep":"0.55","focus":"0.50",
         "greenred":"0.50","nature":"0.58","lofi":"0.65"}.get(estilo,"0.60")
    if estilo == "sleep":
        return (f"scale={W}:{H}:force_original_aspect_ratio=increase,crop={W}:{H},"
                f"colorchannelmixer=rr={b}:gg={b}:bb={b},"
                f"drawbox=y=0:color=black@0.72:width=iw:height=130:t=fill,"
                f"drawbox=y=ih-80:color=black@0.72:width=iw:height=80:t=fill,"
                f"drawtext=text='{hz}':fontsize=66:fontcolor=#FFD700:x=(w-text_w)/2:y=12:bold=1:shadowcolor=#8B6914:shadowx=3:shadowy=3,"
                f"drawtext=text='BINAURAL · SOLFEGGIO':fontsize=22:fontcolor=#FCD34D@0.88:x=(w-text_w)/2:y=90,"
                f"drawtext=text='{t}':fontsize=28:fontcolor=white@0.9:x=(w-text_w)/2:y=h*0.79:shadowcolor=#000:shadowx=2:shadowy=2,"
                f"drawtext=text='{m}':fontsize=14:fontcolor=#94A3B8:x=(w-text_w)/2:y=h-52")
    elif estilo in ("focus","greenred"):
        cor = "#00CFFF" if estilo=="greenred" else "#00FF88"
        return (f"scale={W}:{H}:force_original_aspect_ratio=increase,crop={W}:{H},"
                f"colorchannelmixer=rr={b}:gg={b}:bb={b},"
                f"drawbox=y=0:color=black@0.78:width=iw:height=120:t=fill,"
                f"drawbox=y=ih-80:color=black@0.78:width=iw:height=80:t=fill,"
                f"drawtext=text='{hz or 40}Hz':fontsize=80:fontcolor={cor}:x=(w-text_w)/2:y=6:bold=1:shadowcolor=#001a00:shadowx=5:shadowy=5,"
                f"drawtext=text='GAMMA · BINAURAL · FOCUS':fontsize=18:fontcolor={cor}@0.9:x=(w-text_w)/2:y=96,"
                f"drawtext=text='{t}':fontsize=26:fontcolor=white:x=(w-text_w)/2:y=h*0.81:bold=1:shadowcolor=#000:shadowx=2:shadowy=2,"
                f"drawtext=text='{m}':fontsize=14:fontcolor=#86EFAC:x=(w-text_w)/2:y=h-52")
    elif estilo == "dark":
        return (f"scale={W}:{H}:force_original_aspect_ratio=increase,crop={W}:{H},"
                f"colorchannelmixer=rr={b}:gg={b}:bb={b},"
                f"drawbox=y=0:color=black@0.85:width=iw:height=105:t=fill,"
                f"drawbox=y=ih-80:color=black@0.85:width=iw:height=80:t=fill,"
                f"drawbox=x=16:y=20:color=#EF4444:width=13:height=13:t=fill,"
                f"drawtext=text='AO VIVO · Psychology':fontsize=18:fontcolor=#EF4444:x=38:y=16:bold=1,"
                f"drawtext=text='{t}':fontsize=34:fontcolor=white:x=(w-text_w)/2:y=h*0.38:bold=1:shadowcolor=#000:shadowx=3:shadowy=3,"
                f"drawtext=text='{m}':fontsize=14:fontcolor=#CBD5E1:x=(w-text_w)/2:y=h-52")
    else:
        return (f"scale={W}:{H}:force_original_aspect_ratio=increase,crop={W}:{H},"
                f"colorchannelmixer=rr={b}:gg={b}:bb={b},"
                f"drawbox=y=0:color=black@0.70:width=iw:height=100:t=fill,"
                f"drawbox=y=ih-80:color=black@0.70:width=iw:height=80:t=fill,"
                f"drawbox=x=16:y=20:color=#EF4444:width=10:height=10:t=fill,"
                f"drawtext=text='Psychology · Science':fontsize=18:fontcolor=#818CF8:x=36:y=17:bold=1,"
                f"drawtext=text='{t}':fontsize=30:fontcolor=white:x=(w-text_w)/2:y=h*0.42:bold=1:shadowcolor=#000:shadowx=2:shadowy=2,"
                f"drawtext=text='{m}':fontsize=14:fontcolor=#A5B4FC:x=(w-text_w)/2:y=h-52")

def render(img_p, audio_p, vf, out_p):
    d = min(dur(audio_p)+0.5, 59.0)
    subprocess.run(["ffmpeg","-y","-loop","1","-i",str(img_p),"-i",str(audio_p),
                    "-vf",vf,"-t",str(d),"-c:v","libx264","-preset","fast",
                    "-pix_fmt","yuv420p","-r","30","-c:a","aac","-b:a","128k",
                    "-shortest",str(out_p)], capture_output=True, timeout=300)
    return out_p.exists() and out_p.stat().st_size > 100000

def salvar(titulo, script, voz, cpm, mp4=""):
    if not SB_KEY: return
    import urllib3; urllib3.disable_warnings()
    requests.post(f"{SB_URL}/rest/v1/en_channel_queue", headers=SBH,
        json={"titulo_en":titulo[:100],"script_en":script,"voz_en":voz,
              "canal_destino":"UCyCkIpsVgME9yCj_oXJFheA",
              "rpm_estimado":cpm,"status":"mp4_ready" if mp4 else "pending"},
        timeout=8, verify=False)

def run():
    import urllib3; urllib3.disable_warnings()
    print("=== GLOBAL RENDER — 5 Temas × 5 Idiomas ===\n")
    total = 0
    for tema in TEMAS:
        estilo = tema["estilo"]; hz = tema.get("hz")
        print(f"\n[{tema['id']}] {tema['EN'][:50]} → {estilo}")
        img_p = obter_img(estilo)
        if not img_p: print("  ⚠️ sem imagem"); continue
        fa = binaural(hz)
        for idioma, cfg in CANAIS.items():
            titulo = tema.get(idioma, tema["EN"])
            script = tema.get("scripts",{}).get(idioma,"")
            if not script: continue
            voz_p = TMP/f"voz_{tema['id']}_{idioma}.mp3"
            ok = tts(script, cfg["voz"], str(voz_p))
            if not ok: salvar(titulo,script,cfg["voz"],cfg["cpm"]); continue
            mix_p = TMP/f"mix_{tema['id']}_{idioma}.aac"
            if fa and fa.exists():
                subprocess.run(["ffmpeg","-y","-i",str(voz_p),"-i",str(fa),
                    "-filter_complex","[0:a]volume=1[v];[1:a]volume=0.12[f];[v][f]amix=inputs=2:duration=first[out]",
                    "-map","[out]","-c:a","aac","-b:a","128k",str(mix_p)],
                    capture_output=True, timeout=60)
            else: mix_p = voz_p
            vf = overlay_vf(estilo, titulo, cfg["marca"], hz)
            out_p = TMP/f"v_{tema['id']}_{idioma}.mp4"
            ok2 = render(img_p, mix_p, vf, out_p)
            if ok2:
                print(f"  🎬 {idioma}: {out_p.stat().st_size//1024}KB ✅")
                total += 1; salvar(titulo, script, cfg["voz"], cfg["cpm"], str(out_p))
            else:
                salvar(titulo, script, cfg["voz"], cfg["cpm"])
                print(f"  📝 {idioma}: salvo")
            time.sleep(1)
        time.sleep(3)
    print(f"\n{'='*45}\n  🎬 {total} vídeos | 5 idiomas × 5 temas\n{'='*45}")

if __name__=="__main__": run()
