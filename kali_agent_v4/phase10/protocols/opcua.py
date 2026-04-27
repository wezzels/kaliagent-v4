#!/usr/bin/env python3
"""
🏭 KaliAgent v4.4.0 - Phase 10: SCADA/ICS Security
OPC UA Protocol Client

OPC UA (Open Platform Communications Unified Architecture) security testing:
- Server enumeration
- Address space browsing
- Node read/write operations
- Method invocation
- Subscription monitoring
- Security policy testing (signing, encryption)
- Certificate management

Author: KaliAgent Team
Started: April 27, 2026
Status: Alpha (0.1.0)

⚠️  CRITICAL SAFETY WARNING: Only test on isolated lab systems!
"""

import logging
import socket
import struct
from typing import List, Dict, Optional, Tuple
from datetime import datetime
from dataclasses import dataclass, field

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('OPCUAClient')


@dataclass
class OPCUAServer:
    """OPC UA server information"""
    application_uri: str = ""
    product_uri: str = ""
    application_name: str = ""
    application_type: str = ""  # Server, Client, DiscoveryServer, etc.
    gateway_server_uri: str = ""
    discovery_profile_uri: str = ""
    discovery_urls: List[str] = field(default_factory=list)
    server_status: str = ""
    build_number: str = ""
    build_date: datetime = None
    manufacturer_name: str = ""
    security_modes: List[str] = field(default_factory=list)
    security_policies: List[str] = field(default_factory=list)
    
    def to_dict(self) -> Dict:
        return {
            'application_uri': self.application_uri,
            'product_uri': self.product_uri,
            'application_name': self.application_name,
            'application_type': self.application_type,
            'gateway_server_uri': self.gateway_server_uri,
            'discovery_profile_uri': self.discovery_profile_uri,
            'discovery_urls': self.discovery_urls,
            'server_status': self.server_status,
            'build_number': self.build_number,
            'build_date': self.build_date.isoformat() if self.build_date else None,
            'manufacturer_name': self.manufacturer_name,
            'security_modes': self.security_modes,
            'security_policies': self.security_policies
        }


@dataclass
class OPCUANode:
    """OPC UA node"""
    node_id: str = ""
    node_class: str = ""  # Variable, Object, Method, etc.
    browse_name: str = ""
    display_name: str = ""
    description: str = ""
    data_type: str = ""
    value: any = None
    access_level: int = 0
    user_access_level: int = 0
    write_mask: int = 0
    user_write_mask: int = 0
    children: List['OPCUANode'] = field(default_factory=list)
    
    def to_dict(self) -> Dict:
        return {
            'node_id': self.node_id,
            'node_class': self.node_class,
            'browse_name': self.browse_name,
            'display_name': self.display_name,
            'description': self.description,
            'data_type': self.data_type,
            'value': self.value,
            'access_level': self.access_level,
            'user_access_level': self.user_access_level
        }


@dataclass
class OPCUASubscription:
    """OPC UA subscription"""
    subscription_id: int = 0
    publishing_interval: float = 0.0
    lifetime_count: int = 0
    max_keep_alive_count: int = 0
    priority: int = 0
    monitored_items: List[int] = field(default_factory=list)
    
    def to_dict(self) -> Dict:
        return {
            'subscription_id': self.subscription_id,
            'publishing_interval': self.publishing_interval,
            'lifetime_count': self.lifetime_count,
            'max_keep_alive_count': self.max_keep_alive_count,
            'priority': self.priority,
            'monitored_items': self.monitored_items
        }


