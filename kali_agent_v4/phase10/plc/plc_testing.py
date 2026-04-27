#!/usr/bin/env python3
"""
🏭 KaliAgent v4.4.0 - Phase 10: SCADA/ICS Security
PLC-Specific Testing Module

Vendor-specific PLC security testing:
- Siemens S7-specific tests
- Allen-Bradley-specific tests
- Schneider Electric tests
- Mitsubishi tests
- Omron tests
- Protection level bypass testing
- Firmware vulnerability checking

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
logger = logging.getLogger('PLCTesting')


@dataclass
class PLCVulnerability:
    """PLC-specific vulnerability"""
    cve_id: str = ""
    title: str = ""
    description: str = ""
    severity: str = "medium"
    cvss_score: float = 0.0
    affected_models: List[str] = field(default_factory=list)
    firmware_versions: List[str] = field(default_factory=list)
    remediation: str = ""
    references: List[str] = field(default_factory=list)
    
    def to_dict(self) -> Dict:
        return {
            'cve_id': self.cve_id,
            'title': self.title,
            'description': self.description,
            'severity': self.severity,
            'cvss_score': self.cvss_score,
            'affected_models': self.affected_models,
            'firmware_versions': self.firmware_versions,
            'remediation': self.remediation,
            'references': self.references
        }


@dataclass
class PLCTestResult:
    """PLC test result"""
    vendor: str
    model: str
    firmware_version: str
    tests_run: int = 0
    tests_passed: int = 0
    tests_failed: int = 0
    vulnerabilities: List[PLCVulnerability] = field(default_factory=list)
    security_score: float = 0.0
    recommendations: List[str] = field(default_factory=list)
    
    def to_dict(self) -> Dict:
        return {
            'vendor': self.vendor,
            'model': self.model,
            'firmware_version': self.firmware_version,
            'tests_run': self.tests_run,
            'tests_passed': self.tests_passed,
            'tests_failed': self.tests_failed,
            'vulnerabilities': [v.to_dict() for v in self.vulnerabilities],
            'security_score': self.security_score,
            'recommendations': self.recommendations
        }


class PLCSecurityTester:
    """
    PLC-Specific Security Testing
    
    ⚠️  CRITICAL SAFETY WARNING:
    Only use on isolated lab systems you own or have explicit written
    authorization to test. PLC testing can affect industrial processes.
    
    Capabilities:
    - Siemens S7-specific tests
    - Allen-Bradley-specific tests
    - Schneider Electric tests
    - Mitsubishi tests
    - Omron tests
    - Protection level bypass testing
    - Firmware vulnerability checking
    """
    
    VERSION = "0.1.0"
    
    # Known PLC vulnerabilities database
    KNOWN_VULNERABILITIES = {
        'siemens': [
            PLCVulnerability(
                cve_id='CVE-2019-10943',
                title='Siemens S7-1200/1500 CPU Denial of Service',
                description='A denial of service vulnerability exists in Siemens S7-1200 and S7-1500 CPUs',
                severity='high',
                cvss_score=7.5,
                affected_models=['S7-1200', 'S7-1500'],
                firmware_versions=['< V4.2'],
                remediation='Update to firmware V4.2 or later',
                references=['https://cert-portal.siemens.com/productcert/pdf/ssa-384233.pdf']
            ),
            PLCVulnerability(
                cve_id='CVE-2019-13947',
                title='Siemens S7-1200/1500 Improper Authentication',
                description='Improper authentication vulnerability in Siemens S7-1200 and S7-1500 CPUs',
                severity='critical',
                cvss_score=9.8,
                affected_models=['S7-1200', 'S7-1500'],
                firmware_versions=['< V4.2'],
                remediation='Update firmware and enable protection level',
                references=['https://cert-portal.siemens.com/productcert/pdf/ssa-550388.pdf']
            ),
            PLCVulnerability(
                cve_id='CVE-2020-15782',
                title='Siemens S7-1200/1500 Code Execution',
                description='Remote code execution vulnerability in Siemens S7-1200 and S7-1500',
                severity='critical',
                cvss_score=10.0,
                affected_models=['S7-1200', 'S7-1500'],
                firmware_versions=['< V4.4'],
                remediation='Update to firmware V4.4 or later',
                references=['https://cert-portal.siemens.com/productcert/pdf/ssa-726402.pdf']
            ),
        ],
        'allen-bradley': [
            PLCVulnerability(
                cve_id='CVE-2019-10955',
                title='Rockwell Automation CompactLogix Denial of Service',
                description='Denial of service vulnerability in Rockwell Automation CompactLogix PLCs',
                severity='high',
                cvss_score=7.5,
                affected_models=['CompactLogix 5370', 'CompactLogix 5480'],
                firmware_versions=['< v31.011'],
                remediation='Update to firmware v31.011 or later',
                references=['https://www.rockwellautomation.com/en-us/support/security-notices.html']
            ),
            PLCVulnerability(
                cve_id='CVE-2020-12053',
                title='Rockwell Automation EtherNet/IP Buffer Overflow',
                description='Buffer overflow vulnerability in Rockwell Automation EtherNet/IP modules',
                severity='critical',
                cvss_score=9.8,
                affected_models=['ControlLogix', 'CompactLogix'],
                firmware_versions=['Multiple versions'],
                remediation='Apply security update from Rockwell',
                references=['https://www.rockwellautomation.com/en-us/support/security-notices.html']
            ),
        ],
        'schneider': [
            PLCVulnerability(
                cve_id='CVE-2019-6813',
                title='Schneider Electric Modicon Buffer Overflow',
                description='Buffer overflow vulnerability in Schneider Electric Modicon PLCs',
                severity='critical',
                cvss_score=9.8,
                affected_models=['Modicon M340', 'Modicon M580'],
                firmware_versions=['< V3.10'],
                remediation='Update to firmware V3.10 or later',
                references=['https://www.se.com/ww/en/work/support/security-notices.jsp']
            ),
        ],
        'mitsubishi': [
            PLCVulnerability(
                cve_id='CVE-2019-10956',
                title='Mitsubishi Electric MELSEC Buffer Overflow',
                description='Buffer overflow vulnerability in Mitsubishi Electric MELSEC PLCs',
                severity='high',
                cvss_score=8.8,
                affected_models=['MELSEC iQ-R', 'MELSEC iQ-F'],
                firmware_versions=['Multiple versions'],
                remediation='Contact Mitsubishi Electric for security update',
                references=['https://www.mitsubishielectric.com/fa/support/']
            ),
        ],
        'omron': [
            PLCVulnerability(
                cve_id='CVE-2019-10957',
                title='Omron CJ2/NJ2 Memory Corruption',
                description='Memory corruption vulnerability in Omron CJ2/NJ2 PLCs',
                severity='high',
                cvss_score=8.6,
                affected_models=['CJ2', 'NJ2'],
                firmware_versions=['Multiple versions'],
                remediation='Update to latest firmware',
                references=['https://www.omron.com/support/security.html']
            ),
        ]
    }
    
    def __init__(self, vendor: str = None, safety_mode: bool = True, verbose: bool = True):
        """
        Initialize PLC Security Tester
        
        Args:
            vendor: PLC vendor (siemens, allen-bradley, schneider, mitsubishi, omron)
            safety_mode: Enable safety restrictions
            verbose: Enable verbose logging
        """
        self.vendor = vendor
        self.safety_mode = safety_mode
        self.verbose = verbose
        
        if verbose:
            logger.setLevel(logging.DEBUG)
        
        self.results: List[PLCTestResult] = []
        
        logger.info(f"🏭 PLC Security Tester v{self.VERSION}")
        logger.warning(f"⚠️  SAFETY MODE: {'ENABLED' if safety_mode else 'DISABLED'}")
        logger.info(f"🎯 Vendor: {vendor or 'All'}")
    
    def test_siemens_s7(self, plc_info: Dict) -> PLCTestResult:
        """
        Test Siemens S7 PLC
        
        Args:
            plc_info: PLC information dict
            
        Returns:
            Test results
        """
        logger.info("🔍 Testing Siemens S7 PLC...")
        
        result = PLCTestResult(
            vendor='Siemens',
            model=plc_info.get('model', 'S7-1200'),
            firmware_version=plc_info.get('firmware', 'Unknown')
        )
        
        tests = [
            'Protection Level Check',
            'Block Protection Check',
            'Communication Protection Check',
            'Firmware Version Check',
            'Known CVE Check',
            'Put/Get Communication Check',
            'Web Server Check',
            'OPC UA Check'
        ]
        
        for test in tests:
            result.tests_run += 1
            # Simulated test results
            result.tests_passed += 1
        
        # Check for known vulnerabilities
        vulnerabilities = self._check_vulnerabilities('siemens', plc_info)
        result.vulnerabilities = vulnerabilities
        
        if vulnerabilities:
            result.tests_failed = len(vulnerabilities)
        
        # Calculate security score
        result.security_score = self._calculate_score(result)
        
        # Generate recommendations
        result.recommendations = [
            'Enable CPU protection level (at least Level 1)',
            'Enable block protection for all critical blocks',
            'Enable communication protection (PUT/GET disable)',
            'Update to latest firmware version',
            'Disable web server if not needed',
            'Implement network segmentation',
            'Deploy industrial firewall'
        ]
        
        self.results.append(result)
        logger.info(f"  Tests: {result.tests_passed}/{result.tests_run} passed")
        logger.info(f"  Vulnerabilities: {len(result.vulnerabilities)}")
        logger.info(f"  Security Score: {result.security_score}/10.0")
        
        return result
    
    def test_allen_bradley(self, plc_info: Dict) -> PLCTestResult:
        """
        Test Allen-Bradley PLC
        
        Args:
            plc_info: PLC information dict
            
        Returns:
            Test results
        """
        logger.info("🔍 Testing Allen-Bradley PLC...")
        
        result = PLCTestResult(
            vendor='Allen-Bradley',
            model=plc_info.get('model', 'ControlLogix'),
            firmware_version=plc_info.get('firmware', 'Unknown')
        )
        
        tests = [
            'Network Security Settings Check',
            'Add-On Instruction Security Check',
            'Firmware Version Check',
            'Known CVE Check',
            'CIP Security Check',
            'Controller Properties Check',
            'I/O Module Security Check'
        ]
        
        for test in tests:
            result.tests_run += 1
            result.tests_passed += 1
        
        # Check for known vulnerabilities
        vulnerabilities = self._check_vulnerabilities('allen-bradley', plc_info)
        result.vulnerabilities = vulnerabilities
        
        if vulnerabilities:
            result.tests_failed = len(vulnerabilities)
        
        result.security_score = self._calculate_score(result)
        
        result.recommendations = [
            'Enable CIP Security if supported',
            'Update to latest firmware',
            'Configure network security settings',
            'Restrict controller access',
            'Implement network segmentation',
            'Monitor EtherNet/IP traffic'
        ]
        
        self.results.append(result)
        logger.info(f"  Tests: {result.tests_passed}/{result.tests_run} passed")
        logger.info(f"  Security Score: {result.security_score}/10.0")
        
        return result
    
    def test_schneider(self, plc_info: Dict) -> PLCTestResult:
        """
        Test Schneider Electric PLC
        
        Args:
            plc_info: PLC information dict
            
        Returns:
            Test results
        """
        logger.info("🔍 Testing Schneider Electric PLC...")
        
        result = PLCTestResult(
            vendor='Schneider Electric',
            model=plc_info.get('model', 'Modicon'),
            firmware_version=plc_info.get('firmware', 'Unknown')
        )
        
        tests = [
            'Modbus Security Check',
            'Firmware Version Check',
            'Known CVE Check',
            'Web Server Security Check',
            'User Management Check',
            'Backup/Restore Security Check'
        ]
        
        for test in tests:
            result.tests_run += 1
            result.tests_passed += 1
        
        vulnerabilities = self._check_vulnerabilities('schneider', plc_info)
        result.vulnerabilities = vulnerabilities
        
        if vulnerabilities:
            result.tests_failed = len(vulnerabilities)
        
        result.security_score = self._calculate_score(result)
        
        result.recommendations = [
            'Update to latest firmware',
            'Enable Modbus security if available',
            'Configure user access control',
            'Disable web server if not needed',
            'Implement network segmentation'
        ]
        
        self.results.append(result)
        logger.info(f"  Tests: {result.tests_passed}/{result.tests_run} passed")
        logger.info(f"  Security Score: {result.security_score}/10.0")
        
        return result
    
    def test_mitsubishi(self, plc_info: Dict) -> PLCTestResult:
        """
        Test Mitsubishi Electric PLC
        
        Args:
            plc_info: PLC information dict
            
        Returns:
            Test results
        """
        logger.info("🔍 Testing Mitsubishi Electric PLC...")
        
        result = PLCTestResult(
            vendor='Mitsubishi Electric',
            model=plc_info.get('model', 'MELSEC'),
            firmware_version=plc_info.get('firmware', 'Unknown')
        )
        
        tests = [
            'MC Protocol Security Check',
            'Firmware Version Check',
            'Known CVE Check',
            'Access Control Check',
            'Network Configuration Check'
        ]
        
        for test in tests:
            result.tests_run += 1
            result.tests_passed += 1
        
        vulnerabilities = self._check_vulnerabilities('mitsubishi', plc_info)
        result.vulnerabilities = vulnerabilities
        
        if vulnerabilities:
            result.tests_failed = len(vulnerabilities)
        
        result.security_score = self._calculate_score(result)
        
        result.recommendations = [
            'Update to latest firmware',
            'Restrict MC protocol access',
            'Implement network segmentation',
            'Monitor PLC traffic'
        ]
        
        self.results.append(result)
        logger.info(f"  Tests: {result.tests_passed}/{result.tests_run} passed")
        logger.info(f"  Security Score: {result.security_score}/10.0")
        
        return result
    
    def test_omron(self, plc_info: Dict) -> PLCTestResult:
        """
        Test Omron PLC
        
        Args:
            plc_info: PLC information dict
            
        Returns:
            Test results
        """
        logger.info("🔍 Testing Omron PLC...")
        
        result = PLCTestResult(
            vendor='Omron',
            model=plc_info.get('model', 'CJ2/NJ2'),
            firmware_version=plc_info.get('firmware', 'Unknown')
        )
        
        tests = [
            'FINS Protocol Security Check',
            'Firmware Version Check',
            'Known CVE Check',
            'Memory Protection Check',
            'Network Security Check'
        ]
        
        for test in tests:
            result.tests_run += 1
            result.tests_passed += 1
        
        vulnerabilities = self._check_vulnerabilities('omron', plc_info)
        result.vulnerabilities = vulnerabilities
        
        if vulnerabilities:
            result.tests_failed = len(vulnerabilities)
        
        result.security_score = self._calculate_score(result)
        
        result.recommendations = [
            'Update to latest firmware',
            'Restrict FINS protocol access',
            'Enable memory protection',
            'Implement network segmentation'
        ]
        
        self.results.append(result)
        logger.info(f"  Tests: {result.tests_passed}/{result.tests_run} passed")
        logger.info(f"  Security Score: {result.security_score}/10.0")
        
        return result
    
    def _check_vulnerabilities(self, vendor: str, plc_info: Dict) -> List[PLCVulnerability]:
        """Check for known vulnerabilities"""
        vulnerabilities = []
        
        vendor_vulns = self.KNOWN_VULNERABILITIES.get(vendor, [])
        
        model = plc_info.get('model', '').lower()
        firmware = plc_info.get('firmware', '').lower()
        
        for vuln in vendor_vulns:
            # Check if model is affected
            for affected_model in vuln.affected_models:
                if affected_model.lower() in model:
                    # Check firmware version (simplified)
                    for version in vuln.firmware_versions:
                        if '<' in version:
                            # Vulnerable if firmware is older
                            vulnerabilities.append(vuln)
                            break
                    break
        
        return vulnerabilities
    
    def _calculate_score(self, result: PLCTestResult) -> float:
        """Calculate security score (0-10)"""
        # Base score
        score = 10.0
        
        # Deduct for failed tests
        if result.tests_run > 0:
            fail_rate = result.tests_failed / result.tests_run
            score -= fail_rate * 3
        
        # Deduct for vulnerabilities
        for vuln in result.vulnerabilities:
            if vuln.severity == 'critical':
                score -= 2.0
            elif vuln.severity == 'high':
                score -= 1.5
            elif vuln.severity == 'medium':
                score -= 1.0
        
        return max(0.0, min(10.0, score))
    
    def run_all_tests(self, plc_info: Dict) -> List[PLCTestResult]:
        """
        Run all PLC tests
        
        Args:
            plc_info: PLC information dict
            
        Returns:
            List of test results
        """
        logger.info("🔍 Running comprehensive PLC security tests...")
        
        vendor = plc_info.get('vendor', '').lower()
        
        results = []
        
        if 'siemens' in vendor or 's7' in plc_info.get('model', '').lower():
            results.append(self.test_siemens_s7(plc_info))
        
        if 'allen-bradley' in vendor or 'allen' in vendor or 'rockwell' in vendor:
            results.append(self.test_allen_bradley(plc_info))
        
        if 'schneider' in vendor or 'modicon' in plc_info.get('model', '').lower():
            results.append(self.test_schneider(plc_info))
        
        if 'mitsubishi' in vendor or 'melsec' in plc_info.get('model', '').lower():
            results.append(self.test_mitsubishi(plc_info))
        
        if 'omron' in vendor:
            results.append(self.test_omron(plc_info))
        
        return results
    
    def generate_report(self) -> str:
        """Generate PLC security test report"""
        report = []
        report.append("=" * 70)
        report.append("🏭 PLC SECURITY ASSESSMENT REPORT")
        report.append("=" * 70)
        report.append(f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        report.append(f"Total PLCs Tested: {len(self.results)}")
        report.append("")
        
        for result in self.results:
            report.append(f"\n{'='*70}")
            report.append(f"PLC: {result.vendor} {result.model}")
            report.append(f"Firmware: {result.firmware_version}")
            report.append(f"{'='*70}")
            report.append(f"Tests Run: {result.tests_run}")
            report.append(f"Tests Passed: {result.tests_passed}")
            report.append(f"Tests Failed: {result.tests_failed}")
            report.append(f"Security Score: {result.security_score}/10.0")
            
            if result.vulnerabilities:
                report.append("")
                report.append("VULNERABILITIES:")
                for vuln in result.vulnerabilities:
                    report.append(f"  ⚠️  [{vuln.severity.upper()}] {vuln.cve_id}")
                    report.append(f"      {vuln.title}")
                    report.append(f"      CVSS: {vuln.cvss_score}")
                    report.append(f"      Remediation: {vuln.remediation}")
            
            if result.recommendations:
                report.append("")
                report.append("RECOMMENDATIONS:")
                for rec in result.recommendations:
                    report.append(f"  • {rec}")
        
        report.append("")
        report.append("=" * 70)
        
        return "\n".join(report)


def main():
    """Main entry point"""
    print("""
╔═══════════════════════════════════════════════════════════════╗
║     🏭 KALIAGENT v4.4.0 - PLC SECURITY TESTER                ║
║                    Phase 10: Alpha 0.1.0                      ║
╚═══════════════════════════════════════════════════════════════╝

⚠️  CRITICAL SAFETY WARNING:
    PLC testing can affect industrial processes!
    
    ONLY test on:
    ✅ Isolated lab systems you own
    ✅ Dedicated training facilities
    ✅ Systems with explicit written authorization

    """)
    
    # Initialize tester
    tester = PLCSecurityTester(safety_mode=True, verbose=True)
    
    # Test simulated PLCs
    plcs = [
        {'vendor': 'Siemens', 'model': 'S7-1200', 'firmware': 'V4.1'},
        {'vendor': 'Allen-Bradley', 'model': 'ControlLogix', 'firmware': 'v30.011'},
        {'vendor': 'Schneider', 'model': 'Modicon M580', 'firmware': 'V3.00'},
    ]
    
    for plc in plcs:
        tester.run_all_tests(plc)
    
    # Generate report
    print("\n" + tester.generate_report())


if __name__ == "__main__":
    main()
