# AI_Tools/build.py — Build V5.7.7 (Direct IP Connection)
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
# 1. NETWORK FIX (Hardcoded IP)
# ═══════════════════════════════════════════════════════════════
NOBITEX_API_PY = '''# modules/network/nobitex_api.py
import requests
import urllib3

# Suppress SSL warnings (since we access via IP, SSL will complain)
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

class NobitexAPI:
    # WE USE THE IP FOUND BY YOUR NSLOOKUP
    DIRECT_IP = "178.22.122.100" 
    BASE_URL = f"https://{DIRECT_IP}"

    def __init__(self):
        self.session = requests.Session()
        self.session.trust_env = False
        
        self.session.headers.update({
            # We must tell the server which domain we want, 
            # even though we connect to the IP directly.
            "Host": "api.nobitex.ir",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/120.0.0.0 Safari/537.36",
            "Accept": "application/json"
        })

    def get_ohlcv(self, symbol, resolution="60", from_ts=None, to_ts=None):
        url = f"{self.BASE_URL}/market/udf/history"
        
        params = {
            "symbol": symbol,
            "resolution": resolution,
            "from": from_ts,
            "to": to_ts
        }
        
        try:
            # verify=False is MANDATORY when using direct IP
            response = self.session.get(url, params=params, timeout=15, verify=False)
            
            if response.status_code == 200:
                data = response.json()
                # Check if API returned success status
                if data.get("s") == "ok":
                    return data
                else:
                    return {"s": "error", "msg": f"API Error: {data.get('s')}"}
            else:
                return {"s": "error", "msg": f"HTTP {response.status_code}"}
                
        except Exception as e:
            return {"s": "error", "msg": f"{type(e).__name__}: {str(e)}"}
'''

# ═══════════════════════════════════════════════════════════════
# 2. MAIN (Final Verification)
# ═══════════════════════════════════════════════════════════════
MAIN_PY = '''#!/usr/bin/env python3
"""OCEAN HUNTER V5.7.7 — IP Bypass Mode"""
import os, sys, time
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from modules.network.nobitex_api import NobitexAPI

def main():
    print("\\n" + "=" * 60)
    print("🚀 OCEAN HUNTER V5.7.7 — DIRECT IP BYPASS")
    print("=" * 60)

    print("\\n[TEST] Connecting to Nobitex via 178.22.122.100...")
    
    api = NobitexAPI()
    now = int(time.time())
    
    # Try to fetch Bitcoin data
    data = api.get_ohlcv("BTCIRT", from_ts=now-3600, to_ts=now)
    
    if data.get("s") == "ok":
        price = data['c'][-1]
        print(f"      ✅ SUCCESS! Connection Established!")
        print(f"      💰 Current BTC Price: {price:,.0f} IRT")
        print("      (We successfully bypassed the DNS blockage)")
    else:
        print(f"      ❌ FAILED: {data.get('msg')}")
        print("      If this fails, the Firewall is blocking the IP itself.")
        
    print("\\n" + "=" * 60)

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
    print("\n[1/4] 📝 Configuring IP Bypass...")
    for path, content in FILES_TO_CREATE.items():
        full_path = os.path.join(ROOT, path)
        with open(full_path, "w", encoding="utf-8") as f:
            f.write(content)
        print(f"      ✅ Updated: {path}")

def step2_git():
    print("\n[2/4] 🐙 Git Sync...")
    try:
        setup_git.setup()
        setup_git.sync("Build V5.7.7: Direct IP Connection")
        print("      ✅ Saved to History")
    except:
        pass

def step3_context():
    try:
        context_gen.create_context_file()
    except:
        pass

def step4_launch():
    print("\n[4/4] 🚀 Launching Bot...")
    subprocess.run([VENV_PYTHON, "main.py"], cwd=ROOT)

def main():
    print("\n🚀 STARTING BUILD V5.7.7...")
    step1_create_files()
    step2_git()
    step3_context()
    step4_launch()

if __name__ == "__main__":
    main()
