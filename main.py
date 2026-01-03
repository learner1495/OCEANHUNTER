import os
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
    
    report_msg = "🧠 OCEAN HUNTER ANALYSIS (V7.1)\n"
    report_msg += "Strategy: RSI (14) - 1 Hour Timeframe\n"
    report_msg += "─" * 20 + "\n\n"
    
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
                
            line = f"🔹 {symbol.replace('USDT','')}: {price_str}\n"
            line += f"   RSI: {result['rsi']} → {result['signal']}\n"
            report_msg += line + "\n"
            
            print(f"   ✅ {symbol}: RSI={result['rsi']} ({result['signal']})")
        else:
            report_msg += f"❌ {symbol}: Connection Failed\n"
            
    print(f"\n[3] 📨 Sending Analysis Report...")
    send_telegram(report_msg)
    print("✅ Done.")

if __name__ == "__main__":
    main()
