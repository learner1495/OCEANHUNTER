
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
    """
    A simple logic to test the Runner:
    - Buy if price drops 1% below previous close (Dip Buy)
    - Sell if price rises 1% above avg buy
    """
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
        "🏆 **Ocean Hunter: Phase 5 Complete**\n\n"
        "✅ **Backtest Runner Operational**\n"
        f"📊 Symbol: `{stats['symbol']}`\n"
        f"💰 Final Equity: `{stats['final_equity']:.2f} USDT`\n"
        f"📈 ROI: `{stats['roi']:.2f}%`\n\n"
        "Ready for REAL Strategy Injection (Smart Sniper)."
    )
    send_telegram(msg)

if __name__ == "__main__":
    main()
