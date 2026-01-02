# modules/data/collector.py
import time
from datetime import datetime
from typing import Dict, Any, List, Optional
from modules.network import get_client
from .storage import get_storage

class DataCollector:
    DEFAULT_SYMBOLS = ["BTCIRT", "ETHIRT", "USDTIRT"]

    def __init__(self):
        self.client = get_client()
        self.storage = get_storage()
        self.symbols = self.DEFAULT_SYMBOLS.copy()

    def fetch_ohlcv(self, symbol: str, resolution: str = "60") -> tuple[List[Dict], str]:
        """Returns (candles, error_message)"""
        try:
            now = int(time.time())
            from_ts = now - (24 * 60 * 60) # Last 24h
            
            result = self.client.get_ohlcv(symbol=symbol, resolution=resolution, from_ts=from_ts, to_ts=now)
            
            if result.get("s") != "ok":
                error_msg = result.get("msg", "Unknown API Error")
                return [], error_msg
                
            candles = []
            timestamps = result.get("t", [])
            closes = result.get("c", [])
            
            # Simplified for checking connection
            for i in range(len(timestamps)):
                candles.append({
                    "timestamp": timestamps[i],
                    "close": float(closes[i])
                })
            return candles, ""
            
        except Exception as e:
            return [], str(e)

    def collect_all(self):
        pass # Not used in main right now

_collector: Optional[DataCollector] = None
def get_collector() -> DataCollector:
    global _collector
    if _collector is None:
        _collector = DataCollector()
    return _collector
