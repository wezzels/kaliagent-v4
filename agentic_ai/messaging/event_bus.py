"""
Event Bus - Event Streaming for Agents
========================================

Provides event streaming with support for event sourcing,
event handlers, and event filtering.
"""

import json
import logging
from dataclasses import dataclass, field, asdict
from datetime import datetime
from enum import Enum
from typing import Any, Callable, Dict, List, Optional, Type, TypeVar
from functools import wraps

import redis

logger = logging.getLogger(__name__)

E = TypeVar('E', bound='Event')


class EventPriority(Enum):
    """Event priority levels."""
    LOW = 1
    NORMAL = 5
    HIGH = 8
    CRITICAL = 10


@dataclass
class Event:
    """Event structure for agent event streaming."""
    event_id: str
    event_type: str
    source: str
    data: Dict[str, Any]
    timestamp: datetime = field(default_factory=datetime.utcnow)
    priority: EventPriority = EventPriority.NORMAL
    correlation_id: Optional[str] = None
    causation_id: Optional[str] = None  # ID of event that caused this one
    version: int = 1

    def to_json(self) -> str:
        """Serialize event to JSON."""
        data = asdict(self)
        data['timestamp'] = self.timestamp.isoformat()
        data['priority'] = self.priority.value
        return json.dumps(data)

    @classmethod
    def from_json(cls, json_str: str) -> 'Event':
        """Deserialize event from JSON."""
        data = json.loads(json_str)
        data['timestamp'] = datetime.fromisoformat(data['timestamp'])
        data['priority'] = EventPriority(data['priority'])
        return cls(**data)

    def with_causation(self, cause_event: 'Event') -> 'Event':
        """Create new event with causation from this event."""
        self.causation_id = cause_event.event_id
        self.correlation_id = cause_event.correlation_id or cause_event.event_id
        return self


# Type for event handlers
EventHandler = Callable[[Event], None]


