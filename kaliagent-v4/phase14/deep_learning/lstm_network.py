#!/usr/bin/env python3
"""
🧠 KaliAgent v5.0.0 - Phase 14: Advanced ML/AI Models
LSTM Network for Security Anomaly Detection

LSTM (Long Short-Term Memory) networks for time-series anomaly detection:
- Network traffic sequence analysis
- User behavior pattern detection
- System call sequence monitoring
- Multi-feature temporal anomaly detection

Author: KaliAgent Team
Started: April 28, 2026
Status: Alpha (0.1.0)

Hardware: Optimized for RTX 5060 Ti 16GB (darth/10.0.0.117)
"""

import logging
import numpy as np
from typing import List, Dict, Tuple, Optional
from datetime import datetime
from dataclasses import dataclass, field
import uuid

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('LSTMNetwork')

# Try to import PyTorch
try:
    import torch
    import torch.nn as nn
    import torch.optim as optim
    from torch.utils.data import Dataset, DataLoader
    TORCH_AVAILABLE = True
    logger.info("✅ PyTorch available")
except ImportError:
    TORCH_AVAILABLE = False
    logger.warning("⚠️  PyTorch not available - using NumPy fallback")


@dataclass
class LSTMConfig:
    """LSTM network configuration"""
    input_size: int = 50
    hidden_size: int = 128
    num_layers: int = 2
    dropout: float = 0.2
    bidirectional: bool = False
    learning_rate: float = 0.001
    batch_size: int = 32
    epochs: int = 50
    sequence_length: int = 100


@dataclass
class AnomalyResult:
    """Anomaly detection result"""
    id: str
    timestamp: datetime
    anomaly_score: float
    is_anomaly: bool
    confidence: float
    sequence_length: int
    features: Dict[str, float] = field(default_factory=dict)
    explanation: str = ""
    
    def to_dict(self) -> Dict:
        return {
            'id': self.id,
            'timestamp': self.timestamp.isoformat(),
            'anomaly_score': self.anomaly_score,
            'is_anomaly': self.is_anomaly,
            'confidence': self.confidence,
            'sequence_length': self.sequence_length,
            'features': self.features,
            'explanation': self.explanation
        }


class LSTMSecurityDataset(Dataset):
    """PyTorch Dataset for security time-series data"""
    
    def __init__(self, sequences: np.ndarray, labels: np.ndarray = None):
        self.sequences = torch.FloatTensor(sequences) if TORCH_AVAILABLE else sequences
        self.labels = torch.FloatTensor(labels) if labels is not None and TORCH_AVAILABLE else labels
        
    def __len__(self) -> int:
        return len(self.sequences)
    
    def __getitem__(self, idx) -> Tuple:
        if self.labels is not None:
            return self.sequences[idx], self.labels[idx]
        return self.sequences[idx]


