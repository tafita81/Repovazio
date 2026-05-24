#!/usr/bin/env python3
"""
PRODUCTION JOB HUNTER 24/7 — Rafael Rodrigues
Modes: discover | apply | email | report
Tel: +5522992418257
"""
import smtplib, time, os, json, re, hashlib, datetime, base64, sys
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
import urllib.request, urllib.parse
from urllib.error import HTTPError

MODE = sys.argv[1] if len(sys.argv) > 1 else "all"

GMAIL_USER   = "tafita81@gmail.com"
REPLY_TO     = "Rafa_roberto2004@yahoo.com.br"
APP_PASS     = os.environ.get("GMAIL_APP_PASSWORD","")
SUPA_URL     = os.environ.get("SUPABASE_URL","https://tpjvalzwkqwttvmszvie.supabase.co")
SUPA_KEY     = os.environ.get("SUPABASE_ANON_KEY","")
CV_PATH      = ".github/assets/rafael_cv.pdf"
PHONE        = "+5522992418257"

PROFILE = {
    "first_name":"Rafael","last_name":"Rodrigues",
    "email":"Rafa_roberto2004@yahoo.com.br","phone":PHONE,
    "linkedin":"https://linkedin.com/in/rafael-r-a3946a15",
    "current_company":"Dataex","current_title":"Senior Data Analyst",
    "years_experience":"15","location":"Brazil",
    "work_authorization":"require_sponsorship",
}

COVER = lambda role,co: f"""Dear {co} Hiring Team,

I am applying for the {role} position. Senior Data Analyst and Analytics Engineer with 15+ years of enterprise BI experience. Microsoft PL-300 Power BI Data Analyst and Tableau Desktop Specialist certified. Available immediately.

Key achievements:
• $9M+ operational savings — TIM/OI Telecommunications (500M+ records/month)
• 70% report latency reduction via DAX/SQL optimization — Keyrus consulting
• Enterprise analytics for 200+ business users (Financial Services, Retail, Telecom)
• Multi-cloud stack: Power BI · Tableau · BigQuery · Snowflake · Databricks · Azure Synapse

Phone: {PHONE}
LinkedIn: https://linkedin.com/in/rafael-r-a3946a15

Available immediately for remote engagement.

Best regards,
Rafael Rodrigues — Senior Data Analyst | PL-300 | {PHONE}
Rafa_roberto2004@yahoo.com.br | Open to US/EU Remote"""

# ═══ 200+ GREENHOUSE COMPANIES ═══════════════════════════════════════════════
GH_COMPANIES = [
    # Analytics & BI Platforms
    "amplitude","mixpanel","segment","fullstory","heap","pendo",
    "thoughtspot","sigmacomputing","mode-analytics","hex","metabase",
    "redash","lightdash","preset","cube","sisense","chartio",
    "klipfolio","grow","holistics","omni-analytics",
    # Data Engineering
    "dbt-labs","fivetran","airbyte","stitch","hightouch","census",
    "rudderstack","tealium","mparticle","lytics",
    "monte-carlo-data","acceldata","datafold","soda-data",
    "coalesce-io","select-star","atlan","collibra","alation",
    "dagster-io","prefect","astronomer","mage-ai","kestra-io",
    # Cloud & Infrastructure
    "databricks","snowflake","firebolt-analytics","imply","tinybird",
    "clickhouse","starburst","dremio","alluxio","kyligence",
    "neon","planetscale","cockroachdb","upstash","fauna",
    "datadog","newrelic-relyance","honeycombio","grafana-labs",
    "elastic","algolia","typesense","meilisearch",
    # Tech Startups (Series B+)
    "brex","ramp","mercury","stripe","square","marqeta","payoneer",
    "deel","remote","oyster","rippling","gusto","justworks","trinethr",
    "lattice","cultureamp","15five","leapsome","betterworks","reflektive",
    "asana","mondaydotcom","notion","coda","airtable","webflow",
    "figma","invision","zeroheight","loom","miro","conceptboard",
    "zendesk","freshdesk","intercom","drift","gong","outreach","salesloft",
    "hubspot","pipedrive","close","copper","affinity",
    # AI / ML
    "openai","cohere","ai21labs","together-ai","perplexity-ai",
    "scale-ai","labelbox","appen","surge-ai","defined-ai",
    "weights-biases","neptune-ai","arize-ai","whylabs","fiddler-ai",
    "bentoml","ray-project","modal-labs","replicate","banana-dev",
    # Financial
    "coinbase","kraken","gemini-cryptocurrency","robin-hood",
    "plaid","yodlee","finicity","mx-technologies","quovo",
    "adyen","checkout-com","rapyd","stripe","affirm","klarna-us",
    # E-commerce & Retail
    "shopify","woocommerce","bigcommerce","magento","salesforce-commerce",
    "narvar","shipbob","easypost","shipstation","ordoro",
    "bazaarvoice","yotpo","okendo","loox","stamped-io",
    # Healthcare & BioTech
    "sorcero","olive-ai","health-catalyst","arcadia","innovaccer",
    "veradigm","lightbeam-health","arcus","jellyfish",
    "color-genomics","tempus","flatiron-health","veeva",
    # Media & Entertainment
    "spotify","soundcloud","deezer","bandcamp","beatport",
    "canva","crello","visme","piktochart","venngage",
    # Travel & Hospitality
    "airbnb","expedia","booking","tripadvisor","trivago",
    "hopper","kiwi","skyscanner","kayak","momondo",
    # SaaS Enterprise
    "servicenow","freshworks","zoho-corp","zendesk","box",
    "dropbox","docusign","hellosign","pandadoc","signnow",
    "twilio","sendgrid","mailchimp","klaviyo","braze","iterable",
    "amplitude","segment","heap","mixpanel","pendo",
    # Developer Tools
    "gitlab","hashicorp","terraform","ansible","puppet","chef",
    "cloudflare","fastly","bunny-net","imperva","f5",
    "pagerduty","opsgenie","rootly","incident-io","blameless",
    "linear","height-app","plane-dev","shortcut","basecamp",
    "zapier","make","n8n","pipedream","activepieces","integromat",
    "sentry","rollbar","bugsnag","raygun","trackjs",
    # LATAM / Brazil expansion
    "nubank","stone-co","totvs","vtex","linx","movidesk",
    "conta-azul","nuvemshop","rdstation","resultadosdigitais",
    "exact-sales","pipefy","runrun-it","sngular",
]

