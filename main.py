#!/usr/bin/env python3
"""OCEAN HUNTER V5.7.4 — Connectivity Diagnostic"""
import os, sys, time
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from dotenv import load_dotenv
from modules.data.collector import get_collector

TARGET_COINS = ["BTCIRT", "ETHIRT", "DOGEIRT"]

def main():
    load_dotenv()
    print("\n" + "=" * 60)
    print("🌊 OCEAN HUNTER V5.7.4 — Direct Connection Mode")
    print("   ⚠️  Ignoring System Proxies (Bypassing VPN settings)")
    print("=" * 60)
    
    print("\n[1] 🔌 Initializing Network...")
    try:
        collector = get_collector()
        print("      ✅ Collector Ready")
    except Exception as e:
        print(f"      ❌ Failed to init: {e}")
        return

    print("\n[2] 📡 Testing Connectivity to Nobitex...")
    print(f"      {'SYMBOL':<10} | {'STATUS':<15} | {'DETAIL'}")
    print("      " + "-" * 50)
    
    success_count = 0
    for symbol in TARGET_COINS:
        candles, error = collector.fetch_ohlcv(symbol)
        
        if candles:
            last_price = candles[-1]['close']
            print(f"      {symbol:<10} | {'✅ ONLINE':<15} | Price: {last_price:,.0f} IRT")
            success_count += 1
        else:
            print(f"      {symbol:<10} | {'❌ FAILED':<15} | {error}")
            
    print("\n" + "=" * 60)
    if success_count == 0:
        print("❌ CRITICAL: No connection.")
        print("   Suggestion: Turn OFF all VPNs completely and retry.")
    else:
        print("✅ SUCCESS: Connection Established!")
    print("=" * 60 + "\n")

if __name__ == "__main__":
    main()
