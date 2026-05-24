#!/usr/bin/env python3
"""
PLAYWRIGHT JOB HUNTER — Preenche formulários reais
Rafael Rodrigues | +5522992418257
"""
import os, time, json, datetime, urllib.request, urllib.parse, hashlib, sys
from playwright.sync_api import sync_playwright, TimeoutError as PWTimeout

PHONE     = "+5522992418257"
REPLY_TO  = "Rafa_roberto2004@yahoo.com.br"
SUPA_URL  = os.environ.get("SUPABASE_URL","https://tpjvalzwkqwttvmszvie.supabase.co")
SUPA_KEY  = os.environ.get("SUPABASE_ANON_KEY","")
CV_PATH   = ".github/assets/rafael_cv.pdf"

PROFILE = {
    "first_name":    "Rafael",
    "last_name":     "Rodrigues",
    "email":         REPLY_TO,
    "phone":         PHONE,
    "linkedin":      "https://linkedin.com/in/rafael-r-a3946a15",
    "location":      "Brazil",
    "company":       "Dataex",
    "title":         "Senior Data Analyst",
    "years_exp":     "15",
    "salary":        "120000",
    "authorized":    "Yes",   # work authorization
    "sponsorship":   "No",    # visa sponsorship
    "referrer":      "LinkedIn",
    "cover": lambda role, co: f"""Dear {co} Hiring Team,

I am applying for the {role} position. Senior Data Analyst and Analytics Engineer with 15+ years of enterprise BI experience. Microsoft PL-300 Power BI Data Analyst and Tableau Desktop Specialist certified.

Key achievements:
• $9M+ operational savings — TIM/OI Telecommunications
• 70% report latency reduction via DAX/SQL optimization — Keyrus
• Analytics platforms for 200+ business users (Financial Services, Retail, Telecom)
• Multi-cloud: Power BI · BigQuery · Snowflake · Databricks · Azure Synapse

Phone: {PHONE}
LinkedIn: https://linkedin.com/in/rafael-r-a3946a15

Available immediately for remote engagement.
Rafael Rodrigues — PL-300 | Tableau Certified | +5522992418257"""
}

# ─── RESPOSTAS PARA PERGUNTAS CUSTOMIZADAS ────────────────────────────────────
ANSWER_MAP = {
    # work authorization
    "authorized": "Yes",
    "legally authorized": "Yes",
    "work in the country": "Yes",
    "work authorization": "Yes",
    "eligible to work": "Yes",
    # sponsorship
    "sponsorship": "No",
    "visa sponsorship": "No",
    "require.*sponsor": "No",
    "sponsor.*work": "No",
    # source / referral
    "how did you hear": "LinkedIn",
    "how did you find": "LinkedIn",
    "referred by": "LinkedIn",
    "source": "LinkedIn",
    "referr": "LinkedIn",
    # relocation
    "relocat": "Yes",
    "willing to relocat": "Yes",
    # remote
    "remote": "Yes",
    "work remotely": "Yes",
    # salary
    "salary": "120000",
    "compensation": "120000",
    "expected salary": "120000",
    # start date
    "start date": "Immediately",
    "available to start": "Immediately",
    "when can you start": "Immediately",
    # gender / diversity (optional)
    "gender": "Prefer not to say",
    "race": "I don't wish to answer",
    "ethnicity": "I don't wish to answer",
    "veteran": "I am not a protected veteran",
    "disability": "I don't wish to answer",
    # experience
    "years of experience": "15+",
    "years.*experience": "15",
}

def get_answer(label: str) -> str:
    label_lower = label.lower()
    import re
    for pattern, answer in ANSWER_MAP.items():
        if re.search(pattern, label_lower):
            return answer
    return ""

