# AI_Tools/build.py — Build V5.7 (Real Data / Mock Alert)
# ═══════════════════════════════════════════════════════════════

import os
import sys
import subprocess
import socket
from datetime import datetime

import context_gen
import setup_git

# ═══════════════════════════════════════════════════════════════
# CONFIG
# ═══════════════════════════════════════════════════════════════
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(SCRIPT_DIR)
VENV_PATH = os.path.join(ROOT, ".venv")
if sys.platform == "win32":
    VENV_PYTHON = os.path.join(VENV_PATH, "Scripts", "python.exe")
else:
    VENV_PYTHON = os.path.join(VENV_PATH, "bin", "python")

# ═══════════════════════════════════════════════════════════════
# NEW FILES CONTENT
# ═══════════════════════════════════════════════════════════════

# 1. TECHNICAL ANALYSIS MODULE (Simplified for V5.7)
TECHNICAL_PY = '''# modules/analysis/technical.py
import math

def calculate_rsi(prices, period=14):
    """Simple RSI Calculation"""
    if len(prices) < period + 1:
        return 50  # Not enough data
    
    gains = []
    losses = []
    
    for i in range(1, len(prices)):
        delta = prices[i] - prices[i-1]
        if delta > 0:
            gains.append(delta)
            losses.append(0)
        else:
            gains.append(0)
            losses.append(abs(delta))
            
    # Simple Average (SMMA approximation for initial test)
    avg_gain = sum(gains[-period:]) / period
    avg_loss = sum(losses[-period:]) / period
    
    if avg_loss == 0:
        return 100
        
    rs = avg_gain / avg_loss
    rsi = 100 - (100 / (1 + rs))
    return round(rsi, 2)

def analyze_market(symbol, candles):
    """Analyzes candles and returns a signal"""
    if not candles:
        return {"signal": "NEUTRAL", "reason": "No Data"}
        
    closes = [c['close'] for c in candles]
    current_price = closes[-1]
    rsi = calculate_rsi(closes)
    
    signal = "NEUTRAL"
    reason = f"RSI is {rsi}"
    
    if rsi < 30:
        signal = "BUY 🟢"
        reason = f"Oversold (RSI {rsi})"
    elif rsi > 70:
        signal = "SELL 🔴"
        reason = f"Overbought (RSI {rsi})"
        
    return {
        "symbol": symbol,
        "price": current_price,
        "rsi": rsi,
        "signal": signal,
        "reason": reason
    }
'''

# 2. UPDATED MAIN.PY (Real Data Fetcher)
MAIN_PY = '''#!/usr/bin/env python3
"""OCEAN HUNTER V5.7 — Real Data / Mock Alert"""

import os
import sys
import time
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from dotenv import load_dotenv
from modules.data.collector import get_collector
from modules.analysis.technical import analyze_market

# Volatile Coins to Watch
TARGET_COINS = ["BTCIRT", "ETHIRT", "DOGEIRT", "SHIBIRT", "PEPEIRT"]

def main():
    load_dotenv()
    print("\\n" + "=" * 60)
    print("🌊 OCEAN HUNTER V5.7 — Market Scanner (No VPN Mode)")
    print("=" * 60)
    
    print("\\n[1] 🔌 Connecting to Nobitex (Direct)...")
    collector = get_collector()
    
    # Update symbol list
    collector.symbols = TARGET_COINS
    
    print(f"      Watching: {', '.join(TARGET_COINS)}")
    print("\\n[2] 📊 Fetching & Analyzing Data...")
    print(f"      {'SYMBOL':<10} | {'PRICE (IRT)':<15} | {'RSI':<6} | {'SIGNAL'}")
    print("      " + "-" * 50)
    
    results = collector.collect_all()
    
    for symbol in TARGET_COINS:
        # Get candles from storage or memory
        candles = collector.fetch_ohlcv(symbol, resolution="60") # 1 Hour candles
        
        if candles:
            # ANALYZE
            analysis = analyze_market(symbol, candles)
            
            # OUTPUT (Mock Alert)
            print(f"      {symbol:<10} | {analysis['price']:<15,} | {analysis['rsi']:<6} | {analysis['signal']}")
            
            # Simulation of Telegram Alert
            if "BUY" in analysis['signal'] or "SELL" in analysis['signal']:
                print(f"      Op >> 🔔 [MOCK TELEGRAM] Sending Alert: {analysis['reason']}")
        else:
            print(f"      {symbol:<10} | {'ERROR':<15} | {'---':<6} | ❌ No Data")
            
    print("\\n" + "=" * 60)
    print("✅ SCAN COMPLETE")
    print("👉 Note: Telegram was skipped (Mock Mode) until VPN is ready.")
    print("=" * 60 + "\\n")

if __name__ == "__main__":
    main()
'''

FILES_TO_CREATE = {
    "modules/analysis/technical.py": TECHNICAL_PY,
    "main.py": MAIN_PY
}

# ═══════════════════════════════════════════════════════════════
# BUILD STEPS
# ═══════════════════════════════════════════════════════════════
def step1_create_files():
    print("\n[1/4] 📝 Updating Logic Files...")
    for path, content in FILES_TO_CREATE.items():
        full_path = os.path.join(ROOT, path)
        dir_name = os.path.dirname(full_path)
        if not os.path.exists(dir_name):
            os.makedirs(dir_name)
        
        with open(full_path, "w", encoding="utf-8") as f:
            f.write(content)
        print(f"      ✅ Updated: {path}")

def step2_git():
    print("\n[2/4] 🐙 Git Sync...")
    try:
        setup_git.setup()
        setup_git.sync("Build V5.7: Real Data Scanner")
        print("      ✅ Saved to History")
    except:
        print("      ⚠️ Git skipped")

def step3_context():
    print("\n[3/4] 📋 Context Update...")
    context_gen.create_context_file()
    print("      ✅ Context Updated")

def step4_launch():
    print("\n[4/4] 🚀 Launching Scanner...")
    subprocess.run([VENV_PYTHON, "main.py"], cwd=ROOT)

def main():
    print("\n🚀 STARTING BUILD V5.7...")
    step1_create_files()
    step2_git()
    step3_context()
    step4_launch()

if __name__ == "__main__":
    main()
