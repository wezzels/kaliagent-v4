#!/usr/bin/env python3
"""
KaliAgent v4 - Demo Recorder
Creates animated terminal demos as ASCII art / text files
Can be converted to GIFs later or embedded as code blocks
"""

import os
import time
from datetime import datetime

OUTPUT_DIR = "./recordings/demos"
os.makedirs(OUTPUT_DIR, exist_ok=True)


def type_writer(text, delay=0.03):
    """Simulate typing effect"""
    for char in text:
        print(char, end='', flush=True)
        time.sleep(delay)
    print()


def create_demo_file(filename: str, content: str):
    """Save demo to file"""
    filepath = os.path.join(OUTPUT_DIR, filename)
    with open(filepath, 'w') as f:
        f.write(content)
    print(f"✅ Created: {filepath}")
    return filepath


def demo_dashboard():
    """Demo 1: Dashboard Startup"""
    content = """
╔═══════════════════════════════════════════════════════════════╗
║  🍀 KALIAGENT V4 - DASHBOARD STARTUP                          ║
╚═══════════════════════════════════════════════════════════════╝

$ python phase6/dashboard_v2.py

🍀 Starting KaliAgent v4 Dashboard v2...
📊 Access: http://localhost:5007

[2026-04-24 06:00:00] Initializing dashboard...
[2026-04-24 06:00:01] ✅ Connected to Redis (port 6379)
[2026-04-24 06:00:02] ✅ Connected to Ollama (port 11434)
[2026-04-24 06:00:03] ✅ Sliver C2 active (port 8888)
[2026-04-24 06:00:03] ✅ Empire C2 active (port 1337)
[2026-04-24 06:00:04] ✅ Enhanced C2 active (port 8889)
[2026-04-24 06:00:05] ✅ Lab network verified (10.0.100.0/24)

╔═══════════════════════════════════════════════════════════════╗
║  📊 SYSTEM STATS                                              ║
╠═══════════════════════════════════════════════════════════════╣
║  CPU Usage:     ████████░░░░░░░░░░░░  23.5%                  ║
║  Memory Usage:  ██████████████░░░░░░  45.2%                  ║
║  Disk Usage:    ████████████████████░░  67.8%                ║
║  Network RX:    1024.5 KB/s                                  ║
║  Network TX:    512.3 KB/s                                   ║
╚═══════════════════════════════════════════════════════════════╝

🎉 Dashboard ready! Access: http://localhost:5007
"""
    return create_demo_file("01_dashboard_startup.txt", content)


def demo_network_scan():
    """Demo 2: Network Scan"""
    content = """
╔═══════════════════════════════════════════════════════════════╗
║  🔍 KALIAGENT V4 - NETWORK SCAN                               ║
╚═══════════════════════════════════════════════════════════════╝

$ ./kaliagent scan -t 10.0.100.0/24 --type nmap

🔍 Starting nmap scan on 10.0.100.0/24...

Scan Progress:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

[████░░░░░░░░░░░░░░░░░░░░] 20% - Host discovery
  → 10.0.100.1 (Gateway)
  → 10.0.100.10 (Juice Shop)
  → 10.0.100.20 (Windows Target)
  → 10.0.100.30 (Linux Target)

[████████░░░░░░░░░░░░░░░░] 40% - Port scanning
  → 23 open ports discovered

[████████████░░░░░░░░░░░░] 60% - Service detection
  → SSH (22), HTTP (80), HTTPS (443)
  → SMB (445), RDP (3389)

[████████████████░░░░░░░░] 80% - OS detection
  → Ubuntu 16.04 (10.0.100.10)
  → Windows Server 2016 (10.0.100.20)
  → Ubuntu 14.04 (10.0.100.30)

[████████████████████████] 100% - Complete!

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📊 SCAN RESULTS:

  Hosts Discovered:      5
  Open Ports:           23
  Services Identified:  47
  Vulnerabilities:      12

⚠️  CRITICAL FINDINGS:
  • MS17-010 (EternalBlue) - 10.0.100.20
  • SQL Injection - 10.0.100.10:3000
  • Outdated Apache 2.4.18 - 10.0.100.10

💾 Results saved to: scans/scan_20260424_060500.json
"""
    return create_demo_file("02_network_scan.txt", content)


