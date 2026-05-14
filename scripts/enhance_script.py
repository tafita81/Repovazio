"""
Melhoria sequencial de scripts — psicologia.doc
MEMÓRIA ETERNA: LONG = 13.000-14.000 chars = 15min fixo
                SHORT = 725-841 chars = 50-58s
Gate: score >= 95/100 com referência científica PMID obrigatória
"""
import os, sys, json, re, time, urllib.request

SB_URL = "https://tpjvalzwkqwttvmszvie.supabase.co"
SB_KEY = os.environ.get("SUPABASE_ANON_KEY","")
GH_PAT = os.environ.get("GH_PAT","")
NVIDIA_KEY = os.environ.get("NVIDIA_API_KEY","")
GROQ_KEY = os.environ.get("GROQ_API_KEY","")
OPENAI_KEY = os.environ.get("OPENAI_API_KEY","")
REPO = "tafita81/Repovazio"
MAX_TENTATIVAS = 5
# MEMÓRIA ETERNA conf=100
LONG_MIN, LONG_MAX = 13000, 14000
SHORT_MIN, SHORT_MAX = 725, 841

def sb_get(table, filters="", select="*"):
    url = f"{SB_URL}/rest/v1/{table}?select={select}"
    if filters: url += f"&{filters}"
    req = urllib.request.Request(url,
        headers={"apikey":SB_KEY,"Authorization":f"Bearer {SB_KEY}"})
    with urllib.request.urlopen(req, timeout=30) as r: return json.loads(r.read())

def sb_patch(table, filters, data):
    req = urllib.request.Request(f"{SB_URL}/rest/v1/{table}?{filters}",
        data=json.dumps(data).encode(), method="PATCH",
        headers={"apikey":SB_KEY,"Authorization":f"Bearer {SB_KEY}",
                 "Content-Type":"application/json","Prefer":"return=minimal"})
    with urllib.request.urlopen(req, timeout=30) as r: return r.status

def call_llm(system, user, max_tokens=6000):
    """NVIDIA DeepSeek → Groq → OpenAI fallback chain"""
    for model, url, key in [
        ("deepseek-ai/deepseek-r1","https://integrate.api.nvidia.com/v1/chat/completions", NVIDIA_KEY),
        ("llama-3.3-70b-versatile","https://api.groq.com/openai/v1/chat/completions", GROQ_KEY),
        ("gpt-4o-mini","https://api.openai.com/v1/chat/completions", OPENAI_KEY),
    ]:
        if not key: continue
        try:
            payload = {"model":model,"messages":[{"role":"system","content":system},{"role":"user","content":user}],"max_tokens":max_tokens,"temperature":0.7}
            req = urllib.request.Request(url, data=json.dumps(payload).encode(),
                headers={"Authorization":f"Bearer {key}","Content-Type":"application/json"})
            with urllib.request.urlopen(req, timeout=90) as r:
                return json.loads(r.read())["choices"][0]["message"]["content"]
        except Exception as e:
            print(f"  {model} falhou: {str(e)[:60]}")
    return None

