#!/usr/bin/env python3
"""
KaliAgent v4 - Phase 8: Cloud Exploitation Agent
AWS, Azure, and GCP security assessment automation
"""

import json
import time
from datetime import datetime
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field
from enum import Enum


class CloudProvider(Enum):
    """Supported cloud providers"""
    AWS = "aws"
    AZURE = "azure"
    GCP = "gcp"


class AttackType(Enum):
    """Cloud attack types"""
    RECON = "recon"
    IAM_ENUM = "iam_enumeration"
    PRIV_ESC = "privilege_escalation"
    DATA_EXFIL = "data_exfiltration"
    PERSISTENCE = "persistence"
    LATERAL = "lateral_movement"


@dataclass
class CloudResource:
    """Cloud resource definition"""
    resource_id: str
    resource_type: str
    provider: str
    region: str
    attributes: Dict[str, Any] = field(default_factory=dict)
    vulnerabilities: List[str] = field(default_factory=list)
    risk_level: str = "unknown"


@dataclass
class CloudFinding:
    """Cloud security finding"""
    finding_id: str
    title: str
    severity: str  # critical, high, medium, low, info
    description: str
    resource_id: str
    attack_vector: str
    remediation: str
    cvss_score: float = 0.0
    evidence: Dict[str, Any] = field(default_factory=dict)


