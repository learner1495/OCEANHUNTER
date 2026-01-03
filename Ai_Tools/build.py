# ═══════════════════════════════════════════════════════════════
# شروع بخش ۱ از ۲
# ═══════════════════════════════════════════════════════════════

# AI_Tools/build.py — MEXC Auth Fix + Telegram SOCKS5
# Reference: BUILD-FIX-083
# Template: V3.5

import os
import sys
import subprocess
import socket
from datetime import datetime

# ═══════════════════════════════════════════════════════════════
# PATHS
# ═══════════════════════════════════════════════════════════════
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(SCRIPT_DIR)
VENV_PATH = os.path.join(ROOT, ".venv")
VENV_PYTHON = os.path.join(VENV_PATH, "Scripts", "python.exe") if sys.platform == "win32" else os.path.join(VENV_PATH, "bin", "python")

# ═══════════════════════════════════════════════════════════════
# CONFIG
# ═══════════════════════════════════════════════════════════════
FOLDERS = []
NEW_FILES = {}
MAIN_FILE = "main.py"
errors = []

def log_error(step, error):
    errors.append(f"[{step}] {error}")
    print(f"      ⚠️ Error: {error}")

# ═══════════════════════════════════════════════════════════════
# MODIFY_FILES — فایل‌هایی که اصلاح می‌شوند
# ═══════════════════════════════════════════════════════════════

