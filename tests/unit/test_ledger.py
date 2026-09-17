from kite_strategy_platform.reporting.ledger import TradeLedger

def test_duplicate_record_id_is_not_recorded_twice():
    ledger=TradeLedger()
    assert ledger.record({"record_id":"position-1","gross_pnl":10,"turnover":100,"orders":1}) is not None
    assert ledger.record({"record_id":"position-1","gross_pnl":10,"turnover":100,"orders":1}) is None
    assert len(ledger.rows)==1
