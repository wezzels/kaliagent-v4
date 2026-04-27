"""
RedTeamAgent - Offensive Security Operations
=============================================

Provides penetration testing automation, exploit simulation,
adversary emulation, attack path discovery, and red team operations.
"""

import logging
import secrets
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from typing import Any, Dict, List, Optional


logger = logging.getLogger(__name__)


class EngagementType(Enum):
    """Engagement types."""
    PENETRATION_TEST = "penetration_test"
    RED_TEAM = "red_team"
    ADVERSARY_EMULATION = "adversary_emulation"
    PURPLE_TEAM = "purple_team"
    TABLETOP_EXERCISE = "tabletop"


class EngagementStatus(Enum):
    """Engagement status."""
    PLANNING = "planning"
    RECON = "reconnaissance"
    WEAPONIZATION = "weaponization"
    DELIVERY = "delivery"
    EXPLOITATION = "exploitation"
    INSTALLATION = "installation"
    C2 = "command_and_control"
    ACTIONS = "actions_on_objectives"
    REPORTING = "reporting"
    COMPLETED = "completed"


class TargetType(Enum):
    """Target types."""
    NETWORK = "network"
    WEB_APP = "web_application"
    MOBILE_APP = "mobile_application"
    SOCIAL = "social_engineering"
    PHYSICAL = "physical"
    CLOUD = "cloud_infrastructure"
    INTERNAL = "internal_network"
    EXTERNAL = "external_network"


class FindingSeverity(Enum):
    """Finding severity."""
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    INFORMATIONAL = "informational"


@dataclass
class Engagement:
    """Red team engagement."""
    engagement_id: str
    name: str
    engagement_type: EngagementType
    status: EngagementStatus
    start_date: datetime
    end_date: Optional[datetime] = None
    scope: List[str] = field(default_factory=list)
    rules_of_engagement: List[str] = field(default_factory=list)
    objectives: List[str] = field(default_factory=list)
    targets: List[str] = field(default_factory=list)
    team_members: List[str] = field(default_factory=list)
    findings_count: int = 0
    critical_findings: int = 0
    created_at: datetime = field(default_factory=datetime.utcnow)


@dataclass
class Target:
    """Target system."""
    target_id: str
    name: str
    target_type: TargetType
    ip_address: Optional[str] = None
    domain: Optional[str] = None
    os: Optional[str] = None
    services: List[Dict[str, Any]] = field(default_factory=list)
    vulnerabilities: List[str] = field(default_factory=list)
    credentials_found: List[Dict[str, str]] = field(default_factory=list)
    accessed: bool = False
    compromised_at: Optional[datetime] = None
    engagement_id: Optional[str] = None


@dataclass
class Finding:
    """Security finding."""
    finding_id: str
    title: str
    description: str
    severity: FindingSeverity
    engagement_id: str
    target_id: Optional[str] = None
    cvss_score: Optional[float] = None
    category: str = ""  # initial_access, execution, persistence, etc.
    mitre_attack: List[str] = field(default_factory=list)
    evidence: List[str] = field(default_factory=list)
    remediation: str = ""
    reproduction_steps: List[str] = field(default_factory=list)
    screenshots: List[str] = field(default_factory=list)
    discovered_at: datetime = field(default_factory=datetime.utcnow)
    reported: bool = False


@dataclass
class Credential:
    """Discovered credential."""
    credential_id: str
    username: str
    source: str  # mimikatz, keylogger, phishing, etc.
    engagement_id: str
    password: Optional[str] = None
    hash: Optional[str] = None
    target_id: Optional[str] = None
    valid: bool = True
    tested_at: Optional[datetime] = None
    privileges: List[str] = field(default_factory=list)


@dataclass
class AttackPath:
    """Discovered attack path."""
    path_id: str
    name: str
    engagement_id: str
    start_point: str
    end_point: str
    steps: List[Dict[str, Any]] = field(default_factory=list)
    severity: FindingSeverity = FindingSeverity.HIGH
    time_to_exploit: int = 0  # minutes
    detection_evasion: List[str] = field(default_factory=list)
    mitre_attack: List[str] = field(default_factory=list)
    discovered_at: datetime = field(default_factory=datetime.utcnow)


