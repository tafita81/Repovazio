#!/usr/bin/env python3
"""
DICE EASY APPLY v3
Usa DICE_ACCESS_TOKEN (GitHub Secret) para autenticar e aplicar
"""
import os, json, time, re, datetime, urllib.request, urllib.parse

SUPA = os.environ.get("SUPABASE_URL","https://tpjvalzwkqwttvmszvie.supabase.co")
KEY  = os.environ.get("SUPABASE_ANON_KEY","")
AKEY = os.environ.get("ANTHROPIC_API_KEY","")
CV   = ".github/assets/rafael_cv.pdf"
PROF = {"first":"Rafael","last":"Rodrigues","email":"Rafa_roberto2004@yahoo.com.br",
        "phone":"+5522992418257","linkedin":"https://linkedin.com/in/rafael-r-a3946a15"}
KW   = ["data analyst","power bi","business intelligence","bi developer",
        "analytics engineer","reporting analyst","tableau","bi analyst"]

# Tokens via GitHub Secrets
DICE_ACCESS  = os.environ.get("DICE_ACCESS_TOKEN","")
DICE_REFRESH = os.environ.get("DICE_REFRESH_TOKEN","")

def seen(jid):
    h = {"apikey":KEY,"Authorization":"Bearer "+KEY}
    rq = urllib.request.Request(
        SUPA+"/rest/v1/job_applications?job_id=eq."+urllib.parse.quote(str(jid))+"&select=id&limit=1",
        headers=h)
    try:
        with urllib.request.urlopen(rq,timeout=6) as r: return len(json.loads(r.read()))>0
    except: return False

def save(co, role, url, jid, status):
    h = {"apikey":KEY,"Authorization":"Bearer "+KEY,"Content-Type":"application/json"}
    d = {"company":co,"role":role,"url":url,"job_id":str(jid),
         "application_method":"dice_easy_apply_v3","status":status,"platform":"Dice",
         "applied_at":datetime.datetime.now(datetime.timezone.utc).isoformat(),
         "email":PROF["email"],"country":"US"}
    rq = urllib.request.Request(SUPA+"/rest/v1/job_applications",
        data=json.dumps(d).encode(), method="POST", headers=h)
    try:
        with urllib.request.urlopen(rq,timeout=6) as r: pass
    except: pass

def search_easy_apply(access_token, query):
    jobs = []
    try:
        url = ("https://job-search-api.svc.dhigroupinc.com/v1/dice/jobs/search"
               "?q="+urllib.parse.quote(query)+
               "&countryCode2=US&radius=30&radiusUnit=mi&page=1&pageSize=20"
               "&filters.easyApply=true")
        rq = urllib.request.Request(url, headers={
            "User-Agent":"Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)",
            "x-api-key":"1YAt0R9wBg4WfsF9VB2778F4BkEFeDe0",
            "Cookie":"access="+access_token,
            "Origin":"https://www.dice.com",
        })
        with urllib.request.urlopen(rq, timeout=10) as r:
            data = json.loads(r.read())
        for j in data.get("data",[]):
            if j.get("easyApply") and any(k in j.get("title","").lower() for k in KW):
                jobs.append(j)
    except Exception as e:
        print(f"    search err: {str(e)[:50]}")
    return jobs

def apply_via_playwright(ctx, access_token, guid, co, role):
    pg = ctx.new_page()
    try:
        # Injetar cookie de sessão
        ctx.add_cookies([{
            "name":"access","value":access_token,
            "domain":".dice.com","path":"/","secure":True,"httpOnly":True
        }])
        url = f"https://www.dice.com/job-detail/{guid}"
        pg.goto(url, timeout=15000)
        pg.wait_for_load_state("domcontentloaded", timeout=8000)
        time.sleep(2)

        body = pg.inner_text("body")
        if "Applied" in body:
            pg.close()
            return "already_applied"

        # Clicar Easy Apply
        for sel in ["button:has-text('Easy Apply')","[data-cy='easy-apply-btn']",
                    "button.btn--primary","button[class*='apply' i]"]:
            try:
                el = pg.locator(sel).first
                if el.is_visible(timeout=2000):
                    el.click(); time.sleep(3)
                    # Tentar submeter
                    for sub_sel in ["button:has-text('Submit')","button:has-text('Apply Now')",
                                    "button[type='submit']"]:
                        try:
                            sub = pg.locator(sub_sel).first
                            if sub.is_visible(timeout=1200):
                                sub.click(); time.sleep(4)
                                pg.close()
                                return "success"
                        except: pass
                    pg.close()
                    return "modal_clicked"
            except: pass

        pg.close()
        return "no_btn"
    except Exception as e:
        try: pg.close()
        except: pass
        return "err:"+str(e)[:20]

def main():
    today = datetime.date.today().strftime("%d/%m/%Y")
    print("\n"+"━"*55)
    print(f"  🎲 DICE EASY APPLY v3 — {today}")
    print("━"*55+"\n")

    if not DICE_ACCESS:
        print("  ❌ DICE_ACCESS_TOKEN não configurado")
        return

    print(f"  ✅ Token: {DICE_ACCESS[:15]}... ({len(DICE_ACCESS)} chars)")

    # Buscar vagas Easy Apply
    all_jobs = []
    for q in ["power bi", "data analyst", "business intelligence analyst",
              "analytics engineer", "tableau developer", "bi developer"]:
        jobs = search_easy_apply(DICE_ACCESS, q)
        for j in jobs:
            if not any(x["guid"]==j["guid"] for x in all_jobs):
                all_jobs.append(j)
        time.sleep(0.3)

    new_jobs = [j for j in all_jobs if not seen(f"dice_v3_{j['guid'][:12]}")]
    print(f"  Encontradas: {len(all_jobs)} | Novas: {len(new_jobs)}")

    if not new_jobs:
        print("  Todas as vagas já foram processadas\n")
        return

    ok = fail = 0
    from playwright.sync_api import sync_playwright
    with sync_playwright() as pw:
        br = pw.chromium.launch(headless=True, args=[
            "--no-sandbox","--disable-dev-shm-usage","--disable-gpu",
            "--disable-blink-features=AutomationControlled"])
        ctx = br.new_context(
            user_agent="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 Chrome/124.0.0.0 Safari/537.36",
            viewport={"width":1366,"height":768}, locale="en-US")
        ctx.add_init_script("Object.defineProperty(navigator,'webdriver',{get:()=>undefined});window.chrome={runtime:{}};")

        for j in new_jobs[:20]:
            co   = j.get("companyName","?")
            role = j.get("title","?")
            guid = j.get("guid","")
            sal  = j.get("salary","")
            jid  = f"dice_v3_{guid[:12]}"
            if seen(jid): continue

            print(f"  {co[:22]:<22} {role[:36]}", end=" ", flush=True)
            if sal: print(f"[{sal[:12]}]", end=" ", flush=True)

            res = apply_via_playwright(ctx, DICE_ACCESS, guid, co, role)
            icon = "✅" if res in ["success","already_applied"] else "📋"
            print(f"→ {icon} {res}")

            save(co, role, f"https://www.dice.com/job-detail/{guid}", jid, res)
            if res in ["success","already_applied"]: ok += 1
            else: fail += 1
            time.sleep(1.5)

        br.close()

    print(f"\n  ✅ {ok} aplicadas | ⚠️ {fail} outros")
    print("━"*55+"\n")

if __name__ == "__main__":
    main()
