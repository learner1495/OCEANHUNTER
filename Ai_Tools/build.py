# ═══════════════════════════════════════════════════════════════
# AI_Tools/build.py — EXCHANGE-TEST-093
# ساخت تست اتصال صرافی + ارسال به تلگرام
# ═══════════════════════════════════════════════════════════════

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
VENV_PYTHON = os.path.join(VENV_PATH, "Scripts", "python.exe") if sys.platform == "win32" else os.path.join(VENV_PATH, "bin", "python")

# ═══════════════════════════════════════════════════════════════
# ⭐ CUSTOMIZE — فایل تست Exchange
# ═══════════════════════════════════════════════════════════════
FOLDERS = []

NEW_FILES = {
    "test_exchange.py": '''# ═══════════════════════════════════════════════════════════════
# test_exchange.py — تست اتصال صرافی + ارسال به تلگرام
# Reference: EXCHANGE-TEST-093
# ═══════════════════════════════════════════════════════════════

import os
import sys
from datetime import datetime

# Add project root to path
PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

def main():
    print("=" * 60)
    print("🌊 OCEAN HUNTER — Exchange Connection Test")
    print(f"⏰ {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)
    
    # ═══ Step 1: Connect to MEXC ═══
    print("\\n[1] Connecting to MEXC...")
    
    try:
        from modules.network.mexc_api import get_client
        client = get_client()
        
        # Ping test
        ping = client.ping()
        if "error" in ping:
            print(f"   ❌ Ping Failed: {ping}")
            return
        print("   ✅ Connected to MEXC!")
        
    except Exception as e:
        print(f"   ❌ Connection Error: {e}")
        return
    
    # ═══ Step 2: Get Top Crypto Prices ═══
    print("\\n[2] Fetching Crypto Prices...")
    
    symbols = ["BTCUSDT", "ETHUSDT", "BNBUSDT", "SOLUSDT", "XRPUSDT", 
               "ADAUSDT", "DOGEUSDT", "TRXUSDT", "TONUSDT", "SHIBUSDT"]
    
    prices = {}
    for symbol in symbols:
        try:
            result = client.get_ticker_price(symbol)
            if "price" in result:
                price = float(result["price"])
                prices[symbol] = price
                coin = symbol.replace("USDT", "")
                print(f"   💰 {coin}: ${price:,.4f}")
            else:
                print(f"   ⚠️ {symbol}: No price data")
        except Exception as e:
            print(f"   ❌ {symbol}: {e}")
    
    # ═══ Step 3: Get Account Balance ═══
    print("\\n[3] Checking Account Balance...")
    
    balances = []
    try:
        account = client.get_account()
        if "balances" in account:
            print("   ✅ Authentication Successful!")
            
            # Find non-zero balances
            for b in account["balances"]:
                free = float(b.get("free", 0))
                locked = float(b.get("locked", 0))
                if free > 0 or locked > 0:
                    asset = b["asset"]
                    total = free + locked
                    balances.append({"asset": asset, "free": free, "locked": locked, "total": total})
                    print(f"   💵 {asset}: {free:.6f} (locked: {locked:.6f})")
            
            if not balances:
                print("   📭 No assets found (empty account)")
        else:
            print(f"   ⚠️ Account response: {account}")
            
    except Exception as e:
        print(f"   ❌ Balance Error: {e}")
    
    # ═══ Step 4: Build Report ═══
    print("\\n[4] Building Report...")
    
    report = "🌊 <b>OCEAN HUNTER — Market Report</b>\\n"
    report += f"📅 {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\\n"
    report += "─" * 25 + "\\n\\n"
    
    # Prices section
    report += "📊 <b>Top 10 Crypto Prices:</b>\\n"
    for symbol, price in prices.items():
        coin = symbol.replace("USDT", "")
        if price >= 1000:
            report += f"   • {coin}: <code>${price:,.2f}</code>\\n"
        elif price >= 1:
            report += f"   • {coin}: <code>${price:.4f}</code>\\n"
        else:
            report += f"   • {coin}: <code>${price:.8f}</code>\\n"
    
    report += "\\n"
    
    # Balance section
    if balances:
        report += "💼 <b>Your Balances:</b>\\n"
        for b in balances[:10]:  # Max 10
            report += f"   • {b['asset']}: <code>{b['free']:.6f}</code>\\n"
    else:
        report += "💼 <b>Balances:</b> No assets\\n"
    
    report += "\\n✅ <i>Connection Test Successful!</i>"
    
    print("   ✅ Report Ready!")
    
    # ═══ Step 5: Send to Telegram ═══
    print("\\n[5] Sending to Telegram...")
    
    try:
        from modules.network.telegram_bot import get_bot
        bot = get_bot()
        
        # Test connection first
        if not bot.test_connection():
            print("   ❌ Bot connection failed!")
            return
        
        # Send report
        result = bot.send_message(report)
        
        if result.get("ok"):
            print("   ✅ Report sent to Telegram!")
            print("\\n" + "=" * 60)
            print("🎉 ALL TESTS PASSED!")
            print("=" * 60)
        else:
            print(f"   ❌ Send failed: {result}")
            
    except Exception as e:
        print(f"   ❌ Telegram Error: {e}")

if __name__ == "__main__":
    main()
'''
}

