from collections import defaultdict
from datetime import datetime
from kite_strategy_platform.domain.market_data import Candle, Quote

class MinuteCandleBuilder:
    def __init__(self): self._ticks=defaultdict(list)
    def add(self, quote: Quote) -> Candle | None:
        key=(quote.contract_id, quote.timestamp.replace(second=0,microsecond=0)); self._ticks[key].append(quote)
        return None
    def close(self, contract_id: str, minute: datetime) -> Candle | None:
        ticks=self._ticks.pop((contract_id,minute.replace(second=0,microsecond=0)), [])
        prices=[t.last for t in ticks if t.last is not None]
        if not prices: return None
        return Candle(contract_id, minute.replace(second=0,microsecond=0), prices[0], max(prices), min(prices), prices[-1], tick_count=len(prices))
