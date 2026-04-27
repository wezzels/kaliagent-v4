"""
AuditAgent - Internal Audit & Control Testing
==============================================

Provides audit planning, control testing, evidence collection,
finding management, and audit reporting for internal audits.
"""

import logging
import secrets
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from typing import Any, Dict, List, Optional


logger = logging.getLogger(__name__)


class AuditType(Enum):
    """Audit types."""
    INTERNAL = "internal"
    EXTERNAL = "external"
    COMPLIANCE = "compliance"
    IT_GENERAL = "it_general"
    IT_APPLICATION = "it_application"
    OPERATIONAL = "operational"
    FINANCIAL = "financial"
    INVESTIGATIVE = "investigative"


class AuditStatus(Enum):
    """Audit status."""
    PLANNED = "planned"
    IN_PROGRESS = "in_progress"
    FIELDWORK_COMPLETE = "fieldwork_complete"
    REVIEW = "review"
    REPORTING = "reporting"
    COMPLETE = "complete"
    ON_HOLD = "on_hold"


class ControlType(Enum):
    """Control types."""
    PREVENTIVE = "preventive"
    DETECTIVE = "detective"
    CORRECTIVE = "corrective"
    DIRECTIVE = "directive"
    COMPENSATING = "compensating"


class ControlStatus(Enum):
    """Control testing status."""
    NOT_TESTED = "not_tested"
    TESTING_IN_PROGRESS = "testing_in_progress"
    EFFECTIVE = "effective"
    INEFFECTIVE = "ineffective"
    PARTIALLY_EFFECTIVE = "partially_effective"


class FindingSeverity(Enum):
    """Finding severity."""
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    OBSERVATION = "observation"


class FindingStatus(Enum):
    """Finding status."""
    OPEN = "open"
    IN_PROGRESS = "in_progress"
    REMEDIATION_VERIFICATION = "remediation_verification"
    CLOSED = "closed"
    ACCEPTED = "accepted"


@dataclass
class Audit:
    """Audit engagement."""
    audit_id: str
    title: str
    description: str
    audit_type: AuditType
    status: AuditStatus
    auditor: str
    auditee: str
    scope: str
    objectives: List[str] = field(default_factory=list)
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    planned_hours: float = 0.0
    actual_hours: float = 0.0
    findings_count: int = 0
    created_at: datetime = field(default_factory=datetime.utcnow)


@dataclass
class Control:
    """Internal control."""
    control_id: str
    audit_id: str
    name: str
    description: str
    control_type: ControlType
    control_owner: str
    frequency: str  # daily, weekly, monthly, quarterly, annually, continuous
    status: ControlStatus = ControlStatus.NOT_TESTED
    test_procedures: List[str] = field(default_factory=list)
    test_results: List[Dict[str, Any]] = field(default_factory=list)
    evidence: List[str] = field(default_factory=list)
    tested_at: Optional[datetime] = None
    tested_by: str = ""


@dataclass
class Finding:
    """Audit finding."""
    finding_id: str
    audit_id: str
    control_id: Optional[str]
    title: str
    description: str
    severity: FindingSeverity
    status: FindingStatus
    condition: str  # What was found
    criteria: str  # What was expected
    cause: str = ""
    effect: str = ""
    recommendation: str = ""
    management_response: str = ""
    action_plan: str = ""
    responsible_party: str = ""
    due_date: Optional[datetime] = None
    closed_at: Optional[datetime] = None
    created_at: datetime = field(default_factory=datetime.utcnow)


@dataclass
class Evidence:
    """Audit evidence."""
    evidence_id: str
    audit_id: str
    finding_id: Optional[str]
    control_id: Optional[str]
    title: str
    description: str
    evidence_type: str  # document, screenshot, log, interview, observation
    location: str  # file path, URL, etc.
    collected_by: str
    collected_at: datetime = field(default_factory=datetime.utcnow)
    reviewed: bool = False
    reviewed_by: str = ""


