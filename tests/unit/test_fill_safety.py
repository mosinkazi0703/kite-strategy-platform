from datetime import datetime
from kite_strategy_platform.domain.market_data import Quote
from kite_strategy_platform.domain.orders import OrderIntent
from kite_strategy_platform.execution.fill_model import BidAskFillModel
def test_rejects_corrupt_executable_quote():
    q=Quote("x",datetime.now(),last=100,bid=1000000,ask=101)
    assert BidAskFillModel().fill(OrderIntent("x","BUY",1),q) is None
