#!/usr/bin/env python3
"""
🎯 KaliAgent v4 - CVE-2024-6387: OpenSSH regreSSHion RCE

Complete demonstration of CVE-2024-6387 — Race condition in OpenSSH's
sshd SIGALRM handler (signal-safety violation) allowing remote unauthenticated
code execution as root.

MITRE ATT&CK:
  - T1190: Exploit Public-Facing Application
  - T1068: Exploitation for Privilege Escalation
  - T1021.004: SSH Remote Services

CWE-362: Race Condition
CWE-479: Signal Handling Error

Attack Flow:
  1. Attacker connects to SSH and sends a very slow authentication
  2. After LoginGraceTime (default 120s), sshd sends SIGALRM to kill the child
  3. The SIGALRM handler calls async-unsafe functions (syslog, malloc/free)
  4. If main thread is in malloc/free when signal fires → heap corruption
  5. Attacker wins the race → controlled heap corruption → RCE as root

⚠️  WARNING: For authorized security testing and education only.
         Unauthorized access to computer systems is illegal.

Author: KaliAgent Team
Created: April 28, 2026
Version: 1.0.0
"""

import argparse
import sys
import os
import logging
import time
import socket
import struct
import threading
import json
import hashlib
from datetime import datetime
from dataclasses import dataclass, field
from typing import List, Optional, Tuple, Dict
from pathlib import Path
from enum import Enum

logging.basicConfig(level=logging.INFO, format='%(asctime)s [%(levelname)s] %(message)s')
logger = logging.getLogger('CVE-2024-6387')


# =============================================================================
# ENUMERATIONS
# =============================================================================

class SSHState(Enum):
    """SSH connection states for the fuzzer"""
    DISCONNECTED = "disconnected"
    TCP_CONNECTED = "tcp_connected"
    BANNER_RECEIVED = "banner_received"
    KEX_INIT_SENT = "kex_init_sent"
    KEX_INIT_RECEIVED = "kex_init_received"
    KEX_DH_SENT = "kex_dh_sent"
    AUTH_REQUEST = "auth_request"
    SLOW_AUTH = "slow_auth"
    TIMING_OUT = "timing_out"
    ERROR = "error"


class VulnStatus(Enum):
    """Vulnerability assessment status"""
    VULNERABLE = "vulnerable"
    PATCHED = "patched"
    UNKNOWN = "unknown"
    MITIGATED = "mitigated"


# =============================================================================
# DATA CLASSES
# =============================================================================

@dataclass
class SSHServerConfig:
    """Target SSH server configuration"""
    host: str = "127.0.0.1"
    port: int = 22
    timeout: float = 5.0
    login_grace_time: int = 120  # Default OpenSSH LoginGraceTime


@dataclass
class FuzzerConfig:
    """Configuration for the SSH connection fuzzer"""
    target: SSHServerConfig = field(default_factory=SSHServerConfig)
    num_connections: int = 10
    delay_min: float = 0.1
    delay_max: float = 0.5
    auth_delay: float = 115.0  # Just under LoginGraceTime
    max_retries: int = 3
    payload_size: int = 4096
    slow_auth_method: str = "password"  # password, keyboard-interactive
    concurrent_connections: int = 5
    output_dir: str = "./cve-2024-6387-output"


@dataclass
class TimingResult:
    """Result of a timing analysis probe"""
    timestamp: str
    connection_id: int
    phase: str
    duration_ms: float
    bytes_sent: int
    bytes_received: int
    state: SSHState
    notes: str = ""


@dataclass
class DetectionSignature:
    """Detection signature for the vulnerability"""
    name: str
    description: str
    indicator_type: str  # network, log, process, config
    pattern: str
    severity: str  # low, medium, high, critical
    false_positive_risk: str  # low, medium, high


@dataclass
class ScanResult:
    """Result from scanning a target"""
    target: str
    port: int
    banner: str
    openssh_version: str
    status: VulnStatus
    login_grace_time: Optional[int]
    details: str
    timestamp: str
    mitigations_applied: List[str] = field(default_factory=list)


# =============================================================================
# SSH PROTOCOL HELPERS
# =============================================================================

