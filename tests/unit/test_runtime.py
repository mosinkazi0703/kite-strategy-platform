from kite_strategy_platform.runtime.loader import load_enabled_strategies
from kite_strategy_platform.runtime.session import PaperSession
def test_all_strategy_configs_are_discoverable():
    ids=[x["strategy"]["id"] for x in load_enabled_strategies("config") if x["enabled"]]
    assert "reversal_credit_v1" in ids and "dynamic_calendar_spread_v1" in ids
def test_session_writes_report(tmp_path):
    s=PaperSession(tmp_path); s.record_trade({"gross_pnl":100,"turnover":0,"orders":0}); assert s.report()["net_pnl"]==100
