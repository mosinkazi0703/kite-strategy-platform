from datetime import datetime, timezone
from zoneinfo import ZoneInfo
from kite_strategy_platform.runtime.composition import LivePaperComposition
from kite_strategy_platform.runtime.registry import create_handlers
from kite_strategy_platform.runtime.loader import load_enabled_strategies
from kite_strategy_platform.kite.instrument_service import InstrumentService

class PaperTradingCoordinator:
    """Two-stage unattended paper runtime. Real broker order APIs are never used."""
    def __init__(self,api_key,access_token,root="runtime",config_dir="config"):
        self.api_key=api_key; self.access_token=access_token; self.root=root; self.configs=load_enabled_strategies(config_dir); self.handlers=create_handlers(self.configs); self.session=None; self.composition=None; self.stage="INIT"
    def load_instruments(self,force=False):
        self.rows=InstrumentService(self.root).load_or_download(self.api_key,self.access_token,force); self.stage="INSTRUMENTS_LOADED"; return self.rows
    def subscribe_underlying_first(self):
        if not hasattr(self,"rows"): raise RuntimeError("instrument master must be loaded first")
        configured=self.configs[0]["strategy"]; symbol=configured["underlying"]
        exchange=configured.get("exchange","NSE")
        exact=[r for r in self.rows if r.get("tradingsymbol")==symbol and r.get("exchange")==exchange]
        index_50=[r for r in self.rows if r.get("tradingsymbol")==f"{symbol} 50" and r.get("exchange")==exchange]
        rows=exact or index_50
        if len(rows)!=1:
            candidates=[r.get("tradingsymbol") for r in self.rows if r.get("exchange")==exchange and symbol in r.get("tradingsymbol","")][:10]
            raise ValueError(f"expected one underlying contract for {symbol}, found {len(rows)}; candidates: {candidates}")
        self.underlying_token=int(rows[0]["instrument_token"]); self.stage="UNDERLYING_SUBSCRIBED"; return (self.underlying_token,)
    def capture_open(self,quote):
        if self.stage!="UNDERLYING_SUBSCRIBED": raise RuntimeError("underlying must be subscribed first")
        local=quote.timestamp.astimezone(ZoneInfo("Asia/Kolkata")).time()
        if (local.hour,local.minute)!=(9,15): raise ValueError("reference quote must be from 09:15 Asia/Kolkata")
        self.opening_price=quote.last; self.stage="OPEN_CAPTURED"; return self.opening_price
    def build_option_universe(self,today,timeframe="weekly",strike_step=None,hedge_distance=6):
        if self.stage!="OPEN_CAPTURED": raise RuntimeError("09:15 opening price required")
        symbol=self.configs[0]["strategy"]["underlying"]; self.composition=LivePaperComposition(self.rows,symbol,self.root); u=self.composition.build_universe(self.opening_price,today,timeframe,strike_step,hedge_distance); self.stage="OPTIONS_SUBSCRIBED"; return u
    def resolved_subscription_pairs(self, today):
        universe=self.build_option_universe(today)
        return [(c.instrument_token,c.contract_id) for c in universe.contracts]
    def start_paper(self):
        if self.stage!="OPTIONS_SUBSCRIBED": raise RuntimeError("option universe must be built first")
        self.stage="RUNNING"; return self.composition
    def on_underlying_quote(self, quote):
        if self.stage=="UNDERLYING_SUBSCRIBED" and quote.last is not None:
            local=quote.timestamp.astimezone(ZoneInfo("Asia/Kolkata"))
            if (local.hour,local.minute)==(9,15): return self.capture_open(quote)
        return None
