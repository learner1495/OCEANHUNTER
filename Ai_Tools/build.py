# AI_Tools/build.py — Phase 9: Dashboard & Live Loop
# ═══════════════════════════════════════════════════════════════
# Ref: OCEAN-HUNTER-PHASE9-DASHBOARD
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

# ═══════════════════════════════════════════════════════════════
# 1. MEXC PROVIDER (Interface)
# ═══════════════════════════════════════════════════════════════
MEXC_PROVIDER_CODE = """
import os
import time
import hmac
import hashlib
import requests
import pandas as pd
from datetime import datetime
from dotenv import load_dotenv

class MEXCProvider:
    def __init__(self):
        load_dotenv()
        self.api_key = os.getenv("MEXC_API_KEY")
        self.secret_key = os.getenv("MEXC_SECRET_KEY")
        self.base_url = "https://api.mexc.com"
        
    def _get_signature(self, params):
        query_string = "&".join([f"{k}={v}" for k, v in sorted(params.items())])
        return hmac.new(self.secret_key.encode('utf-8'), query_string.encode('utf-8'), hashlib.sha256).hexdigest()

    def _request(self, method, endpoint, params=None, signed=False):
        url = f"{self.base_url}{endpoint}"
        params = params or {}
        
        headers = {"Content-Type": "application/json"}
        if signed:
            if not self.api_key or not self.secret_key:
                return None
            params["timestamp"] = int(time.time() * 1000)
            params["signature"] = self._get_signature(params)
            headers["X-MEXC-APIKEY"] = self.api_key

        try:
            if method == "GET":
                resp = requests.get(url, headers=headers, params=params, timeout=10)
            elif method == "POST":
                resp = requests.post(url, headers=headers, params=params, timeout=10)
                
            if resp.status_code == 200:
                return resp.json()
            return None
        except:
            return None

    def fetch_ohlcv(self, symbol="SOLUSDT", interval="1m", limit=100):
        endpoint = "/api/v3/klines"
        params = {"symbol": symbol, "interval": interval, "limit": limit}
        data = self._request("GET", endpoint, params=params, signed=False)
        
        if not data: return pd.DataFrame()

        df = pd.DataFrame(data, columns=[
            "timestamp", "open", "high", "low", "close", "volume", 
            "close_time", "q_vol", "trades", "taker_b_vol", "taker_q_vol", "ignore"
        ])
        df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
        numeric_cols = ['open', 'high', 'low', 'close', 'volume']
        df[numeric_cols] = df[numeric_cols].apply(pd.to_numeric, axis=1)
        return df[['timestamp', 'open', 'high', 'low', 'close', 'volume']]

    def get_balance(self, asset="USDT"):
        data = self._request("GET", "/api/v3/account", signed=True)
        if data and 'balances' in data:
            for b in data['balances']:
                if b['asset'] == asset:
                    return float(b['free'])
        return 0.0
"""

# ═══════════════════════════════════════════════════════════════
# 2. RUN BOT (The Engine)
# ═══════════════════════════════════════════════════════════════
RUN_BOT_CODE = """
import os
import sys
import time
from dotenv import load_dotenv

# Add Root to path
sys.path.append(os.getcwd())

from data.mexc_provider import MEXCProvider
from strategy.smart_sniper import SmartSniperStrategy
from models.virtual_wallet import VirtualWallet

# Load Env
load_dotenv()
MODE = os.getenv("MODE", "PAPER").upper()
SYMBOL = "SOLUSDT"

# Telegram Setup
TG_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
TG_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

def send_telegram(msg):
    if not TG_TOKEN or not TG_CHAT_ID: return
    try:
        import requests
        url = f"https://api.telegram.org/bot{TG_TOKEN}/sendMessage"
        payload = {"chat_id": TG_CHAT_ID, "text": msg, "parse_mode": "HTML"}
        requests.post(url, json=payload, timeout=5)
    except: pass

def main():
    print(f"🚀 ENGINE STARTED | Mode: {MODE}")
    send_telegram(f"▶️ <b>Ocean Hunter Engine Started</b> ({MODE})")
    
    provider = MEXCProvider()
    strategy = SmartSniperStrategy()
    
    while True:
        try:
            # Simple heartbeat loop for now
            df = provider.fetch_ohlcv(symbol=SYMBOL, limit=50)
            if not df.empty:
                current_price = df.iloc[-1]['close']
                rsi = strategy.indicators.get('rsi', pd.Series([0])).iloc[-1]
                
                # Logic placeholder
                print(f"   Tick: {current_price} | RSI: {rsi:.2f}")
                
            time.sleep(10) # Fast loop
            
        except KeyboardInterrupt:
            break
        except Exception as e:
            print(f"Error: {e}")
            time.sleep(5)

if __name__ == "__main__":
    main()
"""

