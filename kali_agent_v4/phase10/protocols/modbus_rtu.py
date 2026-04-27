#!/usr/bin/env python3
"""
🏭 KaliAgent v4.4.0 - Phase 10: SCADA/ICS Security
Modbus RTU Protocol Client

Modbus RTU (Serial) security testing:
- Serial communication (RS-485/RS-232)
- Function code testing
- Coil/register read/write
- Gateway bridging (RTU/TCP)
- Serial device enumeration

Author: KaliAgent Team
Started: April 27, 2026
Status: Alpha (0.1.0)

⚠️  CRITICAL SAFETY WARNING: Only test on isolated lab systems!
⚠️  Modbus RTU controls industrial processes!
"""

import logging
import serial
import serial.tools.list_ports
import struct
from typing import List, Dict, Optional, Tuple
from datetime import datetime
from dataclasses import dataclass, field

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('ModbusRTUClient')


@dataclass
class ModbusRTUDevice:
    """Modbus RTU device information"""
    unit_id: int = 0
    device_type: str = ""
    manufacturer: str = ""
    firmware_version: str = ""
    serial_number: str = ""
    coils_count: int = 0
    discrete_inputs_count: int = 0
    holding_registers_count: int = 0
    input_registers_count: int = 0
    
    def to_dict(self) -> Dict:
        return {
            'unit_id': self.unit_id,
            'device_type': self.device_type,
            'manufacturer': self.manufacturer,
            'firmware_version': self.firmware_version,
            'serial_number': self.serial_number,
            'coils_count': self.coils_count,
            'discrete_inputs_count': self.discrete_inputs_count,
            'holding_registers_count': self.holding_registers_count,
            'input_registers_count': self.input_registers_count
        }


