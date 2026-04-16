"""
DevOpsAgent Tests
=================

Unit tests for DevOpsAgent - infrastructure automation, CI/CD,
deployment orchestration, and monitoring.
"""

import pytest
from datetime import datetime, timedelta

from agentic_ai.agents.devops import (
    DevOpsAgent,
    DeploymentStatus,
    PipelineStatus,
    InfrastructureType,
)


class TestDevOpsAgentInitialization:
    """Test DevOpsAgent initialization."""
    
    def test_agent_creation(self):
        """Test agent can be created."""
        from agentic_ai.agents.devops import DevOpsAgent
        
        agent = DevOpsAgent()
        assert agent.agent_id == "devops-agent"
        assert len(agent.infrastructure) >= 2  # Default resources
    
    def test_get_state(self):
        """Test state summary."""
        agent = DevOpsAgent()
        state = agent.get_state()
        
        assert 'agent_id' in state
        assert 'deployments_count' in state
        assert 'pipelines_count' in state
        assert 'resources_count' in state
        assert 'active_alerts' in state


class TestDeploymentManagement:
    """Test deployment management."""
    
    @pytest.fixture
    def devops_agent(self):
        """Create DevOpsAgent instance."""
        return DevOpsAgent()
    
    def test_create_deployment(self, devops_agent):
        """Test deployment creation."""
        deployment = devops_agent.create_deployment(
            application="my-app",
            version="1.0.0",
            environment="production",
            deployed_by="ci-bot",
        )
        
        assert deployment.deployment_id.startswith("deploy-")
        assert deployment.application == "my-app"
        assert deployment.version == "1.0.0"
        assert deployment.environment == "production"
        assert deployment.status == DeploymentStatus.PENDING
    
    def test_update_deployment_status(self, devops_agent):
        """Test deployment status updates."""
        deployment = devops_agent.create_deployment(
            application="my-app",
            version="1.0.0",
            environment="production",
            deployed_by="ci-bot",
        )
        
        # Update to deploying
        updated = devops_agent.update_deployment_status(
            deployment.deployment_id,
            DeploymentStatus.DEPLOYING,
            logs=["Starting deployment..."],
        )
        
        assert updated.status == DeploymentStatus.DEPLOYING
        assert len(updated.logs) >= 1
        
        # Complete deployment
        updated = devops_agent.update_deployment_status(
            deployment.deployment_id,
            DeploymentStatus.DEPLOYED,
        )
        
        assert updated.status == DeploymentStatus.DEPLOYED
        assert updated.deployed_at is not None
    
    def test_rollback_deployment(self, devops_agent):
        """Test deployment rollback."""
        deployment = devops_agent.create_deployment(
            application="my-app",
            version="2.0.0",
            environment="production",
            deployed_by="ci-bot",
        )
        
        # Rollback
        updated = devops_agent.rollback_deployment(
            deployment.deployment_id,
            rollback_to="1.0.0",
            rolled_back_by="admin",
        )
        
        assert updated.status == DeploymentStatus.ROLLED_BACK
        assert updated.rollback_to == "1.0.0"
    
    def test_get_deployments_filter(self, devops_agent):
        """Test filtering deployments."""
        # Create multiple deployments
        devops_agent.create_deployment("app1", "1.0", "dev", "user1")
        devops_agent.create_deployment("app2", "1.0", "prod", "user2")
        devops_agent.create_deployment("app3", "1.0", "prod", "user3")
        
        # Filter by environment
        prod = devops_agent.get_deployments(environment="prod")
        assert len(prod) == 2
        
        # Get all
        all_deps = devops_agent.get_deployments()
        assert len(all_deps) == 3


