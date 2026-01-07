# AI_Tools/build.py — Phase 23: Final Path Fix & Robust Test Execution
# ═══════════════════════════════════════════════════════════════
# Ref: PHASE-23-ROBUST-RUNNER
# ═══════════════════════════════════════════════════════════════

import os
import sys
import subprocess
import json
import time

# ═══════════════════════════════════════════════════════════════
# 1. SETUP PATHS (با درک صحیح از ساختار پروژه)
# ═══════════════════════════════════════════════════════════════
AI_TOOLS_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(AI_TOOLS_DIR) # مسیر ریشه پروژه F:\OCEANHUNTER است
sys.path.append(AI_TOOLS_DIR)

try:
    import context_gen
    import setup_git
except ImportError:
    pass

VENV_PYTHON = os.path.join(PROJECT_ROOT, ".venv", "Scripts", "python.exe")

# ═══════════════════════════════════════════════════════════════
# 2. DEFINE THE *ULTIMATE* ROBUST TEST RUNNER
# ═══════════════════════════════════════════════════════════════
# این نسخه از run_tests.py به طور قطعی مشکل مسیر را حل می‌کند.
# با استفاده از __file__، مسیرها را نسبت به مکان خودش محاسبه می‌کند.

ROBUST_TEST_RUNNER_CONTENT = r'''
import os
import json
import sys
import time
import pandas as pd
from datetime import datetime

# ===================================================================
# --- ULTIMATE PATH FIX ---
# این بخش به صورت داینامیک و دقیق مسیرها را محاسبه می‌کند و به محل
# اجرای اسکریپت (os.getcwd()) وابسته نیست.
# ===================================================================
SCRIPT_FILE_PATH = os.path.abspath(__file__)
# مسیر پوشه tests: F:\OCEANHUNTER\tests
TESTS_DIR = os.path.dirname(SCRIPT_FILE_PATH)
# مسیر ریشه پروژه: F:\OCEANHUNTER
PROJECT_ROOT = os.path.dirname(TESTS_DIR)

# افزودن مسیر ریشه به sys.path برای پیدا کردن ماژول‌های پروژه
if PROJECT_ROOT not in sys.path:
    sys.path.append(PROJECT_ROOT)

print(f"✅ Project Root Detected: {PROJECT_ROOT}")

# ===================================================================
# 1. SIMULATION COMPONENTS (بدون تغییر)
# ===================================================================

class SimulatedWallet:
    def __init__(self, initial_balance_data):
        self.balances = initial_balance_data.copy()
        print(f"  -> 🏦 Wallet initialized with: {self.balances}")

    def get_balance(self, asset):
        return self.balances.get(asset, 0.0)

    def execute_buy(self, symbol, amount, price):
        base, quote = symbol.split('/')
        cost = amount * price
        if self.get_balance(quote) >= cost:
            self.balances[quote] -= cost
            self.balances[base] = self.get_balance(base) + amount
            return True
        return False

    def execute_sell(self, symbol, amount, price):
        base, quote = symbol.split('/')
        if self.get_balance(base) >= amount:
            revenue = amount * price
            self.balances[base] -= amount
            self.balances[quote] = self.get_balance(quote) + revenue
            return True
        return False

class SimpleSmartSniperStrategy:
    def __init__(self, entry_threshold=70):
        self.entry_threshold = entry_threshold

    def analyze(self, candles_df):
        signals = []
        if 'rsi' not in candles_df.columns:
            print("   ⚠️  'rsi' column not found in data. Cannot generate signals.")
            return signals
            
        low_rsi_candles = candles_df[candles_df['rsi'] < 30]
        for index, row in low_rsi_candles.iterrows():
            signals.append({'action': 'BUY', 'price': row['close'], 'reason': f'RSI {row["rsi"]:.2f}'})
        return signals

# ===================================================================
# 2. TEST RUNNER (با مسیرهای اصلاح شده)
# ===================================================================

class TestRunner:
    def __init__(self):
        # استفاده از مسیرهای دقیق و محاسبه‌شده بر اساس PROJECT_ROOT
        self.scenarios_dir = os.path.join(PROJECT_ROOT, "data", "scenarios")
        self.data_dir = os.path.join(PROJECT_ROOT, "data")
        self.reports_dir = os.path.join(PROJECT_ROOT, "tests", "outputs")
        self.results = []
        
        print(f"  -> 📂 Scenarios Directory: {self.scenarios_dir}")
        print(f"  -> 📊 Reports Directory: {self.reports_dir}")

        if not os.path.exists(self.reports_dir):
            os.makedirs(self.reports_dir)
            print(f"  -> ✅ Created reports directory.")

    def load_scenarios(self):
        if not os.path.exists(self.scenarios_dir):
            print(f"❌ FATAL: Scenarios directory not found!")
            print(f"   Please ensure this path exists: {self.scenarios_dir}")
            return None
        
        files = [f for f in os.listdir(self.scenarios_dir) if f.endswith('.json')]
        scenarios = []
        for f in files:
            with open(os.path.join(self.scenarios_dir, f), 'r') as file:
                scenarios.append(json.load(file))
        return sorted(scenarios, key=lambda x: x['scenario_id'])

    def run_scenario(self, scenario):
        sc_id = scenario['scenario_id']
        print(f"\n🔄 Running {sc_id}: {scenario['name']}...")
        
        # --- بارگذاری داده‌های سناریو ---
        wallet_file_path = os.path.join(self.data_dir, "wallets", scenario['initial_wallet'])
        with open(wallet_file_path, 'r') as f:
            initial_wallet_data = json.load(f)
            
        wallet = SimulatedWallet(initial_wallet_data)
        strategy = SimpleSmartSniperStrategy()
        
        candle_file = scenario['candle_files'][0] # For simplicity, using the first candle file
        candle_path = os.path.join(self.data_dir, "candles", candle_file)
        if not os.path.exists(candle_path):
            print(f"   ❌ FAILED: Candle file not found at {candle_path}")
            self.results.append({"scenario_id": sc_id, "status": "FAIL", "reason": "Data file missing"})
            return
            
        candles_df = pd.read_csv(candle_path)
        signals = strategy.analyze(candles_df)
        
        trades = 0
        if signals:
            buy_signal = signals[0]
            amount_to_buy = 1 # مقدار خرید برای سادگی تست
            if wallet.execute_buy('SOL/USDT', amount_to_buy, buy_signal['price']):
                trades += 1
                print(f"  -> 🤖 Executed BUY: {amount_to_buy} SOL @ {buy_signal['price']} USDT (Reason: {buy_signal['reason']})")
        
        # --- ارزیابی نتایج ---
        # در این نسخه ساده، فقط وجود معامله را بررسی می‌کنیم
        status = "PASS" if trades > 0 else "NO_TRADES"
        
        result = {
            "scenario_id": sc_id, "status": status,
            "trades_executed": trades, "final_balance": wallet.balances
        }
        self.results.append(result)
        
        icon = "✅" if status == "PASS" else "⚠️"
        print(f"   {icon} Result: {status}")

    def generate_report(self):
        total = len(self.results)
        passed = sum(1 for r in self.results if r['status'] == "PASS")
        
        report = {
            "run_timestamp": datetime.now().isoformat(),
            "summary": {"total_scenarios": total, "passed": passed},
            "details": self.results
        }
        
        report_path = os.path.join(self.reports_dir, f"TEST_REPORT_{int(time.time())}.json")
        with open(report_path, 'w') as f:
            json.dump(report, f, indent=4)
            
        print("\n" + "="*50)
        print("📊 SIMULATION COMPLETE")
        print(f"   Total Scenarios: {total} | Passed: {passed}")
        print(f"   📄 Report saved to: {os.path.relpath(report_path, PROJECT_ROOT)}")
        print("="*50)

if __name__ == "__main__":
    runner = TestRunner()
    scenarios = runner.load_scenarios()
    
    if scenarios is None:
        sys.exit(1)
        
    if not scenarios:
        print("\n⚠️ No scenarios found in 'data/scenarios'.")
        print("   Did you run 'setup_test_data.py' first?")
    else:
        print(f"\n🚀 Starting Test Suite ({len(scenarios)} Scenarios)...")
        print("-" * 50)
        for sc in scenarios:
            runner.run_scenario(sc)
        runner.generate_report()

'''

