# KaliAgent v3 Installation Package

**Version:** 3.0.0  
**Platform:** Kali Linux  
**Status:** Production Ready ✅

---

## 📦 What's Included

This installation package contains everything needed to deploy KaliAgent v3 on Kali Linux:

| File | Purpose | Size |
|------|---------|------|
| `install.sh` | Main installation script | 14KB |
| `uninstall.sh` | Uninstallation script | 6KB |
| `requirements.txt` | Python dependencies | 2KB |
| `INSTALL_GUIDE.md` | Complete installation guide | 9KB |
| `README.md` | This file | - |

---

## 🚀 Quick Start

### 1. Download Package

```bash
# From GitLab (IDM)
cd /tmp
git clone https://idm.wezzel.com/crab-meat-repos/agentic-ai.git
cd agentic-ai/kali_agent_v3/install

# Or from GitHub
git clone https://github.com/wezzels/agentic-ai.git
cd agentic-ai/kali_agent_v3/install
```

### 2. Run Installer

```bash
# Make executable
chmod +x install.sh

# Install with default profile (standard)
sudo ./install.sh

# Or choose a profile
sudo ./install.sh --minimal    # ~500MB
sudo ./install.sh --standard   # ~2GB (recommended)
sudo ./install.sh --advanced   # ~5GB
sudo ./install.sh --expert     # ~8GB
```

### 3. Verify Installation

```bash
# Check service
sudo systemctl status kaliagent

# Test CLI
kaliagent --version

# Run health check
kaliagent health
```

---

## 📋 Installation Profiles

| Profile | Size | Tools | Best For |
|---------|------|-------|----------|
| **Minimal** | ~500MB | Essential | Learning, testing |
| **Standard** ⭐ | ~2GB | Common | Most users |
| **Advanced** | ~5GB | Extended | Red teams |
| **Expert** | ~8GB | All 602 | Researchers |

---

## 🎯 What Gets Installed

### System Packages
- Python 3.9+
- System tools (nmap, netcat, curl, etc.)
- Development libraries
- SSL/TLS support

### Python Packages
- FastAPI (web framework)
- Cryptography libraries
- Database drivers
- CLI tools
- Testing frameworks (optional)

### KaliAgent Components
- Core modules (tool manager, authorization, hardware)
- Weaponization (payload generator, encoder, testing)
- C2 integration (Sliver, Empire, orchestration)
- Production (monitoring, security audit)
- Documentation
- Tool database (602 tools)

### Configuration
- Systemd service
- CLI wrapper
- Configuration files
- Environment variables
- Log directories

---

## 📁 Installation Locations

| Component | Location |
|-----------|----------|
| **Installation** | `/opt/kaliagent_v3/` |
| **Configuration** | `/etc/kaliagent_v3/` |
| **Data** | `/var/lib/kaliagent_v3/` |
| **Logs** | `/var/log/kaliagent_v3/` |
| **CLI** | `/usr/local/bin/kaliagent` |
| **Service** | `/etc/systemd/system/kaliagent.service` |

---

## 🔧 Post-Installation

### 1. Configure

```bash
# Edit main configuration
sudo nano /etc/kaliagent_v3/kaliagent.conf

# Set environment variables (IMPORTANT: change defaults!)
sudo nano /etc/kaliagent_v3/.env
```

**Must Change:**
- `KALIAGENT_PIN` - Your authorization PIN
- `KALIAGENT_SECRET_KEY` - Generate random string
- C2 passwords (if using)

### 2. Start Service

```bash
sudo systemctl start kaliagent
sudo systemctl enable kaliagent
```

### 3. Test

```bash
# Check version
kaliagent --version

# List tools
kaliagent tools list --limit 10

# Check health
kaliagent health
```

---

## 📚 Documentation

After installation, full documentation is available at:

```bash
/opt/kaliagent_v3/docs/
├── README.md              # Project overview
├── API_REFERENCE.md       # Complete API docs
├── TRAINING_GUIDE.md      # Step-by-step tutorials
└── WEAPONIZATION_GUIDE.md # Weaponization docs
```

---

## 🆘 Troubleshooting

### Service Won't Start

```bash
# Check logs
sudo journalctl -u kaliagent -n 50

# Verify configuration
sudo python3 -c "import configparser; c = configparser.ConfigParser(); c.read('/etc/kaliagent_v3/kaliagent.conf'); print('Config OK')"

# Test imports
sudo /opt/kaliagent_v3/venv/bin/python -c "from core.tool_manager import ToolManager; print('Imports OK')"
```

### CLI Not Found

```bash
# Reinstall wrapper
sudo ln -sf /opt/kaliagent_v3/venv/bin/kaliagent /usr/local/bin/kaliagent

# Or use full path
/opt/kaliagent_v3/venv/bin/python -m kaliagent --help
```

### Permission Denied

```bash
# Fix ownership
sudo chown -R kaliagent:kaliagent /opt/kaliagent_v3
sudo chown -R kaliagent:kaliagent /var/lib/kaliagent_v3
sudo chown -R kaliagent:kaliagent /var/log/kaliagent_v3
```

---

## 🗑️ Uninstallation

### Keep Data

```bash
cd /tmp/agentic-ai/kali_agent_v3/install
sudo ./uninstall.sh --keep-data
```

### Complete Removal (Purge)

```bash
sudo ./uninstall.sh --purge
```

---

## 🔒 Security Notes

### Before Installation

1. **Review the installer:**
   ```bash
   cat install.sh
   ```

2. **Verify checksums (if provided):**
   ```bash
   sha256sum install.sh
   ```

### After Installation

1. **Change default credentials immediately**
2. **Configure firewall** (if exposing API)
3. **Enable audit logging**
4. **Set strong authorization PIN**
5. **Regular security audits**

---

## 📊 System Requirements

| Requirement | Minimum | Recommended |
|-------------|---------|-------------|
| **OS** | Kali Linux 2023.x | Kali Linux 2024.x |
| **CPU** | 2 cores | 4+ cores |
| **RAM** | 4GB | 8GB+ |
| **Disk** | 10GB | 20GB+ |
| **Python** | 3.9 | 3.10+ |

---

## 🎓 Learning Resources

### Built-in Tutorials

```bash
kaliagent tutorial basic
kaliagent tutorial authorization
kaliagent tutorial weaponization
kaliagent tutorial c2
```

### Example Commands

```bash
# Search for tools
kaliagent tools search nmap

# Get tool info
kaliagent tools info nmap

# Request authorization
kaliagent auth request nmap_scan --reason "Network mapping"

# Run security audit
kaliagent audit run

# View audit report
kaliagent audit report
```

---

## 📞 Support

### Documentation
- Local: `/opt/kaliagent_v3/docs/`
- Repository: `docs/` directory

### Logs
- Service: `sudo journalctl -u kaliagent`
- Application: `/var/log/kaliagent_v3/kaliagent.log`

### Issues
- Report bugs via repository issue tracker
- Include logs and error messages

---

## 📈 Version History

### v3.0.0 (April 2026)
- ✅ Initial production release
- ✅ 602 tools in database
- ✅ Multi-C2 orchestration
- ✅ 4-level authorization
- ✅ Security auditing
- ✅ 94% test coverage

---

## ⚖️ License

See main repository for license information.

---

**Ready to install? Run `sudo ./install.sh` to get started! 🍀**

*Last Updated: April 22, 2026*
