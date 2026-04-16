"""
Demo API Server - Mock Data for Dashboard
==========================================

Provides mock data API so the dashboard works standalone
without requiring live agent connections.
"""

import json
import random
from datetime import datetime, timedelta
from typing import List, Dict, Any
from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import uvicorn

app = FastAPI(
    title="Agentic AI Demo API",
    description="Mock data API for Agentic AI Dashboard",
    version="1.0.0",
)

# Enable CORS for dashboard
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ============================================================================
# Mock Data Generators
# ============================================================================

def generate_chaos_experiments(count: int = 10) -> List[Dict[str, Any]]:
    """Generate mock chaos experiments."""
    experiment_types = [
        "instance_termination", "latency_injection", "network_partition",
        "cpu_stress", "memory_stress", "az_failure", "region_failure",
    ]
    severities = ["low", "medium", "high", "critical"]
    statuses = ["completed", "running", "scheduled", "failed"]
    
    experiments = []
    for i in range(count):
        exp = {
            "experiment_id": f"exp-{random.randint(1000, 9999)}",
            "name": f"{random.choice(['AZ', 'Region', 'Instance', 'Network'])} Failure Test {i+1}",
            "experiment_type": random.choice(experiment_types),
            "severity": random.choice(severities),
            "status": random.choice(statuses),
            "duration_minutes": random.randint(15, 60),
            "created_at": (datetime.utcnow() - timedelta(days=random.randint(0, 30))).isoformat(),
            "target_count": random.randint(1, 10),
            "success_rate": random.uniform(0.7, 1.0) if random.random() > 0.2 else None,
        }
        experiments.append(exp)
    
    return experiments


def generate_chaos_runs(experiment_id: str, count: int = 5) -> List[Dict[str, Any]]:
    """Generate mock experiment runs."""
    statuses = ["success", "failure", "partial"]
    targets = ["i-abc123", "i-def456", "i-ghi789", "i-jkl012"]
    
    runs = []
    for i in range(count):
        run = {
            "run_id": f"run-{random.randint(1000, 9999)}",
            "experiment_id": experiment_id,
            "status": random.choice(statuses),
            "target": random.choice(targets),
            "started_at": (datetime.utcnow() - timedelta(hours=random.randint(1, 100))).isoformat(),
            "duration_seconds": random.randint(60, 600),
            "resiliency_score": random.uniform(60, 100),
            "findings": random.randint(0, 5),
        }
        runs.append(run)
    
    return runs


def generate_vendors(count: int = 15) -> List[Dict[str, Any]]:
    """Generate mock vendors."""
    tiers = ["tier_1", "tier_2", "tier_3", "tier_4"]
    categories = ["saas", "cloud", "infrastructure", "security", "analytics"]
    statuses = ["active", "pending_review", "under_assessment"]
    
    vendors = []
    for i in range(count):
        vendor = {
            "vendor_id": f"vendor-{random.randint(1000, 9999)}",
            "name": f"{random.choice(['Cloud', 'Data', 'Secure', 'Tech', 'Smart'])}{random.choice(['Corp', 'Inc', 'LLC', 'Systems'])} {i+1}",
            "tier": random.choice(tiers),
            "category": random.choice(categories),
            "status": random.choice(statuses),
            "risk_score": random.uniform(0.1, 0.9),
            "inherent_risk": random.uniform(0.2, 0.8),
            "residual_risk": random.uniform(0.1, 0.6),
            "last_assessment": (datetime.utcnow() - timedelta(days=random.randint(0, 180))).isoformat(),
            "open_findings": random.randint(0, 10),
            "new_alerts": random.randint(0, 5),
        }
        vendors.append(vendor)
    
    return vendors