# ═══════════════════════════════════════════════════════════════
# 3. BUILD STEPS
# ═══════════════════════════════════════════════════════════════

def main():
    print("\n[1/3] 🩹 Applying Robust Path Fix to Test Runner...")
    
    # مسیر صحیح فایل run_tests.py در ریشه پروژه
    runner_path = os.path.join(PROJECT_ROOT, "tests", "run_tests.py")
    
    try:
        with open(runner_path, "w", encoding="utf-8") as f:
            f.write(ROBUST_TEST_RUNNER_CONTENT)
        print(f"      ✅ 'tests/run_tests.py' updated successfully.")
    except Exception as e:
        print(f"      ❌ FAILED to write to {runner_path}: {e}")
        return

    print(f"\n[2/3] 🚀 Executing Test Suite with corrected paths...")
    print(f"      👉 Running: {os.path.relpath(VENV_PYTHON, PROJECT_ROOT)} {os.path.relpath(runner_path, PROJECT_ROOT)}")
    
    # اجرای تست و گرفتن خروجی
    result = subprocess.run(
        [VENV_PYTHON, runner_path],
        capture_output=True, text=True, encoding='utf-8',
        cwd=PROJECT_ROOT # اجرای اسکریپت از ریشه پروژه برای اطمینان
    )
    
    print("-" * 20 + " Test Runner Output " + "-" * 20)
    print(result.stdout)
    if result.stderr:
        print("-" * 20 + " Test Runner Errors " + "-" * 20)
        print(result.stderr)
    print("-" * 62)
    
    if result.returncode == 0:
        print("      ✅ Test suite completed. A new report should be in 'tests/outputs'.")
    else:
        print("      ❌ Test suite FAILED. Review the errors above.")

    print(f"\n[3/3] 📚 Git Sync...")
    if 'context_gen' in sys.modules: context_gen.create_context_file()
    if 'setup_git' in sys.modules: setup_git.sync("Phase 23: Implement Robust Test Runner")
    
    print("\n✅ Build complete. The system should now be stable.")

if __name__ == "__main__":
    main()
