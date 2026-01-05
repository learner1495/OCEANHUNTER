
import os
import requests
import sys
from dotenv import load_dotenv

load_dotenv()

TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

print("-" * 60)
print("📡 TELEGRAM CONNECTIVITY TEST (SMART PROXY)")
print("-" * 60)

if not TOKEN or not CHAT_ID:
    print("❌ ERROR: TELEGRAM_BOT_TOKEN or TELEGRAM_CHAT_ID missing.")
    sys.exit(1)

# List of common local proxies used by V2Ray, NekoBox, Clash, etc.
# We will try them one by one.
POTENTIAL_PROXIES = [
    None,                           # Try Direct first (might work if VPN is in TUN mode)
    "http://127.0.0.1:10809",       # V2Ray Default HTTP
    "socks5://127.0.0.1:10808",     # V2Ray Default SOCKS
    "http://127.0.0.1:2081",        # NekoBox/Hiddify HTTP
    "socks5://127.0.0.1:2080",      # NekoBox/Hiddify SOCKS
    "http://127.0.0.1:7890",        # Clash Default
    "socks5://127.0.0.1:7891",      # Clash SOCKS
    "http://127.0.0.1:1080",        # Generic Proxy
]

working_proxy = None
bot_username = ""

print(f"🔹 Token: {TOKEN[:5]}...{TOKEN[-5:]}")
print(f"🔹 Checking {len(POTENTIAL_PROXIES)} connection methods...")

# 1. FIND WORKING PROXY
for proxy_url in POTENTIAL_PROXIES:
    proxies_dict = {"https": proxy_url, "http": proxy_url} if proxy_url else None
    label = proxy_url if proxy_url else "DIRECT CONNECTION"
    
    print(f"\n   👉 Trying: {label} ... ", end="")
    try:
        url = f"https://api.telegram.org/bot{TOKEN}/getMe"
        resp = requests.get(url, proxies=proxies_dict, timeout=5)
        
        if resp.status_code == 200:
            print("✅ SUCCESS!")
            working_proxy = proxies_dict
            data = resp.json()
            bot_username = data['result']['username']
            print(f"      🎉 Connected to Bot: @{bot_username}")
            break
        else:
            print(f"❌ Failed (HTTP {resp.status_code})")
    except Exception as e:
        print("❌ Failed (Timeout/Error)")

if not working_proxy and not bot_username:
    print("\n" + "="*60)
    print("❌ CRITICAL: ALL CONNECTION ATTEMPTS FAILED.")
    print("   Please check your V2Ray/VPN settings.")
    print("   Look for 'Local Port' or 'HTTP Proxy Port' in your VPN app.")
    print("   Common ports: 10809, 2081, 7890")
    print("="*60)
    sys.exit(1)

# 2. SEND MESSAGE
print(f"\n[2] Sending Test Message using found path...")
try:
    msg = f"🔔 OCEAN HUNTER: Connection Successful!\n🚀 Proxy used: {working_proxy if working_proxy else 'Direct'}"
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    payload = {"chat_id": CHAT_ID, "text": msg}
    
    resp = requests.post(url, json=payload, proxies=working_proxy, timeout=10)
    data = resp.json()
    
    if data.get("ok"):
        print("   ✅ MESSAGE SENT SUCCESSFULLY!")
        print("   👉 Check your Telegram app now.")
        
        # Save working proxy to .env for future use (Optional logic could go here)
        print(f"   ℹ️  To make this permanent, you might need to set HTTPS_PROXY in .env")
        if working_proxy:
             print(f"       Example: HTTPS_PROXY={working_proxy['https']}")
    else:
        print(f"   ❌ Send Failed: {data}")

except Exception as e:
    print(f"   ❌ Error sending message: {e}")

print("-" * 60)