@dataclass
class AuditWorkpaper:
    """Audit workpaper."""
    workpaper_id: str
    audit_id: str
    title: str
    section: str
    content: str
    reviewer: str = ""
    reviewed: bool = False
    created_by: str = ""
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)


class AuditAgent:
    """
    Audit Agent for internal audit planning, control testing,
    evidence collection, and audit reporting.
    """

    def __init__(self, agent_id: str = "audit-agent"):
        self.agent_id = agent_id
        self.audits: Dict[str, Audit] = {}
        self.controls: Dict[str, Control] = {}
        self.findings: Dict[str, Finding] = {}
        self.evidence: Dict[str, Evidence] = {}
        self.workpapers: Dict[str, AuditWorkpaper] = {}

        # Audit templates
        self.templates = {
            'it_general': self._itgc_template(),
            'access_review': self._access_review_template(),
            'change_management': self._change_mgmt_template(),
        }

    # ============================================
    # Audit Planning
    # ============================================

    def create_audit(
        self,
        title: str,
        description: str,
        audit_type: AuditType,
        auditor: str,
        auditee: str,
        scope: str,
        objectives: Optional[List[str]] = None,
        planned_hours: float = 0.0,
    ) -> Audit:
        """Create audit engagement."""
        audit = Audit(
            audit_id=self._generate_id("audit"),
            title=title,
            description=description,
            audit_type=audit_type,
            status=AuditStatus.PLANNED,
            auditor=auditor,
            auditee=auditee,
            scope=scope,
            objectives=objectives or [],
            planned_hours=planned_hours,
        )

        self.audits[audit.audit_id] = audit
        return audit

    def start_audit(self, audit_id: str) -> bool:
        """Start audit fieldwork."""
        if audit_id not in self.audits:
            return False

        self.audits[audit_id].status = AuditStatus.IN_PROGRESS
        self.audits[audit_id].start_date = datetime.utcnow()
        return True

    def update_audit_status(
        self,
        audit_id: str,
        status: AuditStatus,
    ) -> bool:
        """Update audit status."""
        if audit_id not in self.audits:
            return False

        self.audits[audit_id].status = status

        if status == AuditStatus.COMPLETE:
            self.audits[audit_id].end_date = datetime.utcnow()

        return True

    def complete_audit(self, audit_id: str, actual_hours: float) -> bool:
        """Complete audit."""
        if audit_id not in self.audits:
            return False

        audit = self.audits[audit_id]
        audit.status = AuditStatus.COMPLETE
        audit.end_date = datetime.utcnow()
        audit.actual_hours = actual_hours

        return True

    def get_audits(
        self,
        audit_type: Optional[AuditType] = None,
        status: Optional[AuditStatus] = None,
    ) -> List[Audit]:
        """Get audits with filtering."""
        audits = list(self.audits.values())

        if audit_type:
            audits = [a for a in audits if a.audit_type == audit_type]

        if status:
            audits = [a for a in audits if a.status == status]

        return audits

    # ============================================
    # Control Testing
    # ============================================

    def add_control(
        self,
        audit_id: str,
        name: str,
        description: str,
        control_type: ControlType,
        control_owner: str,
        frequency: str,
        test_procedures: Optional[List[str]] = None,
    ) -> Control:
        """Add control for testing."""
        if audit_id not in self.audits:
            raise ValueError(f"Audit {audit_id} not found")

        control = Control(
            control_id=self._generate_id("ctrl"),
            audit_id=audit_id,
            name=name,
            description=description,
            control_type=control_type,
            control_owner=control_owner,
            frequency=frequency,
            test_procedures=test_procedures or [],
        )

        self.controls[control.control_id] = control
        return control

    def test_control(
        self,
        control_id: str,
        tested_by: str,
        test_results: List[Dict[str, Any]],
        evidence: Optional[List[str]] = None,
    ) -> bool:
        """Test control and record results."""
        if control_id not in self.controls:
            return False

        control = self.controls[control_id]
        control.tested_by = tested_by
        control.tested_at = datetime.utcnow()
        control.test_results = test_results
        control.evidence = evidence or []

        # Determine effectiveness
        passed = sum(1 for r in test_results if r.get('passed', False))
        total = len(test_results)

        if passed == total:
            control.status = ControlStatus.EFFECTIVE
        elif passed == 0:
            control.status = ControlStatus.INEFFECTIVE
        else:
            control.status = ControlStatus.PARTIALLY_EFFECTIVE

        return True

    def get_controls(
        self,
        audit_id: Optional[str] = None,
        control_type: Optional[ControlType] = None,
        status: Optional[ControlStatus] = None,
    ) -> List[Control]:
        """Get controls with filtering."""
        controls = list(self.controls.values())

        if audit_id:
            controls = [c for c in controls if c.audit_id == audit_id]

        if control_type:
            controls = [c for c in controls if c.control_type == control_type]

        if status:
            controls = [c for c in controls if c.status == status]

        return controls

    # ============================================
    # Finding Management
    # ============================================

    def create_finding(
        self,
        audit_id: str,
        title: str,
        description: str,
        severity: FindingSeverity,
        condition: str,
        criteria: str,
        control_id: Optional[str] = None,
        cause: str = "",
        effect: str = "",
    ) -> Finding:
        """Create audit finding."""
        if audit_id not in self.audits:
            raise ValueError(f"Audit {audit_id} not found")

        finding = Finding(
            finding_id=self._generate_id("find"),
            audit_id=audit_id,
            control_id=control_id,
            title=title,
            description=description,
            severity=severity,
            status=FindingStatus.OPEN,
            condition=condition,
            criteria=criteria,
            cause=cause,
            effect=effect,
        )

        self.findings[finding.finding_id] = finding
        self.audits[audit_id].findings_count += 1

        return finding

    def update_finding(
        self,
        finding_id: str,
        recommendation: str = "",
        management_response: str = "",
        action_plan: str = "",
        responsible_party: str = "",
        due_date: Optional[datetime] = None,
    ) -> bool:
        """Update finding details."""
        if finding_id not in self.findings:
            return False

        finding = self.findings[finding_id]

        if recommendation:
            finding.recommendation = recommendation
        if management_response:
            finding.management_response = management_response
        if action_plan:
            finding.action_plan = action_plan
        if responsible_party:
            finding.responsible_party = responsible_party
        if due_date:
            finding.due_date = due_date

        return True

    def update_finding_status(
        self,
        finding_id: str,
        status: FindingStatus,
    ) -> bool:
        """Update finding status."""
        if finding_id not in self.findings:
            return False

        finding = self.findings[finding_id]
        finding.status = status

        if status == FindingStatus.CLOSED:
            finding.closed_at = datetime.utcnow()

        return True

    def get_findings(
        self,
        audit_id: Optional[str] = None,
        severity: Optional[FindingSeverity] = None,
        status: Optional[FindingStatus] = None,
    ) -> List[Finding]:
        """Get findings with filtering."""
        findings = list(self.findings.values())

        if audit_id:
            findings = [f for f in findings if f.audit_id == audit_id]

        if severity:
            findings = [f for f in findings if f.severity == severity]

        if status:
            findings = [f for f in findings if f.status == status]

        return findings

    # ============================================
    # Evidence Collection
    # ============================================

    def collect_evidence(
        self,
        audit_id: str,
        title: str,
        description: str,
        evidence_type: str,
        location: str,
        collected_by: str,
        finding_id: Optional[str] = None,
        control_id: Optional[str] = None,
    ) -> Evidence:
        """Collect audit evidence."""
        if audit_id not in self.audits:
            raise ValueError(f"Audit {audit_id} not found")

        evidence = Evidence(
            evidence_id=self._generate_id("evid"),
            audit_id=audit_id,
            finding_id=finding_id,
            control_id=control_id,
            title=title,
            description=description,
            evidence_type=evidence_type,
            location=location,
            collected_by=collected_by,
        )

        self.evidence[evidence.evidence_id] = evidence
        return evidence

    def review_evidence(
        self,
        evidence_id: str,
        reviewed_by: str,
    ) -> bool:
        """Mark evidence as reviewed."""
        if evidence_id not in self.evidence:
            return False

        self.evidence[evidence_id].reviewed = True
        self.evidence[evidence_id].reviewed_by = reviewed_by

        return True

    def get_evidence(
        self,
        audit_id: Optional[str] = None,
        evidence_type: Optional[str] = None,
        reviewed: Optional[bool] = None,
    ) -> List[Evidence]:
        """Get evidence with filtering."""
        evidence = list(self.evidence.values())

        if audit_id:
            evidence = [e for e in evidence if e.audit_id == audit_id]

        if evidence_type:
            evidence = [e for e in evidence if e.evidence_type == evidence_type]

        if reviewed is not None:
            evidence = [e for e in evidence if e.reviewed == reviewed]

        return evidence

    # ============================================
    # Workpapers
    # ============================================

    def create_workpaper(
        self,
        audit_id: str,
        title: str,
        section: str,
        content: str,
        created_by: str,
    ) -> AuditWorkpaper:
        """Create audit workpaper."""
        if audit_id not in self.audits:
            raise ValueError(f"Audit {audit_id} not found")

        workpaper = AuditWorkpaper(
            workpaper_id=self._generate_id("wp"),
            audit_id=audit_id,
            title=title,
            section=section,
            content=content,
            created_by=created_by,
        )

        self.workpapers[workpaper.workpaper_id] = workpaper
        return workpaper

    def review_workpaper(
        self,
        workpaper_id: str,
        reviewer: str,
    ) -> bool:
        """Review workpaper."""
        if workpaper_id not in self.workpapers:
            return False

        self.workpapers[workpaper_id].reviewed = True
        self.workpapers[workpaper_id].reviewer = reviewer

        return True

    # ============================================
    # Reporting
    # ============================================

    def generate_audit_report(self, audit_id: str) -> Dict[str, Any]:
        """Generate audit report."""
        if audit_id not in self.audits:
            return {'error': 'Audit not found'}

        audit = self.audits[audit_id]
        controls = self.get_controls(audit_id=audit_id)
        findings = self.get_findings(audit_id=audit_id)
        evidence = self.get_evidence(audit_id=audit_id)

        # Control effectiveness
        effective = len([c for c in controls if c.status == ControlStatus.EFFECTIVE])
        ineffective = len([c for c in controls if c.status == ControlStatus.INEFFECTIVE])
        partial = len([c for c in controls if c.status == ControlStatus.PARTIALLY_EFFECTIVE])

        # Findings by severity
        by_severity = {}
        for sev in FindingSeverity:
            by_severity[sev.value] = len([f for f in findings if f.severity == sev])

        # Open findings
        open_findings = len([f for f in findings if f.status != FindingStatus.CLOSED])

        return {
            'audit': {
                'audit_id': audit_id,
                'title': audit.title,
                'type': audit.audit_type.value,
                'status': audit.status.value,
                'auditor': audit.auditor,
                'auditee': audit.auditee,
                'scope': audit.scope,
                'period': {
                    'start': audit.start_date.isoformat() if audit.start_date else None,
                    'end': audit.end_date.isoformat() if audit.end_date else None,
                },
                'hours': {
                    'planned': audit.planned_hours,
                    'actual': audit.actual_hours,
                },
            },
            'controls': {
                'total': len(controls),
                'effective': effective,
                'ineffective': ineffective,
                'partially_effective': partial,
                'effectiveness_rate': (effective / len(controls) * 100) if controls else 0,
            },
            'findings': {
                'total': len(findings),
                'by_severity': by_severity,
                'open': open_findings,
                'closed': len(findings) - open_findings,
            },
            'evidence': {
                'total': len(evidence),
                'reviewed': len([e for e in evidence if e.reviewed]),
            },
        }

    def get_audit_dashboard(self) -> Dict[str, Any]:
        """Generate audit dashboard."""
        audits = list(self.audits.values())
        findings = list(self.findings.values())

        # Audits by status
        by_status = {}
        for status in AuditStatus:
            by_status[status.value] = len([a for a in audits if a.status == status])

        # Findings by severity
        by_severity = {}
        for sev in FindingSeverity:
            by_severity[sev.value] = len([f for f in findings if f.severity == sev])

        # Overdue findings
        now = datetime.utcnow()
        overdue = len([
            f for f in findings
            if f.due_date and f.due_date < now and f.status != FindingStatus.CLOSED
        ])

        return {
            'audits': {
                'total': len(audits),
                'by_status': by_status,
                'in_progress': by_status.get('in_progress', 0),
            },
            'findings': {
                'total': len(findings),
                'by_severity': by_severity,
                'open': len([f for f in findings if f.status != FindingStatus.CLOSED]),
                'overdue': overdue,
            },
            'controls': {
                'total': len(self.controls),
                'effective': len([c for c in self.controls.values() if c.status == ControlStatus.EFFECTIVE]),
                'tested': len([c for c in self.controls.values() if c.status != ControlStatus.NOT_TESTED]),
            },
        }

    # ============================================
    # Templates
    # ============================================

    def _itgc_template(self) -> Dict[str, Any]:
        """IT General Controls template."""
        return {
            'name': 'IT General Controls',
            'domains': [
                'Access Control',
                'Change Management',
                'IT Operations',
                'Backup & Recovery',
            ],
        }

    def _access_review_template(self) -> Dict[str, Any]:
        """Access Review template."""
        return {
            'name': 'Access Review',
            'focus_areas': [
                'User provisioning',
                'Privileged access',
                'Termination process',
                'Segregation of duties',
            ],
        }

    def _change_mgmt_template(self) -> Dict[str, Any]:
        """Change Management template."""
        return {
            'name': 'Change Management',
            'focus_areas': [
                'Change approval',
                'Testing requirements',
                'Emergency changes',
                'Rollback procedures',
            ],
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
            'audits_count': len(self.audits),
            'in_progress_audits': len([a for a in self.audits.values() if a.status == AuditStatus.IN_PROGRESS]),
            'controls_count': len(self.controls),
            'effective_controls': len([c for c in self.controls.values() if c.status == ControlStatus.EFFECTIVE]),
            'findings_count': len(self.findings),
            'open_findings': len([f for f in self.findings.values() if f.status != FindingStatus.CLOSED]),
            'evidence_count': len(self.evidence),
            'workpapers_count': len(self.workpapers),
        }


