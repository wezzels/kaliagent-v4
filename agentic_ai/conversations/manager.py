"""
Conversation Manager
====================

Manages multiple conversation threads between agents.
"""

from typing import Optional, Dict, Any, List
from datetime import datetime
import uuid

from .thread import MessageThread, ConversationMessage, MessageType
from .state import ConversationState, ConversationStatus


class ConversationManager:
    """Manages agent conversations and threads."""

    def __init__(self):
        self.threads: Dict[str, MessageThread] = {}
        self.states: Dict[str, ConversationState] = {}
        self.agent_threads: Dict[str, List[str]] = {}  # agent_id -> thread_ids

    def create_thread(
        self,
        title: str,
        creator: str,
        participants: Optional[List[str]] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> MessageThread:
        """Create a new conversation thread."""
        thread_id = str(uuid.uuid4())[:8]

        thread = MessageThread(
            thread_id=thread_id,
            title=title,
            creator=creator,
        )

        # Add initial participants
        if participants:
            for participant in participants:
                thread.participants.add(participant)

        # Create state
        state = ConversationState(
            thread_id=thread_id,
            title=title,
            participants=[creator] + (participants or []),
            metadata=metadata or {},
        )

        # Store
        self.threads[thread_id] = thread
        self.states[thread_id] = state

        # Index by agent
        self._index_thread(creator, thread_id)
        if participants:
            for participant in participants:
                self._index_thread(participant, thread_id)

        return thread

    def _index_thread(self, agent_id: str, thread_id: str):
        """Index a thread by agent."""
        if agent_id not in self.agent_threads:
            self.agent_threads[agent_id] = []
        if thread_id not in self.agent_threads[agent_id]:
            self.agent_threads[agent_id].append(thread_id)

    def get_thread(self, thread_id: str) -> Optional[MessageThread]:
        """Get a thread by ID."""
        return self.threads.get(thread_id)

    def get_state(self, thread_id: str) -> Optional[ConversationState]:
        """Get conversation state by thread ID."""
        return self.states.get(thread_id)

    def send_message(
        self,
        thread_id: str,
        sender: str,
        content: str,
        type: MessageType = MessageType.MESSAGE,
        recipient: Optional[str] = None,
        in_reply_to: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> Optional[ConversationMessage]:
        """Send a message to a thread."""
        thread = self.get_thread(thread_id)
        if not thread or not thread.is_active:
            return None

        message = thread.add_message(
            sender=sender,
            content=content,
            type=type,
            recipient=recipient,
            in_reply_to=in_reply_to,
            metadata=metadata,
        )

        # Update state
        state = self.get_state(thread_id)
        if state:
            state.add_message(message.to_dict())
            state.add_participant(sender)
            if recipient:
                state.add_participant(recipient)

        return message

    def get_agent_threads(self, agent_id: str) -> List[MessageThread]:
        """Get all threads for an agent."""
        thread_ids = self.agent_threads.get(agent_id, [])
        return [self.threads[tid] for tid in thread_ids if tid in self.threads]

    def get_active_threads(self, agent_id: Optional[str] = None) -> List[MessageThread]:
        """Get active threads, optionally filtered by agent."""
        threads = [t for t in self.threads.values() if t.is_active]
        if agent_id:
            threads = [t for t in threads if agent_id in t.participants]
        return threads

    def close_thread(self, thread_id: str) -> bool:
        """Close a thread."""
        thread = self.get_thread(thread_id)
        if not thread:
            return False

        thread.close()

        state = self.get_state(thread_id)
        if state:
            state.complete()

        return True

    def archive_thread(self, thread_id: str) -> bool:
        """Archive a thread."""
        state = self.get_state(thread_id)
        if not state:
            return False

        state.archive()
        return True

    def get_thread_history(
        self,
        thread_id: str,
        limit: Optional[int] = None,
    ) -> List[ConversationMessage]:
        """Get message history for a thread."""
        thread = self.get_thread(thread_id)
        if not thread:
            return []
        return thread.get_messages(limit=limit)

    def search_messages(
        self,
        query: str,
        agent_id: Optional[str] = None,
        limit: int = 50,
    ) -> List[ConversationMessage]:
        """Search messages by content."""
        results = []

        threads = self.get_active_threads(agent_id) if agent_id else self.threads.values()

        for thread in threads:
            for msg in thread.messages:
                if query.lower() in msg.content.lower():
                    results.append(msg)
                    if len(results) >= limit:
                        return results

        return results

    def get_stats(self) -> Dict[str, Any]:
        """Get conversation statistics."""
        total_threads = len(self.threads)
        active_threads = len([t for t in self.threads.values() if t.is_active])
        total_messages = sum(len(t.messages) for t in self.threads.values())

        return {
            "total_threads": total_threads,
            "active_threads": active_threads,
            "archived_threads": total_threads - active_threads,
            "total_messages": total_messages,
            "total_participants": len(self.agent_threads),
            "avg_messages_per_thread": total_messages / total_threads if total_threads > 0 else 0,
        }
