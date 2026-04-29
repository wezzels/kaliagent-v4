# Phase 14: Model Registry Summary

## Overview

Model Registry provides version control, metadata tracking, and deployment management for ML models.

## Features

### 1. Semantic Versioning
- Standard versioning: `major.minor.patch` (e.g., `1.0.0`, `1.1.0`, `2.0.0`)
- Version lineage tracking (parent_version)
- Automatic version sorting

### 2. Metadata Tracking
- **Model Info:** type, framework, framework version
- **Training:** data hash, samples, duration, metrics, hyperparameters
- **Evaluation:** precision, recall, f1, accuracy, etc.
- **Artifacts:** file path, size, SHA256 hash
- **Deployment:** status, environment, deployed_at

### 3. Model Storage
- Automatic model file copying to registry
- SHA256 hash verification
- Size tracking
- Organized by model name and version

### 4. Deployment Management
- Status tracking: development, staging, production, deprecated
- Environment tracking
- Deployment timestamps
- Deprecation support

### 5. A/B Testing
- Compare two model versions
- Metric-based comparison
- Statistical significance (p-value)
- Automated recommendations: promote, reject, needs_more_data

### 6. Version Comparison
- Side-by-side metric comparison
- Improvement percentage calculation
- Multi-metric comparison

---

## Usage

### Initialize Registry

```python
from phase14.model_registry import ModelRegistry

registry = ModelRegistry("./model_registry")
```

### Register Model

```python
metadata = registry.register(
    model_name="lstm_anomaly_detector",
    version="1.0.0",
    model_path="./models/lstm_v1.pt",
    model_type="lstm",
    framework="pytorch",
    training_metrics={"loss": 0.05, "accuracy": 0.95},
    evaluation_metrics={"precision": 0.98, "recall": 0.92, "f1": 0.95},
    hyperparameters={"hidden_size": 128, "layers": 2, "dropout": 0.2},
    description="LSTM anomaly detector v1.0",
    tags=["anomaly", "lstm", "production"]
)
```

### Get Model

```python
# Get latest version
metadata = registry.get("lstm_anomaly_detector")

# Get specific version
metadata = registry.get("lstm_anomaly_detector", "1.0.0")

# Access metadata
print(metadata.evaluation_metrics)  # {"precision": 0.98, ...}
print(metadata.model_path)          # "./model_registry/models/..."
print(metadata.model_hash)          # SHA256 hash
```

### List Models

```python
# List all models
models = registry.list_models()  # ["lstm_anomaly_detector", "autoencoder", ...]

# List versions
versions = registry.list_versions("lstm_anomaly_detector")  # ["1.0.0", "1.1.0"]
```

### Deploy Model

```python
# Deploy to staging
registry.deploy("lstm_anomaly_detector", "1.1.0", "staging")

# Deploy to production
registry.deploy("lstm_anomaly_detector", "1.0.0", "production")

# Deprecate old version
registry.deprecate("lstm_anomaly_detector", "0.9.0")
```

### A/B Testing

```python
result = registry.ab_test(
    control_model="lstm_anomaly_detector",
    control_version="1.0.0",
    candidate_model="lstm_anomaly_detector",
    candidate_version="1.1.0",
    metric_name="f1",
    control_score=0.95,
    candidate_score=0.96,
    p_value=0.03  # optional
)

print(result.recommendation)  # "promote", "reject", or "needs_more_data"
print(result.improvement)     # +1.05%
```

### Compare Versions

```python
comparison = registry.compare_versions(
    "lstm_anomaly_detector", "1.0.0", "1.1.0"
)

for metric, scores in comparison["metrics"].items():
    print(f"{metric}: {scores['version1']:.4f} → {scores['version2']:.4f} ({scores['improvement']:+.1f}%)")
```

**Output:**
```
f1: 0.9500 → 0.9600 (+1.1%)
precision: 0.9800 → 0.9900 (+1.0%)
recall: 0.9200 → 0.9400 (+2.2%)
```

### Export Registry

```python
registry.export_registry("./registry_export.json")
```

---

## Directory Structure

```
model_registry/
├── models/
│   ├── lstm_anomaly_detector/
│   │   ├── v1.0.0.pt
│   │   └── v1.1.0.pt
│   └── autoencoder/
│       └── v1.0.0.pt
├── metadata/
│   ├── lstm_anomaly_detector/
│   │   ├── v1.0.0.json
│   │   └── v1.1.0.json
│   └── autoencoder/
│       └── v1.0.0.json
└── registry_export.json
```

---

## Metadata Schema

```json
{
  "name": "lstm_anomaly_detector",
  "version": "1.0.0",
  "created_at": "2026-04-29T00:00:00",
  "created_by": "system",
  "model_type": "lstm",
  "framework": "pytorch",
  "framework_version": "2.12.0+cu128",
  "training_metrics": {
    "loss": 0.05,
    "accuracy": 0.95
  },
  "evaluation_metrics": {
    "precision": 0.98,
    "recall": 0.92,
    "f1": 0.95
  },
  "hyperparameters": {
    "hidden_size": 128,
    "layers": 2,
    "dropout": 0.2
  },
  "model_path": "./model_registry/models/lstm_anomaly_detector/v1.0.0.pt",
  "model_size_bytes": 524288,
  "model_hash": "sha256:abc123...",
  "status": "production",
  "deployment_environment": "production",
  "deployed_at": "2026-04-29T00:02:00",
  "description": "LSTM anomaly detector v1.0",
  "tags": ["anomaly", "lstm", "production"]
}
```

---

## A/B Test Recommendations

| Condition | Recommendation |
|-----------|---------------|
| Improvement > 5% AND significant | `promote` |
| Improvement > 5% AND not significant | `needs_more_data` |
| Improvement < -5% | `reject` |
| -5% ≤ Improvement ≤ 5% | `needs_more_data` |

---

## Integration with ML Pipeline

```python
# After training
registry = ModelRegistry()

# Register trained model
metadata = registry.register(
    model_name="lstm_anomaly_detector",
    version="1.0.0",
    model_path="./trained_model.pt",
    training_metrics=training_history,
    evaluation_metrics=test_metrics,
    hyperparameters=config
)

# Deploy to production
registry.deploy("lstm_anomaly_detector", "1.0.0", "production")

# Later, compare with new version
comparison = registry.compare_versions("lstm_anomaly_detector", "1.0.0", "1.1.0")
```

---

## Demo Results

```
📝 Registering models...
📂 Registered models: ['lstm_anomaly_detector']
   Versions: ['1.0.0', '1.1.0']

🚀 Deploying model...

📊 Running A/B test...
   Control: lstm_anomaly_detector:1.0.0 = 0.9500
   Candidate: lstm_anomaly_detector:1.1.0 = 0.9600
   Improvement: +1.05%
   Recommendation: needs_more_data

📈 Comparing versions...
   f1: 0.9500 → 0.9600 (+1.1%)
   precision: 0.9800 → 0.9900 (+1.0%)
   recall: 0.9200 → 0.9400 (+2.2%)
```

---

## Files

```
phase14/model_registry/
├── model_registry.py  (19 KB) - Main registry implementation
└── __init__.py        - Module init
```

---

## Status

**Alpha (0.1.0)** - Core functionality working

- [x] Model registration ✅
- [x] Metadata tracking ✅
- [x] Artifact storage ✅
- [x] Deployment management ✅
- [x] A/B testing ✅
- [x] Version comparison ✅
- [ ] Model serving (future)
- [ ] Automatic rollback (future)

---

*Created: April 29, 2026*  
*KaliAgent v5.0.0 - Phase 14 Model Registry*
