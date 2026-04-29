#!/usr/bin/env python3
"""
🧠 KaliAgent v5.0.0 - Phase 14 Sprint 1.3: Monitoring & Observability

Prometheus metrics, Grafana dashboards, and alerting:
- Prometheus metrics exporter
- Custom ML metrics (latency, throughput, accuracy)
- GPU monitoring
- Alert rules
- Grafana dashboard JSON

Author: KaliAgent Team
Status: Alpha (0.1.0)
"""

import logging
import time
import json
from typing import Dict, List, Optional
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
import threading

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger('Monitoring')

# Try to import prometheus_client
try:
    from prometheus_client import Counter, Histogram, Gauge, start_http_server, CollectorRegistry, generate_latest
    PROMETHEUS_AVAILABLE = True
except ImportError:
    PROMETHEUS_AVAILABLE = False
    logger.warning("⚠️  prometheus_client not available - install with: pip install prometheus-client")


@dataclass
class AlertRule:
    """Alerting rule definition"""
    name: str
    metric: str
    condition: str  # e.g., "> 0.95", "< 100"
    threshold: float
    duration_seconds: int = 300  # 5 min
    severity: str = "warning"  # warning, critical
    description: str = ""
    runbook_url: str = ""


class MLMetrics:
    """
    ML-specific metrics collection
    
    Tracks:
    - Inference latency
    - Throughput (requests/sec)
    - Model accuracy (if labels available)
    - Queue depth
    - Cache hit rate
    - GPU utilization
    """
    
    def __init__(self, registry: CollectorRegistry = None):
        self.registry = registry
        self.start_time = time.time()
        
        if PROMETHEUS_AVAILABLE:
            self._create_metrics()
            logger.info("✅ Prometheus metrics created")
    
    def _create_metrics(self):
        """Create Prometheus metrics"""
        
        # Counter metrics
        self.inference_total = Counter(
            'kaliagent_inference_total',
            'Total number of inferences',
            ['model', 'status']  # labels
        )
        
        self.requests_total = Counter(
            'kaliagent_requests_total',
            'Total API requests',
            ['endpoint', 'method', 'status']
        )
        
        # Histogram metrics (for latency distributions)
        self.inference_latency = Histogram(
            'kaliagent_inference_latency_seconds',
            'Inference latency in seconds',
            ['model', 'gpu'],
            buckets=[0.001, 0.005, 0.01, 0.025, 0.05, 0.1, 0.25, 0.5, 1.0, 2.5, 5.0]
        )
        
        self.request_latency = Histogram(
            'kaliagent_request_latency_seconds',
            'API request latency in seconds',
            ['endpoint'],
            buckets=[0.01, 0.025, 0.05, 0.1, 0.25, 0.5, 1.0, 2.5, 5.0, 10.0]
        )
        
        # Gauge metrics (current state)
        self.queue_depth = Gauge(
            'kaliagent_queue_depth',
            'Current queue depth',
            ['queue_name']
        )
        
        self.cache_hit_rate = Gauge(
            'kaliagent_cache_hit_rate',
            'Cache hit rate (0-1)',
            ['cache_name']
        )
        
        self.gpu_utilization = Gauge(
            'kaliagent_gpu_utilization_percent',
            'GPU utilization percentage',
            ['gpu_id']
        )
        
        self.gpu_memory = Gauge(
            'kaliagent_gpu_memory_bytes',
            'GPU memory used in bytes',
            ['gpu_id']
        )
        
        self.model_accuracy = Gauge(
            'kaliagent_model_accuracy',
            'Model accuracy (if labels available)',
            ['model', 'version']
        )
        
        self.active_connections = Gauge(
            'kaliagent_active_connections',
            'Number of active connections'
        )
    
    def record_inference(self, model: str, latency_sec: float, gpu: bool = False, status: str = "success"):
        """Record inference metric"""
        if not PROMETHEUS_AVAILABLE:
            return
        
        self.inference_total.labels(model=model, status=status).inc()
        self.inference_latency.labels(model=model, gpu=str(gpu).lower()).observe(latency_sec)
    
    def record_request(self, endpoint: str, method: str, latency_sec: float, status: int):
        """Record API request metric"""
        if not PROMETHEUS_AVAILABLE:
            return
        
        self.requests_total.labels(endpoint=endpoint, method=method, status=status).inc()
        self.request_latency.labels(endpoint=endpoint).observe(latency_sec)
    
    def set_queue_depth(self, queue_name: str, depth: int):
        """Set queue depth gauge"""
        if not PROMETHEUS_AVAILABLE:
            return
        self.queue_depth.labels(queue_name=queue_name).set(depth)
    
    def set_cache_hit_rate(self, cache_name: str, rate: float):
        """Set cache hit rate gauge"""
        if not PROMETHEUS_AVAILABLE:
            return
        self.cache_hit_rate.labels(cache_name=cache_name).set(rate)
    
    def set_gpu_metrics(self, gpu_id: str, utilization: float, memory_bytes: int):
        """Set GPU metrics"""
        if not PROMETHEUS_AVAILABLE:
            return
        self.gpu_utilization.labels(gpu_id=gpu_id).set(utilization)
        self.gpu_memory.labels(gpu_id=gpu_id).set(memory_bytes)
    
    def set_model_accuracy(self, model: str, version: str, accuracy: float):
        """Set model accuracy"""
        if not PROMETHEUS_AVAILABLE:
            return
        self.model_accuracy.labels(model=model, version=version).set(accuracy)
    
    def get_metrics_text(self) -> str:
        """Get metrics in Prometheus text format"""
        if not PROMETHEUS_AVAILABLE:
            return "# Prometheus not available"
        return generate_latest(self.registry).decode('utf-8')


