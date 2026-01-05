
import os
import sys
import subprocess
import time

# ─── COLOR CONFIG ───
class Colors:
    HEADER = '\033[95m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    GREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'

# ─── PATH SETUP ───
# Ensure we run from Project Root
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
os.chdir(CURRENT_DIR)

def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')

def print_banner():
    clear_screen()
    print(Colors.CYAN + "╔════════════════════════════════════════════════════════════╗" + Colors.ENDC)
    print(Colors.CYAN + "║   " + Colors.BOLD + "🌊 OCEAN HUNTER | COMMAND CENTER v2.5 (Stable)" + Colors.ENDC + Colors.CYAN + "           ║" + Colors.ENDC)
    print(Colors.CYAN + "╚════════════════════════════════════════════════════════════╝" + Colors.ENDC)
    print(f" {Colors.BOLD}📍 Root Path:{Colors.ENDC} {os.getcwd()}")
    
    # Check .env status
    if os.path.exists(".env"):
        print(f" {Colors.BOLD}🔐 Security:{Colors.ENDC}  {Colors.GREEN}.env Found{Colors.ENDC}")
    else:
        print(f" {Colors.BOLD}🔐 Security:{Colors.ENDC}  {Colors.FAIL}.env MISSING!{Colors.ENDC}")
    print(Colors.BLUE + "──────────────────────────────────────────────────────────────" + Colors.ENDC)

def run_script(script_path):
    full_path = os.path.abspath(script_path)
    print(f"\n{Colors.WARNING}>> Launching: {script_path}{Colors.ENDC}")
    time.sleep(1)
    
    python_exec = sys.executable
    try:
        # Critical: Run with CURRENT_DIR as cwd
        subprocess.run([python_exec, full_path], cwd=CURRENT_DIR, check=False)
    except Exception as e:
        print(f"{Colors.FAIL}Execution Error: {e}{Colors.ENDC}")
    
    input(f"\n{Colors.BLUE}[Press Enter to return to menu]{Colors.ENDC}")

def main_menu():
    while True:
        print_banner()
        print(f"{Colors.BOLD}ACTIONS:{Colors.ENDC}")
        print(" [1] 🚀 START BOT (Live Trading Mode)")
        print(" [2] 🛡️ START BOT (Safe Mode - Simulation)")
        print(" [3] 📡 TEST TELEGRAM CONNECTION (Critical Step)")
        print(" [4] 🛠️ RE-BUILD PROJECT (Update Logic via build.py)")
        print(" [5] ❌ EXIT")
        print("\n" + Colors.BLUE + "──────────────────────────────────────────────────────────────" + Colors.ENDC)
        
        choice = input(f"{Colors.GREEN}>> Select Option [1-5]: {Colors.ENDC}").strip()
        
        if choice == '1':
            os.environ['MODE'] = 'LIVE'
            run_script("run_bot.py")
        elif choice == '2':
            os.environ['MODE'] = 'SAFE'
            run_script("run_bot.py")
        elif choice == '3':
            # This file is usually in Ai_Tools or Root based on context. 
            # Assuming we create a temporary test wrapper or execute logic directly.
            # For now, we point to a dedicated test script if exists, or inline logic.
            if os.path.exists("test_telegram_conn.py"):
                 run_script("test_telegram_conn.py")
            else:
                 # Create temp test script
                 with open("test_telegram_conn.py", "w", encoding="utf-8") as f:
                     f.write("import os\nfrom dotenv import load_dotenv\nload_dotenv()\n")
                     f.write("print('Testing Token loading...')\n")
                     f.write("print(f'Token found: {bool(os.getenv(\"TELEGRAM_BOT_TOKEN\"))}')")
                 run_script("test_telegram_conn.py")
                 
        elif choice == '4':
            build_script = os.path.join("Ai_Tools", "build.py")
            run_script(build_script)
        elif choice == '5':
            print("\n👋 Exiting...")
            break
        else:
            print(f"\n{Colors.FAIL}Invalid input.{Colors.ENDC}")
            time.sleep(1)

if __name__ == "__main__":
    os.system('color') # Enable colors in CMD
    main_menu()
