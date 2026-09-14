import argparse, os
from .config import load_config
def main():
    p=argparse.ArgumentParser(); sub=p.add_subparsers(dest="command", required=True)
    v=sub.add_parser("validate"); v.add_argument("--strategy", default="config/strategy_reversal_credit.yaml"); v.add_argument("--trading", default="config/paper_trading.yaml")
    s=sub.add_parser("start-paper"); s.add_argument("--tokens", nargs="+", type=int); s.add_argument("--root", default=os.getenv("KITE_RUNTIME_ROOT","runtime"))
    allp=sub.add_parser("run-all"); allp.add_argument("--tokens", nargs="+", type=int); allp.add_argument("--root", default=os.getenv("KITE_RUNTIME_ROOT","runtime")); allp.add_argument("--config-dir",default="config")
    demo=sub.add_parser("self-test-paper"); demo.add_argument("--root",default="runtime")
    ins=sub.add_parser("download-instruments"); ins.add_argument("--root",default=os.getenv("KITE_RUNTIME_ROOT","runtime")); ins.add_argument("--force",action="store_true")
    r=sub.add_parser("list-strategies"); r.add_argument("--config-dir",default="config")
    a=p.parse_args()
    if a.command == "validate": print(load_config(a.strategy, a.trading).model_dump_json(indent=2))
    elif a.command == "start-paper":
        if os.getenv("KITE_TRADING_MODE","paper") != "paper": raise SystemExit("refusing to start: paper mode required")
        tokens=a.tokens or [int(x) for x in os.getenv("KITE_INSTRUMENT_TOKENS","").split(",") if x.strip()]
        if not tokens: raise SystemExit("provide --tokens or KITE_INSTRUMENT_TOKENS")
        from .collector.live import LiveCollector
        LiveCollector(tokens,a.root).run()
    elif a.command == "run-all":
        if os.getenv("KITE_TRADING_MODE","paper") != "paper": raise SystemExit("refusing to start: paper mode required")
        tokens=a.tokens or [int(x) for x in os.getenv("KITE_INSTRUMENT_TOKENS","").split(",") if x.strip()]
        if not tokens: raise SystemExit("provide --tokens or KITE_INSTRUMENT_TOKENS")
        from .runtime.application import UnattendedPaperApplication
        UnattendedPaperApplication(tokens,a.root,a.config_dir).run()
    elif a.command == "self-test-paper":
        from .runtime.synthetic import run_synthetic_paper
        print(run_synthetic_paper(a.root))
    elif a.command == "download-instruments":
        from .kite.instrument_service import InstrumentService
        rows=InstrumentService(a.root).load_or_download(os.environ["KITE_API_KEY"],os.environ["KITE_ACCESS_TOKEN"],a.force)
        print(f"saved instrument snapshot: {len(rows)} instruments")
    elif a.command == "list-strategies":
        from .runtime.loader import load_enabled_strategies
        for item in load_enabled_strategies(a.config_dir):
            if item.get("enabled"): print(item.get("strategy",{}).get("id",item["_path"]))
