from datetime import date,datetime
from kite_strategy_platform.domain.instruments import Contract
from kite_strategy_platform.domain.market_data import Quote
from kite_strategy_platform.execution.fill_model import BidAskFillModel
from kite_strategy_platform.execution.paper_broker import PaperBroker
from kite_strategy_platform.engines.paper_engine import PaperTradingEngine
from kite_strategy_platform.strategies.legs import build_four_legs
class FakeMargin:
    def margin_for_legs(self,legs): return {"initial":100000,"final":50000,"total":50000}
def test_margin_recorded_and_limit_enforced():
    cs=[Contract("NFO",f"{s}{t}",i,date(2026,1,8),s,t,50,.05) for i,(s,t) in enumerate([(100,"CE"),(106,"CE"),(100,"PE"),(94,"PE")])]
    legs=build_four_legs("UP",100,100,6,1,cs); qs={l.contract.contract_id:Quote(l.contract.contract_id,datetime.now(),bid=20 if l.side=="SELL" else 9,ask=21 if l.side=="SELL" else 11) for l in legs}
    pos=PaperTradingEngine(PaperBroker(BidAskFillModel()),margin_client=FakeMargin()).open(legs,qs); assert pos.margin["final"]==50000
    try: PaperTradingEngine(PaperBroker(BidAskFillModel()),margin_client=FakeMargin(),max_margin=49999).open(legs,qs)
    except ValueError as e: assert "margin limit" in str(e)
    else: assert False
