import time
import logging
from collections import deque

logger = logging.getLogger("RateLimiter")

class RateLimiter:
    def __init__(self, max_calls=25, period=60):
        self.max_calls = max_calls
        self.period = period
        self.timestamps = deque()

    def wait_if_needed(self):
        now = time.time()
        while self.timestamps and self.timestamps[0] <= now - self.period:
            self.timestamps.popleft()

        if len(self.timestamps) >= self.max_calls:
            sleep_time = self.timestamps[0] + self.period - now + 0.1
            if sleep_time > 0:
                time.sleep(sleep_time)
            self.wait_if_needed()
        
        self.timestamps.append(time.time())