def get_capabilities() -> Dict[str, Any]:
    """Return agent capabilities for orchestration."""
    return {
        'agent_type': 'audit',
        'version': '1.0.0',
        'capabilities': [
            'create_audit',
            'start_audit',
            'update_audit_status',
            'complete_audit',
            'get_audits',
            'add_control',
            'test_control',
            'get_controls',
            'create_finding',
            'update_finding',
            'update_finding_status',
            'get_findings',
            'collect_evidence',
            'review_evidence',
            'get_evidence',
            'create_workpaper',
            'review_workpaper',
            'generate_audit_report',
            'get_audit_dashboard',
        ],
        'audit_types': [t.value for t in AuditType],
        'audit_statuses': [s.value for s in AuditStatus],
        'control_types': [t.value for t in ControlType],
        'control_statuses': [s.value for s in ControlStatus],
        'finding_severities': [s.value for s in FindingSeverity],
        'finding_statuses': [s.value for s in FindingStatus],
    }


if __name__ == "__main__":
    agent = AuditAgent()

    # Create audit
    audit = agent.create_audit(
        title="IT General Controls Audit 2026",
        description="Annual ITGC audit",
        audit_type=AuditType.IT_GENERAL,
        auditor="lead-auditor@example.com",
        auditee="IT Department",
        scope="Access control, change management, IT operations",
        objectives=[
            "Assess access control effectiveness",
            "Evaluate change management process",
            "Review IT operations procedures",
        ],
        planned_hours=120.0,
    )

    print(f"Created audit: {audit.title}")

    # Start audit
    agent.start_audit(audit.audit_id)

    # Add controls
    ctrl1 = agent.add_control(
        audit.audit_id,
        "User Access Review",
        "Quarterly user access reviews",
        ControlType.PREVENTIVE,
        "it-manager@example.com",
        "quarterly",
        test_procedures=[
            "Select sample of 25 users",
            "Verify access rights match job roles",
            "Check for terminated users with active access",
        ],
    )

    ctrl2 = agent.add_control(
        audit.audit_id,
        "Change Approval",
        "All changes require approval",
        ControlType.PREVENTIVE,
        "change-manager@example.com",
        "continuous",
        test_procedures=[
            "Select sample of 20 changes",
            "Verify approval before implementation",
            "Check emergency change process",
        ],
    )

    # Test controls
    agent.test_control(
        ctrl1.control_id,
        tested_by="auditor@example.com",
        test_results=[
            {'procedure': 'Sample selection', 'passed': True},
            {'procedure': 'Access verification', 'passed': True},
            {'procedure': 'Termination check', 'passed': False, 'note': '2 users found'},
        ],
    )

    agent.test_control(
        ctrl2.control_id,
        tested_by="auditor@example.com",
        test_results=[
            {'procedure': 'Sample selection', 'passed': True},
            {'procedure': 'Approval verification', 'passed': True},
            {'procedure': 'Emergency changes', 'passed': True},
        ],
    )

    # Create finding
    finding = agent.create_finding(
        audit.audit_id,
        title="Terminated Users with Active Access",
        description="2 terminated users still have active system access",
        severity=FindingSeverity.HIGH,
        condition="2 terminated employees have active access",
        criteria="All terminated users should have access revoked within 24 hours",
        control_id=ctrl1.control_id,
        cause="HR termination process not integrated with IT systems",
        effect="Unauthorized access risk",
    )

    # Update finding
    agent.update_finding(
        finding.finding_id,
        recommendation="Automate access revocation via HR-IT integration",
        management_response="Will implement automated workflow",
        action_plan="Deploy HR-IT integration by Q2",
        responsible_party="it-director@example.com",
        due_date=datetime.utcnow() + timedelta(days=90),
    )

    # Collect evidence
    agent.collect_evidence(
        audit.audit_id,
        title="Access Review Documentation",
        description="Q4 2025 access review sign-offs",
        evidence_type="document",
        location="/evidence/access-review-q4-2025.pdf",
        collected_by="auditor@example.com",
        control_id=ctrl1.control_id,
    )

    # Generate report
    report = agent.generate_audit_report(audit.audit_id)
    print(f"\nAudit Report:")
    print(f"  Controls: {report['controls']['total']}")
    print(f"  Effectiveness: {report['controls']['effectiveness_rate']:.1f}%")
    print(f"  Findings: {report['findings']['total']}")

    # Get dashboard
    dashboard = agent.get_audit_dashboard()
    print(f"\nAudit Dashboard:")
    print(f"  Total Audits: {dashboard['audits']['total']}")
    print(f"  In Progress: {dashboard['audits']['in_progress']}")
    print(f"  Open Findings: {dashboard['findings']['open']}")

    print(f"\nState: {agent.get_state()}")
