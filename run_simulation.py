
import os
import csv
import sys
from datetime import datetime

# ════════════════ CONFIG ════════════════
SCENARIO_FILE = os.path.join("tests", "data", "candles", "SOL_M15_DCA.csv")
INITIAL_BALANCE = 1000.0
TAKE_PROFIT_PCT = 0.015  # 1.5% Real Target
DCA_LAYERS = [
    {"drop": 0.03, "mult": 1.5},  # Layer 1: -3%
    {"drop": 0.06, "mult": 2.0},  # Layer 2: -6%
    {"drop": 0.10, "mult": 2.5},  # Layer 3: -10%
]

# ════════════════ VIRTUAL WALLET ════════════════
class SimWallet:
    def __init__(self, balance):
        self.balance = balance
        self.position = None
        self.history = []

    def buy(self, price, timestamp, reason="Entry"):
        if not self.position:
            # First Entry: Buy $100
            amt_usd = 100.0
            coins = amt_usd / price
            self.balance -= amt_usd
            self.position = {
                "avg_price": price, "coins": coins, "invested": amt_usd, "layer": 0
            }
            self.history.append(f"[{timestamp}] 🛒 BUY (Entry) @ {price} | Inv: ${amt_usd}")
            return True
        else:
            # DCA Entry
            layer = self.position["layer"]
            if layer >= len(DCA_LAYERS): return False
            
            mult = DCA_LAYERS[layer]["mult"]
            amt_usd = self.position["invested"] * (mult - 1) # Simple DCA sizing
            
            if self.balance < amt_usd:
                self.history.append(f"[{timestamp}] ⚠️ NO FUNDS FOR DCA!")
                return False

            coins = amt_usd / price
            self.balance -= amt_usd
            
            # Update Position
            total_coins = self.position["coins"] + coins
            total_invested = self.position["invested"] + amt_usd
            new_avg = total_invested / total_coins
            
            self.position["avg_price"] = new_avg
            self.position["coins"] = total_coins
            self.position["invested"] = total_invested
            self.position["layer"] += 1
            
            self.history.append(f"[{timestamp}] 📉 BUY (DCA L{self.position['layer']}) @ {price} | New Avg: {new_avg:.2f}")
            return True

    def sell(self, price, timestamp, reason="TP"):
        if not self.position: return
        
        coins = self.position["coins"]
        revenue = coins * price
        invested = self.position["invested"]
        pnl = revenue - invested
        pnl_pct = (pnl / invested) * 100
        
        self.balance += revenue
        self.history.append(f"[{timestamp}] 🎉 SELL ({reason}) @ {price} | PnL: ${pnl:.2f} ({pnl_pct:.2f}%) | Bal: ${self.balance:.2f}")
        self.position = None
        return True

# ════════════════ ENGINE ════════════════
def run_sim():
    if not os.path.exists(SCENARIO_FILE):
        print(f"❌ Error: Test data not found: {SCENARIO_FILE}")
        return

    wallet = SimWallet(INITIAL_BALANCE)
    print(f"⏯️  RUNNING SIMULATION: SOL_M15_DCA (Crash Scenario)...")
    print("-" * 60)

    with open(SCENARIO_FILE, "r") as f:
        reader = csv.DictReader(f)
        candles = list(reader)

    # Simplified Loop (Simulating real-time feed)
    rsi_history = [] 
    
    for i, row in enumerate(candles):
        price = float(row["close"])
        timestamp = datetime.fromtimestamp(float(row["timestamp"])).strftime("%Y-%m-%d %H:%M")
        scenario_tag = row["scenario_tag"]
        
        # 1. LOGIC (Simplified for Speed Test)
        # We assume the "tag" in the CSV dictates the market condition
        # In real bot, this is calculated by RSI/BB
        
        should_enter = (scenario_tag == "ENTRY_SIGNAL")
        
        # 2. WALLET MANAGEMENT
        if wallet.position:
            avg = wallet.position["avg_price"]
            pnl_pct = (price - avg) / avg
            layer = wallet.position["layer"]
            
            # Check Exit
            if pnl_pct >= TAKE_PROFIT_PCT or scenario_tag == "DCA_EXIT_PROFIT":
                wallet.sell(price, timestamp)
            
            # Check DCA
            elif layer < len(DCA_LAYERS):
                trigger = DCA_LAYERS[layer]["drop"]
                # In simulation, we force trigger if tag says so OR price drops
                if pnl_pct <= -trigger or "DCA_LAYER" in scenario_tag:
                    wallet.buy(price, timestamp, "DCA")
                    
        else:
            if should_enter:
                wallet.buy(price, timestamp)

    print("-" * 60)
    for log in wallet.history:
        print(log)
    print("-" * 60)
    print(f"🏁 FINAL BALANCE: ${wallet.balance:.2f}")
    print(f"📈 TOTAL PROFIT:  ${wallet.balance - INITIAL_BALANCE:.2f}")

if __name__ == "__main__":
    run_sim()
