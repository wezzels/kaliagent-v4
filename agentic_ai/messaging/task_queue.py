"""
Task Queue - Distributed Task Processing
==========================================

Redis-based task queue for asynchronous task execution.
Supports delayed tasks, retries, and priority queues.
"""

import json
import logging
import time
import uuid
from dataclasses import dataclass, field, asdict
from datetime import datetime, timedelta
from enum import Enum
from typing import Any, Callable, Dict, List, Optional, TypeVar
from functools import wraps

import redis

logger = logging.getLogger(__name__)

R = TypeVar('R')


class TaskStatus(Enum):
    """Task status values."""
    PENDING = "pending"
    QUEUED = "queued"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    RETRYING = "retrying"
    CANCELLED = "cancelled"


@dataclass
class Task:
    """Task structure for queue processing."""
    task_id: str
    task_type: str
    payload: Dict[str, Any]
    status: TaskStatus = TaskStatus.PENDING
    priority: int = 5  # 1-10
    created_at: datetime = field(default_factory=datetime.utcnow)
    scheduled_at: Optional[datetime] = None
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    result: Optional[Any] = None
    error: Optional[str] = None
    retry_count: int = 0
    max_retries: int = 3
    timeout_seconds: int = 300
    queue_name: str = "default"

    def to_json(self) -> str:
        """Serialize task to JSON."""
        data = asdict(self)
        data['status'] = self.status.value
        data['created_at'] = self.created_at.isoformat()
        if self.scheduled_at:
            data['scheduled_at'] = self.scheduled_at.isoformat()
        if self.started_at:
            data['started_at'] = self.started_at.isoformat()
        if self.completed_at:
            data['completed_at'] = self.completed_at.isoformat()
        return json.dumps(data)

    @classmethod
    def from_json(cls, json_str: str) -> 'Task':
        """Deserialize task from JSON."""
        data = json.loads(json_str)
        data['status'] = TaskStatus(data['status'])
        data['created_at'] = datetime.fromisoformat(data['created_at'])
        if data.get('scheduled_at'):
            data['scheduled_at'] = datetime.fromisoformat(data['scheduled_at'])
        if data.get('started_at'):
            data['started_at'] = datetime.fromisoformat(data['started_at'])
        if data.get('completed_at'):
            data['completed_at'] = datetime.fromisoformat(data['completed_at'])
        return cls(**data)

    def can_retry(self) -> bool:
        """Check if task can be retried."""
        return self.retry_count < self.max_retries


T = TypeVar('T')


