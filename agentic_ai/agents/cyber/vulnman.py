"""
VulnerabilityManagementAgent - Vulnerability Scanning & Patch Management
=========================================================================

Provides vulnerability scanning, CVE tracking, patch management,
risk scoring, and remediation workflow automation.
"""

import logging
import secrets
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from typing import Any, Dict, List, Optional


logger = logging.getLogger(__name__)


class Severity(Enum):
    """CVSS severity levels."""
    NONE = "none"  # 0.0
    LOW = "low"  # 0.1-3.9
    MEDIUM = "medium"  # 4.0-6.9
    HIGH = "high"  # 7.0-8.9
    CRITICAL = "critical"  # 9.0-10.0


class VulnerabilityStatus(Enum):
    """Vulnerability status."""
    NEW = "new"
    CONFIRMED = "confirmed"
    IN_REMEDIATION = "in_remediation"
    PATCHED = "patched"
    MITIGATED = "mitigated"
    ACCEPTED_RISK = "accepted_risk"
    FALSE_POSITIVE = "false_positive"


class AssetType(Enum):
    """Asset types."""
    SERVER = "server"
    WORKSTATION = "workstation"
    NETWORK_DEVICE = "network_device"
    WEB_APPLICATION = "web_application"
    DATABASE = "database"
    CONTAINER = "container"
    CLOUD_RESOURCE = "cloud_resource"
    IOT_DEVICE = "iot_device"


@dataclass
class Asset:
    """IT Asset record."""
    asset_id: str
    name: str
    asset_type: AssetType
    ip_address: Optional[str] = None
    hostname: Optional[str] = None
    os: Optional[str] = None
    owner: Optional[str] = None
    location: str = ""
    criticality: str = "medium"  # low, medium, high, critical
    tags: List[str] = field(default_factory=list)
    vulnerabilities_count: int = 0
    last_scan: Optional[datetime] = None
    created_at: datetime = field(default_factory=datetime.utcnow)


@dataclass
class Vulnerability:
    """Vulnerability record."""
    vuln_id: str
    cve_id: Optional[str]
    title: str
    description: str
    severity: Severity
    cvss_score: float
    asset_id: str
    status: VulnerabilityStatus
    scanner: str  # nessus, qualys, openvas, etc.
    discovered_at: datetime = field(default_factory=datetime.utcnow)
    remediation: str = ""
    patch_available: bool = False
    patch_id: Optional[str] = None
    exploit_available: bool = False
    exploit_maturity: str = ""  # unproven, poc, weaponized, active
    affected_component: str = ""
    port: Optional[int] = None
    references: List[str] = field(default_factory=list)
    assigned_to: Optional[str] = None
    due_date: Optional[datetime] = None
    remediated_at: Optional[datetime] = None


@dataclass
class Scan:
    """Vulnerability scan record."""
    scan_id: str
    name: str
    scanner: str
    status: str  # scheduled, running, completed, failed
    target_type: str  # asset, network, application
    targets: List[str]
    scheduled_at: Optional[datetime] = None
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    vulnerabilities_found: int = 0
    critical_count: int = 0
    high_count: int = 0
    medium_count: int = 0
    low_count: int = 0
    created_by: Optional[str] = None


@dataclass
class Patch:
    """Patch record."""
    patch_id: str
    name: str
    vendor: str
    product: str
    kb_article: Optional[str] = None
    severity: Severity = Severity.MEDIUM
    released_date: Optional[datetime] = None
    affected_assets: List[str] = field(default_factory=list)
    deployment_status: str = "pending"  # pending, deploying, deployed, failed
    deployed_count: int = 0
    failed_count: int = 0


