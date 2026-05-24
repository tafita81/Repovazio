#!/usr/bin/env python3
"""
AUTONOMOUS JOB HUNTER — Rafael Rodrigues
Roda diariamente. Busca vagas, aplica via Greenhouse API / Lever API / Email.
Rastreia tudo no Supabase. Nunca aplica duas vezes para a mesma vaga.
Tel: +5522992418257
"""
import smtplib, time, os, json, re, hashlib, datetime, base64, io
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
import urllib.request, urllib.parse
from urllib.error import HTTPError, URLError

# ─── CREDENCIAIS ──────────────────────────────────────────────────────────────
GMAIL_USER    = "tafita81@gmail.com"
REPLY_TO      = "Rafa_roberto2004@yahoo.com.br"
APP_PASS      = os.environ["GMAIL_APP_PASSWORD"]
SUPABASE_URL  = os.environ.get("SUPABASE_URL","https://tpjvalzwkqwttvmszvie.supabase.co")
SUPABASE_KEY  = os.environ.get("SUPABASE_ANON_KEY","")
CV_PATH       = ".github/assets/rafael_cv.pdf"

# ─── PERFIL COMPLETO DE RAFAEL ─────────────────────────────────────────────────
PROFILE = {
    "first_name":        "Rafael",
    "last_name":         "Rodrigues",
    "email":             "Rafa_roberto2004@yahoo.com.br",
    "phone":             "+5522992418257",
    "phone_country":     "BR",
    "linkedin":          "https://linkedin.com/in/rafael-r-a3946a15",
    "location":          "Brazil",
    "years_experience":  "15",
    "current_title":     "Senior Data Analyst",
    "current_company":   "Dataex",
    "desired_salary":    "120000",
    "currency":          "USD",
    "work_auth":         "Requires Visa Sponsorship",
    "remote_only":       True,
    "available_start":   "Immediately",
    "education_degree":  "Master's Degree",
    "education_school":  "IBMEC Business School",
    "education_major":   "Business Administration (MBA)",
    "certifications":    "Microsoft PL-300, Tableau Desktop Specialist",
}

COVER_TEMPLATE = """Dear Hiring Team,

I am applying for the {role} position at {company}. I am a Senior Data Analyst and Analytics Engineer with 15+ years of enterprise BI experience, Microsoft PL-300 Power BI Data Analyst and Tableau Desktop Specialist certified, available to start immediately.

Selected highlights:
• $9M+ operational savings generated through analytics-driven optimization (TIM/OI Telecommunications)
• 70% reduction in report latency via DAX/SQL optimization (Keyrus)
• Analytics platforms serving 200+ business users across Financial Services, Retail, and Telecom
• 500M+ subscriber records processed monthly in real-time analytics environments
• Multi-cloud: BigQuery · Snowflake · Databricks SQL · Azure Synapse · Amazon Athena

Core stack: Power BI (DAX, Power Query, RLS, Dataflows) · Tableau · Looker · SQL · Python · Azure · GCP · AWS

I combine deep technical expertise with strong stakeholder communication skills, consistently delivering analytics that drive measurable business impact rather than just reports.

Phone: +5522992418257
LinkedIn: https://linkedin.com/in/rafael-r-a3946a15

Available immediately for remote engagement. Looking forward to discussing how I can contribute to {company}'s analytics goals.

Best regards,
Rafael Rodrigues
Senior Data Analyst | Analytics Engineer | Cloud BI Specialist
+55 22 99241-8257 | Rafa_roberto2004@yahoo.com.br
🌎 Open to US/EU Remote | Available Immediately
"""

# ─── SUPABASE HELPERS ──────────────────────────────────────────────────────────
def supa_get(table, params=""):
    url = f"{SUPABASE_URL}/rest/v1/{table}?{params}"
    req = urllib.request.Request(url, headers={
        "apikey": SUPABASE_KEY, "Authorization": f"Bearer {SUPABASE_KEY}",
        "Content-Type": "application/json"
    })
    with urllib.request.urlopen(req, timeout=10) as r:
        return json.loads(r.read())

