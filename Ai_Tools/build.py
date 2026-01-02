# AI_Tools/build.py — Build V5.7.3 (Integration Fix based on Screenshot)
# ═══════════════════════════════════════════════════════════════

import os
import sys
import subprocess
from datetime import datetime

import context_gen
import setup_git

# ═══════════════════════════════════════════════════════════════
# CONFIG
# ═══════════════════════════════════════════════════════════════
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(SCRIPT_DIR)
VENV_PATH = os.path.join(ROOT, ".venv")
if sys.platform == "win32":
    VENV_PYTHON = os.path.join(VENV_PATH, "Scripts", "python.exe")
else:
    VENV_PYTHON = os.path.join(VENV_PATH, "bin", "python")

# ═══════════════════════════════════════════════════════════════
# 1. NETWORK LAYER FIX (Adapting to nobitex_api.py)
# ═══════════════════════════════════════════════════════════════

# Updating __init__ to expose the API from nobitex_api.py
NETWORK_INIT = '''# modules/network/__init__.py
from .nobitex_api import NobitexAPI

_client_instance = None

def get_client():
    global _client_instance
    if _client_instance is None:
        _client_instance = NobitexAPI()
    return _client_instance
'''

# Standardizing nobitex_api.py to work with collector
NOBITEX_API_PY = '''# modules/network/nobitex_api.py
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
'''

# ═══════════════════════════════════════════════════════════════
# 2. DATA COLLECTOR (Syntax Fixed)
# ═══════════════════════════════════════════════════════════════
COLLECTOR_PY = '''# modules/data/collector.py
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
            
            # Calling the method on existing nobitex_api instance
            result = self.client.get_ohlcv(symbol=symbol, resolution=resolution, from_ts=from_ts, to_ts=now)
            
            if result.get("s") != "ok":
                # print(f"DEBUG: {result}")
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
                    "open": float(opens[i]),
                    "high": float(highs[i]),
                    "low": float(lows[i]),
                    "close": float(closes[i]),
                    "volume": float(volumes[i])
                })
            return candles
        except Exception as e:
            print(f"[Collector] Error processing {symbol}: {e}")
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
        results = {"timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"), "symbols": {}, "total_candles": 0}
        
        for symbol in self.symbols:
            res = self.collect_symbol(symbol)
            results["symbols"][symbol] = res
            results["total_candles"] += res["candles_fetched"]
            time.sleep(0.3) # Small delay to be polite
            
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
'''

# ═══════════════════════════════════════════════════════════════
# 3. ANALYSIS & MAIN
# ═══════════════════════════════════════════════════════════════
TECHNICAL_PY = '''# modules/analysis/technical.py
def calculate_rsi(prices, period=14):
    if len(prices) < period + 1: return 50
    gains, losses = [], []
    for i in range(1, len(prices)):
        delta = prices[i] - prices[i-1]
        gains.append(max(delta, 0))
        losses.append(abs(min(delta, 0)))
    if not gains: return 50
    avg_gain = sum(gains[-period:]) / period
    avg_loss = sum(losses[-period:]) / period
    if avg_loss == 0: return 100
    rs = avg_gain / avg_loss
    return round(100 - (100 / (1 + rs)), 2)

def analyze_market(symbol, candles):
    if not candles: return {"signal": "NEUTRAL", "reason": "No Data", "price": 0, "rsi": 0}
    closes = [c['close'] for c in candles]
    rsi = calculate_rsi(closes)
    signal, reason = "NEUTRAL", f"RSI {rsi}"
    if rsi < 30: signal, reason = "BUY 🟢", f"Oversold ({rsi})"
    elif rsi > 70: signal, reason = "SELL 🔴", f"Overbought ({rsi})"
    return {"symbol": symbol, "price": closes[-1], "rsi": rsi, "signal": signal, "reason": reason}
'''

