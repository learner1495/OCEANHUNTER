#!/usr/bin/env python3
"""OCEAN HUNTER V5.7.6 — Network Exorcist"""
import os, sys, time, subprocess, socket
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from modules.network.nobitex_api import NobitexAPI

def run_cmd(cmd):
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, shell=True)
        return result.stdout.strip()
    except Exception as e:
        return str(e)

def main():
    print("\n" + "=" * 60)
    print("🧹 OCEAN HUNTER V5.7.6 — NETWORK EXORCIST")
    print("=" * 60)

    # ---------------------------------------------------------
    # TEST 1: RAW INTERNET (PING GOOGLE DNS)
    # ---------------------------------------------------------
    print("\n[TEST 1] 🌍 Pinging Google (8.8.8.8)...")
    # Using ping to check if network adapter works at all
    ping_res = run_cmd("ping -n 1 8.8.8.8")
    if "TTL=" in ping_res:
        print("      ✅ Internet Connection: ALIVE")
    else:
        print("      ❌ Internet Connection: DEAD (Check Cable/Wifi)")
        print(f"      Debug: {ping_res[:100]}...")

    # ---------------------------------------------------------
    # TEST 2: SYSTEM DNS (NSLOOKUP)
    # ---------------------------------------------------------
    print("\n[TEST 2] 📖 System DNS Lookup (nslookup api.nobitex.ir)...")
    ns_res = run_cmd("nslookup api.nobitex.ir")
    
    resolved_ip = None
    if "Address" in ns_res:
        print("      ✅ System DNS: WORKING")
        # Extract IP roughly
        for line in ns_res.splitlines():
            if "Address" in line and "8.8.8.8" not in line: # simplistic
                print(f"      ℹ️  OS sees IP as: {line.split()[-1]}")
    else:
        print("      ❌ System DNS: FAILED")
        print("      (Windows itself cannot find Nobitex)")
        print(ns_res)

    # ---------------------------------------------------------
    # TEST 3: PYTHON REQUEST (CLEAN ENV)
    # ---------------------------------------------------------
    print("\n[TEST 3] 🐍 Python Request (Proxies Purged)...")
    api = NobitexAPI() # This cleans env vars in __init__
    
    now = int(time.time())
    data = api.get_ohlcv("BTCIRT", from_ts=now-3600, to_ts=now)
    
    if data.get("s") == "ok":
        price = data['c'][-1]
        print(f"      ✅ SUCCESS! Price: {price} IRT")
        print("      (Removing proxy variables fixed it!)")
    else:
        print(f"      ❌ FAILED: {data.get('msg')}")
        
    print("\n" + "=" * 60)
    print("DIAGNOSIS SUMMARY:")
    print("1. If Test 1 fails: You have no internet.")
    print("2. If Test 2 fails: Your Windows DNS is broken (try 'ipconfig /flushdns').")
    print("3. If Test 3 fails but Test 2 passes: Python is blocked by Firewall.")
    print("=" * 60 + "\n")

if __name__ == "__main__":
    main()
