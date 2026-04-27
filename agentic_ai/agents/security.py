"""
SecurityAgent - Security Monitoring & Incident Response
========================================================

Provides security scanning, vulnerability assessment, incident response,
secrets management, and security policy enforcement.
"""

import hashlib
import logging
import os
import re
import secrets
import string
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from typing import Any, Dict, List, Optional, Tuple


logger = logging.getLogger(__name__)


class SeverityLevel(Enum):
    """Security issue severity levels."""
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    INFO = "info"


class ThreatType(Enum):
    """Types of security threats."""
    # Injection Attacks
    SQL_INJECTION = "sql_injection"
    NOSQL_INJECTION = "nosql_injection"
    LDAP_INJECTION = "ldap_injection"
    XSS = "cross_site_scripting"
    XXE = "xml_external_entity"
    COMMAND_INJECTION = "command_injection"
    CODE_INJECTION = "code_injection"

    # Protocol/Network
    CSRF = "csrf"
    SSRF = "ssrf"
    PATH_TRAVERSAL = "path_traversal"
    UNVALIDATED_REDIRECT = "unvalidated_redirect"

    # Cryptography
    WEAK_CRYPTO = "weak_cryptography"
    INSECURE_RANDOM = "insecure_random"
    HARDCODED_SECRETS = "hardcoded_secrets"

    # Authentication/Session
    BRUTE_FORCE = "brute_force"
    SESSION_HIJACK = "session_hijack"
    SESSION_FIXATION = "session_fixation"
    PRIVILEGE_ESCALATION = "privilege_escalation"

    # Data/Deserialization
    INSECURE_DESERIALIZATION = "insecure_deserialization"
    SENSITIVE_DATA_EXPOSURE = "sensitive_data_exposure"

    # Other
    MALWARE = "malware"
    SUSPICIOUS_ACTIVITY = "suspicious_activity"
    DEBUG_MODE_ENABLED = "debug_mode_enabled"
    SECURITY_MISCONFIGURATION = "security_misconfiguration"


@dataclass
class SecurityFinding:
    """A security vulnerability or issue finding."""
    finding_id: str
    threat_type: ThreatType
    severity: SeverityLevel
    title: str
    description: str
    location: str  # File path, URL, or component
    line_number: Optional[int] = None
    code_snippet: Optional[str] = None
    recommendation: str = ""
    cwe_id: Optional[str] = None  # Common Weakness Enumeration
    cvss_score: Optional[float] = None
    created_at: datetime = field(default_factory=datetime.utcnow)
    status: str = "open"  # open, investigating, mitigated, false_positive
    assigned_to: Optional[str] = None


@dataclass
class SecurityIncident:
    """A security incident requiring response."""
    incident_id: str
    title: str
    description: str
    severity: SeverityLevel
    threat_type: ThreatType
    source_ip: Optional[str] = None
    target_resource: Optional[str] = None
    user_id: Optional[str] = None
    detected_at: datetime = field(default_factory=datetime.utcnow)
    status: str = "detected"  # detected, investigating, contained, resolved
    response_actions: List[str] = field(default_factory=list)
    evidence: List[str] = field(default_factory=list)
    resolved_at: Optional[datetime] = None
    resolved_by: Optional[str] = None


@dataclass
class SecretRotation:
    """Secret rotation tracking."""
    rotation_id: str
    secret_name: str
    secret_type: str  # api_key, password, token, certificate
    last_rotated: datetime
    next_rotation: datetime
    rotation_count: int = 0
    status: str = "active"  # active, expired, revoked


@dataclass
class SecurityPolicy:
    """Security policy definition."""
    policy_id: str
    name: str
    description: str
    rules: List[Dict[str, Any]]
    enabled: bool = True
    enforcement_level: str = "audit"  # audit, warn, block


class SimpleStateStore:
    """Simple in-memory state store for when full infrastructure is not available."""

    def __init__(self):
        self._data = {}

    def get(self, key: str, default: Any = None) -> Any:
        return self._data.get(key, default)

    def set(self, key: str, value: Any):
        self._data[key] = value

    def delete(self, key: str):
        if key in self._data:
            del self._data[key]


