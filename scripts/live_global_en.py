#!/usr/bin/env python3
"""
live_global_en.py — 24/7 English Stream targeting USA/UK/AU/CA
CPM target: $15-50 | Keywords: 528hz sleep, anxiety psychology, healing frequency

Model: Meditative Mind ($50K/mo) + Therapy in a Nutshell ($40K/mo)
"""
import os, time, subprocess, pathlib, requests, textwrap, hashlib, threading
from datetime import datetime, timezone, timedelta

STREAM_KEY = os.getenv("YOUTUBE_STREAM_KEY_EN", os.getenv("YOUTUBE_STREAM_KEY", ""))
GROQ_KEY   = os.getenv("GROQ_API_KEY", "")
RTMP_URL   = f"rtmp://a.rtmp.youtube.com/live2/{STREAM_KEY}"
W, H = 1280, 720
TMP = pathlib.Path("/tmp/live_en")
TMP.mkdir(exist_ok=True)

# ─── 4 STREAMS BY HOUR (UTC) — optimized for USA/UK audiences ───────────
STREAMS_EN = {
    "sleep": {
        "hz": 528, "hz_right": 532, "hz_base": 174,
        "utc_hours": [0,1,2,3,4,5,6,7,8,9],   # midnight-9am USA EST
        "title": "🔴 528Hz SLEEP MUSIC | Anxiety & Attachment Healing | Psychology LIVE",
        "color": "#050515", "text_color": "#818CF8",
        "brand": "Sarah Mitchell · Behavioral Research & Psychology",
        "cta": "Free AI Companion: daniela-ia.vercel.app",
        "content": [
            ("Anxious Attachment & Sleep", "Anxious attachment hyperactivates the amygdala during sleep — explaining 3am rumination. Not weakness. Biology. — Ainsworth/Siegel"),
            ("Cortisol & Insomnia", "Chronic anxiety raises cortisol, which suppresses melatonin. 40% of anxious people have measurable sleep disruption. — Sapolsky/Stanford"),
            ("Narcissism Recovery", "Leaving a narcissistic relationship takes 3.5 years average for the nervous system to recalibrate. — Malkin/Harvard"),
            ("528Hz DNA Repair", "528Hz has been linked to reduced stress hormones and increased wellbeing markers in peer-reviewed research. — NCBI 2019"),
            ("Trauma & REM", "Unprocessed trauma disrupts REM cycles. The body rehearses threats during sleep. — van der Kolk/Boston"),
            ("Secure Attachment & Rest", "Securely attached people sleep 1.2 hours more on average. The nervous system regulates more easily. — Johnson/EFT"),
            ("Gaslighting Recovery", "After gaslighting, trusting your own perception takes time. The nervous system needs corrective experiences. — Freyd/Oregon"),
            ("Impostor Syndrome 3am", "3am self-doubt is cognitive, not realistic. Dunning-Kruger: the most competent doubt most. Not a signal — noise."),
        ]
    },
    "focus": {
        "hz": 40, "hz_right": 40, "hz_base": 10,
        "utc_hours": [10,11,12,13,14,15,16],    # morning USA EST
        "title": "🔴 40Hz FOCUS | ADHD & Procrastination | Psychology & Neuroscience LIVE",
        "color": "#020F02", "text_color": "#34D399",
        "brand": "Sarah Mitchell · Behavioral Research & Psychology",
        "cta": "Interview Coach AI: interview-assistant-pro-sigma.vercel.app",
        "content": [
            ("40Hz Gamma & ADHD", "40Hz gamma stimulation improves working memory by 23% in adults with ADHD. — MIT Lincoln Lab 2024"),
            ("Procrastination Is Pain", "Procrastination activates the anterior cingulate cortex — the same region processing physical pain. — Sirois/Sheffield"),
            ("Dopamine & ADHD", "ADHD is dopamine dysregulation, not attention failure. The task must activate the reward circuit first. — Barkley"),
            ("Flow State Neuroscience", "In flow, the prefrontal cortex partially deactivates. You think less and do more — paradoxically. — Csikszentmihalyi"),
            ("Gamma Waves & Memory", "Gamma oscillations (40Hz) are associated with high-speed information processing and long-term potentiation. — Davidson/Wisconsin"),
            ("ADHD & Self-Compassion", "Harsh self-criticism worsens ADHD symptoms. Self-compassion improves executive function measurably. — Neff"),
            ("Ultradian Rhythm", "25min focus + 5min rest matches the brain's natural ultradian cycle. Not a technique — biology. — Kleitman"),
            ("Rejection Sensitive Dysphoria", "Emotional dysregulation in ADHD often includes intense fear of rejection — underdiagnosed but common. — Dodson"),
        ]
    },
    "healing": {
        "hz": 432, "hz_right": 439, "hz_base": 136,
        "utc_hours": [17,18,19],                 # afternoon USA EST
        "title": "🔴 432Hz HEALING | Narcissism, Trauma & Recovery | Psychology LIVE",
        "color": "#0A0218", "text_color": "#C4B5FD",
        "brand": "Sarah Mitchell · Behavioral Research & Psychology",
        "cta": "Free AI Wellness: daniela-ia.vercel.app",
        "content": [
            ("Covert Narcissism", "The most dangerous narcissist doesn't seem arrogant. They seem like the biggest victim. — Malkin/Harvard"),
            ("Trauma & the Body", "Trauma isn't just memory — it's nervous system reorganization. The body keeps the score. — van der Kolk"),
            ("432Hz Natural Tuning", "432Hz is mathematically aligned with natural resonance: Verdi's tuning, geometric harmony, Schumann resonance."),
            ("Self-Compassion & Healing", "8 weeks of self-compassion practice measurably increases prefrontal cortex volume. — Neff/Germer"),
            ("Boundary vs. Wall", "A boundary has language. A wall has silence. They protect differently. — Tawwab"),
            ("Theta Waves & Memory", "Theta oscillations (4-8Hz) — present during 432Hz meditation — are critical for emotional memory consolidation."),
            ("Complex Trauma Recovery", "Complex trauma recovery isn't linear. The nervous system learns safety through repeated corrective experience."),
            ("Anxious Attachment Patterns", "Texting obsessively, testing partners, fusion — not character flaws. Nervous system learning from early inconsistency."),
        ]
    },
    "prime": {
        "hz": 963, "hz_right": 971, "hz_base": 396,
        "utc_hours": [20,21,22,23],              # evening USA EST = peak CPM
        "title": "🔴 963Hz LIBERATION | Anxiety, Gaslighting & Attachment LIVE | Psychology",
        "color": "#120008", "text_color": "#FB7185",
        "brand": "Sarah Mitchell · Behavioral Research & Psychology",
        "cta": "Interview Coach: interview-assistant-pro-sigma.vercel.app",
        "content": [
            ("Anxiety & Amygdala", "Your amygdala detects threats 33ms before conscious awareness. Not overreacting — biology at speed. — LeDoux/NYU"),
            ("Gaslighting Signs", "When you trust their version of reality more than yours, gaslighting has already worked. — Freyd"),
            ("Anxious Attachment Stats", "62% of adults have insecure attachment. Most never knew. It's the norm, not the exception. — Global Ainsworth Data"),
            ("963Hz & Activation", "963Hz is associated with activation, clarity, and reconnection with intuitive processing. — Solfeggio tradition"),
            ("Validation Addiction", "Likes activate the same reward circuit as cocaine. Variable ratio reinforcement — the most addictive schedule. — Skinner/Alter"),
            ("Covert Narcissism Recovery", "You don't need to understand why they did it. You need your nervous system to feel safe again."),
            ("Impostor Syndrome Peak", "The more competent you are, the more you know what you don't know. Impostor syndrome is metacognition."),
            ("Emotional Liberation", "Healing trauma isn't forgetting. It's the nervous system learning the threat has passed. — van der Kolk/Levine"),
        ]
    },
}

