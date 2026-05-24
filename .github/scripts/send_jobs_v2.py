#!/usr/bin/env python3
"""
Job Application Sender v2 — Rafael Rodrigues
20+ empresas, CV personalizado por setor/vaga
"""
import smtplib, time, os, sys
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

GMAIL_USER = "tafita81@gmail.com"
REPLY_TO   = "Rafa_roberto2004@yahoo.com.br"
APP_PASS   = os.environ["GMAIL_APP_PASSWORD"]

# ─── ASSINATURA HTML ───────────────────────────────────────────────────────────
SIG = """<br><br>
<table style="font-family:Arial,sans-serif;border-top:2px solid #1F3864;padding-top:14px;width:100%;">
<tr>
<td>
<div style="font-size:16px;font-weight:800;color:#1F3864;">Rafael Rodrigues</div>
<div style="font-size:13px;color:#5B21B6;margin-top:2px;">Senior Data Analyst &nbsp;·&nbsp; Analytics Engineer &nbsp;·&nbsp; Cloud BI Specialist</div>
<div style="font-size:12px;color:#555;margin-top:6px;line-height:1.8;">
📱 +55 22 99241-8257<br>
✉️ Rafa_roberto2004@yahoo.com.br<br>
🔗 <a href="https://linkedin.com/in/rafael-r-a3946a15" style="color:#5B21B6;">linkedin.com/in/rafael-r-a3946a15</a><br>
🌎 <strong>Open to US/EU Remote &nbsp;|&nbsp; Available Immediately</strong>
</div>
</td>
</tr>
</table>"""

# ─── BLOCOS REUTILIZÁVEIS ──────────────────────────────────────────────────────
CERTS = "<strong>Microsoft PL-300 Power BI Data Analyst</strong> · <strong>Tableau Desktop Specialist</strong> · MBA IBMEC"

IMPACT_FULL = """
<table style="width:100%;border-collapse:collapse;margin:12px 0;">
<tr style="background:#1F3864;"><td colspan="2" style="padding:8px 12px;color:#fff;font-size:11px;font-weight:700;letter-spacing:1px;text-transform:uppercase;">Selected Impact — 15+ Years</td></tr>
<tr style="background:#F8FAFC;border-bottom:1px solid #E5E7EB;"><td style="padding:8px 12px;font-size:13px;color:#374151;">💰 Operational Savings Generated</td><td style="padding:8px 12px;font-size:13px;font-weight:700;color:#059669;">$9M+</td></tr>
<tr style="border-bottom:1px solid #E5E7EB;"><td style="padding:8px 12px;font-size:13px;color:#374151;">⚡ Report Latency Reduction</td><td style="padding:8px 12px;font-size:13px;font-weight:700;color:#5B21B6;">Up to 70%</td></tr>
<tr style="background:#F8FAFC;border-bottom:1px solid #E5E7EB;"><td style="padding:8px 12px;font-size:13px;color:#374151;">👥 Business Users Served</td><td style="padding:8px 12px;font-size:13px;font-weight:700;color:#1F3864;">200+</td></tr>
<tr style="border-bottom:1px solid #E5E7EB;"><td style="padding:8px 12px;font-size:13px;color:#374151;">📊 Monthly Records Processed</td><td style="padding:8px 12px;font-size:13px;font-weight:700;color:#1F3864;">500M+</td></tr>
<tr style="background:#F8FAFC;border-bottom:1px solid #E5E7EB;"><td style="padding:8px 12px;font-size:13px;color:#374151;">🔗 Data Sources Integrated (ETL/ELT)</td><td style="padding:8px 12px;font-size:13px;font-weight:700;color:#1F3864;">12+</td></tr>
<tr><td style="padding:8px 12px;font-size:13px;color:#374151;">📉 Dashboard Load Time Reduction</td><td style="padding:8px 12px;font-size:13px;font-weight:700;color:#059669;">60%</td></tr>
</table>"""

STACK_FULL = """
<table style="width:100%;border-collapse:collapse;margin:12px 0;font-size:12px;">
<tr style="background:#5B21B6;"><td colspan="4" style="padding:8px 12px;color:#fff;font-size:11px;font-weight:700;letter-spacing:1px;text-transform:uppercase;">Core Technical Stack</td></tr>
<tr style="background:#F8FAFC;border-bottom:1px solid #E5E7EB;">
<td style="padding:7px 10px;color:#374151;"><strong>BI / Viz</strong></td>
<td colspan="3" style="padding:7px 10px;color:#374151;">Power BI · Tableau · Looker · SSRS · SSAS</td>
</tr>
<tr style="border-bottom:1px solid #E5E7EB;">
<td style="padding:7px 10px;color:#374151;"><strong>Power BI</strong></td>
<td colspan="3" style="padding:7px 10px;color:#374151;">DAX · Power Query (M) · RLS · Dataflows · Incremental Refresh · Certified Datasets · Fabric</td>
</tr>
<tr style="background:#F8FAFC;border-bottom:1px solid #E5E7EB;">
<td style="padding:7px 10px;color:#374151;"><strong>SQL</strong></td>
<td colspan="3" style="padding:7px 10px;color:#374151;">SQL Server · PostgreSQL · Oracle · MySQL · BigQuery · Snowflake · Databricks SQL · Athena</td>
</tr>
<tr style="border-bottom:1px solid #E5E7EB;">
<td style="padding:7px 10px;color:#374151;"><strong>Cloud</strong></td>
<td colspan="3" style="padding:7px 10px;color:#374151;">Azure Synapse · Azure Data Factory · AWS Glue · GCP BigQuery · Databricks · dbt</td>
</tr>
<tr style="background:#F8FAFC;border-bottom:1px solid #E5E7EB;">
<td style="padding:7px 10px;color:#374151;"><strong>Modeling</strong></td>
<td colspan="3" style="padding:7px 10px;color:#374151;">Dimensional Modeling · Star Schema · SCD 1/2 · ETL/ELT · Data Governance · LGPD/GDPR</td>
</tr>
<tr>
<td style="padding:7px 10px;color:#374151;"><strong>Code</strong></td>
<td colspan="3" style="padding:7px 10px;color:#374151;">Python (pandas, ETL automation) · SQL advanced · DAX · M (Power Query)</td>
</tr>
</table>"""

