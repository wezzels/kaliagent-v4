"""
Shared Workspace System
========================

Enables multiple agents and humans to collaborate in shared workspaces.
"""

from typing import Dict, Any, List, Optional, Set
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
import uuid
import threading
from copy import deepcopy


class LockType(str, Enum):
    """Types of resource locks."""
    READ = "read"
    WRITE = "write"
    EXCLUSIVE = "exclusive"


@dataclass
class ResourceLock:
    """Lock on a workspace resource."""

    lock_id: str = field(default_factory=lambda: str(uuid.uuid4())[:8])
    resource_id: str = ""
    holder_id: str = ""  # Agent or human ID
    lock_type: LockType = LockType.WRITE
    acquired_at: str = field(default_factory=lambda: datetime.utcnow().isoformat())
    expires_at: Optional[str] = None
    purpose: str = ""

    def is_expired(self) -> bool:
        """Check if lock has expired."""
        if not self.expires_at:
            return False
        return datetime.fromisoformat(self.expires_at) < datetime.utcnow()

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "lock_id": self.lock_id,
            "resource_id": self.resource_id,
            "holder_id": self.holder_id,
            "lock_type": self.lock_type.value,
            "acquired_at": self.acquired_at,
            "expires_at": self.expires_at,
            "purpose": self.purpose,
        }


@dataclass
class ChangeRecord:
    """Record of a change to workspace state."""

    change_id: str = field(default_factory=lambda: str(uuid.uuid4())[:8])
    workspace_id: str = ""
    resource_id: str = ""
    changer_id: str = ""
    change_type: str = ""  # create, update, delete
    old_value: Optional[Any] = None
    new_value: Optional[Any] = None
    timestamp: str = field(default_factory=lambda: datetime.utcnow().isoformat())
    metadata: Dict[str, str] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "change_id": self.change_id,
            "workspace_id": self.workspace_id,
            "resource_id": self.resource_id,
            "changer_id": self.changer_id,
            "change_type": self.change_type,
            "old_value": self.old_value,
            "new_value": self.new_value,
            "timestamp": self.timestamp,
            "metadata": self.metadata,
        }


@dataclass
class WorkspaceResource:
    """A resource within a workspace."""

    resource_id: str = field(default_factory=lambda: str(uuid.uuid4())[:8])
    name: str = ""
    resource_type: str = ""  # document, file, data, etc.
    content: Any = None
    metadata: Dict[str, Any] = field(default_factory=dict)

    created_at: str = field(default_factory=lambda: datetime.utcnow().isoformat())
    updated_at: str = field(default_factory=lambda: datetime.utcnow().isoformat())
    created_by: str = ""

    # Version tracking
    version: int = 0

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "resource_id": self.resource_id,
            "name": self.name,
            "resource_type": self.resource_type,
            "content": self.content,
            "metadata": self.metadata,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
            "created_by": self.created_by,
            "version": self.version,
        }


