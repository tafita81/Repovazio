#!/usr/bin/env python3
"""
GRAVIA FINAL — Sportsbook vs Polymarket Arbitrage
Maior uso real: bookmaker implied prob vs prediction market price
"""
import os, json, math, time, requests
from datetime import datetime, timezone

# ── Tempo preciso (HTTP NTP) ──────────────────────────────────────
def precise_time():
    for url in ["http://worldtimeapi.org/api/timezone/UTC","https://timeapi.io/api/Time/current/zone?timeZone=UTC"]:
        try:
            r = requests.get(url, timeout=3)
            if r.status_code == 200:
                d = r.json()
                t = d.get("unixtime") or time.time()
                return float(t), url.split("/")[2]
        except: pass
    return time.time(), "system"

# ── Supabase ──────────────────────────────────────────────────────
SB  = "https://tpjvalzwkqwttvmszvie.supabase.co"
KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InRwanZhbHp3a3F3dHR2bXN6dmllIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NzYwMzUyOTMsImV4cCI6MjA5MTYxMTI5M30.UEgUo0Mw15ihQZykLAY5QApRzgTXkfIewZFzIgwao3Q"

def _h(): return {"apikey":KEY,"Authorization":f"Bearer {KEY}","Content-Type":"application/json","Prefer":"return=representation"}
def sg(t,f=""): return requests.get(f"{SB}/rest/v1/{t}?{f}", headers=_h(), timeout=8).json()
def su(t,d):    requests.post(f"{SB}/rest/v1/{t}", headers={**_h(),"Prefer":"resolution=merge-duplicates,return=minimal"}, json=d, timeout=8)
def si(t,d):    return requests.post(f"{SB}/rest/v1/{t}", headers=_h(), json=d, timeout=8).json()
def sp(t,d,f):  requests.patch(f"{SB}/rest/v1/{t}?{f}", headers=_h(), json=d, timeout=8)

# ── BTC Price ─────────────────────────────────────────────────────
def get_btc():
    for url, parse in [
        ("https://api.kraken.com/0/public/Ticker?pair=XBTUSD", lambda d: float(list(d["result"].values())[0]["c"][0])),
        ("https://www.bitstamp.net/api/v2/ticker/btcusd/",     lambda d: float(d["last"])),
        ("https://api.coinbase.com/v2/prices/BTC-USD/spot",    lambda d: float(d["data"]["amount"])),
    ]:
        try:
            r = requests.get(url, timeout=4)
            if r.status_code == 200: return parse(r.json())
        except: pass
    return None

# ── Polymarket — preços e tokens via Gamma API ────────────────────
TEAM_KEYWORDS = {
    "OKC":    ["thunder","oklahoma"],
    "KNICKS": ["knicks"],
    "SPURS":  ["san antonio","spurs"],
    "CAR":    ["hurricanes"],
    "VGK":    ["golden knights"],
    "MTL":    ["canadiens"],
}

def get_poly_markets():
    """Retorna tokens + preços reais via Gamma API (sempre atualizados)"""
    try:
        r = requests.get("https://gamma-api.polymarket.com/markets?active=true&closed=false&_limit=20", timeout=8)
        ms = r.json() if isinstance(r.json(), list) else []
        result = {}
        for m in ms:
            q = (m.get("question") or "").lower()
            team = None
            for t, kws in TEAM_KEYWORDS.items():
                if any(kw in q for kw in kws): team = t; break
            if not team: continue
            
            cids_raw = m.get("clobTokenIds","[]")
            try: cids = json.loads(cids_raw) if isinstance(cids_raw,str) else (cids_raw or [])
            except: cids = []
            
            result[team] = {
                "token_yes": cids[0] if cids else None,
                "token_no":  cids[1] if len(cids)>1 else None,
                "bid":  float(m.get("bestBid",0) or 0),
                "ask":  float(m.get("bestAsk",0) or 0),
                "last": float(m.get("lastTradePrice",0) or 0),
                "mid":  (float(m.get("bestBid",0) or 0) + float(m.get("bestAsk",0) or 0)) / 2,
                "1h":   float(m.get("oneHourPriceChange",0) or 0),
                "24h":  float(m.get("oneDayPriceChange",0) or 0),
                "vol24":float(m.get("volume24hr",0) or 0),
                "q": (m.get("question") or "")[:70],
            }
        return result
    except Exception as e:
        print(f"  Poly error: {e}"); return {}

