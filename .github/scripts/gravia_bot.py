#!/usr/bin/env python3
import os,json,math,time,requests
from datetime import datetime,timezone

SB="https://tpjvalzwkqwttvmszvie.supabase.co"
KEY="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InRwanZhbHp3a3F3dHR2bXN6dmllIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NzYwMzUyOTMsImV4cCI6MjA5MTYxMTI5M30.UEgUo0Mw15ihQZykLAY5QApRzgTXkfIewZFzIgwao3Q"
def _h():return{"apikey":KEY,"Authorization":f"Bearer {KEY}","Content-Type":"application/json","Prefer":"return=representation"}
def sg(t,f=""):return requests.get(f"{SB}/rest/v1/{t}?{f}",headers=_h(),timeout=8).json()
def su(t,d):requests.post(f"{SB}/rest/v1/{t}",headers={**_h(),"Prefer":"resolution=merge-duplicates,return=minimal"},json=d,timeout=8)
def si(t,d):return requests.post(f"{SB}/rest/v1/{t}",headers=_h(),json=d,timeout=8).json()
def sp(t,d,f):requests.patch(f"{SB}/rest/v1/{t}?{f}",headers=_h(),json=d,timeout=8)

def precise_time():
    for url in["http://worldtimeapi.org/api/timezone/UTC","https://timeapi.io/api/Time/current/zone?timeZone=UTC"]:
        try:
            r=requests.get(url,timeout=3)
            if r.status_code==200:
                d=r.json();return float(d.get("unixtime") or d.get("dateTime") or time.time())
        except:pass
    return time.time()

def get_btc():
    for url,p in[("https://api.kraken.com/0/public/Ticker?pair=XBTUSD",lambda d:float(list(d["result"].values())[0]["c"][0])),
                 ("https://www.bitstamp.net/api/v2/ticker/btcusd/",lambda d:float(d["last"])),
                 ("https://api.coinbase.com/v2/prices/BTC-USD/spot",lambda d:float(d["data"]["amount"]))]:
        try:
            r=requests.get(url,timeout=4)
            if r.status_code==200:return p(r.json())
        except:pass
    return None

TEAMS={"OKC":["thunder","oklahoma"],"KNICKS":["knicks"],"SPURS":["san antonio","spurs"],
       "CAR":["hurricanes"],"VGK":["golden knights"],"MTL":["canadiens"]}

def get_poly():
    r=requests.get("https://gamma-api.polymarket.com/markets?active=true&closed=false&_limit=20",timeout=8)
    ms=r.json() if isinstance(r.json(),list) else[]
    out={}
    for m in ms:
        q=(m.get("question") or"").lower()
        team=next((t for t,kws in TEAMS.items() if any(k in q for k in kws)),None)
        if not team:continue
        cids_raw=m.get("clobTokenIds","[]")
        try:cids=json.loads(cids_raw) if isinstance(cids_raw,str) else(cids_raw or[])
        except:cids=[]
        out[team]={"yes":cids[0] if cids else None,"no":cids[1] if len(cids)>1 else None,
            "bid":float(m.get("bestBid",0) or 0),"ask":float(m.get("bestAsk",0) or 0),
            "mid":(float(m.get("bestBid",0) or 0)+float(m.get("bestAsk",0) or 0))/2,
            "last":float(m.get("lastTradePrice",0) or 0),
            "1h":float(m.get("oneHourPriceChange",0) or 0),
            "24h":float(m.get("oneDayPriceChange",0) or 0),
            "vol24":float(m.get("volume24hr",0) or 0)}
    return out

def ml2p(ml):
    if ml>0:return 100/(ml+100)
    return abs(ml)/(abs(ml)+100)