class AlertManager:
    """
    Alerting system
    
    Features:
    - Define alert rules
    - Evaluate conditions
    - Send alerts (webhook, email, etc.)
    - Alert history
    """
    
    def __init__(self):
        self.rules: List[AlertRule] = []
        self.alerts_history: List[Dict] = []
        self.active_alerts: Dict[str, Dict] = {}
        
        # Create default rules
        self._create_default_rules()
        
        logger.info(f"🚨 Alert Manager initialized with {len(self.rules)} rules")
    
    def _create_default_rules(self):
        """Create default alerting rules"""
        
        self.rules.extend([
            AlertRule(
                name="HighInferenceLatency",
                metric="kaliagent_inference_latency_seconds",
                condition="> 0.5",
                threshold=0.5,
                duration_seconds=300,
                severity="warning",
                description="Inference latency exceeds 500ms for 5 minutes",
                runbook_url="https://wiki.internal/runbooks/high-latency"
            ),
            
            AlertRule(
                name="HighErrorRate",
                metric="kaliagent_requests_total",
                condition="error_rate > 0.05",
                threshold=0.05,
                duration_seconds=300,
                severity="critical",
                description="Error rate exceeds 5% for 5 minutes",
                runbook_url="https://wiki.internal/runbooks/high-error-rate"
            ),
            
            AlertRule(
                name="HighQueueDepth",
                metric="kaliagent_queue_depth",
                condition="> 500",
                threshold=500,
                duration_seconds=180,
                severity="warning",
                description="Queue depth exceeds 500 for 3 minutes",
                runbook_url="https://wiki.internal/runbooks/queue-backlog"
            ),
            
            AlertRule(
                name="LowCacheHitRate",
                metric="kaliagent_cache_hit_rate",
                condition="< 0.5",
                threshold=0.5,
                duration_seconds=600,
                severity="info",
                description="Cache hit rate below 50% for 10 minutes",
                runbook_url="https://wiki.internal/runbooks/low-cache-hit"
            ),
            
            AlertRule(
                name="HighGPUUtilization",
                metric="kaliagent_gpu_utilization_percent",
                condition="> 90",
                threshold=90.0,
                duration_seconds=300,
                severity="warning",
                description="GPU utilization above 90% for 5 minutes",
                runbook_url="https://wiki.internal/runbooks/high-gpu"
            ),
            
            AlertRule(
                name="GPUOutOfMemory",
                metric="kaliagent_gpu_memory_bytes",
                condition="> 0.95 * total_memory",
                threshold=0.95,
                duration_seconds=60,
                severity="critical",
                description="GPU memory usage above 95%",
                runbook_url="https://wiki.internal/runbooks/gpu-oom"
            )
        ])
    
    def evaluate_rules(self, metrics: Dict[str, float]) -> List[Dict]:
        """Evaluate alert rules against current metrics"""
        triggered_alerts = []
        
        for rule in self.rules:
            # Parse condition (simplified - real implementation would use PromQL)
            condition = rule.condition
            metric_name = rule.metric.split('_')[0]  # Simplified
            
            if metric_name in metrics:
                value = metrics[metric_name]
                
                # Evaluate condition
                triggered = False
                if ">" in condition:
                    triggered = value > rule.threshold
                elif "<" in condition:
                    triggered = value < rule.threshold
                elif "==" in condition:
                    triggered = value == rule.threshold
                
                if triggered:
                    alert = {
                        "rule_name": rule.name,
                        "metric": rule.metric,
                        "value": value,
                        "threshold": rule.threshold,
                        "condition": rule.condition,
                        "severity": rule.severity,
                        "description": rule.description,
                        "timestamp": datetime.now().isoformat(),
                        "runbook_url": rule.runbook_url
                    }
                    
                    triggered_alerts.append(alert)
                    self.alerts_history.append(alert)
                    self.active_alerts[rule.name] = alert
                    
                    logger.warning(f"🚨 ALERT: {rule.name} - {rule.description} (value={value}, threshold={rule.threshold})")
        
        return triggered_alerts
    
    def get_active_alerts(self) -> List[Dict]:
        """Get currently active alerts"""
        return list(self.active_alerts.values())
    
    def clear_alert(self, rule_name: str):
        """Clear an active alert"""
        if rule_name in self.active_alerts:
            del self.active_alerts[rule_name]
            logger.info(f"✅ Cleared alert: {rule_name}")
    
    def export_rules(self, filepath: str):
        """Export alert rules to Prometheus rule format"""
        prometheus_rules = {
            "groups": [
                {
                    "name": "kaliagent_alerts",
                    "rules": []
                }
            ]
        }
        
        for rule in self.rules:
            prometheus_rules["groups"][0]["rules"].append({
                "alert": rule.name,
                "expr": f"{rule.metric} {rule.condition}",
                "for": f"{rule.duration_seconds}s",
                "labels": {
                    "severity": rule.severity
                },
                "annotations": {
                    "summary": rule.name,
                    "description": rule.description,
                    "runbook_url": rule.runbook_url
                }
            })
        
        with open(filepath, 'w') as f:
            json.dump(prometheus_rules, f, indent=2)
        
        logger.info(f"💾 Exported {len(self.rules)} alert rules to {filepath}")


