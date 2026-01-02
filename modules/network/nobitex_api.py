# modules/network/nobitex_api.py
import requests
import urllib3
from requests.adapters import HTTPAdapter
from urllib3.util import connection

# Suppress SSL warnings
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# --- MAGIC TRICK: FORCE DNS RESOLUTION ---
# This overrides the system DNS and forces Python to connect 
# to the specific working IP for api.nobitex.ir

ORIGIN_CONNECT = connection.create_connection

def patched_create_connection(address, *args, **kwargs):
    host, port = address
    if host == "api.nobitex.ir":
        # We force the IP we found earlier
        return ORIGIN_CONNECT(("178.22.122.100", port), *args, **kwargs)
    return ORIGIN_CONNECT(address, *args, **kwargs)

connection.create_connection = patched_create_connection
# ------------------------------------------

class NobitexAPI:
    BASE_URL = "https://api.nobitex.ir"

    def __init__(self):
        self.session = requests.Session()
        self.session.trust_env = False  # Ignore system proxies
        
        self.session.headers.update({
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/120.0.0.0 Safari/537.36",
            "Accept": "application/json"
        })

    def get_ohlcv(self, symbol, resolution="60", from_ts=None, to_ts=None):
        url = f"{self.BASE_URL}/market/udf/history"
        
        params = {
            "symbol": symbol,
            "resolution": resolution,
            "from": from_ts,
            "to": to_ts
        }
        
        try:
            # We use the domain name, but the patch above forces it to the IP
            response = self.session.get(url, params=params, timeout=15, verify=False)
            
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
