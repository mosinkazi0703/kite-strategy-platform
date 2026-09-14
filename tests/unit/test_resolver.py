from kite_strategy_platform.kite.resolver import InstrumentResolver
def test_resolver_requires_complete_universe():
    rows=[{"exchange":"NFO","tradingsymbol":"X","instrument_token":"1","expiry":"2026-01-08","strike":"100","instrument_type":"CE","lot_size":"1","tick_size":".05","name":"NIFTY"}]
    r=InstrumentResolver(rows)
    try: r.resolve("NIFTY",__import__('datetime').date(2026,1,8),[100])
    except ValueError as e: assert "missing contracts" in str(e)
    else: assert False
