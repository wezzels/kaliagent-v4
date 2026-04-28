#!/usr/bin/env python3
"""
🎯 KaliAgent v4 - CVE-2024-21626: runc Container Escape (Leaky Vessels)

Complete demonstration of CVE-2024-21626 — File descriptor leak in
runc that allows container escape to the host filesystem.

MITRE ATT&CK:
  - T1611: Escape to Host
  - T1068: Exploitation for Privilege Escalation

CWE-403: Exposure of File Descriptor to Unintended Control Sphere

Attack Flow:
  1. runc exec leaks file descriptor (fd) to container process
  2. Container process discovers the leaked fd via /proc/self/fd/
  3. WORKDIR is set to /proc/self/fd/<leaked_fd> (host filesystem)
  4. Container can access host filesystem through the fd
  5. Full container escape: read/write host files, chroot escape

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
from datetime import datetime
from dataclasses import dataclass, field
from typing import List, Optional, Dict, Any
from pathlib import Path
from enum import Enum

logging.basicConfig(level=logging.INFO, format='%(asctime)s [%(levelname)s] %(message)s')
logger = logging.getLogger('CVE-2024-21626')


# =============================================================================
# ENUMERATIONS
# =============================================================================

class ContainerRuntime(Enum):
    """Container runtime types"""
    DOCKER = "docker"
    PODMAN = "podman"
    CONTAINERD = "containerd"
    UNKNOWN = "unknown"


class EscapeRisk(Enum):
    """Container escape risk level"""
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    NONE = "none"


class RuncStatus(Enum):
    """runc vulnerability status"""
    VULNERABLE = "vulnerable"
    PATCHED = "patched"
    NOT_FOUND = "not_found"
    UNKNOWN = "unknown"


# =============================================================================
# DATA CLASSES
# =============================================================================

@dataclass
class ContainerConfig:
    """Container configuration for testing"""
    runtime: ContainerRuntime = ContainerRuntime.DOCKER
    container_id: str = ""
    image: str = "alpine:latest"
    privileged: bool = False
    pid_mode: str = ""
    user_namespace: bool = False
    seccomp_profile: str = ""


@dataclass
class FDScanResult:
    """Result of a file descriptor scan"""
    fd_number: int
    fd_target: str
    fd_type: str  # file, directory, socket, pipe, unknown
    readable: bool
    writable: bool
    host_access: bool  # Does this fd point to host filesystem?
    risk: EscapeRisk = EscapeRisk.NONE


@dataclass
class RuncVersion:
    """Parsed runc version"""
    raw: str = "unknown"
    major: int = 0
    minor: int = 0
    patch: int = 0
    status: RuncStatus = RuncStatus.UNKNOWN


@dataclass
class DetectionSignature:
    """Detection signature for the vulnerability"""
    name: str
    description: str
    indicator_type: str  # container, host, filesystem, network
    pattern: str
    severity: str
    false_positive_risk: str


# =============================================================================
# RUNC VERSION CHECKER
# =============================================================================

class RuncVersionChecker:
    """
    Check runc version for CVE-2024-21626 vulnerability.

    Vulnerable: runc < 1.1.12
    Patched: runc >= 1.1.12
    """

    PATCHED_VERSION = (1, 1, 12)

    def detect_runc(self) -> RuncVersion:
        """Detect runc version on the system"""
        version = RuncVersion()

        # Try direct runc command
        try:
            result = subprocess.run(
                ['runc', '--version'], capture_output=True, text=True, timeout=5
            )
            if result.returncode == 0:
                version = self._parse_version(result.stdout)
                return version
        except FileNotFoundError:
            pass
        except Exception as e:
            logger.debug(f"Error running runc --version: {e}")

        # Try via docker (docker-runc)
        try:
            result = subprocess.run(
                ['docker-runc', '--version'], capture_output=True, text=True, timeout=5
            )
            if result.returncode == 0:
                version = self._parse_version(result.stdout)
                return version
        except FileNotFoundError:
            pass
        except Exception:
            pass

        # Try via docker info
        try:
            result = subprocess.run(
                ['docker', 'info', '-f', '{{.Runtimes}}'],
                capture_output=True, text=True, timeout=10
            )
            if result.returncode == 0:
                version.status = RuncStatus.NOT_FOUND
        except Exception:
            pass

        version.status = RuncStatus.NOT_FOUND
        return version

    def _parse_version(self, version_output: str) -> RuncVersion:
        """Parse runc version string"""
        version = RuncVersion()
        version.raw = version_output.strip()

        for line in version_output.split('\n'):
            line = line.strip()
            if line.startswith('runc version'):
                parts = line.split()
                if len(parts) >= 3:
                    ver_str = parts[2]
                    try:
                        vparts = ver_str.split('.')
                        version.major = int(vparts[0])
                        version.minor = int(vparts[1]) if len(vparts) > 1 else 0
                        version.patch = int(vparts[2]) if len(vparts) > 2 else 0

                        # Check vulnerability
                        current = (version.major, version.minor, version.patch)
                        if current < self.PATCHED_VERSION:
                            version.status = RuncStatus.VULNERABLE
                        else:
                            version.status = RuncStatus.PATCHED
                    except (ValueError, IndexError):
                        version.status = RuncStatus.UNKNOWN
                break

        return version

    def check_docker_version(self) -> Optional[str]:
        """Check Docker version as additional info"""
        try:
            result = subprocess.run(
                ['docker', 'version', '-f', '{{.Server.Version}}'],
                capture_output=True, text=True, timeout=10
            )
            if result.returncode == 0:
                return result.stdout.strip()
        except Exception:
            pass
        return None


# =============================================================================
# CONTAINER ESCAPE DETECTOR
# =============================================================================

class ContainerEscapeDetector:
    """
    Detect if a container environment is vulnerable to CVE-2024-21626.

    Checks:
    1. Is the current process in a container?
    2. Are there leaked file descriptors?
    3. Can we access host filesystem via /proc/self/fd/?
    4. What capabilities does the container have?
    """

    # Indicators that we're inside a container
    CONTAINER_INDICATORS = [
        "/.dockerenv",
        "/.dockerinit",
        "/run/.containerenv",
    ]

    def is_in_container(self) -> bool:
        """Check if we're running inside a container"""
        for indicator in self.CONTAINER_INDICATORS:
            if os.path.exists(indicator):
                return True

        # Check cgroup
        try:
            with open('/proc/1/cgroup', 'r') as f:
                cgroup = f.read()
                if 'docker' in cgroup or 'containerd' in cgroup:
                    return True
        except Exception:
            pass

        # Check /proc/1/cmdline
        try:
            with open('/proc/1/cmdline', 'r') as f:
                cmdline = f.read()
                if 'containerd' in cmdline or 'runc' in cmdline:
                    return True
        except Exception:
            pass

        return False

    def scan_file_descriptors(self) -> List[FDScanResult]:
        """
        Scan /proc/self/fd/ for leaked file descriptors.

        In a vulnerable runc setup, one of the fds will point to
        the host filesystem root or container filesystem handle
        that runc leaked during exec.
        """
        results = []
        fd_dir = Path("/proc/self/fd")

        if not fd_dir.exists():
            logger.warning("Cannot access /proc/self/fd/")
            return results

        for fd_entry in fd_dir.iterdir():
            try:
                fd_num = int(fd_entry.name)
                fd_link = os.readlink(str(fd_entry))

                # Determine fd type
                fd_type = "unknown"
                readable = False
                writable = False
                host_access = False

                # Check if the fd target suggests host access
                if fd_link.startswith('/') and not fd_link.startswith('/proc/'):
                    # Could be a leaked host filesystem fd
                    # In vulnerable runc, this would be the container's rootfs
                    # which is actually on the host
                    if not fd_link.startswith('/dev/') and not fd_link.startswith('/sys/'):
                        host_access = True  # Potential host access via leaked fd

                # Try to determine if readable/writable
                try:
                    fd_path = f"/proc/self/fd/{fd_num}"
                    flags = os.open(fd_path, os.O_RDONLY | os.O_PATH)
                    os.close(flags)
                    readable = True
                except Exception:
                    pass

                # Determine type
                if fd_link.startswith('socket:'):
                    fd_type = "socket"
                    host_access = False
                elif fd_link.startswith('pipe:'):
                    fd_type = "pipe"
                    host_access = False
                elif fd_link.startswith('/dev/'):
                    fd_type = "device"
                    host_access = False
                elif fd_link.startswith('anon_inode:'):
                    fd_type = "anon_inode"
                    host_access = False
                elif os.path.isdir(fd_link) if not fd_link.startswith('/') else False:
                    fd_type = "directory"
                else:
                    fd_type = "file"

                risk = EscapeRisk.NONE
                if host_access:
                    risk = EscapeRisk.HIGH
                    if fd_type == "directory":
                        risk = EscapeRisk.CRITICAL  # Directory fd = full escape

                result = FDScanResult(
                    fd_number=fd_num,
                    fd_target=fd_link,
                    fd_type=fd_type,
                    readable=readable,
                    writable=writable,
                    host_access=host_access,
                    risk=risk,
                )
                results.append(result)

            except (ValueError, OSError) as e:
                logger.debug(f"Error scanning fd {fd_entry.name}: {e}")
                continue

        return results

    def check_escape_vectors(self) -> List[Dict[str, Any]]:
        """Check for various container escape vectors"""
        vectors = []

        # Check 1: Leaked FD escape
        leaked_fds = [r for r in self.scan_file_descriptors() if r.host_access]
        if leaked_fds:
            vectors.append({
                "vector": "Leaked FD (CVE-2024-21626)",
                "risk": "CRITICAL" if any(r.risk == EscapeRisk.CRITICAL for r in leaked_fds) else "HIGH",
                "details": f"Found {len(leaked_fds)} file descriptors with potential host access",
                "evidence": [f"fd {r.fd_number} → {r.fd_target}" for r in leaked_fds[:5]],
            })

        # Check 2: Privileged container
        try:
            with open('/proc/1/status', 'r') as f:
                status = f.read()
                if 'CapEff: 0000003fffffffff' in status:
                    vectors.append({
                        "vector": "Privileged Container",
                        "risk": "CRITICAL",
                        "details": "Container has all capabilities — trivial escape",
                        "evidence": ["CapEff: 0000003fffffffff"],
                    })
        except Exception:
            pass

        # Check 3: Host PID namespace
        if os.path.exists('/proc/1/cgroup'):
            try:
                with open('/proc/1/cgroup', 'r') as f:
                    cgroup = f.read()
                    if 'docker' not in cgroup and 'containerd' not in cgroup:
                        vectors.append({
                            "vector": "Host PID Namespace",
                            "risk": "HIGH",
                            "details": "Container shares PID namespace with host",
                            "evidence": ["PID 1 cgroup does not indicate container"],
                        })
            except Exception:
                pass

        # Check 4: Mounted host filesystems
        try:
            with open('/proc/mounts', 'r') as f:
                mounts = f.read()
                host_mounts = []
                for line in mounts.split('\n'):
                    if any(p in line for p in ['/host', '/var/run/docker', '/var/lib/docker']):
                        host_mounts.append(line)
                if host_mounts:
                    vectors.append({
                        "vector": "Host Filesystem Mounted",
                        "risk": "CRITICAL",
                        "details": "Host filesystem paths are mounted in container",
                        "evidence": host_mounts[:3],
                    })
        except Exception:
            pass

        return vectors


