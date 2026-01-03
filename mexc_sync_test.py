import requests
import os
import time
import urllib3
import hashlib
import hmac
from dotenv import load_dotenv

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
load_dotenv()

# --- CONFIG ---
PROXY_URL = "http://127.0.0.1:10809"
PROXIES = {"http": PROXY_URL, "https": PROXY_URL}
MEXC_BASE = "https://api.mexc.com"
MEXC_KEY = os.getenv("MEXC_API_KEY")
MEXC_SECRET = os.getenv("MEXC_SECRET_KEY")

def log(msg):
    print(f"   {msg}")

def get_server_time():
    """Gets precise server time from MEXC to fix timestamp errors"""
    try:
        url = f"{MEXC_BASE}/api/v3/time"
        resp = requests.get(url, proxies=PROXIES, verify=False, timeout=5)
        if resp.status_code == 200:
            return resp.json()['serverTime']
    except Exception as e:
        log(f"⚠️ Could not fetch server time: {e}")
    return int(time.time() * 1000)

def get_signature(query_string):
    return hmac.new(MEXC_SECRET.encode(), query_string.encode(), hashlib.sha256).hexdigest()

def test_account_with_sync():
    print("-" * 50)
    print("🚀 OCEAN HUNTER V6.8 — TIME SYNC FIX")
    print("-" * 50)
    
    if not MEXC_KEY or not MEXC_SECRET:
        log("❌ FAIL: API Keys missing in .env")
        return

    # 1. Get Server Time
    print("[1] ⏳ Synchronizing Clock...")
    server_time = get_server_time()
    local_time = int(time.time() * 1000)
    diff = server_time - local_time
    log(f"Server Time: {server_time}")
    log(f"Local Time:  {local_time}")
    log(f"Difference:  {diff} ms")

    # 2. Prepare Request with recvWindow
    print("\n[2] 🔐 Checking Account Balance...")
    endpoint = "/api/v3/account"
    
    # We use server_time directly and add a large recvWindow (60s)
    query = f"timestamp={server_time}&recvWindow=60000"
    signature = get_signature(query)
    final_url = f"{MEXC_BASE}{endpoint}?{query}&signature={signature}"
    
    headers = {"X-MEXC-APIKEY": MEXC_KEY}

    try:
        resp = requests.get(final_url, headers=headers, proxies=PROXIES, verify=False, timeout=10)
        
        if resp.status_code == 200:
            data = resp.json()
            log("✅ SUCCESS! Authentication Passed.")
            
            # Show balances
            balances = [b for b in data['balances'] if float(b['free']) > 0 or float(b['locked']) > 0]
            if balances:
                print("\n   💰 YOUR WALLET ASSETS:")
                for b in balances:
                    print(f"      - {b['asset']}: {b['free']}")
            else:
                log("💰 Balance: Wallet is empty (but connected).")
                
        elif resp.status_code == 400:
             log(f"❌ TIMESTAMP ERROR: {resp.text}")
             log("👉 Solution: Check your PC clock settings to be 'Automatic'.")
        elif resp.status_code == 401:
            log("❌ AUTH FAIL: Invalid API Key or Permissions.")
        else:
            log(f"❌ HTTP ERROR {resp.status_code}: {resp.text}")
            
    except Exception as e:
        log(f"❌ CONNECTION ERROR: {e}")

if __name__ == "__main__":
    test_account_with_sync()
