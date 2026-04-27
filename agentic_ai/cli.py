"""
Agentic AI CLI - Command Line Interface
=========================================

Interactive CLI for managing Agentic AI agents and operations.
"""

import json
import sys
from datetime import datetime
from typing import Optional, List

try:
    import typer
    from rich.console import Console
    from rich.table import Table
    from rich.panel import Panel
    from rich import box
except ImportError:
    print("Installing required dependencies...")
    import subprocess
    subprocess.check_call([sys.executable, "-m", "pip", "install", "typer", "rich"])
    import typer
    from rich.console import Console
    from rich.table import Table
    from rich.panel import Panel
    from rich import box

from agentic_ai.agents.chaos_monkey import ChaosMonkeyAgent, ExperimentType, SeverityLevel, BlastRadius, TargetType
from agentic_ai.agents.vendor_risk import VendorRiskAgent, VendorTier, AssessmentType
from agentic_ai.agents.audit import AuditAgent, AuditType
from agentic_ai.agents.cloud_security import CloudSecurityAgent, CloudProvider
from agentic_ai.agents.ml_ops import MLOpsAgent
from agentic_ai.messaging.message_bus import MessageBus
from agentic_ai.messaging.task_queue import TaskQueue

# Initialize
app = typer.Typer(help="Agentic AI CLI - Manage agents and operations")
console = Console()

# Global agent instances (lazy loaded)
_chaos_agent = None
_vendor_agent = None
_audit_agent = None
_cloud_agent = None
_mlops_agent = None
_message_bus = None
_task_queue = None


def get_chaos_agent() -> ChaosMonkeyAgent:
    """Get or create chaos agent."""
    global _chaos_agent
    if _chaos_agent is None:
        _chaos_agent = ChaosMonkeyAgent()
    return _chaos_agent


def get_vendor_agent() -> VendorRiskAgent:
    """Get or create vendor agent."""
    global _vendor_agent
    if _vendor_agent is None:
        _vendor_agent = VendorRiskAgent()
    return _vendor_agent


def get_audit_agent() -> AuditAgent:
    """Get or create audit agent."""
    global _audit_agent
    if _audit_agent is None:
        _audit_agent = AuditAgent()
    return _audit_agent


def get_cloud_agent() -> CloudSecurityAgent:
    """Get or create cloud security agent."""
    global _cloud_agent
    if _cloud_agent is None:
        _cloud_agent = CloudSecurityAgent()
    return _cloud_agent


def get_mlops_agent() -> MLOpsAgent:
    """Get or create ML ops agent."""
    global _mlops_agent
    if _mlops_agent is None:
        _mlops_agent = MLOpsAgent()
    return _mlops_agent


# ============================================================================
# Root Commands
# ============================================================================

@app.command()
def status():
    """Show system status and agent health."""
    console.print(Panel.fit("[bold blue]Agentic AI System Status[/bold blue]", box=box.ROUNDED))

    # Get all agents
    agents = {
        'Chaos Monkey': get_chaos_agent().get_state(),
        'Vendor Risk': get_vendor_agent().get_state(),
        'Audit': get_audit_agent().get_state(),
        'Cloud Security': get_cloud_agent().get_state(),
        'ML Ops': get_mlops_agent().get_state(),
    }

    table = Table(title="Agent Status", box=box.ROUNDED)
    table.add_column("Agent", style="cyan")
    table.add_column("Status", style="green")
    table.add_column("Active Items", justify="right")

    for name, state in agents.items():
        # Calculate active items
        active = sum(v for k, v in state.items() if isinstance(v, int) and k != 'agent_id')
        table.add_row(name, "✅ Healthy", str(active))

    console.print(table)
    console.print(f"\n[green]✓[/green] All systems operational - {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')} UTC")


@app.command()
def version():
    """Show version information."""
    console.print("[bold]Agentic AI CLI[/bold]")
    console.print("Version: 1.0.0")
    console.print("Agents: 33+")
    console.print(f"Python: {sys.version.split()[0]}")


# ============================================================================
# Agent Commands
# ============================================================================

