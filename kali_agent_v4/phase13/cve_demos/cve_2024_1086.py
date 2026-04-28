#!/usr/bin/env python3
"""
🎯 KaliAgent v4 - CVE-2024-1086: Linux nftables Use-After-Free LPE

Complete demonstration of CVE-2024-1086 — Use-after-free vulnerability
in the Linux kernel's nf_tables subsystem allowing local privilege
escalation to root.

MITRE ATT&CK:
  - T1068: Exploitation for Privilege Escalation
  - T1548.001: Abuse Elevation Control Mechanism: Setuid/Setgid

CWE-416: Use After Free
CWE-787: Out-of-bounds Write (consequence)

Attack Flow:
  1. Attacker creates nftables rules with specially crafted verdicts
  2. nft_verdict_init() accepts positive verdict values → NF_DROP + offset
  3. First NF_DROP frees the nft_chain object
  4. Second NF_DROP attempts double-free → use-after-free
  5. Attacker sprays heap to reclaim freed object
  6. Arbitrary kernel read/write via controlled nft_chain
  7. Overwrite modprobe_path or cred → root shell

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
import json
import subprocess
import struct
from datetime import datetime
from dataclasses import dataclass, field
from typing import List, Optional, Dict, Any
from pathlib import Path
from enum import Enum

logging.basicConfig(level=logging.INFO, format='%(asctime)s [%(levelname)s] %(message)s')
logger = logging.getLogger('CVE-2024-1086')


# =============================================================================
# ENUMERATIONS
# =============================================================================

class KernelStatus(Enum):
    """Kernel vulnerability status"""
    VULNERABLE = "vulnerable"
    PATCHED = "patched"
    UNKNOWN = "unknown"
    MITIGATED = "mitigated"


class NftablesTestResult(Enum):
    """Result of an nftables test"""
    SUCCESS = "success"
    FAILURE = "failure"
    PERMISSION_DENIED = "permission_denied"
    KERNEL_UNSUPPORTED = "kernel_unsupported"
    ERROR = "error"


# =============================================================================
# DATA CLASSES
# =============================================================================

@dataclass
class KernelConfig:
    """Target kernel configuration"""
    version: str = "unknown"
    arch: str = "unknown"
    nftables_available: bool = False
    net_admin_cap: bool = False
    unprivileged_userns: bool = False
    config_path: str = "/boot/config-unknown"


@dataclass
class FuzzerConfig:
    """Configuration for nftables rule fuzzing"""
    max_rules: int = 100
    verdict_range_start: int = 0
    verdict_range_end: int = 0xFFFFFF
    spray_count: int = 4096
    spray_size: int = 256
    target_slab: str = "kmalloc-cg-256"
    output_dir: str = "./cve-2024-1086-output"
    dry_run: bool = True  # Safety: never actually exploit by default


@dataclass
class UAFDetectionResult:
    """Result of a use-after-free detection check"""
    check_name: str
    status: str  # vulnerable, safe, unknown
    details: str
    evidence: str = ""


@dataclass
class PrivEscCheck:
    """Result of a privilege escalation check"""
    uid_start: int
    uid_current: int
    gid_start: int
    gid_current: int
    escalated: bool
    method: str
    details: str


@dataclass
class DetectionSignature:
    """Detection signature for the vulnerability"""
    name: str
    description: str
    indicator_type: str  # kernel, process, syscall, config
    pattern: str
    severity: str
    false_positive_risk: str


# =============================================================================
# KERNEL ANALYSIS
# =============================================================================

class KernelAnalyzer:
    """
    Analyze the local kernel for CVE-2024-1086 vulnerability.

    Checks:
    1. Kernel version
    2. nftables module availability
    3. CONFIG_USER_NS and CAP_NET_ADMIN capabilities
    4. Relevant kernel config options
    """

    # Vulnerable kernel versions (from the advisory)
    VULNERABLE_RANGES = [
        ("5.4.0", "6.7.x"),   # Main vulnerable range
    ]

    PATCHED_SINCE = "6.8"

    def __init__(self):
        self.kernel_config = KernelConfig()
        self._detect_kernel()

    def _detect_kernel(self):
        """Detect kernel version and configuration"""
        # Kernel version
        try:
            uname_result = subprocess.run(
                ['uname', '-r'], capture_output=True, text=True, timeout=5
            )
            self.kernel_config.version = uname_result.stdout.strip()
        except Exception as e:
            logger.error(f"Failed to detect kernel version: {e}")

        # Architecture
        try:
            arch_result = subprocess.run(
                ['uname', '-m'], capture_output=True, text=True, timeout=5
            )
            self.kernel_config.arch = arch_result.stdout.strip()
        except Exception:
            pass

        # Kernel config
        config_path = f"/boot/config-{self.kernel_config.version}"
        if os.path.exists(config_path):
            self.kernel_config.config_path = config_path
            self._parse_kernel_config(config_path)

        # Check nftables availability
        try:
            nft_result = subprocess.run(
                ['nft', '-v'], capture_output=True, text=True, timeout=5
            )
            if nft_result.returncode == 0:
                self.kernel_config.nftables_available = True
        except FileNotFoundError:
            self.kernel_config.nftables_available = False
        except Exception:
            pass

        # Check current capabilities
        try:
            cap_result = subprocess.run(
                ['capsh', '--print'], capture_output=True, text=True, timeout=5
            )
            if 'cap_net_admin' in cap_result.stdout.lower():
                self.kernel_config.net_admin_cap = True
        except FileNotFoundError:
            pass
        except Exception:
            pass

    def _parse_kernel_config(self, config_path: str):
        """Parse kernel config for relevant options"""
        try:
            with open(config_path, 'r') as f:
                for line in f:
                    line = line.strip()
                    if line.startswith('CONFIG_USER_NS='):
                        self.kernel_config.unprivileged_userns = (
                            line.endswith('=y')
                        )
        except Exception as e:
            logger.warning(f"Failed to parse kernel config: {e}")

    def check_vulnerability(self) -> KernelStatus:
        """Check if the kernel is vulnerable"""
        version = self.kernel_config.version
        if not version or version == "unknown":
            return KernelStatus.UNKNOWN

        try:
            # Parse version components
            parts = version.split('.')
            major = int(parts[0])
            minor = int(parts[1].split('-')[0].split('+')[0])

            # Kernel 6.8+ is patched
            if major > 6 or (major == 6 and minor >= 8):
                return KernelStatus.PATCHED

            # Kernel 5.4 through 6.7 is vulnerable (with nftables)
            if major == 5 and minor >= 4:
                return KernelStatus.VULNERABLE
            if major == 6 and minor <= 7:
                return KernelStatus.VULNERABLE

            return KernelStatus.UNKNOWN
        except (ValueError, IndexError):
            return KernelStatus.UNKNOWN

    def get_report(self) -> Dict[str, Any]:
        """Get a complete kernel analysis report"""
        return {
            "kernel_version": self.kernel_config.version,
            "architecture": self.kernel_config.arch,
            "nftables_available": self.kernel_config.nftables_available,
            "net_admin_cap": self.kernel_config.net_admin_cap,
            "unprivileged_userns": self.kernel_config.unprivileged_userns,
            "vulnerability_status": self.check_vulnerability().value,
            "config_path": self.kernel_config.config_path,
        }


# =============================================================================
# NFTABLES FUZZER (Safe Demo)
# =============================================================================

class NftablesFuzzer:
    """
    Demonstrates the nftables rule patterns that trigger CVE-2024-1086.

    This is a SAFE demonstration — it shows the rule structures that
    would trigger the vulnerability but does NOT actually exploit it.
    Use --dry-run=False only on systems you own with explicit permission.

    The vulnerability:
      nft_verdict_init() in net/netfilter/nf_tables_api.c accepts
      positive verdict values. NF_DROP is 0, but a verdict of
      NF_DROP + NFT_RETURN (positive value) causes the chain reference
      to be dropped while the chain is still being used.

      Two NF_DROP verdicts on the same chain:
        1st NF_DROP: decrements chain refcount, may free chain
        2nd NF_DROP: accesses freed chain → UAF → double-free
    """

    def __init__(self, config: FuzzerConfig):
        self.config = config
        self.test_results: List[Dict] = []

    def generate_malicious_rule_set(self) -> str:
        """
        Generate an nftables rule set that demonstrates the vulnerability pattern.

        This creates the rule structure that triggers nft_verdict_init() with
        positive verdict values. In a real exploit, these rules cause the
        use-after-free condition.
        """
        ruleset = """#!/usr/sbin/nft -f
