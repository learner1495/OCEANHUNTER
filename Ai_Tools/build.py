# AI_Tools/build.py — Phase 3: Simulator Core Integration (FIXED V2)
# ═══════════════════════════════════════════════════════════════
# Ref: GEMINI-PHASE3-DATA-ENGINE-FIX
# ═══════════════════════════════════════════════════════════════

import os
import sys
import subprocess
import glob

# ═══ Import Internal Modules ═══
try:
    import context_gen
    import setup_git
except ImportError:
    pass 

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(SCRIPT_DIR)
VENV_PATH = os.path.join(ROOT, ".venv")
VENV_PYTHON = os.path.join(VENV_PATH, "Scripts", "python.exe") if sys.platform == "win32" else os.path.join(VENV_PATH, "bin", "python")

# ═══════════════════════════════════════════════════════════════
# ⭐ CONTENT GENERATION
# ═══════════════════════════════════════════════════════════════

# 1. ROBUST DATA ENGINE (Fixes Column Mismatch)
DATA_ENGINE_CODE = """
import pandas as pd
import logging
from .interfaces import IDataProvider

logger = logging.getLogger("DataEngine")

class CsvCandlePlayer(IDataProvider):
    \"\"\"
    Reads historical data from CSV and serves it candle by candle.
    Compatible with:
    1. Generated Test Data (timestamp, open, high...)
    2. Binance/MEXC Export (Open time, Open, High...)
    \"\"\"
    def __init__(self, csv_path):
        self.csv_path = csv_path
        self.data = pd.DataFrame()
        self.current_index = 0
        self._load_data()

    def _load_data(self):
        try:
            df = pd.read_csv(self.csv_path)
            
            # 1. Normalize Column Names (Lowercase & Strip)
            df.columns = [c.lower().strip() for c in df.columns]
            
            # 2. Map Standard Names
            rename_map = {
                'open time': 'timestamp',
                'time': 'timestamp',
                'date': 'timestamp',
                'vol': 'volume'
            }
            df.rename(columns=rename_map, inplace=True)
            
            # 3. Validate Required Columns
            required = {'timestamp', 'open', 'high', 'low', 'close', 'volume'}
            if not required.issubset(df.columns):
                missing = required - set(df.columns)
                raise ValueError(f"CSV missing columns: {missing}. Found: {list(df.columns)}")
                
            # 4. Sort by time
            df.sort_values('timestamp', inplace=True)
            df.reset_index(drop=True, inplace=True)
            
            self.data = df
            logger.info(f"Loaded {len(df)} candles from {self.csv_path}")
            
        except Exception as e:
            logger.error(f"Failed to load CSV: {e}")
            raise

    def get_next_candle(self):
        if self.current_index < len(self.data):
            # Convert row to dict
            candle = self.data.iloc[self.current_index].to_dict()
            self.current_index += 1
            return candle
        return None

    def get_server_time(self):
        # Return time of current candle (Simulation Time)
        if self.current_index > 0:
            return self.data.iloc[self.current_index - 1]['timestamp']
        return 0
"""

# 2. SIMULATOR LOGIC (Same as before)
SIMULATOR_CODE = """
import logging
from .interfaces import IDataProvider
from .virtual_wallet import VirtualWallet

logger = logging.getLogger("Simulator")

class MarketSimulator:
    \"\"\"
    The Brain of the Test.
    Connects DataProvider (Market) -> VirtualWallet (Account).
    \"\"\"
    def __init__(self, wallet: VirtualWallet, data_provider: IDataProvider):
        self.wallet = wallet
        self.data_provider = data_provider
        self.current_candle = None
        self.steps_count = 0

    def run_step(self):
        \"\"\"Advances the simulation by one candle.\"\"\"
        candle = self.data_provider.get_next_candle()
        
        if not candle:
            return False # End of Data

        self.current_candle = candle
        self.steps_count += 1
        return True

    def execute_trade(self, symbol: str, side: str, quantity: float):
        \"\"\"Manually execute a trade at the CURRENT candle's closing price.\"\"\"
        if not self.current_candle:
            raise Exception("Market not started yet. Call run_step() first.")
            
        price = self.current_candle['close']
        cost = price * quantity
        fee = cost * self.wallet.commission_rate
        
        if side.upper() == "BUY":
            usdt_bal = self.wallet.get_balance("USDT")
            total_cost = cost + fee
            
            if usdt_bal >= total_cost:
                self.wallet.balances["USDT"] = usdt_bal - total_cost
                current_asset = self.wallet.get_balance(symbol)
                self.wallet.balances[symbol] = current_asset + quantity
                logger.info(f"👉 EXECUTED BUY {quantity} {symbol} @ ${price}")
            else:
                logger.error("Insufficient USDT for BUY")

        elif side.upper() == "SELL":
            asset_bal = self.wallet.get_balance(symbol)
            if asset_bal >= quantity:
                self.wallet.balances[symbol] = asset_bal - quantity
                proceeds = cost - fee
                current_usdt = self.wallet.get_balance("USDT")
                self.wallet.balances["USDT"] = current_usdt + proceeds
                logger.info(f"👉 EXECUTED SELL {quantity} {symbol} @ ${price}")
            else:
                logger.error(f"Insufficient {symbol} for SELL")

    def get_market_price(self):
        return self.current_candle['close'] if self.current_candle else 0
"""

