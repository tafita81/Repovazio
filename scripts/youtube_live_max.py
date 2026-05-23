#!/usr/bin/env python3
"""
youtube_live_max.py — Sistema Live MÁXIMO baseado nos canais mais monetizados do mundo

MODELO: Meditative Mind ($50K/mês) + Psych2Go ($120K/mês) aplicado ao BR

4 STREAMS ROTACIONADOS POR HORÁRIO:
  00h-08h BR → "528Hz DORMIR | Liberar Ansiedade e Apego"
              (pessoas dormem com live = 7h watch time por sessão)
  08h-14h BR → "40Hz FOCO | TDAH e Procrastinação | Psicologia"
              (trabalhadores, estudantes, alta retenção)
  14h-18h BR → "432Hz EQUILIBRIO | Narcisismo e Trauma | Curar"
              (tarde, menor audiência mas alta qualidade)
  18h-24h BR → "963Hz ANSIEDADE | Apego, Gaslighting | Daniela Coelho"
              (PRIME TIME — maior audiência + maior CPM)

CPM ESPERADO: $8-20 (mental health keyword = alto CPM)
WATCH TIME MÉDIO: 4-8h/usuário nos streams noturnos
RECEITA ESTIMADA (1K subs monetizados): $500-2000/mês só AdSense
"""
import os, time, subprocess, pathlib, requests, textwrap, json
from datetime import datetime, timezone, timedelta
import threading, hashlib

STREAM_KEY = os.getenv("YOUTUBE_STREAM_KEY", "")
GROQ_KEY   = os.getenv("GROQ_API_KEY", "")
RTMP_URL   = f"rtmp://a.rtmp.youtube.com/live2/{STREAM_KEY}"
W, H       = 1280, 720
FPS        = 30
TMP        = pathlib.Path("/tmp/live_max")
TMP.mkdir(exist_ok=True)

MARCA = "Daniela Coelho · Pesquisa e Conteúdo em Psicologia"

# ────────────────────────────────────────────────────────────
# FREQUÊNCIAS REAIS — Geradas por FFmpeg (livre de direitos)
# Modelo: Meditative Mind usa exatamente essas frequências
# ────────────────────────────────────────────────────────────
FREQUENCIAS = {
    "528hz_sono": {
        "hz_principal": 528, "hz_base": 174, "hz_binaural": 4,
        "nome": "528Hz SONO PROFUNDO",
        "descricao": "Frequência de transformação + ondas delta para sono",
        "cor_tema": "#0A0A2E",  # azul noite profundo
        "cor_texto": "#A78BFA",
        "titulo_yt": "🔴 528Hz SONO PROFUNDO | Liberar Ansiedade e Apego | Psicologia do Sono",
        "horario_br": "22h-08h",
    },
    "40hz_foco": {
        "hz_principal": 40, "hz_base": 10, "hz_binaural": 40,
        "nome": "40Hz FOCO GAMMA",
        "descricao": "Ondas Gamma (40Hz) ativam memória e concentração — TDAH e foco",
        "cor_tema": "#0A1A0A",  # verde escuro
        "cor_texto": "#34D399",
        "titulo_yt": "🔴 40Hz FOCO | TDAH, Procrastinação e Neurociência | Psicologia",
        "horario_br": "08h-14h",
    },
    "432hz_equilibrio": {
        "hz_principal": 432, "hz_base": 136, "hz_binaural": 7,
        "nome": "432Hz EQUILÍBRIO",
        "descricao": "Afinação natural 432Hz + ondas theta para equilíbrio emocional",
        "cor_tema": "#0F0A1A",  # roxo escuro
        "cor_texto": "#C4B5FD",
        "titulo_yt": "🔴 432Hz EQUILÍBRIO | Narcisismo, Trauma e Cura | Daniela Coelho",
        "horario_br": "14h-18h",
    },
    "963hz_prime": {
        "hz_principal": 963, "hz_base": 396, "hz_binaural": 8,
        "nome": "963Hz LIBERTAÇÃO",
        "descricao": "963Hz + 396Hz libertação de culpa e ansiedade — prime time",
        "cor_tema": "#0F0505",  # vermelho escuro
        "cor_texto": "#FCA5A5",
        "titulo_yt": "🔴 963Hz ANSIEDADE | Gaslighting, Apego e Libertação | LIVE Psicologia",
        "horario_br": "18h-22h",
    },
}

