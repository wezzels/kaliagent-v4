"""
Tests for Collaboration Sessions
=================================

Unit tests for session management features.
"""

import pytest
from datetime import datetime, timedelta


@pytest.fixture
def session_imports():
    """Import session modules."""
    from agentic_ai.collaboration.sessions import (
        CollaborationSession, SessionManager, Participant,
        ParticipantRole, SessionStatus, SessionConfig, SessionEvent
    )
    
    return {
        'CollaborationSession': CollaborationSession,
        'SessionManager': SessionManager,
        'Participant': Participant,
        'ParticipantRole': ParticipantRole,
        'SessionStatus': SessionStatus,
        'SessionConfig': SessionConfig,
        'SessionEvent': SessionEvent,
    }


class TestParticipant:
    """Test Participant class."""
    
    def test_participant_creation(self, session_imports):
        """Test creating a participant."""
        Participant = session_imports['Participant']
        ParticipantRole = session_imports['ParticipantRole']
        
        participant = Participant(
            user_id="user-1",
            name="Alice",
            role=ParticipantRole.EDITOR,
        )
        
        assert participant.user_id == "user-1"
        assert participant.name == "Alice"
        assert participant.role == ParticipantRole.EDITOR
    
    def test_participant_capabilities(self, session_imports):
        """Test participant capabilities by role."""
        Participant = session_imports['Participant']
        ParticipantRole = session_imports['ParticipantRole']
        
        # Viewer
        viewer = Participant(user_id="v1", role=ParticipantRole.VIEWER)
        assert viewer.can_edit is False
        assert viewer.can_invite is False
        assert viewer.can_moderate is False
        
        # Editor
        editor = Participant(user_id="e1", role=ParticipantRole.EDITOR)
        assert editor.can_edit is True
        assert editor.can_invite is False
        assert editor.can_moderate is False
        
        # Cohost
        cohost = Participant(user_id="c1", role=ParticipantRole.COHOST)
        assert cohost.can_edit is True
        assert cohost.can_invite is True
        assert cohost.can_moderate is True
        
        # Host
        host = Participant(user_id="h1", role=ParticipantRole.HOST)
        assert host.can_edit is True
        assert host.can_invite is True
        assert host.can_moderate is True
    
    def test_participant_to_dict(self, session_imports):
        """Test participant serialization."""
        Participant = session_imports['Participant']
        ParticipantRole = session_imports['ParticipantRole']
        
        participant = Participant(
            user_id="user-1",
            name="Bob",
            role=ParticipantRole.EDITOR,
        )
        
        data = participant.to_dict()
        
        assert data["user_id"] == "user-1"
        assert data["name"] == "Bob"
        assert data["role"] == "editor"


class TestSessionConfig:
    """Test SessionConfig class."""
    
    def test_config_creation(self, session_imports):
        """Test creating session config."""
        SessionConfig = session_imports['SessionConfig']
        
        config = SessionConfig(
            max_participants=10,
            require_invite=True,
            auto_pause_empty=False,
        )
        
        assert config.max_participants == 10
        assert config.require_invite is True
        assert config.auto_pause_empty is False
    
    def test_config_to_dict(self, session_imports):
        """Test config serialization."""
        SessionConfig = session_imports['SessionConfig']
        
        config = SessionConfig()
        data = config.to_dict()
        
        assert data["max_participants"] == 50
        assert "require_invite" in data


class TestSessionEvent:
    """Test SessionEvent class."""
    
    def test_event_creation(self, session_imports):
        """Test creating a session event."""
        SessionEvent = session_imports['SessionEvent']
        
        event = SessionEvent(
            session_id="session-001",
            event_type="participant_joined",
            actor_id="user-1",
            target_id="participant-1",
        )
        
        assert event.session_id == "session-001"
        assert event.event_type == "participant_joined"
    
    def test_event_to_dict(self, session_imports):
        """Test event serialization."""
        SessionEvent = session_imports['SessionEvent']
        
        event = SessionEvent(
            session_id="session-001",
            event_type="role_changed",
            data={"old_role": "viewer", "new_role": "editor"},
        )
        
        data = event.to_dict()
        
        assert data["event_type"] == "role_changed"
        assert "event_id" in data


