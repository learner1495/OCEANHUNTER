# AI_Tools/build.py — Phase 6: Strategy Injection (Smart Sniper V10.8.2)
# ══════════════════════════════════════════════════════════════════════
# Ref: OCEAN-HUNTER-PHASE6-STRATEGY
# ══════════════════════════════════════════════════════════════════════

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
# ⭐ STRATEGY LOGIC (Phase 6)
# ═══════════════════════════════════════════════════════════════

SMART_SNIPER_CODE = """
import pandas as pd
import numpy as np
import logging

class SmartSniperStrategy:
    \"\"\"
    🌊 Ocean Hunter Strategy: Smart Sniper V10.8.2
    
    Logic:
    1. Indicators: RSI(14), MACD(12,26,9), Bollinger Bands(20, 2std)
    2. Entry: Score-based system (RSI Dip + BB Touch + MACD Histogram)
    3. Exit: Fixed TP/SL or RSI Overbought
    \"\"\"
    def __init__(self, provider, symbol, risk_per_trade=0.98):
        self.provider = provider
        self.symbol = symbol
        self.risk_per_trade = risk_per_trade # Use 98% of available balance
        
        # History Buffer for Calculation
        self.history = []
        self.warmup_period = 35 # Min candles needed for MACD/RSI
        
        # Position Management
        self.position_size = 0.0
        self.entry_price = 0.0
        
        # Risk Settings
        self.tp_percent = 0.015  # 1.5% Target
        self.sl_percent = 0.010  # 1.0% Stop Loss

    def _calculate_indicators(self, df):
        \"\"\"Calculates Technical Indicators on the DataFrame\"\"\"
        # RSI
        delta = df['close'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
        rs = gain / loss
        df['rsi'] = 100 - (100 / (1 + rs))
        
        # Bollinger Bands
        df['bb_mid'] = df['close'].rolling(window=20).mean()
        df['bb_std'] = df['close'].rolling(window=20).std()
        df['bb_upper'] = df['bb_mid'] + (df['bb_std'] * 2)
        df['bb_lower'] = df['bb_mid'] - (df['bb_std'] * 2)
        
        # MACD
        exp12 = df['close'].ewm(span=12, adjust=False).mean()
        exp26 = df['close'].ewm(span=26, adjust=False).mean()
        df['macd'] = exp12 - exp26
        df['signal'] = df['macd'].ewm(span=9, adjust=False).mean()
        
        return df.iloc[-1] # Return only the latest row

    def on_candle(self, candle):
        \"\"\"Main Logic Loop called on every new candle\"\"\"
        # 1. Update History
        self.history.append({
            'open': candle['open'],
            'high': candle['high'],
            'low': candle['low'],
            'close': candle['close'],
            'volume': candle['volume']
        })
        
        # Keep history manageable (last 100 candles is enough)
        if len(self.history) > 100:
            self.history.pop(0)
            
        # 2. Warmup Check
        if len(self.history) < self.warmup_period:
            return

        # 3. Calculate Indicators
        df = pd.DataFrame(self.history)
        latest = self._calculate_indicators(df)
        
        current_price = latest['close']
        rsi = latest['rsi']
        
        # 4. Check Exit Conditions (If we have a position)
        if self.position_size > 0:
            self._check_exit(current_price, rsi)
            return

        # 5. Check Entry Conditions (If we have NO position)
        self._check_entry(latest)

    def _check_entry(self, latest):
        score = 0
        price = latest['close']
        
        # ─── SCORING SYSTEM ───
        
        # A. RSI Condition (Oversold)
        if latest['rsi'] < 30:
            score += 40
        elif latest['rsi'] < 40:
            score += 20
            
        # B. Bollinger Band Condition (Dip)
        if price <= latest['bb_lower']:
            score += 30 # Strong Signal: Touching Lower Band
        elif price <= (latest['bb_lower'] * 1.005):
            score += 10 # Near Lower Band
            
        # C. MACD Condition (Momentum)
        if latest['macd'] > latest['signal']:
            score += 10 # Bullish Momentum

        # ─── EXECUTION ───
        THRESHOLD = 50 
        
        if score >= THRESHOLD:
            balance = self.provider.get_balance("USDT")
            if balance > 10:
                amount_to_spend = balance * self.risk_per_trade
                qty = amount_to_spend / price
                
                print(f"   ⚡ SIGNAL FIRED (Score: {score}) | RSI: {latest['rsi']:.1f} | Price: {price:.2f}")
                self.provider.create_order(self.symbol, "BUY", "MARKET", qty)
                
                self.position_size = qty
                self.entry_price = price

    def _check_exit(self, current_price, rsi):
        # Calculate PnL %
        pnl_pct = (current_price - self.entry_price) / self.entry_price
        
        exit_reason = None
        
        # 1. Take Profit
        if pnl_pct >= self.tp_percent:
            exit_reason = "✅ TP Hit"
            
        # 2. Stop Loss
        elif pnl_pct <= -self.sl_percent:
            exit_reason = "❌ SL Hit"
            
        # 3. RSI Overbought (Sniper Exit)
        elif rsi > 70 and pnl_pct > 0.005: # Only exit on RSI if in profit
            exit_reason = "⚠️ RSI Overbought"

        if exit_reason:
            print(f"   🔄 EXITING: {exit_reason} | PnL: {pnl_pct*100:.2f}%")
            self.provider.create_order(self.symbol, "SELL", "MARKET", self.position_size)
            self.position_size = 0.0
            self.entry_price = 0.0
"""

