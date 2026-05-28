#!/usr/bin/env python3
"""
PLATFORM FIXER v2 — abordagem correta
- LinkedIn: usa API guest /jobs-guest/jobs/api/jobPosting/{id} → retorna applyURL direto
- Dice: Playwright visita página renderizada → extrai link Apply
- RemoteOK: usa apply_url da API diretamente
- ZipRecruiter: usa MCP search + API pública
- Wellfound: Playwright → extrai apply link
- Jobright: API correta + segue redirect
"""
import os, sys, json, time, re, datetime, urllib.request, urllib.parse, smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.application import MIMEApplication

SUPA = os.environ.get("SUPABASE_URL","https://tpjvalzwkqwttvmszvie.supabase.co")
KEY  = os.environ.get("SUPABASE_ANON_KEY","")
GMAIL= os.environ.get("GMAIL_APP_PASSWORD","")
AKEY = os.environ.get("ANTHROPIC_API_KEY","")
EM   = os.environ.get("DICE_EMAIL","tafita81@gmail.com")
PW   = os.environ.get("DICE_PASSWORD","Daniela1982@")
CV   = ".github/assets/rafael_cv.pdf"
UA   = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 Chrome/124.0"
PROF = {"first":"Rafael","last":"Rodrigues","email":"Rafa_roberto2004@yahoo.com.br",
        "phone":"+5522992418257","linkedin":"https://linkedin.com/in/rafael-r-a3946a15"}
KW   = ["data analyst","power bi","business intelligence","bi developer",
        "analytics engineer","reporting analyst","tableau","bi analyst","bi developer"]
BOUNCE = {"hire@turing.com","work@andela.com","talent@toptal.com","hey@lemon.io"}

def sb(m,p,d=None):
    h={"apikey":KEY,"Authorization":f"Bearer {KEY}","Content-Type":"application/json"}
    rq=urllib.request.Request(f"{SUPA}/rest/v1/{p}",
       data=json.dumps(d).encode() if d else None,method=m,headers=h)
    try:
        with urllib.request.urlopen(rq,timeout=8) as r:
            return json.loads(r.read()) if m=="GET" else r.status
    except Exception as e: return 409 if "409" in str(e) else None

def seen(jid):
    r=sb("GET",f"job_applications?job_id=eq.{urllib.parse.quote(str(jid))}&select=id&limit=1")
    return isinstance(r,list) and len(r)>0

def save(co,role,url,jid,status,platform,method,salary="",country="US"):
    sb("POST","job_applications",{
        "company":co,"role":role,"url":url,"job_id":str(jid),
        "application_method":method,"status":status,"platform":platform,
        "applied_at":datetime.datetime.now(datetime.timezone.utc).isoformat(),
        "email":PROF["email"],"salary":salary,"country":country})

def detect_ats(url):
    if not url: return None
    u=url.lower()
    for k,v in [("greenhouse","gh"),("lever.co","lever"),("ashbyhq","ashby"),
                ("workday","workday"),("myworkdayjobs","workday"),("icims","icims"),
                ("smartrecruit","smart"),("jobvite","jobvite")]:
        if k in u: return v
    return None

def cover_letter(co,role):
    if not AKEY:
        return (f"15yr Senior Data Analyst, PL-300, USD 9M+ savings. "
                f"Power BI+Tableau+SQL+Azure+BigQuery. Available for {role} at {co}.")
    try:
        p=json.dumps({"model":"claude-sonnet-4-20250514","max_tokens":250,
            "messages":[{"role":"user","content":
                f"2 tight paragraphs: {role} at {co}. Rafael: 15yr DA, PL-300, "
                f"USD 9M+ savings, 70% latency cut, Power BI+Tableau+SQL+Azure+BigQuery+Snowflake. "
                f"No greeting/sign-off. Output ONLY paragraphs."}]}).encode()
        rq=urllib.request.Request("https://api.anthropic.com/v1/messages",data=p,
            headers={"Content-Type":"application/json","x-api-key":AKEY,"anthropic-version":"2023-06-01"})
        with urllib.request.urlopen(rq,timeout=18) as r:
            return json.loads(r.read())["content"][0]["text"].strip()
    except: return f"15yr DA, PL-300, USD 9M savings. Power BI+Tableau. Available for {role} at {co}."

