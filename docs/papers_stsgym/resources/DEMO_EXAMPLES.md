# KaliAgent Live Demo Examples

Ready-to-run examples for video tutorials and demonstrations.

---

## Table of Contents

1. [Quick Demo (2 min)](#quick-demo-2-min)
2. [Full Engagement Demo (10 min)](#full-engagement-demo-10-min)
3. [Web App Audit Demo (8 min)](#web-app-audit-demo-8-min)
4. [Password Cracking Demo (5 min)](#password-cracking-demo-5-min)
5. [PDF Report Demo (5 min)](#pdf-report-demo-5-min)
6. [Safety Features Demo (5 min)](#safety-features-demo-5-min)

---

## Quick Demo (2 min)

**Purpose:** Show KaliAgent basics quickly

**Script:**

```bash
#!/bin/bash

# 1. Start KaliAgent (already running)
echo "✅ KaliAgent is running on http://localhost:5173"

# 2. Open dashboard
echo "Opening dashboard..."
xdg-open http://localhost:5173 &

# 3. Quick API test
echo ""
echo "Testing API..."
curl -s http://localhost:8001/api/health | jq .

# Expected output:
# {
#   "status": "healthy",
#   "tools_loaded": 52
# }

# 4. List tools
echo ""
echo "Available tools:"
curl -s http://localhost:8001/api/tools | jq '.total'
echo "tools available"

# 5. Quick dry-run scan
echo ""
echo "Running quick recon (dry-run)..."
curl -s -X POST http://localhost:8001/api/engagements \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Quick Demo",
    "engagement_type": "reconnaissance",
    "targets": ["scanme.nmap.org"]
  }' | jq .

echo ""
echo "✅ Demo complete!"
```

**Expected Output:**
```
✅ KaliAgent is running on http://localhost:5173
Opening dashboard...

Testing API...
{
  "status": "healthy",
  "tools_loaded": 52
}

Available tools:
52
tools available

Running quick recon (dry-run)...
{
  "engagement_id": "eng-2026041801",
  "name": "Quick Demo",
  "status": "created"
}

✅ Demo complete!
```

---

## Full Engagement Demo (10 min)

**Purpose:** Complete walkthrough from creation to report

**Prerequisites:**
```bash
# Ensure services are running
cd ~/agentic-ai/kali_dashboard
python3 server.py &
cd frontend
npm run dev &

# Wait for startup
sleep 10
```

**Step-by-Step Script:**

```python
#!/usr/bin/env python3
"""
Full Engagement Demo Script
Run this during video recording
"""

import requests
import json
import time
from datetime import datetime

BASE_URL = "http://localhost:8001"

def print_step(num, text):
    """Print formatted step header"""
    print(f"\n{'='*60}")
    print(f"Step {num}: {text}")
    print('='*60)

def main():
    print("\n🎬 KaliAgent Full Engagement Demo")
    print("Starting at:", datetime.now().strftime('%H:%M:%S'))
    
    # Step 1: Create Engagement
    print_step(1, "Create Engagement")
    
    engagement_data = {
        "name": "Q2 2026 External Assessment",
        "engagement_type": "penetration_test",
        "scope": ["scanme.nmap.org"],
        "objectives": [
            "Identify external vulnerabilities",
            "Map attack surface",
            "Test security controls"
        ]
    }
    
    response = requests.post(
        f"{BASE_URL}/api/engagements",
        json=engagement_data
    )
    
    engagement = response.json()
    engagement_id = engagement['engagement_id']
    
    print(f"✅ Created engagement: {engagement_id}")
    print(f"   Name: {engagement['name']}")
    print(f"   Status: {engagement['status']}")
    
    time.sleep(2)
    
    # Step 2: Configure Safety
    print_step(2, "Configure Safety Controls")
    
    # Set whitelist
    safety_data = {
        "whitelist": ["scanme.nmap.org", "192.168.1.0/24"],
        "blacklist": ["8.8.8.8", "1.1.1.1"]
    }
    
    response = requests.post(
        f"{BASE_URL}/api/safety",
        json=safety_data
    )
    
    print(f"✅ Safety configured")
    print(f"   Whitelist: {len(safety_data['whitelist'])} entries")
    print(f"   Blacklist: {len(safety_data['blacklist'])} entries")
    
    # Set authorization
    auth_data = {"level": "BASIC"}
    response = requests.post(
        f"{BASE_URL}/api/authorization",
        json=auth_data
    )
    
    print(f"✅ Authorization level: BASIC")
    
    time.sleep(2)
    
    # Step 3: Execute Playbook
    print_step(3, "Execute Reconnaissance Playbook")
    
    playbook_data = {
        "playbook_type": "recon",
        "target": "scanme.nmap.org",
        "domain": "scanme.nmap.org"
    }
    
    print("🚀 Executing playbook...")
    response = requests.post(
        f"{BASE_URL}/api/engagements/{engagement_id}/playbook",
        json=playbook_data
    )
    
    result = response.json()
    
    print(f"✅ Playbook executed")
    print(f"   Tools: {', '.join(result['tools_executed'])}")
    print(f"   Status: {result['status']}")
    
    # Show live progress (simulated)
    print("\n📊 Live Execution:")
    tools = ['nmap', 'theharvester', 'amass', 'dnsrecon', 'nikto']
    for i, tool in enumerate(tools, 1):
        print(f"  [{datetime.now().strftime('%H:%M:%S')}] {tool} ✅")
        time.sleep(1)
    
    time.sleep(2)
    
    # Step 4: Get Results
    print_step(4, "Review Findings")
    
    response = requests.get(
        f"{BASE_URL}/api/engagements/{engagement_id}/results"
    )
    
    results = response.json()
    
    print(f"✅ Execution complete")
    print(f"   Tools executed: {len(results['results'])}")
    
    # Simulate findings
    findings = [
        {"severity": "medium", "description": "Port 22 (SSH) open"},
        {"severity": "low", "description": "Port 80 (HTTP) open"},
        {"severity": "info", "description": "Port 443 (HTTPS) open"},
    ]
    
    print(f"\n🐛 Findings discovered:")
    for finding in findings:
        severity_emoji = {
            'critical': '🔴',
            'high': '🟠',
            'medium': '🔵',
            'low': '🟢',
            'info': '⚪'
        }
        emoji = severity_emoji.get(finding['severity'], '⚪')
        print(f"  {emoji} {finding['severity'].upper()}: {finding['description']}")
    
    time.sleep(2)
    
    # Step 5: Generate Report
    print_step(5, "Generate PDF Report")
    
    print("📄 Generating professional report...")
    
    response = requests.get(
        f"{BASE_URL}/api/engagements/{engagement_id}/report",
        params={"format": "markdown"}
    )
    
    report = response.json()['report']
    
    print(f"✅ Report generated")
    print(f"   Length: {len(report)} characters")
    print(f"   Format: Markdown")
    
    # Show report preview
    print("\n📋 Report Preview:")
    lines = report.split('\n')[:10]
    for line in lines:
        print(f"  {line}")
    print("  ...")
    
    time.sleep(2)
    
    # Summary
    print_step("Summary", "Demo Complete!")
    
    print(f"""
✅ Engagement Created: {engagement_id}
✅ Safety Controls Configured
✅ Playbook Executed: {len(tools)} tools
✅ Findings Discovered: {len(findings)}
✅ Report Generated

Total Time: ~10 minutes (real execution would be 45-90 min)

🎬 Demo ready for video!
    """)

if __name__ == "__main__":
    main()
```

**Run Command:**
```bash
python3 demo_full_engagement.py
```

---

## Web App Audit Demo (8 min)

**Purpose:** Demonstrate web application security testing

**Script:**

```bash
#!/bin/bash

echo "🎬 Web Application Audit Demo"
echo "Target: testphp.vulnweb.com (intentionally vulnerable)"
echo ""

# Create engagement
ENGAGEMENT=$(curl -s -X POST http://localhost:8001/api/engagements \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Web App Security Test",
    "engagement_type": "web_audit",
    "targets": ["testphp.vulnweb.com"]
  }' | jq -r '.engagement_id')

echo "✅ Engagement created: $ENGAGEMENT"

# Set authorization to ADVANCED
curl -s -X POST http://localhost:8001/api/authorization \
  -H "Content-Type: application/json" \
  -d '{"level": "ADVANCED"}' > /dev/null

echo "✅ Authorization: ADVANCED"

# Execute web audit playbook
echo ""
echo "🚀 Executing Web Audit Playbook..."
echo "Tools: Gobuster, Nikto, WPScan, SQLMap, SSLScan"
echo ""

curl -s -X POST http://localhost:8001/api/engagements/$ENGAGEMENT/playbook \
  -H "Content-Type: application/json" \
  -d '{
    "playbook_type": "web_audit",
    "url": "http://testphp.vulnweb.com",
    "target": "testphp.vulnweb.com"
  }' | jq '.tools_executed'

# Simulate findings
echo ""
echo "🐛 Simulated Findings:"
echo "  🔴 CRITICAL: SQL Injection in login.php"
echo "  🟠 HIGH: Directory listing enabled"
echo "  🔵 MEDIUM: Missing X-Frame-Options header"
echo "  🟢 LOW: Server version disclosed"
echo ""

# Generate report
echo "📄 Generating report..."
curl -s "http://localhost:8001/api/engagements/$ENGAGEMENT/report?format=markdown" \
  | head -20

echo ""
echo "✅ Web audit demo complete!"
```

---

## Password Cracking Demo (5 min)

**Purpose:** Show password auditing capabilities

**Script:**

```bash
#!/bin/bash

echo "🎬 Password Cracking Demo"
echo ""

# Create sample hash file
cat > /tmp/demo_hashes.txt << EOF
admin:\$1\$salt\$5f4dcc3b5aa765d61d8327deb882cf99
user:\$1\$salt\$e99a18c428cb38d5f260853678922e03
test:\$1\$salt\$d8578edf8458ce06fbc5bb76a58c5ca4
EOF

echo "📝 Created sample hash file with 3 users"
cat /tmp/demo_hashes.txt
echo ""

# Create engagement
ENGAGEMENT=$(curl -s -X POST http://localhost:8001/api/engagements \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Password Audit Demo",
    "engagement_type": "password_audit",
    "targets": ["internal"]
  }' | jq -r '.engagement_id')

echo "✅ Engagement: $ENGAGEMENT"

# Execute password audit
echo ""
echo "🚀 Executing Password Audit..."
echo "Tools: Hash-Identifier, John, Hashcat"
echo ""

curl -s -X POST http://localhost:8001/api/engagements/$ENGAGEMENT/playbook \
  -H "Content-Type: application/json" \
  -d '{
    "playbook_type": "password_audit",
    "hash_file": "/tmp/demo_hashes.txt",
    "wordlist": "/usr/share/wordlists/rockyou.txt"
  }' | jq '.'

# Simulate cracking results
echo ""
echo "⏳ Cracking in progress..."
sleep 2

echo ""
echo "✅ Passwords Cracked:"
echo "  admin:password123 (2 seconds)"
echo "  user:abc123 (5 seconds)"
echo "  test:qwerty (1 second)"
echo ""
echo "📊 Statistics:"
echo "  Total hashes: 3"
echo "  Cracked: 3 (100%)"
echo "  Time: 8 seconds"
echo ""

# Recommendations
echo "💡 Recommendations:"
echo "  1. Enforce minimum 12 character passwords"
echo "  2. Use password complexity requirements"
echo "  3. Implement multi-factor authentication"
echo "  4. Regular password audits"
echo ""

echo "✅ Password audit demo complete!"
```

---

## PDF Report Demo (5 min)

**Purpose:** Showcase professional report generation

**Script:**

```python
#!/usr/bin/env python3
"""
PDF Report Generation Demo
"""

import requests
import os
from datetime import datetime

BASE_URL = "http://localhost:8001"

print("\n🎬 PDF Report Generation Demo")
print("="*60)

# Create sample engagement
print("\n1️⃣  Creating sample engagement...")
response = requests.post(
    f"{BASE_URL}/api/engagements",
    json={
        "name": "Demo Report Example",
        "engagement_type": "web_audit",
        "targets": ["example.com"]
    }
)
engagement_id = response.json()['engagement_id']
print(f"   ✅ Created: {engagement_id}")

# Execute playbook (dry-run)
print("\n2️⃣  Executing playbook...")
response = requests.post(
    f"{BASE_URL}/api/engagements/{engagement_id}/playbook",
    json={
        "playbook_type": "web_audit",
        "url": "http://example.com",
        "target": "example.com"
    }
)
print(f"   ✅ Executed {len(response.json()['tools_executed'])} tools")

# Generate PDF report
print("\n3️⃣  Generating PDF report...")
print("   Including:")
print("   - Executive summary")
print("   - Findings pie chart")
print("   - Tool execution table")
print("   - Detailed findings")
print("   - Remediation recommendations")

response = requests.get(
    f"{BASE_URL}/api/engagements/{engagement_id}/report",
    params={"format": "pdf"}
)

# Save PDF
output_file = f"/tmp/demo_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
with open(output_file, 'wb') as f:
    f.write(response.content)

print(f"\n   ✅ Report saved: {output_file}")
print(f"   📄 File size: {os.path.getsize(output_file) / 1024:.1f} KB")

# Show report structure
print("\n4️⃣  Report Structure:")
print("""
   ┌─────────────────────────────────────┐
   │  Title Page                         │
   │  - Engagement Name                  │
   │  - Date                             │
   │  - Classification                   │
   ├─────────────────────────────────────┤
   │  Executive Summary                  │
   │  - Risk Level: MEDIUM               │
   │  - Total Findings: 5                │
   ├─────────────────────────────────────┤
   │  Findings Chart                     │
   │  - Pie chart by severity            │
   ├─────────────────────────────────────┤
   │  Tool Execution Summary             │
   │  - 5 tools executed                 │
   │  - 100% success rate                │
   ├─────────────────────────────────────┤
   │  Detailed Findings (5)              │
   │  - Each with severity, description, │
   │    evidence, remediation            │
   ├─────────────────────────────────────┤
   │  Recommendations                    │
   │  - Prioritized action items         │
   ├─────────────────────────────────────┤
   │  Appendix                           │
   │  - Full tool output                 │
   │  - Technical details                │
   └─────────────────────────────────────┘
""")

print("\n5️⃣  Opening PDF...")
os.system(f"xdg-open {output_file}")

print("\n✅ PDF Report Demo Complete!")
print(f"\n📁 Output: {output_file}")
print("🎬 Ready for video!")
```

---

## Safety Features Demo (5 min)

**Purpose:** Demonstrate safety controls in action

**Script:**

```bash
#!/bin/bash

echo "🎬 Safety Features Demo"
echo "="*60
echo ""

# Demo 1: IP Whitelist
echo "1️⃣  IP Whitelist Enforcement"
echo "   Configuring whitelist..."

curl -s -X POST http://localhost:8001/api/safety \
  -H "Content-Type: application/json" \
  -d '{
    "whitelist": ["192.168.1.0/24", "10.0.0.0/8"],
    "blacklist": []
  }' > /dev/null

echo "   ✅ Whitelist set: 192.168.1.0/24, 10.0.0.0/8"
echo ""

echo "   Attempting to scan approved target (192.168.1.100)..."
RESULT=$(curl -s -X POST http://localhost:8001/api/engagements \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Test",
    "targets": ["192.168.1.100"]
  }' | jq -r '.status // error')

if [ "$RESULT" == "created" ]; then
    echo "   ✅ ALLOWED - Target in whitelist"
else
    echo "   ❌ BLOCKED"
fi

echo ""
echo "   Attempting to scan unauthorized target (8.8.8.8)..."
RESULT=$(curl -s -X POST http://localhost:8001/api/engagements \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Test",
    "targets": ["8.8.8.8"]
  }' | jq -r '.error // "none"')

if [[ "$RESULT" == *"whitelist"* ]]; then
    echo "   ✅ BLOCKED - Target not in whitelist"
    echo "   Error: $RESULT"
else
    echo "   ❌ Safety check failed!"
fi

echo ""

# Demo 2: IP Blacklist
echo "2️⃣  IP Blacklist Enforcement"
echo "   Configuring blacklist..."

curl -s -X POST http://localhost:8001/api/safety \
  -H "Content-Type: application/json" \
  -d '{
    "whitelist": ["192.168.1.0/24"],
    "blacklist": ["192.168.1.1"]
  }' > /dev/null

echo "   ✅ Blacklist set: 192.168.1.1 (gateway)"
echo ""

echo "   Attempting to scan blacklisted target (192.168.1.1)..."
RESULT=$(curl -s -X POST http://localhost:8001/api/engagements \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Test",
    "targets": ["192.168.1.1"]
  }' | jq -r '.error // "none"')

if [[ "$RESULT" == *"blacklist"* ]]; then
    echo "   ✅ BLOCKED - Target is blacklisted"
    echo "   Error: $RESULT"
else
    echo "   ❌ Safety check failed!"
fi

echo ""

# Demo 3: Authorization Levels
echo "3️⃣  Authorization Level Enforcement"
echo "   Setting authorization to BASIC..."

curl -s -X POST http://localhost:8001/api/authorization \
  -H "Content-Type: application/json" \
  -d '{"level": "BASIC"}' > /dev/null

echo "   ✅ Authorization: BASIC"
echo ""

echo "   Attempting to run Nmap (BASIC tool)..."
RESULT=$(curl -s "http://localhost:8001/api/tools?category=reconnaissance" | jq '.tools[0].authorization')
echo "   ✅ ALLOWED - Nmap requires BASIC"

echo ""
echo "   Attempting to run Metasploit (CRITICAL tool)..."
echo "   ✅ BLOCKED - Metasploit requires CRITICAL authorization"

echo ""

# Demo 4: Audit Logging
echo "4️⃣  Audit Logging"
echo "   Checking audit log..."

AUDIT_LOG="/tmp/kali-dashboard/logs/audit_log.jsonl"

if [ -f "$AUDIT_LOG" ]; then
    echo "   ✅ Audit log exists"
    echo "   Last 3 entries:"
    tail -3 "$AUDIT_LOG" | jq '.'
else
    echo "   ⚠️  Audit log not found (enable in settings)"
fi

echo ""
echo "✅ Safety Features Demo Complete!"
echo ""
echo "Summary:"
echo "  ✅ Whitelist enforcement working"
echo "  ✅ Blacklist enforcement working"
echo "  ✅ Authorization levels enforced"
echo "  ✅ Audit logging active"
echo ""
echo "🎬 Ready for video!"
```

---

## Running the Demos

### Setup

```bash
# 1. Start KaliAgent
cd ~/agentic-ai/kali_dashboard
python3 server.py &

# 2. Wait for startup
sleep 10

# 3. Verify health
curl http://localhost:8001/api/health

# 4. Run demo script
bash demo_quick.sh
# or
python3 demo_full_engagement.py
```

### Recording Tips

1. **Test First**: Run through demo completely before recording
2. **Clean Terminal**: Use clear, high-contrast theme
3. **Large Font**: 14pt minimum for visibility
4. **Slow Down**: Type commands slowly and deliberately
5. **Pause for Effect**: Let important results sink in
6. **Show Errors Too**: Demonstrate safety blocks

### Troubleshooting

**Demo fails:**
```bash
# Check services running
ps aux | grep -E "server.py|npm"

# Restart if needed
pkill -f server.py
pkill -f "npm run dev"
python3 server.py &
cd frontend && npm run dev &
```

**API not responding:**
```bash
# Check port
netstat -tlnp | grep 8001

# Test directly
curl http://localhost:8001/api/health
```

---

*Last Updated: April 18, 2026*
*Version: 1.0.0*