# ── ESPN Bookmaker Odds ────────────────────────────────────────────
def ml_to_prob(ml: float) -> float:
    if ml > 0: return 100/(ml+100)
    return abs(ml)/(abs(ml)+100)

def get_live_odds() -> list:
    """Retorna odds DraftKings/ESPN de todos os jogos ao vivo/hoje"""
    games = []
    for sport, league in [("basketball","nba"), ("hockey","nhl")]:
        try:
            r = requests.get(f"https://site.api.espn.com/apis/site/v2/sports/{sport}/{league}/scoreboard", timeout=8)
            events = r.json().get("events",[])
            for ev in events:
                comps = ev.get("competitions",[{}])[0]
                ev_id = ev.get("id",""); comp_id = comps.get("id","")
                status = ev.get("status",{})
                stype = status.get("type",{})
                series = comps.get("series",{})
                notes = comps.get("notes",[])
                teams = {t.get("team",{}).get("abbreviation","?"): int(t.get("score","0") or 0)
                         for t in comps.get("competitors",[])}
                home_away = {t.get("team",{}).get("abbreviation","?"): t.get("homeAway","")
                             for t in comps.get("competitors",[])}
                
                # Busca odds via ESPN ref
                odds_url = f"https://sports.core.api.espn.com/v2/sports/{sport}/leagues/{league}/events/{ev_id}/competitions/{comp_id}/odds"
                r2 = requests.get(odds_url, timeout=6)
                if r2.status_code != 200: continue
                
                for item_ref in r2.json().get("items",[])[:1]:
                    r3 = requests.get(item_ref.get("$ref",""), timeout=5)
                    if r3.status_code != 200: continue
                    bd = r3.json()
                    aw = bd.get("awayTeamOdds",{}); hw = bd.get("homeTeamOdds",{})
                    aw_ml = aw.get("moneyLine"); hw_ml = hw.get("moneyLine")
                    if not (aw_ml and hw_ml): continue
                    
                    aw_p = ml_to_prob(float(aw_ml)); hw_p = ml_to_prob(float(hw_ml))
                    total = aw_p + hw_p
                    # Remove vig (overround do bookmaker)
                    aw_fair = aw_p/total; hw_fair = hw_p/total
                    
                    away_abbr = next((k for k,v in home_away.items() if v=="away"), list(teams.keys())[0])
                    home_abbr = next((k for k,v in home_away.items() if v=="home"), list(teams.keys())[-1])
                    
                    games.append({
                        "sport": league, "name": ev.get("name","?"),
                        "away": away_abbr, "home": home_abbr,
                        "scores": teams, "series": series.get("summary",""),
                        "status": stype.get("description","?"),
                        "period": int(status.get("period",0) or 0),
                        "clock": status.get("displayClock",""),
                        "is_live": stype.get("state","") == "in",
                        "is_final": stype.get("completed",False),
                        "provider": bd.get("provider",{}).get("name","?"),
                        "details": bd.get("details",""),
                        "away_ml": float(aw_ml), "home_ml": float(hw_ml),
                        "away_prob": aw_fair, "home_prob": hw_fair,
                    })
                    break
        except Exception as e:
            print(f"  ESPN {league} error: {e}")
    return games

# ── Modelo de probabilidade de campeonato ─────────────────────────
def championship_prob(series_wins:int, series_losses:int, win_p:float, finals_opp_p:float) -> float:
    """P(champion) via binomial série + Finals"""
    if series_wins >= 4: return max(0.0, 1.0 - finals_opp_p)
    if series_losses >= 4: return 0.0
    wins_needed = 4 - series_wins; max_loss = 3 - series_losses
    p_series = sum(
        math.comb(wins_needed+i-1,i) * win_p**wins_needed * (1-win_p)**i
        for i in range(max_loss+1))
    return float(p_series) * (1.0 - finals_opp_p)

