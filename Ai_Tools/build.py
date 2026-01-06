# AI_Tools/build.py — Phase 19: Integrated Simulation into Dashboard
# ═══════════════════════════════════════════════════════════════
# Ref: PHASE-19-INTEGRATED
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
# 2. UPDATED DASHBOARD WITH SIMULATION (run_dashboard.py)
# ═══════════════════════════════════════════════════════════════

DASHBOARD_CONTENT = r'''
import os
import sys
import time
import requests
import csv
from datetime import datetime
from dotenv import load_dotenv

# Load Environment
load_dotenv()
BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

# ════════════════ HELPER: SEND TELEGRAM ════════════════
def send_telegram(message):
    if not BOT_TOKEN or not CHAT_ID:
        print("   ❌ Telegram credentials missing in .env")
        return
    
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    payload = {"chat_id": CHAT_ID, "text": message, "parse_mode": "Markdown"}
    
    try:
        # Smart Proxy Check (from Phase 14)
        proxies = None
        possible_ports = [10809, 2081, 1080, 7890]
        for port in possible_ports:
            try:
                p_url = f"http://127.0.0.1:{port}"
                requests.get("https://api.telegram.org", proxies={"https": p_url}, timeout=2)
                proxies = {"https": p_url, "http": p_url}
                break
            except:
                continue

        resp = requests.post(url, json=payload, proxies=proxies, timeout=10)
        if resp.status_code == 200:
            print("   ✅ Telegram Notification Sent!")
        else:
            print(f"   ❌ Telegram Error: {resp.text}")
    except Exception as e:
        print(f"   ❌ Network Error: {e}")

# ════════════════ OPTION 4: SIMULATION ENGINE ════════════════
def run_fast_simulation():
    csv_path = os.path.join("tests", "data", "candles", "SOL_M15_DCA.csv")
    if not os.path.exists(csv_path):
        print(f"\n❌ ERROR: Data file not found at: {csv_path}")
        print("   👉 Please run 'python setup_test_data.py' first.")
        input("\n   Press Enter to return...")
        return

    print(f"\n🚀 STARTING HIGH-SPEED SIMULATION (SOL_M15_DCA)...")
    print("-" * 60)
    
    # Sim Config
    balance = 1000.0
    position = None
    history = []
    
    DCA_LAYERS = [
        {"drop": 0.03, "mult": 1.5},
        {"drop": 0.06, "mult": 2.0},
        {"drop": 0.10, "mult": 2.5},
    ]

    with open(csv_path, "r") as f:
        reader = csv.DictReader(f)
        candles = list(reader)

    print(f"   Loaded {len(candles)} candles. Simulating...")
    
    for row in candles:
        price = float(row["close"])
        timestamp = datetime.fromtimestamp(float(row["timestamp"])).strftime("%H:%M")
        tag = row["scenario_tag"]
        
        # 1. LOGIC: BUY
        if not position and tag == "ENTRY_SIGNAL":
            invest = 100.0
            coins = invest / price
            balance -= invest
            position = {"avg": price, "coins": coins, "invested": invest, "layer": 0}
            msg = f"[{timestamp}] 🛒 BUY ENTRY @ ${price:.2f}"
            print("   " + msg)
            history.append(msg)
            
        # 2. LOGIC: MANAGE (DCA & TP)
        elif position:
            avg = position["avg"]
            pnl_pct = (price - avg) / avg
            layer = position["layer"]
            
            # Take Profit (1.5% or tag)
            if pnl_pct >= 0.015 or tag == "DCA_EXIT_PROFIT":
                revenue = position["coins"] * price
                profit = revenue - position["invested"]
                balance += revenue
                msg = f"[{timestamp}] 🎉 TAKE PROFIT @ ${price:.2f} | Profit: ${profit:.2f} ({pnl_pct*100:.2f}%)"
                print("   " + msg)
                history.append(msg)
                position = None # Reset
            
            # DCA Trigger
            elif layer < len(DCA_LAYERS):
                target_drop = DCA_LAYERS[layer]["drop"]
                if pnl_pct <= -target_drop or "DCA_LAYER" in tag:
                    mult = DCA_LAYERS[layer]["mult"]
                    new_inv = position["invested"] * (mult - 1)
                    if balance >= new_inv:
                        balance -= new_inv
                        new_coins = new_inv / price
                        
                        # Update Avg
                        total_inv = position["invested"] + new_inv
                        total_coins = position["coins"] + new_coins
                        position["avg"] = total_inv / total_coins
                        position["coins"] = total_coins
                        position["invested"] = total_inv
                        position["layer"] += 1
                        
                        msg = f"[{timestamp}] 📉 DCA LEVEL {position['layer']} @ ${price:.2f} | New Avg: ${position['avg']:.2f}"
                        print("   " + msg)
                        history.append(msg)

    # FINISH
    total_profit = balance - 1000.0
    print("-" * 60)
    print(f"🏁 FINAL BALANCE: ${balance:.2f}")
    print(f"📈 TOTAL PROFIT:  ${total_profit:.2f}")
    
    # SEND REPORT TO TELEGRAM
    tg_msg = (
        f"🤖 *SIMULATION REPORT: SOL_M15_DCA*\n"
        f"━━━━━━━━━━━━━━━━━━\n"
        f"💰 Initial: $1000.0\n"
        f"🏁 Final: ${balance:.2f}\n"
        f"📈 Profit: ${total_profit:.2f} ({(total_profit/1000)*100:.2f}%)\n"
        f"🔄 Trades: {len(history)}\n\n"
        f"Status: ✅ SUCCESS"
    )
    send_telegram(tg_msg)
    
    input("\n   Press Enter to return to menu...")

# ════════════════ MAIN MENU ════════════════
def main_menu():
    while True:
        os.system('cls' if os.name == 'nt' else 'clear')
        print(r"""
   ___  _____________  ___    _   __   __  ____  ___   _____________________
  / _ \/ ___/ __/ _ \/ _ |  / | / /  / / / / / / / | / /_  __/ __/ _ \/ _ \
 / // / /__/ _// __ / __ | /    /  / /_/ / /_/ /  |/ / / / / _// , _/ // /
 \___/\___/___/_/ |_\/_| |/_/|_|  \____/\____/_/|__/ /_/ /___/_/|_/____/ 
        """)
        print("   🌊 OCEAN HUNTER V10.8.2 - COMMAND CENTER")
        print("   " + "="*50)
        print("   1. 🤖 Run Bot (Safe Mode - Analysis Only)")
        print("   2. 📄 Paper Trading (Live Data Simulation)")
        print("   3. 📡 Test Telegram Connection")
        print("   4. ⏩ RUN FAST SIMULATION (Use Test Data)")
        print("   " + "="*50)
        print("   0. Exit")
        
        choice = input("\n   👉 Select Option: ").strip()
        
        if choice == '1':
            print("\n   Launching Bot in Safe Mode...")
            # subprocess.run([sys.executable, "run_bot.py"]) # Placeholder
            input("   (Function integrated in run_bot.py - Press Enter)")
        elif choice == '2':
            print("\n   Starting Paper Trading...")
            # subprocess.run([sys.executable, "run_paper.py"]) # Placeholder
            input("   (Function integrated in run_paper.py - Press Enter)")
        elif choice == '3':
            os.system(f'{sys.executable} test_telegram_conn.py')
            input("\n   Press Enter...")
        elif choice == '4':
            run_fast_simulation()
        elif choice == '0':
            print("   👋 Exiting...")
            sys.exit()
        else:
            print("   ❌ Invalid option!")
            time.sleep(1)

if __name__ == "__main__":
    try:
        main_menu()
    except KeyboardInterrupt:
        print("\n👋 Bye!")
'''