def send_email(to,co,role):
    if not GMAIL or to in BOUNCE or seen(f"em_{co[:15].lower().replace(' ','')}"): return False
    try:
        msg=MIMEMultipart()
        msg["From"]=f"Rafael Rodrigues <{EM}>"
        msg["To"]=to; msg["Reply-To"]=PROF["email"]
        msg["Subject"]=f"Senior Data Analyst / Power BI — {co}"
        body=f"Dear {co} Hiring Team,\n\n{cover_letter(co,role)}\n\nBest,\nRafael Rodrigues\n{PROF['phone']} | {PROF['email']}"
        msg.attach(MIMEText(body,"plain"))
        if os.path.exists(CV):
            with open(CV,"rb") as f:
                att=MIMEApplication(f.read(),Name="Rafael_Rodrigues_CV.pdf")
                att["Content-Disposition"]='attachment; filename="Rafael_Rodrigues_CV.pdf"'
                msg.attach(att)
        with smtplib.SMTP_SSL("smtp.gmail.com",465) as s:
            s.login(EM,GMAIL); s.send_message(msg)
        save(co,role,f"mailto:{to}",f"em_{co[:15].lower().replace(' ','')}","sent","email","email_cv")
        return True
    except: return False

def fill_gh(ctx,co,role,url,jid):
    pg=ctx.new_page()
    try:
        pg.goto(url,timeout=18000); pg.wait_for_load_state("domcontentloaded",timeout=8000); time.sleep(1.5)
        if "greenhouse" not in pg.url: pg.close(); return "no_gh"
        cv_txt=cover_letter(co,role); filled=0
        for sel,val in [("#first_name,input[name='first_name']",PROF["first"]),
                        ("#last_name,input[name='last_name']",PROF["last"]),
                        ("#email,input[name='email']",PROF["email"]),
                        ("#phone,input[name='phone']",PROF["phone"])]:
            for s in sel.split(","):
                try:
                    el=pg.locator(s.strip()).first
                    if el.is_visible(timeout=400): el.clear(); el.fill(val); filled+=1; break
                except: pass
        for sel in ["input[name*='linkedin']","input[id*='linkedin']"]:
            try:
                el=pg.locator(sel).first
                if el.is_visible(timeout=300): el.fill(PROF["linkedin"])
            except: pass
        if os.path.exists(CV):
            for sel in ["input[type='file'][name*='resume']","input[type='file']"]:
                try:
                    el=pg.locator(sel).first
                    if el.count(): el.set_input_files(CV); time.sleep(2); break
                except: pass
        for sel in ["textarea[name*='cover']","#cover_letter_text"]:
            try:
                el=pg.locator(sel).first
                if el.is_visible(timeout=300):
                    el.fill(f"Dear {co} Hiring Team,\n\n{cv_txt}\n\nBest,\nRafael Rodrigues\n{PROF['phone']}")
            except: pass
        if filled>=2:
            for sel in ["input[type='submit']","button[type='submit']","#submit_app"]:
                try:
                    el=pg.locator(sel).first
                    if el.is_visible(timeout=1200):
                        el.click(force=True); time.sleep(5)
                        body=pg.inner_text("body")[:300].lower(); pg.close()
                        return "success" if any(w in body for w in ["thank","received","submitted"]) else "submitted"
                except: pass
        pg.close(); return f"fields_{filled}"
    except Exception as e: pg.close(); return f"err:{str(e)[:20]}"

