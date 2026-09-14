from dataclasses import dataclass
from datetime import date, timedelta
from kite_strategy_platform.strategies.legs import Leg

@dataclass(frozen=True)
class CalendarConfig:
    timeframe: str="weekly"; profit_target_pct: float=.05; iv_collapse_pct: float=.20; delta_threshold: float=.15; hedge_enabled: bool=True

class DynamicCalendarSpread:
    """Paper-only calendar spread: buy farther expiry, sell nearer expiry."""
    def __init__(self, config: CalendarConfig): self.config=config
    def select_expiries(self, expiries, today):
        valid=sorted(x for x in expiries if x>=today)
        if len(valid)<2: raise ValueError("at least two future expiries are required")
        if self.config.timeframe=="intraday": return valid[0],valid[1]
        if self.config.timeframe=="weekly":
            month=valid[0].month; same=[x for x in valid if x.month==month]
            return (same[0],same[1]) if len(same)>1 else (valid[0],valid[1])
        if self.config.timeframe=="monthly": return valid[0],valid[1]
        raise ValueError("timeframe must be intraday, weekly, or monthly")
    def build_legs(self, contracts, strike, near, far, lots=1):
        def find(expiry):
            x=[c for c in contracts if c.expiry==expiry and c.strike==strike and c.option_type=="CE"]
            if len(x)!=1: raise ValueError(f"expected one CE contract for {expiry} {strike}")
            return x[0]
        return [Leg(find(far),"BUY",find(far).lot_size*lots),Leg(find(near),"SELL",find(near).lot_size*lots)]
    def hedge_required(self, net_delta):
        return self.config.hedge_enabled and abs(net_delta)>=self.config.delta_threshold
    def exit_reason(self, pnl_pct, iv_change_pct, now, expiry, market_close):
        if pnl_pct>=self.config.profit_target_pct: return "PROFIT_TARGET"
        if iv_change_pct<=-self.config.iv_collapse_pct: return "IV_COLLAPSE"
        if self.config.timeframe=="intraday" and now>=market_close: return "MARKET_CLOSE"
        return None