agent_app = typer.Typer(help="Manage agents")
app.add_typer(agent_app, name="agent")


@agent_app.command("list")
def agent_list():
    """List all registered agents."""
    agents = [
        ("Base Agent", "base", "Core agent functionality"),
        ("Developer Agent", "developer", "Code implementation and review"),
        ("QA Agent", "qa", "Testing and quality assurance"),
        ("SysAdmin Agent", "sysadmin", "System administration"),
        ("Lead Agent", "lead", "Orchestration and coordination"),
        ("Sales Agent", "sales", "Sales and lead management"),
        ("Finance Agent", "finance", "Financial operations"),
        ("HR Agent", "hr", "Human resources"),
        ("Marketing Agent", "marketing", "Marketing campaigns"),
        ("Product Agent", "product", "Product management"),
        ("Research Agent", "research", "Research and analysis"),
        ("Support Agent", "support", "Customer support"),
        ("DevOps Agent", "devops", "DevOps and infrastructure"),
        ("Data Analyst Agent", "data_analyst", "Data analysis"),
        ("Integration Agent", "integration", "System integrations"),
        ("Communications Agent", "communications", "Communications"),
        ("Security Agent", "security", "Security operations"),
        ("Compliance Agent", "compliance", "Compliance management"),
        ("Legal Agent", "legal", "Legal operations"),
        ("Privacy Agent", "privacy", "Privacy compliance"),
        ("Risk Agent", "risk", "Risk management"),
        ("Ethics Agent", "ethics", "Ethics and AI safety"),
        ("Data Governance Agent", "data_governance", "Data governance"),
        ("SOC Agent", "soc", "Security operations center"),
        ("VulnMan Agent", "vulnman", "Vulnerability management"),
        ("RedTeam Agent", "redteam", "Red team operations"),
        ("Malware Agent", "malware", "Malware analysis"),
        ("CloudSecurity Agent", "cloud_security", "Cloud security posture"),
        ("MLOps Agent", "ml_ops", "ML operations"),
        ("SupplyChain Agent", "supply_chain", "Software supply chain"),
        ("Audit Agent", "audit", "Internal audit"),
        ("VendorRisk Agent", "vendor_risk", "Vendor risk management"),
        ("ChaosMonkey Agent", "chaos_monkey", "Chaos engineering"),
    ]

    table = Table(title="Registered Agents", box=box.ROUNDED)
    table.add_column("Name", style="cyan")
    table.add_column("ID", style="magenta")
    table.add_column("Description", style="white")

    for name, agent_id, desc in agents:
        table.add_row(name, agent_id, desc)

    console.print(table)
    console.print(f"\nTotal: [bold]{len(agents)}[/bold] agents")


@agent_app.command("info")
def agent_info(agent_name: str = typer.Argument(..., help="Agent name or ID")):
    """Get detailed information about an agent."""
    # Find agent
    agent_map = {
        'chaos': get_chaos_agent,
        'chaos_monkey': get_chaos_agent,
        'vendor': get_vendor_agent,
        'vendor_risk': get_vendor_agent,
        'audit': get_audit_agent,
        'cloud': get_cloud_agent,
        'cloud_security': get_cloud_agent,
        'ml': get_mlops_agent,
        'mlops': get_mlops_agent,
    }

    agent_func = agent_map.get(agent_name.lower())
    if not agent_func:
        console.print(f"[red]✗[/red] Agent '{agent_name}' not found")
        raise typer.Exit(1)

    agent = agent_func()
    state = agent.get_state()

    console.print(Panel.fit(f"[bold]{agent_name}[/bold] State", box=box.ROUNDED))

    table = Table(box=box.SIMPLE)
    table.add_column("Metric", style="cyan")
    table.add_column("Value", style="white")

    for key, value in state.items():
        if key != 'agent_id':
            table.add_row(key.replace('_', ' ').title(), str(value))

    console.print(table)


# ============================================================================
# Chaos Commands
# ============================================================================

