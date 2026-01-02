import requests
import json
import logging
import time
from modules.network.rate_limiter import RateLimiter

logger = logging.getLogger("NobitexAPI")

class NobitexAPI:
    BASE_URL = "https://api.nobitex.ir"

    def __init__(self, token=None, test_mode=False):
        self.token = token
        self.test_mode = test_mode
        self.rate_limiter = RateLimiter(max_calls=25, period=60)
        self.session = requests.Session()
        
        # ⚠️ CRITICAL FOR VPN USERS:
        # trust_env=False tells requests to ignore system proxies (VPN) 
        # and try to connect directly. This helps with Nobitex IP restrictions.
        self.session.trust_env = False 
        self.session.proxies = {} # Explicitly clear proxies

    def _get_headers(self):
        headers = {"content-type": "application/json"}
        if self.token:
            headers["Authorization"] = f"Token {self.token}"
        return headers

    def _send_request(self, method, endpoint, params=None, data=None, public=False):
        """
        Unified request handler with error management and rate limiting.
        """
        url = f"{self.BASE_URL}{endpoint}"
        
        # 1. Check Rate Limit
        self.rate_limiter.wait_if_needed()

        try:
            # 2. Send Request
            response = self.session.request(
                method=method,
                url=url,
                headers=self._get_headers(),
                params=params,
                data=json.dumps(data) if data else None,
                timeout=10 
            )

            # 3. Handle Errors
            if response.status_code != 200:
                logger.error(f"API Error [{response.status_code}]: {response.text}")
                return {"status": "error", "code": response.status_code, "message": response.text}

            return response.json()

        except requests.exceptions.ProxyError:
            logger.error("Proxy Error: VPN might be blocking connection to Nobitex.")
            return {"status": "error", "message": "Proxy/VPN Conflict"}
        except requests.exceptions.ConnectionError:
            logger.error("Connection Error: Check internet.")
            return {"status": "error", "message": "Connection Failed"}
        except Exception as e:
            logger.error(f"Unexpected Error: {e}")
            return {"status": "error", "message": str(e)}

    # ════ Public Endpoints (No Token Needed) ════

    def get_orderbook(self, symbol="BTCUSDT"):
        """Fetches OBI data (Bids/Asks)"""
        return self._send_request("GET", f"/v2/orderbook/{symbol}", public=True)

    def get_market_stats(self, src="btc", dst="usdt"):
        """Fetches Price, Volume, High/Low"""
        return self._send_request("GET", "/market/stats", params={"src": src, "dst": dst}, public=True)
        
    def check_connection(self):
        """Test connection and verify IP location logic"""
        try:
            # Check what IP we are using for Nobitex
            # Nobitex keeps connection open, so if this works, we are good.
            t0 = time.time()
            data = self.get_market_stats()
            ping = (time.time() - t0) * 1000
            
            if data and data.get("status") == "ok":
                return True, f"Connected to Nobitex (Ping: {ping:.0f}ms)"
            else:
                return False, f"Nobitex Error: {data}"
        except Exception as e:
            return False, str(e)