import json
import logging
import threading
import time
import uuid
import websocket

log=logging.getLogger(__name__)
class KiteWebSocketClient:
    """One managed Kite socket. Callback errors must never create extra sockets."""
    def __init__(self, api_key, access_token, on_tick, reconnect=True, max_retries=8, on_connected=None):
        self.url=f"wss://ws.kite.trade?api_key={api_key}&access_token={access_token}"
        self.on_tick=on_tick; self.reconnect=reconnect; self.max_retries=max_retries; self.session_id=str(uuid.uuid4()); self.on_connected=on_connected; self.ws=None; self._stop_requested=threading.Event()
    def close(self):
        self._stop_requested.set(); ws,self.ws=self.ws,None
        if ws:
            try: ws.close()
            except Exception: log.debug("websocket close failed",exc_info=True)
    def run(self, tokens, mode="full"):
        retries=0
        while not self._stop_requested.is_set():
            ws=None
            try:
                ws=websocket.create_connection(self.url, timeout=30); self.ws=ws
                self.subscribe(ws,tokens,mode)
                if self.on_connected: self.on_connected(self)
                retries=0
                while not self._stop_requested.is_set():
                    message=ws.recv()
                    if isinstance(message, bytes) and len(message)>1:
                        try: self.on_tick(message, self.session_id)
                        except Exception: log.exception("websocket tick callback failed; keeping existing socket open")
            except Exception as exc:
                if self._stop_requested.is_set(): break
                if not self.reconnect or retries>=self.max_retries: raise
                retries += 1; log.warning("websocket reconnect attempt=%s error=%s", retries, type(exc).__name__); self._stop_requested.wait(min(2**retries,30))
            finally:
                if ws:
                    try: ws.close()
                    except Exception: log.debug("websocket close failed",exc_info=True)
                if self.ws is ws: self.ws=None
    def subscribe(self, ws, tokens, mode="full"):
        ws.send(json.dumps({"a":"subscribe","v":list(tokens)})); ws.send(json.dumps({"a":"mode","v":[mode,list(tokens)]}))
