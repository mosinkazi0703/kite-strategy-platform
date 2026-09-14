from dataclasses import dataclass
@dataclass
class AlgoInstance: id: str; handler: object; enabled: bool=True
class AlgoOrchestrator:
    def __init__(self,algos): self.algos=[a for a in algos if a.enabled]
    def on_candle(self,candle,opening_price,quotes):
        return {a.id:a.handler.on_candle(candle,opening_price,quotes) for a in self.algos}
    def on_quotes(self,quotes): return {a.id:a.handler.on_quotes(quotes) for a in self.algos if getattr(a.handler,"position",None)}
