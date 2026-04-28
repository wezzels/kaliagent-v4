#!/usr/bin/env python3
"""
🧠 KaliAgent v5.0.0 - Phase 14: Autoencoder for Novelty Detection

Trains on NORMAL data only - detects ANY deviation (zero-day attacks!)

Author: KaliAgent Team
Status: Alpha (0.1.0)
"""

import logging
import numpy as np
from typing import List, Dict
from datetime import datetime
from dataclasses import dataclass, field
import uuid

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger('Autoencoder')

try:
    import torch
    import torch.nn as nn
    import torch.optim as optim
    from torch.utils.data import DataLoader, TensorDataset
    TORCH_AVAILABLE = True
except ImportError:
    TORCH_AVAILABLE = False
    logger.warning("⚠️ PyTorch not available")


@dataclass
class AEConfig:
    input_dim: int = 100
    latent_dim: int = 32
    hidden_dims: List[int] = field(default_factory=lambda: [256, 128, 64])
    dropout: float = 0.2
    learning_rate: float = 0.001
    batch_size: int = 64
    epochs: int = 100


@dataclass
class NoveltyResult:
    id: str
    timestamp: datetime
    reconstruction_error: float
    is_novel: bool
    confidence: float
    explanation: str = ""


class Autoencoder(nn.Module):
    def __init__(self, input_dim, latent_dim, hidden_dims, dropout):
        super().__init__()
        
        # Encoder
        encoder_layers = []
        prev_dim = input_dim
        for h_dim in hidden_dims:
            encoder_layers.extend([
                nn.Linear(prev_dim, h_dim), nn.ReLU(),
                nn.BatchNorm1d(h_dim), nn.Dropout(dropout)
            ])
            prev_dim = h_dim
        encoder_layers.append(nn.Linear(prev_dim, latent_dim))
        self.encoder = nn.Sequential(*encoder_layers)
        
        # Decoder
        decoder_layers = []
        prev_dim = latent_dim
        for h_dim in reversed(hidden_dims):
            decoder_layers.extend([
                nn.Linear(prev_dim, h_dim), nn.ReLU(),
                nn.BatchNorm1d(h_dim), nn.Dropout(dropout)
            ])
            prev_dim = h_dim
        decoder_layers.append(nn.Linear(prev_dim, input_dim))
        self.decoder = nn.Sequential(*decoder_layers)
        
    def forward(self, x):
        return self.decoder(self.encoder(x))


class AutoencoderDetector:
    VERSION = "0.1.0"
    
    def __init__(self, config: AEConfig = None):
        self.config = config or AEConfig()
        self.model = None
        self.device = None
        self.is_trained = False
        self.feature_means = None
        self.feature_stds = None
        self.novelty_threshold = None
        
        if TORCH_AVAILABLE:
            # Default to GPU if available
            self.device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
            
            # Check if GPU is usable (test tensor operation)
            if torch.cuda.is_available():
                gpu_name = torch.cuda.get_device_name(0)
                try:
                    # Test if CUDA actually works
                    test_tensor = torch.zeros(1).cuda()
                    test_tensor = test_tensor + 1
                    logger.info(f"🔧 Using GPU: {gpu_name}")
                except RuntimeError as e:
                    # CUDA doesn't work
                    logger.warning(f"⚠️  GPU detected: {gpu_name}")
                    logger.warning(f"⚠️  CUDA error: {str(e)[:100]}")
                    logger.warning("⚠️  Falling back to CPU mode")
                    self.device = torch.device('cpu')
            else:
                logger.info("🔧 Using device: CPU")
            
            self._build_model()
        
        logger.info(f"🧠 Autoencoder v{self.VERSION}")
    
    def _build_model(self):
        if not TORCH_AVAILABLE:
            return
        self.model = Autoencoder(
            self.config.input_dim, self.config.latent_dim,
            self.config.hidden_dims, self.config.dropout
        ).to(self.device)
        self.criterion = nn.MSELoss()
        self.optimizer = optim.Adam(self.model.parameters(), lr=self.config.learning_rate)
        logger.info(f"✅ Model built: {sum(p.numel() for p in self.model.parameters()):,} params")
    
    def _normalize(self, X: np.ndarray, fit: bool = False) -> np.ndarray:
        if fit:
            self.feature_means = np.mean(X, axis=0)
            self.feature_stds = np.std(X, axis=0) + 1e-8
        return (X - self.feature_means) / self.feature_stds
    
    def fit(self, X_normal: np.ndarray, X_val: np.ndarray = None,
            epochs: int = None, batch_size: int = None) -> Dict:
        if not TORCH_AVAILABLE:
            return {'error': 'PyTorch not available'}
        
        epochs = epochs or self.config.epochs
        batch_size = batch_size or self.config.batch_size
        
        logger.info(f"📚 Training on NORMAL data only...")
        X_norm = self._normalize(X_normal, fit=True)
        
        train_loader = DataLoader(TensorDataset(torch.FloatTensor(X_norm)),
                                  batch_size=batch_size, shuffle=True)
        
        history = {'loss': [], 'val_loss': []}
        self.model.train()
        
        for epoch in range(epochs):
            epoch_loss = 0.0
            for (inputs,) in train_loader:
                inputs = inputs.to(self.device)
                self.optimizer.zero_grad()
                reconstructed = self.model(inputs)
                loss = self.criterion(reconstructed, inputs)
                loss.backward()
                torch.nn.utils.clip_grad_norm_(self.model.parameters(), max_norm=1.0)
                self.optimizer.step()
                epoch_loss += loss.item()
            
            avg_loss = epoch_loss / len(train_loader)
            history['loss'].append(avg_loss)
            
            if (epoch + 1) % 20 == 0 or epoch == 0:
                logger.info(f"   Epoch {epoch+1}/{epochs} - Loss: {avg_loss:.6f}")
        
        self.is_trained = True
        self._calculate_threshold(X_norm)
        logger.info(f"✅ Training complete! Final loss: {history['loss'][-1]:.6f}")
        return history
    
    def _calculate_threshold(self, X_norm: np.ndarray):
        errors = self._get_errors(X_norm)
        self.novelty_threshold = np.percentile(errors, 99)
        logger.info(f"   Threshold: {self.novelty_threshold:.6f} (99th percentile)")
    
    def _get_errors(self, X: np.ndarray) -> np.ndarray:
        if not TORCH_AVAILABLE or not self.is_trained:
            return np.zeros(len(X))
        
        X_norm = self._normalize(X, fit=False)
        loader = DataLoader(TensorDataset(torch.FloatTensor(X_norm)),
                           batch_size=self.config.batch_size)
        
        self.model.eval()
        errors = []
        with torch.no_grad():
            for (inputs,) in loader:
                inputs = inputs.to(self.device)
                reconstructed = self.model(inputs)
                mse = torch.mean((reconstructed - inputs) ** 2, dim=1)
                errors.extend(mse.cpu().numpy())
        return np.array(errors)
    
    def novelty_score(self, X: np.ndarray) -> np.ndarray:
        return self._get_errors(X)
    
    def detect(self, X: np.ndarray, threshold: float = None) -> np.ndarray:
        scores = self.novelty_score(X)
        threshold = threshold or self.novelty_threshold
        return (scores > threshold).astype(int)
    
    def detect_single(self, sample: np.ndarray) -> NoveltyResult:
        if sample.ndim == 1:
            sample = sample.reshape(1, -1)
        
        score = self.novelty_score(sample)[0]
        is_novel = score > self.novelty_threshold
        confidence = min(1.0, score / self.novelty_threshold) if is_novel else 1 - (score / self.novelty_threshold)
        
        severity = "CRITICAL" if score > self.novelty_threshold * 3 else \
                   "HIGH" if score > self.novelty_threshold * 2 else \
                   "MEDIUM" if is_novel else "NORMAL"
        
        return NoveltyResult(
            id=str(uuid.uuid4())[:8],
            timestamp=datetime.now(),
            reconstruction_error=float(score),
            is_novel=bool(is_novel),
            confidence=float(confidence),
            explanation=f"{severity} novelty (error={score:.6f})"
        )


