from datetime import date
from kite_strategy_platform.domain.instruments import Contract
from kite_strategy_platform.kite.instrument_master import to_contract

def test_contract_identity_keeps_expiry_distinct():
    a=Contract("NFO","NIFTYCE",1,date(2026,1,1),25000,"CE",65,.05)
    b=Contract("NFO","NIFTYCE",2,date(2026,1,8),25000,"CE",65,.05)
    assert a.contract_id != b.contract_id
def test_instrument_row_uses_metadata():
    c=to_contract({"exchange":"NFO","tradingsymbol":"X","instrument_token":"4","expiry":"2026-01-08","strike":"25000","instrument_type":"CE","lot_size":"75","tick_size":"0.05","name":"NIFTY"})
    assert c.lot_size==75 and c.expiry==date(2026,1,8)
