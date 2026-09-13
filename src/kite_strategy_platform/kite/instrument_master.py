import csv, io, gzip
from datetime import date, datetime
import httpx
from kite_strategy_platform.domain.instruments import Contract

def download_instruments(api_key: str, access_token: str) -> list[dict]:
    r=httpx.get("https://api.kite.trade/instruments", headers={"X-Kite-Version":"3", "Authorization":f"token {api_key}:{access_token}"}, timeout=60)
    r.raise_for_status()
    raw = gzip.decompress(r.content) if r.content[:2] == b"\x1f\x8b" else r.content
    return list(csv.DictReader(io.StringIO(raw.decode("utf-8"))))

def to_contract(row: dict) -> Contract:
    expiry = date.fromisoformat(row["expiry"]) if row.get("expiry") else None
    return Contract(row["exchange"], row["tradingsymbol"], int(row["instrument_token"]), expiry, float(row["strike"]) if row.get("strike") else None, row.get("instrument_type") if row.get("instrument_type") in {"CE","PE"} else None, int(row["lot_size"]), float(row["tick_size"]), row.get("name", ""))
