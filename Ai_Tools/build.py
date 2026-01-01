# ═══════════════════════════════════════════════════════════════
# AI_Tools/build.py — Session 2: Network Modules
# OCEAN HUNTER V10.8.2 — COMPLETE FILE
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

# ═══════════════════════════════════════════════════════════════
# ERROR TRACKING
# ═══════════════════════════════════════════════════════════════
errors = []

def log_error(step, error):
    errors.append(f"[{step}] {error}")
    print(f"      ⚠️ Error: {error}")

# ═══════════════════════════════════════════════════════════════
# SESSION 2 CONFIG
# ═══════════════════════════════════════════════════════════════
FOLDERS = []
MAIN_FILE = "main.py"

# ═══════════════════════════════════════════════════════════════
# FILE CONTENTS
# ═══════════════════════════════════════════════════════════════

ENV_CONTENT = '''# OCEAN HUNTER V10.8.2 — Environment Variables
MODE=PAPER
NOBITEX_API_KEY=eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJ0b2tlbl9pZCI6NTM1NTY0LCJwYXlsb2FkIjp7ImNsaWVudF9pZCI6ImxlYXJuZXIxNDk1IiwidG9rZW5fdHlwZSI6InRyYWRlIiwiY3JlYXRlX3RpbWUiOjE3MzU3MjA5NjYsImV4cGlyZV90aW1lIjoxNzY3MjU2OTY2LCJzY29wZXMiOlsidHJhZGUiXX19.Vy2YCMQ0LoLqxPDqfVdvLPFCNUQkRA-_6Lo7e3rgDzM
TELEGRAM_BOT_TOKEN=8519168043:AAEeRDhMogTxpElxgB0zUom9YzKXAnRBKew
TELEGRAM_CHAT_ID=6539865961
MAX_POSITION_USDT=100
GLOBAL_STOP_LOSS_PCT=15
'''

REQUIREMENTS_CONTENT = '''requests>=2.31.0
python-dotenv>=1.0.0
pandas>=2.0.0
numpy>=1.24.0
aiohttp>=3.9.0
'''

RATE_LIMITER_CONTENT = '''import time
import threading
from typing import Optional

class RateLimiter:
    def __init__(self, max_tokens: int = 60, refill_seconds: float = 60.0):
        self.max_tokens = max_tokens
        self.tokens = max_tokens
        self.refill_rate = max_tokens / refill_seconds
        self.last_refill = time.time()
        self.lock = threading.Lock()
        self.min_spacing = 0.5
        self.last_request = 0.0
    
    def _refill(self):
        now = time.time()
        elapsed = now - self.last_refill
        self.tokens = min(self.max_tokens, self.tokens + elapsed * self.refill_rate)
        self.last_refill = now
    
    def acquire(self, tokens: int = 1, timeout: Optional[float] = 30.0) -> bool:
        start_time = time.time()
        while True:
            with self.lock:
                self._refill()
                spacing = time.time() - self.last_request
                if spacing < self.min_spacing:
                    time.sleep(self.min_spacing - spacing)
                if self.tokens >= tokens:
                    self.tokens -= tokens
                    self.last_request = time.time()
                    return True
            if timeout and (time.time() - start_time) >= timeout:
                return False
            time.sleep(0.1)
    
    def get_status(self) -> dict:
        with self.lock:
            self._refill()
            return {"tokens_available": round(self.tokens, 2), "max_tokens": self.max_tokens}

_limiter = RateLimiter()
def acquire(tokens: int = 1) -> bool:
    return _limiter.acquire(tokens)
def get_status() -> dict:
    return _limiter.get_status()
'''

NOBITEX_API_CONTENT = '''import os
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
        self._last_request_time = 0
    
    def _request(self, method: str, endpoint: str, data: dict = None) -> Dict[str, Any]:
        if not rate_limiter.acquire():
            return {"status": "error", "message": "Rate limit exceeded"}
        
        elapsed = time.time() - self._last_request_time
        if elapsed < 0.5:
            time.sleep(0.5 - elapsed)
        
        url = f"{self.BASE_URL}{endpoint}"
        try:
            if method.upper() == "GET":
                response = self.session.get(url, params=data, timeout=10)
            else:
                response = self.session.post(url, json=data, timeout=10)
            self._last_request_time = time.time()
            if response.status_code == 200:
                return response.json()
            return {"status": "error", "code": response.status_code}
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
            result["public_api"] = Truewallets = self.get_wallets()
        if wallets.get("status") == "ok":
            result["private_api"] = True
            result["message"] = "Full access"
        else:
            result["message"] = "Auth issue"
        return result
    
    def get_rate_limit_status(self) -> Dict[str, Any]:
        return rate_limiter.get_status()

_client: Optional[NobitexAPI] = None
def get_client() -> NobitexAPI:
    global _client
    if _client is None:
        _client = NobitexAPI()
    return _client
'''

