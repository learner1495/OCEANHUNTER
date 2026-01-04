# AI_Tools/build.py — Phase 4: Test Provider Implementation
# ═══════════════════════════════════════════════════════════════
# Ref: GEMINI-PHASE4-PROVIDER-ADAPTER
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
# ⭐ CONTENT GENERATION (Phase 4 Logic)
# ═══════════════════════════════════════════════════════════════

# 1. The Adapter Class (TestSimulatorProvider)
PROVIDER_CODE = """
import logging
from .simulator import MarketSimulator

logger = logging.getLogger("TestProvider")

class TestSimulatorProvider:
    \"\"\"
    A wrapper around MarketSimulator that mimics a Real Exchange Provider.
    Strategies will interact with THIS class, not the Simulator directly.
    \"\"\"
    def __init__(self, simulator: MarketSimulator):
        self.sim = simulator

    # --- Market Data Methods ---
    def get_ticker_price(self, symbol: str) -> float:
        \"\"\"Returns the current price from the simulator.\"\"\"
        return self.sim.get_market_price()

    def get_server_time(self):
        \"\"\"Returns the simulated time.\"\"\"
        if self.sim.current_candle:
            return self.sim.current_candle.get('timestamp')
        return 0

    # --- Account Methods ---
    def get_balance(self, asset: str) -> float:
        \"\"\"Returns balance from the Virtual Wallet.\"\"\"
        return self.sim.wallet.get_balance(asset)

    def get_all_balances(self) -> dict:
        return self.sim.wallet.balances

    # --- Trading Methods ---
    def create_order(self, symbol: str, side: str, order_type: str, quantity: float, price: float = None):
        \"\"\"
        Mimics creating an order on an exchange.
        Currently supports 'MARKET' orders mainly.
        \"\"\"
        # For simulation simplicity in Phase 4, we treat LIMIT as MARKET execution at current price
        # (A real backtester would check if Low <= Price <= High)
        
        # Validations
        current_price = self.get_ticker_price(symbol)
        if current_price <= 0:
            logger.error("❌ Cannot place order: Market price is 0 (Simulation not started?)")
            return None

        logger.info(f"⚡ Requesting Order: {side} {quantity} {symbol} (Type: {order_type})")
        
        try:
            # Delegate execution to the Simulator Core
            self.sim.execute_trade(symbol, side, quantity)
            
            # Return a fake order structure (like CCXT/Exchange API returns)
            return {
                "symbol": symbol,
                "id": f"sim-order-{self.sim.steps_count}",
                "side": side,
                "amount": quantity,
                "price": current_price,
                "status": "closed", # Instant execution
                "filled": quantity
            }
        except Exception as e:
            logger.error(f"❌ Order Failed: {e}")
            return None
"""

