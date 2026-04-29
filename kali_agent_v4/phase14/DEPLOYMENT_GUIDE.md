# KaliAgent v5.0.0 - Production Deployment Guide

## Kubernetes Cluster Deployment

**Version:** 5.0.0  
**Status:** Production Ready ✅  
**Date:** April 29, 2026

---

## Prerequisites

### Cluster Requirements

- **Kubernetes:** v1.26+
- **Nodes:** 3+ (for HA)
- **CPU:** 8+ cores per node
- **Memory:** 32GB+ per node
- **GPU:** NVIDIA RTX 3060+ (optional, for inference)
- **Storage:** 100GB+ SSD

### Required Components

- **Ingress Controller:** nginx-ingress
- **Certificate Manager:** cert-manager (for TLS)
- **Metrics Server:** For HPA
- **GPU Operator:** (optional, for GPU nodes)

---

## Quick Deploy (5 minutes)

```bash
# 1. Clone repository
git clone https://github.com/wezzels/kaliagent-v4.git
cd kaliagent-v4/phase14

# 2. Generate Kubernetes manifests
python3 serving/auto_scaling.py

# 3. Create namespace
kubectl create namespace ml-platform

# 4. Create secrets
kubectl create secret generic kaliagent-ml-secrets \
  --from-literal=api-key=$(openssl rand -hex 32) \
  -n ml-platform

# 5. Deploy
kubectl apply -k ./k8s_manifests/

# 6. Verify
kubectl get pods -n ml-platform
kubectl get svc -n ml-platform
kubectl get hpa -n ml-platform

# 7. Get external IP
kubectl get svc kaliagent-ml-service -n ml-platform
```

---

## Detailed Deployment

### Step 1: Generate Manifests

```bash
cd ~/stsgym-work/agentic_ai/kali_agent_v4/phase14

# Generate all K8s manifests
python3 serving/auto_scaling.py

# Verify manifests
ls -la k8s_manifests/
# Should show:
# - deployment.yaml
# - hpa.yaml
# - service.yaml
# - ingress.yaml
# - configmap.yaml
# - kustomization.yaml
```

### Step 2: Create Namespace

```bash
kubectl create namespace ml-platform

# Label namespace for monitoring
kubectl label namespace ml-platform monitoring=enabled
```

### Step 3: Create Secrets

```bash
# Generate secure API key
API_KEY=$(openssl rand -hex 32)
echo "API Key: $API_KEY"  # Save this!

# Create secret
kubectl create secret generic kaliagent-ml-secrets \
  --from-literal=api-key=$API_KEY \
  --from-literal=jwt-secret=$(openssl rand -hex 32) \
  -n ml-platform

# Verify secret
kubectl get secret kaliagent-ml-secrets -n ml-platform
```

### Step 4: Configure GPU Nodes (Optional)

```bash
# Install NVIDIA GPU Operator
helm repo add nvidia https://helm.ngc.nvidia.com/nvidia
helm install gpu-operator nvidia/gpu-operator \
  --namespace gpu-operator --create-namespace

# Wait for GPU operator
kubectl wait --for=condition=ready pod -l app=nvidia-device-plugin-ds -n gpu-operator --timeout=300s

# Verify GPU nodes
kubectl get nodes -o custom-columns=NAME:.metadata.name,GPU:.status.allocatable/nvidia\.com/gpu
```

### Step 5: Deploy Application

```bash
# Deploy with kustomize
kubectl apply -k ./k8s_manifests/

# Or deploy individual manifests
kubectl apply -f k8s_manifests/deployment.yaml
kubectl apply -f k8s_manifests/service.yaml
kubectl apply -f k8s_manifests/hpa.yaml
kubectl apply -f k8s_manifests/configmap.yaml
kubectl apply -f k8s_manifests/ingress.yaml
```

### Step 6: Verify Deployment

```bash
# Check pods
kubectl get pods -n ml-platform

# Expected output:
# NAME                          READY   STATUS    RESTARTS   AGE
# kaliagent-ml-6d8f9b7c4-x2k9   1/1     Running   0          2m
# kaliagent-ml-6d8f9b7c4-p3m1   1/1     Running   0          2m
# kaliagent-ml-6d8f9b7c4-j7n4   1/1     Running   0          2m

# Check services
kubectl get svc -n ml-platform

# Expected output:
# NAME                  TYPE           CLUSTER-IP     EXTERNAL-IP     PORT(S)        AGE
# kaliagent-ml-service  LoadBalancer   10.96.123.45   203.0.113.100   80:30XXX/TCP   2m

# Check HPA
kubectl get hpa -n ml-platform

# Expected output:
# NAME             REFERENCE                   TARGETS   MINPODS   MAXPODS   REPLICAS   AGE
# kaliagent-ml-hpa Deployment/kaliagent-ml     0%/70%    2         20        3          2m

# Check logs
kubectl logs -f deployment/kaliagent-ml -n ml-platform
```

### Step 7: Configure Ingress (Optional)