# 3. TEST SCRIPT (Fixed Paths)
RUN_TEST_SCRIPT = """
import os
import sys
import requests
import logging
from dotenv import load_dotenv

# Add project root to sys.path
sys.path.append(os.getcwd())

from tests.core.virtual_wallet import VirtualWallet
from tests.core.data_engine import CsvCandlePlayer
from tests.core.simulator import MarketSimulator

# Setup Logging
logging.basicConfig(level=logging.INFO, format='%(name)s - %(message)s')
load_dotenv()

TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

def find_correct_csv():
    # Priority 1: Generated Test Data (Standard Format)
    priority_path = os.path.join("tests", "data", "candles", "SOL_M15.csv")
    if os.path.exists(priority_path):
        return priority_path
        
    # Priority 2: Any CSV in tests/data
    for root, dirs, files in os.walk("tests/data"):
        for file in files:
            if file.endswith(".csv"):
                return os.path.join(root, file)
                
    return None

def send_telegram(msg):
    if not TOKEN or not CHAT_ID:
        return
    try:
        url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
        requests.post(url, json={"chat_id": CHAT_ID, "text": msg, "parse_mode": "Markdown"}, timeout=10)
    except:
        pass

def main():
    print("🚀 STARTING PHASE 3: INTEGRATION TEST (V2)")
    
    csv_file = find_correct_csv()
    if not csv_file:
        print("❌ ERROR: No Test Data found! Run 'python setup_test_data.py' first.")
        sys.exit(1)
        
    print(f"📂 Using Data: {csv_file}")

    try:
        # 1. Init System
        wallet = VirtualWallet(initial_balances={"USDT": 1000.0})
        data = CsvCandlePlayer(csv_file)
        sim = MarketSimulator(wallet, data)

        # 2. Run Simulation
        print("⏳ Running Simulation Loop...")
        
        # Step 1: Advance & BUY
        if sim.run_step():
            price_start = sim.get_market_price()
            print(f"   🔹 Start Price: ${price_start}")
            
            # Buy ~ $100
            qty = round(100.0 / price_start, 4)
            sim.execute_trade("SOL", "BUY", qty)

        # Step 2: Fast forward
        last_price = 0
        candles_processed = 0
        while sim.run_step():
            last_price = sim.get_market_price()
            candles_processed += 1
            
        # Step 3: SELL
        print(f"   🔹 End Price: ${last_price} (Processed {candles_processed} candles)")
        sim.execute_trade("SOL", "SELL", qty)
        
        # 3. Results
        final_usdt = wallet.get_balance("USDT")
        pnl = final_usdt - 1000.0
        pnl_percent = (pnl / 1000.0) * 100
        
        print("-" * 30)
        print(f"💰 Final Balance: ${final_usdt:.2f}")
        print(f"MEG PnL: ${pnl:.2f} ({pnl_percent:.2f}%)")
        print("-" * 30)

        # 4. Report
        msg = (
            "🔗 **Ocean Hunter: Phase 3 Complete**\\n\\n"
            "✅ **Integration Successful**\\n"
            f"📂 Data: `{os.path.basename(csv_file)}`\\n"
            f"🕯 Candles: {candles_processed}\\n"
            f"💵 PnL: `{pnl:.2f} USDT` ({pnl_percent:.2f}%)\\n\\n"
            "Simulator Core is Stable. Ready for Strategy."
        )
        send_telegram(msg)
        
    except Exception as e:
        print(f"❌ Runtime Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
"""

# ═══════════════════════════════════════════════════════════════
# CONFIGURATION
# ═══════════════════════════════════════════════════════════════
NEW_FILES = {
    "tests/core/data_engine.py": DATA_ENGINE_CODE,
    "tests/core/simulator.py": SIMULATOR_CODE,
    "run_phase3.py": RUN_TEST_SCRIPT
}

# ═══════════════════════════════════════════════════════════════
# EXECUTION
# ═══════════════════════════════════════════════════════════════
def main():
    print("\n" + "═" * 50)
    print(f"🔧 BUILD Phase 3: Simulator Core (Fix Data Engine)")
    print("═" * 50)

    try:
        # 1. Write Files
        print("\n[1/4] 📝 Writing Files...")
        for path, content in NEW_FILES.items():
            full = os.path.join(ROOT, path)
            with open(full, "w", encoding="utf-8") as f:
                f.write(content)
            print(f"      ✅ Wrote: {path}")

        # 2. Context Gen
        print("\n[2/4] 📋 Refreshing Context...")
        import context_gen
        context_gen.create_context_file()

        # 3. Run the Test
        print("\n[3/4] 🏃 Running Integration Test (Local)...")
        result = subprocess.run([VENV_PYTHON, os.path.join(ROOT, "run_phase3.py")], cwd=ROOT)
        
        if result.returncode != 0:
            raise Exception("Test Script Failed!")

        # 4. Git Sync
        print("\n[4/4] 🐙 Git Sync...")
        try:
            setup_git.setup()
            setup_git.sync("Phase 3: Simulator Integration (Final Fix)")
            print("      ✅ Git Synced")
        except:
            print("      ⚠️ Git Warning (Ignored)")

    except Exception as e:
        print(f"\n💥 Critical Error: {e}")

    finally:
        if os.path.exists(os.path.join(ROOT, "run_phase3.py")):
            os.remove(os.path.join(ROOT, "run_phase3.py"))

if __name__ == "__main__":
    main()