# ─── SUPABASE ─────────────────────────────────────────────────────────────────
def supa_insert(table, data):
    url = f"{SUPA_URL}/rest/v1/{table}"
    body = json.dumps(data).encode()
    req = urllib.request.Request(url, data=body, method="POST", headers={
        "apikey":SUPA_KEY,"Authorization":f"Bearer {SUPA_KEY}",
        "Content-Type":"application/json","Prefer":"return=minimal"
    })
    try:
        with urllib.request.urlopen(req, timeout=10) as r: return r.status
    except: return 0

def is_applied(eid):
    url = f"{SUPA_URL}/rest/v1/job_leads?external_id=eq.{urllib.parse.quote(str(eid))}&applied=eq.true&select=id"
    req = urllib.request.Request(url, headers={"apikey":SUPA_KEY,"Authorization":f"Bearer {SUPA_KEY}"})
    try:
        with urllib.request.urlopen(req, timeout=8) as r:
            return len(json.loads(r.read())) > 0
    except: return False

def mark_applied(eid, company, role, url, platform, method, status="sent"):
    now = datetime.datetime.now(datetime.timezone.utc).isoformat()
    supa_insert("job_leads", {"external_id":str(eid),"company":company,"role":role,
        "url":url,"platform":platform,"applied":True,"applied_at":now,"ats_type":method})
    supa_insert("job_applications", {"company":company,"role":role,"url":url,
        "application_method":method,"platform":platform,"status":status})

# ─── GREENHOUSE DISCOVERY ─────────────────────────────────────────────────────
GH_COMPANIES = [
    "braze","twilio","adyen","stripe","elastic","clickhouse",
    "databricks","datadog","honeycombio","grafana-labs","newrelic-relyance",
    "amplitude","mixpanel","segment","fullstory","heap","pendo",
    "thoughtspot","sigmacomputing","mode-analytics","hex","metabase",
    "dbt-labs","fivetran","airbyte","hightouch","census","monte-carlo-data",
    "brex","ramp","mercury","affirm","gusto","rippling","lattice",
    "cultureamp","asana","notion","webflow","figma","miro","loom",
    "zendesk","intercom","gong","outreach","salesloft","hubspot",
    "coinbase","kraken","robinhood","plaid","marqeta","payoneer",
    "openai","cohere","scale-ai","labelbox","weights-biases","arize-ai",
    "shopify","woocommerce","narvar","bazaarvoice","yotpo",
    "airbnb","expedia","hopper","tripadvisor",
    "sorcero","corsearch","lexipol","preply","airalo","moniepoint",
    "nubank","vtex","rdstation",
    "gitlab","hashicorp","elastic","cloudflare","fastly",
    "pagerduty","linear","zapier","sentry","rollbar",
]

KEYWORDS = ["data analyst","power bi","business intelligence","bi developer",
            "analytics engineer","bi analyst","reporting analyst","data visualization"]

def discover_gh_jobs():
    jobs = []
    for co in GH_COMPANIES:
        try:
            url = f"https://boards-api.greenhouse.io/v1/boards/{co}/jobs"
            req = urllib.request.Request(url, headers={"User-Agent":"Mozilla/5.0"})
            with urllib.request.urlopen(req, timeout=6) as r:
                data = json.loads(r.read())
                for j in data.get("jobs",[]):
                    if any(k in j.get("title","").lower() for k in KEYWORDS):
                        apply_url = j.get("absolute_url","")
                        if apply_url:
                            jobs.append({
                                "id":f"gh_{co}_{j['id']}",
                                "company":co.replace("-"," ").title(),
                                "role":j["title"],
                                "url":apply_url,
                                "platform":"Greenhouse",
                                "ats_type":"greenhouse_playwright"
                            })
        except: pass
        time.sleep(0.2)
    return jobs

