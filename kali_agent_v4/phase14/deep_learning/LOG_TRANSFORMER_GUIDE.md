# 🧠 Security Log Transformer - User Guide

**Version:** 0.1.1  
**Status:** Working ✅  
**Test Accuracy:** 76% (synthetic data)  
**Training Time:** ~2 minutes on GPU

---

## Overview

The Security Log Transformer is a transformer-based deep learning model for analyzing security logs. It can:

- **Classify log entries** by attack type
- **Detect anomalies** in log patterns
- **Learn from synthetic or real logs**

---

## Architecture

```
Input Logs → Token Embedding → Positional Encoding →
Transformer Encoder (4 layers, 8 heads) →
Global Average Pooling → Classification Head → Output
```

**Parameters:**
- Embedding dimension: 256
- Attention heads: 8
- Transformer layers: 4
- Feedforward dimension: 512
- Dropout: 0.1

---

## Quick Start

### 1. Run Demo

```bash
cd ~/stsgym-work/agentic_ai/kaliagent-v4
source venv/bin/activate
python3 kali_agent_v4/phase14/deep_learning/log_transformer.py
```

**Expected Output:**
```
🧠 Security Log Transformer v0.1.1
   Parameters: 256d, 8 heads, 4 layers

📊 Generating sample logs...
   Generated 500 logs in 5 classes

📝 Building vocabulary...
   Vocabulary size: 474

🧠 Creating transformer model...
   Device: cuda
   Parameters: 2,263,301

📚 Training transformer...
   Epoch  1/15 - Train Loss: 1.71, Acc: 0.21 | Test Loss: 1.58, Acc: 0.25
   ...
   Epoch 15/15 - Train Loss: 0.37, Acc: 0.89 | Test Loss: 0.68, Acc: 0.76

✅ Log Transformer demo complete!
   Best Test Accuracy: 0.7604
```

### 2. Use in Your Code

```python
from phase14.deep_learning.log_transformer import (
    SecurityLogTransformer,
    TransformerConfig,
    LogDataset,
    LogTransformerTrainer,
    build_vocab
)
from torch.utils.data import DataLoader
import torch

# Your logs
logs = [
    "User admin logged in from 192.168.1.100",
    "Failed login attempt for user root from 10.0.0.50",
    "Port scan detected from 203.0.113.50",
    # ... more logs
]

# Labels (0=normal, 1=brute_force, 2=network_scan, etc.)
labels = [0, 1, 2, ...]

# Build vocabulary
word2idx = build_vocab(logs, max_vocab=5000)

# Create dataset
dataset = LogDataset(logs, labels, word2idx, max_len=128)
loader = DataLoader(dataset, batch_size=32, shuffle=True)

# Create model
config = TransformerConfig(
    vocab_size=len(word2idx),
    d_model=256,
    nhead=8,
    num_layers=4,
    num_classes=5  # Number of log classes
)

model = SecurityLogTransformer(config)
device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
model = model.to(device)

# Train
trainer = LogTransformerTrainer(model, learning_rate=1e-4)

for epoch in range(15):
    metrics = trainer.train_epoch(loader, device)
    print(f"Epoch {epoch+1}: Loss={metrics['loss']:.4f}, Acc={metrics['accuracy']:.4f}")

# Predict
model.eval()
with torch.no_grad():
    sample_log = "Failed login attempt for user admin from 10.0.0.1"
    tokens = dataset._encode(sample_log)
    src = torch.tensor([tokens]).to(device)
    predicted, confidence = model.predict(src)
    print(f"Predicted class: {predicted[0]}, Confidence: {confidence[0]:.4f}")
```

---

## Log Classes

The demo uses 5 synthetic log classes:

| Class ID | Class Name | Example |
|----------|------------|---------|
| 0 | `normal_login` | "User logged in successfully" |
| 1 | `normal_access` | "File accessed by user" |
| 2 | `normal_service` | "Service started successfully" |
| 3 | `brute_force` | "Failed login attempt (multiple)" |
| 4 | `network_scan` | "Port scan detected" |

**For production**, you can define your own classes:
- Authentication events
- File access events
- Network events
- System events
- Security alerts
- Malware detections

---

## Training on Real Data

### 1. Prepare Your Data

```python
# Load your logs
with open('security_logs.txt') as f:
    logs = [line.strip() for line in f]

# Create labels (you need to label your logs)
# This could come from SIEM alerts, manual labeling, etc.
labels = []
for log in logs:
    if 'failed login' in log.lower():
        labels.append(1)  # brute_force
    elif 'port scan' in log.lower():
        labels.append(2)  # network_scan
    elif 'injection' in log.lower():
        labels.append(3)  # injection
    else:
        labels.append(0)  # normal
```

### 2. Train

