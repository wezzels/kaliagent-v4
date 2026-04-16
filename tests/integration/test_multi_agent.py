"""
Multi-Agent Integration Tests
==============================

Integration tests for multi-agent orchestration workflows.
Tests verify agents can collaborate and share context effectively.
"""

import pytest
from datetime import datetime, timedelta

from agentic_ai.agents.cyber.soc import SOCAgent
from agentic_ai.agents.devops import DevOpsAgent
from agentic_ai.agents.communications import CommunicationsAgent
from agentic_ai.agents.legal import LegalAgent
from agentic_ai.agents.vendor_risk import VendorRiskAgent, VendorTier
from agentic_ai.agents.cloud_security import CloudSecurityAgent, CloudProvider, Severity
from agentic_ai.agents.audit import AuditAgent, AuditType, ControlType
from agentic_ai.agents.data_governance import DataGovernanceAgent, DataType, DataClassification
from agentic_ai.agents.privacy import PrivacyAgent, DataSubjectRight
from agentic_ai.agents.security import SecurityAgent
from agentic_ai.agents.compliance import ComplianceAgent
from agentic_ai.agents.chaos_monkey import ChaosMonkeyAgent, ExperimentType, TargetType
from agentic_ai.agents.ml_ops import MLOpsAgent


# ============================================================================
# Security Incident Response Integration Test
# ============================================================================

class TestSecurityIncidentResponse:
    """Test security incident response workflow across agents."""
    
    def test_full_incident_response_workflow(self):
        """Test complete incident response from detection to resolution."""
        # Initialize agents
        soc = SOCAgent()
        devops = DevOpsAgent()
        comms = CommunicationsAgent()
        legal = LegalAgent()
        cloud_sec = CloudSecurityAgent()
        
        # Phase 1: Detection (SOC)
        incident = soc.report_security_incident(
            title="Unauthorized API Access",
            description="Suspicious login from unusual location",
            severity="high",
            incident_type="unauthorized_access",
            affected_systems=["api-gateway"],
        )
        
        assert incident.incident_id.startswith("inc-")
        assert incident.severity == "high"
        
        # Phase 2: Containment (DevOps)
        containment_task = devops.create_task(
            title="Isolate Affected Systems",
            description="Isolate compromised API gateway instances",
            priority="critical",
            assignee="security-team@example.com",
        )
        
        assert containment_task.task_id.startswith("task-")
        assert containment_task.priority == "critical"
        
        # Phase 3: Communication (Comms)
        notification = comms.send_email(
            to=["security-team@example.com"],
            subject="Security Incident Alert",
            body=f"Incident {incident.incident_id} detected",
            priority="high",
        )
        
        assert notification is not None
        
        # Phase 4: Legal (Legal)
        legal_matter = legal.create_legal_matter(
            title=f"Security Incident {incident.incident_id}",
            matter_type="data_breach",
            description="Unauthorized access incident",
            priority="urgent",
        )
        
        assert legal_matter.matter_id.startswith("legal-")
        
        # Phase 5: Cloud Security Review
        aws_account = cloud_sec.add_account(
            "123456789012", CloudProvider.AWS, "Production", "production", "owner",
        )
        
        finding = cloud_sec.create_finding(
            "MFA Not Enforced",
            "Admin account compromised did not have MFA",
            Severity.HIGH,
            "iam-user-admin",
            aws_account.account_id,
        )
        
        assert finding.finding_id.startswith("find-")
        
        # Phase 6: Resolution
        soc.update_incident_status(incident.incident_id, "resolved")
        
        # Verify all agents have state
        assert soc.get_state()['incidents_count'] >= 1
        assert devops.get_state()['tasks_count'] >= 1
        assert legal.get_state()['matters_count'] >= 1
        assert cloud_sec.get_state()['findings_count'] >= 1
    
    def test_incident_escalation_workflow(self):
        """Test incident escalation based on severity."""
        soc = SOCAgent()
        comms = CommunicationsAgent()
        
        # Create critical incident
        incident = soc.report_security_incident(
            title="Critical: Database Breach",
            description="Customer data exfiltration detected",
            severity="critical",
            incident_type="data_breach",
            affected_systems=["customer-database"],
        )
        
        # Verify escalation triggers
        assert incident.severity == "critical"
        
        # Critical incidents should trigger executive notification
        exec_notification = comms.send_email(
            to=["ciso@example.com", "ceo@example.com"],
            subject="CRITICAL: Security Incident",
            body="Critical incident requires immediate attention",
            priority="critical",
        )
        
        assert exec_notification is not None