# ═══ 100+ LEVER COMPANIES ════════════════════════════════════════════════════
LV_COMPANIES = [
    "proxify","edvantis","ciklum","toptal","andela","turing",
    "arc-dev","hired","upwork-enterprise","we-are-developers",
    "scale-ai","appen-technologies","defined-ai","toloka","surge-hq",
    "dataiku","datarobot","h2o-ai","rapids-ai","determined-ai",
    "periscope-data","numerator","similarweb","semrush","sistrix",
    "celonis","process-street","nintex-pega","appian-corp",
    "thoughtworks","slalom","ness-technologies","globant",
    "wizeline","nearshore-it","gorilla-logic","softvision",
    "endava","modus-create","capco","publicis-sapient",
    "booz-allen","leidos","saic-technology","caci-intl",
    "palantir","c3-ai","dataiku","databricks-lever",
    "mongodb","redis-labs","couchbase","arangodb","datastax",
    "timescale","influxdata","questdb","yugabyte","cockroach-labs",
    "pinecone","weaviate","qdrant","chroma-db","milvus",
    "langchain","llamaindex","haystack-deepset","cohere-lever",
    "replit","vercel-jobs","netlify","railway-app","render-com",
    "fly-io","supabase-lever","planetscale-lever","neon-lever",
    "loom","notion-lever","figma-lever","miro-lever","coda-lever",
    "linear-app","height-tasks","plane-so","shortcut-lever",
    "remote-com","deel-lever","oyster-hr","multiplier-hq",
    "papaya-global","globalisation-partners","atlas-hxm","velocity-global",
    "greenhouse-hiring","lever-talent","workable-lever","bamboohr-lever",
    "culture-amp","15five-lever","leapsome-lever","lattice-lever",
    "betterworks","reflektive-lever","engagedly","performyard",
    "gong-io","outreach-lever","salesloft-lever","apollo-io",
    "klenty","lemlist","woodpecker-co","instantly-ai","smartlead",
    "clearbit","lusha","zoominfo-lever","seamless-ai","hunter-io",
    "klaviyo-lever","braze-lever","iterable-lever","sendgrid-lever",
    "mailchimp-lever","activecampaign","drip-ecommerce","convertkit",
    "buffer","hootsuite","sprout-social","brandwatch","mention-me",
]

# ═══ SMARTRECRUITERS COMPANIES ════════════════════════════════════════════════
SR_COMPANIES = [
    "Nike","IKEA","McDonalds","Bosch","Siemens",
    "Airbus","Booking","HelloFresh","Zalando","Klarna",
    "SumUp","N26","Wise","Monzo","Revolut",
    "Delivery Hero","Just Eat Takeaway","DoorDash-SR",
    "Renault","Peugeot","Volkswagen","BMW","Daimler",
    "Deutsche Bank","Societe Generale","BNP Paribas",
    "Carrefour","Auchan","Decathlon","Leroy Merlin",
    "AccorHotels","Marriott-SR","Hilton-SR","IHG",
]

