import json, logging, time, uuid
import websocket

log=logging.getLogger(__name__)
class KiteWebSocketClient:
    def __init__(self, api_key, access_token, on_tick, reconnect=True, max_retries=8, on_connected=None):
        self.url=f"wss://ws.kite.trade?api_key={api_key}&access_token={access_token}"
        self.on_tick=on_tick; self.reconnect=reconnect; self.max_retries=max_retries; self.session_id=str(uuid.uuid4()); self.on_connected=on_connected; self.ws=None
    def run(self, tokens, mode="full"):
        retries=0
        while True:
            try:
                ws=websocket.create_connection(self.url, timeout=30); self.ws=ws
                self.subscribe(ws,tokens,mode)
                if self.on_connected: self.on_connected(self)
                retries=0
                while True:
                    message=ws.recv()
                    if isinstance(message, bytes) and len(message)>1: self.on_tick(message, self.session_id)
            except Exception as exc:
                if not self.reconnect or retries>=self.max_retries: raise
                retries += 1; log.warning("websocket reconnect attempt=%s error=%s", retries, type(exc).__name__); time.sleep(min(2**retries,30))
    def subscribe(self, ws, tokens, mode="full"):
        ws.send(json.dumps({"a":"subscribe","v":list(tokens)})); ws.send(json.dumps({"a":"mode","v":[mode,list(tokens)]}))
