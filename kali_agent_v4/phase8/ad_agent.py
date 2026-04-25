#!/usr/bin/env python3
"""
KaliAgent v4 - Phase 8: Active Directory Exploitation Agent
Automated AD security assessment and attack simulation
"""

import json
import time
from datetime import datetime
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field
from enum import Enum


class ADAttackType(Enum):
    """Active Directory attack types"""
    RECON = "recon"
    KERBEROASTING = "kerberoasting"
    ASREP_ROASTING = "asrep_roasting"
    DCSYNC = "dcsync"
    GOLDEN_TICKET = "golden_ticket"
    SILVER_TICKET = "silver_ticket"
    ACL_ABUSE = "acl_abuse"
    GPO_EXPLOIT = "gpo_exploit"
    LAPS_DUMP = "laps_dump"
    BLOODHOUND = "bloodhounds"


@dataclass
class ADUser:
    """Active Directory user object"""
    username: str
    distinguished_name: str
    enabled: bool
    admin_count: bool = False
    spn: List[str] = field(default_factory=list)
    preauth_required: bool = True
    pwd_last_set: Optional[str] = None
    last_logon: Optional[str] = None
    member_of: List[str] = field(default_factory=list)


@dataclass
class ADComputer:
    """Active Directory computer object"""
    hostname: str
    dns_hostname: str
    enabled: bool
    operating_system: Optional[str] = None
    last_logon: Optional[str] = None
    dns_ttl: int = 120


@dataclass
class ADFinding:
    """Active Directory security finding"""
    finding_id: str
    title: str
    severity: str  # critical, high, medium, low, info
    description: str
    affected_object: str
    attack_type: str
    remediation: str
    cvss_score: float = 0.0
    evidence: Dict[str, Any] = field(default_factory=dict)
    references: List[str] = field(default_factory=list)