# ═══ EMAIL TARGETS (25 empresas confirmadas) ══════════════════════════════════
EMAIL_TARGETS = [
    # ── Confirmados anteriores ────────────────────────────────────────────────
    {"c":"Edvantis","r":"Senior Analytics Engineer (Power BI)","to":"recruiting@edvantis.com","sector":"consulting"},
    {"c":"Wire IT","r":"Power BI Developer","to":"info@wireit.pt","sector":"consulting"},
    {"c":"Data Meaning","r":"Power BI Developer / BI Consultant","to":"info@datameaning.com","sector":"consulting"},
    {"c":"Proxify","r":"Senior Power BI Developer","to":"talent@proxify.io","sector":"network"},
    {"c":"Smart Working","r":"Senior Power BI Developer","to":"jobs@smartworking.io","sector":"network"},
    {"c":"Ciklum","r":"Senior BI Analyst","to":"careers@ciklum.com","sector":"consulting"},
    {"c":"Sorcero","r":"Senior Data Analyst","to":"careers@sorcero.com","sector":"tech"},
    {"c":"Loenbro","r":"BI Engineer","to":"hr@loenbro.com","sector":"construction"},
    {"c":"GXO Logistics","r":"Senior Analyst DA & BI","to":"analytics.talent@gxo.com","sector":"logistics"},
    {"c":"PRECISIONeffect","r":"Senior Data Analyst (Power BI)","to":"careers@precisioneffect.com","sector":"healthcare"},
    {"c":"Corsearch","r":"Senior Data Analyst","to":"careers@corsearch.com","sector":"tech"},
    {"c":"Airalo","r":"Senior Data Analyst Growth","to":"people@airalo.com","sector":"telecom"},
    {"c":"Moniepoint","r":"Senior Data Analyst","to":"talent@moniepoint.com","sector":"fintech"},
    {"c":"Keyrus Global","r":"Senior Power BI Consultant","to":"talent@keyrus.com","sector":"consulting"},
    {"c":"Imagine Worldwide","r":"Senior BI & Data Analyst","to":"jobs@imagineworldwide.org","sector":"ngo"},
    {"c":"Digital Data Foundation","r":"Power BI Developer","to":"careers@digitaldatafoundation.com","sector":"consulting"},
    {"c":"Alpha Omega","r":"Azure Power BI Developer","to":"careers@alphaomega.com","sector":"government"},
    {"c":"Exsilio Solutions","r":"Power BI Developer","to":"hr@exsilio.com","sector":"microsoft-partner"},
    {"c":"Rock Encantech","r":"Senior Data Analyst","to":"people@rockencantech.com.br","sector":"tech-br"},
    {"c":"Lexipol","r":"Senior Reporting Analyst GTM","to":"recruiting@lexipol.com","sector":"saas"},
    {"c":"Preply","r":"Senior Data Analyst London","to":"recruiting@preply.com","sector":"edtech"},
    {"c":"Upvanta","r":"Data Visualization Expert Power BI","to":"rekrutacja@upvanta.com","sector":"consulting"},
    {"c":"NearSource Technologies","r":"Senior DA SQL Power BI Looker","to":"careers@nearsource.com","sector":"consulting"},
    {"c":"e.l.f. Beauty","r":"Power BI Developer","to":"careers@elfbeauty.com","sector":"retail"},
    {"c":"Trilogy Federal","r":"Senior SQL Server Power BI Developer","to":"jobs@trilogyfederal.com","sector":"government"},
    {"c":"Toptal","r":"Senior Data Analyst / Power BI Developer","to":"talent@toptal.com","sector":"network"},
    {"c":"Andela","r":"Senior Analytics Engineer","to":"work@andela.com","sector":"network"},
    {"c":"Turing","r":"Senior Data Analyst Remote","to":"hire@turing.com","sector":"network"},
    {"c":"Arc.dev","r":"Senior Power BI Developer","to":"talent@arc.dev","sector":"network"},
    {"c":"Crossover","r":"Senior Data Analyst","to":"apply@crossover.com","sector":"network"},
    {"c":"Pangian","r":"Senior Data Analyst Remote","to":"hello@pangian.com","sector":"network"},
    {"c":"X-Team","r":"Senior Data Analyst","to":"join@x-team.com","sector":"network"},
    {"c":"Lemon.io","r":"Senior Power BI Developer","to":"hey@lemon.io","sector":"network"},
    {"c":"Gun.io","r":"Senior Data Analyst","to":"work@gun.io","sector":"network"},
    {"c":"Toggl Hire","r":"Senior Analytics Engineer","to":"careers@toggl.com","sector":"saas"},
    # ── Novos alvos semana 2 ──────────────────────────────────────────────────
    {"c":"Improvado","r":"Senior Data Analyst","to":"jobs@improvado.io","sector":"marketing-analytics"},
    {"c":"Funnel.io","r":"Senior BI Developer","to":"careers@funnel.io","sector":"marketing-analytics"},
    {"c":"Supermetrics","r":"Senior Analytics Engineer","to":"jobs@supermetrics.com","sector":"marketing-analytics"},
    {"c":"Stacked Marketer","r":"Data Analyst","to":"careers@stackedmarketer.com","sector":"media"},
    {"c":"Adjust","r":"Senior Data Analyst","to":"jobs@adjust.com","sector":"mobile-analytics"},
    {"c":"AppsFlyer","r":"Senior Data Analyst","to":"careers@appsflyer.com","sector":"mobile-analytics"},
    {"c":"Branch","r":"Senior Data Analyst","to":"careers@branch.io","sector":"mobile-analytics"},
    {"c":"Singular","r":"BI Analyst","to":"jobs@singular.net","sector":"mobile-analytics"},
    {"c":"Kochava","r":"Senior Data Analyst","to":"careers@kochava.com","sector":"mobile-analytics"},
    {"c":"Northbeam","r":"Senior Data Analyst","to":"jobs@northbeam.io","sector":"marketing-analytics"},
    {"c":"Triple Whale","r":"Data Analyst","to":"careers@triplewhale.com","sector":"ecommerce-analytics"},
    {"c":"Daasity","r":"Senior BI Developer","to":"jobs@daasity.com","sector":"ecommerce-analytics"},
    {"c":"Littledata","r":"Data Analyst","to":"hello@littledata.io","sector":"ecommerce-analytics"},
    {"c":"Polar Analytics","r":"Senior Data Analyst","to":"jobs@polar-analytics.com","sector":"ecommerce-analytics"},
    {"c":"Conjura","r":"Senior Data Analyst","to":"hello@conjura.com","sector":"ecommerce-analytics"},
    {"c":"Pachyderm","r":"Senior Analytics Engineer","to":"careers@pachyderm.com","sector":"mlops"},
    {"c":"Weights & Biases","r":"Senior Data Analyst","to":"jobs@wandb.com","sector":"mlops"},
    {"c":"Comet ML","r":"Analytics Engineer","to":"careers@comet.ml","sector":"mlops"},
    {"c":"Evidently AI","r":"Senior Data Analyst","to":"jobs@evidentlyai.com","sector":"mlops"},
    {"c":"WhyLabs","r":"Data Analyst","to":"careers@whylabs.ai","sector":"mlops"},
    {"c":"Arize AI","r":"Senior Analytics Engineer","to":"jobs@arize.com","sector":"mlops"},
    {"c":"Monte Carlo","r":"Senior Data Analyst","to":"jobs@montecarlodata.com","sector":"data-quality"},
    {"c":"Acceldata","r":"Senior Analytics Engineer","to":"careers@acceldata.io","sector":"data-quality"},
    {"c":"Soda Data","r":"Data Analyst","to":"jobs@soda.io","sector":"data-quality"},
    {"c":"Great Expectations","r":"Senior Data Analyst","to":"jobs@greatexpectations.io","sector":"data-quality"},
    {"c":"Select Star","r":"Analytics Engineer","to":"careers@selectstar.com","sector":"data-catalog"},
    {"c":"Atlan","r":"Senior Data Analyst","to":"careers@atlan.com","sector":"data-catalog"},
    {"c":"DataHub Project","r":"Analytics Engineer","to":"careers@acryl.io","sector":"data-catalog"},
    {"c":"Stemma","r":"Senior Data Analyst","to":"hello@stemma.ai","sector":"data-catalog"},
]

