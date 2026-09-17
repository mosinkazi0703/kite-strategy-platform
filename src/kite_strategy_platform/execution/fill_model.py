from dataclasses import dataclass
@dataclass(frozen=True)
class Fill: price: float; quantity: int; slippage: float = 0
class BidAskFillModel:
    def __init__(self, slippage_ticks=0, tick_size=0.05): self.slippage_ticks=slippage_ticks; self.tick_size=tick_size
    def fill(self, intent, quote):
        if quote is None: return None
        if quote.bid is None or quote.ask is None or quote.bid <= 0 or quote.ask <= 0 or quote.bid > quote.ask: return None
        if quote.last is not None and (quote.last <= 0 or quote.bid > quote.last * 5 or quote.ask > quote.last * 5 or quote.ask < quote.last / 5): return None
        price = quote.executable_buy if intent.side == "BUY" else quote.executable_sell
        if price is None: return None
        slip = self.slippage_ticks * self.tick_size
        return Fill(price + slip if intent.side == "BUY" else price - slip, intent.quantity, slip)
