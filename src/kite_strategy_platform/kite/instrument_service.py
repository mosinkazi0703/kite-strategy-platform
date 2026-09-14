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
    def snapshot_path(self, day=None):
        day=day or datetime.now().date().isoformat(); return self.root/f"data/reference/instruments/snapshot_date={day}/instruments.json"
    def load_or_download(self,api_key,access_token,force=False):
        path=self.snapshot_path()
        if path.exists() and not force: return json.loads(path.read_text(encoding="utf-8"))
        rows=self.snapshot(api_key,access_token)
        if not rows: raise RuntimeError("instrument master download returned no instruments")
        return rows
    def resolve_chain(self,rows,underlying,expiry,atm,step,hedge_distance=6):
        strikes={atm,atm+hedge_distance*step,atm-hedge_distance*step}; return InstrumentResolver(rows).resolve(underlying,expiry,strikes)
