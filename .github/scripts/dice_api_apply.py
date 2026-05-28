#!/usr/bin/env python3
"""
DICE API APPLY — Usa token de sessão salvo no Supabase
Não precisa de login headless — usa a API interna do Dice diretamente
"""
import os, json, time, datetime, urllib.request, urllib.parse, re

SUPA = os.environ.get("SUPABASE_URL", "https://tpjvalzwkqwttvmszvie.supabase.co")
KEY  = os.environ.get("SUPABASE_ANON_KEY", "")

def sb_get(path):
    req = urllib.request.Request(f"{SUPA}/rest/v1/{path}",
        headers={"apikey": KEY, "Authorization": f"Bearer {KEY}"})
    try:
        with urllib.request.urlopen(req, timeout=8) as r:
            return json.loads(r.read())
    except: return []

def sb_post(table, data):
    req = urllib.request.Request(f"{SUPA}/rest/v1/{table}",
        data=json.dumps(data).encode(), method="POST",
        headers={"apikey": KEY, "Authorization": f"Bearer {KEY}",
                 "Content-Type": "application/json", "Prefer": "return=minimal"})
    try:
        with urllib.request.urlopen(req, timeout=8) as r: return r.status
    except: return 0

def get_dice_token():
    """Recupera token salvo via página de captura"""
    rows = sb_get("ia_cache?cache_key=eq.secret%3ADICE_SESSION_TOKEN&select=cache_value")
    if rows and rows[0].get("cache_value"):
        return rows[0]["cache_value"]
    # Fallback: credenciais diretas
    return None

def dice_api_headers(token):
    return {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
        "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X) AppleWebKit/605.1.15",
        "Accept": "application/json",
        "Origin": "https://www.dice.com",
        "Referer": "https://www.dice.com/",
        "x-api-key": "1YAt0R9wBg4WfsF9VB2778F4BkEFeDe0",
    }

def dice_easy_apply_api(token, job_id, job_title, company):
    """Aplica via API interna do Dice (sem Playwright)"""
    hdrs = dice_api_headers(token)
    
    # 1. Verificar job details via API
    try:
        req = urllib.request.Request(
            f"https://job-search-api.svc.dhigroupinc.com/v1/dice/jobs/{job_id}",
            headers=hdrs)
        with urllib.request.urlopen(req, timeout=8) as r:
            job = json.loads(r.read())
    except:
        job = {}
    
    apply_url = (job.get("applyUrl","") or 
                 job.get("externalUrl","") or 
                 job.get("detailsPageUrl",""))
    
    # 2. Se tem URL externa (Greenhouse/Lever), retorna para aplicar via formulário
    if any(k in apply_url for k in ["greenhouse","lever","workday","ashby","smartrecruit"]):
        return "external", apply_url
    
    # 3. Tentar Easy Apply via API
    try:
        payload = json.dumps({
            "jobId": job_id,
            "jobTitle": job_title,
            "company": company,
            "applicationType": "EASY_APPLY",
            "resumeId": None,
        }).encode()
        req = urllib.request.Request(
            "https://platform.dice.com/api/v1/apply/easy",
            data=payload, method="POST", headers=hdrs)
        with urllib.request.urlopen(req, timeout=10) as r:
            result = json.loads(r.read())
            if result.get("success") or result.get("applicationId"):
                return "success", result.get("applicationId","")
    except Exception as e:
        pass
    
    # 4. Fallback: API v2
    try:
        payload = json.dumps({"jobId": job_id}).encode()
        req = urllib.request.Request(
            f"https://www.dice.com/api/apply/{job_id}",
            data=payload, method="POST", headers=hdrs)
        with urllib.request.urlopen(req, timeout=10) as r:
            return "success_v2", ""
    except Exception as e:
        return "failed", str(e)[:50]

