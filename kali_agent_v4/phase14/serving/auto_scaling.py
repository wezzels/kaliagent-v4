#!/usr/bin/env python3
"""
🧠 KaliAgent v5.0.0 - Phase 14 Sprint 1.3: Auto-Scaling & Load Balancing

Kubernetes deployment and auto-scaling:
- HPA (Horizontal Pod Autoscaler) configs
- Load balancer setup
- Health check endpoints
- Graceful shutdown
- Rolling updates

Author: KaliAgent Team
Status: Alpha (0.1.0)
"""

import logging
import json
import time
from typing import Dict, List, Optional
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger('AutoScaling')


@dataclass
class ScalingConfig:
    """Auto-scaling configuration"""
    min_replicas: int = 2
    max_replicas: int = 20
    target_cpu_utilization: int = 70
    target_memory_utilization: int = 80
    target_requests_per_second: int = 100
    scale_up_cooldown_seconds: int = 60
    scale_down_cooldown_seconds: int = 300


@dataclass
class PodStatus:
    """Pod status information"""
    pod_id: str
    status: str  # running, pending, terminating
    cpu_utilization: float
    memory_utilization: float
    requests_per_second: float
    created_at: str
    last_seen: str


class AutoScaler:
    """
    Horizontal Pod Autoscaler (HPA) implementation
    
    Features:
    - CPU-based scaling
    - Memory-based scaling
    - Request-based scaling
    - Cooldown periods
    - Min/max replica limits
    """
    
    VERSION = "0.1.0"
    
    def __init__(self, config: ScalingConfig = None):
        self.config = config or ScalingConfig()
        self.current_replicas = self.config.min_replicas
        self.last_scale_up = 0
        self.last_scale_down = 0
        self.pod_statuses: List[PodStatus] = []
        self.scaling_history: List[Dict] = []
        
        logger.info(f"⚖️ AutoScaler v{self.VERSION}")
        logger.info(f"   Min replicas: {self.config.min_replicas}")
        logger.info(f"   Max replicas: {self.config.max_replicas}")
        logger.info(f"   Target CPU: {self.config.target_cpu_utilization}%")
    
    def update_pod_statuses(self, statuses: List[PodStatus]):
        """Update pod statuses"""
        self.pod_statuses = statuses
    
    def calculate_desired_replicas(self) -> int:
        """Calculate desired replicas based on metrics"""
        if not self.pod_statuses:
            return self.config.min_replicas
        
        # Calculate average metrics
        avg_cpu = sum(p.cpu_utilization for p in self.pod_statuses) / len(self.pod_statuses)
        avg_memory = sum(p.memory_utilization for p in self.pod_statuses) / len(self.pod_statuses)
        total_rps = sum(p.requests_per_second for p in self.pod_statuses)
        
        # CPU-based scaling
        cpu_replicas = int(self.current_replicas * (avg_cpu / self.config.target_cpu_utilization))
        
        # Memory-based scaling
        memory_replicas = int(self.current_replicas * (avg_memory / self.config.target_memory_utilization))
        
        # Request-based scaling
        rps_replicas = int(total_rps / self.config.target_requests_per_second)
        
        # Take the maximum of all scaling strategies
        desired = max(cpu_replicas, memory_replicas, rps_replicas, self.config.min_replicas)
        desired = min(desired, self.config.max_replicas)
        
        logger.debug(f"   CPU suggests: {cpu_replicas}, Memory: {memory_replicas}, RPS: {rps_replicas}")
        logger.debug(f"   Desired replicas: {desired}")
        
        return desired
    
    def scale(self) -> Dict:
        """Perform scaling decision"""
        current_time = time.time()
        desired = self.calculate_desired_replicas()
        
        action = "none"
        reason = "Metrics within target range"
        
        if desired > self.current_replicas:
            # Scale up
            if current_time - self.last_scale_up >= self.config.scale_up_cooldown_seconds:
                action = "scale_up"
                reason = f"High load detected (desired: {desired}, current: {self.current_replicas})"
                self.last_scale_up = current_time
                self.current_replicas = desired
        elif desired < self.current_replicas:
            # Scale down
            if current_time - self.last_scale_down >= self.config.scale_down_cooldown_seconds:
                action = "scale_down"
                reason = f"Low load detected (desired: {desired}, current: {self.current_replicas})"
                self.last_scale_down = current_time
                self.current_replicas = desired
        
        # Record scaling event
        event = {
            "timestamp": datetime.now().isoformat(),
            "action": action,
            "reason": reason,
            "previous_replicas": self.current_replicas,
            "new_replicas": desired if action != "none" else self.current_replicas,
            "metrics": {
                "avg_cpu": sum(p.cpu_utilization for p in self.pod_statuses) / max(len(self.pod_statuses), 1),
                "avg_memory": sum(p.memory_utilization for p in self.pod_statuses) / max(len(self.pod_statuses), 1),
                "total_rps": sum(p.requests_per_second for p in self.pod_statuses)
            }
        }
        
        self.scaling_history.append(event)
        
        if action != "none":
            logger.info(f"⚖️  Scaling: {action} - {reason}")
        
        return event
    
    def get_status(self) -> Dict:
        """Get autoscaler status"""
        return {
            "current_replicas": self.current_replicas,
            "min_replicas": self.config.min_replicas,
            "max_replicas": self.config.max_replicas,
            "target_cpu_utilization": self.config.target_cpu_utilization,
            "scaling_events": len(self.scaling_history),
            "last_scale_up": datetime.fromtimestamp(self.last_scale_up).isoformat() if self.last_scale_up else None,
            "last_scale_down": datetime.fromtimestamp(self.last_scale_down).isoformat() if self.last_scale_down else None
        }


