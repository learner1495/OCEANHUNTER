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

    def fetch_ohlcv(self, symbol: str, resolution: str = "60") -> List[Dict]:
        try:
            now = int(time.time())
            from_ts = now - (24 * 60 * 60) # Last 24h
            result = self.client.get_ohlcv(symbol=symbol, resolution=resolution, from_ts=from_ts, to_ts=now)
            
            if result.get("s") != "ok":
                # print(f"[Collector] API error for {symbol}: {result.get('s', 'unknown')}")
                return []
                
            candles = []
            timestamps = result.get("t", [])
            opens = result.get("o", [])
            highs = result.get("h", [])
            lows = result.get("l", [])
            closes = result.get("c", [])
            volumes = result.get("v", [])
            
            for i in range(len(timestamps)):
                candles.append({
                    "timestamp": timestamps[i],
                    "open": float(opens[i]) if i < len(opens) else 0,
                    "high": float(highs[i]) if i < len(highs) else 0,
                    "low": float(lows[i]) if i < len(lows) else 0,
                    "close": float(closes[i]) if i < len(closes) else 0,
                    "volume": float(volumes[i]) if i < len(volumes) else 0
                })
            return candles
        except Exception as e:
            print(f"[Collector] Error fetching {symbol}: {e}")
            return []

    def collect_symbol(self, symbol: str) -> Dict[str, Any]:
        result = {"symbol": symbol, "success": False, "candles_fetched": 0, "candles_saved": 0}
        candles = self.fetch_ohlcv(symbol)
        result["candles_fetched"] = len(candles)
        
        if not candles:
            return result
            
        saved = self.storage.save_ohlcv(symbol, candles)
        if saved:
            result["success"] = True
            result["candles_saved"] = len(candles)
        return result

    def collect_all(self) -> Dict[str, Any]:
        results = {"timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"), "symbols": {}, "total_candles": 0, "success_count": 0}
        
        for symbol in self.symbols:
            # print(f"      📊 Collecting {symbol}...")
            res = self.collect_symbol(symbol)
            results["symbols"][symbol] = res
            results["total_candles"] += res["candles_fetched"]
            
            if res["success"]:
                results["success_count"] += 1
                # print(f"         ✅ {res['candles_fetched']} candles")
            else:
                pass
                # print(f"         ❌ Failed")
            time.sleep(0.5)
            
        return results

    def get_summary(self) -> Dict[str, Any]:
        summary = {}
        for symbol in self.symbols:
            summary[symbol] = self.storage.get_stats(symbol)
        return summary

_collector: Optional[DataCollector] = None
def get_collector() -> DataCollector:
    global _collector
    if _collector is None:
        _collector = DataCollector()
    return _collector
