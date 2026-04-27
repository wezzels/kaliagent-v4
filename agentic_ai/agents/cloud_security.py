"""
CloudSecurityAgent - Cloud Security Posture Management (CSPM)
==============================================================

Provides cloud security monitoring, compliance checking, misconfiguration
detection, and remediation for AWS, Azure, and GCP environments.
"""

import logging
import secrets
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from typing import Any, Dict, List, Optional


logger = logging.getLogger(__name__)


class CloudProvider(Enum):
    """Cloud providers."""
    AWS = "aws"
    AZURE = "azure"
    GCP = "gcp"
    MULTI = "multi_cloud"


class ResourceType(Enum):
    """Cloud resource types."""
    EC2 = "ec2"
    S3 = "s3"
    RDS = "rds"
    LAMBDA = "lambda"
    IAM = "iam"
    VPC = "vpc"
    KMS = "kms"
    EKS = "eks"
    VM = "vm"
    STORAGE_ACCOUNT = "storage_account"
    SQL_DATABASE = "sql_database"
    FUNCTION = "function"
    GCE = "gce"
    GCS = "gcs"
    BIGQUERY = "bigquery"
    GKE = "gke"


class ComplianceFramework(Enum):
    """Compliance frameworks."""
    CIS_AWS = "cis_aws"
    CIS_AZURE = "cis_azure"
    CIS_GCP = "cis_gcp"
    PCI_DSS = "pci_dss"
    HIPAA = "hipaa"
    SOC2 = "soc2"
    GDPR = "gdpr"
    NIST = "nist"
    ISO27001 = "iso27001"


class Severity(Enum):
    """Finding severity."""
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    INFO = "info"


class FindingStatus(Enum):
    """Finding status."""
    OPEN = "open"
    IN_PROGRESS = "in_progress"
    RESOLVED = "resolved"
    FALSE_POSITIVE = "false_positive"
    ACCEPTED_RISK = "accepted_risk"


@dataclass
class CloudAccount:
    """Cloud account record."""
    account_id: str
    provider: CloudProvider
    name: str
    environment: str  # production, staging, development
    owner: str
    created_at: datetime = field(default_factory=datetime.utcnow)
    last_scanned: Optional[datetime] = None
    resource_count: int = 0
    findings_count: int = 0


@dataclass
class CloudResource:
    """Cloud resource record."""
    resource_id: str
    resource_type: ResourceType
    account_id: str
    region: str
    name: str
    tags: Dict[str, str] = field(default_factory=dict)
    configuration: Dict[str, Any] = field(default_factory=dict)
    compliant: bool = True
    last_checked: datetime = field(default_factory=datetime.utcnow)


@dataclass
class SecurityFinding:
    """Security finding."""
    finding_id: str
    title: str
    description: str
    severity: Severity
    status: FindingStatus
    resource_id: Optional[str]
    account_id: str
    compliance_framework: Optional[ComplianceFramework] = None
    control_id: Optional[str] = None
    remediation: str = ""
    detected_at: datetime = field(default_factory=datetime.utcnow)
    resolved_at: Optional[datetime] = None
    assigned_to: Optional[str] = None


@dataclass
class Policy:
    """Security policy."""
    policy_id: str
    name: str
    description: str
    provider: CloudProvider
    resource_type: ResourceType
    rule_expression: str
    severity: Severity
    compliance_frameworks: List[ComplianceFramework] = field(default_factory=list)
    enabled: bool = True
    created_at: datetime = field(default_factory=datetime.utcnow)


@dataclass
class Remediation:
    """Remediation action."""
    remediation_id: str
    finding_id: str
    action_type: str  # manual, automated, terraform, cli
    action_description: str
    status: str  # pending, in_progress, completed, failed
    executed_by: Optional[str] = None
    executed_at: Optional[datetime] = None
    result: Optional[str] = None