def fill_lever(ctx,co,role,url,jid):
    pg=ctx.new_page()
    try:
        pg.goto(url,timeout=18000); pg.wait_for_load_state("domcontentloaded",timeout=8000); time.sleep(1.5)
        if "lever.co" not in pg.url: pg.close(); return "no_lever"
        cv_txt=cover_letter(co,role); filled=0
        for sel,val in [("input[name='name']",f"{PROF['first']} {PROF['last']}"),
                        ("input[name='email']",PROF["email"]),
                        ("input[name='phone']",PROF["phone"]),
                        ("input[name*='linkedin']",PROF["linkedin"])]:
            try:
                el=pg.locator(sel).first
                if el.is_visible(timeout=400): el.fill(val); filled+=1
            except: pass
        try:
            el=pg.locator("textarea[name='comments'],textarea[name='additionalInfo']").first
            if el.is_visible(timeout=300): el.fill(f"Dear {co},\n\n{cv_txt}\n\nBest,\nRafael")
        except: pass
        if os.path.exists(CV):
            try:
                el=pg.locator("input[type='file']").first
                if el.count(): el.set_input_files(CV); time.sleep(2)
            except: pass
        if filled>=2:
            for sel in ["button[type='submit']","button:has-text('Submit application')"]:
                try:
                    el=pg.locator(sel).first
                    if el.is_visible(timeout=1000):
                        el.click(force=True); time.sleep(5)
                        body=pg.inner_text("body")[:200].lower(); pg.close()
                        return "success" if "thank" in body else "submitted"
                except: pass
        pg.close(); return f"lever_f{filled}"
    except Exception as e: pg.close(); return f"err:{str(e)[:20]}"

def apply_via_ats(ctx,co,role,apply_url,jid,platform,salary="",country="US"):
    ats=detect_ats(apply_url)
    if ats=="gh": res=fill_gh(ctx,co,role,apply_url,jid)
    elif ats=="lever": res=fill_lever(ctx,co,role,apply_url,jid)
    elif ats: res=f"ats_{ats}"
    else: res="no_ats"
    save(co,role,apply_url,jid,res,platform,f"{platform.lower()}_ats",salary,country)
    return res

def pw_get_apply_url(ctx, url):
    """Usa Playwright para renderizar página e extrair link de Apply"""
    pg=ctx.new_page()
    try:
        pg.goto(url,timeout=18000); pg.wait_for_load_state("networkidle",timeout=12000); time.sleep(2)
        # Procurar link de Apply na página renderizada
        for sel in ["a[href*='greenhouse']:not([href*='boards.greenhouse'])",
                    "a[href*='lever.co']","a[href*='ashbyhq.com']",
                    "a[href*='workday']","a[href*='myworkdayjobs']",
                    "a:has-text('Apply Now')","a:has-text('Apply now')","a:has-text('Apply')"]:
            try:
                el=pg.locator(sel).first
                if el.is_visible(timeout=500):
                    href=el.get_attribute("href") or ""
                    if href and len(href)>10:
                        # Se for link de apply externo, seguir
                        if detect_ats(href):
                            pg.close(); return href
                        # Se for botão Apply, clicar e ver redirect
                        with pg.expect_navigation(timeout=8000):
                            el.click()
                        new_url=pg.url
                        if detect_ats(new_url):
                            pg.close(); return new_url
                        break
            except: pass
        # Último recurso: extrair do HTML renderizado
        html=pg.content()
        for pat in [r'href="(https://[^"]*greenhouse\.io[^"]*)"',
                    r'href="(https://jobs\.lever\.co[^"]*)"',
                    r'href="(https://[^"]*ashbyhq[^"]*)"',
                    r'"applyUrl"\s*:\s*"([^"]+)"',
                    r'"companyApplyUrl"\s*:\s*"([^"]+)"',
                    r'"apply_url"\s*:\s*"([^"]+)"']:
            m=re.search(pat,html,re.I)
            if m:
                found=m.group(1).replace('\\/','/')
                if detect_ats(found): pg.close(); return found
        pg.close(); return ""
    except Exception as e:
        try: pg.close()
        except: pass
        return ""

