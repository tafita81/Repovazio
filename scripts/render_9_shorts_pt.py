#!/usr/bin/env python3
"""
render_9_shorts_pt.py
Gera os 9 shorts PT-BR com:
  - Imagem correta do banco analisado (9 estilos virais)
  - TTS AntonioNeural/FranciscaNeural com rate otimizado
  - Binaural quando aplicável
  - Overlay FFmpeg por estilo
  - Sincronização imagem↔frase
  - Salvar no Supabase

BANCO ANALISADO:
  meditative.jpg    9.5/10 → 528Hz/sono/healing (Meditative Mind 3.2M)
  psych2go.jpg      8.5/10 → ansiedade/apego/burnout (Psych2Go 10.5M)
  lofi_study.jpg    10/10  → lofi/estudo/concentração (Lofi Girl 14M)
  greenred.jpg      9.5/10 → binaural/geometria (Greenred 2M)
  cinematic_dark.jpg 9.5/10 → narcisismo/gaslighting (Psychology Dark)
  jason.jpg         9.0/10 → paz/natureza/serenidade (Jason Stephenson 2.5M)
  thumbnail_adhd    8.0/10 → ADHD/40Hz/foco
"""
import os, subprocess, requests, pathlib, time, re

SB_URL = os.getenv("SUPABASE_URL","https://tpjvalzwkqwttvmszvie.supabase.co")
SB_KEY = os.getenv("SUPABASE_SERVICE_KEY","")
SBH = {"apikey":SB_KEY,"Authorization":f"Bearer {SB_KEY}",
       "Content-Type":"application/json","Prefer":"return=minimal"}
GH_RAW = "https://raw.githubusercontent.com/tafita81/Repovazio/main"
TMP = pathlib.Path("/tmp/r9"); TMP.mkdir(exist_ok=True)
W, H = 1920, 1080

# MAPA IMAGEM → ESTILO → OVERLAY
IMGS = {
    "meditative":    {"url":f"{GH_RAW}/public/estilos_virais/meditative.jpg",   "br":"0.55","overlay":"sleep"},
    "psych2go":      {"url":f"{GH_RAW}/public/estilos_virais/psych2go.jpg",      "br":"0.62","overlay":"psych"},
    "lofi_study":    {"url":f"{GH_RAW}/public/estilos_virais/lofi_study.jpg",    "br":"0.65","overlay":"lofi"},
    "greenred":      {"url":f"{GH_RAW}/public/estilos_virais/greenred.jpg",      "br":"0.50","overlay":"greenred"},
    "cinematic_dark":{"url":f"{GH_RAW}/public/estilos_virais/cinematic_dark.jpg","br":"0.52","overlay":"dark"},
    "jason":         {"url":f"{GH_RAW}/public/estilos_virais/jason.jpg",         "br":"0.58","overlay":"nature"},
    "adhd_focus":    {"url":f"{GH_RAW}/public/thumbnails/thumbnail_adhd_focus.jpg","br":"0.50","overlay":"focus"},
}

