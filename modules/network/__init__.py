from .mexc_api import MexcAPI

_client_instance = None

def get_client():
    global _client_instance
    if _client_instance is None:
        _client_instance = MexcAPI()
    return _client_instance