class LSTMSecurityDetector:
    """
    LSTM-based Security Anomaly Detector
    
    Architecture:
    - Input: Sequence of security metrics
    - LSTM Layers: 2-3 layers with 64-128 hidden units
    - Dropout: 0.2-0.3 for regularization
    - Output: Anomaly score (0-1)
    """
    
    VERSION = "0.1.0"
    
    def __init__(self, config: LSTMConfig = None):
        self.config = config or LSTMConfig()
        self.model = None
        self.device = None
        self.is_trained = False
        self.training_history = []
        self.feature_means = None
        self.feature_stds = None
        self.anomaly_threshold = 0.5
        
        if TORCH_AVAILABLE:
            self.device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
            logger.info(f"🔧 Using device: {self.device}")
            if torch.cuda.is_available():
                logger.info(f"   GPU: {torch.cuda.get_device_name(0)}")
                logger.info(f"   VRAM: {torch.cuda.get_device_properties(0).total_memory / 1024**3:.2f} GB")
            self._build_model()
        else:
            logger.warning("⚠️  Running in NumPy fallback mode")
        
        logger.info(f"🧠 LSTM Security Detector v{self.VERSION}")
        logger.info(f"   Input size: {self.config.input_size}")
        logger.info(f"   Hidden size: {self.config.hidden_size}")
        logger.info(f"   Num layers: {self.config.num_layers}")
    
    def _build_model(self) -> None:
        """Build LSTM model architecture"""
        if not TORCH_AVAILABLE:
            return
        
        class LSTMModel(nn.Module):
            def __init__(self, input_size, hidden_size, num_layers, dropout, bidirectional):
                super(LSTMModel, self).__init__()
                self.hidden_size = hidden_size
                self.num_layers = num_layers
                self.bidirectional = 2 if bidirectional else 1
                
                self.lstm = nn.LSTM(
                    input_size=input_size,
                    hidden_size=hidden_size,
                    num_layers=num_layers,
                    batch_first=True,
                    dropout=dropout if num_layers > 1 else 0,
                    bidirectional=bidirectional
                )
                
                self.attention = nn.Sequential(
                    nn.Linear(hidden_size * self.bidirectional, hidden_size),
                    nn.Tanh(),
                    nn.Linear(hidden_size, 1),
                    nn.Softmax(dim=1)
                )
                
                self.fc1 = nn.Linear(hidden_size * self.bidirectional, 64)
                self.relu = nn.ReLU()
                self.dropout = nn.Dropout(dropout)
                self.fc2 = nn.Linear(64, 1)
                self.sigmoid = nn.Sigmoid()
                
            def forward(self, x):
                lstm_out, _ = self.lstm(x)
                attn_weights = self.attention(lstm_out)
                context_vector = torch.sum(attn_weights * lstm_out, dim=1)
                out = self.fc1(context_vector)
                out = self.relu(out)
                out = self.dropout(out)
                out = self.fc2(out)
                out = self.sigmoid(out)
                return out
        
        self.model = LSTMModel(
            input_size=self.config.input_size,
            hidden_size=self.config.hidden_size,
            num_layers=self.config.num_layers,
            dropout=self.config.dropout,
            bidirectional=self.config.bidirectional
        )
        
        self.model = self.model.to(self.device)
        self.criterion = nn.BCELoss()
        self.optimizer = optim.Adam(self.model.parameters(), lr=self.config.learning_rate)
        
        logger.info("✅ Model built successfully")
        logger.info(f"   Total parameters: {sum(p.numel() for p in self.model.parameters()):,}")
    
    def _normalize(self, X: np.ndarray, fit: bool = False) -> np.ndarray:
        if fit:
            self.feature_means = np.mean(X, axis=(0, 1))
            self.feature_stds = np.std(X, axis=(0, 1)) + 1e-8
        return (X - self.feature_means) / self.feature_stds
    
    def fit(self, X_train: np.ndarray, y_train: np.ndarray = None,
            X_val: np.ndarray = None, y_val: np.ndarray = None,
            epochs: int = None, batch_size: int = None) -> Dict:
        if not TORCH_AVAILABLE:
            return {'error': 'PyTorch not available'}
        
        epochs = epochs or self.config.epochs
        batch_size = batch_size or self.config.batch_size
        
        logger.info(f"📚 Training LSTM model...")
        logger.info(f"   Training samples: {len(X_train)}")
        logger.info(f"   Epochs: {epochs}")
        
        X_train_norm = self._normalize(X_train, fit=True)
        
        if y_train is None:
            y_train = np.zeros(len(X_train))
        
        train_dataset = LSTMSecurityDataset(X_train_norm, y_train)
        train_loader = DataLoader(train_dataset, batch_size=batch_size, shuffle=True)
        
        history = {'loss': [], 'accuracy': [], 'val_loss': [], 'val_accuracy': []}
        self.model.train()
        
        for epoch in range(epochs):
            epoch_loss = 0.0
            epoch_correct = 0
            epoch_total = 0
            
            for batch_idx, (inputs, labels) in enumerate(train_loader):
                inputs = inputs.to(self.device)
                labels = labels.to(self.device)
                
                self.optimizer.zero_grad()
                outputs = self.model(inputs).squeeze()
                loss = self.criterion(outputs, labels)
                loss.backward()
                torch.nn.utils.clip_grad_norm_(self.model.parameters(), max_norm=1.0)
                self.optimizer.step()
                
                epoch_loss += loss.item()
                predictions = (outputs > 0.5).float()
                epoch_correct += (predictions == labels).sum().item()
                epoch_total += labels.size(0)
            
            avg_loss = epoch_loss / len(train_loader)
            accuracy = epoch_correct / epoch_total
            history['loss'].append(avg_loss)
            history['accuracy'].append(accuracy)
            
            if (epoch + 1) % 10 == 0 or epoch == 0:
                logger.info(f"   Epoch {epoch+1}/{epochs} - Loss: {avg_loss:.4f} | Acc: {accuracy:.4f}")
        
        self.is_trained = True
        self.training_history = history
        self._calculate_threshold(X_train_norm)
        
        logger.info(f"✅ Training complete! Final loss: {history['loss'][-1]:.4f}")
        return history
    
    def _calculate_threshold(self, X_normalized: np.ndarray) -> None:
        scores = self._predict_scores(X_normalized)
        self.anomaly_threshold = np.percentile(scores, 95)
        logger.info(f"   Anomaly threshold: {self.anomaly_threshold:.4f}")
    
    def _predict_scores(self, X: np.ndarray) -> np.ndarray:
        if not TORCH_AVAILABLE or not self.is_trained:
            return np.zeros(len(X))
        
        X_norm = self._normalize(X, fit=False)
        dataset = LSTMSecurityDataset(X_norm)
        loader = DataLoader(dataset, batch_size=self.config.batch_size)
        
        self.model.eval()
        scores = []
        
        with torch.no_grad():
            for inputs in loader:
                if isinstance(inputs, tuple):
                    inputs = inputs[0]
                inputs = inputs.to(self.device)
                outputs = self.model(inputs).squeeze().cpu().numpy()
                scores.extend(outputs if outputs.ndim > 0 else [outputs])
        
        return np.array(scores)
    
    def predict(self, X: np.ndarray, threshold: float = None) -> np.ndarray:
        scores = self._predict_scores(X)
        threshold = threshold or self.anomaly_threshold
        return (scores > threshold).astype(int)
    
    def detect(self, sequence: np.ndarray, feature_names: List[str] = None) -> AnomalyResult:
        if sequence.ndim == 1:
            sequence = sequence.reshape(1, -1)
        if sequence.ndim == 2 and sequence.shape[0] == 1:
            sequence = sequence.reshape(1, sequence.shape[1], 1)
        
        score = self._predict_scores(sequence)[0]
        is_anomaly = score > self.anomaly_threshold
        confidence = score if is_anomaly else 1 - score
        
        explanation = f"{'ANOMALY' if is_anomaly else 'NORMAL'} (score={score:.3f})"
        
        result = AnomalyResult(
            id=str(uuid.uuid4())[:8],
            timestamp=datetime.now(),
            anomaly_score=float(score),
            is_anomaly=bool(is_anomaly),
            confidence=float(confidence),
            sequence_length=len(sequence),
            explanation=explanation
        )
        
        if is_anomaly:
            logger.warning(f"⚠️  Anomaly detected: {result.id} (score: {score:.4f})")
        else:
            logger.info(f"✅ Normal: {result.id} (score: {score:.4f})")
        
        return result
    
    def save(self, path: str) -> None:
        if not TORCH_AVAILABLE:
            return
        checkpoint = {
            'model_state_dict': self.model.state_dict(),
            'config': self.config,
            'feature_means': self.feature_means,
            'feature_stds': self.feature_stds,
            'anomaly_threshold': self.anomaly_threshold,
            'is_trained': self.is_trained
        }
        torch.save(checkpoint, path)
        logger.info(f"💾 Model saved to {path}")
    
    def load(self, path: str) -> None:
        if not TORCH_AVAILABLE:
            return
        checkpoint = torch.load(path, map_location=self.device)
        self.model.load_state_dict(checkpoint['model_state_dict'])
        self.config = checkpoint['config']
        self.feature_means = checkpoint['feature_means']
        self.feature_stds = checkpoint['feature_stds']
        self.anomaly_threshold = checkpoint['anomaly_threshold']
        self.is_trained = checkpoint['is_trained']
        logger.info(f"📂 Model loaded from {path}")


