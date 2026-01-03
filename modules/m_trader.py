import json
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
