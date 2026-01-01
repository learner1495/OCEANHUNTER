#!/usr/bin/env python3
"""
OCEAN HUNTER V10.8.2 — Main Entry Point
تست اتصال به Nobitex و Telegram
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

        print(f"      Public API:  {'✅' if result['public_api'] else '❌'}")
        print(f"      Private API: {'✅' if result['private_api'] else '❌'}")
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
                print(f"      ⚠️ Telegram error: {response.get('error', 'Unknown')}")
        else:
            print("      ⚠️ Telegram not configured")

    except Exception as e:
        print(f"      ❌ Error: {e}")

    # ─── 3. نمایش Rate Limiter ───
    print("\n[3/3] ⏱️ Rate Limiter Status...")
    try:
        from modules.network import get_statusrl_status = get_status()
        print(f"      Tokens: {rl_status['tokens_available']}/{rl_status['max_tokens']}")
        print(f"      Usage:  {rl_status['usage_percent']}%")

    except Exception as e:
        print(f"      ❌ Error: {e}")

    # ─── پایان ───
    print("\n" + "=" * 50)
    print("✅ ALL TESTS COMPLETE")
    print("=" * 50 + "\n")


if __name__ == "__main__":
    main()
