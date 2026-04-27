"""
Conversation Thread
===================

Manages a single conversation thread between agents.
"""

from typing import Optional, Dict, Any, List
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
import uuid


class MessageType(str, Enum):
    """Types of conversation messages."""
    MESSAGE = "message"
    QUESTION = "question"
    RESPONSE = "response"
    PROPOSAL = "proposal"
    VOTE = "vote"
    DECISION = "decision"
    NOTIFICATION = "notification"


@dataclass
class ConversationMessage:
    """A single message in a conversation."""

    id: str = field(default_factory=lambda: str(uuid.uuid4())[:8])
    thread_id: str = ""
    sender: str = ""
    recipient: Optional[str] = None  # None for broadcast
    type: MessageType = MessageType.MESSAGE
    content: str = ""
    metadata: Dict[str, Any] = field(default_factory=dict)
    in_reply_to: Optional[str] = None  # ID of parent message
    created_at: str = field(default_factory=lambda: datetime.utcnow().isoformat())

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "id": self.id,
            "thread_id": self.thread_id,
            "sender": self.sender,
            "recipient": self.recipient,
            "type": self.type.value,
            "content": self.content,
            "metadata": self.metadata,
            "in_reply_to": self.in_reply_to,
            "created_at": self.created_at,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "ConversationMessage":
        """Create from dictionary."""
        return cls(
            id=data.get("id", str(uuid.uuid4())[:8]),
            thread_id=data.get("thread_id", ""),
            sender=data.get("sender", ""),
            recipient=data.get("recipient"),
            type=MessageType(data.get("type", "message")),
            content=data.get("content", ""),
            metadata=data.get("metadata", {}),
            in_reply_to=data.get("in_reply_to"),
            created_at=data.get("created_at", datetime.utcnow().isoformat()),
        )


class MessageThread:
    """Manages a conversation thread."""

    def __init__(self, thread_id: str, title: str, creator: str):
        self.thread_id = thread_id
        self.title = title
        self.creator = creator
        self.messages: List[ConversationMessage] = []
        self.participants: set = {creator}
        self.created_at = datetime.utcnow().isoformat()
        self.updated_at = self.created_at
        self.is_active = True

    def add_message(
        self,
        sender: str,
        content: str,
        type: MessageType = MessageType.MESSAGE,
        recipient: Optional[str] = None,
        in_reply_to: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> ConversationMessage:
        """Add a message to the thread."""
        message = ConversationMessage(
            thread_id=self.thread_id,
            sender=sender,
            recipient=recipient,
            type=type,
            content=content,
            metadata=metadata or {},
            in_reply_to=in_reply_to,
        )

        self.messages.append(message)
        self.participants.add(sender)
        if recipient:
            self.participants.add(recipient)

        self.updated_at = datetime.utcnow().isoformat()

        return message

    def get_messages(self, limit: Optional[int] = None) -> List[ConversationMessage]:
        """Get messages, optionally limited."""
        if limit:
            return self.messages[-limit:]
        return self.messages

    def get_message_by_id(self, message_id: str) -> Optional[ConversationMessage]:
        """Get a specific message by ID."""
        for msg in self.messages:
            if msg.id == message_id:
                return msg
        return None

    def get_replies(self, message_id: str) -> List[ConversationMessage]:
        """Get all replies to a message."""
        return [msg for msg in self.messages if msg.in_reply_to == message_id]

    def get_participants(self) -> List[str]:
        """Get all participants."""
        return list(self.participants)

    def close(self):
        """Close the thread."""
        self.is_active = False
        self.updated_at = datetime.utcnow().isoformat()

    def get_summary(self) -> Dict[str, Any]:
        """Get thread summary."""
        return {
            "thread_id": self.thread_id,
            "title": self.title,
            "creator": self.creator,
            "message_count": len(self.messages),
            "participant_count": len(self.participants),
            "participants": list(self.participants),
            "is_active": self.is_active,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
        }