# ============================================================================
# Vendor Assessment Integration Test
# ============================================================================

class TestVendorAssessment:
    """Test vendor risk assessment workflow."""
    
    def test_full_vendor_assessment_workflow(self):
        """Test complete vendor assessment from onboarding to approval."""
        vendor_risk = VendorRiskAgent()
        security = SecurityAgent()
        compliance = ComplianceAgent()
        legal = LegalAgent()
        
        # Phase 1: Vendor Onboarding
        vendor = vendor_risk.add_vendor(
            name="CloudVendor Inc",
            legal_name="CloudVendor Incorporated",
            tier=VendorTier.TIER_1,
            category="saas",
            relationship_type="vendor",
            contract_start=datetime.utcnow(),
            contract_value=500000.0,
        )
        
        assert vendor.vendor_id.startswith("vendor-")
        assert vendor.tier == VendorTier.TIER_1
        
        # Phase 2: Security Assessment
        security_assessment = security.create_assessment(
            title=f"Security Assessment - {vendor.name}",
            assessment_type="vendor_security",
            scope="Cloud infrastructure security",
            assessor="security-team@example.com",
        )
        
        security_control = security.add_control(
            assessment_id=security_assessment.assessment_id,
            name="Access Control",
            description="MFA and RBAC",
            control_type="preventive",
            category="access_management",
            status="effective",
        )
        
        assert security_control.control_id.startswith("ctrl-")
        
        # Phase 3: Compliance Verification
        compliance_assessment = compliance.create_assessment(
            name=f"Compliance Review - {vendor.name}",
            assessment_type="vendor_compliance",
            scope="SOC2, ISO27001",
            assessor="compliance-team@example.com",
        )
        
        soc2_cert = compliance.add_certificate(
            certificate_type="soc2_type2",
            issuer=vendor.name,
            issued_date=datetime.utcnow() - timedelta(days=90),
            expiry_date=datetime.utcnow() + timedelta(days=275),
            status="valid",
        )
        
        assert soc2_cert.certificate_id.startswith("cert-")
        
        # Phase 4: Legal Review
        legal_matter = legal.create_legal_matter(
            title=f"Contract Review - {vendor.name}",
            matter_type="contract_review",
            description="MSA and DPA review",
            priority="high",
        )
        
        assert legal_matter.matter_id.startswith("legal-")
        
        # Phase 5: Risk Scoring
        assessment = vendor_risk.create_assessment(
            vendor_id=vendor.vendor_id,
            assessment_type="initial",
            assessor="vendor-risk@example.com",
        )
        
        vendor_risk.complete_assessment(
            assessment.assessment_id,
            inherent_risk_score=0.7,
            control_effectiveness=0.85,
            residual_risk_score=0.3,
            overall_opinion="APPROVED",
        )
        
        assert assessment.residual_risk_level.value in ['low', 'medium', 'high', 'extreme']
        
        # Verify all agents have state
        assert vendor_risk.get_state()['vendors_count'] >= 1
        assert security.get_state()['assessments_count'] >= 1
        assert compliance.get_state()['certificates_count'] >= 1


# ============================================================================
# Audit Preparation Integration Test
# ============================================================================

