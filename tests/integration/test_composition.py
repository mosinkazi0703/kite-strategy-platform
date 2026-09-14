from datetime import date,datetime,timezone
from kite_strategy_platform.runtime.composition import LivePaperComposition
from kite_strategy_platform.domain.market_data import Quote
def rows():
 r=[{"exchange":"NSE","tradingsymbol":"NIFTY","instrument_token":"1","expiry":"","strike":"","instrument_type":"EQ","lot_size":"1","tick_size":".05","name":"NIFTY"}]; i=2
 for e in ("2026-01-08","2026-01-15"):
  for s in (20000,20050,19950):
   for t in ("CE","PE"): r.append({"exchange":"NFO","tradingsymbol":f"NIFTY{s}{t}","instrument_token":str(i),"expiry":e,"strike":str(s),"instrument_type":t,"lot_size":"65","tick_size":".05","name":"NIFTY"}); i+=1
 return r
def test_universe_quote_freshness_and_marking(tmp_path):
 c=LivePaperComposition(rows(),"NIFTY",tmp_path); u=c.build_universe(20020,date(2026,1,1),hedge_distance=1); assert len(u.tokens)==13
 for contract in u.contracts: c.on_quote(Quote(contract.contract_id,datetime.now(timezone.utc),last=10,bid=9,ask=11))
 assert c.mark_positions()=={}
