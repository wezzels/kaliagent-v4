"""
Messaging Integration Tests
===========================

Integration tests for event-driven architecture:
- Message bus (pub/sub)
- Event bus (event streaming)
- Task queue (distributed tasks)
- Agent protocol (inter-agent communication)
"""

import pytest
import time
from datetime import datetime, timedelta
from unittest.mock import Mock, patch, MagicMock
from typing import List

from agentic_ai.messaging.message_bus import MessageBus, Message, MessageType
from agentic_ai.messaging.event_bus import EventBus, Event, EventPriority, on_event
from agentic_ai.messaging.task_queue import TaskQueue, Task, TaskStatus
from agentic_ai.messaging.agent_protocol import AgentProtocol, AgentMessage, AgentCapability, AgentRegistry


# ============================================================================
# Message Bus Tests
# ============================================================================

class TestMessageBus:
    """Test MessageBus functionality."""
    
    @patch('redis.Redis')
    def test_message_serialization(self, mock_redis):
        """Test message JSON serialization."""
        message = Message(
            message_id="test-123",
            message_type=MessageType.EVENT,
            source_agent="test-agent",
            target_agent=None,
            topic="test.topic",
            payload={'key': 'value'},
            priority=8,
        )
        
        json_str = message.to_json()
        assert 'test-123' in json_str
        assert 'event' in json_str
        
        # Deserialize
        restored = Message.from_json(json_str)
        assert restored.message_id == message.message_id
        assert restored.message_type == MessageType.EVENT
        assert restored.payload == {'key': 'value'}
    
    @patch('redis.Redis')
    def test_message_bus_publish(self, mock_redis):
        """Test publishing messages."""
        bus = MessageBus(redis_url="redis://localhost:6379")
        bus._redis = mock_redis
        
        message = Message(
            message_id="test-123",
            message_type=MessageType.EVENT,
            source_agent="test-agent",
            target_agent=None,
            topic="test.topic",
            payload={'data': 'test'},
        )
        
        result = bus.publish(message)
        
        assert result is True
        mock_redis.publish.assert_called_once()
    
    @patch('redis.Redis')
    def test_message_bus_subscribe(self, mock_redis):
        """Test subscribing to topics."""
        bus = MessageBus(redis_url="redis://localhost:6379")
        bus._redis = mock_redis
        bus._pubsub = mock_redis.pubsub()
        
        callback = Mock()
        bus.subscribe("test.topic", callback)
        
        assert "test.topic" in bus._subscribers
        assert callback in bus._subscribers["test.topic"]
    
    @patch('redis.Redis')
    def test_message_bus_request_response(self, mock_redis):
        """Test request/response pattern."""
        bus = MessageBus(redis_url="redis://localhost:6379")
        bus._redis = mock_redis
        
        # Setup mock for response
        mock_pubsub = Mock()
        mock_pubsub.get_message.return_value = {
            'type': 'message',
            'data': Message(
                message_id="resp-123",
                message_type=MessageType.RESPONSE,
                source_agent="responder",
                target_agent="requester",
                topic="reply.test",
                payload={'result': 'success'},
            ).to_json(),
        }
        mock_redis.pubsub.return_value = mock_pubsub
        
        request = Message(
            message_id="req-123",
            message_type=MessageType.REQUEST,
            source_agent="requester",
            target_agent="responder",
            topic="request.topic",
            payload={'action': 'test'},
        )
        
        response = bus.request(request, timeout_seconds=5)
        
        assert response is not None
        assert response.payload['result'] == 'success'
    
    @patch('redis.Redis')
    def test_dead_letter_queue(self, mock_redis):
        """Test dead letter queue handling."""
        bus = MessageBus(redis_url="redis://localhost:6379")
        bus._redis = mock_redis
        
        message = Message(
            message_id="fail-123",
            message_type=MessageType.EVENT,
            source_agent="test-agent",
            target_agent=None,
            topic="test.topic",
            payload={},
        )
        
        # Simulate DLQ send
        bus._send_to_dlq(message, "Test error")
        
        mock_redis.lpush.assert_called_once()
    
    @patch('redis.Redis')
    def test_dlq_retry(self, mock_redis):
        """Test retrying messages from DLQ."""
        bus = MessageBus(redis_url="redis://localhost:6379")
        bus._redis = mock_redis
        
        # Mock DLQ message
        original_message = Message(
            message_id="retry-123",
            message_type=MessageType.EVENT,
            source_agent="test-agent",
            target_agent=None,
            topic="test.topic",
            payload={},
        )
        
        dlq_message = {
            'original_message': original_message.to_json(),
            'error': 'Test error',
            'timestamp': datetime.utcnow().isoformat(),
        }
        
        mock_redis.lrange.return_value = [str(dlq_message)]
        
        result = bus.retry_dlq_message(0)
        
        # Should republish original message
        assert mock_redis.publish.called


