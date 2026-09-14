from kite_strategy_platform.runtime.loader import load_enabled_strategies
from kite_strategy_platform.runtime.registry import create_handlers
def test_registry_creates_both_strategy_handlers():
    handlers=create_handlers(load_enabled_strategies("config")); assert set(handlers)=={"reversal_credit_v1","dynamic_calendar_spread_v1"}