# ── Parse série (ex: "OKC leads series 3-2") ─────────────────────
def parse_series(series_str:str, team:str):
    try:
        s = series_str.lower()
        # "okc leads series 3-2" ou "tied 2-2" ou "sa leads 3-1"
        import re
        m = re.search(r'(\d)-(\d)', s)
        if not m: return 0,0
        a,b = int(m.group(1)), int(m.group(2))
        team_l = team.lower()
        if "tied" in s: return a,b  # ambos mesmo
        if any(kw in s for kw in [team_l,"leads"]):
            # "leads" = o time mencionado está ganhando
            if team_l in s.split("leads")[0] if "leads" in s else s:
                return a,b
        return b,a  # invertido
    except: return 0,0

# ── AI Decision ───────────────────────────────────────────────────
def ai_decide(prompt:str) -> tuple[bool,str]:
    for key, url, model in [
        (os.environ.get("GROQ_API_KEY",""),   "https://api.groq.com/openai/v1/chat/completions",         "llama-3.3-70b-versatile"),
        (os.environ.get("NVIDIA_API_KEY",""), "https://integrate.api.nvidia.com/v1/chat/completions",     "deepseek-ai/deepseek-v3"),
    ]:
        if not key: continue
        try:
            r = requests.post(url,
                headers={"Authorization":f"Bearer {key}","Content-Type":"application/json"},
                json={"model":model,"messages":[{"role":"user","content":prompt}],"max_tokens":10,"temperature":0.0},
                timeout=6)
            ans = r.json()["choices"][0]["message"]["content"].strip().upper()
            return "EXECUTE" in ans, model
        except: pass
    return True, "no-ai"

# ── Execução real via py-clob-client ──────────────────────────────
LIVE = os.environ.get("POLY_TRADING_LIVE","").lower() == "true"

def place_order(token_id:str, side:str, price:float, size_usdc:float) -> dict:
    if not LIVE:
        return {"mode":"PAPER","token":token_id[:16],"side":side,"price":price,"size_usdc":size_usdc}
    try:
        from py_clob_client.client import ClobClient
        from py_clob_client.clob_types import OrderArgs, OrderType
        from py_clob_client.constants import POLYGON
        client = ClobClient(
            host="https://clob.polymarket.com", key=os.environ.get("POLY_PRIVATE_KEY",""),
            chain_id=POLYGON, creds={"key":os.environ.get("POLY_API_KEY",""),
                "secret":os.environ.get("POLY_SECRET",""),"passphrase":os.environ.get("POLY_PASSPHRASE","")})
        order  = client.create_order(OrderArgs(
            token_id=token_id, price=price,
            size=round(size_usdc/price, 2), side=side, order_type=OrderType.GTC))
        resp   = client.post_order(order)
        return {"mode":"🔴LIVE","order_id":resp.get("orderID","?"),"status":resp.get("status","?")}
    except Exception as e:
        return {"mode":"🔴LIVE","error":str(e)}

