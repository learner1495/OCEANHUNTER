#!/usr/bin/env python3
"""Ocean Hunter Configuration — MEXC Edition"""
import os
from pathlib import Path
from dotenv import load_dotenv

PROJECT_ROOT = Path(__file__).parent
load_dotenv(PROJECT_ROOT / ".env")

ACTIVE_EXCHANGE = "MEXC"
MEXC_API_KEY = os.getenv("MEXC_API_KEY", "")
MEXC_SECRET_KEY = os.getenv("MEXC_SECRET_KEY", "")
MEXC_BASE_URL = "https://api.mexc.com"
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID", "")
TRADE_COINS = ["BTC", "ETH", "SOL", "XRP", "DOGE"]
QUOTE_CURRENCY = "USDT"
ENTRY_SCORE_MIN = 70
RSI_PERIOD, RSI_OVERSOLD, BB_PERIOD = 14, 35, 20
VOLUME_SMA_PERIOD, VOLUME_SPIKE_MULT = 20, 1.5
TAKE_PROFIT_MIN, TAKE_PROFIT_MAX = 1.5, 3.0
TRAILING_STOP_TRIGGER, TRAILING_STOP_DISTANCE = 1.0, 0.5
MAX_POSITIONS, MIN_ORDER_USDT, RATE_LIMIT_DELAY = 3, 15, 0.5
MODE = os.getenv("MODE", "PAPER")
