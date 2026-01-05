
import sys
import os
from dotenv import load_dotenv

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from modules.network.telegram_client import TelegramBot

def test():
    print("\n📡 TESTING TELEGRAM CONNECTION...")
    
    env_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), '.env')
    load_dotenv(env_path)
    
    token = os.getenv("TELEGRAM_BOT_TOKEN")
    
    print(f"   Context: .env found at {env_path}")
    print(f"   Token Loaded: {'YES' if token else 'NO'}")
    
    bot = TelegramBot()
    print("   Attempting to send message...")
    result = bot.send_message("📡 <b>Test Packet</b>\nOcean Hunter Connectivity Verified.")
    
    if result:
        print("\n   ✅ SUCCESS: Message sent to Telegram.")
    else:
        print("\n   ❌ FAILED: Check VPN or Token.")
        
    input("\nPress Enter to return...")

if __name__ == "__main__":
    test()
