from kite_strategy_platform.engines.paper_engine import PaperTradingEngine
from kite_strategy_platform.execution.paper_broker import PaperBroker
from kite_strategy_platform.execution.fill_model import BidAskFillModel
from kite_strategy_platform.strategies.legs import build_four_legs
class PaperLifecycle:
    def __init__(self,session,universe,target=1.0,stop=.3): self.session=session; self.universe=universe; self.engine=PaperTradingEngine(PaperBroker(BidAskFillModel()),target,stop); self.positions={}
    def reversal_entry(self,direction,quotes):
        contracts=[c for c in self.universe.contracts if c.expiry==self.universe.expiries[0]]; legs=build_four_legs(direction,self.universe.atm_strike,self.universe.atm_strike,6,50,contracts); p=self.engine.open(legs,quotes); self.positions["reversal_credit_v1"]=p; return p
    def calendar_entry(self,quotes):
        from kite_strategy_platform.strategies.calendar_spread import DynamicCalendarSpread,CalendarConfig
        near,far=self.universe.expiries[:2]; legs=DynamicCalendarSpread(CalendarConfig()).build_legs(self.universe.contracts,self.universe.atm_strike,near,far); p=PaperTradingEngine(PaperBroker(BidAskFillModel()),allow_debit=True).open(legs,quotes); self.positions["dynamic_calendar_spread_v1"]=p; return p
    def mark(self,quotes,now,iv_change=0,delta=0):
        for sid,p in self.positions.items():
            prices={k:quotes[k].last for k in p.entries if k in quotes}; pnl=p.pnl_points(prices)
            if pnl is not None: self.session.event("mark",strategy_id=sid,pnl=pnl,iv_change=iv_change,delta=delta,state=p.state)
