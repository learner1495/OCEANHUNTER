#!/usr/bin/env python3
"""MEXC API Client — Raw Socket Edition"""
import socket, ssl, json, hmac, hashlib, time, os
from urllib.parse import urlencode
from dotenv import load_dotenv
load_dotenv()

class MEXCClient:
    HOST, PORT = "api.mexc.com", 443
    
    def __init__(self):
        self.api_key = os.getenv("MEXC_API_KEY", "")
        self.secret_key = os.getenv("MEXC_SECRET_KEY", "")
        self._ctx = ssl.create_default_context()
    
    def _request(self, method, endpoint, params=None, auth=False):
        params = params or {}
        if auth:
            params["timestamp"] = int(time.time() * 1000)
            qs = urlencode(sorted(params.items()))
            params["signature"] = hmac.new(self.secret_key.encode(), qs.encode(), hashlib.sha256).hexdigest()
        query = urlencode(params) if params else ""
        path = f"/api/v3{endpoint}" + (f"?{query}" if query and method == "GET" else "")
        headers = [f"{method} {path} HTTP/1.1", f"Host: {self.HOST}", "Accept: application/json",
                   "Content-Type: application/x-www-form-urlencoded", "Connection: close"]
        if self.api_key:
            headers.append(f"X-MEXC-APIKEY: {self.api_key}")
        body = query if method == "POST" else ""
        if body:
            headers.append(f"Content-Length: {len(body)}")
        request = "\r\n".join(headers) + "\r\n\r\n" + body
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(20)
            wrapped = self._ctx.wrap_socket(sock, server_hostname=self.HOST)
            wrapped.connect((self.HOST, self.PORT))
            wrapped.sendall(request.encode())
            response = b""
            while True:
                chunk = wrapped.recv(4096)
                if not chunk:
                    break
                response += chunk
            wrapped.close()
            parts = response.split(b"\r\n\r\n", 1)
            if len(parts) == 2:
                hdr, body = parts
                if b"Transfer-Encoding: chunked" in hdr:
                    body = self._decode_chunked(body)
                return json.loads(body.decode())
            return {"error": "Invalid response"}
        except socket.timeout:
            return {"error": "Timeout"}
        except ssl.SSLError as e:
            return {"error": f"SSL: {e}"}
        except Exception as e:
            return {"error": str(e)}
    
    def _decode_chunked(self, data):
        result = b""
        while data:
            end = data.find(b"\r\n")
            if end == -1:
                break
            try:
                size = int(data[:end].decode().strip(), 16)
            except:
                break
            if size == 0:
                break
            result += data[end+2:end+2+size]
            data = data[end+4+size:]
        return result
    
    def ping(self):
        return self._request("GET", "/ping")
    
    def get_time(self):
        return self._request("GET", "/time")
    
    def get_price(self, symbol):
        r = self._request("GET", "/ticker/price", {"symbol": symbol})
        return float(r.get("price", 0)) if "error" not in r else 0.0
    
    def get_prices(self, symbols=None):
        r = self._request("GET", "/ticker/price")
        if not isinstance(r, list):
            return {}
        prices = {i["symbol"]: float(i["price"]) for i in r}
        return {s: prices.get(s, 0) for s in symbols} if symbols else prices
    
    def get_orderbook(self, symbol, limit=20):
        r = self._request("GET", "/depth", {"symbol": symbol, "limit": limit})
        if "error" in r:
            return {"bids": [], "asks": []}
        return {"bids": [[float(p), float(q)] for p, q in r.get("bids", [])],
                "asks": [[float(p), float(q)] for p, q in r.get("asks", [])]}
    
    def get_klines(self, symbol, interval="1h", limit=100):
        r = self._request("GET", "/klines", {"symbol": symbol, "interval": interval, "limit": limit})
        if not isinstance(r, list):
            return []
        return [{"time": k[0], "open": float(k[1]), "high": float(k[2]), "low": float(k[3]),
                 "close": float(k[4]), "volume": float(k[5])} for k in r]
    
    def get_ticker_24h(self, symbol=None):
        params = {"symbol": symbol} if symbol else {}
        return self._request("GET", "/ticker/24hr", params)
    
    def get_account(self):
        return self._request("GET", "/account", auth=True)
    
    def get_balances(self):
        acc = self.get_account()
        if "balances" not in acc:
            return {}
        return {b["asset"]: {"free": float(b["free"]), "locked": float(b["locked"])}
                for b in acc["balances"] if float(b["free"]) > 0 or float(b["locked"]) > 0}
    
    def get_balance(self, asset):
        return self.get_balances().get(asset, {"free": 0, "locked": 0})
    
    def place_order(self, symbol, side, quantity, order_type="MARKET", price=None):
        params = {"symbol": symbol, "side": side.upper(), "type": order_type, "quantity": str(quantity)}
        if order_type == "LIMIT" and price:
            params["price"], params["timeInForce"] = str(price), "GTC"
        return self._request("POST", "/order", params, auth=True)
    
    def get_open_orders(self, symbol=None):
        params = {"symbol": symbol} if symbol else {}
        r = self._request("GET", "/openOrders", params, auth=True)
        return r if isinstance(r, list) else []
    
    def cancel_order(self, symbol, order_id):
        return self._request("DELETE", "/order", {"symbol": symbol, "orderId": order_id}, auth=True)
    
    def calculate_obi(self, symbol, depth=20):
        ob = self.get_orderbook(symbol, depth)
        if not ob["bids"] or not ob["asks"]:
            return 0
        bid_vol = sum(b[1] for b in ob["bids"])
        ask_vol = sum(a[1] for a in ob["asks"])
        total = bid_vol + ask_vol
        return (bid_vol - ask_vol) / total if total > 0 else 0
    
    def get_ohlcv(self, symbol, resolution="15", limit=100):
        interval_map = {"1": "1m", "5": "5m", "15": "15m", "30": "30m", "60": "1h", "240": "4h", "D": "1d"}
        klines = self.get_klines(symbol, interval_map.get(resolution, "15m"), limit)
        if not klines:
            return {"s": "error", "msg": "No data"}
        return {"s": "ok", "t": [k["time"]//1000 for k in klines],
                "o": [k["open"] for k in klines], "h": [k["high"] for k in klines],
                "l": [k["low"] for k in klines], "c": [k["close"] for k in klines],
                "v": [k["volume"] for k in klines]}

MexcAPI = MEXCClient
