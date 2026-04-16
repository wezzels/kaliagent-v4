#!/usr/bin/env python3
"""
Multi-Agent Orchestration Examples
===================================

Demonstrates how multiple agents work together through the Lead Agent
to accomplish complex tasks that span multiple domains.
"""

from agentic_ai.agents.devops import DevOpsAgent, DeploymentStatus, PipelineStatus
from agentic_ai.agents.data_analyst import DataAnalystAgent
from agentic_ai.agents.support import SupportAgent, TicketPriority, TicketCategory
from agentic_ai.agents.security import SecurityAgent, SeverityLevel, ThreatType


def example_incident_response_workflow():
    """Example: Multi-agent incident response workflow."""
    print("=" * 70)
    print("Example 1: Multi-Agent Incident Response")
    print("=" * 70)
    print()
    
    # Initialize agents
    security = SecurityAgent()
    devops = DevOpsAgent()
    support = SupportAgent()
    
    print("🚨 INCIDENT DETECTED: SQL Injection Attack\n")
    
    # Security Agent detects attack
    print("1. Security Agent detects attack...")
    security_incident = security.create_incident(
        title="SQL Injection Attack Detected",
        description="Multiple SQL injection attempts on /api/users endpoint",
        severity=SeverityLevel.CRITICAL,
        threat_type=ThreatType.SQL_INJECTION,
        source_ip="192.168.1.100",
        target_resource="/api/users",
    )
    print(f"   Incident ID: {security_incident.incident_id}")
    print(f"   Severity: {security_incident.severity.value}")
    print(f"   Auto-response actions: {len(security_incident.response_actions)}")
    print()
    
    # DevOps Agent creates emergency deployment
    print("2. DevOps Agent initiates emergency patch...")
    patch = devops.create_deployment(
        application="security-patch",
        version="1.0.1-hotfix",
        environment="production",
        deployed_by="security-agent",
    )
    devops.update_deployment_status(patch.deployment_id, DeploymentStatus.DEPLOYING)
    devops.update_deployment_status(patch.deployment_id, DeploymentStatus.DEPLOYED)
    print(f"   Emergency patch deployed: {patch.version}")
    print()
    
    # Support Agent creates high-priority ticket
    print("3. Support Agent creates incident ticket...")
    ticket = support.create_ticket(
        subject="SECURITY INCIDENT: SQL Injection Attack",
        description=f"Attack detected from {security_incident.source_ip}. Emergency patch deployed.",
        customer_id="internal",
        customer_email="security@example.com",
        priority=TicketPriority.CRITICAL,
        category=TicketCategory.TECHNICAL,
    )
    print(f"   Ticket ID: {ticket.ticket_id}")
    print(f"   Priority: {ticket.priority.value}")
    print()
    
    # Generate incident report
    print("4. Incident Summary:")
    print(f"   ✓ Security incident logged")
    print(f"   ✓ Emergency patch deployed")
    print(f"   ✓ Support ticket created")
    print()


