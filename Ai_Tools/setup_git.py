#!/usr/bin/env python3
"""
SETUP_GIT.PY V3.0 — GIT MANAGER WITH AUTO-LOGIN
Functions: setup() = one-time init | sync() = every build
Auth: Git Credential Manager (Browser OAuth)
"""
import os
import subprocess
import sys
import platform
from datetime import datetime

# === CONFIGURATION ===
GIT_USERNAME = "learner1495"
GIT_EMAIL = "mostafa53548188@gmail.com"
BRANCH = "main"

# === PATH SETUP ===
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
ROOT_DIR = os.path.dirname(SCRIPT_DIR)
REPO_NAME = os.path.basename(ROOT_DIR)
REMOTE_URL = f"https://github.com/{GIT_USERNAME}/{REPO_NAME}.git"


def run(cmd, cwd=None):
    """Run command and return (success, output)"""
    try:
        result = subprocess.run(
            cmd if isinstance(cmd, list) else cmd.split(),
            cwd=cwd or ROOT_DIR,
            capture_output=True,
            text=True,
            timeout=120
        )
        output = result.stdout.strip() or result.stderr.strip()
        return result.returncode == 0, output
    except Exception as e:
        return False, str(e)


def print_status(msg, success=True):
    """Print formatted status"""
    symbol = "✅" if success else "❌"
    print(f"      {symbol} {msg}")


def configure_credential_manager():
    """Setup Git Credential Manager for browser-based auth"""
    print("\n   🔐 Configuring Git Credential Manager...")
    
    system = platform.system()
    
    if system == "Windows":
        run(["git", "config", "--global", "credential.helper", "manager"])
        print_status("Windows Credential Manager configured")
    elif system == "Darwin":
        run(["git", "config", "--global", "credential.helper", "osxkeychain"])
        print_status("macOS Keychain configured")
    else:
        success, _ = run(["git", "credential-manager", "--version"])
        if success:
            run(["git", "config", "--global", "credential.helper", "manager-core"])
            print_status("Git Credential Manager Core configured")
        else:
            run(["git", "config", "--global", "credential.helper", "store"])
            print_status("Git credential store configured (fallback)", False)
    
    return True


def setup():
    """One-time Git initialization"""
    print("\n" + "=" * 60)
    print("   🚀 SETUP_GIT.PY V3.0 — INITIAL SETUP")
    print("=" * 60)
    
    git_dir = os.path.join(ROOT_DIR, ".git")
    
    # Step 1: Configure credential manager
    configure_credential_manager()
    
    # Step 2: Set identity
    print("\n   👤 Setting Git identity...")
    run(["git", "config", "--global", "user.name", GIT_USERNAME])
    run(["git", "config", "--global", "user.email", GIT_EMAIL])
    print_status(f"Identity: {GIT_USERNAME} <{GIT_EMAIL}>")
    
    # Step 3: Init repo if needed
    if not os.path.exists(git_dir):
        print("\n   📁 Initializing Git repository...")
        run(["git", "init"], cwd=ROOT_DIR)
        run(["git", "branch", "-M", BRANCH], cwd=ROOT_DIR)
        print_status(f"Repository initialized with branch: {BRANCH}")
    else:
        print_status("Repository already exists")
    
    # Step 4: Setup remote
    print("\n   🌐 Configuring remote...")
    success, remotes = run(["git", "remote", "-v"], cwd=ROOT_DIR)
    if "origin" in remotes:
        run(["git", "remote", "set-url", "origin", REMOTE_URL], cwd=ROOT_DIR)
        print_status(f"Remote updated: {REMOTE_URL}")
    else:
        run(["git", "remote", "add", "origin", REMOTE_URL], cwd=ROOT_DIR)
        print_status(f"Remote added: {REMOTE_URL}")
    
    # Step 5: Create .gitignore
    gitignore_path = os.path.join(ROOT_DIR, ".gitignore")
    if not os.path.exists(gitignore_path):
        print("\n   📄 Creating .gitignore...")
        gitignore_content = """.venv/
__pycache__/
*.pyc
*.pyo
.env
*.log
.DS_Store
Thumbs.db
*.db
context_backups/
"""
        with open(gitignore_path, "w", encoding="utf-8") as f:
            f.write(gitignore_content)
        print_status(".gitignore created")
    
    print("\n" + "=" * 60)
    print("   ✅ SETUP COMPLETE")
    print("=" * 60)
    return True


