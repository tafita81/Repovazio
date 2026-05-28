#!/usr/bin/env python3
"""
UNIVERSAL APPLY v1
Resolve de uma vez todos os sites pendentes:

1. WORKDAY    — form multi-step via Playwright (cria conta se necessário)
2. EMAIL FALLBACK — para tudo que não tem ATS suportado
3. RE-PROCESS — reprocessa registros stuck (no_board/ats_workday/clicked/etc)
4. LINKEDIN   — com regex correto + Workday support
5. DICE       — via company email direto (Innovative IT, Intersect, HMG etc)
6. REMOTEOK   — segue redirect real via Playwright
7. INDEED     — extrai apply URL via Playwright renderizado
8. JOBRIGHT   — API correta v2
"""
import os, json, time, re, datetime, urllib.request, urllib.parse, smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.application import MIMEApplication

SUPA  = os.environ.get("SUPABASE_URL", "https://tpjvalzwkqwttvmszvie.supabase.co")
KEY   = os.environ.get("SUPABASE_ANON_KEY", "")
GMAIL = os.environ.get("GMAIL_APP_PASSWORD", "")
AKEY  = os.environ.get("ANTHROPIC_API_KEY", "")
EM    = os.environ.get("DICE_EMAIL", "tafita81@gmail.com")
PW    = os.environ.get("DICE_PASSWORD", "Daniela1982@")
CV    = ".github/assets/rafael_cv.pdf"
UA    = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 Chrome/124.0"
PROF  = {
    "first": "Rafael", "last": "Rodrigues",
    "email": "Rafa_roberto2004@yahoo.com.br",
    "phone": "+5522992418257",
    "linkedin": "https://linkedin.com/in/rafael-r-a3946a15",
}
KW    = ["data analyst","power bi","business intelligence","bi developer",
         "analytics engineer","reporting analyst","tableau","bi analyst"]
BOUNCE = {"hire@turing.com","work@andela.com","talent@toptal.com","hey@lemon.io",
          "work@gun.io","join@x-team.com","careers@toggl.com"}

# Empresas com email já conhecido
KNOWN_EMAILS = {
    "innovative it technologies": "hr@iiti.com",
    "intersect group": "jobs@intersectgroup.com",
    "central point partners": "recruiting@centralpointpartners.com",
    "hmg america": "info@hmgamerica.com",
    "drunix solution": "hr@drunixsolution.com",
    "purple drive technologies": "hr@purpledrive.com",
}

def sb(m, p, d=None):
    h = {"apikey": KEY, "Authorization": "Bearer " + KEY, "Content-Type": "application/json"}
    rq = urllib.request.Request(SUPA + "/rest/v1/" + p,
         data=json.dumps(d).encode() if d else None, method=m, headers=h)
    try:
        with urllib.request.urlopen(rq, timeout=8) as r:
            return json.loads(r.read()) if m == "GET" else r.status
    except Exception as e:
        return 409 if "409" in str(e) else None

def seen(jid):
    r = sb("GET", "job_applications?job_id=eq." + urllib.parse.quote(str(jid)) + "&select=id&limit=1")
    return isinstance(r, list) and len(r) > 0

def save(co, role, url, jid, status, platform, method, salary="", country="US"):
    sb("POST", "job_applications", {
        "company": co, "role": role, "url": url, "job_id": str(jid),
        "application_method": method, "status": status, "platform": platform,
        "applied_at": datetime.datetime.now(datetime.timezone.utc).isoformat(),
        "email": PROF["email"], "salary": salary, "country": country
    })

def update_status(jid, new_status):
    sb("PATCH", "job_applications?job_id=eq." + urllib.parse.quote(str(jid)),
       {"status": new_status})

def cover(co, role):
    if not AKEY:
        return ("15yr Senior DA, PL-300, USD 9M+ savings. "
                "Power BI+Tableau+SQL+Azure+BigQuery. Available for " + role + " at " + co + ".")
    try:
        p = json.dumps({"model": "claude-sonnet-4-20250514", "max_tokens": 220,
            "messages": [{"role": "user", "content":
                "2 tight paragraphs cover letter for " + role + " at " + co + ". "
                "Rafael 15yr DA PL-300 USD 9M savings 70pct latency Power BI Tableau SQL Azure BigQuery Snowflake. "
                "No greeting no sign-off. Only 2 paragraphs."}]}).encode()
        rq = urllib.request.Request("https://api.anthropic.com/v1/messages", data=p,
            headers={"Content-Type": "application/json", "x-api-key": AKEY, "anthropic-version": "2023-06-01"})
        with urllib.request.urlopen(rq, timeout=18) as r:
            return json.loads(r.read())["content"][0]["text"].strip()
    except:
        return "15yr DA PL-300 USD 9M savings available for " + role + " at " + co + "."