class VulnerabilityManagementAgent:
    """
    Vulnerability Management Agent for scanning,
    tracking, and remediating security vulnerabilities.
    """

    def __init__(self, agent_id: str = "vulnman-agent"):
        self.agent_id = agent_id
        self.assets: Dict[str, Asset] = {}
        self.vulnerabilities: Dict[str, Vulnerability] = {}
        self.scans: Dict[str, Scan] = {}
        self.patches: Dict[str, Patch] = {}

        # CVSS calculator
        self.cvss_weights = {
            'AV:N': 0.85, 'AV:A': 0.62, 'AV:L': 0.55, 'AV:P': 0.2,
            'AC:L': 0.77, 'AC:H': 0.44,
            'PR:N': 0.85, 'PR:L': 0.62, 'PR:H': 0.27,
            'UI:N': 0.85, 'UI:R': 0.62,
            'S:U': 6.42, 'S:C': 7.52,
            'C:N': 0.0, 'C:L': 0.22, 'C:H': 0.56,
            'I:N': 0.0, 'I:L': 0.22, 'I:H': 0.56,
            'A:N': 0.0, 'A:L': 0.22, 'A:H': 0.56,
        }

    # ============================================
    # Asset Management
    # ============================================

    def add_asset(
        self,
        name: str,
        asset_type: AssetType,
        ip_address: Optional[str] = None,
        hostname: Optional[str] = None,
        os: Optional[str] = None,
        owner: Optional[str] = None,
        criticality: str = "medium",
        tags: Optional[List[str]] = None,
    ) -> Asset:
        """Add an asset to inventory."""
        asset = Asset(
            asset_id=self._generate_id("asset"),
            name=name,
            asset_type=asset_type,
            ip_address=ip_address,
            hostname=hostname,
            os=os,
            owner=owner,
            criticality=criticality,
            tags=tags or [],
        )

        self.assets[asset.asset_id] = asset
        logger.info(f"Added asset: {asset.name} ({asset.asset_type.value})")
        return asset

    def get_assets(
        self,
        asset_type: Optional[AssetType] = None,
        criticality: Optional[str] = None,
        owner: Optional[str] = None,
    ) -> List[Asset]:
        """Get assets with filtering."""
        assets = list(self.assets.values())

        if asset_type:
            assets = [a for a in assets if a.asset_type == asset_type]

        if criticality:
            assets = [a for a in assets if a.criticality == criticality]

        if owner:
            assets = [a for a in assets if a.owner == owner]

        return assets

    def update_asset_vuln_count(self, asset_id: str, count: int) -> bool:
        """Update asset vulnerability count."""
        if asset_id not in self.assets:
            return False

        self.assets[asset_id].vulnerabilities_count = count
        self.assets[asset_id].last_scan = datetime.utcnow()
        return True

    # ============================================
    # Vulnerability Management
    # ============================================

    def add_vulnerability(
        self,
        cve_id: Optional[str],
        title: str,
        description: str,
        cvss_score: float,
        asset_id: str,
        scanner: str,
        remediation: str = "",
        exploit_available: bool = False,
        affected_component: str = "",
        port: Optional[int] = None,
    ) -> Vulnerability:
        """Add a vulnerability finding."""
        severity = self._cvss_to_severity(cvss_score)

        vuln = Vulnerability(
            vuln_id=self._generate_id("vuln"),
            cve_id=cve_id,
            title=title,
            description=description,
            severity=severity,
            cvss_score=cvss_score,
            asset_id=asset_id,
            status=VulnerabilityStatus.NEW,
            scanner=scanner,
            remediation=remediation,
            exploit_available=exploit_available,
            affected_component=affected_component,
            port=port,
        )

        self.vulnerabilities[vuln.vuln_id] = vuln

        # Update asset count
        if asset_id in self.assets:
            self.assets[asset_id].vulnerabilities_count += 1

        logger.info(f"Added vulnerability: {vuln.title} ({vuln.severity.value})")
        return vuln

    def update_vulnerability_status(
        self,
        vuln_id: str,
        status: VulnerabilityStatus,
        assigned_to: Optional[str] = None,
        due_date: Optional[datetime] = None,
    ) -> bool:
        """Update vulnerability status."""
        if vuln_id not in self.vulnerabilities:
            return False

        vuln = self.vulnerabilities[vuln_id]
        vuln.status = status

        if assigned_to:
            vuln.assigned_to = assigned_to

        if due_date:
            vuln.due_date = due_date

        if status == VulnerabilityStatus.PATCHED:
            vuln.remediated_at = datetime.utcnow()

        return True

    def get_vulnerabilities(
        self,
        severity: Optional[Severity] = None,
        status: Optional[VulnerabilityStatus] = None,
        asset_id: Optional[str] = None,
        exploit_available: Optional[bool] = None,
    ) -> List[Vulnerability]:
        """Get vulnerabilities with filtering."""
        vulns = list(self.vulnerabilities.values())

        if severity:
            vulns = [v for v in vulns if v.severity == severity]

        if status:
            vulns = [v for v in vulns if v.status == status]

        if asset_id:
            vulns = [v for v in vulns if v.asset_id == asset_id]

        if exploit_available is not None:
            vulns = [v for v in vulns if v.exploit_available == exploit_available]

        return vulns

    def get_overdue_vulnerabilities(self) -> List[Vulnerability]:
        """Get vulnerabilities past due date."""
        now = datetime.utcnow()
        return [
            v for v in self.vulnerabilities.values()
            if v.due_date and v.due_date < now and v.status not in [
                VulnerabilityStatus.PATCHED,
                VulnerabilityStatus.MITIGATED,
                VulnerabilityStatus.ACCEPTED_RISK,
            ]
        ]

    # ============================================
    # Scan Management
    # ============================================

    def create_scan(
        self,
        name: str,
        scanner: str,
        target_type: str,
        targets: List[str],
        scheduled_at: Optional[datetime] = None,
        created_by: Optional[str] = None,
    ) -> Scan:
        """Create a vulnerability scan."""
        scan = Scan(
            scan_id=self._generate_id("scan"),
            name=name,
            scanner=scanner,
            status="scheduled" if scheduled_at else "running",
            target_type=target_type,
            targets=targets,
            scheduled_at=scheduled_at,
            started_at=datetime.utcnow() if not scheduled_at else None,
            created_by=created_by,
        )

        self.scans[scan.scan_id] = scan
        return scan

    def complete_scan(
        self,
        scan_id: str,
        vulnerabilities_found: int,
        critical: int = 0,
        high: int = 0,
        medium: int = 0,
        low: int = 0,
    ) -> bool:
        """Mark a scan as completed."""
        if scan_id not in self.scans:
            return False

        scan = self.scans[scan_id]
        scan.status = "completed"
        scan.completed_at = datetime.utcnow()
        scan.vulnerabilities_found = vulnerabilities_found
        scan.critical_count = critical
        scan.high_count = high
        scan.medium_count = medium
        scan.low_count = low

        return True

    def get_scans(self, status: Optional[str] = None) -> List[Scan]:
        """Get scans with filtering."""
        scans = list(self.scans.values())

        if status:
            scans = [s for s in scans if s.status == status]

        return scans

    # ============================================
    # Patch Management
    # ============================================

    def add_patch(
        self,
        name: str,
        vendor: str,
        product: str,
        severity: Severity = Severity.MEDIUM,
        kb_article: Optional[str] = None,
        affected_assets: Optional[List[str]] = None,
    ) -> Patch:
        """Add a patch to track."""
        patch = Patch(
            patch_id=self._generate_id("patch"),
            name=name,
            vendor=vendor,
            product=product,
            kb_article=kb_article,
            severity=severity,
            released_date=datetime.utcnow(),
            affected_assets=affected_assets or [],
        )

        self.patches[patch.patch_id] = patch
        return patch

    def deploy_patch(self, patch_id: str, asset_ids: List[str]) -> Dict[str, Any]:
        """Simulate patch deployment."""
        if patch_id not in self.patches:
            return {'success': False, 'error': 'Patch not found'}

        patch = self.patches[patch_id]
        deployed = 0
        failed = 0

        for asset_id in asset_ids:
            # Simulate deployment (90% success rate)
            if hash(asset_id) % 10 != 0:  # Simple simulation
                deployed += 1
            else:
                failed += 1

        patch.deployment_status = "deployed" if failed == 0 else "partial"
        patch.deployed_count += deployed
        patch.failed_count += failed

        return {
            'success': True,
            'deployed': deployed,
            'failed': failed,
            'patch_id': patch_id,
        }

    def get_patches(self, severity: Optional[Severity] = None) -> List[Patch]:
        """Get patches with filtering."""
        patches = list(self.patches.values())

        if severity:
            patches = [p for p in patches if p.severity == severity]

        return patches

    # ============================================
    # Reporting & Metrics
    # ============================================

    def get_vuln_metrics(self) -> Dict[str, Any]:
        """Get vulnerability management metrics."""
        vulns = list(self.vulnerabilities.values())

        by_severity = {}
        for sev in Severity:
            by_severity[sev.value] = len([v for v in vulns if v.severity == sev])

        by_status = {}
        for status in VulnerabilityStatus:
            by_status[status.value] = len([v for v in vulns if v.status == status])

        # Calculate risk score
        risk_score = (
            by_severity.get('critical', 0) * 10 +
            by_severity.get('high', 0) * 5 +
            by_severity.get('medium', 0) * 2 +
            by_severity.get('low', 0) * 1
        )

        # Exploitable vulns
        exploitable = len([v for v in vulns if v.exploit_available])

        # Overdue
        overdue = len(self.get_overdue_vulnerabilities())

        return {
            'total_vulnerabilities': len(vulns),
            'by_severity': by_severity,
            'by_status': by_status,
            'risk_score': risk_score,
            'exploitable': exploitable,
            'overdue': overdue,
            'assets_scanned': len([a for a in self.assets.values() if a.last_scan]),
            'total_assets': len(self.assets),
        }

    def get_asset_risk_profile(self, asset_id: str) -> Dict[str, Any]:
        """Get risk profile for an asset."""
        if asset_id not in self.assets:
            return {'error': 'Asset not found'}

        asset = self.assets[asset_id]
        asset_vulns = [v for v in self.vulnerabilities.values() if v.asset_id == asset_id]

        critical = len([v for v in asset_vulns if v.severity == Severity.CRITICAL])
        high = len([v for v in asset_vulns if v.severity == Severity.HIGH])
        exploitable = len([v for v in asset_vulns if v.exploit_available])

        risk_score = critical * 10 + high * 5 + len(asset_vulns) * 2

        return {
            'asset_id': asset_id,
            'name': asset.name,
            'criticality': asset.criticality,
            'total_vulnerabilities': len(asset_vulns),
            'critical': critical,
            'high': high,
            'exploitable': exploitable,
            'risk_score': risk_score,
            'last_scan': asset.last_scan.isoformat() if asset.last_scan else None,
        }

    def get_remediation_priority(self, limit: int = 20) -> List[Dict[str, Any]]:
        """Get prioritized remediation list."""
        vulns = list(self.vulnerabilities.values())

        # Filter out already handled
        active = [
            v for v in vulns
            if v.status not in [
                VulnerabilityStatus.PATCHED,
                VulnerabilityStatus.MITIGATED,
                VulnerabilityStatus.ACCEPTED_RISK,
                VulnerabilityStatus.FALSE_POSITIVE,
            ]
        ]

        # Score and sort
        scored = []
        for v in active:
            score = v.cvss_score * 10
            if v.exploit_available:
                score *= 1.5
            if v.asset_id in self.assets:
                crit = self.assets[v.asset_id].criticality
                if crit == 'critical':
                    score *= 1.5
                elif crit == 'high':
                    score *= 1.2

            scored.append((score, v))

        scored.sort(key=lambda x: x[0], reverse=True)

        return [
            {
                'vuln_id': v.vuln_id,
                'title': v.title,
                'cve_id': v.cve_id,
                'cvss_score': v.cvss_score,
                'severity': v.severity.value,
                'asset': self.assets.get(v.asset_id, {}).name if v.asset_id in self.assets else v.asset_id,
                'exploit_available': v.exploit_available,
                'priority_score': round(score, 1),
            }
            for score, v in scored[:limit]
        ]

    # ============================================
    # Utilities
    # ============================================

    def _cvss_to_severity(self, score: float) -> Severity:
        """Convert CVSS score to severity."""
        if score == 0:
            return Severity.NONE
        elif score <= 3.9:
            return Severity.LOW
        elif score <= 6.9:
            return Severity.MEDIUM
        elif score <= 8.9:
            return Severity.HIGH
        else:
            return Severity.CRITICAL

    def _generate_id(self, prefix: str) -> str:
        """Generate a unique ID."""
        timestamp = datetime.utcnow().strftime('%Y%m%d%H%M%S')
        random_suffix = secrets.token_hex(4)
        return f"{prefix}-{timestamp}-{random_suffix}"

    def get_state(self) -> Dict[str, Any]:
        """Get agent state summary."""
        vulns = list(self.vulnerabilities.values())
        return {
            'agent_id': self.agent_id,
            'assets_count': len(self.assets),
            'vulnerabilities_count': len(vulns),
            'critical_vulns': len([v for v in vulns if v.severity == Severity.CRITICAL]),
            'high_vulns': len([v for v in vulns if v.severity == Severity.HIGH]),
            'exploitable_vulns': len([v for v in vulns if v.exploit_available]),
            'scans_count': len(self.scans),
            'patches_count': len(self.patches),
        }


