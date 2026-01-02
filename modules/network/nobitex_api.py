# modules/network/nobitex_api.py
import requests
import urllib3

# Suppress SSL warnings (since we access via IP, SSL will complain)
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

class NobitexAPI:
    # WE USE THE IP FOUND BY YOUR NSLOOKUP
    DIRECT_IP = "178.22.122.100" 
    BASE_URL = f"https://{DIRECT_IP}"

    def __init__(self):
        self.session = requests.Session()
        self.session.trust_env = False
        
        self.session.headers.update({
            # We must tell the server which domain we want, 
            # even though we connect to the IP directly.
            "Host": "api.nobitex.ir",
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
            # verify=False is MANDATORY when using direct IP
            response = self.session.get(url, params=params, timeout=15, verify=False)
            
            if response.status_code == 200:
                data = response.json()
                # Check if API returned success status
                if data.get("s") == "ok":
                    return data
                else:
                    return {"s": "error", "msg": f"API Error: {data.get('s')}"}
            else:
                return {"s": "error", "msg": f"HTTP {response.status_code}"}
                
        except Exception as e:
            return {"s": "error", "msg": f"{type(e).__name__}: {str(e)}"}
