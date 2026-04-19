"""
Tests for KaliAgent v2 and RedTeam Agent v2
=============================================

Tests cover:
- CVE → Exploit matching
- Tool recommendations
- MITRE ATT&CK mapping
- Risk scoring
- Attack path generation
- Detection testing
"""

import pytest
from datetime import datetime
from agentic_ai.agents.cyber.kali_v2 import (
    KaliAgentV2,
    CVEMatchingEngine,
    ToolRecommendationEngine,
    RemediationEngine,
    ToolCategory,
    AuthorizationLevel,
)
from agentic_ai.agents.cyber.redteam_v2 import (
    RedTeamAgentV2,
    MITRE_ATTACK_TECHNIQUES,
)


# ============================================
# KaliAgent v2 Tests
# ============================================

class TestKaliAgentV2:
    """Test KaliAgent v2 features."""
    
    def test_agent_initialization(self):
        """Test agent initializes correctly."""
        agent = KaliAgentV2(workspace="/tmp/test-kali-v2")
        state = agent.get_state()
        
        assert state['version'] == "2.0.0"
        assert state['total_tools'] > 20  # Should have many tools
        assert 'cve_exploit_matching' in state['capabilities']
        assert 'tool_recommendations' in state['capabilities']
    
    def test_cve_matching(self):
        """Test CVE to exploit matching."""
        agent = KaliAgentV2()
        
        # Test known CVEs
        test_cases = [
            ("CVE-2017-0144", "EternalBlue", "exploit/windows/smb/ms17_010_eternalblue"),
            ("CVE-2021-44228", "Log4Shell", "exploit/multi/http/log4shell_header_injection"),
            ("CVE-2019-0708", "BlueKeep", "exploit/windows/rdp/cve_2019_0708_bluekeep_rce"),
        ]
        
        for cve_id, expected_exploit, expected_module in test_cases:
            match = agent.match_exploits_for_cve(cve_id)
            assert match is not None, f"CVE {cve_id} should have exploit"
            assert match['exploit_name'] == expected_exploit
            assert match['metasploit_module'] == expected_module
            assert match['rank'] >= 1 and match['rank'] <= 5
    
    def test_tool_recommendations(self):
        """Test AI-powered tool recommendations."""
        agent = KaliAgentV2()
        
        # Test web server target
        target_info = {
            "type": "web_server",
            "os": "linux",
            "services": [
                {"name": "http", "port": 80},
                {"name": "ssh", "port": 22},
            ],
        }
        
        recs = agent.recommend_tools_for_target(target_info)
        
        assert len(recs) > 0
        # Check for expected tools (at least some of these should be present)
        tool_names = [r['name'] for r in recs]
        assert any(name in tool_names for name in ['nuclei', 'dalfox', 'gobuster', 'httpx'])
        
        # Test AD target
        target_info_ad = {
            "type": "active_directory",
            "os": "windows",
            "services": [
                {"name": "ldap", "port": 389},
                {"name": "smb", "port": 445},
            ],
        }
        
        recs_ad = agent.recommend_tools_for_target(target_info_ad)
        assert len(recs_ad) > 0
        ad_tool_names = [r['name'] for r in recs_ad]
        assert any(name in ad_tool_names for name in ['crackmapexec', 'certipy'])
    
    def test_remediation_planning(self):
        """Test automatic remediation planning."""
        agent = KaliAgentV2()
        
        findings = [
            {"title": "EternalBlue", "cve_id": "CVE-2017-0144", "severity": "critical"},
            {"title": "Log4Shell", "cve_id": "CVE-2021-44228", "severity": "critical"},
            {"title": "SQL Injection", "category": "sql_injection", "severity": "critical"},
            {"title": "Weak Passwords", "category": "weak_passwords", "severity": "high"},
        ]
        
        plan = agent.generate_remediation_plan(findings)
        
        assert plan['total_findings'] == 4
        assert len(plan['critical']) >= 2
        assert len(plan['high']) >= 1
        assert 'estimated_effort' in plan
    
    def test_new_tool_categories(self):
        """Test new tool categories are available."""
        agent = KaliAgentV2()
        
        # Cloud Security
        cloud_tools = agent.list_tools(ToolCategory.CLOUD_SECURITY)
        assert len(cloud_tools) > 0
        assert any(t['name'] == 'pacu' for t in cloud_tools)
        assert any(t['name'] == 'prowler' for t in cloud_tools)
        
        # Active Directory
        ad_tools = agent.list_tools(ToolCategory.ACTIVE_DIRECTORY)
        assert len(ad_tools) > 0
        assert any(t['name'] == 'crackmapexec' for t in ad_tools)
        assert any(t['name'] == 'certipy' for t in ad_tools)
        
        # Container Security
        container_tools = agent.list_tools(ToolCategory.CONTAINER_SECURITY)
        assert len(container_tools) > 0
        assert any(t['name'] == 'trivy' for t in container_tools)
        assert any(t['name'] == 'kube-hunter' for t in container_tools)
    
    def test_authorization_control(self):
        """Test authorization level control."""
        agent = KaliAgentV2()
        
        # Without authorization
        authorized, msg = agent.check_authorization("pacu")
        assert not authorized
        
        # With BASIC auth
        agent.set_authorization(AuthorizationLevel.BASIC)
        authorized, msg = agent.check_authorization("pacu")
        assert authorized  # Pacu is now BASIC
        
        # Try CRITICAL tool with BASIC auth
        authorized, msg = agent.check_authorization("impacket-secretsdump")
        assert not authorized  # Requires CRITICAL
        
        # With CRITICAL auth
        agent.set_authorization(AuthorizationLevel.CRITICAL)
        authorized, msg = agent.check_authorization("impacket-secretsdump")
        assert authorized


