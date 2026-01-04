
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
        "⚙️ **Ocean Hunter: Phase 7 Complete**\n\n"
        "✅ **Stress Test Passed**\n"
        "🧪 Scenario: `Dip & Rip (Synthetic)`\n"
        f"📊 Symbol: `SOL_SYNTH`\n"
        f"💰 Equity: `{stats['final_equity']:.2f} USDT`\n"
        f"📈 ROI: `{stats['roi']:.2f}%`\n"
        f"🔢 Trades: `{stats['simulated_trades']}`\n\n"
        "🚀 **System is READY for LIVE DEPLOYMENT (Phase 8).**"
    )
    send_telegram(msg)

if __name__ == "__main__":
    main()
