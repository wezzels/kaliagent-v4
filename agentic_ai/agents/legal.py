"""
LegalAgent - Legal & Compliance
================================

Provides contract review, legal document generation, compliance checking,
risk assessment, and regulatory tracking.
"""

import logging
import secrets
import re
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from typing import Any, Dict, List, Optional


logger = logging.getLogger(__name__)


class DocumentType(Enum):
    """Legal document types."""
    CONTRACT = "contract"
    NDA = "nda"
    TERMS_OF_SERVICE = "terms_of_service"
    PRIVACY_POLICY = "privacy_policy"
    EMPLOYMENT_AGREEMENT = "employment_agreement"
    VENDOR_AGREEMENT = "vendor_agreement"
    LICENSE = "license"
    COMPLIANCE_REPORT = "compliance_report"


class RiskLevel(Enum):
    """Risk assessment levels."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class ComplianceStatus(Enum):
    """Compliance status."""
    COMPLIANT = "compliant"
    PARTIALLY_COMPLIANT = "partially_compliant"
    NON_COMPLIANT = "non_compliant"
    REVIEW_REQUIRED = "review_required"


class Regulation(Enum):
    """Regulations to track."""
    GDPR = "gdpr"
    CCPA = "ccpa"
    HIPAA = "hipaa"
    SOC2 = "soc2"
    ISO27001 = "iso27001"
    PCI_DSS = "pci_dss"


@dataclass
class LegalDocument:
    """Legal document."""
    document_id: str
    title: str
    document_type: DocumentType
    status: str  # draft, review, approved, executed, expired
    parties: List[str]
    effective_date: Optional[datetime] = None
    expiration_date: Optional[datetime] = None
    value: float = 0.0
    clauses: List[Dict[str, Any]] = field(default_factory=list)
    risks: List[Dict[str, Any]] = field(default_factory=list)
    created_at: datetime = field(default_factory=datetime.utcnow)


@dataclass
class ComplianceCheck:
    """Compliance check result."""
    check_id: str
    regulation: Regulation
    status: ComplianceStatus
    findings: List[str]
    recommendations: List[str]
    checked_at: datetime = field(default_factory=datetime.utcnow)
    next_review: Optional[datetime] = None


@dataclass
class ContractClause:
    """Contract clause analysis."""
    clause_id: str
    clause_type: str
    text: str
    risk_level: RiskLevel
    notes: str = ""
    suggested_changes: List[str] = field(default_factory=list)


class LegalAgent:
    """
    Legal Agent for contract review, document generation,
    compliance checking, and risk assessment.
    """

    def __init__(self, agent_id: str = "legal-agent"):
        self.agent_id = agent_id
        self.documents: Dict[str, LegalDocument] = {}
        self.compliance_checks: Dict[str, ComplianceCheck] = {}
        self.regulations: Dict[Regulation, Dict[str, Any]] = {}
        self.clause_library: Dict[str, ContractClause] = {}

        # Initialize regulation tracking
        self._init_regulations()

        # Common contract clauses
        self._init_clause_library()

    def _init_regulations(self):
        """Initialize regulation tracking."""
        self.regulations = {
            Regulation.GDPR: {
                'name': 'General Data Protection Regulation',
                'region': 'EU',
                'last_audit': None,
                'status': ComplianceStatus.REVIEW_REQUIRED,
            },
            Regulation.CCPA: {
                'name': 'California Consumer Privacy Act',
                'region': 'California, USA',
                'last_audit': None,
                'status': ComplianceStatus.REVIEW_REQUIRED,
            },
            Regulation.HIPAA: {
                'name': 'Health Insurance Portability and Accountability Act',
                'region': 'USA',
                'last_audit': None,
                'status': ComplianceStatus.REVIEW_REQUIRED,
            },
            Regulation.SOC2: {
                'name': 'Service Organization Control 2',
                'region': 'Global',
                'last_audit': None,
                'status': ComplianceStatus.REVIEW_REQUIRED,
            },
        }

    def _init_clause_library(self):
        """Initialize clause library."""
        self.clause_library = {
            'termination': ContractClause(
                clause_id='clause-termination',
                clause_type='termination',
                text='Either party may terminate this agreement with 30 days written notice.',
                risk_level=RiskLevel.LOW,
            ),
            'liability': ContractClause(
                clause_id='clause-liability',
                clause_type='liability',
                text='Liability shall be limited to the total amount paid under this agreement.',
                risk_level=RiskLevel.MEDIUM,
            ),
            'indemnification': ContractClause(
                clause_id='clause-indemnification',
                clause_type='indemnification',
                text='Each party agrees to indemnify the other against third-party claims.',
                risk_level=RiskLevel.HIGH,
            ),
            'confidentiality': ContractClause(
                clause_id='clause-confidentiality',
                clause_type='confidentiality',
                text='Both parties agree to keep all confidential information secret.',
                risk_level=RiskLevel.LOW,
            ),
        }

    # ============================================
    # Document Management
    # ============================================

    def create_document(
        self,
        title: str,
        document_type: DocumentType,
        parties: List[str],
        effective_date: Optional[datetime] = None,
        expiration_date: Optional[datetime] = None,
        value: float = 0.0,
    ) -> LegalDocument:
        """Create a legal document."""
        doc = LegalDocument(
            document_id=self._generate_id("doc"),
            title=title,
            document_type=document_type,
            status="draft",
            parties=parties,
            effective_date=effective_date,
            expiration_date=expiration_date,
            value=value,
        )

        self.documents[doc.document_id] = doc
        logger.info(f"Created document: {doc.title}")
        return doc

    def update_document_status(
        self,
        document_id: str,
        status: str,
    ) -> Optional[LegalDocument]:
        """Update document status."""
        if document_id not in self.documents:
            return None

        doc = self.documents[document_id]
        doc.status = status

        return doc

    def get_documents(
        self,
        document_type: Optional[DocumentType] = None,
        status: Optional[str] = None,
    ) -> List[LegalDocument]:
        """Get documents with filtering."""
        docs = list(self.documents.values())

        if document_type:
            docs = [d for d in docs if d.document_type == document_type]

        if status:
            docs = [d for d in docs if d.status == status]

        return docs

    def get_expiring_documents(self, days_ahead: int = 30) -> List[LegalDocument]:
        """Get documents expiring within specified days."""
        threshold = datetime.utcnow() + timedelta(days=days_ahead)
        expiring = []

        for doc in self.documents.values():
            if doc.expiration_date and doc.expiration_date <= threshold:
                if doc.status not in ['expired', 'executed']:
                    expiring.append(doc)

        return expiring

    # ============================================
    # Contract Review
    # ============================================

    def review_contract(
        self,
        document_id: str,
        contract_text: str,
    ) -> Dict[str, Any]:
        """Review contract for risks and issues."""
        if document_id not in self.documents:
            return {'error': 'Document not found'}

        doc = self.documents[document_id]
        risks = []
        issues = []

        # Check for common risk patterns
        risk_patterns = {
            'unlimited_liability': r'unlimited.*liability|liability.*unlimited',
            'auto_renewal': r'automatically.*renew|renew.*automatically',
            'exclusive': r'exclusive.*basis|sole.*provider',
            'penalty': r'penalty.*fee|liquidated.*damages',
            'one_sided_termination': r'terminate.*immediately|terminate.*without.*notice',
        }

        for risk_name, pattern in risk_patterns.items():
            if re.search(pattern, contract_text, re.IGNORECASE):
                risks.append({
                    'type': risk_name,
                    'severity': 'high' if risk_name in ['unlimited_liability', 'penalty'] else 'medium',
                    'description': f"Detected {risk_name.replace('_', ' ')} clause",
                })

        # Check for missing standard clauses
        standard_clauses = ['termination', 'confidentiality', 'liability', 'governing_law']
        for clause in standard_clauses:
            if clause not in contract_text.lower():
                issues.append(f"Missing standard clause: {clause}")

        # Update document with findings
        doc.risks = risks

        review_result = {
            'document_id': document_id,
            'risks_found': len(risks),
            'issues_found': len(issues),
            'risks': risks,
            'issues': issues,
            'overall_risk': self._calculate_overall_risk(risks),
        }

        logger.info(f"Reviewed contract {document_id}: {len(risks)} risks found")
        return review_result

    def _calculate_overall_risk(self, risks: List[Dict[str, Any]]) -> RiskLevel:
        """Calculate overall risk level."""
        if not risks:
            return RiskLevel.LOW

        high_risks = [r for r in risks if r.get('severity') == 'high']

        if high_risks:
            return RiskLevel.HIGH
        elif len(risks) >= 3:
            return RiskLevel.MEDIUM
        else:
            return RiskLevel.LOW

    def add_clause_to_document(
        self,
        document_id: str,
        clause_type: str,
        clause_text: str,
    ) -> bool:
        """Add clause to document."""
        if document_id not in self.documents:
            return False

        doc = self.documents[document_id]
        doc.clauses.append({
            'type': clause_type,
            'text': clause_text,
            'added_at': datetime.utcnow().isoformat(),
        })

        return True

    # ============================================
    # Compliance
    # ============================================

    def run_compliance_check(
        self,
        regulation: Regulation,
        checklist: List[Dict[str, Any]],
    ) -> ComplianceCheck:
        """Run compliance check against regulation."""
        findings = []
        recommendations = []
        non_compliant = 0

        for item in checklist:
            if not item.get('compliant', False):
                non_compliant += 1
                findings.append(item.get('finding', f"Non-compliant: {item.get('requirement')}"))
                if item.get('recommendation'):
                    recommendations.append(item['recommendation'])

        # Determine status
        if non_compliant == 0:
            status = ComplianceStatus.COMPLIANT
        elif non_compliant <= len(checklist) * 0.2:
            status = ComplianceStatus.PARTIALLY_COMPLIANT
        else:
            status = ComplianceStatus.NON_COMPLIANT

        check = ComplianceCheck(
            check_id=self._generate_id("compliance"),
            regulation=regulation,
            status=status,
            findings=findings,
            recommendations=recommendations,
            next_review=datetime.utcnow() + timedelta(days=90),
        )

        self.compliance_checks[check.check_id] = check

        # Update regulation status
        if regulation in self.regulations:
            self.regulations[regulation]['status'] = status
            self.regulations[regulation]['last_audit'] = datetime.utcnow()

        logger.info(f"Compliance check {regulation.value}: {status.value}")
        return check

    def get_compliance_status(self) -> Dict[str, Any]:
        """Get overall compliance status."""
        status = {
            'regulations': {},
            'recent_checks': [],
            'overall_status': ComplianceStatus.REVIEW_REQUIRED,
        }

        for reg, info in self.regulations.items():
            status['regulations'][reg.value] = {
                'name': info['name'],
                'region': info['region'],
                'status': info['status'].value,
                'last_audit': info['last_audit'].isoformat() if info['last_audit'] else None,
            }

        # Get recent checks
        recent = sorted(
            self.compliance_checks.values(),
            key=lambda x: x.checked_at,
            reverse=True,
        )[:5]

        status['recent_checks'] = [
            {
                'regulation': c.regulation.value,
                'status': c.status.value,
                'findings_count': len(c.findings),
                'checked_at': c.checked_at.isoformat(),
            }
            for c in recent
        ]

        return status

    # ============================================
    # Document Templates
    # ============================================

    def generate_nda_template(
        self,
        disclosing_party: str,
        receiving_party: str,
        effective_date: datetime,
    ) -> str:
        """Generate NDA template."""
        template = f"""
