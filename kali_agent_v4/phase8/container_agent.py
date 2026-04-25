#!/usr/bin/env python3
"""
KaliAgent v4 - Phase 8: Container & Kubernetes Exploitation Agent
Docker daemon exploits, container escapes, and K8s attacks
"""

import json
import time
from datetime import datetime
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field
from enum import Enum


class ContainerAttackType(Enum):
    """Container attack types"""
    RECON = "recon"
    DAEMON_EXPLOIT = "daemon_exploit"
    CONTAINER_ESCAPE = "container_escape"
    PRIV_ESC = "privilege_escalation"
    SECRETS_EXTRACT = "secrets_extraction"
    K8S_RBAC_ABUSE = "k8s_rbac_abuse"
    K8S_POD_ESCAPE = "k8s_pod_escape"
    SUPPLY_CHAIN = "supply_chain"


@dataclass
class ContainerFinding:
    """Container security finding"""
    finding_id: str
    title: str
    severity: str
    description: str
    affected_object: str
    attack_type: str
    remediation: str
    cvss_score: float = 0.0
    evidence: Dict[str, Any] = field(default_factory=dict)
    references: List[str] = field(default_factory=list)


@dataclass
class K8sResource:
    """Kubernetes resource"""
    kind: str
    name: str
    namespace: str
    labels: Dict[str, str] = field(default_factory=dict)
    annotations: Dict[str, str] = field(default_factory=dict)


