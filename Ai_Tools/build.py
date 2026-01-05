# AI_Tools/build.py — Phase 16: Smart Sniper Logic (Full Scoring)
# ═══════════════════════════════════════════════════════════════
# Ref: PHASE-16-SMART-SCORE
# ═══════════════════════════════════════════════════════════════

import os
import sys
import subprocess
import time

# ═══════════════════════════════════════════════════════════════
# 1. SETUP PATHS
# ═══════════════════════════════════════════════════════════════
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(SCRIPT_DIR)
sys.path.append(SCRIPT_DIR)

try:
    import context_gen
    import setup_git
except ImportError:
    pass

VENV_PYTHON = os.path.join(PROJECT_ROOT, ".venv", "Scripts", "python.exe")

# ═══════════════════════════════════════════════════════════════
# 2. THE SMART SNIPER LOGIC (run_bot.py)
# ═══════════════════════════════════════════════════════════════

BOT_CONTENT = r'''
import os
import time
import requests
import statistics
import math
from datetime import datetime
from dotenv import load_dotenv

# Load Environment
load_dotenv()
MODE = os.getenv("MODE", "SAFE")

# ════════════════ STRATEGY CONFIG ════════════════
SYMBOL = "BTCUSDT"
TIMEFRAME = "1m"       # Use 1m for testing speed (In real production: 15m)
BB_PERIOD = 20
BB_STD_DEV = 2.0
RSI_PERIOD = 14
VOLUME_MA = 20
ENTRY_THRESHOLD = 70   # Min Score to trigger SIGNAL

# API CONFIG
TG_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
TG_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")
PROXY_URL = os.getenv("HTTPS_PROXY", "http://127.0.0.1:10809")
PROXIES = {"http": PROXY_URL, "https": PROXY_URL}

# ════════════════ TELEGRAM ════════════════
def send_telegram(msg):
    if not TG_TOKEN or not TG_CHAT_ID: return
    url = f"https://api.telegram.org/bot{TG_TOKEN}/sendMessage"
    payload = {"chat_id": TG_CHAT_ID, "text": msg, "parse_mode": "HTML"}
    try:
        requests.post(url, json=payload, timeout=5) # Try Direct
    except:
        try:
            requests.post(url, json=payload, proxies=PROXIES, timeout=5) # Try Proxy
        except: pass

# ════════════════ MARKET DATA ════════════════
def get_market_data():
    # Fetch enough candles for BB(20) and RSI(14)
    base_url = "https://api.mexc.com/api/v3/klines"
    params = {"symbol": SYMBOL, "interval": TIMEFRAME, "limit": 50}
    try:
        resp = requests.get(base_url, params=params, timeout=5)
        return resp.json()
    except:
        try:
            resp = requests.get(base_url, params=params, proxies=PROXIES, timeout=5)
            return resp.json()
        except: return None

def get_current_price():
    try:
        url = "https://api.mexc.com/api/v3/ticker/price"
        resp = requests.get(url, params={"symbol": SYMBOL}, proxies=PROXIES, timeout=3)
        return float(resp.json()['price'])
    except: return 0.0

# ════════════════ TECHNICAL INDICATORS ════════════════
def calculate_rsi(prices, period=14):
    if len(prices) < period + 1: return 50
    deltas = [prices[i] - prices[i-1] for i in range(1, len(prices))]
    gains = [d if d > 0 else 0 for d in deltas]
    losses = [abs(d) if d < 0 else 0 for d in deltas]
    
    avg_gain = sum(gains[-period:]) / period
    avg_loss = sum(losses[-period:]) / period
    
    if avg_loss == 0: return 100
    rs = avg_gain / avg_loss
    return 100 - (100 / (1 + rs))

def calculate_bb(prices, period=20, std_dev=2.0):
    if len(prices) < period: return 0, 0, 0
    slice_data = prices[-period:]
    sma = sum(slice_data) / period
    std = statistics.stdev(slice_data)
    upper = sma + (std * std_dev)
    lower = sma - (std * std_dev)
    return upper, sma, lower

def calculate_volume_spike(volumes, period=20):
    if len(volumes) < period: return False
    current_vol = volumes[-1]
    avg_vol = sum(volumes[-period-1:-1]) / period  # Exclude current
    if avg_vol == 0: return False
    return current_vol > (1.5 * avg_vol)

# ════════════════ SCORING ENGINE (The Brain) ════════════════
def analyze_market(klines):
    if not klines: return None
    
    # Extract Data
    closes = [float(k[4]) for k in klines]
    volumes = [float(k[5]) for k in klines]
    opens = [float(k[1]) for k in klines]
    
    current_price = closes[-1]
    
    # 1. Calculate Indicators
    rsi = calculate_rsi(closes, RSI_PERIOD)
    bb_upper, bb_mid, bb_lower = calculate_bb(closes, BB_PERIOD, BB_STD_DEV)
    vol_spike = calculate_volume_spike(volumes, VOLUME_MA)
    is_green = closes[-1] > opens[-1]
    
    # 2. Calculate Score (Based on ARCHITECTURE.txt [2.2])
    score = 0
    reasons = []
    
    # Rule A: Technical (RSI < 35 AND Price < BB_Lower) -> 35 pts
    # Modified slightly for testing: RSI < 40 or Price < Lower
    if rsi < 40:
        score += 20
        reasons.append("RSI Oversold")
    if current_price < bb_lower:
        score += 15
        reasons.append("Below BB Lower")
        
    # Rule B: Volume Spike -> 25 pts
    if vol_spike:
        score += 25
        reasons.append("Volume Spike")
        
    # Rule C: Momentum (Green Candle) -> 25 pts
    if is_green:
        score += 25
        reasons.append("Momentum Bullish")
        
    return {
        "price": current_price,
        "rsi": round(rsi, 2),
        "bb_lower": round(bb_lower, 2),
        "score": score,
        "reasons": reasons
    }

# ════════════════ MAIN LOOP ════════════════
def main():
    os.system('cls' if os.name == 'nt' else 'clear')
    print("╔════════════════════════════════════════════════════╗")
    print(f"║ 🧠 SMART SNIPER ENGINE: {MODE} MODE              ║")
    print(f"║ 🎯 Symbol: {SYMBOL:<10} TF: {TIMEFRAME:<5} Threshold: {ENTRY_THRESHOLD} ║")
    print("╚════════════════════════════════════════════════════╝")
    
    send_telegram(f"🧠 <b>SMART SNIPER STARTED</b>\nSymbol: {SYMBOL}")
    print("\n⏳ Initializing Indicators (20 candles)...")
    
    last_score = 0
    
    try:
        while True:
            data = get_market_data()
            if data:
                analysis = analyze_market(data)
                
                # Colors
                timestamp = datetime.now().strftime("%H:%M:%S")
                score = analysis['score']
                rsi = analysis['rsi']
                price = analysis['price']
                
                # Dynamic Color for Score
                s_color = "\033[92m" if score >= ENTRY_THRESHOLD else "\033[93m" if score >= 50 else "\033[90m"
                r_color = "\033[91m" if rsi > 70 else "\033[92m" if rsi < 30 else "\033[97m"
                
                print(f"[{timestamp}] 💵 {price} | RSI: {r_color}{rsi:<5}\033[0m | Score: {s_color}{score}/100\033[0m")
                
                if analysis['reasons']:
                    print(f"            └─ Detected: {', '.join(analysis['reasons'])}")

                # TRIGGER LOGIC
                if score >= ENTRY_THRESHOLD and last_score < ENTRY_THRESHOLD:
                    msg = (f"🚀 <b>ENTRY SIGNAL DETECTED</b>\n"
                           f"Symbol: {SYMBOL}\n"
                           f"Score: {score}/100\n"
                           f"Price: {price}\n"
                           f"Reasons: {', '.join(analysis['reasons'])}")
                    print(f"\n✅ SENDING ALERT: Score {score}\n")
                    send_telegram(msg)
                
                last_score = score

            else:
                print("⚠️  Network/Proxy glitch... retrying", end='\r')
                
            time.sleep(10) # Update every 10s

    except KeyboardInterrupt:
        print("\n🛑 Bot Stopped.")

if __name__ == "__main__":
    main()
'''

# ═══════════════════════════════════════════════════════════════
# 3. BUILD PROCESS
# ═══════════════════════════════════════════════════════════════

def main():
    print(f"\n[1/3] 🧠 Upgrading to Smart Sniper V2 (Full Scoring)...")
    
    bot_path = os.path.join(PROJECT_ROOT, "run_bot.py")
    with open(bot_path, "w", encoding="utf-8") as f:
        f.write(BOT_CONTENT)
    
    print("      ✅ Logic upgraded.")

    print("\n[2/3] 📚 Git Sync...")
    if 'context_gen' in sys.modules:
        context_gen.create_context_file()
    if 'setup_git' in sys.modules:
        setup_git.sync("Phase 16: Smart Scoring Engine")
    print("      ✅ Synced")

    print("\n[3/3] 🏁 Launching V2...")
    time.sleep(2)
    if sys.platform == "win32":
        bat_path = os.path.join(PROJECT_ROOT, "run_dashboard.bat")
        os.system(f'start "" "{bat_path}"')
    else:
        subprocess.run([VENV_PYTHON, "run_dashboard.py"], cwd=PROJECT_ROOT)

if __name__ == "__main__":
    main()
