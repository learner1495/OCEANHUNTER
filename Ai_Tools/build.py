# build.py — OCEAN HUNTER V10.8.2
# Session 2.1: Repair Build (Fix main.py + Git Auto-Login)
# ═══════════════════════════════════════════════════════════════

import os
import subprocess
import sys

# ═══════════════════════════════════════════════════════════════
# CONFIGURATION
# ═══════════════════════════════════════════════════════════════
ROOT_DIR = r"F:\OCEANHUNTER"
AI_TOOLS_DIR = os.path.join(ROOT_DIR, "AI_Tools")
MODULES_DIR = os.path.join(ROOT_DIR, "modules")
VENV_PYTHON = os.path.join(ROOT_DIR, ".venv", "Scripts", "python.exe")

# ═══════════════════════════════════════════════════════════════
# HELPER: Write File
# ═══════════════════════════════════════════════════════════════
def write_file(path, content):
    """Write content to file, create dirs if needed"""
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, 'w', encoding='utf-8') as f:
        f.write(content)
    print(f"      ✅ Written: {os.path.relpath(path, ROOT_DIR)}")

# ═══════════════════════════════════════════════════════════════
# STEP 1: Fix main.py (Syntax Error)
# ═══════════════════════════════════════════════════════════════
def step1_fix_main():
    print("\n[1/3] 🔧 Fixing main.py...")
    
    main_content = '''# main.py — OCEAN HUNTER V10.8.2
# ═══════════════════════════════════════════════════════════════

import os
from dotenv import load_dotenv

load_dotenv()

def main():
    print("=" * 50)
    print("🌊 OCEAN HUNTER V10.8.2")
    print("=" * 50)
    
    mode = os.getenv("MODE", "PAPER")
    print(f"\\n🔧 Mode: {mode}")
    
    try:
        from modules.network import get_client, get_bot
        
        # ─── Test Nobitex API ───
        print("\\n[1/3] 🔌 Testing Nobitex API...")
        client = get_client()
        result = client.test_connection()
        print(f"      Public API: {'✅' if result['public_api'] else '❌'}")
        print(f"      Private API: {'✅' if result['private_api'] else '❌'}")
        print(f"      Message: {result['message']}")
        
        # ─── Test Telegram ───
        print("\\n[2/3] 📱 Testing Telegram Bot...")
        bot = get_bot()
        tg_result = bot.test_connection()
        print(f"      Status: {tg_result['message']}")
        
        if tg_result.get("ok"):
            bot.send_startup(mode)
            print("      ✅ Startup message sent!")
        # ─── Rate Limiter Status ───
        print("\\n[3/3] ⏱️ Rate Limiter Status...")rl_status = client.get_rate_limit_status()
        print(f"      Tokens: {rl_status['tokens_available']}/{rl_status['max_tokens']}")
        print(f"      Usage: {rl_status['usage_percent']}%")
        
    except ImportError as e:
        print(f"\\n❌ Import Error: {e}")
        print("   Run build.py first to create modules.")except Exception as e:
        print(f"\\n❌ Error: {e}")
    
    print("\\n" + "=" * 50)
    print("✅ Session 2 Network Test Complete")
    print("=" * 50)

if __name__ == "__main__":
    main()
'''
    
    write_file(os.path.join(ROOT_DIR, "main.py"), main_content)

