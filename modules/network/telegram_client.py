
import os
import requests
from dotenv import load_dotenv

# Ensure env is loaded
load_dotenv(os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), '.env'))

class TelegramBot:
    def __init__(self):
        self.token = os.getenv("TELEGRAM_BOT_TOKEN")
        self.chat_id = os.getenv("TELEGRAM_CHAT_ID")
        self.base_url = f"https://api.telegram.org/bot{self.token}/sendMessage"

    def send_message(self, message):
        if not self.token or not self.chat_id:
            print(f"🔕 Telegram Auth Missing (Check .env).")
            return False

        payload = {
            "chat_id": self.chat_id,
            "text": message,
            "parse_mode": "HTML"
        }
        
        try:
            # Using verify=False to avoid SSL issues on some local proxies, can be removed in prod
            response = requests.post(self.base_url, json=payload, timeout=10)
            if response.status_code == 200:
                return True
            else:
                print(f"❌ TG Error {response.status_code}: {response.text}")
                return False
        except Exception as e:
            print(f"❌ TG Connection Error: {e}")
            return False
