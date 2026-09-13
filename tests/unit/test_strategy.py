from datetime import datetime
from kite_strategy_platform.config import load_config
from kite_strategy_platform.domain.market_data import Candle
from kite_strategy_platform.strategies.reversal_credit import ReversalCreditStrategy

def test_triggers_and_ambiguous():
    c=load_config("config/strategy_reversal_credit.yaml", "config/paper_trading.yaml")
    s=ReversalCreditStrategy(c.strategy)
    def candle(h,l): return Candle("x", datetime(2026,1,1,10,0), 100, h, l, 100)
    assert s.trigger(100, candle(100.6,100)).direction == "UP"
    assert s.trigger(100, candle(100.6,99.4)).direction == "AMBIGUOUS_TRIGGER"
