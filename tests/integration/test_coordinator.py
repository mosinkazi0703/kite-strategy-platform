from datetime import datetime,timezone,date
from kite_strategy_platform.runtime.coordinator import PaperTradingCoordinator
from kite_strategy_platform.domain.market_data import Quote
def test_coordinator_enforces_two_stage_startup(tmp_path):
    c=PaperTradingCoordinator("key","token",tmp_path); c.rows=[{"exchange":"NSE","tradingsymbol":"NIFTY","instrument_token":"1","expiry":"","strike":"","instrument_type":"EQ","lot_size":"1","tick_size":".05","name":"NIFTY"}]
    assert c.subscribe_underlying_first()==(1,)
    q=Quote("1",datetime(2026,1,1,3,45,tzinfo=timezone.utc),last=20000)
    assert c.capture_open(q)==20000

def test_coordinator_accepts_kite_index_display_symbol(tmp_path):
    c=PaperTradingCoordinator("key","token",tmp_path); c.rows=[{"exchange":"NSE","tradingsymbol":"NIFTY 50","instrument_token":"256265","expiry":"","strike":"","instrument_type":"EQ","lot_size":"1","tick_size":".05","name":"NIFTY 50"}]
    assert c.subscribe_underlying_first()==(256265,)
