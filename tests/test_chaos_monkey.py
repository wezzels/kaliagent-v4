"""
ChaosMonkeyAgent Tests
======================

Unit tests for ChaosMonkeyAgent - Chaos engineering & resiliency testing.
"""

import pytest
from datetime import datetime, timedelta

from agentic_ai.agents.chaos_monkey import (
    ChaosMonkeyAgent,
    ExperimentType,
    ExperimentStatus,
    TargetType,
    SeverityLevel,
    BlastRadius,
    AbortCondition,
)


class TestChaosMonkeyAgent:
    """Test ChaosMonkeyAgent."""
    
    @pytest.fixture
    def chaos(self):
        """Create ChaosMonkeyAgent instance."""
        return ChaosMonkeyAgent()
    
    def test_register_target(self, chaos):
        """Test registering target."""
        target = chaos.register_target(
            target_type=TargetType.INSTANCE,
            name="web-server-1",
            cloud_provider="aws",
            region="us-east-1",
            availability_zone="us-east-1a",
            tags=['web', 'production'],
            critical=False,
        )
        
        assert target.target_id.startswith("target-")
        assert target.target_type == TargetType.INSTANCE
        assert target.cloud_provider == "aws"
        assert target.critical is False
    
    def test_register_critical_target(self, chaos):
        """Test registering critical target."""
        target = chaos.register_target(
            target_type=TargetType.DATABASE,
            name="db-primary",
            cloud_provider="aws",
            region="us-east-1",
            availability_zone="us-east-1a",
            critical=True,
        )
        
        assert target.critical is True
    
    def test_get_targets_by_type(self, chaos):
        """Test filtering targets by type."""
        chaos.register_target(TargetType.INSTANCE, "web-1", "aws", "us-east-1", "us-east-1a")
        chaos.register_target(TargetType.INSTANCE, "web-2", "aws", "us-east-1", "us-east-1b")
        chaos.register_target(TargetType.DATABASE, "db-1", "aws", "us-east-1", "us-east-1a")
        
        instances = chaos.get_targets(target_type=TargetType.INSTANCE)
        databases = chaos.get_targets(target_type=TargetType.DATABASE)
        
        assert len(instances) == 2
        assert len(databases) == 1
    
    def test_get_targets_by_cloud(self, chaos):
        """Test filtering targets by cloud provider."""
        chaos.register_target(TargetType.INSTANCE, "aws-1", "aws", "us-east-1", "a")
        chaos.register_target(TargetType.INSTANCE, "gcp-1", "gcp", "us-central1", "a")
        chaos.register_target(TargetType.INSTANCE, "azure-1", "azure", "eastus", "1")
        
        aws = chaos.get_targets(cloud_provider="aws")
        gcp = chaos.get_targets(cloud_provider="gcp")
        
        assert len(aws) == 1
        assert len(gcp) == 1
    
    def test_select_random_targets(self, chaos):
        """Test random target selection."""
        for i in range(5):
            chaos.register_target(
                TargetType.INSTANCE, f"web-{i}", "aws", "us-east-1", "a",
                critical=False,
            )
        
        chaos.register_target(
            TargetType.INSTANCE, "db-primary", "aws", "us-east-1", "a",
            critical=True,
        )
        
        # Select 2 non-critical targets
        selected = chaos.select_random_targets(count=2, target_type=TargetType.INSTANCE, exclude_critical=True)
        
        assert len(selected) == 2
        assert all(not t.critical for t in selected)
        assert all(t.target_type == TargetType.INSTANCE for t in selected)
    
    def test_select_random_targets_excludes_critical(self, chaos):
        """Test that critical targets are excluded."""
        chaos.register_target(TargetType.INSTANCE, "web-1", "aws", "us-east-1", "a", critical=False)
        chaos.register_target(TargetType.INSTANCE, "web-2", "aws", "us-east-1", "a", critical=False)
        chaos.register_target(TargetType.INSTANCE, "db-primary", "aws", "us-east-1", "a", critical=True)
        
        selected = chaos.select_random_targets(count=3, exclude_critical=True)
        
        assert len(selected) == 2  # Only 2 non-critical
        assert all(not t.critical for t in selected)
    
    def test_create_experiment(self, chaos):
        """Test creating chaos experiment."""
        experiment = chaos.create_experiment(
            name="Instance Termination Test",
            description="Test auto-healing",
            experiment_type=ExperimentType.INSTANCE_TERMINATION,
            severity=SeverityLevel.MEDIUM,
            blast_radius=BlastRadius.LIMITED,
            duration_minutes=30,
            hypothesis="System will auto-heal within 5 minutes",
            expected_outcome="No user impact",
            abort_conditions=[AbortCondition.ERROR_RATE_THRESHOLD],
            abort_thresholds={'error_rate': 2.0, 'availability': 99.0},
            created_by="chaos-team@example.com",
        )
        
        assert experiment.experiment_id.startswith("exp-")
        assert experiment.experiment_type == ExperimentType.INSTANCE_TERMINATION
        assert experiment.severity == SeverityLevel.MEDIUM
        assert experiment.blast_radius == BlastRadius.LIMITED
        assert experiment.status == ExperimentStatus.SCHEDULED
        assert experiment.duration_minutes == 30
        assert 'error_rate' in experiment.abort_thresholds
    
    def test_schedule_experiment(self, chaos):
        """Test scheduling experiment."""
        experiment = chaos.create_experiment(
            "Test", "Desc", ExperimentType.INSTANCE_TERMINATION,
            SeverityLevel.LOW, BlastRadius.SINGLE, 15,
        )
        
        start_time = datetime.utcnow() + timedelta(hours=1)
        result = chaos.schedule_experiment(experiment.experiment_id, start_time)
        
        assert result is True
        assert experiment.scheduled_start is not None
        assert experiment.scheduled_end is not None
    
    def test_assign_targets(self, chaos):
        """Test assigning targets to experiment."""
        experiment = chaos.create_experiment(
            "Test", "Desc", ExperimentType.INSTANCE_TERMINATION,
            SeverityLevel.LOW, BlastRadius.SINGLE, 15,
        )
        
        t1 = chaos.register_target(TargetType.INSTANCE, "web-1", "aws", "us-east-1", "a")
        t2 = chaos.register_target(TargetType.INSTANCE, "web-2", "aws", "us-east-1", "b")
        
        result = chaos.assign_targets(experiment.experiment_id, [t1.target_id, t2.target_id])
        
        assert result is True
        assert experiment.target_count == 2
        assert len(experiment.targets) == 2
    
    def test_start_experiment(self, chaos):
        """Test starting experiment."""
        experiment = chaos.create_experiment(
            "Test", "Desc", ExperimentType.INSTANCE_TERMINATION,
            SeverityLevel.LOW, BlastRadius.SINGLE, 15,
        )
        
        target = chaos.register_target(TargetType.INSTANCE, "web-1", "aws", "us-east-1", "a")
        chaos.assign_targets(experiment.experiment_id, [target.target_id])
        
        result = chaos.start_experiment(experiment.experiment_id)
        
        assert result is True
        assert experiment.status == ExperimentStatus.RUNNING
        assert experiment.started_at is not None
        assert len(chaos.runs) == 1
    
    def test_start_experiment_creates_runs(self, chaos):
        """Test that starting experiment creates runs."""
        experiment = chaos.create_experiment(
            "Test", "Desc", ExperimentType.INSTANCE_TERMINATION,
            SeverityLevel.LOW, BlastRadius.SINGLE, 15,
        )
        
        t1 = chaos.register_target(TargetType.INSTANCE, "web-1", "aws", "us-east-1", "a")
        t2 = chaos.register_target(TargetType.INSTANCE, "web-2", "aws", "us-east-1", "b")
        chaos.assign_targets(experiment.experiment_id, [t1.target_id, t2.target_id])
        
        chaos.start_experiment(experiment.experiment_id)
        
        runs = [r for r in chaos.runs.values() if r.experiment_id == experiment.experiment_id]
        assert len(runs) == 2
    
    def test_execute_termination(self, chaos):
        """Test executing instance termination."""
        experiment = chaos.create_experiment(
            "Test", "Desc", ExperimentType.INSTANCE_TERMINATION,
            SeverityLevel.LOW, BlastRadius.SINGLE, 15,
        )
        
        target = chaos.register_target(TargetType.INSTANCE, "web-1", "aws", "us-east-1", "a")
        chaos.assign_targets(experiment.experiment_id, [target.target_id])
        chaos.start_experiment(experiment.experiment_id)
        
        run = list(chaos.runs.values())[0]
        
        result = chaos.execute_termination(run.run_id)
        
        assert result is True
        assert run.status == "completed"
        assert run.started_at is not None
        assert run.completed_at is not None
        assert run.duration_seconds >= 0
        assert 'action' in run.result
        assert run.result['action'] == 'terminate'
    
    def test_execute_latency_injection(self, chaos):
        """Test executing latency injection."""
        experiment = chaos.create_experiment(
            "Test", "Desc", ExperimentType.LATENCY_INJECTION,
            SeverityLevel.MEDIUM, BlastRadius.LIMITED, 15,
        )
        
        target = chaos.register_target(TargetType.SERVICE, "api-service", "kubernetes", "us-east-1", "a")
        chaos.assign_targets(experiment.experiment_id, [target.target_id])
        chaos.start_experiment(experiment.experiment_id)
        
        run = list(chaos.runs.values())[0]
        
        result = chaos.execute_latency_injection(run.run_id, latency_ms=500, jitter_percent=10.0)
        
        assert result is True
        assert run.status == "completed"
        assert 'action' in run.result
        assert run.result['action'] == 'latency_injection'
        assert run.result['latency_ms'] == 500
        assert 'actual_latency_ms' in run.result
    
    def test_complete_experiment(self, chaos):
        """Test completing experiment."""
        experiment = chaos.create_experiment(
            "Test", "Desc", ExperimentType.INSTANCE_TERMINATION,
            SeverityLevel.LOW, BlastRadius.SINGLE, 15,
        )
        
        target = chaos.register_target(TargetType.INSTANCE, "web-1", "aws", "us-east-1", "a")
        chaos.assign_targets(experiment.experiment_id, [target.target_id])
        chaos.start_experiment(experiment.experiment_id)
        
        result = chaos.complete_experiment(
            experiment.experiment_id,
            actual_outcome="System recovered in 3 minutes",
            lessons_learned=["Auto-scaling worked well", "Need more AZs"],
        )
        
        assert result is True
        assert experiment.status == ExperimentStatus.COMPLETED
        assert experiment.completed_at is not None
        assert experiment.actual_outcome == "System recovered in 3 minutes"
        assert len(experiment.lessons_learned) == 2
    
    def test_abort_experiment(self, chaos):
        """Test aborting experiment."""
        experiment = chaos.create_experiment(
            "Test", "Desc", ExperimentType.INSTANCE_TERMINATION,
            SeverityLevel.LOW, BlastRadius.SINGLE, 15,
        )
        
        target = chaos.register_target(TargetType.INSTANCE, "web-1", "aws", "us-east-1", "a")
        chaos.assign_targets(experiment.experiment_id, [target.target_id])
        chaos.start_experiment(experiment.experiment_id)
        
        result = chaos.abort_experiment(experiment.experiment_id, "Error rate exceeded threshold")
        
        assert result is True
        assert experiment.status == ExperimentStatus.ABORTED
        assert experiment.completed_at is not None
        assert any("Aborted" in lesson for lesson in experiment.lessons_learned)
        
        # Runs should be aborted
        runs = [r for r in chaos.runs.values() if r.experiment_id == experiment.experiment_id]
        assert all(r.status == "aborted" for r in runs)
    
    def test_get_experiments_by_type(self, chaos):
        """Test filtering experiments by type."""
        chaos.create_experiment("E1", "D", ExperimentType.INSTANCE_TERMINATION, SeverityLevel.LOW, BlastRadius.SINGLE, 15)
        chaos.create_experiment("E2", "D", ExperimentType.LATENCY_INJECTION, SeverityLevel.MEDIUM, BlastRadius.LIMITED, 30)
        chaos.create_experiment("E3", "D", ExperimentType.NETWORK_PARTITION, SeverityLevel.HIGH, BlastRadius.MODERATE, 45)
        
        termination = chaos.get_experiments(experiment_type=ExperimentType.INSTANCE_TERMINATION)
        latency = chaos.get_experiments(experiment_type=ExperimentType.LATENCY_INJECTION)
        
        assert len(termination) == 1
        assert len(latency) == 1
    
    def test_get_experiments_by_status(self, chaos):
        """Test filtering experiments by status."""
        e1 = chaos.create_experiment("E1", "D", ExperimentType.INSTANCE_TERMINATION, SeverityLevel.LOW, BlastRadius.SINGLE, 15)
        e2 = chaos.create_experiment("E2", "D", ExperimentType.INSTANCE_TERMINATION, SeverityLevel.LOW, BlastRadius.SINGLE, 15)
        e3 = chaos.create_experiment("E3", "D", ExperimentType.INSTANCE_TERMINATION, SeverityLevel.LOW, BlastRadius.SINGLE, 15)
        
        t1 = chaos.register_target(TargetType.INSTANCE, "web-1", "aws", "us-east-1", "a")
        chaos.assign_targets(e2.experiment_id, [t1.target_id])
        chaos.start_experiment(e2.experiment_id)
        
        chaos.assign_targets(e3.experiment_id, [t1.target_id])
        chaos.start_experiment(e3.experiment_id)
        chaos.complete_experiment(e3.experiment_id, "outcome")
        
        scheduled = chaos.get_experiments(status=ExperimentStatus.SCHEDULED)
        running = chaos.get_experiments(status=ExperimentStatus.RUNNING)
        completed = chaos.get_experiments(status=ExperimentStatus.COMPLETED)
        
        assert len(scheduled) == 1
        assert len(running) == 1
        assert len(completed) == 1
    
    def test_add_blackout_window(self, chaos):
        """Test adding blackout window."""
        window = chaos.add_blackout_window(
            name="Business Hours",
            start_time="09:00",
            end_time="17:00",
            days=['monday', 'tuesday', 'wednesday', 'thursday', 'friday'],
            timezone="UTC",
            reason="Protect production during peak hours",
        )
        
        assert window.window_id.startswith("blackout-")
        assert window.start_time == "09:00"
        assert window.end_time == "17:00"
        assert len(window.days) == 5
    
    def test_add_safety_constraint(self, chaos):
        """Test adding safety constraint."""
        constraint = chaos.add_safety_constraint(
            name="Max 10% Capacity",
            description="Never affect more than 10% of capacity",
            constraint_type="max_percentage",
            parameters={'max_percentage': 10},
        )
        
        assert constraint.constraint_id.startswith("constraint-")
        assert constraint.constraint_type == "max_percentage"
        assert constraint.parameters['max_percentage'] == 10
    
    def test_add_metric_threshold(self, chaos):
        """Test adding metric threshold."""
        experiment = chaos.create_experiment(
            "Test", "Desc", ExperimentType.INSTANCE_TERMINATION,
            SeverityLevel.LOW, BlastRadius.SINGLE, 15,
        )
        
        threshold = chaos.add_metric_threshold(
            experiment.experiment_id,
            metric_name="error_rate",
            operator="gt",
            threshold_value=2.0,
        )
        
        assert threshold.threshold_id.startswith("threshold-")
        assert threshold.metric_name == "error_rate"
        assert threshold.operator == "gt"
        assert threshold.threshold_value == 2.0
    
    def test_check_metric_thresholds_breach(self, chaos):
        """Test metric threshold breach detection."""
        experiment = chaos.create_experiment(
            "Test", "Desc", ExperimentType.INSTANCE_TERMINATION,
            SeverityLevel.LOW, BlastRadius.SINGLE, 15,
        )
        
        chaos.add_metric_threshold(experiment.experiment_id, "error_rate", "gt", 2.0)
        chaos.add_metric_threshold(experiment.experiment_id, "latency_p99", "gt", 5000)
        
        # Breach error_rate threshold
        breached = chaos.check_metric_thresholds(experiment.experiment_id, {'error_rate': 5.0, 'latency_p99': 1000})
        
        assert 'error_rate' in breached
        assert 'latency_p99' not in breached
    
    def test_check_metric_thresholds_no_breach(self, chaos):
        """Test metric thresholds with no breach."""
        experiment = chaos.create_experiment(
            "Test", "Desc", ExperimentType.INSTANCE_TERMINATION,
            SeverityLevel.LOW, BlastRadius.SINGLE, 15,
        )
        
        chaos.add_metric_threshold(experiment.experiment_id, "error_rate", "gt", 2.0)
        
        breached = chaos.check_metric_thresholds(experiment.experiment_id, {'error_rate': 1.0})
        
        assert len(breached) == 0
    
    def test_calculate_resiliency_score(self, chaos):
        """Test resiliency score calculation."""
        # Create and complete experiments
        for i in range(5):
            e = chaos.create_experiment(
                f"Test {i}", "Desc", ExperimentType.INSTANCE_TERMINATION,
                SeverityLevel.LOW, BlastRadius.SINGLE, 15,
            )
            chaos.complete_experiment(e.experiment_id, f"Outcome {i}")
        
        score = chaos.calculate_resiliency_score("web-service")
        
        assert score.score_id.startswith("score-")
        assert score.service_name == "web-service"
        assert score.experiments_run == 5
        assert score.experiments_passed == 5
        assert 0 <= score.overall_score <= 100
        assert 0 <= score.availability_score <= 100
    
    def test_get_chaos_dashboard(self, chaos):
        """Test chaos dashboard generation."""
        # Create experiments
        chaos.create_experiment("E1", "D", ExperimentType.INSTANCE_TERMINATION, SeverityLevel.LOW, BlastRadius.SINGLE, 15)
        chaos.create_experiment("E2", "D", ExperimentType.LATENCY_INJECTION, SeverityLevel.MEDIUM, BlastRadius.LIMITED, 30)
        
        # Add targets
        chaos.register_target(TargetType.INSTANCE, "web-1", "aws", "us-east-1", "a")
        chaos.register_target(TargetType.INSTANCE, "web-2", "aws", "us-east-1", "a", critical=True)
        
        dashboard = chaos.get_chaos_dashboard()
        
        assert 'experiments' in dashboard
        assert 'runs' in dashboard
        assert 'targets' in dashboard
        assert 'safety' in dashboard
        assert 'resiliency' in dashboard
        assert dashboard['experiments']['total'] == 2
        assert dashboard['targets']['total'] == 2
        assert dashboard['targets']['critical'] == 1
    
    def test_get_experiment_report(self, chaos):
        """Test experiment report generation."""
        experiment = chaos.create_experiment(
            "Test Experiment", "Test Description",
            ExperimentType.INSTANCE_TERMINATION,
            SeverityLevel.MEDIUM, BlastRadius.LIMITED, 30,
            hypothesis="System will recover",
            expected_outcome="No user impact",
        )
        
        target = chaos.register_target(TargetType.INSTANCE, "web-1", "aws", "us-east-1", "a")
        chaos.assign_targets(experiment.experiment_id, [target.target_id])
        chaos.start_experiment(experiment.experiment_id)
        chaos.complete_experiment(experiment.experiment_id, "Actual outcome", ["Lesson 1"])
        
        report = chaos.get_experiment_report(experiment.experiment_id)
        
        assert 'experiment' in report
        assert 'targets' in report
        assert 'runs' in report
        assert 'timing' in report
        assert report['experiment']['name'] == "Test Experiment"
        assert report['experiment']['actual_outcome'] == "Actual outcome"
    
    def test_get_state(self, chaos):
        """Test agent state summary."""
        chaos.register_target(TargetType.INSTANCE, "web-1", "aws", "us-east-1", "a")
        chaos.register_target(TargetType.INSTANCE, "web-2", "aws", "us-east-1", "a", critical=True)
        
        experiment = chaos.create_experiment(
            "Test", "Desc", ExperimentType.INSTANCE_TERMINATION,
            SeverityLevel.LOW, BlastRadius.SINGLE, 15,
        )
        chaos.assign_targets(experiment.experiment_id, ["target-1"])
        chaos.start_experiment(experiment.experiment_id)
        
        state = chaos.get_state()
        
        assert state['targets_count'] == 2
        assert state['critical_targets'] == 1
        assert state['experiments_count'] == 1
        assert state['running_experiments'] == 1
        assert 'agent_id' in state


