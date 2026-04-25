#!/usr/bin/env python3
"""
KaliAgent v4 - Phase 8: Mobile Application Security Agent
Android APK and iOS IPA analysis and exploitation
"""

import json
import time
from datetime import datetime
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field
from enum import Enum


class MobilePlatform(Enum):
    """Mobile platforms"""
    ANDROID = "android"
    IOS = "ios"


class AttackType(Enum):
    """Mobile attack types"""
    RECON = "recon"
    MANIFEST_ANALYSIS = "manifest_analysis"
    DECOMPILE = "decompile"
    HARDCODED_SECRETS = "hardcoded_secrets"
    INSECURE_STORAGE = "insecure_storage"
    SSL_PINNING_BYPASS = "ssl_pinning_bypass"
    ROOT_JAILBREAK_BYPASS = "root_jailbreak_bypass"
    INTENT_INJECTION = "intent_injection"
    DEEP_LINK_ABUSE = "deep_link_abuse"
    KEYCHAIN_EXTRACTION = "keychain_extraction"


@dataclass
class MobileFinding:
    """Mobile security finding"""
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
    owasp_mobile: str = ""  # OWASP Mobile Top 10 reference


@dataclass
class APKInfo:
    """Android APK information"""
    package_name: str
    version_name: str
    version_code: int
    min_sdk: int
    target_sdk: int
    permissions: List[str] = field(default_factory=list)
    components: Dict[str, List] = field(default_factory=dict)
    certificates: List[str] = field(default_factory=list)


@dataclass
class IPAInfo:
    """iOS IPA information"""
    bundle_id: str
    version: str
    min_ios: str
    entitlements: Dict[str, Any] = field(default_factory=dict)
    frameworks: List[str] = field(default_factory=list)
    url_schemes: List[str] = field(default_factory=list)


