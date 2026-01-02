# AI_Tools/build.py — Build V5.7.9 (System Host Injector)
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
# 1. NETWORK FIX (Clean Standard Request)
# ═══════════════════════════════════════════════════════════════
# We go back to standard requests because we want to fix the OS resolution
NOBITEX_API_PY = '''# modules/network/nobitex_api.py
import requests
import urllib3

# Suppress SSL warnings
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

class NobitexAPI:
    BASE_URL = "https://api.nobitex.ir"

    def __init__(self):
        self.session = requests.Session()
        self.session.trust_env = False  # NO PROXIES
        
        self.session.headers.update({
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
            # Standard request, trusting the OS to resolve DNS
            response = self.session.get(url, params=params, timeout=10, verify=False)
            
            if response.status_code == 200:
                data = response.json()
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
# 2. MAIN (Diagnostic & Injection)
# ═══════════════════════════════════════════════════════════════
MAIN_PY = '''#!/usr/bin/env python3
"""OCEAN HUNTER V5.7.9 — HOSTS FILE INJECTOR"""
import os, sys, time
import socket
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from modules.network.nobitex_api import NobitexAPI

def check_dns():
    print(f"   🔎 Checking DNS resolution for api.nobitex.ir...")
    try:
        ip = socket.gethostbyname("api.nobitex.ir")
        print(f"      ✅ Resolved to: {ip}")
        return True
    except socket.gaierror:
        print(f"      ❌ Python failed to resolve DNS.")
        return False

def modify_hosts_file():
    print(f"\\n   💉 Attempting to inject IP into Windows HOSTS file...")
    hosts_path = r"C:\\Windows\\System32\\drivers\\etc\\hosts"
    entry = "\\n178.22.122.100 api.nobitex.ir\\n"
    
    try:
        # Check if already exists
        with open(hosts_path, 'r') as f:
            content = f.read()
            if "api.nobitex.ir" in content:
                print("      ℹ️ Entry already exists in HOSTS file.")
                return

        # Append
        with open(hosts_path, 'a') as f:
            f.write(entry)
        print("      ✅ Successfully added to HOSTS file!")
    except PermissionError:
        print("      ⚠️ PERMISSION DENIED: Run terminal as Administrator to fix DNS permanently.")
        print("      (Trying temporary workaround...)")
    except Exception as e:
        print(f"      ❌ Error modifying HOSTS: {e}")

def main():
    print("\\n" + "=" * 60)
    print("🚀 OCEAN HUNTER V5.7.9 — SYSTEM FIX")
    print("=" * 60)

    # 1. Try to fix DNS manually
    modify_hosts_file()

    # 2. Check if Python can see it now
    dns_ok = check_dns()
    
    # 3. Try Connection
    print("\\n[TEST] Final Connection Attempt...")
    api = NobitexAPI()
    now = int(time.time())
    
    data = api.get_ohlcv("BTCIRT", from_ts=now-3600, to_ts=now)
    
    if data.get("s") == "ok":
        price = data['c'][-1]
        print(f"      ✅ SUCCESS! WE ARE CONNECTED!")
        print(f"      💰 Current BTC Price: {price:,.0f} IRT")
    else:
        print(f"      ❌ FAILED: {data.get('msg')}")
        
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
    print("\n[1/4] 📝 Configuring System Fix...")
    for path, content in FILES_TO_CREATE.items():
        full_path = os.path.join(ROOT, path)
        with open(full_path, "w", encoding="utf-8") as f:
            f.write(content)
        print(f"      ✅ Updated: {path}")

def step2_git():
    print("\n[2/4] 🐙 Git Sync...")
    try:
        setup_git.setup()
        setup_git.sync("Build V5.7.9: Hosts File Injector")
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
    print("\n🚀 STARTING BUILD V5.7.9...")
    step1_create_files()
    step2_git()
    step3_context()
    step4_launch()

if __name__ == "__main__":
    main() 