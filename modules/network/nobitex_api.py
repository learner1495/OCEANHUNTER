import requests
import json
import logging
import time
import os
from dotenv import load_dotenv
from modules.network.rate_limiter import RateLimiter

load_dotenv()
logger = logging.getLogger("NobitexAPI")

class NobitexAPI:
    BASE_URL = "https://api.nobitex.ir"

    def __init__(self, test_mode=False):
        # Changed to match your .env file variable name
        self.token = os.getenv("NOBITEX_API_KEY") 
        self.test_mode = test_mode
        self.rate_limiter = RateLimiter(max_calls=25, period=60)
        self.session = requests.Session()
        
        # ⚠️ NOBITEX NEEDS DIRECT CONNECTION (Bypass VPN)
        self.session.trust_env = False 
        self.session.proxies = {}

    def _get_headers(self):
        headers = {"content-type": "application/json"}
        if self.token:
            headers["Authorization"] = f"Token {self.token}"
        return headers

    def _send_request(self, method, endpoint, params=None, data=None, public=False):
        url = f"{self.BASE_URL}{endpoint}"
        self.rate_limiter.wait_if_needed()

        try:
            response = self.session.request(
                method=method,
                url=url,
                headers=self._get_headers(),
                params=params,
                data=json.dumps(data) if data else None,
                timeout=10 
            )

            if response.status_code != 200:
                logger.error(f"API Error [{response.status_code}]: {response.text}")
                return {"status": "error", "code": response.status_code, "message": response.text}

            return response.json()

        except requests.exceptions.ProxyError:
            return {"status": "error", "message": "Proxy/VPN Conflict"}
        except requests.exceptions.ConnectionError:
            return {"status": "error", "message": "Connection Failed (Check VPN Split Tunneling)"}
        except Exception as e:
            return {"status": "error", "message": str(e)}

    def get_orderbook(self, symbol="BTCUSDT"):
        return self._send_request("GET", f"/v2/orderbook/{symbol}", public=True)

    def get_market_stats(self, src="btc", dst="usdt"):
        return self._send_request("GET", "/market/stats", params={"src": src, "dst": dst}, public=True)
    
    def get_profile(self):
        """Test Private API (Needs Token)"""
        return self._send_request("GET", "/users/profile")

    def check_connection(self):
        try:
            # 1. Test Public
            t0 = time.time()
            stats = self.get_market_stats()
            ping = (time.time() - t0) * 1000
            
            if not stats or stats.get("status") == "error":
                return False, f"Public API Failed: {stats.get('message')}"

            # 2. Test Private (if token exists)
            auth_msg = "Skipped (No Token)"
            if self.token:
                profile = self.get_profile()
                if profile and profile.get("status") == "ok":
                    auth_msg = "Authenticated ✅"
                else:
                    auth_msg = f"Auth Failed ❌ ({profile.get('message')})"
            
            return True, f"Connected ({ping:.0f}ms) | {auth_msg}"
        except Exception as e:
            return False, str(e)