#!/usr/bin/env python3
"""
PLATFORM FIXER v3
Estratégia definitiva:
  - LinkedIn/Dice/Indeed/ROK → extrai nome da empresa → busca board GH/Lever diretamente
  - Se não tem board → email direto
  - RemoteOK → segue redirect real do botão Apply
  - ZipRecruiter → API correta
"""
import os, json, time, re, datetime, urllib.request, urllib.parse, smtplib
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
        "analytics engineer","reporting analyst","tableau","bi analyst"]
BOUNCE = {"hire@turing.com","work@andela.com","talent@toptal.com","hey@lemon.io",
          "work@gun.io","join@x-team.com","careers@toggl.com"}

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

def get(url,hdrs=None,timeout=10):
    h={"User-Agent":UA,"Accept":"text/html,application/json"}
    if hdrs: h.update(hdrs)
    try:
        with urllib.request.urlopen(urllib.request.Request(url,headers=h),timeout=timeout) as r:
            return r.read().decode("utf-8",errors="ignore")
    except: return ""

def cover_letter(co,role):
    if not AKEY:
        return(f"15yr Senior DA, PL-300, USD 9M+ savings. "
               f"Power BI+Tableau+SQL+Azure+BigQuery. Available for {role} at {co}.")
    try:
        p=json.dumps({"model":"claude-sonnet-4-20250514","max_tokens":220,
            "messages":[{"role":"user","content":
                f"2 tight paragraphs: {role} at {co}. Rafael: 15yr DA PL-300 USD 9M savings "
                f"70pct latency cut Power BI Tableau SQL Azure BigQuery Snowflake. "
                f"No greeting no sign-off. Only paragraphs."}]}).encode()
        rq=urllib.request.Request("https://api.anthropic.com/v1/messages",data=p,
            headers={"Content-Type":"application/json","x-api-key":AKEY,"anthropic-version":"2023-06-01"})
        with urllib.request.urlopen(rq,timeout=18) as r:
            return json.loads(r.read())["content"][0]["text"].strip()
    except: return f"15yr DA PL-300 USD 9M savings available for {role} at {co}."

def send_email(to,co,role):
    if not GMAIL or to in BOUNCE: return False
    eid=f"em_{re.sub(r'[^a-z0-9]','',co.lower())[:18]}"
    if seen(eid): return False
    try:
        msg=MIMEMultipart()
        msg["From"]=f"Rafael Rodrigues <{EM}>"; msg["To"]=to
        msg["Reply-To"]=PROF["email"]
        msg["Subject"]=f"Senior Data Analyst / Power BI — {co}"
        msg.attach(MIMEText(
            f"Dear {co} Hiring Team,\n\n{cover_letter(co,role)}\n\n"
            f"Best,\nRafael Rodrigues\n{PROF['phone']} | {PROF['email']}","plain"))
        if os.path.exists(CV):
            with open(CV,"rb") as f:
                att=MIMEApplication(f.read(),Name="Rafael_Rodrigues_CV.pdf")
                att["Content-Disposition"]='attachment; filename="Rafael_Rodrigues_CV.pdf"'
                msg.attach(att)
        with smtplib.SMTP_SSL("smtp.gmail.com",465) as s:
            s.login(EM,GMAIL); s.send_message(msg)
        save(co,role,f"mailto:{to}",eid,"sent","email","email_cv")
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
                    el.fill(f"Dear {co} Hiring Team,\n\n{cv_txt}\n\nBest,\nRafael\n{PROF['phone']}")
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
                        ("input[name='email']",PROF["email"]),("input[name='phone']",PROF["phone"]),
                        ("input[name*='linkedin']",PROF["linkedin"])]:
            try:
                el=pg.locator(sel).first
                if el.is_visible(timeout=400): el.fill(val); filled+=1
            except: pass
        try:
            el=pg.locator("textarea[name='comments'],textarea").first
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

# ── EMPRESA → BOARD GH/LEVER ───────────────────────────────────────────────────
def company_to_slug(name):
    """Converte nome da empresa em slugs possíveis para GH/Lever"""
    clean = re.sub(r'[^a-z0-9\s]','',name.lower())
    words = clean.split()
    slugs = []
    # Slug sem espaço
    slugs.append(''.join(words))
    # Slug com hífen
    slugs.append('-'.join(words))
    # Só primeira palavra
    slugs.append(words[0] if words else clean)
    # Sem palavras comuns
    stop = {'inc','llc','corp','ltd','co','the','group','global'}
    main = [w for w in words if w not in stop]
    if main:
        slugs.append(''.join(main))
        slugs.append('-'.join(main))
    return list(dict.fromkeys(slugs))[:6]  # dedup, max 6