# CVE-2024-1086 Demonstration Rule Set
# ⚠️  This demonstrates the vulnerability pattern — dry-run only

table ip demo_cve_2024_1086 {
    # Chain 1: The chain that will be freed via double NF_DROP
    chain vuln_chain {
        type filter hook input priority 0; policy accept;

        # Rule with NF_DROP verdict — first decrement of chain refcount
        # nft_verdict_init() accepts this positive verdict value
        meta l4proto tcp drop

        # Rule with second NF_DROP — triggers UAF on already-freed chain
        # This is the "double free" condition
        meta l4proto udp drop
    }

    # Chain 2: References vuln_chain (increases refcount)
    chain ref_chain {
        type filter hook forward priority 0; policy accept;

        # Jump to vuln_chain — increments refcount
        meta l4proto tcp jump vuln_chain
    }

    # Chain 3: Verdict manipulation
    chain verdict_chain {
        type filter hook output priority 0; policy accept;

        # Positive verdict value that nft_verdict_init() incorrectly accepts
        # This creates the NF_DROP + offset condition
        meta l4proto icmp counter
    }
}
"""
        return ruleset

    def generate_double_free_pattern(self) -> str:
        """
        Generate the specific double-free trigger pattern.

        The exploit uses:
        1. Create chain A with a verdict referencing chain B
        2. Delete chain A → first NF_DROP frees chain B's object
        3. Delete chain B → second NF_DROP accesses freed memory → UAF
        """
        pattern = """#!/usr/sbin/nft -f