class TaskQueue:
    """
    Redis-based task queue for distributed task processing.

    Supports:
    - Priority queues
    - Delayed/scheduled tasks
    - Task retries with exponential backoff
    - Task timeouts
    - Dead letter queue for failed tasks
    - Task result storage
    """

    def __init__(
        self,
        redis_url: str = "redis://localhost:6379",
        queue_prefix: str = "tasks",
        result_ttl_seconds: int = 3600,
    ):
        """
        Initialize task queue.

        Args:
            redis_url: Redis connection URL
            queue_prefix: Prefix for queue keys
            result_ttl_seconds: TTL for task results
        """
        self.redis_url = redis_url
        self.queue_prefix = queue_prefix
        self.result_ttl_seconds = result_ttl_seconds
        self._redis: Optional[redis.Redis] = None
        self._handlers: Dict[str, Callable] = {}
        self._running = False

    def connect(self) -> None:
        """Connect to Redis."""
        self._redis = redis.from_url(
            self.redis_url,
            decode_responses=True,
            socket_connect_timeout=5,
        )
        logger.info(f"TaskQueue connected to Redis: {self.redis_url}")

    def disconnect(self) -> None:
        """Disconnect from Redis."""
        self._running = False
        if self._redis:
            self._redis.close()
        logger.info("TaskQueue disconnected")

    def _get_queue_key(self, queue_name: str) -> str:
        """Get queue key with prefix."""
        return f"{self.queue_prefix}:{queue_name}"

    def _get_scheduled_key(self) -> str:
        """Get scheduled tasks key."""
        return f"{self.queue_prefix}:scheduled"

    def _get_result_key(self, task_id: str) -> str:
        """Get result key for task."""
        return f"{self.queue_prefix}:result:{task_id}"

    def register_handler(self, task_type: str) -> Callable:
        """
        Decorator to register task handler.

        Usage:
            @task_queue.register_handler('email.send')
            def send_email(payload: Dict[str, Any]) -> bool:
                # Send email logic
                return True
        """
        def decorator(func: Callable) -> Callable:
            self._handlers[task_type] = func
            logger.info(f"Registered handler for {task_type}")
            return func
        return decorator

    def enqueue(
        self,
        task_type: str,
        payload: Dict[str, Any],
        priority: int = 5,
        delay_seconds: int = 0,
        timeout_seconds: int = 300,
        max_retries: int = 3,
        queue_name: str = "default",
    ) -> Task:
        """
        Add task to queue.

        Args:
            task_type: Type of task (must have registered handler)
            payload: Task data
            priority: Priority 1-10 (10 highest)
            delay_seconds: Delay before execution
            timeout_seconds: Task timeout
            max_retries: Max retry attempts
            queue_name: Queue name

        Returns:
            Created task
        """
        if not self._redis:
            self.connect()

        task = Task(
            task_id=str(uuid.uuid4()),
            task_type=task_type,
            payload=payload,
            priority=priority,
            scheduled_at=datetime.utcnow() + timedelta(seconds=delay_seconds) if delay_seconds > 0 else None,
            timeout_seconds=timeout_seconds,
            max_retries=max_retries,
            queue_name=queue_name,
        )

        if delay_seconds > 0:
            # Add to scheduled queue
            self._redis.zadd(
                self._get_scheduled_key(),
                {task.to_json(): task.scheduled_at.timestamp()}
            )
        else:
            # Add to priority queue
            self._redis.zadd(
                self._get_queue_key(queue_name),
                {task.to_json(): -priority}  # Negative for descending order
            )

        logger.debug(f"Enqueued task {task.task_id} to {queue_name}")
        return task

    def enqueue_batch(
        self,
        tasks: List[Dict[str, Any]],
        queue_name: str = "default",
    ) -> List[Task]:
        """
        Add multiple tasks to queue.

        Args:
            tasks: List of task definitions
            queue_name: Queue name

        Returns:
            List of created tasks
        """
        created_tasks = []

        for task_def in tasks:
            task = self.enqueue(
                task_type=task_def.get('task_type', 'default'),
                payload=task_def.get('payload', {}),
                priority=task_def.get('priority', 5),
                delay_seconds=task_def.get('delay_seconds', 0),
                queue_name=queue_name,
            )
            created_tasks.append(task)

        return created_tasks

    def dequeue(self, queue_name: str = "default", timeout_seconds: int = 5) -> Optional[Task]:
        """
        Get next task from queue.

        Args:
            queue_name: Queue to dequeue from
            timeout_seconds: Block timeout

        Returns:
            Next task or None
        """
        if not self._redis:
            self.connect()

        # First, move scheduled tasks that are due
        self._process_scheduled_tasks()

        # Get highest priority task
        queue_key = self._get_queue_key(queue_name)
        result = self._redis.zpopmin(queue_key, count=1)

        if not result:
            return None

        task_json = result[0][0]
        task = Task.from_json(task_json)
        task.status = TaskStatus.QUEUED

        return task

    def _process_scheduled_tasks(self) -> None:
        """Move scheduled tasks that are due to their queues."""
        if not self._redis:
            return

        now = datetime.utcnow().timestamp()
        scheduled_key = self._get_scheduled_key()

        # Get due tasks
        due_tasks = self._redis.zrangebyscore(scheduled_key, '-inf', now)

        for task_json in due_tasks:
            task = Task.from_json(task_json)

            # Remove from scheduled
            self._redis.zrem(scheduled_key, task_json)

            # Add to queue
            queue_key = self._get_queue_key(task.queue_name)
            self._redis.zadd(queue_key, {task.to_json(): -task.priority})

            logger.debug(f"Moved scheduled task {task.task_id} to queue")

    def execute_task(self, task: Task) -> bool:
        """
        Execute task with registered handler.

        Args:
            task: Task to execute

        Returns:
            True if successful
        """
        if task.task_type not in self._handlers:
            task.status = TaskStatus.FAILED
            task.error = f"No handler registered for {task.task_type}"
            logger.error(task.error)
            return False

        handler = self._handlers[task.task_type]
        task.status = TaskStatus.RUNNING
        task.started_at = datetime.utcnow()

        try:
            # Execute with timeout
            import signal

            def timeout_handler(signum, frame):
                raise TimeoutError(f"Task {task.task_id} timed out")

            # Set timeout (Unix only)
            try:
                signal.signal(signal.SIGALRM, timeout_handler)
                signal.alarm(task.timeout_seconds)
            except (AttributeError, ValueError):
                pass  # Not on Unix or already in alarm

            # Execute handler
            result = handler(task.payload)

            # Cancel alarm
            try:
                signal.alarm(0)
            except (AttributeError, ValueError):
                pass

            task.status = TaskStatus.COMPLETED
            task.result = result
            task.completed_at = datetime.utcnow()

            # Store result
            self._store_result(task)

            logger.info(f"Task {task.task_id} completed successfully")
            return True

        except Exception as e:
            task.status = TaskStatus.FAILED
            task.error = str(e)
            task.completed_at = datetime.utcnow()

            logger.error(f"Task {task.task_id} failed: {e}")

            # Retry if possible
            if task.can_retry():
                self._retry_task(task)
            else:
                self._send_to_dlq(task)

            return False

    def _store_result(self, task: Task) -> None:
        """Store task result with TTL."""
        if not self._redis:
            return

        result_key = self._get_result_key(task.task_id)
        result_data = {
            'task_id': task.task_id,
            'status': task.status.value,
            'result': task.result,
            'completed_at': task.completed_at.isoformat() if task.completed_at else None,
        }

        self._redis.setex(
            result_key,
            self.result_ttl_seconds,
            json.dumps(result_data)
        )

    def _retry_task(self, task: Task) -> None:
        """Schedule task for retry with exponential backoff."""
        task.retry_count += 1
        task.status = TaskStatus.RETRYING

        # Exponential backoff: 2^retry_count seconds
        delay = 2 ** task.retry_count

        task.scheduled_at = datetime.utcnow() + timedelta(seconds=delay)

        # Re-add to scheduled queue
        if self._redis:
            self._redis.zadd(
                self._get_scheduled_key(),
                {task.to_json(): task.scheduled_at.timestamp()}
            )

        logger.info(f"Task {task.task_id} scheduled for retry {task.retry_count}/{task.max_retries}")

    def _send_to_dlq(self, task: Task) -> None:
        """Send failed task to dead letter queue."""
        if not self._redis:
            return

        dlq_key = f"{self.queue_prefix}:dlq"
        dlq_data = {
            'task': task.to_json(),
            'failed_at': datetime.utcnow().isoformat(),
        }

        self._redis.lpush(dlq_key, json.dumps(dlq_data))
        self._redis.ltrim(dlq_key, 0, 999)  # Keep last 1000

        logger.warning(f"Task {task.task_id} sent to DLQ after {task.max_retries} retries")

    def get_task_result(self, task_id: str, wait_seconds: int = 0) -> Optional[Dict[str, Any]]:
        """
        Get task result.

        Args:
            task_id: Task ID
            wait_seconds: Wait for completion (0 = no wait)

        Returns:
            Task result or None
        """
        if not self._redis:
            return None

        result_key = self._get_result_key(task_id)

        # Wait for result if requested
        start_time = time.time()
        while wait_seconds > 0:
            result = self._redis.get(result_key)
            if result:
                return json.loads(result)

            if time.time() - start_time >= wait_seconds:
                break

            time.sleep(0.1)

        # Final check
        result = self._redis.get(result_key)
        return json.loads(result) if result else None

    def get_queue_length(self, queue_name: str = "default") -> int:
        """Get number of tasks in queue."""
        if not self._redis:
            return 0

        return self._redis.zcard(self._get_queue_key(queue_name))

    def get_dlq_length(self) -> int:
        """Get number of tasks in dead letter queue."""
        if not self._redis:
            return 0

        dlq_key = f"{self.queue_prefix}:dlq"
        return self._redis.llen(dlq_key)

    def retry_dlq_task(self, task_index: int) -> bool:
        """Retry task from dead letter queue."""
        if not self._redis:
            return False

        dlq_key = f"{self.queue_prefix}:dlq"
        task_json = self._redis.lindex(dlq_key, task_index)

        if not task_json:
            return False

        dlq_data = json.loads(task_json)
        task = Task.from_json(dlq_data['task'])

        # Reset task state
        task.status = TaskStatus.PENDING
        task.error = None
        task.retry_count = 0

        # Re-enqueue
        self._redis.zadd(
            self._get_queue_key(task.queue_name),
            {task.to_json(): -task.priority}
        )

        # Remove from DLQ
        self._redis.lrem(dlq_key, task_index + 1, task_json)

        logger.info(f"Retried DLQ task {task.task_id}")
        return True

    def clear_dlq(self) -> int:
        """Clear dead letter queue."""
        if not self._redis:
            return 0

        dlq_key = f"{self.queue_prefix}:dlq"
        count = self._redis.llen(dlq_key)
        self._redis.delete(dlq_key)

        logger.info(f"Cleared {count} tasks from DLQ")
        return count

    def process_tasks(self, queue_name: str = "default", batch_size: int = 10) -> int:
        """
        Process tasks from queue.

        Args:
            queue_name: Queue to process
            batch_size: Max tasks to process

        Returns:
            Number of tasks processed
        """
        processed = 0

        while processed < batch_size:
            task = self.dequeue(queue_name, timeout_seconds=0)

            if not task:
                break

            self.execute_task(task)
            processed += 1

        return processed

    def run_worker(self, queue_names: Optional[List[str]] = None, poll_seconds: int = 1) -> None:
        """
        Run worker to process tasks continuously.

        Args:
            queue_names: Queues to process (None for all)
            poll_seconds: Poll interval
        """
        if not queue_names:
            queue_names = ['default']

        self._running = True
        logger.info(f"Worker started for queues: {queue_names}")

        while self._running:
            for queue_name in queue_names:
                processed = self.process_tasks(queue_name)

                if processed == 0:
                    time.sleep(poll_seconds)

    def stop_worker(self) -> None:
        """Stop worker loop."""
        self._running = False
        logger.info("Worker stopping...")


