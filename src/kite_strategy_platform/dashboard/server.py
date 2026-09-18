from __future__ import annotations

import json
from datetime import datetime, timezone
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

from kite_strategy_platform.kite.instrument_master import to_contract


def read_new_rows(path: Path, offset: int):
    if not path.exists(): return [], offset
    with path.open("r", encoding="utf-8") as stream:
        stream.seek(offset); data=stream.read(); offset=stream.tell()
    return [json.loads(line) for line in data.splitlines() if line.strip()], offset


class RuntimeView:
    def __init__(self, root="runtime"):
        self.root=Path(root); self.event_offset=0; self.tick_offset=0
        self.session={}; self.positions={}; self.marks={}; self.quotes={}; self.events=[]; self.symbols={}

    def load_symbols(self):
        snapshots=sorted((self.root/"data"/"reference"/"instruments").glob("snapshot_date=*/instruments.json"))
        if not snapshots or self.symbols: return
        try:
            self.symbols={to_contract(row).contract_id:row["tradingsymbol"] for row in json.loads(snapshots[-1].read_text(encoding="utf-8"))}
        except Exception: pass

    def update(self):
        self.load_symbols()
        rows,self.event_offset=read_new_rows(self.root/"paper"/"events.jsonl",self.event_offset)
        for event in rows:
            kind=event.get("event")
            if kind=="paper_session_start": self.session=event; self.positions={}; self.marks={}; self.events=[]
            if not self.session: continue
            self.events=(self.events+[event])[-80:]
            if kind=="paper_entry": self.positions[event["strategy_id"]]=event
            if kind=="exit": self.positions.pop(event.get("strategy_id"),None)
            if kind=="mark": self.marks[event.get("strategy_id")]=event
        rows,self.tick_offset=read_new_rows(self.root/"data"/"raw_ticks"/"ticks.jsonl",self.tick_offset)
        for quote in rows: self.quotes[quote.get("contract_id")]=quote

    def snapshot(self):
        self.update(); now=datetime.now(timezone.utc); latest=max(self.quotes.values(),key=lambda x:x.get("received_at_utc",""),default={})
        try: live=(now-datetime.fromisoformat(latest["received_at_utc"])).total_seconds()<=10
        except (KeyError,ValueError): live=False
        positions=[]
        for strategy,entry in self.positions.items():
            legs=[]
            for order in entry.get("margin_details",{}).get("orders",[]):
                quote=next((q for cid,q in self.quotes.items() if self.symbols.get(cid)==order.get("tradingsymbol")),{})
                legs.append({"symbol":order.get("tradingsymbol"),"side":order.get("transaction_type"),"quantity":order.get("quantity"),"last":quote.get("last_price"),"bid":quote.get("bid"),"ask":quote.get("ask"),"at":quote.get("received_at_utc")})
            mark=self.marks.get(strategy,{})
            positions.append({"strategy":strategy,"state":mark.get("state","OPEN"),"margin_required":entry.get("margin_required"),"initial_cashflow_rupees":entry.get("initial_cashflow_rupees"),"pnl_points":mark.get("pnl_points"),"gross_pnl_rupees":mark.get("gross_pnl_rupees"),"mark_at":mark.get("at"),"legs":legs})
        return {"generated_at":now.isoformat(),"collector":{"status":"LIVE" if live else "STALE_OR_STOPPED","latest_tick_at":latest.get("received_at_utc"),"tracked_contracts":len(self.quotes)},"session":self.session,"positions":positions,"events":list(reversed(self.events[-25:]))}


