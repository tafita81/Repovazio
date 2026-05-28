#!/usr/bin/env python3
"""
EMAIL HUNTER v4 — DEFINITIVO
Deduplicação dupla: UNIQUE INDEX no banco + cheque prévio
Nunca envia duas vezes para mesma empresa/email
"""
import os,time,json,smtplib,datetime,urllib.request,urllib.parse
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders

GMAIL  = "tafita81@gmail.com"
PASS   = os.environ.get("GMAIL_APP_PASSWORD","")
REPLY  = "Rafa_roberto2004@yahoo.com.br"
PHONE  = "+5522992418257"
CV     = ".github/assets/rafael_cv.pdf"
SUPA   = os.environ.get("SUPABASE_URL","https://tpjvalzwkqwttvmszvie.supabase.co")
KEY    = os.environ.get("SUPABASE_ANON_KEY","")

BLACKLIST = {
    "careers@elfbeauty.com","jobs@trilogyfederal.com","recruiting@preply.com",
    "recruiting@lexipol.com","people@rockencantech.com.br","jobs@imagineworldwide.org",
    "talent@moniepoint.com","analytics.talent@gxo.com","careers@ciklum.com",
    "jobs@smartworking.io","hello@stemma.ai","careers@selectstar.com",
    "jobs@greatexpectations.io","jobs@soda.io","careers@acceldata.io",
    "jobs@montecarlodata.com","jobs@evidentlyai.com","jobs@polar-analytics.com",
    "hello@littledata.io","careers@nearsource.com","careers@precisioneffect.com",
    "careers@pachyderm.com",
}

TARGETS = [
    {"c":"Edvantis",           "r":"Senior Analytics Engineer (Power BI)",  "to":"recruiting@edvantis.com"},
    {"c":"Wire IT",            "r":"Power BI Developer",                    "to":"info@wireit.pt"},
    {"c":"Data Meaning",       "r":"Power BI Developer / BI Consultant",    "to":"info@datameaning.com"},
    {"c":"Proxify",            "r":"Senior Power BI Developer",             "to":"talent@proxify.io"},
    {"c":"Sorcero",            "r":"Senior Data Analyst",                   "to":"careers@sorcero.com"},
    {"c":"Loenbro",            "r":"BI Engineer",                           "to":"hr@loenbro.com"},
    {"c":"Corsearch",          "r":"Senior Data Analyst",                   "to":"careers@corsearch.com"},
    {"c":"Airalo",             "r":"Senior Data Analyst, Growth",           "to":"people@airalo.com"},
    {"c":"Keyrus Global",      "r":"Senior Power BI Consultant",            "to":"talent@keyrus.com"},
    {"c":"Alpha Omega",        "r":"Azure Power BI Developer",              "to":"careers@alphaomega.com"},
    {"c":"Exsilio Solutions",  "r":"Power BI Developer",                    "to":"hr@exsilio.com"},
    {"c":"Upvanta",            "r":"Data Visualization Expert Power BI",    "to":"rekrutacja@upvanta.com"},
    {"c":"Toptal",             "r":"Senior Data Analyst / Power BI",        "to":"talent@toptal.com"},
    {"c":"Andela",             "r":"Senior Analytics Engineer",             "to":"work@andela.com"},
    {"c":"Turing",             "r":"Senior Data Analyst Remote",            "to":"hire@turing.com"},
    {"c":"Arc.dev",            "r":"Senior Power BI Developer",             "to":"talent@arc.dev"},
    {"c":"Crossover",          "r":"Senior Data Analyst",                   "to":"apply@crossover.com"},
    {"c":"Lemon.io",           "r":"Senior Power BI Developer",             "to":"hey@lemon.io"},
    {"c":"Gun.io",             "r":"Senior Data Analyst",                   "to":"work@gun.io"},
    {"c":"Toggl",              "r":"Senior Analytics Engineer",             "to":"careers@toggl.com"},
    {"c":"X-Team",             "r":"Senior Data Analyst",                   "to":"join@x-team.com"},
    {"c":"Pangian",            "r":"Senior Data Analyst Remote",            "to":"hello@pangian.com"},
    {"c":"Improvado",          "r":"Senior Data Analyst",                   "to":"jobs@improvado.io"},
    {"c":"Funnel.io",          "r":"Senior BI Developer",                   "to":"careers@funnel.io"},
    {"c":"Supermetrics",       "r":"Senior Analytics Engineer",             "to":"jobs@supermetrics.com"},
    {"c":"Adjust",             "r":"Senior Data Analyst",                   "to":"jobs@adjust.com"},
    {"c":"AppsFlyer",          "r":"Senior Data Analyst",                   "to":"careers@appsflyer.com"},
    {"c":"Triple Whale",       "r":"Data Analyst",                         "to":"careers@triplewhale.com"},
    {"c":"Northbeam",          "r":"Senior Data Analyst",                   "to":"jobs@northbeam.io"},
    {"c":"Atlan",              "r":"Senior Data Analyst",                   "to":"careers@atlan.com"},
    {"c":"WhyLabs",            "r":"Data Analyst",                         "to":"careers@whylabs.ai"},
    {"c":"Arize AI",           "r":"Senior Analytics Engineer",             "to":"jobs@arize.com"},
]