```bash
# Install nginx-ingress if not present
helm repo add ingress-nginx https://kubernetes.github.io/ingress-nginx
helm install ingress-nginx ingress-nginx/ingress-nginx \
  --namespace ingress-nginx --create-namespace

# Update ingress with your domain
# Edit k8s_manifests/ingress.yaml
# Change: ml.kaliagent.local to your domain

# Apply ingress
kubectl apply -f k8s_manifests/ingress.yaml -n ml-platform

# Get ingress IP
kubectl get ingress kaliagent-ml-ingress -n ml-platform
```

### Step 8: Setup TLS (Optional but Recommended)

```bash
# Install cert-manager
helm repo add jetstack https://charts.jetstack.io
helm install cert-manager jetstack/cert-manager \
  --namespace cert-manager --create-namespace \
  --set installCRDs=true

# Create ClusterIssuer
cat <<EOF | kubectl apply -f -
apiVersion: cert-manager.io/v1
kind: ClusterIssuer
metadata:
  name: letsencrypt-prod
spec:
  acme:
    server: https://acme-v02.api.letsencrypt.org/directory
    email: your-email@example.com
    privateKeySecretRef:
      name: letsencrypt-prod
    solvers:
    - http01:
        ingress:
          class: nginx
EOF

# TLS will be automatically provisioned via ingress
```

---

## Monitoring Setup

### Deploy Prometheus

```bash
# Add Prometheus repo
helm repo add prometheus-community https://prometheus-community.github.io/helm-charts

# Install Prometheus
helm install prometheus prometheus-community/kube-prometheus-stack \
  --namespace monitoring --create-namespace \
  --set prometheus.service.type=LoadBalancer

# Access Prometheus
kubectl get svc -n monitoring | grep prometheus
# Visit: http://<EXTERNAL-IP>:9090
```

### Import Grafana Dashboard

```bash
# Generate dashboard
python3 serving/monitoring.py

# Get Grafana password
kubectl get secret prometheus-grafana \
  -n monitoring -o jsonpath="{.data.admin-password}" | base64 --decode

# Access Grafana
kubectl get svc -n monitoring | grep grafana
# Visit: http://<EXTERNAL-IP>:3000
# Login: admin / <password from above>

# Import dashboard
# Go to: Dashboards → Import
# Upload: grafana_dashboard.json (generated by monitoring.py)
```

### Configure Alerting

```bash
# Export alert rules
python3 -c "from phase14.serving.monitoring import AlertManager; AlertManager().export_rules('./alert_rules.json')"

# Import into Prometheus Alertmanager
# Configure in alertmanager.yml
```

---

## Auto-Scaling Configuration

### View HPA Status

```bash
# Watch HPA in real-time
kubectl get hpa kaliagent-ml-hpa -n ml-platform -w

# Expected behavior:
# - Scale up when CPU > 70%
# - Scale up when memory > 80%
# - Scale up when RPS > 100 per pod
# - Scale down after 5 min cooldown
```

### Manual Scaling

```bash
# Override HPA (temporary)
kubectl scale deployment kaliagent-ml --replicas=5 -n ml-platform

# HPA will regain control after 5 minutes
```

### Customize Scaling

```bash
# Edit HPA
kubectl edit hpa kaliagent-ml-hpa -n ml-platform

# Adjust thresholds:
# - targetCPUUtilizationPercentage: 70
# - targetMemoryUtilizationPercentage: 80
# - minReplicas: 2
# - maxReplicas: 20
```

---

## Security Hardening

### Enable Network Policies

```bash
# Create network policy
cat <<EOF | kubectl apply -f -
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: kaliagent-ml-network-policy
  namespace: ml-platform
spec:
  podSelector:
    matchLabels:
      app: kaliagent-ml
  policyTypes:
  - Ingress
  - Egress
  ingress:
  - from:
    - namespaceSelector:
        matchLabels:
          name: ingress-nginx
    ports:
    - protocol: TCP
      port: 8000
  egress:
  - {}
EOF
```

### Enable Pod Security Policy

```bash
# Create pod security policy
cat <<EOF | kubectl apply -f -
apiVersion: policy/v1beta1
kind: PodSecurityPolicy
metadata:
  name: kaliagent-ml-psp
spec:
  privileged: false
  allowPrivilegeEscalation: false
  requiredDropCapabilities:
  - ALL
  volumes:
  - 'configMap'
  - 'emptyDir'
  - 'secret'
  hostNetwork: false
  hostIPC: false
  hostPID: false
  runAsUser:
    rule: 'MustRunAsNonRoot'
  seLinux:
    rule: 'RunAsAny'
  fsGroup:
    rule: 'RunAsAny'
  supplementalGroups:
    rule: 'RunAsAny'
EOF
```

### Rotate Secrets

```bash
# Rotate API key
kubectl delete secret kaliagent-ml-secrets -n ml-platform
kubectl create secret generic kaliagent-ml-secrets \
  --from-literal=api-key=$(openssl rand -hex 32) \
  -n ml-platform

# Restart pods to pick up new secret
kubectl rollout restart deployment kaliagent-ml -n ml-platform
```

