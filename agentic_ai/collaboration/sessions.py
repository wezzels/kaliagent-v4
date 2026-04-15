"""
Collaboration Session Management
=================================

Manages collaborative sessions with multiple participants.
"""

from typing import Dict, Any, List, Optional, Set, Callable
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
import uuid
import threading
import json


class SessionStatus(str, Enum):
    """Session status."""
    INITIALIZING = "initializing"
    ACTIVE = "active"
    PAUSED = "paused"
    ENDING = "ending"
    ENDED = "ended"


class ParticipantRole(str, Enum):
    """Participant roles in a session."""
    HOST = "host"  # Full control, can end session
    COHOST = "cohost"  # Can manage participants
    EDITOR = "editor"  # Can edit content
    VIEWER = "viewer"  # Read-only
    OBSERVER = "observer"  # Can observe but not interact


@dataclass
class Participant:
    """Participant in a collaboration session."""
    
    participant_id: str = field(default_factory=lambda: str(uuid.uuid4())[:8])
    user_id: str = ""
    name: str = ""
    role: ParticipantRole = ParticipantRole.VIEWER
    joined_at: str = field(default_factory=lambda: datetime.utcnow().isoformat())
    left_at: Optional[str] = None
    is_active: bool = True
    
    # Capabilities based on role
    can_edit: bool = False
    can_invite: bool = False
    can_moderate: bool = False
    
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def __post_init__(self):
        """Set capabilities based on role."""
        if self.role in [ParticipantRole.HOST, ParticipantRole.COHOST, ParticipantRole.EDITOR]:
            self.can_edit = True
        if self.role in [ParticipantRole.HOST, ParticipantRole.COHOST]:
            self.can_invite = True
            self.can_moderate = True
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "participant_id": self.participant_id,
            "user_id": self.user_id,
            "name": self.name,
            "role": self.role.value,
            "joined_at": self.joined_at,
            "left_at": self.left_at,
            "is_active": self.is_active,
            "can_edit": self.can_edit,
            "can_invite": self.can_invite,
            "can_moderate": self.can_moderate,
            "metadata": self.metadata,
        }


@dataclass
class SessionEvent:
    """Event in a session lifecycle."""
    
    event_id: str = field(default_factory=lambda: str(uuid.uuid4())[:8])
    session_id: str = ""
    event_type: str = ""  # participant_joined, participant_left, role_changed, etc.
    actor_id: str = ""  # Who triggered the event
    target_id: str = ""  # Who/what the event affects
    timestamp: str = field(default_factory=lambda: datetime.utcnow().isoformat())
    data: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "event_id": self.event_id,
            "session_id": self.session_id,
            "event_type": self.event_type,
            "actor_id": self.actor_id,
            "target_id": self.target_id,
            "timestamp": self.timestamp,
            "data": self.data,
        }


@dataclass
class SessionConfig:
    """Configuration for a collaboration session."""
    
    max_participants: int = 50
    allow_public_join: bool = False
    require_invite: bool = True
    auto_pause_empty: bool = True
    empty_timeout_minutes: int = 30
    max_duration_minutes: Optional[int] = None
    record_events: bool = True
    allow_role_changes: bool = True
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "max_participants": self.max_participants,
            "allow_public_join": self.allow_public_join,
            "require_invite": self.require_invite,
            "auto_pause_empty": self.auto_pause_empty,
            "empty_timeout_minutes": self.empty_timeout_minutes,
            "max_duration_minutes": self.max_duration_minutes,
            "record_events": self.record_events,
            "allow_role_changes": self.allow_role_changes,
        }