# ============================================
# RedTeam Agent v2 Tests
# ============================================

class TestRedTeamAgentV2:
    """Test RedTeam Agent v2 features."""
    
    def test_agent_initialization(self):
        """Test agent initializes correctly."""
        agent = RedTeamAgentV2()
        state = agent.get_state()
        
        assert state['version'] == "2.0.0"
        assert state['mitre_techniques_loaded'] > 20
        assert 'mitre_attack_mapping' in state['capabilities']
        assert 'risk_scoring' in state['capabilities']
    
    def test_mitre_technique_lookup(self):
        """Test MITRE ATT&CK technique lookup."""
        agent = RedTeamAgentV2()
        
        # Test various techniques
        test_techniques = [
            ("T1566", "Phishing", "initial_access"),
            ("T1059", "Command and Scripting Interpreter", "execution"),
            ("T1003", "OS Credential Dumping", "credential_access"),
            ("T1021", "Remote Services", "lateral_movement"),
            ("T1486", "Data Encrypted for Impact", "impact"),
        ]
        
        for tech_id, expected_name, expected_tactic in test_techniques:
            tech = agent.get_technique(tech_id)
            assert tech is not None
            assert tech['name'] == expected_name
            assert tech['tactic'] == expected_tactic
    
    def test_mitre_coverage(self):
        """Test MITRE coverage calculation."""
        agent = RedTeamAgentV2()
        
        # Add findings with MITRE mappings
        agent.findings = {
            "f1": {
                "engagement_id": "eng_test",
                "severity": "critical",
                "mitre_attack": ["T1190", "T1059"],
            },
            "f2": {
                "engagement_id": "eng_test",
                "severity": "high",
                "mitre_attack": ["T1021", "T1003"],
            },
        }
        
        coverage = agent.get_mitre_coverage("eng_test")
        
        assert coverage['total_techniques'] > 0
        assert len(coverage['techniques_mapped']) >= 4
        assert coverage['coverage_percentage'] > 0
    
    def test_risk_scoring(self):
        """Test risk scoring calculation."""
        agent = RedTeamAgentV2()
        
        # Add findings of various severities
        agent.findings = {
            "f1": {"engagement_id": "eng_test", "severity": "critical", "mitre_attack": ["T1190"]},
            "f2": {"engagement_id": "eng_test", "severity": "critical", "mitre_attack": ["T1059"]},
            "f3": {"engagement_id": "eng_test", "severity": "high", "mitre_attack": ["T1021"]},
            "f4": {"engagement_id": "eng_test", "severity": "medium", "mitre_attack": []},
        }
        
        risk = agent.calculate_engagement_risk("eng_test")
        
        assert risk.overall_risk_score > 0
        assert risk.overall_risk_score <= 100
        assert risk.risk_level in ['low', 'medium', 'high', 'critical']
        assert 'severity' in risk.risk_factors
        assert 'mitre_coverage' in risk.risk_factors
    
    def test_attack_path_generation(self):
        """Test attack path generation."""
        agent = RedTeamAgentV2()
        
        # Add findings
        agent.findings = {
            "f1": {
                "engagement_id": "eng_test",
                "title": "SQL Injection",
                "severity": "critical",
                "mitre_attack": ["T1190"],
            },
            "f2": {
                "engagement_id": "eng_test",
                "title": "Credential Dumping",
                "severity": "high",
                "mitre_attack": ["T1003"],
            },
        }
        
        paths = agent.generate_attack_path_from_findings("eng_test")
        
        assert len(paths) > 0
        path = paths[0]
        assert 'path_id' in path
        assert 'visualization' in path
        assert 'nodes' in path['visualization']
        assert 'edges' in path['visualization']
    
    def test_pivot_identification(self):
        """Test pivot point identification."""
        agent = RedTeamAgentV2()
        
        # Add targets
        agent.targets = {
            "t1": {
                "target_id": "t1",
                "engagement_id": "eng_test",
                "ip_address": "192.168.1.10",
                "accessed": True,
                "services": [{"name": "smb", "port": 445}],
                "credentials_found": [{"username": "admin", "password": "test"}],
            },
            "t2": {
                "target_id": "t2",
                "engagement_id": "eng_test",
                "ip_address": "192.168.1.20",
                "accessed": False,
                "services": [],
            },
        }
        
        pivots = agent.identify_pivot_points("eng_test")
        
        assert len(pivots) > 0
        pivot = pivots[0]
        assert pivot.source_host == "192.168.1.10"
        assert "192.168.1.20" in pivot.target_hosts
        assert pivot.method in ['psexec', 'wmi', 'ssh', 'rdp']
    
    def test_detection_testing(self):
        """Test purple team detection testing."""
        agent = RedTeamAgentV2()
        
        # Create detection test
        test = agent.create_detection_test(
            technique_id="T1059",
            engagement_id="eng_test",
            test_type="atomic",
        )
        
        assert test.test_id is not None
        assert test.technique_id == "T1059"
        assert test.status == "planned"
        
        # Execute test (detected)
        agent.execute_detection_test(
            test.test_id,
            detected=True,
            detection_time_seconds=120,
            detection_source="SIEM",
        )
        
        assert test.status == "executed"
        assert test.detected is True
        assert test.detection_time_seconds == 120
    
    def test_executive_summary(self):
        """Test executive summary generation."""
        agent = RedTeamAgentV2()
        
        # Setup engagement
        agent.engagements["eng_test"] = {
            "name": "Q2 Red Team Exercise",
            "engagement_type": "red_team",
            "start_date": "2026-04-01",
            "end_date": "2026-04-19",
        }
        
        # Add findings
        agent.findings = {
            "f1": {"engagement_id": "eng_test", "severity": "critical", "mitre_attack": ["T1190"]},
            "f2": {"engagement_id": "eng_test", "severity": "high", "mitre_attack": ["T1021"]},
        }
        
        # Add detection test
        test = agent.create_detection_test("T1059", "eng_test")
        agent.execute_detection_test(test.test_id, detected=True, detection_time_seconds=120)
        
        summary = agent.generate_executive_summary("eng_test")
        
        assert summary['engagement_name'] == "Q2 Red Team Exercise"
        assert 'overall_risk' in summary
        assert 'key_findings' in summary
        assert 'mitre_coverage' in summary
        assert 'recommendations' in summary
        assert len(summary['recommendations']) > 0