class MobileAgent:
    """
    Mobile Application Security Testing Agent
    
    Android Capabilities:
    - APK decompilation
    - Manifest analysis
    - Permission audit
    - Component exposure
    - Hardcoded secrets
    - SSL pinning bypass
    - Root detection bypass
    - Intent injection
    
    iOS Capabilities:
    - IPA analysis
    - Entitlements audit
    - Keychain extraction
    - URL scheme abuse
    - Jailbreak detection bypass
    - SSL pinning bypass
    
    ⚠️ WARNING: For authorized testing ONLY
    """
    
    def __init__(self, platform: MobilePlatform = MobilePlatform.ANDROID):
        self.platform = platform
        self.agent_id = f"mobile-{platform.value}-{datetime.now().strftime('%Y%m%d%H%M%S')}"
        self.session_data = {}
        self.findings: List[MobileFinding] = []
        self.apk_info: Optional[APKInfo] = None
        self.ipa_info: Optional[IPAInfo] = None
        self Decompiled_code = []
        self.secrets = []
        
        print(f"📱 Mobile Agent initialized: {self.agent_id}")
        print(f"   Platform: {platform.value}")
    
    def analyze_apk(self, apk_path: str) -> APKInfo:
        """Analyze Android APK file"""
        print(f"\n🤖 Analyzing Android APK...")
        print(f"   Path: {apk_path}")
        
        # Simulate APK analysis
        self.apk_info = APKInfo(
            package_name="com.example.vulnerable_app",
            version_name="2.1.0",
            version_code=21,
            min_sdk=21,
            target_sdk=33,
            permissions=[
                "android.permission.INTERNET",
                "android.permission.CAMERA",
                "android.permission.READ_CONTACTS",
                "android.permission.WRITE_EXTERNAL_STORAGE",
                "android.permission.READ_SMS",
                "android.permission.RECEIVE_SMS",
                "android.permission.ACCESS_FINE_LOCATION"
            ],
            components={
                "activities": [
                    {"name": ".MainActivity", "exported": True},
                    {"name": ".LoginActivity", "exported": True},
                    {"name": ".SettingsActivity", "exported": False}
                ],
                "services": [
                    {"name": ".BackgroundService", "exported": True},
                    {"name": ".SyncService", "exported": True}
                ],
                "receivers": [
                    {"name": ".SMSReceiver", "exported": True},
                    {"name": ".BootReceiver", "exported": True}
                ],
                "providers": [
                    {"name": ".DatabaseProvider", "exported": True}
                ]
            },
            certificates=[
                {"issuer": "CN=Example Corp", "valid_from": "2024-01-01", "valid_to": "2027-01-01"}
            ]
        )
        
        print(f"   Package: {self.apk_info.package_name}")
        print(f"   Version: {self.apk_info.version_name}")
        print(f"   Permissions: {len(self.apk_info.permissions)}")
        print(f"   Activities: {len(self.apk_info.components['activities'])}")
        
        # Analyze for security issues
        self._analyze_apk_security()
        
        return self.apk_info
    
    def _analyze_apk_security(self):
        """Analyze APK for security vulnerabilities"""
        
        # Check for dangerous permissions
        dangerous_perms = [
            "READ_SMS", "RECEIVE_SMS", "SEND_SMS",
            "READ_CONTACTS", "WRITE_CONTACTS",
            "ACCESS_FINE_LOCATION", "CAMERA",
            "RECORD_AUDIO", "READ_CALL_LOG"
        ]
        
        for perm in self.apk_info.permissions:
            if any(dangerous in perm for dangerous in dangerous_perms):
                self.findings.append(MobileFinding(
                    finding_id=f"ANDROID-PERM-{perm.split('.')[-1]}",
                    title=f"Dangerous Permission: {perm}",
                    severity="medium",
                    description=f"App requests {perm} permission",
                    affected_object=self.apk_info.package_name,
                    attack_type="recon",
                    remediation="Remove permission if not essential, implement runtime permissions",
                    cvss_score=5.5,
                    owasp_mobile="M7: Client Code Quality"
                ))
        
        # Check for exported components
        for component_type, components in self.apk_info.components.items():
            exported = [c for c in components if c.get('exported', False)]
            if exported:
                severity = "high" if component_type == "providers" else "medium"
                self.findings.append(MobileFinding(
                    finding_id=f"ANDROID-EXPORT-{component_type.upper()}",
                    title=f"Exported {component_type.title()}",
                    severity=severity,
                    description=f"{len(exported)} {component_type} are exported and accessible by other apps",
                    affected_object=self.apk_info.package_name,
                    attack_type="intent_injection",
                    remediation=f"Set android:exported='false' unless inter-app communication is required",
                    cvss_score=7.0 if severity == "high" else 5.5,
                    owasp_mobile="M1: Improper Platform Usage"
                ))
        
        # Check for debug flag
        if self.apk_info.target_sdk < 31:
            self.findings.append(MobileFinding(
                finding_id="ANDROID-DEBUG-001",
                title="Debuggable in Release",
                severity="high",
                description="App may be debuggable (targetSdkVersion < 31)",
                affected_object=self.apk_info.package_name,
                attack_type="recon",
                remediation="Set android:debuggable='false' in release builds",
                cvss_score=6.5,
                owasp_mobile="M8: Code Tampering"
            ))
    
    def analyze_ipa(self, ipa_path: str) -> IPAInfo:
        """Analyze iOS IPA file"""
        print(f"\n🍎 Analyzing iOS IPA...")
        print(f"   Path: {ipa_path}")
        
        # Simulate IPA analysis
        self.ipa_info = IPAInfo(
            bundle_id="com.example.vulnerable_ios",
            version="3.2.1",
            min_ios="14.0",
            entitlements={
                "com.apple.security.application-groups": ["group.com.example.app"],
                "com.apple.developer.associated-domains": ["example.com"],
                "com.apple.security.network.client": True,
                "keychain-access-groups": ["$(AppIdentifierPrefix)com.example.app"]
            },
            frameworks=[
                "UIKit.framework",
                "Foundation.framework",
                "Security.framework",
                "CoreData.framework"
            ],
            url_schemes=[
                "exampleapp://",
                "exampleapp-auth://",
                "exampleapp-deep://payment"
            ]
        )
        
        print(f"   Bundle ID: {self.ipa_info.bundle_id}")
        print(f"   Version: {self.ipa_info.version}")
        print(f"   URL Schemes: {len(self.ipa_info.url_schemes)}")
        
        # Analyze for security issues
        self._analyze_ipa_security()
        
        return self.ipa_info
    
    def _analyze_ipa_security(self):
        """Analyze IPA for security vulnerabilities"""
        
        # Check for ATS (App Transport Security)
        self.findings.append(MobileFinding(
            finding_id="IOS-ATS-001",
            title="App Transport Security Configuration",
            severity="medium",
            description="ATS may be disabled or configured with exceptions",
            affected_object=self.ipa_info.bundle_id,
            attack_type="recon",
            remediation="Enable ATS with default settings, avoid NSAllowsArbitraryLoads",
            cvss_score=6.0,
            owasp_mobile="M3: Insecure Communication"
        ))
        
        # Check URL schemes
        if len(self.ipa_info.url_schemes) > 0:
            self.findings.append(MobileFinding(
                finding_id=f"IOS-URLSCHEME-001",
                title="Custom URL Schemes Defined",
                severity="medium",
                description=f"{len(self.ipa_info.url_schemes)} custom URL schemes may be vulnerable to injection",
                affected_object=self.ipa_info.bundle_id,
                attack_type="deep_link_abuse",
                remediation="Validate all URL scheme inputs, implement authentication for sensitive actions",
                cvss_score=6.5,
                owasp_mobile="M1: Improper Platform Usage"
            ))
        
        # Check for jailbreak detection
        self.findings.append(MobileFinding(
            finding_id="IOS-JAILBREAK-001",
            title="Jailbreak Detection Required",
            severity="medium",
            description="App should implement jailbreak detection",
            affected_object=self.ipa_info.bundle_id,
            attack_type="root_jailbreak_bypass",
            remediation="Implement jailbreak detection using multiple checks",
            cvss_score=5.5,
            owasp_mobile="M8: Code Tampering"
        ))
    
    def extract_hardcoded_secrets(self) -> List[Dict]:
        """Extract hardcoded secrets from app"""
        print(f"\n🔍 Extracting hardcoded secrets...")
        
        # Simulate secret extraction
        if self.platform == MobilePlatform.ANDROID:
            secrets = [
                {
                    "type": "api_key",
                    "value": "AIzaSyDxxxxxxxxxxxxxxxxxxxxxxxxxxxx",
                    "location": "res/values/strings.xml",
                    "service": "Google Maps API",
                    "risk": "high"
                },
                {
                    "type": "aws_key",
                    "value": "AKIAIOSFODNN7EXAMPLE",
                    "location": "com/example/app/Config.java",
                    "service": "AWS",
                    "risk": "critical"
                },
                {
                    "type": "jwt_secret",
                    "value": "super-secret-jwt-key-123",
                    "location": "com/example/app/AuthManager.java",
                    "service": "JWT",
                    "risk": "critical"
                },
                {
                    "type": "database_password",
                    "value": "Pr0d_P@ssw0rd!",
                    "location": "com/example/app/DatabaseHelper.java",
                    "service": "Production DB",
                    "risk": "critical"
                }
            ]
        else:  # iOS
            secrets = [
                {
                    "type": "api_key",
                    "value": "sk_xxxxxxxxxxxxxxxxxxxxxxxx",
                    "location": "AppDelegate.swift",
                    "service": "Stripe API",
                    "risk": "critical"
                },
                {
                    "type": "firebase_config",
                    "value": "AIzaSyDxxxxxxxxxxxxxxxxxxxxxxxxxxxx",
                    "location": "GoogleService-Info.plist",
                    "service": "Firebase",
                    "risk": "high"
                }
            ]
        
        self.secrets = secrets
        
        # Generate findings
        for secret in secrets:
            self.findings.append(MobileFinding(
                finding_id=f"SECRET-{secret['type'].upper()}-{secret['service'].split()[0]}",
                title=f"Hardcoded Secret: {secret['service']}",
                severity="critical" if secret['risk'] == 'critical' else "high",
                description=f"{secret['type']} found in {secret['location']}",
                affected_object=self.apk_info.package_name if self.apk_info else self.ipa_info.bundle_id,
                attack_type="hardcoded_secrets",
                remediation="Remove hardcoded secrets, use secure backend or key management service",
                cvss_score=9.0 if secret['risk'] == 'critical' else 7.5,
                evidence={"type": secret['type'], "service": secret['service']},
                owasp_mobile="M2: Insecure Data Storage"
            ))
        
        print(f"   Found {len(secrets)} hardcoded secrets")
        print(f"   Critical: {sum(1 for s in secrets if s['risk'] == 'critical')}")
        
        return secrets
    
    def check_insecure_storage(self) -> List[MobileFinding]:
        """Check for insecure data storage"""
        print(f"\n💾 Checking insecure storage...")
        
        storage_findings = []
        
        if self.platform == MobilePlatform.ANDROID:
            # Android storage issues
            issues = [
                {
                    "name": "External Storage",
                    "severity": "high",
                    "description": "Sensitive data stored in external storage",
                    "location": "/sdcard/app_data/"
                },
                {
                    "name": "SharedPreferences",
                    "severity": "medium",
                    "description": "Unencrypted SharedPreferences with sensitive data",
                    "location": "/data/data/package/shared_prefs/"
                },
                {
                    "name": "SQLite Database",
                    "severity": "medium",
                    "description": "Unencrypted SQLite database",
                    "location": "/data/data/package/databases/"
                }
            ]
        else:  # iOS
            # iOS storage issues
            issues = [
                {
                    "name": "NSUserDefaults",
                    "severity": "medium",
                    "description": "Sensitive data in NSUserDefaults (not encrypted)",
                    "location": "Library/Preferences/"
                },
                {
                    "name": "CoreData",
                    "severity": "medium",
                    "description": "Unencrypted CoreData database",
                    "location": "Application Support/"
                },
                {
                    "name": "File System",
                    "severity": "high",
                    "description": "Sensitive files stored without protection",
                    "location": "Documents/"
                }
            ]
        
        for issue in issues:
            finding = MobileFinding(
                finding_id=f"STORAGE-{issue['name'].replace(' ', '-').upper()}",
                title=f"Insecure Storage: {issue['name']}",
                severity=issue['severity'],
                description=issue['description'],
                affected_object=issue['location'],
                attack_type="insecure_storage",
                remediation=self._get_storage_remediation(issue['name']),
                cvss_score=7.0 if issue['severity'] == 'high' else 5.5,
                evidence={"location": issue['location']},
                owasp_mobile="M2: Insecure Data Storage"
            )
            storage_findings.append(finding)
            self.findings.append(finding)
            print(f"   ⚠️  {issue['name']}: {issue['description']}")
        
        return storage_findings
    
    def _get_storage_remediation(self, storage_type: str) -> str:
        """Get remediation for storage issue"""
        remediations = {
            "External Storage": "Use internal storage or encrypt files before storing externally",
            "SharedPreferences": "Use EncryptedSharedPreferences or Android Keystore",
            "SQLite Database": "Implement SQLCipher for database encryption",
            "NSUserDefaults": "Use Keychain for sensitive data storage",
            "CoreData": "Enable CoreData encryption with SQLCipher",
            "File System": "Use Data Protection API for file encryption"
        }
        return remediations.get(storage_type, "Implement proper encryption")
    
    def ssl_pinning_check(self) -> MobileFinding:
        """Check SSL pinning implementation"""
        print(f"\n🔒 Checking SSL pinning...")
        
        # Simulate SSL pinning check
        pinning_status = {
            "implemented": False,
            "method": None,
            "bypassable": True
        }
        
        finding = MobileFinding(
            finding_id="SSL-PINNING-001",
            title="SSL Pinning Not Implemented",
            severity="high",
            description="App does not implement SSL/TLS certificate pinning",
            affected_object=self.apk_info.package_name if self.apk_info else self.ipa_info.bundle_id,
            attack_type="ssl_pinning_bypass",
            remediation="Implement certificate pinning using OkHttp (Android) or NSURLSession (iOS)",
            cvss_score=7.0,
            evidence=pinning_status,
            owasp_mobile="M3: Insecure Communication"
        )
        
        self.findings.append(finding)
        print(f"   ⚠️  SSL Pinning: Not implemented")
        print(f"   Vulnerable to MITM attacks")
        
        return finding
    
    def root_jailbreak_detection_check(self) -> MobileFinding:
        """Check root/jailbreak detection"""
        print(f"\n🔍 Checking root/jailbreak detection...")
        
        detection_status = {
            "implemented": False,
            "methods": [],
            "bypassable": True
        }
        
        finding = MobileFinding(
            finding_id="ROOT-DETECT-001",
            title="No Root/Jailbreak Detection",
            severity="medium",
            description="App does not detect rooted/jailbroken devices",
            affected_object=self.apk_info.package_name if self.apk_info else self.ipa_info.bundle_id,
            attack_type="root_jailbreak_bypass",
            remediation="Implement root/jailbreak detection using multiple checks",
            cvss_score=6.0,
            evidence=detection_status,
            owasp_mobile="M8: Code Tampering"
        )
        
        self.findings.append(finding)
        print(f"   ⚠️  Root/Jailbreak Detection: Not implemented")
        
        return finding
    
    def bypass_ssl_pinning(self) -> Dict:
        """Simulate SSL pinning bypass"""
        print(f"\n🔓 Attempting SSL pinning bypass...")
        
        if self.platform == MobilePlatform.ANDROID:
            bypass_method = "Frida script with okhttp3.CertificatePinner hook"
            tools = ["frida", "objection", "justtrustme"]
        else:
            bypass_method = "Frida script with NSURLSession hook"
            tools = ["frida", "ssl-kill-switch2", "proxyman"]
        
        result = {
            "success": True,
            "method": bypass_method,
            "tools_used": tools,
            "time_taken": "5-10 minutes",
            "mitm_possible": True
        }
        
        print(f"   ✅ Bypass successful using {bypass_method}")
        print(f"   Tools: {', '.join(tools)}")
        print(f"   ⚠️  MITM attacks now possible")
        
        return result
    
    def bypass_root_jailbreak_detection(self) -> Dict:
        """Simulate root/jailbreak detection bypass"""
        print(f"\n🔓 Attempting root/jailbreak detection bypass...")
        
        if self.platform == MobilePlatform.ANDROID:
            bypass_method = "Frida script hiding root binaries and packages"
            detection_evasion = [
                "Hide su binary",
                "Hide Magisk package",
                "Hide root management apps",
                "Spoof build tags"
            ]
        else:
            bypass_method = "Jailbreak detection bypass via Frida"
            detection_evasion = [
                "Hide /Applications/Cydia.app",
                "Hide libsubstitute.dylib",
                "Spoof system files"
            ]
        
        result = {
            "success": True,
            "method": bypass_method,
            "evasion_techniques": detection_evasion,
            "tools": ["frida", "shadow", "iHide"]
        }
        
        print(f"   ✅ Bypass successful")
        print(f"   Method: {bypass_method}")
        print(f"   Techniques: {len(detection_evasion)}")
        
        return result
    
    def generate_report(self) -> Dict:
        """Generate mobile security assessment report"""
        print(f"\n📄 Generating mobile security report...")
        
        severity_counts = {
            'critical': sum(1 for f in self.findings if f.severity == 'critical'),
            'high': sum(1 for f in self.findings if f.severity == 'high'),
            'medium': sum(1 for f in self.findings if f.severity == 'medium'),
            'low': sum(1 for f in self.findings if f.severity == 'low')
        }
        
        report = {
            "agent_id": self.agent_id,
            "timestamp": datetime.utcnow().isoformat(),
            "platform": self.platform.value,
            "app_info": {
                "package": self.apk_info.package_name if self.apk_info else self.ipa_info.bundle_id,
                "version": self.apk_info.version_name if self.apk_info else self.ipa_info.version
            },
            "summary": {
                "total_findings": len(self.findings),
                "secrets_found": len(self.secrets),
                **severity_counts
            },
            "critical_findings": [
                {
                    "id": f.finding_id,
                    "title": f.title,
                    "cvss": f.cvss_score,
                    "owasp": f.owasp_mobile
                }
                for f in self.findings if f.severity == 'critical'
            ],
            "owasp_mobile_coverage": list(set(f.owasp_mobile for f in self.findings if f.owasp_mobile)),
            "recommendations": self._generate_recommendations()
        }
        
        return report
    
    def _generate_recommendations(self) -> List[str]:
        """Generate security recommendations"""
        recommendations = []
        
        if any(f.attack_type == 'hardcoded_secrets' for f in self.findings):
            recommendations.append("CRITICAL: Remove all hardcoded secrets, use secure backend")
        
        if any(f.attack_type == 'ssl_pinning_bypass' for f in self.findings):
            recommendations.append("HIGH: Implement SSL/TLS certificate pinning")
        
        if any(f.attack_type == 'insecure_storage' for f in self.findings):
            recommendations.append("HIGH: Encrypt all sensitive data at rest")
        
        if any(f.attack_type == 'root_jailbreak_bypass' for f in self.findings):
            recommendations.append("MEDIUM: Implement root/jailbreak detection")
        
        # General recommendations
        recommendations.append("Use ProGuard/R8 (Android) or Bitcode (iOS) for obfuscation")
        recommendations.append("Implement certificate pinning")
        recommendations.append("Use Android Keystore or iOS Keychain for secrets")
        recommendations.append("Regular security assessments and penetration testing")
        
        return recommendations
    
    def get_status(self) -> Dict:
        """Get agent status"""
        return {
            "agent_id": self.agent_id,
            "platform": self.platform.value,
            "app_analyzed": bool(self.apk_info or self.ipa_info),
            "secrets_found": len(self.secrets),
            "findings_count": len(self.findings),
            "last_activity": self.session_data.get('timestamp', 'N/A')
        }


