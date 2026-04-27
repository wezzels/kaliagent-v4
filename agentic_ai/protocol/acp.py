"""
ACP (Agent Communication Protocol)
===================================

Basic message types and bus for agent communication.
"""

from typing import Optional, Dict, Any, List
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
import uuid


class MessageType(str, Enum):
    """Message type enumeration."""
    REQUEST = "request"
    RESPONSE = "response"
    EVENT = "event"
    NOTIFICATION = "notification"
    ERROR = "error"


class Priority(str, Enum):
    """Message priority levels."""
    LOW = "low"
    NORMAL = "normal"
    HIGH = "high"
    URGENT = "urgent"


@dataclass
class ACPMessage:
    """Agent Communication Protocol message."""

    message_id: str = field(default_factory=lambda: str(uuid.uuid4())[:8])
    message_type: MessageType = MessageType.REQUEST
    priority: Priority = Priority.NORMAL

    sender: str = ""
    recipient: str = ""
    subject: str = ""
    body: Dict[str, Any] = field(default_factory=dict)

    created_at: str = field(default_factory=lambda: datetime.utcnow().isoformat())
    expires_at: Optional[str] = None
    correlation_id: Optional[str] = None

    delivered: bool = False
    delivered_at: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "message_id": self.message_id,
            "message_type": self.message_type.value,
            "priority": self.priority.value,
            "sender": self.sender,
            "recipient": self.recipient,
            "subject": self.subject,
            "body": self.body,
            "created_at": self.created_at,
            "expires_at": self.expires_at,
            "correlation_id": self.correlation_id,
            "delivered": self.delivered,
            "delivered_at": self.delivered_at,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'ACPMessage':
        """Create from dictionary."""
        msg = cls()
        msg.message_id = data.get("message_id", msg.message_id)
        msg.message_type = MessageType(data.get("message_type", "request"))
        msg.priority = Priority(data.get("priority", "normal"))
        msg.sender = data.get("sender", "")
        msg.recipient = data.get("recipient", "")
        msg.subject = data.get("subject", "")
        msg.body = data.get("body", {})
        msg.created_at = data.get("created_at", msg.created_at)
        msg.expires_at = data.get("expires_at")
        msg.correlation_id = data.get("correlation_id")
        msg.delivered = data.get("delivered", False)
        msg.delivered_at = data.get("delivered_at")
        return msg


class ACPBus:
    """Simple in-memory message bus for agent communication."""

    def __init__(self):
        self._messages: List[ACPMessage] = []
        self._subscribers: Dict[str, List] = {}

    def publish(self, message: ACPMessage):
        """Publish a message to the bus."""
        self._messages.append(message)

        topic = message.subject
        if topic in self._subscribers:
            for callback in self._subscribers[topic]:
                try:
                    callback(message)
                except Exception:
                    pass

    def subscribe(self, topic: str, callback):
        """Subscribe to a topic."""
        if topic not in self._subscribers:
            self._subscribers[topic] = []
        self._subscribers[topic].append(callback)

    def get_messages(self, sender: Optional[str] = None,
                     recipient: Optional[str] = None,
                     message_type: Optional[MessageType] = None) -> List[ACPMessage]:
        """Get messages with optional filters."""
        messages = self._messages

        if sender:
            messages = [m for m in messages if m.sender == sender]
        if recipient:
            messages = [m for m in messages if m.recipient == recipient]
        if message_type:
            messages = [m for m in messages if m.message_type == message_type]

        return messages

    def clear(self):
        """Clear all messages."""
        self._messages.clear()
