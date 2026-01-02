# modules/network/nobitex_api.py
import requests
import os
import sys

# 1. PURGE PROXIES FROM ENVIRONMENT
# VPNs often leave these variables dirty
for k in ['HTTP_PROXY', 'HTTPS_PROXY', 'http_proxy', 'https_proxy']:
    if k in os.environ:
        print(f"      🧹 Removing dirty env var: {k}={os.environ[k]}")
        del os.environ[k]

class NobitexAPI:
    BASE_URL = "https://api.nobitex.ir"

    def __init__(self):
        self.session = requests.Session()
        self.session.trust_env = False  # Double check: Don't trust system proxy
        
        self.session.headers.update({
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Accept": "application/json",
            "Connection": "keep-alive"
        })

    def get_ohlcv(self, symbol, resolution="60", from_ts=None, to_ts=None):
        url = f"{self.BASE_URL}/market/udf/history"
        
        # Hardcoded params for testing
        params = {
            "symbol": symbol,
            "resolution": resolution,
            "from": from_ts,
            "to": to_ts
        }
        
        try:
            # timeout increased to 20
            response = self.session.get(url, params=params, timeout=20, verify=False)
            
            if response.status_code == 200:
                return response.json()
            else:
                return {"s": "error", "msg": f"HTTP {response.status_code}"}
                
        except Exception as e:
            return {"s": "error", "msg": f"{type(e).__name__}: {str(e)}"}
