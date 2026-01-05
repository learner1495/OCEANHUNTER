# AI_Tools/build.py — Phase 14: Smart Proxy Auto-Detect
# ═══════════════════════════════════════════════════════════════
# Ref: PHASE-14-PROXY-FIX
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

# A. Dashboard (Unchanged)
DASHBOARD_CONTENT = r'''
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
'''

# B. SMART TELEGRAM TESTER (Proxy Auto-Detect)
TELEGRAM_TESTER_CONTENT = r'''
import os
import requests
import sys
from dotenv import load_dotenv

load_dotenv()

TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

print("-" * 60)
print("📡 TELEGRAM CONNECTIVITY TEST (SMART PROXY)")
print("-" * 60)

if not TOKEN or not CHAT_ID:
    print("❌ ERROR: TELEGRAM_BOT_TOKEN or TELEGRAM_CHAT_ID missing.")
    sys.exit(1)

# List of common local proxies used by V2Ray, NekoBox, Clash, etc.
# We will try them one by one.
POTENTIAL_PROXIES = [
    None,                           # Try Direct first (might work if VPN is in TUN mode)
    "http://127.0.0.1:10809",       # V2Ray Default HTTP
    "socks5://127.0.0.1:10808",     # V2Ray Default SOCKS
    "http://127.0.0.1:2081",        # NekoBox/Hiddify HTTP
    "socks5://127.0.0.1:2080",      # NekoBox/Hiddify SOCKS
    "http://127.0.0.1:7890",        # Clash Default
    "socks5://127.0.0.1:7891",      # Clash SOCKS
    "http://127.0.0.1:1080",        # Generic Proxy
]

working_proxy = None
bot_username = ""

print(f"🔹 Token: {TOKEN[:5]}...{TOKEN[-5:]}")
print(f"🔹 Checking {len(POTENTIAL_PROXIES)} connection methods...")

# 1. FIND WORKING PROXY
for proxy_url in POTENTIAL_PROXIES:
    proxies_dict = {"https": proxy_url, "http": proxy_url} if proxy_url else None
    label = proxy_url if proxy_url else "DIRECT CONNECTION"
    
    print(f"\n   👉 Trying: {label} ... ", end="")
    try:
        url = f"https://api.telegram.org/bot{TOKEN}/getMe"
        resp = requests.get(url, proxies=proxies_dict, timeout=5)
        
        if resp.status_code == 200:
            print("✅ SUCCESS!")
            working_proxy = proxies_dict
            data = resp.json()
            bot_username = data['result']['username']
            print(f"      🎉 Connected to Bot: @{bot_username}")
            break
        else:
            print(f"❌ Failed (HTTP {resp.status_code})")
    except Exception as e:
        print("❌ Failed (Timeout/Error)")

if not working_proxy and not bot_username:
    print("\n" + "="*60)
    print("❌ CRITICAL: ALL CONNECTION ATTEMPTS FAILED.")
    print("   Please check your V2Ray/VPN settings.")
    print("   Look for 'Local Port' or 'HTTP Proxy Port' in your VPN app.")
    print("   Common ports: 10809, 2081, 7890")
    print("="*60)
    sys.exit(1)

# 2. SEND MESSAGE
print(f"\n[2] Sending Test Message using found path...")
try:
    msg = f"🔔 OCEAN HUNTER: Connection Successful!\n🚀 Proxy used: {working_proxy if working_proxy else 'Direct'}"
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    payload = {"chat_id": CHAT_ID, "text": msg}
    
    resp = requests.post(url, json=payload, proxies=working_proxy, timeout=10)
    data = resp.json()
    
    if data.get("ok"):
        print("   ✅ MESSAGE SENT SUCCESSFULLY!")
        print("   👉 Check your Telegram app now.")
        
        # Save working proxy to .env for future use (Optional logic could go here)
        print(f"   ℹ️  To make this permanent, you might need to set HTTPS_PROXY in .env")
        if working_proxy:
             print(f"       Example: HTTPS_PROXY={working_proxy['https']}")
    else:
        print(f"   ❌ Send Failed: {data}")

except Exception as e:
    print(f"   ❌ Error sending message: {e}")

print("-" * 60)
'''

# C. BAT Launcher (Unchanged)
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
    
    with open(os.path.join(PROJECT_ROOT, "run_dashboard.py"), "w", encoding="utf-8") as f:
        f.write(DASHBOARD_CONTENT)
    with open(os.path.join(PROJECT_ROOT, "test_telegram_conn.py"), "w", encoding="utf-8") as f:
        f.write(TELEGRAM_TESTER_CONTENT)
    with open(os.path.join(PROJECT_ROOT, "run_dashboard.bat"), "w", encoding="utf-8") as f:
        f.write(BAT_CONTENT)
    
    print("      ✅ Smart Telegram Tester installed.")

    print("\n[2/4] 📚 Git Sync...")
    if 'context_gen' in sys.modules:
        context_gen.create_context_file()
    if 'setup_git' in sys.modules:
        setup_git.sync("Phase 14: Smart Proxy Fix")
    print("      ✅ Synced")

    print("\n[3/4] 🚀 Launching Dashboard...")
    print("      ⚠️  A new window will open...")
    time.sleep(1)
    
    # Force open external window
    if sys.platform == "win32":
        bat_path = os.path.join(PROJECT_ROOT, "run_dashboard.bat")
        os.system(f'start "" "{bat_path}"')
    else:
        subprocess.run([sys.executable, "run_dashboard.py"], cwd=PROJECT_ROOT)

if __name__ == "__main__":
    main()