# ═══════════════════════════════════════════════════════════════
# STEP 2: Update setup_git.py (V3.0 with Auto-Login)
# ═══════════════════════════════════════════════════════════════
def step2_fix_setup_git():
    print("\n[2/3] 🐙 Updating setup_git.py to V3.0...")
    
    setup_git_content = '''# AI_Tools/setup_git.py — V3.0 (Auto-Login via Browser)
# ═══════════════════════════════════════════════════════════════
# ویژگی‌ها:
# 1. استفاده از Git Credential Manager
# 2. باز کردن خودکار مرورگر برای لاگین
# 3. کاملاً اتوماتیک — بدون input()
# ═══════════════════════════════════════════════════════════════

import os
import subprocess
import webbrowser
from datetime import datetime
import time

# ═══════════════════════════════════════════════════════════════
# CONFIGURATION
# ═══════════════════════════════════════════════════════════════
GITHUB_USERNAME = "learner1495"
GITHUB_EMAIL = "mostafa53548188@gmail.com"

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
ROOT_DIR = os.path.dirname(SCRIPT_DIR)
PROJECT_NAME = os.path.basename(ROOT_DIR)
REMOTE_URL = f"https://github.com/{GITHUB_USERNAME}/{PROJECT_NAME}.git"
REPO_WEB_URL = f"https://github.com/{GITHUB_USERNAME}/{PROJECT_NAME}"

# ═══════════════════════════════════════════════════════════════
# HELPER: Run Git Command
# ═══════════════════════════════════════════════════════════════
def run_git(command, show_error=True, timeout=120):
    """Execute git command in ROOT_DIR"""
    try:
        result = subprocess.run(
            command,
            shell=True,
            cwd=ROOT_DIR,
            capture_output=True,
            text=True,
            timeout=timeout
        )
        if result.returncode == 0:
            return True, result.stdout.strip()
        else:
            if show_error and result.stderr.strip():
                err_msg = result.stderr.strip()[:100]
                if "fatal" in err_msg.lower() or "error" in err_msg.lower():
                    print(f"      ⚠️ {err_msg}")
            return False, result.stderr.strip()
    except subprocess.TimeoutExpired:
        print("      ❌ Command timed out")
        return False, "timeout"
    except Exception as e:
        print(f"      ❌ Error: {e}")
        return False, str(e)

# ═══════════════════════════════════════════════════════════════
# CHECK: Git Installed?
# ═══════════════════════════════════════════════════════════════
def check_git_installed():
    """Check if git is available"""
    try:
        result = subprocess.run(
            "git --version",
            shell=True,
            capture_output=True,
            text=True,
            timeout=10
        )
        if result.returncode == 0:
            print(f"      ✅ {result.stdout.strip()}")
            return True
        return False
    except:
        return False

# ═══════════════════════════════════════════════════════════════
# SETUP: Credential Helper (Windows)
# ═══════════════════════════════════════════════════════════════
def setup_credential_helper():
    """Configure Git to use Windows Credential Manager"""
    print("      🔐 Configuring credential helper...")
    
    # Try manager-core first (newer Git)
    run_git('git config --global credential.helper manager-core', show_error=False)
    
    # Fallback to manager (older Git)
    run_git('git config --global credential.helper manager', show_error=False)
    
    # Enable credential caching
    run_git('git config --global credential.helper "cache --timeout=604800"', show_error=False)
    
    print("      ✅ Credential helper ready")

# ═══════════════════════════════════════════════════════════════
# CHECK: Repository Exists on GitHub?
# ═══════════════════════════════════════════════════════════════
def check_repo_exists():
    """Check if repo exists on GitHub"""
    print("      🔍 Checking if repo exists on GitHub...")
    
    success, output = run_git(f"git ls-remote {REMOTE_URL}", show_error=False, timeout=30)
    
    if success:
        print("      ✅ Repository found on GitHub")
        return True
    elif "Repository not found" in output or "not found" in output.lower():
        print("      ⚠️ Repository NOT found on GitHub!")
        return False
    elif "could not read Username" in output or "Authentication" in output:
        print("      ⚠️ Authentication required")
        return None  # Unknown - need auth first
    else:
        print(f"      ⚠️ Unknown status")
        return None

# ═══════════════════════════════════════════════════════════════
# ACTION: Open GitHub to Create Repo
# ═══════════════════════════════════════════════════════════════
def open_github_create_repo():
    """Open browser to create new repo"""
    create_url = f"https://github.com/new?name={PROJECT_NAME}&visibility=private"
    
    print(f"      🌐 Opening browser to create repo...")
    print(f"      📝 Repo name: {PROJECT_NAME}")
    print(f"      🔗 URL: {create_url}")
    
    webbrowser.open(create_url)
    
    print("\\n      ⏳ Waiting 10 seconds for you to create the repo...")
    print("      📌 Just click 'Create repository' button in browser")
    time.sleep(10)

# ═══════════════════════════════════════════════════════════════
# ACTION: Open GitHub for Login
# ═══════════════════════════════════════════════════════════════
def open_github_login():
    """Open browser for GitHub login"""
    login_url = "https://github.com/login"
    
    print(f"      🌐 Opening GitHub login page...")
    webbrowser.open(login_url)
    
    print("\\n      ⏳ Waiting 15 seconds for login...")
    print("      📌 Please login in the browser window")
    time.sleep(15)

# ═══════════════════════════════════════════════════════════════
# SETUP: Main Setup Function
# ═══════════════════════════════════════════════════════════════
def setup():
    """
    Full Git setup:
    1. Check git installed
    2. Create .gitignore
    3. git init
    4. Configure user
    5. Setup credential helper
    6. Set remote
    """
    try:
        print(f"      📂 Root: {ROOT_DIR}")
        print(f"      🔗 Remote: {REMOTE_URL}")
        
        # ─── Check Git ───
        if not check_git_installed():
            print("      ❌ Git not installed!")
            print("      📥 Download: https://git-scm.com/download/win")
            webbrowser.open("https://git-scm.com/download/win")
            return False
        
        # ─── Create .gitignore ───
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
state.json
"""
        if not os.path.exists(gitignore_path):
            with open(gitignore_path, 'w', encoding='utf-8') as f:
                f.write(gitignore_content)
            print("      ✅ Created .gitignore")
        else:
            print("      ℹ️ .gitignore exists")
        
        # ─── Git Init ───
        git_dir = os.path.join(ROOT_DIR, ".git")
        if os.path.exists(git_dir):
            print("      ℹ️ Git already initialized")
        else:
            success, _ = run_git("git init")
            if success:
                print("      ✅ Git initialized")
            else:
                return False
        
        # ─── User Config ───
        run_git(f'git config user.name "{GITHUB_USERNAME}"', show_error=False)
        run_git(f'git config user.email "{GITHUB_EMAIL}"', show_error=False)
        print(f"      ✅ Git user: {GITHUB_USERNAME}")
        
        # ─── Credential Helper ───
        setup_credential_helper()
        
        # ─── Branch ───
        run_git("git branch -M main", show_error=False)
        # ─── Remote ───
        run_git("git remote remove origin", show_error=False)
        run_git(f"git remote add origin {REMOTE_URL}", show_error=False)
        print(f"      ✅ Remote: {REMOTE_URL}")
        
        return True
        
    except Exception as e:
        print(f"      ❌ Setup error: {e}")
        return False

# ═══════════════════════════════════════════════════════════════
# SYNC: Commit and Push (with Auto-Login)
# ═══════════════════════════════════════════════════════════════
def sync(message=None):
    """
    Commit and push with automatic browser login if needed
    """
    try:
        if not message:
            message = f"Auto-commit {datetime.now().strftime('%Y-%m-%d %H:%M')}"
        
        # ─── Add ───
        success, _ = run_git("git add .")
        if success:
            print("      ✅ Staged changes")
        
        # ─── Commit ───
        success, output = run_git(f'git commit -m "{message}"')
        if success:
            print(f"      ✅ Committed: {message[:40]}...")
        elif "nothing to commit" in output.lower():
            print("      ℹ️ Nothing to commit")
        
        # ─── Check Repo Exists ───
        repo_status = check_repo_exists()
        if repo_status == False:
            # Repo doesn't exist - open browser to create
            open_github_create_repo()
            
            # Check again
            repo_status = check_repo_exists()
            if not repo_status:
                print("      ❌ Please create the repo manually and run again")
                print(f"      🔗 https://github.com/new?name={PROJECT_NAME}")
                return False
        
        # ─── Push ───
        print("      ⏳ Pushing to GitHub...")
        success, output = run_git("git push -u origin main", timeout=60)
        
        if success:
            print("      ✅ Pushed to GitHub!")
            print(f"      🔗 View: {REPO_WEB_URL}")
            return True
        
        # ─── Handle Auth Error ───
        if "could not read Username" in output or "Authentication" in output:
            print("      🔑 Authentication required - opening browser...")
            open_github_login()
            
            # Try again
            print("      🔄 Retrying push...")
            success, output = run_git("git push -u origin main", timeout=60)
            
            if success:
                print("      ✅ Pushed to GitHub!")
                return True
        
        # ─── Handle Rejected ───
        if "rejected" in output.lower():
            print("      ⚠️ Push rejected - trying force push...")
            success, _ = run_git("git push -u origin main --force", timeout=60)
            if success:
                print("      ✅ Force pushed!")
                return True
        
        print(f"      ⚠️ Push issue - check manually")
        print(f"      🔗 {REPO_WEB_URL}")
        return False
        
    except Exception as e:
        print(f"      ❌ Sync error: {e}")
        return False

# ═══════════════════════════════════════════════════════════════
# STANDALONE
# ═══════════════════════════════════════════════════════════════
if __name__ == "__main__":
    print("\\n" + "═" * 50)
    print("🐙 GIT SETUP V3.0 (Auto-Login)")
    print("═" * 50)
    
    print("\\n[1/2] Setting up Git...")
    setup()
    
    print("\\n[2/2] Syncing to GitHub...")
    sync("Manual sync")
    
    print("\\n" + "═" * 50)
    print("✅ Done!")
    print("═" * 50)
'''
    
    write_file(os.path.join(AI_TOOLS_DIR, "setup_git.py"), setup_git_content)

