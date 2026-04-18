# KaliAgent Quick Start Guide

Get up and running with KaliAgent in 15 minutes.

---

## 5-Minute Setup

### Prerequisites Check

```bash
# Verify Python 3.10+
python3 --version

# Verify Node.js 18+
node --version

# Verify Kali tools
which nmap nikto sqlmap
```

### Install & Run

```bash
# 1. Install Python dependencies
pip install fastapi uvicorn pydantic reportlab matplotlib

# 2. Install dashboard dependencies
cd kali_dashboard/frontend
npm install

# 3. Start backend API
cd ..
python3 server.py &

# 4. Start frontend
cd frontend
npm run dev

# 5. Open dashboard
# http://localhost:5173
```

---

## Your First Engagement

### Step 1: Create Engagement

**Via Dashboard:**
1. Go to **Engagements** tab
2. Click **New Engagement**
3. Fill in details:
   - Name: `Quick Test`
   - Type: `Reconnaissance`
   - Targets: `scanme.nmap.org` (safe test target)
4. Click **Create**

**Via API:**
```bash
curl -X POST http://localhost:8001/api/engagements \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Quick Test",
    "engagement_type": "reconnaissance",
    "targets": ["scanme.nmap.org"]
  }'
```

### Step 2: Execute Playbook

**Via Dashboard:**
1. Go to **Playbooks** tab
2. Select **Comprehensive Reconnaissance**
3. Enter target: `scanme.nmap.org`
4. Click **Execute**
5. Watch live execution

**Expected Output:**
```
[10:23:45] Nmap → Port scan (1-10000) ✅
[10:24:12] theHarvester → Email/subdomain harvest ✅
[10:24:45] Amass → Subdomain enumeration ✅
[10:25:18] DNSrecon → DNS records ✅
[10:25:52] Nikto → Web server scan ✅

✅ Playbook completed in 2m 7s
📊 5 tools executed
🐛 3 findings discovered
```

### Step 3: View Results

**Via Dashboard:**
1. Go to **Engagements** tab
2. Click on your engagement
3. View:
   - Execution results
   - Findings by severity
   - Tool output logs
   - Generated report

**Via API:**
```bash
# Get results
curl http://localhost:8001/api/engagements/eng-001/results

# Generate report
curl http://localhost:8001/api/engagements/eng-001/report?format=markdown
```

---

## Common Workflows

### 🔍 External Reconnaissance

```bash
curl -X POST http://localhost:8001/api/engagements/eng-001/playbook \
  -H "Content-Type: application/json" \
  -d '{
    "playbook_type": "recon",
    "target": "example.com",
    "domain": "example.com"
  }'
```

**Tools Executed:**
- Nmap (port scan)
- theHarvester (email harvest)
- Amass (subdomain enum)
- DNSrecon (DNS records)
- Nikto (web scan)

**Duration:** 45-90 minutes

---

### 🌐 Web Application Audit

```bash
curl -X POST http://localhost:8001/api/engagements/eng-001/playbook \
  -H "Content-Type: application/json" \
  -d '{
    "playbook_type": "web_audit",
    "url": "https://example.com",
    "target": "example.com"
  }'
```

**Tools Executed:**
- Gobuster (directory brute-force)
- Nikto (web vulnerabilities)
- WPScan (WordPress audit)
- SQLMap (SQL injection)
- SSLScan (TLS config)

**Duration:** 60-120 minutes

---

### 🔐 Password Cracking

```bash
curl -X POST http://localhost:8001/api/engagements/eng-001/playbook \
  -H "Content-Type: application/json" \
  -d '{
    "playbook_type": "password_audit",
    "hash_file": "/path/to/hashes.txt",
    "wordlist": "/usr/share/wordlists/rockyou.txt"
  }'
```

**Tools Executed:**
- Hash-Identifier (identify hash type)
- John the Ripper (dictionary attack)
- Hashcat (GPU brute-force)
- Crunch (wordlist generation)

**Duration:** 30 minutes - 24 hours (varies)

---

### 📡 Wireless Audit

```bash
curl -X POST http://localhost:8001/api/engagements/eng-001/playbook \
  -H "Content-Type: application/json" \
  -d '{
    "playbook_type": "wireless_audit",
    "interface": "wlan0",
    "bssid": "AA:BB:CC:DD:EE:FF"
  }'
```

**Tools Executed:**
- Kismet (network detection)
- Wifite (automated audit)
- Aircrack-ng (WPA crack)
- Reaver (WPS attack)

