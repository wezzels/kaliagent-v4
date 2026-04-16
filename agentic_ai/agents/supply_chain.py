"""
SupplyChainAgent - Software Supply Chain Security
==================================================

Provides SBOM management, dependency tracking, vulnerability correlation,
vendor risk assessment, and supply chain security monitoring.
"""

import logging
import secrets
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from typing import Any, Dict, List, Optional


logger = logging.getLogger(__name__)


class PackageType(Enum):
    """Package types."""
    NPM = "npm"
    PYPI = "pypi"
    MAVEN = "maven"
    GEM = "gem"
    NUGET = "nuget"
    GO = "go"
    CARGO = "cargo"
    CONDA = "conda"
    DOCKER = "docker"
    OS = "os_package"


class VulnerabilitySeverity(Enum):
    """Vulnerability severity."""
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


class RiskLevel(Enum):
    """Vendor risk levels."""
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


class SBOMFormat(Enum):
    """SBOM formats."""
    SPDX = "spdx"
    CYCLONEDX = "cyclonedx"
    SWID = "swid"


@dataclass
class Package:
    """Software package."""
    package_id: str
    name: str
    version: str
    package_type: PackageType
    license: str = ""
    homepage: str = ""
    repository: str = ""
    direct_dependency: bool = True
    parent_package: Optional[str] = None
    vulnerabilities: List[str] = field(default_factory=list)
    added_at: datetime = field(default_factory=datetime.utcnow)


@dataclass
class SBOM:
    """Software Bill of Materials."""
    sbom_id: str
    name: str
    version: str
    format: SBOMFormat
    project: str
    packages_count: int = 0
    vulnerabilities_count: int = 0
    critical_vulns: int = 0
    created_at: datetime = field(default_factory=datetime.utcnow)
    packages: List[str] = field(default_factory=list)


@dataclass
class Vulnerability:
    """Package vulnerability."""
    vuln_id: str
    cve_id: str
    package_id: str
    package_name: str
    affected_versions: str
    fixed_version: str
    severity: VulnerabilitySeverity
    cvss_score: float
    description: str
    references: List[str] = field(default_factory=list)
    discovered_at: datetime = field(default_factory=datetime.utcnow)
    status: str = "open"  # open, in_progress, patched, accepted


@dataclass
class Vendor:
    """Software vendor."""
    vendor_id: str
    name: str
    type: str  # software, service, cloud, hardware
    criticality: str  # critical, high, medium, low
    contact_email: str = ""
    security_contact: str = ""
    risk_score: float = 0.0
    last_assessment: Optional[datetime] = None
    certifications: List[str] = field(default_factory=list)
    contracts: List[str] = field(default_factory=list)
    incidents: List[str] = field(default_factory=list)


@dataclass
class VendorAssessment:
    """Vendor risk assessment."""
    assessment_id: str
    vendor_id: str
    assessment_type: str  # initial, annual, incident-triggered
    status: str  # planned, in_progress, completed
    assessor: str
    security_score: float = 0.0
    privacy_score: float = 0.0
    compliance_score: float = 0.0
    overall_score: float = 0.0
    findings: List[Dict[str, Any]] = field(default_factory=list)
    recommendations: List[str] = field(default_factory=list)
    created_at: datetime = field(default_factory=datetime.utcnow)
    completed_at: Optional[datetime] = None


@dataclass
class SecurityIncident:
    """Supply chain security incident."""
    incident_id: str
    title: str
    description: str
    severity: str
    affected_packages: List[str] = field(default_factory=list)
    affected_vendors: List[str] = field(default_factory=list)
    status: str = "reported"  # reported, investigating, contained, resolved
    root_cause: str = ""
    remediation: List[str] = field(default_factory=list)
    reported_at: datetime = field(default_factory=datetime.utcnow)
    resolved_at: Optional[datetime] = None


