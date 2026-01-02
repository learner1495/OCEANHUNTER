# modules/analysis/technical.py
import math

def calculate_rsi(prices, period=14):
    """Simple RSI Calculation"""
    if len(prices) < period + 1:
        return 50  # Not enough data
    
    gains = []
    losses = []
    
    for i in range(1, len(prices)):
        delta = prices[i] - prices[i-1]
        if delta > 0:
            gains.append(delta)
            losses.append(0)
        else:
            gains.append(0)
            losses.append(abs(delta))
            
    # Simple Average (SMMA approximation for initial test)
    avg_gain = sum(gains[-period:]) / period
    avg_loss = sum(losses[-period:]) / period
    
    if avg_loss == 0:
        return 100
        
    rs = avg_gain / avg_loss
    rsi = 100 - (100 / (1 + rs))
    return round(rsi, 2)

def analyze_market(symbol, candles):
    """Analyzes candles and returns a signal"""
    if not candles:
        return {"signal": "NEUTRAL", "reason": "No Data"}
        
    closes = [c['close'] for c in candles]
    current_price = closes[-1]
    rsi = calculate_rsi(closes)
    
    signal = "NEUTRAL"
    reason = f"RSI is {rsi}"
    
    if rsi < 30:
        signal = "BUY 🟢"
        reason = f"Oversold (RSI {rsi})"
    elif rsi > 70:
        signal = "SELL 🔴"
        reason = f"Overbought (RSI {rsi})"
        
    return {
        "symbol": symbol,
        "price": current_price,
        "rsi": rsi,
        "signal": signal,
        "reason": reason
    }
