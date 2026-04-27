"""
MLOpsAgent - Machine Learning Operations
=========================================

Provides ML model lifecycle management, training pipelines, model registry,
experiment tracking, deployment automation, and model monitoring.
"""

import logging
import secrets
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from typing import Any, Dict, List, Optional


logger = logging.getLogger(__name__)


class ModelStage(Enum):
    """Model lifecycle stages."""
    DEVELOPMENT = "development"
    STAGING = "staging"
    PRODUCTION = "production"
    ARCHIVED = "archived"
    DEPRECATED = "deprecated"


class ModelStatus(Enum):
    """Model status."""
    TRAINING = "training"
    EVALUATING = "evaluating"
    READY = "ready"
    DEPLOYED = "deployed"
    FAILED = "failed"


class ExperimentStatus(Enum):
    """Experiment status."""
    PLANNED = "planned"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    STOPPED = "stopped"


class DeploymentStrategy(Enum):
    """Deployment strategies."""
    IMMEDIATE = "immediate"
    CANARY = "canary"
    BLUE_GREEN = "blue_green"
    SHADOW = "shadow"


class AlertType(Enum):
    """Alert types."""
    DATA_DRIFT = "data_drift"
    CONCEPT_DRIFT = "concept_drift"
    PERFORMANCE_DEGRADATION = "performance_degradation"
    LATENCY_SPIKE = "latency_spike"
    ERROR_RATE = "error_rate"


@dataclass
class Dataset:
    """ML dataset."""
    dataset_id: str
    name: str
    description: str
    version: str
    location: str  # S3, GCS, etc.
    record_count: int
    feature_count: int
    created_at: datetime = field(default_factory=datetime.utcnow)
    owner: str = ""
    tags: List[str] = field(default_factory=list)


@dataclass
class Experiment:
    """ML experiment."""
    experiment_id: str
    name: str
    description: str
    status: ExperimentStatus
    dataset_id: Optional[str]
    model_type: str
    hyperparameters: Dict[str, Any] = field(default_factory=dict)
    metrics: Dict[str, float] = field(default_factory=dict)
    artifacts: List[str] = field(default_factory=list)
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    created_by: str = ""


@dataclass
class Model:
    """ML model."""
    model_id: str
    name: str
    description: str
    version: str
    stage: ModelStage
    status: ModelStatus
    experiment_id: Optional[str]
    framework: str  # tensorflow, pytorch, sklearn, etc.
    metrics: Dict[str, float] = field(default_factory=dict)
    location: str = ""  # Model registry path
    input_schema: Dict[str, Any] = field(default_factory=dict)
    output_schema: Dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.utcnow)
    deployed_at: Optional[datetime] = None
    owner: str = ""


@dataclass
class Deployment:
    """Model deployment."""
    deployment_id: str
    model_id: str
    environment: str  # staging, production
    endpoint: str
    strategy: DeploymentStrategy
    status: str  # deploying, running, failed, stopped
    instances: int = 1
    traffic_percentage: float = 100.0
    health_status: str = "unknown"
    deployed_at: Optional[datetime] = None
    config: Dict[str, Any] = field(default_factory=dict)


@dataclass
class ModelMonitor:
    """Model monitoring config."""
    monitor_id: str
    model_id: str
    metrics_to_track: List[str]
    baseline_metrics: Dict[str, float]
    thresholds: Dict[str, float]
    check_frequency: str  # hourly, daily, weekly
    alert_channels: List[str] = field(default_factory=list)
    enabled: bool = True
    created_at: datetime = field(default_factory=datetime.utcnow)


@dataclass
class Alert:
    """Model alert."""
    alert_id: str
    model_id: Optional[str]
    deployment_id: Optional[str]
    alert_type: AlertType
    severity: str  # low, medium, high, critical
    title: str
    description: str
    current_value: float
    threshold: float
    status: str  # open, investigating, resolved
    created_at: datetime = field(default_factory=datetime.utcnow)
    resolved_at: Optional[datetime] = None


