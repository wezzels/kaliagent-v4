"""
EthicsAgent - AI Ethics & Algorithmic Fairness
===============================================

Provides AI ethics review, bias detection, fairness assessment,
explainability tracking, and ethical impact assessments.
"""

import logging
import secrets
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from typing import Any, Dict, List, Optional


logger = logging.getLogger(__name__)


class EthicsPrinciple(Enum):
    """AI ethics principles."""
    FAIRNESS = "fairness"
    TRANSPARENCY = "transparency"
    ACCOUNTABILITY = "accountability"
    PRIVACY = "privacy"
    SAFETY = "safety"
    NON_DISCRIMINATION = "non_discrimination"
    HUMAN_AGENCY = "human_agency"
    SOCIETAL_WELLBEING = "societal_wellbeing"


class BiasType(Enum):
    """Bias types."""
    HISTORICAL = "historical"
    REPRESENTATION = "representation"
    MEASUREMENT = "measurement"
    AGGREGATION = "aggregation"
    EVALUATION = "evaluation"
    DEPLOYMENT = "deployment"
    AUTOMATION = "automation_bias"


class FairnessMetric(Enum):
    """Fairness metrics."""
    DEMOGRAPHIC_PARITY = "demographic_parity"
    EQUALIZED_ODDS = "equalized_odds"
    EQUAL_OPPORTUNITY = "equal_opportunity"
    PREDICTIVE_PARITY = "predictive_parity"
    CALIBRATION = "calibration"
    INDIVIDUAL_FAIRNESS = "individual_fairness"


class RiskLevel(Enum):
    """Risk levels."""
    NEGLIGIBLE = "negligible"
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    UNACCEPTABLE = "unacceptable"


class AssessmentStatus(Enum):
    """Assessment status."""
    DRAFT = "draft"
    IN_REVIEW = "in_review"
    APPROVED = "approved"
    REJECTED = "rejected"
    REQUIRES_REMEDIATION = "requires_remediation"


@dataclass
class AIModel:
    """AI/ML model record."""
    model_id: str
    name: str
    description: str
    model_type: str  # classification, regression, clustering, nlp, cv, etc.
    purpose: str
    risk_level: RiskLevel
    developer: str
    version: str = "1.0"
    training_data_description: str = ""
    training_period: Optional[str] = None
    deployment_date: Optional[datetime] = None
    last_updated: datetime = field(default_factory=datetime.utcnow)
    tags: List[str] = field(default_factory=list)


@dataclass
class EthicsAssessment:
    """AI ethics assessment."""
    assessment_id: str
    model_id: str
    assessment_type: str  # initial, periodic, incident-triggered
    status: AssessmentStatus
    principles_evaluated: List[EthicsPrinciple]
    overall_risk: RiskLevel = RiskLevel.MEDIUM
    findings: List[Dict[str, Any]] = field(default_factory=list)
    recommendations: List[str] = field(default_factory=list)
    mitigations: List[str] = field(default_factory=list)
    reviewer: Optional[str] = None
    reviewed_at: Optional[datetime] = None
    created_at: datetime = field(default_factory=datetime.utcnow)


@dataclass
class BiasAssessment:
    """Bias assessment record."""
    bias_id: str
    model_id: str
    bias_type: BiasType
    affected_group: str
    description: str
    severity: RiskLevel
    evidence: Dict[str, Any] = field(default_factory=dict)
    metric_used: Optional[FairnessMetric] = None
    metric_value: Optional[float] = None
    threshold: Optional[float] = None
    status: str = "identified"  # identified, investigating, mitigated, accepted
    remediation_plan: str = ""
    identified_at: datetime = field(default_factory=datetime.utcnow)


@dataclass
class FairnessReport:
    """Fairness metrics report."""
    report_id: str
    model_id: str
    dataset: str
    protected_attributes: List[str]
    metrics: Dict[FairnessMetric, Dict[str, Any]]
    overall_score: float
    disparities: List[Dict[str, Any]] = field(default_factory=list)
    recommendations: List[str] = field(default_factory=list)
    generated_at: datetime = field(default_factory=datetime.utcnow)