# ══════════════════════════════════════════════════════════════════════════════
# FIXERS
# ══════════════════════════════════════════════════════════════════════════════

def fix_linkedin(ctx):
    print("\n  ── LINKEDIN ──────────────────────────────────")
    ok=processed=0
    # LinkedIn guest jobPosting API — retorna applyMethod com applyStartUrl
    for q in ["power bi developer","senior data analyst","analytics engineer","business intelligence analyst"]:
        try:
            raw_html=urllib.request.urlopen(
                urllib.request.Request(
                    f"https://www.linkedin.com/jobs-guest/jobs/api/seeMoreJobPostings/search"
                    f"?keywords={urllib.parse.quote(q)}&location=United+States&f_WT=2&start=0&count=20",
                    headers={"User-Agent":UA,"Accept":"text/html"}),timeout=10).read().decode("utf-8",errors="ignore")
            job_ids=re.findall(r'data-entity-urn="[^"]*jobPosting:(\d+)"',raw_html)
            titles  =re.findall(r'class="base-search-card__title"[^>]*>\s*([^<]+)\s*<',raw_html)
            companies=re.findall(r'class="base-search-card__subtitle"[^>]*>\s*([^<]+)\s*<',raw_html)
            for i,jid_raw in enumerate(job_ids[:12]):
                jid=f"li_{jid_raw}"
                if seen(jid): continue
                co  =(companies[i].strip() if i<len(companies) else "?")
                role=(titles[i].strip() if i<len(titles) else q)
                if not any(k in role.lower() for k in KW): continue
                print(f"    {co[:20]:<20} {role[:32]}",end=" ",flush=True)
                # Usar API de detalhes do job — retorna JSON com applyMethod
                try:
                    detail=urllib.request.urlopen(
                        urllib.request.Request(
                            f"https://www.linkedin.com/jobs-guest/jobs/api/jobPosting/{jid_raw}",
                            headers={"User-Agent":UA}),timeout=8).read().decode("utf-8",errors="ignore")
                    # Extrair apply URL do JSON embutido
                    apply_url=""
                    for pat in [r'"applyStartUrl"\s*:\s*"([^"]+)"',
                                r'"companyApplyUrl"\s*:\s*"([^"]+)"',
                                r'href="(https://[^"]*(?:greenhouse|lever\.co|ashbyhq|workday|myworkday)[^"]*)"']:
                        m=re.search(pat,detail,re.I)
                        if m: apply_url=m.group(1).replace('\\/','\/').replace('\\/','/');\
                              apply_url=apply_url.replace('\\/','/');\
                              break
                except: apply_url=""
                if not apply_url:
                    # Fallback: Playwright renderiza a página
                    apply_url=pw_get_apply_url(ctx,f"https://www.linkedin.com/jobs/view/{jid_raw}/")
                ats=detect_ats(apply_url)
                if ats=="gh":
                    res=fill_gh(ctx,co,role,apply_url,jid)
                elif ats=="lever":
                    res=fill_lever(ctx,co,role,apply_url,jid)
                elif ats:
                    res=f"ats_{ats}"
                    save(co,role,apply_url,jid,res,"LinkedIn","li_ats")
                else:
                    email_try=f"jobs@{re.sub(r'[^a-z]','',co.lower())}.com"
                    res="email_sent" if send_email(email_try,co,role) else "no_apply"
                    save(co,role,f"https://linkedin.com/jobs/view/{jid_raw}/",jid,res,"LinkedIn","li_email")
                icon="✅" if "success" in res or "submit" in res or "email_sent" in res else "📋"
                print(f"→ {icon} {res}")
                if "success" in res or "submit" in res or "email_sent" in res: ok+=1
                processed+=1; time.sleep(1.2)
        except Exception as e: print(f"    ERRO busca: {str(e)[:50]}")
    print(f"  LinkedIn: {processed} processadas, {ok} aplicadas")

