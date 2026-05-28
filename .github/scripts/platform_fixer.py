#!/usr/bin/env python3
"""
PLATFORM FIXER v1 — corrige Dice/RemoteOK/Jobright/Indeed/LinkedIn/Wellfound/ZipRecruiter
Estratégia: extrair apply_url DIRETO das APIs (sem clicar em React SPAs)
"""
import os, sys, json, time, re, datetime, urllib.request, urllib.parse, smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.application import MIMEApplication

SUPA  = os.environ.get("SUPABASE_URL","https://tpjvalzwkqwttvmszvie.supabase.co")
KEY   = os.environ.get("SUPABASE_ANON_KEY","")
GMAIL = os.environ.get("GMAIL_APP_PASSWORD","")
AKEY  = os.environ.get("ANTHROPIC_API_KEY","")
EMAIL = os.environ.get("DICE_EMAIL","tafita81@gmail.com")
PWD   = os.environ.get("DICE_PASSWORD","Daniela1982@")

CV    = ".github/assets/rafael_cv.pdf"
PROF  = {
    "first":"Rafael","last":"Rodrigues",
    "email":"Rafa_roberto2004@yahoo.com.br",
    "phone":"+5522992418257",
    "linkedin":"https://linkedin.com/in/rafael-r-a3946a15",
}
UA = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 Chrome/124.0"
KWORDS = ["data analyst","power bi","business intelligence","bi developer",
          "analytics engineer","reporting analyst","tableau","bi analyst"]

def sb(m,p,d=None):
    h={"apikey":KEY,"Authorization":f"Bearer {KEY}","Content-Type":"application/json"}
    rq=urllib.request.Request(f"{SUPA}/rest/v1/{p}",
       data=json.dumps(d).encode() if d else None,method=m,headers=h)
    try:
        with urllib.request.urlopen(rq,timeout=8) as r:
            return json.loads(r.read()) if m=="GET" else r.status
    except Exception as e:
        return 409 if "409" in str(e) else None

def seen(jid):
    r=sb("GET",f"job_applications?job_id=eq.{urllib.parse.quote(str(jid))}&select=id&limit=1")
    return isinstance(r,list) and len(r)>0

def save(co,role,url,jid,status,platform,method,salary="",country="US"):
    sb("POST","job_applications",{
        "company":co,"role":role,"url":url,"job_id":str(jid),
        "application_method":method,"status":status,"platform":platform,
        "applied_at":datetime.datetime.now(datetime.timezone.utc).isoformat(),
        "email":PROF["email"],"salary":salary,"country":country})

def get(url, headers=None, timeout=10):
    h={"User-Agent":UA,"Accept":"application/json, text/html"}
    if headers: h.update(headers)
    try:
        rq=urllib.request.Request(url,headers=h)
        with urllib.request.urlopen(rq,timeout=timeout) as r:
            ct = r.headers.get("Content-Type","")
            raw = r.read()
            return raw.decode("utf-8",errors="ignore")
    except: return ""

def extract_apply_url(html_or_json):
    """Extrai URL de apply de qualquer conteúdo"""
    patterns = [
        r'(https://boards\.greenhouse\.io/[^\s"\'<>]+)',
        r'(https://job-boards\.greenhouse\.io/[^\s"\'<>]+)',
        r'(https://jobs\.lever\.co/[^\s"\'<>]+)',
        r'(https://jobs\.ashbyhq\.com/[^\s"\'<>]+)',
        r'(https://[^\s"\'<>]*workday[^\s"\'<>]+)',
        r'(https://[^\s"\'<>]*myworkdayjobs[^\s"\'<>]+)',
        r'"applyUrl"\s*:\s*"([^"]+)"',
        r'"apply_url"\s*:\s*"([^"]+)"',
        r'"applicationUrl"\s*:\s*"([^"]+)"',
        r'href="(https://[^"]*(?:greenhouse|lever|ashby|workday|icims|jobvite|smartrecruit)[^"]*)"',
    ]
    for pat in patterns:
        m = re.search(pat, html_or_json, re.I)
        if m:
            url = m.group(1).strip().rstrip('"\'')
            if len(url) > 10: return url
    return ""

def detect_ats(url):
    if not url: return None
    for k,v in [("greenhouse","gh"),("lever.co","lever"),("ashbyhq","ashby"),
                ("workday","workday"),("myworkdayjobs","workday"),("icims","icims"),
                ("smartrecruit","smart"),("jobvite","jobvite"),("taleo","taleo")]:
        if k in url.lower(): return v
    return None

