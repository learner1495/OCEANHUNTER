# AI_Tools/build.py — Build V7.0 (Data Engine Initialization)
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
# MODULE: DATA ENGINE (m_data.py)
# ═══════════════════════════════════════════════════════════════
M_DATA_CONTENT = '''import requests
import os
import csv
import time
from datetime import datetime

# --- CONFIG ---
MEXC_BASE = "https://api.mexc.com"
PROXY_URL = "http://127.0.0.1:10809"
PROXIES = {"http": PROXY_URL, "https": PROXY_URL}

class DataEngine:
    def __init__(self, data_dir="data"):
        self.data_dir = data_dir
        if not os.path.exists(self.data_dir):
            os.makedirs(self.data_dir)
            
    def fetch_candles(self, symbol, interval="60m", limit=50):
        """
        Fetch OHLCV Data from MEXC
        Intervals: 1m, 5m, 15m, 30m, 60m, 4h, 1d, 1M
        """
        endpoint = "/api/v3/klines"
        params = {
            "symbol": symbol,
            "interval": interval,
            "limit": limit
        }
        
        try:
            print(f"   ⬇️ Fetching {symbol} ({interval})...")
            resp = requests.get(
                f"{MEXC_BASE}{endpoint}", 
                params=params, 
                proxies=PROXIES, 
                verify=False, 
                timeout=10
            )
            
            if resp.status_code == 200:
                data = resp.json()
                # MEXC Format: [Open Time, Open, High, Low, Close, Volume, Close Time, ...]
                processed_data = []
                for candle in data:
                    processed_data.append({
                        "timestamp": candle[0],
                        "datetime": datetime.fromtimestamp(candle[0]/1000).strftime('%Y-%m-%d %H:%M:%S'),
                        "open": candle[1],
                        "high": candle[2],
                        "low": candle[3],
                        "close": candle[4],
                        "volume": candle[5]
                    })
                return processed_data
            else:
                print(f"   ❌ API Error: {resp.status_code} - {resp.text}")
                return []
                
        except Exception as e:
            print(f"   ❌ Connection Error: {e}")
            return []

    def save_to_csv(self, symbol, data):
        if not data:
            return False
            
        filename = os.path.join(self.data_dir, f"{symbol}_history.csv")
        keys = data[0].keys()
        
        try:
            with open(filename, 'w', newline='', encoding='utf-8') as f:
                writer = csv.DictWriter(f, fieldnames=keys)
                writer.writeheader()
                writer.writerows(data)
            print(f"   💾 Saved to {filename} ({len(data)} rows)")
            return True
        except Exception as e:
            print(f"   ❌ Save Error: {e}")
            return False
'''

# ═══════════════════════════════════════════════════════════════
# MAIN APP (main.py)
# ═══════════════════════════════════════════════════════════════
MAIN_CONTENT = '''import os
import time
import requests
import urllib3
from dotenv import load_dotenv
from modules.m_data import DataEngine

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
load_dotenv()

# --- CONFIG ---
TG_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
TG_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")
PROXY_URL = "http://127.0.0.1:10809"
PROXIES = {"http": PROXY_URL, "https": PROXY_URL}

def send_telegram(msg):
    if not TG_TOKEN or not TG_CHAT_ID: return
    url = f"https://api.telegram.org/bot{TG_TOKEN}/sendMessage"
    payload = {"chat_id": TG_CHAT_ID, "text": msg}
    try:
        requests.post(url, json=payload, proxies=PROXIES, verify=False, timeout=5)
    except: pass

def main():
    print("-" * 50)
    print("🚀 OCEAN HUNTER V7.0 — DATA ENGINE")
    print("-" * 50)
    
    engine = DataEngine()
    
    # Symbols to track (Defined in Architecture)
    targets = ["BTCUSDT", "ETHUSDT", "SOLUSDT", "BNBUSDT", "XRPUSDT"]
    
    report_msg = "📊 OCEAN HUNTER DATA REPORT (V7.0)\\n\\n"
    success_count = 0
    
    for symbol in targets:
        # Fetch last 24 candles (1 Hour timeframe)
        candles = engine.fetch_candles(symbol, interval="60m", limit=24)
        
        if candles:
            saved = engine.save_to_csv(symbol, candles)
            if saved:
                last_price = candles[-1]['close']
                report_msg += f"✅ {symbol}: ${last_price}\\n"
                success_count += 1
            else:
                report_msg += f"⚠️ {symbol}: Save Failed\\n"
        else:
            report_msg += f"❌ {symbol}: Fetch Failed\\n"
            
    # Final Report
    if success_count == len(targets):
        report_msg += "\\n✅ All Systems Operational.\\nReady for Analysis."
    else:
        report_msg += "\\n⚠️ Some data streams failed."
        
    print(f"\\n[3] 📨 Sending Report...")
    send_telegram(report_msg)
    print("✅ Done.")

if __name__ == "__main__":
    main()
'''

# ═══════════════════════════════════════════════════════════════
# BUILD STEPS
# ═══════════════════════════════════════════════════════════════
def main():
    print("\n🚀 BUILD V7.0 — DATA ENGINE INITIALIZATION")
    
    # 1. Create Data Module
    modules_dir = os.path.join(ROOT, "modules")
    if not os.path.exists(modules_dir): os.makedirs(modules_dir)
    
    with open(os.path.join(modules_dir, "m_data.py"), "w", encoding="utf-8") as f:
        f.write(M_DATA_CONTENT)
    print(f"   📝 Created modules/m_data.py")
    
    # 2. Update Main
    with open(os.path.join(ROOT, "main.py"), "w", encoding="utf-8") as f:
        f.write(MAIN_CONTENT)
    print(f"   📝 Updated main.py")

    # 3. Create Data Folder (Empty)
    data_dir = os.path.join(ROOT, "data")
    if not os.path.exists(data_dir):
        os.makedirs(data_dir)
        print(f"   📁 Created data/ directory")

    # 4. Git Sync
    try:
        setup_git.setup()
        setup_git.sync("Build V7.0: Data Engine + CSV Storage")
    except: pass

    # 5. Run
    print("\n" + "="*50)
    print("   RUNNING V7.0 DATA TEST...")
    print("="*50)
    subprocess.run([VENV_PYTHON, "main.py"], cwd=ROOT)

if __name__ == "__main__":
    main()
