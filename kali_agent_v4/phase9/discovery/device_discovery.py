#!/usr/bin/env python3
"""
🔍 KaliAgent v4.3.0 - Phase 9: IoT Exploitation
Device Discovery Module

Network scanning and device fingerprinting:
- Network scanning (Nmap integration)
- Service detection
- Device fingerprinting
- Protocol identification
- Vendor detection
- Vulnerability correlation

Author: KaliAgent Team
Started: April 27, 2026
Status: Alpha (0.1.0)
"""

import logging
import subprocess
import socket
import re
import json
from typing import List, Dict, Optional, Tuple
from datetime import datetime
from dataclasses import dataclass, field
from pathlib import Path

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('DeviceDiscovery')


@dataclass
class DiscoveredDevice:
    """Represents a discovered IoT device"""
    ip_address: str
    mac_address: str = ""
    hostname: str = ""
    vendor: str = ""
    device_type: str = ""
    model: str = ""
    os_info: str = ""
    open_ports: List[int] = field(default_factory=list)
    services: List[Dict] = field(default_factory=list)
    protocols: List[str] = field(default_factory=list)
    vulnerabilities: List[str] = field(default_factory=list)
    risk_score: float = 0.0
    confidence: float = 0.0
    
    def to_dict(self) -> Dict:
        return {
            'ip_address': self.ip_address,
            'mac_address': self.mac_address,
            'hostname': self.hostname,
            'vendor': self.vendor,
            'device_type': self.device_type,
            'model': self.model,
            'os_info': self.os_info,
            'open_ports': self.open_ports,
            'services': self.services,
            'protocols': self.protocols,
            'vulnerabilities': self.vulnerabilities,
            'risk_score': self.risk_score,
            'confidence': self.confidence
        }


@dataclass
class NetworkService:
    """Represents a network service"""
    port: int
    protocol: str  # tcp/udp
    service_name: str
    product: str = ""
    version: str = ""
    extra_info: str = ""
    banner: str = ""
    
    def to_dict(self) -> Dict:
        return {
            'port': self.port,
            'protocol': self.protocol,
            'service_name': self.service_name,
            'product': self.product,
            'version': self.version,
            'extra_info': self.extra_info,
            'banner': self.banner
        }


