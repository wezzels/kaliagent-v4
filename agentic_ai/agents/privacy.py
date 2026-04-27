"""
PrivacyAgent - Data Privacy & Compliance
=========================================

Provides GDPR, CCPA, and privacy regulation compliance,
data subject rights management, consent tracking, and privacy impact assessments.
"""

import logging
import secrets
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from typing import Any, Dict, List, Optional


logger = logging.getLogger(__name__)


class PrivacyRegulation(Enum):
    """Privacy regulations."""
    GDPR = "gdpr"  # EU General Data Protection Regulation
    CCPA = "ccpa"  # California Consumer Privacy Act
    CPRA = "cpra"  # California Privacy Rights Act
    LGPD = "lgpd"  # Brazil Lei Geral de Proteção de Dados
    PIPEDA = "pipeda"  # Canada Personal Information Protection
    HIPAA = "hipaa"  # USA Health Insurance Portability
    COPPA = "coppa"  # Children's Online Privacy Protection
    VCDPA = "vcdpa"  # Virginia Consumer Data Protection


class DataSubjectRight(Enum):
    """Data subject rights."""
    ACCESS = "access"  # Right to access
    RECTIFICATION = "rectification"  # Right to correct
    ERASURE = "erasure"  # Right to delete (RTBF)
    PORTABILITY = "portability"  # Right to data portability
    RESTRICTION = "restriction"  # Right to restrict processing
    OBJECTION = "objection"  # Right to object
    WITHDRAW_CONSENT = "withdraw_consent"
    NON_DISCRIMINATION = "non_discrimination"  # CCPA specific


class RequestStatus(Enum):
    """Request status."""
    SUBMITTED = "submitted"
    VERIFIED = "verified"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    DENIED = "denied"
    APPEALED = "appealed"


class ConsentStatus(Enum):
    """Consent status."""
    GIVEN = "given"
    WITHDRAWN = "withdrawn"
    EXPIRED = "expired"
    PENDING = "pending"


class ProcessingPurpose(Enum):
    """Data processing purposes."""
    SERVICE_DELIVERY = "service_delivery"
    MARKETING = "marketing"
    ANALYTICS = "analytics"
    PERSONALIZATION = "personalization"
    LEGAL_OBLIGATION = "legal_obligation"
    LEGITIMATE_INTEREST = "legitimate_interest"
    CONSENT_BASED = "consent_based"


@dataclass
class DataSubject:
    """Data subject (individual) record."""
    subject_id: str
    name: str
    email: str
    jurisdiction: str  # EU, California, Brazil, etc.
    applicable_regulations: List[PrivacyRegulation]
    created_at: datetime = field(default_factory=datetime.utcnow)
    verified: bool = False
    data_categories: List[str] = field(default_factory=list)
    consent_records: List[str] = field(default_factory=list)
    requests_count: int = 0


@dataclass
class DataProcessingActivity:
    """Data processing activity record."""
    activity_id: str
    name: str
    description: str
    data_categories: List[str]
    purposes: List[ProcessingPurpose]
    legal_basis: str  # consent, contract, legal, legitimate interest
    data_recipients: List[str] = field(default_factory=list)
    retention_period: int = 0  # days
    retention_unit: str = "days"  # days, months, years
    cross_border_transfer: bool = False
    transfer_mechanisms: List[str] = field(default_factory=list)  # SCCs, adequacy, etc.
    risk_level: str = "low"  # low, medium, high
    created_at: datetime = field(default_factory=datetime.utcnow)


@dataclass
class DataSubjectRequest:
    """Data subject rights request."""
    request_id: str
    subject_id: str
    right_type: DataSubjectRight
    status: RequestStatus
    submitted_at: datetime
    deadline: datetime
    verified_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    response_data: Optional[Dict[str, Any]] = None
    denial_reason: Optional[str] = None
    assigned_to: Optional[str] = None
    notes: List[str] = field(default_factory=list)


@dataclass
class ConsentRecord:
    """Consent record."""
    consent_id: str
    subject_id: str
    purpose: ProcessingPurpose
    status: ConsentStatus
    given_at: Optional[datetime] = None
    withdrawn_at: Optional[datetime] = None
    expires_at: Optional[datetime] = None
    method: str = ""  # web_form, api, verbal, written
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None
    version: str = "1.0"


