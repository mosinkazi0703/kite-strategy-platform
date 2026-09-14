from datetime import date,datetime,timezone
from kite_strategy_platform.runtime.bootstrap import MarketUniverse
from kite_strategy_platform.runtime.session import PaperSession
from kite_strategy_platform.runtime.lifecycle import PaperLifecycle
from kite_strategy_platform.domain.instruments import Contract
from kite_strategy_platform.domain.market_data import Quote
def test_two_strategy_paper_lifecycle(tmp_path):
 cs=[]
 for e in (date(2026,1,8),date(2026,1,15)):
  for s in (20000,20300,19700):
   for t in ("CE","PE"): cs.append(Contract("NFO",f"{e}{s}{t}",len(cs)+1,e,s,t,50,.05))
 u=MarketUniverse(None,20000,(date(2026,1,8),date(2026,1,15)),tuple(cs),tuple(c.instrument_token for c in cs)); l=PaperLifecycle(PaperSession(tmp_path),u)
 q={c.contract_id:Quote(c.contract_id,datetime.now(timezone.utc),last=10,bid=20 if c.strike==20000 else 9,ask=21 if c.strike==20000 else 11) for c in cs}
 l.reversal_entry("UP",q); l.calendar_entry(q); l.mark(q,datetime.now(timezone.utc),delta=.2); assert len(l.positions)==2
