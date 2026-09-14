from datetime import date,datetime,timezone
from kite_strategy_platform.runtime.lifecycle import PaperLifecycle
from kite_strategy_platform.runtime.session import PaperSession
from kite_strategy_platform.runtime.bootstrap import MarketUniverse
from kite_strategy_platform.domain.instruments import Contract
from kite_strategy_platform.domain.market_data import Quote
def test_target_exit_persists_trade(tmp_path):
 cs=[Contract("NFO",f"x{i}",i,date(2026,1,8),s,t,50,.05) for i,(s,t) in enumerate([(100,"CE"),(400,"CE"),(100,"PE"),(-200,"PE")])]
 u=MarketUniverse(None,100,(date(2026,1,8),date(2026,1,15)),tuple(cs),tuple(range(4))); s=PaperSession(tmp_path); l=PaperLifecycle(s,u)
 q={c.contract_id:Quote(c.contract_id,datetime.now(timezone.utc),last=10,bid=20 if c.strike==100 else 9,ask=21 if c.strike==100 else 11) for c in cs}; p=l.reversal_entry("UP",q)
 q={k:Quote(k,datetime.now(timezone.utc),last=0,bid=0,ask=0) for k in q}; l.mark(q,datetime.now(timezone.utc)); assert p.state=="CLOSED" and len(s.ledger.rows)==1
