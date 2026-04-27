#!/usr/bin/env python3
"""
🏭 KaliAgent v4.4.0 - Phase 10: SCADA/ICS Security
HMI/SCADA Security Testing Module

HMI and SCADA system security testing:
- HMI discovery and enumeration
- HMI vulnerability assessment
- SCADA system testing
- Historian testing
- Default credential checking
- Web interface testing

Author: KaliAgent Team
Started: April 27, 2026
Status: Alpha (0.1.0)

⚠️  CRITICAL SAFETY WARNING: Only test on isolated lab systems!
"""

import logging
import requests
from typing import List, Dict, Optional
from datetime import datetime
from dataclasses import dataclass, field

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('HMITesting')


@dataclass
class HMIVulnerability:
    """HMI vulnerability"""
    title: str
    description: str
    severity: str = "medium"
    cvss_score: float = 0.0
    cwe_id: str = ""
    remediation: str = ""
    
    def to_dict(self) -> Dict:
        return {
            'title': self.title,
            'description': self.description,
            'severity': self.severity,
            'cvss_score': self.cvss_score,
            'cwe_id': self.cwe_id,
            'remediation': self.remediation
        }


@dataclass
class HMITestResult:
    """HMI test result"""
    vendor: str
    model: str
    ip_address: str
    port: int
    vulnerabilities: List[HMIVulnerability] = field(default_factory=list)
    default_creds_found: bool = False
    web_interface_exposed: bool = False
    security_score: float = 0.0
    
    def to_dict(self) -> Dict:
        return {
            'vendor': self.vendor,
            'model': self.model,
            'ip_address': self.ip_address,
            'port': self.port,
            'vulnerabilities': [v.to_dict() for v in self.vulnerabilities],
            'default_creds_found': self.default_creds_found,
            'web_interface_exposed': self.web_interface_exposed,
            'security_score': self.security_score
        }


