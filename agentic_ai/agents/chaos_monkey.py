"""
ChaosMonkeyAgent - Chaos Engineering & Resiliency Testing
==========================================================

Provides chaos engineering experiments, failure injection, resiliency testing,
and system robustness validation following Netflix's Chaos Monkey principles.

Inspired by Netflix Chaos Monkey: https://github.com/Netflix/chaosmonkey
"""

import logging
import random
import secrets
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from typing import Any, Dict, List, Optional


logger = logging.getLogger(__name__)


class ExperimentType(Enum):
    """Chaos experiment types."""
    INSTANCE_TERMINATION = "instance_termination"
    SERVICE_FAILURE = "service_failure"
    LATENCY_INJECTION = "latency_injection"
    BANDWIDTH_LIMITATION = "bandwidth_limitation"
    CPU_STRESS = "cpu_stress"
    MEMORY_STRESS = "memory_stress"
    DISK_FILL = "disk_fill"
    NETWORK_PARTITION = "network_partition"
    DNS_FAILURE = "dns_failure"
    API_FAILURE = "api_failure"
    DATABASE_FAILURE = "database_failure"
    CACHE_FAILURE = "cache_failure"
    QUEUE_FAILURE = "queue_failure"
    REGION_FAILURE = "region_failure"
    AZ_FAILURE = "az_failure"
    DEPENDENCY_FAILURE = "dependency_failure"


class ExperimentStatus(Enum):
    """Experiment status."""
    SCHEDULED = "scheduled"
    RUNNING = "running"
    COMPLETED = "completed"
    ABORTED = "aborted"
    FAILED = "failed"
    PAUSED = "paused"


class TargetType(Enum):
    """Target types for chaos experiments."""
    INSTANCE = "instance"
    SERVICE = "service"
    CONTAINER = "container"
    POD = "pod"
    NODE = "node"
    CLUSTER = "cluster"
    REGION = "region"
    AVAILABILITY_ZONE = "availability_zone"
    DATABASE = "database"
    CACHE = "cache"
    QUEUE = "queue"
    API = "api"


class SeverityLevel(Enum):
    """Experiment severity levels."""
    LOW = "low"  # Minimal impact, single non-critical instance
    MEDIUM = "medium"  # Moderate impact, multiple instances or single critical
    HIGH = "high"  # Significant impact, service degradation expected
    CRITICAL = "critical"  # Major impact, potential outage scenario


class BlastRadius(Enum):
    """Blast radius constraints."""
    SINGLE = "single"  # Single instance/component
    LIMITED = "limited"  # Up to 10% of capacity
    MODERATE = "moderate"  # Up to 25% of capacity
    UNCONSTRAINED = "unconstrained"  # No limits (use with caution)


class AbortCondition(Enum):
    """Conditions that trigger experiment abort."""
    ERROR_RATE_THRESHOLD = "error_rate_threshold"
    LATENCY_THRESHOLD = "latency_threshold"
    AVAILABILITY_THRESHOLD = "availability_threshold"
    MANUAL_ABORT = "manual_abort"
    HEALTH_CHECK_FAILURE = "health_check_failure"
    CASCADE_FAILURE = "cascade_failure"


@dataclass
class Target:
    """Chaos experiment target."""
    target_id: str
    target_type: TargetType
    name: str
    cloud_provider: str  # aws, gcp, azure, kubernetes
    region: str
    availability_zone: str
    metadata: Dict[str, Any] = field(default_factory=dict)
    tags: List[str] = field(default_factory=list)
    critical: bool = False
    created_at: datetime = field(default_factory=datetime.utcnow)


@dataclass
class Experiment:
    """Chaos engineering experiment."""
    experiment_id: str
    name: str
    description: str
    experiment_type: ExperimentType
    status: ExperimentStatus
    severity: SeverityLevel
    blast_radius: BlastRadius
    targets: List[str] = field(default_factory=list)
    target_count: int = 0
    duration_minutes: int = 0
    scheduled_start: Optional[datetime] = None
    scheduled_end: Optional[datetime] = None
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    abort_conditions: List[AbortCondition] = field(default_factory=list)
    abort_thresholds: Dict[str, float] = field(default_factory=dict)
    hypothesis: str = ""
    expected_outcome: str = ""
    actual_outcome: str = ""
    lessons_learned: List[str] = field(default_factory=list)
    created_by: str = ""
    approved_by: str = ""