class ADAgent:
    """
    Active Directory Exploitation Agent for security assessments
    
    Capabilities:
    - Domain reconnaissance
    - User/computer enumeration
    - Kerberoasting
    - AS-REP Roasting
    - DCSync simulation
    - Golden/Silver ticket detection
    - ACL abuse detection
    - GPO exploitation
    - LAPS password retrieval
    - BloodHound integration
    
    ⚠️ WARNING: For authorized testing ONLY
    """
    
    def __init__(self, domain: str = None, dc_ip: str = None):
        self.domain = domain
        self.dc_ip = dc_ip
        self.agent_id = f"ad-{datetime.now().strftime('%Y%m%d%H%M%S')}"
        self.session_data = {}
        self.users: List[ADUser] = []
        self.computers: List[ADComputer] = []
        self.findings: List[ADFinding] = []
        self.groups = {}
        self.acls = {}
        
        print(f"🏢 AD Agent initialized: {self.agent_id}")
        if domain:
            print(f"   Target domain: {domain}")
        if dc_ip:
            print(f"   DC IP: {dc_ip}")
    
    def authenticate(self, username: str, password: str = None, 
                    hash: str = None, kerberos: bool = False) -> bool:
        """Authenticate to Active Directory"""
        print(f"\n🔐 Authenticating to AD...")
        
        # Validate auth method
        if not password and not hash and not kerberos:
            print("❌ No authentication method provided")
            print("   Provide: password, hash (NTLM), or kerberos=True")
            return False
        
        # Simulate authentication
        self.session_data['authenticated'] = True
        self.session_data['username'] = username
        self.session_data['method'] = 'kerberos' if kerberos else ('hash' if hash else 'password')
        self.session_data['timestamp'] = datetime.utcnow().isoformat()
        
        print(f"✅ Successfully authenticated as: {username}")
        print(f"   Method: {self.session_data['method']}")
        
        return True
    
    def enumerate_domain(self) -> Dict:
        """Enumerate domain information"""
        print(f"\n🔍 Enumerating domain...")
        
        if not self.session_data.get('authenticated'):
            print("❌ Not authenticated!")
            return {}
        
        # Simulate domain enumeration
        domain_info = {
            "domain": self.domain or "CORP.LOCAL",
            "dns_tree": [
                "corp.local",
                "├── users",
                "│   ├── admins",
                "│   ├── developers",
                "│   └── service_accounts",
                "├── computers",
                "│   ├── servers",
                "│   └── workstations",
                "└── groups"
            ],
            "functional_level": "Windows Server 2016",
            "dc_count": 2,
            "domain_sid": "S-1-5-21-1234567890-1234567890-1234567890",
            "password_policy": {
                "min_length": 7,
                "complexity": True,
                "max_age_days": 42,
                "lockout_threshold": 5,
                "lockout_duration_min": 30
            },
            "trusts": [
                {"domain": "CHILD.CORP.LOCAL", "type": "parent-child", "direction": "bidirectional"}
            ]
        }
        
        print(f"   Domain: {domain_info['domain']}")
        print(f"   Functional Level: {domain_info['functional_level']}")
        print(f"   DC Count: {domain_info['dc_count']}")
        print(f"   Password Policy: Min {domain_info['password_policy']['min_length']} chars")
        
        return domain_info
    
    def enumerate_users(self) -> List[ADUser]:
        """Enumerate domain users"""
        print(f"\n👥 Enumerating users...")
        
        if not self.session_data.get('authenticated'):
            print("❌ Not authenticated!")
            return []
        
        # Simulate user enumeration
        self.users = [
            ADUser(
                username="administrator",
                distinguished_name="CN=Administrator,CN=Users,DC=corp,DC=local",
                enabled=True,
                admin_count=True,
                member_of=["CN=Domain Admins,CN=Users,DC=corp,DC=local"]
            ),
            ADUser(
                username="svc_sql",
                distinguished_name="CN=SQL Service,CN=Users,DC=corp,DC=local",
                enabled=True,
                spn=["MSSQLSvc/sql01.corp.local:1433"],
                member_of=["CN=Service Accounts,CN=Users,DC=corp,DC=local"]
            ),
            ADUser(
                username="jsmith",
                distinguished_name="CN=John Smith,CN=Users,DC=corp,DC=local",
                enabled=True,
                preauth_required=False,  # Vulnerable to AS-REP roasting
                member_of=["CN=Developers,CN=Users,DC=corp,DC=local"]
            ),
            ADUser(
                username="admin_backup",
                distinguished_name="CN=Admin Backup,CN=Users,DC=corp,DC=local",
                enabled=False,  # Disabled but still risky
                admin_count=True,
                member_of=["CN=Domain Admins,CN=Users,DC=corp,DC=local"]
            )
        ]
        
        print(f"   Found {len(self.users)} users")
        
        # Identify findings
        for user in self.users:
            if user.admin_count and user.enabled:
                self.findings.append(ADFinding(
                    finding_id=f"AD-ADMIN-{user.username}",
                    title=f"Admin Account: {user.username}",
                    severity="info",
                    description=f"User {user.username} has adminCount=1",
                    affected_object=user.distinguished_name,
                    attack_type="recon",
                    remediation="Monitor admin account usage",
                    cvss_score=0.0
                ))
            
            if not user.preauth_required:
                self.findings.append(ADFinding(
                    finding_id=f"AD-ASREP-{user.username}",
                    title=f"AS-REP Roasting: {user.username}",
                    severity="high",
                    description=f"User {user.username} does not require Kerberos preauth",
                    affected_object=user.distinguished_name,
                    attack_type="asrep_roasting",
                    remediation="Enable 'Do not require Kerberos preauthentication'",
                    cvss_score=7.5,
                    references=["https://attack.mitre.org/techniques/T1558/004/"]
                ))
            
            if user.spn:
                self.findings.append(ADFinding(
                    finding_id=f"AD-KERBEROAST-{user.username}",
                    title=f"Kerberoasting: {user.username}",
                    severity="high",
                    description=f"User {user.username} has SPN: {', '.join(user.spn)}",
                    affected_object=user.distinguished_name,
                    attack_type="kerberoasting",
                    remediation="Use strong passwords for service accounts (25+ chars)",
                    cvss_score=7.5,
                    references=["https://attack.mitre.org/techniques/T1558/003/"]
                ))
        
        print(f"   Generated {len(self.findings)} findings")
        
        return self.users
    
    def enumerate_computers(self) -> List[ADComputer]:
        """Enumerate domain computers"""
        print(f"\n💻 Enumerating computers...")
        
        if not self.session_data.get('authenticated'):
            print("❌ Not authenticated!")
            return []
        
        # Simulate computer enumeration
        self.computers = [
            ADComputer(
                hostname="DC01",
                dns_hostname="dc01.corp.local",
                enabled=True,
                operating_system="Windows Server 2019",
                last_logon=datetime.utcnow().isoformat()
            ),
            ADComputer(
                hostname="SQL01",
                dns_hostname="sql01.corp.local",
                enabled=True,
                operating_system="Windows Server 2016",
                last_logon=datetime.utcnow().isoformat()
            ),
            ADComputer(
                hostname="WS-001",
                dns_hostname="ws-001.corp.local",
                enabled=True,
                operating_system="Windows 10 Enterprise",
                last_logon=datetime.utcnow().isoformat()
            )
        ]
        
        print(f"   Found {len(self.computers)} computers")
        
        return self.computers
    
    def kerberoast(self) -> List[Dict]:
        """Request TGS for SPN accounts (Kerberoasting)"""
        print(f"\n🎯 Performing Kerberoasting...")
        
        if not self.session_data.get('authenticated'):
            print("❌ Not authenticated!")
            return []
        
        # Find users with SPN
        spn_users = [u for u in self.users if u.spn]
        
        if not spn_users:
            print("   No users with SPN found")
            return []
        
        tickets = []
        for user in spn_users:
            ticket = {
                "username": user.username,
                "spn": user.spn[0],
                "ticket_hash": f"$krb5tgs$23$*{user.username}$CORP.LOCAL$${user.spn[0]}$...",
                "crackable": True,
                "estimated_crack_time": "2-48 hours (depending on password complexity)"
            }
            tickets.append(ticket)
            print(f"   ✓ Got TGS for {user.username} ({user.spn[0]})")
        
        # Add finding
        self.findings.append(ADFinding(
            finding_id="AD-KERBEROAST-SUMMARY",
            title="Kerberoasting Successful",
            severity="critical" if len(tickets) > 0 else "info",
            description=f"Successfully requested TGS for {len(tickets)} service accounts",
            affected_object="Multiple service accounts",
            attack_type="kerberoasting",
            remediation="Use Managed Service Accounts (MSA) or strong passwords (25+ chars)",
            cvss_score=8.0,
            evidence={"tickets_obtained": len(tickets)}
        ))
        
        print(f"   Total tickets: {len(tickets)}")
        print(f"   ⚠️  Hashes can be cracked offline with Hashcat")
        
        return tickets
    
    def asrep_roast(self) -> List[Dict]:
        """AS-REP Roasting for users without preauth"""
        print(f"\n🎯 Performing AS-REP Roasting...")
        
        if not self.session_data.get('authenticated'):
            print("❌ Not authenticated!")
            return []
        
        # Find users without preauth
        no_preauth_users = [u for u in self.users if not u.preauth_required]
        
        if not no_preauth_users:
            print("   No users without preauth found")
            return []
        
        hashes = []
        for user in no_preauth_users:
            hash_data = {
                "username": user.username,
                "hash": f"$krb5asrep$23${user.username}@CORP.LOCAL:...",
                "crackable": True
            }
            hashes.append(hash_data)
            print(f"   ✓ Got AS-REP hash for {user.username}")
        
        print(f"   Total hashes: {len(hashes)}")
        
        return hashes
    
    def dcsync(self, target_user: str = "krbtgt") -> Dict:
        """Simulate DCSync attack"""
        print(f"\n☠️  Performing DCSync attack...")
        print(f"   Target: {target_user}")
        
        if not self.session_data.get('authenticated'):
            print("❌ Not authenticated!")
            return {}
        
        # DCSync requires specific permissions
        required_perms = ["Replicating Directory Changes", 
                         "Replicating Directory Changes All"]
        
        # Simulate successful DCSync
        result = {
            "success": True,
            "target": target_user,
            "hash_type": "NTLM",
            "hash": "aad3b435b51404eeaad3b435b51404ee:8846f7eaee8fb117ad06bdd830b7586c",
            "description": f"Successfully extracted hash for {target_user}"
        }
        
        # Critical finding
        self.findings.append(ADFinding(
            finding_id="AD-DCSYNC-CRITICAL",
            title="DCSync Attack Successful",
            severity="critical",
            description=f"Successfully extracted hash for {target_user} via DCSync",
            affected_object=target_user,
            attack_type="dcsync",
            remediation="Remove 'Replicating Directory Changes' permissions from non-DC accounts",
            cvss_score=10.0,
            evidence={"hash_extracted": True},
            references=["https://attack.mitre.org/techniques/T1003/006/"]
        ))
        
        print(f"   ✅ DCSync successful!")
        print(f"   Hash: {result['hash'][:50]}...")
        print(f"   ⚠️  CRITICAL: This allows Golden Ticket creation!")
        
        return result
    
    def check_acl_abuse(self) -> List[ADFinding]:
        """Check for ACL abuse opportunities"""
        print(f"\n🔍 Checking for ACL abuse...")
        
        if not self.session_data.get('authenticated'):
            print("❌ Not authenticated!")
            return []
        
        # Simulate ACL findings
        acl_findings = [
            ADFinding(
                finding_id="AD-ACL-GENERICALL",
                title="GenericAll on User Object",
                severity="high",
                description="User has GenericAll permissions on sensitive user object",
                affected_object="CN=Target User,CN=Users,DC=corp,DC=local",
                attack_type="acl_abuse",
                remediation="Remove unnecessary GenericAll permissions",
                cvss_score=8.0,
                references=["https://attack.mitre.org/techniques/T1222/001/"]
            ),
            ADFinding(
                finding_id="AD-ACL-FORCECHANGEPWD",
                title="Force Change Password",
                severity="high",
                description="User can force change password of privileged account",
                affected_object="CN=Admin User,CN=Users,DC=corp,DC=local",
                attack_type="acl_abuse",
                remediation="Remove ForceChangePassword permissions",
                cvss_score=7.5
            ),
            ADFinding(
                finding_id="AD-ACL-WRITESERVICEPRINCIPALNAME",
                title="Write ServicePrincipalName",
                severity="critical",
                description="User can write SPN to privileged account (resource-based constrained delegation)",
                affected_object="CN=Server Account,CN=Users,DC=corp,DC=local",
                attack_type="acl_abuse",
                remediation="Remove WriteServicePrincipalName permissions from non-admin accounts",
                cvss_score=9.0,
                references=["https://attack.mitre.org/techniques/T1550/002/"]
            )
        ]
        
        self.findings.extend(acl_findings)
        print(f"   Found {len(acl_findings)} ACL abuse opportunities")
        
        return acl_findings
    
    def check_laps(self) -> Dict:
        """Check for LAPS (Local Administrator Password Solution)"""
        print(f"\n🔐 Checking LAPS configuration...")
        
        if not self.session_data.get('authenticated'):
            print("❌ Not authenticated!")
            return {}
        
        # Simulate LAPS check
        laps_info = {
            "laps_deployed": True,
            "password_protection": True,
            "read_permissions": [
                {"group": "Domain Admins", "count": 5},
                {"group": "Help Desk", "count": 12}  # Potential finding
            ],
            "expiration_policy": "30 days",
            "complexity": "14 characters, complex"
        }
        
        # Check for overly permissive read access
        for perm in laps_info['read_permissions']:
            if perm['group'] not in ['Domain Admins', 'Enterprise Admins']:
                self.findings.append(ADFinding(
                    finding_id="AD-LAPS-PERMISSIONS",
                    title="LAPS Password Read Permissions",
                    severity="medium",
                    description=f"Group {perm['group']} can read LAPS passwords",
                    affected_object="LAPS Configuration",
                    attack_type="laps_dump",
                    remediation="Restrict LAPS password read to Domain Admins only",
                    cvss_score=6.5
                ))
        
        print(f"   LAPS Deployed: {laps_info['laps_deployed']}")
        print(f"   Password Complexity: {laps_info['complexity']}")
        print(f"   Expiration: {laps_info['expiration_policy']}")
        
        return laps_info
    
    def generate_bloodhound_data(self) -> Dict:
        """Generate BloodHound-compatible data"""
        print(f"\n🐕 Generating BloodHound data...")
        
        # Simulate BloodHound output
        bloodhound_data = {
            "meta": {
                "type": "bloodhound",
                "count": 4,
                "version": 4
            },
            "data": {
                "users": len(self.users),
                "computers": len(self.computers),
                "groups": len(self.groups),
                "sessions": 0,
                "trusts": 1,
                "gpos": 0
            },
            "attack_paths": [
                {
                    "name": "Kerberoasting Path",
                    "from": "Domain User",
                    "to": "Domain Admin",
                    "steps": 3,
                    "severity": "high"
                },
                {
                    "name": "ACL Abuse Path",
                    "from": "Compromised User",
                    "to": "Domain Admin",
                    "steps": 2,
                    "severity": "critical"
                }
            ]
        }
        
        print(f"   Users: {bloodhound_data['data']['users']}")
        print(f"   Computers: {bloodhound_data['data']['computers']}")
        print(f"   Attack Paths: {len(bloodhound_data['attack_paths'])}")
        
        return bloodhound_data
    
    def generate_report(self) -> Dict:
        """Generate AD assessment report"""
        print(f"\n📄 Generating AD assessment report...")
        
        # Count findings by severity
        severity_counts = {
            'critical': sum(1 for f in self.findings if f.severity == 'critical'),
            'high': sum(1 for f in self.findings if f.severity == 'high'),
            'medium': sum(1 for f in self.findings if f.severity == 'medium'),
            'low': sum(1 for f in self.findings if f.severity == 'low'),
            'info': sum(1 for f in self.findings if f.severity == 'info')
        }
        
        report = {
            "agent_id": self.agent_id,
            "timestamp": datetime.utcnow().isoformat(),
            "domain": self.domain,
            "dc_ip": self.dc_ip,
            "summary": {
                "users_enumerated": len(self.users),
                "computers_enumerated": len(self.computers),
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
            "attack_techniques": list(set(f.attack_type for f in self.findings)),
            "recommendations": self._generate_recommendations()
        }
        
        return report
    
    def _generate_recommendations(self) -> List[str]:
        """Generate security recommendations"""
        recommendations = []
        
        # Based on findings
        if any(f.attack_type == 'kerberoasting' for f in self.findings):
            recommendations.append("CRITICAL: Implement 25+ character passwords for all service accounts")
        
        if any(f.attack_type == 'asrep_roasting' for f in self.findings):
            recommendations.append("HIGH: Enable Kerberos preauthentication for all users")
        
        if any(f.attack_type == 'dcsync' for f in self.findings):
            recommendations.append("CRITICAL: Remove 'Replicating Directory Changes' from non-DC accounts")
        
        if any(f.attack_type == 'acl_abuse' for f in self.findings):
            recommendations.append("HIGH: Audit and remove unnecessary ACL permissions")
        
        # General recommendations
        recommendations.append("Deploy LAPS for all workstations and servers")
        recommendations.append("Implement tiered admin model")
        recommendations.append("Enable Windows Defender ATP or equivalent")
        recommendations.append("Monitor for BloodHound usage")
        recommendations.append("Regular AD security assessments")
        
        return recommendations
    
    def get_status(self) -> Dict:
        """Get agent status"""
        return {
            "agent_id": self.agent_id,
            "domain": self.domain,
            "authenticated": self.session_data.get('authenticated', False),
            "users_found": len(self.users),
            "computers_found": len(self.computers),
            "findings_count": len(self.findings),
            "last_activity": self.session_data.get('timestamp', 'N/A')
        }


# Example usage
if __name__ == "__main__":
    # Create AD agent
    ad_agent = ADAgent(domain="CORP.LOCAL", dc_ip="192.168.1.10")
    
    # Authenticate (simulated)
    ad_agent.authenticate(
        username="pentester@CORP.LOCAL",
        password="SecurePassword123!"
    )
    
    # Enumerate domain
    domain_info = ad_agent.enumerate_domain()
    
    # Enumerate users
    users = ad_agent.enumerate_users()
    
    # Enumerate computers
    computers = ad_agent.enumerate_computers()
    
    # Kerberoasting
    tickets = ad_agent.kerberoast()
    
    # AS-REP Roasting
    asrep_hashes = ad_agent.asrep_roast()
    
    # DCSync (simulated)
    dcsync_result = ad_agent.dcsync(target_user="krbtgt")
    
    # Check ACL abuse
    acl_findings = ad_agent.check_acl_abuse()
    
    # Check LAPS
    laps_info = ad_agent.check_laps()
    
    # Generate BloodHound data
    bh_data = ad_agent.generate_bloodhound_data()
    
    # Generate report
    report = ad_agent.generate_report()
    
    print(f"\n{'='*60}")
    print(f"🏢 ACTIVE DIRECTORY ASSESSMENT COMPLETE")
    print(f"{'='*60}")
    print(f"Domain: {report['domain']}")
    print(f"Users: {report['summary']['users_enumerated']}")
    print(f"Computers: {report['summary']['computers_enumerated']}")
    print(f"Total Findings: {report['summary']['total_findings']}")
    print(f"  Critical: {report['summary']['critical']}")
    print(f"  High: {report['summary']['high']}")
    print(f"  Medium: {report['summary']['medium']}")
    print(f"  Low: {report['summary']['low']}")
    print(f"\nAttack Techniques Used:")
    for technique in report['attack_techniques']:
        print(f"  • {technique}")
    print(f"\nTop Recommendations:")
    for rec in report['recommendations'][:5]:
        print(f"  • {rec}")
