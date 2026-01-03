import requests
import socket
import urllib3
import time

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# --- CONFIG ---
PROXY_URL = "http://127.0.0.1:10809"  # Found in V6.4
NOBITEX_URL = "https://api.nobitex.ir/market/global-stats"
GOOGLE_CHECK = "https://www.google.com"

def test_direct_nobitex():
    print("\n[1] TESTING DIRECT CONNECTION TO NOBITEX (IRAN IP)...")
    session = requests.Session()
    session.trust_env = False  # IGNORE System Proxies
    
    # 1. Try standard DNS
    try:
        print("   👉 Attempting standard connection (No Proxy)...")
        resp = session.post(NOBITEX_URL, verify=False, timeout=5)
        if resp.status_code == 200:
            print("   ✅ SUCCESS! Direct connection works.")
            return True
        else:
            print(f"   ❌ HTTP Error: {resp.status_code}")
    except Exception as e:
        print(f"   ❌ Standard Connection Failed: {e}")

    # 2. Try Manual IP (DNS Bypass) if step 1 failed
    print("   👉 Attempting Direct IP Bypass (104.26.12.16)...")
    try:
        headers = {"Host": "api.nobitex.ir"}
        # Cloudflare IP often used by Nobitex
        resp = session.post("https://104.26.12.16/market/global-stats", headers=headers, verify=False, timeout=5)
        if resp.status_code == 200:
            print("   ✅ SUCCESS! Direct IP works.")
            print("   ℹ️  NOTE: We might need to use this IP in the main code.")
            return True
        else:
            print(f"   ❌ IP Bypass HTTP Error: {resp.status_code}")
    except Exception as e:
        print(f"   ❌ IP Bypass Failed: {e}")
    
    return False

def test_proxy_foreign():
    print("\n[2] TESTING PROXY CONNECTION FOR MEXC/TELEGRAM...")
    proxies = {"http": PROXY_URL, "https": PROXY_URL}
    
    try:
        print(f"   👉 Connecting to Google/MEXC via {PROXY_URL}...")
        resp = requests.get(GOOGLE_CHECK, proxies=proxies, verify=False, timeout=10)
        if resp.status_code == 200:
            print("   ✅ SUCCESS! Proxy is working for foreign sites.")
            return True
        else:
            print(f"   ❌ Proxy HTTP Error: {resp.status_code}")
    except Exception as e:
        print(f"   ❌ Proxy Failed: {e}")
        print("   ⚠️ Ensure V2RayN is RUNNING.")
    
    return False

def main():
    print("-" * 50)
    print("🚀 OCEAN HUNTER V6.5 — SPLIT TUNNEL TEST")
    print("-" * 50)
    
    nobitex_ok = test_direct_nobitex()
    proxy_ok = test_proxy_foreign()

    print("\n" + "="*50)
    print("📊 FINAL DIAGNOSIS & ACTION PLAN")
    print("="*50)

    if nobitex_ok and proxy_ok:
        print("✅ PERFECT SCENARIO!")
        print("   We will configure the bot to:")
        print("   1. Use NO PROXY for Nobitex.")
        print("   2. Use PROXY (10809) for Telegram/MEXC.")
    elif not nobitex_ok:
        print("⚠️ NOBITEX ISSUE:")
        print("   Your ISP is blocking Nobitex DNS or IP.")
        print("   We may need to hardcode the IP in the bot.")
    elif not proxy_ok:
        print("⚠️ PROXY ISSUE:")
        print("   V2RayN is not responding on port 10809.")

if __name__ == "__main__":
    main()