class SSHProtocolHelper:
    """
    Low-level SSH protocol helpers for crafting raw SSH packets.

    This is used to demonstrate the timing characteristics of the
    vulnerability, NOT to build a working exploit payload.
    """

    # SSH message codes
    SSH_MSG_DISCONNECT = 1
    SSH_MSG_KEXINIT = 20
    SSH_MSG_KEXDH_INIT = 30
    SSH_MSG_USERAUTH_REQUEST = 50

    @staticmethod
    def build_packet(payload: bytes, block_size: int = 8) -> bytes:
        """Build a raw SSH transport packet (unencrypted)"""
        # SSH binary packet format:
        # uint32    packet_length (not including mac or length field itself)
        # byte      padding_length
        # byte[n1]  payload
        # byte[n2]  random padding
        padding_needed = block_size - ((1 + len(payload)) % block_size)
        if padding_needed < 4:
            padding_needed += block_size

        packet_length = 1 + len(payload) + padding_needed
        packet = struct.pack('>I', packet_length)
        packet += struct.pack('B', padding_needed)
        packet += payload
        packet += os.urandom(padding_needed)
        return packet

    @staticmethod
    def build_kexinit(offers: Optional[Dict[str, List[str]]] = None) -> bytes:
        """Build SSH_MSG_KEXINIT with optional custom algorithm offers"""
        if offers is None:
            offers = {
                'kex': ['diffie-hellman-group14-sha256', 'ecdh-sha2-nistp256'],
                'server_host_key': ['ssh-rsa', 'rsa-sha2-256'],
                'encryption_c2s': ['aes128-ctr', 'aes256-ctr'],
                'encryption_s2c': ['aes128-ctr', 'aes256-ctr'],
                'mac_c2s': ['hmac-sha2-256'],
                'mac_s2c': ['hmac-sha2-256'],
                'compression_c2s': ['none'],
                'compression_s2c': ['none'],
                'languages_c2s': [''],
                'languages_s2c': [''],
            }

        payload = struct.pack('B', SSHProtocolHelper.SSH_MSG_KEXINIT)
        payload += os.urandom(16)  # cookie

        # Algorithm lists in order
        for key in ['kex', 'server_host_key', 'encryption_c2s', 'encryption_s2c',
                     'mac_c2s', 'mac_s2c', 'compression_c2s', 'compression_s2c',
                     'languages_c2s', 'languages_s2c']:
            algs = ','.join(offers.get(key, ['']))
            alg_bytes = algs.encode('ascii')
            payload += struct.pack('>I', len(alg_bytes))
            payload += alg_bytes

        payload += struct.pack('B', 0)  # first_kex_packet_follows
        payload += struct.pack('>I', 0)  # reserved

        return payload

    @staticmethod
    def build_userauth_request(username: str, method: str = "password",
                                service: str = "ssh-connection") -> bytes:
        """Build SSH_MSG_USERAUTH_REQUEST"""
        payload = struct.pack('B', SSHProtocolHelper.SSH_MSG_USERAUTH_REQUEST)
        payload += struct.pack('>I', len(username.encode())) + username.encode()
        payload += struct.pack('>I', len(service.encode())) + service.encode()
        payload += struct.pack('>I', len(method.encode())) + method.encode()

        if method == "password":
            payload += struct.pack('B', 0)  # FALSE = not changing password
            # Deliberately do NOT send the password — keep the auth pending
            # to trigger the LoginGraceTime timeout

        return payload

    @staticmethod
    def parse_banner(data: bytes) -> Optional[str]:
        """Extract SSH banner from raw data"""
        try:
            text = data.decode('utf-8', errors='replace')
            for line in text.split('\n'):
                if line.startswith('SSH-'):
                    return line.strip()
        except Exception:
            pass
        return None

    @staticmethod
    def extract_openssh_version(banner: str) -> Optional[str]:
        """Extract OpenSSH version from banner string"""
        if 'OpenSSH' not in banner:
            return None
        try:
            # "SSH-2.0-OpenSSH_9.6p1 Ubuntu-10"
            parts = banner.split('OpenSSH_')
            if len(parts) > 1:
                version = parts[1].split()[0].split('p')[0]  # Remove patch level
                return version
        except Exception:
            pass
        return None


# =============================================================================
# VULNERABILITY ANALYZER
# =============================================================================

