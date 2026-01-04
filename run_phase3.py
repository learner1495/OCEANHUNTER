
import os
import sys
import requests
import logging
from dotenv import load_dotenv

# Add project root to sys.path
sys.path.append(os.getcwd())

from tests.core.virtual_wallet import VirtualWallet
from tests.core.data_engine import CsvCandlePlayer
from tests.core.simulator import MarketSimulator

# Setup Logging
logging.basicConfig(level=logging.INFO, format='%(name)s - %(message)s')
load_dotenv()

TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

def find_correct_csv():
    # Priority 1: Generated Test Data (Standard Format)
    priority_path = os.path.join("tests", "data", "candles", "SOL_M15.csv")
    if os.path.exists(priority_path):
        return priority_path
        
    # Priority 2: Any CSV in tests/data
    for root, dirs, files in os.walk("tests/data"):
        for file in files:
            if file.endswith(".csv"):
                return os.path.join(root, file)
                
    return None

def send_telegram(msg):
    if not TOKEN or not CHAT_ID:
        return
    try:
        url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
        requests.post(url, json={"chat_id": CHAT_ID, "text": msg, "parse_mode": "Markdown"}, timeout=10)
    except:
        pass

def main():
    print("🚀 STARTING PHASE 3: INTEGRATION TEST (V2)")
    
    csv_file = find_correct_csv()
    if not csv_file:
        print("❌ ERROR: No Test Data found! Run 'python setup_test_data.py' first.")
        sys.exit(1)
        
    print(f"📂 Using Data: {csv_file}")

    try:
        # 1. Init System
        wallet = VirtualWallet(initial_balances={"USDT": 1000.0})
        data = CsvCandlePlayer(csv_file)
        sim = MarketSimulator(wallet, data)

        # 2. Run Simulation
        print("⏳ Running Simulation Loop...")
        
        # Step 1: Advance & BUY
        if sim.run_step():
            price_start = sim.get_market_price()
            print(f"   🔹 Start Price: ${price_start}")
            
            # Buy ~ $100
            qty = round(100.0 / price_start, 4)
            sim.execute_trade("SOL", "BUY", qty)

        # Step 2: Fast forward
        last_price = 0
        candles_processed = 0
        while sim.run_step():
            last_price = sim.get_market_price()
            candles_processed += 1
            
        # Step 3: SELL
        print(f"   🔹 End Price: ${last_price} (Processed {candles_processed} candles)")
        sim.execute_trade("SOL", "SELL", qty)
        
        # 3. Results
        final_usdt = wallet.get_balance("USDT")
        pnl = final_usdt - 1000.0
        pnl_percent = (pnl / 1000.0) * 100
        
        print("-" * 30)
        print(f"💰 Final Balance: ${final_usdt:.2f}")
        print(f"MEG PnL: ${pnl:.2f} ({pnl_percent:.2f}%)")
        print("-" * 30)

        # 4. Report
        msg = (
            "🔗 **Ocean Hunter: Phase 3 Complete**\n\n"
            "✅ **Integration Successful**\n"
            f"📂 Data: `{os.path.basename(csv_file)}`\n"
            f"🕯 Candles: {candles_processed}\n"
            f"💵 PnL: `{pnl:.2f} USDT` ({pnl_percent:.2f}%)\n\n"
            "Simulator Core is Stable. Ready for Strategy."
        )
        send_telegram(msg)
        
    except Exception as e:
        print(f"❌ Runtime Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
