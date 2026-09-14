import argparse, os
from .config import load_config
def main():
    p=argparse.ArgumentParser(); sub=p.add_subparsers(dest="command", required=True)
    v=sub.add_parser("validate"); v.add_argument("--strategy", default="config/strategy_reversal_credit.yaml"); v.add_argument("--trading", default="config/paper_trading.yaml")
    s=sub.add_parser("start-paper"); s.add_argument("--tokens", nargs="+", type=int); s.add_argument("--root", default=os.getenv("KITE_RUNTIME_ROOT","runtime"))
    a=p.parse_args()
    if a.command == "validate": print(load_config(a.strategy, a.trading).model_dump_json(indent=2))
    elif a.command == "start-paper":
        if os.getenv("KITE_TRADING_MODE","paper") != "paper": raise SystemExit("refusing to start: paper mode required")
        tokens=a.tokens or [int(x) for x in os.getenv("KITE_INSTRUMENT_TOKENS","").split(",") if x.strip()]
        if not tokens: raise SystemExit("provide --tokens or KITE_INSTRUMENT_TOKENS")
        from .collector.live import LiveCollector
        LiveCollector(tokens,a.root).run()
