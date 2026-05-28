#!/usr/bin/env python3
"""
SESSION MANAGER v1
Salva e reutiliza cookies de sessão de qualquer plataforma.
Login usa stealth máximo para evitar detecção de bot.
"""
import os, json, time, datetime, urllib.request, urllib.parse

SUPA = os.environ.get("SUPABASE_URL","https://tpjvalzwkqwttvmszvie.supabase.co")
KEY  = os.environ.get("SUPABASE_ANON_KEY","")
EMAIL    = os.environ.get("DICE_EMAIL","tafita81@gmail.com")
PASSWORD = os.environ.get("DICE_PASSWORD","Daniela1982@")

def sb_get(path):
    req = urllib.request.Request(f"{SUPA}/rest/v1/{path}",
        headers={"apikey":KEY,"Authorization":f"Bearer {KEY}"})
    try:
        with urllib.request.urlopen(req, timeout=8) as r: return json.loads(r.read())
    except: return []

def sb_upsert(table, data):
    req = urllib.request.Request(f"{SUPA}/rest/v1/{table}",
        data=json.dumps(data).encode(), method="POST",
        headers={"apikey":KEY,"Authorization":f"Bearer {KEY}",
                 "Content-Type":"application/json","Prefer":"resolution=merge-duplicates"})
    try:
        with urllib.request.urlopen(req, timeout=8) as r: return r.status
    except: return 0

def save_session(platform, cookies_json, extra=None):
    expires = (datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(days=25)).isoformat()
    sb_upsert("ia_cache", {
        "cache_key": f"session:{platform}",
        "value": json.dumps({"cookies": cookies_json, "extra": extra or {}, "email": EMAIL}),
        "expires_at": expires
    })

def load_session(platform):
    rows = sb_get(f"ia_cache?cache_key=eq.session%3A{platform}&select=value,expires_at&limit=1")
    if not rows: return None
    row = rows[0]
    exp = row.get("expires_at","")
    if exp and exp < datetime.datetime.now(datetime.timezone.utc).isoformat():
        return None  # expirado
    try: return json.loads(row["value"])
    except: return None

def stealth_context(p):
    """Cria browser context com stealth máximo"""
    br = p.chromium.launch(
        headless=True,
        args=[
            "--no-sandbox","--disable-dev-shm-usage","--disable-gpu",
            "--disable-blink-features=AutomationControlled",
            "--disable-features=IsolateOrigins,site-per-process",
            "--disable-web-security","--lang=en-US",
        ]
    )
    ctx = br.new_context(
        user_agent="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
        viewport={"width":1366,"height":768},
        locale="en-US", timezone_id="America/New_York",
        geolocation={"latitude":40.7128,"longitude":-74.0060},
        permissions=["geolocation"],
        extra_http_headers={"Accept-Language":"en-US,en;q=0.9"}
    )
    ctx.add_init_script("""
        Object.defineProperty(navigator,'webdriver',{get:()=>undefined});
        Object.defineProperty(navigator,'plugins',{get:()=>[1,2,3,4,5]});
        Object.defineProperty(navigator,'languages',{get:()=>['en-US','en']});
        window.chrome={runtime:{}};
        const orig=document.createElement.bind(document);
        document.createElement=function(tag){const el=orig(tag);if(tag==='canvas'){const ctx=el.getContext('2d');if(ctx){const orig2=ctx.getImageData.bind(ctx);ctx.getImageData=function(x,y,w,h){const d=orig2(x,y,w,h);for(let i=0;i<d.data.length;i+=4)d.data[i]+=Math.floor(Math.random()*2);return d;}}}return el;};
    """)
    return br, ctx

def human_type(page, selector, text, delay_range=(80,180)):
    import random
    el = page.locator(selector).first
    el.click()
    time.sleep(0.3)
    for ch in text:
        el.press(ch)
        time.sleep(random.uniform(delay_range[0], delay_range[1]) / 1000)

def try_login_dice(ctx):
    pg = ctx.new_page()
    try:
        pg.goto("https://www.dice.com/dashboard/login", timeout=20000)
        pg.wait_for_load_state("domcontentloaded", timeout=10000)
        time.sleep(2)
        for sel in ["#email","input[name='email']","input[type='email']"]:
            try:
                el = pg.locator(sel).first
                if el.is_visible(timeout=2000):
                    human_type(pg, sel, EMAIL)
                    break
            except: pass
        time.sleep(0.8)
        for sel in ["button[type='submit']","button:has-text('Sign In')","button:has-text('Continue')"]:
            try:
                el = pg.locator(sel).first
                if el.is_visible(timeout=800): el.click(); break
            except: pass
        time.sleep(3)
        for sel in ["#password","input[type='password']","input[name='password']"]:
            try:
                el = pg.locator(sel).first
                if el.is_visible(timeout=4000):
                    human_type(pg, sel, PASSWORD)
                    break
            except: pass
        time.sleep(0.8)
        for sel in ["button[type='submit']","button:has-text('Sign In')"]:
            try:
                el = pg.locator(sel).first
                if el.is_visible(timeout=800): el.click(); break
            except: pass
        time.sleep(5)
        url = pg.url
        if any(x in url for x in ["dashboard/jobs","dashboard/profile","/home","/search"]) and "login" not in url:
            cookies = ctx.cookies()
            pg.close()
            return cookies
        pg.close()
        return None
    except Exception as e:
        try: pg.close()
        except: pass
        return None

