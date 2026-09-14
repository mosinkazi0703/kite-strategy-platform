from dataclasses import dataclass
from datetime import date, datetime, time
from kite_strategy_platform.kite.instrument_master import to_contract

@dataclass(frozen=True)
class MarketUniverse:
    underlying: object; atm_strike: float; expiries: tuple; contracts: tuple; tokens: tuple

class MarketBootstrap:
    def __init__(self, rows, underlying_symbol, underlying_exchange="NSE", derivative_exchange="NFO"):
        self.rows=rows; self.symbol=underlying_symbol; self.exchange=underlying_exchange; self.derivative_exchange=derivative_exchange
    def opening_price(self, quotes, reference_time=time(9,15)):
        candidates=[q for q in quotes if q.timestamp.timetz().replace(tzinfo=None)==reference_time and q.last is not None]
        if not candidates: raise ValueError("09:15 underlying opening price is unavailable")
        return candidates[0].last
    def select_expiries(self, today, mode="weekly"):
        dates=sorted({date.fromisoformat(r["expiry"]) for r in self.rows if r.get("expiry") and r.get("exchange")==self.derivative_exchange and (r.get("name")==self.symbol or r.get("tradingsymbol","").startswith(self.symbol)) and date.fromisoformat(r["expiry"])>=today})
        if len(dates)<2: raise ValueError("fewer than two future expiries available")
        if mode=="weekly": return tuple(dates[:2])
        if mode=="monthly":
            months=[]
            for d in dates:
                key=(d.year,d.month)
                if key not in months: months.append(key)
            selected=[d for d in dates if (d.year,d.month) in months[:2]]
            return tuple(sorted({d for d in selected if (d.year,d.month) in months[:2]}))[:2]
        raise ValueError("expiry mode must be weekly or monthly")
    def build(self, spot, today, mode="weekly", strike_step=None, hedge_distance=6):
        options=[to_contract(r) for r in self.rows if r.get("exchange")==self.derivative_exchange and r.get("instrument_type") in ("CE","PE") and (r.get("name")==self.symbol or r.get("tradingsymbol","").startswith(self.symbol))]
        if not options: raise ValueError("no option contracts found for configured underlying")
        step=strike_step or min(abs(a.strike-b.strike) for a in options for b in options if a.strike!=b.strike)
        atm=round(spot/step)*step; expiries=self.select_expiries(today,mode); required={atm,atm+hedge_distance*step,atm-hedge_distance*step}
        contracts=tuple(c for c in options if c.expiry in expiries and c.strike in required)
        expected={(e,s,t) for e in expiries for s in required for t in ("CE","PE")}
        actual={(c.expiry,c.strike,c.option_type) for c in contracts}
        if expected!=actual: raise ValueError(f"incomplete option chain: missing {sorted(expected-actual)}")
        underlying=next((r for r in self.rows if r.get("exchange")==self.exchange and r.get("tradingsymbol")==self.symbol),None)
        tokens=tuple(sorted({int(r["instrument_token"]) for r in self.rows if r.get("exchange")==self.exchange and r.get("tradingsymbol")==self.symbol} | {c.instrument_token for c in contracts}))
        if not underlying: raise ValueError("underlying instrument is missing")
        return MarketUniverse(to_contract(underlying),atm,expiries,contracts,tokens)
