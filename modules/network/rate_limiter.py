# modules/network/rate_limiter.py
import time
import threading

class RateLimiter:
    def __init__(self, max_tokens: int = 60, refill_seconds: float = 60.0):
        self.max_tokens = max_tokens
        self.tokens = max_tokens
        self.refill_rate = max_tokens / refill_seconds
        self.last_refill = time.time()
        self.lock = threading.Lock()

    def _refill(self):
        now = time.time()
        elapsed = now - self.last_refill
        self.tokens = min(self.max_tokens, self.tokens + elapsed * self.refill_rate)
        self.last_refill = now

    def acquire(self, tokens: int = 1) -> bool:
        with self.lock:
            self._refill()
            if self.tokens >= tokens:
                self.tokens -= tokens
                return True
            return False

    def get_status(self) -> dict:
        with self.lock:
            self._refill()
            return {
                "tokens_available": round(self.tokens, 2),
                "max_tokens": self.max_tokens,
                "usage_percent": round((1 - self.tokens/self.max_tokens) * 100, 1)
            }

_limiter = RateLimiter()

def acquire(tokens: int = 1) -> bool:
    return _limiter.acquire(tokens)

def get_status() -> dict:
    return _limiter.get_status()