TELEGRAM_BOT_CONTENT = '''import os
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
        text = f"🚀 <b>OCEAN HUNTER STARTED</b>\\nMode: {mode}\\nTime: {datetime.now()}"
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
    return get_bot().send_message(f"{title}\\n{msg}")
'''

NETWORK_INIT_CONTENT = '''from .nobitex_api import NobitexAPI, get_client
from .telegram_bot import TelegramBot, get_bot, send_alert
from .rate_limiter import RateLimiter, acquire, get_status
'''

MAIN_PY_CONTENT = '''import os
from dotenv import load_dotenv
load_dotenv()

def main():
    print("=" * 50)
    print("OCEAN HUNTER V10.8.2")
    print("=" * 50)
    mode = os.getenv("MODE", "PAPER")
    print(f"Mode: {mode}")
    
    try:
        from modules.network import get_client, get_bot
        
        print("\\n[1] Nobitex API...")
        client = get_client()
        r = client.test_connection()
        print(f"    Public: {r['public_api']}, Private: {r['private_api']}")
        
        print("\\n[2] Telegram...")
        bot = get_bot()
        tr = bot.test_connection()
        print(f"    Status: {tr['message']}")
        if tr.get("ok"):
            bot.send_startup(mode)
        print("\\n[3] Rate Limiter...")
        rl = client.get_rate_limit_status()
        print(f"    Tokens: {rl['tokens_available']}/{rl['max_tokens']}")except Exception as e:
        print(f"Error: {e}")
    print("\\n" + "=" * 50)
    print("Session 2 Complete")

if __name__ == "__main__":
    main()
'''

# ═══════════════════════════════════════════════════════════════
# FILES DICT
# ═══════════════════════════════════════════════════════════════
NEW_FILES = {
    "modules/network/rate_limiter.py": RATE_LIMITER_CONTENT,
    "modules/network/nobitex_api.py": NOBITEX_API_CONTENT,
    "modules/network/telegram_bot.py": TELEGRAM_BOT_CONTENT,
    "modules/network/__init__.py": NETWORK_INIT_CONTENT,
}

MODIFY_FILES = {
    ".env": ENV_CONTENT,
    "requirements.txt": REQUIREMENTS_CONTENT,
    "main.py": MAIN_PY_CONTENT,
}

# ═══════════════════════════════════════════════════════════════
# BUILD STEPS
# ═══════════════════════════════════════════════════════════════
def step1_system():
    print("\n[1/9] System Check...")
    try:
        socket.create_connection(("8.8.8.8", 53), timeout=3)
        print("      OK")
    except Exception as e:
        log_error("Step1", e)

def step2_venv():
    print("\n[2/9] Venv...")
    if os.path.exists(VENV_PYTHON):
        print("      Exists")
    else:
        subprocess.run([sys.executable, "-m", "venv", VENV_PATH], check=True)
        print("      Created")

def step3_deps():
    print("\n[3/9] Dependencies...")
    req = os.path.join(ROOT, "requirements.txt")
    if os.path.exists(req):
        subprocess.run([VENV_PYTHON, "-m", "pip", "install", "-r", req, "-q"], capture_output=True)
        print("      Installed")

def step4_folders():
    print("\n[4/9] Folders...")
    print("      None needed")

def step5_new_files():
    print("\n[5/9] New Files...")
    for path, content in NEW_FILES.items():
        full = os.path.join(ROOT, path)
        os.makedirs(os.path.dirname(full), exist_ok=True)
        with open(full, "w", encoding="utf-8") as f:
            f.write(content)
        print(f"      Created: {path}")

def step6_modify():
    print("\n[6/9] Modify Files...")
    for path, content in MODIFY_FILES.items():
        full = os.path.join(ROOT, path)
        with open(full, "w", encoding="utf-8") as f:
            f.write(content)
        print(f"      Modified: {path}")

# ═══════════════════════════════════════════════════════════════
# MAIN
# ═══════════════════════════════════════════════════════════════
def main():
    start = datetime.now()
    print("\n" + "=" * 50)
    print("BUILD SESSION 2 | Network Modules")
    print("=" * 50)

    step1_system()
    step2_venv()
    step3_deps()
    step4_folders()
    step5_new_files()
    step6_modify()

    print("\n[7/9] Context...")
    try:
        context_gen.create_context_file()
        print("      Done")
    except Exception as e:
        log_error("Context", e)

    print("\n[8/9] Git...")
    try:
        setup_git.setup()
        setup_git.sync("Session 2: Network Modules")
        print("      Synced")
    except Exception as e:
        log_error("Git", e)

    print("\n[9/9] Launch...")
    main_path = os.path.join(ROOT, MAIN_FILE)
    if os.path.exists(main_path):
        subprocess.run([VENV_PYTHON, main_path], cwd=ROOT)

    print("\n" + "=" * 50)
    if errors:
        print(f"Done with {len(errors)} error(s)")
    else:
        print("BUILD COMPLETE")
    print("=" * 50)

if __name__ == "__main__":
    main()
