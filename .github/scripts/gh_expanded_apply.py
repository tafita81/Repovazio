#!/usr/bin/env python3
"""Apply to expanded GH boards — 17 novas vagas"""
import os,json,time,datetime,urllib.request,urllib.parse

SUPA=os.environ.get("SUPABASE_URL","https://tpjvalzwkqwttvmszvie.supabase.co")
KEY=os.environ.get("SUPABASE_ANON_KEY","")
AKEY=os.environ.get("ANTHROPIC_API_KEY","")
CV=".github/assets/rafael_cv.pdf"
PROF={"first":"Rafael","last":"Rodrigues","email":"Rafa_roberto2004@yahoo.com.br",
       "phone":"+5522992418257","linkedin":"https://linkedin.com/in/rafael-r-a3946a15"}

JOBS = [
  {
    "board": "oscar",
    "title": "Analytics Engineer I",
    "url": "http://www.hioscar.com/careers/7872595?gh_jid=7872595",
    "jid": "gh_7872595",
    "company": "Oscar"
  },
  {
    "board": "oscar",
    "title": "Lead Analytics Engineer",
    "url": "http://www.hioscar.com/careers/7809846?gh_jid=7809846",
    "jid": "gh_7809846",
    "company": "Oscar"
  },
  {
    "board": "roblox",
    "title": "Data Analyst, Operations (IP & Legal Compliance)",
    "url": "https://careers.roblox.com/jobs/7856888?gh_jid=7856888",
    "jid": "gh_7856888",
    "company": "Roblox"
  },
  {
    "board": "roblox",
    "title": "Finance Analytics Engineer",
    "url": "https://careers.roblox.com/jobs/7546358?gh_jid=7546358",
    "jid": "gh_7546358",
    "company": "Roblox"
  },
  {
    "board": "roblox",
    "title": "Senior Risk Data Analyst",
    "url": "https://careers.roblox.com/jobs/7514942?gh_jid=7514942",
    "jid": "gh_7514942",
    "company": "Roblox"
  },
  {
    "board": "wpp",
    "title": "Business Intelligence Developer",
    "url": "https://job-boards.greenhouse.io/wpp/jobs/8539089002",
    "jid": "gh_8539089002",
    "company": "Wpp"
  },
  {
    "board": "wpp",
    "title": "Data Analyst (Procurement & REWS)",
    "url": "https://job-boards.greenhouse.io/wpp/jobs/8393841002",
    "jid": "gh_8393841002",
    "company": "Wpp"
  },
  {
    "board": "wpp",
    "title": "GL Reporting Analyst",
    "url": "https://job-boards.greenhouse.io/wpp/jobs/8504923002",
    "jid": "gh_8504923002",
    "company": "Wpp"
  },
  {
    "board": "smartsheet",
    "title": "Director, Analytics Engineering & BI Platform (Remote Eligible)",
    "url": "https://job-boards.greenhouse.io/smartsheet/jobs/7951990",
    "jid": "gh_7951990",
    "company": "Smartsheet"
  },
  {
    "board": "smartsheet",
    "title": "Sr. Analytics Engineer - Data Warehouse (Hybrid, Bangalore)",
    "url": "https://job-boards.greenhouse.io/smartsheet/jobs/7960582",
    "jid": "gh_7960582",
    "company": "Smartsheet"
  },
  {
    "board": "smartsheet",
    "title": "Sr. Business Intelligence Engineer, Enterprise Intelligence (Hybrid, Bangalore)",
    "url": "https://job-boards.greenhouse.io/smartsheet/jobs/7835513",
    "jid": "gh_7835513",
    "company": "Smartsheet"
  },
  {
    "board": "smartsheet",
    "title": "Sr. Data Analyst GTM Strategy & Operations, EMEA",
    "url": "https://job-boards.greenhouse.io/smartsheet/jobs/7662421",
    "jid": "gh_7662421",
    "company": "Smartsheet"
  },
  {
    "board": "oscar",
    "title": "Analytics Engineer I",
    "url": "http://www.hioscar.com/careers/7872595?gh_jid=7872595",
    "jid": "gh_7872595",
    "company": "Oscar"
  },
  {
    "board": "oscar",
    "title": "Lead Analytics Engineer",
    "url": "http://www.hioscar.com/careers/7809846?gh_jid=7809846",
    "jid": "gh_7809846",
    "company": "Oscar"
  },
  {
    "board": "wpp",
    "title": "Business Intelligence Developer",
    "url": "https://job-boards.greenhouse.io/wpp/jobs/8539089002",
    "jid": "gh_8539089002",
    "company": "Wpp"
  },
  {
    "board": "wpp",
    "title": "Data Analyst (Procurement & REWS)",
    "url": "https://job-boards.greenhouse.io/wpp/jobs/8393841002",
    "jid": "gh_8393841002",
    "company": "Wpp"
  },
  {
    "board": "wpp",
    "title": "GL Reporting Analyst",
    "url": "https://job-boards.greenhouse.io/wpp/jobs/8504923002",
    "jid": "gh_8504923002",
    "company": "Wpp"
  }
]

def seen(jid):
    h={"apikey":KEY,"Authorization":f"Bearer {KEY}"}
    rq=urllib.request.Request(f"{SUPA}/rest/v1/job_applications?job_id=eq.{urllib.parse.quote(str(jid))}&select=id&limit=1",headers=h)
    try:
        with urllib.request.urlopen(rq,timeout=6) as r: return len(json.loads(r.read()))>0
    except: return False

