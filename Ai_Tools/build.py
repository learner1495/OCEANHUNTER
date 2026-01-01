# AI_Tools/build.py — V3.8 Full Rebuild
# ═══════════════════════════════════════════════════════════════

import os
import sys
import subprocess
import socket
from datetime import datetime

import context_gen
import setup_git

# ═══════════════════════════════════════════════════════════════
# PATHS
# ═══════════════════════════════════════════════════════════════
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(SCRIPT_DIR)
VENV_PATH = os.path.join(ROOT, ".venv")
VENV_PYTHON = os.path.join(VENV_PATH, "Scripts", "python.exe") if sys.platform == "win32" else os.path.join(VENV_PATH, "bin", "python")

MAIN_FILE = "main.py"
errors = []

def log_error(step, error):
    errors.append(f"[{step}] {error}")
    print(f"      ⚠️ Error: {error}")

# ═══════════════════════════════════════════════════════════════
# FILE CONTENTS
# ═══════════════════════════════════════════════════════════════

MAIN_PY_CONTENT = '''#!/usr/bin/env python3
"""
OCEAN HUNTER V10.8.2 — Main Entry Point
"""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from dotenv import load_dotenv
load_dotenv()

def main():
    print("\\n" + "=" * 50)
    print("🌊 OCEAN HUNTER V10.8.2")
    print("=" * 50)

    mode = os.getenv("MODE", "PAPER")
    print(f"\\n🔧 Mode: {mode}")

    # ─── 1. تست Nobitex API ───
    print("\\n[1/3] 🔌 Testing Nobitex API...")
    try:
        from modules.network import get_client
        client = get_client()
        result = client.test_connection()

        pub = "✅" if result["public_api"] else "❌"
        prv = "✅" if result["private_api"] else "❌"
        print(f"      Public API:  {pub}")
        print(f"      Private API: {prv}")
        print(f"      Message: {result['message']}")

    except Exception as e:
        print(f"      ❌ Error: {e}")

    # ─── 2. تست Telegram Bot ───
    print("\\n[2/3] 📱 Testing Telegram Bot...")
    try:
        from modules.network import get_bot
        bot = get_bot()

        if bot.enabled:
            response = bot.send_alert(
                title="OCEAN HUNTER ONLINE",
                message="✅ سیستم با موفقیت راه‌اندازی شد",
                alert_type="SUCCESS"
            )
            if response.get("ok"):
                print("      ✅ Telegram message sent!")
            else:
                err = response.get("error", "Unknown")
                print(f"      ⚠️ Telegram error: {err}")
        else:
            print("      ⚠️ Telegram not configured")

    except Exception as e:
        print(f"      ❌ Error: {e}")

    # ─── 3. نمایش Rate Limiter ───
    print("\\n[3/3] ⏱️ Rate Limiter Status...")
    try:
        from modules.network import get_statusrl_status = get_status()
        tokens = rl_status.get("tokens_available", "N/A")
        max_t = rl_status.get("max_tokens", "N/A")
        usage = rl_status.get("usage_percent", "N/A")
        print(f"      Tokens: {tokens}/{max_t}")
        print(f"      Usage:  {usage}%")

    except Exception as e:
        print(f"      ❌ Error: {e}")

    # ─── پایان ───
    print("\\n" + "=" * 50)
    print("✅ ALL TESTS COMPLETE")
    print("=" * 50 + "\\n")

if __name__ == "__main__":
    main()
'''

