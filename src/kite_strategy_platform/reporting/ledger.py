from .costs import CostModel
class TradeLedger:
    def __init__(self,costs=None):
        self.costs=costs or CostModel(); self.rows=[]; self._record_ids=set()
    def record(self,trade):
        record_id=trade.get("record_id")
        if record_id is not None and record_id in self._record_ids:
            return None
        row=dict(trade); row["costs"]=self.costs.calculate(row.get("turnover",0),row.get("orders",0)); row["net_pnl"]=None if row.get("gross_pnl") is None else row["gross_pnl"]-row["costs"]; self.rows.append(row)
        if record_id is not None: self._record_ids.add(record_id)
        return row