class CloudSecurityAgent:
    """
    Cloud Security Agent for CSPM, compliance checking,
    misconfiguration detection, and remediation.
    """

    def __init__(self, agent_id: str = "cloud-security-agent"):
        self.agent_id = agent_id
        self.accounts: Dict[str, CloudAccount] = {}
        self.resources: Dict[str, CloudResource] = {}
        self.findings: Dict[str, SecurityFinding] = {}
        self.policies: Dict[str, Policy] = {}
        self.remediations: Dict[str, Remediation] = {}

        # Built-in security policies
        self.builtin_policies = self._init_builtin_policies()

    def _init_builtin_policies(self) -> List[Dict[str, Any]]:
        """Initialize built-in security policies."""
        return [
            {
                'name': 'S3 Bucket Public Access',
                'provider': CloudProvider.AWS,
                'resource_type': ResourceType.S3,
                'rule': 'public_access_block == false',
                'severity': Severity.CRITICAL,
                'frameworks': [ComplianceFramework.CIS_AWS, ComplianceFramework.PCI_DSS],
                'remediation': 'Enable S3 block public access settings',
            },
            {
                'name': 'EC2 Security Group Open SSH',
                'provider': CloudProvider.AWS,
                'resource_type': ResourceType.EC2,
                'rule': 'ingress.port == 22 and ingress.cidr == 0.0.0.0/0',
                'severity': Severity.HIGH,
                'frameworks': [ComplianceFramework.CIS_AWS],
                'remediation': 'Restrict SSH access to specific IPs',
            },
            {
                'name': 'RDS Public Accessible',
                'provider': CloudProvider.AWS,
                'resource_type': ResourceType.RDS,
                'rule': 'publicly_accessible == true',
                'severity': Severity.HIGH,
                'frameworks': [ComplianceFramework.CIS_AWS, ComplianceFramework.PCI_DSS],
                'remediation': 'Disable public accessibility for RDS',
            },
            {
                'name': 'IAM User Without MFA',
                'provider': CloudProvider.AWS,
                'resource_type': ResourceType.IAM,
                'rule': 'mfa_enabled == false',
                'severity': Severity.HIGH,
                'frameworks': [ComplianceFramework.CIS_AWS, ComplianceFramework.SOC2],
                'remediation': 'Enable MFA for all IAM users',
            },
            {
                'name': 'Storage Account Public Blob',
                'provider': CloudProvider.AZURE,
                'resource_type': ResourceType.STORAGE_ACCOUNT,
                'rule': 'public_access_level == blob',
                'severity': Severity.CRITICAL,
                'frameworks': [ComplianceFramework.CIS_AZURE],
                'remediation': 'Set storage account to private',
            },
            {
                'name': 'GCS Bucket AllUsers',
                'provider': CloudProvider.GCP,
                'resource_type': ResourceType.GCS,
                'rule': 'iam_policy contains allUsers',
                'severity': Severity.CRITICAL,
                'frameworks': [ComplianceFramework.CIS_GCP],
                'remediation': 'Remove allUsers from bucket IAM policy',
            },
            {
                'name': 'Unencrypted EBS Volume',
                'provider': CloudProvider.AWS,
                'resource_type': ResourceType.EC2,
                'rule': 'encrypted == false',
                'severity': Severity.MEDIUM,
                'frameworks': [ComplianceFramework.CIS_AWS, ComplianceFramework.HIPAA],
                'remediation': 'Enable EBS encryption',
            },
            {
                'name': 'KMS Key Rotation Disabled',
                'provider': CloudProvider.AWS,
                'resource_type': ResourceType.KMS,
                'rule': 'rotation_enabled == false',
                'severity': Severity.MEDIUM,
                'frameworks': [ComplianceFramework.CIS_AWS, ComplianceFramework.PCI_DSS],
                'remediation': 'Enable automatic key rotation',
            },
        ]

    # ============================================
    # Account Management
    # ============================================

    def add_account(
        self,
        account_id: str,
        provider: CloudProvider,
        name: str,
        environment: str,
        owner: str,
    ) -> CloudAccount:
        """Add cloud account for monitoring."""
        account = CloudAccount(
            account_id=self._generate_id("acct"),
            provider=provider,
            name=name,
            environment=environment,
            owner=owner,
        )

        self.accounts[account.account_id] = account
        logger.info(f"Added cloud account: {account.name}")
        return account

    def update_account_scan(
        self,
        account_id: str,
        resource_count: int,
        findings_count: int,
    ) -> bool:
        """Update account scan results."""
        if account_id not in self.accounts:
            return False

        account = self.accounts[account_id]
        account.last_scanned = datetime.utcnow()
        account.resource_count = resource_count
        account.findings_count = findings_count

        return True

    def get_accounts(
        self,
        provider: Optional[CloudProvider] = None,
        environment: Optional[str] = None,
    ) -> List[CloudAccount]:
        """Get accounts with filtering."""
        accounts = list(self.accounts.values())

        if provider:
            accounts = [a for a in accounts if a.provider == provider]

        if environment:
            accounts = [a for a in accounts if a.environment == environment]

        return accounts

    # ============================================
    # Resource Management
    # ============================================

    def add_resource(
        self,
        resource_type: ResourceType,
        account_id: str,
        region: str,
        name: str,
        configuration: Optional[Dict[str, Any]] = None,
        tags: Optional[Dict[str, str]] = None,
    ) -> CloudResource:
        """Add cloud resource for monitoring."""
        resource = CloudResource(
            resource_id=self._generate_id("res"),
            resource_type=resource_type,
            account_id=account_id,
            region=region,
            name=name,
            configuration=configuration or {},
            tags=tags or {},
        )

        self.resources[resource.resource_id] = resource
        return resource

    def check_resource_compliance(self, resource_id: str, policies: List[Policy]) -> List[SecurityFinding]:
        """Check resource against policies."""
        if resource_id not in self.resources:
            return []

        resource = self.resources[resource_id]
        findings = []

        for policy in policies:
            if policy.resource_type != resource.resource_type:
                continue

            # Evaluate policy rule (simplified)
            violates = self._evaluate_rule(policy.rule_expression, resource.configuration)

            if violates:
                finding = self.create_finding(
                    title=policy.name,
                    description=f"Resource {resource.name} violates policy",
                    severity=policy.severity,
                    resource_id=resource_id,
                    account_id=resource.account_id,
                    compliance_framework=policy.compliance_frameworks[0] if policy.compliance_frameworks else None,
                    control_id=policy.policy_id,
                    remediation=policy.rule_expression.replace('rule:', 'Fix: '),
                )
                findings.append(finding)

        return findings

    def _evaluate_rule(self, rule: str, config: Dict[str, Any]) -> bool:
        """Evaluate policy rule against configuration."""
        # Simplified rule evaluation
        # In production, use OPA/Rego or similar
        if 'public' in rule.lower() and 'true' in rule.lower():
            for key, value in config.items():
                if 'public' in key.lower() and value is True:
                    return True
        if 'false' in rule.lower():
            for key, value in config.items():
                if 'encrypt' in key.lower() and value is False:
                    return True
                if 'mfa' in key.lower() and value is False:
                    return True
        return False

    def get_resources(
        self,
        resource_type: Optional[ResourceType] = None,
        account_id: Optional[str] = None,
        region: Optional[str] = None,
        compliant: Optional[bool] = None,
    ) -> List[CloudResource]:
        """Get resources with filtering."""
        resources = list(self.resources.values())

        if resource_type:
            resources = [r for r in resources if r.resource_type == resource_type]

        if account_id:
            resources = [r for r in resources if r.account_id == account_id]

        if region:
            resources = [r for r in resources if r.region == region]

        if compliant is not None:
            resources = [r for r in resources if r.compliant == compliant]

        return resources

    # ============================================
    # Finding Management
    # ============================================

    def create_finding(
        self,
        title: str,
        description: str,
        severity: Severity,
        resource_id: Optional[str],
        account_id: str,
        compliance_framework: Optional[ComplianceFramework] = None,
        control_id: Optional[str] = None,
        remediation: str = "",
    ) -> SecurityFinding:
        """Create security finding."""
        finding = SecurityFinding(
            finding_id=self._generate_id("find"),
            title=title,
            description=description,
            severity=severity,
            status=FindingStatus.OPEN,
            resource_id=resource_id,
            account_id=account_id,
            compliance_framework=compliance_framework,
            control_id=control_id,
            remediation=remediation,
        )

        self.findings[finding.finding_id] = finding

        # Update account findings count
        if account_id in self.accounts:
            self.accounts[account_id].findings_count += 1

        return finding

    def update_finding_status(
        self,
        finding_id: str,
        status: FindingStatus,
        assigned_to: Optional[str] = None,
    ) -> bool:
        """Update finding status."""
        if finding_id not in self.findings:
            return False

        finding = self.findings[finding_id]
        finding.status = status

        if assigned_to:
            finding.assigned_to = assigned_to

        if status == FindingStatus.RESOLVED:
            finding.resolved_at = datetime.utcnow()

        return True

    def get_findings(
        self,
        severity: Optional[Severity] = None,
        status: Optional[FindingStatus] = None,
        account_id: Optional[str] = None,
        compliance_framework: Optional[ComplianceFramework] = None,
    ) -> List[SecurityFinding]:
        """Get findings with filtering."""
        findings = list(self.findings.values())

        if severity:
            findings = [f for f in findings if f.severity == severity]

        if status:
            findings = [f for f in findings if f.status == status]

        if account_id:
            findings = [f for f in findings if f.account_id == account_id]

        if compliance_framework:
            findings = [f for f in findings if f.compliance_framework == compliance_framework]

        return findings

    # ============================================
    # Policy Management
    # ============================================

    def create_policy(
        self,
        name: str,
        description: str,
        provider: CloudProvider,
        resource_type: ResourceType,
        rule_expression: str,
        severity: Severity,
        compliance_frameworks: Optional[List[ComplianceFramework]] = None,
    ) -> Policy:
        """Create custom security policy."""
        policy = Policy(
            policy_id=self._generate_id("policy"),
            name=name,
            description=description,
            provider=provider,
            resource_type=resource_type,
            rule_expression=rule_expression,
            severity=severity,
            compliance_frameworks=compliance_frameworks or [],
        )

        self.policies[policy.policy_id] = policy
        return policy

    def get_policies(
        self,
        provider: Optional[CloudProvider] = None,
        enabled: Optional[bool] = None,
    ) -> List[Policy]:
        """Get policies with filtering."""
        policies = list(self.policies.values())

        if provider:
            policies = [p for p in policies if p.provider == provider]

        if enabled is not None:
            policies = [p for p in policies if p.enabled == enabled]

        return policies

    # ============================================
    # Remediation
    # ============================================

    def create_remediation(
        self,
        finding_id: str,
        action_type: str,
        action_description: str,
    ) -> Remediation:
        """Create remediation action."""
        remediation = Remediation(
            remediation_id=self._generate_id("rem"),
            finding_id=finding_id,
            action_type=action_type,
            action_description=action_description,
            status="pending",
        )

        self.remediations[remediation.remediation_id] = remediation
        return remediation

    def execute_remediation(
        self,
        remediation_id: str,
        executed_by: str,
        result: str,
    ) -> bool:
        """Mark remediation as executed."""
        if remediation_id not in self.remediations:
            return False

        remediation = self.remediations[remediation_id]
        remediation.status = "completed"
        remediation.executed_by = executed_by
        remediation.executed_at = datetime.utcnow()
        remediation.result = result

        # Update finding status
        if remediation.finding_id in self.findings:
            self.findings[remediation.finding_id].status = FindingStatus.RESOLVED
            self.findings[remediation.finding_id].resolved_at = datetime.utcnow()

        return True

    # ============================================
    # Compliance Reporting
    # ============================================

    def get_compliance_score(self, framework: ComplianceFramework) -> Dict[str, Any]:
        """Calculate compliance score for a framework."""
        findings = self.get_findings(compliance_framework=framework)

        total_controls = len([p for p in self.policies.values() if framework in p.compliance_frameworks])
        open_findings = len([f for f in findings if f.status == FindingStatus.OPEN])

        if total_controls == 0:
            return {'framework': framework.value, 'score': None, 'message': 'No controls defined'}

        # Score = 100 - (open_findings / total_controls * 100)
        score = max(0, 100 - (open_findings / total_controls * 100))

        return {
            'framework': framework.value,
            'score': round(score, 1),
            'total_controls': total_controls,
            'open_findings': open_findings,
            'passed_controls': total_controls - open_findings,
        }

    def get_cloud_security_report(self) -> Dict[str, Any]:
        """Generate cloud security report."""
        accounts = list(self.accounts.values())
        findings = list(self.findings.values())

        # By provider
        by_provider = {}
        for provider in CloudProvider:
            by_provider[provider.value] = len([a for a in accounts if a.provider == provider])

        # By severity
        by_severity = {}
        for severity in Severity:
            by_severity[severity.value] = len([f for f in findings if f.severity == severity])

        # By status
        by_status = {}
        for status in FindingStatus:
            by_status[status.value] = len([f for f in findings if f.status == status])

        # Open critical/high findings
        critical_open = len([f for f in findings if f.severity == Severity.CRITICAL and f.status == FindingStatus.OPEN])
        high_open = len([f for f in findings if f.severity == Severity.HIGH and f.status == FindingStatus.OPEN])

        return {
            'accounts': {
                'total': len(accounts),
                'by_provider': by_provider,
                'production': len([a for a in accounts if a.environment == 'production']),
            },
            'resources': {
                'total': len(self.resources),
                'compliant': len([r for r in self.resources.values() if r.compliant]),
                'non_compliant': len([r for r in self.resources.values() if not r.compliant]),
            },
            'findings': {
                'total': len(findings),
                'by_severity': by_severity,
                'by_status': by_status,
                'critical_open': critical_open,
                'high_open': high_open,
            },
            'policies': {
                'total': len(self.policies),
                'enabled': len([p for p in self.policies.values() if p.enabled]),
            },
            'remediation': {
                'total': len(self.remediations),
                'completed': len([r for r in self.remediations.values() if r.status == 'completed']),
                'pending': len([r for r in self.remediations.values() if r.status == 'pending']),
            },
        }

    def get_account_risk_profile(self, account_id: str) -> Dict[str, Any]:
        """Get risk profile for a cloud account."""
        if account_id not in self.accounts:
            return {'error': 'Account not found'}

        account = self.accounts[account_id]
        findings = self.get_findings(account_id=account_id)

        critical = len([f for f in findings if f.severity == Severity.CRITICAL and f.status == FindingStatus.OPEN])
        high = len([f for f in findings if f.severity == Severity.HIGH and f.status == FindingStatus.OPEN])
        medium = len([f for f in findings if f.severity == Severity.MEDIUM and f.status == FindingStatus.OPEN])

        # Risk score: critical*10 + high*5 + medium*2
        risk_score = critical * 10 + high * 5 + medium * 2

        risk_level = "low"
        if risk_score >= 50:
            risk_level = "critical"
        elif risk_score >= 25:
            risk_level = "high"
        elif risk_score >= 10:
            risk_level = "medium"

        return {
            'account_id': account_id,
            'name': account.name,
            'provider': account.provider.value,
            'environment': account.environment,
            'risk_score': risk_score,
            'risk_level': risk_level,
            'findings': {
                'critical': critical,
                'high': high,
                'medium': medium,
                'total': len(findings),
            },
            'resources': account.resource_count,
            'last_scanned': account.last_scanned.isoformat() if account.last_scanned else None,
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
        findings = list(self.findings.values())
        return {
            'agent_id': self.agent_id,
            'accounts_count': len(self.accounts),
            'resources_count': len(self.resources),
            'findings_count': len(findings),
            'open_findings': len([f for f in findings if f.status == FindingStatus.OPEN]),
            'critical_open': len([f for f in findings if f.severity == Severity.CRITICAL and f.status == FindingStatus.OPEN]),
            'policies_count': len(self.policies),
            'remediations_count': len(self.remediations),
        }


def get_capabilities() -> Dict[str, Any]:
    """Return agent capabilities for orchestration."""
    return {
        'agent_type': 'cloud_security',
        'version': '1.0.0',
        'capabilities': [
            'add_account',
            'update_account_scan',
            'get_accounts',
            'add_resource',
            'check_resource_compliance',
            'get_resources',
            'create_finding',
            'update_finding_status',
            'get_findings',
            'create_policy',
            'get_policies',
            'create_remediation',
            'execute_remediation',
            'get_compliance_score',
            'get_cloud_security_report',
            'get_account_risk_profile',
        ],
        'cloud_providers': [p.value for p in CloudProvider],
        'resource_types': [t.value for t in ResourceType],
        'compliance_frameworks': [f.value for f in ComplianceFramework],
        'severities': [s.value for s in Severity],
        'finding_statuses': [s.value for s in FindingStatus],
    }


if __name__ == "__main__":
    agent = CloudSecurityAgent()

    # Add accounts
    aws_prod = agent.add_account(
        account_id="123456789012",
        provider=CloudProvider.AWS,
        name="Production AWS",
        environment="production",
        owner="cloud-team@example.com",
    )

    print(f"Added account: {aws_prod.name}")

    # Add resources
    s3_bucket = agent.add_resource(
        resource_type=ResourceType.S3,
        account_id=aws_prod.account_id,
        region="us-east-1",
        name="company-data-bucket",
        configuration={'public_access_block': True, 'encrypted': True},
        tags={'environment': 'production'},
    )

    ec2_instance = agent.add_resource(
        resource_type=ResourceType.EC2,
        account_id=aws_prod.account_id,
        region="us-east-1",
        name="web-server-1",
        configuration={'encrypted': False, 'public_ip': True},
    )

    # Create policy
    policy = agent.create_policy(
        name="Unencrypted EBS",
        description="All EBS volumes must be encrypted",
        provider=CloudProvider.AWS,
        resource_type=ResourceType.EC2,
        rule_expression="encrypted == false",
        severity=Severity.MEDIUM,
        compliance_frameworks=[ComplianceFramework.CIS_AWS],
    )

    # Check compliance
    findings = agent.check_resource_compliance(ec2_instance.resource_id, [policy])
    print(f"Found {len(findings)} compliance issues")

    # Create finding
    finding = agent.create_finding(
        title="S3 Bucket Public Access",
        description="Bucket allows public access",
        severity=Severity.CRITICAL,
        resource_id=s3_bucket.resource_id,
        account_id=aws_prod.account_id,
        compliance_framework=ComplianceFramework.CIS_AWS,
        remediation="Enable block public access",
    )

    # Create remediation
    remediation = agent.create_remediation(
        finding.finding_id,
        action_type="terraform",
        action_description="Apply terraform to enable block public access",
    )

    # Execute remediation
    agent.execute_remediation(remediation.remediation_id, "automation", "Terraform apply successful")

    # Get compliance score
    score = agent.get_compliance_score(ComplianceFramework.CIS_AWS)
    print(f"CIS AWS Score: {score['score']}")

    # Get risk profile
    profile = agent.get_account_risk_profile(aws_prod.account_id)
    print(f"Risk Level: {profile['risk_level']}")

    # Get report
    report = agent.get_cloud_security_report()
    print(f"\nCloud Security Report:")
    print(f"  Accounts: {report['accounts']['total']}")
    print(f"  Findings: {report['findings']['total']}")
    print(f"  Critical Open: {report['findings']['critical_open']}")

    print(f"\nState: {agent.get_state()}")
