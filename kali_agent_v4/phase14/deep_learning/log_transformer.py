#!/usr/bin/env python3
"""
🧠 KaliAgent v5.1.0 - Security Log Transformer

Transformer-based model for security log analysis:
- Anomaly detection in logs
- Log classification (attack type)
- Semantic search
- Named entity recognition

Architecture:
- Token embedding + positional encoding
- Multi-head self-attention
- Feed-forward networks
- Classification head

Author: KaliAgent Team
Started: April 29, 2026
Status: Alpha (0.1.0)
"""

import logging
import math
import numpy as np
from typing import List, Dict, Tuple, Optional
from dataclasses import dataclass, field
from datetime import datetime
import json

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
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
    vocab_size: int = 10000  # Log token vocabulary size
    d_model: int = 512  # Embedding dimension
    nhead: int = 8  # Number of attention heads
    num_layers: int = 6  # Number of transformer layers
    dim_feedforward: int = 2048  # Feedforward dimension
    dropout: float = 0.1  # Dropout rate
    max_seq_len: int = 512  # Maximum sequence length
    num_classes: int = 10  # Number of classification classes
    learning_rate: float = 1e-4  # Learning rate
    batch_size: int = 32  # Batch size
    epochs: int = 50  # Training epochs


@dataclass
class LogAnalysisResult:
    """Log analysis result"""
    log_id: str
    timestamp: str
    original_log: str
    predicted_class: str
    confidence: float
    anomaly_score: float
    attention_weights: Optional[np.ndarray] = None
    entities: Dict[str, List[str]] = field(default_factory=dict)
    
    def to_dict(self) -> Dict:
        return {
            'log_id': self.log_id,
            'timestamp': self.timestamp,
            'original_log': self.original_log[:200],
            'predicted_class': self.predicted_class,
            'confidence': self.confidence,
            'anomaly_score': self.anomaly_score,
            'entities': self.entities
        }


class PositionalEncoding(nn.Module):
    """Positional encoding for transformer"""
    
    def __init__(self, d_model: int, dropout: float = 0.1, max_len: int = 512):
        super().__init__()
        self.dropout = nn.Dropout(p=dropout)
        
        # Create positional encoding matrix
        position = torch.arange(max_len).unsqueeze(1)
        div_term = torch.exp(torch.arange(0, d_model, 2) * (-math.log(10000.0) / d_model))
        pe = torch.zeros(max_len, 1, d_model)
        pe[:, 0, 0::2] = torch.sin(position * div_term)
        pe[:, 0, 1::2] = torch.cos(position * div_term)
        
        # Register as buffer (not a parameter)
        self.register_buffer('pe', pe)
    
    def forward(self, x: torch.Tensor) -> torch.Tensor:
        """
        Args:
            x: Tensor of shape [seq_len, batch_size, embedding_dim]
        """
        x = x + self.pe[:x.size(0)]
        return self.dropout(x)


