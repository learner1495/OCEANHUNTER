# AI_Tools/build.py — Build V8.0 (Paper Trading Engine)
# ═══════════════════════════════════════════════════════════════

import os
import sys
import subprocess
import setup_git

# ═══════════════════════════════════════════════════════════════
# CONFIG
# ═══════════════════════════════════════════════════════════════
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(SCRIPT_DIR)
VENV_PATH = os.path.join(ROOT, ".venv")
if sys.platform == "win32":
    VENV_PYTHON = os.path.join(VENV_PATH, "Scripts", "python.exe")
else:
    VENV_PYTHON = os.path.join(VENV_PATH, "bin", "python")

# ═══════════════════════════════════════════════════════════════
# MODULE: TRADER (m_trader.py) - New Simulation Engine
# ═══════════════════════════════════════════════════════════════
M_TRADER_CONTENT = '''import json
import os
from datetime import datetime

class PaperTrader:
    def __init__(self, initial_balance=1000):
        self.state_file = "data/paper_state.json"
        self.initial_balance = initial_balance
        self.load_state()

    def load_state(self):
        """Loads the simulated wallet state"""
        if os.path.exists(self.state_file):
            with open(self.state_file, 'r') as f:
                self.state = json.load(f)
        else:
            self.state = {
                "usdt_balance": self.initial_balance,
                "positions": {},  # Format: {"BTCUSDT": {"amount": 0.1, "entry_price": 50000}}
                "history": []
            }
            self.save_state()

    def save_state(self):
        """Saves current wallet state"""
        os.makedirs("data", exist_ok=True)
        with open(self.state_file, 'w') as f:
            json.dump(self.state, f, indent=4)

    def execute(self, symbol, signal, price):
        """Executes a paper trade based on signal"""
        if "BUY" in signal:
            return self.buy(symbol, price)
        elif "SELL" in signal:
            return self.sell(symbol, price)
        return None

    def buy(self, symbol, price):
        # Only buy if we have USDT and no current position for this symbol
        if self.state["usdt_balance"] > 10 and symbol not in self.state["positions"]:
            # Invest 20% of available balance per trade
            trade_amount_usdt = self.state["usdt_balance"] * 0.20
            amount_crypto = trade_amount_usdt / price
            
            # Update State
            self.state["usdt_balance"] -= trade_amount_usdt
            self.state["positions"][symbol] = {
                "amount": amount_crypto,
                "entry_price": price,
                "time": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }
            
            log = f"🟢 PAPER BUY: {symbol} @ ${price} (Amt: {amount_crypto:.6f})"
            self.state["history"].append(log)
            self.save_state()
            return log
        return None

    def sell(self, symbol, price):
        # Only sell if we have a position
        if symbol in self.state["positions"]:
            pos = self.state["positions"][symbol]
            amount = pos["amount"]
            revenue = amount * price
            profit = revenue - (amount * pos["entry_price"])
            
            # Update State
            self.state["usdt_balance"] += revenue
            del self.state["positions"][symbol]
            
            log = f"🔴 PAPER SELL: {symbol} @ ${price} | PnL: ${profit:.2f}"
            self.state["history"].append(log)
            self.save_state()
            return log
        return None
        
    def get_portfolio_value(self, current_prices):
        """Calculates total value (USDT + Assets)"""
        total = self.state["usdt_balance"]
        for sym, pos in self.state["positions"].items():
            current_price = current_prices.get(sym, pos["entry_price"])
            total += pos["amount"] * current_price
        return total
'''