KEYWORDS = ["data analyst","power bi","business intelligence","bi developer","analytics engineer","bi analyst","reporting analyst","data visualization","analytics engineer"]

SIG = f"""<br><br><table style="font-family:Arial;border-top:2px solid #1F3864;padding-top:12px;"><tr><td>
<div style="font-size:15px;font-weight:800;color:#1F3864;">Rafael Rodrigues</div>
<div style="font-size:12px;color:#5B21B6;">Senior Data Analyst · Analytics Engineer · Cloud BI Specialist</div>
<div style="font-size:11px;color:#555;line-height:1.9;margin-top:4px;">
📱 <strong>{PHONE}</strong><br>✉️ {REPLY_TO}<br>
🔗 linkedin.com/in/rafael-r-a3946a15<br>
🌎 <strong>Open to US/EU Remote · Available Immediately</strong></div></td></tr></table>"""

IMPACT = """<table style="width:100%;border-collapse:collapse;margin:12px 0;font-size:12px;">
<tr style="background:#1F3864;"><td colspan="2" style="padding:7px 12px;color:#fff;font-weight:700;letter-spacing:1px;text-transform:uppercase;">Selected Impact — 15+ Years Enterprise BI</td></tr>
<tr style="background:#F8FAFC;border-bottom:1px solid #E5E7EB;"><td style="padding:7px 10px;color:#374151;">💰 Operational Savings</td><td style="padding:7px 10px;font-weight:700;color:#059669;">$9M+ — TIM/OI Telecom</td></tr>
<tr style="border-bottom:1px solid #E5E7EB;"><td style="padding:7px 10px;color:#374151;">⚡ Report Latency Reduction</td><td style="padding:7px 10px;font-weight:700;color:#5B21B6;">70% — Keyrus Consulting</td></tr>
<tr style="background:#F8FAFC;border-bottom:1px solid #E5E7EB;"><td style="padding:7px 10px;color:#374151;">👥 Business Users Served</td><td style="padding:7px 10px;font-weight:700;">200+ across industries</td></tr>
<tr style="border-bottom:1px solid #E5E7EB;"><td style="padding:7px 10px;color:#374151;">📊 Records Processed Monthly</td><td style="padding:7px 10px;font-weight:700;">500M+ subscribers</td></tr>
<tr><td style="padding:7px 10px;color:#374151;">📞 Direct Contact</td><td style="padding:7px 10px;font-weight:700;color:#1F3864;">{PHONE}</td></tr>
</table>""".replace("{PHONE}", PHONE)

