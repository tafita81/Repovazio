#!/usr/bin/env python3
import os, requests, time

TOKEN = os.getenv("SUPABASE_ACCESS_TOKEN","")
PROJ  = "tpjvalzwkqwttvmszvie"
BASE  = f"https://api.supabase.com/v1/projects/{PROJ}/functions"
H     = {"Authorization": f"Bearer {TOKEN}"}

KEEP = {
    "gh-commit","daniela-chat","daniela-app","daniela-admin",
    "app-runtime","connectors-api","youtube-api","cerebro-autonomo",
    "video-generator","cases-researcher","youtube-publisher",
    "render-trigger","intelligence-engine","analytics-collector",
    "social-publisher","github-secrets-setup-all","audit-youtube",
    "videos-page-publisher","piloto-prepare","cases-bootstrap",
    "github-run-logs","github-workflow-status","mp4-upload",
    "github-job-log","assemble-v10","v11-assemble-commit",
    "v12-assemble-commit","v12-all-inserter",
}

ORPHANS = [
    "commit-learn","commit-skills","commit-chat","commit-route",
    "commit-from-chunks","commit-route-final","commit-from-cache",
    "commit-chatia","store-v6-p1","commit-v8-route","commit-executor-v7",
    "commit-ia-v6","test-b64-len","commit-ia-executor","exec-sql",
    "deploy-v9","commit-v9-runner","do-commit-v9","trigger-commit",
    "do-commit-v10","commit-v10-final","add-browser","run-now","trigger",
    "v10-trigger","v10-commit-pat","v10-p0","fix-and-upgrade","commit-v9d",
    "v10-final-commit","fix-monitor-now","test-pat","v10-chunk-test",
    "commit-v10-now","v10-commit-real","v10-go","commit-v10-final2",
    "read-file","upgrade-chat-upload","fix-chat-upload2","fix-browser-route",
    "v10-assemble-commit","assemble-and-commit-v10","v11-fix-parts",
    "fix-cron-route","v11-final-commit","v11-debug","v11-commit-chunks",
    "v11-fix-together","v12-ins-01","v12-micro-p0","v12-insert-p4p9",
    "v12-kv-store","v12-insert-p7","v12-insert-p7-exact","v12-p7-native",
    "v12-p7-v2","v12-p7-final","v12-p8-fn","create-vercel-project",
    "debug-sbk","render-one","debug-secret-key","debug-envs",
    "github-yaml-view","github-secrets-setup","github-commit","github-commits",
    "github-workflow-yaml","github-workflow-fix","github-step-log",
]

def run():
    if not TOKEN:
        print("ERRO: SUPABASE_ACCESS_TOKEN nao configurado")
        print("1. app.supabase.com -> Account -> Access Tokens -> New Token")
        print("2. GitHub -> Settings -> Secrets -> SUPABASE_ACCESS_TOKEN")
        return
    r = requests.get(BASE, headers=H, timeout=15)
    if r.status_code != 200:
        print(f"Erro {r.status_code}: {r.text[:100]}")
        return
    all_fns = {fn["slug"] for fn in r.json()}
    to_delete = [fn for fn in ORPHANS if fn in all_fns and fn not in KEEP]
    print(f"Total: {len(all_fns)} | Deletar: {len(to_delete)}")
    deleted = 0
    for slug in to_delete:
        r2 = requests.delete(f"{BASE}/{slug}", headers=H, timeout=15)
        ok = r2.status_code in (200, 204, 404)
        print(f"  {'OK' if ok else 'ERRO'} {slug}")
        if ok: deleted += 1
        time.sleep(0.3)
    print(f"Deletadas: {deleted} | Restando: {len(all_fns)-deleted}")

if __name__=="__main__": run()
