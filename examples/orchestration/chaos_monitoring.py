"""
Chaos Engineering with Monitoring - Multi-Agent Orchestration Example
======================================================================

Demonstrates chaos experiments with real-time monitoring:
- ChaosMonkeyAgent: Runs chaos experiments (instance termination, latency injection)
- MLOpsAgent: Monitors model performance during experiments
- CloudSecurityAgent: Validates security posture remains intact
- DevOpsAgent: Auto-remediation if thresholds breached

This example shows safe chaos engineering with automated abort conditions.
"""

import sys
from datetime import datetime, timedelta
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from agentic_ai.agents.chaos_monkey import ChaosMonkeyAgent, ExperimentType, SeverityLevel, BlastRadius, TargetType
from agentic_ai.agents.ml_ops import MLOpsAgent, ModelStage, DeploymentStrategy
from agentic_ai.agents.cloud_security import CloudSecurityAgent, CloudProvider, Severity
from agentic_ai.agents.devops import DevOpsAgent


def run_chaos_with_monitoring():
    """Execute chaos engineering experiment with monitoring."""
    
    print("=" * 80)
    print("CHAOS ENGINEERING WITH MONITORING - Multi-Agent Orchestration")
    print("=" * 80)
    print()
    
    # Initialize all agents
    chaos = ChaosMonkeyAgent()
    mlops = MLOpsAgent()
    cloud_sec = CloudSecurityAgent()
    devops = DevOpsAgent()
    
    # ========================================================================
    # PHASE 1: SETUP - Register infrastructure targets
    # ========================================================================
    print("\n🎯 PHASE 1: INFRASTRUCTURE SETUP")
    print("-" * 80)
    
    # Register targets for chaos experiments
    print("\n[ChaosMonkey Agent] Registering chaos targets...")
    
    # Production web servers (non-critical, can be terminated)
    web_targets = []
    for i in range(5):
        target = chaos.register_target(
            target_type=TargetType.INSTANCE,
            name=f"web-server-{i+1}",
            cloud_provider="aws",
            region="us-east-1",
            availability_zone=f"us-east-1{'a' if i < 2 else 'b' if i < 4 else 'c'}",
            metadata={
                'instance_type': 'm5.xlarge',
                'autoscaling_group': 'web-prod-asg',
                'health_check_endpoint': '/health',
            },
            tags=['web', 'production', 'stateless'],
            critical=False,
        )
        web_targets.append(target)
    
    print(f"  ✓ Registered {len(web_targets)} web server targets")
    
    # Database (critical - should NOT be selected for random chaos)
    db_target = chaos.register_target(
        target_type=TargetType.DATABASE,
        name="postgres-primary",
        cloud_provider="aws",
        region="us-east-1",
        availability_zone="us-east-1a",
        metadata={
            'instance_type': 'r5.2xlarge',
            'engine': 'postgresql-15',
            'multi_az': True,
        },
        tags=['database', 'production', 'stateful'],
        critical=True,  # Critical - excluded from random selection
    )
    print(f"  ✓ Registered 1 database target (CRITICAL - protected)")
    
    # ML inference service
    ml_target = chaos.register_target(
        target_type=TargetType.SERVICE,
        name="ml-inference-service",
        cloud_provider="kubernetes",
        region="us-east-1",
        availability_zone="us-east-1a",
        metadata={
            'namespace': 'ml-production',
            'deployment': 'churn-predictor',
            'replicas': 3,
            'endpoint': 'https://ml-api.example.com/v1/predict',
        },
        tags=['ml', 'inference', 'production'],
        critical=False,
    )
    print(f"  ✓ Registered 1 ML service target")
    
    # ========================================================================
    # PHASE 2: MODEL REGISTRY & BASELINE
    # ========================================================================
    print("\n\n🤖 PHASE 2: ML MODEL BASELINE")
    print("-" * 80)
    
    # MLOps Agent registers production model
    print("\n[MLOps Agent] Registering production model...")
    
    # Register dataset
    dataset = mlops.register_dataset(
        name="Customer Churn Production Data",
        description="Live customer data for churn prediction",
        location="s3://ml-data/churn/production",
        record_count=1000000,
        feature_count=50,
        owner="ml-team@example.com",
        tags=['churn', 'production', 'real-time'],
    )
    print(f"  ✓ Dataset registered: {dataset.name}")
    
    # Create experiment for baseline
    baseline_exp = mlops.create_experiment(
        name="Churn Model Baseline Performance",
        description="Pre-chaos baseline metrics",
        model_type="xgboost",
        dataset_id=dataset.dataset_id,
        hyperparameters={'max_depth': 6, 'learning_rate': 0.1, 'n_estimators': 100},
        created_by="ml-ops@example.com",
    )
    mlops.start_experiment(baseline_exp.experiment_id)
    print(f"  ✓ Baseline experiment started")
    
    # Complete baseline with metrics
    baseline_metrics = {
        'accuracy': 0.92,
        'precision': 0.89,
        'recall': 0.87,
        'f1': 0.88,
        'auc': 0.94,
        'latency_p50': 45,  # ms
        'latency_p99': 120,  # ms
        'throughput': 1000,  # requests/sec
    }
    
    mlops.complete_experiment(
        baseline_exp.experiment_id,
        metrics=baseline_metrics,
        artifacts=['baseline_metrics.json', 'confusion_matrix.png'],
    )
    print(f"  ✓ Baseline metrics recorded")
    print(f"    - Accuracy: {baseline_metrics['accuracy']:.2%}")
    print(f"    - P99 Latency: {baseline_metrics['latency_p99']}ms")
    print(f"    - Throughput: {baseline_metrics['throughput']} req/s")
    
    # Register model
    model = mlops.register_model(
        name="Churn Predictor v2.3",
        description="XGBoost model for customer churn prediction",
        framework="xgboost",
        experiment_id=baseline_exp.experiment_id,
        version="2.3.0",
        owner="ml-team@example.com",
    )
    print(f"  ✓ Model registered: {model.name}")
    
    # Deploy to production
    deployment = mlops.deploy_model(
        model_id=model.model_id,
        environment="production",
        endpoint="https://ml-api.example.com/v1/predict/churn",
        strategy=DeploymentStrategy.CANARY,
        instances=3,
        config={
            'min_instances': 2,
            'max_instances': 10,
            'cpu_threshold': 70,
            'memory_threshold': 80,
        },
    )
    print(f"  ✓ Model deployed to production")
    print(f"    - Endpoint: {deployment.endpoint}")
    print(f"    - Instances: {deployment.instances}")
    
    # Create monitor for the model
    print("\n[MLOps Agent] Setting up model monitoring...")
    
    model_monitor = mlops.create_monitor(
        model_id=model.model_id,
        metrics_to_track=['accuracy', 'latency_p99', 'error_rate', 'throughput'],
        baseline_metrics={
            'accuracy': 0.92,
            'latency_p99': 120,
            'error_rate': 0.01,
            'throughput': 1000,
        },
        thresholds={
            'accuracy': 0.05,  # Alert if drops by 5%
            'latency_p99': 50,  # Alert if increases by 50ms
            'error_rate': 0.02,  # Alert if exceeds 2%
            'throughput': 200,  # Alert if drops by 200 req/s
        },
        check_frequency="minute",
        alert_channels=['slack', 'pagerduty', 'email'],
    )
    print(f"  ✓ Model monitor created: {model_monitor.monitor_id}")
    print(f"    - Check frequency: {model_monitor.check_frequency}")
    print(f"    - Alert channels: {', '.join(model_monitor.alert_channels)}")
    
    # ========================================================================
    # PHASE 3: CLOUD SECURITY BASELINE
    # ========================================================================
    print("\n\n🔒 PHASE 3: CLOUD SECURITY BASELINE")
    print("-" * 80)
    
    # CloudSecurity Agent establishes security baseline
    print("\n[CloudSecurity Agent] Establishing security baseline...")
    
    # Add AWS account
    aws_account = cloud_sec.add_account(
        account_id="123456789012",
        provider=CloudProvider.AWS,
        name="Production AWS",
        environment="production",
        owner="cloud-security@example.com",
    )
    print(f"  ✓ AWS account registered: {aws_account.account_id}")
    
    # Register resources
    resources = []
    for i, target in enumerate(web_targets):
        resource = cloud_sec.add_resource(
            resource_type=cloud_sec.ResourceType.EC2,
            account_id=aws_account.account_id,
            region=target.region,
            name=target.name,
            configuration={
                'instance_type': 'm5.xlarge',
                'encrypted': True,
                'public_ip': False,
                'security_groups': ['sg-web-prod'],
            },
            tags=target.tags,
        )
        resources.append(resource)
    
    print(f"  ✓ {len(resources)} EC2 resources registered")
    
    # Create security policies
    print("\n[CloudSecurity Agent] Creating security policies...")
    
    security_policies = [
        cloud_sec.create_policy(
            name="EC2 Public IP Prohibited",
            description="Production EC2 instances must not have public IPs",
            provider=CloudProvider.AWS,
            resource_type=cloud_sec.ResourceType.EC2,
            rule_expression="public_ip == false",
            severity=Severity.HIGH,
            compliance_frameworks=['cis_aws'],
        ),
        cloud_sec.create_policy(
            name="EBS Encryption Required",
            description="All EBS volumes must be encrypted",
            provider=CloudProvider.AWS,
            resource_type=cloud_sec.ResourceType.EC2,
            rule_expression="encrypted == true",
            severity=Severity.MEDIUM,
            compliance_frameworks=['cis_aws', 'pci_dss'],
        ),
    ]
    print(f"  ✓ {len(security_policies)} security policies created")
    
    # Get baseline compliance score
    baseline_compliance = cloud_sec.get_compliance_score('cis_aws')
    print(f"\n  ✓ Baseline CIS AWS Compliance: {baseline_compliance.get('score', 0):.1f}%")
    
    # ========================================================================
    # PHASE 4: CHAOS EXPERIMENT EXECUTION
    # ========================================================================
    print("\n\n💥 PHASE 4: CHAOS EXPERIMENT EXECUTION")
    print("-" * 80)
    
    # Create chaos experiment
    print("\n[ChaosMonkey Agent] Creating chaos experiment...")
    
    experiment = chaos.create_experiment(
        name="Instance Termination - Web Servers",
        description="Test auto-healing by terminating random web server instances",
        experiment_type=ExperimentType.INSTANCE_TERMINATION,
        severity=SeverityLevel.MEDIUM,
        blast_radius=BlastRadius.LIMITED,
        duration_minutes=15,
        hypothesis="Auto-scaling will replace terminated instances within 3 minutes with no user impact",
        expected_outcome="No increase in error rate, latency remains under 200ms P99",
        abort_conditions=[
            chaos.AbortCondition.ERROR_RATE_THRESHOLD,
            chaos.AbortCondition.LATENCY_THRESHOLD,
            chaos.AbortCondition.AVAILABILITY_THRESHOLD,
        ],
        abort_thresholds={
            'error_rate': 2.0,  # Abort if error rate > 2%
            'latency_p99': 500,  # Abort if P99 > 500ms
            'availability': 99.0,  # Abort if availability < 99%
        },
        created_by="chaos-team@example.com",
    )
    print(f"  ✓ Experiment created: {experiment.experiment_id}")
    print(f"    - Type: {experiment.experiment_type.value}")
    print(f"    - Severity: {experiment.severity.value}")
    print(f"    - Blast radius: {experiment.blast_radius.value}")
    print(f"    - Duration: {experiment.duration_minutes} minutes")
    
    # Select random targets (excludes critical)
    selected_targets = chaos.select_random_targets(
        count=2,
        target_type=TargetType.INSTANCE,
        exclude_critical=True,
    )
    print(f"\n  ✓ Selected {len(selected_targets)} targets for termination:")
    for t in selected_targets:
        print(f"    - {t.name} ({t.availability_zone})")
    
    # Assign targets and schedule
    chaos.assign_targets(experiment.experiment_id, [t.target_id for t in selected_targets])
    
    # Add metric thresholds for monitoring
    print("\n[ChaosMonkey Agent] Configuring abort thresholds...")
    
    chaos.add_metric_threshold(
        experiment.experiment_id,
        metric_name="error_rate",
        operator="gt",
        threshold_value=2.0,
    )
    chaos.add_metric_threshold(
        experiment.experiment_id,
        metric_name="latency_p99",
        operator="gt",
        threshold_value=500,
    )
    print(f"  ✓ Abort thresholds configured")
    
    # Start experiment
    print("\n[ChaosMonkey Agent] 🚀 STARTING CHAOS EXPERIMENT...")
    
    if not chaos.start_experiment(experiment.experiment_id):
        print("  ✗ Experiment blocked by safety constraints or blackout window")
        return
    
    print(f"  ✓ Experiment started at {experiment.started_at}")
    
    # Execute termination on each target
    print("\n[ChaosMonkey Agent] Executing instance terminations...")
    
    runs = [r for r in chaos.runs.values() if r.experiment_id == experiment.experiment_id]
    for run in runs:
        chaos.execute_termination(run.run_id)
        target = next((t for t in selected_targets if t.target_id == run.target_id), None)
        if target:
            print(f"  💥 TERMINATED: {target.name} ({target.region})")
            print(f"     Run ID: {run.run_id}")
            print(f"     Duration: {run.duration_seconds:.1f}s")
    
    # ========================================================================
    # PHASE 5: REAL-TIME MONITORING
    # ========================================================================
    print("\n\n📊 PHASE 5: REAL-TIME MONITORING")
    print("-" * 80)
    
    # Simulate monitoring during chaos
    print("\n[MLOps Agent] Monitoring model performance during chaos...")
    
    # Simulate metrics during experiment (t+1 minute)
    metrics_t1 = {
        'accuracy': 0.91,  # Slight drop
        'latency_p99': 145,  # Increased from 120ms
        'error_rate': 0.015,  # 1.5% (under 2% threshold)
        'throughput': 950,  # Slight drop
    }
    
    # Check for alerts
    alerts = mlops.check_model_metrics(model.model_id, metrics_t1)
    print(f"\n  T+1min metrics:")
    print(f"    - Accuracy: {metrics_t1['accuracy']:.2%} (baseline: 92%)")
    print(f"    - P99 Latency: {metrics_t1['latency_p99']}ms (baseline: 120ms)")
    print(f"    - Error Rate: {metrics_t1['error_rate']:.2%} (threshold: 2%)")
    print(f"    - Throughput: {metrics_t1['throughput']} req/s (baseline: 1000)")
    print(f"    - Alerts generated: {len(alerts)}")
    
    # Check chaos thresholds
    print("\n[ChaosMonkey Agent] Checking abort conditions...")
    
    breached = chaos.check_metric_thresholds(
        experiment.experiment_id,
        metrics={
            'error_rate': metrics_t1['error_rate'] * 100,  # Convert to percentage
            'latency_p99': metrics_t1['latency_p99'],
        },
    )
    
    if breached:
        print(f"  ⚠️  THRESHOLDS BREACHED: {', '.join(breached)}")
        print("  ⚠️  Experiment would be aborted!")
    else:
        print(f"  ✓ All thresholds within limits")
        print(f"  ✓ Experiment continues...")
    
    # Simulate T+3min (auto-scaling kicked in)
    print("\n  [Auto-scaling] New instances launched to replace terminated...")
    
    metrics_t3 = {
        'accuracy': 0.92,  # Back to baseline
        'latency_p99': 125,  # Nearly back to baseline
        'error_rate': 0.01,  # Back to normal
        'throughput': 1000,  # Fully recovered
    }
    
    print(f"\n  T+3min metrics (recovery):")
    print(f"    - Accuracy: {metrics_t3['accuracy']:.2%} ✓")
    print(f"    - P99 Latency: {metrics_t3['latency_p99']}ms ✓")
    print(f"    - Error Rate: {metrics_t3['error_rate']:.2%} ✓")
    print(f"    - Throughput: {metrics_t3['throughput']} req/s ✓")
    
    # ========================================================================
    # PHASE 6: SECURITY VALIDATION
    # ========================================================================
    print("\n\n🛡️ PHASE 6: SECURITY VALIDATION")
    print("-" * 80)
    
    # CloudSecurity Agent validates security posture
    print("\n[CloudSecurity Agent] Validating security posture post-chaos...")
    
    # Check for new security findings
    findings = cloud_sec.get_findings(status='open')
    print(f"  ✓ Open security findings: {len(findings)}")
    
    # Get updated compliance score
    post_chaos_compliance = cloud_sec.get_compliance_score('cis_aws')
    print(f"  ✓ Post-chaos CIS Compliance: {post_chaos_compliance.get('score', 0):.1f}%")
    
    if post_chaos_compliance.get('score', 0) >= baseline_compliance.get('score', 0):
        print(f"  ✓ Security posture maintained during chaos")
    else:
        print(f"  ⚠️  Security posture degraded - investigation required")
    
    # ========================================================================
    # PHASE 7: COMPLETION & ANALYSIS
    # ========================================================================
    print("\n\n✅ PHASE 7: EXPERIMENT COMPLETION & ANALYSIS")
    print("-" * 80)
    
    # Complete the experiment
    print("\n[ChaosMonkey Agent] Completing experiment...")
    
    chaos.complete_experiment(
        experiment.experiment_id,
        actual_outcome="System recovered within 3 minutes. Auto-scaling replaced terminated instances. No user-visible impact. Error rate remained below 2% threshold throughout.",
        lessons_learned=[
            "Auto-scaling group responded within 45 seconds",
            "Load balancer health checks detected failures in 15 seconds",
            "P99 latency spiked to 145ms but recovered within 2 minutes",
            "No security posture degradation observed",
            "Model accuracy remained stable throughout experiment",
            "Recommendation: Add more AZs for better resilience",
        ],
    )
    print(f"  ✓ Experiment completed at {experiment.completed_at}")
    print(f"  ✓ Duration: {(experiment.completed_at - experiment.started_at).total_seconds():.0f} seconds")
    
    # Get experiment report
    report = chaos.get_experiment_report(experiment.experiment_id)
    
    # Calculate resiliency score
    print("\n[MLOps Agent] Calculating resiliency score...")
    
    resiliency_score = mlops.calculate_resiliency_score("churn-predictor")
    print(f"  ✓ Resiliency Score: {resiliency_score.overall_score:.1f}/100")
    print(f"    - Availability: {resiliency_score.availability_score:.1f}")
    print(f"    - Recovery: {resiliency_score.recovery_score:.1f}")
    print(f"    - Degradation: {resiliency_score.degradation_score:.1f}")
    print(f"    - Monitoring: {resiliency_score.monitoring_score:.1f}")
    
    # DevOps Agent creates follow-up tasks
    print("\n[DevOps Agent] Creating follow-up tasks...")
    
    tasks = [
        devops.create_task(
            title="Add third AZ for web servers",
            description="Experiment showed benefit of multi-AZ. Add us-east-1c to autoscaling group.",
            priority="medium",
            assignee="platform-team@example.com",
            due_date=datetime.utcnow() + timedelta(days=14),
        ),
        devops.create_task(
            title="Reduce auto-scaling cooldown",
            description="Current 5min cooldown too conservative. Reduce to 2min for faster recovery.",
            priority="low",
            assignee="platform-team@example.com",
            due_date=datetime.utcnow() + timedelta(days=30),
        ),
    ]
    print(f"  ✓ {len(tasks)} follow-up tasks created")
    
    # ========================================================================
    # SUMMARY
    # ========================================================================
    print("\n\n" + "=" * 80)
    print("CHAOS EXPERIMENT SUMMARY")
    print("=" * 80)
    
    print(f"""
EXPERIMENT: {experiment.name}
EXPERIMENT ID: {experiment.experiment_id}
STATUS: {experiment.status.value.upper()}
DURATION: {(experiment.completed_at - experiment.started_at).total_seconds():.0f} seconds

HYPOTHESIS: {experiment.hypothesis}
RESULT: ✅ VERIFIED

TARGETS TERMINATED: {len(selected_targets)}
  {chr(10).join(f"  - {t.name}" for t in selected_targets)}

MONITORING:
  ✓ Baseline accuracy: {baseline_metrics['accuracy']:.2%}
  ✓ Worst accuracy during chaos: 91%
  ✓ Final accuracy: {metrics_t3['accuracy']:.2%}
  
  ✓ Baseline P99 latency: {baseline_metrics['latency_p99']}ms
  ✓ Peak P99 latency: 145ms
  ✓ Final P99 latency: {metrics_t3['latency_p99']}ms

SECURITY:
  ✓ Baseline compliance: {baseline_compliance.get('score', 0):.1f}%
  ✓ Post-chaos compliance: {post_chaos_compliance.get('score', 0):.1f}%
  ✓ Security posture: MAINTAINED

RESILIENCY SCORE: {resiliency_score.overall_score:.1f}/100

LESSONS LEARNED:
{chr(10).join(f"  • {lesson}" for lesson in experiment.lessons_learned)}
""")
    
    # Get final state from all agents
    print("\nAGENT STATES:")
    print(f"  ChaosMonkey Agent: {chaos.get_state()}")
    print(f"  MLOps Agent: {mlops.get_state()}")
    print(f"  CloudSecurity Agent: {cloud_sec.get_state()}")
    print(f"  DevOps Agent: {devops.get_state()}")
    
    print("\n" + "=" * 80)
    print("✅ CHAOS ENGINEERING WORKFLOW COMPLETE")
    print("=" * 80)
    
    return {
        'experiment': experiment,
        'resiliency_score': resiliency_score,
        'agents': {
            'chaos': chaos.get_state(),
            'mlops': mlops.get_state(),
            'cloud_sec': cloud_sec.get_state(),
            'devops': devops.get_state(),
        },
    }


if __name__ == "__main__":
    result = run_chaos_with_monitoring()
    print("\n📊 Workflow execution successful!")