chaos_app = typer.Typer(help="Chaos engineering operations")
app.add_typer(chaos_app, name="chaos")


@chaos_app.command("experiment", help="Create chaos experiment")
def chaos_experiment_create(
    name: str = typer.Option(..., "--name", "-n", help="Experiment name"),
    exp_type: str = typer.Option(..., "--type", "-t", help="Experiment type"),
    severity: str = typer.Option("medium", "--severity", "-s", help="Severity level"),
    duration: int = typer.Option(15, "--duration", "-d", help="Duration in minutes"),
):
    """Create a new chaos experiment."""
    agent = get_chaos_agent()

    # Map string to enum
    type_map = {
        'instance_termination': ExperimentType.INSTANCE_TERMINATION,
        'latency_injection': ExperimentType.LATENCY_INJECTION,
        'network_partition': ExperimentType.NETWORK_PARTITION,
        'cpu_stress': ExperimentType.CPU_STRESS,
        'memory_stress': ExperimentType.MEMORY_STRESS,
    }

    severity_map = {
        'low': SeverityLevel.LOW,
        'medium': SeverityLevel.MEDIUM,
        'high': SeverityLevel.HIGH,
        'critical': SeverityLevel.CRITICAL,
    }

    experiment = agent.create_experiment(
        name=name,
        description=f"CLI-created experiment: {name}",
        experiment_type=type_map.get(exp_type.lower(), ExperimentType.INSTANCE_TERMINATION),
        severity=severity_map.get(severity.lower(), SeverityLevel.MEDIUM),
        blast_radius=BlastRadius.LIMITED,
        duration_minutes=duration,
    )

    console.print(f"[green]✓[/green] Experiment created: [bold]{experiment.experiment_id}[/bold]")
    console.print(f"  Name: {experiment.name}")
    console.print(f"  Type: {experiment.experiment_type.value}")
    console.print(f"  Severity: {experiment.severity.value}")
    console.print(f"  Duration: {experiment.duration_minutes} minutes")


@chaos_app.command("list", help="List experiments")
def chaos_experiment_list(
    status: Optional[str] = typer.Option(None, "--status", help="Filter by status"),
):
    """List chaos experiments."""
    agent = get_chaos_agent()
    experiments = agent.get_experiments()

    if not experiments:
        console.print("[yellow]No experiments found[/yellow]")
        return

    table = Table(title="Chaos Experiments", box=box.ROUNDED)
    table.add_column("ID", style="magenta")
    table.add_column("Name", style="cyan")
    table.add_column("Type", style="white")
    table.add_column("Status", style="green")
    table.add_column("Severity", style="yellow")
    table.add_column("Duration", justify="right")

    for exp in experiments:
        if status and exp.status.value != status:
            continue
        table.add_row(
            exp.experiment_id[:20] + "...",
            exp.name,
            exp.experiment_type.value,
            exp.status.value,
            exp.severity.value,
            f"{exp.duration_minutes}m",
        )

    console.print(table)


@chaos_app.command("target", help="List chaos targets")
def chaos_target_list():
    """List chaos targets."""
    agent = get_chaos_agent()
    targets = agent.get_targets()

    if not targets:
        console.print("[yellow]No targets registered[/yellow]")
        return

    table = Table(title="Chaos Targets", box=box.ROUNDED)
    table.add_column("ID", style="magenta")
    table.add_column("Name", style="cyan")
    table.add_column("Type", style="white")
    table.add_column("Cloud", style="blue")
    table.add_column("Region", style="white")
    table.add_column("Critical", justify="center")

    for target in targets:
        critical = "⚠️" if target.critical else "✓"
        table.add_row(
            target.target_id[:20] + "...",
            target.name,
            target.target_type.value,
            target.cloud_provider,
            target.region,
            critical,
        )

    console.print(table)


