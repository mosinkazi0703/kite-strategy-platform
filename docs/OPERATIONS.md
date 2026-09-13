# Operations and smoke test

1. Set `KITE_API_KEY`, `KITE_API_SECRET`, and the daily access token in the process environment.
2. Validate YAML before market open.
3. Download and snapshot the instrument master; verify expiry, lot size, strike step, and subscription capacity.
4. Run synthetic fixture tests first. A future read-only WebSocket smoke test must capture ticks only and must not place orders.
5. Stop gracefully, flush checkpoints, and inspect quality reports for gaps, duplicates, stale quotes, and residual paper exposure.
