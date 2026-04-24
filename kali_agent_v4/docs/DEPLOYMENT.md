# KaliAgent v4 - Deployment Guide

**Version:** 4.0.0  
**Last Updated:** April 24, 2026

---

## Table of Contents

1. [Quick Start](#quick-start)
2. [Docker Deployment](#docker-deployment)
3. [Manual Installation](#manual-installation)
4. [Kubernetes Deployment](#kubernetes-deployment)
5. [Production Hardening](#production-hardening)
6. [Troubleshooting](#troubleshooting)

---

## Quick Start

### Prerequisites

- Docker 24.0+ and Docker Compose 2.0+
- Python 3.11+
- 8GB RAM minimum (16GB recommended)
- 50GB disk space
- NVIDIA GPU (optional, for AI features)

### One-Command Deploy

```bash
# Clone repository
git clone https://github.com/wezzels/kaliagent-v4.git
cd kaliagent-v4

# Start all services
docker-compose up -d

# Verify deployment
docker-compose ps

# Access dashboard
open http://localhost:5007
```

---

## Docker Deployment

### Standard Deployment

```bash
# Build and start
docker-compose build
docker-compose up -d

# View logs
docker-compose logs -f

# Stop services
docker-compose down
```

### With HTTPS (Production)

```bash
# Generate self-signed certificate (or use Let's Encrypt)
mkdir ssl
openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
    -keyout ssl/privkey.pem \
    -out ssl/fullchain.pem \
    -subj "/CN=kaliagent.example.com"

# Start with HTTPS profile
docker-compose --profile https up -d

# Access via HTTPS
open https://localhost
```

### Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `KALIAGENT_ENV` | `production` | Environment mode |
| `KALIAGENT_VERSION` | `4.0.0` | Version string |
| `OLLAMA_HOST` | `http://ollama:11434` | Ollama API endpoint |
| `REDIS_URL` | `redis://redis:6379` | Redis connection |

Example `.env` file:

```bash
KALIAGENT_ENV=production
KALIAGENT_VERSION=4.0.0
OLLAMA_HOST=http://ollama:11434
REDIS_URL=redis://redis:6379/0
```

---

## Manual Installation

### Step 1: Install Dependencies

```bash
# System packages (Ubuntu/Debian)
sudo apt update
sudo apt install -y \
    python3.11 \
    python3.11-venv \
    python3-pip \
    nmap \
    aircrack-ng \
    sqlmap \
    wireshark \
    tcpdump \
    git \
    curl

# Python virtual environment
python3 -m venv venv
source venv/bin/activate

# Python packages
pip install -r requirements.txt
```

### Step 2: Configure Services

```bash
# Create directories
mkdir -p reports recordings data

# Copy example config
cp .env.example .env

# Edit configuration
nano .env
```

### Step 3: Start Services

```bash
# Start Redis (required)
sudo systemctl start redis
sudo systemctl enable redis

# Start Ollama (for AI features)
ollama serve &

# Start dashboard
python phase6/dashboard_v2.py
```

### Step 4: Install as System Service

```bash
# Create service file
sudo nano /etc/systemd/system/kaliagent.service
```

```ini
[Unit]
Description=KaliAgent v4 Dashboard
After=network.target redis.service

[Service]
Type=simple
User=kaliagent
Group=kaliagent
WorkingDirectory=/opt/kaliagent-v4
Environment="PATH=/opt/kaliagent-v4/venv/bin"
ExecStart=/opt/kaliagent-v4/venv/bin/python phase6/dashboard_v2.py
Restart=always
RestartSec=5

[Install]
WantedBy=multi-user.target
```

```bash
# Enable and start
sudo systemctl daemon-reload
sudo systemctl enable kaliagent
sudo systemctl start kaliagent
sudo systemctl status kaliagent
```

---

## Kubernetes Deployment

### Prerequisites

- Kubernetes 1.27+ cluster
- kubectl configured
- Helm 3.0+ (optional)

### Deploy with kubectl

```bash
# Apply manifests
kubectl apply -f k8s/production/

# Check status
kubectl get pods -l app=kaliagent

# View logs
kubectl logs -f deployment/kaliagent-production

# Access service
kubectl port-forward svc/kaliagent 5007:5007
```

### Deploy with Helm

```bash
# Add Helm repo
helm repo add kaliagent https://charts.kaliagent.example.com
helm repo update

# Install
helm install kaliagent kaliagent/kaliagent \
    --namespace kaliagent \
    --create-namespace \
    --values values.yaml

# Upgrade
helm upgrade kaliagent kaliagent/kaliagent \
    --namespace kaliagent \
    --values values.yaml
```

### Example values.yaml

```yaml
replicaCount: 3

image:
  repository: registry.example.com/kaliagent
  tag: "4.0.0"
  pullPolicy: IfNotPresent

ingress:
  enabled: true
  className: nginx
  hosts:
    - host: kaliagent.example.com
      paths:
        - path: /
          pathType: Prefix
  tls:
    - secretName: kaliagent-tls
      hosts:
        - kaliagent.example.com

resources:
  limits:
    cpu: 2000m
    memory: 4Gi
  requests:
    cpu: 500m
    memory: 1Gi

autoscaling:
  enabled: true
  minReplicas: 2
  maxReplicas: 10
  targetCPUUtilizationPercentage: 80
```

---

## Production Hardening

### Security Checklist

- [ ] Change default passwords
- [ ] Enable HTTPS with valid certificate
- [ ] Configure firewall rules
- [ ] Enable audit logging
- [ ] Set up monitoring/alerting
- [ ] Configure backups
- [ ] Review network policies
- [ ] Enable rate limiting
- [ ] Configure CORS properly
- [ ] Update all dependencies

### Firewall Rules

```bash
# Allow dashboard (HTTPS)
sudo ufw allow 443/tcp

# Allow SSH (change port in production)
sudo ufw allow 22/tcp

# Block C2 ports from external access
sudo ufw deny 8888/tcp
sudo ufw deny 1337/tcp
sudo ufw deny 8889/tcp

# Enable firewall
sudo ufw enable
```

### Monitoring

```bash
# Install Prometheus + Grafana
helm install prometheus prometheus-community/kube-prometheus-stack

# Configure alerts
kubectl apply -f k8s/monitoring/alerts.yaml
```

### Backups

```bash
#!/bin/bash
# backup.sh - Daily backup script

DATE=$(date +%Y%m%d)
BACKUP_DIR="/backups/kaliagent/$DATE"

mkdir -p "$BACKUP_DIR"

# Backup database
docker exec kaliagent-db pg_dump -U kaliagent kaliagent > "$BACKUP_DIR/database.sql"

# Backup reports
docker cp kaliagent:/app/reports "$BACKUP_DIR/reports"

# Backup recordings
docker cp kaliagent:/app/recordings "$BACKUP_DIR/recordings"

# Compress
tar -czf "$BACKUP_DIR.tar.gz" "$BACKUP_DIR"
rm -rf "$BACKUP_DIR"

# Upload to S3 (optional)
aws s3 cp "$BACKUP_DIR.tar.gz" s3://backups/kaliagent/

# Cleanup old backups (keep 30 days)
find /backups/kaliagent -name "*.tar.gz" -mtime +30 -delete
```

Add to crontab:

```bash
# Daily backup at 2 AM
0 2 * * * /opt/kaliagent-v4/scripts/backup.sh
```

---

## Troubleshooting

### Dashboard Won't Start

```bash
# Check logs
docker-compose logs kaliagent

# Common issues:
# 1. Port already in use
sudo lsof -i :5007

# 2. Missing dependencies
docker-compose build --no-cache

# 3. Permission errors
sudo chown -R $USER:$USER .
```

### C2 Servers Not Connecting

```bash
# Verify network isolation
docker network inspect kaliagent_attack-network

# Check C2 server logs
docker-compose logs sliver
docker-compose logs empire

# Test connectivity
docker exec kaliagent curl http://sliver:8888/health
```

### AI Features Not Working

```bash
# Check Ollama status
docker-compose ps ollama

# Verify model is downloaded
docker exec ollama ollama list

# Download model if missing
docker exec ollama ollama pull qwen3.5:cloud

# Test Ollama API
curl http://localhost:11434/api/tags
```

### Performance Issues

```bash
# Check resource usage
docker stats

# Increase Docker resources
# Edit /etc/docker/daemon.json
{
  "default-ulimits": {
    "nofile": {
      "Name": "nofile",
      "Hard": 65536,
      "Soft": 32768
    }
  }
}

# Restart Docker
sudo systemctl restart docker
```

---

## Support

For additional help:

- **Documentation:** [docs/](docs/)
- **Issues:** [GitHub Issues](https://github.com/wezzels/kaliagent-v4/issues)
- **Email:** support@kaliagent.example.com

---

**🍀 Happy (Legal) Hacking!**