def detect_ats(url):
    if not url: return None
    u = url.lower()
    for k, v in [("greenhouse", "gh"), ("lever.co", "lever"), ("ashbyhq", "ashby"),
                 ("workday", "workday"), ("myworkdayjobs", "workday"),
                 ("icims", "icims"), ("smartrecruit", "smart"), ("jobvite", "jobvite"),
                 ("taleo", "taleo"), ("successfactors", "sap"), ("bamboohr", "bamboo"),
                 ("rippling", "rippling"), ("greenhouse", "gh")]:
        if k in u: return v
    return None

def send_email(to, co, role, jid=None):
    if not GMAIL or to in BOUNCE: return False
    eid = jid or ("em_" + re.sub(r'[^a-z0-9]', '', co.lower())[:18])
    if seen(eid): return False
    try:
        msg = MIMEMultipart()
        msg["From"] = "Rafael Rodrigues <" + EM + ">"
        msg["To"] = to
        msg["Reply-To"] = PROF["email"]
        msg["Subject"] = "Senior Data Analyst / Power BI Developer — " + co
        body = ("Dear " + co + " Hiring Team,\n\n" + cover(co, role) +
                "\n\nBest regards,\nRafael Rodrigues\n" + PROF["phone"] + " | " + PROF["email"])
        msg.attach(MIMEText(body, "plain"))
        if os.path.exists(CV):
            with open(CV, "rb") as f:
                att = MIMEApplication(f.read(), Name="Rafael_Rodrigues_CV.pdf")
                att["Content-Disposition"] = 'attachment; filename="Rafael_Rodrigues_CV.pdf"'
                msg.attach(att)
        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as s:
            s.login(EM, GMAIL)
            s.send_message(msg)
        save(co, role, "mailto:" + to, eid, "sent", "email", "email_cv")
        return True
    except:
        return False

# ── Greenhouse form ───────────────────────────────────────────────────────────
def fill_gh(ctx, co, role, url, jid):
    pg = ctx.new_page()
    try:
        pg.goto(url, timeout=18000)
        pg.wait_for_load_state("domcontentloaded", timeout=8000)
        time.sleep(1.5)
        if "greenhouse" not in pg.url:
            pg.close()
            return "no_gh"
        cv_txt = cover(co, role)
        filled = 0
        for sel, val in [("#first_name", PROF["first"]), ("input[name='first_name']", PROF["first"]),
                         ("#last_name", PROF["last"]), ("input[name='last_name']", PROF["last"]),
                         ("#email", PROF["email"]), ("input[name='email']", PROF["email"]),
                         ("#phone", PROF["phone"]), ("input[name='phone']", PROF["phone"])]:
            try:
                el = pg.locator(sel).first
                if el.is_visible(timeout=400):
                    el.clear(); el.fill(val); filled += 1
            except: pass
        for sel in ["input[name*='linkedin']", "input[id*='linkedin']"]:
            try:
                el = pg.locator(sel).first
                if el.is_visible(timeout=300): el.fill(PROF["linkedin"])
            except: pass
        if os.path.exists(CV):
            for sel in ["input[type='file'][name*='resume']", "input[type='file']"]:
                try:
                    el = pg.locator(sel).first
                    if el.count(): el.set_input_files(CV); time.sleep(2); break
                except: pass
        for sel in ["textarea[name*='cover']", "#cover_letter_text"]:
            try:
                el = pg.locator(sel).first
                if el.is_visible(timeout=300):
                    el.fill("Dear " + co + " Hiring Team,\n\n" + cv_txt + "\n\nBest,\nRafael\n" + PROF["phone"])
            except: pass
        if filled >= 2:
            for sel in ["input[type='submit']", "button[type='submit']", "#submit_app"]:
                try:
                    el = pg.locator(sel).first
                    if el.is_visible(timeout=1200):
                        el.click(force=True); time.sleep(5)
                        body = pg.inner_text("body")[:300].lower()
                        pg.close()
                        return "success" if any(w in body for w in ["thank", "received", "submitted"]) else "submitted"
                except: pass
        pg.close(); return "fields_" + str(filled)
    except Exception as e:
        try: pg.close()
        except: pass
        return "err:" + str(e)[:20]

