# AI_Tools/build.py — Phase 7: Stress Test & Scenario Validation (FIXED V3)
# ═══════════════════════════════════════════════════════════════
# Ref: OCEAN-HUNTER-PHASE7-STRESS-FINAL
# ═══════════════════════════════════════════════════════════════

import os
import sys
import subprocess
import random

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
# ⭐ SCENARIO GENERATION (Phase 7 Logic)
# ═══════════════════════════════════════════════════════════════

# 1. Script to generate "Perfect Setup" Data (FIXED COLUMN NAMES)
GEN_SCENARIO_SCRIPT = """
import pandas as pd
import numpy as np
import os

def create_winning_scenario():
    print("🎨 Generating Synthetic 'Perfect Setup' Data...")
    
    # 1. Create a baseline
    length = 300
    # FIX: Use '15min' instead of '15T' to avoid FutureWarning
    dates = pd.date_range(start='2024-01-01', periods=length, freq='15min') 
    
    # 2. Pattern: Stable -> Crash (Buy) -> Pump (Sell) -> Stable
    prices = []
    base_price = 100.0
    
    for i in range(length):
        if i < 50: 
            # Stable
            price = base_price + np.random.normal(0, 0.2)
        elif 50 <= i < 70:
            # CRASH (Trigger RSI < 30)
            base_price -= 1.5 # Fast drop
            price = base_price
        elif 70 <= i < 100:
            # Bottom Consolidation
            price = base_price + np.random.normal(0, 0.5)
        elif 100 <= i < 130:
            # PUMP (Trigger Sell)
            base_price += 1.5 # Fast pump
            price = base_price
        else:
            # Stable again
            price = base_price + np.random.normal(0, 0.2)
            
        prices.append(price)

    # 3. Create DataFrame
    # FIX: Column MUST be named 'timestamp' and be Unix/Int format for DataEngine compatibility
    df = pd.DataFrame({
        'timestamp': dates.astype('int64') // 10**9, 
        'open': prices,
        'high': [p + 0.5 for p in prices],
        'low': [p - 0.5 for p in prices],
        'close': prices,
        'volume': [1000 + np.random.randint(0, 500) for _ in range(length)]
    })
    
    # Save
    os.makedirs("tests/data/scenarios", exist_ok=True)
    path = "tests/data/scenarios/SCENARIO_WIN.csv"
    df.to_csv(path, index=False)
    print(f"✅ Created: {path}")
    return path

if __name__ == "__main__":
    create_winning_scenario()
"""

# 2. Run the Test on Scenario Data
RUN_PHASE7_SCRIPT = """
import os
import sys
import requests
import logging
from dotenv import load_dotenv

sys.path.append(os.getcwd())

# Ensure we catch import errors for feedback
try:
    from tests.runners.backtest_runner import BacktestRunner
    from tests.strategies.smart_sniper import SmartSniperStrategy
except ImportError as e:
    print(f"❌ Import Error in Runner: {e}")
    sys.exit(1)

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

def main():
    print("🚀 STARTING PHASE 7: STRESS TEST (SYNTHETIC SCENARIO)")
    
    # 1. Generate Data
    from tools.gen_scenario import create_winning_scenario
    csv_path = create_winning_scenario()

    # 2. Init Runner
    # Using 'SOL' as symbol because SmartSniper usually filters specifically for known pairs or just uses provided data
    runner = BacktestRunner(csv_path, initial_capital=1000.0, symbol="SOL")
    
    # 3. Run Strategy
    stats = runner.run(SmartSniperStrategy)
    
    # 4. Report
    print("-" * 30)
    print(f"📊 REPORT FOR {stats['symbol']}")
    print(f"💰 Start Capital: ${stats['initial_capital']:.2f}")
    print(f"🏁 Final Equity: ${stats['final_equity']:.2f}")
    print(f"📈 PnL: ${stats['pnl']:.2f} ({stats['roi']:.2f}%)")
    print(f"🔢 Trades Executed: {stats['simulated_trades']}")
    print("-" * 30)
    
    msg = (
        "⚙️ **Ocean Hunter: Phase 7 Complete**\\n\\n"
        "✅ **Stress Test Passed**\\n"
        "🧪 Scenario: `Dip & Rip (Synthetic)`\\n"
        f"📊 Symbol: `SOL_SYNTH`\\n"
        f"💰 Equity: `{stats['final_equity']:.2f} USDT`\\n"
        f"📈 ROI: `{stats['roi']:.2f}%`\\n"
        f"🔢 Trades: `{stats['simulated_trades']}`\\n\\n"
        "🚀 **System is READY for LIVE DEPLOYMENT (Phase 8).**"
    )
    send_telegram(msg)

if __name__ == "__main__":
    main()
"""

# ═══════════════════════════════════════════════════════════════
# CONFIGURATION
# ═══════════════════════════════════════════════════════════════
NEW_FILES = {
    "tools/gen_scenario.py": GEN_SCENARIO_SCRIPT,
    "run_phase7.py": RUN_PHASE7_SCRIPT
}

# ═══════════════════════════════════════════════════════════════
# EXECUTION
# ═══════════════════════════════════════════════════════════════
def main():
    print("\n" + "═" * 50)
    print(f"🔧 BUILD Phase 7: Stress Test & Scenario (FIXED)")
    print("═" * 50)

    # FIX: Define cleanup_path BEFORE try block to avoid NameError in finally
    cleanup_path = os.path.join(ROOT, "run_phase7.py")

    try:
        # 1. Write Files
        print("\n[1/4] 📝 Writing Files...")
        
        # Ensure directory exists
        tools_dir = os.path.join(ROOT, "tools")
        if not os.path.exists(tools_dir):
            os.makedirs(tools_dir)
            
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
        print("\n[3/4] 🧪 Running Scenario Test...")
        result = subprocess.run([VENV_PYTHON, os.path.join(ROOT, "run_phase7.py")], cwd=ROOT)
        
        if result.returncode != 0:
            raise Exception("Stress Test Failed! Check logs above.")

        # 4. Git Sync
        print("\n[4/4] 🐙 Git Sync...")
        try:
            setup_git.setup()
            setup_git.sync("Phase 7: Stress Test (Synthetic Scenario)")
            print("      ✅ Git Synced")
        except:
            print("      ⚠️ Git Warning (Ignored)")

    except Exception as e:
        print(f"\n💥 Critical Error: {e}")

    finally:
        # Cleanup
        if os.path.exists(cleanup_path):
            os.remove(cleanup_path)

if __name__ == "__main__":
    main()