# =============================================================================
# LEAKED FD SCANNER
# =============================================================================

class LeakedFDScanner:
    """
    Dedicated scanner for detecting the specific fd leak pattern
    used by CVE-2024-21626.

    The vulnerability: runc exec opens /proc/self/fd/ as a file
    descriptor before entering the container. This fd is leaked
    to the container process, allowing the container to access
    the host filesystem via the leaked fd.

    Detection strategy:
    1. Check if WORKDIR can be set to /proc/self/fd/<n>
    2. List all fds and check for unexpected directory fds
    3. Test if any fd gives access beyond container rootfs
    """

    def __init__(self):
        self.findings: List[Dict] = []

    def scan_for_leaked_fds(self) -> List[Dict]:
        """Scan for leaked file descriptors specific to CVE-2024-21626"""
        detector = ContainerEscapeDetector()
        fd_results = detector.scan_file_descriptors()

        for fd in fd_results:
            # CVE-2024-21626 pattern: fd pointing to a directory that
            # is NOT /proc, NOT /dev, NOT a socket/pipe
            if fd.fd_type in ("directory", "unknown") and fd.host_access:
                # Try to read the directory via the fd
                try:
                    fd_path = f"/proc/self/fd/{fd.fd_number}"
                    entries = os.listdir(fd_path)
                    self.findings.append({
                        "fd": fd.fd_number,
                        "target": fd.fd_target,
                        "type": "potential_leak",
                        "entries_sample": entries[:10],
                        "risk": "CRITICAL" if len(entries) > 2 else "HIGH",
                    })
                except PermissionError:
                    self.findings.append({
                        "fd": fd.fd_number,
                        "target": fd.fd_target,
                        "type": "potential_leak",
                        "entries_sample": [],
                        "risk": "MEDIUM",
                    })
                except NotADirectoryError:
                    pass
                except Exception as e:
                    self.findings.append({
                        "fd": fd.fd_number,
                        "target": fd.fd_target,
                        "type": "error",
                        "error": str(e),
                        "risk": "LOW",
                    })

        return self.findings

    def test_workdir_escape(self, test_path: str = "/proc/self/fd/3") -> Dict[str, Any]:
        """
        Test if WORKDIR can be set to a /proc/self/fd/ path.

        This is the core of CVE-2024-21626: if WORKDIR is set
        to /proc/self/fd/<leaked_fd>, subsequent operations
        (like COPY) use the host filesystem as their working
        directory, allowing container escape.

        This is a SAFE check — it only tests path resolution,
        not actual exploitation.
        """
        result = {
            "test_path": test_path,
            "resolvable": False,
            "is_directory": False,
            "risk": "NONE",
            "details": "",
        }

        try:
            if os.path.exists(test_path):
                result["resolvable"] = True
                if os.path.isdir(test_path):
                    result["is_directory"] = True
                    result["risk"] = "CRITICAL"
                    result["details"] = (
                        f"Path {test_path} resolves to a directory — "
                        f"WORKDIR escape would succeed"
                    )
                else:
                    result["risk"] = "MEDIUM"
                    result["details"] = f"Path {test_path} exists but is not a directory"
            else:
                result["details"] = f"Path {test_path} does not exist"
        except Exception as e:
            result["details"] = f"Error testing path: {e}"

        return result


