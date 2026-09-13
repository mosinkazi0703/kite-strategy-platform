import argparse
from .config import load_config
def main():
    p=argparse.ArgumentParser(); sub=p.add_subparsers(dest="command", required=True)
    v=sub.add_parser("validate"); v.add_argument("--strategy", default="config/strategy_reversal_credit.yaml"); v.add_argument("--trading", default="config/paper_trading.yaml")
    a=p.parse_args()
    if a.command == "validate": print(load_config(a.strategy, a.trading).model_dump_json(indent=2))
