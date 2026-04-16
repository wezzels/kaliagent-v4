"""
SupplyChainAgent Tests
======================

Unit tests for SupplyChainAgent - SBOM, dependencies & vendor risk.
"""

import pytest
from datetime import datetime, timedelta

from agentic_ai.agents.supply_chain import (
    SupplyChainAgent,
    PackageType,
    VulnerabilitySeverity,
    RiskLevel,
    SBOMFormat,
)


class TestSupplyChainAgent:
    """Test SupplyChainAgent."""
    
    @pytest.fixture
    def sc_agent(self):
        """Create SupplyChainAgent instance."""
        return SupplyChainAgent()
    
    def test_add_package(self, sc_agent):
        """Test adding package."""
        pkg = sc_agent.add_package(
            name="lodash",
            version="4.17.21",
            package_type=PackageType.NPM,
            license="MIT",
            direct_dependency=True,
        )
        
        assert pkg.package_id.startswith("pkg-")
        assert pkg.name == "lodash"
        assert pkg.version == "4.17.21"
        assert pkg.package_type == PackageType.NPM
    
    def test_add_transitive_dependency(self, sc_agent):
        """Test adding transitive dependency."""
        parent = sc_agent.add_package("express", "4.18.2", PackageType.NPM)
        
        child = sc_agent.add_package(
            name="body-parser",
            version="1.20.0",
            package_type=PackageType.NPM,
            direct_dependency=False,
            parent_package=parent.package_id,
        )
        
        assert child.parent_package == parent.package_id
        assert child.direct_dependency is False
    
    def test_get_packages_by_type(self, sc_agent):
        """Test filtering packages by type."""
        sc_agent.add_package("lodash", "4.17.21", PackageType.NPM)
        sc_agent.add_package("requests", "2.28.0", PackageType.PYPI)
        sc_agent.add_package("spring-core", "5.3.0", PackageType.MAVEN)
        
        npm = sc_agent.get_packages(package_type=PackageType.NPM)
        pypi = sc_agent.get_packages(package_type=PackageType.PYPI)
        
        assert len(npm) == 1
        assert len(pypi) == 1
    
    def test_get_dependency_tree(self, sc_agent):
        """Test dependency tree generation."""
        root = sc_agent.add_package("app", "1.0.0", PackageType.NPM)
        child1 = sc_agent.add_package("dep1", "1.0.0", PackageType.NPM, parent_package=root.package_id)
        child2 = sc_agent.add_package("dep2", "1.0.0", PackageType.NPM, parent_package=root.package_id)
        
        tree = sc_agent.get_dependency_tree(root.package_id)
        
        assert tree['package_id'] == root.package_id
        assert tree['direct_dependencies'] == 2
        assert len(tree['children']) == 2
    
    def test_create_sbom(self, sc_agent):
        """Test creating SBOM."""
        pkg1 = sc_agent.add_package("lodash", "4.17.21", PackageType.NPM)
        pkg2 = sc_agent.add_package("express", "4.18.2", PackageType.NPM)
        
        sbom = sc_agent.create_sbom(
            name="App SBOM",
            version="1.0",
            format=SBOMFormat.CYCLONEDX,
            project="web-app",
            packages=[pkg1.package_id, pkg2.package_id],
        )
        
        assert sbom.sbom_id.startswith("sbom-")
        assert sbom.format == SBOMFormat.CYCLONEDX
        assert sbom.packages_count == 2
    
    def test_analyze_sbom(self, sc_agent):
        """Test SBOM vulnerability analysis."""
        pkg = sc_agent.add_package("lodash", "4.17.20", PackageType.NPM)
        
        sbom = sc_agent.create_sbom(
            "Test SBOM", "1.0", SBOMFormat.SPDX, "test",
            packages=[pkg.package_id],
        )
        
        sc_agent.add_vulnerability(
            cve_id="CVE-2021-23337",
            package_id=pkg.package_id,
            affected_versions="<4.17.21",
            fixed_version="4.17.21",
            cvss_score=7.2,
            description="Command injection",
        )
        
        analysis = sc_agent.analyze_sbom(sbom.sbom_id)
        
        assert analysis['vulnerabilities']['total'] == 1
        assert analysis['vulnerabilities']['high'] == 1
    
    def test_add_vulnerability(self, sc_agent):
        """Test adding vulnerability."""
        pkg = sc_agent.add_package("lodash", "4.17.20", PackageType.NPM)
        
        vuln = sc_agent.add_vulnerability(
            cve_id="CVE-2021-23337",
            package_id=pkg.package_id,
            affected_versions="<4.17.21",
            fixed_version="4.17.21",
            cvss_score=7.2,
            description="Command injection vulnerability",
        )
        
        assert vuln.vuln_id.startswith("vuln-")
        assert vuln.cve_id == "CVE-2021-23337"
        assert vuln.severity == VulnerabilitySeverity.HIGH
        assert vuln.cvss_score == 7.2
        assert vuln.status == "open"
    
    def test_vulnerability_severity_from_cvss(self, sc_agent):
        """Test CVSS to severity mapping."""
        pkg = sc_agent.add_package("test", "1.0", PackageType.NPM)
        
        # Critical (>= 9.0)
        v1 = sc_agent.add_vulnerability("CVE-1", pkg.package_id, "*", "fixed", 9.5, "desc")
        assert v1.severity == VulnerabilitySeverity.CRITICAL
        
        # High (>= 7.0)
        v2 = sc_agent.add_vulnerability("CVE-2", pkg.package_id, "*", "fixed", 7.5, "desc")
        assert v2.severity == VulnerabilitySeverity.HIGH
        
        # Medium (>= 4.0)
        v3 = sc_agent.add_vulnerability("CVE-3", pkg.package_id, "*", "fixed", 5.5, "desc")
        assert v3.severity == VulnerabilitySeverity.MEDIUM
        
        # Low (< 4.0)
        v4 = sc_agent.add_vulnerability("CVE-4", pkg.package_id, "*", "fixed", 2.0, "desc")
        assert v4.severity == VulnerabilitySeverity.LOW
    
    def test_update_vulnerability_status(self, sc_agent):
        """Test updating vulnerability status."""
        pkg = sc_agent.add_package("test", "1.0", PackageType.NPM)
        
        vuln = sc_agent.add_vulnerability(
            "CVE-TEST", pkg.package_id, "*", "fixed", 7.0, "desc",
        )
        
        result = sc_agent.update_vulnerability_status(vuln.vuln_id, "patched")
        
        assert result is True
        assert vuln.status == "patched"
    
    def test_get_vulnerabilities_by_severity(self, sc_agent):
        """Test filtering vulnerabilities by severity."""
        pkg = sc_agent.add_package("test", "1.0", PackageType.NPM)
        
        sc_agent.add_vulnerability("CVE-1", pkg.package_id, "*", "fixed", 9.5, "desc")
        sc_agent.add_vulnerability("CVE-2", pkg.package_id, "*", "fixed", 7.5, "desc")
        sc_agent.add_vulnerability("CVE-3", pkg.package_id, "*", "fixed", 5.5, "desc")
        
        critical = sc_agent.get_vulnerabilities(severity=VulnerabilitySeverity.CRITICAL)
        high = sc_agent.get_vulnerabilities(severity=VulnerabilitySeverity.HIGH)
        
        assert len(critical) == 1
        assert len(high) == 1
    
    def test_add_vendor(self, sc_agent):
        """Test adding vendor."""
        vendor = sc_agent.add_vendor(
            name="npm Inc",
            type="software",
            criticality="high",
            contact_email="security@npmjs.com",
            security_contact="security@npmjs.com",
            certifications=['SOC2', 'ISO27001'],
        )
        
        assert vendor.vendor_id.startswith("vendor-")
        assert vendor.criticality == "high"
        assert len(vendor.certifications) == 2
    
    def test_calculate_vendor_risk(self, sc_agent):
        """Test vendor risk calculation."""
        vendor = sc_agent.add_vendor("Test Vendor", "software", "critical")
        
        risk = sc_agent.calculate_vendor_risk(vendor.vendor_id)
        
        # Critical base = 1.0, with 0 certs and 0 incidents
        assert risk == 1.0
        assert vendor.risk_score == 1.0
    
    def test_vendor_risk_with_certifications(self, sc_agent):
        """Test vendor risk with certifications."""
        vendor = sc_agent.add_vendor(
            "Secure Vendor", "software", "high",
            certifications=['SOC2', 'ISO27001', 'PCI-DSS'],
        )
        
        risk = sc_agent.calculate_vendor_risk(vendor.vendor_id)
        
        # High base = 0.75, cert bonus = 0.15 (3 certs * 0.05, capped at 0.2)
        assert risk == 0.6  # 0.75 - 0.15
    
    def test_create_assessment(self, sc_agent):
        """Test creating vendor assessment."""
        vendor = sc_agent.add_vendor("Test", "software", "high")
        
        assessment = sc_agent.create_assessment(
            vendor.vendor_id,
            assessment_type="annual",
            assessor="security@example.com",
        )
        
        assert assessment.assessment_id.startswith("assess-")
        assert assessment.status == "planned"
        assert assessment.assessor == "security@example.com"
    
    def test_complete_assessment(self, sc_agent):
        """Test completing vendor assessment."""
        vendor = sc_agent.add_vendor("Test", "software", "high")
        
        assessment = sc_agent.create_assessment(vendor.vendor_id, "annual", "assessor")
        
        result = sc_agent.complete_assessment(
            assessment.assessment_id,
            security_score=85.0,
            privacy_score=90.0,
            compliance_score=95.0,
            findings=[{'category': 'security', 'finding': 'Good'}],
            recommendations=["Maintain practices"],
        )
        
        assert result is True
        assert assessment.status == "completed"
        assert assessment.completed_at is not None
        assert assessment.overall_score == 89.5  # 85*0.4 + 90*0.3 + 95*0.3
    
    def test_get_assessments_by_status(self, sc_agent):
        """Test filtering assessments by status."""
        vendor = sc_agent.add_vendor("Test", "software", "high")
        
        a1 = sc_agent.create_assessment(vendor.vendor_id, "initial", "a1")
        a2 = sc_agent.create_assessment(vendor.vendor_id, "annual", "a2")
        
        sc_agent.complete_assessment(a1.assessment_id, 80, 80, 80)
        
        planned = sc_agent.get_assessments(status="planned")
        completed = sc_agent.get_assessments(status="completed")
        
        assert len(planned) == 1
        assert len(completed) == 1
    
    def test_report_incident(self, sc_agent):
        """Test reporting security incident."""
        pkg = sc_agent.add_package("event-stream", "3.3.6", PackageType.NPM)
        vendor = sc_agent.add_vendor("malicious-actor", "unknown", "critical")
        
        incident = sc_agent.report_incident(
            title="Malicious Package Injection",
            description="event-stream compromised",
            severity="critical",
            affected_packages=[pkg.package_id],
            affected_vendors=[vendor.vendor_id],
        )
        
        assert incident.incident_id.startswith("incident-")
        assert incident.status == "reported"
        assert len(vendor.incidents) == 1
    
    def test_resolve_incident(self, sc_agent):
        """Test resolving incident."""
        incident = sc_agent.report_incident(
            "Test Incident", "Description", "high",
        )
        
        result = sc_agent.resolve_incident(
            incident.incident_id,
            root_cause="Compromised dependency",
            remediation=["Remove package", "Audit dependencies"],
        )
        
        assert result is True
        assert incident.status == "resolved"
        assert incident.resolved_at is not None
        assert incident.root_cause == "Compromised dependency"
    
    def test_get_incidents_by_status(self, sc_agent):
        """Test filtering incidents by status."""
        i1 = sc_agent.report_incident("Incident 1", "Desc", "critical")
        i2 = sc_agent.report_incident("Incident 2", "Desc", "high")
        i3 = sc_agent.report_incident("Incident 3", "Desc", "medium")
        
        sc_agent.resolve_incident(i1.incident_id, "cause", ["fix"])
        
        open_incidents = sc_agent.get_incidents(status="reported")
        resolved = sc_agent.get_incidents(status="resolved")
        
        assert len(open_incidents) == 2
        assert len(resolved) == 1
    
    def test_get_supply_chain_report(self, sc_agent):
        """Test supply chain report generation."""
        # Add packages
        sc_agent.add_package("pkg1", "1.0", PackageType.NPM)
        sc_agent.add_package("pkg2", "1.0", PackageType.PYPI)
        
        # Add vulnerability
        pkg = list(sc_agent.packages.values())[0]
        sc_agent.add_vulnerability("CVE-TEST", pkg.package_id, "*", "fixed", 7.0, "desc")
        
        # Add vendor
        sc_agent.add_vendor("Vendor", "software", "high")
        
        report = sc_agent.get_supply_chain_report()
        
        assert 'packages' in report
        assert 'vulnerabilities' in report
        assert 'vendors' in report
        assert 'incidents' in report
        assert report['packages']['total'] == 2
    
    def test_get_vendor_risk_report(self, sc_agent):
        """Test vendor risk report."""
        vendor = sc_agent.add_vendor("Test Vendor", "software", "high")
        
        assessment = sc_agent.create_assessment(vendor.vendor_id, "annual", "assessor")
        sc_agent.complete_assessment(assessment.assessment_id, 85, 90, 95)
        
        report = sc_agent.get_vendor_risk_report(vendor.vendor_id)
        
        assert 'vendor' in report
        assert 'assessments' in report
        assert report['vendor']['risk_score'] > 0
    
    def test_get_state(self, sc_agent):
        """Test agent state summary."""
        sc_agent.add_package("test", "1.0", PackageType.NPM)
        sc_agent.add_vendor("vendor", "software", "high")
        
        state = sc_agent.get_state()
        
        assert state['packages_count'] == 1
        assert state['vendors_count'] == 1
        assert 'agent_id' in state