@dataclass
class ExperimentRun:
    """Individual experiment execution."""
    run_id: str
    experiment_id: str
    target_id: str
    status: str  # pending, running, completed, failed, aborted
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    duration_seconds: float = 0.0
    result: Dict[str, Any] = field(default_factory=dict)
    metrics_before: Dict[str, float] = field(default_factory=dict)
    metrics_after: Dict[str, float] = field(default_factory=dict)
    error_message: str = ""


@dataclass
class SafetyConstraint:
    """Safety constraints for chaos experiments."""
    constraint_id: str
    name: str
    description: str
    constraint_type: str  # blackout_window, max_percentage, exclude_critical, require_approval
    enabled: bool = True
    parameters: Dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.utcnow)


@dataclass
class BlackoutWindow:
    """Time window where chaos experiments are not allowed."""
    window_id: str
    name: str
    start_time: str  # HH:MM format
    end_time: str  # HH:MM format
    days: List[str] = field(default_factory=list)  # monday, tuesday, etc.
    timezone: str = "UTC"
    enabled: bool = True
    reason: str = ""


@dataclass
class MetricThreshold:
    """Metric thresholds for abort conditions."""
    threshold_id: str
    experiment_id: str
    metric_name: str  # error_rate, latency_p99, availability, etc.
    operator: str  # gt, lt, gte, lte, eq
    threshold_value: float
    current_value: float = 0.0
    breached: bool = False
    breach_count: int = 0
    created_at: datetime = field(default_factory=datetime.utcnow)


@dataclass
class ResiliencyScore:
    """System resiliency score from experiments."""
    score_id: str
    service_name: str
    overall_score: float  # 0-100
    availability_score: float
    recovery_score: float
    degradation_score: float
    monitoring_score: float
    experiments_run: int = 0
    experiments_passed: int = 0
    mttr_minutes: float = 0.0  # Mean time to recovery
    last_assessed: datetime = field(default_factory=datetime.utcnow)


