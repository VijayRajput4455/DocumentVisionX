"""
Metrics collection for performance monitoring.
Tracks operation latencies (OCR, LLM, extraction) by document type.
Supports per-operation timing and statistics aggregation.
"""

import time
from collections import defaultdict
from threading import Lock
from typing import Dict, List, Optional
from dataclasses import dataclass, field


@dataclass
class OperationMetrics:
    """Metrics for a single operation type."""
    operation: str
    count: int = 0
    total_ms: float = 0.0
    min_ms: float = float('inf')
    max_ms: float = 0.0
    samples: List[float] = field(default_factory=list)
    
    def add_sample(self, duration_ms: float):
        """Record a single operation timing."""
        self.count += 1
        self.total_ms += duration_ms
        self.min_ms = min(self.min_ms, duration_ms)
        self.max_ms = max(self.max_ms, duration_ms)
        self.samples.append(duration_ms)
        
        # Keep only last 100 samples to avoid unbounded memory growth
        if len(self.samples) > 100:
            self.samples.pop(0)
    
    @property
    def avg_ms(self) -> float:
        """Average operation duration (ms)."""
        return self.total_ms / self.count if self.count > 0 else 0.0
    
    @property
    def p50_ms(self) -> float:
        """Median operation duration (ms)."""
        if not self.samples:
            return 0.0
        sorted_samples = sorted(self.samples)
        mid = len(sorted_samples) // 2
        return sorted_samples[mid]
    
    @property
    def p95_ms(self) -> float:
        """95th percentile operation duration (ms)."""
        if not self.samples:
            return 0.0
        sorted_samples = sorted(self.samples)
        idx = int(len(sorted_samples) * 0.95)
        return sorted_samples[min(idx, len(sorted_samples) - 1)]
    
    def to_dict(self) -> dict:
        """Export metrics as dictionary."""
        return {
            "operation": self.operation,
            "count": self.count,
            "avg_ms": round(self.avg_ms, 2),
            "min_ms": round(self.min_ms, 2) if self.min_ms != float('inf') else 0.0,
            "max_ms": round(self.max_ms, 2),
            "p50_ms": round(self.p50_ms, 2),
            "p95_ms": round(self.p95_ms, 2),
        }


class MetricsCollector:
    """
    Thread-safe metrics collection for performance monitoring.
    
    Usage:
        metrics = MetricsCollector()
        start = metrics.timer_start()
        # ... do work ...
        metrics.record_operation("aadhar_ocr", start)
        
        stats = metrics.get_stats("aadhar_ocr")
    """
    
    def __init__(self):
        self._metrics: Dict[str, OperationMetrics] = defaultdict(
            lambda: OperationMetrics(operation="")
        )
        self._lock = Lock()
    
    @staticmethod
    def timer_start() -> float:
        """Start a timer (returns current time in ms)."""
        return time.time() * 1000.0
    
    def record_operation(self, operation: str, start_time_ms: float):
        """
        Record the duration of an operation.
        
        Args:
            operation: Operation name (e.g., "aadhar_ocr", "pancard_llm")
            start_time_ms: Start time from timer_start() in milliseconds
        """
        duration_ms = (time.time() * 1000.0) - start_time_ms
        
        with self._lock:
            if operation not in self._metrics:
                self._metrics[operation] = OperationMetrics(operation=operation)
            self._metrics[operation].add_sample(duration_ms)
    
    def get_stats(self, operation: str) -> Optional[dict]:
        """
        Get statistics for a specific operation.
        
        Returns:
            dict with count, avg_ms, min_ms, max_ms, p50_ms, p95_ms or None
        """
        with self._lock:
            if operation not in self._metrics:
                return None
            return self._metrics[operation].to_dict()
    
    def get_all_stats(self) -> Dict[str, dict]:
        """Get statistics for all tracked operations."""
        with self._lock:
            return {
                op: metrics.to_dict()
                for op, metrics in self._metrics.items()
            }
    
    def reset(self, operation: Optional[str] = None):
        """Reset metrics for a specific operation or all operations."""
        with self._lock:
            if operation:
                if operation in self._metrics:
                    del self._metrics[operation]
            else:
                self._metrics.clear()


# Global singleton metrics instance
_METRICS_INSTANCE = MetricsCollector()


def get_metrics_collector() -> MetricsCollector:
    """Get the global metrics collector instance."""
    return _METRICS_INSTANCE


def record_operation(operation: str, start_time_ms: float):
    """Convenience function to record an operation timing."""
    get_metrics_collector().record_operation(operation, start_time_ms)


def timer_start() -> float:
    """Convenience function to start a timer."""
    return MetricsCollector.timer_start()