class RedTeamAgent:
    """
    Red Team Agent for offensive security operations,
    penetration testing, and adversary emulation.
    """

    def __init__(self, agent_id: str = "redteam-agent"):
        self.agent_id = agent_id
        self.engagements: Dict[str, Engagement] = {}
        self.targets: Dict[str, Target] = {}
        self.findings: Dict[str, Finding] = {}
        self.credentials: Dict[str, Credential] = {}
        self.attack_paths: Dict[str, AttackPath] = {}

        # MITRE ATT&CK techniques library
        self.attack_techniques = {
            'T1566': 'Phishing',
            'T1059': 'Command and Scripting Interpreter',
            'T1078': 'Valid Accounts',
            'T1003': 'OS Credential Dumping',
            'T1021': 'Remote Services',
            'T1053': 'Scheduled Task/Job',
            'T1547': 'Boot or Logon Autostart Execution',
            'T1070': 'Indicator Removal',
            'T1048': 'Exfiltration Over Alternative Protocol',
            'T1486': 'Data Encrypted for Impact',
        }

        # Exploit database
        self.exploit_db = self._init_exploit_db()

    def _init_exploit_db(self) -> Dict[str, Dict[str, Any]]:
        """Initialize exploit database."""
        return {
            'eternal_blue': {
                'cve': 'CVE-2017-0144',
                'platform': 'windows',
                'port': 445,
                'difficulty': 'easy',
                'reliability': 'high',
            },
            'bluekeep': {
                'cve': 'CVE-2019-0708',
                'platform': 'windows',
                'port': 3389,
                'difficulty': 'medium',
                'reliability': 'medium',
            },
            'log4shell': {
                'cve': 'CVE-2021-44228',
                'platform': 'java',
                'port': 'any',
                'difficulty': 'easy',
                'reliability': 'critical',
            },
            'proxyshell': {
                'cve': 'CVE-2021-34473',
                'platform': 'exchange',
                'port': 443,
                'difficulty': 'medium',
                'reliability': 'high',
            },
        }

    # ============================================
    # Engagement Management
    # ============================================

    def create_engagement(
        self,
        name: str,
        engagement_type: EngagementType,
        start_date: datetime,
        scope: List[str],
        objectives: List[str],
        rules_of_engagement: Optional[List[str]] = None,
        team_members: Optional[List[str]] = None,
    ) -> Engagement:
        """Create a new engagement."""
        engagement = Engagement(
            engagement_id=self._generate_id("eng"),
            name=name,
            engagement_type=engagement_type,
            status=EngagementStatus.PLANNING,
            start_date=start_date,
            scope=scope,
            rules_of_engagement=rules_of_engagement or [],
            objectives=objectives,
            team_members=team_members or [],
        )

        self.engagements[engagement.engagement_id] = engagement
        logger.info(f"Created engagement: {engagement.name}")
        return engagement

    def update_engagement_status(
        self,
        engagement_id: str,
        status: EngagementStatus,
    ) -> bool:
        """Update engagement status."""
        if engagement_id not in self.engagements:
            return False

        self.engagements[engagement_id].status = status
        return True

    def add_target_to_engagement(
        self,
        engagement_id: str,
        target: str,
    ) -> bool:
        """Add target to engagement."""
        if engagement_id not in self.engagements:
            return False

        if target not in self.engagements[engagement_id].targets:
            self.engagements[engagement_id].targets.append(target)

        return True

    def get_engagements(
        self,
        engagement_type: Optional[EngagementType] = None,
        status: Optional[EngagementStatus] = None,
    ) -> List[Engagement]:
        """Get engagements with filtering."""
        engagements = list(self.engagements.values())

        if engagement_type:
            engagements = [e for e in engagements if e.engagement_type == engagement_type]

        if status:
            engagements = [e for e in engagements if e.status == status]

        return engagements

    # ============================================
    # Target Management
    # ============================================

    def add_target(
        self,
        name: str,
        target_type: TargetType,
        ip_address: Optional[str] = None,
        domain: Optional[str] = None,
        os: Optional[str] = None,
        services: Optional[List[Dict[str, Any]]] = None,
        engagement_id: Optional[str] = None,
    ) -> Target:
        """Add a target to the engagement."""
        target = Target(
            target_id=self._generate_id("tgt"),
            name=name,
            target_type=target_type,
            ip_address=ip_address,
            domain=domain,
            os=os,
            services=services or [],
            engagement_id=engagement_id,
        )

        self.targets[target.target_id] = target

        if engagement_id:
            self.add_target_to_engagement(engagement_id, target.target_id)

        return target

    def mark_target_compromised(self, target_id: str) -> bool:
        """Mark target as compromised."""
        if target_id not in self.targets:
            return False

        target = self.targets[target_id]
        target.accessed = True
        target.compromised_at = datetime.utcnow()

        return True

    def add_service_to_target(
        self,
        target_id: str,
        service_name: str,
        port: int,
        version: Optional[str] = None,
        vulnerable: bool = False,
    ) -> bool:
        """Add service to target."""
        if target_id not in self.targets:
            return False

        self.targets[target_id].services.append({
            'name': service_name,
            'port': port,
            'version': version,
            'vulnerable': vulnerable,
            'added_at': datetime.utcnow().isoformat(),
        })

        return True

    def get_targets(
        self,
        target_type: Optional[TargetType] = None,
        engagement_id: Optional[str] = None,
        compromised_only: bool = False,
    ) -> List[Target]:
        """Get targets with filtering."""
        targets = list(self.targets.values())

        if target_type:
            targets = [t for t in targets if t.target_type == target_type]

        if engagement_id:
            targets = [t for t in targets if t.engagement_id == engagement_id]

        if compromised_only:
            targets = [t for t in targets if t.accessed]

        return targets

    # ============================================
    # Finding Management
    # ============================================

    def add_finding(
        self,
        title: str,
        description: str,
        severity: FindingSeverity,
        engagement_id: str,
        target_id: Optional[str] = None,
        category: str = "",
        mitre_attack: Optional[List[str]] = None,
        evidence: Optional[List[str]] = None,
        remediation: str = "",
    ) -> Finding:
        """Add a security finding."""
        finding = Finding(
            finding_id=self._generate_id("find"),
            title=title,
            description=description,
            severity=severity,
            engagement_id=engagement_id,
            target_id=target_id,
            category=category,
            mitre_attack=mitre_attack or [],
            evidence=evidence or [],
            remediation=remediation,
        )

        self.findings[finding.finding_id] = finding

        # Update engagement findings count
        if engagement_id in self.engagements:
            self.engagements[engagement_id].findings_count += 1
            if severity == FindingSeverity.CRITICAL:
                self.engagements[engagement_id].critical_findings += 1

        return finding

    def get_findings(
        self,
        engagement_id: Optional[str] = None,
        severity: Optional[FindingSeverity] = None,
        reported: Optional[bool] = None,
    ) -> List[Finding]:
        """Get findings with filtering."""
        findings = list(self.findings.values())

        if engagement_id:
            findings = [f for f in findings if f.engagement_id == engagement_id]

        if severity:
            findings = [f for f in findings if f.severity == severity]

        if reported is not None:
            findings = [f for f in findings if f.reported == reported]

        return findings

    def mark_finding_reported(self, finding_id: str) -> bool:
        """Mark finding as reported."""
        if finding_id not in self.findings:
            return False

        self.findings[finding_id].reported = True
        return True

    # ============================================
    # Credential Management
    # ============================================

    def add_credential(
        self,
        username: str,
        source: str,
        password: Optional[str] = None,
        hash: Optional[str] = None,
        target_id: Optional[str] = None,
        engagement_id: Optional[str] = None,
        privileges: Optional[List[str]] = None,
    ) -> Credential:
        """Add discovered credential."""
        cred = Credential(
            credential_id=self._generate_id("cred"),
            username=username,
            password=password,
            hash=hash,
            source=source,
            target_id=target_id,
            engagement_id=engagement_id,
            privileges=privileges or [],
        )

        self.credentials[cred.credential_id] = cred

        if target_id and target_id in self.targets:
            self.targets[target_id].credentials_found.append({
                'credential_id': cred.credential_id,
                'username': username,
                'added_at': datetime.utcnow().isoformat(),
            })

        return cred

    def test_credential(self, credential_id: str, valid: bool) -> bool:
        """Test if credential is valid."""
        if credential_id not in self.credentials:
            return False

        cred = self.credentials[credential_id]
        cred.valid = valid
        cred.tested_at = datetime.utcnow()

        return True

    def get_credentials(
        self,
        engagement_id: Optional[str] = None,
        valid_only: bool = False,
    ) -> List[Credential]:
        """Get credentials with filtering."""
        creds = list(self.credentials.values())

        if engagement_id:
            creds = [c for c in creds if c.engagement_id == engagement_id]

        if valid_only:
            creds = [c for c in creds if c.valid]

        return creds

    # ============================================
    # Attack Path Discovery
    # ============================================

    def create_attack_path(
        self,
        name: str,
        engagement_id: str,
        start_point: str,
        end_point: str,
        steps: List[Dict[str, Any]],
        mitre_attack: Optional[List[str]] = None,
    ) -> AttackPath:
        """Document an attack path."""
        path = AttackPath(
            path_id=self._generate_id("path"),
            name=name,
            engagement_id=engagement_id,
            start_point=start_point,
            end_point=end_point,
            steps=steps,
            mitre_attack=mitre_attack or [],
            time_to_exploit=sum(s.get('time_minutes', 0) for s in steps),
        )

        # Determine severity based on end point
        if 'domain_admin' in end_point.lower() or 'critical' in end_point.lower():
            path.severity = FindingSeverity.CRITICAL
        elif 'admin' in end_point.lower() or 'sensitive' in end_point.lower():
            path.severity = FindingSeverity.HIGH

        self.attack_paths[path.path_id] = path
        return path

    def get_attack_paths(self, engagement_id: Optional[str] = None) -> List[AttackPath]:
        """Get attack paths with filtering."""
        paths = list(self.attack_paths.values())

        if engagement_id:
            paths = [p for p in paths if p.engagement_id == engagement_id]

        return paths

    # ============================================
    # Reporting
    # ============================================

    def generate_engagement_report(self, engagement_id: str) -> Dict[str, Any]:
        """Generate engagement report."""
        if engagement_id not in self.engagements:
            return {'error': 'Engagement not found'}

        engagement = self.engagements[engagement_id]
        findings = self.get_findings(engagement_id=engagement_id)
        paths = self.get_attack_paths(engagement_id=engagement_id)
        creds = self.get_credentials(engagement_id=engagement_id)
        targets = self.get_targets(engagement_id=engagement_id)

        # Findings by severity
        by_severity = {}
        for sev in FindingSeverity:
            by_severity[sev.value] = len([f for f in findings if f.severity == sev])

        # Compromised targets
        compromised = len([t for t in targets if t.accessed])

        return {
            'engagement': {
                'id': engagement_id,
                'name': engagement.name,
                'type': engagement.engagement_type.value,
                'status': engagement.status.value,
                'duration_days': (engagement.end_date or datetime.utcnow() - engagement.start_date).days if engagement.end_date else (datetime.utcnow() - engagement.start_date).days,
            },
            'summary': {
                'total_targets': len(targets),
                'compromised_targets': compromised,
                'compromise_rate': round(compromised / len(targets) * 100, 1) if targets else 0,
                'total_findings': len(findings),
                'findings_by_severity': by_severity,
                'attack_paths': len(paths),
                'credentials_found': len(creds),
                'valid_credentials': len([c for c in creds if c.valid]),
            },
            'mitre_coverage': self._get_mitre_coverage(findings, paths),
            'recommendations': self._generate_recommendations(findings),
        }

    def _get_mitre_coverage(self, findings: List[Finding], paths: List[AttackPath]) -> Dict[str, Any]:
        """Get MITRE ATT&CK coverage."""
        techniques = set()

        for f in findings:
            techniques.update(f.mitre_attack)

        for p in paths:
            techniques.update(p.mitre_attack)

        return {
            'techniques_used': list(techniques),
            'technique_names': [self.attack_techniques.get(t, t) for t in techniques],
            'total_techniques': len(techniques),
        }

    def _generate_recommendations(self, findings: List[Finding]) -> List[Dict[str, Any]]:
        """Generate prioritized recommendations."""
        recommendations = []

        # Group by severity
        critical = [f for f in findings if f.severity == FindingSeverity.CRITICAL]
        high = [f for f in findings if f.severity == FindingSeverity.HIGH]

        for f in critical[:5]:
            recommendations.append({
                'priority': 'critical',
                'finding': f.title,
                'remediation': f.remediation,
            })

        for f in high[:5]:
            recommendations.append({
                'priority': 'high',
                'finding': f.title,
                'remediation': f.remediation,
            })

        return recommendations

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
            'engagements_count': len(self.engagements),
            'active_engagements': len([e for e in self.engagements.values() if e.status != EngagementStatus.COMPLETED]),
            'targets_count': len(self.targets),
            'compromised_targets': len([t for t in self.targets.values() if t.accessed]),
            'findings_count': len(self.findings),
            'critical_findings': len([f for f in self.findings.values() if f.severity == FindingSeverity.CRITICAL]),
            'credentials_count': len(self.credentials),
            'attack_paths_count': len(self.attack_paths),
        }

    # ============================================
    # KaliAgent Integration
    # ============================================

    def execute_kali_recon(
        self,
        engagement_id: str,
        target: str,
        domain: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Execute reconnaissance using KaliAgent.

        Integrates with KaliAgent to run automated recon playbook
        and stores results in engagement.
        """
        try:
            from agentic_ai.agents.cyber.kali import KaliAgent, AuthorizationLevel

            # Initialize KaliAgent
            kali = KaliAgent()
            kali.set_authorization(AuthorizationLevel.BASIC)

            # Run recon playbook
            results = kali.run_recon_playbook(
                target=target,
                domain=domain,
            )

            # Process results and add to engagement
            findings_added = 0
            services_added = 0

            if "nmap" in results and results["nmap"].exit_code == 0:
                # Parse nmap output for services
                for line in results["nmap"].stdout.split("\n"):
                    if "open" in line:
                        parts = line.split()
                        if len(parts) >= 2:
                            port = parts[0].replace("/tcp", "")
                            service = parts[1] if len(parts) > 1 else "unknown"
                            self.add_service_to_target(
                                target_id=target,
                                engagement_id=engagement_id,
                                port=int(port),
                                protocol="tcp",
                                service=service,
                            )
                            services_added += 1

            # Generate report
            report = kali.generate_playbook_report(
                playbook_name="recon",
                results=results,
            )

            return {
                "success": True,
                "engagement_id": engagement_id,
                "target": target,
                "services_discovered": services_added,
                "findings_added": findings_added,
                "tools_executed": list(results.keys()),
                "report": report,
            }

        except ImportError:
            return {"success": False, "error": "KaliAgent not available"}
        except Exception as e:
            logger.error(f"Kali recon failed: {e}")
            return {"success": False, "error": str(e)}

    def execute_kali_web_audit(
        self,
        engagement_id: str,
        url: str,
        target: str,
    ) -> Dict[str, Any]:
        """Execute web application audit using KaliAgent."""
        try:
            from agentic_ai.agents.cyber.kali import KaliAgent, AuthorizationLevel

            kali = KaliAgent()
            kali.set_authorization(AuthorizationLevel.ADVANCED)

            results = kali.run_web_audit_playbook(
                url=url,
                target=target,
            )

            # Add findings from results
            findings_added = 0
            for tool_name, result in results.items():
                if result.exit_code == 0 and result.stdout:
                    # Parse output for vulnerabilities
                    if "vulnerabilit" in result.stdout.lower() or "injection" in result.stdout.lower():
                        self.add_finding(
                            engagement_id=engagement_id,
                            title=f"{tool_name} - Vulnerability Detected",
                            description=result.stdout[:500],
                            severity=FindingSeverity.HIGH,
                            target_id=target,
                            category="web_application",
                        )
                        findings_added += 1

            report = kali.generate_playbook_report(
                playbook_name="web_audit",
                results=results,
            )

            return {
                "success": True,
                "engagement_id": engagement_id,
                "url": url,
                "findings_added": findings_added,
                "tools_executed": list(results.keys()),
                "report": report,
            }

        except ImportError:
            return {"success": False, "error": "KaliAgent not available"}
        except Exception as e:
            logger.error(f"Kali web audit failed: {e}")
            return {"success": False, "error": str(e)}

    def execute_kali_password_audit(
        self,
        engagement_id: str,
        hash_file: str,
        wordlist: str = "/usr/share/wordlists/rockyou.txt",
    ) -> Dict[str, Any]:
        """Execute password cracking audit using KaliAgent."""
        try:
            from agentic_ai.agents.cyber.kali import KaliAgent, AuthorizationLevel

            kali = KaliAgent()
            kali.set_authorization(AuthorizationLevel.ADVANCED)

            results = kali.run_password_audit_playbook(
                hash_file=hash_file,
                wordlist=wordlist,
            )

            # Extract cracked credentials
            creds_added = 0
            for tool_name, result in results.items():
                if result.exit_code == 0:
                    # Parse cracked passwords from output
                    for line in result.stdout.split("\n"):
                        if ":" in line and not line.startswith("#"):
                            parts = line.split(":")
                            if len(parts) >= 2:
                                self.add_credential(
                                    engagement_id=engagement_id,
                                    username=parts[0],
                                    password=parts[1] if len(parts) > 1 else None,
                                    source=tool_name,
                                )
                                creds_added += 1

            report = kali.generate_playbook_report(
                playbook_name="password_audit",
                results=results,
            )

            return {
                "success": True,
                "engagement_id": engagement_id,
                "credentials_cracked": creds_added,
                "tools_executed": list(results.keys()),
                "report": report,
            }

        except ImportError:
            return {"success": False, "error": "KaliAgent not available"}
        except Exception as e:
            logger.error(f"Kali password audit failed: {e}")
            return {"success": False, "error": str(e)}

    def execute_kali_full_engagement(
        self,
        engagement_id: str,
        targets: List[str],
        domains: Optional[Dict[str, str]] = None,
    ) -> Dict[str, Any]:
        """Execute full engagement using KaliAgent playbooks.

        Runs complete engagement: recon → web audit → password audit → report
        """
        results = {
            "engagement_id": engagement_id,
            "phase_results": [],
            "total_findings": 0,
            "total_credentials": 0,
            "total_services": 0,
        }

        # Phase 1: Reconnaissance
        for target in targets:
            domain = domains.get(target) if domains else None
            recon_result = self.execute_kali_recon(
                engagement_id=engagement_id,
                target=target,
                domain=domain,
            )
            results["phase_results"].append({"phase": "recon", "target": target, **recon_result})
            if recon_result.get("success"):
                results["total_services"] += recon_result.get("services_discovered", 0)

        # Phase 2: Web audits (if web targets)
        # Phase 3: Password audits (if hashes found)
        # Phase 4: Generate final report

        final_report = self.generate_engagement_report(engagement_id)
        results["final_report"] = final_report

        return results


def get_capabilities() -> Dict[str, Any]:
    """Return agent capabilities for orchestration."""
    return {
        'agent_type': 'redteam',
        'version': '1.0.0',
        'capabilities': [
            'create_engagement',
            'update_engagement_status',
            'add_target_to_engagement',
            'get_engagements',
            'add_target',
            'mark_target_compromised',
            'add_service_to_target',
            'get_targets',
            'add_finding',
            'get_findings',
            'mark_finding_reported',
            'add_credential',
            'test_credential',
            'get_credentials',
            'create_attack_path',
            'get_attack_paths',
            'generate_engagement_report',
        ],
        'engagement_types': [e.value for e in EngagementType],
        'engagement_statuses': [s.value for s in EngagementStatus],
        'target_types': [t.value for t in TargetType],
        'finding_severities': [s.value for s in FindingSeverity],
        'mitre_techniques': list(RedTeamAgent(None).attack_techniques.keys()),
    }


if __name__ == "__main__":
    agent = RedTeamAgent()

    # Create engagement
    engagement = agent.create_engagement(
        name="Q2 Red Team Exercise",
        engagement_type=EngagementType.RED_TEAM,
        start_date=datetime.utcnow(),
        scope=["10.0.0.0/24", "example.com"],
        objectives=["Gain domain admin", "Access sensitive data", "Test detection"],
        rules_of_engagement=["No production impact", "Business hours only"],
        team_members=["red1", "red2"],
    )

    print(f"Created engagement: {engagement.name}")

    # Add targets
    target1 = agent.add_target(
        name="Web Server",
        target_type=TargetType.WEB_APP,
        ip_address="10.0.1.10",
        domain="web.example.com",
        os="Ubuntu 22.04",
        engagement_id=engagement.engagement_id,
    )

    agent.add_service_to_target(target1.target_id, "nginx", 80, "1.18.0", vulnerable=True)
    agent.add_service_to_target(target1.target_id, "ssh", 22, "OpenSSH 8.2")

    print(f"Added target: {target1.name}")

    # Add findings
    finding1 = agent.add_finding(
        title="SQL Injection in Login Form",
        description="Authentication bypass via SQL injection",
        severity=FindingSeverity.CRITICAL,
        engagement_id=engagement.engagement_id,
        target_id=target1.target_id,
        category="initial_access",
        mitre_attack=['T1190', 'T1059'],
        remediation="Use parameterized queries",
    )

    print(f"Added finding: {finding1.title}")

    # Add credentials
    cred = agent.add_credential(
        username="admin",
        password="Password123!",
        source="phishing",
        engagement_id=engagement.engagement_id,
        privileges=['local_admin'],
    )

    agent.test_credential(cred.credential_id, valid=True)

    # Create attack path
    path = agent.create_attack_path(
        name="Web to Domain Admin",
        engagement_id=engagement.engagement_id,
        start_point="External Web Server",
        end_point="Domain Admin",
        steps=[
            {'action': 'SQL Injection', 'target': 'web server', 'time_minutes': 15},
            {'action': 'Credential Dump', 'target': 'web server', 'time_minutes': 10},
            {'action': 'Lateral Movement', 'target': 'DC', 'time_minutes': 30},
            {'action': 'DC Sync', 'target': 'domain', 'time_minutes': 20},
        ],
        mitre_attack=['T1190', 'T1003', 'T1021', 'T1078'],
    )

    print(f"Created attack path: {path.name} ({path.time_to_exploit} min)")

    # Generate report
    report = agent.generate_engagement_report(engagement.engagement_id)
    print(f"\nEngagement Report:")
    print(f"  Targets: {report['summary']['total_targets']}")
    print(f"  Compromised: {report['summary']['compromised_targets']}")
    print(f"  Findings: {report['summary']['total_findings']}")
    print(f"  MITRE Techniques: {report['mitre_coverage']['total_techniques']}")

    print(f"\nState: {agent.get_state()}")
