import kite_strategy_platform.kite.websocket_client as module
from kite_strategy_platform.kite.websocket_client import KiteWebSocketClient

class FakeSocket:
    def __init__(self): self.closed=False; self.sent=[]
    def send(self,message): self.sent.append(message)
    def recv(self): return b"tick"
    def close(self): self.closed=True

def test_callback_failure_does_not_reconnect_or_leak_socket(monkeypatch):
    socket=FakeSocket(); calls=[]
    monkeypatch.setattr(module.websocket,"create_connection",lambda *_args,**_kwargs: calls.append(1) or socket)
    client=None
    def broken_callback(*_):
        client.close(); raise RuntimeError("margin endpoint failed")
    client=KiteWebSocketClient("key","token",broken_callback)
    client.run([1])
    assert len(calls)==1 and socket.closed and client.ws is None
