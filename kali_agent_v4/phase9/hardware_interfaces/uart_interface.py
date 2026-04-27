#!/usr/bin/env python3
"""
🔌 KaliAgent v4.3.0 - Phase 9: IoT Exploitation
UART (Serial) Interface Module

Hardware debugging via UART serial console:
- Serial port detection
- Baud rate auto-detection
- Console access
- Command injection
- Credential extraction
- Firmware dump via serial

Author: KaliAgent Team
Started: April 27, 2026
Status: Alpha (0.1.0)
"""

import logging
import serial
import serial.tools.list_ports
import time
import re
import json
from typing import List, Dict, Optional, Tuple
from datetime import datetime
from dataclasses import dataclass, field
import threading

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('UARTInterface')


@dataclass
class SerialPort:
    """Represents a serial port"""
    device: str
    description: str
    hwid: str
    is_usb: bool = False
    manufacturer: str = ""
    product: str = ""
    
    def to_dict(self) -> Dict:
        return {
            'device': self.device,
            'description': self.description,
            'hwid': self.hwid,
            'is_usb': self.is_usb,
            'manufacturer': self.manufacturer,
            'product': self.product
        }


@dataclass
class UARTConfig:
    """UART configuration"""
    port: str
    baudrate: int = 115200
    bytesize: int = serial.EIGHTBITS
    parity: str = serial.PARITY_NONE
    stopbits: int = serial.STOPBITS_ONE
    timeout: float = 1.0
    rtscts: bool = False
    dsrdtr: bool = False
    xonxoff: bool = False
    
    def to_dict(self) -> Dict:
        return {
            'port': self.port,
            'baudrate': self.baudrate,
            'bytesize': self.bytesize,
            'parity': self.parity,
            'stopbits': self.stopbits,
            'timeout': self.timeout
        }


@dataclass
class UARTSession:
    """UART session information"""
    config: UARTConfig
    connected: bool = False
    console_detected: bool = False
    shell_type: str = ""
    credentials_found: List[Dict] = field(default_factory=list)
    commands_executed: List[str] = field(default_factory=list)
    output_buffer: str = ""
    
    def to_dict(self) -> Dict:
        return {
            'config': self.config.to_dict(),
            'connected': self.connected,
            'console_detected': self.console_detected,
            'shell_type': self.shell_type,
            'credentials_count': len(self.credentials_found),
            'commands_executed': len(self.commands_executed)
        }


