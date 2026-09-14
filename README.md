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

## Start paper-mode collection

```powershell
$env:KITE_API_KEY = "your_api_key"
$env:KITE_ACCESS_TOKEN = "your_daily_access_token"
$env:KITE_TRADING_MODE = "paper"
$env:KITE_INSTRUMENT_TOKENS = "256265,260105"
$env:PYTHONPATH = "src"
& "C:\Program Files\LibreOffice\program\python.exe" -m kite_strategy_platform.cli start-paper
```

Ticks are appended to `runtime/data/raw_ticks/ticks.jsonl`; completed candles are partitioned under `runtime/data/candles/interval=1minute/trading_date=YYYY-MM-DD/candles.parquet`. No order API is called.

The paper engine also includes `DynamicCalendarSpread` in `config/strategy_calendar_spread.yaml`: it buys the farther-expiry CE and sells the nearer-expiry CE, selects expiries from actual master data, exits on target/IV collapse/market close, and exposes a configurable delta threshold for optional futures hedging.

See `docs/STRATEGY_RULES.md`, `docs/DATA_SCHEMA.md`, and `docs/OPERATIONS.md` for the implementation contract and smoke-test checklist.
