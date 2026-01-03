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
# We use the working proxy from previous tests
PROXY_URL = "http://127.0.0.1:10809"
PROXIES = {"http": PROXY_URL, "https": PROXY_URL}

MEXC_BASE = "https://api.mexc.com"
TG_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
TG_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")
MEXC_KEY = os.getenv("MEXC_API_KEY")
MEXC_SECRET = os.getenv("MEXC_SECRET_KEY")

def log(msg):
    print(f"   {msg}")

def test_telegram():
    print("\n[1] 📨 TESTING TELEGRAM...")
    if not TG_TOKEN or not TG_CHAT_ID:
        log("❌ FAIL: Token or Chat ID missing in .env")
        return False
    
    url = f"https://api.telegram.org/bot{TG_TOKEN}/sendMessage"
    payload = {
        "chat_id": TG_CHAT_ID,
        "text": "🌊 OCEAN HUNTER: System Operational!\n✅ Connected to MEXC\n✅ Proxy Active (10809)"
    }
    
    try:
        log(f"Sending message via proxy {PROXY_URL}...")
        resp = requests.post(url, json=payload, proxies=PROXIES, verify=False, timeout=10)
        if resp.status_code == 200:
            log("✅ SUCCESS: Check your Telegram now!")
            return True
        else:
            log(f"❌ FAIL: HTTP {resp.status_code} - {resp.text}")
    except Exception as e:
        log(f"❌ CONNECTION FAIL: {e}")
    return False

def get_mexc_signature(query_string):
    return hmac.new(MEXC_SECRET.encode(), query_string.encode(), hashlib.sha256).hexdigest()

def test_mexc_private():
    print("\n[2] 🔐 TESTING MEXC PRIVATE API (ACCOUNT)...")
    if not MEXC_KEY or not MEXC_SECRET:
        log("⚠️ SKIPPING: API Keys missing in .env")
        return

    endpoint = "/api/v3/account"
    timestamp = int(time.time() * 1000)
    query = f"timestamp={timestamp}"
    signature = get_mexc_signature(query)
    final_url = f"{MEXC_BASE}{endpoint}?{query}&signature={signature}"
    
    headers = {"X-MEXC-APIKEY": MEXC_KEY}

    try:
        resp = requests.get(final_url, headers=headers, proxies=PROXIES, verify=False, timeout=10)
        if resp.status_code == 200:
            data = resp.json()
            log("✅ SUCCESS: Account Accessible.")
            # Show balances
            balances = [b for b in data['balances'] if float(b['free']) > 0 or float(b['locked']) > 0]
            if balances:
                for b in balances:
                    log(f"💰 Balance: {b['asset']} = {b['free']}")
            else:
                log("💰 Balance: Wallet is empty (but connected).")
        elif resp.status_code == 401:
            log("❌ AUTH FAIL: Invalid API Key or Permissions.")
            log(f"Response: {resp.text}")
        else:
            log(f"❌ HTTP ERROR {resp.status_code}: {resp.text}")
            
    except Exception as e:
        log(f"❌ CONNECTION ERROR: {e}")

def main():
    print("-" * 50)
    print("🚀 OCEAN HUNTER V6.7 — FINAL INTEGRATION TEST")
    print("-" * 50)
    
    tg_ok = test_telegram()
    test_mexc_private()
    
    print("-" * 50)
    if tg_ok:
        print("🎉 GREAT JOB! The bot is ready to hunt on MEXC.")
    else:
        print("⚠️ Telegram failed. Check your Token/ChatID or VPN.")

if __name__ == "__main__":
    main()
