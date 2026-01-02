import requests
import json
import logging
import time
import os
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
from dotenv import load_dotenv
from modules.network.rate_limiter import RateLimiter

load_dotenv()
logger = logging.getLogger("NobitexAPI")

class NobitexAPI:
    BASE_URL = "https://api.nobitex.ir"

    def __init__(self, test_mode=False):
        self.token = os.getenv("NOBITEX_API_KEY") 
        self.test_mode = test_mode
        
        # Arch 2.5.1: 30 req/min limit (We use 25 for safety)
        self.rate_limiter = RateLimiter(max_calls=25, period=60)
        
        # Network Hardening: Force Direct Connection
        self.session = requests.Session()
        self.session.trust_env = False  # Ignore System Proxy
        self.session.proxies = {"http": None, "https": None} # Explicit No Proxy
        
        # Retry Logic for unstable networks
        retries = Retry(total=3, backoff_factor=1, status_forcelist=[500, 502, 503, 504])
        self.session.mount('https://', HTTPAdapter(max_retries=retries))

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
                timeout=12 # Slight increase for VPN latency
            )

            if response.status_code != 200:
                logger.error(f"API Error [{response.status_code}]: {response.text}")
                return {"status": "error", "code": response.status_code, "message": response.text}

            return response.json()

        except requests.exceptions.ProxyError:
            return {"status": "error", "message": "Proxy/VPN Conflict"}
        except requests.exceptions.ConnectionError:
            return {"status": "error", "message": "Connection Failed (VPN Split Tunneling Required)"}
        except Exception as e:
            return {"status": "error", "message": str(e)}

    # ---------------------------------------------------------
    # PUBLIC ENDPOINTS (For Strategy & Analysis)
    # ---------------------------------------------------------
    
    def get_orderbook(self, symbol="BTCUSDT"):
        # Arch 2.2: Required for OBI Calculation
        return self._send_request("GET", f"/v2/orderbook/{symbol}", public=True)

    def get_market_stats(self, src="btc", dst="usdt"):
        # General health check
        return self._send_request("GET", "/market/stats", params={"src": src, "dst": dst}, public=True)
    
    def get_ohlcv(self, symbol="BTCUSDT", resolution="15", limit=100):
        # Arch 2.1: M15 Timeframe required
        # resolution: 15 (min), 60 (hour), D (day)
        params = {"symbol": symbol, "resolution": resolution, "limit": limit}
        return self._send_request("GET", "/market/udf/history", params=params, public=True)

    # ---------------------------------------------------------
    # PRIVATE ENDPOINTS (For Trading & Wallet)
    # ---------------------------------------------------------

    def get_wallet(self):
        # Arch 1.2: Capital Allocation (USDT, BTC, PAXG, etc.)
        return self._send_request("POST", "/users/wallets/list")

    def get_profile(self):
        return self._send_request("GET", "/users/profile")

    def check_connection(self):
        try:
            # 1. Test Public (OHLCV is light and good test)
            t0 = time.time()
            # Request M15 candles for BTC (Standard check)
            stats = self.get_ohlcv(symbol="BTCUSDT", resolution="15", limit=1)
            ping = (time.time() - t0) * 1000
            
            if not stats or stats.get("status") == "error":
                return False, f"Public API Failed: {stats.get('message')}"
            
            # Check if we actually got candle data (s = status: ok)
            if stats.get('s') != 'ok':
                 return False, f"Data Error: {stats}"

            # 2. Test Private
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