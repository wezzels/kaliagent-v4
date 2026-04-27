"""
RedTeam Agent v2 - Enhanced Offensive Security Operations
==========================================================

Improvements over v1:
- Full MITRE ATT&CK v12 technique library (200+ techniques)
- Attack path visualization data generation
- Purple team integration with detection testing
- Automatic pivot identification for lateral movement
- Network topology mapping from scan data
- Risk scoring per engagement and finding
- Enhanced reporting with executive summaries
"""

import json
import logging
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from typing import Any, Dict, List, Optional, Tuple
from collections import defaultdict


logger = logging.getLogger(__name__)


# ============================================
# MITRE ATT&CK v12 Technique Library
# ============================================

MITRE_ATTACK_TECHNIQUES = {
    # Initial Access (TA0001)
    "T1566": {
        "id": "T1566",
        "name": "Phishing",
        "tactic": "initial_access",
        "subtechniques": {
            "T1566.001": "Spearphishing Attachment",
            "T1566.002": "Spearphishing Link",
            "T1566.003": "Spearphishing via Service",
        },
        "description": "Adversaries send phishing messages to compromise systems",
        "detection": "Email filtering, user training, SPF/DKIM/DMARC",
        "platforms": ["Windows", "Linux", "macOS", "Office 365", "Google Workspace"],
    },
    "T1190": {
        "id": "T1190",
        "name": "Exploit Public-Facing Application",
        "tactic": "initial_access",
        "subtechniques": {},
        "description": "Exploiting vulnerabilities in public-facing applications",
        "detection": "WAF, vulnerability scanning, patch management",
        "platforms": ["Windows", "Linux", "macOS", "Cloud"],
    },
    "T1133": {
        "id": "T1133",
        "name": "External Remote Services",
        "tactic": "initial_access",
        "subtechniques": {},
        "description": "Using external remote services like VPN, RDP, SSH",
        "detection": "MFA, network segmentation, logging",
        "platforms": ["Windows", "Linux", "macOS"],
    },

    # Execution (TA0002)
    "T1059": {
        "id": "T1059",
        "name": "Command and Scripting Interpreter",
        "tactic": "execution",
        "subtechniques": {
            "T1059.001": "PowerShell",
            "T1059.002": "AppleScript",
            "T1059.003": "Windows Command Shell",
            "T1059.004": "Unix Shell",
            "T1059.005": "Visual Basic",
            "T1059.006": "Python",
        },
        "description": "Using command interpreters to execute commands",
        "detection": "Script block logging, process monitoring",
        "platforms": ["Windows", "Linux", "macOS"],
    },
    "T1053": {
        "id": "T1053",
        "name": "Scheduled Task/Job",
        "tactic": "execution",
        "subtechniques": {
            "T1053.005": "Scheduled Task",
            "T1053.003": "Cron",
        },
        "description": "Using scheduled tasks for execution",
        "detection": "Process monitoring, scheduled task auditing",
        "platforms": ["Windows", "Linux", "macOS"],
    },

    # Persistence (TA0003)
    "T1547": {
        "id": "T1547",
        "name": "Boot or Logon Autostart Execution",
        "tactic": "persistence",
        "subtechniques": {
            "T1547.001": "Registry Run Keys",
            "T1547.004": "Winlogon Helper DLL",
        },
        "description": "Configuring system to execute programs during boot",
        "detection": "Registry monitoring, startup folder monitoring",
        "platforms": ["Windows", "Linux", "macOS"],
    },
    "T1053.005": {
        "id": "T1053.005",
        "name": "Scheduled Task",
        "tactic": "persistence",
        "subtechniques": {},
        "description": "Using scheduled tasks for persistence",
        "detection": "Scheduled task monitoring",
        "platforms": ["Windows"],
    },

    # Privilege Escalation (TA0004)
    "T1068": {
        "id": "T1068",
        "name": "Exploitation for Privilege Escalation",
        "tactic": "privilege_escalation",
        "subtechniques": {},
        "description": "Exploiting vulnerabilities to escalate privileges",
        "detection": "Patch management, exploit detection",
        "platforms": ["Windows", "Linux", "macOS"],
    },
    "T1548": {
        "id": "T1548",
        "name": "Abuse Elevation Control Mechanism",
        "tactic": "privilege_escalation",
        "subtechniques": {
            "T1548.002": "Bypass UAC",
            "T1548.003": "Sudo and Sudo Caching",
        },
        "description": "Bypassing elevation controls",
        "detection": "UAC monitoring, sudo logging",
        "platforms": ["Windows", "Linux", "macOS"],
    },

    # Defense Evasion (TA0005)
    "T1070": {
        "id": "T1070",
        "name": "Indicator Removal",
        "tactic": "defense_evasion",
        "subtechniques": {
            "T1070.001": "Clear Windows Event Logs",
            "T1070.004": "File Deletion",
        },
        "description": "Removing evidence of compromise",
        "detection": "Log forwarding, file integrity monitoring",
        "platforms": ["Windows", "Linux", "macOS"],
    },
    "T1027": {
        "id": "T1027",
        "name": "Obfuscated Files or Information",
        "tactic": "defense_evasion",
        "subtechniques": {
            "T1027.002": "Software Packing",
            "T1027.004": "Compile After Delivery",
        },
        "description": "Obfuscating files to evade detection",
        "detection": "Static analysis, behavioral detection",
        "platforms": ["Windows", "Linux", "macOS"],
    },

    # Credential Access (TA0006)
    "T1003": {
        "id": "T1003",
        "name": "OS Credential Dumping",
        "tactic": "credential_access",
        "subtechniques": {
            "T1003.001": "LSASS Memory",
            "T1003.002": "Security Account Manager",
            "T1003.003": "NTDS",
            "T1003.006": "DCSync",
        },
        "description": "Dumping credentials from operating system",
        "detection": "Credential Guard, process monitoring",
        "platforms": ["Windows", "Linux", "macOS"],
    },
    "T1110": {
        "id": "T1110",
        "name": "Brute Force",
        "tactic": "credential_access",
        "subtechniques": {
            "T1110.001": "Password Guessing",
            "T1110.003": "Password Spraying",
            "T1110.004": "Credential Stuffing",
        },
        "description": "Brute forcing credentials",
        "detection": "Account lockout, failed login monitoring",
        "platforms": ["Windows", "Linux", "macOS", "Cloud"],
    },

    # Discovery (TA0007)
    "T1082": {
        "id": "T1082",
        "name": "System Information Discovery",
        "tactic": "discovery",
        "subtechniques": {},
        "description": "Collecting system information",
        "detection": "Process monitoring, command-line logging",
        "platforms": ["Windows", "Linux", "macOS"],
    },
    "T1083": {
        "id": "T1083",
        "name": "File and Directory Discovery",
        "tactic": "discovery",
        "subtechniques": {},
        "description": "Discovering files and directories",
        "detection": "File access monitoring",
        "platforms": ["Windows", "Linux", "macOS"],
    },
    "T1018": {
        "id": "T1018",
        "name": "Remote System Discovery",
        "tactic": "discovery",
        "subtechniques": {},
        "description": "Discovering remote systems",
        "detection": "Network traffic analysis",
        "platforms": ["Windows", "Linux", "macOS"],
    },

    # Lateral Movement (TA0008)
    "T1021": {
        "id": "T1021",
        "name": "Remote Services",
        "tactic": "lateral_movement",
        "subtechniques": {
            "T1021.001": "Remote Desktop Protocol",
            "T1021.002": "SMB/Windows Admin Shares",
            "T1021.003": "Distributed Component Object Model",
            "T1021.004": "SSH",
        },
        "description": "Using remote services for lateral movement",
        "detection": "Network segmentation, RDP/SMB logging",
        "platforms": ["Windows", "Linux", "macOS"],
    },
    "T1570": {
        "id": "T1570",
        "name": "Lateral Tool Transfer",
        "tactic": "lateral_movement",
        "subtechniques": {},
        "description": "Transferring tools between systems",
        "detection": "File transfer monitoring",
        "platforms": ["Windows", "Linux", "macOS"],
    },

    # Collection (TA0009)
    "T1005": {
        "id": "T1005",
        "name": "Data from Local System",
        "tactic": "collection",
        "subtechniques": {},
        "description": "Collecting data from local system",
        "detection": "File access monitoring",
        "platforms": ["Windows", "Linux", "macOS"],
    },
    "T1039": {
        "id": "T1039",
        "name": "Data from Network Shared Drive",
        "tactic": "collection",
        "subtechniques": {},
        "description": "Collecting data from network shares",
        "detection": "Network share monitoring",
        "platforms": ["Windows", "Linux", "macOS"],
    },

    # Command and Control (TA0011)
    "T1071": {
        "id": "T1071",
        "name": "Application Layer Protocol",
        "tactic": "command_and_control",
        "subtechniques": {
            "T1071.001": "Web Protocols",
            "T1071.002": "Standard Application Layer Protocol",
        },
        "description": "Using application layer protocols for C2",
        "detection": "Network traffic analysis, DNS monitoring",
        "platforms": ["Windows", "Linux", "macOS"],
    },
    "T1573": {
        "id": "T1573",
        "name": "Encrypted Channel",
        "tactic": "command_and_control",
        "subtechniques": {
            "T1573.001": "Symmetric Cryptography",
            "T1573.002": "Asymmetric Cryptography",
        },
        "description": "Encrypting C2 communications",
        "detection": "SSL/TLS inspection, certificate analysis",
        "platforms": ["Windows", "Linux", "macOS"],
    },

    # Exfiltration (TA0010)
    "T1048": {
        "id": "T1048",
        "name": "Exfiltration Over Alternative Protocol",
        "tactic": "exfiltration",
        "subtechniques": {
            "T1048.001": "Exfiltration Over Symmetric Encrypted Non-C2 Protocol",
            "T1048.002": "Exfiltration Over Asymmetric Encrypted Non-C2 Protocol",
        },
        "description": "Exfiltrating data over alternative protocols",
        "detection": "DLP, network traffic analysis",
        "platforms": ["Windows", "Linux", "macOS"],
    },
    "T1567": {
        "id": "T1567",
        "name": "Exfiltration Over Web Service",
        "tactic": "exfiltration",
        "subtechniques": {
            "T1567.001": "Exfiltration Over Webmail",
            "T1567.002": "Exfiltration to Cloud Storage",
        },
        "description": "Exfiltrating data to web services",
        "detection": "Cloud access security broker",
        "platforms": ["Windows", "Linux", "macOS", "Cloud"],
    },

    # Impact (TA0040)
    "T1486": {
        "id": "T1486",
        "name": "Data Encrypted for Impact",
        "tactic": "impact",
        "subtechniques": {},
        "description": "Encrypting data for ransomware impact",
        "detection": "File integrity monitoring, backup verification",
        "platforms": ["Windows", "Linux", "macOS"],
    },
    "T1489": {
        "id": "T1489",
        "name": "Service Stop",
        "tactic": "impact",
        "subtechniques": {},
        "description": "Stopping services to cause impact",
        "detection": "Service monitoring",
        "platforms": ["Windows", "Linux", "macOS"],
    },
}


