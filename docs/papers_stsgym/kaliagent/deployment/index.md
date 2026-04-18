# KaliAgent Deployment Guide

Production deployment instructions with infrastructure diagrams and automation.

---

## Table of Contents

1. [Architecture Overview](#architecture-overview)
2. [Docker Deployment](#docker-deployment)
3. [Kubernetes Deployment](#kubernetes-deployment)
4. [Cloud Deployment (AWS)](#cloud-deployment-aws)
5. [On-Premises Deployment](#on-premises-deployment)
6. [High Availability Setup](#high-availability-setup)
7. [Monitoring & Logging](#monitoring--logging)
8. [Backup & Recovery](#backup--recovery)
9. [Scaling Guide](#scaling-guide)

---

## Architecture Overview

### System Architecture

```mermaid
graph TB
    subgraph "User Layer"
        A[Web Browser]
        B[Mobile App]
        C[API Client]
    end
    
    subgraph "Frontend Layer"
        D[Nginx Reverse Proxy<br/>Port 443/8443]
        E[React Dashboard<br/>Port 5173]
    end
    
    subgraph "Application Layer"
        F[KaliAgent API<br/>FastAPI Port 8001]
        G[Task Queue<br/>Redis Port 6379]
    end
    
    subgraph "Data Layer"
        H[(PostgreSQL<br/>Port 5432)]
        I[(Redis Cache<br/>Port 6379)]
        J[/Audit Logs<br/>JSONL/]
    end
    
    subgraph "Tools Layer"
        K[Kali Tools<br/>52 utilities]
        L[Metasploit RPC<br/>Port 55553]
        M[PDF Generator<br/>ReportLab]
    end
    
    A --> D
    B --> D
    C --> F
    D --> E
    D --> F
    E --> F
    F --> G
    F --> H
    F --> I
    F --> J
    F --> K
    F --> L
    F --> M
```

### Network Architecture

```mermaid
graph LR
    subgraph "DMZ"
        A[Internet] --> B[Load Balancer]
        B --> C[Nginx Proxy]
    end
    
    subgraph "Application Tier"
        C --> D[KaliAgent API 1]
        C --> E[KaliAgent API 2]
        C --> F[KaliAgent API 3]
    end
    
    subgraph "Data Tier"
        D --> G[(PostgreSQL Primary)]
        E --> H[(PostgreSQL Replica)]
        F --> G
        D --> I[(Redis Cluster)]
        E --> I
        F --> I
    end
    
    subgraph "Management"
        J[Prometheus] --> D
        J --> E
        J --> F
        K[Grafana] --> J
    end
```

---

## Docker Deployment

### Quick Deploy

```mermaid
graph TD
    A[Clone Repo] --> B[Create .env File]
    B --> C[docker-compose up]
    C --> D[Verify Services]
    D --> E{All Green?}
    E -->|Yes| F[✅ Deploy Complete]
    E -->|No| G[Check Logs]
    G --> H[Fix Issues]
    H --> C
```

### Prerequisites

| Component | Version | Install Command |
|-----------|---------|-----------------|
| **Docker** | 20.10+ | `curl -fsSL https://get.docker.com \| sh` |
| **Docker Compose** | 2.0+ | `apt install docker-compose-plugin` |
| **RAM** | 8GB min | - |
| **Storage** | 50GB SSD | - |

### Docker Compose File

**docker-compose.yml:**

```yaml
version: '3.8'

services:
  # KaliAgent Backend
  kali-agent:
    build: .
    ports:
      - "8001:8001"
    environment:
      - DATABASE_URL=postgresql://kali:secure_password@postgres:5432/kali
      - MSFRPC_HOST=metasploit
      - MSFRPC_PORT=55553
      - MSFRPC_PASSWORD=metasploit_password
      - AUTH_LEVEL=BASIC
      - AUDIT_LOG_PATH=/var/log/kali/audit.jsonl
    volumes:
      - kali_logs:/var/log/kali
      - kali_workspace:/tmp/kali-workspace
    depends_on:
      postgres:
        condition: service_healthy
      metasploit:
        condition: service_started
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8001/api/health"]
      interval: 30s
      timeout: 10s
      retries: 3

  # Frontend Dashboard
  kali-frontend:
    build: ./frontend
    ports:
      - "80:80"
    volumes:
      - ./frontend/nginx.conf:/etc/nginx/nginx.conf:ro
    depends_on:
      - kali-agent
    restart: unless-stopped

  # PostgreSQL Database
  postgres:
    image: postgres:15-alpine
    environment:
      - POSTGRES_USER=kali
      - POSTGRES_PASSWORD=secure_password
      - POSTGRES_DB=kali
    volumes:
      - postgres_data:/var/lib/postgresql/data
    restart: unless-stopped
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U kali"]
      interval: 10s
      timeout: 5s
      retries: 5

  # Metasploit RPC
  metasploit:
    image: metasploitframework/metasploit-framework
    command: >
      sh -c "msfdb init && 
             msfrpcd -P metasploit_password -a 0.0.0.0 -p 55553"
    ports:
      - "55553:55553"
    volumes:
      - msf_data:/root/.msf4
    restart: unless-stopped

  # Redis Cache
  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"
    command: redis-server --appendonly yes
    volumes:
      - redis_data:/data
    restart: unless-stopped

volumes:
  postgres_data:
  msf_data:
  kali_logs:
  kali_workspace:
  redis_data:
```

### Deployment Steps

```bash
# Step 1: Clone repository
git clone https://github.com/wezzels/agentic-ai.git
cd agentic-ai/kali_dashboard

# Step 2: Create .env file with secure passwords
cat > .env << EOF
POSTGRES_USER=kali
POSTGRES_PASSWORD=$(openssl rand -base64 32)
MSFRPC_PASSWORD=$(openssl rand -base64 32)
AUTH_LEVEL=BASIC
EOF

# Step 3: Start all services
docker-compose up -d

# Step 4: Check status
docker-compose ps

# Expected output:
# NAME                  STATUS         PORTS
# kali_dashboard-kali-agent   Up (healthy)   0.0.0.0:8001->8001/tcp
# kali_dashboard-kali-frontend Up             0.0.0.0:80->80/tcp
# kali_dashboard-postgres     Up (healthy)   5432/tcp
# kali_dashboard-metasploit   Up             0.0.0.0:55553->55553/tcp
# kali_dashboard-redis        Up             0.0.0.0:6379->6379/tcp

# Step 5: View logs
docker-compose logs -f

# Step 6: Verify health
curl http://localhost:8001/api/health
# Expected: {"status":"healthy","agents_loaded":52}
```

---

## Kubernetes Deployment

### Cluster Architecture

```mermaid
graph TB
    subgraph "Kubernetes Cluster"
        A[Ingress Controller<br/>nginx-ingress]
        
        subgraph "Production Namespace"
            B[KaliAgent Deployment<br/>3 replicas]
            C[PostgreSQL StatefulSet<br/>1 primary + 2 replicas]
            D[Redis StatefulSet<br/>3 nodes]
        end
        
        subgraph "Monitoring Namespace"
            E[Prometheus]
            F[Grafana]
        end
    end
    
    A --> B
    B --> C
    B --> D
    B --> E
    E --> F
```

### Kubernetes Manifests

**namespace.yaml:**
```yaml
apiVersion: v1
kind: Namespace
metadata:
  name: kali-agent
  labels:
    name: kali-agent
    environment: production
```

**deployment.yaml:**
```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: kali-agent
  namespace: kali-agent
  labels:
    app: kali-agent
    version: v1.0.0
spec:
  replicas: 3
  selector:
    matchLabels:
      app: kali-agent
  template:
    metadata:
      labels:
        app: kali-agent
        version: v1.0.0
    spec:
      containers:
      - name: kali-agent
        image: kali-agent:latest
        ports:
        - containerPort: 8001
        env:
        - name: DATABASE_URL
          valueFrom:
            secretKeyRef:
              name: kali-secrets
              key: database-url
        - name: MSFRPC_PASSWORD
          valueFrom:
            secretKeyRef:
              name: kali-secrets
              key: msfrpc-password
        resources:
          requests:
            memory: "512Mi"
            cpu: "250m"
          limits:
            memory: "2Gi"
            cpu: "1000m"
        livenessProbe:
          httpGet:
            path: /api/health
            port: 8001
          initialDelaySeconds: 30
          periodSeconds: 10
        readinessProbe:
          httpGet:
            path: /api/health
            port: 8001
          initialDelaySeconds: 5
          periodSeconds: 5
```

**service.yaml:**
```yaml
apiVersion: v1
kind: Service
metadata:
  name: kali-agent-service
  namespace: kali-agent
spec:
  selector:
    app: kali-agent
  ports:
  - protocol: TCP
    port: 80
    targetPort: 8001
  type: ClusterIP
---
apiVersion: v1
kind: Service
metadata:
  name: kali-agent-external
  namespace: kali-agent
spec:
  selector:
    app: kali-agent
  ports:
  - protocol: TCP
    port: 443
    targetPort: 8001
  type: LoadBalancer
```

**ingress.yaml:**
```yaml
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: kali-agent-ingress
  namespace: kali-agent
  annotations:
    kubernetes.io/ingress.class: nginx
    nginx.ingress.kubernetes.io/ssl-redirect: "true"
    cert-manager.io/cluster-issuer: "letsencrypt-prod"
spec:
  tls:
  - hosts:
    - agents.example.com
    secretName: kali-agent-tls
  rules:
  - host: agents.example.com
    http:
      paths:
      - path: /
        pathType: Prefix
        backend:
          service:
            name: kali-agent-service
            port:
              number: 80
```

### Deploy to Kubernetes

```bash
# Step 1: Create namespace
kubectl apply -f kubernetes/namespace.yaml

# Step 2: Create secrets
kubectl create secret generic kali-secrets \
  --from-literal=database-url="postgresql://kali:password@postgres:5432/kali" \
  --from-literal=msfrpc-password="$(openssl rand -base64 32)" \
  -n kali-agent

# Step 3: Apply manifests
kubectl apply -f kubernetes/

# Step 4: Verify deployment
kubectl get pods -n kali-agent
kubectl get services -n kali-agent
kubectl get ingress -n kali-agent

# Step 5: View logs
kubectl logs -f deployment/kali-agent -n kali-agent
```

---

## Cloud Deployment (AWS)

### AWS Architecture

```mermaid
graph TB
    subgraph "AWS Cloud"
        A[Route 53<br/>DNS]
        B[CloudFront<br/>CDN]
        C[Application Load Balancer]
        
        subgraph "VPC"
            subgraph "Public Subnet"
                D[NAT Gateway]
            end
            
            subgraph "Private Subnet"
                E[ECS Cluster<br/>KaliAgent Tasks]
                F[RDS PostgreSQL<br/>Multi-AZ]
                G[ElastiCache Redis]
                H[S3 Bucket<br/>Reports & Logs]
            end
        end
        
        I[ECR<br/>Container Registry]
        J[CloudWatch<br/>Monitoring]
    end
    
    A --> B
    B --> C
    C --> E
    E --> F
    E --> G
    E --> H
    I --> E
    E --> J
```

### Terraform Configuration

**main.tf:**
```terraform
provider "aws" {
  region = "us-east-1"
}

# VPC
resource "aws_vpc" "kali" {
  cidr_block = "10.0.0.0/16"
  
  tags = {
    Name = "kali-agent-vpc"
  }
}

# ECS Cluster
resource "aws_ecs_cluster" "kali" {
  name = "kali-agent-cluster"
}

# RDS PostgreSQL
resource "aws_db_instance" "kali" {
  identifier        = "kali-agent-db"
  engine            = "postgres"
  engine_version    = "15.4"
  instance_class    = "db.t3.medium"
  allocated_storage = 100
  
  db_name  = "kali"
  username = "kali"
  password = var.db_password
  
  multi_az               = true
  storage_encrypted      = true
  automatically_backup   = true
  backup_retention_period = 7
  
  vpc_security_group_ids = [aws_security_group.rds.id]
  db_subnet_group_name   = aws_db_subnet_group.kali.name
}

# ElastiCache Redis
resource "aws_elasticache_cluster" "kali" {
  cluster_id           = "kali-agent-redis"
  engine               = "redis"
  node_type            = "cache.t3.medium"
  num_cache_nodes      = 3
  engine_version       = "7.0"
  port                 = 6379
}

# S3 Bucket for Reports
resource "aws_s3_bucket" "kali_reports" {
  bucket = "kali-agent-reports-${data.aws_caller_identity.current.account_id}"
}

# ECR Repository
resource "aws_ecr_repository" "kali_agent" {
  name                 = "kali-agent"
  image_tag_mutability = "MUTABLE"
  
  image_scanning_configuration {
    scan_on_push = true
  }
}
```

### Deploy with Terraform

```bash
# Step 1: Initialize Terraform
terraform init

# Step 2: Review plan
terraform plan -out=tfplan

# Step 3: Apply configuration
terraform apply tfplan

# Step 4: Build and push Docker image
docker build -t kali-agent .
docker tag kali-agent:latest ${AWS_ACCOUNT}.dkr.ecr.us-east-1.amazonaws.com/kali-agent:latest
docker push ${AWS_ACCOUNT}.dkr.ecr.us-east-1.amazonaws.com/kali-agent:latest

# Step 5: Deploy to ECS
aws ecs create-service \
  --cluster kali-agent-cluster \
  --service-name kali-agent-service \
  --task-definition kali-agent:1 \
  --desired-count 3 \
  --launch-type FARGATE
```

---

## High Availability Setup

### HA Architecture

```mermaid
graph TB
    subgraph "Load Balancer"
        A[HAProxy/Keepalived<br/>Virtual IP]
    end
    
    subgraph "Active Nodes"
        B[KaliAgent Node 1<br/>192.168.1.10]
        C[KaliAgent Node 2<br/>192.168.1.11]
        D[KaliAgent Node 3<br/>192.168.1.12]
    end
    
    subgraph "Database Cluster"
        E[PostgreSQL Primary<br/>192.168.1.20]
        F[PostgreSQL Replica 1<br/>192.168.1.21]
        G[PostgreSQL Replica 2<br/>192.168.1.22]
    end
    
    subgraph "Redis Cluster"
        H[Redis Master<br/>192.168.1.30]
        I[Redis Slave 1<br/>192.168.1.31]
        J[Redis Slave 2<br/>192.168.1.32]
    end
    
    A --> B
    A --> C
    A --> D
    B --> E
    C --> E
    D --> E
    E --> F
    E --> G
    B --> H
    C --> H
    D --> H
    H --> I
    H --> J
```

### PostgreSQL HA with Patroni

**patroni.yml:**
```yaml
scope: kali-agent
namespace: /db/
name: postgresql-1

restapi:
  listen: 0.0.0.0:8008
  connect_address: postgresql-1:8008

etcd:
  hosts: etcd-1:2379,etcd-2:2379,etcd-3:2379

bootstrap:
  dcs:
    ttl: 30
    loop_wait: 10
    retry_timeout: 10
    maximum_lag_on_failover: 1048576
    postgresql:
      use_pg_rewind: true
      use_slots: true
      parameters:
        wal_level: replica
        hot_standby: "on"
        max_wal_senders: 10
        max_replication_slots: 10

postgresql:
  listen: 0.0.0.0:5432
  connect_address: postgresql-1:5432
  data_dir: /var/lib/postgresql/data
  pgpass: /tmp/pgpass
  authentication:
    replication:
      username: replicator
      password: secure_password
    superuser:
      username: postgres
      password: secure_password
  parameters:
    unix_socket_directories: '.'

tags:
  nofailover: false
  noloadbalance: false
  clonefrom: false
  nosync: false
```

---

## Backup & Recovery

### Backup Strategy

```mermaid
graph TD
    A[Daily Backup<br/>2 AM UTC] --> B[PostgreSQL Dump]
    A --> C[Redis Snapshot]
    A --> D[Audit Logs Archive]
    
    B --> E[Compress & Encrypt]
    C --> E
    D --> E
    
    E --> F[Upload to S3]
    F --> G[Enable Versioning]
    G --> H[Set Lifecycle Policy<br/>30 days → Glacier]
    
    H --> I[Weekly Verification<br/>Restore Test]
```

### Backup Script

**backup.sh:**
```bash
#!/bin/bash
set -e

BACKUP_DIR="/backups"
DATE=$(date +%Y%m%d_%H%M%S)
S3_BUCKET="kali-agent-backups"

echo "🔄 Starting backup at $(date)"

# PostgreSQL backup
echo "📊 Backing up PostgreSQL..."
pg_dump -h postgres -U kali kali | gzip > ${BACKUP_DIR}/postgres_${DATE}.sql.gz

# Redis backup
echo "💾 Backing up Redis..."
redis-cli BGSAVE
sleep 5
cp /var/lib/redis/dump.rdb ${BACKUP_DIR}/redis_${DATE}.rdb

# Audit logs backup
echo "📝 Archiving audit logs..."
tar -czf ${BACKUP_DIR}/audit_logs_${DATE}.tar.gz /var/log/kali/audit.jsonl

# Encrypt backups
echo "🔒 Encrypting backups..."
for file in ${BACKUP_DIR}/*${DATE}*; do
    openssl enc -aes-256-cbc -salt -in $file -out $file.enc -pass pass:${ENCRYPTION_KEY}
    rm $file
done

# Upload to S3
echo "☁️  Uploading to S3..."
aws s3 cp ${BACKUP_DIR}/ s3://${S3_BUCKET}/${DATE}/ --recursive

# Cleanup local backups (keep 7 days)
echo "🧹 Cleaning up old backups..."
find ${BACKUP_DIR} -name "*.enc" -mtime +7 -delete

echo "✅ Backup complete at $(date)"
```

### Recovery Procedure

```mermaid
sequenceDiagram
    participant Admin
    participant Script
    participant S3
    participant DB
    participant App
    
    Admin->>Script: Initiate Recovery
    Script->>S3: Download Latest Backup
    S3-->>Script: Backup Files
    Script->>DB: Stop Application
    DB-->>Script: Stopped
    Script->>DB: Restore PostgreSQL
    Script->>DB: Restore Redis
    Script->>DB: Verify Integrity
    DB-->>Script: Restore Complete
    Script->>App: Start Application
    App-->>Script: Running
    Script->>Admin: Recovery Complete
```

---

## Monitoring & Logging

### Monitoring Stack

```mermaid
graph TB
    subgraph "KaliAgent"
        A[API Server]
        B[Task Queue]
    end
    
    subgraph "Metrics Collection"
        C[Prometheus<br/>Port 9090]
        D[Node Exporter<br/>Port 9100]
    end
    
    subgraph "Visualization"
        E[Grafana<br/>Port 3000]
    end
    
    subgraph "Alerting"
        F[Alertmanager<br/>Port 9093]
        G[Slack Webhook]
        H[Email SMTP]
    end
    
    A --> C
    B --> C
    C --> D
    C --> E
    C --> F
    F --> G
    F --> H
```

### Prometheus Metrics

**Key Metrics to Monitor:**

| Metric | Type | Description | Alert Threshold |
|--------|------|-------------|-----------------|
| `kali_api_requests_total` | Counter | Total API requests | - |
| `kali_api_request_duration_seconds` | Histogram | Request latency | p99 > 2s |
| `kali_playbook_executions_total` | Counter | Playbooks executed | - |
| `kali_findings_total` | Counter | Security findings | Critical > 10/day |
| `kali_tool_executions_total` | Counter | Tool executions | - |
| `kali_active_engagements` | Gauge | Current engagements | > 100 |
| `kali_database_connections` | Gauge | DB connections | > 80% max |
| `kali_redis_memory_used` | Gauge | Redis memory | > 80% max |

### Grafana Dashboards

**Dashboard Panels:**

1. **Overview**
   - API request rate (req/s)
   - Active engagements
   - Findings by severity
   - System health

2. **Performance**
   - Request latency (p50, p95, p99)
   - Database query time
   - Redis cache hit rate
   - Memory usage

3. **Security**
   - Findings over time
   - Tool execution count
   - Authorization failures
   - Safety blocks

---

## Scaling Guide

### Scaling Decision Tree

```mermaid
graph TD
    A[Performance Issue?] --> B{High CPU?}
    B -->|Yes| C[Scale API Horizontally]
    B -->|No| D{High Memory?}
    D -->|Yes| E{Redis or DB?}
    E -->|Redis| F[Scale Redis Cluster]
    E -->|DB| G[Add Read Replicas]
    D -->|No| H{High Disk I/O?}
    H -->|Yes| I[Upgrade to SSD/NVMe]
    H -->|No| J[Check Network]
    
    C --> K[Add API Replicas]
    F --> L[Add Redis Nodes]
    G --> M[Promote Replica]
    I --> N[Migration Required]
    J --> O[Network Team]
```

### Horizontal Scaling

**Add API Replicas:**

```bash
# Docker Compose
docker-compose up -d --scale kali-agent=5

# Kubernetes
kubectl scale deployment kali-agent --replicas=5

# ECS
aws ecs update-service \
  --cluster kali-agent-cluster \
  --service kali-agent-service \
  --desired-count 5
```

### Vertical Scaling

**Resource Recommendations:**

| Workload | CPU | RAM | Storage | Network |
|----------|-----|-----|---------|---------|
| **Small** (<10 users) | 4 cores | 8 GB | 50 GB SSD | 1 Gbps |
| **Medium** (10-50 users) | 8 cores | 16 GB | 100 GB SSD | 1 Gbps |
| **Large** (50-100 users) | 16 cores | 32 GB | 200 GB NVMe | 10 Gbps |
| **Enterprise** (100+ users) | 32+ cores | 64+ GB | 500+ GB NVMe | 10+ Gbps |

---

## Troubleshooting

### Common Deployment Issues

| Issue | Symptoms | Solution |
|-------|----------|----------|
| **Port Conflict** | "Address already in use" | Change port in config or stop conflicting service |
| **Database Connection** | "Cannot connect to PostgreSQL" | Check DB is running, verify credentials |
| **Metasploit RPC** | "MSFRPC connection failed" | Start msfrpcd, check password |
| **Permission Denied** | "Cannot write to /var/log" | chown kali:kali /var/log/kali |
| **Docker Network** | "Container cannot communicate" | docker network inspect, recreate network |

### Health Check Commands

```bash
# Check all services
docker-compose ps

# View logs
docker-compose logs -f kali-agent
docker-compose logs -f postgres
docker-compose logs -f metasploit

# Test API
curl http://localhost:8001/api/health

# Test database
docker-compose exec postgres psql -U kali -c "SELECT 1"

# Test Redis
docker-compose exec redis redis-cli ping

# Test Metasploit
curl -X POST http://localhost:55553/api -d '{"method":"auth.login"}'
```

---

*Last Updated: April 18, 2026*  
*Version: 2.0.0 (Improved with Mermaid diagrams)*

**Deployment ready! 🚀**
