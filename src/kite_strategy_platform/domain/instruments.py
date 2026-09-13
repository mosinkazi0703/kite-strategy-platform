from dataclasses import dataclass
from datetime import date
from hashlib import sha256

@dataclass(frozen=True)
class Contract:
    exchange: str; tradingsymbol: str; instrument_token: int; expiry: date | None
    strike: float | None; option_type: str | None; lot_size: int; tick_size: float
    underlying: str = ""

    @property
    def contract_id(self) -> str:
        raw = f"{self.exchange}|{self.tradingsymbol}|{self.instrument_token}|{self.expiry}|{self.strike}|{self.option_type}"
        return sha256(raw.encode()).hexdigest()[:20]