# ─── PLAYWRIGHT FORM FILLER ───────────────────────────────────────────────────
def fill_greenhouse_form(page, job, cv_path):
    """Preenche formulário Greenhouse com Playwright"""
    role, company = job["role"], job["company"]
    cover_text = PROFILE["cover"](role, company)

    try:
        # Navegar para o formulário
        page.goto(job["url"], timeout=25000)
        page.wait_for_load_state("domcontentloaded", timeout=15000)

        # ── Campos padrão ────────────────────────────────────────────────────
        for selector, value in [
            ("input[name='first_name']",  PROFILE["first_name"]),
            ("input[name='last_name']",   PROFILE["last_name"]),
            ("input[name='email']",       PROFILE["email"]),
            ("input[name='phone']",       PROFILE["phone"]),
            ("input[name='candidate-location']", PROFILE["location"]),
        ]:
            try:
                el = page.locator(selector).first
                if el.is_visible(timeout=2000):
                    el.fill(value)
            except: pass

        # ── LinkedIn ─────────────────────────────────────────────────────────
        for sel in ["input[name*='linkedin']","input[placeholder*='LinkedIn']","input[id*='linkedin']"]:
            try:
                el = page.locator(sel).first
                if el.is_visible(timeout=1000):
                    el.fill(PROFILE["linkedin"])
                    break
            except: pass

        # ── Upload do CV PDF ──────────────────────────────────────────────────
        if os.path.exists(cv_path):
            try:
                file_input = page.locator("input[type='file'][name='resume']").first
                if file_input.count() > 0:
                    file_input.set_input_files(cv_path)
                    time.sleep(1)
            except:
                try:
                    file_input = page.locator("input[type='file']").first
                    file_input.set_input_files(cv_path)
                    time.sleep(1)
                except: pass

        # ── Cover letter ──────────────────────────────────────────────────────
        for sel in ["textarea[name='cover_letter']","textarea[id*='cover']","textarea[placeholder*='cover']"]:
            try:
                el = page.locator(sel).first
                if el.is_visible(timeout=1000):
                    el.fill(cover_text[:4000])
                    break
            except: pass

        # ── Perguntas customizadas ────────────────────────────────────────────
        # Selects (dropdowns)
        selects = page.locator("select").all()
        for sel_el in selects:
            try:
                label_text = ""
                # Tentar encontrar o label associado
                sel_id = sel_el.get_attribute("id") or ""
                if sel_id:
                    label = page.locator(f"label[for='{sel_id}']").first
                    if label.count():
                        label_text = label.inner_text().lower()
                
                answer = get_answer(label_text)
                if answer:
                    options = sel_el.locator("option").all()
                    for opt in options:
                        opt_text = opt.inner_text().lower()
                        if answer.lower() in opt_text or opt_text in answer.lower():
                            sel_el.select_option(value=opt.get_attribute("value") or opt.inner_text())
                            break
                    else:
                        # Tentar Yes/No genérico
                        if answer in ["Yes","No"]:
                            for opt in options:
                                if opt.inner_text().strip().lower() == answer.lower():
                                    sel_el.select_option(label=opt.inner_text())
                                    break
            except: pass

        # Radio buttons (work auth, sponsorship, etc.)
        radios = page.locator("input[type='radio']").all()
        processed_names = set()
        for radio in radios:
            try:
                name = radio.get_attribute("name") or ""
                if name in processed_names: continue
                
                label_text = ""
                radio_id = radio.get_attribute("id") or ""
                if radio_id:
                    label = page.locator(f"label[for='{radio_id}']").first
                    if label.count():
                        label_text = label.inner_text().lower()
                
                answer = get_answer(label_text) or get_answer(name.lower())
                if answer:
                    # Selecionar o radio com o valor correspondente
                    value = radio.get_attribute("value") or ""
                    if answer.lower() in value.lower() or value.lower() in answer.lower():
                        radio.check()
                        processed_names.add(name)
                    elif answer == "Yes" and value.lower() in ["yes","1","true"]:
                        radio.check()
                        processed_names.add(name)
                    elif answer == "No" and value.lower() in ["no","0","false"]:
                        radio.check()
                        processed_names.add(name)
            except: pass

        # Text inputs customizados (question_XXXXXX)
        custom_inputs = page.locator("input[name^='question_'], textarea[name^='question_']").all()
        for inp in custom_inputs:
            try:
                name = inp.get_attribute("name") or ""
                label_text = ""
                inp_id = inp.get_attribute("id") or ""
                if inp_id:
                    label = page.locator(f"label[for='{inp_id}']").first
                    if label.count():
                        label_text = label.inner_text()
                
                answer = get_answer(label_text)
                if not answer:
                    answer = PROFILE["referrer"]  # default: LinkedIn
                
                tag = inp.evaluate("el => el.tagName")
                if tag == "TEXTAREA":
                    inp.fill(answer)
                else:
                    inp.fill(answer)
            except: pass

        # ── Submeter o formulário ─────────────────────────────────────────────
        submit = None
        for sel in [
            "input[type='submit']",
            "button[type='submit']",
            "button:has-text('Submit')",
            "button:has-text('Apply')",
            "button:has-text('Send Application')",
            "[data-testid*='submit']",
        ]:
            try:
                el = page.locator(sel).first
                if el.is_visible(timeout=1000):
                    submit = el
                    break
            except: pass

        if submit:
            submit.click(timeout=5000)
            time.sleep(3)
            
            # Verificar se foi enviado
            current_url = page.url
            title = page.title().lower()
            success = any(k in title or k in current_url for k in 
                         ["thank","confirmation","success","submitted","received"])
            return "success" if success else "submitted"
        else:
            return "no_submit_button"

    except PWTimeout:
        return "timeout"
    except Exception as e:
        return f"error: {str(e)[:60]}"

