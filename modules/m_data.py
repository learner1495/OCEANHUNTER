import requests
import os
import csv
import time
from datetime import datetime

# --- CONFIG ---
MEXC_BASE = "https://api.mexc.com"
PROXY_URL = "http://127.0.0.1:10809"
PROXIES = {"http": PROXY_URL, "https": PROXY_URL}

class DataEngine:
    def __init__(self, data_dir="data"):
        self.data_dir = data_dir
        if not os.path.exists(self.data_dir):
            os.makedirs(self.data_dir)
            
    def fetch_candles(self, symbol, interval="60m", limit=50):
        """
        Fetch OHLCV Data from MEXC
        Intervals: 1m, 5m, 15m, 30m, 60m, 4h, 1d, 1M
        """
        endpoint = "/api/v3/klines"
        params = {
            "symbol": symbol,
            "interval": interval,
            "limit": limit
        }
        
        try:
            print(f"   ⬇️ Fetching {symbol} ({interval})...")
            resp = requests.get(
                f"{MEXC_BASE}{endpoint}", 
                params=params, 
                proxies=PROXIES, 
                verify=False, 
                timeout=10
            )
            
            if resp.status_code == 200:
                data = resp.json()
                # MEXC Format: [Open Time, Open, High, Low, Close, Volume, Close Time, ...]
                processed_data = []
                for candle in data:
                    processed_data.append({
                        "timestamp": candle[0],
                        "datetime": datetime.fromtimestamp(candle[0]/1000).strftime('%Y-%m-%d %H:%M:%S'),
                        "open": candle[1],
                        "high": candle[2],
                        "low": candle[3],
                        "close": candle[4],
                        "volume": candle[5]
                    })
                return processed_data
            else:
                print(f"   ❌ API Error: {resp.status_code} - {resp.text}")
                return []
                
        except Exception as e:
            print(f"   ❌ Connection Error: {e}")
            return []

    def save_to_csv(self, symbol, data):
        if not data:
            return False
            
        filename = os.path.join(self.data_dir, f"{symbol}_history.csv")
        keys = data[0].keys()
        
        try:
            with open(filename, 'w', newline='', encoding='utf-8') as f:
                writer = csv.DictWriter(f, fieldnames=keys)
                writer.writeheader()
                writer.writerows(data)
            print(f"   💾 Saved to {filename} ({len(data)} rows)")
            return True
        except Exception as e:
            print(f"   ❌ Save Error: {e}")
            return False