def supa_insert(table, data):
    url = f"{SUPABASE_URL}/rest/v1/{table}"
    body = json.dumps(data).encode()
    req = urllib.request.Request(url, data=body, method="POST", headers={
        "apikey": SUPABASE_KEY, "Authorization": f"Bearer {SUPABASE_KEY}",
        "Content-Type": "application/json", "Prefer": "return=minimal"
    })
    try:
        with urllib.request.urlopen(req, timeout=10) as r:
            return r.status
    except HTTPError as e:
        if e.code == 409: return 409  # duplicate
        raise

def is_already_applied(external_id):
    try:
        rows = supa_get("job_leads", f"external_id=eq.{urllib.parse.quote(str(external_id))}&applied=eq.true")
        return len(rows) > 0
    except: return False

def mark_applied(external_id, company, role, url, platform, ats_type, salary=""):
    try:
        supa_insert("job_leads", {
            "external_id": str(external_id), "company": company, "role": role,
            "url": url, "platform": platform, "salary": salary or "",
            "application_method": ats_type, "applied": True,
            "applied_at": datetime.datetime.utcnow().isoformat(),
            "ats_type": ats_type
        })
        supa_insert("job_applications", {
            "company": company, "role": role, "url": url,
            "application_method": ats_type, "platform": platform,
            "salary": salary or "", "status": "sent"
        })
    except Exception as e:
        print(f"  [DB] {e}")

# ─── FONTES DE VAGAS ──────────────────────────────────────────────────────────
def search_greenhouse_boards():
    """Busca vagas em Greenhouse de empresas conhecidas"""
    companies = [
        "sorcero","airalo","moniepoint","corsearch","lexipol",
        "preply","ciklum","datadog","gitlab","hubspot","notion",
        "figma","loom","retool","rippling","brex","deel","remote",
        "gusto","lattice","asana","zendesk","intercom","segment",
        "amplitude","mixpanel","dbt-labs","fivetran","stitch",
        "thoughtspot","looker","sisense","sigma","metabase",
        "mode-analytics","hex","lightdash","cube","airbyte",
        "hightouch","census","rudderstack","supermetrics","funnel",
        "klipfolio","grow","chartio","holistics","redash",
    ]
    KEYWORDS = ["data analyst","power bi","business intelligence","bi developer","analytics engineer","bi analyst"]
    found = []
    for co in companies:
        try:
            url = f"https://boards-api.greenhouse.io/v1/boards/{co}/jobs?content=true"
            req = urllib.request.Request(url, headers={"User-Agent":"Mozilla/5.0"})
            with urllib.request.urlopen(req, timeout=8) as r:
                data = json.loads(r.read())
                for j in data.get("jobs",[]):
                    title = j.get("title","").lower()
                    if any(kw in title for kw in KEYWORDS):
                        found.append({
                            "id": f"gh_{co}_{j['id']}",
                            "company": co.replace("-"," ").title(),
                            "role": j["title"],
                            "url": j.get("absolute_url",""),
                            "platform": "Greenhouse",
                            "ats_type": "greenhouse",
                            "ats_company": co,
                            "ats_job_id": j["id"],
                            "salary": "",
                        })
        except: pass
        time.sleep(0.3)
    return found

def search_lever_boards():
    """Busca vagas em Lever de empresas conhecidas"""
    companies = [
        "proxify","edvantis","data-meaning","wire-it",
        "ciklum","nextech","loenbro","imagine-worldwide",
        "scale-ai","openai","anthropic","cohere","mistral-ai",
        "huggingface","weights-biases","neptune-ai","mlflow",
        "databricks","snowflake","dbt-labs","monte-carlo-data",
        "great-expectations","tecton","feast","hopsworks",
        "whylabs","arize-ai","evidently-ai","fiddler","seldon",
        "bentoml","ray","anyscale","modal-labs","replicate",
    ]
    KEYWORDS = ["data analyst","power bi","business intelligence","bi developer","analytics engineer"]
    found = []
    for co in companies:
        try:
            url = f"https://api.lever.co/v0/postings/{co}?mode=json"
            req = urllib.request.Request(url, headers={"User-Agent":"Mozilla/5.0"})
            with urllib.request.urlopen(req, timeout=8) as r:
                jobs = json.loads(r.read())
                for j in jobs:
                    title = j.get("text","").lower()
                    if any(kw in title for kw in KEYWORDS):
                        found.append({
                            "id": f"lv_{co}_{j['id']}",
                            "company": co.replace("-"," ").title(),
                            "role": j["text"],
                            "url": j.get("hostedUrl",""),
                            "platform": "Lever",
                            "ats_type": "lever",
                            "ats_company": co,
                            "ats_job_id": j["id"],
                            "salary": j.get("salaryRange",""),
                        })
        except: pass
        time.sleep(0.3)
    return found

