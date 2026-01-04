#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
OCEAN HUNTER V10.8.2 - Test Data Generator
Auto-creates all test folders and data files
Run from project root: python setup_test_data.py
"""

import os
import json
from pathlib import Path

# ═══════════════════════════════════════════════════════════════
# SECTION 1: DIRECTORY STRUCTURE
# ═══════════════════════════════════════════════════════════════

BASE_DIR = Path(__file__).parent / "tests"

DIRECTORIES = [
    "data/candles",
    "data/orderbooks", 
    "data/scenarios",
    "data/wallets",
    "providers",
    "runners",
    "reporters",
    "outputs"
]

def create_directories():
    """Create all required test directories"""
    print("=" * 60)
    print("📁 Creating directory structure...")
    print("=" * 60)
    
    for dir_path in DIRECTORIES:
        full_path = BASE_DIR / dir_path
        full_path.mkdir(parents=True, exist_ok=True)
        print(f"  ✅ Created: {full_path}")
    
    # Create __init__.py files
    init_dirs = ["", "providers", "runners", "reporters"]
    for dir_name in init_dirs:
        init_file = BASE_DIR / dir_name / "__init__.py"
        init_file.touch(exist_ok=True)
        print(f"  ✅ Created: {init_file}")
    
    # Create .gitkeep in outputs
    gitkeep = BASE_DIR / "outputs" / ".gitkeep"
    gitkeep.touch(exist_ok=True)
    
    print("\n✅ Directory structure complete!\n")

# ═══════════════════════════════════════════════════════════════
# SECTION 2: WALLET DATA
# ═══════════════════════════════════════════════════════════════

INITIAL_WALLET = {
    "version": "V10.8.2",
    "created": "2026-01-04",
    "description": "Initial wallet state for testing",
    "balances": {
        "USDT": {"available": 400.0, "locked": 0.0},
        "SOL": {"available": 0.0, "locked": 0.0, "avg_price": 0.0},
        "BNB": {"available": 0.0, "locked": 0.0, "avg_price": 0.0},
        "XRP": {"available": 0.0, "locked": 0.0, "avg_price": 0.0},
        "AVAX": {"available": 0.0, "locked": 0.0, "avg_price": 0.0},
        "LINK": {"available": 0.0, "locked": 0.0, "avg_price": 0.0},
        "BTC": {"available": 0.005, "locked": 0.0, "avg_price": 42000.0},
        "PAXG": {"available": 0.08, "locked": 0.0, "avg_price": 2500.0}
    },
    "settings": {
        "fee_rate": 0.0035,
        "max_positions": 3,
        "position_size_usdt": 100.0
    }
}

def create_wallet():
    """Create initial wallet JSON file"""
    print("=" * 60)
    print("💰 Creating wallet file...")
    print("=" * 60)
    
    wallet_path = BASE_DIR / "data/wallets/initial_wallet_v10.8.2.json"
    with open(wallet_path, 'w', encoding='utf-8') as f:
        json.dump(INITIAL_WALLET, f, indent=2, ensure_ascii=False)
    
    print(f"  ✅ Created: {wallet_path}")
    print("\n✅ Wallet file complete!\n")

# ═══════════════════════════════════════════════════════════════
# SECTION 3: CANDLE DATA GENERATOR
# ═══════════════════════════════════════════════════════════════

def generate_candles(symbol, timeframe, base_price, scenarios):
    """
    Generate candle data with specific scenarios
    
    scenarios: list of tuples (candle_index, tag, price_modifier)
    """
    candles = []
    current_price = base_price
    base_timestamp = 1704067200  # 2024-01-01 00:00:00
    
    # Timeframe to seconds
    tf_seconds = 900 if timeframe == "M15" else 3600  # M15=900s, 1H=3600s
    
    for i in range(100):
        timestamp = base_timestamp + (i * tf_seconds)
        
        # Check if this candle has a special scenario
        tag = "NORMAL"
        price_mod = 1.0
        
        for sc_idx, sc_tag, sc_mod in scenarios:
            if i == sc_idx:
                tag = sc_tag
                price_mod = sc_mod
                break
        
        # Generate OHLCV
        current_price *= price_mod
        variance = current_price * 0.005  # 0.5% variance
        
        open_p = current_price
        high_p = current_price + variance
        low_p = current_price - variance
        close_p = current_price + (variance * 0.3)
        volume = 10000 + (i * 100)
        
        candles.append({
            "timestamp": timestamp,
            "open": round(open_p, 2),
            "high": round(high_p, 2),
            "low": round(low_p, 2),
            "close": round(close_p, 2),
            "volume": volume,
            "scenario_tag": tag
        })
        
        current_price = close_p
    
    return candles

def save_candles_csv(candles, filename):
    """Save candles to CSV file"""
    filepath = BASE_DIR / "data/candles" / filename
    
    with open(filepath, 'w', encoding='utf-8') as f:
        # Header
        f.write("timestamp,open,high,low,close,volume,scenario_tag\n")
        
        # Data
        for c in candles:
            f.write(f"{c['timestamp']},{c['open']},{c['high']},{c['low']},{c['close']},{c['volume']},{c['scenario_tag']}\n")
    
    print(f"  ✅ Created: {filepath}")
# ═══════════════════════════════════════════════════════════════
# SECTION 4: ALL CANDLE DEFINITIONS
# ═══════════════════════════════════════════════════════════════

CANDLE_CONFIGS = {
    # ─────────────────────────────────────────────────────────────
    # SOL - Solana
    # ─────────────────────────────────────────────────────────────
    "SOL_M15": {
        "symbol": "SOL", "timeframe": "M15", "base_price": 95.0,
        "scenarios": [
            (15, "ENTRY_SIGNAL", 1.02),
            (45, "EXIT_PROFIT", 1.025),
            (70, "ENTRY_SIGNAL", 0.98),
            (90, "EXIT_PROFIT", 1.03)
        ]
    },
    "SOL_M15_DCA": {
        "symbol": "SOL", "timeframe": "M15", "base_price": 100.0,
        "scenarios": [
            (10, "ENTRY_SIGNAL", 1.0),
            (18, "DCA_LAYER1_TRIGGER", 0.97),
            (25, "DCA_LAYER2_TRIGGER", 0.94),
            (32, "DCA_LAYER3_TRIGGER", 0.90),
            (50, "RECOVERY_START", 1.05),
            (70, "DCA_EXIT_PROFIT", 1.08)
        ]
    },
    "SOL_M15_TRAILING": {
        "symbol": "SOL", "timeframe": "M15", "base_price": 95.0,
        "scenarios": [
            (5, "ENTRY_SIGNAL", 1.02),
            (10, "TRAILING_ACTIVATED", 1.03),
            (12, "NEW_HIGH", 1.02),
            (14, "NEW_HIGH", 1.015),
            (16, "NEW_HIGH", 1.01),
            (20, "TRAILING_EXIT", 0.985)
        ]
    },
    "SOL_M15_GLOBAL_STOP": {
        "symbol": "SOL", "timeframe": "M15", "base_price": 100.0,
        "scenarios": [
            (3, "ENTRY_SIGNAL", 1.0),
            (8, "DECLINE_START", 0.96),
            (12, "GLOBAL_STOP_HIT", 0.88)
        ]
    },
    "SOL_1H": {
        "symbol": "SOL", "timeframe": "1H", "base_price": 95.0,
        "scenarios": [
            (10, "MULTI_TF_CONFIRM", 1.02),
            (30, "EXIT_SIGNAL", 1.03)
        ]
    },
    
    # ─────────────────────────────────────────────────────────────
    # BNB - Binance Coin
    # ─────────────────────────────────────────────────────────────
    "BNB_M15": {
        "symbol": "BNB", "timeframe": "M15", "base_price": 315.0,
        "scenarios": [
            (15, "ENTRY_SIGNAL", 1.02),
            (45, "EXIT_PROFIT", 1.025),
            (75, "ENTRY_SIGNAL", 0.98),
            (95, "EXIT_PROFIT", 1.03)
        ]
    },
    "BNB_M15_DCA": {
        "symbol": "BNB", "timeframe": "M15", "base_price": 320.0,
        "scenarios": [
            (8, "ENTRY_SIGNAL", 1.0),
            (15, "DCA_LAYER1_TRIGGER", 0.97),
            (22, "DCA_LAYER2_TRIGGER", 0.94),
            (30, "DCA_LAYER3_TRIGGER", 0.90),
            (45, "RECOVERY_START", 1.05),
            (65, "DCA_EXIT_PROFIT", 1.08)
        ]
    },
    "BNB_1H": {
        "symbol": "BNB", "timeframe": "1H", "base_price": 315.0,
        "scenarios": [
            (12, "MULTI_TF_CONFIRM", 1.02),
            (35, "EXIT_SIGNAL", 1.03)
        ]
    },
    
    # ─────────────────────────────────────────────────────────────
    # XRP - Ripple
    # ─────────────────────────────────────────────────────────────
    "XRP_M15": {
        "symbol": "XRP", "timeframe": "M15", "base_price": 0.62,
        "scenarios": [
            (12, "ENTRY_SIGNAL", 1.02),
            (40, "EXIT_PROFIT", 1.025),
            (68, "ENTRY_SIGNAL", 0.98),
            (88, "EXIT_PROFIT", 1.03)
        ]
    },
    "XRP_M15_DCA": {
        "symbol": "XRP", "timeframe": "M15", "base_price": 0.65,
        "scenarios": [
            (10, "ENTRY_SIGNAL", 1.0),
            (20, "DCA_LAYER1_TRIGGER", 0.97),
            (28, "DCA_LAYER2_TRIGGER", 0.94),
            (35, "DCA_LAYER3_TRIGGER", 0.90),
            (55, "RECOVERY_START", 1.05),
            (75, "DCA_EXIT_PROFIT", 1.08)
        ]
    },
    "XRP_1H": {
        "symbol": "XRP", "timeframe": "1H", "base_price": 0.62,
        "scenarios": [
            (15, "MULTI_TF_CONFIRM", 1.02),
            (40, "EXIT_SIGNAL", 1.03)
        ]
    },
    
    # ─────────────────────────────────────────────────────────────
    # AVAX - Avalanche
    # ─────────────────────────────────────────────────────────────
    "AVAX_M15": {
        "symbol": "AVAX", "timeframe": "M15", "base_price": 35.0,
        "scenarios": [
            (18, "ENTRY_SIGNAL", 1.02),
            (48, "EXIT_PROFIT", 1.025),
            (72, "ENTRY_SIGNAL", 0.98),
            (92, "EXIT_PROFIT", 1.03)
        ]
    },
    "AVAX_M15_DCA": {
        "symbol": "AVAX", "timeframe": "M15", "base_price": 36.0,
        "scenarios": [
            (12, "ENTRY_SIGNAL", 1.0),
            (22, "DCA_LAYER1_TRIGGER", 0.97),
            (30, "DCA_LAYER2_TRIGGER", 0.94),
            (38, "DCA_LAYER3_TRIGGER", 0.90),
            (52, "RECOVERY_START", 1.05),
            (72, "DCA_EXIT_PROFIT", 1.08)
        ]
    },
    "AVAX_1H": {
        "symbol": "AVAX", "timeframe": "1H", "base_price": 35.0,
        "scenarios": [
            (14, "MULTI_TF_CONFIRM", 1.02),
            (38, "EXIT_SIGNAL", 1.03)
        ]
    },
    
    # ─────────────────────────────────────────────────────────────
    # LINK - Chainlink
    # ─────────────────────────────────────────────────────────────
    "LINK_M15": {
        "symbol": "LINK", "timeframe": "M15", "base_price": 14.5,
        "scenarios": [
            (14, "ENTRY_SIGNAL", 1.02),
            (42, "EXIT_PROFIT", 1.025),
            (70, "ENTRY_SIGNAL", 0.98),
            (90, "EXIT_PROFIT", 1.03)
        ]
    },
    "LINK_M15_DCA": {
        "symbol": "LINK", "timeframe": "M15", "base_price": 15.0,
        "scenarios": [
            (10, "ENTRY_SIGNAL", 1.0),
            (20, "DCA_LAYER1_TRIGGER", 0.97),
            (28, "DCA_LAYER2_TRIGGER", 0.94),
            (36, "DCA_LAYER3_TRIGGER", 0.90),
            (54, "RECOVERY_START", 1.05),
            (74, "DCA_EXIT_PROFIT", 1.08)
        ]
    },
    "LINK_1H": {
        "symbol": "LINK", "timeframe": "1H", "base_price": 14.5,
        "scenarios": [
            (16, "MULTI_TF_CONFIRM", 1.02),
            (42, "EXIT_SIGNAL", 1.03)
        ]
    },

    # ─────────────────────────────────────────────────────────────
    # BTC & PAXG (Market Health Only)
    # ─────────────────────────────────────────────────────────────
    "BTC_1H": {
        "symbol": "BTC", "timeframe": "1H", "base_price": 42000.0,
        "scenarios": [
            (10, "HEALTH_STRONG", 1.02),
            (30, "HEALTH_NEUTRAL", 1.0),
            (55, "HEALTH_WEAK", 0.97),
            (75, "HEALTH_RECOVER", 1.03)
        ]
    },
    "PAXG_1H": {
        "symbol": "PAXG", "timeframe": "1H", "base_price": 2500.0,
        "scenarios": [
            (20, "SAFE_HAVEN_STABLE", 1.005),
            (50, "SAFE_HAVEN_INFLOW", 1.01)
        ]
    }
}

def create_all_candles():
    print("=" * 60)
    print("📊 Generating candle CSV files...")
    print("=" * 60)

    for name, cfg in CANDLE_CONFIGS.items():
        candles = generate_candles(
            cfg["symbol"],
            cfg["timeframe"],
            cfg["base_price"],
            cfg["scenarios"]
        )
        save_candles_csv(candles, f"{name}.csv")

    print("\n✅ All candle files created!\n")
# ═══════════════════════════════════════════════════════════════
# SECTION 5: ORDERBOOK DATA
# ═══════════════════════════════════════════════════════════════

def create_orderbooks():
    print("=" * 60)
    print("📘 Creating orderbook JSON files...")
    print("=" * 60)

    symbols = ["SOL", "BNB", "XRP", "AVAX", "LINK"]

    for sym in symbols:
        orderbook = {
            "symbol": sym,
            "bids": [[round(100 - i * 0.1, 2), 50 + i * 5] for i in range(10)],
            "asks": [[round(100 + i * 0.1, 2), 50 + i * 5] for i in range(10)],
            "spread": 0.1,
            "depth": "NORMAL",
            "timestamp": 1704067200
        }

        path = BASE_DIR / "data/orderbooks" / f"{sym}.json"
        with open(path, "w", encoding="utf-8") as f:
            json.dump(orderbook, f, indent=2)

        print(f"  ✅ Created: {path}")

    print("\n✅ Orderbooks created!\n")

# ═══════════════════════════════════════════════════════════════
# SECTION 6: SCENARIO FILES (SC-001 → SC-015)
# ═══════════════════════════════════════════════════════════════

def create_scenarios():
    print("=" * 60)
    print("🧪 Creating scenario JSON files...")
    print("=" * 60)

    for i in range(1, 16):
        sc_id = f"SC-{i:03d}"
        scenario = {
            "scenario_id": sc_id,
            "name": f"Auto Generated Scenario {i}",
            "description": "Generated for full test framework coverage",
            "duration_candles": 100,
            "initial_wallet": "initial_wallet_v10.8.2.json",
            "candle_files": {
                "SOL": "SOL_M15.csv",
                "BNB": "BNB_M15.csv",
                "BTC": "BTC_1H.csv"
            },
            "orderbook_files": {
                "SOL": "SOL.json"
            },
            "expected_results": {
                "total_trades": i % 3 + 1,
                "winning_trades": 1,
                "final_usdt_min": 380,
                "btc_vault_increased": True
            },
            "assertions": [
                {"type": "entry_triggered", "symbol": "SOL", "candle_index": 15},
                {"type": "exit_triggered", "symbol": "SOL", "min_profit_pct": 2}
            ]
        }

        path = BASE_DIR / "data/scenarios" / f"{sc_id}.json"
        with open(path, "w", encoding="utf-8") as f:
            json.dump(scenario, f, indent=2)

        print(f"  ✅ Created: {path}")

    print("\n✅ Scenario files created!\n")

# ═══════════════════════════════════════════════════════════════
# SECTION 7: MAIN EXECUTION
# ═══════════════════════════════════════════════════════════════

def main():
    create_directories()
    create_wallet()
    create_all_candles()
    create_orderbooks()
    create_scenarios()

    print("=" * 60)
    print("🎉 TEST DATA GENERATION COMPLETE")
    print("All Phase 2 test data is ready.")
    print("=" * 60)

if __name__ == "__main__":
    main()
