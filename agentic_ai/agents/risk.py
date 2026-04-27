"""
RiskAgent - Enterprise Risk Management (ERM)
=============================================

Provides risk identification, assessment, treatment planning,
risk registers, key risk indicators (KRIs), and risk reporting.
"""

import logging
import secrets
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from typing import Any, Dict, List, Optional


logger = logging.getLogger(__name__)


class RiskCategory(Enum):
    """Risk categories."""
    STRATEGIC = "strategic"
    OPERATIONAL = "operational"
    FINANCIAL = "financial"
    COMPLIANCE = "compliance"
    REPUTATIONAL = "reputational"
    CYBERSECURITY = "cybersecurity"
    TECHNOLOGY = "technology"
    THIRD_PARTY = "third_party"
    BUSINESS_CONTINUITY = "business_continuity"
    LEGAL = "legal"
    HUMAN_RESOURCES = "human_resources"
    ENVIRONMENTAL = "environmental"


class RiskLevel(Enum):
    """Risk levels."""
    VERY_LOW = "very_low"
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    VERY_HIGH = "very_high"
    CRITICAL = "critical"


class RiskStatus(Enum):
    """Risk status."""
    IDENTIFIED = "identified"
    ASSESSED = "assessed"
    TREATMENT_PLANNED = "treatment_planned"
    TREATMENT_IN_PROGRESS = "treatment_in_progress"
    MONITORED = "monitored"
    CLOSED = "closed"
    ACCEPTED = "accepted"


class TreatmentStrategy(Enum):
    """Risk treatment strategies."""
    AVOID = "avoid"
    REDUCE = "reduce"
    SHARE = "share"  # Transfer/Insure
    ACCEPT = "accept"


@dataclass
class Risk:
    """Risk record."""
    risk_id: str
    title: str
    description: str
    category: RiskCategory
    status: RiskStatus
    owner: str
    inherent_likelihood: int = 1  # 1-5
    inherent_impact: int = 1  # 1-5
    inherent_score: int = 1  # likelihood * impact
    residual_likelihood: int = 1
    residual_impact: int = 1
    residual_score: int = 1
    treatment_strategy: Optional[TreatmentStrategy] = None
    treatment_plan: str = ""
    controls: List[str] = field(default_factory=list)
    identified_at: datetime = field(default_factory=datetime.utcnow)
    assessed_at: Optional[datetime] = None
    target_resolution: Optional[datetime] = None
    closed_at: Optional[datetime] = None
    tags: List[str] = field(default_factory=list)


@dataclass
class Control:
    """Risk control."""
    control_id: str
    name: str
    description: str
    control_type: str  # preventive, detective, corrective, directive
    risk_id: Optional[str] = None
    owner: str = ""
    frequency: str = "ongoing"  # daily, weekly, monthly, quarterly, annually, ongoing
    effectiveness: str = "effective"  # effective, partially_effective, ineffective
    last_tested: Optional[datetime] = None
    test_results: str = ""
    automated: bool = False
    created_at: datetime = field(default_factory=datetime.utcnow)


@dataclass
class KeyRiskIndicator:
    """Key Risk Indicator (KRI)."""
    kri_id: str
    name: str
    description: str
    category: RiskCategory
    metric_type: str  # percentage, count, ratio, score
    risk_id: Optional[str] = None
    current_value: float = 0.0
    threshold_green: float = 0.0  # Acceptable
    threshold_yellow: float = 0.0  # Warning
    threshold_red: float = 0.0  # Critical
    direction: str = "lower_is_better"  # lower_is_better, higher_is_better
    status: str = "green"  # green, yellow, red
    last_measured: Optional[datetime] = None
    trend: str = "stable"  # improving, stable, deteriorating
    created_at: datetime = field(default_factory=datetime.utcnow)


@dataclass
class RiskAssessment:
    """Risk assessment record."""
    assessment_id: str
    name: str
    scope: str
    start_date: datetime
    status: str  # planned, in_progress, completed
    end_date: Optional[datetime] = None
    risks_identified: int = 0
    high_risks: int = 0
    critical_risks: int = 0
    assessor: str = ""
    findings: List[Dict[str, Any]] = field(default_factory=list)
    recommendations: List[str] = field(default_factory=list)
    created_at: datetime = field(default_factory=datetime.utcnow)


