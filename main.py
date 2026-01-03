"""
OCEAN HUNTER — Main Entry Point
Tests MEXC API + Telegram Notification
"""

import sys
import os
from datetime import datetime

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def main():
    print("=" * 60)
    print("🌊 OCEAN HUNTER V10.8.2 — System Test")
    print(f"⏰ {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)

    results = []

    # === TEST 1: MEXC Connection ===
    print("\n[1/5] Testing MEXC Connection...")
    try:
        from modules.network.mexc_api import get_client
        client = get_client()

        # Ping
        ping = client.ping()
        if "error" not in ping:
            print("   ✅ Ping: OK")
            results.append("MEXC Ping: ✅")
        else:
            print(f"   ❌ Ping Failed: {ping}")
            results.append("MEXC Ping: ❌")

    except Exception as e:
        print(f"   ❌ MEXC Import Error: {e}")
        results.append(f"MEXC: ❌ {e}")

    # === TEST 2: Server Time ===
    print("\n[2/5] Getting Server Time...")
    try:
        time_resp = client.get_server_time()
        if "serverTime" in time_resp:
            st = time_resp["serverTime"]
            print(f"   ✅ Server Time: {st}")
            results.append("Server Time: ✅")
        else:
            print(f"   ⚠️ Response: {time_resp}")
            results.append("Server Time: ⚠️")
    except Exception as e:
        print(f"   ❌ Error: {e}")
        results.append(f"Server Time: ❌")

    # === TEST 3: BTC Price ===
    print("\n[3/5] Getting BTC Price...")
    try:
        price = client.get_ticker_price("BTCUSDT")
        if "price" in price:
            p = price["price"]
            print(f"   ✅ BTCUSDT: ${p}")
            results.append(f"BTC Price: ${p}")
        else:
            print(f"   ⚠️ Response: {price}")
            results.append("BTC Price: ⚠️")
    except Exception as e:
        print(f"   ❌ Error: {e}")
        results.append("BTC Price: ❌")

    # === TEST 4: Account Auth ===
    print("\n[4/5] Testing Authentication...")
    try:
        account = client.get_account()
        if "balances" in account:
            count = len(account["balances"])
            print(f"   ✅ Auth Success! Found {count} assets")
            results.append(f"Auth: ✅ ({count} assets)")

            # Show non-zero balances
            for b in account["balances"][:5]:
                free = float(b.get("free", 0))
                locked = float(b.get("locked", 0))
                if free > 0 or locked > 0:
                    print(f"      💰 {b['asset']}: {free} (locked: {locked})")

        elif "error" in account:
            print(f"   ❌ Auth Failed: {account['error']}")
            results.append(f"Auth: ❌ {account.get('error', 'Unknown')}")
        elif "code" in account:
            print(f"   ❌ API Error {account.get('code')}: {account.get('msg')}")
            results.append(f"Auth: ❌ Code {account.get('code')}")
        else:
            print(f"   ⚠️ Unexpected: {account}")
            results.append("Auth: ⚠️")
    except Exception as e:
        print(f"   ❌ Error: {e}")
        results.append(f"Auth: ❌ {e}")

    # === TEST 5: Telegram ===
    print("\n[5/5] Testing Telegram...")
    try:
        from modules.network.telegram_bot import get_bot
        bot = get_bot()

        # First test connection
        if bot.test_connection():
            print("   ✅ Bot Connected")

            # Send report
            report = "🌊 <b>OCEAN HUNTER Test Report</b>\n\n"
            report += "\n".join(results)
            report += f"\n\n⏰ {datetime.now().strftime('%H:%M:%S')}"

            send_result = bot.send_message(report)
            if send_result.get("ok"):
                print("   ✅ Telegram Message Sent!")
                results.append("Telegram: ✅")
            else:
                print(f"   ⚠️ Send Failed: {send_result}")
                results.append("Telegram: ⚠️")
        else:
            print("   ❌ Bot Connection Failed")
            results.append("Telegram: ❌")

    except Exception as e:
        print(f"   ❌ Telegram Error: {e}")
        results.append(f"Telegram: ❌ {e}")

    # === SUMMARY ===
    print("\n" + "=" * 60)
    print("📊 TEST SUMMARY")
    print("=" * 60)
    for r in results:
        print(f"   {r}")
    print("=" * 60)

    return 0

if __name__ == "__main__":
    sys.exit(main())
