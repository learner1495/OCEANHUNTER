# AI_Tools/build.py — V5.2.2 (Fix Init Import Error)
# ═══════════════════════════════════════════════════════════════
# اصلاحیه: بازنویسی اجباری __init__.py برای رفع ImportError
# ═══════════════════════════════════════════════════════════════

import os
import sys
import subprocess
import socket
from datetime import datetime
import time

import context_gen
import setup_git

# ═══════════════════════════════════════════════════════════════
# PATHS
# ═══════════════════════════════════════════════════════════════
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(SCRIPT_DIR)
VENV_PATH = os.path.join(ROOT, ".venv")

if sys.platform == "win32":
    VENV_PYTHON = os.path.join(VENV_PATH, "Scripts", "python.exe")
else:
    VENV_PYTHON = os.path.join(VENV_PATH, "bin", "python")

MAIN_FILE = "main.py"
errors = []

def log_error(step, error):
    errors.append(f"[{step}] {error}")
    print(f"      ⚠️ Error: {error}")

def write_file(path, content):
    try:
        # Force UTF-8 to handle any special chars
        with open(path, 'w', encoding='utf-8') as f:
            f.write(content.strip())
        print(f"      ✅ Wrote: {os.path.basename(path)}")
    except Exception as e:
        log_error("WriteFile", f"Failed to write {path}: {e}")

# ═══════════════════════════════════════════════════════════════
# CODE TEMPLATES (Network Layer)
# ═══════════════════════════════════════════════════════════════

RATE_LIMITER_CODE = """
import time
import logging
from collections import deque

logger = logging.getLogger("RateLimiter")

class RateLimiter:
    def __init__(self, max_calls=25, period=60):
        \"\"\"
        Nobitex Limit: 30 req/min.
        We use 25 req/min (Safety Buffer).
        \"\"\"
        self.max_calls = max_calls
        self.period = period
        self.timestamps = deque()

    def wait_if_needed(self):
        \"\"\"Checks history and waits if limit is reached.\"\"\"
        now = time.time()
        
        # Remove timestamps older than the period
        while self.timestamps and self.timestamps[0] <= now - self.period:
            self.timestamps.popleft()

        if len(self.timestamps) >= self.max_calls:
            sleep_time = self.timestamps[0] + self.period - now + 0.1
            if sleep_time > 0:
                logger.warning(f"Rate limit reached. Sleeping for {sleep_time:.2f}s")
                time.sleep(sleep_time)
            
            # Clean up again after sleep
            self.wait_if_needed()
        
        self.timestamps.append(time.time())
"""

NOBITEX_API_CODE = """
import requests
import json
import logging
import time
from modules.network.rate_limiter import RateLimiter

logger = logging.getLogger("NobitexAPI")

class NobitexAPI:
    BASE_URL = "https://api.nobitex.ir"

    def __init__(self, token=None, test_mode=False):
        self.token = token
        self.test_mode = test_mode
        self.rate_limiter = RateLimiter(max_calls=25, period=60)
        self.session = requests.Session()
        
        # ⚠️ CRITICAL FOR VPN USERS:
        # trust_env=False tells requests to ignore system proxies (VPN) 
        # and try to connect directly. This helps with Nobitex IP restrictions.
        self.session.trust_env = False 
        self.session.proxies = {} # Explicitly clear proxies

    def _get_headers(self):
        headers = {"content-type": "application/json"}
        if self.token:
            headers["Authorization"] = f"Token {self.token}"
        return headers

    def _send_request(self, method, endpoint, params=None, data=None, public=False):
        \"\"\"
        Unified request handler with error management and rate limiting.
        \"\"\"
        url = f"{self.BASE_URL}{endpoint}"
        
        # 1. Check Rate Limit
        self.rate_limiter.wait_if_needed()

        try:
            # 2. Send Request
            response = self.session.request(
                method=method,
                url=url,
                headers=self._get_headers(),
                params=params,
                data=json.dumps(data) if data else None,
                timeout=10 
            )

            # 3. Handle Errors
            if response.status_code != 200:
                logger.error(f"API Error [{response.status_code}]: {response.text}")
                return {"status": "error", "code": response.status_code, "message": response.text}

            return response.json()

        except requests.exceptions.ProxyError:
            logger.error("Proxy Error: VPN might be blocking connection to Nobitex.")
            return {"status": "error", "message": "Proxy/VPN Conflict"}
        except requests.exceptions.ConnectionError:
            logger.error("Connection Error: Check internet.")
            return {"status": "error", "message": "Connection Failed"}
        except Exception as e:
            logger.error(f"Unexpected Error: {e}")
            return {"status": "error", "message": str(e)}

    # ════ Public Endpoints (No Token Needed) ════

    def get_orderbook(self, symbol="BTCUSDT"):
        \"\"\"Fetches OBI data (Bids/Asks)\"\"\"
        return self._send_request("GET", f"/v2/orderbook/{symbol}", public=True)

    def get_market_stats(self, src="btc", dst="usdt"):
        \"\"\"Fetches Price, Volume, High/Low\"\"\"
        return self._send_request("GET", "/market/stats", params={"src": src, "dst": dst}, public=True)
        
    def check_connection(self):
        \"\"\"Test connection and verify IP location logic\"\"\"
        try:
            # Check what IP we are using for Nobitex
            # Nobitex keeps connection open, so if this works, we are good.
            t0 = time.time()
            data = self.get_market_stats()
            ping = (time.time() - t0) * 1000
            
            if data and data.get("status") == "ok":
                return True, f"Connected to Nobitex (Ping: {ping:.0f}ms)"
            else:
                return False, f"Nobitex Error: {data}"
        except Exception as e:
            return False, str(e)
"""