class CollaborationSession:
    """A collaborative session with multiple participants."""
    
    def __init__(self, session_id: Optional[str] = None,
                 name: str = "", creator_id: str = ""):
        self.session_id = session_id or str(uuid.uuid4())[:8]
        self.name = name
        self.description: str = ""
        self.creator_id = creator_id
        
        # Status
        self.status: SessionStatus = SessionStatus.INITIALIZING
        self.created_at: str = datetime.utcnow().isoformat()
        self.started_at: Optional[str] = None
        self.ended_at: Optional[str] = None
        
        # Participants
        self._participants: Dict[str, Participant] = {}
        self._invites: Dict[str, Dict[str, Any]] = {}  # invite_code -> invite_data
        
        # Configuration
        self.config = SessionConfig()
        
        # Event tracking
        self._event_log: List[SessionEvent] = []
        self._event_callbacks: List[Callable] = []
        
        # Session data (shared state)
        self._data: Dict[str, Any] = {}
        self._metadata: Dict[str, Any] = {}
        
        # Thread safety
        self._lock = threading.RLock()
        
        # Initialize
        self._emit_event("session_created", creator_id)
    
    def _emit_event(self, event_type: str, actor_id: str = "",
                   target_id: str = "", data: Optional[Dict] = None):
        """Emit a session event."""
        event = SessionEvent(
            session_id=self.session_id,
            event_type=event_type,
            actor_id=actor_id,
            target_id=target_id,
            data=data or {},
        )
        
        with self._lock:
            if self.config.record_events:
                self._event_log.append(event)
        
        # Notify callbacks
        for callback in self._event_callbacks:
            try:
                callback(event.to_dict())
            except Exception:
                pass
    
    def start(self):
        """Start the session."""
        with self._lock:
            if self.status == SessionStatus.INITIALIZING:
                self.status = SessionStatus.ACTIVE
                self.started_at = datetime.utcnow().isoformat()
                self._emit_event("session_started", self.creator_id)
    
    def pause(self, paused_by: str = ""):
        """Pause the session."""
        with self._lock:
            if self.status == SessionStatus.ACTIVE:
                self.status = SessionStatus.PAUSED
                self._emit_event("session_paused", paused_by)
    
    def resume(self, resumed_by: str = ""):
        """Resume a paused session."""
        with self._lock:
            if self.status == SessionStatus.PAUSED:
                self.status = SessionStatus.ACTIVE
                self._emit_event("session_resumed", resumed_by)
    
    def end(self, ended_by: str = ""):
        """End the session."""
        with self._lock:
            if self.status not in [SessionStatus.ENDING, SessionStatus.ENDED]:
                self.status = SessionStatus.ENDING
                self._emit_event("session_ending", ended_by)
                
                # Disconnect all participants
                for participant_id in list(self._participants.keys()):
                    self._remove_participant_internal(participant_id, "session_ended")
                
                self.status = SessionStatus.ENDED
                self.ended_at = datetime.utcnow().isoformat()
                self._emit_event("session_ended", ended_by)
    
    def join(self, user_id: str, name: str = "",
             invite_code: Optional[str] = None) -> Optional[Participant]:
        """Join a participant to the session."""
        with self._lock:
            # Check session status
            if self.status != SessionStatus.ACTIVE:
                return None
            
            # Check capacity
            if len(self._participants) >= self.config.max_participants:
                return None
            
            # Check invite requirement
            if self.config.require_invite and invite_code:
                if invite_code not in self._invites:
                    return None
                invite = self._invites[invite_code]
                if invite.get("used", False):
                    return None
                invite["used"] = True
            
            # Check if already joined
            existing = self._get_participant_by_user(user_id)
            if existing and existing.is_active:
                existing.is_active = True
                return existing
            
            # Determine role
            role = ParticipantRole.VIEWER
            if user_id == self.creator_id:
                role = ParticipantRole.HOST
            
            # Create participant
            participant = Participant(
                user_id=user_id,
                name=name or f"User-{user_id[:4]}",
                role=role,
            )
            
            self._participants[participant.participant_id] = participant
            
            self._emit_event(
                "participant_joined",
                actor_id=user_id,
                target_id=participant.participant_id,
                data={"role": role.value},
            )
            
            return participant
    
    def leave(self, participant_id: str, user_id: str = ""):
        """Remove a participant from the session."""
        with self._lock:
            self._remove_participant_internal(participant_id, "left", user_id)
    
    def _remove_participant_internal(self, participant_id: str,
                                     reason: str = "left",
                                     user_id: str = ""):
        """Internal participant removal (must be called with lock held)."""
        if participant_id not in self._participants:
            return
        
        participant = self._participants[participant_id]
        participant.is_active = False
        participant.left_at = datetime.utcnow().isoformat()
        
        self._emit_event(
            "participant_left",
            actor_id=user_id or participant.user_id,
            target_id=participant_id,
            data={"reason": reason},
        )
        
        # Auto-pause if empty and configured
        if self.config.auto_pause_empty:
            active_count = self.get_active_participant_count()
            if active_count == 0 and self.status == SessionStatus.ACTIVE:
                self.status = SessionStatus.PAUSED
                self._emit_event("session_auto_paused", data={"reason": "empty"})
    
    def _get_participant_by_user(self, user_id: str) -> Optional[Participant]:
        """Get participant by user ID (must be called with lock held)."""
        for p in self._participants.values():
            if p.user_id == user_id:
                return p
        return None
    
    def get_participant(self, participant_id: str) -> Optional[Participant]:
        """Get a participant by ID."""
        with self._lock:
            return self._participants.get(participant_id)
    
    def get_active_participants(self) -> List[Participant]:
        """Get all active participants."""
        with self._lock:
            return [
                p for p in self._participants.values()
                if p.is_active
            ]
    
    def get_active_participant_count(self) -> int:
        """Get count of active participants."""
        with self._lock:
            return sum(1 for p in self._participants.values() if p.is_active)
    
    def change_role(self, participant_id: str, new_role: ParticipantRole,
                   changed_by: str = "") -> bool:
        """Change a participant's role."""
        with self._lock:
            if not self.config.allow_role_changes:
                return False
            
            if participant_id not in self._participants:
                return False
            
            participant = self._participants[participant_id]
            old_role = participant.role
            
            participant.role = new_role
            participant.can_edit = new_role in [
                ParticipantRole.HOST, ParticipantRole.COHOST, ParticipantRole.EDITOR
            ]
            participant.can_invite = new_role in [
                ParticipantRole.HOST, ParticipantRole.COHOST
            ]
            participant.can_moderate = new_role in [
                ParticipantRole.HOST, ParticipantRole.COHOST
            ]
            
            self._emit_event(
                "role_changed",
                actor_id=changed_by,
                target_id=participant_id,
                data={
                    "old_role": old_role.value,
                    "new_role": new_role.value,
                },
            )
            
            return True
    
    def create_invite(self, created_by: str = "",
                     expires_minutes: int = 60,
                     max_uses: int = 1) -> str:
        """Create an invite code for the session."""
        invite_code = str(uuid.uuid4())[:12]
        
        with self._lock:
            self._invites[invite_code] = {
                "created_by": created_by,
                "created_at": datetime.utcnow().isoformat(),
                "expires_at": (
                    datetime.utcnow() + timedelta(minutes=expires_minutes)
                ).isoformat(),
                "max_uses": max_uses,
                "uses": 0,
                "used": False,
            }
        
        self._emit_event(
            "invite_created",
            actor_id=created_by,
            data={
                "invite_code": invite_code,
                "expires_minutes": expires_minutes,
            },
        )
        
        return invite_code
    
    def get_data(self, key: str, default: Any = None) -> Any:
        """Get session data."""
        with self._lock:
            return self._data.get(key, default)
    
    def set_data(self, key: str, value: Any, set_by: str = ""):
        """Set session data."""
        with self._lock:
            old_value = self._data.get(key)
            self._data[key] = value
            
            self._emit_event(
                "data_changed",
                actor_id=set_by,
                data={
                    "key": key,
                    "old_value": old_value,
                    "new_value": value,
                },
            )
    
    def register_event_callback(self, callback: Callable):
        """Register a callback for session events."""
        self._event_callbacks.append(callback)
    
    def get_event_log(self, limit: int = 100,
                     event_type: Optional[str] = None) -> List[SessionEvent]:
        """Get session event log."""
        with self._lock:
            events = self._event_log.copy()
        
        if event_type:
            events = [e for e in events if e.event_type == event_type]
        
        # Sort by timestamp descending
        events.sort(key=lambda e: e.timestamp, reverse=True)
        
        return events[:limit]
    
    def set_metadata(self, key: str, value: Any):
        """Set session metadata (not tracked in event log)."""
        with self._lock:
            self._metadata[key] = value
    
    def get_metadata(self, key: str, default: Any = None) -> Any:
        """Get session metadata."""
        with self._lock:
            return self._metadata.get(key, default)
    
    def is_expired(self) -> bool:
        """Check if session has exceeded max duration."""
        if not self.config.max_duration_minutes or not self.started_at:
            return False
        
        start = datetime.fromisoformat(self.started_at)
        elapsed = datetime.utcnow() - start
        
        return elapsed > timedelta(minutes=self.config.max_duration_minutes)
    
    def get_state(self) -> Dict[str, Any]:
        """Get session state summary."""
        with self._lock:
            return {
                "session_id": self.session_id,
                "name": self.name,
                "status": self.status.value,
                "participant_count": self.get_active_participant_count(),
                "max_participants": self.config.max_participants,
                "created_at": self.created_at,
                "started_at": self.started_at,
                "ended_at": self.ended_at,
                "creator_id": self.creator_id,
                "event_count": len(self._event_log),
            }
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        with self._lock:
            return {
                "session_id": self.session_id,
                "name": self.name,
                "description": self.description,
                "status": self.status.value,
                "creator_id": self.creator_id,
                "participants": [p.to_dict() for p in self._participants.values()],
                "config": self.config.to_dict(),
                "metadata": self._metadata,
                "recent_events": [e.to_dict() for e in self._event_log[-10:]],
                "created_at": self.created_at,
                "started_at": self.started_at,
                "ended_at": self.ended_at,
            }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'CollaborationSession':
        """Create from dictionary (for persistence)."""
        session = cls(
            session_id=data.get("session_id"),
            name=data.get("name", ""),
            creator_id=data.get("creator_id", ""),
        )
        
        session.description = data.get("description", "")
        session.status = SessionStatus(data.get("status", "initializing"))
        session.created_at = data.get("created_at", session.created_at)
        session.started_at = data.get("started_at")
        session.ended_at = data.get("ended_at")
        
        # Restore config
        config_data = data.get("config", {})
        session.config.max_participants = config_data.get("max_participants", 50)
        session.config.allow_public_join = config_data.get("allow_public_join", False)
        session.config.require_invite = config_data.get("require_invite", True)
        session.config.auto_pause_empty = config_data.get("auto_pause_empty", True)
        session.config.empty_timeout_minutes = config_data.get("empty_timeout_minutes", 30)
        session.config.max_duration_minutes = config_data.get("max_duration_minutes")
        session.config.record_events = config_data.get("record_events", True)
        session.config.allow_role_changes = config_data.get("allow_role_changes", True)
        
        # Restore metadata
        session._metadata = data.get("metadata", {})
        
        # Restore participants
        for p_data in data.get("participants", []):
            participant = Participant(
                participant_id=p_data.get("participant_id"),
                user_id=p_data.get("user_id", ""),
                name=p_data.get("name", ""),
                role=ParticipantRole(p_data.get("role", "viewer")),
                joined_at=p_data.get("joined_at"),
                left_at=p_data.get("left_at"),
                is_active=p_data.get("is_active", True),
            )
            session._participants[participant.participant_id] = participant
        
        return session