# =============================================================================
# DETECTION SIGNATURES
# =============================================================================

DETECTION_SIGNATURES = [
    DetectionSignature(
        name="runc Version < 1.1.12",
        description="Vulnerable runc version installed on host",
        indicator_type="host",
        pattern="runc version < 1.1.12 detected via 'runc --version'",
        severity="critical",
        false_positive_risk="low",
    ),
    DetectionSignature(
        name="Unexpected Directory FD in Container",
        description="File descriptor pointing to directory leaked into container",
        indicator_type="container",
        pattern="/proc/self/fd/<n> resolves to a directory outside "
                "expected container paths (not /proc, /dev, /sys)",
        severity="critical",
        false_positive_risk="low",
    ),
    DetectionSignature(
        name="WORKDIR /proc/self/fd/ Pattern",
        description="Container image or runtime config using /proc/self/fd/ as WORKDIR",
        indicator_type="container",
        pattern="Dockerfile contains 'WORKDIR /proc/self/fd/' or "
                "container process cwd is /proc/self/fd/<n>",
        severity="critical",
        false_positive_risk="low",
    ),
    DetectionSignature(
        name="Container Accessing Host Filesystem",
        description="Container process accessing files outside its rootfs",
        indicator_type="filesystem",
        pattern="Container process opens file via /proc/self/fd/<n>/etc/passwd "
                "or similar host filesystem path",
        severity="critical",
        false_positive_risk="medium",
    ),
    DetectionSignature(
        name="runc exec FD Leak",
        description="runc exec leaks file descriptor before container entry",
        indicator_type="host",
        pattern="strace of runc exec shows open(/proc/self/fd/) before "
                "container namespace entry, fd not closed",
        severity="critical",
        false_positive_risk="low",
    ),
]


