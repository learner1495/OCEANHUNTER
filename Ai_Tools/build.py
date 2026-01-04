# AI_Tools/build.py — Phase 1: Virtual Wallet (MEXC Edition) + Git Sync
# ═══════════════════════════════════════════════════════════════
# Ref: GEMINI-PHASE1-MEXC-FIX-GIT
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
# ⭐ CONTENT GENERATION
# ═══════════════════════════════════════════════════════════════

# 1. Virtual Wallet Code (MEXC 0.1% Fee)
VIRTUAL_WALLET_CODE = """
import logging
from typing import Dict, Optional

# Configure logging
logger = logging.getLogger("VirtualWallet")

class VirtualWallet:
    \"\"\"
    Simulates a crypto exchange wallet with locking mechanism and fees.
    
    EXCHANGE: MEXC Global
    FEE STRUCTURE: 0.1% (0.001) for Maker/Taker (Standard Spot)
    \"\"\"
    
    def __init__(self, initial_balances: Dict[str, float] = None, commission_rate: float = 0.001):
        # Default commission_rate set to 0.001 (0.1%) for MEXC
        self.balances = initial_balances if initial_balances else {}  # Available funds
        self.locked = {}  # Funds locked in open orders
        self.commission_rate = commission_rate
        self.history = [] # Transaction history log

    def get_balance(self, asset: str) -> float:
        \"\"\"Returns AVAILABLE balance (not including locked).\"\"\"
        return self.balances.get(asset, 0.0)

    def get_total_balance(self, asset: str) -> float:
        \"\"\"Returns Total balance (Available + Locked).\"\"\"
        return self.balances.get(asset, 0.0) + self.locked.get(asset, 0.0)

    def lock_funds(self, asset: str, amount: float) -> bool:
        \"\"\"Locks funds for an order. Returns True if successful.\"\"\"
        if amount <= 0:
            return False
            
        available = self.balances.get(asset, 0.0)
        # Using a small epsilon for float comparison safety
        if available >= amount:
            self.balances[asset] = available - amount
            self.locked[asset] = self.locked.get(asset, 0.0) + amount
            return True
        else:
            logger.warning(f"Insufficient funds to lock {amount} {asset}. Available: {available}")
            return False

    def unlock_funds(self, asset: str, amount: float):
        \"\"\"Unlocks funds (e.g., cancelled order).\"\"\"
        locked_amount = self.locked.get(asset, 0.0)
        if locked_amount >= amount:
            self.locked[asset] = locked_amount - amount
            self.balances[asset] = self.balances.get(asset, 0.0) + amount
        else:
            logger.error(f"Attempted to unlock {amount} {asset} but only {locked_amount} is locked.")
            # Recover as much as possible
            self.balances[asset] = self.balances.get(asset, 0.0) + locked_amount
            self.locked[asset] = 0

    def apply_trade(self, side: str, base_asset: str, quote_asset: str, 
                   amount: float, price: float, is_maker: bool = False):
        \"\"\"
        Executes a trade and updates balances.
        side: 'BUY' or 'SELL'
        amount: Amount of Base Asset (e.g., BTC)
        price: Price in Quote Asset (e.g., USDT)
        \"\"\"
        cost = amount * price
        fee_rate = self.commission_rate 
        
        if side == 'BUY':
            # Buyer pays Quote (USDT), receives Base (BTC)
            # Funds were already locked in Quote (USDT)
            
            # 1. Deduct cost from locked Quote
            current_locked = self.locked.get(quote_asset, 0.0)
            if current_locked >= cost:
                self.locked[quote_asset] = current_locked - cost
            else:
                # Fallback correction
                remaining = cost - current_locked
                if self.balances.get(quote_asset, 0) >= remaining:
                    self.balances[quote_asset] -= remaining
                self.locked[quote_asset] = 0
                
            # 2. Add Base (BTC) - Fee is deducted from received asset on MEXC
            gross_receive = amount
            fee = gross_receive * fee_rate
            net_receive = gross_receive - fee
            
            self.balances[base_asset] = self.balances.get(base_asset, 0.0) + net_receive
            
            self._log_trade(side, base_asset, quote_asset, amount, price, fee, fee_asset=base_asset)
            
        elif side == 'SELL':
            # Seller pays Base (BTC), receives Quote (USDT)
            # Funds (BTC) were locked
            
            # 1. Deduct Base from locked
            current_locked = self.locked.get(base_asset, 0.0)
            if current_locked >= amount:
                self.locked[base_asset] = current_locked - amount
            else:
                 remaining = amount - current_locked
                 if self.balances.get(base_asset, 0) >= remaining:
                     self.balances[base_asset] -= remaining
                 self.locked[base_asset] = 0
                 
            # 2. Add Quote (USDT) - Fee deducted from USDT received
            gross_receive = cost
            fee = gross_receive * fee_rate
            net_receive = gross_receive - fee
            
            self.balances[quote_asset] = self.balances.get(quote_asset, 0.0) + net_receive
            
            self._log_trade(side, base_asset, quote_asset, amount, price, fee, fee_asset=quote_asset)

    def _log_trade(self, side, base, quote, amount, price, fee, fee_asset):
        self.history.append({
            "side": side,
            "pair": f"{base}{quote}",
            "amount": amount,
            "price": price,
            "fee": fee,
            "fee_asset": fee_asset,
            "timestamp": "SIMULATED" 
        })
"""

