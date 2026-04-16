"""
SecurityAgent Integration Tests
================================

Integration tests for SecurityAgent with Lead Agent orchestration
and end-to-end security workflows.
"""

import pytest


class TestSecurityAgentCapabilities:
    """Test SecurityAgent capabilities export for orchestration."""
    
    def test_get_capabilities(self):
        """Test capabilities export for Lead Agent."""
        from agentic_ai.agents.security import get_capabilities, ThreatType, SeverityLevel
        
        caps = get_capabilities()
        
        assert caps['agent_type'] == 'security'
        assert caps['version'] == '1.0.0'
        assert len(caps['capabilities']) >= 14
        
        # Verify all key capabilities
        required_caps = [
            'scan_code', 'scan_file', 'scan_directory',
            'create_incident', 'update_incident_status', 'get_incidents',
            'register_secret', 'rotate_secret', 'generate_secure_secret',
            'validate_password', 'check_rate_limit',
            'log_access', 'detect_anomalies',
            'generate_security_report',
        ]
        
        for cap in required_caps:
            assert cap in caps['capabilities'], f"Missing capability: {cap}"
        
        # Verify threat types
        assert len(caps['threat_types']) >= 20
        assert 'sql_injection' in caps['threat_types']
        assert 'cross_site_scripting' in caps['threat_types']
        assert 'brute_force' in caps['threat_types']
        
        # Verify severity levels
        assert len(caps['severity_levels']) == 5
        assert 'critical' in caps['severity_levels']
        assert 'high' in caps['severity_levels']


class TestSecurityLeadAgentOrchestration:
    """Test SecurityAgent integration with Lead Agent patterns."""
    
    def test_security_task_delegation(self):
        """Test Lead Agent can delegate security tasks."""
        from agentic_ai.agents.security import SecurityAgent, ThreatType, SeverityLevel
        
        agent = SecurityAgent()
        
        # Simulate Lead Agent delegating security scan
        task_result = agent.scan_code(
            "query = 'SELECT * FROM users WHERE id=' + user_id",
            "api/users.py"
        )
        
        assert len(task_result) >= 1
        assert task_result[0].threat_type == ThreatType.SQL_INJECTION
        assert task_result[0].severity == SeverityLevel.CRITICAL
    
    def test_security_incident_escalation(self):
        """Test security incidents can be escalated to Lead Agent."""
        from agentic_ai.agents.security import SecurityAgent, ThreatType, SeverityLevel
        
        agent = SecurityAgent()
        
        # Create critical incident
        incident = agent.create_incident(
            title="Critical: SQL Injection Attack",
            description="Multiple SQL injection attempts detected",
            severity=SeverityLevel.CRITICAL,
            threat_type=ThreatType.SQL_INJECTION,
            source_ip="10.0.0.100",
            target_resource="/api/users",
        )
        
        # Verify incident is ready for escalation
        assert incident.severity == SeverityLevel.CRITICAL
        assert incident.status == "investigating"  # Auto-responded
        assert len(incident.response_actions) >= 1
        
        # Simulate Lead Agent receiving escalation
        escalation_data = {
            'incident_id': incident.incident_id,
            'severity': incident.severity.value,
            'title': incident.title,
            'actions_taken': incident.response_actions,
        }
        
        assert escalation_data['severity'] == 'critical'
        assert len(escalation_data['actions_taken']) > 0
    
    def test_security_policy_enforcement_workflow(self):
        """Test security policy enforcement in workflow."""
        from agentic_ai.agents.security import SecurityAgent
        
        agent = SecurityAgent()
        
        # Simulate user registration workflow
        user_passwords = [
            ("user1", "weak"),
            ("user2", "password123"),
            ("user3", "SecureP@ssw0rd123!"),
        ]
        
        results = []
        for username, password in user_passwords:
            is_valid, violations = agent.validate_password(password)
            results.append({
                'username': username,
                'allowed': is_valid,
                'violations': violations,
            })
        
        # Verify policy enforcement
        assert results[0]['allowed'] is False  # weak
        assert results[1]['allowed'] is False  # password123
        assert results[2]['allowed'] is True   # SecureP@ssw0rd123!
    
    def test_rate_limiting_workflow(self):
        """Test rate limiting in authentication workflow."""
        from agentic_ai.agents.security import SecurityAgent
        
        agent = SecurityAgent()
        
        # Simulate login attempts
        login_results = []
        for i in range(10):
            allowed, remaining = agent.check_rate_limit("user123", "login")
            login_results.append(allowed)
            
            # Log the attempt
            agent.log_access(
                user_id="user123",
                resource="/api/login",
                action="login",
                source_ip="10.0.0.1",
                success=False,
            )
        
        # First 5 should be allowed, rest blocked
        assert login_results[:5] == [True] * 5
        assert login_results[5:] == [False] * 5


