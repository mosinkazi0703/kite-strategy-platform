from datetime import date
from kite_strategy_platform.kite.instrument_master import to_contract

class InstrumentResolver:
    def __init__(self, rows): self.contracts=[to_contract(r) for r in rows]
    def resolve(self, underlying, expiry, strikes, option_types=("CE","PE")):
        found=[c for c in self.contracts if c.underlying==underlying and c.expiry==expiry and c.strike in strikes and c.option_type in option_types]
        keys={(c.strike,c.option_type) for c in found}
        missing={(s,t) for s in strikes for t in option_types}-keys
        if missing: raise ValueError(f"missing contracts: {sorted(missing)}")
        return found
    def expiries(self, underlying, option_type=None):
        return sorted({c.expiry for c in self.contracts if c.underlying==underlying and (option_type is None or c.option_type==option_type) and c.expiry})