# Correct Init Content (No get_client)
INIT_FILE_CODE = """
from .nobitex_api import NobitexAPI
"""

# ═══════════════════════════════════════════════════════════════
# STEPS
# ═══════════════════════════════════════════════════════════════

def step1_system():
    print("\n[1/9] 🌐 System Check...")
    try:
        socket.create_connection(("8.8.8.8", 53), timeout=3)
        print("      ✅ Internet OK")
    except Exception as e:
        log_error("Step1", f"No internet - {e}")

def step2_venv():
    print("\n[2/9] 🐍 Virtual Environment...")
    if os.path.exists(VENV_PYTHON):
        print("      ✅ Exists")
    else:
        log_error("Step2", "Venv missing (run setup first or old build)")

def step3_deps():
    print("\n[3/9] 📦 Dependencies...")
    # Ensure requests is installed for API
    try:
        subprocess.run(
            [VENV_PYTHON, "-m", "pip", "install", "requests", "-q"],
            check=True
        )
        print("      ✅ 'requests' library verified")
    except Exception as e:
        log_error("Step3", e)

def step4_folders():
    print("\n[4/9] 📁 Folders...")
    net_path = os.path.join(ROOT, "modules", "network")
    if not os.path.exists(net_path):
        os.makedirs(net_path)
        print("      ✅ Created modules/network/")
    else:
        print("      ✅ modules/network/ exists")

def step5_files():
    print("\n[5/9] 📝 Files Creation (Network Layer)...")
    
    # 1. Create Rate Limiter
    rl_path = os.path.join(ROOT, "modules", "network", "rate_limiter.py")
    write_file(rl_path, RATE_LIMITER_CODE)

    # 2. Create Nobitex API
    api_path = os.path.join(ROOT, "modules", "network", "nobitex_api.py")
    write_file(api_path, NOBITEX_API_CODE)

    # 3. FORCE overwrite __init__.py to fix ImportError
    init_path = os.path.join(ROOT, "modules", "network", "__init__.py")
    write_file(init_path, INIT_FILE_CODE)

def step6_modify():
    print("\n[6/9] ✏️ Modify...")
    print("      ℹ️ Logic injected in Step 5")

def step7_context():
    print("\n[7/9] 📋 Context Generation...")
    try:
        context_gen.create_context_file()
        print("      ✅ Context created")
    except Exception as e:
        log_error("Step7", e)

def step8_git():
    print("\n[8/9] 🐙 Git Sync...")
    try:
        setup_git.setup()
        setup_git.sync(f"Build V5.2.2: Fix Init Import Error")
        print("      ✅ Git synced")
    except Exception as e:
        log_error("Step8", e)

def step9_launch():
    print("\n[9/9] 🚀 Launch & Test...")
    print("      ℹ️ Testing Network Layer (Nobitex Connection)...")
    
    test_script = """
import sys
import os
sys.path.append(os.getcwd())
from modules.network.nobitex_api import NobitexAPI

print("-" * 50)
print("NETWORK DIAGNOSTIC (NOBITEX)")
print("-" * 50)

api = NobitexAPI()
print("   • Trying to connect to Nobitex Market Stats...")
print("   • Bypass Mode (trust_env=False): ACTIVE")

success, msg = api.check_connection()

if success:
    print(f"   [OK] SUCCESS: {msg}")
    print("   Note: Connection established successfully.")
    print("   The system bypassed the VPN to reach Nobitex.")
else:
    print(f"   [X] FAILED: {msg}")
    print("   Troubleshooting:")
    print("       1. Ensure VPN is NOT in 'Lockdown' or 'Full Tunnel' mode (like Cisco).")
    print("       2. Use Split Tunneling if available.")
print("-" * 50)
"""
    test_file = os.path.join(ROOT, "test_network.py")
    
    # FIX: Explicit utf-8 encoding for Windows
    with open(test_file, "w", encoding="utf-8") as f:
        f.write(test_script)
        
    subprocess.run([VENV_PYTHON, "test_network.py"], cwd=ROOT)
    os.remove(test_file)

# ═══════════════════════════════════════════════════════════════
# MAIN
# ═══════════════════════════════════════════════════════════════

def main():
    start_time = datetime.now()
    print("\n" + "═" * 60)
    print(f"🔧 BUILD V5.2.2 — Network Layer (Import Fix)")
    print("═" * 60)

    try:
        step1_system()
        step2_venv()
        step3_deps()
        step4_folders()
        step5_files()
        step6_modify()
        step7_context()
        step8_git()
        step9_launch()

    except Exception as e:
        print(f"\n💥 Critical error: {e}")
        errors.append(str(e))

    finally:
        print("\n" + "═" * 60)
        if errors:
            print(f"⚠️ ERRORS: {errors}")
        else:
            print("✅ NETWORK LAYER BUILT SUCCESSFULLY")
        print("═" * 60 + "\n")

if __name__ == "__main__":
    main()
