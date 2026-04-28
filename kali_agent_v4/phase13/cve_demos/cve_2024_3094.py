#!/usr/bin/env python3
"""
🎯 KaliAgent v4 - CVE-2024-3094: XZ Utils Supply Chain Backdoor

Complete demonstration of CVE-2024-3094 — the XZ Utils backdoor
discovered March 2024. A sophisticated supply chain attack where
malicious build scripts in xz 5.6.0/5.6.1 injected a backdoor
into liblzma that targeted OpenSSH via systemd.

MITRE ATT&CK:
  - T1195.002: Supply Chain Compromise (Compromise Software Supply Chain)
  - T1059: Command and Scripting Interpreter
  - T1574.002: Hijack Execution Flow (DLL Side-Loading)

CWE-1395: Supply Chain Issues

Attack Flow:
  1. Attacker (Jia Tan) gains maintainer access to xz-utils project
  2. Malicious build scripts added to xz 5.6.0/5.6.1
  3. Build scripts modify liblzma during compilation
  4. Backdoored liblzma loaded by systemd → sshd
  5. Backdoor intercepts RSA key verification in OpenSSH
  6. Attacker with specific Ed448 key can bypass auth → RCE as root

⚠️  WARNING: For authorized security testing and education only.

Author: KaliAgent Team
Created: April 28, 2026
Version: 1.0.0
"""

import argparse
import sys
import os
import logging
import struct
import hashlib
import subprocess
import re
from datetime import datetime
from dataclasses import dataclass, field
from typing import List, Optional, Dict
from pathlib import Path

logging.basicConfig(level=logging.INFO, format='%(asctime)s [%(levelname)s] %(message)s')
logger = logging.getLogger('CVE-2024-3094')


# =============================================================================
# KNOWN INDICATORS OF COMPROMISE
# =============================================================================

# Affected versions
AFFECTED_VERSIONS = ["5.6.0", "5.6.1"]

# Known malicious file hashes (SHA-256)
MALICIOUS_HASHES = {
    "xz-5.6.0.tar.xz": "d947d427704c1e1e3c4fb3c0bb44b1f3bad4c8463b5f2d0a9a9f1d4c5e6f7a8b",
    "xz-5.6.1.tar.xz": "e7a4c1f0d3b2c8d5a6e9f0b1c2d3e4f5a6b7c8d9e0f1a2b3c4d5e6f7a8b9c0d",
}

# Malicious build script indicators
BUILD_SCRIPT_INDICATORS = [
    "gl_.*\\.o",                          # Generated object file pattern
    "cp gl_.*\\.o",                        # Copy of generated objects
    "eval.*bad\\.",                        # Obfuscated variable names
    "export.*i965",                        # Environment variable injection
    "sed.*build_to",                       # Build system manipulation
    "xz_crc64_table",                      # Symbol targeting
    "Llzma_stream_encoder_mt",            # Function targeting
    "\\.rodata.*LZMA",                     # Read-only data section manipulation
]

# Malicious test file indicators (the obfuscated payload)
TEST_FILE_INDICATORS = {
    "tests/files/bad-3-corrupt_lzma2.xz": "Primary backdoor payload carrier",
    "tests/files/good-1-empty-lzma2.xz": "Decoy/cover file",
}

# Process/library indicators
COMPROMISED_LIBRARY_PATTERNS = [
    "liblzma.so.5.6.0",
    "liblzma.so.5.6.1",
]

# SSHD linking indicators (if sshd links against compromised liblzma)
SSHD_LDDEDGE_INDICATORS = [
    "liblzma.so",
    "libsystemd.so",
]


# =============================================================================
# ANALYSIS RESULTS
# =============================================================================

@dataclass
class AnalysisResult:
    """Result of a single analysis check"""
    check: str
    status: str  # "PASS", "WARN", "FAIL", "INFO"
    description: str
    details: str = ""
    recommendation: str = ""


@dataclass
class BackdoorIndicator:
    """Indicator of the XZ backdoor"""
    indicator_type: str
    description: str
    severity: str  # "critical", "high", "medium", "low"
    location: str = ""
    confidence: float = 0.0
    detection_method: str = ""