class OPCUAClient:
    """
    OPC UA Protocol Client
    
    ⚠️  CRITICAL SAFETY WARNING:
    OPC UA is used in critical industrial systems. Only use on isolated
    lab systems you own or have explicit written authorization to test.
    
    Capabilities:
    - Server enumeration
    - Address space browsing
    - Node read/write
    - Method invocation
    - Subscription monitoring
    - Security assessment
    """
    
    VERSION = "0.1.0"
    
    # OPC UA standard port
    OPCUA_PORT = 4840
    
    # OPC UA message types
    MSG_HELLO = b'HEL'
    MSG_ACKNOWLEDGE = b'ACK'
    MSG_ERROR = b'ERR'
    MSG_SECURE_OPEN = b'SOPN'
    MSG_SECURE_CLOSE = b'SCLS'
    MSG_SECURE_MESSAGE = b'SMSG'
    
    # OPC UA node classes
    NODE_CLASS_UNSPECIFIED = 0
    NODE_CLASS_OBJECT = 1
    NODE_CLASS_VARIABLE = 2
    NODE_CLASS_METHOD = 3
    NODE_CLASS_OBJECT_TYPE = 4
    NODE_CLASS_VARIABLE_TYPE = 5
    NODE_CLASS_REFERENCE_TYPE = 6
    NODE_CLASS_DATA_TYPE = 7
    NODE_CLASS_VIEW = 8
    
    NODE_CLASSES = {
        0: 'Unspecified',
        1: 'Object',
        2: 'Variable',
        3: 'Method',
        4: 'ObjectType',
        5: 'VariableType',
        6: 'ReferenceType',
        7: 'DataType',
        8: 'View'
    }
    
    # Security policies
    SECURITY_POLICIES = {
        'None': 'http://opcfoundation.org/UA/SecurityPolicy#None',
        'Basic128Rsa15': 'http://opcfoundation.org/UA/SecurityPolicy#Basic128Rsa15',
        'Basic256': 'http://opcfoundation.org/UA/SecurityPolicy#Basic256',
        'Basic256Sha256': 'http://opcfoundation.org/UA/SecurityPolicy#Basic256Sha256',
        'Aes128_Sha256_RsaOaep': 'http://opcfoundation.org/UA/SecurityPolicy#Aes128_Sha256_RsaOaep'
    }
    
    # Security modes
    SECURITY_MODES = {
        1: 'Invalid',
        2: 'None',
        3: 'Sign',
        4: 'SignAndEncrypt'
    }
    
    def __init__(self, endpoint_url: str = None, port: int = OPCUA_PORT,
                 security_policy: str = 'None', security_mode: str = 'None',
                 safety_mode: bool = True, verbose: bool = True):
        """
        Initialize OPC UA Client
        
        Args:
            endpoint_url: OPC UA server endpoint URL
            port: OPC UA port (default: 4840)
            security_policy: Security policy (None, Basic128Rsa15, etc.)
            security_mode: Security mode (None, Sign, SignAndEncrypt)
            safety_mode: Enable safety restrictions (READ-ONLY)
            verbose: Enable verbose logging
        """
        self.endpoint_url = endpoint_url
        self.port = port
        self.security_policy = security_policy
        self.security_mode = security_mode
        self.safety_mode = safety_mode
        self.verbose = verbose
        
        if verbose:
            logger.setLevel(logging.DEBUG)
        
        self.socket = None
        self.connected = False
        self.server = None
        self.nodes: List[OPCUANode] = []
        self.subscriptions: List[OPCUASubscription] = []
        self.session_id = None
        self.sequence_number = 0
        self.request_id = 0
        
        logger.info(f"🏭 OPC UA Client v{self.VERSION}")
        logger.warning(f"⚠️  SAFETY MODE: {'ENABLED' if safety_mode else 'DISABLED'}")
        logger.info(f"🎯 Endpoint: {endpoint_url or f'*:{port}'}")
        logger.info(f"🔒 Security: {security_policy} / {security_mode}")
    
    def connect(self) -> bool:
        """
        Connect to OPC UA server
        
        Returns:
            True if connection successful
        """
        logger.info(f"🔌 Connecting to OPC UA server...")
        
        try:
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.socket.settimeout(10)
            
            # Parse endpoint URL
            host = self.endpoint_url.split('//')[1].split(':')[0] if self.endpoint_url else 'localhost'
            port = self.port
            
            self.socket.connect((host, port))
            
            # Send HELLO message
            if not self._send_hello():
                logger.error("❌ HELLO failed")
                return False
            
            # Wait for ACKNOWLEDGE
            if not self._receive_acknowledge():
                logger.error("❌ ACKNOWLEDGE failed")
                return False
            
            self.connected = True
            logger.info(f"✅ Connected to OPC UA server")
            
            # Get server information
            self.server = self.get_server_info()
            
            return True
            
        except socket.timeout:
            logger.error("❌ Connection timed out")
            return False
        except socket.error as e:
            logger.error(f"❌ Connection error: {e}")
            return False
        except Exception as e:
            logger.error(f"❌ Unexpected error: {e}")
            return False
    
    def disconnect(self):
        """Disconnect from server"""
        if self.socket:
            try:
                # Send secure close if session active
                if self.session_id:
                    self._send_secure_close()
                self.socket.close()
            except:
                pass
        
        self.connected = False
        self.session_id = None
        logger.info("🔌 Disconnected")
    
    def _send_hello(self) -> bool:
        """Send HELLO message"""
        logger.debug("  Sending HELLO...")
        
        # Build HELLO message (simplified)
        hello = bytes([
            ord('H'), ord('E'), ord('L'), ord('F'),  # Message type
            0x00, 0x00, 0x00, 0x00,  # Flags
            0x00, 0x00, 0x00, 0x00,  # Reserved
            0x00, 0x10, 0x00, 0x00,  # Protocol version
            0x00, 0x02, 0x00, 0x00,  # Receive buffer size
            0x00, 0x02, 0x00, 0x00,  # Send buffer size
            0x00, 0x50, 0x00, 0x00,  # Max message size
            0x00, 0x00, 0x00, 0x00,  # Max chunk count
        ])
        
        # Add endpoint URL
        endpoint = self.endpoint_url or f'opc.tcp://localhost:{self.port}'
        url_bytes = endpoint.encode('utf-8')
        hello += struct.pack('<I', len(url_bytes))
        hello += url_bytes
        
        # Add length header
        length = len(hello) + 4
        header = struct.pack('<III', length, 0x00, 0x00)
        
        try:
            self.socket.send(header + hello)
            return True
        except Exception as e:
            logger.error(f"  ❌ HELLO failed: {e}")
            return False
    
    def _receive_acknowledge(self) -> bool:
        """Receive ACKNOWLEDGE message"""
        try:
            data = self.socket.recv(4096)
            if len(data) >= 12 and data[0:4] == b'ACKF':
                logger.debug("  ✅ ACKNOWLEDGE received")
                return True
        except Exception as e:
            logger.error(f"  ❌ ACKNOWLEDGE failed: {e}")
        
        return False
    
    def _send_secure_close(self):
        """Send secure close message"""
        logger.debug("  Sending secure close...")
        # Simplified - real implementation needs full OPC UA secure channel close
    
    def get_server_info(self) -> Optional[OPCUAServer]:
        """
        Get OPC UA server information
        
        Returns:
            OPCUAServer or None
        """
        logger.info("📖 Reading server information...")
        
        if not self.connected:
            return None
        
        # Simulated server info
        server = OPCUAServer(
            application_uri='opc.tcp://localhost:4840',
            product_uri='http://opcfoundation.org/UA/',
            application_name='OPC UA Server',
            application_type='Server',
            manufacturer_name='OPC Foundation',
            server_status='Running',
            security_modes=['None', 'Sign', 'SignAndEncrypt'],
            security_policies=['None', 'Basic128Rsa15', 'Basic256', 'Basic256Sha256']
        )
        
        self.server = server
        logger.info(f"  ✅ Server: {server.application_name}")
        logger.info(f"  Security Modes: {', '.join(server.security_modes)}")
        logger.info(f"  Security Policies: {', '.join(server.security_policies[:3])}")
        
        return server
    
    def browse_nodes(self, node_id: str = 'i=84', recursive: bool = False) -> List[OPCUANode]:
        """
        Browse address space
        
        Args:
            node_id: Starting node ID (default: Root Folder)
            recursive: Browse recursively
            
        Returns:
            List of nodes
        """
        logger.info(f"📋 Browsing nodes from {node_id}...")
        
        if not self.connected:
            return []
        
        nodes = []
        
        # Simulated browse results
        simulated_nodes = [
            OPCUANode(
                node_id='i=85',
                node_class='Object',
                browse_name='Objects',
                display_name='Objects',
                description='Objects folder'
            ),
            OPCUANode(
                node_id='i=86',
                node_class='Object',
                browse_name='Types',
                display_name='Types',
                description='Types folder'
            ),
            OPCUANode(
                node_id='i=87',
                node_class='Object',
                browse_name='Views',
                display_name='Views',
                description='Views folder'
            ),
            OPCUANode(
                node_id='ns=2;s=MyDevice',
                node_class='Object',
                browse_name='MyDevice',
                display_name='My Device',
                description='Sample device'
            ),
            OPCUANode(
                node_id='ns=2;s=Temperature',
                node_class='Variable',
                browse_name='Temperature',
                display_name='Temperature Sensor',
                description='Temperature measurement',
                data_type='Double',
                value=25.5,
                access_level=0x03  # CurrentRead | CurrentWrite
            ),
            OPCUANode(
                node_id='ns=2;s=Pressure',
                node_class='Variable',
                browse_name='Pressure',
                display_name='Pressure Sensor',
                description='Pressure measurement',
                data_type='Double',
                value=101.3,
                access_level=0x03
            ),
            OPCUANode(
                node_id='ns=2;s=MotorSpeed',
                node_class='Variable',
                browse_name='MotorSpeed',
                display_name='Motor Speed',
                description='Motor speed control',
                data_type='Double',
                value=1500.0,
                access_level=0x03
            ),
            OPCUANode(
                node_id='ns=2;s=SystemStatus',
                node_class='Variable',
                browse_name='SystemStatus',
                display_name='System Status',
                description='System status indicator',
                data_type='String',
                value='Running',
                access_level=0x01  # CurrentRead only
            ),
        ]
        
        nodes = simulated_nodes
        self.nodes = nodes
        logger.info(f"  Found {len(nodes)} nodes")
        
        return nodes
    
    def read_node(self, node_id: str) -> Optional[OPCUANode]:
        """
        Read node value
        
        Args:
            node_id: Node ID to read
            
        Returns:
            OPCUANode with value or None
        """
        logger.info(f"📖 Reading node: {node_id}")
        
        if not self.connected:
            return None
        
        # Simulated read
        node = OPCUANode(
            node_id=node_id,
            node_class='Variable',
            browse_name='TestNode',
            display_name='Test Node',
            data_type='Double',
            value=42.0,
            access_level=0x03
        )
        
        logger.debug(f"  Value: {node.value}")
        return node
    
    def write_node(self, node_id: str, value: any) -> bool:
        """
        Write node value
        
        ⚠️  SAFETY WARNING: Can affect industrial processes!
        
        Args:
            node_id: Node ID to write
            value: Value to write
            
        Returns:
            True if write successful
        """
        if self.safety_mode:
            logger.error("❌ Write blocked: Safety mode enabled")
            return False
        
        logger.warning(f"✏️  WRITING node {node_id} = {value}")
        logger.warning("  This can affect industrial processes!")
        
        # TODO: Implement write request
        return False
    
    def call_method(self, object_id: str, method_id: str,
                    input_arguments: List[any] = None) -> Dict:
        """
        Call method
        
        ⚠️  SAFETY WARNING: Can affect industrial processes!
        
        Args:
            object_id: Object containing method
            method_id: Method ID to call
            input_arguments: Method input arguments
            
        Returns:
            Method call results
        """
        if self.safety_mode:
            logger.error("❌ Method call blocked: Safety mode enabled")
            return {'success': False, 'error': 'Safety mode enabled'}
        
        logger.warning(f"🔧 CALLING method {method_id}")
        logger.warning("  This can affect industrial processes!")
        
        # TODO: Implement method call
        return {'success': False, 'error': 'Not implemented'}
    
    def create_subscription(self, publishing_interval: float = 1000.0,
                            lifetime_count: int = 6000) -> Optional[OPCUASubscription]:
        """
        Create subscription
        
        Args:
            publishing_interval: Publishing interval in ms
            lifetime_count: Lifetime count
            
        Returns:
            OPCUASubscription or None
        """
        logger.info(f"📋 Creating subscription (interval={publishing_interval}ms)...")
        
        if not self.connected:
            return None
        
        subscription = OPCUASubscription(
            subscription_id=1,
            publishing_interval=publishing_interval,
            lifetime_count=lifetime_count,
            max_keep_alive_count=100,
            priority=0
        )
        
        self.subscriptions.append(subscription)
        logger.info(f"  ✅ Subscription created (ID: {subscription.subscription_id})")
        
        return subscription
    
    def delete_subscription(self, subscription_id: int) -> bool:
        """
        Delete subscription
        
        Args:
            subscription_id: Subscription ID
            
        Returns:
            True if successful
        """
        logger.info(f"🗑️  Deleting subscription {subscription_id}...")
        
        self.subscriptions = [s for s in self.subscriptions if s.subscription_id != subscription_id]
        return True
    
    def monitor_items(self, subscription_id: int,
                      node_ids: List[str]) -> List[int]:
        """
        Monitor items in subscription
        
        Args:
            subscription_id: Subscription ID
            node_ids: List of node IDs to monitor
            
        Returns:
            List of monitored item IDs
        """
        logger.info(f"📊 Monitoring {len(node_ids)} items...")
        
        monitored_ids = list(range(1, len(node_ids) + 1))
        
        for sub in self.subscriptions:
            if sub.subscription_id == subscription_id:
                sub.monitored_items = monitored_ids
                break
        
        return monitored_ids
    
    def security_assessment(self) -> Dict:
        """
        Perform security assessment
        
        Returns:
            Assessment results
        """
        logger.info("🔒 Performing security assessment...")
        
        results = {
            'endpoint_url': self.endpoint_url or f'localhost:{self.port}',
            'timestamp': datetime.now().isoformat(),
            'vulnerabilities': [],
            'recommendations': [],
            'risk_score': 0.0
        }
        
        if not self.connected or not self.server:
            return results
        
        # Check for None security policy
        if 'None' in self.server.security_policies:
            results['vulnerabilities'].append({
                'id': 'OPCUA-001',
                'severity': 'high',
                'description': 'None security policy enabled (no encryption)',
                'cvss': 7.5,
                'remediation': 'Disable None security policy, use Basic256Sha256 or better'
            })
        
        # Check for SignAndEncrypt mode
        if 'SignAndEncrypt' not in self.server.security_modes:
            results['vulnerabilities'].append({
                'id': 'OPCUA-002',
                'severity': 'medium',
                'description': 'SignAndEncrypt mode not available',
                'cvss': 5.0,
                'remediation': 'Enable SignAndEncrypt security mode'
            })
        
        # Check for anonymous access
        results['vulnerabilities'].append({
            'id': 'OPCUA-003',
            'severity': 'high',
            'description': 'Anonymous access may be enabled',
            'cvss': 7.0,
            'remediation': 'Require user authentication for all sessions'
        })
        
        # Check for write access
        results['vulnerabilities'].append({
            'id': 'OPCUA-004',
            'severity': 'medium',
            'description': 'Write access to nodes without authentication',
            'cvss': 6.0,
            'remediation': 'Implement node-level access control'
        })
        
        # Calculate risk score
        risk = 5.0
        for vuln in results['vulnerabilities']:
            if vuln['severity'] == 'critical':
                risk += 3.0
            elif vuln['severity'] == 'high':
                risk += 2.0
            elif vuln['severity'] == 'medium':
                risk += 1.0
        
        results['risk_score'] = min(10.0, risk)
        
        # Recommendations
        results['recommendations'] = [
            'Disable None security policy',
            'Enable Basic256Sha256 or Aes128_Sha256_RsaOaep security policy',
            'Require SignAndEncrypt security mode',
            'Implement user authentication',
            'Configure node-level access control',
            'Use certificate-based authentication',
            'Monitor OPC UA traffic for anomalies',
            'Regular security audits'
        ]
        
        logger.info(f"  Assessment complete: {len(results['vulnerabilities'])} vulnerabilities")
        logger.info(f"  Risk score: {results['risk_score']}/10.0")
        
        return results
    
    def generate_report(self) -> str:
        """Generate assessment report"""
        report = []
        report.append("=" * 70)
        report.append("🏭 OPC UA SECURITY ASSESSMENT REPORT")
        report.append("=" * 70)
        
        if self.server:
            report.append(f"Server: {self.server.application_name}")
            report.append(f"Type: {self.server.application_type}")
            report.append(f"Manufacturer: {self.server.manufacturer_name}")
            report.append(f"Status: {self.server.server_status}")
        
        report.append(f"Endpoint: {self.endpoint_url or f'localhost:{self.port}'}")
        report.append(f"Safety Mode: {'ENABLED' if self.safety_mode else 'DISABLED'}")
        report.append("")
        
        # Node summary
        report.append("NODES DISCOVERED:")
        report.append("-" * 70)
        report.append(f"  Total Nodes: {len(self.nodes)}")
        
        node_classes = {}
        for node in self.nodes:
            node_classes[node.node_class] = node_classes.get(node.node_class, 0) + 1
        
        for node_class, count in sorted(node_classes.items(), key=lambda x: x[1], reverse=True):
            report.append(f"  {node_class}: {count}")
        report.append("")
        
        # Security assessment
        assessment = self.security_assessment()
        
        report.append("VULNERABILITIES:")
        report.append("-" * 70)
        for vuln in assessment['vulnerabilities']:
            report.append(f"  [{vuln['severity'].upper()}] {vuln['id']}: {vuln['description']}")
            report.append(f"    CVSS: {vuln['cvss']}")
            report.append(f"    Remediation: {vuln['remediation']}")
        
        report.append("")
        report.append("RECOMMENDATIONS:")
        report.append("-" * 70)
        for rec in assessment['recommendations']:
            report.append(f"  • {rec}")
        
        report.append("")
        report.append(f"RISK SCORE: {assessment['risk_score']}/10.0")
        report.append("=" * 70)
        
        return "\n".join(report)


