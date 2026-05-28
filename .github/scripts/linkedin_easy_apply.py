#!/usr/bin/env python3
"""
LINKEDIN EASY APPLY v2
Usa cookie li_at salvo no Supabase para aplicar via LinkedIn API interna
"""
import os, json, time, re, datetime, urllib.request, urllib.parse

SUPA = os.environ.get("SUPABASE_URL","https://tpjvalzwkqwttvmszvie.supabase.co")
KEY  = os.environ.get("SUPABASE_ANON_KEY","")
AKEY = os.environ.get("ANTHROPIC_API_KEY","")
EM   = os.environ.get("DICE_EMAIL","tafita81@gmail.com")
CV   = ".github/assets/rafael_cv.pdf"
PROF = {
    "first":"Rafael","last":"Rodrigues",
    "email":"Rafa_roberto2004@yahoo.com.br",
    "phone":"+5522992418257",
    "linkedin":"https://linkedin.com/in/rafael-r-a3946a15",
}
KW = ["data analyst","power bi","business intelligence","bi developer",
      "analytics engineer","reporting analyst","tableau","bi analyst"]

def sb(m,p,d=None):
    h={"apikey":KEY,"Authorization":"Bearer "+KEY,"Content-Type":"application/json"}
    rq=urllib.request.Request(SUPA+"/rest/v1/"+p,
       data=json.dumps(d).encode() if d else None,method=m,headers=h)
    try:
        with urllib.request.urlopen(rq,timeout=8) as r:
            return json.loads(r.read()) if m=="GET" else r.status
    except Exception as e: return 409 if "409" in str(e) else None

def seen(jid):
    r=sb("GET","job_applications?job_id=eq."+urllib.parse.quote(str(jid))+"&select=id&limit=1")
    return isinstance(r,list) and len(r)>0

def save(co,role,url,jid,status):
    sb("POST","job_applications",{
        "company":co,"role":role,"url":url,"job_id":str(jid),
        "application_method":"linkedin_easy_apply_v2","status":status,
        "platform":"LinkedIn","applied_at":datetime.datetime.now(datetime.timezone.utc).isoformat(),
        "email":PROF["email"],"country":"US"})

def get_li_token():
    rows=sb("GET","ia_cache?cache_key=eq.secret%3ALINKEDIN_LI_AT&select=value,expires_at&limit=1")
    if not isinstance(rows,list) or not rows: return None
    exp=rows[0].get("expires_at","")
    if exp and exp < datetime.datetime.now(datetime.timezone.utc).isoformat(): return None
    return rows[0].get("value","") or None

def li_headers(li_at):
    return {
        "Cookie": "li_at="+li_at,
        "Csrf-Token": "ajax:"+str(int(time.time())),
        "X-Li-Lang": "en_US",
        "X-RestLi-Protocol-Version": "2.0.0",
        "X-Li-Track": '{"clientVersion":"1.13","mpVersion":"1.13","osName":"web","timezoneOffset":-5}',
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 Chrome/124.0",
        "Accept": "application/vnd.linkedin.normalized+json+2.1",
        "Accept-Language": "en-US,en;q=0.9",
        "Referer": "https://www.linkedin.com/jobs/",
    }

def search_easy_apply_jobs(li_at, query, limit=20):
    """Busca vagas com Easy Apply via API do LinkedIn Voyager"""
    jobs = []
    try:
        # LinkedIn Voyager API — busca de vagas com filtro Easy Apply
        params = urllib.parse.urlencode({
            "decorationId": "com.linkedin.voyager.deco.jserp.WebJobSearchHitLite-14",
            "count": limit,
            "filters": "List(easy_apply->true,locationFallback->United%20States,workplaceType->2)",
            "keywords": query,
            "origin": "JOB_SEARCH_PAGE_KEYWORD_AUTOCOMPLETE",
            "q": "jserpFilters",
            "start": 0,
        })
        url = "https://www.linkedin.com/voyager/api/jobs/jobPostings?"+params
        rq = urllib.request.Request(url, headers=li_headers(li_at))
        with urllib.request.urlopen(rq, timeout=10) as r:
            data = json.loads(r.read())
        elements = data.get("elements",[]) or data.get("data",{}).get("elements",[])
        for el in elements:
            jid_raw = el.get("jobPostingId","") or el.get("id","")
            title = el.get("title","") or el.get("jobPosting",{}).get("title","")
            co = el.get("companyName","") or el.get("companyDetails",{}).get("company","")
            if jid_raw and title:
                jobs.append({
                    "id": "li_ea_"+str(jid_raw),
                    "jid_raw": str(jid_raw),
                    "title": title,
                    "company": co,
                    "url": "https://www.linkedin.com/jobs/view/"+str(jid_raw)+"/",
                })
    except Exception as e:
        pass
    return jobs

