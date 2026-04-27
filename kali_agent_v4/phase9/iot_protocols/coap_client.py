#!/usr/bin/env python3
"""
📡 KaliAgent v4.3.0 - Phase 9: IoT Exploitation
CoAP Protocol Client & Security Testing

Tests CoAP (Constrained Application Protocol) for security vulnerabilities:
- Resource discovery
- Unauthorized GET/POST/PUT/DELETE
- DDoS amplification detection
- DTLS security testing
- Observable resource monitoring

Author: KaliAgent Team
Started: April 27, 2026
Status: Alpha (0.1.0)
"""

import logging
import socket
import struct
import json
import random
from typing import List, Dict, Optional, Tuple
from datetime import datetime
from dataclasses import dataclass, field
from urllib.parse import urlparse

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('CoAPClient')

# Try to import aiocoap, fall back to socket-based implementation
try:
    import asyncio
    import aiocoap
    import aiocoap.resource
    AIOCOAP_AVAILABLE = True
except ImportError:
    AIOCOAP_AVAILABLE = False
    logger.warning("aiocoap not installed, using socket-based implementation")
    logger.warning("Install with: pip install aiocoap")


@dataclass
class CoAPResource:
    """Represents a CoAP resource"""
    path: str
    methods: List[str] = field(default_factory=list)
    content_type: str = "unknown"
    observable: bool = False
    size: int = 0
    last_value: str = ""
    sensitive: bool = False
    writable: bool = False
    
    def to_dict(self) -> Dict:
        return {
            'path': self.path,
            'methods': self.methods,
            'content_type': self.content_type,
            'observable': self.observable,
            'size': self.size,
            'sensitive': self.sensitive,
            'writable': self.writable
        }


@dataclass
class CoAPServer:
    """Represents a CoAP server"""
    host: str
    port: int = 5683
    dtls_port: int = 5684
    resources: List[CoAPResource] = field(default_factory=list)
    anonymous_access: bool = False
    vulnerabilities: List[Dict] = field(default_factory=list)
    ddos_amplification: bool = False
    risk_score: float = 0.0
    
    def to_dict(self) -> Dict:
        return {
            'host': self.host,
            'port': self.port,
            'resource_count': len(self.resources),
            'anonymous_access': self.anonymous_access,
            'ddos_amplification': self.ddos_amplification,
            'vulnerabilities': self.vulnerabilities,
            'risk_score': self.risk_score
        }


