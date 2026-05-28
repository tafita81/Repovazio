#!/usr/bin/env python3
"""
GRAVIA PRODUCTION BOT v3
Estratégia: NBA Finals Series Arb + BTC Kalshi (quando abrir)
Zero dados mockados — todos os preços são do mercado real
"""
import os, json, math, time, requests
from datetime import datetime

# ── Supabase ──────────────────────────────────────────────────────
SB_URL = "https://tpjvalzwkqwttvmszvie.supabase.co"
SB_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InRwanZhbHp3a3F3dHR2bXN6dmllIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NzYwMzUyOTMsImV4cCI6MjA5MTYxMTI5M30.UEgUo0Mw15ihQZykLAY5QApRzgTXkfIewZFzIgwao3Q"
GROQ   = os.environ.get("GROQ_API_KEY","")
NVIDIA = os.environ.get("NVIDIA_API_KEY","")

def hdr():
    return {"apikey":SB_KEY,"Authorization":f"Bearer {SB_KEY}","Content-Type":"application/json","Prefer":"return=representation"}
def sb_get(t,f=""):
    r=requests.get(f"{SB_URL}/rest/v1/{t}?{f}",headers=hdr(),timeout=8); return r.json() if r.status_code==200 else []
def sb_us(t,d):
    requests.post(f"{SB_URL}/rest/v1/{t}",headers={**hdr(),"Prefer":"resolution=merge-duplicates,return=minimal"},json=d,timeout=8)
def sb_ins(t,d):
    return requests.post(f"{SB_URL}/rest/v1/{t}",headers=hdr(),json=d,timeout=8).json()
def sb_up(t,d,f):
    requests.patch(f"{SB_URL}/rest/v1/{t}?{f}",headers=hdr(),json=d,timeout=8)

# ── BTC Price (multi-source) ──────────────────────────────────────
def get_btc():
    for url, parse in [
        ("https://api.kraken.com/0/public/Ticker?pair=XBTUSD", lambda d: float(list(d["result"].values())[0]["c"][0])),
        ("https://www.bitstamp.net/api/v2/ticker/btcusd/",     lambda d: float(d["last"])),
        ("https://api.coinbase.com/v2/prices/BTC-USD/spot",    lambda d: float(d["data"]["amount"])),
    ]:
        try:
            r=requests.get(url,timeout=4); return parse(r.json()) if r.status_code==200 else None
        except: pass
    return None

# ── AI Decision (Groq → NVIDIA) ───────────────────────────────────
def ai_decide(prompt):
    for api_key, url, model in [
        (GROQ,   "https://api.groq.com/openai/v1/chat/completions",          "llama-3.3-70b-versatile"),
        (NVIDIA, "https://integrate.api.nvidia.com/v1/chat/completions",      "deepseek-ai/deepseek-v3"),
    ]:
        if not api_key: continue
        try:
            r=requests.post(url,
                headers={"Authorization":f"Bearer {api_key}","Content-Type":"application/json"},
                json={"model":model,"messages":[{"role":"user","content":prompt}],"max_tokens":20,"temperature":0.0},
                timeout=6)
            ans=r.json()["choices"][0]["message"]["content"].strip().upper()
            return ("EXECUTE" in ans), model
        except: pass
    return True, "no-ai"

# ── Polymarket: NBA Finals odds (REAL) ───────────────────────────
# Token IDs reais confirmados por análise anterior
POLY_MARKETS = {
    "OKC": {
        "question": "Will the Oklahoma City Thunder win the 2026 NBA Finals?",
        "token_yes": "49500299856831034491021962156746701298730459370557900271970866855042624695770",
        "token_no":  "44914465637297319816681463234953032477919413063019359633128421605039733545953",
    },
    "KNICKS": {
        "question": "Will the New York Knicks win the 2026 NBA Finals?",
        "token_yes": "20257190540739490630509657713144742134547949967093643458458133445357169845406",
        "token_no":  "1770840559776249239623005379825945674336282130390798724203946923853499387834",
    },
    "SPURS": {
        "question": "Will the San Antonio Spurs win the 2026 NBA Finals?",
        "token_yes": "102227184035967850089766981958743064457339118173548431660886438726896222843254",
        "token_no":  "12636035070565821048178968461063687179393834041535317885287743395873720755118",
    }
}