class DeviceDiscovery:
    """
    IoT Device Discovery Module
    
    Capabilities:
    - Network scanning
    - Port scanning
    - Service detection
    - OS fingerprinting
    - Device identification
    - Vulnerability correlation
    """
    
    VERSION = "0.1.0"
    
    # IoT device signatures
    DEVICE_SIGNATURES = {
        # IP Cameras
        'hikvision': {
            'ports': [80, 554, 8000],
            'banners': ['Hikvision', 'HIK', 'hikvision'],
            'ouis': ['48A195', 'D8D18A', '784859'],
            'device_type': 'IP Camera'
        },
        'dahua': {
            'ports': [80, 554, 37777],
            'banners': ['Dahua', 'DAHUA', 'dh'],
            'ouis': ['84C9B2', '543265'],
            'device_type': 'IP Camera'
        },
        'axis': {
            'ports': [80, 443, 554],
            'banners': ['AXIS', 'Axis'],
            'ouis': ['00408C', 'ACCC8E', 'B8A44F'],
            'device_type': 'IP Camera'
        },
        'foscam': {
            'ports': [80, 88],
            'banners': ['Foscam', 'FOSCAM'],
            'ouis': ['6469A2', '344B3D'],
            'device_type': 'IP Camera'
        },
        
        # Routers
        'tp-link': {
            'ports': [80, 443],
            'banners': ['TP-LINK', 'TP-Link', 'TP-Link Technologies'],
            'ouis': ['50C7BF', '1459C0', '244BFE'],
            'device_type': 'Router'
        },
        'netgear': {
            'ports': [80, 443],
            'banners': ['NETGEAR', 'Netgear', 'Managed Switch'],
            'ouis': ['204E7F', '3894ED', '944452'],
            'device_type': 'Router'
        },
        'linksys': {
            'ports': [80, 443],
            'banners': ['Linksys', 'LINKSYS', 'Cisco-Linksys'],
            'ouis': ['001839', '0014BF', '001E58'],
            'device_type': 'Router'
        },
        'asus': {
            'ports': [80, 443, 22],
            'banners': ['ASUS', 'Asus', 'ASUSTeK'],
            'ouis': ['B06EBF', 'F46D04', '38D547'],
            'device_type': 'Router'
        },
        'd-link': {
            'ports': [80, 443],
            'banners': ['D-Link', 'D-Link Corporation', 'D-Link Systems'],
            'ouis': ['14D64D', 'C8BE19', '388804'],
            'device_type': 'Router'
        },
        
        # Smart Home
        'philips-hue': {
            'ports': [80, 443],
            'banners': ['Philips hue', 'BWSB', 'SBSB'],
            'ouis': ['001788'],
            'device_type': 'Smart Home Hub'
        },
        'samsung-smartthings': {
            'ports': [39500],
            'banners': ['SmartThings', 'smartthings'],
            'ouis': ['18B430', '245EBE'],
            'device_type': 'Smart Home Hub'
        },
        'amazon-echo': {
            'ports': [443, 8883],
            'banners': ['Amazon', 'amazon'],
            'ouis': ['74C246', 'A002DC'],
            'device_type': 'Smart Speaker'
        },
        
        # Industrial
        'siemens': {
            'ports': [102, 502, 80],
            'banners': ['SIEMENS', 'Siemens', 'SIMATIC'],
            'ouis': ['001A42', '001B1B', '08005A'],
            'device_type': 'PLC'
        },
        'allen-bradley': {
            'ports': [44818, 2222, 80],
            'banners': ['Allen-Bradley', 'ROCKWELL', 'AB'],
            'ouis': ['0000CD', '0000E8'],
            'device_type': 'PLC'
        },
        
        # Printers
        'hp': {
            'ports': [80, 443, 9100, 515],
            'banners': ['HP', 'Hewlett-Packard', 'HP LaserJet'],
            'ouis': ['0017A4', '3417EB', 'D48564'],
            'device_type': 'Printer'
        },
        'canon': {
            'ports': [80, 443, 9100],
            'banners': ['Canon', 'CANON', 'i-SENSYS'],
            'ouis': ['000085', '000347', '3808FD'],
            'device_type': 'Printer'
        },
    }
    
    # IoT protocol signatures
    IOT_PROTOCOLS = {
        'mqtt': {'ports': [1883, 8883], 'type': 'tcp'},
        'coap': {'ports': [5683, 5684], 'type': 'udp'},
        'modbus': {'ports': [502], 'type': 'tcp'},
        'bacnet': {'ports': [47808], 'type': 'udp'},
        'zigbee': {'ports': [], 'type': '802.15.4'},
        'zwave': {'ports': [], 'type': 'rf'},
        'onvif': {'ports': [80, 443], 'type': 'tcp'},
        'rtsp': {'ports': [554], 'type': 'tcp'},
        'upnp': {'ports': [1900], 'type': 'udp'},
        'ssdp': {'ports': [1900], 'type': 'udp'},
    }
    
    def __init__(self, output_dir: str = None, verbose: bool = True):
        """
        Initialize Device Discovery
        
        Args:
            output_dir: Output directory for scan results
            verbose: Enable verbose logging
        """
        self.verbose = verbose
        if verbose:
            logger.setLevel(logging.DEBUG)
        
        self.output_dir = output_dir or '.'
        self.devices: List[DiscoveredDevice] = []
        
        # Check for required tools
        self.nmap_available = self._check_tool('nmap')
        self.nmap_path = self._find_nmap()
        
        logger.info(f"🔍 Device Discovery v{self.VERSION}")
        logger.info(f"🔧 Nmap: {'✅' if self.nmap_available else '❌'}")
    
    def _check_tool(self, tool_name: str) -> bool:
        """Check if a tool is available"""
        try:
            subprocess.run(['which', tool_name], capture_output=True, check=True)
            return True
        except subprocess.CalledProcessError:
            return False
    
    def _find_nmap(self) -> str:
        """Find nmap installation"""
        try:
            result = subprocess.run(['which', 'nmap'], capture_output=True, text=True)
            if result.returncode == 0:
                return result.stdout.strip()
        except:
            pass
        
        common_paths = ['/usr/bin/nmap', '/usr/local/bin/nmap', '/opt/nmap/bin/nmap']
        for path in common_paths:
            if Path(path).exists():
                return path
        
        return None
    
    def scan_network(self, target: str, quick: bool = False) -> List[DiscoveredDevice]:
        """
        Scan network for IoT devices
        
        Args:
            target: Target network (CIDR notation or IP)
            quick: Quick scan (fewer probes)
            
        Returns:
            List of discovered devices
        """
        logger.info(f"🔍 Scanning network: {target}")
        
        if not self.nmap_available:
            logger.warning("⚠️  Nmap not available, using basic scan")
            return self._basic_scan(target)
        
        # Build nmap command
        cmd = [self.nmap_path]
        
        if quick:
            # Quick scan
            cmd.extend([
                '-sn',           # Ping scan only
                '-T4',           # Aggressive timing
                '--min-rate', '1000',
            ])
        else:
            # Full scan
            cmd.extend([
                '-sS',           # SYN scan
                '-sV',           # Version detection
                '-O',            # OS detection
                '-A',            # Aggressive scan
                '-T4',           # Aggressive timing
                '--min-rate', '500',
            ])
        
        cmd.extend(['-oX', '-', target])  # XML output to stdout
        
        logger.debug(f"  Running: {' '.join(cmd)}")
        
        try:
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
            
            if result.returncode == 0:
                devices = self._parse_nmap_xml(result.stdout)
                self.devices = devices
                logger.info(f"✅ Discovered {len(devices)} devices")
                return devices
            else:
                logger.error(f"❌ Nmap failed: {result.stderr}")
                return []
                
        except subprocess.TimeoutExpired:
            logger.error("❌ Scan timed out")
            return []
        except Exception as e:
            logger.error(f"❌ Scan failed: {e}")
            return []
    
    def _basic_scan(self, target: str) -> List[DiscoveredDevice]:
        """Basic network scan without nmap"""
        logger.info("  Running basic scan...")
        
        devices = []
        
        # Parse target
        if '/' in target:
            # CIDR notation - scan common IPs
            base = target.split('/')[0].rsplit('.', 1)[0]
            ips = [f"{base}.{i}" for i in range(1, 255)]
        else:
            ips = [target]
        
        for ip in ips[:50]:  # Limit to 50 IPs
            try:
                # Try to connect to common ports
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                sock.settimeout(0.5)
                
                for port in [80, 443, 22, 23, 21, 554]:
                    result = sock.connect_ex((ip, port))
                    if result == 0:
                        device = DiscoveredDevice(
                            ip_address=ip,
                            open_ports=[port],
                            confidence=0.5
                        )
                        devices.append(device)
                        logger.debug(f"  Found: {ip}:{port}")
                        break
                
                sock.close()
                
            except Exception as e:
                pass
        
        self.devices = devices
        return devices
    
    def _parse_nmap_xml(self, xml_output: str) -> List[DiscoveredDevice]:
        """Parse nmap XML output"""
        devices = []
        
        try:
            import xml.etree.ElementTree as ET
            root = ET.fromstring(xml_output)
            
            for host in root.findall('.//host'):
                # Get IP address
                addr_elem = host.find('address[@addrtype="ipv4"]')
                if addr_elem is None:
                    continue
                
                ip_address = addr_elem.get('addr')
                mac_address = ""
                
                mac_elem = host.find('address[@addrtype="mac"]')
                if mac_elem is not None:
                    mac_address = mac_elem.get('addr')
                
                # Get hostname
                hostname_elem = host.find('.//hostname')
                hostname = hostname_elem.get('name', '') if hostname_elem is not None else ''
                
                # Get vendor
                vendor_elem = host.find('.//vendor')
                vendor = vendor_elem.get('name', '') if vendor_elem is not None else ''
                
                # Get OS info
                os_elem = host.find('.//osmatch')
                os_info = os_elem.get('name', '') if os_elem is not None else ''
                
                # Get open ports and services
                open_ports = []
                services = []
                
                for port_elem in host.findall('.//port'):
                    port_num = int(port_elem.get('portid'))
                    port_proto = port_elem.get('protocol')
                    
                    state_elem = port_elem.find('state')
                    if state_elem is not None and state_elem.get('state') == 'open':
                        open_ports.append(port_num)
                        
                        # Get service info
                        service_elem = port_elem.find('service')
                        if service_elem is not None:
                            service = NetworkService(
                                port=port_num,
                                protocol=port_proto,
                                service_name=service_elem.get('name', ''),
                                product=service_elem.get('product', ''),
                                version=service_elem.get('version', ''),
                                extra_info=service_elem.get('extrainfo', ''),
                                banner=service_elem.get('method', '')
                            )
                            services.append(service.to_dict())
                
                # Create device
                device = DiscoveredDevice(
                    ip_address=ip_address,
                    mac_address=mac_address,
                    hostname=hostname,
                    vendor=vendor,
                    open_ports=open_ports,
                    services=services,
                    os_info=os_info
                )
                
                # Fingerprint device
                self._fingerprint_device(device)
                
                devices.append(device)
                
        except Exception as e:
            logger.error(f"❌ XML parse error: {e}")
        
        return devices
    
    def _fingerprint_device(self, device: DiscoveredDevice):
        """Fingerprint device based on signatures"""
        logger.debug(f"  Fingerprinting {device.ip_address}...")
        
        best_match = None
        best_score = 0
        
        # Check against known signatures
        for sig_name, sig_data in self.DEVICE_SIGNATURES.items():
            score = 0
            
            # Check ports
            port_matches = set(device.open_ports) & set(sig_data['ports'])
            if port_matches:
                score += len(port_matches) * 2
            
            # Check vendor
            if sig_name.replace('-', ' ') in device.vendor.lower():
                score += 5
            
            # Check services/banners
            for service in device.services:
                banner = service.get('banner', '') + service.get('product', '')
                for sig_banner in sig_data['banners']:
                    if sig_banner.lower() in banner.lower():
                        score += 10
            
            # Check MAC OUI
            if device.mac_address:
                oui = device.mac_address.replace(':', '').upper()[:6]
                if oui in sig_data['ouis']:
                    score += 15
            
            if score > best_score:
                best_score = score
                best_match = sig_data
        
        # Apply fingerprint
        if best_match and best_score >= 5:
            device.device_type = best_match['device_type']
            device.model = best_match.get('device_type', '')
            device.confidence = min(1.0, best_score / 20)
            device.risk_score = self._calculate_risk(device)
            
            # Detect protocols
            device.protocols = self._detect_protocols(device)
            
            # Correlate vulnerabilities
            device.vulnerabilities = self._correlate_vulnerabilities(device)
            
            logger.debug(f"  Matched: {best_match['device_type']} (confidence: {device.confidence:.2f})")
        else:
            device.confidence = 0.3
            device.risk_score = 5.0
    
    def _detect_protocols(self, device: DiscoveredDevice) -> List[str]:
        """Detect IoT protocols in use"""
        protocols = []
        
        for protocol, config in self.IOT_PROTOCOLS.items():
            for port in config['ports']:
                if port in device.open_ports:
                    protocols.append(protocol)
                    break
        
        # Check services for protocol hints
        for service in device.services:
            service_name = service.get('service_name', '').lower()
            
            if 'rtsp' in service_name:
                protocols.append('rtsp')
            if 'http' in service_name and 'onvif' in service.get('extra_info', '').lower():
                protocols.append('onvif')
            if 'upnp' in service_name or 'ssdp' in service_name:
                protocols.append('upnp')
        
        return list(set(protocols))
    
    def _correlate_vulnerabilities(self, device: DiscoveredDevice) -> List[str]:
        """Correlate known vulnerabilities based on device fingerprint"""
        vulns = []
        
        vendor = device.vendor.lower()
        device_type = device.device_type.lower()
        
        # Hikvision
        if 'hikvision' in vendor or 'hik' in vendor:
            vulns.extend([
                'CVE-2017-7921 (Auth Bypass)',
                'CVE-2017-7923 (Backdoor)',
                'CVE-2017-7928 (Privilege Escalation)'
            ])
        
        # Dahua
        if 'dahua' in vendor:
            vulns.extend([
                'CVE-2017-7927 (Backdoor)',
                'CVE-2021-33044 (Auth Bypass)'
            ])
        
        # Netgear
        if 'netgear' in vendor:
            vulns.extend([
                'CVE-2017-5521 (RCE)',
                'CVE-2016-1555 (Backdoor)'
            ])
        
        # TP-Link
        if 'tp-link' in vendor or 'tp link' in vendor:
            vulns.extend([
                'CVE-2017-13772 (Auth Bypass)',
                'CVE-2020-9375 (Buffer Overflow)'
            ])
        
        # Foscam
        if 'foscam' in vendor:
            vulns.extend([
                'CVE-2014-9184 (Backdoor)',
                'CVE-2014-9185 (RCE)'
            ])
        
        # Generic IoT
        if device_type in ['ip camera', 'router']:
            vulns.extend([
                'Default credentials likely',
                'Telnet may be enabled',
                'Firmware may be outdated'
            ])
        
        return vulns
    
    def _calculate_risk(self, device: DiscoveredDevice) -> float:
        """Calculate device risk score (0-10)"""
        score = 5.0  # Base score
        
        # High-risk ports
        risky_ports = [23, 2323, 21, 554, 8080]
        for port in device.open_ports:
            if port in risky_ports:
                score += 0.5
        
        # Vulnerabilities
        score += len(device.vulnerabilities) * 0.3
        
        # Device type risk
        high_risk_types = ['ip camera', 'plc', 'router']
        if device.device_type.lower() in high_risk_types:
            score += 1.0
        
        # Open services
        if len(device.services) > 5:
            score += 1.0
        
        return min(10.0, score)
    
    def scan_port(self, target: str, ports: List[int] = None) -> Dict:
        """
        Scan specific ports on target
        
        Args:
            target: Target IP address
            ports: List of ports to scan
            
        Returns:
            Port scan results
        """
        logger.info(f"🔍 Scanning ports on {target}")
        
        if ports is None:
            # Common IoT ports
            ports = [21, 22, 23, 25, 53, 80, 111, 443, 515, 554, 1883, 
                    3306, 3389, 5000, 502, 5432, 5683, 8080, 8443, 9000]
        
        results = {'open': [], 'closed': [], 'filtered': []}
        
        for port in ports:
            try:
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                sock.settimeout(1)
                result = sock.connect_ex((target, port))
                
                if result == 0:
                    results['open'].append(port)
                else:
                    results['closed'].append(port)
                
                sock.close()
                
            except Exception as e:
                results['filtered'].append(port)
        
        logger.info(f"  Open: {len(results['open'])}, Closed: {len(results['closed'])}, Filtered: {len(results['filtered'])}")
        
        return results
    
    def identify_device(self, ip_address: str) -> Optional[DiscoveredDevice]:
        """
        Identify a specific device
        
        Args:
            ip_address: Target IP address
            
        Returns:
            DiscoveredDevice or None
        """
        logger.info(f"🔍 Identifying device: {ip_address}")
        
        # Scan device
        devices = self.scan_network(ip_address, quick=False)
        
        if devices:
            return devices[0]
        
        return None
    
    def export_results(self, filepath: str = None) -> str:
        """
        Export scan results to JSON
        
        Args:
            filepath: Output file path
            
        Returns:
            JSON string
        """
        data = {
            'scan_date': datetime.now().isoformat(),
            'total_devices': len(self.devices),
            'devices': [d.to_dict() for d in self.devices]
        }
        
        json_str = json.dumps(data, indent=2, default=str)
        
        if filepath:
            with open(filepath, 'w') as f:
                f.write(json_str)
            logger.info(f"✅ Results exported to {filepath}")
        
        return json_str
    
    def generate_report(self) -> str:
        """Generate scan report"""
        report = []
        report.append("=" * 70)
        report.append("🔍 IOT DEVICE DISCOVERY REPORT")
        report.append("=" * 70)
        report.append(f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        report.append(f"Total Devices: {len(self.devices)}")
        report.append("")
        
        # Summary by type
        type_counts = {}
        for device in self.devices:
            dtype = device.device_type or 'Unknown'
            type_counts[dtype] = type_counts.get(dtype, 0) + 1
        
        report.append("DEVICE SUMMARY:")
        report.append("-" * 70)
        for dtype, count in sorted(type_counts.items(), key=lambda x: x[1], reverse=True):
            report.append(f"  {dtype}: {count}")
        
        report.append("")
        report.append("DETAILED FINDINGS:")
        report.append("-" * 70)
        
        for device in self.devices:
            report.append(f"\n📱 {device.ip_address}")
            report.append(f"   MAC: {device.mac_address or 'Unknown'}")
            report.append(f"   Vendor: {device.vendor or 'Unknown'}")
            report.append(f"   Type: {device.device_type or 'Unknown'}")
            report.append(f"   Confidence: {device.confidence:.0%}")
            report.append(f"   Risk Score: {device.risk_score}/10.0")
            
            if device.open_ports:
                report.append(f"   Open Ports: {', '.join(map(str, device.open_ports))}")
            
            if device.protocols:
                report.append(f"   Protocols: {', '.join(device.protocols)}")
            
            if device.vulnerabilities:
                report.append(f"   Vulnerabilities:")
                for vuln in device.vulnerabilities[:5]:
                    report.append(f"     ⚠️  {vuln}")
        
        report.append("")
        report.append("=" * 70)
        
        return "\n".join(report)
    
    def get_statistics(self) -> Dict:
        """Get scan statistics"""
        type_counts = {}
        vendor_counts = {}
        risk_scores = []
        
        for device in self.devices:
            dtype = device.device_type or 'Unknown'
            type_counts[dtype] = type_counts.get(dtype, 0) + 1
            
            vendor = device.vendor or 'Unknown'
            vendor_counts[vendor] = vendor_counts.get(vendor, 0) + 1
            
            risk_scores.append(device.risk_score)
        
        return {
            'total_devices': len(self.devices),
            'by_type': type_counts,
            'by_vendor': vendor_counts,
            'avg_risk_score': sum(risk_scores) / len(risk_scores) if risk_scores else 0,
            'high_risk_devices': sum(1 for d in self.devices if d.risk_score >= 7.0)
        }


def main():
    """Main entry point"""
    print("""
╔═══════════════════════════════════════════════════════════════╗
║     🔍 KALIAGENT v4.3.0 - IOT DEVICE DISCOVERY               ║
║                    Phase 9: Alpha 0.1.0                       ║
╚═══════════════════════════════════════════════════════════════╝
    """)
    
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python device_discovery.py <target> [quick]")
        print("\nExamples:")
        print("  python device_discovery.py 192.168.1.0/24")
        print("  python device_discovery.py 192.168.1.100")
        print("  python device_discovery.py 192.168.1.0/24 quick")
        sys.exit(1)
    
    target = sys.argv[1]
    quick = len(sys.argv) > 2 and sys.argv[2] == 'quick'
    
    # Initialize discovery
    discovery = DeviceDiscovery(verbose=True)
    
    # Scan network
    print(f"\n🔍 Scanning: {target}")
    devices = discovery.scan_network(target, quick=quick)
    
    # Generate report
    print("\n" + discovery.generate_report())
    
    # Export results
    report_file = f"device_scan_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    discovery.export_results(report_file)
    print(f"\n✅ Results saved to: {report_file}")
    
    # Statistics
    stats = discovery.get_statistics()
    print(f"\n📊 STATISTICS:")
    print(f"  Total Devices: {stats['total_devices']}")
    print(f"  High Risk: {stats['high_risk_devices']}")
    print(f"  Avg Risk Score: {stats['avg_risk_score']:.1f}/10.0")


if __name__ == "__main__":
    main()
