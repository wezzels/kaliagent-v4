# Getting Started with Agentic AI

**Version:** 0.7.0  
**Time to First Run:** 5 minutes

---

## Prerequisites

- Python 3.12+
- Docker & Docker Compose (for full stack)
- Git

---

## Step 1: Clone & Setup

```bash
# Clone repository
git clone https://idm.wezzel.com/crab-meat-repos/agentic-ai.git
cd agentic-ai

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Linux/macOS
# or: venv\Scripts\activate  # Windows

# Install dependencies
pip install -r requirements.txt
```

---

## Step 2: Quick Test

```bash
# Run tests to verify setup
pytest tests/ -v --tb=short

# Expected: 383 tests passing
```

---

## Step 3: Run Examples

### Example 1: Multi-Agent Collaboration

```bash
python examples/multi_agent_collaboration.py
```

**What it does:**
- Creates a shared workspace
- 3 agents edit a document simultaneously
- Demonstrates conflict resolution
- Shows presence tracking

**Expected output:**
```
==============================================================
Multi-Agent Collaborative Document Editing
==============================================================

Created document: Project README (ID: ws-xxx)

[developer] Starting to edit document...
[reviewer] Starting to edit document...
[tech-writer] Starting to edit document...

[developer] Submitted operation (version 1)
[reviewer] Submitted operation (version 2)
[tech-writer] Submitted operation (version 3)

==============================================================
Results:
==============================================================
Final document version: 3
Active users: 3
```

### Example 2: Session Management

```bash
python examples/session_management.py
```

**What it does:**
- Creates a collaboration session
- 4 participants join with different roles
- Demonstrates role changes and invites
- Shows activity tracking

---

## Step 4: Run Full Stack (Docker)

```bash
# Start all services
docker-compose up -d

# Check status
docker-compose ps

# View logs
docker-compose logs -f agentic-ai
```

**Services Started:**
| Service | Port | URL |
|---------|------|-----|
| Agentic AI API | 5000 | http://localhost:5000 |
| Redis | 6379 | localhost:6379 |
| Ollama (LLM) | 11434 | http://localhost:11434 |
| Prometheus | 9090 | http://localhost:9090 |
| Grafana | 3000 | http://localhost:3000 |

---

## Step 5: Test API Endpoints

### Health Check

```bash
curl http://localhost:5000/health
```

**Response:**
```json
{
  "status": "healthy",
  "version": "0.7.0",
  "environment": "development",
  "timestamp": "2026-04-16T01:00:00"
}
```

### Create Workspace

```bash
curl -X POST http://localhost:5000/api/v1/workspaces \
  -H "Content-Type: application/json" \
  -d '{"name": "My Workspace", "creator_id": "alice"}'
```

### Create Session

```bash
curl -X POST http://localhost:5000/api/v1/sessions \
  -H "Content-Type: application/json" \
  -d '{"name": "Team Meeting", "creator_id": "alice"}'
```

### Get Online Users

```bash
curl http://localhost:5000/api/v1/presence
```

---

## Step 6: Run Benchmarks

```bash
python benchmarks/performance_test.py
```

**Expected results:**
- Real-time ops: ~570 ops/sec
- Workspace ops: ~60,000 ops/sec
- Session scaling: ~58,000 ops/sec
- Presence tracking: ~64,000 ops/sec

---

## Step 7: Explore the Code

### Key Modules

```python
# Import agents
from agentic_ai.agents.developer import DeveloperAgent
from agentic_ai.agents.lead import LeadAgent

# Import collaboration
from agentic_ai.collaboration.workspace import Workspace
from agentic_ai.collaboration.sessions import SessionManager
from agentic_ai.collaboration.realtime import RealTimeCollaboration

# Import monitoring
from agentic_ai.monitoring.metrics import MetricsRegistry
from agentic_ai.monitoring.dashboard import Dashboard
```

### Create Your First Agent

```python
from agentic_ai.agents.developer import DeveloperAgent
from agentic_ai.infrastructure.state_store import StateStore

# Initialize
state = StateStore()
agent = DeveloperAgent(agent_id="my-agent", state_store=state)

# Execute a task
result = agent.execute_task("Write a function to calculate fibonacci")
print(result.output)
```

### Create a Collaboration Session

```python
from agentic_ai.collaboration.sessions import SessionManager
from agentic_ai.collaboration.workspace import Workspace

# Create session manager
manager = SessionManager()

# Create session
session = manager.create_session("My Session", creator_id="alice")
session.start()

# Participants join
session.join(user_id="alice", name="Alice")
session.join(user_id="bob", name="Bob")

# Create workspace
workspace = Workspace(name="Shared Workspace")
workspace.add_participant("alice", is_owner=True)
workspace.add_participant("bob")

# Create shared document
doc = workspace.create_resource(
    name="Notes",
    resource_type="document",
    content="Meeting notes here",
    creator_id="alice",
)
```

---

## Step 8: Deploy to Production

### Docker

```bash
# Build production image
docker build -t agentic-ai:latest .

# Run container
docker run -d -p 5000:5000 -p 8000:8000 \
  -e REDIS_HOST=redis \
  -e DATABASE_URL=sqlite:///app/data/agentic.db \
  agentic-ai:latest
```

### Kubernetes

```bash
# Apply manifests
kubectl apply -f kubernetes/

# Check deployment
kubectl get pods -n agentic-ai

# View logs
kubectl logs -f deployment/agentic-ai -n agentic-ai
```

### Automated Deploy

```bash
./deploy.sh prod
```

---

## Common Issues

### Issue: Tests Failing

```bash
# Ensure you're in the right directory
cd ~/stsgym-work/agentic_ai

# Ensure virtual environment is activated
source venv/bin/activate

# Run with verbose output
pytest tests/ -v --tb=long
```

### Issue: Docker Compose Fails

```bash
# Check Docker is running
docker ps

# Check ports aren't in use
lsof -i :5000
lsof -i :6379

# Rebuild containers
docker-compose down
docker-compose up -d --build
```

### Issue: Module Not Found

```bash
# Ensure you're running from project root
cd ~/stsgym-work/agentic_ai

# Set PYTHONPATH
export PYTHONPATH=.

# Or install in editable mode
pip install -e .
```

---

## Next Steps

1. **Read the docs:**
   - [DEPLOYMENT.md](DEPLOYMENT.md) - Full deployment guide
   - [PHASE7_MULTIPLAYER.md](../PHASE7_MULTIPLAYER.md) - Collaboration features

2. **Customize agents:**
   - Create your own agent types
   - Extend existing agents with new capabilities

3. **Integrate with your stack:**
   - Connect to your LLM provider
   - Add custom metrics to Prometheus
   - Create custom Grafana dashboards

4. **Join the community:**
   - Discord: https://discord.com/invite/clawd
   - Documentation: https://docs.openclaw.ai

---

## Need Help?

- **Documentation:** See `docs/` folder
- **Examples:** See `examples/` folder
- **Tests:** See `tests/` folder for usage patterns
- **Issues:** https://github.com/openclaw/openclaw/issues

---

**Happy Building! 🚀**