class MLOpsAgent:
    """
    MLOps Agent for ML lifecycle management,
    experiment tracking, deployment, and monitoring.
    """

    def __init__(self, agent_id: str = "mlops-agent"):
        self.agent_id = agent_id
        self.datasets: Dict[str, Dataset] = {}
        self.experiments: Dict[str, Experiment] = {}
        self.models: Dict[str, Model] = {}
        self.deployments: Dict[str, Deployment] = {}
        self.monitors: Dict[str, ModelMonitor] = {}
        self.alerts: Dict[str, Alert] = {}

        # Supported frameworks
        self.frameworks = ['tensorflow', 'pytorch', 'sklearn', 'xgboost', 'lightgbm', 'keras']

    # ============================================
    # Dataset Management
    # ============================================

    def register_dataset(
        self,
        name: str,
        description: str,
        location: str,
        record_count: int,
        feature_count: int,
        version: str = "1.0",
        owner: str = "",
        tags: Optional[List[str]] = None,
    ) -> Dataset:
        """Register a dataset."""
        dataset = Dataset(
            dataset_id=self._generate_id("data"),
            name=name,
            description=description,
            version=version,
            location=location,
            record_count=record_count,
            feature_count=feature_count,
            owner=owner,
            tags=tags or [],
        )

        self.datasets[dataset.dataset_id] = dataset
        return dataset

    def get_datasets(self, tag: Optional[str] = None) -> List[Dataset]:
        """Get datasets with filtering."""
        datasets = list(self.datasets.values())

        if tag:
            datasets = [d for d in datasets if tag in d.tags]

        return datasets

    # ============================================
    # Experiment Tracking
    # ============================================

    def create_experiment(
        self,
        name: str,
        description: str,
        model_type: str,
        dataset_id: Optional[str],
        hyperparameters: Optional[Dict[str, Any]],
        created_by: str,
    ) -> Experiment:
        """Create ML experiment."""
        experiment = Experiment(
            experiment_id=self._generate_id("exp"),
            name=name,
            description=description,
            status=ExperimentStatus.PLANNED,
            dataset_id=dataset_id,
            model_type=model_type,
            hyperparameters=hyperparameters or {},
            created_by=created_by,
        )

        self.experiments[experiment.experiment_id] = experiment
        return experiment

    def start_experiment(self, experiment_id: str) -> bool:
        """Start experiment."""
        if experiment_id not in self.experiments:
            return False

        self.experiments[experiment_id].status = ExperimentStatus.RUNNING
        self.experiments[experiment_id].started_at = datetime.utcnow()
        return True

    def complete_experiment(
        self,
        experiment_id: str,
        metrics: Dict[str, float],
        artifacts: Optional[List[str]] = None,
    ) -> bool:
        """Complete experiment with results."""
        if experiment_id not in self.experiments:
            return False

        experiment = self.experiments[experiment_id]
        experiment.status = ExperimentStatus.COMPLETED
        experiment.completed_at = datetime.utcnow()
        experiment.metrics = metrics
        experiment.artifacts = artifacts or []

        return True

    def get_experiments(
        self,
        status: Optional[ExperimentStatus] = None,
        model_type: Optional[str] = None,
    ) -> List[Experiment]:
        """Get experiments with filtering."""
        experiments = list(self.experiments.values())

        if status:
            experiments = [e for e in experiments if e.status == status]

        if model_type:
            experiments = [e for e in experiments if e.model_type == model_type]

        return experiments

    # ============================================
    # Model Registry
    # ============================================

    def register_model(
        self,
        name: str,
        description: str,
        framework: str,
        experiment_id: Optional[str],
        version: str = "1.0",
        owner: str = "",
        input_schema: Optional[Dict[str, Any]] = None,
        output_schema: Optional[Dict[str, Any]] = None,
    ) -> Model:
        """Register model in registry."""
        model = Model(
            model_id=self._generate_id("model"),
            name=name,
            description=description,
            version=version,
            stage=ModelStage.DEVELOPMENT,
            status=ModelStatus.READY,
            experiment_id=experiment_id,
            framework=framework,
            owner=owner,
            input_schema=input_schema or {},
            output_schema=output_schema or {},
        )

        self.models[model.model_id] = model

        # Copy metrics from experiment
        if experiment_id and experiment_id in self.experiments:
            model.metrics = self.experiments[experiment_id].metrics

        return model

    def update_model_stage(self, model_id: str, stage: ModelStage) -> bool:
        """Update model stage."""
        if model_id not in self.models:
            return False

        self.models[model_id].stage = stage

        if stage == ModelStage.PRODUCTION:
            self.models[model_id].deployed_at = datetime.utcnow()
            self.models[model_id].status = ModelStatus.DEPLOYED

        return True

    def get_models(
        self,
        stage: Optional[ModelStage] = None,
        framework: Optional[str] = None,
    ) -> List[Model]:
        """Get models with filtering."""
        models = list(self.models.values())

        if stage:
            models = [m for m in models if m.stage == stage]

        if framework:
            models = [m for m in models if m.framework == framework]

        return models

    # ============================================
    # Deployment
    # ============================================

    def deploy_model(
        self,
        model_id: str,
        environment: str,
        endpoint: str,
        strategy: DeploymentStrategy = DeploymentStrategy.IMMEDIATE,
        instances: int = 1,
        config: Optional[Dict[str, Any]] = None,
    ) -> Deployment:
        """Deploy model to environment."""
        if model_id not in self.models:
            raise ValueError(f"Model {model_id} not found")

        deployment = Deployment(
            deployment_id=self._generate_id("deploy"),
            model_id=model_id,
            environment=environment,
            endpoint=endpoint,
            strategy=strategy,
            status="deploying",
            instances=instances,
            config=config or {},
        )

        self.deployments[deployment.deployment_id] = deployment

        # Update model
        self.models[model_id].stage = ModelStage.PRODUCTION
        self.models[model_id].status = ModelStatus.DEPLOYED

        return deployment

    def update_deployment_status(
        self,
        deployment_id: str,
        status: str,
        health_status: Optional[str] = None,
    ) -> bool:
        """Update deployment status."""
        if deployment_id not in self.deployments:
            return False

        deployment = self.deployments[deployment_id]
        deployment.status = status

        if health_status:
            deployment.health_status = health_status

        if status == "running":
            deployment.deployed_at = datetime.utcnow()

        return True

    def get_deployments(
        self,
        environment: Optional[str] = None,
        status: Optional[str] = None,
    ) -> List[Deployment]:
        """Get deployments with filtering."""
        deployments = list(self.deployments.values())

        if environment:
            deployments = [d for d in deployments if d.environment == environment]

        if status:
            deployments = [d for d in deployments if d.status == status]

        return deployments

    # ============================================
    # Model Monitoring
    # ============================================

    def create_monitor(
        self,
        model_id: str,
        metrics_to_track: List[str],
        baseline_metrics: Dict[str, float],
        thresholds: Dict[str, float],
        check_frequency: str,
        alert_channels: Optional[List[str]] = None,
    ) -> ModelMonitor:
        """Create model monitor."""
        monitor = ModelMonitor(
            monitor_id=self._generate_id("monitor"),
            model_id=model_id,
            metrics_to_track=metrics_to_track,
            baseline_metrics=baseline_metrics,
            thresholds=thresholds,
            check_frequency=check_frequency,
            alert_channels=alert_channels or [],
        )

        self.monitors[monitor.monitor_id] = monitor
        return monitor

    def check_model_metrics(
        self,
        model_id: str,
        current_metrics: Dict[str, float],
    ) -> List[Alert]:
        """Check metrics against thresholds and create alerts."""
        monitors = [m for m in self.monitors.values() if m.model_id == model_id and m.enabled]
        alerts = []

        for monitor in monitors:
            for metric in monitor.metrics_to_track:
                if metric not in current_metrics:
                    continue

                threshold = monitor.thresholds.get(metric)
                baseline = monitor.baseline_metrics.get(metric, 0)
                current = current_metrics[metric]

                # Check for drift/degradation
                if threshold and abs(current - baseline) > threshold:
                    alert_type = AlertType.DATA_DRIFT if 'accuracy' in metric.lower() else AlertType.PERFORMANCE_DEGRADATION

                    alert = self.create_alert(
                        model_id=model_id,
                        alert_type=alert_type,
                        severity="high" if abs(current - baseline) > threshold * 2 else "medium",
                        title=f"{metric} drift detected",
                        description=f"{metric}: {current:.4f} (baseline: {baseline:.4f}, threshold: {threshold:.4f})",
                        current_value=current,
                        threshold=threshold,
                    )
                    alerts.append(alert)

        return alerts

    def create_alert(
        self,
        model_id: Optional[str],
        alert_type: AlertType,
        severity: str,
        title: str,
        description: str,
        current_value: float,
        threshold: float,
        deployment_id: Optional[str] = None,
    ) -> Alert:
        """Create model alert."""
        alert = Alert(
            alert_id=self._generate_id("alert"),
            model_id=model_id,
            deployment_id=deployment_id,
            alert_type=alert_type,
            severity=severity,
            title=title,
            description=description,
            current_value=current_value,
            threshold=threshold,
            status="open",
        )

        self.alerts[alert.alert_id] = alert
        return alert

    def resolve_alert(self, alert_id: str) -> bool:
        """Resolve alert."""
        if alert_id not in self.alerts:
            return False

        self.alerts[alert_id].status = "resolved"
        self.alerts[alert_id].resolved_at = datetime.utcnow()
        return True

    def get_alerts(
        self,
        alert_type: Optional[AlertType] = None,
        severity: Optional[str] = None,
        status: Optional[str] = None,
    ) -> List[Alert]:
        """Get alerts with filtering."""
        alerts = list(self.alerts.values())

        if alert_type:
            alerts = [a for a in alerts if a.alert_type == alert_type]

        if severity:
            alerts = [a for a in alerts if a.severity == severity]

        if status:
            alerts = [a for a in alerts if a.status == status]

        return alerts

    # ============================================
    # Reporting
    # ============================================

    def get_mlops_dashboard(self) -> Dict[str, Any]:
        """Generate MLOps dashboard."""
        models = list(self.models.values())
        experiments = list(self.experiments.values())
        deployments = list(self.deployments.values())
        alerts = list(self.alerts.values())

        # Models by stage
        by_stage = {}
        for stage in ModelStage:
            by_stage[stage.value] = len([m for m in models if m.stage == stage])

        # Experiments by status
        by_exp_status = {}
        for status in ExperimentStatus:
            by_exp_status[status.value] = len([e for e in experiments if e.status == status])

        # Active alerts
        open_alerts = len([a for a in alerts if a.status == "open"])
        critical_alerts = len([a for a in alerts if a.severity == "critical" and a.status == "open"])

        return {
            'models': {
                'total': len(models),
                'by_stage': by_stage,
                'production': by_stage.get('production', 0),
            },
            'experiments': {
                'total': len(experiments),
                'by_status': by_exp_status,
                'running': by_exp_status.get('running', 0),
            },
            'deployments': {
                'total': len(deployments),
                'running': len([d for d in deployments if d.status == 'running']),
                'production': len([d for d in deployments if d.environment == 'production']),
            },
            'monitoring': {
                'active_monitors': len([m for m in self.monitors.values() if m.enabled]),
                'alerts': {
                    'total': len(alerts),
                    'open': open_alerts,
                    'critical': critical_alerts,
                },
            },
        }

    def get_model_performance(self, model_id: str) -> Dict[str, Any]:
        """Get model performance report."""
        if model_id not in self.models:
            return {'error': 'Model not found'}

        model = self.models[model_id]
        deployments = [d for d in self.deployments.values() if d.model_id == model_id]
        alerts = [a for a in self.alerts.values() if a.model_id == model_id]

        return {
            'model': {
                'model_id': model_id,
                'name': model.name,
                'version': model.version,
                'stage': model.stage.value,
                'framework': model.framework,
            },
            'metrics': model.metrics,
            'deployments': [
                {
                    'deployment_id': d.deployment_id,
                    'environment': d.environment,
                    'status': d.status,
                    'health': d.health_status,
                }
                for d in deployments
            ],
            'alerts': {
                'total': len(alerts),
                'open': len([a for a in alerts if a.status == 'open']),
                'by_type': {
                    t.value: len([a for a in alerts if a.alert_type == t])
                    for t in AlertType
                },
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
            'datasets_count': len(self.datasets),
            'experiments_count': len(self.experiments),
            'models_count': len(self.models),
            'production_models': len([m for m in self.models.values() if m.stage == ModelStage.PRODUCTION]),
            'deployments_count': len(self.deployments),
            'active_deployments': len([d for d in self.deployments.values() if d.status == 'running']),
            'monitors_count': len(self.monitors),
            'open_alerts': len([a for a in self.alerts.values() if a.status == 'open']),
        }


def get_capabilities() -> Dict[str, Any]:
    """Return agent capabilities for orchestration."""
    return {
        'agent_type': 'mlops',
        'version': '1.0.0',
        'capabilities': [
            'register_dataset',
            'get_datasets',
            'create_experiment',
            'start_experiment',
            'complete_experiment',
            'get_experiments',
            'register_model',
            'update_model_stage',
            'get_models',
            'deploy_model',
            'update_deployment_status',
            'get_deployments',
            'create_monitor',
            'check_model_metrics',
            'create_alert',
            'resolve_alert',
            'get_alerts',
            'get_mlops_dashboard',
            'get_model_performance',
        ],
        'model_stages': [s.value for s in ModelStage],
        'model_statuses': [s.value for s in ModelStatus],
        'experiment_statuses': [s.value for s in ExperimentStatus],
        'deployment_strategies': [s.value for s in DeploymentStrategy],
        'alert_types': [t.value for t in AlertType],
        'frameworks': ['tensorflow', 'pytorch', 'sklearn', 'xgboost', 'lightgbm', 'keras'],
    }


if __name__ == "__main__":
    agent = MLOpsAgent()

    # Register dataset
    dataset = agent.register_dataset(
        name="Customer Churn Dataset",
        description="Historical customer data for churn prediction",
        location="s3://ml-data/churn/v1",
        record_count=100000,
        feature_count=25,
        owner="data-team@example.com",
        tags=['churn', 'customers', 'production'],
    )

    print(f"Registered dataset: {dataset.name}")

    # Create experiment
    experiment = agent.create_experiment(
        name="Churn Prediction v1",
        description="XGBoost model for churn prediction",
        model_type="xgboost",
        dataset_id=dataset.dataset_id,
        hyperparameters={'max_depth': 6, 'learning_rate': 0.1, 'n_estimators': 100},
        created_by="ml-engineer@example.com",
    )

    agent.start_experiment(experiment.experiment_id)

    # Complete experiment
    agent.complete_experiment(
        experiment.experiment_id,
        metrics={'accuracy': 0.92, 'precision': 0.89, 'recall': 0.87, 'f1': 0.88},
        artifacts=['model.pkl', 'scaler.pkl', 'feature_importance.png'],
    )

    print(f"Experiment completed: {experiment.metrics}")

    # Register model
    model = agent.register_model(
        name="Churn Predictor",
        description="XGBoost model for customer churn",
        framework="xgboost",
        experiment_id=experiment.experiment_id,
        version="1.0",
        owner="ml-team@example.com",
    )

    print(f"Registered model: {model.name}")

    # Promote to production
    agent.update_model_stage(model.model_id, ModelStage.PRODUCTION)

    # Deploy model
    deployment = agent.deploy_model(
        model_id=model.model_id,
        environment="production",
        endpoint="https://api.example.com/v1/predict/churn",
        strategy=DeploymentStrategy.CANARY,
        instances=3,
        config={'min_instances': 2, 'max_instances': 10},
    )

    agent.update_deployment_status(deployment.deployment_id, "running", "healthy")

    print(f"Deployed to: {deployment.endpoint}")

    # Create monitor
    monitor = agent.create_monitor(
        model_id=model.model_id,
        metrics_to_track=['accuracy', 'latency_p99', 'error_rate'],
        baseline_metrics={'accuracy': 0.92, 'latency_p99': 100, 'error_rate': 0.01},
        thresholds={'accuracy': 0.05, 'latency_p99': 50, 'error_rate': 0.02},
        check_frequency="hourly",
        alert_channels=['slack', 'pagerduty'],
    )

    # Simulate drift detection
    alerts = agent.check_model_metrics(
        model.model_id,
        current_metrics={'accuracy': 0.85, 'latency_p99': 120, 'error_rate': 0.015},
    )

    print(f"Generated {len(alerts)} alerts")

    # Get dashboard
    dashboard = agent.get_mlops_dashboard()
    print(f"\nMLOps Dashboard:")
    print(f"  Models: {dashboard['models']['total']}")
    print(f"  Production: {dashboard['models']['production']}")
    print(f"  Open Alerts: {dashboard['monitoring']['alerts']['open']}")

    print(f"\nState: {agent.get_state()}")