MAIN_PY = '''#!/usr/bin/env python3
"""OCEAN HUNTER V5.7.3 — Standardized Network"""
import os, sys, time
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from dotenv import load_dotenv
from modules.data.collector import get_collector
from modules.analysis.technical import analyze_market

TARGET_COINS = ["BTCIRT", "ETHIRT", "DOGEIRT", "SHIBIRT", "PEPEIRT"]

def main():
    load_dotenv()
    print("\\n" + "=" * 60)
    print("🌊 OCEAN HUNTER V5.7.3 — File System Integrated")
    print("=" * 60)
    
    print("\\n[1] 🔌 Initializing Network (nobitex_api.py)...")
    try:
        collector = get_collector()
        collector.symbols = TARGET_COINS
        print("      ✅ Collector Ready")
    except Exception as e:
        print(f"      ❌ Failed to init collector: {e}")
        return

    print(f"      Watching: {', '.join(TARGET_COINS)}")
    print("\\n[2] 📊 Fetching & Analyzing Data...")
    print(f"      {'SYMBOL':<10} | {'PRICE (IRT)':<15} | {'RSI':<6} | {'SIGNAL'}")
    print("      " + "-" * 50)
    
    try:
        results = collector.collect_all()
    except Exception as e:
        print(f"      ❌ Collection Failed: {e}")
        return
    
    for symbol in TARGET_COINS:
        candles = collector.fetch_ohlcv(symbol)
        if candles:
            analysis = analyze_market(symbol, candles)
            print(f"      {symbol:<10} | {analysis['price']:<15,} | {analysis['rsi']:<6} | {analysis['signal']}")
            if "BUY" in analysis['signal'] or "SELL" in analysis['signal']:
                print(f"      Op >> 🔔 [MOCK] Alert: {analysis['reason']}")
        else:
            print(f"      {symbol:<10} | {'ERROR':<15} | {'---':<6} | ❌ No Data")
            
    print("\\n" + "=" * 60)
    print("✅ SCAN COMPLETE")
    print("=" * 60 + "\\n")

if __name__ == "__main__":
    main()
'''

FILES_TO_CREATE = {
    "modules/network/__init__.py": NETWORK_INIT,       # FIXED: Links to nobitex_api
    "modules/network/nobitex_api.py": NOBITEX_API_PY, # FIXED: Standardized methods
    "modules/data/collector.py": COLLECTOR_PY,         # FIXED: Syntax
    "modules/analysis/technical.py": TECHNICAL_PY,
    "main.py": MAIN_PY
}

# ═══════════════════════════════════════════════════════════════
# BUILD STEPS
# ═══════════════════════════════════════════════════════════════
def step1_create_files():
    print("\n[1/4] 📝 Synchronizing Files with Image Structure...")
    for path, content in FILES_TO_CREATE.items():
        full_path = os.path.join(ROOT, path)
        dir_name = os.path.dirname(full_path)
        if not os.path.exists(dir_name):
            os.makedirs(dir_name)
        
        with open(full_path, "w", encoding="utf-8") as f:
            f.write(content)
        print(f"      ✅ Updated: {path}")

def step2_git():
    print("\n[2/4] 🐙 Git Sync...")
    try:
        setup_git.setup()
        setup_git.sync("Build V5.7.3: Fix Network Import Error")
        print("      ✅ Saved to History")
    except:
        print("      ⚠️ Git skipped")

def step3_context():
    print("\n[3/4] 📋 Context Update...")
    try:
        context_gen.create_context_file()
        print("      ✅ Context Updated")
    except:
        pass

def step4_launch():
    print("\n[4/4] 🚀 Launching Scanner...")
    subprocess.run([VENV_PYTHON, "main.py"], cwd=ROOT)

def main():
    print("\n🚀 STARTING BUILD V5.7.3...")
    step1_create_files()
    step2_git()
    step3_context()
    step4_launch()

if __name__ == "__main__":
    main()
