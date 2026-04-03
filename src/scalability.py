import time
from collections import defaultdict, deque
from threading import BoundedSemaphore, Lock

from src.config import (
    API_RATE_LIMIT_PER_MINUTE,
    MAX_CONCURRENT_LLM_CALLS,
    MAX_CONCURRENT_OCR_TASKS,
)

OCR_LIMIT = max(1, MAX_CONCURRENT_OCR_TASKS)
LLM_LIMIT = max(1, MAX_CONCURRENT_LLM_CALLS)

OCR_SEMAPHORE = BoundedSemaphore(OCR_LIMIT)
LLM_SEMAPHORE = BoundedSemaphore(LLM_LIMIT)


class InMemoryRateLimiter:
    def __init__(self, requests_per_minute: int):
        self.requests_per_minute = max(1, requests_per_minute)
        self.window_seconds = 60
        self._buckets = defaultdict(deque)
        self._lock = Lock()

    def allow(self, key: str) -> bool:
        now = time.time()
        cutoff = now - self.window_seconds

        with self._lock:
            bucket = self._buckets[key]
            while bucket and bucket[0] < cutoff:
                bucket.popleft()

            if len(bucket) >= self.requests_per_minute:
                return False

            bucket.append(now)
            return True

    def snapshot(self):
        now = time.time()
        cutoff = now - self.window_seconds

        with self._lock:
            active_keys = 0
            requests_in_window = 0

            for key, bucket in list(self._buckets.items()):
                while bucket and bucket[0] < cutoff:
                    bucket.popleft()

                if not bucket:
                    del self._buckets[key]
                    continue

                active_keys += 1
                requests_in_window += len(bucket)

            return {
                "requests_per_minute": self.requests_per_minute,
                "window_seconds": self.window_seconds,
                "active_keys": active_keys,
                "requests_in_window": requests_in_window,
            }


def _semaphore_stats(name, semaphore, limit):
    # CPython exposes current free slots via the private _value field.
    available = int(getattr(semaphore, "_value", 0))
    in_use = max(0, limit - available)
    utilization = in_use / limit if limit else 0.0
    return {
        "name": name,
        "limit": limit,
        "in_use": in_use,
        "available": available,
        "utilization": round(utilization, 3),
    }


def get_scalability_stats():
    return {
        "ocr": _semaphore_stats("ocr", OCR_SEMAPHORE, OCR_LIMIT),
        "llm": _semaphore_stats("llm", LLM_SEMAPHORE, LLM_LIMIT),
        "rate_limit": RATE_LIMITER.snapshot(),
    }


RATE_LIMITER = InMemoryRateLimiter(API_RATE_LIMIT_PER_MINUTE)
