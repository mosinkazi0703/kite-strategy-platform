from dataclasses import dataclass
from datetime import datetime
from typing import Sequence

@dataclass(frozen=True)
class Quote:
    contract_id: str; timestamp: datetime; last: float | None = None
    bid: float | None = None; ask: float | None = None; volume: int = 0; open_interest: int | None = None
    depth: tuple = ()
    @property
    def executable_buy(self): return self.ask
    @property
    def executable_sell(self): return self.bid

@dataclass(frozen=True)
class Candle:
    contract_id: str; start: datetime; open: float; high: float; low: float; close: float
    source: str = "websocket"; tick_count: int = 0; complete: bool = True