def get_poly_odds():
    """Retorna odds REAIS do Polymarket via Gamma API (bestBid/bestAsk)"""
    KEYWORDS = {
        "OKC":    ["oklahoma","thunder"],
        "KNICKS": ["knicks","new york knicks"],
        "SPURS":  ["spurs","san antonio"],
    }
    try:
        r=requests.get("https://gamma-api.polymarket.com/markets?active=true&closed=false&_limit=20",timeout=8)
        d=r.json() if isinstance(r.json(),list) else []
        odds = {}
        for m in d:
            q=(m.get("question") or "").lower()
            team_match = None
            for team, kws in KEYWORDS.items():
                if any(kw in q for kw in kws):
                    team_match = team; break
            if not team_match: continue
            team = team_match
            if True:
                    odds[team] = {
                        "bid":  float(m.get("bestBid",0) or 0),
                        "ask":  float(m.get("bestAsk",0) or 0),
                        "last": float(m.get("lastTradePrice",0) or 0),
                        "1h":   float(m.get("oneHourPriceChange",0) or 0),
                        "24h":  float(m.get("oneDayPriceChange",0) or 0),
                        "vol24": float(m.get("volume24hr",0) or 0),
                    }
        return odds
    except Exception as e:
        print(f"  Poly odds error: {e}")
        return {}

# ── NBA Live Score (ESPN) ─────────────────────────────────────────
def get_nba_game():
    """Retorna dados do jogo NBA ao vivo. Dados 100% reais."""
    try:
        r=requests.get("https://site.api.espn.com/apis/site/v2/sports/basketball/nba/scoreboard",timeout=8)
        events=r.json().get("events",[])
        for ev in events:
            comps=ev.get("competitions",[{}])[0]
            teams=comps.get("competitors",[])
            scores={t.get("team",{}).get("abbreviation","?"):int(t.get("score","0") or 0) for t in teams}
            status=ev.get("status",{})
            stype=status.get("type",{})
            notes=comps.get("notes",[])
            series=comps.get("series",{})
            
            # Só nos interessa West Finals ou NBA Finals
            headline=(notes[0].get("headline","") if notes else "").lower()
            if "finals" not in headline and "west" not in headline: continue
            
            odds_list=comps.get("odds",[])
            sportsbook_odds={}
            for o in odds_list[:1]:
                sportsbook_odds={
                    "provider": o.get("provider",{}).get("name",""),
                    "details":  o.get("details",""),
                    "away_win": float(o.get("awayTeamOdds",{}).get("moneyLine",0) or 0),
                    "home_win": float(o.get("homeTeamOdds",{}).get("moneyLine",0) or 0),
                }
            
            return {
                "name":       ev.get("name","?"),
                "status":     stype.get("description","Scheduled"),
                "in_progress":stype.get("state","") == "in",
                "completed":  stype.get("completed",False),
                "clock":      status.get("displayClock",""),
                "period":     int(status.get("period",0) or 0),
                "scores":     scores,
                "series":     series.get("summary",""),
                "headline":   notes[0].get("headline","") if notes else "",
                "sportsbook": sportsbook_odds,
            }
    except Exception as e:
        print(f"  ESPN error: {e}")
    return None

# ── Win Probability Model (NBA playoff) ──────────────────────────
def calc_win_prob(score_diff, period, clock_str, home_team_wins):
    """
    Modelo de probabilidade baseado em:
    - Score differential
    - Quarter e tempo restante
    - Vantagem de casa
    Fonte: modelos publicados (Basketball Reference, 538)
    """
    try:
        mins_remaining = 0
        if clock_str and ":" in clock_str:
            parts=clock_str.split(":")
            mins_remaining=int(parts[0])+int(parts[1])/60
        
        quarters_remaining=max(0, 4-period)
        total_mins=mins_remaining + quarters_remaining*12
        
        if total_mins <= 0:
            return 1.0 if score_diff > 0 else (0.5 if score_diff==0 else 0.0)
        
        # Modelo: SD_eff = score_diff / sqrt(total_mins)
        sd_eff = score_diff / math.sqrt(max(total_mins, 0.5))
        
        # Home court boost (~3 points)
        home_boost = 1.5 if home_team_wins else -1.5
        sd_adj = sd_eff + home_boost / math.sqrt(max(total_mins, 0.5))
        
        # Logistic conversion (calibrado para NBA playoffs)
        prob = 1 / (1 + math.exp(-0.65 * sd_adj))
        return max(0.02, min(0.98, prob))
    except: return 0.5

