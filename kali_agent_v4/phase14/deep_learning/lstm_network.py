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
    input_size: int = 50  # Number of features
    hidden_size: int = 128  # LSTM hidden units
    num_layers: int = 2  # Number of LSTM layers
    dropout: float = 0.2  # Dropout rate
    bidirectional: bool = False  # Bidirectional LSTM
    learning_rate: float = 0.001  # Learning rate
    batch_size: int = 32  # Training batch size
    epochs: int = 50  # Number of training epochs
    sequence_length: int = 100  # Input sequence length


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
        """
        Initialize dataset
        
        Args:
            sequences: Array of shape (num_samples, seq_length, num_features)
            labels: Array of shape (num_samples,) - 1 for anomaly, 0 for normal
        """
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
    - Input: Sequence of security metrics (seq_length × num_features)
    - LSTM Layers: 2-3 layers with 64-128 hidden units
    - Dropout: 0.2-0.3 for regularization
    - Output: Anomaly score (0-1)
    
    Use Cases:
    - Network traffic anomaly detection
    - User behavior monitoring
    - System call sequence analysis
    - Multi-feature temporal patterns
    """
    
    VERSION = "0.1.0"
    
    def __init__(self, config: LSTMConfig = None):
        """
        Initialize LSTM Security Detector
        
        Args:
            config: LSTM configuration
        """
        self.config = config or LSTMConfig()
        self.model = None
        self.device = None
        self.is_trained = False
        self.training_history = []
        
        # Statistics for normalization
        self.feature_means = None
        self.feature_stds = None
        
        # Anomaly threshold (auto-calculated or manual)
        self.anomaly_threshold = 0.5
        
        if TORCH_AVAILABLE:
            # Set device (GPU if available)
            self.device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
            logger.info(f"🔧 Using device: {self.device}")
            
            # Initialize model
            self._build_model()
        else:
            logger.warning("⚠️  Running in NumPy fallback mode (limited functionality)")
        
        logger.info(f"🧠 LSTM Security Detector v{self.VERSION}")
        logger.info(f"   Input size: {self.config.input_size}")
        logger.info(f"   Hidden size: {self.config.hidden_size}")
        logger.info(f"   Num layers: {self.config.num_layers}")
        logger.info(f"   Sequence length: {self.config.sequence_length}")
    
    def _build_model(self) -> None:
        """Build LSTM model architecture"""
        if not TORCH_AVAILABLE:
            return
        
        class LSTMModel(nn.Module):
            """LSTM model for anomaly detection"""
            
            def __init__(self, input_size, hidden_size, num_layers, dropout, bidirectional):
                super(LSTMModel, self).__init__()
                
                self.hidden_size = hidden_size
                self.num_layers = num_layers
                self.bidirectional = 2 if bidirectional else 1
                
                # LSTM layers
                self.lstm = nn.LSTM(
                    input_size=input_size,
                    hidden_size=hidden_size,
                    num_layers=num_layers,
                    batch_first=True,
                    dropout=dropout if num_layers > 1 else 0,
                    bidirectional=bidirectional
                )
                
                # Attention layer (optional improvement)
                self.attention = nn.Sequential(
                    nn.Linear(hidden_size * self.bidirectional, hidden_size),
                    nn.Tanh(),
                    nn.Linear(hidden_size, 1),
                    nn.Softmax(dim=1)
                )
                
                # Output layers
                self.fc1 = nn.Linear(hidden_size * self.bidirectional, 64)
                self.relu = nn.ReLU()
                self.dropout = nn.Dropout(dropout)
                self.fc2 = nn.Linear(64, 1)
                self.sigmoid = nn.Sigmoid()
                
            def forward(self, x):
                # LSTM forward
                lstm_out, _ = self.lstm(x)
                
                # Attention mechanism
                attn_weights = self.attention(lstm_out)
                context_vector = torch.sum(attn_weights * lstm_out, dim=1)
                
                # Fully connected layers
                out = self.fc1(context_vector)
                out = self.relu(out)
                out = self.dropout(out)
                out = self.fc2(out)
                out = self.sigmoid(out)
                
                return out
        
        # Create model
        self.model = LSTMModel(
            input_size=self.config.input_size,
            hidden_size=self.config.hidden_size,
            num_layers=self.config.num_layers,
            dropout=self.config.dropout,
            bidirectional=self.config.bidirectional
        )
        
        # Move to device
        self.model = self.model.to(self.device)
        
        # Loss and optimizer
        self.criterion = nn.BCELoss()
        self.optimizer = optim.Adam(self.model.parameters(), lr=self.config.learning_rate)
        
        logger.info("✅ Model built successfully")
        logger.info(f"   Total parameters: {sum(p.numel() for p in self.model.parameters()):,}")
    
    def _normalize(self, X: np.ndarray, fit: bool = False) -> np.ndarray:
        """Normalize features using z-score"""
        if fit:
            self.feature_means = np.mean(X, axis=(0, 1))
            self.feature_stds = np.std(X, axis=(0, 1)) + 1e-8
        
        return (X - self.feature_means) / self.feature_stds
    
    def fit(self, X_train: np.ndarray, y_train: np.ndarray = None,
            X_val: np.ndarray = None, y_val: np.ndarray = None,
            epochs: int = None, batch_size: int = None) -> Dict:
        """
        Train LSTM model
        
        Args:
            X_train: Training sequences (num_samples, seq_length, num_features)
            y_train: Training labels (num_samples,) - optional for unsupervised
            X_val: Validation sequences (optional)
            y_val: Validation labels (optional)
            epochs: Override config epochs
            batch_size: Override config batch_size
            
        Returns:
            Training history
        """
        if not TORCH_AVAILABLE:
            logger.error("❌ PyTorch required for training")
            return {'error': 'PyTorch not available'}
        
        epochs = epochs or self.config.epochs
        batch_size = batch_size or self.config.batch_size
        
        logger.info(f"📚 Training LSTM model...")
        logger.info(f"   Training samples: {len(X_train)}")
        logger.info(f"   Epochs: {epochs}")
        logger.info(f"   Batch size: {batch_size}")
        
        # Normalize data
        X_train_norm = self._normalize(X_train, fit=True)
        
        # Create labels if not provided (unsupervised - all normal = 0)
        if y_train is None:
            logger.info("   No labels provided - training in unsupervised mode")
            y_train = np.zeros(len(X_train))
        
        # Create datasets
        train_dataset = LSTMSecurityDataset(X_train_norm, y_train)
        train_loader = DataLoader(train_dataset, batch_size=batch_size, shuffle=True)
        
        # Validation data
        if X_val is not None:
            X_val_norm = self._normalize(X_val, fit=False)
            if y_val is None:
                y_val = np.zeros(len(X_val))
            val_dataset = LSTMSecurityDataset(X_val_norm, y_val)
            val_loader = DataLoader(val_dataset, batch_size=batch_size)
        else:
            val_loader = None
        
        # Training loop
        history = {
            'loss': [],
            'accuracy': [],
            'val_loss': [],
            'val_accuracy': []
        }
        
        self.model.train()
        
        for epoch in range(epochs):
            epoch_loss = 0.0
            epoch_correct = 0
            epoch_total = 0
            
            for batch_idx, (inputs, labels) in enumerate(train_loader):
                # Move to device
                inputs = inputs.to(self.device)
                labels = labels.to(self.device)
                
                # Forward pass
                self.optimizer.zero_grad()
                outputs = self.model(inputs).squeeze()
                loss = self.criterion(outputs, labels)
                
                # Backward pass
                loss.backward()
                
                # Gradient clipping (prevent exploding gradients)
                torch.nn.utils.clip_grad_norm_(self.model.parameters(), max_norm=1.0)
                
                self.optimizer.step()
                
                # Statistics
                epoch_loss += loss.item()
                predictions = (outputs > 0.5).float()
                epoch_correct += (predictions == labels).sum().item()
                epoch_total += labels.size(0)
            
            # Calculate epoch metrics
            avg_loss = epoch_loss / len(train_loader)
            accuracy = epoch_correct / epoch_total
            
            history['loss'].append(avg_loss)
            history['accuracy'].append(accuracy)
            
            # Validation
            if val_loader is not None:
                self.model.eval()
                val_loss = 0.0
                val_correct = 0
                val_total = 0
                
                with torch.no_grad():
                    for inputs, labels in val_loader:
                        inputs = inputs.to(self.device)
                        labels = labels.to(self.device)
                        
                        outputs = self.model(inputs).squeeze()
                        loss = self.criterion(outputs, labels)
                        
                        val_loss += loss.item()
                        predictions = (outputs > 0.5).float()
                        val_correct += (predictions == labels).sum().item()
                        val_total += labels.size(0)
                
                history['val_loss'].append(val_loss / len(val_loader))
                history['val_accuracy'].append(val_correct / val_total)
                
                self.model.train()
            
            # Log progress
            if (epoch + 1) % 10 == 0 or epoch == 0:
                val_msg = ""
                if val_loader is not None:
                    val_msg = f" | Val Loss: {history['val_loss'][-1]:.4f} | Val Acc: {history['val_accuracy'][-1]:.4f}"
                
                logger.info(f"   Epoch {epoch+1}/{epochs} - Loss: {avg_loss:.4f} | Acc: {accuracy:.4f}{val_msg}")
        
        self.is_trained = True
        self.training_history = history
        
        # Auto-calculate anomaly threshold from training data
        self._calculate_threshold(X_train_norm)
        
        logger.info(f"✅ Training complete!")
        logger.info(f"   Final loss: {history['loss'][-1]:.4f}")
        logger.info(f"   Final accuracy: {history['accuracy'][-1]:.4f}")
        
        return history
    
    def _calculate_threshold(self, X_normalized: np.ndarray) -> None:
        """Calculate optimal anomaly threshold from training data"""
        logger.info("📊 Calculating anomaly threshold...")
        
        # Get predictions on training data
        scores = self._predict_scores(X_normalized)
        
        # Use percentile-based threshold (e.g., 95th percentile of normal data)
        self.anomaly_threshold = np.percentile(scores, 95)
        
        logger.info(f"   Anomaly threshold: {self.anomaly_threshold:.4f} (95th percentile)")
    
    def _predict_scores(self, X: np.ndarray) -> np.ndarray:
        """Get anomaly scores for sequences"""
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
        """
        Predict anomalies
        
        Args:
            X: Input sequences (num_samples, seq_length, num_features)
            threshold: Override anomaly threshold
            
        Returns:
            Binary predictions (1 = anomaly, 0 = normal)
        """
        scores = self._predict_scores(X)
        threshold = threshold or self.anomaly_threshold
        return (scores > threshold).astype(int)
    
    def detect(self, sequence: np.ndarray, feature_names: List[str] = None) -> AnomalyResult:
        """
        Detect anomaly in single sequence
        
        Args:
            sequence: Input sequence (seq_length, num_features) or (num_features,)
            feature_names: Optional feature names for explanation
            
        Returns:
            AnomalyResult object
        """
        # Reshape if needed - ensure (1, seq_length, num_features)
        if sequence.ndim == 1:
            # (num_features,) -> (1, 1, num_features)
            sequence = sequence.reshape(1, 1, -1)
        elif sequence.ndim == 2:
            if sequence.shape[0] == 1:
                # (1, num_features) -> (1, 1, num_features)
                sequence = sequence.reshape(1, 1, -1)
            else:
                # (seq_length, num_features) -> (1, seq_length, num_features)
                sequence = sequence.reshape(1, sequence.shape[0], sequence.shape[1])
        
        # Get anomaly score
        score = self._predict_scores(sequence)[0]
        is_anomaly = score > self.anomaly_threshold
        confidence = score if is_anomaly else 1 - score
        
        # Generate explanation
        explanation = self._generate_explanation(sequence, score, feature_names)
        
        result = AnomalyResult(
            id=str(uuid.uuid4())[:8],
            timestamp=datetime.now(),
            anomaly_score=float(score),
            is_anomaly=bool(is_anomaly),
            confidence=float(confidence),
            sequence_length=len(sequence),
            features=self._extract_features(sequence, feature_names),
            explanation=explanation
        )
        
        if is_anomaly:
            logger.warning(f"⚠️  Anomaly detected: {result.id} (score: {score:.4f})")
        else:
            logger.info(f"✅ Normal: {result.id} (score: {score:.4f})")
        
        return result
    
    def _generate_explanation(self, sequence: np.ndarray, score: float,
                             feature_names: List[str] = None) -> str:
        """Generate human-readable explanation"""
        if score > 0.8:
            severity = "CRITICAL"
        elif score > 0.6:
            severity = "HIGH"
        elif score > self.anomaly_threshold:
            severity = "MEDIUM"
        else:
            severity = "NORMAL"
        
        if feature_names:
            # Find which features contribute most to anomaly
            # sequence shape: (1, seq_length, num_features)
            # Take std across time steps for each feature
            seq_squeezed = sequence.squeeze(0)  # (seq_length, num_features)
            feature_importance = np.std(seq_squeezed, axis=0)  # (num_features,)
            top_feature_indices = feature_importance.argsort()[-3:][::-1]
            top_names = []
            for i in range(len(top_feature_indices)):
                idx = int(top_feature_indices[i])
                if idx < len(feature_names):
                    top_names.append(feature_names[idx])
                else:
                    top_names.append(f"Feature_{idx}")
            features_str = ", ".join(top_names)
            return f"{severity} anomaly (score={score:.3f}). Top contributing features: {features_str}"
        else:
            return f"{severity} anomaly detected (score={score:.3f}, threshold={self.anomaly_threshold:.3f})"
    
    def _extract_features(self, sequence: np.ndarray,
                         feature_names: List[str] = None) -> Dict[str, float]:
        """Extract summary features from sequence"""
        features = {}
        
        # Basic statistics
        features['mean'] = float(np.mean(sequence))
        features['std'] = float(np.std(sequence))
        features['max'] = float(np.max(sequence))
        features['min'] = float(np.min(sequence))
        
        # Add named features if provided
        if feature_names and len(feature_names) == sequence.shape[-1]:
            for i, name in enumerate(feature_names):
                features[f'{name}_mean'] = float(np.mean(sequence[..., i]))
        
        return features
    
    def save(self, path: str) -> None:
        """Save model to disk"""
        if not TORCH_AVAILABLE:
            logger.error("❌ Cannot save model - PyTorch not available")
            return
        
        checkpoint = {
            'model_state_dict': self.model.state_dict(),
            'config': self.config,
            'feature_means': self.feature_means,
            'feature_stds': self.feature_stds,
            'anomaly_threshold': self.anomaly_threshold,
            'training_history': self.training_history,
            'is_trained': self.is_trained
        }
        
        torch.save(checkpoint, path)
        logger.info(f"💾 Model saved to {path}")
    
    def load(self, path: str) -> None:
        """Load model from disk"""
        if not TORCH_AVAILABLE:
            logger.error("❌ Cannot load model - PyTorch not available")
            return
        
        checkpoint = torch.load(path, map_location=self.device)
        
        self.model.load_state_dict(checkpoint['model_state_dict'])
        self.config = checkpoint['config']
        self.feature_means = checkpoint['feature_means']
        self.feature_stds = checkpoint['feature_stds']
        self.anomaly_threshold = checkpoint['anomaly_threshold']
        self.training_history = checkpoint['training_history']
        self.is_trained = checkpoint['is_trained']
        
        logger.info(f"📂 Model loaded from {path}")


def generate_sample_data(num_samples: int = 1000, seq_length: int = 100,
                        num_features: int = 5, anomaly_ratio: float = 0.1) -> Tuple:
    """
    Generate synthetic security time-series data for testing
    
    Args:
        num_samples: Number of sequences
        seq_length: Length of each sequence
        num_features: Number of features per timestep
        anomaly_ratio: Fraction of anomalies
        
    Returns:
        X (sequences), y (labels)
    """
    logger.info(f"📊 Generating synthetic data...")
    logger.info(f"   Samples: {num_samples}")
    logger.info(f"   Sequence length: {seq_length}")
    logger.info(f"   Features: {num_features}")
    logger.info(f"   Anomaly ratio: {anomaly_ratio}")
    
    # Generate normal data (correlated features, smooth patterns)
    X_normal = np.zeros((num_samples, seq_length, num_features))
    
    for i in range(num_samples):
        # Base pattern with some noise
        base = np.sin(np.linspace(0, 4 * np.pi, seq_length))
        for f in range(num_features):
            X_normal[i, :, f] = base * (1 + 0.1 * f) + np.random.normal(0, 0.1, seq_length)
    
    # Generate anomalies (different patterns)
    num_anomalies = int(num_samples * anomaly_ratio)
    X_anomaly = np.zeros((num_anomalies, seq_length, num_features))
    
    for i in range(num_anomalies):
        anomaly_type = np.random.choice(['spike', 'drift', 'noise', 'pattern'])
        
        for f in range(num_features):
            if anomaly_type == 'spike':
                # Sudden spikes
                X_anomaly[i, :, f] = np.random.normal(0, 1, seq_length)
                spike_pos = np.random.randint(0, seq_length, 3)
                X_anomaly[i, spike_pos, f] += np.random.uniform(3, 5, 3)
                
            elif anomaly_type == 'drift':
                # Gradual drift
                X_anomaly[i, :, f] = np.linspace(0, 3, seq_length) + np.random.normal(0, 0.2, seq_length)
                
            elif anomaly_type == 'noise':
                # High frequency noise
                X_anomaly[i, :, f] = np.random.normal(0, 2, seq_length)
                
            elif anomaly_type == 'pattern':
                # Different pattern
                X_anomaly[i, :, f] = np.cos(np.linspace(0, 8 * np.pi, seq_length)) + np.random.normal(0, 0.3, seq_length)
    
    # Combine
    X = np.vstack([X_normal, X_anomaly])
    y = np.concatenate([np.zeros(num_samples), np.ones(num_anomalies)])
    
    # Shuffle
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

Hardware: Optimized for RTX 5060 Ti 16GB (darth/10.0.0.117)

    """)
    
    if not TORCH_AVAILABLE:
        print("⚠️  PyTorch not available. Install with: pip install torch")
        print("   Running in demo mode only.\n")
    
    # Generate synthetic data
    X, y = generate_sample_data(num_samples=500, seq_length=50, 
                                num_features=5, anomaly_ratio=0.15)
    
    # Split data
    split = int(0.8 * len(X))
    X_train, X_test = X[:split], X[split:]
    y_train, y_test = y[:split], y[split:]
    
    print(f"\n📊 Data split: {len(X_train)} train, {len(X_test)} test")
    print(f"   Anomalies: {int(sum(y_train))} train, {int(sum(y_test))} test\n")
    
    # Initialize detector
    config = LSTMConfig(
        input_size=5,
        hidden_size=64,
        num_layers=2,
        dropout=0.2,
        epochs=30,
        batch_size=32
    )
    
    detector = LSTMSecurityDetector(config)
    
    if TORCH_AVAILABLE:
        # Train model
        print("\n📚 Training LSTM model...")
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
        test_seq = X_test[0]  # Shape: (seq_length, num_features) = (50, 5)
        result = detector.detect(test_seq, feature_names=[
            'bytes_sent', 'bytes_recv', 'packets_sent', 'packets_recv', 'connections'
        ])
        
        print(f"\n   Result: {result.explanation}")
        print(f"   Confidence: {result.confidence:.2%}")
        
    else:
        print("⚠️  Skipping training (PyTorch not available)")
        print("\n💡 To enable full functionality:")
        print("   pip install torch torchvision torchaudio")
    
    print("\n" + "="*70)
    print("✅ LSTM Security Detector demo complete!")
    print("="*70)


if __name__ == "__main__":
    main()
