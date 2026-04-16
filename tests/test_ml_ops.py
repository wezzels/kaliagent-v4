"""
MLOpsAgent Tests
================

Unit tests for MLOpsAgent - ML lifecycle, deployment & monitoring.
"""

import pytest
from datetime import datetime, timedelta

from agentic_ai.agents.ml_ops import (
    MLOpsAgent,
    ModelStage,
    ModelStatus,
    ExperimentStatus,
    DeploymentStrategy,
    AlertType,
)


class TestMLOpsAgent:
    """Test MLOpsAgent."""
    
    @pytest.fixture
    def mlops(self):
        """Create MLOpsAgent instance."""
        return MLOpsAgent()
    
    def test_register_dataset(self, mlops):
        """Test registering dataset."""
        dataset = mlops.register_dataset(
            name="Training Data",
            description="ML training dataset",
            location="s3://bucket/data",
            record_count=10000,
            feature_count=20,
            version="1.0",
            owner="data-team@example.com",
            tags=['training', 'production'],
        )
        
        assert dataset.dataset_id.startswith("data-")
        assert dataset.record_count == 10000
        assert dataset.feature_count == 20
        assert 'training' in dataset.tags
    
    def test_get_datasets_by_tag(self, mlops):
        """Test filtering datasets by tag."""
        mlops.register_dataset("DS1", "Desc", "loc", 1000, 10, tags=['training'])
        mlops.register_dataset("DS2", "Desc", "loc", 2000, 20, tags=['validation'])
        mlops.register_dataset("DS3", "Desc", "loc", 3000, 30, tags=['training', 'test'])
        
        training = mlops.get_datasets(tag='training')
        
        assert len(training) == 2
    
    def test_create_experiment(self, mlops):
        """Test creating experiment."""
        dataset = mlops.register_dataset("Test", "Desc", "loc", 1000, 10)
        
        experiment = mlops.create_experiment(
            name="Experiment v1",
            description="Test experiment",
            model_type="xgboost",
            dataset_id=dataset.dataset_id,
            hyperparameters={'learning_rate': 0.1, 'max_depth': 5},
            created_by="ml@example.com",
        )
        
        assert experiment.experiment_id.startswith("exp-")
        assert experiment.status == ExperimentStatus.PLANNED
        assert experiment.hyperparameters['learning_rate'] == 0.1
    
    def test_start_experiment(self, mlops):
        """Test starting experiment."""
        experiment = mlops.create_experiment(
            "Test", "Desc", "xgboost", None, {}, "user",
        )
        
        result = mlops.start_experiment(experiment.experiment_id)
        
        assert result is True
        assert experiment.status == ExperimentStatus.RUNNING
        assert experiment.started_at is not None
    
    def test_complete_experiment(self, mlops):
        """Test completing experiment."""
        experiment = mlops.create_experiment(
            "Test", "Desc", "xgboost", None, {}, "user",
        )
        mlops.start_experiment(experiment.experiment_id)
        
        result = mlops.complete_experiment(
            experiment.experiment_id,
            metrics={'accuracy': 0.95, 'f1': 0.93},
            artifacts=['model.pkl', 'metrics.json'],
        )
        
        assert result is True
        assert experiment.status == ExperimentStatus.COMPLETED
        assert experiment.completed_at is not None
        assert experiment.metrics['accuracy'] == 0.95
        assert len(experiment.artifacts) == 2
    
    def test_get_experiments_by_status(self, mlops):
        """Test filtering experiments by status."""
        e1 = mlops.create_experiment("E1", "Desc", "xgboost", None, {}, "user")
        e2 = mlops.create_experiment("E2", "Desc", "pytorch", None, {}, "user")
        e3 = mlops.create_experiment("E3", "Desc", "tensorflow", None, {}, "user")
        
        mlops.start_experiment(e2.experiment_id)
        mlops.start_experiment(e3.experiment_id)
        mlops.complete_experiment(e3.experiment_id, {})
        
        running = mlops.get_experiments(status=ExperimentStatus.RUNNING)
        completed = mlops.get_experiments(status=ExperimentStatus.COMPLETED)
        
        assert len(running) == 1
        assert len(completed) == 1
    
    def test_register_model(self, mlops):
        """Test registering model."""
        experiment = mlops.create_experiment(
            "Test Exp", "Desc", "xgboost", None,
            {'lr': 0.1}, "user",
        )
        mlops.complete_experiment(experiment.experiment_id, {'accuracy': 0.92})
        
        model = mlops.register_model(
            name="Churn Model",
            description="Customer churn predictor",
            framework="xgboost",
            experiment_id=experiment.experiment_id,
            version="1.0",
            owner="ml-team@example.com",
        )
        
        assert model.model_id.startswith("model-")
        assert model.stage == ModelStage.DEVELOPMENT
        assert model.status == ModelStatus.READY
        assert model.metrics['accuracy'] == 0.92
    
    def test_update_model_stage(self, mlops):
        """Test updating model stage."""
        model = mlops.register_model(
            "Test", "Desc", "xgboost", None, "1.0", "user",
        )
        
        # Promote to staging
        mlops.update_model_stage(model.model_id, ModelStage.STAGING)
        assert model.stage == ModelStage.STAGING
        
        # Promote to production
        mlops.update_model_stage(model.model_id, ModelStage.PRODUCTION)
        assert model.stage == ModelStage.PRODUCTION
        assert model.status == ModelStatus.DEPLOYED
        assert model.deployed_at is not None
    
    def test_get_models_by_stage(self, mlops):
        """Test filtering models by stage."""
        m1 = mlops.register_model("M1", "Desc", "xgboost", None, "1.0", "user")
        m2 = mlops.register_model("M2", "Desc", "pytorch", None, "1.0", "user")
        m3 = mlops.register_model("M3", "Desc", "tensorflow", None, "1.0", "user")
        
        mlops.update_model_stage(m2.model_id, ModelStage.STAGING)
        mlops.update_model_stage(m3.model_id, ModelStage.PRODUCTION)
        
        prod = mlops.get_models(stage=ModelStage.PRODUCTION)
        dev = mlops.get_models(stage=ModelStage.DEVELOPMENT)
        
        assert len(prod) == 1
        assert len(dev) == 1
    
    def test_deploy_model(self, mlops):
        """Test deploying model."""
        model = mlops.register_model("Test", "Desc", "xgboost", None, "1.0", "user")
        
        deployment = mlops.deploy_model(
            model_id=model.model_id,
            environment="production",
            endpoint="https://api.example.com/predict",
            strategy=DeploymentStrategy.CANARY,
            instances=3,
            config={'min_instances': 2},
        )
        
        assert deployment.deployment_id.startswith("deploy-")
        assert deployment.status == "deploying"
        assert deployment.strategy == DeploymentStrategy.CANARY
        assert model.stage == ModelStage.PRODUCTION
    
    def test_update_deployment_status(self, mlops):
        """Test updating deployment status."""
        model = mlops.register_model("Test", "Desc", "xgboost", None, "1.0", "user")
        deployment = mlops.deploy_model(model.model_id, "production", "endpoint")
        
        result = mlops.update_deployment_status(
            deployment.deployment_id,
            "running",
            health_status="healthy",
        )
        
        assert result is True
        assert deployment.status == "running"
        assert deployment.health_status == "healthy"
        assert deployment.deployed_at is not None
    
    def test_get_deployments_by_environment(self, mlops):
        """Test filtering deployments by environment."""
        model = mlops.register_model("Test", "Desc", "xgboost", None, "1.0", "user")
        
        d1 = mlops.deploy_model(model.model_id, "staging", "staging-endpoint")
        d2 = mlops.deploy_model(model.model_id, "production", "prod-endpoint")
        
        prod = mlops.get_deployments(environment="production")
        staging = mlops.get_deployments(environment="staging")
        
        assert len(prod) == 1
        assert len(staging) == 1
    
    def test_create_monitor(self, mlops):
        """Test creating model monitor."""
        model = mlops.register_model("Test", "Desc", "xgboost", None, "1.0", "user")
        
        monitor = mlops.create_monitor(
            model_id=model.model_id,
            metrics_to_track=['accuracy', 'latency_p99'],
            baseline_metrics={'accuracy': 0.95, 'latency_p99': 100},
            thresholds={'accuracy': 0.05, 'latency_p99': 50},
            check_frequency="hourly",
            alert_channels=['slack', 'pagerduty'],
        )
        
        assert monitor.monitor_id.startswith("monitor-")
        assert len(monitor.metrics_to_track) == 2
        assert monitor.thresholds['accuracy'] == 0.05
    
    def test_check_model_metrics(self, mlops):
        """Test checking metrics and generating alerts."""
        model = mlops.register_model("Test", "Desc", "xgboost", None, "1.0", "user")
        
        mlops.create_monitor(
            model.model_id,
            metrics_to_track=['accuracy'],
            baseline_metrics={'accuracy': 0.95},
            thresholds={'accuracy': 0.05},
            check_frequency="hourly",
        )
        
        # Normal metrics - no alert
        alerts = mlops.check_model_metrics(model.model_id, {'accuracy': 0.93})
        assert len(alerts) == 0
        
        # Drift detected - alert generated
        alerts = mlops.check_model_metrics(model.model_id, {'accuracy': 0.85})
        assert len(alerts) >= 1
        assert alerts[0].alert_type in [AlertType.DATA_DRIFT, AlertType.PERFORMANCE_DEGRADATION]
    
    def test_create_alert(self, mlops):
        """Test creating alert."""
        model = mlops.register_model("Test", "Desc", "xgboost", None, "1.0", "user")
        
        alert = mlops.create_alert(
            model_id=model.model_id,
            alert_type=AlertType.DATA_DRIFT,
            severity="high",
            title="Accuracy drift detected",
            description="Accuracy dropped below threshold",
            current_value=0.85,
            threshold=0.90,
        )
        
        assert alert.alert_id.startswith("alert-")
        assert alert.status == "open"
        assert alert.severity == "high"
    
    def test_resolve_alert(self, mlops):
        """Test resolving alert."""
        alert = mlops.create_alert(
            None, AlertType.DATA_DRIFT, "high",
            "Title", "Desc", 0.85, 0.90,
        )
        
        result = mlops.resolve_alert(alert.alert_id)
        
        assert result is True
        assert alert.status == "resolved"
        assert alert.resolved_at is not None
    
    def test_get_alerts_by_severity(self, mlops):
        """Test filtering alerts by severity."""
        mlops.create_alert(None, AlertType.DATA_DRIFT, "low", "T", "D", 0.1, 0.2)
        mlops.create_alert(None, AlertType.DATA_DRIFT, "medium", "T", "D", 0.1, 0.2)
        mlops.create_alert(None, AlertType.DATA_DRIFT, "high", "T", "D", 0.1, 0.2)
        mlops.create_alert(None, AlertType.DATA_DRIFT, "critical", "T", "D", 0.1, 0.2)
        
        high = mlops.get_alerts(severity="high")
        critical = mlops.get_alerts(severity="critical")
        
        assert len(high) == 1
        assert len(critical) == 1
    
    def test_get_mlops_dashboard(self, mlops):
        """Test MLOps dashboard generation."""
        # Create models at different stages
        m1 = mlops.register_model("M1", "Desc", "xgboost", None, "1.0", "user")
        m2 = mlops.register_model("M2", "Desc", "pytorch", None, "1.0", "user")
        m3 = mlops.register_model("M3", "Desc", "tensorflow", None, "1.0", "user")
        
        mlops.update_model_stage(m3.model_id, ModelStage.PRODUCTION)
        
        # Create deployment
        mlops.deploy_model(m3.model_id, "production", "endpoint")
        
        # Create alerts
        mlops.create_alert(m3.model_id, AlertType.DATA_DRIFT, "high", "T", "D", 0.1, 0.2)
        
        dashboard = mlops.get_mlops_dashboard()
        
        assert 'models' in dashboard
        assert 'experiments' in dashboard
        assert 'deployments' in dashboard
        assert 'monitoring' in dashboard
        assert dashboard['models']['production'] == 1
    
    def test_get_model_performance(self, mlops):
        """Test model performance report."""
        model = mlops.register_model(
            "Test Model", "Desc", "xgboost", None, "1.0", "user",
        )
        mlops.complete_experiment(
            mlops.experiments[model.experiment_id].experiment_id if model.experiment_id else mlops.create_experiment("E", "D", "xgboost", None, {}, "u").experiment_id,
            {'accuracy': 0.92, 'f1': 0.90},
        )
        
        mlops.update_model_stage(model.model_id, ModelStage.PRODUCTION)
        mlops.deploy_model(model.model_id, "production", "endpoint")
        
        mlops.create_alert(
            model.model_id, AlertType.DATA_DRIFT, "medium",
            "Drift", "Desc", 0.85, 0.90,
        )
        
        perf = mlops.get_model_performance(model.model_id)
        
        assert 'model' in perf
        assert 'metrics' in perf
        assert 'deployments' in perf
        assert 'alerts' in perf
    
    def test_frameworks_list(self, mlops):
        """Test supported frameworks."""
        frameworks = mlops.frameworks
        
        assert 'tensorflow' in frameworks
        assert 'pytorch' in frameworks
        assert 'sklearn' in frameworks
        assert 'xgboost' in frameworks


