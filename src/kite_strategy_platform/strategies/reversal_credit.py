from dataclasses import dataclass
from datetime import datetime, time
from kite_strategy_platform.domain.market_data import Candle

@dataclass(frozen=True)
class Trigger:
    direction: str; candle: Candle; reason: str = "threshold_reached"

class ReversalCreditStrategy:
    """Pure trigger logic; execution is injected by paper/backtest engines."""
    def __init__(self, config): self.config = config
    def trigger(self, opening_price: float, candle: Candle) -> Trigger | None:
        t = candle.start.timetz().replace(tzinfo=None)
        start = time.fromisoformat(self.config.trigger.scan_start)
        cutoff = time.fromisoformat(self.config.trigger.entry_cutoff)
        if not (start <= t < cutoff): return None
        upper = opening_price * (1 + self.config.trigger.percentage)
        lower = opening_price * (1 - self.config.trigger.percentage)
        up, down = candle.high >= upper, candle.low <= lower
        if up and down: return Trigger("AMBIGUOUS_TRIGGER", candle, "both_thresholds_touched")
        if up: return Trigger("UP", candle)
        if down: return Trigger("DOWN", candle)
        return None