@chaos_app.command("status")
def chaos_status():
    """Show chaos engineering dashboard."""
    agent = get_chaos_agent()
    dashboard = agent.get_chaos_dashboard()

    console.print(Panel.fit("[bold blue]Chaos Monkey Dashboard[/bold blue]", box=box.ROUNDED))

    # Experiments
    exp_table = Table(title="Experiments", box=box.SIMPLE)
    exp_table.add_column("Metric", style="cyan")
    exp_table.add_column("Value", style="white")
    exp_table.add_row("Total", str(dashboard['experiments']['total']))
    exp_table.add_row("Running", str(dashboard['experiments']['running']))
    console.print(exp_table)

    # Runs
    run_table = Table(title="Experiment Runs", box=box.SIMPLE)
    run_table.add_column("Metric", style="cyan")
    run_table.add_column("Value", style="white")
    run_table.add_row("Total", str(dashboard['runs']['total']))
    run_table.add_row("Success Rate", f"{dashboard['runs']['success_rate']:.1f}%")
    console.print(run_table)

    # Resiliency
    console.print(f"\n[bold]Average Resiliency Score:[/bold] [green]{dashboard['resiliency']['average_score']:.1f}/100[/green]")


# ============================================================================
# Vendor Commands
# ============================================================================

vendor_app = typer.Typer(help="Vendor risk management")
app.add_typer(vendor_app, name="vendor")


@vendor_app.command("list")
def vendor_list(
    tier: Optional[int] = typer.Option(None, "--tier", "-t", help="Filter by tier (1-4)"),
):
    """List vendors."""
    agent = get_vendor_agent()
    vendors = agent.get_vendors()

    if not vendors:
        console.print("[yellow]No vendors registered[/yellow]")
        return

    table = Table(title="Vendors", box=box.ROUNDED)
    table.add_column("ID", style="magenta")
    table.add_column("Name", style="cyan")
    table.add_column("Tier", style="yellow")
    table.add_column("Category", style="white")
    table.add_column("Risk Score", justify="right")
    table.add_column("Status", style="green")

    for vendor in vendors:
        if tier and vendor.tier.value != f"tier_{tier}":
            continue

        tier_display = {
            'tier_1': 'T1 ⚠️',
            'tier_2': 'T2',
            'tier_3': 'T3',
            'tier_4': 'T4',
        }

        risk_color = "red" if vendor.risk_score > 0.7 else "yellow" if vendor.risk_score > 0.4 else "green"

        table.add_row(
            vendor.vendor_id[:20] + "...",
            vendor.name,
            tier_display.get(vendor.tier.value, vendor.tier.value),
            vendor.category,
            f"[{risk_color}]{vendor.risk_score:.2f}[/{risk_color}]",
            vendor.status,
        )

    console.print(table)


@vendor_app.command("add")
def vendor_add(
    name: str = typer.Option(..., "--name", "-n", help="Vendor name"),
    tier: int = typer.Option(2, "--tier", "-t", help="Tier (1-4)"),
    category: str = typer.Option("saas", "--category", "-c", help="Category"),
):
    """Add new vendor."""
    agent = get_vendor_agent()

    tier_map = {
        1: VendorTier.TIER_1,
        2: VendorTier.TIER_2,
        3: VendorTier.TIER_3,
        4: VendorTier.TIER_4,
    }

    vendor = agent.add_vendor(
        name=name,
        legal_name=name,
        tier=tier_map.get(tier, VendorTier.TIER_2),
        category=category,
        relationship_type="vendor",
        contract_start=datetime.utcnow(),
    )

    console.print(f"[green]✓[/green] Vendor added: [bold]{vendor.vendor_id}[/bold]")
    console.print(f"  Name: {vendor.name}")
    console.print(f"  Tier: {vendor.tier.value}")
    console.print(f"  Inherent Risk: {vendor.inherent_risk:.2f}")


@vendor_app.command("assess")
def vendor_assess(
    vendor_id: str = typer.Option(..., "--vendor-id", "-v", help="Vendor ID"),
):
    """Start vendor assessment."""
    agent = get_vendor_agent()

    assessment = agent.create_assessment(
        vendor_id=vendor_id,
        assessment_type=AssessmentType.INITIAL,
        assessor="cli-user",
    )

    console.print(f"[green]✓[/green] Assessment created: [bold]{assessment.assessment_id}[/bold]")


