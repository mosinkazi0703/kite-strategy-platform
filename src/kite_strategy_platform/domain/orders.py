from dataclasses import dataclass
@dataclass(frozen=True)
class OrderIntent: contract_id: str; side: str; quantity: int
