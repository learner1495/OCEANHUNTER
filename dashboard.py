# AI_Tools/build.py — Maintenance Mode: Context & Git Sync Only
# ═══════════════════════════════════════════════════════════════
# Ref: OCEAN-SYNC-ONLY
# ═══════════════════════════════════════════════════════════════

import os
import sys
from datetime import datetime

# تلاش برای ایمپورت ماژول‌های ورک‌فلو
try:
    import context_gen
    import setup_git
except ImportError as e:
    print(f"❌ Critical Error: Missing workflow modules! {e}")
    sys.exit(1)

# ═══════════════════════════════════════════════════════════════
# EXECUTION
# ═══════════════════════════════════════════════════════════════

def force_update():
    print("="*60)
    print("      OCEAN HUNTER | FORCE CONTEXT UPDATE & GIT SYNC")
    print("="*60)
    
    # 1. Update Context
    print("\n[1/2] 🧠 Regenerating Project Context...")
    try:
        # فراخوانی مستقیم تابع تولید کانتکست
        context_gen.create_context_file()
        
        # بررسی اینکه آیا فایل واقعا آپدیت شده است؟
        context_path = os.path.join(os.path.dirname(__file__), "LATEST_PROJECT_CONTEXT.txt")
        if os.path.exists(context_path):
            t = datetime.fromtimestamp(os.path.getmtime(context_path))
            print(f"      ✅ Context File Updated Successfully.")
            print(f"      db Path: {context_path}")
            print(f"      🕒 Timestamp: {t}")
        else:
            print("      ⚠️ Warning: File generated but not found at expected path.")
            
    except Exception as e:
        print(f"      ❌ Context Generation Failed: {e}")
        return # اگر کانتکست ساخته نشد، گیت سینک نکنیم بهتر است

    # 2. Git Sync
    print("\n[2/2] 🐙 Syncing with GitHub...")
    try:
        # بررسی وجود پوشه گیت
        root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        if not os.path.exists(os.path.join(root, ".git")):
            print("      ⚙️ Initializing Git first...")
            setup_git.setup()
            
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M')
        commit_msg = f"Manual Sync: Preparation for Cloud Review {timestamp}"
        
        setup_git.sync(commit_msg)
        print("      ✅ Git Push Complete.")
        
    except Exception as e:
        print(f"      ❌ Git Sync Failed: {e}")

if __name__ == "__main__":
    force_update()
    print("\n✅ OPERATION FINISHED.")
    input("Press Enter to exit...")
