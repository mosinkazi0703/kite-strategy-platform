from dataclasses import dataclass
from kite_strategy_platform.domain.instruments import Contract
@dataclass(frozen=True)
class Leg:
    contract: Contract; side: str; quantity: int
def build_four_legs(direction, current_atm, opening_atm, hedge_distance, step, expiry_contracts, lots=1, hedge=True):
    def find(strike, typ):
        matches=[c for c in expiry_contracts if c.strike==strike and c.option_type==typ]
        if len(matches)!=1: raise ValueError(f"expected exactly one contract for {strike} {typ}, found {len(matches)}")
        return matches[0]
    specs = [(current_atm,"CE","SELL"),(current_atm+hedge_distance*step,"CE","BUY"),(opening_atm,"PE","SELL"),(opening_atm-hedge_distance*step,"PE","BUY")] if direction=="UP" else [(current_atm,"PE","SELL"),(current_atm-hedge_distance*step,"PE","BUY"),(opening_atm,"CE","SELL"),(opening_atm+hedge_distance*step,"CE","BUY")]
    if not hedge: specs=[x for x in specs if x[2]=="SELL"]
    return [Leg(find(strike,typ),side,c.lot_size*lots) for strike,typ,side in specs for c in [find(strike,typ)]]
