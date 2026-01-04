# AI_Tools/build.py — Phase 8: Live Connection Setup (SYNTAX FIX)
# ═══════════════════════════════════════════════════════════════
# Ref: OCEAN-HUNTER-PHASE8-FIX-SYNTAX
# ═══════════════════════════════════════════════════════════════

import os
import sys
import subprocess

# ═══ Import Internal Modules ═══
try:
    import context_gen
    import setup_git
except ImportError:
    pass 

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(SCRIPT_DIR)
VENV_PATH = os.path.join(ROOT, ".venv")
VENV_PYTHON = os.path.join(VENV_PATH, "Scripts", "python.exe") if sys.platform == "win32" else os.path.join(VENV_PATH, "bin", "python")

# ═══════════════════════════════════════════════════════════════
# ⭐ LIVE CONNECTION TEST SCRIPT (ESCAPED CHARACTERS FIXED)
# ═══════════════════════════════════════════════════════════════

CHECK_LIVE_SCRIPT = """
import os
import sys
import time
import hmac
import hashlib
import requests
import json
from datetime import datetime
from dotenv import load_dotenv

# Add Root to path
sys.path.append(os.getcwd())

# Load Env
load_dotenv()

# Configuration
API_KEY = os.getenv("MEXC_API_KEY")
SECRET_KEY = os.getenv("MEXC_SECRET_KEY")
BASE_URL = "https://api.mexc.com"

# Telegram Config
TG_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
TG_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

def send_telegram(msg):
    if not TG_TOKEN or not TG_CHAT_ID: return
    try:
        url = f"https://api.telegram.org/bot{TG_TOKEN}/sendMessage"
        payload = {"chat_id": TG_CHAT_ID, "text": msg, "parse_mode": "HTML"}
        requests.post(url, json=payload, timeout=5)
    except: pass

def get_signature(params):
    query_string = "&".join([f"{k}={v}" for k, v in sorted(params.items())])
    return hmac.new(SECRET_KEY.encode('utf-8'), query_string.encode('utf-8'), hashlib.sha256).hexdigest()

def check_connection():
    print("🔌 Initiating LIVE Connection to MEXC Global...")
    
    if not API_KEY or "CHANGE_ME" in API_KEY or len(API_KEY) < 10:
        print("❌ ERROR: API_KEY is invalid or not set in .env")
        print("👉 Please open .env file and paste your MEXC API Keys.")
        sys.exit(1)

    headers = {
        "X-MEXC-APIKEY": API_KEY,
        "Content-Type": "application/json"
    }

    # 1. Check Server Time (Public Endpoint)
    try:
        resp = requests.get(f"{BASE_URL}/api/v3/time", timeout=10)
        server_time = resp.json()['serverTime']
        print(f"✅ Public API OK. Server Time: {server_time}")
    except Exception as e:
        print(f"❌ Public API Connection Failed: {e}")
        print("👉 Check your VPN/Internet connection.")
        sys.exit(1)

    # 2. Check Account Balance (Private Endpoint - Signature Required)
    timestamp = int(time.time() * 1000)
    params = {"timestamp": timestamp}
    params["signature"] = get_signature(params)
    
    print("🔑 Authenticating...")
    try:
        resp = requests.get(f"{BASE_URL}/api/v3/account", headers=headers, params=params, timeout=10)
        
        if resp.status_code == 200:
            data = resp.json()
            balances = [b for b in data['balances'] if float(b['free']) > 0 or float(b['locked']) > 0]
            
            print(f"✅ AUTHENTICATION SUCCESSFUL!")
            print(f"💰 Account Type: {data['accountType']}")
            
            balance_str = ""
            if balances:
                print("💼 WALLET CONTENTS:")
                for b in balances:
                    print(f"   - {b['asset']}: {b['free']} (Locked: {b['locked']})")
                    # Double escape needed for file generation
                    balance_str += f"🔹 <b>{b['asset']}</b>: <code>{b['free']}</code>\\n"
            else:
                print("   (Wallet is Empty)")
                balance_str = "🔹 Wallet is Empty (0.00)\\n"

            # Success Message
            msg = (
                "🚀 <b>Ocean Hunter: LIVE SYSTEM ONLINE</b>\\n\\n"
                "✅ <b>Connection Established</b>\\n"
                "🏦 Exchange: <code>MEXC Global</code>\\n"
                f"{balance_str}\\n"
                "🤖 <i>Ready for Real Trading.</i>"
            )
            send_telegram(msg)
            return True
            
        else:
            print(f"❌ AUTH FAILED: HTTP {resp.status_code}")
            print(f"⚠️ Response: {resp.text}")
            return False

    except Exception as e:
        print(f"❌ Critical Error during Auth: {e}")
        return False

if __name__ == "__main__":
    success = check_connection()
    if not success:
        sys.exit(1)
"""

# ═══════════════════════════════════════════════════════════════
# CONFIGURATION
# ═══════════════════════════════════════════════════════════════
NEW_FILES = {
    "tools/check_live_connection.py": CHECK_LIVE_SCRIPT
}

# ═══════════════════════════════════════════════════════════════
# EXECUTION
# ═══════════════════════════════════════════════════════════════
def main():
    print("\n" + "═" * 50)
    print(f"🔧 BUILD Phase 8: Live Connection Setup (Fix)")
    print("═" * 50)

    try:
        # 1. Write Files
        print("\n[1/3] 📝 Writing Tools...")
        tools_dir = os.path.join(ROOT, "tools")
        if not os.path.exists(tools_dir):
            os.makedirs(tools_dir)
            
        for path, content in NEW_FILES.items():
            full = os.path.join(ROOT, path)
            with open(full, "w", encoding="utf-8") as f:
                f.write(content)
            print(f"      ✅ Wrote: {path}")

        # 2. Run Connection Test
        print("\n[2/3] 🔌 Testing Connection to Exchange...")
        print("      (Make sure your VPN is ON and .env is updated)")
        
        result = subprocess.run([VENV_PYTHON, os.path.join(ROOT, "tools/check_live_connection.py")], cwd=ROOT)
        
        if result.returncode != 0:
            raise Exception("Live Connection Failed. Check API Keys and VPN.")

        # 3. Git Sync
        print("\n[3/3] 🐙 Git Sync...")
        try:
            setup_git.setup()
            setup_git.sync("Phase 8: Live Connection Established")
            print("      ✅ Git Synced")
        except:
            print("      ⚠️ Git Warning (Ignored)")

        print("\n🎉 PHASE 8 COMPLETE: SYSTEM IS ONLINE!")

    except Exception as e:
        print(f"\n💥 Error: {e}")

if __name__ == "__main__":
    main()
