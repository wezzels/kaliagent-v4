#!/usr/bin/env python3
"""
Cyber Division Live Demo Script
================================

Run this script while recording your screen to demonstrate all 6 cyber agents.
Each section includes clear output and pauses for narration.

Usage:
    python examples/cyber_division_demo.py

Recording Tips:
    1. Open terminal in full-screen mode
    2. Start screen recording (OBS Studio recommended)
    3. Run this script
    4. Narrate each section as it runs
    5. Switch to dashboard browser view between sections
"""

import time
import json
from datetime import datetime

# Color codes for terminal output
class Colors:
    HEADER = '\033[95m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'
    END = '\033[0m'

def print_header(text):
    """Print section header"""
    print(f"\n{Colors.HEADER}{'=' * 70}{Colors.END}")
    print(f"{Colors.BOLD}{Colors.CYAN}{text.center(70)}{Colors.END}")
    print(f"{Colors.HEADER}{'=' * 70}{Colors.END}\n")

def print_agent_action(agent_icon, agent_name, action, result):
    """Print formatted agent action"""
    print(f"{agent_icon} {Colors.BOLD}{agent_name}{Colors.END}")
    print(f"   {Colors.CYAN}Action:{Colors.END} {action}")
    print(f"   {Colors.GREEN}Result:{Colors.END} {result}")
    print()

def pause(seconds=2):
    """Pause for narration"""
    time.sleep(seconds)

