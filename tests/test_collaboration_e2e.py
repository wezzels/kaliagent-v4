"""
End-to-End Collaboration Tests
===============================

Integration tests for complete collaboration workflows.
"""

import pytest
import time
from datetime import datetime, timedelta


@pytest.fixture
def collaboration_imports():
    """Import all collaboration modules."""
    from agentic_ai.collaboration.workspace import Workspace, WorkspaceResource, LockType
    from agentic_ai.collaboration.permissions import PermissionManager, Permission, Role
    from agentic_ai.collaboration.realtime import (
        RealTimeCollaboration, Operation, OperationType
    )
    from agentic_ai.collaboration.sessions import (
        CollaborationSession, SessionManager, ParticipantRole, SessionStatus
    )
    from agentic_ai.collaboration.presence import (
        CollaborationHub, PresenceStatus, ActivityType
    )
    
    return {
        'Workspace': Workspace,
        'WorkspaceResource': WorkspaceResource,
        'LockType': LockType,
        'PermissionManager': PermissionManager,
        'Permission': Permission,
        'Role': Role,
        'ParticipantRole': ParticipantRole,
        'RealTimeCollaboration': RealTimeCollaboration,
        'Operation': Operation,
        'OperationType': OperationType,
        'CollaborationSession': CollaborationSession,
        'SessionManager': SessionManager,
        'SessionStatus': SessionStatus,
        'CollaborationHub': CollaborationHub,
        'PresenceStatus': PresenceStatus,
        'ActivityType': ActivityType,
    }


