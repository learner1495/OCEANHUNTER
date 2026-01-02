# AI_Tools/build.py — Build V5.7.6 (DNS Fix & Proxy Cleaner)
# ═══════════════════════════════════════════════════════════════

import os
import sys
import subprocess
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
# 1. NETWORK FIX (Aggressive Proxy Cleaning)
# ═══════════════════════════════════════════════════════════════
NOBITEX_API_PY = '''# modules/network/nobitex_api.py
import requests
import os
import sys

# 1. PURGE PROXIES FROM ENVIRONMENT
# VPNs often leave these variables dirty
for k in ['HTTP_PROXY', 'HTTPS_PROXY', 'http_proxy', 'https_proxy']:
    if k in os.environ:
        print(f"      🧹 Removing dirty env var: {k}={os.environ[k]}")
        del os.environ[k]

class NobitexAPI:
    BASE_URL = "https://api.nobitex.ir"

    def __init__(self):
        self.session = requests.Session()
        self.session.trust_env = False  # Double check: Don't trust system proxy
        
        self.session.headers.update({
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Accept": "application/json",
            "Connection": "keep-alive"
        })

    def get_ohlcv(self, symbol, resolution="60", from_ts=None, to_ts=None):
        url = f"{self.BASE_URL}/market/udf/history"
        
        # Hardcoded params for testing
        params = {
            "symbol": symbol,
            "resolution": resolution,
            "from": from_ts,
            "to": to_ts
        }
        
        try:
            # timeout increased to 20
            response = self.session.get(url, params=params, timeout=20, verify=False)
            
            if response.status_code == 200:
                return response.json()
            else:
                return {"s": "error", "msg": f"HTTP {response.status_code}"}
                
        except Exception as e:
            return {"s": "error", "msg": f"{type(e).__name__}: {str(e)}"}
'''

# ═══════════════════════════════════════════════════════════════
# 2. MAIN (System Level Diagnosis)
# ═══════════════════════════════════════════════════════════════
MAIN_PY = '''#!/usr/bin/env python3
"""OCEAN HUNTER V5.7.6 — Network Exorcist"""
import os, sys, time, subprocess, socket
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from modules.network.nobitex_api import NobitexAPI

def run_cmd(cmd):
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, shell=True)
        return result.stdout.strip()
    except Exception as e:
        return str(e)

def main():
    print("\\n" + "=" * 60)
    print("🧹 OCEAN HUNTER V5.7.6 — NETWORK EXORCIST")
    print("=" * 60)

    # ---------------------------------------------------------
    # TEST 1: RAW INTERNET (PING GOOGLE DNS)
    # ---------------------------------------------------------
    print("\\n[TEST 1] 🌍 Pinging Google (8.8.8.8)...")
    # Using ping to check if network adapter works at all
    ping_res = run_cmd("ping -n 1 8.8.8.8")
    if "TTL=" in ping_res:
        print("      ✅ Internet Connection: ALIVE")
    else:
        print("      ❌ Internet Connection: DEAD (Check Cable/Wifi)")
        print(f"      Debug: {ping_res[:100]}...")

    # ---------------------------------------------------------
    # TEST 2: SYSTEM DNS (NSLOOKUP)
    # ---------------------------------------------------------
    print("\\n[TEST 2] 📖 System DNS Lookup (nslookup api.nobitex.ir)...")
    ns_res = run_cmd("nslookup api.nobitex.ir")
    
    resolved_ip = None
    if "Address" in ns_res:
        print("      ✅ System DNS: WORKING")
        # Extract IP roughly
        for line in ns_res.splitlines():
            if "Address" in line and "8.8.8.8" not in line: # simplistic
                print(f"      ℹ️  OS sees IP as: {line.split()[-1]}")
    else:
        print("      ❌ System DNS: FAILED")
        print("      (Windows itself cannot find Nobitex)")
        print(ns_res)

    # ---------------------------------------------------------
    # TEST 3: PYTHON REQUEST (CLEAN ENV)
    # ---------------------------------------------------------
    print("\\n[TEST 3] 🐍 Python Request (Proxies Purged)...")
    api = NobitexAPI() # This cleans env vars in __init__
    
    now = int(time.time())
    data = api.get_ohlcv("BTCIRT", from_ts=now-3600, to_ts=now)
    
    if data.get("s") == "ok":
        price = data['c'][-1]
        print(f"      ✅ SUCCESS! Price: {price} IRT")
        print("      (Removing proxy variables fixed it!)")
    else:
        print(f"      ❌ FAILED: {data.get('msg')}")
        
    print("\\n" + "=" * 60)
    print("DIAGNOSIS SUMMARY:")
    print("1. If Test 1 fails: You have no internet.")
    print("2. If Test 2 fails: Your Windows DNS is broken (try 'ipconfig /flushdns').")
    print("3. If Test 3 fails but Test 2 passes: Python is blocked by Firewall.")
    print("=" * 60 + "\\n")

if __name__ == "__main__":
    main()
'''

FILES_TO_CREATE = {
    "modules/network/nobitex_api.py": NOBITEX_API_PY,
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
        setup_git.sync("Build V5.7.6: DNS & Proxy Fix")
        print("      ✅ Saved to History")
    except:
        pass

def step3_context():
    try:
        context_gen.create_context_file()
    except:
        pass

def step4_launch():
    print("\n[4/4] 🚀 Launching Exorcist...")
    subprocess.run([VENV_PYTHON, "main.py"], cwd=ROOT)

def main():
    print("\n🚀 STARTING BUILD V5.7.6...")
    step1_create_files()
    step2_git()
    step3_context()
    step4_launch()

if __name__ == "__main__":
    main()
