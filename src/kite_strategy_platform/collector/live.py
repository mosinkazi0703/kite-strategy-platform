import os
from datetime import datetime, timezone
from .storage import AppendOnlyStore
from .candle_builder import MinuteCandleBuilder
from kite_strategy_platform.kite.websocket_client import KiteWebSocketClient
from kite_strategy_platform.kite.tick_decoder import decode_packets
class LiveCollector:
    def __init__(self,tokens,root="runtime",mode="full",on_quote=None,on_candle=None):
        self.tokens=tokens; self.store=AppendOnlyStore(root); self.builder=MinuteCandleBuilder(); self.sequence=0; self.token_to_contract={t:str(t) for t in tokens}; self.mode=mode; self.last_minute={}; self.on_quote=on_quote; self.on_candle=on_candle
    def on_frame(self,frame,session_id):
        rows=[]
        for q in decode_packets(frame,self.token_to_contract):
            self.sequence+=1; rows.append({"schema_version":"1.0","received_at_utc":q.timestamp.isoformat(),"contract_id":q.contract_id,"last_price":q.last,"bid":q.bid,"ask":q.ask,"volume":q.volume,"open_interest":q.open_interest,"session_id":session_id,"sequence":self.sequence}); self.builder.add(q)
            if self.on_quote: self.on_quote(q)
            minute=q.timestamp.replace(second=0,microsecond=0); previous=self.last_minute.get(q.contract_id)
            if previous and previous < minute:
                candle=self.builder.close(q.contract_id,previous)
                if candle:
                    day=previous.date().isoformat(); self.store.append_table(f"data/candles/interval=1minute/trading_date={day}/candles.parquet",[candle.__dict__])
                    if self.on_candle: self.on_candle(candle)
            self.last_minute[q.contract_id]=minute
        if rows: self.store.append_jsonl("data/raw_ticks/ticks.jsonl",rows)
    def run(self):
        self.store.append_jsonl("logs/events.jsonl",[{"event":"collector_start","at":datetime.now(timezone.utc).isoformat()}])
        KiteWebSocketClient(os.environ["KITE_API_KEY"],os.environ["KITE_ACCESS_TOKEN"],self.on_frame).run(self.tokens,self.mode)
