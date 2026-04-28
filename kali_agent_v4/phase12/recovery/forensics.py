#!/usr/bin/env python3
"""
🚨 KaliAgent v4.4.0 - Phase 12: Automated Response & Remediation
Digital Forensics Module

Forensic evidence collection:
- Memory acquisition
- Disk imaging
- Log collection
- Network capture
- Chain of custody
- Evidence preservation

Author: KaliAgent Team
Started: April 28, 2026
Status: Alpha (0.1.0)
"""

import logging
import hashlib
from typing import List, Dict, Optional
from datetime import datetime
from dataclasses import dataclass, field
import uuid

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger('Forensics')


@dataclass
class Evidence:
    """Digital evidence item"""
    id: str
    type: str
    source: str
    collected_at: datetime
    collected_by: str
    size_bytes: int
    hash_md5: str
    hash_sha256: str
    chain_of_custody: List[Dict] = field(default_factory=list)
    location: str = ""
    notes: str = ""
    
    def to_dict(self) -> Dict:
        return {
            'id': self.id,
            'type': self.type,
            'source': self.source,
            'collected_at': self.collected_at.isoformat(),
            'collected_by': self.collected_by,
            'size_bytes': self.size_bytes,
            'hash_md5': self.hash_md5,
            'hash_sha256': self.hash_sha256,
            'chain_of_custody': self.chain_of_custody,
            'location': self.location,
            'notes': self.notes
        }


@dataclass
class ForensicCase:
    """Forensic case"""
    id: str
    incident_id: str
    title: str
    created_at: datetime
    investigator: str
    evidence: List[Evidence] = field(default_factory=list)
    status: str = "open"
    notes: str = ""