# CVE-2024-1086 Double-Free Trigger Pattern
# ⚠️  Demonstrates the UAF pattern — dry-run only

# Step 1: Create the tables and chains
table ip exploit {
    chain base_chain {
        type filter hook input priority 0; policy accept;
    }

    # This chain's verdict will be manipulated
    chain target_chain {
        counter accept
    }
}

# Step 2: Add rule with verdict pointing to target_chain
# nft add rule ip exploit base_chain ip daddr 10.0.0.1 jump target_chain

# Step 3: Trigger double NF_DROP
# When the rule is deleted, nft_verdict_init() processes the verdict
# The first NF_DROP decrements refcount → free
# The second NF_DROP accesses freed memory → UAF

# In the real exploit:
# delete rule → NF_DROP (1st) → free chain object
# delete chain → NF_DROP (2nd) → access freed object → UAF
# spray heap → reclaim freed slot with controlled data
# → arbitrary kernel R/W → root
"""
        return pattern

    def generate_heap_spray_pattern(self) -> str:
        """
        Generate the heap spray pattern used to reclaim freed objects.

        After the UAF, the attacker sprays the kernel heap to place
        a controlled object in the freed slot.
        """
        pattern = """# CVE-2024-1086 Heap Spray Pattern
# ⚠️  Educational demonstration only

