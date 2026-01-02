# AI_Tools/build.py — Build V6.1 (Video Code + VPN Fix)
# ═══════════════════════════════════════════════════════════════

import os
import sys
import subprocess
import setup_git
import context_gen

# ═══════════════════════════════════════════════════════════════
# CONFIG
# ═══════════════════════════════════════════════════════════════
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(SCRIPT_DIR)
VENV_PATH = os.path.join(ROOT, ".venv")
if sys.platform == "win32":
    VENV_PYTHON = os.path.join(VENV_PATH, "Scripts", "python.exe")
else:
    VENV_PYTHON = os.path.join(VENV_PATH, "bin", "python")

# ═══════════════════════════════════════════════════════════════
# SIMPLE TEST WITH VPN DIAGNOSTICS
# ═══════════════════════════════════════════════════════════════
SIMPLE_TEST_PY = '''import requests
import sys

print("-" * 50)
print("🔍 DIAGNOSTIC MODE: Checking your connection...")

# 1. Check if VPN is changing our IP
try:
    print("   🌐 Checking Internet & IP...")
    ip_info = requests.get("http://ip-api.com/json", timeout=10).json()
    print(f"   ✅ Internet OK! Your IP: {ip_info['query']}")
    print(f"   🌍 Location: {ip_info['country']} (If this is Iran, VPN is OFF/Not working)")
except Exception as e:
    print(f"   ❌ Internet Check Failed: {e}")
    print("   ⚠️ WARNING: If you have no internet, Nobitex will definitely fail.")

print("-" * 50)

# 2. Run the simple Nobitex code (Video Method)
url = "https://api.nobitex.ir/market/global-stats"
print(f"🚀 Connecting to {url} ...")

try:
    # verify=False prevents SSL errors common with some VPNs
    response = requests.request("POST", url, verify=False, timeout=15)
    
    if response.status_code == 200:
        print("\\n✅ SUCCESS! (Data received):")
        print(response.text[:200] + "... (truncated)") 
    else:
        print(f"\\n❌ Connected, but server said: HTTP {response.status_code}")
        print(response.text)

except Exception as e:
    print(f"\\n❌ FAILURE: {e}")
    if "11001" in str(e):
        print("   👉 CAUSE: DNS Failure. Your VPN is likely NOT tunnelling Python traffic.")
    elif "SSL" in str(e):
        print("   👉 CAUSE: SSL Block. The firewall intercepted the secure connection.")
'''

# ═══════════════════════════════════════════════════════════════
# BUILD STEPS
# ═══════════════════════════════════════════════════════════════
def main():
    print("\n🚀 BUILD V6.1 — SIMPLE VPN TEST")
    
    # Write the file
    test_file = os.path.join(ROOT, "simple_test.py")
    with open(test_file, "w", encoding="utf-8") as f:
        f.write(SIMPLE_TEST_PY)
    print(f"   📝 Created simple_test.py (With VPN Diagnostics)")

    # Git Sync
    try:
        setup_git.setup()
        setup_git.sync("Build V6.1: VPN Diagnostic Test")
    except: pass

    # Run it
    print("\n" + "="*50)
    print("   RUNNING TEST (PLEASE ENSURE VPN IS ON)...")
    print("="*50)
    subprocess.run([VENV_PYTHON, "simple_test.py"], cwd=ROOT)

if __name__ == "__main__":
    main()