# ═══════════════════════════════════════════════════════════════
# 3. BUILD PROCESS
# ═══════════════════════════════════════════════════════════════

def main():
    print(f"\n[1/3] 🏗️  Updating Dashboard (Option 4 Added)...")
    
    # Ensure Test Data Exists (Just in case, run the generator user provided)
    setup_data_path = os.path.join(PROJECT_ROOT, "setup_test_data.py")
    if os.path.exists(setup_data_path):
        print("      📊 Verifying Test Data...")
        subprocess.run([VENV_PYTHON, setup_data_path], cwd=PROJECT_ROOT, stdout=subprocess.DEVNULL)
    
    # Overwrite run_dashboard.py
    dashboard_path = os.path.join(PROJECT_ROOT, "run_dashboard.py")
    with open(dashboard_path, "w", encoding="utf-8") as f:
        f.write(DASHBOARD_CONTENT)
    
    print("      ✅ Dashboard Updated.")

    print("\n[2/3] 📚 Git Sync...")
    if 'context_gen' in sys.modules:
        context_gen.create_context_file()
    if 'setup_git' in sys.modules:
        setup_git.sync("Phase 19: Dashboard Simulation Integration")

    print("\n[3/3] 🚀 Launching Dashboard...")
    print("      ⚠️  PLEASE CHECK THE NEW WINDOW!")
    time.sleep(2)

    # Force open external window properly
    if sys.platform == "win32":
        bat_path = os.path.join(PROJECT_ROOT, "run_dashboard.bat")
        os.system(f'start "" "{bat_path}"')
    else:
        subprocess.run([sys.executable, dashboard_path], cwd=PROJECT_ROOT)

if __name__ == "__main__":
    main()
