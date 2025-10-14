"""
Rate limiter utility for API throttling.

Implements token bucket algorithm for rate limiting API requests.
"""

import time
from threading import Lock
from typing import Optional

from lib.logger import get_logger

logger = get_logger("rate_limiter")


class RateLimiter:
    """
    Token bucket rate limiter for API requests.

    Limits the rate of requests to prevent exceeding API quotas.
    """

    def __init__(self, requests_per_minute: int = 60):
        """
        Initialize rate limiter.

        Args:
            requests_per_minute: Maximum requests per minute
        """
        self.requests_per_minute = requests_per_minute
        self.tokens = requests_per_minute
        self.max_tokens = requests_per_minute
        self.last_refill = time.time()
        self.lock = Lock()

        logger.debug(f"Rate limiter initialized: {requests_per_minute} req/min")

    def _refill_tokens(self):
        """Refill tokens based on elapsed time."""
        now = time.time()
        elapsed = now - self.last_refill

        # Add tokens based on elapsed time
        tokens_to_add = elapsed * (self.requests_per_minute / 60.0)
        self.tokens = min(self.max_tokens, self.tokens + tokens_to_add)
        self.last_refill = now

    def acquire(self, timeout: Optional[float] = None) -> bool:
        """
        Acquire permission to make a request.

        Blocks until a token is available or timeout is reached.

        Args:
            timeout: Maximum time to wait in seconds (None = wait forever)

        Returns:
            True if acquired, False if timeout reached
        """
        start_time = time.time()

        while True:
            with self.lock:
                self._refill_tokens()

                if self.tokens >= 1:
                    self.tokens -= 1
                    logger.debug(f"Token acquired ({self.tokens:.1f} remaining)")
                    return True

            # Check timeout
            if timeout is not None:
                elapsed = time.time() - start_time
                if elapsed >= timeout:
                    logger.warning("Rate limit acquisition timeout")
                    return False

            # Wait a bit before retrying
            time.sleep(0.1)

    def wait_if_needed(self):
        """
        Wait if rate limit would be exceeded.

        Convenience method that blocks until ready.
        """
        self.acquire()
