# Agentic AI Helm Chart

[Helm](https://helm.sh) chart for deploying Agentic AI on Kubernetes.

## Introduction

This chart bootstraps an Agentic AI deployment on a Kubernetes cluster using the Helm package manager.

It includes:
- Agentic AI application deployment with autoscaling
- Redis cluster for message bus and caching
- PostgreSQL database for persistent storage
- Prometheus metrics export
- Grafana dashboard integration
- Horizontal Pod Autoscaler (HPA)
- Service and Ingress configuration

## Prerequisites

- Kubernetes 1.19+
- Helm 3.0+
- PV provisioner support in the underlying infrastructure (optional)

## Installation

### Add Helm Repository

```bash
helm repo add agentic-ai https://wezzels.github.io/agentic-ai
helm repo update
```

### Install Chart

```bash
# Install with default values
helm install my-agentic-ai agentic-ai/agentic-ai

# Install with custom values
helm install my-agentic-ai agentic-ai/agentic-ai -f values.yaml

# Install in specific namespace
helm install my-agentic-ai agentic-ai/agentic-ai --namespace agentic-ai --create-namespace
```

## Configuration

The following table lists the configurable parameters of the Agentic AI chart and their default values.

| Parameter | Description | Default |
|-----------|-------------|---------|
| `replicaCount` | Number of replicas | `3` |
| `image.repository` | Image repository | `wezzels/agentic-ai` |
| `image.tag` | Image tag | `latest` |
| `image.pullPolicy` | Image pull policy | `IfNotPresent` |
| `service.type` | Service type | `ClusterIP` |
| `service.port` | Service port | `8000` |
| `resources.limits.cpu` | CPU limit | `2000m` |
| `resources.limits.memory` | Memory limit | `2048Mi` |
| `resources.requests.cpu` | CPU request | `500m` |
| `resources.requests.memory` | Memory request | `512Mi` |
| `autoscaling.enabled` | Enable autoscaling | `true` |
| `autoscaling.minReplicas` | Minimum replicas | `3` |
| `autoscaling.maxReplicas` | Maximum replicas | `10` |
| `autoscaling.targetCPUUtilizationPercentage` | CPU target | `80` |
| `redis.enabled` | Deploy Redis | `true` |
| `postgresql.enabled` | Deploy PostgreSQL | `true` |
| `prometheus.enabled` | Enable Prometheus metrics | `true` |
| `grafana.enabled` | Enable Grafana dashboards | `true` |

Specify each parameter using the `--set key=value[,key=value]` argument to `helm install`. For example:

```bash
helm install my-agentic-ai agentic-ai/agentic-ai \
  --set replicaCount=5 \
  --set redis.enabled=true \
  --set postgresql.enabled=true
```

Alternatively, a YAML file that specifies the values for the parameters can be provided while installing the chart. For example:

```bash
helm install my-agentic-ai agentic-ai/agentic-ai -f values.yaml
```

## Uninstallation

To uninstall/delete the `my-agentic-ai` deployment:

```bash
helm uninstall my-agentic-ai
```

The command removes all the Kubernetes components associated with the chart and deletes the release.

## Scaling

### Manual Scaling

```bash
kubectl scale deployment my-agentic-ai --replicas=5
```

### Autoscaling

The chart includes HPA configuration that automatically scales based on CPU and memory utilization:

```yaml
autoscaling:
  enabled: true
  minReplicas: 3
  maxReplicas: 10
  targetCPUUtilizationPercentage: 80
  targetMemoryUtilizationPercentage: 80
```

## Monitoring

### Prometheus Metrics

Enable Prometheus metrics export:

```yaml
prometheus:
  enabled: true
  port: 9090
```

Metrics are exposed at `/metrics` endpoint.

### Grafana Dashboards

Enable Grafana dashboard integration:

```yaml
grafana:
  enabled: true
  dashboards:
    - name: "Agentic AI Overview"
    - name: "Agent Metrics"
    - name: "Chaos Engineering"
```

## High Availability

For production deployments, enable HA features:

```yaml
# Multiple replicas with autoscaling
replicaCount: 3
autoscaling:
  enabled: true
  minReplicas: 3
  maxReplicas: 10

# Redis replication
redis:
  architecture: replication
  replica:
    replicaCount: 2

# PostgreSQL with read replicas
postgresql:
  readReplicas:
    replicaCount: 2

# Pod disruption budget
podDisruptionBudget:
  enabled: true
  minAvailable: 2
```

## Security

### Network Policies

Enable network policies:

```yaml
networkPolicy:
  enabled: true
  allowExternal: false
```

### Secrets Management

Secrets are managed via Kubernetes Secrets:

```bash
# View secrets
kubectl get secrets my-agentic-ai-secrets

# Get secret value
kubectl get secret my-agentic-ai-secrets -o jsonpath="{.data.secret-key}" | base64 --decode
```

## Troubleshooting

### Check Pod Status

```bash
kubectl get pods -l app.kubernetes.io/name=agentic-ai
```

### View Logs

```bash
kubectl logs -l app.kubernetes.io/name=agentic-ai -f
```

### Port Forward

```bash
kubectl port-forward svc/my-agentic-ai 8000:8000
```

Then access at http://localhost:8000

### Debug Values

```bash
helm install my-agentic-ai agentic-ai/agentic-ai --debug --dry-run
```

## Upgrading

### Upgrade Chart

```bash
helm upgrade my-agentic-ai agentic-ai/agentic-ai
```

### Upgrade with New Values

```bash
helm upgrade my-agentic-ai agentic-ai/agentic-ai -f new-values.yaml
```

## Version Compatibility

| Chart Version | App Version | Kubernetes | Helm |
|---------------|-------------|------------|------|
| 1.0.0 | 1.0.0 | 1.19+ | 3.0+ |

## Support

- GitHub Issues: https://github.com/wezzels/agentic-ai/issues
- Documentation: https://github.com/wezzels/agentic-ai/tree/main/docs
- Discord: https://discord.com/invite/clawd

## License

MIT License - see [LICENSE](https://github.com/wezzels/agentic-ai/blob/main/LICENSE)
