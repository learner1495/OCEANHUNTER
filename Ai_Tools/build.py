# AI_Tools/build.py — Phase 12: Final Infrastructure Fix
# ═══════════════════════════════════════════════════════════════
# Ref: PHASE-12-FINAL-ROOT-FIX
# ═══════════════════════════════════════════════════════════════

import os
import sys
import subprocess
import time

# ═══════════════════════════════════════════════════════════════
# 1. SETUP PATHS & IMPORTS
# ═══════════════════════════════════════════════════════════════

# Determine paths relative to THIS script (Ai_Tools/build.py)
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__)) # F:\OCEANHUNTER\Ai_Tools
PROJECT_ROOT = os.path.dirname(SCRIPT_DIR)              # F:\OCEANHUNTER
sys.path.append(SCRIPT_DIR)                             # Allow importing siblings

# Try imports
try:
    import context_gen
    import setup_git
except ImportError:
    print("⚠️ Warning: context_gen or setup_git not found in Ai_Tools.")

VENV_PYTHON = os.path.join(PROJECT_ROOT, ".venv", "Scripts", "python.exe")

# ═══════════════════════════════════════════════════════════════
# 2. TEMPLATES (DASHBOARD & BAT)
# ═══════════════════════════════════════════════════════════════

DASHBOARD_CONTENT = r'''
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
'''

BAT_CONTENT = r'''
@echo off
cd /d "%~dp0"
title OCEAN HUNTER - LAUNCHER
color 0B
cls
echo ======================================================
echo    OCEAN HUNTER v10.8.2 | LAUNCHER
echo ======================================================
echo.
echo [INFO] Checking Python Environment...

if exist ".venv\Scripts\python.exe" (
    echo [OK] Using Virtual Environment (.venv)
    ".venv\Scripts\python.exe" run_dashboard.py
) else (
    echo [WARN] .venv not found. Attempting system python...
    python run_dashboard.py
)

if %ERRORLEVEL% NEQ 0 (
    echo.
    echo [ERROR] Could not launch dashboard.
    pause
)
'''

# ═══════════════════════════════════════════════════════════════
# 3. BUILD LOGIC
# ═══════════════════════════════════════════════════════════════

def main():
    print(f"\n[1/4] 🏗️  Target Root: {PROJECT_ROOT}")
    
    # 1. Generate run_dashboard.py in ROOT
    dash_path = os.path.join(PROJECT_ROOT, "run_dashboard.py")
    try:
        with open(dash_path, "w", encoding="utf-8") as f:
            f.write(DASHBOARD_CONTENT)
        print(f"      ✅ Generated: {dash_path}")
    except Exception as e:
        print(f"      ❌ Error writing dashboard: {e}")
        return

    # 2. Generate run_dashboard.bat in ROOT
    bat_path = os.path.join(PROJECT_ROOT, "run_dashboard.bat")
    try:
        with open(bat_path, "w", encoding="utf-8") as f:
            f.write(BAT_CONTENT)
        print(f"      ✅ Generated: {bat_path}")
    except Exception as e:
        print(f"      ❌ Error writing bat file: {e}")

    # 3. Update Context (Standard Workflow)
    print("\n[2/4] 📚 Updating Context & Git...")
    try:
        if 'context_gen' in sys.modules:
            context_gen.create_context_file()
            print("      ✅ Context Updated")
        if 'setup_git' in sys.modules:
            setup_git.sync("Phase 12: Dashboard Fix")
            print("      ✅ Git Synced")
    except Exception as e:
        print(f"      ⚠️  Context/Git Warning: {e}")

    # 4. Auto-Launch Dashboard
    print("\n[3/4] 🚀 Launching Dashboard...")
    print("      (A new menu should appear. If not, use 'run_dashboard.bat' in project root)")
    time.sleep(2)

    runner = VENV_PYTHON if os.path.exists(VENV_PYTHON) else sys.executable
    
    # CRITICAL: Run subprocess relative to PROJECT_ROOT, not Ai_Tools
    try:
        subprocess.run([runner, "run_dashboard.py"], cwd=PROJECT_ROOT)
    except Exception as e:
        print(f"      ❌ Launch Failed: {e}")
        print(f"      👉 Please go to {PROJECT_ROOT} and double-click run_dashboard.bat")

if __name__ == "__main__":
    main()