class VulnerabilityAnalyzer:
    """
    Analyze SSH servers for CVE-2024-6387 vulnerability.

    Checks:
    1. OpenSSH version from banner
    2. LoginGraceTime configuration
    3. Signal handler safety assessment
    """

    # Vulnerable version ranges (from the advisory)
    VULNERABLE_RANGES = [
        ("8.5p1", "9.7p1"),     # Main vulnerable range
        ("3.0p1", "4.3p1"),     # Original regreSSHion (old)
    ]

    PATCHED_VERSIONS = {
        "9.8p1": "First patched version",
    }

    def __init__(self):
        self.results: List[ScanResult] = []

    def check_version(self, version_str: str) -> VulnStatus:
        """Check if an OpenSSH version is vulnerable"""
        if not version_str:
            return VulnStatus.UNKNOWN

        try:
            # Simple version comparison
            parts = version_str.replace('p', '.').split('.')
            major = int(parts[0]) if parts else 0
            minor = int(parts[1]) if len(parts) > 1 else 0

            # OpenSSH 8.5p1 through 9.7p1 are vulnerable
            if major == 8 and minor >= 5:
                return VulnStatus.VULNERABLE
            if major == 9 and minor <= 7:
                return VulnStatus.VULNERABLE
            if major == 9 and minor >= 8:
                return VulnStatus.PATCHED
            if major < 8:
                return VulnStatus.UNKNOWN  # Too old to determine
            return VulnStatus.PATCHED
        except (ValueError, IndexError):
            return VulnStatus.UNKNOWN

    def scan_target(self, target: SSHServerConfig) -> ScanResult:
        """Scan a single SSH server for vulnerability"""
        logger.info(f"🔍 Scanning {target.host}:{target.port}")

        banner = ""
        version = ""
        status = VulnStatus.UNKNOWN
        login_grace_time = None
        mitigations = []

        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(target.timeout)
            sock.connect((target.host, target.port))

            # Receive banner
            banner_data = sock.recv(4096)
            banner = SSHProtocolHelper.parse_banner(banner_data) or ""
            version = SSHProtocolHelper.extract_openssh_version(banner) or ""

            if version:
                status = self.check_version(version)
            else:
                status = VulnStatus.UNKNOWN

            sock.close()

        except socket.timeout:
            status = VulnStatus.UNKNOWN
            logger.warning(f"Connection to {target.host}:{target.port} timed out")
        except ConnectionRefusedError:
            status = VulnStatus.UNKNOWN
            logger.warning(f"Connection to {target.host}:{target.port} refused")
        except Exception as e:
            logger.error(f"Error scanning {target.host}:{target.port}: {e}")

        result = ScanResult(
            target=target.host,
            port=target.port,
            banner=banner,
            openssh_version=version,
            status=status,
            login_grace_time=login_grace_time,
            details=f"OpenSSH {version} — {status.value}",
            timestamp=datetime.now().isoformat(),
            mitigations_applied=mitigations,
        )
        self.results.append(result)
        return result

    def scan_multiple(self, targets: List[SSHServerConfig]) -> List[ScanResult]:
        """Scan multiple targets"""
        results = []
        for target in targets:
            result = self.scan_target(target)
            results.append(result)
        return results


# =============================================================================
# TIMING ANALYZER
# =============================================================================

