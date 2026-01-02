#!/usr/bin/env python3
"""OCEAN HUNTER V5.7.9 — HOSTS FILE INJECTOR"""
import os, sys, time
import socket
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from modules.network.nobitex_api import NobitexAPI

def check_dns():
    print(f"   🔎 Checking DNS resolution for api.nobitex.ir...")
    try:
        ip = socket.gethostbyname("api.nobitex.ir")
        print(f"      ✅ Resolved to: {ip}")
        return True
    except socket.gaierror:
        print(f"      ❌ Python failed to resolve DNS.")
        return False

def modify_hosts_file():
    print(f"\n   💉 Attempting to inject IP into Windows HOSTS file...")
    hosts_path = r"C:\Windows\System32\drivers\etc\hosts"
    entry = "\n178.22.122.100 api.nobitex.ir\n"
    
    try:
        # Check if already exists
        with open(hosts_path, 'r') as f:
            content = f.read()
            if "api.nobitex.ir" in content:
                print("      ℹ️ Entry already exists in HOSTS file.")
                return

        # Append
        with open(hosts_path, 'a') as f:
            f.write(entry)
        print("      ✅ Successfully added to HOSTS file!")
    except PermissionError:
        print("      ⚠️ PERMISSION DENIED: Run terminal as Administrator to fix DNS permanently.")
        print("      (Trying temporary workaround...)")
    except Exception as e:
        print(f"      ❌ Error modifying HOSTS: {e}")

def main():
    print("\n" + "=" * 60)
    print("🚀 OCEAN HUNTER V5.7.9 — SYSTEM FIX")
    print("=" * 60)

    # 1. Try to fix DNS manually
    modify_hosts_file()

    # 2. Check if Python can see it now
    dns_ok = check_dns()
    
    # 3. Try Connection
    print("\n[TEST] Final Connection Attempt...")
    api = NobitexAPI()
    now = int(time.time())
    
    data = api.get_ohlcv("BTCIRT", from_ts=now-3600, to_ts=now)
    
    if data.get("s") == "ok":
        price = data['c'][-1]
        print(f"      ✅ SUCCESS! WE ARE CONNECTED!")
        print(f"      💰 Current BTC Price: {price:,.0f} IRT")
    else:
        print(f"      ❌ FAILED: {data.get('msg')}")
        
    print("\n" + "=" * 60)

if __name__ == "__main__":
    main()