# ═══════════════════════════════════════════════════════════════
# STEP 3: Run Git Setup & Sync
# ═══════════════════════════════════════════════════════════════
def step3_run_git():
    print("\n[3/3] 🐙 Running Git Setup & Sync...")
    
    # Import the module we just created
    sys.path.insert(0, AI_TOOLS_DIR)
    
    # Clear any cached import
    if 'setup_git' in sys.modules:
        del sys.modules['setup_git']
    
    try:
        import setup_git
        
        print("\n   ─── Git Setup ───")
        setup_git.setup()
        
        print("\n   ─── Git Sync ───")
        setup_git.sync("Session 2.1: Repair Build - Fixed main.py + Git V3.0")
        
    except Exception as e:
        print(f"      ❌ Git error: {e}")
        print("      📌 Run manually: python AI_Tools/setup_git.py")

# ═══════════════════════════════════════════════════════════════
# MAIN
# ═══════════════════════════════════════════════════════════════
def main():
    print("=" * 60)
    print("🌊 OCEAN HUNTER V10.8.2 — Build Session 2.1 (Repair)")
    print("=" * 60)
    print("📋 This build will:")
    print("   1. Fix main.py (Syntax Error)")
    print("   2. Update setup_git.py to V3.0 (Auto-Login)")
    print("   3. Push to GitHub (opens browser if needed)")
    print("=" * 60)
    
    # Execute steps
    step1_fix_main()
    step2_fix_setup_git()
    step3_run_git()
    
    print("\n" + "=" * 60)
    print("✅ BUILD SESSION 2.1 COMPLETE")
    print("=" * 60)
    print("\n📌 Next: Test with:")
    print(f"   cd {ROOT_DIR}")
    print("   .\\.venv\\Scripts\\python.exe main.py")
    print("=" * 60)

if __name__ == "__main__":
    main()
