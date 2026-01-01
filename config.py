# config.py — OCEAN HUNTER V10.8.2
# ═══════════════════════════════════════════════════════════════

import os
from dotenv import load_dotenv

load_dotenv()

# ═══ API KEYS ═══
NOBITEX_API_KEY = os.getenv("NOBITEX_API_KEY", "")
NOBITEX_API_SECRET = os.getenv("NOBITEX_API_SECRET", "")
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID", "")

# ═══ PROXY ═══
PROXY_HOST = os.getenv("PROXY_HOST", "127.0.0.1")
PROXY_PORT = int(os.getenv("PROXY_PORT", 1080))

# ═══ TRADING PAIRS ═══
TRADE_COINS = ["SOL", "BNB", "XRP", "AVAX", "LINK"]
QUOTE_CURRENCY = "USDT"

# ═══ ALLOCATION (%) ═══
ALLOCATION = {
    "SOL": 25,
    "BNB": 20,
    "XRP": 15,
    "AVAX": 10,
    "LINK": 10,
    "USDT": 10,  # Reserve"BTC": 5,    # Growth Fund
    "PAXG": 5,   # Safe Haven
}

# ═══ STRATEGY PARAMS ═══
ENTRY_SCORE_MIN = 70
RSI_PERIOD = 14
RSI_OVERSOLD = 35
BB_PERIOD = 20
VOLUME_SMA_PERIOD = 20
VOLUME_SPIKE_MULT = 1.5

# ═══ EXIT PARAMS ═══
TAKE_PROFIT_MIN = 1.5  # %
TAKE_PROFIT_MAX = 3.0  # %
TRAILING_STOP_TRIGGER = 1.0  # %
TRAILING_STOP_DISTANCE = 0.5  # %

# ═══ DCA LAYERS ═══
DCA_LAYERS = {
    "L1": {"trigger": -3, "add": 50},
    "L2": {"trigger": -6, "add": 75},
    "L3": {"trigger": -10, "add": 100},
}

# ═══ LIMITS ═══
MAX_POSITIONS = 3
MIN_ORDER_USDT = 15  # 12 + buffer
RATE_LIMIT_DELAY = 2.5  # seconds

# ═══ NOBITEX API ═══
NOBITEX_BASE_URL = "https://api.nobitex.ir"