# Test Script for Phase 6
RUN_PHASE6_SCRIPT = """
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
        "🧠 **Ocean Hunter: Phase 6 Complete**\\n\\n"
        "✅ **Strategy Injection Successful**\\n"
        "🔫 Model: `Smart Sniper V10.8.2`\\n"
        f"📊 Symbol: `{stats['symbol']}`\\n"
        f"💰 Equity: `{stats['final_equity']:.2f} USDT`\\n"
        f"📈 ROI: `{stats['roi']:.2f}%`\\n"
        f"🔢 Trades: `{stats['simulated_trades']}`\\n\\n"
        "Ready for Stress Test (Phase 7)."
    )
    send_telegram(msg)

if __name__ == "__main__":
    main()
"""

# ═══════════════════════════════════════════════════════════════
# CONFIGURATION
# ═══════════════════════════════════════════════════════════════
NEW_FILES = {
    "tests/strategies/smart_sniper.py": SMART_SNIPER_CODE,
    "run_phase6.py": RUN_PHASE6_SCRIPT
}

# ═══════════════════════════════════════════════════════════════
# EXECUTION
# ═══════════════════════════════════════════════════════════════
def main():
    print("\n" + "═" * 50)
    print(f"🔧 BUILD Phase 6: Strategy Injection")
    print("═" * 50)

    try:
        # 1. Write Files
        print("\n[1/4] 📝 Writing Files...")
        
        # Ensure directory exists
        strat_dir = os.path.join(ROOT, "tests", "strategies")
        if not os.path.exists(strat_dir):
            os.makedirs(strat_dir)
            
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
        print("\n[3/4] 🧠 Running Smart Sniper Simulation...")
        result = subprocess.run([VENV_PYTHON, os.path.join(ROOT, "run_phase6.py")], cwd=ROOT)
        
        if result.returncode != 0:
            raise Exception("Strategy Test Failed!")

        # 4. Git Sync
        print("\n[4/4] 🐙 Git Sync...")
        try:
            setup_git.setup()
            setup_git.sync("Phase 6: Strategy Injection (Smart Sniper)")
            print("      ✅ Git Synced")
        except:
            print("      ⚠️ Git Warning (Ignored)")

    except Exception as e:
        print(f"\n💥 Critical Error: {e}")

    finally:
        # Cleanup
        cleanup_path = os.path.join(ROOT, "run_phase6.py")
        if os.path.exists(cleanup_path):
            os.remove(cleanup_path)

if __name__ == "__main__":
    main()