def generate_sample_data(num_samples: int = 1000, seq_length: int = 100,
                        num_features: int = 5, anomaly_ratio: float = 0.1) -> Tuple:
    logger.info(f"📊 Generating synthetic data...")
    
    X_normal = np.zeros((num_samples, seq_length, num_features))
    for i in range(num_samples):
        base = np.sin(np.linspace(0, 4 * np.pi, seq_length))
        for f in range(num_features):
            X_normal[i, :, f] = base * (1 + 0.1 * f) + np.random.normal(0, 0.1, seq_length)
    
    num_anomalies = int(num_samples * anomaly_ratio)
    X_anomaly = np.zeros((num_anomalies, seq_length, num_features))
    
    for i in range(num_anomalies):
        anomaly_type = np.random.choice(['spike', 'drift', 'noise', 'pattern'])
        for f in range(num_features):
            if anomaly_type == 'spike':
                X_anomaly[i, :, f] = np.random.normal(0, 1, seq_length)
                spike_pos = np.random.randint(0, seq_length, 3)
                X_anomaly[i, spike_pos, f] += np.random.uniform(3, 5, 3)
            elif anomaly_type == 'drift':
                X_anomaly[i, :, f] = np.linspace(0, 3, seq_length) + np.random.normal(0, 0.2, seq_length)
            elif anomaly_type == 'noise':
                X_anomaly[i, :, f] = np.random.normal(0, 2, seq_length)
            elif anomaly_type == 'pattern':
                X_anomaly[i, :, f] = np.cos(np.linspace(0, 8 * np.pi, seq_length)) + np.random.normal(0, 0.3, seq_length)
    
    X = np.vstack([X_normal, X_anomaly])
    y = np.concatenate([np.zeros(num_samples), np.ones(num_anomalies)])
    
    indices = np.random.permutation(len(X))
    X = X[indices]
    y = y[indices]
    
    logger.info(f"✅ Generated {len(X)} samples ({int(sum(y))} anomalies)")
    return X, y


