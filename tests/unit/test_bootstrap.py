from datetime import date,datetime
from kite_strategy_platform.runtime.bootstrap import MarketBootstrap
from kite_strategy_platform.domain.market_data import Quote
def rows():
    r=[{"exchange":"NSE","tradingsymbol":"NIFTY","instrument_token":"1","expiry":"","strike":"","instrument_type":"EQ","lot_size":"1","tick_size":".05","name":"NIFTY"}]
    i=2
    for e in ("2026-01-08","2026-01-15"):
      for s in (20000,20050,19950):
       for t in ("CE","PE"):
        r.append({"exchange":"NFO","tradingsymbol":f"NIFTY{s}{t}","instrument_token":str(i),"expiry":e,"strike":str(s),"instrument_type":t,"lot_size":"65","tick_size":".05","name":"NIFTY"}); i+=1
    return r
def test_bootstrap_selects_atm_expiries_and_tokens():
    b=MarketBootstrap(rows(),"NIFTY"); u=b.build(20020,date(2026,1,1),hedge_distance=1); assert u.atm_strike==20000 and len(u.tokens)==13
def test_opening_price_requires_0915():
    b=MarketBootstrap(rows(),"NIFTY")
    assert b.opening_price([Quote("1",datetime(2026,1,1,9,15),last=20020)])==20020

def test_bootstrap_uses_modal_strike_interval_not_irregular_gap():
    data=rows()
    for expiry in ("2026-01-08","2026-01-15"):
        for typ in ("CE","PE"):
            data.append({"exchange":"NFO","tradingsymbol":f"ODD{typ}","instrument_token":"99","expiry":expiry,"strike":"20005","instrument_type":typ,"lot_size":"65","tick_size":".05","name":"NIFTY"})
    assert MarketBootstrap(data,"NIFTY").build(20020,date(2026,1,1),hedge_distance=1).atm_strike==20000
