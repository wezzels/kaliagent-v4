#!/usr/bin/env python3
"""
KaliAgent v4 - Phase 8: Evasion & Persistence Agent
AMSI bypass, AV evasion, persistence mechanisms, and rootkit detection
"""

import json
import time
from datetime import datetime
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field
from enum import Enum


class EvasionType(Enum):
    """Evasion technique types"""
    AMSI_BYPASS = "amsi_bypass"
    AV_EVASION = "av_evasion"
    EDR_EVASION = "edr_evasion"
    SANDBOX_EVASION = "sandbox_evasion"
    VM_DETECTION = "vm_detection"
    DEBUGGING_EVASION = "debugging_evasion"


class PersistenceType(Enum):
    """Persistence mechanism types"""
    REGISTRY = "registry"
    SCHEDULED_TASK = "scheduled_task"
    SERVICE = "service"
    STARTUP = "startup"
    WMI = "wmi_subscription"
    DLL_HIJACK = "dll_hijack"
    PROCESS_INJECTION = "process_injection"


@dataclass
class EvasionFinding:
    """Evasion/Persistence finding"""
    finding_id: str
    title: str
    severity: str
    description: str
    technique: str
    detection_method: str
    remediation: str
    cvss_score: float = 0.0
    evidence: Dict[str, Any] = field(default_factory=dict)
    references: List[str] = field(default_factory=list)
    mitre_attack: str = ""