SHORTS = [
    {
        "id":683,"titulo":"O Narcisista Que Parece Vítima","img":"cinematic_dark","hz":None,"voz":"pt-BR-AntonioNeural",
        "frases":[
            "O narcisista mais PERIGOSO da sua vida não grita.",
            "Ele CHORA.",
            "E quando você tenta se afastar... de repente, você é quem está ERRADA.",
            "Isso tem NOME.",
            "E tem sinais que a MAIORIA das pessoas NUNCA percebe.",
            "Porque ele não age como você imagina que um narcisista age.",
            "Ele age como alguém que PRECISA de você.",
            "Se você quer entender o narcisista encoberto por COMPLETO...",
            "O vídeo está no canal. SALVA agora para assistir mais tarde.",
        ],
    },
    {
        "id":701,"titulo":"Depressão Silenciosa — Os Sinais Que Ninguém Vê","img":"psych2go","hz":None,"voz":"pt-BR-FranciscaNeural",
        "frases":[
            "Depressão silenciosa não parece tristeza.",
            "Parece CANSAÇO que nunca passa.",
            "Parece funcionar... mas por dentro estar APAGADA.",
            "Você ri nas fotos. Responde mensagens. Cumpre prazos.",
            "Mas de noite... o VAZIO aparece.",
            "Isso tem NOME.",
            "E afeta 1 em cada 5 pessoas sem que elas saibam.",
            "SALVA agora se isso faz sentido para você.",
        ],
    },
    {
        "id":684,"titulo":"Ansiedade de Alto Funcionamento","img":"psych2go","hz":None,"voz":"pt-BR-FranciscaNeural",
        "frases":[
            "Você parece bem para todo mundo.",
            "Mas por dentro você está em MODO DE EMERGÊNCIA constante.",
            "Isso não é força. Isso é ansiedade de alto funcionamento.",
            "E a MAIORIA das pessoas ao seu redor NUNCA percebe.",
            "Porque você sorri. Você entrega. Você aparece.",
            "Mas por dentro... o seu sistema nervoso está em COLAPSO.",
            "Isso tem NOME. E tem como MUDAR.",
            "SALVA esse vídeo para assistir mais tarde.",
        ],
    },
    {
        "id":688,"titulo":"Burnout Não É Cansaço — É Colapso Neurológico","img":"psych2go","hz":None,"voz":"pt-BR-AntonioNeural",
        "frases":[
            "Burnout não é PREGUIÇA.",
            "É colapso neurológico.",
            "O seu sistema nervoso simplesmente... DESLIGOU.",
            "E descanso sozinho não resolve.",
            "Porque não é o corpo que está cansado.",
            "É o sistema de regulação emocional que ESGOTOU.",
            "Isso é NEUROLÓGICO. E tem saída.",
            "SALVA agora para entender o que está acontecendo.",
        ],
    },
    {
        "id":689,"titulo":"Síndrome do Impostor","img":"psych2go","hz":None,"voz":"pt-BR-FranciscaNeural",
        "frases":[
            "Você sente que qualquer hora vão DESCOBRIR que você não merece estar onde está.",
            "Isso não é falta de confiança.",
            "Isso é Síndrome do Impostor.",
            "E afeta 70% das pessoas de ALTA performance.",
            "Você não é a única que se sente assim.",
            "E não... você NÃO está fingindo.",
            "Isso tem NOME. E tem como mudar.",
            "SALVA agora para assistir mais tarde.",
        ],
    },
    {
        "id":710,"titulo":"Gaslighting — Quando Te Fazem Duvidar da Realidade","img":"cinematic_dark","hz":None,"voz":"pt-BR-AntonioNeural",
        "frases":[
            "Gaslighting não parece manipulação.",
            "Parece... você sendo SENSÍVEL demais.",
            "Parece... você que INVENTOU tudo.",
            "Parece... você que não consegue LEMBRAR direito.",
            "Mas isso tem NOME.",
            "E é uma das formas mais SÉRIAS de abuso psicológico.",
            "Porque ataca a sua percepção da REALIDADE.",
            "SALVA agora se isso ressoa com você.",
        ],
    },
    {
        "id":"528hz","titulo":"528Hz — Reduz Cortisol e Ansiedade Cientificamente","img":"meditative","hz":"528Hz","voz":"pt-BR-AntonioNeural",
        "frases":[
            "528Hz não é misticismo.",
            "É física de ondas aplicada ao sistema nervoso.",
            "Estudos mostram redução de 65% no cortisol após exposição.",
            "Cortisol é o hormônio do estresse... e esse nível IMPORTA.",
            "Essa frequência ressoa com o DNA humano.",
            "E seu sistema nervoso RESPONDE.",
            "Ouça por 15 minutos antes de dormir.",
            "SALVA para a próxima vez que sentir ansiedade.",
        ],
    },
    {
        "id":"40hz","titulo":"40Hz Gamma — Protocolo TDAH e Foco Profundo","img":"adhd_focus","hz":"40Hz","voz":"pt-BR-AntonioNeural",
        "frases":[
            "40Hz não é moda.",
            "É a frequência gamma do cérebro em estado de foco MÁXIMO.",
            "Estudos do MIT mostram melhora de 23% em memória de trabalho.",
            "Para quem tem TDAH... isso é revolucionário.",
            "Seu cérebro não está quebrado. Ele funciona numa frequência diferente.",
            "E 40Hz o ajuda a sincronizar.",
            "Ouça durante trabalho ou estudo por 45 minutos.",
            "SALVA para usar no próximo projeto importante.",
        ],
    },
    {
        "id":"lofi","titulo":"Lofi para Estudar — Sem Distrações","img":"lofi_study","hz":None,"voz":"pt-BR-FranciscaNeural",
        "frases":[
            "O seu cérebro precisa de um estado de fluxo para absorver.",
            "E música lofi cria exatamente isso.",
            "Sem letra. Sem pico de atenção. Só fluxo.",
            "Pesquisas mostram aumento de 20% na retenção.",
            "Porque o cérebro usa recursos cognitivos para processar letras.",
            "Sem letra... toda energia vai para o conteúdo.",
            "Bota aqui. Abre o livro. E estuda.",
            "SALVA para a próxima sessão de estudos.",
        ],
    },
]

