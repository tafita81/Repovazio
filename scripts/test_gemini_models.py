import requests, os, json, base64

GEMINI_KEY = os.environ.get("GEMINI_API_KEY", "AIzaSyBhd3vwMkFJ2dSfnbHNVtNJvgpiZtX0j1Q")

# Testar os modelos disponíveis para image generation
models_to_try = [
    "gemini-2.0-flash-preview-image-generation",
    "gemini-2.0-flash-exp-image-generation", 
    "imagen-3.0-generate-002",
    "gemini-2.0-flash-exp",
]

print("🔍 Testando modelos Gemini para geração de imagem...")
prompt_text = "chibi anime girl, kawaii style, psych2go style, mint-green blouse, short dark hair, cream background"

for model in models_to_try:
    try:
        # Testar generate content
        url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={GEMINI_KEY}"
        payload = {
            "contents": [{"parts": [{"text": prompt_text}]}],
            "generationConfig": {"responseModalities": ["IMAGE", "TEXT"]}
        }
        r = requests.post(url, json=payload, timeout=30)
        status = r.status_code
        
        if status == 200:
            data = r.json()
            has_image = any(
                "inlineData" in part
                for cand in data.get("candidates", [])
                for part in cand.get("content", {}).get("parts", [])
            )
            print(f"  ✅ {model}: {status} | imagem={'SIM' if has_image else 'NÃO'}")
            if has_image:
                # Salvar para verificar
                for cand in data.get("candidates", []):
                    for part in cand.get("content", {}).get("parts", []):
                        if "inlineData" in part:
                            raw = base64.b64decode(part["inlineData"]["data"])
                            with open(f'/tmp/test_{model.replace("-","_")}.jpg', 'wb') as f:
                                f.write(raw)
                            print(f"       → Imagem: {len(raw)//1024}KB salva")
        elif status == 404:
            print(f"  ❌ {model}: modelo não existe")
        elif status == 400:
            err = r.json().get("error", {}).get("message", "")[:100]
            print(f"  ⚠️  {model}: 400 — {err}")
        elif status == 429:
            print(f"  ⏳ {model}: rate limit")
        else:
            print(f"  ❓ {model}: {status}")
    except Exception as e:
        print(f"  💥 {model}: {str(e)[:60]}")

# Testar Imagen separado
print("\n🖼️  Testando Imagen 3...")
try:
    url2 = f"https://generativelanguage.googleapis.com/v1beta/models/imagen-3.0-generate-002:predict?key={GEMINI_KEY}"
    r2 = requests.post(url2, json={
        "instances": [{"prompt": prompt_text}],
        "parameters": {"sampleCount": 1, "aspectRatio": "9:16"}
    }, timeout=30)
    print(f"  Imagen 3: {r2.status_code} | {r2.text[:150]}")
except Exception as e:
    print(f"  Imagen 3: {e}")