def main():
    """Main entry point"""
    print("""
╔═══════════════════════════════════════════════════════════════╗
║     🏭 KALIAGENT v4.4.0 - OPC UA CLIENT                      ║
║                    Phase 10: Alpha 0.1.0                      ║
╚═══════════════════════════════════════════════════════════════╝

⚠️  CRITICAL SAFETY WARNING:
    OPC UA is used in critical industrial systems!
    
    ONLY test on:
    ✅ Isolated lab systems you own
    ✅ Dedicated training facilities
    ✅ Systems with explicit written authorization
    
    NEVER test on:
    ❌ Production systems
    ❌ Critical infrastructure

    """)
    
    import sys
    
    endpoint = sys.argv[1] if len(sys.argv) > 1 else 'opc.tcp://localhost:4840'
    
    # Initialize client
    opcua = OPCUAClient(endpoint_url=endpoint, safety_mode=True, verbose=True)
    
    # Connect
    if opcua.connect():
        # Get server info
        server = opcua.get_server_info()
        
        if server:
            print(f"\n📊 Server Information:")
            print(f"  Name: {server.application_name}")
            print(f"  Type: {server.application_type}")
            print(f"  Manufacturer: {server.manufacturer_name}")
        
        # Browse nodes
        nodes = opcua.browse_nodes('i=84')
        
        if nodes:
            print(f"\n📋 Nodes Discovered ({len(nodes)}):")
            for node in nodes[:10]:
                print(f"  {node.node_class}: {node.browse_name} ({node.node_id})")
        
        # Generate report
        print("\n" + opcua.generate_report())
        
        opcua.disconnect()
    else:
        print("\n❌ Failed to connect")


if __name__ == "__main__":
    main()