class TestSecurityScanWorkflows:
    """Test comprehensive security scanning workflows."""
    
    def test_full_codebase_scan(self):
        """Test scanning entire codebase."""
        from agentic_ai.agents.security import SecurityAgent, SeverityLevel
        
        agent = SecurityAgent()
        
        # Scan multiple files
        test_files = [
            ("file1.py", "query = 'SELECT * FROM x WHERE a=' + input"),
            ("file2.py", "return '<script>' + user_input + '</script>'"),
            ("file3.py", "open('/data/' + filename)"),
            ("file4.py", "AWS_KEY = 'AKIAIOSFODNN7EXAMPLE'"),
        ]
        
        all_findings = []
        for filename, code in test_files:
            findings = agent.scan_code(code, filename)
            all_findings.extend(findings)
        
        # Verify findings
        assert len(all_findings) >= 4
        
        # Should have variety of threat types
        threat_types = set(f.threat_type.value for f in all_findings)
        assert 'sql_injection' in threat_types
        assert 'cross_site_scripting' in threat_types
        assert 'hardcoded_secrets' in threat_types
    
    def test_ci_cd_security_gate(self):
        """Test security gate for CI/CD pipeline."""
        from agentic_ai.agents.security import SecurityAgent, SeverityLevel
        
        agent = SecurityAgent()
        
        # Simulate code change
        new_code = """
def authenticate(token):
    query = "SELECT * FROM users WHERE token = '" + token + "'"
    return db.execute(query)
"""
        
        findings = agent.scan_code(new_code, "new_feature.py")
        
        # Security gate logic
        critical_findings = [f for f in findings if f.severity == SeverityLevel.CRITICAL]
        high_findings = [f for f in findings if f.severity == SeverityLevel.HIGH]
        
        # Gate should fail on critical/high findings
        gate_passed = len(critical_findings) == 0 and len(high_findings) == 0
        
        assert gate_passed is False
        assert len(critical_findings) >= 1
        
        # Generate gate report
        gate_report = {
            'passed': gate_passed,
            'critical_count': len(critical_findings),
            'high_count': len(high_findings),
            'total_findings': len(findings),
            'blocking_issues': [f.title for f in critical_findings + high_findings],
        }
        
        assert gate_report['passed'] is False
        assert len(gate_report['blocking_issues']) > 0
    
    def test_secrets_rotation_workflow(self):
        """Test automated secrets rotation workflow."""
        from agentic_ai.agents.security import SecurityAgent
        
        agent = SecurityAgent()
        
        # Register secrets
        secrets = [
            ("API_KEY_1", "api_key", 30),
            ("DB_PASSWORD", "password", 60),
            ("JWT_SECRET", "token", 90),
        ]
        
        rotations = []
        for name, secret_type, days in secrets:
            rotation = agent.register_secret(name, secret_type, rotation_days=days)
            rotations.append(rotation)
        
        # Simulate time passing (30 days)
        import datetime
        for rotation in rotations:
            if rotation.secret_name == "API_KEY_1":
                rotation.last_rotated = datetime.datetime.utcnow() - datetime.timedelta(days=31)
                rotation.next_rotation = datetime.datetime.utcnow() - datetime.timedelta(days=1)
        
        # Check for rotations needed
        due = agent.get_secrets_due_for_rotation(days_ahead=7)
        
        assert len(due) >= 1
        assert any(r.secret_name == "API_KEY_1" for r in due)
        
        # Perform rotation
        for rotation in due:
            if rotation.secret_name == "API_KEY_1":
                new_secret = agent.generate_secure_secret("api_key", length=32)
                agent.rotate_secret(rotation.rotation_id, new_secret)
        
        # Verify rotation completed
        due_after = agent.get_secrets_due_for_rotation(days_ahead=7)
        assert not any(r.secret_name == "API_KEY_1" for r in due_after)