MODIFY_FILES = {

# ─────────────────────────────────────────────────────────────
# FILE 1: modules/network/mexc_api.py (Auth Fix)
# ─────────────────────────────────────────────────────────────
"modules/network/mexc_api.py": '''"""
MEXC API Client — Raw Socket Implementation
For OCEAN HUNTER V10.8.2
Fixed: Content-Type header for authentication
"""

import socket
import ssl
import hmac
import hashlib
import time
import json
import os
import logging
from urllib.parse import urlencode
from dotenv import load_dotenv

load_dotenv()
logger = logging.getLogger("MEXC_API")


class MEXCClient:
    """MEXC Spot API via raw HTTPS socket"""

    def __init__(self):
        self.api_key = os.getenv("MEXC_API_KEY", "")
        self.api_secret = os.getenv("MEXC_SECRET_KEY", "")
        self.host = "api.mexc.com"
        self.base_path = "/api/v3"

    def _raw_request(self, method: str, path: str, params: dict = None, signed: bool = False) -> dict:
        """Send HTTPS request via raw socket"""
        params = params or {}

        if signed:
            params["timestamp"] = int(time.time() * 1000)
            query = urlencode(params)
            signature = hmac.new(
                self.api_secret.encode("utf-8"),
                query.encode("utf-8"),
                hashlib.sha256
            ).hexdigest()
            params["signature"] = signature

        query_string = urlencode(params) if params else ""

        if method == "GET":
            full_path = f"{self.base_path}{path}"
            if query_string:
                full_path += f"?{query_string}"
            body = ""
            content_type = "application/json"
        else:
            full_path = f"{self.base_path}{path}"
            body = query_string
            content_type = "application/x-www-form-urlencoded"

        headers = [
            f"{method} {full_path} HTTP/1.1",
            f"Host: {self.host}",
            f"X-MEXC-APIKEY: {self.api_key}",
            f"Content-Type: {content_type}",
            "Connection: close",
        ]

        if body:
            headers.append(f"Content-Length: {len(body)}")

        request = "\\r\\n".join(headers) + "\\r\\n\\r\\n"
        if body:
            request += body

        try:
            context = ssl.create_default_context()
            with socket.create_connection((self.host, 443), timeout=15) as sock:
                with context.wrap_socket(sock, server_hostname=self.host) as ssock:
                    ssock.sendall(request.encode("utf-8"))
                    response = b""
                    while True:
                        chunk = ssock.recv(4096)
                        if not chunk:
                            break
                        response += chunk

            response_text = response.decode("utf-8", errors="ignore")

            if "\\r\\n\\r\\n" in response_text:
                _, body_text = response_text.split("\\r\\n\\r\\n", 1)
            else:
                body_text = response_text

            if body_text.startswith("{") or body_text.startswith("["):
                return json.loads(body_text)
            else:
                lines = body_text.split("\\r\\n")
                for line in lines:
                    line = line.strip()
                    if line.startswith("{") or line.startswith("["):
                        return json.loads(line)
            return {"raw": body_text}

        except json.JSONDecodeError as e:
            logger.error(f"JSON parse error: {e}")
            return {"error": str(e)}
        except Exception as e:
            logger.error(f"Request failed: {e}")
            return {"error": str(e)}

    def ping(self) -> dict:
        return self._raw_request("GET", "/ping")

    def get_server_time(self) -> dict:
        return self._raw_request("GET", "/time")

    def get_ticker_price(self, symbol: str = "BTCUSDT") -> dict:
        return self._raw_request("GET", "/ticker/price", {"symbol": symbol})

    def get_orderbook(self, symbol: str, limit: int = 20) -> dict:
        return self._raw_request("GET", "/depth", {"symbol": symbol, "limit": limit})

    def get_account(self) -> dict:
        return self._raw_request("GET", "/account", signed=True)

    def get_balance(self, asset: str = None) -> dict:
        account = self.get_account()
        if "error" in account:
            return account
        balances = account.get("balances", [])
        if asset:
            for b in balances:
                if b.get("asset") == asset:
                    return b
            return {"asset": asset, "free": "0", "locked": "0"}
        return {"balances": balances}

    def create_order(self, symbol: str, side: str, order_type: str,
                     quantity: float, price: float = None) -> dict:
        params = {
            "symbol": symbol,
            "side": side.upper(),
            "type": order_type.upper(),
            "quantity": str(quantity),
        }
        if price and order_type.upper() == "LIMIT":
            params["price"] = str(price)
        return self._raw_request("POST", "/order", params, signed=True)

    def cancel_order(self, symbol: str, order_id: str = None) -> dict:
        params = {"symbol": symbol}
        if order_id:
            params["orderId"] = order_id
        return self._raw_request("DELETE", "/order", params, signed=True)

    def get_open_orders(self, symbol: str = None) -> dict:
        params = {"symbol": symbol} if symbol else {}
        return self._raw_request("GET", "/openOrders", params, signed=True)


_client_instance = None

def get_client() -> MEXCClient:
    global _client_instance
    if _client_instance is None:
        _client_instance = MEXCClient()
    return _client_instance
''',

# ─────────────────────────────────────────────────────────────
# FILE 2: modules/network/telegram_bot.py (Full SOCKS5)
# ─────────────────────────────────────────────────────────────
"modules/network/telegram_bot.py": '''"""
Telegram Bot — SOCKS5 Proxy Support
For OCEAN HUNTER V10.8.2
"""

import socket
import ssl
import json
import os
import logging
from urllib.parse import quote
from dotenv import load_dotenv

load_dotenv()
logger = logging.getLogger("TELEGRAM")


class TelegramBot:
    """Telegram Bot via SOCKS5 proxy (Raw Socket)"""

    def __init__(self):
        self.token = os.getenv("TELEGRAM_BOT_TOKEN", "")
        self.chat_id = os.getenv("TELEGRAM_CHAT_ID", "")
        self.proxy_host = os.getenv("PROXY_HOST", "127.0.0.1")
        self.proxy_port = int(os.getenv("PROXY_PORT", "1080"))
        self.use_proxy = os.getenv("USE_PROXY", "true").lower() == "true"
        self.api_host = "api.telegram.org"

    def _socks5_connect(self, target_host: str, target_port: int) -> socket.socket:
        """Connect via SOCKS5 proxy"""
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(15)
        sock.connect((self.proxy_host, self.proxy_port))

        sock.sendall(b"\\x05\\x01\\x00")
        resp = sock.recv(2)
        if resp != b"\\x05\\x00":
            raise Exception(f"SOCKS5 handshake failed: {resp.hex()}")

        req = b"\\x05\\x01\\x00\\x03"
        req += bytes([len(target_host)]) + target_host.encode()
        req += target_port.to_bytes(2, "big")
        sock.sendall(req)

        resp = sock.recv(10)
        if resp[1] != 0:
            raise Exception(f"SOCKS5 connect failed: code {resp[1]}")

        return sock

    def _direct_connect(self, target_host: str, target_port: int) -> socket.socket:
        """Direct connection without proxy"""
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(15)
        sock.connect((target_host, target_port))
        return sock

    def _request(self, method: str, params: dict = None) -> dict:
        """Send request to Telegram API"""
        params = params or {}
        path = f"/bot{self.token}/{method}"

        if params:
            query = "&".join(f"{k}={quote(str(v))}" for k, v in params.items())
            path = f"{path}?{query}"

        request = f"GET {path} HTTP/1.1\\r\\n"
        request += f"Host: {self.api_host}\\r\\n"
        request += "Connection: close\\r\\n\\r\\n"

        try:
            if self.use_proxy:
                sock = self._socks5_connect(self.api_host, 443)
            else:
                sock = self._direct_connect(self.api_host, 443)

            context = ssl.create_default_context()
            with context.wrap_socket(sock, server_hostname=self.api_host) as ssock:
                ssock.sendall(request.encode())
                response = b""
                while True:
                    chunk = ssock.recv(4096)
                    if not chunk:
                        break
                    response += chunk

            text = response.decode("utf-8", errors="ignore")
            if "\\r\\n\\r\\n" in text:
                _, body = text.split("\\r\\n\\r\\n", 1)
            else:
                body = text

            for line in body.split("\\r\\n"):
                line = line.strip()
                if line.startswith("{"):
                    return json.loads(line)

            if body.strip().startswith("{"):
                return json.loads(body.strip())

            return {"ok": False, "raw": body[:200]}

        except Exception as e:
            logger.error(f"Telegram request failed: {e}")
            return {"ok": False, "error": str(e)}

    def send_message(self, text: str, chat_id: str = None) -> dict:
        """Send a text message"""
        return self._request("sendMessage", {
            "chat_id": chat_id or self.chat_id,
            "text": text,
            "parse_mode": "HTML"
        })

    def send_alert(self, level: str, message: str) -> dict:
        """Send formatted alert"""
        emojis = {"INFO": "ℹ️", "WARNING": "⚠️", "CRITICAL": "🚨", "SUCCESS": "✅"}
        emoji = emojis.get(level.upper(), "📌")
        text = f"{emoji} <b>{level.upper()}</b>\\n{message}"
        return self.send_message(text)

    def test_connection(self) -> bool:
        """Test if bot can connect"""
        result = self._request("getMe")
        return result.get("ok", False)


_bot_instance = None

def get_bot() -> TelegramBot:
    global _bot_instance
    if _bot_instance is None:
        _bot_instance = TelegramBot()
    return _bot_instance

def send_telegram(message: str, level: str = "INFO") -> bool:
    """Quick send function"""
    bot = get_bot()
    result = bot.send_alert(level, message)
    return result.get("ok", False)
''',

# ═══════════════════════════════════════════════════════════════
# پایان بخش ۱ از ۲
# ═══════════════════════════════════════════════════════════════
# ═══════════════════════════════════════════════════════════════
# شروع بخش ۲ از ۲
# ═══════════════════════════════════════════════════════════════

# ─────────────────────────────────────────────────────────────
# FILE 3: main.py (Full Test + Telegram Integration)
# ─────────────────────────────────────────────────────────────
"main.py": '''"""
OCEAN HUNTER — Main Entry Point
Tests MEXC API + Telegram Notification
"""

import sys
import os
from datetime import datetime

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def main():
    print("=" * 60)
    print("🌊 OCEAN HUNTER V10.8.2 — System Test")
    print(f"⏰ {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)

    results = []

    # === TEST 1: MEXC Connection ===
    print("\\n[1/5] Testing MEXC Connection...")
    try:
        from modules.network.mexc_api import get_client
        client = get_client()

        # Ping
        ping = client.ping()
        if "error" not in ping:
            print("   ✅ Ping: OK")
            results.append("MEXC Ping: ✅")
        else:
            print(f"   ❌ Ping Failed: {ping}")
            results.append("MEXC Ping: ❌")

    except Exception as e:
        print(f"   ❌ MEXC Import Error: {e}")
        results.append(f"MEXC: ❌ {e}")

    # === TEST 2: Server Time ===
    print("\\n[2/5] Getting Server Time...")
    try:
        time_resp = client.get_server_time()
        if "serverTime" in time_resp:
            st = time_resp["serverTime"]
            print(f"   ✅ Server Time: {st}")
            results.append("Server Time: ✅")
        else:
            print(f"   ⚠️ Response: {time_resp}")
            results.append("Server Time: ⚠️")
    except Exception as e:
        print(f"   ❌ Error: {e}")
        results.append(f"Server Time: ❌")

    # === TEST 3: BTC Price ===
    print("\\n[3/5] Getting BTC Price...")
    try:
        price = client.get_ticker_price("BTCUSDT")
        if "price" in price:
            p = price["price"]
            print(f"   ✅ BTCUSDT: ${p}")
            results.append(f"BTC Price: ${p}")
        else:
            print(f"   ⚠️ Response: {price}")
            results.append("BTC Price: ⚠️")
    except Exception as e:
        print(f"   ❌ Error: {e}")
        results.append("BTC Price: ❌")

    # === TEST 4: Account Auth ===
    print("\\n[4/5] Testing Authentication...")
    try:
        account = client.get_account()
        if "balances" in account:
            count = len(account["balances"])
            print(f"   ✅ Auth Success! Found {count} assets")
            results.append(f"Auth: ✅ ({count} assets)")

            # Show non-zero balances
            for b in account["balances"][:5]:
                free = float(b.get("free", 0))
                locked = float(b.get("locked", 0))
                if free > 0 or locked > 0:
                    print(f"      💰 {b['asset']}: {free} (locked: {locked})")

        elif "error" in account:
            print(f"   ❌ Auth Failed: {account['error']}")
            results.append(f"Auth: ❌ {account.get('error', 'Unknown')}")
        elif "code" in account:
            print(f"   ❌ API Error {account.get('code')}: {account.get('msg')}")
            results.append(f"Auth: ❌ Code {account.get('code')}")
        else:
            print(f"   ⚠️ Unexpected: {account}")
            results.append("Auth: ⚠️")
    except Exception as e:
        print(f"   ❌ Error: {e}")
        results.append(f"Auth: ❌ {e}")

    # === TEST 5: Telegram ===
    print("\\n[5/5] Testing Telegram...")
    try:
        from modules.network.telegram_bot import get_bot
        bot = get_bot()

        # First test connection
        if bot.test_connection():
            print("   ✅ Bot Connected")

            # Send report
            report = "🌊 <b>OCEAN HUNTER Test Report</b>\\n\\n"
            report += "\\n".join(results)
            report += f"\\n\\n⏰ {datetime.now().strftime('%H:%M:%S')}"

            send_result = bot.send_message(report)
            if send_result.get("ok"):
                print("   ✅ Telegram Message Sent!")
                results.append("Telegram: ✅")
            else:
                print(f"   ⚠️ Send Failed: {send_result}")
                results.append("Telegram: ⚠️")
        else:
            print("   ❌ Bot Connection Failed")
            results.append("Telegram: ❌")

    except Exception as e:
        print(f"   ❌ Telegram Error: {e}")
        results.append(f"Telegram: ❌ {e}")

    # === SUMMARY ===
    print("\\n" + "=" * 60)
    print("📊 TEST SUMMARY")
    print("=" * 60)
    for r in results:
        print(f"   {r}")
    print("=" * 60)

    return 0

if __name__ == "__main__":
    sys.exit(main())
''',

}  # End of MODIFY_FILES

