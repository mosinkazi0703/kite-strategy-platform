from dataclasses import dataclass, field
from kite_strategy_platform.domain.orders import OrderIntent
@dataclass
class Position:
    legs: list; entries: dict = field(default_factory=dict); state: str = "OPEN"; exit_reason: str|None=None
    def pnl_points(self, prices):
        total=0
        for leg in self.legs:
            if leg.contract.contract_id not in prices: self.state="DATA_INCOMPLETE"; return None
            diff=prices[leg.contract.contract_id]-self.entries[leg.contract.contract_id]
            total += -diff if leg.side=="SELL" else diff
        return total
class PaperTradingEngine:
    def __init__(self, broker, target=1.0, stop=0.3): self.broker=broker; self.target=target; self.stop=stop
    def open(self, legs, quotes):
        entries={}
        for leg in legs:
            fill=self.broker.fill(OrderIntent(leg.contract.contract_id,leg.side,leg.quantity),quotes.get(leg.contract.contract_id)) if quotes.get(leg.contract.contract_id) else None
            if not fill: raise ValueError(f"missing executable entry quote: {leg.contract.contract_id}")
            entries[leg.contract.contract_id]=fill.price
        credit=sum(entries[l.contract.contract_id] * (-1 if l.side=="BUY" else 1) for l in legs)
        if credit<=0: raise ValueError("non-positive net credit")
        return Position(legs,entries)