@dataclass
class RiskEvent:
    """Risk event/incident."""
    event_id: str
    risk_id: Optional[str]
    title: str
    description: str
    actual_impact: str
    financial_impact: float = 0.0
    occurred_at: datetime = field(default_factory=datetime.utcnow)
    detected_at: datetime = field(default_factory=datetime.utcnow)
    status: str = "reported"  # reported, investigating, contained, resolved
    root_cause: str = ""
    lessons_learned: List[str] = field(default_factory=list)


class RiskAgent:
    """
    Risk Agent for Enterprise Risk Management (ERM),
    risk registers, KRIs, and risk reporting.
    """

    def __init__(self, agent_id: str = "risk-agent"):
        self.agent_id = agent_id
        self.risks: Dict[str, Risk] = {}
        self.controls: Dict[str, Control] = {}
        self.kris: Dict[str, KeyRiskIndicator] = {}
        self.assessments: Dict[str, RiskAssessment] = {}
        self.events: Dict[str, RiskEvent] = {}

        # Risk scoring matrix
        self.risk_matrix = {
            1: RiskLevel.VERY_LOW,
            2: RiskLevel.LOW,
            3: RiskLevel.MEDIUM,
            4: RiskLevel.HIGH,
            5: RiskLevel.VERY_HIGH,
            6: RiskLevel.HIGH,
            8: RiskLevel.VERY_HIGH,
            9: RiskLevel.CRITICAL,
            10: RiskLevel.CRITICAL,
            12: RiskLevel.CRITICAL,
            15: RiskLevel.CRITICAL,
            16: RiskLevel.CRITICAL,
            20: RiskLevel.CRITICAL,
            25: RiskLevel.CRITICAL,
        }

        # Default risk appetite by category
        self.risk_appetite = {
            RiskCategory.STRATEGIC: {'tolerance': 'medium', 'limit': 15},
            RiskCategory.OPERATIONAL: {'tolerance': 'low', 'limit': 10},
            RiskCategory.FINANCIAL: {'tolerance': 'low', 'limit': 8},
            RiskCategory.COMPLIANCE: {'tolerance': 'very_low', 'limit': 5},
            RiskCategory.CYBERSECURITY: {'tolerance': 'low', 'limit': 10},
            RiskCategory.REPUTATIONAL: {'tolerance': 'very_low', 'limit': 5},
        }

    # ============================================
    # Risk Management
    # ============================================

    def identify_risk(
        self,
        title: str,
        description: str,
        category: RiskCategory,
        owner: str,
        inherent_likelihood: int,
        inherent_impact: int,
        tags: Optional[List[str]] = None,
    ) -> Risk:
        """Identify a new risk."""
        inherent_score = inherent_likelihood * inherent_impact

        risk = Risk(
            risk_id=self._generate_id("risk"),
            title=title,
            description=description,
            category=category,
            status=RiskStatus.IDENTIFIED,
            owner=owner,
            inherent_likelihood=inherent_likelihood,
            inherent_impact=inherent_impact,
            inherent_score=inherent_score,
            residual_likelihood=inherent_likelihood,
            residual_impact=inherent_impact,
            residual_score=inherent_score,
            tags=tags or [],
        )

        self.risks[risk.risk_id] = risk
        logger.info(f"Identified risk: {risk.title}")
        return risk

    def assess_risk(
        self,
        risk_id: str,
        controls: Optional[List[str]] = None,
        residual_likelihood: Optional[int] = None,
        residual_impact: Optional[int] = None,
    ) -> bool:
        """Assess risk with controls consideration."""
        if risk_id not in self.risks:
            return False

        risk = self.risks[risk_id]
        risk.status = RiskStatus.ASSESSED
        risk.assessed_at = datetime.utcnow()

        if controls:
            risk.controls = controls

        if residual_likelihood:
            risk.residual_likelihood = residual_likelihood

        if residual_impact:
            risk.residual_impact = residual_impact

        risk.residual_score = risk.residual_likelihood * risk.residual_impact
        return True

    def plan_treatment(
        self,
        risk_id: str,
        strategy: TreatmentStrategy,
        treatment_plan: str,
        target_resolution: Optional[datetime] = None,
    ) -> bool:
        """Plan risk treatment."""
        if risk_id not in self.risks:
            return False

        risk = self.risks[risk_id]
        risk.treatment_strategy = strategy
        risk.treatment_plan = treatment_plan
        risk.status = RiskStatus.TREATMENT_PLANNED

        if target_resolution:
            risk.target_resolution = target_resolution

        return True

    def update_risk_status(
        self,
        risk_id: str,
        status: RiskStatus,
    ) -> bool:
        """Update risk status."""
        if risk_id not in self.risks:
            return False

        self.risks[risk_id].status = status

        if status == RiskStatus.CLOSED:
            self.risks[risk_id].closed_at = datetime.utcnow()

        return True

    def get_risks(
        self,
        category: Optional[RiskCategory] = None,
        status: Optional[RiskStatus] = None,
        min_score: Optional[int] = None,
        owner: Optional[str] = None,
    ) -> List[Risk]:
        """Get risks with filtering."""
        risks = list(self.risks.values())

        if category:
            risks = [r for r in risks if r.category == category]

        if status:
            risks = [r for r in risks if r.status == status]

        if min_score:
            risks = [r for r in risks if r.residual_score >= min_score]

        if owner:
            risks = [r for r in risks if r.owner == owner]

        return risks

    def get_high_priority_risks(self, limit: int = 20) -> List[Risk]:
        """Get high priority risks sorted by score."""
        risks = list(self.risks.values())

        # Filter open risks
        open_risks = [
            r for r in risks
            if r.status not in [RiskStatus.CLOSED, RiskStatus.ACCEPTED]
        ]

        # Sort by residual score descending
        open_risks.sort(key=lambda r: r.residual_score, reverse=True)

        return open_risks[:limit]

    # ============================================
    # Control Management
    # ============================================

    def create_control(
        self,
        name: str,
        description: str,
        control_type: str,
        owner: str,
        risk_id: Optional[str] = None,
        frequency: str = "ongoing",
        automated: bool = False,
    ) -> Control:
        """Create a risk control."""
        control = Control(
            control_id=self._generate_id("ctrl"),
            name=name,
            description=description,
            control_type=control_type,
            risk_id=risk_id,
            owner=owner,
            frequency=frequency,
            automated=automated,
        )

        self.controls[control.control_id] = control

        # Link to risk
        if risk_id and risk_id in self.risks:
            if control.control_id not in self.risks[risk_id].controls:
                self.risks[risk_id].controls.append(control.control_id)

        return control

    def test_control(
        self,
        control_id: str,
        effectiveness: str,
        test_results: str,
    ) -> bool:
        """Test control effectiveness."""
        if control_id not in self.controls:
            return False

        control = self.controls[control_id]
        control.effectiveness = effectiveness
        control.test_results = test_results
        control.last_tested = datetime.utcnow()

        return True

    def get_controls(
        self,
        control_type: Optional[str] = None,
        effectiveness: Optional[str] = None,
        risk_id: Optional[str] = None,
    ) -> List[Control]:
        """Get controls with filtering."""
        controls = list(self.controls.values())

        if control_type:
            controls = [c for c in controls if c.control_type == control_type]

        if effectiveness:
            controls = [c for c in controls if c.effectiveness == effectiveness]

        if risk_id:
            controls = [c for c in controls if c.risk_id == risk_id]

        return controls

    # ============================================
    # Key Risk Indicators
    # ============================================

    def create_kri(
        self,
        name: str,
        description: str,
        category: RiskCategory,
        metric_type: str,
        threshold_green: float,
        threshold_yellow: float,
        threshold_red: float,
        direction: str = "lower_is_better",
        risk_id: Optional[str] = None,
    ) -> KeyRiskIndicator:
        """Create a Key Risk Indicator."""
        kri = KeyRiskIndicator(
            kri_id=self._generate_id("kri"),
            name=name,
            description=description,
            category=category,
            metric_type=metric_type,
            threshold_green=threshold_green,
            threshold_yellow=threshold_yellow,
            threshold_red=threshold_red,
            direction=direction,
            risk_id=risk_id,
        )

        self.kris[kri.kri_id] = kri
        return kri

    def update_kri_value(
        self,
        kri_id: str,
        current_value: float,
    ) -> bool:
        """Update KRI value and calculate status."""
        if kri_id not in self.kris:
            return False

        kri = self.kris[kri_id]
        kri.current_value = current_value
        kri.last_measured = datetime.utcnow()

        # Determine status based on thresholds and direction
        if kri.direction == "lower_is_better":
            if current_value <= kri.threshold_green:
                kri.status = "green"
            elif current_value <= kri.threshold_yellow:
                kri.status = "yellow"
            else:
                kri.status = "red"
        else:  # higher_is_better
            if current_value >= kri.threshold_green:
                kri.status = "green"
            elif current_value >= kri.threshold_yellow:
                kri.status = "yellow"
            else:
                kri.status = "red"

        # Determine trend (simplified)
        kri.trend = "stable"  # In real impl, compare to historical values

        return True

    def get_kris(
        self,
        category: Optional[RiskCategory] = None,
        status: Optional[str] = None,
    ) -> List[KeyRiskIndicator]:
        """Get KRIs with filtering."""
        kris = list(self.kris.values())

        if category:
            kris = [k for k in kris if k.category == category]

        if status:
            kris = [k for k in kris if k.status == status]

        return kris

    def get_kris_at_risk(self) -> List[KeyRiskIndicator]:
        """Get KRIs in yellow or red status."""
        return [k for k in self.kris.values() if k.status in ['yellow', 'red']]

    # ============================================
    # Risk Assessments
    # ============================================

    def create_assessment(
        self,
        name: str,
        scope: str,
        assessor: str,
        start_date: datetime,
    ) -> RiskAssessment:
        """Create a risk assessment."""
        assessment = RiskAssessment(
            assessment_id=self._generate_id("assess"),
            name=name,
            scope=scope,
            status="planned",
            start_date=start_date,
            assessor=assessor,
        )

        self.assessments[assessment.assessment_id] = assessment
        return assessment

    def complete_assessment(
        self,
        assessment_id: str,
        risks_identified: int,
        findings: Optional[List[Dict[str, Any]]] = None,
        recommendations: Optional[List[str]] = None,
    ) -> bool:
        """Complete a risk assessment."""
        if assessment_id not in self.assessments:
            return False

        assessment = self.assessments[assessment_id]
        assessment.status = "completed"
        assessment.end_date = datetime.utcnow()
        assessment.risks_identified = risks_identified
        assessment.findings = findings or []
        assessment.recommendations = recommendations or []

        # Count high/critical risks
        high_risks = [f for f in assessment.findings if f.get('severity') in ['high', 'critical']]
        assessment.high_risks = len([f for f in high_risks if f.get('severity') == 'high'])
        assessment.critical_risks = len([f for f in high_risks if f.get('severity') == 'critical'])

        return True

    def get_assessments(self, status: Optional[str] = None) -> List[RiskAssessment]:
        """Get assessments with filtering."""
        assessments = list(self.assessments.values())

        if status:
            assessments = [a for a in assessments if a.status == status]

        return assessments

    # ============================================
    # Risk Events
    # ============================================

    def report_event(
        self,
        title: str,
        description: str,
        actual_impact: str,
        financial_impact: float = 0.0,
        risk_id: Optional[str] = None,
    ) -> RiskEvent:
        """Report a risk event/incident."""
        event = RiskEvent(
            event_id=self._generate_id("event"),
            risk_id=risk_id,
            title=title,
            description=description,
            actual_impact=actual_impact,
            financial_impact=financial_impact,
        )

        self.events[event.event_id] = event
        logger.warning(f"Risk event reported: {event.title}")
        return event

    def resolve_event(
        self,
        event_id: str,
        root_cause: str,
        lessons_learned: List[str],
    ) -> bool:
        """Resolve a risk event."""
        if event_id not in self.events:
            return False

        event = self.events[event_id]
        event.status = "resolved"
        event.root_cause = root_cause
        event.lessons_learned = lessons_learned

        return True

    def get_events(
        self,
        risk_id: Optional[str] = None,
        status: Optional[str] = None,
    ) -> List[RiskEvent]:
        """Get events with filtering."""
        events = list(self.events.values())

        if risk_id:
            events = [e for e in events if e.risk_id == risk_id]

        if status:
            events = [e for e in events if e.status == status]

        return events

    # ============================================
    # Reporting
    # ============================================

    def get_risk_register(self) -> Dict[str, Any]:
        """Generate risk register report."""
        risks = list(self.risks.values())

        # By category
        by_category = {}
        for cat in RiskCategory:
            by_category[cat.value] = len([r for r in risks if r.category == cat])

        # By status
        by_status = {}
        for status in RiskStatus:
            by_status[status.value] = len([r for r in risks if r.status == status])

        # By score
        by_score = {
            'critical': len([r for r in risks if r.residual_score >= 20]),
            'very_high': len([r for r in risks if 15 <= r.residual_score < 20]),
            'high': len([r for r in risks if 10 <= r.residual_score < 15]),
            'medium': len([r for r in risks if 5 <= r.residual_score < 10]),
            'low': len([r for r in risks if r.residual_score < 5]),
        }

        return {
            'total_risks': len(risks),
            'by_category': by_category,
            'by_status': by_status,
            'by_score': by_score,
            'open_risks': len([r for r in risks if r.status not in [RiskStatus.CLOSED, RiskStatus.ACCEPTED]]),
            'avg_residual_score': round(sum(r.residual_score for r in risks) / len(risks), 1) if risks else 0,
        }

    def get_risk_dashboard(self) -> Dict[str, Any]:
        """Generate risk dashboard summary."""
        risks = list(self.risks.values())
        events = list(self.events.values())
        kris = list(self.kris.values())

        # Top risks
        top_risks = sorted(risks, key=lambda r: r.residual_score, reverse=True)[:5]

        # KRIs at risk
        kris_at_risk = [k for k in kris if k.status in ['yellow', 'red']]

        # Events this month
        this_month = datetime.utcnow() - timedelta(days=30)
        recent_events = [e for e in events if e.occurred_at >= this_month]

        # Financial impact
        total_financial_impact = sum(e.financial_impact for e in events)

        return {
            'overview': {
                'total_risks': len(risks),
                'critical_risks': len([r for r in risks if r.residual_score >= 20]),
                'high_risks': len([r for r in risks if 15 <= r.residual_score < 20]),
                'open_risks': len([r for r in risks if r.status not in [RiskStatus.CLOSED, RiskStatus.ACCEPTED]]),
            },
            'top_risks': [
                {
                    'risk_id': r.risk_id,
                    'title': r.title,
                    'category': r.category.value,
                    'score': r.residual_score,
                    'status': r.status.value,
                }
                for r in top_risks
            ],
            'kris': {
                'total': len(kris),
                'at_risk': len(kris_at_risk),
                'red': len([k for k in kris if k.status == 'red']),
                'yellow': len([k for k in kris if k.status == 'yellow']),
            },
            'events': {
                'total': len(events),
                'last_30_days': len(recent_events),
                'total_financial_impact': total_financial_impact,
            },
            'controls': {
                'total': len(self.controls),
                'tested': len([c for c in self.controls.values() if c.last_tested]),
                'effective': len([c for c in self.controls.values() if c.effectiveness == 'effective']),
            },
        }

    def get_risk_appetite_status(self) -> Dict[str, Any]:
        """Get risk appetite compliance status."""
        status = {}

        for category, appetite in self.risk_appetite.items():
            risks_in_cat = [r for r in self.risks.values() if r.category == category]

            # Count risks above appetite limit
            above_limit = len([r for r in risks_in_cat if r.residual_score > appetite['limit']])

            status[category.value] = {
                'tolerance': appetite['tolerance'],
                'limit': appetite['limit'],
                'total_risks': len(risks_in_cat),
                'above_limit': above_limit,
                'compliant': above_limit == 0,
                'max_score': max([r.residual_score for r in risks_in_cat], default=0),
            }

        return status

    # ============================================
    # Utilities
    # ============================================

    def _score_to_level(self, score: int) -> RiskLevel:
        """Convert score to risk level."""
        if score <= 2:
            return RiskLevel.VERY_LOW
        elif score <= 4:
            return RiskLevel.LOW
        elif score <= 9:
            return RiskLevel.MEDIUM
        elif score <= 15:
            return RiskLevel.HIGH
        else:
            return RiskLevel.VERY_HIGH

    def _generate_id(self, prefix: str) -> str:
        """Generate a unique ID."""
        timestamp = datetime.utcnow().strftime('%Y%m%d%H%M%S')
        random_suffix = secrets.token_hex(4)
        return f"{prefix}-{timestamp}-{random_suffix}"

    def get_state(self) -> Dict[str, Any]:
        """Get agent state summary."""
        risks = list(self.risks.values())
        return {
            'agent_id': self.agent_id,
            'risks_count': len(risks),
            'open_risks': len([r for r in risks if r.status not in [RiskStatus.CLOSED, RiskStatus.ACCEPTED]]),
            'critical_risks': len([r for r in risks if r.residual_score >= 20]),
            'high_risks': len([r for r in risks if 15 <= r.residual_score < 20]),
            'controls_count': len(self.controls),
            'kris_count': len(self.kris),
            'kris_at_risk': len([k for k in self.kris.values() if k.status in ['yellow', 'red']]),
            'assessments_count': len(self.assessments),
            'events_count': len(self.events),
        }