# ═══════════════════════════════════════════════════════════════
# HELPER FUNCTIONS
# ═══════════════════════════════════════════════════════════════

def check_internet():
    """Check internet connectivity"""
    try:
        socket.create_connection(("8.8.8.8", 53), timeout=5)
        return True
    except OSError:
        return False

def run_cmd(cmd, desc, critical=False):
    """Run subprocess command"""
    try:
        result = subprocess.run(
            cmd, capture_output=True, text=True, timeout=120,
            cwd=ROOT, shell=isinstance(cmd, str)
        )
        if result.returncode == 0:
            print(f"      ✅ {desc}")
            return True, result.stdout
        else:
            print(f"      ❌ {desc}: {result.stderr[:100]}")
            if critical:
                log_error(desc, result.stderr)
            return False, result.stderr
    except Exception as e:
        print(f"      ❌ {desc}: {e}")
        if critical:
            log_error(desc, str(e))
        return False, str(e)

# ═══════════════════════════════════════════════════════════════
# BUILD STEPS
# ═══════════════════════════════════════════════════════════════

def step1_system_check():
    """Step 1: System checks"""
    print("\n" + "═" * 60)
    print("📍 STEP 1/9: System Checks")
    print("═" * 60)

    # Python version
    ver = sys.version_info
    print(f"   🐍 Python: {ver.major}.{ver.minor}.{ver.micro}")
    if ver.major < 3 or ver.minor < 10:
        log_error("Python", "Requires Python 3.10+")
        return False

    # Internet
    print("   🌐 Checking Internet...")
    if check_internet():
        print("      ✅ Internet OK")
    else:
        print("      ⚠️ No Internet (continuing offline)")

    return True