# ============================================================================
# Event Bus Tests
# ============================================================================

class TestEventBus:
    """Test EventBus functionality."""
    
    @patch('redis.Redis')
    def test_event_serialization(self, mock_redis):
        """Test event JSON serialization."""
        event = Event(
            event_id="event-123",
            event_type="user.created",
            source="user-service",
            data={'user_id': '123', 'email': 'test@example.com'},
            priority=EventPriority.HIGH,
        )
        
        json_str = event.to_json()
        assert 'event-123' in json_str
        assert 'user.created' in json_str
        
        # Deserialize
        restored = Event.from_json(json_str)
        assert restored.event_id == event.event_id
        assert restored.event_type == "user.created"
        assert restored.priority == EventPriority.HIGH
    
    @patch('redis.Redis')
    def test_event_publish(self, mock_redis):
        """Test publishing events."""
        bus = EventBus(redis_url="redis://localhost:6379")
        bus._redis = mock_redis
        
        event = Event(
            event_id="event-123",
            event_type="test.event",
            source="test-service",
            data={'key': 'value'},
        )
        
        result = bus.publish(event)
        
        assert result is True
        mock_redis.xadd.assert_called()
    
    @patch('redis.Redis')
    def test_event_emit(self, mock_redis):
        """Test emitting events with convenience method."""
        bus = EventBus(redis_url="redis://localhost:6379")
        bus._redis = mock_redis
        
        event = bus.emit(
            event_type="order.created",
            data={'order_id': '123', 'total': 99.99},
            source="order-service",
            priority=EventPriority.HIGH,
        )
        
        assert event.event_type == "order.created"
        assert event.data['order_id'] == '123'
        assert event.priority == EventPriority.HIGH
    
    @patch('redis.Redis')
    def test_event_subscribe(self, mock_redis):
        """Test subscribing to events."""
        bus = EventBus(redis_url="redis://localhost:6379")
        bus._redis = mock_redis
        
        handler = Mock()
        bus.subscribe("user.created", handler)
        
        assert "user.created" in bus._handlers
    
    @patch('redis.Redis')
    def test_event_decorator(self, mock_redis):
        """Test event handler decorator."""
        bus = EventBus(redis_url="redis://localhost:6379")
        bus._redis = mock_redis
        
        @on_event('test.event')
        def handle_test_event(event: Event):
            return event.data
        
        # Verify decorator sets event type
        assert hasattr(handle_test_event, '_event_type')
        assert handle_test_event._event_type == 'test.event'
    
    @patch('redis.Redis')
    def test_event_replay(self, mock_redis):
        """Test replaying historical events."""
        bus = EventBus(redis_url="redis://localhost:6379")
        bus._redis = mock_redis
        
        # Mock historical events
        mock_events = [
            (b'1', {'data': Event(
                event_id="event-1",
                event_type="test.event",
                source="test",
                data={'seq': 1},
            ).to_json()}),
            (b'2', {'data': Event(
                event_id="event-2",
                event_type="test.event",
                source="test",
                data={'seq': 2},
            ).to_json()}),
        ]
        
        mock_redis.xrange.return_value = mock_events
        
        handler = Mock()
        count = bus.replay_events("test.event", handler)
        
        assert count == 2
        assert handler.call_count == 2
    
    @patch('redis.Redis')
    def test_event_history(self, mock_redis):
        """Test getting event history by correlation ID."""
        bus = EventBus(redis_url="redis://localhost:6379")
        bus._redis = mock_redis
        
        correlation_id = "corr-123"
        
        # Mock events with correlation
        mock_events = [
            (b'1', {'data': Event(
                event_id="event-1",
                event_type="order.created",
                source="order-service",
                data={},
                correlation_id=correlation_id,
            ).to_json()}),
        ]
        
        mock_redis.xrange.return_value = mock_events
        
        events = bus.get_event_history(correlation_id)
        
        assert len(events) == 1
        assert events[0].correlation_id == correlation_id