class TestEndToEndCollaboration:
    """End-to-end collaboration workflow tests."""
    
    def test_multi_agent_collaborative_workflow(self, collaboration_imports):
        """Test multiple agents collaborating on a shared document."""
        Workspace = collaboration_imports['Workspace']
        RealTimeCollaboration = collaboration_imports['RealTimeCollaboration']
        Operation = collaboration_imports['Operation']
        OperationType = collaboration_imports['OperationType']
        CollaborationHub = collaboration_imports['CollaborationHub']
        
        # Setup
        workspace = Workspace(name="Agent Collaboration")
        rtc = RealTimeCollaboration()
        hub = CollaborationHub()
        
        # Agents join workspace
        workspace.add_participant("agent-1", is_owner=True)
        workspace.add_participant("agent-2")
        
        # Create shared document
        doc = workspace.create_resource(
            name="Shared Document",
            resource_type="document",
            content="Initial content",
            creator_id="agent-1",
        )
        
        # Agents come online
        hub.presence.mark_active("agent-1")
        hub.presence.mark_active("agent-2")
        
        # Agent-1 starts editing
        rtc.connect_user("agent-1", name="Agent-1")
        op1 = Operation(
            operation_type=OperationType.INSERT,
            document_id=doc.resource_id,
            user_id="agent-1",
            position=0,
            content="Agent-1: ",
        )
        rtc.submit_operation(op1)
        
        # Agent-2 concurrently edits
        rtc.connect_user("agent-2", name="Agent-2")
        op2 = Operation(
            operation_type=OperationType.INSERT,
            document_id=doc.resource_id,
            user_id="agent-2",
            position=0,
            content="Agent-2: ",
        )
        rtc.submit_operation(op2)
        
        # Verify both operations were processed
        doc_state = rtc.get_document_state(doc.resource_id)
        assert doc_state["version"] >= 2
        
        # All agents should be online
        online = hub.presence.get_online_users()
        assert len(online) >= 2
    
    def test_session_with_realtime_collaboration(self, collaboration_imports):
        """Test collaboration session with real-time features."""
        CollaborationSession = collaboration_imports['CollaborationSession']
        SessionManager = collaboration_imports['SessionManager']
        RealTimeCollaboration = collaboration_imports['RealTimeCollaboration']
        CollaborationHub = collaboration_imports['CollaborationHub']
        Workspace = collaboration_imports['Workspace']
        
        # Create session manager
        manager = SessionManager()
        rtc = RealTimeCollaboration()
        hub = CollaborationHub()
        
        # Create collaboration session
        session = manager.create_session(
            name="Team Collaboration",
            creator_id="alice",
        )
        session.start()
        
        # Create workspace for session
        workspace = Workspace(name="Session Workspace")
        session.set_metadata("workspace_id", workspace.workspace_id)
        
        # Participants join
        alice = session.join(user_id="alice", name="Alice")
        bob = session.join(user_id="bob", name="Bob")
        
        # Join workspace
        workspace.add_participant("alice", is_owner=True)
        workspace.add_participant("bob")
        
        # Set presence
        hub.presence.mark_active("alice", session_id=session.session_id)
        hub.presence.mark_active("bob", session_id=session.session_id)
        
        # Create document in workspace
        doc = workspace.create_resource(
            name="Meeting Notes",
            resource_type="document",
            content="# Meeting Notes\n\n",
            creator_id="alice",
        )
        
        # Alice starts typing
        hub.typing.start_typing("alice", "document", doc.resource_id)
        
        typists = hub.typing.get_typing_users("document", doc.resource_id)
        assert "alice" in typists
        
        # Alice stops typing and saves
        hub.typing.stop_typing("alice", "document", doc.resource_id)
        
        workspace.update_resource(
            doc.resource_id,
            content="# Meeting Notes\n\n## Attendees\n- Alice\n- Bob\n",
            updater_id="alice",
        )
        
        # Verify session state
        assert session.get_active_participant_count() == 2
        
        # Check activity
        doc_activity = workspace.get_change_log(resource_id=doc.resource_id)
        assert len(doc_activity) >= 2  # create + update
    
    def test_conflict_resolution_workflow(self, collaboration_imports):
        """Test operational transformation conflict resolution."""
        Workspace = collaboration_imports['Workspace']
        RealTimeCollaboration = collaboration_imports['RealTimeCollaboration']
        Operation = collaboration_imports['Operation']
        OperationType = collaboration_imports['OperationType']
        
        # Setup
        workspace = Workspace(name="Conflict Test")
        rtc = RealTimeCollaboration()
        
        workspace.add_participant("user-1", is_owner=True)
        workspace.add_participant("user-2")
        
        doc = workspace.create_resource(
            name="Test Doc",
            resource_type="document",
            content="Hello",
            creator_id="user-1",
        )
        
        # Both users connect
        rtc.connect_user("user-1", name="User-1")
        rtc.connect_user("user-2", name="User-2")
        
        # Concurrent operations at same position
        op1 = Operation(
            operation_type=OperationType.INSERT,
            document_id=doc.resource_id,
            user_id="user-1",
            position=5,
            content=" World",
        )
        
        op2 = Operation(
            operation_type=OperationType.INSERT,
            document_id=doc.resource_id,
            user_id="user-2",
            position=5,
            content="!",
        )
        
        # Submit both operations
        result1 = rtc.submit_operation(op1)
        result2 = rtc.submit_operation(op2)
        
        # Both should have versions
        assert result1.version >= 1
        assert result2.version >= 1
        
        # Get final state
        state = rtc.get_document_state(doc.resource_id)
        assert state["version"] >= 2
    
    def test_permission_enforcement_workflow(self, collaboration_imports):
        """Test permission enforcement across collaboration features."""
        Workspace = collaboration_imports['Workspace']
        PermissionManager = collaboration_imports['PermissionManager']
        Role = collaboration_imports['Role']
        Permission = collaboration_imports['Permission']
        
        # Setup
        workspace = Workspace(name="Permission Test")
        perm_manager = PermissionManager()
        
        # Create users with different roles
        perm_manager.grant_access("admin", Role.OWNER)
        perm_manager.grant_access("editor", Role.EDITOR)
        perm_manager.grant_access("viewer", Role.VIEWER)
        
        workspace.add_participant("admin", is_owner=True)
        workspace.add_participant("editor")
        workspace.add_participant("viewer")
        
        # Create resource
        resource = workspace.create_resource(
            name="Protected Doc",
            resource_type="document",
            content="Secret content",
            creator_id="admin",
        )
        
        # Admin can do anything
        assert perm_manager.has_permission("admin", Permission.ADMIN)
        
        # Editor can edit but not delete
        assert perm_manager.has_permission("editor", Permission.WRITE)
        
        # Viewer can only read
        assert perm_manager.has_permission("viewer", Permission.READ)
        assert not perm_manager.has_permission("viewer", Permission.WRITE)
    
    def test_presence_and_activity_tracking(self, collaboration_imports):
        """Test comprehensive presence and activity tracking."""
        CollaborationHub = collaboration_imports['CollaborationHub']
        PresenceStatus = collaboration_imports['PresenceStatus']
        ActivityType = collaboration_imports['ActivityType']
        CollaborationSession = collaboration_imports['CollaborationSession']
        
        # Setup
        hub = CollaborationHub()
        session = CollaborationSession(name="Activity Test", creator_id="user-1")
        session.start()
        
        # User joins
        session.join(user_id="user-1", name="Alice")
        hub.presence.mark_active("user-1", session_id=session.session_id)
        
        # Check presence
        presence = hub.presence.get_presence("user-1")
        assert presence.status == PresenceStatus.ONLINE
        
        # User performs actions
        hub.activity.add_event(
            event_type=ActivityType.JOINED,
            user_id="user-1",
            target_type="session",
            target_id=session.session_id,
            user_name="Alice",
        )
        
        hub.activity.add_event(
            event_type=ActivityType.EDITED,
            user_id="user-1",
            target_type="document",
            target_id="doc-1",
            user_name="Alice",
        )
        
        # Get user activity
        user_activity = hub.activity.get_user_activity("user-1", limit=10)
        assert len(user_activity) >= 2
        
        # Get session activity
        session_activity = hub.activity.get_target_activity(
            "session", session.session_id, limit=10
        )
        assert len(session_activity) >= 1
        
        # User goes away
        hub.presence.set_presence("user-1", PresenceStatus.AWAY)
        
        presence = hub.presence.get_presence("user-1")
        assert presence.status == PresenceStatus.AWAY
        
        # User goes offline
        hub.presence.set_offline("user-1")
        
        presence = hub.presence.get_presence("user-1")
        assert presence.status == PresenceStatus.OFFLINE
    
    def test_multi_session_management(self, collaboration_imports):
        """Test managing multiple concurrent collaboration sessions."""
        SessionManager = collaboration_imports['SessionManager']
        CollaborationHub = collaboration_imports['CollaborationHub']
        Workspace = collaboration_imports['Workspace']
        
        # Setup
        manager = SessionManager()
        hub = CollaborationHub()
        
        # Create multiple sessions
        session1 = manager.create_session(name="Morning Standup", creator_id="alice")
        session2 = manager.create_session(name="Design Review", creator_id="bob")
        session3 = manager.create_session(name="Planning", creator_id="charlie")
        
        session1.start()
        session2.start()
        session3.start()
        
        # Create workspaces for each
        ws1 = Workspace(name="Standup Workspace")
        ws2 = Workspace(name="Design Workspace")
        ws3 = Workspace(name="Planning Workspace")
        
        # Users join multiple sessions
        session1.join(user_id="alice", name="Alice")
        session1.join(user_id="bob", name="Bob")
        
        session2.join(user_id="bob", name="Bob")
        session2.join(user_id="charlie", name="Charlie")
        session2.join(user_id="alice", name="Alice")
        
        session3.join(user_id="alice", name="Alice")
        session3.join(user_id="charlie", name="Charlie")
        
        # Set presence for each session
        hub.presence.mark_active("alice", session_id=session1.session_id)
        hub.presence.mark_active("bob", session_id=session1.session_id)
        
        # Get user's sessions
        alice_sessions = manager.get_user_sessions("alice")
        assert len(alice_sessions) == 3
        
        bob_sessions = manager.get_user_sessions("bob")
        assert len(bob_sessions) == 2
        
        # End one session
        manager.end_session(session1.session_id, ended_by="alice")
        
        # Check state
        state = manager.get_state()
        assert state["active_sessions"] == 2
        assert state["ended_sessions"] >= 1
    
    def test_full_collaboration_lifecycle(self, collaboration_imports):
        """Test complete collaboration lifecycle from start to finish."""
        SessionManager = collaboration_imports['SessionManager']
        Workspace = collaboration_imports['Workspace']
        PermissionManager = collaboration_imports['PermissionManager']
        Role = collaboration_imports['Role']
        RealTimeCollaboration = collaboration_imports['RealTimeCollaboration']
        CollaborationHub = collaboration_imports['CollaborationHub']
        Operation = collaboration_imports['Operation']
        OperationType = collaboration_imports['OperationType']
        
        # Phase 1: Setup
        manager = SessionManager()
        rtc = RealTimeCollaboration()
        hub = CollaborationHub()
        
        session = manager.create_session(
            name="Project Kickoff",
            creator_id="project-lead",
        )
        session.start()
        
        workspace = Workspace(name="Project Workspace")
        perm_manager = PermissionManager()
        
        # Phase 2: Participants join
        project_lead = session.join(user_id="project-lead", name="Project Lead")
        developer1 = session.join(user_id="dev-1", name="Developer 1")
        developer2 = session.join(user_id="dev-2", name="Developer 2")
        
        # Add to workspace
        workspace.add_participant("project-lead", is_owner=True)
        workspace.add_participant("dev-1")
        workspace.add_participant("dev-2")
        
        # Set permissions
        perm_manager.grant_access("project-lead", Role.OWNER)
        perm_manager.grant_access("dev-1", Role.EDITOR)
        perm_manager.grant_access("dev-2", Role.EDITOR)
        
        # Phase 3: Come online
        for user_id in ["project-lead", "dev-1", "dev-2"]:
            hub.presence.mark_active(user_id, session_id=session.session_id)
            rtc.connect_user(user_id)
        
        # Phase 4: Collaborative work
        # Create project document
        project_doc = workspace.create_resource(
            name="Project Plan",
            resource_type="document",
            content="# Project Plan\n\n",
            creator_id="project-lead",
        )
        
        # Multiple users edit
        for i, user_id in enumerate(["dev-1", "dev-2"]):
            op = Operation(
                operation_type=OperationType.INSERT,
                document_id=project_doc.resource_id,
                user_id=user_id,
                position=len(project_doc.content),
                content=f"## Section {i+1}\n\n",
            )
            rtc.submit_operation(op)
        
        # Phase 5: Check workspace changes
        changes = workspace.get_change_log(resource_id=project_doc.resource_id)
        assert len(changes) >= 1  # At least create
        
        # Phase 6: Session management
        # End session
        manager.end_session(session.session_id, ended_by="project-lead")
        
        # Verify final state
        assert session.status.value == "ended"
        
        hub_state = hub.get_state()
        assert hub_state["presence"]["total_users"] >= 3
        
        rtc_state = rtc.get_state()
        assert rtc_state["total_users"] >= 3


class TestPerformanceScenarios:
    """Performance-focused integration tests."""
    
    def test_high_frequency_operations(self, collaboration_imports):
        """Test handling high-frequency operations."""
        RealTimeCollaboration = collaboration_imports['RealTimeCollaboration']
        Operation = collaboration_imports['Operation']
        OperationType = collaboration_imports['OperationType']
        
        rtc = RealTimeCollaboration()
        rtc.connect_user("user-1")
        
        doc_id = "perf-test-doc"
        
        # Submit 100 operations rapidly
        start_time = datetime.utcnow()
        
        for i in range(100):
            op = Operation(
                operation_type=OperationType.INSERT,
                document_id=doc_id,
                user_id="user-1",
                position=i,
                content="x",
            )
            rtc.submit_operation(op)
        
        end_time = datetime.utcnow()
        elapsed = (end_time - start_time).total_seconds()
        
        # Should complete in reasonable time (< 5 seconds for 100 ops)
        assert elapsed < 5.0
        
        # Check document state
        state = rtc.get_document_state(doc_id)
        assert state["version"] == 100


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
