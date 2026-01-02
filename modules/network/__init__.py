# modules/network/__init__.py
from .nobitex_api import NobitexAPI

_client_instance = None

def get_client():
    global _client_instance
    if _client_instance is None:
        _client_instance = NobitexAPI()
    return _client_instance
