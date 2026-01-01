# modules/network/telegram_bot.py
import os
import requests
from typing import Dict, Any
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

class TelegramBot:
    BASE_URL = "https://api.telegram.org/bot"

    def __init__(self):
        self.token = os.getenv("TELEGRAM_BOT_TOKEN", "")
        self.chat_id = os.getenv("TELEGRAM_CHAT_ID", "")
        self.enabled = bool(self.token and self.chat_id)

    def _send_request(self, method: str, data: dict) -> Dict[str, Any]:
        if not self.enabled:
            return {"ok": False, "error": "Bot not configured"}

        url = f"{self.BASE_URL}{self.token}/{method}"

        try:
            response = requests.post(url, json=data, timeout=10)
            return response.json()
        except Exception as e:
            return {"ok": False, "error": str(e)}

    def send_message(self, text: str, parse_mode: str = "HTML") -> Dict[str, Any]:
        return self._send_request("sendMessage", {
            "chat_id": self.chat_id,
            "text": text,
            "parse_mode": parse_mode
        })

    def send_alert(self, title: str, message: str, alert_type: str = "INFO") -> Dict[str, Any]:
        icons = {"INFO": "ℹ️", "SUCCESS": "✅", "WARNING": "⚠️", "ERROR": "❌", "TRADE": "💰"}
        icon = icons.get(alert_type.upper(), "📌")
        timestamp = datetime.now().strftime("%H:%M:%S")

        text = f"{icon} <b>{title}</b>\n\n{message}\n\n<code>🕐 {timestamp}</code>"
        return self.send_message(text)

_bot = None

def get_bot() -> TelegramBot:
    global _bot
    if _bot is None:
        _bot = TelegramBot()
    return _bot

def send_alert(title: str, message: str, alert_type: str = "INFO") -> Dict[str, Any]:
    return get_bot().send_alert(title, message, alert_type)
