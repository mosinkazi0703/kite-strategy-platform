import argparse, os
from .config import load_config
def main():
    p=argparse.ArgumentParser(); sub=p.add_subparsers(dest="command", required=True)
    v=sub.add_parser("validate"); v.add_argument("--strategy", default="config/strategy_reversal_credit.yaml"); v.add_argument("--trading", default="config/paper_trading.yaml")
    s=sub.add_parser("start-paper"); s.add_argument("--tokens", nargs="+", type=int); s.add_argument("--root", default=os.getenv("KITE_RUNTIME_ROOT","runtime"))
    allp=sub.add_parser("run-all"); allp.add_argument("--root", default=os.getenv("KITE_RUNTIME_ROOT","runtime")); allp.add_argument("--config-dir",default="config")
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
        from .runtime.coordinator import PaperTradingCoordinator
        from .runtime.application import UnattendedPaperApplication
        coordinator=PaperTradingCoordinator(os.environ["KITE_API_KEY"],os.environ["KITE_ACCESS_TOKEN"],a.root,a.config_dir)
        coordinator.load_instruments(); coordinator.subscribe_underlying_first()
        app=UnattendedPaperApplication([coordinator.underlying_token],a.root,a.config_dir)
        lifecycle=None
        def route_quote(quote):
            nonlocal lifecycle
            opening=coordinator.on_underlying_quote(quote)
            if opening is not None:
                from datetime import date
                app.collector.expand(coordinator.resolved_subscription_pairs(date.today()))
                composition=coordinator.start_paper()
                from .runtime.lifecycle import PaperLifecycle
                lifecycle=PaperLifecycle(composition.session,composition.universe)
            if coordinator.composition:
                coordinator.composition.on_quote(quote)
                if lifecycle and "dynamic_calendar_spread_v1" not in lifecycle.positions:
                    required={c.contract_id for c in coordinator.composition.universe.contracts}
                    if required.issubset(coordinator.composition.quotes): lifecycle.calendar_entry(coordinator.composition.quotes)
                if lifecycle: lifecycle.mark(coordinator.composition.quotes,quote.timestamp)
        def route_candle(candle):
            if not lifecycle or candle.contract_id != str(coordinator.underlying_token): return
            trigger=coordinator.handlers["reversal_credit_v1"].trigger(coordinator.opening_price,candle)
            if trigger and trigger.direction in ("UP","DOWN") and "reversal_credit_v1" not in lifecycle.positions:
                lifecycle.reversal_entry(trigger.direction,coordinator.composition.quotes)
        app.collector.on_quote=route_quote
        app.collector.on_candle=route_candle
        app.run()
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

if __name__ == "__main__":
    main()
