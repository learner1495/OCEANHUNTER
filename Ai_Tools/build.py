# ═══ PART 1 OF 1: build.py — Session 1 (Structure Setup) ═══

# AI_Tools/build.py — Template V3.4
# ═══════════════════════════════════════════════════════════════
# Session 1: ساخت ساختار پوشه‌ها و فایل‌های پایه
# ═══════════════════════════════════════════════════════════════

import os
import sys
import subprocess
import socket
from datetime import datetime

# ═══ Import ماژول‌های داخلی ═══
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
# ⭐ SESSION 1: STRUCTURE SETUP
# ═══════════════════════════════════════════════════════════════
FOLDERS = [
    "modules/core",
    "modules/network",
    "modules/analysis",
    "modules/trading",
    "modules/security",
    "modules/watchdog",
    "logs",
]

NEW_FILES = {
    # ─── Root Files ───
    "requirements.txt": """requests>=2.31.0
python-dotenv>=1.0.0
PySocks>=1.7.1
""",

    ".env": """# NOBITEX API
NOBITEX_API_KEY=your_api_key_here
NOBITEX_API_SECRET=your_api_secret_here

# TELEGRAM
TELEGRAM_BOT_TOKEN=your_bot_token_here
TELEGRAM_CHAT_ID=your_chat_id_here

# PROXY (for Telegram)
PROXY_HOST=127.0.0.1
PROXY_PORT=1080
""",

    "config.py": '''# config.py — OCEAN HUNTER V10.8.2
# ═══════════════════════════════════════════════════════════════

import os
from dotenv import load_dotenv

load_dotenv()

# ═══ API KEYS ═══
NOBITEX_API_KEY = os.getenv("NOBITEX_API_KEY", "")
NOBITEX_API_SECRET = os.getenv("NOBITEX_API_SECRET", "")
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID", "")

# ═══ PROXY ═══
PROXY_HOST = os.getenv("PROXY_HOST", "127.0.0.1")
PROXY_PORT = int(os.getenv("PROXY_PORT", 1080))

# ═══ TRADING PAIRS ═══
TRADE_COINS = ["SOL", "BNB", "XRP", "AVAX", "LINK"]
QUOTE_CURRENCY = "USDT"

# ═══ ALLOCATION (%) ═══
ALLOCATION = {
    "SOL": 25,
    "BNB": 20,
    "XRP": 15,
    "AVAX": 10,
    "LINK": 10,
    "USDT": 10,  # Reserve"BTC": 5,    # Growth Fund
    "PAXG": 5,   # Safe Haven
}

# ═══ STRATEGY PARAMS ═══
ENTRY_SCORE_MIN = 70
RSI_PERIOD = 14
RSI_OVERSOLD = 35
BB_PERIOD = 20
VOLUME_SMA_PERIOD = 20
VOLUME_SPIKE_MULT = 1.5

# ═══ EXIT PARAMS ═══
TAKE_PROFIT_MIN = 1.5  # %
TAKE_PROFIT_MAX = 3.0  # %
TRAILING_STOP_TRIGGER = 1.0  # %
TRAILING_STOP_DISTANCE = 0.5  # %

# ═══ DCA LAYERS ═══
DCA_LAYERS = {
    "L1": {"trigger": -3, "add": 50},
    "L2": {"trigger": -6, "add": 75},
    "L3": {"trigger": -10, "add": 100},
}

# ═══ LIMITS ═══
MAX_POSITIONS = 3
MIN_ORDER_USDT = 15  # 12 + buffer
RATE_LIMIT_DELAY = 2.5  # seconds

# ═══ NOBITEX API ═══
NOBITEX_BASE_URL = "https://api.nobitex.ir"
''',

    "state.json": """{
    "positions": {},
    "pending_queue": [],
    "last_heartbeat": null,
    "total_profit_usdt": 0,
    "btc_accumulated": 0,
    "paxg_accumulated": 0
}
""",

    "main.py": '''# main.py — OCEAN HUNTER V10.8.2
# ═══════════════════════════════════════════════════════════════

import time
from datetime import datetime

def main():
    print("=" * 50)
    print("🌊 OCEAN HUNTER V10.8.2")
    print(f"⏰ Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 50)
    print()
    print("✅ Structure Ready")
    print("⏳ Modules will be implemented in next sessions...")
    print()
    print("=" * 50)

if __name__ == "__main__":
    main()
''',

    # ─── Module __init__ Files ───
    "modules/__init__.py": "# OCEAN HUNTER Modules\n",
    "modules/core/__init__.py": "# Core Module\n",
    "modules/network/__init__.py": "# Network Module\n",
    "modules/analysis/__init__.py": "# Analysis Module\n",
    "modules/trading/__init__.py": "# Trading Module\n",
    "modules/security/__init__.py": "# Security Module\n",
    "modules/watchdog/__init__.py": "# Watchdog Module\n",
}

MODIFY_FILES = {}
MAIN_FILE = "main.py"

# ═══════════════════════════════════════════════════════════════
# ERROR TRACKING
# ═══════════════════════════════════════════════════════════════
errors = []

def log_error(step, error):
    errors.append(f"[{step}] {error}")
    print(f"      ⚠️ Error: {error}")

# ═══════════════════════════════════════════════════════════════
# STEPS 1-6
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
        subprocess.run([VENV_PYTHON, "-m", "pip", "install", "-r", req],
                      capture_output=True, check=True)
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

    print("\n" + "═" * 50)
    print(f"🔧 BUILD V3.4 | OCEAN HUNTER — Session 1")
    print(f"⏰ Started: {start_time.strftime('%H:%M:%S')}")
    print("═" * 50)

    try:
        step1_system()
        step2_venv()
        step3_deps()
        step4_folders()
        step5_new_files()
        step6_modify()

        print("\n[7/9] 📋 Context Generation...")
        try:
            context_gen.create_context_file()
            print("      ✅ Context created")
        except Exception as e:
            log_error("Step7-Context", e)

        print("\n[8/9] 🐙 Git...")
        try:
            setup_git.setup()
            setup_git.sync(f"Session 1: Structure Setup — {start_time.strftime('%Y-%m-%d %H:%M')}")
            print("      ✅ Git synced")
        except Exception as e:
            log_error("Step8-Git", e)

        print("\n[9/9] 🚀 Launch...")
        try:
            main_path = os.path.join(ROOT, MAIN_FILE)
            if os.path.exists(main_path):
                print("=" * 40)
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

        print("\n" + "═" * 50)

        if errors:
            print(f"⚠️ BUILD COMPLETED WITH {len(errors)} ERROR(S)")
            print("─" * 50)
            for err in errors:
                print(f"   • {err}")
        else:
            print("✅ BUILD COMPLETE — NO ERRORS")

        print("─" * 50)
        print(f"⏱️ Duration: {duration}s")
        print(f"🏁 Finished: {end_time.strftime('%H:%M:%S')}")
        print("═" * 50)

if __name__ == "__main__":
    main()