class KubernetesDeployer:
    """
    Kubernetes deployment generator
    
    Generates:
    - Deployment YAML
    - Service YAML
    - HPA YAML
    - Ingress YAML
    - ConfigMap YAML
    """
    
    def __init__(self, app_name: str = "kaliagent-ml", namespace: str = "ml-platform"):
        self.app_name = app_name
        self.namespace = namespace
    
    def generate_deployment(self, replicas: int = 3, image: str = "kaliagent-ml:latest") -> str:
        """Generate Kubernetes Deployment YAML"""
        return f"""apiVersion: apps/v1
kind: Deployment
metadata:
  name: {self.app_name}
  namespace: {self.namespace}
  labels:
    app: {self.app_name}
    version: v5.0.0
spec:
  replicas: {replicas}
  selector:
    matchLabels:
      app: {self.app_name}
  template:
    metadata:
      labels:
        app: {self.app_name}
        version: v5.0.0
    spec:
      containers:
      - name: {self.app_name}
        image: {image}
        ports:
        - containerPort: 8000
          name: http
        - containerPort: 9090
          name: metrics
        resources:
          requests:
            cpu: "500m"
            memory: "512Mi"
          limits:
            cpu: "2000m"
            memory: "2Gi"
        livenessProbe:
          httpGet:
            path: /health
            port: 8000
          initialDelaySeconds: 30
          periodSeconds: 10
        readinessProbe:
          httpGet:
            path: /health
            port: 8000
          initialDelaySeconds: 5
          periodSeconds: 5
        env:
        - name: KALIAGENT_API_KEY
          valueFrom:
            secretKeyRef:
              name: {self.app_name}-secrets
              key: api-key
        - name: KALIAGENT_HOST
          value: "0.0.0.0"
        - name: KALIAGENT_PORT
          value: "8000"
      imagePullSecrets:
      - name: registry-secret
"""
    
    def generate_hpa(self, min_replicas: int = 2, max_replicas: int = 20) -> str:
        """Generate HorizontalPodAutoscaler YAML"""
        return f"""apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: {self.app_name}-hpa
  namespace: {self.namespace}
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: {self.app_name}
  minReplicas: {min_replicas}
  maxReplicas: {max_replicas}
  metrics:
  - type: Resource
    resource:
      name: cpu
      target:
        type: Utilization
        averageUtilization: 70
  - type: Resource
    resource:
      name: memory
      target:
        type: Utilization
        averageUtilization: 80
  - type: Pods
    pods:
      metric:
        name: kaliagent_requests_total
      target:
        type: AverageValue
        averageValue: "100"
  behavior:
    scaleUp:
      stabilizationWindowSeconds: 60
      policies:
      - type: Percent
        value: 100
        periodSeconds: 15
    scaleDown:
      stabilizationWindowSeconds: 300
      policies:
      - type: Percent
        value: 10
        periodSeconds: 60
"""
    
    def generate_service(self) -> str:
        """Generate Kubernetes Service YAML"""
        return f"""apiVersion: v1
kind: Service
metadata:
  name: {self.app_name}-service
  namespace: {self.namespace}
  labels:
    app: {self.app_name}
spec:
  type: LoadBalancer
  ports:
  - port: 80
    targetPort: 8000
    protocol: TCP
    name: http
  - port: 9090
    targetPort: 9090
    protocol: TCP
    name: metrics
  selector:
    app: {self.app_name}
"""
    
    def generate_ingress(self, domain: str = "ml.kaliagent.local") -> str:
        """Generate Ingress YAML"""
        return f"""apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: {self.app_name}-ingress
  namespace: {self.namespace}
  annotations:
    nginx.ingress.kubernetes.io/ssl-redirect: "true"
    nginx.ingress.kubernetes.io/rate-limit: "100"
    cert-manager.io/cluster-issuer: "letsencrypt-prod"
spec:
  ingressClassName: nginx
  tls:
  - hosts:
    - {domain}
    secretName: {self.app_name}-tls
  rules:
  - host: {domain}
    http:
      paths:
      - path: /
        pathType: Prefix
        backend:
          service:
            name: {self.app_name}-service
            port:
              number: 80
"""
    
    def generate_configmap(self, config: Dict) -> str:
        """Generate ConfigMap YAML"""
        config_yaml = "\n".join(f"  {key}: \"{value}\"" for key, value in config.items())
        
        return f"""apiVersion: v1
kind: ConfigMap
metadata:
  name: {self.app_name}-config
  namespace: {self.namespace}
data:
{config_yaml}
"""
    
    def export_all(self, output_dir: str = "./k8s"):
        """Export all Kubernetes manifests"""
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)
        
        # Generate manifests
        manifests = {
            "deployment.yaml": self.generate_deployment(),
            "hpa.yaml": self.generate_hpa(),
            "service.yaml": self.generate_service(),
            "ingress.yaml": self.generate_ingress(),
            "configmap.yaml": self.generate_configmap({
                "LOG_LEVEL": "info",
                "ENABLE_GPU": "true",
                "BATCH_SIZE": "32",
                "CACHE_TTL": "300"
            })
        }
        
        # Write files
        for filename, content in manifests.items():
            filepath = output_path / filename
            with open(filepath, 'w') as f:
                f.write(content)
            logger.info(f"💾 Exported {filepath}")
        
        # Create kustomization
        kustomization = {
            "apiVersion": "kustomize.config.k8s.io/v1beta1",
            "kind": "Kustomization",
            "resources": list(manifests.keys()),
            "namespace": self.namespace
        }
        
        with open(output_path / "kustomization.yaml", 'w') as f:
            json.dump(kustomization, f, indent=2)
        
        logger.info(f"💾 Exported kustomization.yaml")
        logger.info(f"\n🚀 Deploy with:")
        logger.info(f"   kubectl apply -k {output_dir}/")


