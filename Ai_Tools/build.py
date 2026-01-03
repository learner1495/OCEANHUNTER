#!/usr/bin/env python3
# AI_Tools/build.py
# OCEAN HUNTER V10.8.2 — MEXC Edition
# Auto-generated build script — DO NOT EDIT MANUALLY
# Reference: MEXC-BUILD-001

import os
import sys
import subprocess
import socket
from datetime import datetime

# ══════════════════════════════════════════════════════════════════════════════
# PATH SETUP
# ══════════════════════════════════════════════════════════════════════════════
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(SCRIPT_DIR)
sys.path.insert(0, SCRIPT_DIR)

# ══════════════════════════════════════════════════════════════════════════════
# LOGGING
# ══════════════════════════════════════════════════════════════════════════════
ERRORS, WARNINGS = [], []

def log(level, section, msg):
    ts = datetime.now().strftime("%H:%M:%S")
    print(f"[{ts}] [{level}] [{section}] {msg}")
    if level == "ERROR": ERRORS.append(f"{section}: {msg}")
    if level == "WARN": WARNINGS.append(f"{section}: {msg}")

def log_info(s, m): log("INFO", s, m)
def log_warn(s, m): log("WARN", s, m)
def log_error(s, m): log("ERROR", s, m)

# ══════════════════════════════════════════════════════════════════════════════
# SUBPROCESS RUNNER
# ══════════════════════════════════════════════════════════════════════════════
def run_cmd(cmd, desc, critical=False, timeout=120):
    log_info("CMD", f"{desc}...")
    try:
        r = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout, cwd=PROJECT_ROOT)
        if r.returncode == 0:
            log_info("CMD", f"✅ {desc}")
            return True, r.stdout
        else:
            log_error("CMD", f"❌ {desc}: {r.stderr[:200]}")
            if critical: sys.exit(1)
            return False, r.stderr
    except subprocess.TimeoutExpired:
        log_error("CMD", f"⏱️ Timeout: {desc}")
        return False, "Timeout"
    except Exception as e:
        log_error("CMD", f"💥 {desc}: {e}")
        return False, str(e)

# ══════════════════════════════════════════════════════════════════════════════
# SYSTEM CHECKS
# ══════════════════════════════════════════════════════════════════════════════
def check_internet():
    log_info("NET", "Checking internet...")
    try:
        socket.create_connection(("8.8.8.8", 53), timeout=5)
        log_info("NET", "✅ Internet OK")
        return True
    except OSError:
        log_warn("NET", "⚠️ No internet")
        return False

def check_dns():
    log_info("DNS", "Checking DNS...")
    try:
        socket.gethostbyname("github.com")
        log_info("DNS", "✅ DNS OK")
        return True
    except socket.gaierror:
        log_warn("DNS", "⚠️ DNS failed")
        return False

def check_python():
    v = sys.version_info
    log_info("PY", f"Python {v.major}.{v.minor}.{v.micro}")
    if v.major >= 3 and v.minor >= 10:
        log_info("PY", "✅ Version OK")
        return True
    log_error("PY", "❌ Need Python 3.10+")
    return False
# ══════════════════════════════════════════════════════════════════════════════
# FILE CONTENTS
# ══════════════════════════════════════════════════════════════════════════════

