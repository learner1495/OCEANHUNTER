import os
import time
import requests
from typing import Optional, Dict, Any
from dotenv import load_dotenv
from . import rate_limiter

load_dotenv()

class NobitexAPI:
    BASE_URL = "https://api.nobitex.ir"
    
    def __init__(self):
        self.api_key = os.getenv("NOBITEX_API_KEY", "")
        self.session = requests.Session()
        self.session.headers.update({
            "Authorization": f"Token {self.api_key}",
            "Content-Type": "application/json"
        })
        self._last_request_time = 0
    
    def _request(self, method: str, endpoint: str, data: dict = None) -> Dict[str, Any]:
        if not rate_limiter.acquire():
            return {"status": "error", "message": "Rate limit exceeded"}
        
        elapsed = time.time() - self._last_request_time
        if elapsed < 0.5:
            time.sleep(0.5 - elapsed)
        
        url = f"{self.BASE_URL}{endpoint}"
        try:
            if method.upper() == "GET":
                response = self.session.get(url, params=data, timeout=10)
            else:
                response = self.session.post(url, json=data, timeout=10)
            self._last_request_time = time.time()
            if response.status_code == 200:
                return response.json()
            return {"status": "error", "code": response.status_code}
        except Exception as e:
            return {"status": "error", "message": str(e)}
    
    def get_market_stats(self) -> Dict[str, Any]:
        return self._request("GET", "/market/stats")
    
    def get_wallets(self) -> Dict[str, Any]:
        return self._request("POST", "/users/wallets/list")
    
    def test_connection(self) -> Dict[str, Any]:
        result = {"public_api": False, "private_api": False, "message": ""}
        stats = self.get_market_stats()
        if stats.get("status") == "ok":
            result["public_api"] = Truewallets = self.get_wallets()
        if wallets.get("status") == "ok":
            result["private_api"] = True
            result["message"] = "Full access"
        else:
            result["message"] = "Auth issue"
        return result
    
    def get_rate_limit_status(self) -> Dict[str, Any]:
        return rate_limiter.get_status()

_client: Optional[NobitexAPI] = None
def get_client() -> NobitexAPI:
    global _client
    if _client is None:
        _client = NobitexAPI()
    return _client
