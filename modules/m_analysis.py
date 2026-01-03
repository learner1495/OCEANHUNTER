
def calculate_rsi(prices, period=14):
    """Calculates Relative Strength Index (RSI)"""
    if len(prices) < period + 1:
        return 50  # Not enough data
        
    gains = []
    losses = []
    
    # Calculate price changes
    for i in range(1, len(prices)):
        delta = prices[i] - prices[i-1]
        if delta > 0:
            gains.append(delta)
            losses.append(0)
        else:
            gains.append(0)
            losses.append(abs(delta))
            
    # Calculate initial average
    avg_gain = sum(gains[:period]) / period
    avg_loss = sum(losses[:period]) / period
    
    # Calculate smoothed averages
    for i in range(period, len(prices) - 1):
        avg_gain = (avg_gain * (period - 1) + gains[i]) / period
        avg_loss = (avg_loss * (period - 1) + losses[i]) / period
        
    if avg_loss == 0:
        return 100
        
    rs = avg_gain / avg_loss
    rsi = 100 - (100 / (1 + rs))
    return round(rsi, 2)

def analyze_market(symbol, candles):
    """Analyzes market data and returns a signal"""
    if not candles or len(candles) < 20:
        return {"signal": "WAIT", "rsi": 0, "price": 0}
        
    # Extract closing prices
    closes = [float(c['close']) for c in candles]
    current_price = closes[-1]
    
    # Calculate RSI
    rsi = calculate_rsi(closes)
    
    # Logic Strategy
    signal = "NEUTRAL ⚪"
    if rsi < 30:
        signal = "BUY 🟢 (Oversold)"
    elif rsi > 70:
        signal = "SELL 🔴 (Overbought)"
        
    return {
        "symbol": symbol,
        "price": current_price,
        "rsi": rsi,
        "signal": signal
    }
