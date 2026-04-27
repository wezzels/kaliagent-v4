"""
DevOpsAgent - Infrastructure Automation & CI/CD
=================================================

Provides infrastructure automation, CI/CD pipeline management,
deployment orchestration, monitoring, and cost optimization.
"""

import logging
import os
import re
import secrets
import string
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from typing import Any, Dict, List, Optional, Tuple


logger = logging.getLogger(__name__)


class DeploymentStatus(Enum):
    """Deployment status states."""
    PENDING = "pending"
    BUILDING = "building"
    TESTING = "testing"
    DEPLOYING = "deploying"
    DEPLOYED = "deployed"
    FAILED = "failed"
    ROLLED_BACK = "rolled_back"


class InfrastructureType(Enum):
    """Infrastructure resource types."""
    VM = "virtual_machine"
    CONTAINER = "container"
    DATABASE = "database"
    STORAGE = "storage"
    NETWORK = "network"
    LOAD_BALANCER = "load_balancer"
    CDN = "cdn"
    DNS = "dns"


class PipelineStatus(Enum):
    """CI/CD pipeline status."""
    QUEUED = "queued"
    RUNNING = "running"
    PASSED = "passed"
    FAILED = "failed"
    CANCELLED = "cancelled"


@dataclass
class Deployment:
    """Deployment tracking."""
    deployment_id: str
    application: str
    version: str
    environment: str  # dev, staging, prod
    status: DeploymentStatus
    created_at: datetime = field(default_factory=datetime.utcnow)
    deployed_at: Optional[datetime] = None
    deployed_by: Optional[str] = None
    rollback_to: Optional[str] = None
    health_check_url: Optional[str] = None
    logs: List[str] = field(default_factory=list)


@dataclass
class Pipeline:
    """CI/CD pipeline definition."""
    pipeline_id: str
    name: str
    repository: str
    branch: str
    status: PipelineStatus
    stages: List[str] = field(default_factory=list)
    current_stage: Optional[str] = None
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    artifacts: List[str] = field(default_factory=list)
    logs_url: Optional[str] = None


@dataclass
class InfrastructureResource:
    """Infrastructure resource tracking."""
    resource_id: str
    resource_type: InfrastructureType
    name: str
    region: str
    status: str  # running, stopped, error
    cost_per_hour: float = 0.0
    tags: Dict[str, str] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class Alert:
    """Monitoring alert."""
    alert_id: str
    name: str
    severity: str  # critical, warning, info
    metric: str
    threshold: float
    current_value: float
    triggered_at: datetime = field(default_factory=datetime.utcnow)
    acknowledged: bool = False
    acknowledged_by: Optional[str] = None
    resolved_at: Optional[datetime] = None


