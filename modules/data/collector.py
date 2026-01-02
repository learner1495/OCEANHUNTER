# modules/data/collector.py
import time
from typing import Dict, List, Optional
from modules.network import get_client
from .storage import get_storage

class DataCollector:
    def __init__(self):
        self.client = get_client()

    def test_connection(self):
        """Run DNS check"""
        return self.client.debug_dns()

    def fetch_ohlcv(self, symbol: str) -> tuple[List[Dict], str]:
        try:
            now = int(time.time())
            from_ts = now - (24 * 60 * 60)
            result = self.client.get_ohlcv(symbol=symbol, resolution="60", from_ts=from_ts, to_ts=now)
            
            if result.get("s") != "ok":
                return [], result.get("msg", "Unknown Error")
                
            candles = []
            timestamps = result.get("t", [])
            closes = result.get("c", [])
            for i in range(len(timestamps)):
                candles.append({"timestamp": timestamps[i], "close": float(closes[i])})
            return candles, ""
        except Exception as e:
            return [], str(e)

_collector: Optional[DataCollector] = None
def get_collector() -> DataCollector:
    global _collector
    if _collector is None:
        _collector = DataCollector()
    return _collector