# 2. The Test Script for Phase 4
RUN_TEST_SCRIPT = """
import os
import sys
import requests
import logging
from dotenv import load_dotenv

sys.path.append(os.getcwd())

from tests.core.virtual_wallet import VirtualWallet
from tests.core.data_engine import CsvCandlePlayer
from tests.core.simulator import MarketSimulator
from tests.core.test_provider import TestSimulatorProvider

logging.basicConfig(level=logging.INFO, format='%(name)s - %(message)s')
load_dotenv()

TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

def send_telegram(msg):
    if not TOKEN or not CHAT_ID: return
    try:
        requests.post(f"https://api.telegram.org/bot{TOKEN}/sendMessage", 
                      json={"chat_id": CHAT_ID, "text": msg, "parse_mode": "Markdown"}, timeout=5)
    except: pass

def main():
    print("🚀 STARTING PHASE 4: PROVIDER ADAPTER TEST")

    # 1. Setup Environment
    csv_path = os.path.join("tests", "data", "candles", "SOL_M15.csv")
    if not os.path.exists(csv_path):
        # Fallback search
        import glob
        files = glob.glob("tests/data/**/*.csv", recursive=True)
        if files: csv_path = files[0]
        else:
            print("❌ No CSV data found.")
            sys.exit(1)

    print(f"📂 Data: {csv_path}")

    # 2. Init Core Modules
    wallet = VirtualWallet(initial_balances={"USDT": 2000.0}) # Start with $2000
    data = CsvCandlePlayer(csv_path)
    sim = MarketSimulator(wallet, data)
    
    # 3. Init The Adapter (The Star of Phase 4)
    provider = TestSimulatorProvider(sim)
    print("✅ TestSimulatorProvider Initialized")

    # 4. Run "Strategy-Like" Loop
    print("⏳ Loop Started...")
    
    orders_placed = 0
    
    # Simulate a loop
    while sim.run_step():
        # "Strategy" Logic:
        # Check Price using PROVIDER (not simulator directly)
        price = provider.get_ticker_price("SOL")
        
        # Simple Logic: Buy on first candle, Sell on 50th
        if sim.steps_count == 1:
            print(f"   💡 Strategy Signal: BUY at ${price}")
            # Use PROVIDER to trade
            qty = 500.0 / price # Invest $500
            order = provider.create_order("SOL", "BUY", "MARKET", qty)
            if order:
                print(f"      ✅ Order ID: {order['id']} Filled")
                orders_placed += 1

        elif sim.steps_count == 50:
            print(f"   💡 Strategy Signal: SELL at ${price}")
            # Check balance using PROVIDER
            sol_balance = provider.get_balance("SOL")
            if sol_balance > 0:
                provider.create_order("SOL", "SELL", "MARKET", sol_balance)
                orders_placed += 1
    
    # 5. Report
    final_bal = provider.get_balance("USDT")
    pnl = final_bal - 2000.0
    
    print("-" * 30)
    print(f"💰 Final Balance: ${final_bal:.2f}")
    print(f"📈 PnL: ${pnl:.2f}")
    print(f"📝 Orders via Provider: {orders_placed}")
    print("-" * 30)

    msg = (
        "🔗 **Ocean Hunter: Phase 4 Complete**\\n\\n"
        "✅ **Provider Adapter Active**\\n"
        f"🔌 Class: `TestSimulatorProvider`\\n"
        f"📝 Orders Executed: {orders_placed}\\n"
        f"💵 PnL Test: `{pnl:.2f} USDT`\\n\\n"
        "System is now compatible with Strategy Runners."
    )
    send_telegram(msg)

if __name__ == "__main__":
    main()
"""

# ═══════════════════════════════════════════════════════════════
# CONFIGURATION
# ═══════════════════════════════════════════════════════════════
NEW_FILES = {
    "tests/core/test_provider.py": PROVIDER_CODE,
    "run_phase4.py": RUN_TEST_SCRIPT
}

# ═══════════════════════════════════════════════════════════════
# EXECUTION
# ═══════════════════════════════════════════════════════════════
def main():
    print("\n" + "═" * 50)
    print(f"🔧 BUILD Phase 4: Test Simulator Provider")
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
        print("\n[3/4] 🏃 Running Phase 4 Test...")
        result = subprocess.run([VENV_PYTHON, os.path.join(ROOT, "run_phase4.py")], cwd=ROOT)
        
        if result.returncode != 0:
            raise Exception("Test Script Failed!")

        # 4. Git Sync
        print("\n[4/4] 🐙 Git Sync...")
        try:
            setup_git.setup()
            setup_git.sync("Phase 4: Provider Adapter Implementation")
            print("      ✅ Git Synced")
        except:
            print("      ⚠️ Git Warning (Ignored)")

    except Exception as e:
        print(f"\n💥 Critical Error: {e}")

    finally:
        # Cleanup
        if os.path.exists(os.path.join(ROOT, "run_phase4.py")):
            os.remove(os.path.join(ROOT, "run_phase4.py"))

if __name__ == "__main__":
    main()
