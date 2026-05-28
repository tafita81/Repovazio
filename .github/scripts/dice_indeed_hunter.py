#!/usr/bin/env python3
"""
DICE + INDEED HUNTER — Rastreia vagas e navega para aplicar
Usa API Dice pública + Indeed RSS
Rafael Rodrigues | +5522992418257
"""
import os,time,json,hashlib,datetime,urllib.request,urllib.parse,re
from playwright.sync_api import sync_playwright, TimeoutError as PWTimeout

SUPA  = os.environ.get("SUPABASE_URL","https://tpjvalzwkqwttvmszvie.supabase.co")
KEY   = os.environ.get("SUPABASE_ANON_KEY","")
PHONE = "+5522992418257"
EMAIL = "Rafa_roberto2004@yahoo.com.br"
CV    = ".github/assets/rafael_cv.pdf"

KWORDS = ["data analyst","power bi","business intelligence","analytics engineer",
          "bi developer","bi analyst","reporting analyst","data visualization"]
def chk(t): return any(k in (t or "").lower() for k in KWORDS)

def supa_post(table,data):
    req = urllib.request.Request(f"{SUPA}/rest/v1/{table}",
        data=json.dumps(data).encode(),method="POST",
        headers={"apikey":KEY,"Authorization":f"Bearer {KEY}",
                 "Content-Type":"application/json","Prefer":"return=minimal"})
    try:
        with urllib.request.urlopen(req,timeout=8) as r: return r.status
    except: return 0

def is_applied(eid):
    url = f"{SUPA}/rest/v1/job_leads?external_id=eq.{urllib.parse.quote(str(eid))}&applied=eq.true&select=id&limit=1"
    req = urllib.request.Request(url,headers={"apikey":KEY,"Authorization":f"Bearer {KEY}"})
    try:
        with urllib.request.urlopen(req,timeout=6) as r: return len(json.loads(r.read()))>0
    except: return False

def mark(eid,co,role,url,platform):
    now = datetime.datetime.now(datetime.timezone.utc).isoformat()
    supa_post("job_leads",{"external_id":str(eid),"company":co,"role":role,
        "url":url,"platform":platform,"applied":True,"applied_at":now,"ats_type":platform.lower()})
    supa_post("job_applications",{"company":co,"role":role,"url":url,
        "application_method":platform.lower(),"status":"opened","platform":platform})

# ── DICE via API pública ──────────────────────────────────────────────────────
def search_dice():
    jobs = []
    searches = ["power+bi+developer","data+analyst+remote","analytics+engineer+remote"]
    for q in searches:
        try:
            url = (f"https://job-search-api.svc.dhigroupinc.com/v1/dice/jobs/search"
                   f"?q={q}&countryCode2=US&radius=30&radiusUnit=mi"
                   f"&page=1&pageSize=20&facets=employmentType|postedDate|workFromHomeAvailability"
                   f"&filters.workplaceTypes=Remote&filters.employmentType=FULLTIME"
                   f"&fields=id,title,companyName,employmentType,workplaceTypes,salary,postedDate,detailsPageUrl")
            req = urllib.request.Request(url,headers={
                "User-Agent":"Mozilla/5.0","x-api-key":"1YAt0R9wBg4WfsF9VB2778F4BkEFeDe0"})
            with urllib.request.urlopen(req,timeout=10) as r:
                data = json.loads(r.read())
            for j in data.get("data",[]):
                if chk(j.get("title","")):
                    jid = j.get("id") or j.get("guid","")
                    jobs.append({"id":f"dice_{jid}","co":j.get("companyName","?"),
                        "title":j.get("title",""),"url":j.get("detailsPageUrl",""),
                        "platform":"Dice","salary":j.get("salary","")})
            time.sleep(0.5)
        except: pass
    # Dedup
    seen=set(); uniq=[]
    for j in jobs:
        if j["id"] not in seen: seen.add(j["id"]); uniq.append(j)
    return uniq

