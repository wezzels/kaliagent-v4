# 🍀 KaliAgent v4

**Real Attack Works Edition**

[![Version](https://img.shields.io/badge/version-4.0.0-green.svg)](https://github.com/wezzels/kaliagent-v4)
[![License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)
[![Python](https://img.shields.io/badge/python-3.11+-blue.svg)](https://python.org)
[![Build](https://github.com/wezzels/kaliagent-v4/workflows/CI/badge.svg)](https://github.com/wezzels/kaliagent-v4/actions)

---

## 🎯 Overview

**KaliAgent v4** is a fully automated penetration testing platform featuring real C2 infrastructure, AI-powered attack planning, and professional report generation.

> ⚠️ **WARNING:** Only use on systems you own or have explicit written permission to test. This tool is for educational and authorized security testing purposes only.

---

## ✨ Features

### 🔬 Complete Attack Lab
- Isolated network (10.0.100.0/24) with no internet leak
- Pre-configured vulnerable targets (Juice Shop, Metasploitable)
- Real C2 servers (Sliver, Empire, Enhanced)
- One-command deployment via Docker

### ⚔️ Automated Attack Chains
| Attack Type | Capability | Status |
|-------------|------------|--------|
| **Web App** | SQLi → Shell | ✅ |
| **WiFi** | Monitor → Crack | ✅ |
| **Network** | Scan → Own | ✅ |
| **CVE Exploits** | EternalBlue, Log4Shell | ✅ |

### 🤖 AI-Powered Automation
- Natural language commands ("Scan the 10.0.100.0/24 network")
- LLM-powered attack planning
- Automated vulnerability analysis
- Smart report generation

### 📊 Professional Dashboard
- Real-time WebSocket updates
- Live terminal output
- Network topology visualization
- Attack history charts

### 📄 Report Generation
- PDF (professional formatting)
- HTML (responsive design)
- JSON (data exchange)
- CVSS scoring included

---

## 🚀 Quick Start

### Option 1: Docker (Recommended)

```bash
# Clone repository
git clone https://github.com/wezzels/kaliagent-v4.git
cd kaliagent-v4

# Start all services
docker-compose up -d

# Access dashboard
open http://localhost:5007
```

### Option 2: Manual Installation

```bash
# Install dependencies
pip install -r requirements.txt

# Start dashboard
python phase6/dashboard_v2.py

# Access dashboard
open http://localhost:5007
```

### Option 3: CLI

```bash
# Make CLI executable
chmod +x kaliagent

# Run commands
./kaliagent --version
./kaliagent status
./kaliagent scan -t 10.0.100.0/24
./kaliagent attack -t 10.0.100.10 -a web
./kaliagent report -f pdf
```

---

## 📖 Documentation

| Document | Description |
|----------|-------------|
| [README.md](README.md) | This file - quick start |
| [CHANGELOG.md](CHANGELOG.md) | Version history |
| [docs/DEPLOYMENT.md](docs/DEPLOYMENT.md) | Production deployment guide |
| [docs/API.md](docs/API.md) | REST API documentation |
| [docs/SECURITY.md](docs/SECURITY.md) | Security best practices |

---

## 🎬 Demo

### Dashboard Preview

![Dashboard](docs/images/dashboard-preview.png)

### Example Commands

```bash
# Scan network
./kaliagent scan -t 10.0.100.0/24 --type nmap

# Launch attack
./kaliagent attack -t 10.0.100.10 -a web --method sql_injection

# Generate report
./kaliagent report -f pdf -o ./reports

# AI natural language
./kaliagent ai "Find all web servers and check for SQL injection"

# Check system health
./kaliagent doctor
```

### Python API

```python
from phase6 import Phase6Orchestrator

# Initialize
agent = Phase6Orchestrator()

# AI-powered analysis
analysis = agent.analyze_target("10.0.100.10")

# Generate professional report
reports = agent.generate_report(attack_results, format='all')

# Chat with AI assistant
response = agent.chat("What's the best exploit for Apache 2.4.18?")
```

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                     KaliAgent v4                             │
├─────────────────────────────────────────────────────────────┤
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐         │
│  │  Dashboard  │  │   CLI       │  │   API       │         │
│  │  (WebSocket)│  │  (Click)    │  │  (REST)     │         │
│  └──────┬──────┘  └──────┬──────┘  └──────┬──────┘         │
│         │                │                │                 │
│         └────────────────┼────────────────┘                 │
│                          │                                  │
│                  ┌───────▼────────┐                         │
│                  │  Orchestrator  │                         │
│                  └───────┬────────┘                         │
│                          │                                  │
│     ┌────────────────────┼────────────────────┐             │
│     │                    │                    │             │
│ ┌───▼────┐      ┌───────▼───────┐     ┌─────▼─────┐        │
│ │  LLM   │      │   Attack      │     │  Report   │        │
│ │  AI    │      │   Chains      │     │ Generator │        │
│ └────────┘      └───────────────┘     └───────────┘        │
└─────────────────────────────────────────────────────────────┘
```

---

## 🛡️ Security Features

- ✅ Non-root Docker containers
- ✅ Network isolation (no internet leak)
- ✅ Rate limiting on all endpoints
- ✅ Security headers (CSP, HSTS, X-Frame-Options)
- ✅ Input validation
- ✅ Audit logging

---

## 🧪 Testing

```bash
# Run unit tests
pytest tests/unit -v

# Run E2E tests (requires Docker)
docker-compose up -d
pytest tests/e2e -v

# Generate coverage report
pytest --cov=. --cov-report=html
```

---

## 📦 Components

| Component | File | Size | Purpose |
|-----------|------|------|---------|
| LLM Integration | `llm_integration.py` | 7.8 KB | AI commands |
| Report Generator | `report_generator.py` | 17.6 KB | PDF/HTML/JSON |
| Dashboard v2 | `dashboard_v2.py` | 25.0 KB | Web UI |
| Video Generator | `demo_video_generator.py` | 10.1 KB | Demo reels |
| CLI | `kaliagent` | 8.4 KB | Command line |
| Docker | `Dockerfile` | 1.7 KB | Containerization |

**Total:** ~70 KB of production code

---

## 🎯 Roadmap

### Completed (v4.0.0)
- ✅ Phase 1: Attack Lab Infrastructure
- ✅ Phase 2: Real C2 Deployment
- ✅ Phase 3: Automated Attack Chains
- ✅ Phase 4: Real Exploitation Modules
- ✅ Phase 5: Hardware Attacks
- ✅ Phase 6: AI + Polish

### Future (v4.1.0+)
- [ ] Phase 7: Multi-Agent Orchestration
- [ ] Cloud exploitation (AWS, Azure, GCP)
- [ ] Active Directory automation
- [ ] Mobile app testing
- [ ] Voice commands
- [ ] Custom fine-tuned LLM

---

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

---

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## ⚠️ Legal Disclaimer

**KaliAgent v4** is designed for authorized security testing and educational purposes only.

- Only test systems you own or have explicit written permission to test
- The authors are not responsible for misuse or damages
- Compliance with local, state, and federal laws is your responsibility
- This tool is provided "as is" without warranty

---

## 🙏 Acknowledgments

- OWASP Juice Shop team
- Sliver C2 developers
- Empire C2 developers
- Ollama team
- Metasploit community

---

## 📞 Support

- **Issues:** [GitHub Issues](https://github.com/wezzels/kaliagent-v4/issues)
- **Documentation:** [docs/](docs/)
- **Email:** security@example.com

---

**🍀 Built with ❤️ by the KaliAgent Team**

*Version 4.0.0 - Real Attack Works Edition*
