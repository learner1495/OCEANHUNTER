
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
        "🏗 **Ocean Hunter: Phase 1 Complete**\n\n"
        "✅ **Module:** Virtual Wallet (`tests/core/virtual_wallet.py`)\n"
        "✅ **Config:** MEXC Mode (Fee: 0.1%)\n"
        "✅ **Data Safety:** Existing test data preserved.\n"
        "✅ **Git:** Synced with remote.\n"
        "✅ **Context:** Updated to include test architecture.\n\n"
        "Ready for Phase 2: Data Provider Implementation."
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