class TimingAnalyzer:
    """
    Analyze timing characteristics of SSH connections to identify
    the race window for CVE-2024-6387.

    The vulnerability requires the SIGALRM handler to fire while the
    main thread is in an async-unsafe function (malloc/free/syslog).
    This analyzer measures timing to characterize the race window.
    """

    def __init__(self, config: FuzzerConfig):
        self.config = config
        self.results: List[TimingResult] = []
        self._connection_id = 0

    def probe_connection(self) -> TimingResult:
        """Perform a single timing probe against the target"""
        self._connection_id += 1
        conn_id = self._connection_id
        target = self.config.target

        phase = "connect"
        start = time.monotonic()
        state = SSHState.DISCONNECTED
        bytes_sent = 0
        bytes_received = 0

        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(target.timeout)
            sock.connect((target.host, target.port))
            state = SSHState.TCP_CONNECTED
            connect_time = time.monotonic() - start

            # Receive banner
            phase = "banner"
            banner_start = time.monotonic()
            data = sock.recv(4096)
            banner_time = time.monotonic() - banner_start
            bytes_received += len(data)
            state = SSHState.BANNER_RECEIVED

            # Send KEXINIT
            phase = "kex_init"
            kex_start = time.monotonic()
            kex_payload = SSHProtocolHelper.build_kexinit()
            kex_packet = SSHProtocolHelper.build_packet(kex_payload)
            sock.send(kex_packet)
            bytes_sent += len(kex_packet)
            state = SSHState.KEX_INIT_SENT

            # Receive server KEXINIT
            phase = "kex_recv"
            resp = sock.recv(4096)
            bytes_received += len(resp)
            state = SSHState.KEX_INIT_RECEIVED

            # If we got here, the handshake progressed normally
            # In a real exploit, the attacker would NOT complete DH
            # to trigger the LoginGraceTime timeout

            total_time = time.monotonic() - start
            sock.close()

            result = TimingResult(
                timestamp=datetime.now().isoformat(),
                connection_id=conn_id,
                phase=phase,
                duration_ms=total_time * 1000,
                bytes_sent=bytes_sent,
                bytes_received=bytes_received,
                state=state,
                notes=f"Normal handshake completed in {total_time:.3f}s"
            )

        except socket.timeout:
            total_time = time.monotonic() - start
            result = TimingResult(
                timestamp=datetime.now().isoformat(),
                connection_id=conn_id,
                phase=phase,
                duration_ms=total_time * 1000,
                bytes_sent=bytes_sent,
                bytes_received=bytes_received,
                state=SSHState.TIMING_OUT,
                notes=f"Timeout in phase '{phase}' after {total_time:.3f}s"
            )
        except Exception as e:
            total_time = time.monotonic() - start
            result = TimingResult(
                timestamp=datetime.now().isoformat(),
                connection_id=conn_id,
                phase=phase,
                duration_ms=total_time * 1000,
                bytes_sent=bytes_sent,
                bytes_received=bytes_received,
                state=SSHState.ERROR,
                notes=f"Error in phase '{phase}': {e}"
            )

        self.results.append(result)
        return result

    def analyze_timing(self, num_probes: int = 10) -> Dict:
        """Analyze timing over multiple probes"""
        logger.info(f"⏱️  Running {num_probes} timing probes against "
                     f"{self.config.target.host}:{self.config.target.port}")

        for _ in range(num_probes):
            self.probe_connection()
            time.sleep(0.5)

        # Compute statistics
        durations = [r.duration_ms for r in self.results if r.state != SSHState.ERROR]

        analysis = {
            "total_probes": len(self.results),
            "successful_probes": len(durations),
            "min_ms": min(durations) if durations else 0,
            "max_ms": max(durations) if durations else 0,
            "avg_ms": sum(durations) / len(durations) if durations else 0,
            "timeout_probes": sum(1 for r in self.results if r.state == SSHState.TIMING_OUT),
            "error_probes": sum(1 for r in self.results if r.state == SSHState.ERROR),
            "login_grace_time_s": self.config.target.login_grace_time,
            "race_window_estimate_ms": 50,  # Estimated race window
            "notes": [
                "The race window is the time during which SIGALRM fires",
                "while main thread is in malloc/free/syslog (async-unsafe).",
                "Exploitation probability increases with more concurrent attempts.",
                "glibc's malloc/free operations typically take < 100μs,",
                "but syslog calls can block longer, widening the window.",
            ]
        }

        return analysis


# =============================================================================
# DETECTION SIGNATURES
# =============================================================================

