import os
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
    
    report_msg = "📊 OCEAN HUNTER DATA REPORT (V7.0)\n\n"
    success_count = 0
    
    for symbol in targets:
        # Fetch last 24 candles (1 Hour timeframe)
        candles = engine.fetch_candles(symbol, interval="60m", limit=24)
        
        if candles:
            saved = engine.save_to_csv(symbol, candles)
            if saved:
                last_price = candles[-1]['close']
                report_msg += f"✅ {symbol}: ${last_price}\n"
                success_count += 1
            else:
                report_msg += f"⚠️ {symbol}: Save Failed\n"
        else:
            report_msg += f"❌ {symbol}: Fetch Failed\n"
            
    # Final Report
    if success_count == len(targets):
        report_msg += "\n✅ All Systems Operational.\nReady for Analysis."
    else:
        report_msg += "\n⚠️ Some data streams failed."
        
    print(f"\n[3] 📨 Sending Report...")
    send_telegram(report_msg)
    print("✅ Done.")

if __name__ == "__main__":
    main()