class Workspace:
    """Shared workspace for collaborative work."""

    def __init__(self, workspace_id: Optional[str] = None, name: str = ""):
        self.workspace_id = workspace_id or str(uuid.uuid4())[:8]
        self.name = name
        self.description: str = ""

        # Resources
        self._resources: Dict[str, WorkspaceResource] = {}
        self._locks: Dict[str, ResourceLock] = {}  # resource_id -> lock
        self._lock_history: List[ResourceLock] = []

        # Change tracking
        self._change_log: List[ChangeRecord] = []
        self._max_history = 1000

        # Participants
        self._participants: Set[str] = set()
        self._owners: Set[str] = set()

        # Thread safety
        self._lock = threading.RLock()

        # Events
        self._event_callbacks: List[callable] = []

    def _emit_event(self, event_type: str, data: Dict[str, Any]):
        """Emit a workspace event."""
        event = {
            "event_type": event_type,
            "workspace_id": self.workspace_id,
            "timestamp": datetime.utcnow().isoformat(),
            "data": data,
        }

        for callback in self._event_callbacks:
            try:
                callback(event)
            except Exception:
                pass

    def add_participant(self, participant_id: str, is_owner: bool = False):
        """Add a participant to the workspace."""
        with self._lock:
            self._participants.add(participant_id)
            if is_owner:
                self._owners.add(participant_id)

        self._emit_event("participant_joined", {
            "participant_id": participant_id,
            "is_owner": is_owner,
        })

    def remove_participant(self, participant_id: str):
        """Remove a participant from the workspace."""
        with self._lock:
            self._participants.discard(participant_id)
            self._owners.discard(participant_id)

            # Release any locks held by this participant
            to_release = [
                rid for rid, lock in self._locks.items()
                if lock.holder_id == participant_id
            ]
            for rid in to_release:
                self._release_lock_internal(rid)

        self._emit_event("participant_left", {
            "participant_id": participant_id,
        })

    def get_participants(self) -> Set[str]:
        """Get all participant IDs."""
        with self._lock:
            return self._participants.copy()

    def get_owners(self) -> Set[str]:
        """Get owner participant IDs."""
        with self._lock:
            return self._owners.copy()

    def create_resource(self, name: str, resource_type: str,
                       content: Any = None, creator_id: str = "") -> WorkspaceResource:
        """Create a new resource in the workspace."""
        resource = WorkspaceResource(
            name=name,
            resource_type=resource_type,
            content=content,
            created_by=creator_id,
        )

        with self._lock:
            self._resources[resource.resource_id] = resource

            # Record change
            self._record_change(ChangeRecord(
                workspace_id=self.workspace_id,
                resource_id=resource.resource_id,
                changer_id=creator_id,
                change_type="create",
                new_value=resource.to_dict(),
            ))

        self._emit_event("resource_created", {
            "resource_id": resource.resource_id,
            "name": name,
            "creator_id": creator_id,
        })

        return resource

    def get_resource(self, resource_id: str) -> Optional[WorkspaceResource]:
        """Get a resource by ID."""
        with self._lock:
            return self._resources.get(resource_id)

    def list_resources(self, resource_type: Optional[str] = None) -> List[WorkspaceResource]:
        """List resources, optionally filtered by type."""
        with self._lock:
            resources = list(self._resources.values())

        if resource_type:
            resources = [r for r in resources if r.resource_type == resource_type]

        return resources

    def update_resource(self, resource_id: str, content: Any,
                       updater_id: str = "", metadata: Optional[Dict] = None) -> bool:
        """Update a resource's content."""
        with self._lock:
            resource = self._resources.get(resource_id)
            if not resource:
                return False

            # Check lock
            if not self._can_modify(resource_id, updater_id):
                return False

            old_value = resource.to_dict()

            # Update resource
            resource.content = content
            resource.updated_at = datetime.utcnow().isoformat()
            resource.version += 1

            if metadata:
                resource.metadata.update(metadata)

            # Record change
            self._record_change(ChangeRecord(
                workspace_id=self.workspace_id,
                resource_id=resource_id,
                changer_id=updater_id,
                change_type="update",
                old_value=old_value,
                new_value=resource.to_dict(),
            ))

        self._emit_event("resource_updated", {
            "resource_id": resource_id,
            "updater_id": updater_id,
            "version": resource.version,
        })

        return True

    def delete_resource(self, resource_id: str, deleter_id: str = "") -> bool:
        """Delete a resource."""
        with self._lock:
            if resource_id not in self._resources:
                return False

            # Check lock
            if not self._can_modify(resource_id, deleter_id):
                return False

            old_value = self._resources[resource_id].to_dict()
            del self._resources[resource_id]

            # Release any lock
            self._release_lock_internal(resource_id)

            # Record change
            self._record_change(ChangeRecord(
                workspace_id=self.workspace_id,
                resource_id=resource_id,
                changer_id=deleter_id,
                change_type="delete",
                old_value=old_value,
            ))

        self._emit_event("resource_deleted", {
            "resource_id": resource_id,
            "deleter_id": deleter_id,
        })

        return True

    def acquire_lock(self, resource_id: str, holder_id: str,
                    lock_type: LockType = LockType.WRITE,
                    duration_minutes: int = 30,
                    purpose: str = "") -> Optional[ResourceLock]:
        """Acquire a lock on a resource."""
        with self._lock:
            # Check if resource exists
            if resource_id not in self._resources:
                return None

            # Check existing lock
            existing = self._locks.get(resource_id)
            if existing and not existing.is_expired():
                # Check lock compatibility
                if not self._locks_compatible(existing, lock_type):
                    return None

            # Create new lock
            lock = ResourceLock(
                resource_id=resource_id,
                holder_id=holder_id,
                lock_type=lock_type,
                purpose=purpose,
                expires_at=(
                    datetime.utcnow() + timedelta(minutes=duration_minutes)
                ).isoformat() if duration_minutes else None,
            )

            self._locks[resource_id] = lock
            self._lock_history.append(lock)

        self._emit_event("lock_acquired", {
            "resource_id": resource_id,
            "holder_id": holder_id,
            "lock_type": lock_type.value,
        })

        return lock

    def release_lock(self, resource_id: str, holder_id: str) -> bool:
        """Release a lock."""
        with self._lock:
            return self._release_lock_internal(resource_id, holder_id)

    def _release_lock_internal(self, resource_id: str,
                               holder_id: Optional[str] = None) -> bool:
        """Internal lock release (must be called with lock held)."""
        lock = self._locks.get(resource_id)
        if not lock:
            return False

        if holder_id and lock.holder_id != holder_id:
            return False

        del self._locks[resource_id]

        self._emit_event("lock_released", {
            "resource_id": resource_id,
            "holder_id": lock.holder_id,
        })

        return True

    def get_lock(self, resource_id: str) -> Optional[ResourceLock]:
        """Get current lock on a resource."""
        with self._lock:
            lock = self._locks.get(resource_id)
            if lock and lock.is_expired():
                del self._locks[resource_id]
                return None
            return lock

    def get_change_log(self, limit: int = 100,
                      resource_id: Optional[str] = None) -> List[ChangeRecord]:
        """Get change history."""
        with self._lock:
            changes = self._change_log.copy()

        if resource_id:
            changes = [c for c in changes if c.resource_id == resource_id]

        # Sort by timestamp descending
        changes.sort(key=lambda c: c.timestamp, reverse=True)

        return changes[:limit]

    def _record_change(self, change: ChangeRecord):
        """Record a change (must be called with lock held)."""
        self._change_log.append(change)

        # Trim history
        if len(self._change_log) > self._max_history:
            self._change_log = self._change_log[-self._max_history:]

    def _can_modify(self, resource_id: str, participant_id: str) -> bool:
        """Check if participant can modify resource (must be called with lock held)."""
        # Owners can always modify
        if participant_id in self._owners:
            return True

        # Check lock
        lock = self._locks.get(resource_id)
        if lock:
            if lock.is_expired():
                del self._locks[resource_id]
                return True
            return lock.holder_id == participant_id

        # No lock, any participant can modify
        return participant_id in self._participants

    def _locks_compatible(self, existing: ResourceLock,
                         new_type: LockType) -> bool:
        """Check if locks are compatible (must be called with lock held)."""
        # Read locks are compatible with each other
        if existing.lock_type == LockType.READ and new_type == LockType.READ:
            return True

        # Exclusive locks are never compatible
        if existing.lock_type == LockType.EXCLUSIVE or new_type == LockType.EXCLUSIVE:
            return False

        # Write locks conflict with everything
        return False

    def register_event_callback(self, callback: callable):
        """Register a callback for workspace events."""
        self._event_callbacks.append(callback)

    def get_state(self) -> Dict[str, Any]:
        """Get workspace state summary."""
        with self._lock:
            return {
                "workspace_id": self.workspace_id,
                "name": self.name,
                "description": self.description,
                "participant_count": len(self._participants),
                "owner_count": len(self._owners),
                "resource_count": len(self._resources),
                "active_locks": sum(1 for l in self._locks.values() if not l.is_expired()),
                "change_count": len(self._change_log),
            }

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        with self._lock:
            return {
                "workspace_id": self.workspace_id,
                "name": self.name,
                "description": self.description,
                "resources": [r.to_dict() for r in self._resources.values()],
                "participants": list(self._participants),
                "owners": list(self._owners),
                "locks": [l.to_dict() for l in self._locks.values() if not l.is_expired()],
                "recent_changes": [c.to_dict() for c in self._change_log[-10:]],
            }