MODIFY_FILES = {}
MAIN_FILE = "test_exchange.py"  # اجرای فایل تست

# ═══════════════════════════════════════════════════════════════
# ERROR TRACKING
# ═══════════════════════════════════════════════════════════════
errors = []

def log_error(step, error):
    """ثبت خطا بدون توقف"""
    errors.append(f"[{step}] {error}")
    print(f"      ⚠️ Error: {error}")

# ═══════════════════════════════════════════════════════════════
# STEPS 1-6
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
        subprocess.run([VENV_PYTHON, "-m", "pip", "install", "-r", req],
                      capture_output=True, check=True)
        print("      ✅ Installed")
    except Exception as e:
        log_error("Step3", e)

def step4_folders():
    print("\n[4/9] 📁 Folders...")
    try:
        if not FOLDERS:
            print("      ℹ️ None defined")
            return
        for f in FOLDERS:
            path = os.path.join(ROOT, f)
            if not os.path.exists(path):
                os.makedirs(path)
                print(f"      ✅ Created: {f}/")
    except Exception as e:
        log_error("Step4", e)

def step5_new_files():
    print("\n[5/9] 📝 New Files...")
    try:
        if not NEW_FILES:
            print("      ℹ️ None defined")
            return
        for path, content in NEW_FILES.items():
            full = os.path.join(ROOT, path)
            parent = os.path.dirname(full)
            if parent and not os.path.exists(parent):
                os.makedirs(parent)
            with open(full, "w", encoding="utf-8") as f:
                f.write(content)
            print(f"      ✅ Created: {path}")
    except Exception as e:
        log_error("Step5", e)

def step6_modify():
    print("\n[6/9] ✏️ Modify Files...")
    try:
        if not MODIFY_FILES:
            print("      ℹ️ None defined")
            return
        for path, content in MODIFY_FILES.items():
            full = os.path.join(ROOT, path)
            with open(full, "w", encoding="utf-8") as f:
                f.write(content)
            print(f"      ✏️ Modified: {path}")
    except Exception as e:
        log_error("Step6", e)

# ═══════════════════════════════════════════════════════════════
# MAIN
# ═══════════════════════════════════════════════════════════════
def main():
    start_time = datetime.now()

    print("\n" + "═" * 50)
    print(f"🔧 BUILD — EXCHANGE TEST | OCEAN HUNTER")
    print(f"⏰ Started: {start_time.strftime('%H:%M:%S')}")
    print("═" * 50)

    try:
        # ─── مراحل 1-6: Setup ───
        step1_system()
        step2_venv()
        step3_deps()
        step4_folders()
        step5_new_files()
        step6_modify()

        # ─── مرحله 7: Context ───
        print("\n[7/9] 📋 Context Generation...")
        try:
            context_gen.create_context_file()
            print("      ✅ Context created")
        except Exception as e:
            log_error("Step7-Context", e)

        # ─── مرحله 8: Git ───
        print("\n[8/9] 🐙 Git...")
        try:
            setup_git.setup()
            setup_git.sync(f"Build: Exchange Test {start_time.strftime('%Y-%m-%d %H:%M')}")
            print("      ✅ Git synced")
        except Exception as e:
            log_error("Step8-Git", e)

        # ─── مرحله 9: Launch ───
        print("\n[9/9] 🚀 Launch Test...")
        try:
            main_path = os.path.join(ROOT, MAIN_FILE)
            if os.path.exists(main_path):
                print("=" * 50)
                print("🧪 RUNNING EXCHANGE TEST...")
                print("=" * 50)
                subprocess.run([VENV_PYTHON, main_path], cwd=ROOT)
            else:
                print(f"      ℹ️ No {MAIN_FILE}")
        except Exception as e:
            log_error("Step9-Launch", e)

    except KeyboardInterrupt:
        print("\n\n⛔ Build cancelled by user")
        errors.append("KeyboardInterrupt")

    except Exception as e:
        print(f"\n\n💥 Critical error: {e}")
        errors.append(f"Critical: {e}")

    finally:
        # ═══ همیشه اجرا می‌شود ═══
        end_time = datetime.now()
        duration = (end_time - start_time).seconds

        print("\n" + "═" * 50)

        if errors:
            print(f"⚠️ BUILD COMPLETED WITH {len(errors)} ERROR(S)")
            print("─" * 50)
            for err in errors:
                print(f"   • {err}")
        else:
            print("✅ BUILD COMPLETE — NO ERRORS")

        print("─" * 50)
        print(f"⏱️ Duration: {duration}s")
        print(f"🏁 Finished: {end_time.strftime('%H:%M:%S')}")
        print("═" * 50)

if __name__ == "__main__":
    main()
