# AI_Tools/build.py — V5.4 (Architecture Sync + Network Fix Attempt)
# ═══════════════════════════════════════════════════════════════
# Ref: REF-ARCH-V10.8.2-FINAL-LOCK-610
# Updates:
# 1. NobitexAPI updated with OHLCV, Orderbook, Wallet (Per Arch Sec 2 & 15)
# 2. Hardened Network Adapter mounting to bypass Proxy
# ═══════════════════════════════════════════════════════════════

import os
import sys
import subprocess
import socket
import time

import context_gen
import setup_git

# ═══════════════════════════════════════════════════════════════
# PATHS
# ═══════════════════════════════════════════════════════════════
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(SCRIPT_DIR)
VENV_PATH = os.path.join(ROOT, ".venv")
ENV_FILE = os.path.join(ROOT, ".env")

if sys.platform == "win32":
    VENV_PYTHON = os.path.join(VENV_PATH, "Scripts", "python.exe")
else:
    VENV_PYTHON = os.path.join(VENV_PATH, "bin", "python")

errors = []

def log_error(step, error):
    errors.append(f"[{step}] {error}")
    print(f"      ⚠️ Error: {error}")

def write_file(path, content):
    try:
        with open(path, 'w', encoding='utf-8') as f:
            f.write(content.strip())
        print(f"      ✅ Wrote: {os.path.basename(path)}")
    except Exception as e:
        log_error("WriteFile", f"Failed to write {path}: {e}")

# ═══════════════════════════════════════════════════════════════
# CODE TEMPLATES (UPDATED PER ARCHITECTURE V10.8.2)
# ═══════════════════════════════════════════════════════════════

# Updated NobitexAPI with methods required for Strategy (OHLCV, Wallets)
NOBITEX_API_CODE = """
import requests
import json
import logging
import time
import os
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
from dotenv import load_dotenv
from modules.network.rate_limiter import RateLimiter

load_dotenv()
logger = logging.getLogger("NobitexAPI")

class NobitexAPI:
    BASE_URL = "https://api.nobitex.ir"

    def __init__(self, test_mode=False):
        self.token = os.getenv("NOBITEX_API_KEY") 
        self.test_mode = test_mode
        
        # Arch 2.5.1: 30 req/min limit (We use 25 for safety)
        self.rate_limiter = RateLimiter(max_calls=25, period=60)
        
        # Network Hardening: Force Direct Connection
        self.session = requests.Session()
        self.session.trust_env = False  # Ignore System Proxy
        self.session.proxies = {"http": None, "https": None} # Explicit No Proxy
        
        # Retry Logic for unstable networks
        retries = Retry(total=3, backoff_factor=1, status_forcelist=[500, 502, 503, 504])
        self.session.mount('https://', HTTPAdapter(max_retries=retries))

    def _get_headers(self):
        headers = {"content-type": "application/json"}
        if self.token:
            headers["Authorization"] = f"Token {self.token}"
        return headers

    def _send_request(self, method, endpoint, params=None, data=None, public=False):
        url = f"{self.BASE_URL}{endpoint}"
        self.rate_limiter.wait_if_needed()

        try:
            response = self.session.request(
                method=method,
                url=url,
                headers=self._get_headers(),
                params=params,
                data=json.dumps(data) if data else None,
                timeout=12 # Slight increase for VPN latency
            )

            if response.status_code != 200:
                logger.error(f"API Error [{response.status_code}]: {response.text}")
                return {"status": "error", "code": response.status_code, "message": response.text}

            return response.json()

        except requests.exceptions.ProxyError:
            return {"status": "error", "message": "Proxy/VPN Conflict"}
        except requests.exceptions.ConnectionError:
            return {"status": "error", "message": "Connection Failed (VPN Split Tunneling Required)"}
        except Exception as e:
            return {"status": "error", "message": str(e)}

    # ---------------------------------------------------------
    # PUBLIC ENDPOINTS (For Strategy & Analysis)
    # ---------------------------------------------------------
    
    def get_orderbook(self, symbol="BTCUSDT"):
        # Arch 2.2: Required for OBI Calculation
        return self._send_request("GET", f"/v2/orderbook/{symbol}", public=True)

    def get_market_stats(self, src="btc", dst="usdt"):
        # General health check
        return self._send_request("GET", "/market/stats", params={"src": src, "dst": dst}, public=True)
    
    def get_ohlcv(self, symbol="BTCUSDT", resolution="15", limit=100):
        # Arch 2.1: M15 Timeframe required
        # resolution: 15 (min), 60 (hour), D (day)
        params = {"symbol": symbol, "resolution": resolution, "limit": limit}
        return self._send_request("GET", "/market/udf/history", params=params, public=True)

    # ---------------------------------------------------------
    # PRIVATE ENDPOINTS (For Trading & Wallet)
    # ---------------------------------------------------------

    def get_wallet(self):
        # Arch 1.2: Capital Allocation (USDT, BTC, PAXG, etc.)
        return self._send_request("POST", "/users/wallets/list")

    def get_profile(self):
        return self._send_request("GET", "/users/profile")

    def check_connection(self):
        try:
            # 1. Test Public (OHLCV is light and good test)
            t0 = time.time()
            # Request M15 candles for BTC (Standard check)
            stats = self.get_ohlcv(symbol="BTCUSDT", resolution="15", limit=1)
            ping = (time.time() - t0) * 1000
            
            if not stats or stats.get("status") == "error":
                return False, f"Public API Failed: {stats.get('message')}"
            
            # Check if we actually got candle data (s = status: ok)
            if stats.get('s') != 'ok':
                 return False, f"Data Error: {stats}"

            # 2. Test Private
            auth_msg = "Skipped (No Token)"
            if self.token:
                profile = self.get_profile()
                if profile and profile.get("status") == "ok":
                    auth_msg = "Authenticated ✅"
                else:
                    auth_msg = f"Auth Failed ❌ ({profile.get('message')})"
            
            return True, f"Connected ({ping:.0f}ms) | {auth_msg}"
        except Exception as e:
            return False, str(e)
"""