def obter_img(img_key):
    cfg = IMGS.get(img_key, IMGS["jason"])
    p = TMP/f"img_{img_key}.jpg"
    if p.exists() and p.stat().st_size > 20000: return p, cfg
    try:
        r = requests.get(cfg["url"], timeout=15)
        if r.status_code == 200 and len(r.content) > 10000:
            p.write_bytes(r.content); return p, cfg
    except: pass
    return None, cfg

def dur(path):
    r = subprocess.run(["ffprobe","-v","error","-show_entries","format=duration",
                        "-of","default=noprint_wrappers=1:nokey=1",str(path)],
                       capture_output=True, timeout=8)
    try: return float(r.stdout.strip())
    except: return 3.0

def tts(texto, voz, out):
    s = ". ".join(x.strip() for x in texto.replace('\n',' ').split('.') if x.strip())
    subprocess.run(["edge-tts",f"--voice={voz}","--rate=-12%",
                    f"--text={s}",f"--write-media={out}"],
                   capture_output=True, timeout=60)
    return pathlib.Path(out).exists()

def binaural(hz_str):
    if not hz_str: return None
    hz = int(re.sub(r'[^0-9]','',hz_str) or "528")
    ao = TMP/f"bi_{hz}.aac"
    if ao.exists() and ao.stat().st_size > 30000: return ao
    hr = hz + (4 if hz < 200 else 8)
    subprocess.run(["ffmpeg","-y","-f","lavfi","-i",f"sine=frequency={hz}:duration=600",
                    "-f","lavfi","-i",f"sine=frequency={hr}:duration=600",
                    "-filter_complex","[0:a]volume=0.04[l];[1:a]volume=0.04[r];[l][r]amerge=inputs=2[out]",
                    "-map","[out]","-c:a","aac","-b:a","128k",str(ao)],
                   capture_output=True, timeout=90)
    return ao if ao.exists() else None

