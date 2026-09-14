from .costs import CostModel
class TradeLedger:
    def __init__(self,costs=None): self.costs=costs or CostModel(); self.rows=[]
    def record(self,trade):
        row=dict(trade); row["costs"]=self.costs.calculate(row.get("turnover",0),row.get("orders",0)); row["net_pnl"]=None if row.get("gross_pnl") is None else row["gross_pnl"]-row["costs"]; self.rows.append(row); return row