NON-DISCLOSURE AGREEMENT

This Non-Disclosure Agreement ("Agreement") is entered into as of {effective_date.strftime('%Y-%m-%d')}

BETWEEN:
{disclosing_party} ("Disclosing Party")

AND:
{receiving_party} ("Receiving Party")

1. CONFIDENTIAL INFORMATION
The Receiving Party agrees to keep all Confidential Information secret and confidential.

2. OBLIGATIONS
The Receiving Party shall:
a) Hold Confidential Information in strict confidence
b) Not disclose to any third parties
c) Use solely for the Purpose

3. TERM
This Agreement shall remain in effect for 2 years from the Effective Date.

4. GOVERNING LAW
This Agreement shall be governed by applicable law.

IN WITNESS WHEREOF, the parties have executed this Agreement.
"""
        return template

    def generate_terms_template(self, company_name: str, effective_date: datetime) -> str:
        """Generate Terms of Service template."""
        template = f"""
TERMS OF SERVICE

Effective Date: {effective_date.strftime('%Y-%m-%d')}

1. ACCEPTANCE OF TERMS
By accessing {company_name}'s services, you agree to these Terms.

2. SERVICES
{company_name} provides services as described on our website.

3. USER OBLIGATIONS
Users agree to use services lawfully and not interfere with operations.

