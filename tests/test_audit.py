"""
AuditAgent Tests
================

Unit tests for AuditAgent - Internal audit & control testing.
"""

import pytest
from datetime import datetime, timedelta

from agentic_ai.agents.audit import (
    AuditAgent,
    AuditType,
    AuditStatus,
    ControlType,
    ControlStatus,
    FindingSeverity,
    FindingStatus,
)


class TestAuditAgent:
    """Test AuditAgent."""
    
    @pytest.fixture
    def audit_agent(self):
        """Create AuditAgent instance."""
        return AuditAgent()
    
    def test_create_audit(self, audit_agent):
        """Test creating audit."""
        audit = audit_agent.create_audit(
            title="ITGC Audit 2026",
            description="Annual IT general controls audit",
            audit_type=AuditType.IT_GENERAL,
            auditor="auditor@example.com",
            auditee="IT Department",
            scope="Access control, change management",
            objectives=["Assess controls", "Test effectiveness"],
            planned_hours=100.0,
        )
        
        assert audit.audit_id.startswith("audit-")
        assert audit.status == AuditStatus.PLANNED
        assert audit.planned_hours == 100.0
    
    def test_start_audit(self, audit_agent):
        """Test starting audit."""
        audit = audit_agent.create_audit(
            "Test Audit", "Desc", AuditType.INTERNAL,
            "auditor", "auditee", "scope",
        )
        
        result = audit_agent.start_audit(audit.audit_id)
        
        assert result is True
        assert audit.status == AuditStatus.IN_PROGRESS
        assert audit.start_date is not None
    
    def test_complete_audit(self, audit_agent):
        """Test completing audit."""
        audit = audit_agent.create_audit(
            "Test", "Desc", AuditType.INTERNAL,
            "auditor", "auditee", "scope",
        )
        audit_agent.start_audit(audit.audit_id)
        
        result = audit_agent.complete_audit(audit.audit_id, actual_hours=95.0)
        
        assert result is True
        assert audit.status == AuditStatus.COMPLETE
        assert audit.end_date is not None
        assert audit.actual_hours == 95.0
    
    def test_get_audits_by_type(self, audit_agent):
        """Test filtering audits by type."""
        audit_agent.create_audit("ITGC", "Desc", AuditType.IT_GENERAL, "a", "au", "scope")
        audit_agent.create_audit("Financial", "Desc", AuditType.FINANCIAL, "a", "au", "scope")
        audit_agent.create_audit("Compliance", "Desc", AuditType.COMPLIANCE, "a", "au", "scope")
        
        itgc = audit_agent.get_audits(audit_type=AuditType.IT_GENERAL)
        financial = audit_agent.get_audits(audit_type=AuditType.FINANCIAL)
        
        assert len(itgc) == 1
        assert len(financial) == 1
    
    def test_add_control(self, audit_agent):
        """Test adding control."""
        audit = audit_agent.create_audit(
            "Test", "Desc", AuditType.IT_GENERAL,
            "auditor", "auditee", "scope",
        )
        
        control = audit_agent.add_control(
            audit.audit_id,
            name="User Access Review",
            description="Quarterly access reviews",
            control_type=ControlType.PREVENTIVE,
            control_owner="it-manager@example.com",
            frequency="quarterly",
            test_procedures=[
                "Select sample of 25 users",
                "Verify access rights",
            ],
        )
        
        assert control.control_id.startswith("ctrl-")
        assert control.control_type == ControlType.PREVENTIVE
        assert len(control.test_procedures) == 2
    
    def test_test_control_effective(self, audit_agent):
        """Test control testing - effective."""
        audit = audit_agent.create_audit("Test", "Desc", AuditType.IT_GENERAL, "a", "au", "scope")
        control = audit_agent.add_control(
            audit.audit_id, "Test Control", "Desc",
            ControlType.PREVENTIVE, "owner", "monthly",
        )
        
        result = audit_agent.test_control(
            control.control_id,
            tested_by="auditor@example.com",
            test_results=[
                {'procedure': 'Test 1', 'passed': True},
                {'procedure': 'Test 2', 'passed': True},
                {'procedure': 'Test 3', 'passed': True},
            ],
        )
        
        assert result is True
        assert control.status == ControlStatus.EFFECTIVE
        assert control.tested_by == "auditor@example.com"
    
    def test_test_control_ineffective(self, audit_agent):
        """Test control testing - ineffective."""
        audit = audit_agent.create_audit("Test", "Desc", AuditType.IT_GENERAL, "a", "au", "scope")
        control = audit_agent.add_control(
            audit.audit_id, "Test Control", "Desc",
            ControlType.PREVENTIVE, "owner", "monthly",
        )
        
        audit_agent.test_control(
            control.control_id,
            tested_by="auditor",
            test_results=[
                {'procedure': 'Test 1', 'passed': False},
                {'procedure': 'Test 2', 'passed': False},
            ],
        )
        
        assert control.status == ControlStatus.INEFFECTIVE
    
    def test_test_control_partially_effective(self, audit_agent):
        """Test control testing - partially effective."""
        audit = audit_agent.create_audit("Test", "Desc", AuditType.IT_GENERAL, "a", "au", "scope")
        control = audit_agent.add_control(
            audit.audit_id, "Test Control", "Desc",
            ControlType.PREVENTIVE, "owner", "monthly",
        )
        
        audit_agent.test_control(
            control.control_id,
            tested_by="auditor",
            test_results=[
                {'procedure': 'Test 1', 'passed': True},
                {'procedure': 'Test 2', 'passed': False},
                {'procedure': 'Test 3', 'passed': True},
            ],
        )
        
        assert control.status == ControlStatus.PARTIALLY_EFFECTIVE
    
    def test_get_controls_by_status(self, audit_agent):
        """Test filtering controls by status."""
        audit = audit_agent.create_audit("Test", "Desc", AuditType.IT_GENERAL, "a", "au", "scope")
        
        c1 = audit_agent.add_control(audit.audit_id, "C1", "Desc", ControlType.PREVENTIVE, "o", "m")
        c2 = audit_agent.add_control(audit.audit_id, "C2", "Desc", ControlType.DETECTIVE, "o", "m")
        
        audit_agent.test_control(c1.control_id, "auditor", [{'passed': True}])
        audit_agent.test_control(c2.control_id, "auditor", [{'passed': False}])
        
        effective = audit_agent.get_controls(status=ControlStatus.EFFECTIVE)
        ineffective = audit_agent.get_controls(status=ControlStatus.INEFFECTIVE)
        
        assert len(effective) == 1
        assert len(ineffective) == 1
    
    def test_create_finding(self, audit_agent):
        """Test creating audit finding."""
        audit = audit_agent.create_audit("Test", "Desc", AuditType.IT_GENERAL, "a", "au", "scope")
        control = audit_agent.add_control(audit.audit_id, "Ctrl", "Desc", ControlType.PREVENTIVE, "o", "m")
        
        finding = audit_agent.create_finding(
            audit.audit_id,
            title="Access Control Weakness",
            description="Users have excessive privileges",
            severity=FindingSeverity.HIGH,
            condition="10 users have admin access without justification",
            criteria="Principle of least privilege should be enforced",
            control_id=control.control_id,
            cause="No access review process",
            effect="Increased risk of unauthorized access",
        )
        
        assert finding.finding_id.startswith("find-")
        assert finding.severity == FindingSeverity.HIGH
        assert finding.status == FindingStatus.OPEN
        assert audit.findings_count == 1
    
    def test_update_finding(self, audit_agent):
        """Test updating finding details."""
        audit = audit_agent.create_audit("Test", "Desc", AuditType.IT_GENERAL, "a", "au", "scope")
        finding = audit_agent.create_finding(
            audit.audit_id, "Title", "Desc",
            FindingSeverity.MEDIUM, "condition", "criteria",
        )
        
        due_date = datetime.utcnow() + timedelta(days=60)
        
        result = audit_agent.update_finding(
            finding.finding_id,
            recommendation="Implement access reviews",
            management_response="Will implement in Q2",
            action_plan="Deploy automated review system",
            responsible_party="it-director@example.com",
            due_date=due_date,
        )
        
        assert result is True
        assert finding.recommendation == "Implement access reviews"
        assert finding.responsible_party == "it-director@example.com"
        assert finding.due_date == due_date
    
    def test_update_finding_status(self, audit_agent):
        """Test updating finding status."""
        audit = audit_agent.create_audit("Test", "Desc", AuditType.IT_GENERAL, "a", "au", "scope")
        finding = audit_agent.create_finding(
            audit.audit_id, "Title", "Desc",
            FindingSeverity.MEDIUM, "condition", "criteria",
        )
        
        # Move to in progress
        audit_agent.update_finding_status(finding.finding_id, FindingStatus.IN_PROGRESS)
        assert finding.status == FindingStatus.IN_PROGRESS
        
        # Close finding
        audit_agent.update_finding_status(finding.finding_id, FindingStatus.CLOSED)
        assert finding.status == FindingStatus.CLOSED
        assert finding.closed_at is not None
    
    def test_get_findings_by_severity(self, audit_agent):
        """Test filtering findings by severity."""
        audit = audit_agent.create_audit("Test", "Desc", AuditType.IT_GENERAL, "a", "au", "scope")
        
        audit_agent.create_finding(audit.audit_id, "Critical", "Desc", FindingSeverity.CRITICAL, "c", "cr")
        audit_agent.create_finding(audit.audit_id, "High", "Desc", FindingSeverity.HIGH, "c", "cr")
        audit_agent.create_finding(audit.audit_id, "Medium", "Desc", FindingSeverity.MEDIUM, "c", "cr")
        audit_agent.create_finding(audit.audit_id, "Low", "Desc", FindingSeverity.LOW, "c", "cr")
        
        high = audit_agent.get_findings(severity=FindingSeverity.HIGH)
        critical = audit_agent.get_findings(severity=FindingSeverity.CRITICAL)
        
        assert len(high) == 1
        assert len(critical) == 1
    
    def test_collect_evidence(self, audit_agent):
        """Test collecting evidence."""
        audit = audit_agent.create_audit("Test", "Desc", AuditType.IT_GENERAL, "a", "au", "scope")
        control = audit_agent.add_control(audit.audit_id, "Ctrl", "Desc", ControlType.PREVENTIVE, "o", "m")
        
        evidence = audit_agent.collect_evidence(
            audit.audit_id,
            title="Access Review Report",
            description="Q4 2025 access review documentation",
            evidence_type="document",
            location="/evidence/access-review-q4.pdf",
            collected_by="auditor@example.com",
            control_id=control.control_id,
        )
        
        assert evidence.evidence_id.startswith("evid-")
        assert evidence.evidence_type == "document"
        assert evidence.reviewed is False
    
    def test_review_evidence(self, audit_agent):
        """Test reviewing evidence."""
        audit = audit_agent.create_audit("Test", "Desc", AuditType.IT_GENERAL, "a", "au", "scope")
        
        evidence = audit_agent.collect_evidence(
            audit.audit_id, "Evidence", "Desc",
            "document", "/path", "collector",
        )
        
        result = audit_agent.review_evidence(evidence.evidence_id, "reviewer@example.com")
        
        assert result is True
        assert evidence.reviewed is True
        assert evidence.reviewed_by == "reviewer@example.com"
    
    def test_get_evidence_by_type(self, audit_agent):
        """Test filtering evidence by type."""
        audit = audit_agent.create_audit("Test", "Desc", AuditType.IT_GENERAL, "a", "au", "scope")
        
        audit_agent.collect_evidence(audit.audit_id, "Doc", "Desc", "document", "/doc", "c")
        audit_agent.collect_evidence(audit.audit_id, "Screenshot", "Desc", "screenshot", "/img", "c")
        audit_agent.collect_evidence(audit.audit_id, "Log", "Desc", "log", "/log", "c")
        
        docs = audit_agent.get_evidence(evidence_type="document")
        screenshots = audit_agent.get_evidence(evidence_type="screenshot")
        
        assert len(docs) == 1
        assert len(screenshots) == 1
    
    def test_create_workpaper(self, audit_agent):
        """Test creating workpaper."""
        audit = audit_agent.create_audit("Test", "Desc", AuditType.IT_GENERAL, "a", "au", "scope")
        
        workpaper = audit_agent.create_workpaper(
            audit.audit_id,
            title="Access Control Testing",
            section="Fieldwork",
            content="Detailed testing procedures and results...",
            created_by="auditor@example.com",
        )
        
        assert workpaper.workpaper_id.startswith("wp-")
        assert workpaper.content.startswith("Detailed")
        assert workpaper.reviewed is False
    
    def test_review_workpaper(self, audit_agent):
        """Test reviewing workpaper."""
        audit = audit_agent.create_audit("Test", "Desc", AuditType.IT_GENERAL, "a", "au", "scope")
        workpaper = audit_agent.create_workpaper(
            audit.audit_id, "WP", "section", "content", "creator",
        )
        
        result = audit_agent.review_workpaper(workpaper.workpaper_id, "reviewer@example.com")
        
        assert result is True
        assert workpaper.reviewed is True
        assert workpaper.reviewer == "reviewer@example.com"
    
    def test_generate_audit_report(self, audit_agent):
        """Test audit report generation."""
        audit = audit_agent.create_audit(
            "ITGC Audit", "Desc", AuditType.IT_GENERAL,
            "auditor", "auditee", "scope",
        )
        audit_agent.start_audit(audit.audit_id)
        
        # Add controls
        c1 = audit_agent.add_control(audit.audit_id, "Effective Ctrl", "Desc", ControlType.PREVENTIVE, "o", "m")
        c2 = audit_agent.add_control(audit.audit_id, "Ineffective Ctrl", "Desc", ControlType.DETECTIVE, "o", "m")
        
        audit_agent.test_control(c1.control_id, "auditor", [{'passed': True}])
        audit_agent.test_control(c2.control_id, "auditor", [{'passed': False}])
        
        # Add finding
        audit_agent.create_finding(
            audit.audit_id, "Finding", "Desc",
            FindingSeverity.HIGH, "condition", "criteria",
        )
        
        report = audit_agent.generate_audit_report(audit.audit_id)
        
        assert 'audit' in report
        assert 'controls' in report
        assert 'findings' in report
        assert 'evidence' in report
        assert report['controls']['total'] == 2
        assert report['controls']['effective'] == 1
        assert report['findings']['total'] == 1
    
    def test_get_audit_dashboard(self, audit_agent):
        """Test audit dashboard."""
        # Create multiple audits
        audit_agent.create_audit("Audit 1", "Desc", AuditType.IT_GENERAL, "a", "au", "scope")
        audit2 = audit_agent.create_audit("Audit 2", "Desc", AuditType.FINANCIAL, "a", "au", "scope")
        
        audit_agent.start_audit(audit2.audit_id)
        
        # Create findings
        audit_agent.create_finding(audit2.audit_id, "Finding", "Desc", FindingSeverity.HIGH, "c", "cr")
        
        dashboard = audit_agent.get_audit_dashboard()
        
        assert 'audits' in dashboard
        assert 'findings' in dashboard
        assert 'controls' in dashboard
        assert dashboard['audits']['total'] == 2
        assert dashboard['audits']['in_progress'] == 1
    
    def test_audit_templates(self, audit_agent):
        """Test audit templates."""
        templates = audit_agent.templates
        
        assert 'it_general' in templates
        assert 'access_review' in templates
        assert 'change_management' in templates
        assert templates['it_general']['name'] == 'IT General Controls'
    
    def test_get_state(self, audit_agent):
        """Test agent state summary."""
        audit = audit_agent.create_audit("Test", "Desc", AuditType.IT_GENERAL, "a", "au", "scope")
        audit_agent.start_audit(audit.audit_id)
        audit_agent.add_control(audit.audit_id, "Ctrl", "Desc", ControlType.PREVENTIVE, "o", "m")
        
        state = audit_agent.get_state()
        
        assert state['audits_count'] == 1
        assert state['in_progress_audits'] == 1
        assert 'agent_id' in state


