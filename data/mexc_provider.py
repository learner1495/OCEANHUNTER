
import os
import time
import hmac
import hashlib
import requests
import pandas as pd
from datetime import datetime
from dotenv import load_dotenv

class MEXCProvider:
    def __init__(self):
        load_dotenv()
        self.api_key = os.getenv("MEXC_API_KEY")
        self.secret_key = os.getenv("MEXC_SECRET_KEY")
        self.base_url = "https://api.mexc.com"
        
    def _get_signature(self, params):
        query_string = "&".join([f"{k}={v}" for k, v in sorted(params.items())])
        return hmac.new(self.secret_key.encode('utf-8'), query_string.encode('utf-8'), hashlib.sha256).hexdigest()

    def _request(self, method, endpoint, params=None, signed=False):
        url = f"{self.base_url}{endpoint}"
        params = params or {}
        
        headers = {"Content-Type": "application/json"}
        if signed:
            if not self.api_key or not self.secret_key:
                return None
            params["timestamp"] = int(time.time() * 1000)
            params["signature"] = self._get_signature(params)
            headers["X-MEXC-APIKEY"] = self.api_key

        try:
            if method == "GET":
                resp = requests.get(url, headers=headers, params=params, timeout=10)
            elif method == "POST":
                resp = requests.post(url, headers=headers, params=params, timeout=10)
                
            if resp.status_code == 200:
                return resp.json()
            return None
        except:
            return None

    def fetch_ohlcv(self, symbol="SOLUSDT", interval="1m", limit=100):
        endpoint = "/api/v3/klines"
        params = {"symbol": symbol, "interval": interval, "limit": limit}
        data = self._request("GET", endpoint, params=params, signed=False)
        
        if not data: return pd.DataFrame()

        df = pd.DataFrame(data, columns=[
            "timestamp", "open", "high", "low", "close", "volume", 
            "close_time", "q_vol", "trades", "taker_b_vol", "taker_q_vol", "ignore"
        ])
        df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
        numeric_cols = ['open', 'high', 'low', 'close', 'volume']
        df[numeric_cols] = df[numeric_cols].apply(pd.to_numeric, axis=1)
        return df[['timestamp', 'open', 'high', 'low', 'close', 'volume']]

    def get_balance(self, asset="USDT"):
        data = self._request("GET", "/api/v3/account", signed=True)
        if data and 'balances' in data:
            for b in data['balances']:
                if b['asset'] == asset:
                    return float(b['free'])
        return 0.0
