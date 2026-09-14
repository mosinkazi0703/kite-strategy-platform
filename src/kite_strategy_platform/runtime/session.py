import json
from datetime import datetime, timezone
from pathlib import Path
from kite_strategy_platform.reporting.ledger import TradeLedger

class PaperSession:
    def __init__(self, root="runtime"):
        self.root=Path(root); self.ledger=TradeLedger(); self.events=[]; self.positions={}
    def event(self, event, **data):
        row={"at":datetime.now(timezone.utc).isoformat(),"event":event,**data}; self.events.append(row)
        path=self.root/"paper"/"events.jsonl"; path.parent.mkdir(parents=True,exist_ok=True)
        with path.open("a",encoding="utf-8") as f: f.write(json.dumps(row,default=str)+"\n")
    def record_trade(self, trade):
        row=self.ledger.record(trade); path=self.root/"paper"/"trades.jsonl"; path.parent.mkdir(parents=True,exist_ok=True)
        with path.open("a",encoding="utf-8") as f: f.write(json.dumps(row,default=str)+"\n")
        return row
    def report(self):
        report={"generated_at":datetime.now(timezone.utc).isoformat(),"trades":len(self.ledger.rows),"resolved":sum(r.get("net_pnl") is not None for r in self.ledger.rows),"net_pnl":sum(r.get("net_pnl") or 0 for r in self.ledger.rows)}
        path=self.root/"paper"/"daily_report.json"; path.parent.mkdir(parents=True,exist_ok=True); path.write_text(json.dumps(report,indent=2),encoding="utf-8"); return report
