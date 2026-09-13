from kite_strategy_platform.engines.paper_engine import PaperTradingEngine
class BacktestEngine:
    def __init__(self, strategy, execution): self.strategy=strategy; self.execution=execution; self.trades=[]
    def run(self, candles, opening_price):
        for candle in candles:
            trigger=self.strategy.trigger(opening_price,candle)
            if trigger and trigger.direction != "AMBIGUOUS_TRIGGER": self.trades.append({"time":candle.start,"direction":trigger.direction,"entry_after":candle.start})
        return self.trades
