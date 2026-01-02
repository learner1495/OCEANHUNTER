#!/usr/bin/env python3
"""OCEAN HUNTER V5.7.7 — IP Bypass Mode"""
import os, sys, time
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from modules.network.nobitex_api import NobitexAPI

def main():
    print("\n" + "=" * 60)
    print("🚀 OCEAN HUNTER V5.7.7 — DIRECT IP BYPASS")
    print("=" * 60)

    print("\n[TEST] Connecting to Nobitex via 178.22.122.100...")
    
    api = NobitexAPI()
    now = int(time.time())
    
    # Try to fetch Bitcoin data
    data = api.get_ohlcv("BTCIRT", from_ts=now-3600, to_ts=now)
    
    if data.get("s") == "ok":
        price = data['c'][-1]
        print(f"      ✅ SUCCESS! Connection Established!")
        print(f"      💰 Current BTC Price: {price:,.0f} IRT")
        print("      (We successfully bypassed the DNS blockage)")
    else:
        print(f"      ❌ FAILED: {data.get('msg')}")
        print("      If this fails, the Firewall is blocking the IP itself.")
        
    print("\n" + "=" * 60)

if __name__ == "__main__":
    main()