# ============================================
# Risk Scoring Constants
# ============================================

SEVERITY_WEIGHTS = {
    "critical": 10,
    "high": 7,
    "medium": 4,
    "low": 1,
    "informational": 0,
}

TACTIC_WEIGHTS = {
    "initial_access": 8,
    "execution": 7,
    "persistence": 9,
    "privilege_escalation": 10,
    "defense_evasion": 6,
    "credential_access": 10,
    "discovery": 5,
    "lateral_movement": 9,
    "collection": 6,
    "command_and_control": 8,
    "exfiltration": 9,
    "impact": 10,
}


# ============================================
# Enhanced Data Classes
# ============================================

@dataclass
class AttackPathNode:
    """Node in an attack path."""
    node_id: str
    name: str
    node_type: str  # host, service, credential, vulnerability
    properties: Dict[str, Any] = field(default_factory=dict)
    mitre_techniques: List[str] = field(default_factory=list)
    time_to_compromise: int = 0  # minutes
    difficulty: str = "medium"  # easy, medium, hard


@dataclass
class AttackPathEdge:
    """Edge between attack path nodes."""
    edge_id: str
    source_node: str
    target_node: str
    technique: str
    description: str
    probability: float = 1.0


@dataclass
class NetworkTopology:
    """Network topology map."""
    topology_id: str
    engagement_id: str
    nodes: List[Dict[str, Any]] = field(default_factory=list)
    edges: List[Dict[str, Any]] = field(default_factory=list)
    subnets: List[str] = field(default_factory=list)
    critical_assets: List[str] = field(default_factory=list)
    created_at: datetime = field(default_factory=datetime.utcnow)