def sync(message=None):
    """Sync changes to GitHub"""
    print("\n" + "=" * 60)
    print("   🔄 SETUP_GIT.PY V3.0 — SYNC")
    print("=" * 60)
    
    # Auto-generate commit message if not provided
    if not message:
        message = f"Auto-sync: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
    
    # Step 1: Check if .git exists
    git_dir = os.path.join(ROOT_DIR, ".git")
    if not os.path.exists(git_dir):
        print("   ⚠️ Git not initialized. Running setup() first...")
        setup()
    
    # Step 2: Add all changes
    print("\n   📦 Staging changes...")
    success, output = run(["git", "add", "."], cwd=ROOT_DIR)
    print_status("Changes staged" if success else f"Stage failed: {output}", success)
    
    # Step 3: Check if there are changes to commit
    success, status = run(["git", "status", "--porcelain"], cwd=ROOT_DIR)
    if not status.strip():
        print_status("No changes to commit")
        print("\n" + "=" * 60)
        print("   ✅ SYNC COMPLETE — No changes")
        print("=" * 60)
        return True
    
    # Step 4: Commit
    print("\n   💾 Committing...")
    success, output = run(["git", "commit", "-m", message], cwd=ROOT_DIR)
    if success:
        print_status(f"Committed: {message[:50]}...")
    else:
        if "nothing to commit" in output:
            print_status("Nothing to commit")
        else:
            print_status(f"Commit issue: {output[:100]}", False)
    
    # Step 5: Push
    print("\n   🚀 Pushing to GitHub...")
    print("      (اگر مرورگر باز شد، لاگین کنید)")
    
    success, output = run(["git", "push", "-u", "origin", BRANCH], cwd=ROOT_DIR)
    
    if success:
        print_status("Push successful!")
        print("\n" + "=" * 60)
        print("   ✅ SYNC COMPLETE")
        print(f"      Repo: https://github.com/{GIT_USERNAME}/{REPO_NAME}")
        print("=" * 60)
        return True
    else:
        if "rejected" in output:
            print_status("Push rejected — trying pull first...", False)
            run(["git", "pull", "--rebase", "origin", BRANCH], cwd=ROOT_DIR)
            success, output = run(["git", "push", "-u", "origin", BRANCH], cwd=ROOT_DIR)
            if success:
                print_status("Push after pull: Success")
                return True
            else:
                print_status("Push after pull: Failed", False)
                return False
        elif "Authentication" in output or "403" in output or "fatal" in output.lower():
            print_status("Authentication needed", False)
            print("\n" + "-" * 60)
            print("   🔐 AUTHENTICATION REQUIRED")
            print("-" * 60)
            print("\n   مرورگر باید باز شود برای لاگین GitHub.")
            print("   اگر باز نشد:")
            print("   1. https://github.com/settings/tokens")
            print("   2. Personal Access Token بسازید")
            print(f"   3. git push -u origin {BRANCH}")
            print("-" * 60)
            return False
        else:
            print_status(f"Push failed: {output[:100]}", False)
            return False


# === MAIN ===
if __name__ == "__main__":
    print("\n" + "=" * 60)
    print("🐙 SETUP_GIT V3.0 — Standalone Mode")
    print("=" * 60)
    
    if len(sys.argv) > 1:
        if sys.argv[1] == "setup":
            setup()
        elif sys.argv[1] == "sync":
            msg = sys.argv[2] if len(sys.argv) > 2 else None
            sync(msg)
        else:
            print("Usage: python setup_git.py [setup|sync] [message]")
    else:
        if not os.path.exists(os.path.join(ROOT_DIR, ".git")):
            setup()
        sync("Manual sync from standalone")
    
    print("\n✅ Done!")