def fetch_new_dice_jobs():
    """Busca novas vagas relevantes no Dice via API pública"""
    queries = [
        "power+bi+developer", "senior+data+analyst",
        "analytics+engineer", "business+intelligence+analyst",
        "bi+developer", "tableau+developer"
    ]
    jobs = []
    seen = set()
    KWORDS = ["data analyst","power bi","business intelligence","bi developer","analytics engineer",
              "reporting analyst","data visualization","tableau","looker","bi analyst"]
    
    for q in queries:
        try:
            url = (f"https://job-search-api.svc.dhigroupinc.com/v1/dice/jobs/search"
                   f"?q={q}&countryCode2=US&radius=30&radiusUnit=mi&page=1&pageSize=20"
                   f"&filters.workplaceTypes=Remote&filters.employmentType=FULLTIME"
                   f"&filters.easyApply=true"  # Apenas Easy Apply
                   f"&fields=id,title,companyName,salary,detailsPageUrl,easyApply,summary")
            req = urllib.request.Request(url, headers={
                "User-Agent": "Mozilla/5.0",
                "x-api-key": "1YAt0R9wBg4WfsF9VB2778F4BkEFeDe0"
            })
            with urllib.request.urlopen(req, timeout=10) as r:
                data = json.loads(r.read())
            for j in data.get("data", []):
                title = j.get("title","")
                if not any(k in title.lower() for k in KWORDS): continue
                jid = j.get("id") or j.get("guid","")
                if jid in seen: continue
                seen.add(jid)
                jobs.append({
                    "id": jid, "title": title,
                    "company": j.get("companyName","?"),
                    "url": j.get("detailsPageUrl",""),
                    "salary": j.get("salary",""),
                    "easy_apply": j.get("easyApply", False),
                })
            time.sleep(0.3)
        except: pass
    return jobs

def already_applied(job_id):
    r = sb_get(f"job_applications?job_id=eq.dice_{urllib.parse.quote(str(job_id))}&select=id&limit=1")
    return len(r) > 0

def save(company, role, url, jid, status, salary=""):
    now = datetime.datetime.now(datetime.timezone.utc).isoformat()
    sb_post("job_applications", {
        "company": company, "role": role, "url": url,
        "job_id": f"dice_{jid}", "platform": "Dice",
        "application_method": "dice_api_easy_apply",
        "status": status, "applied_at": now,
        "email": "Rafa_roberto2004@yahoo.com.br",
        "salary": salary, "country": "US"
    })

def main():
    today = datetime.date.today().strftime("%d/%m/%Y")
    print(f"\n{'━'*55}")
    print(f"  🎲 DICE API APPLY — {today}")
    print(f"{'━'*55}\n")

    # Obter token
    token = get_dice_token()
    if not token:
        print("  ❌ Token Dice não encontrado no Supabase")
        print("  → Acesse: https://repovazio.vercel.app/dice-capture.html")
        print("  → Faça o processo enquanto logado no Dice")
        return

    print(f"  ✅ Token encontrado: {token[:12]}...{token[-6:]}")

    # Buscar vagas Easy Apply
    jobs = fetch_new_dice_jobs()
    new_jobs = [j for j in jobs if j["easy_apply"] and not already_applied(j["id"])]
    print(f"  Vagas Easy Apply encontradas: {len(jobs)} total | {len(new_jobs)} novas\n")

    ok = fail = external = 0
    for j in new_jobs[:20]:
        co   = j["company"][:22]
        role = j["title"][:40]
        sal  = j.get("salary","")[:15]
        print(f"  {co:<24} {role:<40} {sal:<15}", end=" ", flush=True)

        result, detail = dice_easy_apply_api(token, j["id"], j["title"], j["company"])

        if result in ("success","success_v2"):
            print(f"✅ aplicado")
            save(j["company"], j["title"], j["url"], j["id"], "success", j.get("salary",""))
            ok += 1
        elif result == "external":
            print(f"🔗 → {detail[:40]}")
            save(j["company"], j["title"], detail, j["id"], "external_ats", j.get("salary",""))
            external += 1
        else:
            print(f"⚠️  {result}")
            save(j["company"], j["title"], j["url"], j["id"], f"failed_{result[:20]}", j.get("salary",""))
            fail += 1
        time.sleep(1.5)

    print(f"\n{'━'*55}")
    print(f"  ✅ {ok} aplicados | 🔗 {external} externos | ⚠️ {fail} falhas")
    print(f"{'━'*55}\n")

if __name__ == "__main__":
    main()
