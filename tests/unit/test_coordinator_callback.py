from datetime import datetime,timezone
from kite_strategy_platform.runtime.coordinator import PaperTradingCoordinator
from kite_strategy_platform.domain.market_data import Quote
def test_underlying_callback_captures_0915_ist(tmp_path):
    c=PaperTradingCoordinator("x","y",tmp_path); c.rows=[{"exchange":"NSE","tradingsymbol":"NIFTY","instrument_token":"1","expiry":"","strike":"","instrument_type":"EQ","lot_size":"1","tick_size":".05","name":"NIFTY"}]; c.subscribe_underlying_first()
    assert c.on_underlying_quote(Quote("1",datetime(2026,1,1,3,45,tzinfo=timezone.utc),last=20000))==20000
