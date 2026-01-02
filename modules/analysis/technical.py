# modules/analysis/technical.py
def calculate_rsi(prices, period=14):
    if len(prices) < period + 1: return 50
    gains, losses = [], []
    for i in range(1, len(prices)):
        delta = prices[i] - prices[i-1]
        gains.append(max(delta, 0))
        losses.append(abs(min(delta, 0)))
    if not gains: return 50
    avg_gain = sum(gains[-period:]) / period
    avg_loss = sum(losses[-period:]) / period
    if avg_loss == 0: return 100
    rs = avg_gain / avg_loss
    return round(100 - (100 / (1 + rs)), 2)

def analyze_market(symbol, candles):
    if not candles: return {"signal": "NEUTRAL", "reason": "No Data", "price": 0, "rsi": 0}
    closes = [c['close'] for c in candles]
    rsi = calculate_rsi(closes)
    signal, reason = "NEUTRAL", f"RSI {rsi}"
    if rsi < 30: signal, reason = "BUY 🟢", f"Oversold ({rsi})"
    elif rsi > 70: signal, reason = "SELL 🔴", f"Overbought ({rsi})"
    return {"symbol": symbol, "price": closes[-1], "rsi": rsi, "signal": signal, "reason": reason}