def generate_audits(count: int = 8) -> List[Dict[str, Any]]:
    """Generate mock audits."""
    types = ["it_general", "compliance", "internal", "external", "soc2", "iso27001"]
    statuses = ["planning", "in_progress", "fieldwork", "reporting", "completed"]
    
    audits = []
    for i in range(count):
        audit = {
            "audit_id": f"audit-{random.randint(1000, 9999)}",
            "title": f"{random.choice(['SOC2', 'ISO27001', 'ITGC', 'Compliance'])} Audit {2024 + random.randint(0, 2)}",
            "audit_type": random.choice(types),
            "status": random.choice(statuses),
            "auditor": f"auditor{random.randint(1, 10)}@auditfirm.com",
            "auditee": f"{random.choice(['Finance', 'IT', 'HR', 'Operations'])} Department",
            "start_date": (datetime.utcnow() - timedelta(days=random.randint(0, 90))).isoformat(),
            "end_date": (datetime.utcnow() + timedelta(days=random.randint(0, 60))).isoformat(),
            "findings_count": random.randint(0, 20),
            "controls_tested": random.randint(10, 100),
            "effectiveness_rate": random.uniform(0.6, 1.0),
        }
        audits.append(audit)
    
    return audits


def generate_cloud_findings(count: int = 20) -> List[Dict[str, Any]]:
    """Generate mock cloud security findings."""
    providers = ["aws", "azure", "gcp"]
    severities = ["critical", "high", "medium", "low"]
    statuses = ["open", "in_progress", "resolved", "accepted"]
    services = ["ec2", "s3", "rds", "lambda", "iam", "vpc", "eks"]
    
    findings = []
    for i in range(count):
        finding = {
            "finding_id": f"finding-{random.randint(1000, 9999)}",
            "title": f"{random.choice(['Unencrypted', 'Public', 'Overprivileged', 'Unused', 'Misconfigured'])} {random.choice(services).upper()} Resource",
            "severity": random.choice(severities),
            "status": random.choice(statuses),
            "cloud_provider": random.choice(providers),
            "service": random.choice(services),
            "resource_id": f"{random.choice(services)}-{random.randint(1000, 9999)}",
            "region": random.choice(["us-east-1", "us-west-2", "eu-west-1", "ap-southeast-1"]),
            "created_at": (datetime.utcnow() - timedelta(days=random.randint(0, 60))).isoformat(),
            "remediation_steps": f"Review and fix {random.choice(services)} configuration",
        }
        findings.append(finding)
    
    return findings


def generate_ml_models(count: int = 10) -> List[Dict[str, Any]]:
    """Generate mock ML models."""
    frameworks = ["tensorflow", "pytorch", "sklearn", "xgboost"]
    stages = ["development", "staging", "production", "deprecated"]
    types = ["classification", "regression", "clustering", "forecasting"]
    
    models = []
    for i in range(count):
        model = {
            "model_id": f"model-{random.randint(1000, 9999)}",
            "name": f"{random.choice(['Fraud', 'Churn', 'Demand', 'Risk', 'Quality'])} {random.choice(['Detector', 'Predictor', 'Classifier', 'Forecaster'])}",
            "framework": random.choice(frameworks),
            "stage": random.choice(stages),
            "model_type": random.choice(types),
            "version": f"v{random.randint(1, 5)}.{random.randint(0, 9)}.{random.randint(0, 9)}",
            "created_at": (datetime.utcnow() - timedelta(days=random.randint(0, 180))).isoformat(),
            "metrics": {
                "accuracy": random.uniform(0.7, 0.99),
                "precision": random.uniform(0.7, 0.99),
                "recall": random.uniform(0.7, 0.99),
                "f1_score": random.uniform(0.7, 0.99),
            },
            "drift_score": random.uniform(0, 0.3),
            "last_trained": (datetime.utcnow() - timedelta(days=random.randint(0, 30))).isoformat(),
        }
        models.append(model)
    
    return models