def example_product_launch_workflow():
    """Example: Multi-agent product launch workflow."""
    print("=" * 70)
    print("Example 2: Multi-Agent Product Launch")
    print("=" * 70)
    print()
    
    # Initialize agents
    devops = DevOpsAgent()
    data = DataAnalystAgent()
    support = SupportAgent()
    
    print("🚀 PRODUCT LAUNCH: Version 2.0\n")
    
    # DevOps: Create deployment pipeline
    print("1. DevOps Agent sets up deployment pipeline...")
    pipeline = devops.create_pipeline(
        name="v2.0 Launch Pipeline",
        repository="my-app",
        branch="release/v2.0",
        stages=["build", "test", "staging-deploy", "load-test", "prod-deploy"],
    )
    devops.start_pipeline(pipeline.pipeline_id)
    
    # Simulate pipeline progress
    for stage in pipeline.stages:
        devops.update_pipeline_stage(pipeline.pipeline_id, stage, "passed")
        print(f"   ✓ Stage '{stage}' passed")
    print()
    
    # DevOps: Deploy to production
    print("2. DevOps Agent deploys to production...")
    deployment = devops.create_deployment(
        application="my-app",
        version="2.0.0",
        environment="production",
        deployed_by="release-bot",
    )
    devops.update_deployment_status(deployment.deployment_id, DeploymentStatus.DEPLOYED)
    print(f"   ✓ Deployed {deployment.application}:{deployment.version}")
    print()
    
    # Data Analyst: Set up launch metrics tracking
    print("3. Data Analyst Agent sets up metrics tracking...")
    metrics_dataset = data.register_dataset(
        name="Launch Day Metrics",
        source="analytics",
        columns=['timestamp', 'users', 'signups', 'revenue', 'errors'],
    )
    
    # Simulate loading launch data
    launch_data = [
        {'timestamp': '09:00', 'users': 1000, 'signups': 50, 'revenue': 5000, 'errors': 0},
        {'timestamp': '10:00', 'users': 2500, 'signups': 150, 'revenue': 15000, 'errors': 2},
        {'timestamp': '11:00', 'users': 5000, 'signups': 300, 'revenue': 30000, 'errors': 1},
    ]
    data.load_data(metrics_dataset.dataset_id, launch_data)
    
    stats = data.calculate_statistics(metrics_dataset.dataset_id, 'users')
    print(f"   ✓ Tracking {stats['count']} data points")
    print(f"   ✓ Avg users: {stats['mean']:.0f}")
    print()
    
    # Support: Prepare for influx of tickets
    print("4. Support Agent prepares support team...")
    support.add_knowledge_article(
        title="What's New in Version 2.0",
        content="Version 2.0 includes: new dashboard, improved performance, dark mode...",
        category="product",
        tags=["v2.0", "release", "features"],
    )
    print(f"   ✓ Knowledge base updated")
    print(f"   ✓ Total articles: {len(support.knowledge_base)}")
    print()
    
    # Launch summary
    print("5. Launch Summary:")
    print(f"   ✓ Pipeline: {pipeline.status.value}")
    print(f"   ✓ Deployment: {deployment.status.value}")
    print(f"   ✓ Metrics: {stats['count']} data points collected")
    print(f"   ✓ Support: KB ready with {len(support.knowledge_base)} articles")
    print()


def example_monthly_reporting_workflow():
    """Example: Multi-agent monthly reporting workflow."""
    print("=" * 70)
    print("Example 3: Multi-Agent Monthly Reporting")
    print("=" * 70)
    print()
    
    # Initialize agents
    devops = DevOpsAgent()
    data = DataAnalystAgent()
    support = SupportAgent()
    security = SecurityAgent()
    
    print("📊 MONTHLY REPORT: March 2026\n")
    
    # DevOps: Infrastructure report
    print("1. DevOps Agent - Infrastructure Report:")
    infra_summary = devops.get_infrastructure_summary()
    print(f"   Resources: {infra_summary['total_resources']}")
    print(f"   Monthly Cost: ${infra_summary['monthly_cost']:.2f}")
    print(f"   Deployments: {len(devops.get_deployments())}")
    print(f"   Pipelines: {len(devops.get_pipelines())}")
    print()
    
    # Data Analyst: Business metrics report
    print("2. Data Analyst Agent - Business Metrics:")
    metrics = data.register_dataset("Monthly Metrics", "analytics", ['metric', 'value'])
    data.load_data(metrics.dataset_id, [
        {'metric': 'users', 'value': 50000},
        {'metric': 'signups', 'value': 5000},
        {'metric': 'churn', 'value': 2.5},
    ])
    insights = data.generate_insights(metrics.dataset_id)
    print(f"   Datasets analyzed: {len(data.datasets)}")
    print(f"   Insights generated: {len(insights.insights)}")
    print()
    
    # Support: Customer support report
    print("3. Support Agent - Support Report:")
    support_metrics = support.get_support_metrics(days=30)
    print(f"   Total Tickets: {support_metrics['total_tickets']}")
    print(f"   Avg Resolution: {support_metrics['avg_resolution_time_minutes']:.0f} min")
    print(f"   Satisfaction: {support_metrics['avg_satisfaction_score']:.1f}/5 ⭐")
    print(f"   SLA Breaches: {support_metrics['sla_breaches']}")
    print()
    
    # Security: Security report
    print("4. Security Agent - Security Report:")
    security_report = security.generate_security_report(period_days=30)
    print(f"   Findings: {security_report['findings']['total']}")
    print(f"   Incidents: {security_report['incidents']['total']}")
    print(f"   Critical: {security_report['incidents']['critical']}")
    print(f"   Secrets Tracked: {security_report['secrets']['total_tracked']}")
    print()
    
    # Consolidated report
    print("5. Consolidated Monthly Report:")
    print(f"   ┌─────────────────────────────────────┐")
    print(f"   │ Infrastructure: {infra_summary['total_resources']} resources, ${infra_summary['monthly_cost']:.2f}/mo │")
    print(f"   │ Business: {metrics.row_count} metrics tracked                  │")
    print(f"   │ Support: {support_metrics['total_tickets']} tickets, {support_metrics['avg_satisfaction_score']:.1f}⭐ satisfaction    │")
    print(f"   │ Security: {security_report['incidents']['total']} incidents, {security_report['findings']['total']} findings      │")
    print(f"   └─────────────────────────────────────┘")
    print()


