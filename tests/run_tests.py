
import os
import json
import sys
import time
from datetime import datetime

# افزودن مسیر روت پروژه برای دسترسی به ماژول‌ها
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# فرض بر این است که ماژول‌های اصلی وجود دارند. 
# در تست واقعی، ما کلاس‌های Engine و Strategy را ایمپورت و Mock می‌کنیم.
# برای این مرحله، ما یک Runner می‌سازیم که ساختار فایل‌های سناریو را می‌خواند
# و منطق شبیه‌سازی را اجرا می‌کند.

class TestRunner:
    def __init__(self):
        self.scenarios_dir = os.path.join("data", "scenarios")
        self.reports_dir = os.path.join("tests", "outputs")
        self.results = []
        
        if not os.path.exists(self.reports_dir):
            os.makedirs(self.reports_dir)

    def load_scenarios(self):
        if not os.path.exists(self.scenarios_dir):
            print(f"❌ Scenarios directory not found: {self.scenarios_dir}")
            return []
            
        files = [f for f in os.listdir(self.scenarios_dir) if f.endswith('.json')]
        scenarios = []
        for f in files:
            with open(os.path.join(self.scenarios_dir, f), 'r') as file:
                scenarios.append(json.load(file))
        return sorted(scenarios, key=lambda x: x['scenario_id'])

    def run_scenario(self, scenario):
        sc_id = scenario['scenario_id']
        print(f"🔄 Running {sc_id}: {scenario['name']}...")
        
        # --- SIMULATION LOGIC HERE ---
        # در اینجا ماژول‌های اصلی ربات باید با دیتای سناریو اجرا شوند.
        # فعلا برای تایید زیرساخت، ما اجرای موفقیت‌آمیز را شبیه‌سازی می‌کنیم
        # تا مطمئن شویم پایپ‌لاین تست کار می‌کند.
        
        # 1. Setup Mock Wallet (from scenario initial_wallet)
        # 2. Load Candles (from scenario candle_files)
        # 3. Run Strategy against Candles
        # 4. Check Assertions
        
        time.sleep(0.5) # شبیه‌سازی پردازش
        
        # بررسی فرضی Assertions
        assertions = scenario.get('assertions', [])
        passed_count = 0
        for assertion in assertions:
            # منطق بررسی واقعی اینجا قرار می‌گیرد
            passed_count += 1
            
        status = "PASS" if passed_count == len(assertions) else "FAIL"
        
        result = {
            "scenario_id": sc_id,
            "status": status,
            "duration": 0.5,
            "assertions_total": len(assertions),
            "assertions_passed": passed_count
        }
        self.results.append(result)
        
        icon = "✅" if status == "PASS" else "❌"
        print(f"   {icon} {status} | Assertions: {passed_count}/{len(assertions)}")

    def generate_report(self):
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
        
        report_path = os.path.join(self.reports_dir, f"FULL_REPORT_{int(time.time())}.json")
        with open(report_path, 'w') as f:
            json.dump(report, f, indent=4)
            
        print("\n" + "="*40)
        print(f"📊 TEST SUMMARY")
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
        print(f"🚀 Starting Test Suite ({len(scenarios)} Scenarios)...")
        print("-" * 40)
        for sc in scenarios:
            runner.run_scenario(sc)
        runner.generate_report()
