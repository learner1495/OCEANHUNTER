#!/usr/bin/env python3
"""
OCEAN HUNTER V10.8.2 — Main Entry Point
"""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from dotenv import load_dotenv
load_dotenv()

def main():
    print("\n" + "=" * 50)
    print("🌊 OCEAN HUNTER V10.8.2")
    print("=" * 50)

    mode = os.getenv("MODE", "PAPER")
    print(f"\n🔧 Mode: {mode}")

    # ─── 1. تست Nobitex API ───
    print("\n[1/3] 🔌 Testing Nobitex API...")
    try:
        from modules.network import get_client
        client = get_client()
        result = client.test_connection()

        pub = "✅" if result["public_api"] else "❌"
        prv = "✅" if result["private_api"] else "❌"
        print(f"      Public API:  {pub}")
        print(f"      Private API: {prv}")
        print(f"      Message: {result['message']}")

    except Exception as e:
        print(f"      ❌ Error: {e}")

    # ─── 2. تست Telegram Bot ───
    print("\n[2/3] 📱 Testing Telegram Bot...")
    try:
        from modules.network import get_bot
        bot = get_bot()

        if bot.enabled:
            response = bot.send_alert(
                title="OCEAN HUNTER ONLINE",
                message="✅ سیستم با موفقیت راه‌اندازی شد",
                alert_type="SUCCESS"
            )
            if response.get("ok"):
                print("      ✅ Telegram message sent!")
            else:
                err = response.get("error", "Unknown")
                print(f"      ⚠️ Telegram error: {err}")
        else:
            print("      ⚠️ Telegram not configured")

    except Exception as e:
        print(f"      ❌ Error: {e}")

    # ─── 3. نمایش Rate Limiter ───
    print("\n[3/3] ⏱️ Rate Limiter Status...")
    try:
        from modules.network import get_statusrl_status = get_status()
        tokens = rl_status.get("tokens_available", "N/A")
        max_t = rl_status.get("max_tokens", "N/A")
        usage = rl_status.get("usage_percent", "N/A")
        print(f"      Tokens: {tokens}/{max_t}")
        print(f"      Usage:  {usage}%")

    except Exception as e:
        print(f"      ❌ Error: {e}")

    # ─── پایان ───
    print("\n" + "=" * 50)
    print("✅ ALL TESTS COMPLETE")
    print("=" * 50 + "\n")

if __name__ == "__main__":
    main()
