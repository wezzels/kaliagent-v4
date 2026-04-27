"""
Agent Protocol - Inter-Agent Communication
===========================================

Defines the protocol for agent-to-agent communication
using the message bus and event bus.
"""

import json
import logging
import uuid
from dataclasses import dataclass, field, asdict
from datetime import datetime
from enum import Enum
from typing import Any, Callable, Dict, List, Optional, Type, TypeVar
from abc import ABC, abstractmethod

from .message_bus import MessageBus, Message, MessageType
from .event_bus import EventBus, Event, EventPriority

logger = logging.getLogger(__name__)

A = TypeVar('A', bound='AgentProtocol')


class AgentCapability:
    """Agent capability definition."""

    def __init__(
        self,
        name: str,
        description: str,
        input_schema: Dict[str, Any],
        output_schema: Dict[str, Any],
    ):
        self.name = name
        self.description = description
        self.input_schema = input_schema
        self.output_schema = output_schema

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            'name': self.name,
            'description': self.description,
            'input_schema': self.input_schema,
            'output_schema': self.output_schema,
        }


@dataclass
class AgentMessage:
    """Structured message between agents."""
    message_id: str
    sender_agent: str
    receiver_agent: Optional[str]
    action: str
    parameters: Dict[str, Any]
    timestamp: datetime = field(default_factory=datetime.utcnow)
    correlation_id: Optional[str] = None
    reply_to: Optional[str] = None
    priority: int = 5
    ttl_seconds: int = 3600

    def to_message(self) -> Message:
        """Convert to MessageBus message."""
        return Message(
            message_id=self.message_id,
            message_type=MessageType.REQUEST,
            source_agent=self.sender_agent,
            target_agent=self.receiver_agent,
            topic=f"agent.{self.receiver_agent or 'broadcast'}",
            payload={
                'action': self.action,
                'parameters': self.parameters,
            },
            correlation_id=self.correlation_id,
            reply_to=self.reply_to,
            ttl_seconds=self.ttl_seconds,
            priority=self.priority,
        )

    @classmethod
    def from_message(cls, message: Message) -> 'AgentMessage':
        """Create from MessageBus message."""
        return cls(
            message_id=message.message_id,
            sender_agent=message.source_agent,
            receiver_agent=message.target_agent,
            action=message.payload.get('action', 'unknown'),
            parameters=message.payload.get('parameters', {}),
            timestamp=message.timestamp,
            correlation_id=message.correlation_id,
            reply_to=message.reply_to,
            priority=message.priority,
            ttl_seconds=message.ttl_seconds,
        )


