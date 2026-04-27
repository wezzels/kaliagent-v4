"""
Conversation State
==================

Tracks the state of a conversation thread.
"""

from typing import Optional, Dict, Any, List
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum


class ConversationStatus(str, Enum):
    """Status of a conversation."""
    ACTIVE = "active"
    PAUSED = "paused"
    COMPLETED = "completed"
    ARCHIVED = "archived"


@dataclass
class ConversationState:
    """State of a conversation thread."""

    thread_id: str
    title: str
    status: ConversationStatus = ConversationStatus.ACTIVE
    participants: List[str] = field(default_factory=list)
    messages: List[Dict[str, Any]] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
    created_at: str = field(default_factory=lambda: datetime.utcnow().isoformat())
    updated_at: Optional[str] = None
    completed_at: Optional[str] = None

    def add_message(self, message: Dict[str, Any]):
        """Add a message to the conversation."""
        self.messages.append(message)
        self.updated_at = datetime.utcnow().isoformat()

    def get_message_count(self) -> int:
        """Get total message count."""
        return len(self.messages)

    def get_participants(self) -> List[str]:
        """Get unique participants."""
        return list(set(self.participants))

    def add_participant(self, agent_id: str):
        """Add a participant to the conversation."""
        if agent_id not in self.participants:
            self.participants.append(agent_id)
            self.updated_at = datetime.utcnow().isoformat()

    def complete(self):
        """Mark conversation as completed."""
        self.status = ConversationStatus.COMPLETED
        self.completed_at = datetime.utcnow().isoformat()
        self.updated_at = datetime.utcnow().isoformat()

    def archive(self):
        """Archive the conversation."""
        self.status = ConversationStatus.ARCHIVED
        self.updated_at = datetime.utcnow().isoformat()

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "thread_id": self.thread_id,
            "title": self.title,
            "status": self.status.value,
            "participants": self.participants,
            "message_count": len(self.messages),
            "created_at": self.created_at,
            "updated_at": self.updated_at,
            "completed_at": self.completed_at,
            "metadata": self.metadata,
        }