def generate_normal_data(n=5000, dim=50):
    X = np.zeros((n, dim))
    for i in range(n):
        base = np.random.normal(0, 1, dim)
        for j in range(1, dim):
            base[j] = 0.5 * base[j-1] + 0.5 * base[j]
        X[i] = base
    return X


def generate_attack_data(n=500, dim=50, attack_type='spike'):
    X = np.zeros((n, dim))
    for i in range(n):
        if attack_type == 'spike':
            X[i] = np.random.normal(0, 1, dim)
            spikes = np.random.choice(dim, 5, replace=False)
            X[i, spikes] += np.random.uniform(3, 5, 5)
        elif attack_type == 'drift':
            X[i] = np.random.normal(0, 1, dim) + np.random.uniform(2, 4)
    return X


def main():
    print("""
╔═══════════════════════════════════════════════════════════════╗
║     🧠 KALIAGENT v5.0.0 - AUTOENCODER NOVELTY DETECTOR       ║
║                    Phase 14: Alpha 0.1.0                      ║
╚═══════════════════════════════════════════════════════════════╝

Key: Trains on NORMAL data only - detects ANY deviation!

    """)
    
    if not TORCH_AVAILABLE:
        print("⚠️ PyTorch not available")
        return
    
    # Generate data
    X_normal = generate_normal_data(n=3000, dim=50)
    X_attack = generate_attack_data(n=100, dim=50, attack_type='spike')
    
    X_test = np.vstack([X_normal[:500], X_attack])
    y_test = np.concatenate([np.zeros(500), np.ones(len(X_attack))])
    
    print(f"📊 Data: {len(X_normal)} train (normal), {len(X_test)} test ({int(sum(y_test))} attacks)\n")
    
    config = AEConfig(input_dim=50, latent_dim=16, hidden_dims=[128, 64, 32], epochs=50, batch_size=64)
    detector = AutoencoderDetector(config)
    
    # Train
    print("📚 Training autoencoder on NORMAL data only...")
    history = detector.fit(X_normal, X_val=X_normal[500:1000])
    
    # Evaluate
    print("\n📊 Evaluating...")
    predictions = detector.detect(X_test)
    
    accuracy = np.mean(predictions == y_test)
    precision = np.sum((predictions == 1) & (y_test == 1)) / max(np.sum(predictions == 1), 1)
    recall = np.sum((predictions == 1) & (y_test == 1)) / max(np.sum(y_test == 1), 1)
    f1 = 2 * precision * recall / max(precision + recall, 1e-8)
    
    print(f"\n✅ Test Results:")
    print(f"   Accuracy: {accuracy:.4f}")
    print(f"   Precision: {precision:.4f}")
    print(f"   Recall: {recall:.4f}")
    print(f"   F1 Score: {f1:.4f}")
    
    # Test single
    print("\n🔍 Testing single sample...")
    result = detector.detect_single(X_test[0])
    print(f"   Result: {result.explanation}")
    print(f"   Confidence: {result.confidence:.2%}")
    
    print("\n" + "="*70)
    print("✅ Autoencoder demo complete!")
    print("="*70)


if __name__ == "__main__":
    main()
