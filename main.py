import os
from dotenv import load_dotenv
load_dotenv()

def main():
    print("=" * 50)
    print("OCEAN HUNTER V10.8.2")
    print("=" * 50)
    mode = os.getenv("MODE", "PAPER")
    print(f"Mode: {mode}")
    
    try:
        from modules.network import get_client, get_bot
        
        print("\n[1] Nobitex API...")
        client = get_client()
        r = client.test_connection()
        print(f"    Public: {r['public_api']}, Private: {r['private_api']}")
        
        print("\n[2] Telegram...")
        bot = get_bot()
        tr = bot.test_connection()
        print(f"    Status: {tr['message']}")
        if tr.get("ok"):
            bot.send_startup(mode)
        print("\n[3] Rate Limiter...")
        rl = client.get_rate_limit_status()
        print(f"    Tokens: {rl['tokens_available']}/{rl['max_tokens']}")except Exception as e:
        print(f"Error: {e}")
    print("\n" + "=" * 50)
    print("Session 2 Complete")

if __name__ == "__main__":
    main()
