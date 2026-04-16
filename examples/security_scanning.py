#!/usr/bin/env python3
"""
SecurityAgent Examples
======================

Demonstrates vulnerability scanning, incident response,
secrets management, and security policy enforcement.
"""

from agentic_ai.agents.security import (
    SecurityAgent,
    SeverityLevel,
    ThreatType,
)


def example_vulnerability_scanning():
    """Example: Scan code for vulnerabilities."""
    print("=" * 70)
    print("Example 1: Vulnerability Scanning")
    print("=" * 70)
    print()
    
    agent = SecurityAgent()
    
    # Vulnerable code example
    vulnerable_code = """
def login(username, password):
    # SQL Injection vulnerability
    query = "SELECT * FROM users WHERE username = '" + username + "' OR 1=1--"
    db.execute(query)
    
def render_content(user_input):
    # XSS vulnerability
    return "<html><body><script>" + user_input + "</script></body></html>"

def read_file(filename):
    # Path traversal vulnerability
    with open("/var/data/" + filename, "r") as f:
        return f.read()

# Hardcoded credentials
AWS_KEY = "AKIAIOSFODNN7EXAMPLE"
API_KEY = "sk_live_abcdef1234567890"
password = "admin123"
"""
    
    print("Scanning vulnerable code...")
    findings = agent.scan_code(vulnerable_code, "vulnerable.py")
    
    print(f"\nFound {len(findings)} security issues:\n")
    
    # Group by severity
    by_severity = {}
    for finding in findings:
        sev = finding.severity.value
        if sev not in by_severity:
            by_severity[sev] = []
        by_severity[sev].append(finding)
    
    for severity in ['critical', 'high', 'medium', 'low']:
        if severity in by_severity:
            print(f"\n{severity.upper()} ({len(by_severity[severity])} issues):")
            for finding in by_severity[severity][:3]:  # Show first 3
                print(f"  {finding.title}")
                print(f"     Location: {finding.location}:{finding.line_number}")
                print(f"     Type: {finding.threat_type.value}")
                print(f"     CWE: {finding.cwe_id}")
                print(f"     Fix: {finding.recommendation}")
                print()
    
    print(f"\nTotal recommendations: {len(findings)} fixes suggested")


def example_incident_response():
    """Example: Security incident detection and response."""
    print("\n" + "=" * 70)
    print("Example 2: Incident Response")
    print("=" * 70)
    print()
    
    agent = SecurityAgent()
    
    # Simulate brute force attack
    print("Simulating brute force attack...")
    
    for i in range(6):
        agent.log_access(
            user_id="attacker",
            resource="/api/login",
            action="login",
            source_ip="192.168.1.100",
            success=False,
            metadata={'user_agent': 'Mozilla/5.0'},
        )
    
    # Check for incidents
    incidents = agent.get_incidents()
    
    if incidents:
        print(f"\nDetected {len(incidents)} security incident(s):\n")
        for incident in incidents:
            print(f"  Incident ID: {incident.incident_id}")
            print(f"  Title: {incident.title}")
            print(f"  Severity: {incident.severity.value}")
            print(f"  Status: {incident.status}")
            print(f"  Threat Type: {incident.threat_type.value}")
            print(f"  Source IP: {incident.source_ip}")
            print(f"  Target: {incident.target_resource}")
            print(f"  Auto-Response Actions:")
            for action in incident.response_actions:
                print(f"    - {action}")
            print()
    
    # Simulate resolving an incident
    if incidents:
        print("Responding to incident...")
        agent.update_incident_status(
            incidents[0].incident_id,
            "contained",
            response_actions=["Blocked IP at firewall", "Notified security team"],
        )
        print(f"  Incident status updated to 'contained'")


def example_secrets_management():
    """Example: Secrets rotation tracking."""
    print("\n" + "=" * 70)
    print("Example 3: Secrets Management")
    print("=" * 70)
    print()
    
    agent = SecurityAgent()
    
    # Register secrets for rotation tracking
    print("Registering secrets for rotation tracking...")
    
    secrets = [
        ("STRIPE_API_KEY", "api_key", 90),
        ("AWS_ACCESS_KEY", "api_key", 90),
        ("DATABASE_PASSWORD", "password", 60),
        ("JWT_SECRET", "token", 180),
    ]
    
    rotations = []
    for name, secret_type, days in secrets:
        rotation = agent.register_secret(name, secret_type, rotation_days=days)
        rotations.append(rotation)
        print(f"  - {name} - Next rotation: {rotation.next_rotation.strftime('%Y-%m-%d')}")
    
    # Generate secure secrets
    print("\nGenerating secure secrets:")
    new_api_key = agent.generate_secure_secret("api_key", length=32)
    new_password = agent.generate_secure_secret("password", length=16)
    
    print(f"  API Key: {new_api_key[:8]}...{new_api_key[-4:]}")
    print(f"  Password: {new_password[:8]}...{new_password[-4:]}")
    
    # Check for secrets due for rotation
    print("\nChecking for secrets due for rotation...")
    due = agent.get_secrets_due_for_rotation(days_ahead=7)
    if due:
        print(f"  {len(due)} secret(s) due for rotation")
        for rotation in due:
            print(f"    - {rotation.secret_name}")
    else:
        print("  No secrets due for rotation in the next 7 days")


