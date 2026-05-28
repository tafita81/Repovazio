#!/usr/bin/env python3
"""
YOUTUBE JOB SCRAPER
━━━━━━━━━━━━━━━━━━
Acessa canal YouTube, lê descrição de cada vídeo,
extrai vagas anunciadas e candidata Rafael automaticamente.

Canal: https://youtube.com/@NidhiNagori29
Método: Playwright (sem login necessário — conteúdo público)
"""
import os, re, json, time, datetime, hashlib, urllib.request, urllib.parse
from playwright.sync_api import sync_playwright

CHANNEL_URL = "https://www.youtube.com/@NidhiNagori29/videos"
CHANNEL_ID  = "UCbxAT78lGaDJTaO1JkcVs_g"
SUPA  = os.environ.get("SUPABASE_URL", "https://tpjvalzwkqwttvmszvie.supabase.co")
KEY   = os.environ.get("SUPABASE_ANON_KEY", "")
AKEY  = os.environ.get("ANTHROPIC_API_KEY", "")

# Padrões para detectar vagas em descrições de vídeo
JOB_PATTERNS = [
    r"apply\s+(?:here|now|at|link)[\s:]+?(https?://\S+)",
    r"job\s+link[\s:]+?(https?://\S+)",
    r"application\s+link[\s:]+?(https?://\S+)",
    r"apply[\s:]+?(https?://\S+)",
    r"careers?[\s.@:]+?(https?://\S+)",
    r"hiring[\s:]+?(https?://\S+)",
    r"(https?://(?:boards\.greenhouse\.io|jobs\.lever\.co|grnh\.se|app\.greenhouse\.io|jobs\.ashbyhq\.com|workable\.com|smartrecruiters\.com|jobs\.workday\.com|jobvite\.com|careers\.\S+)/\S+)",
    r"(https?://\S+(?:greenhouse|lever|workday|ashby|smartrecruit|jobvite|icims|taleo|brassring)\S+)",
]

COMPANY_PATTERNS = [
    r"(?:company|employer|hiring company)[\s:]+([A-Z][A-Za-z\s&,\.]{2,40})",
    r"([A-Z][A-Za-z\s&]{2,30})\s+is\s+hiring",
    r"([A-Z][A-Za-z\s&]{2,30})\s+jobs?\s+openings?",
    r"join\s+([A-Z][A-Za-z\s&]{2,30})\s+as",
]

ROLE_PATTERNS = [
    r"(?:role|position|job title|opening)[\s:]+([A-Za-z\s\-\/]{5,60})",
    r"hiring\s+(?:a\s+)?([A-Za-z\s\-\/]{5,50})\s+(?:at|for|in)",
    r"([Ss]enior\s+[A-Za-z\s\-]{5,50})\s+(?:role|position|opening)",
    r"([A-Za-z\s\-\/]{5,50})\s+job\s+opening",
]

def sb_get(path):
    req = urllib.request.Request(f"{SUPA}/rest/v1/{path}",
        headers={"apikey": KEY, "Authorization": f"Bearer {KEY}"})
    try:
        with urllib.request.urlopen(req, timeout=6) as r:
            return json.loads(r.read())
    except: return []

def sb_post(data):
    req = urllib.request.Request(f"{SUPA}/rest/v1/job_applications",
        data=json.dumps(data).encode(), method="POST",
        headers={"apikey": KEY, "Authorization": f"Bearer {KEY}",
                 "Content-Type": "application/json", "Prefer": "return=minimal"})
    try:
        with urllib.request.urlopen(req, timeout=8) as r: return r.status
    except: return 0

def already_saved(jid):
    r = sb_get(f"job_applications?job_id=eq.{urllib.parse.quote(str(jid))}&select=id&limit=1")
    return len(r) > 0