class TestPipelineManagement:
    """Test CI/CD pipeline management."""
    
    @pytest.fixture
    def devops_agent(self):
        """Create DevOpsAgent instance."""
        return DevOpsAgent()
    
    def test_create_pipeline(self, devops_agent):
        """Test pipeline creation."""
        pipeline = devops_agent.create_pipeline(
            name="Main CI",
            repository="my-app",
            branch="main",
            stages=["build", "test", "deploy"],
        )
        
        assert pipeline.pipeline_id.startswith("pipeline-")
        assert pipeline.name == "Main CI"
        assert pipeline.status == PipelineStatus.QUEUED
        assert len(pipeline.stages) == 3
    
    def test_start_pipeline(self, devops_agent):
        """Test starting a pipeline."""
        pipeline = devops_agent.create_pipeline(
            name="Main CI",
            repository="my-app",
            branch="main",
            stages=["build", "test", "deploy"],
        )
        
        started = devops_agent.start_pipeline(pipeline.pipeline_id)
        
        assert started.status == PipelineStatus.RUNNING
        assert started.started_at is not None
        assert started.current_stage == "build"
    
    def test_pipeline_stage_progression(self, devops_agent):
        """Test pipeline stage progression."""
        pipeline = devops_agent.create_pipeline(
            name="Main CI",
            repository="my-app",
            branch="main",
            stages=["build", "test", "deploy"],
        )
        
        devops_agent.start_pipeline(pipeline.pipeline_id)
        
        # Pass build stage
        updated = devops_agent.update_pipeline_stage(
            pipeline.pipeline_id,
            "build",
            "passed",
        )
        
        assert updated.current_stage == "test"
        assert updated.status == PipelineStatus.RUNNING
        
        # Pass test stage
        updated = devops_agent.update_pipeline_stage(
            pipeline.pipeline_id,
            "test",
            "passed",
        )
        
        assert updated.current_stage == "deploy"
        
        # Pass deploy stage (completes pipeline)
        updated = devops_agent.update_pipeline_stage(
            pipeline.pipeline_id,
            "deploy",
            "passed",
        )
        
        assert updated.status == PipelineStatus.PASSED
        assert updated.completed_at is not None
    
    def test_pipeline_failure(self, devops_agent):
        """Test pipeline failure handling."""
        pipeline = devops_agent.create_pipeline(
            name="Main CI",
            repository="my-app",
            branch="main",
            stages=["build", "test", "deploy"],
        )
        
        devops_agent.start_pipeline(pipeline.pipeline_id)
        
        # Fail at test stage
        updated = devops_agent.update_pipeline_stage(
            pipeline.pipeline_id,
            "test",
            "failed",
        )
        
        assert updated.status == PipelineStatus.FAILED
        assert updated.completed_at is not None


class TestInfrastructureManagement:
    """Test infrastructure resource management."""
    
    @pytest.fixture
    def devops_agent(self):
        """Create DevOpsAgent instance."""
        return DevOpsAgent()
    
    def test_register_resource(self, devops_agent):
        """Test registering infrastructure resource."""
        from agentic_ai.agents.devops import InfrastructureResource
        
        resource = InfrastructureResource(
            resource_id="web-server-2",
            resource_type=InfrastructureType.VM,
            name="Web Server 2",
            region="us-west-2",
            status="running",
            cost_per_hour=0.15,
        )
        
        devops_agent.register_resource(resource)
        
        assert "web-server-2" in devops_agent.infrastructure
        assert devops_agent.infrastructure["web-server-2"].name == "Web Server 2"
    
    def test_update_resource_status(self, devops_agent):
        """Test updating resource status."""
        resource = devops_agent.update_resource_status("web-server-1", "stopped")
        
        assert resource.status == "stopped"
    
    def test_get_resource_costs(self, devops_agent):
        """Test cost calculation."""
        costs = devops_agent.get_resource_costs(hours=24)
        
        assert 'total' in costs
        assert costs['total'] > 0  # Has default resources
    
    def test_infrastructure_summary(self, devops_agent):
        """Test infrastructure summary."""
        summary = devops_agent.get_infrastructure_summary()
        
        assert 'total_resources' in summary
        assert 'by_type' in summary
        assert 'by_status' in summary
        assert 'hourly_cost' in summary
        assert 'daily_cost' in summary
        assert 'monthly_cost' in summary