@dataclass
class ExplainabilityRecord:
    """Model explainability record."""
    record_id: str
    model_id: str
    technique: str  # SHAP, LIME, feature_importance, etc.
    explanation_type: str  # global, local
    features: List[Dict[str, Any]] = field(default_factory=list)
    visualization_url: Optional[str] = None
    generated_at: datetime = field(default_factory=datetime.utcnow)


@dataclass
class EthicalIncident:
    """Ethical incident record."""
    incident_id: str
    model_id: Optional[str]
    title: str
    description: str
    severity: RiskLevel
    principles_violated: List[EthicsPrinciple]
    affected_parties: List[str] = field(default_factory=list)
    status: str = "reported"  # reported, investigating, contained, resolved
    root_cause: str = ""
    remediation: List[str] = field(default_factory=list)
    reported_at: datetime = field(default_factory=datetime.utcnow)
    resolved_at: Optional[datetime] = None


@dataclass
class HumanOversight:
    """Human oversight configuration."""
    oversight_id: str
    model_id: str
    oversight_type: str  # human_in_loop, human_on_loop, human_oversight
    trigger_conditions: List[str] = field(default_factory=list)
    reviewers: List[str] = field(default_factory=list)
    escalation_path: List[str] = field(default_factory=list)
    review_timeout_hours: int = 24
    enabled: bool = True
    created_at: datetime = field(default_factory=datetime.utcnow)


