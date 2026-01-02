import requests
import logging
import os
from dotenv import load_dotenv

load_dotenv()
logger = logging.getLogger("TelegramBot")

class TelegramBot:
    def __init__(self):
        self.token = os.getenv("TELEGRAM_BOT_TOKEN")
        self.chat_id = os.getenv("TELEGRAM_CHAT_ID")
        self.enabled = bool(self.token and self.chat_id)
        
        # ⚠️ TELEGRAM NEEDS VPN (Use System Proxy)
        self.session = requests.Session()
        self.session.trust_env = True 

    def send_message(self, message):
        if not self.enabled:
            return False

        url = f"https://api.telegram.org/bot{self.token}/sendMessage"
        payload = {
            "chat_id": self.chat_id,
            "text": message,
            "parse_mode": "Markdown"
        }

        try:
            response = self.session.post(url, json=payload, timeout=10)
            return response.status_code == 200
        except Exception as e:
            logger.error(f"Telegram Connection Error: {e}")
            return False