# Data schema

Normalized records must include `schema_version`, timezone-aware receive/exchange timestamps, exact `contract_id`, instrument token, source, and quality flags. Raw ticks are append-only; candles are never manufactured for empty minutes. Parquet is intended for market data and JSONL for operational events, written atomically under the configured runtime root.
