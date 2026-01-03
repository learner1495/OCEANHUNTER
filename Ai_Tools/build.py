#!/usr/bin/env python3
"""
═══════════════════════════════════════════════════════════════════════════════
                    OCEAN HUNTER V10.8.2 — BUILD SCRIPT
                         MEXC EDITION — Full Migration
                              Reference: BUILD-MEXC-068
═══════════════════════════════════════════════════════════════════════════════
"""
import os, sys, subprocess, socket
from datetime import datetime
import context_gen, setup_git

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(SCRIPT_DIR)
VENV_PATH = os.path.join(ROOT, ".venv")
VENV_PYTHON = os.path.join(VENV_PATH, "Scripts", "python.exe") if sys.platform == "win32" else os.path.join(VENV_PATH, "bin", "python")

FOLDERS = ["modules", "modules/network", "modules/strategy", "modules/telegram", "data", "logs", "backups"]

NEW_FILES = {

"config.py": '''#!/usr/bin/env python3
"""Ocean Hunter Configuration — MEXC Edition"""
import os
from pathlib import Path
from dotenv import load_dotenv

PROJECT_ROOT = Path(__file__).parent
load_dotenv(PROJECT_ROOT / ".env")

ACTIVE_EXCHANGE = "MEXC"
MEXC_API_KEY = os.getenv("MEXC_API_KEY", "")
MEXC_SECRET_KEY = os.getenv("MEXC_SECRET_KEY", "")
MEXC_BASE_URL = "https://api.mexc.com"
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID", "")
TRADE_COINS = ["BTC", "ETH", "SOL", "XRP", "DOGE"]
QUOTE_CURRENCY = "USDT"
ENTRY_SCORE_MIN = 70
RSI_PERIOD, RSI_OVERSOLD, BB_PERIOD = 14, 35, 20
VOLUME_SMA_PERIOD, VOLUME_SPIKE_MULT = 20, 1.5
TAKE_PROFIT_MIN, TAKE_PROFIT_MAX = 1.5, 3.0
TRAILING_STOP_TRIGGER, TRAILING_STOP_DISTANCE = 1.0, 0.5
MAX_POSITIONS, MIN_ORDER_USDT, RATE_LIMIT_DELAY = 3, 15, 0.5
MODE = os.getenv("MODE", "PAPER")
''',

"modules/__init__.py": '# Ocean Hunter Modules\n',

"modules/network/__init__.py": '''from .mexc_api import MEXCClient
from .telegram_bot import TelegramBot

def get_client():
    return MEXCClient()
''',

"modules/network/mexc_api.py": '''#!/usr/bin/env python3
"""MEXC API Client — Raw Socket Edition"""
import socket, ssl, json, hmac, hashlib, time, os
from urllib.parse import urlencode
from dotenv import load_dotenv
load_dotenv()

class MEXCClient:
    HOST, PORT = "api.mexc.com", 443
    
    def __init__(self):
        self.api_key = os.getenv("MEXC_API_KEY", "")
        self.secret_key = os.getenv("MEXC_SECRET_KEY", "")
        self._ctx = ssl.create_default_context()
    
    def _request(self, method, endpoint, params=None, auth=False):
        params = params or {}
        if auth:
            params["timestamp"] = int(time.time() * 1000)
            qs = urlencode(sorted(params.items()))
            params["signature"] = hmac.new(self.secret_key.encode(), qs.encode(), hashlib.sha256).hexdigest()
        query = urlencode(params) if params else ""
        path = f"/api/v3{endpoint}" + (f"?{query}" if query and method == "GET" else "")
        headers = [f"{method} {path} HTTP/1.1", f"Host: {self.HOST}", "Accept: application/json",
                   "Content-Type: application/x-www-form-urlencoded", "Connection: close"]
        if self.api_key:
            headers.append(f"X-MEXC-APIKEY: {self.api_key}")
        body = query if method == "POST" else ""
        if body:
            headers.append(f"Content-Length: {len(body)}")
        request = "\\r\\n".join(headers) + "\\r\\n\\r\\n" + body
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(20)
            wrapped = self._ctx.wrap_socket(sock, server_hostname=self.HOST)
            wrapped.connect((self.HOST, self.PORT))
            wrapped.sendall(request.encode())
            response = b""
            while True:
                chunk = wrapped.recv(4096)
                if not chunk:
                    break
                response += chunk
            wrapped.close()
            parts = response.split(b"\\r\\n\\r\\n", 1)
            if len(parts) == 2:
                hdr, body = parts
                if b"Transfer-Encoding: chunked" in hdr:
                    body = self._decode_chunked(body)
                return json.loads(body.decode())
            return {"error": "Invalid response"}
        except socket.timeout:
            return {"error": "Timeout"}
        except ssl.SSLError as e:
            return {"error": f"SSL: {e}"}
        except Exception as e:
            return {"error": str(e)}
    
    def _decode_chunked(self, data):
        result = b""
        while data:
            end = data.find(b"\\r\\n")
            if end == -1:
                break
            try:
                size = int(data[:end].decode().strip(), 16)
            except:
                break
            if size == 0:
                break
            result += data[end+2:end+2+size]
            data = data[end+4+size:]
        return result
    
    def ping(self):
        return self._request("GET", "/ping")
    
    def get_time(self):
        return self._request("GET", "/time")
    
    def get_price(self, symbol):
        r = self._request("GET", "/ticker/price", {"symbol": symbol})
        return float(r.get("price", 0)) if "error" not in r else 0.0
    
    def get_prices(self, symbols=None):
        r = self._request("GET", "/ticker/price")
        if not isinstance(r, list):
            return {}
        prices = {i["symbol"]: float(i["price"]) for i in r}
        return {s: prices.get(s, 0) for s in symbols} if symbols else prices
    
    def get_orderbook(self, symbol, limit=20):
        r = self._request("GET", "/depth", {"symbol": symbol, "limit": limit})
        if "error" in r:
            return {"bids": [], "asks": []}
        return {"bids": [[float(p), float(q)] for p, q in r.get("bids", [])],
                "asks": [[float(p), float(q)] for p, q in r.get("asks", [])]}
    
    def get_klines(self, symbol, interval="1h", limit=100):
        r = self._request("GET", "/klines", {"symbol": symbol, "interval": interval, "limit": limit})
        if not isinstance(r, list):
            return []
        return [{"time": k[0], "open": float(k[1]), "high": float(k[2]), "low": float(k[3]),
                 "close": float(k[4]), "volume": float(k[5])} for k in r]
    
    def get_ticker_24h(self, symbol=None):
        params = {"symbol": symbol} if symbol else {}
        return self._request("GET", "/ticker/24hr", params)
    
    def get_account(self):
        return self._request("GET", "/account", auth=True)
    
    def get_balances(self):
        acc = self.get_account()
        if "balances" not in acc:
            return {}
        return {b["asset"]: {"free": float(b["free"]), "locked": float(b["locked"])}
                for b in acc["balances"] if float(b["free"]) > 0 or float(b["locked"]) > 0}
    
    def get_balance(self, asset):
        return self.get_balances().get(asset, {"free": 0, "locked": 0})
    
    def place_order(self, symbol, side, quantity, order_type="MARKET", price=None):
        params = {"symbol": symbol, "side": side.upper(), "type": order_type, "quantity": str(quantity)}
        if order_type == "LIMIT" and price:
            params["price"], params["timeInForce"] = str(price), "GTC"
        return self._request("POST", "/order", params, auth=True)
    
    def get_open_orders(self, symbol=None):
        params = {"symbol": symbol} if symbol else {}
        r = self._request("GET", "/openOrders", params, auth=True)
        return r if isinstance(r, list) else []
    
    def cancel_order(self, symbol, order_id):
        return self._request("DELETE", "/order", {"symbol": symbol, "orderId": order_id}, auth=True)
    
    def calculate_obi(self, symbol, depth=20):
        ob = self.get_orderbook(symbol, depth)
        if not ob["bids"] or not ob["asks"]:
            return 0
        bid_vol = sum(b[1] for b in ob["bids"])
        ask_vol = sum(a[1] for a in ob["asks"])
        total = bid_vol + ask_vol
        return (bid_vol - ask_vol) / total if total > 0 else 0
    
    def get_ohlcv(self, symbol, resolution="15", limit=100):
        interval_map = {"1": "1m", "5": "5m", "15": "15m", "30": "30m", "60": "1h", "240": "4h", "D": "1d"}
        klines = self.get_klines(symbol, interval_map.get(resolution, "15m"), limit)
        if not klines:
            return {"s": "error", "msg": "No data"}
        return {"s": "ok", "t": [k["time"]//1000 for k in klines],
                "o": [k["open"] for k in klines], "h": [k["high"] for k in klines],
                "l": [k["low"] for k in klines], "c": [k["close"] for k in klines],
                "v": [k["volume"] for k in klines]}

MexcAPI = MEXCClient
''',

"modules/network/telegram_bot.py": '''#!/usr/bin/env python3
"""Telegram Bot Stub"""
import os

class TelegramBot:
    def __init__(self):
        self.token = os.getenv("TELEGRAM_BOT_TOKEN", "")
        self.chat_id = os.getenv("TELEGRAM_CHAT_ID", "")
    
    def send(self, msg):
        print(f"[TG] {msg}")
        return True
''',

"modules/strategy/__init__.py": '# Strategy Module\n',

"modules/telegram/__init__.py": '# Telegram Module\n',
"main.py": '''#!/usr/bin/env python3
"""OCEAN HUNTER V10.8.2 — MEXC Edition"""
import sys
from datetime import datetime

def main():
    print("=" * 60)
    print("       🌊 OCEAN HUNTER V10.8.2 — MEXC Edition")
    print("=" * 60)
    print(f"   Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    try:
        from modules.network import get_client
        client = get_client()
        print("✅ MEXCClient loaded via get_client()")
    except ImportError as e:
        print(f"❌ Import Error: {e}")
        return 1
    print("\\n[TEST 1] Ping MEXC...")
    ping = client.ping()
    if "error" in ping:
        print(f"   ❌ Ping failed: {ping['error']}")
        return 1
    print("   ✅ Ping OK")
    print("\\n[TEST 2] Server Time...")
    st = client.get_time()
    if "serverTime" in st:
        print(f"   ✅ Server Time: {st['serverTime']}")
    else:
        print(f"   ⚠️ Response: {st}")
    print("\\n[TEST 3] BTC Price...")
    price = client.get_price("BTCUSDT")
    if price > 0:
        print(f"   ✅ BTCUSDT: ${price:,.2f}")
    else:
        print("   ⚠️ Could not get price")
    print("\\n[TEST 4] Authentication...")
    acc = client.get_account()
    if "error" not in acc and "balances" in acc:
        print("   ✅ Auth SUCCESS")
        usdt = client.get_balance("USDT")
        print(f"   💰 USDT Balance: {usdt['free']:.2f}")
    else:
        print(f"   ⚠️ Auth: {acc.get('error', acc.get('msg', 'Unknown'))}")
    print("\\n" + "=" * 60)
    print("   🌊 All tests completed — MEXC Ready")
    print("=" * 60)
    return 0

if __name__ == "__main__":
    sys.exit(main())
''',

}