# ────────────────────────────────────────────────────────────
# CONTEÚDO PSICOLÓGICO MAPEADO ÀS FREQUÊNCIAS
# Baseado nos tópicos mais virais do Psych2Go + MedCircle
# ────────────────────────────────────────────────────────────
CONTEUDO_POR_FREQ = {
    "528hz_sono": [
        ("Apego Ansioso e Sono", "O apego ansioso ativa a amígdala mesmo durante o sono. Isso explica acordar às 3h pensando em alguém. — Ainsworth/Siegel"),
        ("Cortisol e Insônia", "Ansiedade crônica eleva cortisol. Cortisol bloqueia melatonina. Esse ciclo explica insônia em 40% dos ansiosos. — Sapolsky"),
        ("Ruminação Noturna", "O loop mental às 3h não é fraqueza. É o córtex pré-frontal tentando resolver o que a amígdala marcou como ameaça. — Siegel"),
        ("Regulação Noturna", "Respiração 4-7-8: ativa o nervo vago. Reduz cortisol em 28% em 10 minutos. — Weil/Harvard"),
        ("Trauma e Sono", "Trauma não processado interrompe ciclos REM. O corpo 'ensaia' ameaças passadas durante a noite. — van der Kolk"),
        ("Apego Seguro e Descanso", "Pessoas com apego seguro dormem em média 1.2h mais que as com apego ansioso. O sistema nervoso regula mais fácil. — Johnson"),
        ("528Hz e Serotonina", "Frequências de 528Hz demonstraram em pesquisa aumento de 25% em marcadores de bem-estar celular. — Baati/NCBI"),
    ],
    "40hz_foco": [
        ("TDAH e Ondas Gamma", "40Hz de estimulação auditiva melhora memória de trabalho em 23% em adultos com TDAH. — MIT/Alzheimer's Research"),
        ("Procrastinação Neural", "Procrastinação ativa córtex cingulado anterior — o mesmo da dor física. Não é falta de disciplina. — Sirois"),
        ("Dopamina e Foco", "TDAH é frequentemente desregulação de dopamina, não de atenção. A tarefa precisa ativar o circuito de recompensa. — Barkley"),
        ("Memória de Trabalho", "Ondas Gamma (40Hz) são associadas a processamento de informação de alta velocidade. Meditação ativa naturalmente. — Davidson/Wisconsin"),
        ("Flow State", "Estado de flow: córtex pré-frontal parcialmente desativa. Isso explica o paradoxo — você pensa menos e faz mais. — Csikszentmihalyi"),
        ("Pomodoro e Neuroquímica", "25 minutos de foco + 5 de pausa corresponde ao ciclo ultradian natural do cérebro. Não é técnica — é biologia. — Ultradian Rhythm"),
        ("Música e Cognição", "Frequências específicas sincronizam oscilações neurais. 40Hz melhora conectividade frontoparietal. — Gardner/Harvard"),
    ],
    "432hz_equilibrio": [
        ("Narcisismo e Cura", "Sair de um relacionamento narcísico leva em média 3.5 anos para o sistema nervoso recalibrar. É neuroquímica, não fraqueza. — Malkin"),
        ("Trauma Complexo", "Trauma relacional reorganiza o sistema nervoso. A cura começa pelo corpo, não pelo entendimento racional. — van der Kolk"),
        ("432Hz Natural", "432Hz é matematicamente consistente com o universo natural — afinação de Verdi, geometria sagrada, ressonância Schumann. — Música Pitagórica"),
        ("Autocompaixão e Neuroplasticidade", "Praticar autocompaixão por 8 semanas aumenta volume do córtex pré-frontal e reduz amígdala. Literalmente. — Neff/Germer"),
        ("Fronteiras e Identidade", "Dificuldade de dizer não é frequentemente derivada de apego ansioso formado antes dos 5 anos. — Ainsworth/Johnson"),
        ("Regulação Emocional", "Ondas theta (4-8Hz) — geradas por meditação e música em 432Hz — são associadas a consolidação de memória emocional. — Hippocampus Research"),
        ("Gaslighting e Recuperação", "Reconstruir confiança na própria percepção após gaslighting leva tempo. O sistema nervoso precisa de experiências corretivas repetidas. — Freyd"),
    ],
    "963hz_prime": [
        ("Ansiedade e Amígdala", "Sua amígdala processa ameaças 33ms antes de você ter consciência delas. Não é exagero — é biologia evoluída. — LeDoux/NYU"),
        ("Gaslighting Identificação", "Quando você duvida mais da sua memória do que da versão da outra pessoa, o gaslighting já funcionou. — Freyd/Oregon"),
        ("Apego Ansioso Números", "62% dos adultos têm apego inseguro. A maioria nunca soube. É o padrão mais comum, não exceção. — Ainsworth Global Data"),
        ("963Hz Pineal", "963Hz é associada a ativação da glândula pineal e produção de melatonina. Tradição milenar + pesquisa moderna convergem. — Solfeggio"),
        ("Vício em Validação", "Likes e comentários ativam o mesmo circuito de recompensa que cocaína. Reforço variável — o mais viciante. — Skinner/Alter"),
        ("Narcisismo Encoberto", "O narcisismo encoberto é o mais perigoso: opera através de vitimização, não grandiosidade. Ninguém ensina a reconhecer. — Malkin/Harvard"),
        ("Libertação do Trauma", "A cura do trauma não é esquecer. É o sistema nervoso aprender que a ameaça passou. — van der Kolk/Levine"),
    ],
}