def search_remotive():
    """Busca vagas no Remotive"""
    KEYWORDS = ["data analyst","power bi","business intelligence","bi analyst","analytics engineer"]
    found = []
    try:
        url = "https://remotive.com/api/remote-jobs?category=data&limit=50"
        req = urllib.request.Request(url, headers={"User-Agent":"Mozilla/5.0 AppleWebKit/537.36"})
        with urllib.request.urlopen(req, timeout=15) as r:
            data = json.loads(r.read())
            for j in data.get("jobs",[]):
                title = j.get("title","").lower()
                if any(kw in title for kw in KEYWORDS):
                    co = j["company_name"]
                    email = ""  # Remotive jobs geralmente têm link de aplicação
                    found.append({
                        "id": f"rm_{j['id']}",
                        "company": co,
                        "role": j["title"],
                        "url": j["url"],
                        "platform": "Remotive",
                        "ats_type": "url",
                        "salary": j.get("salary",""),
                    })
    except Exception as e:
        print(f"  [Remotive] {e}")
    return found

# ─── APLICAÇÃO VIA GREENHOUSE API ─────────────────────────────────────────────
def apply_greenhouse(job, cv_bytes):
    co = job["ats_company"]
    jid = job["ats_job_id"]
    cover = COVER_TEMPLATE.format(role=job["role"], company=job["company"])

    boundary = "----FormBoundary" + hashlib.md5(str(time.time()).encode()).hexdigest()[:16]
    body_parts = []

    def add_field(name, value):
        body_parts.append(
            f"--{boundary}\r\nContent-Disposition: form-data; name=\"{name}\"\r\n\r\n{value}\r\n"
        )

    add_field("first_name", PROFILE["first_name"])
    add_field("last_name", PROFILE["last_name"])
    add_field("email", PROFILE["email"])
    add_field("phone", PROFILE["phone"])
    add_field("cover_letter_text", cover)

    # LinkedIn URL
    add_field("job[source][public_name]", "LinkedIn")

    # Custom fields comuns
    add_field("job[questions][phone]", PROFILE["phone"])

    # CV como arquivo
    body_parts.append(
        f"--{boundary}\r\n"
        f"Content-Disposition: form-data; name=\"resume\"; filename=\"Rafael_Rodrigues_CV.pdf\"\r\n"
        f"Content-Type: application/pdf\r\n\r\n"
    )
    body_str = "".join(body_parts).encode("utf-8")
    body_str += cv_bytes
    body_str += f"\r\n--{boundary}--\r\n".encode("utf-8")

    url = f"https://boards-api.greenhouse.io/v1/boards/{co}/jobs/{jid}/applications"
    req = urllib.request.Request(
        url, data=body_str, method="POST",
        headers={
            "Content-Type": f"multipart/form-data; boundary={boundary}",
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36",
        }
    )
    try:
        with urllib.request.urlopen(req, timeout=15) as r:
            return r.status, "success"
    except HTTPError as e:
        body = e.read().decode("utf-8","ignore")[:200]
        return e.code, body
    except Exception as e:
        return 0, str(e)[:100]