@dataclass
class PrivacyImpactAssessment:
    """Privacy Impact Assessment (PIA/DPIA)."""
    pia_id: str
    name: str
    project_description: str
    status: str  # draft, in_review, approved, rejected
    risk_level: str = "pending"
    data_categories: List[str] = field(default_factory=list)
    processing_purposes: List[ProcessingPurpose] = field(default_factory=list)
    risks_identified: List[Dict[str, Any]] = field(default_factory=list)
    mitigations: List[str] = field(default_factory=list)
    dpo_review: bool = False
    approved_at: Optional[datetime] = None
    created_at: datetime = field(default_factory=datetime.utcnow)


@dataclass
class DataBreach:
    """Data breach record."""
    breach_id: str
    title: str
    description: str
    severity: str  # low, medium, high, critical
    status: str  # detected, contained, investigating, notified, closed
    detected_at: datetime
    contained_at: Optional[datetime] = None
    affected_subjects: int = 0
    data_categories: List[str] = field(default_factory=list)
    root_cause: str = ""
    notification_required: bool = False
    notified_authority: Optional[datetime] = None
    notified_subjects: Optional[datetime] = None
    remediation: List[str] = field(default_factory=list)


class PrivacyAgent:
    """
    Privacy Agent for GDPR, CCPA, and privacy regulation compliance,
    data subject rights, consent management, and privacy assessments.
    """

    def __init__(self, agent_id: str = "privacy-agent"):
        self.agent_id = agent_id
        self.data_subjects: Dict[str, DataSubject] = {}
        self.processing_activities: Dict[str, DataProcessingActivity] = {}
        self.requests: Dict[str, DataSubjectRequest] = {}
        self.consent_records: Dict[str, ConsentRecord] = {}
        self.pias: Dict[str, PrivacyImpactAssessment] = {}
        self.breaches: Dict[str, DataBreach] = {}

        # Regulatory requirements
        self.regulation_requirements = self._init_regulation_requirements()

        # Default retention policies
        self.retention_policies = {
            'customer_data': {'period': 730, 'unit': 'days'},  # 2 years
            'marketing_data': {'period': 365, 'unit': 'days'},  # 1 year
            'analytics_data': {'period': 90, 'unit': 'days'},  # 90 days
            'logs': {'period': 30, 'unit': 'days'},  # 30 days
        }

    def _init_regulation_requirements(self) -> Dict[str, Dict[str, Any]]:
        """Initialize regulatory requirements."""
        return {
            PrivacyRegulation.GDPR.value: {
                'jurisdiction': 'EU',
                'response_days': 30,
                'rights': [
                    DataSubjectRight.ACCESS,
                    DataSubjectRight.RECTIFICATION,
                    DataSubjectRight.ERASURE,
                    DataSubjectRight.PORTABILITY,
                    DataSubjectRight.RESTRICTION,
                    DataSubjectRight.OBJECTION,
                    DataSubjectRight.WITHDRAW_CONSENT,
                ],
                'breach_notification_hours': 72,
                'dpo_required': True,
            },
            PrivacyRegulation.CCPA.value: {
                'jurisdiction': 'California, USA',
                'response_days': 45,
                'rights': [
                    DataSubjectRight.ACCESS,
                    DataSubjectRight.DELETION,
                    DataSubjectRight.PORTABILITY,
                    DataSubjectRight.OBJECTION,
                    DataSubjectRight.NON_DISCRIMINATION,
                ],
                'breach_notification': 'expedited',
                'opt_out_required': True,
            },
            PrivacyRegulation.LGPD.value: {
                'jurisdiction': 'Brazil',
                'response_days': 15,
                'rights': [
                    DataSubjectRight.ACCESS,
                    DataSubjectRight.RECTIFICATION,
                    DataSubjectRight.ERASURE,
                    DataSubjectRight.PORTABILITY,
                ],
            },
            PrivacyRegulation.HIPAA.value: {
                'jurisdiction': 'USA',
                'response_days': 30,
                'phi_protection': True,
                'breach_notification_days': 60,
            },
        }

    # ============================================
    # Data Subject Management
    # ============================================

    def register_data_subject(
        self,
        name: str,
        email: str,
        jurisdiction: str,
        applicable_regulations: Optional[List[PrivacyRegulation]] = None,
    ) -> DataSubject:
        """Register a data subject."""
        subject = DataSubject(
            subject_id=self._generate_id("subj"),
            name=name,
            email=email,
            jurisdiction=jurisdiction,
            applicable_regulations=applicable_regulations or [],
        )

        self.data_subjects[subject.subject_id] = subject
        return subject

    def verify_data_subject(self, subject_id: str, verification_method: str) -> bool:
        """Verify data subject identity."""
        if subject_id not in self.data_subjects:
            return False

        self.data_subjects[subject_id].verified = True
        return True

    def get_data_subject(self, subject_id: str) -> Optional[DataSubject]:
        """Get data subject by ID."""
        return self.data_subjects.get(subject_id)

    def get_data_subjects(
        self,
        jurisdiction: Optional[str] = None,
        regulation: Optional[PrivacyRegulation] = None,
    ) -> List[DataSubject]:
        """Get data subjects with filtering."""
        subjects = list(self.data_subjects.values())

        if jurisdiction:
            subjects = [s for s in subjects if s.jurisdiction == jurisdiction]

        if regulation:
            subjects = [s for s in subjects if regulation in s.applicable_regulations]

        return subjects

    # ============================================
    # Data Subject Rights Requests
    # ============================================

    def create_request(
        self,
        subject_id: str,
        right_type: DataSubjectRight,
        assigned_to: Optional[str] = None,
    ) -> DataSubjectRequest:
        """Create a data subject rights request."""
        if subject_id not in self.data_subjects:
            raise ValueError(f"Data subject {subject_id} not found")

        subject = self.data_subjects[subject_id]

        # Determine deadline based on regulations
        deadline_days = 30  # Default
        for reg in subject.applicable_regulations:
            req = self.regulation_requirements.get(reg.value, {})
            if 'response_days' in req:
                deadline_days = max(deadline_days, req['response_days'])

        request = DataSubjectRequest(
            request_id=self._generate_id("req"),
            subject_id=subject_id,
            right_type=right_type,
            status=RequestStatus.SUBMITTED,
            submitted_at=datetime.utcnow(),
            deadline=datetime.utcnow() + timedelta(days=deadline_days),
            assigned_to=assigned_to,
        )

        self.requests[request.request_id] = request
        subject.requests_count += 1

        logger.info(f"Created {right_type.value} request for {subject.email}")
        return request

    def verify_request(self, request_id: str) -> bool:
        """Verify a request (identity verification complete)."""
        if request_id not in self.requests:
            return False

        request = self.requests[request_id]
        request.status = RequestStatus.VERIFIED
        request.verified_at = datetime.utcnow()

        return True

    def update_request_status(
        self,
        request_id: str,
        status: RequestStatus,
        response_data: Optional[Dict[str, Any]] = None,
        denial_reason: Optional[str] = None,
    ) -> bool:
        """Update request status."""
        if request_id not in self.requests:
            return False

        request = self.requests[request_id]
        request.status = status

        if response_data:
            request.response_data = response_data

        if denial_reason:
            request.denial_reason = denial_reason

        if status == RequestStatus.COMPLETED:
            request.completed_at = datetime.utcnow()

        return True

    def get_requests(
        self,
        subject_id: Optional[str] = None,
        status: Optional[RequestStatus] = None,
        right_type: Optional[DataSubjectRight] = None,
        overdue_only: bool = False,
    ) -> List[DataSubjectRequest]:
        """Get requests with filtering."""
        requests = list(self.requests.values())

        if subject_id:
            requests = [r for r in requests if r.subject_id == subject_id]

        if status:
            requests = [r for r in requests if r.status == status]

        if right_type:
            requests = [r for r in requests if r.right_type == right_type]

        if overdue_only:
            now = datetime.utcnow()
            requests = [r for r in requests if r.deadline < now and r.status != RequestStatus.COMPLETED]

        return requests

    def fulfill_access_request(self, request_id: str, data: Dict[str, Any]) -> bool:
        """Fulfill an access request with data export."""
        if request_id not in self.requests:
            return False

        request = self.requests[request_id]

        if request.right_type != DataSubjectRight.ACCESS:
            return False

        return self.update_request_status(
            request_id,
            RequestStatus.COMPLETED,
            response_data={
                'export_format': 'json',
                'data_categories': list(data.keys()),
                'export_timestamp': datetime.utcnow().isoformat(),
                'data': data,
            },
        )

    def fulfill_erasure_request(self, request_id: str, systems_cleared: List[str]) -> bool:
        """Fulfill an erasure (deletion) request."""
        if request_id not in self.requests:
            return False

        request = self.requests[request_id]

        if request.right_type != DataSubjectRight.ERASURE:
            return False

        return self.update_request_status(
            request_id,
            RequestStatus.COMPLETED,
            response_data={
                'systems_cleared': systems_cleared,
                'deletion_timestamp': datetime.utcnow().isoformat(),
            },
        )

    # ============================================
    # Consent Management
    # ============================================

    def record_consent(
        self,
        subject_id: str,
        purpose: ProcessingPurpose,
        method: str,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None,
        expires_in_days: Optional[int] = None,
    ) -> ConsentRecord:
        """Record consent given."""
        consent = ConsentRecord(
            consent_id=self._generate_id("consent"),
            subject_id=subject_id,
            purpose=purpose,
            status=ConsentStatus.GIVEN,
            given_at=datetime.utcnow(),
            method=method,
            ip_address=ip_address,
            user_agent=user_agent,
            version="1.0",
        )

        if expires_in_days:
            consent.expires_at = datetime.utcnow() + timedelta(days=expires_in_days)

        self.consent_records[consent.consent_id] = consent

        if subject_id in self.data_subjects:
            self.data_subjects[subject_id].consent_records.append(consent.consent_id)

        return consent

    def withdraw_consent(self, consent_id: str) -> bool:
        """Withdraw consent."""
        if consent_id not in self.consent_records:
            return False

        consent = self.consent_records[consent_id]
        consent.status = ConsentStatus.WITHDRAWN
        consent.withdrawn_at = datetime.utcnow()

        return True

    def get_consents(
        self,
        subject_id: Optional[str] = None,
        purpose: Optional[ProcessingPurpose] = None,
        status: Optional[ConsentStatus] = None,
    ) -> List[ConsentRecord]:
        """Get consent records with filtering."""
        consents = list(self.consent_records.values())

        if subject_id:
            consents = [c for c in consents if c.subject_id == subject_id]

        if purpose:
            consents = [c for c in consents if c.purpose == purpose]

        if status:
            consents = [c for c in consents if c.status == status]

        return consents

    def check_valid_consent(self, subject_id: str, purpose: ProcessingPurpose) -> bool:
        """Check if valid consent exists for a purpose."""
        consents = self.get_consents(
            subject_id=subject_id,
            purpose=purpose,
            status=ConsentStatus.GIVEN,
        )

        now = datetime.utcnow()

        for consent in consents:
            # Check if not expired
            if consent.expires_at and consent.expires_at < now:
                continue
            return True

        return False

    # ============================================
    # Processing Activities (ROPA)
    # ============================================

    def add_processing_activity(
        self,
        name: str,
        description: str,
        data_categories: List[str],
        purposes: List[ProcessingPurpose],
        legal_basis: str,
        retention_days: int,
        data_recipients: Optional[List[str]] = None,
        cross_border: bool = False,
        risk_level: str = "low",
    ) -> DataProcessingActivity:
        """Add a processing activity (Record of Processing Activities)."""
        activity = DataProcessingActivity(
            activity_id=self._generate_id("ropa"),
            name=name,
            description=description,
            data_categories=data_categories,
            purposes=purposes,
            legal_basis=legal_basis,
            retention_period=retention_days,
            data_recipients=data_recipients or [],
            cross_border_transfer=cross_border,
            risk_level=risk_level,
        )

        self.processing_activities[activity.activity_id] = activity
        return activity

    def get_processing_activities(
        self,
        risk_level: Optional[str] = None,
        purpose: Optional[ProcessingPurpose] = None,
    ) -> List[DataProcessingActivity]:
        """Get processing activities with filtering."""
        activities = list(self.processing_activities.values())

        if risk_level:
            activities = [a for a in activities if a.risk_level == risk_level]

        if purpose:
            activities = [a for a in activities if purpose in a.purposes]

        return activities

    # ============================================
    # Privacy Impact Assessments
    # ============================================

    def create_pia(
        self,
        name: str,
        project_description: str,
        data_categories: List[str],
        processing_purposes: List[ProcessingPurpose],
    ) -> PrivacyImpactAssessment:
        """Create a Privacy Impact Assessment."""
        pia = PrivacyImpactAssessment(
            pia_id=self._generate_id("pia"),
            name=name,
            project_description=project_description,
            status="draft",
            data_categories=data_categories,
            processing_purposes=processing_purposes,
        )

        self.pias[pia.pia_id] = pia
        return pia

    def add_risk_to_pia(
        self,
        pia_id: str,
        risk_description: str,
        likelihood: str,  # low, medium, high
        impact: str,  # low, medium, high
        mitigations: Optional[List[str]] = None,
    ) -> bool:
        """Add identified risk to PIA."""
        if pia_id not in self.pias:
            return False

        pia = self.pias[pia_id]

        risk_score = {'low': 1, 'medium': 2, 'high': 3}
        overall_score = risk_score.get(likelihood, 1) * risk_score.get(impact, 1)

        pia.risks_identified.append({
            'description': risk_description,
            'likelihood': likelihood,
            'impact': impact,
            'risk_score': overall_score,
            'mitigations': mitigations or [],
            'identified_at': datetime.utcnow().isoformat(),
        })

        # Update overall risk level
        max_score = max(r.get('risk_score', 0) for r in pia.risks_identified)
        if max_score >= 6:
            pia.risk_level = "high"
        elif max_score >= 3:
            pia.risk_level = "medium"
        else:
            pia.risk_level = "low"

        return True

    def approve_pia(self, pia_id: str, dpo_reviewed: bool = True) -> bool:
        """Approve a PIA."""
        if pia_id not in self.pias:
            return False

        pia = self.pias[pia_id]
        pia.status = "approved"
        pia.dpo_review = dpo_reviewed
        pia.approved_at = datetime.utcnow()

        return True

    def get_pias(self, status: Optional[str] = None) -> List[PrivacyImpactAssessment]:
        """Get PIAs with filtering."""
        pias = list(self.pias.values())

        if status:
            pias = [p for p in pias if p.status == status]

        return pias

    # ============================================
    # Data Breach Management
    # ============================================

    def report_breach(
        self,
        title: str,
        description: str,
        severity: str,
        affected_subjects: int,
        data_categories: List[str],
    ) -> DataBreach:
        """Report a data breach."""
        breach = DataBreach(
            breach_id=self._generate_id("breach"),
            title=title,
            description=description,
            severity=severity,
            status="detected",
            detected_at=datetime.utcnow(),
            affected_subjects=affected_subjects,
            data_categories=data_categories,
        )

        self.breaches[breach.breach_id] = breach

        # Determine if notification required
        if severity in ['high', 'critical']:
            breach.notification_required = True

        logger.warning(f"Data breach reported: {breach.title}")
        return breach

    def contain_breach(self, breach_id: str) -> bool:
        """Mark breach as contained."""
        if breach_id not in self.breaches:
            return False

        breach = self.breaches[breach_id]
        breach.status = "contained"
        breach.contained_at = datetime.utcnow()

        return True

    def notify_authority(self, breach_id: str, authority: str) -> bool:
        """Record authority notification."""
        if breach_id not in self.breaches:
            return False

        breach = self.breaches[breach_id]
        breach.notified_authority = datetime.utcnow()

        if breach.status == "contained":
            breach.status = "notified"

        return True

    def close_breach(
        self,
        breach_id: str,
        root_cause: str,
        remediation: List[str],
    ) -> bool:
        """Close a breach with full documentation."""
        if breach_id not in self.breaches:
            return False

        breach = self.breaches[breach_id]
        breach.status = "closed"
        breach.root_cause = root_cause
        breach.remediation = remediation

        return True

    def get_breaches(
        self,
        severity: Optional[str] = None,
        status: Optional[str] = None,
    ) -> List[DataBreach]:
        """Get breaches with filtering."""
        breaches = list(self.breaches.values())

        if severity:
            breaches = [b for b in breaches if b.severity == severity]

        if status:
            breaches = [b for b in breaches if b.status == status]

        return breaches

    # ============================================
    # Compliance Reporting
    # ============================================

    def get_compliance_report(self) -> Dict[str, Any]:
        """Generate privacy compliance report."""
        subjects = list(self.data_subjects.values())
        requests = list(self.requests.values())
        consents = list(self.consent_records.values())
        breaches = list(self.breaches.values())
        pias = list(self.pias.values())

        # Request metrics
        by_status = {}
        for status in RequestStatus:
            by_status[status.value] = len([r for r in requests if r.status == status])

        overdue = len([r for r in requests if r.deadline < datetime.utcnow() and r.status != RequestStatus.COMPLETED])

        # Consent metrics
        active_consents = len([c for c in consents if c.status == ConsentStatus.GIVEN])
        withdrawn = len([c for c in consents if c.status == ConsentStatus.WITHDRAWN])

        # Breach metrics
        breaches_this_year = len([
            b for b in breaches
            if b.detected_at.year == datetime.utcnow().year
        ])

        return {
            'data_subjects': {
                'total': len(subjects),
                'verified': len([s for s in subjects if s.verified]),
                'by_jurisdiction': self._group_by_field(subjects, 'jurisdiction'),
            },
            'requests': {
                'total': len(requests),
                'by_status': by_status,
                'overdue': overdue,
                'completion_rate': round(
                    by_status.get('completed', 0) / len(requests) * 100, 1
                ) if requests else 0,
            },
            'consents': {
                'total': len(consents),
                'active': active_consents,
                'withdrawn': withdrawn,
            },
            'breaches': {
                'total': len(breaches),
                'this_year': breaches_this_year,
                'notification_required': len([b for b in breaches if b.notification_required]),
            },
            'pias': {
                'total': len(pias),
                'approved': len([p for p in pias if p.status == 'approved']),
                'high_risk': len([p for p in pias if p.risk_level == 'high']),
            },
            'processing_activities': len(self.processing_activities),
        }

    def _group_by_field(self, items: List[Any], field: str) -> Dict[str, int]:
        """Group items by a field."""
        result = {}
        for item in items:
            value = getattr(item, field, 'unknown')
            result[value] = result.get(value, 0) + 1
        return result

    def get_regulation_compliance(self, regulation: PrivacyRegulation) -> Dict[str, Any]:
        """Get compliance status for a specific regulation."""
        req = self.regulation_requirements.get(regulation.value, {})

        subjects = [
            s for s in self.data_subjects.values()
            if regulation in s.applicable_regulations
        ]

        requests = [
            r for r in self.requests.values()
            if any(
                s.subject_id == r.subject_id and regulation in s.applicable_regulations
                for s in subjects
            )
        ]

        overdue = len([r for r in requests if r.deadline < datetime.utcnow() and r.status != RequestStatus.COMPLETED])

        return {
            'regulation': regulation.value,
            'jurisdiction': req.get('jurisdiction', 'Unknown'),
            'data_subjects': len(subjects),
            'requests': {
                'total': len(requests),
                'overdue': overdue,
                'compliant': overdue == 0,
            },
            'response_deadline_days': req.get('response_days', 30),
            'breach_notification': req.get('breach_notification_hours', req.get('breach_notification_days', 'N/A')),
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
            'data_subjects_count': len(self.data_subjects),
            'requests_count': len(self.requests),
            'pending_requests': len([r for r in self.requests.values() if r.status != RequestStatus.COMPLETED]),
            'consents_count': len(self.consent_records),
            'active_consents': len([c for c in self.consent_records.values() if c.status == ConsentStatus.GIVEN]),
            'processing_activities_count': len(self.processing_activities),
            'pias_count': len(self.pias),
            'breaches_count': len(self.breaches),
            'open_breaches': len([b for b in self.breaches.values() if b.status != 'closed']),
        }