def fix_dice(ctx):
    print("\n  ── DICE ──────────────────────────────────────")
    ok=processed=0
    # Buscar vagas via Dice web (scraper do HTML público)
    for q in ["power+bi+developer","senior+data+analyst","analytics+engineer","bi+analyst"]:
        try:
            raw=urllib.request.urlopen(urllib.request.Request(
                f"https://www.dice.com/jobs?q={q}&countryCode2=US&radius=30&radiusUnit=mi"
                f"&page=1&pageSize=20&filters.workplaceTypes=Remote&filters.employmentType=FULLTIME",
                headers={"User-Agent":UA}),timeout=10).read().decode("utf-8",errors="ignore")
            # Extrair guids das vagas
            guids=re.findall(r'"guid"\s*:\s*"([a-f0-9\-]{36})"',raw)
            titles=re.findall(r'"title"\s*:\s*"([^"]{5,80})"',raw)
            companies=re.findall(r'"companyName"\s*:\s*"([^"]{2,60})"',raw)
            for i,guid in enumerate(guids[:15]):
                jid=f"dice_{guid}"
                if seen(jid): continue
                co=(companies[i] if i<len(companies) else "?")
                role=(titles[i] if i<len(titles) else q.replace("+"," "))
                if not any(k in role.lower() for k in KW): continue
                print(f"    {co[:20]:<20} {role[:32]}",end=" ",flush=True)
                # Playwright visita página do job e extrai apply link
                apply_url=pw_get_apply_url(ctx,f"https://www.dice.com/job-detail/{guid}")
                ats=detect_ats(apply_url)
                if ats=="gh": res=fill_gh(ctx,co,role,apply_url,jid)
                elif ats=="lever": res=fill_lever(ctx,co,role,apply_url,jid)
                elif ats: res=f"ats_{ats}"; save(co,role,apply_url,jid,res,"Dice","dice_ats")
                else:
                    # Email direto
                    email_try=f"careers@{re.sub(r'[^a-z]','',co.lower())}.com"
                    res="email_sent" if send_email(email_try,co,role) else "no_apply"
                    save(co,role,f"https://www.dice.com/job-detail/{guid}",jid,res,"Dice","dice_email")
                icon="✅" if "success" in res or "submit" in res or "email_sent" in res else "📋"
                print(f"→ {icon} {res}")
                if "success" in res or "submit" in res or "email_sent" in res: ok+=1
                processed+=1; time.sleep(1.5)
        except Exception as e: print(f"    ERRO: {str(e)[:50]}")
    print(f"  Dice: {processed} processadas, {ok} aplicadas")