# ── INDEED via RSS ────────────────────────────────────────────────────────────
def search_indeed():
    jobs = []
    feeds = [
        "https://www.indeed.com/rss?q=power+bi+developer&l=remote&jt=fulltime&sort=date",
        "https://www.indeed.com/rss?q=senior+data+analyst+remote&jt=fulltime&sort=date",
        "https://www.indeed.com/rss?q=analytics+engineer+remote&jt=fulltime&sort=date",
    ]
    for url in feeds:
        try:
            req = urllib.request.Request(url,headers={"User-Agent":"Mozilla/5.0"})
            with urllib.request.urlopen(req,timeout=10) as r:
                rss = r.read().decode("utf-8","ignore")
            items = re.findall(r"<item>(.*?)</item>",rss,re.DOTALL)
            for item in items:
                t = re.search(r"<title><!\[CDATA\[(.*?)\]\]>",item)
                l = re.search(r"<link>(.*?)</link>",item)
                g = re.search(r"<guid[^>]*>(.*?)</guid>",item)
                co= re.search(r"<source[^>]*>(.*?)</source>",item)
                if t and chk(t.group(1)):
                    jid = g.group(1) if g else hashlib.md5(t.group(1).encode()).hexdigest()[:10]
                    jobs.append({"id":f"indeed_{hashlib.md5(jid.encode()).hexdigest()[:10]}",
                        "co":co.group(1) if co else "?","title":t.group(1),
                        "url":l.group(1) if l else "","platform":"Indeed"})
            time.sleep(0.5)
        except: pass
    seen=set(); uniq=[]
    for j in jobs:
        if j["id"] not in seen: seen.add(j["id"]); uniq.append(j)
    return uniq

# ── Navegar para a vaga e tentar aplicar / registrar ─────────────────────────
def process_job(page, job):
    """Navega até a vaga, verifica se tem Greenhouse/Lever, registra"""
    if not job.get("url"): return "no_url"
    try:
        page.goto(job["url"],timeout=20000)
        page.wait_for_load_state("domcontentloaded",timeout=10000); time.sleep(2)
        final = page.url
        # Se redirecionou para Greenhouse, aplicar
        if "greenhouse.io" in final or "boards.greenhouse.io" in final:
            for sel,val in [("input[name='first_name']","Rafael"),
                            ("input[name='last_name']","Rodrigues"),
                            ("input[name='email']",EMAIL),("input[name='phone']",PHONE)]:
                try:
                    el=page.locator(sel).first
                    if el.is_visible(timeout=800): el.fill(val)
                except: pass
            if os.path.exists(CV):
                try:
                    fi=page.locator("input[type='file'][name='resume']").first
                    if fi.count(): fi.set_input_files(CV); time.sleep(1)
                except: pass
            for sel in ["input[type='submit']","button[type='submit']:has-text('Submit')"]:
                try:
                    el=page.locator(sel).first
                    if el.is_visible(timeout=1000): el.click(); time.sleep(3); return "success_gh"
                except: pass
        return "navigated"
    except PWTimeout: return "timeout"
    except Exception as e: return f"err:{str(e)[:30]}"

def main():
    today = datetime.date.today().strftime("%d/%m/%Y")
    print(f"\n{'='*60}")
    print(f"  DICE + INDEED HUNTER — {today}")
    print(f"{'='*60}\n")
    print("Buscando no Dice...",end=" ",flush=True)
    dice_jobs = search_dice(); print(f"{len(dice_jobs)} vagas")
    print("Buscando no Indeed...",end=" ",flush=True)
    indeed_jobs = search_indeed(); print(f"{len(indeed_jobs)} vagas")
    all_jobs = dice_jobs + indeed_jobs
    new = [j for j in all_jobs if not is_applied(j["id"])]
    print(f"\nTotal: {len(all_jobs)} | Novas: {len(new)}\n")
    if not new: print("✅ Nenhuma nova."); return
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True,args=["--no-sandbox","--disable-dev-shm-usage"])
        ctx = browser.new_context(
            user_agent="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36",
            viewport={"width":1280,"height":800})
        ctx.add_init_script("Object.defineProperty(navigator,'webdriver',{get:()=>undefined})")
        ok=0
        for i,job in enumerate(new[:30],1):
            page=ctx.new_page()
            print(f"  [{i:2}/{min(len(new),30)}] [{job['platform']:6}] {job['co'][:20]:<22} {job['title'][:38]}",end=" ",flush=True)
            result=process_job(page,job)
            icon="✅" if "success" in result else "📋"
            print(f"{icon} {result}")
            mark(job["id"],job["co"],job["title"],job["url"],job["platform"])
            if "success" in result: ok+=1
            try: page.close()
            except: pass
            time.sleep(2)
        browser.close()
    print(f"\n  ✅ {ok} via GH | {len(new)-ok} registradas | {today}")

if __name__ == "__main__":
    main()