def get_odds():
    games=[]
    for sport,league in[("basketball","nba"),("hockey","nhl")]:
        try:
            events=requests.get(f"https://site.api.espn.com/apis/site/v2/sports/{sport}/{league}/scoreboard",timeout=8).json().get("events",[])
            for ev in events:
                c=ev.get("competitions",[{}])[0];eid=ev.get("id","");cid=c.get("id","")
                st=ev.get("status",{});stype=st.get("type",{})
                teams={t.get("team",{}).get("abbreviation","?"):(t.get("homeAway",""),int(t.get("score","0") or 0)) for t in c.get("competitors",[])}
                series=c.get("series",{}).get("summary","")
                r2=requests.get(f"https://sports.core.api.espn.com/v2/sports/{sport}/leagues/{league}/events/{eid}/competitions/{cid}/odds",timeout=6)
                if r2.status_code!=200:continue
                items=r2.json().get("items",[])
                if not items:continue
                r3=requests.get(items[0].get("$ref",""),timeout=5)
                if r3.status_code!=200:continue
                bd=r3.json();aw=bd.get("awayTeamOdds",{});hw=bd.get("homeTeamOdds",{})
                aw_ml=aw.get("moneyLine");hw_ml=hw.get("moneyLine")
                if not(aw_ml and hw_ml):continue
                aw_p=ml2p(float(aw_ml));hw_p=ml2p(float(hw_ml));tot=aw_p+hw_p
                away=next((k for k,(ha,s) in teams.items() if ha=="away"),list(teams.keys())[0])
                home=next((k for k,(ha,s) in teams.items() if ha=="home"),list(teams.keys())[-1])
                games.append({"sport":league,"name":ev.get("name","?"),"away":away,"home":home,
                    "scores":{k:s for k,(ha,s) in teams.items()},"series":series,
                    "status":stype.get("description","?"),"is_live":stype.get("state","")=="in",
                    "is_final":stype.get("completed",False),
                    "period":int(st.get("period",0) or 0),"clock":st.get("displayClock",""),
                    "prov":bd.get("provider",{}).get("name","?"),"details":bd.get("details",""),
                    "away_ml":float(aw_ml),"home_ml":float(hw_ml),
                    "away_p":aw_p/tot,"home_p":hw_p/tot})
        except Exception as e:print(f"  ESPN {league}: {e}")
    return games

def ai(prompt):
    for k,url,model in[(os.environ.get("GROQ_API_KEY",""),"https://api.groq.com/openai/v1/chat/completions","llama-3.3-70b-versatile"),
                       (os.environ.get("NVIDIA_API_KEY",""),"https://integrate.api.nvidia.com/v1/chat/completions","deepseek-ai/deepseek-v3")]:
        if not k:continue
        try:
            r=requests.post(url,headers={"Authorization":f"Bearer {k}","Content-Type":"application/json"},
                json={"model":model,"messages":[{"role":"user","content":prompt}],"max_tokens":10,"temperature":0.0},timeout=6)
            ans=r.json()["choices"][0]["message"]["content"].strip().upper()
            return"EXECUTE" in ans,model
        except:pass
    return True,"no-ai"

LIVE=os.environ.get("POLY_TRADING_LIVE","").lower()=="true"

def place(token_id,side,price,size_usdc):
    if not LIVE:return{"PAPER":True,"token":str(token_id)[:16],"side":side,"price":price}
    try:
        from py_clob_client.client import ClobClient
        from py_clob_client.clob_types import OrderArgs,OrderType
        from py_clob_client.constants import POLYGON
        c=ClobClient(host="https://clob.polymarket.com",key=os.environ.get("POLY_PRIVATE_KEY",""),
            chain_id=POLYGON,creds={"key":os.environ.get("POLY_API_KEY",""),
                "secret":os.environ.get("POLY_SECRET",""),"passphrase":os.environ.get("POLY_PASSPHRASE","")})
        signed=c.create_order(OrderArgs(token_id=token_id,price=price,size=round(size_usdc/price,2),side=side,order_type=OrderType.GTC))
        resp=c.post_order(signed)
        return{"LIVE":True,"order_id":resp.get("orderID","?"),"status":resp.get("status","?")}
    except Exception as e:return{"LIVE":True,"error":str(e)}