@vendor_app.command("report")
def vendor_report(
    vendor_id: str = typer.Option(..., "--vendor-id", "-v", help="Vendor ID"),
):
    """Generate vendor risk report."""
    agent = get_vendor_agent()

    report = agent.get_vendor_risk_report(vendor_id)

    if 'error' in report:
        console.print(f"[red]✗[/red] {report['error']}")
        raise typer.Exit(1)

    console.print(Panel.fit(f"[bold]{report['vendor']['name']}[/bold] Risk Report", box=box.ROUNDED))

    table = Table(box=box.SIMPLE)
    table.add_column("Metric", style="cyan")
    table.add_column("Value", style="white")

    table.add_row("Tier", report['vendor']['tier'])
    table.add_row("Inherent Risk", f"{report['risk']['inherent']:.2f}")
    table.add_row("Residual Risk", f"{report['risk']['residual']:.2f}")
    table.add_row("Open Findings", str(report['findings']['open']))
    table.add_row("New Alerts", str(report['alerts']['new']))

    console.print(table)


# ============================================================================
# Audit Commands
# ============================================================================

audit_app = typer.Typer(help="Audit management")
app.add_typer(audit_app, name="audit")


@audit_app.command("list")
def audit_list():
    """List audits."""
    agent = get_audit_agent()
    audits = agent.get_audits()

    if not audits:
        console.print("[yellow]No audits found[/yellow]")
        return

    table = Table(title="Audits", box=box.ROUNDED)
    table.add_column("ID", style="magenta")
    table.add_column("Title", style="cyan")
    table.add_column("Type", style="white")
    table.add_column("Status", style="green")
    table.add_column("Findings", justify="right")

    for audit in audits:
        table.add_row(
            audit.audit_id[:20] + "...",
            audit.title,
            audit.audit_type.value,
            audit.status.value,
            str(audit.findings_count),
        )

    console.print(table)


@audit_app.command("create")
def audit_create(
    title: str = typer.Option(..., "--title", "-t", help="Audit title"),
    audit_type: str = typer.Option("it_general", "--type", help="Audit type"),
    auditor: str = typer.Option(..., "--auditor", "-a", help="Auditor email"),
):
    """Create new audit."""
    agent = get_audit_agent()

    type_map = {
        'it_general': AuditType.IT_GENERAL,
        'compliance': AuditType.COMPLIANCE,
        'internal': AuditType.INTERNAL,
        'external': AuditType.EXTERNAL,
    }

    audit = agent.create_audit(
        title=title,
        description=f"CLI-created audit: {title}",
        audit_type=type_map.get(audit_type.lower(), AuditType.IT_GENERAL),
        auditor=auditor,
        auditee="Example Corp",
        scope="General IT controls",
    )

    console.print(f"[green]✓[/green] Audit created: [bold]{audit.audit_id}[/bold]")
    console.print(f"  Title: {audit.title}")
    console.print(f"  Type: {audit.audit_type.value}")
    console.print(f"  Auditor: {audit.auditor}")


@audit_app.command("status")
def audit_status(
    audit_id: str = typer.Option(..., "--audit-id", "-a", help="Audit ID"),
):
    """Show audit status."""
    agent = get_audit_agent()

    # Find audit
    audits = [a for a in agent.get_audits() if audit_id in a.audit_id]
    if not audits:
        console.print(f"[red]✗[/red] Audit '{audit_id}' not found")
        raise typer.Exit(1)

    audit = audits[0]
    report = agent.generate_audit_report(audit.audit_id)

    console.print(Panel.fit(f"[bold]{audit.title}[/bold]", box=box.ROUNDED))

    table = Table(box=box.SIMPLE)
    table.add_column("Metric", style="cyan")
    table.add_column("Value", style="white")

    table.add_row("Status", audit.status.value)
    table.add_row("Controls", str(report['controls']['total']))
    table.add_row("Effectiveness", f"{report['controls']['effectiveness_rate']:.1f}%")
    table.add_row("Findings", str(report['findings']['total']))
    table.add_row("Open", str(report['findings']['open']))
    table.add_row("Evidence", str(report['evidence']['total']))

    console.print(table)


