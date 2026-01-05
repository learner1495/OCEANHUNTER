
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