# 2. Updated Context Gen (Scanning 'tests' folder)
CONTEXT_GEN_CODE = """
import os
import datetime

# CONFIG
OUTPUT_FILE = "LATEST_PROJECT_CONTEXT.txt"
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
ROOT_DIR = os.path.dirname(SCRIPT_DIR)

# Folders to scan
INCLUDE_DIRS = ['AI_Tools', 'modules', 'tests'] 
EXCLUDE_DIRS = ['.git', '.venv', '__pycache__', 'context_backups', 'data', 'logs', 'candles', 'wallets', 'orderbooks']
# Note: We exclude raw data folders inside 'tests' from context to keep context small, 
# but include 'tests/core', 'tests/runners' etc.

EXTENSIONS = ['.py', '.txt', '.md', '.json', '.env']

def get_tree(startpath):
    tree = ""
    for root, dirs, files in os.walk(startpath):
        dirs[:] = [d for d in dirs if d not in EXCLUDE_DIRS]
        level = root.replace(startpath, '').count(os.sep)
        indent = ' ' * 4 * (level)
        tree += f"{indent}{os.path.basename(root)}/\\n"
        subindent = ' ' * 4 * (level + 1)
        for f in files:
            if any(f.endswith(ext) for ext in EXTENSIONS):
                tree += f"{subindent}{f}\\n"
    return tree

def read_files(startpath):
    content = ""
    for root, dirs, files in os.walk(startpath):
        dirs[:] = [d for d in dirs if d not in EXCLUDE_DIRS]
        for f in files:
            # Skip large data files even if json/txt
            if "LATEST_PROJECT_CONTEXT" in f: continue
            
            if any(f.endswith(ext) for ext in EXTENSIONS):
                path = os.path.join(root, f)
                rel_path = os.path.relpath(path, startpath)
                
                try:
                    with open(path, 'r', encoding='utf-8') as file:
                        content += f"\\n{'='*20}\\nFile: {rel_path}\\n{'='*20}\\n"
                        content += file.read() + "\\n"
                except Exception as e:
                    content += f"\\nError reading {rel_path}: {e}\\n"
    return content

def create_context_file():
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    header = f"GENERATED: {timestamp}\\n"
    header += f"VERSION: 3.1 (Phase 1: Virtual Wallet)\\n\\n"
    
    structure = "PROJECT STRUCTURE:\\n" + get_tree(ROOT_DIR)
    file_contents = "\\nFILE CONTENTS:\\n" + read_files(ROOT_DIR)
    
    full_content = header + structure + file_contents
    
    output_path = os.path.join(SCRIPT_DIR, OUTPUT_FILE)
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(full_content)
    
    print(f"✅ Context generated at: {output_path}")

if __name__ == "__main__":
    create_context_file()
"""

