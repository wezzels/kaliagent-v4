"""
Presence & Activity Tracking
=============================

Track user presence, activity, and generate activity feeds.
"""

from typing import Dict, Any, List, Optional, Set, Callable
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
import uuid
import threading


class PresenceStatus(str, Enum):
    """User presence status."""
    ONLINE = "online"
    AWAY = "away"
    BUSY = "busy"
    DO_NOT_DISTURB = "do_not_disturb"
    OFFLINE = "offline"


class ActivityType(str, Enum):
    """Types of activities."""
    JOINED = "joined"
    LEFT = "left"
    EDITED = "edited"
    COMMENTED = "commented"
    VIEWED = "viewed"
    SHARED = "shared"
    DOWNLOADED = "downloaded"
    DELETED = "deleted"
    RENAMED = "renamed"
    ROLE_CHANGED = "role_changed"
    STATUS_CHANGED = "status_changed"


@dataclass
class PresenceInfo:
    """Current presence information for a user."""

    user_id: str = ""
    status: PresenceStatus = PresenceStatus.OFFLINE
    last_seen: str = field(default_factory=lambda: datetime.utcnow().isoformat())
    current_session: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)

    # Auto-away settings
    auto_away_minutes: int = 5
    auto_offline_minutes: int = 30

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "user_id": self.user_id,
            "status": self.status.value,
            "last_seen": self.last_seen,
            "current_session": self.current_session,
            "metadata": self.metadata,
        }

    def is_auto_away(self) -> bool:
        """Check if user should be auto-marked as away."""
        last = datetime.fromisoformat(self.last_seen)
        elapsed = datetime.utcnow() - last
        return elapsed > timedelta(minutes=self.auto_away_minutes)

    def is_auto_offline(self) -> bool:
        """Check if user should be auto-marked as offline."""
        last = datetime.fromisoformat(self.last_seen)
        elapsed = datetime.utcnow() - last
        return elapsed > timedelta(minutes=self.auto_offline_minutes)


@dataclass
class ActivityEvent:
    """An activity event in the feed."""

    event_id: str = field(default_factory=lambda: str(uuid.uuid4())[:8])
    event_type: ActivityType = ActivityType.VIEWED
    user_id: str = ""
    user_name: str = ""
    target_type: str = ""  # session, document, workspace, etc.
    target_id: str = ""
    target_name: str = ""
    timestamp: str = field(default_factory=lambda: datetime.utcnow().isoformat())
    metadata: Dict[str, Any] = field(default_factory=dict)
    visibility: str = "public"  # public, participants, private

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "event_id": self.event_id,
            "event_type": self.event_type.value,
            "user_id": self.user_id,
            "user_name": self.user_name,
            "target_type": self.target_type,
            "target_id": self.target_id,
            "target_name": self.target_name,
            "timestamp": self.timestamp,
            "metadata": self.metadata,
            "visibility": self.visibility,
        }


@dataclass
class TypingIndicator:
    """Typing indicator for a user."""

    user_id: str = ""
    target_type: str = ""  # session, document, channel
    target_id: str = ""
    is_typing: bool = False
    started_at: Optional[str] = None
    stopped_at: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "user_id": self.user_id,
            "target_type": self.target_type,
            "target_id": self.target_id,
            "is_typing": self.is_typing,
            "started_at": self.started_at,
            "stopped_at": self.stopped_at,
        }