def demo_sql_injection():
    """Demo 3: SQL Injection Attack"""
    content = """
╔═══════════════════════════════════════════════════════════════╗
║  💉 KALIAGENT V4 - SQL INJECTION ATTACK                       ║
╚═══════════════════════════════════════════════════════════════╝

$ ./kaliagent attack -t 10.0.100.10 -a web --method sql_injection

⚔️  Launching web attack on 10.0.100.10...
🎯 Target: OWASP Juice Shop (port 3000)

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

STEP 1/5: Reconnaissance
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
[✓] Nmap scan confirmed web server
[✓] Technology stack identified:
    • Framework: Angular
    • Server: Apache 2.4.18
    • Database: SQLite

STEP 2/5: Vulnerability Detection
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
[✓] SQLMap scan initiated
[✓] Testing GET parameters...
[✓] Testing POST parameters...
[!] VULNERABILITY FOUND!
    Location: /rest/user/authentication
    Parameter: username
    Type: Boolean-based blind SQL injection

STEP 3/5: Exploitation
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
[✓] Crafting payload: admin'--
[✓] Sending request...
[!] AUTHENTICATION BYPASSED!
    Logged in as: admin@juice-sh.op
    Role: Administrator

STEP 4/5: Post-Exploitation
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
[✓] Dumping database...
[✓] Extracting users table...
[!] 127 user records found!
    • admin@juice-sh.op (password hash extracted)
    • jim@juice-sh.op
    • bender@juice-sh.op
    • (124 more...)

[✓] Extracting products table...
[✓] Extracting orders table...

STEP 5/5: Evidence Collection
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
[✓] Screenshot captured
[✓] Request/response logs saved
[✓] Database dump exported

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

🎉 ATTACK SUCCESSFUL!

Summary:
  • Target: 10.0.100.10:3000
  • Vulnerability: SQL Injection (CVSS 9.8)
  • Access Gained: Administrator
  • Data Exfiltrated: 127 user records

💾 Evidence saved to: evidence/sqli_20260424_061000/
📄 Report updated: reports/pentest_report_20260424.pdf
"""
    return create_demo_file("03_sql_injection.txt", content)


def demo_report_generation():
    """Demo 4: Report Generation"""
    content = """
╔═══════════════════════════════════════════════════════════════╗
║  📄 KALIAGENT V4 - PROFESSIONAL REPORT GENERATION             ║
╚═══════════════════════════════════════════════════════════════╝

$ ./kaliagent report -f pdf --output ./reports

📄 Generating penetration test report...

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

[1/7] Executive Summary
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
[✓] Analyzing attack results...
[✓] Generating risk assessment...
[✓] Writing executive overview...
    → 15 vulnerabilities discovered
    → 2 Critical, 5 High, 8 Medium
    → Immediate action recommended

[2/7] Scope of Engagement
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
[✓] Documenting target scope...
[✓] Listing in-scope systems...
[✓] Defining rules of engagement...

[3/7] Methodology
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
[✓] OSSTMM compliance verified
[✓] Tools documented
[✓] Techniques catalogued

[4/7] Detailed Findings
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
[✓] Finding #1: SQL Injection (Critical)
[✓] Finding #2: EternalBlue (Critical)
[✓] Finding #3: Outdated Apache (High)
[✓] Finding #4: Weak Credentials (High)
[✓] Finding #5-15: (Medium/Low)

[5/7] Evidence
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
[✓] Including 23 screenshots
[✓] Attacking request/response logs
[✓] Embedding network diagrams

[6/7] Remediation Recommendations
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
[✓] Prioritized by risk level
[✓] Step-by-step fix instructions
[✓] Estimated effort for each

[7/7] CVSS Scoring & Conclusion
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
[✓] Calculating CVSS 3.1 scores
[✓] Writing conclusion
[✓] Final review...

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

🎉 REPORT GENERATION COMPLETE!

Generated Files:
  📄 PDF:  reports/pentest_report_20260424_061500.pdf (2.4 MB, 47 pages)
  🌐 HTML: reports/pentest_report_20260424_061500.html (856 KB)
  📊 JSON: reports/pentest_report_20260424_061500.json (124 KB)

Preview:
╔═══════════════════════════════════════════════════════════════╗
║  PENETRATION TEST REPORT                                      ║
║  Client: Internal Security Assessment                         ║
║  Date: April 24, 2026                                         ║
╠═══════════════════════════════════════════════════════════════╣
║  EXECUTIVE SUMMARY                                            ║
║  This assessment identified 15 security vulnerabilities...    ║
╚═══════════════════════════════════════════════════════════════╝
"""
    return create_demo_file("04_report_generation.txt", content)


