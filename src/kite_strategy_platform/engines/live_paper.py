from datetime import time
from kite_strategy_platform.domain.orders import OrderIntent
class LivePaperStrategy:
    def __init__(self, strategy, engine, legs_factory): self.strategy=strategy; self.engine=engine; self.legs_factory=legs_factory; self.position=None; self.opening_price=None
    def on_candle(self,candle,opening_price,quotes):
        if self.position: return self.on_quotes(quotes)
        signal=self.strategy.trigger(opening_price,candle)
        if signal and signal.direction in ("UP","DOWN"):
            legs=self.legs_factory(signal.direction); self.position=self.engine.open(legs,quotes); return {"event":"entry","direction":signal.direction}
    def on_quotes(self,quotes):
        prices={k:(q.last if q and q.last is not None else None) for k,q in quotes.items()}
        if any(v is None for v in prices.values()): self.position.state="DATA_INCOMPLETE"; return {"event":"data_incomplete"}
        pnl=self.position.pnl_points(prices)
        if pnl is None: return {"event":"data_incomplete"}
        credit=sum(self.position.entries[l.contract.contract_id] * (-1 if l.side=="BUY" else 1) for l in self.position.legs)
        if pnl >= credit*self.engine.target: self.position.state="CLOSED"; self.position.exit_reason="TARGET"
        elif pnl <= -credit*self.engine.stop: self.position.state="CLOSED"; self.position.exit_reason="STOP"
        return {"event":"mark","pnl_points":pnl,"state":self.position.state}