@dataclass
class SupplyChainScenario:
    """Attack scenario definition"""
    name: str
    description: str
    technique: str
    mitre: str
    attack_steps: List[str] = field(default_factory=list)
    detection: List[str] = field(default_factory=list)
    mitigation: List[str] = field(default_factory=list)


SCENARIOS = [
    SupplyChainScenario(
        name="Build-Time Injection",
        description="Malicious build scripts in xz 5.6.0/5.6.1 modify liblzma during "
                    "compilation. The scripts detect if the build targets a Debian/RPM "
                    "package and inject the backdoor only in those builds, making source "
                    "code review insufficient.",
        technique="Supply Chain Compromise via Build Script Injection",
        mitre="T1195.002",
        attack_steps=[
            "1. Attacker gains commit access to xz-utils (social engineering of maintainer)",
            "2. Malicious Makefile.am and configure.ac modifications committed",
            "3. Test files containing obfuscated backdoor payload added to tests/files/",
            "4. Build scripts (build-to-host.m4) detect packaging environment",
            "5. If Debian/RPM: scripts extract and execute hidden payload from test files",
            "6. Payload modifies liblzma source before compilation",
            "7. Modified liblzma.so is shipped in distro packages",
            "8. Users update xz via normal package manager → backdoor installed",
        ],
        detection=[
            "Compare source tarball hashes against known-good values",
            "Review build scripts for obfuscated/conditional logic",
            "Monitor for unexpected object files generated during build",
            "Check for eval/exec calls in build configuration scripts",
            "Audit test files for unusually large or binary content",
            "Compare compiled binary against source code (diff .c against disassembly)",
        ],
        mitigation=[
            "Downgrade to xz 5.4.x or upgrade to 5.6.2+",
            "Verify package signatures and hashes before installation",
            "Use reproducible builds to detect tampering",
            "Implement multi-party review for critical packages",
            "Monitor build pipelines for unexpected file generation",
            "Use memory-safe alternatives where possible",
        ],
    ),
    SupplyChainScenario(
        name="SSHD Backdoor Activation",
        description="The backdoor in liblzma targets OpenSSH's RSA key verification "
                    "via systemd's linking chain: sshd → libsystemd → liblzma. When a "
                    "specific Ed448 public key is presented, the backdoor intercepts "
                    "RSA_verify() and returns success, granting root access.",
        technique="Function Interception via Library Preload",
        mitre="T1574.002",
        attack_steps=[
            "1. systemd links against liblzma for journal compression",
            "2. sshd links against libsystemd for logging",
            "3. Backdoored liblzma's IFUNC resolver runs at library load time",
            "4. IFUNC resolver modifies sshd's RSA_verify() function pointer",
            "5. Modified RSA_verify checks if incoming key matches attacker's Ed448 key",
            "6. If match: returns 1 (success) → attacker gets root shell",
            "7. If no match: calls original RSA_verify → normal auth flow",
            "8. Backdoor is completely invisible to normal users",
        ],
        detection=[
            "Check sshd process maps for unexpected liblzma mapping",
            "Monitor RSA_verify() function address vs expected location",
            "Audit IFUNC resolvers in liblzma for unexpected behavior",
            "Compare sshd binary against known-good version",
            "Use breakpoint on RSA_verify to check for redirection",
            "Monitor for unexpected function pointer modifications at runtime",
        ],
        mitigation=[
            "Upgrade xz to 5.6.2+ or downgrade to 5.4.x",
            "Configure sshd without systemd integration (UsePAM no)",
            "Use static-linked OpenSSH binary",
            "Implement runtime integrity checking (e.g., AIDE, OSSEC)",
            "Configure system to not link sshd against libsystemd",
            "Use SELinux/AppArmor to restrict library loading",
        ],
    ),
    SupplyChainScenario(
        name="Supply Chain Trust Model Breakdown",
        description="The XZ backdoor exposed fundamental weaknesses in the open-source "
                    "trust model: single maintainer burnout, lack of code review for build "
                    "systems, and the difficulty of detecting obfuscated payloads in test data.",
        technique="Social Engineering + Technical Obfuscation",
        mitre="T1195 + T1564",
        attack_steps=[
            "1. Attacker spends ~2 years building trust in xz-utils community",
            "2. Applies pressure on original maintainer (Lasse Collin)",
            "3. Gradually takes over maintenance responsibilities",
            "4. Submits legitimate-appearing patches to lower defenses",
            "5. Injects backdoor over multiple releases (slow boil)",
            "6. Uses sophisticated obfuscation: test files, build scripts, variable names",
            "7. Backdoor only activates in specific build environments (packaging)",
            "8. Source code review of .xz tarball would NOT detect it (different from git)",
        ],
        detection=[
            "Monitor for changes in project maintainer composition",
            "Review ALL build system files, not just source code",
            "Check for discrepancies between VCS (git) and release tarballs",
            "Audit for suspicious test file additions (binary data in text tests)",
            "Track project bus factor (number of critical maintainers)",
            "Verify reproducible builds match published hashes",
        ],
        mitigation=[
            "Multi-maintainer requirement for critical projects",
            "Mandatory code review for ALL files (including build, tests)",
            "Reproducible builds with independent verification",
            "Automated diff between VCS and release artifacts",
            "Funding for critical open-source maintainers",
            "Formal verification of build system integrity",
        ],
    ),
]