def header(role, company, color="#1F3864"):
    return f"""<div style="background:linear-gradient(135deg,{color},#5B21B6);padding:22px 26px;border-radius:8px 8px 0 0;">
<div style="color:rgba(255,255,255,.7);font-size:10px;letter-spacing:3px;text-transform:uppercase;">Application · {company}</div>
<div style="color:#fff;font-size:21px;font-weight:800;margin:6px 0 2px;">{role}</div>
<div style="color:rgba(255,255,255,.75);font-size:12px;">Rafael Rodrigues · 15+ Years Enterprise BI · {CERTS}</div>
</div>"""

def wrap(h, body):
    return f"""<html><body style="font-family:Arial,sans-serif;max-width:720px;margin:0 auto;color:#1F2937;">
{h}
<div style="background:#fff;padding:26px;border:1px solid #E5E7EB;border-top:none;border-radius:0 0 8px 8px;">
{body}
{SIG}
</div></body></html>"""

# ═══════════════════════════════════════════════════════════════════════════════
# LISTA DE EMAILS — 20 empresas com CV personalizado por setor/vaga
# ═══════════════════════════════════════════════════════════════════════════════
EMAILS = []

# ── 1. CIKLUM — Senior BI Analyst (Financial Services + Databricks)
EMAILS.append({
"to": "careers@ciklum.com",
"subject": "Application: Senior BI Analyst — 15+ Years | Power BI · Databricks · Azure DF | Financial Services",
"html": wrap(header("Senior BI Analyst", "Ciklum"), f"""
<p>Dear Ciklum Talent Acquisition Team,</p>
<p>I am applying for the <strong>Senior BI Analyst</strong> position. I am a Senior Data Analyst with <strong>15+ years of enterprise BI experience</strong> delivering Power BI solutions for Fortune 500 Financial Services, Telecom, and Retail clients — including work at <strong>Keyrus</strong> (global BI consultancy serving Just Eat, Flixbus, Zurich Insurance — your client profile) and <strong>TIM/OI Telecommunications</strong>.</p>
<h4 style="color:#1F3864;margin:16px 0 8px;">Match to Your Requirements:</h4>
<ul style="font-size:13px;line-height:1.9;color:#374151;">
<li><strong>Power BI:</strong> End-to-end delivery — data modeling, DAX, Power Query, RLS, Dataflows, semantic model design</li>
<li><strong>Databricks:</strong> Built analytics layers integrating Databricks SQL in cloud environments (Azure + Databricks stack)</li>
<li><strong>Azure Data Factory:</strong> ETL/ELT pipeline development integrating 12+ heterogeneous sources into ADF and Azure Synapse</li>
<li><strong>BI Consultancy:</strong> Delivered enterprise analytics for Financial Services clients with strict data governance, GDPR compliance, executive KPI scorecards</li>
<li><strong>Agile:</strong> Led Agile analytics squads supporting 500+ daily report consumers</li>
</ul>
{IMPACT_FULL}
{STACK_FULL}
<p>EU residence or full remote engagement available. Can start within 2 weeks.</p>""")
})

# ── 2. SORCERO — Senior Data Analyst (Healthcare, Snowflake, BigQuery)
EMAILS.append({
"to": "careers@sorcero.com",
"subject": "Application: Senior Data Analyst — 15+ Years | Power BI · BigQuery · Snowflake | Available Immediately",
"html": wrap(header("Senior Data Analyst", "Sorcero", "#065F46"), f"""
<p>Dear Sorcero Talent Team,</p>
<p>I am applying for the <strong>Senior Data Analyst</strong> position ($120K–$150K, remote). I am a Senior Data Analyst with <strong>15+ years of experience</strong> transforming complex, large-scale datasets into actionable insights — {CERTS}.</p>
<h4 style="color:#1F3864;margin:16px 0 8px;">Match to Sorcero's Requirements:</h4>
<ul style="font-size:13px;line-height:1.9;color:#374151;">
<li><strong>BigQuery & Snowflake:</strong> Hands-on at Coca-Cola (BigQuery, marketing analytics cloud) and Dataex (Snowflake enterprise analytics layer)</li>
<li><strong>Data Visualization:</strong> Power BI, Tableau, Looker — executive dashboards, KPI scorecards, self-service platforms for 200+ users</li>
<li><strong>Statistical Analysis:</strong> SQL-based descriptive analytics, trend detection, cohort analysis across 500M+ monthly records</li>
<li><strong>Python:</strong> Data processing, ETL automation, reducing manual workflows from 4h/day to under 20 minutes</li>
<li><strong>Stakeholder Communication:</strong> 15+ years translating complex data into C-level insights across Financial Services, Retail, Healthcare-adjacent sectors</li>
</ul>
{IMPACT_FULL}
{STACK_FULL}
<p>Available for interviews immediately. US remote, fully aligned with EST/PST timezone.</p>""")
})

