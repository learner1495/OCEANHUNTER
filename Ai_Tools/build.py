# AI_Tools/build.py — Data Collection V5.0
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

FOLDERS = ["modules/data", "data/ohlcv"]
errors = []

def log_error(step, error):
    errors.append(f"[{step}] {error}")
    print(f"      ⚠️ Error: {error}")

# ═══════════════════════════════════════════════════════════════
# MAIN.PY CONTENT
# ═══════════════════════════════════════════════════════════════
MAIN_PY = '''#!/usr/bin/env python3
"""OCEAN HUNTER V10.9 — Data Collection"""

import os
import sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from dotenv import load_dotenv
load_dotenv()

def main():
    print("\\n" + "=" * 50)
    print("🌊 OCEAN HUNTER V10.9 — Data Collection")
    print("=" * 50)

    mode = os.getenv("MODE", "PAPER")
    print(f"\\n🔧 Mode: {mode}")

    print("\\n[1/4] 🔌 Testing Nobitex API...")
    try:
        from modules.network import get_client
        client = get_client()
        result = client.test_connection()
        print(f"      Public API:  {\\'✅\\' if result[\\'public_api\\'] else \\'❌\\'}")
        print(f"      Private API: {\\'✅\\' if result[\\'private_api\\'] else \\'❌\\'}")
    except Exception as e:
        print(f"      ❌ Error: {e}")

    print("\\n[2/4] 📱 Testing Telegram Bot...")
    try:
        from modules.network import get_bot
        bot = get_bot()
        if bot.enabled:
            response = bot.send_alert(title="OCEAN HUNTER V10.9", message="✅ Data Collection فعال شد", alert_type="SUCCESS")
            if response.get("ok"):
                print("      ✅ Telegram message sent!")
            else:
                print(f"      ⚠️ Telegram error: {response.get(\\'error\\', \\'Unknown\\')}")
        else:
            print("      ⚠️ Telegram not configured")
    except Exception as e:
        print(f"      ❌ Error: {e}")

    print("\\n[3/4] ⏱️ Rate Limiter Status...")
    try:
        from modules.network import get_statusrl_status = get_status()
        print(f"      Tokens: {rl_status[\\'tokens_available\\']}/{rl_status[\\'max_tokens\\']}")
        print(f"      Usage:  {rl_status[\\'usage_percent\\']}%")
    except Exception as e:
        print(f"      ❌ Error: {e}")

    print("\\n[4/4] 📊 Data Collection...")
    try:
        from modules.data import get_collector
        collector = get_collector()
        results = collector.collect_all()
        print(f"      ✅ Collected {results[\\'total_candles\\']} candles")
        print(f"      📈 Symbols: {results[\\'success_count\\']}/{len(results[\\'symbols\\'])}")
        summary = collector.get_summary()
        for symbol, stats in summary.items():
            if stats.get(\\'exists\\'):
                print(f"      📁 {symbol}: {stats[\\'rows\\']} rows")
    except Exception as e:
        print(f"      ❌ Error: {e}")

    print("\\n" + "=" * 50)
    print("✅ ALL TASKS COMPLETE")
    print("=" * 50 + "\\n")

if __name__ == "__main__":
    main()
'''

# ═══════════════════════════════════════════════════════════════
# DATA MODULE FILES
# ═══════════════════════════════════════════════════════════════
DATA_INIT = '''# modules/data/__init__.py
from .collector import DataCollector, get_collector
from .storage import DataStorage, get_storage
__all__ = ["DataCollector", "get_collector", "DataStorage", "get_storage"]
'''

