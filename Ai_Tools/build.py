# AI_Tools/build.py — Phase 11: Light Build (No Re-install)
# ═══════════════════════════════════════════════════════════════
# Ref: PHASE-11-LIGHT-BUILD
# ═══════════════════════════════════════════════════════════════

import os
import sys

# ═══════════════════════════════════════════════════════════════
# 1. SETUP PATHS & UTILS (No External Deps)
# ═══════════════════════════════════════════════════════════════

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(SCRIPT_DIR)

def load_env_manual(env_path):
    """Reads .env without needing the 'python-dotenv' library installed on host."""
    env_vars = {}
    if os.path.exists(env_path):
        with open(env_path, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith('#') or '=' not in line:
                    continue
                key, val = line.split('=', 1)
                env_vars[key.strip()] = val.strip().strip("'").strip('"')
    return env_vars

# Load Workflow Modules (If present)
try:
    import context_gen
    import setup_git
except ImportError:
    pass

# ═══════════════════════════════════════════════════════════════
# 2. FILE TEMPLATES (The code to be injected)
# ═══════════════════════════════════════════════════════════════

TELEGRAM_CLIENT_CODE = r'''
import os
import requests
from dotenv import load_dotenv

# Ensure env is loaded
load_dotenv(os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), '.env'))

class TelegramBot:
    def __init__(self):
        self.token = os.getenv("TELEGRAM_BOT_TOKEN")
        self.chat_id = os.getenv("TELEGRAM_CHAT_ID")
        self.base_url = f"https://api.telegram.org/bot{self.token}/sendMessage"

    def send_message(self, message):
        if not self.token or not self.chat_id:
            print(f"🔕 Telegram Auth Missing (Check .env).")
            return False

        payload = {
            "chat_id": self.chat_id,
            "text": message,
            "parse_mode": "HTML"
        }
        
        try:
            # Using verify=False to avoid SSL issues on some local proxies, can be removed in prod
            response = requests.post(self.base_url, json=payload, timeout=10)
            if response.status_code == 200:
                return True
            else:
                print(f"❌ TG Error {response.status_code}: {response.text}")
                return False
        except Exception as e:
            print(f"❌ TG Connection Error: {e}")
            return False
'''

RUN_BOT_CODE = r'''
import os
import time
import sys
from dotenv import load_dotenv

# Setup Paths
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

# Imports
from modules.mexc_provider import MEXCData
from modules.network.telegram_client import TelegramBot

# Load Environment
load_dotenv()

# Configuration
SYMBOL = "BTCUSDT"
TIMEFRAME = "15m"

def calculate_rsi(prices, period=14):
    import numpy as np
    if len(prices) < period + 1: return 50.0
    deltas = np.diff(prices)
    seed = deltas[:period+1]
    up = seed[seed >= 0].sum()/period
    down = -seed[seed < 0].sum()/period
    rs = up/down if down != 0 else 0
    rsi = np.zeros_like(prices)
    rsi[:period] = 100. - 100./(1. + rs)
    for i in range(period, len(prices)):
        delta = deltas[i-1]
        if delta > 0:
            upval = delta
            downval = 0.
        else:
            upval = 0.
            downval = -delta
        up = (up * (period - 1) + upval) / period
        down = (down * (period - 1) + downval) / period
        rs = up/down if down != 0 else 0
        rsi[i] = 100. - 100./(1. + rs)
    return rsi[-1]

def calculate_bollinger_bands(prices, period=20, std_dev=2):
    import numpy as np
    if len(prices) < period: return 0, 0, 0
    sma = np.mean(prices[-period:])
    std = np.std(prices[-period:])
    upper = sma + (std_dev * std)
    lower = sma - (std_dev * std)
    return upper, sma, lower

def run_engine():
    print(f"\n🚀 OCEAN HUNTER ENGINE STARTED")
    print(f"🎯 Target: {SYMBOL} | Strategy: Smart Sniper V10.8.2")
    
    provider = MEXCData()
    bot = TelegramBot()
    
    # Startup Message
    start_msg = f"🌊 <b>OCEAN HUNTER ONLINE</b>\nSymbol: {SYMBOL}\nMode: {os.getenv('MODE', 'UNKNOWN')}"
    print("   📨 Sending startup message to Telegram...")
    if bot.send_message(start_msg):
        print("   ✅ Telegram Connected Successfully.")
    else:
        print("   ⚠️ Telegram Message Failed (Check VPN/Proxy/Keys).")

    cycle_count = 0
    
    while True:
        try:
            cycle_count += 1
            if cycle_count % 10 == 0:
                 print(f"\n[Cycle {cycle_count}] Scanning Markets...")
            
            # Fetch & Analyze
            df = provider.get_klines(SYMBOL, TIMEFRAME, limit=50)
            if df is not None and not df.empty:
                closes = df['close'].values
                current_price = closes[-1]
                rsi = calculate_rsi(closes)
                upper, mid, lower = calculate_bollinger_bands(closes)
                
                score = 0
                reasons = []
                
                # Strategy Logic
                if rsi < 35:
                    score += 35
                    reasons.append(f"RSI Oversold ({rsi:.2f})")
                if current_price < lower:
                    score += 35
                    reasons.append("Price < BB Lower")
                
                # Signal Trigger
                if score >= 70:
                    msg = f"🎯 <b>SIGNAL DETECTED</b>\nPrice: {current_price}\nScore: {score}\nReasons: {', '.join(reasons)}"
                    print(f"   🚨 SIGNAL FOUND! Score: {score}")
                    bot.send_message(msg)
                    time.sleep(60) 
                
                # Status Line
                sys.stdout.write(f"\r   Price: {current_price:.2f} | RSI: {rsi:.2f} | Score: {score}   ")
                sys.stdout.flush()

            time.sleep(5)

        except KeyboardInterrupt:
            bot.send_message("🛑 Bot Stopped by User.")
            break
        except Exception as e:
            print(f"Error: {e}")
            time.sleep(10)

if __name__ == "__main__":
    run_engine()
'''

TESTER_CODE = r'''
import sys
import os
from dotenv import load_dotenv

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from modules.network.telegram_client import TelegramBot

def test():
    print("\n📡 TESTING TELEGRAM CONNECTION...")
    
    env_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), '.env')
    load_dotenv(env_path)
    
    token = os.getenv("TELEGRAM_BOT_TOKEN")
    
    print(f"   Context: .env found at {env_path}")
    print(f"   Token Loaded: {'YES' if token else 'NO'}")
    
    bot = TelegramBot()
    print("   Attempting to send message...")
    result = bot.send_message("📡 <b>Test Packet</b>\nOcean Hunter Connectivity Verified.")
    
    if result:
        print("\n   ✅ SUCCESS: Message sent to Telegram.")
    else:
        print("\n   ❌ FAILED: Check VPN or Token.")
        
    input("\nPress Enter to return...")

if __name__ == "__main__":
    test()
'''

# ═══════════════════════════════════════════════════════════════
# 3. MAIN BUILD LOGIC
# ═══════════════════════════════════════════════════════════════

def main():
    print("="*60)
    print("      OCEAN HUNTER | PHASE 11: TELEGRAM LINKUP (LIGHT)")
    print("="*60)

    # 1. READ ENV MANUALLY (Just to check, no dependency needed)
    env_path = os.path.join(PROJECT_ROOT, ".env")
    env_vars = load_env_manual(env_path)
    token = env_vars.get("TELEGRAM_BOT_TOKEN")
    
    if token:
        print(f"✅ Environment Config Detected.")
    else:
        print("⚠️ Warning: TELEGRAM_BOT_TOKEN not found in .env (Bot may fail).")

    # 2. GENERATE FILES
    print("\n🛠️ [2/3] Generating code files...")
    
    # Telegram Client
    net_dir = os.path.join(PROJECT_ROOT, "modules", "network")
    os.makedirs(net_dir, exist_ok=True)
    with open(os.path.join(net_dir, "telegram_client.py"), "w", encoding="utf-8") as f:
        f.write(TELEGRAM_CLIENT_CODE)
    print("   -> Created modules/network/telegram_client.py")
    
    # Run Bot
    with open(os.path.join(PROJECT_ROOT, "run_bot.py"), "w", encoding="utf-8") as f:
        f.write(RUN_BOT_CODE)
    print("   -> Created run_bot.py")

    # Tester
    with open(os.path.join(PROJECT_ROOT, "test_telegram_conn.py"), "w", encoding="utf-8") as f:
        f.write(TESTER_CODE)
    print("   -> Created test_telegram_conn.py")

    # 3. SYNC
    print("\n🐙 [3/3] Syncing to Git...")
    if 'context_gen' in sys.modules and 'setup_git' in sys.modules:
        try:
            context_gen.create_context_file()
            setup_git.sync("Phase 11: Telegram Integration (Light Build)")
        except Exception as e:
            print(f"   ⚠️ Git Sync Warning: {e}")
    else:
        print("   ⚠️ Workflow modules missing. Skipping Git sync.")

if __name__ == "__main__":
    main()
    print("\n✅ BUILD COMPLETE.")
    print("👉 Now run the Dashboard (Option 3) to test Telegram.")
