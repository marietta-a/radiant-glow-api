from __future__ import annotations

import asyncio
import time
from collections import deque


class RateLimiter:
    """Sliding-window limiter: at most `max_calls` calls per `period` seconds.

    `acquire()` waits (FIFO) instead of failing, so bursts are smoothed out rather than rejected.
    `wait_for_capacity()` + `record()` let a single consumer check capacity before it takes work.
    """

    def __init__(self, max_calls: int, period: float):
        self.max_calls = max_calls
        self.period = period
        self._calls: deque[float] = deque()
        self._lock: asyncio.Lock | None = None  # created lazily, inside the running loop

    def _wait_time(self) -> float:
        now = time.monotonic()
        while self._calls and now - self._calls[0] >= self.period:
            self._calls.popleft()
        if len(self._calls) < self.max_calls:
            return 0.0
        return self._calls[0] + self.period - now

    def record(self) -> None:
        self._calls.append(time.monotonic())

    def try_acquire(self) -> bool:
        """Take a slot if one is free right now; never waits."""
        if self._wait_time() > 0:
            return False
        self.record()
        return True

    async def wait_for_capacity(self) -> None:
        while (wait := self._wait_time()) > 0:
            await asyncio.sleep(wait)

    async def acquire(self) -> None:
        if self._lock is None:
            self._lock = asyncio.Lock()
        async with self._lock:
            await self.wait_for_capacity()
            self.record()