# ─── MAIN ─────────────────────────────────────────────────────────────────────
def main():
    today = datetime.date.today().strftime("%d/%m/%Y")
    print(f"\n{'='*65}")
    print(f"  PLAYWRIGHT JOB HUNTER — {today}")
    print(f"  Tel: {PHONE}")
    print(f"{'='*65}\n")

    if not os.path.exists(CV_PATH):
        print(f"❌ CV não encontrado: {CV_PATH}")
        return

    print(f"✅ CV PDF: {os.path.getsize(CV_PATH):,} bytes\n")

    print("Descobrindo vagas Greenhouse...")
    jobs = discover_gh_jobs()
    new_jobs = [j for j in jobs if not is_applied(j["id"])]
    print(f"Total: {len(jobs)} vagas | Novas: {len(new_jobs)}\n")

    if not new_jobs:
        print("✅ Nenhuma vaga nova — tudo já aplicado!")
        return

    results = []
    with sync_playwright() as p:
        browser = p.chromium.launch(
            headless=True,
            args=["--no-sandbox","--disable-dev-shm-usage","--disable-gpu"]
        )
        context = browser.new_context(
            user_agent="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            viewport={"width":1280,"height":800},
            locale="en-US",
        )

        print("── PREENCHENDO FORMULÁRIOS ─────────────────────────────────────")
        for i, job in enumerate(new_jobs[:30], 1):  # max 30 por run
            page = context.new_page()
            print(f"  [{i:2}/{min(len(new_jobs),30)}] {job['company'][:25]:<27} {job['role'][:40]}", end=" ", flush=True)
            
            result = fill_greenhouse_form(page, job, CV_PATH)
            page.close()
            
            ok = result in ["success","submitted"]
            icon = "✅" if result == "success" else "📨" if result == "submitted" else "⚠️"
            print(f"{icon} {result}")
            
            status = "success" if ok else result
            mark_applied(job["id"], job["company"], job["role"],
                        job["url"], job["platform"], "playwright_gh", status)
            results.append({**job, "result": result})
            time.sleep(2)

        browser.close()

    ok_count = sum(1 for r in results if r["result"] in ["success","submitted"])
    print(f"\n{'='*65}")
    print(f"  RESULTADO: {ok_count}/{len(results)} formulários preenchidos")
    print(f"{'='*65}\n")

if __name__ == "__main__":
    main()
