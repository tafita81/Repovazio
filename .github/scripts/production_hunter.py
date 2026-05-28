#!/usr/bin/env python3
"""
EMAIL HUNTER v5 — APENAS ENDEREÇOS VERIFICADOS
Blacklist completa com todos os bounces confirmados pelo Gmail
"""
import os, time, json, smtplib, datetime, urllib.request, urllib.parse
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

# ════════════════════════════════════════════════════════════════════
# BLACKLIST COMPLETA — todos confirmados pelo mailer-daemon no Gmail
# ════════════════════════════════════════════════════════════════════
BOUNCE_BLACKLIST = {
    # Lote 1 (histórico)
    "careers@elfbeauty.com","jobs@trilogyfederal.com","recruiting@preply.com",
    "recruiting@lexipol.com","people@rockencantech.com.br","jobs@imagineworldwide.org",
    "talent@moniepoint.com","analytics.talent@gxo.com","careers@ciklum.com",
    "jobs@smartworking.io","hello@stemma.ai","careers@selectstar.com",
    "jobs@soda.io","careers@acceldata.io","jobs@montecarlodata.com",
    "jobs@evidentlyai.com","jobs@polar-analytics.com","hello@littledata.io",
    "careers@nearsource.com","careers@precisioneffect.com","careers@pachyderm.com",
    "jobs@greatexpectations.io",
    # Lote 2 (28/05 — novos bounces detectados pelo Gmail)
    "jobs@northbeam.io","careers@funnel.io","jobs@improvado.io",
    "hello@pangian.com","join@x-team.com","careers@toggl.com",
    "work@gun.io","hey@lemon.io","hire@turing.com",
    "work@andela.com","talent@toptal.com",
}

# ════════════════════════════════════════════════════════════════════
# LISTA FINAL — apenas endereços que NÃO bouncearam
# Consultoras e Microsoft Partners que aceitam email
# ════════════════════════════════════════════════════════════════════
TARGETS = [
    {"c":"Edvantis",           "r":"Senior Analytics Engineer (Power BI)", "to":"recruiting@edvantis.com"},
    {"c":"Wire IT",            "r":"Power BI Developer",                   "to":"info@wireit.pt"},
    {"c":"Data Meaning",       "r":"Power BI / BI Consultant",             "to":"info@datameaning.com"},
    {"c":"Proxify",            "r":"Senior Power BI Developer",            "to":"talent@proxify.io"},
    {"c":"Sorcero",            "r":"Senior Data Analyst",                  "to":"careers@sorcero.com"},
    {"c":"Loenbro",            "r":"BI Engineer",                          "to":"hr@loenbro.com"},
    {"c":"Corsearch",          "r":"Senior Data Analyst",                  "to":"careers@corsearch.com"},
    {"c":"Airalo",             "r":"Senior Data Analyst, Growth",          "to":"people@airalo.com"},
    {"c":"Keyrus Global",      "r":"Senior Power BI Consultant",           "to":"talent@keyrus.com"},
    {"c":"Alpha Omega",        "r":"Azure Power BI Developer",             "to":"careers@alphaomega.com"},
    {"c":"Exsilio Solutions",  "r":"Power BI Developer",                   "to":"hr@exsilio.com"},
    {"c":"Upvanta",            "r":"Data Visualization Expert Power BI",   "to":"rekrutacja@upvanta.com"},
    {"c":"Arc.dev",            "r":"Senior Power BI Developer",            "to":"talent@arc.dev"},
    {"c":"Crossover",          "r":"Senior Data Analyst",                  "to":"apply@crossover.com"},
    {"c":"Supermetrics",       "r":"Senior Analytics Engineer",            "to":"jobs@supermetrics.com"},
    {"c":"Adjust",             "r":"Senior Data Analyst",                  "to":"jobs@adjust.com"},
    {"c":"AppsFlyer",          "r":"Senior Data Analyst",                  "to":"careers@appsflyer.com"},
    {"c":"Triple Whale",       "r":"Data Analyst",                         "to":"careers@triplewhale.com"},
    {"c":"Atlan",              "r":"Senior Data Analyst",                  "to":"careers@atlan.com"},
    {"c":"WhyLabs",            "r":"Data Analyst",                         "to":"careers@whylabs.ai"},
    {"c":"Arize AI",           "r":"Senior Analytics Engineer",            "to":"jobs@arize.com"},
]

