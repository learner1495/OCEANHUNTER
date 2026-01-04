
import logging
from .interfaces import IDataProvider
from .virtual_wallet import VirtualWallet

logger = logging.getLogger("Simulator")

class MarketSimulator:
    """
    The Brain of the Test.
    Connects DataProvider (Market) -> VirtualWallet (Account).
    """
    def __init__(self, wallet: VirtualWallet, data_provider: IDataProvider):
        self.wallet = wallet
        self.data_provider = data_provider
        self.current_candle = None
        self.steps_count = 0

    def run_step(self):
        """Advances the simulation by one candle."""
        candle = self.data_provider.get_next_candle()
        
        if not candle:
            return False # End of Data

        self.current_candle = candle
        self.steps_count += 1
        return True

    def execute_trade(self, symbol: str, side: str, quantity: float):
        """Manually execute a trade at the CURRENT candle's closing price."""
        if not self.current_candle:
            raise Exception("Market not started yet. Call run_step() first.")
            
        price = self.current_candle['close']
        cost = price * quantity
        fee = cost * self.wallet.commission_rate
        
        if side.upper() == "BUY":
            usdt_bal = self.wallet.get_balance("USDT")
            total_cost = cost + fee
            
            if usdt_bal >= total_cost:
                self.wallet.balances["USDT"] = usdt_bal - total_cost
                current_asset = self.wallet.get_balance(symbol)
                self.wallet.balances[symbol] = current_asset + quantity
                logger.info(f"👉 EXECUTED BUY {quantity} {symbol} @ ${price}")
            else:
                logger.error("Insufficient USDT for BUY")

        elif side.upper() == "SELL":
            asset_bal = self.wallet.get_balance(symbol)
            if asset_bal >= quantity:
                self.wallet.balances[symbol] = asset_bal - quantity
                proceeds = cost - fee
                current_usdt = self.wallet.get_balance("USDT")
                self.wallet.balances["USDT"] = current_usdt + proceeds
                logger.info(f"👉 EXECUTED SELL {quantity} {symbol} @ ${price}")
            else:
                logger.error(f"Insufficient {symbol} for SELL")

    def get_market_price(self):
        return self.current_candle['close'] if self.current_candle else 0