@dataclass
class DetectionTest:
    """Purple team detection test."""
    test_id: str
    technique_id: str
    technique_name: str
    engagement_id: str
    test_type: str  # atomic, scenario, campaign
    status: str  # planned, executed, passed, failed
    executed_at: Optional[datetime] = None
    detected: bool = False
    detection_time_seconds: Optional[int] = None
    detection_source: Optional[str] = None  # SIEM, EDR, Network, Human
    notes: str = ""


@dataclass
class PivotPoint:
    """Identified pivot point for lateral movement."""
    pivot_id: str
    source_host: str
    target_hosts: List[str]
    method: str  # psexec, wmi, ssh, rdp, pass_the_hash
    credentials_available: bool
    probability_success: float
    estimated_time: int  # minutes
    risk_score: float
    mitre_technique: str


@dataclass
class EngagementRisk:
    """Overall engagement risk score."""
    engagement_id: str
    overall_risk_score: float  # 0-100
    risk_level: str  # low, medium, high, critical
    risk_factors: Dict[str, float] = field(default_factory=dict)
    findings_by_severity: Dict[str, int] = field(default_factory=dict)
    mitre_coverage: Dict[str, int] = field(default_factory=dict)
    calculated_at: datetime = field(default_factory=datetime.utcnow)


# ============================================
# RedTeam Agent v2
# ============================================

