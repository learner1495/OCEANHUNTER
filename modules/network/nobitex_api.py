# modules/network/nobitex_api.py
import requests
import urllib3
import sys
import os

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# Apply Patch
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
try:
    from modules.network.dns_bypass import apply_patch
    apply_patch()
    print("✅ Precision DNS Engine Activated")
except ImportError:
    print("⚠️ Could not load DNS Bypass")

class NobitexAPI:
    BASE_URL = "https://api.nobitex.ir"

    def __init__(self):
        self.session = requests.Session()
        self.session.trust_env = False 
        self.session.headers.update({
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/120.0.0.0 Safari/537.36",
            "Accept": "application/json"
        })

    def get_ohlcv(self, symbol, resolution="60", from_ts=None, to_ts=None):
        url = f"{self.BASE_URL}/market/udf/history"
        params = {"symbol": symbol, "resolution": resolution, "from": from_ts, "to": to_ts}
        
        try:
            print(f"   📡 Connecting to {url} ...")
            response = self.session.get(url, params=params, timeout=20, verify=False)
            
            if response.status_code == 200:
                data = response.json()
                if data.get("s") == "ok":
                    return data
                else:
                    return {"s": "error", "msg": f"API Error: {data.get('s')}"}
            else:
                return {"s": "error", "msg": f"HTTP {response.status_code}"}
                
        except Exception as e:
            return {"s": "error", "msg": f"{type(e).__name__}: {str(e)}"}