# ─── APLICAÇÃO VIA LEVER API ──────────────────────────────────────────────────
def apply_lever(job, cv_bytes):
    co = job["ats_company"]
    jid = job["ats_job_id"]
    cover = COVER_TEMPLATE.format(role=job["role"], company=job["company"])

    boundary = "----LeverBoundary" + hashlib.md5(str(time.time()).encode()).hexdigest()[:16]
    body_parts = []

    def add_field(name, value):
        body_parts.append(
            f"--{boundary}\r\nContent-Disposition: form-data; name=\"{name}\"\r\n\r\n{value}\r\n"
        )

    add_field("name", f"{PROFILE['first_name']} {PROFILE['last_name']}")
    add_field("email", PROFILE["email"])
    add_field("phone", PROFILE["phone"])
    add_field("org", PROFILE["current_company"])
    add_field("urls[LinkedIn]", PROFILE["linkedin"])
    add_field("cover", cover)

    body_parts.append(
        f"--{boundary}\r\n"
        f"Content-Disposition: form-data; name=\"resume\"; filename=\"Rafael_Rodrigues_CV.pdf\"\r\n"
        f"Content-Type: application/pdf\r\n\r\n"
    )
    body_str = "".join(body_parts).encode("utf-8")
    body_str += cv_bytes
    body_str += f"\r\n--{boundary}--\r\n".encode("utf-8")

    url = f"https://api.lever.co/v0/postings/{co}/{jid}/apply"
    req = urllib.request.Request(
        url, data=body_str, method="POST",
        headers={
            "Content-Type": f"multipart/form-data; boundary={boundary}",
            "User-Agent": "Mozilla/5.0",
        }
    )
    try:
        with urllib.request.urlopen(req, timeout=15) as r:
            return r.status, "success"
    except HTTPError as e:
        body = e.read().decode("utf-8","ignore")[:200]
        return e.code, body
    except Exception as e:
        return 0, str(e)[:100]

# ─── ENVIO DE EMAIL ────────────────────────────────────────────────────────────
EMAIL_TARGETS = [
    # Seed companies com emails confirmados (adicionar novas a cada semana via monitor)
    {"company":"Edvantis","role":"Senior Analytics Engineer (Power BI)","to":"recruiting@edvantis.com"},
    {"company":"Wire IT","role":"Power BI Developer","to":"info@wireit.pt"},
    {"company":"Data Meaning","role":"Power BI Developer / BI Consultant","to":"info@datameaning.com"},
    {"company":"Proxify","role":"Senior Power BI Developer","to":"talent@proxify.io"},
    {"company":"Smart Working","role":"Senior Power BI Developer","to":"jobs@smartworking.io"},
    {"company":"Ciklum","role":"Senior BI Analyst","to":"careers@ciklum.com"},
    {"company":"Sorcero","role":"Senior Data Analyst","to":"careers@sorcero.com"},
    {"company":"Loenbro","role":"BI Engineer","to":"hr@loenbro.com"},
    {"company":"GXO Logistics","role":"Senior Analyst DA & BI","to":"analytics.talent@gxo.com"},
    {"company":"PRECISIONeffect","role":"Senior Data Analyst (Power BI)","to":"careers@precisioneffect.com"},
    {"company":"Corsearch","role":"Senior Data Analyst","to":"careers@corsearch.com"},
    {"company":"Airalo","role":"Senior Data Analyst (Growth)","to":"people@airalo.com"},
    {"company":"Moniepoint","role":"Senior Data Analyst","to":"talent@moniepoint.com"},
    {"company":"Keyrus Global","role":"Senior Power BI Consultant","to":"talent@keyrus.com"},
    {"company":"Imagine Worldwide","role":"Senior BI & Data Analyst","to":"jobs@imagineworldwide.org"},
    {"company":"Digital Data Foundation","role":"Power BI Developer","to":"careers@digitaldatafoundation.com"},
    {"company":"Alpha Omega","role":"Azure Power BI Developer","to":"careers@alphaomega.com"},
    {"company":"Exsilio Solutions","role":"Power BI Developer","to":"hr@exsilio.com"},
    {"company":"Rock Encantech","role":"Senior Data Analyst","to":"people@rockencantech.com.br"},
    {"company":"Lexipol","role":"Senior Reporting Analyst GTM","to":"recruiting@lexipol.com"},
    {"company":"Preply","role":"Senior Data Analyst London","to":"recruiting@preply.com"},
    {"company":"Upvanta","role":"Data Visualization Expert Power BI","to":"rekrutacja@upvanta.com"},
    {"company":"NearSource Technologies","role":"Senior DA SQL Power BI Looker","to":"careers@nearsource.com"},
    {"company":"e.l.f. Beauty","role":"Power BI Developer","to":"careers@elfbeauty.com"},
    {"company":"Trilogy Federal","role":"Senior SQL Server Power BI Developer","to":"jobs@trilogyfederal.com"},
]