class PresenceManager:
    """Manages user presence information."""

    def __init__(self, auto_away_minutes: int = 5,
                 auto_offline_minutes: int = 30):
        self._presence: Dict[str, PresenceInfo] = {}
        self._auto_away_minutes = auto_away_minutes
        self._auto_offline_minutes = auto_offline_minutes
        self._lock = threading.RLock()
        self._callbacks: List[Callable] = []

    def _emit_presence_change(self, user_id: str, old_status: PresenceStatus,
                             new_status: PresenceStatus):
        """Emit presence change event."""
        for callback in self._callbacks:
            try:
                callback({
                    "event_type": "presence_changed",
                    "user_id": user_id,
                    "old_status": old_status.value,
                    "new_status": new_status.value,
                    "timestamp": datetime.utcnow().isoformat(),
                })
            except Exception:
                pass

    def set_presence(self, user_id: str, status: PresenceStatus,
                    session_id: Optional[str] = None,
                    metadata: Optional[Dict] = None):
        """Set a user's presence status."""
        with self._lock:
            if user_id not in self._presence:
                self._presence[user_id] = PresenceInfo(
                    user_id=user_id,
                    auto_away_minutes=self._auto_away_minutes,
                    auto_offline_minutes=self._auto_offline_minutes,
                )

            presence = self._presence[user_id]
            old_status = presence.status

            presence.status = status
            presence.last_seen = datetime.utcnow().isoformat()

            if session_id:
                presence.current_session = session_id

            if metadata:
                presence.metadata.update(metadata)

            if old_status != status:
                self._emit_presence_change(user_id, old_status, status)

    def get_presence(self, user_id: str) -> Optional[PresenceInfo]:
        """Get a user's presence information."""
        with self._lock:
            return self._presence.get(user_id)

    def get_all_presence(self, status: Optional[PresenceStatus] = None) -> List[PresenceInfo]:
        """Get all presence info, optionally filtered by status."""
        with self._lock:
            presence_list = list(self._presence.values())

        if status:
            presence_list = [p for p in presence_list if p.status == status]

        return presence_list

    def get_online_users(self) -> List[PresenceInfo]:
        """Get all online users."""
        with self._lock:
            return [
                p for p in self._presence.values()
                if p.status in [PresenceStatus.ONLINE, PresenceStatus.AWAY, PresenceStatus.BUSY]
            ]

    def mark_active(self, user_id: str, session_id: Optional[str] = None):
        """Mark a user as active (updates last_seen and sets online)."""
        with self._lock:
            if user_id not in self._presence:
                self._presence[user_id] = PresenceInfo(
                    user_id=user_id,
                    auto_away_minutes=self._auto_away_minutes,
                    auto_offline_minutes=self._auto_offline_minutes,
                )

            presence = self._presence[user_id]
            old_status = presence.status

            presence.last_seen = datetime.utcnow().isoformat()

            if presence.status == PresenceStatus.OFFLINE:
                presence.status = PresenceStatus.ONLINE

            if session_id:
                presence.current_session = session_id

            if old_status != presence.status:
                self._emit_presence_change(user_id, old_status, presence.status)

    def set_offline(self, user_id: str):
        """Mark a user as offline."""
        with self._lock:
            if user_id in self._presence:
                presence = self._presence[user_id]
                old_status = presence.status

                presence.status = PresenceStatus.OFFLINE
                presence.current_session = None

                self._emit_presence_change(user_id, old_status, PresenceStatus.OFFLINE)

    def cleanup_inactive(self) -> int:
        """Auto-update presence for inactive users."""
        updated = 0

        with self._lock:
            for presence in self._presence.values():
                if presence.status == PresenceStatus.OFFLINE:
                    continue

                if presence.is_auto_offline():
                    old_status = presence.status
                    presence.status = PresenceStatus.OFFLINE
                    presence.current_session = None
                    self._emit_presence_change(presence.user_id, old_status, PresenceStatus.OFFLINE)
                    updated += 1
                elif presence.is_auto_away() and presence.status == PresenceStatus.ONLINE:
                    old_status = presence.status
                    presence.status = PresenceStatus.AWAY
                    self._emit_presence_change(presence.user_id, old_status, PresenceStatus.AWAY)
                    updated += 1

        return updated

    def register_callback(self, callback: Callable):
        """Register a callback for presence changes."""
        self._callbacks.append(callback)

    def get_state(self) -> Dict[str, Any]:
        """Get presence manager state."""
        with self._lock:
            return {
                "total_users": len(self._presence),
                "online": sum(1 for p in self._presence.values() if p.status == PresenceStatus.ONLINE),
                "away": sum(1 for p in self._presence.values() if p.status == PresenceStatus.AWAY),
                "busy": sum(1 for p in self._presence.values() if p.status == PresenceStatus.BUSY),
                "offline": sum(1 for p in self._presence.values() if p.status == PresenceStatus.OFFLINE),
            }


class ActivityFeed:
    """Activity feed for tracking user actions."""

    def __init__(self, max_events: int = 1000):
        self._events: List[ActivityEvent] = []
        self._max_events = max_events
        self._lock = threading.RLock()
        self._callbacks: List[Callable] = []

    def add_event(self, event_type: ActivityType, user_id: str,
                 target_type: str, target_id: str,
                 user_name: str = "", target_name: str = "",
                 metadata: Optional[Dict] = None,
                 visibility: str = "public") -> ActivityEvent:
        """Add an event to the activity feed."""
        event = ActivityEvent(
            event_type=event_type,
            user_id=user_id,
            user_name=user_name or f"User-{user_id[:4]}",
            target_type=target_type,
            target_id=target_id,
            target_name=target_name,
            metadata=metadata or {},
            visibility=visibility,
        )

        with self._lock:
            self._events.append(event)

            # Trim old events
            if len(self._events) > self._max_events:
                self._events = self._events[-self._max_events:]

        # Notify callbacks
        for callback in self._callbacks:
            try:
                callback(event.to_dict())
            except Exception:
                pass

        return event

    def get_events(self, limit: int = 50,
                  user_id: Optional[str] = None,
                  target_type: Optional[str] = None,
                  target_id: Optional[str] = None,
                  event_type: Optional[ActivityType] = None,
                  since: Optional[str] = None) -> List[ActivityEvent]:
        """Get events from the feed with optional filters."""
        with self._lock:
            events = self._events.copy()

        # Apply filters
        if user_id:
            events = [e for e in events if e.user_id == user_id]

        if target_type:
            events = [e for e in events if e.target_type == target_type]

        if target_id:
            events = [e for e in events if e.target_id == target_id]

        if event_type:
            events = [e for e in events if e.event_type == event_type]

        if since:
            events = [e for e in events if e.timestamp > since]

        # Sort by timestamp descending
        events.sort(key=lambda e: e.timestamp, reverse=True)

        return events[:limit]

    def get_user_activity(self, user_id: str, limit: int = 20) -> List[ActivityEvent]:
        """Get activity for a specific user."""
        return self.get_events(user_id=user_id, limit=limit)

    def get_target_activity(self, target_type: str, target_id: str,
                           limit: int = 20) -> List[ActivityEvent]:
        """Get activity for a specific target (e.g., session, document)."""
        return self.get_events(
            target_type=target_type,
            target_id=target_id,
            limit=limit,
        )

    def register_callback(self, callback: Callable):
        """Register a callback for new events."""
        self._callbacks.append(callback)

    def clear_old_events(self, older_than_hours: int = 24) -> int:
        """Clear events older than specified time."""
        cutoff = datetime.utcnow() - timedelta(hours=older_than_hours)

        with self._lock:
            original_count = len(self._events)
            self._events = [
                e for e in self._events
                if datetime.fromisoformat(e.timestamp) > cutoff
            ]
            return original_count - len(self._events)

    def get_state(self) -> Dict[str, Any]:
        """Get activity feed state."""
        with self._lock:
            return {
                "total_events": len(self._events),
                "max_events": self._max_events,
            }