class TestCollaborationSession:
    """Test CollaborationSession class."""
    
    def test_session_creation(self, session_imports):
        """Test creating a collaboration session."""
        CollaborationSession = session_imports['CollaborationSession']
        
        session = CollaborationSession(
            session_id="session-001",
            name="Team Meeting",
            creator_id="user-1",
        )
        
        assert session.session_id == "session-001"
        assert session.name == "Team Meeting"
        assert session.creator_id == "user-1"
        assert session.status.value == "initializing"
    
    def test_session_start(self, session_imports):
        """Test starting a session."""
        CollaborationSession = session_imports['CollaborationSession']
        SessionStatus = session_imports['SessionStatus']
        
        session = CollaborationSession(name="Test")
        session.start()
        
        assert session.status == SessionStatus.ACTIVE
        assert session.started_at is not None
    
    def test_session_pause_resume(self, session_imports):
        """Test pausing and resuming a session."""
        CollaborationSession = session_imports['CollaborationSession']
        SessionStatus = session_imports['SessionStatus']
        
        session = CollaborationSession(name="Test")
        session.start()
        session.pause(paused_by="user-1")
        
        assert session.status == SessionStatus.PAUSED
        
        session.resume(resumed_by="user-1")
        assert session.status == SessionStatus.ACTIVE
    
    def test_session_end(self, session_imports):
        """Test ending a session."""
        CollaborationSession = session_imports['CollaborationSession']
        SessionStatus = session_imports['SessionStatus']
        
        session = CollaborationSession(name="Test")
        session.start()
        session.end(ended_by="user-1")
        
        assert session.status == SessionStatus.ENDED
        assert session.ended_at is not None
    
    def test_session_join(self, session_imports):
        """Test joining a session."""
        CollaborationSession = session_imports['CollaborationSession']
        
        session = CollaborationSession(
            name="Test",
            creator_id="user-1",
        )
        session.start()
        
        # Creator joins automatically as host
        participant = session.join(user_id="user-1", name="Alice")
        
        assert participant is not None
        assert participant.user_id == "user-1"
    
    def test_session_join_multiple(self, session_imports):
        """Test multiple participants joining."""
        CollaborationSession = session_imports['CollaborationSession']
        
        session = CollaborationSession(name="Test", creator_id="user-1")
        session.start()
        
        session.join(user_id="user-1", name="Alice")
        session.join(user_id="user-2", name="Bob")
        session.join(user_id="user-3", name="Charlie")
        
        active = session.get_active_participants()
        assert len(active) == 3
    
    def test_session_leave(self, session_imports):
        """Test leaving a session."""
        CollaborationSession = session_imports['CollaborationSession']
        
        session = CollaborationSession(name="Test", creator_id="user-1")
        session.start()
        
        participant = session.join(user_id="user-1", name="Alice")
        session.leave(participant.participant_id, user_id="user-1")
        
        active = session.get_active_participants()
        assert len(active) == 0
    
    def test_session_role_change(self, session_imports):
        """Test changing participant role."""
        CollaborationSession = session_imports['CollaborationSession']
        ParticipantRole = session_imports['ParticipantRole']
        
        session = CollaborationSession(name="Test", creator_id="user-1")
        session.start()
        
        participant = session.join(user_id="user-2", name="Bob")
        
        # Change to editor
        success = session.change_role(
            participant.participant_id,
            ParticipantRole.EDITOR,
            changed_by="user-1",
        )
        
        assert success is True
        assert participant.role == ParticipantRole.EDITOR
        assert participant.can_edit is True
    
    def test_session_invite(self, session_imports):
        """Test creating session invites."""
        CollaborationSession = session_imports['CollaborationSession']
        
        session = CollaborationSession(name="Test", creator_id="user-1")
        session.start()
        
        invite_code = session.create_invite(
            created_by="user-1",
            expires_minutes=60,
            max_uses=1,
        )
        
        assert invite_code is not None
        assert len(invite_code) == 12
    
    def test_session_data(self, session_imports):
        """Test session data storage."""
        CollaborationSession = session_imports['CollaborationSession']
        
        session = CollaborationSession(name="Test")
        
        session.set_data("key1", "value1", set_by="user-1")
        value = session.get_data("key1")
        
        assert value == "value1"
    
    def test_session_event_log(self, session_imports):
        """Test session event log."""
        CollaborationSession = session_imports['CollaborationSession']
        
        session = CollaborationSession(name="Test", creator_id="user-1")
        session.start()
        session.join(user_id="user-2", name="Bob")
        
        events = session.get_event_log()
        
        assert len(events) > 0
    
    def test_session_to_dict(self, session_imports):
        """Test session serialization."""
        CollaborationSession = session_imports['CollaborationSession']
        
        session = CollaborationSession(
            name="Test Session",
            creator_id="user-1",
        )
        
        data = session.to_dict()
        
        assert data["name"] == "Test Session"
        assert "session_id" in data
        assert "participants" in data
    
    def test_session_from_dict(self, session_imports):
        """Test session deserialization."""
        CollaborationSession = session_imports['CollaborationSession']
        
        original = CollaborationSession(
            name="Test",
            creator_id="user-1",
        )
        original.description = "Test description"
        original.set_metadata("key", "value")
        
        data = original.to_dict()
        restored = CollaborationSession.from_dict(data)
        
        assert restored.session_id == original.session_id
        assert restored.name == original.name
        assert restored.description == original.description
    
    def test_session_capacity_limit(self, session_imports):
        """Test session capacity limit."""
        CollaborationSession = session_imports['CollaborationSession']
        SessionConfig = session_imports['SessionConfig']
        
        session = CollaborationSession(name="Test", creator_id="user-1")
        session.config.max_participants = 2
        session.start()
        
        session.join(user_id="user-1", name="Alice")
        session.join(user_id="user-2", name="Bob")
        
        # Third join should fail
        participant = session.join(user_id="user-3", name="Charlie")
        
        assert participant is None
    
    def test_session_auto_pause(self, session_imports):
        """Test auto-pause when empty."""
        CollaborationSession = session_imports['CollaborationSession']
        SessionStatus = session_imports['SessionStatus']
        
        session = CollaborationSession(name="Test", creator_id="user-1")
        session.config.auto_pause_empty = True
        session.start()
        
        participant = session.join(user_id="user-1", name="Alice")
        session.leave(participant.participant_id)
        
        assert session.status == SessionStatus.PAUSED


