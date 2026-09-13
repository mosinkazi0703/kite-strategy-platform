import hashlib, os
from urllib.parse import urlencode
import httpx

def login_url(api_key: str, redirect_params: str | None = None) -> str:
    query = {"v": "3", "api_key": api_key}
    if redirect_params: query["redirect_params"] = redirect_params
    return "https://kite.zerodha.com/connect/login?" + urlencode(query)

def exchange_request_token(request_token: str, *, api_key: str | None = None, api_secret: str | None = None) -> dict:
    key, secret = api_key or os.environ["KITE_API_KEY"], api_secret or os.environ["KITE_API_SECRET"]
    checksum = hashlib.sha256((key + request_token + secret).encode()).hexdigest()
    response = httpx.post("https://api.kite.trade/session/token", data={"api_key": key, "request_token": request_token, "checksum": checksum}, headers={"X-Kite-Version": "3"}, timeout=20)
    response.raise_for_status()
    return response.json()["data"]