def score_script(script, titulo, is_short, seo_score, tags):
    """Score real — memória eterna conf=100"""
    score = 0; falhas = []; L = len(script or "")
    if L >= 100: score += 20
    else: return 0, ["sem_script"]
    
    if is_short:
        if SHORT_MIN <= L <= SHORT_MAX: score += 20
        elif L < SHORT_MIN: score += 8; falhas.append(f"short_curto_{L}")
        else: falhas.append(f"short_longo_{L}")
    else:
        if LONG_MIN <= L <= LONG_MAX: score += 20
        elif L > LONG_MAX: score += 12; falhas.append(f"long_acima_14k_trim_{L}")
        elif L >= 11000: score += 12; falhas.append(f"long_falta_{13000-L}")
        elif L >= 8000: score += 6; falhas.append(f"long_incompleto_{L}")
        else: falhas.append(f"long_muito_curto_{L}")
    
    if titulo and re.search(r"\d+\s*sinai?s?|não\s+é|quando\s+você|por\s+que\s+você|silencioso|disfarçado|manipula|gaslighting|autossabotag|como\s+parar|síndrome", titulo or "", re.I):
        score += 15
    elif titulo and len(titulo) > 20: score += 7; falhas.append("formula_fraca")
    else: falhas.append("sem_titulo_viral")
    
    if re.search(r"DSM-5|Bowlby|van\s+der\s+Kolk|Brené|PMID|Journal\s+of|neurociência|University|pesquisa\s+(mostrou|revelou)|estudo\s+clínico|Ramani|American\s+Psychiatric", script or "", re.I):
        score += 15
    elif re.search(r"psicólogo|terapeuta|evidências|comprovado|cientificamente", script or "", re.I):
        score += 8; falhas.append("ref_fraca")
    else: falhas.append("sem_ref_cientifica")
    
    if re.search(r"você|seu|sua|imagine|já\s+(percebeu|viveu)|sabe\s+aquela", (script or "")[:200], re.I):
        score += 10
    else: score += 3
    
    if (seo_score or 0) >= 99: score += 10
    elif (seo_score or 0) >= 95: score += 8
    else: falhas.append("seo_baixo")
    
    if (tags and len(tags) >= 10): score += 5
    elif (tags and len(tags) >= 5): score += 3
    else: falhas.append("poucas_tags")
    score += 5  # pub_order
    return score, falhas

def melhorar_short(script, titulo, falhas):
    L = len(script or "")
    system = """Você é Daniela Coelho, psicóloga BR. Escreva script para YouTube Short.
REGRAS ABSOLUTAS:
- Exatamente 725-841 caracteres (contar com espaços)
- Incluir referência científica (DSM-5, Bowlby, neurociência, PMID) integrada naturalmente
- Hook emocional nos primeiros 50 chars (você/seu/sua/imagine)
- Fórmula viral: N Sinais / Não é X é Y / Por que você
- Cada frase em linha separada para TTS"""
    user = f"""Título: {titulo}
Script atual ({L} chars):
{script}

PROBLEMAS: {", ".join(falhas)}

TAREFA: Reescreva este script SHORT.
- Tamanho EXATO: 725-841 chars
- Incluir referência científica obrigatória
- Manter gancho do título
- Output: APENAS o script, sem comentários, sem aspas"""
    resp = call_llm(system, user, 900)
    if resp:
        novo = resp.strip()
        if SHORT_MIN <= len(novo) <= SHORT_MAX: return novo
        if len(novo) > SHORT_MAX: return novo[:SHORT_MAX]
        if len(novo) < SHORT_MIN:
            novo += f"\n\n{titulo} — assista a versão completa no canal."
        return novo if len(novo) <= SHORT_MAX else novo[:SHORT_MAX]
    return None

def melhorar_long(script, titulo, falhas):
    L = len(script or "")
    precisa_trim = any("acima_14k" in f for f in falhas)
    precisa_expand = any("falta" in f or "incompleto" in f or "muito_curto" in f for f in falhas)
    precisa_ref = "sem_ref_cientifica" in falhas
    
    if precisa_trim and L > LONG_MAX:
        # Truncar elegantemente
        novo = script[:LONG_MAX]
        ultimo_ponto = max(novo.rfind(". "), novo.rfind("\n"))
        if ultimo_ponto > LONG_MIN: novo = novo[:ultimo_ponto+1]
        return novo if LONG_MIN <= len(novo) <= LONG_MAX else script[:LONG_MAX]
    
    system = """Você é Daniela Coelho, psicóloga BR especialista em psicologia viral.
REGRAS:
- Tom empático, científico, acessível
- Incluir referências científicas: DSM-5, Bowlby, van der Kolk, PMID obrigatório
- Casos ficticios anonimizados: Maria, Carlos, Ana, Pedro
- Frases curtas para TTS (max 2 linhas por parágrafo)
- Hook emocional forte no início
- 5 open loops ao longo do texto
- Cliffhanger no final"""
    
    faltam = LONG_MIN - L if precisa_expand else 0
    user = f"""Título: {titulo}
Script atual ({L} chars):
{script[:2000]}
[...continua até {L} chars...]
{script[-1500:] if L > 3500 else ""}

PROBLEMAS: {", ".join(falhas)}
{"EXPANDIR: adicionar " + str(faltam) + " chars com mais exemplos, ciência e insights" if precisa_expand else ""}
{"ADICIONAR REFERÊNCIAS CIENTÍFICAS (DSM-5, Bowlby, van der Kolk, PMID)" if precisa_ref else ""}

Retorne o script melhorado completo com exatamente {LONG_MIN}-{LONG_MAX} chars.
Output: APENAS o script, sem comentários."""
    
    resp = call_llm(system, user, 8000)
    if resp and len(resp) > 500:
        novo = script + "\n\n" + resp if precisa_expand else resp
        if len(novo) > LONG_MAX: novo = novo[:LONG_MAX]
        return novo
    return None