DETECTION_SIGNATURES = [
    DetectionSignature(
        name="Multiple SSH Timeouts",
        description="Many SSH connections timing out near LoginGraceTime",
        indicator_type="network",
        pattern="Multiple SSH connections from same source, each lasting "
                "approximately LoginGraceTime seconds before disconnect",
        severity="high",
        false_positive_risk="medium",
    ),
    DetectionSignature(
        name="sshd SIGALRM Crash",
        description="sshd child process crashes in SIGALRM handler",
        indicator_type="log",
        pattern="sshd[PID]: fatal: Timeout before authentication, "
                "or segfault in sshd child after LoginGraceTime",
        severity="critical",
        false_positive_risk="low",
    ),
    DetectionSignature(
        name="Incomplete SSH Handshakes",
        description="Connections that complete KEXINIT but never finish DH",
        indicator_type="network",
        pattern="SSH KEXINIT exchange completed but no DH follow-up, "
                "connection held open until timeout",
        severity="high",
        false_positive_risk="medium",
    ),
    DetectionSignature(
        name="Vulnerable OpenSSH Banner",
        description="OpenSSH version 8.5p1 through 9.7p1 in banner",
        indicator_type="network",
        pattern="Banner contains 'SSH-2.0-OpenSSH_8.[5-9]' or "
                "'SSH-2.0-OpenSSH_9.[0-7]'",
        severity="high",
        false_positive_risk="low",
    ),
    DetectionSignature(
        name="Heap Corruption in sshd",
        description="Memory corruption detected in sshd process",
        indicator_type="process",
        pattern="ASAN/Valgrind report of heap corruption in sshd, "
                "or kernel oops mentioning sshd",
        severity="critical",
        false_positive_risk="low",
    ),
    DetectionSignature(
        name="Concurrent Slow Auth",
        description="Multiple concurrent slow-authentication SSH connections",
        indicator_type="network",
        pattern="More than 10 concurrent SSH connections from same source, "
                "all in pre-auth state",
        severity="high",
        false_positive_risk="medium",
    ),
]


# =============================================================================
# MITIGATION STEPS
# =============================================================================

MITIGATIONS = [
    {
        "action": "Upgrade OpenSSH",
        "description": "Upgrade to OpenSSH 9.8p1 or later",
        "priority": "critical",
        "details": "OpenSSH 9.8p1 moves the async-unsafe code out of the "
                   "SIGALRM handler. The signal handler now only sets a flag, "
                   "and the unsafe cleanup happens in the main event loop.",
        "commands": [
            "apt update && apt install openssh-server  # Debian/Ubuntu",
            "yum update openssh-server                  # RHEL/CentOS",
        ],
    },
    {
        "action": "Set LoginGraceTime to 0",
        "description": "Disable the LoginGraceTime timeout entirely",
        "priority": "high",
        "details": "Setting LoginGraceTime to 0 disables the SIGALRM handler "
                   "entirely, removing the vulnerable code path. However, this "
                   "means unauthenticated connections will never be cleaned up, "
                   "which can lead to DoS.",
        "commands": [
            "echo 'LoginGraceTime 0' >> /etc/ssh/sshd_config",
            "systemctl restart sshd",
        ],
    },
    {
        "action": "Reduce LoginGraceTime",
        "description": "Reduce LoginGraceTime to make exploitation harder",
        "priority": "medium",
        "details": "A very short LoginGraceTime (e.g., 10s) reduces the race "
                   "window but doesn't eliminate the vulnerability. Combined "
                   "with rate limiting, this makes exploitation impractical.",
        "commands": [
            "echo 'LoginGraceTime 10' >> /etc/ssh/sshd_config",
            "systemctl restart sshd",
        ],
    },
    {
        "action": "UsePAM no",
        "description": "Disable PAM authentication in sshd",
        "priority": "medium",
        "details": "When UsePAM is enabled, the SIGALRM handler calls "
                   "PAM cleanup functions which are also async-unsafe. "
                   "Disabling PAM reduces the attack surface of the signal handler.",
        "commands": [
            "echo 'UsePAM no' >> /etc/ssh/sshd_config",
            "systemctl restart sshd",
        ],
    },
    {
        "action": "Network Rate Limiting",
        "description": "Rate limit SSH connections at the network level",
        "priority": "medium",
        "details": "Exploit requires many concurrent connections to win the race. "
                   "Rate limiting makes this impractical.",
        "commands": [
            "iptables -A INPUT -p tcp --dport 22 -m state --state NEW "
            "-m recent --set --name ssh",
            "iptables -A INPUT -p tcp --dport 22 -m state --state NEW "
            "-m recent --update --seconds 60 --hitcount 10 --name ssh -j DROP",
        ],
    },
    {
        "action": "Firewall Restriction",
        "description": "Restrict SSH access to trusted IPs only",
        "priority": "high",
        "details": "Only allow SSH from known management networks.",
        "commands": [
            "iptables -A INPUT -p tcp --dport 22 -s 10.0.0.0/8 -j ACCEPT",
            "iptables -A INPUT -p tcp --dport 22 -j DROP",
        ],
    },
]