class CloudAgent:
    """
    Cloud Exploitation Agent for multi-cloud security assessments
    
    Supports:
    - AWS (Amazon Web Services)
    - Azure (Microsoft)
    - GCP (Google Cloud Platform)
    
    Capabilities:
    - Reconnaissance
    - IAM enumeration
    - Privilege escalation detection
    - Data exfiltration simulation
    - Persistence detection
    - Lateral movement
    """
    
    def __init__(self, provider: CloudProvider, profile: str = "default"):
        self.provider = provider
        self.profile = profile
        self.agent_id = f"cloud-{provider.value}-{datetime.now().strftime('%H%M%S')}"
        self.resources: List[CloudResource] = []
        self.findings: List[CloudFinding] = []
        self.session_data = {}
        
        print(f"☁️  Cloud Agent initialized: {self.agent_id} ({provider.value})")
    
    def authenticate(self, credentials: Dict[str, str]) -> bool:
        """Authenticate to cloud provider"""
        print(f"🔐 Authenticating to {self.provider.value}...")
        
        # Validate credentials based on provider
        if self.provider == CloudProvider.AWS:
            required = ['access_key', 'secret_key']
        elif self.provider == CloudProvider.AZURE:
            required = ['client_id', 'tenant_id', 'client_secret']
        elif self.provider == CloudProvider.GCP:
            required = ['project_id', 'credentials_json']
        else:
            return False
        
        # Check required fields
        for field in required:
            if field not in credentials:
                print(f"❌ Missing credential: {field}")
                return False
        
        # In production, would actually authenticate
        # For now, simulate success
        self.session_data['authenticated'] = True
        self.session_data['timestamp'] = datetime.utcnow().isoformat()
        
        print(f"✅ Successfully authenticated to {self.provider.value}")
        return True
    
    def enumerate_iam(self) -> Dict:
        """Enumerate IAM users, roles, and policies"""
        print(f"\n🔍 Enumerating IAM on {self.provider.value}...")
        
        if not self.session_data.get('authenticated'):
            print("❌ Not authenticated!")
            return {}
        
        # Simulate IAM enumeration based on provider
        if self.provider == CloudProvider.AWS:
            return self._enumerate_aws_iam()
        elif self.provider == CloudProvider.AZURE:
            return self._enumerate_azure_ad()
        elif self.provider == CloudProvider.GCP:
            return self._enumerate_gcp_iam()
        
        return {}
    
    def _enumerate_aws_iam(self) -> Dict:
        """Enumerate AWS IAM"""
        result = {
            "users": [
                {"name": "admin", "groups": ["Administrators"], "mfa": False},
                {"name": "developer", "groups": ["Developers"], "mfa": True},
                {"name": "readonly", "groups": ["ReadOnly"], "mfa": False}
            ],
            "roles": [
                {"name": "LambdaExecutionRole", "trusted_entities": ["lambda.amazonaws.com"]},
                {"name": "EC2AdminRole", "trusted_entities": ["ec2.amazonaws.com"]}
            ],
            "policies": [
                {"name": "AdminAccess", "type": "managed", "attached": 3},
                {"name": "S3FullAccess", "type": "managed", "attached": 5}
            ],
            "risk_findings": [
                {
                    "type": "no_mfa",
                    "severity": "high",
                    "description": "User 'admin' has no MFA enabled"
                },
                {
                    "type": "overprivileged",
                    "severity": "medium",
                    "description": "Role 'EC2AdminRole' has excessive permissions"
                }
            ]
        }
        
        print(f"   Found {len(result['users'])} users")
        print(f"   Found {len(result['roles'])} roles")
        print(f"   Found {len(result['policies'])} policies")
        print(f"   Found {len(result['risk_findings'])} risk findings")
        
        return result
    
    def _enumerate_azure_ad(self) -> Dict:
        """Enumerate Azure Active Directory"""
        result = {
            "users": [
                {"name": "admin@tenant.onmicrosoft.com", "role": "Global Admin"},
                {"name": "user@tenant.onmicrosoft.com", "role": "User"}
            ],
            "groups": [
                {"name": "Global Administrators", "members": 2},
                {"name": "Cloud Application Administrators", "members": 3}
            ],
            "applications": [
                {"name": "Azure Portal", "id": "00000001-0000-0000-c000-000000000000"},
                {"name": "Office 365", "id": "00000002-0000-0000-c000-000000000000"}
            ],
            "risk_findings": [
                {
                    "type": "guest_users",
                    "severity": "medium",
                    "description": "Guest users have excessive permissions"
                }
            ]
        }
        
        print(f"   Found {len(result['users'])} users")
        print(f"   Found {len(result['groups'])} groups")
        print(f"   Found {len(result['applications'])} applications")
        
        return result
    
    def _enumerate_gcp_iam(self) -> Dict:
        """Enumerate GCP IAM"""
        result = {
            "service_accounts": [
                {"name": "compute@project.iam.gserviceaccount.com", "roles": ["compute.admin"]},
                {"name": "lambda@project.iam.gserviceaccount.com", "roles": ["storage.admin"]}
            ],
            "projects": [
                {"name": "production-project", "id": "prod-12345"},
                {"name": "development-project", "id": "dev-67890"}
            ],
            "roles": [
                {"name": "roles/compute.admin", "members": 5},
                {"name": "roles/storage.admin", "members": 3}
            ],
            "risk_findings": [
                {
                    "type": "service_account_key",
                    "severity": "critical",
                    "description": "Service account keys are rotated infrequently"
                }
            ]
        }
        
        print(f"   Found {len(result['service_accounts'])} service accounts")
        print(f"   Found {len(result['projects'])} projects")
        
        return result
    
    def scan_resources(self, resource_types: List[str] = None) -> List[CloudResource]:
        """Scan cloud resources"""
        print(f"\n🔍 Scanning cloud resources...")
        
        if resource_types is None:
            resource_types = ['compute', 'storage', 'database', 'networking']
        
        resources = []
        
        for resource_type in resource_types:
            # Simulate resource discovery
            resource = CloudResource(
                resource_id=f"{resource_type}-{datetime.now().strftime('%Y%m%d%H%M%S')}",
                resource_type=resource_type,
                provider=self.provider.value,
                region="us-east-1",
                attributes={"status": "running"},
                vulnerabilities=[],
                risk_level="medium"
            )
            resources.append(resource)
        
        self.resources = resources
        print(f"   Discovered {len(resources)} resources")
        
        return resources
    
    def detect_privilege_escalation(self) -> List[CloudFinding]:
        """Detect privilege escalation paths"""
        print(f"\n🎯 Detecting privilege escalation paths...")
        
        findings = []
        
        # Simulate privilege escalation detection
        if self.provider == CloudProvider.AWS:
            findings = self._detect_aws_priv_esc()
        elif self.provider == CloudProvider.AZURE:
            findings = self._detect_azure_priv_esc()
        elif self.provider == CloudProvider.GCP:
            findings = self._detect_gcp_priv_esc()
        
        self.findings.extend(findings)
        print(f"   Found {len(findings)} privilege escalation paths")
        
        return findings
    
    def _detect_aws_priv_esc(self) -> List[CloudFinding]:
        """Detect AWS privilege escalation paths"""
        return [
            CloudFinding(
                finding_id="PRIVESC-AWS-001",
                title="IAM Policy Over-Permission",
                severity="high",
                description="IAM policy allows iam:PassRole which can lead to privilege escalation",
                resource_id="policy-admin-001",
                attack_vector="PassRole to Lambda function",
                remediation="Remove iam:PassRole permission or restrict to specific roles",
                cvss_score=7.5,
                evidence={"policy": "arn:aws:iam::123456789012:policy/admin"}
            ),
            CloudFinding(
                finding_id="PRIVESC-AWS-002",
                title="Lambda Function Update",
                severity="critical",
                description="User can update Lambda function code with lambda:UpdateFunctionCode",
                resource_id="lambda-function-001",
                attack_vector="Inject malicious code into Lambda function",
                remediation="Restrict lambda:UpdateFunctionCode to CI/CD pipeline only",
                cvss_score=9.0,
                evidence={"function": "arn:aws:lambda:us-east-1:123456789012:function:vulnerable"}
            )
        ]
    
    def _detect_azure_priv_esc(self) -> List[CloudFinding]:
        """Detect Azure privilege escalation paths"""
        return [
            CloudFinding(
                finding_id="PRIVESC-AZURE-001",
                title="Contributor Role on Subscription",
                severity="high",
                description="User has Contributor role at subscription level",
                resource_id="subscription-001",
                attack_vector="Create privileged resources",
                remediation="Use resource-group level permissions instead",
                cvss_score=7.0
            )
        ]
    
    def _detect_gcp_priv_esc(self) -> List[CloudFinding]:
        """Detect GCP privilege escalation paths"""
        return [
            CloudFinding(
                finding_id="PRIVESC-GCP-001",
                title="Service Account Token Creation",
                severity="critical",
                description="Can create service account keys",
                resource_id="sa-compute-001",
                attack_vector="Create key and impersonate service account",
                remediation="Restrict iam.serviceAccountKeyCreator role",
                cvss_score=8.5
            )
        ]
    
    def enumerate_storage(self) -> Dict:
        """Enumerate storage resources (S3, Blob, GCS)"""
        print(f"\n📦 Enumerating storage...")
        
        storage_data = {
            "buckets": [],
            "public_access": [],
            "sensitive_data": []
        }
        
        # Simulate storage enumeration
        if self.provider == CloudProvider.AWS:
            storage_data = {
                "buckets": [
                    {"name": "company-public-assets", "public": True, "encrypted": False},
                    {"name": "company-logs", "public": False, "encrypted": True},
                    {"name": "backup-data", "public": False, "encrypted": False}
                ],
                "public_access": [
                    {
                        "bucket": "company-public-assets",
                        "risk": "medium",
                        "description": "Bucket is publicly readable"
                    }
                ],
                "sensitive_data": [
                    {
                        "bucket": "backup-data",
                        "risk": "high",
                        "description": "Unencrypted backup data"
                    }
                ]
            }
        
        print(f"   Found {len(storage_data['buckets'])} buckets")
        print(f"   Found {len(storage_data['public_access'])} public access issues")
        print(f"   Found {len(storage_data['sensitive_data'])} sensitive data issues")
        
        return storage_data
    
    def generate_report(self) -> Dict:
        """Generate cloud assessment report"""
        print(f"\n📄 Generating cloud assessment report...")
        
        report = {
            "agent_id": self.agent_id,
            "provider": self.provider.value,
            "timestamp": datetime.utcnow().isoformat(),
            "summary": {
                "resources_scanned": len(self.resources),
                "findings_count": len(self.findings),
                "critical": sum(1 for f in self.findings if f.severity == "critical"),
                "high": sum(1 for f in self.findings if f.severity == "high"),
                "medium": sum(1 for f in self.findings if f.severity == "medium"),
                "low": sum(1 for f in self.findings if f.severity == "low")
            },
            "findings": [
                {
                    "id": f.finding_id,
                    "title": f.title,
                    "severity": f.severity,
                    "cvss": f.cvss_score,
                    "description": f.description
                }
                for f in self.findings
            ],
            "recommendations": self._generate_recommendations()
        }
        
        return report
    
    def _generate_recommendations(self) -> List[str]:
        """Generate security recommendations"""
        recommendations = []
        
        # Analyze findings and generate recommendations
        critical_count = sum(1 for f in self.findings if f.severity == "critical")
        high_count = sum(1 for f in self.findings if f.severity == "high")
        
        if critical_count > 0:
            recommendations.append("IMMEDIATE: Address critical findings within 24 hours")
        
        if high_count > 0:
            recommendations.append("HIGH PRIORITY: Remediate high-severity findings within 1 week")
        
        recommendations.append("Enable MFA for all privileged users")
        recommendations.append("Implement least-privilege access")
        recommendations.append("Enable cloud trail/logging")
        recommendations.append("Regular access reviews")
        
        return recommendations
    
    def get_status(self) -> Dict:
        """Get agent status"""
        return {
            "agent_id": self.agent_id,
            "provider": self.provider.value,
            "authenticated": self.session_data.get('authenticated', False),
            "resources_found": len(self.resources),
            "findings_count": len(self.findings),
            "last_activity": self.session_data.get('timestamp', 'N/A')
        }


