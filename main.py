#!/usr/bin/env python3
"""OCEAN HUNTER V5.7.3 — Standardized Network"""
import os, sys, time
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from dotenv import load_dotenv
from modules.data.collector import get_collector
from modules.analysis.technical import analyze_market

TARGET_COINS = ["BTCIRT", "ETHIRT", "DOGEIRT", "SHIBIRT", "PEPEIRT"]

def main():
    load_dotenv()
    print("\n" + "=" * 60)
    print("🌊 OCEAN HUNTER V5.7.3 — File System Integrated")
    print("=" * 60)
    
    print("\n[1] 🔌 Initializing Network (nobitex_api.py)...")
    try:
        collector = get_collector()
        collector.symbols = TARGET_COINS
        print("      ✅ Collector Ready")
    except Exception as e:
        print(f"      ❌ Failed to init collector: {e}")
        return

    print(f"      Watching: {', '.join(TARGET_COINS)}")
    print("\n[2] 📊 Fetching & Analyzing Data...")
    print(f"      {'SYMBOL':<10} | {'PRICE (IRT)':<15} | {'RSI':<6} | {'SIGNAL'}")
    print("      " + "-" * 50)
    
    try:
        results = collector.collect_all()
    except Exception as e:
        print(f"      ❌ Collection Failed: {e}")
        return
    
    for symbol in TARGET_COINS:
        candles = collector.fetch_ohlcv(symbol)
        if candles:
            analysis = analyze_market(symbol, candles)
            print(f"      {symbol:<10} | {analysis['price']:<15,} | {analysis['rsi']:<6} | {analysis['signal']}")
            if "BUY" in analysis['signal'] or "SELL" in analysis['signal']:
                print(f"      Op >> 🔔 [MOCK] Alert: {analysis['reason']}")
        else:
            print(f"      {symbol:<10} | {'ERROR':<15} | {'---':<6} | ❌ No Data")
            
    print("\n" + "=" * 60)
    print("✅ SCAN COMPLETE")
    print("=" * 60 + "\n")

if __name__ == "__main__":
    main()
