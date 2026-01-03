from .mexc_api import MEXCClient
from .telegram_bot import TelegramBot

def get_client():
    return MEXCClient()