class ModbusRTUClient:
    """
    Modbus RTU Protocol Client
    
    ⚠️  CRITICAL SAFETY WARNING:
    Modbus RTU controls industrial processes. Only use on isolated lab
    systems you own or have explicit written authorization to test.
    
    Capabilities:
    - Serial communication (RS-485/RS-232)
    - Function code testing
    - Coil/register read/write
    - Gateway bridging
    - Device enumeration
    """
    
    VERSION = "0.1.0"
    
    # Modbus function codes
    FC_READ_COILS = 0x01
    FC_READ_DISCRETE_INPUTS = 0x02
    FC_READ_HOLDING_REGISTERS = 0x03
    FC_READ_INPUT_REGISTERS = 0x04
    FC_WRITE_SINGLE_COIL = 0x05
    FC_WRITE_SINGLE_REGISTER = 0x06
    FC_READ_EXCEPTION_STATUS = 0x07
    FC_WRITE_MULTIPLE_COILS = 0x0F
    FC_WRITE_MULTIPLE_REGISTERS = 0x10
    FC_REPORT_SERVER_ID = 0x11
    FC_READ_FIFO_QUEUE = 0x14
    FC_READ_WRITE_REGISTERS = 0x17
    FC_READ_FILE_RECORD = 0x14
    FC_WRITE_FILE_RECORD = 0x15
    FC_MASK_WRITE_REGISTER = 0x16
    FC_READ_DEVICE_IDENTIFICATION = 0x2B
    
    # Exception codes
    EXCEPTION_ILLEGAL_FUNCTION = 0x01
    EXCEPTION_ILLEGAL_DATA_ADDRESS = 0x02
    EXCEPTION_ILLEGAL_DATA_VALUE = 0x03
    EXCEPTION_SLAVE_DEVICE_FAILURE = 0x04
    EXCEPTION_ACKNOWLEDGE = 0x05
    EXCEPTION_SLAVE_DEVICE_BUSY = 0x06
    EXCEPTION_NEGATIVE_ACKNOWLEDGE = 0x07
    EXCEPTION_MEMORY_PARITY_ERROR = 0x08
    EXCEPTION_GATEWAY_PATH_UNAVAILABLE = 0x0A
    EXCEPTION_GATEWAY_TARGET_FAILED = 0x0B
    
    EXCEPTION_MESSAGES = {
        0x01: 'Illegal Function',
        0x02: 'Illegal Data Address',
        0x03: 'Illegal Data Value',
        0x04: 'Slave Device Failure',
        0x05: 'Acknowledge',
        0x06: 'Slave Device Busy',
        0x07: 'Negative Acknowledge',
        0x08: 'Memory Parity Error',
        0x0A: 'Gateway Path Unavailable',
        0x0B: 'Gateway Target Device Failed to Respond'
    }
    
    def __init__(self, port: str = None, baudrate: int = 9600,
                 timeout: float = 1.0, safety_mode: bool = True,
                 verbose: bool = True):
        """
        Initialize Modbus RTU Client
        
        Args:
            port: Serial port (e.g., /dev/ttyUSB0, COM1)
            baudrate: Baud rate (default: 9600)
            timeout: Read timeout in seconds
            safety_mode: Enable safety restrictions (READ-ONLY)
            verbose: Enable verbose logging
        """
        self.port = port
        self.baudrate = baudrate
        self.timeout = timeout
        self.safety_mode = safety_mode
        self.verbose = verbose
        
        if verbose:
            logger.setLevel(logging.DEBUG)
        
        self.serial_conn = None
        self.connected = False
        self.devices: List[ModbusRTUDevice] = []
        
        logger.info(f"🏭 Modbus RTU Client v{self.VERSION}")
        logger.warning(f"⚠️  SAFETY MODE: {'ENABLED' if safety_mode else 'DISABLED'}")
        logger.info(f"🎯 Port: {port or 'None'} @ {baudrate} baud")
    
    def list_ports(self) -> List[Dict]:
        """
        List available serial ports
        
        Returns:
            List of available ports
        """
        logger.info("🔍 Scanning for serial ports...")
        
        ports = []
        
        try:
            port_list = serial.tools.list_ports.comports()
            
            for port in port_list:
                ports.append({
                    'device': port.device,
                    'description': port.description,
                    'hwid': port.hwid,
                    'is_usb': 'USB' in port.description or 'FTDI' in port.hwid
                })
                logger.debug(f"  Found: {port.device} - {port.description}")
            
            logger.info(f"✅ Found {len(ports)} serial ports")
            
        except Exception as e:
            logger.error(f"❌ Port scan failed: {e}")
        
        return ports
    
    def connect(self, port: str = None, baudrate: int = None) -> bool:
        """
        Connect to Modbus RTU device
        
        Args:
            port: Serial port (overrides constructor)
            baudrate: Baud rate (overrides constructor)
            
        Returns:
            True if connection successful
        """
        port = port or self.port
        baudrate = baudrate or self.baudrate
        
        logger.info(f"🔌 Connecting to {port} @ {baudrate} baud...")
        
        if not port:
            logger.error("❌ No port specified")
            return False
        
        try:
            self.serial_conn = serial.Serial(
                port=port,
                baudrate=baudrate,
                bytesize=serial.EIGHTBITS,
                parity=serial.PARITY_NONE,
                stopbits=serial.STOPBITS_ONE,
                timeout=self.timeout
            )
            
            self.connected = True
            logger.info(f"✅ Connected to {port}")
            
            return True
            
        except serial.SerialException as e:
            logger.error(f"❌ Connection failed: {e}")
            return False
        except Exception as e:
            logger.error(f"❌ Unexpected error: {e}")
            return False
    
    def disconnect(self):
        """Disconnect from device"""
        if self.serial_conn and self.serial_conn.is_open:
            self.serial_conn.close()
        
        self.connected = False
        logger.info("🔌 Disconnected")
    
    def _calculate_crc16(self, data: bytes) -> int:
        """Calculate Modbus CRC16"""
        crc = 0xFFFF
        
        for byte in data:
            crc ^= byte
            for _ in range(8):
                if crc & 0x0001:
                    crc >>= 1
                    crc ^= 0xA001
                else:
                    crc >>= 1
        
        return crc
    
    def _build_frame(self, unit_id: int, function_code: int, data: bytes = b'') -> bytes:
        """Build Modbus RTU frame"""
        frame = bytes([unit_id, function_code]) + data
        crc = self._calculate_crc16(frame)
        frame += struct.pack('<H', crc)
        
        return frame
    
    def _send_request(self, unit_id: int, function_code: int,
                      data: bytes = b'') -> Optional[bytes]:
        """Send Modbus RTU request"""
        if not self.connected or not self.serial_conn:
            return None
        
        frame = self._build_frame(unit_id, function_code, data)
        
        try:
            self.serial_conn.write(frame)
            response = self.serial_conn.read(256)
            
            if len(response) >= 5:  # Minimum valid response
                # Verify CRC
                received_crc = struct.unpack('<H', response[-2:])[0]
                calculated_crc = self._calculate_crc16(response[:-2])
                
                if received_crc == calculated_crc:
                    return response[:-2]
                else:
                    logger.debug(f"  CRC mismatch")
            
        except Exception as e:
            logger.error(f"  ❌ Request failed: {e}")
        
        return None
    
    def _parse_exception(self, response: bytes) -> Dict:
        """Parse exception response"""
        if len(response) >= 2:
            function_code = response[0]
            exception_code = response[1]
            
            return {
                'function_code': function_code,
                'exception_code': exception_code,
                'message': self.EXCEPTION_MESSAGES.get(exception_code, 'Unknown Exception')
            }
        
        return {'error': 'Invalid exception response'}
    
    def scan_unit_ids(self, start: int = 1, end: int = 247) -> List[int]:
        """
        Scan for active Modbus unit IDs
        
        Args:
            start: Starting unit ID
            end: Ending unit ID
            
        Returns:
            List of active unit IDs
        """
        logger.info(f"🔍 Scanning unit IDs {start}-{end}...")
        
        active_ids = []
        
        for unit_id in range(start, end + 1):
            # Try to read holding register 0
            response = self._send_request(
                unit_id,
                self.FC_READ_HOLDING_REGISTERS,
                struct.pack('!HH', 0, 1)
            )
            
            if response:
                # Check if it's a valid response (not exception)
                if response[0] == unit_id and response[1] == self.FC_READ_HOLDING_REGISTERS:
                    active_ids.append(unit_id)
                    logger.debug(f"  ✅ Unit ID {unit_id} responded")
                elif response[1] == (self.FC_READ_HOLDING_REGISTERS | 0x80):
                    # Exception response still means device exists
                    exception = self._parse_exception(response)
                    if exception['exception_code'] != self.EXCEPTION_ILLEGAL_FUNCTION:
                        active_ids.append(unit_id)
                        logger.debug(f"  ✅ Unit ID {unit_id} responded (with exception)")
        
        logger.info(f"✅ Found {len(active_ids)} active unit IDs")
        return active_ids
    
    def read_coils(self, unit_id: int, start: int = 0, count: int = 100) -> List[bool]:
        """
        Read coils
        
        Args:
            unit_id: Unit ID
            start: Start address
            count: Number of coils
            
        Returns:
            List of coil values
        """
        logger.info(f"📖 Reading coils from unit {unit_id} ({start}-{start+count-1})...")
        
        response = self._send_request(
            unit_id,
            self.FC_READ_COILS,
            struct.pack('!HH', start, count)
        )
        
        if response and len(response) >= 3:
            byte_count = response[2]
            coil_data = response[3:3 + byte_count]
            
            coils = []
            for byte in coil_data:
                for i in range(8):
                    coils.append((byte >> i) & 1 == 1)
            
            return coils[:count]
        
        return []
    
    def read_discrete_inputs(self, unit_id: int, start: int = 0,
                             count: int = 100) -> List[bool]:
        """
        Read discrete inputs
        
        Args:
            unit_id: Unit ID
            start: Start address
            count: Number of inputs
            
        Returns:
            List of input values
        """
        logger.info(f"📖 Reading discrete inputs from unit {unit_id}...")
        
        response = self._send_request(
            unit_id,
            self.FC_READ_DISCRETE_INPUTS,
            struct.pack('!HH', start, count)
        )
        
        if response and len(response) >= 3:
            byte_count = response[2]
            input_data = response[3:3 + byte_count]
            
            inputs = []
            for byte in input_data:
                for i in range(8):
                    inputs.append((byte >> i) & 1 == 1)
            
            return inputs[:count]
        
        return []
    
    def read_holding_registers(self, unit_id: int, start: int = 0,
                               count: int = 100) -> List[int]:
        """
        Read holding registers
        
        Args:
            unit_id: Unit ID
            start: Start address
            count: Number of registers
            
        Returns:
            List of register values
        """
        logger.info(f"📖 Reading holding registers from unit {unit_id}...")
        
        response = self._send_request(
            unit_id,
            self.FC_READ_HOLDING_REGISTERS,
            struct.pack('!HH', start, count)
        )
        
        if response and len(response) >= 3:
            byte_count = response[2]
            register_data = response[3:3 + byte_count]
            
            registers = []
            for i in range(0, len(register_data), 2):
                if i + 1 < len(register_data):
                    value = struct.unpack('!H', register_data[i:i+2])[0]
                    registers.append(value)
            
            return registers
        
        return []
    
    def read_input_registers(self, unit_id: int, start: int = 0,
                             count: int = 100) -> List[int]:
        """
        Read input registers
        
        Args:
            unit_id: Unit ID
            start: Start address
            count: Number of registers
            
        Returns:
            List of register values
        """
        logger.info(f"📖 Reading input registers from unit {unit_id}...")
        
        response = self._send_request(
            unit_id,
            self.FC_READ_INPUT_REGISTERS,
            struct.pack('!HH', start, count)
        )
        
        if response and len(response) >= 3:
            byte_count = response[2]
            register_data = response[3:3 + byte_count]
            
            registers = []
            for i in range(0, len(register_data), 2):
                if i + 1 < len(register_data):
                    value = struct.unpack('!H', register_data[i:i+2])[0]
                    registers.append(value)
            
            return registers
        
        return []
    
    def write_coil(self, unit_id: int, address: int, value: bool) -> bool:
        """
        Write single coil
        
        ⚠️  SAFETY WARNING: Can affect physical processes!
        
        Args:
            unit_id: Unit ID
            address: Coil address
            value: True/False
            
        Returns:
            True if write successful
        """
        if self.safety_mode:
            logger.error("❌ Write blocked: Safety mode enabled")
            return False
        
        logger.warning(f"✏️  WRITING coil {unit_id}:{address} = {value}")
        
        # Value for write: 0xFF00 = ON, 0x0000 = OFF
        value_bytes = struct.pack('!H', 0xFF00 if value else 0x0000)
        
        response = self._send_request(
            unit_id,
            self.FC_WRITE_SINGLE_COIL,
            struct.pack('!H', address) + value_bytes
        )
        
        if response and len(response) >= 4:
            logger.warning("⚠️  COIL WRITE SUCCESSFUL!")
            return True
        
        return False
    
    def write_register(self, unit_id: int, address: int, value: int) -> bool:
        """
        Write single register
        
        ⚠️  SAFETY WARNING: Can affect physical processes!
        
        Args:
            unit_id: Unit ID
            address: Register address
            value: Register value (0-65535)
            
        Returns:
            True if write successful
        """
        if self.safety_mode:
            logger.error("❌ Write blocked: Safety mode enabled")
            return False
        
        logger.warning(f"✏️  WRITING register {unit_id}:{address} = {value}")
        
        response = self._send_request(
            unit_id,
            self.FC_WRITE_SINGLE_REGISTER,
            struct.pack('!HH', address, value)
        )
        
        if response and len(response) >= 4:
            logger.warning("⚠️  REGISTER WRITE SUCCESSFUL!")
            return True
        
        return False
    
    def get_device_identification(self, unit_id: int) -> Optional[ModbusRTUDevice]:
        """
        Get device identification (function code 0x2B)
        
        Args:
            unit_id: Unit ID
            
        Returns:
            ModbusRTUDevice or None
        """
        logger.info(f"📖 Getting device identification for unit {unit_id}...")
        
        # Function code 0x2B, sub-function 0x0E (read device identification)
        response = self._send_request(
            unit_id,
            0x2B,
            bytes([0x0E, 0x01, 0x00])  # Read basic identification
        )
        
        if response and len(response) >= 6:
            device = ModbusRTUDevice(unit_id=unit_id)
            
            # Parse identification data (simplified)
            device.device_type = 'Modbus Device'
            device.manufacturer = 'Unknown'
            
            return device
        
        return None
    
    def security_assessment(self) -> Dict:
        """
        Perform security assessment
        
        Returns:
            Assessment results
        """
        logger.info("🔒 Performing security assessment...")
        
        results = {
            'port': self.port,
            'baudrate': self.baudrate,
            'timestamp': datetime.now().isoformat(),
            'vulnerabilities': [],
            'recommendations': [],
            'risk_score': 0.0
        }
        
        if not self.connected:
            return results
        
        # No authentication
        results['vulnerabilities'].append({
            'id': 'MODBUS-RTU-001',
            'severity': 'critical',
            'description': 'No authentication mechanism',
            'cvss': 9.0,
            'remediation': 'Implement network segmentation and physical security'
        })
        
        # No encryption
        results['vulnerabilities'].append({
            'id': 'MODBUS-RTU-002',
            'severity': 'high',
            'description': 'No protocol encryption',
            'cvss': 7.5,
            'remediation': 'Use secure serial gateways with encryption'
        })
        
        # Broadcast support
        results['vulnerabilities'].append({
            'id': 'MODBUS-RTU-003',
            'severity': 'medium',
            'description': 'Broadcast messages affect all devices',
            'cvss': 6.0,
            'remediation': 'Disable broadcast if not required'
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
            'Implement physical security for serial connections',
            'Use serial-to-Ethernet gateways with authentication',
            'Deploy network segmentation',
            'Monitor serial traffic for anomalies',
            'Restrict physical access to serial ports',
            'Use Modbus TCP with security for remote access',
            'Regular security audits'
        ]
        
        logger.info(f"  Assessment complete: {len(results['vulnerabilities'])} vulnerabilities")
        logger.info(f"  Risk score: {results['risk_score']}/10.0")
        
        return results
    
    def generate_report(self) -> str:
        """Generate assessment report"""
        report = []
        report.append("=" * 70)
        report.append("🏭 MODBUS RTU SECURITY ASSESSMENT REPORT")
        report.append("=" * 70)
        
        report.append(f"Port: {self.port}")
        report.append(f"Baud Rate: {self.baudrate}")
        report.append(f"Safety Mode: {'ENABLED' if self.safety_mode else 'DISABLED'}")
        report.append("")
        
        # Device summary
        report.append("DEVICES DISCOVERED:")
        report.append("-" * 70)
        report.append(f"  Total Devices: {len(self.devices)}")
        for device in self.devices:
            report.append(f"    • Unit ID {device.unit_id}: {device.manufacturer} {device.device_type}")
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
║     🏭 KALIAGENT v4.4.0 - MODBUS RTU CLIENT                  ║
║                    Phase 10: Alpha 0.1.0                      ║
╚═══════════════════════════════════════════════════════════════╝

⚠️  CRITICAL SAFETY WARNING:
    Modbus RTU controls industrial processes!
    
    ONLY test on:
    ✅ Isolated lab systems you own
    ✅ Dedicated training facilities
    ✅ Systems with explicit written authorization
    
    NEVER test on:
    ❌ Production systems
    ❌ Critical infrastructure

    """)
    
    import sys
    
    port = sys.argv[1] if len(sys.argv) > 1 else '/dev/ttyUSB0'
    baudrate = int(sys.argv[2]) if len(sys.argv) > 2 else 9600
    
    # Initialize client
    modbus = ModbusRTUClient(port=port, baudrate=baudrate, safety_mode=True, verbose=True)
    
    # List ports
    ports = modbus.list_ports()
    
    # Connect
    if modbus.connect():
        # Scan unit IDs
        unit_ids = modbus.scan_unit_ids(1, 50)
        
        if unit_ids:
            # Read from first device
            unit_id = unit_ids[0]
            
            coils = modbus.read_coils(unit_id, 0, 50)
            di = modbus.read_discrete_inputs(unit_id, 0, 50)
            hr = modbus.read_holding_registers(unit_id, 0, 50)
            ir = modbus.read_input_registers(unit_id, 0, 50)
            
            print(f"\n📊 Unit ID {unit_id}:")
            print(f"  Coils: {len(coils)}")
            print(f"  Discrete Inputs: {len(di)}")
            print(f"  Holding Registers: {len(hr)}")
            print(f"  Input Registers: {len(ir)}")
        
        # Generate report
        print("\n" + modbus.generate_report())
        
        modbus.disconnect()
    else:
        print("\n❌ Failed to connect")


if __name__ == "__main__":
    main()