MEXC_API_CONTENT = '''import socket
import ssl
import hmac
import hashlib
import time
import json
import logging
import os
from dotenv import load_dotenv

load_dotenv()
logger = logging.getLogger("MEXC_API")

class MexcAPI:
    HOST = "api.mexc.com"
    PORT = 443
    TIMEOUT = 30
    
    def __init__(self):
        self.api_key = os.getenv("MEXC_API_KEY", "")
        self.secret = os.getenv("MEXC_SECRET", "")
        self.ctx = ssl.create_default_context()
    
    def _request(self, method, path, params=None, auth=False):
        try:
            query = "&".join(f"{k}={v}" for k, v in (params or {}).items())
            if auth:
                ts = int(time.time() * 1000)
                query = f"{query}&timestamp={ts}" if query else f"timestamp={ts}"
                sig = hmac.new(self.secret.encode(), query.encode(), hashlib.sha256).hexdigest()
                query = f"{query}&signature={sig}"
            
            full_path = f"{path}?{query}" if query else path
            sock = socket.create_connection((self.HOST, self.PORT), timeout=self.TIMEOUT)
            ssl_sock = self.ctx.wrap_socket(sock, server_hostname=self.HOST)
            
            headers = f"Host: {self.HOST}\\r\\nConnection: close\\r\\n"
            if auth: headers += f"X-MEXC-APIKEY: {self.api_key}\\r\\n"
            headers += "Content-Type: application/json\\r\\n"
            
            request = f"{method} {full_path} HTTP/1.1\\r\\n{headers}\\r\\n"
            ssl_sock.sendall(request.encode())
            
            response = b""
            while True:
                try:
                    data = ssl_sock.recv(8192)
                    if not data: break
                    response += data
                except: break
            ssl_sock.close()
            
            parts = response.decode(errors="ignore").split("\\r\\n\\r\\n", 1)
            if len(parts) < 2: return {"error": "Empty response"}
            
            body = parts[1]
            if body.startswith("[") or body.startswith("{"): return json.loads(body)
            for line in body.split("\\r\\n"):
                line = line.strip()
                if line.startswith("[") or line.startswith("{"): return json.loads(line)
            return {"error": f"Cannot parse: {body[:100]}"}
        except socket.timeout: return {"error": "Connection timeout"}
        except ssl.SSLError as e: return {"error": f"SSL Error: {e}"}
        except json.JSONDecodeError as e: return {"error": f"JSON Error: {e}"}
        except Exception as e: return {"error": f"{type(e).__name__}: {e}"}
    
    def ping(self): return self._request("GET", "/api/v3/ping")
    
    def get_price(self, symbol):
        r = self._request("GET", "/api/v3/ticker/price", {"symbol": symbol})
        return float(r.get("price", 0)) if "error" not in r else None
    
    def get_prices(self, symbols=None):
        r = self._request("GET", "/api/v3/ticker/price")
        if "error" in r or not isinstance(r, list): return {}
        return {i["symbol"]: float(i.get("price", 0)) for i in r if symbols is None or i["symbol"] in symbols}
    
    def get_orderbook(self, symbol, limit=20):
        r = self._request("GET", "/api/v3/depth", {"symbol": symbol, "limit": limit})
        if "error" in r: return {"bids": [], "asks": []}
        return {"bids": [[float(p), float(q)] for p, q in r.get("bids", [])],
                "asks": [[float(p), float(q)] for p, q in r.get("asks", [])]}
    
    def get_klines(self, symbol, interval="15m", limit=100):
        r = self._request("GET", "/api/v3/klines", {"symbol": symbol, "interval": interval, "limit": limit})
        if "error" in r or not isinstance(r, list): return []
        return [[int(k[0]), float(k[1]), float(k[2]), float(k[3]), float(k[4]), float(k[5])] for k in r]
    
    def get_ticker_24h(self, symbol):
        return self._request("GET", "/api/v3/ticker/24hr", {"symbol": symbol})
    
    def get_balance(self):
        r = self._request("GET", "/api/v3/account", auth=True)
        if "error" in r: return {}
        return {b["asset"]: {"free": float(b.get("free", 0)), "locked": float(b.get("locked", 0)),
                "total": float(b.get("free", 0)) + float(b.get("locked", 0))}
                for b in r.get("balances", []) if float(b.get("free", 0)) + float(b.get("locked", 0)) > 0}
    
    def place_order(self, symbol, side, order_type, quantity, price=None):
        params = {"symbol": symbol, "side": side.upper(), "type": order_type.upper(), "quantity": quantity}
        if order_type.upper() == "LIMIT" and price: params["price"] = price
        return self._request("POST", "/api/v3/order", params, auth=True)
    
    def cancel_order(self, symbol, order_id):
        return self._request("DELETE", "/api/v3/order", {"symbol": symbol, "orderId": order_id}, auth=True)
    
    def get_open_orders(self, symbol=None):
        params = {"symbol": symbol} if symbol else {}
        return self._request("GET", "/api/v3/openOrders", params, auth=True)
    
    def get_order(self, symbol, order_id):
        return self._request("GET", "/api/v3/order", {"symbol": symbol, "orderId": order_id}, auth=True)
    
    def get_ohlcv(self, symbol, resolution="15", from_ts=None, to_ts=None):
        interval_map = {"1": "1m", "5": "5m", "15": "15m", "30": "30m", "60": "1h", "240": "4h", "D": "1d", "1D": "1d"}
        klines = self.get_klines(symbol, interval_map.get(resolution, "15m"), 100)
        if not klines: return {"s": "error", "msg": "No data"}
        return {"s": "ok", "t": [k[0]//1000 for k in klines], "o": [k[1] for k in klines],
                "h": [k[2] for k in klines], "l": [k[3] for k in klines],
                "c": [k[4] for k in klines], "v": [k[5] for k in klines]}
    
    def calculate_obi(self, symbol, depth=20):
        ob = self.get_orderbook(symbol, depth)
        if not ob["bids"] or not ob["asks"]: return 0
        bid_vol, ask_vol = sum(b[1] for b in ob["bids"]), sum(a[1] for a in ob["asks"])
        return (bid_vol - ask_vol) / (bid_vol + ask_vol) if (bid_vol + ask_vol) > 0 else 0
'''