class CoAPClient:
    """
    CoAP Security Testing Client
    
    Capabilities:
    - Server discovery
    - Resource enumeration (.well-known/core)
    - Method testing (GET, POST, PUT, DELETE)
    - DDoS amplification detection
    - DTLS security testing
    - Observable resource monitoring
    """
    
    VERSION = "0.1.0"
    
    # CoAP method codes
    METHOD_GET = 0x01
    METHOD_POST = 0x02
    METHOD_PUT = 0x03
    METHOD_DELETE = 0x04
    
    # CoAP option numbers
    OPT_URI_PATH = 11
    OPT_CONTENT_FORMAT = 12
    OPT_ACCEPT = 17
    OPT_OBSERVE = 6
    
    # Common CoAP resources to check
    COMMON_RESOURCES = [
        '.well-known/core',
        '.well-known/node',
        'api',
        'api/v1',
        'sensors',
        'actuators',
        'devices',
        'config',
        'status',
        'info',
        'version',
        'health',
        'led',
        'light',
        'temperature',
        'humidity',
        'motion',
        'door',
        'window',
        'lock',
        'switch',
        'power',
        'energy',
        'admin',
        'system',
        'debug',
    ]
    
    # Sensitive resource patterns
    SENSITIVE_PATTERNS = [
        'admin',
        'config',
        'credential',
        'password',
        'secret',
        'token',
        'key',
        'auth',
        'login',
        'user',
        'private',
        'secure',
        'cert',
        'firmware',
        'update',
        'boot',
    ]
    
    def __init__(self, host: str, port: int = 5683, timeout: int = 5, verbose: bool = True):
        """
        Initialize CoAP Client
        
        Args:
            host: Server hostname or IP
            port: CoAP port (default: 5683)
            timeout: Request timeout in seconds
            verbose: Enable verbose logging
        """
        self.host = host
        self.port = port
        self.timeout = timeout
        self.verbose = verbose
        
        if verbose:
            logger.setLevel(logging.DEBUG)
        
        self.server = CoAPServer(host=host, port=port)
        self.message_id = random.randint(0, 65535)
        
        logger.info(f"📡 CoAP Client v{self.VERSION} initialized")
        logger.info(f"🎯 Target: {host}:{port}")
    
    def _build_request(self, method: int, path: str, payload: bytes = None) -> bytes:
        """
        Build CoAP request packet
        
        Args:
            method: CoAP method code
            path: Resource path
            payload: Optional payload
            
        Returns:
            CoAP packet bytes
        """
        self.message_id = (self.message_id + 1) % 65536
        
        # CoAP header: Version(2) + Type(2) + TKL(4) | Code(8) | Message ID(16)
        header = struct.pack('!BBH',
            0x40,  # Version 1, Confirmable message
            method,
            self.message_id
        )
        
        # Token (4 bytes random)
        token = random.randbytes(4)
        
        # Options
        options = b''
        
        # URI-Path option
        path_bytes = path.encode('utf-8')
        if len(path_bytes) <= 12:
            options += struct.pack('!B', len(path_bytes) | (self.OPT_URI_PATH << 4))
        else:
            options += struct.pack('!BB', 13 | (self.OPT_URI_PATH << 4), len(path_bytes) - 13)
        options += path_bytes
        
        # Payload marker
        packet = header + token + options
        
        if payload:
            packet += b'\xff' + payload
        
        return packet
    
    def _send_request(self, method: int, path: str, payload: bytes = None) -> Tuple[bool, bytes]:
        """
        Send CoAP request
        
        Args:
            method: CoAP method code
            path: Resource path
            payload: Optional payload
            
        Returns:
            (success, response) tuple
        """
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            sock.settimeout(self.timeout)
            
            request = self._build_request(method, path, payload)
            sock.sendto(request, (self.host, self.port))
            
            response, addr = sock.recvfrom(4096)
            sock.close()
            
            return True, response
            
        except socket.timeout:
            logger.debug(f"⏱️  Timeout for {path}")
            return False, b''
        except Exception as e:
            logger.error(f"❌ Request error: {e}")
            return False, b''
    
    def _parse_response(self, response: bytes) -> Dict:
        """
        Parse CoAP response
        
        Args:
            response: Response bytes
            
        Returns:
            Parsed response data
        """
        if len(response) < 4:
            return {'error': 'Invalid response'}
        
        # Parse header
        ver_type_tkl = response[0]
        code = response[1]
        message_id = struct.unpack('!H', response[2:4])[0]
        
        # Token length
        token_len = ver_type_tkl & 0x0F
        
        # Parse options and payload
        offset = 4 + token_len
        options = []
        payload = b''
        
        if offset < len(response):
            if response[offset] == 0xFF:
                # Payload marker
                payload = response[offset + 1:]
            else:
                # Parse options (simplified)
                option_delta = 0
                while offset < len(response):
                    option_byte = response[offset]
                    if option_byte == 0xFF:
                        payload = response[offset + 1:]
                        break
                    
                    delta = (option_byte >> 4) & 0x0F
                    length = option_byte & 0x0F
                    offset += 1 + delta + length
                    option_delta += delta
        
        # Response code meaning
        code_class = code >> 5
        code_detail = code & 0x1F
        
        return {
            'code': code,
            'code_class': code_class,
            'code_detail': code_detail,
            'message_id': message_id,
            'payload': payload.decode('utf-8', errors='ignore') if payload else '',
            'success': code_class == 2  # 2.xx = Success
        }
    
    def discover_resources(self) -> List[CoAPResource]:
        """
        Discover CoAP resources
        
        Returns:
            List of discovered resources
        """
        logger.info("🔍 Discovering CoAP resources...")
        
        resources = []
        
        # Try .well-known/core (CoAP link format)
        success, response = self._send_request(self.METHOD_GET, '.well-known/core')
        
        if success and response:
            parsed = self._parse_response(response)
            if parsed['success']:
                logger.info("✅ Found .well-known/core")
                
                # Parse link format (simplified)
                links = parsed['payload'].split(',')
                for link in links:
                    if '<' in link and '>' in link:
                        path = link.split('<')[1].split('>')[0]
                        resource = CoAPResource(path=path)
                        
                        # Check for attributes
                        if 'obs' in link:
                            resource.observable = True
                        if 'POST' in link or 'PUT' in link:
                            resource.writable = True
                        
                        resources.append(resource)
                        logger.debug(f"  Found: {path}")
        
        # If no resources found, try common paths
        if not resources:
            logger.info("📋 Trying common resource paths...")
            
            for path in self.COMMON_RESOURCES:
                success, response = self._send_request(self.METHOD_GET, path)
                
                if success and response:
                    parsed = self._parse_response(response)
                    
                    if parsed['success']:
                        resource = CoAPResource(
                            path=path,
                            methods=['GET'],
                            size=len(parsed['payload']),
                            last_value=parsed['payload'][:100]
                        )
                        
                        # Check if sensitive
                        if any(pattern in path.lower() for pattern in self.SENSITIVE_PATTERNS):
                            resource.sensitive = True
                            logger.warning(f"⚠️  SENSITIVE: {path}")
                        
                        resources.append(resource)
                        logger.debug(f"  ✅ {path} ({len(parsed['payload'])} bytes)")
        
        self.server.resources = resources
        logger.info(f"📊 Discovered {len(resources)} resources")
        
        return resources
    
    def test_methods(self, resource: CoAPResource) -> Dict:
        """
        Test HTTP methods on resource
        
        Args:
            resource: CoAP resource to test
            
        Returns:
            Method test results
        """
        logger.debug(f"🔧 Testing methods on {resource.path}...")
        
        results = {
            'GET': False,
            'POST': False,
            'PUT': False,
            'DELETE': False
        }
        
        # Test GET
        success, response = self._send_request(self.METHOD_GET, resource.path)
        if success:
            parsed = self._parse_response(response)
            results['GET'] = parsed['success']
            resource.methods.append('GET')
        
        # Test POST
        success, response = self._send_request(
            self.METHOD_POST, 
            resource.path, 
            b'{"test": "data"}'
        )
        if success:
            parsed = self._parse_response(response)
            results['POST'] = parsed['success']
            if parsed['success']:
                resource.methods.append('POST')
                resource.writable = True
        
        # Test PUT
        success, response = self._send_request(
            self.METHOD_PUT, 
            resource.path, 
            b'{"test": "updated"}'
        )
        if success:
            parsed = self._parse_response(response)
            results['PUT'] = parsed['success']
            if parsed['success']:
                resource.methods.append('PUT')
                resource.writable = True
        
        # Test DELETE
        success, response = self._send_request(self.METHOD_DELETE, resource.path)
        if success:
            parsed = self._parse_response(response)
            results['DELETE'] = parsed['success']
            if parsed['success']:
                resource.methods.append('DELETE')
        
        return results
    
    def test_ddos_amplification(self) -> bool:
        """
        Test for DDoS amplification vulnerability
        
        Returns:
            True if vulnerable to amplification
        """
        logger.info("🚨 Testing DDoS amplification...")
        
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            sock.settimeout(self.timeout)
            
            # Send small request with spoofed source (simulated)
            request = self._build_request(self.METHOD_GET, '.well-known/core')
            
            # Measure request size
            request_size = len(request)
            
            # Send and measure response
            sock.sendto(request, (self.host, self.port))
            response, _ = sock.recvfrom(65535)
            response_size = len(response)
            
            sock.close()
            
            # Calculate amplification factor
            if request_size > 0:
                amplification = response_size / request_size
                
                logger.info(f"📊 Request: {request_size} bytes, Response: {response_size} bytes")
                logger.info(f"📊 Amplification factor: {amplification:.1f}x")
                
                if amplification > 10:
                    logger.warning(f"⚠️  VULNERABLE: {amplification:.1f}x amplification!")
                    self.server.ddos_amplification = True
                    self.server.vulnerabilities.append({
                        'type': 'ddos_amplification',
                        'severity': 'critical',
                        'cvss': 9.0,
                        'amplification_factor': amplification,
                        'description': f'DDoS amplification factor: {amplification:.1f}x'
                    })
                    return True
            
            return False
            
        except Exception as e:
            logger.error(f"❌ DDoS test error: {e}")
            return False
    
    def test_dtls(self) -> Dict:
        """
        Test DTLS security
        
        Returns:
            DTLS test results
        """
        logger.info("🔒 Testing DTLS security...")
        
        results = {
            'dtls_enabled': False,
            'dtls_port': self.server.dtls_port,
            'vulnerabilities': []
        }
        
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            sock.settimeout(self.timeout)
            
            # Try to connect to DTLS port
            sock.sendto(b'\x16\xfe\xfd', (self.host, self.server.dtls_port))
            
            # Check for response
            sock.settimeout(2)
            try:
                response, _ = sock.recvfrom(1024)
                if response:
                    results['dtls_enabled'] = True
                    logger.info(f"✅ DTLS enabled on port {self.server.dtls_port}")
            except socket.timeout:
                logger.info(f"ℹ️  DTLS not enabled on port {self.server.dtls_port}")
            
            sock.close()
            
        except Exception as e:
            logger.debug(f"DTLS test error: {e}")
        
        return results
    
    def calculate_risk_score(self) -> float:
        """
        Calculate server risk score (0-10)
        
        Returns:
            Risk score
        """
        score = 5.0  # Base score
        
        # Anonymous access (CoAP is typically unauthenticated)
        if self.server.anonymous_access:
            score += 1.0
        
        # DDoS amplification
        if self.server.ddos_amplification:
            score += 3.0
        
        # Writable resources
        writable_count = sum(1 for r in self.server.resources if r.writable)
        if writable_count > 0:
            score += min(2.0, writable_count * 0.5)
        
        # Sensitive resources
        sensitive_count = sum(1 for r in self.server.resources if r.sensitive)
        if sensitive_count > 0:
            score += min(2.0, sensitive_count * 0.5)
        
        # Vulnerabilities
        for vuln in self.server.vulnerabilities:
            if vuln.get('severity') == 'critical':
                score += 1.5
            elif vuln.get('severity') == 'high':
                score += 1.0
        
        self.server.risk_score = min(10.0, score)
        return self.server.risk_score
    
    def generate_report(self, output_format: str = 'text') -> str:
        """
        Generate CoAP security assessment report
        
        Args:
            output_format: 'text' or 'json'
            
        Returns:
            Formatted report
        """
        logger.info("📊 Generating report...")
        
        self.calculate_risk_score()
        
        if output_format == 'json':
            return json.dumps(self.server.to_dict(), indent=2, default=str)
        
        # Text format
        report = []
        report.append("=" * 70)
        report.append("📡 CoAP SECURITY ASSESSMENT REPORT")
        report.append("=" * 70)
        report.append(f"Server: {self.server.host}:{self.server.port}")
        report.append(f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        report.append(f"Risk Score: {self.server.risk_score}/10.0")
        report.append("")
        
        report.append("FINDINGS:")
        report.append("-" * 70)
        
        if self.server.ddos_amplification:
            report.append("🚨 CRITICAL: DDoS amplification vulnerability!")
        
        for vuln in self.server.vulnerabilities:
            report.append(f"⚠️  {vuln['severity'].upper()}: {vuln['description']}")
        
        report.append("")
        report.append("RESOURCES DISCOVERED:")
        report.append("-" * 70)
        
        for resource in self.server.resources[:20]:
            methods = ', '.join(resource.methods) if resource.methods else 'GET'
            flags = []
            if resource.sensitive:
                flags.append('SENSITIVE')
            if resource.writable:
                flags.append('WRITABLE')
            if resource.observable:
                flags.append('OBSERVABLE')
            
            flag_str = f" [{', '.join(flags)}]" if flags else ""
            report.append(f"  {resource.path} ({methods}){flag_str}")
        
        if len(self.server.resources) > 20:
            report.append(f"  ... and {len(self.server.resources) - 20} more")
        
        report.append("")
        report.append("RECOMMENDATIONS:")
        report.append("-" * 70)
        report.append("1. Implement DTLS for encryption")
        report.append("2. Add authentication mechanism")
        report.append("3. Configure ACLs for resource access")
        report.append("4. Disable unused methods (POST, PUT, DELETE)")
        report.append("5. Rate limit responses to prevent amplification")
        report.append("6. Monitor and log all CoAP requests")
        report.append("")
        report.append("=" * 70)
        
        return "\n".join(report)
    
    def run_assessment(self) -> str:
        """
        Run complete CoAP security assessment
        
        Returns:
            Assessment report
        """
        logger.info("🚀 Starting CoAP security assessment...")
        
        # Step 1: Discover resources
        resources = self.discover_resources()
        
        # Step 2: Test methods on each resource
        for resource in resources:
            self.test_methods(resource)
        
        # Step 3: Test DDoS amplification
        self.test_ddos_amplification()
        
        # Step 4: Test DTLS
        dtls_results = self.test_dtls()
        
        # Generate report
        report = self.generate_report()
        
        logger.info("✅ Assessment complete!")
        return report


def main():
    """Main entry point"""
    print("""
╔═══════════════════════════════════════════════════════════════╗
║     📡 KALIAGENT v4.3.0 - CoAP SECURITY TESTER               ║
║                    Phase 9: Alpha 0.1.0                       ║
╚═══════════════════════════════════════════════════════════════╝
    """)
    
    import sys
    host = sys.argv[1] if len(sys.argv) > 1 else "192.168.1.100"
    port = int(sys.argv[2]) if len(sys.argv) > 2 else 5683
    
    # Initialize client
    coap_client = CoAPClient(host=host, port=port, verbose=True)
    
    # Run assessment
    report = coap_client.run_assessment()
    
    # Print report
    print("\n" + report)
    
    # Save to file
    with open(f'coap_assessment_{host.replace(".", "_")}.txt', 'w') as f:
        f.write(report)
    
    print(f"\n✅ Report saved to: coap_assessment_{host.replace('.', '_')}.txt")


if __name__ == "__main__":
    main()
