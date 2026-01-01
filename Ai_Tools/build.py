# AI_Tools/build.py — V4.0 (No main.py rewrite)
# ═══════════════════════════════════════════════════════════════
# 9 مرحله — main.py دست نمی‌خورد
# ═══════════════════════════════════════════════════════════════

import os
import sys
import subprocess
import socket
from datetime import datetime

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

MAIN_FILE = "main.py"
errors = []


def log_error(step, error):
    errors.append(f"[{step}] {error}")
    print(f"      ⚠️ Error: {error}")


# ═══════════════════════════════════════════════════════════════
# STEPS
# ═══════════════════════════════════════════════════════════════

def step1_system():
    print("\n[1/9] 🌐 System Check...")
    try:
        socket.create_connection(("8.8.8.8", 53), timeout=3)
        print("      ✅ Internet OK")
    except Exception as e:
        log_error("Step1", f"No internet - {e}")


def step2_venv():
    print("\n[2/9] 🐍 Virtual Environment...")
    try:
        if os.path.exists(VENV_PYTHON):
            print("      ✅ Exists")
            return
        subprocess.run([sys.executable, "-m", "venv", VENV_PATH], check=True)
        print("      ✅ Created")
    except Exception as e:
        log_error("Step2", e)


def step3_deps():
    print("\n[3/9] 📦 Dependencies...")
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
        log_error("Step3", e)


def step4_folders():
    print("\n[4/9] 📁 Folders...")
    network_dir = os.path.join(ROOT, "modules", "network")
    if not os.path.exists(network_dir):
        os.makedirs(network_dir)
        print(f"      ✅ Created: modules/network/")
    else:
        print("      ✅ Exists")


def step5_files():
    print("\n[5/9] 📝 Files...")
    print("      ℹ️ Skipped (main.py not touched)")


def step6_modify():
    print("\n[6/9] ✏️ Modify...")
    print("      ℹ️ Skipped (no modifications)")


def step7_context():
    print("\n[7/9] 📋 Context Generation...")
    try:
        context_gen.create_context_file()
        print("      ✅ Context created")
    except Exception as e:
        log_error("Step7", e)


def step8_git():
    print("\n[8/9] 🐙 Git Sync...")
    try:
        setup_git.setup()
        setup_git.sync(f"Build V4.0: {datetime.now().strftime('%Y-%m-%d %H:%M')}")
        print("      ✅ Git synced")
    except Exception as e:
        log_error("Step8", e)


def step9_launch():
    print("\n[9/9] 🚀 Launch...")
    main_path = os.path.join(ROOT, MAIN_FILE)
    if os.path.exists(main_path):
        print("      " + "─" * 40)
        subprocess.run([VENV_PYTHON, main_path], cwd=ROOT)
    else:
        print(f"      ℹ️ No {MAIN_FILE}")


# ═══════════════════════════════════════════════════════════════
# MAIN
# ═══════════════════════════════════════════════════════════════

def main():
    start_time = datetime.now()

    print("\n" + "═" * 60)
    print(f"🔧 BUILD V4.0 — Infrastructure Only")
    print(f"📁 Project: {os.path.basename(ROOT)}")
    print(f"⏰ Started: {start_time.strftime('%Y-%m-%d %H:%M:%S')}")
    print("═" * 60)

    try:
        step1_system()
        step2_venv()
        step3_deps()
        step4_folders()
        step5_files()
        step6_modify()
        step7_context()
        step8_git()
        step9_launch()

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
            print(f"⚠️ BUILD COMPLETE WITH {len(errors)} ERROR(S):")
            for err in errors:
                print(f"   • {err}")
        else:
            print("✅ BUILD COMPLETE — NO ERRORS")
        print("─" * 60)
        print(f"⏱️ Duration: {duration}s")
        print(f"🏁 Finished: {end_time.strftime('%H:%M:%S')}")
        print("═" * 60 + "\n")


if __name__ == "__main__":
    main()