---

## Troubleshooting

### Pod Not Starting

```bash
# Check pod status
kubectl describe pod <pod-name> -n ml-platform

# Check logs
kubectl logs <pod-name> -n ml-platform

# Common issues:
# - ImagePullBackoff: Check image name and registry credentials
# - CrashLoopBackoff: Check application logs
# - Pending: Check node resources and taints
```

### HPA Not Scaling

```bash
# Check metrics-server
kubectl get pods -n kube-system | grep metrics-server

# Check HPA events
kubectl describe hpa kaliagent-ml-hpa -n ml-platform

# Verify metrics available
kubectl top pods -n ml-platform
```

### High Latency

```bash
# Check resource usage
kubectl top pods -n ml-platform

# Check if GPU is being used
kubectl exec <pod-name> -n ml-platform -- nvidia-smi

# Scale up manually
kubectl scale deployment kaliagent-ml --replicas=10 -n ml-platform

# Check network latency
kubectl exec <pod-name> -n ml-platform -- ping <service-name>
```

### GPU Issues

```bash
# Check GPU operator
kubectl get pods -n gpu-operator

# Check GPU allocation
kubectl describe node <node-name> | grep -A 5 "Allocated resources"

# Verify GPU in pod
kubectl exec <pod-name> -n ml-platform -- nvidia-smi
```

---

## Performance Tuning

### Resource Limits

```yaml
# In deployment.yaml, adjust:
resources:
  requests:
    cpu: "500m"      # Increase if CPU bound
    memory: "512Mi"  # Increase if memory bound
  limits:
    cpu: "2000m"     # Max CPU per pod
    memory: "2Gi"    # Max memory per pod
```

### HPA Thresholds

```yaml
# In hpa.yaml, adjust:
metrics:
- resource:
    name: cpu
    target:
      averageUtilization: 70  # Lower = more aggressive scaling
- resource:
    name: memory
    target:
      averageUtilization: 80  # Lower = more aggressive scaling
```

### Batch Size

```bash
# In configmap.yaml, adjust:
data:
  BATCH_SIZE: "32"  # Increase for better GPU utilization
  CACHE_TTL: "300"  # Increase for better cache hit rate
```

---

## Backup & Recovery

### Backup Configuration

```bash
# Export all manifests
kubectl get deployment,svc,hpa,configmap,ingress -n ml-platform -o yaml > backup.yaml

# Backup secrets (encrypted)
kubectl get secret kaliagent-ml-secrets -n ml-platform -o yaml > secrets-backup.yaml
```

### Restore from Backup

```bash
# Restore configuration
kubectl apply -f backup.yaml

# Restore secrets
kubectl apply -f secrets-backup.yaml
```

### Disaster Recovery

```bash
# In case of complete failure:
# 1. Recreate namespace
kubectl delete namespace ml-platform
kubectl create namespace ml-platform

# 2. Recreate secrets
kubectl create secret generic kaliagent-ml-secrets \
  --from-literal=api-key=<your-saved-api-key> \
  -n ml-platform

# 3. Redeploy
kubectl apply -k ./k8s_manifests/
```

---

## Cost Optimization

### Use Spot Instances

```yaml
# In deployment.yaml, add tolerations:
spec:
  tolerations:
  - key: "spot-instance"
    operator: "Equal"
    value: "true"
    effect: "NoSchedule"
```

### Right-Size Resources

```bash
# Monitor actual usage
kubectl top pods -n ml-platform

# Adjust requests/limits based on actual usage
# Reduce over-provisioned resources
```

### Scale Down at Night

```bash
# Create cronjob to scale down
cat <<EOF | kubectl apply -f -
apiVersion: batch/v1
kind: CronJob
metadata:
  name: kaliagent-ml-scale-down
  namespace: ml-platform
spec:
  schedule: "0 22 * * *"  # 10 PM daily
  jobTemplate:
    spec:
      template:
        spec:
          containers:
          - name: kubectl
            image: bitnami/kubectl
            command:
            - kubectl
            - scale
            - deployment/kaliagent-ml
            - --replicas=2
            - -n
            - ml-platform
          restartPolicy: OnFailure
EOF
```

---

## Production Checklist

- [ ] Namespace created
- [ ] Secrets created and saved
- [ ] Manifests generated
- [ ] Deployment applied
- [ ] Pods running (3+ replicas)
- [ ] Service has external IP
- [ ] HPA configured and active
- [ ] Monitoring deployed (Prometheus + Grafana)
- [ ] Alerts configured
- [ ] TLS enabled (if public)
- [ ] Network policies applied
- [ ] Backup completed
- [ ] Load testing passed
- [ ] Documentation updated
- [ ] Team trained

---

## Support

**Documentation:** phase14/PHASE_14_COMPLETE.md  
**Issues:** https://github.com/wezzels/kaliagent-v4/issues  
**Discord:** https://discord.com/invite/clawd  

---

*Created: April 29, 2026*  
*KaliAgent v5.0.0 - Production Deployment Guide*
