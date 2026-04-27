"""
ComplianceAgent - Regulatory Compliance & Auditing
====================================================

Provides compliance tracking, policy management, audit preparation,
risk assessment, and regulatory reporting.
"""

import logging
import secrets
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from typing import Any, Dict, List, Optional


logger = logging.getLogger(__name__)


class ComplianceStatus(Enum):
    """Compliance status."""
    COMPLIANT = "compliant"
    PARTIALLY_COMPLIANT = "partially_compliant"
    NON_COMPLIANT = "non_compliant"
    NOT_ASSESSED = "not_assessed"
    EXEMPT = "exempt"


class RiskLevel(Enum):
    """Risk assessment levels."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class AuditStatus(Enum):
    """Audit status."""
    PLANNED = "planned"
    IN_PROGRESS = "in_progress"
    REVIEW = "review"
    COMPLETED = "completed"
    REMEDIATION = "remediation"


class ControlType(Enum):
    """Control types."""
    ADMINISTRATIVE = "administrative"
    TECHNICAL = "technical"
    PHYSICAL = "physical"
    OPERATIONAL = "operational"


@dataclass
class Regulation:
    """Regulatory framework."""
    regulation_id: str
    name: str
    framework: str  # GDPR, HIPAA, SOC2, ISO27001, PCI-DSS, etc.
    jurisdiction: str
    status: ComplianceStatus
    effective_date: Optional[datetime] = None
    last_assessment: Optional[datetime] = None
    next_assessment: Optional[datetime] = None
    owner: Optional[str] = None
    controls_count: int = 0
    controls_passed: int = 0
    created_at: datetime = field(default_factory=datetime.utcnow)


@dataclass
class Control:
    """Compliance control."""
    control_id: str
    name: str
    description: str
    control_type: ControlType
    regulation_id: str
    status: ComplianceStatus
    evidence_required: bool = True
    evidence_locations: List[str] = field(default_factory=list)
    last_tested: Optional[datetime] = None
    test_frequency: str = "quarterly"  # monthly, quarterly, annually
    owner: Optional[str] = None
    risk_level: RiskLevel = RiskLevel.MEDIUM
    created_at: datetime = field(default_factory=datetime.utcnow)


@dataclass
class Audit:
    """Compliance audit."""
    audit_id: str
    name: str
    audit_type: str  # internal, external, certification
    regulation_id: str
    status: AuditStatus
    start_date: datetime
    end_date: Optional[datetime] = None
    auditor: Optional[str] = None
    findings: List[Dict[str, Any]] = field(default_factory=list)
    recommendations: List[str] = field(default_factory=list)
    score: Optional[float] = None
    created_at: datetime = field(default_factory=datetime.utcnow)


@dataclass
class Policy:
    """Company policy document."""
    policy_id: str
    title: str
    category: str  # security, privacy, hr, it, etc.
    version: str
    status: str  # draft, review, approved, archived
    effective_date: Optional[datetime] = None
    review_date: Optional[datetime] = None
    owner: Optional[str] = None
    approvers: List[str] = field(default_factory=list)
    related_controls: List[str] = field(default_factory=list)
    created_at: datetime = field(default_factory=datetime.utcnow)


@dataclass
class Finding:
    """Compliance finding."""
    finding_id: str
    title: str
    description: str
    severity: RiskLevel
    status: str  # open, in_progress, resolved, accepted
    regulation_id: Optional[str] = None
    control_id: Optional[str] = None
    audit_id: Optional[str] = None
    remediation_plan: str = ""
    due_date: Optional[datetime] = None
    resolved_date: Optional[datetime] = None
    assigned_to: Optional[str] = None
    created_at: datetime = field(default_factory=datetime.utcnow)


class ComplianceAgent:
    """
    Compliance Agent for regulatory compliance tracking,
    policy management, audit preparation, and risk assessment.
    """

    def __init__(self, agent_id: str = "compliance-agent"):
        self.agent_id = agent_id
        self.regulations: Dict[str, Regulation] = {}
        self.controls: Dict[str, Control] = {}
        self.audits: Dict[str, Audit] = {}
        self.policies: Dict[str, Policy] = {}
        self.findings: Dict[str, Finding] = {}

        # Pre-built framework templates
        self.framework_templates = self._init_framework_templates()

    def _init_framework_templates(self) -> Dict[str, Dict[str, Any]]:
        """Initialize compliance framework templates."""
        return {
            'SOC2': {
                'name': 'SOC 2 Type II',
                'trust_principles': ['security', 'availability', 'processing_integrity', 'confidentiality', 'privacy'],
                'controls_count': 85,
            },
            'ISO27001': {
                'name': 'ISO/IEC 27001:2022',
                'domains': 4,
                'controls_count': 93,
                'annexes': ['A.5', 'A.6', 'A.7', 'A.8'],
            },
            'GDPR': {
                'name': 'General Data Protection Regulation',
                'jurisdiction': 'EU',
                'principles': 7,
                'articles': 99,
            },
            'HIPAA': {
                'name': 'Health Insurance Portability and Accountability Act',
                'jurisdiction': 'USA',
                'rules': ['Privacy', 'Security', 'Breach Notification', 'Enforcement'],
            },
            'PCI-DSS': {
                'name': 'Payment Card Industry Data Security Standard',
                'requirements': 12,
                'levels': 4,
            },
            'CCPA': {
                'name': 'California Consumer Privacy Act',
                'jurisdiction': 'California, USA',
                'rights': ['know', 'delete', 'opt-out', 'non-discrimination'],
            },
        }

    # ============================================
    # Regulation Management
    # ============================================

    def add_regulation(
        self,
        name: str,
        framework: str,
        jurisdiction: str,
        owner: Optional[str] = None,
        next_assessment: Optional[datetime] = None,
    ) -> Regulation:
        """Add a regulatory framework to track."""
        regulation = Regulation(
            regulation_id=self._generate_id("reg"),
            name=name,
            framework=framework,
            jurisdiction=jurisdiction,
            status=ComplianceStatus.NOT_ASSESSED,
            owner=owner,
            next_assessment=next_assessment,
        )

        self.regulations[regulation.regulation_id] = regulation
        logger.info(f"Added regulation: {regulation.name}")
        return regulation

    def update_regulation_status(
        self,
        regulation_id: str,
        controls_passed: int,
        controls_total: int,
    ) -> bool:
        """Update regulation compliance status based on controls."""
        if regulation_id not in self.regulations:
            return False

        reg = self.regulations[regulation_id]
        reg.controls_count = controls_total
        reg.controls_passed = controls_passed
        reg.last_assessment = datetime.utcnow()

        # Calculate status
        compliance_rate = controls_passed / controls_total if controls_total > 0 else 0

        if compliance_rate >= 0.95:
            reg.status = ComplianceStatus.COMPLIANT
        elif compliance_rate >= 0.70:
            reg.status = ComplianceStatus.PARTIALLY_COMPLIANT
        else:
            reg.status = ComplianceStatus.NON_COMPLIANT

        return True

    def get_regulations(self, framework: Optional[str] = None) -> List[Regulation]:
        """Get regulations with filtering."""
        regulations = list(self.regulations.values())

        if framework:
            regulations = [r for r in regulations if r.framework == framework]

        return regulations

    # ============================================
    # Control Management
    # ============================================

    def create_control(
        self,
        name: str,
        description: str,
        control_type: ControlType,
        regulation_id: str,
        risk_level: RiskLevel = RiskLevel.MEDIUM,
        owner: Optional[str] = None,
        test_frequency: str = "quarterly",
    ) -> Control:
        """Create a compliance control."""
        control = Control(
            control_id=self._generate_id("ctrl"),
            name=name,
            description=description,
            control_type=control_type,
            regulation_id=regulation_id,
            status=ComplianceStatus.NOT_ASSESSED,
            owner=owner,
            risk_level=risk_level,
            test_frequency=test_frequency,
        )

        self.controls[control.control_id] = control

        # Update regulation controls count
        if regulation_id in self.regulations:
            self.regulations[regulation_id].controls_count += 1

        return control

    def test_control(
        self,
        control_id: str,
        passed: bool,
        evidence_locations: Optional[List[str]] = None,
    ) -> bool:
        """Test a control and update status."""
        if control_id not in self.controls:
            return False

        control = self.controls[control_id]
        control.last_tested = datetime.utcnow()
        control.evidence_locations = evidence_locations or []
        control.status = ComplianceStatus.COMPLIANT if passed else ComplianceStatus.NON_COMPLIANT

        return True

    def get_controls(
        self,
        regulation_id: Optional[str] = None,
        status: Optional[ComplianceStatus] = None,
        control_type: Optional[ControlType] = None,
    ) -> List[Control]:
        """Get controls with filtering."""
        controls = list(self.controls.values())

        if regulation_id:
            controls = [c for c in controls if c.regulation_id == regulation_id]

        if status:
            controls = [c for c in controls if c.status == status]

        if control_type:
            controls = [c for c in controls if c.control_type == control_type]

        return controls

    # ============================================
    # Audit Management
    # ============================================

    def create_audit(
        self,
        name: str,
        audit_type: str,
        regulation_id: str,
        start_date: datetime,
        auditor: Optional[str] = None,
    ) -> Audit:
        """Create a compliance audit."""
        audit = Audit(
            audit_id=self._generate_id("audit"),
            name=name,
            audit_type=audit_type,
            regulation_id=regulation_id,
            status=AuditStatus.PLANNED,
            start_date=start_date,
            auditor=auditor,
        )

        self.audits[audit.audit_id] = audit
        logger.info(f"Created audit: {audit.name}")
        return audit

    def start_audit(self, audit_id: str) -> bool:
        """Start an audit."""
        if audit_id not in self.audits:
            return False

        self.audits[audit_id].status = AuditStatus.IN_PROGRESS
        return True

    def complete_audit(
        self,
        audit_id: str,
        score: float,
        findings: Optional[List[Dict[str, Any]]] = None,
        recommendations: Optional[List[str]] = None,
    ) -> bool:
        """Complete an audit."""
        if audit_id not in self.audits:
            return False

        audit = self.audits[audit_id]
        audit.status = AuditStatus.COMPLETED
        audit.end_date = datetime.utcnow()
        audit.score = score
        audit.findings = findings or []
        audit.recommendations = recommendations or []

        return True

    def get_audits(self, status: Optional[AuditStatus] = None) -> List[Audit]:
        """Get audits with filtering."""
        audits = list(self.audits.values())

        if status:
            audits = [a for a in audits if a.status == status]

        return audits

    # ============================================
    # Policy Management
    # ============================================

    def create_policy(
        self,
        title: str,
        category: str,
        version: str,
        owner: Optional[str] = None,
        review_date: Optional[datetime] = None,
    ) -> Policy:
        """Create a policy document."""
        policy = Policy(
            policy_id=self._generate_id("policy"),
            title=title,
            category=category,
            version=version,
            status="draft",
            owner=owner,
            review_date=review_date,
        )

        self.policies[policy.policy_id] = policy
        return policy

    def approve_policy(self, policy_id: str, approver: str) -> bool:
        """Approve a policy."""
        if policy_id not in self.policies:
            return False

        policy = self.policies[policy_id]

        if approver not in policy.approvers:
            policy.approvers.append(approver)

        # Auto-approve if at least 2 approvers
        if len(policy.approvers) >= 2:
            policy.status = "approved"
            policy.effective_date = datetime.utcnow()

        return True

    def get_policies(
        self,
        category: Optional[str] = None,
        status: Optional[str] = None,
    ) -> List[Policy]:
        """Get policies with filtering."""
        policies = list(self.policies.values())

        if category:
            policies = [p for p in policies if p.category == category]

        if status:
            policies = [p for p in policies if p.status == status]

        return policies

    def get_policies_due_for_review(self, days_ahead: int = 30) -> List[Policy]:
        """Get policies due for review."""
        threshold = datetime.utcnow() + timedelta(days=days_ahead)

        return [
            p for p in self.policies.values()
            if p.review_date and p.review_date <= threshold and p.status == "approved"
        ]

    # ============================================
    # Finding Management
    # ============================================

    def create_finding(
        self,
        title: str,
        description: str,
        severity: RiskLevel,
        regulation_id: Optional[str] = None,
        control_id: Optional[str] = None,
        audit_id: Optional[str] = None,
        due_date: Optional[datetime] = None,
        assigned_to: Optional[str] = None,
    ) -> Finding:
        """Create a compliance finding."""
        finding = Finding(
            finding_id=self._generate_id("finding"),
            title=title,
            description=description,
            severity=severity,
            regulation_id=regulation_id,
            control_id=control_id,
            audit_id=audit_id,
            assigned_to=assigned_to,
            due_date=due_date,
        )

        self.findings[finding.finding_id] = finding
        logger.info(f"Created finding: {finding.title}")
        return finding

    def resolve_finding(
        self,
        finding_id: str,
        remediation_plan: str,
    ) -> bool:
        """Resolve a finding."""
        if finding_id not in self.findings:
            return False

        finding = self.findings[finding_id]
        finding.status = "resolved"
        finding.remediation_plan = remediation_plan
        finding.resolved_date = datetime.utcnow()

        return True

    def get_findings(
        self,
        severity: Optional[RiskLevel] = None,
        status: Optional[str] = None,
    ) -> List[Finding]:
        """Get findings with filtering."""
        findings = list(self.findings.values())

        if severity:
            findings = [f for f in findings if f.severity == severity]

        if status:
            findings = [f for f in findings if f.status == status]

        return findings

    # ============================================
    # Compliance Reporting
    # ============================================

    def get_compliance_report(self) -> Dict[str, Any]:
        """Generate comprehensive compliance report."""
        regulations = list(self.regulations.values())
        controls = list(self.controls.values())
        audits = list(self.audits.values())
        findings = list(self.findings.values())

        # Calculate overall compliance
        total_controls = len(controls)
        compliant_controls = len([c for c in controls if c.status == ComplianceStatus.COMPLIANT])
        compliance_rate = (compliant_controls / total_controls * 100) if total_controls > 0 else 0

        # Findings by severity
        critical_findings = len([f for f in findings if f.severity == RiskLevel.CRITICAL and f.status != 'resolved'])
        high_findings = len([f for f in findings if f.severity == RiskLevel.HIGH and f.status != 'resolved'])

        # Audit status
        completed_audits = len([a for a in audits if a.status == AuditStatus.COMPLETED])
        avg_audit_score = sum(a.score for a in audits if a.score) / completed_audits if completed_audits > 0 else 0

        return {
            'summary': {
                'compliance_rate': round(compliance_rate, 1),
                'total_regulations': len(regulations),
                'total_controls': total_controls,
                'compliant_controls': compliant_controls,
            },
            'regulations': {
                'compliant': len([r for r in regulations if r.status == ComplianceStatus.COMPLIANT]),
                'partial': len([r for r in regulations if r.status == ComplianceStatus.PARTIALLY_COMPLIANT]),
                'non_compliant': len([r for r in regulations if r.status == ComplianceStatus.NON_COMPLIANT]),
                'not_assessed': len([r for r in regulations if r.status == ComplianceStatus.NOT_ASSESSED]),
            },
            'findings': {
                'critical_open': critical_findings,
                'high_open': high_findings,
                'total_open': len([f for f in findings if f.status != 'resolved']),
                'total_resolved': len([f for f in findings if f.status == 'resolved']),
            },
            'audits': {
                'total': len(audits),
                'completed': completed_audits,
                'in_progress': len([a for a in audits if a.status == AuditStatus.IN_PROGRESS]),
                'average_score': round(avg_audit_score, 1),
            },
            'risk_score': self._calculate_risk_score(critical_findings, high_findings, compliance_rate),
        }

    def _calculate_risk_score(self, critical: int, high: int, compliance_rate: float) -> float:
        """Calculate overall risk score (0-100, lower is better)."""
        base_score = 100 - compliance_rate
        critical_penalty = critical * 15
        high_penalty = high * 8

        return min(100, base_score + critical_penalty + high_penalty)

    def get_framework_status(self, framework: str) -> Dict[str, Any]:
        """Get status for a specific framework."""
        regulations = [r for r in self.regulations.values() if r.framework == framework]

        if not regulations:
            return {'error': f'No regulations found for framework: {framework}'}

        reg_ids = [r.regulation_id for r in regulations]
        controls = [c for c in self.controls.values() if c.regulation_id in reg_ids]

        total = len(controls)
        passed = len([c for c in controls if c.status == ComplianceStatus.COMPLIANT])

        return {
            'framework': framework,
            'regulations_count': len(regulations),
            'controls_total': total,
            'controls_passed': passed,
            'compliance_rate': round(passed / total * 100, 1) if total > 0 else 0,
            'template': self.framework_templates.get(framework, {}),
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
            'regulations_count': len(self.regulations),
            'controls_count': len(self.controls),
            'audits_count': len(self.audits),
            'policies_count': len(self.policies),
            'open_findings': len([f for f in self.findings.values() if f.status != 'resolved']),
        }


def get_capabilities() -> Dict[str, Any]:
    """Return agent capabilities for orchestration."""
    return {
        'agent_type': 'compliance',
        'version': '1.0.0',
        'capabilities': [
            'add_regulation',
            'update_regulation_status',
            'get_regulations',
            'create_control',
            'test_control',
            'get_controls',
            'create_audit',
            'start_audit',
            'complete_audit',
            'get_audits',
            'create_policy',
            'approve_policy',
            'get_policies',
            'get_policies_due_for_review',
            'create_finding',
            'resolve_finding',
            'get_findings',
            'get_compliance_report',
            'get_framework_status',
        ],
        'compliance_statuses': [s.value for s in ComplianceStatus],
        'risk_levels': [l.value for l in RiskLevel],
        'audit_statuses': [s.value for s in AuditStatus],
        'control_types': [t.value for t in ControlType],
        'framework_templates': list(ComplianceAgent(None).framework_templates.keys()),
    }


if __name__ == "__main__":
    agent = ComplianceAgent()

    # Add regulation
    reg = agent.add_regulation(
        name="SOC 2 Type II",
        framework="SOC2",
        jurisdiction="USA",
        owner="compliance@example.com",
        next_assessment=datetime.utcnow() + timedelta(days=180),
    )

    print(f"Added regulation: {reg.name}")

    # Create controls
    ctrl1 = agent.create_control(
        name="Access Control Policy",
        description="Ensure proper access controls are in place",
        control_type=ControlType.ADMINISTRATIVE,
        regulation_id=reg.regulation_id,
        risk_level=RiskLevel.HIGH,
    )

    ctrl2 = agent.create_control(
        name="Encryption at Rest",
        description="All data must be encrypted at rest",
        control_type=ControlType.TECHNICAL,
        regulation_id=reg.regulation_id,
    )

    print(f"Created {len(agent.controls)} controls")

    # Test control
    agent.test_control(ctrl1.control_id, passed=True, evidence_locations=["/docs/access-policy.pdf"])

    # Create audit
    audit = agent.create_audit(
        name="SOC 2 Annual Audit",
        audit_type="external",
        regulation_id=reg.regulation_id,
        start_date=datetime.utcnow(),
        auditor="External Auditor LLC",
    )

    print(f"Created audit: {audit.name}")

    # Create policy
    policy = agent.create_policy(
        title="Information Security Policy",
        category="security",
        version="1.0",
        owner="ciso@example.com",
        review_date=datetime.utcnow() + timedelta(days=365),
    )

    print(f"Created policy: {policy.title}")

    # Create finding
    finding = agent.create_finding(
        title="Missing MFA for admin accounts",
        description="Some admin accounts do not have MFA enabled",
        severity=RiskLevel.HIGH,
        regulation_id=reg.regulation_id,
        assigned_to="security@example.com",
        due_date=datetime.utcnow() + timedelta(days=30),
    )

    print(f"Created finding: {finding.title}")

    # Get compliance report
    report = agent.get_compliance_report()
    print(f"\nCompliance Rate: {report['summary']['compliance_rate']}%")
    print(f"Risk Score: {report['risk_score']}")

    print(f"\nState: {agent.get_state()}")