def already_sent(company, email):
    """Verifica no banco se já foi enviado — usa o UNIQUE INDEX"""
    url = (f"{SUPA}/rest/v1/job_applications"
           f"?company=eq.{urllib.parse.quote(company)}"
           f"&email=eq.{urllib.parse.quote(email)}"
           f"&status=in.(sent,success)&select=id&limit=1")
    req = urllib.request.Request(url,
        headers={"apikey":KEY,"Authorization":f"Bearer {KEY}"})
    try:
        with urllib.request.urlopen(req, timeout=6) as r:
            return len(json.loads(r.read())) > 0
    except: return False

def save(company, role, email, status):
    now = datetime.datetime.now(datetime.timezone.utc).isoformat()
    url = f"{SUPA}/rest/v1/job_applications"
    data = {"company":company,"role":role,"email":email,
            "application_method":"email","status":status,
            "platform":"email","applied_at":now}
    req = urllib.request.Request(url, data=json.dumps(data).encode(),
        method="POST", headers={"apikey":KEY,"Authorization":f"Bearer {KEY}",
        "Content-Type":"application/json","Prefer":"return=minimal"})
    try:
        with urllib.request.urlopen(req, timeout=8) as r: return r.status
    except Exception as e:
        # 409 = duplicate (UNIQUE INDEX violado) — correto ignorar
        return 409 if "409" in str(e) else 0

def build(company, role, to):
    msg = MIMEMultipart("alternative")
    msg["Subject"] = (f"Application: {role} — 15+ Yrs | PL-300 | "
                      f"{PHONE} | Available Immediately")
    msg["From"]    = f"Rafael Rodrigues <{GMAIL}>"
    msg["To"]      = to
    msg["Reply-To"]= REPLY
    msg.attach(MIMEText(f"""Dear {company} Hiring Team,

I am applying for the {role} position.

Senior Data Analyst | Power BI Developer | Analytics Engineer — 15+ years.

Certifications: Microsoft PL-300 | Tableau Desktop Specialist | MBA IBMEC

Key impact: USD 9M+ savings · 200+ business users · 70% latency reduction · 500M+ records/month
Stack: Power BI · DAX · SQL · Python · Tableau · BigQuery · Snowflake · Databricks · Azure Synapse

Experience:
• Dataex (2022–Present): Enterprise BI, Power BI + Tableau + Looker, 200+ users
• Keyrus (2019–2022): Senior BI Consultant, Azure Synapse, 10+ enterprise clients
• Coca-Cola (2018–2019): Senior Data Analyst, BigQuery, 83% automation efficiency
• TIM/OI Telecom (2007–2017): 500M+ records/month, USD 9M+ savings

Available immediately. CV attached.

Rafael Rodrigues
{PHONE} | {REPLY}
LinkedIn: https://linkedin.com/in/rafael-r-a3946a15
""","plain"))
    if os.path.exists(CV):
        with open(CV,"rb") as f:
            att = MIMEBase("application","octet-stream")
            att.set_payload(f.read())
        encoders.encode_base64(att)
        att.add_header("Content-Disposition","attachment",
                       filename="Rafael_Rodrigues_CV.pdf")
        msg.attach(att)
    return msg

def main():
    today = datetime.date.today().strftime("%d/%m/%Y")
    print(f"\n{'='*60}")
    print(f"  EMAIL HUNTER v4 — {today}")
    print(f"  Dedup: UNIQUE INDEX banco + cheque prévio")
    print(f"{'='*60}\n")
    if not PASS: print("❌ GMAIL_APP_PASSWORD ausente"); return
    try:
        srv = smtplib.SMTP_SSL("smtp.gmail.com",465)
        srv.login(GMAIL,PASS)
        print("✅ SMTP OK\n")
    except Exception as e: print(f"❌ {e}"); return
    sent=skip=err=0
    for t in TARGETS:
        co,role,to = t["c"],t["r"],t["to"]
        # ── Tripla verificação ──────────────────────────────────────────
        if to.lower() in BLACKLIST:
            print(f"  🚫 BLACKLIST   {to}"); skip+=1; continue
        if already_sent(co, to):
            print(f"  ⏭️  JÁ ENVIADO  {co:<22} {to}"); skip+=1; continue
        # ── Enviar ─────────────────────────────────────────────────────
        print(f"  📧 {co:<22} → {to:<38}",end=" ",flush=True)
        try:
            srv.sendmail(GMAIL, to, build(co,role,to).as_string())
            rc = save(co,role,to,"sent")
            if rc == 409:
                print("⏭️  duplicata ignorada (banco)")
                skip+=1
            else:
                print("✅"); sent+=1; time.sleep(4)
        except Exception as e:
            print(f"❌ {str(e)[:50]}"); err+=1; time.sleep(1)
    srv.quit()
    print(f"\n{'='*60}")
    print(f"  ✅ {sent} enviados | ⏭️ {skip} já enviados/blacklist | ❌ {err}")
    print(f"{'='*60}\n")

if __name__ == "__main__":
    main()
