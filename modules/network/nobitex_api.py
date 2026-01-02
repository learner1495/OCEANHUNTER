# modules/network/nobitex_api.py
import requests
import time

class NobitexAPI:
    BASE_URL = "https://api.nobitex.ir"

    def __init__(self):
        self.session = requests.Session()
        # CRITICAL FIX: Bypass system proxies (broken VPNs)
        self.session.trust_env = False 
        
        self.session.headers.update({
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Accept": "application/json",
            "Connection": "keep-alive"
        })

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
            # Increased timeout to 20s
            response = self.session.get(url, params=params, timeout=20)
            
            if response.status_code == 200:
                data = response.json()
                if data.get("s") == "ok":
                    return data
                else:
                    return {"s": "error", "msg": f"API Status: {data.get('s')}", "debug": data}
            else:
                return {"s": "error", "msg": f"HTTP {response.status_code}", "code": response.status_code}
                
        except requests.exceptions.ProxyError:
            return {"s": "error", "msg": "Proxy Error (Check VPN)"}
        except requests.exceptions.ConnectionError:
            return {"s": "error", "msg": "Connection Failed (No Internet?)"}
        except requests.exceptions.Timeout:
            return {"s": "error", "msg": "Timeout (Slow Internet)"}
        except Exception as e:
            return {"s": "error", "msg": str(e)}
