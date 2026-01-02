import time
import logging
from collections import deque

logger = logging.getLogger("RateLimiter")

class RateLimiter:
    def __init__(self, max_calls=25, period=60):
        """
        Nobitex Limit: 30 req/min.
        We use 25 req/min (Safety Buffer).
        """
        self.max_calls = max_calls
        self.period = period
        self.timestamps = deque()

    def wait_if_needed(self):
        """Checks history and waits if limit is reached."""
        now = time.time()
        
        # Remove timestamps older than the period
        while self.timestamps and self.timestamps[0] <= now - self.period:
            self.timestamps.popleft()

        if len(self.timestamps) >= self.max_calls:
            sleep_time = self.timestamps[0] + self.period - now + 0.1
            if sleep_time > 0:
                logger.warning(f"Rate limit reached. Sleeping for {sleep_time:.2f}s")
                time.sleep(sleep_time)
            
            # Clean up again after sleep
            self.wait_if_needed()
        
        self.timestamps.append(time.time())