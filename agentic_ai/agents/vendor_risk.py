"""
VendorRiskAgent - Third-Party Risk Management
==============================================

Provides vendor risk assessments, SIG questionnaires, continuous
monitoring, risk scoring, and third-party risk management workflows.
"""

import logging
import secrets
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from typing import Any, Dict, List, Optional


logger = logging.getLogger(__name__)


class VendorTier(Enum):
    """Vendor criticality tiers."""
    TIER_1 = "tier_1"  # Critical - core business function
    TIER_2 = "tier_2"  # High - important business function
    TIER_3 = "tier_3"  # Medium - supporting function
    TIER_4 = "tier_4"  # Low - minimal impact


class RiskDomain(Enum):
    """Risk assessment domains."""
    INFORMATION_SECURITY = "information_security"
    PRIVACY = "privacy"
    BUSINESS_CONTINUITY = "business_continuity"
    COMPLIANCE = "compliance"
    FINANCIAL = "financial"
    OPERATIONAL = "operational"
    REPUTATIONAL = "reputational"
    STRATEGIC = "strategic"


class AssessmentType(Enum):
    """Assessment types."""
    INITIAL = "initial"
    ANNUAL = "annual"
    EVENT_DRIVEN = "event_driven"
    INCIDENT_TRIGGERED = "incident_triggered"
    CONTRACT_RENEWAL = "contract_renewal"


class QuestionnaireType(Enum):
    """Questionnaire types."""
    SIG_LITE = "sig_lite"
    SIG_CORE = "sig_core"
    SIG_FULL = "sig_full"
    CAIQ = "caiq"
    CUSTOM = "custom"


class ControlMaturity(Enum):
    """Control maturity levels."""
    NON_EXISTENT = "non_existent"
    INITIAL = "initial"
    REPEATABLE = "repeatable"
    DEFINED = "defined"
    MANAGED = "managed"
    OPTIMIZED = "optimized"


class ResidualRisk(Enum):
    """Residual risk levels."""
    EXTREME = "extreme"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    MINIMAL = "minimal"


@dataclass
class Vendor:
    """Third-party vendor."""
    vendor_id: str
    name: str
    legal_name: str
    tier: VendorTier
    category: str  # cloud, software, hardware, service, etc.
    relationship_type: str  # vendor, partner, supplier, contractor
    contract_start: datetime
    contract_end: Optional[datetime]
    contract_value: float = 0.0
    primary_contact: str = ""
    security_contact: str = ""
    risk_owner: str = ""
    inherent_risk: float = 0.0
    residual_risk: float = 0.0
    last_assessment: Optional[datetime] = None
    next_assessment: Optional[datetime] = None
    status: str = "active"  # active, under_review, suspended, terminated


@dataclass
class Questionnaire:
    """Risk assessment questionnaire."""
    questionnaire_id: str
    vendor_id: str
    questionnaire_type: QuestionnaireType
    version: str
    status: str  # draft, sent, in_progress, completed, reviewed
    total_questions: int = 0
    answered_questions: int = 0
    created_at: datetime = field(default_factory=datetime.utcnow)
    sent_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    reviewed_at: Optional[datetime] = None


@dataclass
class Question:
    """Questionnaire question."""
    question_id: str
    questionnaire_id: str
    domain: RiskDomain
    question_text: str
    control_objective: str
    response_type: str  # yes_no, multiple_choice, text, evidence_required
    weight: float = 1.0
    response_options: List[str] = field(default_factory=list)
    response: Optional[str] = None
    evidence_provided: bool = False
    notes: str = ""
    score: float = 0.0


@dataclass
class Finding:
    """Risk assessment finding."""
    finding_id: str
    vendor_id: str
    assessment_id: str
    domain: RiskDomain
    title: str
    description: str
    severity: str  # critical, high, medium, low
    inherent_risk: float
    control_effectiveness: float
    residual_risk: float
    recommendation: str = ""
    management_response: str = ""
    remediation_plan: str = ""
    due_date: Optional[datetime] = None
    status: str = "open"  # open, in_progress, remediated, accepted, closed
    created_at: datetime = field(default_factory=datetime.utcnow)