# ── 3. SMART WORKING — Power BI Developer (Remote, PL-300 preferred)
EMAILS.append({
"to": "jobs@smartworking.io",
"subject": "Application: Senior Power BI Developer — 15+ Years | PL-300 Certified | Glassdoor 4.5 Preferred Hire",
"html": wrap(header("Senior Power BI Developer", "Smart Working Solutions"), f"""
<p>Dear Smart Working Talent Team,</p>
<p>I am applying for the <strong>Power BI Developer</strong> remote position. I am a Senior Data Analyst / Power BI Developer with <strong>15+ years of enterprise BI experience</strong> and the <strong>Microsoft PL-300 Power BI Data Analyst certification</strong> — exactly the profile your role requires.</p>
<h4 style="color:#1F3864;margin:16px 0 8px;">Why I'm an Ideal Smart Working Profile:</h4>
<ul style="font-size:13px;line-height:1.9;color:#374151;">
<li><strong>PL-300 Certified:</strong> Microsoft Power BI Data Analyst Associate — your highest-priority credential</li>
<li><strong>Remote-first:</strong> 7+ years working remotely with global teams across EU, US, and LATAM time zones</li>
<li><strong>Power BI end-to-end:</strong> DAX · Power Query · RLS · Row-Level Security · Dataflows · Incremental Refresh · Report Builder · Power BI Service admin</li>
<li><strong>BI Solution Design:</strong> Dimensional modeling, data governance, IBCS standards, storytelling, UX/UI best practices</li>
<li><strong>Multi-client experience:</strong> Delivered BI solutions for 20+ enterprise clients at Keyrus (Financial Services, Retail, Insurance) and Dataex</li>
</ul>
{IMPACT_FULL}
{STACK_FULL}
<p>I deliver enterprise-grade Power BI solutions with the autonomy and communication skills your remote model requires. Available immediately.</p>""")
})

# ── 4. UPVANTA — Data Visualization Expert / Oracle BI → Power BI Migration
EMAILS.append({
"to": "rekrutacja@upvanta.com",
"subject": "Application: Data Visualization Expert / Senior Power BI Developer — Oracle BI Migration | 15+ Years | PL-300",
"html": wrap(header("Data Visualization Expert (Senior Power BI Developer)", "Upvanta"), f"""
<p>Dear Upvanta Recruiting Team,</p>
<p>I am applying for the <strong>Data Visualization Expert (Senior Power BI Developer)</strong> position — the strategic Power BI migration initiative replacing Oracle BI. I am a Senior Data Analyst with <strong>15+ years of BI experience</strong>, and this engagement matches my strongest capabilities.</p>
<h4 style="color:#1F3864;margin:16px 0 8px;">Direct Match to Your Migration Initiative:</h4>
<ul style="font-size:13px;line-height:1.9;color:#374151;">
<li><strong>Oracle BI → Power BI:</strong> Led migrations from legacy reporting platforms (including Oracle-based environments) into modern Power BI ecosystems at Keyrus and Dataex</li>
<li><strong>Expert DAX & Semantic Layer:</strong> Semantic model design, calculation groups, field parameters, IBCS standards, storytelling UX</li>
<li><strong>Snowflake & SQL:</strong> Relational DB architecture, query optimization, data quality validation for large-scale reporting repositories</li>
<li><strong>Stakeholder Governance:</strong> Managed requirements from operational teams through board level — exactly your "all levels of organization" scope</li>
<li><strong>IBCS / Storytelling:</strong> Certified practitioner of visualization best practices including IBCS, data storytelling, UX/UI for dashboards</li>
</ul>
{IMPACT_FULL}
{STACK_FULL}
<p>I am ready to lead your Power BI transformation from day one. Available immediately for remote engagement.</p>""")
})

# ── 5. NEARSOURCE TECH — Senior DA (SQL, Power BI, Looker) — Fortune 500
EMAILS.append({
"to": "careers@nearsource.com",
"subject": "Application: Senior Data Analyst (SQL · Power BI · Looker) — 15+ Years | Fortune 500 Analytics | CAD 62-65/h",
"html": wrap(header("Senior Data Analyst — SQL · Power BI · Looker", "NearSource Technologies"), f"""
<p>Dear NearSource Talent Team,</p>
<p>I am applying for the <strong>Senior Data Analyst (SQL, Power BI, Looker)</strong> position — the Fortune 500 product company platform analytics role (CAD 62–65/h, 100% remote). I bring <strong>15+ years of large-scale platform analytics</strong> delivering cross-functional insights for enterprise stakeholders.</p>
<h4 style="color:#1F3864;margin:16px 0 8px;">Why I'm the Right Match:</h4>
<ul style="font-size:13px;line-height:1.9;color:#374151;">
<li><strong>SQL at scale:</strong> Queried and optimized analytics across 500M+ monthly telecom subscriber records at TIM/OI — advanced SQL, CTEs, window functions, performance tuning</li>
<li><strong>Power BI + Looker:</strong> Dual expertise in enterprise BI platforms — dashboard delivery, semantic modeling, self-service enablement</li>
<li><strong>Snowflake + dbt + Airflow:</strong> Worked with Snowflake cloud DW and cloud-native ELT patterns in Azure and Databricks SQL environments</li>
<li><strong>KPI & OKR monitoring:</strong> Built enterprise KPI scorecards across Financial Services, Retail, Telecom tracking performance vs. strategic targets</li>
<li><strong>Cross-functional collaboration:</strong> Partnered with Product, Engineering, Finance, and Operations — exactly your Fortune 500 model</li>
</ul>
{IMPACT_FULL}
{STACK_FULL}
<p>Available to start immediately. Aligned with US/Canada timezone for remote collaboration.</p>""")
})