# ═══════════════════════════════════════════════════════════════
# MAIN APP UPDATE (main.py) - Integrate Trader
# ═══════════════════════════════════════════════════════════════
MAIN_CONTENT = '''import os
import time
import requests
import urllib3
from dotenv import load_dotenv
from modules.m_data import DataEngine
from modules.m_analysis import analyze_market
from modules.m_trader import PaperTrader

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
load_dotenv()

# --- CONFIG ---
TG_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
TG_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")
PROXY_URL = "http://127.0.0.1:10809"
PROXIES = {"http": PROXY_URL, "https": PROXY_URL}

def send_telegram(msg):
    if not TG_TOKEN or not TG_CHAT_ID: return
    url = f"https://api.telegram.org/bot{TG_TOKEN}/sendMessage"
    payload = {"chat_id": TG_CHAT_ID, "text": msg}
    try:
        requests.post(url, json=payload, proxies=PROXIES, verify=False, timeout=5)
    except: pass

def main():
    print("-" * 50)
    print("📜 OCEAN HUNTER V8.0 — PAPER TRADING")
    print("-" * 50)
    
    engine = DataEngine()
    trader = PaperTrader(initial_balance=1000) # Start with $1000 Fake USDT
    
    targets = ["BTCUSDT", "ETHUSDT", "SOLUSDT", "BNBUSDT", "XRPUSDT"]
    current_prices = {}
    
    report_msg = "📜 PAPER TRADING REPORT (V8.0)\\n"
    report_msg += "Strategy: RSI (14) | Fake Balance: $1000\\n"
    report_msg += "─" * 25 + "\\n\\n"
    
    trade_logs = []

    for symbol in targets:
        # 1. Fetch Data
        candles = engine.fetch_candles(symbol, interval="60m", limit=50)
        
        if candles:
            # 2. Analyze
            result = analyze_market(symbol, candles)
            current_prices[symbol] = result['price']
            
            # 3. Execute Trade (Simulation)
            trade_action = trader.execute(symbol, result['signal'], result['price'])
            
            if trade_action:
                trade_logs.append(trade_action)
                print(f"   ⚡ ACTION: {trade_action}")
            
            # Format Report
            icon = "⚪"
            if "BUY" in result['signal']: icon = "🟢"
            elif "SELL" in result['signal']: icon = "🔴"
            
            line = f"{icon} {symbol.replace('USDT','')}: ${result['price']}\\n"
            line += f"   RSI: {result['rsi']} ({result['signal'].split()[0]})\\n"
            report_msg += line + "\\n"
        else:
            report_msg += f"❌ {symbol}: Connection Failed\\n"
            
    # 4. Portfolio Summary
    total_val = trader.get_portfolio_value(current_prices)
    roi = ((total_val - 1000) / 1000) * 100
    
    report_msg += "─" * 25 + "\\n"
    report_msg += f"💰 Wallet: ${trader.state['usdt_balance']:.2f}\\n"
    report_msg += f"📊 Net Worth: ${total_val:.2f} ({roi:+.2f}%)\\n"
    
    if trade_logs:
        report_msg += "\\n📝 NEW TRADES:\\n" + "\\n".join(trade_logs)
            
    print(f"\\n[4] 📨 Sending Report (Val: ${total_val:.2f})...")
    send_telegram(report_msg)
    print("✅ Done.")

if __name__ == "__main__":
    main()
'''

# ═══════════════════════════════════════════════════════════════
# BUILD STEPS
# ═══════════════════════════════════════════════════════════════
def main():
    print("\n🚀 BUILD V8.0 — PAPER TRADING ENGINE")
    
    # 1. Create Trader Module
    modules_dir = os.path.join(ROOT, "modules")
    with open(os.path.join(modules_dir, "m_trader.py"), "w", encoding="utf-8") as f:
        f.write(M_TRADER_CONTENT)
    print(f"   📝 Created modules/m_trader.py")
    
    # 2. Update Main
    with open(os.path.join(ROOT, "main.py"), "w", encoding="utf-8") as f:
        f.write(MAIN_CONTENT)
    print(f"   📝 Updated main.py")

    # 3. Git Sync
    try:
        setup_git.setup()
        setup_git.sync("Build V8.0: Added Paper Trading")
    except: pass

    # 4. Run
    print("\n" + "="*50)
    print("   RUNNING V8.0 SIMULATION...")
    print("="*50)
    subprocess.run([VENV_PYTHON, "main.py"], cwd=ROOT)

if __name__ == "__main__":
    main()
