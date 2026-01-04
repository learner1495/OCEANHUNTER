
import os
import sys
import requests
import logging
from dotenv import load_dotenv

sys.path.append(os.getcwd())

from tests.core.virtual_wallet import VirtualWallet
from tests.core.data_engine import CsvCandlePlayer
from tests.core.simulator import MarketSimulator
from tests.core.test_provider import TestSimulatorProvider

logging.basicConfig(level=logging.INFO, format='%(name)s - %(message)s')
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
    print("🚀 STARTING PHASE 4: PROVIDER ADAPTER TEST")

    # 1. Setup Environment
    csv_path = os.path.join("tests", "data", "candles", "SOL_M15.csv")
    if not os.path.exists(csv_path):
        # Fallback search
        import glob
        files = glob.glob("tests/data/**/*.csv", recursive=True)
        if files: csv_path = files[0]
        else:
            print("❌ No CSV data found.")
            sys.exit(1)

    print(f"📂 Data: {csv_path}")

    # 2. Init Core Modules
    wallet = VirtualWallet(initial_balances={"USDT": 2000.0}) # Start with $2000
    data = CsvCandlePlayer(csv_path)
    sim = MarketSimulator(wallet, data)
    
    # 3. Init The Adapter (The Star of Phase 4)
    provider = TestSimulatorProvider(sim)
    print("✅ TestSimulatorProvider Initialized")

    # 4. Run "Strategy-Like" Loop
    print("⏳ Loop Started...")
    
    orders_placed = 0
    
    # Simulate a loop
    while sim.run_step():
        # "Strategy" Logic:
        # Check Price using PROVIDER (not simulator directly)
        price = provider.get_ticker_price("SOL")
        
        # Simple Logic: Buy on first candle, Sell on 50th
        if sim.steps_count == 1:
            print(f"   💡 Strategy Signal: BUY at ${price}")
            # Use PROVIDER to trade
            qty = 500.0 / price # Invest $500
            order = provider.create_order("SOL", "BUY", "MARKET", qty)
            if order:
                print(f"      ✅ Order ID: {order['id']} Filled")
                orders_placed += 1

        elif sim.steps_count == 50:
            print(f"   💡 Strategy Signal: SELL at ${price}")
            # Check balance using PROVIDER
            sol_balance = provider.get_balance("SOL")
            if sol_balance > 0:
                provider.create_order("SOL", "SELL", "MARKET", sol_balance)
                orders_placed += 1
    
    # 5. Report
    final_bal = provider.get_balance("USDT")
    pnl = final_bal - 2000.0
    
    print("-" * 30)
    print(f"💰 Final Balance: ${final_bal:.2f}")
    print(f"📈 PnL: ${pnl:.2f}")
    print(f"📝 Orders via Provider: {orders_placed}")
    print("-" * 30)

    msg = (
        "🔗 **Ocean Hunter: Phase 4 Complete**\n\n"
        "✅ **Provider Adapter Active**\n"
        f"🔌 Class: `TestSimulatorProvider`\n"
        f"📝 Orders Executed: {orders_placed}\n"
        f"💵 PnL Test: `{pnl:.2f} USDT`\n\n"
        "System is now compatible with Strategy Runners."
    )
    send_telegram(msg)

if __name__ == "__main__":
    main()