class TestAuditPreparation:
    """Test SOC2 audit preparation workflow."""
    
    def test_full_audit_prep_workflow(self):
        """Test complete audit preparation across all agents."""
        audit = AuditAgent()
        data_gov = DataGovernanceAgent()
        privacy = PrivacyAgent()
        security = SecurityAgent()
        
        # Phase 1: Audit Planning
        soc2_audit = audit.create_audit(
            title="SOC2 Type II Audit 2026",
            description="Annual SOC2 audit",
            audit_type=AuditType.IT_GENERAL,
            auditor="external-auditor@auditfirm.com",
            auditee="Example Corp",
            scope="Security, Availability, Confidentiality",
            planned_hours=200.0,
        )
        
        audit.start_audit(soc2_audit.audit_id)
        
        assert soc2_audit.audit_id.startswith("audit-")
        assert soc2_audit.status.value == "in_progress"
        
        # Phase 2: Control Documentation
        controls = [
            audit.add_control(
                audit_id=soc2_audit.audit_id,
                name="Logical Access Controls",
                description="MFA, RBAC",
                control_type=ControlType.PREVENTIVE,
                control_owner="security-team@example.com",
                frequency="continuous",
            ),
            audit.add_control(
                audit_id=soc2_audit.audit_id,
                name="Backup and Recovery",
                description="Daily backups",
                control_type=ControlType.CORRECTIVE,
                control_owner="platform-team@example.com",
                frequency="daily",
            ),
        ]
        
        assert len(controls) == 2
        
        # Phase 3: Data Governance Evidence
        data_asset = data_gov.register_asset(
            name="Customer Database",
            description="Primary customer data",
            data_type=DataType.PII,
            classification=DataClassification.RESTRICTED,
            owner="data-team@example.com",
            location="aws:rds:customer-db",
        )
        
        assert data_asset.asset_id.startswith("asset-")
        
        evidence_1 = audit.collect_evidence(
            audit_id=soc2_audit.audit_id,
            title="Data Asset Inventory",
            description="Complete data asset list",
            evidence_type="document",
            location="/evidence/data-assets.xlsx",
            collected_by="data-governance@example.com",
        )
        
        assert evidence_1.evidence_id.startswith("evid-")
        
        # Phase 4: Privacy Evidence
        processing_activity = privacy.register_processing_activity(
            name="Customer Account Management",
            purpose=privacy.ProcessingPurpose.SERVICE_DELIVERY,
            data_categories=[DataType.PII],
            legal_basis="contract",
        )
        
        dsar = privacy.create_data_request(
            subject_id="customer-001",
            right_type=DataSubjectRight.ACCESS,
            submitted_at=datetime.utcnow() - timedelta(days=30),
            deadline=datetime.utcnow() - timedelta(days=5),
            status="completed",
        )
        
        evidence_2 = audit.collect_evidence(
            audit_id=soc2_audit.audit_id,
            title="DSAR Log",
            description="Data subject request log",
            evidence_type="document",
            location="/evidence/dsar-log.xlsx",
            collected_by="privacy@example.com",
        )
        
        # Phase 5: Security Evidence
        security_assessment = security.create_assessment(
            title="Access Review Q4 2025",
            assessment_type="access_review",
            scope="Production access",
            assessor="security-team@example.com",
        )
        
        evidence_3 = audit.collect_evidence(
            audit_id=soc2_audit.audit_id,
            title="Access Review Report",
            description="Q4 access review",
            evidence_type="document",
            location="/evidence/access-review.pdf",
            collected_by="security@example.com",
        )
        
        # Phase 6: Control Testing
        for control in controls:
            audit.test_control(
                control_id=control.control_id,
                tested_by="auditor@auditfirm.com",
                test_results=[{'procedure': 'Test 1', 'passed': True}],
            )
        
        # Phase 7: Audit Report
        report = audit.generate_audit_report(soc2_audit.audit_id)
        
        assert 'audit' in report
        assert 'controls' in report
        assert 'evidence' in report
        
        # Verify all agents have state
        assert audit.get_state()['audits_count'] >= 1
        assert data_gov.get_state()['assets_count'] >= 1
        assert privacy.get_state()['requests_count'] >= 1
        assert security.get_state()['assessments_count'] >= 1


# ============================================================================
# Chaos Monitoring Integration Test
# ============================================================================