def generate_ml_experiments(count: int = 15) -> List[Dict[str, Any]]:
    """Generate mock ML experiments."""
    statuses = ["running", "completed", "failed", "queued"]
    types = ["classification", "regression", "clustering"]
    
    experiments = []
    for i in range(count):
        exp = {
            "experiment_id": f"exp-ml-{random.randint(1000, 9999)}",
            "name": f"Experiment {random.choice(['A', 'B', 'C', 'D'])}-{random.randint(1, 100)}",
            "model_type": random.choice(types),
            "status": random.choice(statuses),
            "created_at": (datetime.utcnow() - timedelta(days=random.randint(0, 60))).isoformat(),
            "completed_at": (datetime.utcnow() - timedelta(days=random.randint(0, 30))).isoformat() if random.random() > 0.3 else None,
            "metrics": {
                "loss": random.uniform(0.1, 2.0),
                "accuracy": random.uniform(0.7, 0.99),
                "val_accuracy": random.uniform(0.65, 0.98),
            } if random.random() > 0.3 else {},
            "hyperparameters": {
                "learning_rate": random.uniform(0.001, 0.1),
                "batch_size": random.choice([16, 32, 64, 128]),
                "epochs": random.randint(10, 100),
            },
        }
        experiments.append(exp)
    
    return experiments


def generate_system_health() -> Dict[str, Any]:
    """Generate mock system health data."""
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "agents": {
            "total": 33,
            "healthy": random.randint(30, 33),
            "degraded": random.randint(0, 2),
            "unhealthy": 0,
        },
        "services": {
            "redis": {"status": "healthy", "latency_ms": random.uniform(0.5, 2.0)},
            "database": {"status": "healthy", "connections": random.randint(10, 50)},
            "message_bus": {"status": "healthy", "queue_depth": random.randint(0, 100)},
            "task_queue": {"status": "healthy", "pending_tasks": random.randint(0, 50)},
        },
        "performance": {
            "requests_per_second": random.uniform(500, 700),
            "p99_latency_ms": random.uniform(2, 5),
            "p95_latency_ms": random.uniform(1, 3),
            "p50_latency_ms": random.uniform(0.3, 1),
        },
        "uptime_hours": random.randint(100, 1000),
    }


# ============================================================================
# API Endpoints
# ============================================================================

@app.get("/")
def root():
    """API root."""
    return {
        "name": "Agentic AI Demo API",
        "version": "1.0.0",
        "status": "running",
        "timestamp": datetime.utcnow().isoformat(),
    }


@app.get("/health")
def health():
    """Health check endpoint."""
    return {"status": "healthy", "timestamp": datetime.utcnow().isoformat()}


# Chaos Endpoints

@app.get("/api/chaos/experiments")
def get_chaos_experiments(
    limit: int = Query(default=20, ge=1, le=100),
    status: str = Query(default=None),
):
    """Get chaos experiments."""
    experiments = generate_chaos_experiments(limit)
    if status:
        experiments = [e for e in experiments if e["status"] == status]
    return {"experiments": experiments, "total": len(experiments)}


@app.get("/api/chaos/experiments/{experiment_id}/runs")
def get_chaos_runs(experiment_id: str, limit: int = Query(default=10, ge=1, le=50)):
    """Get experiment runs."""
    runs = generate_chaos_runs(experiment_id, limit)
    return {"runs": runs, "total": len(runs)}


@app.get("/api/chaos/status")
def get_chaos_status():
    """Get chaos dashboard status."""
    experiments = generate_chaos_experiments(50)
    runs = []
    for exp in experiments[:10]:
        runs.extend(generate_chaos_runs(exp["experiment_id"], 3))
    
    completed = [e for e in experiments if e["status"] == "completed"]
    success_rate = sum(e.get("success_rate", 0) for e in completed) / max(len(completed), 1)
    
    return {
        "experiments": {
            "total": len(experiments),
            "running": len([e for e in experiments if e["status"] == "running"]),
            "completed": len(completed),
            "failed": len([e for e in experiments if e["status"] == "failed"]),
        },
        "runs": {
            "total": len(runs),
            "success_rate": success_rate * 100,
        },
        "resiliency": {
            "average_score": sum(r.get("resiliency_score", 80) for r in runs) / max(len(runs), 1),
        },
    }


