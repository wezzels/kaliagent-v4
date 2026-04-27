"""
DataGovernanceAgent - Data Classification, Retention & Quality
================================================================

Provides data classification, retention policies, data lineage tracking,
data quality monitoring, and governance workflow automation.
"""

import logging
import secrets
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from typing import Any, Dict, List, Optional


logger = logging.getLogger(__name__)


class DataClassification(Enum):
    """Data classification levels."""
    PUBLIC = "public"
    INTERNAL = "internal"
    CONFIDENTIAL = "confidential"
    RESTRICTED = "restricted"
    CRITICAL = "critical"


class DataType(Enum):
    """Data types."""
    PII = "pii"  # Personal Identifiable Information
    PHI = "phi"  # Protected Health Information
    PCI = "pci"  # Payment Card Information
    FINANCIAL = "financial"
    IP = "intellectual_property"
    HR = "human_resources"
    LEGAL = "legal"
    OPERATIONAL = "operational"
    ANALYTICS = "analytics"
    LOGS = "logs"


class DataQualityDimension(Enum):
    """Data quality dimensions."""
    ACCURACY = "accuracy"
    COMPLETENESS = "completeness"
    CONSISTENCY = "consistency"
    TIMELINESS = "timeliness"
    UNIQUENESS = "uniqueness"
    VALIDITY = "validity"


class RetentionAction(Enum):
    """Retention actions."""
    KEEP = "keep"
    ARCHIVE = "archive"
    DELETE = "delete"
    ANONYMIZE = "anonymize"
    AGGREGATE = "aggregate"


@dataclass
class DataAsset:
    """Data asset record."""
    asset_id: str
    name: str
    description: str
    data_type: DataType
    classification: DataClassification
    owner: str
    steward: Optional[str] = None
    location: str = ""  # Database, bucket, etc.
    system: str = ""
    created_at: datetime = field(default_factory=datetime.utcnow)
    last_modified: datetime = field(default_factory=datetime.utcnow)
    record_count: int = 0
    size_bytes: int = 0
    tags: List[str] = field(default_factory=list)


@dataclass
class RetentionPolicy:
    """Data retention policy."""
    policy_id: str
    name: str
    data_types: List[DataType]
    retention_period: int  # days
    action: RetentionAction
    retention_unit: str = "days"  # days, months, years
    legal_hold: bool = False
    regulatory_requirement: str = ""
    exceptions: List[str] = field(default_factory=list)
    created_at: datetime = field(default_factory=datetime.utcnow)


@dataclass
class DataLineage:
    """Data lineage record."""
    lineage_id: str
    source_asset: str
    target_asset: str
    transformation: str
    process_name: str
    frequency: str = "daily"  # real-time, hourly, daily, weekly, monthly
    last_run: Optional[datetime] = None
    status: str = "unknown"  # success, failed, warning, unknown
    records_processed: int = 0
    created_at: datetime = field(default_factory=datetime.utcnow)


@dataclass
class DataQualityRule:
    """Data quality rule."""
    rule_id: str
    name: str
    asset_id: str
    dimension: DataQualityDimension
    rule_expression: str
    threshold: float  # 0-100%
    severity: str = "medium"  # low, medium, high, critical
    enabled: bool = True
    last_check: Optional[datetime] = None
    last_result: Optional[float] = None
    created_at: datetime = field(default_factory=datetime.utcnow)


@dataclass
class QualityIssue:
    """Data quality issue."""
    issue_id: str
    rule_id: str
    asset_id: str
    severity: str
    description: str
    affected_records: int = 0
    status: str = "open"  # open, investigating, resolved, accepted
    detected_at: datetime = field(default_factory=datetime.utcnow)
    resolved_at: Optional[datetime] = None
    assigned_to: Optional[str] = None
    remediation: str = ""


@dataclass
@dataclass
class AccessRequest:
    """Data access request."""
    request_id: str
    asset_id: str
    requester: str
    purpose: str
    access_level: str
    status: str = "pending"  # pending, approved, denied, revoked
    approved_by: Optional[str] = None
    approved_at: Optional[datetime] = None
    expires_at: Optional[datetime] = None
    justification: str = ""