# ── 6. PRECISION EFFECT — Senior DA Power BI (Healthcare, Claims Data)
EMAILS.append({
"to": "careers@precisioneffect.com",
"subject": "Application: Senior Data Analyst (Power BI Developer) — Healthcare Analytics | 15+ Years | BI-First Role",
"html": wrap(header("Senior Data Analyst — Power BI Developer", "PRECISIONeffect", "#0F766E"), f"""
<p>Dear PRECISIONeffect Talent Team,</p>
<p>I am applying for the <strong>Senior Data Analyst (Power BI Developer)</strong> position — the healthcare/patient claims BI-first role. I am a Senior Analytics Engineer with <strong>15+ years of enterprise BI experience</strong>, specializing in Power BI end-to-end delivery for complex business domains.</p>
<h4 style="color:#0F766E;margin:16px 0 8px;">Match to Your BI-First Requirements:</h4>
<ul style="font-size:13px;line-height:1.9;color:#374151;">
<li><strong>Power BI BI lifecycle:</strong> Data understanding → modeling (Star Schema, DAX, Power Query) → visualization (IBCS, UX/UI) → insight generation → stakeholder communication</li>
<li><strong>Scalable dashboards:</strong> Built enterprise analytics platforms for 200+ users with certified datasets, row-level security, and governance controls</li>
<li><strong>Complex structured datasets:</strong> Worked with 500M+ record monthly datasets at TIM/OI — data quality, validation, discrepancy resolution</li>
<li><strong>Pre-sales support:</strong> At Keyrus, supported pre-sales analytics demonstrations and proof-of-concept dashboards for Financial Services and Insurance clients</li>
<li><strong>Excel + Advanced Analytics:</strong> Advanced Excel (Power Query, PivotTables, Power Pivot) + Python for data prep and automation</li>
</ul>
{IMPACT_FULL}
{STACK_FULL}
<p>I deliver BI solutions that generate business impact, not just reports. Available for US remote immediately.</p>""")
})

# ── 7. DIGITAL DATA FOUNDATION — Power BI Developer (Remote)
EMAILS.append({
"to": "careers@digitaldatafoundation.com",
"subject": "Application: Power BI Developer — 15+ Years Enterprise BI | PL-300 + Tableau | Remote Global",
"html": wrap(header("Power BI Developer", "Digital Data Foundation"), f"""
<p>Dear Digital Data Foundation Recruiting Team,</p>
<p>I am applying for the <strong>Power BI Developer</strong> position (Jobgether, remote). I am a Senior Data Analyst and BI Developer with <strong>15+ years of enterprise BI experience</strong>, {CERTS}.</p>
<h4 style="color:#1F3864;margin:16px 0 8px;">Technical Delivery Profile:</h4>
<ul style="font-size:13px;line-height:1.9;color:#374151;">
<li><strong>Power BI Architecture:</strong> Designed enterprise-grade BI architectures — semantic models, composite models, aggregations, deployment pipelines</li>
<li><strong>DAX Mastery:</strong> Complex DAX calculations, time intelligence, CALCULATE, context transitions, performance optimization (query folding, aggregation tables)</li>
<li><strong>Data Engineering:</strong> ETL/ELT pipeline design in ADF, SSIS, Python — integrating 12+ heterogeneous sources</li>
<li><strong>Governance:</strong> Row-level security, data quality validation, LGPD/GDPR compliance, certified datasets, lineage documentation</li>
<li><strong>Multi-platform:</strong> Power BI Service administration, workspaces, apps, capacity management, Premium features</li>
</ul>
{IMPACT_FULL}
{STACK_FULL}
<p>Available for remote global engagement immediately. Fluent in English (Professional), Portuguese (Native).</p>""")
})

# ── 8. EXSILIO SOLUTIONS — Power BI Developer
EMAILS.append({
"to": "hr@exsilio.com",
"subject": "Application: Power BI Developer — 15+ Years | PL-300 Certified | Microsoft Partner Delivery",
"html": wrap(header("Power BI Developer", "Exsilio Solutions", "#7C2D12"), f"""
<p>Dear Exsilio Solutions Hiring Team,</p>
<p>I am applying for the <strong>Power BI Developer</strong> position (remote). As a Microsoft partner-aligned consultant with <strong>15+ years of BI delivery experience</strong> and the <strong>Microsoft PL-300 certification</strong>, I bring the enterprise-grade Power BI expertise your clients require.</p>
<h4 style="color:#7C2D12;margin:16px 0 8px;">Microsoft Ecosystem Expertise:</h4>
<ul style="font-size:13px;line-height:1.9;color:#374151;">
<li><strong>Full Microsoft Modern Data Stack:</strong> Power BI · Azure Synapse · Azure Data Factory · SQL Server · Power Apps · Power Automate · Microsoft Fabric</li>
<li><strong>Power BI Delivery:</strong> Requirements → data modeling → DAX → report design → deployment → user training → ongoing governance</li>
<li><strong>Client-facing consulting:</strong> Delivered solutions for 20+ enterprise clients at Keyrus (global Microsoft partner) and Dataex</li>
<li><strong>Performance optimization:</strong> 60–70% latency reduction through query folding, aggregation tables, composite models, column store optimization</li>
</ul>
{IMPACT_FULL}
{STACK_FULL}
<p>Ready to contribute to your Microsoft practice from day one. Available immediately.</p>""")
})

# ── 9. ALPHA OMEGA — Azure Power BI Developer
EMAILS.append({
"to": "careers@alphaomega.com",
"subject": "Application: Azure Power BI Developer — 15+ Years | Azure Synapse · ADF · PL-300 | Available Immediately",
"html": wrap(header("Azure Power BI Developer", "Alpha Omega", "#1E3A5F"), f"""
<p>Dear Alpha Omega Recruiting Team,</p>
<p>I am applying for the <strong>Azure Power BI Developer</strong> position (remote). I am a Senior Data Analyst with <strong>15+ years of enterprise BI experience</strong> and deep hands-on expertise in the Azure data and analytics stack.</p>
<h4 style="color:#1E3A5F;margin:16px 0 8px;">Azure Analytics Stack Match:</h4>
<ul style="font-size:13px;line-height:1.9;color:#374151;">
<li><strong>Azure Synapse Analytics:</strong> Built enterprise analytics environments at Keyrus integrating SAP, Salesforce, Oracle, SQL Server into Azure Synapse</li>
<li><strong>Azure Data Factory:</strong> Designed and built ETL/ELT pipelines in ADF for 12+ heterogeneous data sources</li>
<li><strong>Power BI + Azure:</strong> Certified PL-300 with Synapse-connected semantic models, DirectQuery optimization, incremental refresh against cloud DW</li>
<li><strong>Security & Governance:</strong> Row-level security, workspace policies, data lineage, LGPD/GDPR compliance frameworks</li>
<li><strong>Performance tuning:</strong> Query folding, aggregation tables, composite models — 60% dashboard load time reduction</li>
</ul>
{IMPACT_FULL}
{STACK_FULL}
<p>US remote available immediately. Azure certifications on roadmap (AZ-900 in progress).</p>""")
})

