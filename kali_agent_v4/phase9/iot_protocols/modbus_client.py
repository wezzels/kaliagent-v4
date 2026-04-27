#!/usr/bin/env python3
"""
📡 KaliAgent v4.3.0 - Phase 9: IoT Exploitation
Modbus Protocol Client & Security Testing

Tests Modbus/TCP for security vulnerabilities in ICS/SCADA systems:
- Coil read/write
- Register read/write
- PLC enumeration
- Function code testing
- Unauthorized access detection

Author: KaliAgent Team
Started: April 27, 2026
Status: Alpha (0.1.0)
"""

import logging
import socket
import struct
import json
from typing import List, Dict, Optional, Tuple
from datetime import datetime
from dataclasses import dataclass, field

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('ModbusClient')

# Try to import pymodbus, fall back to socket-based implementation
try:
    from pymodbus.client import ModbusTcpClient
    from pymodbus.exceptions import ModbusException
    PYMODBUS_AVAILABLE = True
except ImportError:
    PYMODBUS_AVAILABLE = False
    logger.warning("pymodbus not installed, using socket-based implementation")
    logger.warning("Install with: pip install pymodbus")


@dataclass
class ModbusDevice:
    """Represents a Modbus device"""
    host: str
    port: int = 502
    unit_id: int = 1
    vendor: str = "Unknown"
    model: str = "Unknown"
    firmware: str = "Unknown"
    coils: Dict = field(default_factory=dict)
    discrete_inputs: Dict = field(default_factory=dict)
    holding_registers: Dict = field(default_factory=dict)
    input_registers: Dict = field(default_factory=dict)
    vulnerabilities: List[Dict] = field(default_factory=list)
    risk_score: float = 0.0
    
    def to_dict(self) -> Dict:
        return {
            'host': self.host,
            'port': self.port,
            'unit_id': self.unit_id,
            'vendor': self.vendor,
            'model': self.model,
            'coils_count': len(self.coils),
            'registers_count': len(self.holding_registers),
            'vulnerabilities': self.vulnerabilities,
            'risk_score': self.risk_score
        }


