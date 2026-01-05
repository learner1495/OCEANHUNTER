# AI_Tools/build.py — Phase 9 Fix: Auto-Launch & Telegram Test
# ═══════════════════════════════════════════════════════════════
# Ref: OCEAN-HUNTER-PHASE9-FIX-LAUNCHER
# ═══════════════════════════════════════════════════════════════

import os
import sys
import subprocess
import time

# ═══ Import Internal Modules ═══
try:
    import context_gen
    import setup_git
except ImportError:
    pass 

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(SCRIPT_DIR)

# ═══════════════════════════════════════════════════════════════
# 1. MEXC PROVIDER (No Change)
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
import requests
import pandas as pd
from dotenv import load_dotenv

# Add Root to path
sys.path.append(os.getcwd())

from data.mexc_provider import MEXCProvider
from strategy.smart_sniper import SmartSniperStrategy

# Load Env
load_dotenv()
MODE = os.getenv("MODE", "PAPER").upper()
SYMBOL = "SOLUSDT"
TG_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
TG_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

def send_telegram(msg):
    if not TG_TOKEN or not TG_CHAT_ID: 
        print("⚠️ Telegram keys missing in .env")
        return
    try:
        url = f"https://api.telegram.org/bot{TG_TOKEN}/sendMessage"
        payload = {"chat_id": TG_CHAT_ID, "text": msg, "parse_mode": "HTML"}
        requests.post(url, json=payload, timeout=5)
    except Exception as e:
        print(f"Telegram Error: {e}")

def main():
    print(f"🚀 ENGINE STARTED | Mode: {MODE}")
    send_telegram(f"▶️ <b>Ocean Hunter Engine Started</b>\\nMode: {MODE}\\nSymbol: {SYMBOL}")
    
    provider = MEXCProvider()
    strategy = SmartSniperStrategy()
    
    print(f"   Monitoring {SYMBOL}...")
    
    while True:
        try:
            # Simple heartbeat loop for now
            df = provider.fetch_ohlcv(symbol=SYMBOL, limit=50)
            if not df.empty:
                current_price = df.iloc[-1]['close']
                print(f"   [{time.strftime('%H:%M:%S')}] Price: {current_price} USDT")
                
                # Here we would feed data to strategy...
                
            time.sleep(10) # 10s Loop
            
        except KeyboardInterrupt:
            print("\\n🛑 Stopping Engine...")
            send_telegram("🛑 <b>Ocean Hunter Engine Stopped</b>")
            break
        except Exception as e:
            print(f"Error: {e}")
            time.sleep(5)

if __name__ == "__main__":
    main()
"""

# ═══════════════════════════════════════════════════════════════
# 3. DASHBOARD (Updated UI)
# ═══════════════════════════════════════════════════════════════
DASHBOARD_CODE = """
import os
import sys
import time
import subprocess
import signal
import requests
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
        "TG_TOKEN": os.getenv("TELEGRAM_BOT_TOKEN", ""),
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
    print("🌊 OCEAN HUNTER COMMANDER v1.1")
    print("═" * 40)
    print(f"📡 MODE:      {config['MODE']}")
    print(f"🤖 BOT STATE: {'🟢 RUNNING' if bot_process else '🔴 STOPPED'}")
    print("═" * 40)

def test_telegram():
    cfg = load_config()
    print("\\n📨 TELEGRAM TEST")
    if not cfg['TG_TOKEN'] or not cfg['TG_ID']:
        print("❌ Token or Chat ID is missing in .env")
    else:
        print("   Sending test message...")
        try:
            url = f"https://api.telegram.org/bot{cfg['TG_TOKEN']}/sendMessage"
            payload = {"chat_id": cfg['TG_ID'], "text": "✅ <b>Test Message from Dashboard</b>", "parse_mode": "HTML"}
            resp = requests.post(url, json=payload, timeout=5)
            if resp.status_code == 200:
                print("   ✅ Success! Check your Telegram.")
            else:
                print(f"   ❌ Failed. Status: {resp.status_code}")
                print(f"   Response: {resp.text}")
        except Exception as e:
            print(f"   ❌ Error: {e}")
    input("\\nPress Enter to return...")

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
        print("2. Update TELEGRAM Keys")
        print("3. Back")
        
        ch = input("\\nSelect: ")
        if ch == '1':
            new_mode = input("Enter Mode (PAPER/LIVE): ").upper()
            if new_mode in ['PAPER', 'LIVE']:
                update_env_variable("MODE", new_mode)
        elif ch == '2':
            token = input("Enter Bot Token: ")
            chat_id = input("Enter Chat ID: ")
            update_env_variable("TELEGRAM_BOT_TOKEN", token)
            update_env_variable("TELEGRAM_CHAT_ID", chat_id)
        elif ch == '3':
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
        print("🚀 Starting Engine...")
        cmd = [sys.executable, "run_bot.py"]
        if sys.platform == "win32":
            # Opens in a NEW separate window so you can see logs while keeping dashboard open
            bot_process = subprocess.Popen(cmd, creationflags=subprocess.CREATE_NEW_CONSOLE)
        else:
            bot_process = subprocess.Popen(cmd)
        print("✅ Bot Started in new window.")
    time.sleep(2)

def main():
    while True:
        cfg = load_config()
        show_header(cfg)
        
        print("1. 🟢 Start / 🔴 Stop Bot")
        print("2. 💰 Check Wallet Balance")
        print("3. 📨 Test Telegram Connection")
        print("4. ⚙️ Settings (Keys, Mode)")
        print("5. ❌ Exit Dashboard")
        
        choice = input("\\nSelect Option [1-5]: ")
        
        if choice == '1':
            toggle_bot()
        elif choice == '2':
            menu_wallets()
        elif choice == '3':
            test_telegram()
        elif choice == '4':
            menu_settings()
        elif choice == '5':
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
    print(f"🔧 BUILD Phase 9 Fix: Auto-Launcher")
    print("═" * 50)

    try:
        # 1. Write Files
        print("\n[1/3] 📝 Writing Files...")
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
            setup_git.sync("Phase 9 Fix: Dashboard Auto-Launch")
            print("      ✅ Git Synced")
        except:
            print("      ⚠️ Git Warning (Ignored)")
            
        print("\n[3/3] 🚀 LAUNCHING DASHBOARD...")
        print("      ⚠️ Look for a NEW window opening now!")
        
        time.sleep(2)
        
        # AUTO LAUNCH LOGIC
        dash_path = os.path.join(ROOT, "dashboard.py")
        if sys.platform == "win32":
            subprocess.Popen(f'start cmd /k "{sys.executable}" "{dash_path}"', shell=True)
        else:
            # Linux/Mac fallback
            print(f"      👉 Please run: python {dash_path}")

        print("\n🎉 DONE! You can close this build window.")

    except Exception as e:
        print(f"\n💥 Error: {e}")

if __name__ == "__main__":
    main()
