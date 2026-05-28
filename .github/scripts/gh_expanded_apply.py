#!/usr/bin/env python3
"""Apply to expanded GH boards"""
import os, json, time, datetime, urllib.request, urllib.parse

SUPA = os.environ.get("SUPABASE_URL", "https://tpjvalzwkqwttvmszvie.supabase.co")
KEY  = os.environ.get("SUPABASE_ANON_KEY", "")
AKEY = os.environ.get("ANTHROPIC_API_KEY", "")
CV   = ".github/assets/rafael_cv.pdf"
PROF = {
    "first": "Rafael", "last": "Rodrigues",
    "email": "Rafa_roberto2004@yahoo.com.br",
    "phone": "+5522992418257",
    "linkedin": "https://linkedin.com/in/rafael-r-a3946a15",
}

JOBS = [
  {
    "board": "oscar",
    "company": "Oscar",
    "title": "Analytics Engineer I",
    "url": "http://www.hioscar.com/careers/7872595?gh_jid=7872595",
    "jid": "gh_7872595"
  },
  {
    "board": "oscar",
    "company": "Oscar",
    "title": "Lead Analytics Engineer",
    "url": "http://www.hioscar.com/careers/7809846?gh_jid=7809846",
    "jid": "gh_7809846"
  },
  {
    "board": "roblox",
    "company": "Roblox",
    "title": "Data Analyst, Operations (IP & Legal Compliance)",
    "url": "https://careers.roblox.com/jobs/7856888?gh_jid=7856888",
    "jid": "gh_7856888"
  },
  {
    "board": "roblox",
    "company": "Roblox",
    "title": "Finance Analytics Engineer",
    "url": "https://careers.roblox.com/jobs/7546358?gh_jid=7546358",
    "jid": "gh_7546358"
  },
  {
    "board": "roblox",
    "company": "Roblox",
    "title": "Senior Risk Data Analyst",
    "url": "https://careers.roblox.com/jobs/7514942?gh_jid=7514942",
    "jid": "gh_7514942"
  },
  {
    "board": "wpp",
    "company": "Wpp",
    "title": "Business Intelligence Developer",
    "url": "https://job-boards.greenhouse.io/wpp/jobs/8539089002",
    "jid": "gh_8539089002"
  },
  {
    "board": "wpp",
    "company": "Wpp",
    "title": "Data Analyst (Procurement & REWS)",
    "url": "https://job-boards.greenhouse.io/wpp/jobs/8393841002",
    "jid": "gh_8393841002"
  },
  {
    "board": "wpp",
    "company": "Wpp",
    "title": "GL Reporting Analyst",
    "url": "https://job-boards.greenhouse.io/wpp/jobs/8504923002",
    "jid": "gh_8504923002"
  },
  {
    "board": "smartsheet",
    "company": "Smartsheet",
    "title": "Director, Analytics Engineering & BI Platform (Remote Eligible)",
    "url": "https://job-boards.greenhouse.io/smartsheet/jobs/7951990",
    "jid": "gh_7951990"
  },
  {
    "board": "smartsheet",
    "company": "Smartsheet",
    "title": "Sr. Analytics Engineer - Data Warehouse (Hybrid, Bangalore)",
    "url": "https://job-boards.greenhouse.io/smartsheet/jobs/7960582",
    "jid": "gh_7960582"
  },
  {
    "board": "smartsheet",
    "company": "Smartsheet",
    "title": "Sr. Business Intelligence Engineer, Enterprise Intelligence (Hybrid, Bangalore)",
    "url": "https://job-boards.greenhouse.io/smartsheet/jobs/7835513",
    "jid": "gh_7835513"
  },
  {
    "board": "smartsheet",
    "company": "Smartsheet",
    "title": "Sr. Data Analyst GTM Strategy & Operations, EMEA",
    "url": "https://job-boards.greenhouse.io/smartsheet/jobs/7662421",
    "jid": "gh_7662421"
  },
  {
    "board": "wpp",
    "company": "Wpp",
    "title": "Business Intelligence Developer",
    "url": "https://job-boards.greenhouse.io/wpp/jobs/8539089002",
    "jid": "gh_8539089002"
  },
  {
    "board": "wpp",
    "company": "Wpp",
    "title": "Data Analyst (Procurement & REWS)",
    "url": "https://job-boards.greenhouse.io/wpp/jobs/8393841002",
    "jid": "gh_8393841002"
  },
  {
    "board": "wpp",
    "company": "Wpp",
    "title": "GL Reporting Analyst",
    "url": "https://job-boards.greenhouse.io/wpp/jobs/8504923002",
    "jid": "gh_8504923002"
  }
]

def seen(jid):
    h = {"apikey": KEY, "Authorization": "Bearer " + KEY}
    q = urllib.parse.quote(str(jid))
    rq = urllib.request.Request(SUPA + "/rest/v1/job_applications?job_id=eq." + q + "&select=id&limit=1", headers=h)
    try:
        with urllib.request.urlopen(rq, timeout=6) as r:
            return len(json.loads(r.read())) > 0
    except:
        return False

def save(co, role, url, jid, status):
    h = {"apikey": KEY, "Authorization": "Bearer " + KEY, "Content-Type": "application/json"}
    d = {
        "company": co, "role": role, "url": url, "job_id": jid,
        "application_method": "gh_expanded", "status": status,
        "platform": "Greenhouse",
        "applied_at": datetime.datetime.now(datetime.timezone.utc).isoformat(),
        "email": PROF["email"], "country": "US"
    }
    rq = urllib.request.Request(SUPA + "/rest/v1/job_applications",
        data=json.dumps(d).encode(), method="POST", headers=h)
    try:
        with urllib.request.urlopen(rq, timeout=6) as r:
            pass
    except:
        pass