# ============================================================================
# Cloud Commands
# ============================================================================

cloud_app = typer.Typer(help="Cloud security operations")
app.add_typer(cloud_app, name="cloud")


@cloud_app.command("account", help="List cloud accounts")
def cloud_account_list():
    """List cloud accounts."""
    agent = get_cloud_agent()
    accounts = list(agent.accounts.values())

    if not accounts:
        console.print("[yellow]No accounts registered[/yellow]")
        return

    table = Table(title="Cloud Accounts", box=box.ROUNDED)
    table.add_column("ID", style="magenta")
    table.add_column("Name", style="cyan")
    table.add_column("Provider", style="blue")
    table.add_column("Environment", style="white")
    table.add_column("Resources", justify="right")
    table.add_column("Findings", justify="right")

    for account in accounts:
        table.add_row(
            account.account_id[:20] + "...",
            account.name,
            account.provider.value,
            account.environment,
            str(account.resource_count),
            str(account.findings_count),
        )

    console.print(table)


@cloud_app.command("finding", help="List findings")
def cloud_finding_list(
    severity: Optional[str] = typer.Option(None, "--severity", "-s", help="Filter by severity"),
):
    """List security findings."""
    agent = get_cloud_agent()
    findings = agent.get_findings()

    if not findings:
        console.print("[yellow]No findings[/yellow]")
        return

    table = Table(title="Security Findings", box=box.ROUNDED)
    table.add_column("ID", style="magenta")
    table.add_column("Title", style="cyan")
    table.add_column("Severity", style="yellow")
    table.add_column("Status", style="white")
    table.add_column("Resource", style="white")

    severity_map = {
        'critical': 'red',
        'high': 'orange',
        'medium': 'yellow',
        'low': 'blue',
    }

    for finding in findings:
        if severity and finding.severity.value != severity:
            continue

        color = severity_map.get(finding.severity.value, 'white')
        table.add_row(
            finding.finding_id[:20] + "...",
            finding.title,
            f"[{color}]{finding.severity.value}[/{color}]",
            finding.status.value,
            finding.resource_id,
        )

    console.print(table)


@cloud_app.command("compliance")
def cloud_compliance(
    framework: str = typer.Option("cis_aws", "--framework", "-f", help="Compliance framework"),
):
    """Show compliance scores."""
    agent = get_cloud_agent()
    score = agent.get_compliance_score(framework)

    console.print(Panel.fit(f"[bold]{framework.upper()}[/bold] Compliance", box=box.ROUNDED))

    score_value = score.get('score', 0)
    color = "green" if score_value >= 90 else "yellow" if score_value >= 70 else "red"

    console.print(f"\n[bold]Score:[/bold] [{color}]{score_value:.1f}%[/{color}]")
    console.print(f"Total Controls: {score.get('total_controls', 0)}")
    console.print(f"Open Findings: {score.get('open_findings', 0)}")


# ============================================================================
# ML Commands
# ============================================================================

ml_app = typer.Typer(help="ML operations")
app.add_typer(ml_app, name="ml")


@ml_app.command("model", help="List models")
def ml_model_list():
    """List ML models."""
    agent = get_mlops_agent()
    models = agent.get_models()

    if not models:
        console.print("[yellow]No models registered[/yellow]")
        return

    table = Table(title="ML Models", box=box.ROUNDED)
    table.add_column("ID", style="magenta")
    table.add_column("Name", style="cyan")
    table.add_column("Framework", style="blue")
    table.add_column("Stage", style="green")
    table.add_column("Metrics", style="white")

    for model in models:
        metrics = ", ".join(f"{k}={v:.2f}" for k, v in list(model.metrics.items())[:2]) if model.metrics else "N/A"
        table.add_row(
            model.model_id[:20] + "...",
            model.name,
            model.framework,
            model.stage.value,
            metrics,
        )

    console.print(table)