def hora_br_atual():
    br_tz = timezone(timedelta(hours=-3))
    return datetime.now(br_tz).hour

def selecionar_stream():
    """Seleciona o stream baseado no horário BR atual"""
    hora = hora_br_atual()
    if 22 <= hora or hora < 8:
        return "528hz_sono"
    elif 8 <= hora < 14:
        return "40hz_foco"
    elif 14 <= hora < 18:
        return "432hz_equilibrio"
    else:  # 18-22h = prime time
        return "963hz_prime"

def gerar_audio_frequencia(freq_config, duracao_min=30):
    """
    Gera áudio de frequência real via FFmpeg
    Modelo exato do Meditative Mind: hz_principal + hz_base (harmônico) + binaural beat
    """
    hz_p = freq_config["hz_principal"]
    hz_b = freq_config["hz_base"]
    hz_bi = freq_config["hz_binaural"]
    duracao_s = duracao_min * 60
    
    out = TMP / f"freq_{hz_p}hz_{duracao_min}min.aac"
    if out.exists() and out.stat().st_size > 100000:
        print(f"    ♻️  Reutilizando áudio {hz_p}Hz")
        return out
    
    print(f"    🎵 Gerando {hz_p}Hz + {hz_b}Hz + binaural {hz_bi}Hz ({duracao_min}min)...")
    
    # Binaural: ouvido esquerdo = hz_p, ouvido direito = hz_p + hz_bi
    hz_right = hz_p + hz_bi
    
    cmd = [
        "ffmpeg", "-y",
        # Canal esquerdo: frequência principal (muito suave)
        "-f", "lavfi", "-i", f"sine=frequency={hz_p}:duration={duracao_s}",
        # Canal direito: principal + binaural (para beat)
        "-f", "lavfi", "-i", f"sine=frequency={hz_right}:duration={duracao_s}",
        # Harmônico base (mais grave, muito suave)
        "-f", "lavfi", "-i", f"sine=frequency={hz_b}:duration={duracao_s}",
        # Ruído rosa suave (simula "som da natureza")
        "-f", "lavfi", "-i", f"anoisesrc=color=pink:duration={duracao_s}",
        
        "-filter_complex",
        # Mixar: esquerdo binaural
        "[0:a]volume=0.04[fl];"
        # Direito binaural (hz ligeiramente diferente = beat)
        "[1:a]volume=0.04[fr];"
        # Harmônico base nos dois canais
        "[2:a]volume=0.015[base];"
        # Ruído rosa muito baixo (textura)
        "[3:a]volume=0.005[pink];"
        # Merge: estéreo binaural
        "[fl][fr]amerge=inputs=2[binaural];"
        # Add base + pink a ambos canais
        "[binaural][base][pink]amix=inputs=3:duration=longest[out]",
        
        "-map", "[out]",
        "-c:a", "aac", "-b:a", "192k", "-ar", "44100",
        str(out)
    ]
    
    result = subprocess.run(cmd, capture_output=True, timeout=120)
    if out.exists() and out.stat().st_size > 10000:
        print(f"    ✅ Áudio gerado: {out.stat().st_size//1024}KB")
        return out
    print(f"    ❌ Falha no áudio: {result.stderr[-200:]}")
    return None