def find_ats_board(company, role_kw=""):
    """Busca board GH ou Lever da empresa — retorna (ats_type, url, job_url)"""
    for slug in company_to_slug(company):
        # Greenhouse
        try:
            api=f"https://boards-api.greenhouse.io/v1/boards/{slug}/jobs"
            raw=get(api,{"User-Agent":UA},timeout=5)
            if raw and '"jobs"' in raw:
                jobs=json.loads(raw).get("jobs",[])
                for j in jobs:
                    if any(k in j.get("title","").lower() for k in KW):
                        return "gh", f"https://boards.greenhouse.io/{slug}", j.get("absolute_url","")
                if jobs:  # board existe mas sem vaga específica — retorna board mesmo assim
                    return "gh", f"https://boards.greenhouse.io/{slug}", jobs[0].get("absolute_url","")
        except: pass
        # Lever
        try:
            api2=f"https://api.lever.co/v0/postings/{slug}?mode=json"
            raw2=get(api2,{"User-Agent":UA},timeout=5)
            if raw2 and '"id"' in raw2:
                jobs2=json.loads(raw2) if raw2.startswith('[') else []
                for j in jobs2:
                    if any(k in j.get("text","").lower() for k in KW):
                        return "lever", f"https://jobs.lever.co/{slug}", j.get("hostedUrl","")
                if jobs2:
                    return "lever", f"https://jobs.lever.co/{slug}", jobs2[0].get("hostedUrl","")
        except: pass
    return None, None, None

def process_job(ctx, co, role, source_url, jid, platform, salary="", country="US"):
    """Pipeline unificado: empresa → board → apply"""
    print(f"    {co[:22]:<22} {role[:35]}", end=" ", flush=True)
    # 1. Tentar achar board GH/Lever diretamente
    ats, board_url, job_url = find_ats_board(co, role)
    if ats == "gh" and job_url:
        res = fill_gh(ctx, co, role, job_url, jid)
        icon = "✅" if "success" in res or "submit" in res else "📋"
        print(f"→ {icon} GH:{res}")
        save(co,role,job_url,jid,res,platform,f"{platform.lower()}_gh",salary,country)
        return res
    elif ats == "lever" and job_url:
        res = fill_lever(ctx, co, role, job_url, jid)
        icon = "✅" if "success" in res or "submit" in res else "📋"
        print(f"→ {icon} Lv:{res}")
        save(co,role,job_url,jid,res,platform,f"{platform.lower()}_lever",salary,country)
        return res
    # 2. Email direto
    domain = re.sub(r'[^a-z0-9]','',co.lower())[:20]
    for addr in [f"careers@{domain}.com", f"jobs@{domain}.com", f"talent@{domain}.com"]:
        if send_email(addr, co, role):
            print(f"→ 📧 email:{addr}")
            return "email_sent"
    print(f"→ ⚠️  no_board_no_email")
    save(co,role,source_url,jid,"no_board",platform,f"{platform.lower()}_miss",salary,country)
    return "no_board"

# ══════════════════════════════════════════════════════════════════════════════
# FONTES
# ══════════════════════════════════════════════════════════════════════════════

def run_linkedin(ctx):
    print("\n  ── LINKEDIN ──────────────────────────────────")
    ok=processed=0
    for q in ["power bi developer","senior data analyst","analytics engineer","bi analyst"]:
        try:
            raw=get(
                f"https://www.linkedin.com/jobs-guest/jobs/api/seeMoreJobPostings/search"
                f"?keywords={urllib.parse.quote(q)}&location=United+States&f_WT=2&start=0&count=20",
                {"Accept":"text/html"})
            ids=re.findall(r'data-entity-urn="[^"]*jobPosting:(\d+)"',raw)
            titles=re.findall(r'class="base-search-card__title"[^>]*>\s*([^<]+)\s*<',raw)
            companies=re.findall(r'class="base-search-card__subtitle"[^>]*>\s*([^<]+)\s*<',raw)
            for i,lid in enumerate(ids[:15]):
                jid=f"li2_{lid}"
                if seen(jid): continue
                co=(companies[i].strip() if i<len(companies) else "?")
                role=(titles[i].strip() if i<len(titles) else q)
                if not any(k in role.lower() for k in KW): continue
                res=process_job(ctx,co,role,f"https://linkedin.com/jobs/view/{lid}/",jid,"LinkedIn")
                if "success" in res or "submit" in res or "email" in res: ok+=1
                processed+=1; time.sleep(1.5)
        except: pass
    print(f"  LinkedIn: {processed} processadas, {ok} aplicadas")

