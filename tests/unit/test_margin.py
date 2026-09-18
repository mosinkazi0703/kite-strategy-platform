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

def test_position_pnl_rupees_uses_leg_quantity():
    cs=[Contract("NFO","x",1,date(2026,1,8),100,"CE",50,.05)]
    from kite_strategy_platform.strategies.legs import Leg
    cid=cs[0].contract_id
    position=PaperTradingEngine(PaperBroker(BidAskFillModel()),allow_debit=True).open([Leg(cs[0],"BUY",50)],{cid:Quote(cid,datetime.now(),last=10,bid=9,ask=10)})
    assert position.pnl_points({cid:12}) == 2
    assert position.pnl_rupees({cid:12}) == 100

def test_nested_kite_basket_margin_uses_final_total():
    class NestedMargin:
        def margin_for_legs(self,_): return {"initial":{"total":100000},"final":{"total":50000}}
    cs=[Contract("NFO","x",1,date(2026,1,8),100,"CE",50,.05)]
    from kite_strategy_platform.strategies.legs import Leg
    cid=cs[0].contract_id; quote=Quote(cid,datetime.now(),last=10,bid=9,ask=10)
    position=PaperTradingEngine(PaperBroker(BidAskFillModel()),margin_client=NestedMargin(),max_margin=50000,allow_debit=True).open([Leg(cs[0],"BUY",50)],{cid:quote})
    assert position.margin_required == 50000.0
