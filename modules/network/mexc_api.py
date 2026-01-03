"""
MEXC API Client — Raw Socket Implementation
For OCEAN HUNTER V10.8.2
Fixed: Content-Type header for authentication
"""

import socket
import ssl
import hmac
import hashlib
import time
import json
import os
import logging
from urllib.parse import urlencode
from dotenv import load_dotenv

load_dotenv()
logger = logging.getLogger("MEXC_API")


class MEXCClient:
    """MEXC Spot API via raw HTTPS socket"""

    def __init__(self):
        self.api_key = os.getenv("MEXC_API_KEY", "")
        self.api_secret = os.getenv("MEXC_SECRET_KEY", "")
        self.host = "api.mexc.com"
        self.base_path = "/api/v3"

    def _raw_request(self, method: str, path: str, params: dict = None, signed: bool = False) -> dict:
        """Send HTTPS request via raw socket"""
        params = params or {}

        if signed:
            params["timestamp"] = int(time.time() * 1000)
            query = urlencode(params)
            signature = hmac.new(
                self.api_secret.encode("utf-8"),
                query.encode("utf-8"),
                hashlib.sha256
            ).hexdigest()
            params["signature"] = signature

        query_string = urlencode(params) if params else ""

        if method == "GET":
            full_path = f"{self.base_path}{path}"
            if query_string:
                full_path += f"?{query_string}"
            body = ""
            content_type = "application/json"
        else:
            full_path = f"{self.base_path}{path}"
            body = query_string
            content_type = "application/x-www-form-urlencoded"

        headers = [
            f"{method} {full_path} HTTP/1.1",
            f"Host: {self.host}",
            f"X-MEXC-APIKEY: {self.api_key}",
            f"Content-Type: {content_type}",
            "Connection: close",
        ]

        if body:
            headers.append(f"Content-Length: {len(body)}")

        request = "\r\n".join(headers) + "\r\n\r\n"
        if body:
            request += body

        try:
            context = ssl.create_default_context()
            with socket.create_connection((self.host, 443), timeout=15) as sock:
                with context.wrap_socket(sock, server_hostname=self.host) as ssock:
                    ssock.sendall(request.encode("utf-8"))
                    response = b""
                    while True:
                        chunk = ssock.recv(4096)
                        if not chunk:
                            break
                        response += chunk

            response_text = response.decode("utf-8", errors="ignore")

            if "\r\n\r\n" in response_text:
                _, body_text = response_text.split("\r\n\r\n", 1)
            else:
                body_text = response_text

            if body_text.startswith("{") or body_text.startswith("["):
                return json.loads(body_text)
            else:
                lines = body_text.split("\r\n")
                for line in lines:
                    line = line.strip()
                    if line.startswith("{") or line.startswith("["):
                        return json.loads(line)
            return {"raw": body_text}

        except json.JSONDecodeError as e:
            logger.error(f"JSON parse error: {e}")
            return {"error": str(e)}
        except Exception as e:
            logger.error(f"Request failed: {e}")
            return {"error": str(e)}

    def ping(self) -> dict:
        return self._raw_request("GET", "/ping")

    def get_server_time(self) -> dict:
        return self._raw_request("GET", "/time")

    def get_ticker_price(self, symbol: str = "BTCUSDT") -> dict:
        return self._raw_request("GET", "/ticker/price", {"symbol": symbol})

    def get_orderbook(self, symbol: str, limit: int = 20) -> dict:
        return self._raw_request("GET", "/depth", {"symbol": symbol, "limit": limit})

    def get_account(self) -> dict:
        return self._raw_request("GET", "/account", signed=True)

    def get_balance(self, asset: str = None) -> dict:
        account = self.get_account()
        if "error" in account:
            return account
        balances = account.get("balances", [])
        if asset:
            for b in balances:
                if b.get("asset") == asset:
                    return b
            return {"asset": asset, "free": "0", "locked": "0"}
        return {"balances": balances}

    def create_order(self, symbol: str, side: str, order_type: str,
                     quantity: float, price: float = None) -> dict:
        params = {
            "symbol": symbol,
            "side": side.upper(),
            "type": order_type.upper(),
            "quantity": str(quantity),
        }
        if price and order_type.upper() == "LIMIT":
            params["price"] = str(price)
        return self._raw_request("POST", "/order", params, signed=True)

    def cancel_order(self, symbol: str, order_id: str = None) -> dict:
        params = {"symbol": symbol}
        if order_id:
            params["orderId"] = order_id
        return self._raw_request("DELETE", "/order", params, signed=True)

    def get_open_orders(self, symbol: str = None) -> dict:
        params = {"symbol": symbol} if symbol else {}
        return self._raw_request("GET", "/openOrders", params, signed=True)


_client_instance = None

def get_client() -> MEXCClient:
    global _client_instance
    if _client_instance is None:
        _client_instance = MEXCClient()
    return _client_instance
