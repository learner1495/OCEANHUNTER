
import os
import requests
from dotenv import load_dotenv

load_dotenv()

TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

def send_report():
    if not TOKEN or not CHAT_ID:
        print("⚠️ Telegram credentials missing.")
        return

    msg = (
        "⏳ **Ocean Hunter: Phase 2 Complete**\n\n"
        "✅ **Module:** Data Engine (`tests/core/data_engine.py`)\n"
        "✅ **Interface:** `IDataProvider` defined.\n"
        "✅ **Function:** CSV Reading & Time Simulation ready.\n"
        "✅ **Git:** Synced with remote.\n\n"
        "Ready for Phase 3: Integration (Connecting Wallet + Data)."
    )
    
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    payload = {"chat_id": CHAT_ID, "text": msg, "parse_mode": "Markdown"}
    
    try:
        resp = requests.post(url, json=payload, timeout=10)
        print(f"Telegram sent: {resp.status_code}")
    except Exception as e:
        print(f"Telegram fail: {e}")

if __name__ == "__main__":
    send_report()
