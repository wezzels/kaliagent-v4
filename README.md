# Agentic AI 🤖

**Version:** 0.7.0  
**Status:** Production Ready ✅  
**License:** MIT

[![Tests](https://img.shields.io/badge/tests-383%20passing-green)]()
[![Coverage](https://img.shields.io/badge/coverage-85%25-blue)]()
[![Python](https://img.shields.io/badge/python-3.12+-blue)]()
[![Docker](https://img.shields.io/badge/docker-ready-blue)]()
[![Kubernetes](https://img.shields.io/badge/kubernetes-ready-blue)]()

---

## What is Agentic AI?

**Agentic AI** is a multi-agent orchestration framework that enables AI agents to work together, collaborate in real-time, and coordinate complex workflows.

Think of it as an **"operating system for AI agents"** — providing infrastructure for communication, collaboration, decision-making, and production deployment.

---

## ✨ Key Features

| Category | Features |
|----------|----------|
| **🤖 AI Agents** | Developer, QA, Sales, Finance, SysAdmin, Lead Orchestrator |
| **💬 Communication** | ACP Protocol, Redis message bus, async task queues |
| **📝 Collaboration** | Real-time editing, operational transformation, workspaces |
| **👥 Sessions** | Multi-participant sessions, roles, invites, presence tracking |
| **🗳️ Consensus** | Voting, proposals, agreement tracking |
| **📊 Monitoring** | Prometheus metrics, Grafana dashboards, alerting |
| **🚀 Deployment** | Docker, Kubernetes, CI/CD, auto-scaling |

---

## 🚀 Quick Start

### Option 1: Docker Compose (Recommended for Development)

```bash
# Clone repository
git clone https://idm.wezzel.com/crab-meat-repos/agentic-ai.git
cd agentic-ai

# Start full stack (app + Redis + Ollama + Prometheus + Grafana)
docker-compose up -d

# Check status
docker-compose ps

# View logs
docker-compose logs -f agentic-ai
```

**Access Points:**
- API: http://localhost:5000
- Grafana: http://localhost:3000 (admin/admin)
- Prometheus: http://localhost:9090

### Option 2: Local Python

```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Run tests
pytest tests/ -v

# Run examples
python examples/multi_agent_collaboration.py
python examples/session_management.py

# Run benchmarks
python benchmarks/performance_test.py
```

---

## 📚 Documentation

| Document | Description |
|----------|-------------|
| [DEPLOYMENT.md](docs/DEPLOYMENT.md) | Complete deployment guide (Docker, K8s, monitoring) |
| [PHASE5_INTEGRATION.md](PHASE5_INTEGRATION.md) | Integration workflows |
| [PHASE6_ADVANCED.md](PHASE6_ADVANCED.md) | Advanced features (conversations, consensus, learning) |
| [PHASE7_MULTIPLAYER.md](PHASE7_MULTIPLAYER.md) | Collaboration system |

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────┐
│                    Agentic AI v0.7.0                    │
├─────────────────────────────────────────────────────────┤
│  ┌─────────┐  ┌─────────┐  ┌─────────┐  ┌─────────┐   │
│  │Developer│  │   QA    │  │  Sales  │  │ Finance │   │
│  └────┬────┘  └────┬────┘  └────┬────┘  └────┬────┘   │
│       │            │            │            │         │
│       └────────────┴─────┬──────┴────────────┘         │
│                          │                              │
│                   ┌──────▼──────┐                       │
│                   │ Lead Agent  │  (Orchestrator)       │
│                   └──────┬──────┘                       │
│                          │                              │
│    ┌─────────────────────┼─────────────────────┐       │
│    │                     │                     │       │
│    ▼                     ▼                     ▼       │
│ ┌──────┐           ┌──────────┐          ┌────────┐   │
│ │Redis │           │  SQLite  │          │ Ollama │   │
│ │ Bus  │           │  State   │          │  LLM   │   │
│ └──────┘           └──────────┘          └────────┘   │
│                                                         │
│    ┌─────────────────────────────────────────┐         │
│    │      Collaboration Layer                │         │
│    │  • Workspaces  • Real-Time Editing      │         │
│    │  • Sessions    • Presence Tracking      │         │
│    └─────────────────────────────────────────┘         │
└─────────────────────────────────────────────────────────┘
```

---

## 📦 Project Structure

```
agentic-ai/
├── agentic_ai/              # Main package (~150KB)
│   ├── agents/              # 6 specialized agents
│   ├── infrastructure/      # Redis, SQLite, Ollama
│   ├── protocol/            # ACP + Workflows
│   ├── conversations/       # Multi-turn dialogue
│   ├── consensus/           # Voting & proposals
│   ├── learning/            # Feedback & performance
│   ├── monitoring/          # Metrics, dashboards, alerts
│   └── collaboration/       # Workspaces, real-time, sessions
├── tests/                   # 383 tests
├── examples/                # Usage examples
├── benchmarks/              # Performance tests
├── docs/                    # Documentation
├── kubernetes/              # K8s manifests
├── monitoring/              # Prometheus + Grafana configs
├── Dockerfile               # Production image
├── docker-compose.yml       # Dev stack
├── deploy.sh                # Auto-deploy script
├── .gitlab-ci.yml          # CI/CD pipeline
└── requirements.txt         # Dependencies
```

---

## 🧪 Running Tests

```bash
# All tests
pytest tests/ -v

# With coverage
pytest tests/ -v --cov=agentic_ai --cov-report=html

# Specific test file
pytest tests/test_collaboration_e2e.py -v

# Specific test
pytest tests/test_base_agent.py::test_agent_execute_task -v
```

**Test Coverage:** 383 tests passing across all modules

---

## 📊 Performance Benchmarks

| Benchmark | Throughput | P50 Latency | P95 Latency | P99 Latency |
|-----------|------------|-------------|-------------|-------------|
| Real-time Operations | 570 ops/sec | 1.8ms | 3.4ms | 3.5ms |
| Workspace Operations | 61,805 ops/sec | 0.01ms | 0.02ms | 0.05ms |
| Session Scaling | 58,893 ops/sec | 0.01ms | 0.02ms | 0.04ms |
| Presence Tracking | 64,725 ops/sec | 0.01ms | 0.02ms | 0.04ms |

Run benchmarks:
```bash
python benchmarks/performance_test.py
```

---

## 🚀 Deployment

### Docker

```bash
# Build image
docker build -t agentic-ai:latest .

# Run container
docker run -d -p 5000:5000 -p 8000:8000 agentic-ai:latest
```

### Kubernetes

```bash
# Deploy to cluster
kubectl apply -f kubernetes/

# Check status
kubectl get pods -n agentic-ai

# Scale
kubectl scale deployment agentic-ai --replicas=5 -n agentic-ai
```

### Automated Deploy

```bash
# Deploy to environment
./deploy.sh dev      # Development
./deploy.sh staging  # Staging
./deploy.sh prod     # Production
```

---

## 🔧 Configuration

### Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `AGENTIC_AI_ENV` | production | Environment (dev/staging/prod) |
| `AGENTIC_AI_LOG_LEVEL` | INFO | Logging level |
| `REDIS_HOST` | localhost | Redis hostname |
| `REDIS_PORT` | 6379 | Redis port |
| `DATABASE_URL` | sqlite:///app/data/agentic.db | Database connection |
| `OLLAMA_HOST` | http://localhost:11434 | Ollama endpoint |
| `MAX_WORKERS` | 10 | Maximum agent workers |

---

## 📈 Monitoring

### Prometheus Metrics

- `agentic_ai_agents_total` - Total active agents
- `agentic_ai_sessions_active` - Active collaboration sessions
- `agentic_ai_operations_total` - Total operations processed
- `agentic_ai_collaboration_events_total` - Collaboration events
- `agentic_ai_request_duration_seconds` - Request latency

### Grafana Dashboards

1. **System Overview** - CPU, memory, network
2. **Agent Performance** - Agent activity, task completion
3. **Collaboration Metrics** - Sessions, participants, operations
4. **Error Tracking** - Error rates, types, sources

---

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Merge Request

### Development Guidelines

- Write tests for new features
- Follow existing code style (black, isort, flake8)
- Update documentation
- Ensure CI/CD pipeline passes

---

## 📝 License

MIT License - see LICENSE file for details.

---

## 🙏 Acknowledgments

- Built on [OpenClaw](https://github.com/openclaw/openclaw) framework
- LLM inference via [Ollama](https://ollama.ai)
- Metrics via [Prometheus](https://prometheus.io) + [Grafana](https://grafana.com)

---

## 📞 Support

- **Documentation:** https://docs.openclaw.ai
- **Discord:** https://discord.com/invite/clawd
- **Issues:** https://github.com/openclaw/openclaw/issues

---

**Built with ❤️ by Wesley Robbins**  
**Version 0.7.0 - April 2026**
