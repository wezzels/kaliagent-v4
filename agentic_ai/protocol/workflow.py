"""
Advanced Workflow Protocol
===========================

Enhanced workflow support for parallel execution, conditional branching,
retry logic, and rollback mechanisms.
"""

from typing import Optional, Dict, Any, List, Callable, TYPE_CHECKING
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
import uuid
import asyncio

if TYPE_CHECKING:
    from .workflow import Task


class TaskStatus(str, Enum):
    """Enhanced task status."""
    PENDING = "pending"
    QUEUED = "queued"
    RUNNING = "running"
    PAUSED = "paused"
    COMPLETED = "completed"
    FAILED = "failed"
    RETRYING = "retrying"
    CANCELLED = "cancelled"
    ROLLED_BACK = "rolled_back"


class ExecutionMode(str, Enum):
    """Task execution mode."""
    SEQUENTIAL = "sequential"
    PARALLEL = "parallel"
    BATCH = "batch"


class RetryStrategy(str, Enum):
    """Retry strategy types."""
    NONE = "none"
    FIXED = "fixed"
    EXPONENTIAL = "exponential"
    LINEAR = "linear"


@dataclass
class RetryConfig:
    """Retry configuration for a task."""

    strategy: RetryStrategy = RetryStrategy.NONE
    max_retries: int = 3
    initial_delay_ms: int = 1000
    max_delay_ms: int = 60000
    multiplier: float = 2.0

    def get_delay(self, attempt: int) -> int:
        """Calculate delay for given attempt number."""
        if self.strategy == RetryStrategy.NONE:
            return 0
        elif self.strategy == RetryStrategy.FIXED:
            return self.initial_delay_ms
        elif self.strategy == RetryStrategy.LINEAR:
            return min(self.initial_delay_ms * attempt, self.max_delay_ms)
        elif self.strategy == RetryStrategy.EXPONENTIAL:
            delay = self.initial_delay_ms * (self.multiplier ** (attempt - 1))
            return min(int(delay), self.max_delay_ms)
        return 0


@dataclass
class Condition:
    """Conditional execution rule."""

    condition_id: str = field(default_factory=lambda: str(uuid.uuid4())[:8])
    type: str = "expression"
    expression: Optional[str] = None
    function: Optional[Callable] = None
    required_status: Optional[TaskStatus] = None

    def evaluate(self, context: Dict[str, Any]) -> bool:
        """Evaluate the condition."""
        if self.type == "status" and self.required_status:
            task_status = context.get("status")
            return task_status == self.required_status.value

        if self.type == "expression" and self.expression:
            try:
                safe_context = {k: v for k, v in context.items() if not k.startswith('_')}
                return eval(self.expression, {"__builtins__": {}}, safe_context)
            except Exception:
                return False

        if self.type == "function" and self.function:
            try:
                return self.function(context)
            except Exception:
                return False

        return True


@dataclass
class Task:
    """Enhanced task with advanced features."""

    task_id: str = field(default_factory=lambda: str(uuid.uuid4())[:8])
    task_type: str = ""
    description: str = ""
    agent_type: str = ""
    payload: Dict[str, Any] = field(default_factory=dict)

    status: TaskStatus = TaskStatus.PENDING
    execution_mode: ExecutionMode = ExecutionMode.SEQUENTIAL
    priority: int = 0

    dependencies: List[str] = field(default_factory=list)
    conditions: List[Condition] = field(default_factory=list)

    retry_config: RetryConfig = field(default_factory=RetryConfig)
    retry_count: int = 0
    last_error: Optional[str] = None

    created_at: str = field(default_factory=lambda: datetime.utcnow().isoformat())
    started_at: Optional[str] = None
    completed_at: Optional[str] = None
    timeout_ms: Optional[int] = None

    result: Optional[Dict[str, Any]] = None

    rollback_task_id: Optional[str] = None
    compensating_transaction: Optional[Dict[str, Any]] = None

    def can_start(self, completed_tasks: Dict[str, 'Task']) -> bool:
        """Check if task can start (dependencies met)."""
        for dep_id in self.dependencies:
            dep_task = completed_tasks.get(dep_id)
            if not dep_task or dep_task.status != TaskStatus.COMPLETED:
                return False

        for condition in self.conditions:
            context = {
                "task": self,
                "dependencies": completed_tasks,
                "status": self.status.value,
            }
            if not condition.evaluate(context):
                return False

        return True

    def should_retry(self) -> bool:
        """Check if task should be retried."""
        if self.retry_config.strategy == RetryStrategy.NONE:
            return False
        return self.retry_count < self.retry_config.max_retries

    def get_retry_delay(self) -> int:
        """Get delay before next retry."""
        return self.retry_config.get_delay(self.retry_count + 1)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "task_id": self.task_id,
            "task_type": self.task_type,
            "description": self.description,
            "agent_type": self.agent_type,
            "status": self.status.value,
            "execution_mode": self.execution_mode.value,
            "priority": self.priority,
            "dependencies": self.dependencies,
            "retry_count": self.retry_count,
            "last_error": self.last_error,
            "created_at": self.created_at,
            "started_at": self.started_at,
            "completed_at": self.completed_at,
            "result": self.result,
        }


