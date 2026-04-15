"""
Metrics Collection System
==========================

Collects and aggregates performance metrics from agents and workflows.
"""

from typing import Dict, Any, List, Optional, Callable
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
import uuid
import threading
from collections import defaultdict


class MetricType(str, Enum):
    """Types of metrics that can be collected."""
    COUNTER = "counter"  # Incrementing value (e.g., requests)
    GAUGE = "gauge"  # Point-in-time value (e.g., memory)
    HISTOGRAM = "histogram"  # Distribution of values
    TIMER = "timer"  # Duration measurements


@dataclass
class MetricPoint:
    """Single metric data point."""
    
    metric_name: str
    metric_type: MetricType
    value: float
    timestamp: str = field(default_factory=lambda: datetime.utcnow().isoformat())
    labels: Dict[str, str] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "metric_name": self.metric_name,
            "metric_type": self.metric_type.value,
            "value": self.value,
            "timestamp": self.timestamp,
            "labels": self.labels,
        }


@dataclass
class MetricSeries:
    """Time series of metric points."""
    
    metric_name: str
    metric_type: MetricType
    labels: Dict[str, str] = field(default_factory=dict)
    points: List[MetricPoint] = field(default_factory=list)
    
    def add_point(self, value: float, timestamp: Optional[str] = None):
        """Add a data point."""
        if timestamp is None:
            timestamp = datetime.utcnow().isoformat()
        
        point = MetricPoint(
            metric_name=self.metric_name,
            metric_type=self.metric_type,
            value=value,
            timestamp=timestamp,
            labels=self.labels,
        )
        self.points.append(point)
    
    def latest(self) -> Optional[float]:
        """Get latest value."""
        if not self.points:
            return None
        return self.points[-1].value
    
    def average(self, window_seconds: int = 60) -> Optional[float]:
        """Get average over time window."""
        if not self.points:
            return None
        
        cutoff = datetime.utcnow() - timedelta(seconds=window_seconds)
        recent = [
            p for p in self.points
            if datetime.fromisoformat(p.timestamp) > cutoff
        ]
        
        if not recent:
            return None
        
        return sum(p.value for p in recent) / len(recent)
    
    def count(self, window_seconds: int = 60) -> int:
        """Get count of points in time window."""
        if not self.points:
            return 0
        
        cutoff = datetime.utcnow() - timedelta(seconds=window_seconds)
        return sum(
            1 for p in self.points
            if datetime.fromisoformat(p.timestamp) > cutoff
        )


class MetricsCollector:
    """Centralized metrics collection system."""
    
    def __init__(self, retention_seconds: int = 3600):
        self._metrics: Dict[str, Dict[str, MetricSeries]] = defaultdict(dict)
        self._retention_seconds = retention_seconds
        self._lock = threading.Lock()
        self._callbacks: List[Callable] = []
    
    def _get_key(self, metric_name: str, labels: Dict[str, str]) -> str:
        """Generate unique key for metric series."""
        label_str = ",".join(f"{k}={v}" for k, v in sorted(labels.items()))
        return f"{metric_name}{{{label_str}}}"
    
    def _cleanup_old_points(self):
        """Remove points older than retention period."""
        cutoff = datetime.utcnow() - timedelta(seconds=self._retention_seconds)
        
        for metric_dict in self._metrics.values():
            for series in metric_dict.values():
                series.points = [
                    p for p in series.points
                    if datetime.fromisoformat(p.timestamp) > cutoff
                ]
    
    def record(self, metric_name: str, value: float, 
               metric_type: MetricType = MetricType.GAUGE,
               labels: Optional[Dict[str, str]] = None):
        """Record a metric value."""
        if labels is None:
            labels = {}
        
        key = self._get_key(metric_name, labels)
        
        with self._lock:
            if key not in self._metrics[metric_name]:
                self._metrics[metric_name][key] = MetricSeries(
                    metric_name=metric_name,
                    metric_type=metric_type,
                    labels=labels,
                )
            
            self._metrics[metric_name][key].add_point(value)
            
            # Periodic cleanup
            if len(self._metrics[metric_name][key].points) > 1000:
                self._cleanup_old_points()
        
        # Notify callbacks
        for callback in self._callbacks:
            try:
                callback(metric_name, value, labels)
            except Exception:
                pass
    
    def increment(self, metric_name: str, amount: float = 1.0,
                  labels: Optional[Dict[str, str]] = None):
        """Increment a counter metric."""
        if labels is None:
            labels = {}
        
        key = self._get_key(metric_name, labels)
        
        with self._lock:
            if key not in self._metrics[metric_name]:
                self._metrics[metric_name][key] = MetricSeries(
                    metric_name=metric_name,
                    metric_type=MetricType.COUNTER,
                    labels=labels,
                )
            
            current = self._metrics[metric_name][key].latest() or 0
            self._metrics[metric_name][key].add_point(current + amount)
    
    def timer(self, metric_name: str, labels: Optional[Dict[str, str]] = None):
        """Context manager for timing operations."""
        return TimerContext(self, metric_name, labels or {})
    
    def get_metric(self, metric_name: str, 
                   labels: Optional[Dict[str, str]] = None) -> Optional[MetricSeries]:
        """Get a metric series."""
        if labels is None:
            labels = {}
        
        key = self._get_key(metric_name, labels)
        
        with self._lock:
            if metric_name in self._metrics:
                return self._metrics[metric_name].get(key)
        return None
    
    def get_all_metrics(self, window_seconds: int = 60) -> Dict[str, Any]:
        """Get all metrics with recent data."""
        result = {}
        cutoff = datetime.utcnow() - timedelta(seconds=window_seconds)
        
        with self._lock:
            for metric_name, series_dict in self._metrics.items():
                metric_data = []
                for key, series in series_dict.items():
                    recent_points = [
                        p for p in series.points
                        if datetime.fromisoformat(p.timestamp) > cutoff
                    ]
                    if recent_points:
                        metric_data.append({
                            "name": metric_name,
                            "type": series.metric_type.value,
                            "labels": series.labels,
                            "latest": series.latest(),
                            "average": series.average(window_seconds),
                            "count": len(recent_points),
                        })
                
                if metric_data:
                    result[metric_name] = metric_data
        
        return result
    
    def register_callback(self, callback: Callable):
        """Register a callback to be called on each metric record."""
        self._callbacks.append(callback)
    
    def clear(self):
        """Clear all metrics."""
        with self._lock:
            self._metrics.clear()


class TimerContext:
    """Context manager for timing operations."""
    
    def __init__(self, collector: MetricsCollector, metric_name: str, 
                 labels: Dict[str, str]):
        self.collector = collector
        self.metric_name = metric_name
        self.labels = labels
        self.start_time: Optional[datetime] = None
    
    def __enter__(self):
        self.start_time = datetime.utcnow()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.start_time:
            duration = (datetime.utcnow() - self.start_time).total_seconds()
            self.collector.record(
                self.metric_name,
                duration * 1000,  # Convert to milliseconds
                MetricType.TIMER,
                self.labels,
            )
        return False