PAGE = """<!doctype html><html><head><meta charset='utf-8'><title>Kite Paper Dashboard</title><style>
body{font-family:Segoe UI,Arial;background:#0b1220;color:#e5e7eb;margin:0;padding:25px}.sub{color:#94a3b8}.cards{display:flex;gap:12px;flex-wrap:wrap}.card{background:#162033;border:1px solid #27354e;border-radius:10px;padding:16px;margin:12px 0;min-width:230px}.label{color:#94a3b8;font-size:12px;text-transform:uppercase}.value{font-size:24px;font-weight:bold;margin-top:6px}.good{color:#34d399}.bad{color:#fb7185}table{width:100%;border-collapse:collapse;margin-top:10px}th,td{text-align:left;padding:8px;border-bottom:1px solid #27354e;font-size:13px}th{color:#94a3b8}pre{white-space:pre-wrap;font-size:12px}</style></head><body>
<h1>Kite Paper Dashboard</h1><p class='sub' id='updated'></p><div class='cards' id='cards'></div><h2>Open paper positions</h2><div id='positions'></div><h2>Recent lifecycle events</h2><div class='card' id='events'></div>
<script>
const e=v=>String(v??'—').replaceAll('&','&amp;').replaceAll('<','&lt;'); const m=v=>v==null?'—':new Intl.NumberFormat('en-IN',{style:'currency',currency:'INR',maximumFractionDigits:2}).format(v); const n=v=>v==null?'—':Number(v).toFixed(2);
function show(d){let c=d.collector;document.querySelector('#updated').textContent='Updated '+new Date(d.generated_at).toLocaleTimeString();document.querySelector('#cards').innerHTML=`<div class='card'><div class='label'>Collector</div><div class='value ${c.status==='LIVE'?'good':'bad'}'>${c.status}</div><div class='sub'>Latest ${e(c.latest_tick_at)}</div></div><div class='card'><div class='label'>Tracked contracts</div><div class='value'>${c.tracked_contracts}</div><div class='sub'>${e((d.session.strategies||[]).join(', '))}</div></div>`;document.querySelector('#positions').innerHTML=d.positions.length?d.positions.map(p=>`<div class='card'><div class='label'>${e(p.strategy)} · ${e(p.state)}</div><div class='cards'><div><div class='label'>Gross P&L</div><div class='value ${p.gross_pnl_rupees>=0?'good':'bad'}'>${m(p.gross_pnl_rupees)}</div><div>${n(p.pnl_points)} points</div></div><div><div class='label'>Margin</div><div class='value'>${m(p.margin_required)}</div><div>Entry: ${m(p.initial_cashflow_rupees)}</div></div></div><table><tr><th>Leg</th><th>Side</th><th>Qty</th><th>LTP</th><th>Bid / Ask</th><th>Tick</th></tr>${p.legs.map(l=>`<tr><td>${e(l.symbol)}</td><td>${e(l.side)}</td><td>${e(l.quantity)}</td><td>${n(l.last)}</td><td>${n(l.bid)} / ${n(l.ask)}</td><td>${e(l.at)}</td></tr>`).join('')}</table></div>`).join(''):'<div class="card">No open paper position.</div>';document.querySelector('#events').innerHTML=d.events.map(x=>`<pre>${e(x.at)}  ${e(x.event)}  ${e(x.strategy_id||'')}  ${e(x.reason||'')}</pre>`).join('');}
async function load(){try{show(await (await fetch('/api/snapshot')).json())}catch(x){document.querySelector('#events').textContent=x}}load();setInterval(load,2000);
</script></body></html>"""


def serve(root="runtime", host="127.0.0.1", port=8765):
    view=RuntimeView(root)
    class Handler(BaseHTTPRequestHandler):
        def do_GET(self):
            if self.path=="/api/snapshot":
                body=json.dumps(view.snapshot()).encode(); self.send_response(200); self.send_header("Content-Type","application/json"); self.end_headers(); self.wfile.write(body)
            elif self.path=="/":
                self.send_response(200); self.send_header("Content-Type","text/html; charset=utf-8"); self.end_headers(); self.wfile.write(PAGE.encode())
            else: self.send_error(404)
        def log_message(self,*_): pass
    server=ThreadingHTTPServer((host,port),Handler); print(f"Dashboard: http://{host}:{port}")
    try: server.serve_forever()
    except KeyboardInterrupt: pass
    finally: server.server_close()