class HMISecurityTester:
    """
    HMI/SCADA Security Testing
    
    ⚠️  CRITICAL SAFETY WARNING:
    Only use on isolated lab systems. HMI/SCADA testing can affect
    industrial processes and building systems.
    
    Capabilities:
    - HMI discovery and enumeration
    - HMI vulnerability assessment
    - SCADA system testing
    - Historian testing
    - Default credential checking
    - Web interface testing
    """
    
    VERSION = "0.1.0"
    
    # Common HMI/SCADA vendors and default credentials
    DEFAULT_CREDS = {
        'Wonderware': [('admin', 'admin'), ('Administrator', '')],
        'GE': [('admin', 'admin'), ('user', 'user')],
        'Siemens': [('admin', 'admin'), ('operator', 'operator')],
        'Rockwell': [('admin', 'admin'), ('rockwell', 'rockwell')],
        'Schneider': [('admin', 'admin'), ('USER', 'USER')],
        'ABB': [('admin', 'admin'), ('guest', 'guest')],
        'Honeywell': [('admin', 'admin'), ('operator', 'operator')],
        'Emerson': [('admin', 'admin'), ('default', 'default')],
        'Yokogawa': [('admin', 'admin'), ('user', 'password')],
        'Omron': [('admin', 'admin'), ('omron', 'omron')],
    }
    
    # Known HMI vulnerabilities
    KNOWN_VULNS = {
        'Wonderware InTouch': [
            HMIVulnerability(
                title='Unauthenticated Access',
                description='Default installation allows unauthenticated access',
                severity='high',
                cvss_score=7.5,
                cwe_id='CWE-306',
                remediation='Enable authentication and configure user access control'
            ),
        ],
        'GE Cimplicity': [
            HMIVulnerability(
                title='Weak Authentication',
                description='Default credentials are commonly used',
                severity='medium',
                cvss_score=5.5,
                cwe_id='CWE-798',
                remediation='Change default credentials immediately'
            ),
        ],
        'Siemens WinCC': [
            HMIVulnerability(
                title='Project File Exposure',
                description='Project files may be accessible without authentication',
                severity='high',
                cvss_score=7.0,
                cwe_id='CWE-200',
                remediation='Restrict access to project files and enable authentication'
            ),
        ],
        'Rockwell FactoryTalk': [
            HMIVulnerability(
                title='Directory Traversal',
                description='Potential directory traversal in web interface',
                severity='high',
                cvss_score=7.5,
                cwe_id='CWE-22',
                remediation='Update to latest version and restrict web access'
            ),
        ],
    }
    
    def __init__(self, safety_mode: bool = True, verbose: bool = True):
        """
        Initialize HMI Security Tester
        
        Args:
            safety_mode: Enable safety restrictions
            verbose: Enable verbose logging
        """
        self.safety_mode = safety_mode
        self.verbose = verbose
        
        if verbose:
            logger.setLevel(logging.DEBUG)
        
        self.results: List[HMITestResult] = []
        
        logger.info(f"🏭 HMI Security Tester v{self.VERSION}")
        logger.warning(f"⚠️  SAFETY MODE: {'ENABLED' if safety_mode else 'DISABLED'}")
    
    def discover_hmi(self, ip_address: str, ports: List[int] = None) -> Dict:
        """
        Discover HMI device
        
        Args:
            ip_address: HMI IP address
            ports: Ports to scan
            
        Returns:
            Discovery results
        """
        logger.info(f"🔍 Discovering HMI at {ip_address}...")
        
        if ports is None:
            ports = [80, 443, 8080, 8443, 5900, 3389]
        
        discovery = {
            'ip_address': ip_address,
            'vendor': 'Unknown',
            'model': 'Unknown',
            'open_ports': [],
            'web_interface': False,
            'rdp_exposed': False,
            'vnc_exposed': False
        }
        
        for port in ports:
            if self._check_port(ip_address, port):
                discovery['open_ports'].append(port)
                
                if port in [80, 443, 8080, 8443]:
                    discovery['web_interface'] = True
                    vendor = self._identify_vendor(ip_address, port)
                    if vendor:
                        discovery['vendor'] = vendor
                elif port == 3389:
                    discovery['rdp_exposed'] = True
                elif port == 5900:
                    discovery['vnc_exposed'] = True
        
        logger.info(f"  Open ports: {discovery['open_ports']}")
        logger.info(f"  Vendor: {discovery['vendor']}")
        
        return discovery
    
    def _check_port(self, ip: str, port: int) -> bool:
        """Check if port is open"""
        import socket
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(1)
            result = sock.connect_ex((ip, port))
            sock.close()
            return result == 0
        except:
            return False
    
    def _identify_vendor(self, ip: str, port: int) -> str:
        """Identify HMI vendor from web interface"""
        try:
            response = requests.get(f"http://{ip}:{port}", timeout=5)
            content = response.text.lower()
            
            if 'wonderware' in content or 'intouch' in content:
                return 'Wonderware'
            elif 'cimplicity' in content or 'ge digital' in content:
                return 'GE'
            elif 'wincc' in content or 'siemens' in content:
                return 'Siemens'
            elif 'factorytalk' in content or 'rockwell' in content:
                return 'Rockwell'
            elif 'citect' in content or 'schneider' in content:
                return 'Schneider'
            elif 'system 800xa' in content or 'abb' in content:
                return 'ABB'
            
            return 'Unknown'
            
        except:
            return 'Unknown'
    
    def test_default_credentials(self, ip: str, port: int, vendor: str) -> bool:
        """
        Test default credentials
        
        Args:
            ip: HMI IP address
            port: Web interface port
            vendor: HMI vendor
            
        Returns:
            True if default credentials found
        """
        logger.info(f"🔑 Testing default credentials for {vendor}...")
        
        creds = self.DEFAULT_CREDS.get(vendor, [('admin', 'admin')])
        
        for username, password in creds:
            if self._test_login(ip, port, username, password):
                logger.warning(f"⚠️  DEFAULT CREDENTIALS FOUND: {username}:{password}")
                return True
        
        return False
    
    def _test_login(self, ip: str, port: int, username: str, password: str) -> bool:
        """Test login credentials"""
        try:
            # Try common login paths
            login_paths = ['/login', '/auth', '/authenticate', '/weblogin']
            
            for path in login_paths:
                try:
                    response = requests.post(
                        f"http://{ip}:{port}{path}",
                        data={'username': username, 'password': password},
                        timeout=5
                    )
                    
                    if response.status_code == 200 and 'welcome' in response.text.lower():
                        return True
                except:
                    pass
            
            return False
            
        except:
            return False
    
    def test_web_interface(self, ip: str, port: int) -> List[HMIVulnerability]:
        """
        Test web interface vulnerabilities
        
        Args:
            ip: HMI IP address
            port: Web interface port
            
        Returns:
            List of vulnerabilities
        """
        logger.info(f"🌐 Testing web interface at {ip}:{port}...")
        
        vulnerabilities = []
        
        try:
            # Check for directory listing
            response = requests.get(f"http://{ip}:{port}/", timeout=5)
            
            if 'Index of' in response.text:
                vulnerabilities.append(HMIVulnerability(
                    title='Directory Listing Enabled',
                    description='Web server allows directory browsing',
                    severity='medium',
                    cvss_score=5.3,
                    cwe_id='CWE-548',
                    remediation='Disable directory listing in web server configuration'
                ))
            
            # Check for backup files
            backup_extensions = ['.bak', '.backup', '.old', '.orig']
            for ext in backup_extensions:
                try:
                    response = requests.get(f"http://{ip}:{port}/config{ext}", timeout=3)
                    if response.status_code == 200:
                        vulnerabilities.append(HMIVulnerability(
                            title='Backup File Exposed',
                            description=f'Backup file accessible: config{ext}',
                            severity='high',
                            cvss_score=7.5,
                            cwe_id='CWE-530',
                            remediation='Remove backup files from web-accessible directories'
                        ))
                except:
                    pass
            
            # Check for sensitive file exposure
            sensitive_files = ['/config.xml', '/system.ini', '/passwords.txt']
            for file in sensitive_files:
                try:
                    response = requests.get(f"http://{ip}:{port}{file}", timeout=3)
                    if response.status_code == 200:
                        vulnerabilities.append(HMIVulnerability(
                            title='Sensitive File Exposed',
                            description=f'Sensitive file accessible: {file}',
                            severity='critical',
                            cvss_score=9.0,
                            cwe_id='CWE-200',
                            remediation='Restrict access to sensitive configuration files'
                        ))
                except:
                    pass
            
        except Exception as e:
            logger.debug(f"  Web test error: {e}")
        
        return vulnerabilities
    
    def test_hmi(self, ip_address: str, vendor: str = 'Unknown',
                 model: str = 'Unknown') -> HMITestResult:
        """
        Comprehensive HMI security test
        
        Args:
            ip_address: HMI IP address
            vendor: HMI vendor
            model: HMI model
            
        Returns:
            Test results
        """
        logger.info(f"🔍 Testing HMI: {vendor} {model} at {ip_address}")
        
        result = HMITestResult(
            vendor=vendor,
            model=model,
            ip_address=ip_address,
            port=80
        )
        
        # Discover HMI
        discovery = self.discover_hmi(ip_address)
        
        # Test web interface
        if discovery['web_interface']:
            result.web_interface_exposed = True
            
            # Test default credentials
            if self.test_default_credentials(ip_address, 80, vendor):
                result.default_creds_found = True
                result.vulnerabilities.append(HMIVulnerability(
                    title='Default Credentials',
                    description='Default login credentials are active',
                    severity='critical',
                    cvss_score=9.8,
                    cwe_id='CWE-798',
                    remediation='Change default credentials immediately'
                ))
            
            # Test web vulnerabilities
            web_vulns = self.test_web_interface(ip_address, 80)
            result.vulnerabilities.extend(web_vulns)
        
        # Check for known vendor vulnerabilities
        vendor_vulns = self.KNOWN_VULNS.get(vendor, [])
        result.vulnerabilities.extend(vendor_vulns)
        
        # Check RDP/VNC exposure
        if discovery.get('rdp_exposed'):
            result.vulnerabilities.append(HMIVulnerability(
                title='RDP Exposed',
                description='Remote Desktop Protocol exposed to network',
                severity='medium',
                cvss_score=5.5,
                cwe_id='CWE-284',
                remediation='Restrict RDP access to authorized networks only'
            ))
        
        if discovery.get('vnc_exposed'):
            result.vulnerabilities.append(HMIVulnerability(
                title='VNC Exposed',
                description='VNC remote access exposed to network',
                severity='high',
                cvss_score=7.5,
                cwe_id='CWE-284',
                remediation='Restrict VNC access and enable authentication'
            ))
        
        # Calculate security score
        result.security_score = self._calculate_score(result)
        
        self.results.append(result)
        
        logger.info(f"  Vulnerabilities: {len(result.vulnerabilities)}")
        logger.info(f"  Security Score: {result.security_score}/10.0")
        
        return result
    
    def _calculate_score(self, result: HMITestResult) -> float:
        """Calculate security score (0-10)"""
        score = 10.0
        
        # Deduct for vulnerabilities
        for vuln in result.vulnerabilities:
            if vuln.severity == 'critical':
                score -= 2.5
            elif vuln.severity == 'high':
                score -= 2.0
            elif vuln.severity == 'medium':
                score -= 1.0
            elif vuln.severity == 'low':
                score -= 0.5
        
        # Deduct for default creds
        if result.default_creds_found:
            score -= 2.0
        
        # Deduct for exposed interfaces
        if result.web_interface_exposed:
            score -= 0.5
        
        return max(0.0, min(10.0, score))
    
    def test_historian(self, ip_address: str) -> Dict:
        """
        Test historian server
        
        Args:
            ip_address: Historian IP address
            
        Returns:
            Test results
        """
        logger.info(f"📊 Testing historian at {ip_address}...")
        
        results = {
            'ip_address': ip_address,
            'database_exposed': False,
            'api_exposed': False,
            'vulnerabilities': []
        }
        
        # Check common historian ports
        historian_ports = [
            (1433, 'SQL Server'),
            (1521, 'Oracle'),
            (5432, 'PostgreSQL'),
            (3306, 'MySQL'),
            (8080, 'REST API'),
            (4840, 'OPC UA')
        ]
        
        for port, service in historian_ports:
            if self._check_port(ip_address, port):
                logger.info(f"  {service} exposed on port {port}")
                
                if 'SQL' in service or 'Oracle' in service or 'MySQL' in service:
                    results['database_exposed'] = True
                elif 'API' in service or 'OPC' in service:
                    results['api_exposed'] = True
        
        return results
    
    def generate_report(self) -> str:
        """Generate HMI security test report"""
        report = []
        report.append("=" * 70)
        report.append("🏭 HMI/SCADA SECURITY ASSESSMENT REPORT")
        report.append("=" * 70)
        report.append(f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        report.append(f"Total HMIs Tested: {len(self.results)}")
        report.append("")
        
        for result in self.results:
            report.append(f"\n{'='*70}")
            report.append(f"HMI: {result.vendor} {result.model}")
            report.append(f"IP Address: {result.ip_address}:{result.port}")
            report.append(f"{'='*70}")
            report.append(f"Web Interface Exposed: {'YES' if result.web_interface_exposed else 'No'}")
            report.append(f"Default Credentials: {'FOUND ⚠️' if result.default_creds_found else 'Not Found'}")
            report.append(f"Security Score: {result.security_score}/10.0")
            
            if result.vulnerabilities:
                report.append("")
                report.append("VULNERABILITIES:")
                for vuln in result.vulnerabilities:
                    report.append(f"  ⚠️  [{vuln.severity.upper()}] {vuln.title}")
                    report.append(f"      {vuln.description}")
                    report.append(f"      CVSS: {vuln.cvss_score}")
                    report.append(f"      CWE: {vuln.cwe_id}")
                    report.append(f"      Remediation: {vuln.remediation}")
            
            report.append("")
            report.append("RECOMMENDATIONS:")
            report.append("  • Change all default credentials")
            report.append("  • Enable authentication on all interfaces")
            report.append("  • Restrict network access to HMI")
            report.append("  • Implement network segmentation")
            report.append("  • Regular security updates")
            report.append("  • Monitor HMI access logs")
        
        report.append("")
        report.append("=" * 70)
        
        return "\n".join(report)


def main():
    """Main entry point"""
    print("""
╔═══════════════════════════════════════════════════════════════╗
║     🏭 KALIAGENT v4.4.0 - HMI/SCADA TESTER                   ║
║                    Phase 10: Alpha 0.1.0                      ║
╚═══════════════════════════════════════════════════════════════╝

⚠️  CRITICAL SAFETY WARNING:
    HMI/SCADA testing can affect industrial processes!
    
    ONLY test on:
    ✅ Isolated lab systems you own
    ✅ Dedicated training facilities
    ✅ Systems with explicit written authorization

    """)
    
    # Initialize tester
    tester = HMISecurityTester(safety_mode=True, verbose=True)
    
    # Test simulated HMIs
    hmis = [
        {'ip': '192.168.10.200', 'vendor': 'Wonderware', 'model': 'InTouch'},
        {'ip': '192.168.10.201', 'vendor': 'Siemens', 'model': 'WinCC'},
        {'ip': '192.168.10.202', 'vendor': 'Rockwell', 'model': 'FactoryTalk'},
    ]
    
    for hmi in hmis:
        tester.test_hmi(hmi['ip'], hmi['vendor'], hmi['model'])
    
    # Generate report
    print("\n" + tester.generate_report())


if __name__ == "__main__":
    main()
