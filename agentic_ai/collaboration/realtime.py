"""
Real-Time Collaboration System
===============================

WebSocket-based real-time updates and operational transformation
for collaborative editing.
"""

from typing import Dict, Any, List, Optional, Set, Callable
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
import uuid
import threading
import json


class OperationType(str, Enum):
    """Types of operations."""
    INSERT = "insert"
    DELETE = "delete"
    UPDATE = "update"
    MOVE = "move"


class ConnectionStatus(str, Enum):
    """Connection status."""
    CONNECTING = "connecting"
    CONNECTED = "connected"
    DISCONNECTED = "disconnected"
    RECONNECTING = "reconnecting"


@dataclass
class Operation:
    """An operation for operational transformation."""

    operation_id: str = field(default_factory=lambda: str(uuid.uuid4())[:8])
    operation_type: OperationType = OperationType.UPDATE
    document_id: str = ""
    user_id: str = ""

    # Operation data
    position: Optional[int] = None
    content: Optional[str] = None
    length: int = 0
    path: List[str] = field(default_factory=list)  # For nested structures

    # Metadata
    timestamp: str = field(default_factory=lambda: datetime.utcnow().isoformat())
    version: int = 0
    parent_operation: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "operation_id": self.operation_id,
            "operation_type": self.operation_type.value,
            "document_id": self.document_id,
            "user_id": self.user_id,
            "position": self.position,
            "content": self.content,
            "length": self.length,
            "path": self.path,
            "timestamp": self.timestamp,
            "version": self.version,
            "parent_operation": self.parent_operation,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Operation':
        """Create from dictionary."""
        return cls(
            operation_id=data.get("operation_id"),
            operation_type=OperationType(data.get("operation_type", "update")),
            document_id=data.get("document_id", ""),
            user_id=data.get("user_id", ""),
            position=data.get("position"),
            content=data.get("content"),
            length=data.get("length", 0),
            path=data.get("path", []),
            timestamp=data.get("timestamp"),
            version=data.get("version", 0),
            parent_operation=data.get("parent_operation"),
        )


@dataclass
class CursorPosition:
    """Cursor position for a user."""

    user_id: str = ""
    document_id: str = ""
    position: int = 0
    selection_start: Optional[int] = None
    selection_end: Optional[int] = None
    timestamp: str = field(default_factory=lambda: datetime.utcnow().isoformat())

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "user_id": self.user_id,
            "document_id": self.document_id,
            "position": self.position,
            "selection_start": self.selection_start,
            "selection_end": self.selection_end,
            "timestamp": self.timestamp,
        }


@dataclass
class ActiveUser:
    """Currently active user in a session."""

    user_id: str = ""
    name: str = ""
    status: ConnectionStatus = ConnectionStatus.CONNECTED
    cursors: Dict[str, CursorPosition] = field(default_factory=dict)  # document_id -> cursor
    last_activity: str = field(default_factory=lambda: datetime.utcnow().isoformat())
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "user_id": self.user_id,
            "name": self.name,
            "status": self.status.value,
            "cursors": {k: v.to_dict() for k, v in self.cursors.items()},
            "last_activity": self.last_activity,
            "metadata": self.metadata,
        }