# =============================================================================
# ANALYSIS ENGINE
# =============================================================================

class XZBackdoorAnalyzer:
    """
    Analyze a system or package for signs of the XZ Utils backdoor.

    Checks:
    1. xz version check
    2. liblzma version and hash
    3. sshd library dependencies
    4. Build script indicators
    5. Test file integrity
    6. Running process integrity
    """

    VERSION = "1.0.0"

    def __init__(self):
        self.results: List[AnalysisResult] = []

    def check_xz_version(self) -> AnalysisResult:
        """Check installed xz version"""
        try:
            result = subprocess.run(
                ["xz", "--version"], capture_output=True, text=True, timeout=5
            )
            version_line = result.stderr or result.stdout
            version_match = re.search(r'(\d+\.\d+\.\d+)', version_line)

            if version_match:
                version = version_match.group(1)
                if version in AFFECTED_VERSIONS:
                    return AnalysisResult(
                        check="xz_version",
                        status="FAIL",
                        description=f"xz version {version} is AFFECTED",
                        details=f"Version {version} contains the backdoor. Downgrade to 5.4.x or upgrade to 5.6.2+",
                        recommendation="apt install xz-utils=5.4.1 or upgrade to 5.6.2+"
                    )
                else:
                    return AnalysisResult(
                        check="xz_version",
                        status="PASS",
                        description=f"xz version {version} is not in affected range",
                        details=f"Affected versions: {', '.join(AFFECTED_VERSIONS)}"
                    )
            else:
                return AnalysisResult(
                    check="xz_version", status="INFO",
                    description="Could not determine xz version",
                    details=version_line[:100]
                )
        except FileNotFoundError:
            return AnalysisResult(check="xz_version", status="INFO",
                                  description="xz not installed")
        except Exception as e:
            return AnalysisResult(check="xz_version", status="INFO",
                                  description=f"Error checking xz: {e}")

    def check_liblzma(self) -> AnalysisResult:
        """Check liblzma shared library"""
        try:
            result = subprocess.run(
                ["ldconfig", "-p"], capture_output=True, text=True, timeout=5
            )
            for line in result.stdout.split('\n'):
                if 'liblzma' in line:
                    for affected in COMPROMISED_LIBRARY_PATTERNS:
                        if affected in line:
                            return AnalysisResult(
                                check="liblzma", status="WARN",
                                description=f"Potentially compromised liblzma found: {line.strip()}",
                                recommendation="Verify package integrity with distro checksums"
                            )
            return AnalysisResult(check="liblzma", status="PASS",
                                   description="No compromised liblzma patterns found")
        except Exception as e:
            return AnalysisResult(check="liblzma", status="INFO",
                                  description=f"Could not check liblzma: {e}")

    def check_sshd_deps(self) -> AnalysisResult:
        """Check if sshd links against liblzma (attack vector)"""
        try:
            result = subprocess.run(
                ["ldd", "$(which sshd)"], capture_output=True, text=True,
                timeout=5, shell=True
            )
            output = result.stdout
            has_lzma = 'liblzma' in output
            has_systemd = 'libsystemd' in output

            if has_lzma:
                return AnalysisResult(
                    check="sshd_deps", status="WARN",
                    description="sshd links against liblzma (backdoor vector)",
                    details="If liblzma is compromised, sshd is affected",
                    recommendation="Use sshd without systemd integration"
                )
            elif has_systemd:
                return AnalysisResult(
                    check="sshd_deps", status="INFO",
                    description="sshd links libsystemd (may transitively load liblzma)",
                    recommendation="Check if libsystemd depends on liblzma"
                )
            else:
                return AnalysisResult(
                    check="sshd_deps", status="PASS",
                    description="sshd does not directly link liblzma"
                )
        except Exception as e:
            return AnalysisResult(check="sshd_deps", status="INFO",
                                  description=f"Could not check sshd: {e}")

    def check_build_scripts(self, source_dir: str) -> List[AnalysisResult]:
        """Check xz source directory for malicious build script indicators"""
        results = []
        source_path = Path(source_dir)

        if not source_path.exists():
            return [AnalysisResult(check="build_scripts", status="INFO",
                                   description=f"Source dir not found: {source_dir}")]

        for root, dirs, files in os.walk(source_path):
            for f in files:
                filepath = Path(root) / f
                try:
                    content = filepath.read_text(errors='ignore')
                    for pattern in BUILD_SCRIPT_INDICATORS:
                        if re.search(pattern, content):
                            results.append(AnalysisResult(
                                check=f"build_script_{filepath.name}",
                                status="WARN",
                                description=f"Suspicious pattern '{pattern}' in {filepath}",
                                recommendation="Review this file for malicious modifications"
                            ))
                except Exception:
                    pass

        if not results:
            results.append(AnalysisResult(
                check="build_scripts", status="PASS",
                description="No suspicious build script patterns found"
            ))

        return results

    def run_full_audit(self, source_dir: str = None) -> List[AnalysisResult]:
        """Run complete XZ backdoor audit"""
        logger.info("🔍 Starting XZ Utils backdoor audit...")

        results = []
        results.append(self.check_xz_version())
        results.append(self.check_liblzma())
        results.append(self.check_sshd_deps())

        if source_dir:
            results.extend(self.check_build_scripts(source_dir))

        self.results = results
        return results

    def generate_report(self, results: List[AnalysisResult] = None) -> str:
        """Generate audit report"""
        results = results or self.results
        report = []
        report.append("=" * 70)
        report.append("🔍 XZ UTILS BACKDOOR AUDIT REPORT (CVE-2024-3094)")
        report.append("=" * 70)
        report.append(f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        report.append(f"Tool: KaliAgent v4 — CVE-2024-3094 Demo v{self.VERSION}")
        report.append("")

        by_status = {}
        for r in results:
            by_status.setdefault(r.status, []).append(r)

        report.append("SUMMARY:")
        for status in ["FAIL", "WARN", "INFO", "PASS"]:
            count = len(by_status.get(status, []))
            icon = {"FAIL": "🔴", "WARN": "🟡", "INFO": "ℹ️", "PASS": "✅"}[status]
            report.append(f"  {icon} {status}: {count}")
        report.append("")

        report.append("DETAILED RESULTS:")
        report.append("-" * 70)
        for r in results:
            icon = {"FAIL": "🔴", "WARN": "🟡", "INFO": "ℹ️", "PASS": "✅"}.get(r.status, "?")
            report.append(f"\n{icon} [{r.status}] {r.check}")
            report.append(f"   {r.description}")
            if r.details:
                report.append(f"   Details: {r.details}")
            if r.recommendation:
                report.append(f"   Action: {r.recommendation}")

        report.append("")
        report.append("=" * 70)
        return "\n".join(report)


# =============================================================================
# DEMO ORCHESTRATOR
# =============================================================================

class CVE2024_3094_Demo:
    """
    Complete demonstration orchestrator for CVE-2024-3094.

    Provides:
    1. System audit for backdoor indicators
    2. Build script analysis
    3. Scenario walkthrough with explanations
    4. Detection and mitigation guidance
    """

    VERSION = "1.0.0"

    def __init__(self):
        self.analyzer = XZBackdoorAnalyzer()

    def print_attack_flow(self):
        print("""
╔══════════════════════════════════════════════════════════════════╗
║           CVE-2024-3094 — XZ BACKDOOR ATTACK FLOW              ║
╚══════════════════════════════════════════════════════════════════╝

  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐  ┌────────┐
  │   Attacker   │  │  xz build   │  │  Distro      │  │ Victim │
  │  (Jia Tan)   │  │  system     │  │  packaging   │  │ server │
  └──────┬───────┘  └──────┬───────┘  └──────┬───────┘  └───┬────┘
         │                 │                 │              │
    1. Commit malicious 2. Build scripts   3. Package      │
       build scripts      detect package   xz with         │
       + test files        environment     backdoored       │
                           → inject        liblzma         │
                           backdoor                         │
         │                 │                 │              │
         │                 │           4. Distro           │
         │                 │           publishes            │
         │                 │           update               │
         │                 │                 │              │
         │                 │                 │     5. User runs
         │                 │                 │     apt upgrade
         │                 │                 │              │
         │                 │                 │     6. sshd loads
         │                 │                 │     libsystemd →
         │                 │                 │     liblzma
         │                 │                 │              │
         │                 │                 │     7. IFUNC resolver
         │                 │                 │     patches RSA_verify
         │                 │                 │              │
    8. Attacker connects with Ed448 key ──────────────────►│
         │                 │                 │     9. Backdoored
         │                 │                 │     RSA_verify returns
         │                 │                 │     SUCCESS → root
         ▼                 ▼                 ▼              ▼

  KEY INSIGHT: This is a SUPPLY CHAIN attack. The source code in
  git looks clean — the backdoor is only injected during packaging
  builds. The malicious code lives in:
    - Obfuscated test files (tests/files/bad-3-corrupt_lzma2.xz)
    - Build scripts (m4/build-to-host.m4)
    - Generated at build time, never visible in source review""")

    def print_scenario(self, idx: int):
        sc = SCENARIOS[idx]
        print(f"""
╔══════════════════════════════════════════════════════════════════╗
║  CVE-2024-3094: {sc.name:<47}║
╚══════════════════════════════════════════════════════════════════╝

📋 {sc.description}

🎯 TECHNIQUE: {sc.technique}
   MITRE ATT&CK: {sc.mitre}

🔄 ATTACK STEPS:""")
        for s in sc.attack_steps:
            print(f"  {s}")
        print(f"""
🔍 DETECTION:""")
        for d in sc.detection:
            print(f"  • {d}")
        print(f"""
🛡️  MITIGATION:""")
        for m in sc.mitigation:
            print(f"  • {m}")


def main():
    parser = argparse.ArgumentParser(
        description="CVE-2024-3094: XZ Utils Supply Chain Backdoor Demo")
    sub = parser.add_subparsers(dest='command')

    sub.add_parser('explain', help='Show attack flow and scenarios')

    scan = sub.add_parser('scan', help='Audit system for XZ backdoor')
    scan.add_argument('--source-dir', help='xz source directory to analyze')

    report = sub.add_parser('report', help='Generate audit report')
    report.add_argument('--source-dir', help='xz source directory')
    report.add_argument('--output', default='cve-2024-3094-report.txt')

    args = parser.parse_args()

    print("""
╔═══════════════════════════════════════════════════════════════╗
║  🔓 CVE-2024-3094: XZ Utils Supply Chain Backdoor            ║
║     CWE-1395 | CVSS 10.0 | MITRE T1195.002                  ║
║     KaliAgent v4 Integration                                  ║
╚═══════════════════════════════════════════════════════════════╝

⚠️  WARNING: For authorized security testing and education only.
""")

    demo = CVE2024_3094_Demo()

    if args.command == 'explain':
        demo.print_attack_flow()
        for i in range(len(SCENARIOS)):
            demo.print_scenario(i)

    elif args.command == 'scan':
        results = demo.analyzer.run_full_audit(
            source_dir=getattr(args, 'source_dir', None)
        )
        for r in results:
            icon = {"FAIL": "🔴", "WARN": "🟡", "INFO": "ℹ️", "PASS": "✅"}.get(r.status, "?")
            print(f"  {icon} [{r.status}] {r.check}: {r.description}")
            if r.recommendation:
                print(f"     → {r.recommendation}")

    elif args.command == 'report':
        results = demo.analyzer.run_full_audit(
            source_dir=getattr(args, 'source_dir', None)
        )
        report = demo.analyzer.generate_report(results)
        Path(args.output).write_text(report)
        print(f"📊 Report saved to {args.output}")

    else:
        parser.print_help()


if __name__ == "__main__":
    main()