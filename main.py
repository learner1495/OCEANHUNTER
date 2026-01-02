#!/usr/bin/env python3
"""OCEAN HUNTER V5.7.5 — Lab Test"""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from modules.data.collector import get_collector

def main():
    print("\n" + "=" * 60)
    print("🔬 OCEAN HUNTER V5.7.5 — LAB TEST")
    print("=" * 60)
    
    collector = get_collector()
    
    # TEST 1: DNS
    print("\n[TEST 1] 🌍 DNS Resolution (api.nobitex.ir)...")
    success, result = collector.test_connection()
    if success:
        print(f"      ✅ Resolved IP: {result}")
        print("      (This means Python CAN find the server)")
    else:
        print(f"      ❌ DNS FAILED: {result}")
        print("      (Python cannot find the server address)")
        return

    # TEST 2: HTTP REQUEST (SSL Disabled)
    print("\n[TEST 2] 📡 Data Fetch (SSL Verify=False)...")
    symbol = "BTCIRT"
    candles, error = collector.fetch_ohlcv(symbol)
    
    if candles:
        price = candles[-1]['close']
        print(f"      ✅ SUCCESS! Price: {price:,.0f} IRT")
        print("      (Problem was SSL Certificate. We bypassed it.)")
    else:
        print(f"      ❌ CONNECTION FAILED: {error}")
        print("      (Check error details above)")

    print("\n" + "=" * 60)
    if candles:
        print("🎉 GREAT! We found the solution.")
        print("   The script can now read data from Nobitex.")
    else:
        print("⚠️ STILL FAILING?")
        print("   If DNS passed but HTTP failed, Firewall might be blocking python.exe")
    print("=" * 60 + "\n")

if __name__ == "__main__":
    main()