# After UAF is triggered, the freed nft_chain object's memory slot
# needs to be reclaimed with attacker-controlled data.
#
# Common spray targets for kmalloc-cg-256 slab:
#   - setxattr() with controlled value size
#   - userfaultfd() pages
#   - pipe_buffer objects
#   - msg_msg objects
#   - sk_buff data
#
# The spray overwrites the freed nft_chain object's function pointers
# with addresses pointing to the attacker's payload.
#
# Spray technique (setxattr):
#   for i in range(4096):
#       setxattr(f"/tmp/spray_{i}", "user.spray", spray_data, 256, 0)
#
# Spray technique (msg_msg):
#   for i in range(4096):
#       msgsnd(qid, &msg, 256 - 0x30, IPC_NOWAIT)
#
# Once the freed slot is reclaimed:
#   - nft_chain->ops->dump points to attacker-controlled function
#   - Triggering dump → arbitrary code execution in kernel context
#   - Overwrite modprobe_path or task cred → root
"""
        return pattern

    def test_nftables_basic(self) -> NftablesTestResult:
        """Test basic nftables functionality"""
        if not self.config.dry_run:
            logger.warning("Running non-dry-run nftables tests!")

        # Check if nft command exists
        try:
            result = subprocess.run(
                ['nft', '-v'], capture_output=True, text=True, timeout=5
            )
            if result.returncode != 0:
                return NftablesTestResult.KERNEL_UNSUPPORTED
        except FileNotFoundError:
            return NftablesTestResult.KERNEL_UNSUPPORTED
        except Exception:
            return NftablesTestResult.ERROR

        # Check if we can list tables
        try:
            result = subprocess.run(
                ['nft', 'list', 'tables'], capture_output=True, text=True, timeout=5
            )
            if result.returncode == 0:
                return NftablesTestResult.SUCCESS
            elif 'Permission denied' in result.stderr:
                return NftablesTestResult.PERMISSION_DENIED
        except Exception:
            pass

        return NftablesTestResult.ERROR

    def run_safe_check(self) -> List[Dict]:
        """Run safe nftables checks (no exploitation)"""
        results = []

        # Check 1: nftables availability
        r = self.test_nftables_basic()
        results.append({
            "check": "nftables_availability",
            "result": r.value,
            "details": "nft command availability and permissions",
        })

        # Check 2: kernel version
        try:
            uname = subprocess.run(
                ['uname', '-r'], capture_output=True, text=True, timeout=5
            )
            version = uname.stdout.strip()
            analyzer = KernelAnalyzer()
            status = analyzer.check_vulnerability()
            results.append({
                "check": "kernel_vulnerability",
                "result": status.value,
                "details": f"Kernel {version}: {status.value}",
            })
        except Exception as e:
            results.append({
                "check": "kernel_vulnerability",
                "result": "error",
                "details": str(e),
            })

        # Check 3: CAP_NET_ADMIN
        uid = os.getuid()
        results.append({
            "check": "net_admin_capability",
            "result": "has_cap" if uid == 0 else "no_cap",
            "details": f"Current UID: {uid}, need CAP_NET_ADMIN for nftables",
        })

        self.test_results = results
        return results


# =============================================================================
# UAF DETECTOR
# =============================================================================

class UAFDetector:
    """
    Detects the use-after-free condition for CVE-2024-1086.

    Uses multiple techniques:
    1. Kernel version check
    2. nftables module parameter check
    3. Kernel config analysis
    4. Runtime behavior check (safe probing)
    """

    def __init__(self):
        self.results: List[UAFDetectionResult] = []

    def check_kernel_version(self) -> UAFDetectionResult:
        """Check kernel version against known vulnerable ranges"""
        analyzer = KernelAnalyzer()
        status = analyzer.check_vulnerability()
        kc = analyzer.kernel_config

        result = UAFDetectionResult(
            check_name="kernel_version",
            status=status.value,
            details=f"Kernel {kc.version} on {kc.arch}",
            evidence=f"Version range 5.4-6.7 is vulnerable; 6.8+ is patched",
        )
        self.results.append(result)
        return result

    def check_nftables_config(self) -> UAFDetectionResult:
        """Check kernel config for nftables-related options"""
        kc = KernelConfig()
        vulnerable_options = []

        config_path = f"/boot/config-{os.uname().release}"
        if os.path.exists(config_path):
            try:
                with open(config_path, 'r') as f:
                    for line in f:
                        line = line.strip()
                        if line.startswith('CONFIG_NF_TABLES=') and line.endswith('=y'):
                            vulnerable_options.append("CONFIG_NF_TABLES=y (nftables enabled)")
                        if line.startswith('CONFIG_USER_NS=') and line.endswith('=y'):
                            vulnerable_options.append(
                                "CONFIG_USER_NS=y (unprivileged user namespaces)"
                            )
            except Exception:
                pass

        if vulnerable_options:
            status = "vulnerable" if len(vulnerable_options) >= 2 else "unknown"
        else:
            status = "unknown"

        result = UAFDetectionResult(
            check_name="nftables_config",
            status=status,
            details="Kernel config options that affect exploitability",
            evidence="; ".join(vulnerable_options) if vulnerable_options else "Config not readable",
        )
        self.results.append(result)
        return result

    def check_net_admin_restriction(self) -> UAFDetectionResult:
        """Check if unprivileged NET_ADMIN is restricted"""
        # Check sysctl for unprivileged user namespace restrictions
        restricted = False
        try:
            result = subprocess.run(
                ['sysctl', 'kernel.unprivileged_userns_clone'],
                capture_output=True, text=True, timeout=5
            )
            if '0' in result.stdout:
                restricted = True
        except Exception:
            pass

        try:
            result = subprocess.run(
                ['sysctl', 'user.max_user_namespaces'],
                capture_output=True, text=True, timeout=5
            )
            if '0' in result.stdout:
                restricted = True
        except Exception:
            pass

        result = UAFDetectionResult(
            check_name="net_admin_restriction",
            status="safe" if restricted else "vulnerable",
            details="Unprivileged user namespace + NET_ADMIN access",
            evidence="Restricted" if restricted else "Not restricted — unprivileged users can create network namespaces",
        )
        self.results.append(result)
        return result

    def run_all_checks(self) -> List[UAFDetectionResult]:
        """Run all detection checks"""
        self.check_kernel_version()
        self.check_nftables_config()
        self.check_net_admin_restriction()
        return self.results


# =============================================================================
# PRIVILEGE ESCALATION CHECKER
# =============================================================================

class PrivEscChecker:
    """
    Checks current privilege level and demonstrates privilege
    escalation detection (does NOT actually escalate).
    """

    def check_current(self) -> PrivEscCheck:
        """Check current privilege level"""
        uid = os.getuid()
        gid = os.getgid()
        return PrivEscCheck(
            uid_start=uid,
            uid_current=uid,
            gid_start=gid,
            gid_current=gid,
            escalated=(uid == 0),
            method="none" if uid != 0 else "already_root",
            details=f"UID={uid}, GID={gid}",
        )

    def check_capabilities(self) -> List[str]:
        """Check current process capabilities"""
        caps = []
        try:
            result = subprocess.run(
                ['capsh', '--print'], capture_output=True, text=True, timeout=5
            )
            for line in result.stdout.split('\n'):
                if 'Cap' in line:
                    caps.append(line.strip())
        except FileNotFoundError:
            caps.append("capsh not available — install libcap2-bin")
        except Exception as e:
            caps.append(f"Error: {e}")
        return caps


# =============================================================================
# DETECTION SIGNATURES
# =============================================================================

DETECTION_SIGNATURES = [
    DetectionSignature(
        name="Kernel Version 5.4-6.7",
        description="Kernel version in vulnerable range with nftables enabled",
        indicator_type="kernel",
        pattern="Linux kernel 5.4.x through 6.7.x with CONFIG_NF_TABLES=y",
        severity="critical",
        false_positive_risk="low",
    ),
    DetectionSignature(
        name="Double NF_DROP Verdict",
        description="nftables rules with double NF_DROP on same chain",
        indicator_type="kernel",
        pattern="Two NF_DROP verdicts referencing the same nft_chain object, "
                "causing refcount underflow and UAF",
        severity="critical",
        false_positive_risk="low",
    ),
    DetectionSignature(
        name="Unprivileged Net Namespace Creation",
        description="Unprivileged user creating network namespaces",
        indicator_type="syscall",
        pattern="unshare(CLONE_NEWNET) from non-root user, followed by "
                "nftables rule manipulation",
        severity="high",
        false_positive_risk="medium",
    ),
    DetectionSignature(
        name="Kernel Heap Spray Pattern",
        description="Large number of setxattr/msgsnd calls for heap spray",
        indicator_type="process",
        pattern="Process creating thousands of xattrs or message queue messages "
                "of size ~256 bytes (kmalloc-cg-256 slab targeting)",
        severity="high",
        false_positive_risk="medium",
    ),
    DetectionSignature(
        name="nft_chain Refcount Anomaly",
        description="nft_chain object with unexpected refcount",
        indicator_type="kernel",
        pattern="Kernel debug output showing nft_chain refcount going negative "
                "or reaching zero while still referenced",
        severity="critical",
        false_positive_risk="low",
    ),
]


# =============================================================================
# MITIGATION STEPS
# =============================================================================

MITIGATIONS = [
    {
        "action": "Upgrade Kernel",
        "description": "Upgrade to Linux kernel 6.8 or later",
        "priority": "critical",
        "details": "Kernel 6.8 added proper validation in nft_verdict_init() "
                   "to reject positive verdict values that could cause UAF. "
                   "The patch adds a check: if (verdict < 0) reject.",
        "commands": [
            "apt update && apt install linux-image-6.8.0-generic  # Debian/Ubuntu",
            "yum update kernel                                          # RHEL/CentOS",
        ],
    },
    {
        "action": "Disable Unprivileged User Namespaces",
        "description": "Prevent unprivileged users from creating user namespaces",
        "priority": "high",
        "details": "The exploit requires CAP_NET_ADMIN inside a user namespace. "
                   "Disabling unprivileged user namespace creation prevents the "
                   "entire attack chain for non-root users.",
        "commands": [
            "sysctl -w kernel.unprivileged_userns_clone=0",
            "sysctl -w user.max_user_namespaces=0",
            "echo 'kernel.unprivileged_userns_clone=0' >> /etc/sysctl.d/99-security.conf",
        ],
    },
    {
        "action": "Restrict CAP_NET_ADMIN",
        "description": "Restrict CAP_NET_ADMIN capability to trusted users",
        "priority": "high",
        "details": "Even with user namespaces enabled, restricting which users "
                   "can gain CAP_NET_ADMIN prevents the exploit from non-root.",
        "commands": [
            "# Use AppArmor or SELinux to restrict nftables access",
            "aa-disable nftables  # If using AppArmor profile",
        ],
    },
    {
        "action": "Disable nftables Module",
        "description": "Blacklist the nf_tables kernel module if not needed",
        "priority": "medium",
        "details": "If nftables is not required, blacklisting the module "
                   "removes the attack surface entirely.",
        "commands": [
            "echo 'install nf_tables /bin/true' >> /etc/modprobe.d/disable-nftables.conf",
            "modprobe -r nf_tables 2>/dev/null || true",
        ],
    },
    {
        "action": "Monitor nftables Usage",
        "description": "Audit and monitor nftables rule changes",
        "priority": "medium",
        "details": "Use auditd to monitor nftables system calls and detect "
                   "unusual rule manipulation patterns.",
        "commands": [
            "auditctl -a exit,always -F arch=b64 -S __NR_sendmsg -F a0=0 -k nftables",
            "auditctl -a exit,always -F arch=b64 -S __NR_setsockopt -k nftables",
        ],
    },
    {
        "action": "Apply Distribution Patches",
        "description": "Apply distribution-specific backported patches",
        "priority": "critical",
        "details": "Most distributions have backported the fix to their "
                   "supported kernel versions. Check your distro's advisory.",
        "commands": [
            "apt update && apt upgrade  # Debian/Ubuntu",
            "yum update                 # RHEL/CentOS",
            "dnf upgrade                 # Fedora",
        ],
    },
]


# =============================================================================
# MAIN DEMO CLASS
# =============================================================================

class CVE2024_1086_Demo:
    """
    Complete demonstration orchestrator for CVE-2024-1086.

    Provides:
    1. Kernel vulnerability scanning
    2. nftables rule fuzzing (safe demonstration)
    3. Use-after-free detection
    4. Privilege escalation checking
    5. Detection signature reference
    6. Mitigation guidance with commands
    """

    VERSION = "1.0.0"

    def __init__(self):
        self.output_dir = Path("./cve-2024-1086-output")
        self.kernel_analyzer = KernelAnalyzer()
        self.fuzzer: Optional[NftablesFuzzer] = None
        self.uaf_detector = UAFDetector()
        self.privesc_checker = PrivEscChecker()

    def scan(self) -> Dict[str, Any]:
        """Scan the local system for vulnerability"""
        report = self.kernel_analyzer.get_report()
        logger.info(f"🔍 Kernel scan: {report['kernel_version']} → {report['vulnerability_status']}")
        return report

    def run_detection(self) -> List[UAFDetectionResult]:
        """Run UAF detection checks"""
        return self.uaf_detector.run_all_checks()

    def generate_rules(self, output_dir: str = None, pattern: str = "full") -> List[str]:
        """Generate demonstration nftables rule files"""
        out = Path(output_dir or self.output_dir)
        out.mkdir(parents=True, exist_ok=True)

        files = []
        fuzzer = NftablesFuzzer(FuzzerConfig())

        if pattern in ("full", "all"):
            ruleset = fuzzer.generate_malicious_rule_set()
            path = out / "nftables_vuln_pattern.nft"
            path.write_text(ruleset)
            files.append(str(path))
            logger.info(f"📝 Generated: {path}")

        if pattern in ("double_free", "all"):
            pattern_data = fuzzer.generate_double_free_pattern()
            path = out / "double_free_pattern.nft"
            path.write_text(pattern_data)
            files.append(str(path))
            logger.info(f"📝 Generated: {path}")

        if pattern in ("spray", "all"):
            spray = fuzzer.generate_heap_spray_pattern()
            path = out / "heap_spray_pattern.txt"
            path.write_text(spray)
            files.append(str(path))
            logger.info(f"📝 Generated: {path}")

        return files

    def print_attack_flow(self):
        """Print the complete attack flow diagram"""
        print("""
