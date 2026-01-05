
import os
import time
import requests
import hmac
import hashlib
import json
from datetime import datetime
from dotenv import load_dotenv

# Load Environment
load_dotenv()
MODE = os.getenv("MODE", "SAFE")  # SAFE or LIVE

# ════════════════ CONFIGURATION ════════════════
SYMBOL = "BTCUSDT"
TIMEFRAME = "1m"  # For testing
RSI_PERIOD = 14
RSI_OVERBOUGHT = 70
RSI_OVERSOLD = 30
CHECK_INTERVAL = 10  # Seconds

# API KEYS
MEXC_KEY = os.getenv("MEXC_API_KEY")
MEXC_SECRET = os.getenv("MEXC_SECRET_KEY")
TG_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
TG_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

# PROXY (Optional - uses what worked in test)
PROXY_URL = os.getenv("HTTPS_PROXY", "http://127.0.0.1:10809")
PROXIES = {
    "http": PROXY_URL,
    "https": PROXY_URL
}
# Try direct first if proxy fails or not needed (based on user test)
USE_PROXY = True 

# ════════════════ TELEGRAM MODULE ════════════════
def send_telegram(msg):
    if not TG_TOKEN or not TG_CHAT_ID:
        print("   ❌ Telegram details missing in .env")
        return
    
    url = f"https://api.telegram.org/bot{TG_TOKEN}/sendMessage"
    payload = {"chat_id": TG_CHAT_ID, "text": msg}
    
    # Try Direct First (Since user confirmed it works)
    try:
        requests.post(url, json=payload, timeout=5)
        return
    except:
        # Fallback to Proxy
        try:
            requests.post(url, json=payload, proxies=PROXIES, timeout=5)
        except Exception as e:
            print(f"   ⚠️ Telegram Fail: {e}")

# ════════════════ MEXC MODULE ════════════════
def get_market_data():
    """Fetch candles for RSI calculation"""
    base_url = "https://api.mexc.com/api/v3/klines"
    params = {
        "symbol": SYMBOL,
        "interval": TIMEFRAME,
        "limit": RSI_PERIOD + 5
    }
    try:
        # Try direct
        resp = requests.get(base_url, params=params, timeout=5)
        return resp.json()
    except:
        try:
            # Try Proxy
            resp = requests.get(base_url, params=params, proxies=PROXIES, timeout=5)
            return resp.json()
        except Exception as e:
            print(f"❌ API Error: {e}")
            return None

def get_current_price():
    base_url = "https://api.mexc.com/api/v3/ticker/price"
    params = {"symbol": SYMBOL}
    try:
        resp = requests.get(base_url, params=params, timeout=5)
        return float(resp.json()['price'])
    except:
        return 0.0

# ════════════════ ANALYSIS MODULE ════════════════
def calculate_rsi(klines):
    if not klines or len(klines) < RSI_PERIOD:
        return 50.0
    
    closes = [float(k[4]) for k in klines]
    
    # Simple RSI Calculation
    gains = []
    losses = []
    
    for i in range(1, len(closes)):
        delta = closes[i] - closes[i-1]
        if delta > 0:
            gains.append(delta)
            losses.append(0)
        else:
            gains.append(0)
            losses.append(abs(delta))
            
    # Slicing to period
    avg_gain = sum(gains[-RSI_PERIOD:]) / RSI_PERIOD
    avg_loss = sum(losses[-RSI_PERIOD:]) / RSI_PERIOD
    
    if avg_loss == 0:
        return 100.0
        
    rs = avg_gain / avg_loss
    rsi = 100 - (100 / (1 + rs))
    return round(rsi, 2)

# ════════════════ MAIN LOOP ════════════════
def main():
    os.system('cls' if os.name == 'nt' else 'clear')
    print("╔══════════════════════════════════════════╗")
    print(f"║ 🌊 OCEAN HUNTER: {MODE} MODE             ║")
    print(f"║ 🎯 Symbol: {SYMBOL} | TF: {TIMEFRAME}           ║")
    print("╚══════════════════════════════════════════╝")
    
    msg = f"🚀 <b>BOT STARTED</b>\nMode: {MODE}\nSymbol: {SYMBOL}"
    send_telegram(msg)
    print("✅ Startup Message sent to Telegram.")
    
    print("\n⏳ Waiting for market data...")
    
    try:
        while True:
            # 1. Get Data
            klines = get_market_data()
            price = get_current_price()
            
            if klines and price > 0:
                # 2. Analyze
                rsi = calculate_rsi(klines)
                
                # 3. Display Status
                timestamp = datetime.now().strftime("%H:%M:%S")
                
                status_color = "\033[92m" if rsi < 30 else "\033[91m" if rsi > 70 else "\033[97m"
                print(f"[{timestamp}] Price: {price} | RSI: {status_color}{rsi}\033[0m")
                
                # 4. Strategy Logic (Simulation for now)
                if rsi < RSI_OVERSOLD:
                    print("    🟢 SIGNAL: POTENTIAL BUY (Oversold)")
                    # if MODE == 'LIVE': execute_trade(...)
                    
                elif rsi > RSI_OVERBOUGHT:
                    print("    🔴 SIGNAL: POTENTIAL SELL (Overbought)")
                    # if MODE == 'LIVE': execute_trade(...)

            else:
                print("⚠️  Data fetch failed, retrying...")

            time.sleep(CHECK_INTERVAL)

    except KeyboardInterrupt:
        print("\n🛑 Bot Stopped by user.")
        send_telegram("🛑 <b>BOT STOPPED</b>")

if __name__ == "__main__":
    main()
