#!/usr/bin/env python3
"""
en_channel_engine.py — Canal EN Automático
Cruzamento: DeepL (500K chars/mes gratis) + LibreTranslate (no-auth backup) + Edge TTS EN

IDEIA ÚNICA: Cada vídeo PT-BR do psicologia.doc é automaticamente:
1. Traduzido para EN (DeepL 500K grátis/mês)
2. Narrado em inglês (Edge TTS en-US-GuyNeural)
3. Publicado no canal EN faceless

5 canais de receita do mesmo conteúdo. RPM EN = 3-10x BR.
"""

import requests, os, asyncio
from datetime import datetime

DEEPL_KEY = os.getenv("DEEPL_API_KEY","")
SB_URL    = os.getenv("SUPABASE_URL","https://tpjvalzwkqwttvmszvie.supabase.co")
SB_KEY    = os.getenv("SUPABASE_SERVICE_ROLE_KEY","")

def traduzir_deepl(texto: str, idioma_alvo: str = "EN-US") -> str:
    """DeepL API — 500K chars/mês grátis"""
    if not DEEPL_KEY: return traduzir_libre(texto)
    
    r = requests.post("https://api-free.deepl.com/v2/translate",
        headers={"Authorization": f"DeepL-Auth-Key {DEEPL_KEY}"},
        json={"text": [texto], "target_lang": idioma_alvo, "source_lang": "PT"},
        timeout=30)
    
    if r.status_code == 200:
        return r.json()["translations"][0]["text"]
    return traduzir_libre(texto)

def traduzir_libre(texto: str) -> str:
    """LibreTranslate backup — gratuito, sem auth"""
    try:
        r = requests.post("https://libretranslate.com/translate",
            json={"q": texto, "source": "pt", "target": "en", "format": "text"},
            timeout=20)
        if r.status_code == 200:
            return r.json().get("translatedText", texto)
    except:
        pass
    return texto

async def narrar_en(texto: str, output_path: str, voz: str = "en-US-GuyNeural"):
    """Narrar em inglês com Edge TTS — gratuito, ilimitado"""
    import edge_tts
    communicate = edge_tts.Communicate(texto, voz)
    await communicate.save(output_path)

def processar_video_ptbr(video_id: str, script_ptbr: str, titulo_ptbr: str) -> dict:
    """Traduz e prepara versão EN de um video PT-BR"""
    
    # 1. Traduzir título
    titulo_en = traduzir_deepl(titulo_ptbr)
    
    # 2. Traduzir script
    script_en = traduzir_deepl(script_ptbr)
    
    # 3. Adaptar titulo para EN (mais clickbait)
    # Padrões que funcionam em EN:
    titulo_en_viral = titulo_en
    if "Narcisismo" in titulo_ptbr:
        titulo_en_viral = titulo_en.replace("Narcissism", "Covert Narcissism")
    
    resultado = {
        "video_id_ptbr": video_id,
        "titulo_en": titulo_en_viral,
        "script_en": script_en[:500],
        "voz_en": "en-US-GuyNeural",
        "canal_destino": "EN Psychology Channel (faceless)",
        "rpm_estimado": "$5-15 USD",
        "status": "traduzido",
        "data": datetime.now().isoformat()
    }
    
    # Salvar no Supabase
    if SB_KEY:
        requests.post(f"{SB_URL}/rest/v1/en_channel_queue",
            headers={"apikey": SB_KEY, "Authorization": f"Bearer {SB_KEY}",
                     "Content-Type": "application/json"},
            json=resultado, timeout=15)
    
    return resultado

if __name__ == "__main__":
    # Testar com o video #683
    resultado = processar_video_ptbr(
        "683",
        "O narcisista mais perigoso não humilha. Ele faz você se sentir culpada por machucá-lo.",
        "Narcisismo Encoberto: Os 7 Sinais Que Ele Está Te Manipulando Sem Você Perceber"
    )
    print(f"EN Title: {resultado['titulo_en']}")
    print(f"Status: {resultado['status']}")
