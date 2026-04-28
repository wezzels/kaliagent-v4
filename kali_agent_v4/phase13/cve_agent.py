#!/usr/bin/env python3
"""
🎯 KaliAgent v4 - Phase 13: CVE Demo Integration Agent

Provides a unified interface for running CVE demonstration modules
within the KaliAgent framework. Each demo module includes:
- Vulnerability explanation
- Attack flow visualization
- Exploit/payload generation
- Capture/detection server
- Detection and mitigation guidance

Current demos:
  - CVE-2026-32202: Windows Shell LNK NTLM Hash Capture (CWE-693)

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
    "CVE-2026-32202": {
        "module": "cve_2026_32202",
        "class": "CVE2026_32202_Demo",
        "description": "Windows Shell LNK NTLM Hash Capture (CWE-693)",
        "severity": "MEDIUM (CVSS 4.3)",
        "actively_exploited": True,
    },
}


def list_demos():
    """List available CVE demos"""
    print("""
╔═══════════════════════════════════════════════════════════════╗
║  🔓 KaliAgent v4 — CVE Demo Registry                          ║
╚═══════════════════════════════════════════════════════════════╝
""")
    for cve, info in DEMO_REGISTRY.items():
        exploited = " 🔴 ACTIVE" if info["actively_exploited"] else ""
        print(f"  [{cve}] {info['description']}")
        print(f"    Severity: {info['severity']}{exploited}")
        print()


def run_demo(cve_id: str, args: list):
    """Run a specific CVE demo"""
    if cve_id not in DEMO_REGISTRY:
        print(f"❌ Unknown CVE: {cve_id}")
        print(f"   Available: {', '.join(DEMO_REGISTRY.keys())}")
        sys.exit(1)

    info = DEMO_REGISTRY[cve_id]
    module = importlib.import_module(info["module"])
    demo_class = getattr(module, info["class"])
    demo = demo_class()

    if not args:
        # Interactive mode
        print(f"\n🎯 Running {cve_id}: {info['description']}\n")
        demo.print_attack_flow()
    else:
        # Pass args to the demo's main
        sys.argv = [info["module"]] + args
        module.main()


def main():
    parser = argparse.ArgumentParser(
        description="KaliAgent v4 — CVE Demo Integration",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    sub = parser.add_subparsers(dest='command')

    sub.add_parser('list', help='List available CVE demos')

    run = sub.add_parser('run', help='Run a CVE demo')
    run.add_argument('cve', help='CVE identifier (e.g., CVE-2026-32202)')
    run.add_argument('demo_args', nargs='*', help='Arguments for the demo')

    args = parser.parse_args()

    print("""
╔═══════════════════════════════════════════════════════════════╗
║  🔓 KaliAgent v4 — Phase 13: CVE Demo Integration             ║
║     Version 1.0.0                                             ║
╚═══════════════════════════════════════════════════════════════╝
""")

    if args.command == 'list':
        list_demos()
    elif args.command == 'run':
        run_demo(args.cve, args.demo_args)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()