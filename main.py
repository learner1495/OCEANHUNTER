import os
import time
import requests
import urllib3
from dotenv import load_dotenv
from modules.m_data import DataEngine
from modules.m_analysis import analyze_market
from modules.m_trader import PaperTrader

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
load_dotenv()

# --- CONFIG ---
TG_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
TG_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")
PROXY_URL = "http://127.0.0.1:10809"
PROXIES = {"http": PROXY_URL, "https": PROXY_URL}

def send_telegram(msg):
    if not TG_TOKEN or not TG_CHAT_ID: return
    url = f"https://api.telegram.org/bot{TG_TOKEN}/sendMessage"
    payload = {"chat_id": TG_CHAT_ID, "text": msg}
    try:
        requests.post(url, json=payload, proxies=PROXIES, verify=False, timeout=5)
    except: pass

def main():
    print("-" * 50)
    print("📜 OCEAN HUNTER V8.0 — PAPER TRADING")
    print("-" * 50)
    
    engine = DataEngine()
    trader = PaperTrader(initial_balance=1000) # Start with $1000 Fake USDT
    
    targets = ["BTCUSDT", "ETHUSDT", "SOLUSDT", "BNBUSDT", "XRPUSDT"]
    current_prices = {}
    
    report_msg = "📜 PAPER TRADING REPORT (V8.0)\n"
    report_msg += "Strategy: RSI (14) | Fake Balance: $1000\n"
    report_msg += "─" * 25 + "\n\n"
    
    trade_logs = []

    for symbol in targets:
        # 1. Fetch Data
        candles = engine.fetch_candles(symbol, interval="60m", limit=50)
        
        if candles:
            # 2. Analyze
            result = analyze_market(symbol, candles)
            current_prices[symbol] = result['price']
            
            # 3. Execute Trade (Simulation)
            trade_action = trader.execute(symbol, result['signal'], result['price'])
            
            if trade_action:
                trade_logs.append(trade_action)
                print(f"   ⚡ ACTION: {trade_action}")
            
            # Format Report
            icon = "⚪"
            if "BUY" in result['signal']: icon = "🟢"
            elif "SELL" in result['signal']: icon = "🔴"
            
            line = f"{icon} {symbol.replace('USDT','')}: ${result['price']}\n"
            line += f"   RSI: {result['rsi']} ({result['signal'].split()[0]})\n"
            report_msg += line + "\n"
        else:
            report_msg += f"❌ {symbol}: Connection Failed\n"
            
    # 4. Portfolio Summary
    total_val = trader.get_portfolio_value(current_prices)
    roi = ((total_val - 1000) / 1000) * 100
    
    report_msg += "─" * 25 + "\n"
    report_msg += f"💰 Wallet: ${trader.state['usdt_balance']:.2f}\n"
    report_msg += f"📊 Net Worth: ${total_val:.2f} ({roi:+.2f}%)\n"
    
    if trade_logs:
        report_msg += "\n📝 NEW TRADES:\n" + "\n".join(trade_logs)
            
    print(f"\n[4] 📨 Sending Report (Val: ${total_val:.2f})...")
    send_telegram(report_msg)
    print("✅ Done.")

if __name__ == "__main__":
    main()