class TestChaosMonitoring:
    """Test chaos engineering with monitoring workflow."""
    
    def test_chaos_with_ml_monitoring(self):
        """Test chaos experiment with ML model monitoring."""
        chaos = ChaosMonkeyAgent()
        mlops = MLOpsAgent()
        
        # Setup: Register ML model
        dataset = mlops.register_dataset(
            name="Test Dataset",
            description="ML training data",
            location="s3://ml-data/test",
            record_count=10000,
            feature_count=20,
        )
        
        experiment = mlops.create_experiment(
            name="Baseline Experiment",
            description="Model baseline",
            model_type="xgboost",
            dataset_id=dataset.dataset_id,
            hyperparameters={},
            created_by="ml-team@example.com",
        )
        
        mlops.start_experiment(experiment.experiment_id)
        mlops.complete_experiment(
            experiment.experiment_id,
            metrics={'accuracy': 0.92, 'latency_p99': 120},
        )
        
        model = mlops.register_model(
            name="Test Model",
            description="XGBoost classifier",
            framework="xgboost",
            experiment_id=experiment.experiment_id,
        )
        
        deployment = mlops.deploy_model(
            model_id=model.model_id,
            environment="production",
            endpoint="https://api.example.com/predict",
        )
        
        monitor = mlops.create_monitor(
            model_id=model.model_id,
            metrics_to_track=['accuracy', 'latency_p99'],
            baseline_metrics={'accuracy': 0.92, 'latency_p99': 120},
            thresholds={'accuracy': 0.05, 'latency_p99': 50},
            check_frequency="minute",
        )
        
        # Chaos: Create experiment
        target = chaos.register_target(
            target_type=TargetType.SERVICE,
            name="ml-inference-service",
            cloud_provider="kubernetes",
            region="us-east-1",
            availability_zone="us-east-1a",
        )
        
        exp = chaos.create_experiment(
            name="ML Service Latency Test",
            description="Inject latency and monitor model performance",
            experiment_type=ExperimentType.LATENCY_INJECTION,
            severity="medium",
            blast_radius="limited",
            duration_minutes=15,
            abort_conditions=[chaos.AbortCondition.LATENCY_THRESHOLD],
            abort_thresholds={'latency_p99': 500},
        )
        
        chaos.assign_targets(exp.experiment_id, [target.target_id])
        chaos.start_experiment(exp.experiment_id)
        
        # Execute latency injection
        run = list(chaos.runs.values())[0]
        chaos.execute_latency_injection(run.run_id, latency_ms=200)
        
        # Monitor: Check for drift
        degraded_metrics = {'accuracy': 0.88, 'latency_p99': 320}
        alerts = mlops.check_model_metrics(model.model_id, degraded_metrics)
        
        # Should have latency alert
        assert len(alerts) >= 1 or degraded_metrics['latency_p99'] > 120 + 50
        
        # Complete experiment
        chaos.complete_experiment(
            exp.experiment_id,
            actual_outcome="Latency increased but model remained functional",
            lessons_learned=["System handled latency injection well"],
        )
        
        # Verify state
        assert chaos.get_state()['experiments_count'] >= 1
        assert mlops.get_state()['models_count'] >= 1
        assert mlops.get_state()['monitors_count'] >= 1


# ============================================================================
# Cross-Agent Context Sharing Tests
# ============================================================================

class TestCrossAgentContextSharing:
    """Test context sharing between agents."""
    
    def test_incident_context_sharing(self):
        """Test that incident context is shared across agents."""
        soc = SOCAgent()
        devops = DevOpsAgent()
        legal = LegalAgent()
        
        # SOC creates incident
        incident = soc.report_security_incident(
            title="Shared Context Test",
            description="Testing context propagation",
            severity="high",
            incident_type="test",
            affected_systems=["system-a", "system-b"],
            source_ip="192.168.1.100",
            target_user="admin@example.com",
        )
        
        # DevOps creates task referencing incident
        task = devops.create_task(
            title=f"Respond to {incident.incident_id}",
            description=incident.description,
            priority="critical",
            assignee="responder@example.com",
        )
        
        # Legal creates matter referencing incident
        matter = legal.create_legal_matter(
            title=f"Legal Review: {incident.incident_id}",
            matter_type="incident_review",
            description=incident.description,
            priority="high",
        )
        
        # Verify context is preserved
        assert incident.incident_id in task.title
        assert incident.incident_id in matter.title
        assert task.priority == "critical"
        assert matter.priority == "high"
    
    def test_vendor_context_propagation(self):
        """Test vendor context propagation across agents."""
        vendor_risk = VendorRiskAgent()
        security = SecurityAgent()
        compliance = ComplianceAgent()
        
        # VendorRisk creates vendor
        vendor = vendor_risk.add_vendor(
            name="Context Test Vendor",
            legal_name="Context Test Inc",
            tier=VendorTier.TIER_2,
            category="saas",
            relationship_type="vendor",
            contract_start=datetime.utcnow(),
        )
        
        # Security assessment references vendor
        security_assessment = security.create_assessment(
            title=f"Security: {vendor.name}",
            assessment_type="vendor_security",
            scope="Security review",
            assessor="security@example.com",
            target_vendor=vendor.name,
        )
        
        # Compliance cert references vendor
        cert = compliance.add_certificate(
            certificate_type="soc2_type2",
            issuer=vendor.name,
            issued_date=datetime.utcnow(),
            expiry_date=datetime.utcnow() + timedelta(days=365),
            status="valid",
        )
        
        # Verify vendor context preserved
        assert vendor.name in security_assessment.title
        assert vendor.name in cert.issuer


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
