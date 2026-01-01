# main.py — OCEAN HUNTER V10.8.2
# ═══════════════════════════════════════════════════════════════

import os
from dotenv import load_dotenv

load_dotenv()

def main():
    print("=" * 50)
    print("🌊 OCEAN HUNTER V10.8.2")
    print("=" * 50)
    
    mode = os.getenv("MODE", "PAPER")
    print(f"\n🔧 Mode: {mode}")
    
    try:
        from modules.network import get_client, get_bot
        
        # ─── Test Nobitex API ───
        print("\n[1/3] 🔌 Testing Nobitex API...")
        client = get_client()
        result = client.test_connection()
        print(f"      Public API: {'✅' if result['public_api'] else '❌'}")
        print(f"      Private API: {'✅' if result['private_api'] else '❌'}")
        print(f"      Message: {result['message']}")
        
        # ─── Test Telegram ───
        print("\n[2/3] 📱 Testing Telegram Bot...")
        bot = get_bot()
        tg_result = bot.test_connection()
        print(f"      Status: {tg_result['message']}")
        
        if tg_result.get("ok"):
            bot.send_startup(mode)
            print("      ✅ Startup message sent!")
        # ─── Rate Limiter Status ───
        print("\n[3/3] ⏱️ Rate Limiter Status...")
        rl_status = client.get_rate_limit_status()
        print(f"      Tokens: {rl_status['tokens_available']}/{rl_status['max_tokens']}")
        print(f"      Usage: {rl_status['usage_percent']}%")
        
    except ImportError as e:
        print(f"\n❌ Import Error: {e}")
        print("   Run build.py first to create modules.")
    except Exception as e:
        print(f"\n❌ Error: {e}")
    
    print("\n" + "=" * 50)
    print("✅ Session 2 Network Test Complete")
    print("=" * 50)

if __name__ == "__main__":
    main()