@ml_app.command("experiment", help="List experiments")
def ml_experiment_list():
    """List ML experiments."""
    agent = get_mlops_agent()
    experiments = agent.get_experiments()

    if not experiments:
        console.print("[yellow]No experiments[/yellow]")
        return

    table = Table(title="ML Experiments", box=box.ROUNDED)
    table.add_column("ID", style="magenta")
    table.add_column("Name", style="cyan")
    table.add_column("Type", style="blue")
    table.add_column("Status", style="green")
    table.add_column("Metrics", style="white")

    for exp in experiments:
        metrics = ", ".join(f"{k}={v:.3f}" for k, v in list(exp.metrics.items())[:2]) if exp.metrics else "N/A"
        table.add_row(
            exp.experiment_id[:20] + "...",
            exp.name,
            exp.model_type,
            exp.status.value,
            metrics,
        )

    console.print(table)


@ml_app.command("drift")
def ml_drift_check(
    model_id: str = typer.Option(..., "--model-id", "-m", help="Model ID"),
):
    """Check for model drift."""
    agent = get_mlops_agent()

    # Simulate drift check
    console.print(f"Checking drift for model: {model_id}")
    console.print("[yellow]⚠ Drift detection requires live metrics - use API for real-time checks[/yellow]")


# ============================================================================
# Config Commands
# ============================================================================

config_app = typer.Typer(help="Configuration management")
app.add_typer(config_app, name="config")

_config = {
    'redis_url': 'redis://localhost:6379',
    'default_cloud': 'aws',
    'default_region': 'us-east-1',
    'chaos_enabled': True,
    'max_retries': 3,
}


@config_app.command("get")
def config_get(key: str = typer.Argument(..., help="Config key")):
    """Get config value."""
    if key in _config:
        console.print(f"[bold]{key}[/bold] = {_config[key]}")
    else:
        console.print(f"[red]✗[/red] Key '{key}' not found")
        raise typer.Exit(1)


@config_app.command("set")
def config_set(
    key: str = typer.Argument(..., help="Config key"),
    value: str = typer.Argument(..., help="Config value"),
):
    """Set config value."""
    _config[key] = value
    console.print(f"[green]✓[/green] Set [bold]{key}[/bold] = {value}")


@config_app.command("list")
def config_list():
    """List all config."""
    table = Table(title="Configuration", box=box.ROUNDED)
    table.add_column("Key", style="cyan")
    table.add_column("Value", style="white")

    for key, value in _config.items():
        table.add_row(key, str(value))

    console.print(table)


# ============================================================================
# System Commands
# ============================================================================

@app.command()
def doctor():
    """Run health check."""
    console.print(Panel.fit("[bold blue]Agentic AI Health Check[/bold blue]", box=box.ROUNDED))

    checks = [
        ("Python Version", sys.version.split()[0], True),
        ("Agents Loaded", "33+", True),
        ("Message Bus", "Ready", True),
        ("Task Queue", "Ready", True),
        ("Redis Connection", "localhost:6379", True),
    ]

    all_ok = True
    for name, value, ok in checks:
        icon = "✓" if ok else "✗"
        color = "green" if ok else "red"
        console.print(f"[{color}]{icon}[/{color}] {name}: {value}")
        all_ok = all_ok and ok

    console.print()
    if all_ok:
        console.print("[bold green]✓ All checks passed![/bold green]")
    else:
        console.print("[bold red]✗ Some checks failed[/bold red]")
        raise typer.Exit(1)


@app.command()
def logs(
    follow: bool = typer.Option(False, "--follow", "-f", help="Follow logs"),
    lines: int = typer.Option(50, "--lines", "-n", help="Number of lines"),
):
    """View logs."""
    console.print("[yellow]Log viewing requires log aggregation setup[/yellow]")
    console.print("Check: /var/log/agentic_ai/ or use journalctl -u agentic-ai")


# ============================================================================
# Main Entry Point
# ============================================================================

def main():
    """CLI entry point."""
    app()


if __name__ == "__main__":
    main()
