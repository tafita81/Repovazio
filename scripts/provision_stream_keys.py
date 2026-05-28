#!/usr/bin/env python3
"""
provision_stream_keys.py - Agente autonomo de provisionamento de stream keys.

Para cada idioma alvo cujo secret YOUTUBE_STREAM_KEY_<LANG> ainda NAO existe, o agente:
  1. troca o refresh token do canal por um access token (OAuth2 Google);
  2. chama liveStreams.insert (YouTube Data API v3) -> obtem a stream key (cdn.ingestionInfo.streamName);
  3. grava a key como GitHub Actions repository secret (sealed box / libsodium);
  4. (best-effort) espelha a key no Supabase ia_cache.

LIMITE IRREDUTIVEL: o consentimento OAuth e por canal e exige um humano 1x no navegador.
Sem um refresh token VALIDO daquele canal, o idioma e PULADO com log explicito de remediacao.
Assim que o refresh token existir, este agente provisiona a key sozinho no proximo cron.

ENV esperadas:
  GH_PAT, GH_REPO, YOUTUBE_CLIENT_ID, YOUTUBE_CLIENT_SECRET,
  YOUTUBE_REFRESH_TOKEN (PT) e/ou YOUTUBE_REFRESH_TOKEN_<LANG> por canal,
  TARGET_LANGS (csv), SUPABASE_URL + SUPABASE_SERVICE_KEY (opcional, p/ espelho).
"""
import os, sys, json, base64, time
import requests
from nacl import encoding, public

REPO          = os.getenv("GH_REPO", "tafita81/Repovazio")
GH_PAT        = os.getenv("GH_PAT", "").strip()
CLIENT_ID     = os.getenv("YOUTUBE_CLIENT_ID", "").strip()
CLIENT_SECRET = os.getenv("YOUTUBE_CLIENT_SECRET", "").strip()
SUPA_URL      = os.getenv("SUPABASE_URL", "").strip().rstrip("/")
SUPA_KEY      = os.getenv("SUPABASE_SERVICE_KEY", "").strip()
TARGETS       = [x.strip().upper() for x in (os.getenv("TARGET_LANGS") or
                 "PT,EN,ES,DE,FR,IT,JA,KO,AR,ZH,RU,HI").split(",") if x.strip()]
GH = {"Authorization": "Bearer " + GH_PAT, "Accept": "application/vnd.github+json",
      "User-Agent": "psidoc-provisioner", "X-GitHub-Api-Version": "2022-11-28"}

def secret_name(lang):  return "YOUTUBE_STREAM_KEY" if lang == "PT" else "YOUTUBE_STREAM_KEY_" + lang
def refresh_name(lang): return "YOUTUBE_REFRESH_TOKEN" if lang == "PT" else "YOUTUBE_REFRESH_TOKEN_" + lang

def existing_secret_names():
    names, page = set(), 1
    while True:
        r = requests.get("https://api.github.com/repos/%s/actions/secrets?per_page=100&page=%d" % (REPO, page),
                         headers=GH, timeout=30)
        r.raise_for_status()
        chunk = r.json().get("secrets", [])
        names.update(s["name"] for s in chunk)
        if len(chunk) < 100: break
        page += 1
    return names

def get_access_token(refresh_token):
    r = requests.post("https://oauth2.googleapis.com/token", timeout=30, data={
        "client_id": CLIENT_ID, "client_secret": CLIENT_SECRET,
        "refresh_token": refresh_token, "grant_type": "refresh_token"})
    if r.status_code != 200:
        raise RuntimeError("oauth %d: %s" % (r.status_code, r.text[:160]))
    return r.json()["access_token"]

