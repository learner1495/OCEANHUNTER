
import os
import json
import sys
import time
import pandas as pd
from datetime import datetime

# افزودن مسیر روت پروژه برای دسترسی به ماژول‌ها
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# ===================================================================
# 1. SIMULATION COMPONENTS
# ===================================================================

class SimulatedWallet:
    """یک کیف پول مجازی برای ردیابی دارایی‌ها در طول تست."""
    def __init__(self, initial_balance):
        self.balances = initial_balance.copy()
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
    """نسخه بسیار ساده شده استراتژی برای تست."""
    def __init__(self, entry_threshold=70):
        self.entry_threshold = entry_threshold
        # در نسخه کامل، اندیکاتورها اینجا محاسبه می‌شوند
        
    def analyze(self, candles_df):
        """تحلیل داده‌های کندل و تولید سیگنال."""
        signals = []
        for index, row in candles_df.iterrows():
            score = 0
            # منطق ساده: اگر RSI زیر 30 باشد، امتیاز خرید بده
            if 'rsi' in row and row['rsi'] < 30:
                score += 80 # امتیاز بالا برای تحریک خرید
            
            if score >= self.entry_threshold:
                signals.append({'action': 'BUY', 'price': row['close'], 'reason': f'RSI {row["rsi"]:.2f}'})
            
            # منطق ساده خروج: سود 2%
            # (در تست واقعی، این بخش با وضعیت پوزیشن در ارتباط خواهد بود)
        return signals


# ===================================================================
# 2. TEST RUNNER
# ===================================================================

class TestRunner:
    def __init__(self):
        self.scenarios_dir = os.path.join(os.getcwd(), "data", "scenarios")
        self.data_dir = os.path.join(os.getcwd(), "data")
        self.reports_dir = os.path.join(os.getcwd(), "tests", "outputs")
        self.results = []
        
        if not os.path.exists(self.reports_dir):
            os.makedirs(self.reports_dir)

    def load_scenarios(self):
        files = [f for f in os.listdir(self.scenarios_dir) if f.endswith('.json')]
        scenarios = []
        for f in files:
            with open(os.path.join(self.scenarios_dir, f), 'r') as file:
                scenarios.append(json.load(file))
        return sorted(scenarios, key=lambda x: x['scenario_id'])

    def run_scenario(self, scenario):
        sc_id = scenario['scenario_id']
        print(f"🔄 Running {sc_id}: {scenario['name']}...")
        
        wallet = SimulatedWallet(scenario['initial_wallet'])
        strategy = SimpleSmartSniperStrategy()
        
        # بارگذاری دیتای کندل
        candle_file = scenario['candle_files'][0]
        candle_path = os.path.join(self.data_dir, candle_file)
        if not os.path.exists(candle_path):
            print(f"   ❌ FAILED: Candle file not found at {candle_path}")
            self.results.append({"scenario_id": sc_id, "status": "FAIL", "reason": "Data file missing"})
            return
            
        candles_df = pd.read_csv(candle_path)
        
        # اجرای استراتژی (فعلا یک پاس ساده)
        signals = strategy.analyze(candles_df)
        
        # اجرای اولین سیگنال خرید (برای تست)
        if signals:
            buy_signal = signals[0]
            amount_to_buy = 1  # 1 SOL for simplicity
            wallet.execute_buy('SOL/USDT', amount_to_buy, buy_signal['price'])
            print(f"  -> 🤖 Executed BUY: {amount_to_buy} SOL @ {buy_signal['price']} USDT")
        
        # بررسی Assertions
        passed_count = 0
        total_assertions = len(scenario.get('assertions', []))
        
        for assertion in scenario.get('assertions', []):
            actual_value = wallet.get_balance(assertion['asset'])
            expected_value = assertion['expected_value']
            
            # مقایسه با یک تلورانس کوچک برای اعداد اعشاری
            if abs(actual_value - expected_value) < 0.01:
                passed_count += 1
            else:
                print(f"   -> Assertion FAIL for {assertion['asset']}: Expected ~{expected_value}, Got {actual_value:.2f}")

        status = "PASS" if passed_count == total_assertions else "FAIL"
        
        result = {
            "scenario_id": sc_id,
            "status": status,
            "assertions_total": total_assertions,
            "assertions_passed": passed_count
        }
        self.results.append(result)
        
        icon = "✅" if status == "PASS" else "❌"
        print(f"   {icon} {status} | Assertions: {passed_count}/{total_assertions}")

    def generate_report(self):
        # (کد این بخش بدون تغییر باقی می‌ماند)
        total = len(self.results)
        passed = sum(1 for r in self.results if r['status'] == "PASS")
        failed = total - passed
        
        report = {
            "timestamp": datetime.now().isoformat(),
            "total_scenarios": total,
            "passed": passed,
            "failed": failed,
            "details": self.results
        }
        
        report_path = os.path.join(self.reports_dir, f"SIM_REPORT_{int(time.time())}.json")
        with open(report_path, 'w') as f:
            json.dump(report, f, indent=4)
            
        print("\n" + "="*40)
        print(f"📊 REAL SIMULATION SUMMARY")
        print(f"   Total: {total}")
        print(f"   Passed: {passed}")
        print(f"   Failed: {failed}")
        print(f"   📄 Report saved to: {report_path}")
        print("="*40)

if __name__ == "__main__":
    runner = TestRunner()
    scenarios = runner.load_scenarios()
    
    if not scenarios:
        print("⚠️ No scenarios found. Run 'setup_test_data.py' first.")
    else:
        print(f"🚀 Starting Real Simulation Test Suite ({len(scenarios)} Scenarios)...")
        print("-" * 40)
        for sc in scenarios:
            runner.run_scenario(sc)
        runner.generate_report()
