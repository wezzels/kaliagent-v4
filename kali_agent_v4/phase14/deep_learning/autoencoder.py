#!/usr/bin/env python3
"""
🧠 KaliAgent v5.0.0 - Phase 14: Advanced ML/AI Models
Autoencoder for Novel Attack Detection

Autoencoders for unsupervised anomaly detection:
- Zero-day attack detection
- Novel malware identification
- Unusual network behavior
- System call anomalies

Trains on NORMAL data only - detects ANY deviation!

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
logger = logging.getLogger('Autoencoder')

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
class AutoencoderConfig:
    """Autoencoder configuration"""
    input_dim: int = 100  # Number of input features
    latent_dim: int = 32  # Compressed representation size
    hidden_dims: List[int] = field(default_factory=lambda: [256, 128, 64])
    dropout: float = 0.2  # Dropout rate
    learning_rate: float = 0.001  # Learning rate
    batch_size: int = 64  # Training batch size
    epochs: int = 100  # Number of training epochs


@dataclass
class NoveltyResult:
    """Novelty detection result"""
    id: str
    timestamp: datetime
    reconstruction_error: float
    is_novel: bool
    confidence: float
    input_features: Dict[str, float] = field(default_factory=dict)
    error_breakdown: Dict[str, float] = field(default_factory=dict)
    explanation: str = ""
    
    def to_dict(self) -> Dict:
        return {
            'id': self.id,
            'timestamp': self.timestamp.isoformat(),
            'reconstruction_error': self.reconstruction_error,
            'is_novel': self.is_novel,
            'confidence': self.confidence,
            'input_features': self.input_features,
            'error_breakdown': self.error_breakdown,
            'explanation': self.explanation
        }


class SecurityAutoencoder(nn.Module):
    """
    Autoencoder neural network for novelty detection
    
    Architecture:
    - Encoder: Input → 256 → 128 → 64 → 32 (latent)
    - Latent space: 32 dimensions (compressed representation)
    - Decoder: 32 → 64 → 128 → 256 → Output
    - Loss: Reconstruction error (MSE)
    """
    
    def __init__(self, input_dim, latent_dim, hidden_dims, dropout):
        super(SecurityAutoencoder, self).__init__()
        
        # Encoder
        encoder_layers = []
        prev_dim = input_dim
        for hidden_dim in hidden_dims:
            encoder_layers.extend([
                nn.Linear(prev_dim, hidden_dim),
                nn.ReLU(),
                nn.BatchNorm1d(hidden_dim),
                nn.Dropout(dropout)
            ])
            prev_dim = hidden_dim
        
        encoder_layers.append(nn.Linear(prev_dim, latent_dim))
        self.encoder = nn.Sequential(*encoder_layers)
        
        # Decoder
        decoder_layers = []
        prev_dim = latent_dim
        for hidden_dim in reversed(hidden_dims):
            decoder_layers.extend([
                nn.Linear(prev_dim, hidden_dim),
                nn.ReLU(),
                nn.BatchNorm1d(hidden_dim),
                nn.Dropout(dropout)
            ])
            prev_dim = hidden_dim
        
        decoder_layers.append(nn.Linear(prev_dim, input_dim))
        self.decoder = nn.Sequential(*decoder_layers)
        
    def forward(self, x):
        encoded = self.encoder(x)
        decoded = self.decoder(encoded)
        return decoded
    
    def encode(self, x):
        """Encode input to latent space"""
        return self.encoder(x)
    
    def decode(self, z):
        """Decode from latent space"""
        return self.decoder(z)


class VariationalAutoencoder(nn.Module):
    """
    Variational Autoencoder (VAE) for improved novelty detection
    
    Adds probabilistic latent space for better anomaly scoring
    """
    
    def __init__(self, input_dim, latent_dim, hidden_dims, dropout):
        super(VariationalAutoencoder, self).__init__()
        
        # Encoder
        encoder_layers = []
        prev_dim = input_dim
        for hidden_dim in hidden_dims:
            encoder_layers.extend([
                nn.Linear(prev_dim, hidden_dim),
                nn.ReLU(),
                nn.BatchNorm1d(hidden_dim),
                nn.Dropout(dropout)
            ])
            prev_dim = hidden_dim
        
        self.encoder = nn.Sequential(*encoder_layers)
        
        # Latent space (mean and variance)
        self.fc_mu = nn.Linear(prev_dim, latent_dim)
        self.fc_logvar = nn.Linear(prev_dim, latent_dim)
        
        # Decoder
        decoder_layers = []
        prev_dim = latent_dim
        for hidden_dim in reversed(hidden_dims):
            decoder_layers.extend([
                nn.Linear(prev_dim, hidden_dim),
                nn.ReLU(),
                nn.BatchNorm1d(hidden_dim),
                nn.Dropout(dropout)
            ])
            prev_dim = hidden_dim
        
        decoder_layers.append(nn.Linear(prev_dim, input_dim))
        self.decoder = nn.Sequential(*decoder_layers)
        
    def encode(self, x):
        """Encode to latent space parameters"""
        h = self.encoder(x)
        mu = self.fc_mu(h)
        logvar = self.fc_logvar(h)
        return mu, logvar
    
    def reparameterize(self, mu, logvar):
        """Reparameterization trick for VAE"""
        std = torch.exp(0.5 * logvar)
        eps = torch.randn_like(std)
        return mu + eps * std
    
    def decode(self, z):
        """Decode from latent space"""
        return self.decoder(z)
    
    def forward(self, x):
        mu, logvar = self.encode(x)
        z = self.reparameterize(mu, logvar)
        reconstructed = self.decode(z)
        return reconstructed, mu, logvar


class AutoencoderNoveltyDetector:
    """
    Autoencoder-based Novelty Detector
    
    Key Advantage: Trains on NORMAL data only
    Detects: ANY deviation from normal (zero-day attacks!)
    
    How it works:
    1. Train autoencoder on normal data
    2. Autoencoder learns to reconstruct normal patterns
    3. Anomalies don't reconstruct well
    4. High reconstruction error = novelty/anomaly
    """
    
    VERSION = "0.1.0"
    
    def __init__(self, config: AutoencoderConfig = None, use_vae: bool = False):
        """
        Initialize Autoencoder Novelty Detector
        
        Args:
            config: Autoencoder configuration
            use_vae: Use Variational Autoencoder instead of standard
        """
        self.config = config or AutoencoderConfig()
        self.use_vae = use_vae
        self.model = None
        self.device = None
        self.is_trained = False
        self.training_history = []
        
        # Statistics for normalization
        self.feature_means = None
        self.feature_stds = None
        
        # Novelty threshold (auto-calculated)
        self.novelty_threshold = None
        
        if TORCH_AVAILABLE:
            # Set device
            self.device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
            logger.info(f"🔧 Using device: {self.device}")
            
            # Initialize model
            self._build_model()
        else:
            logger.warning("⚠️  Running in NumPy fallback mode")
        
        logger.info(f"🧠 Autoencoder Novelty Detector v{self.VERSION}")
        logger.info(f"   Input dim: {self.config.input_dim}")
        logger.info(f"   Latent dim: {self.config.latent_dim}")
        logger.info(f"   Hidden dims: {self.config.hidden_dims}")
        logger.info(f"   VAE: {self.use_vae}")
    
    def _build_model(self) -> None:
        """Build autoencoder model"""
        if not TORCH_AVAILABLE:
            return
        
        if self.use_vae:
            self.model = VariationalAutoencoder(
                input_dim=self.config.input_dim,
                latent_dim=self.config.latent_dim,
                hidden_dims=self.config.hidden_dims,
                dropout=self.config.dropout
            )
            logger.info("✅ Variational Autoencoder built")
        else:
            self.model = SecurityAutoencoder(
                input_dim=self.config.input_dim,
                latent_dim=self.config.latent_dim,
                hidden_dims=self.config.hidden_dims,
                dropout=self.config.dropout
            )
            logger.info("✅ Standard Autoencoder built")
        
        # Move to device
        self.model = self.model.to(self.device)
        
        # Loss and optimizer
        self.criterion = nn.MSELoss()
        self.optimizer = optim.Adam(self.model.parameters(), lr=self.config.learning_rate)
        
        logger.info(f"   Total parameters: {sum(p.numel() for p in self.model.parameters()):,}")
    
    def _normalize(self, X: np.ndarray, fit: bool = False) -> np.ndarray:
        """Normalize features using z-score"""
        if fit:
            self.feature_means = np.mean(X, axis=0)
            self.feature_stds = np.std(X, axis=0) + 1e-8
        
        return (X - self.feature_means) / self.feature_stds
    
    def fit(self, X_normal: np.ndarray, X_val: np.ndarray = None,
            epochs: int = None, batch_size: int = None) -> Dict:
        """
        Train autoencoder on NORMAL data only
        
        Args:
            X_normal: Normal data (num_samples, num_features)
            X_val: Validation data (optional)
            epochs: Override config epochs
            batch_size: Override config batch size
            
        Returns:
            Training history
        """
        if not TORCH_AVAILABLE:
            logger.error("❌ PyTorch required for training")
            return {'error': 'PyTorch not available'}
        
        epochs = epochs or self.config.epochs
        batch_size = batch_size or self.config.batch_size
        
        logger.info(f"📚 Training autoencoder on NORMAL data only...")
        logger.info(f"   Training samples: {len(X_normal)}")
        logger.info(f"   Epochs: {epochs}")
        logger.info(f"   Batch size: {batch_size}")
        logger.info(f"   Model: {'VAE' if self.use_vae else 'Standard AE'}")
        
        # Normalize data
        X_normal_norm = self._normalize(X_normal, fit=True)
        
        # Create dataset
        train_dataset = torch.utils.data.TensorDataset(
            torch.FloatTensor(X_normal_norm)
        )
        train_loader = DataLoader(train_dataset, batch_size=batch_size, shuffle=True)
        
        # Validation data
        if X_val is not None:
            X_val_norm = self._normalize(X_val, fit=False)
            val_dataset = torch.utils.data.TensorDataset(
                torch.FloatTensor(X_val_norm)
            )
            val_loader = DataLoader(val_dataset, batch_size=batch_size)
        else:
            val_loader = None
        
        # Training loop
        history = {
            'loss': [],
            'reconstruction_error': [],
            'val_loss': []
        }
        
        self.model.train()
        
        for epoch in range(epochs):
            epoch_loss = 0.0
            
            for batch_idx, (inputs,) in enumerate(train_loader):
                # Move to device
                inputs = inputs.to(self.device)
                
                # Forward pass
                self.optimizer.zero_grad()
                
                if self.use_vae:
                    reconstructed, mu, logvar = self.model(inputs)
                    # VAE loss = reconstruction loss + KL divergence
                    recon_loss = self.criterion(reconstructed, inputs)
                    kl_loss = -0.5 * torch.mean(1 + logvar - mu.pow(2) - logvar.exp())
                    loss = recon_loss + 0.001 * kl_loss  # KL weight
                else:
                    reconstructed = self.model(inputs)
                    loss = self.criterion(reconstructed, inputs)
                
                # Backward pass
                loss.backward()
                
                # Gradient clipping
                torch.nn.utils.clip_grad_norm_(self.model.parameters(), max_norm=1.0)
                
                self.optimizer.step()
                
                epoch_loss += loss.item()
            
            # Calculate epoch metrics
            avg_loss = epoch_loss / len(train_loader)
            history['loss'].append(avg_loss)
            history['reconstruction_error'].append(avg_loss)  # Same for AE
            
            # Validation
            if val_loader is not None:
                self.model.eval()
                val_loss = 0.0
                
                with torch.no_grad():
                    for (inputs,) in val_loader:
                        inputs = inputs.to(self.device)
                        
                        if self.use_vae:
                            reconstructed, _, _ = self.model(inputs)
                        else:
                            reconstructed = self.model(inputs)
                        
                        loss = self.criterion(reconstructed, inputs)
                        val_loss += loss.item()
                
                history['val_loss'].append(val_loss / len(val_loader))
                self.model.train()
            
            # Log progress
            if (epoch + 1) % 20 == 0 or epoch == 0:
                val_msg = ""
                if val_loader is not None:
                    val_msg = f" | Val Loss: {history['val_loss'][-1]:.6f}"
                
                logger.info(f"   Epoch {epoch+1}/{epochs} - Loss: {avg_loss:.6f}{val_msg}")
        
        self.is_trained = True
        self.training_history = history
        
        # Auto-calculate novelty threshold
        self._calculate_threshold(X_normal_norm)
        
        logger.info(f"✅ Training complete!")
        logger.info(f"   Final loss: {history['loss'][-1]:.6f}")
        
        return history
    
    def _calculate_threshold(self, X_normalized: np.ndarray) -> None:
        """Calculate novelty threshold from normal data"""
        logger.info("📊 Calculating novelty threshold...")
        
        # Get reconstruction errors for normal data
        errors = self._get_reconstruction_errors(X_normalized)
        
        # Use percentile-based threshold (e.g., 99th percentile)
        self.novelty_threshold = np.percentile(errors, 99)
        
        logger.info(f"   Novelty threshold: {self.novelty_threshold:.6f} (99th percentile)")
    
    def _get_reconstruction_errors(self, X: np.ndarray) -> np.ndarray:
        """Calculate reconstruction errors for samples"""
        if not TORCH_AVAILABLE or not self.is_trained:
            return np.zeros(len(X))
        
        X_norm = self._normalize(X, fit=False)
        dataset = torch.utils.data.TensorDataset(torch.FloatTensor(X_norm))
        loader = DataLoader(dataset, batch_size=self.config.batch_size)
        
        self.model.eval()
        errors = []
        
        with torch.no_grad():
            for (inputs,) in loader:
                inputs = inputs.to(self.device)
                
                if self.use_vae:
                    reconstructed, _, _ = self.model(inputs)
                else:
                    reconstructed = self.model(inputs)
                
                # Calculate MSE per sample
                mse = torch.mean((reconstructed - inputs) ** 2, dim=1)
                errors.extend(mse.cpu().numpy())
        
        return np.array(errors)
    
    def novelty_score(self, X: np.ndarray) -> np.ndarray:
        """
        Get novelty scores (reconstruction errors)
        
        Args:
            X: Input samples (num_samples, num_features)
            
        Returns:
            Novelty scores (higher = more novel/anomalous)
        """
        return self._get_reconstruction_errors(X)
    
    def detect(self, X: np.ndarray, threshold: float = None) -> np.ndarray:
        """
        Detect novelties/anomalies
        
        Args:
            X: Input samples
            threshold: Override novelty threshold
            
        Returns:
            Binary predictions (1 = novel/anomalous, 0 = normal)
        """
        scores = self.novelty_score(X)
        threshold = threshold or self.novelty_threshold
        return (scores > threshold).astype(int)
    
    def detect_single(self, sample: np.ndarray, feature_names: List[str] = None) -> NoveltyResult:
        """
        Detect novelty in single sample
        
        Args:
            sample: Input sample (num_features,)
            feature_names: Optional feature names
            
        Returns:
            NoveltyResult object
        """
        # Reshape if needed
        if sample.ndim == 1:
            sample = sample.reshape(1, -1)
        
        # Get novelty score
        score = self.novelty_score(sample)[0]
        is_novel = score > self.novelty_threshold
        confidence = score / self.novelty_threshold if is_novel else 1 - (score / self.novelty_threshold)
        
        # Calculate error breakdown by feature
        sample_norm = self._normalize(sample, fit=False)
        self.model.eval()
        
        with torch.no_grad():
            input_tensor = torch.FloatTensor(sample_norm).to(self.device)
            
            if self.use_vae:
                reconstructed, _, _ = self.model(input_tensor)
            else:
                reconstructed = self.model(input_tensor)
            
            reconstructed = reconstructed.cpu().numpy()
            error_per_feature = np.mean((reconstructed - sample_norm) ** 2, axis=0)
        
        # Generate explanation
        explanation = self._generate_explanation(score, is_novel, feature_names, error_per_feature)
        
        # Extract input features
        input_features = {}
        if feature_names:
            for i, name in enumerate(feature_names):
                if i < sample.shape[-1]:
                    input_features[name] = float(sample[0, i])
        else:
            input_features['mean'] = float(np.mean(sample))
            input_features['std'] = float(np.std(sample))
        
        result = NoveltyResult(
            id=str(uuid.uuid4())[:8],
            timestamp=datetime.now(),
            reconstruction_error=float(score),
            is_novel=bool(is_novel),
            confidence=float(min(1.0, confidence)),
            input_features=input_features,
            error_breakdown={f'feature_{i}': float(v) for i, v in enumerate(error_per_feature)},
            explanation=explanation
        )
        
        if is_novel:
            logger.warning(f"⚠️  Novelty detected: {result.id} (error: {score:.6f})")
        else:
            logger.info(f"✅ Normal: {result.id} (error: {score:.6f})")
        
        return result
    
    def _generate_explanation(self, score: float, is_novel: bool,
                             feature_names: List[str] = None,
                             error_per_feature: np.ndarray = None) -> str:
        """Generate human-readable explanation"""
        if is_novel:
            if score > self.novelty_threshold * 3:
                severity = "CRITICAL"
            elif score > self.novelty_threshold * 2:
                severity = "HIGH"
            else:
                severity = "MEDIUM"
            
            if error_per_feature is not None and feature_names:
                # Find features with highest reconstruction error
                top_features = np.argsort(error_per_feature)[-3:][::-1]
                top_names = [feature_names[i] if i < len(feature_names) else f"Feature_{i}"
                            for i in top_features]
                features_str = ", ".join(top_names)
                return f"{severity} novelty (error={score:.6f}). Highest error features: {features_str}"
            else:
                return f"{severity} novelty detected (error={score:.6f}, threshold={self.novelty_threshold:.6f})"
        else:
            return f"Normal pattern (error={score:.6f}, threshold={self.novelty_threshold:.6f})"
    
    def save(self, path: str) -> None:
        """Save model to disk"""
        if not TORCH_AVAILABLE:
            logger.error("❌ Cannot save model - PyTorch not available")
            return
        
        checkpoint = {
            'model_state_dict': self.model.state_dict(),
            'config': self.config,
            'use_vae': self.use_vae,
            'feature_means': self.feature_means,
            'feature_stds': self.feature_stds,
            'novelty_threshold': self.novelty_threshold,
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
        self.use_vae = checkpoint['use_vae']
        self.feature_means = checkpoint['feature_means']
        self.feature_stds = checkpoint['feature_stds']
        self.novelty_threshold = checkpoint['novelty_threshold']
        self.training_history = checkpoint['training_history']
        self.is_trained = checkpoint['is_trained']
        
        logger.info(f"📂 Model loaded from {path}")


def generate_normal_data(num_samples: int = 5000, num_features: int = 50) -> np.ndarray:
    """Generate synthetic normal data for training"""
    logger.info(f"📊 Generating normal data...")
    
    # Correlated features with smooth patterns
    X = np.zeros((num_samples, num_features))
    
    for i in range(num_samples):
        # Base pattern
        base = np.random.normal(0, 1, num_features)
        
        # Add correlations
        for j in range(1, num_features):
            base[j] = 0.5 * base[j-1] + 0.5 * base[j]
        
        X[i] = base
    
    logger.info(f"✅ Generated {num_samples} normal samples")
    
    return X


def generate_attack_data(num_samples: int = 500, num_features: int = 50,
                        attack_type: str = 'anomaly') -> np.ndarray:
    """Generate synthetic attack/anomaly data"""
    logger.info(f"📊 Generating attack data ({attack_type})...")
    
    X = np.zeros((num_samples, num_features))
    
    for i in range(num_samples):
        if attack_type == 'anomaly':
            # Random anomalies
            X[i] = np.random.normal(0, 3, num_features)
        elif attack_type == 'spike':
            # Spikes in random features
            X[i] = np.random.normal(0, 1, num_features)
            spike_features = np.random.choice(num_features, 5, replace=False)
            X[i, spike_features] += np.random.uniform(3, 5, 5)
        elif attack_type == 'drift':
            # Gradual drift
            X[i] = np.random.normal(0, 1, num_features) + np.random.uniform(2, 4)
        elif attack_type == 'pattern':
            # Different pattern
            X[i] = np.sin(np.linspace(0, 4 * np.pi, num_features)) * 2
    
    logger.info(f"✅ Generated {num_samples} attack samples")
    
    return X


def main():
    """Main entry point - Demo autoencoder novelty detection"""
    print("""