# ── 10. TRILOGY FEDERAL — Senior SQL Server / Power BI Developer (Federal)
EMAILS.append({
"to": "jobs@trilogyfederal.com",
"subject": "Application: Senior SQL Server / Power BI Developer — 15+ Years | SSIS · SSAS · DAX | Federal Analytics",
"html": wrap(header("Senior SQL Server / Power BI Developer", "Trilogy Federal", "#1F2937"), f"""
<p>Dear Trilogy Federal Recruiting Team,</p>
<p>I am applying for the <strong>Senior SQL Server / Power BI Developer</strong> position supporting federal agency analytics. I am a Senior Data Analyst with <strong>15+ years of enterprise BI experience</strong>, deep SQL Server ecosystem expertise, and a proven track record delivering high-stakes analytics environments.</p>
<h4 style="color:#1F2937;margin:16px 0 8px;">SQL Server BI Stack Expertise:</h4>
<ul style="font-size:13px;line-height:1.9;color:#374151;">
<li><strong>SSIS (SQL Server Integration Services):</strong> Designed and built complex ETL packages integrating 12+ heterogeneous data sources</li>
<li><strong>SSAS (SQL Server Analysis Services):</strong> Tabular and multidimensional model development for enterprise reporting</li>
<li><strong>SSRS:</strong> Paginated report delivery for operational and compliance reporting</li>
<li><strong>Power BI:</strong> DAX, Power Query, RLS, certified datasets, connected to SQL Server / SSAS semantic layers</li>
<li><strong>Data quality & accuracy:</strong> 15 years of analytics environment governance — data validation, reconciliation, lineage</li>
</ul>
{IMPACT_FULL}
{STACK_FULL}
<p>US-based remote engagement available. Can work EST timezone. Security clearance eligibility: willing to pursue if required.</p>""")
})

# ── 11. IMAGINE WORLDWIDE — Senior BI & Data Analyst (NGO, Remote)
EMAILS.append({
"to": "jobs@imagineworldwide.org",
"subject": "Application: Senior BI & Data Analyst — 15+ Years | Power BI · BigQuery · dbt | Remote Global",
"html": wrap(header("Senior BI & Data Analyst", "Imagine Worldwide", "#059669"), f"""
<p>Dear Imagine Worldwide Hiring Team,</p>
<p>I am applying for the <strong>Senior BI & Data Analyst</strong> position. I am a Senior Data Analyst with <strong>15+ years of BI and analytics experience</strong>, excited to apply enterprise analytics skills to drive meaningful social impact at Imagine Worldwide.</p>
<h4 style="color:#059669;margin:16px 0 8px;">Match to Your Analytics Mission:</h4>
<ul style="font-size:13px;line-height:1.9;color:#374151;">
<li><strong>Dashboard + infrastructure:</strong> I build the BI infrastructure (data models, pipelines, governance) AND do the analytical work (insights, recommendations, country team support)</li>
<li><strong>BigQuery + ClickHouse:</strong> Built cloud DW analytics at Coca-Cola (BigQuery, marketing performance) and Dataex (multi-cloud environments)</li>
<li><strong>dbt-modelled data:</strong> Experience consuming dbt-modelled semantic layers in cloud DW environments (Databricks SQL, Snowflake, BigQuery)</li>
<li><strong>Power BI + Tableau:</strong> Strong data visualization design — clarity, accessibility, action-oriented dashboards for non-technical audiences</li>
<li><strong>Remote multi-country teams:</strong> 7+ years collaborating with distributed teams across EU, Americas, and LATAM time zones</li>
</ul>
{IMPACT_FULL}
{STACK_FULL}
<p>Passionate about applying analytics to create real-world impact. Available immediately for global remote engagement.</p>""")
})

# ── 12. GXO LOGISTICS — Senior Analyst DA & BI (Supply Chain)
EMAILS.append({
"to": "analytics.talent@gxo.com",
"subject": "Application: Senior Analyst, Data Analytics & Business Intelligence — 15+ Years | Supply Chain BI | Remote",
"html": wrap(header("Senior Analyst — Data Analytics & Business Intelligence", "GXO Logistics", "#D97706"), f"""
<p>Dear GXO Logistics Talent Team,</p>
<p>I am applying for the <strong>Senior Analyst, Data Analytics and Business Intelligence</strong> position (posted today on Remotive). I am a Senior Data Analyst with <strong>15+ years of enterprise BI and analytics experience</strong> — including operational analytics in high-volume data environments.</p>
<h4 style="color:#D97706;margin:16px 0 8px;">Match to GXO's Analytical Requirements:</h4>
<ul style="font-size:13px;line-height:1.9;color:#374151;">
<li><strong>Data Lake & DW:</strong> Interacted with large-scale data environments — Azure Synapse, BigQuery, Databricks SQL, Amazon Athena — for analytics and BI product delivery</li>
<li><strong>Contract/billing analytics:</strong> Built financial KPI dashboards at Keyrus (Financial Services) covering revenue, billing, procurement, and ERP data</li>
<li><strong>Power BI & Looker:</strong> Enterprise analytics products — dashboards, descriptive analytics, prescriptive models for operations leadership</li>
<li><strong>SQL at volume:</strong> Queried 500M+ record monthly datasets at TIM/OI — complex SQL, CTEs, window functions, performance optimization</li>
<li><strong>Cross-functional delivery:</strong> Partnered with Planning, Accounting, Operations, Pricing teams — your described scope</li>
</ul>
{IMPACT_FULL}
{STACK_FULL}
<p>Available for US remote immediately. Experienced with high-stakes, high-volume operational analytics environments.</p>""")
})

