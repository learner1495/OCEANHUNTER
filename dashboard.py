
import os
import sys
import time
import subprocess
import signal
import requests
from dotenv import load_dotenv, set_key

# Add Root to path
sys.path.append(os.getcwd())
from data.mexc_provider import MEXCProvider

# Global Bot Process
bot_process = None

def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')

def load_config():
    load_dotenv(override=True)
    return {
        "MODE": os.getenv("MODE", "PAPER"),
        "MEXC_KEY": os.getenv("MEXC_API_KEY", ""),
        "TG_TOKEN": os.getenv("TELEGRAM_BOT_TOKEN", ""),
        "TG_ID": os.getenv("TELEGRAM_CHAT_ID", "")
    }

def update_env_variable(key, value):
    env_path = os.path.join(os.getcwd(), ".env")
    set_key(env_path, key, value)
    load_dotenv(override=True)
    print(f"✅ Updated {key} successfully.")
    time.sleep(1)

def show_header(config):
    clear_screen()
    print("🌊 OCEAN HUNTER COMMANDER v1.1")
    print("═" * 40)
    print(f"📡 MODE:      {config['MODE']}")
    print(f"🤖 BOT STATE: {'🟢 RUNNING' if bot_process else '🔴 STOPPED'}")
    print("═" * 40)

def test_telegram():
    cfg = load_config()
    print("\n📨 TELEGRAM TEST")
    if not cfg['TG_TOKEN'] or not cfg['TG_ID']:
        print("❌ Token or Chat ID is missing in .env")
    else:
        print("   Sending test message...")
        try:
            url = f"https://api.telegram.org/bot{cfg['TG_TOKEN']}/sendMessage"
            payload = {"chat_id": cfg['TG_ID'], "text": "✅ <b>Test Message from Dashboard</b>", "parse_mode": "HTML"}
            resp = requests.post(url, json=payload, timeout=5)
            if resp.status_code == 200:
                print("   ✅ Success! Check your Telegram.")
            else:
                print(f"   ❌ Failed. Status: {resp.status_code}")
                print(f"   Response: {resp.text}")
        except Exception as e:
            print(f"   ❌ Error: {e}")
    input("\nPress Enter to return...")

def menu_wallets():
    print("\n💰 WALLET CHECKER")
    print("Fetching data from MEXC...")
    try:
        p = MEXCProvider()
        usdt = p.get_balance("USDT")
        sol = p.get_balance("SOL")
        print(f"   USDT: {usdt}")
        print(f"   SOL:  {sol}")
    except Exception as e:
        print(f"   Error: {e}")
    input("\nPress Enter to return...")

def menu_settings():
    while True:
        clear_screen()
        print("⚙️ SETTINGS EDITOR")
        print("1. Change MODE (PAPER/LIVE)")
        print("2. Update TELEGRAM Keys")
        print("3. Back")
        
        ch = input("\nSelect: ")
        if ch == '1':
            new_mode = input("Enter Mode (PAPER/LIVE): ").upper()
            if new_mode in ['PAPER', 'LIVE']:
                update_env_variable("MODE", new_mode)
        elif ch == '2':
            token = input("Enter Bot Token: ")
            chat_id = input("Enter Chat ID: ")
            update_env_variable("TELEGRAM_BOT_TOKEN", token)
            update_env_variable("TELEGRAM_CHAT_ID", chat_id)
        elif ch == '3':
            break

def toggle_bot():
    global bot_process
    if bot_process:
        # Stop
        if sys.platform == "win32":
            bot_process.terminate()
        else:
            os.kill(bot_process.pid, signal.SIGTERM)
        bot_process = None
        print("🛑 Bot Stopped.")
    else:
        # Start
        print("🚀 Starting Engine...")
        cmd = [sys.executable, "run_bot.py"]
        if sys.platform == "win32":
            # Opens in a NEW separate window so you can see logs while keeping dashboard open
            bot_process = subprocess.Popen(cmd, creationflags=subprocess.CREATE_NEW_CONSOLE)
        else:
            bot_process = subprocess.Popen(cmd)
        print("✅ Bot Started in new window.")
    time.sleep(2)

def main():
    while True:
        cfg = load_config()
        show_header(cfg)
        
        print("1. 🟢 Start / 🔴 Stop Bot")
        print("2. 💰 Check Wallet Balance")
        print("3. 📨 Test Telegram Connection")
        print("4. ⚙️ Settings (Keys, Mode)")
        print("5. ❌ Exit Dashboard")
        
        choice = input("\nSelect Option [1-5]: ")
        
        if choice == '1':
            toggle_bot()
        elif choice == '2':
            menu_wallets()
        elif choice == '3':
            test_telegram()
        elif choice == '4':
            menu_settings()
        elif choice == '5':
            if bot_process:
                print("⚠️ Warning: Bot is still running. Stop it first? (y/n)")
                if input().lower() == 'y':
                    toggle_bot()
            print("Bye!")
            sys.exit()

if __name__ == "__main__":
    main()