@dataclass
class Workflow:
    """Enhanced workflow with advanced features."""

    workflow_id: str = field(default_factory=lambda: str(uuid.uuid4())[:8])
    name: str = ""
    description: str = ""
    tasks: List[Task] = field(default_factory=list)

    status: str = "draft"
    execution_mode: ExecutionMode = ExecutionMode.SEQUENTIAL
    parallel_limit: int = 5

    enable_rollback: bool = True
    rollback_tasks: List[Task] = field(default_factory=list)

    created_at: str = field(default_factory=lambda: datetime.utcnow().isoformat())
    started_at: Optional[str] = None
    completed_at: Optional[str] = None
    timeout_ms: Optional[int] = None

    result: Optional[Dict[str, Any]] = None
    error: Optional[str] = None

    def add_task(self, task: Task):
        """Add a task to the workflow."""
        self.tasks.append(task)

    def get_pending_tasks(self, completed_tasks: Dict[str, Task]) -> List[Task]:
        """Get tasks ready to execute."""
        pending = []
        for task in self.tasks:
            if task.status == TaskStatus.PENDING:
                if task.can_start(completed_tasks):
                    pending.append(task)
        return pending

    def get_parallel_tasks(self, completed_tasks: Dict[str, Task]) -> List[Task]:
        """Get tasks that can run in parallel."""
        pending = self.get_pending_tasks(completed_tasks)
        parallel_tasks = [
            t for t in pending
            if t.execution_mode == ExecutionMode.PARALLEL
        ]
        return parallel_tasks[:self.parallel_limit]

    def get_rollback_tasks(self, failed_task: Task) -> List[Task]:
        """Get rollback tasks for a failed task."""
        if not self.enable_rollback:
            return []

        rollback = []

        if failed_task.rollback_task_id:
            rollback_task = next(
                (t for t in self.tasks if t.task_id == failed_task.rollback_task_id),
                None
            )
            if rollback_task:
                rollback.append(rollback_task)

        rollback.extend(self.rollback_tasks)

        return rollback

    def is_complete(self) -> bool:
        """Check if workflow is complete."""
        completed_count = sum(
            1 for t in self.tasks if t.status == TaskStatus.COMPLETED
        )
        return completed_count == len(self.tasks)

    def has_failed(self) -> bool:
        """Check if workflow has failed."""
        failed_count = sum(
            1 for t in self.tasks if t.status == TaskStatus.FAILED
        )
        return failed_count > 0 and not any(t.should_retry() for t in self.tasks if t.status == TaskStatus.FAILED)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "workflow_id": self.workflow_id,
            "name": self.name,
            "description": self.description,
            "status": self.status,
            "execution_mode": self.execution_mode.value,
            "task_count": len(self.tasks),
            "completed_tasks": sum(1 for t in self.tasks if t.status == TaskStatus.COMPLETED),
            "failed_tasks": sum(1 for t in self.tasks if t.status == TaskStatus.FAILED),
            "enable_rollback": self.enable_rollback,
            "created_at": self.created_at,
            "started_at": self.started_at,
            "completed_at": self.completed_at,
            "result": self.result,
            "error": self.error,
        }