def cover(co, role):
    if not AKEY:
        return (f"Senior Data Analyst with 15 years of enterprise BI, PL-300 certified. "
                f"USD 9M+ savings, 70% latency reduction. Power BI, Tableau, SQL, Azure, BigQuery. "
                f"Available immediately for {role} at {co}.")
    try:
        p=json.dumps({"model":"claude-sonnet-4-20250514","max_tokens":280,
            "messages":[{"role":"user","content":
                f"2 tight paragraphs for cover letter: {role} at {co}. "
                f"Rafael: 15yr Senior DA, PL-300, Tableau, USD 9M+ savings, 70% latency cut, "
                f"200+ users, Power BI+SQL+Python+Azure+BigQuery+Snowflake. "
                f"No greeting/sign-off. Output ONLY paragraphs."}]}).encode()
        rq=urllib.request.Request("https://api.anthropic.com/v1/messages",data=p,
            headers={"Content-Type":"application/json","x-api-key":AKEY,"anthropic-version":"2023-06-01"})
        with urllib.request.urlopen(rq,timeout=18) as r:
            return json.loads(r.read())["content"][0]["text"].strip()
    except:
        return f"15yr Senior DA, PL-300, USD 9M savings. Power BI+Tableau+SQL+Azure. Available for {role} at {co}."

BOUNCE = {"hire@turing.com","work@andela.com","talent@toptal.com","hey@lemon.io","work@gun.io"}

def send_email(to, co, role):
    if not GMAIL or to in BOUNCE or seen(f"email_{co.lower()[:20]}"): return False
    try:
        msg=MIMEMultipart()
        msg["From"]=f"Rafael Rodrigues <{EMAIL}>"
        msg["To"]=to
        msg["Reply-To"]=PROF["email"]
        msg["Subject"]=f"Senior Data Analyst / Power BI — {co}"
        body=f"Dear {co} Hiring Team,\n\n{cover(co,role)}\n\nBest,\nRafael Rodrigues\n{PROF['phone']} | {PROF['email']}"
        msg.attach(MIMEText(body,"plain"))
        if os.path.exists(CV):
            with open(CV,"rb") as f:
                att=MIMEApplication(f.read(),Name="Rafael_Rodrigues_CV.pdf")
                att["Content-Disposition"]='attachment; filename="Rafael_Rodrigues_CV.pdf"'
                msg.attach(att)
        with smtplib.SMTP_SSL("smtp.gmail.com",465) as s:
            s.login(EMAIL,GMAIL); s.send_message(msg)
        save(co,role,f"mailto:{to}",f"email_{co.lower()[:20]}","sent","email","email_cv")
        return True
    except: return False

# ── Playwright form fillers ────────────────────────────────────────────────────
def fill_gh(ctx, co, role, url, jid):
    pg=ctx.new_page()
    try:
        pg.goto(url,timeout=18000); pg.wait_for_load_state("domcontentloaded",timeout=8000); time.sleep(1.5)
        if "greenhouse" not in pg.url: pg.close(); return "no_gh"
        cv_txt=cover(co,role); filled=0
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

