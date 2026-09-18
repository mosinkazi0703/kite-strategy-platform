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
    d=sub.add_parser("dashboard"); d.add_argument("--root",default=os.getenv("KITE_RUNTIME_ROOT","runtime")); d.add_argument("--host",default="127.0.0.1"); d.add_argument("--port",type=int,default=8765)
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
        calendar_entry_attempted=False
        def reject_entry(strategy_id,error):
            response=getattr(error,"response",None); details={"strategy_id":strategy_id,"reason":"ENTRY_SETUP_FAILED","error_type":type(error).__name__}
            if response is not None:
                details["http_status"]=response.status_code; details["http_body"]=response.text[:500]
            coordinator.composition.session.event("entry_rejected",**details)
        def route_quote(quote):
            nonlocal lifecycle,calendar_entry_attempted
            opening=coordinator.on_underlying_quote(quote)
            if opening is not None:
                from datetime import date
                app.collector.expand(coordinator.resolved_subscription_pairs(date.today()))
                composition=coordinator.start_paper()
                # The resolved-market composition owns the live positions and ledger.
                # Report that same session at shutdown rather than the bootstrap session.
                app.session=composition.session
                composition.session.event("reference_captured",price=opening,kind=coordinator.reference_kind)
                from .runtime.lifecycle import PaperLifecycle
                from .kite.margin_client import KiteMarginClient
                max_margin=float(os.environ["KITE_MAX_PAPER_MARGIN"]) if os.getenv("KITE_MAX_PAPER_MARGIN") else None
                lifecycle=PaperLifecycle(composition.session,composition.universe,margin_client=KiteMarginClient(coordinator.api_key,coordinator.access_token),max_margin=max_margin)
            if coordinator.composition:
                coordinator.composition.on_quote(quote)
                if lifecycle and not calendar_entry_attempted and "dynamic_calendar_spread_v1" not in lifecycle.positions:
                    required={c.contract_id for c in coordinator.composition.universe.contracts}
                    if required.issubset(coordinator.composition.quotes):
                        calendar_entry_attempted=True
                        try: lifecycle.calendar_entry(coordinator.composition.quotes)
                        except Exception as error: reject_entry("dynamic_calendar_spread_v1",error)
                if lifecycle: lifecycle.mark(coordinator.composition.quotes,quote.timestamp)
        def route_candle(candle):
            if not lifecycle or candle.contract_id != str(coordinator.underlying_token): return
            trigger=coordinator.handlers["reversal_credit_v1"].trigger(coordinator.opening_price,candle)
            if trigger and trigger.direction in ("UP","DOWN") and "reversal_credit_v1" not in lifecycle.positions:
                try: lifecycle.reversal_entry(trigger.direction,coordinator.composition.quotes)
                except Exception as error: reject_entry("reversal_credit_v1",error)
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
    elif a.command == "dashboard":
        from .dashboard.server import serve
        serve(a.root,a.host,a.port)

if __name__ == "__main__":
    main()
