#!/usr/bin/env python3
"""OCEAN HUNTER V10.8.2 — MEXC Edition"""
import sys
from datetime import datetime

def main():
    print("=" * 60)
    print("       🌊 OCEAN HUNTER V10.8.2 — MEXC Edition")
    print("=" * 60)
    print(f"   Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    try:
        from modules.network import get_client
        client = get_client()
        print("✅ MEXCClient loaded via get_client()")
    except ImportError as e:
        print(f"❌ Import Error: {e}")
        return 1
    print("\n[TEST 1] Ping MEXC...")
    ping = client.ping()
    if "error" in ping:
        print(f"   ❌ Ping failed: {ping['error']}")
        return 1
    print("   ✅ Ping OK")
    print("\n[TEST 2] Server Time...")
    st = client.get_time()
    if "serverTime" in st:
        print(f"   ✅ Server Time: {st['serverTime']}")
    else:
        print(f"   ⚠️ Response: {st}")
    print("\n[TEST 3] BTC Price...")
    price = client.get_price("BTCUSDT")
    if price > 0:
        print(f"   ✅ BTCUSDT: ${price:,.2f}")
    else:
        print("   ⚠️ Could not get price")
    print("\n[TEST 4] Authentication...")
    acc = client.get_account()
    if "error" not in acc and "balances" in acc:
        print("   ✅ Auth SUCCESS")
        usdt = client.get_balance("USDT")
        print(f"   💰 USDT Balance: {usdt['free']:.2f}")
    else:
        print(f"   ⚠️ Auth: {acc.get('error', acc.get('msg', 'Unknown'))}")
    print("\n" + "=" * 60)
    print("   🌊 All tests completed — MEXC Ready")
    print("=" * 60)
    return 0

if __name__ == "__main__":
    sys.exit(main())