def fill_lever(ctx, co, role, url, jid):
    pg = ctx.new_page()
    try:
        pg.goto(url, timeout=18000)
        pg.wait_for_load_state("domcontentloaded", timeout=8000)
        time.sleep(1.5)
        if "lever.co" not in pg.url: pg.close(); return "no_lever"
        cv_txt = cover(co, role); filled = 0
        for sel, val in [("input[name='name']", PROF["first"] + " " + PROF["last"]),
                         ("input[name='email']", PROF["email"]),
                         ("input[name='phone']", PROF["phone"]),
                         ("input[name*='linkedin']", PROF["linkedin"])]:
            try:
                el = pg.locator(sel).first
                if el.is_visible(timeout=400): el.fill(val); filled += 1
            except: pass
        try:
            el = pg.locator("textarea[name='comments'],textarea").first
            if el.is_visible(timeout=300):
                el.fill("Dear " + co + ",\n\n" + cv_txt + "\n\nBest,\nRafael")
        except: pass
        if os.path.exists(CV):
            try:
                el = pg.locator("input[type='file']").first
                if el.count(): el.set_input_files(CV); time.sleep(2)
            except: pass
        if filled >= 2:
            for sel in ["button[type='submit']", "button:has-text('Submit application')"]:
                try:
                    el = pg.locator(sel).first
                    if el.is_visible(timeout=1000):
                        el.click(force=True); time.sleep(5)
                        body = pg.inner_text("body")[:200].lower()
                        pg.close()
                        return "success" if "thank" in body else "submitted"
                except: pass
        pg.close(); return "lever_f" + str(filled)
    except Exception as e:
        try: pg.close()
        except: pass
        return "err:" + str(e)[:20]

# ── WORKDAY apply ─────────────────────────────────────────────────────────────
def fill_workday(ctx, co, role, url, jid):
    """Tenta apply em Workday — form multi-step"""
    pg = ctx.new_page()
    try:
        pg.goto(url, timeout=20000)
        pg.wait_for_load_state("networkidle", timeout=12000)
        time.sleep(2)
        # Clicar Apply
        for sel in ["a:has-text('Apply')", "button:has-text('Apply')",
                    "[data-automation-id='applyNowButton']", ".css-apply-button"]:
            try:
                el = pg.locator(sel).first
                if el.is_visible(timeout=1500): el.click(); time.sleep(3); break
            except: pass
        # Verificar se pediu criar conta
        if "create account" in pg.inner_text("body").lower() or "sign in" in pg.inner_text("body").lower():
            # Tentar criar conta ou preencher como guest
            for sel in ["button:has-text('Apply Manually')", "a:has-text('Apply Manually')",
                        "button:has-text('Continue as Guest')", "[data-automation-id='createAccountLink']"]:
                try:
                    el = pg.locator(sel).first
                    if el.is_visible(timeout=1000): el.click(); time.sleep(2); break
                except: pass
        filled = 0
        # Preencher campos básicos
        for sel, val in [
            ("[data-automation-id='legalNameSection_firstName']", PROF["first"]),
            ("[data-automation-id='legalNameSection_lastName']", PROF["last"]),
            ("[data-automation-id='email']", PROF["email"]),
            ("[data-automation-id='phone-number']", PROF["phone"]),
            ("input[name*='firstName']", PROF["first"]),
            ("input[name*='lastName']", PROF["last"]),
            ("input[type='email']", PROF["email"]),
        ]:
            try:
                el = pg.locator(sel).first
                if el.is_visible(timeout=500): el.fill(val); filled += 1
            except: pass
        # Upload CV se disponível
        if os.path.exists(CV):
            for sel in ["input[type='file']", "[data-automation-id='file-upload-input']"]:
                try:
                    el = pg.locator(sel).first
                    if el.count(): el.set_input_files(CV); time.sleep(2); break
                except: pass
        pg.close()
        if filled >= 2:
            return "workday_partial_" + str(filled)
        return "workday_no_fields"
    except Exception as e:
        try: pg.close()
        except: pass
        return "workday_err:" + str(e)[:20]

# ── Company→email fallback ────────────────────────────────────────────────────
def company_email_fallback(co, role, jid=None):
    """Tenta email direto para a empresa usando domínio inferido"""
    co_lower = co.lower().strip()
    # Verificar emails conhecidos primeiro
    for key, addr in KNOWN_EMAILS.items():
        if key in co_lower:
            return send_email(addr, co, role, jid)
    # Inferir domínio
    slug = re.sub(r'\b(inc|llc|corp|ltd|co|the|group|global|technologies|solutions|consulting|services)\b', '', co_lower)
    slug = re.sub(r'[^a-z0-9]', '', slug.strip())[:20]
    if not slug: return False
    for pattern in ["careers@{}.com", "jobs@{}.com", "talent@{}.com", "hr@{}.com"]:
        addr = pattern.format(slug)
        if addr in BOUNCE: continue
        if send_email(addr, co, role, jid):
            return True
    return False