def create_stream_key(access_token, lang):
    hdr = {"Authorization": "Bearer " + access_token, "Content-Type": "application/json"}
    body = {"snippet": {"title": "psicologia.doc %s 24/7" % lang},
            "cdn": {"frameRate": "variable", "ingestionType": "rtmp", "resolution": "variable"}}
    r = requests.post("https://www.googleapis.com/youtube/v3/liveStreams?part=snippet,cdn",
                      headers=hdr, data=json.dumps(body), timeout=30)
    if r.status_code not in (200, 201):
        raise RuntimeError("liveStreams.insert %d: %s" % (r.status_code, r.text[:200]))
    return r.json()["cdn"]["ingestionInfo"]["streamName"]

def put_repo_secret(name, value):
    pk = requests.get("https://api.github.com/repos/%s/actions/secrets/public-key" % REPO, headers=GH, timeout=30)
    pk.raise_for_status(); pkj = pk.json()
    sealed = public.SealedBox(public.PublicKey(pkj["key"].encode(), encoding.Base64Encoder))
    enc = base64.b64encode(sealed.encrypt(value.encode())).decode()
    r = requests.put("https://api.github.com/repos/%s/actions/secrets/%s" % (REPO, name), headers=GH,
                     data=json.dumps({"encrypted_value": enc, "key_id": pkj["key_id"]}), timeout=30)
    if r.status_code not in (201, 204):
        raise RuntimeError("put secret %d: %s" % (r.status_code, r.text[:160]))

def mirror_supabase(lang, value):
    if not (SUPA_URL and SUPA_KEY): return
    ck = "secret:" + secret_name(lang)
    h = {"apikey": SUPA_KEY, "Authorization": "Bearer " + SUPA_KEY,
         "Content-Type": "application/json", "Prefer": "resolution=merge-duplicates"}
    try:
        up = requests.patch("%s/rest/v1/ia_cache?cache_key=eq.%s" % (SUPA_URL, ck),
                            headers=h, data=json.dumps({"value": value}), timeout=20)
        if up.status_code in (200, 204) and up.text not in ("[]", ""):
            return
        requests.post("%s/rest/v1/ia_cache" % SUPA_URL, headers=h,
                      data=json.dumps({"cache_key": ck, "value": value}), timeout=20)
    except Exception as e:
        print("   (espelho Supabase falhou, nao critico: %s)" % e)

def main():
    if not (GH_PAT and CLIENT_ID and CLIENT_SECRET):
        print("ABORT: faltam GH_PAT / YOUTUBE_CLIENT_ID / YOUTUBE_CLIENT_SECRET como secrets."); return
    existing = existing_secret_names()
    print("Stream-key secrets existentes:", sorted(n for n in existing if "STREAM_KEY" in n))
    criadas = pulei = falhei = 0
    for lang in TARGETS:
        sn = secret_name(lang)
        if sn in existing:
            print("[%s] ja existe %s -> pulo." % (lang, sn)); pulei += 1; continue
        rt = os.getenv(refresh_name(lang), "").strip()
        if not rt:
            print("[%s] sem %s (precisa do consentimento OAuth desse canal) -> pulo." % (lang, refresh_name(lang)))
            pulei += 1; continue
        try:
            at = get_access_token(rt)
        except Exception as e:
            print("[%s] OAuth FALHOU: %s -> reautentique e atualize %s." % (lang, e, refresh_name(lang)))
            falhei += 1; continue
        try:
            key = create_stream_key(at, lang)
        except Exception as e:
            print("[%s] criacao da stream key FALHOU: %s" % (lang, e)); falhei += 1; continue
        try:
            put_repo_secret(sn, key)
        except Exception as e:
            print("[%s] gravacao do secret FALHOU: %s" % (lang, e)); falhei += 1; continue
        mirror_supabase(lang, key)
        print("[%s] OK stream key criada e secret %s gravado (autonomo)." % (lang, sn)); criadas += 1
        time.sleep(1)
    print("=== RESUMO provisionamento: criadas=%d puladas=%d falhas=%d ===" % (criadas, pulei, falhei))

if __name__ == "__main__":
    main()
