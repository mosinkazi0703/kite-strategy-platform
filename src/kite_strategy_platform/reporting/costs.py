from dataclasses import dataclass
@dataclass(frozen=True)
class CostModel:
    brokerage_per_order: float=0.0; transaction_rate: float=0.0; tax_rate: float=0.0
    def calculate(self, turnover, orders): return self.brokerage_per_order*orders + turnover*self.transaction_rate + turnover*self.tax_rate