# ── Processar vagas stuck ─────────────────────────────────────────────────────
def process_stuck(ctx):
    """Reprocessa registros com status não-aplicado"""
    print("\n  ── REPROCESSANDO STUCK ───────────────────────")
    stuck_statuses = ["no_board", "no_ats", "ats_workday", "clicked",
                      "opened_page", "tracked", "discovered", "pending_apply",
                      "no_ats_detected", "no_apply", "no_apply_url", "no_board_no_email"]
    all_stuck = []
    for st in stuck_statuses:
        r = sb("GET", "job_applications?status=eq." + urllib.parse.quote(st) +
               "&select=job_id,company,role,url,platform,status&limit=50")
        if isinstance(r, list): all_stuck.extend(r)
    # Dedup by job_id
    seen_jids = set()
    unique = []
    for a in all_stuck:
        jid = a.get("job_id", "")
        if jid and jid not in seen_jids:
            seen_jids.add(jid); unique.append(a)
    print(f"  {len(unique)} registros para reprocessar")
    ok = 0
    for a in unique[:40]:
        co   = (a.get("company") or "?").strip()
        role = (a.get("role") or "Data Analyst").strip()
        url  = a.get("url") or ""
        jid  = a.get("job_id", "")
        plat = a.get("platform", "?")
        if not co or co == "?":
            continue
        print(f"    [{plat:10}] {co[:22]:<22} {role[:30]}", end=" ", flush=True)
        ats = detect_ats(url)
        if ats == "gh":
            res = fill_gh(ctx, co, role, url, jid + "_retry")
            print("→ ✅ GH:" + res) if "success" in res or "submit" in res else print("→ 📋 " + res)
            if "success" in res or "submit" in res: ok += 1
        elif ats == "lever":
            res = fill_lever(ctx, co, role, url, jid + "_retry")
            print("→ ✅ Lever:" + res) if "success" in res or "submit" in res else print("→ 📋 " + res)
            if "success" in res or "submit" in res: ok += 1
        elif ats == "workday":
            res = fill_workday(ctx, co, role, url, jid + "_wd")
            print("→ 📋 WD:" + res)
            if "partial" in res:
                # Salvar como workday_applied e tentar email como backup
                save(co, role, url, jid + "_wd", res, plat, "workday")
                if company_email_fallback(co, role, jid + "_em"):
                    print("    + 📧 email fallback")
                    ok += 1
        else:
            # Email fallback
            sent = company_email_fallback(co, role, jid + "_email_retry")
            if sent:
                print("→ 📧 email_sent"); ok += 1
            else:
                print("→ ⚠️  no_channel")
        time.sleep(0.8)
    print(f"  Stuck reprocessados: {ok} resolvidos")

