# AI_Tools/build.py — Build V5.7.4 (Direct Connection Fix)
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
# 1. NETWORK FIX (Bypass System Proxy)
# ═══════════════════════════════════════════════════════════════
NOBITEX_API_PY = '''# modules/network/nobitex_api.py
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
'''

# ═══════════════════════════════════════════════════════════════
# 2. COLLECTOR (Show Errors)
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
'''

# ═══════════════════════════════════════════════════════════════
# 3. MAIN (Debug Output)
# ═══════════════════════════════════════════════════════════════
MAIN_PY = '''#!/usr/bin/env python3
"""OCEAN HUNTER V5.7.4 — Connectivity Diagnostic"""
import os, sys, time
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from dotenv import load_dotenv
from modules.data.collector import get_collector

TARGET_COINS = ["BTCIRT", "ETHIRT", "DOGEIRT"]

def main():
    load_dotenv()
    print("\\n" + "=" * 60)
    print("🌊 OCEAN HUNTER V5.7.4 — Direct Connection Mode")
    print("   ⚠️  Ignoring System Proxies (Bypassing VPN settings)")
    print("=" * 60)
    
    print("\\n[1] 🔌 Initializing Network...")
    try:
        collector = get_collector()
        print("      ✅ Collector Ready")
    except Exception as e:
        print(f"      ❌ Failed to init: {e}")
        return

    print("\\n[2] 📡 Testing Connectivity to Nobitex...")
    print(f"      {'SYMBOL':<10} | {'STATUS':<15} | {'DETAIL'}")
    print("      " + "-" * 50)
    
    success_count = 0
    for symbol in TARGET_COINS:
        candles, error = collector.fetch_ohlcv(symbol)
        
        if candles:
            last_price = candles[-1]['close']
            print(f"      {symbol:<10} | {'✅ ONLINE':<15} | Price: {last_price:,.0f} IRT")
            success_count += 1
        else:
            print(f"      {symbol:<10} | {'❌ FAILED':<15} | {error}")
            
    print("\\n" + "=" * 60)
    if success_count == 0:
        print("❌ CRITICAL: No connection.")
        print("   Suggestion: Turn OFF all VPNs completely and retry.")
    else:
        print("✅ SUCCESS: Connection Established!")
    print("=" * 60 + "\\n")

if __name__ == "__main__":
    main()
'''

FILES_TO_CREATE = {
    "modules/network/nobitex_api.py": NOBITEX_API_PY, # Updated with Proxy Bypass
    "modules/data/collector.py": COLLECTOR_PY,        # Updated to return errors
    "main.py": MAIN_PY
}

# ═══════════════════════════════════════════════════════════════
# BUILD STEPS
# ═══════════════════════════════════════════════════════════════
def step1_create_files():
    print("\n[1/4] 📝 Updating Network Logic...")
    for path, content in FILES_TO_CREATE.items():
        full_path = os.path.join(ROOT, path)
        with open(full_path, "w", encoding="utf-8") as f:
            f.write(content)
        print(f"      ✅ Updated: {path}")

def step2_git():
    print("\n[2/4] 🐙 Git Sync...")
    try:
        setup_git.setup()
        setup_git.sync("Build V5.7.4: Direct Connection Fix")
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
    print("\n[4/4] 🚀 Launching Diagnostic...")
    subprocess.run([VENV_PYTHON, "main.py"], cwd=ROOT)

def main():
    print("\n🚀 STARTING BUILD V5.7.4...")
    step1_create_files()
    step2_git()
    step3_context()
    step4_launch()

if __name__ == "__main__":
    main()