def save(co,role,url,jid,status):
    h={"apikey":KEY,"Authorization":f"Bearer {KEY}","Content-Type":"application/json"}
    d={"company":co,"role":role,"url":url,"job_id":jid,"application_method":"gh_expanded",
        "status":status,"platform":"Greenhouse","applied_at":datetime.datetime.now(datetime.timezone.utc).isoformat(),
        "email":PROF["email"],"country":"US"}
    rq=urllib.request.Request(f"{SUPA}/rest/v1/job_applications",
        data=json.dumps(d).encode(),method="POST",headers=h)
    try:
        with urllib.request.urlopen(rq,timeout=6) as r: pass
    except: pass

def cover(co,role):
    if not AKEY:
        return f"15yr Senior DA PL-300 USD 9M savings available for {role} at {co}."
    try:
        p=json.dumps({"model":"claude-sonnet-4-20250514","max_tokens":200,
            "messages":[{"role":"user","content":
                f"2 tight paragraphs cover letter {role} at {co}. "
                f"Rafael 15yr DA PL-300 USD 9M savings 70pct latency Power BI Tableau SQL Azure BigQuery. "
                f"No greeting no sign-off. Only paragraphs."}]}).encode()
        rq=urllib.request.Request("https://api.anthropic.com/v1/messages",data=p,
            headers={"Content-Type":"application/json","x-api-key":AKEY,"anthropic-version":"2023-06-01"})
        with urllib.request.urlopen(rq,timeout=18) as r:
            return json.loads(r.read())["content"][0]["text"].strip()
    except: return f"15yr DA PL-300 USD 9M savings for {role} at {co}."

def main():
    from playwright.sync_api import sync_playwright
    ok=skip=fail=0
    today=datetime.date.today().strftime("%d/%m/%Y")
    print(f"\n{chr(9473)*55}")
    print(f"  GH EXPANDED BOARDS — {today} — {len(JOBS)} vagas")
    print(f"{chr(9473)*55}\n")
    with sync_playwright() as pw:
        br=pw.chromium.launch(headless=True,args=["--no-sandbox","--disable-dev-shm-usage","--disable-gpu","--disable-blink-features=AutomationControlled"])
        ctx=br.new_context(user_agent="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 Chrome/124.0",viewport={"width":1366,"height":768},locale="en-US")
        ctx.add_init_script("Object.defineProperty(navigator,\'webdriver\',{get:()=>undefined})")
        for job in JOBS:
            jid=job["jid"]; co=job["company"]; role=job["title"]; url=job["url"]
            if seen(jid): skip+=1; continue
            print(f"  {co[:20]:<20} {role[:38]}", end=" ", flush=True)
            pg=ctx.new_page()
            try:
                pg.goto(url,timeout=18000); pg.wait_for_load_state("domcontentloaded",timeout=8000); time.sleep(1.5)
                if "greenhouse" not in pg.url: pg.close(); print("→ ⚠️ no_gh"); save(co,role,url,jid,"no_gh"); fail+=1; continue
                cv_txt=cover(co,role); filled=0
                for sel,val in [("#first_name,input[name=\'first_name\']",PROF["first"]),
                                ("#last_name,input[name=\'last_name\']",PROF["last"]),
                                ("#email,input[name=\'email\']",PROF["email"]),
                                ("#phone,input[name=\'phone\']",PROF["phone"])]:
                    for s in sel.split(","):
                        try:
                            el=pg.locator(s.strip()).first
                            if el.is_visible(timeout=400): el.clear(); el.fill(val); filled+=1; break
                        except: pass
                for sel in ["input[name*=\'linkedin\']","input[id*=\'linkedin\']"]:
                    try:
                        el=pg.locator(sel).first
                        if el.is_visible(timeout=300): el.fill(PROF["linkedin"])
                    except: pass
                if os.path.exists(CV):
                    for sel in ["input[type=\'file\'][name*=\'resume\']","input[type=\'file\']"]:
                        try:
                            el=pg.locator(sel).first
                            if el.count(): el.set_input_files(CV); time.sleep(2); break
                        except: pass
                for sel in ["textarea[name*=\'cover\']","#cover_letter_text"]:
                    try:
                        el=pg.locator(sel).first
                        if el.is_visible(timeout=300):
                            el.fill(f"Dear {co} Hiring Team,\n\n{cv_txt}\n\nBest,\nRafael Rodrigues\n{PROF[\'phone\']}")
                    except: pass
                if filled>=2:
                    for sel in ["input[type=\'submit\']","button[type=\'submit\']","#submit_app"]:
                        try:
                            el=pg.locator(sel).first
                            if el.is_visible(timeout=1200):
                                el.click(force=True); time.sleep(5)
                                body=pg.inner_text("body")[:300].lower(); pg.close()
                                res="success" if any(w in body for w in ["thank","received","submitted"]) else "submitted"
                                print(f"→ ✅ {res}"); save(co,role,url,jid,res); ok+=1
                                break
                        except: pass
                    else:
                        pg.close(); print(f"→ ⚠️ fields_{filled}"); save(co,role,url,jid,f"fields_{filled}"); fail+=1
                else:
                    pg.close(); print(f"→ ⚠️ fields_{filled}"); save(co,role,url,jid,f"fields_{filled}"); fail+=1
            except Exception as e:
                try: pg.close()
                except: pass
                print(f"→ ❌ {str(e)[:25]}"); save(co,role,url,jid,"err"); fail+=1
            time.sleep(1.2)
        br.close()
    print(f"\n{chr(9473)*55}")
    print(f"  ✅ {ok} aplicadas | ⏭️ {skip} já feitas | ⚠️ {fail} falhas")
    print(f"{chr(9473)*55}\n")

if __name__=="__main__":
    main()