# ── LinkedIn com regex correto ────────────────────────────────────────────────
def run_linkedin(ctx):
    print("\n  ── LINKEDIN (regex fixo) ─────────────────────")
    ok = processed = 0
    for q in ["power bi developer", "senior data analyst", "analytics engineer", "bi analyst"]:
        try:
            raw = urllib.request.urlopen(urllib.request.Request(
                "https://www.linkedin.com/jobs-guest/jobs/api/seeMoreJobPostings/search"
                "?keywords=" + urllib.parse.quote(q) + "&location=United+States&f_WT=2&start=0&count=20",
                headers={"User-Agent": UA, "Accept": "text/html"}), timeout=10).read().decode("utf-8", errors="ignore")
            # Regex correto para empresa
            companies = [x.strip() for x in re.findall(r'hidden-nested-link[^>]+>([^<]{2,60})</a>', raw)]
            titles    = [x.strip() for x in re.findall(r'base-search-card__title[^>]+>([^<]{5,80})<', raw)]
            job_ids   = re.findall(r'data-entity-urn="[^"]*jobPosting:(\d+)"', raw)
            for i, lid in enumerate(job_ids[:15]):
                jid = "li3_" + lid
                if seen(jid): continue
                co   = (companies[i] if i < len(companies) else "?").strip()
                role = (titles[i] if i < len(titles) else q).strip()
                if not co or co == "?" or not any(k in role.lower() for k in KW): continue
                print(f"    {co[:22]:<22} {role[:32]}", end=" ", flush=True)
                # Buscar board GH/Lever da empresa
                ats_type, apply_url = find_company_ats(co, role)
                if ats_type == "gh":
                    res = fill_gh(ctx, co, role, apply_url, jid)
                    icon = "✅" if "success" in res or "submit" in res else "📋"
                    print("→ " + icon + " GH:" + res)
                elif ats_type == "lever":
                    res = fill_lever(ctx, co, role, apply_url, jid)
                    icon = "✅" if "success" in res or "submit" in res else "📋"
                    print("→ " + icon + " Lv:" + res)
                elif ats_type == "workday":
                    res = fill_workday(ctx, co, role, apply_url, jid)
                    print("→ 📋 WD:" + res)
                    save(co, role, apply_url, jid, res, "LinkedIn", "li_workday")
                    if company_email_fallback(co, role, jid + "_em"):
                        print("    + 📧"); ok += 1
                    processed += 1; time.sleep(1.2); continue
                else:
                    sent = company_email_fallback(co, role, jid + "_email")
                    res = "email_sent" if sent else "no_channel"
                    icon = "📧" if sent else "⚠️"
                    print("→ " + icon + " " + res)
                save(co, role, apply_url or "https://linkedin.com/jobs/view/" + lid + "/",
                     jid, res, "LinkedIn", "li_unified")
                if "success" in res or "submit" in res or "email_sent" in res: ok += 1
                processed += 1; time.sleep(1.2)
        except Exception as e:
            print("    ERRO: " + str(e)[:50])
    print(f"  LinkedIn: {processed} processadas, {ok} aplicadas")

def find_company_ats(company, role=""):
    """Busca board GH/Lever ou domínio Workday da empresa"""
    clean = re.sub(r'\b(inc|llc|corp|ltd|co|the|group|global|technologies|solutions|consulting|services)\b',
                   '', company.lower())
    slug_base = re.sub(r'[^a-z0-9]', '', clean.strip())
    slug_dash  = re.sub(r'[^a-z0-9]', '-', clean.strip()).strip('-')
    words = clean.split()
    slugs = list(dict.fromkeys([
        slug_base, slug_dash,
        slug_base[:10], slug_base[:8],
        words[0] if words else slug_base,
        '-'.join([w for w in words if w]),
        ''.join([w for w in words if len(w) > 2]),
    ]))[:7]
    for slug in slugs:
        if not slug or len(slug) < 2: continue
        # Greenhouse
        try:
            rq = urllib.request.Request(
                "https://boards-api.greenhouse.io/v1/boards/" + slug + "/jobs",
                headers={"User-Agent": UA})
            with urllib.request.urlopen(rq, timeout=4) as r:
                jobs = json.loads(r.read()).get("jobs", [])
            relevant = [j for j in jobs if any(k in j.get("title", "").lower() for k in KW)]
            if relevant:
                return "gh", relevant[0].get("absolute_url", "https://boards.greenhouse.io/" + slug)
            if jobs:
                return "gh", jobs[0].get("absolute_url", "https://boards.greenhouse.io/" + slug)
        except: pass
        # Lever
        try:
            rq2 = urllib.request.Request(
                "https://api.lever.co/v0/postings/" + slug + "?mode=json",
                headers={"User-Agent": UA})
            with urllib.request.urlopen(rq2, timeout=4) as r:
                jobs2 = json.loads(r.read())
            if isinstance(jobs2, list) and jobs2:
                relevant2 = [j for j in jobs2 if any(k in j.get("text", "").lower() for k in KW)]
                target = relevant2[0] if relevant2 else jobs2[0]
                return "lever", target.get("hostedUrl", "https://jobs.lever.co/" + slug)
        except: pass
        # Workday
        try:
            wd_url = "https://" + slug + ".myworkdayjobs.com/External"
            rq3 = urllib.request.Request(wd_url, headers={"User-Agent": UA})
            with urllib.request.urlopen(rq3, timeout=4) as r:
                if r.status == 200:
                    return "workday", wd_url
        except: pass
    return None, ""

