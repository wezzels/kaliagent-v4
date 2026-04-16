# Demo Setup Guide

Quick setup for running Agentic AI dashboard with mock data.

## Option 1: Docker Compose (Recommended)

### Start Demo Stack

```bash
# Start all services
docker-compose -f docker-compose.demo.yaml up -d

# Check status
docker-compose -f docker-compose.demo.yaml ps

# View logs
docker-compose -f docker-compose.demo.yaml logs -f
```

### Access Services

- **Dashboard**: http://localhost:5173
- **Demo API**: http://localhost:8080
- **API Docs**: http://localhost:8080/docs
- **Redis**: localhost:6379

### Stop Demo Stack

```bash
docker-compose -f docker-compose.demo.yaml down
```

---

## Option 2: Manual Setup

### Start Demo API Server

```bash
# Install dependencies
pip install -r requirements.txt

# Run API server
python api_server.py
```

Access at: http://localhost:8080

### Start Dashboard

```bash
cd dashboard

# Install dependencies
npm install

# Run development server
npm run dev
```

Access at: http://localhost:5173

---

## Option 3: Kubernetes (Helm)

### Install with Helm

```bash
# Add repository
helm repo add agentic-ai https://wezzels.github.io/agentic-ai
helm repo update

# Install chart
helm install my-agentic-ai agentic-ai/agentic-ai --namespace agentic-ai --create-namespace

# Check status
kubectl get pods -n agentic-ai

# Port forward
kubectl port-forward svc/my-agentic-ai 8000:8000 -n agentic-ai
```

Access at: http://localhost:8000

### Uninstall

```bash
helm uninstall my-agentic-ai -n agentic-ai
```

---

## Demo API Endpoints

### System

```bash
# Health check
curl http://localhost:8080/health

# System health
curl http://localhost:8080/api/system/health

# List agents
curl http://localhost:8080/api/system/agents
```

### Chaos Engineering

```bash
# List experiments
curl http://localhost:8080/api/chaos/experiments

# Get experiment runs
curl http://localhost:8080/api/chaos/experiments/exp-1234/runs

# Chaos status
curl http://localhost:8080/api/chaos/status
```

### Vendor Risk

```bash
# List vendors
curl http://localhost:8080/api/vendors

# Get vendor report
curl http://localhost:8080/api/vendors/vendor-1234/report
```

### Audit

```bash
# List audits
curl http://localhost:8080/api/audits

# Get audit report
curl http://localhost:8080/api/audits/audit-1234/report
```

### Cloud Security

```bash
# List findings
curl http://localhost:8080/api/cloud/findings

# Get compliance score
curl http://localhost:8080/api/cloud/compliance?framework=cis_aws

# List accounts
curl http://localhost:8080/api/cloud/accounts
```

### ML Ops

```bash
# List models
curl http://localhost:8080/api/ml/models

# List experiments
curl http://localhost:8080/api/ml/experiments

# Check drift
curl http://localhost:8080/api/ml/drift/model-1234
```

---

## Dashboard Views

Once the dashboard is running, access these views:

1. **Overview** - System health, agent status, recent activity
2. **Chaos Monkey** - Experiments, runs, resiliency scores
3. **Vendor Risk** - Vendor assessments, risk scores, findings
4. **Audit** - Audit progress, findings, remediation
5. **Cloud Security** - CSPM findings, compliance scores
6. **ML Ops** - Models, experiments, drift detection

---

## Troubleshooting

### Dashboard Not Loading

```bash
# Check API server
curl http://localhost:8080/health

# Check dashboard logs
docker-compose -f docker-compose.demo.yaml logs dashboard
```

### API Not Responding

```bash
# Restart API container
docker-compose -f docker-compose.demo.yaml restart api

# Check API logs
docker-compose -f docker-compose.demo.yaml logs api
```

### Port Already in Use

Edit `docker-compose.demo.yaml` and change ports:

```yaml
ports:
  - "8081:8080"  # Change 8080 to 8081
```

---

## Customization

### Change Mock Data

Edit `api_server.py` to customize mock data generation:

```python
def generate_chaos_experiments(count: int = 10):
    # Customize data generation
    pass
```

### Add New Endpoints

Add new endpoints to `api_server.py`:

```python
@app.get("/api/custom/endpoint")
def get_custom_data():
    return {"data": "custom"}
```

---

## Next Steps

1. **Explore Dashboard** - Navigate through all 6 views
2. **Check API Docs** - Visit http://localhost:8080/docs
3. **Review Code** - Check `api_server.py` for mock data logic
4. **Deploy to Production** - See [DEPLOYMENT.md](DEPLOYMENT.md)

---

*Last updated: April 16, 2026*