class EvasionAgent:
    """
    Evasion & Persistence Testing Agent
    
    Evasion Capabilities:
    - AMSI bypass detection
    - AV signature evasion
    - EDR detection bypass
    - Sandbox evasion
    - VM detection
    - Debugging detection bypass
    
    Persistence Capabilities:
    - Registry run keys
    - Scheduled tasks
    - Windows services
    - Startup folder
    - WMI subscriptions
    - DLL hijacking
    - Process injection
    
    ⚠️ WARNING: For authorized testing ONLY
    """
    
    def __init__(self, target_os: str = "windows"):
        self.target_os = target_os
        self.agent_id = f"evasion-{datetime.now().strftime('%Y%m%d%H%M%S')}"
        self.session_data = {}
        self.findings: List[EvasionFinding] = []
        self.persistence_mechanisms = []
        self.evasion_techniques = []
        
        print(f"🎭 Evasion Agent initialized: {self.agent_id}")
        print(f"   Target OS: {target_os}")
    
    def check_amsi(self) -> Dict:
        """Check AMSI (Antimalware Scan Interface) status"""
        print(f"\n🔍 Checking AMSI status...")
        
        # Simulate AMSI check
        amsi_info = {
            "enabled": True,
            "version": "1.0",
            "bypassable": True,
            "known_bypasses": [
                "Memory patching",
                "COM hijacking",
                "Script block logging disable",
                "amsi.dll patching"
            ]
        }
        
        print(f"   AMSI Enabled: {amsi_info['enabled']}")
        print(f"   Version: {amsi_info['version']}")
        print(f"   Bypassable: {amsi_info['bypassable']}")
        
        # Generate finding
        self.findings.append(EvasionFinding(
            finding_id="EVASION-AMSI-001",
            title="AMSI Bypass Possible",
            severity="high",
            description="AMSI can be bypassed using known techniques",
            technique="amsi_bypass",
            detection_method="Monitor for amsi.dll memory modifications",
            remediation="Implement additional layers of defense, not just AMSI",
            cvss_score=7.5,
            evidence=amsi_info,
            references=["https://attack.mitre.org/techniques/T1562/001/"],
            mitre_attack="T1562.001"
        ))
        
        return amsi_info
    
    def bypass_amsi(self) -> Dict:
        """Simulate AMSI bypass"""
        print(f"\n🔓 Attempting AMSI bypass...")
        
        bypass_methods = [
            {
                "name": "Memory Patching",
                "success": True,
                "detection": "Low",
                "description": "Patch amsi.dll in memory to disable scanning"
            },
            {
                "name": "COM Hijacking",
                "success": True,
                "detection": "Medium",
                "description": "Hijack AMSI COM object to bypass scanning"
            },
            {
                "name": "Script Block Logging Disable",
                "success": True,
                "detection": "Low",
                "description": "Disable PowerShell script block logging"
            }
        ]
        
        for method in bypass_methods:
            print(f"   ✅ {method['name']}: {'Success' if method['success'] else 'Failed'}")
            self.evasion_techniques.append(method)
        
        result = {
            "success": True,
            "methods_used": len(bypass_methods),
            "detection_risk": "Low-Medium"
        }
        
        print(f"   ✅ AMSI bypass successful")
        print(f"   Methods: {len(bypass_methods)}")
        
        return result
    
    def check_av_evasion(self) -> Dict:
        """Check antivirus evasion techniques"""
        print(f"\n🔍 Checking AV evasion...")
        
        # Simulate AV check
        av_info = {
            "detected_av": ["Windows Defender", "Malwarebytes"],
            "realtime_protection": True,
            "cloud_protection": True,
            "behavioral_analysis": True,
            "evasion_possible": True
        }
        
        print(f"   Detected AV: {', '.join(av_info['detected_av'])}")
        print(f"   Realtime: {av_info['realtime_protection']}")
        print(f"   Cloud: {av_info['cloud_protection']}")
        
        # Evasion techniques
        evasion_methods = [
            {
                "name": "Obfuscation",
                "effectiveness": "Medium",
                "description": "Code obfuscation to evade signatures"
            },
            {
                "name": "Encryption",
                "effectiveness": "High",
                "description": "Encrypt payload, decrypt at runtime"
            },
            {
                "name": "Living off the Land",
                "effectiveness": "High",
                "description": "Use legitimate system tools (LOLBins)"
            },
            {
                "name": "Process Injection",
                "effectiveness": "High",
                "description": "Inject code into legitimate processes"
            }
        ]
        
        for method in evasion_methods:
            print(f"   ✅ {method['name']}: {method['effectiveness']} effectiveness")
            self.evasion_techniques.append(method)
        
        return av_info
    
    def check_edr_evasion(self) -> Dict:
        """Check EDR evasion techniques"""
        print(f"\n🔍 Checking EDR evasion...")
        
        # Simulate EDR check
        edr_info = {
            "detected_edr": ["CrowdStrike Falcon", "Microsoft Defender ATP"],
            "kernel_callbacks": True,
            "etw_enabled": True,
            "evasion_possible": True
        }
        
        print(f"   Detected EDR: {', '.join(edr_info['detected_edr'])}")
        print(f"   Kernel Callbacks: {edr_info['kernel_callbacks']}")
        print(f"   ETW Enabled: {edr_info['etw_enabled']}")
        
        # EDR evasion techniques
        evasion_methods = [
            {
                "name": "ETW Patching",
                "effectiveness": "High",
                "detection": "Medium",
                "description": "Patch ETW to disable event logging"
            },
            {
                "name": "Kernel Callback Removal",
                "effectiveness": "Critical",
                "detection": "High",
                "description": "Remove EDR kernel callbacks"
            },
            {
                "name": "Direct Syscalls",
                "effectiveness": "High",
                "detection": "Low",
                "description": "Use direct syscalls to bypass user-mode hooks"
            },
            {
                "name": "Sleep Obfuscation",
                "effectiveness": "Medium",
                "detection": "Low",
                "description": "Obfuscate memory during sleep"
            }
        ]
        
        for method in evasion_methods:
            print(f"   ⚠️  {method['name']}: {method['effectiveness']} (Detection: {method['detection']})")
        
        return edr_info
    
    def check_sandbox_evasion(self) -> Dict:
        """Check sandbox detection/evasion"""
        print(f"\n🔍 Checking sandbox evasion...")
        
        sandbox_checks = [
            {
                "name": "User Activity Check",
                "detectable": True,
                "description": "Check for mouse movements, keyboard input"
            },
            {
                "name": "Running Processes",
                "detectable": True,
                "description": "Check for sandbox-specific processes"
            },
            {
                "name": "Hardware Check",
                "detectable": True,
                "description": "Check CPU cores, RAM amount"
            },
            {
                "name": "Uptime Check",
                "detectable": True,
                "description": "Check system uptime (sandboxes often freshly booted)"
            }
        ]
        
        for check in sandbox_checks:
            print(f"   ✅ {check['name']}: {check['description']}")
        
        return {"sandbox_evasion_possible": True, "methods": len(sandbox_checks)}
    
    def check_vm_detection(self) -> Dict:
        """Check VM detection techniques"""
        print(f"\n🔍 Checking VM detection...")
        
        vm_checks = [
            {
                "name": "MAC Address Check",
                "detectable": True,
                "vm_indicators": ["08:00:27 (VirtualBox)", "00:0C:29 (VMware)"]
            },
            {
                "name": "BIOS/SMBIOS Check",
                "detectable": True,
                "vm_indicators": ["VirtualBox", "VMware", "QEMU"]
            },
            {
                "name": "Device Drivers",
                "detectable": True,
                "vm_indicators": ["vmmouse.sys", "vmhgfs.sys", "VBoxMouse.sys"]
            },
            {
                "name": "Registry Keys",
                "detectable": True,
                "vm_indicators": ["HKLM\\SOFTWARE\\VMware", "HKLM\\SOFTWARE\\Oracle\\VirtualBox"]
            }
        ]
        
        for check in vm_checks:
            print(f"   ✅ {check['name']}: {len(check['vm_indicators'])} indicators")
        
        return {"vm_detection_possible": True, "methods": len(vm_checks)}
    
    def enumerate_persistence(self) -> List[Dict]:
        """Enumerate persistence mechanisms"""
        print(f"\n🔍 Enumerating persistence mechanisms...")
        
        # Simulate persistence enumeration
        self.persistence_mechanisms = [
            {
                "type": "registry",
                "location": "HKCU\\Software\\Microsoft\\Windows\\CurrentVersion\\Run",
                "value": "MaliciousApp",
                "data": "C:\\Users\\victim\\AppData\\Local\\Temp\\malware.exe",
                "severity": "critical"
            },
            {
                "type": "scheduled_task",
                "name": "\\Microsoft\\Windows\\UpdateTask",
                "command": "C:\\Windows\\Temp\\backdoor.exe",
                "trigger": "At logon",
                "severity": "critical"
            },
            {
                "type": "service",
                "name": "WindowsUpdateService",
                "binary": "C:\\ProgramData\\svchost.exe",
                "start_type": "Automatic",
                "severity": "critical"
            },
            {
                "type": "startup",
                "location": "C:\\Users\\victim\\AppData\\Roaming\\Microsoft\\Windows\\Start Menu\\Programs\\Startup",
                "file": "update.lnk",
                "target": "C:\\Temp\\malware.exe",
                "severity": "high"
            },
            {
                "type": "wmi",
                "namespace": "root\\cimv2",
                "class": "Win32_Process",
                "query": "SELECT * FROM Win32_Process WHERE Name='explorer.exe'",
                "action": "C:\\Windows\\Temp\\implant.exe",
                "severity": "critical"
            }
        ]
        
        print(f"   Found {len(self.persistence_mechanisms)} persistence mechanisms")
        
        # Generate findings
        for mechanism in self.persistence_mechanisms:
            self.findings.append(EvasionFinding(
                finding_id=f"PERSISTENCE-{mechanism['type'].upper()}-{mechanism.get('name', mechanism.get('value', 'Unknown'))[:20]}",
                title=f"Persistence: {mechanism['type'].title()}",
                severity=mechanism['severity'],
                description=f"Malicious {mechanism['type']} found: {mechanism.get('name', mechanism.get('value', 'Unknown'))}",
                technique="persistence",
                detection_method=f"Monitor {mechanism['type']} creation/modification",
                remediation=self._get_persistence_remediation(mechanism['type']),
                cvss_score=9.0 if mechanism['severity'] == 'critical' else 7.5,
                evidence=mechanism,
                mitre_attack=self._get_mitre_persistence(mechanism['type'])
            ))
        
        return self.persistence_mechanisms
    
    def _get_persistence_remediation(self, persistence_type: str) -> str:
        """Get remediation for persistence mechanism"""
        remediations = {
            "registry": "Remove registry key, monitor for recreation with Sysmon",
            "scheduled_task": "Delete scheduled task, audit Task Scheduler logs",
            "service": "Stop and delete service, check service binary",
            "startup": "Remove startup item, check startup folder",
            "wmi": "Remove WMI subscription with Get-WmiObject, monitor WMI activity",
            "dll_hijack": "Restore legitimate DLL, implement DLL signing",
            "process_injection": "Terminate injected process, analyze memory dump"
        }
        return remediations.get(persistence_type, "Remove persistence mechanism")
    
    def _get_mitre_persistence(self, persistence_type: str) -> str:
        """Get MITRE ATT&CK technique ID"""
        mitre_ids = {
            "registry": "T1547.001",
            "scheduled_task": "T1053.005",
            "service": "T1543.003",
            "startup": "T1547.001",
            "wmi": "T1546.003",
            "dll_hijack": "T1574.001",
            "process_injection": "T1055"
        }
        return mitre_ids.get(persistence_type, "T1053")
    
    def check_dll_hijacking(self) -> List[EvasionFinding]:
        """Check for DLL hijacking opportunities"""
        print(f"\n🔍 Checking DLL hijacking opportunities...")
        
        dll_findings = []
        
        # Simulate DLL hijacking checks
        vulnerable_dlls = [
            {
                "dll": "wbemcomn.dll",
                "location": "C:\\Windows\\System32\\wbem\\",
                "hijackable": True,
                "severity": "critical"
            },
            {
                "dll": "propsys.dll",
                "location": "C:\\Windows\\System32\\",
                "hijackable": True,
                "severity": "high"
            },
            {
                "dll": "ntshrui.dll",
                "location": "C:\\Windows\\System32\\",
                "hijackable": False,
                "severity": "medium"
            }
        ]
        
        for dll in vulnerable_dlls:
            if dll['hijackable']:
                finding = EvasionFinding(
                    finding_id=f"DLL-HIJACK-{dll['dll'].split('.')[0].upper()}",
                    title=f"DLL Hijacking: {dll['dll']}",
                    severity=dll['severity'],
                    description=f"{dll['dll']} can be hijacked for code execution",
                    technique="dll_hijack",
                    detection_method="Monitor DLL loads from non-standard paths",
                    remediation="Implement DLL signing, use SafeDllSearchMode",
                    cvss_score=9.0 if dll['severity'] == 'critical' else 7.5,
                    evidence=dll,
                    mitre_attack="T1574.001"
                )
                dll_findings.append(finding)
                self.findings.append(finding)
                print(f"   ⚠️  {dll['dll']}: Hijackable")
            else:
                print(f"   ✅ {dll['dll']}: Protected")
        
        return dll_findings
    
    def check_process_injection(self) -> Dict:
        """Check process injection techniques"""
        print(f"\n🔍 Checking process injection...")
        
        injection_techniques = [
            {
                "name": "CreateRemoteThread",
                "detectable": True,
                "description": "Classic process injection"
            },
            {
                "name": "NtMapViewOfSection",
                "detectable": False,
                "description": "Section mapping injection"
            },
            {
                "name": "APC Injection",
                "detectable": True,
                "description": "Asynchronous Procedure Call injection"
            },
            {
                "name": "Process Hollowing",
                "detectable": False,
                "description": "Replace legitimate process code"
            },
            {
                "name": "DLL Injection",
                "detectable": True,
                "description": "Load DLL into remote process"
            }
        ]
        
        for technique in injection_techniques:
            print(f"   {'⚠️' if not technique['detectable'] else '✅'} {technique['name']}: {technique['description']}")
        
        return {"injection_techniques": len(injection_techniques), "detectable": sum(1 for t in injection_techniques if t['detectable'])}
    
    def generate_report(self) -> Dict:
        """Generate evasion & persistence assessment report"""
        print(f"\n📄 Generating evasion & persistence report...")
        
        severity_counts = {
            'critical': sum(1 for f in self.findings if f.severity == 'critical'),
            'high': sum(1 for f in self.findings if f.severity == 'high'),
            'medium': sum(1 for f in self.findings if f.severity == 'medium'),
            'low': sum(1 for f in self.findings if f.severity == 'low')
        }
        
        report = {
            "agent_id": self.agent_id,
            "timestamp": datetime.utcnow().isoformat(),
            "target_os": self.target_os,
            "summary": {
                "total_findings": len(self.findings),
                "evasion_techniques": len(self.evasion_techniques),
                "persistence_mechanisms": len(self.persistence_mechanisms),
                **severity_counts
            },
            "critical_findings": [
                {
                    "id": f.finding_id,
                    "title": f.title,
                    "cvss": f.cvss_score,
                    "mitre": f.mitre_attack
                }
                for f in self.findings if f.severity == 'critical'
            ],
            "mitre_coverage": list(set(f.mitre_attack for f in self.findings if f.mitre_attack)),
            "recommendations": self._generate_recommendations()
        }
        
        return report
    
    def _generate_recommendations(self) -> List[str]:
        """Generate security recommendations"""
        recommendations = []
        
        if any(f.technique == "amsi_bypass" for f in self.findings):
            recommendations.append("HIGH: Implement defense-in-depth, not just AMSI")
        
        if any(f.technique == "persistence" for f in self.findings):
            recommendations.append("CRITICAL: Monitor persistence mechanisms with Sysmon")
        
        if any(f.technique == "dll_hijack" for f in self.findings):
            recommendations.append("HIGH: Implement DLL signing and SafeDllSearchMode")
        
        # General recommendations
        recommendations.append("Deploy EDR with behavioral analysis")
        recommendations.append("Enable PowerShell script block logging")
        recommendations.append("Monitor for LOLBin abuse")
        recommendations.append("Implement application whitelisting")
        recommendations.append("Regular threat hunting exercises")
        
        return recommendations
    
    def get_status(self) -> Dict:
        """Get agent status"""
        return {
            "agent_id": self.agent_id,
            "target_os": self.target_os,
            "evasion_techniques": len(self.evasion_techniques),
            "persistence_mechanisms": len(self.persistence_mechanisms),
            "findings_count": len(self.findings),
            "last_activity": self.session_data.get('timestamp', 'N/A')
        }