class TestChaosMonkeyCapabilities:
    """Test ChaosMonkeyAgent capabilities export."""
    
    def test_capabilities(self):
        """Test capabilities export."""
        from agentic_ai.agents.chaos_monkey import get_capabilities
        caps = get_capabilities()
        
        assert caps['agent_type'] == 'chaos_monkey'
        assert len(caps['capabilities']) >= 19
        assert 'register_target' in caps['capabilities']
        assert 'create_experiment' in caps['capabilities']
        assert 'start_experiment' in caps['capabilities']
        assert 'execute_termination' in caps['capabilities']
        assert 'execute_latency_injection' in caps['capabilities']
        assert 'calculate_resiliency_score' in caps['capabilities']
    
    def test_experiment_types(self):
        """Test experiment types in capabilities."""
        from agentic_ai.agents.chaos_monkey import get_capabilities
        caps = get_capabilities()
        
        assert 'instance_termination' in caps['experiment_types']
        assert 'latency_injection' in caps['experiment_types']
        assert 'network_partition' in caps['experiment_types']
        assert 'cpu_stress' in caps['experiment_types']
        assert 'memory_stress' in caps['experiment_types']
    
    def test_target_types(self):
        """Test target types in capabilities."""
        from agentic_ai.agents.chaos_monkey import get_capabilities
        caps = get_capabilities()
        
        assert 'instance' in caps['target_types']
        assert 'service' in caps['target_types']
        assert 'container' in caps['target_types']
        assert 'pod' in caps['target_types']
        assert 'database' in caps['target_types']
    
    def test_severity_levels(self):
        """Test severity levels in capabilities."""
        from agentic_ai.agents.chaos_monkey import get_capabilities
        caps = get_capabilities()
        
        assert 'low' in caps['severity_levels']
        assert 'medium' in caps['severity_levels']
        assert 'high' in caps['severity_levels']
        assert 'critical' in caps['severity_levels']
    
    def test_blast_radius(self):
        """Test blast radius levels in capabilities."""
        from agentic_ai.agents.chaos_monkey import get_capabilities
        caps = get_capabilities()
        
        assert 'single' in caps['blast_radius_levels']
        assert 'limited' in caps['blast_radius_levels']
        assert 'moderate' in caps['blast_radius_levels']
        assert 'unconstrained' in caps['blast_radius_levels']
    
    def test_supported_clouds(self):
        """Test supported cloud providers."""
        from agentic_ai.agents.chaos_monkey import get_capabilities
        caps = get_capabilities()
        
        assert 'aws' in caps['supported_clouds']
        assert 'gcp' in caps['supported_clouds']
        assert 'azure' in caps['supported_clouds']
        assert 'kubernetes' in caps['supported_clouds']


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