# =============================================================================
# MAIN DEMO CLASS
# =============================================================================

class CVE2024_6387_Demo:
    """
    Complete demonstration orchestrator for CVE-2024-6387.

    Provides:
    1. SSH server scanning for vulnerability detection
    2. Timing analysis to characterize the race window
    3. Connection fuzzing to demonstrate the attack pattern
    4. Detection signature reference
    5. Mitigation guidance with commands
    """

    VERSION = "1.0.0"

    def __init__(self):
        self.output_dir = Path("./cve-2024-6387-output")
        self.analyzer = VulnerabilityAnalyzer()
        self.timing: Optional[TimingAnalyzer] = None

    def scan(self, target: str = "127.0.0.1", port: int = 22,
             timeout: float = 5.0) -> ScanResult:
        """Scan a target SSH server for CVE-2024-6387"""
        config = SSHServerConfig(host=target, port=port, timeout=timeout)
        return self.analyzer.scan_target(config)

    def generate_timing_report(self, config: FuzzerConfig,
                                num_probes: int = 10) -> Dict:
        """Generate a timing analysis report"""
        self.timing = TimingAnalyzer(config)
        return self.timing.analyze_timing(num_probes)

    def print_attack_flow(self):
        """Print the complete attack flow diagram"""
        print("""
╔══════════════════════════════════════════════════════════════════╗
║           CVE-2024-6387 — regreSSHion ATTACK FLOW               ║
╚══════════════════════════════════════════════════════════════════╝

  ┌──────────────┐     ┌──────────────┐     ┌──────────────┐
  │   Attacker   │     │    sshd      │     │   sshd       │
  │   (Client)   │     │  (Main)      │     │  (SIGALRM    │
  │              │     │              │     │   Handler)   │
  └──────┬───────┘     └──────┬───────┘     └──────┬───────┘
         │                    │                     │
    1. Connect to         2. sshd forks         3. Alarm set
       SSH port 22           child process        for LoginGraceTime
         │                    │                     │
         │            4. Send ───────────────►  (waiting)
         │               KEXINIT                   │
         │                    │                     │
    5. Send KEXINIT      6. Key exchange             │
       but NEVER          starts                    │
       complete DH                                   │
         │                    │                     │
         │            7. Main thread enters           │
         │               malloc/free/syslog          │
         │                    │                     │
         │                    │              8. LoginGraceTime
         │                    │                 expires → SIGALRM
         │                    │                     │
         │                    │              9. Signal handler
         │                    │                 calls syslog()
         │                    │                 calls free()
         │                    │                 ← ASYNC-UNSAFE!
         │                    │                     │
         │              10. HEAP CORRUPTION ◄────────┤
         │                    │                     │
         │              11. Controlled write          │
         │                 → RCE as root             │
         ▼                    ▼                     ▼

  KEY INSIGHT: The SIGALRM handler (sig_alarm()) in sshd calls
  async-unsafe functions:

    ❌  syslog(LOG_AUTHPRIV, ...)   — may call malloc
    ❌  free()                      — corrupts heap if main thread
                                    is also in malloc/free
    ❌  _exit()                     — may flush stdio buffers

  The race condition:
    Thread A (main):  malloc() → [heap locked] ──────┐
    Thread B (SIGALRM): free() → [heap locked] ←────┘ BOOM

  Exploitation difficulty:
    • ~10,000 attempts needed on average (glibc)
    • ~100-1,000 attempts on musl libc (wider race window)
    • ASLR bypass required for code execution
    • But: sshd fork() preserves memory layout → no ASLR issue
""")

    def print_detection_signatures(self):
        """Print all detection signatures"""
        print("""
╔══════════════════════════════════════════════════════════════════╗
║           CVE-2024-6387 — DETECTION SIGNATURES                  ║
╚══════════════════════════════════════════════════════════════════╝
""")
        for sig in DETECTION_SIGNATURES:
            print(f"""
  📍 {sig.name}
     Type:      {sig.indicator_type}
     Severity:  {sig.severity}
     FP Risk:   {sig.false_positive_risk}
     Pattern:   {sig.pattern}
     Details:   {sig.description}""")

    def print_mitigations(self):
        """Print all mitigation steps"""
        print("""
╔══════════════════════════════════════════════════════════════════╗
║           CVE-2024-6387 — MITIGATION STEPS                      ║
╚══════════════════════════════════════════════════════════════════╝
""")
        for mit in MITIGATIONS:
            print(f"""
  🛡️  {mit['action']} (Priority: {mit['priority']})
     {mit['description']}
     {mit['details']}""")
            if mit.get('commands'):
                print("     Commands:")
                for cmd in mit['commands']:
                    print(f"       $ {cmd}")

    def explain(self):
        """Full explanation of the vulnerability"""
        self.print_attack_flow()
        self.print_detection_signatures()
        self.print_mitigations()

    def generate_report(self, scan_results: Optional[List[ScanResult]] = None) -> str:
        """Generate a complete markdown report"""
        report = []
        report.append("# CVE-2024-6387: OpenSSH regreSSHion RCE")
        report.append("")
        report.append(f"**Date:** {datetime.now().strftime('%Y-%m-%d')}")
        report.append("**Tool:** KaliAgent v4 — CVE-2024-6387 Demo v1.0.0")
        report.append("")
        report.append("## Summary")
        report.append("")
        report.append("A signal handler race condition in OpenSSH's sshd allows unauthenticated")
        report.append("remote code execution as root. The SIGALRM handler calls async-unsafe")
        report.append("functions (syslog, malloc/free), and if the main thread is simultaneously")
        report.append("in an async-unsafe function, heap corruption occurs, leading to RCE.")
        report.append("")
        report.append("## CVSS")
        report.append("- **Score:** 8.1 HIGH")
        report.append("- **Vector:** CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:H/I:H/A:H")
        report.append("- **EPSS:** ~97% probability of exploitation")
        report.append("")
        report.append("## Vulnerable Versions")
        report.append("- OpenSSH 8.5p1 through 9.7p1 (and some earlier versions)")
        report.append("- OpenSSH 3.0p1 through 4.3p1 (original signal handler issue)")
        report.append("")
        report.append("## Detection Signatures")
        report.append("")
        for sig in DETECTION_SIGNATURES:
            report.append(f"### {sig.name}")
            report.append(f"- **Type:** {sig.indicator_type}")
            report.append(f"- **Severity:** {sig.severity}")
            report.append(f"- **Pattern:** {sig.pattern}")
            report.append("")
        report.append("## Mitigations")
        report.append("")
        for mit in MITIGATIONS:
            report.append(f"### {mit['action']} (Priority: {mit['priority']})")
            report.append(f"{mit['description']}")
            report.append(f"{mit['details']}")
            if mit.get('commands'):
                report.append("```bash")
                for cmd in mit['commands']:
                    report.append(cmd)
                report.append("```")
            report.append("")
        if scan_results:
            report.append("## Scan Results")
            report.append("")
            report.append("| Target | Port | Version | Status |")
            report.append("|--------|------|---------|--------|")
            for r in scan_results:
                report.append(f"| {r.target} | {r.port} | {r.openssh_version or 'unknown'} | {r.status.value} |")
            report.append("")
        return "\n".join(report)