class TypingManager:
    """Manages typing indicators."""

    def __init__(self, timeout_seconds: int = 5):
        self._typing: Dict[str, TypingIndicator] = {}  # key: user_id:target_type:target_id
        self._timeout_seconds = timeout_seconds
        self._lock = threading.RLock()
        self._callbacks: List[Callable] = []

    def _get_key(self, user_id: str, target_type: str, target_id: str) -> str:
        """Generate unique key for typing indicator."""
        return f"{user_id}:{target_type}:{target_id}"

    def start_typing(self, user_id: str, target_type: str, target_id: str):
        """Mark a user as typing."""
        key = self._get_key(user_id, target_type, target_id)

        with self._lock:
            indicator = TypingIndicator(
                user_id=user_id,
                target_type=target_type,
                target_id=target_id,
                is_typing=True,
                started_at=datetime.utcnow().isoformat(),
            )
            self._typing[key] = indicator

        # Notify callbacks
        self._emit_typing_change(indicator)

    def stop_typing(self, user_id: str, target_type: str, target_id: str):
        """Mark a user as stopped typing."""
        key = self._get_key(user_id, target_type, target_id)

        with self._lock:
            if key in self._typing:
                indicator = self._typing[key]
                indicator.is_typing = False
                indicator.stopped_at = datetime.utcnow().isoformat()
                del self._typing[key]

        # Notify callbacks
        self._emit_typing_change(indicator)

    def _emit_typing_change(self, indicator: TypingIndicator):
        """Emit typing change event."""
        for callback in self._callbacks:
            try:
                callback(indicator.to_dict())
            except Exception:
                pass

    def get_typing_users(self, target_type: str, target_id: str) -> List[str]:
        """Get list of users currently typing in a target."""
        with self._lock:
            return [
                ind.user_id for ind in self._typing.values()
                if ind.target_type == target_type
                and ind.target_id == target_id
                and ind.is_typing
            ]

    def cleanup_stale(self) -> int:
        """Clean up stale typing indicators (timeout)."""
        cutoff = datetime.utcnow() - timedelta(seconds=self._timeout_seconds)

        with self._lock:
            to_remove = []
            for key, indicator in self._typing.items():
                if indicator.started_at:
                    started = datetime.fromisoformat(indicator.started_at)
                    if started < cutoff:
                        to_remove.append(key)

            for key in to_remove:
                indicator = self._typing[key]
                indicator.is_typing = False
                del self._typing[key]
                self._emit_typing_change(indicator)

        return len(to_remove)

    def register_callback(self, callback: Callable):
        """Register a callback for typing changes."""
        self._callbacks.append(callback)


class CollaborationHub:
    """Central hub for presence, activity, and typing."""

    def __init__(self):
        self.presence = PresenceManager()
        self.activity = ActivityFeed()
        self.typing = TypingManager()

        # Link presence to activity
        def on_presence_change(event):
            if event["event_type"] == "presence_changed":
                self.activity.add_event(
                    event_type=ActivityType.STATUS_CHANGED,
                    user_id=event["user_id"],
                    target_type="user",
                    target_id=event["user_id"],
                    metadata={
                        "old_status": event["old_status"],
                        "new_status": event["new_status"],
                    },
                    visibility="participants",
                )

        self.presence.register_callback(on_presence_change)

    def get_state(self) -> Dict[str, Any]:
        """Get hub state."""
        return {
            "presence": self.presence.get_state(),
            "activity": self.activity.get_state(),
            "typing": {
                "active_typists": len(self.typing._typing),
            },
        }