# Default task queue instance
_default_queue: Optional[TaskQueue] = None


def get_task_queue(redis_url: str = "redis://localhost:6379") -> TaskQueue:
    """Get or create default task queue."""
    global _default_queue
    if _default_queue is None:
        _default_queue = TaskQueue(redis_url=redis_url)
    return _default_queue


def enqueue_task(
    task_type: str,
    payload: Dict[str, Any],
    **kwargs
) -> Task:
    """Enqueue task using default queue."""
    queue = get_task_queue()
    return queue.enqueue(task_type, payload, **kwargs)


def task(task_type: str, **kwargs):
    """
    Decorator to register and enqueue task.

    Usage:
        @task('email.send', priority=8)
        def send_email(to: str, subject: str, body: str):
            # Send email
            pass

        # Call to enqueue:
        send_email.enqueue(to='user@example.com', subject='Hello', body='World')
    """
    def decorator(func: Callable) -> Callable:
        queue = get_task_queue()
        queue.register_handler(task_type)(func)

        def enqueue_wrapper(**enqueue_kwargs):
            merged_kwargs = {**kwargs, **enqueue_kwargs}
            return queue.enqueue(task_type, merged_kwargs)

        func.enqueue = enqueue_wrapper  # type: ignore
        return func
    return decorator
