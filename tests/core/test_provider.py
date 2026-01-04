
import logging
from .simulator import MarketSimulator

logger = logging.getLogger("TestProvider")

class TestSimulatorProvider:
    """
    A wrapper around MarketSimulator that mimics a Real Exchange Provider.
    Strategies will interact with THIS class, not the Simulator directly.
    """
    def __init__(self, simulator: MarketSimulator):
        self.sim = simulator

    # --- Market Data Methods ---
    def get_ticker_price(self, symbol: str) -> float:
        """Returns the current price from the simulator."""
        return self.sim.get_market_price()

    def get_server_time(self):
        """Returns the simulated time."""
        if self.sim.current_candle:
            return self.sim.current_candle.get('timestamp')
        return 0

    # --- Account Methods ---
    def get_balance(self, asset: str) -> float:
        """Returns balance from the Virtual Wallet."""
        return self.sim.wallet.get_balance(asset)

    def get_all_balances(self) -> dict:
        return self.sim.wallet.balances

    # --- Trading Methods ---
    def create_order(self, symbol: str, side: str, order_type: str, quantity: float, price: float = None):
        """
        Mimics creating an order on an exchange.
        Currently supports 'MARKET' orders mainly.
        """
        # For simulation simplicity in Phase 4, we treat LIMIT as MARKET execution at current price
        # (A real backtester would check if Low <= Price <= High)
        
        # Validations
        current_price = self.get_ticker_price(symbol)
        if current_price <= 0:
            logger.error("❌ Cannot place order: Market price is 0 (Simulation not started?)")
            return None

        logger.info(f"⚡ Requesting Order: {side} {quantity} {symbol} (Type: {order_type})")
        
        try:
            # Delegate execution to the Simulator Core
            self.sim.execute_trade(symbol, side, quantity)
            
            # Return a fake order structure (like CCXT/Exchange API returns)
            return {
                "symbol": symbol,
                "id": f"sim-order-{self.sim.steps_count}",
                "side": side,
                "amount": quantity,
                "price": current_price,
                "status": "closed", # Instant execution
                "filled": quantity
            }
        except Exception as e:
            logger.error(f"❌ Order Failed: {e}")
            return None