class GrafanaDashboard:
    """
    Grafana dashboard generator
    
    Creates JSON dashboard for import into Grafana
    """
    
    def __init__(self):
        self.dashboard = self._create_dashboard()
    
    def _create_dashboard(self) -> Dict:
        """Create Grafana dashboard JSON"""
        return {
            "dashboard": {
                "id": None,
                "uid": "kaliagent-ml",
                "title": "KaliAgent ML Platform",
                "tags": ["kaliagent", "ml", "security"],
                "timezone": "browser",
                "schemaVersion": 38,
                "version": 1,
                "refresh": "10s",
                "panels": [
                    self._create_inference_latency_panel(),
                    self._create_throughput_panel(),
                    self._create_queue_depth_panel(),
                    self._create_cache_panel(),
                    self._create_gpu_panel(),
                    self._create_error_rate_panel()
                ]
            }
        }
    
    def _create_inference_latency_panel(self) -> Dict:
        """Create inference latency panel"""
        return {
            "id": 1,
            "title": "Inference Latency (p99, p95, avg)",
            "type": "graph",
            "gridPos": {"h": 8, "w": 12, "x": 0, "y": 0},
            "targets": [
                {
                    "expr": "histogram_quantile(0.99, rate(kaliagent_inference_latency_seconds_bucket[5m]))",
                    "legendFormat": "p99"
                },
                {
                    "expr": "histogram_quantile(0.95, rate(kaliagent_inference_latency_seconds_bucket[5m]))",
                    "legendFormat": "p95"
                },
                {
                    "expr": "rate(kaliagent_inference_latency_seconds_sum[5m]) / rate(kaliagent_inference_latency_seconds_count[5m])",
                    "legendFormat": "avg"
                }
            ],
            "yAxes": [{"format": "s", "label": "Latency"}],
            "xAxis": {"mode": "time"}
        }
    
    def _create_throughput_panel(self) -> Dict:
        """Create throughput panel"""
        return {
            "id": 2,
            "title": "Throughput (requests/sec)",
            "type": "graph",
            "gridPos": {"h": 8, "w": 12, "x": 12, "y": 0},
            "targets": [
                {
                    "expr": "rate(kaliagent_requests_total[1m])",
                    "legendFormat": "{{endpoint}}"
                }
            ],
            "yAxes": [{"format": "reqps", "label": "Requests/sec"}]
        }
    
    def _create_queue_depth_panel(self) -> Dict:
        """Create queue depth panel"""
        return {
            "id": 3,
            "title": "Queue Depth",
            "type": "graph",
            "gridPos": {"h": 8, "w": 8, "x": 0, "y": 8},
            "targets": [
                {
                    "expr": "kaliagent_queue_depth",
                    "legendFormat": "{{queue_name}}"
                }
            ],
            "yAxes": [{"format": "short", "label": "Queue Depth"}],
            "alert": {
                "name": "High Queue Depth",
                "conditions": [
                    {
                        "evaluator": {"params": [500], "type": "gt"},
                        "operator": {"type": "and"},
                        "query": {"params": ["A", "5m", "now"]}
                    }
                ]
            }
        }
    
    def _create_cache_panel(self) -> Dict:
        """Create cache hit rate panel"""
        return {
            "id": 4,
            "title": "Cache Hit Rate",
            "type": "graph",
            "gridPos": {"h": 8, "w": 8, "x": 8, "y": 8},
            "targets": [
                {
                    "expr": "kaliagent_cache_hit_rate",
                    "legendFormat": "{{cache_name}}"
                }
            ],
            "yAxes": [{"format": "percentunit", "min": 0, "max": 1}]
        }
    
    def _create_gpu_panel(self) -> Dict:
        """Create GPU utilization panel"""
        return {
            "id": 5,
            "title": "GPU Utilization",
            "type": "graph",
            "gridPos": {"h": 8, "w": 8, "x": 16, "y": 8},
            "targets": [
                {
                    "expr": "kaliagent_gpu_utilization_percent",
                    "legendFormat": "GPU {{gpu_id}}"
                }
            ],
            "yAxes": [{"format": "percent", "min": 0, "max": 100}]
        }
    
    def _create_error_rate_panel(self) -> Dict:
        """Create error rate panel"""
        return {
            "id": 6,
            "title": "Error Rate",
            "type": "graph",
            "gridPos": {"h": 8, "w": 12, "x": 0, "y": 16},
            "targets": [
                {
                    "expr": "sum(rate(kaliagent_requests_total{status=~\"5..\"}[5m])) / sum(rate(kaliagent_requests_total[5m]))",
                    "legendFormat": "Error Rate"
                }
            ],
            "yAxes": [{"format": "percentunit", "min": 0}],
            "alert": {
                "name": "High Error Rate",
                "conditions": [
                    {
                        "evaluator": {"params": [0.05], "type": "gt"},
                        "operator": {"type": "and"},
                        "query": {"params": ["A", "5m", "now"]}
                    }
                ]
            }
        }
    
    def export(self, filepath: str):
        """Export dashboard to JSON file"""
        with open(filepath, 'w') as f:
            json.dump(self.dashboard, f, indent=2)
        
        logger.info(f"💾 Exported Grafana dashboard to {filepath}")