# Example usage
if __name__ == "__main__":
    # Create Android agent
    android_agent = MobileAgent(platform=MobilePlatform.ANDROID)
    
    # Analyze APK
    apk_info = android_agent.analyze_apk("/path/to/app.apk")
    
    # Extract secrets
    secrets = android_agent.extract_hardcoded_secrets()
    
    # Check storage
    storage = android_agent.check_insecure_storage()
    
    # SSL pinning check
    ssl_check = android_agent.ssl_pinning_check()
    
    # Bypass SSL pinning
    ssl_bypass = android_agent.bypass_ssl_pinning()
    
    # Root detection check
    root_check = android_agent.root_jailbreak_detection_check()
    
    # Bypass root detection
    root_bypass = android_agent.bypass_root_jailbreak_detection()
    
    # Generate report
    report = android_agent.generate_report()
    
    print(f"\n{'='*60}")
    print(f"📱 MOBILE SECURITY ASSESSMENT COMPLETE")
    print(f"{'='*60}")
    print(f"Platform: {report['platform']}")
    print(f"App: {report['app_info']['package']}")
    print(f"Version: {report['app_info']['version']}")
    print(f"Total Findings: {report['summary']['total_findings']}")
    print(f"  Critical: {report['summary']['critical']}")
    print(f"  High: {report['summary']['high']}")
    print(f"  Medium: {report['summary']['medium']}")
    print(f"Secrets Found: {report['summary']['secrets_found']}")
    print(f"\nOWASP Mobile Coverage:")
    for owasp in report['owasp_mobile_coverage']:
        print(f"  • {owasp}")
    print(f"\nTop Recommendations:")
    for rec in report['recommendations'][:5]:
        print(f"  • {rec}")