# ═══ SUPABASE ═════════════════════════════════════════════════════════════════
def db(method, table, data=None, params=""):
    url = f"{SUPA_URL}/rest/v1/{table}?{params}"
    hdrs = {"apikey":SUPA_KEY,"Authorization":f"Bearer {SUPA_KEY}","Content-Type":"application/json","Prefer":"return=minimal"}
    body = json.dumps(data).encode() if data else None
    req = urllib.request.Request(url, data=body, method=method, headers=hdrs)
    try:
        with urllib.request.urlopen(req, timeout=12) as r:
            try: return json.loads(r.read()), r.status
            except: return {}, r.status
    except HTTPError as e:
        return {}, e.code
    except Exception as e:
        return {}, 0

def is_applied(eid):
    rows, _ = db("GET","job_leads",params=f"external_id=eq.{urllib.parse.quote(str(eid))}&applied=eq.true&select=id")
    return isinstance(rows,list) and len(rows)>0

def save_lead(eid, company, role, url, platform, ats_type, salary=""):
    data = {"external_id":str(eid),"company":company,"role":role,"url":url,
            "platform":platform,"salary":salary or "","application_method":ats_type,
            "applied":True,"applied_at":datetime.datetime.utcnow().isoformat()+"Z","ats_type":ats_type}
    db("POST","job_leads",data)
    db("POST","job_applications",{"company":company,"role":role,"url":url,
        "application_method":ats_type,"platform":platform,"salary":salary or "","status":"sent"})

def get_week_key():
    now = datetime.datetime.utcnow()
    return f"W{now.isocalendar()[1]}_{now.year}"

# ═══ JOB DISCOVERY ════════════════════════════════════════════════════════════
def discover_greenhouse():
    found = []
    for co in GH_COMPANIES:
        try:
            url = f"https://boards-api.greenhouse.io/v1/boards/{co}/jobs"
            req = urllib.request.Request(url, headers={"User-Agent":"JobHunter/1.0"})
            with urllib.request.urlopen(req, timeout=6) as r:
                data = json.loads(r.read())
                for j in data.get("jobs",[]):
                    title = j.get("title","").lower()
                    if any(kw in title for kw in KEYWORDS):
                        found.append({"id":f"gh_{co}_{j['id']}","company":co.replace("-"," ").title(),
                            "role":j["title"],"url":j.get("absolute_url",""),
                            "platform":"Greenhouse","ats_type":"greenhouse",
                            "ats_company":co,"ats_job_id":j["id"],"salary":""})
        except: pass
        time.sleep(0.2)
    return found