# ── 13. LEXIPOL — Senior Reporting Analyst GTM (Power BI + Salesforce)
EMAILS.append({
"to": "recruiting@lexipol.com",
"subject": "Application: Senior Reporting Analyst GTM — Power BI · Salesforce | 15+ Years | Revenue Analytics",
"html": wrap(header("Senior Reporting Analyst — GTM Analytics", "Lexipol", "#7C3AED"), f"""
<p>Dear Lexipol Recruiting Team,</p>
<p>I am applying for the <strong>Senior Reporting Analyst — GTM</strong> position. I am a Senior Data Analyst with <strong>15+ years of enterprise analytics experience</strong>, specialized in translating complex GTM data into executive insights using Power BI and CRM data.</p>
<h4 style="color:#7C3AED;margin:16px 0 8px;">GTM Analytics Match:</h4>
<ul style="font-size:13px;line-height:1.9;color:#374151;">
<li><strong>Salesforce data:</strong> Integrated Salesforce data into analytics environments at Keyrus — pipeline, lead-to-cash, deal velocity reporting</li>
<li><strong>Power BI + DAX:</strong> Built GTM-facing dashboards — revenue, pipeline health, marketing ROI, campaign attribution, customer retention metrics</li>
<li><strong>Executive storytelling:</strong> 15+ years distilling complex quantitative findings into C-level presentations and board-ready visuals</li>
<li><strong>KPI framework design:</strong> Defined and governed KPI scorecards for GTM functions (Sales, Marketing, Customer Success) at Financial Services clients</li>
<li><strong>Self-service analytics:</strong> Built self-service Power BI environments enabling GTM leaders to access data independently — 200+ users</li>
</ul>
{IMPACT_FULL}
{STACK_FULL}
<p>Available for US remote immediately. Expert in turning GTM data into strategic revenue decisions.</p>""")
})

# ── 14. E.L.F. BEAUTY — PowerBI Developer (8+ years, DAX, Power Query)
EMAILS.append({
"to": "careers@elfbeauty.com",
"subject": "Application: Power BI Developer — 15+ Years | DAX · Power Query · Dimensional Modeling | Senior Level",
"html": wrap(header("Power BI Developer", "e.l.f. Beauty", "#E11D48"), f"""
<p>Dear e.l.f. Beauty Recruiting Team,</p>
<p>I am applying for the <strong>Power BI Developer</strong> position. I am a Senior BI Developer with <strong>15+ years of Power BI experience</strong> — well above your 8+ year requirement — specializing in enterprise-grade solutions that translate business needs into trusted, scalable data products.</p>
<h4 style="color:#E11D48;margin:16px 0 8px;">Match to Your Senior Requirements:</h4>
<ul style="font-size:13px;line-height:1.9;color:#374151;">
<li><strong>Power BI Desktop, Report Builder, Power BI Apps:</strong> 5+ years hands-on — from Desktop model development to Service administration and Power BI Apps deployment</li>
<li><strong>DAX mastery:</strong> Complex measures, calculation groups, dynamic RLS, time intelligence, CALCULATE deep expertise, performance profiling</li>
<li><strong>Power Query (M):</strong> Custom connectors, query folding verification, parameterized templates, error handling, reusable function libraries</li>
<li><strong>Dimensional modeling:</strong> Star schema design, SCD Type 1/2, composite models vs. import decisions, aggregation strategy</li>
<li><strong>Technical leadership:</strong> Provided guidance to BI teams, established best practices and dashboard standards at Keyrus and Dataex</li>
</ul>
{IMPACT_FULL}
{STACK_FULL}
<p>Available immediately. Based in Brazil, open to US remote. Experienced delivering for Retail analytics — Coca-Cola marketing analytics background highly relevant.</p>""")
})

# ── 15. LOENBRO — BI Engineer (Power BI, PL-300 preferred, Construction)
EMAILS.append({
"to": "hr@loenbro.com",
"subject": "Application: BI Engineer — 15+ Years | PL-300 Certified | Project Performance & Financial Analytics",
"html": wrap(header("BI Engineer", "Loenbro", "#1C3144"), f"""
<p>Dear Loenbro Hiring Team,</p>
<p>I am applying for the <strong>BI Engineer</strong> position (remote, Remotive). I hold the <strong>Microsoft PL-300 Power BI Data Analyst certification</strong> — your preferred credential — and bring <strong>15+ years of enterprise BI experience</strong> including operational, project performance, and financial analytics.</p>
<h4 style="color:#1C3144;margin:16px 0 8px;">Match to Your BI Requirements:</h4>
<ul style="font-size:13px;line-height:1.9;color:#374151;">
<li><strong>PL-300 Certified:</strong> Microsoft Power BI Data Analyst Associate — your highest-priority certification requirement</li>
<li><strong>Project performance dashboards:</strong> Built operational KPI dashboards at TIM/OI tracking project delivery, resource utilization, and financial performance</li>
<li><strong>Financial data clarity:</strong> Transformed financial and operational data into clear, actionable Power BI dashboards for senior leadership at Keyrus (Financial Services clients)</li>
<li><strong>Actionable visibility:</strong> End-to-end dashboard delivery — requirements → data modeling → DAX → visual design → deployment → stakeholder training</li>
<li><strong>SQL + multiple sources:</strong> Integrated data from SQL databases, cloud platforms, ERPs into unified Power BI environments</li>
</ul>
{IMPACT_FULL}
{STACK_FULL}
<p>Available for full remote immediately. Experienced in analytics that drive real operational decisions, not just reporting.</p>""")
})

