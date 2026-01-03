import socket
import ssl
import hmac
import hashlib
import time
import json
import logging
import os
from dotenv import load_dotenv

load_dotenv()
logger = logging.getLogger("MEXC_API")

class MexcAPI:
    HOST = "api.mexc.com"
    PORT = 443
    TIMEOUT = 30
    
    def __init__(self):
        self.api_key = os.getenv("MEXC_API_KEY", "")
        self.secret = os.getenv("MEXC_SECRET", "")
        self.ctx = ssl.create_default_context()
    
    def _request(self, method, path, params=None, auth=False):
        try:
            query = "&".join(f"{k}={v}" for k, v in (params or {}).items())
            if auth:
                ts = int(time.time() * 1000)
                query = f"{query}&timestamp={ts}" if query else f"timestamp={ts}"
                sig = hmac.new(self.secret.encode(), query.encode(), hashlib.sha256).hexdigest()
                query = f"{query}&signature={sig}"
            
            full_path = f"{path}?{query}" if query else path
            sock = socket.create_connection((self.HOST, self.PORT), timeout=self.TIMEOUT)
            ssl_sock = self.ctx.wrap_socket(sock, server_hostname=self.HOST)
            
            headers = f"Host: {self.HOST}\r\nConnection: close\r\n"
            if auth: headers += f"X-MEXC-APIKEY: {self.api_key}\r\n"
            headers += "Content-Type: application/json\r\n"
            
            request = f"{method} {full_path} HTTP/1.1\r\n{headers}\r\n"
            ssl_sock.sendall(request.encode())
            
            response = b""
            while True:
                try:
                    data = ssl_sock.recv(8192)
                    if not data: break
                    response += data
                except: break
            ssl_sock.close()
            
            parts = response.decode(errors="ignore").split("\r\n\r\n", 1)
            if len(parts) < 2: return {"error": "Empty response"}
            
            body = parts[1]
            if body.startswith("[") or body.startswith("{"): return json.loads(body)
            for line in body.split("\r\n"):
                line = line.strip()
                if line.startswith("[") or line.startswith("{"): return json.loads(line)
            return {"error": f"Cannot parse: {body[:100]}"}
        except socket.timeout: return {"error": "Connection timeout"}
        except ssl.SSLError as e: return {"error": f"SSL Error: {e}"}
        except json.JSONDecodeError as e: return {"error": f"JSON Error: {e}"}
        except Exception as e: return {"error": f"{type(e).__name__}: {e}"}
    
    def ping(self): return self._request("GET", "/api/v3/ping")
    
    def get_price(self, symbol):
        r = self._request("GET", "/api/v3/ticker/price", {"symbol": symbol})
        return float(r.get("price", 0)) if "error" not in r else None
    
    def get_prices(self, symbols=None):
        r = self._request("GET", "/api/v3/ticker/price")
        if "error" in r or not isinstance(r, list): return {}
        return {i["symbol"]: float(i.get("price", 0)) for i in r if symbols is None or i["symbol"] in symbols}
    
    def get_orderbook(self, symbol, limit=20):
        r = self._request("GET", "/api/v3/depth", {"symbol": symbol, "limit": limit})
        if "error" in r: return {"bids": [], "asks": []}
        return {"bids": [[float(p), float(q)] for p, q in r.get("bids", [])],
                "asks": [[float(p), float(q)] for p, q in r.get("asks", [])]}
    
    def get_klines(self, symbol, interval="15m", limit=100):
        r = self._request("GET", "/api/v3/klines", {"symbol": symbol, "interval": interval, "limit": limit})
        if "error" in r or not isinstance(r, list): return []
        return [[int(k[0]), float(k[1]), float(k[2]), float(k[3]), float(k[4]), float(k[5])] for k in r]
    
    def get_ticker_24h(self, symbol):
        return self._request("GET", "/api/v3/ticker/24hr", {"symbol": symbol})
    
    def get_balance(self):
        r = self._request("GET", "/api/v3/account", auth=True)
        if "error" in r: return {}
        return {b["asset"]: {"free": float(b.get("free", 0)), "locked": float(b.get("locked", 0)),
                "total": float(b.get("free", 0)) + float(b.get("locked", 0))}
                for b in r.get("balances", []) if float(b.get("free", 0)) + float(b.get("locked", 0)) > 0}
    
    def place_order(self, symbol, side, order_type, quantity, price=None):
        params = {"symbol": symbol, "side": side.upper(), "type": order_type.upper(), "quantity": quantity}
        if order_type.upper() == "LIMIT" and price: params["price"] = price
        return self._request("POST", "/api/v3/order", params, auth=True)
    
    def cancel_order(self, symbol, order_id):
        return self._request("DELETE", "/api/v3/order", {"symbol": symbol, "orderId": order_id}, auth=True)
    
    def get_open_orders(self, symbol=None):
        params = {"symbol": symbol} if symbol else {}
        return self._request("GET", "/api/v3/openOrders", params, auth=True)
    
    def get_order(self, symbol, order_id):
        return self._request("GET", "/api/v3/order", {"symbol": symbol, "orderId": order_id}, auth=True)
    
    def get_ohlcv(self, symbol, resolution="15", from_ts=None, to_ts=None):
        interval_map = {"1": "1m", "5": "5m", "15": "15m", "30": "30m", "60": "1h", "240": "4h", "D": "1d", "1D": "1d"}
        klines = self.get_klines(symbol, interval_map.get(resolution, "15m"), 100)
        if not klines: return {"s": "error", "msg": "No data"}
        return {"s": "ok", "t": [k[0]//1000 for k in klines], "o": [k[1] for k in klines],
                "h": [k[2] for k in klines], "l": [k[3] for k in klines],
                "c": [k[4] for k in klines], "v": [k[5] for k in klines]}
    
    def calculate_obi(self, symbol, depth=20):
        ob = self.get_orderbook(symbol, depth)
        if not ob["bids"] or not ob["asks"]: return 0
        bid_vol, ask_vol = sum(b[1] for b in ob["bids"]), sum(a[1] for a in ob["asks"])
        return (bid_vol - ask_vol) / (bid_vol + ask_vol) if (bid_vol + ask_vol) > 0 else 0