# =============================================================================
# MITIGATION STEPS
# =============================================================================

MITIGATIONS = [
    {
        "action": "Upgrade runc",
        "description": "Upgrade to runc 1.1.12 or later",
        "priority": "critical",
        "details": "runc 1.1.12 properly closes leaked file descriptors "
                   "before entering the container namespace. The fix ensures "
                   "that /proc/self/fd/ is not leaked during runc exec.",
        "commands": [
            "apt update && apt install containerd.io  # Debian/Ubuntu (includes runc)",
            "yum update runc                         # RHEL/CentOS",
            "dockerd --version  # Verify Docker uses updated runc",
        ],
    },
    {
        "action": "Apply Seccomp Profiles",
        "description": "Use restrictive seccomp profiles to limit syscalls",
        "priority": "high",
        "details": "A properly configured seccomp profile can prevent the "
                   "container from using the leaked fd by restricting "
                   "openat() and other file operations on /proc/self/fd/.",
        "commands": [
            "docker run --security-opt seccomp=unconfined ...  # DO NOT do this",
            "docker run --security-opt seccomp=default.json ... # Use default profile",
            "# Use Docker's default seccomp profile (already restricts /proc access)",
        ],
    },
    {
        "action": "Use User Namespaces",
        "description": "Enable user namespace remapping for containers",
        "priority": "high",
        "details": "User namespace remapping (userns-remap) limits the "
                   "impact of container escape by mapping container root "
                   "to an unprivileged user on the host.",
        "commands": [
            'echo \'{"userns-remap": "default"}\' >> /etc/docker/daemon.json',
            "systemctl restart docker",
            "# Or per-container: docker run --userns=host ...",
        ],
    },
    {
        "action": "Restrict Container Capabilities",
        "description": "Drop all unnecessary capabilities from containers",
        "priority": "medium",
        "details": "Even with a leaked fd, a container without CAP_SYS_ADMIN "
                   "and CAP_SYS_CHROOT has limited escape options.",
        "commands": [
            "docker run --cap-drop=ALL --cap-add=NET_BIND_SERVICE ...",
            "# Drop all caps, add only what's needed",
        ],
    },
    {
        "action": "Read-Only Root Filesystem",
        "description": "Run containers with read-only root filesystem",
        "priority": "medium",
        "details": "With --read-only, the container cannot modify its "
                   "rootfs, limiting what an escaped process can do.",
        "commands": [
            "docker run --read-only --tmpfs /tmp ...",
        ],
    },
    {
        "action": "Update Container Runtime",
        "description": "Update Docker/containerd to versions with patched runc",
        "priority": "critical",
        "details": "Most container runtimes bundle runc. Updating Docker "
                   "or containerd will pull in the patched version.",
        "commands": [
            "curl -fsSL https://get.docker.com | sh  # Install latest Docker",
            "apt update && apt upgrade docker-ce      # Debian/Ubuntu",
            "yum update docker-ce                      # RHEL/CentOS",
        ],
    },
]