# ============================================================================
# Task Queue Tests
# ============================================================================

class TestTaskQueue:
    """Test TaskQueue functionality."""
    
    @patch('redis.Redis')
    def test_task_serialization(self, mock_redis):
        """Test task JSON serialization."""
        task = Task(
            task_id="task-123",
            task_type="email.send",
            payload={'to': 'test@example.com', 'subject': 'Test'},
            priority=8,
            max_retries=3,
        )
        
        json_str = task.to_json()
        assert 'task-123' in json_str
        assert 'email.send' in json_str
        
        # Deserialize
        restored = Task.from_json(json_str)
        assert restored.task_id == task.task_id
        assert restored.task_type == "email.send"
        assert restored.status == TaskStatus.PENDING
    
    @patch('redis.Redis')
    def test_task_enqueue(self, mock_redis):
        """Test enqueueing tasks."""
        queue = TaskQueue(redis_url="redis://localhost:6379")
        queue._redis = mock_redis
        
        task = queue.enqueue(
            task_type="email.send",
            payload={'to': 'test@example.com'},
            priority=8,
            delay_seconds=0,
        )
        
        assert task.task_id.startswith("task-")
        assert task.status == TaskStatus.PENDING
        mock_redis.zadd.assert_called()
    
    @patch('redis.Redis')
    def test_task_enqueue_delayed(self, mock_redis):
        """Test enqueueing delayed tasks."""
        queue = TaskQueue(redis_url="redis://localhost:6379")
        queue._redis = mock_redis
        
        task = queue.enqueue(
            task_type="report.generate",
            payload={'report_id': '123'},
            delay_seconds=300,  # 5 minutes
        )
        
        assert task.scheduled_at is not None
        # Should be added to scheduled queue
        mock_redis.zadd.assert_called()
    
    @patch('redis.Redis')
    def test_task_register_handler(self, mock_redis):
        """Test registering task handlers."""
        queue = TaskQueue(redis_url="redis://localhost:6379")
        queue._redis = mock_redis
        
        @queue.register_handler('email.send')
        def send_email(payload):
            return True
        
        assert 'email.send' in queue._handlers
    
    @patch('redis.Redis')
    def test_task_decorator(self, mock_redis):
        """Test task decorator."""
        queue = TaskQueue(redis_url="redis://localhost:6379")
        queue._redis = mock_redis
        
        @queue.task('notification.send', priority=7)
        def send_notification(message: str):
            return True
        
        # Handler should be registered
        assert 'notification.send' in queue._handlers
    
    @patch('redis.Redis')
    def test_task_retry(self, mock_redis):
        """Test task retry with exponential backoff."""
        queue = TaskQueue(redis_url="redis://localhost:6379")
        queue._redis = mock_redis
        
        task = Task(
            task_id="task-123",
            task_type="test.task",
            payload={},
            retry_count=1,
            max_retries=3,
        )
        
        # Should be able to retry
        assert task.can_retry() is True
        
        # Simulate retry
        queue._retry_task(task)
        
        assert task.retry_count == 2
        assert task.status == TaskStatus.RETRYING
        assert task.scheduled_at is not None
    
    @patch('redis.Redis')
    def test_task_max_retries(self, mock_redis):
        """Test task fails after max retries."""
        queue = TaskQueue(redis_url="redis://localhost:6379")
        queue._redis = mock_redis
        
        task = Task(
            task_id="task-123",
            task_type="test.task",
            payload={},
            retry_count=3,
            max_retries=3,
        )
        
        # Should not be able to retry
        assert task.can_retry() is False
        
        # Should go to DLQ
        queue._send_to_dlq(task)
        mock_redis.lpush.assert_called()
    
    @patch('redis.Redis')
    def test_task_result(self, mock_redis):
        """Test getting task result."""
        queue = TaskQueue(redis_url="redis://localhost:6379")
        queue._redis = mock_redis
        
        # Mock stored result
        result_data = {
            'task_id': 'task-123',
            'status': 'completed',
            'result': {'success': True},
            'completed_at': datetime.utcnow().isoformat(),
        }
        mock_redis.get.return_value = str(result_data)
        
        result = queue.get_task_result('task-123')
        
        assert result is not None
        assert result['status'] == 'completed'
    
    @patch('redis.Redis')
    def test_batch_enqueue(self, mock_redis):
        """Test batch enqueueing."""
        queue = TaskQueue(redis_url="redis://localhost:6379")
        queue._redis = mock_redis
        
        tasks = [
            {'task_type': 'email.send', 'payload': {'to': 'a@example.com'}},
            {'task_type': 'email.send', 'payload': {'to': 'b@example.com'}},
            {'task_type': 'email.send', 'payload': {'to': 'c@example.com'}},
        ]
        
        created = queue.enqueue_batch(tasks)
        
        assert len(created) == 3
        assert all(t.task_id.startswith("task-") for t in created)