def extract_jobs_from_description(desc, video_title, video_url):
    """Extrai vagas de uma descrição de vídeo"""
    jobs = []
    desc_lower = desc.lower()

    # Extrair URLs de candidatura
    apply_urls = []
    for pat in JOB_PATTERNS:
        found = re.findall(pat, desc, re.IGNORECASE)
        apply_urls.extend(found)
    apply_urls = list(set([u.rstrip(".,);\n") for u in apply_urls if len(u) > 20]))

    # Extrair empresa
    company = "?"
    for pat in COMPANY_PATTERNS:
        m = re.search(pat, desc)
        if m: company = m.group(1).strip(); break
    if company == "?":
        # Tentar extrair do título
        m = re.search(r"at\s+([A-Z][A-Za-z\s&]{2,30})\s*[\|\-]", video_title)
        if m: company = m.group(1).strip()

    # Extrair cargo
    role = video_title
    for pat in ROLE_PATTERNS:
        m = re.search(pat, desc)
        if m: role = m.group(1).strip(); break

    # Verificar se é relevante para Rafael
    relevant_kws = ["data analyst","power bi","business intelligence","analytics engineer",
                    "bi developer","tableau","looker","reporting","sql","data engineer",
                    "senior analyst","bi analyst","analytics","data science","snowflake",
                    "azure","bigquery","databricks","dbt"]
    is_relevant = any(k in desc_lower or k in video_title.lower() for k in relevant_kws)

    if not is_relevant:
        return []

    # Criar entrada para cada URL encontrada
    if apply_urls:
        for url in apply_urls[:3]:
            jid = f"yt_{hashlib.md5((url+video_url).encode()).hexdigest()[:12]}"
            if not already_saved(jid):
                # Detectar tipo de ATS
                method = "greenhouse_form"
                if "lever.co" in url: method = "lever_form"
                elif "workday" in url: method = "workday_form"
                elif "smartrecruit" in url: method = "smartrecruiters"
                elif "ashby" in url: method = "ashby_form"
                elif "linkedin" in url: method = "linkedin_apply"

                jobs.append({
                    "id": jid, "company": company, "role": role[:80],
                    "url": url, "source_video": video_url,
                    "method": method, "desc": desc[:1500],
                    "platform": "YouTube/NidhiNagori"
                })
    else:
        # Sem URL de candidatura explícita — registrar como descoberta com URL do vídeo
        jid = f"yt_{hashlib.md5(video_url.encode()).hexdigest()[:12]}"
        if not already_saved(jid):
            jobs.append({
                "id": jid, "company": company, "role": role[:80],
                "url": video_url, "source_video": video_url,
                "method": "manual_review", "desc": desc[:1500],
                "platform": "YouTube/NidhiNagori"
            })

    return jobs

def get_video_description(page, video_url):
    """Abre um vídeo YouTube e extrai a descrição completa"""
    try:
        page.goto(video_url, timeout=25000)
        page.wait_for_load_state("domcontentloaded", timeout=15000)
        time.sleep(3)

        # Expandir descrição (clicar em "...more" / "Show more")
        for sel in [
            "tp-yt-paper-button#expand",
            "button[aria-label='Show more']",
            "#expand",
            "yt-formatted-string.more-button",
            "[aria-label*='more']",
        ]:
            try:
                el = page.locator(sel).first
                if el.is_visible(timeout=2000): el.click(); time.sleep(1); break
            except: pass

        # Extrair texto da descrição
        desc = ""
        for sel in [
            "#description-inner",
            "#description yt-formatted-string",
            "#description",
            "ytd-text-inline-expander",
            "#snippet-text",
        ]:
            try:
                el = page.locator(sel).first
                if el.is_visible(timeout=2000):
                    desc = el.inner_text()
                    if len(desc) > 50: break
            except: pass

        # Extrair título
        title = ""
        try:
            title = page.locator("h1.ytd-video-primary-info-renderer, h1 yt-formatted-string").first.inner_text()
        except:
            try: title = page.title().replace(" - YouTube", "")
            except: pass

        return title.strip(), desc.strip()
    except Exception as e:
        return "", ""

def scrape_channel_videos(ctx, max_videos=50):
    """Scrapes the channel and collects video URLs"""
    print(f"  Abrindo canal: {CHANNEL_URL}")
    page = ctx.new_page()
    video_urls = []

    try:
        page.goto(CHANNEL_URL, timeout=25000)
        page.wait_for_load_state("domcontentloaded", timeout=15000)
        time.sleep(4)

        # Scroll para carregar mais vídeos
        for _ in range(5):
            page.keyboard.press("End")
            time.sleep(2)

        # Extrair URLs de vídeos
        links = page.locator("a#video-title-link, a.ytd-grid-video-renderer, a[href*='/watch?v=']").all()
        for link in links:
            try:
                href = link.get_attribute("href")
                if href and "/watch?v=" in href:
                    full_url = f"https://www.youtube.com{href}" if href.startswith("/") else href
                    if full_url not in video_urls:
                        video_urls.append(full_url)
            except: pass

        # Também buscar via conteúdo da página
        content = page.content()
        found_ids = re.findall(r'watch\?v=([a-zA-Z0-9_\-]{11})', content)
        for vid_id in found_ids:
            url = f"https://www.youtube.com/watch?v={vid_id}"
            if url not in video_urls:
                video_urls.append(url)

        print(f"  {len(video_urls)} vídeos encontrados no canal")
    except Exception as e:
        print(f"  Erro ao acessar canal: {str(e)[:50]}")
    finally:
        page.close()

    return list(dict.fromkeys(video_urls))[:max_videos]