# Vendor Risk Endpoints

@app.get("/api/vendors")
def get_vendors(
    limit: int = Query(default=20, ge=1, le=100),
    tier: int = Query(default=None, ge=1, le=4),
):
    """Get vendors."""
    vendors = generate_vendors(limit)
    if tier:
        vendors = [v for v in vendors if v["tier"] == f"tier_{tier}"]
    return {"vendors": vendors, "total": len(vendors)}


@app.get("/api/vendors/{vendor_id}")
def get_vendor(vendor_id: str):
    """Get vendor details."""
    vendors = generate_vendors(100)
    vendor = next((v for v in vendors if v["vendor_id"] == vendor_id), None)
    if not vendor:
        raise HTTPException(status_code=404, detail="Vendor not found")
    return vendor


@app.get("/api/vendors/{vendor_id}/report")
def get_vendor_report(vendor_id: str):
    """Get vendor risk report."""
    vendors = generate_vendors(100)
    vendor = next((v for v in vendors if v["vendor_id"] == vendor_id), None)
    if not vendor:
        raise HTTPException(status_code=404, detail="Vendor not found")
    
    return {
        "vendor": vendor,
        "risk": {
            "inherent": vendor["inherent_risk"],
            "residual": vendor["residual_risk"],
            "trend": "decreasing" if random.random() > 0.5 else "increasing",
        },
        "findings": {
            "open": vendor["open_findings"],
            "critical": random.randint(0, vendor["open_findings"]),
            "high": random.randint(0, vendor["open_findings"]),
        },
        "alerts": {
            "new": vendor["new_alerts"],
            "acknowledged": random.randint(0, vendor["new_alerts"]),
        },
    }


# Audit Endpoints

@app.get("/api/audits")
def get_audits(limit: int = Query(default=20, ge=1, le=100)):
    """Get audits."""
    audits = generate_audits(limit)
    return {"audits": audits, "total": len(audits)}


@app.get("/api/audits/{audit_id}")
def get_audit(audit_id: str):
    """Get audit details."""
    audits = generate_audits(100)
    audit = next((a for a in audits if a["audit_id"] == audit_id), None)
    if not audit:
        raise HTTPException(status_code=404, detail="Audit not found")
    return audit


@app.get("/api/audits/{audit_id}/report")
def get_audit_report(audit_id: str):
    """Get audit report."""
    audits = generate_audits(100)
    audit = next((a for a in audits if a["audit_id"] == audit_id), None)
    if not audit:
        raise HTTPException(status_code=404, detail="Audit not found")
    
    return {
        "audit": audit,
        "controls": {
            "total": audit["controls_tested"],
            "effective": int(audit["controls_tested"] * audit["effectiveness_rate"]),
            "ineffective": int(audit["controls_tested"] * (1 - audit["effectiveness_rate"])),
            "effectiveness_rate": audit["effectiveness_rate"] * 100,
        },
        "findings": {
            "total": audit["findings_count"],
            "open": random.randint(0, audit["findings_count"]),
            "closed": random.randint(0, audit["findings_count"]),
        },
        "evidence": {
            "total": random.randint(50, 200),
            "pending_review": random.randint(0, 20),
        },
    }


# Cloud Security Endpoints

@app.get("/api/cloud/findings")
def get_cloud_findings(
    limit: int = Query(default=50, ge=1, le=200),
    severity: str = Query(default=None),
    provider: str = Query(default=None),
):
    """Get cloud security findings."""
    findings = generate_cloud_findings(limit)
    if severity:
        findings = [f for f in findings if f["severity"] == severity]
    if provider:
        findings = [f for f in findings if f["cloud_provider"] == provider]
    return {"findings": findings, "total": len(findings)}