def step2_venv():
    """Step 2: Setup venv"""
    print("\n" + "═" * 60)
    print("📍 STEP 2/9: Virtual Environment")
    print("═" * 60)

    if os.path.exists(VENV_PATH):
        print(f"   ✅ venv exists: {VENV_PATH}")
        return True

    print("   🔧 Creating venv...")
    success, _ = run_cmd([sys.executable, "-m", "venv", VENV_PATH], "Create venv", critical=True)
    return success

def step3_dependencies():
    """Step 3: Install dependencies"""
    print("\n" + "═" * 60)
    print("📍 STEP 3/9: Dependencies")
    print("═" * 60)

    req_file = os.path.join(ROOT, "requirements.txt")
    if not os.path.exists(req_file):
        print("   ⚠️ No requirements.txt, skipping")
        return True

    print("   📦 Installing packages...")
    success, _ = run_cmd([VENV_PYTHON, "-m", "pip", "install", "-r", req_file, "-q"], "pip install")
    return success

def step4_folders():
    """Step 4: Create folders"""
    print("\n" + "═" * 60)
    print("📍 STEP 4/9: Folders")
    print("═" * 60)

    for folder in FOLDERS:
        path = os.path.join(ROOT, folder)
        if not os.path.exists(path):
            os.makedirs(path, exist_ok=True)
            print(f"   📁 Created: {folder}")
        else:
            print(f"   ✅ Exists: {folder}")

    # Ensure modules/network exists for our files
    network_path = os.path.join(ROOT, "modules", "network")
    os.makedirs(network_path, exist_ok=True)
    print(f"   📁 Ensured: modules/network")

    return True