def already_sent(company, email):
    url = (f"{SUPA}/rest/v1/job_applications"
           f"?company=eq.{urllib.parse.quote(company)}"
           f"&email=eq.{urllib.parse.quote(email)}"
           f"&status=in.(sent,success)&select=id&limit=1")
    req = urllib.request.Request(url, headers={"apikey":KEY,"Authorization":f"Bearer {KEY}"})
    try:
        with urllib.request.urlopen(req, timeout=6) as r:
            return len(json.loads(r.read())) > 0
    except: return False

def save(company, role, email):
    now = datetime.datetime.now(datetime.timezone.utc).isoformat()
    req = urllib.request.Request(f"{SUPA}/rest/v1/job_applications",
        data=json.dumps({"company":company,"role":role,"email":email,
            "application_method":"email","status":"sent","platform":"email",
            "applied_at":now}).encode(),
        method="POST",
        headers={"apikey":KEY,"Authorization":f"Bearer {KEY}",
                 "Content-Type":"application/json","Prefer":"return=minimal"})
    try:
        with urllib.request.urlopen(req, timeout=8): pass
    except: pass  # 409 = duplicate = ok

def build(company, role, to):
    msg = MIMEMultipart()
    msg["Subject"] = f"Application: {role} — 15+ Yrs | PL-300 | {PHONE} | Available Immediately"
    msg["From"]    = f"Rafael Rodrigues <{GMAIL}>"
    msg["To"]      = to
    msg["Reply-To"]= REPLY
    msg.attach(MIMEText(f"""Dear {company} Hiring Team,

I am applying for the {role} position.

Senior Data Analyst | Power BI Developer | Analytics Engineer — 15+ years.

Certifications: Microsoft PL-300 | Tableau Desktop Specialist | MBA IBMEC

Impact: USD 9M+ savings · 200+ business users · 70% latency reduction · 500M+ records/month
Stack: Power BI · DAX · SQL · Python · Tableau · BigQuery · Snowflake · Databricks · Azure Synapse

Experience:
• Dataex (2022–Present): Enterprise BI, Power BI + Tableau + Looker, 200+ users
• Keyrus (2019–2022): BI Consultant, Azure Synapse, SAP, Salesforce, 10+ enterprise clients
• Coca-Cola (2018–2019): Senior Data Analyst, BigQuery, 83% automation efficiency
• TIM/OI Telecom (2007–2017): 500M+ records/month, USD 9M+ savings

Available immediately. CV attached.

Rafael Rodrigues | {PHONE} | {REPLY}
LinkedIn: https://linkedin.com/in/rafael-r-a3946a15
""", "plain"))
    if os.path.exists(CV):
        with open(CV,"rb") as f:
            att = MIMEBase("application","octet-stream")
            att.set_payload(f.read())
        encoders.encode_base64(att)
        att.add_header("Content-Disposition","attachment",filename="Rafael_Rodrigues_CV.pdf")
        msg.attach(att)
    return msg

def main():
    today = datetime.date.today().strftime("%d/%m/%Y")
    clean = [t for t in TARGETS if t["to"].lower() not in BOUNCE_BLACKLIST]
    print(f"\n{'='*60}")
    print(f"  EMAIL HUNTER v5 — {today}")
    print(f"  Alvos válidos: {len(clean)} | Blacklist: {len(BOUNCE_BLACKLIST)}")
    print(f"{'='*60}\n")
    if not PASS: print("❌ GMAIL_APP_PASSWORD ausente"); return
    try:
        srv = smtplib.SMTP_SSL("smtp.gmail.com",465)
        srv.login(GMAIL,PASS)
        print("✅ SMTP OK\n")
    except Exception as e: print(f"❌ {e}"); return
    sent = skip = 0
    for t in clean:
        co, role, to = t["c"], t["r"], t["to"]
        if already_sent(co, to):
            print(f"  ⏭️  Já enviado: {co}"); skip+=1; continue
        print(f"  📧 {co:<22} → {to:<38}", end=" ", flush=True)
        try:
            srv.sendmail(GMAIL, to, build(co,role,to).as_string())
            save(co, role, to)
            print("✅"); sent+=1; time.sleep(5)
        except Exception as e:
            print(f"❌ {str(e)[:50]}")
    srv.quit()
    print(f"\n  ✅ {sent} enviados | ⏭️  {skip} já enviados")

if __name__ == "__main__":
    main()
