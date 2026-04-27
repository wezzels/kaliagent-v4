"""
Feedback Collection
====================

Collects and processes feedback for agent learning.
"""

from typing import Optional, Dict, Any, List
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
import uuid


class FeedbackType(str, Enum):
    """Types of feedback."""
    EXPLICIT_POSITIVE = "explicit_positive"  # User rated 4-5 stars
    EXPLICIT_NEGATIVE = "explicit_negative"  # User rated 1-2 stars
    IMPLICIT_SUCCESS = "implicit_success"  # Task completed successfully
    IMPLICIT_FAILURE = "implicit_failure"  # Task failed or error
    CORRECTION = "correction"  # User corrected agent output
    SUGGESTION = "suggestion"  # User provided improvement suggestion


@dataclass
class Feedback:
    """A single feedback instance."""

    feedback_id: str = field(default_factory=lambda: str(uuid.uuid4())[:8])
    agent_id: str = ""
    task_type: str = ""
    feedback_type: FeedbackType = FeedbackType.IMPLICIT_SUCCESS
    rating: Optional[float] = None  # 1.0-5.0 for explicit feedback
    content: str = ""  # Feedback text or correction
    context: Dict[str, Any] = field(default_factory=dict)  # Task context
    original_output: Optional[str] = None  # For corrections
    corrected_output: Optional[str] = None  # For corrections
    source: str = "user"  # user, system, agent
    weight: float = 1.0  # Feedback importance
    created_at: str = field(default_factory=lambda: datetime.utcnow().isoformat())

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "feedback_id": self.feedback_id,
            "agent_id": self.agent_id,
            "task_type": self.task_type,
            "feedback_type": self.feedback_type.value,
            "rating": self.rating,
            "content": self.content,
            "context": self.context,
            "original_output": self.original_output,
            "corrected_output": self.corrected_output,
            "source": self.source,
            "weight": self.weight,
            "created_at": self.created_at,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Feedback":
        """Create from dictionary."""
        return cls(
            feedback_id=data.get("feedback_id", str(uuid.uuid4())[:8]),
            agent_id=data.get("agent_id", ""),
            task_type=data.get("task_type", ""),
            feedback_type=FeedbackType(data.get("feedback_type", "implicit_success")),
            rating=data.get("rating"),
            content=data.get("content", ""),
            context=data.get("context", {}),
            original_output=data.get("original_output"),
            corrected_output=data.get("corrected_output"),
            source=data.get("source", "user"),
            weight=data.get("weight", 1.0),
            created_at=data.get("created_at", datetime.utcnow().isoformat()),
        )

    def get_score(self) -> float:
        """Get numerical score from feedback (-1.0 to 1.0)."""
        if self.feedback_type == FeedbackType.EXPLICIT_POSITIVE:
            return (self.rating or 5.0) / 5.0  # 0.8-1.0
        elif self.feedback_type == FeedbackType.EXPLICIT_NEGATIVE:
            return -(5.0 - (self.rating or 1.0)) / 5.0  # -0.8 to -1.0
        elif self.feedback_type == FeedbackType.IMPLICIT_SUCCESS:
            return 0.5  # Mild positive
        elif self.feedback_type == FeedbackType.IMPLICIT_FAILURE:
            return -0.5  # Mild negative
        elif self.feedback_type == FeedbackType.CORRECTION:
            return -0.3  # Slight negative (needed correction)
        elif self.feedback_type == FeedbackType.SUGGESTION:
            return 0.2  # Slight positive (engagement)
        return 0.0


