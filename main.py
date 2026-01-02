#!/usr/bin/env python3
"""OCEAN HUNTER V5.8.2 — SMART LOOKUP"""
import os, sys, time
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from modules.network.nobitex_api import NobitexAPI

def main():
    print("\n" + "=" * 60)
    print("🚀 OCEAN HUNTER V5.8.2 — SMART DNS LOOKUP")
    print("=" * 60)

    print("\n[TEST] Initializing...")
    api = NobitexAPI()
    now = int(time.time())
    
    # Try BTCIRT
    data = api.get_ohlcv("BTCIRT", from_ts=now-3600, to_ts=now)
    
    if data.get("s") == "ok":
        price = data['c'][-1]
        print(f"\n" + "=" * 60)
        print(f"✅ CONNECTION SUCCESSFUL!")
        print(f"💰 BTC Price: {price:,.0f} IRT")
        print("=" * 60)
    else:
        print(f"\n❌ FAILED: {data.get('msg')}")

if __name__ == "__main__":
    main()
