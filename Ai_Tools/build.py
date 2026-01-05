# AI_Tools/build.py — Phase 17: Paper Trading Simulation
# ═══════════════════════════════════════════════════════════════
# Ref: PHASE-17-PAPER-TRADING
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
# 2. THE PAPER TRADING BOT (run_bot.py)
# ═══════════════════════════════════════════════════════════════

BOT_CONTENT = r'''
import os
import time
import requests
import statistics
import math
from datetime import datetime
from dotenv import load_dotenv

# Load Environment
load_dotenv()

# ════════════════ CONFIG ════════════════
SYMBOL = "BTCUSDT"
TIMEFRAME = "1m"
ENTRY_THRESHOLD = 70       # Enter if Score >= 70
TAKE_PROFIT_PCT = 1.5      # Sell if Profit >= 1.5%
STOP_LOSS_PCT = -2.0       # Sell if Loss >= 2.0% (Simulated Safety)

# API CONFIG
TG_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
TG_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")
PROXY_URL = os.getenv("HTTPS_PROXY", "http://127.0.0.1:10809")
PROXIES = {"http": PROXY_URL, "https": PROXY_URL}

# ════════════════ PAPER WALLET ════════════════
class PaperWallet:
    def __init__(self, initial_usdt=1000):
        self.usdt = initial_usdt
        self.btc = 0.0
        self.entry_price = 0.0
        self.in_position = False
        self.trades = 0

    def buy(self, price):
        if self.in_position: return False
        amount_to_buy = self.usdt  # All in for simulation
        self.btc = amount_to_buy / price
        self.usdt = 0
        self.entry_price = price
        self.in_position = True
        return True

    def sell(self, price, reason):
        if not self.in_position: return False
        sale_value = self.btc * price
        pnl = sale_value - (self.btc * self.entry_price)
        pnl_pct = (pnl / (self.btc * self.entry_price)) * 100
        
        self.usdt = sale_value
        self.btc = 0
        self.in_position = False
        self.trades += 1
        return pnl, pnl_pct

wallet = PaperWallet(initial_usdt=1000)

# ════════════════ TELEGRAM ════════════════
def send_telegram(msg):
    if not TG_TOKEN or not TG_CHAT_ID: return
    url = f"https://api.telegram.org/bot{TG_TOKEN}/sendMessage"
    payload = {"chat_id": TG_CHAT_ID, "text": msg, "parse_mode": "HTML"}
    try:
        requests.post(url, json=payload, timeout=5)
    except:
        try:
            requests.post(url, json=payload, proxies=PROXIES, timeout=5)
        except: pass

# ════════════════ MARKET DATA ════════════════
def get_market_data():
    base_url = "https://api.mexc.com/api/v3/klines"
    params = {"symbol": SYMBOL, "interval": TIMEFRAME, "limit": 50}
    try:
        resp = requests.get(base_url, params=params, timeout=5)
        return resp.json()
    except:
        try:
            resp = requests.get(base_url, params=params, proxies=PROXIES, timeout=5)
            return resp.json()
        except: return None

# ════════════════ INDICATORS ════════════════
def calculate_indicators(klines):
    if not klines: return None
    closes = [float(k[4]) for k in klines]
    opens = [float(k[1]) for k in klines]
    volumes = [float(k[5]) for k in klines]
    
    # RSI
    period = 14
    if len(closes) < period + 1: return None
    deltas = [closes[i] - closes[i-1] for i in range(1, len(closes))]
    gains = [d if d > 0 else 0 for d in deltas]
    losses = [abs(d) if d < 0 else 0 for d in deltas]
    avg_gain = sum(gains[-period:]) / period
    avg_loss = sum(losses[-period:]) / period
    rs = avg_gain / avg_loss if avg_loss != 0 else 0
    rsi = 100 - (100 / (1 + rs)) if avg_loss != 0 else 100

    # BB
    slice_data = closes[-20:]
    sma = sum(slice_data) / 20
    std = statistics.stdev(slice_data)
    bb_lower = sma - (2 * std)

    # Volume Spike
    curr_vol = volumes[-1]
    avg_vol = sum(volumes[-21:-1]) / 20
    vol_spike = curr_vol > (1.5 * avg_vol)

    return {
        "price": closes[-1],
        "rsi": rsi,
        "bb_lower": bb_lower,
        "vol_spike": vol_spike,
        "is_green": closes[-1] > opens[-1]
    }

# ════════════════ SCORING ════════════════
def get_score(data):
    score = 0
    reasons = []
    if data['rsi'] < 40: score += 20; reasons.append("RSI Oversold")
    if data['price'] < data['bb_lower']: score += 15; reasons.append("Below BB")
    if data['vol_spike']: score += 25; reasons.append("Vol Spike")
    if data['is_green']: score += 25; reasons.append("Bullish Candle")
    return score, reasons

# ════════════════ MAIN LOOP ════════════════
def main():
    os.system('cls' if os.name == 'nt' else 'clear')
    print("╔════════════════════════════════════════════════════╗")
    print(f"║ 📝 PAPER TRADING SIMULATION (SAFE MODE)          ║")
    print(f"║ 💰 Wallet: ${wallet.usdt:.2f} USDT                      ║")
    print("╚════════════════════════════════════════════════════╝")
    
    send_telegram("📝 <b>PAPER TRADING STARTED</b>\nSimulated Wallet: $1000")
    
    try:
        while True:
            klines = get_market_data()
            if klines:
                data = calculate_indicators(klines)
                score, reasons = get_score(data)
                price = data['price']
                
                # Console Output
                timestamp = datetime.now().strftime("%H:%M:%S")
                
                if wallet.in_position:
                    # CHECK FOR EXIT
                    curr_val = wallet.btc * price
                    pnl_pct = ((curr_val - 1000) / 1000) * 100 # Approx PnL based on initial
                    pnl_color = "\033[92m" if pnl_pct > 0 else "\033[91m"
                    
                    print(f"[{timestamp}] 💼 HOLDING | Price: {price} | PnL: {pnl_color}{pnl_pct:.2f}%\033[0m")
                    
                    # Exit Conditions
                    exit_msg = ""
                    if pnl_pct >= TAKE_PROFIT_PCT:
                        pnl, pct = wallet.sell(price, "Take Profit")
                        exit_msg = f"✅ <b>TAKE PROFIT</b> (+{pct:.2f}%)"
                    elif pnl_pct <= STOP_LOSS_PCT:
                        pnl, pct = wallet.sell(price, "Stop Loss")
                        exit_msg = f"🛑 <b>STOP LOSS</b> ({pct:.2f}%)"
                    
                    if exit_msg:
                        print(f"\n💰 {exit_msg} | New Balance: ${wallet.usdt:.2f}\n")
                        send_telegram(f"{exit_msg}\nPrice: {price}\nBalance: ${wallet.usdt:.2f}")

                else:
                    # CHECK FOR ENTRY
                    s_color = "\033[92m" if score >= ENTRY_THRESHOLD else "\033[90m"
                    print(f"[{timestamp}] 🔎 {price} | Score: {s_color}{score}/100\033[0m | RSI: {data['rsi']:.1f}")
                    
                    if score >= ENTRY_THRESHOLD:
                        wallet.buy(price)
                        msg = (f"🚀 <b>SIMULATED BUY</b>\n"
                               f"Price: {price}\n"
                               f"Score: {score}\n"
                               f"Reasons: {', '.join(reasons)}")
                        print(f"\n🛒 BUY EXECUTED at {price}\n")
                        send_telegram(msg)
            else:
                print("⚠️  Network glitch...", end='\r')
                
            time.sleep(10)

    except KeyboardInterrupt:
        print("\n🛑 Bot Stopped.")

if __name__ == "__main__":
    main()
'''

# ═══════════════════════════════════════════════════════════════
# 3. BUILD PROCESS
# ═══════════════════════════════════════════════════════════════

def main():
    print(f"\n[1/3] 📝 Upgrading to Paper Trading Mode...")
    
    bot_path = os.path.join(PROJECT_ROOT, "run_bot.py")
    with open(bot_path, "w", encoding="utf-8") as f:
        f.write(BOT_CONTENT)
    
    print("      ✅ Simulation logic installed.")

    print("\n[2/3] 📚 Git Sync...")
    if 'context_gen' in sys.modules:
        context_gen.create_context_file()
    if 'setup_git' in sys.modules:
        setup_git.sync("Phase 17: Paper Trading Integration")

    print("\n[3/3] 🏁 Launching Simulation...")
    time.sleep(2)
    if sys.platform == "win32":
        bat_path = os.path.join(PROJECT_ROOT, "run_dashboard.bat")
        os.system(f'start "" "{bat_path}"')
    else:
        subprocess.run([VENV_PYTHON, "run_dashboard.py"], cwd=PROJECT_ROOT)

if __name__ == "__main__":
    main()
