from datetime import datetime
from kite_strategy_platform.domain.market_data import Candle, Quote
from kite_strategy_platform.execution.fill_model import BidAskFillModel
from kite_strategy_platform.execution.paper_broker import PaperBroker
from kite_strategy_platform.engines.paper_engine import PaperTradingEngine
from kite_strategy_platform.strategies.legs import build_four_legs
from kite_strategy_platform.runtime.session import PaperSession
def run_synthetic_paper(root="runtime"):
    session=PaperSession(root); session.event("synthetic_start")
    from kite_strategy_platform.domain.instruments import Contract
    from datetime import date
    cs=[Contract("NFO",f"{s}{t}",i,date(2026,1,8),s,t,50,.05) for i,(s,t) in enumerate([(100,"CE"),(106,"CE"),(100,"PE"),(94,"PE")])]
    legs=build_four_legs("UP",100,100,6,1,cs)
    quotes={l.contract.contract_id:Quote(l.contract.contract_id,datetime(2026,1,1,10),last=10,bid=20 if l.side=="SELL" else 9,ask=21 if l.side=="SELL" else 11) for l in legs}
    position=PaperTradingEngine(PaperBroker(BidAskFillModel())).open(legs,quotes)
    session.record_trade({"strategy_id":"reversal_credit_v1","status":"CLOSED","gross_pnl":0,"turnover":sum(q.last*q.volume for q in quotes.values()),"orders":len(legs),"margin_required":None})
    session.event("synthetic_complete",state=position.state); return session.report()
