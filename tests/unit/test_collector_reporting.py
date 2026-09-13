from datetime import datetime
from kite_strategy_platform.collector.candle_builder import MinuteCandleBuilder
from kite_strategy_platform.domain.market_data import Quote
from kite_strategy_platform.reporting.report import summarize
from kite_strategy_platform.sweeps import parameter_sweep

def test_candle_builder_aggregates_and_empty_minute_is_missing():
    b=MinuteCandleBuilder(); t=datetime(2026,1,1,10,0,4)
    b.add(Quote("x",t,last=10)); b.add(Quote("x",t.replace(second=40),last=12))
    c=b.close("x",t); assert (c.open,c.high,c.low,c.close,c.tick_count)==(10,12,10,12,2)
    assert b.close("x",t.replace(minute=1)) is None
def test_reporting_keeps_unresolved_out_of_resolved_count():
    r=summarize([{"pnl":10},{"pnl":-5},{"pnl":None}]); assert r["trade_count"]==2 and r["unresolved_count"]==1 and r["gross_pnl"]==5
def test_parameter_sweep_runs_cartesian_matrix():
    r=parameter_sweep({"base":1},{"target":[.5,1],"hedge":[True,False]},lambda c:c["target"])
    assert len(r)==4
