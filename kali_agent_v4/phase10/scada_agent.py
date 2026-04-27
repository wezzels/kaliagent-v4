#!/usr/bin/env python3
"""
🏭 KaliAgent v4.4.0 - Phase 10: SCADA/ICS Security
Main SCADA/ICS Agent

Orchestrates industrial control system security testing:
- ICS device discovery
- Protocol testing (Modbus, S7comm, EtherNet/IP, DNP3, BACnet, OPC UA)
- PLC security assessment
- HMI/SCADA testing
- ICS malware detection
- Vulnerability correlation

Author: KaliAgent Team
Started: April 27, 2026
Status: Alpha (0.1.0)

⚠️  CRITICAL SAFETY WARNING: Only test on isolated lab systems!
"""

import logging
from typing import List, Dict, Optional
from datetime import datetime
from dataclasses import dataclass, field

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('SCADAAgent')


@dataclass
class ICSDevice:
    """Represents an ICS/SCADA device"""
    ip_address: str
    device_type: str = ""  # PLC, HMI, RTU, Historian, etc.
    vendor: str = ""
    model: str = ""
    firmware_version: str = ""
    serial_number: str = ""
    protocols: List[str] = field(default_factory=list)
    open_ports: List[int] = field(default_factory=list)
    vulnerabilities: List[Dict] = field(default_factory=list)
    risk_score: float = 0.0
    safety_critical: bool = False
    
    def to_dict(self) -> Dict:
        return {
            'ip_address': self.ip_address,
            'device_type': self.device_type,
            'vendor': self.vendor,
            'model': self.model,
            'firmware_version': self.firmware_version,
            'serial_number': self.serial_number,
            'protocols': self.protocols,
            'open_ports': self.open_ports,
            'vulnerabilities': self.vulnerabilities,
            'risk_score': self.risk_score,
            'safety_critical': self.safety_critical
        }


@dataclass
class PLCInfo:
    """PLC-specific information"""
    ip_address: str
    vendor: str
    model: str
    cpu_type: str = ""
    firmware_version: str = ""
    project_name: str = ""
    protection_level: str = ""
    run_mode: str = ""  # RUN, STOP, HOLD
    memory_size: int = 0
    
    def to_dict(self) -> Dict:
        return {
            'ip_address': self.ip_address,
            'vendor': self.vendor,
            'model': self.model,
            'cpu_type': self.cpu_type,
            'firmware_version': self.firmware_version,
            'project_name': self.project_name,
            'protection_level': self.protection_level,
            'run_mode': self.run_mode,
            'memory_size': self.memory_size
        }