def try_login_indeed(ctx):
    pg = ctx.new_page()
    try:
        pg.goto("https://secure.indeed.com/auth?hl=en_US&co=US&continue=%2F", timeout=20000)
        pg.wait_for_load_state("domcontentloaded", timeout=10000)
        time.sleep(2)
        for sel in ["#ifl-InputFormField-3","input[name='__email']","input[type='email']","#emailOrUsername"]:
            try:
                el = pg.locator(sel).first
                if el.is_visible(timeout=2000):
                    human_type(pg, sel, EMAIL)
                    break
            except: pass
        time.sleep(0.6)
        for sel in ["button[type='submit']","#login-submit-button","button:has-text('Continue')"]:
            try:
                el = pg.locator(sel).first
                if el.is_visible(timeout=800): el.click(); break
            except: pass
        time.sleep(3)
        for sel in ["input[type='password']","#ifl-InputFormField-7"]:
            try:
                el = pg.locator(sel).first
                if el.is_visible(timeout=4000):
                    human_type(pg, sel, PASSWORD)
                    break
            except: pass
        time.sleep(0.6)
        for sel in ["button[type='submit']","#login-submit-button"]:
            try:
                el = pg.locator(sel).first
                if el.is_visible(timeout=800): el.click(); break
            except: pass
        time.sleep(5)
        if "indeed.com" in pg.url and "auth" not in pg.url and "login" not in pg.url:
            cookies = ctx.cookies()
            pg.close()
            return cookies
        pg.close()
        return None
    except Exception as e:
        try: pg.close()
        except: pass
        return None

def try_login_wellfound(ctx):
    pg = ctx.new_page()
    try:
        pg.goto("https://wellfound.com/login", timeout=20000)
        pg.wait_for_load_state("domcontentloaded", timeout=10000)
        time.sleep(2)
        for sel in ["input[name='user[email]']","input[type='email']","#user_email"]:
            try:
                el = pg.locator(sel).first
                if el.is_visible(timeout=2000):
                    human_type(pg, sel, EMAIL)
                    break
            except: pass
        time.sleep(0.5)
        for sel in ["input[type='password']","input[name='user[password]']"]:
            try:
                el = pg.locator(sel).first
                if el.is_visible(timeout=2000):
                    human_type(pg, sel, PASSWORD)
                    break
            except: pass
        time.sleep(0.5)
        for sel in ["input[type='submit']","button[type='submit']","button:has-text('Sign in')"]:
            try:
                el = pg.locator(sel).first
                if el.is_visible(timeout=800): el.click(); break
            except: pass
        time.sleep(5)
        if "wellfound.com" in pg.url and "login" not in pg.url:
            cookies = ctx.cookies()
            pg.close()
            return cookies
        pg.close()
        return None
    except Exception as e:
        try: pg.close()
        except: pass
        return None

def try_login_linkedin(ctx):
    pg = ctx.new_page()
    try:
        pg.goto("https://www.linkedin.com/login", timeout=20000)
        pg.wait_for_load_state("domcontentloaded", timeout=10000)
        time.sleep(2)
        for sel in ["#username","input[name='session_key']","input[type='email']"]:
            try:
                el = pg.locator(sel).first
                if el.is_visible(timeout=2000):
                    human_type(pg, sel, EMAIL)
                    break
            except: pass
        for sel in ["#password","input[name='session_password']","input[type='password']"]:
            try:
                el = pg.locator(sel).first
                if el.is_visible(timeout=2000):
                    human_type(pg, sel, PASSWORD)
                    break
            except: pass
        time.sleep(0.5)
        for sel in ["button[type='submit']","button:has-text('Sign in')"]:
            try:
                el = pg.locator(sel).first
                if el.is_visible(timeout=800): el.click(); break
            except: pass
        time.sleep(6)
        # LinkedIn muitas vezes pede verificação — salvar cookies mesmo assim
        cookies = ctx.cookies()
        li_cookies = [c for c in cookies if "li_at" in c.get("name","") or "JSESSIONID" in c.get("name","")]
        pg.close()
        if li_cookies:
            return cookies
        return None
    except Exception as e:
        try: pg.close()
        except: pass
        return None

if __name__ == "__main__":
    from playwright.sync_api import sync_playwright
    print("SESSION MANAGER — testando logins\n")
    with sync_playwright() as p:
        br, ctx = stealth_context(p)
        for name, fn in [("dice", try_login_dice), ("indeed", try_login_indeed),
                         ("wellfound", try_login_wellfound), ("linkedin", try_login_linkedin)]:
            print(f"  {name}...", end=" ", flush=True)
            sess = load_session(name)
            if sess:
                print(f"✅ sessão em cache")
                continue
            cookies = fn(ctx)
            if cookies:
                save_session(name, cookies)
                print(f"✅ {len(cookies)} cookies salvos")
            else:
                print(f"⚠️  login falhou")
        br.close()