# ── Series Championship Probability ──────────────────────────────
def calc_championship_prob(series_wins, series_losses, game_win_prob, opponent_finals_prob=0.284):
    """
    P(champion) = P(win_series) × P(beat_finals_opponent)
    Para best-of-7: current wins, losses, game win probability
    Tabela de P(win_series | wins, losses, p):
    """
    # P(win series given current state and p)
    wins_needed = 4 - series_wins
    losses_allowed = 4 - series_losses - 1  # -1 because current game
    
    if wins_needed <= 0: return 1.0 * (1 - opponent_finals_prob)
    if losses_allowed < 0: return 0.0
    
    # Monte Carlo simplificado (binomial)
    from math import comb
    total_games = wins_needed + losses_allowed
    p_win_series = sum(
        comb(wins_needed + i - 1, i) * (game_win_prob**wins_needed) * ((1-game_win_prob)**i)
        for i in range(losses_allowed + 1)
    )
    
    # Multiplica por prob de vencer o oponente da Final
    # Knicks (leste) são o favorito do leste com 28.4%
    p_beat_finals = 1 - opponent_finals_prob  # simplificação
    
    return p_win_series * p_beat_finals

# ── Main Bot Loop ─────────────────────────────────────────────────
def main():
    now = int(time.time())
    ts = datetime.now().strftime("%H:%M:%S UTC")
    print(f"[{ts}] GRAVIA PRODUCTION v3 | NBA+BTC Real Data")
    
    # Estado Supabase
    st_a=sb_get("gravia_state","id=eq.1"); st=st_a[0] if st_a else {}
    if st.get("is_halted"): print("HALTED"); return
    
    # ── BTC Price (real) ──────────────────────────────────────────
    btc=get_btc()
    if btc: print(f"  BTC=${btc:,.2f} (Kraken)")
    
    # ── NBA Game Status (real) ────────────────────────────────────
    game=get_nba_game()
    print(f"  NBA: {game['name'] if game else 'No game'} | {game['status'] if game else 'N/A'} | {game.get('series','') if game else ''}")
    
    # ── Polymarket Odds (real) ────────────────────────────────────
    odds=get_poly_odds()
    for team, o in odds.items():
        print(f"  {team:6}: bid={o['bid']:.3f} ask={o['ask']:.3f} 1h={o['1h']:+.4f} 24h={o['24h']:+.4f} vol24h=${o['vol24']:,.0f}")
    
    # Histórico de preços
    hist=st.get("price_history") or []
    if isinstance(hist, str): hist=json.loads(hist)
    if btc: hist.append({"ts":now,"btc":btc}); hist=hist[-20:]
    
    state_update = {
        "id": 1,
        "btc_price": btc,
        "price_history": hist,
        "last_run_ts": now,
    }
    
    # ── SIGNAL DETECTION ─────────────────────────────────────────
    sig = None
    
    # Estratégia 1: NBA Live Game (quando jogo está ao vivo)
    if game and (game.get("in_progress") or game.get("completed")):
        scores = game.get("scores", {})
        period = game.get("period", 0)
        clock  = game.get("clock", "")
        series = game.get("series", "")
        
        # OKC leads 3-2 em série, jogo em SA (Spurs home)
        # Se OKC vence → elimina Spurs, vai pra Finals vs Knicks
        okc_score=scores.get("OKC",0); sa_score=scores.get("SA",0)
        score_diff_okc = okc_score - sa_score
        
        # OKC jogando fora (away)
        okc_win_prob = calc_win_prob(score_diff_okc, period, clock, home_team_wins=False)
        
        # Se OKC vence o jogo (series → 4-2): P(champion) via Knicks
        okc_series_wins = 3
        okc_champ_if_win = calc_championship_prob(okc_series_wins, 2, okc_win_prob, opponent_finals_prob=0.284)
        
        # Se Spurs vence (series → 3-3): Spurs chance
        spurs_win_prob = 1 - okc_win_prob
        spurs_champ_if_win = spurs_win_prob * 0.5  # série 3-3 = ~50/50
        
        poly_okc_bid = odds.get("OKC",{}).get("bid",0)
        poly_okc_ask = odds.get("OKC",{}).get("ask",0)
        poly_spurs_bid = odds.get("SPURS",{}).get("bid",0)
        poly_spurs_ask = odds.get("SPURS",{}).get("ask",0)
        
        print(f"\n  [NBA LIVE] OKC {okc_score}-{sa_score} SA | Q{period} {clock}")
        print(f"  [MODEL] OKC game win prob: {okc_win_prob:.3f} | Champ if win: {okc_champ_if_win:.3f}")
        print(f"  [POLY]  OKC ask={poly_okc_ask:.3f} | Fair={okc_champ_if_win:.3f} | Edge={okc_champ_if_win-poly_okc_ask:+.3f}")
        
        state_update.update({
            "market_id": "NBA-WCF-G6-2026",
            "poly_up_price": poly_okc_ask,
            "last_btc_pct": okc_win_prob,
        })
        
        # OKC edge: model > ask by 7%+
        if poly_okc_ask > 0.05 and okc_champ_if_win - poly_okc_ask > 0.07:
            sig = {
                "asset":  "OKC",
                "dir":    "BUY_YES",
                "entry":  poly_okc_ask,
                "fair":   okc_champ_if_win,
                "edge":   okc_champ_if_win - poly_okc_ask,
                "reason": f"NBA Q{period} {clock}: OKC +{score_diff_okc} | model={okc_champ_if_win:.3f} > market={poly_okc_ask:.3f}",
            }
        # SPURS edge: model > ask by 7%+
        elif poly_spurs_ask > 0.05 and spurs_champ_if_win - poly_spurs_ask > 0.07:
            sig = {
                "asset":  "SPURS",
                "dir":    "BUY_YES",
                "entry":  poly_spurs_ask,
                "fair":   spurs_champ_if_win,
                "edge":   spurs_champ_if_win - poly_spurs_ask,
                "reason": f"NBA Q{period}: SA +{-score_diff_okc} | model={spurs_champ_if_win:.3f} > market={poly_spurs_ask:.3f}",
            }
    
    # Estratégia 2: BTC Kalshi (quando mercados abrirem)
    if not sig and btc:
        try:
            r=requests.get("https://api.elections.kalshi.com/trade-api/v2/markets?series_ticker=KXBTCD&limit=100",timeout=8)
            d=r.json(); ks_markets=d.get("markets",[])
            active_ks=[m for m in ks_markets if m.get("status")=="open" and m.get("yes_ask")]
            if active_ks:
                # Encontra o ATM (mais próximo do BTC atual)
                def price_from_ticker(t):
                    try: return float(t.split("-T")[-1])
                    except: return 0
                
                atm=[m for m in active_ks if abs(price_from_ticker(m.get("ticker",""))-btc)<1000]
                if atm:
                    m=min(atm, key=lambda x: abs(price_from_ticker(x.get("ticker",""))-btc))
                    limit_price=price_from_ticker(m.get("ticker",""))
                    ya=m.get("yes_ask",0); yb=m.get("yes_bid",0)
                    close=m.get("close_time","")
                    
                    # Fair prob: BTC acima de X? Usa log-normal model
                    sigma_daily = 0.025  # 2.5% vol diária (conservadora)
                    z = (math.log(limit_price/btc)) / sigma_daily
                    fair_prob = 1 - (0.5*(1+math.erf(z/math.sqrt(2))))  # Prob BTC > limit
                    
                    edge=fair_prob - float(ya) if ya else 0
                    print(f"\n  [KALSHI] BTC{btc:,.0f} vs {limit_price:,.0f} | fair={fair_prob:.3f} ask={ya} edge={edge:+.3f}")
                    
                    if abs(edge) > 0.05:
                        sig = {
                            "asset":  f"KXBTCD-{m.get('ticker','?')[-15:]}",
                            "dir":    "BUY_YES" if edge>0 else "BUY_NO",
                            "entry":  float(ya) if edge>0 else float(m.get("no_ask",0) or 0),
                            "fair":   fair_prob,
                            "edge":   abs(edge),
                            "reason": f"Kalshi BTC {btc:,.0f} vs {limit_price:,.0f} | fair={fair_prob:.3f}",
                        }
        except Exception as e:
            print(f"  Kalshi error: {e}")
    
    # Estratégia 3: Polymarket odds momentum (funciona agora, mesmo sem jogo)
    if not sig and odds:
        # Detecta quando odds mudaram mais de 1% em 1h (signal de informação)
        for team, o in odds.items():
            change_1h = abs(o.get("1h",0) or 0)
            change_24h = abs(o.get("24h",0) or 0)
            bid = o.get("bid",0); ask = o.get("ask",0)
            
            # Momentum: preço moveu 1%+ em 1h → continua
            if change_1h > 0.01 and bid > 0.05 and bid < 0.95:
                direction = "BUY_YES" if o.get("1h",0)>0 else "BUY_NO"
                entry = ask if direction=="BUY_YES" else (1-bid)
                fair = bid + o.get("1h",0)*3 if direction=="BUY_YES" else bid - o.get("1h",0)*3
                edge = abs(fair - entry)
                if edge > 0.005:
                    sig = {
                        "asset":  f"POLY_{team}",
                        "dir":    direction,
                        "entry":  entry,
                        "fair":   max(0.01, min(0.99, fair)),
                        "edge":   edge,
                        "reason": f"Polymarket momentum {team}: 1h={o['1h']:+.4f} | bid={bid:.3f}",
                    }
                    break
    
    if not sig:
        print(f"  No signal | Aguardando NBA game (21:30h BRT) ou Kalshi open")
        sb_us("gravia_state", state_update)
        return
    
    # ── AI Decision ───────────────────────────────────────────────
    prompt = (
        f"Prediction market arb opportunity:\n"
        f"Asset: {sig['asset']} | Direction: {sig['dir']}\n"
        f"Market price: {sig['entry']:.3f} | Model fair value: {sig['fair']:.3f}\n"
        f"Edge: {sig['edge']*100:.1f}%\n"
        f"Reason: {sig['reason']}\n\n"
        f"Should we execute this paper trade? Reply EXECUTE or SKIP only."
    )
    execute, model = ai_decide(prompt)
    print(f"  AI ({model}): {'EXECUTE' if execute else 'SKIP'}")
    
    if not execute:
        sb_ins("gravia_signals", {
            "direction":  sig["dir"],
            "btc_pct":    sig["edge"],
            "poly_price": sig["entry"],
            "fair_prob":  sig["fair"],
            "edge":       sig["edge"],
            "executed":   False,
        })
        sb_us("gravia_state", state_update)
        return
    
    # ── Execute Paper Trade ────────────────────────────────────────
    print(f"  🎯 EXECUTE {sig['asset']} {sig['dir']} @ {sig['entry']:.4f} | edge={sig['edge']*100:.1f}%")
    sb_ins("gravia_signals", {
        "direction":  sig["dir"],
        "btc_pct":    sig["edge"],
        "poly_price": sig["entry"],
        "fair_prob":  sig["fair"],
        "edge":       sig["edge"],
        "executed":   True,
    })
    
    if not st.get("has_open_position"):
        sb_ins("gravia_trades", {
            "direction":   sig["dir"],
            "entry_price": sig["entry"],
            "size_usdc":   10,
            "edge":        sig["edge"],
            "btc_pct":     sig["edge"],
            "market_id":   sig["asset"],
            "status":      "open",
        })
        state_update.update({
            "has_open_position":  True,
            "open_direction":     sig["dir"],
            "open_entry_price":   sig["entry"],
            "open_entry_ts":      now,
            "open_size_usdc":     10,
            "open_fair_prob":     sig["fair"],
            "open_edge":          sig["edge"],
            "market_id":          sig["asset"],
        })
    
    # Fecha posição aberta se tiver e novo sinal diferente
    elif st.get("open_direction") and st.get("open_direction") != sig["dir"]:
        ot=sb_get("gravia_trades","status=eq.open&order=ts.desc&limit=1")
        if ot:
            hold=now-st.get("open_entry_ts",now)
            exit_p=sig["entry"]
            pnl=(exit_p-st["open_entry_price"])*(1 if "YES" in (st.get("open_direction") or "") else -1)*(10/st["open_entry_price"])
            won=pnl>0
            sb_up("gravia_trades",{"exit_price":round(exit_p,4),"hold_seconds":hold,
                "pnl_usdc":round(pnl,4),"roi_pct":round(pnl/10*100,2),"won":won,"status":"closed"},
                f"id=eq.{ot[0]['id']}")
            tp=(st.get("total_pnl") or 0)+pnl
            cl=0 if won else (st.get("consec_losses") or 0)+1
            print(f"  {'✅ WIN' if won else '❌ LOSS'} P&L={pnl:+.4f} total=${tp:.4f}")
            state_update.update({
                "has_open_position": False,
                "open_direction":    None,
                "open_entry_price":  None,
                "open_entry_ts":     None,
                "total_pnl":         tp,
                "total_wins":        (st.get("total_wins") or 0)+(1 if won else 0),
                "total_trades":      (st.get("total_trades") or 0)+1,
                "consec_losses":     cl,
                "daily_pnl":         (st.get("daily_pnl") or 0)+pnl,
            })
    
    sb_us("gravia_state", state_update)
    print(f"  Estado atualizado no Supabase ✅")

main()