class DigitalForensics:
    """
    Digital Forensics Module
    
    Capabilities:
    - Memory acquisition
    - Disk imaging
    - Log collection
    - Network packet capture
    - Chain of custody management
    - Evidence preservation
    """
    
    VERSION = "0.1.0"
    
    def __init__(self, config: Dict = None):
        self.config = config or {}
        self.cases: List[ForensicCase] = []
        self.evidence: List[Evidence] = []
        self.storage_path = config.get('storage_path', '/evidence')
        
        logger.info(f"🔬 Digital Forensics v{self.VERSION}")
        logger.info(f"   Storage: {self.storage_path}")
    
    def create_case(self, incident_id: str, title: str,
                   investigator: str = "automated") -> ForensicCase:
        """
        Create forensic case
        
        Args:
            incident_id: Related incident ID
            title: Case title
            investigator: Investigator name
            
        Returns:
            Forensic case
        """
        case = ForensicCase(
            id=str(uuid.uuid4())[:8],
            incident_id=incident_id,
            title=title,
            created_at=datetime.now(),
            investigator=investigator
        )
        
        self.cases.append(case)
        logger.info(f"📁 Forensic case created: {case.id}")
        logger.info(f"   Incident: {incident_id}")
        logger.info(f"   Title: {title}")
        
        return case
    
    def collect_memory(self, hostname: str, method: str = 'dump',
                      compress: bool = True) -> Evidence:
        """
        Collect memory dump
        
        Args:
            hostname: Target hostname
            method: Collection method (dump, acquire, etc.)
            compress: Compress after collection
            
        Returns:
            Evidence item
        """
        logger.info(f"🧠 Collecting memory from {hostname}")
        logger.info(f"   Method: {method}")
        logger.info(f"   Compress: {compress}")
        
        # Simulate memory dump
        memory_size = 16 * 1024 * 1024 * 1024  # 16GB
        memory_data = b'\x00' * 1024  # Simulated
        
        # Calculate hashes
        md5_hash = hashlib.md5(memory_data).hexdigest()
        sha256_hash = hashlib.sha256(memory_data).hexdigest()
        
        evidence = Evidence(
            id=str(uuid.uuid4())[:8],
            type='memory_dump',
            source=hostname,
            collected_at=datetime.now(),
            collected_by='automated',
            size_bytes=memory_size,
            hash_md5=md5_hash,
            hash_sha256=sha256_hash,
            location=f"{self.storage_path}/memory/{hostname}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.dmp",
            notes=f"Memory dump via {method}"
        )
        
        # Add to chain of custody
        self._add_custody_entry(evidence, 'collection', 'automated')
        
        self.evidence.append(evidence)
        logger.info(f"✅ Memory collected: {evidence.id}")
        logger.info(f"   Size: {memory_size / (1024**3):.1f}GB")
        logger.info(f"   SHA256: {sha256_hash[:16]}...")
        
        return evidence
    
    def collect_disk_image(self, hostname: str, drive: str = 'C:',
                          method: str = 'dd') -> Evidence:
        """
        Collect disk image
        
        Args:
            hostname: Target hostname
            drive: Drive letter/path
            method: Imaging method
            
        Returns:
            Evidence item
        """
        logger.info(f"💾 Collecting disk image from {hostname}:{drive}")
        logger.info(f"   Method: {method}")
        
        # Simulate disk image
        disk_size = 500 * 1024 * 1024 * 1024  # 500GB
        disk_data = b'\x00' * 1024  # Simulated
        
        # Calculate hashes
        md5_hash = hashlib.md5(disk_data).hexdigest()
        sha256_hash = hashlib.sha256(disk_data).hexdigest()
        
        evidence = Evidence(
            id=str(uuid.uuid4())[:8],
            type='disk_image',
            source=f"{hostname}:{drive}",
            collected_at=datetime.now(),
            collected_by='automated',
            size_bytes=disk_size,
            hash_md5=md5_hash,
            hash_sha256=sha256_hash,
            location=f"{self.storage_path}/disk/{hostname}_{drive}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.img",
            notes=f"Disk image via {method}"
        )
        
        self._add_custody_entry(evidence, 'collection', 'automated')
        
        self.evidence.append(evidence)
        logger.info(f"✅ Disk image collected: {evidence.id}")
        logger.info(f"   Size: {disk_size / (1024**3):.1f}GB")
        
        return evidence
    
    def collect_logs(self, hostname: str, log_types: List[str] = None,
                    time_range: Dict = None) -> Evidence:
        """
        Collect system logs
        
        Args:
            hostname: Target hostname
            log_types: Types of logs (security, system, application)
            time_range: Time range for collection
            
        Returns:
            Evidence item
        """
        if log_types is None:
            log_types = ['security', 'system', 'application']
        
        logger.info(f"📋 Collecting logs from {hostname}")
        logger.info(f"   Types: {', '.join(log_types)}")
        
        # Simulate log collection
        log_data = f"Logs from {hostname}".encode()
        
        # Calculate hashes
        md5_hash = hashlib.md5(log_data).hexdigest()
        sha256_hash = hashlib.sha256(log_data).hexdigest()
        
        evidence = Evidence(
            id=str(uuid.uuid4())[:8],
            type='logs',
            source=hostname,
            collected_at=datetime.now(),
            collected_by='automated',
            size_bytes=len(log_data),
            hash_md5=md5_hash,
            hash_sha256=sha256_hash,
            location=f"{self.storage_path}/logs/{hostname}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.zip",
            notes=f"Log types: {', '.join(log_types)}"
        )
        
        self._add_custody_entry(evidence, 'collection', 'automated')
        
        self.evidence.append(evidence)
        logger.info(f"✅ Logs collected: {evidence.id}")
        
        return evidence
    
    def collect_network_capture(self, hostname: str, interface: str = 'eth0',
                               duration_seconds: int = 60) -> Evidence:
        """
        Collect network packet capture
        
        Args:
            hostname: Target hostname
            interface: Network interface
            duration_seconds: Capture duration
            
        Returns:
            Evidence item
        """
        logger.info(f"📡 Collecting network capture from {hostname}")
        logger.info(f"   Interface: {interface}")
        logger.info(f"   Duration: {duration_seconds}s")
        
        # Simulate pcap
        pcap_data = b'\x00' * 1024  # Simulated
        
        # Calculate hashes
        md5_hash = hashlib.md5(pcap_data).hexdigest()
        sha256_hash = hashlib.sha256(pcap_data).hexdigest()
        
        evidence = Evidence(
            id=str(uuid.uuid4())[:8],
            type='network_capture',
            source=f"{hostname}:{interface}",
            collected_at=datetime.now(),
            collected_by='automated',
            size_bytes=len(pcap_data),
            hash_md5=md5_hash,
            hash_sha256=sha256_hash,
            location=f"{self.storage_path}/pcap/{hostname}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pcap",
            notes=f"Capture on {interface} for {duration_seconds}s"
        )
        
        self._add_custody_entry(evidence, 'collection', 'automated')
        
        self.evidence.append(evidence)
        logger.info(f"✅ Network capture collected: {evidence.id}")
        
        return evidence
    
    def collect_artifacts(self, hostname: str, 
                         artifact_types: List[str] = None) -> Evidence:
        """
        Collect system artifacts
        
        Args:
            hostname: Target hostname
            artifact_types: Types of artifacts
            
        Returns:
            Evidence item
        """
        if artifact_types is None:
            artifact_types = [
                'registry', 'prefetch', 'shellbags', 'jumplists',
                'browser_history', 'recent_files', 'usb_devices'
            ]
        
        logger.info(f"🔍 Collecting artifacts from {hostname}")
        logger.info(f"   Types: {', '.join(artifact_types)}")
        
        # Simulate artifact collection
        artifact_data = f"Artifacts from {hostname}".encode()
        
        # Calculate hashes
        md5_hash = hashlib.md5(artifact_data).hexdigest()
        sha256_hash = hashlib.sha256(artifact_data).hexdigest()
        
        evidence = Evidence(
            id=str(uuid.uuid4())[:8],
            type='artifacts',
            source=hostname,
            collected_at=datetime.now(),
            collected_by='automated',
            size_bytes=len(artifact_data),
            hash_md5=md5_hash,
            hash_sha256=sha256_hash,
            location=f"{self.storage_path}/artifacts/{hostname}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.zip",
            notes=f"Artifact types: {', '.join(artifact_types)}"
        )
        
        self._add_custody_entry(evidence, 'collection', 'automated')
        
        self.evidence.append(evidence)
        logger.info(f"✅ Artifacts collected: {evidence.id}")
        
        return evidence
    
    def _add_custody_entry(self, evidence: Evidence, action: str,
                          who: str, notes: str = ""):
        """Add chain of custody entry"""
        custody_entry = {
            'timestamp': datetime.now().isoformat(),
            'action': action,
            'who': who,
            'notes': notes
        }
        
        evidence.chain_of_custody.append(custody_entry)
    
    def transfer_custody(self, evidence_id: str, from_whom: str,
                        to_whom: str, reason: str = "") -> bool:
        """
        Transfer evidence custody
        
        Args:
            evidence_id: Evidence ID
            from_whom: Current custodian
            to_whom: New custodian
            reason: Transfer reason
            
        Returns:
            Success status
        """
        evidence = next((e for e in self.evidence if e.id == evidence_id), None)
        
        if not evidence:
            logger.error(f"Evidence not found: {evidence_id}")
            return False
        
        self._add_custody_entry(
            evidence,
            'transfer',
            to_whom,
            f"Transferred from {from_whom}: {reason}"
        )
        
        logger.info(f"✅ Custody transferred: {evidence_id}")
        logger.info(f"   From: {from_whom}")
        logger.info(f"   To: {to_whom}")
        
        return True
    
    def get_evidence_summary(self) -> Dict:
        """Get evidence summary"""
        by_type = {}
        
        for ev in self.evidence:
            if ev.type not in by_type:
                by_type[ev.type] = {'count': 0, 'size': 0}
            by_type[ev.type]['count'] += 1
            by_type[ev.type]['size'] += ev.size_bytes
        
        return {
            'total_evidence': len(self.evidence),
            'total_cases': len(self.cases),
            'total_size_bytes': sum(e.size_bytes for e in self.evidence),
            'by_type': by_type
        }
    
    def generate_report(self, case_id: str = None) -> str:
        """Generate forensics report"""
        summary = self.get_evidence_summary()
        
        report = []
        report.append("=" * 70)
        report.append("🔬 DIGITAL FORENSICS REPORT")
        report.append("=" * 70)
        report.append(f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        report.append("")
        report.append(f"Total Cases: {summary['total_cases']}")
        report.append(f"Total Evidence Items: {summary['total_evidence']}")
        report.append(f"Total Size: {summary['total_size_bytes'] / (1024**3):.2f}GB")
        report.append("")
        
        report.append("EVIDENCE BY TYPE:")
        for type_, data in summary['by_type'].items():
            report.append(f"  {type_}: {data['count']} items ({data['size'] / (1024**2):.1f}MB)")
        report.append("")
        
        if self.evidence:
            report.append("RECENT EVIDENCE:")
            report.append("-" * 70)
            for ev in self.evidence[-10:]:
                report.append(f"\n  📦 {ev.id} - {ev.type}")
                report.append(f"     Source: {ev.source}")
                report.append(f"     Collected: {ev.collected_at}")
                report.append(f"     Size: {ev.size_bytes / (1024**2):.1f}MB")
                report.append(f"     SHA256: {ev.hash_sha256[:32]}...")
                report.append(f"     Custody Entries: {len(ev.chain_of_custody)}")
        
        report.append("")
        report.append("=" * 70)
        
        return "\n".join(report)


def main():
    """Main entry point"""
    print("""
╔═══════════════════════════════════════════════════════════════╗
║     🔬 DIGITAL FORENSICS MODULE                              ║
║                    Phase 12: Alpha 0.1.0                      ║
╚═══════════════════════════════════════════════════════════════╝

Capabilities:
  - Memory acquisition
  - Disk imaging
  - Log collection
  - Network capture
  - Artifact collection
  - Chain of custody

    """)
    
    forensics = DigitalForensics()
    
    # Create case
    case = forensics.create_case('INC-001', 'Malware Investigation')
    
    # Collect evidence
    forensics.collect_memory('WS-001', method='dump')
    forensics.collect_logs('WS-001', ['security', 'system'])
    forensics.collect_artifacts('WS-001', ['registry', 'prefetch', 'shellbags'])
    forensics.collect_network_capture('WS-001', interface='eth0', duration_seconds=60)
    
    # Transfer custody
    evidence = forensics.evidence[0]
    forensics.transfer_custody(evidence.id, 'automated', 'investigator_jones', 'Case assignment')
    
    # Generate report
    print(forensics.generate_report())


if __name__ == "__main__":
    main()