# Example usage
if __name__ == "__main__":
    # Create AWS cloud agent
    aws_agent = CloudAgent(CloudProvider.AWS)
    
    # Authenticate (simulated)
    aws_agent.authenticate({
        'access_key': 'AKIAIOSFODNN7EXAMPLE',
        'secret_key': 'wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY'
    })
    
    # Enumerate IAM
    iam_data = aws_agent.enumerate_iam()
    
    # Scan resources
    resources = aws_agent.scan_resources()
    
    # Detect privilege escalation
    priv_esc = aws_agent.detect_privilege_escalation()
    
    # Enumerate storage
    storage = aws_agent.enumerate_storage()
    
    # Generate report
    report = aws_agent.generate_report()
    
    print(f"\n{'='*60}")
    print(f"☁️  CLOUD ASSESSMENT COMPLETE")
    print(f"{'='*60}")
    print(f"Provider: {report['provider']}")
    print(f"Resources: {report['summary']['resources_scanned']}")
    print(f"Findings: {report['summary']['findings_count']}")
    print(f"  Critical: {report['summary']['critical']}")
    print(f"  High: {report['summary']['high']}")
    print(f"  Medium: {report['summary']['medium']}")
    print(f"  Low: {report['summary']['low']}")
    print(f"\nRecommendations:")
    for rec in report['recommendations'][:3]:
        print(f"  • {rec}")