class SupplyChainAgent:
    """
    Supply Chain Agent for SBOM management, dependency tracking,
    vendor risk assessment, and supply chain security.
    """
    
    def __init__(self, agent_id: str = "supply-chain-agent"):
        self.agent_id = agent_id
        self.packages: Dict[str, Package] = {}
        self.sboms: Dict[str, SBOM] = {}
        self.vulnerabilities: Dict[str, Vulnerability] = {}
        self.vendors: Dict[str, Vendor] = {}
        self.assessments: Dict[str, VendorAssessment] = {}
        self.incidents: Dict[str, SecurityIncident] = {}
        
        # Risk assessment criteria
        self.risk_criteria = {
            'security_practices': 0.3,
            'compliance': 0.25,
            'incident_history': 0.2,
            'financial_stability': 0.15,
            'data_handling': 0.1,
        }
    
    # ============================================
    # Package Management
    # ============================================
    
    def add_package(
        self,
        name: str,
        version: str,
        package_type: PackageType,
        license: str = "",
        direct_dependency: bool = True,
        parent_package: Optional[str] = None,
    ) -> Package:
        """Add package to inventory."""
        package = Package(
            package_id=self._generate_id("pkg"),
            name=name,
            version=version,
            package_type=package_type,
            license=license,
            direct_dependency=direct_dependency,
            parent_package=parent_package,
        )
        
        self.packages[package.package_id] = package
        return package
    
    def get_packages(
        self,
        package_type: Optional[PackageType] = None,
        direct_only: bool = False,
    ) -> List[Package]:
        """Get packages with filtering."""
        packages = list(self.packages.values())
        
        if package_type:
            packages = [p for p in packages if p.package_type == package_type]
        
        if direct_only:
            packages = [p for p in packages if p.direct_dependency]
        
        return packages
    
    def get_dependency_tree(self, package_id: str) -> Dict[str, Any]:
        """Get dependency tree for a package."""
        if package_id not in self.packages:
            return {'error': 'Package not found'}
        
        package = self.packages[package_id]
        
        # Find children
        children = [
            p for p in self.packages.values()
            if p.parent_package == package_id
        ]
        
        return {
            'package_id': package_id,
            'name': package.name,
            'version': package.version,
            'vulnerabilities': len(package.vulnerabilities),
            'direct_dependencies': len(children),
            'children': [
                self.get_dependency_tree(c.package_id)
                for c in children
            ],
        }
    
    # ============================================
    # SBOM Management
    # ============================================
    
    def create_sbom(
        self,
        name: str,
        version: str,
        format: SBOMFormat,
        project: str,
        packages: Optional[List[str]] = None,
    ) -> SBOM:
        """Create SBOM for a project."""
        sbom = SBOM(
            sbom_id=self._generate_id("sbom"),
            name=name,
            version=version,
            format=format,
            project=project,
            packages=packages or [],
        )
        
        sbom.packages_count = len(sbom.packages)
        
        self.sboms[sbom.sbom_id] = sbom
        return sbom
    
    def analyze_sbom(self, sbom_id: str) -> Dict[str, Any]:
        """Analyze SBOM for vulnerabilities."""
        if sbom_id not in self.sboms:
            return {'error': 'SBOM not found'}
        
        sbom = self.sboms[sbom_id]
        
        # Count vulnerabilities
        vulns = [
            v for v in self.vulnerabilities.values()
            if v.package_id in sbom.packages
        ]
        
        sbom.vulnerabilities_count = len(vulns)
        sbom.critical_vulns = len([v for v in vulns if v.severity == VulnerabilitySeverity.CRITICAL])
        
        return {
            'sbom_id': sbom_id,
            'packages_count': sbom.packages_count,
            'vulnerabilities': {
                'total': sbom.vulnerabilities_count,
                'critical': sbom.critical_vulns,
                'high': len([v for v in vulns if v.severity == VulnerabilitySeverity.HIGH]),
                'medium': len([v for v in vulns if v.severity == VulnerabilitySeverity.MEDIUM]),
                'low': len([v for v in vulns if v.severity == VulnerabilitySeverity.LOW]),
            },
        }
    
    def get_sboms(self, format: Optional[SBOMFormat] = None) -> List[SBOM]:
        """Get SBOMs with filtering."""
        sboms = list(self.sboms.values())
        
        if format:
            sboms = [s for s in sboms if s.format == format]
        
        return sboms
    
    # ============================================
    # Vulnerability Management
    # ============================================
    
    def add_vulnerability(
        self,
        cve_id: str,
        package_id: str,
        affected_versions: str,
        fixed_version: str,
        cvss_score: float,
        description: str,
        references: Optional[List[str]] = None,
    ) -> Vulnerability:
        """Add vulnerability for a package."""
        if package_id not in self.packages:
            raise ValueError(f"Package {package_id} not found")
        
        # Determine severity from CVSS
        if cvss_score >= 9.0:
            severity = VulnerabilitySeverity.CRITICAL
        elif cvss_score >= 7.0:
            severity = VulnerabilitySeverity.HIGH
        elif cvss_score >= 4.0:
            severity = VulnerabilitySeverity.MEDIUM
        else:
            severity = VulnerabilitySeverity.LOW
        
        vuln = Vulnerability(
            vuln_id=self._generate_id("vuln"),
            cve_id=cve_id,
            package_id=package_id,
            package_name=self.packages[package_id].name,
            affected_versions=affected_versions,
            fixed_version=fixed_version,
            severity=severity,
            cvss_score=cvss_score,
            description=description,
            references=references or [],
        )
        
        self.vulnerabilities[vuln.vuln_id] = vuln
        
        # Update package
        if vuln.vuln_id not in self.packages[package_id].vulnerabilities:
            self.packages[package_id].vulnerabilities.append(vuln.vuln_id)
        
        return vuln
    
    def update_vulnerability_status(
        self,
        vuln_id: str,
        status: str,
    ) -> bool:
        """Update vulnerability status."""
        if vuln_id not in self.vulnerabilities:
            return False
        
        self.vulnerabilities[vuln_id].status = status
        
        if status == "patched":
            self.vulnerabilities[vuln_id].resolved_at = datetime.utcnow()
        
        return True
    
    def get_vulnerabilities(
        self,
        severity: Optional[VulnerabilitySeverity] = None,
        status: Optional[str] = None,
        package_id: Optional[str] = None,
    ) -> List[Vulnerability]:
        """Get vulnerabilities with filtering."""
        vulns = list(self.vulnerabilities.values())
        
        if severity:
            vulns = [v for v in vulns if v.severity == severity]
        
        if status:
            vulns = [v for v in vulns if v.status == status]
        
        if package_id:
            vulns = [v for v in vulns if v.package_id == package_id]
        
        return vulns
    
    # ============================================
    # Vendor Management
    # ============================================
    
    def add_vendor(
        self,
        name: str,
        type: str,
        criticality: str,
        contact_email: str = "",
        security_contact: str = "",
        certifications: Optional[List[str]] = None,
    ) -> Vendor:
        """Add vendor to registry."""
        vendor = Vendor(
            vendor_id=self._generate_id("vendor"),
            name=name,
            type=type,
            criticality=criticality,
            contact_email=contact_email,
            security_contact=security_contact,
            certifications=certifications or [],
        )
        
        self.vendors[vendor.vendor_id] = vendor
        return vendor
    
    def calculate_vendor_risk(self, vendor_id: str) -> float:
        """Calculate vendor risk score."""
        if vendor_id not in self.vendors:
            return 0.0
        
        vendor = self.vendors[vendor_id]
        
        # Base score from criticality
        criticality_scores = {
            'critical': 1.0,
            'high': 0.75,
            'medium': 0.5,
            'low': 0.25,
        }
        
        base_score = criticality_scores.get(vendor.criticality, 0.5)
        
        # Adjust for certifications
        cert_bonus = min(0.2, len(vendor.certifications) * 0.05)
        
        # Adjust for incidents
        incident_penalty = min(0.3, len(vendor.incidents) * 0.1)
        
        risk_score = base_score - cert_bonus + incident_penalty
        
        vendor.risk_score = risk_score
        return risk_score
    
    def get_vendors(
        self,
        type: Optional[str] = None,
        criticality: Optional[str] = None,
    ) -> List[Vendor]:
        """Get vendors with filtering."""
        vendors = list(self.vendors.values())
        
        if type:
            vendors = [v for v in vendors if v.type == type]
        
        if criticality:
            vendors = [v for v in vendors if v.criticality == criticality]
        
        return vendors
    
    # ============================================
    # Vendor Assessment
    # ============================================
    
    def create_assessment(
        self,
        vendor_id: str,
        assessment_type: str,
        assessor: str,
    ) -> VendorAssessment:
        """Create vendor assessment."""
        if vendor_id not in self.vendors:
            raise ValueError(f"Vendor {vendor_id} not found")
        
        assessment = VendorAssessment(
            assessment_id=self._generate_id("assess"),
            vendor_id=vendor_id,
            assessment_type=assessment_type,
            status="planned",
            assessor=assessor,
        )
        
        self.assessments[assessment.assessment_id] = assessment
        return assessment
    
    def complete_assessment(
        self,
        assessment_id: str,
        security_score: float,
        privacy_score: float,
        compliance_score: float,
        findings: Optional[List[Dict[str, Any]]] = None,
        recommendations: Optional[List[str]] = None,
    ) -> bool:
        """Complete vendor assessment."""
        if assessment_id not in self.assessments:
            return False
        
        assessment = self.assessments[assessment_id]
        assessment.status = "completed"
        assessment.completed_at = datetime.utcnow()
        assessment.security_score = security_score
        assessment.privacy_score = privacy_score
        assessment.compliance_score = compliance_score
        
        # Calculate overall score
        assessment.overall_score = (
            security_score * 0.4 +
            privacy_score * 0.3 +
            compliance_score * 0.3
        )
        
        assessment.findings = findings or []
        assessment.recommendations = recommendations or []
        
        # Update vendor
        vendor = self.vendors[assessment.vendor_id]
        vendor.last_assessment = datetime.utcnow()
        vendor.risk_score = 1.0 - (assessment.overall_score / 100)
        
        return True
    
    def get_assessments(
        self,
        vendor_id: Optional[str] = None,
        status: Optional[str] = None,
    ) -> List[VendorAssessment]:
        """Get assessments with filtering."""
        assessments = list(self.assessments.values())
        
        if vendor_id:
            assessments = [a for a in assessments if a.vendor_id == vendor_id]
        
        if status:
            assessments = [a for a in assessments if a.status == status]
        
        return assessments
    
    # ============================================
    # Incident Management
    # ============================================
    
    def report_incident(
        self,
        title: str,
        description: str,
        severity: str,
        affected_packages: Optional[List[str]] = None,
        affected_vendors: Optional[List[str]] = None,
    ) -> SecurityIncident:
        """Report supply chain security incident."""
        incident = SecurityIncident(
            incident_id=self._generate_id("incident"),
            title=title,
            description=description,
            severity=severity,
            affected_packages=affected_packages or [],
            affected_vendors=affected_vendors or [],
        )
        
        self.incidents[incident.incident_id] = incident
        
        # Update vendor incidents
        for vendor_id in incident.affected_vendors:
            if vendor_id in self.vendors:
                self.vendors[vendor_id].incidents.append(incident.incident_id)
        
        return incident
    
    def resolve_incident(
        self,
        incident_id: str,
        root_cause: str,
        remediation: List[str],
    ) -> bool:
        """Resolve security incident."""
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
        severity: Optional[str] = None,
        status: Optional[str] = None,
    ) -> List[SecurityIncident]:
        """Get incidents with filtering."""
        incidents = list(self.incidents.values())
        
        if severity:
            incidents = [i for i in incidents if i.severity == severity]
        
        if status:
            incidents = [i for i in incidents if i.status == status]
        
        return incidents
    
    # ============================================
    # Reporting
    # ============================================
    
    def get_supply_chain_report(self) -> Dict[str, Any]:
        """Generate supply chain security report."""
        packages = list(self.packages.values())
        vulns = list(self.vulnerabilities.values())
        vendors = list(self.vendors.values())
        incidents = list(self.incidents.values())
        
        # Package stats
        by_type = {}
        for ptype in PackageType:
            by_type[ptype.value] = len([p for p in packages if p.package_type == ptype])
        
        # Vulnerability stats
        by_severity = {}
        for sev in VulnerabilitySeverity:
            by_severity[sev.value] = len([v for v in vulns if v.severity == sev])
        
        # Vendor stats
        by_criticality = {}
        for crit in ['critical', 'high', 'medium', 'low']:
            by_criticality[crit] = len([v for v in vendors if v.criticality == crit])
        
        return {
            'packages': {
                'total': len(packages),
                'by_type': by_type,
                'direct': len([p for p in packages if p.direct_dependency]),
                'transitive': len([p for p in packages if not p.direct_dependency]),
            },
            'sboms': {
                'total': len(self.sboms),
            },
            'vulnerabilities': {
                'total': len(vulns),
                'by_severity': by_severity,
                'open': len([v for v in vulns if v.status == 'open']),
            },
            'vendors': {
                'total': len(vendors),
                'by_criticality': by_criticality,
                'assessed': len([v for v in vendors if v.last_assessment]),
            },
            'incidents': {
                'total': len(incidents),
                'open': len([i for i in incidents if i.status != 'resolved']),
            },
        }
    
    def get_vendor_risk_report(self, vendor_id: str) -> Dict[str, Any]:
        """Get vendor risk report."""
        if vendor_id not in self.vendors:
            return {'error': 'Vendor not found'}
        
        vendor = self.vendors[vendor_id]
        assessments = self.get_assessments(vendor_id=vendor_id)
        incidents = [i for i in self.incidents.values() if vendor_id in i.affected_vendors]
        
        return {
            'vendor': {
                'vendor_id': vendor_id,
                'name': vendor.name,
                'type': vendor.type,
                'criticality': vendor.criticality,
                'risk_score': vendor.risk_score,
            },
            'assessments': {
                'total': len(assessments),
                'latest_score': assessments[-1].overall_score if assessments else None,
                'last_assessment': vendor.last_assessment.isoformat() if vendor.last_assessment else None,
            },
            'incidents': {
                'total': len(incidents),
                'open': len([i for i in incidents if i.status != 'resolved']),
            },
            'certifications': vendor.certifications,
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
            'packages_count': len(self.packages),
            'sboms_count': len(self.sboms),
            'vulnerabilities_count': len(self.vulnerabilities),
            'critical_vulns': len([v for v in self.vulnerabilities.values() if v.severity == VulnerabilitySeverity.CRITICAL]),
            'vendors_count': len(self.vendors),
            'assessments_count': len(self.assessments),
            'incidents_count': len(self.incidents),
            'open_incidents': len([i for i in self.incidents.values() if i.status != 'resolved']),
        }