# ============================================================================
# Agent Protocol Tests
# ============================================================================

class TestAgentProtocol:
    """Test AgentProtocol functionality."""
    
    @patch('redis.Redis')
    def test_agent_capability_registration(self, mock_redis):
        """Test registering agent capabilities."""
        agent = AgentProtocol(
            agent_id="test-agent-1",
            agent_type="test",
            redis_url="redis://localhost:6379",
        )
        agent._redis = mock_redis
        
        capability = AgentCapability(
            name="query.database",
            description="Query database for information",
            input_schema={'query': {'type': 'string'}},
            output_schema={'results': {'type': 'array'}},
        )
        
        handler = Mock()
        agent.register_capability(capability, handler)
        
        assert "query.database" in agent._capabilities
        assert agent._handlers["query.database"] == handler
    
    @patch('redis.Redis')
    def test_agent_message_serialization(self, mock_redis):
        """Test agent message serialization."""
        message = AgentMessage(
            message_id="msg-123",
            sender_agent="agent-1",
            receiver_agent="agent-2",
            action="query.database",
            parameters={'query': 'SELECT * FROM users'},
        )
        
        # Convert to MessageBus message
        bus_message = message.to_message()
        
        assert bus_message.message_type == MessageType.REQUEST
        assert bus_message.topic == "agent.agent-2"
        assert bus_message.payload['action'] == "query.database"
    
    @patch('redis.Redis')
    def test_agent_request(self, mock_redis):
        """Test agent sending request."""
        agent = AgentProtocol(
            agent_id="agent-1",
            agent_type="test",
            redis_url="redis://localhost:6379",
        )
        agent._message_bus = Mock()
        
        # Mock response
        agent._message_bus.request.return_value = Message(
            message_id="resp-123",
            message_type=MessageType.RESPONSE,
            source_agent="agent-2",
            target_agent="agent-1",
            topic="reply.test",
            payload={'result': 'success'},
        )
        
        response = agent.request(
            target_agent="agent-2",
            action="query.database",
            parameters={'query': 'test'},
            timeout_seconds=30,
        )
        
        assert response is not None
        assert response['result'] == 'success'
    
    @patch('redis.Redis')
    def test_agent_broadcast(self, mock_redis):
        """Test agent broadcasting message."""
        agent = AgentProtocol(
            agent_id="agent-1",
            agent_type="test",
            redis_url="redis://localhost:6379",
        )
        agent._message_bus = Mock()
        
        result = agent.broadcast(
            action="system.announcement",
            parameters={'message': 'System maintenance at 2 AM'},
        )
        
        assert result is True
        agent._message_bus.publish.assert_called()
    
    @patch('redis.Redis')
    def test_agent_heartbeat(self, mock_redis):
        """Test agent heartbeat."""
        agent = AgentProtocol(
            agent_id="agent-1",
            agent_type="test",
            redis_url="redis://localhost:6379",
        )
        agent._event_bus = Mock()
        
        agent.send_heartbeat()
        
        assert agent._event_bus.emit.called
        event_args = agent._event_bus.emit.call_args
        assert event_args[1]['event_type'] == 'agent.heartbeat'
        assert event_args[1]['data']['agent_id'] == 'agent-1'
    
    @patch('redis.Redis')
    def test_agent_status(self, mock_redis):
        """Test getting agent status."""
        agent = AgentProtocol(
            agent_id="agent-1",
            agent_type="test",
            redis_url="redis://localhost:6379",
        )
        
        status = agent.get_status()
        
        assert status['agent_id'] == 'agent-1'
        assert status['agent_type'] == 'test'
        assert 'capabilities' in status


