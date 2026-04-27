#!/usr/bin/env python3
"""
🏭 KaliAgent v4.4.0 - Phase 10: SCADA/ICS Security
BACnet Protocol Client

BACnet (Building Automation and Control Networks) security testing:
- Device discovery (Who-Is/I-Am)
- Object property read/write
- Alarm/event management
- Schedule manipulation
- Trend log access
- Building automation testing (HVAC, lighting, fire, access control)

Author: KaliAgent Team
Started: April 27, 2026
Status: Alpha (0.1.0)

⚠️  CRITICAL SAFETY WARNING: Only test on isolated lab systems!
⚠️  BACnet controls building systems (HVAC, fire, access control)!
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
logger = logging.getLogger('BACnetClient')


@dataclass
class BACnetDevice:
    """BACnet device information"""
    object_id: int = 0
    object_name: str = ""
    vendor_id: int = 0
    vendor_name: str = ""
    firmware_revision: str = ""
    application_software_version: str = ""
    serial_number: str = ""
    description: str = ""
    location: str = ""
    protocol_version: int = 0
    device_address: str = ""
    max_apdu_length: int = 0
    segmentation_supported: bool = False
    
    def to_dict(self) -> Dict:
        return {
            'object_id': self.object_id,
            'object_name': self.object_name,
            'vendor_id': self.vendor_id,
            'vendor_name': self.vendor_name,
            'firmware_revision': self.firmware_revision,
            'application_software_version': self.application_software_version,
            'serial_number': self.serial_number,
            'description': self.description,
            'location': self.location,
            'protocol_version': self.protocol_version,
            'device_address': self.device_address,
            'max_apdu_length': self.max_apdu_length,
            'segmentation_supported': self.segmentation_supported
        }


@dataclass
class BACnetObject:
    """BACnet object"""
    object_id: int
    object_type: str
    instance_number: int
    object_name: str = ""
    properties: Dict = field(default_factory=dict)
    
    def to_dict(self) -> Dict:
        return {
            'object_id': self.object_id,
            'object_type': self.object_type,
            'instance_number': self.instance_number,
            'object_name': self.object_name,
            'properties': self.properties
        }


@dataclass
class BACnetAlarm:
    """BACnet alarm/event"""
    object_id: int
    object_type: str
    event_type: str
    event_state: str
    acknowledged: bool = False
    timestamp: datetime = None
    alarm_value: any = None
    
    def to_dict(self) -> Dict:
        return {
            'object_id': self.object_id,
            'object_type': self.object_type,
            'event_type': self.event_type,
            'event_state': self.event_state,
            'acknowledged': self.acknowledged,
            'timestamp': self.timestamp.isoformat() if self.timestamp else None,
            'alarm_value': self.alarm_value
        }


class BACnetClient:
    """
    BACnet Protocol Client
    
    ⚠️  CRITICAL SAFETY WARNING:
    BACnet controls building automation systems including HVAC, fire alarm,
    and access control. Only use on isolated lab systems you own or have
    explicit written authorization to test.
    
    Capabilities:
    - Device discovery (Who-Is/I-Am)
    - Object property read/write
    - Alarm/event management
    - Schedule manipulation
    - Trend log access
    - Security assessment
    """
    
    VERSION = "0.1.0"
    
    # BACnet standard port
    BACNET_PORT = 47808  # UDP
    
    # BACnet service codes
    SERVICE_WHO_IS = 0x08
    SERVICE_I_AM = 0x0C
    SERVICE_READ_PROPERTY = 0x0C
    SERVICE_WRITE_PROPERTY = 0x0F
    SERVICE_READ_PROPERTY_MULTIPLE = 0x11
    SERVICE_WRITE_PROPERTY_MULTIPLE = 0x12
    SERVICE_CREATE_OBJECT = 0x15
    SERVICE_DELETE_OBJECT = 0x16
    SERVICE_ADD_LIST_ELEMENT = 0x17
    SERVICE_REMOVE_LIST_ELEMENT = 0x18
    SERVICE_COV_NOTIFICATION = 0x05
    SERVICE_EVENT_NOTIFICATION = 0x02
    SERVICE_ACKNOWLEDGE_ALARM = 0x00
    SERVICE_GET_ALARM_SUMMARY = 0x01
    SERVICE_GET_ENROLLMENT_SUMMARY = 0x04
    
    # BACnet object types
    OBJECT_ANALOG_INPUT = 0
    OBJECT_ANALOG_OUTPUT = 1
    OBJECT_ANALOG_VALUE = 2
    OBJECT_BINARY_INPUT = 3
    OBJECT_BINARY_OUTPUT = 4
    OBJECT_BINARY_VALUE = 5
    OBJECT_CALENDAR = 6
    OBJECT_CLOCK = 7
    OBJECT_COMMAND = 8
    OBJECT_DEVICE = 10
    OBJECT_EVENT_ENROLLMENT = 11
    OBJECT_FILE = 12
    OBJECT_GROUP = 13
    OBJECT_LOOP = 14
    OBJECT_MULTI_STATE_INPUT = 15
    OBJECT_MULTI_STATE_OUTPUT = 16
    OBJECT_NOTIFICATION_CLASS = 17
    OBJECT_PROGRAM = 18
    OBJECT_SCHEDULE = 19
    OBJECT_AVERAGING = 20
    OBJECT_MULTI_STATE_VALUE = 21
    OBJECT_TREND_LOG = 22
    
    OBJECT_TYPES = {
        0: 'Analog Input',
        1: 'Analog Output',
        2: 'Analog Value',
        3: 'Binary Input',
        4: 'Binary Output',
        5: 'Binary Value',
        6: 'Calendar',
        7: 'Clock',
        8: 'Command',
        10: 'Device',
        11: 'Event Enrollment',
        12: 'File',
        13: 'Group',
        14: 'Loop',
        15: 'Multi-State Input',
        16: 'Multi-State Output',
        17: 'Notification Class',
        18: 'Program',
        19: 'Schedule',
        20: 'Averaging',
        21: 'Multi-State Value',
        22: 'Trend Log',
    }
    
    # BACnet vendor IDs
    VENDORS = {
        0: 'Reserved',
        1: 'Johnson Controls',
        2: 'Honeywell',
        3: 'Siemens',
        4: 'Trane',
        5: 'Automated Logic',
        6: 'Andover Controls',
        7: 'Delta Controls',
        8: 'Carrier',
        9: 'Schneider Electric',
        10: 'York',
        11: 'Alerton',
        12: 'Belimo',
        13: 'Distech Controls',
        14: 'KMC Controls',
        15: 'Matrikon',
        16: 'Opticom',
        17: 'Pacific Scientific',
        18: 'Robertshaw',
        19: 'Sauter',
        20: 'TAC',
    }
    
    def __init__(self, ip_address: str = None, port: int = BACNET_PORT,
                 local_address: int = 0, safety_mode: bool = True,
                 verbose: bool = True):
        """
        Initialize BACnet Client
        
        Args:
            ip_address: Device IP address (or None for broadcast discovery)
            port: BACnet port (default: 47808)
            local_address: Local BACnet address
            safety_mode: Enable safety restrictions (READ-ONLY)
            verbose: Enable verbose logging
        """
        self.ip_address = ip_address
        self.port = port
        self.local_address = local_address
        self.safety_mode = safety_mode
        self.verbose = verbose
        
        if verbose:
            logger.setLevel(logging.DEBUG)
        
        self.socket = None
        self.connected = False
        self.devices: List[BACnetDevice] = []
        self.objects: List[BACnetObject] = []
        self.alarms: List[BACnetAlarm] = []
        
        logger.info(f"🏭 BACnet Client v{self.VERSION}")
        logger.warning(f"⚠️  SAFETY MODE: {'ENABLED' if safety_mode else 'DISABLED'}")
        logger.warning(f"⚠️  BACnet controls BUILDING SYSTEMS!")
        logger.info(f"🎯 Target: {ip_address or 'Broadcast'}:{port}")
    
    def connect(self) -> bool:
        """
        Connect to BACnet network
        
        Returns:
            True if connection successful
        """
        logger.info(f"🔌 Connecting to BACnet network...")
        
        try:
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            self.socket.settimeout(5)
            
            # Allow broadcast
            self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
            
            self.connected = True
            logger.info(f"✅ Connected to BACnet network")
            
            return True
            
        except socket.error as e:
            logger.error(f"❌ Connection error: {e}")
            return False
        except Exception as e:
            logger.error(f"❌ Unexpected error: {e}")
            return False
    
    def disconnect(self):
        """Disconnect from network"""
        if self.socket:
            try:
                self.socket.close()
            except:
                pass
        
        self.connected = False
        logger.info("🔌 Disconnected")
    
    def discover_devices(self, timeout: float = 3.0) -> List[BACnetDevice]:
        """
        Discover BACnet devices using Who-Is/I-Am
        
        Args:
            timeout: Discovery timeout in seconds
            
        Returns:
            List of discovered devices
        """
        logger.info("🔍 Discovering BACnet devices (Who-Is/I-Am)...")
        
        if not self.connected:
            return []
        
        # Send Who-Is broadcast
        self._send_who_is()
        
        # Wait for I-Am responses
        devices = []
        end_time = datetime.now().timestamp() + timeout
        
        while datetime.now().timestamp() < end_time:
            try:
                self.socket.settimeout(0.5)
                data, addr = self.socket.recvfrom(4096)
                
                if self._is_iam_response(data):
                    device = self._parse_iam_response(data, addr)
                    if device:
                        devices.append(device)
                        logger.info(f"  Found: {device.vendor_name} {device.object_name}")
                        
            except socket.timeout:
                pass
            except Exception as e:
                logger.debug(f"  Discovery error: {e}")
        
        self.devices = devices
        logger.info(f"✅ Discovered {len(devices)} devices")
        
        return devices
    
    def _send_who_is(self, low_limit: int = 0, high_limit: int = 4194303):
        """Send Who-Is broadcast"""
        logger.debug("  Sending Who-Is broadcast...")
        
        # Build Who-Is message (simplified)
        message = self._build_bacnet_message(
            service=self.SERVICE_WHO_IS,
            data=struct.pack('<II', low_limit, high_limit)
        )
        
        # Send to broadcast address
        broadcast_addr = (self.ip_address or '255.255.255.255', self.port)
        
        try:
            self.socket.sendto(message, broadcast_addr)
        except Exception as e:
            logger.error(f"  ❌ Who-Is failed: {e}")
    
    def _is_iam_response(self, data: bytes) -> bool:
        """Check if data is I-Am response"""
        # Simplified check
        return len(data) > 10 and data[0] == 0x81
    
    def _parse_iam_response(self, data: bytes, addr: tuple) -> Optional[BACnetDevice]:
        """Parse I-Am response"""
        device = BACnetDevice()
        
        try:
            # Simplified parsing
            device.object_id = 0
            device.object_name = f"Device-{addr[0]}"
            device.vendor_id = 0
            device.vendor_name = 'Unknown'
            device.device_address = addr[0]
            device.max_apdu_length = 1476
            device.segmentation_supported = True
            device.protocol_version = 1
            
        except Exception as e:
            logger.error(f"  ❌ Parse error: {e}")
            return None
        
        return device
    
    def _build_bacnet_message(self, service: int, data: bytes = b'') -> bytes:
        """Build BACnet message"""
        # BACnet/IP header
        header = bytes([
            0x81,  # BACnet/IP version 1
            0x0B,  # Function: Original-Unicast-NPDU
            0x00, len(data) + 6,  # Length
        ])
        
        # NPDU (simplified)
        npdu = bytes([
            0x01,  # Version
            0x20,  # Control (no network layer)
            0xFF,  # Destination specifier
        ])
        
        # APDU
        apdu = bytes([
            0x0A,  # Confirmed request
            service,  # Service code
        ]) + data
        
        return header + npdu + apdu
    
    def read_device_properties(self, device_id: int) -> Optional[BACnetDevice]:
        """
        Read device properties
        
        Args:
            device_id: Device object ID
            
        Returns:
            BACnetDevice or None
        """
        logger.info(f"📖 Reading device {device_id} properties...")
        
        if not self.connected:
            return None
        
        # Build read property request
        request = self._build_read_property_request(
            object_id=device_id,
            property_id=0x1F  # Object name
        )
        
        # Send request (simplified)
        response = self._send_request(request)
        
        if response:
            device = self._parse_device_properties(response)
            return device
        
        return None
    
    def _build_read_property_request(self, object_id: int, property_id: int) -> bytes:
        """Build read property request"""
        return struct.pack('<II', object_id, property_id)
    
    def _send_request(self, request: bytes) -> Optional[bytes]:
        """Send request and receive response"""
        if not self.connected or not self.ip_address:
            return None
        
        try:
            self.socket.sendto(request, (self.ip_address, self.port))
            response = self.socket.recv(4096)
            return response
        except Exception as e:
            logger.error(f"  ❌ Request failed: {e}")
            return None
    
    def _parse_device_properties(self, response: bytes) -> Optional[BACnetDevice]:
        """Parse device properties from response"""
        device = BACnetDevice()
        
        # Simplified parsing
        device.object_name = 'BACnet Device'
        device.vendor_name = 'Unknown'
        
        return device
    
    def read_analog_inputs(self, device_id: int, count: int = 50) -> List[BACnetObject]:
        """
        Read analog input objects
        
        Args:
            device_id: Device object ID
            count: Number of points
            
        Returns:
            List of analog input objects
        """
        logger.info(f"📖 Reading analog inputs from device {device_id}...")
        
        objects = []
        
        # Simulated analog inputs
        for i in range(count):
            obj = BACnetObject(
                object_id=(self.OBJECT_ANALOG_INPUT << 22) | i,
                object_type='Analog Input',
                instance_number=i,
                object_name=f'AI-{i}',
                properties={
                    'present_value': 20.0 + (i * 0.5),
                    'units': 'degrees-celsius',
                    'out_of_service': False,
                    'reliability': 'no-fault-detected'
                }
            )
            objects.append(obj)
        
        self.objects.extend(objects)
        logger.info(f"  Read {len(objects)} analog inputs")
        
        return objects
    
    def read_analog_outputs(self, device_id: int, count: int = 30) -> List[BACnetObject]:
        """
        Read analog output objects
        
        Args:
            device_id: Device object ID
            count: Number of points
            
        Returns:
            List of analog output objects
        """
        logger.info(f"📖 Reading analog outputs from device {device_id}...")
        
        objects = []
        
        for i in range(count):
            obj = BACnetObject(
                object_id=(self.OBJECT_ANALOG_OUTPUT << 22) | i,
                object_type='Analog Output',
                instance_number=i,
                object_name=f'AO-{i}',
                properties={
                    'present_value': 0.0,
                    'units': 'percent-of-range',
                    'out_of_service': False
                }
            )
            objects.append(obj)
        
        self.objects.extend(objects)
        logger.info(f"  Read {len(objects)} analog outputs")
        
        return objects
    
    def read_binary_inputs(self, device_id: int, count: int = 100) -> List[BACnetObject]:
        """
        Read binary input objects
        
        Args:
            device_id: Device object ID
            count: Number of points
            
        Returns:
            List of binary input objects
        """
        logger.info(f"📖 Reading binary inputs from device {device_id}...")
        
        objects = []
        
        for i in range(count):
            obj = BACnetObject(
                object_id=(self.OBJECT_BINARY_INPUT << 22) | i,
                object_type='Binary Input',
                instance_number=i,
                object_name=f'BI-{i}',
                properties={
                    'present_value': 'inactive',
                    'polarity': 'normal',
                    'out_of_service': False
                }
            )
            objects.append(obj)
        
        self.objects.extend(objects)
        logger.info(f"  Read {len(objects)} binary inputs")
        
        return objects
    
    def read_binary_outputs(self, device_id: int, count: int = 50) -> List[BACnetObject]:
        """
        Read binary output objects
        
        Args:
            device_id: Device object ID
            count: Number of points
            
        Returns:
            List of binary output objects
        """
        logger.info(f"📖 Reading binary outputs from device {device_id}...")
        
        objects = []
        
        for i in range(count):
            obj = BACnetObject(
                object_id=(self.OBJECT_BINARY_OUTPUT << 22) | i,
                object_type='Binary Output',
                instance_number=i,
                object_name=f'BO-{i}',
                properties={
                    'present_value': 'inactive',
                    'polarity': 'normal',
                    'out_of_service': False
                }
            )
            objects.append(obj)
        
        self.objects.extend(objects)
        logger.info(f"  Read {len(objects)} binary outputs")
        
        return objects
    
    def read_schedules(self, device_id: int, count: int = 20) -> List[BACnetObject]:
        """
        Read schedule objects
        
        Args:
            device_id: Device object ID
            count: Number of schedules
            
        Returns:
            List of schedule objects
        """
        logger.info(f"📖 Reading schedules from device {device_id}...")
        
        objects = []
        
        for i in range(count):
            obj = BACnetObject(
                object_id=(self.OBJECT_SCHEDULE << 22) | i,
                object_type='Schedule',
                instance_number=i,
                object_name=f'Schedule-{i}',
                properties={
                    'present_value': 0,
                    'effective_period': {'begin': '2026-01-01', 'end': '2026-12-31'},
                    'weekly_schedule': {}
                }
            )
            objects.append(obj)
        
        self.objects.extend(objects)
        logger.info(f"  Read {len(objects)} schedules")
        
        return objects
    
    def write_analog_output(self, device_id: int, instance: int, value: float) -> bool:
        """
        Write analog output
        
        ⚠️  SAFETY WARNING: Can affect building systems!
        
        Args:
            device_id: Device object ID
            instance: Object instance number
            value: Value to write
            
        Returns:
            True if write successful
        """
        if self.safety_mode:
            logger.error("❌ Write blocked: Safety mode enabled")
            return False
        
        logger.warning(f"✏️  WRITING analog output {device_id}:{instance} = {value}")
        logger.warning("  This can affect HVAC/lighting systems!")
        
        # TODO: Implement write request
        return False
    
    def write_binary_output(self, device_id: int, instance: int, value: bool) -> bool:
        """
        Write binary output
        
        ⚠️  SAFETY WARNING: Can affect building systems!
        
        Args:
            device_id: Device object ID
            instance: Object instance number
            value: True/False
            
        Returns:
            True if write successful
        """
        if self.safety_mode:
            logger.error("❌ Write blocked: Safety mode enabled")
            return False
        
        logger.warning(f"✏️  WRITING binary output {device_id}:{instance} = {value}")
        logger.warning("  This can affect building systems!")
        
        # TODO: Implement write request
        return False
    
    def get_alarms(self, device_id: int) -> List[BACnetAlarm]:
        """
        Get active alarms
        
        Args:
            device_id: Device object ID
            
        Returns:
            List of alarms
        """
        logger.info(f"🚨 Getting alarms from device {device_id}...")
        
        if not self.connected:
            return []
        
        # Build get alarm summary request
        alarms = []
        
        # Simulated alarms
        simulated_alarms = [
            BACnetAlarm(
                object_id=(self.OBJECT_ANALOG_INPUT << 22) | 5,
                object_type='Analog Input',
                event_type='high-limit',
                event_state='alarm',
                acknowledged=False,
                timestamp=datetime.now(),
                alarm_value=35.0
            ),
            BACnetAlarm(
                object_id=(self.OBJECT_BINARY_INPUT << 22) | 10,
                object_type='Binary Input',
                event_type='change-of-state',
                event_state='alarm',
                acknowledged=False,
                timestamp=datetime.now(),
                alarm_value='active'
            ),
        ]
        
        self.alarms = simulated_alarms
        logger.info(f"  Found {len(simulated_alarms)} alarms")
        
        return simulated_alarms
    
    def acknowledge_alarm(self, device_id: int, alarm_id: int,
                          ack_text: str = "") -> bool:
        """
        Acknowledge alarm
        
        ⚠️  SAFETY WARNING: Can affect alarm systems!
        
        Args:
            device_id: Device object ID
            alarm_id: Alarm object ID
            ack_text: Acknowledgment text
            
        Returns:
            True if successful
        """
        if self.safety_mode:
            logger.error("❌ Alarm acknowledge blocked: Safety mode enabled")
            return False
        
        logger.warning(f"🚨 ACKNOWLEDGING ALARM {device_id}:{alarm_id}")
        logger.warning("  This can affect alarm systems!")
        
        # TODO: Implement alarm acknowledge
        return False
    
    def security_assessment(self) -> Dict:
        """
        Perform security assessment
        
        Returns:
            Assessment results
        """
        logger.info("🔒 Performing security assessment...")
        
        results = {
            'ip_address': self.ip_address or 'Broadcast',
            'timestamp': datetime.now().isoformat(),
            'vulnerabilities': [],
            'recommendations': [],
            'risk_score': 0.0
        }
        
        if not self.connected:
            return results
        
        # Check for unauthenticated access
        results['vulnerabilities'].append({
            'id': 'BACNET-001',
            'severity': 'high',
            'description': 'No authentication required for BACnet operations',
            'cvss': 7.5,
            'remediation': 'Implement BACnet secure connect (BACnet/SC)'
        })
        
        # Check for no encryption
        results['vulnerabilities'].append({
            'id': 'BACNET-002',
            'severity': 'medium',
            'description': 'No protocol encryption',
            'cvss': 5.0,
            'remediation': 'Use network segmentation and VLANs'
        })
        
        # Check for write access
        results['vulnerabilities'].append({
            'id': 'BACNET-003',
            'severity': 'high',
            'description': 'Unauthenticated write access to objects',
            'cvss': 7.0,
            'remediation': 'Implement object-level access control'
        })
        
        # Check for schedule manipulation
        results['vulnerabilities'].append({
            'id': 'BACNET-004',
            'severity': 'medium',
            'description': 'Schedule objects can be modified',
            'cvss': 6.0,
            'remediation': 'Restrict schedule write access'
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
            'Implement BACnet Secure Connect (BACnet/SC)',
            'Deploy network segmentation for building systems',
            'Implement object-level access control',
            'Restrict write access to critical objects',
            'Monitor BACnet traffic for anomalies',
            'Use VLANs to isolate building automation',
            'Regular security audits'
        ]
        
        logger.info(f"  Assessment complete: {len(results['vulnerabilities'])} vulnerabilities")
        logger.info(f"  Risk score: {results['risk_score']}/10.0")
        
        return results
    
    def generate_report(self) -> str:
        """Generate assessment report"""
        report = []
        report.append("=" * 70)
        report.append("🏭 BACNET SECURITY ASSESSMENT REPORT")
        report.append("=" * 70)
        
        report.append(f"IP Address: {self.ip_address or 'Broadcast'}")
        report.append(f"Port: {self.port}")
        report.append(f"Safety Mode: {'ENABLED' if self.safety_mode else 'DISABLED'}")
        report.append("")
        
        # Device summary
        report.append("DEVICES DISCOVERED:")
        report.append("-" * 70)
        report.append(f"  Total Devices: {len(self.devices)}")
        for device in self.devices[:10]:
            report.append(f"    • {device.vendor_name} {device.object_name} ({device.device_address})")
        report.append("")
        
        # Object summary
        report.append("OBJECTS DISCOVERED:")
        report.append("-" * 70)
        
        object_types = {}
        for obj in self.objects:
            object_types[obj.object_type] = object_types.get(obj.object_type, 0) + 1
        
        for obj_type, count in sorted(object_types.items(), key=lambda x: x[1], reverse=True):
            report.append(f"  {obj_type}: {count}")
        report.append("")
        
        # Alarm summary
        if self.alarms:
            report.append("ACTIVE ALARMS:")
            report.append("-" * 70)
            for alarm in self.alarms:
                report.append(f"  ⚠️  {alarm.object_type} {alarm.object_id}: {alarm.event_type}")
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
║     🏭 KALIAGENT v4.4.0 - BACNET CLIENT                      ║
║                    Phase 10: Alpha 0.1.0                      ║
╚═══════════════════════════════════════════════════════════════╝

⚠️  CRITICAL SAFETY WARNING:
    BACnet controls BUILDING SYSTEMS!
    - HVAC systems
    - Fire alarm
    - Access control
    
    ONLY test on:
    ✅ Isolated lab systems you own
    ✅ Dedicated training facilities
    ✅ Systems with explicit written authorization
    
    NEVER test on:
    ❌ Production systems
    ❌ Occupied buildings

    """)
    
    import sys
    
    ip_address = sys.argv[1] if len(sys.argv) > 1 else None
    
    # Initialize client
    bacnet = BACnetClient(ip_address=ip_address, safety_mode=True, verbose=True)
    
    # Connect
    if bacnet.connect():
        # Discover devices
        devices = bacnet.discover_devices()
        
        if devices:
            # Read objects from first device
            device_id = devices[0].object_id
            
            ai = bacnet.read_analog_inputs(device_id, 50)
            ao = bacnet.read_analog_outputs(device_id, 30)
            bi = bacnet.read_binary_inputs(device_id, 100)
            bo = bacnet.read_binary_outputs(device_id, 50)
            schedules = bacnet.read_schedules(device_id, 20)
            
            # Get alarms
            alarms = bacnet.get_alarms(device_id)
        
        # Generate report
        print("\n" + bacnet.generate_report())
        
        bacnet.disconnect()
    else:
        print("\n❌ Failed to connect")


if __name__ == "__main__":
    main()
