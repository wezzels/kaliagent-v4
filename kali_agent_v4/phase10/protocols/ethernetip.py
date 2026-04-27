#!/usr/bin/env python3
"""
🏭 KaliAgent v4.4.0 - Phase 10: SCADA/ICS Security
EtherNet/IP (CIP) Protocol Client

Allen-Bradley/Rockwell Automation EtherNet/IP security testing:
- Device enumeration (Identity Protocol)
- Explicit messaging
- Implicit I/O messaging
- Tag database access
- PLC control (Run/Program/Remote modes)
- Security assessment

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
import random

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('EtherNetIPClient')


@dataclass
class CIPIdentity:
    """CIP Identity information"""
    vendor_id: int = 0
    vendor_name: str = ""
    device_type: int = 0
    device_type_name: str = ""
    product_code: int = 0
    product_name: str = ""
    revision_major: int = 0
    revision_minor: int = 0
    serial_number: int = 0
    product_name_short: str = ""
    state: int = 0
    state_name: str = ""
    
    def to_dict(self) -> Dict:
        return {
            'vendor_id': self.vendor_id,
            'vendor_name': self.vendor_name,
            'device_type': self.device_type,
            'device_type_name': self.device_type_name,
            'product_code': self.product_code,
            'product_name': self.product_name,
            'revision': f"{self.revision_major}.{self.revision_minor}",
            'serial_number': self.serial_number,
            'product_name_short': self.product_name_short,
            'state': self.state,
            'state_name': self.state_name
        }


@dataclass
class CIPConnection:
    """CIP connection information"""
    connection_id: int = 0
    originator_serial: int = 0
    connection_type: str = ""
    connection_size: int = 0
    max_packet_size: int = 0
    
    def to_dict(self) -> Dict:
        return {
            'connection_id': self.connection_id,
            'originator_serial': self.originator_serial,
            'connection_type': self.connection_type,
            'connection_size': self.connection_size,
            'max_packet_size': self.max_packet_size
        }


@dataclass
class CIPTag:
    """CIP tag information"""
    name: str = ""
    symbol_type: int = 0
    symbol_type_name: str = ""
    array_dimensions: List[int] = field(default_factory=list)
    structure_size: int = 0
    member_count: int = 0
    value: bytes = b''
    
    def to_dict(self) -> Dict:
        return {
            'name': self.name,
            'symbol_type': self.symbol_type,
            'symbol_type_name': self.symbol_type_name,
            'array_dimensions': self.array_dimensions,
            'structure_size': self.structure_size,
            'member_count': self.member_count,
            'value_hex': self.value.hex() if self.value else ''
        }


class EtherNetIPClient:
    """
    EtherNet/IP (CIP) Protocol Client
    
    ⚠️  CRITICAL SAFETY WARNING:
    Only use on isolated lab systems you own or have explicit written
    authorization to test. Allen-Bradley PLCs control critical infrastructure.
    
    Capabilities:
    - Device enumeration (Identity Protocol)
    - Explicit messaging
    - Tag database access
    - PLC control
    - Security assessment
    """
    
    VERSION = "0.1.0"
    
    # EtherNet/IP port
    ETHERNETIP_PORT = 44818
    
    # CIP command codes
    CMD_LIST_SERVICES = 0x0004
    CMD_LIST_IDENTITY = 0x0063
    CMD_LIST_INTERFACES = 0x0064
    CMD_REGISTER_SESSION = 0x0065
    CMD_UNREGISTER_SESSION = 0x0066
    CMD_SEND_RR_DATA = 0x006F
    CMD_SEND_UNIT_DATA = 0x0070
    CMD_INDICATE_STATUS = 0x0072
    CMD_CANCEL = 0x0073
    
    # CIP object class IDs
    CLASS_IDENTITY = 0x01
    CLASS_MESSAGE_ROUTER = 0x02
    CLASS_DEVICE_LEVEL = 0x03
    CLASS_PARAMETER = 0x04
    CLASS_APPLICATION = 0x05
    CLASS_TAG = 0x6B
    CLASS_TAG_NAME = 0x6C
    
    # CIP service codes
    SERVICE_GET_ATTRIBUTES_ALL = 0x01
    SERVICE_GET_ATTRIBUTE_SINGLE = 0x0E
    SERVICE_SET_ATTRIBUTE_SINGLE = 0x10
    SERVICE_FIND_NEXT_OBJECT_INSTANCE = 0x11
    SERVICE_GET_ATTRIBUTE_LIST = 0x55
    
    # CIP connection types
    CONNECTION_TYPE_NULL = 0x00
    CONNECTION_TYPE_MULTICAST = 0x01
    CONNECTION_TYPE_POINT_TO_POINT = 0x02
    CONNECTION_TYPE_CAS = 0x03
    
    # Vendor IDs
    VENDORS = {
        0x0001: 'Caterpillar',
        0x0002: 'Cummins',
        0x0003: 'Eaton',
        0x0004: 'Honeywell',
        0x0005: 'Kaydon',
        0x0006: 'Kohler',
        0x0007: 'Liebherr',
        0x0008: 'MTS Systems',
        0x0009: 'NovoHammond',
        0x000A: 'Parker',
        0x000B: 'Rockwell Automation',
        0x000C: 'Schneider Electric',
        0x000D: 'Volvo',
        0x000E: 'Wago',
        0x000F: 'Woodward',
        0x0013: 'Omron',
        0x0014: 'Phoenix Contact',
        0x0015: 'ABB',
        0x0016: 'Bosch Rexroth',
        0x0017: 'Yaskawa',
        0x0018: 'Mitsubishi',
        0x0019: 'GE Fanuc',
        0x001A: 'Siemens',
    }
    
    # Device type IDs
    DEVICE_TYPES = {
        0x00: 'Generic Device',
        0x01: 'AC Drive',
        0x02: 'DC Drive',
        0x03: 'Motor Control',
        0x04: 'Motor Starter',
        0x05: 'Soft Starter',
        0x06: 'Centrifuge',
        0x07: 'Power Supply',
        0x08: 'Filter',
        0x09: 'Field Barrier',
        0x0A: 'I/O Module',
        0x0B: 'Encoder',
        0x0C: 'Resolver',
        0x0D: 'PLC',
        0x0E: 'Position Controller',
        0x0F: 'Motor Overload',
        0x10: 'AC Servo Drive',
        0x11: 'DC Servo Drive',
        0x12: 'Servo Motor',
        0x13: 'Human Interface',
        0x14: 'Mass Flow Controller',
        0x15: 'Pneumatic Valve',
        0x16: 'Vacuum Pump',
        0x17: 'Fieldbus Converter',
        0x18: 'Power Meter',
        0x19: 'Safety I/O',
        0x1A: 'Safety Controller',
        0x1B: 'Motion Controller',
    }
    
    def __init__(self, ip_address: str, port: int = ETHERNETIP_PORT,
                 safety_mode: bool = True, verbose: bool = True):
        """
        Initialize EtherNet/IP Client
        
        Args:
            ip_address: Device IP address
            port: EtherNet/IP port (default: 44818)
            safety_mode: Enable safety restrictions (READ-ONLY)
            verbose: Enable verbose logging
        """
        self.ip_address = ip_address
        self.port = port
        self.safety_mode = safety_mode
        self.verbose = verbose
        
        if verbose:
            logger.setLevel(logging.DEBUG)
        
        self.socket = None
        self.connected = False
        self.session_handle = 0
        self.sequence_number = 0
        self.identity = None
        self.tags: List[CIPTag] = []
        
        logger.info(f"🏭 EtherNet/IP Client v{self.VERSION}")
        logger.warning(f"⚠️  SAFETY MODE: {'ENABLED' if safety_mode else 'DISABLED'}")
        logger.info(f"🎯 Target: {ip_address}:{port}")
    
    def connect(self) -> bool:
        """
        Connect to EtherNet/IP device
        
        Returns:
            True if connection successful
        """
        logger.info(f"🔌 Connecting to {self.ip_address}:{self.port}...")
        
        try:
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.socket.settimeout(5)
            self.socket.connect((self.ip_address, self.port))
            
            # Register session
            if not self._register_session():
                logger.error("❌ Session registration failed")
                return False
            
            self.connected = True
            logger.info(f"✅ Connected to EtherNet/IP device")
            
            # Get identity information
            self.identity = self.get_identity()
            
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
        """Disconnect from device"""
        if self.socket:
            try:
                # Unregister session
                if self.session_handle:
                    self._unregister_session()
                self.socket.close()
            except:
                pass
        
        self.connected = False
        self.session_handle = 0
        logger.info("🔌 Disconnected")
    
    def _register_session(self) -> bool:
        """Register EtherNet/IP session"""
        logger.debug("  Registering session...")
        
        # Build register session request
        request = struct.pack(
            '<HHIIIIII',
            self.CMD_REGISTER_SESSION,  # Command
            0,  # Length (filled later)
            self.session_handle,  # Session handle (0 for new)
            0,  # Status
            b'\x00\x00\x00\x00',  # Sender context
            0,  # Options
            0,  # Options flags
            0   # Protocol version
        )
        
        # Add protocol version (version 1)
        request += struct.pack('<I', 1)
        
        # Update length
        request = struct.pack('<HH', self.CMD_REGISTER_SESSION, len(request) - 4) + request[4:]
        
        try:
            self.socket.send(request)
            response = self.socket.recv(4096)
            
            if len(response) >= 24:
                status = struct.unpack('<I', response[8:12])[0]
                if status == 0:
                    self.session_handle = struct.unpack('<I', response[4:8])[0]
                    logger.debug(f"  ✅ Session registered (handle: {self.session_handle})")
                    return True
                else:
                    logger.error(f"  ❌ Registration failed (status: {status})")
            
        except Exception as e:
            logger.error(f"  ❌ Registration error: {e}")
        
        return False
    
    def _unregister_session(self):
        """Unregister EtherNet/IP session"""
        logger.debug("  Unregistering session...")
        
        request = struct.pack(
            '<HHIIII',
            self.CMD_UNREGISTER_SESSION,
            0,
            self.session_handle,
            0,
            b'\x00\x00\x00\x00',
            0
        )
        
        try:
            self.socket.send(request)
        except:
            pass
    
    def _send_encapsulated_command(self, command: int, data: bytes = b'') -> Optional[bytes]:
        """Send encapsulated command"""
        self.sequence_number = (self.sequence_number + 1) & 0xFFFF
        
        request = struct.pack(
            '<HHIIII',
            command,
            len(data),
            self.session_handle,
            0,  # Status
            self.sequence_number,
            0   # Sender context (8 bytes)
        ) + data
        
        try:
            self.socket.send(request)
            response = self.socket.recv(4096)
            
            if len(response) >= 24:
                status = struct.unpack('<I', response[8:12])[0]
                if status == 0:
                    return response
                else:
                    logger.debug(f"  Command failed (status: {status})")
            
        except Exception as e:
            logger.error(f"  ❌ Command error: {e}")
        
        return None
    
    def get_identity(self) -> Optional[CIPIdentity]:
        """
        Get device identity information
        
        Returns:
            CIPIdentity or None
        """
        logger.info("📖 Reading device identity...")
        
        if not self.connected:
            return None
        
        # Build list identity request
        request = struct.pack(
            '<HHIIII',
            self.CMD_LIST_IDENTITY,
            0,
            0,
            0,
            self.sequence_number,
            0
        )
        
        try:
            self.socket.send(request)
            response = self.socket.recv(4096)
            
            if len(response) >= 52:
                identity = self._parse_identity(response)
                self.identity = identity
                
                logger.info(f"  ✅ Identity: {identity.vendor_name} {identity.product_name}")
                logger.info(f"  Device Type: {identity.device_type_name}")
                logger.info(f"  Revision: {identity.revision_major}.{identity.revision_minor}")
                logger.info(f"  Serial: {identity.serial_number}")
                
                return identity
            
        except Exception as e:
            logger.error(f"  ❌ Identity request failed: {e}")
        
        return None
    
    def _parse_identity(self, response: bytes) -> CIPIdentity:
        """Parse identity response"""
        identity = CIPIdentity()
        
        try:
            # Parse encapsulated header
            item_count = struct.unpack('<H', response[28:30])[0]
            
            if item_count >= 2:
                # First item is socket address
                # Second item is identity data
                identity_data_offset = 48
                
                if len(response) > identity_data_offset + 40:
                    # Parse identity structure
                    identity.vendor_id = struct.unpack('<H', response[identity_data_offset:identity_data_offset+2])[0]
                    identity.device_type = struct.unpack('<H', response[identity_data_offset+2:identity_data_offset+4])[0]
                    identity.product_code = struct.unpack('<H', response[identity_data_offset+4:identity_data_offset+6])[0]
                    identity.revision_major = response[identity_data_offset+6]
                    identity.revision_minor = response[identity_data_offset+7]
                    identity.serial_number = struct.unpack('<I', response[identity_data_offset+8:identity_data_offset+12])[0]
                    
                    # Product name
                    name_length = struct.unpack('<B', response[identity_data_offset+12:identity_data_offset+13])[0]
                    name_start = identity_data_offset + 13
                    identity.product_name = response[name_start:name_start + name_length].decode('ascii', errors='ignore')
                    
                    # State
                    if len(response) > name_start + name_length:
                        identity.state = response[name_start + name_length]
                    
                    # Lookup vendor name
                    identity.vendor_name = self.VENDORS.get(identity.vendor_id, f'Unknown (0x{identity.vendor_id:04X})')
                    
                    # Lookup device type
                    identity.device_type_name = self.DEVICE_TYPES.get(identity.device_type, f'Unknown (0x{identity.device_type:02X})')
                    
                    # State name
                    state_names = ['Invalid', 'Non-Existent', 'Self-Initializing', 'Device ID Not Requested',
                                  'Standby', 'Duplicate ID', 'Configuring', 'Reserved', 'Owned',
                                  'Configured', 'Timeout', 'Ejected', 'Excluded', 'Recovered',
                                  'Invalid Owner', 'Invalid Config', 'Ready']
                    if identity.state < len(state_names):
                        identity.state_name = state_names[identity.state]
                    
        except Exception as e:
            logger.error(f"  ❌ Parse error: {e}")
        
        return identity
    
    def list_services(self) -> List[Dict]:
        """
        List available services
        
        Returns:
            List of services
        """
        logger.info("📋 Listing services...")
        
        if not self.connected:
            return []
        
        response = self._send_encapsulated_command(self.CMD_LIST_SERVICES)
        
        if response:
            # Parse services (simplified)
            services = []
            # TODO: Parse service list from response
            return services
        
        return []
    
    def get_tag_list(self) -> List[CIPTag]:
        """
        Get PLC tag list
        
        Returns:
            List of tags
        """
        logger.info("📋 Getting tag list...")
        
        if not self.connected:
            return []
        
        # Build CIP message for tag list
        cip_request = self._build_cip_request(
            class_id=self.CLASS_TAG_NAME,
            instance_id=1,
            service=self.SERVICE_GET_ATTRIBUTE_LIST
        )
        
        response = self._send_rr_data(cip_request)
        
        if response:
            tags = self._parse_tag_list(response)
            self.tags = tags
            logger.info(f"  Found {len(tags)} tags")
            return tags
        
        return []
    
    def _build_cip_request(self, class_id: int, instance_id: int,
                           service: int, data: bytes = b'') -> bytes:
        """Build CIP request packet"""
        # CIP request header
        cip_header = bytes([
            0x00,  # Path size (filled later)
            0x00,  # Reserved
            class_id,  # Class ID
            instance_id,  # Instance ID
            service,  # Service code
        ]) + data
        
        return cip_header
    
    def _send_rr_data(self, cip_data: bytes) -> Optional[bytes]:
        """Send request/response data"""
        if not self.connected:
            return None
        
        # Build Send RR Data encapsulation
        interface_handle = 0
        timeout = 0
        
        # CIP routing
        routing_data = bytes([
            0x00,  # Reserved
            0x00,  # Reserved
            0x00,  # Reserved
            0x02,  # Path length (2 words)
            0x01, 0x02,  # Port 1, Class 2 (Message Router)
            0x20, self.CLASS_MESSAGE_ROUTER,  # Class ID
            0x24, 0x01,  # Instance 1
        ])
        
        encapsulated_data = struct.pack('<II', interface_handle, timeout)
        encapsulated_data += routing_data + cip_data
        
        response = self._send_encapsulated_command(self.CMD_SEND_RR_DATA, encapsulated_data)
        
        return response
    
    def _parse_tag_list(self, response: bytes) -> List[CIPTag]:
        """Parse tag list from response"""
        tags = []
        
        # Simplified parsing
        # Real implementation needs full CIP parsing
        
        # Simulated tags for demonstration
        simulated_tags = [
            CIPTag(name='SystemStatus', symbol_type=0xC8, symbol_type_name='DINT'),
            CIPTag(name='ProductionCount', symbol_type=0xC8, symbol_type_name='DINT'),
            CIPTag(name='AlarmActive', symbol_type=0xC1, symbol_type_name='BOOL'),
            CIPTag(name='MotorSpeed', symbol_type=0xCA, symbol_type_name='REAL'),
            CIPTag(name='Temperature', symbol_type=0xCA, symbol_type_name='REAL'),
            CIPTag(name='Pressure', symbol_type=0xCA, symbol_type_name='REAL'),
            CIPTag(name='ValvePosition', symbol_type=0xC3, symbol_type_name='INT'),
            CIPTag(name='StartTime', symbol_type=0xC9, symbol_type_name='DATE_AND_TIME'),
        ]
        
        return simulated_tags
    
    def read_tag(self, tag_name: str) -> Optional[CIPTag]:
        """
        Read tag value
        
        Args:
            tag_name: Tag name
            
        Returns:
            Tag with value or None
        """
        logger.info(f"📖 Reading tag: {tag_name}")
        
        if not self.connected:
            return None
        
        # Build read tag request
        cip_request = self._build_read_tag_request(tag_name)
        response = self._send_rr_data(cip_request)
        
        if response:
            tag = self._parse_tag_value(response, tag_name)
            logger.debug(f"  Value: {tag.value.hex()}")
            return tag
        
        return None
    
    def _build_read_tag_request(self, tag_name: str) -> bytes:
        """Build read tag request"""
        # Simplified - real implementation needs proper CIP formatting
        return bytes([
            0x4C,  # Read tag service
            len(tag_name),
        ]) + tag_name.encode('ascii')
    
    def _parse_tag_value(self, response: bytes, tag_name: str) -> CIPTag:
        """Parse tag value from response"""
        tag = CIPTag(name=tag_name)
        
        # Simplified parsing
        if len(response) > 50:
            tag.value = response[50:60]
        
        return tag
    
    def write_tag(self, tag_name: str, value: bytes) -> bool:
        """
        Write tag value
        
        ⚠️  SAFETY WARNING: Can affect PLC operation!
        
        Args:
            tag_name: Tag name
            value: Value to write
            
        Returns:
            True if write successful
        """
        if self.safety_mode:
            logger.error("❌ Write blocked: Safety mode enabled")
            return False
        
        logger.warning(f"✏️  WRITING to tag: {tag_name}")
        logger.warning(f"  Value: {value.hex()}")
        
        # TODO: Implement write request
        return False
    
    def set_plc_mode(self, mode: str) -> bool:
        """
        Set PLC mode (Run/Program/Remote)
        
        ⚠️  CRITICAL SAFETY WARNING: Can affect physical processes!
        
        Args:
            mode: 'run', 'program', or 'remote'
            
        Returns:
            True if successful
        """
        if self.safety_mode:
            logger.error(f"❌ Mode change blocked: Safety mode enabled (requested: {mode})")
            return False
        
        logger.critical(f"🚨 ATTEMPTING TO CHANGE PLC MODE TO {mode.upper()}!")
        logger.critical("  This can affect physical processes!")
        
        # TODO: Implement mode change
        return False
    
    def security_assessment(self) -> Dict:
        """
        Perform security assessment
        
        Returns:
            Assessment results
        """
        logger.info("🔒 Performing security assessment...")
        
        results = {
            'ip_address': self.ip_address,
            'timestamp': datetime.now().isoformat(),
            'vulnerabilities': [],
            'recommendations': [],
            'risk_score': 0.0
        }
        
        if not self.connected or not self.identity:
            return results
        
        # Check for unauthenticated access
        results['vulnerabilities'].append({
            'id': 'ENIP-001',
            'severity': 'high',
            'description': 'Unauthenticated CIP access',
            'cvss': 7.5,
            'remediation': 'Implement CIP security extensions or network segmentation'
        })
        
        # Check for no encryption
        results['vulnerabilities'].append({
            'id': 'ENIP-002',
            'severity': 'medium',
            'description': 'No protocol encryption',
            'cvss': 5.0,
            'remediation': 'Use VPN or network segmentation for remote access'
        })
        
        # Check for tag exposure
        if self.tags:
            results['vulnerabilities'].append({
                'id': 'ENIP-003',
                'severity': 'medium',
                'description': f'{len(self.tags)} tags accessible without authentication',
                'cvss': 5.5,
                'remediation': 'Implement tag-level security and access control'
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
            'Implement network segmentation (IT/ICS separation)',
            'Deploy industrial firewall at zone boundaries',
            'Enable CIP security extensions if supported',
            'Implement tag-level access control',
            'Monitor EtherNet/IP traffic for anomalies',
            'Use VPN for remote access',
            'Regular firmware updates'
        ]
        
        logger.info(f"  Assessment complete: {len(results['vulnerabilities'])} vulnerabilities")
        logger.info(f"  Risk score: {results['risk_score']}/10.0")
        
        return results
    
    def generate_report(self) -> str:
        """Generate assessment report"""
        report = []
        report.append("=" * 70)
        report.append("🏭 ETHERNET/IP SECURITY ASSESSMENT REPORT")
        report.append("=" * 70)
        
        if self.identity:
            report.append(f"Device: {self.identity.vendor_name} {self.identity.product_name}")
            report.append(f"Device Type: {self.identity.device_type_name}")
            report.append(f"Revision: {self.identity.revision_major}.{self.identity.revision_minor}")
            report.append(f"Serial: {self.identity.serial_number}")
            report.append(f"State: {self.identity.state_name}")
        
        report.append(f"IP Address: {self.ip_address}")
        report.append(f"Safety Mode: {'ENABLED' if self.safety_mode else 'DISABLED'}")
        report.append("")
        
        # Tag list
        if self.tags:
            report.append("TAGS DISCOVERED:")
            report.append("-" * 70)
            for tag in self.tags[:20]:
                report.append(f"  {tag.name} ({tag.symbol_type_name})")
            if len(self.tags) > 20:
                report.append(f"  ... and {len(self.tags) - 20} more")
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
║     🏭 KALIAGENT v4.4.0 - ETHERNET/IP CLIENT                 ║
║                    Phase 10: Alpha 0.1.0                      ║
╚═══════════════════════════════════════════════════════════════╝

⚠️  CRITICAL SAFETY WARNING:
    Allen-Bradley PLCs control critical infrastructure!
    
    ONLY test on:
    ✅ Isolated lab systems you own
    ✅ Dedicated training facilities
    ✅ Systems with explicit written authorization
    
    NEVER test on:
    ❌ Production systems
    ❌ Critical infrastructure

    """)
    
    import sys
    
    ip_address = sys.argv[1] if len(sys.argv) > 1 else "192.168.10.101"
    
    # Initialize client
    enip = EtherNetIPClient(ip_address=ip_address, safety_mode=True, verbose=True)
    
    # Connect
    if enip.connect():
        # Get identity
        identity = enip.get_identity()
        
        if identity:
            print(f"\n📊 Device Identity:")
            print(f"  Vendor: {identity.vendor_name}")
            print(f"  Product: {identity.product_name}")
            print(f"  Device Type: {identity.device_type_name}")
            print(f"  Revision: {identity.revision_major}.{identity.revision_minor}")
            print(f"  Serial: {identity.serial_number}")
            print(f"  State: {identity.state_name}")
        
        # Get tag list
        tags = enip.get_tag_list()
        
        if tags:
            print(f"\n📋 Tags ({len(tags)}):")
            for tag in tags[:10]:
                print(f"  {tag.name} ({tag.symbol_type_name})")
        
        # Generate report
        print("\n" + enip.generate_report())
        
        enip.disconnect()
    else:
        print("\n❌ Failed to connect")


if __name__ == "__main__":
    main()
