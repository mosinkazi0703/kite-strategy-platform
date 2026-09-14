from kite_strategy_platform.config import load_config
from kite_strategy_platform.strategies.calendar_spread import CalendarConfig,DynamicCalendarSpread
from kite_strategy_platform.strategies.reversal_credit import ReversalCreditStrategy
def create_handlers(configs):
    handlers={}
    for raw in configs:
        if not raw.get("enabled"): continue
        s=raw.get("strategy",{}); sid=s.get("id")
        if sid=="dynamic_calendar_spread_v1": handlers[sid]=DynamicCalendarSpread(CalendarConfig(s.get("timeframe","weekly"),s.get("profit_target_pct",.05),s.get("iv_collapse_pct",.2),s.get("delta_threshold",.15),s.get("hedge_enabled",True)))
        elif sid=="reversal_credit_v1": handlers[sid]=ReversalCreditStrategy(load_config(raw["_path"]).strategy)
        else: raise ValueError(f"no live handler registered for {sid}")
    return handlers