class DataGovernanceAgent:
    """
    Data Governance Agent for data classification, retention,
    lineage tracking, quality monitoring, and access management.
    """

    def __init__(self, agent_id: str = "data-governance-agent"):
        self.agent_id = agent_id
        self.assets: Dict[str, DataAsset] = {}
        self.retention_policies: Dict[str, RetentionPolicy] = {}
        self.lineage: Dict[str, DataLineage] = {}
        self.quality_rules: Dict[str, DataQualityRule] = {}
        self.quality_issues: Dict[str, QualityIssue] = {}
        self.access_requests: Dict[str, AccessRequest] = {}

        # Default retention periods by data type
        self.default_retention = {
            DataType.PII: {'period': 730, 'unit': 'days', 'action': RetentionAction.DELETE},
            DataType.PHI: {'period': 2190, 'unit': 'days', 'action': RetentionAction.ARCHIVE},  # 6 years
            DataType.PCI: {'period': 365, 'unit': 'days', 'action': RetentionAction.DELETE},
            DataType.FINANCIAL: {'period': 2555, 'unit': 'days', 'action': RetentionAction.ARCHIVE},  # 7 years
            DataType.LOGS: {'period': 90, 'unit': 'days', 'action': RetentionAction.DELETE},
            DataType.ANALYTICS: {'period': 365, 'unit': 'days', 'action': RetentionAction.AGGREGATE},
        }

        # Classification criteria
        self.classification_keywords = {
            DataClassification.CRITICAL: ['trade_secret', 'crown_jewel', 'mission_critical'],
            DataClassification.RESTRICTED: ['ssn', 'credit_card', 'password', 'secret'],
            DataClassification.CONFIDENTIAL: ['confidential', 'proprietary', 'internal_only'],
            DataClassification.INTERNAL: ['internal', 'company_only'],
            DataClassification.PUBLIC: ['public', 'published', 'press'],
        }

    # ============================================
    # Data Asset Management
    # ============================================

    def register_asset(
        self,
        name: str,
        description: str,
        data_type: DataType,
        classification: DataClassification,
        owner: str,
        location: str,
        system: str,
        steward: Optional[str] = None,
        tags: Optional[List[str]] = None,
    ) -> DataAsset:
        """Register a data asset."""
        asset = DataAsset(
            asset_id=self._generate_id("asset"),
            name=name,
            description=description,
            data_type=data_type,
            classification=classification,
            owner=owner,
            steward=steward,
            location=location,
            system=system,
        )

        self.assets[asset.asset_id] = asset
        logger.info(f"Registered asset: {asset.name}")
        return asset

    def update_asset_metrics(
        self,
        asset_id: str,
        record_count: Optional[int] = None,
        size_bytes: Optional[int] = None,
    ) -> bool:
        """Update asset metrics."""
        if asset_id not in self.assets:
            return False

        asset = self.assets[asset_id]
        asset.last_modified = datetime.utcnow()

        if record_count is not None:
            asset.record_count = record_count

        if size_bytes is not None:
            asset.size_bytes = size_bytes

        return True

    def get_assets(
        self,
        data_type: Optional[DataType] = None,
        classification: Optional[DataClassification] = None,
        owner: Optional[str] = None,
    ) -> List[DataAsset]:
        """Get assets with filtering."""
        assets = list(self.assets.values())

        if data_type:
            assets = [a for a in assets if a.data_type == data_type]

        if classification:
            assets = [a for a in assets if a.classification == classification]

        if owner:
            assets = [a for a in assets if a.owner == owner]

        return assets

    def classify_data(self, content: str) -> DataClassification:
        """Auto-classify data based on content keywords."""
        content_lower = content.lower()

        for classification, keywords in self.classification_keywords.items():
            for keyword in keywords:
                if keyword in content_lower:
                    return classification

        return DataClassification.INTERNAL

    # ============================================
    # Retention Policy Management
    # ============================================

    def create_retention_policy(
        self,
        name: str,
        data_types: List[DataType],
        retention_period: int,
        action: RetentionAction,
        regulatory_requirement: str = "",
        legal_hold: bool = False,
    ) -> RetentionPolicy:
        """Create retention policy."""
        policy = RetentionPolicy(
            policy_id=self._generate_id("policy"),
            name=name,
            data_types=data_types,
            retention_period=retention_period,
            retention_unit="days",
            action=action,
            regulatory_requirement=regulatory_requirement,
            legal_hold=legal_hold,
        )

        self.retention_policies[policy.policy_id] = policy
        return policy

    def get_retention_period(self, asset_id: str) -> Dict[str, Any]:
        """Get retention period for an asset."""
        if asset_id not in self.assets:
            return {'error': 'Asset not found'}

        asset = self.assets[asset_id]

        # Check for specific policy
        for policy in self.retention_policies.values():
            if asset.data_type in policy.data_types:
                return {
                    'policy_id': policy.policy_id,
                    'policy_name': policy.name,
                    'retention_period': policy.retention_period,
                    'unit': policy.retention_unit,
                    'action': policy.action.value,
                    'legal_hold': policy.legal_hold,
                }

        # Use default
        default = self.default_retention.get(asset.data_type, {
            'period': 365,
            'unit': 'days',
            'action': RetentionAction.ARCHIVE,
        })

        return {
            'policy_id': 'default',
            'retention_period': default['period'],
            'unit': default['unit'],
            'action': default['action'].value,
        }

    def get_assets_due_for_action(self, action: RetentionAction) -> List[Dict[str, Any]]:
        """Get assets due for retention action."""
        due = []
        now = datetime.utcnow()

        for asset in self.assets.values():
            retention = self.get_retention_period(asset.asset_id)
            if 'error' in retention:
                continue

            # Simulate created_at for demo
            age_days = 400  # In real impl, calculate from asset.created_at

            if age_days >= retention['retention_period']:
                due.append({
                    'asset_id': asset.asset_id,
                    'name': asset.name,
                    'action': retention['action'],
                    'days_overdue': age_days - retention['retention_period'],
                })

        return [d for d in due if d['action'] == action.value]

    # ============================================
    # Data Lineage
    # ============================================

    def add_lineage(
        self,
        source_asset: str,
        target_asset: str,
        transformation: str,
        process_name: str,
        frequency: str = "daily",
    ) -> DataLineage:
        """Add data lineage record."""
        lineage = DataLineage(
            lineage_id=self._generate_id("lineage"),
            source_asset=source_asset,
            target_asset=target_asset,
            transformation=transformation,
            process_name=process_name,
            frequency=frequency,
        )

        self.lineage[lineage.lineage_id] = lineage
        return lineage

    def update_lineage_status(
        self,
        lineage_id: str,
        status: str,
        records_processed: int = 0,
    ) -> bool:
        """Update lineage execution status."""
        if lineage_id not in self.lineage:
            return False

        lineage = self.lineage[lineage_id]
        lineage.status = status
        lineage.last_run = datetime.utcnow()
        lineage.records_processed = records_processed

        return True

    def get_lineage(self, asset_id: str, direction: str = "both") -> Dict[str, Any]:
        """Get data lineage for an asset."""
        upstream = [
            l for l in self.lineage.values()
            if l.target_asset == asset_id
        ]

        downstream = [
            l for l in self.lineage.values()
            if l.source_asset == asset_id
        ]

        result = {'asset_id': asset_id}

        if direction in ['upstream', 'both']:
            result['upstream'] = [
                {
                    'lineage_id': l.lineage_id,
                    'source': l.source_asset,
                    'transformation': l.transformation,
                    'process': l.process_name,
                }
                for l in upstream
            ]

        if direction in ['downstream', 'both']:
            result['downstream'] = [
                {
                    'lineage_id': l.lineage_id,
                    'target': l.target_asset,
                    'transformation': l.transformation,
                    'process': l.process_name,
                }
                for l in downstream
            ]

        return result

    # ============================================
    # Data Quality
    # ============================================

    def create_quality_rule(
        self,
        name: str,
        asset_id: str,
        dimension: DataQualityDimension,
        rule_expression: str,
        threshold: float,
        severity: str = "medium",
    ) -> DataQualityRule:
        """Create data quality rule."""
        rule = DataQualityRule(
            rule_id=self._generate_id("rule"),
            name=name,
            asset_id=asset_id,
            dimension=dimension,
            rule_expression=rule_expression,
            threshold=threshold,
            severity=severity,
        )

        self.quality_rules[rule.rule_id] = rule
        return rule

    def execute_quality_check(self, rule_id: str, result: float) -> bool:
        """Execute quality check and record result."""
        if rule_id not in self.quality_rules:
            return False

        rule = self.quality_rules[rule_id]
        rule.last_check = datetime.utcnow()
        rule.last_result = result

        # Create issue if below threshold
        if result < rule.threshold:
            self._create_quality_issue(rule, result)

        return True

    def _create_quality_issue(self, rule: DataQualityRule, result: float):
        """Create quality issue from failed check."""
        issue = QualityIssue(
            issue_id=self._generate_id("issue"),
            rule_id=rule.rule_id,
            asset_id=rule.asset_id,
            severity=rule.severity,
            description=f"Quality check '{rule.name}' failed: {result:.1f}% < {rule.threshold}%",
            status="open",
        )

        self.quality_issues[issue.issue_id] = issue
        logger.warning(f"Quality issue detected: {issue.description}")

    def resolve_quality_issue(
        self,
        issue_id: str,
        remediation: str,
    ) -> bool:
        """Resolve a quality issue."""
        if issue_id not in self.quality_issues:
            return False

        issue = self.quality_issues[issue_id]
        issue.status = "resolved"
        issue.resolved_at = datetime.utcnow()
        issue.remediation = remediation

        return True

    def get_quality_issues(
        self,
        asset_id: Optional[str] = None,
        severity: Optional[str] = None,
        status: Optional[str] = None,
    ) -> List[QualityIssue]:
        """Get quality issues with filtering."""
        issues = list(self.quality_issues.values())

        if asset_id:
            issues = [i for i in issues if i.asset_id == asset_id]

        if severity:
            issues = [i for i in issues if i.severity == severity]

        if status:
            issues = [i for i in issues if i.status == status]

        return issues

    def get_quality_score(self, asset_id: str) -> Dict[str, Any]:
        """Calculate overall quality score for an asset."""
        rules = [r for r in self.quality_rules.values() if r.asset_id == asset_id]

        if not rules:
            return {'asset_id': asset_id, 'score': None, 'message': 'No rules defined'}

        scores = [r.last_result for r in rules if r.last_result is not None]

        if not scores:
            return {'asset_id': asset_id, 'score': None, 'message': 'No checks executed'}

        avg_score = sum(scores) / len(scores)

        return {
            'asset_id': asset_id,
            'score': round(avg_score, 1),
            'rules_count': len(rules),
            'checks_executed': len(scores),
            'dimension_scores': self._get_dimension_scores(rules),
        }

    def _get_dimension_scores(self, rules: List[DataQualityRule]) -> Dict[str, float]:
        """Get scores by quality dimension."""
        by_dimension: Dict[str, List[float]] = {}

        for rule in rules:
            if rule.last_result is not None:
                dim = rule.dimension.value
                if dim not in by_dimension:
                    by_dimension[dim] = []
                by_dimension[dim].append(rule.last_result)

        return {
            dim: round(sum(scores) / len(scores), 1)
            for dim, scores in by_dimension.items()
        }

    # ============================================
    # Access Management
    # ============================================

    def request_access(
        self,
        asset_id: str,
        requester: str,
        purpose: str,
        access_level: str,
        justification: str = "",
    ) -> AccessRequest:
        """Request access to data asset."""
        request = AccessRequest(
            request_id=self._generate_id("access"),
            asset_id=asset_id,
            requester=requester,
            purpose=purpose,
            access_level=access_level,
            justification=justification,
        )

        self.access_requests[request.request_id] = request
        return request

    def approve_access(
        self,
        request_id: str,
        approved_by: str,
        expires_in_days: int = 90,
    ) -> bool:
        """Approve access request."""
        if request_id not in self.access_requests:
            return False

        request = self.access_requests[request_id]
        request.status = "approved"
        request.approved_by = approved_by
        request.approved_at = datetime.utcnow()
        request.expires_at = datetime.utcnow() + timedelta(days=expires_in_days)

        return True

    def deny_access(self, request_id: str, denied_by: str, reason: str = "") -> bool:
        """Deny access request."""
        if request_id not in self.access_requests:
            return False

        request = self.access_requests[request_id]
        request.status = "denied"
        request.approved_by = denied_by
        request.approved_at = datetime.utcnow()

        if reason:
            request.justification += f" (Denied: {reason})"

        return True

    def revoke_access(self, request_id: str) -> bool:
        """Revoke approved access."""
        if request_id not in self.access_requests:
            return False

        request = self.access_requests[request_id]
        request.status = "revoked"

        return True

    def get_access_requests(
        self,
        asset_id: Optional[str] = None,
        status: Optional[str] = None,
        requester: Optional[str] = None,
    ) -> List[AccessRequest]:
        """Get access requests with filtering."""
        requests = list(self.access_requests.values())

        if asset_id:
            requests = [r for r in requests if r.asset_id == asset_id]

        if status:
            requests = [r for r in requests if r.status == status]

        if requester:
            requests = [r for r in requests if r.requester == requester]

        return requests

    # ============================================
    # Reporting
    # ============================================

    def get_governance_report(self) -> Dict[str, Any]:
        """Generate data governance report."""
        assets = list(self.assets.values())
        issues = list(self.quality_issues.values())
        requests = list(self.access_requests.values())

        # Classification distribution
        by_classification = {}
        for cls in DataClassification:
            by_classification[cls.value] = len([a for a in assets if a.classification == cls])

        # Data type distribution
        by_type = {}
        for dtype in DataType:
            by_type[dtype.value] = len([a for a in assets if a.data_type == dtype])

        # Quality metrics
        open_issues = len([i for i in issues if i.status == 'open'])
        critical_issues = len([i for i in issues if i.severity == 'critical' and i.status == 'open'])

        # Access metrics
        pending_requests = len([r for r in requests if r.status == 'pending'])

        return {
            'assets': {
                'total': len(assets),
                'by_classification': by_classification,
                'by_type': by_type,
                'total_records': sum(a.record_count for a in assets),
                'total_size_gb': round(sum(a.size_bytes for a in assets) / (1024**3), 2),
            },
            'quality': {
                'total_issues': len(issues),
                'open_issues': open_issues,
                'critical_issues': critical_issues,
                'rules_count': len(self.quality_rules),
            },
            'access': {
                'total_requests': len(requests),
                'pending': pending_requests,
                'approved': len([r for r in requests if r.status == 'approved']),
                'denied': len([r for r in requests if r.status == 'denied']),
            },
            'lineage': {
                'total_mappings': len(self.lineage),
            },
            'retention': {
                'policies_count': len(self.retention_policies),
            },
        }

    def get_compliance_summary(self) -> Dict[str, Any]:
        """Get compliance summary for regulated data."""
        regulated_types = [DataType.PII, DataType.PHI, DataType.PCI]

        regulated_assets = [
            a for a in self.assets.values()
            if a.data_type in regulated_types
        ]

        summary = {}
        for dtype in regulated_types:
            assets = [a for a in regulated_assets if a.data_type == dtype]
            summary[dtype.value] = {
                'asset_count': len(assets),
                'classifications': list(set(a.classification.value for a in assets)),
                'owners': list(set(a.owner for a in assets)),
            }

        return {
            'regulated_data_types': summary,
            'total_regulated_assets': len(regulated_assets),
            'retention_policies': len(self.retention_policies),
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
            'assets_count': len(self.assets),
            'retention_policies_count': len(self.retention_policies),
            'lineage_mappings_count': len(self.lineage),
            'quality_rules_count': len(self.quality_rules),
            'open_quality_issues': len([i for i in self.quality_issues.values() if i.status == 'open']),
            'pending_access_requests': len([r for r in self.access_requests.values() if r.status == 'pending']),
        }