def overlay(estilo, titulo, marca, hz_label, bright):
    t = titulo[:50].replace("'",r"\'")
    m = marca.replace("'",r"\'")
    hz = (hz_label or "").replace("'",r"\'")
    if estilo == "sleep":
        return (f"scale={W}:{H}:force_original_aspect_ratio=increase,crop={W}:{H},"
                f"colorchannelmixer=rr={bright}:gg={bright}:bb={bright},"
                f"drawbox=y=0:color=black@0.72:width=iw:height=130:t=fill,"
                f"drawbox=y=ih-80:color=black@0.72:width=iw:height=80:t=fill,"
                f"drawtext=text='{hz}':fontsize=66:fontcolor=#FFD700:x=(w-text_w)/2:y=12:bold=1:shadowcolor=#8B6914:shadowx=3:shadowy=3,"
                f"drawtext=text='BINAURAL · SOLFEGGIO':fontsize=22:fontcolor=#FCD34D@0.88:x=(w-text_w)/2:y=90,"
                f"drawtext=text='{t}':fontsize=28:fontcolor=white@0.9:x=(w-text_w)/2:y=h*0.79:shadowcolor=#000:shadowx=2:shadowy=2,"
                f"drawtext=text='{m}':fontsize=14:fontcolor=#94A3B8:x=(w-text_w)/2:y=h-52")
    elif estilo in ("focus","greenred"):
        cor = "#00CFFF" if estilo=="greenred" else "#00FF88"
        return (f"scale={W}:{H}:force_original_aspect_ratio=increase,crop={W}:{H},"
                f"colorchannelmixer=rr={bright}:gg={bright}:bb={bright},"
                f"drawbox=y=0:color=black@0.78:width=iw:height=120:t=fill,"
                f"drawbox=y=ih-80:color=black@0.78:width=iw:height=80:t=fill,"
                f"drawtext=text='{hz or '40Hz'}':fontsize=80:fontcolor={cor}:x=(w-text_w)/2:y=6:bold=1:shadowcolor=#001a00:shadowx=5:shadowy=5,"
                f"drawtext=text='GAMMA · BINAURAL · FOCUS':fontsize=18:fontcolor={cor}@0.9:x=(w-text_w)/2:y=96,"
                f"drawtext=text='{t}':fontsize=26:fontcolor=white:x=(w-text_w)/2:y=h*0.81:bold=1:shadowcolor=#000:shadowx=2:shadowy=2,"
                f"drawtext=text='{m}':fontsize=14:fontcolor=#86EFAC:x=(w-text_w)/2:y=h-52")
    elif estilo in ("dark","live_bold"):
        return (f"scale={W}:{H}:force_original_aspect_ratio=increase,crop={W}:{H},"
                f"colorchannelmixer=rr={bright}:gg={bright}:bb={bright},"
                f"drawbox=y=0:color=black@0.85:width=iw:height=105:t=fill,"
                f"drawbox=y=ih-80:color=black@0.85:width=iw:height=80:t=fill,"
                f"drawbox=x=16:y=20:color=#EF4444:width=13:height=13:t=fill,"
                f"drawtext=text='AO VIVO · Psychology':fontsize=18:fontcolor=#EF4444:x=38:y=16:bold=1,"
                f"drawtext=text='Science-Based Content':fontsize=15:fontcolor=#94A3B8:x=38:y=42,"
                f"drawtext=text='{t}':fontsize=34:fontcolor=white:x=(w-text_w)/2:y=h*0.38:bold=1:shadowcolor=#000:shadowx=3:shadowy=3,"
                f"drawtext=text='{m}':fontsize=14:fontcolor=#CBD5E1:x=(w-text_w)/2:y=h-52")
    elif estilo == "lofi":
        return (f"scale={W}:{H}:force_original_aspect_ratio=increase,crop={W}:{H},"
                f"colorchannelmixer=rr={bright}:gg={bright}:bb={bright},"
                f"drawbox=y=0:color=black@0.65:width=iw:height=90:t=fill,"
                f"drawbox=y=ih-70:color=black@0.65:width=iw:height=70:t=fill,"
                f"drawbox=x=16:y=16:color=#EF4444:width=10:height=10:t=fill,"
                f"drawtext=text='AO VIVO':fontsize=16:fontcolor=#EF4444:x=34:y=14:bold=1,"
                f"drawtext=text='lofi · psicologia · frequências':fontsize=14:fontcolor=#E8C49A@0.85:x=34:y=38,"
                f"drawtext=text='{t}':fontsize=26:fontcolor=white@0.9:x=(w-text_w)/2:y=h*0.83:shadowcolor=#000:shadowx=1:shadowy=1,"
                f"drawtext=text='{m}':fontsize=13:fontcolor=#E8C49A:x=(w-text_w)/2:y=h-44")
    else:  # psych / nature
        return (f"scale={W}:{H}:force_original_aspect_ratio=increase,crop={W}:{H},"
                f"colorchannelmixer=rr={bright}:gg={bright}:bb={bright},"
                f"drawbox=y=0:color=black@0.70:width=iw:height=100:t=fill,"
                f"drawbox=y=ih-80:color=black@0.70:width=iw:height=80:t=fill,"
                f"drawbox=x=16:y=20:color=#EF4444:width=10:height=10:t=fill,"
                f"drawtext=text='Psychology · Science':fontsize=18:fontcolor=#818CF8:x=36:y=17:bold=1,"
                f"drawtext=text='{t}':fontsize=30:fontcolor=white:x=(w-text_w)/2:y=h*0.42:bold=1:shadowcolor=#000:shadowx=2:shadowy=2,"
                f"drawtext=text='{m}':fontsize=14:fontcolor=#A5B4FC:x=(w-text_w)/2:y=h-52")