def utc_hour(): return datetime.now(timezone.utc).hour

def select_stream():
    h = utc_hour()
    for k, v in STREAMS_EN.items():
        if h in v["utc_hours"]: return k, v
    return "prime", STREAMS_EN["prime"]

def gen_audio(hz, hz_right, hz_base, mins=30):
    out = TMP / f"audio_{hz}hz_{mins}m.aac"
    if out.exists() and out.stat().st_size > 50000:
        return out
    dur = mins * 60
    cmd = ["ffmpeg", "-y",
        "-f","lavfi","-i",f"sine=frequency={hz}:duration={dur}",
        "-f","lavfi","-i",f"sine=frequency={hz_right}:duration={dur}",
        "-f","lavfi","-i",f"sine=frequency={hz_base}:duration={dur}",
        "-f","lavfi","-i",f"anoisesrc=color=pink:duration={dur}",
        "-filter_complex",
        f"[0:a]volume=0.035[l];"
        f"[1:a]volume=0.035[r];"
        f"[2:a]volume=0.012[b];"
        f"[3:a]volume=0.004[p];"
        "[l][r]amerge=inputs=2[bin];"
        "[bin][b][p]amix=inputs=3:duration=longest[out]",
        "-map","[out]","-c:a","aac","-b:a","192k","-ar","44100",str(out)]
    subprocess.run(cmd, capture_output=True, timeout=120)
    return out if out.exists() else None