def example_policy_enforcement():
    """Example: Security policy enforcement."""
    print("\n" + "=" * 70)
    print("Example 4: Policy Enforcement")
    print("=" * 70)
    print()
    
    agent = SecurityAgent()
    
    # Password validation
    print("Password Policy Enforcement:\n")
    
    test_passwords = [
        "weak",
        "password123",
        "NoSpecial1",
        "nouppercase1!",
        "SecureP@ssw0rd123!",
    ]
    
    for password in test_passwords:
        is_valid, violations = agent.validate_password(password)
        status = "PASS" if is_valid else "FAIL"
        print(f"  [{status}] '{password}'")
        if violations:
            for v in violations:
                print(f"      - {v}")
    
    # Rate limiting
    print("\nRate Limiting Check:\n")
    
    # Simulate login attempts
    for i in range(6):
        allowed, remaining = agent.check_rate_limit("user123", "login")
        status = "OK" if allowed else "BLOCKED"
        print(f"  Attempt {i+1}: [{status}] Allowed={allowed}, Remaining={remaining}")
    
    # Get active policies
    print("\nActive Security Policies:\n")
    for policy_id, policy in agent.policies.items():
        status = "ON" if policy.enabled else "OFF"
        print(f"  [{status}] {policy.name}")
        print(f"      Enforcement: {policy.enforcement_level}")
        print(f"      Rules: {len(policy.rules)}")


def example_security_reporting():
    """Example: Generate security report."""
    print("\n" + "=" * 70)
    print("Example 5: Security Reporting")
    print("=" * 70)
    print()
    
    agent = SecurityAgent()
    
    # Create some security events
    agent.create_incident(
        title="SQL Injection Attempt",
        description="Detected in /api/users endpoint",
        severity=SeverityLevel.CRITICAL,
        threat_type=ThreatType.SQL_INJECTION,
        source_ip="10.0.0.50",
    )
    
    agent.scan_code("query = 'SELECT * FROM x WHERE a=' + input", "test.py")
    
    # Generate report
    print("Generating security report...\n")
    report = agent.generate_security_report(period_days=30)
    
    print(f"Report Generated: {report['generated_at']}")
    print(f"Period: {report['period_days']} days\n")
    
    print("Findings Summary:")
    print(f"  Total: {report['findings']['total']}")
    print(f"  Open: {report['findings']['open']}")
    if report['findings']['by_severity']:
        print(f"  By Severity: {report['findings']['by_severity']}")
    
    print("\nIncidents Summary:")
    print(f"  Total: {report['incidents']['total']}")
    print(f"  Critical: {report['incidents']['critical']}")
    print(f"  By Status: {report['incidents']['by_status']}")
    
    print("\nSecrets Summary:")
    print(f"  Tracked: {report['secrets']['total_tracked']}")
    print(f"  Due for Rotation: {report['secrets']['due_for_rotation']}")
    
    print("\nCompliance:")
    print(f"  Policies Enabled: {report['policies']['enabled']}/{report['policies']['total']}")
    
    print("\nAnomalies Detected:", report['anomalies_detected'])


def example_directory_scan():
    """Example: Scan a directory for vulnerabilities."""
    print("\n" + "=" * 70)
    print("Example 6: Directory Scanning")
    print("=" * 70)
    print()
    
    agent = SecurityAgent()
    
    print("Scanning current directory for vulnerabilities...")
    print("(This may take a moment)\n")
    
    # Scan current directory (excluding venv, node_modules, etc.)
    findings = agent.scan_directory(".", extensions=['.py'])
    
    if findings:
        print(f"Found {len(findings)} potential issues:\n")
        
        # Group by file
        by_file = {}
        for finding in findings:
            loc = finding.location
            if loc not in by_file:
                by_file[loc] = []
            by_file[loc].append(finding)
        
        for file_path, file_findings in list(by_file.items())[:5]:  # Show first 5 files
            print(f"  {file_path} ({len(file_findings)} issues)")
            for finding in file_findings[:2]:  # Show first 2 per file
                print(f"      - Line {finding.line_number}: {finding.title}")
            if len(file_findings) > 2:
                print(f"      ... and {len(file_findings) - 2} more")
            print()
    else:
        print("No vulnerabilities detected in scanned files!")


def main():
    """Run all security examples."""
    print("\n" + "=" * 70)
    print("SecurityAgent - Comprehensive Examples")
    print("=" * 70)
    
    example_vulnerability_scanning()
    example_incident_response()
    example_secrets_management()
    example_policy_enforcement()
    example_security_reporting()
    example_directory_scan()
    
    print("\n" + "=" * 70)
    print("All examples complete!")
    print("=" * 70)
    print()
    print("Next steps:")
    print("  - Integrate SecurityAgent into your CI/CD pipeline")
    print("  - Set up automated secret rotation")
    print("  - Configure security policies for your organization")
    print("  - Enable real-time monitoring and alerting")
    print()


if __name__ == "__main__":
    main()