# ═══════════════════════════════════════════════════════════════
# 3. DASHBOARD (The UI)
# ═══════════════════════════════════════════════════════════════
DASHBOARD_CODE = """
import os
import sys
import time
import subprocess
import signal
from dotenv import load_dotenv, set_key

# Add Root to path
sys.path.append(os.getcwd())
from data.mexc_provider import MEXCProvider

# Global Bot Process
bot_process = None

def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')

def load_config():
    load_dotenv(override=True)
    return {
        "MODE": os.getenv("MODE", "PAPER"),
        "MEXC_KEY": os.getenv("MEXC_API_KEY", ""),
        "TG_ID": os.getenv("TELEGRAM_CHAT_ID", "")
    }

def update_env_variable(key, value):
    env_path = os.path.join(os.getcwd(), ".env")
    set_key(env_path, key, value)
    load_dotenv(override=True)
    print(f"✅ Updated {key} successfully.")
    time.sleep(1)

def show_header(config):
    clear_screen()
    print("🌊 OCEAN HUNTER COMMANDER v1.0")
    print("═" * 40)
    print(f"📡 MODE:      {config['MODE']}")
    print(f"🤖 BOT STATE: {'🟢 RUNNING' if bot_process else '🔴 STOPPED'}")
    print("═" * 40)

def menu_wallets():
    print("\\n💰 WALLET CHECKER")
    print("Fetching data from MEXC...")
    try:
        p = MEXCProvider()
        usdt = p.get_balance("USDT")
        sol = p.get_balance("SOL")
        print(f"   USDT: {usdt}")
        print(f"   SOL:  {sol}")
    except Exception as e:
        print(f"   Error: {e}")
    input("\\nPress Enter to return...")

def menu_settings():
    while True:
        clear_screen()
        print("⚙️ SETTINGS EDITOR")
        print("1. Change MODE (PAPER/LIVE)")
        print("2. Update MEXC API Key")
        print("3. Update MEXC Secret Key")
        print("4. Back")
        
        ch = input("\\nSelect: ")
        if ch == '1':
            new_mode = input("Enter Mode (PAPER/LIVE): ").upper()
            if new_mode in ['PAPER', 'LIVE']:
                update_env_variable("MODE", new_mode)
        elif ch == '2':
            new_key = input("Enter New API Key: ")
            update_env_variable("MEXC_API_KEY", new_key)
        elif ch == '3':
            new_sec = input("Enter New Secret Key: ")
            update_env_variable("MEXC_SECRET_KEY", new_sec)
        elif ch == '4':
            break

def toggle_bot():
    global bot_process
    if bot_process:
        # Stop
        if sys.platform == "win32":
            bot_process.terminate()
        else:
            os.kill(bot_process.pid, signal.SIGTERM)
        bot_process = None
        print("🛑 Bot Stopped.")
    else:
        # Start
        cmd = [sys.executable, "run_bot.py"]
        # Use Popen to run in background (new console window on Windows is better)
        if sys.platform == "win32":
            bot_process = subprocess.Popen(cmd, creationflags=subprocess.CREATE_NEW_CONSOLE)
        else:
            bot_process = subprocess.Popen(cmd)
        print("✅ Bot Started in background.")
    time.sleep(2)

def main():
    while True:
        cfg = load_config()
        show_header(cfg)
        
        print("1. 🟢 Start / 🔴 Stop Bot")
        print("2. 💰 Check Wallet Balance")
        print("3. ⚙️ Settings (Keys, Mode)")
        print("4. ❌ Exit Dashboard")
        
        choice = input("\\nSelect Option [1-4]: ")
        
        if choice == '1':
            toggle_bot()
        elif choice == '2':
            menu_wallets()
        elif choice == '3':
            menu_settings()
        elif choice == '4':
            if bot_process:
                print("⚠️ Warning: Bot is still running. Stop it first? (y/n)")
                if input().lower() == 'y':
                    toggle_bot()
            print("Bye!")
            sys.exit()

if __name__ == "__main__":
    main()
"""

# ═══════════════════════════════════════════════════════════════
# CONFIGURATION
# ═══════════════════════════════════════════════════════════════
NEW_FILES = {
    "data/mexc_provider.py": MEXC_PROVIDER_CODE,
    "run_bot.py": RUN_BOT_CODE,
    "dashboard.py": DASHBOARD_CODE
}

# ═══════════════════════════════════════════════════════════════
# EXECUTION
# ═══════════════════════════════════════════════════════════════
def main():
    print("\n" + "═" * 50)
    print(f"🔧 BUILD Phase 9: Commander Dashboard")
    print("═" * 50)

    try:
        # 1. Write Files
        print("\n[1/3] 📝 Writing Files...")
        
        # Ensure data dir exists
        data_dir = os.path.join(ROOT, "data")
        if not os.path.exists(data_dir):
            os.makedirs(data_dir)

        for path, content in NEW_FILES.items():
            full = os.path.join(ROOT, path)
            with open(full, "w", encoding="utf-8") as f:
                f.write(content)
            print(f"      ✅ Wrote: {path}")

        # 2. Git Sync
        print("\n[2/3] 🐙 Git Sync...")
        try:
            setup_git.setup()
            setup_git.sync("Phase 9: Added Dashboard UI")
            print("      ✅ Git Synced")
        except:
            print("      ⚠️ Git Warning (Ignored)")
            
        print("\n[3/3] 🏁 READY TO LAUNCH")
        print("      Run the dashboard with:")
        print("      python dashboard.py")

        print("\n🎉 PHASE 9 COMPLETE!")

    except Exception as e:
        print(f"\n💥 Error: {e}")

if __name__ == "__main__":
    main()