def run_dice(ctx):
    print("\n  ── DICE ──────────────────────────────────────")
    ok=processed=0
    for q in ["power+bi+developer","senior+data+analyst","analytics+engineer","bi+analyst"]:
        try:
            raw=get(
                f"https://www.dice.com/jobs?q={q}&countryCode2=US&radius=30&radiusUnit=mi"
                f"&page=1&pageSize=20&filters.workplaceTypes=Remote&filters.employmentType=FULLTIME",
                {"Accept":"text/html"})
            guids=re.findall(r'"guid"\s*:\s*"([a-f0-9\-]{36})"',raw)
            titles=re.findall(r'"title"\s*:\s*"([^"]{5,80})"',raw)
            companies=re.findall(r'"companyName"\s*:\s*"([^"]{2,60})"',raw)
            for i,guid in enumerate(guids[:12]):
                jid=f"dice2_{guid[:16]}"
                if seen(jid): continue
                co=(companies[i] if i<len(companies) else "?")
                role=(titles[i] if i<len(titles) else q.replace("+"," "))
                if not any(k in role.lower() for k in KW): continue
                res=process_job(ctx,co,role,f"https://www.dice.com/job-detail/{guid}",jid,"Dice")
                if "success" in res or "submit" in res or "email" in res: ok+=1
                processed+=1; time.sleep(1.2)
        except: pass
    print(f"  Dice: {processed} processadas, {ok} aplicadas")

def run_remoteok(ctx):
    print("\n  ── REMOTE OK ─────────────────────────────────")
    ok=processed=0
    try:
        raw=get("https://remoteok.com/api",{"Accept":"application/json"})
        jobs=json.loads(raw)[1:]
        for j in jobs:
            if not isinstance(j,dict): continue
            if not any(k in j.get("position","").lower() for k in KW): continue
            jid=f"rok2_{j.get('id','')}"
            if seen(jid): continue
            co=j.get("company","?"); role=j.get("position","?")
            # Seguir URL do RemoteOK para pegar link real da empresa
            rok_url=j.get("apply_url","") or j.get("url","")
            real_url=""
            if rok_url:
                pg=ctx.new_page()
                try:
                    pg.goto(rok_url,timeout=15000); pg.wait_for_load_state("domcontentloaded",timeout=8000); time.sleep(1)
                    # Clicar no botão "Apply for this job"
                    for sel in ["a.button[href*='http']:not([href*='remoteok'])",
                                "a[data-action='apply']:not([href*='remoteok'])",
                                "a:has-text('Apply for this job')"]:
                        try:
                            el=pg.locator(sel).first
                            if el.is_visible(timeout=800):
                                href=el.get_attribute("href") or ""
                                if href and "remoteok" not in href and len(href)>10:
                                    real_url=href; break
                        except: pass
                    if not real_url:
                        html=pg.content()
                        m=re.search(r'href="(https?://(?!remoteok)[^\s"\'<>]{20,})"',html)
                        if m: real_url=m.group(1)
                    pg.close()
                except: pg.close()
            # Tentar board GH/Lever da empresa primeiro
            ats,board_url,job_url=find_ats_board(co,role)
            if ats=="gh" and job_url:
                print(f"    {co[:22]:<22} {role[:32]}", end=" ", flush=True)
                res=fill_gh(ctx,co,role,job_url,jid)
                save(co,role,job_url,jid,res,"RemoteOK","rok_gh")
            elif ats=="lever" and job_url:
                print(f"    {co[:22]:<22} {role[:32]}", end=" ", flush=True)
                res=fill_lever(ctx,co,role,job_url,jid)
                save(co,role,job_url,jid,res,"RemoteOK","rok_lever")
            elif real_url and any(k in real_url.lower() for k in ["greenhouse","lever.co","ashby"]):
                print(f"    {co[:22]:<22} {role[:32]}", end=" ", flush=True)
                from urllib.parse import urlparse
                dom=urlparse(real_url).netloc
                if "greenhouse" in dom: res=fill_gh(ctx,co,role,real_url,jid)
                else: res=fill_lever(ctx,co,role,real_url,jid)
                save(co,role,real_url,jid,res,"RemoteOK","rok_direct")
            else:
                print(f"    {co[:22]:<22} {role[:32]}", end=" ", flush=True)
                domain=re.sub(r'[^a-z0-9]','',co.lower())[:20]
                sent=False
                for addr in [f"jobs@{domain}.com",f"careers@{domain}.com"]:
                    if send_email(addr,co,role): sent=True; break
                res="email_sent" if sent else "no_board"
                save(co,role,rok_url,jid,res,"RemoteOK","rok_email")
            icon="✅" if "success" in res or "submit" in res or "email" in res else "📋"
            print(f"→ {icon} {res}")
            if "success" in res or "submit" in res or "email_sent" in res: ok+=1
            processed+=1; time.sleep(1)
    except Exception as e: print(f"    ERRO: {e}")
    print(f"  RemoteOK: {processed} processadas, {ok} aplicadas")