class ChaosMonkeyAgent:
    """
    Chaos Monkey Agent for chaos engineering experiments,
    failure injection, and resiliency testing.
    
    Inspired by Netflix Chaos Monkey - randomly terminates instances
    and injects failures to build resilient systems.
    """
    
    def __init__(self, agent_id: str = "chaos-monkey-agent"):
        self.agent_id = agent_id
        self.targets: Dict[str, Target] = {}
        self.experiments: Dict[str, Experiment] = {}
        self.runs: Dict[str, ExperimentRun] = {}
        self.safety_constraints: Dict[str, SafetyConstraint] = {}
        self.blackout_windows: Dict[str, BlackoutWindow] = {}
        self.metric_thresholds: Dict[str, MetricThreshold] = {}
        self.resiliency_scores: Dict[str, ResiliencyScore] = {}
        
        # Default abort thresholds
        self.default_abort_thresholds = {
            'error_rate': 5.0,  # 5% error rate
            'latency_p99': 5000,  # 5 seconds
            'availability': 95.0,  # 95% availability
        }
    
    # ============================================
    # Target Management
    # ============================================
    
    def register_target(
        self,
        target_type: TargetType,
        name: str,
        cloud_provider: str,
        region: str,
        availability_zone: str,
        metadata: Optional[Dict[str, Any]] = None,
        tags: Optional[List[str]] = None,
        critical: bool = False,
    ) -> Target:
        """Register a target for chaos experiments."""
        target = Target(
            target_id=self._generate_id("target"),
            target_type=target_type,
            name=name,
            cloud_provider=cloud_provider,
            region=region,
            availability_zone=availability_zone,
            metadata=metadata or {},
            tags=tags or [],
            critical=critical,
        )
        
        self.targets[target.target_id] = target
        return target
    
    def get_targets(
        self,
        target_type: Optional[TargetType] = None,
        cloud_provider: Optional[str] = None,
        region: Optional[str] = None,
        critical: Optional[bool] = None,
    ) -> List[Target]:
        """Get targets with filtering."""
        targets = list(self.targets.values())
        
        if target_type:
            targets = [t for t in targets if t.target_type == target_type]
        
        if cloud_provider:
            targets = [t for t in targets if t.cloud_provider == cloud_provider]
        
        if region:
            targets = [t for t in targets if t.region == region]
        
        if critical is not None:
            targets = [t for t in targets if t.critical == critical]
        
        return targets
    
    def select_random_targets(
        self,
        count: int = 1,
        target_type: Optional[TargetType] = None,
        exclude_critical: bool = True,
    ) -> List[Target]:
        """Randomly select targets for chaos experiment."""
        candidates = self.get_targets(target_type=target_type)
        
        if exclude_critical:
            candidates = [t for t in candidates if not t.critical]
        
        if not candidates:
            return []
        
        count = min(count, len(candidates))
        return random.sample(candidates, count)
    
    # ============================================
    # Experiment Management
    # ============================================
    
    def create_experiment(
        self,
        name: str,
        description: str,
        experiment_type: ExperimentType,
        severity: SeverityLevel,
        blast_radius: BlastRadius,
        duration_minutes: int,
        hypothesis: str = "",
        expected_outcome: str = "",
        abort_conditions: Optional[List[AbortCondition]] = None,
        abort_thresholds: Optional[Dict[str, float]] = None,
        created_by: str = "",
    ) -> Experiment:
        """Create chaos engineering experiment."""
        experiment = Experiment(
            experiment_id=self._generate_id("exp"),
            name=name,
            description=description,
            experiment_type=experiment_type,
            status=ExperimentStatus.SCHEDULED,
            severity=severity,
            blast_radius=blast_radius,
            duration_minutes=duration_minutes,
            hypothesis=hypothesis,
            expected_outcome=expected_outcome,
            abort_conditions=abort_conditions or [],
            abort_thresholds=abort_thresholds or self.default_abort_thresholds.copy(),
            created_by=created_by,
        )
        
        self.experiments[experiment.experiment_id] = experiment
        return experiment
    
    def schedule_experiment(
        self,
        experiment_id: str,
        start_time: datetime,
        end_time: Optional[datetime] = None,
    ) -> bool:
        """Schedule experiment for execution."""
        if experiment_id not in self.experiments:
            return False
        
        experiment = self.experiments[experiment_id]
        experiment.scheduled_start = start_time
        
        if end_time:
            experiment.scheduled_end = end_time
        else:
            experiment.scheduled_end = start_time + timedelta(minutes=experiment.duration_minutes)
        
        return True
    
    def assign_targets(
        self,
        experiment_id: str,
        target_ids: List[str],
    ) -> bool:
        """Assign targets to experiment."""
        if experiment_id not in self.experiments:
            return False
        
        experiment = self.experiments[experiment_id]
        experiment.targets = target_ids
        experiment.target_count = len(target_ids)
        
        return True
    
    def start_experiment(self, experiment_id: str) -> bool:
        """Start chaos experiment."""
        if experiment_id not in self.experiments:
            return False
        
        # Check blackout windows
        if self._is_in_blackout():
            logger.warning(f"Experiment {experiment_id} blocked by blackout window")
            return False
        
        # Check safety constraints
        if not self._check_safety_constraints(experiment_id):
            logger.warning(f"Experiment {experiment_id} blocked by safety constraints")
            return False
        
        experiment = self.experiments[experiment_id]
        experiment.status = ExperimentStatus.RUNNING
        experiment.started_at = datetime.utcnow()
        
        # Create experiment runs for each target
        for target_id in experiment.targets:
            self._create_experiment_run(experiment_id, target_id)
        
        return True
    
    def _create_experiment_run(self, experiment_id: str, target_id: str) -> ExperimentRun:
        """Create individual experiment run."""
        experiment = self.experiments[experiment_id]
        
        run = ExperimentRun(
            run_id=self._generate_id("run"),
            experiment_id=experiment_id,
            target_id=target_id,
            status="pending",
        )
        
        self.runs[run.run_id] = run
        return run
    
    def execute_termination(self, run_id: str) -> bool:
        """Execute instance termination."""
        if run_id not in self.runs:
            return False
        
        run = self.runs[run_id]
        run.status = "running"
        run.started_at = datetime.utcnow()
        
        # Simulate termination (in real implementation, would call cloud API)
        target = self.targets.get(run.target_id)
        if target:
            run.result = {
                'action': 'terminate',
                'target': target.name,
                'target_type': target.target_type.value,
                'cloud_provider': target.cloud_provider,
                'region': target.region,
            }
        
        # Simulate completion
        run.completed_at = datetime.utcnow()
        run.duration_seconds = (run.completed_at - run.started_at).total_seconds()
        run.status = "completed"
        
        return True
    
    def execute_latency_injection(
        self,
        run_id: str,
        latency_ms: int,
        jitter_percent: float = 10.0,
    ) -> bool:
        """Execute latency injection."""
        if run_id not in self.runs:
            return False
        
        run = self.runs[run_id]
        run.status = "running"
        run.started_at = datetime.utcnow()
        
        actual_latency = latency_ms * (1 + random.uniform(-jitter_percent/100, jitter_percent/100))
        
        run.result = {
            'action': 'latency_injection',
            'latency_ms': latency_ms,
            'actual_latency_ms': actual_latency,
            'jitter_percent': jitter_percent,
        }
        
        run.completed_at = datetime.utcnow()
        run.duration_seconds = (run.completed_at - run.started_at).total_seconds()
        run.status = "completed"
        
        return True
    
    def complete_experiment(
        self,
        experiment_id: str,
        actual_outcome: str = "",
        lessons_learned: Optional[List[str]] = None,
    ) -> bool:
        """Complete chaos experiment."""
        if experiment_id not in self.experiments:
            return False
        
        experiment = self.experiments[experiment_id]
        experiment.status = ExperimentStatus.COMPLETED
        experiment.completed_at = datetime.utcnow()
        experiment.actual_outcome = actual_outcome
        experiment.lessons_learned = lessons_learned or []
        
        return True
    
    def abort_experiment(self, experiment_id: str, reason: str) -> bool:
        """Abort chaos experiment."""
        if experiment_id not in self.experiments:
            return False
        
        experiment = self.experiments[experiment_id]
        experiment.status = ExperimentStatus.ABORTED
        experiment.completed_at = datetime.utcnow()
        experiment.lessons_learned.append(f"Aborted: {reason}")
        
        # Abort all running runs
        for run in self.runs.values():
            if run.experiment_id == experiment_id and run.status == "running":
                run.status = "aborted"
                run.completed_at = datetime.utcnow()
        
        return True
    
    def get_experiments(
        self,
        experiment_type: Optional[ExperimentType] = None,
        status: Optional[ExperimentStatus] = None,
        severity: Optional[SeverityLevel] = None,
    ) -> List[Experiment]:
        """Get experiments with filtering."""
        experiments = list(self.experiments.values())
        
        if experiment_type:
            experiments = [e for e in experiments if e.experiment_type == experiment_type]
        
        if status:
            experiments = [e for e in experiments if e.status == status]
        
        if severity:
            experiments = [e for e in experiments if e.severity == severity]
        
        return experiments
    
    # ============================================
    # Safety Constraints
    # ============================================
    
    def add_safety_constraint(
        self,
        name: str,
        description: str,
        constraint_type: str,
        parameters: Optional[Dict[str, Any]] = None,
    ) -> SafetyConstraint:
        """Add safety constraint."""
        constraint = SafetyConstraint(
            constraint_id=self._generate_id("constraint"),
            name=name,
            description=description,
            constraint_type=constraint_type,
            parameters=parameters or {},
        )
        
        self.safety_constraints[constraint.constraint_id] = constraint
        return constraint
    
    def add_blackout_window(
        self,
        name: str,
        start_time: str,
        end_time: str,
        days: Optional[List[str]] = None,
        timezone: str = "UTC",
        reason: str = "",
    ) -> BlackoutWindow:
        """Add blackout window."""
        window = BlackoutWindow(
            window_id=self._generate_id("blackout"),
            name=name,
            start_time=start_time,
            end_time=end_time,
            days=days or [],
            timezone=timezone,
            reason=reason,
        )
        
        self.blackout_windows[window.window_id] = window
        return window
    
    def _is_in_blackout(self) -> bool:
        """Check if current time is in blackout window."""
        now = datetime.utcnow()
        current_time = now.strftime("%H:%M")
        current_day = now.strftime("%A").lower()
        
        for window in self.blackout_windows.values():
            if not window.enabled:
                continue
            
            if window.days and current_day not in window.days:
                continue
            
            if window.start_time <= current_time <= window.end_time:
                return True
        
        return False
    
    def _check_safety_constraints(self, experiment_id: str) -> bool:
        """Check if experiment passes safety constraints."""
        experiment = self.experiments.get(experiment_id)
        if not experiment:
            return False
        
        # Check critical target exclusion
        if experiment.blast_radius != BlastRadius.UNCONSTRAINED:
            for target_id in experiment.targets:
                target = self.targets.get(target_id)
                if target and target.critical:
                    return False
        
        # Check max percentage constraint
        for constraint in self.safety_constraints.values():
            if not constraint.enabled:
                continue
            
            if constraint.constraint_type == "max_percentage":
                max_pct = constraint.parameters.get('max_percentage', 10)
                # Would check actual percentage here
                pass
        
        return True
    
    def add_metric_threshold(
        self,
        experiment_id: str,
        metric_name: str,
        operator: str,
        threshold_value: float,
    ) -> MetricThreshold:
        """Add metric threshold for abort conditions."""
        threshold = MetricThreshold(
            threshold_id=self._generate_id("threshold"),
            experiment_id=experiment_id,
            metric_name=metric_name,
            operator=operator,
            threshold_value=threshold_value,
        )
        
        self.metric_thresholds[threshold.threshold_id] = threshold
        return threshold
    
    def check_metric_thresholds(
        self,
        experiment_id: str,
        metrics: Dict[str, float],
    ) -> List[str]:
        """Check if any metric thresholds are breached."""
        breached = []
        
        for threshold in self.metric_thresholds.values():
            if threshold.experiment_id != experiment_id:
                continue
            
            metric_value = metrics.get(threshold.metric_name, 0)
            threshold.current_value = metric_value
            
            # Check threshold
            if threshold.operator == 'gt' and metric_value > threshold.threshold_value:
                threshold.breached = True
                threshold.breach_count += 1
                breached.append(threshold.metric_name)
            elif threshold.operator == 'lt' and metric_value < threshold.threshold_value:
                threshold.breached = True
                threshold.breach_count += 1
                breached.append(threshold.metric_name)
        
        return breached
    
    # ============================================
    # Resiliency Scoring
    # ============================================
    
    def calculate_resiliency_score(
        self,
        service_name: str,
        experiments: Optional[List[str]] = None,
    ) -> ResiliencyScore:
        """Calculate resiliency score for a service."""
        # Get experiments for this service
        service_experiments = []
        if experiments:
            service_experiments = [
                self.experiments[eid] for eid in experiments
                if eid in self.experiments
            ]
        else:
            service_experiments = list(self.experiments.values())
        
        if not service_experiments:
            return ResiliencyScore(
                score_id=self._generate_id("score"),
                service_name=service_name,
                overall_score=0.0,
                availability_score=0.0,
                recovery_score=0.0,
                degradation_score=0.0,
                monitoring_score=0.0,
            )
        
        # Calculate scores
        completed = [e for e in service_experiments if e.status == ExperimentStatus.COMPLETED]
        passed = len([e for e in completed if e.actual_outcome])  # Has outcome = passed
        
        experiments_run = len(service_experiments)
        experiments_passed = passed
        
        # Availability score (based on successful experiments)
        availability_score = (experiments_passed / experiments_run * 100) if experiments_run > 0 else 0
        
        # Recovery score (based on MTTR)
        recovery_score = 80.0  # Default, would calculate from actual recovery times
        
        # Degradation score (how well system degraded)
        degradation_score = 75.0  # Default
        
        # Monitoring score (were issues detected?)
        monitoring_score = 90.0  # Default
        
        # Overall weighted score
        overall_score = (
            availability_score * 0.4 +
            recovery_score * 0.3 +
            degradation_score * 0.2 +
            monitoring_score * 0.1
        )
        
        score = ResiliencyScore(
            score_id=self._generate_id("score"),
            service_name=service_name,
            overall_score=overall_score,
            availability_score=availability_score,
            recovery_score=recovery_score,
            degradation_score=degradation_score,
            monitoring_score=monitoring_score,
            experiments_run=experiments_run,
            experiments_passed=experiments_passed,
        )
        
        self.resiliency_scores[service_name] = score
        return score
    
    # ============================================
    # Reporting
    # ============================================
    
    def get_chaos_dashboard(self) -> Dict[str, Any]:
        """Generate chaos engineering dashboard."""
        experiments = list(self.experiments.values())
        runs = list(self.runs.values())
        
        # Experiments by status
        by_status = {}
        for status in ExperimentStatus:
            by_status[status.value] = len([e for e in experiments if e.status == status])
        
        # Experiments by type
        by_type = {}
        for etype in ExperimentType:
            by_type[etype.value] = len([e for e in experiments if e.experiment_type == etype])
        
        # Run success rate
        completed_runs = [r for r in runs if r.status == "completed"]
        failed_runs = [r for r in runs if r.status == "failed"]
        
        return {
            'experiments': {
                'total': len(experiments),
                'by_status': by_status,
                'by_type': by_type,
                'running': by_status.get('running', 0),
            },
            'runs': {
                'total': len(runs),
                'completed': len(completed_runs),
                'failed': len(failed_runs),
                'success_rate': (len(completed_runs) / len(runs) * 100) if runs else 0,
            },
            'targets': {
                'total': len(self.targets),
                'critical': len([t for t in self.targets.values() if t.critical]),
            },
            'safety': {
                'constraints': len(self.safety_constraints),
                'blackout_windows': len(self.blackout_windows),
                'in_blackout': self._is_in_blackout(),
            },
            'resiliency': {
                'services_scored': len(self.resiliency_scores),
                'average_score': sum(s.overall_score for s in self.resiliency_scores.values()) / len(self.resiliency_scores) if self.resiliency_scores else 0,
            },
        }
    
    def get_experiment_report(self, experiment_id: str) -> Dict[str, Any]:
        """Generate experiment report."""
        if experiment_id not in self.experiments:
            return {'error': 'Experiment not found'}
        
        experiment = self.experiments[experiment_id]
        runs = [r for r in self.runs.values() if r.experiment_id == experiment_id]
        
        return {
            'experiment': {
                'experiment_id': experiment_id,
                'name': experiment.name,
                'type': experiment.experiment_type.value,
                'status': experiment.status.value,
                'severity': experiment.severity.value,
                'blast_radius': experiment.blast_radius.value,
                'duration_minutes': experiment.duration_minutes,
                'hypothesis': experiment.hypothesis,
                'expected_outcome': experiment.expected_outcome,
                'actual_outcome': experiment.actual_outcome,
                'lessons_learned': experiment.lessons_learned,
            },
            'targets': {
                'count': experiment.target_count,
                'target_ids': experiment.targets,
            },
            'runs': {
                'total': len(runs),
                'completed': len([r for r in runs if r.status == 'completed']),
                'failed': len([r for r in runs if r.status == 'failed']),
                'aborted': len([r for r in runs if r.status == 'aborted']),
            },
            'timing': {
                'scheduled_start': experiment.scheduled_start.isoformat() if experiment.scheduled_start else None,
                'scheduled_end': experiment.scheduled_end.isoformat() if experiment.scheduled_end else None,
                'started_at': experiment.started_at.isoformat() if experiment.started_at else None,
                'completed_at': experiment.completed_at.isoformat() if experiment.completed_at else None,
            },
        }
    
    # ============================================
    # Utilities
    # ============================================
    
    def _generate_id(self, prefix: str) -> str:
        """Generate a unique ID."""
        timestamp = datetime.utcnow().strftime('%Y%m%d%H%M%S')
        random_suffix = secrets.token_hex(4)
        return f"{prefix}-{timestamp}-{random_suffix}"
    
    def get_state(self) -> Dict[str, Any]:
        """Get agent state summary."""
        return {
            'agent_id': self.agent_id,
            'targets_count': len(self.targets),
            'critical_targets': len([t for t in self.targets.values() if t.critical]),
            'experiments_count': len(self.experiments),
            'running_experiments': len([e for e in self.experiments.values() if e.status == ExperimentStatus.RUNNING]),
            'runs_count': len(self.runs),
            'safety_constraints_count': len(self.safety_constraints),
            'blackout_windows_count': len(self.blackout_windows),
            'resiliency_scores_count': len(self.resiliency_scores),
        }