# ── Dice via email ───────────────────────────────────────────────────────────
def run_dice_email(ctx):
    """Para vagas Dice que nunca foram submetidas — email direto"""
    print("\n  ── DICE → EMAIL DIRETO ───────────────────────")
    ok = 0
    stuck_dice = sb("GET",
        "job_applications?platform=eq.Dice&status=in.(clicked,discovered,no_ats_detected,needs_token)"
        "&select=job_id,company,role,url&limit=20")
    if not isinstance(stuck_dice, list): stuck_dice = []
    seen_cos = set()
    for a in stuck_dice:
        co   = (a.get("company") or "").strip()
        role = (a.get("role") or "Data Analyst").strip()
        jid  = a.get("job_id", "")
        if not co or co in seen_cos: continue
        seen_cos.add(co)
        print(f"    {co[:25]:<25} {role[:30]}", end=" ", flush=True)
        sent = company_email_fallback(co, role, jid + "_email")
        print("→ 📧 sent" if sent else "→ ⚠️ skip")
        if sent: ok += 1
        time.sleep(0.5)
    print(f"  Dice email: {ok} enviados")

# ── RemoteOK via Playwright real ─────────────────────────────────────────────
def run_remoteok(ctx):
    print("\n  ── REMOTE OK (Playwright) ────────────────────")
    ok = processed = 0
    try:
        raw = urllib.request.urlopen(urllib.request.Request(
            "https://remoteok.com/api", headers={"User-Agent": UA, "Accept": "application/json"}),
            timeout=10).read().decode("utf-8", errors="ignore")
        jobs = json.loads(raw)[1:]
        for j in jobs:
            if not isinstance(j, dict): continue
            if not any(k in j.get("position", "").lower() for k in KW): continue
            jid = "rok3_" + str(j.get("id", ""))
            if seen(jid): continue
            co   = j.get("company", "?")
            role = j.get("position", "?")
            rok_url = j.get("url", "")
            print(f"    {co[:22]:<22} {role[:30]}", end=" ", flush=True)
            # Tentar board GH/Lever direto primeiro
            ats_type, apply_url = find_company_ats(co, role)
            if ats_type == "gh":
                res = fill_gh(ctx, co, role, apply_url, jid)
            elif ats_type == "lever":
                res = fill_lever(ctx, co, role, apply_url, jid)
            else:
                # Playwright visita remoteok page e extrai apply link real
                pg = ctx.new_page()
                try:
                    pg.goto(rok_url, timeout=12000)
                    pg.wait_for_load_state("domcontentloaded", timeout=8000)
                    time.sleep(1.5)
                    # Clicar no Apply button e capturar o URL que ele abre
                    real_url = ""
                    for sel in ["a.button.action-apply", "a[href*='http']:not([href*='remoteok'])"]:
                        try:
                            el = pg.locator(sel).first
                            if el.is_visible(timeout=800):
                                href = el.get_attribute("href") or ""
                                if href and "remoteok" not in href and len(href) > 15:
                                    real_url = href; break
                        except: pass
                    pg.close()
                except:
                    try: pg.close()
                    except: pass
                if real_url:
                    ats2 = detect_ats(real_url)
                    if ats2 == "gh": res = fill_gh(ctx, co, role, real_url, jid)
                    elif ats2 == "lever": res = fill_lever(ctx, co, role, real_url, jid)
                    else:
                        sent = company_email_fallback(co, role, jid + "_em")
                        res = "email_sent" if sent else "no_apply"
                else:
                    sent = company_email_fallback(co, role, jid + "_em")
                    res = "email_sent" if sent else "no_apply"
            icon = "✅" if "success" in res or "submit" in res or "email_sent" in res else "📋"
            print("→ " + icon + " " + res)
            save(co, role, rok_url, jid, res, "RemoteOK", "rok_unified")
            if "success" in res or "submit" in res or "email_sent" in res: ok += 1
            processed += 1; time.sleep(1)
    except Exception as e:
        print("    ERRO: " + str(e)[:60])
    print(f"  RemoteOK: {processed} processadas, {ok} aplicadas")