class TestSessionManager:
    """Test SessionManager class."""
    
    def test_manager_creation(self, session_imports):
        """Test creating session manager."""
        SessionManager = session_imports['SessionManager']
        
        manager = SessionManager()
        assert manager is not None
    
    def test_create_session(self, session_imports):
        """Test creating a session via manager."""
        SessionManager = session_imports['SessionManager']
        
        manager = SessionManager()
        session = manager.create_session(
            name="Team Meeting",
            creator_id="user-1",
        )
        
        assert session.name == "Team Meeting"
        assert manager.get_session(session.session_id) is not None
    
    def test_list_sessions(self, session_imports):
        """Test listing sessions."""
        SessionManager = session_imports['SessionManager']
        SessionStatus = session_imports['SessionStatus']
        
        manager = SessionManager()
        manager.create_session(name="Session 1", creator_id="user-1")
        manager.create_session(name="Session 2", creator_id="user-1")
        
        sessions = manager.list_sessions()
        assert len(sessions) == 2
    
    def test_end_session(self, session_imports):
        """Test ending a session via manager."""
        SessionManager = session_imports['SessionManager']
        SessionStatus = session_imports['SessionStatus']
        
        manager = SessionManager()
        session = manager.create_session(name="Test", creator_id="user-1")
        
        success = manager.end_session(session.session_id, ended_by="user-1")
        
        assert success is True
        assert session.status == SessionStatus.ENDED
    
    def test_get_user_sessions(self, session_imports):
        """Test getting user's sessions."""
        SessionManager = session_imports['SessionManager']
        
        manager = SessionManager()
        
        session1 = manager.create_session(name="Session 1", creator_id="user-1")
        session2 = manager.create_session(name="Session 2", creator_id="user-2")
        
        session1.start()
        session2.start()
        
        session1.join(user_id="user-1", name="Alice")
        session2.join(user_id="user-1", name="Alice")
        
        user_sessions = manager.get_user_sessions("user-1")
        
        assert len(user_sessions) == 2
    
    def test_cleanup_ended(self, session_imports):
        """Test cleaning up ended sessions."""
        SessionManager = session_imports['SessionManager']
        
        manager = SessionManager()
        
        session = manager.create_session(name="Test", creator_id="user-1")
        manager.end_session(session.session_id)
        
        # Manually set old ended time
        session.ended_at = (datetime.utcnow() - timedelta(minutes=90)).isoformat()
        
        removed = manager.cleanup_ended(older_than_minutes=60)
        
        assert removed >= 1
    
    def test_manager_state(self, session_imports):
        """Test getting manager state."""
        SessionManager = session_imports['SessionManager']
        
        manager = SessionManager()
        manager.create_session(name="Active", creator_id="user-1")
        
        state = manager.get_state()
        
        assert "total_sessions" in state
        assert state["total_sessions"] == 1