╔══════════════════════════════════════════════════════════════════╗
║           CVE-2024-1086 — nftables UAF ATTACK FLOW               ║
╚══════════════════════════════════════════════════════════════════╝

  ┌──────────────┐     ┌──────────────┐     ┌──────────────┐
  │   Attacker   │     │    Kernel    │     │    Kernel    │
  │  (Userland)  │     │  nftables    │     │  Heap/Slab  │
  └──────┬───────┘     └──────┬───────┘     └──────┬───────┘
         │                    │                     │
    1. unshare(              2. Create nftables   3. nft_chain
       CLONE_NEWNET)         table + chains        object
         │                    │                     │
    3. Add rule with    4. nft_verdict_init()  5. Chain refcount
       verdict pointing     accepts POSITIVE      incremented
       to target_chain      verdict value          │
         │                    │                     │
    6. Delete rule ──────► 7. NF_DROP #1 ──────► 8. refcount-- → 0
                              (first free)          → FREE chain
                                │                     │
    9. Delete chain ──────► 10. NF_DROP #2 ──────► 11. UAF!
                               (second free)         Access freed
                                 │                   chain object
                                 │                     │
    12. Heap spray ──────────────────────────────────► 13. Reclaim
        (setxattr/msg_msg)                             freed slot
        with controlled data                           │
                                 │                     │
    14. Trigger dump ──────► 15. nft_chain->ops  ──► 16. Controlled
        on manipulated         ->dump()                  function
        chain                                            call
                                 │                     │
                           17. Arbitrary kernel ◄──────┘
                              R/W → root

  KEY INSIGHT: nft_verdict_init() does NOT validate that verdict
  values are non-positive. The code assumes verdict < 0 for
  NF_DROP, but accepts NF_DROP + offset (positive value).

  This causes:
    1st NF_DROP: refcount goes to 0 → object freed
    2nd NF_DROP: accesses freed memory → double-free/UAF

  The exploit path:
    UAF → heap spray → control nft_chain object → modprobe_path
    overwrite → trigger unknown binary → root shell

  Requirements:
    • CAP_NET_ADMIN (via user namespace: unshare -n)
    • Kernel 5.4 - 6.7 with CONFIG_NF_TABLES=y
    • CONFIG_USER_NS=y (for unprivileged access)