# ── Indeed via Playwright ────────────────────────────────────────────────────
def run_indeed(ctx):
    print("\n  ── INDEED (Playwright) ───────────────────────")
    ok = processed = 0
    for q in ["power bi", "data analyst", "analytics engineer"]:
        for cc in ["us", "ca", "gb"]:
            try:
                xml = urllib.request.urlopen(urllib.request.Request(
                    "https://" + cc + ".indeed.com/rss?q=" + urllib.parse.quote(q) +
                    "&remotejob=032b3046-06a3-4876-8dfd-474eb5e7ed11&sort=date&limit=8",
                    headers={"User-Agent": UA}), timeout=8).read().decode("utf-8", errors="ignore")
                for item in re.findall(r'<item>(.*?)</item>', xml, re.DOTALL)[:5]:
                    title_m   = re.search(r'<title><!\[CDATA\[([^\]]+)\]\]>|<title>([^<]+)<', item)
                    company_m = re.search(r'<source[^>]*>([^<]+)<', item)
                    jk_m      = re.search(r'jk=([a-f0-9]+)', item)
                    if not jk_m: continue
                    jid  = "ind3_" + cc + "_" + jk_m.group(1)
                    if seen(jid): continue
                    co   = (company_m.group(1).strip() if company_m else "?")
                    role = ((title_m.group(1) or title_m.group(2) or "").strip() if title_m else q)
                    if not any(k in role.lower() for k in KW): continue
                    print(f"    [{cc.upper()}] {co[:20]:<20} {role[:28]}", end=" ", flush=True)
                    # Tentar board GH/Lever da empresa primeiro
                    ats_type, apply_url = find_company_ats(co, role)
                    if ats_type == "gh":
                        res = fill_gh(ctx, co, role, apply_url, jid)
                    elif ats_type == "lever":
                        res = fill_lever(ctx, co, role, apply_url, jid)
                    else:
                        # Playwright extrai apply URL da página Indeed
                        job_url = "https://" + cc + ".indeed.com/viewjob?jk=" + jk_m.group(1)
                        pg = ctx.new_page()
                        try:
                            pg.goto(job_url, timeout=15000)
                            pg.wait_for_load_state("networkidle", timeout=10000)
                            time.sleep(1.5)
                            external_url = ""
                            for sel in ["a#applyButtonLinkContainer", "button[id*='apply']",
                                        "a:has-text('Apply now')", "a:has-text('Apply on company site')"]:
                                try:
                                    el = pg.locator(sel).first
                                    if el.is_visible(timeout=800):
                                        href = el.get_attribute("href") or ""
                                        if href and detect_ats(href):
                                            external_url = href; break
                                except: pass
                            if not external_url:
                                html = pg.content()
                                for pat in [r'"externalApplyLink":"([^"]+)"',
                                            r'(https://[^"]*greenhouse\.io[^"]{5,})',
                                            r'(https://jobs\.lever\.co[^"]{5,})']:
                                    m = re.search(pat, html)
                                    if m: external_url = m.group(1).replace('\\/','\/'); break
                            pg.close()
                        except:
                            try: pg.close()
                            except: pass
                        if external_url and detect_ats(external_url) == "gh":
                            res = fill_gh(ctx, co, role, external_url, jid)
                        elif external_url and detect_ats(external_url) == "lever":
                            res = fill_lever(ctx, co, role, external_url, jid)
                        else:
                            sent = company_email_fallback(co, role, jid + "_em")
                            res = "email_sent" if sent else "no_apply"
                    icon = "✅" if "success" in res or "submit" in res or "email_sent" in res else "📋"
                    print("→ " + icon + " " + res)
                    save(co, role, "https://" + cc + ".indeed.com/viewjob?jk=" + jk_m.group(1),
                         jid, res, "Indeed", "indeed_unified", country=cc.upper())
                    if "success" in res or "submit" in res or "email_sent" in res: ok += 1
                    processed += 1; time.sleep(1.5)
            except: pass
    print(f"  Indeed: {processed} processadas, {ok} aplicadas")

# ── Jobright via Playwright ──────────────────────────────────────────────────
def run_jobright(ctx):
    print("\n  ── JOBRIGHT (Playwright) ─────────────────────")
    ok = processed = 0
    for q in ["power bi", "data analyst", "analytics engineer"]:
        pg = ctx.new_page()
        try:
            pg.goto("https://jobright.ai/jobs?keyword=" + urllib.parse.quote(q) + "&type=Remote",
                    timeout=15000)
            pg.wait_for_load_state("networkidle", timeout=10000)
            time.sleep(2)
            html = pg.content()
            pg.close()
            # Extrair empresa + título + URL
            cos   = re.findall(r'"companyName"\s*:\s*"([^"]+)"', html)
            roles = re.findall(r'"title"\s*:\s*"([^"]{5,80})"', html)
            urls  = re.findall(r'"url"\s*:\s*"(https?://[^"]+)"', html)
            ids   = re.findall(r'"id"\s*:\s*"([a-z0-9\-]{8,})"', html)
            for i, co in enumerate(cos[:10]):
                role = (roles[i] if i < len(roles) else q)
                if not any(k in role.lower() for k in KW): continue
                jid  = "jr3_" + (ids[i][:16] if i < len(ids) else str(i))
                if seen(jid): continue
                url  = (urls[i] if i < len(urls) else "")
                print(f"    {co[:22]:<22} {role[:30]}", end=" ", flush=True)
                ats_type, apply_url = find_company_ats(co, role)
                if ats_type == "gh":
                    res = fill_gh(ctx, co, role, apply_url, jid)
                elif ats_type == "lever":
                    res = fill_lever(ctx, co, role, apply_url, jid)
                else:
                    sent = company_email_fallback(co, role, jid + "_em")
                    res = "email_sent" if sent else "no_board"
                icon = "✅" if "success" in res or "submit" in res or "email_sent" in res else "📋"
                print("→ " + icon + " " + res)
                save(co, role, url or "https://jobright.ai", jid, res, "Jobright.ai", "jr_unified")
                if "success" in res or "submit" in res or "email_sent" in res: ok += 1
                processed += 1; time.sleep(1)
        except Exception as e:
            try: pg.close()
            except: pass
            print("    ERRO: " + str(e)[:50])
    print(f"  Jobright: {processed} processadas, {ok} aplicadas")