class UARTInterface:
    """
    UART Serial Interface for Hardware Debugging
    
    Capabilities:
    - Serial port enumeration
    - Baud rate auto-detection
    - Console detection
    - Interactive shell access
    - Command execution
    - Credential extraction
    - Firmware dump via serial
    """
    
    VERSION = "0.1.0"
    
    # Common baud rates
    COMMON_BAUDRATES = [
        9600, 19200, 38400, 57600, 115200, 
        230400, 460800, 921600, 1000000
    ]
    
    # Console prompts
    CONSOLE_PROMPTS = [
        r'#\s*$',                    # Root shell
        r'\$\s*$',                   # User shell
        r'>\s*$',                    # Secondary prompt
        r'login:\s*$',               # Login prompt
        r'password:\s*$',            # Password prompt
        r'Username:\s*$',            # Username prompt
        r'Password:\s*$',            # Password prompt
        r'U-Boot>',                  # U-Boot bootloader
        r'CFE>',                     # CFE bootloader
        r'RedBoot>',                 # RedBoot bootloader
        r'uboot>',                   # U-Boot (lowercase)
        r'Please press Enter to activate this console',  # Linux serial console
        r'Press \[Enter\] to boot',  # Boot prompt
    ]
    
    # Common boot commands
    BOOT_COMMANDS = [
        'printenv',                 # U-Boot: show environment
        'print',                    # CFE: show environment
        'help',                     # Show help
        '?',                        # Show help (short)
        'version',                  # Show version
        'bdinfo',                   # Board info
        'reset',                    # Reset device
        'boot',                     # Boot system
        'bootm',                    # Boot memory
        'bootz',                    # Boot zImage
        'go',                       # Go to address
    ]
    
    # Shell commands for credential extraction
    CRED_EXTRACTION_COMMANDS = [
        'cat /etc/passwd',
        'cat /etc/shadow',
        'cat /etc/config/system',
        'cat /etc/config/wireless',
        'cat /etc/shadow',
        'grep -r "password" /etc/',
        'grep -r "passwd" /etc/',
        'grep -r "secret" /etc/',
        'grep -r "key" /etc/config/',
        'cat /proc/cmdline',
        'env',
        'printenv',
        'set',
    ]
    
    def __init__(self, verbose: bool = True):
        """
        Initialize UART Interface
        
        Args:
            verbose: Enable verbose logging
        """
        self.verbose = verbose
        if verbose:
            logger.setLevel(logging.DEBUG)
        
        self.serial_conn = None
        self.session = None
        self.read_thread = None
        self.running = False
        
        logger.info(f"🔌 UART Interface v{self.VERSION}")
    
    def list_ports(self) -> List[SerialPort]:
        """
        List available serial ports
        
        Returns:
            List of available serial ports
        """
        logger.info("🔍 Scanning for serial ports...")
        
        ports = []
        
        try:
            port_list = serial.tools.list_ports.comports()
            
            for port in port_list:
                serial_port = SerialPort(
                    device=port.device,
                    description=port.description,
                    hwid=port.hwid,
                    is_usb='USB' in port.description or 'FTDI' in port.hwid,
                    manufacturer=port.manufacturer or "",
                    product=port.product or ""
                )
                
                ports.append(serial_port)
                logger.debug(f"  Found: {port.device} - {port.description}")
            
            logger.info(f"✅ Found {len(ports)} serial ports")
            
        except Exception as e:
            logger.error(f"❌ Error scanning ports: {e}")
        
        return ports
    
    def connect(self, port: str, baudrate: int = 115200,
                timeout: float = 1.0) -> bool:
        """
        Connect to serial port
        
        Args:
            port: Serial port device
            baudrate: Baud rate
            timeout: Read timeout in seconds
            
        Returns:
            True if connection successful
        """
        logger.info(f"🔌 Connecting to {port} at {baudrate} baud...")
        
        try:
            self.serial_conn = serial.Serial(
                port=port,
                baudrate=baudrate,
                bytesize=serial.EIGHTBITS,
                parity=serial.PARITY_NONE,
                stopbits=serial.STOPBITS_ONE,
                timeout=timeout,
                rtscts=False,
                dsrdtr=False,
                xonxoff=False
            )
            
            # Reset DTR/RTS lines
            self.serial_conn.dtr = True
            self.serial_conn.rts = True
            time.sleep(0.1)
            self.serial_conn.dtr = False
            self.serial_conn.rts = False
            
            self.session = UARTSession(
                config=UARTConfig(
                    port=port,
                    baudrate=baudrate,
                    timeout=timeout
                ),
                connected=True
            )
            
            logger.info(f"✅ Connected to {port}")
            return True
            
        except serial.SerialException as e:
            logger.error(f"❌ Connection failed: {e}")
            return False
        except Exception as e:
            logger.error(f"❌ Unexpected error: {e}")
            return False
    
    def disconnect(self):
        """Disconnect from serial port"""
        if self.serial_conn and self.serial_conn.is_open:
            self.serial_conn.close()
            logger.info("🔌 Disconnected")
        
        self.session = None
        self.serial_conn = None
    
    def auto_detect_baudrate(self, port: str, timeout: float = 2.0) -> int:
        """
        Auto-detect baud rate
        
        Args:
            port: Serial port device
            timeout: Timeout per baud rate test
            
        Returns:
            Detected baud rate or 0 if not found
        """
        logger.info("🔍 Auto-detecting baud rate...")
        
        for baudrate in self.COMMON_BAUDRATES:
            logger.debug(f"  Trying {baudrate} baud...")
            
            try:
                conn = serial.Serial(
                    port=port,
                    baudrate=baudrate,
                    timeout=timeout
                )
                
                # Send Enter to trigger prompt
                conn.write(b'\n')
                time.sleep(0.5)
                
                # Read response
                response = conn.read(conn.in_waiting or 1024)
                conn.close()
                
                # Check for readable text
                try:
                    text = response.decode('utf-8', errors='ignore')
                    
                    # Look for console prompts or readable characters
                    if any(re.search(prompt, text, re.MULTILINE) 
                           for prompt in self.CONSOLE_PROMPTS):
                        logger.info(f"✅ Detected baud rate: {baudrate}")
                        return baudrate
                    
                    # Check for high ratio of printable characters
                    printable = sum(c.isprintable() or c.isspace() 
                                   for c in text)
                    if len(text) > 10 and printable / len(text) > 0.8:
                        logger.info(f"✅ Likely baud rate: {baudrate}")
                        return baudrate
                        
                except:
                    pass
                    
            except Exception as e:
                logger.debug(f"  Failed at {baudrate}: {e}")
        
        logger.warning("⚠️  Could not auto-detect baud rate")
        return 0
    
    def detect_console(self, timeout: float = 5.0) -> bool:
        """
        Detect if console is available
        
        Args:
            timeout: How long to wait for console
            
        Returns:
            True if console detected
        """
        logger.info("🔍 Detecting console...")
        
        if not self.serial_conn or not self.serial_conn.is_open:
            return False
        
        # Send Enter keys to trigger prompt
        for _ in range(3):
            self.serial_conn.write(b'\n')
            time.sleep(0.5)
        
        # Read response
        time.sleep(1)
        response = self.read_all(timeout=timeout)
        
        if not response:
            logger.warning("⚠️  No response from device")
            return False
        
        logger.debug(f"  Response: {response[:200]}")
        
        # Check for console prompts
        for prompt in self.CONSOLE_PROMPTS:
            if re.search(prompt, response, re.MULTILINE):
                logger.info(f"✅ Console detected (pattern: {prompt})")
                self.session.console_detected = True
                
                # Determine shell type
                if 'U-Boot' in response:
                    self.session.shell_type = 'u-boot'
                elif 'CFE' in response:
                    self.session.shell_type = 'cfe'
                elif 'RedBoot' in response:
                    self.session.shell_type = 'redboot'
                elif '#' in response:
                    self.session.shell_type = 'root-shell'
                elif '$' in response:
                    self.session.shell_type = 'user-shell'
                else:
                    self.session.shell_type = 'unknown'
                
                logger.info(f"📊 Shell type: {self.session.shell_type}")
                return True
        
        logger.warning("⚠️  Console not detected (may need button press)")
        return False
    
    def read_all(self, timeout: float = 1.0) -> str:
        """
        Read all available data
        
        Args:
            timeout: Read timeout
            
        Returns:
            Read data as string
        """
        if not self.serial_conn or not self.serial_conn.is_open:
            return ""
        
        start_time = time.time()
        data = b''
        
        while time.time() - start_time < timeout:
            if self.serial_conn.in_waiting:
                data += self.serial_conn.read(self.serial_conn.in_waiting)
                start_time = time.time()  # Reset timeout on data
            else:
                time.sleep(0.1)
        
        try:
            return data.decode('utf-8', errors='ignore')
        except:
            return data.decode('latin-1', errors='ignore')
    
    def write(self, data: str):
        """
        Write data to serial
        
        Args:
            data: Data to write
        """
        if not self.serial_conn or not self.serial_conn.is_open:
            return
        
        self.serial_conn.write(data.encode('utf-8', errors='ignore'))
        logger.debug(f"  TX: {data[:50]}")
    
    def write_line(self, command: str):
        """
        Write command with newline
        
        Args:
            command: Command to execute
        """
        self.write(command + '\n')
        time.sleep(0.5)
    
    def execute_command(self, command: str, timeout: float = 2.0) -> str:
        """
        Execute command on serial console
        
        Args:
            command: Command to execute
            timeout: Response timeout
            
        Returns:
            Command output
        """
        logger.debug(f"⚡ Executing: {command}")
        
        if not self.serial_conn or not self.serial_conn.is_open:
            return ""
        
        # Send command
        self.write_line(command)
        
        # Read response
        response = self.read_all(timeout=timeout)
        
        if self.session:
            self.session.commands_executed.append(command)
        
        return response
    
    def extract_credentials(self) -> List[Dict]:
        """
        Extract credentials from device via UART
        
        Returns:
            List of discovered credentials
        """
        logger.info("🔑 Extracting credentials via UART...")
        
        credentials = []
        
        if not self.session or not self.session.console_detected:
            logger.error("❌ No console detected")
            return credentials
        
        for command in self.CRED_EXTRACTION_COMMANDS:
            logger.debug(f"  Running: {command}")
            
            output = self.execute_command(command, timeout=3.0)
            
            if output:
                # Parse credentials from output
                found = self._parse_credentials(output, command)
                credentials.extend(found)
                
                if found:
                    logger.warning(f"  🔑 Found {len(found)} credentials from {command}")
        
        if self.session:
            self.session.credentials_found = credentials
        
        logger.info(f"✅ Extracted {len(credentials)} credentials")
        return credentials
    
    def _parse_credentials(self, output: str, source: str) -> List[Dict]:
        """Parse credentials from command output"""
        credentials = []
        
        # Password patterns
        patterns = [
            (r'password[=:\s]+([^\s]+)', 'password'),
            (r'passwd[=:\s]+([^\s]+)', 'password'),
            (r'secret[=:\s]+([^\s]+)', 'secret'),
            (r'key[=:\s]+([^\s]+)', 'key'),
            (r'wpa_psk[=:\s]+([^\s]+)', 'wifi_password'),
            (r'wpa_passphrase[=:\s]+([^\s]+)', 'wifi_password'),
        ]
        
        for pattern, cred_type in patterns:
            matches = re.findall(pattern, output, re.IGNORECASE)
            
            for match in matches:
                # Skip placeholders
                if match.lower() in ['xxxx', '****', 'changeme']:
                    continue
                
                credentials.append({
                    'type': cred_type,
                    'value': match,
                    'source': source,
                    'timestamp': datetime.now().isoformat()
                })
        
        return credentials
    
    def dump_firmware(self, output_path: str, 
                      start_addr: int = 0x00000000,
                      length: int = 0x00400000) -> bool:
        """
        Dump firmware via serial (slow but works on many devices)
        
        Args:
            output_path: Output file path
            start_addr: Start address
            length: Length to dump
            
        Returns:
            True if dump successful
        """
        logger.info(f"💾 Dumping firmware from 0x{start_addr:08X}...")
        logger.info(f"  Length: {length:,} bytes ({length/1024/1024:.1f} MB)")
        logger.warning("⚠️  This may take a LONG time over serial!")
        
        if not self.session or not self.session.console_detected:
            logger.error("❌ No console detected")
            return False
        
        try:
            with open(output_path, 'wb') as f:
                bytes_dumped = 0
                chunk_size = 256  # Read 256 bytes at a time
                
                # Try different dump methods based on shell type
                if self.session.shell_type == 'u-boot':
                    # U-Boot: use md command
                    addr = start_addr
                    while bytes_dumped < length:
                        # md.b <address> <count>
                        output = self.execute_command(
                            f'md.b 0x{addr:08X} {chunk_size}',
                            timeout=5.0
                        )
                        
                        # Parse hex dump
                        data = self._parse_uboot_md(output)
                        if data:
                            f.write(data)
                            bytes_dumped += len(data)
                            addr += len(data)
                            
                            if bytes_dumped % (1024 * 1024) == 0:
                                logger.info(f"  Progress: {bytes_dumped/1024/1024:.1f} MB / {length/1024/1024:.1f} MB")
                        else:
                            logger.warning("  No more data, stopping")
                            break
                else:
                    # Generic: try xxd or hexdump
                    logger.info("  Trying xxd/hexdump method...")
                    
                    # This is a simplified approach - real implementation
                    # would need to be device-specific
                    output = self.execute_command(
                        f'xxd -p /dev/mtd0',
                        timeout=30.0
                    )
                    
                    if output:
                        # Parse hex output
                        hex_data = output.replace('\n', '').replace(' ', '')
                        data = bytes.fromhex(hex_data)
                        f.write(data)
                        bytes_dumped = len(data)
                        logger.info(f"  Dumped {bytes_dumped} bytes")
            
            logger.info(f"✅ Firmware dumped to {output_path}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Dump failed: {e}")
            return False
    
    def _parse_uboot_md(self, output: str) -> bytes:
        """Parse U-Boot md command output"""
        data = b''
        
        # U-Boot md output format:
        # 00000000: 00 01 02 03 04 05 06 07 08 09 0a 0b 0c 0d 0e 0f ................
        lines = output.split('\n')
        
        for line in lines:
            if ':' in line:
                # Extract hex bytes
                parts = line.split(':')
                if len(parts) >= 2:
                    hex_part = parts[1].split()[0:16]  # Up to 16 bytes
                    try:
                        for byte in hex_part:
                            if len(byte) == 2:
                                data += bytes([int(byte, 16)])
                    except:
                        pass
        
        return data
    
    def interactive_shell(self):
        """Start interactive serial shell"""
        logger.info("🖥️  Starting interactive shell (Ctrl+] to exit)...")
        
        if not self.serial_conn or not self.serial_conn.is_open:
            logger.error("❌ Not connected")
            return
        
        import sys
        import select
        import tty
        import termios
        
        # Save terminal settings
        old_settings = termios.tcgetattr(sys.stdin)
        
        try:
            # Set raw mode
            tty.setcbreak(sys.stdin.fileno())
            
            self.running = True
            
            # Start read thread
            def read_thread():
                while self.running:
                    if self.serial_conn.in_waiting:
                        data = self.serial_conn.read(self.serial_conn.in_waiting)
                        sys.stdout.write(data.decode('utf-8', errors='ignore'))
                        sys.stdout.flush()
                    time.sleep(0.01)
            
            thread = threading.Thread(target=read_thread, daemon=True)
            thread.start()
            
            # Write loop
            while self.running:
                if select.select([sys.stdin], [], [], 0.1)[0]:
                    char = sys.stdin.read(1)
                    
                    # Ctrl+] to exit
                    if char == '\x1d':
                        print("\n🛑 Exiting interactive shell")
                        self.running = False
                        break
                    
                    self.serial_conn.write(char.encode('utf-8'))
        
        except Exception as e:
            logger.error(f"❌ Shell error: {e}")
        
        finally:
            # Restore terminal settings
            termios.tcsetattr(sys.stdin, termios.TCSADRAIN, old_settings)
            self.running = False
    
    def get_session_info(self) -> Dict:
        """Get current session information"""
        if self.session:
            return self.session.to_dict()
        return {'connected': False}
    
    def generate_report(self) -> str:
        """Generate UART session report"""
        report = []
        report.append("=" * 70)
        report.append("🔌 UART INTERFACE SESSION REPORT")
        report.append("=" * 70)
        
        if self.session:
            report.append(f"Port: {self.session.config.port}")
            report.append(f"Baud Rate: {self.session.config.baudrate}")
            report.append(f"Connected: {self.session.connected}")
            report.append(f"Console Detected: {self.session.console_detected}")
            report.append(f"Shell Type: {self.session.shell_type}")
            report.append(f"Commands Executed: {len(self.session.commands_executed)}")
            report.append(f"Credentials Found: {len(self.session.credentials_found)}")
            
            if self.session.credentials_found:
                report.append("")
                report.append("CREDENTIALS:")
                report.append("-" * 70)
                for cred in self.session.credentials_found:
                    report.append(f"  Type: {cred['type']}")
                    report.append(f"  Value: {cred['value'][:40]}")
                    report.append(f"  Source: {cred['source']}")
        else:
            report.append("No active session")
        
        report.append("")
        report.append("=" * 70)
        
        return "\n".join(report)