def main():
    T0=precise_time()
    ts=datetime.fromtimestamp(T0,tz=timezone.utc).strftime("%H:%M:%S.%f")[:-3]
    print(f"[{ts} UTC] GRAVIA | {'LIVE' if LIVE else 'PAPER'} | sportsbook arb")
    st=(sg("gravia_state","id=eq.1") or[{}])[0]
    if st.get("is_halted"):print("HALTED");return
    btc=get_btc();now=int(T0)
    hist=st.get("price_history") or[]
    if isinstance(hist,str):hist=json.loads(hist)
    if btc:hist.append({"ts":now,"btc":btc});hist=hist[-30:]
    print(f"  BTC ${btc:,.2f}" if btc else"  BTC n/a")

    poly=get_poly()
    for t,p in poly.items():
        fl="!" if abs(p["1h"])>=0.003 else" "
        print(f"  {fl}{t:6}: {p['mid']:.3f} 1h={p['1h']:+.4f} vol24=${p['vol24']:,.0f}")

    games=get_odds();signals=[]
    for g in games:
        away,home=g["away"],g["home"];ap,hp=g["away_p"],g["home_p"];ser=g["series"]
        print(f"\n  [{g['prov']}] {g['name']} | {g['details']} | {g['status']}")
        print(f"    {g['scores']} | {ser} | {away}={ap:.3f} {home}={hp:.3f}")

        if g["sport"]=="nba" and"OKC" in(away,home):
            okc_p=ap if away=="OKC" else hp
            k_mid=poly.get("KNICKS",{}).get("mid",0.284)
            p_win=1.0-k_mid;p_lose=0.58*(1.0-k_mid)
            fair=okc_p*p_win+(1-okc_p)*p_lose
            mid=poly.get("OKC",{}).get("mid",0);edge=mid-fair
            print(f"    OKC fair_champ={fair:.3f} poly={mid:.3f} edge={edge*100:+.1f}%")
            if abs(edge)>0.03:
                buy_no=edge>0
                tok=poly.get("OKC",{}).get("no" if buy_no else"yes")
                entry=round((1-mid) if buy_no else mid,4)
                signals.append({"asset":"OKC_CHAMP","token_id":tok,
                    "direction":"BUY_NO" if buy_no else"BUY_YES",
                    "entry":entry,"fair":round((1-fair) if buy_no else fair,4),"edge":abs(edge),
                    "reason":f"DK {away} p={okc_p:.3f}→champ_fair={fair:.3f} poly={mid:.3f}"})

        if g["sport"]=="nhl" and"CAR" in(away,home):
            car_p=ap if away=="CAR" else hp
            vgk_mid=poly.get("VGK",{}).get("mid",0.441)
            p_win=1.0-vgk_mid;p_lose=0.85*(1.0-vgk_mid)
            fair=car_p*p_win+(1-car_p)*p_lose
            mid=poly.get("CAR",{}).get("mid",0);edge=mid-fair
            print(f"    CAR fair_champ={fair:.3f} poly={mid:.3f} edge={edge*100:+.1f}%")
            if abs(edge)>0.03:
                buy_no=edge>0
                tok=poly.get("CAR",{}).get("no" if buy_no else"yes")
                entry=round((1-mid) if buy_no else mid,4)
                signals.append({"asset":"CAR_CHAMP","token_id":tok,
                    "direction":"BUY_NO" if buy_no else"BUY_YES",
                    "entry":entry,"fair":round((1-fair) if buy_no else fair,4),"edge":abs(edge),
                    "reason":f"DK CAR p={car_p:.3f}→champ_fair={fair:.3f} poly={mid:.3f}"})

    if not signals:
        for t,p in poly.items():
            if abs(p["1h"])>=0.004 and 0.05<p["mid"]<0.95 and p["vol24"]>20000:
                buy=p["1h"]>0;tok=p.get("yes" if buy else"no")
                signals.append({"asset":f"{t}_MOM","token_id":tok,
                    "direction":"BUY_YES" if buy else"BUY_NO",
                    "entry":round(p["ask"] if buy else 1-p["bid"],4),
                    "fair":round(p["mid"]+p["1h"]*5,4),"edge":abs(p["1h"])*5,
                    "reason":f"{t} momentum 1h={p['1h']:+.4f}"})

    signals.sort(key=lambda x:-x["edge"])
    base={"id":1,"btc_price":btc,"price_history":hist,"last_run_ts":now,
          "poly_up_price":poly.get("OKC",{}).get("mid",0)}
    if not signals:print("\n  Sem sinal");su("gravia_state",base);return

    sig=signals[0]
    if not sig.get("token_id"):print(f"\n  Sem token {sig['asset']}");su("gravia_state",base);return

    execute,model=ai(f"Arb {sig['asset']} {sig['direction']} edge={sig['edge']*100:.1f}%\n{sig['reason']}\nEXECUTE or SKIP?")
    print(f"\n  AI ({model}): {'EXECUTE' if execute else 'SKIP'}")
    print(f"  {sig['asset']} {sig['direction']} @ {sig['entry']:.4f} fair={sig['fair']:.4f} edge={sig['edge']*100:.1f}%")

    si("gravia_signals",{"direction":sig["direction"],"btc_pct":sig["edge"],
        "poly_price":sig["entry"],"fair_prob":sig["fair"],"edge":sig["edge"],"executed":execute})
    if not execute:su("gravia_state",base);return

    if st.get("has_open_position") and st.get("open_entry_ts"):
        ot=sg("gravia_trades","status=eq.open&order=ts.desc&limit=1")
        if ot:
            hold=now-(st.get("open_entry_ts") or now)
            dir_yes="YES" in(st.get("open_direction") or"")
            old_t=(st.get("market_id") or"").split("_")[0]
            cur=poly.get(old_t,{}).get("mid") or st.get("open_entry_price",0)
            ep=float(cur if dir_yes else 1-cur)
            pnl=(ep-st["open_entry_price"])*(1 if dir_yes else-1)*(10/st["open_entry_price"])
            won=pnl>0
            sp("gravia_trades",{"exit_price":round(ep,4),"hold_seconds":hold,
                "pnl_usdc":round(pnl,4),"roi_pct":round(pnl/10*100,2),"won":won,"status":"closed"},
                f"id=eq.{ot[0]['id']}")
            tp=(st.get("total_pnl") or 0)+pnl;cl=0 if won else(st.get("consec_losses") or 0)+1
            print(f"  {'WIN' if won else 'LOSS'} P&L={pnl:+.4f} total=${tp:.4f}")
            base.update({"has_open_position":False,"total_pnl":tp,
                "total_wins":(st.get("total_wins") or 0)+(1 if won else 0),
                "total_trades":(st.get("total_trades") or 0)+1,"consec_losses":cl,
                "daily_pnl":(st.get("daily_pnl") or 0)+pnl,
                "is_halted":(st.get("daily_pnl") or 0)+pnl<=-50 or cl>=5})

    order=place(sig["token_id"],"BUY" if"YES" in sig["direction"] else"SELL",sig["entry"],10.0)
    si("gravia_trades",{"direction":sig["direction"],"entry_price":sig["entry"],
        "size_usdc":10,"edge":sig["edge"],"btc_pct":sig["edge"],"market_id":sig["asset"],"status":"open"})
    base.update({"has_open_position":True,"open_direction":sig["direction"],
        "open_entry_price":sig["entry"],"open_entry_ts":now,"open_size_usdc":10,
        "open_fair_prob":sig["fair"],"open_edge":sig["edge"],"market_id":sig["asset"]})
    su("gravia_state",base)

    roi=(sig["fair"]-sig["entry"])/max(sig["entry"],0.001)*10
    print(f"\n  {'LIVE' if LIVE else 'PAPER'} {order}")
    print(f"  OK {(time.time()-T0)*1000:.0f}ms | {sig['asset']} @ {sig['entry']:.4f} | P&L esperado ${roi:+.2f}")

main()
