import requests
import os
import time
import urllib3
from dotenv import load_dotenv

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
load_dotenv()

# We use the proxy found in V6.4/V6.5
PROXY_URL = "http://127.0.0.1:10809"
PROXIES = {"http": PROXY_URL, "https": PROXY_URL}

def main():
    print("-" * 50)
    print("🚀 OCEAN HUNTER V6.6 — MEXC ACTIVATION")
    print("-" * 50)
    print(f"🔌 Proxy: {PROXY_URL}")

    # 1. Public Endpoint Check (Ping)
    print("\n[1] Pinging MEXC Public API...")
    try:
        url = "https://api.mexc.com/api/v3/ping"
        resp = requests.get(url, proxies=PROXIES, verify=False, timeout=10)
        
        if resp.status_code == 200:
            print("   ✅ MEXC Server is REACHABLE!")
            print(f"   Response: {resp.json()}")
        else:
            print(f"   ❌ Failed to ping: HTTP {resp.status_code}")
            return # Stop if we can't even ping
            
    except Exception as e:
        print(f"   ❌ Connection Error: {e}")
        print("   ⚠️ Ensure V2RayN is running on port 10809!")
        return

    # 2. Market Data Check
    print("\n[2] Fetching BTC Price...")
    try:
        url = "https://api.mexc.com/api/v3/ticker/price?symbol=BTCUSDT"
        resp = requests.get(url, proxies=PROXIES, verify=False, timeout=10)
        data = resp.json()
        
        print(f"   💰 BTC Price: {data['price']} USDT")
        print("   ✅ Market Data Flow is WORKING.")
        
    except Exception as e:
        print(f"   ❌ Market Data Failed: {e}")

    # 3. Check for Credentials
    api_key = os.getenv("MEXC_API_KEY")
    secret_key = os.getenv("MEXC_SECRET_KEY")
    
    print("\n[3] Checking Credentials...")
    if not api_key or "your_api_key" in api_key:
        print("   ⚠️  WARNING: API Key not set in .env file.")
        print("   👉 Please open .env and paste your MEXC keys.")
    else:
        print("   ✅ API Key found in config.")
        print("   (We will test trade authentication in the next step)")

if __name__ == "__main__":
    main()