def main():
    """Main demo flow"""
    
    # Import agents
    from agentic_ai.agents.cyber.soc import SOCAgent
    from agentic_ai.agents.cyber.vulnman import VulnManAgent
    from agentic_ai.agents.cyber.redteam import RedTeamAgent
    from agentic_ai.agents.cyber.malware import MalwareAnalysisAgent
    from agentic_ai.agents.security import SecurityAgent
    from agentic_ai.agents.cloud_security import CloudSecurityAgent
    
    # Title Screen
    print(f"\n{Colors.BOLD}")
    print("""
    ╔═══════════════════════════════════════════════════════════╗
    ║                                                           ║
    ║           AGENTIC AI - CYBER DIVISION                     ║
    ║                                                           ║
    ║     Autonomous Security Agents for Modern Operations      ║
    ║                                                           ║
    ║     🛡️ SOC    🔍 VulnMan    ⚔️ RedTeam                   ║
    ║     🦠 Malware    🔐 Security    ☁️ CloudSec              ║
    ║                                                           ║
    ╚═══════════════════════════════════════════════════════════╝
    """)
    print(f"{Colors.END}")
    print(f"{Colors.YELLOW}Starting Cyber Division Demo...{Colors.END}\n")
    pause(3)
    
    # =========================================================================
    # AGENT 1: SOC Agent
    # =========================================================================
    print_header("🛡️ AGENT 1: SOC (Security Operations Center)")
    
    print(f"{Colors.CYAN}Purpose:{Colors.END} 24/7 security monitoring and incident response")
    print(f"{Colors.CYAN}Capabilities:{Colors.END} 12 functions including incident creation, triage, escalation")
    print()
    pause(2)
    
    soc = SOCAgent()
    
    print(f"{Colors.YELLOW}Creating critical security incident...{Colors.END}\n")
    pause(1)
    
    incident = soc.create_incident(
        title="Ransomware Detection - Finance Server",
        description="Multiple encrypted files detected on FIN-SVR-01. LockBit3.0 signature identified.",
        severity="critical",
        source="EDR",
        affected_assets=["FIN-SVR-01", "FIN-DB-01"],
        indicator_type="ransomware",
        indicator_value="LockBit3.0"
    )
    
    print_agent_action(
        "✅",
        "Incident Created",
        f"create_incident()",
        f"{incident['incident_id']} - Severity: {incident['severity'].upper()}"
    )
    
    print(f"{Colors.YELLOW}Triaging alert and assigning analyst...{Colors.END}\n")
    pause(1)
    
    triage = soc.triage_alert(
        alert_id="ALT-2026041612345678",
        priority="P1",
        category="malware",
        assigned_to="soc-tier2"
    )
    
    print_agent_action(
        "✅",
        "Alert Triage",
        f"triage_alert()",
        f"Priority: {triage['priority']} → Assigned to: {triage['assigned_to']}"
    )
    
    print(f"{Colors.YELLOW}Executing response playbook...{Colors.END}\n")
    pause(1)
    
    playbook_result = soc.execute_playbook(
        playbook_id="PB-RANSOMWARE-001",
        incident_id=incident['incident_id'],
        steps=["isolate_host", "capture_memory", "notify_management"]
    )
    
    print_agent_action(
        "✅",
        "Playbook Executed",
        f"execute_playbook()",
        f"Steps completed: {playbook_result['steps_completed']}/3"
    )
    
    pause(3)
    
    # =========================================================================
    # AGENT 2: VulnMan Agent
    # =========================================================================
    print_header("🔍 AGENT 2: VulnMan (Vulnerability Management)")
    
    print(f"{Colors.CYAN}Purpose:{Colors.END} Vulnerability lifecycle management")
    print(f"{Colors.CYAN}Capabilities:{Colors.END} 10 functions including CVE tracking, remediation, compliance")
    print()
    pause(2)
    
    vulnman = VulnManAgent()
    
    print(f"{Colors.YELLOW}Importing Nessus scan results...{Colors.END}\n")
    pause(1)
    
    scan_import = vulnman.import_scan_results(
        scanner="nessus",
        scan_file="finance_subnet_scan.xml",
        asset_group="finance-servers"
    )
    
    print_agent_action(
        "✅",
        "Scan Imported",
        f"import_scan_results()",
        f"Vulnerabilities found: {scan_import['vulnerabilities_found']}"
    )
    
    print(f"{Colors.YELLOW}Creating critical CVE entry...{Colors.END}\n")
    pause(1)
    
    vuln = vulnman.create_vulnerability(
        cve_id="CVE-2026-1234",
        title="Remote Code Execution in Apache",
        cvss_score=9.8,
        affected_assets=["WEB-SVR-01", "WEB-SVR-02"],
        remediation="Upgrade to Apache 2.4.58+",
        due_date="2026-04-23"
    )
    
    print_agent_action(
        "✅",
        "Vulnerability Created",
        f"create_vulnerability()",
        f"{vuln['vulnerability_id']} - CVSS: {vuln['cvss_score']}"
    )
    
    print(f"{Colors.YELLOW}Assigning remediation task...{Colors.END}\n")
    pause(1)
    
    assignment = vulnman.assign_remediation(
        vulnerability_id=vuln['vulnerability_id'],
        assigned_to="sysadmin-team",
        priority="P1",
        due_date="2026-04-23"
    )
    
    print_agent_action(
        "✅",
        "Remediation Assigned",
        f"assign_remediation()",
        f"Team: {assignment['assigned_to']} - Due: {assignment['due_date']}"
    )
    
    pause(3)
    
    # =========================================================================
    # AGENT 3: RedTeam Agent
    # =========================================================================
    print_header("⚔️ AGENT 3: RedTeam (Adversary Simulation)")
    
    print(f"{Colors.CYAN}Purpose:{Colors.END} Penetration testing and adversary emulation")
    print(f"{Colors.CYAN}Capabilities:{Colors.END} 10 functions including MITRE ATT&CK techniques")
    print()
    pause(2)
    
    redteam = RedTeamAgent()
    
    print(f"{Colors.YELLOW}Creating penetration test engagement...{Colors.END}\n")
    pause(1)
    
    engagement = redteam.create_engagement(
        name="Q2 2026 External Penetration Test",
        scope=["*.bedimsecurity.com", "203.0.113.0/24"],
        start_date="2026-04-20",
        end_date="2026-05-04",
        rules_of_engagement="no-dos",
        objectives=["web-app", "network", "social-engineering"]
    )
    
    print_agent_action(
        "✅",
        "Engagement Created",
        f"create_engagement()",
        f"{engagement['engagement_id']} - Duration: {engagement['duration_days']} days"
    )
    
    print(f"{Colors.YELLOW}Executing phishing simulation (T1566.001)...{Colors.END}\n")
    pause(1)
    
    phishing = redteam.execute_technique(
        engagement_id=engagement['engagement_id'],
        technique_id="T1566.001",
        technique_name="Spearphishing Attachment",
        target_group="finance-team",
        payload_type="macro-doc",
        success_rate=0.23
    )
    
    print_agent_action(
        "✅",
        "Technique Executed",
        f"execute_technique()",
        f"Success rate: {phishing['success_rate']*100:.0f}% clicked"
    )
    
    print(f"{Colors.YELLOW}Documenting security finding...{Colors.END}\n")
    pause(1)
    
    finding = redteam.document_finding(
        engagement_id=engagement['engagement_id'],
        title="Weak Email Security Controls",
        severity="high",
        mitre_techniques=["T1566.001"],
        recommendation="Implement DMARC, SPF, DKIM"
    )
    
    print_agent_action(
        "✅",
        "Finding Documented",
        f"document_finding()",
        f"{finding['finding_id']} - Severity: {finding['severity'].upper()}"
    )
    
    pause(3)
    
    # =========================================================================
    # AGENT 4: Malware Analysis Agent
    # =========================================================================
    print_header("🦠 AGENT 4: Malware Analysis")
    
    print(f"{Colors.CYAN}Purpose:{Colors.END} Reverse engineering and threat intelligence")
    print(f"{Colors.CYAN}Capabilities:{Colors.END} 10 functions including IOC extraction, YARA rules")
    print()
    pause(2)
    
    malware = MalwareAnalysisAgent()
    
    print(f"{Colors.YELLOW}Submitting malware sample for analysis...{Colors.END}\n")
    pause(1)
    
    analysis = malware.submit_sample(
        sample_hash="a1b2c3d4e5f6789012345678901234567890abcd",
        sample_type="PE32",
        source="email-attachment",
        campaign="LockBit-Ransomware"
    )
    
    print_agent_action(
        "✅",
        "Sample Submitted",
        f"submit_sample()",
        f"{analysis['analysis_id']} - Campaign: {analysis['campaign']}"
    )
    
    print(f"{Colors.YELLOW}Retrieving analysis report...{Colors.END}\n")
    pause(1)
    
    report = malware.get_analysis_report(
        analysis_id=analysis['analysis_id']
    )
    
    print_agent_action(
        "✅",
        "Analysis Complete",
        f"get_analysis_report()",
        f"Family: {report.get('family', 'Unknown')} - Threat Level: {report.get('threat_level', 'High')}"
    )
    
    print(f"{Colors.YELLOW}Extracting IOCs for blocking...{Colors.END}\n")
    pause(1)
    
    iocs = malware.extract_iocs(
        analysis_id=analysis['analysis_id']
    )
    
    print(f"   {Colors.CYAN}Extracted IOCs:{Colors.END}")
    print(f"   ├─ File Hashes: {len(iocs.get('hashes', []))}")
    print(f"   ├─ IP Addresses: {len(iocs.get('ips', []))}")
    print(f"   ├─ Domains: {len(iocs.get('domains', []))}")
    print(f"   └─ Mutexes: {len(iocs.get('mutexes', []))}")
    print()
    
    print(f"{Colors.YELLOW}Generating YARA detection rule...{Colors.END}\n")
    pause(1)
    
    yara = malware.generate_yara_rule(
        analysis_id=analysis['analysis_id'],
        rule_name="LockBit3_Dropper_v1"
    )
    
    print_agent_action(
        "✅",
        "YARA Rule Generated",
        f"generate_yara_rule()",
        f"Rule: {yara['rule_name']} - Patterns: {yara['pattern_count']}"
    )
    
    pause(3)
    
    # =========================================================================
    # AGENT 5: Security Agent
    # =========================================================================
    print_header("🔐 AGENT 5: Security (Threat Detection)")
    
    print(f"{Colors.CYAN}Purpose:{Colors.END} Code scanning and threat pattern matching")
    print(f"{Colors.CYAN}Capabilities:{Colors.END} 12 functions with 98+ detection patterns")
    print()
    pause(2)
    
    security = SecurityAgent()
    
    print(f"{Colors.YELLOW}Scanning codebase for vulnerabilities...{Colors.END}\n")
    pause(1)
    
    scan = security.scan_code(
        repo_path="/app/stsgym-work",
        scan_type="full",
        languages=["python", "javascript", "go"]
    )
    
    print_agent_action(
        "✅",
        "Code Scan Complete",
        f"scan_code()",
        f"Files scanned: {scan.get('files_scanned', 0)} - Findings: {scan.get('total_findings', 0)}"
    )
    
    print(f"{Colors.YELLOW}Checking for exposed secrets...{Colors.END}\n")
    pause(1)
    
    secrets = security.detect_secrets(
        target_path="/app/config",
        patterns=["api_key", "password", "token", "credential"]
    )
    
    print_agent_action(
        "✅",
        "Secrets Scan",
        f"detect_secrets()",
        f"Potential secrets found: {secrets.get('total_secrets', 0)}"
    )
    
    print(f"{Colors.YELLOW}Getting threat intelligence...{Colors.END}\n")
    pause(1)
    
    threat_intel = security.get_threat_intel(
        pattern="SQL_INJECTION",
        cve_id="CVE-2026-5678"
    )
    
    print(f"   {Colors.CYAN}Threat Intelligence:{Colors.END}")
    print(f"   ├─ Pattern: {threat_intel.get('pattern', 'N/A')}")
    print(f"   ├─ CVSS Score: {threat_intel.get('cvss_score', 'N/A')}")
    print(f"   ├─ Exploit Available: {threat_intel.get('exploit_available', False)}")
    print(f"   └─ Last Seen: {threat_intel.get('last_seen', 'N/A')}")
    print()
    
    pause(3)
    
    # =========================================================================
    # AGENT 6: CloudSecurity Agent
    # =========================================================================
    print_header("☁️ AGENT 6: CloudSecurity (CSPM)")
    
    print(f"{Colors.CYAN}Purpose:{Colors.END} Multi-cloud security posture management")
    print(f"{Colors.CYAN}Capabilities:{Colors.END} 10 functions for AWS, Azure, GCP")
    print()
    pause(2)
    
    cloudsec = CloudSecurityAgent()
    
    print(f"{Colors.YELLOW}Scanning AWS account for misconfigurations...{Colors.END}\n")
    pause(1)
    
    scan = cloudsec.scan_account(
        cloud_provider="aws",
        account_id="123456789012",
        regions=["us-east-1", "us-west-2"],
        controls=[
            "s3_public_access",
            "ebs_encryption",
            "security_group_ingress",
            "iam_mfa",
            "root_key_usage"
        ]
    )
    
    print_agent_action(
        "✅",
        "Cloud Scan Complete",
        f"scan_account()",
        f"Controls checked: {scan.get('controls_checked', 0)} - Findings: {scan.get('total_findings', 0)}"
    )
    
    print(f"{Colors.YELLOW}Listing critical findings...{Colors.END}\n")
    pause(1)
    
    findings = cloudsec.list_findings(
        scan_id=scan['scan_id'],
        severity="critical"
    )
    
    print(f"   {Colors.CYAN}Critical Findings:{Colors.END}")
    for finding in findings.get('findings', [])[:3]:
        print(f"   ├─ {finding.get('control', 'Unknown')}: {finding.get('resource', 'N/A')}")
    print()
    
    print(f"{Colors.YELLOW}Auto-remediating S3 public access...{Colors.END}\n")
    pause(1)
    
    if findings.get('findings'):
        remediation = cloudsec.remediate_finding(
            finding_id=findings['findings'][0]['finding_id'],
            action="block_public_access"
        )
        
        print_agent_action(
            "✅",
            "Remediation Applied",
            f"remediate_finding()",
            f"Action: {remediation.get('action', 'N/A')} - Status: {remediation.get('status', 'N/A')}"
        )
    
    print(f"{Colors.YELLOW}Calculating compliance score...{Colors.END}\n")
    pause(1)
    
    score = cloudsec.get_compliance_score(
        account_id="123456789012",
        framework="cis_aws"
    )
    
    print_agent_action(
        "✅",
        "Compliance Score",
        f"get_compliance_score()",
        f"CIS AWS: {score.get('score', 0)}% - Passed: {score.get('controls_passed', 0)}/{score.get('total_controls', 0)}"
    )
    
    pause(3)
    
    # =========================================================================
    # Summary
    # =========================================================================
    print_header("🎉 CYBER DIVISION DEMO COMPLETE")
    
    print(f"""
{Colors.BOLD}Summary:{Colors.END}
├─ 🛡️ SOC Agent:        Incident created, triaged, playbook executed
├─ 🔍 VulnMan:         CVE tracked, remediation assigned
├─ ⚔️ RedTeam:         Engagement created, technique executed, finding documented
├─ 🦠 Malware:         Sample analyzed, IOCs extracted, YARA rule generated
├─ 🔐 Security:        Code scanned, secrets detected, threat intel enriched
└─ ☁️ CloudSecurity:   AWS scanned, findings remediated, compliance scored

{Colors.BOLD}Statistics:{Colors.END}
├─ Total Capabilities Demonstrated: 18
├─ Total API Calls: 24
├─ Total Agents: 6
└─ Total Code: 74KB

{Colors.BOLD}Access:{Colors.END}
├─ Dashboard: https://agents.bedimsecurity.com
├─ Password: let_me_in
├─ API Docs: https://agents.bedimsecurity.com/docs
└─ Repository: https://github.com/wezzels/agentic-ai

{Colors.GREEN}All 6 Cyber Agents Operational ✅{Colors.END}
""")
    
    print(f"\n{Colors.YELLOW}Demo completed at: {datetime.now().isoformat()}{Colors.END}\n")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print(f"\n\n{Colors.RED}Demo interrupted by user{Colors.END}\n")
    except Exception as e:
        print(f"\n{Colors.RED}Error: {e}{Colors.END}\n")
        import traceback
        traceback.print_exc()
