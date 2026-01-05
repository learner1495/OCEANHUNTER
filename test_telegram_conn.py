
import os
import requests
import sys
from dotenv import load_dotenv

# Force load .env
load_dotenv()

TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

print("-" * 50)
print("📡 TELEGRAM CONNECTIVITY TEST")
print("-" * 50)

if not TOKEN or not CHAT_ID:
    print("❌ ERROR: TELEGRAM_BOT_TOKEN or TELEGRAM_CHAT_ID not found in .env")
    print("   Please check your .env file.")
    sys.exit(1)

print(f"🔹 Token: {TOKEN[:5]}...{TOKEN[-5:]}")
print(f"🔹 Chat ID: {CHAT_ID}")

# 1. Check Bot Info
print("\n[1] Checking Bot Status...")
try:
    url = f"https://api.telegram.org/bot{TOKEN}/getMe"
    resp = requests.get(url, timeout=10)
    data = resp.json()
    
    if data.get("ok"):
        bot_name = data["result"]["first_name"]
        print(f"   ✅ Connected as: @{data['result']['username']} ({bot_name})")
    else:
        print(f"   ❌ API Error: {data}")
        sys.exit(1)
except Exception as e:
    print(f"   ❌ Connection Failed: {e}")
    print("   (Check your VPN/Internet)")
    sys.exit(1)

# 2. Send Test Message
print("\n[2] Sending Test Message...")
try:
    msg = "🔔 OCEAN HUNTER: Connection Successful!\nYour bot is ready to trade."
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    payload = {"chat_id": CHAT_ID, "text": msg}
    
    resp = requests.post(url, json=payload, timeout=10)
    data = resp.json()
    
    if data.get("ok"):
        print("   ✅ MESSAGE SENT SUCCESSFULLY!")
        print("   👉 Check your Telegram app now.")
    else:
        print(f"   ❌ Send Failed: {data}")

except Exception as e:
    print(f"   ❌ Error sending message: {e}")

print("-" * 50)
