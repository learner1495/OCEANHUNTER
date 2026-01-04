
import pandas as pd
import numpy as np
import logging

class SmartSniperStrategy:
    """
    🌊 Ocean Hunter Strategy: Smart Sniper V10.8.2
    
    Logic:
    1. Indicators: RSI(14), MACD(12,26,9), Bollinger Bands(20, 2std)
    2. Entry: Score-based system (RSI Dip + BB Touch + MACD Histogram)
    3. Exit: Fixed TP/SL or RSI Overbought
    """
    def __init__(self, provider, symbol, risk_per_trade=0.98):
        self.provider = provider
        self.symbol = symbol
        self.risk_per_trade = risk_per_trade # Use 98% of available balance
        
        # History Buffer for Calculation
        self.history = []
        self.warmup_period = 35 # Min candles needed for MACD/RSI
        
        # Position Management
        self.position_size = 0.0
        self.entry_price = 0.0
        
        # Risk Settings
        self.tp_percent = 0.015  # 1.5% Target
        self.sl_percent = 0.010  # 1.0% Stop Loss

    def _calculate_indicators(self, df):
        """Calculates Technical Indicators on the DataFrame"""
        # RSI
        delta = df['close'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
        rs = gain / loss
        df['rsi'] = 100 - (100 / (1 + rs))
        
        # Bollinger Bands
        df['bb_mid'] = df['close'].rolling(window=20).mean()
        df['bb_std'] = df['close'].rolling(window=20).std()
        df['bb_upper'] = df['bb_mid'] + (df['bb_std'] * 2)
        df['bb_lower'] = df['bb_mid'] - (df['bb_std'] * 2)
        
        # MACD
        exp12 = df['close'].ewm(span=12, adjust=False).mean()
        exp26 = df['close'].ewm(span=26, adjust=False).mean()
        df['macd'] = exp12 - exp26
        df['signal'] = df['macd'].ewm(span=9, adjust=False).mean()
        
        return df.iloc[-1] # Return only the latest row

    def on_candle(self, candle):
        """Main Logic Loop called on every new candle"""
        # 1. Update History
        self.history.append({
            'open': candle['open'],
            'high': candle['high'],
            'low': candle['low'],
            'close': candle['close'],
            'volume': candle['volume']
        })
        
        # Keep history manageable (last 100 candles is enough)
        if len(self.history) > 100:
            self.history.pop(0)
            
        # 2. Warmup Check
        if len(self.history) < self.warmup_period:
            return

        # 3. Calculate Indicators
        df = pd.DataFrame(self.history)
        latest = self._calculate_indicators(df)
        
        current_price = latest['close']
        rsi = latest['rsi']
        
        # 4. Check Exit Conditions (If we have a position)
        if self.position_size > 0:
            self._check_exit(current_price, rsi)
            return

        # 5. Check Entry Conditions (If we have NO position)
        self._check_entry(latest)

    def _check_entry(self, latest):
        score = 0
        price = latest['close']
        
        # ─── SCORING SYSTEM ───
        
        # A. RSI Condition (Oversold)
        if latest['rsi'] < 30:
            score += 40
        elif latest['rsi'] < 40:
            score += 20
            
        # B. Bollinger Band Condition (Dip)
        if price <= latest['bb_lower']:
            score += 30 # Strong Signal: Touching Lower Band
        elif price <= (latest['bb_lower'] * 1.005):
            score += 10 # Near Lower Band
            
        # C. MACD Condition (Momentum)
        if latest['macd'] > latest['signal']:
            score += 10 # Bullish Momentum

        # ─── EXECUTION ───
        THRESHOLD = 50 
        
        if score >= THRESHOLD:
            balance = self.provider.get_balance("USDT")
            if balance > 10:
                amount_to_spend = balance * self.risk_per_trade
                qty = amount_to_spend / price
                
                print(f"   ⚡ SIGNAL FIRED (Score: {score}) | RSI: {latest['rsi']:.1f} | Price: {price:.2f}")
                self.provider.create_order(self.symbol, "BUY", "MARKET", qty)
                
                self.position_size = qty
                self.entry_price = price

    def _check_exit(self, current_price, rsi):
        # Calculate PnL %
        pnl_pct = (current_price - self.entry_price) / self.entry_price
        
        exit_reason = None
        
        # 1. Take Profit
        if pnl_pct >= self.tp_percent:
            exit_reason = "✅ TP Hit"
            
        # 2. Stop Loss
        elif pnl_pct <= -self.sl_percent:
            exit_reason = "❌ SL Hit"
            
        # 3. RSI Overbought (Sniper Exit)
        elif rsi > 70 and pnl_pct > 0.005: # Only exit on RSI if in profit
            exit_reason = "⚠️ RSI Overbought"

        if exit_reason:
            print(f"   🔄 EXITING: {exit_reason} | PnL: {pnl_pct*100:.2f}%")
            self.provider.create_order(self.symbol, "SELL", "MARKET", self.position_size)
            self.position_size = 0.0
            self.entry_price = 0.0