# ============================================================================
# Agent Registry Tests
# ============================================================================

class TestAgentRegistry:
    """Test AgentRegistry functionality."""
    
    @patch('redis.Redis')
    def test_agent_registration(self, mock_redis):
        """Test registering agent in registry."""
        registry = AgentRegistry(redis_url="redis://localhost:6379")
        registry._redis = mock_redis
        
        capabilities = [
            {'name': 'query.database', 'description': 'Query DB'},
            {'name': 'write.logs', 'description': 'Write logs'},
        ]
        
        registry.register_agent(
            agent_id="agent-1",
            agent_type="test",
            capabilities=capabilities,
        )
        
        mock_redis.hset.assert_called()
    
    @patch('redis.Redis')
    def test_get_agent_by_id(self, mock_redis):
        """Test getting agent by ID."""
        registry = AgentRegistry(redis_url="redis://localhost:6379")
        registry._redis = mock_redis
        
        agent_data = {
            'agent_id': 'agent-1',
            'agent_type': 'test',
            'capabilities': '[]',
            'last_heartbeat': datetime.utcnow().isoformat(),
        }
        mock_redis.hget.return_value = str(agent_data)
        
        agent = registry.get_agent('agent-1')
        
        assert agent is not None
        assert agent['agent_id'] == 'agent-1'
    
    @patch('redis.Redis')
    def test_get_agents_by_type(self, mock_redis):
        """Test getting agents by type."""
        registry = AgentRegistry(redis_url="redis://localhost:6379")
        registry._redis = mock_redis
        
        agents = [
            {'agent_id': 'agent-1', 'agent_type': 'security', 'capabilities': '[]'},
            {'agent_id': 'agent-2', 'agent_type': 'security', 'capabilities': '[]'},
            {'agent_id': 'agent-3', 'agent_type': 'audit', 'capabilities': '[]'},
        ]
        
        mock_redis.hgetall.return_value = {
            f'agent-{i}': str(agent) for i, agent in enumerate(agents, 1)
        }
        
        security_agents = registry.get_agents_by_type('security')
        
        assert len(security_agents) == 2
        assert all(a['agent_type'] == 'security' for a in security_agents)
    
    @patch('redis.Redis')
    def test_find_agents_by_capability(self, mock_redis):
        """Test finding agents by capability."""
        registry = AgentRegistry(redis_url="redis://localhost:6379")
        registry._redis = mock_redis
        
        agents = {
            'agent-1': str({
                'agent_id': 'agent-1',
                'agent_type': 'security',
                'capabilities': '[{"name": "scan.vulnerabilities"}]',
            }),
            'agent-2': str({
                'agent_id': 'agent-2',
                'agent_type': 'audit',
                'capabilities': '[{"name": "audit.controls"}]',
            }),
        }
        
        mock_redis.hgetall.return_value = agents
        
        agents_with_capability = registry.find_agents_by_capability('scan.vulnerabilities')
        
        assert len(agents_with_capability) == 1
        assert agents_with_capability[0]['agent_id'] == 'agent-1'
    
    @patch('redis.Redis')
    def test_cleanup_stale_agents(self, mock_redis):
        """Test cleaning up stale agents."""
        registry = AgentRegistry(redis_url="redis://localhost:6379")
        registry._redis = mock_redis
        
        old_agent = {
            'agent_id': 'old-agent',
            'agent_type': 'test',
            'last_heartbeat': (datetime.utcnow() - timedelta(minutes=10)).isoformat(),
        }
        
        new_agent = {
            'agent_id': 'new-agent',
            'agent_type': 'test',
            'last_heartbeat': datetime.utcnow().isoformat(),
        }
        
        mock_redis.hgetall.return_value = {
            'old-agent': str(old_agent),
            'new-agent': str(new_agent),
        }
        
        removed = registry.cleanup_stale_agents(max_age_seconds=300)
        
        assert removed == 1
        mock_redis.hdel.assert_called_with('agent_registry', 'old-agent')


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