# ── 16. ROCK ENCANTECH — Senior Data Analyst (Power BI, SQL, KPIs, BR company)
EMAILS.append({
"to": "people@rockencantech.com.br",
"subject": "Candidatura: Senior Data Analyst — 15+ Anos | Power BI · DAX · SQL · Governança de KPIs | Disponível Imediatamente",
"html": wrap(header("Senior Data Analyst", "Rock Encantech", "#7C3AED"), f"""
<p>Prezada Equipe de Pessoas da Rock Encantech,</p>
<p>Estou me candidatando para a vaga de <strong>Senior Data Analyst</strong>. Sou Analista de Dados Sênior com <strong>15+ anos de experiência em BI e Analytics empresarial</strong>, {CERTS}. Tenho experiência sólida e comprovada em Power BI, modelagem, DAX e boas práticas de visualização — exatamente o perfil que vocês buscam.</p>
<h4 style="color:#7C3AED;margin:16px 0 8px;">Match com os Requisitos da Vaga:</h4>
<ul style="font-size:13px;line-height:1.9;color:#374151;">
<li><strong>Power BI avançado:</strong> Modelagem, DAX complexo, Power Query, RLS, Dataflows — dashboards de alta performance e confiabilidade</li>
<li><strong>SQL avançado:</strong> Análise, transformação e exploração de dados em ambientes analíticos de larga escala (500M+ registros/mês)</li>
<li><strong>Governança de KPIs:</strong> Definição, evolução e governança de KPIs estratégicos para gestores e C-level em múltiplos setores</li>
<li><strong>Automação de rotinas:</strong> Redução de processamento manual de 4h/dia para menos de 20 minutos com Python e SQL</li>
<li><strong>Storytelling com dados:</strong> 15+ anos traduzindo dados complexos em insights acionáveis para stakeholders de todos os níveis</li>
</ul>
{IMPACT_FULL}
{STACK_FULL}
<p>Disponível para início imediato. Aberto a trabalho remoto ou híbrido. Portfolio disponível sob solicitação.</p>""")
})

# ── 17. CORSEARCH — Senior Data Analyst (Brand Protection, AI)
EMAILS.append({
"to": "careers@corsearch.com",
"subject": "Application: Senior Data Analyst — Brand Protection Analytics | 15+ Years | Available Immediately",
"html": wrap(header("Senior Data Analyst", "Corsearch", "#0369A1"), f"""
<p>Dear Corsearch Talent Team,</p>
<p>I am applying for the <strong>Senior Data Analyst</strong> position producing metrics, visualizations, and data-driven recommendations for Corsearch's AI-powered brand protection platform. I am a Senior Data Analyst with <strong>15+ years of enterprise analytics experience</strong>, available immediately.</p>
<h4 style="color:#0369A1;margin:16px 0 8px;">Analytics for Product Teams:</h4>
<ul style="font-size:13px;line-height:1.9;color:#374151;">
<li><strong>Product analytics:</strong> Built metrics frameworks tracking user behavior, platform performance, and business outcomes for product and executive teams</li>
<li><strong>Visualizations & benchmarks:</strong> Designed comparative analytics dashboards (benchmarks, trend analysis, cohort comparisons) in Power BI, Tableau, and Looker</li>
<li><strong>Data-driven recommendations:</strong> 15+ years delivering analytics that directly influenced strategic decisions at C-level — not just reporting</li>
<li><strong>Cross-functional delivery:</strong> Partnered with Engineering, Product, Customer Success, and Sales to translate data into product improvements</li>
<li><strong>Python + SQL:</strong> Advanced analytics, automated workflows, reducing manual processing from hours to minutes</li>
</ul>
{IMPACT_FULL}
{STACK_FULL}
<p>Available for US/EU remote immediately. Passionate about building analytics that create measurable business impact.</p>""")
})

# ── 18. AIRALO — Senior Data Analyst (eSIM, Growth & Retention)
EMAILS.append({
"to": "people@airalo.com",
"subject": "Application: Senior Data Analyst (Growth & Retention) — 15+ Years | Telecom Analytics | Available Immediately",
"html": wrap(header("Senior Data Analyst — Growth & Retention", "Airalo", "#0EA5E9"), f"""
<p>Dear Airalo People Team,</p>
<p>I am applying for the <strong>Senior Data Analyst</strong> positions — Growth (paid acquisition) and Retention analytics. I am a Senior Data Analyst with <strong>15+ years of enterprise analytics experience</strong>, including deep expertise in both telecom subscriber analytics and paid acquisition performance.</p>
<h4 style="color:#0EA5E9;margin:16px 0 8px;">Why Airalo is a Perfect Match:</h4>
<ul style="font-size:13px;line-height:1.9;color:#374151;">
<li><strong>Telecom analytics:</strong> 15 years at TIM/OI Telecommunications — churn prediction, subscriber growth modeling, ARPU analysis, 500M+ subscriber records/month</li>
<li><strong>Paid acquisition analytics:</strong> Built marketing performance dashboards at Coca-Cola via Google BigQuery — Google Ads, paid acquisition ROI, campaign attribution</li>
<li><strong>Retention analytics:</strong> Lifecycle cohort analysis, retention rate modeling, churn prediction models for 10M+ subscriber base</li>
<li><strong>CRM data:</strong> Integrated Salesforce CRM data into analytics pipelines at Keyrus — lead-to-close, engagement, and retention metrics</li>
<li><strong>Self-service BI:</strong> Built platforms enabling Product and Marketing teams to access data independently — 200+ business users</li>
</ul>
{IMPACT_FULL}
{STACK_FULL}
<p>Available for EU/US remote immediately. Telecom + acquisition analytics is my core expertise — directly aligned with Airalo's eSIM growth model.</p>""")
})

