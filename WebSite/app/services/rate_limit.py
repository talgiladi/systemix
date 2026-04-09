"""Small in-memory rate limiting utility for contact submissions."""

from __future__ import annotations

import time
from collections import defaultdict, deque
from threading import Lock

from app.config import settings


class SlidingWindowRateLimiter:
    """Permit a fixed number of events within a moving time window."""

    def __init__(self, max_requests: int, window_seconds: int) -> None:
        self.max_requests = max_requests
        self.window_seconds = window_seconds
        self._events: dict[str, deque[float]] = defaultdict(deque)
        self._lock = Lock()

    def allow(self, key: str) -> bool:
        now = time.time()
        with self._lock:
            timestamps = self._events[key]
            while timestamps and now - timestamps[0] > self.window_seconds:
                timestamps.popleft()
            if len(timestamps) >= self.max_requests:
                return False
            timestamps.append(now)
            return True


contact_rate_limiter = SlidingWindowRateLimiter(
    max_requests=settings.contact_rate_limit,
    window_seconds=settings.contact_rate_window_seconds,
)
