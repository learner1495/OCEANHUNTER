# AI_Tools/build.py — Build V5.7.5 (SSL Disable & DNS Test)
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
# 1. NETWORK FIX (Disable SSL Verify + Debug Info)
# ═══════════════════════════════════════════════════════════════
NOBITEX_API_PY = '''# modules/network/nobitex_api.py
import requests
import socket
import urllib3

# Suppress SSL warnings for this diagnostic build
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

class NobitexAPI:
    BASE_URL = "https://api.nobitex.ir"

    def __init__(self):
        self.session = requests.Session()
        self.session.trust_env = False  # Bypass proxies
        self.session.headers.update({
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Accept": "application/json",
            "Connection": "keep-alive"
        })

    def debug_dns(self):
        """Check what IP Python sees for Nobitex"""
        try:
            domain = "api.nobitex.ir"
            ip = socket.gethostbyname(domain)
            return True, ip
        except Exception as e:
            return False, str(e)

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
            # FORCE DISABLE SSL VERIFICATION (verify=False)
            response = self.session.get(url, params=params, timeout=15, verify=False)
            
            if response.status_code == 200:
                data = response.json()
                if data.get("s") == "ok":
                    return data
                else:
                    return {"s": "error", "msg": f"API Status: {data.get('s')}", "debug": data}
            else:
                return {"s": "error", "msg": f"HTTP {response.status_code}", "code": response.status_code}
                
        except Exception as e:
            # Return full error details
            return {"s": "error", "msg": f"{type(e).__name__}: {str(e)}"}
'''

# ═══════════════════════════════════════════════════════════════
# 2. COLLECTOR (Pass-through errors)
# ═══════════════════════════════════════════════════════════════
COLLECTOR_PY = '''# modules/data/collector.py
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
'''

# ═══════════════════════════════════════════════════════════════
# 3. MAIN (Deep Diagnostic)
# ═══════════════════════════════════════════════════════════════
MAIN_PY = '''#!/usr/bin/env python3
"""OCEAN HUNTER V5.7.5 — Lab Test"""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from modules.data.collector import get_collector

def main():
    print("\\n" + "=" * 60)
    print("🔬 OCEAN HUNTER V5.7.5 — LAB TEST")
    print("=" * 60)
    
    collector = get_collector()
    
    # TEST 1: DNS
    print("\\n[TEST 1] 🌍 DNS Resolution (api.nobitex.ir)...")
    success, result = collector.test_connection()
    if success:
        print(f"      ✅ Resolved IP: {result}")
        print("      (This means Python CAN find the server)")
    else:
        print(f"      ❌ DNS FAILED: {result}")
        print("      (Python cannot find the server address)")
        return

    # TEST 2: HTTP REQUEST (SSL Disabled)
    print("\\n[TEST 2] 📡 Data Fetch (SSL Verify=False)...")
    symbol = "BTCIRT"
    candles, error = collector.fetch_ohlcv(symbol)
    
    if candles:
        price = candles[-1]['close']
        print(f"      ✅ SUCCESS! Price: {price:,.0f} IRT")
        print("      (Problem was SSL Certificate. We bypassed it.)")
    else:
        print(f"      ❌ CONNECTION FAILED: {error}")
        print("      (Check error details above)")

    print("\\n" + "=" * 60)
    if candles:
        print("🎉 GREAT! We found the solution.")
        print("   The script can now read data from Nobitex.")
    else:
        print("⚠️ STILL FAILING?")
        print("   If DNS passed but HTTP failed, Firewall might be blocking python.exe")
    print("=" * 60 + "\\n")

if __name__ == "__main__":
    main()
'''

FILES_TO_CREATE = {
    "modules/network/nobitex_api.py": NOBITEX_API_PY,
    "modules/data/collector.py": COLLECTOR_PY,
    "main.py": MAIN_PY
}

# ═══════════════════════════════════════════════════════════════
# BUILD STEPS
# ═══════════════════════════════════════════════════════════════
def step1_create_files():
    print("\n[1/4] 📝 Updating Files for Lab Test...")
    for path, content in FILES_TO_CREATE.items():
        full_path = os.path.join(ROOT, path)
        with open(full_path, "w", encoding="utf-8") as f:
            f.write(content)
        print(f"      ✅ Updated: {path}")

def step2_git():
    print("\n[2/4] 🐙 Git Sync...")
    try:
        setup_git.setup()
        setup_git.sync("Build V5.7.5: SSL Bypass Diagnostic")
        print("      ✅ Saved to History")
    except:
        pass

def step3_context():
    try:
        context_gen.create_context_file()
    except:
        pass

def step4_launch():
    print("\n[4/4] 🚀 Launching Lab Test...")
    subprocess.run([VENV_PYTHON, "main.py"], cwd=ROOT)

def main():
    print("\n🚀 STARTING BUILD V5.7.5...")
    step1_create_files()
    step2_git()
    step3_context()
    step4_launch()

if __name__ == "__main__":
    main()
