
import os
import sys
import subprocess
import time
from dotenv import load_dotenv

load_dotenv()

class Colors:
    HEADER = '\033[95m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    GREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
os.chdir(CURRENT_DIR)

def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')

def print_banner():
    clear_screen()
    print(Colors.CYAN + "╔════════════════════════════════════════════════════════════╗" + Colors.ENDC)
    print(Colors.CYAN + "║   " + Colors.BOLD + "🌊 OCEAN HUNTER | COMMAND CENTER v2.7" + Colors.ENDC + Colors.CYAN + "                  ║" + Colors.ENDC)
    print(Colors.CYAN + "╚════════════════════════════════════════════════════════════╝" + Colors.ENDC)
    print(f" 📍 Root: {os.getcwd()}")
    
    if os.getenv("TELEGRAM_BOT_TOKEN"):
        print(f" 🔐 Telegram: {Colors.GREEN}Configured{Colors.ENDC}")
    else:
        print(f" 🔐 Telegram: {Colors.FAIL}MISSING IN .ENV{Colors.ENDC}")
    print(Colors.BLUE + "──────────────────────────────────────────────────────────────" + Colors.ENDC)

def run_script(script_name):
    print(f"\n{Colors.WARNING}>> Running {script_name}...{Colors.ENDC}")
    time.sleep(1)
    python_exec = sys.executable
    try:
        subprocess.run([python_exec, script_name], cwd=CURRENT_DIR)
    except Exception as e:
        print(f"{Colors.FAIL}Error: {e}{Colors.ENDC}")
    input(f"\n{Colors.BLUE}[Press Enter]{Colors.ENDC}")

def main_menu():
    while True:
        print_banner()
        print(" [1] 🚀 START BOT (Live)")
        print(" [2] 🛡️ START BOT (Safe Mode)")
        print(" [3] 📡 TEST TELEGRAM (Auto-Detect Proxy)")
        print(" [4] 🛠️ RE-BUILD (Update Code)")
        print(" [5] ❌ EXIT")
        print("\n" + Colors.BLUE + "──────────────────────────────────────────────────────────────" + Colors.ENDC)
        
        try:
            choice = input(f"{Colors.GREEN}>> Select: {Colors.ENDC}").strip()
        except:
            break

        if choice == '1':
            os.environ['MODE'] = 'LIVE'
            run_script("run_bot.py")
        elif choice == '2':
            os.environ['MODE'] = 'SAFE'
            run_script("run_bot.py")
        elif choice == '3':
            run_script("test_telegram_conn.py")
        elif choice == '4':
            run_script(os.path.join("Ai_Tools", "build.py"))
        elif choice == '5':
            break
        else:
            print("Invalid.")
            time.sleep(0.5)

if __name__ == "__main__":
    os.system('color')
    main_menu()
