#!/usr/bin/env python3
"""
🎯 KaliAgent v4 - Phase 13: CVE Demo Integration Agent

Unified interface for running CVE demonstration modules.
Each demo includes: vulnerability explanation, attack flow,
payload generation, detection signatures, and mitigation guidance.

Current demos:
  - CVE-2024-6387:  OpenSSH regreSSHion RCE
  - CVE-2024-1086:  Linux nftables use-after-free LPE
  - CVE-2024-21626: runc container escape (Leaky Vessels)
  - CVE-2024-3094:  XZ Utils supply chain backdoor
  - CVE-2025-29927: Next.js middleware authorization bypass
  - CVE-2026-32202: Windows Shell LNK NTLM hash capture

⚠️  For authorized security testing and education only.

Author: KaliAgent Team
Created: April 28, 2026
Version: 1.0.0
"""

import argparse
import sys
import importlib
from pathlib import Path
from datetime import datetime

DEMO_REGISTRY = {
    "CVE-2024-6387": {
        "module": "cve_2024_6387",
        "class": "CVE2024_6387_Demo",
        "description": "OpenSSH regreSSHion Remote Code Execution",
        "severity": "CRITICAL (CVSS 8.1)",
        "actively_exploited": True,
        "cwe": "CWE-362/CWE-479",
        "mitre": "T1190",
    },
    "CVE-2024-1086": {
        "module": "cve_2024_1086",
        "class": "CVE2024_1086_Demo",
        "description": "Linux nftables use-after-free Local Privilege Escalation",
        "severity": "HIGH (CVSS 7.8)",
        "actively_exploited": True,
        "cwe": "CWE-416",
        "mitre": "T1068",
    },
    "CVE-2024-21626": {
        "module": "cve_2024_21626",
        "class": "CVE2024_21626_Demo",
        "description": "runc Container Escape (Leaky Vessels)",
        "severity": "HIGH (CVSS 8.6)",
        "actively_exploited": False,
        "cwe": "CWE-403",
        "mitre": "T1611",
    },
    "CVE-2024-3094": {
        "module": "cve_2024_3094",
        "class": "CVE2024_3094_Demo",
        "description": "XZ Utils Supply Chain Backdoor",
        "severity": "CRITICAL (CVSS 10.0)",
        "actively_exploited": True,
        "cwe": "CWE-1395",
        "mitre": "T1195.002",
    },
    "CVE-2025-29927": {
        "module": "cve_2025_29927",
        "class": "CVE2025_29927_Demo",
        "description": "Next.js Middleware Authorization Bypass",
        "severity": "CRITICAL (CVSS 9.1)",
        "actively_exploited": True,
        "cwe": "CWE-285",
        "mitre": "T1190",
    },
    "CVE-2026-32202": {
        "module": "cve_2026_32202",
        "class": "CVE2026_32202_Demo",
        "description": "Windows Shell LNK NTLM Hash Capture",
        "severity": "MEDIUM (CVSS 4.3)",
        "actively_exploited": True,
        "cwe": "CWE-693",
        "mitre": "T1187",
    },
}


def list_demos():
    """List available CVE demos"""
    print("""
╔═══════════════════════════════════════════════════════════════╗
║  🔓 KaliAgent v4 — CVE Demo Registry                          ║
║     6 CVE Demonstrations Available                              ║
╚════════════════════════════════════════════════════════════════╝
""")
    for cve, info in DEMO_REGISTRY.items():
        exploited = " 🔴 ACTIVE" if info["actively_exploited"] else ""
        print(f"  [{cve}] {info['description']}")
        print(f"    Severity: {info['severity']}{exploited}")
        print(f"    CWE: {info['cwe']} | MITRE: {info['mitre']}")
        print()


def run_demo(cve_id: str, args: list):
    """Run a specific CVE demo"""
    if cve_id not in DEMO_REGISTRY:
        print(f"❌ Unknown CVE: {cve_id}")
        print(f"   Available: {', '.join(DEMO_REGISTRY.keys())}")
        sys.exit(1)

    info = DEMO_REGISTRY[cve_id]
    sys.path.insert(0, str(Path(__file__).parent / "cve_demos"))
    module = importlib.import_module(info["module"])
    demo_class = getattr(module, info["class"])
    demo = demo_class()

    if not args:
        print(f"\n🎯 Running {cve_id}: {info['description']}\n")
        demo.print_attack_flow()
    else:
        sys.argv = [info["module"]] + args
        module.main()


def main():
    parser = argparse.ArgumentParser(
        description="KaliAgent v4 — CVE Demo Integration")
    sub = parser.add_subparsers(dest='command')

    sub.add_parser('list', help='List available CVE demos')

    run = sub.add_parser('run', help='Run a CVE demo')
    run.add_argument('cve', help='CVE identifier (e.g., CVE-2026-32202)')
    run.add_argument('demo_args', nargs='*', help='Arguments for the demo')

    args = parser.parse_args()

    print("""
╔═══════════════════════════════════════════════════════════════╗
║  🔓 KaliAgent v4 — Phase 13: CVE Demo Integration             ║
║     Version 1.0.0 | 6 CVEs | ⚠️ Authorized testing only       ║
╚════════════════════════════════════════════════════════════════╝
""")

    if args.command == 'list':
        list_demos()
    elif args.command == 'run':
        run_demo(args.cve, args.demo_args)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()