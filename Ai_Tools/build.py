# AI_Tools/build.py — Phase 5: Backtest Runner & Reporting (FIXED)
# ═══════════════════════════════════════════════════════════════
# Ref: GEMINI-PHASE5-RUNNER-FIX
# ═══════════════════════════════════════════════════════════════

import os
import sys
import subprocess

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
# ⭐ CONTENT GENERATION (Phase 5 Logic)
# ═══════════════════════════════════════════════════════════════

# 1. The Backtest Runner Class
RUNNER_CODE = """
import logging
import time
from tests.core.virtual_wallet import VirtualWallet
from tests.core.data_engine import CsvCandlePlayer
from tests.core.simulator import MarketSimulator
from tests.core.test_provider import TestSimulatorProvider

logger = logging.getLogger("BacktestRunner")

class BacktestRunner:
    \"\"\"
    Orchestrates the entire backtest process:
    1. Sets up Wallet, Data, Simulator, Provider.
    2. Initializes the Strategy with the Provider.
    3. Runs the simulation loop.
    4. Generates a Performance Report.
    \"\"\"
    def __init__(self, csv_path, initial_capital=1000.0, symbol="SOL"):
        self.symbol = symbol
        self.initial_capital = initial_capital
        
        # Core Components
        self.wallet = VirtualWallet(initial_balances={"USDT": initial_capital})
        self.data_engine = CsvCandlePlayer(csv_path)
        self.simulator = MarketSimulator(self.wallet, self.data_engine)
        self.provider = TestSimulatorProvider(self.simulator)
        
        # Stats
        self.trades = []
        self.start_time = time.time()

    def run(self, strategy_class):
        \"\"\"
        Runs the backtest using the given Strategy Class.
        strategy_class: A class that accepts (provider, symbol) and has on_candle() method.
        \"\"\"
        print(f"🚀 Starting Backtest on {self.symbol}...")
        
        # Initialize Strategy
        strategy = strategy_class(self.provider, self.symbol)
        
        steps = 0
        while self.simulator.run_step():
            # Get current candle data
            candle = self.simulator.current_candle
            
            # Tick the strategy
            strategy.on_candle(candle)
            steps += 1
            
            if steps % 100 == 0:
                print(f"   ⏳ Processed {steps} candles...", end='\\r')

        print(f"\\n✅ Backtest Complete. Processed {steps} candles.")
        return self._generate_report()

    def _generate_report(self):
        \"\"\"Calculates basic performance metrics.\"\"\"
        final_balance = self.wallet.get_balance("USDT")
        
        # Calculate Asset Value (sell everything at last price)
        last_price = self.simulator.get_market_price()
        asset_qty = self.wallet.get_balance(self.symbol)
        asset_value = asset_qty * last_price
        
        total_equity = final_balance + asset_value
        pnl = total_equity - self.initial_capital
        roi = (pnl / self.initial_capital) * 100
        
        report = {
            "initial_capital": self.initial_capital,
            "final_equity": total_equity,
            "pnl": pnl,
            "roi": roi,
            "symbol": self.symbol,
            "simulated_trades": len(self.provider.orders) if hasattr(self.provider, 'orders') else "N/A"
        }
        return report
"""