class ContainerAgent:
    """
    Container & Kubernetes Exploitation Agent
    
    Capabilities:
    - Docker daemon reconnaissance
    - Container escape detection
    - Privilege escalation paths
    - Secrets extraction
    - Kubernetes RBAC abuse
    - Pod security bypass
    - Supply chain attacks
    
    ⚠️ WARNING: For authorized testing ONLY
    """
    
    def __init__(self, target: str = "localhost", k8s_context: str = None):
        self.target = target
        self.k8s_context = k8s_context
        self.agent_id = f"container-{datetime.now().strftime('%Y%m%d%H%M%S')}"
        self.session_data = {}
        self.findings: List[ContainerFinding] = []
        self.containers = []
        self.images = []
        self.k8s_resources: List[K8sResource] = []
        
        print(f"🐳 Container Agent initialized: {self.agent_id}")
        print(f"   Target: {target}")
        if k8s_context:
            print(f"   K8s Context: {k8s_context}")
    
    def check_docker_daemon(self) -> Dict:
        """Check Docker daemon accessibility and configuration"""
        print(f"\n🔍 Checking Docker daemon...")
        
        # Simulate daemon check
        daemon_info = {
            "accessible": True,
            "version": "24.0.7",
            "api_version": "1.43",
            "os": "linux",
            "arch": "amd64",
            "ncpu": 8,
            "containers_running": 12,
            "security": {
                "selinux_enabled": False,
                "apparmor_enabled": True,
                "rootless": False,
                "userns_remapping": False
            }
        }
        
        print(f"   Docker Version: {daemon_info['version']}")
        print(f"   Containers Running: {daemon_info['containers_running']}")
        print(f"   SELinux: {daemon_info['security']['selinux_enabled']}")
        print(f"   Rootless: {daemon_info['security']['rootless']}")
        
        # Check for vulnerable configurations
        if not daemon_info['security']['selinux_enabled']:
            self.findings.append(ContainerFinding(
                finding_id="CONTAINER-SELINUX-001",
                title="SELinux Disabled",
                severity="medium",
                description="SELinux is not enabled, reducing container isolation",
                affected_object="Docker Daemon",
                attack_type="recon",
                remediation="Enable SELinux with --selinux-enabled flag",
                cvss_score=5.5
            ))
        
        if not daemon_info['security']['rootless']:
            self.findings.append(ContainerFinding(
                finding_id="CONTAINER-ROOTLESS-001",
                title="Not Running Rootless",
                severity="medium",
                description="Docker daemon running as root increases attack surface",
                affected_object="Docker Daemon",
                attack_type="recon",
                remediation="Consider rootless Docker deployment",
                cvss_score=5.0
            ))
        
        return daemon_info
    
    def enumerate_containers(self) -> List[Dict]:
        """Enumerate running containers"""
        print(f"\n🔍 Enumerating containers...")
        
        # Simulate container enumeration
        self.containers = [
            {
                "id": "abc123def456",
                "name": "/web-app",
                "image": "nginx:1.21",
                "status": "running",
                "ports": ["80:80", "443:443"],
                "privileged": False,
                "capabilities": ["NET_BIND_SERVICE"],
                "volumes": ["/var/www:/usr/share/nginx/html:ro"],
                "network_mode": "bridge"
            },
            {
                "id": "def789ghi012",
                "name": "/database",
                "image": "postgres:13",
                "status": "running",
                "ports": ["5432:5432"],
                "privileged": False,
                "capabilities": [],
                "volumes": ["/data/postgres:/var/lib/postgresql/data"],
                "network_mode": "bridge"
            },
            {
                "id": "ghi345jkl678",
                "name": "/jenkins",
                "image": "jenkins/jenkins:lts",
                "status": "running",
                "ports": ["8080:8080"],
                "privileged": True,  # CRITICAL FINDING!
                "capabilities": ["SYS_ADMIN", "NET_ADMIN"],
                "volumes": ["/var/run/docker.sock:/var/run/docker.sock"],  # CRITICAL!
                "network_mode": "host"
            }
        ]
        
        print(f"   Found {len(self.containers)} containers")
        
        # Analyze for security issues
        for container in self.containers:
            # Check privileged mode
            if container.get('privileged'):
                self.findings.append(ContainerFinding(
                    finding_id=f"CONTAINER-PRIV-{container['name']}",
                    title=f"Privileged Container: {container['name']}",
                    severity="critical",
                    description=f"Container {container['name']} runs in privileged mode",
                    affected_object=container['name'],
                    attack_type="container_escape",
                    remediation="Remove privileged flag and use specific capabilities instead",
                    cvss_score=9.0,
                    evidence={"container": container},
                    references=["https://attack.mitre.org/techniques/T1611/"]
                ))
            
            # Check Docker socket mount
            volumes = container.get('volumes', [])
            for volume in volumes:
                if 'docker.sock' in volume:
                    self.findings.append(ContainerFinding(
                        finding_id=f"CONTAINER-SOCKET-{container['name']}",
                        title=f"Docker Socket Mounted: {container['name']}",
                        severity="critical",
                        description=f"Container {container['name']} has Docker socket mounted - full host control possible",
                        affected_object=container['name'],
                        attack_type="container_escape",
                        remediation="Remove Docker socket mount immediately",
                        cvss_score=10.0,
                        evidence={"volume": volume},
                        references=["https://github.com/BishopFox/container-pentest-playbook"]
                    ))
            
            # Check capabilities
            caps = container.get('capabilities', [])
            dangerous_caps = ['SYS_ADMIN', 'NET_ADMIN', 'SYS_PTRACE']
            for cap in caps:
                if cap in dangerous_caps:
                    self.findings.append(ContainerFinding(
                        finding_id=f"CONTAINER-CAP-{container['name']}-{cap}",
                        title=f"Dangerous Capability: {cap}",
                        severity="high",
                        description=f"Container {container['name']} has {cap} capability",
                        affected_object=container['name'],
                        attack_type="privilege_escalation",
                        remediation=f"Remove {cap} capability if not absolutely required",
                        cvss_score=7.5
                    ))
        
        print(f"   Generated {len(self.findings)} findings")
        
        return self.containers
    
    def enumerate_images(self) -> List[Dict]:
        """Enumerate Docker images"""
        print(f"\n🔍 Enumerating images...")
        
        # Simulate image enumeration
        self.images = [
            {
                "id": "sha256:abc123",
                "repository": "nginx",
                "tag": "1.21",
                "created": "2024-01-15",
                "size": "142MB",
                "vulnerabilities": {
                    "critical": 0,
                    "high": 2,
                    "medium": 5,
                    "low": 12
                }
            },
            {
                "id": "sha256:def456",
                "repository": "postgres",
                "tag": "13",
                "created": "2024-02-20",
                "size": "376MB",
                "vulnerabilities": {
                    "critical": 1,
                    "high": 3,
                    "medium": 8,
                    "low": 15
                }
            },
            {
                "id": "sha256:ghi789",
                "repository": "jenkins/jenkins",
                "tag": "lts",
                "created": "2023-11-10",
                "size": "4.2GB",
                "vulnerabilities": {
                    "critical": 5,
                    "high": 12,
                    "medium": 25,
                    "low": 40
                }
            }
        ]
        
        print(f"   Found {len(self.images)} images")
        
        # Check for vulnerable images
        for image in self.images:
            vulns = image.get('vulnerabilities', {})
            if vulns.get('critical', 0) > 0:
                self.findings.append(ContainerFinding(
                    finding_id=f"CONTAINER-VULN-{image['repository']}",
                    title=f"Vulnerable Image: {image['repository']}:{image['tag']}",
                    severity="critical" if vulns['critical'] > 2 else "high",
                    description=f"Image has {vulns['critical']} critical vulnerabilities",
                    affected_object=f"{image['repository']}:{image['tag']}",
                    attack_type="recon",
                    remediation="Update to latest patched version",
                    cvss_score=8.5 if vulns['critical'] > 2 else 7.0,
                    evidence={"vulnerabilities": vulns}
                ))
        
        return self.images
    
    def container_escape_check(self) -> List[ContainerFinding]:
        """Check for container escape vulnerabilities"""
        print(f"\n🔍 Checking for container escape vectors...")
        
        escape_vectors = []
        
        # Simulate escape vector detection
        escape_checks = [
            {
                "name": "Docker Socket",
                "check": "/var/run/docker.sock accessible",
                "vulnerable": True,
                "severity": "critical",
                "description": "Docker socket accessible from container allows full host control"
            },
            {
                "name": "Proc Mount",
                "check": "/proc mounted without hidepid",
                "vulnerable": False,
                "severity": "medium",
                "description": "Proc filesystem visible to containers"
            },
            {
                "name": "Sys Module",
                "check": "/sys mounted read-write",
                "vulnerable": False,
                "severity": "high",
                "description": "Sys filesystem writable from container"
            },
            {
                "name": "CVE-2019-5736",
                "check": "runc version vulnerable",
                "vulnerable": False,
                "severity": "critical",
                "description": "runc container escape vulnerability"
            },
            {
                "name": "Dirty Cow",
                "check": "Kernel version vulnerable to CVE-2016-5195",
                "vulnerable": False,
                "severity": "critical",
                "description": "Dirty Cow privilege escalation"
            }
        ]
        
        for check in escape_checks:
            if check['vulnerable']:
                finding = ContainerFinding(
                    finding_id=f"ESCAPE-{check['name'].replace(' ', '-')}",
                    title=f"Escape Vector: {check['name']}",
                    severity=check['severity'],
                    description=check['description'],
                    affected_object="Container Runtime",
                    attack_type="container_escape",
                    remediation=self._get_escape_remediation(check['name']),
                    cvss_score=9.0 if check['severity'] == 'critical' else 7.0,
                    evidence={"check": check['check']}
                )
                escape_vectors.append(finding)
                self.findings.append(finding)
                print(f"   ⚠️  VULNERABLE: {check['name']}")
            else:
                print(f"   ✅ Secure: {check['name']}")
        
        return escape_vectors
    
    def _get_escape_remediation(self, vector: str) -> str:
        """Get remediation for escape vector"""
        remediations = {
            "Docker Socket": "Remove Docker socket mount, use Docker-in-Docker or kaniko instead",
            "Proc Mount": "Mount /proc with hidepid=2 option",
            "Sys Module": "Mount /sys as read-only",
            "CVE-2019-5736": "Update runc to version 1.0.0-rc93 or later",
            "Dirty Cow": "Update kernel to patched version"
        }
        return remediations.get(vector, "Review container security configuration")
    
    def extract_secrets(self) -> Dict:
        """Extract secrets from containers"""
        print(f"\n🔐 Extracting secrets from containers...")
        
        secrets_found = {
            "env_vars": [],
            "files": [],
            "k8s_secrets": [],
            "docker_configs": []
        }
        
        # Simulate secret extraction
        secrets_found['env_vars'] = [
            {
                "container": "/web-app",
                "name": "DATABASE_URL",
                "value": "postgres://admin:password123@db:5432/app",
                "risk": "high"
            },
            {
                "container": "/web-app",
                "name": "API_KEY",
                "value": "sk-xxxxxxxxxxxxxxxxxxxxxxxx",
                "risk": "critical"
            }
        ]
        
        secrets_found['files'] = [
            {
                "container": "/database",
                "path": "/var/lib/postgresql/data/.pgpass",
                "risk": "high",
                "description": "PostgreSQL password file"
            }
        ]
        
        # Generate findings
        for secret in secrets_found['env_vars']:
            self.findings.append(ContainerFinding(
                finding_id=f"SECRET-ENV-{secret['name']}",
                title=f"Secret in Environment: {secret['name']}",
                severity="critical" if secret['risk'] == 'critical' else "high",
                description=f"Sensitive value exposed in {secret['container']} environment",
                affected_object=secret['container'],
                attack_type="secrets_extract",
                remediation="Use Docker secrets or external secret management (Vault, AWS Secrets Manager)",
                cvss_score=8.5 if secret['risk'] == 'critical' else 7.0,
                evidence={"name": secret['name']}
            ))
        
        print(f"   Environment Variables: {len(secrets_found['env_vars'])}")
        print(f"   Files: {len(secrets_found['files'])}")
        print(f"   ⚠️  Total secrets exposed: {len(secrets_found['env_vars']) + len(secrets_found['files'])}")
        
        return secrets_found
    
    def k8s_recon(self) -> Dict:
        """Kubernetes reconnaissance"""
        print(f"\n🔍 Kubernetes reconnaissance...")
        
        if not self.k8s_context:
            print("   ⚠️  No K8s context configured")
            return {}
        
        # Simulate K8s enumeration
        k8s_info = {
            "cluster_version": "v1.28.4",
            "nodes": 3,
            "namespaces": ["default", "kube-system", "production", "development"],
            "pods": 45,
            "services": 23,
            "deployments": 18,
            "service_accounts": 67,
            "cluster_roles": 156,
            "secrets": 89
        }
        
        print(f"   Cluster Version: {k8s_info['cluster_version']}")
        print(f"   Nodes: {k8s_info['nodes']}")
        print(f"   Pods: {k8s_info['pods']}")
        print(f"   Namespaces: {len(k8s_info['namespaces'])}")
        
        # Check for security issues
        if k8s_info['cluster_version'] < "v1.25.0":
            self.findings.append(ContainerFinding(
                finding_id="K8S-VERSION-001",
                title="Outdated Kubernetes Version",
                severity="high",
                description=f"Cluster running old version {k8s_info['cluster_version']}",
                affected_object="Kubernetes Cluster",
                attack_type="recon",
                remediation="Upgrade to latest stable Kubernetes version",
                cvss_score=7.0
            ))
        
        return k8s_info
    
    def k8s_rbac_check(self) -> List[ContainerFinding]:
        """Check Kubernetes RBAC for abuse opportunities"""
        print(f"\n🔍 Checking K8s RBAC...")
        
        if not self.k8s_context:
            print("   ⚠️  No K8s context configured")
            return []
        
        rbac_findings = []
        
        # Simulate RBAC issues
        rbac_issues = [
            {
                "name": "Cluster Admin Binding",
                "severity": "critical",
                "description": "Service account bound to cluster-admin role",
                "affected": "system:serviceaccount:default:jenkins",
                "remediation": "Use least-privilege roles instead of cluster-admin"
            },
            {
                "name": "Wildcard Permissions",
                "severity": "high",
                "description": "Role with wildcard (*) permissions on resources",
                "affected": "role:developer-full-access",
                "remediation": "Specify explicit resources and verbs"
            },
            {
                "name": "Pod Exec Permission",
                "severity": "high",
                "description": "Service account can exec into pods",
                "affected": "system:serviceaccount:development:dev-sa",
                "remediation": "Remove pods/exec permission unless absolutely required"
            }
        ]
        
        for issue in rbac_issues:
            finding = ContainerFinding(
                finding_id=f"K8S-RBAC-{issue['name'].replace(' ', '-')}",
                title=f"RBAC Issue: {issue['name']}",
                severity=issue['severity'],
                description=issue['description'],
                affected_object=issue['affected'],
                attack_type="k8s_rbac_abuse",
                remediation=issue['remediation'],
                cvss_score=9.0 if issue['severity'] == 'critical' else 7.5
            )
            rbac_findings.append(finding)
            self.findings.append(finding)
            print(f"   ⚠️  {issue['name']}")
        
        return rbac_findings
    
    def k8s_pod_security_check(self) -> List[ContainerFinding]:
        """Check Pod Security Standards/Contexts"""
        print(f"\n🔍 Checking K8s Pod Security...")
        
        if not self.k8s_context:
            print("   ⚠️  No K8s context configured")
            return []
        
        pss_findings = []
        
        # Simulate PSS violations
        violations = [
            {
                "pod": "production/web-app-7d8f9c",
                "violation": "Privileged container",
                "severity": "critical",
                "remediation": "Set securityContext.privileged: false"
            },
            {
                "pod": "production/database-0",
                "violation": "Running as root",
                "severity": "high",
                "remediation": "Set securityContext.runAsNonRoot: true"
            },
            {
                "pod": "development/test-pod",
                "violation": "Host network enabled",
                "severity": "high",
                "remediation": "Set hostNetwork: false"
            }
        ]
        
        for violation in violations:
            finding = ContainerFinding(
                finding_id=f"K8S-PSS-{violation['violation'].replace(' ', '-')}",
                title=f"Pod Security Violation: {violation['violation']}",
                severity=violation['severity'],
                description=f"Pod {violation['pod']} violates pod security standards",
                affected_object=violation['pod'],
                attack_type="k8s_pod_escape",
                remediation=violation['remediation'],
                cvss_score=8.5 if violation['severity'] == 'critical' else 7.0
            )
            pss_findings.append(finding)
            self.findings.append(finding)
        
        print(f"   Found {len(pss_findings)} PSS violations")
        
        return pss_findings
    
    def supply_chain_check(self) -> List[ContainerFinding]:
        """Check for supply chain vulnerabilities"""
        print(f"\n🔍 Checking container supply chain...")
        
        supply_chain_findings = []
        
        # Simulate supply chain issues
        issues = [
            {
                "image": "jenkins/jenkins:lts",
                "issue": "No image signature verification",
                "severity": "medium",
                "remediation": "Implement Docker Content Trust or cosign"
            },
            {
                "image": "nginx:1.21",
                "issue": "Base image outdated (6 months)",
                "severity": "medium",
                "remediation": "Update to latest base image"
            },
            {
                "registry": "docker.io",
                "issue": "Pulling from public registry without verification",
                "severity": "low",
                "remediation": "Use private registry with image scanning"
            }
        ]
        
        for issue in issues:
            finding = ContainerFinding(
                finding_id=f"SUPPLY-{issue['issue'].split()[0]}",
                title=f"Supply Chain: {issue['issue']}",
                severity=issue['severity'],
                description=issue['issue'],
                affected_object=issue.get('image', issue.get('registry', 'Unknown')),
                attack_type="supply_chain",
                remediation=issue['remediation'],
                cvss_score=5.5 if issue['severity'] == 'medium' else 4.0
            )
            supply_chain_findings.append(finding)
            self.findings.append(finding)
        
        print(f"   Found {len(supply_chain_findings)} supply chain issues")
        
        return supply_chain_findings
    
    def generate_report(self) -> Dict:
        """Generate container security assessment report"""
        print(f"\n📄 Generating container security report...")
        
        severity_counts = {
            'critical': sum(1 for f in self.findings if f.severity == 'critical'),
            'high': sum(1 for f in self.findings if f.severity == 'high'),
            'medium': sum(1 for f in self.findings if f.severity == 'medium'),
            'low': sum(1 for f in self.findings if f.severity == 'low')
        }
        
        report = {
            "agent_id": self.agent_id,
            "timestamp": datetime.utcnow().isoformat(),
            "target": self.target,
            "k8s_context": self.k8s_context,
            "summary": {
                "containers": len(self.containers),
                "images": len(self.images),
                "total_findings": len(self.findings),
                **severity_counts
            },
            "critical_findings": [
                {
                    "id": f.finding_id,
                    "title": f.title,
                    "cvss": f.cvss_score
                }
                for f in self.findings if f.severity == 'critical'
            ],
            "attack_vectors": list(set(f.attack_type for f in self.findings)),
            "recommendations": self._generate_recommendations()
        }
        
        return report
    
    def _generate_recommendations(self) -> List[str]:
        """Generate security recommendations"""
        recommendations = []
        
        if any(f.attack_type == 'container_escape' for f in self.findings):
            recommendations.append("CRITICAL: Remove Docker socket mounts from containers")
            recommendations.append("CRITICAL: Remove privileged flag from containers")
        
        if any(f.attack_type == 'secrets_extract' for f in self.findings):
            recommendations.append("HIGH: Use Docker secrets or external secret management")
        
        if any(f.attack_type == 'k8s_rbac_abuse' for f in self.findings):
            recommendations.append("CRITICAL: Remove cluster-admin bindings from service accounts")
        
        if any(f.attack_type == 'k8s_pod_escape' for f in self.findings):
            recommendations.append("HIGH: Enforce Pod Security Standards (Restricted profile)")
        
        # General recommendations
        recommendations.append("Implement image scanning in CI/CD pipeline")
        recommendations.append("Use read-only root filesystem for containers")
        recommendations.append("Drop all capabilities and add only required ones")
        recommendations.append("Enable SELinux/AppArmor for container isolation")
        recommendations.append("Regular container security assessments")
        
        return recommendations
    
    def get_status(self) -> Dict:
        """Get agent status"""
        return {
            "agent_id": self.agent_id,
            "target": self.target,
            "k8s_context": self.k8s_context,
            "containers_found": len(self.containers),
            "images_found": len(self.images),
            "findings_count": len(self.findings),
            "last_activity": self.session_data.get('timestamp', 'N/A')
        }