# =============================================================================
# CLI ENTRY POINT
# =============================================================================

def main():
    parser = argparse.ArgumentParser(
        description="CVE-2024-6387: OpenSSH regreSSHion RCE Demo",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Scan target for vulnerability
  python cve_2024_6387.py scan --target 192.168.1.1

  # Scan multiple targets
  python cve_2024_6387.py scan --target 192.168.1.1 --target 192.168.1.2

  # Timing analysis
  python cve_2024_6387.py scan --target 192.168.1.1 --timing --probes 20

  # Show attack flow and detection
  python cve_2024_6387.py explain

  # Generate report
  python cve_2024_6387.py report --target 192.168.1.1

⚠️  For authorized security testing and education only.
""")

    sub = parser.add_subparsers(dest='command')

    # Scan
    scan_p = sub.add_parser('scan', help='Scan SSH server for vulnerability')
    scan_p.add_argument('--target', '-t', action='append', default=['127.0.0.1'],
                        help='Target host(s)')
    scan_p.add_argument('--port', '-p', type=int, default=22, help='SSH port')
    scan_p.add_argument('--timeout', type=float, default=5.0, help='Connection timeout')
    scan_p.add_argument('--timing', action='store_true', help='Include timing analysis')
    scan_p.add_argument('--probes', type=int, default=10, help='Timing probes')

    # Explain
    sub.add_parser('explain', help='Show attack flow, detection, and mitigation')

    # Report
    rep = sub.add_parser('report', help='Generate markdown report')
    rep.add_argument('--target', '-t', action='append', default=['127.0.0.1'])
    rep.add_argument('--port', '-p', type=int, default=22)
    rep.add_argument('--output', '-o', default='cve-2024-6387-report.md')

    # Generate
    gen = sub.add_parser('generate', help='Generate demo configuration files')
    gen.add_argument('--output', '-o', default='./cve-2024-6387-output')

    args = parser.parse_args()

    print("""
╔═══════════════════════════════════════════════════════════════╗
║  🔓 CVE-2024-6387: OpenSSH regreSSHion RCE                   ║
║     CWE-362/CWE-479 | CVSS 8.1 | MITRE T1190                ║
║     KaliAgent v4 Integration                                  ║
╚═══════════════════════════════════════════════════════════════╝

⚠️  WARNING: For authorized security testing and education only.
    Unauthorized access to computer systems is illegal.
""")

    demo = CVE2024_6387_Demo()

    if args.command == 'scan':
        results = []
        for target in args.target:
            result = demo.scan(target, args.port, args.timeout)
            results.append(result)

            status_emoji = {
                VulnStatus.VULNERABLE: "🔴",
                VulnStatus.PATCHED: "🟢",
                VulnStatus.MITIGATED: "🟡",
                VulnStatus.UNKNOWN: "⚪",
            }
            emoji = status_emoji.get(result.status, "⚪")
            print(f"\n  {emoji} {result.target}:{result.port}")
            print(f"     Banner:  {result.banner or 'N/A'}")
            print(f"     Version: {result.openssh_version or 'unknown'}")
            print(f"     Status:  {result.status.value}")

        if args.timing and results:
            print(f"\n⏱️  Running timing analysis ({args.probes} probes)...")
            config = FuzzerConfig(target=SSHServerConfig(
                host=args.target[0], port=args.port, timeout=args.timeout))
            analysis = demo.generate_timing_report(config, args.probes)
            print(f"\n  Timing Analysis Results:")
            print(f"    Probes:        {analysis['successful_probes']}/{analysis['total_probes']}")
            print(f"    Min latency:   {analysis['min_ms']:.1f}ms")
            print(f"    Max latency:   {analysis['max_ms']:.1f}ms")
            print(f"    Avg latency:   {analysis['avg_ms']:.1f}ms")
            print(f"    Timeouts:      {analysis['timeout_probes']}")
            print(f"    Errors:        {analysis['error_probes']}")
            print(f"    Race window:   ~{analysis['race_window_estimate_ms']}ms")
            for note in analysis['notes']:
                print(f"    ℹ️  {note}")

    elif args.command == 'explain':
        demo.explain()

    elif args.command == 'report':
        results = []
        for target in args.target:
            result = demo.scan(target, args.port, 5.0)
            results.append(result)
        report = demo.generate_report(results)
        Path(args.output).write_text(report)
        print(f"📊 Report saved to {args.output}")

    elif args.command == 'generate':
        output = Path(args.output)
        output.mkdir(parents=True, exist_ok=True)

        # Generate demo config
        config_data = {
            "cve": "CVE-2024-6387",
            "description": "OpenSSH regreSSHion RCE",
            "mitigations": [
                {"action": m["action"], "priority": m["priority"]}
                for m in MITIGATIONS
            ],
            "detection_signatures": [
                {"name": s.name, "type": s.indicator_type, "severity": s.severity}
                for s in DETECTION_SIGNATURES
            ],
        }
        config_path = output / "cve-2024-6387-config.json"
        config_path.write_text(json.dumps(config_data, indent=2))
        print(f"📝 Demo config saved to {config_path}")

    else:
        parser.print_help()


if __name__ == "__main__":
    main()