class TestSecurityIncidentWorkflows:
    """Test security incident response workflows."""
    
    def test_brute_force_detection_and_response(self):
        """Test automated brute force detection and response."""
        from agentic_ai.agents.security import SecurityAgent, ThreatType
        
        agent = SecurityAgent()
        
        # Simulate brute force attack
        for i in range(10):
            agent.log_access(
                user_id="victim",
                resource="/api/login",
                action="login",
                source_ip="192.168.1.100",
                success=False,
            )
        
        # Verify incident was created
        incidents = agent.get_incidents(threat_type=ThreatType.BRUTE_FORCE)
        assert len(incidents) >= 1
        
        incident = incidents[0]
        assert incident.severity.value == 'high'
        assert len(incident.response_actions) > 0
        
        # Verify auto-response actions
        actions = incident.response_actions
        assert any('block' in a.lower() or 'password' in a.lower() for a in actions)
    
    def test_anomaly_detection_workflow(self):
        """Test anomaly detection and alerting workflow."""
        from agentic_ai.agents.security import SecurityAgent
        
        agent = SecurityAgent()
        
        # Simulate normal activity
        for i in range(5):
            agent.log_access(
                user_id="normal_user",
                resource="/api/data",
                action="read",
                source_ip="10.0.0.1",
                success=True,
            )
        
        # Simulate suspicious activity (many failures)
        for i in range(20):
            agent.log_access(
                user_id="suspicious_user",
                resource="/api/login",
                action="login",
                source_ip="10.0.0.50",
                success=False,
            )
        
        # Detect anomalies
        anomalies = agent.detect_anomalies(window_hours=24)
        
        assert len(anomalies) >= 1
        
        failure_anomalies = [a for a in anomalies if a['type'] == 'high_failure_rate']
        assert len(failure_anomalies) >= 1
        assert failure_anomalies[0]['user_id'] == 'suspicious_user'
    
    def test_incident_lifecycle_management(self):
        """Test complete incident lifecycle management."""
        from agentic_ai.agents.security import SecurityAgent, SeverityLevel, ThreatType
        
        agent = SecurityAgent()
        
        # Create incident
        incident = agent.create_incident(
            title="Data Exfiltration Attempt",
            description="Unusual data export detected",
            severity=SeverityLevel.CRITICAL,
            threat_type=ThreatType.SUSPICIOUS_ACTIVITY,
            user_id="insider_threat",
        )
        
        # Lifecycle: detected -> investigating -> contained -> resolved
        assert incident.status == "investigating"  # Auto-responded
        
        # Security team investigates
        agent.update_incident_status(
            incident.incident_id,
            "contained",
            response_actions=["Disabled user account", "Preserved logs"],
        )
        
        incident = agent.incidents[incident.incident_id]
        assert incident.status == "contained"
        
        # Final resolution
        agent.update_incident_status(
            incident.incident_id,
            "resolved",
            resolved_by="security-team",
            response_actions=["Terminated user", "Updated policies"],
        )
        
        incident = agent.incidents[incident.incident_id]
        assert incident.status == "resolved"
        assert incident.resolved_by == "security-team"
        assert incident.resolved_at is not None


class TestSecurityReportingWorkflow:
    """Test security reporting and compliance workflows."""
    
    def test_compliance_report_generation(self):
        """Test generating compliance reports."""
        from agentic_ai.agents.security import SecurityAgent, SeverityLevel, ThreatType
        
        agent = SecurityAgent()
        
        # Create security events
        agent.create_incident(
            title="Test Incident",
            description="Test",
            severity=SeverityLevel.HIGH,
            threat_type=ThreatType.BRUTE_FORCE,
        )
        
        agent.scan_code("query = 'SELECT' + input", "test.py")
        
        # Generate compliance report
        report = agent.generate_security_report(period_days=30)
        
        # Verify report structure
        required_sections = ['generated_at', 'period_days', 'findings', 'incidents', 'secrets', 'policies']
        for section in required_sections:
            assert section in report
        
        # Verify findings data
        assert 'total' in report['findings']
        assert 'by_severity' in report['findings']
        assert 'open' in report['findings']
        
        # Verify incidents data
        assert 'total' in report['incidents']
        assert 'by_status' in report['incidents']
        assert 'critical' in report['incidents']
    
    def test_security_metrics_dashboard(self):
        """Test generating metrics for security dashboard."""
        from agentic_ai.agents.security import SecurityAgent, ThreatType
        
        agent = SecurityAgent()
        
        # Create various security events
        threat_types = list(ThreatType)
        severities = ['critical', 'high', 'medium', 'low', 'info']
        
        for i in range(5):
            agent.create_incident(
                title=f"Incident {i}",
                description="Test",
                severity=severities[i % 5],
                threat_type=threat_types[i % len(threat_types)],
            )
        
        # Get state for dashboard
        state = agent.get_state()
        
        assert 'agent_id' in state
        assert 'findings_count' in state
        assert 'incidents_count' in state
        assert 'open_critical_incidents' in state
        
        # Dashboard metrics
        metrics = {
            'total_incidents': state['incidents_count'],
            'critical_open': state['open_critical_incidents'],
            'secrets_tracked': state['secrets_tracked'],
            'policies_enabled': state['policies_count'],
        }
        
        assert metrics['total_incidents'] >= 5


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