# Example usage
if __name__ == "__main__":
    # Create evasion agent
    agent = EvasionAgent(target_os="windows")
    
    # Check AMSI
    amsi = agent.check_amsi()
    
    # Bypass AMSI
    amsi_bypass = agent.bypass_amsi()
    
    # Check AV evasion
    av = agent.check_av_evasion()
    
    # Check EDR evasion
    edr = agent.check_edr_evasion()
    
    # Check sandbox evasion
    sandbox = agent.check_sandbox_evasion()
    
    # Check VM detection
    vm = agent.check_vm_detection()
    
    # Enumerate persistence
    persistence = agent.enumerate_persistence()
    
    # Check DLL hijacking
    dll_hijack = agent.check_dll_hijacking()
    
    # Check process injection
    injection = agent.check_process_injection()
    
    # Generate report
    report = agent.generate_report()
    
    print(f"\n{'='*60}")
    print(f"🎭 EVASION & PERSISTENCE ASSESSMENT COMPLETE")
    print(f"{'='*60}")
    print(f"Target OS: {report['target_os']}")
    print(f"Total Findings: {report['summary']['total_findings']}")
    print(f"  Critical: {report['summary']['critical']}")
    print(f"  High: {report['summary']['high']}")
    print(f"  Medium: {report['summary']['medium']}")
    print(f"Evasion Techniques: {report['summary']['evasion_techniques']}")
    print(f"Persistence Mechanisms: {report['summary']['persistence_mechanisms']}")
    print(f"\nMITRE ATT&CK Coverage:")
    for mitre in report['mitre_coverage'][:10]:
        print(f"  • {mitre}")
    print(f"\nTop Recommendations:")
    for rec in report['recommendations'][:5]:
        print(f"  • {rec}")