class AgentProtocol(ABC):
    """
    Base class for agent communication protocol.

    Provides:
    - Message bus integration
    - Event bus integration
    - Request/response handling
    - Capability registration
    - Health monitoring
    """

    def __init__(
        self,
        agent_id: str,
        agent_type: str,
        redis_url: str = "redis://localhost:6379",
    ):
        """
        Initialize agent protocol.

        Args:
            agent_id: Unique agent identifier
            agent_type: Type of agent
            redis_url: Redis connection URL
        """
        self.agent_id = agent_id
        self.agent_type = agent_type
        self.redis_url = redis_url

        self._message_bus: Optional[MessageBus] = None
        self._event_bus: Optional[EventBus] = None
        self._capabilities: Dict[str, AgentCapability] = {}
        self._handlers: Dict[str, Callable] = {}
        self._running = False
        self._last_heartbeat = datetime.utcnow()

    def connect(self) -> None:
        """Connect to message and event buses."""
        self._message_bus = MessageBus(redis_url=self.redis_url)
        self._message_bus.connect()

        self._event_bus = EventBus(redis_url=self.redis_url)
        self._event_bus.connect()

        # Subscribe to agent messages
        self._message_bus.subscribe(
            f"agent.{self.agent_id}",
            self._handle_message,
        )

        logger.info(f"Agent {self.agent_id} connected")

    def disconnect(self) -> None:
        """Disconnect from buses."""
        self._running = False

        if self._message_bus:
            self._message_bus.disconnect()
        if self._event_bus:
            self._event_bus.disconnect()

        logger.info(f"Agent {self.agent_id} disconnected")

    def register_capability(self, capability: AgentCapability, handler: Callable) -> None:
        """
        Register agent capability with handler.

        Args:
            capability: Capability definition
            handler: Handler function
        """
        self._capabilities[capability.name] = capability
        self._handlers[capability.name] = handler
        logger.info(f"Registered capability: {capability.name}")

    def get_capabilities(self) -> List[Dict[str, Any]]:
        """Get list of registered capabilities."""
        return [cap.to_dict() for cap in self._capabilities.values()]

    def send_message(self, message: AgentMessage) -> bool:
        """
        Send message to another agent.

        Args:
            message: Message to send

        Returns:
            True if sent successfully
        """
        if not self._message_bus:
            self.connect()

        return self._message_bus.publish(message.to_message())

    def request(
        self,
        target_agent: str,
        action: str,
        parameters: Dict[str, Any],
        timeout_seconds: int = 30,
    ) -> Optional[Dict[str, Any]]:
        """
        Send request to agent and wait for response.

        Args:
            target_agent: Target agent ID
            action: Action to invoke
            parameters: Action parameters
            timeout_seconds: Response timeout

        Returns:
            Response data or None
        """
        message = AgentMessage(
            message_id=str(uuid.uuid4()),
            sender_agent=self.agent_id,
            receiver_agent=target_agent,
            action=action,
            parameters=parameters,
        )

        if not self._message_bus:
            self.connect()

        response = self._message_bus.request(message.to_message(), timeout_seconds)

        if response:
            return response.payload
        return None

    def broadcast(
        self,
        action: str,
        parameters: Dict[str, Any],
    ) -> bool:
        """
        Broadcast message to all agents.

        Args:
            action: Action name
            parameters: Action parameters

        Returns:
            True if broadcast successful
        """
        message = AgentMessage(
            message_id=str(uuid.uuid4()),
            sender_agent=self.agent_id,
            receiver_agent=None,  # Broadcast
            action=action,
            parameters=parameters,
        )

        return self.send_message(message)

    def emit_event(
        self,
        event_type: str,
        data: Dict[str, Any],
        priority: EventPriority = EventPriority.NORMAL,
    ) -> Event:
        """
        Emit event to event bus.

        Args:
            event_type: Type of event
            data: Event data
            priority: Event priority

        Returns:
            Emitted event
        """
        if not self._event_bus:
            self.connect()

        return self._event_bus.emit(
            event_type=event_type,
            data=data,
            source=self.agent_id,
            priority=priority,
        )

    def subscribe_to_agent(self, agent_id: str, callback: Callable[[AgentMessage], None]) -> None:
        """
        Subscribe to messages from specific agent.

        Args:
            agent_id: Agent to subscribe to
            callback: Message handler
        """
        def wrapper(message: Message):
            agent_message = AgentMessage.from_message(message)
            callback(agent_message)

        if self._message_bus:
            self._message_bus.subscribe(f"agent.{agent_id}", wrapper)

    def _handle_message(self, message: Message) -> None:
        """Handle incoming message."""
        try:
            agent_message = AgentMessage.from_message(message)

            # Check if we have handler for this action
            if agent_message.action in self._handlers:
                handler = self._handlers[agent_message.action]

                try:
                    # Execute handler
                    result = handler(agent_message.parameters)

                    # Send response if request
                    if message.reply_to:
                        self._send_response(message, result)

                    # Emit event for successful execution
                    self.emit_event(
                        f"agent.action.completed.{agent_message.action}",
                        {
                            'agent_id': self.agent_id,
                            'action': agent_message.action,
                            'message_id': agent_message.message_id,
                            'result': result,
                        },
                    )

                except Exception as e:
                    logger.error(f"Handler error: {e}")

                    if message.reply_to:
                        self._send_error_response(message, str(e))

                    self.emit_event(
                        f"agent.action.failed.{agent_message.action}",
                        {
                            'agent_id': self.agent_id,
                            'action': agent_message.action,
                            'message_id': agent_message.message_id,
                            'error': str(e),
                        },
                    )
            else:
                logger.warning(f"No handler for action: {agent_message.action}")

        except Exception as e:
            logger.error(f"Failed to handle message: {e}")

    def _send_response(self, original_message: Message, result: Any) -> bool:
        """Send response to original request."""
        if not self._message_bus:
            return False

        return self._message_bus.respond(original_message, {
            'status': 'success',
            'result': result,
            'agent_id': self.agent_id,
        })

    def _send_error_response(self, original_message: Message, error: str) -> bool:
        """Send error response."""
        if not self._message_bus:
            return False

        return self._message_bus.respond(original_message, {
            'status': 'error',
            'error': error,
            'agent_id': self.agent_id,
        })

    def send_heartbeat(self) -> None:
        """Send heartbeat event."""
        self._last_heartbeat = datetime.utcnow()

        self.emit_event(
            'agent.heartbeat',
            {
                'agent_id': self.agent_id,
                'agent_type': self.agent_type,
                'timestamp': self._last_heartbeat.isoformat(),
                'capabilities': list(self._capabilities.keys()),
            },
            priority=EventPriority.LOW,
        )

    def get_status(self) -> Dict[str, Any]:
        """Get agent status."""
        return {
            'agent_id': self.agent_id,
            'agent_type': self.agent_type,
            'running': self._running,
            'last_heartbeat': self._last_heartbeat.isoformat(),
            'capabilities': list(self._capabilities.keys()),
        }

    @abstractmethod
    def initialize(self) -> None:
        """Initialize agent-specific resources."""
        pass

    @abstractmethod
    def shutdown(self) -> None:
        """Shutdown agent gracefully."""
        pass

    def run(self) -> None:
        """Run agent main loop."""
        self._running = True
        self.initialize()

        heartbeat_interval = 30  # seconds
        last_heartbeat = datetime.utcnow()

        logger.info(f"Agent {self.agent_id} started")

        try:
            while self._running:
                # Send periodic heartbeat
                if (datetime.utcnow() - last_heartbeat).total_seconds() > heartbeat_interval:
                    self.send_heartbeat()
                    last_heartbeat = datetime.utcnow()

                # Process messages (non-blocking)
                if self._message_bus:
                    # In real implementation, this would be event-driven
                    pass

                # Small sleep to prevent busy waiting
                import time
                time.sleep(1)

        except KeyboardInterrupt:
            logger.info(f"Agent {self.agent_id} interrupted")
        finally:
            self.shutdown()
            self.disconnect()