class TestMLOpsCapabilities:
    """Test MLOpsAgent capabilities export."""
    
    def test_capabilities(self):
        """Test capabilities export."""
        from agentic_ai.agents.ml_ops import get_capabilities
        caps = get_capabilities()
        
        assert caps['agent_type'] == 'mlops'
        assert len(caps['capabilities']) >= 19
        assert 'register_model' in caps['capabilities']
        assert 'deploy_model' in caps['capabilities']
        assert 'create_monitor' in caps['capabilities']
    
    def test_model_stages(self):
        """Test model stages in capabilities."""
        from agentic_ai.agents.ml_ops import get_capabilities
        caps = get_capabilities()
        
        assert 'development' in caps['model_stages']
        assert 'staging' in caps['model_stages']
        assert 'production' in caps['model_stages']
    
    def test_deployment_strategies(self):
        """Test deployment strategies in capabilities."""
        from agentic_ai.agents.ml_ops import get_capabilities
        caps = get_capabilities()
        
        assert 'immediate' in caps['deployment_strategies']
        assert 'canary' in caps['deployment_strategies']
        assert 'blue_green' in caps['deployment_strategies']
    
    def test_alert_types(self):
        """Test alert types in capabilities."""
        from agentic_ai.agents.ml_ops import get_capabilities
        caps = get_capabilities()
        
        assert 'data_drift' in caps['alert_types']
        assert 'concept_drift' in caps['alert_types']
        assert 'performance_degradation' in caps['alert_types']


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