@dataclass
class Assessment:
    """Vendor risk assessment."""
    assessment_id: str
    vendor_id: str
    assessment_type: AssessmentType
    assessor: str
    status: str  # planned, in_progress, completed, reviewed
    inherent_risk_score: float = 0.0
    control_effectiveness: float = 0.0
    residual_risk_score: float = 0.0
    residual_risk_level: ResidualRisk = ResidualRisk.MEDIUM
    questionnaire_id: Optional[str] = None
    findings_count: int = 0
    critical_findings: int = 0
    recommendations: List[str] = field(default_factory=list)
    overall_opinion: str = ""
    created_at: datetime = field(default_factory=datetime.utcnow)
    completed_at: Optional[datetime] = None
    reviewed_at: Optional[datetime] = None


@dataclass
class ContinuousMonitor:
    """Continuous vendor monitoring."""
    monitor_id: str
    vendor_id: str
    enabled: bool = True
    monitoring_types: List[str] = field(default_factory=list)  # security_ratings, news, breaches, financial
    check_frequency: str = "daily"
    last_check: Optional[datetime] = None
    alerts: List[str] = field(default_factory=list)
    risk_trend: str = "stable"  # improving, stable, deteriorating


@dataclass
class Alert:
    """Vendor risk alert."""
    alert_id: str
    vendor_id: str
    alert_type: str  # security_rating_change, breach, news, contract_expiry, assessment_due
    severity: str
    title: str
    description: str
    source: str
    status: str = "new"  # new, acknowledged, investigating, resolved
    created_at: datetime = field(default_factory=datetime.utcnow)
    acknowledged_at: Optional[datetime] = None
    resolved_at: Optional[datetime] = None