def fix_remoteok(ctx):
    print("\n  ── REMOTE OK ─────────────────────────────────")
    ok=processed=0
    try:
        raw=urllib.request.urlopen(urllib.request.Request(
            "https://remoteok.com/api",headers={"User-Agent":UA,"Accept":"application/json"}),
            timeout=10).read().decode("utf-8",errors="ignore")
        jobs=json.loads(raw)[1:]
        for j in jobs:
            if not isinstance(j,dict): continue
            if not any(k in j.get("position","").lower() for k in KW): continue
            jid=f"rok_{j.get('id','')}"
            if seen(jid): continue
            co=j.get("company","?"); role=j.get("position","?")
            apply_url=j.get("apply_url","") or j.get("url","")
            print(f"    {co[:20]:<20} {role[:32]}",end=" ",flush=True)
            ats=detect_ats(apply_url)
            if ats=="gh": res=fill_gh(ctx,co,role,apply_url,jid)
            elif ats=="lever": res=fill_lever(ctx,co,role,apply_url,jid)
            elif apply_url and "mailto:" in apply_url:
                to=apply_url.replace("mailto:","").split("?")[0]
                res="email_sent" if send_email(to,co,role) else "email_failed"
                save(co,role,apply_url,jid,res,"RemoteOK","rok_email")
            elif apply_url:
                # Playwright visita para extrair GH/Lever link
                inner=pw_get_apply_url(ctx,apply_url)
                if detect_ats(inner) in ["gh","lever"]:
                    res=(fill_gh if detect_ats(inner)=="gh" else fill_lever)(ctx,co,role,inner,jid)
                else:
                    email_try=f"jobs@{re.sub(r'[^a-z]','',co.lower())}.com"
                    res="email_sent" if send_email(email_try,co,role) else f"ats_{detect_ats(inner) or 'none'}"
                    save(co,role,inner or apply_url,jid,res,"RemoteOK","rok_apply")
            else: res="no_url"; save(co,role,"",jid,res,"RemoteOK","rok_apply")
            icon="✅" if "success" in res or "submit" in res or "email_sent" in res else "📋"
            print(f"→ {icon} {res}")
            if "success" in res or "submit" in res or "email_sent" in res: ok+=1
            processed+=1; time.sleep(1)
    except Exception as e: print(f"    ERRO: {str(e)[:60]}")
    print(f"  RemoteOK: {processed} processadas, {ok} aplicadas")

def fix_indeed(ctx):
    print("\n  ── INDEED ────────────────────────────────────")
    ok=processed=0
    for q in ["power bi","data analyst","analytics engineer"]:
        for cc in ["us","ca","gb"]:
            try:
                xml=urllib.request.urlopen(urllib.request.Request(
                    f"https://{cc}.indeed.com/rss?q={urllib.parse.quote(q)}"
                    f"&remotejob=032b3046-06a3-4876-8dfd-474eb5e7ed11&sort=date&limit=8",
                    headers={"User-Agent":UA}),timeout=8).read().decode("utf-8",errors="ignore")
                for item in re.findall(r'<item>(.*?)</item>',xml,re.DOTALL)[:5]:
                    title_m=re.search(r'<title>([^<]+)<',item)
                    co_m=re.search(r'<source[^>]*>([^<]+)<',item)
                    link_m=re.search(r'<link>([^<]+)<',item)
                    jk_m=re.search(r'jk=([a-f0-9]+)',item)
                    if not (link_m and jk_m): continue
                    jid=f"indeed_{cc}_{jk_m.group(1)}"
                    if seen(jid): continue
                    co=co_m.group(1) if co_m else "?"
                    role=title_m.group(1) if title_m else q
                    job_url=link_m.group(1)
                    print(f"    [{cc.upper()}] {co[:18]:<18} {role[:30]}",end=" ",flush=True)
                    # Playwright extrai apply URL da página renderizada Indeed
                    apply_url=pw_get_apply_url(ctx,job_url)
                    ats=detect_ats(apply_url)
                    if ats=="gh": res=fill_gh(ctx,co,role,apply_url,jid)
                    elif ats=="lever": res=fill_lever(ctx,co,role,apply_url,jid)
                    elif ats: res=f"ats_{ats}"; save(co,role,apply_url,jid,res,"Indeed","indeed_ats",country=cc.upper())
                    else:
                        email_try=f"careers@{re.sub(r'[^a-z]','',co.lower())}.com"
                        res="email_sent" if send_email(email_try,co,role) else "no_apply"
                        save(co,role,job_url,jid,res,"Indeed","indeed_email",country=cc.upper())
                    icon="✅" if "success" in res or "submit" in res or "email_sent" in res else "📋"
                    print(f"→ {icon} {res}")
                    if "success" in res or "submit" in res or "email_sent" in res: ok+=1
                    processed+=1; time.sleep(1.5)
            except: pass
    print(f"  Indeed: {processed} processadas, {ok} aplicadas")

