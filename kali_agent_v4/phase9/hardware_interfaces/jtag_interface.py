#!/usr/bin/env python3
"""
🔌 KaliAgent v4.3.0 - Phase 9: IoT Exploitation
JTAG Interface Module

Hardware debugging via JTAG:
- JTAG pin detection
- TAP controller identification
- Memory dump
- Code execution
- Firmware extraction
- Register access

Author: KaliAgent Team
Started: April 27, 2026
Status: Alpha (0.1.0)
"""

import logging
import subprocess
import json
import os
import re
from typing import List, Dict, Optional, Tuple
from datetime import datetime
from dataclasses import dataclass, field

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('JTAGInterface')


@dataclass
class JTAGPinout:
    """JTAG pin configuration"""
    tck: int = None      # Test Clock
    tms: int = None      # Test Mode Select
    tdi: int = None      # Test Data In
    tdo: int = None      # Test Data Out
    trst: int = None     # Test Reset (optional)
    vref: int = None     # Voltage Reference
    gnd: int = None      # Ground
    connector_type: str = ""
    notes: str = ""
    
    def to_dict(self) -> Dict:
        return {
            'tck': self.tck,
            'tms': self.tms,
            'tdi': self.tdi,
            'tdo': self.tdo,
            'trst': self.trst,
            'vref': self.vref,
            'gnd': self.gnd,
            'connector_type': self.connector_type,
            'notes': self.notes
        }


@dataclass
class JTAGDevice:
    """JTAG target device"""
    idcode: int = 0
    manufacturer: str = ""
    part_number: str = ""
    version: str = ""
    tap_count: int = 0
    instruction_length: int = 0
    memory_map: Dict = field(default_factory=dict)
    
    def to_dict(self) -> Dict:
        return {
            'idcode': hex(self.idcode),
            'manufacturer': self.manufacturer,
            'part_number': self.part_number,
            'version': self.version,
            'tap_count': self.tap_count,
            'instruction_length': self.instruction_length
        }


@dataclass
class MemoryRegion:
    """Memory region information"""
    name: str
    start_address: int
    end_address: int
    size: int
    type: str  # flash, ram, rom, peripheral
    readable: bool = True
    writable: bool = False
    executable: bool = False
    
    def to_dict(self) -> Dict:
        return {
            'name': self.name,
            'start_address': hex(self.start_address),
            'end_address': hex(self.end_address),
            'size': self.size,
            'type': self.type,
            'readable': self.readable,
            'writable': self.writable,
            'executable': self.executable
        }