class VendorRiskAgent:
    """
    Vendor Risk Agent for third-party risk management,
    assessments, SIG questionnaires, and continuous monitoring.
    """

    def __init__(self, agent_id: str = "vendor-risk-agent"):
        self.agent_id = agent_id
        self.vendors: Dict[str, Vendor] = {}
        self.questionnaires: Dict[str, Questionnaire] = {}
        self.questions: Dict[str, Question] = {}
        self.findings: Dict[str, Finding] = {}
        self.assessments: Dict[str, Assessment] = {}
        self.monitors: Dict[str, ContinuousMonitor] = {}
        self.alerts: Dict[str, Alert] = {}

        # SIG questionnaires
        self.sig_questions = self._load_sig_questions()

        # Risk weights by domain
        self.domain_weights = {
            RiskDomain.INFORMATION_SECURITY: 0.30,
            RiskDomain.PRIVACY: 0.20,
            RiskDomain.BUSINESS_CONTINUITY: 0.15,
            RiskDomain.COMPLIANCE: 0.15,
            RiskDomain.FINANCIAL: 0.10,
            RiskDomain.OPERATIONAL: 0.05,
            RiskDomain.REPUTATIONAL: 0.03,
            RiskDomain.STRATEGIC: 0.02,
        }

    # ============================================
    # Vendor Management
    # ============================================

    def add_vendor(
        self,
        name: str,
        legal_name: str,
        tier: VendorTier,
        category: str,
        relationship_type: str,
        contract_start: datetime,
        contract_end: Optional[datetime] = None,
        contract_value: float = 0.0,
        primary_contact: str = "",
        security_contact: str = "",
        risk_owner: str = "",
    ) -> Vendor:
        """Add vendor to registry."""
        vendor = Vendor(
            vendor_id=self._generate_id("vendor"),
            name=name,
            legal_name=legal_name,
            tier=tier,
            category=category,
            relationship_type=relationship_type,
            contract_start=contract_start,
            contract_end=contract_end,
            contract_value=contract_value,
            primary_contact=primary_contact,
            security_contact=security_contact,
            risk_owner=risk_owner,
        )

        # Calculate inherent risk based on tier
        tier_risk = {
            VendorTier.TIER_1: 0.9,
            VendorTier.TIER_2: 0.7,
            VendorTier.TIER_3: 0.5,
            VendorTier.TIER_4: 0.3,
        }
        vendor.inherent_risk = tier_risk.get(tier, 0.5)

        self.vendors[vendor.vendor_id] = vendor
        return vendor

    def update_vendor_risk(
        self,
        vendor_id: str,
        residual_risk: float,
    ) -> bool:
        """Update vendor residual risk."""
        if vendor_id not in self.vendors:
            return False

        self.vendors[vendor_id].residual_risk = residual_risk
        return True

    def get_vendors(
        self,
        tier: Optional[VendorTier] = None,
        status: Optional[str] = None,
        category: Optional[str] = None,
    ) -> List[Vendor]:
        """Get vendors with filtering."""
        vendors = list(self.vendors.values())

        if tier:
            vendors = [v for v in vendors if v.tier == tier]

        if status:
            vendors = [v for v in vendors if v.status == status]

        if category:
            vendors = [v for v in vendors if v.category == category]

        return vendors

    def get_vendors_due_for_assessment(self, days: int = 30) -> List[Vendor]:
        """Get vendors due for assessment within specified days."""
        now = datetime.utcnow()
        threshold = now + timedelta(days=days)

        return [
            v for v in self.vendors.values()
            if v.next_assessment and v.next_assessment <= threshold
        ]

    # ============================================
    # Questionnaire Management
    # ============================================

    def create_questionnaire(
        self,
        vendor_id: str,
        questionnaire_type: QuestionnaireType,
        version: str = "1.0",
    ) -> Questionnaire:
        """Create vendor questionnaire."""
        if vendor_id not in self.vendors:
            raise ValueError(f"Vendor {vendor_id} not found")

        questionnaire = Questionnaire(
            questionnaire_id=self._generate_id("quest"),
            vendor_id=vendor_id,
            questionnaire_type=questionnaire_type,
            version=version,
            status="draft",
        )

        # Populate questions based on type
        self._populate_questions(questionnaire)

        self.questionnaires[questionnaire.questionnaire_id] = questionnaire
        return questionnaire

    def _populate_questions(self, questionnaire: Questionnaire) -> None:
        """Populate questionnaire with questions."""
        question_count = {
            QuestionnaireType.SIG_LITE: 50,
            QuestionnaireType.SIG_CORE: 150,
            QuestionnaireType.SIG_FULL: 300,
            QuestionnaireType.CAIQ: 200,
        }

        count = question_count.get(questionnaire.questionnaire_type, 100)
        questionnaire.total_questions = count

        # Create sample questions across domains
        domains = list(RiskDomain)
        questions_per_domain = count // len(domains)

        for domain in domains:
            for i in range(questions_per_domain):
                question = Question(
                    question_id=self._generate_id("q"),
                    questionnaire_id=questionnaire.questionnaire_id,
                    domain=domain,
                    question_text=f"Sample {domain.value} question {i+1}",
                    control_objective=f"Ensure {domain.value} controls",
                    response_type="yes_no",
                    response_options=["Yes", "No", "Partial", "N/A"],
                )
                self.questions[question.question_id] = question

    def send_questionnaire(self, questionnaire_id: str) -> bool:
        """Send questionnaire to vendor."""
        if questionnaire_id not in self.questionnaires:
            return False

        self.questionnaires[questionnaire_id].status = "sent"
        self.questionnaires[questionnaire_id].sent_at = datetime.utcnow()
        return True

    def respond_to_question(
        self,
        question_id: str,
        response: str,
        evidence_provided: bool = False,
        notes: str = "",
    ) -> bool:
        """Record question response."""
        if question_id not in self.questions:
            return False

        question = self.questions[question_id]
        question.response = response
        question.evidence_provided = evidence_provided
        question.notes = notes

        # Score response
        if response.lower() in ["yes", "fully implemented"]:
            question.score = 1.0
        elif response.lower() in ["partial", "partially implemented"]:
            question.score = 0.5
        else:
            question.score = 0.0

        # Update questionnaire progress
        questionnaire = self.questionnaires.get(question.questionnaire_id)
        if questionnaire:
            answered = len([
                q for q in self.questions.values()
                if q.questionnaire_id == questionnaire.questionnaire_id and q.response
            ])
            questionnaire.answered_questions = answered

            if answered == questionnaire.total_questions:
                questionnaire.status = "completed"
                questionnaire.completed_at = datetime.utcnow()

        return True

    def get_questionnaires(
        self,
        vendor_id: Optional[str] = None,
        status: Optional[str] = None,
        questionnaire_type: Optional[QuestionnaireType] = None,
    ) -> List[Questionnaire]:
        """Get questionnaires with filtering."""
        questionnaires = list(self.questionnaires.values())

        if vendor_id:
            questionnaires = [q for q in questionnaires if q.vendor_id == vendor_id]

        if status:
            questionnaires = [q for q in questionnaires if q.status == status]

        if questionnaire_type:
            questionnaires = [q for q in questionnaires if q.questionnaire_type == questionnaire_type]

        return questionnaires

    # ============================================
    # Assessment
    # ============================================

    def create_assessment(
        self,
        vendor_id: str,
        assessment_type: AssessmentType,
        assessor: str,
        questionnaire_id: Optional[str] = None,
    ) -> Assessment:
        """Create vendor risk assessment."""
        if vendor_id not in self.vendors:
            raise ValueError(f"Vendor {vendor_id} not found")

        assessment = Assessment(
            assessment_id=self._generate_id("assess"),
            vendor_id=vendor_id,
            assessment_type=assessment_type,
            assessor=assessor,
            status="planned",
            questionnaire_id=questionnaire_id,
        )

        self.assessments[assessment.assessment_id] = assessment
        return assessment

    def start_assessment(self, assessment_id: str) -> bool:
        """Start assessment."""
        if assessment_id not in self.assessments:
            return False

        self.assessments[assessment_id].status = "in_progress"
        return True

    def complete_assessment(
        self,
        assessment_id: str,
        inherent_risk_score: float,
        control_effectiveness: float,
        residual_risk_score: float,
        findings: Optional[List[Dict[str, Any]]] = None,
        recommendations: Optional[List[str]] = None,
        overall_opinion: str = "",
    ) -> bool:
        """Complete assessment."""
        if assessment_id not in self.assessments:
            return False

        assessment = self.assessments[assessment_id]
        assessment.status = "completed"
        assessment.completed_at = datetime.utcnow()
        assessment.inherent_risk_score = inherent_risk_score
        assessment.control_effectiveness = control_effectiveness
        assessment.residual_risk_score = residual_risk_score

        # Determine risk level
        if residual_risk_score >= 0.8:
            assessment.residual_risk_level = ResidualRisk.EXTREME
        elif residual_risk_score >= 0.6:
            assessment.residual_risk_level = ResidualRisk.HIGH
        elif residual_risk_score >= 0.4:
            assessment.residual_risk_level = ResidualRisk.MEDIUM
        elif residual_risk_score >= 0.2:
            assessment.residual_risk_level = ResidualRisk.LOW
        else:
            assessment.residual_risk_level = ResidualRisk.MINIMAL

        assessment.recommendations = recommendations or []
        assessment.overall_opinion = overall_opinion

        # Update vendor
        vendor = self.vendors[assessment.vendor_id]
        vendor.residual_risk = residual_risk_score
        vendor.last_assessment = datetime.utcnow()
        vendor.next_assessment = datetime.utcnow() + timedelta(days=365)

        # Create findings
        if findings:
            for f in findings:
                self.create_finding(
                    assessment_id,
                    f['domain'],
                    f['title'],
                    f['description'],
                    f['severity'],
                    f.get('inherent_risk', 0.5),
                    f.get('control_effectiveness', 0.5),
                    f.get('residual_risk', 0.3),
                )

        return True

    def get_assessments(
        self,
        vendor_id: Optional[str] = None,
        status: Optional[str] = None,
        assessment_type: Optional[AssessmentType] = None,
    ) -> List[Assessment]:
        """Get assessments with filtering."""
        assessments = list(self.assessments.values())

        if vendor_id:
            assessments = [a for a in assessments if a.vendor_id == vendor_id]

        if status:
            assessments = [a for a in assessments if a.status == status]

        if assessment_type:
            assessments = [a for a in assessments if a.assessment_type == assessment_type]

        return assessments

    # ============================================
    # Finding Management
    # ============================================

    def create_finding(
        self,
        assessment_id: str,
        domain: RiskDomain,
        title: str,
        description: str,
        severity: str,
        inherent_risk: float,
        control_effectiveness: float,
        residual_risk: float,
    ) -> Finding:
        """Create assessment finding."""
        if assessment_id not in self.assessments:
            raise ValueError(f"Assessment {assessment_id} not found")

        assessment = self.assessments[assessment_id]

        finding = Finding(
            finding_id=self._generate_id("finding"),
            vendor_id=assessment.vendor_id,
            assessment_id=assessment_id,
            domain=domain,
            title=title,
            description=description,
            severity=severity,
            inherent_risk=inherent_risk,
            control_effectiveness=control_effectiveness,
            residual_risk=residual_risk,
        )

        self.findings[finding.finding_id] = finding
        assessment.findings_count += 1

        if severity == "critical":
            assessment.critical_findings += 1

        return finding

    def update_finding(
        self,
        finding_id: str,
        recommendation: str = "",
        management_response: str = "",
        remediation_plan: str = "",
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
        if remediation_plan:
            finding.remediation_plan = remediation_plan
        if due_date:
            finding.due_date = due_date

        return True

    def update_finding_status(
        self,
        finding_id: str,
        status: str,
    ) -> bool:
        """Update finding status."""
        if finding_id not in self.findings:
            return False

        self.findings[finding_id].status = status

        if status == "closed":
            self.findings[finding_id].closed_at = datetime.utcnow()

        return True

    def get_findings(
        self,
        vendor_id: Optional[str] = None,
        severity: Optional[str] = None,
        status: Optional[str] = None,
    ) -> List[Finding]:
        """Get findings with filtering."""
        findings = list(self.findings.values())

        if vendor_id:
            findings = [f for f in findings if f.vendor_id == vendor_id]

        if severity:
            findings = [f for f in findings if f.severity == severity]

        if status:
            findings = [f for f in findings if f.status == status]

        return findings

    # ============================================
    # Continuous Monitoring
    # ============================================

    def enable_monitoring(
        self,
        vendor_id: str,
        monitoring_types: List[str],
        check_frequency: str = "daily",
    ) -> ContinuousMonitor:
        """Enable continuous monitoring for vendor."""
        if vendor_id not in self.vendors:
            raise ValueError(f"Vendor {vendor_id} not found")

        monitor = ContinuousMonitor(
            monitor_id=self._generate_id("monitor"),
            vendor_id=vendor_id,
            enabled=True,
            monitoring_types=monitoring_types,
            check_frequency=check_frequency,
        )

        self.monitors[monitor.monitor_id] = monitor
        return monitor

    def record_monitoring_result(
        self,
        monitor_id: str,
        risk_trend: str,
        alerts: Optional[List[str]] = None,
    ) -> bool:
        """Record monitoring check result."""
        if monitor_id not in self.monitors:
            return False

        monitor = self.monitors[monitor_id]
        monitor.last_check = datetime.utcnow()
        monitor.risk_trend = risk_trend
        monitor.alerts = alerts or []

        return True

    def get_monitors(
        self,
        enabled: Optional[bool] = None,
    ) -> List[ContinuousMonitor]:
        """Get monitors with filtering."""
        monitors = list(self.monitors.values())

        if enabled is not None:
            monitors = [m for m in monitors if m.enabled == enabled]

        return monitors

    # ============================================
    # Alert Management
    # ============================================

    def create_alert(
        self,
        vendor_id: str,
        alert_type: str,
        severity: str,
        title: str,
        description: str,
        source: str,
    ) -> Alert:
        """Create vendor risk alert."""
        alert = Alert(
            alert_id=self._generate_id("alert"),
            vendor_id=vendor_id,
            alert_type=alert_type,
            severity=severity,
            title=title,
            description=description,
            source=source,
        )

        self.alerts[alert.alert_id] = alert
        return alert

    def acknowledge_alert(self, alert_id: str) -> bool:
        """Acknowledge alert."""
        if alert_id not in self.alerts:
            return False

        self.alerts[alert_id].status = "acknowledged"
        self.alerts[alert_id].acknowledged_at = datetime.utcnow()
        return True

    def resolve_alert(self, alert_id: str) -> bool:
        """Resolve alert."""
        if alert_id not in self.alerts:
            return False

        self.alerts[alert_id].status = "resolved"
        self.alerts[alert_id].resolved_at = datetime.utcnow()
        return True

    def get_alerts(
        self,
        vendor_id: Optional[str] = None,
        severity: Optional[str] = None,
        status: Optional[str] = None,
    ) -> List[Alert]:
        """Get alerts with filtering."""
        alerts = list(self.alerts.values())

        if vendor_id:
            alerts = [a for a in alerts if a.vendor_id == vendor_id]

        if severity:
            alerts = [a for a in alerts if a.severity == severity]

        if status:
            alerts = [a for a in alerts if a.status == status]

        return alerts

    # ============================================
    # Reporting
    # ============================================

    def get_vendor_risk_report(self, vendor_id: str) -> Dict[str, Any]:
        """Generate vendor risk report."""
        if vendor_id not in self.vendors:
            return {'error': 'Vendor not found'}

        vendor = self.vendors[vendor_id]
        assessments = self.get_assessments(vendor_id=vendor_id)
        findings = self.get_findings(vendor_id=vendor_id)
        alerts = self.get_alerts(vendor_id=vendor_id)

        latest_assessment = assessments[-1] if assessments else None

        return {
            'vendor': {
                'vendor_id': vendor_id,
                'name': vendor.name,
                'tier': vendor.tier.value,
                'category': vendor.category,
                'status': vendor.status,
                'contract': {
                    'start': vendor.contract_start.isoformat(),
                    'end': vendor.contract_end.isoformat() if vendor.contract_end else None,
                    'value': vendor.contract_value,
                },
            },
            'risk': {
                'inherent': vendor.inherent_risk,
                'residual': vendor.residual_risk,
                'trend': 'stable',
            },
            'assessments': {
                'total': len(assessments),
                'latest': {
                    'date': latest_assessment.completed_at.isoformat() if latest_assessment and latest_assessment.completed_at else None,
                    'type': latest_assessment.assessment_type.value if latest_assessment else None,
                    'risk_level': latest_assessment.residual_risk_level.value if latest_assessment else None,
                } if latest_assessment else None,
            },
            'findings': {
                'total': len(findings),
                'open': len([f for f in findings if f.status != 'closed']),
                'by_severity': {
                    'critical': len([f for f in findings if f.severity == 'critical']),
                    'high': len([f for f in findings if f.severity == 'high']),
                    'medium': len([f for f in findings if f.severity == 'medium']),
                    'low': len([f for f in findings if f.severity == 'low']),
                },
            },
            'alerts': {
                'total': len(alerts),
                'new': len([a for a in alerts if a.status == 'new']),
            },
        }

    def get_vendor_risk_dashboard(self) -> Dict[str, Any]:
        """Generate vendor risk dashboard."""
        vendors = list(self.vendors.values())
        assessments = list(self.assessments.values())
        findings = list(self.findings.values())
        alerts = list(self.alerts.values())

        # Vendors by tier
        by_tier = {}
        for tier in VendorTier:
            by_tier[tier.value] = len([v for v in vendors if v.tier == tier])

        # Assessments due
        due_soon = len(self.get_vendors_due_for_assessment(30))

        # Findings by severity
        by_severity = {}
        for sev in ['critical', 'high', 'medium', 'low']:
            by_severity[sev] = len([f for f in findings if f.severity == sev])

        # Open findings
        open_findings = len([f for f in findings if f.status != 'closed'])

        return {
            'vendors': {
                'total': len(vendors),
                'by_tier': by_tier,
                'active': len([v for v in vendors if v.status == 'active']),
            },
            'assessments': {
                'total': len(assessments),
                'completed': len([a for a in assessments if a.status == 'completed']),
                'due_soon': due_soon,
            },
            'findings': {
                'total': len(findings),
                'open': open_findings,
                'by_severity': by_severity,
            },
            'alerts': {
                'total': len(alerts),
                'new': len([a for a in alerts if a.status == 'new']),
            },
            'monitoring': {
                'enabled': len([m for m in self.monitors.values() if m.enabled]),
            },
        }

    # ============================================
    # SIG Questions
    # ============================================

    def _load_sig_questions(self) -> Dict[str, Any]:
        """Load SIG questionnaire templates."""
        return {
            'sig_lite': {
                'name': 'SIG Lite',
                'questions': 50,
                'domains': ['info_sec', 'privacy', 'bc'],
            },
            'sig_core': {
                'name': 'SIG Core',
                'questions': 150,
                'domains': ['info_sec', 'privacy', 'bc', 'compliance', 'financial'],
            },
            'sig_full': {
                'name': 'SIG Full',
                'questions': 300,
                'domains': list(RiskDomain),
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
            'vendors_count': len(self.vendors),
            'by_tier': {
                tier.value: len([v for v in self.vendors.values() if v.tier == tier])
                for tier in VendorTier
            },
            'assessments_count': len(self.assessments),
            'questionnaires_count': len(self.questionnaires),
            'findings_count': len(self.findings),
            'open_findings': len([f for f in self.findings.values() if f.status != 'closed']),
            'monitors_count': len(self.monitors),
            'alerts_count': len(self.alerts),
            'new_alerts': len([a for a in self.alerts.values() if a.status == 'new']),
        }


def get_capabilities() -> Dict[str, Any]:
    """Return agent capabilities for orchestration."""
    return {
        'agent_type': 'vendor_risk',
        'version': '1.0.0',
        'capabilities': [
            'add_vendor',
            'update_vendor_risk',
            'get_vendors',
            'get_vendors_due_for_assessment',
            'create_questionnaire',
            'send_questionnaire',
            'respond_to_question',
            'get_questionnaires',
            'create_assessment',
            'start_assessment',
            'complete_assessment',
            'get_assessments',
            'create_finding',
            'update_finding',
            'update_finding_status',
            'get_findings',
            'enable_monitoring',
            'record_monitoring_result',
            'get_monitors',
            'create_alert',
            'acknowledge_alert',
            'resolve_alert',
            'get_alerts',
            'get_vendor_risk_report',
            'get_vendor_risk_dashboard',
        ],
        'vendor_tiers': [t.value for t in VendorTier],
        'risk_domains': [d.value for d in RiskDomain],
        'assessment_types': [t.value for t in AssessmentType],
        'questionnaire_types': [t.value for t in QuestionnaireType],
        'residual_risk_levels': [l.value for l in ResidualRisk],
    }


if __name__ == "__main__":
    agent = VendorRiskAgent()

    # Add vendors
    vendor1 = agent.add_vendor(
        name="CloudProvider Inc",
        legal_name="CloudProvider Incorporated",
        tier=VendorTier.TIER_1,
        category="cloud",
        relationship_type="vendor",
        contract_start=datetime.utcnow() - timedelta(days=365),
        contract_end=datetime.utcnow() + timedelta(days=365),
        contract_value=500000.0,
        primary_contact="contact@cloudprovider.com",
        security_contact="security@cloudprovider.com",
        risk_owner="cto@example.com",
    )

    vendor2 = agent.add_vendor(
        name="SaaS Vendor",
        legal_name="SaaS Vendor LLC",
        tier=VendorTier.TIER_2,
        category="software",
        relationship_type="vendor",
        contract_start=datetime.utcnow() - timedelta(days=180),
        contract_value=100000.0,
    )

    print(f"Added {len(agent.vendors)} vendors")

    # Create questionnaire
    questionnaire = agent.create_questionnaire(
        vendor1.vendor_id,
        QuestionnaireType.SIG_CORE,
    )

    print(f"Created questionnaire: {questionnaire.questionnaire_type.value}")

    # Send questionnaire
    agent.send_questionnaire(questionnaire.questionnaire_id)

    # Create assessment
    assessment = agent.create_assessment(
        vendor1.vendor_id,
        AssessmentType.ANNUAL,
        assessor="risk-team@example.com",
        questionnaire_id=questionnaire.questionnaire_id,
    )

    agent.start_assessment(assessment.assessment_id)

    # Complete assessment
    agent.complete_assessment(
        assessment.assessment_id,
        inherent_risk_score=0.8,
        control_effectiveness=0.7,
        residual_risk_score=0.4,
        findings=[
            {
                'domain': RiskDomain.INFORMATION_SECURITY,
                'title': 'MFA Not Enforced',
                'description': 'MFA not enforced for all users',
                'severity': 'high',
                'inherent_risk': 0.7,
                'control_effectiveness': 0.4,
                'residual_risk': 0.5,
            },
        ],
        recommendations=["Enforce MFA for all users"],
        overall_opinion="Acceptable with remediation",
    )

    print(f"Assessment completed: {assessment.residual_risk_level.value}")

    # Enable monitoring
    monitor = agent.enable_monitoring(
        vendor1.vendor_id,
        monitoring_types=['security_ratings', 'breaches', 'news'],
        check_frequency="daily",
    )

    # Create alert
    alert = agent.create_alert(
        vendor1.vendor_id,
        alert_type="security_rating_change",
        severity="medium",
        title="Security Rating Downgrade",
        description="Vendor security rating dropped from A to B",
        source="security_ratings",
    )

    print(f"Created alert: {alert.title}")

    # Get dashboard
    dashboard = agent.get_vendor_risk_dashboard()
    print(f"\nVendor Risk Dashboard:")
    print(f"  Total Vendors: {dashboard['vendors']['total']}")
    print(f"  Tier 1: {dashboard['vendors']['by_tier']['tier_1']}")
    print(f"  Assessments Due: {dashboard['assessments']['due_soon']}")
    print(f"  Open Findings: {dashboard['findings']['open']}")

    print(f"\nState: {agent.get_state()}")
