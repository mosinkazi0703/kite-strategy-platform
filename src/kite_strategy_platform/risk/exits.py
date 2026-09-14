from datetime import datetime, time
def forced_exit_reason(now, expiry, entry_date, intraday_only=False, expiry_time=time(15,20), next_day_time=time(9,20)):
    if expiry and now.date()==expiry and now.time()>=expiry_time: return "EXPIRY_HARD_EXIT"
    if intraday_only and now.date()==entry_date and now.time()>=expiry_time: return "INTRADAY_HARD_EXIT"
    if not intraday_only and now.date()>entry_date and now.time()>=next_day_time: return "NEXT_DAY_HARD_EXIT"
    return None