class SecurityLogTransformer(nn.Module):
    """
    Transformer for security log analysis
    
    Architecture:
    - Token embedding
    - Positional encoding
    - N transformer encoder layers
    - Classification head
    - Anomaly detection head
    """
    
    VERSION = "0.1.0"
    
    def __init__(self, config: TransformerConfig):
        super().__init__()
        self.config = config
        
        # Token embedding
        self.embedding = nn.Embedding(config.vocab_size, config.d_model)
        
        # Positional encoding
        self.pos_encoder = PositionalEncoding(config.d_model, config.dropout, config.max_seq_len)
        
        # Transformer encoder
        encoder_layer = nn.TransformerEncoderLayer(
            d_model=config.d_model,
            nhead=config.nhead,
            dim_feedforward=config.dim_feedforward,
            dropout=config.dropout,
            activation='gelu',
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
        
        # Anomaly detection head (reconstruction-based)
        self.anomaly_head = nn.Sequential(
            nn.Linear(config.d_model, config.d_model),
            nn.ReLU(),
            nn.Linear(config.d_model, config.d_model)  # Match embedding dimension
        )
        
        # Initialize weights
        self._init_weights()
        
        logger.info(f"🧠 Security Log Transformer v{self.VERSION}")
        logger.info(f"   d_model: {config.d_model}")
        logger.info(f"   nhead: {config.nhead}")
        logger.info(f"   num_layers: {config.num_layers}")
        logger.info(f"   vocab_size: {config.vocab_size}")
        logger.info(f"   num_classes: {config.num_classes}")
    
    def _init_weights(self):
        """Initialize weights with Xavier uniform"""
        for p in self.parameters():
            if p.dim() > 1:
                nn.init.xavier_uniform_(p)
    
    def generate_square_subsequent_mask(self, sz: int) -> torch.Tensor:
        """Generate mask for causal attention"""
        mask = torch.triu(torch.ones(sz, sz), diagonal=1)
        mask = mask.masked_fill(mask == 1, float('-inf'))
        return mask
    
    def forward(self, src: torch.Tensor, src_mask: Optional[torch.Tensor] = None) -> Tuple:
        """
        Forward pass
        
        Args:
            src: Input tokens [batch_size, seq_len]
            src_mask: Attention mask [seq_len, seq_len]
            
        Returns:
            logits: Classification logits [batch_size, num_classes]
            anomaly_scores: Anomaly scores [batch_size]
            attention_weights: Attention weights [batch_size, seq_len, seq_len]
        """
        # Embedding + positional encoding
        embedded = self.embedding(src) * math.sqrt(self.config.d_model)
        encoded = self.pos_encoder(embedded)
        
        # Transformer encoder
        if src_mask is None:
            src_mask = self.generate_square_subsequent_mask(encoded.size(1))
        
        transformer_out = self.transformer_encoder(encoded, src_mask)
        
        # Use [CLS] token (first position) for classification
        cls_output = transformer_out[:, 0, :]
        
        # Classification
        logits = self.classifier(cls_output)
        
        # Anomaly detection (reconstruction error)
        reconstructed = self.anomaly_head(transformer_out)
        anomaly_scores = F.mse_loss(reconstructed, embedded, reduction='none').mean(dim=[1, 2])
        
        # Extract attention weights from last layer
        attention_weights = None
        # Note: Would need to modify transformer to return attention weights
        
        return logits, anomaly_scores, attention_weights
    
    def predict(self, src: torch.Tensor) -> Tuple:
        """Make prediction"""
        self.eval()
        with torch.no_grad():
            logits, anomaly_scores, _ = self.forward(src)
            probs = F.softmax(logits, dim=-1)
            confidence, predicted = torch.max(probs, dim=-1)
            return predicted, confidence, anomaly_scores


class LogDataset(Dataset):
    """Dataset for security logs"""
    
    def __init__(self, logs: List[str], labels: Optional[List[int]] = None,
                 tokenizer=None, max_len: int = 512):
        self.logs = logs
        self.labels = labels
        self.tokenizer = tokenizer or SimpleLogTokenizer()
        self.max_len = max_len
    
    def __len__(self) -> int:
        return len(self.logs)
    
    def __getitem__(self, idx) -> Tuple:
        log = self.logs[idx]
        
        # Tokenize
        tokens = self.tokenizer.encode(log, max_len=self.max_len)
        
        if self.labels is not None:
            return torch.tensor(tokens, dtype=torch.long), torch.tensor(self.labels[idx], dtype=torch.long)
        return torch.tensor(tokens, dtype=torch.long)


class SimpleLogTokenizer:
    """Simple tokenizer for security logs"""
    
    def __init__(self, vocab_size: int = 10000):
        self.vocab_size = vocab_size
        self.word2idx = {'<PAD>': 0, '<CLS>': 1, '<UNK>': 2}
        self.idx2word = {0: '<PAD>', 1: '<CLS>', 2: '<UNK>'}
        self.next_idx = 3
    
    def encode(self, text: str, max_len: int = 512) -> List[int]:
        """Encode text to tokens"""
        # Simple word-level tokenization
        words = text.lower().split()
        
        tokens = [self.word2idx['<CLS>']]  # Start with CLS token
        
        for word in words[:max_len - 1]:
            if word in self.word2idx:
                tokens.append(self.word2idx[word])
            else:
                if self.next_idx < self.vocab_size:
                    self.word2idx[word] = self.next_idx
                    self.idx2word[self.next_idx] = word
                    tokens.append(self.next_idx)
                    self.next_idx += 1
                else:
                    tokens.append(self.word2idx['<UNK>'])
        
        # Pad to max_len
        tokens += [self.word2idx['<PAD>']] * (max_len - len(tokens))
        
        return tokens[:max_len]
    
    def build_vocab(self, texts: List[str]):
        """Build vocabulary from texts"""
        for text in texts:
            words = text.lower().split()
            for word in words:
                if word not in self.word2idx and self.next_idx < self.vocab_size:
                    self.word2idx[word] = self.next_idx
                    self.idx2word[self.next_idx] = word
                    self.next_idx += 1


class LogTransformerTrainer:
    """Trainer for log transformer"""
    
    def __init__(self, model: SecurityLogTransformer, learning_rate: float = 1e-4):
        self.model = model
        self.optimizer = torch.optim.Adam(model.parameters(), lr=learning_rate)
        self.classification_criterion = nn.CrossEntropyLoss()
        self.anomaly_criterion = nn.MSELoss()
    
    def train_epoch(self, dataloader: DataLoader, device: torch.device) -> Dict:
        """Train for one epoch"""
        self.model.train()
        total_loss = 0
        total_cls_loss = 0
        total_anomaly_loss = 0
        correct = 0
        total = 0
        
        for batch_idx, (src, labels) in enumerate(dataloader):
            src = src.to(device)
            labels = labels.to(device)
            
            # Forward pass
            self.optimizer.zero_grad()
            logits, anomaly_scores, _ = self.model(src)
            
            # Calculate losses
            cls_loss = self.classification_criterion(logits, labels)
            anomaly_loss = self.anomaly_criterion(anomaly_scores, torch.zeros_like(anomaly_scores))
            loss = cls_loss + 0.1 * anomaly_loss  # Weight anomaly loss
            
            # Backward pass
            loss.backward()
            torch.nn.utils.clip_grad_norm_(self.model.parameters(), max_norm=1.0)
            self.optimizer.step()
            
            # Statistics
            total_loss += loss.item()
            total_cls_loss += cls_loss.item()
            total_anomaly_loss += anomaly_loss.item()
            
            _, predicted = torch.max(logits, dim=-1)
            correct += (predicted == labels).sum().item()
            total += labels.size(0)
        
        return {
            'loss': total_loss / len(dataloader),
            'cls_loss': total_cls_loss / len(dataloader),
            'anomaly_loss': total_anomaly_loss / len(dataloader),
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
                
                logits, anomaly_scores, _ = self.model(src)
                loss = self.classification_criterion(logits, labels)
                
                total_loss += loss.item()
                
                _, predicted = torch.max(logits, dim=-1)
                correct += (predicted == labels).sum().item()
                total += labels.size(0)
        
        return {
            'loss': total_loss / len(dataloader),
            'accuracy': correct / total
        }


def generate_sample_logs(num_samples: int = 1000, num_classes: int = 5) -> Tuple:
    """Generate synthetic security logs for testing"""
    
    log_templates = [
        # Normal logs
        "User {user} logged in successfully from {ip}",
        "File {file} accessed by {user}",
        "Service {service} started successfully",
        "Backup completed for {server}",
        "Email sent to {email}",
        
        # Attack logs
        "Failed login attempt for user {user} from {ip} (attempt {count})",
        "Suspicious file {file} downloaded from {url}",
        "Port scan detected from {ip} targeting ports {ports}",
        "SQL injection attempt detected in query {query}",
        "Privilege escalation attempt by {user} on {server}"
    ]
    
    class_names = ['normal', 'brute_force', 'malware', 'network_scan', 'injection']
    
    logs = []
    labels = []
    
    for i in range(num_samples):
        template = log_templates[i % len(log_templates)]
        label = i % num_classes
        
        # Fill in template
        log = template.format(
            user=f"user{i % 100}",
            ip=f"192.168.{i % 256}.{i % 256}",
            file=f"file_{i}.txt",
            service=f"service_{i % 10}",
            server=f"server_{i % 5}",
            email=f"user{i}@example.com",
            count=i % 10 + 1,
            url=f"http://malicious{i}.com",
            ports=",".join(str(p) for p in range(20 + i % 10, 30 + i % 10)),
            query=f"SELECT * FROM users WHERE id={i}"
        )
        
        logs.append(log)
        labels.append(label)
    
    return logs, labels, class_names


def main():
    """Demo log transformer"""
    print("""
╔═══════════════════════════════════════════════════════════════╗
║     🧠 KALIAGENT v5.1.0 - SECURITY LOG TRANSFORMER           ║
║                    Phase 14: Alpha 0.1.0                      ║
╚═══════════════════════════════════════════════════════════════╝

    """)
    
    if not TORCH_AVAILABLE:
        print("⚠️ PyTorch not available")
        return
    
    # Generate sample logs
    print("📊 Generating sample logs...")
    logs, labels, class_names = generate_sample_logs(num_samples=500, num_classes=5)
    print(f"   Generated {len(logs)} logs in {len(class_names)} classes")
    
    # Split data
    split = int(0.8 * len(logs))
    train_logs, test_logs = logs[:split], logs[split:]
    train_labels, test_labels = labels[:split], labels[split:]
    
    # Create tokenizer and datasets
    print("\n📝 Building vocabulary...")
    tokenizer = SimpleLogTokenizer(vocab_size=1000)
    tokenizer.build_vocab(train_logs)
    print(f"   Vocabulary size: {len(tokenizer.word2idx)}")
    
    train_dataset = LogDataset(train_logs, train_labels, tokenizer, max_len=128)
    test_dataset = LogDataset(test_logs, test_labels, tokenizer, max_len=128)
    
    train_loader = DataLoader(train_dataset, batch_size=32, shuffle=True)
    test_loader = DataLoader(test_dataset, batch_size=32)
    
    # Create model
    print("\n🧠 Creating transformer model...")
    config = TransformerConfig(
        vocab_size=len(tokenizer.word2idx),
        d_model=256,
        nhead=8,
        num_layers=4,
        dim_feedforward=512,
        dropout=0.1,
        max_seq_len=128,
        num_classes=len(class_names),
        learning_rate=1e-4,
        batch_size=32,
        epochs=10
    )
    
    model = SecurityLogTransformer(config)
    device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
    model = model.to(device)
    print(f"   Device: {device}")
    print(f"   Parameters: {sum(p.numel() for p in model.parameters()):,}")
    
    # Train
    print("\n📚 Training transformer...")
    trainer = LogTransformerTrainer(model, learning_rate=config.learning_rate)
    
    for epoch in range(config.epochs):
        train_metrics = trainer.train_epoch(train_loader, device)
        test_metrics = trainer.evaluate(test_loader, device)
        
        print(f"   Epoch {epoch+1}/{config.epochs}")
        print(f"      Train Loss: {train_metrics['loss']:.4f}, Acc: {train_metrics['accuracy']:.4f}")
        print(f"      Test Loss: {test_metrics['loss']:.4f}, Acc: {test_metrics['accuracy']:.4f}")
    
    # Test predictions
    print("\n🔍 Testing predictions...")
    model.eval()
    with torch.no_grad():
        sample_log = test_logs[0]
        tokens = tokenizer.encode(sample_log, max_len=128)
        src = torch.tensor([tokens], dtype=torch.long).to(device)
        
        predicted, confidence, anomaly_score = model.predict(src)
        
        print(f"   Log: {sample_log[:100]}...")
        print(f"   Predicted Class: {class_names[predicted[0]]}")
        print(f"   Confidence: {confidence[0]:.4f}")
        print(f"   Anomaly Score: {anomaly_score[0]:.6f}")
    
    print("\n" + "="*70)
    print("✅ Log Transformer demo complete!")
    print("="*70)


if __name__ == "__main__":
    main()