NOBITEX_API_CONTENT = '''# modules/network/nobitex_api.py
import os
import time
import requests
from typing import Optional, Dict, Any
from dotenv import load_dotenv
from . import rate_limiter

load_dotenv()

class NobitexAPI:
    BASE_URL = "https://api.nobitex.ir"

    def __init__(self):
        self.api_key = os.getenv("NOBITEX_API_KEY", "")
        self.session = requests.Session()
        self.session.headers.update({
            "Authorization": f"Token {self.api_key}",
            "Content-Type": "application/json"
        })

    def _request(self, method: str, endpoint: str, data: dict = None) -> Dict[str, Any]:
        if not rate_limiter.acquire():
            return {"status": "error", "message": "Rate limit exceeded"}

        url = f"{self.BASE_URL}{endpoint}"

        try:
            if method.upper() == "GET":
                response = self.session.get(url, params=data, timeout=10)
            else:
                response = self.session.post(url, json=data, timeout=10)

            if response.status_code == 200:
                return response.json()
            else:
                return {"status": "error", "code": response.status_code, "message": response.text[:200]}

        except Exception as e:
            return {"status": "error", "message": str(e)}

    def get_market_stats(self) -> Dict[str, Any]:
        return self._request("GET", "/market/stats")

    def get_wallets(self) -> Dict[str, Any]:
        return self._request("POST", "/users/wallets/list")

    def test_connection(self) -> Dict[str, Any]:
        result = {"public_api": False, "private_api": False, "message": ""}

        stats = self.get_market_stats()
        if stats.get("status") == "ok":
            result["public_api"] = True

        wallet_result = self.get_wallets()
        if wallet_result.get("status") == "ok":
            result["private_api"] = True
            result["message"] = "Full access confirmed"
        else:
            msg = wallet_result.get("message", "Auth failed")
            result["message"] = msg

        return result

_client: Optional[NobitexAPI] = None

def get_client() -> NobitexAPI:
    global _client
    if _client is None:
        _client = NobitexAPI()
    return _client
'''

TELEGRAM_BOT_CONTENT = '''# modules/network/telegram_bot.py
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

        text = f"{icon} <b>{title}</b>\\n\\n{message}\\n\\n<code>🕐 {timestamp}</code>"
        return self.send_message(text)

_bot = None

def get_bot() -> TelegramBot:
    global _bot
    if _bot is None:
        _bot = TelegramBot()
    return _bot

def send_alert(title: str, message: str, alert_type: str = "INFO") -> Dict[str, Any]:
    return get_bot().send_alert(title, message, alert_type)
'''

RATE_LIMITER_CONTENT = '''# modules/network/rate_limiter.py
import time
import threading

class RateLimiter:
    def __init__(self, max_tokens: int = 60, refill_seconds: float = 60.0):
        self.max_tokens = max_tokens
        self.tokens = max_tokens
        self.refill_rate = max_tokens / refill_seconds
        self.last_refill = time.time()
        self.lock = threading.Lock()

    def _refill(self):
        now = time.time()
        elapsed = now - self.last_refill
        self.tokens = min(self.max_tokens, self.tokens + elapsed * self.refill_rate)
        self.last_refill = now

    def acquire(self, tokens: int = 1) -> bool:
        with self.lock:
            self._refill()
            if self.tokens >= tokens:
                self.tokens -= tokens
                return True
            return False

    def get_status(self) -> dict:
        with self.lock:
            self._refill()
            return {
                "tokens_available": round(self.tokens, 2),
                "max_tokens": self.max_tokens,
                "usage_percent": round((1 - self.tokens/self.max_tokens) * 100, 1)
            }

_limiter = RateLimiter()

def acquire(tokens: int = 1) -> bool:
    return _limiter.acquire(tokens)

def get_status() -> dict:
    return _limiter.get_status()
'''

NETWORK_INIT_CONTENT = '''# modules/network/__init__.py
from .nobitex_api import NobitexAPI, get_client
from .telegram_bot import TelegramBot, get_bot, send_alert
from .rate_limiter import RateLimiter, acquire, get_status

__all__ = [
    "NobitexAPI", "get_client",
    "TelegramBot", "get_bot", "send_alert",
    "RateLimiter", "acquire", "get_status"
]
'''

# ═══════════════════════════════════════════════════════════════
# BUILD STEPS
# ═══════════════════════════════════════════════════════════════

def step1_system():
    print("\n[1/9] 🌐 System Check...")
    try:
        socket.create_connection(("8.8.8.8", 53), timeout=3)
        print("      ✅ Internet OK")
    except Exception as e:
        log_error("Step1", f"No internet - {e}")

def step2_venv():
    print("\n[2/9] 🐍 Virtual Environment...")
    try:
        if os.path.exists(VENV_PYTHON):
            print("      ✅ Exists")
            return
        subprocess.run([sys.executable, "-m", "venv", VENV_PATH], check=True)
        print("      ✅ Created")
    except Exception as e:
        log_error("Step2", e)

