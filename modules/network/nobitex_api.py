# modules/network/nobitex_api.py
import requests
import time

class NobitexAPI:
    BASE_URL = "https://api.nobitex.ir"

    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            "User-Agent": "Mozilla/5.0 (compatible; OceanHunter/5.0)",
            "Accept": "application/json"
        })

    def get_ohlcv(self, symbol, resolution="60", from_ts=None, to_ts=None):
        """
        Fetches OHLCV data directly from Nobitex Public API
        """
        url = f"{self.BASE_URL}/market/udf/history"
        
        # Ensure timestamps are integers
        if from_ts: from_ts = int(from_ts)
        if to_ts: to_ts = int(to_ts)
        
        params = {
            "symbol": symbol,
            "resolution": resolution,
            "from": from_ts,
            "to": to_ts
        }
        
        try:
            # 10s timeout for direct connection
            response = self.session.get(url, params=params, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                if data.get("s") == "ok":
                    return data
                else:
                    return {"s": "error", "msg": "No data returned", "debug": data}
            else:
                return {"s": "error", "code": response.status_code}
                
        except Exception as e:
            return {"s": "error", "msg": str(e)}
