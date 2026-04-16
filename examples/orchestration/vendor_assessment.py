"""
Vendor Risk Assessment - Multi-Agent Orchestration Example
===========================================================

Demonstrates comprehensive vendor risk assessment:
- VendorRiskAgent: Initiates assessment, SIG questionnaire
- SecurityAgent: Reviews security controls, penetration test results
- ComplianceAgent: Checks regulatory compliance (SOC2, ISO27001, GDPR)
- LegalAgent: Reviews contracts, SLAs, data processing agreements

This example shows third-party risk management workflow.
"""

import sys
from datetime import datetime, timedelta
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from agentic_ai.agents.vendor_risk import VendorRiskAgent, VendorTier, AssessmentType, QuestionnaireType, RiskDomain
from agentic_ai.agents.security import SecurityAgent
from agentic_ai.agents.compliance import ComplianceAgent
from agentic_ai.agents.legal import LegalAgent


def run_vendor_assessment():
    """Execute comprehensive vendor risk assessment workflow."""
    
    print("=" * 80)
    print("VENDOR RISK ASSESSMENT - Multi-Agent Orchestration")
    print("=" * 80)
    print()
    
    # Initialize all agents
    vendor_risk = VendorRiskAgent()
    security = SecurityAgent()
    compliance = ComplianceAgent()
    legal = LegalAgent()
    
    # ========================================================================
    # PHASE 1: VENDOR ONBOARDING
    # ========================================================================
    print("\n🏢 PHASE 1: VENDOR ONBOARDING")
    print("-" * 80)
    
    # VendorRisk Agent registers new vendor
    print("\n[VendorRisk Agent] Registering new vendor...")
    
    vendor = vendor_risk.add_vendor(
        name="CloudData Analytics",
        legal_name="CloudData Analytics Inc",
        tier=VendorTier.TIER_1,  # Critical - handles customer data
        category="saas",
        relationship_type="vendor",
        contract_start=datetime.utcnow(),
        contract_end=datetime.utcnow() + timedelta(days=730),  # 2 years
        contract_value=500000.0,  # $500K annual
        primary_contact="sales@clouddata.io",
        security_contact="security@clouddata.io",
        risk_owner="procurement@example.com",
    )
    print(f"  ✓ Vendor registered: {vendor.name}")
    print(f"  ✓ Tier: {vendor.tier.value} (Critical)")
    print(f"  ✓ Contract value: ${vendor.contract_value:,.0f}/year")
    print(f"  ✓ Risk owner: {vendor.risk_owner}")
    
    # Calculate inherent risk
    inherent_risk = vendor_risk.calculate_vendor_risk(vendor.vendor_id)
    print(f"  ✓ Inherent risk score: {inherent_risk:.2f} (High due to Tier 1)")
    
    # ========================================================================
    # PHASE 2: SECURITY QUESTIONNAIRE (SIG)
    # ========================================================================
    print("\n\n📋 PHASE 2: SECURITY QUESTIONNAIRE (SIG)")
    print("-" * 80)
    
    # Create SIG Core questionnaire
    print("\n[VendorRisk Agent] Creating SIG Core questionnaire...")
    
    questionnaire = vendor_risk.create_questionnaire(
        vendor_id=vendor.vendor_id,
        questionnaire_type=QuestionnaireType.SIG_CORE,
        version="2024.1",
    )
    print(f"  ✓ Questionnaire created: {questionnaire.questionnaire_id}")
    print(f"  ✓ Type: {questionnaire.questionnaire_type.value}")
    print(f"  ✓ Total questions: {questionnaire.total_questions}")
    
    # Send questionnaire to vendor
    print("\n[VendorRisk Agent] Sending questionnaire to vendor...")
    
    vendor_risk.send_questionnaire(questionnaire.questionnaire_id)
    print(f"  ✓ Questionnaire sent to {vendor.security_contact}")
    
    # Simulate vendor responses (sample across domains)
    print("\n[VendorRisk Agent] Processing vendor responses...")
    
    # Get questions and simulate responses
    questions = [q for q in vendor_risk.questions.values() if q.questionnaire_id == questionnaire.questionnaire_id][:20]
    
    # Simulate responses with varying scores
    response_scores = []
    for i, q in enumerate(questions):
        if i % 5 == 0:  # Every 5th question is partial
            response = "Partially Implemented"
            score = 0.5
        elif i % 7 == 0:  # Every 7th is No
            response = "No"
            score = 0.0
        else:  # Most are Yes
            response = "Yes"
            score = 1.0
        
        vendor_risk.respond_to_question(
            question_id=q.question_id,
            response=response,
            evidence_provided=(score == 1.0),
            notes=f"Response {i+1} of {len(questions)}",
        )
        response_scores.append(score)
    
    avg_score = sum(response_scores) / len(response_scores)
    print(f"  ✓ {len(questions)} responses processed")
    print(f"  ✓ Response rate: {len([s for s in response_scores if s > 0])}/{len(questions)} ({len([s for s in response_scores if s > 0])/len(questions)*100:.0f}%)")
    print(f"  ✓ Average score: {avg_score:.2f} ({avg_score*100:.0f}%)")
    
    # Mark questionnaire as completed
    questionnaire.status = "completed"
    questionnaire.completed_at = datetime.utcnow()
    
    # ========================================================================
    # PHASE 3: SECURITY ASSESSMENT
    # ========================================================================
    print("\n\n🔒 PHASE 3: SECURITY ASSESSMENT")
    print("-" * 80)
    
    # SecurityAgent reviews vendor security
    print("\n[Security Agent] Conducting security assessment...")
    
    # Create security assessment
    security_assessment = security.create_assessment(
        title=f"Security Assessment - {vendor.name}",
        assessment_type="vendor_security",
        scope="Cloud infrastructure, application security, data protection",
        assessor="security-team@example.com",
        target_vendor=vendor.name,
    )
    print(f"  ✓ Security assessment created: {security_assessment.assessment_id}")
    
    # Review security controls
    print("\n[Security Agent] Evaluating security controls...")
    
    security_controls = [
        security.add_control(
            assessment_id=security_assessment.assessment_id,
            name="Access Control",
            description="MFA, RBAC, least privilege",
            control_type="preventive",
            category="access_management",
            status="effective",
        ),
        security.add_control(
            assessment_id=security_assessment.assessment_id,
            name="Encryption",
            description="Data at rest and in transit",
            control_type="preventive",
            category="data_protection",
            status="effective",
        ),
        security.add_control(
            assessment_id=security_assessment.assessment_id,
            name="Vulnerability Management",
            description="Monthly scans, patching SLA",
            control_type="detective",
            category="vulnerability_management",
            status="partially_effective",
        ),
        security.add_control(
            assessment_id=security_assessment.assessment_id,
            name="Incident Response",
            description="24/7 SOC, 1hr response time",
            control_type="corrective",
            category="incident_response",
            status="effective",
        ),
        security.add_control(
            assessment_id=security_assessment.assessment_id,
            name="Penetration Testing",
            description="Annual pentest, last: 6 months ago",
            control_type="detective",
            category="security_testing",
            status="effective",
        ),
    ]
    print(f"  ✓ {len(security_controls)} security controls evaluated")
    
    # Review penetration test results
    print("\n[Security Agent] Reviewing penetration test results...")
    
    pentest_report = security.create_finding(
        assessment_id=security_assessment.assessment_id,
        title="Penetration Test Summary",
        description="Annual penetration test conducted by third-party firm",
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
    print(f"  ✓ Penetration test reviewed")
    print(f"    - Critical: {pentest_report.findings_critical}")
    print(f"    - High: {pentest_report.findings_high}")
    print(f"    - Medium: {pentest_report.findings_medium} (remediated)")
    print(f"    - Low: {pentest_report.findings_low} (remediated)")
    
    # Create security findings from questionnaire
    print("\n[Security Agent] Identifying security gaps...")
    
    security_findings = [
        security.create_finding(
            assessment_id=security_assessment.assessment_id,
            title="Incomplete MFA Rollout",
            description="15% of users do not have MFA enabled",
            finding_type="control_gap",
            severity="medium",
            status="open",
            recommendation="Enforce MFA for all users within 30 days",
        ),
        security.create_finding(
            assessment_id=security_assessment.assessment_id,
            title="Vulnerability Patching SLA Not Met",
            description="Critical patches sometimes exceed 7-day SLA",
            finding_type="process_gap",
            severity="medium",
            status="open",
            recommendation="Improve patching automation and monitoring",
        ),
    ]
    print(f"  ✓ {len(security_findings)} security findings identified")
    
    # ========================================================================
    # PHASE 4: COMPLIANCE VERIFICATION
    # ========================================================================
    print("\n\n✅ PHASE 4: COMPLIANCE VERIFICATION")
    print("-" * 80)
    
    # ComplianceAgent verifies certifications
    print("\n[Compliance Agent] Verifying compliance certifications...")
    
    # Create compliance assessment
    compliance_assessment = compliance.create_assessment(
        name=f"Vendor Compliance Review - {vendor.name}",
        assessment_type="vendor_compliance",
        scope="SOC2, ISO27001, GDPR, HIPAA",
        assessor="compliance-team@example.com",
    )
    print(f"  ✓ Compliance assessment created: {compliance_assessment.assessment_id}")
    
    # Verify SOC2 Type II
    print("\n[Compliance Agent] Verifying SOC2 Type II...")
    
    soc2_cert = compliance.add_certificate(
        certificate_type="soc2_type2",
        issuer="CloudData Analytics",
        issued_date=datetime.utcnow() - timedelta(days=90),
        expiry_date=datetime.utcnow() + timedelta(days=275),
        status="valid",
        scope="Cloud-based data analytics platform",
        auditor="Big4 Audit Firm LLP",
    )
    print(f"  ✓ SOC2 Type II: {soc2_cert.status.upper()} (expires in {275} days)")
    
    # Verify ISO27001
    print("\n[Compliance Agent] Verifying ISO27001...")
    
    iso_cert = compliance.add_certificate(
        certificate_type="iso27001",
        issuer="CloudData Analytics",
        issued_date=datetime.utcnow() - timedelta(days=180),
        expiry_date=datetime.utcnow() + timedelta(days=545),
        status="valid",
        scope="Information Security Management",
        auditor="ISO Certification Body",
    )
    print(f"  ✓ ISO27001: {iso_cert.status.upper()} (expires in {545} days)")
    
    # Verify GDPR compliance
    print("\n[Compliance Agent] Assessing GDPR compliance...")
    
    gdpr_assessment = compliance.check_gdpr_compliance(
        processing_type="vendor_data_processing",
        data_categories=["personal_data", "customer_analytics"],
        data_processor=True,
        dpa_signed=True,
        eu_data_transfer=True,
        transfer_mechanism="SCCs",
    )
    print(f"  ✓ GDPR Assessment: {gdpr_assessment.get('compliant', False)}")
    print(f"    - DPA signed: {gdpr_assessment.get('dpa_signed', False)}")
    print(f"    - Transfer mechanism: {gdpr_assessment.get('transfer_mechanism', 'N/A')}")
    
    # Check HIPAA (if applicable)
    print("\n[Compliance Agent] Checking HIPAA compliance...")
    
    hipaa_status = compliance.check_hipaa_compliance(
        phi_handled=False,  # This vendor doesn't handle PHI
        baa_required=False,
    )
    print(f"  ✓ HIPAA: Not Applicable (no PHI)")
    
    # Create compliance findings
    print("\n[Compliance Agent] Documenting compliance gaps...")
    
    compliance_findings = [
        compliance.create_finding(
            assessment_id=compliance_assessment.assessment_id,
            title="SOC2 Report Age",
            description="SOC2 report is 3 months old, request updated report",
            severity="low",
            status="open",
            recommendation="Request updated SOC2 Type II report",
        ),
    ]
    print(f"  ✓ {len(compliance_findings)} compliance findings documented")
    
    # ========================================================================
    # PHASE 5: LEGAL REVIEW
    # ========================================================================
    print("\n\n⚖️ PHASE 5: LEGAL REVIEW")
    print("-" * 80)
    
    # LegalAgent reviews contracts
    print("\n[Legal Agent] Reviewing legal documents...")
    
    # Create legal matter for vendor review
    legal_matter = legal.create_legal_matter(
        title=f"Vendor Contract Review - {vendor.name}",
        matter_type="contract_review",
        description="Comprehensive legal review of vendor agreement",
        priority="high",
        related_matters=[],
    )
    print(f"  ✓ Legal matter created: {legal_matter.matter_id}")
    
    # Review Master Services Agreement
    print("\n[Legal Agent] Reviewing Master Services Agreement...")
    
    msa_review = legal.review_contract(
        contract_type="msa",
        contract_id=f"MSA-{vendor.name.replace(' ', '-')}",
        counterparty=vendor.legal_name,
        review_areas=[
            "liability_caps",
            "indemnification",
            "termination_rights",
            "ip_ownership",
            "confidentiality",
        ],
    )
    print(f"  ✓ MSA reviewed")
    print(f"    - Liability cap: ${msa_review.get('liability_cap', 'N/A'):,}")
    print(f"    - Termination for cause: {msa_review.get('termination_for_cause', 'N/A')}")
    print(f"    - Auto-renewal: {msa_review.get('auto_renewal', 'N/A')}")
    
    # Review Data Processing Agreement
    print("\n[Legal Agent] Reviewing Data Processing Agreement...")
    
    dpa_review = legal.review_contract(
        contract_type="dpa",
        contract_id=f"DPA-{vendor.name.replace(' ', '-')}",
        counterparty=vendor.legal_name,
        review_areas=[
            "data_ownership",
            "subprocessors",
            "data_return_deletion",
            "breach_notification",
            "audit_rights",
        ],
    )
    print(f"  ✓ DPA reviewed")
    print(f"    - Data ownership: {dpa_review.get('data_ownership', 'Customer retains all rights')}")
    print(f"    - Breach notification: {dpa_review.get('breach_notification', '48 hours')}")
    print(f"    - Subprocessors allowed: {dpa_review.get('subprocessors', 'With notice')}")
    
    # Review SLA
    print("\n[Legal Agent] Reviewing Service Level Agreement...")
    
    sla_terms = legal.create_contract_clause(
        matter_id=legal_matter.matter_id,
        clause_type="sla",
        title="Service Level Commitments",
        content="""
        - Uptime guarantee: 99.9% monthly
        - Performance: API response time < 500ms (P95)
        - Support response: 1 hour for critical, 4 hours for high
        - Service credits: 10% credit for each 0.1% below 99.9%
        - Termination right: If uptime < 99.0% for 2 consecutive months
        """,
    )
    print(f"  ✓ SLA terms documented")
    print(f"    - Uptime guarantee: 99.9%")
    print(f"    - Critical support response: 1 hour")
    print(f"    - Service credits: 10% per 0.1% below SLA")
    
    # Identify legal risks
    print("\n[Legal Agent] Identifying legal risks...")
    
    legal_findings = [
        legal.create_compliance_timeline(
            matter_id=legal_matter.matter_id,
            events=[
                {
                    'event': 'Contract renewal notice deadline',
                    'deadline': datetime.utcnow() + timedelta(days=670),
                    'status': 'scheduled',
                    'notes': '90 days before contract end',
                },
                {
                    'event': 'Annual security review',
                    'deadline': datetime.utcnow() + timedelta(days=365),
                    'status': 'scheduled',
                    'notes': 'Required by contract Section 8.3',
                },
            ],
        ),
    ]
    print(f"  ✓ {len(legal_findings)} legal timelines established")
    
    # ========================================================================
    # PHASE 6: RISK SCORING & DECISION
    # ========================================================================
    print("\n\n📊 PHASE 6: RISK SCORING & DECISION")
    print("-" * 80)
    
    # Create comprehensive assessment
    print("\n[VendorRisk Agent] Creating comprehensive risk assessment...")
    
    assessment = vendor_risk.create_assessment(
        vendor_id=vendor.vendor_id,
        assessment_type=AssessmentType.INITIAL,
        assessor="vendor-risk-team@example.com",
        questionnaire_id=questionnaire.questionnaire_id,
    )
    print(f"  ✓ Assessment created: {assessment.assessment_id}")
    
    # Calculate overall risk score
    print("\n[VendorRisk Agent] Calculating risk scores...")
    
    # Security score (from SecurityAgent findings)
    security_score = 85.0  # 2 medium findings
    
    # Compliance score (from ComplianceAgent)
    compliance_score = 92.0  # SOC2, ISO27001 valid, GDPR compliant
    
    # Legal score (from LegalAgent review)
    legal_score = 90.0  # Standard terms, acceptable risks
    
    # Overall weighted score
    overall_score = (
        security_score * 0.4 +
        compliance_score * 0.35 +
        legal_score * 0.25
    )
    
    print(f"  ✓ Security Score: {security_score:.1f}/100")
    print(f"  ✓ Compliance Score: {compliance_score:.1f}/100")
    print(f"  ✓ Legal Score: {legal_score:.1f}/100")
    print(f"  ✓ Overall Risk Score: {overall_score:.1f}/100")
    
    # Complete assessment
    vendor_risk.complete_assessment(
        assessment_id=assessment.assessment_id,
        inherent_risk_score=inherent_risk,
        control_effectiveness=overall_score / 100,
        residual_risk_score=1.0 - (overall_score / 100),
        findings=[
            {
                'domain': RiskDomain.INFORMATION_SECURITY,
                'title': 'Incomplete MFA Rollout',
                'description': '15% of users without MFA',
                'severity': 'medium',
                'inherent_risk': 0.6,
                'control_effectiveness': 0.7,
                'residual_risk': 0.4,
            },
            {
                'domain': RiskDomain.COMPLIANCE,
                'title': 'SOC2 Report Age',
                'description': 'Report is 3 months old',
                'severity': 'low',
                'inherent_risk': 0.3,
                'control_effectiveness': 0.9,
                'residual_risk': 0.2,
            },
        ],
        recommendations=[
            "Require MFA enforcement within 30 days",
            "Request updated SOC2 Type II report",
            "Schedule annual security review",
            "Monitor patching SLA compliance",
        ],
        overall_opinion="APPROVED WITH CONDITIONS",
    )
    print(f"  ✓ Assessment completed")
    print(f"  ✓ Residual risk level: {assessment.residual_risk_level.value}")
    print(f"  ✓ Overall opinion: {assessment.overall_opinion}")
    
    # Enable continuous monitoring
    print("\n[VendorRisk Agent] Enabling continuous monitoring...")
    
    monitor = vendor_risk.enable_monitoring(
        vendor_id=vendor.vendor_id,
        monitoring_types=['security_ratings', 'breaches', 'news', 'financial'],
        check_frequency="weekly",
    )
    print(f"  ✓ Continuous monitoring enabled: {monitor.monitor_id}")
    print(f"    - Check frequency: {monitor.check_frequency}")
    print(f"    - Monitoring types: {', '.join(monitor.monitoring_types)}")
    
    # ========================================================================
    # SUMMARY
    # ========================================================================
    print("\n\n" + "=" * 80)
    print("VENDOR ASSESSMENT SUMMARY")
    print("=" * 80)
    
    print(f"""
VENDOR: {vendor.name}
LEGAL NAME: {vendor.legal_name}
TIER: {vendor.tier.value} (Critical)
CONTRACT VALUE: ${vendor.contract_value:,.0f}/year

ASSESSMENT RESULT: {assessment.overall_opinion}

RISK SCORES:
  ✓ Inherent Risk: {inherent_risk:.2f}
  ✓ Overall Score: {overall_score:.1f}/100
  ✓ Residual Risk: {assessment.residual_risk_score:.2f}
  ✓ Risk Level: {assessment.residual_risk_level.value.upper()}

BREAKDOWN:
  ✓ Security: {security_score:.1f}/100 (2 medium findings)
  ✓ Compliance: {compliance_score:.1f}/100 (SOC2, ISO27001 valid)
  ✓ Legal: {legal_score:.1f}/100 (standard terms)

CERTIFICATIONS:
  ✓ SOC2 Type II: Valid (expires in 275 days)
  ✓ ISO27001: Valid (expires in 545 days)
  ✓ GDPR: Compliant (SCCs in place)

FINDINGS:
  ✓ Security: {len(security_findings)} findings
  ✓ Compliance: {len(compliance_findings)} findings
  ✓ Legal: Timeline events established

RECOMMENDATIONS:
{chr(10).join(f"  • {rec}" for rec in assessment.recommendations)}

NEXT REVIEW: {format_date(datetime.utcnow() + timedelta(days=365))}
""")
    
    # Get final state from all agents
    print("\nAGENT STATES:")
    print(f"  VendorRisk Agent: {vendor_risk.get_state()}")
    print(f"  Security Agent: {security.get_state()}")
    print(f"  Compliance Agent: {compliance.get_state()}")
    print(f"  Legal Agent: {legal.get_state()}")
    
    print("\n" + "=" * 80)
    print("✅ VENDOR RISK ASSESSMENT WORKFLOW COMPLETE")
    print("=" * 80)
    
    return {
        'vendor': vendor,
        'assessment': assessment,
        'overall_score': overall_score,
        'agents': {
            'vendor_risk': vendor_risk.get_state(),
            'security': security.get_state(),
            'compliance': compliance.get_state(),
            'legal': legal.get_state(),
        },
    }


def format_date(dt):
    """Format datetime for display."""
    return dt.strftime("%Y-%m-%d")


if __name__ == "__main__":
    result = run_vendor_assessment()
    print("\n📊 Workflow execution successful!")
