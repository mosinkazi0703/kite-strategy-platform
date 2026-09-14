from datetime import datetime
from pathlib import Path
import json
from .instrument_master import download_instruments
from .resolver import InstrumentResolver
class InstrumentService:
    def __init__(self,root="runtime"): self.root=Path(root)
    def snapshot(self,api_key,access_token):
        rows=download_instruments(api_key,access_token); day=datetime.now().date().isoformat(); path=self.root/f"data/reference/instruments/snapshot_date={day}/instruments.json"
        path.parent.mkdir(parents=True,exist_ok=True); path.write_text(json.dumps(rows),encoding="utf-8"); return rows
    def resolve_chain(self,rows,underlying,expiry,atm,step,hedge_distance=6):
        strikes={atm,atm+hedge_distance*step,atm-hedge_distance*step}; return InstrumentResolver(rows).resolve(underlying,expiry,strikes)