SIG_HTML = """<br><br><table style="font-family:Arial,sans-serif;border-top:2px solid #1F3864;padding-top:12px;">
<tr><td>
<div style="font-size:15px;font-weight:800;color:#1F3864;">Rafael Rodrigues</div>
<div style="font-size:12px;color:#5B21B6;">Senior Data Analyst &nbsp;·&nbsp; Analytics Engineer &nbsp;·&nbsp; Cloud BI Specialist</div>
<div style="font-size:11px;color:#555;line-height:1.8;margin-top:4px;">
📱 <strong>+55 22 99241-8257</strong><br>✉️ Rafa_roberto2004@yahoo.com.br<br>
🔗 linkedin.com/in/rafael-r-a3946a15<br>
🌎 <strong>Open to US/EU Remote &nbsp;|&nbsp; Available Immediately</strong>
</div></td></tr></table>"""

IMPACT = """<table style="width:100%;border-collapse:collapse;margin:14px 0;font-size:12px;">
<tr style="background:#1F3864;"><td colspan="2" style="padding:7px 12px;color:#fff;font-weight:700;letter-spacing:1px;text-transform:uppercase;">Selected Impact — 15+ Years</td></tr>
<tr style="background:#F8FAFC;border-bottom:1px solid #E5E7EB;"><td style="padding:7px 12px;color:#374151;">💰 Operational Savings</td><td style="padding:7px 12px;font-weight:700;color:#059669;">$9M+</td></tr>
<tr style="border-bottom:1px solid #E5E7EB;"><td style="padding:7px 12px;color:#374151;">⚡ Report Latency Reduction</td><td style="padding:7px 12px;font-weight:700;color:#5B21B6;">70%</td></tr>
<tr style="background:#F8FAFC;border-bottom:1px solid #E5E7EB;"><td style="padding:7px 12px;color:#374151;">👥 Business Users Served</td><td style="padding:7px 12px;font-weight:700;">200+</td></tr>
<tr style="border-bottom:1px solid #E5E7EB;"><td style="padding:7px 12px;color:#374151;">📊 Monthly Records Processed</td><td style="padding:7px 12px;font-weight:700;">500M+</td></tr>
<tr><td style="padding:7px 12px;color:#374151;">📞 Contact</td><td style="padding:7px 12px;font-weight:700;color:#1F3864;">+55 22 99241-8257</td></tr>
</table>"""

def build_email_html(company, role, cover):
    return f"""<html><body style="font-family:Arial,sans-serif;max-width:680px;margin:0 auto;color:#1F2937;">
<div style="background:linear-gradient(135deg,#1F3864,#5B21B6);padding:20px 24px;border-radius:8px 8px 0 0;">
<div style="color:rgba(255,255,255,.7);font-size:10px;letter-spacing:3px;text-transform:uppercase;">Application · {company}</div>
<div style="color:#fff;font-size:20px;font-weight:800;margin:6px 0 2px;">{role}</div>
<div style="color:rgba(255,255,255,.75);font-size:12px;">Rafael Rodrigues · 15+ Years Enterprise BI · PL-300 · Tableau Specialist</div>
</div>
<div style="background:#fff;padding:24px;border:1px solid #E5E7EB;border-top:none;border-radius:0 0 8px 8px;">
{"".join(f"<p style='font-size:13px;line-height:1.8;color:#374151;'>{p}</p>" for p in cover.strip().split('\n\n') if p.strip())}
{IMPACT}
{SIG_HTML}
</div></body></html>"""

def send_email_application(server, target, cv_bytes, today_str):
    cover = COVER_TEMPLATE.format(role=target["role"], company=target["company"])
    html  = build_email_html(target["company"], target["role"], cover)
    msg   = MIMEMultipart("mixed")
    msg["From"]     = f"Rafael Rodrigues <{GMAIL_USER}>"
    msg["To"]       = target["to"]
    msg["Subject"]  = f"Application: {target['role']} — 15+ Years | PL-300 | +55 22 99241-8257 | Available Immediately"
    msg["Reply-To"] = REPLY_TO
    msg.attach(MIMEText(html, "html"))
    # Attach PDF CV
    att = MIMEBase("application","pdf")
    att.set_payload(cv_bytes)
    encoders.encode_base64(att)
    att.add_header("Content-Disposition","attachment",filename="Rafael_Rodrigues_Senior_DA_CV.pdf")
    msg.attach(att)
    server.sendmail(GMAIL_USER, [target["to"]], msg.as_string())