def discover_lever():
    found = []
    for co in LV_COMPANIES:
        try:
            url = f"https://api.lever.co/v0/postings/{co}?mode=json"
            req = urllib.request.Request(url, headers={"User-Agent":"JobHunter/1.0"})
            with urllib.request.urlopen(req, timeout=6) as r:
                jobs = json.loads(r.read())
                for j in jobs:
                    title = j.get("text","").lower()
                    if any(kw in title for kw in KEYWORDS):
                        sal = ""
                        if "salaryRange" in j and j["salaryRange"]:
                            sal = f"{j['salaryRange'].get('min','')}–{j['salaryRange'].get('max','')} {j['salaryRange'].get('currency','')}"
                        found.append({"id":f"lv_{co}_{j['id']}","company":co.replace("-"," ").title(),
                            "role":j["text"],"url":j.get("hostedUrl",""),
                            "platform":"Lever","ats_type":"lever",
                            "ats_company":co,"ats_job_id":j["id"],"salary":sal})
        except: pass
        time.sleep(0.2)
    return found

def discover_smartrecruiters():
    found = []
    for co in SR_COMPANIES:
        try:
            slug = co.lower().replace(" ","-").replace("_","-")
            url = f"https://api.smartrecruiters.com/v1/companies/{slug}/postings?limit=20"
            req = urllib.request.Request(url, headers={"User-Agent":"Mozilla/5.0"})
            with urllib.request.urlopen(req, timeout=8) as r:
                data = json.loads(r.read())
                for j in data.get("content",[]):
                    title = j.get("name","").lower()
                    if any(kw in title for kw in KEYWORDS):
                        found.append({"id":f"sr_{slug}_{j['id']}","company":co,
                            "role":j["name"],"url":f"https://jobs.smartrecruiters.com/{slug}/{j['id']}",
                            "platform":"SmartRecruiters","ats_type":"smartrecruiters",
                            "ats_company":slug,"ats_job_id":j["id"],"salary":""})
        except: pass
        time.sleep(0.3)
    return found

# ═══ APPLY GREENHOUSE ══════════════════════════════════════════════════════════
def apply_greenhouse(job, cv_bytes):
    co, jid = job["ats_company"], job["ats_job_id"]
    boundary = "----GHBound" + hashlib.md5(f"{co}{jid}{time.time()}".encode()).hexdigest()[:12]
    parts = []
    for name, val in [("first_name",PROFILE["first_name"]),("last_name",PROFILE["last_name"]),
                      ("email",PROFILE["email"]),("phone",PROFILE["phone"]),
                      ("cover_letter_text",COVER(job["role"],job["company"])),
                      ("job[source][public_name]","LinkedIn")]:
        parts.append(f"--{boundary}\r\nContent-Disposition: form-data; name=\"{name}\"\r\n\r\n{val}\r\n")
    body  = "".join(parts).encode("utf-8")
    body += f"--{boundary}\r\nContent-Disposition: form-data; name=\"resume\"; filename=\"Rafael_Rodrigues_CV.pdf\"\r\nContent-Type: application/pdf\r\n\r\n".encode()
    body += cv_bytes + f"\r\n--{boundary}--\r\n".encode()
    try:
        req = urllib.request.Request(
            f"https://boards-api.greenhouse.io/v1/boards/{co}/jobs/{jid}/applications",
            data=body, method="POST",
            headers={"Content-Type":f"multipart/form-data; boundary={boundary}","User-Agent":"Mozilla/5.0"})
        with urllib.request.urlopen(req, timeout=15) as r:
            return r.status, "ok"
    except HTTPError as e:
        return e.code, e.read().decode("utf-8","ignore")[:80]
    except Exception as e:
        return 0, str(e)[:60]

def apply_lever(job, cv_bytes):
    co, jid = job["ats_company"], job["ats_job_id"]
    boundary = "----LVBound" + hashlib.md5(f"{co}{jid}{time.time()}".encode()).hexdigest()[:12]
    parts = []
    for name, val in [("name",f"{PROFILE['first_name']} {PROFILE['last_name']}"),
                      ("email",PROFILE["email"]),("phone",PROFILE["phone"]),
                      ("org",PROFILE["current_company"]),("urls[LinkedIn]",PROFILE["linkedin"]),
                      ("cover",COVER(job["role"],job["company"]))]:
        parts.append(f"--{boundary}\r\nContent-Disposition: form-data; name=\"{name}\"\r\n\r\n{val}\r\n")
    body  = "".join(parts).encode("utf-8")
    body += f"--{boundary}\r\nContent-Disposition: form-data; name=\"resume\"; filename=\"Rafael_Rodrigues_CV.pdf\"\r\nContent-Type: application/pdf\r\n\r\n".encode()
    body += cv_bytes + f"\r\n--{boundary}--\r\n".encode()
    try:
        req = urllib.request.Request(
            f"https://api.lever.co/v0/postings/{co}/{jid}/apply",
            data=body, method="POST",
            headers={"Content-Type":f"multipart/form-data; boundary={boundary}","User-Agent":"Mozilla/5.0"})
        with urllib.request.urlopen(req, timeout=15) as r:
            return r.status, "ok"
    except HTTPError as e:
        return e.code, e.read().decode("utf-8","ignore")[:80]
    except Exception as e:
        return 0, str(e)[:60]