MODIFY_FILES = {}
MAIN_FILE = "main.py"
errors = []

def log_error(step, error):
    errors.append(f"[{step}] {error}")
    print(f"      ⚠️ Error: {error}")

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
        subprocess.run([VENV_PYTHON, "-m", "pip", "install", "-r", req], capture_output=True, check=True)
        print("      ✅ Installed")
    except Exception as e:
        log_error("Step3", e)

def step4_folders():
    print("\n[4/9] 📁 Folders...")
    try:
        if not FOLDERS:
            print("      ℹ️ None defined")
            return
        for f in FOLDERS:
            path = os.path.join(ROOT, f)
            if not os.path.exists(path):
                os.makedirs(path)
                print(f"      ✅ Created: {f}/")
    except Exception as e:
        log_error("Step4", e)

def step5_new_files():
    print("\n[5/9] 📝 New Files...")
    try:
        if not NEW_FILES:
            print("      ℹ️ None defined")
            return
        for path, content in NEW_FILES.items():
            full = os.path.join(ROOT, path)
            parent = os.path.dirname(full)
            if parent and not os.path.exists(parent):
                os.makedirs(parent)
            with open(full, "w", encoding="utf-8") as f:
                f.write(content)
            print(f"      ✅ Created: {path}")
    except Exception as e:
        log_error("Step5", e)

