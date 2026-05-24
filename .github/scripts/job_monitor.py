#!/usr/bin/env python3
"""
Daily Job Monitor — Rafael Rodrigues
Roda diariamente, encontra novas vagas, envia digest por email
"""
import smtplib, json, os, datetime, time, urllib.request
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

GMAIL_USER = "tafita81@gmail.com"
REPLY_TO   = "Rafa_roberto2004@yahoo.com.br"
APP_PASS   = os.environ["GMAIL_APP_PASSWORD"]
SEEN_FILE  = ".github/scripts/seen_jobs.json"

SEARCHES = [
    "https://remotive.com/api/remote-jobs?category=data&search=power+bi&limit=20",
    "https://remotive.com/api/remote-jobs?category=data&search=data+analyst+senior&limit=20",
    "https://remotive.com/api/remote-jobs?category=data&search=business+intelligence&limit=20",
]

# Indeed RSS feeds (vagas EUA)
INDEED_SEARCHES = [
    ("Senior Power BI Developer", "remote"),
    ("Senior Data Analyst Power BI", "remote"),
    ("Analytics Engineer Power BI", "remote"),
]

def load_seen():
    try:
        with open(SEEN_FILE) as f:
            return set(json.load(f))
    except:
        return set()

def save_seen(seen):
    os.makedirs(os.path.dirname(SEEN_FILE), exist_ok=True)
    with open(SEEN_FILE, "w") as f:
        json.dump(list(seen), f)

def fetch_remotive():
    jobs = []
    for url in SEARCHES:
        try:
            req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
            with urllib.request.urlopen(req, timeout=15) as r:
                data = json.loads(r.read())
                jobs.extend(data.get("jobs", []))
        except Exception as e:
            print(f"Remotive err: {e}")
    seen_ids = set(str(j["id"]) for j in jobs)
    unique = {str(j["id"]): j for j in jobs}
    return list(unique.values())

def build_digest_html(new_jobs, date_str):
    if not new_jobs:
        return None
    rows = ""
    for j in new_jobs:
        sal = j.get("salary") or "N/A"
        tags = ", ".join(j.get("tags", [])[:5])
        rows += f"""
<tr style="border-bottom:1px solid #E5E7EB;">
  <td style="padding:12px 8px;">
    <div style="font-weight:700;color:#1F3864;font-size:13px;">{j["title"]}</div>
    <div style="color:#5B21B6;font-size:12px;">{j["company_name"]}</div>
    <div style="color:#6B7280;font-size:11px;margin-top:4px;">{tags}</div>
  </td>
  <td style="padding:12px 8px;color:#059669;font-size:12px;white-space:nowrap;">{sal[:25]}</td>
  <td style="padding:12px 8px;">
    <a href="{j["url"]}" style="background:#1F3864;color:#fff;padding:6px 12px;border-radius:6px;font-size:11px;font-weight:700;text-decoration:none;">Aplicar</a>
  </td>
</tr>"""

    return f"""<html><body style="font-family:Arial,sans-serif;max-width:700px;margin:0 auto;color:#1F2937;">
<div style="background:linear-gradient(135deg,#1F3864,#5B21B6);padding:20px 24px;border-radius:8px 8px 0 0;">
  <div style="color:#C4B5FD;font-size:11px;letter-spacing:2px;text-transform:uppercase;">{date_str}</div>
  <div style="color:#fff;font-size:22px;font-weight:800;margin-top:4px;">
    🔍 {len(new_jobs)} Nova{"s" if len(new_jobs)>1 else ""} Vaga{"s" if len(new_jobs)>1 else ""} Encontrada{"s" if len(new_jobs)>1 else ""}
  </div>
  <div style="color:#C4B5FD;font-size:13px;">Rafael Rodrigues · Job Monitor Diário</div>
</div>
<div style="background:#fff;padding:20px;border:1px solid #E5E7EB;border-top:none;border-radius:0 0 8px 8px;">
  <table style="width:100%;border-collapse:collapse;">
    <thead>
      <tr style="background:#F8FAFC;border-bottom:2px solid #E5E7EB;">
        <th style="padding:10px 8px;text-align:left;font-size:11px;color:#6B7280;text-transform:uppercase;">Vaga / Empresa</th>
        <th style="padding:10px 8px;text-align:left;font-size:11px;color:#6B7280;text-transform:uppercase;">Salário</th>
        <th style="padding:10px 8px;text-align:left;font-size:11px;color:#6B7280;text-transform:uppercase;">Ação</th>
      </tr>
    </thead>
    <tbody>{rows}</tbody>
  </table>
  <div style="margin-top:20px;padding:16px;background:#F0FDF4;border-radius:8px;border:1px solid #BBF7D0;">
    <div style="font-size:12px;color:#065F46;">
      ✅ Monitor rodou às {date_str} · Próxima verificação: amanhã às 9h (Brasília)
    </div>
  </div>
</div>
</body></html>"""

def main():
    today = datetime.date.today().strftime("%d/%m/%Y")
    print(f"=== Job Monitor — {today} ===")

    seen = load_seen()
    all_jobs = fetch_remotive()
    print(f"Total vagas encontradas: {len(all_jobs)}")

    new_jobs = [j for j in all_jobs if str(j["id"]) not in seen]
    print(f"Novas vagas: {len(new_jobs)}")

    # Atualizar seen
    for j in all_jobs:
        seen.add(str(j["id"]))
    save_seen(seen)

    if not new_jobs:
        print("Nenhuma vaga nova hoje.")
        return

    html = build_digest_html(new_jobs, today)
    if not html:
        return

    print("Enviando digest...")
    msg = MIMEMultipart("alternative")
    msg["From"]     = f"Job Monitor <{GMAIL_USER}>"
    msg["To"]       = GMAIL_USER
    msg["Reply-To"] = REPLY_TO
    msg["Subject"]  = f"🔍 {len(new_jobs)} Nova{'s' if len(new_jobs)>1 else ''} Vaga{'s' if len(new_jobs)>1 else ''} — {today}"
    msg.attach(MIMEText(html, "html"))

    s = smtplib.SMTP("smtp.gmail.com", 587)
    s.ehlo(); s.starttls()
    s.login(GMAIL_USER, APP_PASS)
    s.sendmail(GMAIL_USER, [GMAIL_USER], msg.as_string())
    s.quit()
    print(f"Digest enviado: {len(new_jobs)} vagas!")

if __name__ == "__main__":
    main()
