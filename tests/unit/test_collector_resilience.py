from datetime import datetime, timedelta, timezone
from kite_strategy_platform.collector.live import LiveCollector
from kite_strategy_platform.domain.market_data import Quote
import kite_strategy_platform.collector.live as live_module

def test_candle_storage_failure_does_not_stop_quote_routing(tmp_path,monkeypatch):
    seen=[]; collector=LiveCollector([1],tmp_path,on_quote=seen.append)
    first=Quote("1",datetime(2026,1,1,9,15,tzinfo=timezone.utc),last=10)
    second=Quote("1",first.timestamp+timedelta(minutes=1),last=11)
    frames=iter([[first],[second]])
    monkeypatch.setattr(live_module,"decode_packets",lambda *_: next(frames))
    def fail(*_): raise PermissionError("locked")
    monkeypatch.setattr(collector.store,"append_parquet_part",fail)
    collector.on_frame(b"x","session"); collector.on_frame(b"x","session")
    assert seen == [first,second]
    assert collector.last_minute["1"] == second.timestamp.replace(second=0,microsecond=0)
    assert 'candle_storage_error' in (tmp_path/'logs'/'events.jsonl').read_text(encoding='utf-8')