# Telegram Bot (Untouched - it works)
TELEGRAM_BOT_CODE = """
import requests
import logging
import os
from dotenv import load_dotenv

load_dotenv()
logger = logging.getLogger("TelegramBot")

class TelegramBot:
    def __init__(self):
        self.token = os.getenv("TELEGRAM_BOT_TOKEN")
        self.chat_id = os.getenv("TELEGRAM_CHAT_ID")
        self.enabled = bool(self.token and self.chat_id)
        
        # ⚠️ TELEGRAM NEEDS VPN (Use System Proxy)
        self.session = requests.Session()
        self.session.trust_env = True 

    def send_message(self, message):
        if not self.enabled:
            return False

        url = f"https://api.telegram.org/bot{self.token}/sendMessage"
        payload = {
            "chat_id": self.chat_id,
            "text": message,
            "parse_mode": "Markdown"
        }

        try:
            response = self.session.post(url, json=payload, timeout=10)
            return response.status_code == 200
        except Exception as e:
            logger.error(f"Telegram Connection Error: {e}")
            return False
"""

RATE_LIMITER_CODE = """
import time
import logging
from collections import deque

logger = logging.getLogger("RateLimiter")

class RateLimiter:
    def __init__(self, max_calls=25, period=60):
        self.max_calls = max_calls
        self.period = period
        self.timestamps = deque()

    def wait_if_needed(self):
        now = time.time()
        while self.timestamps and self.timestamps[0] <= now - self.period:
            self.timestamps.popleft()

        if len(self.timestamps) >= self.max_calls:
            sleep_time = self.timestamps[0] + self.period - now + 0.1
            if sleep_time > 0:
                time.sleep(sleep_time)
            self.wait_if_needed()
        
        self.timestamps.append(time.time())
"""

INIT_NETWORK_CODE = """
from .nobitex_api import NobitexAPI
from .rate_limiter import RateLimiter
from .telegram_bot import TelegramBot
"""

# ═══════════════════════════════════════════════════════════════
# STEPS
# ═══════════════════════════════════════════════════════════════

def step1_system():
    print("\n[1/9] 🌐 System Check...")
    try:
        socket.create_connection(("8.8.8.8", 53), timeout=3)
        print("      ✅ Internet OK")
    except:
        log_error("Step1", "No internet access")

def step2_venv():
    print("\n[2/9] 🐍 Virtual Environment...")
    if os.path.exists(VENV_PYTHON):
        print("      ✅ Exists")
    else:
        log_error("Step2", "Venv missing")

def step3_deps():
    print("\n[3/9] 📦 Dependencies...")
    # Ensuring requests is installed
    subprocess.run([VENV_PYTHON, "-m", "pip", "install", "requests", "python-dotenv", "-q"], check=True)
    print("      ✅ Verified")

def step4_folders():
    print("\n[4/9] 📁 Folders...")
    net_path = os.path.join(ROOT, "modules", "network")
    if not os.path.exists(net_path):
        os.makedirs(net_path)
    print("      ✅ modules/network/ exists")