class DevOpsAgent:
    """
    DevOps Agent for infrastructure automation, CI/CD,
    deployment orchestration, and monitoring.
    """

    def __init__(self, agent_id: str = "devops-agent"):
        self.agent_id = agent_id
        self.deployments: Dict[str, Deployment] = {}
        self.pipelines: Dict[str, Pipeline] = {}
        self.infrastructure: Dict[str, InfrastructureResource] = {}
        self.alerts: Dict[str, Alert] = {}
        self.metrics: Dict[str, List[Dict[str, Any]]] = {}

        # Initialize default infrastructure
        self._init_defaults()

    def _init_defaults(self):
        """Initialize default infrastructure resources."""
        # Example infrastructure
        self.infrastructure = {
            'web-server-1': InfrastructureResource(
                resource_id='web-server-1',
                resource_type=InfrastructureType.VM,
                name='Production Web Server 1',
                region='us-east-1',
                status='running',
                cost_per_hour=0.10,
                tags={'env': 'prod', 'team': 'platform'},
            ),
            'db-primary': InfrastructureResource(
                resource_id='db-primary',
                resource_type=InfrastructureType.DATABASE,
                name='Primary Database',
                region='us-east-1',
                status='running',
                cost_per_hour=0.50,
                tags={'env': 'prod', 'team': 'data'},
            ),
        }

    # ============================================
    # Deployment Management
    # ============================================

    def create_deployment(
        self,
        application: str,
        version: str,
        environment: str,
        deployed_by: str,
        health_check_url: Optional[str] = None,
    ) -> Deployment:
        """Create a new deployment."""
        deployment = Deployment(
            deployment_id=self._generate_id("deploy"),
            application=application,
            version=version,
            environment=environment,
            status=DeploymentStatus.PENDING,
            deployed_by=deployed_by,
            health_check_url=health_check_url,
        )

        self.deployments[deployment.deployment_id] = deployment
        logger.info(f"Created deployment: {deployment.deployment_id} - {application}:{version}")
        return deployment

    def update_deployment_status(
        self,
        deployment_id: str,
        status: DeploymentStatus,
        logs: Optional[List[str]] = None,
    ) -> Optional[Deployment]:
        """Update deployment status."""
        if deployment_id not in self.deployments:
            return None

        deployment = self.deployments[deployment_id]
        deployment.status = status

        if logs:
            deployment.logs.extend(logs)

        if status == DeploymentStatus.DEPLOYED:
            deployment.deployed_at = datetime.utcnow()

        logger.info(f"Deployment {deployment_id} status: {status.value}")
        return deployment

    def rollback_deployment(
        self,
        deployment_id: str,
        rollback_to: str,
        rolled_back_by: str,
    ) -> Optional[Deployment]:
        """Rollback deployment to previous version."""
        if deployment_id not in self.deployments:
            return None

        deployment = self.deployments[deployment_id]
        deployment.status = DeploymentStatus.ROLLED_BACK
        deployment.rollback_to = rollback_to
        deployment.logs.append(f"Rolled back to {rollback_to} by {rolled_back_by}")

        logger.warning(f"Deployment {deployment_id} rolled back to {rollback_to}")
        return deployment

    def get_deployments(
        self,
        environment: Optional[str] = None,
        status: Optional[DeploymentStatus] = None,
        limit: int = 50,
    ) -> List[Deployment]:
        """Get deployments with filtering."""
        deployments = list(self.deployments.values())

        if environment:
            deployments = [d for d in deployments if d.environment == environment]

        if status:
            deployments = [d for d in deployments if d.status == status]

        # Sort by creation time (newest first)
        deployments.sort(key=lambda x: x.created_at, reverse=True)

        return deployments[:limit]

    # ============================================
    # CI/CD Pipeline Management
    # ============================================

    def create_pipeline(
        self,
        name: str,
        repository: str,
        branch: str,
        stages: List[str],
    ) -> Pipeline:
        """Create a new CI/CD pipeline."""
        pipeline = Pipeline(
            pipeline_id=self._generate_id("pipeline"),
            name=name,
            repository=repository,
            branch=branch,
            status=PipelineStatus.QUEUED,
            stages=stages,
        )

        self.pipelines[pipeline.pipeline_id] = pipeline
        logger.info(f"Created pipeline: {pipeline.pipeline_id} - {name}")
        return pipeline

    def start_pipeline(self, pipeline_id: str) -> Optional[Pipeline]:
        """Start a queued pipeline."""
        if pipeline_id not in self.pipelines:
            return None

        pipeline = self.pipelines[pipeline_id]
        pipeline.status = PipelineStatus.RUNNING
        pipeline.started_at = datetime.utcnow()
        pipeline.current_stage = pipeline.stages[0] if pipeline.stages else None

        return pipeline

    def update_pipeline_stage(
        self,
        pipeline_id: str,
        stage: str,
        status: str,  # passed, failed
    ) -> Optional[Pipeline]:
        """Update pipeline stage status."""
        if pipeline_id not in self.pipelines:
            return None

        pipeline = self.pipelines[pipeline_id]

        if status == "failed":
            pipeline.status = PipelineStatus.FAILED
            pipeline.completed_at = datetime.utcnow()
        else:
            # Move to next stage
            current_idx = pipeline.stages.index(stage) if stage in pipeline.stages else -1
            if current_idx >= 0 and current_idx < len(pipeline.stages) - 1:
                pipeline.current_stage = pipeline.stages[current_idx + 1]
            else:
                pipeline.status = PipelineStatus.PASSED
                pipeline.completed_at = datetime.utcnow()

        return pipeline

    def get_pipelines(
        self,
        status: Optional[PipelineStatus] = None,
        limit: int = 50,
    ) -> List[Pipeline]:
        """Get pipelines with filtering."""
        pipelines = list(self.pipelines.values())

        if status:
            pipelines = [p for p in pipelines if p.status == status]

        pipelines.sort(key=lambda x: x.started_at or datetime.min, reverse=True)
        return pipelines[:limit]

    # ============================================
    # Infrastructure Management
    # ============================================

    def register_resource(self, resource: InfrastructureResource):
        """Register an infrastructure resource."""
        self.infrastructure[resource.resource_id] = resource
        logger.info(f"Registered resource: {resource.resource_id} ({resource.resource_type.value})")

    def update_resource_status(
        self,
        resource_id: str,
        status: str,
    ) -> Optional[InfrastructureResource]:
        """Update resource status."""
        if resource_id not in self.infrastructure:
            return None

        resource = self.infrastructure[resource_id]
        resource.status = status

        return resource

    def get_resource_costs(self, hours: int = 24) -> Dict[str, float]:
        """Calculate resource costs for time period."""
        costs = {}
        total = 0.0

        for resource in self.infrastructure.values():
            if resource.status == 'running':
                cost = resource.cost_per_hour * hours
                costs[resource.resource_id] = cost
                total += cost

        costs['total'] = total
        return costs

    def get_infrastructure_summary(self) -> Dict[str, Any]:
        """Get infrastructure summary."""
        by_type = {}
        by_status = {}
        total_cost = 0.0

        for resource in self.infrastructure.values():
            # By type
            rtype = resource.resource_type.value
            by_type[rtype] = by_type.get(rtype, 0) + 1

            # By status
            by_status[resource.status] = by_status.get(resource.status, 0) + 1

            # Cost
            if resource.status == 'running':
                total_cost += resource.cost_per_hour

        return {
            'total_resources': len(self.infrastructure),
            'by_type': by_type,
            'by_status': by_status,
            'hourly_cost': total_cost,
            'daily_cost': total_cost * 24,
            'monthly_cost': total_cost * 24 * 30,
        }

    # ============================================
    # Monitoring & Alerting
    # ============================================

    def record_metric(self, metric_name: str, value: float, tags: Optional[Dict[str, str]] = None):
        """Record a metric data point."""
        if metric_name not in self.metrics:
            self.metrics[metric_name] = []

        self.metrics[metric_name].append({
            'timestamp': datetime.utcnow().isoformat(),
            'value': value,
            'tags': tags or {},
        })

        # Keep last 1000 data points
        if len(self.metrics[metric_name]) > 1000:
            self.metrics[metric_name] = self.metrics[metric_name][-1000:]

    def create_alert(
        self,
        name: str,
        severity: str,
        metric: str,
        threshold: float,
        current_value: float,
    ) -> Alert:
        """Create a monitoring alert."""
        alert = Alert(
            alert_id=self._generate_id("alert"),
            name=name,
            severity=severity,
            metric=metric,
            threshold=threshold,
            current_value=current_value,
        )

        self.alerts[alert.alert_id] = alert
        logger.warning(f"Alert created: {alert.name} - {metric} = {current_value} (threshold: {threshold})")
        return alert

    def acknowledge_alert(self, alert_id: str, acknowledged_by: str) -> bool:
        """Acknowledge an alert."""
        if alert_id not in self.alerts:
            return False

        self.alerts[alert_id].acknowledged = True
        self.alerts[alert_id].acknowledged_by = acknowledged_by

        return True

    def resolve_alert(self, alert_id: str) -> bool:
        """Resolve an alert."""
        if alert_id not in self.alerts:
            return False

        self.alerts[alert_id].resolved_at = datetime.utcnow()

        return True

    def get_active_alerts(self, severity: Optional[str] = None) -> List[Alert]:
        """Get active (unresolved) alerts."""
        alerts = [a for a in self.alerts.values() if not a.resolved_at]

        if severity:
            alerts = [a for a in alerts if a.severity == severity]

        return alerts

    def check_thresholds(self) -> List[Alert]:
        """Check metrics against thresholds and create alerts."""
        new_alerts = []

        # Example thresholds
        thresholds = {
            'cpu_usage': {'warning': 70.0, 'critical': 90.0},
            'memory_usage': {'warning': 75.0, 'critical': 95.0},
            'disk_usage': {'warning': 80.0, 'critical': 95.0},
            'error_rate': {'warning': 1.0, 'critical': 5.0},
            'latency_p99': {'warning': 500.0, 'critical': 1000.0},
        }

        for metric_name, limits in thresholds.items():
            if metric_name in self.metrics and self.metrics[metric_name]:
                latest = self.metrics[metric_name][-1]['value']

                if latest >= limits['critical']:
                    alert = self.create_alert(
                        name=f"Critical: {metric_name}",
                        severity="critical",
                        metric=metric_name,
                        threshold=limits['critical'],
                        current_value=latest,
                    )
                    new_alerts.append(alert)
                elif latest >= limits['warning']:
                    alert = self.create_alert(
                        name=f"Warning: {metric_name}",
                        severity="warning",
                        metric=metric_name,
                        threshold=limits['warning'],
                        current_value=latest,
                    )
                    new_alerts.append(alert)

        return new_alerts

    # ============================================
    # Cost Optimization
    # ============================================

    def get_cost_report(self, days: int = 30) -> Dict[str, Any]:
        """Generate cost optimization report."""
        summary = self.get_infrastructure_summary()

        # Identify optimization opportunities
        opportunities = []

        # Check for stopped resources still incurring costs
        for resource in self.infrastructure.values():
            if resource.status == 'stopped' and resource.cost_per_hour > 0:
                opportunities.append({
                    'type': 'stopped_resource',
                    'resource_id': resource.resource_id,
                    'recommendation': f"Terminate or snapshot {resource.name}",
                    'savings_per_month': resource.cost_per_hour * 24 * 30,
                })

        # Check for underutilized resources (simulated)
        for resource in self.infrastructure.values():
            if resource.resource_type == InfrastructureType.VM and resource.status == 'running':
                # In production, check actual utilization
                opportunities.append({
                    'type': 'rightsizing',
                    'resource_id': resource.resource_id,
                    'recommendation': f"Review sizing for {resource.name}",
                    'potential_savings': resource.cost_per_hour * 0.3 * 24 * 30,  # Estimate 30% savings
                })

        return {
            'period_days': days,
            'current_costs': summary,
            'optimization_opportunities': opportunities,
            'potential_monthly_savings': sum(o['potential_savings'] for o in opportunities),
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
            'deployments_count': len(self.deployments),
            'pipelines_count': len(self.pipelines),
            'resources_count': len(self.infrastructure),
            'active_alerts': len(self.get_active_alerts()),
            'critical_alerts': len([a for a in self.alerts.values() if a.severity == 'critical' and not a.resolved_at]),
        }


def get_capabilities() -> Dict[str, Any]:
    """Return agent capabilities for orchestration."""
    return {
        'agent_type': 'devops',
        'version': '1.0.0',
        'capabilities': [
            'create_deployment',
            'update_deployment_status',
            'rollback_deployment',
            'get_deployments',
            'create_pipeline',
            'start_pipeline',
            'update_pipeline_stage',
            'get_pipelines',
            'register_resource',
            'update_resource_status',
            'get_resource_costs',
            'get_infrastructure_summary',
            'record_metric',
            'create_alert',
            'acknowledge_alert',
            'resolve_alert',
            'get_active_alerts',
            'check_thresholds',
            'get_cost_report',
        ],
        'deployment_statuses': [s.value for s in DeploymentStatus],
        'pipeline_statuses': [s.value for s in PipelineStatus],
        'infrastructure_types': [t.value for t in InfrastructureType],
    }


if __name__ == "__main__":
    # Quick test
    agent = DevOpsAgent()

    # Create deployment
    deployment = agent.create_deployment(
        application="my-app",
        version="1.2.0",
        environment="production",
        deployed_by="ci-bot",
    )

    print(f"Created deployment: {deployment.deployment_id}")
    print(f"State: {agent.get_state()}")