def main():
    """Main entry point"""
    print("""
╔═══════════════════════════════════════════════════════════════╗
║     🔌 KALIAGENT v4.3.0 - UART INTERFACE                     ║
║                    Phase 9: Alpha 0.1.0                       ║
╚═══════════════════════════════════════════════════════════════╝

⚠️  WARNING: Hardware debugging can brick devices!
⚠️  ONLY use on lab devices you own!
⚠️  Ensure proper voltage levels (3.3V vs 5V)!

    """)
    
    import sys
    
    uart = UARTInterface(verbose=True)
    
    # List available ports
    ports = uart.list_ports()
    
    if not ports:
        print("\n❌ No serial ports found")
        print("Connect a USB-to-TTL adapter and try again")
        sys.exit(1)
    
    print("\n📊 Available serial ports:")
    for i, port in enumerate(ports, 1):
        usb_flag = "🔌 USB" if port.is_usb else ""
        print(f"  {i}. {port.device} - {port.description} {usb_flag}")
    
    # Auto-detect baud rate if port specified
    if len(sys.argv) > 1:
        port_device = sys.argv[1]
        
        print(f"\n🔍 Auto-detecting baud rate on {port_device}...")
        baudrate = uart.auto_detect_baudrate(port_device)
        
        if baudrate:
            print(f"✅ Detected: {baudrate} baud")
            
            # Connect
            if uart.connect(port_device, baudrate):
                print(f"\n🔌 Connected to {port_device}")
                
                # Detect console
                if uart.detect_console():
                    print(f"✅ Console detected: {uart.session.shell_type}")
                    
                    # Extract credentials
                    print("\n🔑 Extracting credentials...")
                    creds = uart.extract_credentials()
                    
                    if creds:
                        print(f"\n📊 Found {len(creds)} credentials:")
                        for cred in creds:
                            print(f"  {cred['type']}: {cred['value'][:40]}")
                    
                    # Generate report
                    print("\n" + uart.generate_report())
                    
                    # Interactive shell option
                    print("\n🖥️  Start interactive shell? (y/n)")
                    if input().lower() == 'y':
                        uart.interactive_shell()
                
                uart.disconnect()
        else:
            print("❌ Could not detect baud rate")
            print("Try specifying manually: python uart_interface.py /dev/ttyUSB0 115200")
    else:
        print("\n💡 Usage:")
        print(f"  python uart_interface.py <port>              # Auto-detect baud")
        print(f"  python uart_interface.py <port> <baudrate>   # Specific baud")
        print(f"\nExample:")
        print(f"  python uart_interface.py /dev/ttyUSB0")
        print(f"  python uart_interface.py /dev/ttyUSB0 115200")


if __name__ == "__main__":
    main()