# ============================================
# Integration Tests
# ============================================

class TestIntegration:
    """Integration tests for v2 agents."""
    
    def test_full_engagement_workflow(self):
        """Test complete engagement workflow."""
        # Initialize agents
        kali = KaliAgentV2()
        redteam = RedTeamAgentV2()
        
        # 1. Scan target with recommendations
        target_info = {
            "type": "web_server",
            "os": "linux",
            "services": [
                {"name": "http", "port": 80, "version": "nginx 1.18.0"},
                {"name": "ssh", "port": 22},
            ],
        }
        
        recs = kali.recommend_tools_for_target(target_info)
        assert len(recs) > 0
        
        # 2. Simulate findings from scan
        findings = [
            {"title": "SQL Injection", "cve_id": None, "category": "sql_injection", "severity": "critical"},
            {"title": "Outdated Nginx", "cve_id": "CVE-2021-23017", "severity": "high"},
        ]
        
        # 3. Generate remediation plan
        plan = kali.generate_remediation_plan(findings)
        assert plan['total_findings'] == 2
        
        # 4. Map to MITRE ATT&CK
        for finding in findings:
            techniques = redteam.map_finding_to_mitre(finding)
            finding['mitre_attack'] = techniques
        
        # 5. Calculate risk
        redteam.findings = {
            f"f{i}": {"engagement_id": "eng_test", **f}
            for i, f in enumerate(findings)
        }
        
        risk = redteam.calculate_engagement_risk("eng_test")
        assert risk.overall_risk_score > 0
        
        # 6. Generate executive summary
        redteam.engagements["eng_test"] = {
            "name": "Web App Pentest",
            "engagement_type": "penetration_test",
            "start_date": "2026-04-19",
        }
        
        summary = redteam.generate_executive_summary("eng_test")
        assert summary is not None
        assert summary['overall_risk']['score'] > 0


# ============================================
# Run Tests
# ============================================

if __name__ == "__main__":
    pytest.main([__file__, "-v"])