def apply_smartrecruiters(job, cv_bytes):
    co, jid = job["ats_company"], job["ats_job_id"]
    payload = json.dumps({
        "firstName":PROFILE["first_name"],"lastName":PROFILE["last_name"],
        "email":PROFILE["email"],"phoneNumber":PROFILE["phone"],
        "web":{"LinkedIn":PROFILE["linkedin"]},
        "coverLetter":COVER(job["role"],job["company"])
    }).encode()
    try:
        req = urllib.request.Request(
            f"https://api.smartrecruiters.com/v1/companies/{co}/postings/{jid}/applications",
            data=payload, method="POST",
            headers={"Content-Type":"application/json","User-Agent":"Mozilla/5.0"})
        with urllib.request.urlopen(req, timeout=15) as r:
            return r.status, "ok"
    except HTTPError as e:
        return e.code, e.read().decode("utf-8","ignore")[:80]
    except Exception as e:
        return 0, str(e)[:60]

# ═══ EMAIL ════════════════════════════════════════════════════════════════════
def email_html(company, role):
    cover_txt = COVER(role, company)
    paras = "".join(f"<p style='font-size:13px;line-height:1.9;color:#374151;'>{p}</p>"
                    for p in cover_txt.split('\n\n') if p.strip())
    return f"""<html><body style="font-family:Arial;max-width:700px;margin:0 auto;">
<div style="background:linear-gradient(135deg,#1F3864,#5B21B6);padding:20px 26px;border-radius:8px 8px 0 0;">
<div style="color:rgba(255,255,255,.7);font-size:10px;letter-spacing:3px;text-transform:uppercase;">Application · {company}</div>
<div style="color:#fff;font-size:20px;font-weight:800;margin-top:6px;">{role}</div>
<div style="color:rgba(255,255,255,.75);font-size:12px;">Rafael Rodrigues · 15+ Years · PL-300 · {PHONE}</div>
</div>
<div style="background:#fff;padding:24px;border:1px solid #E5E7EB;border-top:none;border-radius:0 0 8px 8px;">
{paras}{IMPACT}{SIG}</div></body></html>"""

def run_emails(server, cv_bytes):
    wk = get_week_key()
    sent = 0
    for t in EMAIL_TARGETS:
        eid = f"email_{hashlib.md5(t['to'].encode()).hexdigest()[:8]}_{wk}"
        if is_applied(eid):
            continue
        try:
            msg = MIMEMultipart("mixed")
            msg["From"]    = f"Rafael Rodrigues <{GMAIL_USER}>"
            msg["To"]      = t["to"]
            msg["Subject"] = f"Application: {t['r']} — 15+ Yrs | PL-300 | {PHONE} | Available Now"
            msg["Reply-To"]= REPLY_TO
            msg.attach(MIMEText(email_html(t["c"],t["r"]), "html"))
            if cv_bytes:
                att = MIMEBase("application","pdf")
                att.set_payload(cv_bytes); encoders.encode_base64(att)
                att.add_header("Content-Disposition","attachment",filename="Rafael_Rodrigues_Senior_DA_CV.pdf")
                msg.attach(att)
            server.sendmail(GMAIL_USER,[t["to"]],msg.as_string())
            save_lead(eid,t["c"],t["r"],t["to"],"email","email")
            print(f"  ✅ Email → {t['c']} ({t['to']})")
            sent += 1
            time.sleep(4)
        except Exception as e:
            print(f"  ❌ Email {t['c']}: {e}")
    return sent

def run_ats(cv_bytes):
    applied = 0
    jobs = []
    print("  Descobrindo vagas Greenhouse...")
    jobs += discover_greenhouse()
    print(f"  Greenhouse: {len(jobs)} vagas encontradas")
    lv = discover_lever()
    print(f"  Lever: {len(lv)} vagas encontradas")
    jobs += lv
    sr = discover_smartrecruiters()
    print(f"  SmartRecruiters: {len(sr)} vagas encontradas")
    jobs += sr

    for job in jobs:
        if is_applied(job["id"]): continue
        ats = job["ats_type"]
        if ats == "greenhouse":
            code, detail = apply_greenhouse(job, cv_bytes)
        elif ats == "lever":
            code, detail = apply_lever(job, cv_bytes)
        elif ats == "smartrecruiters":
            code, detail = apply_smartrecruiters(job, cv_bytes)
        else:
            continue
        ok = code in [200,201,202]
        save_lead(job["id"],job["company"],job["role"],job["url"],job["platform"],ats,job.get("salary",""))
        icon = "✅" if ok else f"⚠️ {code}"
        print(f"  {icon} {job['ats_type'].upper()}: {job['company'][:25]} — {job['role'][:35]}")
        applied += 1
        time.sleep(2)
    return applied