class TestMonitoringAlerting:
    """Test monitoring and alerting."""
    
    @pytest.fixture
    def devops_agent(self):
        """Create DevOpsAgent instance."""
        return DevOpsAgent()
    
    def test_record_metric(self, devops_agent):
        """Test recording metrics."""
        devops_agent.record_metric("cpu_usage", 75.5, {"host": "web-1"})
        
        assert "cpu_usage" in devops_agent.metrics
        assert len(devops_agent.metrics["cpu_usage"]) == 1
    
    def test_create_alert(self, devops_agent):
        """Test creating alerts."""
        alert = devops_agent.create_alert(
            name="High CPU",
            severity="critical",
            metric="cpu_usage",
            threshold=90.0,
            current_value=95.5,
        )
        
        assert alert.alert_id.startswith("alert-")
        assert alert.severity == "critical"
        assert not alert.acknowledged
    
    def test_acknowledge_alert(self, devops_agent):
        """Test acknowledging alerts."""
        alert = devops_agent.create_alert(
            name="High CPU",
            severity="warning",
            metric="cpu_usage",
            threshold=70.0,
            current_value=75.0,
        )
        
        success = devops_agent.acknowledge_alert(alert.alert_id, "admin")
        
        assert success is True
        assert devops_agent.alerts[alert.alert_id].acknowledged is True
    
    def test_resolve_alert(self, devops_agent):
        """Test resolving alerts."""
        alert = devops_agent.create_alert(
            name="High CPU",
            severity="warning",
            metric="cpu_usage",
            threshold=70.0,
            current_value=75.0,
        )
        
        success = devops_agent.resolve_alert(alert.alert_id)
        
        assert success is True
        assert devops_agent.alerts[alert.alert_id].resolved_at is not None
    
    def test_get_active_alerts(self, devops_agent):
        """Test getting active alerts."""
        devops_agent.create_alert("Alert 1", "critical", "cpu", 90, 95)
        devops_agent.create_alert("Alert 2", "warning", "memory", 80, 85)
        
        alert3 = devops_agent.create_alert("Alert 3", "warning", "disk", 85, 90)
        devops_agent.resolve_alert(alert3.alert_id)
        
        active = devops_agent.get_active_alerts()
        assert len(active) == 2  # Only unresolved
    
    def test_check_thresholds(self, devops_agent):
        """Test automatic threshold checking."""
        # Record high CPU
        devops_agent.record_metric("cpu_usage", 95.0)
        
        # Check thresholds (should create alert)
        alerts = devops_agent.check_thresholds()
        
        assert len(alerts) >= 1
        assert any(a.severity == "critical" for a in alerts)


class TestCostOptimization:
    """Test cost optimization features."""
    
    @pytest.fixture
    def devops_agent(self):
        """Create DevOpsAgent instance."""
        return DevOpsAgent()
    
    def test_cost_report(self, devops_agent):
        """Test cost optimization report."""
        report = devops_agent.get_cost_report(days=30)
        
        assert 'period_days' in report
        assert 'current_costs' in report
        assert 'optimization_opportunities' in report
        assert 'potential_monthly_savings' in report


class TestDevOpsCapabilities:
    """Test capabilities export for orchestration."""
    
    def test_get_capabilities(self):
        """Test capabilities export."""
        from agentic_ai.agents.devops import get_capabilities, DeploymentStatus, PipelineStatus
        
        caps = get_capabilities()
        
        assert caps['agent_type'] == 'devops'
        assert len(caps['capabilities']) >= 19
        
        # Verify key capabilities
        required = [
            'create_deployment', 'update_deployment_status', 'rollback_deployment',
            'create_pipeline', 'start_pipeline', 'update_pipeline_stage',
            'register_resource', 'get_resource_costs',
            'record_metric', 'create_alert', 'resolve_alert',
            'get_cost_report',
        ]
        
        for cap in required:
            assert cap in caps['capabilities'], f"Missing: {cap}"
        
        # Verify enums exported
        assert len(caps['deployment_statuses']) >= 5
        assert len(caps['pipeline_statuses']) >= 4
        assert len(caps['infrastructure_types']) >= 5


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
