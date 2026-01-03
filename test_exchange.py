# ═══════════════════════════════════════════════════════════════
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
    print("\n[1] Connecting to MEXC...")
    
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
    print("\n[2] Fetching Crypto Prices...")
    
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
    print("\n[3] Checking Account Balance...")
    
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
    print("\n[4] Building Report...")
    
    report = "🌊 <b>OCEAN HUNTER — Market Report</b>\n"
    report += f"📅 {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
    report += "─" * 25 + "\n\n"
    
    # Prices section
    report += "📊 <b>Top 10 Crypto Prices:</b>\n"
    for symbol, price in prices.items():
        coin = symbol.replace("USDT", "")
        if price >= 1000:
            report += f"   • {coin}: <code>${price:,.2f}</code>\n"
        elif price >= 1:
            report += f"   • {coin}: <code>${price:.4f}</code>\n"
        else:
            report += f"   • {coin}: <code>${price:.8f}</code>\n"
    
    report += "\n"
    
    # Balance section
    if balances:
        report += "💼 <b>Your Balances:</b>\n"
        for b in balances[:10]:  # Max 10
            report += f"   • {b['asset']}: <code>{b['free']:.6f}</code>\n"
    else:
        report += "💼 <b>Balances:</b> No assets\n"
    
    report += "\n✅ <i>Connection Test Successful!</i>"
    
    print("   ✅ Report Ready!")
    
    # ═══ Step 5: Send to Telegram ═══
    print("\n[5] Sending to Telegram...")
    
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
            print("\n" + "=" * 60)
            print("🎉 ALL TESTS PASSED!")
            print("=" * 60)
        else:
            print(f"   ❌ Send failed: {result}")
            
    except Exception as e:
        print(f"   ❌ Telegram Error: {e}")

if __name__ == "__main__":
    main()
