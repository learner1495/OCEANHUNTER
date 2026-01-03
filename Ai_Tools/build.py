# AI_Tools/build.py — Build V6.6 (Switch to MEXC)
# ═══════════════════════════════════════════════════════════════

import os
import sys
import subprocess
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
# 1. UPDATE .ENV TEMPLATE
# ═══════════════════════════════════════════════════════════════
def update_env_file():
    env_path = os.path.join(ROOT, ".env")
    
    # Check if MEXC keys exist, if not append them
    if os.path.exists(env_path):
        with open(env_path, "r", encoding="utf-8") as f:
            content = f.read()
        
        new_content = content
        if "MEXC_ACCESS_KEY" not in content and "MEXC_API_KEY" not in content:
            new_content += "\n\n# === MEXC CONFIG ===\n"
            new_content += "MEXC_API_KEY=your_api_key_here\n"
            new_content += "MEXC_SECRET_KEY=your_secret_key_here\n"
        
        # Force Proxy Config update to what we found working
        if "PROXY_PORT=10809" not in content:
            # Replace or append correct proxy settings
            new_content += "\n# === PROXY CONFIG (AUTO-FIXED) ===\n"
            new_content += "PROXY_TYPE=HTTP\n"
            new_content += "PROXY_PORT=10809\n"
            new_content += "PROXY_URL=http://127.0.0.1:10809\n"

        with open(env_path, "w", encoding="utf-8") as f:
            f.write(new_content)
            
    print("   ✅ .env file updated with MEXC & Proxy settings.")

# ═══════════════════════════════════════════════════════════════
# 2. MEXC CONNECTION TEST SCRIPT
# ═══════════════════════════════════════════════════════════════
MEXC_TEST_PY = '''import requests
import os
import time
import urllib3
from dotenv import load_dotenv

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
load_dotenv()

# We use the proxy found in V6.4/V6.5
PROXY_URL = "http://127.0.0.1:10809"
PROXIES = {"http": PROXY_URL, "https": PROXY_URL}

def main():
    print("-" * 50)
    print("🚀 OCEAN HUNTER V6.6 — MEXC ACTIVATION")
    print("-" * 50)
    print(f"🔌 Proxy: {PROXY_URL}")

    # 1. Public Endpoint Check (Ping)
    print("\\n[1] Pinging MEXC Public API...")
    try:
        url = "https://api.mexc.com/api/v3/ping"
        resp = requests.get(url, proxies=PROXIES, verify=False, timeout=10)
        
        if resp.status_code == 200:
            print("   ✅ MEXC Server is REACHABLE!")
            print(f"   Response: {resp.json()}")
        else:
            print(f"   ❌ Failed to ping: HTTP {resp.status_code}")
            return # Stop if we can't even ping
            
    except Exception as e:
        print(f"   ❌ Connection Error: {e}")
        print("   ⚠️ Ensure V2RayN is running on port 10809!")
        return

    # 2. Market Data Check
    print("\\n[2] Fetching BTC Price...")
    try:
        url = "https://api.mexc.com/api/v3/ticker/price?symbol=BTCUSDT"
        resp = requests.get(url, proxies=PROXIES, verify=False, timeout=10)
        data = resp.json()
        
        print(f"   💰 BTC Price: {data['price']} USDT")
        print("   ✅ Market Data Flow is WORKING.")
        
    except Exception as e:
        print(f"   ❌ Market Data Failed: {e}")

    # 3. Check for Credentials
    api_key = os.getenv("MEXC_API_KEY")
    secret_key = os.getenv("MEXC_SECRET_KEY")
    
    print("\\n[3] Checking Credentials...")
    if not api_key or "your_api_key" in api_key:
        print("   ⚠️  WARNING: API Key not set in .env file.")
        print("   👉 Please open .env and paste your MEXC keys.")
    else:
        print("   ✅ API Key found in config.")
        print("   (We will test trade authentication in the next step)")

if __name__ == "__main__":
    main()
'''

# ═══════════════════════════════════════════════════════════════
# BUILD STEPS
# ═══════════════════════════════════════════════════════════════
def main():
    print("\n🚀 BUILD V6.6 — SWITCH TO MEXC")
    
    # Update Env
    update_env_file()
    
    # Write the test file
    test_file = os.path.join(ROOT, "mexc_connect.py")
    with open(test_file, "w", encoding="utf-8") as f:
        f.write(MEXC_TEST_PY)
    print(f"   📝 Created mexc_connect.py")

    # Git Sync
    try:
        setup_git.setup()
        setup_git.sync("Build V6.6: Enable MEXC Support")
    except: pass

    # Run it
    print("\n" + "="*50)
    print("   RUNNING MEXC CONNECTION TEST...")
    print("="*50)
    subprocess.run([VENV_PYTHON, "mexc_connect.py"], cwd=ROOT)

if __name__ == "__main__":
    main()