# 2. A Mock Strategy for Testing the Runner
RUN_PHASE5_SCRIPT = """
import os
import sys
import requests
import logging
from dotenv import load_dotenv

sys.path.append(os.getcwd())

from tests.runners.backtest_runner import BacktestRunner

# Setup Logging
logging.basicConfig(level=logging.INFO, format='%(message)s')
load_dotenv()

TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

def send_telegram(msg):
    if not TOKEN or not CHAT_ID: return
    try:
        requests.post(f"https://api.telegram.org/bot{TOKEN}/sendMessage", 
                      json={"chat_id": CHAT_ID, "text": msg, "parse_mode": "Markdown"}, timeout=5)
    except: pass

# --- Mock Strategy for Phase 5 Test ---
class SimpleRSIStrategy:
    \"\"\"
    A simple logic to test the Runner:
    - Buy if price drops 1% below previous close (Dip Buy)
    - Sell if price rises 1% above avg buy
    \"\"\"
    def __init__(self, provider, symbol):
        self.provider = provider
        self.symbol = symbol
        self.position = 0
        self.last_close = 0

    def on_candle(self, candle):
        close = candle['close']
        
        # Skip first candle
        if self.last_close == 0:
            self.last_close = close
            return

        # Simple Logic
        change = (close - self.last_close) / self.last_close
        
        # BUY Logic (Dip)
        if change < -0.005 and self.position == 0: # -0.5% drop
            balance = self.provider.get_balance("USDT")
            if balance > 10:
                qty = (balance * 0.99) / close # Use 99% of cash
                self.provider.create_order(self.symbol, "BUY", "MARKET", qty)
                self.position = qty
                print(f"      🔵 BUY Signal at {close:.2f}")

        # SELL Logic (Profit)
        elif change > 0.005 and self.position > 0: # +0.5% pump
            self.provider.create_order(self.symbol, "SELL", "MARKET", self.position)
            print(f"      🟠 SELL Signal at {close:.2f}")
            self.position = 0

        self.last_close = close

# --- Main Execution ---
def main():
    print("🚀 STARTING PHASE 5: BACKTEST RUNNER TEST")
    
    # Locate Data
    csv_path = os.path.join("tests", "data", "candles", "SOL_M15.csv")
    if not os.path.exists(csv_path):
        import glob
        files = glob.glob("tests/data/**/*.csv", recursive=True)
        if files: csv_path = files[0]
        else:
            print("❌ No CSV found."); sys.exit(1)

    # Init Runner
    runner = BacktestRunner(csv_path, initial_capital=5000.0, symbol="SOL")
    
    # Run with our Simple Strategy
    stats = runner.run(SimpleRSIStrategy)
    
    # Report
    print("-" * 30)
    print(f"📊 REPORT FOR {stats['symbol']}")
    print(f"💰 Start Capital: ${stats['initial_capital']:.2f}")
    print(f"🏁 Final Equity: ${stats['final_equity']:.2f}")
    print(f"📈 PnL: ${stats['pnl']:.2f} ({stats['roi']:.2f}%)")
    print("-" * 30)
    
    msg = (
        "🏆 **Ocean Hunter: Phase 5 Complete**\\n\\n"
        "✅ **Backtest Runner Operational**\\n"
        f"📊 Symbol: `{stats['symbol']}`\\n"
        f"💰 Final Equity: `{stats['final_equity']:.2f} USDT`\\n"
        f"📈 ROI: `{stats['roi']:.2f}%`\\n\\n"
        "Ready for REAL Strategy Injection (Smart Sniper)."
    )
    send_telegram(msg)

if __name__ == "__main__":
    main()
"""

# ═══════════════════════════════════════════════════════════════
# CONFIGURATION
# ═══════════════════════════════════════════════════════════════
NEW_FILES = {
    "tests/runners/backtest_runner.py": RUNNER_CODE,
    "run_phase5.py": RUN_PHASE5_SCRIPT
}

# ═══════════════════════════════════════════════════════════════
# EXECUTION
# ═══════════════════════════════════════════════════════════════
def main():
    print("\n" + "═" * 50)
    print(f"🔧 BUILD Phase 5: Backtest Runner Engine")
    print("═" * 50)

    try:
        # 1. Write Files
        print("\n[1/4] 📝 Writing Files...")
        
        # Ensure directory exists
        runner_dir = os.path.join(ROOT, "tests", "runners")
        if not os.path.exists(runner_dir):
            os.makedirs(runner_dir)
            
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
        print("\n[3/4] 🏃 Running Phase 5 Test...")
        result = subprocess.run([VENV_PYTHON, os.path.join(ROOT, "run_phase5.py")], cwd=ROOT)
        
        if result.returncode != 0:
            raise Exception("Test Script Failed!")

        # 4. Git Sync
        print("\n[4/4] 🐙 Git Sync...")
        try:
            setup_git.setup()
            setup_git.sync("Phase 5: Backtest Runner Engine")
            print("      ✅ Git Synced")
        except:
            print("      ⚠️ Git Warning (Ignored)")

    except Exception as e:
        print(f"\n💥 Critical Error: {e}")

    finally:
        # Cleanup
        cleanup_path = os.path.join(ROOT, "run_phase5.py")
        if os.path.exists(cleanup_path):
            os.remove(cleanup_path)

if __name__ == "__main__":
    main()