def demo():
    """Demo auto-scaling system"""
    print("""
╔═══════════════════════════════════════════════════════════════╗
║     🧠 KALIAGENT v5.0.0 - AUTO-SCALING & LOAD BALANCING      ║
╚═══════════════════════════════════════════════════════════════╝

    """)
    
    # Initialize autoscaler
    config = ScalingConfig(
        min_replicas=2,
        max_replicas=10,
        target_cpu_utilization=70,
        target_memory_utilization=80
    )
    
    scaler = AutoScaler(config)
    
    # Simulate pod metrics
    print("⚖️  Simulating pod metrics...")
    for i in range(5):
        pods = [
            PodStatus(
                pod_id=f"pod-{i}-{j}",
                status="running",
                cpu_utilization=60 + (j * 10),
                memory_utilization=70 + (j * 5),
                requests_per_second=80 + (j * 20),
                created_at=datetime.now().isoformat(),
                last_seen=datetime.now().isoformat()
            )
            for j in range(3)
        ]
        
        scaler.update_pod_statuses(pods)
        decision = scaler.scale()
        
        print(f"   Round {i+1}: {scaler.current_replicas} replicas, "
              f"Action: {decision['action']}")
    
    # Show status
    print("\n📊 Autoscaler Status:")
    status = scaler.get_status()
    for key, value in status.items():
        print(f"   {key}: {value}")
    
    # Generate K8s manifests
    print("\n🚀 Generating Kubernetes manifests...")
    deployer = KubernetesDeployer(app_name="kaliagent-ml", namespace="ml-platform")
    deployer.export_all("./k8s_manifests")
    
    print("\n" + "="*70)
    print("✅ Auto-scaling demo complete!")
    print("="*70)


if __name__ == "__main__":
    demo()
