
import os
import sys
import time
import subprocess
import signal
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
    print("🌊 OCEAN HUNTER COMMANDER v1.0")
    print("═" * 40)
    print(f"📡 MODE:      {config['MODE']}")
    print(f"🤖 BOT STATE: {'🟢 RUNNING' if bot_process else '🔴 STOPPED'}")
    print("═" * 40)

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
        print("2. Update MEXC API Key")
        print("3. Update MEXC Secret Key")
        print("4. Back")
        
        ch = input("\nSelect: ")
        if ch == '1':
            new_mode = input("Enter Mode (PAPER/LIVE): ").upper()
            if new_mode in ['PAPER', 'LIVE']:
                update_env_variable("MODE", new_mode)
        elif ch == '2':
            new_key = input("Enter New API Key: ")
            update_env_variable("MEXC_API_KEY", new_key)
        elif ch == '3':
            new_sec = input("Enter New Secret Key: ")
            update_env_variable("MEXC_SECRET_KEY", new_sec)
        elif ch == '4':
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
        cmd = [sys.executable, "run_bot.py"]
        # Use Popen to run in background (new console window on Windows is better)
        if sys.platform == "win32":
            bot_process = subprocess.Popen(cmd, creationflags=subprocess.CREATE_NEW_CONSOLE)
        else:
            bot_process = subprocess.Popen(cmd)
        print("✅ Bot Started in background.")
    time.sleep(2)

def main():
    while True:
        cfg = load_config()
        show_header(cfg)
        
        print("1. 🟢 Start / 🔴 Stop Bot")
        print("2. 💰 Check Wallet Balance")
        print("3. ⚙️ Settings (Keys, Mode)")
        print("4. ❌ Exit Dashboard")
        
        choice = input("\nSelect Option [1-4]: ")
        
        if choice == '1':
            toggle_bot()
        elif choice == '2':
            menu_wallets()
        elif choice == '3':
            menu_settings()
        elif choice == '4':
            if bot_process:
                print("⚠️ Warning: Bot is still running. Stop it first? (y/n)")
                if input().lower() == 'y':
                    toggle_bot()
            print("Bye!")
            sys.exit()

if __name__ == "__main__":
    main()