NETWORK_INIT_CONTENT = '''from .mexc_api import MexcAPI

_client_instance = None

def get_client():
    global _client_instance
    if _client_instance is None:
        _client_instance = MexcAPI()
    return _client_instance
'''

ENV_TEMPLATE = '''# OCEAN HUNTER V10.8.2 — MEXC Edition
# Exchange
MEXC_API_KEY=mx0vglgT1sDiSHvzkz
MEXC_SECRET=5a9e39d83a7043d19dcbf41d7880eb1a

# Telegram
TELEGRAM_BOT_TOKEN=
TELEGRAM_CHAT_ID=

# Mode: PAPER | LIVE_TEST | LIVE_FULL
TRADING_MODE=PAPER
'''
# ══════════════════════════════════════════════════════════════════════════════
# STEP 1: SYSTEM CHECKS
# ══════════════════════════════════════════════════════════════════════════════
def step1_system_checks():
    print("\n" + "="*60)
    print("STEP 1: SYSTEM CHECKS")
    print("="*60)
    
    py_ok = check_python()
    net_ok = check_internet()
    dns_ok = check_dns()
    
    return py_ok  # Network optional

# ══════════════════════════════════════════════════════════════════════════════
# STEP 2: VENV SETUP
# ══════════════════════════════════════════════════════════════════════════════
def step2_venv_setup():
    print("\n" + "="*60)
    print("STEP 2: VENV SETUP")
    print("="*60)
    
    venv_path = os.path.join(PROJECT_ROOT, ".venv")
    if os.path.exists(venv_path):
        log_info("VENV", "✅ .venv already exists")
        return True
    
    log_info("VENV", "Creating virtual environment...")
    ok, _ = run_cmd([sys.executable, "-m", "venv", venv_path], "Create .venv", critical=True)
    return ok

# ══════════════════════════════════════════════════════════════════════════════
# STEP 3: PIP INSTALL
# ══════════════════════════════════════════════════════════════════════════════
def get_venv_python():
    if sys.platform == "win32":
        return os.path.join(PROJECT_ROOT, ".venv", "Scripts", "python.exe")
    return os.path.join(PROJECT_ROOT, ".venv", "bin", "python")

def step3_pip_install():
    print("\n" + "="*60)
    print("STEP 3: PIP INSTALL")
    print("="*60)
    
    req_file = os.path.join(PROJECT_ROOT, "requirements.txt")
    if not os.path.exists(req_file):
        log_warn("PIP", "requirements.txt not found, skipping")
        return True
    
    vpy = get_venv_python()
    run_cmd([vpy, "-m", "pip", "install", "--upgrade", "pip"], "Upgrade pip", timeout=120)
    ok, _ = run_cmd([vpy, "-m", "pip", "install", "-r", req_file], "Install requirements", timeout=300)
    return ok

# ══════════════════════════════════════════════════════════════════════════════
# STEP 4: FOLDER CREATION
# ══════════════════════════════════════════════════════════════════════════════
def step4_create_folders():
    print("\n" + "="*60)
    print("STEP 4: FOLDER CREATION")
    print("="*60)
    
    folders = [
        "modules/network",
        "modules/analysis",
        "modules/security",
        "modules/trading",
        "modules/watchdog",
        "data/state",
        "data/logs",
        "data/trades",
        "AI_Tools/context_backups"
    ]
    
    for folder in folders:
        path = os.path.join(PROJECT_ROOT, folder)
        os.makedirs(path, exist_ok=True)
        log_info("DIR", f"✅ {folder}")
    
    return True

# ══════════════════════════════════════════════════════════════════════════════
# STEP 5: FILE CREATION
# ══════════════════════════════════════════════════════════════════════════════
def write_file(rel_path, content):
    full_path = os.path.join(PROJECT_ROOT, rel_path)
    os.makedirs(os.path.dirname(full_path), exist_ok=True)
    with open(full_path, "w", encoding="utf-8") as f:
        f.write(content)
    log_info("FILE", f"✅ {rel_path}")

def step5_create_files():
    print("\n" + "="*60)
    print("STEP 5: FILE CREATION")
    print("="*60)
    
    # Main MEXC API Module
    write_file("modules/network/mexc_api.py", MEXC_API_CONTENT)
    
    # Network __init__.py (Updated for MEXC)
    write_file("modules/network/__init__.py", NETWORK_INIT_CONTENT)
    
    # .env template (if not exists)
    env_path = os.path.join(PROJECT_ROOT, ".env")
    if not os.path.exists(env_path):
        write_file(".env", ENV_TEMPLATE)
        log_info("FILE", "⚠️ .env created — UPDATE TELEGRAM CREDENTIALS!")
    else:
        log_info("FILE", "ℹ️ .env exists, skipping")
    
    # Module __init__ files
    for mod in ["analysis", "security", "trading", "watchdog"]:
        init_path = f"modules/{mod}/__init__.py"
        full = os.path.join(PROJECT_ROOT, init_path)
        if not os.path.exists(full):
            write_file(init_path, f"# {mod.title()} Module\n")
    
    return True

