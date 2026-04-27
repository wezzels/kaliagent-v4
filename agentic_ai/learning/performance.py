"""
Performance Tracking
=====================

Tracks agent performance metrics over time.
"""

from typing import Optional, Dict, Any, List
from dataclasses import dataclass, field
from datetime import datetime, timedelta
import json


@dataclass
class AgentMetrics:
    """Performance metrics for an agent."""

    agent_id: str
    task_type: str

    # Task counts
    total_tasks: int = 0
    successful_tasks: int = 0
    failed_tasks: int = 0

    # Timing
    total_time_ms: float = 0.0
    avg_time_ms: float = 0.0
    min_time_ms: Optional[float] = None
    max_time_ms: Optional[float] = None

    # Quality
    avg_rating: Optional[float] = None
    total_feedback_count: int = 0
    positive_feedback: int = 0
    negative_feedback: int = 0

    # Learning
    corrections_count: int = 0
    improvement_rate: float = 0.0  # Rate of improvement over time

    # Error tracking
    error_counts: Dict[str, int] = field(default_factory=dict)

    # Time tracking
    first_task_at: Optional[str] = None
    last_task_at: Optional[str] = None
    updated_at: str = field(default_factory=lambda: datetime.utcnow().isoformat())

    def record_task(
        self,
        success: bool,
        duration_ms: float,
        error: Optional[str] = None,
    ):
        """Record a task execution."""
        self.total_tasks += 1
        self.updated_at = datetime.utcnow().isoformat()

        if success:
            self.successful_tasks += 1
        else:
            self.failed_tasks += 1
            if error:
                self.error_counts[error] = self.error_counts.get(error, 0) + 1

        # Update timing
        self.total_time_ms += duration_ms
        self.avg_time_ms = self.total_time_ms / self.total_tasks

        if self.min_time_ms is None or duration_ms < self.min_time_ms:
            self.min_time_ms = duration_ms
        if self.max_time_ms is None or duration_ms > self.max_time_ms:
            self.max_time_ms = duration_ms

        # Update timestamps
        now = datetime.utcnow().isoformat()
        if not self.first_task_at:
            self.first_task_at = now
        self.last_task_at = now

    def record_feedback(self, rating: float, is_positive: bool):
        """Record feedback."""
        self.total_feedback_count += 1

        # Update average rating
        if self.avg_rating is None:
            self.avg_rating = rating
        else:
            # Running average
            self.avg_rating = (
                (self.avg_rating * (self.total_feedback_count - 1) + rating)
                / self.total_feedback_count
            )

        if is_positive:
            self.positive_feedback += 1
        else:
            self.negative_feedback += 1

    def record_correction(self):
        """Record a correction."""
        self.corrections_count += 1

    def get_success_rate(self) -> float:
        """Get success rate."""
        if self.total_tasks == 0:
            return 0.0
        return self.successful_tasks / self.total_tasks

    def get_feedback_ratio(self) -> float:
        """Get positive feedback ratio."""
        if self.total_feedback_count == 0:
            return 0.0
        return self.positive_feedback / self.total_feedback_count

    def get_performance_score(self) -> float:
        """Get overall performance score (0.0-1.0)."""
        # Weight factors
        success_weight = 0.4
        feedback_weight = 0.3
        speed_weight = 0.2
        correction_weight = 0.1

        # Success rate component
        success_score = self.get_success_rate()

        # Feedback component
        feedback_score = self.get_feedback_ratio()

        # Speed component (normalize to 0-1, assume 10s is good)
        speed_score = 1.0
        if self.avg_time_ms and self.avg_time_ms > 0:
            speed_score = min(1.0, 10000 / self.avg_time_ms)  # 10s = 1.0

        # Correction penalty
        correction_score = max(0.0, 1.0 - (self.corrections_count * 0.1))

        # Weighted average
        total_score = (
            success_weight * success_score +
            feedback_weight * feedback_score +
            speed_weight * speed_score +
            correction_weight * correction_score
        )

        return min(1.0, max(0.0, total_score))

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "agent_id": self.agent_id,
            "task_type": self.task_type,
            "total_tasks": self.total_tasks,
            "successful_tasks": self.successful_tasks,
            "failed_tasks": self.failed_tasks,
            "success_rate": self.get_success_rate(),
            "avg_time_ms": self.avg_time_ms,
            "min_time_ms": self.min_time_ms,
            "max_time_ms": self.max_time_ms,
            "avg_rating": self.avg_rating,
            "total_feedback_count": self.total_feedback_count,
            "feedback_ratio": self.get_feedback_ratio(),
            "corrections_count": self.corrections_count,
            "performance_score": self.get_performance_score(),
            "error_counts": self.error_counts,
            "first_task_at": self.first_task_at,
            "last_task_at": self.last_task_at,
            "updated_at": self.updated_at,
        }