# Example usage
if __name__ == "__main__":
    # Create container agent
    agent = ContainerAgent(target="localhost", k8s_context="docker-desktop")
    
    # Check Docker daemon
    daemon_info = agent.check_docker_daemon()
    
    # Enumerate containers
    containers = agent.enumerate_containers()
    
    # Enumerate images
    images = agent.enumerate_images()
    
    # Check escape vectors
    escapes = agent.container_escape_check()
    
    # Extract secrets
    secrets = agent.extract_secrets()
    
    # K8s recon
    k8s_info = agent.k8s_recon()
    
    # K8s RBAC check
    rbac_findings = agent.k8s_rbac_check()
    
    # K8s Pod security check
    pss_findings = agent.k8s_pod_security_check()
    
    # Supply chain check
    supply_chain = agent.supply_chain_check()
    
    # Generate report
    report = agent.generate_report()
    
    print(f"\n{'='*60}")
    print(f"🐳 CONTAINER SECURITY ASSESSMENT COMPLETE")
    print(f"{'='*60}")
    print(f"Target: {report['target']}")
    print(f"Containers: {report['summary']['containers']}")
    print(f"Images: {report['summary']['images']}")
    print(f"Total Findings: {report['summary']['total_findings']}")
    print(f"  Critical: {report['summary']['critical']}")
    print(f"  High: {report['summary']['high']}")
    print(f"  Medium: {report['summary']['medium']}")
    print(f"  Low: {report['summary']['low']}")
    print(f"\nAttack Vectors:")
    for vector in report['attack_vectors']:
        print(f"  • {vector}")
    print(f"\nTop Recommendations:")
    for rec in report['recommendations'][:5]:
        print(f"  • {rec}")
