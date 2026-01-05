
import os
import time
import sys
from dotenv import load_dotenv

# Setup Paths
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

# Imports
from modules.mexc_provider import MEXCData
from modules.network.telegram_client import TelegramBot

# Load Environment
load_dotenv()

# Configuration
SYMBOL = "BTCUSDT"
TIMEFRAME = "15m"

def calculate_rsi(prices, period=14):
    import numpy as np
    if len(prices) < period + 1: return 50.0
    deltas = np.diff(prices)
    seed = deltas[:period+1]
    up = seed[seed >= 0].sum()/period
    down = -seed[seed < 0].sum()/period
    rs = up/down if down != 0 else 0
    rsi = np.zeros_like(prices)
    rsi[:period] = 100. - 100./(1. + rs)
    for i in range(period, len(prices)):
        delta = deltas[i-1]
        if delta > 0:
            upval = delta
            downval = 0.
        else:
            upval = 0.
            downval = -delta
        up = (up * (period - 1) + upval) / period
        down = (down * (period - 1) + downval) / period
        rs = up/down if down != 0 else 0
        rsi[i] = 100. - 100./(1. + rs)
    return rsi[-1]

def calculate_bollinger_bands(prices, period=20, std_dev=2):
    import numpy as np
    if len(prices) < period: return 0, 0, 0
    sma = np.mean(prices[-period:])
    std = np.std(prices[-period:])
    upper = sma + (std_dev * std)
    lower = sma - (std_dev * std)
    return upper, sma, lower

def run_engine():
    print(f"\n🚀 OCEAN HUNTER ENGINE STARTED")
    print(f"🎯 Target: {SYMBOL} | Strategy: Smart Sniper V10.8.2")
    
    provider = MEXCData()
    bot = TelegramBot()
    
    # Startup Message
    start_msg = f"🌊 <b>OCEAN HUNTER ONLINE</b>\nSymbol: {SYMBOL}\nMode: {os.getenv('MODE', 'UNKNOWN')}"
    print("   📨 Sending startup message to Telegram...")
    if bot.send_message(start_msg):
        print("   ✅ Telegram Connected Successfully.")
    else:
        print("   ⚠️ Telegram Message Failed (Check VPN/Proxy/Keys).")

    cycle_count = 0
    
    while True:
        try:
            cycle_count += 1
            if cycle_count % 10 == 0:
                 print(f"\n[Cycle {cycle_count}] Scanning Markets...")
            
            # Fetch & Analyze
            df = provider.get_klines(SYMBOL, TIMEFRAME, limit=50)
            if df is not None and not df.empty:
                closes = df['close'].values
                current_price = closes[-1]
                rsi = calculate_rsi(closes)
                upper, mid, lower = calculate_bollinger_bands(closes)
                
                score = 0
                reasons = []
                
                # Strategy Logic
                if rsi < 35:
                    score += 35
                    reasons.append(f"RSI Oversold ({rsi:.2f})")
                if current_price < lower:
                    score += 35
                    reasons.append("Price < BB Lower")
                
                # Signal Trigger
                if score >= 70:
                    msg = f"🎯 <b>SIGNAL DETECTED</b>\nPrice: {current_price}\nScore: {score}\nReasons: {', '.join(reasons)}"
                    print(f"   🚨 SIGNAL FOUND! Score: {score}")
                    bot.send_message(msg)
                    time.sleep(60) 
                
                # Status Line
                sys.stdout.write(f"\r   Price: {current_price:.2f} | RSI: {rsi:.2f} | Score: {score}   ")
                sys.stdout.flush()

            time.sleep(5)

        except KeyboardInterrupt:
            bot.send_message("🛑 Bot Stopped by User.")
            break
        except Exception as e:
            print(f"Error: {e}")
            time.sleep(10)

if __name__ == "__main__":
    run_engine()