def render(img_p, audio_p, vf, d, out_p):
    subprocess.run(["ffmpeg","-y","-loop","1","-i",str(img_p),"-i",str(audio_p),
                    "-vf",vf,"-t",str(d),"-c:v","libx264","-preset","fast",
                    "-pix_fmt","yuv420p","-r","30","-c:a","aac","-b:a","128k",
                    "-shortest",str(out_p)], capture_output=True, timeout=300)
    return out_p.exists() and out_p.stat().st_size > 100000

def salvar(vid_id, titulo, frases, voz, mp4=""):
    if not SB_KEY: return
    script = "\n".join(frases)
    requests.post(f"{SB_URL}/rest/v1/en_channel_queue", headers=SBH,
        json={"titulo_en":str(titulo)[:100],"script_en":script,"voz_en":voz,
              "canal_destino":"UCyCkIpsVgME9yCj_oXJFheA",
              "rpm_estimado":7.0,"status":"mp4_ready" if mp4 else "pending"},
        timeout=8)

def run():
    print("=== 9 SHORTS PT-BR — BANCO VIRAL ANALISADO ===\n")
    total = 0
    marca = "Daniela Coelho · Pesquisa em Psicologia"

    for s in SHORTS:
        print(f"\n[{s['id']}] {s['titulo'][:50]}")

        # Imagem do banco analisado
        img_p, img_cfg = obter_img(s["img"])
        if not img_p:
            print(f"  ⚠️ Imagem {s['img']} não disponível"); continue
        print(f"  📸 {s['img']}.jpg ✅ overlay:{img_cfg['overlay']}")

        # TTS
        texto = ". ".join(s["frases"])
        voz_p = TMP/f"voz_{s['id']}.mp3"
        ok = tts(texto, s["voz"], str(voz_p))
        if not ok: print("  ⚠️ TTS falhou"); salvar(s["id"],s["titulo"],s["frases"],s["voz"]); continue

        # Mix binaural
        fa = binaural(s.get("hz"))
        mix_p = TMP/f"mix_{s['id']}.aac"
        if fa and fa.exists():
            subprocess.run(["ffmpeg","-y","-i",str(voz_p),"-i",str(fa),
                "-filter_complex","[0:a]volume=1[v];[1:a]volume=0.12[f];[v][f]amix=inputs=2:duration=first[out]",
                "-map","[out]","-c:a","aac","-b:a","128k",str(mix_p)],
                capture_output=True, timeout=60)
        else: mix_p = voz_p

        d = min(dur(mix_p)+0.5, 59.0)
        vf = overlay(img_cfg["overlay"], s["titulo"], marca, s.get("hz"), img_cfg["br"])
        out_p = TMP/f"short_{s['id']}.mp4"
        ok2 = render(img_p, mix_p, vf, d, out_p)

        if ok2:
            sz = out_p.stat().st_size//1024
            print(f"  🎬 {out_p.name} {sz}KB ✅ ({d:.1f}s)")
            total += 1
            salvar(s["id"], s["titulo"], s["frases"], s["voz"], str(out_p))
        else:
            print(f"  📝 salvo Supabase (render falhou)")
            salvar(s["id"], s["titulo"], s["frases"], s["voz"])
        time.sleep(2)

    print(f"\n{'='*50}")
    print(f"  🎬 {total}/9 shorts renderizados")
    print(f"  📸 Banco: 9 imagens virais analisadas")
    print(f"  Estilos: Meditative·Psych2Go·Lofi·Greenred·Dark·Jason")
    print("="*50)

if __name__=="__main__":
    run()