def step5_files():
    """Step 5: Create/Modify files"""
    print("\n" + "═" * 60)
    print("📍 STEP 5/9: Files (Create/Modify)")
    print("═" * 60)

    # New files
    for rel_path, content in NEW_FILES.items():
        full_path = os.path.join(ROOT, rel_path)
        os.makedirs(os.path.dirname(full_path), exist_ok=True)
        with open(full_path, "w", encoding="utf-8") as f:
            f.write(content)
        print(f"   📄 Created: {rel_path}")

    # Modified files (MEXC, Telegram, main)
    for rel_path, content in MODIFY_FILES.items():
        full_path = os.path.join(ROOT, rel_path)
        os.makedirs(os.path.dirname(full_path), exist_ok=True)
        with open(full_path, "w", encoding="utf-8") as f:
            f.write(content)
        print(f"   ✏️ Modified: {rel_path}")

    return True

def step6_context():
    """Step 6: Generate context"""
    print("\n" + "═" * 60)
    print("📍 STEP 6/9: Context Generation")
    print("═" * 60)

    try:
        sys.path.insert(0, SCRIPT_DIR)
        import context_gen
        context_gen.create_context_file()
        print("   ✅ Context generated")
        return True
    except Exception as e:
        print(f"   ⚠️ Context generation failed: {e}")
        log_error("Context", str(e))
        return True  # Non-critical