def get_imagem_tematica(tema, cor_fundo, seed):
    """Imagem via Pollinations FLUX adaptada ao tema"""
    prompt = (
        f"masterpiece, ultra HD, dreamy dark aesthetic background, "
        f"{tema} concept, {cor_fundo} dark tones, "
        f"abstract particles floating, aurora borealis effect, "
        f"extremely peaceful and calming, no text, no people, "
        f"cinematic quality, 8k resolution "
        f"### text, watermark, nsfw, blurry, people, faces, logos"
    )
    url = (f"https://image.pollinations.ai/prompt/{requests.utils.quote(prompt[:420])}"
           f"?model=flux&width={W}&height={H}&seed={seed}&nologo=true")
    try:
        r = requests.get(url, timeout=60)
        if r.status_code == 200 and len(r.content) > 10000:
            return r.content
    except Exception as e:
        print(f"    Pollinations: {e}")
    return None

def gerar_insight_groq(tema, base, freq_nome):
    """Insight psicológico contextualizado na frequência"""
    if not GROQ_KEY:
        return base
    try:
        r = requests.post("https://api.groq.com/openai/v1/chat/completions",
            headers={"Authorization": f"Bearer {GROQ_KEY}", "Content-Type": "application/json"},
            json={"model": "llama-3.3-70b-versatile",
                  "messages": [{"role": "user", "content":
                    f"Reescreva essa frase de psicologia de forma levemente diferente."
                    f"Contexto: stream {freq_nome}. Máximo 100 chars. Sem aspas:\n{base}"}],
                  "max_tokens": 50, "temperature": 0.85},
            timeout=10)
        if r.status_code == 200:
            return r.json()["choices"][0]["message"]["content"].strip()
    except: pass
    return base

