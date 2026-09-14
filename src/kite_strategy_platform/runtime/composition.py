from datetime import datetime, timezone
from kite_strategy_platform.runtime.session import PaperSession
from kite_strategy_platform.runtime.bootstrap import MarketBootstrap
from kite_strategy_platform.execution.fill_model import BidAskFillModel
from kite_strategy_platform.execution.paper_broker import PaperBroker
from kite_strategy_platform.engines.paper_engine import PaperTradingEngine

class LivePaperComposition:
    """Deterministic composition layer shared by live and synthetic feeds."""
    def __init__(self, rows, underlying, root="runtime", max_quote_age_seconds=5, margin_client=None):
        self.session=PaperSession(root); self.bootstrap=MarketBootstrap(rows,underlying); self.quotes={}; self.handlers=[]; self.max_age=max_quote_age_seconds; self.margin_client=margin_client
    def build_universe(self, spot, today, timeframe="weekly", strike_step=None, hedge_distance=6):
        self.universe=self.bootstrap.build(spot,today,timeframe,strike_step,hedge_distance); self.tokens=self.universe.tokens; self.session.event("universe_resolved",atm=self.universe.atm_strike,expiries=self.universe.expiries,tokens=self.tokens); return self.universe
    def on_quote(self, quote): self.quotes[quote.contract_id]=quote
    def fresh_quotes(self, contract_ids, now=None):
        now=now or datetime.now(timezone.utc); result={}
        for cid in contract_ids:
            q=self.quotes.get(cid)
            if q and (now-q.timestamp).total_seconds()<=self.max_age: result[cid]=q
        return result
    def open_position(self, strategy_id, legs, now=None):
        ids=[x.contract.contract_id for x in legs]; quotes=self.fresh_quotes(ids,now)
        if len(quotes)!=len(ids): self.session.event("entry_rejected",strategy_id=strategy_id,reason="STALE_OR_MISSING_QUOTE"); return None
        engine=PaperTradingEngine(PaperBroker(BidAskFillModel()),margin_client=self.margin_client)
        position=engine.open(legs,quotes); self.session.positions[strategy_id]=position
        self.session.event("paper_entry",strategy_id=strategy_id,margin=getattr(position,"margin",None)); return position
    def mark_positions(self, now=None):
        now=now or datetime.now(timezone.utc); results={}
        for sid,pos in list(self.session.positions.items()):
            quotes=self.fresh_quotes([l.contract.contract_id for l in pos.legs],now)
            if len(quotes)!=len(pos.legs): pos.state="DATA_INCOMPLETE"; results[sid]="DATA_INCOMPLETE"; continue
            prices={k:q.last for k,q in quotes.items()}; pnl=pos.pnl_points(prices); results[sid]=pnl
            self.session.event("position_mark",strategy_id=sid,pnl_points=pnl,state=pos.state)
        return results
