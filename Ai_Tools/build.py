# AI_Tools/build.py — Build V7.1 (Analysis Engine)
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
# MODULE: ANALYSIS (m_analysis.py)
# ═══════════════════════════════════════════════════════════════
M_ANALYSIS_CONTENT = '''
def calculate_rsi(prices, period=14):
    """Calculates Relative Strength Index (RSI)"""
    if len(prices) < period + 1:
        return 50  # Not enough data
        
    gains = []
    losses = []
    
    # Calculate price changes
    for i in range(1, len(prices)):
        delta = prices[i] - prices[i-1]
        if delta > 0:
            gains.append(delta)
            losses.append(0)
        else:
            gains.append(0)
            losses.append(abs(delta))
            
    # Calculate initial average
    avg_gain = sum(gains[:period]) / period
    avg_loss = sum(losses[:period]) / period
    
    # Calculate smoothed averages
    for i in range(period, len(prices) - 1):
        avg_gain = (avg_gain * (period - 1) + gains[i]) / period
        avg_loss = (avg_loss * (period - 1) + losses[i]) / period
        
    if avg_loss == 0:
        return 100
        
    rs = avg_gain / avg_loss
    rsi = 100 - (100 / (1 + rs))
    return round(rsi, 2)

def analyze_market(symbol, candles):
    """Analyzes market data and returns a signal"""
    if not candles or len(candles) < 20:
        return {"signal": "WAIT", "rsi": 0, "price": 0}
        
    # Extract closing prices
    closes = [float(c['close']) for c in candles]
    current_price = closes[-1]
    
    # Calculate RSI
    rsi = calculate_rsi(closes)
    
    # Logic Strategy
    signal = "NEUTRAL ⚪"
    if rsi < 30:
        signal = "BUY 🟢 (Oversold)"
    elif rsi > 70:
        signal = "SELL 🔴 (Overbought)"
        
    return {
        "symbol": symbol,
        "price": current_price,
        "rsi": rsi,
        "signal": signal
    }
'''

# ═══════════════════════════════════════════════════════════════
# MAIN APP UPDATE (main.py)
# ═══════════════════════════════════════════════════════════════
MAIN_CONTENT = '''import os
import time
import requests
import urllib3
from dotenv import load_dotenv
from modules.m_data import DataEngine
from modules.m_analysis import analyze_market

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
    print("🧠 OCEAN HUNTER V7.1 — ANALYSIS ENGINE")
    print("-" * 50)
    
    engine = DataEngine()
    targets = ["BTCUSDT", "ETHUSDT", "SOLUSDT", "BNBUSDT", "XRPUSDT"]
    
    report_msg = "🧠 OCEAN HUNTER ANALYSIS (V7.1)\\n"
    report_msg += "Strategy: RSI (14) - 1 Hour Timeframe\\n"
    report_msg += "─" * 20 + "\\n\\n"
    
    for symbol in targets:
        # 1. Fetch Data (Need at least 30 candles for accurate RSI)
        candles = engine.fetch_candles(symbol, interval="60m", limit=50)
        
        if candles:
            # 2. Save Data
            engine.save_to_csv(symbol, candles)
            
            # 3. Analyze Data
            result = analyze_market(symbol, candles)
            
            # 4. Format Output
            price_str = f"${result['price']}"
            if result['price'] < 10: price_str = f"${result['price']:.4f}"
                
            line = f"🔹 {symbol.replace('USDT','')}: {price_str}\\n"
            line += f"   RSI: {result['rsi']} → {result['signal']}\\n"
            report_msg += line + "\\n"
            
            print(f"   ✅ {symbol}: RSI={result['rsi']} ({result['signal']})")
        else:
            report_msg += f"❌ {symbol}: Connection Failed\\n"
            
    print(f"\\n[3] 📨 Sending Analysis Report...")
    send_telegram(report_msg)
    print("✅ Done.")

if __name__ == "__main__":
    main()
'''

# ═══════════════════════════════════════════════════════════════
# BUILD STEPS
# ═══════════════════════════════════════════════════════════════
def main():
    print("\n🚀 BUILD V7.1 — ANALYSIS ENGINE")
    
    # 1. Create Analysis Module
    modules_dir = os.path.join(ROOT, "modules")
    with open(os.path.join(modules_dir, "m_analysis.py"), "w", encoding="utf-8") as f:
        f.write(M_ANALYSIS_CONTENT)
    print(f"   📝 Created modules/m_analysis.py")
    
    # 2. Update Main
    with open(os.path.join(ROOT, "main.py"), "w", encoding="utf-8") as f:
        f.write(MAIN_CONTENT)
    print(f"   📝 Updated main.py")

    # 3. Git Sync
    try:
        setup_git.setup()
        setup_git.sync("Build V7.1: Added RSI Analysis")
    except: pass

    # 4. Run
    print("\n" + "="*50)
    print("   RUNNING V7.1 ANALYSIS...")
    print("="*50)
    subprocess.run([VENV_PYTHON, "main.py"], cwd=ROOT)

if __name__ == "__main__":
    main()