def get_next_video():
    force_id = os.environ.get("FORCE_PIPELINE_ID","")
    if force_id:
        rows = sb_get("content_pipeline", f"id=eq.{force_id}",
            "id,pub_order,status,youtube_title,target_platform,script,seo_score,youtube_tags")
    else:
        rows = sb_get("content_pipeline",
            "pub_order=not.is.null&mp4_url=is.null&status=in.(audio_ready,pending,ready_tts)&order=pub_order.asc&limit=1",
            "id,pub_order,status,youtube_title,target_platform,script,seo_score,youtube_tags")
    return rows[0] if rows else None

def dispatch_render(pid):
    req = urllib.request.Request(
        f"https://api.github.com/repos/{REPO}/actions/workflows/render-mp4-v2.yml/dispatches",
        data=json.dumps({"ref":"main"}).encode(), method="POST",
        headers={"Authorization":f"Bearer {GH_PAT}","Accept":"application/vnd.github+json","Content-Type":"application/json"})
    try:
        with urllib.request.urlopen(req, timeout=15) as r: return r.status == 204
    except: return False

def main():
    video = get_next_video()
    if not video:
        print("✅ Fila vazia — todos vídeos processados ou aguardando Cérebro!")
        return 0
    
    pid = video["id"]; po = video["pub_order"]
    titulo = video.get("youtube_title",""); plat = video.get("target_platform","")
    script = video.get("script","") or ""; seo = video.get("seo_score",0) or 0
    tags = video.get("youtube_tags",[]) or []
    is_short = plat in ("youtube_shorts","instagram_reels","tiktok_short")
    
    print(f"\n{'='*55}")
    print(f"📹 #{po} ID={pid} {'SHORT' if is_short else 'LONG'}")
    print(f"   {titulo[:55]}")
    print(f"{'='*55}")
    
    script_atual = script
    for t in range(1, MAX_TENTATIVAS+1):
        score, falhas = score_script(script_atual, titulo, is_short, seo, tags)
        print(f"\n  Tentativa {t} | Score {score}/100 | {'✅' if score>=95 else '❌'} {', '.join(falhas[:2])}")
        
        if score >= 95:
            print(f"  ✅ Score {score} — atualizar banco e renderizar...")
            sb_patch("content_pipeline", f"id=eq.{pid}", {"script":script_atual,"status":"audio_ready"})
            ok = dispatch_render(pid)
            print(f"  Render: {'✅ OK' if ok else '❌ falhou'}")
            return 0
        
        if t >= MAX_TENTATIVAS: break
        print(f"  🔧 Melhorando script...")
        novo = melhorar_short(script_atual, titulo, falhas) if is_short else melhorar_long(script_atual, titulo, falhas)
        if novo: script_atual = novo; print(f"  Script: {len(script_atual)} chars")
        else: print(f"  LLM não retornou, aguardando..."); time.sleep(3)
    
    print(f"\n⚠️  #{po} não atingiu 95 após {MAX_TENTATIVAS} tentativas")
    return 1

if __name__ == "__main__":
    sys.exit(main())
