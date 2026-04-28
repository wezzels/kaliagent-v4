#!/usr/bin/env python3
"""
🎯 KaliAgent v4.4.0 - Phase 11: Automated Threat Hunting
Persistence Hunting Playbook

Hunting for persistence mechanisms:
- Registry run keys
- Scheduled tasks
- Startup folders
- Service installation
- WMI subscriptions
- Browser extensions
- Login scripts

Author: KaliAgent Team
Started: April 28, 2026
Status: Alpha (0.1.0)
"""

import logging
from typing import List, Dict
from datetime import datetime
from dataclasses import dataclass, field

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger('PersistenceHunt')


@dataclass
class PersistenceFinding:
    """Persistence finding"""
    technique: str
    severity: str
    confidence: float
    description: str
    location: str = ""
    payload: str = ""
    mitre_attack: str = ""
    evidence: List[str] = field(default_factory=list)
    recommended_actions: List[str] = field(default_factory=list)


class PersistenceHunter:
    """
    Persistence Hunting Playbook
    
    MITRE ATT&CK: TA0003 (Persistence)
    
    Techniques:
    - T1547: Boot or Logon Autostart Execution
    - T1053: Scheduled Task/Job
    - T1543: Create or Modify System Process
    - T1546: Event Triggered Execution
    - T1176: Browser Extensions
    - T1037: Boot or Logon Initialization Scripts
    """
    
    VERSION = "0.1.0"
    
    # Suspicious registry run keys
    SUSPICIOUS_RUN_KEYS = [
        r'HKLM\Software\Microsoft\Windows\CurrentVersion\Run',
        r'HKCU\Software\Microsoft\Windows\CurrentVersion\Run',
        r'HKLM\Software\Microsoft\Windows\CurrentVersion\RunOnce',
        r'HKCU\Software\Microsoft\Windows\CurrentVersion\RunOnce',
        r'HKLM\Software\Microsoft\Windows NT\CurrentVersion\Winlogon',
    ]
    
    # Suspicious scheduled task patterns
    SUSPICIOUS_TASK_PATTERNS = [
        'powershell', 'cmd', 'wscript', 'cscript',
        'mshta', 'regsvr32', 'rundll32',
        'certutil', 'bitsadmin', 'msiexec',
        'hidden', 'bypass', 'encodedcommand',
        '-nop', '-w hidden', '-enc'
    ]
    
    # Known persistence locations
    PERSISTENCE_LOCATIONS = [
        'Startup folder',
        'Registry Run keys',
        'Scheduled Tasks',
        'Services',
        'WMI subscriptions',
        'Browser extensions',
        'Shell extensions',
        'Credential providers',
        'LSA providers',
        'Winlogon helpers',
    ]
    
    def __init__(self):
        self.findings: List[PersistenceFinding] = []
        logger.info(f"🔄 Persistence Hunter v{self.VERSION}")
    
    def detect_registry_persistence(self, logs: List[Dict]) -> List[PersistenceFinding]:
        """Detect registry-based persistence"""
        logger.info("🔍 Hunting for Registry Persistence...")
        
        findings = []
        
        # Registry modification events
        reg_events = [4657, 4658]  # Registry key/value modified
        
        for log in logs:
            event_id = log.get('event_id')
            key_name = log.get('registry_key', '').lower()
            value_name = log.get('registry_value', '').lower()
            data = log.get('registry_data', '').lower()
            
            # Check for run key modifications
            if any(run_key.lower() in key_name for run_key in self.SUSPICIOUS_RUN_KEYS):
                # Check for suspicious payloads
                is_suspicious = any(
                    pattern in data or pattern in value_name 
                    for pattern in self.SUSPICIOUS_TASK_PATTERNS
                )
                
                severity = 'high' if is_suspicious else 'medium'
                confidence = 0.8 if is_suspicious else 0.6
                
                finding = PersistenceFinding(
                    technique='Registry Run Keys',
                    severity=severity,
                    confidence=confidence,
                    description=f'Registry run key modification detected',
                    location=key_name,
                    payload=data[:200] if data else 'Unknown',
                    mitre_attack='T1547.001',
                    evidence=[
                        f"Key: {key_name}",
                        f"Value: {value_name}",
                        f"Data: {data[:100]}",
                        f"User: {log.get('user', 'unknown')}"
                    ],
                    recommended_actions=[
                        'Verify if modification is authorized',
                        'Check payload destination',
                        'Scan file for malware',
                        'Review user activity',
                        'Consider removing if unauthorized'
                    ]
                )
                findings.append(finding)
        
        logger.info(f"   Registry persistence: {len(findings)}")
        return findings
    
    def detect_scheduled_tasks(self, logs: List[Dict]) -> List[PersistenceFinding]:
        """Detect scheduled task persistence"""
        logger.info("🔍 Hunting for Scheduled Task Persistence...")
        
        findings = []
        
        # Task creation events
        task_events = [4698, 4700, 4701]  # Task created/enabled/disabled
        
        for log in logs:
            event_id = log.get('event_id')
            task_name = log.get('task_name', '').lower()
            command = log.get('task_command', '').lower()
            trigger = log.get('task_trigger', '').lower()
            
            if event_id == 4698:  # Task created
                # Check for suspicious patterns
                is_suspicious = any(
                    pattern in command or pattern in task_name
                    for pattern in self.SUSPICIOUS_TASK_PATTERNS
                )
                
                # Check for hidden tasks
                is_hidden = 'hidden' in command or 'hidden' in task_name
                
                severity = 'high' if is_suspicious else 'medium' if is_hidden else 'low'
                confidence = 0.85 if is_suspicious else 0.65
                
                finding = PersistenceFinding(
                    technique='Scheduled Task',
                    severity=severity,
                    confidence=confidence,
                    description=f'Scheduled task created: {task_name}',
                    location=task_name,
                    payload=command[:200] if command else 'Unknown',
                    mitre_attack='T1053.005',
                    evidence=[
                        f"Task Name: {task_name}",
                        f"Command: {command[:100]}",
                        f"Trigger: {trigger}",
                        f"Creator: {log.get('user', 'unknown')}"
                    ],
                    recommended_actions=[
                        'Verify if task is authorized',
                        'Review task command',
                        'Check task trigger conditions',
                        'Scan associated files',
                        'Disable if unauthorized'
                    ]
                )
                findings.append(finding)
        
        logger.info(f"   Scheduled task persistence: {len(findings)}")
        return findings
    
    def detect_service_persistence(self, logs: List[Dict]) -> List[PersistenceFinding]:
        """Detect service-based persistence"""
        logger.info("🔍 Hunting for Service Persistence...")
        
        findings = []
        
        # Service installation events
        service_events = [7045, 4697]  # Service installed
        
        for log in logs:
            event_id = log.get('event_id')
            service_name = log.get('service_name', '').lower()
            service_path = log.get('service_path', '').lower()
            service_type = log.get('service_type', '').lower()
            
            if event_id in service_events:
                # Check for suspicious patterns
                is_suspicious = any(
                    pattern in service_path or pattern in service_name
                    for pattern in self.SUSPICIOUS_TASK_PATTERNS
                )
                
                # Check for unusual service types
                is_unusual = 'user' in service_type or 'interactive' in service_type
                
                severity = 'high' if is_suspicious else 'medium' if is_unusual else 'low'
                
                finding = PersistenceFinding(
                    technique='Service Installation',
                    severity=severity,
                    confidence=0.75,
                    description=f'Service installed: {service_name}',
                    location=service_name,
                    payload=service_path[:200] if service_path else 'Unknown',
                    mitre_attack='T1543.003',
                    evidence=[
                        f"Service Name: {service_name}",
                        f"Service Path: {service_path[:100]}",
                        f"Service Type: {service_type}",
                        f"Installer: {log.get('user', 'unknown')}"
                    ],
                    recommended_actions=[
                        'Verify if service is legitimate',
                        'Check service binary signature',
                        'Review service permissions',
                        'Scan binary for malware',
                        'Stop and remove if unauthorized'
                    ]
                )
                findings.append(finding)
        
        logger.info(f"   Service persistence: {len(findings)}")
        return findings
    
    def detect_wmi_persistence(self, logs: List[Dict]) -> List[PersistenceFinding]:
        """Detect WMI-based persistence"""
        logger.info("🔍 Hunting for WMI Persistence...")
        
        findings = []
        
        # WMI event consumer creation
        wmi_events = [5857, 5858, 5859, 5860, 5861]
        
        for log in logs:
            event_id = log.get('event_id')
            
            if event_id in wmi_events:
                query = log.get('wmi_query', '').lower()
                consumer = log.get('wmi_consumer', '').lower()
                
                is_suspicious = any(
                    pattern in query or pattern in consumer
                    for pattern in self.SUSPICIOUS_TASK_PATTERNS
                )
                
                severity = 'high' if is_suspicious else 'medium'
                
                finding = PersistenceFinding(
                    technique='WMI Subscription',
                    severity=severity,
                    confidence=0.8,
                    description='WMI event consumer created',
                    location='WMI Repository',
                    payload=query[:200] if query else 'Unknown',
                    mitre_attack='T1546.003',
                    evidence=[
                        f"Event ID: {event_id}",
                        f"Query: {query[:100]}",
                        f"Consumer: {consumer}",
                        f"Creator: {log.get('user', 'unknown')}"
                    ],
                    recommended_actions=[
                        'Investigate WMI subscription',
                        'Check associated query',
                        'Review consumer details',
                        'Remove malicious subscription',
                        'Monitor for recreation'
                    ]
                )
                findings.append(finding)
        
        logger.info(f"   WMI persistence: {len(findings)}")
        return findings
    
    def detect_startup_folder(self, logs: List[Dict]) -> List[PersistenceFinding]:
        """Detect startup folder persistence"""
        logger.info("🔍 Hunting for Startup Folder Persistence...")
        
        findings = []
        
        # File creation in startup folders
        startup_paths = [
            'startup',
            'start menu\\programs\\startup',
            'shell:startup',
            'shell:common startup'
        ]
        
        for log in logs:
            file_path = log.get('file_path', '').lower()
            operation = log.get('operation', '').lower()
            
            if any(path in file_path for path in startup_paths):
                if operation in ['create', 'write', 'modify']:
                    file_name = log.get('file_name', '').lower()
                    
                    # Check for suspicious extensions
                    suspicious_ext = ['.vbs', '.vbe', '.js', '.jse', '.bat', '.cmd', '.ps1', '.wsf']
                    is_suspicious = any(file_name.endswith(ext) for ext in suspicious_ext)
                    
                    severity = 'high' if is_suspicious else 'medium'
                    
                    finding = PersistenceFinding(
                        technique='Startup Folder',
                        severity=severity,
                        confidence=0.7,
                        description=f'File added to startup: {file_name}',
                        location=file_path,
                        payload=file_path,
                        mitre_attack='T1547.001',
                        evidence=[
                            f"File: {file_name}",
                            f"Path: {file_path}",
                            f"Operation: {operation}",
                            f"User: {log.get('user', 'unknown')}"
                        ],
                        recommended_actions=[
                            'Verify if file is authorized',
                            'Scan file for malware',
                            'Review file contents',
                            'Remove if unauthorized',
                            'Monitor folder for changes'
                        ]
                    )
                    findings.append(finding)
        
        logger.info(f"   Startup folder persistence: {len(findings)}")
        return findings
    
    def detect_browser_extensions(self, logs: List[Dict]) -> List[PersistenceFinding]:
        """Detect browser extension persistence"""
        logger.info("🔍 Hunting for Browser Extension Persistence...")
        
        findings = []
        
        # Browser extension installation
        browser_events = [
            'chrome_extension',
            'firefox_addon',
            'edge_extension'
        ]
        
        for log in logs:
            event_type = log.get('event_type', '').lower()
            
            if any(browser in event_type for browser in browser_events):
                extension_name = log.get('extension_name', 'Unknown')
                extension_id = log.get('extension_id', 'Unknown')
                source = log.get('source', 'Unknown')
                
                # Check for unknown/suspicious sources
                is_suspicious = source not in ['chrome_web_store', 'firefox_addons', 'edge_store']
                
                severity = 'medium' if is_suspicious else 'low'
                
                finding = PersistenceFinding(
                    technique='Browser Extension',
                    severity=severity,
                    confidence=0.6,
                    description=f'Browser extension installed: {extension_name}',
                    location=extension_name,
                    payload=f"ID: {extension_id}",
                    mitre_attack='T1176',
                    evidence=[
                        f"Extension: {extension_name}",
                        f"ID: {extension_id}",
                        f"Source: {source}",
                        f"Browser: {event_type.split('_')[0]}",
                        f"User: {log.get('user', 'unknown')}"
                    ],
                    recommended_actions=[
                        'Verify if extension is authorized',
                        'Review extension permissions',
                        'Check extension source',
                        'Remove if suspicious',
                        'Implement extension policies'
                    ]
                )
                findings.append(finding)
        
        logger.info(f"   Browser extension persistence: {len(findings)}")
        return findings
    
    def run_full_hunt(self, logs: List[Dict]) -> List[PersistenceFinding]:
        """Run complete persistence hunt"""
        logger.info("🎯 Starting Persistence Hunt...")
        
        all_findings = []
        
        all_findings.extend(self.detect_registry_persistence(logs))
        all_findings.extend(self.detect_scheduled_tasks(logs))
        all_findings.extend(self.detect_service_persistence(logs))
        all_findings.extend(self.detect_wmi_persistence(logs))
        all_findings.extend(self.detect_startup_folder(logs))
        all_findings.extend(self.detect_browser_extensions(logs))
        
        logger.info(f"✅ Hunt complete. Total findings: {len(all_findings)}")
        
        return all_findings
    
    def generate_report(self, findings: List[PersistenceFinding]) -> str:
        """Generate hunt report"""
        report = []
        report.append("=" * 70)
        report.append("🔄 PERSISTENCE HUNT REPORT")
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
                report.append(f"   Location: {f.location}")
                report.append(f"   Payload: {f.payload[:100]}")
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
║     🔄 PERSISTENCE HUNTING PLAYBOOK                          ║
║                    Phase 11: Alpha 0.1.0                      ║
╚═══════════════════════════════════════════════════════════════╝