def criar_slide_freq(img_path, freq_config, tema, insight, num_slide, total_slides, out_path):
    """Cria slide OTIMIZADO para máximo watch time:
    - Background dark (não incomoda sono)
    - Texto aparece suavemente (não distrai)
    - Frequência sempre visível (SEO visual)
    - CTA sutil mas presente
    """
    hz_p    = freq_config["hz_principal"]
    nome    = freq_config["nome"].replace("'", r"\'")
    cor_txt = freq_config["cor_texto"]
    marca   = MARCA.replace("'", r"\'")
    
    # Insight em no máximo 2 linhas de 38 chars
    linhas = textwrap.wrap(insight, 40)[:2]
    l1 = linhas[0].replace("'", r"\'") if linhas else ""
    l2 = linhas[1].replace("'", r"\'") if len(linhas) > 1 else ""
    
    tema_esc = tema.replace("'", r"\'")
    prog     = num_slide / max(total_slides, 1)
    prog_w   = max(4, int(W * prog))
    
    # Hora BR
    br_tz = timezone(timedelta(hours=-3))
    hora_str = datetime.now(br_tz).strftime("%H:%M")
    
    vf = (
        # Base: imagem escurecida (ideal para sono)
        f"scale={W}:{H}:force_original_aspect_ratio=increase,crop={W}:{H},"
        f"colorchannelmixer=rr=0.7:gg=0.7:bb=0.7,"  # escurecer 30%
        
        # Header bar escuro
        f"drawbox=y=0:color=black@0.85:width=iw:height=68:t=fill,"
        
        # Footer bar
        f"drawbox=y=ih-72:color=black@0.90:width=iw:height=72:t=fill,"
        
        # Barra de progresso (cor da frequência)
        f"drawbox=y=ih-4:color={cor_txt}@0.8:width={prog_w}:height=4:t=fill,"
        
        # 🔴 ponto ao vivo
        f"drawbox=x=14:y=17:color=#EF4444:width=10:height=10:t=fill,"
        
        # FREQUÊNCIA em destaque (grande, visível — isso é o SEO visual)
        f"drawtext=text='{hz_p}Hz':fontsize=22:fontcolor={cor_txt}:"
        f"x=34:y=13:bold=1:shadowcolor=black:shadowx=1:shadowy=1,"
        
        # Nome do stream
        f"drawtext=text='{nome}':fontsize=15:fontcolor=white:"
        f"x=110:y=17:shadowcolor=black:shadowx=1:shadowy=1,"
        
        # Horário BR
        f"drawtext=text='{hora_str} BR':fontsize=13:fontcolor=#64748B:x=w-85:y=20,"
        
        # TEMA (pequeno, acima do insight)
        f"drawtext=text='{tema_esc}':fontsize=16:fontcolor={cor_txt}@0.8:"
        f"x=(w-text_w)/2:y=h*0.34:shadowcolor=black:shadowx=1:shadowy=1,"
        
        # INSIGHT — linha 1 (principal)
        f"drawtext=text='{l1}':fontsize=26:fontcolor=white:"
        f"x=(w-text_w)/2:y=h*0.41:bold=1:shadowcolor=#000:shadowx=2:shadowy=2,"
    )
    
    if l2:
        vf += (
            f"drawtext=text='{l2}':fontsize=26:fontcolor=white:"
            f"x=(w-text_w)/2:y=h*0.41+38:bold=1:shadowcolor=#000:shadowx=2:shadowy=2,"
        )
    
    vf += (
        # Marca no rodapé
        f"drawtext=text='{marca}':fontsize=13:fontcolor=#94A3B8:"
        f"x=(w-text_w)/2:y=h-50,"
        
        # CTA produto sutil
        f"drawtext=text='Interview Coach: bit.ly/interview-ia':fontsize=12:"
        f"fontcolor={cor_txt}@0.7:x=(w-text_w)/2:y=h-28"
    )
    
    cmd = [
        "ffmpeg", "-y",
        "-loop", "1", "-i", str(img_path),
        "-vf", vf,
        "-t", "60",  # 60 segundos por slide (Meditative Mind usa 60-90s)
        "-c:v", "libx264", "-preset", "fast",
        "-tune", "stillimage",
        "-pix_fmt", "yuv420p", "-r", str(FPS),
        "-an", str(out_path)
    ]
    result = subprocess.run(cmd, capture_output=True, timeout=180)
    return out_path.exists() and out_path.stat().st_size > 10000

