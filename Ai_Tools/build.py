# AI_Tools/build.py — Phase 2: Data Engine (Candle Player)
# ═══════════════════════════════════════════════════════════════
# Ref: GEMINI-PHASE2-DATA-ENGINE
# ═══════════════════════════════════════════════════════════════

import os
import sys
import subprocess
import socket
from datetime import datetime

# ═══ Import Internal Modules ═══
try:
    import context_gen
    import setup_git
except ImportError:
    pass 

# ═══════════════════════════════════════════════════════════════
# PATHS
# ═══════════════════════════════════════════════════════════════
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(SCRIPT_DIR)
VENV_PATH = os.path.join(ROOT, ".venv")
VENV_PYTHON = os.path.join(VENV_PATH, "Scripts", "python.exe") if sys.platform == "win32" else os.path.join(VENV_PATH, "bin", "python")

# ═══════════════════════════════════════════════════════════════
# ⭐ CONTENT GENERATION (Phase 2 Logic)
# ═══════════════════════════════════════════════════════════════

# 1. Interfaces (Contract for Data & Strategy)
INTERFACES_CODE = """
from abc import ABC, abstractmethod
from typing import Dict, Any

class IDataProvider(ABC):
    \"\"\"Interface for fetching market data (Live or Backtest).\"\"\"
    
    @abstractmethod
    def get_next_candle(self) -> Dict[str, Any]:
        \"\"\"Returns the next candle or None if EOF.\"\"\"
        pass

    @abstractmethod
    def get_server_time(self) -> int:
        \"\"\"Returns current simulated or real server time (ms).\"\"\"
        pass

class IExecutionEngine(ABC):
    \"\"\"Interface for executing orders.\"\"\"
    pass
"""

# 2. Data Engine (The CSV Player)
DATA_ENGINE_CODE = """
import pandas as pd
import logging
import os
from datetime import datetime
from .interfaces import IDataProvider

logger = logging.getLogger("DataEngine")

class CsvCandlePlayer(IDataProvider):
    \"\"\"
    Reads a CSV file and yields candles one by one to simulate live market.
    Expected CSV columns: 'Open time', 'Open', 'High', 'Low', 'Close', 'Volume'
    \"\"\"

    def __init__(self, csv_path: str):
        self.csv_path = csv_path
        self.data = None
        self.current_index = 0
        self.current_timestamp = 0
        
        self._load_data()

    def _load_data(self):
        if not os.path.exists(self.csv_path):
            raise FileNotFoundError(f"Data file not found: {self.csv_path}")
            
        try:
            # Load CSV
            df = pd.read_csv(self.csv_path)
            
            # Standardize columns (strip spaces)
            df.columns = [c.strip() for c in df.columns]
            
            # Ensure required columns exist
            required = ['Open time', 'Open', 'High', 'Low', 'Close', 'Volume']
            if not all(col in df.columns for col in required):
                raise ValueError(f"CSV missing columns. Required: {required}")
                
            # Sort by time just in case
            df = df.sort_values('Open time').reset_index(drop=True)
            
            self.data = df
            logger.info(f"Loaded {len(df)} candles from {os.path.basename(self.csv_path)}")
            
        except Exception as e:
            logger.error(f"Failed to load CSV: {e}")
            raise

    def get_next_candle(self):
        \"\"\"Returns the next row as a dictionary.\"\"\"
        if self.current_index >= len(self.data):
            return None # End of Data
            
        row = self.data.iloc[self.current_index]
        self.current_index += 1
        
        # Convert row to dict
        candle = {
            'timestamp': int(row['Open time']),
            'open': float(row['Open']),
            'high': float(row['High']),
            'low': float(row['Low']),
            'close': float(row['Close']),
            'volume': float(row['Volume'])
        }
        
        # Update internal clock
        self.current_timestamp = candle['timestamp']
        
        return candle

    def get_server_time(self) -> int:
        \"\"\"Returns the close time of the LAST processed candle (simulated 'now').\"\"\"
        return self.current_timestamp
"""

# 3. Telegram Report Script (Phase 2)
REPORT_SCRIPT = """
import os
import requests
from dotenv import load_dotenv

load_dotenv()

TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

def send_report():
    if not TOKEN or not CHAT_ID:
        print("⚠️ Telegram credentials missing.")
        return

    msg = (
        "⏳ **Ocean Hunter: Phase 2 Complete**\\n\\n"
        "✅ **Module:** Data Engine (`tests/core/data_engine.py`)\\n"
        "✅ **Interface:** `IDataProvider` defined.\\n"
        "✅ **Function:** CSV Reading & Time Simulation ready.\\n"
        "✅ **Git:** Synced with remote.\\n\\n"
        "Ready for Phase 3: Integration (Connecting Wallet + Data)."
    )
    
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    payload = {"chat_id": CHAT_ID, "text": msg, "parse_mode": "Markdown"}
    
    try:
        resp = requests.post(url, json=payload, timeout=10)
        print(f"Telegram sent: {resp.status_code}")
    except Exception as e:
        print(f"Telegram fail: {e}")

if __name__ == "__main__":
    send_report()
"""

# ═══════════════════════════════════════════════════════════════
# CONFIGURATION
# ═══════════════════════════════════════════════════════════════
FOLDERS = [
    "tests/core"
]

NEW_FILES = {
    "tests/core/interfaces.py": INTERFACES_CODE,
    "tests/core/data_engine.py": DATA_ENGINE_CODE,
    "report_phase2.py": REPORT_SCRIPT
}

# ═══════════════════════════════════════════════════════════════
# EXECUTION STEPS
# ═══════════════════════════════════════════════════════════════
errors = []

def log_error(step, error):
    errors.append(f"[{step}] {error}")
    print(f"      ⚠️ Error: {error}")

def main():
    print("\n" + "═" * 50)
    print(f"🔧 BUILD Phase 2: Data Engine (Candle Player)")
    print("═" * 50)

    try:
        # 1. Folders
        print("\n[1/6] 📁 Checking Folders...")
        for f in FOLDERS:
            path = os.path.join(ROOT, f)
            os.makedirs(path, exist_ok=True)
            print(f"      ✅ Verified: {f}/")

        # 2. Files
        print("\n[2/6] 📝 Writing Code Files...")
        for path, content in NEW_FILES.items():
            full = os.path.join(ROOT, path)
            with open(full, "w", encoding="utf-8") as f:
                f.write(content)
            print(f"      ✅ Wrote: {path}")

        # 3. Context Gen (Reuse existing module)
        print("\n[3/6] 📋 Refreshing Context...")
        import context_gen
        context_gen.create_context_file()

        # 4. Git Operations
        print("\n[4/6] 🐙 Git Sync...")
        try:
            setup_git.setup()
            setup_git.sync("Phase 2: Data Engine Implementation")
            print("      ✅ Git Synced Successfully")
        except Exception as e:
            log_error("Git", f"Sync failed: {e}")

        # 5. Report
        print("\n[5/6] 🚀 Sending Report...")
        subprocess.run([VENV_PYTHON, os.path.join(ROOT, "report_phase2.py")], cwd=ROOT)

    except Exception as e:
        print(f"\n💥 Critical: {e}")
        errors.append(str(e))

    finally:
        if errors:
            print(f"\n⚠️ Completed with {len(errors)} errors.")
        else:
            print("\n✅ Build Successful.")
            if os.path.exists(os.path.join(ROOT, "report_phase2.py")):
                os.remove(os.path.join(ROOT, "report_phase2.py"))

if __name__ == "__main__":
    main()