def get_capabilities() -> Dict[str, Any]:
    """Return agent capabilities for orchestration."""
    return {
        'agent_type': 'risk',
        'version': '1.0.0',
        'capabilities': [
            'identify_risk',
            'assess_risk',
            'plan_treatment',
            'update_risk_status',
            'get_risks',
            'get_high_priority_risks',
            'create_control',
            'test_control',
            'get_controls',
            'create_kri',
            'update_kri_value',
            'get_kris',
            'get_kris_at_risk',
            'create_assessment',
            'complete_assessment',
            'get_assessments',
            'report_event',
            'resolve_event',
            'get_events',
            'get_risk_register',
            'get_risk_dashboard',
            'get_risk_appetite_status',
        ],
        'risk_categories': [c.value for c in RiskCategory],
        'risk_levels': [l.value for l in RiskLevel],
        'risk_statuses': [s.value for s in RiskStatus],
        'treatment_strategies': [s.value for s in TreatmentStrategy],
    }


if __name__ == "__main__":
    agent = RiskAgent()

    # Identify risks
    risk1 = agent.identify_risk(
        title="Data Breach",
        description="Potential unauthorized access to customer data",
        category=RiskCategory.CYBERSECURITY,
        owner="ciso@example.com",
        inherent_likelihood=4,
        inherent_impact=5,
        tags=['data', 'security', 'privacy'],
    )

    print(f"Identified risk: {risk1.title} (Score: {risk1.inherent_score})")

    # Assess risk with controls
    control = agent.create_control(
        name="Multi-Factor Authentication",
        description="MFA required for all system access",
        control_type="preventive",
        owner="security-team@example.com",
        risk_id=risk1.risk_id,
        automated=True,
    )

    agent.assess_risk(
        risk1.risk_id,
        controls=[control.control_id],
        residual_likelihood=2,
        residual_impact=5,
    )

    print(f"Residual score: {risk1.residual_score}")

    # Plan treatment
    agent.plan_treatment(
        risk1.risk_id,
        strategy=TreatmentStrategy.REDUCE,
        treatment_plan="Implement additional monitoring and DLP",
        target_resolution=datetime.utcnow() + timedelta(days=90),
    )

    # Create KRI
    kri = agent.create_kri(
        name="Failed Login Attempts",
        description="Number of failed login attempts per day",
        category=RiskCategory.CYBERSECURITY,
        metric_type="count",
        threshold_green=100,
        threshold_yellow=500,
        threshold_red=1000,
        direction="lower_is_better",
        risk_id=risk1.risk_id,
    )

    # Update KRI value
    agent.update_kri_value(kri.kri_id, current_value=750)
    print(f"KRI Status: {kri.status}")

    # Create assessment
    assessment = agent.create_assessment(
        name="Q1 Cybersecurity Assessment",
        scope="All IT systems and applications",
        assessor="risk-team@example.com",
        start_date=datetime.utcnow(),
    )

    agent.complete_assessment(
        assessment.assessment_id,
        risks_identified=15,
        findings=[
            {'severity': 'high', 'finding': 'Outdated systems'},
            {'severity': 'critical', 'finding': 'Unpatched vulnerabilities'},
        ],
        recommendations=["Patch management program", "System upgrades"],
    )

    # Report event
    event = agent.report_event(
        title="Phishing Attack",
        description="Targeted phishing campaign against finance team",
        actual_impact="2 employees clicked links, no data loss",
        financial_impact=5000.0,
        risk_id=risk1.risk_id,
    )

    agent.resolve_event(
        event.event_id,
        root_cause="Insufficient security awareness training",
        lessons_learned=["Need more frequent training", "Implement email filtering"],
    )

    # Get risk dashboard
    dashboard = agent.get_risk_dashboard()
    print(f"\nRisk Dashboard:")
    print(f"  Total Risks: {dashboard['overview']['total_risks']}")
    print(f"  Critical: {dashboard['overview']['critical_risks']}")
    print(f"  KRIs at Risk: {dashboard['kris']['at_risk']}")

    # Get risk register
    register = agent.get_risk_register()
    print(f"\nRisk Register:")
    print(f"  By Category: {register['by_category']}")
    print(f"  By Score: {register['by_score']}")

    print(f"\nState: {agent.get_state()}")