def get_capabilities() -> Dict[str, Any]:
    """Return agent capabilities for orchestration."""
    return {
        'agent_type': 'chaos_monkey',
        'version': '1.0.0',
        'capabilities': [
            'register_target',
            'get_targets',
            'select_random_targets',
            'create_experiment',
            'schedule_experiment',
            'assign_targets',
            'start_experiment',
            'execute_termination',
            'execute_latency_injection',
            'complete_experiment',
            'abort_experiment',
            'get_experiments',
            'add_safety_constraint',
            'add_blackout_window',
            'add_metric_threshold',
            'check_metric_thresholds',
            'calculate_resiliency_score',
            'get_chaos_dashboard',
            'get_experiment_report',
        ],
        'experiment_types': [t.value for t in ExperimentType],
        'target_types': [t.value for t in TargetType],
        'severity_levels': [l.value for l in SeverityLevel],
        'blast_radius_levels': [r.value for r in BlastRadius],
        'abort_conditions': [c.value for c in AbortCondition],
        'supported_clouds': ['aws', 'gcp', 'azure', 'kubernetes'],
    }


if __name__ == "__main__":
    agent = ChaosMonkeyAgent()
    
    # Register targets
    target1 = agent.register_target(
        target_type=TargetType.INSTANCE,
        name="web-server-1",
        cloud_provider="aws",
        region="us-east-1",
        availability_zone="us-east-1a",
        tags=['web', 'production'],
        critical=False,
    )
    
    target2 = agent.register_target(
        target_type=TargetType.INSTANCE,
        name="web-server-2",
        cloud_provider="aws",
        region="us-east-1",
        availability_zone="us-east-1b",
        tags=['web', 'production'],
        critical=False,
    )
    
    target3 = agent.register_target(
        target_type=TargetType.INSTANCE,
        name="db-primary",
        cloud_provider="aws",
        region="us-east-1",
        availability_zone="us-east-1a",
        tags=['database', 'production'],
        critical=True,  # Critical - won't be selected for random chaos
    )
    
    print(f"Registered {len(agent.targets)} targets")
    
    # Add blackout window (no chaos during business hours)
    agent.add_blackout_window(
        name="Business Hours",
        start_time="09:00",
        end_time="17:00",
        days=['monday', 'tuesday', 'wednesday', 'thursday', 'friday'],
        timezone="UTC",
        reason="Protect production during peak hours",
    )
    
    # Add safety constraint
    agent.add_safety_constraint(
        name="Max 10% Capacity",
        description="Never affect more than 10% of capacity",
        constraint_type="max_percentage",
        parameters={'max_percentage': 10},
    )
    
    # Create chaos experiment
    experiment = agent.create_experiment(
        name="Instance Termination Test",
        description="Test auto-healing by terminating random instances",
        experiment_type=ExperimentType.INSTANCE_TERMINATION,
        severity=SeverityLevel.MEDIUM,
        blast_radius=BlastRadius.LIMITED,
        duration_minutes=30,
        hypothesis="System will auto-heal within 5 minutes",
        expected_outcome="No user-visible impact, auto-scaling replaces instances",
        abort_conditions=[
            AbortCondition.ERROR_RATE_THRESHOLD,
            AbortCondition.AVAILABILITY_THRESHOLD,
        ],
        abort_thresholds={
            'error_rate': 2.0,
            'availability': 99.0,
        },
        created_by="chaos-team@example.com",
    )
    
    # Select random targets (excluding critical)
    targets = agent.select_random_targets(count=2, target_type=TargetType.INSTANCE)
    target_ids = [t.target_id for t in targets]
    
    agent.assign_targets(experiment.experiment_id, target_ids)
    
    # Schedule experiment
    start_time = datetime.utcnow() + timedelta(hours=1)
    agent.schedule_experiment(experiment.experiment_id, start_time)
    
    print(f"Created experiment: {experiment.name}")
    print(f"Targets: {len(experiment.targets)}")
    
    # Start experiment (would fail if in blackout)
    if agent.start_experiment(experiment.experiment_id):
        print("Experiment started!")
        
        # Execute termination on runs
        runs = [r for r in agent.runs.values() if r.experiment_id == experiment.experiment_id]
        for run in runs:
            agent.execute_termination(run.run_id)
            print(f"  Terminated: {run.result}")
        
        # Complete experiment
        agent.complete_experiment(
            experiment.experiment_id,
            actual_outcome="System recovered in 3 minutes, no user impact",
            lessons_learned=[
                "Auto-scaling worked as expected",
                "Load balancer health checks detected failures quickly",
                "Consider adding more AZs for better resilience",
            ],
        )
    else:
        print("Experiment blocked by safety constraints or blackout")
    
    # Calculate resiliency score
    score = agent.calculate_resiliency_score("web-service")
    print(f"\nResiliency Score: {score.overall_score:.1f}/100")
    
    # Get dashboard
    dashboard = agent.get_chaos_dashboard()
    print(f"\nChaos Dashboard:")
    print(f"  Experiments: {dashboard['experiments']['total']}")
    print(f"  Success Rate: {dashboard['runs']['success_rate']:.1f}%")
    print(f"  In Blackout: {dashboard['safety']['in_blackout']}")
    
    print(f"\nState: {agent.get_state()}")
