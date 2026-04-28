#!/usr/bin/env python3
"""
🎯 KaliAgent v4.4.0 - Phase 11: Automated Threat Hunting
Data Exfiltration Hunting Playbook

Hunting for data exfiltration activities:
- Large data transfers
- Unusual upload patterns
- Cloud storage abuse
- DNS tunneling detection
- Encrypted channel abuse
- Physical media tracking

Author: KaliAgent Team
Started: April 28, 2026
Status: Alpha (0.1.0)
"""

import logging
from typing import List, Dict
from datetime import datetime, timedelta
from dataclasses import dataclass, field

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger('DataExfiltrationHunt')


@dataclass
class ExfiltrationFinding:
    """Data exfiltration finding"""
    technique: str
    severity: str
    confidence: float
    description: str
    data_volume: str = ""
    destination: str = ""
    mitre_attack: str = ""
    evidence: List[str] = field(default_factory=list)
    recommended_actions: List[str] = field(default_factory=list)


class DataExfiltrationHunter:
    """
    Data Exfiltration Hunting Playbook
    
    MITRE ATT&CK: TA0010 (Exfiltration)
    
    Techniques:
    - T1041: Exfiltration Over C2 Channel
    - T1048: Exfiltration Over Alternative Protocol
    - T1567: Exfiltration Over Web Service
    - T1052: Exfiltration Over Physical Media
    - T1029: Scheduled Transfer
    - T1537: Transfer Data to Cloud Account
    """
    
    VERSION = "0.1.0"
    
    # Known exfiltration destinations
    SUSPICIOUS_SERVICES = [
        'mega.nz', 'mediafire.com', 'rapidshare.com',
        'pastebin.com', 'ghostbin.com', 'privatebin.net',
        'discord.com/api', 'telegram.org',
        'github.com', 'gitlab.com', 'bitbucket.org'
    ]
    
    # Large file extensions to monitor
    SENSITIVE_EXTENSIONS = [
        '.sql', '.db', '.sqlite', '.mdb',  # Databases
        '.pst', '.ost', '.mbox',  # Email archives
        '.zip', '.rar', '.7z', '.tar.gz',  # Archives
        '.bak', '.backup', '.dump',  # Backups
        '.key', '.pem', '.pfx', '.p12',  # Certificates/Keys
        '.docx', '.xlsx', '.pptx', '.pdf',  # Documents
        '.dwg', '.dxf',  # CAD files
        '.vmem', '.vmdk', '.vdi',  # VM images
    ]
    
    def __init__(self):
        self.findings: List[ExfiltrationFinding] = []
        logger.info(f"📤 Data Exfiltration Hunter v{self.VERSION}")
    
    def detect_large_transfers(self, logs: List[Dict], 
                                threshold_mb: int = 100) -> List[ExfiltrationFinding]:
        """Detect large data transfers"""
        logger.info(f"🔍 Hunting for Large Data Transfers (>{threshold_mb}MB)...")
        
        findings = []
        
        for log in logs:
            bytes_out = log.get('bytes_out', 0)
            threshold_bytes = threshold_mb * 1024 * 1024
            
            if bytes_out > threshold_bytes:
                size_mb = bytes_out / (1024 * 1024)
                severity = 'critical' if size_mb > 1000 else 'high' if size_mb > 500 else 'medium'
                
                finding = ExfiltrationFinding(
                    technique='Large Data Transfer',
                    severity=severity,
                    confidence=0.7,
                    description=f'Large outbound transfer: {size_mb:.1f}MB',
                    data_volume=f'{size_mb:.1f}MB',
                    destination=log.get('dest_ip', 'unknown'),
                    mitre_attack='T1041',
                    evidence=[
                        f"Source: {log.get('source_ip')}",
                        f"Destination: {log.get('dest_ip')}",
                        f"Size: {size_mb:.1f}MB",
                        f"Protocol: {log.get('protocol', 'unknown')}"
                    ],
                    recommended_actions=[
                        'Investigate source system immediately',
                        'Review what data was transferred',
                        'Check if destination is known/authorized',
                        'Consider network isolation',
                        'Preserve forensic evidence',
                        'Review DLP policies'
                    ]
                )
                findings.append(finding)
        
        logger.info(f"   Large transfers: {len(findings)}")
        return findings
    
    def detect_cloud_upload(self, logs: List[Dict]) -> List[ExfiltrationFinding]:
        """Detect cloud storage uploads"""
        logger.info("🔍 Hunting for Cloud Storage Uploads...")
        
        findings = []
        
        for log in logs:
            destination = log.get('destination', '').lower()
            url = log.get('url', '').lower()
            
            # Check against suspicious services
            for service in self.SUSPICIOUS_SERVICES:
                if service in destination or service in url:
                    # Check if it's a large upload
                    bytes_out = log.get('bytes_out', 0)
                    size_mb = bytes_out / (1024 * 1024)
                    
                    severity = 'high' if size_mb > 50 else 'medium'
                    
                    finding = ExfiltrationFinding(
                        technique='Cloud Storage Upload',
                        severity=severity,
                        confidence=0.75,
                        description=f'Upload to cloud service: {service}',
                        data_volume=f'{size_mb:.1f}MB' if size_mb > 0 else 'Unknown',
                        destination=service,
                        mitre_attack='T1567',
                        evidence=[
                            f"Service: {service}",
                            f"Source: {log.get('source_ip')}",
                            f"User: {log.get('user', 'unknown')}",
                            f"Size: {size_mb:.1f}MB"
                        ],
                        recommended_actions=[
                            'Verify if upload is authorized',
                            'Review uploaded content',
                            'Check user activity history',
                            'Review cloud access policies',
                            'Consider blocking service if unauthorized'
                        ]
                    )
                    findings.append(finding)
                    break
        
        logger.info(f"   Cloud uploads: {len(findings)}")
        return findings
    
    def detect_dns_tunneling(self, logs: List[Dict]) -> List[ExfiltrationFinding]:
        """Detect DNS tunneling"""
        logger.info("🔍 Hunting for DNS Tunneling...")
        
        findings = []
        
        # DNS tunneling indicators:
        # - Unusually long DNS queries
        # - High DNS query volume
        # - Base64-like subdomain patterns
        # - TXT record queries
        
        dns_queries = {}
        
        for log in logs:
            if log.get('protocol') == 'DNS' or log.get('port') == 53:
                source = log.get('source_ip', 'unknown')
                
                if source not in dns_queries:
                    dns_queries[source] = []
                dns_queries[source].append(log)
        
        for source, queries in dns_queries.items():
            # Check for high volume
            if len(queries) > 100:  # Threshold
                # Check for long queries
                long_queries = [q for q in queries if len(q.get('query', '')) > 50]
                
                # Check for TXT queries
                txt_queries = [q for q in queries if q.get('query_type') == 'TXT']
                
                if len(long_queries) > 10 or len(txt_queries) > 20:
                    finding = ExfiltrationFinding(
                        technique='DNS Tunneling',
                        severity='high',
                        confidence=0.8,
                        description=f'Potential DNS tunneling from {source}',
                        data_volume=f'{len(queries)} queries',
                        destination='DNS',
                        mitre_attack='T1048.004',
                        evidence=[
                            f"Source: {source}",
                            f"Total queries: {len(queries)}",
                            f"Long queries: {len(long_queries)}",
                            f"TXT queries: {len(txt_queries)}"
                        ],
                        recommended_actions=[
                            'Investigate source system',
                            'Analyze DNS query patterns',
                            'Check for known DNS tunneling tools',
                            'Consider DNS monitoring solution',
                            'Implement DNS query logging'
                        ]
                    )
                    findings.append(finding)
        
        logger.info(f"   DNS tunneling indicators: {len(findings)}")
        return findings
    
    def detect_sensitive_file_access(self, logs: List[Dict]) -> List[ExfiltrationFinding]:
        """Detect sensitive file access before potential exfiltration"""
        logger.info("🔍 Hunting for Sensitive File Access...")
        
        findings = []
        file_access = {}
        
        for log in logs:
            filename = log.get('filename', '').lower()
            
            # Check for sensitive extensions
            for ext in self.SENSITIVE_EXTENSIONS:
                if filename.endswith(ext):
                    source = log.get('source_ip', 'unknown')
                    user = log.get('user', 'unknown')
                    key = f"{source}_{user}"
                    
                    if key not in file_access:
                        file_access[key] = []
                    file_access[key].append(log)
        
        for key, accesses in file_access.items():
            if len(accesses) >= 5:  # Multiple sensitive files
                source, user = key.split('_', 1)
                files = set(a.get('filename') for a in accesses)
                
                finding = ExfiltrationFinding(
                    technique='Sensitive File Access',
                    severity='medium',
                    confidence=0.65,
                    description=f'Multiple sensitive files accessed by {user}',
                    data_volume=f'{len(files)} files',
                    destination='Local/Network',
                    mitre_attack='T1530',
                    evidence=[
                        f"User: {user}",
                        f"Source: {source}",
                        f"Files accessed: {len(files)}",
                        f"Sample: {list(files)[:5]}"
                    ],
                    recommended_actions=[
                        'Review user activity',
                        'Check if access is authorized',
                        'Monitor for subsequent exfiltration',
                        'Review file access policies',
                        'Consider DLP implementation'
                    ]
                )
                findings.append(finding)
        
        logger.info(f"   Sensitive file access: {len(findings)}")
        return findings
    
    def detect_after_hours_transfer(self, logs: List[Dict]) -> List[ExfiltrationFinding]:
        """Detect after-hours data transfers"""
        logger.info("🔍 Hunting for After-Hours Transfers...")
        
        findings = []
        
        # Business hours: 6 AM - 10 PM
        business_start = 6
        business_end = 22
        
        for log in logs:
            timestamp = log.get('timestamp')
            if timestamp:
                hour = timestamp.hour if hasattr(timestamp, 'hour') else 12
                
                if hour < business_start or hour > business_end:
                    bytes_out = log.get('bytes_out', 0)
                    
                    if bytes_out > 10 * 1024 * 1024:  # > 10MB
                        size_mb = bytes_out / (1024 * 1024)
                        
                        finding = ExfiltrationFinding(
                            technique='After-Hours Transfer',
                            severity='medium',
                            confidence=0.6,
                            description=f'Large transfer outside business hours ({hour}:00)',
                            data_volume=f'{size_mb:.1f}MB',
                            destination=log.get('dest_ip', 'unknown'),
                            mitre_attack='T1029',
                            evidence=[
                                f"Time: {hour}:00",
                                f"Source: {log.get('source_ip')}",
                                f"Destination: {log.get('dest_ip')}",
                                f"Size: {size_mb:.1f}MB"
                            ],
                            recommended_actions=[
                                'Verify if activity is authorized',
                                'Check user work schedule',
                                'Review transferred data',
                                'Monitor for patterns',
                                'Consider time-based access controls'
                            ]
                        )
                        findings.append(finding)
        
        logger.info(f"   After-hours transfers: {len(findings)}")
        return findings
    
    def detect_physical_media(self, logs: List[Dict]) -> List[ExfiltrationFinding]:
        """Detect physical media usage"""
        logger.info("🔍 Hunting for Physical Media Usage...")
        
        findings = []
        
        # Look for USB device connections
        usb_events = [4663, 4660, 4661, 4670, 4673]  # Windows object access
        
        for log in logs:
            event_id = log.get('event_id')
            
            if event_id in usb_events:
                object_name = log.get('object_name', '').lower()
                
                if 'usb' in object_name or 'removable' in object_name or 'floppy' in object_name:
                    finding = ExfiltrationFinding(
                        technique='Physical Media Usage',
                        severity='medium',
                        confidence=0.7,
                        description='Removable media device connected/used',
                        data_volume='Unknown',
                        destination='Physical Media',
                        mitre_attack='T1052',
                        evidence=[
                            f"Event ID: {event_id}",
                            f"Device: {object_name}",
                            f"User: {log.get('user', 'unknown')}",
                            f"System: {log.get('hostname', 'unknown')}"
                        ],
                        recommended_actions=[
                            'Verify if device is authorized',
                            'Review what data was copied',
                            'Check device approval list',
                            'Consider USB port controls',
                            'Implement device encryption'
                        ]
                    )
                    findings.append(finding)
        
        logger.info(f"   Physical media events: {len(findings)}")
        return findings
    
    def run_full_hunt(self, logs: List[Dict]) -> List[ExfiltrationFinding]:
        """Run complete exfiltration hunt"""
        logger.info("🎯 Starting Data Exfiltration Hunt...")
        
        all_findings = []
        
        all_findings.extend(self.detect_large_transfers(logs))
        all_findings.extend(self.detect_cloud_upload(logs))
        all_findings.extend(self.detect_dns_tunneling(logs))
        all_findings.extend(self.detect_sensitive_file_access(logs))
        all_findings.extend(self.detect_after_hours_transfer(logs))
        all_findings.extend(self.detect_physical_media(logs))
        
        logger.info(f"✅ Hunt complete. Total findings: {len(all_findings)}")
        
        return all_findings
    
    def generate_report(self, findings: List[ExfiltrationFinding]) -> str:
        """Generate hunt report"""
        report = []
        report.append("=" * 70)
        report.append("📤 DATA EXFILTRATION HUNT REPORT")
        report.append("=" * 70)
        report.append(f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        report.append(f"Total Findings: {len(findings)}")
        report.append("")
        
        # Calculate total data volume
        total_volume = 0
        for f in findings:
            try:
                if 'MB' in f.data_volume:
                    total_volume += float(f.data_volume.replace('MB', ''))
            except:
                pass
        
        if total_volume > 0:
            report.append(f"Total Data Volume: {total_volume:.1f}MB")
            report.append("")
        
        if findings:
            report.append("DETAILED FINDINGS:")
            report.append("-" * 70)
            
            for i, f in enumerate(findings, 1):
                report.append(f"\n{i}. [{f.severity.upper()}] {f.technique}")
                report.append(f"   MITRE ATT&CK: {f.mitre_attack}")
                report.append(f"   Data Volume: {f.data_volume}")
                report.append(f"   Destination: {f.destination}")
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
║     📤 DATA EXFILTRATION HUNTING PLAYBOOK                    ║
║                    Phase 11: Alpha 0.1.0                      ║
╚═══════════════════════════════════════════════════════════════╝

MITRE ATT&CK: TA0010 (Exfiltration)
    """)
    
    hunter = DataExfiltrationHunter()
    
    # Simulated logs
    logs = [
        {'bytes_out': 500_000_000, 'dest_ip': '203.0.113.50', 'protocol': 'HTTPS'},
        {'destination': 'mega.nz', 'bytes_out': 100_000_000, 'source_ip': '192.168.1.100'},
        {'protocol': 'DNS', 'source_ip': '192.168.1.101', 'query': 'aGVsbG8gd29ybGQ.evil.com', 'query_type': 'TXT'},
        {'filename': 'database.sql', 'source_ip': '192.168.1.102', 'user': 'admin'},
        {'filename': 'backup.zip', 'source_ip': '192.168.1.102', 'user': 'admin'},
        {'event_id': 4663, 'object_name': 'USB Drive (E:)', 'user': 'user1'},
    ]
    
    findings = hunter.run_full_hunt(logs)
    print("\n" + hunter.generate_report(findings))


if __name__ == "__main__":
    main()
