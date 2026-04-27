#!/usr/bin/env python3
"""
🎯 KaliAgent v4.4.0 - Phase 11: Automated Threat Hunting
Lateral Movement Hunting Playbook

Hunting for lateral movement activities:
- SMB share abuse
- RDP hopping
- WMI abuse
- PowerShell remoting
- PsExec detection
- SSH key abuse

Author: KaliAgent Team
Started: April 27, 2026
Status: Alpha (0.1.0)
"""

import logging
from typing import List, Dict
from datetime import datetime
from dataclasses import dataclass, field

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger('LateralMovementHunt')


@dataclass
class LateralMovementFinding:
    """Lateral movement finding"""
    technique: str
    severity: str
    confidence: float
    description: str
    source_system: str = ""
    target_system: str = ""
    mitre_attack: str = ""
    evidence: List[str] = field(default_factory=list)
    recommended_actions: List[str] = field(default_factory=list)


class LateralMovementHunter:
    """
    Lateral Movement Hunting Playbook
    
    MITRE ATT&CK: TA0008 (Lateral Movement)
    
    Techniques:
    - T1021: Remote Services
    - T1021.002: SMB/Windows Admin Shares
    - T1021.001: Remote Desktop Protocol
    - T1047: Windows Management Instrumentation
    - T1021.006: SSH
    - T1563.002: RDP Hijacking
    """
    
    VERSION = "0.1.0"
    
    def __init__(self):
        self.findings: List[LateralMovementFinding] = []
        logger.info(f"🔄 Lateral Movement Hunter v{self.VERSION}")
    
    def detect_smb_abuse(self, logs: List[Dict]) -> List[LateralMovementFinding]:
        """Detect SMB share abuse"""
        logger.info("🔍 Hunting for SMB Abuse...")
        
        findings = []
        
        # Look for:
        # - Event ID 5140 (SMB share access)
        # - Admin share access (C$, ADMIN$)
        # - Unusual source systems accessing shares
        
        for log in logs:
            if log.get('event_id') == 5140:
                share_name = log.get('share_name', '')
                
                if share_name in ['C$', 'ADMIN$', 'IPC$']:
                    finding = LateralMovementFinding(
                        technique='SMB Admin Share Abuse',
                        severity='high',
                        confidence=0.75,
                        description=f'Admin share access detected: {share_name}',
                        source_system=log.get('source_ip', 'unknown'),
                        target_system=log.get('dest_ip', 'unknown'),
                        mitre_attack='T1021.002',
                        evidence=[
                            f"Share: {share_name}",
                            f"Source: {log.get('source_ip')}",
                            f"User: {log.get('user')}"
                        ],
                        recommended_actions=[
                            'Review source system for compromise',
                            'Disable admin shares if not needed',
                            'Implement network segmentation',
                            'Monitor SMB traffic (port 445)',
                            'Restrict lateral movement paths'
                        ]
                    )
                    findings.append(finding)
        
        logger.info(f"   SMB abuse indicators: {len(findings)}")
        return findings
    
    def detect_rdp_hopping(self, logs: List[Dict]) -> List[LateralMovementFinding]:
        """Detect RDP hopping"""
        logger.info("🔍 Hunting for RDP Hopping...")
        
        findings = []
        
        # Look for:
        # - Event ID 4624 (RDP logon, type 10)
        # - Multiple RDP sessions from same source
        # - RDP to sensitive systems
        
        rdp_logons = {}
        
        for log in logs:
            if log.get('event_id') == 4624 and log.get('logon_type') == 10:
                source = log.get('source_ip', 'unknown')
                if source not in rdp_logons:
                    rdp_logons[source] = []
                rdp_logons[source].append(log)
        
        for source, logons in rdp_logons.items():
            if len(logons) >= 3:  # Multiple RDP sessions
                targets = set(l.get('dest_ip') for l in logons)
                finding = LateralMovementFinding(
                    technique='RDP Hopping',
                    severity='high',
                    confidence=0.8,
                    description=f'Multiple RDP sessions from {source} to {len(targets)} systems',
                    source_system=source,
                    target_system=', '.join(targets),
                    mitre_attack='T1021.001',
                    evidence=[
                        f"Source: {source}",
                        f"Targets: {', '.join(targets)}",
                        f"Sessions: {len(logons)}"
                    ],
                    recommended_actions=[
                        'Review source system',
                        'Implement RDP gateway',
                        'Enable NLA (Network Level Authentication)',
                        'Restrict RDP access with firewalls',
                        'Use jump servers for admin access'
                    ]
                )
                findings.append(finding)
        
        logger.info(f"   RDP hopping indicators: {len(findings)}")
        return findings
    
    def detect_wmi_abuse(self, logs: List[Dict]) -> List[LateralMovementFinding]:
        """Detect WMI abuse"""
        logger.info("🔍 Hunting for WMI Abuse...")
        
        findings = []
        
        # Look for:
        # - WMI process creation (Event ID 5857/5858)
        # - Win32_Process.Create
        # - Remote WMI activity
        
        wmi_patterns = ['Win32_Process', 'wmic', 'wmi', 'Get-WmiObject', 'Invoke-WmiMethod']
        
        for log in logs:
            command = log.get('command', '').lower()
            process = log.get('process_name', '').lower()
            
            if any(p in command or p in process for p in wmi_patterns):
                if log.get('remote', False):  # Remote WMI
                    finding = LateralMovementFinding(
                        technique='WMI Abuse',
                        severity='high',
                        confidence=0.85,
                        description='Remote WMI activity detected',
                        source_system=log.get('source_ip', 'unknown'),
                        target_system=log.get('dest_ip', 'unknown'),
                        mitre_attack='T1047',
                        evidence=[
                            f"Command: {command[:100]}",
                            f"Process: {process}",
                            f"Remote: True"
                        ],
                        recommended_actions=[
                            'Review source system',
                            'Disable remote WMI if not needed',
                            'Monitor WMI activity',
                            'Restrict WMI access',
                            'Enable WMI logging'
                        ]
                    )
                    findings.append(finding)
        
        logger.info(f"   WMI abuse indicators: {len(findings)}")
        return findings
    
    def detect_psexec(self, logs: List[Dict]) -> List[LateralMovementFinding]:
        """Detect PsExec usage"""
        logger.info("🔍 Hunting for PsExec...")
        
        findings = []
        
        # Look for:
        # - Service creation with PSEXESVC
        # - Event ID 7045 (service installation)
        # - Named pipe PSEXESVC
        
        for log in logs:
            service = log.get('service_name', '').lower()
            process = log.get('process_name', '').lower()
            
            if 'psexesvc' in service or 'psexec' in process:
                finding = LateralMovementFinding(
                    technique='PsExec',
                    severity='high',
                    confidence=0.9,
                    description='PsExec usage detected',
                    source_system=log.get('source_ip', 'unknown'),
                    target_system=log.get('dest_ip', 'unknown'),
                    mitre_attack='T1021.002',
                    evidence=[
                        f"Service: {service}",
                        f"Process: {process}"
                    ],
                    recommended_actions=[
                        'Review if PsExec is authorized',
                        'Monitor for unauthorized PsExec',
                        'Consider restricting PsExec',
                        'Enable Sysmon for better visibility',
                        'Implement application whitelisting'
                    ]
                )
                findings.append(finding)
        
        logger.info(f"   PsExec indicators: {len(findings)}")
        return findings
    
    def detect_powershell_remoting(self, logs: List[Dict]) -> List[LateralMovementFinding]:
        """Detect PowerShell remoting abuse"""
        logger.info("🔍 Hunting for PowerShell Remoting...")
        
        findings = []
        
        # Look for:
        # - PowerShell remoting sessions
        # - WinRM activity
        # - Event ID 4688 with PowerShell
        
        ps_patterns = ['Enter-PSSession', 'Invoke-Command', 'New-PSSession', 'winrm']
        
        for log in logs:
            command = log.get('command', '').lower()
            
            if any(p in command for p in ps_patterns):
                finding = LateralMovementFinding(
                    technique='PowerShell Remoting',
                    severity='medium',
                    confidence=0.7,
                    description='PowerShell remoting activity detected',
                    source_system=log.get('source_ip', 'unknown'),
                    target_system=log.get('dest_ip', 'unknown'),
                    mitre_attack='T1021.006',
                    evidence=[f"Command: {command[:100]}"],
                    recommended_actions=[
                        'Review if activity is authorized',
                        'Enable PowerShell logging',
                        'Monitor WinRM traffic (5985/5986)',
                        'Restrict PowerShell remoting',
                        'Implement constrained language mode'
                    ]
                )
                findings.append(finding)
        
        logger.info(f"   PowerShell remoting indicators: {len(findings)}")
        return findings
    
    def detect_ssh_abuse(self, logs: List[Dict]) -> List[LateralMovementFinding]:
        """Detect SSH key abuse"""
        logger.info("🔍 Hunting for SSH Abuse...")
        
        findings = []
        
        # Look for:
        # - SSH from unusual sources
        # - Multiple SSH sessions
        # - SSH to sensitive systems
        
        ssh_logons = {}
        
        for log in logs:
            if log.get('service') == 'ssh' or log.get('port') == 22:
                source = log.get('source_ip', 'unknown')
                if source not in ssh_logons:
                    ssh_logons[source] = []
                ssh_logons[source].append(log)
        
        for source, logons in ssh_logons.items():
            if len(logons) >= 5:  # Multiple SSH sessions
                targets = set(l.get('dest_ip') for l in logons)
                finding = LateralMovementFinding(
                    technique='SSH Abuse',
                    severity='medium',
                    confidence=0.65,
                    description=f'Multiple SSH sessions from {source}',
                    source_system=source,
                    target_system=', '.join(targets),
                    mitre_attack='T1021.004',
                    evidence=[
                        f"Source: {source}",
                        f"Targets: {', '.join(targets)}",
                        f"Sessions: {len(logons)}"
                    ],
                    recommended_actions=[
                        'Review SSH key management',
                        'Implement SSH certificate authority',
                        'Monitor SSH traffic',
                        'Restrict SSH access',
                        'Use jump servers'
                    ]
                )
                findings.append(finding)
        
        logger.info(f"   SSH abuse indicators: {len(findings)}")
        return findings
    
    def run_full_hunt(self, logs: List[Dict]) -> List[LateralMovementFinding]:
        """Run complete lateral movement hunt"""
        logger.info("🎯 Starting Lateral Movement Hunt...")
        
        all_findings = []
        
        all_findings.extend(self.detect_smb_abuse(logs))
        all_findings.extend(self.detect_rdp_hopping(logs))
        all_findings.extend(self.detect_wmi_abuse(logs))
        all_findings.extend(self.detect_psexec(logs))
        all_findings.extend(self.detect_powershell_remoting(logs))
        all_findings.extend(self.detect_ssh_abuse(logs))
        
        logger.info(f"✅ Hunt complete. Total findings: {len(all_findings)}")
        
        return all_findings
    
    def generate_report(self, findings: List[LateralMovementFinding]) -> str:
        """Generate hunt report"""
        report = []
        report.append("=" * 70)
        report.append("🔄 LATERAL MOVEMENT HUNT REPORT")
        report.append("=" * 70)
        report.append(f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        report.append(f"Total Findings: {len(findings)}")
        report.append("")
        
        if findings:
            report.append("DETAILED FINDINGS:")
            report.append("-" * 70)
            
            for i, f in enumerate(findings, 1):
                report.append(f"\n{i}. [{f.severity.upper()}] {f.technique}")
                report.append(f"   MITRE ATT&CK: {f.mitre_attack}")
                report.append(f"   Source: {f.source_system}")
                report.append(f"   Target: {f.target_system}")
                report.append(f"   Confidence: {f.confidence:.0%}")
                report.append(f"   Description: {f.description}")
                report.append(f"   Recommended Actions:")
                for action in f.recommended_actions:
                    report.append(f"     • {action}")
        
        report.append("")
        report.append("=" * 70)
        
        return "\n".join(report)


def main():
    """Main entry point"""
    print("""
╔═══════════════════════════════════════════════════════════════╗
║     🔄 LATERAL MOVEMENT HUNTING PLAYBOOK                     ║
║                    Phase 11: Alpha 0.1.0                      ║
╚═══════════════════════════════════════════════════════════════╝

MITRE ATT&CK: TA0008 (Lateral Movement)
    """)
    
    hunter = LateralMovementHunter()
    
    # Simulated logs
    logs = [
        {'event_id': 5140, 'share_name': 'C$', 'source_ip': '192.168.1.100', 'user': 'admin'},
        {'event_id': 4624, 'logon_type': 10, 'source_ip': '192.168.1.100', 'dest_ip': '192.168.1.101'},
        {'event_id': 4624, 'logon_type': 10, 'source_ip': '192.168.1.100', 'dest_ip': '192.168.1.102'},
        {'event_id': 4624, 'logon_type': 10, 'source_ip': '192.168.1.100', 'dest_ip': '192.168.1.103'},
        {'event_id': 7045, 'service_name': 'PSEXESVC'},
        {'command': 'Invoke-Command -ComputerName DC01 -ScriptBlock {whoami}', 'source_ip': '192.168.1.100'},
    ]
    
    findings = hunter.run_full_hunt(logs)
    print("\n" + hunter.generate_report(findings))


if __name__ == "__main__":
    main()
