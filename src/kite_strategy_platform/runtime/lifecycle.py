from kite_strategy_platform.engines.paper_engine import PaperTradingEngine
from kite_strategy_platform.execution.paper_broker import PaperBroker
from kite_strategy_platform.execution.fill_model import BidAskFillModel
from kite_strategy_platform.strategies.legs import build_four_legs
class PaperLifecycle:
    def __init__(self,session,universe,target=1.0,stop=.3,margin_client=None,max_margin=None):
        self.session=session; self.universe=universe; self.margin_client=margin_client; self.max_margin=max_margin
        self.engine=PaperTradingEngine(PaperBroker(BidAskFillModel()),target,stop,margin_client,max_margin); self.positions={}
    def _record_entry(self,sid,p):
        self.session.event("paper_entry",strategy_id=sid,margin_required=p.margin_required,margin_details=p.margin,initial_cashflow_rupees=p.initial_cashflow_rupees())
    def reversal_entry(self,direction,quotes):
        contracts=[c for c in self.universe.contracts if c.expiry==self.universe.expiries[0]]; legs=build_four_legs(direction,self.universe.atm_strike,self.universe.atm_strike,6,50,contracts); p=self.engine.open(legs,quotes); self.positions["reversal_credit_v1"]=p; self._record_entry("reversal_credit_v1",p); return p
    def calendar_entry(self,quotes):
        from kite_strategy_platform.strategies.calendar_spread import DynamicCalendarSpread,CalendarConfig
        near,far=self.universe.expiries[:2]; legs=DynamicCalendarSpread(CalendarConfig()).build_legs(self.universe.contracts,self.universe.atm_strike,near,far); p=PaperTradingEngine(PaperBroker(BidAskFillModel()),margin_client=self.margin_client,max_margin=self.max_margin,allow_debit=True).open(legs,quotes); self.positions["dynamic_calendar_spread_v1"]=p; self._record_entry("dynamic_calendar_spread_v1",p); return p
    def close(self,sid,p,reason,pnl):
        if p.state=="CLOSED": return
        p.state="CLOSED"; p.exit_reason=reason
        self.session.record_trade({"record_id":f"{sid}:{id(p)}","strategy_id":sid,"gross_pnl":pnl,"orders":len(p.legs)*2,"turnover":sum(p.entries[leg.contract.contract_id]*leg.quantity for leg in p.legs),"exit_reason":reason,"margin_required":p.margin_required,"margin_details":p.margin})
        self.session.event("exit",strategy_id=sid,reason=reason,gross_pnl_rupees=pnl)
    def mark(self,quotes,now,iv_change=0,delta=0):
        for sid,p in self.positions.items():
            if p.state=="CLOSED": continue
            prices={k:quotes[k].last for k in p.entries if k in quotes}; points=p.pnl_points(prices); pnl=p.pnl_rupees(prices)
            if pnl is None: continue
            credit=p.initial_cashflow_rupees()
            reason="TARGET" if pnl>=abs(credit)*self.engine.target else "STOP" if pnl<=-abs(credit)*self.engine.stop else None
            expiry=min(l.contract.expiry for l in p.legs if l.contract.expiry)
            if not reason and now.date()>=expiry and now.time().hour>=15 and now.time().minute>=20: reason="EXPIRY_HARD_EXIT"
            if sid=="dynamic_calendar_spread_v1" and iv_change<=-.20: reason=reason or "IV_COLLAPSE"
            if sid=="dynamic_calendar_spread_v1" and abs(delta)>=.15: self.session.event("hedge",strategy_id=sid,delta=delta,action="SIMULATED_FUTURES_HEDGE")
            if reason: self.close(sid,p,reason,pnl)
            self.session.event("mark",strategy_id=sid,pnl_points=points,gross_pnl_rupees=pnl,margin_required=p.margin_required,iv_change=iv_change,delta=delta,state=p.state)