def run_indeed(ctx):
    print("\n  ── INDEED ────────────────────────────────────")
    ok=processed=0
    for q in ["power bi","data analyst","analytics engineer"]:
        for cc in ["us","ca","gb"]:
            try:
                xml=get(f"https://{cc}.indeed.com/rss?q={urllib.parse.quote(q)}"
                        f"&remotejob=032b3046-06a3-4876-8dfd-474eb5e7ed11&sort=date&limit=8")
                for item in re.findall(r'<item>(.*?)</item>',xml,re.DOTALL)[:5]:
                    title_m=re.search(r'<title><!\[CDATA\[([^\]]+)\]\]>|<title>([^<]+)<',item)
                    co_m=re.search(r'<source[^>]*>([^<]+)<',item)
                    jk_m=re.search(r'jk=([a-f0-9]+)',item)
                    if not jk_m: continue
                    jid=f"ind2_{cc}_{jk_m.group(1)}"
                    if seen(jid): continue
                    co=co_m.group(1).strip() if co_m else "?"
                    role=(title_m.group(1) or title_m.group(2) or "").strip() if title_m else q
                    if not any(k in role.lower() for k in KW): continue
                    res=process_job(ctx,co,role,
                        f"https://{cc}.indeed.com/viewjob?jk={jk_m.group(1)}",
                        jid,"Indeed",country=cc.upper())
                    if "success" in res or "submit" in res or "email" in res: ok+=1
                    processed+=1; time.sleep(1.2)
            except: pass
    print(f"  Indeed: {processed} processadas, {ok} aplicadas")

def run_wellfound(ctx):
    print("\n  ── WELLFOUND ─────────────────────────────────")
    ok=processed=0
    for q in ["data-analyst","power-bi","analytics-engineer"]:
        try:
            raw=get(f"https://wellfound.com/jobs?query={q}&remote=true")
            # Extrair empresa + título do HTML
            companies=re.findall(r'href="/company/([^"]+)"',raw)
            job_links=re.findall(r'href="(/jobs/[^"?]+)"',raw)
            for link in list(dict.fromkeys(job_links))[:12]:
                jid=f"wf2_{re.sub(r'[^a-z0-9]','',link)[:25]}"
                if seen(jid): continue
                full_url=f"https://wellfound.com{link}"
                # Extrair co e role do link
                parts=link.replace("/jobs/","").split("-at-",1)
                role_slug=parts[0].replace("-"," ").title() if parts else "Data Analyst"
                co_slug=parts[1].replace("-"," ").title() if len(parts)>1 else "Startup"
                if not any(k in role_slug.lower() for k in KW): continue
                res=process_job(ctx,co_slug,role_slug,full_url,jid,"Wellfound")
                if "success" in res or "submit" in res or "email" in res: ok+=1
                processed+=1; time.sleep(1)
        except Exception as e: print(f"    ERRO: {e}")
    print(f"  Wellfound: {processed} processadas, {ok} aplicadas")

