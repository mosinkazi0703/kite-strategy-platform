from datetime import datetime
from kite_strategy_platform.config import load_config
from kite_strategy_platform.domain.market_data import Candle
from kite_strategy_platform.strategies.reversal_credit import ReversalCreditStrategy

def strategy(): return ReversalCreditStrategy(load_config("config/strategy_reversal_credit.yaml","config/paper_trading.yaml").strategy)
def candle(hour, high, low): return Candle("x",datetime(2026,1,1,hour,0),100,high,low,100)
def test_scan_boundaries_and_next_candle_only():
    s=strategy(); assert s.trigger(100,candle(9,101,99)) is None
    assert s.trigger(100,candle(10,100.5,100)).direction=="UP"
    assert s.trigger(100,candle(14,100.5,100)).direction=="UP"
    assert s.trigger(100,candle(14,100.5,99.4)).direction=="AMBIGUOUS_TRIGGER"