class EventBus:
    """
    Redis-based event bus for agent event streaming.

    Supports:
    - Event publishing with priority
    - Event handlers with filtering
    - Event sourcing (append-only log)
    - Event replay
    - Dead letter events
    """

    def __init__(
        self,
        redis_url: str = "redis://localhost:6379",
        stream_prefix: str = "events",
        event_log_key: str = "event_log",
    ):
        """
        Initialize event bus.

        Args:
            redis_url: Redis connection URL
            stream_prefix: Prefix for event streams
            event_log_key: Key for append-only event log
        """
        self.redis_url = redis_url
        self.stream_prefix = stream_prefix
        self.event_log_key = event_log_key
        self._redis: Optional[redis.Redis] = None
        self._handlers: Dict[str, List[EventHandler]] = {}
        self._running = False

    def connect(self) -> None:
        """Connect to Redis."""
        self._redis = redis.from_url(
            self.redis_url,
            decode_responses=True,
            socket_connect_timeout=5,
        )
        logger.info(f"EventBus connected to Redis: {self.redis_url}")

    def disconnect(self) -> None:
        """Disconnect from Redis."""
        self._running = False
        if self._redis:
            self._redis.close()
        logger.info("EventBus disconnected")

    def _get_stream_key(self, event_type: str) -> str:
        """Get stream key for event type."""
        return f"{self.stream_prefix}:{event_type}"

    def publish(self, event: Event) -> bool:
        """
        Publish event to stream and append to log.

        Args:
            event: Event to publish

        Returns:
            True if published successfully
        """
        if not self._redis:
            self.connect()

        try:
            # Add to event stream
            stream_key = self._get_stream_key(event.event_type)
            event_data = event.to_json()

            # Add to typed stream
            self._redis.xadd(stream_key, {'data': event_data}, maxlen=10000)

            # Add to global event log (for event sourcing)
            self._redis.xadd(
                self.event_log_key,
                {'event_type': event.event_type, 'data': event_data},
                maxlen=100000
            )

            logger.debug(f"Published event {event.event_id} to {stream_key}")
            return True
        except Exception as e:
            logger.error(f"Failed to publish event: {e}")
            return False

    def emit(self, event_type: str, data: Dict[str, Any], source: str, **kwargs) -> Event:
        """
        Convenience method to create and publish event.

        Args:
            event_type: Type of event
            data: Event data
            source: Event source
            **kwargs: Additional event fields

        Returns:
            Published event
        """
        import uuid

        event = Event(
            event_id=str(uuid.uuid4()),
            event_type=event_type,
            source=source,
            data=data,
            **kwargs
        )

        self.publish(event)
        return event

    def subscribe(self, event_type: str, handler: EventHandler) -> None:
        """
        Subscribe to event type with handler.

        Args:
            event_type: Event type to subscribe to (use '*' for all)
            handler: Handler function
        """
        if event_type not in self._handlers:
            self._handlers[event_type] = []

        self._handlers[event_type].append(handler)
        logger.info(f"Subscribed handler to {event_type}")

    def unsubscribe(self, event_type: str, handler: EventHandler) -> None:
        """
        Unsubscribe handler from event type.

        Args:
            event_type: Event type
            handler: Handler to remove
        """
        if event_type in self._handlers:
            self._handlers[event_type].remove(handler)
            logger.info(f"Unsubscribed handler from {event_type}")

    def handle_events(self, event_types: Optional[List[str]] = None, block_ms: int = 1000) -> None:
        """
        Process events from streams (blocking).

        Args:
            event_types: Event types to process (None for all subscribed)
            block_ms: Block timeout in milliseconds
        """
        if not self._redis:
            self.connect()

        self._running = True

        # Determine which streams to read
        if event_types:
            streams = {self._get_stream_key(et): '0' for et in event_types}
        else:
            streams = {self._get_stream_key(et): '0' for et in self._handlers.keys()}

        while self._running:
            try:
                # Read from streams
                messages = self._redis.xread(streams, count=10, block=block_ms)

                if not messages:
                    continue

                for stream_name, stream_messages in messages:
                    for message_id, message_data in stream_messages:
                        self._process_message(stream_name, message_id, message_data)

                        # Update last read ID
                        streams[stream_name] = message_id

            except Exception as e:
                logger.error(f"Error processing events: {e}")

    def _process_message(self, stream_name: str, message_id: str, message_data: dict) -> None:
        """Process single message from stream."""
        try:
            event = Event.from_json(message_data['data'])
            event_type = stream_name.replace(f"{self.stream_prefix}:", "")

            # Call specific handlers
            handlers = self._handlers.get(event_type, [])
            handlers.extend(self._handlers.get('*', []))  # Wildcard handlers

            for handler in handlers:
                try:
                    handler(event)
                except Exception as e:
                    logger.error(f"Handler error for {event.event_id}: {e}")
        except Exception as e:
            logger.error(f"Failed to process message {message_id}: {e}")

    def replay_events(
        self,
        event_type: str,
        handler: EventHandler,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None,
        count: Optional[int] = None,
    ) -> int:
        """
        Replay historical events to handler.

        Args:
            event_type: Event type to replay
            handler: Handler to call for each event
            start_time: Start time filter (None for beginning)
            end_time: End time filter (None for now)
            count: Max events to replay (None for all)

        Returns:
            Number of events replayed
        """
        if not self._redis:
            self.connect()

        stream_key = self._get_stream_key(event_type)

        # Build query
        start = '-' if not start_time else start_time.timestamp() * 1000
        end = '+' if not end_time else end_time.timestamp() * 1000

        # Read historical events
        events = self._redis.xrange(stream_key, min=start, max=end, count=count)

        replayed = 0
        for message_id, message_data in events:
            try:
                event = Event.from_json(message_data['data'])
                handler(event)
                replayed += 1
            except Exception as e:
                logger.error(f"Failed to replay event {message_id}: {e}")

        logger.info(f"Replayed {replayed} events for {event_type}")
        return replayed

    def get_event_history(
        self,
        correlation_id: str,
        limit: int = 100,
    ) -> List[Event]:
        """
        Get event history for correlation ID (event chain).

        Args:
            correlation_id: Correlation ID to trace
            limit: Max events to return

        Returns:
            List of events in order
        """
        if not self._redis:
            self.connect()

        events = []
        start_time = datetime.utcnow() - timedelta(days=7)  # Last 7 days

        stream_messages = self._redis.xrange(
            self.event_log_key,
            min=start_time.timestamp() * 1000,
            max='+',
            count=limit
        )

        for _, message_data in stream_messages:
            try:
                event = Event.from_json(message_data['data'])
                if event.correlation_id == correlation_id:
                    events.append(event)
            except Exception:
                continue

        return events

    def get_event_count(self, event_type: str) -> int:
        """Get count of events for type."""
        if not self._redis:
            return 0

        return self._redis.xlen(self._get_stream_key(event_type))

    def trim_stream(self, event_type: str, max_length: int) -> None:
        """Trim event stream to max length."""
        if not self._redis:
            return

        self._redis.xtrim(self._get_stream_key(event_type), maxlen=max_length)
        logger.info(f"Trimmed {event_type} stream to {max_length}")


# Event decorator for easy handler registration

def on_event(event_type: str):
    """
    Decorator to register event handler.

    Usage:
        @on_event('user.created')
        def handle_user_created(event: Event):
            print(f"User created: {event.data}")
    """
    def decorator(func: EventHandler) -> EventHandler:
        @wraps(func)
        def wrapper(event: Event):
            return func(event)

        # Store event type for later registration
        wrapper._event_type = event_type  # type: ignore
        return wrapper
    return decorator


# Import timedelta for replay_events
from datetime import timedelta