def step3_deps():
    print("\n[3/9] 📦 Dependencies...")
    try:
        req = os.path.join(ROOT, "requirements.txt")
        if not os.path.exists(req):
            print("      ℹ️ No requirements.txt")
            return
        subprocess.run([VENV_PYTHON, "-m", "pip", "install", "-r", req, "-q"],capture_output=True, check=True)
        print("      ✅ Installed")
    except Exception as e:
        log_error("Step3", e)

def step4_folders():
    print("\n[4/9] 📁 Folders...")
    network_dir = os.path.join(ROOT, "modules", "network")
    if not os.path.exists(network_dir):
        os.makedirs(network_dir)
        print(f"      ✅ Created: modules/network/")
    else:
        print("      ✅ Exists")

def step5_write_files():
    print("\n[5/9] 📝 Writing Files...")
    
    files_to_write = {
        "main.py": MAIN_PY_CONTENT,
        "modules/network/__init__.py": NETWORK_INIT_CONTENT,
        "modules/network/nobitex_api.py": NOBITEX_API_CONTENT,
        "modules/network/telegram_bot.py": TELEGRAM_BOT_CONTENT,
        "modules/network/rate_limiter.py": RATE_LIMITER_CONTENT,
    }
    
    for rel_path, content in files_to_write.items():
        full_path = os.path.join(ROOT, rel_path)
        parent = os.path.dirname(full_path)
        if parent and not os.path.exists(parent):
            os.makedirs(parent)
        with open(full_path, "w", encoding="utf-8") as f:
            f.write(content)
        print(f"      ✅ {rel_path}")

def step6_context():
    print("\n[6/9] 📋 Context Generation...")
    try:
        context_gen.create_context_file()
        print("      ✅ Context created")
    except Exception as e:
        log_error("Step6-Context", e)

def step7_git():
    print("\n[7/9] 🐙 Git Sync...")
    try:
        setup_git.setup()
        setup_git.sync(f"Build V3.8: {datetime.now().strftime('%Y-%m-%d %H:%M')}")
        print("      ✅ Git synced")
    except Exception as e:
        log_error("Step7-Git", e)

def step8_launch():
    print("\n[8/9] 🚀 Launch...")
    main_path = os.path.join(ROOT, MAIN_FILE)
    if os.path.exists(main_path):
        print("      " + "─" * 40)
        subprocess.run([VENV_PYTHON, main_path], cwd=ROOT)
    else:
        print(f"      ℹ️ No {MAIN_FILE}")

def step9_summary():
    print("\n[9/9] 📊 Summary...")
    print("      ✅ All steps executed")

# ═══════════════════════════════════════════════════════════════
# MAIN
# ═══════════════════════════════════════════════════════════════
def main():
    start_time = datetime.now()

    print("\n" + "═" * 60)
    print(f"🔧 BUILD V3.8 — FULL REBUILD")
    print(f"📁 Project: {os.path.basename(ROOT)}")
    print(f"⏰ Started: {start_time.strftime('%Y-%m-%d %H:%M:%S')}")
    print("═" * 60)

    try:
        step1_system()
        step2_venv()
        step3_deps()
        step4_folders()
        step5_write_files()
        step6_context()
        step7_git()
        step8_launch()
        step9_summary()
    except KeyboardInterrupt:
        print("\n\n⛔ Build cancelled by user")
        errors.append("KeyboardInterrupt")

    except Exception as e:
        print(f"\n\n💥 Critical error: {e}")
        errors.append(f"Critical: {e}")

    finally:
        end_time = datetime.now()
        duration = (end_time - start_time).seconds

        print("\n" + "═" * 60)
        if errors:
            print(f"⚠️ BUILD COMPLETE WITH {len(errors)} ERROR(S):")
            for err in errors:
                print(f"   • {err}")
        else:
            print("✅ BUILD COMPLETE — NO ERRORS")
        print("─" * 60)
        print(f"⏱️ Duration: {duration}s")
        print(f"🏁 Finished: {end_time.strftime('%H:%M:%S')}")
        print("═" * 60 + "\n")

if __name__ == "__main__":
    main()