def get_capabilities() -> Dict[str, Any]:
    """Return agent capabilities for orchestration."""
    return {
        'agent_type': 'supply_chain',
        'version': '1.0.0',
        'capabilities': [
            'add_package',
            'get_packages',
            'get_dependency_tree',
            'create_sbom',
            'analyze_sbom',
            'get_sboms',
            'add_vulnerability',
            'update_vulnerability_status',
            'get_vulnerabilities',
            'add_vendor',
            'calculate_vendor_risk',
            'get_vendors',
            'create_assessment',
            'complete_assessment',
            'get_assessments',
            'report_incident',
            'resolve_incident',
            'get_incidents',
            'get_supply_chain_report',
            'get_vendor_risk_report',
        ],
        'package_types': [t.value for t in PackageType],
        'vulnerability_severities': [s.value for s in VulnerabilitySeverity],
        'sbom_formats': [f.value for f in SBOMFormat],
        'risk_levels': [l.value for l in RiskLevel],
    }


if __name__ == "__main__":
    agent = SupplyChainAgent()
    
    # Add packages
    pkg1 = agent.add_package(
        name="lodash",
        version="4.17.21",
        package_type=PackageType.NPM,
        license="MIT",
    )
    
    pkg2 = agent.add_package(
        name="express",
        version="4.18.2",
        package_type=PackageType.NPM,
        license="MIT",
    )
    
    # Add transitive dependency
    pkg3 = agent.add_package(
        name="body-parser",
        version="1.20.0",
        package_type=PackageType.NPM,
        license="MIT",
        direct_dependency=False,
        parent_package=pkg2.package_id,
    )
    
    print(f"Added {len(agent.packages)} packages")
    
    # Create SBOM
    sbom = agent.create_sbom(
        name="Web App SBOM",
        version="1.0",
        format=SBOMFormat.CYCLONEDX,
        project="web-app",
        packages=[pkg1.package_id, pkg2.package_id, pkg3.package_id],
    )
    
    # Add vulnerability
    vuln = agent.add_vulnerability(
        cve_id="CVE-2021-23337",
        package_id=pkg1.package_id,
        affected_versions="<4.17.21",
        fixed_version="4.17.21",
        cvss_score=7.2,
        description="Command injection in lodash",
        references=["https://nvd.nist.gov/vuln/detail/CVE-2021-23337"],
    )
    
    print(f"Added vulnerability: {vuln.cve_id}")
    
    # Analyze SBOM
    analysis = agent.analyze_sbom(sbom.sbom_id)
    print(f"SBOM Analysis: {analysis['vulnerabilities']}")
    
    # Add vendor
    vendor = agent.add_vendor(
        name="npm Inc",
        type="software",
        criticality="high",
        contact_email="security@npmjs.com",
        certifications=['SOC2'],
    )
    
    # Create assessment
    assessment = agent.create_assessment(
        vendor.vendor_id,
        assessment_type="annual",
        assessor="security-team@example.com",
    )
    
    # Complete assessment
    agent.complete_assessment(
        assessment.assessment_id,
        security_score=85.0,
        privacy_score=90.0,
        compliance_score=95.0,
        findings=[{'category': 'security', 'finding': 'Strong practices'}],
        recommendations=["Continue current practices"],
    )
    
    print(f"Vendor risk score: {vendor.risk_score}")
    
    # Get report
    report = agent.get_supply_chain_report()
    print(f"\nSupply Chain Report:")
    print(f"  Packages: {report['packages']['total']}")
    print(f"  Vulnerabilities: {report['vulnerabilities']['total']}")
    print(f"  Vendors: {report['vendors']['total']}")
    
    print(f"\nState: {agent.get_state()}")
