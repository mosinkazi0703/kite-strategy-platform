from kite_strategy_platform.kite.margin_client import KiteMarginClient
import kite_strategy_platform.kite.margin_client as module

class Response:
    def raise_for_status(self): pass
    def json(self): return {"data":{"initial":{"total":100},"final":{"total":50}}}

def test_basket_posts_raw_order_array_with_query_parameters(monkeypatch):
    captured={}
    def post(url,**kwargs): captured.update(url=url,**kwargs); return Response()
    monkeypatch.setattr(module.httpx,"post",post)
    orders=[{"exchange":"NFO","tradingsymbol":"NIFTYTEST","quantity":65}]
    result=KiteMarginClient("key","token").basket(orders,consider_positions=True,mode="compact")
    assert captured["json"] == orders
    assert captured["params"] == {"consider_positions":"true","mode":"compact"}
    assert captured["headers"]["Content-Type"] == "application/json"
    assert result["final"]["total"] == 50