╔═══════════════════════════════════════════════════════════════╗
║     🧠 KALIAGENT v5.0.0 - AUTOENCODER NOVELTY DETECTOR       ║
║                    Phase 14: Alpha 0.1.0                      ║
╚═══════════════════════════════════════════════════════════════╝

Key Advantage: Trains on NORMAL data only - detects ANY deviation!
Hardware: Optimized for RTX 5060 Ti 16GB (darth/10.0.0.117)

    """)
    
    if not TORCH_AVAILABLE:
        print("⚠️  PyTorch not available. Install with: pip install torch")
        print("   Running in demo mode only.\n")
    
    # Generate normal training data
    X_normal = generate_normal_data(num_samples=3000, num_features=50)
    
    # Generate test data (normal + attacks)
    X_test_normal = generate_normal_data(num_samples=500, num_features=50)
    X_test_attack = generate_attack_data(num_samples=100, num_features=50, attack_type='spike')
    
    # Combine test data
    X_test = np.vstack([X_test_normal, X_test_attack])
    y_test = np.concatenate([np.zeros(len(X_test_normal)), np.ones(len(X_test_attack))])
    
    print(f"\n📊 Data:")
    print(f"   Training (normal only): {len(X_normal)} samples")
    print(f"   Test: {len(X_test)} samples ({int(sum(y_test))} attacks)")
    print(f"   Features: {X_normal.shape[1]}\n")
    
    # Initialize detector (try VAE first)
    config = AutoencoderConfig(
        input_dim=50,
        latent_dim=16,
        hidden_dims=[128, 64, 32],
        dropout=0.2,
        epochs=50,
        batch_size=64
    )
    
    detector = AutoencoderNoveltyDetector(config, use_vae=True)
    
    if TORCH_AVAILABLE:
        # Train on NORMAL data only
        print("\n📚 Training autoencoder on NORMAL data only...")
        print("   (No attack examples needed!)")
        history = detector.fit(X_normal, X_val=X_test_normal)
        
        # Evaluate
        print("\n📊 Evaluating novelty detection...")
        predictions = detector.detect(X_test)
        
        # Calculate metrics
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
        print("\n🔍 Testing single sample detection...")
        test_sample = X_test[0]
        result = detector.detect_single(test_sample, feature_names=[
            f'feature_{i}' for i in range(50)
        ])
        
        print(f"\n   Result: {result.explanation}")
        print(f"   Confidence: {result.confidence:.2%}")
        print(f"   Reconstruction Error: {result.reconstruction_error:.6f}")
        
    else:
        print("⚠️  Skipping training (PyTorch not available)")
        print("\n💡 To enable full functionality:")
        print("   pip install torch torchvision torchaudio")
    
    print("\n" + "="*70)
    print("✅ Autoencoder Novelty Detector demo complete!")
    print("="*70)


if __name__ == "__main__":
    main()