def get_capabilities() -> Dict[str, Any]:
    """Return agent capabilities for orchestration."""
    return {
        'agent_type': 'vulnerability_management',
        'version': '1.0.0',
        'capabilities': [
            'add_asset',
            'get_assets',
            'add_vulnerability',
            'update_vulnerability_status',
            'get_vulnerabilities',
            'get_overdue_vulnerabilities',
            'create_scan',
            'complete_scan',
            'get_scans',
            'add_patch',
            'deploy_patch',
            'get_patches',
            'get_vuln_metrics',
            'get_asset_risk_profile',
            'get_remediation_priority',
        ],
        'severities': [s.value for s in Severity],
        'vulnerability_statuses': [s.value for s in VulnerabilityStatus],
        'asset_types': [t.value for t in AssetType],
    }


if __name__ == "__main__":
    agent = VulnerabilityManagementAgent()

    # Add assets
    server = agent.add_asset(
        name="web-server-01",
        asset_type=AssetType.SERVER,
        ip_address="10.0.1.10",
        hostname="web01.example.com",
        os="Ubuntu 22.04",
        owner="ops@example.com",
        criticality="high",
    )

    print(f"Added asset: {server.name}")

    # Add vulnerabilities
    vuln1 = agent.add_vulnerability(
        cve_id="CVE-2024-1234",
        title="Remote Code Execution in Apache",
        description="Critical RCE vulnerability in Apache HTTP Server",
        cvss_score=9.8,
        asset_id=server.asset_id,
        scanner="nessus",
        remediation="Upgrade Apache to version 2.4.58 or later",
        exploit_available=True,
        affected_component="apache2",
        port=80,
    )

    vuln2 = agent.add_vulnerability(
        cve_id="CVE-2024-5678",
        title="SQL Injection in Web App",
        description="SQL injection vulnerability in login form",
        cvss_score=7.5,
        asset_id=server.asset_id,
        scanner="burp",
        remediation="Use parameterized queries",
        exploit_available=False,
        affected_component="webapp",
        port=443,
    )

    print(f"Added {len(agent.vulnerabilities)} vulnerabilities")

    # Create scan
    scan = agent.create_scan(
        name="Weekly Vulnerability Scan",
        scanner="nessus",
        target_type="network",
        targets=["10.0.1.0/24"],
        created_by="security@example.com",
    )

    agent.complete_scan(scan.scan_id, vulnerabilities_found=15, critical=2, high=5, medium=6, low=2)

    print(f"Scan completed: {scan.vulnerabilities_found} vulns found")

    # Add patch
    patch = agent.add_patch(
        name="Apache Security Update",
        vendor="Apache",
        product="HTTP Server",
        severity=Severity.CRITICAL,
        affected_assets=[server.asset_id],
    )

    # Deploy patch
    result = agent.deploy_patch(patch.patch_id, [server.asset_id])
    print(f"Patch deployed: {result['deployed']} successful, {result['failed']} failed")

    # Get metrics
    metrics = agent.get_vuln_metrics()
    print(f"\nTotal Vulnerabilities: {metrics['total_vulnerabilities']}")
    print(f"Risk Score: {metrics['risk_score']}")
    print(f"Exploitable: {metrics['exploitable']}")

    # Get remediation priority
    priority = agent.get_remediation_priority()
    print(f"\nTop Remediation Priorities:")
    for p in priority[:3]:
        print(f"  - {p['title']} (Score: {p['priority_score']})")

    print(f"\nState: {agent.get_state()}")