class FeedbackCollector:
    """Collects and aggregates feedback for agents."""

    def __init__(self):
        self.feedback: List[Feedback] = []
        self.agent_feedback: Dict[str, List[Feedback]] = {}
        self.task_type_feedback: Dict[str, List[Feedback]] = {}
        self._callbacks: List = []

    def add_feedback(self, feedback: Feedback) -> str:
        """Add feedback to the collector."""
        self.feedback.append(feedback)

        # Index by agent
        if feedback.agent_id not in self.agent_feedback:
            self.agent_feedback[feedback.agent_id] = []
        self.agent_feedback[feedback.agent_id].append(feedback)

        # Index by task type
        if feedback.task_type not in self.task_type_feedback:
            self.task_type_feedback[feedback.task_type] = []
        self.task_type_feedback[feedback.task_type].append(feedback)

        # Notify callbacks
        for callback in self._callbacks:
            try:
                callback(feedback)
            except Exception:
                pass

        return feedback.feedback_id

    def submit_rating(
        self,
        agent_id: str,
        task_type: str,
        rating: float,
        content: str = "",
        context: Optional[Dict[str, Any]] = None,
    ) -> Feedback:
        """Submit explicit rating feedback."""
        feedback_type = (
            FeedbackType.EXPLICIT_POSITIVE if rating >= 3.5
            else FeedbackType.EXPLICIT_NEGATIVE
        )

        feedback = Feedback(
            agent_id=agent_id,
            task_type=task_type,
            feedback_type=feedback_type,
            rating=min(5.0, max(1.0, rating)),
            content=content,
            context=context or {},
        )

        self.add_feedback(feedback)
        return feedback

    def record_success(
        self,
        agent_id: str,
        task_type: str,
        context: Optional[Dict[str, Any]] = None,
    ) -> Feedback:
        """Record implicit success feedback."""
        feedback = Feedback(
            agent_id=agent_id,
            task_type=task_type,
            feedback_type=FeedbackType.IMPLICIT_SUCCESS,
            context=context or {},
        )

        self.add_feedback(feedback)
        return feedback

    def record_failure(
        self,
        agent_id: str,
        task_type: str,
        error: str = "",
        context: Optional[Dict[str, Any]] = None,
    ) -> Feedback:
        """Record implicit failure feedback."""
        feedback = Feedback(
            agent_id=agent_id,
            task_type=task_type,
            feedback_type=FeedbackType.IMPLICIT_FAILURE,
            content=error,
            context=context or {},
        )

        self.add_feedback(feedback)
        return feedback

    def record_correction(
        self,
        agent_id: str,
        task_type: str,
        original: str,
        corrected: str,
        context: Optional[Dict[str, Any]] = None,
    ) -> Feedback:
        """Record a correction feedback."""
        feedback = Feedback(
            agent_id=agent_id,
            task_type=task_type,
            feedback_type=FeedbackType.CORRECTION,
            original_output=original,
            corrected_output=corrected,
            content=f"Corrected: {original[:50]}... → {corrected[:50]}...",
            context=context or {},
        )

        self.add_feedback(feedback)
        return feedback

    def get_agent_feedback(self, agent_id: str) -> List[Feedback]:
        """Get all feedback for an agent."""
        return self.agent_feedback.get(agent_id, [])

    def get_task_type_feedback(self, task_type: str) -> List[Feedback]:
        """Get all feedback for a task type."""
        return self.task_type_feedback.get(task_type, [])

    def get_recent_feedback(
        self,
        agent_id: Optional[str] = None,
        limit: int = 50,
    ) -> List[Feedback]:
        """Get recent feedback, optionally filtered by agent."""
        if agent_id:
            feedback_list = self.agent_feedback.get(agent_id, self.feedback)
        else:
            feedback_list = self.feedback

        # Sort by created_at descending
        sorted_feedback = sorted(
            feedback_list,
            key=lambda f: f.created_at,
            reverse=True,
        )

        return sorted_feedback[:limit]

    def get_average_rating(self, agent_id: str) -> Optional[float]:
        """Get average rating for an agent."""
        feedback_list = self.get_agent_feedback(agent_id)

        ratings = [f.rating for f in feedback_list if f.rating is not None]
        if not ratings:
            return None

        return sum(ratings) / len(ratings)

    def get_success_rate(self, agent_id: str) -> float:
        """Get success rate for an agent."""
        feedback_list = self.get_agent_feedback(agent_id)

        if not feedback_list:
            return 0.0

        successes = sum(
            1 for f in feedback_list
            if f.feedback_type in [
                FeedbackType.EXPLICIT_POSITIVE,
                FeedbackType.IMPLICIT_SUCCESS,
            ]
        )

        return successes / len(feedback_list)

    def get_learning_score(self, agent_id: str) -> float:
        """Get overall learning score for an agent (-1.0 to 1.0)."""
        feedback_list = self.get_agent_feedback(agent_id)

        if not feedback_list:
            return 0.0

        weighted_sum = sum(f.get_score() * f.weight for f in feedback_list)
        total_weight = sum(f.weight for f in feedback_list)

        if total_weight == 0:
            return 0.0

        return weighted_sum / total_weight

    def get_corrections(self, agent_id: str) -> List[Feedback]:
        """Get all corrections for an agent."""
        feedback_list = self.get_agent_feedback(agent_id)
        return [f for f in feedback_list if f.feedback_type == FeedbackType.CORRECTION]

    def register_callback(self, callback):
        """Register a callback for new feedback."""
        self._callbacks.append(callback)

    def get_stats(self) -> Dict[str, Any]:
        """Get feedback statistics."""
        total = len(self.feedback)

        by_type = {}
        for feedback_type in FeedbackType:
            count = sum(1 for f in self.feedback if f.feedback_type == feedback_type)
            by_type[feedback_type.value] = count

        return {
            "total_feedback": total,
            "by_type": by_type,
            "agents_tracked": len(self.agent_feedback),
            "task_types_tracked": len(self.task_type_feedback),
        }