def example_cost_optimization_workflow():
    """Example: Multi-agent cost optimization workflow."""
    print("=" * 70)
    print("Example 4: Multi-Agent Cost Optimization")
    print("=" * 70)
    print()
    
    # Initialize agents
    devops = DevOpsAgent()
    data = DataAnalystAgent()
    
    print("💰 COST OPTIMIZATION ANALYSIS\n")
    
    # DevOps: Analyze infrastructure costs
    print("1. DevOps Agent - Infrastructure Cost Analysis:")
    cost_report = devops.get_cost_report(days=30)
    print(f"   Current Monthly: ${cost_report['current_costs']['monthly_cost']:.2f}")
    print(f"   Potential Savings: ${cost_report['potential_monthly_savings']:.2f}")
    
    if cost_report['optimization_opportunities']:
        print(f"   Opportunities: {len(cost_report['optimization_opportunities'])}")
        for opp in cost_report['optimization_opportunities'][:2]:
            print(f"      - {opp['recommendation'][:60]}...")
    print()
    
    # Data Analyst: Cost trend analysis
    print("2. Data Analyst Agent - Cost Trend Analysis:")
    cost_data = data.register_dataset("Monthly Costs", "finance", ['month', 'cost'])
    data.load_data(cost_data.dataset_id, [
        {'month': 'Jan', 'cost': 8000},
        {'month': 'Feb', 'cost': 8500},
        {'month': 'Mar', 'cost': 9200},
    ])
    
    trend = data.detect_trends(cost_data.dataset_id, 'cost', 'month')
    print(f"   Trend: {trend['trend']}")
    print(f"   Growth Rate: {trend['growth_rate_percent']:.1f}%")
    
    if trend['trend'] == 'increasing':
        print(f"   ⚠️  Costs are increasing - action needed!")
    print()
    
    # Recommendations
    print("3. Optimization Recommendations:")
    print(f"   ✓ Right-size underutilized resources")
    print(f"   ✓ Implement auto-scaling policies")
    print(f"   ✓ Review reserved instance options")
    print(f"   ✓ Set up cost alerts at ${cost_report['current_costs']['monthly_cost'] * 1.1:.2f}")
    print()
    
    total_savings = cost_report['potential_monthly_savings']
    print(f"   Potential Annual Savings: ${total_savings * 12:,.2f}")
    print()


def main():
    """Run all multi-agent orchestration examples."""
    print("\n" + "=" * 70)
    print("Multi-Agent Orchestration - Comprehensive Examples")
    print("=" * 70)
    
    example_incident_response_workflow()
    example_product_launch_workflow()
    example_monthly_reporting_workflow()
    example_cost_optimization_workflow()
    
    print("\n" + "=" * 70)
    print("All orchestration examples complete!")
    print("=" * 70)
    print()
    print("Key Takeaways:")
    print("  • Agents work together seamlessly through shared state")
    print("  • Lead Agent can orchestrate complex multi-domain workflows")
    print("  • Each agent specializes in its domain while collaborating")
    print("  • Combined capabilities exceed sum of individual agents")
    print()


if __name__ == "__main__":
    main()
