from kite_strategy_platform.runtime.session import PaperSession

def test_report_is_generated_from_its_ledger(tmp_path):
    session=PaperSession(tmp_path)
    session.record_trade({"record_id":"one","gross_pnl":100,"turnover":1000,"orders":2})
    report=session.report()
    assert report["trades"] == 1
    assert report["net_pnl"] == session.ledger.rows[0]["net_pnl"]