class TestAuditCapabilities:
    """Test AuditAgent capabilities export."""
    
    def test_capabilities(self):
        """Test capabilities export."""
        from agentic_ai.agents.audit import get_capabilities
        caps = get_capabilities()
        
        assert caps['agent_type'] == 'audit'
        assert len(caps['capabilities']) >= 19
        assert 'create_audit' in caps['capabilities']
        assert 'test_control' in caps['capabilities']
        assert 'generate_audit_report' in caps['capabilities']
    
    def test_audit_types(self):
        """Test audit types in capabilities."""
        from agentic_ai.agents.audit import get_capabilities
        caps = get_capabilities()
        
        assert 'internal' in caps['audit_types']
        assert 'external' in caps['audit_types']
        assert 'it_general' in caps['audit_types']
        assert 'compliance' in caps['audit_types']
    
    def test_control_types(self):
        """Test control types in capabilities."""
        from agentic_ai.agents.audit import get_capabilities
        caps = get_capabilities()
        
        assert 'preventive' in caps['control_types']
        assert 'detective' in caps['control_types']
        assert 'corrective' in caps['control_types']
    
    def test_finding_severities(self):
        """Test finding severities in capabilities."""
        from agentic_ai.agents.audit import get_capabilities
        caps = get_capabilities()
        
        assert 'critical' in caps['finding_severities']
        assert 'high' in caps['finding_severities']
        assert 'medium' in caps['finding_severities']
        assert 'low' in caps['finding_severities']
        assert 'observation' in caps['finding_severities']


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