def run_ziprecruiter(ctx):
    print("\n  ── ZIPRECRUITER ──────────────────────────────")
    ok=processed=0
    for q in ["power bi developer","data analyst","analytics engineer"]:
        try:
            raw=get(f"https://www.ziprecruiter.com/jobs-search?search={urllib.parse.quote(q)}"
                    f"&location=Remote&days=7&radius=25")
            # Extrair JSON embutido
            data_m=re.search(r'window\.__INITIAL_STATE__\s*=\s*(\{.*?\});',raw,re.S)
            if not data_m: continue
            data=json.loads(data_m.group(1))
            jobs=data.get("searchResults",{}).get("results",[]) or \
                 data.get("jobs",data.get("data",{}).get("jobs",[]))
            if not jobs:
                # Fallback: extrair do HTML diretamente
                titles=re.findall(r'"name"\s*:\s*"([^"]{5,80})"',raw)
                cos=re.findall(r'"hiringOrganization"\s*:\s*\{[^}]*"name"\s*:\s*"([^"]+)"',raw)
                apply_urls=re.findall(r'"url"\s*:\s*"(https?://[^"]+)"',raw)
                for i,role in enumerate(titles[:10]):
                    if not any(k in role.lower() for k in KW): continue
                    co=cos[i] if i<len(cos) else "?"
                    jid=f"zr2_{re.sub(r'[^a-z0-9]','',co.lower()[:12])}_{i}"
                    if seen(jid): continue
                    apply_url=apply_urls[i] if i<len(apply_urls) else ""
                    res=process_job(ctx,co,role,apply_url,jid,"ZipRecruiter")
                    if "success" in res or "submit" in res or "email" in res: ok+=1
                    processed+=1; time.sleep(1)
                continue
            for j in (jobs if isinstance(jobs,list) else [])[:10]:
                role=j.get("name",j.get("title",""))
                if not any(k in role.lower() for k in KW): continue
                co=j.get("hiring_company",{}).get("name",j.get("company","?"))
                jid=f"zr2_{j.get('id','x')[:16]}"
                if seen(jid): continue
                apply_url=j.get("apply_url",j.get("job_url",""))
                res=process_job(ctx,co,role,apply_url,jid,"ZipRecruiter")
                if "success" in res or "submit" in res or "email" in res: ok+=1
                processed+=1; time.sleep(1)
        except Exception as e: print(f"    ERRO: {str(e)[:60]}")
    print(f"  ZipRecruiter: {processed} processadas, {ok} aplicadas")

def run_jobright(ctx):
    print("\n  ── JOBRIGHT ──────────────────────────────────")
    ok=processed=0
    # Jobright agrega vagas — extrair empresa + ir no board GH/Lever diretamente
    for q in ["power bi","data analyst","analytics engineer"]:
        try:
            raw=get(f"https://jobright.ai/jobs?keyword={urllib.parse.quote(q)}&type=Remote")
            cos=re.findall(r'"companyName"\s*:\s*"([^"]+)"',raw)
            roles=re.findall(r'"title"\s*:\s*"([^"]+)"',raw)
            ids=re.findall(r'"id"\s*:\s*"([^"]{8,})"',raw)
            for i,co in enumerate(cos[:12]):
                role=roles[i] if i<len(roles) else q
                if not any(k in role.lower() for k in KW): continue
                jid=f"jr2_{ids[i][:16] if i<len(ids) else str(i)}"
                if seen(jid): continue
                res=process_job(ctx,co,role,"https://jobright.ai",jid,"Jobright.ai")
                if "success" in res or "submit" in res or "email" in res: ok+=1
                processed+=1; time.sleep(1)
        except Exception as e: print(f"    ERRO: {str(e)[:60]}")
    print(f"  Jobright: {processed} processadas, {ok} aplicadas")

def main():
    from playwright.sync_api import sync_playwright
    today=datetime.date.today().strftime("%d/%m/%Y")
    print(f"\n{'━'*58}")
    print(f"  🔧 PLATFORM FIXER v3 — {today}")
    print(f"  Estratégia: empresa → board GH/Lever → apply direto")
    print(f"{'━'*58}")
    with sync_playwright() as pw:
        br=pw.chromium.launch(headless=True,args=[
            "--no-sandbox","--disable-dev-shm-usage","--disable-gpu",
            "--disable-blink-features=AutomationControlled"])
        ctx=br.new_context(user_agent=UA,viewport={"width":1366,"height":768},locale="en-US",
            extra_http_headers={"Accept-Language":"en-US,en;q=0.9"})
        ctx.add_init_script("Object.defineProperty(navigator,'webdriver',{get:()=>undefined})")
        run_linkedin(ctx)
        run_dice(ctx)
        run_remoteok(ctx)
        run_indeed(ctx)
        run_wellfound(ctx)
        run_ziprecruiter(ctx)
        run_jobright(ctx)
        br.close()
    print(f"\n{'━'*58}")
    print("  ✅ Platform Fixer v3 concluído")
    print(f"{'━'*58}\n")

if __name__ == "__main__":
    main()