class TestSessionIntegration:
    """Integration tests for collaboration sessions."""
    
    def test_full_session_lifecycle(self, session_imports):
        """Test complete session lifecycle."""
        CollaborationSession = session_imports['CollaborationSession']
        ParticipantRole = session_imports['ParticipantRole']
        SessionStatus = session_imports['SessionStatus']
        
        # Create session
        session = CollaborationSession(
            name="Project Kickoff",
            creator_id="alice",
        )
        
        # Start session
        session.start()
        assert session.status == SessionStatus.ACTIVE
        
        # Participants join
        alice = session.join(user_id="alice", name="Alice")
        bob = session.join(user_id="bob", name="Bob")
        charlie = session.join(user_id="charlie", name="Charlie")
        
        assert session.get_active_participant_count() == 3
        
        # Change Bob's role to editor
        session.change_role(bob.participant_id, ParticipantRole.EDITOR, changed_by="alice")
        assert bob.can_edit is True
        
        # Set session data
        session.set_data("agenda", "Project planning", set_by="alice")
        assert session.get_data("agenda") == "Project planning"
        
        # Charlie leaves
        session.leave(charlie.participant_id, user_id="charlie")
        assert session.get_active_participant_count() == 2
        
        # End session
        session.end(ended_by="alice")
        assert session.status == SessionStatus.ENDED
    
    def test_multi_session_manager(self, session_imports):
        """Test managing multiple sessions."""
        SessionManager = session_imports['SessionManager']
        SessionStatus = session_imports['SessionStatus']
        
        manager = SessionManager()
        
        # Create multiple sessions
        session1 = manager.create_session(name="Morning Standup", creator_id="alice")
        session2 = manager.create_session(name="Design Review", creator_id="bob")
        
        session1.start()
        session2.start()
        
        # Alice joins both
        session1.join(user_id="alice", name="Alice")
        session2.join(user_id="alice", name="Alice")
        
        # Bob joins only design review
        session2.join(user_id="bob", name="Bob")
        
        # Check user sessions
        alice_sessions = manager.get_user_sessions("alice")
        assert len(alice_sessions) == 2
        
        # End morning standup
        manager.end_session(session1.session_id)
        
        # Check state
        state = manager.get_state()
        assert state["active_sessions"] == 1


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