class OperationalTransformer:
    """Handles operational transformation for conflict resolution."""

    def __init__(self):
        self._buffer: Dict[str, List[Operation]] = {}  # document_id -> operations

    def transform(self, op1: Operation, op2: Operation) -> tuple[Operation, Operation]:
        """
        Transform two concurrent operations.

        Returns transformed (op1', op2') such that:
        apply(apply(doc, op1), op2') == apply(apply(doc, op2), op1')
        """
        if op1.document_id != op2.document_id:
            return op1, op2

        # Create copies to avoid mutating originals
        op1_prime = self._copy_operation(op1)
        op2_prime = self._copy_operation(op2)

        # Transform based on operation types
        if op1.operation_type == OperationType.INSERT and op2.operation_type == OperationType.INSERT:
            op1_prime, op2_prime = self._transform_insert_insert(op1_prime, op2_prime)
        elif op1.operation_type == OperationType.INSERT and op2.operation_type == OperationType.DELETE:
            op1_prime, op2_prime = self._transform_insert_delete(op1_prime, op2_prime)
        elif op1.operation_type == OperationType.DELETE and op2.operation_type == OperationType.INSERT:
            op1_prime, op2_prime = self._transform_delete_insert(op1_prime, op2_prime)
        elif op1.operation_type == OperationType.DELETE and op2.operation_type == OperationType.DELETE:
            op1_prime, op2_prime = self._transform_delete_delete(op1_prime, op2_prime)

        return op1_prime, op2_prime

    def _copy_operation(self, op: Operation) -> Operation:
        """Create a copy of an operation."""
        return Operation(
            operation_id=op.operation_id,
            operation_type=op.operation_type,
            document_id=op.document_id,
            user_id=op.user_id,
            position=op.position,
            content=op.content,
            length=op.length,
            path=op.path.copy(),
            timestamp=op.timestamp,
            version=op.version,
            parent_operation=op.parent_operation,
        )

    def _transform_insert_insert(self, op1: Operation, op2: Operation) -> tuple[Operation, Operation]:
        """Transform two insert operations."""
        if op1.position is not None and op2.position is not None:
            if op1.position <= op2.position:
                op2_prime = self._copy_operation(op2)
                op2_prime.position = op2.position + len(op1.content or "")
                return op1, op2_prime
            else:
                op1_prime = self._copy_operation(op1)
                op1_prime.position = op1.position + len(op2.content or "")
                return op1_prime, op2
        return op1, op2

    def _transform_insert_delete(self, insert_op: Operation, delete_op: Operation) -> tuple[Operation, Operation]:
        """Transform insert and delete operations."""
        if insert_op.position is not None and delete_op.position is not None:
            # Insert happens before delete
            if insert_op.position < delete_op.position:
                delete_op_prime = self._copy_operation(delete_op)
                delete_op_prime.position = delete_op.position + len(insert_op.content or "")
                return insert_op, delete_op_prime
            # Insert happens after delete
            elif insert_op.position >= delete_op.position + delete_op.length:
                insert_op_prime = self._copy_operation(insert_op)
                insert_op_prime.position = insert_op.position - delete_op.length
                return insert_op_prime, delete_op
            # Insert is within delete range
            else:
                insert_op_prime = self._copy_operation(insert_op)
                insert_op_prime.position = delete_op.position
                return insert_op_prime, delete_op
        return insert_op, delete_op

    def _transform_delete_insert(self, delete_op: Operation, insert_op: Operation) -> tuple[Operation, Operation]:
        """Transform delete and insert operations."""
        insert_prime, delete_prime = self._transform_insert_delete(insert_op, delete_op)
        return delete_prime, insert_prime

    def _transform_delete_delete(self, op1: Operation, op2: Operation) -> tuple[Operation, Operation]:
        """Transform two delete operations."""
        if op1.position is not None and op2.position is not None:
            # Non-overlapping deletes
            if op1.position + op1.length <= op2.position:
                op2_prime = self._copy_operation(op2)
                op2_prime.position = op2.position - op1.length
                return op1, op2_prime
            elif op2.position + op2.length <= op1.position:
                op1_prime = self._copy_operation(op1)
                op1_prime.position = op1.position - op2.length
                return op1_prime, op2
            # Overlapping deletes - more complex logic needed
            else:
                # Simplified: adjust positions
                if op1.position < op2.position:
                    op2_prime = self._copy_operation(op2)
                    op2_prime.position = op1.position
                    op2_prime.length = max(0, op2.length - op1.length)
                    return op1, op2_prime
                else:
                    op1_prime = self._copy_operation(op1)
                    op1_prime.position = op2.position
                    op1_prime.length = max(0, op1.length - op2.length)
                    return op1_prime, op2
        return op1, op2

    def apply_operation(self, document: str, operation: Operation) -> str:
        """Apply an operation to a document."""
        if operation.operation_type == OperationType.INSERT:
            if operation.position is not None:
                pos = min(operation.position, len(document))
                return document[:pos] + (operation.content or "") + document[pos:]

        elif operation.operation_type == OperationType.DELETE:
            if operation.position is not None:
                pos = min(operation.position, len(document))
                end = min(pos + operation.length, len(document))
                return document[:pos] + document[end:]

        elif operation.operation_type == OperationType.UPDATE:
            if operation.content is not None:
                return operation.content

        return document