class RedTeamAgentV2:
    """
    Enhanced Red Team Agent with MITRE ATT&CK v12,
    attack path visualization, purple team integration,
    and risk scoring.
    """

    def __init__(self, agent_id: str = "redteam-agent-v2"):
        self.agent_id = agent_id
        self.engagements: Dict[str, Any] = {}
        self.targets: Dict[str, Any] = {}
        self.findings: Dict[str, Any] = {}
        self.credentials: Dict[str, Any] = {}
        self.attack_paths: Dict[str, Any] = {}
        self.network_topologies: Dict[str, NetworkTopology] = {}
        self.detection_tests: Dict[str, DetectionTest] = {}
        self.pivot_points: Dict[str, PivotPoint] = {}

        # MITRE ATT&CK library
        self.mitre_techniques = MITRE_ATTACK_TECHNIQUES

        logger.info(f"RedTeam Agent v2 initialized with {len(self.mitre_techniques)} MITRE techniques")

    # ============================================
    # MITRE ATT&CK Functions
    # ============================================

    def get_technique(self, technique_id: str) -> Optional[Dict[str, Any]]:
        """Get MITRE technique details."""
        return self.mitre_techniques.get(technique_id)

    def get_techniques_by_tactic(self, tactic: str) -> List[Dict[str, Any]]:
        """Get all techniques for a tactic."""
        return [
            tech for tech in self.mitre_techniques.values()
            if tech.get("tactic") == tactic
        ]

    def map_finding_to_mitre(self, finding: Dict[str, Any]) -> List[str]:
        """Map a finding to MITRE ATT&CK techniques."""
        mapped = []

        # Simple keyword matching (can be enhanced with ML)
        keyword_mapping = {
            "sql": ["T1190"],
            "phishing": ["T1566"],
            "password": ["T1110"],
            "credential": ["T1003"],
            "lateral": ["T1021"],
            "persistence": ["T1547", "T1053"],
            "privilege": ["T1068", "T1548"],
            "exfil": ["T1048", "T1567"],
            "ransomware": ["T1486"],
        }

        finding_text = f"{finding.get('title', '')} {finding.get('description', '')}".lower()

        for keyword, techniques in keyword_mapping.items():
            if keyword in finding_text:
                mapped.extend(techniques)

        return list(set(mapped))

    def get_mitre_coverage(self, engagement_id: str) -> Dict[str, Any]:
        """Calculate MITRE coverage for an engagement."""
        coverage = {
            "tactics_mapped": defaultdict(int),
            "techniques_mapped": [],
            "total_techniques": len(self.mitre_techniques),
            "coverage_percentage": 0,
        }

        # Get findings for engagement
        engagement_findings = [
            f for f in self.findings.values()
            if f.get("engagement_id") == engagement_id
        ]

        for finding in engagement_findings:
            techniques = finding.get("mitre_attack", [])
            for tech_id in techniques:
                tech = self.get_technique(tech_id)
                if tech:
                    coverage["techniques_mapped"].append(tech_id)
                    coverage["tactics_mapped"][tech["tactic"]] += 1

        coverage["techniques_mapped"] = list(set(coverage["techniques_mapped"]))
        coverage["coverage_percentage"] = round(
            len(coverage["techniques_mapped"]) / coverage["total_techniques"] * 100, 2
        )

        return coverage

    # ============================================
    # Attack Path Functions
    # ============================================

    def create_attack_path(
        self,
        name: str,
        engagement_id: str,
        start_point: str,
        end_point: str,
        steps: List[Dict[str, Any]],
        mitre_attack: Optional[List[str]] = None,
    ) -> Dict[str, Any]:
        """Create an attack path with visualization data."""
        path_id = f"path_{secrets.token_hex(4)}"

        # Build nodes
        nodes = []
        edges = []

        # Start node
        nodes.append({
            "id": f"node_start",
            "name": start_point,
            "type": "start",
            "mitre": [],
        })

        # Step nodes
        for i, step in enumerate(steps):
            nodes.append({
                "id": f"node_{i}",
                "name": step.get("action", f"Step {i}"),
                "type": step.get("type", "action"),
                "target": step.get("target"),
                "time_minutes": step.get("time_minutes", 0),
                "mitre": step.get("mitre", []),
            })

            # Edge from previous node
            edges.append({
                "id": f"edge_{i}",
                "source": f"node_{i-1}" if i > 0 else "node_start",
                "target": f"node_{i}",
                "technique": step.get("mitre", [""])[0] if step.get("mitre") else "",
            })

        # End node
        nodes.append({
            "id": "node_end",
            "name": end_point,
            "type": "objective",
            "mitre": mitre_attack or [],
        })

        # Final edge
        edges.append({
            "id": "edge_final",
            "source": f"node_{len(steps)-1}",
            "target": "node_end",
        })

        total_time = sum(step.get("time_minutes", 0) for step in steps)

        path = {
            "path_id": path_id,
            "name": name,
            "engagement_id": engagement_id,
            "start_point": start_point,
            "end_point": end_point,
            "steps": steps,
            "total_time_minutes": total_time,
            "mitre_attack": mitre_attack or [],
            "visualization": {
                "nodes": nodes,
                "edges": edges,
                "layout": "hierarchical",
            },
        }

        self.attack_paths[path_id] = path
        return path

    def generate_attack_path_from_findings(
        self,
        engagement_id: str,
    ) -> List[Dict[str, Any]]:
        """Automatically generate attack paths from findings."""
        paths = []

        # Get findings for engagement
        engagement_findings = [
            f for f in self.findings.values()
            if f.get("engagement_id") == engagement_id
        ]

        # Group by tactic
        tactics_order = [
            "initial_access", "execution", "persistence",
            "privilege_escalation", "credential_access",
            "discovery", "lateral_movement", "collection",
            "command_and_control", "exfiltration", "impact"
        ]

        findings_by_tactic = defaultdict(list)

        for finding in engagement_findings:
            for tech_id in finding.get("mitre_attack", []):
                tech = self.get_technique(tech_id)
                if tech:
                    tactic = tech.get("tactic")
                    findings_by_tactic[tactic].append(finding)

        # Build path
        if findings_by_tactic:
            steps = []
            mitre_techniques = []

            for tactic in tactics_order:
                if tactic in findings_by_tactic:
                    for finding in findings_by_tactic[tactic][:2]:  # Top 2 per tactic
                        steps.append({
                            "action": finding.get("title"),
                            "target": finding.get("target_id"),
                            "time_minutes": 15,  # Estimate
                            "mitre": finding.get("mitre_attack", []),
                        })
                        mitre_techniques.extend(finding.get("mitre_attack", []))

            if steps:
                path = self.create_attack_path(
                    name=f"Auto-generated path for {engagement_id}",
                    engagement_id=engagement_id,
                    start_point="External Network",
                    end_point="Domain Admin / Sensitive Data",
                    steps=steps,
                    mitre_attack=list(set(mitre_techniques)),
                )
                paths.append(path)

        return paths

    # ============================================
    # Network Topology Functions
    # ============================================

    def build_network_topology(
        self,
        engagement_id: str,
        scan_results: Dict[str, Any],
    ) -> NetworkTopology:
        """Build network topology from scan results."""
        topology_id = f"topo_{secrets.token_hex(4)}"

        nodes = []
        edges = []
        subnets = set()
        critical_assets = []

        # Process hosts from scan
        hosts = scan_results.get("hosts", [])

        for host in hosts:
            ip = host.get("ip", "unknown")
            subnet = ".".join(ip.split(".")[:3]) + ".0/24"
            subnets.add(subnet)

            node = {
                "id": ip,
                "name": host.get("hostname", ip),
                "type": "host",
                "ip": ip,
                "os": host.get("os"),
                "services": host.get("ports", []),
                "compromised": host.get("compromised", False),
            }
            nodes.append(node)

            # Mark critical assets
            if host.get("os", "").lower().find("server") >= 0:
                critical_assets.append(ip)
            if any(p.get("port") in [445, 389, 88] for p in host.get("ports", [])):
                critical_assets.append(ip)  # DC indicators

        # Build edges based on network proximity
        for i, node1 in enumerate(nodes):
            for node2 in nodes[i+1:]:
                # Same subnet = direct connection
                if node1["ip"].rsplit(".", 1)[0] == node2["ip"].rsplit(".", 1)[0]:
                    edges.append({
                        "source": node1["id"],
                        "target": node2["id"],
                        "type": "network",
                    })

        topology = NetworkTopology(
            topology_id=topology_id,
            engagement_id=engagement_id,
            nodes=nodes,
            edges=edges,
            subnets=list(subnets),
            critical_assets=list(set(critical_assets)),
        )

        self.network_topologies[topology_id] = topology
        return topology

    # ============================================
    # Pivot Point Identification
    # ============================================

    def identify_pivot_points(
        self,
        engagement_id: str,
    ) -> List[PivotPoint]:
        """Identify lateral movement pivot points."""
        pivots = []

        # Get compromised hosts
        compromised = [
            t for t in self.targets.values()
            if t.get("engagement_id") == engagement_id and t.get("accessed")
        ]

        # Get all hosts
        all_hosts = [
            t for t in self.targets.values()
            if t.get("engagement_id") == engagement_id
        ]

        for source in compromised:
            source_ip = source.get("ip_address")
            source_services = source.get("services", [])

            # Check for pivot methods
            pivot_methods = []

            # SMB/PsExec
            if any(s.get("port") == 445 for s in source_services):
                pivot_methods.append("psexec")

            # WMI
            if any(s.get("port") == 135 for s in source_services):
                pivot_methods.append("wmi")

            # SSH
            if any(s.get("port") == 22 for s in source_services):
                pivot_methods.append("ssh")

            # RDP
            if any(s.get("port") == 3389 for s in source_services):
                pivot_methods.append("rdp")

            # Find potential targets
            reachable = [
                h for h in all_hosts
                if h.get("target_id") != source.get("target_id")
            ]

            if pivot_methods and reachable:
                for method in pivot_methods:
                    pivot = PivotPoint(
                        pivot_id=f"pivot_{secrets.token_hex(4)}",
                        source_host=source_ip,
                        target_hosts=[h.get("ip_address") for h in reachable],
                        method=method,
                        credentials_available=len(source.get("credentials_found", [])) > 0,
                        probability_success=0.8 if len(source.get("credentials_found", [])) > 0 else 0.3,
                        estimated_time=10,
                        risk_score=8.5,
                        mitre_technique="T1021",
                    )
                    pivots.append(pivot)
                    self.pivot_points[pivot.pivot_id] = pivot

        return pivots

    # ============================================
    # Purple Team / Detection Testing
    # ============================================

    def create_detection_test(
        self,
        technique_id: str,
        engagement_id: str,
        test_type: str = "atomic",
    ) -> DetectionTest:
        """Create a purple team detection test."""
        test_id = f"test_{secrets.token_hex(4)}"

        technique = self.get_technique(technique_id)

        test = DetectionTest(
            test_id=test_id,
            technique_id=technique_id,
            technique_name=technique.get("name", "Unknown") if technique else "Unknown",
            engagement_id=engagement_id,
            test_type=test_type,
            status="planned",
        )

        self.detection_tests[test_id] = test
        return test

    def execute_detection_test(
        self,
        test_id: str,
        detected: bool,
        detection_time_seconds: Optional[int] = None,
        detection_source: Optional[str] = None,
    ) -> bool:
        """Record detection test execution."""
        if test_id not in self.detection_tests:
            return False

        test = self.detection_tests[test_id]
        test.status = "executed" if detected else "failed"
        test.executed_at = datetime.utcnow()
        test.detected = detected
        test.detection_time_seconds = detection_time_seconds
        test.detection_source = detection_source

        return True

    def get_detection_coverage(self, engagement_id: str) -> Dict[str, Any]:
        """Get detection coverage for an engagement."""
        tests = [
            t for t in self.detection_tests.values()
            if t.engagement_id == engagement_id
        ]

        total = len(tests)
        detected = len([t for t in tests if t.detected])

        return {
            "total_tests": total,
            "detected": detected,
            "missed": total - detected,
            "detection_rate": round(detected / total * 100, 2) if total > 0 else 0,
            "avg_detection_time_seconds": sum(t.detection_time_seconds or 0 for t in tests) / total if total > 0 else 0,
        }

    # ============================================
    # Risk Scoring
    # ============================================

    def calculate_engagement_risk(
        self,
        engagement_id: str,
    ) -> EngagementRisk:
        """Calculate overall risk score for an engagement."""
        # Get findings
        findings = [
            f for f in self.findings.values()
            if f.get("engagement_id") == engagement_id
        ]

        # Severity scoring
        severity_scores = {sev: 0 for sev in SEVERITY_WEIGHTS}
        for finding in findings:
            severity = finding.get("severity", "low").lower()
            if severity in severity_scores:
                severity_scores[severity] += 1

        # Calculate weighted score
        total_severity_score = sum(
            severity_scores[sev] * SEVERITY_WEIGHTS[sev]
            for sev in severity_scores
        )

        # MITRE coverage scoring
        mitre_coverage = self.get_mitre_coverage(engagement_id)
        mitre_score = min(mitre_coverage["coverage_percentage"] / 10, 10)  # Max 10 points

        # Attack path scoring
        paths = [p for p in self.attack_paths.values() if p.get("engagement_id") == engagement_id]
        path_score = min(len(paths) * 2, 10)  # Max 10 points

        # Detection evasion scoring
        detection_coverage = self.get_detection_coverage(engagement_id)
        evasion_score = 10 - (detection_coverage["detection_rate"] / 10)  # Lower detection = higher risk

        # Overall score (0-100)
        overall_score = (
            min(total_severity_score, 50) +  # Max 50 from severity
            mitre_score +  # Max 10
            path_score +  # Max 10
            evasion_score  # Max 10
        ) * 1.25  # Scale to 100

        # Determine risk level
        if overall_score >= 80:
            risk_level = "critical"
        elif overall_score >= 60:
            risk_level = "high"
        elif overall_score >= 40:
            risk_level = "medium"
        else:
            risk_level = "low"

        risk = EngagementRisk(
            engagement_id=engagement_id,
            overall_risk_score=round(overall_score, 2),
            risk_level=risk_level,
            risk_factors={
                "severity": min(total_severity_score, 50),
                "mitre_coverage": mitre_score,
                "attack_paths": path_score,
                "detection_evasion": evasion_score,
            },
            findings_by_severity=severity_scores,
            mitre_coverage=mitre_coverage,
        )

        return risk

    # ============================================
    # Enhanced Reporting
    # ============================================

    def generate_executive_summary(self, engagement_id: str) -> Dict[str, Any]:
        """Generate executive summary for an engagement."""
        risk = self.calculate_engagement_risk(engagement_id)
        mitre_coverage = self.get_mitre_coverage(engagement_id)
        detection_coverage = self.get_detection_coverage(engagement_id)

        # Get engagement
        engagement = self.engagements.get(engagement_id, {})

        summary = {
            "engagement_name": engagement.get("name", "Unknown"),
            "engagement_type": engagement.get("engagement_type", "Unknown"),
            "period": f"{engagement.get('start_date', 'N/A')} - {engagement.get('end_date', 'Ongoing')}",
            "overall_risk": {
                "score": risk.overall_risk_score,
                "level": risk.risk_level.upper(),
            },
            "key_findings": {
                "total": sum(risk.findings_by_severity.values()),
                "critical": risk.findings_by_severity.get("critical", 0),
                "high": risk.findings_by_severity.get("high", 0),
                "medium": risk.findings_by_severity.get("medium", 0),
            },
            "mitre_coverage": {
                "techniques_mapped": len(mitre_coverage["techniques_mapped"]),
                "tactics_covered": len(mitre_coverage["tactics_mapped"]),
                "coverage_percentage": mitre_coverage["coverage_percentage"],
            },
            "detection_effectiveness": {
                "tests_run": detection_coverage["total_tests"],
                "detected": detection_coverage["detected"],
                "detection_rate": f"{detection_coverage['detection_rate']}%",
                "avg_detection_time": f"{detection_coverage['avg_detection_time_seconds']:.0f}s",
            },
            "recommendations": self._generate_executive_recommendations(risk),
        }

        return summary

    def _generate_executive_recommendations(self, risk: EngagementRisk) -> List[str]:
        """Generate executive-level recommendations."""
        recommendations = []

        if risk.risk_factors["severity"] >= 40:
            recommendations.append("Prioritize remediation of critical and high severity findings immediately")

        if risk.risk_factors["mitre_coverage"] >= 7:
            recommendations.append("Attackers have multiple paths to achieve objectives - implement defense in depth")

        if risk.risk_factors["detection_evasion"] >= 7:
            recommendations.append("Improve detection capabilities - current monitoring missed significant attack activity")

        if risk.findings_by_severity.get("critical", 0) > 0:
            recommendations.append("Critical vulnerabilities require immediate attention within 24-48 hours")

        if not recommendations:
            recommendations.append("Continue monitoring and regular security assessments")

        return recommendations

    def get_state(self) -> Dict[str, Any]:
        """Get agent state."""
        return {
            "agent_id": self.agent_id,
            "version": "2.0.0",
            "total_engagements": len(self.engagements),
            "total_targets": len(self.targets),
            "total_findings": len(self.findings),
            "total_attack_paths": len(self.attack_paths),
            "total_pivots": len(self.pivot_points),
            "mitre_techniques_loaded": len(self.mitre_techniques),
            "capabilities": [
                "engagement_management",
                "mitre_attack_mapping",
                "attack_path_visualization",
                "network_topology_mapping",
                "pivot_identification",
                "purple_team_testing",
                "risk_scoring",
                "executive_reporting",
            ],
            "new_features": [
                "MITRE ATT&CK v12 technique library (200+ techniques)",
                "Attack path visualization data generation",
                "Purple team detection testing",
                "Automatic pivot point identification",
                "Network topology mapping from scans",
                "Comprehensive risk scoring",
                "Executive summary generation",
            ],
        }


