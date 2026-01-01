#!/usr/bin/env python3
"""
BUILD.PY V3.5 — CLEAN BUILD
فقط اجرا می‌کند، هیچ فایلی را بازنویسی نمی‌کند
"""

import os
import sys
import subprocess
import socket
from datetime import datetime

# ═══ Import ماژول‌های داخلی ═══
import context_gen
import setup_git

# ═══════════════════════════════════════════════════════════════
# PATHS
# ═══════════════════════════════════════════════════════════════
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(SCRIPT_DIR)
VENV_PATH = os.path.join(ROOT, ".venv")

if sys.platform == "win32":
    VENV_PYTHON = os.path.join(VENV_PATH, "Scripts", "python.exe")
else:
    VENV_PYTHON = os.path.join(VENV_PATH, "bin", "python")

# ═══════════════════════════════════════════════════════════════
# CONFIG
# ═══════════════════════════════════════════════════════════════
MAIN_FILE = "main.py"

# ═══════════════════════════════════════════════════════════════
# ERROR TRACKING
# ═══════════════════════════════════════════════════════════════
errors = []

def log_error(step, error):
    """ثبت خطا بدون توقف"""
    errors.append(f"[{step}] {error}")
    print(f"      ⚠️ Error: {error}")

# ═══════════════════════════════════════════════════════════════
# STEP 1: System Check
# ═══════════════════════════════════════════════════════════════
def step1_system():
    print("\n[1/6] 🌐 System Check...")
    try:
        socket.create_connection(("8.8.8.8", 53), timeout=3)
        print("      ✅ Internet OK")
    except Exception as e:
        log_error("System", f"No internet - {e}")

# ═══════════════════════════════════════════════════════════════
# STEP 2: Virtual Environment
# ═══════════════════════════════════════════════════════════════
def step2_venv():
    print("\n[2/6] 🐍 Virtual Environment...")
    try:
        if os.path.exists(VENV_PYTHON):
            print("      ✅ Exists")
            return
        subprocess.run([sys.executable, "-m", "venv", VENV_PATH], check=True)
        print("      ✅ Created")
    except Exception as e:
        log_error("Venv", e)

# ═══════════════════════════════════════════════════════════════
# STEP 3: Dependencies
# ═══════════════════════════════════════════════════════════════
def step3_deps():
    print("\n[3/6] 📦 Dependencies...")
    try:
        req = os.path.join(ROOT, "requirements.txt")
        if not os.path.exists(req):
            print("      ℹ️ No requirements.txt")
            return
        subprocess.run(
            [VENV_PYTHON, "-m", "pip", "install", "-r", req, "-q"],
            capture_output=True,
            check=True
        )
        print("      ✅ Installed")
    except Exception as e:
        log_error("Deps", e)

# ═══════════════════════════════════════════════════════════════
# STEP 4: Context Generation
# ═══════════════════════════════════════════════════════════════
def step4_context():
    print("\n[4/6] 📋 Context Generation...")
    try:
        context_gen.create_context_file()
        print("      ✅ Context created")
    except Exception as e:
        log_error("Context", e)

# ═══════════════════════════════════════════════════════════════
# STEP 5: Git Sync
# ═══════════════════════════════════════════════════════════════
def step5_git():
    print("\n[5/6] 🐙 Git Sync...")
    try:
        # فقط sync — اگر .git نباشد، خودش setup می‌کند
        result = setup_git.sync(f"Build: {datetime.now().strftime('%Y-%m-%d %H:%M')}")
        if result:
            print("      ✅ Git synced")
        else:
            log_error("Git", "Sync returned False")
    except Exception as e:
        log_error("Git", e)

# ═══════════════════════════════════════════════════════════════
# STEP 6: Launch Main
# ═══════════════════════════════════════════════════════════════
def step6_launch():
    print("\n[6/6] 🚀 Launch...")
    try:
        main_path = os.path.join(ROOT, MAIN_FILE)
        if os.path.exists(main_path):
            print("      " + "─" * 40)
            subprocess.run([VENV_PYTHON, main_path], cwd=ROOT)
        else:
            print(f"      ℹ️ No {MAIN_FILE} — skipping launch")
    except Exception as e:
        log_error("Launch", e)

# ═══════════════════════════════════════════════════════════════
# MAIN
# ═══════════════════════════════════════════════════════════════
def main():
    start_time = datetime.now()

    print("\n" + "═" * 60)
    print(f"🔧 BUILD V3.5 — CLEAN BUILD")
    print(f"📁 Project: {os.path.basename(ROOT)}")
    print(f"⏰ Started: {start_time.strftime('%Y-%m-%d %H:%M:%S')}")
    print("═" * 60)

    try:
        step1_system()
        step2_venv()
        step3_deps()
        step4_context()
        step5_git()
        step6_launch()
    except KeyboardInterrupt:
        print("\n\n⛔ Build cancelled by user")
        errors.append("KeyboardInterrupt")

    except Exception as e:
        print(f"\n\n💥 Critical error: {e}")
        errors.append(f"Critical: {e}")

    finally:
        end_time = datetime.now()
        duration = (end_time - start_time).seconds

        print("\n" + "═" * 60)

        if errors:
            print(f"⚠️ BUILD COMPLETED WITH {len(errors)} ERROR(S)")
            print("─" * 60)
            for err in errors:
                print(f"   • {err}")
                exit_code = 1
        else:
            print("✅ BUILD COMPLETE — NO ERRORS")
            exit_code = 0

        print("─" * 60)
        print(f"⏱️ Duration: {duration}s")
        print(f"🏁 Finished: {end_time.strftime('%H:%M:%S')}")
        print("═" * 60)

        sys.exit(exit_code)

# ═══════════════════════════════════════════════════════════════
# ENTRY POINT
# ═══════════════════════════════════════════════════════════════
if __name__ == "__main__":
    main()