class SecurityAgent:
    """
    Security Agent for vulnerability scanning, incident response,
    and security policy enforcement.
    """

    def __init__(self, agent_id: str = "security-agent", state_store: Optional[Any] = None):
        self.agent_id = agent_id
        self.state_store = state_store or SimpleStateStore()
        self.findings: Dict[str, SecurityFinding] = {}
        self.incidents: Dict[str, SecurityIncident] = {}
        self.secret_rotations: Dict[str, SecretRotation] = {}
        self.policies: Dict[str, SecurityPolicy] = {}
        self.access_logs: List[Dict[str, Any]] = []

        # Security patterns for scanning
        self._init_security_patterns()

        # Load persisted state
        self._load_state()

    def _init_security_patterns(self):
        """Initialize security scanning patterns."""
        # Hardcoded secrets patterns
        self.secret_patterns = {
            'aws_key': re.compile(r'AKIA[0-9A-Z]{16}'),
            'aws_secret': re.compile(r'[A-Za-z0-9/+=]{40}'),
            'github_token': re.compile(r'ghp_[A-Za-z0-9]{36}'),
            'gitlab_token': re.compile(r'glpat-[A-Za-z0-9\-]{20,}'),
            'generic_api_key': re.compile(r'(?i)(api[_-]?key|apikey)\s*[:=]\s*["\']?[A-Za-z0-9]{16,}'),
            'password_assignment': re.compile(r'(?i)(password|passwd|pwd)\s*[:=]\s*["\']?[^"\'\s]{4,}'),
            'private_key': re.compile(r'-----BEGIN (RSA |EC |DSA )?PRIVATE KEY-----'),
            'jwt_secret': re.compile(r'(?i)(jwt[_-]?secret|jwt[_-]?key)\s*[:=]\s*["\']?[^"\'\s]{8,}'),
        }

        # SQL injection patterns
        self.sql_injection_patterns = [
            re.compile(r'(?i)(\bSELECT\b.*\bFROM\b.*\bWHERE\b.*=.*\bOR\b)', re.IGNORECASE),
            re.compile(r'(?i)(\bUNION\b.*\bSELECT\b)', re.IGNORECASE),
            re.compile(r'(?i)(\bDROP\b.*\bTABLE\b)', re.IGNORECASE),
            re.compile(r'--\s*$'),
            re.compile(r';\s*(DROP|DELETE|UPDATE|INSERT)', re.IGNORECASE),
            # String concatenation in SQL queries
            re.compile(r"(?i)(SELECT|INSERT|UPDATE|DELETE|FROM|WHERE).*\+", re.IGNORECASE),
            re.compile(r"\+\s*\w+"),
        ]

        # XSS patterns
        self.xss_patterns = [
            re.compile(r'<script[^>]*>', re.IGNORECASE),
            re.compile(r'javascript:', re.IGNORECASE),
            re.compile(r'on(load|error|click|mouse|focus|blur)\s*=', re.IGNORECASE),
            re.compile(r'<iframe[^>]*>', re.IGNORECASE),
            # String concatenation in HTML context (potential XSS)
            re.compile(r'["\'][^"\']*<[a-z]+>[^"\']*["\']\s*\+\s*\w+', re.IGNORECASE),
            re.compile(r'\+\s*["\'][^"\']*</[a-z]+>["\']', re.IGNORECASE),
        ]

        # Path traversal patterns
        self.path_traversal_patterns = [
            re.compile(r'\.\./'),
            re.compile(r'\.\.\\'),
            re.compile(r'%2e%2e%2f', re.IGNORECASE),
            re.compile(r'%2e%2e/', re.IGNORECASE),
            # String concatenation with paths
            re.compile(r'["\'][^"\']*/[a-z]+["\']\s*\+\s*\w+', re.IGNORECASE),
        ]

        # Command injection patterns
        self.command_injection_patterns = [
            re.compile(r'[;&|`$]'),
            re.compile(r'\$\([^)]+\)'),
            re.compile(r'`[^`]+`'),
        ]

        # Initialize default policies
        self._init_default_policies()

    def _init_default_policies(self):
        """Initialize default security policies."""
        self.policies = {
            'password-complexity': SecurityPolicy(
                policy_id='password-complexity',
                name='Password Complexity Policy',
                description='Enforce strong password requirements',
                rules=[
                    {'name': 'min_length', 'value': 12},
                    {'name': 'require_uppercase', 'value': True},
                    {'name': 'require_lowercase', 'value': True},
                    {'name': 'require_numbers', 'value': True},
                    {'name': 'require_special', 'value': True},
                ],
                enabled=True,
                enforcement_level='block',
            ),
            'session-timeout': SecurityPolicy(
                policy_id='session-timeout',
                name='Session Timeout Policy',
                description='Automatic session timeout after inactivity',
                rules=[
                    {'name': 'timeout_minutes', 'value': 30},
                    {'name': 'absolute_timeout_hours', 'value': 8},
                ],
                enabled=True,
                enforcement_level='block',
            ),
            'rate-limiting': SecurityPolicy(
                policy_id='rate-limiting',
                name='Rate Limiting Policy',
                description='Prevent brute force attacks',
                rules=[
                    {'name': 'max_attempts', 'value': 5},
                    {'name': 'window_minutes', 'value': 15},
                    {'name': 'lockout_duration_hours', 'value': 1},
                ],
                enabled=True,
                enforcement_level='block',
            ),
            'secret-rotation': SecurityPolicy(
                policy_id='secret-rotation',
                name='Secret Rotation Policy',
                description='Regular rotation of API keys and secrets',
                rules=[
                    {'name': 'rotation_days', 'value': 90},
                    {'name': 'notify_days_before', 'value': 7},
                ],
                enabled=True,
                enforcement_level='warn',
            ),
        }

    def _load_state(self):
        """Load persisted security state."""
        try:
            state = self.state_store.get(f"agent:{self.agent_id}:state")
            if state:
                # Restore findings, incidents, etc.
                logger.info("Security agent state loaded")
        except Exception as e:
            logger.debug(f"Could not load security state: {e}")

    def _save_state(self):
        """Persist security state."""
        try:
            state = {
                'findings_count': len(self.findings),
                'incidents_count': len(self.incidents),
                'last_scan': datetime.utcnow().isoformat(),
            }
            self.state_store.set(f"agent:{self.agent_id}:state", state)
        except Exception as e:
            logger.error(f"Could not save security state: {e}")

    # ============================================
    # Vulnerability Scanning
    # ============================================

    def scan_code(self, code: str, file_path: str = "unknown") -> List[SecurityFinding]:
        """
        Scan code for security vulnerabilities.

        Args:
            code: Source code to scan
            file_path: File path for context

        Returns:
            List of security findings
        """
        findings = []
        lines = code.split('\n')

        # Check for hardcoded secrets
        for line_num, line in enumerate(lines, 1):
            for secret_type, pattern in self.secret_patterns.items():
                if pattern.search(line):
                    finding = SecurityFinding(
                        finding_id=self._generate_id("finding"),
                        threat_type=ThreatType.HARDCODED_SECRETS,
                        severity=SeverityLevel.HIGH,
                        title=f"Hardcoded {secret_type.replace('_', ' ').title()} detected",
                        description=f"Potential {secret_type} found in source code",
                        location=file_path,
                        line_number=line_num,
                        code_snippet=line.strip()[:100],
                        recommendation="Use environment variables or a secrets manager",
                        cwe_id="CWE-798",
                    )
                    findings.append(finding)
                    self.findings[finding.finding_id] = finding

        # Check for SQL injection vulnerabilities
        for line_num, line in enumerate(lines, 1):
            for pattern in self.sql_injection_patterns:
                if pattern.search(line):
                    finding = SecurityFinding(
                        finding_id=self._generate_id("finding"),
                        threat_type=ThreatType.SQL_INJECTION,
                        severity=SeverityLevel.CRITICAL,
                        title="Potential SQL Injection vulnerability",
                        description="Unsanitized SQL query detected",
                        location=file_path,
                        line_number=line_num,
                        code_snippet=line.strip()[:100],
                        recommendation="Use parameterized queries or ORM",
                        cwe_id="CWE-89",
                        cvss_score=9.8,
                    )
                    findings.append(finding)
                    self.findings[finding.finding_id] = finding

        # Check for XSS vulnerabilities
        for line_num, line in enumerate(lines, 1):
            for pattern in self.xss_patterns:
                if pattern.search(line):
                    finding = SecurityFinding(
                        finding_id=self._generate_id("finding"),
                        threat_type=ThreatType.XSS,
                        severity=SeverityLevel.HIGH,
                        title="Potential XSS vulnerability",
                        description="Unsanitized user input in HTML context",
                        location=file_path,
                        line_number=line_num,
                        code_snippet=line.strip()[:100],
                        recommendation="Escape output and validate input",
                        cwe_id="CWE-79",
                        cvss_score=7.5,
                    )
                    findings.append(finding)
                    self.findings[finding.finding_id] = finding

        # Check for path traversal
        for line_num, line in enumerate(lines, 1):
            for pattern in self.path_traversal_patterns:
                if pattern.search(line):
                    finding = SecurityFinding(
                        finding_id=self._generate_id("finding"),
                        threat_type=ThreatType.PATH_TRAVERSAL,
                        severity=SeverityLevel.MEDIUM,
                        title="Potential path traversal vulnerability",
                        description="Unsanitized file path detected",
                        location=file_path,
                        line_number=line_num,
                        code_snippet=line.strip()[:100],
                        recommendation="Validate and sanitize file paths",
                        cwe_id="CWE-22",
                    )
                    findings.append(finding)
                    self.findings[finding.finding_id] = finding

        self._save_state()
        return findings

    def scan_file(self, file_path: str) -> List[SecurityFinding]:
        """Scan a file for security vulnerabilities."""
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                code = f.read()
            return self.scan_code(code, file_path)
        except Exception as e:
            logger.error(f"Error scanning file {file_path}: {e}")
            return []

    def scan_directory(self, directory_path: str, extensions: Optional[List[str]] = None) -> List[SecurityFinding]:
        """
        Scan a directory recursively for security vulnerabilities.

        Args:
            directory_path: Path to directory
            extensions: File extensions to scan (default: ['.py', '.js', '.ts', '.java', '.go'])

        Returns:
            List of all findings
        """
        if extensions is None:
            extensions = ['.py', '.js', '.ts', '.java', '.go', '.rb', '.php', '.sh']

        all_findings = []

        for root, dirs, files in os.walk(directory_path):
            # Skip hidden and virtual environments
            dirs[:] = [d for d in dirs if not d.startswith('.') and d not in ['venv', 'node_modules', '__pycache__']]

            for file in files:
                if any(file.endswith(ext) for ext in extensions):
                    file_path = os.path.join(root, file)
                    findings = self.scan_file(file_path)
                    all_findings.extend(findings)

        logger.info(f"Scanned {directory_path}: found {len(all_findings)} issues")
        return all_findings

    # ============================================
    # Incident Response
    # ============================================

    def create_incident(
        self,
        title: str,
        description: str,
        severity: SeverityLevel,
        threat_type: ThreatType,
        source_ip: Optional[str] = None,
        target_resource: Optional[str] = None,
        user_id: Optional[str] = None,
    ) -> SecurityIncident:
        """Create a new security incident."""
        incident = SecurityIncident(
            incident_id=self._generate_id("incident"),
            title=title,
            description=description,
            severity=severity,
            threat_type=threat_type,
            source_ip=source_ip,
            target_resource=target_resource,
            user_id=user_id,
        )

        self.incidents[incident.incident_id] = incident
        logger.warning(f"Security incident created: {incident.incident_id} - {title}")

        # Auto-respond based on severity
        if severity in [SeverityLevel.CRITICAL, SeverityLevel.HIGH]:
            self._auto_respond_incident(incident)

        self._save_state()
        return incident

    def _auto_respond_incident(self, incident: SecurityIncident):
        """Automated incident response actions."""
        actions = []

        if incident.threat_type == ThreatType.BRUTE_FORCE:
            actions.append(f"Block IP {incident.source_ip} at firewall")
            actions.append("Force password reset for affected user")
            actions.append("Enable account lockout")

        elif incident.threat_type == ThreatType.SQL_INJECTION:
            actions.append("Block suspicious requests at WAF")
            actions.append("Review database logs for data exfiltration")
            actions.append("Patch vulnerable endpoint")

        elif incident.threat_type == ThreatType.SESSION_HIJACK:
            actions.append("Invalidate all sessions for user")
            actions.append("Force re-authentication")
            actions.append("Review session logs")

        elif incident.severity == SeverityLevel.CRITICAL:
            actions.append("Alert security team immediately")
            actions.append("Enable enhanced logging")
            actions.append("Consider temporary service isolation")

        incident.response_actions = actions
        incident.status = "investigating"

        logger.info(f"Auto-response for incident {incident.incident_id}: {len(actions)} actions")

    def update_incident_status(
        self,
        incident_id: str,
        status: str,
        resolved_by: Optional[str] = None,
        response_actions: Optional[List[str]] = None,
    ) -> Optional[SecurityIncident]:
        """Update incident status."""
        if incident_id not in self.incidents:
            return None

        incident = self.incidents[incident_id]
        incident.status = status

        if response_actions:
            incident.response_actions.extend(response_actions)

        if status == "resolved":
            incident.resolved_at = datetime.utcnow()
            incident.resolved_by = resolved_by

        self._save_state()
        return incident

    def get_incidents(
        self,
        status: Optional[str] = None,
        severity: Optional[SeverityLevel] = None,
        threat_type: Optional[ThreatType] = None,
        limit: int = 50,
    ) -> List[SecurityIncident]:
        """Get incidents with optional filtering."""
        incidents = list(self.incidents.values())

        if status:
            incidents = [i for i in incidents if i.status == status]

        if severity:
            incidents = [i for i in incidents if i.severity == severity]

        if threat_type:
            incidents = [i for i in incidents if i.threat_type == threat_type]

        # Sort by detection time (newest first)
        incidents.sort(key=lambda x: x.detected_at, reverse=True)

        return incidents[:limit]

    # ============================================
    # Secrets Management
    # ============================================

    def register_secret(
        self,
        secret_name: str,
        secret_type: str,
        rotation_days: int = 90,
    ) -> SecretRotation:
        """Register a secret for rotation tracking."""
        now = datetime.utcnow()
        rotation = SecretRotation(
            rotation_id=self._generate_id("rotation"),
            secret_name=secret_name,
            secret_type=secret_type,
            last_rotated=now,
            next_rotation=now + timedelta(days=rotation_days),
        )

        self.secret_rotations[rotation.rotation_id] = rotation
        logger.info(f"Registered secret for rotation: {secret_name}")
        return rotation

    def rotate_secret(self, rotation_id: str, new_secret_value: str) -> bool:
        """
        Rotate a secret.

        Args:
            rotation_id: Secret rotation record ID
            new_secret_value: New secret value (stored securely in production)

        Returns:
            True if rotation successful
        """
        if rotation_id not in self.secret_rotations:
            return False

        rotation = self.secret_rotations[rotation_id]
        rotation.last_rotated = datetime.utcnow()
        rotation.next_rotation = rotation.last_rotated + timedelta(days=90)
        rotation.rotation_count += 1

        # In production, update the actual secret in secrets manager
        logger.info(f"Rotated secret: {rotation.secret_name} (count: {rotation.rotation_count})")

        self._save_state()
        return True

    def get_secrets_due_for_rotation(self, days_ahead: int = 7) -> List[SecretRotation]:
        """Get secrets due for rotation within specified days."""
        threshold = datetime.utcnow() + timedelta(days=days_ahead)
        due = []

        for rotation in self.secret_rotations.values():
            if rotation.status == "active" and rotation.next_rotation <= threshold:
                due.append(rotation)

        return due

    def generate_secure_secret(
        self,
        secret_type: str = "api_key",
        length: int = 32,
    ) -> str:
        """Generate a cryptographically secure secret."""
        if secret_type == "api_key":
            return secrets.token_urlsafe(length)
        elif secret_type == "password":
            alphabet = string.ascii_letters + string.digits + "!@#$%^&*"
            return ''.join(secrets.choice(alphabet) for _ in range(length))
        elif secret_type == "token":
            return secrets.token_hex(length)
        else:
            return secrets.token_urlsafe(length)

    # ============================================
    # Access Log Analysis
    # ============================================

    def log_access(
        self,
        user_id: str,
        resource: str,
        action: str,
        source_ip: str,
        success: bool,
        metadata: Optional[Dict[str, Any]] = None,
    ):
        """Log an access event for security analysis."""
        log_entry = {
            'timestamp': datetime.utcnow().isoformat(),
            'user_id': user_id,
            'resource': resource,
            'action': action,
            'source_ip': source_ip,
            'success': success,
            'metadata': metadata or {},
        }

        self.access_logs.append(log_entry)

        # Keep last 10000 entries in memory
        if len(self.access_logs) > 10000:
            self.access_logs = self.access_logs[-10000:]

        # Check for suspicious patterns
        self._analyze_access_pattern(log_entry)

    def _analyze_access_pattern(self, log_entry: Dict[str, Any]):
        """Analyze access patterns for anomalies."""
        # Check for brute force (multiple failed logins)
        if not log_entry['success'] and log_entry['action'] == 'login':
            recent_failures = [
                log for log in self.access_logs[-100:]
                if log['user_id'] == log_entry['user_id']
                and log['action'] == 'login'
                and not log['success']
            ]

            if len(recent_failures) >= 5:
                self.create_incident(
                    title=f"Brute force attempt detected",
                    description=f"Multiple failed login attempts for user {log_entry['user_id']}",
                    severity=SeverityLevel.HIGH,
                    threat_type=ThreatType.BRUTE_FORCE,
                    source_ip=log_entry['source_ip'],
                    user_id=log_entry['user_id'],
                )

    def detect_anomalies(self, window_hours: int = 24) -> List[Dict[str, Any]]:
        """Detect anomalies in access logs."""
        anomalies = []
        cutoff = datetime.utcnow() - timedelta(hours=window_hours)

        # Filter recent logs
        recent_logs = [
            log for log in self.access_logs
            if datetime.fromisoformat(log['timestamp']) > cutoff
        ]

        # Count failed logins per user
        failed_by_user = {}
        for log in recent_logs:
            if not log['success'] and log['action'] == 'login':
                user_id = log['user_id']
                failed_by_user[user_id] = failed_by_user.get(user_id, 0) + 1

        # Flag users with high failure rates
        for user_id, count in failed_by_user.items():
            if count >= 10:
                anomalies.append({
                    'type': 'high_failure_rate',
                    'user_id': user_id,
                    'failure_count': count,
                    'severity': 'high',
                })

        # Check for unusual access times
        for log in recent_logs:
            hour = datetime.fromisoformat(log['timestamp']).hour
            if hour in [2, 3, 4, 5]:  # 2-5 AM
                if log['action'] in ['admin_access', 'data_export', 'user_delete']:
                    anomalies.append({
                        'type': 'unusual_time_access',
                        'user_id': log['user_id'],
                        'action': log['action'],
                        'timestamp': log['timestamp'],
                        'severity': 'medium',
                    })

        return anomalies

    # ============================================
    # Policy Enforcement
    # ============================================

    def validate_password(self, password: str) -> Tuple[bool, List[str]]:
        """
        Validate password against security policy.

        Returns:
            Tuple of (is_valid, list_of_violations)
        """
        policy = self.policies.get('password-complexity')
        if not policy or not policy.enabled:
            return True, []

        violations = []
        rules = {rule['name']: rule['value'] for rule in policy.rules}

        # Check minimum length
        if len(password) < rules.get('min_length', 12):
            violations.append(f"Password must be at least {rules['min_length']} characters")

        # Check uppercase
        if rules.get('require_uppercase') and not any(c.isupper() for c in password):
            violations.append("Password must contain uppercase letters")

        # Check lowercase
        if rules.get('require_lowercase') and not any(c.islower() for c in password):
            violations.append("Password must contain lowercase letters")

        # Check numbers
        if rules.get('require_numbers') and not any(c.isdigit() for c in password):
            violations.append("Password must contain numbers")

        # Check special characters
        if rules.get('require_special') and not any(c in "!@#$%^&*()_+-=[]{}|;:,.<>?" for c in password):
            violations.append("Password must contain special characters")

        return len(violations) == 0, violations

    def check_rate_limit(
        self,
        identifier: str,
        action: str,
        window_minutes: int = 15,
    ) -> Tuple[bool, int]:
        """
        Check if action is within rate limits.

        Returns:
            Tuple of (is_allowed, remaining_attempts)
        """
        policy = self.policies.get('rate-limiting')
        if not policy or not policy.enabled:
            return True, 999

        rules = {rule['name']: rule['value'] for rule in policy.rules}
        max_attempts = rules.get('max_attempts', 5)

        # Count recent attempts
        cutoff = datetime.utcnow() - timedelta(minutes=window_minutes)
        recent_logs = [
            log for log in self.access_logs
            if datetime.fromisoformat(log['timestamp']) > cutoff
            and log['user_id'] == identifier
            and log['action'] == action
        ]

        attempts = len(recent_logs)
        remaining = max(0, max_attempts - attempts)

        return attempts < max_attempts, remaining

    def get_policy(self, policy_id: str) -> Optional[SecurityPolicy]:
        """Get a security policy by ID."""
        return self.policies.get(policy_id)

    def update_policy(self, policy_id: str, enabled: bool, enforcement_level: Optional[str] = None) -> bool:
        """Update a security policy."""
        if policy_id not in self.policies:
            return False

        policy = self.policies[policy_id]
        policy.enabled = enabled

        if enforcement_level:
            policy.enforcement_level = enforcement_level

        logger.info(f"Updated policy {policy_id}: enabled={enabled}")
        return True

    # ============================================
    # Reporting
    # ============================================

    def generate_security_report(self, period_days: int = 30) -> Dict[str, Any]:
        """Generate a security status report."""
        cutoff = datetime.utcnow() - timedelta(days=period_days)

        # Count findings by severity
        findings_by_severity = {}
        for finding in self.findings.values():
            if finding.created_at > cutoff:
                sev = finding.severity.value
                findings_by_severity[sev] = findings_by_severity.get(sev, 0) + 1

        # Count incidents by status
        incidents_by_status = {}
        for incident in self.incidents.values():
            if incident.detected_at > cutoff:
                status = incident.status
                incidents_by_status[status] = incidents_by_status.get(status, 0) + 1

        # Secrets due for rotation
        secrets_due = self.get_secrets_due_for_rotation()

        # Anomalies detected
        anomalies = self.detect_anomalies()

        report = {
            'generated_at': datetime.utcnow().isoformat(),
            'period_days': period_days,
            'findings': {
                'total': len([f for f in self.findings.values() if f.created_at > cutoff]),
                'by_severity': findings_by_severity,
                'open': len([f for f in self.findings.values() if f.status == 'open']),
            },
            'incidents': {
                'total': len([i for i in self.incidents.values() if i.detected_at > cutoff]),
                'by_status': incidents_by_status,
                'critical': len([i for i in self.incidents.values() if i.severity == SeverityLevel.CRITICAL]),
            },
            'secrets': {
                'total_tracked': len(self.secret_rotations),
                'due_for_rotation': len(secrets_due),
            },
            'anomalies_detected': len(anomalies),
            'policies': {
                'total': len(self.policies),
                'enabled': len([p for p in self.policies.values() if p.enabled]),
            },
        }

        return report

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
            'findings_count': len(self.findings),
            'incidents_count': len(self.incidents),
            'secrets_tracked': len(self.secret_rotations),
            'policies_count': len(self.policies),
            'access_logs_count': len(self.access_logs),
            'open_critical_incidents': len([
                i for i in self.incidents.values()
                if i.severity == SeverityLevel.CRITICAL and i.status != 'resolved'
            ]),
        }


# ============================================
# Agent Capabilities for Lead Agent
# ============================================

def get_capabilities() -> Dict[str, Any]:
    """Return agent capabilities for orchestration."""
    return {
        'agent_type': 'security',
        'version': '1.0.0',
        'capabilities': [
            'scan_code',
            'scan_file',
            'scan_directory',
            'create_incident',
            'update_incident_status',
            'get_incidents',
            'register_secret',
            'rotate_secret',
            'generate_secure_secret',
            'validate_password',
            'check_rate_limit',
            'log_access',
            'detect_anomalies',
            'generate_security_report',
        ],
        'threat_types': [t.value for t in ThreatType],
        'severity_levels': [s.value for s in SeverityLevel],
    }