**Duration:** 30-90 minutes

---

## Generate Professional Report

### PDF Report

```bash
# Generate PDF with charts and graphics
curl -X POST http://localhost:8001/api/engagements/eng-001/report \
  -H "Content-Type: application/json" \
  -d '{
    "format": "pdf",
    "include_charts": true,
    "include_executive_summary": true
  }' \
  --output report.pdf
```

**Report Includes:**
- Executive summary
- Findings pie chart
- Tool execution table
- Detailed findings
- Remediation recommendations
- Appendix with full output

### Markdown Report

```bash
curl http://localhost:8001/api/engagements/eng-001/report?format=markdown \
  > report.md
```

### JSON Report

```bash
curl http://localhost:8001/api/engagements/eng-001/report?format=json \
  > report.json
```

---

## Safety First!

### Configure IP Whitelist

**Before running any scans, configure your whitelist:**

```bash
curl -X POST http://localhost:8001/api/safety \
  -H "Content-Type: application/json" \
  -d '{
    "whitelist": ["192.168.1.0/24", "10.0.0.0/8"],
    "blacklist": ["8.8.8.8", "1.1.1.1"]
  }'
```

### Set Authorization Level

```bash
# BASIC - Reconnaissance only
curl -X POST http://localhost:8001/api/authorization \
  -H "Content-Type: application/json" \
  -d '{"level": "BASIC"}'

# ADVANCED - Exploitation tools
curl -X POST http://localhost:8001/api/authorization \
  -H "Content-Type: application/json" \
  -d '{"level": "ADVANCED"}'

# CRITICAL - Full access
curl -X POST http://localhost:8001/api/authorization \
  -H "Content-Type: application/json" \
  -d '{"level": "CRITICAL"}'
```

### Enable Dry-Run Mode (Testing)

```bash
# Test without actual execution
curl -X POST http://localhost:8001/api/safety \
  -H "Content-Type: application/json" \
  -d '{
    "dry_run": true,
    "safe_mode": true
  }'
```

---

## Dashboard Quick Reference

### Pages

| Page | Purpose | URL |
|------|---------|-----|
| **Dashboard** | Overview, stats, quick actions | `/` |
| **Engagements** | Create/manage engagements | `/engagements` |
| **Playbooks** | Execute automated workflows | `/playbooks` |
| **Tools** | Browse 52 available tools | `/tools` |
| **Settings** | Configure safety & auth | `/settings` |
| **Live Monitor** | Real-time execution tracking | `/monitor` |

### Keyboard Shortcuts

- `Ctrl+K` - Quick search
- `Ctrl+N` - New engagement
- `Ctrl+R` - Refresh data
- `Esc` - Close modals

---

## API Quick Reference

### Engagements

```bash
# List all
GET /api/engagements

# Create
POST /api/engagements
{
  "name": "My Engagement",
  "type": "penetration_test",
  "targets": ["192.168.1.0/24"]
}

# Get details
GET /api/engagements/{id}

# Execute playbook
POST /api/engagements/{id}/playbook
{
  "playbook_type": "recon",
  "target": "192.168.1.100"
}

# Get results
GET /api/engagements/{id}/results

# Generate report
GET /api/engagements/{id}/report?format=pdf
```

### Tools

```bash
# List all
GET /api/tools

# List by category
GET /api/tools?category=web_application

# Get categories
GET /api/categories
```

### Safety

```bash
# Get current config
GET /api/safety

# Update config
POST /api/safety
{
  "whitelist": ["192.168.1.0/24"],
  "blacklist": ["8.8.8.8"]
}

# Get authorization
GET /api/authorization

# Set authorization
POST /api/authorization
{
  "level": "BASIC"
}
```

---

## Next Steps

### Learn More
- 📖 [Installation Guide](INSTALL.md) - Full installation instructions
- 📚 [User Guide](USER_GUIDE.md) - Detailed usage documentation
- 🔧 [API Reference](http://localhost:8001/docs) - Interactive API docs
- 🛡️ [Security Guide](SECURITY.md) - Safety best practices

### Advanced Features
- Metasploit integration
- RedTeam autonomous engagements
- Custom playbook creation
- PDF report customization
- Email report delivery

### Get Help
- Check logs: `/tmp/kali-dashboard/logs/`
- API docs: `http://localhost:8001/docs`
- GitHub Issues: Report bugs
- Discord: Community support

---

*Happy (Safe) Hacking! 🍀*

*Last Updated: April 18, 2026*