@app.get("/api/cloud/compliance")
def get_cloud_compliance(framework: str = Query(default="cis_aws")):
    """Get cloud compliance score."""
    return {
        "framework": framework,
        "score": random.uniform(70, 98),
        "total_controls": random.randint(100, 200),
        "passed_controls": random.randint(80, 190),
        "failed_controls": random.randint(5, 30),
        "open_findings": random.randint(10, 50),
        "last_assessment": (datetime.utcnow() - timedelta(days=random.randint(0, 30))).isoformat(),
    }


@app.get("/api/cloud/accounts")
def get_cloud_accounts():
    """Get cloud accounts."""
    providers = ["aws", "azure", "gcp"]
    environments = ["production", "staging", "development"]
    
    accounts = []
    for i in range(5):
        accounts.append({
            "account_id": f"acc-{random.randint(1000, 9999)}",
            "name": f"{random.choice(providers).upper()} {random.choice(environments).title()} {i+1}",
            "provider": random.choice(providers),
            "environment": random.choice(environments),
            "resource_count": random.randint(50, 500),
            "findings_count": random.randint(5, 50),
        })
    
    return {"accounts": accounts, "total": len(accounts)}


# ML Ops Endpoints

@app.get("/api/ml/models")
def get_ml_models(limit: int = Query(default=20, ge=1, le=100)):
    """Get ML models."""
    models = generate_ml_models(limit)
    return {"models": models, "total": len(models)}


@app.get("/api/ml/experiments")
def get_ml_experiments(limit: int = Query(default=30, ge=1, le=100)):
    """Get ML experiments."""
    experiments = generate_ml_experiments(limit)
    return {"experiments": experiments, "total": len(experiments)}


@app.get("/api/ml/drift/{model_id}")
def get_model_drift(model_id: str):
    """Get model drift analysis."""
    models = generate_ml_models(100)
    model = next((m for m in models if m["model_id"] == model_id), None)
    if not model:
        raise HTTPException(status_code=404, detail="Model not found")
    
    return {
        "model_id": model_id,
        "drift_detected": model["drift_score"] > 0.2,
        "drift_score": model["drift_score"],
        "threshold": 0.2,
        "features": [
            {"name": f"feature_{i}", "drift_score": random.uniform(0, 0.5)}
            for i in range(5)
        ],
        "recommendation": "retrain" if model["drift_score"] > 0.2 else "monitor",
    }


# System Endpoints

@app.get("/api/system/health")
def get_system_health():
    """Get system health."""
    return generate_system_health()


@app.get("/api/system/agents")
def get_agents():
    """Get all registered agents."""
    categories = {
        "core": ["base", "developer", "qa", "sysadmin", "lead"],
        "business": ["sales", "finance", "hr", "marketing", "product"],
        "operations": ["devops", "support", "integration", "communications"],
        "data": ["research", "data_analyst", "data_governance"],
        "governance": ["legal", "compliance", "privacy", "risk", "ethics"],
        "security": ["security", "soc", "vulnman", "redteam", "malware", "cloud_security"],
        "specialized": ["ml_ops", "supply_chain", "audit", "vendor_risk", "chaos_monkey"],
    }
    
    agents = []
    for category, agent_ids in categories.items():
        for agent_id in agent_ids:
            agents.append({
                "agent_id": f"{agent_id}-{random.randint(1, 3)}",
                "agent_type": agent_id,
                "category": category,
                "status": "healthy" if random.random() > 0.1 else "degraded",
                "capabilities": random.randint(3, 6),
            })
    
    return {"agents": agents, "total": len(agents)}


# ============================================================================
# Main Entry Point
# ============================================================================

if __name__ == "__main__":
    uvicorn.run(
        "api_server:app",
        host="0.0.0.0",
        port=8080,
        reload=True,
    )
