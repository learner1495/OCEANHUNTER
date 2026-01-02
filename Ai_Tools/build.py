# AI_Tools/build.py — Build V6.0 (Copy of Video Tutorial)
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
# EXACT CODE FROM SCREENSHOT
# ═══════════════════════════════════════════════════════════════
# من دقیقاً کدی که در تصویر ویدیو پلیر بود را اینجا تایپ کردم
SIMPLE_TEST_PY = '''import requests

# URL from the video screenshot
url = "https://api.nobitex.ir/market/global-stats"

# payload={}  <-- Commented out in video
# headers = {} <-- Commented out in video

print(f"Connecting to {url} ...")

try:
    # EXACTLY line 8 from screenshot
    response = requests.request("POST", url)

    # EXACTLY line 10 from screenshot
    print(response.text)
    
except Exception as e:
    print(f"❌ Error: {e}")
'''

# ═══════════════════════════════════════════════════════════════
# BUILD STEPS
# ═══════════════════════════════════════════════════════════════
def main():
    print("\n🚀 BUILD V6.0 — THE SIMPLEST TEST")
    
    # Write the file
    test_file = os.path.join(ROOT, "simple_test.py")
    with open(test_file, "w", encoding="utf-8") as f:
        f.write(SIMPLE_TEST_PY)
    print(f"   📝 Created simple_test.py (Exact copy of video)")

    # Git Sync
    try:
        setup_git.setup()
        setup_git.sync("Build V6.0: Simple Video Test")
    except: pass

    # Run it
    print("\n" + "="*50)
    print("   RUNNING THE CODE FROM VIDEO...")
    print("="*50)
    subprocess.run([VENV_PYTHON, "simple_test.py"], cwd=ROOT)

if __name__ == "__main__":
    main()
