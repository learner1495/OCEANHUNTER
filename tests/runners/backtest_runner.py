
import logging
import time
from tests.core.virtual_wallet import VirtualWallet
from tests.core.data_engine import CsvCandlePlayer
from tests.core.simulator import MarketSimulator
from tests.core.test_provider import TestSimulatorProvider

logger = logging.getLogger("BacktestRunner")

class BacktestRunner:
    """
    Orchestrates the entire backtest process:
    1. Sets up Wallet, Data, Simulator, Provider.
    2. Initializes the Strategy with the Provider.
    3. Runs the simulation loop.
    4. Generates a Performance Report.
    """
    def __init__(self, csv_path, initial_capital=1000.0, symbol="SOL"):
        self.symbol = symbol
        self.initial_capital = initial_capital
        
        # Core Components
        self.wallet = VirtualWallet(initial_balances={"USDT": initial_capital})
        self.data_engine = CsvCandlePlayer(csv_path)
        self.simulator = MarketSimulator(self.wallet, self.data_engine)
        self.provider = TestSimulatorProvider(self.simulator)
        
        # Stats
        self.trades = []
        self.start_time = time.time()

    def run(self, strategy_class):
        """
        Runs the backtest using the given Strategy Class.
        strategy_class: A class that accepts (provider, symbol) and has on_candle() method.
        """
        print(f"🚀 Starting Backtest on {self.symbol}...")
        
        # Initialize Strategy
        strategy = strategy_class(self.provider, self.symbol)
        
        steps = 0
        while self.simulator.run_step():
            # Get current candle data
            candle = self.simulator.current_candle
            
            # Tick the strategy
            strategy.on_candle(candle)
            steps += 1
            
            if steps % 100 == 0:
                print(f"   ⏳ Processed {steps} candles...", end='\r')

        print(f"\n✅ Backtest Complete. Processed {steps} candles.")
        return self._generate_report()

    def _generate_report(self):
        """Calculates basic performance metrics."""
        final_balance = self.wallet.get_balance("USDT")
        
        # Calculate Asset Value (sell everything at last price)
        last_price = self.simulator.get_market_price()
        asset_qty = self.wallet.get_balance(self.symbol)
        asset_value = asset_qty * last_price
        
        total_equity = final_balance + asset_value
        pnl = total_equity - self.initial_capital
        roi = (pnl / self.initial_capital) * 100
        
        report = {
            "initial_capital": self.initial_capital,
            "final_equity": total_equity,
            "pnl": pnl,
            "roi": roi,
            "symbol": self.symbol,
            "simulated_trades": len(self.provider.orders) if hasattr(self.provider, 'orders') else "N/A"
        }
        return report