class PubSubChannel:
    """Publish-subscribe channel for real-time events."""

    def __init__(self, channel_id: str):
        self.channel_id = channel_id
        self._subscribers: Dict[str, Callable] = {}  # subscriber_id -> callback
        self._lock = threading.Lock()

    def subscribe(self, subscriber_id: str, callback: Callable) -> bool:
        """Subscribe to channel events."""
        with self._lock:
            self._subscribers[subscriber_id] = callback
        return True

    def unsubscribe(self, subscriber_id: str) -> bool:
        """Unsubscribe from channel."""
        with self._lock:
            if subscriber_id in self._subscribers:
                del self._subscribers[subscriber_id]
                return True
        return False

    def publish(self, event: Dict[str, Any], exclude: Optional[Set[str]] = None):
        """Publish an event to all subscribers."""
        with self._lock:
            for subscriber_id, callback in self._subscribers.items():
                if exclude and subscriber_id in exclude:
                    continue
                try:
                    callback(event)
                except Exception:
                    pass  # Ignore callback errors

    def get_subscriber_count(self) -> int:
        """Get number of subscribers."""
        with self._lock:
            return len(self._subscribers)


class RealTimeCollaboration:
    """Real-time collaboration manager."""

    def __init__(self):
        self._users: Dict[str, ActiveUser] = {}
        self._channels: Dict[str, PubSubChannel] = {}
        self._transformer = OperationalTransformer()
        self._pending_ops: Dict[str, List[Operation]] = {}  # document_id -> pending ops
        self._document_versions: Dict[str, int] = {}  # document_id -> version
        self._lock = threading.RLock()

    def _get_or_create_channel(self, document_id: str) -> PubSubChannel:
        """Get or create a channel for a document."""
        if document_id not in self._channels:
            self._channels[document_id] = PubSubChannel(document_id)
        return self._channels[document_id]

    def connect_user(self, user_id: str, name: str = "") -> ActiveUser:
        """Connect a user to the collaboration system."""
        with self._lock:
            user = ActiveUser(
                user_id=user_id,
                name=name or f"User-{user_id[:4]}",
                status=ConnectionStatus.CONNECTED,
            )
            self._users[user_id] = user
        return user

    def disconnect_user(self, user_id: str):
        """Disconnect a user."""
        with self._lock:
            if user_id in self._users:
                user = self._users[user_id]
                user.status = ConnectionStatus.DISCONNECTED
                user.cursors.clear()

    def get_active_users(self, document_id: Optional[str] = None) -> List[ActiveUser]:
        """Get active users, optionally filtered by document."""
        with self._lock:
            users = [
                u for u in self._users.values()
                if u.status == ConnectionStatus.CONNECTED
            ]

        if document_id:
            users = [
                u for u in users
                if document_id in u.cursors
            ]

        return users

    def update_cursor(self, user_id: str, document_id: str,
                     position: int, selection_start: Optional[int] = None,
                     selection_end: Optional[int] = None):
        """Update a user's cursor position."""
        with self._lock:
            if user_id not in self._users:
                return

            user = self._users[user_id]
            cursor = CursorPosition(
                user_id=user_id,
                document_id=document_id,
                position=position,
                selection_start=selection_start,
                selection_end=selection_end,
            )
            user.cursors[document_id] = cursor
            user.last_activity = datetime.utcnow().isoformat()

        # Broadcast cursor update
        channel = self._get_or_create_channel(document_id)
        channel.publish({
            "event_type": "cursor_update",
            "user_id": user_id,
            "cursor": cursor.to_dict(),
        }, exclude={user_id})

    def submit_operation(self, operation: Operation) -> Operation:
        """Submit an operation for transformation and broadcast."""
        with self._lock:
            document_id = operation.document_id

            # Get current version
            current_version = self._document_versions.get(document_id, 0)
            operation.version = current_version + 1

            # Transform against pending operations
            if document_id in self._pending_ops:
                for pending_op in self._pending_ops[document_id]:
                    operation, _ = self._transformer.transform(operation, pending_op)

            # Store operation
            if document_id not in self._pending_ops:
                self._pending_ops[document_id] = []
            self._pending_ops[document_id].append(operation)

            # Update version
            self._document_versions[document_id] = operation.version

        # Broadcast operation
        channel = self._get_or_create_channel(document_id)
        channel.publish({
            "event_type": "operation",
            "operation": operation.to_dict(),
        }, exclude={operation.user_id})

        return operation

    def apply_operations(self, document: str, operations: List[Operation]) -> str:
        """Apply a list of operations to a document."""
        result = document
        for op in operations:
            result = self._transformer.apply_operation(result, op)
        return result

    def subscribe(self, document_id: str, subscriber_id: str,
                 callback: Callable) -> bool:
        """Subscribe to document events."""
        channel = self._get_or_create_channel(document_id)
        return channel.subscribe(subscriber_id, callback)

    def unsubscribe(self, document_id: str, subscriber_id: str) -> bool:
        """Unsubscribe from document events."""
        if document_id in self._channels:
            return self._channels[document_id].unsubscribe(subscriber_id)
        return False

    def get_document_state(self, document_id: str) -> Dict[str, Any]:
        """Get current state of a document."""
        with self._lock:
            return {
                "document_id": document_id,
                "version": self._document_versions.get(document_id, 0),
                "pending_ops": len(self._pending_ops.get(document_id, [])),
                "active_users": len([
                    u for u in self._users.values()
                    if document_id in u.cursors
                ]),
                "subscribers": self._channels.get(document_id, PubSubChannel(document_id)).get_subscriber_count(),
            }

    def cleanup_inactive(self, inactive_minutes: int = 30):
        """Clean up inactive users and operations."""
        cutoff = datetime.utcnow() - timedelta(minutes=inactive_minutes)

        with self._lock:
            # Remove inactive users
            to_remove = []
            for user_id, user in self._users.items():
                if user.status != ConnectionStatus.DISCONNECTED:
                    last_activity = datetime.fromisoformat(user.last_activity)
                    if last_activity < cutoff:
                        user.status = ConnectionStatus.DISCONNECTED
                        to_remove.append(user_id)

            for user_id in to_remove:
                del self._users[user_id]

            # Clear old pending operations (keep last 100 per document)
            for document_id in list(self._pending_ops.keys()):
                ops = self._pending_ops[document_id]
                if len(ops) > 100:
                    self._pending_ops[document_id] = ops[-100:]

        return len(to_remove)

    def get_state(self) -> Dict[str, Any]:
        """Get real-time collaboration state."""
        with self._lock:
            return {
                "total_users": len(self._users),
                "connected_users": sum(1 for u in self._users.values() if u.status == ConnectionStatus.CONNECTED),
                "active_documents": len(self._document_versions),
                "total_channels": len(self._channels),
                "pending_operations": sum(len(ops) for ops in self._pending_ops.values()),
            }


# Import timedelta
from datetime import timedelta