def get_cover(co, role):
    if not AKEY:
        return "15yr Senior DA PL-300 USD 9M savings Power BI Tableau SQL Azure BigQuery available for " + role + " at " + co + "."
    try:
        payload = json.dumps({
            "model": "claude-sonnet-4-20250514",
            "max_tokens": 200,
            "messages": [{"role": "user", "content":
                "2 tight paragraphs cover letter for " + role + " at " + co + ". "
                "Rafael 15yr DA PL-300 USD 9M savings 70pct latency cut Power BI Tableau SQL Azure BigQuery Snowflake. "
                "No greeting no sign-off. Output ONLY the 2 paragraphs."}]
        }).encode()
        rq = urllib.request.Request("https://api.anthropic.com/v1/messages", data=payload,
            headers={"Content-Type": "application/json", "x-api-key": AKEY, "anthropic-version": "2023-06-01"})
        with urllib.request.urlopen(rq, timeout=18) as r:
            return json.loads(r.read())["content"][0]["text"].strip()
    except:
        return "15yr DA PL-300 USD 9M savings available for " + role + " at " + co + "."

def fill_gh_form(ctx, co, role, url, jid):
    pg = ctx.new_page()
    try:
        pg.goto(url, timeout=18000)
        pg.wait_for_load_state("domcontentloaded", timeout=8000)
        time.sleep(1.5)
        if "greenhouse" not in pg.url:
            pg.close()
            return "no_gh"
        cv_text = get_cover(co, role)
        filled = 0
        field_map = [
            ("#first_name", PROF["first"]),
            ("input[name=\'first_name\']", PROF["first"]),
            ("#last_name", PROF["last"]),
            ("input[name=\'last_name\']", PROF["last"]),
            ("#email", PROF["email"]),
            ("input[name=\'email\']", PROF["email"]),
            ("#phone", PROF["phone"]),
            ("input[name=\'phone\']", PROF["phone"]),
        ]
        for sel, val in field_map:
            try:
                el = pg.locator(sel).first
                if el.is_visible(timeout=400):
                    el.clear()
                    el.fill(val)
                    filled += 1
            except:
                pass
        for sel in ["input[name*=\'linkedin\']", "input[id*=\'linkedin\']"]:
            try:
                el = pg.locator(sel).first
                if el.is_visible(timeout=300):
                    el.fill(PROF["linkedin"])
            except:
                pass
        if os.path.exists(CV):
            for sel in ["input[type=\'file\'][name*=\'resume\']", "input[type=\'file\']"]:
                try:
                    el = pg.locator(sel).first
                    if el.count():
                        el.set_input_files(CV)
                        time.sleep(2)
                        break
                except:
                    pass
        for sel in ["textarea[name*=\'cover\']", "#cover_letter_text"]:
            try:
                el = pg.locator(sel).first
                if el.is_visible(timeout=300):
                    el.fill("Dear " + co + " Hiring Team,\n\n" + cv_text + "\n\nBest,\nRafael Rodrigues\n" + PROF["phone"])
            except:
                pass
        if filled >= 2:
            for sel in ["input[type=\'submit\']", "button[type=\'submit\']", "#submit_app"]:
                try:
                    el = pg.locator(sel).first
                    if el.is_visible(timeout=1200):
                        el.click(force=True)
                        time.sleep(5)
                        body = pg.inner_text("body")[:300].lower()
                        pg.close()
                        keywords = ["thank", "received", "submitted", "applied"]
                        return "success" if any(w in body for w in keywords) else "submitted"
                except:
                    pass
        pg.close()
        return "fields_" + str(filled)
    except Exception as e:
        try:
            pg.close()
        except:
            pass
        return "err:" + str(e)[:20]

def main():
    from playwright.sync_api import sync_playwright
    today = datetime.date.today().strftime("%d/%m/%Y")
    print("\n" + chr(9473)*55)
    print("  GH EXPANDED BOARDS " + today + " — " + str(len(JOBS)) + " vagas")
    print(chr(9473)*55 + "\n")
    ok = skip = fail = 0
    with sync_playwright() as pw:
        br = pw.chromium.launch(headless=True, args=[
            "--no-sandbox", "--disable-dev-shm-usage", "--disable-gpu",
            "--disable-blink-features=AutomationControlled"])
        ctx = br.new_context(
            user_agent="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 Chrome/124.0",
            viewport={"width": 1366, "height": 768}, locale="en-US",
            extra_http_headers={"Accept-Language": "en-US,en;q=0.9"})
        ctx.add_init_script("Object.defineProperty(navigator, \'webdriver\', {get: () => undefined})")
        for job in JOBS:
            jid = job["jid"]
            co = job["company"]
            role = job["title"]
            url = job["url"]
            if seen(jid):
                skip += 1
                continue
            print("  " + co[:20].ljust(20) + " " + role[:38], end=" ", flush=True)
            res = fill_gh_form(ctx, co, role, url, jid)
            icon = "✅" if res in ["success", "submitted"] else "⚠️"
            print("→ " + icon + " " + res)
            save(co, role, url, jid, res)
            if res in ["success", "submitted"]:
                ok += 1
            else:
                fail += 1
            time.sleep(1.2)
        br.close()
    print("\n" + chr(9473)*55)
    print("  ✅ " + str(ok) + " aplicadas | ⏭️ " + str(skip) + " já feitas | ⚠️ " + str(fail) + " falhas")
    print(chr(9473)*55 + "\n")

if __name__ == "__main__":
    main()