def step5_files():
    print("\n[5/9] 📝 Updating Files (Sync with V10.8.2)...")
    
    # 1. Nobitex API (New Version with OHLCV/Wallet)
    write_file(os.path.join(ROOT, "modules", "network", "nobitex_api.py"), NOBITEX_API_CODE)
    
    # 2. Others (Ensure consistency)
    write_file(os.path.join(ROOT, "modules", "network", "rate_limiter.py"), RATE_LIMITER_CODE)
    write_file(os.path.join(ROOT, "modules", "network", "telegram_bot.py"), TELEGRAM_BOT_CODE)
    write_file(os.path.join(ROOT, "modules", "network", "__init__.py"), INIT_NETWORK_CODE)

def step6_modify():
    print("\n[6/9] ✏️ Modify...")
    print("      ℹ️ Logic injected in Step 5")

def step7_context():
    print("\n[7/9] 📋 Context Generation...")
    try:
        context_gen.create_context_file()
        print("      ✅ Context updated")
    except Exception as e:
        log_error("Step7", e)

def step8_git():
    print("\n[8/9] 🐙 Git Sync...")
    try:
        setup_git.setup()
        setup_git.sync(f"Build V5.4: Network Logic Update (Arch V10.8.2 Sync)")
        print("      ✅ Git synced")
    except Exception as e:
        log_error("Step8", e)

def step9_launch():
    print("\n[9/9] 🚀 Network Diagnostic V5.4...")
    
    test_script = """
import sys
import os
import time
from dotenv import load_dotenv

sys.path.append(os.getcwd())
load_dotenv()

from modules.network.nobitex_api import NobitexAPI
from modules.network.telegram_bot import TelegramBot

print("-" * 60)
print("NETWORK DIAGNOSTIC V5.4 (Arch V10.8.2)")
print("-" * 60)

# 1. Test Telegram
print("\\n[1] Testing Telegram (VPN Required)...")
tg = TelegramBot()
if tg.enabled:
    msg = f"🌊 Ocean Hunter V10.8.2: Network Test V5.4\\n🕒 Time: {time.strftime('%H:%M:%S')}"
    if tg.send_message(msg):
        print("    ✅ Telegram Message Sent Successfully!")
    else:
        print("    ❌ Telegram Send Failed")
else:
    print("    ⚠️ Telegram Disabled (.env missing)")

# 2. Test Nobitex
print("\\n[2] Testing Nobitex (Direct Connection)...")
api = NobitexAPI()
success, msg = api.check_connection()

if success:
    print(f"    ✅ Nobitex Connected! Status: {msg}")
    print("    ℹ️  Testing Data Fetch (Architecture Check):")
    
    # Test OHLCV (Needed for Strategy)
    ohlcv = api.get_ohlcv("BTCUSDT", "15", 1)
    if ohlcv and ohlcv.get('s') == 'ok':
        print(f"       ✅ OHLCV (M15) Fetched: {ohlcv['t'][0]} -> {ohlcv['c'][0]}")
    else:
        print(f"       ❌ OHLCV Failed: {ohlcv}")

    # Test Wallet (Needed for Capital)
    if api.token:
        wallet = api.get_wallet()
        if wallet and wallet.get('status') == 'ok':
             print("       ✅ Wallet Data Accessible")
        else:
             print("       ❌ Wallet Data Inaccessible (Check Permissions)")

else:
    print(f"    ❌ Nobitex Failed: {msg}")
    print("\\n    🔴 CRITICAL ACTION REQUIRED:")
    print("       The VPN is still blocking direct connection to Iran.")
    print("       Since code-based bypass failed, you MUST enable 'Split Tunneling'")
    print("       in Turbo VPN and exclude 'python.exe'.")

print("-" * 60)
"""
    test_file = os.path.join(ROOT, "test_network_v4.py")
    with open(test_file, "w", encoding="utf-8") as f:
        f.write(test_script)
        
    subprocess.run([VENV_PYTHON, "test_network_v4.py"], cwd=ROOT)
    os.remove(test_file)

# ═══════════════════════════════════════════════════════════════
# MAIN
# ═══════════════════════════════════════════════════════════════

def main():
    print("\n" + "═" * 60)
    print(f"🔧 BUILD V5.4 — Architecture Sync + Network Hardening")
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
            print("✅ BUILD COMPLETE")
        print("═" * 60 + "\n")

if __name__ == "__main__":
    main()