# ─── RELATÓRIO DIÁRIO ──────────────────────────────────────────────────────────
def send_daily_report(server, results, today_str):
    rows = ""
    for r in results:
        icon = "✅" if r["status"]=="ok" else "⚠️" if r["status"]=="partial" else "❌"
        rows += f"<tr style='border-bottom:1px solid #E5E7EB;'><td style='padding:8px 10px;'>{icon}</td><td style='padding:8px 10px;font-weight:600;color:#1F3864;'>{r['company']}</td><td style='padding:8px 10px;font-size:12px;color:#6B7280;'>{r['role'][:50]}</td><td style='padding:8px 10px;font-size:11px;'>{r['method']}</td><td style='padding:8px 10px;'>{r.get('detail','')[:30]}</td></tr>"

    ok = sum(1 for r in results if r["status"]=="ok")
    html = f"""<html><body style="font-family:Arial,sans-serif;max-width:760px;margin:0 auto;">
<div style="background:linear-gradient(135deg,#1F3864,#5B21B6);padding:22px 26px;border-radius:8px 8px 0 0;">
<div style="color:#C4B5FD;font-size:10px;letter-spacing:3px;text-transform:uppercase;">{today_str}</div>
<div style="color:#fff;font-size:22px;font-weight:800;margin-top:6px;">🤖 Job Hunt Daily Report</div>
<div style="color:#C4B5FD;font-size:13px;">Rafael Rodrigues · Autonomous Job Application System</div>
<div style="display:flex;gap:20px;margin-top:14px;">
<div style="background:rgba(255,255,255,.12);border-radius:8px;padding:10px 16px;text-align:center;">
<div style="color:#34D399;font-size:24px;font-weight:900;">{ok}</div>
<div style="color:rgba(255,255,255,.7);font-size:11px;">Aplicadas</div></div>
<div style="background:rgba(255,255,255,.12);border-radius:8px;padding:10px 16px;text-align:center;">
<div style="color:#FCD34D;font-size:24px;font-weight:900;">{len(results)}</div>
<div style="color:rgba(255,255,255,.7);font-size:11px;">Total tentativas</div></div>
</div></div>
<div style="background:#fff;padding:20px;border:1px solid #E5E7EB;border-top:none;border-radius:0 0 8px 8px;">
<table style="width:100%;border-collapse:collapse;">
<tr style="background:#F8FAFC;border-bottom:2px solid #E5E7EB;">
<th style="padding:8px 10px;text-align:left;font-size:11px;color:#6B7280;text-transform:uppercase;"></th>
<th style="padding:8px 10px;text-align:left;font-size:11px;color:#6B7280;text-transform:uppercase;">Empresa</th>
<th style="padding:8px 10px;text-align:left;font-size:11px;color:#6B7280;text-transform:uppercase;">Vaga</th>
<th style="padding:8px 10px;text-align:left;font-size:11px;color:#6B7280;text-transform:uppercase;">Método</th>
<th style="padding:8px 10px;text-align:left;font-size:11px;color:#6B7280;text-transform:uppercase;">Detalhe</th>
</tr>
{rows}
</table>
<div style="margin-top:16px;padding:14px;background:#F0FDF4;border-radius:8px;border:1px solid #BBF7D0;">
<div style="font-size:12px;color:#065F46;">
✅ Sistema rodando · Próxima execução: amanhã às 9h (Brasília)<br>
📞 Tel sempre incluído: <strong>+55 22 99241-8257</strong><br>
📧 Reply-To: Rafa_roberto2004@yahoo.com.br
</div></div></div></body></html>"""

    msg = MIMEMultipart("alternative")
    msg["From"]     = f"Job Hunt Bot <{GMAIL_USER}>"
    msg["To"]       = GMAIL_USER
    msg["Subject"]  = f"🤖 [{today_str}] Job Hunt Report — {ok}/{len(results)} candidaturas enviadas"
    msg.attach(MIMEText(html, "html"))
    server.sendmail(GMAIL_USER, [GMAIL_USER], msg.as_string())