```python
# Split data
split = int(0.8 * len(logs))
train_logs, test_logs = logs[:split], logs[split:]
train_labels, test_labels = labels[:split], labels[split:]

# Build vocabulary from training data
word2idx = build_vocab(train_logs, max_vocab=10000)

# Create datasets
train_dataset = LogDataset(train_logs, train_labels, word2idx, max_len=256)
test_dataset = LogDataset(test_logs, test_labels, word2idx, max_len=256)

train_loader = DataLoader(train_dataset, batch_size=32, shuffle=True, drop_last=True)
test_loader = DataLoader(test_dataset, batch_size=32, drop_last=True)

# Create and train model
config = TransformerConfig(
    vocab_size=len(word2idx),
    d_model=512,  # Larger for real data
    nhead=8,
    num_layers=6,  # Deeper for real data
    dim_feedforward=2048,
    dropout=0.1,
    max_seq_len=256,
    num_classes=len(set(labels)),
    learning_rate=5e-5
)

model = SecurityLogTransformer(config).to(device)
trainer = LogTransformerTrainer(model, learning_rate=config.learning_rate)

# Train for more epochs
best_acc = 0
for epoch in range(50):
    train_metrics = trainer.train_epoch(train_loader, device)
    test_metrics = trainer.evaluate(test_loader, device)
    
    if test_metrics['accuracy'] > best_acc:
        best_acc = test_metrics['accuracy']
        # Save best model
        torch.save(model.state_dict(), 'best_log_transformer.pth')
    
    if epoch % 5 == 0:
        print(f"Epoch {epoch}: Train Acc={train_metrics['accuracy']:.4f}, "
              f"Test Acc={test_metrics['accuracy']:.4f}")

print(f"Best test accuracy: {best_acc:.4f}")
```

### 3. Load Trained Model

```python
# Load model
config = TransformerConfig(...)  # Same config as training
model = SecurityLogTransformer(config)
model.load_state_dict(torch.load('best_log_transformer.pth'))
model.eval()

# Use for prediction
```

---

## Performance Tips

### 1. GPU Acceleration

```python
device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
model = model.to(device)
```

**Speedup:** 10-30x faster training on GPU

### 2. Batch Size

- Small datasets (< 10K logs): batch_size=16
- Medium datasets (10K-100K): batch_size=32
- Large datasets (> 100K): batch_size=64 or 128

### 3. Learning Rate

- Start with 1e-4
- If loss diverges, try 5e-5 or 1e-5
- Use learning rate scheduler (included)

### 4. Model Size

| Dataset Size | d_model | Layers | Heads |
|--------------|---------|--------|-------|
| Small (< 10K) | 256 | 4 | 8 |
| Medium (10K-100K) | 512 | 6 | 8 |
| Large (> 100K) | 768 | 8 | 12 |

---

## Integration with KaliAgent

### Phase 11 (Threat Hunting)

```python
from phase11.threat_hunter import ThreatHunter
from phase14.deep_learning.log_transformer import SecurityLogTransformer

# Use transformer to classify logs before hunting
logs = threat_hunter.collect_logs()
predictions = transformer.predict(logs)

# Focus hunting on anomalous logs
anomalous_indices = [i for i, p in enumerate(predictions) if p == ANOMALY_CLASS]
threat_hunter.investigate(anomalous_indices)
```

### Phase 12 (Incident Response)

```python
from phase12.incident_responder import IncidentResponder
from phase14.deep_learning.log_transformer import SecurityLogTransformer

# Classify incoming logs in real-time
for log in log_stream:
    prediction = transformer.predict(log)
    
    if prediction == BRUTE_FORCE_CLASS:
        responder.trigger_playbook('brute_force_response')
    elif prediction == MALWARE_CLASS:
        responder.trigger_playbook('malware_containment')
```

### Phase 13 (Threat Intelligence)

```python
from phase13.intelligence.threat_intel import ThreatIntel
from phase14.deep_learning.log_transformer import SecurityLogTransformer

# Extract attack patterns from classified logs
classified_logs = transformer.classify_batch(logs)
patterns = threat_intel.extract_patterns(classified_logs)

# Correlate with threat intelligence
threats = threat_intel.correlate(patterns)
```

---

## Troubleshooting

### CUDA Out of Memory

**Solution:** Reduce batch size or sequence length
```python
config = TransformerConfig(
    batch_size=16,  # Was 32
    max_seq_len=64  # Was 128
)
```

### Loss Not Decreasing

**Solutions:**
1. Check learning rate (try 1e-5)
2. Increase model size (more layers, larger d_model)
3. Check data quality (ensure labels are correct)
4. Train longer (50+ epochs)

### Overfitting

**Solutions:**
1. Increase dropout (0.2 or 0.3)
2. Add weight decay
3. Use early stopping
4. Get more training data
5. Data augmentation (paraphrase logs)

### Poor Accuracy

**Solutions:**
1. Check class balance (balance if needed)
2. Increase vocabulary size
3. Use pre-trained embeddings
4. Try larger model
5. Train longer

---

## Next Steps

### v5.1.0 Enhancements

- [ ] **Attention Visualization** - Show which words influenced prediction
- [ ] **Multi-label Classification** - Support multiple attack types per log
- [ ] **Semantic Search** - Find similar logs using embeddings
- [ ] **Pre-trained Model** - Train on large corpus of security logs
- [ ] **Anomaly Detection Head** - Separate head for anomaly scores
- [ ] **Explainability** - Generate natural language explanations

### Research Directions

- [ ] **BERT for Logs** - Pre-train on massive log corpus
- [ ] **Multi-modal** - Combine logs with network traffic
- [ ] **Continual Learning** - Adapt to new attack patterns
- [ ] **Federated Learning** - Train across organizations

---

## References

1. Vaswani et al. "Attention Is All You Need" (2017)
2. Devlin et al. "BERT: Pre-training of Deep Bidirectional Transformers" (2019)
3. Security Log Analysis with Deep Learning (various papers)

---

*Created: April 29, 2026*  
*KaliAgent v5.1.0 - Deep Learning Module*  
**Status:** Working ✅ | **Accuracy:** 76% (synthetic) | **GPU:** 10-30x speedup