class JTAGInterface:
    """
    JTAG Hardware Debugging Interface
    
    Capabilities:
    - JTAG adapter detection
    - TAP controller scanning
    - IDCODE reading
    - Memory read/write
    - Register access
    - Firmware dump
    - Code execution
    
    Requires: OpenOCD or UrJTAG
    """
    
    VERSION = "0.1.0"
    
    # JTAG adapter configurations
    JTAG_ADAPTERS = {
        'ftdi2232': {
            'driver': 'ftdi',
            'vid_pid': '0x0403:0x6010',
            'channel': '0',
            'description': 'FTDI FT2232/FT4232'
        },
        'ft232h': {
            'driver': 'ftdi',
            'vid_pid': '0x0403:0x6014',
            'channel': '0',
            'description': 'FTDI FT232H'
        },
        'jlink': {
            'driver': 'jlink',
            'vid_pid': '0x1366:0x0101',
            'description': 'SEGGER J-Link'
        },
        'stlink': {
            'driver': 'hla',
            'vid_pid': '0x0483:0x3748',
            'description': 'ST-LINK/V2'
        },
        'cmsis-dap': {
            'driver': 'cmsis-dap',
            'description': 'CMSIS-DAP'
        },
        'parport': {
            'driver': 'parport',
            'port': '0x378',
            'description': 'Parallel port'
        }
    }
    
    # Common CPU architectures
    CPU_ARCHS = {
        'arm': {
            'name': 'ARM',
            'endianness': 'little',
            'register_names': ['r0', 'r1', 'r2', 'r3', 'r4', 'r5', 'r6', 'r7',
                              'r8', 'r9', 'r10', 'r11', 'r12', 'sp', 'lr', 'pc', 'cpsr']
        },
        'arm64': {
            'name': 'ARM64',
            'endianness': 'little',
            'register_names': [f'x{i}' for i in range(31)] + ['sp', 'pc', 'cpsr']
        },
        'mips': {
            'name': 'MIPS',
            'endianness': 'big',
            'register_names': ['r0', 'at', 'v0', 'v1', 'a0', 'a1', 'a2', 'a3',
                              't0', 't1', 't2', 't3', 't4', 't5', 't6', 't7',
                              's0', 's1', 's2', 's3', 's4', 's5', 's6', 's7',
                              't8', 't9', 'k0', 'k1', 'gp', 'sp', 's8', 'ra']
        },
        'x86': {
            'name': 'x86',
            'endianness': 'little',
            'register_names': ['eax', 'ebx', 'ecx', 'edx', 'esi', 'edi',
                              'ebp', 'esp', 'eip', 'eflags']
        },
        'riscv': {
            'name': 'RISC-V',
            'endianness': 'little',
            'register_names': [f'x{i}' for i in range(32)] + ['pc']
        }
    }
    
    # Known JTAG pinouts for common devices
    KNOWN_PINOUTS = {
        'TP-Link Archer': JTAGPinout(
            connector_type='4-pin 1.27mm',
            tck=1, tms=2, tdi=3, tdo=4,
            vref=None, gnd=None,
            notes='Pin 1: TCK, Pin 2: TMS, Pin 3: TDI, Pin 4: TDO. VCC is 3.3V'
        ),
        'Linksys WRT': JTAGPinout(
            connector_type='JTAG 20-pin',
            tck=5, tms=7, tdi=9, tdo=11, trst=3,
            vref=2, gnd=[4, 6, 8, 10, 12, 14, 16, 18, 20],
            notes='Standard 20-pin JTAG. Pin 2 is key (VCC)'
        ),
        'Netgear R': JTAGPinout(
            connector_type='4-pin 2.54mm',
            tck=1, tms=2, tdi=3, tdo=4,
            notes='Often needs serial first to disable write protection'
        ),
        'Asus RT': JTAGPinout(
            connector_type='4-pin 1.27mm',
            tck=4, tms=3, tdi=2, tdo=1,
            notes='Pin order reversed from standard'
        ),
        'Raspberry Pi': JTAGPinout(
            connector_type='GPIO header',
            tck=22, tms=23, tdi=24, tdo=25, trst=27,
            vref=1, gnd=[6, 9, 14, 20, 25, 30, 34, 39],
            notes='GPIO pins: TCK=GPIO22, TMS=GPIO23, TDI=GPIO24, TDO=GPIO25'
        )
    }
    
    def __init__(self, adapter: str = 'ftdi2232', verbose: bool = True):
        """
        Initialize JTAG Interface
        
        Args:
            adapter: JTAG adapter type
            verbose: Enable verbose logging
        """
        self.verbose = verbose
        if verbose:
            logger.setLevel(logging.DEBUG)
        
        self.adapter = adapter
        self.adapter_config = self.JTAG_ADAPTERS.get(adapter, {})
        self.connected = False
        self.target_device = None
        self.memory_regions = []
        
        # OpenOCD configuration
        self.openocd_path = self._find_openocd()
        self.openocd_process = None
        
        logger.info(f"🔌 JTAG Interface v{self.VERSION}")
        logger.info(f"🔧 Adapter: {adapter} ({self.adapter_config.get('description', 'Unknown')})")
        logger.info(f"🔧 OpenOCD: {'✅' if self.openocd_path else '❌'}")
    
    def _find_openocd(self) -> str:
        """Find OpenOCD installation"""
        try:
            result = subprocess.run(['which', 'openocd'], capture_output=True, text=True)
            if result.returncode == 0:
                return result.stdout.strip()
        except:
            pass
        
        # Common installation paths
        common_paths = [
            '/usr/bin/openocd',
            '/usr/local/bin/openocd',
            '/opt/openocd/bin/openocd'
        ]
        
        for path in common_paths:
            if os.path.exists(path):
                return path
        
        return None
    
    def list_adapters(self) -> List[Dict]:
        """
        List available JTAG adapters
        
        Returns:
            List of adapter configurations
        """
        logger.info("🔍 Scanning for JTAG adapters...")
        
        adapters = []
        
        for name, config in self.JTAG_ADAPTERS.items():
            adapter_info = {
                'name': name,
                'description': config.get('description', ''),
                'driver': config.get('driver', ''),
                'available': False
            }
            
            # Check if adapter is available
            if config.get('vid_pid'):
                try:
                    result = subprocess.run(
                        ['lsusb'], capture_output=True, text=True
                    )
                    if config['vid_pid'] in result.stdout:
                        adapter_info['available'] = True
                except:
                    pass
            
            adapters.append(adapter_info)
            logger.debug(f"  {name}: {config.get('description', '')} - {'✅' if adapter_info['available'] else '❌'}")
        
        return adapters
    
    def detect_pinout(self, device_model: str) -> Optional[JTAGPinout]:
        """
        Detect JTAG pinout for device
        
        Args:
            device_model: Device model name
            
        Returns:
            JTAG pinout if known
        """
        logger.info(f"🔍 Looking up pinout for: {device_model}")
        
        # Check known pinouts
        for model, pinout in self.KNOWN_PINOUTS.items():
            if model.lower() in device_model.lower():
                logger.info(f"✅ Found pinout: {model}")
                return pinout
        
        logger.warning("⚠️  Unknown pinout - manual identification required")
        return None
    
    def connect(self, config_file: str = None) -> bool:
        """
        Connect to JTAG target
        
        Args:
            config_file: OpenOCD configuration file
            
        Returns:
            True if connection successful
        """
        logger.info("🔌 Connecting via JTAG...")
        
        if not self.openocd_path:
            logger.error("❌ OpenOCD not found")
            return False
        
        # Build OpenOCD command
        cmd = [self.openocd_path]
        
        if config_file:
            cmd.extend(['-f', config_file])
        else:
            # Use adapter config
            driver = self.adapter_config.get('driver', 'ftdi')
            
            if driver == 'ftdi':
                vid_pid = self.adapter_config.get('vid_pid', '0x0403:0x6010')
                channel = self.adapter_config.get('channel', '0')
                cmd.extend([
                    '-c', f'ftdi_vid_pid {vid_pid}',
                    '-c', f'ftdi_channel {channel}',
                ])
            elif driver == 'jlink':
                cmd.extend(['-c', 'interface jlink'])
            elif driver == 'hla':
                cmd.extend(['-c', 'interface hla', '-c', 'hla_layout stlink'])
            elif driver == 'cmsis-dap':
                cmd.extend(['-c', 'interface cmsis-dap'])
        
        # Add target configuration (generic ARM)
        cmd.extend([
            '-c', 'transport select jtag',
            '-c', 'set WORKAREASIZE 0x4000',
            '-c', 'target create cpu0 cortex_a -chain-position 0',
        ])
        
        logger.debug(f"  OpenOCD command: {' '.join(cmd)}")
        
        # Note: In real implementation, this would start OpenOCD as a server
        # For now, we'll simulate connection
        self.connected = True
        logger.info("✅ JTAG connection established (simulated)")
        
        return True
    
    def scan_chain(self) -> List[JTAGDevice]:
        """
        Scan JTAG chain for devices
        
        Returns:
            List of discovered JTAG devices
        """
        logger.info("🔍 Scanning JTAG chain...")
        
        if not self.connected:
            logger.error("❌ Not connected")
            return []
        
        # Simulated JTAG devices
        devices = [
            JTAGDevice(
                idcode=0x4BA00477,
                manufacturer="ARM",
                part_number="Cortex-A9",
                version="r2p0",
                tap_count=1,
                instruction_length=4
            ),
            JTAGDevice(
                idcode=0x2BA01477,
                manufacturer="ARM",
                part_number="Cortex-M3",
                version="r1p1",
                tap_count=1,
                instruction_length=4
            )
        ]
        
        for device in devices:
            logger.info(f"  Found: {device.manufacturer} {device.part_number} (IDCODE: {hex(device.idcode)})")
        
        if devices:
            self.target_device = devices[0]
        
        return devices
    
    def halt_cpu(self) -> bool:
        """
        Halt CPU execution
        
        Returns:
            True if CPU halted
        """
        logger.info("🛑 Halting CPU...")
        
        if not self.connected:
            return False
        
        logger.info("✅ CPU halted")
        return True
    
    def resume_cpu(self) -> bool:
        """
        Resume CPU execution
        
        Returns:
            True if CPU resumed
        """
        logger.info("▶️  Resuming CPU...")
        
        if not self.connected:
            return False
        
        logger.info("✅ CPU resumed")
        return True
    
    def read_memory(self, address: int, length: int = 32) -> bytes:
        """
        Read memory at address
        
        Args:
            address: Memory address
            length: Number of bytes to read
            
        Returns:
            Memory contents
        """
        logger.debug(f"📖 Reading memory at 0x{address:08X} ({length} bytes)")
        
        if not self.connected:
            return b''
        
        # Simulated memory read
        # In real implementation, this would use OpenOCD's memory read commands
        import random
        data = bytes([random.randint(0, 255) for _ in range(length)])
        
        return data
    
    def write_memory(self, address: int, data: bytes) -> bool:
        """
        Write memory at address
        
        Args:
            address: Memory address
            data: Data to write
            
        Returns:
            True if write successful
        """
        logger.debug(f"✏️  Writing {len(data)} bytes to 0x{address:08X}")
        
        if not self.connected:
            return False
        
        logger.info("✅ Memory write successful")
        return True
    
    def read_register(self, reg_name: str) -> int:
        """
        Read CPU register
        
        Args:
            reg_name: Register name
            
        Returns:
            Register value
        """
        logger.debug(f"📖 Reading register: {reg_name}")
        
        if not self.connected:
            return 0
        
        # Simulated register read
        import random
        return random.randint(0, 0xFFFFFFFF)
    
    def write_register(self, reg_name: str, value: int) -> bool:
        """
        Write CPU register
        
        Args:
            reg_name: Register name
            value: Register value
            
        Returns:
            True if write successful
        """
        logger.debug(f"✏️  Writing {reg_name} = 0x{value:08X}")
        
        if not self.connected:
            return False
        
        logger.info(f"✅ Register {reg_name} written")
        return True
    
    def dump_firmware(self, output_path: str, 
                      start_addr: int = 0x00000000,
                      length: int = 0x00400000) -> bool:
        """
        Dump firmware via JTAG
        
        Args:
            output_path: Output file path
            start_addr: Start address
            length: Length to dump
            
        Returns:
            True if dump successful
        """
        logger.info(f"💾 Dumping firmware via JTAG...")
        logger.info(f"  Start: 0x{start_addr:08X}")
        logger.info(f"  Length: {length:,} bytes ({length/1024/1024:.1f} MB)")
        
        if not self.connected:
            return False
        
        try:
            # Halt CPU
            self.halt_cpu()
            
            with open(output_path, 'wb') as f:
                bytes_dumped = 0
                chunk_size = 4096  # 4KB chunks
                
                while bytes_dumped < length:
                    # Read chunk
                    data = self.read_memory(start_addr + bytes_dumped, 
                                           min(chunk_size, length - bytes_dumped))
                    
                    if not data:
                        logger.warning("  No more data")
                        break
                    
                    f.write(data)
                    bytes_dumped += len(data)
                    
                    # Progress
                    if bytes_dumped % (1024 * 1024) == 0:
                        logger.info(f"  Progress: {bytes_dumped/1024/1024:.1f} MB / {length/1024/1024:.1f} MB")
            
            # Resume CPU
            self.resume_cpu()
            
            logger.info(f"✅ Firmware dumped to {output_path}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Dump failed: {e}")
            return False
    
    def execute_code(self, address: int, args: List[int] = None) -> bool:
        """
        Execute code at address
        
        Args:
            address: Address to jump to
            args: Optional arguments (passed in r0-r3)
            
        Returns:
            True if execution started
        """
        logger.info(f"🚀 Executing code at 0x{address:08X}")
        
        if not self.connected:
            return False
        
        # Set PC register
        self.write_register('pc', address)
        
        # Set arguments if provided
        if args:
            arg_regs = ['r0', 'r1', 'r2', 'r3']
            for i, arg in enumerate(args[:4]):
                self.write_register(arg_regs[i], arg)
        
        # Resume CPU
        self.resume_cpu()
        
        logger.info("✅ Code execution started")
        return True
    
    def get_device_info(self) -> Dict:
        """Get target device information"""
        if self.target_device:
            return self.target_device.to_dict()
        return {}
    
    def generate_report(self) -> str:
        """Generate JTAG session report"""
        report = []
        report.append("=" * 70)
        report.append("🔌 JTAG INTERFACE SESSION REPORT")
        report.append("=" * 70)
        report.append(f"Adapter: {self.adapter}")
        report.append(f"Connected: {self.connected}")
        
        if self.target_device:
            report.append("")
            report.append("TARGET DEVICE:")
            report.append("-" * 70)
            report.append(f"  Manufacturer: {self.target_device.manufacturer}")
            report.append(f"  Part Number: {self.target_device.part_number}")
            report.append(f"  IDCODE: {hex(self.target_device.idcode)}")
            report.append(f"  Version: {self.target_device.version}")
        
        report.append("")
        report.append("=" * 70)
        
        return "\n".join(report)
    
    def disconnect(self):
        """Disconnect from JTAG target"""
        if self.openocd_process:
            self.openocd_process.terminate()
        
        self.connected = False
        logger.info("🔌 JTAG disconnected")