# ── ZipRecruiter via Playwright ──────────────────────────────────────────────
def run_ziprecruiter(ctx):
    print("\n  ── ZIPRECRUITER (Playwright) ─────────────────")
    ok = processed = 0
    for q in ["power bi developer", "data analyst", "analytics engineer"]:
        pg = ctx.new_page()
        try:
            pg.goto("https://www.ziprecruiter.com/jobs-search?search=" + urllib.parse.quote(q) +
                    "&location=Remote&days=7", timeout=15000)
            pg.wait_for_load_state("networkidle", timeout=10000)
            time.sleep(2)
            html = pg.content()
            pg.close()
            # Extrair jobs do JSON embutido
            titles  = re.findall(r'"name"\s*:\s*"([^"]{5,80})"', html)
            cos     = re.findall(r'"hiringOrganization"\s*:\s*\{[^}]*"name"\s*:\s*"([^"]+)"', html)
            for i, role in enumerate(titles[:10]):
                if not any(k in role.lower() for k in KW): continue
                co  = (cos[i] if i < len(cos) else "?")
                jid = "zr3_" + re.sub(r'[^a-z0-9]', '', co.lower())[:10] + str(i)
                if seen(jid): continue
                print(f"    {co[:22]:<22} {role[:30]}", end=" ", flush=True)
                ats_type, apply_url = find_company_ats(co, role)
                if ats_type == "gh":
                    res = fill_gh(ctx, co, role, apply_url, jid)
                elif ats_type == "lever":
                    res = fill_lever(ctx, co, role, apply_url, jid)
                else:
                    sent = company_email_fallback(co, role, jid + "_em")
                    res = "email_sent" if sent else "no_board"
                icon = "✅" if "success" in res or "submit" in res or "email_sent" in res else "📋"
                print("→ " + icon + " " + res)
                save(co, role, "", jid, res, "ZipRecruiter", "zr_unified")
                if "success" in res or "submit" in res or "email_sent" in res: ok += 1
                processed += 1; time.sleep(1)
        except Exception as e:
            try: pg.close()
            except: pass
            print("    ERRO: " + str(e)[:50])
    print(f"  ZipRecruiter: {processed} processadas, {ok} aplicadas")

# ── MAIN ─────────────────────────────────────────────────────────────────────
def main():
    from playwright.sync_api import sync_playwright
    today = datetime.date.today().strftime("%d/%m/%Y")
    print("\n" + chr(9473)*58)
    print("  🌍 UNIVERSAL APPLY v1 — " + today)
    print("  Workday + Email fallback + todos os sites")
    print(chr(9473)*58)
    with sync_playwright() as pw:
        br = pw.chromium.launch(headless=True, args=[
            "--no-sandbox", "--disable-dev-shm-usage", "--disable-gpu",
            "--disable-blink-features=AutomationControlled"])
        ctx = br.new_context(
            user_agent=UA, viewport={"width": 1366, "height": 768}, locale="en-US",
            extra_http_headers={"Accept-Language": "en-US,en;q=0.9"})
        ctx.add_init_script("Object.defineProperty(navigator,'webdriver',{get:()=>undefined})")
        process_stuck(ctx)
        run_dice_email(ctx)
        run_linkedin(ctx)
        run_remoteok(ctx)
        run_indeed(ctx)
        run_jobright(ctx)
        run_ziprecruiter(ctx)
        br.close()
    print("\n" + chr(9473)*58)
    print("  ✅ Universal Apply v1 concluído")
    print(chr(9473)*58 + "\n")

if __name__ == "__main__":
    main()
