from datetime import date, datetime
from kite_strategy_platform.risk.exits import forced_exit_reason
from kite_strategy_platform.reporting.ledger import TradeLedger
from kite_strategy_platform.reporting.costs import CostModel
def test_expiry_and_next_day_exits():
    assert forced_exit_reason(datetime(2026,1,8,15,20),date(2026,1,8),date(2026,1,8))=="EXPIRY_HARD_EXIT"
    assert forced_exit_reason(datetime(2026,1,9,9,20),date(2026,1,8),date(2026,1,8))=="NEXT_DAY_HARD_EXIT"
def test_costs_and_net_ledger():
    row=TradeLedger(CostModel(10,.01,0)).record({"gross_pnl":100,"turnover":1000,"orders":2})
    assert row["costs"]==30 and row["net_pnl"]==70