def start_monitoring_server(port: int = 9090):
    """Start Prometheus metrics server"""
    if not PROMETHEUS_AVAILABLE:
        logger.error("❌ Prometheus client not available")
        return
    
    start_http_server(port)
    logger.info(f"📊 Prometheus metrics server started on port {port}")
    logger.info(f"   Metrics endpoint: http://localhost:{port}/metrics")


def demo():
    """Demo monitoring system"""
    print("""
╔═══════════════════════════════════════════════════════════════╗
║     🧠 KALIAGENT v5.0.0 - MONITORING & OBSERVABILITY         ║
╚═══════════════════════════════════════════════════════════════╝

    """)
    
    if not PROMETHEUS_AVAILABLE:
        print("⚠️  Prometheus not available - install with: pip install prometheus-client")
        return
    
    # Initialize metrics
    metrics = MLMetrics()
    
    # Simulate some inferences
    print("📊 Recording metrics...")
    for i in range(100):
        latency = 0.05 + (i % 10) * 0.01
        metrics.record_inference("lstm_model", latency, gpu=True)
        metrics.record_request("/analyze/threat-report", "POST", latency * 2, 200)
    
    # Set gauges
    metrics.set_queue_depth("inference_queue", 42)
    metrics.set_cache_hit_rate("prediction_cache", 0.75)
    metrics.set_gpu_metrics("0", 65.5, 8 * 1024 * 1024 * 1024)
    
    print("✅ Metrics recorded")
    
    # Alert manager
    alert_manager = AlertManager()
    
    # Test alerting
    print("\n🚨 Testing alerting...")
    test_metrics = {
        "kaliagent_inference_latency_seconds": 0.6,  # Triggers HighInferenceLatency
        "kaliagent_queue_depth": 600,  # Triggers HighQueueDepth
        "kaliagent_cache_hit_rate": 0.3  # Triggers LowCacheHitRate
    }
    
    alerts = alert_manager.evaluate_rules(test_metrics)
    print(f"   Triggered {len(alerts)} alerts:")
    for alert in alerts:
        print(f"   - {alert['rule_name']}: {alert['description']}")
    
    # Export alert rules
    alert_manager.export_rules("./alert_rules.json")
    print("💾 Alert rules exported")
    
    # Grafana dashboard
    print("\n📈 Creating Grafana dashboard...")
    dashboard = GrafanaDashboard()
    dashboard.export("./grafana_dashboard.json")
    print("💾 Dashboard exported")
    
    # Start metrics server
    print("\n🚀 Starting Prometheus metrics server...")
    start_monitoring_server(port=9090)
    print("   Visit: http://localhost:9090/metrics")
    
    print("\n" + "="*70)
    print("✅ Monitoring demo complete!")
    print("="*70)


if __name__ == "__main__":
    demo()
