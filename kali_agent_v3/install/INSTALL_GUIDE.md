# KaliAgent v3 - Installation Guide

**Version:** 3.0.0  
**Platform:** Kali Linux 2023.x or later  
**Status:** Production Ready ✅

---

## 📋 Prerequisites

### System Requirements
- **OS:** Kali Linux 2023.x or later (64-bit)
- **CPU:** 4 cores recommended (2 minimum)
- **RAM:** 8GB recommended (4GB minimum)
- **Disk:** 20GB free space (varies by profile)
- **Python:** 3.9 or later
- **Network:** Internet access for package installation

### Required Permissions
- Root access (sudo) for installation
- Standard user account for runtime

---

## 🚀 Quick Installation (5 Minutes)

### 1. Download Installation Package

```bash
# Clone the repository
cd /tmp
git clone https://idm.wezzel.com/crab-meat-repos/agentic-ai.git
cd agentic-ai/kali_agent_v3/install

# Or from GitHub
git clone https://github.com/wezzels/agentic-ai.git
cd agentic-ai/kali_agent_v3/install
```

### 2. Run Installer

```bash
# Make installer executable
chmod +x install.sh

# Run with default profile (standard)
sudo ./install.sh

# Or specify a profile
sudo ./install.sh --minimal    # Essential tools only (~500MB)
sudo ./install.sh --standard   # Balanced toolkit (~2GB) [DEFAULT]
sudo ./install.sh --advanced   # Full offensive suite (~5GB)
sudo ./install.sh --expert     # Everything + bleeding edge (~8GB)
```

### 3. Verify Installation

```bash
# Check service status
sudo systemctl status kaliagent

# Test CLI
kaliagent --version

# Run health check
kaliagent health
```

---

## ⚙️ Configuration

### 1. Edit Main Configuration

```bash
sudo nano /etc/kaliagent_v3/kaliagent.conf
```

**Key Settings:**
```ini
[general]
profile = standard
log_level = INFO

[authorization]
pin_required_for = advanced,critical
audit_all_actions = true

[weaponization]
output_dir = /var/lib/kaliagent_v3/payloads
auto_test = true

[c2]
sliver_enabled = true
empire_enabled = true
```

### 2. Set Environment Variables

```bash
sudo nano /etc/kaliagent_v3/.env
```

**Required Changes:**
```bash
# Change these defaults!
KALIAGENT_PIN=your_secure_pin_here
KALIAGENT_SECRET_KEY=generate_random_string_here

# C2 Configuration (if using)
SLIVER_GRPC_URL=grpc://your-sliver-server:31337
EMPIRE_API_URL=https://your-empire-server:1337
EMPIRE_API_USERNAME=empire
EMPIRE_API_PASSWORD=your_empire_password
```

### 3. Generate Secret Key

```bash
# Generate a secure random key
python3 -c "import secrets; print(secrets.token_urlsafe(32))"
```

---

## 🎯 Installation Profiles

### Minimal (~500MB)
**Best for:** Learning, testing, resource-constrained systems

**Includes:**
- Core framework
- Basic tool database
- Authorization system
- Essential tools (nmap, netcat, etc.)

**Command:**
```bash
sudo ./install.sh --minimal
```

### Standard (~2GB) ⭐ RECOMMENDED
**Best for:** Most penetration testers, general security work

**Includes:**
- Everything in Minimal
- Weaponization module
- Payload encoding
- Security auditing
- Common security tools

**Command:**
```bash
sudo ./install.sh --standard
```

### Advanced (~5GB)
**Best for:** Red team operations, comprehensive testing

**Includes:**
- Everything in Standard
- Full C2 integration (Sliver + Empire)
- Advanced weaponization
- Multi-C2 orchestration
- Extended tool database

**Command:**
```bash
sudo ./install.sh --advanced
```

### Expert (~8GB)
**Best for:** Security researchers, advanced operators

**Includes:**
- Everything in Advanced
- All 602 tools
- Bleeding edge tools
- Complete documentation
- Test suite
- Demo recordings

**Command:**
```bash
sudo ./install.sh --expert
```

---

## 🔧 Post-Installation

### 1. Start the Service

```bash
sudo systemctl start kaliagent
sudo systemctl enable kaliagent
```

### 2. Check Service Status

```bash
sudo systemctl status kaliagent

# View logs
sudo journalctl -u kaliagent -f
```

### 3. Test Functionality

```bash
# Check tool database
kaliagent tools list --limit 10

# Check authorization system
kaliagent auth test

# Run security audit
kaliagent audit run

# Check system health
kaliagent health
```

### 4. Configure Firewall (if needed)

```bash
# Allow API access (if enabled)
sudo ufw allow from 127.0.0.1 to any port 8080

# Allow C2 communication (if using)
sudo ufw allow out tcp to any port 31337  # Sliver
sudo ufw allow out tcp to any port 1337   # Empire
```

---

## 📁 Directory Structure

After installation:

```
/opt/kaliagent_v3/           # Installation directory
├── core/                    # Core modules
├── weaponization/          # Weaponization modules
├── c2/                     # C2 integration
├── production/             # Production modules
├── docs/                   # Documentation
├── venv/                   # Python virtual environment
└── requirements.txt        # Python dependencies

/etc/kaliagent_v3/          # Configuration
├── kaliagent.conf          # Main configuration
└── .env                    # Environment variables

/var/lib/kaliagent_v3/      # Data
├── tools/                  # Tool database
├── payloads/               # Generated payloads
├── reports/                # Audit reports
├── c2/                     # C2 configurations
└── audit/                  # Audit logs

/var/log/kaliagent_v3/      # Logs
└── kaliagent.log
```

---

## 🔒 Security Considerations

### 1. Change Default Credentials

**Immediately after installation:**
```bash
sudo nano /etc/kaliagent_v3/.env
```

Change:
- `KALIAGENT_PIN` - Authorization PIN
- `KALIAGENT_SECRET_KEY` - API secret key
- C2 passwords

### 2. File Permissions

The installer sets secure permissions:
- Configuration files: 600 (owner read/write only)
- Python modules: 640 (owner read/write, group read)
- Directories: 750 (owner full, group read/execute)
- Data directories: owned by kaliagent user

### 3. Network Security

**Recommendations:**
- Run on isolated network for C2 operations
- Use VPN for remote access
- Enable firewall (ufw)
- Don't expose API to public internet without authentication

### 4. Authorization Levels

Configure based on your security requirements:
```ini
[authorization]
# Require PIN for these action levels
pin_required_for = advanced,critical

# Log all actions
audit_all_actions = true
```

---

## 🐛 Troubleshooting

### Installation Fails

**Problem:** Permission denied errors

**Solution:**
```bash
# Ensure running as root
sudo ./install.sh

# Check disk space
df -h /opt /var /etc

# Check network connectivity
ping -c 3 archive.kali.org
```

### Service Won't Start

**Problem:** `systemctl status kaliagent` shows failed

**Solution:**
```bash
# Check logs
sudo journalctl -u kaliagent -n 50

# Verify configuration
sudo python3 -c "import configparser; c = configparser.ConfigParser(); c.read('/etc/kaliagent_v3/kaliagent.conf'); print('Config OK')"

# Check Python environment
sudo /opt/kaliagent_v3/venv/bin/python --version

# Test imports
sudo /opt/kaliagent_v3/venv/bin/python -c "from core.tool_manager import ToolManager; print('Imports OK')"
```

### CLI Not Found

**Problem:** `kaliagent: command not found`

**Solution:**
```bash
# Check if wrapper exists
ls -la /usr/local/bin/kaliagent

# Reinstall wrapper
sudo ln -sf /opt/kaliagent_v3/venv/bin/kaliagent /usr/local/bin/kaliagent

# Or use full path
/opt/kaliagent_v3/venv/bin/python -m kaliagent --help
```

### Tool Database Empty

**Problem:** No tools found in database

**Solution:**
```bash
# Check if database file exists
ls -la /var/lib/kaliagent_v3/tools/

# Rebuild database
sudo -u kaliagent /opt/kaliagent_v3/venv/bin/python -m kaliagent tools rebuild
```

---

## 📚 Next Steps

After installation:

1. **Read Documentation:**
   ```bash
   cd /opt/kaliagent_v3/docs
   cat README.md
   cat API_REFERENCE.md
   cat TRAINING_GUIDE.md
   ```

2. **Run Tutorials:**
   ```bash
   kaliagent tutorial basic
   kaliagent tutorial authorization
   kaliagent tutorial weaponization
   ```

3. **Explore Tools:**
   ```bash
   kaliagent tools list --category information-gathering
   kaliagent tools search nmap
   kaliagent tools info nmap
   ```

4. **Test Authorization:**
   ```bash
   kaliagent auth request nmap_scan --reason "Network mapping"
   kaliagent auth list
   ```

5. **Run Security Audit:**
   ```bash
   kaliagent audit run
   kaliagent audit report
   ```

---

## 🆘 Getting Help

### Documentation
- Local: `/opt/kaliagent_v3/docs/`
- Online: Repository wiki

### Logs
- Service: `sudo journalctl -u kaliagent`
- Application: `/var/log/kaliagent_v3/kaliagent.log`

### Support
- Issues: Repository issue tracker
- Community: Security forums, Discord

---

## 📊 Installation Verification Checklist

- [ ] Installation completed without errors
- [ ] Service is running (`systemctl status kaliagent`)
- [ ] CLI works (`kaliagent --version`)
- [ ] Configuration edited (PIN, secret key changed)
- [ ] Tool database loaded (602 tools)
- [ ] Authorization system working
- [ ] Logs accessible
- [ ] Firewall configured (if needed)
- [ ] Backup created (optional but recommended)

---

**Installation complete! You're ready to use KaliAgent v3! 🍀**

*Last Updated: April 22, 2026*