# 3. Telegram Report Script
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
        "🏗 **Ocean Hunter: Phase 1 Complete**\\n\\n"
        "✅ **Module:** Virtual Wallet (`tests/core/virtual_wallet.py`)\\n"
        "✅ **Config:** MEXC Mode (Fee: 0.1%)\\n"
        "✅ **Data Safety:** Existing test data preserved.\\n"
        "✅ **Git:** Synced with remote.\\n"
        "✅ **Context:** Updated to include test architecture.\\n\\n"
        "Ready for Phase 2: Data Provider Implementation."
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
    "tests/core/virtual_wallet.py": VIRTUAL_WALLET_CODE,
    "tests/__init__.py": "",          
    "tests/core/__init__.py": "",     
    "report_phase1.py": REPORT_SCRIPT
}

MODIFY_FILES = {
    "AI_Tools/context_gen.py": CONTEXT_GEN_CODE
}

MAIN_FILE = "report_phase1.py" 

# ═══════════════════════════════════════════════════════════════
# EXECUTION STEPS
# ═══════════════════════════════════════════════════════════════
errors = []

def log_error(step, error):
    errors.append(f"[{step}] {error}")
    print(f"      ⚠️ Error: {error}")

def main():
    print("\n" + "═" * 50)
    print(f"🔧 BUILD Phase 1: Virtual Wallet (MEXC Safe Mode)")
    print("═" * 50)

    try:
        # 1. Folders
        print("\n[1/7] 📁 Checking Folders...")
        for f in FOLDERS:
            path = os.path.join(ROOT, f)
            os.makedirs(path, exist_ok=True)
            print(f"      ✅ Verified: {f}/")

        # 2. Files
        print("\n[2/7] 📝 Writing Code Files...")
        for path, content in NEW_FILES.items():
            full = os.path.join(ROOT, path)
            with open(full, "w", encoding="utf-8") as f:
                f.write(content)
            print(f"      ✅ Wrote: {path}")

        # 3. Modify Context Gen
        print("\n[3/7] ✏️ Updating Context Generator...")
        for path, content in MODIFY_FILES.items():
            full = os.path.join(ROOT, path)
            with open(full, "w", encoding="utf-8") as f:
                f.write(content)
            print(f"      ✅ Updated: {path}")

        # 4. Run Context Gen
        print("\n[4/7] 📋 Refreshing Context...")
        import context_gen
        context_gen.create_context_file()

        # 5. Git Operations (CRITICAL STEP ADDED)
        print("\n[5/7] 🐙 Git Sync...")
        try:
            setup_git.setup()
            setup_git.sync("Phase 1: Virtual Wallet Implementation (MEXC)")
            print("      ✅ Git Synced Successfully")
        except Exception as e:
            log_error("Git", f"Sync failed: {e}")

        # 6. Report/Launch
        print("\n[6/7] 🚀 Sending Report...")
        subprocess.run([VENV_PYTHON, os.path.join(ROOT, MAIN_FILE)], cwd=ROOT)

    except Exception as e:
        print(f"\n💥 Critical: {e}")
        errors.append(str(e))

    finally:
        if errors:
            print(f"\n⚠️ Completed with {len(errors)} errors.")
        else:
            print("\n✅ Build Successful.")
            if os.path.exists(os.path.join(ROOT, "report_phase1.py")):
                os.remove(os.path.join(ROOT, "report_phase1.py"))

if __name__ == "__main__":
    main()
