from datetime import date, datetime
import pytest
from kite_strategy_platform.domain.instruments import Contract
from kite_strategy_platform.domain.market_data import Quote
from kite_strategy_platform.domain.orders import OrderIntent
from kite_strategy_platform.strategies.legs import build_four_legs
from kite_strategy_platform.execution.fill_model import BidAskFillModel
from kite_strategy_platform.execution.paper_broker import PaperBroker
from kite_strategy_platform.engines.paper_engine import PaperTradingEngine

def contracts():
    out=[]
    for strike,typ in [(100,"CE"),(106,"CE"),(100,"PE"),(94,"PE")]: out.append(Contract("NFO",f"{strike}{typ}",strike,date(2026,1,8),strike,typ,50,.05))
    return out
def test_up_and_down_build_four_legs():
    cs=contracts(); assert len(build_four_legs("UP",100,100,6,1,cs))==4; assert len(build_four_legs("DOWN",100,100,6,1,cs))==4
def test_unhedged_builds_only_short_legs():
    assert len(build_four_legs("UP",100,100,6,1,contracts(),hedge=False))==2
def test_missing_contract_is_rejected():
    with pytest.raises(ValueError): build_four_legs("UP",100,100,6,1,contracts()[:2])
def test_paper_engine_requires_executable_quotes_and_calculates_credit():
    legs=build_four_legs("UP",100,100,6,1,contracts()); q={l.contract.contract_id:Quote(l.contract.contract_id,datetime(2026,1,1,10),last=10,bid=20 if l.side=="SELL" else 9,ask=21 if l.side=="SELL" else 11) for l in legs}
    pos=PaperTradingEngine(PaperBroker(BidAskFillModel())).open(legs,q)
    assert pos.state=="OPEN" and pos.pnl_points({k:10 for k in q})==0
    del q[legs[0].contract.contract_id]
    with pytest.raises(ValueError, match="missing executable"): PaperTradingEngine(PaperBroker(BidAskFillModel())).open(legs,q)
def test_fill_model_uses_ask_for_buy_bid_for_sell():
    m=BidAskFillModel(slippage_ticks=1,tick_size=.05); q=Quote("x",datetime.now(),bid=9,ask=11)
    assert m.fill(OrderIntent("x","BUY",1),q).price==pytest.approx(11.05)
    assert m.fill(OrderIntent("x","SELL",1),q).price==pytest.approx(8.95)