# ── 19. MONIEPOINT — Senior Data Analyst (Fintech Growth, Africa/Global)
EMAILS.append({
"to": "talent@moniepoint.com",
"subject": "Application: Senior Data Analyst — Fintech Growth Analytics | 15+ Years | Payment Products",
"html": wrap(header("Senior Data Analyst — Growth Analytics", "Moniepoint", "#10B981"), f"""
<p>Dear Moniepoint Talent Team,</p>
<p>I am applying for the <strong>Senior Data Analyst</strong> position developing growth strategies for payment products — user acquisition, retention, and cross-functional collaboration. I am a Senior Data Analyst with <strong>15+ years of enterprise analytics experience</strong>, including financial services and payments analytics.</p>
<h4 style="color:#10B981;margin:16px 0 8px;">Fintech Growth Analytics Match:</h4>
<ul style="font-size:13px;line-height:1.9;color:#374151;">
<li><strong>Payment analytics:</strong> Built financial KPI dashboards at Keyrus for banking and Financial Services clients — transaction analytics, revenue, risk metrics</li>
<li><strong>User acquisition & retention:</strong> Acquisition funnel analytics at Coca-Cola (BigQuery, paid campaigns) + churn/retention modeling at TIM/OI Telecom</li>
<li><strong>Cross-functional collaboration:</strong> Partnered with Product, Engineering, Marketing, Finance teams across 15+ years — driving alignment on growth metrics</li>
<li><strong>Scalable analytics platforms:</strong> Built self-service BI for 200+ business users enabling data-driven decisions at all levels</li>
<li><strong>SQL + Python + Power BI:</strong> Full analytics stack from data extraction to visualization — 500M+ records/month processed</li>
</ul>
{IMPACT_FULL}
{STACK_FULL}
<p>Available for fully remote global engagement immediately. Excited about applying enterprise analytics to Moniepoint's mission.</p>""")
})

# ── 20. RESEND (as email infrastructure) — mas usar Keyrus Global para consulting
EMAILS.append({
"to": "talent@keyrus.com",
"subject": "Expression of Interest: Senior Power BI Consultant — Ex-Keyrus Brazil | 15+ Years | EU/US Remote Consulting",
"html": wrap(header("Senior Power BI Consultant — Expression of Interest", "Keyrus", "#1F3864"), f"""
<p>Dear Keyrus Talent Team,</p>
<p>I am a <strong>former Senior Data Analyst at Keyrus Brazil</strong> (2019–2022) reaching out to express interest in <strong>Senior Power BI Consultant</strong> opportunities across Keyrus's global network — particularly EU and US remote engagements.</p>
<h4 style="color:#1F3864;margin:16px 0 8px;">My Keyrus Consulting Track Record:</h4>
<ul style="font-size:13px;line-height:1.9;color:#374151;">
<li><strong>Enterprise self-service platforms:</strong> Built analytics platforms with Dataflows, certified datasets, incremental refresh for Financial Services, Retail, and Insurance clients</li>
<li><strong>Executive KPI scorecards:</strong> C-level dashboards and governance frameworks delivered to Keyrus's largest accounts</li>
<li><strong>70% query optimization:</strong> SQL and analytical model optimization — consistent delivery of performance improvements across client engagements</li>
<li><strong>Azure Synapse integrations:</strong> SAP, Salesforce, REST APIs, Oracle, SQL Server integrated into Synapse environments for enterprise clients</li>
<li><strong>BI governance standards:</strong> Established delivery guidelines and best practices adopted across the Keyrus Brazil practice</li>
</ul>
<p>Since leaving Keyrus Brazil, I have continued delivering enterprise BI at <strong>Dataex</strong> (200+ users, 12+ data sources, 60% performance improvement) and remain highly active in Power BI and cloud analytics.</p>
{IMPACT_FULL}
{STACK_FULL}
<p>Certified: {CERTS}</p>
<p>Would love to explore consulting opportunities within Keyrus's global network. Available for remote deployment to EU/US client engagements immediately.</p>""")
})

# ═══════════════════════════════════════════════════════════════════════════════
def send_email(server, data):
    msg = MIMEMultipart("alternative")
    msg["From"]     = f"Rafael Rodrigues <{GMAIL_USER}>"
    msg["To"]       = data["to"]
    msg["Subject"]  = data["subject"]
    msg["Reply-To"] = REPLY_TO
    msg.attach(MIMEText(data["html"], "html"))
    server.sendmail(GMAIL_USER, [data["to"]], msg.as_string())

def main():
    print(f"=== JOB APPLICATION SENDER v2 ===")
    print(f"Empresas: {len(EMAILS)}")
    print(f"Remetente: {GMAIL_USER}\n")

    server = smtplib.SMTP("smtp.gmail.com", 587)
    server.ehlo(); server.starttls()
    server.login(GMAIL_USER, APP_PASS)
    print("✅ Gmail autenticado!\n")

    results = []
    for i, e in enumerate(EMAILS, 1):
        to_short = e["to"].split("@")[1]
        print(f"[{i:2}/{len(EMAILS)}] {e['to'][:50]:<52}", end=" ", flush=True)
        try:
            send_email(server, e)
            print("✅")
            results.append(("✅", e["to"], e["subject"][:60]))
        except Exception as err:
            print(f"❌ {str(err)[:40]}")
            results.append(("❌", e["to"], str(err)[:40]))
        time.sleep(3)

    server.quit()
    print(f"\n{'='*60}")
    sent = sum(1 for r in results if r[0]=="✅")
    print(f"RESULTADO: {sent}/{len(EMAILS)} emails enviados")
    print(f"{'='*60}")

if __name__ == "__main__":
    main()
