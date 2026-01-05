
import os
import sys
import time
import requests
from dotenv import load_dotenv

sys.path.append(os.getcwd())
from data.mexc_provider import MEXCProvider

load_dotenv()
MODE = os.getenv("MODE", "PAPER").upper()
SYMBOL = "SOLUSDT"
TG_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
TG_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

def send_telegram(msg):
    if not TG_TOKEN or not TG_CHAT_ID: return
    try:
        url = f"https://api.telegram.org/bot{TG_TOKEN}/sendMessage"
        payload = {"chat_id": TG_CHAT_ID, "text": msg, "parse_mode": "HTML"}
        requests.post(url, json=payload, timeout=5)
    except: pass

def main():
    print(f" OCEAN HUNTER ENGINE | Mode: {MODE}")
    print("=" * 40)
    send_telegram(f"▶️ <b>Engine Started</b> [{MODE}]")
    
    provider = MEXCProvider()
    print(f"   Listening on {SYMBOL}...")
    
    try:
        while True:
            print(f"   [{time.strftime('%H:%M:%S')}] Heartbeat OK - Scanning...")
            time.sleep(10)
    except KeyboardInterrupt:
        print("\nSTOPPING...")
        send_telegram("🛑 <b>Engine Stopped</b>")

if __name__ == "__main__":
    main()
