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
TG_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
TG_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

def log(msg):
    print(f"   {msg}")

def get_server_time():
    try:
        url = f"{MEXC_BASE}/api/v3/time"
        resp = requests.get(url, proxies=PROXIES, verify=False, timeout=5)
        if resp.status_code == 200:
            return resp.json()['serverTime']
    except: pass
    return int(time.time() * 1000)

def get_signature(query_string):
    return hmac.new(MEXC_SECRET.encode(), query_string.encode(), hashlib.sha256).hexdigest()

def send_telegram(message):
    print(f"\n[3] 📨 Sending Telegram Report...")
    if not TG_TOKEN or not TG_CHAT_ID:
        log("❌ Telegram Config Missing")
        return

    url = f"https://api.telegram.org/bot{TG_TOKEN}/sendMessage"
    payload = {"chat_id": TG_CHAT_ID, "text": message}
    
    try:
        resp = requests.post(url, json=payload, proxies=PROXIES, verify=False, timeout=10)
        if resp.status_code == 200:
            log("✅ Telegram Sent Successfully!")
        else:
            log(f"❌ Telegram Fail: {resp.text}")
    except Exception as e:
        log(f"❌ Telegram Error: {e}")

def main():
    print("-" * 50)
    print("🚀 OCEAN HUNTER V6.9 — FINAL INTEGRATION")
    print("-" * 50)
    
    # 1. Sync Time
    print("[1] ⏳ Syncing Time...")
    server_time = get_server_time()
    
    # 2. Check MEXC
    print("[2] 🔐 Checking MEXC...")
    endpoint = "/api/v3/account"
    query = f"timestamp={server_time}&recvWindow=60000"
    signature = get_signature(query)
    final_url = f"{MEXC_BASE}{endpoint}?{query}&signature={signature}"
    headers = {"X-MEXC-APIKEY": MEXC_KEY}

    report_msg = "🌊 OCEAN HUNTER REPORT\n\n"
    report_msg += "✅ System Online (V6.9)\n"
    report_msg += "✅ Proxy Active (10809)\n"

    try:
        resp = requests.get(final_url, headers=headers, proxies=PROXIES, verify=False, timeout=10)
        if resp.status_code == 200:
            data = resp.json()
            log("✅ MEXC Connected!")
            report_msg += "✅ MEXC Authenticated\n\n💰 Assets:\n"
            
            balances = [b for b in data['balances'] if float(b['free']) > 0]
            if balances:
                for b in balances:
                    line = f"{b['asset']}: {b['free']}"
                    log(f"   💰 {line}")
                    report_msg += f"- {line}\n"
            else:
                log("   💰 Wallet Empty")
                report_msg += "- Wallet Empty (Ready to Deposit)\n"
        else:
            err = f"HTTP {resp.status_code} - {resp.text}"
            log(f"❌ {err}")
            report_msg += f"❌ MEXC Error: {resp.status_code}"

    except Exception as e:
        log(f"❌ Error: {e}")
        report_msg += f"❌ Connection Error: {str(e)[:50]}"

    # 3. Send Report
    send_telegram(report_msg)
    print("-" * 50)

if __name__ == "__main__":
    main()