def demo_ai_command():
    """Demo 5: AI Natural Language Command"""
    content = """
╔═══════════════════════════════════════════════════════════════╗
║  🤖 KALIAGENT V4 - AI NATURAL LANGUAGE COMMAND                ║
╚═══════════════════════════════════════════════════════════════╝

$ ./kaliagent ai "Find all web servers in 10.0.100.0/24 and check for SQL injection"

🤖 Processing natural language command...

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

🧠 AI ANALYSIS:

Input: "Find all web servers in 10.0.100.0/24 and check for SQL injection"

Parsed Intent:
  • Action: scan + attack
  • Target Range: 10.0.100.0/24
  • Filter: Web servers (port 80, 443)
  • Attack Type: SQL injection

Recommended Plan:
  1. Scan 10.0.100.0/24 for ports 80,443
  2. Identify web servers
  3. Run SQLMap on each target
  4. Prioritize by vulnerability severity

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Executing Plan...

[1/4] Scanning for web servers...
  ✓ Found: 10.0.100.10:3000 (Juice Shop)
  ✓ Found: 10.0.100.10:80 (Apache)
  ✓ Found: 10.0.100.20:80 (IIS)

[2/4] Analyzing technologies...
  ✓ Juice Shop: Angular + SQLite (High probability of SQLi)
  ✓ Apache 2.4.18: PHP + MySQL (Medium probability)
  ✓ IIS: ASP.NET (Low probability)

[3/4] Running SQLMap on high-priority targets...
  ✓ Testing 10.0.100.10:3000...
  [!] VULNERABLE! Boolean-based SQL injection confirmed
  
  ✓ Testing 10.0.100.10:80...
  [!] VULNERABLE! Error-based SQL injection confirmed

[4/4] Generating report...
  ✓ Documenting findings
  ✓ Calculating CVSS scores
  ✓ Writing remediation steps

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

🎉 AI COMMAND COMPLETE!

Results:
  • Web Servers Found: 3
  • SQL Injection Vulnerabilities: 2
  • Risk Level: CRITICAL

AI Recommendation:
  "Immediate patching required for 10.0.100.10. Both web 
   applications are vulnerable to SQL injection, allowing 
   complete database compromise."

💾 Full report: reports/ai_scan_20260424_062000.pdf
"""
    return create_demo_file("05_ai_natural_language.txt", content)


def create_all_demos():
    """Create all demo files"""
    print("🍀 KaliAgent v4 - Creating Demo Recordings")
    print("=" * 60)
    print()
    
    demos = [
        ("Dashboard Startup", demo_dashboard),
        ("Network Scan", demo_network_scan),
        ("SQL Injection Attack", demo_sql_injection),
        ("Report Generation", demo_report_generation),
        ("AI Natural Language", demo_ai_command),
    ]
    
    for name, func in demos:
        print(f"📝 Creating: {name}")
        func()
        print()
    
    print("=" * 60)
    print("✅ All demo recordings created!")
    print()
    print(f"Output directory: {OUTPUT_DIR}/")
    print()
    print("Files created:")
    for f in sorted(os.listdir(OUTPUT_DIR)):
        filepath = os.path.join(OUTPUT_DIR, f)
        size = os.path.getsize(filepath)
        print(f"  📄 {f} ({size:,} bytes)")
    print()
    print("💡 Tip: These can be converted to GIFs or embedded in docs!")


if __name__ == "__main__":
    create_all_demos()
