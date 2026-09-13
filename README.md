# Kite Strategy Platform

Safe-by-default Kite Connect market-data, paper-trading, and backtesting foundation. The initial release contains a pure, configurable reversal-credit trigger engine and simulation-only execution primitives; it never calls Kite order APIs.

## Windows PowerShell setup

```powershell
py -3.11 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -e ".[dev]"
Copy-Item .env.example .env
python -m pytest
python -m kite_strategy_platform.cli validate
```

Credentials belong only in environment variables or the untracked `.env`. Use Asia/Kolkata timestamps, exact contract IDs, and actual instrument-master expiries. Runtime data and logs are excluded from Git.

See `docs/STRATEGY_RULES.md`, `docs/DATA_SCHEMA.md`, and `docs/OPERATIONS.md` for the implementation contract and smoke-test checklist.
