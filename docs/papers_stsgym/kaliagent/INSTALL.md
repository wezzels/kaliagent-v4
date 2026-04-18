# KaliAgent Installation Guide

Complete installation instructions for KaliAgent security automation platform.

---

## Table of Contents

- [Prerequisites](#prerequisites)
- [System Requirements](#system-requirements)
- [Quick Install](#quick-install)
- [Detailed Installation](#detailed-installation)
- [Kali Linux Tools Setup](#kali-linux-tools-setup)
- [Metasploit Configuration](#metasploit-configuration)
- [Dashboard Installation](#dashboard-installation)
- [Verification](#verification)
- [Troubleshooting](#troubleshooting)

---

## Prerequisites

### Required
- **Operating System**: Kali Linux 2024.x+ (recommended) or Ubuntu 22.04+
- **Python**: 3.10 or higher
- **Node.js**: 18.x or higher (for web dashboard)
- **Kali Tools**: Standard Kali Linux toolset

### Optional (for full features)
- **Metasploit Framework**: For exploitation features
- **PostgreSQL**: For Metasploit database
- **Redis**: For task queuing (future feature)

---

## System Requirements

| Component | Minimum | Recommended |
|-----------|---------|-------------|
| **CPU** | 4 cores | 8+ cores |
| **RAM** | 8 GB | 16+ GB |
| **Storage** | 20 GB | 50+ GB SSD |
| **Network** | 1 Gbps | 1 Gbps+ |

---

## Quick Install

```bash
# Clone repository
git clone https://github.com/wezzels/agentic-ai.git
cd agentic-ai

# Install Python dependencies
pip install -r requirements.txt

# Install dashboard dependencies
cd kali_dashboard/frontend
npm install

# Verify installation
cd ../..
python3 -m pytest tests/test_kali_agent.py -v

# Start dashboard (development)
cd kali_dashboard
python3 server.py &
cd frontend
npm run dev
```

**Access Dashboard:** http://localhost:5173

---

## Detailed Installation

### Step 1: System Preparation

```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install system dependencies
sudo apt install -y \
    python3 \
    python3-pip \
    python3-venv \
    nodejs \
    npm \
    git \
    curl \
    wget
```

### Step 2: Create Virtual Environment

```bash
cd ~/agentic-ai

# Create virtual environment
python3 -m venv venv

# Activate virtual environment
source venv/bin/activate

# Upgrade pip
pip install --upgrade pip
```

### Step 3: Install Python Dependencies

```bash
# Install core dependencies
pip install -r requirements.txt

# Install additional dependencies for KaliAgent
pip install \
    fastapi \
    uvicorn \
    pydantic \
    python-multipart \
    reportlab \
    matplotlib
```

### Step 4: Verify Python Installation

```bash
# Test KaliAgent import
python3 -c "from agentic_ai.agents.cyber.kali import KaliAgent; print('✅ KaliAgent imported successfully')"

# Run unit tests
python3 -m pytest tests/test_kali_agent.py -v
```

---

## Kali Linux Tools Setup

### Option A: Full Kali Linux (Recommended)

If running on Kali Linux, all tools are pre-installed:

```bash
# Verify tool installation
which nmap
which nikto
which sqlmap
which metasploit
```

### Option B: Ubuntu/Debian with Kali Tools

```bash
# Add Kali repository
echo "deb http://http.kali.org/kali kali-rolling main non-free contrib" | \
    sudo tee /etc/apt/sources.list.d/kali.list

# Add Kali GPG key
wget -q -O - https://archive.kali.org/archive-key.asc | sudo apt-key add -

# Update and install Kali tools
sudo apt update
sudo apt install -y kali-linux-default
```

### Option C: Minimal Tool Installation

Install only essential tools:

```bash
sudo apt install -y \
    nmap \
    nikto \
    sqlmap \
    gobuster \
    wpscan \
    john \
    hashcat \
    hydra \
    aircrack-ng \
    wireshark \
    metasploit-framework
```

### Verify Tool Installation

```bash
# Run verification script
python3 scripts/verify_tools.py
```

Expected output:
```
✅ nmap: 7.94
✅ nikto: 2.5.0
✅ sqlmap: 1.8
✅ gobuster: 3.6
✅ wpscan: 3.8.28
✅ john: 1.9.0
✅ hashcat: 6.2.6
✅ hydra: 9.5
✅ aircrack-ng: 1.7
✅ metasploit: 6.4.0

All 52 tools verified successfully!
```

---

## Metasploit Configuration

### Step 1: Start Metasploit RPC

```bash
# Start PostgreSQL (required for Metasploit)
sudo systemctl start postgresql
sudo systemctl enable postgresql

# Initialize Metasploit database
sudo -u postgres msfdb init

# Start Metasploit RPC
msfrpcd -P your_password -a 127.0.0.1 -p 55553
```

### Step 2: Configure KaliAgent

Edit `kali_dashboard/server.py`:

```python
# Metasploit configuration
MSF_CONFIG = {
    'host': '127.0.0.1',
    'port': 55553,
    'password': 'your_password',
}
```

### Step 3: Test Connection

```bash
python3 scripts/test_metasploit.py
```

---

## Dashboard Installation

### Step 1: Install Node.js Dependencies

```bash
cd kali_dashboard/frontend

# Install dependencies
npm install

# If you encounter errors, try:
npm cache clean --force
rm -rf node_modules package-lock.json
npm install
```

### Step 2: Development Mode

```bash
# Start development server
npm run dev

# Access at: http://localhost:5173
```

### Step 3: Production Build

```bash
# Build for production
npm run build

# Preview production build
npm run preview

# Deploy dist/ directory to web server
```

### Step 4: Start Backend API

```bash
cd kali_dashboard

# Start FastAPI server
python3 server.py

# API available at: http://localhost:8001
# API docs at: http://localhost:8001/docs
```

---

## Verification

### Complete Verification Script

```bash
python3 scripts/verify_installation.py
```

This script checks:
- ✅ Python dependencies
- ✅ Node.js installation
- ✅ Kali Linux tools (52 tools)
- ✅ Metasploit connection
- ✅ Dashboard accessibility
- ✅ Unit tests passing

### Expected Output

```
KaliAgent Installation Verification
====================================

[1/6] Python Dependencies... ✅
[2/6] Node.js Installation... ✅
[3/6] Kali Linux Tools... ✅ (52/52 tools)
[4/6] Metasploit Connection... ✅
[5/6] Dashboard API... ✅
[6/6] Unit Tests... ✅ (38/38 passing)

Installation Status: SUCCESS ✅

Dashboard: http://localhost:5173
API: http://localhost:8001
API Docs: http://localhost:8001/docs
```

---

## Troubleshooting

### Common Issues

#### 1. Python Import Errors

```bash
# Reinstall dependencies
pip install --upgrade -r requirements.txt

# Verify virtual environment is activated
which python3  # Should point to venv/bin/python3
```

#### 2. Node.js Version Issues

```bash
# Check Node.js version
node --version  # Should be 18.x or higher

# Update Node.js
curl -fsSL https://deb.nodesource.com/setup_18.x | sudo -E bash -
sudo apt install -y nodejs
```

#### 3. Kali Tools Not Found

```bash
# Check if tools are installed
which nmap

# If missing, install Kali tools
sudo apt install -y kali-linux-default
```

#### 4. Metasploit Connection Failed

```bash
# Check if PostgreSQL is running
sudo systemctl status postgresql

# Restart Metasploit RPC
pkill msfrpcd
msfrpcd -P your_password -a 127.0.0.1 -p 55553
```

#### 5. Dashboard Won't Start

```bash
# Clear npm cache
cd kali_dashboard/frontend
npm cache clean --force

# Reinstall dependencies
rm -rf node_modules package-lock.json
npm install

# Try starting again
npm run dev
```

#### 6. Port Already in Use

```bash
# Find process using port 8001
lsof -i :8001

# Kill the process
kill -9 <PID>

# Or use a different port
python3 server.py --port 8002
```

---

## Post-Installation

### 1. Configure Safety Settings

Edit `kali_dashboard/server.py`:

```python
# Set default authorization level
DEFAULT_AUTH_LEVEL = "BASIC"

# Configure IP whitelist
IP_WHITELIST = ["192.168.1.0/24", "10.0.0.0/8"]

# Enable audit logging
ENABLE_AUDIT_LOGGING = True
AUDIT_LOG_PATH = "/var/log/kali-audit.jsonl"
```

### 2. Create First Engagement

```bash
curl -X POST http://localhost:8001/api/engagements \
  -H "Content-Type: application/json" \
  -d '{
    "name": "My First Engagement",
    "engagement_type": "penetration_test",
    "scope": ["192.168.1.0/24"],
    "objectives": ["Find vulnerabilities", "Test security posture"]
  }'
```

### 3. Execute First Playbook

Via Dashboard:
1. Navigate to **Playbooks** page
2. Select **Comprehensive Reconnaissance**
3. Enter target: `192.168.1.100`
4. Click **Execute Playbook**
5. Monitor live execution

Via API:
```bash
curl -X POST http://localhost:8001/api/engagements/eng-001/playbook \
  -H "Content-Type: application/json" \
  -d '{
    "playbook_type": "recon",
    "target": "192.168.1.100",
    "domain": "example.com"
  }'
```

---

## Next Steps

- 📖 Read [QUICKSTART.md](QUICKSTART.md) for usage guide
- 📊 Explore [API Documentation](http://localhost:8001/docs)
- 🎨 Access [Dashboard](http://localhost:5173)
- 📝 Review [KALI_AGENT.md](../docs/KALI_AGENT.md) for tool reference
- 🔒 Read [SECURITY.md](SECURITY.md) for safety guidelines

---

## Support

- **Documentation**: `/kali_dashboard/README.md`
- **API Docs**: `http://localhost:8001/docs`
- **Issues**: GitHub Issues
- **Discord**: https://discord.gg/clawd

---

*Last Updated: April 18, 2026*
*Version: 1.0.0*