def fix_wellfound(ctx):
    print("\n  ── WELLFOUND ─────────────────────────────────")
    ok=processed=0
    for q in ["data analyst","power bi","analytics engineer"]:
        try:
            pg=ctx.new_page()
            pg.goto(f"https://wellfound.com/jobs?query={urllib.parse.quote(q)}&remote=true",timeout=18000)
            pg.wait_for_load_state("networkidle",timeout=12000); time.sleep(2)
            # Extrair job cards
            job_links=[]
            for el in pg.locator("a[href*='/jobs/'][href*='-']").all()[:20]:
                try:
                    href=el.get_attribute("href") or ""
                    if "/jobs/" in href and href not in job_links: job_links.append(href)
                except: pass
            pg.close()
            for link in job_links[:10]:
                full_url=f"https://wellfound.com{link}" if link.startswith("/") else link
                jid=f"wf_{re.sub(r'[^a-z0-9]','',link.lower())[:30]}"
                if seen(jid): continue
                pg2=ctx.new_page()
                try:
                    pg2.goto(full_url,timeout=15000); pg2.wait_for_load_state("domcontentloaded",timeout=8000); time.sleep(1.5)
                    title_el=pg2.locator("h1").first
                    co_el=pg2.locator("[class*='company'] a,[class*='startup'] a").first
                    role=title_el.inner_text()[:60] if title_el.count() else "Data Analyst"
                    co=co_el.inner_text()[:40] if co_el.count() else "Wellfound Co"
                    if not any(k in role.lower() for k in KW): pg2.close(); continue
                    print(f"    {co[:20]:<20} {role[:32]}",end=" ",flush=True)
                    apply_url=""
                    for sel in ["a[href*='greenhouse']","a[href*='lever.co']","a[href*='ashbyhq']",
                                "a:has-text('Apply')","button:has-text('Apply')"]:
                        try:
                            el=pg2.locator(sel).first
                            if el.is_visible(timeout=500):
                                href=el.get_attribute("href") or ""
                                if detect_ats(href): apply_url=href; break
                                with pg2.expect_navigation(timeout=6000): el.click()
                                if detect_ats(pg2.url): apply_url=pg2.url; break
                        except: pass
                    pg2.close()
                    if detect_ats(apply_url)=="gh": res=fill_gh(ctx,co,role,apply_url,jid)
                    elif detect_ats(apply_url)=="lever": res=fill_lever(ctx,co,role,apply_url,jid)
                    elif apply_url: res=f"ats_{detect_ats(apply_url) or 'other'}"; save(co,role,apply_url,jid,res,"Wellfound","wf_ats")
                    else:
                        email_try=f"jobs@{re.sub(r'[^a-z]','',co.lower())}.com"
                        res="email_sent" if send_email(email_try,co,role) else "no_apply"
                        save(co,role,full_url,jid,res,"Wellfound","wf_email")
                    icon="✅" if "success" in res or "submit" in res or "email_sent" in res else "📋"
                    print(f"→ {icon} {res}")
                    if "success" in res or "submit" in res or "email_sent" in res: ok+=1
                    processed+=1; time.sleep(1)
                except: 
                    try: pg2.close()
                    except: pass
        except Exception as e: print(f"    ERRO: {str(e)[:50]}")
    print(f"  Wellfound: {processed} processadas, {ok} aplicadas")