# Agent registry for service discovery

class AgentRegistry:
    """
    Agent registry for service discovery.

    Tracks available agents and their capabilities.
    """

    def __init__(self, redis_url: str = "redis://localhost:6379"):
        self.redis_url = redis_url
        self._redis: Optional[redis.Redis] = None
        self._registry_key = "agent_registry"

    def connect(self) -> None:
        """Connect to Redis."""
        import redis
        self._redis = redis.from_url(self.redis_url, decode_responses=True)

    def register_agent(self, agent_id: str, agent_type: str, capabilities: List[Dict[str, Any]]) -> None:
        """Register agent in registry."""
        if not self._redis:
            self.connect()

        agent_data = {
            'agent_id': agent_id,
            'agent_type': agent_type,
            'capabilities': json.dumps(capabilities),
            'registered_at': datetime.utcnow().isoformat(),
            'last_heartbeat': datetime.utcnow().isoformat(),
        }

        self._redis.hset(self._registry_key, agent_id, json.dumps(agent_data))

    def deregister_agent(self, agent_id: str) -> None:
        """Remove agent from registry."""
        if self._redis:
            self._redis.hdel(self._registry_key, agent_id)

    def update_heartbeat(self, agent_id: str) -> None:
        """Update agent heartbeat timestamp."""
        if not self._redis:
            return

        data = self._redis.hget(self._registry_key, agent_id)
        if data:
            agent_data = json.loads(data)
            agent_data['last_heartbeat'] = datetime.utcnow().isoformat()
            self._redis.hset(self._registry_key, agent_id, json.dumps(agent_data))

    def get_agent(self, agent_id: str) -> Optional[Dict[str, Any]]:
        """Get agent by ID."""
        if not self._redis:
            return None

        data = self._redis.hget(self._registry_key, agent_id)
        return json.loads(data) if data else None

    def get_agents_by_type(self, agent_type: str) -> List[Dict[str, Any]]:
        """Get all agents of specific type."""
        if not self._redis:
            return []

        agents = []
        all_agents = self._redis.hgetall(self._registry_key)

        for agent_data in all_agents.values():
            data = json.loads(agent_data)
            if data.get('agent_type') == agent_type:
                agents.append(data)

        return agents

    def get_all_agents(self) -> List[Dict[str, Any]]:
        """Get all registered agents."""
        if not self._redis:
            return []

        agents = []
        all_agents = self._redis.hgetall(self._registry_key)

        for agent_data in all_agents.values():
            agents.append(json.loads(agent_data))

        return agents

    def find_agents_by_capability(self, capability_name: str) -> List[Dict[str, Any]]:
        """Find agents that have specific capability."""
        if not self._redis:
            return []

        agents = []
        all_agents = self._redis.hgetall(self._registry_key)

        for agent_data in all_agents.values():
            data = json.loads(agent_data)
            capabilities = json.loads(data.get('capabilities', '[]'))

            if any(cap.get('name') == capability_name for cap in capabilities):
                agents.append(data)

        return agents

    def cleanup_stale_agents(self, max_age_seconds: int = 300) -> int:
        """Remove agents that haven't sent heartbeat recently."""
        if not self._redis:
            return 0

        cutoff = datetime.utcnow() - timedelta(seconds=max_age_seconds)
        removed = 0

        all_agents = self._redis.hgetall(self._registry_key)

        for agent_id, agent_data in all_agents.items():
            data = json.loads(agent_data)
            last_heartbeat = datetime.fromisoformat(data.get('last_heartbeat', ''))

            if last_heartbeat < cutoff:
                self._redis.hdel(self._registry_key, agent_id)
                removed += 1

        if removed > 0:
            logger.info(f"Cleaned up {removed} stale agents")

        return removed


# Import timedelta
from datetime import timedelta
