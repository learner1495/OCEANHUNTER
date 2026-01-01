import time
import threading
from typing import Optional

class RateLimiter:
    def __init__(self, max_tokens: int = 60, refill_seconds: float = 60.0):
        self.max_tokens = max_tokens
        self.tokens = max_tokens
        self.refill_rate = max_tokens / refill_seconds
        self.last_refill = time.time()
        self.lock = threading.Lock()
        self.min_spacing = 0.5
        self.last_request = 0.0
    
    def _refill(self):
        now = time.time()
        elapsed = now - self.last_refill
        self.tokens = min(self.max_tokens, self.tokens + elapsed * self.refill_rate)
        self.last_refill = now
    
    def acquire(self, tokens: int = 1, timeout: Optional[float] = 30.0) -> bool:
        start_time = time.time()
        while True:
            with self.lock:
                self._refill()
                spacing = time.time() - self.last_request
                if spacing < self.min_spacing:
                    time.sleep(self.min_spacing - spacing)
                if self.tokens >= tokens:
                    self.tokens -= tokens
                    self.last_request = time.time()
                    return True
            if timeout and (time.time() - start_time) >= timeout:
                return False
            time.sleep(0.1)
    
    def get_status(self) -> dict:
        with self.lock:
            self._refill()
            return {"tokens_available": round(self.tokens, 2), "max_tokens": self.max_tokens}

_limiter = RateLimiter()
def acquire(tokens: int = 1) -> bool:
    return _limiter.acquire(tokens)
def get_status() -> dict:
    return _limiter.get_status()