class SessionManager:
    """Manages multiple collaboration sessions."""
    
    def __init__(self):
        self._sessions: Dict[str, CollaborationSession] = {}
        self._lock = threading.RLock()
    
    def create_session(self, name: str = "", creator_id: str = "",
                      config: Optional[SessionConfig] = None) -> CollaborationSession:
        """Create a new collaboration session."""
        with self._lock:
            session = CollaborationSession(
                name=name,
                creator_id=creator_id,
            )
            
            if config:
                session.config = config
            
            self._sessions[session.session_id] = session
            return session
    
    def get_session(self, session_id: str) -> Optional[CollaborationSession]:
        """Get a session by ID."""
        with self._lock:
            return self._sessions.get(session_id)
    
    def list_sessions(self, status: Optional[SessionStatus] = None) -> List[CollaborationSession]:
        """List sessions, optionally filtered by status."""
        with self._lock:
            sessions = list(self._sessions.values())
        
        if status:
            sessions = [s for s in sessions if s.status == status]
        
        return sessions
    
    def end_session(self, session_id: str, ended_by: str = "") -> bool:
        """End a session."""
        with self._lock:
            session = self._sessions.get(session_id)
            if session:
                session.end(ended_by)
                return True
        return False
    
    def delete_session(self, session_id: str) -> bool:
        """Delete a session (must be ended first)."""
        with self._lock:
            session = self._sessions.get(session_id)
            if session and session.status == SessionStatus.ENDED:
                del self._sessions[session_id]
                return True
        return False
    
    def get_user_sessions(self, user_id: str) -> List[CollaborationSession]:
        """Get all sessions a user is participating in."""
        with self._lock:
            result = []
            for session in self._sessions.values():
                participant = session._get_participant_by_user(user_id)
                if participant and participant.is_active:
                    result.append(session)
            return result
    
    def cleanup_ended(self, older_than_minutes: int = 60) -> int:
        """Clean up ended sessions older than specified time."""
        cutoff = datetime.utcnow() - timedelta(minutes=older_than_minutes)
        
        with self._lock:
            to_delete = []
            for session_id, session in self._sessions.items():
                if session.status == SessionStatus.ENDED and session.ended_at:
                    ended_time = datetime.fromisoformat(session.ended_at)
                    if ended_time < cutoff:
                        to_delete.append(session_id)
            
            for session_id in to_delete:
                del self._sessions[session_id]
        
        return len(to_delete)
    
    def get_state(self) -> Dict[str, Any]:
        """Get session manager state."""
        with self._lock:
            return {
                "total_sessions": len(self._sessions),
                "active_sessions": sum(1 for s in self._sessions.values() if s.status == SessionStatus.ACTIVE),
                "paused_sessions": sum(1 for s in self._sessions.values() if s.status == SessionStatus.PAUSED),
                "ended_sessions": sum(1 for s in self._sessions.values() if s.status == SessionStatus.ENDED),
            }
