from kite_strategy_platform.runtime.application import UnattendedPaperApplication
def test_application_loads_all_enabled_algorithms(tmp_path):
    app=UnattendedPaperApplication([1],tmp_path)
    assert {x["strategy"]["id"] for x in app.configs if x["enabled"]}=={"reversal_credit_v1","dynamic_calendar_spread_v1"}
