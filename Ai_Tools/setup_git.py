# AI_Tools/setup_git.py — V2.0 (Fully Automatic)
# ═══════════════════════════════════════════════════════════════
# این فایل دو تابع اصلی دارد:
# 1. setup() → راه‌اندازی Git (init, remote, .gitignore)
# 2. sync()  → Commit و Push تغییرات
# 
# هیچ input() ندارد — کاملاً اتوماتیک است
# ═══════════════════════════════════════════════════════════════

import os
import subprocess
from datetime import datetime

# ═══════════════════════════════════════════════════════════════
# CONFIGURATION (تنظیمات)
# ═══════════════════════════════════════════════════════════════
GITHUB_USERNAME = "learner1495"
GITHUB_EMAIL = "mostafa53548188@gmail.com"

# مسیرها
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))  # AI_Tools/
ROOT_DIR = os.path.dirname(SCRIPT_DIR)                    # Project Root
PROJECT_NAME = os.path.basename(ROOT_DIR)                 # نام پوشه = نام ریپو

# URL ریموت (اتوماتیک از نام پوشه)
REMOTE_URL = f"https://github.com/{GITHUB_USERNAME}/{PROJECT_NAME}.git"

# ═══════════════════════════════════════════════════════════════
# HELPER: اجرای دستورات Git
# ═══════════════════════════════════════════════════════════════
def run_git(command, show_error=True):
    """
    اجرای دستور Git در مسیر Root
    Returns: (success: bool, output: str)
    """
    try:
        result = subprocess.run(
            command,
            shell=True,
            cwd=ROOT_DIR,
            capture_output=True,
            text=True,
            timeout=60
        )
        
        if result.returncode == 0:
            return True, result.stdout.strip()
        else:
            if show_error:
                print(f"      ⚠️ Git warning: {result.stderr.strip()}")
            return False, result.stderr.strip()
            
    except subprocess.TimeoutExpired:
        print("      ❌ Git command timed out")
        return False, "timeout"
    except Exception as e:
        print(f"      ❌ Git error: {e}")
        return False, str(e)

# ═══════════════════════════════════════════════════════════════
# SETUP: راه‌اندازی Git (Step 7 در build.py)
# ═══════════════════════════════════════════════════════════════
def setup():
    """
    راه‌اندازی کامل Git:
    1. ساخت .gitignore
    2. git init (اگر نباشد)
    3. تنظیم user.name و user.email
    4. تنظیم remote origin
    
    Returns: bool (موفق یا نه)
    """
    try:
        print(f"      📂 Root: {ROOT_DIR}")
        print(f"      🔗 Remote: {REMOTE_URL}")
        
        # ─── 1. ساخت .gitignore ───
        gitignore_path = os.path.join(ROOT_DIR, ".gitignore")
        gitignore_content = """.venv/
__pycache__/
*.pyc
*.pyo
.env
.env.local
FULL_CODE.txt
_SNAPSHOTS/
*.log
.DS_Store
Thumbs.db
"""
        
        if not os.path.exists(gitignore_path):
            with open(gitignore_path, 'w', encoding='utf-8') as f:
                f.write(gitignore_content)
            print("      ✅ Created .gitignore")
        else:
            print("      ℹ️ .gitignore exists")
        
        # ─── 2. Git Init ───
        git_dir = os.path.join(ROOT_DIR, ".git")
        
        if os.path.exists(git_dir):
            print("      ℹ️ Git already initialized")
        else:
            success, _ = run_git("git init")
            if success:
                print("      ✅ Git initialized")
            else:
                print("      ❌ Git init failed")
                return False
        
        # ─── 3. تنظیم User Config ───
        run_git(f'git config user.name "{GITHUB_USERNAME}"', show_error=False)
        run_git(f'git config user.email "{GITHUB_EMAIL}"', show_error=False)
        print(f"      ✅ Git user: {GITHUB_USERNAME}")
        
        # ─── 4. تنظیم Branch به main ───
        run_git("git branch -M main", show_error=False)
        
        # ─── 5. تنظیم Remote ───
        # اول حذف remote قبلی (اگر باشد)
        run_git("git remote remove origin", show_error=False)
        
        # اضافه کردن remote جدید
        success, _ = run_git(f"git remote add origin {REMOTE_URL}")
        if success:
            print(f"      ✅ Remote set: {REMOTE_URL}")
        else:
            # شاید قبلاً وجود داشته
            print(f"      ℹ️ Remote: {REMOTE_URL}")
        
        return True
        
    except Exception as e:
        print(f"      ❌ Setup error: {e}")
        return False

# ═══════════════════════════════════════════════════════════════
# SYNC: Commit و Push (Step 8 در build.py)
# ═══════════════════════════════════════════════════════════════
def sync(message=None):
    """
    Commit و Push تغییرات به GitHub:
    1. git add .
    2. git commit -m "message"
    3. git push origin main
    
    Args:
        message: پیام commit (اختیاری)
    
    Returns: bool (موفق یا نه)
    """
    try:
        # پیام پیش‌فرض با تاریخ
        if not message:
            message = f"Auto-commit {datetime.now().strftime('%Y-%m-%d %H:%M')}"
        
        # ─── 1. Git Add ───
        success, _ = run_git("git add .")
        if success:
            print("      ✅ Staged all changes")
        else:
            print("      ⚠️ Nothing to stage")
        
        # ─── 2. Git Commit ───
        success, output = run_git(f'git commit -m "{message}"')
        if success:
            print(f"      ✅ Committed: {message}")
        else:
            if "nothing to commit" in output.lower():
                print("      ℹ️ Nothing to commit")
            else:
                print(f"      ⚠️ Commit issue: {output[:50]}")
        
        # ─── 3. Git Push ───
        print("      ⏳ Pushing to GitHub...")
        success, output = run_git("git push -u origin main")
        
        if success:
            print("      ✅ Pushed to GitHub")
            return True
        else:
            # شاید اولین push باشد یا نیاز به pull باشد
            if "rejected" in output.lower():
                print("      ⚠️ Push rejected — trying force push...")
                success, _ = run_git("git push -u origin main --force")
                if success:
                    print("      ✅ Force pushed")
                    return True
            
            print(f"      ⚠️ Push issue (check manually)")
            return True  # ادامه بده حتی با مشکل
        
    except Exception as e:
        print(f"      ❌ Sync error: {e}")
        return False

# ═══════════════════════════════════════════════════════════════
# STANDALONE: اجرای مستقیم
# ═══════════════════════════════════════════════════════════════
if __name__ == "__main__":
    print("\n" + "═" * 50)
    print("🐙 GIT SETUP V2.0 (Standalone Mode)")
    print("═" * 50)
    
    print("\n[1/2] Setting up Git...")
    setup()
    
    print("\n[2/2] Syncing to GitHub...")
    sync("Manual setup commit")
    
    print("\n" + "═" * 50)
    print("✅ Done!")
    print("═" * 50)
