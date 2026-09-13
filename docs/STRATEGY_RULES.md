# Strategy rules

The reversal-credit strategy reads the 09:15 opening reference, scans completed one-minute candles from 10:00 to 14:30, skips ambiguous candles, and enters only on the next executable quote. All thresholds, expiry, hedges, targets, stops, and costs belong in YAML. Missing or stale leg quotes are data-incomplete, never zero.
