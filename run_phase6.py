
import os
import sys
import requests
import logging
from dotenv import load_dotenv

sys.path.append(os.getcwd())

from tests.runners.backtest_runner import BacktestRunner
from tests.strategies.smart_sniper import SmartSniperStrategy

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
    print("🚀 STARTING PHASE 6: SMART SNIPER INJECTION")
    
    # Locate Data
    csv_path = os.path.join("tests", "data", "candles", "SOL_M15.csv")
    if not os.path.exists(csv_path):
        import glob
        files = glob.glob("tests/data/**/*.csv", recursive=True)
        if files: csv_path = files[0]
        else:
            print("❌ No CSV found."); sys.exit(1)

    # Init Runner with $1000
    runner = BacktestRunner(csv_path, initial_capital=1000.0, symbol="SOL")
    
    # Run with REAL Smart Sniper Strategy
    stats = runner.run(SmartSniperStrategy)
    
    # Report
    print("-" * 30)
    print(f"📊 REPORT FOR {stats['symbol']} (Smart Sniper V10.8.2)")
    print(f"💰 Start Capital: ${stats['initial_capital']:.2f}")
    print(f"🏁 Final Equity: ${stats['final_equity']:.2f}")
    print(f"📈 PnL: ${stats['pnl']:.2f} ({stats['roi']:.2f}%)")
    print(f"🔢 Trades Executed: {stats['simulated_trades']}")
    print("-" * 30)
    
    msg = (
        "🧠 **Ocean Hunter: Phase 6 Complete**\n\n"
        "✅ **Strategy Injection Successful**\n"
        "🔫 Model: `Smart Sniper V10.8.2`\n"
        f"📊 Symbol: `{stats['symbol']}`\n"
        f"💰 Equity: `{stats['final_equity']:.2f} USDT`\n"
        f"📈 ROI: `{stats['roi']:.2f}%`\n"
        f"🔢 Trades: `{stats['simulated_trades']}`\n\n"
        "Ready for Stress Test (Phase 7)."
    )
    send_telegram(msg)

if __name__ == "__main__":
    main()
