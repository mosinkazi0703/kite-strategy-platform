import os
import httpx
class KiteMarginClient:
    """Read-only basket margin calculator; never places orders."""
    def __init__(self,api_key=None,access_token=None): self.api_key=api_key or os.environ["KITE_API_KEY"]; self.access_token=access_token or os.environ["KITE_ACCESS_TOKEN"]
    def basket(self,orders,consider_positions=False,mode="compact"):
        r=httpx.post("https://api.kite.trade/margins/basket",json={"orders":orders,"consider_positions":consider_positions,"mode":mode},headers={"X-Kite-Version":"3","Authorization":f"token {self.api_key}:{self.access_token}"},timeout=20); r.raise_for_status(); return r.json()["data"]
    def margin_for_legs(self,legs): return self.basket([{"exchange":l.contract.exchange,"tradingsymbol":l.contract.tradingsymbol,"transaction_type":l.side,"variety":"regular","product":"NRML","order_type":"MARKET","quantity":l.quantity} for l in legs])