def fill_lever(ctx, co, role, url, jid):
    pg=ctx.new_page()
    try:
        pg.goto(url,timeout=18000); pg.wait_for_load_state("domcontentloaded",timeout=8000); time.sleep(1.5)
        if "lever.co" not in pg.url: pg.close(); return "no_lever"
        cv_txt=cover(co,role); filled=0
        for sel,val in [("input[name='name']",f"{PROF['first']} {PROF['last']}"),
                        ("input[name='email']",PROF["email"]),("input[name='phone']",PROF["phone"]),
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

def apply_job(ctx, co, role, apply_url, jid, platform, salary="", country="US"):
    """Roteador central: detecta ATS e aplica"""
    ats = detect_ats(apply_url)
    if ats == "gh":
        res = fill_gh(ctx, co, role, apply_url, jid)
    elif ats == "lever":
        res = fill_lever(ctx, co, role, apply_url, jid)
    elif ats:
        res = f"ats_{ats}_pending"
    else:
        res = "no_ats"
    save(co, role, apply_url, jid, res, platform, f"{platform.lower()}_apply", salary, country)
    return res

# ══════════════════════════════════════════════════════════════════════════════
# FIXERS POR PLATAFORMA
# ══════════════════════════════════════════════════════════════════════════════

def fix_dice(ctx):
    """Dice: extrai apply_url via API de detalhes (não clica na SPA)"""
    print("\n  ── DICE ──────────────────────────────────────")
    ok=0; processed=0

    # Buscar vagas via MCP-style API (sem filtro easyApply que dá 403)
    for q in ["power+bi","data+analyst","analytics+engineer","business+intelligence"]:
        try:
            url=(f"https://job-search-api.svc.dhigroupinc.com/v1/dice/jobs/search"
                 f"?q={q}&countryCode2=US&radius=30&radiusUnit=mi&page=1&pageSize=15"
                 f"&filters.workplaceTypes=Remote&filters.employmentType=FULLTIME"
                 f"&fields=id,guid,title,companyName,salary,easyApply,detailsPageUrl,applyUrl")
            raw = get(url, {"x-api-key":"1YAt0R9wBg4WfsF9VB2778F4BkEFeDe0"})
            if not raw: continue
            data = json.loads(raw)
            for j in data.get("data",[]):
                if not any(k in j.get("title","").lower() for k in KWORDS): continue
                guid = j.get("guid","")
                jid  = f"dice_{guid}"
                if seen(jid): continue

                co   = j.get("companyName","?")
                role = j.get("title","?")
                sal  = j.get("salary","")
                easy = j.get("easyApply",False)

                # Buscar apply_url via detalhe da vaga
                detail_html = get(f"https://www.dice.com/job-detail/{guid}")
                apply_url   = j.get("applyUrl","") or extract_apply_url(detail_html)

                print(f"    {'EA' if easy else '--'} {co[:18]:<18} {role[:32]}", end=" ", flush=True)

                if apply_url and detect_ats(apply_url):
                    res = apply_job(ctx, co, role, apply_url, jid, "Dice", sal)
                    icon = "✅" if "success" in res or "submit" in res else "📋"
                    print(f"→ {icon} {res}")
                    if "success" in res or "submit" in res: ok+=1
                elif easy:
                    # Easy Apply sem URL → email direto para a empresa
                    email_guess = f"careers@{re.sub(r'[^a-z]','',co.lower())}.com"
                    sent = send_email(email_guess, co, role)
                    print(f"→ {'📧 email' if sent else '⚠️ needs_token'}")
                    save(co,role,j.get("detailsPageUrl",""),jid,
                         "email_sent" if sent else "needs_token","Dice","dice_email",sal)
                    if sent: ok+=1
                else:
                    print(f"→ ⚠️ no_apply_url")
                    save(co,role,j.get("detailsPageUrl",""),jid,"no_apply_url","Dice","dice_auto",sal)

                processed+=1; time.sleep(0.8)
        except Exception as e:
            print(f"    ERRO busca: {str(e)[:40]}")
    print(f"  Dice: {processed} processadas, {ok} aplicadas")

def fix_remoteok(ctx):
    """RemoteOK: API retorna apply_url direta"""
    print("\n  ── REMOTE OK ─────────────────────────────────")
    ok=0; processed=0
    raw = get("https://remoteok.com/api")
    if not raw: return
    try: jobs = json.loads(raw)[1:]
    except: return
    for j in jobs:
        if not isinstance(j,dict): continue
        title = j.get("position","").lower()
        if not any(k in title for k in KWORDS): continue
        jid = f"rok_{j.get('id','')}"
        if seen(jid): continue
        co   = j.get("company","?")
        role = j.get("position","?")
        apply_url = j.get("apply_url","") or j.get("url","")
        print(f"    {co[:20]:<20} {role[:35]}", end=" ", flush=True)
        ats = detect_ats(apply_url)
        if ats == "gh":
            res = fill_gh(ctx, co, role, apply_url, jid)
        elif ats == "lever":
            res = fill_lever(ctx, co, role, apply_url, jid)
        elif apply_url and apply_url.startswith("mailto:"):
            to = apply_url.replace("mailto:","").split("?")[0]
            res = "email_sent" if send_email(to, co, role) else "email_failed"
        else:
            # Tentar extrair do HTML da vaga
            html = get(apply_url) if apply_url else ""
            inner_url = extract_apply_url(html)
            if inner_url and detect_ats(inner_url):
                res = apply_job(ctx, co, role, inner_url, jid, "RemoteOK")
            else:
                email_try = f"jobs@{re.sub(r'[^a-z]','',co.lower())}.com"
                res = "email_sent" if send_email(email_try, co, role) else "no_apply"
        save(co, role, apply_url, jid, res, "RemoteOK", "rok_apply")
        icon = "✅" if "success" in res or "submit" in res or "email" in res else "⚠️"
        print(f"→ {icon} {res}")
        if "success" in res or "submit" in res or "email_sent" in res: ok+=1
        processed+=1; time.sleep(1)
    print(f"  RemoteOK: {processed} processadas, {ok} aplicadas")

def fix_jobright(ctx):
    """Jobright: segue redirect para ATS real"""
    print("\n  ── JOBRIGHT.AI ───────────────────────────────")
    ok=0; processed=0
    for q in ["power+bi+developer","senior+data+analyst","analytics+engineer"]:
        try:
            raw = get(f"https://jobright.ai/api/jobs?query={q}&remote=true&limit=15",
                     {"Accept":"application/json"})
            if not raw: continue
            data = json.loads(raw)
            jobs = data if isinstance(data,list) else data.get("jobs",data.get("data",[]))
            for j in jobs[:10]:
                title = (j.get("title") or j.get("position","")).lower()
                if not any(k in title for k in KWORDS): continue
                jid = f"jr_{j.get('id',j.get('_id',''))}"
                if seen(jid): continue
                co   = j.get("company",j.get("companyName","?"))
                role = j.get("title",j.get("position","?"))
                url  = j.get("applyUrl",j.get("apply_url",j.get("url","")))
                print(f"    {co[:20]:<20} {role[:35]}", end=" ", flush=True)
                # Seguir redirect para encontrar ATS
                html = get(url) if url else ""
                apply_url = extract_apply_url(html) or url
                ats = detect_ats(apply_url)
                if ats == "gh":
                    res = fill_gh(ctx, co, role, apply_url, jid)
                elif ats == "lever":
                    res = fill_lever(ctx, co, role, apply_url, jid)
                else:
                    email_try = f"careers@{re.sub(r'[^a-z]','',co.lower())}.com"
                    res = "email_sent" if send_email(email_try, co, role) else "no_ats"
                save(co, role, apply_url or url, jid, res, "Jobright.ai", "jobright_apply")
                icon = "✅" if "success" in res or "submit" in res or "email" in res else "⚠️"
                print(f"→ {icon} {res}")
                if "success" in res or "submit" in res or "email_sent" in res: ok+=1
                processed+=1; time.sleep(1)
        except: pass
    print(f"  Jobright: {processed} processadas, {ok} aplicadas")

def fix_indeed(ctx):
    """Indeed: extrai apply URL do HTML da vaga"""
    print("\n  ── INDEED ────────────────────────────────────")
    ok=0; processed=0
    for q in ["power bi","data analyst","analytics engineer"]:
        for cc in ["us","ca","gb","de","au"]:
            try:
                url=(f"https://{cc}.indeed.com/rss?q={urllib.parse.quote(q)}"
                     f"&remotejob=032b3046-06a3-4876-8dfd-474eb5e7ed11&sort=date&limit=8")
                xml = get(url)
                items = re.findall(r'<item>(.*?)</item>', xml, re.DOTALL)
                for item in items[:6]:
                    title_m   = re.search(r'<title>([^<]+)<',item)
                    company_m = re.search(r'<source[^>]*>([^<]+)<',item)
                    link_m    = re.search(r'<link>([^<]+)<',item)
                    jk_m      = re.search(r'jk=([a-f0-9]+)',item)
                    if not (link_m and jk_m): continue
                    jid  = f"indeed_{cc}_{jk_m.group(1)}"
                    if seen(jid): continue
                    co   = company_m.group(1) if company_m else "?"
                    role = title_m.group(1) if title_m else q
                    job_url = link_m.group(1)
                    print(f"    [{cc.upper()}] {co[:18]:<18} {role[:30]}", end=" ", flush=True)
                    # Extrair apply URL da página Indeed
                    html = get(job_url)
                    apply_url = extract_apply_url(html)
                    # Indeed também embute o URL externo em data-jk ou redirect
                    if not apply_url:
                        ext = re.search(r'"externalApplyLink"\s*:\s*"([^"]+)"', html)
                        if ext: apply_url = ext.group(1).replace('\\/','/')
                    ats = detect_ats(apply_url) if apply_url else None
                    if ats == "gh":
                        res = fill_gh(ctx, co, role, apply_url, jid)
                    elif ats == "lever":
                        res = fill_lever(ctx, co, role, apply_url, jid)
                    elif apply_url:
                        res = f"ats_{ats or 'other'}"
                        save(co, role, apply_url, jid, res, "Indeed", "indeed_ats", country=cc.upper())
                        print(f"→ 📋 {res}"); processed+=1; time.sleep(0.6); continue
                    else:
                        res = "no_apply_url"
                    save(co, role, apply_url or job_url, jid, res, "Indeed", "indeed_apply", country=cc.upper())
                    icon = "✅" if "success" in res or "submit" in res else "⚠️"
                    print(f"→ {icon} {res}")
                    if "success" in res or "submit" in res: ok+=1
                    processed+=1; time.sleep(0.8)
            except: pass
    print(f"  Indeed: {processed} processadas, {ok} aplicadas")

def fix_linkedin(ctx):
    """LinkedIn: guest API + extrai apply URL da página pública"""
    print("\n  ── LINKEDIN ──────────────────────────────────")
    ok=0; processed=0
    for q in ["power bi developer","senior data analyst","analytics engineer","bi analyst"]:
        try:
            raw = get(
                f"https://www.linkedin.com/jobs-guest/jobs/api/seeMoreJobPostings/search"
                f"?keywords={urllib.parse.quote(q)}&location=United+States"
                f"&f_WT=2&start=0&count=15",
                {"Accept":"text/html","Referer":"https://www.linkedin.com/jobs/"})
            ids      = re.findall(r'data-entity-urn="[^"]*jobPosting:(\d+)"', raw)
            titles   = re.findall(r'class="base-search-card__title"[^>]*>([^<]+)<', raw)
            companies= re.findall(r'class="base-search-card__subtitle"[^>]*>([^<]+)<', raw)
            for i,jid_raw in enumerate(ids[:12]):
                jid = f"li_{jid_raw}"
                if seen(jid): continue
                co   = companies[i].strip() if i<len(companies) else "?"
                role = titles[i].strip() if i<len(titles) else q
                if not any(k in role.lower() for k in KWORDS): continue
                print(f"    {co[:20]:<20} {role[:35]}", end=" ", flush=True)
                # Pegar apply URL da página pública do job
                job_html = get(f"https://www.linkedin.com/jobs/view/{jid_raw}/")
                apply_url = extract_apply_url(job_html)
                # Também verificar campo applyMethod
                am = re.search(r'"applyMethod"\s*:\s*\{[^}]*"companyApplyUrl"\s*:\s*"([^"]+)"', job_html)
                if am: apply_url = apply_url or am.group(1).replace('\\/','/')
                ats = detect_ats(apply_url) if apply_url else None
                if ats == "gh":
                    res = fill_gh(ctx, co, role, apply_url, jid)
                elif ats == "lever":
                    res = fill_lever(ctx, co, role, apply_url, jid)
                elif apply_url:
                    res = f"ats_{ats or 'other'}"
                else:
                    email_try = f"jobs@{re.sub(r'[^a-z]','',co.lower())}.com"
                    res = "email_sent" if send_email(email_try, co, role) else "no_apply"
                save(co, role, apply_url or f"https://linkedin.com/jobs/view/{jid_raw}/",
                     jid, res, "LinkedIn", "li_apply")
                icon = "✅" if "success" in res or "submit" in res or "email" in res else "📋"
                print(f"→ {icon} {res}")
                if "success" in res or "submit" in res or "email_sent" in res: ok+=1
                processed+=1; time.sleep(1)
        except: pass
    print(f"  LinkedIn: {processed} processadas, {ok} aplicadas")

def fix_wellfound(ctx):
    """Wellfound: scraper de vagas públicas + apply via ATS"""
    print("\n  ── WELLFOUND ─────────────────────────────────")
    ok=0; processed=0
    try:
        raw = get("https://wellfound.com/jobs?query=data+analyst&remote=true",
                 {"Accept":"text/html"})
        # Extrair job links do HTML
        job_links = re.findall(r'href="(/jobs/[^\s"?]+)"', raw)
        seen_links = set()
        for link in job_links[:15]:
            if link in seen_links: continue
            seen_links.add(link)
            jid = f"wf_{link.replace('/','_')}"
            if seen(jid): continue
            full_url = f"https://wellfound.com{link}"
            job_html = get(full_url)
            # Extrair título e empresa
            title_m  = re.search(r'<title>([^|<]+)',job_html)
            co_m     = re.search(r'"company"\s*:\s*\{"name"\s*:\s*"([^"]+)"',job_html)
            co   = co_m.group(1) if co_m else "Wellfound Co"
            role = title_m.group(1).strip() if title_m else "Data Analyst"
            if not any(k in role.lower() for k in KWORDS): continue
            print(f"    {co[:20]:<20} {role[:35]}", end=" ", flush=True)
            apply_url = extract_apply_url(job_html)
            ats = detect_ats(apply_url) if apply_url else None
            if ats == "gh":
                res = fill_gh(ctx, co, role, apply_url, jid)
            elif ats == "lever":
                res = fill_lever(ctx, co, role, apply_url, jid)
            else:
                email_try = f"jobs@{re.sub(r'[^a-z]','',co.lower())}.com"
                res = "email_sent" if send_email(email_try, co, role) else "no_ats"
            save(co, role, apply_url or full_url, jid, res, "Wellfound", "wf_apply")
            icon = "✅" if "success" in res or "email" in res else "📋"
            print(f"→ {icon} {res}")
            if "success" in res or "email_sent" in res: ok+=1
            processed+=1; time.sleep(1)
    except Exception as e:
        print(f"    ERRO: {str(e)[:50]}")
    print(f"  Wellfound: {processed} processadas, {ok} aplicadas")

def fix_ziprecruiter(ctx):
    """ZipRecruiter: busca via API guest + extrai apply URL"""
    print("\n  ── ZIPRECRUITER ──────────────────────────────")
    ok=0; processed=0
    for q in ["power bi developer","senior data analyst","business intelligence analyst"]:
        try:
            raw = get(
                f"https://api.ziprecruiter.com/jobs/v1?search={urllib.parse.quote(q)}"
                f"&location=Remote&radius_miles=25&days_ago=7&jobs_per_page=15"
                f"&page=1&api_key=bc5a6a04-8a27-478e-acda-2fb7c96ab0bd")
            if not raw: continue
            data = json.loads(raw)
            for j in data.get("jobs",[]):
                title = j.get("name","").lower()
                if not any(k in title for k in KWORDS): continue
                jid = f"zr_{j.get('id','')}"
                if seen(jid): continue
                co   = j.get("hiring_company",{}).get("name","?")
                role = j.get("name","?")
                apply_url = j.get("apply_url","") or j.get("job_url","")
                print(f"    {co[:20]:<20} {role[:35]}", end=" ", flush=True)
                ats = detect_ats(apply_url)
                if ats == "gh":
                    res = fill_gh(ctx, co, role, apply_url, jid)
                elif ats == "lever":
                    res = fill_lever(ctx, co, role, apply_url, jid)
                else:
                    html = get(apply_url) if apply_url else ""
                    inner = extract_apply_url(html)
                    if inner and detect_ats(inner):
                        res = apply_job(ctx, co, role, inner, jid, "ZipRecruiter")
                    else:
                        email_try = f"careers@{re.sub(r'[^a-z]','',co.lower())}.com"
                        res = "email_sent" if send_email(email_try, co, role) else "no_ats"
                save(co, role, apply_url, jid, res, "ZipRecruiter", "zr_apply")
                icon = "✅" if "success" in res or "email" in res else "📋"
                print(f"→ {icon} {res}")
                if "success" in res or "email_sent" in res: ok+=1
                processed+=1; time.sleep(0.8)
        except: pass
    print(f"  ZipRecruiter: {processed} processadas, {ok} aplicadas")

# ── MAIN ───────────────────────────────────────────────────────────────────────
def main():
    from playwright.sync_api import sync_playwright
    today = datetime.date.today().strftime("%d/%m/%Y")
    print(f"\n{'━'*58}")
    print(f"  🔧 PLATFORM FIXER v1 — {today}")
    print(f"  Dice · RemoteOK · Jobright · Indeed · LinkedIn · Wellfound · ZipRecruiter")
    print(f"{'━'*58}")
    with sync_playwright() as pw:
        br = pw.chromium.launch(headless=True, args=[
            "--no-sandbox","--disable-dev-shm-usage","--disable-gpu",
            "--disable-blink-features=AutomationControlled"])
        ctx = br.new_context(
            user_agent=UA, viewport={"width":1366,"height":768}, locale="en-US",
            extra_http_headers={"Accept-Language":"en-US,en;q=0.9"})
        ctx.add_init_script("Object.defineProperty(navigator,'webdriver',{get:()=>undefined})")
        fix_dice(ctx)
        fix_remoteok(ctx)
        fix_jobright(ctx)
        fix_indeed(ctx)
        fix_linkedin(ctx)
        fix_wellfound(ctx)
        fix_ziprecruiter(ctx)
        br.close()
    print(f"\n{'━'*58}")
    print(f"  ✅ Platform Fixer concluído")
    print(f"{'━'*58}\n")

if __name__ == "__main__":
    main()