4. PRIVACY
Our Privacy Policy governs data collection and use.

5. LIMITATION OF LIABILITY
Liability is limited as permitted by law.

6. TERMINATION
We reserve the right to terminate accounts for violations.

7. GOVERNING LAW
These Terms are governed by applicable law.
"""
        return template

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
            'documents_count': len(self.documents),
            'compliance_checks_count': len(self.compliance_checks),
            'expiring_documents': len(self.get_expiring_documents(days_ahead=30)),
            'regulations_tracked': len(self.regulations),
        }


def get_capabilities() -> Dict[str, Any]:
    """Return agent capabilities for orchestration."""
    return {
        'agent_type': 'legal',
        'version': '1.0.0',
        'capabilities': [
            'create_document',
            'update_document_status',
            'get_documents',
            'get_expiring_documents',
            'review_contract',
            'add_clause_to_document',
            'run_compliance_check',
            'get_compliance_status',
            'generate_nda_template',
            'generate_terms_template',
        ],
        'document_types': [t.value for t in DocumentType],
        'risk_levels': [l.value for l in RiskLevel],
        'compliance_statuses': [s.value for s in ComplianceStatus],
        'regulations': [r.value for r in Regulation],
    }


if __name__ == "__main__":
    # Quick test
    agent = LegalAgent()

    # Create NDA
    nda = agent.create_document(
        title="Mutual NDA - Acme Corp",
        document_type=DocumentType.NDA,
        parties=["Our Company", "Acme Corp"],
        effective_date=datetime.utcnow(),
        expiration_date=datetime.utcnow() + timedelta(days=730),
    )

    print(f"Created: {nda.title}")
    print(f"Type: {nda.document_type.value}")
    print(f"Status: {nda.status}")

    # Review contract
    contract_text = "This agreement has unlimited liability and auto-renewal clauses."
    review = agent.review_contract(nda.document_id, contract_text)

    print(f"\nReview Results:")
    print(f"  Risks Found: {review['risks_found']}")
    print(f"  Overall Risk: {review['overall_risk'].value}")

    for risk in review['risks']:
        print(f"  - {risk['type']}: {risk['description']}")

    print(f"\nState: {agent.get_state()}")