def send_report(server, email_sent, ats_applied, today):
    html = f"""<html><body style="font-family:Arial;max-width:720px;margin:0 auto;">
<div style="background:linear-gradient(135deg,#1F3864,#5B21B6);padding:22px 26px;border-radius:8px 8px 0 0;">
<div style="color:#C4B5FD;font-size:10px;letter-spacing:3px;text-transform:uppercase;">{today} · 24/7 Production</div>
<div style="color:#fff;font-size:22px;font-weight:800;margin-top:6px;">🤖 Job Hunter — Relatório</div>
<div style="color:#C4B5FD;">Rafael Rodrigues · Sistema Autônomo · {PHONE}</div>
</div>
<div style="background:#fff;padding:20px;border:1px solid #E5E7EB;border-top:none;border-radius:0 0 8px 8px;">
<table style="width:100%;border-collapse:collapse;margin-bottom:16px;">
<tr style="background:#F8FAFC;border-bottom:2px solid #E5E7EB;">
<th style="padding:10px;text-align:left;font-size:11px;color:#6B7280;text-transform:uppercase;">Método</th>
<th style="padding:10px;text-align:left;font-size:11px;color:#6B7280;text-transform:uppercase;">Enviadas</th>
</tr>
<tr style="border-bottom:1px solid #E5E7EB;"><td style="padding:10px;">📧 Emails Diretos (PDF CV)</td><td style="padding:10px;font-weight:700;color:#059669;">{email_sent}</td></tr>
<tr><td style="padding:10px;">🤖 ATS Auto-Apply (GH+LV+SR)</td><td style="padding:10px;font-weight:700;color:#5B21B6;">{ats_applied}</td></tr>
</table>
<div style="padding:14px;background:#F0FDF4;border-radius:8px;border:1px solid #BBF7D0;font-size:12px;color:#065F46;">
✅ Sistema 24/7 ativo · Próxima execução em 2 horas<br>
📞 Tel sempre incluído: <strong>{PHONE}</strong><br>
📊 Rastreamento: supabase.com/dashboard/project/tpjvalzwkqwttvmszvie
</div></div></body></html>"""
    msg = MIMEMultipart("alternative")
    msg["From"] = f"Job Hunter Bot <{GMAIL_USER}>"
    msg["To"]   = GMAIL_USER
    msg["Subject"] = f"🤖 Job Hunt [{today}] — {email_sent} emails + {ats_applied} ATS"
    msg.attach(MIMEText(html,"html"))
    server.sendmail(GMAIL_USER,[GMAIL_USER],msg.as_string())

def main():
    today = datetime.date.today().strftime("%d/%m/%Y %H:%M")
    print(f"\n{'='*65}")
    print(f"  PRODUCTION JOB HUNTER 24/7 — {today}")
    print(f"  Tel: {PHONE} | Mode: {MODE}")
    print(f"{'='*65}\n")

    cv_bytes = b""
    if os.path.exists(CV_PATH):
        with open(CV_PATH,"rb") as f: cv_bytes = f.read()
        print(f"✅ CV PDF: {len(cv_bytes):,} bytes\n")

    server = None
    if APP_PASS and MODE in ["all","email","report"]:
        try:
            server = smtplib.SMTP("smtp.gmail.com",587)
            server.ehlo(); server.starttls()
            server.login(GMAIL_USER,APP_PASS)
            print("✅ Gmail autenticado\n")
        except Exception as e:
            print(f"⚠️  Gmail: {e}\n")

    email_sent = ats_applied = 0

    if MODE in ["all","email"]:
        print("── EMAILS DIRETOS ──────────────────────────────────────────────")
        if server:
            email_sent = run_emails(server, cv_bytes)
            print(f"  Total emails: {email_sent}\n")

    if MODE in ["all","apply"]:
        print("── ATS AUTO-APPLY ──────────────────────────────────────────────")
        ats_applied = run_ats(cv_bytes)
        print(f"  Total ATS: {ats_applied}\n")

    if server and (email_sent + ats_applied) > 0:
        try:
            send_report(server, email_sent, ats_applied, today)
            print(f"✅ Relatório enviado\n")
        except Exception as e:
            print(f"⚠️  Relatório: {e}")

    if server: server.quit()
    print(f"{'='*65}")
    print(f"  TOTAL: {email_sent} emails + {ats_applied} ATS = {email_sent+ats_applied} candidaturas")
    print(f"{'='*65}\n")

if __name__ == "__main__":
    main()
