# modules/network/nobitex_api.py
import requests
import socket
import urllib3

# Suppress SSL warnings for this diagnostic build
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

class NobitexAPI:
    BASE_URL = "https://api.nobitex.ir"

    def __init__(self):
        self.session = requests.Session()
        self.session.trust_env = False  # Bypass proxies
        self.session.headers.update({
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Accept": "application/json",
            "Connection": "keep-alive"
        })

    def debug_dns(self):
        """Check what IP Python sees for Nobitex"""
        try:
            domain = "api.nobitex.ir"
            ip = socket.gethostbyname(domain)
            return True, ip
        except Exception as e:
            return False, str(e)

    def get_ohlcv(self, symbol, resolution="60", from_ts=None, to_ts=None):
        url = f"{self.BASE_URL}/market/udf/history"
        
        if from_ts: from_ts = int(from_ts)
        if to_ts: to_ts = int(to_ts)
        
        params = {
            "symbol": symbol,
            "resolution": resolution,
            "from": from_ts,
            "to": to_ts
        }
        
        try:
            # FORCE DISABLE SSL VERIFICATION (verify=False)
            response = self.session.get(url, params=params, timeout=15, verify=False)
            
            if response.status_code == 200:
                data = response.json()
                if data.get("s") == "ok":
                    return data
                else:
                    return {"s": "error", "msg": f"API Status: {data.get('s')}", "debug": data}
            else:
                return {"s": "error", "msg": f"HTTP {response.status_code}", "code": response.status_code}
                
        except Exception as e:
            # Return full error details
            return {"s": "error", "msg": f"{type(e).__name__}: {str(e)}"}