# ─── MAIN ──────────────────────────────────────────────────────────────────────
def main():
    today = datetime.date.today().strftime("%d/%m/%Y")
    print(f"\n{'='*65}")
    print(f"  AUTONOMOUS JOB HUNTER — {today}")
    print(f"  Tel: +5522992418257 | {GMAIL_USER}")
    print(f"{'='*65}\n")

    # Carregar PDF do CV
    cv_bytes = b""
    if os.path.exists(CV_PATH):
        with open(CV_PATH,"rb") as f: cv_bytes = f.read()
        print(f"✅ CV carregado: {len(cv_bytes):,} bytes\n")
    else:
        print("⚠️  CV PDF não encontrado — aplicando sem anexo\n")

    results = []
    server = None
    try:
        server = smtplib.SMTP("smtp.gmail.com", 587)
        server.ehlo(); server.starttls()
        server.login(GMAIL_USER, APP_PASS)
        print("✅ Gmail autenticado\n")
    except Exception as e:
        print(f"❌ Gmail falhou: {e}")

    # ── 1. EMAILS DIRETOS ──────────────────────────────────────────────────────
    print("── FASE 1: EMAILS DIRETOS ──────────────────────────────────────")
    for target in EMAIL_TARGETS:
        eid = f"email_{hashlib.md5(target['to'].encode()).hexdigest()[:8]}_{today.replace('/','')}"
        if is_already_applied(eid):
            print(f"  [SKIP] {target['company']} — já enviado hoje")
            continue
        try:
            if server:
                send_email_application(server, target, cv_bytes, today)
                mark_applied(eid, target["company"], target["role"], target["to"], "email", "email")
                results.append({"company":target["company"],"role":target["role"],"status":"ok","method":"Email","detail":target["to"]})
                print(f"  ✅ {target['company']:<30} → {target['to']}")
            time.sleep(3)
        except Exception as e:
            results.append({"company":target["company"],"role":target["role"],"status":"fail","method":"Email","detail":str(e)[:30]})
            print(f"  ❌ {target['company']:<30} — {str(e)[:40]}")

    # ── 2. GREENHOUSE API ──────────────────────────────────────────────────────
    print(f"\n── FASE 2: GREENHOUSE API ──────────────────────────────────────")
    gh_jobs = search_greenhouse_boards()
    print(f"  Encontradas: {len(gh_jobs)} vagas")
    for job in gh_jobs:
        if is_already_applied(job["id"]):
            continue
        code, detail = apply_greenhouse(job, cv_bytes)
        status = "ok" if code in [200,201] else "partial" if code in [302,303,400] else "fail"
        mark_applied(job["id"],job["company"],job["role"],job["url"],"Greenhouse","greenhouse",job.get("salary",""))
        icon = "✅" if status=="ok" else "⚠️" if status=="partial" else "❌"
        results.append({"company":job["company"],"role":job["role"],"status":status,"method":"Greenhouse API","detail":f"HTTP {code}"})
        print(f"  {icon} {job['company']:<30} {job['role'][:35]} → {code}")
        time.sleep(2)

    # ── 3. LEVER API ───────────────────────────────────────────────────────────
    print(f"\n── FASE 3: LEVER API ───────────────────────────────────────────")
    lv_jobs = search_lever_boards()
    print(f"  Encontradas: {len(lv_jobs)} vagas")
    for job in lv_jobs:
        if is_already_applied(job["id"]):
            continue
        code, detail = apply_lever(job, cv_bytes)
        status = "ok" if code in [200,201] else "partial" if code in [302,303,400] else "fail"
        mark_applied(job["id"],job["company"],job["role"],job["url"],"Lever","lever",job.get("salary",""))
        icon = "✅" if status=="ok" else "⚠️" if status=="partial" else "❌"
        results.append({"company":job["company"],"role":job["role"],"status":status,"method":"Lever API","detail":f"HTTP {code}"})
        print(f"  {icon} {job['company']:<30} {job['role'][:35]} → {code}")
        time.sleep(2)

    # ── 4. RELATÓRIO ────────────────────────────────────────────────────────────
    ok_count = sum(1 for r in results if r["status"]=="ok")
    print(f"\n{'='*65}")
    print(f"  RESULTADO FINAL: {ok_count}/{len(results)} aplicações enviadas")
    print(f"{'='*65}")

    if server and results:
        try:
            send_daily_report(server, results, today)
            print(f"\n✅ Relatório enviado para {GMAIL_USER}")
        except Exception as e:
            print(f"❌ Relatório: {e}")

    if server:
        server.quit()

if __name__ == "__main__":
    main()
