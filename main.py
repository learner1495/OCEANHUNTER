#!/usr/bin/env python3
"""OCEAN HUNTER V5.8.0 — DNS SURGERY"""
import os, sys, time
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from modules.network.nobitex_api import NobitexAPI

def main():
    print("\n" + "=" * 60)
    print("🚀 OCEAN HUNTER V5.8.0 — DNS BYPASS SURGERY")
    print("=" * 60)

    print("\n[TEST] Initializing API with Custom DNS Engine...")
    
    api = NobitexAPI()
    now = int(time.time())
    
    print("\n[TEST] Attempting Connection to api.nobitex.ir...")
    data = api.get_ohlcv("BTCIRT", from_ts=now-3600, to_ts=now)
    
    if data.get("s") == "ok":
        price = data['c'][-1]
        print(f"      ✅ SUCCESS! WE HAVE DATA!")
        print(f"      💰 Current BTC Price: {price:,.0f} IRT")
        print("      (The DNS Bypass worked beautifully)")
    else:
        print(f"      ❌ FAILED: {data.get('msg')}")
        
    print("\n" + "=" * 60)

if __name__ == "__main__":
    main()
