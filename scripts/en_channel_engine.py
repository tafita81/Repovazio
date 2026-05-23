#!/usr/bin/env python3
"""
en_channel_engine.py
Traduz scripts PT-BR → EN + narra com Edge TTS EN + gera vídeo
Canal EN = mesma produção, CPM $8-15 vs $1-3 BR = 5-8x mais renda
"""
import os, asyncio, subprocess, json, requests
from pathlib import Path

GROQ_KEY = os.getenv("GROQ_API_KEY", "")
SBU = os.getenv("SUPABASE_URL", "https://tpjvalzwkqwttvmszvie.supabase.co")
SBK = os.getenv("SUPABASE_SERVICE_KEY", "")

EN_VOICES = [
    "en-US-JennyNeural",     # feminina natural EN-US
    "en-US-GuyNeural",       # masculina natural EN-US
    "en-GB-SoniaNeural",     # feminina British English
    "en-AU-NatashaNeural",   # australiana — mercado Oceania
]

TEMAS_EN = [
    ("covert narcissism", "5 Signs Nobody Talks About"),
    ("anxious attachment", "Why We Sabotage Good Relationships"),
    ("childhood trauma", "How It Shows Up in Adults"),
    ("imposter syndrome", "What Harvard Research Actually Says"),
    ("smiling depression", "When Pain Becomes Invisible"),
    ("emotional burnout", "The Science of Real Exhaustion"),
    ("gaslighting", "How to Recognize and Break Free"),
    ("emotional boundaries", "Healthy vs Isolation"),
]

def traduzir_groq(texto_pt, tema_en):
    if not GROQ_KEY:
        return None
    prompt = f"""Translate this psychology script from Brazilian Portuguese to American English.
Keep the same structure, tone, and scientific references.
The topic is: {tema_en}
Make it sound like a natural American psychology podcast host — warm, direct, science-based.
Preserve [pause] markers and emotional beats.
Return ONLY the translated script.

ORIGINAL:
{texto_pt[:3000]}"""
    try:
        r = requests.post("https://api.groq.com/openai/v1/chat/completions",
            headers={"Authorization": f"Bearer {GROQ_KEY}", "Content-Type": "application/json"},
            json={"model": "llama-3.3-70b-versatile",
                  "messages": [{"role": "user", "content": prompt}],
                  "max_tokens": 2000, "temperature": 0.7},
            timeout=60)
        if r.status_code == 200:
            return r.json()["choices"][0]["message"]["content"]
    except: pass
    return None

def gerar_script_en(tema, subtitulo):
    if not GROQ_KEY: return None
    prompt = f"""You are Dr. Sarah Mitchell, a Harvard-trained psychologist with a popular podcast.
Write a complete 8-10 minute podcast script about: {tema} — {subtitulo}

STRUCTURE:
[HOOK 30s] - counter-intuitive opening fact
[REAL CASE 90s] - anonymous clinical vignette
[SCIENCE 2min] - cite real researchers: Malkin, van der Kolk, Gottman, Neff, Siegel
[5 SIGNS 3min] - non-obvious, specific behavioral patterns
[WHAT TO DO 90s] - 3 concrete, actionable steps
[OUTRO 30s] - powerful closing + next episode tease

TONE: Two smart friends talking. Direct, warm, evidence-based. American English.
Use [pause] for natural pauses.
Return ONLY the script."""
    try:
        r = requests.post("https://api.groq.com/openai/v1/chat/completions",
            headers={"Authorization": f"Bearer {GROQ_KEY}", "Content-Type": "application/json"},
            json={"model": "llama-3.3-70b-versatile",
                  "messages": [{"role": "user", "content": prompt}],
                  "max_tokens": 2000, "temperature": 0.75},
            timeout=60)
        if r.status_code == 200:
            return r.json()["choices"][0]["message"]["content"]
    except: pass
    return None

async def narrar_en(texto, arquivo, voz="en-US-JennyNeural"):
    try:
        import edge_tts
        texto_limpo = texto.replace("[pause]", " . ").replace("[HOOK]", "").replace("[SCIENCE]", "").replace("[SIGNS]", "").replace("[OUTRO]", "")
        communicate = edge_tts.Communicate(texto_limpo[:5000], voz, rate="+8%")
        await communicate.save(arquivo)
        return True
    except Exception as e:
        print(f"EdgeTTS EN erro: {e}")
        return False

def run():
    import time
    tema_idx = int(os.getenv("TEMA_IDX", "0")) % len(TEMAS_EN)
    tema, subtitulo = TEMAS_EN[tema_idx]
    voz = os.getenv("EN_VOICE", "en-US-JennyNeural")
    
    print(f"=== EN CHANNEL — {tema}: {subtitulo} ===")
    out_dir = Path(os.getenv("GITHUB_WORKSPACE", ".")) / "output" / "en_channel"
    out_dir.mkdir(parents=True, exist_ok=True)
    
    # Gerar script EN
    print("1. Gerando script EN via Groq...")
    script = gerar_script_en(tema, subtitulo)
    if script:
        script_path = out_dir / f"en_ep{tema_idx+1:02d}_{tema.replace(' ','_')}.md"
        with open(script_path, "w") as f:
            f.write(f"# {tema.title()} — {subtitulo}\n\n{script}")
        print(f"   Script salvo: {script_path.name}")
        
        # Narrar EN
        print(f"2. Narrando com Edge TTS {voz}...")
        narr = str(out_dir / f"en_ep{tema_idx+1:02d}_{tema.replace(' ','_')}.mp3")
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        ok = loop.run_until_complete(narrar_en(script, narr, voz))
        if ok:
            print(f"   Narração: {narr}")
    else:
        print("   Groq indisponível — script não gerado")

if __name__ == "__main__":
    run()