def search_jobs_guest(query, limit=20):
    """Fallback: busca sem autenticação, filtra Easy Apply"""
    jobs = []
    try:
        url = ("https://www.linkedin.com/jobs-guest/jobs/api/seeMoreJobPostings/search"
               "?keywords="+urllib.parse.quote(query)+
               "&location=United+States&f_WT=2&f_LF=f_AL&start=0&count="+str(limit))
        rq = urllib.request.Request(url, headers={
            "User-Agent":"Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36",
            "Accept":"text/html"})
        with urllib.request.urlopen(rq, timeout=10) as r:
            html = r.read().decode("utf-8",errors="ignore")
        ids      = re.findall(r'data-entity-urn="[^"]*jobPosting:(\d+)"', html)
        titles   = [x.strip() for x in re.findall(r'hidden-nested-link[^>]+>([^<]{2,60})</a>', html)]
        # Nota: guest API não confirma Easy Apply por job, mas f_LF=f_AL filtra
        companies = [x.strip() for x in re.findall(r'hidden-nested-link[^>]+>([^<]{2,60})</a>', html)]
        job_titles = [x.strip() for x in re.findall(r'base-search-card__title[^>]+>([^<]{5,80})<', html)]
        for i, jid_raw in enumerate(ids[:limit]):
            jobs.append({
                "id": "li_ea_"+jid_raw,
                "jid_raw": jid_raw,
                "title": job_titles[i] if i < len(job_titles) else query,
                "company": companies[i] if i < len(companies) else "?",
                "url": "https://www.linkedin.com/jobs/view/"+jid_raw+"/",
            })
    except: pass
    return jobs

def get_job_questions(li_at, job_id):
    """Obtém perguntas do formulário Easy Apply"""
    try:
        url = "https://www.linkedin.com/voyager/api/jobs/jobApplications?jobPostingId="+str(job_id)
        rq = urllib.request.Request(url, headers=li_headers(li_at))
        with urllib.request.urlopen(rq, timeout=8) as r:
            return json.loads(r.read())
    except: return {}

def submit_easy_apply(li_at, job_id, company, role):
    """Submete Easy Apply via LinkedIn Voyager API"""
    # Passo 1: Criar rascunho da aplicação
    try:
        draft_payload = json.dumps({
            "jobPostingId": int(job_id),
            "contactInfo": {
                "firstName": PROF["first"],
                "lastName": PROF["last"],
                "email": PROF["email"],
                "phoneNumber": PROF["phone"],
            },
            "resumeId": None,  # Usa o resume default do perfil
        }).encode()
        hdrs = {**li_headers(li_at), "Content-Type": "application/json"}
        rq = urllib.request.Request(
            "https://www.linkedin.com/voyager/api/jobs/jobApplications",
            data=draft_payload, method="POST", headers=hdrs)
        with urllib.request.urlopen(rq, timeout=10) as r:
            draft = json.loads(r.read())
        app_id = draft.get("value",{}).get("jobApplicationId","") or draft.get("id","")
        if app_id:
            # Passo 2: Submeter
            submit_payload = json.dumps({
                "jobApplicationId": app_id,
                "jobPostingId": int(job_id),
                "submitted": True,
            }).encode()
            rq2 = urllib.request.Request(
                "https://www.linkedin.com/voyager/api/jobs/jobApplications/"+str(app_id),
                data=submit_payload, method="PUT", headers=hdrs)
            with urllib.request.urlopen(rq2, timeout=10) as r2:
                result = json.loads(r2.read())
                if result.get("submitted") or result.get("status") == "SUBMITTED":
                    return "success"
        return "api_no_id"
    except urllib.error.HTTPError as e:
        if e.code == 429: return "rate_limited"
        if e.code in [401,403]: return "token_expired"
        return "http_"+str(e.code)
    except Exception as e:
        return "err:"+str(e)[:30]

def easy_apply_playwright_fallback(ctx, li_at, job_id, company, role, url):
    """Playwright com cookies li_at — fallback para jobs sem Voyager API"""
    pg = ctx.new_page()
    try:
        # Injetar cookie li_at
        ctx.add_cookies([{
            "name": "li_at", "value": li_at,
            "domain": ".linkedin.com", "path": "/",
            "secure": True, "httpOnly": True,
        }])
        pg.goto(url, timeout=20000)
        pg.wait_for_load_state("domcontentloaded", timeout=12000)
        time.sleep(2)
        # Clicar Easy Apply
        for sel in [".jobs-apply-button","button:has-text('Easy Apply')","button[aria-label*='Easy Apply']"]:
            try:
                el = pg.locator(sel).first
                if el.is_visible(timeout=2000): el.click(); time.sleep(2); break
            except: pass
        # Verificar se abriu modal
        modal_visible = False
        for sel in [".jobs-easy-apply-modal",".artdeco-modal","[aria-label='Easy Apply']"]:
            try:
                if pg.locator(sel).is_visible(timeout=1500): modal_visible=True; break
            except: pass
        if not modal_visible:
            pg.close(); return "no_modal"
        # Preencher campos do modal
        filled = 0
        for sel, val in [
            ("input[id*='phoneNumber']", PROF["phone"]),
            ("input[name*='phone']", PROF["phone"]),
        ]:
            try:
                el = pg.locator(sel).first
                if el.is_visible(timeout=500): el.clear(); el.fill(val); filled+=1
            except: pass
        # Avançar por todas as páginas do formulário
        submitted = False
        for step in range(6):
            for sel in ["button:has-text('Submit application')","button:has-text('Review')",
                        "button:has-text('Next')","button[aria-label*='Continue']"]:
                try:
                    el = pg.locator(sel).first
                    if el.is_visible(timeout=1000):
                        el.click(); time.sleep(2)
                        if "Submit" in sel: submitted=True
                        break
                except: pass
            if submitted: break
        pg.close()
        return "success" if submitted else "modal_partial"
    except Exception as e:
        try: pg.close()
        except: pass
        return "pw_err:"+str(e)[:25]