MITRE ATT&CK: TA0003 (Persistence)
    """)
    
    hunter = PersistenceHunter()
    
    # Simulated logs
    logs = [
        {'event_id': 4657, 'registry_key': 'HKLM\\Software\\Microsoft\\Windows\\CurrentVersion\\Run', 'registry_value': 'Malware', 'registry_data': 'C:\\temp\\malware.exe', 'user': 'admin'},
        {'event_id': 4698, 'task_name': 'UpdateCheck', 'task_command': 'powershell -w hidden -enc SGVsbG8gV29ybGQ=', 'task_trigger': 'At logon', 'user': 'system'},
        {'event_id': 7045, 'service_name': 'UpdateService', 'service_path': 'C:\\temp\\update.exe', 'service_type': 'user', 'user': 'admin'},
        {'event_id': 5857, 'wmi_query': 'SELECT * FROM __InstanceModificationEvent', 'wmi_consumer': 'ActiveScriptEventConsumer', 'user': 'system'},
        {'file_path': 'C:\\Users\\Admin\\AppData\\Roaming\\Microsoft\\Windows\\Start Menu\\Programs\\Startup\\script.vbs', 'operation': 'create', 'file_name': 'script.vbs', 'user': 'admin'},
    ]
    
    findings = hunter.run_full_hunt(logs)
    print("\n" + hunter.generate_report(findings))


if __name__ == "__main__":
    main()