# ══════════════════════════════════════════════════════════════════════════════
# STEP 6: CONTEXT GENERATION
# ══════════════════════════════════════════════════════════════════════════════
def step6_context_gen():
    print("\n" + "="*60)
    print("STEP 6: CONTEXT GENERATION")
    print("="*60)
    
    try:
        import context_gen
        context_gen.create_context_file()
        log_info("CTX", "✅ Context file updated")
        return True
    except Exception as e:
        log_error("CTX", f"Failed: {e}")
        return False

# ══════════════════════════════════════════════════════════════════════════════
# STEP 7 & 8: GIT OPERATIONS
# ══════════════════════════════════════════════════════════════════════════════
def step7_git_init():
    print("\n" + "="*60)
    print("STEP 7: GIT INIT")
    print("="*60)
    
    git_dir = os.path.join(PROJECT_ROOT, ".git")
    if os.path.exists(git_dir):
        log_info("GIT", "✅ .git already exists")
        return True
    
    try:
        import setup_git
        setup_git.setup()
        log_info("GIT", "✅ Git initialized")
        return True
    except Exception as e:
        log_warn("GIT", f"Init failed: {e}")
        return False

def step8_git_sync():
    print("\n" + "="*60)
    print("STEP 8: GIT SYNC")
    print("="*60)
    
    if not check_internet():
        log_warn("GIT", "⚠️ No internet, skipping sync")
        return False
    
    try:
        import setup_git
        setup_git.sync()
        log_info("GIT", "✅ Git synced")
        return True
    except Exception as e:
        log_warn("GIT", f"Sync failed: {e}")
        return False

# ══════════════════════════════════════════════════════════════════════════════
# STEP 9: APP LAUNCH
# ══════════════════════════════════════════════════════════════════════════════
def step9_launch_app():
    print("\n" + "="*60)
    print("STEP 9: APP LAUNCH")
    print("="*60)
    
    main_py = os.path.join(PROJECT_ROOT, "main.py")
    if not os.path.exists(main_py):
        log_warn("APP", "main.py not found, skipping launch")
        return False
    
    vpy = get_venv_python()
    log_info("APP", "🚀 Launching main.py...")
    
    try:
        subprocess.run([vpy, main_py], cwd=PROJECT_ROOT)
        return True
    except KeyboardInterrupt:
        log_info("APP", "⏹️ Stopped by user")
        return True
    except Exception as e:
        log_error("APP", f"Launch failed: {e}")
        return False

# ══════════════════════════════════════════════════════════════════════════════
# MAIN EXECUTION
# ══════════════════════════════════════════════════════════════════════════════
def print_banner():
    print("""
╔══════════════════════════════════════════════════════════════╗
║           OCEAN HUNTER V10.8.2 — MEXC EDITION                ║
║                    BUILD AUTOMATION                          ║
║                                                              ║
║  Exchange: MEXC Global | Driver: Raw Socket + TLS 1.3       ║
╚══════════════════════════════════════════════════════════════╝
    """)

def print_summary():
    print("\n" + "="*60)
    print("BUILD SUMMARY")
    print("="*60)
    
    if ERRORS:
        print("\n❌ ERRORS:")
        for e in ERRORS: print(f"   • {e}")
    
    if WARNINGS:
        print("\n⚠️ WARNINGS:")
        for w in WARNINGS: print(f"   • {w}")
    
    if not ERRORS and not WARNINGS:
        print("\n✅ All operations completed successfully!")
    
    print("\n" + "="*60)

def main():
    print_banner()
    
    try:
        # Execute all steps in locked order
        if not step1_system_checks():
            log_error("MAIN", "System checks failed")
            return 1
        
        step2_venv_setup()
        step3_pip_install()
        step4_create_folders()
        step5_create_files()
        step6_context_gen()
        step7_git_init()
        step8_git_sync()
        step9_launch_app()
        
        print_summary()
        return 0 if not ERRORS else 1
        
    except KeyboardInterrupt:
        print("\n\n⏹️ Build cancelled by user")
        return 2
    except Exception as e:
        log_error("MAIN", f"Unexpected error: {e}")
        print_summary()
        return 2

if __name__ == "__main__":
    sys.exit(main())
