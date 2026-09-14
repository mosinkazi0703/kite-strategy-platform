from datetime import date,time
import pytest
from kite_strategy_platform.domain.instruments import Contract
from kite_strategy_platform.strategies.calendar_spread import CalendarConfig,DynamicCalendarSpread
def test_expiry_selection_by_timeframe():
    e=[date(2026,1,8),date(2026,1,15),date(2026,2,26)]
    assert DynamicCalendarSpread(CalendarConfig("intraday")).select_expiries(e,date(2026,1,1))==(e[0],e[1])
    assert DynamicCalendarSpread(CalendarConfig("weekly")).select_expiries(e,date(2026,1,1))==(e[0],e[1])
    assert DynamicCalendarSpread(CalendarConfig("monthly")).select_expiries(e,date(2026,1,1))==(e[0],e[1])
def test_calendar_legs_buy_far_sell_near():
    cs=[Contract("NFO","near",1,date(2026,1,8),20000,"CE",50,.05),Contract("NFO","far",2,date(2026,1,15),20000,"CE",50,.05)]
    legs=DynamicCalendarSpread(CalendarConfig()).build_legs(cs,20000,date(2026,1,8),date(2026,1,15)); assert [x.side for x in legs]==["BUY","SELL"]
def test_delta_hedge_and_exits():
    s=DynamicCalendarSpread(CalendarConfig("intraday",.05,.2,.15,True))
    assert s.hedge_required(.2) and not s.hedge_required(.1)
    assert s.exit_reason(.01,-.25, time(14,0),None,time(15,15))=="IV_COLLAPSE"
    assert s.exit_reason(.01,0,time(15,16),None,time(15,15))=="MARKET_CLOSE"
def test_bad_timeframe_rejected():
    with pytest.raises(ValueError): DynamicCalendarSpread(CalendarConfig("daily")).select_expiries([date(2026,1,8),date(2026,1,15)],date(2026,1,1))