class TestSupplyChainCapabilities:
    """Test SupplyChainAgent capabilities export."""
    
    def test_capabilities(self):
        """Test capabilities export."""
        from agentic_ai.agents.supply_chain import get_capabilities
        caps = get_capabilities()
        
        assert caps['agent_type'] == 'supply_chain'
        assert len(caps['capabilities']) >= 20
        assert 'create_sbom' in caps['capabilities']
        assert 'add_vulnerability' in caps['capabilities']
        assert 'calculate_vendor_risk' in caps['capabilities']
    
    def test_package_types(self):
        """Test package types in capabilities."""
        from agentic_ai.agents.supply_chain import get_capabilities
        caps = get_capabilities()
        
        assert 'npm' in caps['package_types']
        assert 'pypi' in caps['package_types']
        assert 'maven' in caps['package_types']
        assert 'docker' in caps['package_types']
    
    def test_sbom_formats(self):
        """Test SBOM formats in capabilities."""
        from agentic_ai.agents.supply_chain import get_capabilities
        caps = get_capabilities()
        
        assert 'spdx' in caps['sbom_formats']
        assert 'cyclonedx' in caps['sbom_formats']
    
    def test_vulnerability_severities(self):
        """Test vulnerability severities in capabilities."""
        from agentic_ai.agents.supply_chain import get_capabilities
        caps = get_capabilities()
        
        assert 'critical' in caps['vulnerability_severities']
        assert 'high' in caps['vulnerability_severities']
        assert 'medium' in caps['vulnerability_severities']
        assert 'low' in caps['vulnerability_severities']


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
