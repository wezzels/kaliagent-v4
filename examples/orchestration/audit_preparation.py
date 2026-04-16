"""
Audit Preparation - Multi-Agent Orchestration Example
======================================================

Demonstrates automated audit preparation across multiple agents:
- AuditAgent: Plans audit, manages controls, evidence collection
- DataGovernanceAgent: Provides data lineage, classification, retention
- PrivacyAgent: Reviews data handling, DSARs, consent records
- SecurityAgent: Provides security controls, access reviews, incident history
- ComplianceAgent: Regulatory mappings, policy documentation
- LegalAgent: Contract reviews, legal holds, regulatory correspondence

This example shows SOC2 Type II audit preparation workflow.
"""

import sys
from datetime import datetime, timedelta
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from agentic_ai.agents.audit import AuditAgent, AuditType, ControlType, FindingSeverity
from agentic_ai.agents.data_governance import DataGovernanceAgent, DataType, DataClassification
from agentic_ai.agents.privacy import PrivacyAgent, DataSubjectRight, ProcessingPurpose
from agentic_ai.agents.security import SecurityAgent
from agentic_ai.agents.compliance import ComplianceAgent
from agentic_ai.agents.legal import LegalAgent


def run_audit_preparation():
    """Execute comprehensive audit preparation workflow."""
    
    print("=" * 80)
    print("AUDIT PREPARATION - Multi-Agent Orchestration")
    print("=" * 80)
    print()
    
    # Initialize all agents
    audit = AuditAgent()
    data_gov = DataGovernanceAgent()
    privacy = PrivacyAgent()
    security = SecurityAgent()
    compliance = ComplianceAgent()
    legal = LegalAgent()
    
    # Define audit period
    audit_period_start = datetime.utcnow() - timedelta(days=365)
    audit_period_end = datetime.utcnow()
    
    # ========================================================================
    # PHASE 1: AUDIT PLANNING
    # ========================================================================
    print("\n📋 PHASE 1: AUDIT PLANNING")
    print("-" * 80)
    
    # AuditAgent creates audit engagement
    print("\n[Audit Agent] Creating SOC2 Type II audit engagement...")
    
    soc2_audit = audit.create_audit(
        title="SOC2 Type II Audit 2026",
        description="Annual SOC2 Type II audit covering Security, Availability, and Confidentiality",
        audit_type=AuditType.IT_GENERAL,
        auditor="external-auditor@auditfirm.com",
        auditee="Example Corp",
        scope="Cloud-based data analytics platform - Security, Availability, Confidentiality trust principles",
        objectives=[
            "Evaluate design and operating effectiveness of security controls",
            "Assess availability commitments and performance",
            "Review confidentiality safeguards for customer data",
            "Test incident response and business continuity capabilities",
        ],
        planned_hours=200.0,
    )
    print(f"  ✓ Audit created: {soc2_audit.audit_id}")
    print(f"  ✓ Type: {soc2_audit.audit_type.value}")
    print(f"  ✓ Auditor: {soc2_audit.auditor}")
    print(f"  ✓ Planned hours: {soc2_audit.planned_hours}")
    
    # Start audit
    audit.start_audit(soc2_audit.audit_id)
    print(f"  ✓ Audit started: {soc2_audit.start_date}")
    
    # ========================================================================
    # PHASE 2: CONTROL DOCUMENTATION
    # ========================================================================
    print("\n\n🎛️ PHASE 2: CONTROL DOCUMENTATION")
    print("-" * 80)
    
    # AuditAgent documents controls for each trust principle
    print("\n[Audit Agent] Documenting controls by trust principle...")
    
    # Security Principle Controls
    print("\n  [Security Principle]")
    
    security_controls = [
        audit.add_control(
            audit_id=soc2_audit.audit_id,
            name="Logical Access Controls",
            description="MFA required for all users, RBAC implemented, least privilege enforced",
            control_type=ControlType.PREVENTIVE,
            control_owner="security-team@example.com",
            frequency="continuous",
            test_procedures=[
                "Select sample of 25 users",
                "Verify MFA enabled for all",
                "Review role assignments match job functions",
                "Check for segregation of duties conflicts",
            ],
        ),
        audit.add_control(
            audit_id=soc2_audit.audit_id,
            name="Security Incident Management",
            description="24/7 SOC monitoring, defined incident response procedures",
            control_type=ControlType.DETECTIVE,
            control_owner="soc-team@example.com",
            frequency="continuous",
            test_procedures=[
                "Review incident response procedure documentation",
                "Select sample of 5 incidents from audit period",
                "Verify incidents were detected, responded to, and resolved per procedure",
                "Interview SOC analysts on incident handling",
            ],
        ),
        audit.add_control(
            audit_id=soc2_audit.audit_id,
            name="Change Management",
            description="All changes require approval, testing, and rollback plan",
            control_type=ControlType.PREVENTIVE,
            control_owner="engineering-team@example.com",
            frequency="continuous",
            test_procedures=[
                "Select sample of 30 changes from audit period",
                "Verify approval before implementation",
                "Review testing evidence for each change",
                "Check emergency change process adherence",
            ],
        ),
    ]
    print(f"    ✓ {len(security_controls)} security controls documented")
    
    # Availability Principle Controls
    print("\n  [Availability Principle]")
    
    availability_controls = [
        audit.add_control(
            audit_id=soc2_audit.audit_id,
            name="Infrastructure Monitoring",
            description="24/7 monitoring of all critical systems, alerting on thresholds",
            control_type=ControlType.DETECTIVE,
            control_owner="platform-team@example.com",
            frequency="continuous",
            test_procedures=[
                "Review monitoring dashboard configurations",
                "Verify alerting thresholds are defined",
                "Test alert delivery mechanisms",
                "Review incident response to monitoring alerts",
            ],
        ),
        audit.add_control(
            audit_id=soc2_audit.audit_id,
            name="Backup and Recovery",
            description="Daily backups, quarterly recovery testing, RPO < 1hr, RTO < 4hr",
            control_type=ControlType.CORRECTIVE,
            control_owner="platform-team@example.com",
            frequency="daily",
            test_procedures=[
                "Review backup configuration and schedules",
                "Select sample of 10 backup logs",
                "Verify successful completion",
                "Review quarterly recovery test results",
            ],
        ),
        audit.add_control(
            audit_id=soc2_audit.audit_id,
            name="Disaster Recovery",
            description="Documented DR plan, annual DR testing, multi-region failover",
            control_type=ControlType.CORRECTIVE,
            control_owner="platform-team@example.com",
            frequency="annually",
            test_procedures=[
                "Review DR plan documentation",
                "Verify annual DR test was conducted",
                "Review test results and lessons learned",
                "Confirm multi-region failover capability",
            ],
        ),
    ]
    print(f"    ✓ {len(availability_controls)} availability controls documented")
    
    # Confidentiality Principle Controls
    print("\n  [Confidentiality Principle]")
    
    confidentiality_controls = [
        audit.add_control(
            audit_id=soc2_audit.audit_id,
            name="Data Encryption",
            description="AES-256 encryption at rest, TLS 1.3 in transit",
            control_type=ControlType.PREVENTIVE,
            control_owner="security-team@example.com",
            frequency="continuous",
            test_procedures=[
                "Review encryption configuration for databases",
                "Verify TLS configuration for all endpoints",
                "Test encryption key management procedures",
                "Review certificate management process",
            ],
        ),
        audit.add_control(
            audit_id=soc2_audit.audit_id,
            name="Data Classification",
            description="All data classified, handling procedures based on classification",
            control_type=ControlType.PREVENTIVE,
            control_owner="data-governance-team@example.com",
            frequency="continuous",
            test_procedures=[
                "Review data classification policy",
                "Select sample of 20 data assets",
                "Verify classification is assigned",
                "Check handling procedures match classification",
            ],
        ),
    ]
    print(f"    ✓ {len(confidentiality_controls)} confidentiality controls documented")
    
    # ========================================================================
    # PHASE 3: DATA GOVERNANCE EVIDENCE
    # ========================================================================
    print("\n\n📊 PHASE 3: DATA GOVERNANCE EVIDENCE")
    print("-" * 80)
    
    # DataGovernanceAgent provides data lineage and classification
    print("\n[DataGovernance Agent] Preparing data governance evidence...")
    
    # Register data assets
    print("\n  [Registering Data Assets]")
    
    data_assets = [
        data_gov.register_asset(
            name="Customer Database",
            description="Primary customer data storage",
            data_type=DataType.PII,
            classification=DataClassification.RESTRICTED,
            owner="data-team@example.com",
            steward="data-steward@example.com",
            location="aws:rds:us-east-1:customer-db",
            system="PostgreSQL 15",
        ),
        data_gov.register_asset(
            name="Analytics Data Lake",
            description="Customer behavior analytics data",
            data_type=DataType.ANALYTICS,
            classification=DataClassification.INTERNAL,
            owner="analytics-team@example.com",
            steward="data-steward@example.com",
            location="aws:s3:us-east-1:analytics-lake",
            system="AWS S3 + Athena",
        ),
        data_gov.register_asset(
            name="Payment Processing",
            description="Credit card and payment data",
            data_type=DataType.PCI,
            classification=DataClassification.RESTRICTED,
            owner="payments-team@example.com",
            steward="security-team@example.com",
            location="aws:rds:us-east-1:payments-db",
            system="PostgreSQL 15 (PCI scope)",
        ),
    ]
    print(f"    ✓ {len(data_assets)} data assets registered")
    
    # Create data lineage
    print("\n  [Documenting Data Lineage]")
    
    lineage = data_gov.create_lineage(
        source_system="Customer Database",
        target_system="Analytics Data Lake",
        transformation="ETL - Daily aggregation",
        frequency="daily",
        owner="data-engineering@example.com",
    )
    print(f"    ✓ Data lineage documented: {lineage.lineage_id}")
    
    # Document retention policies
    print("\n  [Retention Policies]")
    
    retention_policies = [
        data_gov.add_retention_policy(
            name="Customer Data Retention",
            data_types=[DataType.PII],
            retention_period=2555,  # 7 years
            retention_unit="days",
            action=data_gov.RetentionAction.ARCHIVE,
            regulatory_requirement="IRS, Contract obligations",
        ),
        data_gov.add_retention_policy(
            name="Payment Data Retention",
            data_types=[DataType.PCI],
            retention_period=365,  # 1 year
            retention_unit="days",
            action=data_gov.RetentionAction.DELETE,
            regulatory_requirement="PCI-DSS requirement",
        ),
        data_gov.add_retention_policy(
            name="Log Data Retention",
            data_types=[DataType.LOGS],
            retention_period=90,  # 90 days
            retention_unit="days",
            action=data_gov.RetentionAction.DELETE,
            regulatory_requirement="Security monitoring",
        ),
    ]
    print(f"    ✓ {len(retention_policies)} retention policies documented")
    
    # Collect evidence for audit
    print("\n  [Collecting Evidence]")
    
    data_evidence = [
        audit.collect_evidence(
            audit_id=soc2_audit.audit_id,
            title="Data Asset Inventory",
            description="Complete inventory of all data assets with classification",
            evidence_type="document",
            location="/evidence/data-asset-inventory-2026.xlsx",
            collected_by="data-governance@example.com",
        ),
        audit.collect_evidence(
            audit_id=soc2_audit.audit_id,
            title="Data Lineage Diagrams",
            description="Data flow diagrams for all critical data paths",
            evidence_type="document",
            location="/evidence/data-lineage-2026.pdf",
            collected_by="data-governance@example.com",
        ),
        audit.collect_evidence(
            audit_id=soc2_audit.audit_id,
            title="Retention Policy Documentation",
            description="Approved retention policies with regulatory mappings",
            evidence_type="document",
            location="/evidence/retention-policies-2026.pdf",
            collected_by="data-governance@example.com",
        ),
    ]
    print(f"    ✓ {len(data_evidence)} data governance evidence collected")
    
    # ========================================================================
    # PHASE 4: PRIVACY COMPLIANCE EVIDENCE
    # ========================================================================
    print("\n\n🔐 PHASE 4: PRIVACY COMPLIANCE EVIDENCE")
    print("-" * 80)
    
    # PrivacyAgent provides privacy-related evidence
    print("\n[Privacy Agent] Preparing privacy compliance evidence...")
    
    # Register data processing activities
    print("\n  [Processing Activities]")
    
    processing_activities = [
        privacy.register_processing_activity(
            name="Customer Account Management",
            purpose=ProcessingPurpose.SERVICE_DELIVERY,
            data_categories=[DataType.PII],
            legal_basis="contract",
            retention_days=2555,
            data_recipients=["internal:customer-support", "internal:billing"],
        ),
        privacy.register_processing_activity(
            name="Analytics and Personalization",
            purpose=ProcessingPurpose.ANALYTICS,
            data_categories=[DataType.ANALYTICS],
            legal_basis="legitimate_interest",
            retention_days=730,
            data_recipients=["internal:analytics-team"],
        ),
    ]
    print(f"    ✓ {len(processing_activities)} processing activities registered")
    
    # Document DSARs (Data Subject Access Requests)
    print("\n  [Data Subject Requests]")
    
    dsar_requests = [
        privacy.create_data_request(
            subject_id="customer-001",
            right_type=DataSubjectRight.ACCESS,
            submitted_at=datetime.utcnow() - timedelta(days=30),
            deadline=datetime.utcnow() - timedelta(days=5),
            status="completed",
        ),
        privacy.create_data_request(
            subject_id="customer-042",
            right_type=DataSubjectRight.DELETION,
            submitted_at=datetime.utcnow() - timedelta(days=20),
            deadline=datetime.utcnow() + timedelta(days=10),
            status="in_progress",
        ),
        privacy.create_data_request(
            subject_id="customer-108",
            right_type=DataSubjectRight.PORTABILITY,
            submitted_at=datetime.utcnow() - timedelta(days=15),
            deadline=datetime.utcnow() + timedelta(days=15),
            status="in_progress",
        ),
    ]
    print(f"    ✓ {len(dsar_requests)} DSARs documented (audit period)")
    
    # Document consent records
    print("\n  [Consent Records]")
    
    consent_records = [
        privacy.record_consent(
            subject_id="customer-001",
            consent_type="marketing",
            granted=True,
            method="web_form",
        ),
        privacy.record_consent(
            subject_id="customer-002",
            consent_type="marketing",
            granted=False,
            method="web_form",
        ),
    ]
    print(f"    ✓ {len(consent_records)} consent records sampled")
    
    # Collect privacy evidence
    print("\n  [Collecting Evidence]")
    
    privacy_evidence = [
        audit.collect_evidence(
            audit_id=soc2_audit.audit_id,
            title="Privacy Impact Assessments",
            description="PIAs for all high-risk processing activities",
            evidence_type="document",
            location="/evidence/pias-2026.pdf",
            collected_by="privacy-team@example.com",
        ),
        audit.collect_evidence(
            audit_id=soc2_audit.audit_id,
            title="DSAR Log and Responses",
            description="Complete log of all DSARs with response evidence",
            evidence_type="document",
            location="/evidence/dsar-log-2026.xlsx",
            collected_by="privacy-team@example.com",
        ),
        audit.collect_evidence(
            audit_id=soc2_audit.audit_id,
            title="Consent Records Sample",
            description="Sample of consent records with audit trail",
            evidence_type="document",
            location="/evidence/consent-records-2026.xlsx",
            collected_by="privacy-team@example.com",
        ),
    ]
    print(f"    ✓ {len(privacy_evidence)} privacy evidence collected")
    
    # ========================================================================
    # PHASE 5: SECURITY EVIDENCE
    # ========================================================================
    print("\n\n🛡️ PHASE 5: SECURITY EVIDENCE")
    print("-" * 80)
    
    # SecurityAgent provides security-related evidence
    print("\n[Security Agent] Preparing security evidence...")
    
    # Document access reviews
    print("\n  [Access Reviews]")
    
    access_review = security.create_assessment(
        title="Quarterly Access Review - Q4 2025",
        assessment_type="access_review",
        scope="All production system access",
        assessor="security-team@example.com",
    )
    print(f"    ✓ Access review documented: {access_review.assessment_id}")
    
    # Document security incidents
    print("\n  [Security Incidents]")
    
    incidents = [
        security.report_incident(
            title="Phishing Attempt - Credential Harvesting",
            description="Targeted phishing campaign against employees",
            severity="medium",
            incident_type="phishing",
            detected_at=datetime.utcnow() - timedelta(days=180),
            resolved_at=datetime.utcnow() - timedelta(days=179),
            root_cause="Employee clicked malicious link",
            remediation="MFA enforced, security awareness training",
        ),
        security.report_incident(
            title="Vulnerability Scan Finding",
            description="Outdated library in non-production environment",
            severity="low",
            incident_type="vulnerability",
            detected_at=datetime.utcnow() - timedelta(days=90),
            resolved_at=datetime.utcnow() - timedelta(days=85),
            root_cause="Dependency not updated",
            remediation="Library updated, automated scanning implemented",
        ),
    ]
    print(f"    ✓ {len(incidents)} security incidents documented")
    
    # Document penetration tests
    print("\n  [Penetration Tests]")
    
    pentest = security.create_finding(
        assessment_id=access_review.assessment_id,
        title="Annual Penetration Test 2025",
        description="Third-party penetration test of production environment",
        finding_type="pentest_result",
        severity="low",
        status="resolved",
        pentest_date=datetime.utcnow() - timedelta(days=180),
        pentest_firm="SecurityExperts Inc",
        findings_critical=0,
        findings_high=0,
        findings_medium=2,
        findings_low=5,
        all_remediated=True,
    )
    print(f"    ✓ Penetration test documented")
    
    # Collect security evidence
    print("\n  [Collecting Evidence]")
    
    security_evidence = [
        audit.collect_evidence(
            audit_id=soc2_audit.audit_id,
            title="Access Review Reports",
            description="Quarterly access review reports for audit period",
            evidence_type="document",
            location="/evidence/access-reviews-2025.pdf",
            collected_by="security-team@example.com",
        ),
        audit.collect_evidence(
            audit_id=soc2_audit.audit_id,
            title="Security Incident Log",
            description="Complete incident log with response documentation",
            evidence_type="document",
            location="/evidence/incident-log-2025.xlsx",
            collected_by="security-team@example.com",
        ),
        audit.collect_evidence(
            audit_id=soc2_audit.audit_id,
            title="Penetration Test Report",
            description="Annual pentest report with remediation evidence",
            evidence_type="document",
            location="/evidence/pentest-2025.pdf",
            collected_by="security-team@example.com",
        ),
        audit.collect_evidence(
            audit_id=soc2_audit.audit_id,
            title="Security Training Records",
            description="Employee security awareness training completion",
            evidence_type="document",
            location="/evidence/security-training-2025.xlsx",
            collected_by="security-team@example.com",
        ),
    ]
    print(f"    ✓ {len(security_evidence)} security evidence collected")
    
    # ========================================================================
    # PHASE 6: COMPLIANCE & LEGAL EVIDENCE
    # ========================================================================
    print("\n\n⚖️ PHASE 6: COMPLIANCE & LEGAL EVIDENCE")
    print("-" * 80)
    
    # ComplianceAgent provides compliance mappings
    print("\n[Compliance Agent] Preparing compliance evidence...")
    
    # Document certifications
    print("\n  [Certifications]")
    
    certs = [
        compliance.add_certificate(
            certificate_type="soc2_type2",
            issuer="Example Corp",
            issued_date=datetime.utcnow() - timedelta(days=455),
            expiry_date=datetime.utcnow() - timedelta(days=90),
            status="expired",  # Previous year's cert
            scope="Security, Availability, Confidentiality",
            auditor="Previous Audit Firm LLP",
        ),
        compliance.add_certificate(
            certificate_type="iso27001",
            issuer="Example Corp",
            issued_date=datetime.utcnow() - timedelta(days=365),
            expiry_date=datetime.utcnow() + timedelta(days=730),
            status="valid",
            scope="Information Security Management",
            auditor="ISO Certification Body",
        ),
    ]
    print(f"    ✓ {len(certs)} certifications documented")
    
    # Document policies
    print("\n  [Policies]")
    
    policies = [
        compliance.create_policy(
            title="Information Security Policy",
            category="security",
            version="3.2",
            status="approved",
            effective_date=datetime.utcnow() - timedelta(days=365),
            review_date=datetime.utcnow() + timedelta(days=365),
            owner="ciso@example.com",
        ),
        compliance.create_policy(
            title="Data Classification Policy",
            category="data_protection",
            version="2.1",
            status="approved",
            effective_date=datetime.utcnow() - timedelta(days=300),
            review_date=datetime.utcnow() + timedelta(days=65),
            owner="data-governance@example.com",
        ),
        compliance.create_policy(
            title="Incident Response Policy",
            category="security",
            version="4.0",
            status="approved",
            effective_date=datetime.utcnow() - timedelta(days=180),
            review_date=datetime.utcnow() + timedelta(days=185),
            owner="security-team@example.com",
        ),
    ]
    print(f"    ✓ {len(policies)} policies documented")
    
    # LegalAgent provides legal evidence
    print("\n[Legal Agent] Preparing legal evidence...")
    
    # Document contracts
    print("\n  [Contracts & Agreements]")
    
    legal_matter = legal.create_legal_matter(
        title="SOC2 Audit - Legal Documentation",
        matter_type="audit_support",
        description="Legal documentation for SOC2 Type II audit",
        priority="high",
    )
    print(f"    ✓ Legal matter created: {legal_matter.matter_id}")
    
    # Collect compliance and legal evidence
    print("\n  [Collecting Evidence]")
    
    compliance_evidence = [
        audit.collect_evidence(
            audit_id=soc2_audit.audit_id,
            title="Certification Records",
            description="SOC2, ISO27001 certificates and scope documents",
            evidence_type="document",
            location="/evidence/certifications-2025.pdf",
            collected_by="compliance-team@example.com",
        ),
        audit.collect_evidence(
            audit_id=soc2_audit.audit_id,
            title="Policy Documents",
            description="All approved policies with version history",
            evidence_type="document",
            location="/evidence/policies-2025.pdf",
            collected_by="compliance-team@example.com",
        ),
        audit.collect_evidence(
            audit_id=soc2_audit.audit_id,
            title="Customer Contracts Sample",
            description="Sample of customer contracts with SLA terms",
            evidence_type="document",
            location="/evidence/customer-contracts-2025.pdf",
            collected_by="legal-team@example.com",
        ),
        audit.collect_evidence(
            audit_id=soc2_audit.audit_id,
            title="Vendor Agreements",
            description="Key vendor agreements with security requirements",
            evidence_type="document",
            location="/evidence/vendor-agreements-2025.pdf",
            collected_by="legal-team@example.com",
        ),
    ]
    print(f"    ✓ {len(compliance_evidence)} compliance/legal evidence collected")
    
    # ========================================================================
    # PHASE 7: CONTROL TESTING
    # ========================================================================
    print("\n\n🧪 PHASE 7: CONTROL TESTING")
    print("-" * 80)
    
    # AuditAgent tests controls
    print("\n[Audit Agent] Testing control effectiveness...")
    
    # Get all controls
    controls = audit.get_controls(audit_id=soc2_audit.audit_id)
    print(f"\n  ✓ {len(controls)} controls to test")
    
    # Test each control
    tested_controls = []
    for control in controls:
        # Simulate test results
        test_results = [
            {'procedure': p, 'passed': True, 'evidence': f'evidence-{i}'}
            for i, p in enumerate(control.test_procedures)
        ]
        
        # 90% pass rate simulation
        if len(test_results) > 0 and hash(control.control_id) % 10 == 0:
            test_results[-1]['passed'] = False
        
        audit.test_control(
            control_id=control.control_id,
            tested_by="external-auditor@auditfirm.com",
            test_results=test_results,
        )
        tested_controls.append(control)
    
    effective = len([c for c in controls if c.status.value == 'effective'])
    partially = len([c for c in controls if c.status.value == 'partially_effective'])
    ineffective = len([c for c in controls if c.status.value == 'ineffective'])
    
    print(f"\n  ✓ Control testing complete:")
    print(f"    - Effective: {effective} ({effective/len(controls)*100:.0f}%)")
    print(f"    - Partially Effective: {partially} ({partially/len(controls)*100:.0f}%)")
    print(f"    - Ineffective: {ineffective} ({ineffective/len(controls)*100:.0f}%)")
    
    # Create findings for ineffective controls
    print("\n  [Creating Audit Findings]")
    
    for control in controls:
        if control.status.value == 'partially_effective':
            finding = audit.create_finding(
                audit_id=soc2_audit.audit_id,
                title=f"Control Partially Effective: {control.name}",
                description="Control not operating effectively for all test samples",
                severity=FindingSeverity.MEDIUM,
                condition="1 out of 4 test procedures failed",
                criteria="All control procedures should operate effectively",
                control_id=control.control_id,
                cause="Incomplete implementation or process gap",
                effect="Reduced assurance over control objective",
            )
            audit.update_finding(
                finding.finding_id,
                recommendation=f"Remediate gaps in {control.name}",
                management_response="Will address within 30 days",
                action_plan="Update procedure and retrain team",
                responsible_party=control.control_owner,
                due_date=datetime.utcnow() + timedelta(days=30),
            )
    
    findings = audit.get_findings(audit_id=soc2_audit.audit_id)
    print(f"  ✓ {len(findings)} audit findings created")
    
    # ========================================================================
    # PHASE 8: AUDIT REPORT
    # ========================================================================
    print("\n\n📄 PHASE 8: AUDIT REPORT")
    print("-" * 80)
    
    # Generate audit report
    print("\n[Audit Agent] Generating audit report...")
    
    report = audit.generate_audit_report(soc2_audit.audit_id)
    
    print(f"""
  ✓ Audit Report Generated:
    
    AUDIT: {report['audit']['title']}
    TYPE: {report['audit']['type']}
    STATUS: {report['audit']['status']}
    PERIOD: {report['audit']['period']['start'][:10]} to {report['audit']['period']['end'][:10]}
    
    CONTROLS:
      - Total: {report['controls']['total']}
      - Effective: {report['controls']['effective']} ({report['controls']['effectiveness_rate']:.1f}%)
      - Ineffective: {report['controls']['ineffective']}
    
    FINDINGS:
      - Total: {report['findings']['total']}
      - Open: {report['findings']['open']}
      - Critical: {report['findings']['by_severity']['critical']}
      - High: {report['findings']['by_severity']['high']}
      - Medium: {report['findings']['by_severity']['medium']}
      - Low: {report['findings']['by_severity']['low']}
    
    EVIDENCE:
      - Total items: {report['evidence']['total']}
      - Reviewed: {report['evidence']['reviewed']}
""")
    
    # Review workpapers
    print("\n  [Reviewing Workpapers]")
    
    workpapers = [
        audit.create_workpaper(
            audit_id=soc2_audit.audit_id,
            title="Security Controls Testing",
            section="Security",
            content="Detailed testing results for all security controls...",
            created_by="external-auditor@auditfirm.com",
        ),
        audit.create_workpaper(
            audit_id=soc2_audit.audit_id,
            title="Availability Controls Testing",
            section="Availability",
            content="Detailed testing results for availability controls...",
            created_by="external-auditor@auditfirm.com",
        ),
        audit.create_workpaper(
            audit_id=soc2_audit.audit_id,
            title="Confidentiality Controls Testing",
            section="Confidentiality",
            content="Detailed testing results for confidentiality controls...",
            created_by="external-auditor@auditfirm.com",
        ),
    ]
    
    for wp in workpapers:
        audit.review_workpaper(wp.workpaper_id, "audit-manager@auditfirm.com")
    
    print(f"  ✓ {len(workpapers)} workpapers created and reviewed")
    
    # Complete audit
    print("\n[Audit Agent] Completing audit...")
    
    audit.complete_audit(soc2_audit.audit_id, actual_hours=185.0)
    print(f"  ✓ Audit completed in {soc2_audit.actual_hours} hours (planned: {soc2_audit.planned_hours})")
    
    # ========================================================================
    # SUMMARY
    # ========================================================================
    print("\n\n" + "=" * 80)
    print("AUDIT PREPARATION SUMMARY")
    print("=" * 80)
    
    print(f"""
AUDIT: {soc2_audit.title}
AUDIT ID: {soc2_audit.audit_id}
TYPE: {soc2_audit.audit_type.value}
PERIOD: {audit_period_start.strftime('%Y-%m-%d')} to {audit_period_end.strftime('%Y-%m-%d')}
STATUS: {soc2_audit.status.value.upper()}

AGENTS INVOLVED:
  ✓ Audit Agent - Audit planning, control testing, evidence collection
  ✓ DataGovernance Agent - Data assets, lineage, retention policies
  ✓ Privacy Agent - Processing activities, DSARs, consent records
  ✓ Security Agent - Access reviews, incidents, penetration tests
  ✓ Compliance Agent - Certifications, policies, regulatory mappings
  ✓ Legal Agent - Contracts, vendor agreements, legal documentation

EVIDENCE COLLECTED:
  ✓ Data Governance: {len(data_evidence)} items
  ✓ Privacy: {len(privacy_evidence)} items
  ✓ Security: {len(security_evidence)} items
  ✓ Compliance/Legal: {len(compliance_evidence)} items
  ✓ Total: {report['evidence']['total']} items

CONTROLS TESTED:
  ✓ Total: {len(controls)}
  ✓ Effective: {effective} ({effective/len(controls)*100:.0f}%)
  ✓ Partially Effective: {partially}
  ✓ Ineffective: {ineffective}

FINDINGS:
  ✓ Total: {len(findings)}
  ✓ Management responses documented
  ✓ Remediation plans established

WORKPAPERS:
  ✓ {len(workpapers)} workpapers created and reviewed

AUDIT DURATION:
  ✓ Planned: {soc2_audit.planned_hours} hours
  ✓ Actual: {soc2_audit.actual_hours} hours
  ✓ Variance: {soc2_audit.planned_hours - soc2_audit.actual_hours:.0f} hours under budget
""")
    
    # Get final state from all agents
    print("\nAGENT STATES:")
    print(f"  Audit Agent: {audit.get_state()}")
    print(f"  DataGovernance Agent: {data_gov.get_state()}")
    print(f"  Privacy Agent: {privacy.get_state()}")
    print(f"  Security Agent: {security.get_state()}")
    print(f"  Compliance Agent: {compliance.get_state()}")
    print(f"  Legal Agent: {legal.get_state()}")
    
    print("\n" + "=" * 80)
    print("✅ AUDIT PREPARATION WORKFLOW COMPLETE")
    print("=" * 80)
    
    return {
        'audit': soc2_audit,
        'report': report,
        'agents': {
            'audit': audit.get_state(),
            'data_gov': data_gov.get_state(),
            'privacy': privacy.get_state(),
            'security': security.get_state(),
            'compliance': compliance.get_state(),
            'legal': legal.get_state(),
        },
    }


if __name__ == "__main__":
    result = run_audit_preparation()
    print("\n📊 Workflow execution successful!")