class PerformanceTracker:
    """Tracks performance metrics for all agents."""

    def __init__(self):
        self.metrics: Dict[str, AgentMetrics] = {}  # key: "agent_id:task_type"
        self.history: List[Dict[str, Any]] = []  # Historical snapshots

    def _get_key(self, agent_id: str, task_type: str) -> str:
        """Get metrics key."""
        return f"{agent_id}:{task_type}"

    def get_or_create_metrics(
        self,
        agent_id: str,
        task_type: str,
    ) -> AgentMetrics:
        """Get or create metrics for an agent/task type."""
        key = self._get_key(agent_id, task_type)

        if key not in self.metrics:
            self.metrics[key] = AgentMetrics(
                agent_id=agent_id,
                task_type=task_type,
            )

        return self.metrics[key]

    def record_task(
        self,
        agent_id: str,
        task_type: str,
        success: bool,
        duration_ms: float,
        error: Optional[str] = None,
    ) -> AgentMetrics:
        """Record a task execution."""
        metrics = self.get_or_create_metrics(agent_id, task_type)
        metrics.record_task(success, duration_ms, error)

        # Record in history
        self.history.append({
            "timestamp": datetime.utcnow().isoformat(),
            "agent_id": agent_id,
            "task_type": task_type,
            "success": success,
            "duration_ms": duration_ms,
            "error": error,
        })

        return metrics

    def record_feedback(
        self,
        agent_id: str,
        task_type: str,
        rating: float,
        is_positive: bool,
    ) -> AgentMetrics:
        """Record feedback."""
        metrics = self.get_or_create_metrics(agent_id, task_type)
        metrics.record_feedback(rating, is_positive)
        return metrics

    def record_correction(
        self,
        agent_id: str,
        task_type: str,
    ) -> AgentMetrics:
        """Record a correction."""
        metrics = self.get_or_create_metrics(agent_id, task_type)
        metrics.record_correction()
        return metrics

    def get_agent_metrics(self, agent_id: str) -> Dict[str, AgentMetrics]:
        """Get all metrics for an agent."""
        return {
            key: metrics
            for key, metrics in self.metrics.items()
            if metrics.agent_id == agent_id
        }

    def get_task_type_metrics(self, task_type: str) -> Dict[str, AgentMetrics]:
        """Get metrics for a task type across all agents."""
        return {
            key: metrics
            for key, metrics in self.metrics.items()
            if metrics.task_type == task_type
        }

    def get_top_performers(
        self,
        task_type: Optional[str] = None,
        limit: int = 5,
    ) -> List[AgentMetrics]:
        """Get top performing agents."""
        metrics_list = list(self.metrics.values())

        if task_type:
            metrics_list = [m for m in metrics_list if m.task_type == task_type]

        # Sort by performance score
        sorted_metrics = sorted(
            metrics_list,
            key=lambda m: m.get_performance_score(),
            reverse=True,
        )

        return sorted_metrics[:limit]

    def get_worst_performers(
        self,
        task_type: Optional[str] = None,
        limit: int = 5,
    ) -> List[AgentMetrics]:
        """Get worst performing agents."""
        metrics_list = list(self.metrics.values())

        if task_type:
            metrics_list = [m for m in metrics_list if m.task_type == task_type]

        # Filter to agents with at least 5 tasks
        metrics_list = [m for m in metrics_list if m.total_tasks >= 5]

        # Sort by performance score ascending
        sorted_metrics = sorted(
            metrics_list,
            key=lambda m: m.get_performance_score(),
        )

        return sorted_metrics[:limit]

    def get_improvement_rate(
        self,
        agent_id: str,
        task_type: str,
        window_days: int = 7,
    ) -> float:
        """Calculate improvement rate over time window."""
        metrics = self.get_or_create_metrics(agent_id, task_type)

        # Get history for this agent/task
        agent_history = [
            h for h in self.history
            if h["agent_id"] == agent_id and h["task_type"] == task_type
        ]

        if len(agent_history) < 10:  # Need enough data
            return 0.0

        # Split into first half and second half
        mid = len(agent_history) // 2
        first_half = agent_history[:mid]
        second_half = agent_history[mid:]

        # Calculate success rates
        first_success = sum(1 for h in first_half if h["success"]) / len(first_half)
        second_success = sum(1 for h in second_half if h["success"]) / len(second_half)

        # Improvement rate
        rate = second_success - first_success

        # Update metrics
        metrics.improvement_rate = rate

        return rate

    def get_stats(self) -> Dict[str, Any]:
        """Get overall statistics."""
        total_agents = len(set(m.agent_id for m in self.metrics.values()))
        total_task_types = len(set(m.task_type for m in self.metrics.values()))

        avg_performance = (
            sum(m.get_performance_score() for m in self.metrics.values())
            / len(self.metrics)
            if self.metrics else 0.0
        )

        return {
            "total_metrics": len(self.metrics),
            "total_agents": total_agents,
            "total_task_types": total_task_types,
            "total_history_records": len(self.history),
            "avg_performance_score": avg_performance,
        }

    def export_metrics(self) -> str:
        """Export all metrics as JSON."""
        return json.dumps(
            {key: metrics.to_dict() for key, metrics in self.metrics.items()},
            indent=2,
        )