# ── Main ──────────────────────────────────────────────────────────
def main():
    T0, time_src = precise_time()
    ts  = datetime.fromtimestamp(T0, tz=timezone.utc).strftime("%H:%M:%S.%f")[:-3]
    mode_lbl = "🔴 LIVE" if LIVE else "📄 PAPER"
    print(f"[{ts} UTC via {time_src}] GRAVIA | {mode_lbl} | sportsbook arb")

    st   = (sg("gravia_state","id=eq.1") or [{}])[0]
    if st.get("is_halted"): print("  HALTED — reset via dashboard"); return

    btc  = get_btc()
    now  = int(T0)
    hist = st.get("price_history") or []
    if isinstance(hist,str): hist = json.loads(hist)
    if btc: hist.append({"ts":now,"btc":btc}); hist = hist[-30:]
    print(f"  BTC ${btc:,.2f}" if btc else "  BTC: unavailable")

    # Preços Polymarket
    poly = get_poly_markets()
    for team, p in poly.items():
        flag = "⚡" if abs(p["1h"])>=0.003 else " "
        print(f"  {flag}{team:6}: {p['mid']:.3f} | 1h={p['1h']:+.4f} 24h={p['24h']:+.4f} vol=${p['vol24']:,.0f}")

    # Odds ESPN/DraftKings
    games = get_live_odds()
    signals = []

    for g in games:
        away, home = g["away"], g["home"]
        away_p, home_p = g["away_prob"], g["home_prob"]
        series = g["series"]; sport = g["sport"]
        print(f"\n  [{g['provider']}] {g['name']}")
        print(f"    {g['details']} | {g['status']} {g['clock']} | {g['scores']}")
        print(f"    {away}={away_p:.3f} {home}={home_p:.3f} | série: {series}")

        # NBA: OKC série 3-2
        if sport=="nba" and ("OKC" in (away,home)):
            okc_game_p = away_p if away=="OKC" else home_p
            knicks_p = poly.get("KNICKS",{}).get("mid",0.284)
            # G7 em casa para OKC se perder hoje
            p_g7_okc  = 0.58 if "OKC" in series.split("leads")[0] if "leads" in series.lower() else "OKC" else 0.50
            p_if_win  = 1.0 - knicks_p
            p_if_lose = p_g7_okc * (1.0 - knicks_p)
            fair = okc_game_p*p_if_win + (1-okc_game_p)*p_if_lose
            mid  = poly.get("OKC",{}).get("mid",0)
            edge = mid - fair  # >0 = poly sobrevalorizado = vende OKC
            print(f"    OKC game_p={okc_game_p:.3f} → fair_champ={fair:.3f} vs poly={mid:.3f} edge={edge*100:+.1f}%")
            
            if abs(edge) > 0.04:
                buy_no  = edge > 0  # poly sobrevalorizado → compra NO
                team_key= "OKC"
                tok = poly.get(team_key,{}).get("token_no" if buy_no else "token_yes")
                entry = round((1-mid) if buy_no else mid, 4)
                fair_p = round((1-fair) if buy_no else fair, 4)
                signals.append({
                    "asset":f"POLY_{team_key}_CHAMP",
                    "token_id": tok,
                    "direction":"BUY_NO" if buy_no else "BUY_YES",
                    "entry": entry, "fair": fair_p, "edge": abs(edge),
                    "reason": f"{g['provider']} {away} game_p={okc_game_p:.3f}→champ_fair={fair:.3f} poly={mid:.3f}",
                })

        # NHL: CAR série 3-1
        if sport=="nhl" and ("CAR" in (away,home)):
            car_game_p = away_p if away=="CAR" else home_p
            vgk_p = poly.get("VGK",{}).get("mid",0.441)
            # Se CAR vencer hoje (4-1) → vai pra Final vs VGK
            p_if_win  = 1.0 - vgk_p
            p_if_lose = 0.85 * (1.0-vgk_p)  # ainda favorito 3-2
            fair = car_game_p*p_if_win + (1-car_game_p)*p_if_lose
            mid  = poly.get("CAR",{}).get("mid",0)
            edge = mid - fair
            print(f"    CAR game_p={car_game_p:.3f} → fair_champ={fair:.3f} vs poly={mid:.3f} edge={edge*100:+.1f}%")
            
            if abs(edge) > 0.04:
                buy_no  = edge > 0
                tok = poly.get("CAR",{}).get("token_no" if buy_no else "token_yes")
                entry = round((1-mid) if buy_no else mid, 4)
                fair_p = round((1-fair) if buy_no else fair, 4)
                signals.append({
                    "asset":"POLY_CAR_CHAMP",
                    "token_id": tok,
                    "direction":"BUY_NO" if buy_no else "BUY_YES",
                    "entry": entry, "fair": fair_p, "edge": abs(edge),
                    "reason": f"{g['provider']} CAR game_p={car_game_p:.3f}→champ_fair={fair:.3f} poly={mid:.3f}",
                })

    # Momentum fallback (qualquer time com 1h > 0.4%)
    if not signals:
        for team, p in poly.items():
            if abs(p["1h"]) >= 0.004 and 0.05 < p["mid"] < 0.95 and p["vol24"] > 20000:
                buy = p["1h"] > 0
                tok = p.get("token_yes" if buy else "token_no")
                entry = round(p["ask"] if buy else 1-p["bid"], 4)
                fair  = round(p["mid"] + p["1h"]*5, 4)
                signals.append({
                    "asset":f"POLY_{team}_MOMENTUM",
                    "token_id": tok,
                    "direction":"BUY_YES" if buy else "BUY_NO",
                    "entry": entry, "fair": fair, "edge": abs(p["1h"])*5,
                    "reason":f"Momentum 1h={p['1h']:+.4f}",
                })

    signals.sort(key=lambda x: -x["edge"])

    # Atualiza estado base
    base_state = {"id":1,"btc_price":btc,"price_history":hist,"last_run_ts":now,
                  "poly_up_price": poly.get("OKC",{}).get("mid",0)}

    if not signals:
        print(f"\n  No signal")
        su("gravia_state", base_state); return

    sig = signals[0]
    if not sig.get("token_id"):
        print(f"\n  Sinal sem token ID: {sig['asset']}")
        su("gravia_state", base_state); return

    # AI
    prompt = (
        f"Prediction market arb:\n"
        f"Asset: {sig['asset']} | Direction: {sig['direction']}\n"
        f"Entry: {sig['entry']:.4f} | Fair: {sig['fair']:.4f} | Edge: {sig['edge']*100:.1f}%\n"
        f"Reason: {sig['reason']}\n\nEXECUTE or SKIP?"
    )
    execute, model = ai_decide(prompt)
    print(f"\n  AI ({model}): {'EXECUTE' if execute else 'SKIP'} | {sig['asset']} {sig['direction']} edge={sig['edge']*100:.1f}%")

    si("gravia_signals",{"direction":sig["direction"],"btc_pct":sig["edge"],
        "poly_price":sig["entry"],"fair_prob":sig["fair"],"edge":sig["edge"],"executed":execute})

    if not execute:
        su("gravia_state", base_state); return

    # Fecha posição aberta se existir
    if st.get("has_open_position") and st.get("open_entry_ts"):
        ot = sg("gravia_trades","status=eq.open&order=ts.desc&limit=1")
        if ot:
            hold = now - (st.get("open_entry_ts") or now)
            dir_is_yes = "YES" in (st.get("open_direction") or "")
            old_team = (st.get("market_id") or "").replace("POLY_","").replace("_CHAMP","").replace("_MOMENTUM","")
            cur_mid = poly.get(old_team,{}).get("mid") or st.get("open_entry_price",0)
            exit_p = float(cur_mid if dir_is_yes else 1-cur_mid)
            pnl = (exit_p - st["open_entry_price"]) * (1 if dir_is_yes else -1) * (10/st["open_entry_price"])
            won = pnl > 0
            sp("gravia_trades",{"exit_price":round(exit_p,4),"hold_seconds":hold,
                "pnl_usdc":round(pnl,4),"roi_pct":round(pnl/10*100,2),"won":won,"status":"closed"},
                f"id=eq.{ot[0]['id']}")
            tp = (st.get("total_pnl") or 0)+pnl; cl = 0 if won else (st.get("consec_losses") or 0)+1
            print(f"  {'✅' if won else '❌'} Fechou posição: P&L={pnl:+.4f} | total=${tp:.4f}")
            base_state.update({"has_open_position":False,"open_direction":None,
                "open_entry_price":None,"open_entry_ts":None,"total_pnl":tp,
                "total_wins":(st.get("total_wins") or 0)+(1 if won else 0),
                "total_trades":(st.get("total_trades") or 0)+1,
                "consec_losses":cl,"daily_pnl":(st.get("daily_pnl") or 0)+pnl,
                "is_halted":(st.get("daily_pnl") or 0)+pnl<=-50 or cl>=5})

    # Coloca ordem
    order = place_order(sig["token_id"], "BUY" if "YES" in sig["direction"] else "SELL",
                        sig["entry"], 10.0)
    si("gravia_trades",{"direction":sig["direction"],"entry_price":sig["entry"],
        "size_usdc":10,"edge":sig["edge"],"btc_pct":sig["edge"],
        "market_id":sig["asset"],"status":"open"})
    base_state.update({"has_open_position":True,"open_direction":sig["direction"],
        "open_entry_price":sig["entry"],"open_entry_ts":now,"open_size_usdc":10,
        "open_fair_prob":sig["fair"],"open_edge":sig["edge"],"market_id":sig["asset"]})
    su("gravia_state", base_state)

    T1 = time.time()
    roi = (sig["fair"]-sig["entry"])/sig["entry"]*10 if sig["entry"]>0 else 0
    print(f"\n  {'🔴 LIVE' if LIVE else '📄 PAPER'}: {order}")
    print(f"  ✅ {(T1-T0)*1000:.0f}ms | {sig['asset']} {sig['direction']} @ {sig['entry']:.4f}")
    print(f"  📈 P&L esperado: ${roi:+.2f} em $10 se correto")

main()