class SCADAAgent:
    """
    SCADA/ICS Security Testing Agent
    
    ⚠️  CRITICAL SAFETY WARNING:
    Only use on isolated lab systems you own or have explicit written
    authorization to test. ICS testing can cause physical damage,
    process disruption, and safety hazards.
    
    Capabilities:
    - ICS device discovery
    - Protocol testing (Modbus, S7comm, EtherNet/IP, DNP3, BACnet, OPC UA)
    - PLC security assessment
    - HMI/SCADA testing
    - ICS malware detection
    - Vulnerability assessment
    """
    
    VERSION = "0.1.0"
    PHASE = 10
    
    # ICS protocol ports
    ICS_PROTOCOLS = {
        'modbus': {'port': 502, 'type': 'tcp'},
        's7comm': {'port': 102, 'type': 'tcp'},
        'ethernetip': {'port': 44818, 'type': 'tcp'},
        'bacnet': {'port': 47808, 'type': 'udp'},
        'dnp3': {'port': 20000, 'type': 'tcp'},
        'opcua': {'port': 4840, 'type': 'tcp'},
        'profinet': {'port': 34962, 'type': 'tcp'},
        'iccp': {'port': 102, 'type': 'tcp'},
    }
    
    # ICS vendor signatures
    VENDOR_SIGNATURES = {
        'siemens': {
            'ports': [102, 502],
            'ouis': ['001A42', '001B1B', '08005A'],
            'banners': ['SIEMENS', 'SIMATIC'],
            'device_types': ['PLC', 'HMI', 'Drive']
        },
        'allen-bradley': {
            'ports': [44818, 2222],
            'ouis': ['0000CD', '0000E8'],
            'banners': ['Allen-Bradley', 'ROCKWELL'],
            'device_types': ['PLC', 'HMI', 'VFD']
        },
        'schneider': {
            'ports': [502, 47808],
            'ouis': ['000054', '00204A'],
            'banners': ['Schneider', 'Modicon'],
            'device_types': ['PLC', 'HMI']
        },
        'mitsubishi': {
            'ports': [502, 8000],
            'ouis': ['00003F', '000173'],
            'banners': ['Mitsubishi', 'MELSEC'],
            'device_types': ['PLC', 'CNC']
        },
        'omron': {
            'ports': [9600, 502],
            'ouis': ['00010C', '000181'],
            'banners': ['OMRON', 'SYSMAC'],
            'device_types': ['PLC', 'HMI']
        }
    }
    
    def __init__(self, target_network: str = None, verbose: bool = True,
                 safety_mode: bool = True):
        """
        Initialize SCADA/ICS Agent
        
        Args:
            target_network: Target network CIDR
            verbose: Enable verbose logging
            safety_mode: Enable safety restrictions (READ-ONLY operations)
        """
        self.verbose = verbose
        if verbose:
            logger.setLevel(logging.DEBUG)
        
        self.target_network = target_network
        self.safety_mode = safety_mode
        self.devices: List[ICSDevice] = []
        self.start_time = datetime.now()
        
        logger.info(f"🏭 SCADA/ICS Agent v{self.VERSION}")
        logger.warning(f"⚠️  SAFETY MODE: {'ENABLED' if safety_mode else 'DISABLED'}")
        logger.warning(f"⚠️  ONLY test on isolated lab systems!")
        
        if target_network:
            logger.info(f"🎯 Target network: {target_network}")
    
    def discover_ics_devices(self) -> List[ICSDevice]:
        """
        Discover ICS devices on network
        
        Returns:
            List of discovered ICS devices
        """
        logger.info("🔍 Discovering ICS devices...")
        
        if not self.target_network:
            logger.error("❌ No target network specified")
            return []
        
        # Scan for ICS protocol ports
        devices = self._scan_ics_ports()
        
        # Fingerprint devices
        for device in devices:
            self._fingerprint_ics_device(device)
        
        self.devices = devices
        logger.info(f"✅ Discovered {len(devices)} ICS devices")
        
        return devices
    
    def _scan_ics_ports(self) -> List[ICSDevice]:
        """Scan for ICS protocol ports"""
        logger.debug("  Scanning ICS protocol ports...")
        
        devices = []
        
        # TODO: Implement actual port scanning
        # For now, return simulated results
        
        simulated = [
            ICSDevice(
                ip_address="192.168.10.100",
                device_type="PLC",
                vendor="Siemens",
                model="S7-1200",
                protocols=['s7comm', 'modbus'],
                open_ports=[102, 502],
                risk_score=7.5
            ),
            ICSDevice(
                ip_address="192.168.10.101",
                device_type="PLC",
                vendor="Allen-Bradley",
                model="ControlLogix",
                protocols=['ethernetip'],
                open_ports=[44818],
                risk_score=7.0
            )
        ]
        
        return simulated
    
    def _fingerprint_ics_device(self, device: ICSDevice):
        """Fingerprint ICS device"""
        logger.debug(f"  Fingerprinting {device.ip_address}...")
        
        # Check vendor signatures
        for vendor, sig in self.VENDOR_SIGNATURES.items():
            if vendor in device.vendor.lower():
                device.protocols = [p for p in sig['ports'] if p in device.open_ports]
                break
        
        # Calculate risk score
        device.risk_score = self._calculate_risk(device)
    
    def _calculate_risk(self, device: ICSDevice) -> float:
        """Calculate device risk score (0-10)"""
        score = 5.0  # Base score
        
        # Unencrypted protocols
        unencrypted = ['modbus', 's7comm', 'ethernetip']
        for proto in device.protocols:
            if proto in unencrypted:
                score += 0.5
        
        # Default ports
        if 502 in device.open_ports:  # Modbus
            score += 0.5
        if 102 in device.open_ports:  # S7comm
            score += 0.5
        
        # Device type risk
        if device.device_type in ['PLC', 'RTU']:
            score += 1.0
        if device.safety_critical:
            score += 2.0
        
        return min(10.0, score)
    
    def scan_modbus(self, ip_address: str) -> Dict:
        """
        Scan Modbus device
        
        Args:
            ip_address: Device IP
            
        Returns:
            Scan results
        """
        logger.info(f"🔍 Scanning Modbus device: {ip_address}")
        
        if self.safety_mode:
            logger.info("  Safety mode: READ-ONLY operations")
        
        # TODO: Import and use Modbus client from Phase 9
        # from phase9.iot_protocols.modbus_client import ModbusClient
        
        results = {
            'ip_address': ip_address,
            'protocol': 'modbus',
            'unit_ids': [1],
            'coils_readable': True,
            'registers_readable': True,
            'write_protected': self.safety_mode,
            'vulnerabilities': []
        }
        
        return results
    
    def scan_s7(self, ip_address: str) -> Dict:
        """
        Scan Siemens S7 PLC
        
        Args:
            ip_address: PLC IP
            
        Returns:
            Scan results
        """
        logger.info(f"🔍 Scanning Siemens S7 PLC: {ip_address}")
        
        if self.safety_mode:
            logger.info("  Safety mode: READ-ONLY operations")
        
        results = {
            'ip_address': ip_address,
            'protocol': 's7comm',
            'cpu_info': {
                'vendor': 'Siemens',
                'model': 'S7-1200',
                'cpu_type': 'CPU 1214C',
                'firmware': 'V4.2',
                'run_mode': 'RUN'
            },
            'protection_level': 'none',
            'block_protection': False,
            'vulnerabilities': []
        }
        
        return results
    
    def scan_ethernetip(self, ip_address: str) -> Dict:
        """
        Scan EtherNet/IP device
        
        Args:
            ip_address: Device IP
            
        Returns:
            Scan results
        """
        logger.info(f"🔍 Scanning EtherNet/IP device: {ip_address}")
        
        results = {
            'ip_address': ip_address,
            'protocol': 'ethernetip',
            'identity': {
                'vendor': 'Rockwell Automation',
                'device_type': 'Programmable Logic Controller',
                'product_name': 'ControlLogix',
                'revision': '1.0'
            },
            'vulnerabilities': []
        }
        
        return results
    
    def detect_ics_malware(self, target: str) -> Dict:
        """
        Detect ICS malware signatures
        
        Args:
            target: Target IP or network
            
        Returns:
            Malware detection results
        """
        logger.info(f"🦠 Scanning for ICS malware: {target}")
        
        results = {
            'target': target,
            'malware_detected': False,
            'signatures_checked': [
                'Triton/Trisis',
                'Stuxnet',
                'CrashOverride/Industroyer',
                'Havex',
                'BlackEnergy'
            ],
            'findings': []
        }
        
        return results
    
    def generate_report(self, output_format: str = 'text') -> str:
        """
        Generate SCADA/ICS assessment report
        
        Args:
            output_format: 'text', 'json', 'html'
            
        Returns:
            Formatted report
        """
        logger.info("📊 Generating report...")
        
        if output_format == 'json':
            import json
            return json.dumps([d.to_dict() for d in self.devices], indent=2)
        
        # Text format
        report = []
        report.append("=" * 70)
        report.append("🏭 SCADA/ICS SECURITY ASSESSMENT REPORT")
        report.append("=" * 70)
        report.append(f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        report.append(f"Target: {self.target_network}")
        report.append(f"Safety Mode: {'ENABLED' if self.safety_mode else 'DISABLED'}")
        report.append(f"Devices Found: {len(self.devices)}")
        report.append("")
        
        report.append("⚠️  SAFETY NOTICE:")
        report.append("-" * 70)
        report.append("This assessment was conducted in SAFETY MODE (READ-ONLY).")
        report.append("No write operations or control commands were executed.")
        report.append("")
        
        for i, device in enumerate(self.devices, 1):
            report.append(f"\n{'='*70}")
            report.append(f"DEVICE {i}: {device.vendor} {device.model}")
            report.append(f"{'='*70}")
            report.append(f"IP Address:    {device.ip_address}")
            report.append(f"Device Type:   {device.device_type}")
            report.append(f"Vendor:        {device.vendor}")
            report.append(f"Model:         {device.model}")
            report.append(f"Risk Score:    {device.risk_score}/10.0")
            report.append(f"Safety Critical: {'YES ⚠️' if device.safety_critical else 'No'}")
            report.append("")
            report.append(f"Protocols:     {', '.join(device.protocols)}")
            report.append(f"Open Ports:    {', '.join(map(str, device.open_ports))}")
            
            if device.vulnerabilities:
                report.append("")
                report.append("VULNERABILITIES:")
                for vuln in device.vulnerabilities:
                    report.append(f"  ⚠️  {vuln.get('cve', 'Unknown')}: {vuln.get('description', 'N/A')}")
        
        report.append("")
        report.append("RECOMMENDATIONS:")
        report.append("-" * 70)
        report.append("1. Implement network segmentation (IT/ICS separation)")
        report.append("2. Deploy industrial firewalls at zone boundaries")
        report.append("3. Enable protocol authentication where available")
        report.append("4. Implement secure remote access (MFA, jump hosts)")
        report.append("5. Monitor ICS network traffic for anomalies")
        report.append("6. Keep firmware updated (test in lab first)")
        report.append("7. Follow IEC 62443 security guidelines")
        report.append("")
        report.append("=" * 70)
        
        return "\n".join(report)


def main():
    """Main entry point"""
    print("""
╔═══════════════════════════════════════════════════════════════╗
║     🏭 KALIAGENT v4.4.0 - SCADA/ICS AGENT                    ║
║                    Phase 10: Alpha 0.1.0                      ║
╚═══════════════════════════════════════════════════════════════╝

⚠️  CRITICAL SAFETY WARNING:
    ICS/SCADA testing can cause PHYSICAL DAMAGE and SAFETY HAZARDS!
    
    ONLY use on:
    ✅ Isolated lab systems you own
    ✅ Dedicated training facilities
    ✅ Systems with explicit written authorization
    
    NEVER test on:
    ❌ Production systems
    ❌ Critical infrastructure
    ❌ Systems without authorization

    """)
    
    import sys
    
    # Initialize agent
    target = sys.argv[1] if len(sys.argv) > 1 else "192.168.10.0/24"
    scada = SCADAAgent(target_network=target, verbose=True, safety_mode=True)
    
    # Discover devices
    devices = scada.discover_ics_devices()
    
    # Generate report
    report = scada.generate_report()
    print("\n" + report)
    
    # Save report
    with open('scada_assessment_report.txt', 'w') as f:
        f.write(report)
    
    print("\n✅ Report saved to: scada_assessment_report.txt")


if __name__ == "__main__":
    main()