DATA_STORAGE = '''# modules/data/storage.py
import os
import csv
from datetime import datetime
from typing import List, Dict, Any, Optional

class DataStorage:
    def __init__(self, data_dir: str = None):
        if data_dir is None:
            current = os.path.dirname(os.path.abspath(__file__))
            root = os.path.dirname(os.path.dirname(current))
            data_dir = os.path.join(root, "data", "ohlcv")
        self.data_dir = data_dir
        self._ensure_dir()

    def _ensure_dir(self):
        if not os.path.exists(self.data_dir):
            os.makedirs(self.data_dir)

    def _get_filepath(self, symbol: str) -> str:
        safe_symbol = symbol.replace("/", "_").upper()
        return os.path.join(self.data_dir, f"{safe_symbol}.csv")

    def save_ohlcv(self, symbol: str, data: List[Dict]) -> bool:
        if not data:
            return False
        filepath = self._get_filepath(symbol)
        file_exists = os.path.exists(filepath)
        try:
            existing_timestamps = set()
            if file_exists:
                with open(filepath, 'r', encoding='utf-8') as f:
                    reader = csv.DictReader(f)
                    for row in reader:
                        existing_timestamps.add(row.get('timestamp', ''))
            new_data = [row for row in data if str(row.get('timestamp', '')) not in existing_timestamps]
            if not new_data:
                return True
            fieldnames = ['timestamp', 'datetime', 'open', 'high', 'low', 'close', 'volume']
            with open(filepath, 'a', newline='', encoding='utf-8') as f:
                writer = csv.DictWriter(f, fieldnames=fieldnames)
                if not file_exists:
                    writer.writeheader()
                for row in new_data:
                    ts = row.get('timestamp', 0)
                    dt = datetime.fromtimestamp(ts).strftime('%Y-%m-%d %H:%M:%S') if ts else ''
                    writer.writerow({
                        'timestamp': ts, 'datetime': dt,
                        'open': row.get('open', 0), 'high': row.get('high', 0),
                        'low': row.get('low', 0), 'close': row.get('close', 0),
                        'volume': row.get('volume', 0)
                    })
            return True
        except Exception as e:
            print(f"[Storage] Error saving {symbol}: {e}")
            return False

    def get_latest(self, symbol: str, count: int = 100) -> List[Dict]:
        filepath = self._get_filepath(symbol)
        if not os.path.exists(filepath):
            return []
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                rows = list(csv.DictReader(f))
            return rows[-count:] if len(rows) > count else rows
        except Exception as e:
            print(f"[Storage] Error reading {symbol}: {e}")
            return []

    def get_stats(self, symbol: str) -> Dict[str, Any]:
        filepath = self._get_filepath(symbol)
        if not os.path.exists(filepath):
            return {"exists": False, "rows": 0}
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                rows = list(csv.DictReader(f))
            if not rows:
                return {"exists": True, "rows": 0}
            return {
                "exists": True, "rows": len(rows),
                "first_date": rows[0].get('datetime', 'N/A'),
                "last_date": rows[-1].get('datetime', 'N/A'),
                "file_size_kb": round(os.path.getsize(filepath) / 1024, 2)
            }
        except Exception as e:
            return {"exists": True, "rows": 0, "error": str(e)}

_storage: Optional[DataStorage] = None
def get_storage() -> DataStorage:
    global _storage
    if _storage is None:
        _storage = DataStorage()
    return _storage
'''

DATA_COLLECTOR = '''# modules/data/collector.py
import time
from datetime import datetime
from typing import Dict, Any, List, Optional
from modules.network import get_client
from .storage import get_storage

class DataCollector:
    DEFAULT_SYMBOLS = ["BTCIRT", "ETHIRT", "USDTIRT"]

    def __init__(self):
        self.client = get_client()
        self.storage = get_storage()
        self.symbols = self.DEFAULT_SYMBOLS.copy()

    def fetch_ohlcv(self, symbol: str, resolution: str = "15") -> List[Dict]:
        try:
            now = int(time.time())
            from_ts = now - (24 * 60 * 60)
            result = self.client.get_ohlcv(symbol=symbol, resolution=resolution, from_ts=from_ts, to_ts=now)
            if result.get("s") != "ok":
                print(f"[Collector] API error for {symbol}: {result.get('s', 'unknown')}")
                return []
            candles = []
            timestamps = result.get("t", [])
            opens = result.get("o", [])
            highs = result.get("h", [])
            lows = result.get("l", [])
            closes = result.get("c", [])
            volumes = result.get("v", [])
            for i in range(len(timestamps)):
                candles.append({
                    "timestamp": timestamps[i],
                    "open": opens[i] if i < len(opens) else 0,
                    "high": highs[i] if i < len(highs) else 0,
                    "low": lows[i] if i < len(lows) else 0,
                    "close": closes[i] if i < len(closes) else 0,
                    "volume": volumes[i] if i < len(volumes) else 0
                })
            return candles
        except Exception as e:
            print(f"[Collector] Error fetching {symbol}: {e}")
            return []

    def collect_symbol(self, symbol: str) -> Dict[str, Any]:
        result = {"symbol": symbol, "success": False, "candles_fetched": 0, "candles_saved": 0}
        candles = self.fetch_ohlcv(symbol)
        result["candles_fetched"] = len(candles)
        if not candles:
            return result
        saved = self.storage.save_ohlcv(symbol, candles)
        if saved:
            result["success"] = True
            result["candles_saved"] = len(candles)
        return result

    def collect_all(self) -> Dict[str, Any]:
        results = {"timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"), "symbols": {}, "total_candles": 0, "success_count": 0}
        for symbol in self.symbols:
            print(f"      📊 Collecting {symbol}...")
            res = self.collect_symbol(symbol)
            results["symbols"][symbol] = res
            results["total_candles"] += res["candles_fetched"]
            if res["success"]:
                results["success_count"] += 1print(f"         ✅ {res['candles_fetched']} candles")
            else:
                print(f"         ❌ Failed")
            time.sleep(1)
        return results

    def get_summary(self) -> Dict[str, Any]:
        summary = {}
        for symbol in self.symbols:
            summary[symbol] = self.storage.get_stats(symbol)
        return summary

_collector: Optional[DataCollector] = None
def get_collector() -> DataCollector:
    global _collector
    if _collector is None:
        _collector = DataCollector()
    return _collector
'''

