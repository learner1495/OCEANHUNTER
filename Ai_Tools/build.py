# AI_Tools/build.py — Phase 13: Final Setup & Telegram Tester
# ═══════════════════════════════════════════════════════════════
# Ref: PHASE-13-TELEGRAM-TEST
# ═══════════════════════════════════════════════════════════════

import os
import sys
import subprocess
import time

# ═══════════════════════════════════════════════════════════════
# 1. SETUP PATHS
# ═══════════════════════════════════════════════════════════════

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(SCRIPT_DIR)
sys.path.append(SCRIPT_DIR)

try:
    import context_gen
    import setup_git
except ImportError:
    pass

VENV_PYTHON = os.path.join(PROJECT_ROOT, ".venv", "Scripts", "python.exe")

# ═══════════════════════════════════════════════════════════════
# 2. TEMPLATES
# ═══════════════════════════════════════════════════════════════

# A. The Dashboard
DASHBOARD_CONTENT = r'''
import os
import sys
import subprocess
import time
from dotenv import load_dotenv

# Load Env explicitly to be safe
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
    print(Colors.CYAN + "║   " + Colors.BOLD + "🌊 OCEAN HUNTER | COMMAND CENTER v2.6" + Colors.ENDC + Colors.CYAN + "                  ║" + Colors.ENDC)
    print(Colors.CYAN + "╚════════════════════════════════════════════════════════════╝" + Colors.ENDC)
    print(f" 📍 Root: {os.getcwd()}")
    
    if os.getenv("TELEGRAM_BOT_TOKEN") and os.getenv("TELEGRAM_CHAT_ID"):
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
        print(" [3] 📡 TEST TELEGRAM (Send Message)")
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
'''

# B. The Telegram Tester
TELEGRAM_TESTER_CONTENT = r'''
import os
import requests
import sys
from dotenv import load_dotenv

# Force load .env
load_dotenv()

TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

print("-" * 50)
print("📡 TELEGRAM CONNECTIVITY TEST")
print("-" * 50)

if not TOKEN or not CHAT_ID:
    print("❌ ERROR: TELEGRAM_BOT_TOKEN or TELEGRAM_CHAT_ID not found in .env")
    print("   Please check your .env file.")
    sys.exit(1)

print(f"🔹 Token: {TOKEN[:5]}...{TOKEN[-5:]}")
print(f"🔹 Chat ID: {CHAT_ID}")

# 1. Check Bot Info
print("\n[1] Checking Bot Status...")
try:
    url = f"https://api.telegram.org/bot{TOKEN}/getMe"
    resp = requests.get(url, timeout=10)
    data = resp.json()
    
    if data.get("ok"):
        bot_name = data["result"]["first_name"]
        print(f"   ✅ Connected as: @{data['result']['username']} ({bot_name})")
    else:
        print(f"   ❌ API Error: {data}")
        sys.exit(1)
except Exception as e:
    print(f"   ❌ Connection Failed: {e}")
    print("   (Check your VPN/Internet)")
    sys.exit(1)

# 2. Send Test Message
print("\n[2] Sending Test Message...")
try:
    msg = "🔔 OCEAN HUNTER: Connection Successful!\nYour bot is ready to trade."
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    payload = {"chat_id": CHAT_ID, "text": msg}
    
    resp = requests.post(url, json=payload, timeout=10)
    data = resp.json()
    
    if data.get("ok"):
        print("   ✅ MESSAGE SENT SUCCESSFULLY!")
        print("   👉 Check your Telegram app now.")
    else:
        print(f"   ❌ Send Failed: {data}")

except Exception as e:
    print(f"   ❌ Error sending message: {e}")

print("-" * 50)
'''

# C. The BAT Launcher
BAT_CONTENT = r'''
@echo off
cd /d "%~dp0"
title OCEAN HUNTER
color 0B
cls
if exist ".venv\Scripts\python.exe" (
    ".venv\Scripts\python.exe" run_dashboard.py
) else (
    python run_dashboard.py
)
'''

# ═══════════════════════════════════════════════════════════════
# 3. BUILD PROCESS
# ═══════════════════════════════════════════════════════════════

def main():
    print(f"\n[1/4] 🏗️  Building in: {PROJECT_ROOT}")
    
    # 1. Create run_dashboard.py
    with open(os.path.join(PROJECT_ROOT, "run_dashboard.py"), "w", encoding="utf-8") as f:
        f.write(DASHBOARD_CONTENT)
    print("      ✅ run_dashboard.py created")

    # 2. Create test_telegram_conn.py
    with open(os.path.join(PROJECT_ROOT, "test_telegram_conn.py"), "w", encoding="utf-8") as f:
        f.write(TELEGRAM_TESTER_CONTENT)
    print("      ✅ test_telegram_conn.py created")

    # 3. Create run_dashboard.bat
    with open(os.path.join(PROJECT_ROOT, "run_dashboard.bat"), "w", encoding="utf-8") as f:
        f.write(BAT_CONTENT)
    print("      ✅ run_dashboard.bat created")

    # 4. Context & Git
    print("\n[2/4] 📚 Git Sync...")
    if 'context_gen' in sys.modules:
        context_gen.create_context_file()
    if 'setup_git' in sys.modules:
        setup_git.sync("Phase 13: Telegram Tools")
    print("      ✅ Synced")

    # 5. Launch
    print("\n[3/4] 🚀 Launching Dashboard...")
    print("      (Please select Option 3 to test Telegram)")
    time.sleep(2)
    
    runner = VENV_PYTHON if os.path.exists(VENV_PYTHON) else sys.executable
    try:
        subprocess.run([runner, "run_dashboard.py"], cwd=PROJECT_ROOT)
    except KeyboardInterrupt:
        print("\n👋 Exited by user.")
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    main()