def step7_git_init():
    """Step 7: Git init (if needed)"""
    print("\n" + "═" * 60)
    print("📍 STEP 7/9: Git Init")
    print("═" * 60)

    git_dir = os.path.join(ROOT, ".git")
    if os.path.exists(git_dir):
        print("   ✅ Git already initialized")
        return True

    try:
        import setup_git
        setup_git.setup()
        print("   ✅ Git initialized")
        return True
    except Exception as e:
        print(f"   ⚠️ Git init failed: {e}")
        return True  # Non-critical

def step8_git_sync():
    """Step 8: Git sync"""
    print("\n" + "═" * 60)
    print("📍 STEP 8/9: Git Sync")
    print("═" * 60)

    try:
        sys.path.insert(0, SCRIPT_DIR)
        import setup_git
        setup_git.sync()
        print("   ✅ Git synced")
        return True
    except Exception as e:
        print(f"   ⚠️ Git sync failed: {e}")
        return True  # Non-critical

def step9_launch():
    """Step 9: Launch main"""
    print("\n" + "═" * 60)
    print("📍 STEP 9/9: Launch Application")
    print("═" * 60)

    main_path = os.path.join(ROOT, MAIN_FILE)
    if not os.path.exists(main_path):
        print(f"   ❌ {MAIN_FILE} not found")
        return False

    print(f"   🚀 Launching {MAIN_FILE}...")
    print("─" * 60)

    # Run main.py
    result = subprocess.run([VENV_PYTHON, main_path], cwd=ROOT)
    return result.returncode == 0

# ═══════════════════════════════════════════════════════════════
# MAIN EXECUTION
# ═══════════════════════════════════════════════════════════════

def main():
    print("╔" + "═" * 58 + "╗")
    print("║" + "🔨 OCEAN HUNTER BUILD SYSTEM".center(58) + "║")
    print("║" + "MEXC Auth Fix + Telegram SOCKS5".center(58) + "║")
    print("║" + f"📅 {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}".center(58) + "║")
    print("╚" + "═" * 58 + "╝")

    steps = [
        ("System Check", step1_system_check),
        ("Virtual Env", step2_venv),
        ("Dependencies", step3_dependencies),
        ("Folders", step4_folders),
        ("Files", step5_files),
        ("Context", step6_context),
        ("Git Init", step7_git_init),
        ("Git Sync", step8_git_sync),
        ("Launch", step9_launch),
    ]

    for name, func in steps:
        try:
            if not func():
                print(f"\n⚠️ Step '{name}' had issues but continuing...")
        except Exception as e:
            log_error(name, str(e))
            print(f"\n❌ Step '{name}' failed: {e}")

    # Summary
    print("\n" + "═" * 60)
    print("📦 BUILD SUMMARY")
    print("═" * 60)

    if errors:
        print("❌ Errors Encountered:")
        for e in errors:
            print(f"   - {e}")
        print("\n⛔ Build completed with errors.")
        exit_code = 1
    else:
        print("✅ Build completed successfully.")
        exit_code = 0

    print("═" * 60)
    print(f"🏁 Exit Code: {exit_code}")
    print("═" * 60)

    sys.exit(exit_code)

# ═══════════════════════════════════════════════════════════════
# ENTRY POINT
# ═══════════════════════════════════════════════════════════════

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n⛔ Interrupted by user")
        sys.exit(130)
    except Exception as fatal:
        print(f"\n🔥 Fatal Error: {fatal}")
        sys.exit(2)

# ═══════════════════════════════════════════════════════════════
# پایان بخش ۲ از ۲
# ═══════════════════════════════════════════════════════════════

