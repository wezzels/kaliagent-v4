#!/usr/bin/env python3
"""
🧠 KaliAgent v5.1.0 - Security Log Transformer (Fixed)

Transformer-based model for security log analysis:
- Anomaly detection in logs
- Log classification (attack type)
- Semantic similarity

Author: KaliAgent Team
Started: April 29, 2026
Status: Alpha (0.1.1)
"""

import logging
import math
import numpy as np
from typing import List, Dict, Tuple, Optional
from dataclasses import dataclass
import json

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger('LogTransformer')

try:
    import torch
    import torch.nn as nn
    import torch.nn.functional as F
    from torch.utils.data import Dataset, DataLoader
    TORCH_AVAILABLE = True
except ImportError:
    TORCH_AVAILABLE = False
    logger.warning("⚠️ PyTorch not available")


@dataclass
class TransformerConfig:
    """Transformer configuration"""
    vocab_size: int = 10000
    d_model: int = 256
    nhead: int = 8
    num_layers: int = 4
    dim_feedforward: int = 512
    dropout: float = 0.1
    max_seq_len: int = 128
    num_classes: int = 10
    learning_rate: float = 1e-4


class SecurityLogTransformer(nn.Module):
    """
    Simplified Transformer for security log analysis
    """
    
    VERSION = "0.1.1"
    
    def __init__(self, config: TransformerConfig):
        super().__init__()
        self.config = config
        self.d_model = config.d_model
        
        # Token embedding
        self.embedding = nn.Embedding(config.vocab_size, config.d_model, padding_idx=0)
        
        # Positional encoding (simplified)
        self.pos_encoding = self._create_positional_encoding(config.max_seq_len, config.d_model)
        
        # Transformer encoder
        encoder_layer = nn.TransformerEncoderLayer(
            d_model=config.d_model,
            nhead=config.nhead,
            dim_feedforward=config.dim_feedforward,
            dropout=config.dropout,
            activation='relu',
            batch_first=True
        )
        self.transformer_encoder = nn.TransformerEncoder(encoder_layer, num_layers=config.num_layers)
        
        # Classification head
        self.classifier = nn.Sequential(
            nn.Linear(config.d_model, config.d_model // 2),
            nn.ReLU(),
            nn.Dropout(config.dropout),
            nn.Linear(config.d_model // 2, config.num_classes)
        )
        
        self._init_weights()
        
        logger.info(f"🧠 Security Log Transformer v{self.VERSION}")
        logger.info(f"   Parameters: {config.d_model}d, {config.nhead} heads, {config.num_layers} layers")
    
    def _create_positional_encoding(self, max_len: int, d_model: int) -> torch.Tensor:
        """Create positional encoding matrix"""
        pe = torch.zeros(max_len, d_model)
        position = torch.arange(0, max_len, dtype=torch.float).unsqueeze(1)
        div_term = torch.exp(torch.arange(0, d_model, 2).float() * (-math.log(10000.0) / d_model))
        pe[:, 0::2] = torch.sin(position * div_term)
        if d_model % 2 == 0:
            pe[:, 1::2] = torch.cos(position * div_term)
        else:
            pe[:, 1::2] = torch.cos(position * div_term[:-1])
        return pe.unsqueeze(0)  # [1, max_len, d_model]
    
    def _init_weights(self):
        """Initialize weights"""
        for p in self.parameters():
            if p.dim() > 1:
                nn.init.xavier_uniform_(p)
    
    def forward(self, src: torch.Tensor) -> torch.Tensor:
        """
        Forward pass
        
        Args:
            src: Input tokens [batch_size, seq_len]
            
        Returns:
            logits: Classification logits [batch_size, num_classes]
        """
        batch_size, seq_len = src.shape
        
        # Embedding
        embedded = self.embedding(src) * math.sqrt(self.d_model)  # [batch, seq, d_model]
        
        # Add positional encoding (slice to actual sequence length)
        pe = self.pos_encoding[:, :seq_len, :].to(embedded.device)
        encoded = embedded + pe
        
        # Create attention mask for padding (2D: [seq, seq])
        # True means mask this position (padding)
        src_key_padding_mask = (src == 0)  # [batch, seq]
        
        # Transformer encoder
        transformer_out = self.transformer_encoder(encoded, src_key_padding_mask=src_key_padding_mask)  # [batch, seq, d_model]
        
        # Global average pooling (ignore padding)
        mask_2d = (src != 0).float().unsqueeze(-1)  # [batch, seq, 1]
        pooled = (transformer_out * mask_2d).sum(dim=1) / mask_2d.sum(dim=1).clamp(min=1)
        
        # Classification
        logits = self.classifier(pooled)  # [batch, num_classes]
        
        return logits
    
    def predict(self, src: torch.Tensor) -> Tuple:
        """Make prediction"""
        self.eval()
        with torch.no_grad():
            logits = self.forward(src)
            probs = F.softmax(logits, dim=-1)
            confidence, predicted = torch.max(probs, dim=-1)
            return predicted, confidence


class LogDataset(Dataset):
    """Dataset for security logs"""
    
    def __init__(self, logs: List[str], labels: List[int], 
                 word2idx: Dict[str, int], max_len: int = 128):
        self.logs = logs
        self.labels = labels
        self.word2idx = word2idx
        self.max_len = max_len
    
    def __len__(self) -> int:
        return len(self.logs)
    
    def __getitem__(self, idx) -> Tuple:
        log = self.logs[idx]
        tokens = self._encode(log)
        return torch.tensor(tokens, dtype=torch.long), torch.tensor(self.labels[idx], dtype=torch.long)
    
    def _encode(self, text: str) -> List[int]:
        """Encode text to tokens"""
        words = text.lower().split()
        tokens = [1]  # Start token
        
        for word in words[:self.max_len - 2]:
            tokens.append(self.word2idx.get(word, 2))  # 2 = UNK
        
        tokens.append(0)  # Padding
        tokens += [0] * (self.max_len - len(tokens))
        
        return tokens[:self.max_len]


class LogTransformerTrainer:
    """Trainer for log transformer"""
    
    def __init__(self, model: SecurityLogTransformer, learning_rate: float = 1e-4):
        self.model = model
        self.optimizer = torch.optim.Adam(model.parameters(), lr=learning_rate, weight_decay=1e-5)
        self.criterion = nn.CrossEntropyLoss()
        self.scheduler = torch.optim.lr_scheduler.StepLR(self.optimizer, step_size=5, gamma=0.5)
    
    def train_epoch(self, dataloader: DataLoader, device: torch.device) -> Dict:
        """Train for one epoch"""
        self.model.train()
        total_loss = 0
        correct = 0
        total = 0
        
        for src, labels in dataloader:
            src = src.to(device)
            labels = labels.to(device)
            
            self.optimizer.zero_grad()
            logits = self.model(src)
            loss = self.criterion(logits, labels)
            loss.backward()
            torch.nn.utils.clip_grad_norm_(self.model.parameters(), max_norm=1.0)
            self.optimizer.step()
            
            total_loss += loss.item()
            _, predicted = torch.max(logits, dim=-1)
            correct += (predicted == labels).sum().item()
            total += labels.size(0)
        
        self.scheduler.step()
        
        return {
            'loss': total_loss / len(dataloader),
            'accuracy': correct / total
        }
    
    def evaluate(self, dataloader: DataLoader, device: torch.device) -> Dict:
        """Evaluate model"""
        self.model.eval()
        total_loss = 0
        correct = 0
        total = 0
        
        with torch.no_grad():
            for src, labels in dataloader:
                src = src.to(device)
                labels = labels.to(device)
                
                logits = self.model(src)
                loss = self.criterion(logits, labels)
                
                total_loss += loss.item()
                _, predicted = torch.max(logits, dim=-1)
                correct += (predicted == labels).sum().item()
                total += labels.size(0)
        
        return {
            'loss': total_loss / len(dataloader),
            'accuracy': correct / total
        }


def build_vocab(logs: List[str], max_vocab: int = 5000) -> Dict[str, int]:
    """Build vocabulary from logs"""
    word2idx = {'<PAD>': 0, '<CLS>': 1, '<UNK>': 2}
    
    word_counts = {}
    for log in logs:
        for word in log.lower().split():
            word_counts[word] = word_counts.get(word, 0) + 1
    
    # Sort by frequency and take top words
    sorted_words = sorted(word_counts.items(), key=lambda x: -x[1])
    
    for word, _ in sorted_words[:max_vocab - 3]:
        if word not in word2idx:
            word2idx[word] = len(word2idx)
    
    return word2idx


def generate_sample_logs(num_samples: int = 1000, num_classes: int = 5) -> Tuple:
    """Generate synthetic security logs"""
    
    templates = [
        "User {user} logged in successfully from {ip}",
        "File {file} accessed by {user}",
        "Service {service} started successfully",
        "Failed login attempt for user {user} from {ip} attempt {count}",
        "Suspicious file {file} downloaded from {url}",
        "Port scan detected from {ip} targeting ports {ports}",
        "SQL injection attempt detected in query {query}",
        "Privilege escalation attempt by {user} on {server}"
    ]
    
    class_names = ['normal_login', 'normal_access', 'normal_service', 
                   'brute_force', 'malware', 'network_scan', 'injection', 'privilege_escalation']
    
    logs = []
    labels = []
    
    for i in range(num_samples):
        template = templates[i % len(templates)]
        label = i % min(num_classes, len(templates))
        
        log = template.format(
            user=f"user{i % 100}",
            ip=f"192.168.{i % 256}.{i % 256}",
            file=f"file_{i}.txt",
            service=f"service_{i % 10}",
            count=i % 10 + 1,
            url=f"http://example{i}.com",
            ports=",".join(str(p) for p in range(20 + i % 10, 30 + i % 10)),
            query=f"SELECT * FROM users WHERE id={i}",
            server=f"server_{i % 5}"
        )
        
        logs.append(log)
        labels.append(label)
    
    return logs, labels, class_names[:num_classes]


def main():
    """Demo log transformer"""
    print("""
╔═══════════════════════════════════════════════════════════════╗
║     🧠 KALIAGENT v5.1.0 - SECURITY LOG TRANSFORMER           ║
║                    Phase 14: Alpha 0.1.1                      ║
╚═══════════════════════════════════════════════════════════════╝

    """)
    
    if not TORCH_AVAILABLE:
        print("⚠️ PyTorch not available")
        return
    
    # Generate sample logs
    print("📊 Generating sample logs...")
    logs, labels, class_names = generate_sample_logs(num_samples=500, num_classes=5)
    print(f"   Generated {len(logs)} logs in {len(class_names)} classes")
    
    # Build vocabulary
    print("\n📝 Building vocabulary...")
    word2idx = build_vocab(logs, max_vocab=2000)
    print(f"   Vocabulary size: {len(word2idx)}")
    
    # Split data
    split = int(0.8 * len(logs))
    train_logs, test_logs = logs[:split], logs[split:]
    train_labels, test_labels = labels[:split], labels[split:]
    
    # Create datasets
    train_dataset = LogDataset(train_logs, train_labels, word2idx, max_len=128)
    test_dataset = LogDataset(test_logs, test_labels, word2idx, max_len=128)
    
    train_loader = DataLoader(train_dataset, batch_size=32, shuffle=True, drop_last=True)
    test_loader = DataLoader(test_dataset, batch_size=32, drop_last=True)
    
    # Create model
    print("\n🧠 Creating transformer model...")
    config = TransformerConfig(
        vocab_size=len(word2idx),
        d_model=256,
        nhead=8,
        num_layers=4,
        dim_feedforward=512,
        dropout=0.1,
        max_seq_len=128,
        num_classes=len(class_names),
        learning_rate=1e-4
    )
    
    model = SecurityLogTransformer(config)
    device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
    model = model.to(device)
    print(f"   Device: {device}")
    print(f"   Parameters: {sum(p.numel() for p in model.parameters()):,}")
    
    # Train
    print("\n📚 Training transformer...")
    trainer = LogTransformerTrainer(model, learning_rate=config.learning_rate)
    
    best_acc = 0
    for epoch in range(15):
        train_metrics = trainer.train_epoch(train_loader, device)
        test_metrics = trainer.evaluate(test_loader, device)
        
        if test_metrics['accuracy'] > best_acc:
            best_acc = test_metrics['accuracy']
        
        print(f"   Epoch {epoch+1:2d}/15 - "
              f"Train Loss: {train_metrics['loss']:.4f}, Acc: {train_metrics['accuracy']:.4f} | "
              f"Test Loss: {test_metrics['loss']:.4f}, Acc: {test_metrics['accuracy']:.4f}")
    
    # Test predictions
    print("\n🔍 Testing predictions...")
    model.eval()
    
    sample_idx = 0
    sample_log = test_logs[sample_idx]
    sample_label = test_labels[sample_idx]
    
    tokens = test_dataset._encode(sample_log)
    src = torch.tensor([tokens], dtype=torch.long).to(device)
    
    predicted, confidence = model.predict(src)
    
    print(f"   Log: {sample_log[:100]}...")
    print(f"   True Class: {class_names[sample_label]}")
    print(f"   Predicted: {class_names[predicted[0]]}")
    print(f"   Confidence: {confidence[0]:.4f}")
    
    print("\n" + "="*70)
    print(f"✅ Log Transformer demo complete!")
    print(f"   Best Test Accuracy: {best_acc:.4f}")
    print("="*70)


if __name__ == "__main__":
    main()