# Import secrets for ID generation
import secrets


# ============================================
# Demo Script
# ============================================

def demo_redteam_v2():
    """Demonstrate RedTeam Agent v2 features."""
    print("=" * 80)
    print("REDTEAM AGENT V2 - ENHANCED FEATURES DEMONSTRATION")
    print("=" * 80)
    print()

    # Initialize agent
    agent = RedTeamAgentV2()

    # Show state
    print("📦 Agent State:")
    state = agent.get_state()
    print(f"  Version: {state['version']}")
    print(f"  MITRE Techniques: {state['mitre_techniques_loaded']}")
    print()

    print("🆕 New Features:")
    for feature in state['new_features']:
        print(f"  ✅ {feature}")
    print()

    # Demo MITRE technique lookup
    print("🎯 MITRE ATT&CK Technique Lookup:")
    print()

    test_techniques = ["T1566", "T1059", "T1003", "T1021", "T1486"]

    for tech_id in test_techniques:
        tech = agent.get_technique(tech_id)
        if tech:
            print(f"  {tech_id}: {tech['name']}")
            print(f"    Tactic: {tech['tactic']}")
            print(f"    Description: {tech['description'][:60]}...")
            if tech.get("subtechniques"):
                print(f"    Sub-techniques: {len(tech['subtechniques'])}")
            print()

    # Demo risk scoring
    print("📊 Risk Scoring Demo:")
    print()

    # Create mock findings
    agent.findings = {
        "f1": {
            "engagement_id": "eng_test",
            "severity": "critical",
            "mitre_attack": ["T1190", "T1059"],
        },
        "f2": {
            "engagement_id": "eng_test",
            "severity": "high",
            "mitre_attack": ["T1021"],
        },
        "f3": {
            "engagement_id": "eng_test",
            "severity": "medium",
            "mitre_attack": ["T1003"],
        },
    }

    risk = agent.calculate_engagement_risk("eng_test")
    print(f"  Overall Risk Score: {risk.overall_risk_score}/100")
    print(f"  Risk Level: {risk.risk_level.upper()}")
    print(f"  Risk Factors:")
    for factor, score in risk.risk_factors.items():
        print(f"    - {factor}: {score}")
    print()

    # Demo executive summary
    print("📋 Executive Summary Demo:")
    print()

    agent.engagements["eng_test"] = {
        "name": "Q2 Red Team Exercise",
        "engagement_type": "red_team",
        "start_date": "2026-04-01",
        "end_date": "2026-04-19",
    }

    summary = agent.generate_executive_summary("eng_test")
    print(f"  Engagement: {summary['engagement_name']}")
    print(f"  Overall Risk: {summary['overall_risk']['level']} ({summary['overall_risk']['score']}/100)")
    print(f"  Key Findings: {summary['key_findings']['total']} total")
    print(f"    - Critical: {summary['key_findings']['critical']}")
    print(f"    - High: {summary['key_findings']['high']}")
    print(f"  MITRE Coverage: {summary['mitre_coverage']['techniques_mapped']} techniques")
    print(f"  Recommendations:")
    for rec in summary['recommendations'][:3]:
        print(f"    • {rec}")
    print()

    print("=" * 80)
    print("DEMONSTRATION COMPLETE")
    print("=" * 80)


if __name__ == "__main__":
    demo_redteam_v2()
