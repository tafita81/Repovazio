#!/usr/bin/env python3
"""LinkedIn Easy Apply — usa cookies salvos pelo session_manager"""
import os, sys, json, time, datetime, urllib.request, urllib.parse

sys.path.insert(0, os.path.dirname(__file__))
from session_manager import load_session, save_session, stealth_context, sb_upsert, sb_get

SUPA = os.environ.get("SUPABASE_URL","https://tpjvalzwkqwttvmszvie.supabase.co")
KEY  = os.environ.get("SUPABASE_ANON_KEY","")
AKEY = os.environ.get("ANTHROPIC_API_KEY","")

PROFILE = {
    "first":"Rafael","last":"Rodrigues",
    "email":"Rafa_roberto2004@yahoo.com.br",
    "phone":"+5522992418257",
    "linkedin":"https://linkedin.com/in/rafael-r-a3946a15",
    "headline":"Senior Data Analyst | Power BI Developer | 15+ years",
    "cv":".github/assets/rafael_cv.pdf",
}

QUERIES = [
    "Power BI Developer","Senior Data Analyst","Business Intelligence Analyst",
    "Analytics Engineer","BI Developer","Tableau Developer","Reporting Analyst"
]

def already_applied(jid):
    r = sb_get(f"job_applications?job_id=eq.{urllib.parse.quote(str(jid))}&select=id&limit=1")
    return isinstance(r,list) and len(r)>0

def save(co, role, url, jid, status):
    sb_upsert("job_applications",{
        "company":co,"role":role,"url":url,"job_id":str(jid),
        "application_method":"linkedin_easy_apply","status":status,
        "platform":"LinkedIn","applied_at":datetime.datetime.now(datetime.timezone.utc).isoformat(),
        "email":PROFILE["email"],"country":"US"
    })

def search_jobs_api(session_data, query, limit=20):
    """Busca vagas via LinkedIn API interna usando cookies"""
    if not session_data: return []
    # Montar cookie header
    cookies_str = "; ".join([f"{c['name']}={c['value']}" for c in session_data.get("cookies",[])])
    try:
        url = (f"https://www.linkedin.com/jobs-guest/jobs/api/seeMoreJobPostings/search"
               f"?keywords={urllib.parse.quote(query)}&location=United+States"
               f"&f_WT=2&f_EA=true&start=0&count={limit}")
        req = urllib.request.Request(url, headers={
            "User-Agent":"Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36",
            "Cookie": cookies_str,
            "Referer":"https://www.linkedin.com/jobs/",
            "X-Li-Lang":"en_US","X-Li-Track":'{"clientVersion":"1.13","mpVersion":"1.13"}'
        })
        with urllib.request.urlopen(req, timeout=10) as r:
            html = r.read().decode("utf-8", errors="ignore")
        # Extrair job IDs do HTML
        import re
        ids = re.findall(r'data-job-id="(\d+)"', html)
        titles = re.findall(r'class="base-search-card__title[^"]*">([^<]+)<', html)
        companies = re.findall(r'class="base-search-card__subtitle[^"]*">([^<]+)<', html)
        jobs = []
        for i, jid in enumerate(ids[:limit]):
            jobs.append({
                "id": f"li_{jid}",
                "jid": jid,
                "title": titles[i].strip() if i < len(titles) else query,
                "company": companies[i].strip() if i < len(companies) else "?",
                "url": f"https://www.linkedin.com/jobs/view/{jid}/"
            })
        return jobs
    except: return []

def easy_apply_linkedin(ctx, session_data, job):
    """Aplica em vaga via LinkedIn Easy Apply"""
    pg = ctx.new_page()
    try:
        # Restaurar cookies
        for c in session_data.get("cookies",[]):
            try: ctx.add_cookies([c])
            except: pass
        pg.goto(job["url"], timeout=20000)
        pg.wait_for_load_state("domcontentloaded", timeout=10000)
        time.sleep(2)
        # Clicar Easy Apply
        for sel in [".jobs-apply-button","button:has-text('Easy Apply')","button.jobs-apply-button"]:
            try:
                el = pg.locator(sel).first
                if el.is_visible(timeout=2000):
                    el.click(); time.sleep(2); break
            except: pass
        # Preencher formulário modal
        filled = 0
        for sel, val in [
            ("input[id*='phoneNumber']", PROFILE["phone"]),
            ("input[id*='phone']", PROFILE["phone"]),
            ("#follow-company-checkbox-public-profile-url", PROFILE["linkedin"]),
        ]:
            try:
                el = pg.locator(sel).first
                if el.is_visible(timeout=500):
                    el.clear(); el.fill(val); filled += 1
            except: pass
        # Upload CV se necessário
        for sel in ["input[type='file']"]:
            try:
                el = pg.locator(sel).first
                if el.count() and os.path.exists(PROFILE["cv"]):
                    el.set_input_files(PROFILE["cv"]); time.sleep(2); filled += 1
            except: pass
        # Avançar/Submit
        submitted = False
        for _ in range(5):
            for sel in ["button:has-text('Submit application')","button:has-text('Submit')","button:has-text('Next')"]:
                try:
                    el = pg.locator(sel).first
                    if el.is_visible(timeout=800):
                        el.click(); time.sleep(2)
                        if "Submit application" in sel or "Submit" in sel:
                            submitted = True
                        break
                except: pass
            if submitted: break
        pg.close()
        return "success" if submitted else f"partial_{filled}"
    except Exception as e:
        try: pg.close()
        except: pass
        return f"err:{str(e)[:30]}"

def main():
    from playwright.sync_api import sync_playwright
    today = datetime.date.today().strftime("%d/%m/%Y")
    print(f"\n{'━'*58}")
    print(f"  💼 LINKEDIN EASY APPLY — {today}")
    print(f"{'━'*58}\n")
    session = load_session("linkedin")
    if not session:
        print("  ⚠️  Sem sessão LinkedIn salva")
        print("  Tentando login automático...")
        with sync_playwright() as p:
            br, ctx = stealth_context(p)
            from session_manager import try_login_linkedin
            cookies = try_login_linkedin(ctx)
            if cookies:
                save_session("linkedin", cookies)
                session = {"cookies": cookies}
                print(f"  ✅ Login OK — {len(cookies)} cookies")
            br.close()
    if not session:
        print("  ❌ LinkedIn não disponível — capturar token manualmente")
        return
    print(f"  ✅ Sessão disponível")
    ok = skip = err = 0
    with sync_playwright() as p:
        br, ctx = stealth_context(p)
        all_jobs = []
        for q in QUERIES:
            jobs = search_jobs_api(session, q, 10)
            all_jobs.extend(jobs)
            time.sleep(0.5)
        seen = set()
        unique = [j for j in all_jobs if j["id"] not in seen and not seen.add(j["id"])]
        new_jobs = [j for j in unique if not already_applied(j["id"])]
        print(f"  Vagas encontradas: {len(unique)} | Novas: {len(new_jobs)}\n")
        for job in new_jobs[:15]:
            co = job["company"][:22]
            role = job["title"][:38]
            print(f"  {co:<24} {role:<38}", end=" ", flush=True)
            res = easy_apply_linkedin(ctx, session, job)
            icon = "✅" if "success" in res else "📋"
            print(f"{icon} {res}")
            save(job["company"], job["title"], job["url"], job["id"], res)
            if "success" in res: ok += 1
            else: err += 1
            time.sleep(3)
        br.close()
    print(f"\n  ✅ {ok} aplicados | ⏭️ {skip} já feitos | ⚠️ {err} outros")

if __name__ == "__main__":
    main()
