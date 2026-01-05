
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
    send_telegram(f"▶️ <b>Ocean Hunter Engine Started</b>\nMode: {MODE}\nSymbol: {SYMBOL}")
    
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
            print("\n🛑 Stopping Engine...")
            send_telegram("🛑 <b>Ocean Hunter Engine Stopped</b>")
            break
        except Exception as e:
            print(f"Error: {e}")
            time.sleep(5)

if __name__ == "__main__":
    main()