""")

    def print_detection_signatures(self):
        """Print all detection signatures"""
        print("""
╔══════════════════════════════════════════════════════════════════╗
║           CVE-2024-1086 — DETECTION SIGNATURES                  ║
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
║           CVE-2024-1086 — MITIGATION STEPS                      ║
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

    def generate_report(self, scan_data: Optional[Dict] = None,
                         detection_results: Optional[List] = None) -> str:
        """Generate a complete markdown report"""
        report = []
        report.append("# CVE-2024-1086: Linux nftables Use-After-Free LPE")
        report.append("")
        report.append(f"**Date:** {datetime.now().strftime('%Y-%m-%d')}")
        report.append("**Tool:** KaliAgent v4 — CVE-2024-1086 Demo v1.0.0")
        report.append("")
        report.append("## Summary")
        report.append("")
        report.append("A use-after-free vulnerability in the Linux kernel's nf_tables subsystem")
        report.append("allows local privilege escalation. nft_verdict_init() accepts positive")
        report.append("verdict values, causing double NF_DROP on the same chain object, leading")
        report.append("to a double-free condition that can be exploited for arbitrary kernel")
        report.append("read/write and root privilege escalation.")
        report.append("")
        report.append("## CVSS")
        report.append("- **Score:** 7.8 HIGH")
        report.append("- **Vector:** CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H")
        report.append("- **EPSS:** ~88% probability of exploitation")
        report.append("")
        report.append("## Vulnerable Versions")
        report.append("- Linux kernel 5.4 through 6.7 with CONFIG_NF_TABLES=y")
        report.append("- Requires CAP_NET_ADMIN (obtainable via user namespaces)")
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
        if scan_data:
            report.append("## Scan Results")
            report.append("")
            for key, val in scan_data.items():
                report.append(f"- **{key}:** {val}")
            report.append("")
        return "\n".join(report)


