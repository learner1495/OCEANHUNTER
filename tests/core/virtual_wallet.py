
import logging
from typing import Dict, Optional

# Configure logging
logger = logging.getLogger("VirtualWallet")

class VirtualWallet:
    """
    Simulates a crypto exchange wallet with locking mechanism and fees.
    
    EXCHANGE: MEXC Global
    FEE STRUCTURE: 0.1% (0.001) for Maker/Taker (Standard Spot)
    """
    
    def __init__(self, initial_balances: Dict[str, float] = None, commission_rate: float = 0.001):
        # Default commission_rate set to 0.001 (0.1%) for MEXC
        self.balances = initial_balances if initial_balances else {}  # Available funds
        self.locked = {}  # Funds locked in open orders
        self.commission_rate = commission_rate
        self.history = [] # Transaction history log

    def get_balance(self, asset: str) -> float:
        """Returns AVAILABLE balance (not including locked)."""
        return self.balances.get(asset, 0.0)

    def get_total_balance(self, asset: str) -> float:
        """Returns Total balance (Available + Locked)."""
        return self.balances.get(asset, 0.0) + self.locked.get(asset, 0.0)

    def lock_funds(self, asset: str, amount: float) -> bool:
        """Locks funds for an order. Returns True if successful."""
        if amount <= 0:
            return False
            
        available = self.balances.get(asset, 0.0)
        # Using a small epsilon for float comparison safety
        if available >= amount:
            self.balances[asset] = available - amount
            self.locked[asset] = self.locked.get(asset, 0.0) + amount
            return True
        else:
            logger.warning(f"Insufficient funds to lock {amount} {asset}. Available: {available}")
            return False

    def unlock_funds(self, asset: str, amount: float):
        """Unlocks funds (e.g., cancelled order)."""
        locked_amount = self.locked.get(asset, 0.0)
        if locked_amount >= amount:
            self.locked[asset] = locked_amount - amount
            self.balances[asset] = self.balances.get(asset, 0.0) + amount
        else:
            logger.error(f"Attempted to unlock {amount} {asset} but only {locked_amount} is locked.")
            # Recover as much as possible
            self.balances[asset] = self.balances.get(asset, 0.0) + locked_amount
            self.locked[asset] = 0

    def apply_trade(self, side: str, base_asset: str, quote_asset: str, 
                   amount: float, price: float, is_maker: bool = False):
        """
        Executes a trade and updates balances.
        side: 'BUY' or 'SELL'
        amount: Amount of Base Asset (e.g., BTC)
        price: Price in Quote Asset (e.g., USDT)
        """
        cost = amount * price
        fee_rate = self.commission_rate 
        
        if side == 'BUY':
            # Buyer pays Quote (USDT), receives Base (BTC)
            # Funds were already locked in Quote (USDT)
            
            # 1. Deduct cost from locked Quote
            current_locked = self.locked.get(quote_asset, 0.0)
            if current_locked >= cost:
                self.locked[quote_asset] = current_locked - cost
            else:
                # Fallback correction
                remaining = cost - current_locked
                if self.balances.get(quote_asset, 0) >= remaining:
                    self.balances[quote_asset] -= remaining
                self.locked[quote_asset] = 0
                
            # 2. Add Base (BTC) - Fee is deducted from received asset on MEXC
            gross_receive = amount
            fee = gross_receive * fee_rate
            net_receive = gross_receive - fee
            
            self.balances[base_asset] = self.balances.get(base_asset, 0.0) + net_receive
            
            self._log_trade(side, base_asset, quote_asset, amount, price, fee, fee_asset=base_asset)
            
        elif side == 'SELL':
            # Seller pays Base (BTC), receives Quote (USDT)
            # Funds (BTC) were locked
            
            # 1. Deduct Base from locked
            current_locked = self.locked.get(base_asset, 0.0)
            if current_locked >= amount:
                self.locked[base_asset] = current_locked - amount
            else:
                 remaining = amount - current_locked
                 if self.balances.get(base_asset, 0) >= remaining:
                     self.balances[base_asset] -= remaining
                 self.locked[base_asset] = 0
                 
            # 2. Add Quote (USDT) - Fee deducted from USDT received
            gross_receive = cost
            fee = gross_receive * fee_rate
            net_receive = gross_receive - fee
            
            self.balances[quote_asset] = self.balances.get(quote_asset, 0.0) + net_receive
            
            self._log_trade(side, base_asset, quote_asset, amount, price, fee, fee_asset=quote_asset)

    def _log_trade(self, side, base, quote, amount, price, fee, fee_asset):
        self.history.append({
            "side": side,
            "pair": f"{base}{quote}",
            "amount": amount,
            "price": price,
            "fee": fee,
            "fee_asset": fee_asset,
            "timestamp": "SIMULATED" 
        })