def main():
    today = datetime.date.today().strftime("%d/%m/%Y")
    print("\n"+"━"*58)
    print(f"  💼 LINKEDIN EASY APPLY v2 — {today}")
    print("━"*58+"\n")

    li_at = get_li_token()
    if not li_at:
        print("  ❌ Token li_at não encontrado")
        print("  → Acesse: tafita81.github.io/Repovazio/linkedin-setup.html")
        print("  → Cole o código na barra URL do LinkedIn → Salvar")
        return

    print(f"  ✅ Token li_at disponível: {li_at[:12]}...{li_at[-5:]}")

    ok = skip = err = 0
    queries = ["power bi developer","senior data analyst","analytics engineer",
               "business intelligence analyst","bi developer","tableau developer"]

    all_jobs = []
    for q in queries:
        jobs = search_easy_apply_jobs(li_at, q, 15)
        if not jobs:
            jobs = search_jobs_guest(q, 15)
        all_jobs.extend(jobs)
        time.sleep(0.5)

    # Dedup
    seen_ids = set()
    unique = [j for j in all_jobs if j["id"] not in seen_ids and not seen_ids.add(j["id"])]
    new_jobs = [j for j in unique if not seen(j["id"])]
    print(f"  Vagas Easy Apply: {len(unique)} encontradas | {len(new_jobs)} novas\n")

    # Tentar sem Playwright primeiro (API pura)
    for job in new_jobs[:25]:
        co   = job.get("company","?")[:24]
        role = job.get("title","?")[:38]
        print(f"  {co:<24} {role:<38}", end=" ", flush=True)

        res = submit_easy_apply(li_at, job["jid_raw"], job["company"], job["title"])

        if res == "success":
            print("→ ✅ aplicado (API)")
            save(job["company"], job["title"], job["url"], job["id"], "success")
            ok += 1
        elif res == "token_expired":
            print("→ ⚠️  token expirado — renovar em linkedin-setup.html")
            break
        elif res == "rate_limited":
            print("→ ⏸️  rate limit — aguardando...")
            time.sleep(30)
        else:
            print(f"→ 📋 {res}")
            save(job["company"], job["title"], job["url"], job["id"], res)
            err += 1
        time.sleep(2)

    # Playwright fallback para os que a API não conseguiu
    remaining = [j for j in new_jobs[:25] if not seen(j["id"])]
    if remaining and li_at:
        print(f"\n  Playwright fallback: {len(remaining)} vagas...")
        try:
            from playwright.sync_api import sync_playwright
            with sync_playwright() as pw:
                br = pw.chromium.launch(headless=True, args=[
                    "--no-sandbox","--disable-dev-shm-usage","--disable-gpu",
                    "--disable-blink-features=AutomationControlled"])
                ctx = br.new_context(
                    user_agent="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 Chrome/124.0",
                    viewport={"width":1366,"height":768}, locale="en-US")
                ctx.add_init_script("Object.defineProperty(navigator,'webdriver',{get:()=>undefined})")
                for job in remaining:
                    co   = job.get("company","?")[:24]
                    role = job.get("title","?")[:38]
                    print(f"  {co:<24} {role:<38}", end=" ", flush=True)
                    res = easy_apply_playwright_fallback(ctx, li_at, job["jid_raw"],
                        job["company"], job["title"], job["url"])
                    icon = "✅" if "success" in res else "📋"
                    print(f"→ {icon} {res}")
                    save(job["company"], job["title"], job["url"], job["id"], res)
                    if "success" in res: ok += 1
                    time.sleep(2.5)
                br.close()
        except Exception as e:
            print(f"  Playwright ERRO: {str(e)[:60]}")

    print("\n"+"━"*58)
    print(f"  ✅ {ok} aplicadas | ⏭️ {skip} já feitas | ⚠️ {err} outros")
    print("━"*58+"\n")

if __name__ == "__main__":
    main()
