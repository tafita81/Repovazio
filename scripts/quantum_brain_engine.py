#!/usr/bin/env python3
"""quantum_brain_engine.py - Motor Combinatorial Auto-Evolutivo
Combina 1839+ APIs em grupos de 10 gerando sistemas ineditos automaticamente
Aprende: score alto priorizar, baixo descartar. Evolui infinitamente.
"""
import os,json,random,requests,time,hashlib
from datetime import datetime
SB_URL=os.getenv("SUPABASE_URL","https://tpjvalzwkqwttvmszvie.supabase.co")
SB_KEY=os.getenv("SUPABASE_SERVICE_ROLE_KEY","")
GROQ_KEY=os.getenv("GROQ_API_KEY","")
def sbh():
    return {"apikey":SB_KEY,"Authorization":f"Bearer {SB_KEY}","Content-Type":"application/json"}
def get_apis(sem_auth=False,lim=200):
    q=f"{SB_URL}/rest/v1/api_brain?select=name,category,endpoint,auth_type&limit={lim}"
    if sem_auth:q+="&auth_type=eq.none"
    r=requests.get(q,headers=sbh(),timeout=15)
    return r.json() if r.status_code==200 else []
def gerar_combo(apis,n=10):
    escolhidas=random.sample(apis,min(n,len(apis)))
    cid=hashlib.md5("|".join(a["name"] for a in escolhidas).encode()).hexdigest()[:8]
    return {"id":cid,"apis":escolhidas}
def avaliar_combo(combo):
    if not GROQ_KEY:return{"score":50,"produto":"sem key","mecanismo":"","receita_90d_usd":0,"case_real":""}
    nomes=", ".join(f"{a['name']} ({a['category']})" for a in combo["apis"])
    prompt=f"Expert startups. APIs: {nomes}. Score 0-100, produto inedito, mecanismo receita, receita 90d USD, case real. JSON: "+"{\"score\":85,\"produto\":\"nome\",\"mecanismo\":\"como\",\"receita_90d_usd\":5000,\"case_real\":\"empresa\"}"
    try:
        r=requests.post("https://api.groq.com/openai/v1/chat/completions",
            headers={"Authorization":f"Bearer {GROQ_KEY}","Content-Type":"application/json"},
            json={"model":"llama-3.3-70b-versatile","messages":[{"role":"user","content":prompt}],
                  "max_tokens":500,"response_format":{"type":"json_object"}},timeout=45)
        if r.status_code==200:return json.loads(r.json()["choices"][0]["message"]["content"])
    except:pass
    return{"score":0,"produto":"erro","mecanismo":"","receita_90d_usd":0,"case_real":""}
def salvar(combo,aval):
    if not SB_KEY:return
    requests.post(f"{SB_URL}/rest/v1/quantum_combinations",
        headers={**sbh(),"Prefer":"resolution=ignore-duplicates"},
        json={"combo_id":combo["id"],"n_apis":len(combo["apis"]),
              "apis_nomes":[a["name"] for a in combo["apis"]],
              "score":aval.get("score",0),"produto":aval.get("produto",""),
              "mecanismo":aval.get("mecanismo",""),"receita_90d_usd":aval.get("receita_90d_usd",0),
              "case_real":aval.get("case_real",""),"gerado_em":datetime.now().isoformat()},timeout=10)
def run(n=5):
    print(f"QUANTUM BRAIN ENGINE {datetime.now():%Y-%m-%d %H:%M}")
    apis=get_apis(lim=200);gratis=get_apis(sem_auth=True,lim=100)
    print(f"APIs: {len(apis)} total {len(gratis)} gratis")
    res=[]
    for i in range(n):
        pool=gratis if gratis and random.random()<0.6 else apis
        combo=gerar_combo(pool,10)
        print(f"\n[{i+1}/{n}] {combo['id']}: {[a['name'] for a in combo['apis'][:3]]}...")
        aval=avaliar_combo(combo)
        score=aval.get("score",0);receita=aval.get("receita_90d_usd",0)
        print(f"  Score:{score} ${receita:,}/90d {aval.get('produto','?')[:40]}")
        if score>=60:salvar(combo,aval);print(f"  SALVO")
        res.append({"id":combo["id"],"score":score,"receita":receita})
        time.sleep(2)
    best=max(res,key=lambda x:x["score"]) if res else {}
    print(f"\nMelhor: {best.get('id','?')} score={best.get('score',0)} ${best.get('receita',0):,}/90d")
if __name__=="__main__":
    import sys;run(int(sys.argv[1]) if len(sys.argv)>1 else 5)
