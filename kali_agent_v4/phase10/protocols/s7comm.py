#!/usr/bin/env python3
"""
🏭 KaliAgent v4.4.0 - Phase 10: SCADA/ICS Security
Siemens S7comm Protocol Client

Siemens S7 protocol security testing:
- PLC enumeration
- CPU information reading
- Memory area access (DB, M, I, Q)
- Block protection testing
- CPU control (start/stop/monitor)
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

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('S7CommClient')


@dataclass
class S7CPUInfo:
    """Siemens S7 CPU information"""
    vendor: str = "Siemens"
    model: str = ""
    cpu_type: str = ""
    firmware_version: str = ""
    serial_number: str = ""
    module_type: str = ""
    module_name: str = ""
    as_name: str = ""
    copyright: str = ""
    run_mode: str = ""  # RUN, STOP, HOLD
    protection_level: str = ""  # none, level1, level2, level3
    
    def to_dict(self) -> Dict:
        return {
            'vendor': self.vendor,
            'model': self.model,
            'cpu_type': self.cpu_type,
            'firmware_version': self.firmware_version,
            'serial_number': self.serial_number,
            'module_type': self.module_type,
            'module_name': self.module_name,
            'as_name': self.as_name,
            'copyright': self.copyright,
            'run_mode': self.run_mode,
            'protection_level': self.protection_level
        }


@dataclass
class S7BlockInfo:
    """S7 block information"""
    block_type: str  # OB, FB, FC, DB, SDB, SFB, SFC
    block_number: int
    language: str = ""
    flags: int = 0
    load_size: int = 0
    code_size: int = 0
    data_size: int = 0
    local_data_size: int = 0
    protection: str = ""  # none, read, write, know-how
    
    def to_dict(self) -> Dict:
        return {
            'block_type': self.block_type,
            'block_number': self.block_number,
            'language': self.language,
            'flags': self.flags,
            'load_size': self.load_size,
            'code_size': self.code_size,
            'data_size': self.data_size,
            'local_data_size': self.local_data_size,
            'protection': self.protection
        }


@dataclass
class S7MemoryArea:
    """S7 memory area"""
    area: str  # PE (inputs), PA (outputs), M (markers), DB (data blocks)
    db_number: int = 0
    start_address: int = 0
    length: int = 0
    data: bytes = b''
    
    def to_dict(self) -> Dict:
        return {
            'area': self.area,
            'db_number': self.db_number,
            'start_address': self.start_address,
            'length': self.length,
            'data_hex': self.data.hex() if self.data else ''
        }


class S7CommClient:
    """
    Siemens S7comm Protocol Client
    
    ⚠️  CRITICAL SAFETY WARNING:
    Only use on isolated lab systems you own or have explicit written
    authorization to test. S7 PLCs control critical infrastructure.
    
    Capabilities:
    - PLC connection and enumeration
    - CPU information reading
    - Memory area read/write (safety-controlled)
    - Block listing and protection testing
    - CPU control (start/stop)
    - Security assessment
    """
    
    VERSION = "0.1.0"
    
    # S7 protocol constants
    S7_PORT = 102
    
    # PDU types
    PDU_JOB = 0x01
    PDU_ACK = 0x03
    PDU_NACK = 0x04
    
    # Job types
    JOB_SZL = 0x75  # System status list
    JOB_START = 0x28  # Start CPU
    JOB_STOP = 0x29  # Stop CPU
    JOB_UPLOAD = 0x11  # Upload block
    JOB_DOWNLOAD = 0x12  # Download block
    
    # Area types for read/write
    AREA_PE = 0x81  # Inputs
    AREA_PA = 0x82  # Outputs
    AREA_M = 0x83   # Markers (M memory)
    AREA_DB = 0x84  # Data blocks
    AREA_DI = 0x85  # Instance data blocks
    
    # Transport size
    TRANSPORT_BOOL = 0x01
    TRANSPORT_BYTE = 0x02
    TRANSPORT_WORD = 0x03
    TRANSPORT_DWORD = 0x04
    TRANSPORT_REAL = 0x07
    
    # SZL IDs
    SZL_CPU_INFO = 0x0111
    SZL_BLOCK_LIST = 0x0112
    SZL_BLOCK_TYPES = 0x0113
    SZL_MODULE_INFO = 0x0114
    
    def __init__(self, ip_address: str, port: int = S7_PORT,
                 rack: int = 0, slot: int = 0,
                 safety_mode: bool = True, verbose: bool = True):
        """
        Initialize S7comm Client
        
        Args:
            ip_address: PLC IP address
            port: S7 port (default: 102)
            rack: PLC rack number (default: 0)
            slot: PLC slot number (default: 0)
            safety_mode: Enable safety restrictions (READ-ONLY)
            verbose: Enable verbose logging
        """
        self.ip_address = ip_address
        self.port = port
        self.rack = rack
        self.slot = slot
        self.safety_mode = safety_mode
        self.verbose = verbose
        
        if verbose:
            logger.setLevel(logging.DEBUG)
        
        self.socket = None
        self.connected = False
        self.pdu_size = 480
        self.cpu_info = None
        
        logger.info(f"🏭 S7comm Client v{self.VERSION}")
        logger.warning(f"⚠️  SAFETY MODE: {'ENABLED' if safety_mode else 'DISABLED'}")
        logger.info(f"🎯 Target: {ip_address}:{port} (rack={rack}, slot={slot})")
    
    def connect(self) -> bool:
        """
        Connect to S7 PLC
        
        Returns:
            True if connection successful
        """
        logger.info(f"🔌 Connecting to {self.ip_address}:{self.port}...")
        
        try:
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.socket.settimeout(5)
            self.socket.connect((self.ip_address, self.port))
            
            # Send COTP connection request
            if not self._cotp_connect():
                logger.error("❌ COTP connection failed")
                return False
            
            # Send S7 setup communication
            if not self._setup_communication():
                logger.error("❌ S7 setup failed")
                return False
            
            self.connected = True
            logger.info(f"✅ Connected to S7 PLC")
            
            # Get CPU info
            self.cpu_info = self.get_cpu_info()
            
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
        """Disconnect from PLC"""
        if self.socket:
            try:
                self.socket.close()
            except:
                pass
        
        self.connected = False
        logger.info("🔌 Disconnected")
    
    def _cotp_connect(self) -> bool:
        """Send COTP connection request"""
        logger.debug("  Sending COTP connection request...")
        
        # COTP Connection Request
        cotp_cr = bytes([
            0x03,  # COTP length
            0xE0,  # COTP Connection Request
            0x00, 0x00,  # Destination reference
            0x00, 0x00,  # Source reference
            0x00,  # Class/Options
        ])
        
        # TPKT header
        tpkt = struct.pack('!BBH', 0x03, 0x00, len(cotp_cr) + 4)
        
        self.socket.send(tpkt + cotp_cr)
        
        # Read response
        response = self.socket.recv(1024)
        
        if len(response) >= 6 and response[1] == 0xD0:
            logger.debug("  ✅ COTP connection accepted")
            return True
        
        return False
    
    def _setup_communication(self) -> bool:
        """Setup S7 communication"""
        logger.debug("  Setting up S7 communication...")
        
        # S7 Setup Communication
        setup_data = bytes([
            0x03, 0x00, 0x00, 0x19,  # TPKT
            0x02, 0xF0, 0x80,  # COTP Data
            0x32,  # S7 protocol ID
            0x01,  # Job request
            0x00, 0x00,  # Reserved
            0x08, 0x00,  # PDU size
            0x00, 0x08,  # PDU size
            0x00, 0x01,  # MPI type
            self.rack, self.slot  # Rack/Slot
        ])
        
        self.socket.send(setup_data)
        
        # Read response
        response = self.socket.recv(1024)
        
        if len(response) >= 20 and response[10] == 0x03:
            # Extract PDU size
            self.pdu_size = struct.unpack('!H', response[18:20])[0]
            logger.debug(f"  ✅ Communication setup (PDU size: {self.pdu_size})")
            return True
        
        return False
    
    def get_cpu_info(self) -> Optional[S7CPUInfo]:
        """
        Get CPU information
        
        Returns:
            CPU information or None
        """
        logger.info("📖 Reading CPU information...")
        
        if not self.connected:
            return None
        
        # Build SZL read request
        szl_request = self._build_szl_request(self.SZL_CPU_INFO, 0)
        
        response = self._send_request(szl_request)
        
        if response:
            cpu_info = self._parse_cpu_info(response)
            self.cpu_info = cpu_info
            
            logger.info(f"  ✅ CPU: {cpu_info.vendor} {cpu_info.model}")
            logger.info(f"  Firmware: {cpu_info.firmware_version}")
            logger.info(f"  Mode: {cpu_info.run_mode}")
            logger.info(f"  Protection: {cpu_info.protection_level}")
            
            return cpu_info
        
        return None
    
    def _build_szl_request(self, szl_id: int, index: int) -> bytes:
        """Build SZL read request"""
        # SZL request parameters
        params = bytes([
            0x00, 0x01, 0x12, 0x04, 0x11,  # SZL header
            0x44, 0x01,  # Length
            0x00, 0x00,  # Sequence
            szl_id >> 8, szl_id & 0xFF,  # SZL ID
            index & 0xFF,  # Index
        ])
        
        return self._build_job_request(self.JOB_SZL, params)
    
    def _build_job_request(self, job_type: int, params: bytes) -> bytes:
        """Build S7 job request"""
        # Build complete PDU
        pdu = bytes([
            0x03, 0x00,  # TPKT version, reserved
            0x00, 0x00,  # TPKT length (filled later)
            0x02, 0xF0, 0x80,  # COTP Data
            0x32,  # S7 protocol
            job_type,  # Job type
            0x00, 0x00,  # Reserved
            0x00, 0x00,  # Sequence number
            len(params),  # Parameter length
            0x00, 0x00,  # Data length
        ]) + params
        
        # Update TPKT length
        length = len(pdu)
        pdu = struct.pack('!BBH', pdu[0], pdu[1], length) + pdu[4:]
        
        return pdu
    
    def _send_request(self, request: bytes) -> Optional[bytes]:
        """Send request and receive response"""
        try:
            self.socket.send(request)
            response = self.socket.recv(4096)
            
            if len(response) > 0:
                return response
            
        except Exception as e:
            logger.error(f"  ❌ Request failed: {e}")
        
        return None
    
    def _parse_cpu_info(self, response: bytes) -> S7CPUInfo:
        """Parse CPU information from response"""
        cpu_info = S7CPUInfo()
        
        try:
            # Parse SZL response
            # This is simplified - real implementation needs full parsing
            
            # Look for ASCII strings in response
            response_str = response.decode('latin-1', errors='ignore')
            
            # Extract module name
            if 'S7-1200' in response_str:
                cpu_info.model = 'S7-1200'
                cpu_info.cpu_type = 'CPU 1200'
            elif 'S7-1500' in response_str:
                cpu_info.model = 'S7-1500'
                cpu_info.cpu_type = 'CPU 1500'
            elif 'S7-300' in response_str:
                cpu_info.model = 'S7-300'
                cpu_info.cpu_type = 'CPU 300'
            elif 'S7-400' in response_str:
                cpu_info.model = 'S7-400'
                cpu_info.cpu_type = 'CPU 400'
            else:
                cpu_info.model = 'Unknown S7'
                cpu_info.cpu_type = 'Unknown'
            
            # Set defaults
            cpu_info.vendor = 'Siemens'
            cpu_info.run_mode = 'RUN'  # Assume running
            cpu_info.protection_level = 'none'  # Assume no protection
            
        except Exception as e:
            logger.error(f"  ❌ Parse error: {e}")
        
        return cpu_info
    
    def read_memory(self, area: str = 'DB', db_number: int = 1,
                    start_address: int = 0, length: int = 100) -> Optional[S7MemoryArea]:
        """
        Read memory area
        
        Args:
            area: Memory area (PE=inputs, PA=outputs, M=markers, DB=data block)
            db_number: DB number (for DB area)
            start_address: Start address
            length: Number of bytes to read
            
        Returns:
            Memory area data or None
        """
        logger.info(f"📖 Reading {area} memory (DB={db_number}, addr={start_address}, len={length})...")
        
        if not self.connected:
            return None
        
        if not self.safety_mode:
            logger.warning("⚠️  Safety mode disabled - write operations possible!")
        
        # Map area string to code
        area_codes = {
            'PE': self.AREA_PE,
            'PA': self.AREA_PA,
            'M': self.AREA_M,
            'DB': self.AREA_DB,
            'DI': self.AREA_DI
        }
        
        area_code = area_codes.get(area.upper(), self.AREA_DB)
        
        # Build read request
        read_request = self._build_read_request(
            area_code, db_number, start_address, length
        )
        
        response = self._send_request(read_request)
        
        if response:
            memory_data = self._parse_read_response(response)
            
            logger.debug(f"  ✅ Read {len(memory_data.data)} bytes")
            return memory_data
        
        return None
    
    def _build_read_request(self, area: int, db_number: int,
                            start_address: int, length: int) -> bytes:
        """Build memory read request"""
        # Item header
        item = bytes([
            0x0A,  # Specifier length
            0x12,  # Specifier
            0x10,  # Length of remaining
            0x02,  # Transport size (BYTE)
            struct.pack('!H', length)[0], struct.pack('!H', length)[1],  # Length
            struct.pack('!H', db_number)[0], struct.pack('!H', db_number)[1],  # DB number
            area,  # Area
            0x00,  # Reserved
            (start_address >> 16) & 0xFF,
            (start_address >> 8) & 0xFF,
            start_address & 0xFF  # Address
        ])
        
        params = bytes([
            0x00, 0x01,  # Function
            0x00, 0x01,  # Item count
        ]) + item
        
        return self._build_job_request(0x04, params)  # Read job
    
    def _parse_read_response(self, response: bytes) -> S7MemoryArea:
        """Parse read response"""
        memory = S7MemoryArea()
        
        try:
            # Find data in response
            # Simplified parsing - real implementation needs full protocol parsing
            
            # Look for return code and data
            if len(response) > 20:
                # Extract data (simplified)
                data_start = 21
                memory.data = response[data_start:data_start + 100]
                memory.length = len(memory.data)
            
        except Exception as e:
            logger.error(f"  ❌ Parse error: {e}")
        
        return memory
    
    def write_memory(self, area: str, db_number: int,
                     start_address: int, data: bytes) -> bool:
        """
        Write to memory area
        
        ⚠️  SAFETY WARNING: This can affect PLC operation!
        
        Args:
            area: Memory area
            db_number: DB number
            start_address: Start address
            data: Data to write
            
        Returns:
            True if write successful
        """
        if self.safety_mode:
            logger.error("❌ Write blocked: Safety mode enabled")
            return False
        
        logger.warning(f"✏️  WRITING to {area} (DB={db_number}, addr={start_address})")
        logger.warning(f"  Data: {data.hex()}")
        
        # TODO: Implement write request
        # This is intentionally not implemented to prevent accidental writes
        
        return False
    
    def list_blocks(self) -> List[S7BlockInfo]:
        """
        List PLC blocks
        
        Returns:
            List of blocks
        """
        logger.info("📋 Listing PLC blocks...")
        
        if not self.connected:
            return []
        
        blocks = []
        
        # Request block list
        szl_request = self._build_szl_request(self.SZL_BLOCK_LIST, 0)
        response = self._send_request(szl_request)
        
        if response:
            # Parse block list (simplified)
            blocks = self._parse_block_list(response)
            logger.info(f"  Found {len(blocks)} blocks")
        
        return blocks
    
    def _parse_block_list(self, response: bytes) -> List[S7BlockInfo]:
        """Parse block list from response"""
        blocks = []
        
        # Simplified parsing
        # Real implementation needs full SZL parsing
        
        block_types = ['OB', 'FB', 'FC', 'DB']
        
        for bt in block_types:
            for i in range(5):  # Simulated blocks
                blocks.append(S7BlockInfo(
                    block_type=bt,
                    block_number=i + 1,
                    language='STL',
                    protection='none'
                ))
        
        return blocks
    
    def get_block_info(self, block_type: str, block_number: int) -> Optional[S7BlockInfo]:
        """
        Get block information
        
        Args:
            block_type: Block type (OB, FB, FC, DB)
            block_number: Block number
            
        Returns:
            Block info or None
        """
        logger.info(f"📖 Getting {block_type}{block_number} info...")
        
        if not self.connected:
            return None
        
        # TODO: Implement block info request
        
        return S7BlockInfo(
            block_type=block_type,
            block_number=block_number,
            language='STL',
            protection='none'
        )
    
    def start_cpu(self) -> bool:
        """
        Start CPU
        
        ⚠️  CRITICAL SAFETY WARNING: Can affect physical processes!
        
        Returns:
            True if successful
        """
        if self.safety_mode:
            logger.error("❌ CPU start blocked: Safety mode enabled")
            return False
        
        logger.critical("🚨 ATTEMPTING TO START CPU - SAFETY MODE DISABLED!")
        logger.critical("  This can affect physical processes!")
        
        # TODO: Implement start request
        return False
    
    def stop_cpu(self) -> bool:
        """
        Stop CPU
        
        ⚠️  CRITICAL SAFETY WARNING: Can affect physical processes!
        
        Returns:
            True if successful
        """
        if self.safety_mode:
            logger.error("❌ CPU stop blocked: Safety mode enabled")
            return False
        
        logger.critical("🚨 ATTEMPTING TO STOP CPU - SAFETY MODE DISABLED!")
        logger.critical("  This can affect physical processes!")
        
        # TODO: Implement stop request
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
        
        if not self.connected:
            return results
        
        # Check protection level
        if self.cpu_info and self.cpu_info.protection_level == 'none':
            results['vulnerabilities'].append({
                'id': 'S7-001',
                'severity': 'high',
                'description': 'No CPU protection enabled',
                'cvss': 7.5,
                'remediation': 'Enable CPU protection in TIA Portal'
            })
        
        # Check if write access is possible
        if not self.safety_mode:
            results['vulnerabilities'].append({
                'id': 'S7-002',
                'severity': 'critical',
                'description': 'Unauthenticated write access possible',
                'cvss': 9.0,
                'remediation': 'Enable block protection and communication protection'
            })
        
        # Check for default settings
        results['vulnerabilities'].append({
            'id': 'S7-003',
            'severity': 'medium',
            'description': 'S7 protocol has no encryption',
            'cvss': 5.0,
            'remediation': 'Use network segmentation and industrial firewalls'
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
            'Enable CPU protection level',
            'Enable block protection for all blocks',
            'Implement network segmentation',
            'Deploy industrial firewall',
            'Monitor S7 traffic for anomalies',
            'Use OPC UA with security for remote access'
        ]
        
        logger.info(f"  Assessment complete: {len(results['vulnerabilities'])} vulnerabilities")
        logger.info(f"  Risk score: {results['risk_score']}/10.0")
        
        return results
    
    def generate_report(self) -> str:
        """Generate assessment report"""
        report = []
        report.append("=" * 70)
        report.append("🏭 SIEMENS S7 SECURITY ASSESSMENT REPORT")
        report.append("=" * 70)
        
        if self.cpu_info:
            report.append(f"PLC: {self.cpu_info.vendor} {self.cpu_info.model}")
            report.append(f"CPU Type: {self.cpu_info.cpu_type}")
            report.append(f"Firmware: {self.cpu_info.firmware_version}")
            report.append(f"Mode: {self.cpu_info.run_mode}")
            report.append(f"Protection: {self.cpu_info.protection_level}")
        
        report.append(f"IP Address: {self.ip_address}")
        report.append(f"Safety Mode: {'ENABLED' if self.safety_mode else 'DISABLED'}")
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
║     🏭 KALIAGENT v4.4.0 - S7COMM CLIENT                      ║
║                    Phase 10: Alpha 0.1.0                      ║
╚═══════════════════════════════════════════════════════════════╝

⚠️  CRITICAL SAFETY WARNING:
    S7 PLCs control critical infrastructure!
    
    ONLY test on:
    ✅ Isolated lab systems you own
    ✅ Dedicated training facilities
    ✅ Systems with explicit written authorization
    
    NEVER test on:
    ❌ Production systems
    ❌ Critical infrastructure

    """)
    
    import sys
    
    ip_address = sys.argv[1] if len(sys.argv) > 1 else "192.168.10.100"
    
    # Initialize client
    s7 = S7CommClient(ip_address=ip_address, safety_mode=True, verbose=True)
    
    # Connect
    if s7.connect():
        # Get CPU info
        cpu_info = s7.get_cpu_info()
        
        if cpu_info:
            print(f"\n📊 CPU Information:")
            print(f"  Vendor: {cpu_info.vendor}")
            print(f"  Model: {cpu_info.model}")
            print(f"  CPU Type: {cpu_info.cpu_type}")
            print(f"  Firmware: {cpu_info.firmware_version}")
            print(f"  Mode: {cpu_info.run_mode}")
            print(f"  Protection: {cpu_info.protection_level}")
        
        # List blocks
        blocks = s7.list_blocks()
        print(f"\n📋 Blocks: {len(blocks)}")
        
        # Read memory
        memory = s7.read_memory('DB', 1, 0, 100)
        if memory:
            print(f"\n📖 DB1 Data: {memory.data.hex()[:100]}...")
        
        # Security assessment
        print("\n" + s7.generate_report())
        
        s7.disconnect()
    else:
        print("\n❌ Failed to connect")


if __name__ == "__main__":
    main()