class ModbusClient:
    """
    Modbus/TCP Security Testing Client
    
    Capabilities:
    - Device enumeration
    - Coil read/write testing
    - Register read/write testing
    - Function code scanning
    - PLC identification
    - Security assessment
    """
    
    VERSION = "0.1.0"
    
    # Modbus function codes
    FC_READ_COILS = 0x01
    FC_READ_DISCRETE_INPUTS = 0x02
    FC_READ_HOLDING_REGISTERS = 0x03
    FC_READ_INPUT_REGISTERS = 0x04
    FC_WRITE_SINGLE_COIL = 0x05
    FC_WRITE_SINGLE_REGISTER = 0x06
    FC_WRITE_MULTIPLE_COILS = 0x0F
    FC_WRITE_MULTIPLE_REGISTERS = 0x10
    FC_READ_WRITE_REGISTERS = 0x17
    
    # Common PLC unit IDs
    COMMON_UNIT_IDS = list(range(1, 256))
    
    # Known PLC signatures
    PLC_SIGNATURES = {
        'Siemens S7': {
            'registers': [0, 1, 2],
            'values': [0x5337, 0x3030, 0x3030]  # "S7000" in ASCII
        },
        'Schneider Electric': {
            'registers': [0, 1],
            'values': [0x5345, 0x2020]  # "SE  "
        },
        'Allen-Bradley': {
            'registers': [0, 1],
            'values': [0x4142, 0x2020]  # "AB  "
        },
        'Modicon': {
            'registers': [0],
            'values': [0x4D44]  # "MD"
        }
    }
    
    def __init__(self, host: str, port: int = 502, timeout: int = 5, verbose: bool = True):
        """
        Initialize Modbus Client
        
        Args:
            host: PLC/SCADA hostname or IP
            port: Modbus port (default: 502)
            timeout: Request timeout in seconds
            verbose: Enable verbose logging
        """
        self.host = host
        self.port = port
        self.timeout = timeout
        self.verbose = verbose
        
        if verbose:
            logger.setLevel(logging.DEBUG)
        
        self.device = ModbusDevice(host=host, port=port)
        self.transaction_id = 0
        
        logger.info(f"📡 Modbus Client v{self.VERSION} initialized")
        logger.info(f"🎯 Target: {host}:{port}")
        logger.warning(f"⚠️  WARNING: Testing SCADA/ICS systems can cause physical damage!")
        logger.warning(f"⚠️  ONLY test on isolated lab systems!")
    
    def _build_modbus_request(self, unit_id: int, function_code: int, 
                               data: bytes = b'') -> bytes:
        """
        Build Modbus/TCP request
        
        Args:
            unit_id: Slave unit ID
            function_code: Modbus function code
            data: Function-specific data
            
        Returns:
            Modbus/TCP packet bytes
        """
        self.transaction_id = (self.transaction_id + 1) % 65536
        
        # Modbus/TCP header (6 bytes)
        # Transaction ID (2) | Protocol ID (2) | Length (2)
        header = struct.pack('!HHH',
            self.transaction_id,
            0x0000,  # Protocol ID (Modbus)
            len(data) + 1  # Length (unit ID + data)
        )
        
        # Unit ID and function code
        packet = header + struct.pack('!BB', unit_id, function_code) + data
        
        return packet
    
    def _send_request(self, unit_id: int, function_code: int, 
                      data: bytes = b') -> Tuple[bool, bytes]:
        """
        Send Modbus request
        
        Args:
            unit_id: Slave unit ID
            function_code: Modbus function code
            data: Function-specific data
            
        Returns:
            (success, response) tuple
        """
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(self.timeout)
            sock.connect((self.host, self.port))
            
            request = self._build_modbus_request(unit_id, function_code, data)
            sock.send(request)
            
            # Read response header (6 bytes)
            header = sock.recv(6)
            if len(header) < 6:
                sock.close()
                return False, b''
            
            # Parse header
            trans_id, proto_id, length = struct.unpack('!HHH', header)
            
            # Read response body
            response = sock.recv(length)
            
            sock.close()
            
            return True, header + response
            
        except socket.timeout:
            logger.debug(f"⏱️  Timeout for unit {unit_id}, function {function_code:02x}")
            return False, b''
        except Exception as e:
            logger.error(f"❌ Request error: {e}")
            return False, b''
    
    def _parse_exception(self, response: bytes) -> Dict:
        """
        Parse Modbus exception response
        
        Args:
            response: Exception response bytes
            
        Returns:
            Exception details
        """
        if len(response) >= 3:
            function_code = response[0]
            exception_code = response[1]
            
            exception_messages = {
                0x01: "Illegal Function",
                0x02: "Illegal Data Address",
                0x03: "Illegal Data Value",
                0x04: "Slave Device Failure",
                0x05: "Acknowledge",
                0x06: "Slave Device Busy",
                0x08: "Memory Parity Error",
                0x0A: "Gateway Path Unavailable",
                0x0B: "Gateway Target Device Failed to Respond"
            }
            
            return {
                'function_code': function_code,
                'exception_code': exception_code,
                'message': exception_messages.get(exception_code, 'Unknown Exception')
            }
        
        return {'error': 'Invalid exception response'}
    
    def scan_unit_ids(self, start: int = 1, end: int = 255) -> List[int]:
        """
        Scan for active Modbus unit IDs
        
        Args:
            start: Starting unit ID
            end: Ending unit ID
            
        Returns:
            List of active unit IDs
        """
        logger.info(f"🔍 Scanning unit IDs {start}-{end}...")
        
        active_units = []
        
        for unit_id in range(start, end + 1):
            # Try to read holding register 0
            success, response = self._send_request(
                unit_id, 
                self.FC_READ_HOLDING_REGISTERS,
                struct.pack('!HH', 0, 1)  # Address 0, count 1
            )
            
            if success and response:
                # Check if it's a valid response (not exception)
                if len(response) >= 3:
                    func_code = response[7] if len(response) > 7 else response[1]
                    
                    # Normal response has same function code
                    if func_code == self.FC_READ_HOLDING_REGISTERS:
                        active_units.append(unit_id)
                        logger.debug(f"✅ Unit ID {unit_id} responded")
                    # Exception 0x02 (Illegal Data Address) still means device exists
                    elif len(response) > 8 and response[8] == 0x02:
                        active_units.append(unit_id)
                        logger.debug(f"✅ Unit ID {unit_id} responded (with exception)")
        
        logger.info(f"📊 Found {len(active_units)} active unit IDs")
        return active_units
    
    def read_coils(self, unit_id: int, address: int = 0, count: int = 10) -> List[int]:
        """
        Read coil status
        
        Args:
            unit_id: Slave unit ID
            address: Starting coil address
            count: Number of coils to read
            
        Returns:
            List of coil values (0 or 1)
        """
        logger.debug(f"📖 Reading coils from unit {unit_id}, address {address}...")
        
        success, response = self._send_request(
            unit_id,
            self.FC_READ_COILS,
            struct.pack('!HH', address, count)
        )
        
        if success and response:
            # Parse response
            if len(response) > 9:
                byte_count = response[8]
                coil_data = response[9:9 + byte_count]
                
                coils = []
                for byte in coil_data:
                    for i in range(8):
                        coils.append((byte >> i) & 1)
                
                return coils[:count]
        
        return []
    
    def write_coil(self, unit_id: int, address: int, value: bool) -> bool:
        """
        Write single coil
        
        Args:
            unit_id: Slave unit ID
            address: Coil address
            value: True/False or 1/0
            
        Returns:
            True if write successful
        """
        logger.warning(f"✏️  Writing coil {address} = {value} on unit {unit_id}")
        
        # Value for write: 0xFF00 = ON, 0x0000 = OFF
        value_bytes = struct.pack('!H', 0xFF00 if value else 0x0000)
        
        success, response = self._send_request(
            unit_id,
            self.FC_WRITE_SINGLE_COIL,
            struct.pack('!H', address) + value_bytes
        )
        
        if success and response:
            # Check for exception
            if len(response) > 7 and response[7] & 0x80:
                exception = self._parse_exception(response[8:])
                logger.error(f"❌ Write failed: {exception['message']}")
                return False
            
            logger.warning(f"⚠️  COIL WRITE SUCCESSFUL!")
            self.device.vulnerabilities.append({
                'type': 'unauthorized_coil_write',
                'severity': 'critical',
                'cvss': 9.0,
                'unit_id': unit_id,
                'address': address,
                'description': f'Unauthorized coil write allowed at address {address}'
            })
            return True
        
        return False
    
    def read_holding_registers(self, unit_id: int, address: int = 0, 
                                count: int = 10) -> List[int]:
        """
        Read holding registers
        
        Args:
            unit_id: Slave unit ID
            address: Starting register address
            count: Number of registers to read
            
        Returns:
            List of register values
        """
        logger.debug(f"📖 Reading holding registers from unit {unit_id}, address {address}...")
        
        success, response = self._send_request(
            unit_id,
            self.FC_READ_HOLDING_REGISTERS,
            struct.pack('!HH', address, count)
        )
        
        if success and response:
            # Parse response
            if len(response) > 8:
                byte_count = response[8]
                register_data = response[9:9 + byte_count]
                
                registers = []
                for i in range(0, len(register_data), 2):
                    if i + 1 < len(register_data):
                        value = struct.unpack('!H', register_data[i:i+2])[0]
                        registers.append(value)
                
                return registers
        
        return []
    
    def write_register(self, unit_id: int, address: int, value: int) -> bool:
        """
        Write single register
        
        Args:
            unit_id: Slave unit ID
            address: Register address
            value: Register value (0-65535)
            
        Returns:
            True if write successful
        """
        logger.warning(f"✏️  Writing register {address} = {value} on unit {unit_id}")
        
        success, response = self._send_request(
            unit_id,
            self.FC_WRITE_SINGLE_REGISTER,
            struct.pack('!HH', address, value)
        )
        
        if success and response:
            # Check for exception
            if len(response) > 7 and response[7] & 0x80:
                exception = self._parse_exception(response[8:])
                logger.error(f"❌ Write failed: {exception['message']}")
                return False
            
            logger.warning(f"⚠️  REGISTER WRITE SUCCESSFUL!")
            self.device.vulnerabilities.append({
                'type': 'unauthorized_register_write',
                'severity': 'critical',
                'cvss': 9.0,
                'unit_id': unit_id,
                'address': address,
                'description': f'Unauthorized register write allowed at address {address}'
            })
            return True
        
        return False
    
    def identify_plc(self, unit_id: int) -> Dict:
        """
        Attempt to identify PLC vendor/model
        
        Args:
            unit_id: Slave unit ID
            
        Returns:
            PLC identification results
        """
        logger.info(f"🔍 Identifying PLC on unit {unit_id}...")
        
        # Read first few registers to check for signatures
        registers = self.read_holding_registers(unit_id, 0, 10)
        
        if not registers:
            return {'vendor': 'Unknown', 'model': 'Unknown', 'confidence': 0}
        
        logger.debug(f"📊 Register values: {registers}")
        
        # Check against known signatures
        for vendor, sig in self.PLC_SIGNATURES.items():
            match = True
            for i, expected_value in enumerate(sig['values']):
                if i >= len(registers) or registers[i] != expected_value:
                    match = False
                    break
            
            if match:
                logger.info(f"✅ Identified: {vendor}")
                return {
                    'vendor': vendor,
                    'model': 'Unknown',
                    'confidence': 0.8,
                    'registers': registers[:10]
                }
        
        return {
            'vendor': 'Unknown',
            'model': 'Unknown',
            'confidence': 0,
            'registers': registers[:10]
        }
    
    def test_function_codes(self, unit_id: int) -> Dict:
        """
        Test supported function codes
        
        Args:
            unit_id: Slave unit ID
            
        Returns:
            Function code support matrix
        """
        logger.info(f"🔧 Testing function codes on unit {unit_id}...")
        
        function_codes = [
            self.FC_READ_COILS,
            self.FC_READ_DISCRETE_INPUTS,
            self.FC_READ_HOLDING_REGISTERS,
            self.FC_READ_INPUT_REGISTERS,
            self.FC_WRITE_SINGLE_COIL,
            self.FC_WRITE_SINGLE_REGISTER,
        ]
        
        results = {}
        
        for fc in function_codes:
            success, response = self._send_request(unit_id, fc, struct.pack('!HH', 0, 1))
            
            if success and response:
                # Check if normal response or exception
                if len(response) > 7:
                    response_fc = response[7]
                    
                    if response_fc == fc:
                        results[fc] = {'supported': True, 'exception': None}
                        logger.debug(f"✅ Function {fc:02x} supported")
                    elif response_fc == (fc | 0x80):
                        # Exception response
                        exception = self._parse_exception(response[8:])
                        results[fc] = {'supported': False, 'exception': exception['message']}
                        logger.debug(f"❌ Function {fc:02x}: {exception['message']}")
                    else:
                        results[fc] = {'supported': True, 'exception': None}
        
        return results
    
    def calculate_risk_score(self) -> float:
        """
        Calculate device risk score (0-10)
        
        Returns:
            Risk score
        """
        score = 5.0  # Base score
        
        # Unauthorized writes allowed
        write_vulns = [v for v in self.device.vulnerabilities 
                      if 'write' in v.get('type', '')]
        if write_vulns:
            score += min(3.0, len(write_vulns) * 0.5)
        
        # No authentication (Modbus typically has none)
        score += 1.0
        
        # Critical vulnerabilities
        for vuln in self.device.vulnerabilities:
            if vuln.get('severity') == 'critical':
                score += 1.0
        
        self.device.risk_score = min(10.0, score)
        return self.device.risk_score
    
    def generate_report(self, output_format: str = 'text') -> str:
        """
        Generate Modbus security assessment report
        
        Args:
            output_format: 'text' or 'json'
            
        Returns:
            Formatted report
        """
        logger.info("📊 Generating report...")
        
        self.calculate_risk_score()
        
        if output_format == 'json':
            return json.dumps(self.device.to_dict(), indent=2, default=str)
        
        # Text format
        report = []
        report.append("=" * 70)
        report.append("📡 MODBUS/TCP SECURITY ASSESSMENT REPORT")
        report.append("=" * 70)
        report.append(f"Device: {self.device.host}:{self.device.port}")
        report.append(f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        report.append(f"Risk Score: {self.device.risk_score}/10.0")
        report.append("")
        
        report.append("FINDINGS:")
        report.append("-" * 70)
        
        for vuln in self.device.vulnerabilities:
            report.append(f"⚠️  {vuln['severity'].upper()}: {vuln['description']}")
        
        if not self.device.vulnerabilities:
            report.append("ℹ️  No vulnerabilities detected (or testing limited)")
        
        report.append("")
        report.append("DEVICE INFORMATION:")
        report.append("-" * 70)
        report.append(f"Vendor: {self.device.vendor}")
        report.append(f"Model: {self.device.model}")
        report.append(f"Firmware: {self.device.firmware}")
        report.append(f"Unit ID: {self.device.unit_id}")
        report.append("")
        report.append(f"Coils Discovered: {len(self.device.coils)}")
        report.append(f"Registers Discovered: {len(self.device.holding_registers)}")
        
        report.append("")
        report.append("RECOMMENDATIONS:")
        report.append("-" * 70)
        report.append("1. Implement Modbus security extensions (if supported)")
        report.append("2. Use firewall rules to restrict Modbus access")
        report.append("3. Place SCADA network behind secure gateway")
        report.append("4. Disable unused function codes")
        report.append("5. Monitor and log all Modbus traffic")
        report.append("6. Implement network segmentation")
        report.append("7. Consider Modbus/TLS for encryption")
        report.append("")
        report.append("=" * 70)
        
        return "\n".join(report)
    
    def run_assessment(self) -> str:
        """
        Run complete Modbus security assessment
        
        Returns:
            Assessment report
        """
        logger.info("🚀 Starting Modbus security assessment...")
        logger.warning("⚠️  WARNING: This may modify PLC state! Use on lab systems only!")
        
        # Step 1: Scan unit IDs
        unit_ids = self.scan_unit_ids(1, 10)  # Scan first 10 IDs
        
        if not unit_ids:
            logger.info("ℹ️  No Modbus devices found")
            self.device.vulnerabilities.append({
                'type': 'no_devices',
                'severity': 'info',
                'description': 'No Modbus devices responded'
            })
        else:
            # Step 2: Test each unit
            for unit_id in unit_ids:
                self.device.unit_id = unit_id
                logger.info(f"\n🔍 Testing unit ID {unit_id}...")
                
                # Identify PLC
                plc_info = self.identify_plc(unit_id)
                self.device.vendor = plc_info.get('vendor', 'Unknown')
                
                # Read coils
                coils = self.read_coils(unit_id, 0, 20)
                if coils:
                    self.device.coils = {i: coils[i] for i in range(len(coils))}
                    logger.info(f"📊 Read {len(coils)} coils")
                
                # Read registers
                registers = self.read_holding_registers(unit_id, 0, 20)
                if registers:
                    self.device.holding_registers = {i: registers[i] for i in range(len(registers))}
                    logger.info(f"📊 Read {len(registers)} registers")
                
                # Test function codes
                fc_results = self.test_function_codes(unit_id)
                
                # Test write access (CAREFUL!)
                # Only test on lab systems!
                logger.info(f"⚠️  Testing write access (LAB ONLY)...")
                if self.write_coil(unit_id, 0, True):
                    # Write back to original value
                    original_value = self.device.coils.get(0, False)
                    self.write_coil(unit_id, 0, original_value)
        
        # Generate report
        report = self.generate_report()
        
        logger.info("✅ Assessment complete!")
        return report


def main():
    """Main entry point"""
    print("""
╔═══════════════════════════════════════════════════════════════╗
║     📡 KALIAGENT v4.3.0 - MODBUS SECURITY TESTER             ║
║                    Phase 9: Alpha 0.1.0                       ║
╚═══════════════════════════════════════════════════════════════╝

⚠️  WARNING: Modbus testing can affect physical systems!
⚠️  ONLY use on isolated lab networks!
⚠️  NEVER test on production SCADA/ICS systems!

    """)
    
    import sys
    host = sys.argv[1] if len(sys.argv) > 1 else "192.168.1.100"
    port = int(sys.argv[2]) if len(sys.argv) > 2 else 502
    
    # Initialize client
    modbus_client = ModbusClient(host=host, port=port, verbose=True)
    
    # Run assessment
    report = modbus_client.run_assessment()
    
    # Print report
    print("\n" + report)
    
    # Save to file
    with open(f'modbus_assessment_{host.replace(".", "_")}.txt', 'w') as f:
        f.write(report)
    
    print(f"\n✅ Report saved to: modbus_assessment_{host.replace('.', '_')}.txt")


if __name__ == "__main__":
    main()
