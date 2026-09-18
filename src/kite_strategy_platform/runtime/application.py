import signal
from .loader import load_enabled_strategies
from .session import PaperSession
from kite_strategy_platform.collector.live import LiveCollector
from .registry import create_handlers
class UnattendedPaperApplication:
    def __init__(self,tokens,root="runtime",config_dir="config"):
        self.session=PaperSession(root); self.configs=load_enabled_strategies(config_dir); self.last_quotes={}
        self._stopping=False
        self.handlers=create_handlers(self.configs); self.collector=LiveCollector(tokens,root,on_quote=self.on_quote,on_candle=self.on_candle)
        for x in self.configs:
            if x.get("enabled"): self.session.event("strategy_loaded",strategy_id=x.get("strategy",{}).get("id"),config=x["_path"])
    def on_quote(self,quote): self.last_quotes[quote.contract_id]=quote
    def on_candle(self,candle):
        for sid,handler in self.handlers.items():
            self.session.event("candle_routed",strategy_id=sid,contract_id=candle.contract_id,start=candle.start.isoformat())
    def stop(self,*_):
        if self._stopping: return
        self._stopping=True; self.session.event("shutdown",reason="signal"); self.collector.stop()
    def run(self):
        signal.signal(signal.SIGINT,self.stop); signal.signal(signal.SIGTERM,self.stop); self.session.event("paper_session_start",strategies=[x.get("strategy",{}).get("id") for x in self.configs if x.get("enabled")])
        try: self.collector.run()
        finally: self.session.report()