def main():
    """Main entry point - Demo LSTM anomaly detection"""
    print("""
╔═══════════════════════════════════════════════════════════════╗
║     🧠 KALIAGENT v5.0.0 - LSTM ANOMALY DETECTOR              ║
║                    Phase 14: Alpha 0.1.0                      ║
╚═══════════════════════════════════════════════════════════════╝

Hardware: RTX 5060 Ti 16GB (darth/10.0.0.117)

    """)
    
    if not TORCH_AVAILABLE:
        print("⚠️  PyTorch not available. Install with: pip install torch")
        return
    
    # Generate data
    X, y = generate_sample_data(num_samples=500, seq_length=50, 
                                num_features=5, anomaly_ratio=0.15)
    
    split = int(0.8 * len(X))
    X_train, X_test = X[:split], X[split:]
    y_train, y_test = y[:split], y[split:]
    
    print(f"\n📊 Data: {len(X_train)} train, {len(X_test)} test ({int(sum(y_test))} anomalies)\n")
    
    config = LSTMConfig(input_size=5, hidden_size=64, num_layers=2, epochs=30, batch_size=32)
    detector = LSTMSecurityDetector(config)
    
    # Train
    print("\n📚 Training LSTM model on GPU...")
    history = detector.fit(X_train, y_train, X_val=X_test, y_val=y_test)
    
    # Evaluate
    print("\n📊 Evaluating model...")
    predictions = detector.predict(X_test)
    
    accuracy = np.mean(predictions == y_test)
    precision = np.sum((predictions == 1) & (y_test == 1)) / max(np.sum(predictions == 1), 1)
    recall = np.sum((predictions == 1) & (y_test == 1)) / max(np.sum(y_test == 1), 1)
    f1 = 2 * precision * recall / max(precision + recall, 1e-8)
    
    print(f"\n✅ Test Results:")
    print(f"   Accuracy: {accuracy:.4f}")
    print(f"   Precision: {precision:.4f}")
    print(f"   Recall: {recall:.4f}")
    print(f"   F1 Score: {f1:.4f}")
    
    # Test single detection
    print("\n🔍 Testing single sequence detection...")
    test_seq = X_test[0]
    result = detector.detect(test_seq, feature_names=['bytes_sent', 'bytes_recv', 'packets_sent', 'packets_recv', 'connections'])
    print(f"   Result: {result.explanation}")
    print(f"   Confidence: {result.confidence:.2%}")
    
    print("\n" + "="*70)
    print("✅ LSTM Security Detector demo complete!")
    print("="*70)


if __name__ == "__main__":
    main()