class EthicsAgent:
    """
    Ethics Agent for AI ethics review, bias detection,
    fairness assessment, and explainability tracking.
    """

    def __init__(self, agent_id: str = "ethics-agent"):
        self.agent_id = agent_id
        self.models: Dict[str, AIModel] = {}
        self.assessments: Dict[str, EthicsAssessment] = {}
        self.bias_assessments: Dict[str, BiasAssessment] = {}
        self.fairness_reports: Dict[str, FairnessReport] = {}
        self.explainability: Dict[str, ExplainabilityRecord] = {}
        self.incidents: Dict[str, EthicalIncident] = {}
        self.oversight: Dict[str, HumanOversight] = {}

        # Ethics guidelines
        self.ethics_guidelines = self._init_ethics_guidelines()

        # Bias detection thresholds
        self.bias_thresholds = {
            FairnessMetric.DEMOGRAPHIC_PARITY: 0.1,
            FairnessMetric.EQUALIZED_ODDS: 0.1,
            FairnessMetric.EQUAL_OPPORTUNITY: 0.1,
            FairnessMetric.PREDICTIVE_PARITY: 0.1,
        }

    def _init_ethics_guidelines(self) -> Dict[EthicsPrinciple, List[str]]:
        """Initialize ethics guidelines."""
        return {
            EthicsPrinciple.FAIRNESS: [
                "Model should not discriminate against protected groups",
                "Training data should be representative of target population",
                "Outcomes should be equitable across demographics",
            ],
            EthicsPrinciple.TRANSPARENCY: [
                "Model capabilities and limitations should be documented",
                "Decision criteria should be explainable",
                "Stakeholders should be informed of AI usage",
            ],
            EthicsPrinciple.ACCOUNTABILITY: [
                "Clear ownership for model outcomes",
                "Appeal process for automated decisions",
                "Audit trail for model decisions",
            ],
            EthicsPrinciple.PRIVACY: [
                "Personal data should be minimized",
                "Data should be anonymized where possible",
                "Consent should be obtained for data usage",
            ],
            EthicsPrinciple.SAFETY: [
                "Model should not cause harm",
                "Fail-safe mechanisms should be in place",
                "Regular safety testing should be conducted",
            ],
        }

    # ============================================
    # Model Registration
    # ============================================

    def register_model(
        self,
        name: str,
        description: str,
        model_type: str,
        purpose: str,
        developer: str,
        risk_level: RiskLevel,
        training_data_description: str = "",
        tags: Optional[List[str]] = None,
    ) -> AIModel:
        """Register an AI model for ethics oversight."""
        model = AIModel(
            model_id=self._generate_id("model"),
            name=name,
            description=description,
            model_type=model_type,
            purpose=purpose,
            risk_level=risk_level,
            developer=developer,
            training_data_description=training_data_description,
            tags=tags or [],
        )

        self.models[model.model_id] = model
        logger.info(f"Registered model: {model.name}")
        return model

    def update_model_risk(self, model_id: str, risk_level: RiskLevel) -> bool:
        """Update model risk level."""
        if model_id not in self.models:
            return False

        self.models[model_id].risk_level = risk_level
        self.models[model_id].last_updated = datetime.utcnow()

        return True

    def get_models(
        self,
        risk_level: Optional[RiskLevel] = None,
        model_type: Optional[str] = None,
    ) -> List[AIModel]:
        """Get models with filtering."""
        models = list(self.models.values())

        if risk_level:
            models = [m for m in models if m.risk_level == risk_level]

        if model_type:
            models = [m for m in models if m.model_type == model_type]

        return models

    # ============================================
    # Ethics Assessment
    # ============================================

    def create_ethics_assessment(
        self,
        model_id: str,
        assessment_type: str,
        principles_evaluated: Optional[List[EthicsPrinciple]] = None,
    ) -> EthicsAssessment:
        """Create ethics assessment for a model."""
        if model_id not in self.models:
            raise ValueError(f"Model {model_id} not found")

        assessment = EthicsAssessment(
            assessment_id=self._generate_id("ethics"),
            model_id=model_id,
            assessment_type=assessment_type,
            status=AssessmentStatus.DRAFT,
            principles_evaluated=principles_evaluated or list(EthicsPrinciple),
        )

        self.assessments[assessment.assessment_id] = assessment
        return assessment

    def add_finding(
        self,
        assessment_id: str,
        principle: EthicsPrinciple,
        finding: str,
        severity: RiskLevel,
        recommendation: str,
    ) -> bool:
        """Add finding to ethics assessment."""
        if assessment_id not in self.assessments:
            return False

        assessment = self.assessments[assessment_id]
        assessment.findings.append({
            'principle': principle.value,
            'finding': finding,
            'severity': severity.value,
            'recommendation': recommendation,
            'identified_at': datetime.utcnow().isoformat(),
        })

        # Update overall risk
        self._update_assessment_risk(assessment)

        return True

    def complete_assessment(
        self,
        assessment_id: str,
        reviewer: str,
        status: AssessmentStatus,
        mitigations: Optional[List[str]] = None,
    ) -> bool:
        """Complete ethics assessment."""
        if assessment_id not in self.assessments:
            return False

        assessment = self.assessments[assessment_id]
        assessment.status = status
        assessment.reviewer = reviewer
        assessment.reviewed_at = datetime.utcnow()
        assessment.mitigations = mitigations or []

        return True

    def _update_assessment_risk(self, assessment: EthicsAssessment):
        """Update overall risk based on findings."""
        severity_scores = {
            RiskLevel.NEGLIGIBLE: 0,
            RiskLevel.LOW: 1,
            RiskLevel.MEDIUM: 2,
            RiskLevel.HIGH: 3,
            RiskLevel.UNACCEPTABLE: 4,
        }

        if not assessment.findings:
            assessment.overall_risk = RiskLevel.NEGLIGIBLE
            return

        max_severity = max(
            severity_scores.get(RiskLevel(f['severity']), 0)
            for f in assessment.findings
        )

        if max_severity >= 4:
            assessment.overall_risk = RiskLevel.UNACCEPTABLE
        elif max_severity >= 3:
            assessment.overall_risk = RiskLevel.HIGH
        elif max_severity >= 2:
            assessment.overall_risk = RiskLevel.MEDIUM
        else:
            assessment.overall_risk = RiskLevel.LOW

    # ============================================
    # Bias Detection
    # ============================================

    def detect_bias(
        self,
        model_id: str,
        bias_type: BiasType,
        affected_group: str,
        description: str,
        evidence: Dict[str, Any],
        metric_used: Optional[FairnessMetric] = None,
        metric_value: Optional[float] = None,
    ) -> BiasAssessment:
        """Record detected bias."""
        # Determine severity
        severity = RiskLevel.MEDIUM
        if metric_value is not None and metric_used:
            threshold = self.bias_thresholds.get(metric_used, 0.1)
            if abs(metric_value) > threshold * 2:
                severity = RiskLevel.HIGH
            elif abs(metric_value) > threshold:
                severity = RiskLevel.MEDIUM
            else:
                severity = RiskLevel.LOW

        bias = BiasAssessment(
            bias_id=self._generate_id("bias"),
            model_id=model_id,
            bias_type=bias_type,
            affected_group=affected_group,
            description=description,
            severity=severity,
            evidence=evidence,
            metric_used=metric_used,
            metric_value=metric_value,
            threshold=self.bias_thresholds.get(metric_used) if metric_used else None,
        )

        self.bias_assessments[bias.bias_id] = bias
        logger.warning(f"Bias detected in {model_id}: {bias_type.value}")
        return bias

    def create_remediation_plan(
        self,
        bias_id: str,
        plan: str,
    ) -> bool:
        """Create remediation plan for bias."""
        if bias_id not in self.bias_assessments:
            return False

        self.bias_assessments[bias_id].remediation_plan = plan
        self.bias_assessments[bias_id].status = "investigating"

        return True

    def mark_bias_mitigated(self, bias_id: str) -> bool:
        """Mark bias as mitigated."""
        if bias_id not in self.bias_assessments:
            return False

        self.bias_assessments[bias_id].status = "mitigated"
        return True

    def get_bias_assessments(
        self,
        model_id: Optional[str] = None,
        bias_type: Optional[BiasType] = None,
        severity: Optional[RiskLevel] = None,
    ) -> List[BiasAssessment]:
        """Get bias assessments with filtering."""
        assessments = list(self.bias_assessments.values())

        if model_id:
            assessments = [a for a in assessments if a.model_id == model_id]

        if bias_type:
            assessments = [a for a in assessments if a.bias_type == bias_type]

        if severity:
            assessments = [a for a in assessments if a.severity == severity]

        return assessments

    # ============================================
    # Fairness Assessment
    # ============================================

    def generate_fairness_report(
        self,
        model_id: str,
        dataset: str,
        protected_attributes: List[str],
        metrics: Dict[str, Dict[str, Any]],
    ) -> FairnessReport:
        """Generate fairness metrics report."""
        # Parse metrics
        parsed_metrics = {}
        disparities = []

        for metric_name, data in metrics.items():
            try:
                metric = FairnessMetric(metric_name)
                parsed_metrics[metric] = data

                # Check for disparities
                if 'disparity' in data and data['disparity'] > self.bias_thresholds.get(metric, 0.1):
                    disparities.append({
                        'metric': metric_name,
                        'disparity': data['disparity'],
                        'threshold': self.bias_thresholds.get(metric, 0.1),
                    })
            except ValueError:
                continue

        # Calculate overall score (100 - average disparity * 100)
        avg_disparity = sum(d['disparity'] for d in disparities) / len(disparities) if disparities else 0
        overall_score = max(0, 100 - (avg_disparity * 100))

        report = FairnessReport(
            report_id=self._generate_id("fairness"),
            model_id=model_id,
            dataset=dataset,
            protected_attributes=protected_attributes,
            metrics=parsed_metrics,
            overall_score=round(overall_score, 1),
            disparities=disparities,
        )

        # Generate recommendations
        if disparities:
            report.recommendations = [
                f"Address {d['metric']} disparity ({d['disparity']:.2f} > {d['threshold']})",
                "Consider reweighting training data",
                "Evaluate model performance across subgroups",
            ]

        self.fairness_reports[report.report_id] = report
        return report

    def get_fairness_reports(self, model_id: Optional[str] = None) -> List[FairnessReport]:
        """Get fairness reports with filtering."""
        reports = list(self.fairness_reports.values())

        if model_id:
            reports = [r for r in reports if r.model_id == model_id]

        return reports

    # ============================================
    # Explainability
    # ============================================

    def add_explainability_record(
        self,
        model_id: str,
        technique: str,
        explanation_type: str,
        features: Optional[List[Dict[str, Any]]] = None,
        visualization_url: Optional[str] = None,
    ) -> ExplainabilityRecord:
        """Add explainability record."""
        record = ExplainabilityRecord(
            record_id=self._generate_id("explain"),
            model_id=model_id,
            technique=technique,
            explanation_type=explanation_type,
            features=features or [],
            visualization_url=visualization_url,
        )

        self.explainability[record.record_id] = record
        return record

    def get_explainability(self, model_id: str) -> List[ExplainabilityRecord]:
        """Get explainability records for a model."""
        return [
            r for r in self.explainability.values()
            if r.model_id == model_id
        ]

    # ============================================
    # Incident Management
    # ============================================

    def report_incident(
        self,
        title: str,
        description: str,
        severity: RiskLevel,
        principles_violated: List[EthicsPrinciple],
        model_id: Optional[str] = None,
        affected_parties: Optional[List[str]] = None,
    ) -> EthicalIncident:
        """Report ethical incident."""
        incident = EthicalIncident(
            incident_id=self._generate_id("incident"),
            model_id=model_id,
            title=title,
            description=description,
            severity=severity,
            principles_violated=principles_violated,
            affected_parties=affected_parties or [],
        )

        self.incidents[incident.incident_id] = incident
        logger.warning(f"Ethical incident reported: {incident.title}")
        return incident

    def resolve_incident(
        self,
        incident_id: str,
        root_cause: str,
        remediation: List[str],
    ) -> bool:
        """Resolve ethical incident."""
        if incident_id not in self.incidents:
            return False

        incident = self.incidents[incident_id]
        incident.status = "resolved"
        incident.root_cause = root_cause
        incident.remediation = remediation
        incident.resolved_at = datetime.utcnow()

        return True

    def get_incidents(
        self,
        severity: Optional[RiskLevel] = None,
        status: Optional[str] = None,
    ) -> List[EthicalIncident]:
        """Get incidents with filtering."""
        incidents = list(self.incidents.values())

        if severity:
            incidents = [i for i in incidents if i.severity == severity]

        if status:
            incidents = [i for i in incidents if i.status == status]

        return incidents

    # ============================================
    # Human Oversight
    # ============================================

    def configure_oversight(
        self,
        model_id: str,
        oversight_type: str,
        trigger_conditions: List[str],
        reviewers: List[str],
        escalation_path: Optional[List[str]] = None,
        review_timeout_hours: int = 24,
    ) -> HumanOversight:
        """Configure human oversight for a model."""
        oversight = HumanOversight(
            oversight_id=self._generate_id("oversight"),
            model_id=model_id,
            oversight_type=oversight_type,
            trigger_conditions=trigger_conditions,
            reviewers=reviewers,
            escalation_path=escalation_path or [],
            review_timeout_hours=review_timeout_hours,
        )

        self.oversight[oversight.oversight_id] = oversight
        return oversight

    def get_oversight_config(self, model_id: str) -> Optional[HumanOversight]:
        """Get oversight configuration for a model."""
        for oversight in self.oversight.values():
            if oversight.model_id == model_id and oversight.enabled:
                return oversight
        return None

    # ============================================
    # Reporting
    # ============================================

    def get_ethics_report(self) -> Dict[str, Any]:
        """Generate comprehensive ethics report."""
        models = list(self.models.values())
        assessments = list(self.assessments.values())
        incidents = list(self.incidents.values())
        bias_list = list(self.bias_assessments.values())

        # Models by risk
        by_risk = {}
        for risk in RiskLevel:
            by_risk[risk.value] = len([m for m in models if m.risk_level == risk])

        # Assessment status
        by_status = {}
        for status in AssessmentStatus:
            by_status[status.value] = len([a for a in assessments if a.status == status])

        # Bias by type
        by_bias_type = {}
        for bias_type in BiasType:
            by_bias_type[bias_type.value] = len([b for b in bias_list if b.bias_type == bias_type])

        # Open incidents
        open_incidents = len([i for i in incidents if i.status != 'resolved'])

        return {
            'models': {
                'total': len(models),
                'by_risk': by_risk,
                'high_risk_count': by_risk.get('high', 0) + by_risk.get('unacceptable', 0),
            },
            'assessments': {
                'total': len(assessments),
                'by_status': by_status,
                'pending_review': len([a for a in assessments if a.status == AssessmentStatus.IN_REVIEW]),
            },
            'bias': {
                'total_detected': len(bias_list),
                'by_type': by_bias_type,
                'mitigated': len([b for b in bias_list if b.status == 'mitigated']),
            },
            'incidents': {
                'total': len(incidents),
                'open': open_incidents,
                'critical': len([i for i in incidents if i.severity == RiskLevel.UNACCEPTABLE]),
            },
            'oversight': {
                'configured_models': len([o for o in self.oversight.values() if o.enabled]),
            },
        }

    def get_model_ethics_profile(self, model_id: str) -> Dict[str, Any]:
        """Get comprehensive ethics profile for a model."""
        if model_id not in self.models:
            return {'error': 'Model not found'}

        model = self.models[model_id]

        assessments = [a for a in self.assessments.values() if a.model_id == model_id]
        bias_list = [b for b in self.bias_assessments.values() if b.model_id == model_id]
        incidents = [i for i in self.incidents.values() if i.model_id == model_id]
        fairness = [f for f in self.fairness_reports.values() if f.model_id == model_id]
        explainability = self.get_explainability(model_id)
        oversight = self.get_oversight_config(model_id)

        return {
            'model': {
                'model_id': model_id,
                'name': model.name,
                'risk_level': model.risk_level.value,
                'purpose': model.purpose,
            },
            'assessments': {
                'total': len(assessments),
                'latest_status': assessments[-1].status.value if assessments else None,
                'latest_risk': assessments[-1].overall_risk.value if assessments else None,
            },
            'bias': {
                'total_detected': len(bias_list),
                'by_severity': {
                    sev.value: len([b for b in bias_list if b.severity == sev])
                    for sev in RiskLevel
                },
            },
            'incidents': {
                'total': len(incidents),
                'open': len([i for i in incidents if i.status != 'resolved']),
            },
            'fairness': {
                'reports_count': len(fairness),
                'latest_score': fairness[-1].overall_score if fairness else None,
            },
            'explainability': {
                'records_count': len(explainability),
                'techniques_used': list(set(e.technique for e in explainability)),
            },
            'oversight': {
                'configured': oversight is not None,
                'type': oversight.oversight_type if oversight else None,
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
            'models_count': len(self.models),
            'high_risk_models': len([m for m in self.models.values() if m.risk_level in [RiskLevel.HIGH, RiskLevel.UNACCEPTABLE]]),
            'assessments_count': len(self.assessments),
            'bias_detected': len(self.bias_assessments),
            'fairness_reports_count': len(self.fairness_reports),
            'incidents_count': len(self.incidents),
            'open_incidents': len([i for i in self.incidents.values() if i.status != 'resolved']),
            'oversight_configured': len([o for o in self.oversight.values() if o.enabled]),
        }


def get_capabilities() -> Dict[str, Any]:
    """Return agent capabilities for orchestration."""
    return {
        'agent_type': 'ethics',
        'version': '1.0.0',
        'capabilities': [
            'register_model',
            'update_model_risk',
            'get_models',
            'create_ethics_assessment',
            'add_finding',
            'complete_assessment',
            'detect_bias',
            'create_remediation_plan',
            'mark_bias_mitigated',
            'get_bias_assessments',
            'generate_fairness_report',
            'get_fairness_reports',
            'add_explainability_record',
            'get_explainability',
            'report_incident',
            'resolve_incident',
            'get_incidents',
            'configure_oversight',
            'get_oversight_config',
            'get_ethics_report',
            'get_model_ethics_profile',
        ],
        'ethics_principles': [p.value for p in EthicsPrinciple],
        'bias_types': [t.value for t in BiasType],
        'fairness_metrics': [m.value for m in FairnessMetric],
        'risk_levels': [l.value for l in RiskLevel],
        'assessment_statuses': [s.value for s in AssessmentStatus],
    }


if __name__ == "__main__":
    agent = EthicsAgent()

    # Register model
    model = agent.register_model(
        name="Credit Scoring Model v2",
        description="ML model for creditworthiness assessment",
        model_type="classification",
        purpose="Determine loan eligibility",
        developer="ml-team@example.com",
        risk_level=RiskLevel.HIGH,
        training_data_description="Historical loan applications 2020-2024",
        tags=['finance', 'credit', 'high-risk'],
    )

    print(f"Registered model: {model.name}")

    # Create ethics assessment
    assessment = agent.create_ethics_assessment(
        model.model_id,
        assessment_type="initial",
        principles_evaluated=[EthicsPrinciple.FAIRNESS, EthicsPrinciple.NON_DISCRIMINATION],
    )

    # Add findings
    agent.add_finding(
        assessment.assessment_id,
        EthicsPrinciple.FAIRNESS,
        "Lower approval rates for certain demographics",
        RiskLevel.HIGH,
        "Investigate training data representation",
    )

    agent.complete_assessment(
        assessment.assessment_id,
        reviewer="ethics-board@example.com",
        status=AssessmentStatus.REQUIRES_REMEDIATION,
        mitigations=["Retrain with balanced data", "Add fairness constraints"],
    )

    # Detect bias
    bias = agent.detect_bias(
        model.model_id,
        bias_type=BiasType.HISTORICAL,
        affected_group="Age 18-25",
        description="Lower approval rates for young applicants",
        evidence={'approval_rate_young': 0.45, 'approval_rate_overall': 0.68},
        metric_used=FairnessMetric.DEMOGRAPHIC_PARITY,
        metric_value=0.23,
    )

    print(f"Bias detected: {bias.description}")

    # Generate fairness report
    report = agent.generate_fairness_report(
        model.model_id,
        dataset="test_2024",
        protected_attributes=['age', 'gender', 'ethnicity'],
        metrics={
            'demographic_parity': {'disparity': 0.23, 'by_group': {...}},
            'equalized_odds': {'disparity': 0.12, 'by_group': {...}},
        },
    )

    print(f"Fairness Score: {report.overall_score}/100")

    # Add explainability
    agent.add_explainability_record(
        model.model_id,
        technique="SHAP",
        explanation_type="global",
        features=[
            {'name': 'income', 'importance': 0.35},
            {'name': 'credit_history', 'importance': 0.28},
            {'name': 'debt_ratio', 'importance': 0.18},
        ],
    )

    # Configure human oversight
    agent.configure_oversight(
        model.model_id,
        oversight_type="human_in_loop",
        trigger_conditions=["Low confidence prediction", "Borderline decision", "Appeal requested"],
        reviewers=["senior-analyst@example.com"],
        escalation_path=["manager@example.com", "ethics-board@example.com"],
    )

    # Get ethics report
    report = agent.get_ethics_report()
    print(f"\nEthics Report:")
    print(f"  Total Models: {report['models']['total']}")
    print(f"  High Risk: {report['models']['high_risk_count']}")
    print(f"  Bias Detected: {report['bias']['total_detected']}")

    print(f"\nState: {agent.get_state()}")