def main():
    today = datetime.date.today().strftime("%d/%m/%Y")
    print(f"\n{'━'*60}")
    print(f"  🎥 YOUTUBE JOB SCRAPER — {today}")
    print(f"  Canal: @NidhiNagori29 (Canada/Europe/Remote jobs)")
    print(f"{'━'*60}\n")

    all_jobs = []
    videos_processed = 0

    with sync_playwright() as p:
        browser = p.chromium.launch(
            headless=True,
            args=["--no-sandbox", "--disable-dev-shm-usage", "--disable-gpu",
                  "--disable-blink-features=AutomationControlled",
                  "--lang=en-US,en"]
        )
        ctx = browser.new_context(
            user_agent="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            viewport={"width": 1920, "height": 1080},
            locale="en-US"
        )
        ctx.add_init_script("Object.defineProperty(navigator,'webdriver',{get:()=>undefined})")

        # 1. Coletar URLs do canal
        video_urls = scrape_channel_videos(ctx, max_videos=50)

        if not video_urls:
            print("  ⚠️  Sem vídeos encontrados — YouTube bloqueou acesso headless")
            print("  → Usando lista de vídeos recentes via RSS fallback")

            # Fallback: buscar via invidious (mirror público)
            try:
                inv_url = f"https://invidious.snopyta.org/api/v1/channels/{CHANNEL_ID}/videos?page=1"
                req = urllib.request.Request(inv_url, headers={"User-Agent": "Mozilla/5.0"})
                with urllib.request.urlopen(req, timeout=10) as r:
                    data = json.loads(r.read())
                for v in data.get("videos", [])[:30]:
                    vid_id = v.get("videoId","")
                    if vid_id: video_urls.append(f"https://www.youtube.com/watch?v={vid_id}")
                print(f"  Invidious: {len(video_urls)} vídeos")
            except:
                # Fallback 2: buscar IDs via search
                try:
                    search_url = f"https://www.youtube.com/@NidhiNagori29/videos"
                    req2 = urllib.request.Request(search_url, headers={"User-Agent":"Mozilla/5.0"})
                    with urllib.request.urlopen(req2, timeout=10) as r:
                        html = r.read().decode("utf-8","ignore")
                    ids = list(dict.fromkeys(re.findall(r'"videoId":"([a-zA-Z0-9_\-]{11})"', html)))[:30]
                    video_urls = [f"https://www.youtube.com/watch?v={i}" for i in ids]
                    print(f"  HTML parse: {len(video_urls)} vídeos")
                except:
                    print("  Todos os fallbacks falharam")

        # 2. Processar cada vídeo
        print(f"\n  Processando {len(video_urls)} vídeos...\n")
        vid_page = ctx.new_page()

        for i, vid_url in enumerate(video_urls, 1):
            print(f"  [{i:2}/{len(video_urls)}] {vid_url[-30:]}", end=" ", flush=True)

            title, desc = get_video_description(vid_page, vid_url)

            if not desc:
                print("→ sem descrição")
                continue

            jobs = extract_jobs_from_description(desc, title, vid_url)
            videos_processed += 1

            if jobs:
                print(f"→ {len(jobs)} vaga(s): {', '.join(j['company'] for j in jobs)}")
                all_jobs.extend(jobs)
            else:
                # Verificar se é relevante
                relevant_kws = ["data","analytics","power bi","sql","bi ","analyst","engineer","remote","canada","finance"]
                is_rel = any(k in (title+desc).lower() for k in relevant_kws)
                print(f"→ {'relevante (sem link)' if is_rel else 'não relevante'}")

            time.sleep(1.5)

        vid_page.close()
        browser.close()

    # 3. Salvar vagas encontradas
    now = datetime.datetime.now(datetime.timezone.utc).isoformat()
    saved = 0
    for job in all_jobs:
        result = sb_post({
            "company": job["company"], "role": job["role"],
            "url": job["url"], "job_id": job["id"],
            "application_method": job["method"],
            "status": "discovered" if job["method"] == "manual_review" else "pending_apply",
            "platform": job["platform"],
            "applied_at": now, "email": "Rafa_roberto2004@yahoo.com.br",
            "notes": f"Source: {job['source_video']}\n{job['desc'][:300]}",
            "country": "Global"
        })
        if result in [200, 201]: saved += 1

    print(f"\n{'━'*60}")
    print(f"  📺 {videos_processed} vídeos processados")
    print(f"  💼 {len(all_jobs)} vagas extraídas das descrições")
    print(f"  ✅ {saved} novas vagas salvas no banco")
    print(f"  🌍 {today}")
    print(f"{'━'*60}\n")

if __name__ == "__main__":
    main()