def get_capabilities() -> Dict[str, Any]:
    """Return agent capabilities for orchestration."""
    return {
        'agent_type': 'privacy',
        'version': '1.0.0',
        'capabilities': [
            'register_data_subject',
            'verify_data_subject',
            'get_data_subjects',
            'create_request',
            'verify_request',
            'update_request_status',
            'get_requests',
            'fulfill_access_request',
            'fulfill_erasure_request',
            'record_consent',
            'withdraw_consent',
            'get_consents',
            'check_valid_consent',
            'add_processing_activity',
            'get_processing_activities',
            'create_pia',
            'add_risk_to_pia',
            'approve_pia',
            'get_pias',
            'report_breach',
            'contain_breach',
            'notify_authority',
            'close_breach',
            'get_breaches',
            'get_compliance_report',
            'get_regulation_compliance',
        ],
        'regulations': [r.value for r in PrivacyRegulation],
        'data_subject_rights': [r.value for r in DataSubjectRight],
        'request_statuses': [s.value for s in RequestStatus],
        'consent_statuses': [s.value for s in ConsentStatus],
        'processing_purposes': [p.value for p in ProcessingPurpose],
    }


if __name__ == "__main__":
    agent = PrivacyAgent()

    # Register data subject
    subject = agent.register_data_subject(
        name="John Doe",
        email="john@example.com",
        jurisdiction="EU",
        applicable_regulations=[PrivacyRegulation.GDPR],
    )

    print(f"Registered data subject: {subject.name}")

    # Record consent
    consent = agent.record_consent(
        subject_id=subject.subject_id,
        purpose=ProcessingPurpose.MARKETING,
        method="web_form",
        ip_address="192.168.1.100",
        expires_in_days=365,
    )

    print(f"Recorded consent: {consent.purpose.value}")

    # Create access request
    request = agent.create_request(
        subject_id=subject.subject_id,
        right_type=DataSubjectRight.ACCESS,
        assigned_to="privacy@example.com",
    )

    print(f"Created request: {request.right_type.value} (due: {request.deadline})")

    # Fulfill request
    agent.fulfill_access_request(
        request.request_id,
        data={'profile': {...}, 'orders': [...], 'preferences': {...}},
    )

    # Add processing activity
    activity = agent.add_processing_activity(
        name="Customer Analytics",
        description="Analyze customer behavior for insights",
        data_categories=['behavioral', 'transactional', 'device'],
        purposes=[ProcessingPurpose.ANALYTICS],
        legal_basis="legitimate_interest",
        retention_days=365,
        risk_level="medium",
    )

    print(f"Added processing activity: {activity.name}")

    # Create PIA
    pia = agent.create_pia(
        name="AI Recommendation System",
        project_description="ML-based product recommendations",
        data_categories=['purchase_history', 'browsing', 'preferences'],
        processing_purposes=[ProcessingPurpose.PERSONALIZATION],
    )

    agent.add_risk_to_pia(
        pia.pia_id,
        "Potential profiling discrimination",
        likelihood="medium",
        impact="high",
        mitigations=["Bias testing", "Human review", "Opt-out available"],
    )

    print(f"Created PIA: {pia.name} (risk: {pia.risk_level})")

    # Report breach
    breach = agent.report_breach(
        title="Email List Exposure",
        description="Customer emails exposed via misconfigured API",
        severity="high",
        affected_subjects=5000,
        data_categories=['email', 'names'],
    )

    agent.contain_breach(breach.breach_id)
    agent.notify_authority(breach.breach_id, "ICO")

    print(f"Reported breach: {breach.title}")

    # Get compliance report
    report = agent.get_compliance_report()
    print(f"\nCompliance Report:")
    print(f"  Data Subjects: {report['data_subjects']['total']}")
    print(f"  Requests (overdue): {report['requests']['overdue']}")
    print(f"  Active Consents: {report['consents']['active']}")
    print(f"  Breaches (this year): {report['breaches']['this_year']}")

    print(f"\nState: {agent.get_state()}")