def get_image(tema, color, seed):
    prompt = (f"masterpiece, ultra HD cinematic dark background, {tema} theme, "
              f"deep space aurora particles floating, extremely calming serene, "
              f"dark {color} tones, no text no people, healing atmosphere, 8k "
              f"### text watermark nsfw blurry people faces logos cluttered")
    url = (f"https://image.pollinations.ai/prompt/{requests.utils.quote(prompt[:400])}"
           f"?model=flux&width={W}&height={H}&seed={seed}&nologo=true")
    try:
        r = requests.get(url, timeout=60)
        if r.status_code == 200 and len(r.content) > 10000:
            return r.content
    except: pass
    return None

def groq_rephrase(text):
    if not GROQ_KEY or len(text) < 20: return text
    try:
        r = requests.post("https://api.groq.com/openai/v1/chat/completions",
            headers={"Authorization": f"Bearer {GROQ_KEY}", "Content-Type": "application/json"},
            json={"model": "llama-3.3-70b-versatile",
                  "messages": [{"role":"user","content":
                    f"Rephrase this psychology insight slightly differently. Max 95 chars. No quotes:\n{text}"}],
                  "max_tokens": 50, "temperature": 0.85}, timeout=10)
        if r.status_code == 200:
            return r.json()["choices"][0]["message"]["content"].strip()
    except: pass
    return text

def make_slide(img_path, cfg, tema, insight, idx, total, out_path):
    hz      = cfg["hz"]
    txt_c   = cfg["text_color"]
    brand   = cfg["brand"].replace("'", r"\'")
    cta     = cfg["cta"].replace("'", r"\'")
    tema_e  = tema.replace("'", r"\'")
    
    lines = textwrap.wrap(insight, 42)[:2]
    l1 = lines[0].replace("'", r"\'") if lines else ""
    l2 = lines[1].replace("'", r"\'") if len(lines) > 1 else ""
    prog_w = max(4, int(W * (idx / max(total, 1))))
    utc_now = datetime.now(timezone.utc).strftime("%H:%M UTC")
    
    vf = (
        f"scale={W}:{H}:force_original_aspect_ratio=increase,crop={W}:{H},"
        f"colorchannelmixer=rr=0.65:gg=0.65:bb=0.65,"
        f"drawbox=y=0:color=black@0.88:width=iw:height=66:t=fill,"
        f"drawbox=y=ih-70:color=black@0.92:width=iw:height=70:t=fill,"
        f"drawbox=y=ih-4:color={txt_c}@0.85:width={prog_w}:height=4:t=fill,"
        f"drawbox=x=12:y=16:color=#EF4444:width=10:height=10:t=fill,"
        f"drawtext=text='{hz}Hz':fontsize=22:fontcolor={txt_c}:x=30:y=12:bold=1:shadowcolor=black:shadowx=1:shadowy=1,"
        f"drawtext=text='LIVE':fontsize=13:fontcolor=#EF4444:x=30:y=38:bold=1,"
        f"drawtext=text='{tema_e}':fontsize=16:fontcolor={txt_c}@0.9:x=(w-text_w)/2:y=h*0.34:shadowcolor=black:shadowx=1:shadowy=1,"
        f"drawtext=text='{l1}':fontsize=25:fontcolor=white:x=(w-text_w)/2:y=h*0.41:bold=1:shadowcolor=#000:shadowx=2:shadowy=2,"
    )
    if l2:
        vf += f"drawtext=text='{l2}':fontsize=25:fontcolor=white:x=(w-text_w)/2:y=h*0.41+37:bold=1:shadowcolor=#000:shadowx=2:shadowy=2,"
    vf += (
        f"drawtext=text='{utc_now}':fontsize=12:fontcolor=#475569:x=w-90:y=20,"
        f"drawtext=text='{brand}':fontsize=12:fontcolor=#94A3B8:x=(w-text_w)/2:y=h-48,"
        f"drawtext=text='{cta}':fontsize=11:fontcolor={txt_c}@0.75:x=(w-text_w)/2:y=h-28"
    )
    cmd = ["ffmpeg","-y","-loop","1","-i",str(img_path),"-vf",vf,
           "-t","60","-c:v","libx264","-preset","fast","-tune","stillimage",
           "-pix_fmt","yuv420p","-r","30","-an",str(out_path)]
    subprocess.run(cmd, capture_output=True, timeout=180)
    return out_path.exists() and out_path.stat().st_size > 10000