# =============================================================================
# CLI ENTRY POINT
# =============================================================================

def main():
    parser = argparse.ArgumentParser(
        description="CVE-2024-1086: Linux nftables Use-After-Free LPE Demo",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Scan local kernel for vulnerability
  python cve_2024_1086.py scan

  # Run UAF detection checks
  python cve_2024_1086.py scan --detect

  # Generate demo rule files
  python cve_2024_1086.py generate --pattern full

  # Show attack flow and detection
  python cve_2024_1086.py explain

  # Generate report
  python cve_2024_1086.py report

⚠️  For authorized security testing and education only.
""")

    sub = parser.add_subparsers(dest='command')

    # Scan
    scan_p = sub.add_parser('scan', help='Scan local kernel for vulnerability')
    scan_p.add_argument('--detect', action='store_true', help='Run UAF detection checks')

    # Generate
    gen = sub.add_parser('generate', help='Generate demo nftables rule files')
    gen.add_argument('--pattern', '-p', default='all',
                     choices=['full', 'double_free', 'spray', 'all'],
                     help='Rule pattern to generate')
    gen.add_argument('--output', '-o', default='./cve-2024-1086-output')

    # Explain
    sub.add_parser('explain', help='Show attack flow, detection, and mitigation')

    # Report
    rep = sub.add_parser('report', help='Generate markdown report')
    rep.add_argument('--output', '-o', default='cve-2024-1086-report.md')

    args = parser.parse_args()

    print("""
╔═══════════════════════════════════════════════════════════════╗
║  🔓 CVE-2024-1086: Linux nftables Use-After-Free LPE        ║
║     CWE-416 | CVSS 7.8 | MITRE T1068                        ║
║     KaliAgent v4 Integration                                  ║
╚═══════════════════════════════════════════════════════════════╝

⚠️  WARNING: For authorized security testing and education only.
    Unauthorized access to computer systems is illegal.
""")

    demo = CVE2024_1086_Demo()

    if args.command == 'scan':
        report = demo.scan()
        print(f"\n  🔍 Kernel Scan Results:")
        for key, val in report.items():
            print(f"    {key}: {val}")

        if args.detect:
            results = demo.run_detection()
            print(f"\n  🛡️  UAF Detection Results:")
            for r in results:
                emoji = "🔴" if r.status == "vulnerable" else "🟢" if r.status == "safe" else "⚪"
                print(f"    {emoji} {r.check_name}: {r.status}")
                print(f"       {r.details}")
                if r.evidence:
                    print(f"       Evidence: {r.evidence}")

    elif args.command == 'generate':
        files = demo.generate_rules(args.output, args.pattern)
        print(f"\n  📝 Generated {len(files)} demo files:")
        for f in files:
            print(f"    • {f}")

    elif args.command == 'explain':
        demo.explain()

    elif args.command == 'report':
        scan_data = demo.scan()
        detection = demo.run_detection()
        report = demo.generate_report(scan_data, detection)
        Path(args.output).write_text(report)
        print(f"📊 Report saved to {args.output}")

    else:
        parser.print_help()


if __name__ == "__main__":
    main()