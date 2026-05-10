#!/usr/bin/env python3
"""Gera scripts cinematograficos direto via Groq, sem passar por Edge Functions.
Pega ate 3 pipelines pending_generation com voice_profile_required atribuido.
Marca como script_ready apos sucesso.
"""
import os, json, urllib.request, urllib.error

SBU = os.environ["SUPABASE_URL"].rstrip("/")
SBK = os.environ["SUPABASE_SERVICE_KEY"]
GROQ = os.environ["GROQ_API_KEY"]
H_SB = {"apikey": SBK, "Authorization": f"Bearer {SBK}"}

def http(url, method="GET", body=None, headers=None, timeout=120):
    h = dict(headers or {})
    data = None
    if body:
        data = json.dumps(body).encode()
        h["Content-Type"] = "application/json"
    req = urllib.request.Request(url, data=data, method=method, headers=h)
    try:
        with urllib.request.urlopen(req, timeout=timeout) as r:
            return r.status, r.read().decode()
    except urllib.error.HTTPError as e:
        return e.code, e.read().decode() if e.fp else str(e)
    except Exception as e:
        return 0, str(e)

def groq_generate(system, user, max_tokens=8000):
    s, body = http("https://api.groq.com/openai/v1/chat/completions", "POST",
        body={
            "model": "llama-3.3-70b-versatile",
            "messages":[{"role":"system","content":system},{"role":"user","content":user}],
            "max_tokens": max_tokens, "temperature": 0.7
        },
        headers={"Authorization": f"Bearer {GROQ}"}, timeout=180)
    if s == 200:
        d = json.loads(body)
        return d["choices"][0]["message"]["content"]
    print(f"[groq] err {s}: {body[:200]}")
    return None

def main():
    # Pega 3 pipelines pending_generation cinematograficos
    s, raw = http(f"{SBU}/rest/v1/content_pipeline?status=eq.pending_generation&metadata->>eternal_brain_decision=eq.CINEMATIC_RESET_2026-05-10&order=id.desc&limit=3&select=id,title,target_platform,metadata", headers=H_SB)
    if s != 200:
        print(f"[err] supabase fetch {s}: {raw[:200]}"); return
    pipes = json.loads(raw)
    print(f"[gen] {len(pipes)} pipelines cinematograficos pending")

    for p in pipes:
        pid, title, plat, meta = p["id"], p["title"], p["target_platform"], p.get("metadata",{}) or {}
        voz = meta.get("voice_profile_required","feminina_calma_lenta")
        serie_nome = meta.get("serie_nome","Decifre a Mente")
        mirror_canal = meta.get("mirror_canal_origem","Psych2Go")
        mirror_hook = meta.get("mirror_hook_3s","")
        topico = meta.get("topic_seed","psicologia")

        # Calcular duracao alvo
        is_short = plat in ("youtube_shorts","instagram_reels","tiktok_short","pinterest_pin")
        target_min = 1 if is_short else 20
        target_chars = 800 if is_short else 14000  # ~55s / ~16min

        system = f"""Voce eh um roteirista de psicologia/saude mental do canal Daniela Coelho.
Estilo: cinematografico LENTO PROFUNDO CALMO (estilo Psych2Go narrado por Amanda Silvera).
Voz alvo: {voz} - tom hipnotico que prende atencao 2.5min sem dropoff.
Serie: {serie_nome}.
Inspiracao espelho: {mirror_canal} (NAO mencionar o nome).
Hook 3s ouro: {mirror_hook}.

REGRAS NARRACAO:
- Ritmo lento: pausas dramaticas entre frases.
- Frases curtas (max 18 palavras).
- Vocabulario emocional: "voce ja se sentiu...", "imagine que...", "talvez voce reconheca...".
- ZERO mencao a outros canais ou marcas concorrentes.
- ZERO diagnostico medico - apenas educativo.
- Hook nos primeiros 3 segundos = pergunta paradoxal ou afirmacao perturbadora.
- Estrutura: HOOK 5s + DOR/RECONHECIMENTO + N PONTOS PRINCIPAIS + RESOLUCAO + CTA.
- Saida: APENAS o roteiro corrido em portugues BR, sem cabecalhos, sem [tags], sem markdown."""

        user_prompt = f"""Topico: {topico}
Titulo: {title}
Duracao alvo: {target_min} minutos ({target_chars} caracteres aproximadamente).
Plataforma: {plat}.

Gere o roteiro completo agora, em portugues BR cinematografico, narrado em primeira pessoa para o ouvinte. Comece IMEDIATAMENTE com o hook de 3 segundos."""

        print(f"\n[gen] pipeline #{pid}: '{title[:60]}...' (voz={voz}, alvo={target_chars}c)")
        script = groq_generate(system, user_prompt, max_tokens=8000)
        if not script:
            print(f"[gen] #{pid} falhou"); continue
        
        script = script.strip()
        if len(script) < 500:
            print(f"[gen] #{pid} script muito curto ({len(script)}c) - skip"); continue
        
        # Atualizar pipeline: status=script_ready + script
        s_up, body_up = http(f"{SBU}/rest/v1/content_pipeline?id=eq.{pid}", "PATCH",
            body={"status":"script_ready", "script": script,
                  "metadata": {**meta,
                               "script_generated_chars": len(script),
                               "script_generated_at_iso": "2026-05-10T14:00:00Z",
                               "script_generated_via": "groq_direct_cinematic_no_edge_function"}},
            headers={**H_SB, "Prefer":"return=minimal"})
        print(f"[gen] #{pid} -> script_ready ({len(script)}c) update={s_up}")

if __name__ == "__main__":
    main()