def step6_modify():
    print("\n[6/9] ✏️ Modify Files...")
    try:
        if not MODIFY_FILES:
            print("      ℹ️ None defined")
            return
        for path, content in MODIFY_FILES.items():
            full = os.path.join(ROOT, path)
            with open(full, "w", encoding="utf-8") as f:
                f.write(content)
            print(f"      ✏️ Modified: {path}")
    except Exception as e:
        log_error("Step6", e)

# ═══════════════════════════════════════════════════════════════
# MAIN
# ═══════════════════════════════════════════════════════════════
def main():
    start_time = datetime.now()

    print("\n" + "═" * 60)
    print("🔧 OCEAN HUNTER V10.8.2 — BUILD MEXC EDITION")
    print(f"⏰ Started: {start_time.strftime('%Y-%m-%d %H:%M:%S')}")
    print("═" * 60)

    try:
        # ─── مراحل 1-6: Setup ───
        step1_system()
        step2_venv()
        step3_deps()
        step4_folders()
        step5_new_files()
        step6_modify()

        # ─── مرحله 7: Context ───
        print("\n[7/9] 📋 Context Generation...")
        try:
            context_gen.create_context_file()
            print("      ✅ Context created")
        except Exception as e:
            log_error("Step7-Context", e)

        # ─── مرحله 8: Git ───
        print("\n[8/9] 🐙 Git...")
        try:
            setup_git.setup()
            setup_git.sync(f"MEXC Migration: {start_time.strftime('%Y-%m-%d %H:%M')}")
            print("      ✅ Git synced")
        except Exception as e:
            log_error("Step8-Git", e)

        # ─── مرحله 9: Launch ───
        print("\n[9/9] 🚀 Launch...")
        try:
            main_path = os.path.join(ROOT, MAIN_FILE)
            if os.path.exists(main_path):
                print("─" * 60)
                subprocess.run([VENV_PYTHON, main_path], cwd=ROOT)
            else:
                print(f"      ℹ️ No {MAIN_FILE}")
        except Exception as e:
            log_error("Step9-Launch", e)

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
            print(f"⚠️ BUILD COMPLETED WITH {len(errors)} ERROR(S)")
            print("─" * 60)
            for err in errors:
                print(f"   • {err}")
        else:
            print("✅ BUILD COMPLETE — MEXC MIGRATION SUCCESSFUL")

        print("─" * 60)
        print(f"⏱️ Duration: {duration}s")
        print(f"🏁 Finished: {end_time.strftime('%H:%M:%S')}")
        print("═" * 60)

if __name__ == "__main__":
    main()
        