def get_capabilities() -> Dict[str, Any]:
    """Return agent capabilities for orchestration."""
    return {
        'agent_type': 'data_governance',
        'version': '1.0.0',
        'capabilities': [
            'register_asset',
            'update_asset_metrics',
            'get_assets',
            'classify_data',
            'create_retention_policy',
            'get_retention_period',
            'get_assets_due_for_action',
            'add_lineage',
            'update_lineage_status',
            'get_lineage',
            'create_quality_rule',
            'execute_quality_check',
            'resolve_quality_issue',
            'get_quality_issues',
            'get_quality_score',
            'request_access',
            'approve_access',
            'deny_access',
            'revoke_access',
            'get_access_requests',
            'get_governance_report',
            'get_compliance_summary',
        ],
        'classifications': [c.value for c in DataClassification],
        'data_types': [t.value for t in DataType],
        'quality_dimensions': [d.value for d in DataQualityDimension],
        'retention_actions': [a.value for a in RetentionAction],
    }


if __name__ == "__main__":
    agent = DataGovernanceAgent()

    # Register assets
    customers = agent.register_asset(
        name="Customer Database",
        description="Main customer PII database",
        data_type=DataType.PII,
        classification=DataClassification.RESTRICTED,
        owner="data-team@example.com",
        steward="privacy@example.com",
        location="postgres://db-prod/customers",
        system="CRM",
        tags=['customers', 'pii', 'gdpr'],
    )

    print(f"Registered asset: {customers.name}")

    # Create retention policy
    policy = agent.create_retention_policy(
        name="PII Retention",
        data_types=[DataType.PII],
        retention_period=730,  # 2 years
        action=RetentionAction.DELETE,
        regulatory_requirement="GDPR Art. 5(1)(e)",
    )

    # Get retention period
    retention = agent.get_retention_period(customers.asset_id)
    print(f"Retention: {retention['retention_period']} {retention['unit']}")

    # Add lineage
    lineage = agent.add_lineage(
        source_asset=customers.asset_id,
        target_asset="analytics-warehouse",
        transformation="ETL - PII anonymized",
        process_name="daily_customer_etl",
        frequency="daily",
    )

    # Create quality rules
    completeness_rule = agent.create_quality_rule(
        name="Email Completeness",
        asset_id=customers.asset_id,
        dimension=DataQualityDimension.COMPLETENESS,
        rule_expression="email IS NOT NULL AND email != ''",
        threshold=95.0,
        severity="high",
    )

    # Execute quality check
    agent.execute_quality_check(completeness_rule.rule_id, result=92.5)

    # Get quality score
    score = agent.get_quality_score(customers.asset_id)
    print(f"Quality Score: {score['score']}")

    # Request access
    access = agent.request_access(
        asset_id=customers.asset_id,
        requester="analyst@example.com",
        purpose="Q2 customer analysis",
        access_level="read",
        justification="Business analysis for quarterly report",
    )

    # Approve access
    agent.approve_access(access.request_id, "data-owner@example.com", expires_in_days=30)

    # Get governance report
    report = agent.get_governance_report()
    print(f"\nGovernance Report:")
    print(f"  Total Assets: {report['assets']['total']}")
    print(f"  Open Issues: {report['quality']['open_issues']}")
    print(f"  Pending Access: {report['access']['pending']}")

    print(f"\nState: {agent.get_state()}")