def run():
    if not STREAM_KEY:
        print("YOUTUBE_STREAM_KEY_EN not set.")
        print("Add to GitHub Secrets: YOUTUBE_STREAM_KEY_EN")
        return
    
    key, cfg = select_stream()
    content  = cfg["content"]
    
    print(f"=== 🌍 GLOBAL EN LIVE 24/7 ===")
    print(f"    Stream: {key} | {cfg['hz']}Hz")
    print(f"    Title: {cfg['title'][:60]}...")
    print(f"    Targeting: USA/UK/AU/CA | CPM target: $15-50")
    print()
    
    audio = gen_audio(cfg["hz"], cfg["hz_right"], cfg["hz_base"])
    slides, concat_f = [], TMP / "pl_en.txt"
    
    print("Generating initial slides...")
    for i in range(4):
        tema, base = content[i % len(content)]
        seed = int(hashlib.md5(f"en_{key}_{i}".encode()).hexdigest()[:8], 16)
        insight  = groq_rephrase(base)
        img_data = get_image(tema, cfg["color"], seed)
        if not img_data: continue
        img_p = TMP / f"bg_{key}_{seed}.jpg"; img_p.write_bytes(img_data)
        sl = TMP / f"sl_{key}_{i}.mp4"
        if make_slide(img_p, cfg, tema, insight, i, len(content), sl):
            slides.append(sl)
            print(f"  ✅ [{i+1}] {tema[:40]}")
        time.sleep(2)
    
    if not slides: print("No slides generated."); return
    with open(concat_f, "w") as f:
        [f.write(f"file '{s.resolve()}'\n") for s in slides]
    
    print(f"\nStreaming to YouTube → {cfg['hz']}Hz {key.upper()}")
    
    audio_src = ["-stream_loop","-1","-i",str(audio)] if audio and audio.exists() \
                else ["-f","lavfi","-i",f"sine=frequency={cfg['hz']}:duration=999999"]
    
    proc = subprocess.Popen([
        "ffmpeg","-y",
        "-f","concat","-safe","0","-stream_loop","-1","-i",str(concat_f),
        *audio_src,
        "-c:v","libx264","-preset","veryfast","-tune","stillimage",
        "-b:v","3500k","-maxrate","3500k","-bufsize","7000k",
        "-g","60","-pix_fmt","yuv420p",
        "-c:a","aac","-b:a","192k","-ar","44100","-ac","2",
        "-f","flv", RTMP_URL
    ])
    
    def bg(start=4):
        idx = start
        while proc.poll() is None:
            time.sleep(55)
            tema, base = content[idx % len(content)]
            seed = int(hashlib.md5(f"en_{key}_{idx}".encode()).hexdigest()[:8], 16)
            insight  = groq_rephrase(base)
            img_data = get_image(tema, cfg["color"], seed)
            if img_data:
                img_p = TMP / f"bg_{key}_{seed}.jpg"; img_p.write_bytes(img_data)
                sl = TMP / f"sl_{key}_{idx}.mp4"
                if make_slide(img_p, cfg, tema, insight, idx % len(content), len(content), sl):
                    with open(concat_f, "a") as f: f.write(f"file '{sl.resolve()}'\n")
                    print(f"  + {tema[:35]}")
            for old in sorted(TMP.glob(f"sl_{key}_*.mp4"))[:-6]: old.unlink(missing_ok=True)
            idx += 1
    
    threading.Thread(target=bg, daemon=True).start()
    try: proc.wait()
    except KeyboardInterrupt: proc.terminate()

if __name__ == "__main__":
    run()
