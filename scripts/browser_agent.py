#!/usr/bin/env python3
# browser_agent.py - Agente web Playwright (GRATIS via GitHub Actions)
# Drena a fila browser_tasks (Supabase) e executa acoes reais: navegar, digitar, clicar, extrair, screenshot.
import os, sys, json, subprocess, traceback
from datetime import datetime, timezone

SB = os.getenv("SUPABASE_URL", "https://tpjvalzwkqwttvmszvie.supabase.co")
SK = os.getenv("SUPABASE_KEY", "") or os.getenv("SUPABASE_SERVICE_KEY", "")

def _ensure():
    try:
        import requests, playwright  # noqa: F401
    except ImportError:
        subprocess.run([sys.executable, "-m", "pip", "install", "--quiet", "requests", "playwright"], check=False)

_ensure()
import requests
from playwright.sync_api import sync_playwright

H = {"apikey": SK, "Authorization": "Bearer " + SK, "Content-Type": "application/json"}

def fetch_pending(limit=3):
    r = requests.get(SB + "/rest/v1/browser_tasks",
        headers=H,
        params={"status": "eq.pending", "order": "priority.desc,created_at.asc", "limit": str(limit), "select": "*"},
        timeout=20)
    return r.json() if r.ok else []

def patch(task_id, body):
    requests.patch(SB + "/rest/v1/browser_tasks?id=eq." + str(task_id),
        headers={**H, "Prefer": "return=minimal"}, data=json.dumps(body), timeout=20)

def upload_shot(png_bytes, name):
    fname = "browser/" + name
    r = requests.post(SB + "/storage/v1/object/videos/" + fname,
        headers={"apikey": SK, "Authorization": "Bearer " + SK, "Content-Type": "image/png", "x-upsert": "true"},
        data=png_bytes, timeout=60)
    return (SB + "/storage/v1/object/public/videos/" + fname) if r.status_code in (200, 201) else None

def run_task(page, task):
    logs = []; extracted = {}; shots = []
    for i, step in enumerate(task.get("steps") or []):
        act = step.get("action")
        try:
            if act == "goto":
                page.goto(step["url"], wait_until="domcontentloaded", timeout=30000); logs.append("goto " + step["url"])
            elif act in ("type", "fill"):
                sel = step["selector"]; page.wait_for_selector(sel, timeout=15000)
                if act == "fill": page.fill(sel, step.get("text", ""))
                else: page.type(sel, step.get("text", ""), delay=step.get("delay", 40))
                logs.append(act + " " + sel)
            elif act == "click":
                sel = step["selector"]; page.wait_for_selector(sel, timeout=15000); page.click(sel); logs.append("click " + sel)
            elif act == "press":
                page.keyboard.press(step.get("key", "Enter")); logs.append("press " + step.get("key", "Enter"))
            elif act == "wait":
                page.wait_for_timeout(int(step.get("ms", 1000))); logs.append("wait " + str(step.get("ms", 1000)))
            elif act == "wait_for":
                page.wait_for_selector(step["selector"], timeout=int(step.get("timeout", 15000))); logs.append("wait_for " + step["selector"])
            elif act == "scroll":
                page.mouse.wheel(0, int(step.get("y", 1200))); page.wait_for_timeout(500); logs.append("scroll")
            elif act == "extract":
                el = page.query_selector(step["selector"])
                val = None
                if el: val = el.get_attribute(step["attr"]) if step.get("attr") else el.inner_text()
                extracted[step.get("name", "value")] = (val.strip() if val else None)
                logs.append("extract " + step.get("name", "value"))
            elif act == "extract_all":
                els = page.query_selector_all(step["selector"]); lim = int(step.get("limit", 20)); out = []
                for e in els[:lim]:
                    v = e.get_attribute(step["attr"]) if step.get("attr") else e.inner_text()
                    if v: out.append(v.strip())
                extracted[step.get("name", "items")] = out; logs.append("extract_all " + step.get("name", "items") + " (" + str(len(out)) + ")")
            elif act == "screenshot":
                png = page.screenshot(full_page=bool(step.get("full_page", False)))
                url = upload_shot(png, "t" + str(task["id"]) + "_" + str(i) + ".png")
                if url: shots.append(url)
                logs.append("screenshot " + (url or "fail"))
            else:
                logs.append("ACAO DESCONHECIDA: " + str(act))
        except Exception as e:
            logs.append("ERRO step " + str(i) + " (" + str(act) + "): " + str(e)[:160])
    try:
        extracted["_final_url"] = page.url; extracted["_title"] = page.title()
    except Exception:
        pass
    return {"extracted": extracted, "screenshots": shots}, "\n".join(logs)

def main():
    if not SK:
        print("SEM SUPABASE_KEY"); return
    tasks = fetch_pending()
    if not tasks:
        print("Fila vazia."); return
    print("Tarefas pendentes: " + str(len(tasks)))
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True, args=["--no-sandbox", "--disable-dev-shm-usage"])
        for task in tasks:
            tid = task["id"]
            patch(tid, {"status": "running", "started_at": datetime.now(timezone.utc).isoformat(), "attempts": task.get("attempts", 0) + 1})
            print("== Tarefa " + str(tid) + ": " + str(task.get("goal"))[:60])
            ctx = browser.new_context(
                user_agent="Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124 Safari/537.36",
                viewport={"width": 1280, "height": 900})
            page = ctx.new_page()
            try:
                result, logs = run_task(page, task)
                patch(tid, {"status": "done", "result": result, "logs": logs[:8000], "finished_at": datetime.now(timezone.utc).isoformat()})
                print("  done")
            except Exception as e:
                patch(tid, {"status": "error", "logs": traceback.format_exc()[:8000], "finished_at": datetime.now(timezone.utc).isoformat()})
                print("  erro: " + str(e)[:120])
            finally:
                ctx.close()
        browser.close()
    print("Fim.")

if __name__ == "__main__":
    main()
