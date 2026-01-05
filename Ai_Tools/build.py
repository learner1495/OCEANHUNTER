# AI_Tools/build.py — Phase 18: DCA Logic + Aggressive Test
# ═══════════════════════════════════════════════════════════════
# Ref: PHASE-18-DCA-TEST
# ═══════════════════════════════════════════════════════════════

import os
import sys
import subprocess
import time

# ═══════════════════════════════════════════════════════════════
# 1. SETUP PATHS
# ═══════════════════════════════════════════════════════════════
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(SCRIPT_DIR)
sys.path.append(SCRIPT_DIR)

try:
    import context_gen
    import setup_git
except ImportError:
    pass

VENV_PYTHON = os.path.join(PROJECT_ROOT, ".venv", "Scripts", "python.exe")

# ═══════════════════════════════════════════════════════════════
# 2. THE BOT LOGIC (With DCA & Lower Threshold)
# ═══════════════════════════════════════════════════════════════

BOT_CONTENT = r'''
import os
import time
import requests
import statistics
from datetime import datetime
from dotenv import load_dotenv

# Load Environment
load_dotenv()

# ════════════════ CONFIG ════════════════
SYMBOL = "BTCUSDT"
TIMEFRAME = "1m"
# TEMPORARY: Lower threshold to FORCE a trade for testing
ENTRY_THRESHOLD = 40  # Was 70. Set to 40 so it buys immediately.
TAKE_PROFIT_PCT = 0.0015  # 0.15% Target for quick scalp test
STOP_LOSS_PCT = 0.10      # Deep stop loss to allow DCA to work

# DCA SETTINGS (Based on Architecture)
DCA_LAYERS = [
    {"drop": 0.005, "mult": 1.5},  # Layer 1: Drop 0.5% -> Buy 1.5x (TEST SETTING)
    {"drop": 0.010, "mult": 2.0},  # Layer 2: Drop 1.0% -> Buy 2.0x (TEST SETTING)
]
# Note: Real architecture has 3%, 6% drops. I reduced them for FAST testing.

# API CONFIG
TG_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
TG_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")
PROXY_URL = os.getenv("HTTPS_PROXY", "http://127.0.0.1:10809")
PROXIES = {"http": PROXY_URL, "https": PROXY_URL}

# ════════════════ VIRTUAL WALLET (Advanced) ════════════════
class PaperWallet:
    def __init__(self, initial_balance=1000.0):
        self.balance = initial_balance
        self.position = None 
        # position structure: {entry_price, amount, avg_price, layer}

    def buy(self, price, score, amount_usd=None):
        timestamp = datetime.now().strftime("%H:%M:%S")
        
        # Initial Entry
        if not self.position:
            buy_amount = 100.0 # Start with $100
            coin_amount = buy_amount / price
            self.balance -= buy_amount
            
            self.position = {
                "avg_price": price,
                "total_coins": coin_amount,
                "invested": buy_amount,
                "layer": 0,
                "time": timestamp
            }
            return "ENTRY", buy_amount

        # DCA Entry
        else:
            # Calculate next layer amount
            current_layer = self.position["layer"]
            if current_layer >= len(DCA_LAYERS): return False, 0
            
            multiplier = DCA_LAYERS[current_layer]["mult"]
            buy_amount = self.position["invested"] * (multiplier - 1) # Simplified DCA sizing
            
            # Check funds
            if self.balance < buy_amount:
                print("⚠️ Not enough funds for DCA!")
                return False, 0
                
            coin_amount = buy_amount / price
            self.balance -= buy_amount
            
            # Update Averages
            total_coins = self.position["total_coins"] + coin_amount
            total_invested = self.position["invested"] + buy_amount
            new_avg = total_invested / total_coins
            
            self.position["avg_price"] = new_avg
            self.position["total_coins"] = total_coins
            self.position["invested"] = total_invested
            self.position["layer"] += 1
            
            return f"DCA-{current_layer+1}", buy_amount

    def sell(self, price, reason):
        if not self.position: return False
        
        amount = self.position["total_coins"]
        revenue = amount * price
        invested = self.position["invested"]
        pnl = revenue - invested
        pnl_pct = (pnl / invested) * 100
        
        self.balance += revenue
        old_pos = self.position
        self.position = None
        return old_pos, pnl, pnl_pct

wallet = PaperWallet()

# ════════════════ TELEGRAM ════════════════
def send_telegram(msg):
    if not TG_TOKEN: return
    url = f"https://api.telegram.org/bot{TG_TOKEN}/sendMessage"
    payload = {"chat_id": TG_CHAT_ID, "text": msg, "parse_mode": "HTML"}
    try:
        requests.post(url, json=payload, proxies=PROXIES, timeout=5)
    except: pass

# ════════════════ MARKET DATA ════════════════
def get_market_data():
    base_url = "https://api.mexc.com/api/v3/klines"
    params = {"symbol": SYMBOL, "interval": TIMEFRAME, "limit": 50}
    try:
        resp = requests.get(base_url, params=params, proxies=PROXIES, timeout=5)
        return resp.json()
    except: return None

# ════════════════ INDICATORS ════════════════
def calculate_indicators(klines):
    closes = [float(k[4]) for k in klines]
    current_price = closes[-1]
    
    # RSI
    period = 14
    deltas = [closes[i] - closes[i-1] for i in range(1, len(closes))]
    gains = [d if d > 0 else 0 for d in deltas]
    losses = [abs(d) if d < 0 else 0 for d in deltas]
    avg_gain = sum(gains[-period:]) / period
    avg_loss = sum(losses[-period:]) / period
    rs = avg_gain / avg_loss if avg_loss != 0 else 0
    rsi = 100 - (100 / (1 + rs))
    
    # Score Logic
    score = 45 # Baseline
    if rsi < 40: score += 20
    elif rsi < 55: score += 10 # Boost score for testing
    if closes[-1] > closes[-2]: score += 10
    
    return {"price": current_price, "rsi": rsi, "score": score}

# ════════════════ MAIN LOOP ════════════════
def main():
    os.system('cls' if os.name == 'nt' else 'clear')
    print(f"🧪 AGGRESSIVE TEST MODE: Threshold {ENTRY_THRESHOLD}")
    print(f"💰 Wallet: ${wallet.balance}")
    send_telegram(f"🧪 <b>TEST MODE STARTED</b>\nEntry Threshold: {ENTRY_THRESHOLD}")

    while True:
        try:
            data = get_market_data()
            if not data:
                time.sleep(2)
                continue
                
            ind = calculate_indicators(data)
            price = ind['price']
            score = ind['score']
            rsi = round(ind['rsi'], 1)
            t = datetime.now().strftime("%H:%M:%S")

            # 1. MANAGE POSITION
            if wallet.position:
                avg = wallet.position['avg_price']
                pnl_pct = (price - avg) / avg
                layer = wallet.position['layer']
                
                # Check DCA
                next_layer_idx = layer
                if next_layer_idx < len(DCA_LAYERS):
                    trigger_drop = DCA_LAYERS[next_layer_idx]["drop"]
                    # If price drops below trigger %
                    if pnl_pct <= -trigger_drop:
                        type_str, amt = wallet.buy(price, score)
                        if type_str:
                            print(f"\n📉 DCA TRIGGERED! Bought ${amt} @ {price}")
                            send_telegram(f"📉 <b>DCA LEVEL {layer+1}</b>\nNew Avg: {wallet.position['avg_price']:.2f}")

                # Check Profit
                if pnl_pct >= TAKE_PROFIT_PCT:
                    pos, pnl, pct = wallet.sell(price, "TP")
                    print(f"\n🎉 TAKE PROFIT! ${pnl:.2f} ({pct:.2f}%)")
                    send_telegram(f"✅ <b>PROFIT SECURED</b>\nAmount: ${pnl:.2f}\nBal: ${wallet.balance:.2f}")

                # Status Line
                color = "\033[92m" if pnl_pct > 0 else "\033[91m"
                print(f"[{t}] 🔓 POS (L{layer}) | Price: {price} | Avg: {avg:.2f} | PnL: {color}{pnl_pct*100:.2f}%\033[0m")

            # 2. SEARCH FOR ENTRY
            else:
                s_color = "\033[92m" if score >= ENTRY_THRESHOLD else "\033[90m"
                print(f"[{t}] 🔎 {price} | Score: {s_color}{score}\033[0m | RSI: {rsi}")
                
                if score >= ENTRY_THRESHOLD:
                    type_str, amt = wallet.buy(price, score)
                    print(f"\n🚀 ENTERING TRADE! Bought ${amt} @ {price}")
                    send_telegram(f"🚀 <b>BUY SIGNAL</b>\nPrice: {price}\nScore: {score}")

            time.sleep(3)
            
        except KeyboardInterrupt:
            break
        except Exception as e:
            print(f"Error: {e}")
            time.sleep(5)

if __name__ == "__main__":
    main()
'''

# ═══════════════════════════════════════════════════════════════
# 3. BUILD PROCESS
# ═══════════════════════════════════════════════════════════════

def main():
    print(f"\n[1/3] 🧪 Installing Test Logic (DCA + Low Threshold)...")
    
    bot_path = os.path.join(PROJECT_ROOT, "run_bot.py")
    with open(bot_path, "w", encoding="utf-8") as f:
        f.write(BOT_CONTENT)
    
    print("      ✅ Mode: AGGRESSIVE TESTING")

    print("\n[2/3] 📚 Git Sync...")
    if 'context_gen' in sys.modules:
        context_gen.create_context_file()
    if 'setup_git' in sys.modules:
        setup_git.sync("Phase 18: DCA Test Mode")
    
    print("\n[3/3] 🏁 Launching Bot...")
    time.sleep(2)
    if sys.platform == "win32":
        bat_path = os.path.join(PROJECT_ROOT, "run_dashboard.bat")
        os.system(f'start "" "{bat_path}"')
    else:
        subprocess.run([VENV_PYTHON, "run_dashboard.py"], cwd=PROJECT_ROOT)

if __name__ == "__main__":
    main()