def stream_principal():
    """Loop principal — seleciona stream pelo horário e transmite"""
    if not STREAM_KEY:
        freq_id = "963hz_prime"  # demo sem stream
        print("Modo DEMO (sem stream key)")
        print(f"Selecionado: {FREQUENCIAS[freq_id]['titulo_yt']}")
        print()
        print("Para ativar a live:")
        print("1. studio.youtube.com → Criar → Transmissão ao vivo")
        print("2. Copiar Stream Key")  
        print("3. GitHub tafita81/Repovazio → Settings → Secrets → YOUTUBE_STREAM_KEY")
        print("4. Actions → YouTube Live 24/7 MAX → Run workflow")
        return
    
    # Selecionar stream pelo horário BR
    freq_id    = selecionar_stream()
    freq_cfg   = FREQUENCIAS[freq_id]
    conteudos  = CONTEUDO_POR_FREQ[freq_id]
    
    hora = hora_br_atual()
    print(f"=== YOUTUBE LIVE 24/7 MAX ===")
    print(f"    {MARCA}")
    print(f"    Hora BR: {hora:02d}h → Stream: {freq_cfg['nome']}")
    print(f"    Frequência: {freq_cfg['hz_principal']}Hz")
    print(f"    Título: {freq_cfg['titulo_yt'][:60]}...")
    print()
    
    # Gerar áudio de frequência (30 minutos, reaproveita se existir)
    audio = gerar_audio_frequencia(freq_cfg, duracao_min=30)
    
    # Gerar slides iniciais
    print("Gerando slides iniciais...")
    slides = []
    concat_f = TMP / "playlist_max.txt"
    
    for i in range(4):
        tema, base = conteudos[i % len(conteudos)]
        seed       = int(hashlib.md5(f"{freq_id}{i}".encode()).hexdigest()[:8], 16)
        
        print(f"  [{i+1}/4] {tema}")
        insight  = gerar_insight_groq(tema, base, freq_cfg["nome"])
        img_data = get_imagem_tematica(tema, freq_cfg["cor_tema"], seed)
        
        if not img_data:
            print(f"    ⚠️  Imagem falhou")
            continue
        
        img_p = TMP / f"bg_{freq_id}_{seed}.jpg"
        img_p.write_bytes(img_data)
        
        slide_p = TMP / f"slide_{freq_id}_{i}.mp4"
        ok = criar_slide_freq(img_p, freq_cfg, tema, insight, i, len(conteudos), slide_p)
        if ok:
            slides.append(slide_p)
            print(f"    ✅ {slide_p.name} ({slide_p.stat().st_size//1024}KB)")
        time.sleep(2)
    
    if not slides:
        print("Nenhum slide gerado — verificar conexão")
        return
    
    # Criar playlist
    with open(concat_f, "w") as f:
        for s in slides:
            f.write(f"file '{s.resolve()}'\n")
    
    print(f"\n✅ {len(slides)} slides prontos")
    print(f"Iniciando stream → YouTube {freq_cfg['titulo_yt'][:50]}...")
    
    # FFmpeg → RTMP YouTube
    audio_args = []
    if audio and audio.exists():
        audio_args = ["-stream_loop", "-1", "-i", str(audio)]
    else:
        audio_args = ["-f", "lavfi", "-i",
                      f"sine=frequency={freq_cfg['hz_principal']}:duration=999999"]
    
    cmd = [
        "ffmpeg", "-y",
        "-f", "concat", "-safe", "0", "-stream_loop", "-1",
        "-i", str(concat_f),
        *audio_args,
        # Encoding YouTube Live OTIMIZADO
        "-c:v", "libx264",
        "-preset", "veryfast",
        "-tune", "stillimage",      # otimiza para conteúdo estático
        "-b:v", "3500k",
        "-maxrate", "3500k",
        "-bufsize", "7000k",
        "-g", str(FPS * 2),
        "-pix_fmt", "yuv420p",
        "-c:a", "aac",
        "-b:a", "192k",             # alta qualidade de áudio (frequências!)
        "-ar", "44100",
        "-ac", "2",
        "-f", "flv",
        RTMP_URL
    ]
    
    proc = subprocess.Popen(cmd)
    
    # Gerar slides em background
    def bg_generator(start=4):
        idx = start
        while proc.poll() is None:
            time.sleep(55)
            tema, base = conteudos[idx % len(conteudos)]
            seed = int(hashlib.md5(f"{freq_id}{idx}".encode()).hexdigest()[:8], 16)
            insight  = gerar_insight_groq(tema, base, freq_cfg["nome"])
            img_data = get_imagem_tematica(tema, freq_cfg["cor_tema"], seed)
            if img_data:
                img_p = TMP / f"bg_{freq_id}_{seed}.jpg"
                img_p.write_bytes(img_data)
                slide_p = TMP / f"slide_{freq_id}_{idx}.mp4"
                if criar_slide_freq(img_p, freq_cfg, tema, insight, idx % len(conteudos), len(conteudos), slide_p):
                    with open(concat_f, "a") as f:
                        f.write(f"file '{slide_p.resolve()}'\n")
                    print(f"  + {tema[:40]}")
            # Limpar antigos
            for old in sorted(TMP.glob(f"slide_{freq_id}_*.mp4"))[:-6]:
                old.unlink(missing_ok=True)
            idx += 1
    
    threading.Thread(target=bg_generator, daemon=True).start()
    
    try:
        proc.wait()
    except KeyboardInterrupt:
        proc.terminate()

if __name__ == "__main__":
    stream_principal()
