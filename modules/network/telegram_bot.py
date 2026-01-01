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
    
    def send_message(self, text: str) -> Dict[str, Any]:
        if not self.enabled:
            return {"ok": False, "error": "Not configured"}
        url = f"{self.BASE_URL}{self.token}/sendMessage"
        try:
            r = requests.post(url, json={"chat_id": self.chat_id, "text": text, "parse_mode": "HTML"}, timeout=10)
            return r.json()
        except Exception as e:
            return {"ok": False, "error": str(e)}
    
    def send_startup(self, mode: str) -> Dict[str, Any]:
        text = f"🚀 <b>OCEAN HUNTER STARTED</b>\nMode: {mode}\nTime: {datetime.now()}"
        return self.send_message(text)
    
    def test_connection(self) -> Dict[str, Any]:
        if not self.enabled:
            return {"ok": False, "message": "Not configured"}
        r = self.send_message("🔧 Test OK")
        return {"ok": r.get("ok", False), "message": "Connected" if r.get("ok") else "Failed"}

_bot = None
def get_bot() -> TelegramBot:
    global _bot
    if _bot is None:
        _bot = TelegramBot()
    return _bot

def send_alert(title: str, msg: str, t: str = "INFO") -> Dict[str, Any]:
    return get_bot().send_message(f"{title}\n{msg}")