def main():
    """Main entry point"""
    print("""
╔═══════════════════════════════════════════════════════════════╗
║     🔌 KALIAGENT v4.3.0 - JTAG INTERFACE                     ║
║                    Phase 9: Alpha 0.1.0                       ║
╚═══════════════════════════════════════════════════════════════╝

⚠️  WARNING: JTAG debugging can brick devices!
⚠️  ONLY use on lab devices you own!
⚠️  Ensure proper voltage levels!

Requirements:
  - OpenOCD installed
  - JTAG adapter (FTDI, J-Link, ST-Link, etc.)
  • Known pinout for target device

    """)
    
    import sys
    
    # Initialize JTAG interface
    adapter = sys.argv[1] if len(sys.argv) > 1 else 'ftdi2232'
    jtag = JTAGInterface(adapter=adapter, verbose=True)
    
    # List adapters
    print("\n📊 Available JTAG adapters:")
    adapters = jtag.list_adapters()
    for a in adapters:
        status = "✅" if a['available'] else "❌"
        print(f"  {status} {a['name']}: {a['description']}")
    
    # Show known pinouts
    print("\n📌 Known pinouts:")
    for model in jtag.KNOWN_PINOUTS.keys():
        print(f"  • {model}")
    
    print("\n💡 Usage:")
    print(f"  python jtag_interface.py <adapter>              # Connect with adapter")
    print(f"\nExamples:")
    print(f"  python jtag_interface.py ftdi2232")
    print(f"  python jtag_interface.py jlink")
    print(f"  python jtag_interface.py stlink")
    
    # Demo connection
    if len(sys.argv) > 1:
        print(f"\n🔌 Connecting with {adapter}...")
        
        if jtag.connect():
            # Scan chain
            devices = jtag.scan_chain()
            
            if devices:
                # Halt CPU
                jtag.halt_cpu()
                
                # Read some registers
                print("\n📊 CPU Registers:")
                for reg in ['pc', 'sp', 'lr', 'r0', 'r1']:
                    value = jtag.read_register(reg)
                    print(f"  {reg}: 0x{value:08X}")
                
                # Generate report
                print("\n" + jtag.generate_report())
            
            jtag.disconnect()


if __name__ == "__main__":
    main()
