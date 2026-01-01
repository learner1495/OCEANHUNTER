#!/usr/bin/env python3
"""OCEAN HUNTER V10.9 — Data Collection"""

import os
import sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from dotenv import load_dotenv
load_dotenv()

def main():
    print("\n" + "=" * 50)
    print("🌊 OCEAN HUNTER V10.9 — Data Collection")
    print("=" * 50)

    mode = os.getenv("MODE", "PAPER")
    print(f"\n🔧 Mode: {mode}")

    print("\n[1/4] 🔌 Testing Nobitex API...")
    try:
        from modules.network import get_client
        client = get_client()
        result = client.test_connection()
        print(f"      Public API:  {\'✅\' if result[\'public_api\'] else \'❌\'}")
        print(f"      Private API: {\'✅\' if result[\'private_api\'] else \'❌\'}")
    except Exception as e:
        print(f"      ❌ Error: {e}")

    print("\n[2/4] 📱 Testing Telegram Bot...")
    try:
        from modules.network import get_bot
        bot = get_bot()
        if bot.enabled:
            response = bot.send_alert(title="OCEAN HUNTER V10.9", message="✅ Data Collection فعال شد", alert_type="SUCCESS")
            if response.get("ok"):
                print("      ✅ Telegram message sent!")
            else:
                print(f"      ⚠️ Telegram error: {response.get(\'error\', \'Unknown\')}")
        else:
            print("      ⚠️ Telegram not configured")
    except Exception as e:
        print(f"      ❌ Error: {e}")

    print("\n[3/4] ⏱️ Rate Limiter Status...")
    try:
        from modules.network import get_statusrl_status = get_status()
        print(f"      Tokens: {rl_status[\'tokens_available\']}/{rl_status[\'max_tokens\']}")
        print(f"      Usage:  {rl_status[\'usage_percent\']}%")
    except Exception as e:
        print(f"      ❌ Error: {e}")

    print("\n[4/4] 📊 Data Collection...")
    try:
        from modules.data import get_collector
        collector = get_collector()
        results = collector.collect_all()
        print(f"      ✅ Collected {results[\'total_candles\']} candles")
        print(f"      📈 Symbols: {results[\'success_count\']}/{len(results[\'symbols\'])}")
        summary = collector.get_summary()
        for symbol, stats in summary.items():
            if stats.get(\'exists\'):
                print(f"      📁 {symbol}: {stats[\'rows\']} rows")
    except Exception as e:
        print(f"      ❌ Error: {e}")

    print("\n" + "=" * 50)
    print("✅ ALL TASKS COMPLETE")
    print("=" * 50 + "\n")

if __name__ == "__main__":
    main()