NEW_FILES = {
    "modules/data/__init__.py": DATA_INIT,
    "modules/data/storage.py": DATA_STORAGE,
    "modules/data/collector.py": DATA_COLLECTOR
}

MODIFY_FILES = {"main.py": MAIN_PY}

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
        subprocess.run([VENV_PYTHON, "-m", "pip", "install", "-r", req, "-q"], capture_output=True, check=True)
        print("      ✅ Installed")
    except Exception as e:
        log_error("Step3", e)

def step4_folders():
    print("\n[4/9] 📁 Folders...")
    try:
        for f in FOLDERS:
            path = os.path.join(ROOT, f)
            if not os.path.exists(path):
                os.makedirs(path)
                print(f"      ✅ Created: {f}/")
            else:
                print(f"      ℹ️ Exists: {f}/")
    except Exception as e:
        log_error("Step4", e)

def step5_new_files():
    print("\n[5/9] 📝 New Files...")
    try:
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
        for path, content in MODIFY_FILES.items():
            full = os.path.join(ROOT, path)
            with open(full, "w", encoding="utf-8") as f:
                f.write(content)
            print(f"      ✏️ Modified: {path}")
    except Exception as e:
        log_error("Step6", e)

def step7_context():
    print("\n[7/9] 📋 Context Generation...")
    try:
        context_gen.create_context_file()
        print("      ✅ Context created")
    except Exception as e:
        log_error("Step7", e)

def step8_git():
    print("\n[8/9] 🐙 Git Sync...")
    try:
        setup_git.setup()
        setup_git.sync("Build V5.0: Data Collection Module")
        print("      ✅ Git synced")
    except Exception as e:
        log_error("Step8", e)

def step9_launch():
    print("\n[9/9] 🚀 Launch...")
    try:
        main_path = os.path.join(ROOT, "main.py")
        if os.path.exists(main_path):
            print("=" * 40)
            subprocess.run([VENV_PYTHON, main_path], cwd=ROOT)
        else:
            print("      ℹ️ No main.py")
    except Exception as e:
        log_error("Step9", e)

# ═══════════════════════════════════════════════════════════════
# MAIN
# ═══════════════════════════════════════════════════════════════
def main():
    start_time = datetime.now()
    print("\n" + "═" * 50)
    print("🔧 BUILD V5.0 — Data Collection")
    print(f"⏰ Started: {start_time.strftime('%H:%M:%S')}")
    print("═" * 50)

    try:
        step1_system()
        step2_venv()
        step3_deps()
        step4_folders()
        step5_new_files()
        step6_modify()
        step7_context()
        step8_git()
        step9_launch()
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
            print(f"⚠️ BUILD COMPLETE WITH {len(errors)} ERROR(S):")
            for err in errors:
                print(f"   • {err}")
        else:
            print("✅ BUILD COMPLETE — NO ERRORS")
        print(f"⏱️ Duration: {duration}s")
        print(f"🏁 Finished: {end_time.strftime('%H:%M:%S')}")
        print("═" * 50 + "\n")

if __name__ == "__main__":
    main()