# =============================================================================
# MAIN DEMO CLASS
# =============================================================================

class CVE2024_21626_Demo:
    """
    Complete demonstration orchestrator for CVE-2024-21626.

    Provides:
    1. runc version checking
    2. Container escape detection
    3. Leaked FD scanning
    4. Detection signature reference
    5. Mitigation guidance with commands
    """

    VERSION = "1.0.0"

    def __init__(self):
        self.output_dir = Path("./cve-2024-21626-output")
        self.runc_checker = RuncVersionChecker()
        self.escape_detector = ContainerEscapeDetector()
        self.fd_scanner = LeakedFDScanner()

    def scan(self) -> Dict[str, Any]:
        """Scan the local system for vulnerability"""
        report = {}

        # runc version
        runc_ver = self.runc_checker.detect_runc()
        report["runc_version"] = runc_ver.raw
        report["runc_status"] = runc_ver.status.value

        # Docker version
        docker_ver = self.runc_checker.check_docker_version()
        report["docker_version"] = docker_ver or "not found"

        # Container check
        report["in_container"] = self.escape_detector.is_in_container()

        # If in container, scan for escape vectors
        if report["in_container"]:
            vectors = self.escape_detector.check_escape_vectors()
            report["escape_vectors"] = vectors
        else:
            report["escape_vectors"] = []

        logger.info(f"🔍 Scan: runc={runc_ver.raw}, status={runc_ver.status.value}")
        return report

    def scan_fds(self) -> List[Dict]:
        """Scan for leaked file descriptors"""
        return self.fd_scanner.scan_for_leaked_fds()

    def print_attack_flow(self):
        """Print the complete attack flow diagram"""
        print("""
╔══════════════════════════════════════════════════════════════════╗
║           CVE-2024-21626 — Leaky Vessels ATTACK FLOW              ║
╚══════════════════════════════════════════════════════════════════╝

  ┌──────────────┐     ┌──────────────┐     ┌──────────────┐
  │   Attacker   │     │    runc      │     │    Host      │
  │ (Container)  │     │   (Host)     │     │ Filesystem   │
  └──────┬───────┘     └──────┬───────┘     └──────┬───────┘
         │                    │                     │
         │            1. docker exec       2. runc opens
         │               <container>        /proc/self/fd/
         │                    │                (fd leaked!)
         │                    │                     │
    3. Container         4. runc enters       5. Leaked fd
       process               container            still open
       discovers             namespace            in container
       /proc/self/fd/            │                  │
         │                    │                     │
    6. ls /proc/self/fd/ ───────────────────────────►
       → fd N points to host /
         │                    │                     │
    7. WORKDIR set            │                     │
       to /proc/self/fd/N     │                     │
         │                    │                     │
    8. Subsequent          9. Operations            │
       COPY/ADD            use HOST / as            │
       commands             working dir              │
         │                    │                     │
    10. Read /etc/shadow ◄───┼─────────────────────┤
    11. Write /etc/cron.d/ ◄┼─────────────────────┤
    12. Full host access! ◄──┼─────────────────────┘
         ▼                    ▼                     ▼

  KEY INSIGHT: runc exec opens /proc/self/fd/ as a file
  descriptor BEFORE entering the container's namespaces.
  The fd is NOT properly closed before the container process
  starts.

  The container process can:
    1. Find the leaked fd: ls -la /proc/self/fd/
    2. Set WORKDIR to /proc/self/fd/<n>
    3. Access host filesystem through the leaked fd
    4. Read sensitive files (/etc/shadow, SSH keys)
    5. Write to host (/etc/cron.d/, ~/.ssh/)
    6. Achieve full container escape

  Variants in the Leaky Vessels family:
    • CVE-2024-21626: WORKDIR fd leak (this one)
    • CVE-2024-23651: Buildkit mount cache leak
    • CVE-2024-23652: Buildkit build-time race
    • CVE-2024-23653: Buildkit privileged context
""")

    def print_detection_signatures(self):
        """Print all detection signatures"""
        print("""
╔══════════════════════════════════════════════════════════════════╗
║           CVE-2024-21626 — DETECTION SIGNATURES                  ║
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
║           CVE-2024-21626 — MITIGATION STEPS                      ║
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

    def generate_report(self, scan_data: Optional[Dict] = None) -> str:
        """Generate a complete markdown report"""
        report = []
        report.append("# CVE-2024-21626: runc Container Escape (Leaky Vessels)")
        report.append("")
        report.append(f"**Date:** {datetime.now().strftime('%Y-%m-%d')}")
        report.append("**Tool:** KaliAgent v4 — CVE-2024-21626 Demo v1.0.0")
        report.append("")
        report.append("## Summary")
        report.append("")
        report.append("A file descriptor leak in runc allows container escape to the host")
        report.append("filesystem. When runc exec is called, it opens /proc/self/fd/ as a")
        report.append("file descriptor before entering the container namespace. This fd is")
        report.append("leaked to the container process, which can use it to access the host.")
        report.append("")
        report.append("## CVSS")
        report.append("- **Score:** 8.6 HIGH")
        report.append("- **Vector:** CVSS:3.1/AV:L/AC:L/PR:N/UI:N/S:C/C:H/I:H/A:N")
        report.append("")
        report.append("## Vulnerable Versions")
        report.append("- runc < 1.1.12")
        report.append("- Docker with bundled runc < 1.1.12")
        report.append("")
        report.append("## Leaky Vessels Family")
        report.append("- CVE-2024-21626: WORKDIR fd leak (runc)")
        report.append("- CVE-2024-23651: Mount cache leak (BuildKit)")
        report.append("- CVE-2024-23652: Build-time race (BuildKit)")
        report.append("- CVE-2024-23653: Privileged context (BuildKit)")
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
                if isinstance(val, (str, bool, int)):
                    report.append(f"- **{key}:** {val}")
            report.append("")
        return "\n".join(report)


# =============================================================================
# CLI ENTRY POINT
# =============================================================================

def main():
    parser = argparse.ArgumentParser(
        description="CVE-2024-21626: runc Container Escape (Leaky Vessels) Demo",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Scan for vulnerability
  python cve_2024_21626.py scan

  # Scan for leaked FDs (run inside container)
  python cve_2024_21626.py scan --fd-scan

  # Show attack flow and detection
  python cve_2024_21626.py explain

  # Generate report
  python cve_2024_21626.py report

⚠️  For authorized security testing and education only.
""")

    sub = parser.add_subparsers(dest='command')

    # Scan
    scan_p = sub.add_parser('scan', help='Scan for vulnerability')
    scan_p.add_argument('--fd-scan', action='store_true', help='Scan for leaked FDs')

    # Explain
    sub.add_parser('explain', help='Show attack flow, detection, and mitigation')

    # Report
    rep = sub.add_parser('report', help='Generate markdown report')
    rep.add_argument('--output', '-o', default='cve-2024-21626-report.md')

    # Generate
    gen = sub.add_parser('generate', help='Generate demo configuration files')
    gen.add_argument('--output', '-o', default='./cve-2024-21626-output')

    args = parser.parse_args()

    print("""
╔═══════════════════════════════════════════════════════════════╗
║  🔓 CVE-2024-21626: runc Container Escape (Leaky Vessels)  ║
║     CWE-403 | CVSS 8.6 | MITRE T1611                        ║
║     KaliAgent v4 Integration                                  ║
╚═══════════════════════════════════════════════════════════════╝

⚠️  WARNING: For authorized security testing and education only.
    Unauthorized access to computer systems is illegal.
""")

    demo = CVE2024_21626_Demo()

    if args.command == 'scan':
        report = demo.scan()
        print(f"\n  🔍 Scan Results:")
        for key, val in report.items():
            if isinstance(val, (str, bool)):
                print(f"    {key}: {val}")
            elif isinstance(val, list):
                print(f"    {key}:")
                for v in val:
                    print(f"      • {v}")

        if args.fd_scan:
            findings = demo.scan_fds()
            if findings:
                print(f"\n  ⚠️  Leaked FD Findings ({len(findings)}):")
                for f in findings:
                    print(f"    FD {f['fd']}: {f['target']} [{f['risk']}]")
            else:
                print(f"\n  ✅ No leaked FDs detected")

    elif args.command == 'explain':
        demo.explain()

    elif args.command == 'report':
        scan_data = demo.scan()
        report = demo.generate_report(scan_data)
        Path(args.output).write_text(report)
        print(f"📊 Report saved to {args.output}")

    elif args.command == 'generate':
        out = Path(args.output)
        out.mkdir(parents=True, exist_ok=True)

        config_data = {
            "cve": "CVE-2024-21626",
            "description": "runc Container Escape (Leaky Vessels)",
            "mitigations": [
                {"action": m["action"], "priority": m["priority"]}
                for m in MITIGATIONS
            ],
            "detection_signatures": [
                {"name": s.name, "type": s.indicator_type, "severity": s.severity}
                for s in DETECTION_SIGNATURES
            ],
        }
        config_path = out / "cve-2024-21626-config.json"
        config_path.write_text(json.dumps(config_data, indent=2))
        print(f"📝 Demo config saved to {config_path}")

    else:
        parser.print_help()


if __name__ == "__main__":
    main()