def fix_ziprecruiter(ctx):
    print("\n  ── ZIPRECRUITER ──────────────────────────────")
    ok=processed=0
    for q in ["power bi developer","senior data analyst","analytics engineer"]:
        try:
            raw=urllib.request.urlopen(urllib.request.Request(
                f"https://www.ziprecruiter.com/jobs-search?search={urllib.parse.quote(q)}"
                f"&location=Remote&days=7&radius=25",
                headers={"User-Agent":UA,"Accept":"text/html"}),timeout=10).read().decode("utf-8",errors="ignore")
            # Extrair job IDs e apply URLs do HTML
            job_ids=re.findall(r'"jobId"\s*:\s*"([^"]+)"',raw)
            apply_urls=re.findall(r'"applyUrl"\s*:\s*"([^"]+)"',raw)
            job_titles=re.findall(r'"name"\s*:\s*"([^"]{5,80})"',raw)
            job_cos=re.findall(r'"company"\s*:\s*"([^"]{2,60})"',raw)
            for i,jid_raw in enumerate(job_ids[:12]):
                jid=f"zr_{jid_raw[:20]}"
                if seen(jid): continue
                role=(job_titles[i] if i<len(job_titles) else q)
                if not any(k in role.lower() for k in KW): continue
                co=(job_cos[i] if i<len(job_cos) else "?")
                apply_url=(apply_urls[i].replace('\\/','/')
                           if i<len(apply_urls) else "")
                print(f"    {co[:20]:<20} {role[:32]}",end=" ",flush=True)
                ats=detect_ats(apply_url)
                if ats=="gh": res=fill_gh(ctx,co,role,apply_url,jid)
                elif ats=="lever": res=fill_lever(ctx,co,role,apply_url,jid)
                elif apply_url:
                    inner=pw_get_apply_url(ctx,apply_url)
                    ats2=detect_ats(inner)
                    if ats2=="gh": res=fill_gh(ctx,co,role,inner,jid)
                    elif ats2=="lever": res=fill_lever(ctx,co,role,inner,jid)
                    else:
                        email_try=f"careers@{re.sub(r'[^a-z]','',co.lower())}.com"
                        res="email_sent" if send_email(email_try,co,role) else f"ats_{ats2 or 'none'}"
                        save(co,role,inner or apply_url,jid,res,"ZipRecruiter","zr_email")
                else:
                    email_try=f"careers@{re.sub(r'[^a-z]','',co.lower())}.com"
                    res="email_sent" if send_email(email_try,co,role) else "no_apply"
                    save(co,role,"",jid,res,"ZipRecruiter","zr_email")
                if "ats_" not in res and "email" not in res and "no_" not in res:
                    save(co,role,apply_url,jid,res,"ZipRecruiter","zr_apply")
                icon="✅" if "success" in res or "submit" in res or "email_sent" in res else "📋"
                print(f"→ {icon} {res}")
                if "success" in res or "submit" in res or "email_sent" in res: ok+=1
                processed+=1; time.sleep(1)
        except Exception as e: print(f"    ERRO: {str(e)[:50]}")
    print(f"  ZipRecruiter: {processed} processadas, {ok} aplicadas")

def main():
    from playwright.sync_api import sync_playwright
    today=datetime.date.today().strftime("%d/%m/%Y")
    print(f"\n{'━'*58}")
    print(f"  🔧 PLATFORM FIXER v2 — {today}")
    print(f"  LinkedIn · Dice · RemoteOK · Indeed · Wellfound · ZipRecruiter")
    print(f"{'━'*58}")
    with sync_playwright() as pw:
        br=pw.chromium.launch(headless=True,args=[
            "--no-sandbox","--disable-dev-shm-usage","--disable-gpu",
            "--disable-blink-features=AutomationControlled"])
        ctx=br.new_context(
            user_agent=UA,viewport={"width":1366,"height":768},locale="en-US",
            extra_http_headers={"Accept-Language":"en-US,en;q=0.9"})
        ctx.add_init_script("Object.defineProperty(navigator,'webdriver',{get:()=>undefined})")
        fix_linkedin(ctx)
        fix_dice(ctx)
        fix_remoteok(ctx)
        fix_indeed(ctx)
        fix_wellfound(ctx)
        fix_ziprecruiter(ctx)
        br.close()
    print(f"\n{'━'*58}")
    print(f"  ✅ Platform Fixer v2 concluído")
    print(f"{'━'*58}\n")

if __name__ == "__main__":
    main()
