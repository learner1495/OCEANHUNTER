#!/usr/bin/env python3
"""OCEAN HUNTER V5.7 — Real Data / Mock Alert"""

import os
import sys
import time
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from dotenv import load_dotenv
from modules.data.collector import get_collector
from modules.analysis.technical import analyze_market

# Volatile Coins to Watch
TARGET_COINS = ["BTCIRT", "ETHIRT", "DOGEIRT", "SHIBIRT", "PEPEIRT"]

def main():
    load_dotenv()
    print("\n" + "=" * 60)
    print("🌊 OCEAN HUNTER V5.7 — Market Scanner (No VPN Mode)")
    print("=" * 60)
    
    print("\n[1] 🔌 Connecting to Nobitex (Direct)...")
    collector = get_collector()
    
    # Update symbol list
    collector.symbols = TARGET_COINS
    
    print(f"      Watching: {', '.join(TARGET_COINS)}")
    print("\n[2] 📊 Fetching & Analyzing Data...")
    print(f"      {'SYMBOL':<10} | {'PRICE (IRT)':<15} | {'RSI':<6} | {'SIGNAL'}")
    print("      " + "-" * 50)
    
    results = collector.collect_all()
    
    for symbol in TARGET_COINS:
        # Get candles from storage or memory
        candles = collector.fetch_ohlcv(symbol, resolution="60") # 1 Hour candles
        
        if candles:
            # ANALYZE
            analysis = analyze_market(symbol, candles)
            
            # OUTPUT (Mock Alert)
            print(f"      {symbol:<10} | {analysis['price']:<15,} | {analysis['rsi']:<6} | {analysis['signal']}")
            
            # Simulation of Telegram Alert
            if "BUY" in analysis['signal'] or "SELL" in analysis['signal']:
                print(f"      Op >> 🔔 [MOCK TELEGRAM] Sending Alert: {analysis['reason']}")
        else:
            print(f"      {symbol:<10} | {'ERROR':<15} | {'---':<6} | ❌ No Data")
            
    print("\n" + "=" * 60)
    print("✅ SCAN COMPLETE")
    print("👉 Note: Telegram was skipped (Mock Mode) until VPN is ready.")
    print("=" * 60 + "\n")

if __name__ == "__main__":
    main()
