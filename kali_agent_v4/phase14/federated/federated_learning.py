#!/usr/bin/env python3
"""
🧠 KaliAgent v5.0.0 - Phase 14: Federated Learning

Privacy-preserving distributed ML training:
- Federated averaging (FedAvg) algorithm
- Multiple clients train locally
- Only model updates (gradients) are shared
- Differential privacy support
- Secure aggregation ready

Author: KaliAgent Team
Status: Alpha (0.1.0)
"""

import logging
import numpy as np
from typing import List, Dict, Optional, Tuple
from dataclasses import dataclass, field
from datetime import datetime
import json
import copy

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger('FederatedLearning')

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
class ClientConfig:
    """Federated client configuration"""
    client_id: str
    data_samples: int = 1000
    local_epochs: int = 5
    batch_size: int = 32
    learning_rate: float = 0.01
    differential_privacy: bool = False
    privacy_epsilon: float = 1.0  # Differential privacy budget
    clip_norm: float = 1.0  # Gradient clipping norm


@dataclass
class ClientUpdate:
    """Model update from client"""
    client_id: str
    timestamp: str
    num_samples: int
    model_delta: Dict[str, np.ndarray]  # Gradient updates
    loss: float
    metrics: Dict[str, float] = field(default_factory=dict)
    
    def to_dict(self) -> Dict:
        return {
            'client_id': self.client_id,
            'timestamp': self.timestamp,
            'num_samples': self.num_samples,
            'loss': self.loss,
            'metrics': self.metrics,
            # Note: model_delta not serialized for security
        }


@dataclass
class FederatedRound:
    """Federated learning round metadata"""
    round_id: int
    timestamp: str
    num_clients: int
    global_model_version: str
    participating_clients: List[str]
    aggregation_metrics: Dict[str, float]
    round_duration_seconds: float


class FederatedClient:
    """
    Federated learning client
    
    - Receives global model from coordinator
    - Trains on local data (never leaves client)
    - Sends only model updates (gradients)
    - Receives updated global model
    """
    
    def __init__(self, config: ClientConfig, model: nn.Module):
        self.config = config
        self.model = copy.deepcopy(model)
        self.device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
        self.model = self.model.to(self.device)
        
        # Local data (simulated)
        self.local_data = self._generate_local_data()
        
        logger.info(f"👤 Client {config.client_id} initialized")
        logger.info(f"   Local samples: {config.data_samples}")
        logger.info(f"   Device: {self.device}")
    
    def _generate_local_data(self) -> Tuple:
        """Generate synthetic local data (simulates real client data)"""
        # In real implementation, this would be actual client data
        # Each client has different data distribution (non-IID)
        
        np.random.seed(hash(self.config.client_id) % 2**32)
        
        # Generate classification data with client-specific distribution
        n_samples = self.config.data_samples
        n_features = 50
        
        # Client-specific bias (simulates non-IID data)
        client_bias = hash(self.config.client_id) % 100 / 100.0
        
        X = np.random.randn(n_samples, n_features).astype(np.float32)
        y = (np.sum(X[:, :10], axis=1) + client_bias > 0).astype(np.float32)
        
        return torch.FloatTensor(X), torch.FloatTensor(y)
    
    def receive_global_model(self, global_model_state: Dict[str, np.ndarray]):
        """Receive and load global model weights"""
        state_dict = {}
        for key, value in global_model_state.items():
            state_dict[key] = torch.FloatTensor(value).to(self.device)
        self.model.load_state_dict(state_dict)
        logger.debug(f"   Received global model")
    
    def train_local(self) -> ClientUpdate:
        """Train on local data and return model update"""
        logger.info(f"🏋️  Client {self.config.client_id} training locally...")
        
        # Create data loader
        X, y = self.local_data
        dataset = TensorDataset(X, y)
        loader = DataLoader(dataset, batch_size=self.config.batch_size, shuffle=True)
        
        # Optimizer
        optimizer = optim.SGD(self.model.parameters(), lr=self.config.learning_rate)
        criterion = nn.BCELoss()
        
        # Store initial weights
        initial_weights = {}
        for name, param in self.model.named_parameters():
            initial_weights[name] = param.cpu().detach().numpy().copy()
        
        # Local training
        self.model.train()
        total_loss = 0.0
        num_batches = 0
        
        for epoch in range(self.config.local_epochs):
            epoch_loss = 0.0
            for batch_X, batch_y in loader:
                batch_X, batch_y = batch_X.to(self.device), batch_y.to(self.device)
                
                optimizer.zero_grad()
                outputs = self.model(batch_X).squeeze()
                loss = criterion(outputs, batch_y)
                
                # Differential privacy: add noise to gradients
                if self.config.differential_privacy:
                    loss.backward()
                    # Clip gradients
                    torch.nn.utils.clip_grad_norm_(
                        self.model.parameters(), 
                        self.config.clip_norm
                    )
                    # Add Gaussian noise
                    for param in self.model.parameters():
                        if param.grad is not None:
                            noise = torch.randn_like(param.grad) * (self.config.clip_norm / self.config.privacy_epsilon)
                            param.grad.add_(noise)
                else:
                    loss.backward()
                    optimizer.step()
                
                epoch_loss += loss.item()
                num_batches += 1
            
            avg_loss = epoch_loss / len(loader)
            logger.debug(f"   Epoch {epoch+1}/{self.config.local_epochs} - Loss: {avg_loss:.4f}")
            total_loss += avg_loss
        
        avg_loss = total_loss / self.config.local_epochs
        
        # Calculate model delta (gradients)
        model_delta = {}
        for name, param in self.model.named_parameters():
            final_weights = param.cpu().detach().numpy()
            delta = final_weights - initial_weights[name]
            model_delta[name] = delta
        
        # Create update
        update = ClientUpdate(
            client_id=self.config.client_id,
            timestamp=datetime.now().isoformat(),
            num_samples=self.config.data_samples,
            model_delta=model_delta,
            loss=avg_loss,
            metrics={'accuracy': self._evaluate_local()}
        )
        
        logger.info(f"✅ Client {self.config.client_id} training complete")
        logger.info(f"   Loss: {avg_loss:.4f}, Accuracy: {update.metrics['accuracy']:.4f}")
        
        return update
    
    def _evaluate_local(self) -> float:
        """Evaluate model on local data"""
        self.model.eval()
        X, y = self.local_data
        X, y = X.to(self.device), y.to(self.device)
        
        with torch.no_grad():
            outputs = self.model(X).squeeze()
            predictions = (outputs > 0.5).float()
            accuracy = (predictions == y).sum().item() / len(y)
        
        return accuracy


class FederatedCoordinator:
    """
    Federated learning coordinator
    
    - Manages multiple clients
    - Aggregates model updates using FedAvg
    - Maintains global model
    - Tracks training progress
    """
    
    VERSION = "0.1.0"
    
    def __init__(self, global_model: nn.Module, num_clients: int = 10):
        self.global_model = global_model
        self.device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
        self.global_model = self.global_model.to(self.device)
        
        self.num_clients = num_clients
        self.clients: List[FederatedClient] = []
        self.round_history: List[FederatedRound] = []
        self.current_round = 0
        
        # Initialize clients
        self._initialize_clients()
        
        logger.info(f"🎛️ Federated Coordinator v{self.VERSION}")
        logger.info(f"   Global model: {self._count_parameters():,} parameters")
        logger.info(f"   Num clients: {num_clients}")
        logger.info(f"   Device: {self.device}")
    
    def _count_parameters(self) -> int:
        """Count model parameters"""
        return sum(p.numel() for p in self.global_model.parameters())
    
    def _initialize_clients(self):
        """Initialize federated clients"""
        for i in range(self.num_clients):
            config = ClientConfig(
                client_id=f"client_{i:03d}",
                data_samples=np.random.randint(500, 2000),  # Variable data per client
                local_epochs=np.random.randint(3, 7),
                differential_privacy=np.random.choice([True, False]),  # Some clients use DP
                privacy_epsilon=np.random.uniform(0.5, 2.0)
            )
            client = FederatedClient(config, self.global_model)
            self.clients.append(client)
        
        logger.info(f"✅ Initialized {len(self.clients)} clients")
    
    def get_global_model_state(self) -> Dict[str, np.ndarray]:
        """Get current global model weights"""
        state_dict = {}
        for name, param in self.global_model.state_dict().items():
            state_dict[name] = param.cpu().numpy()
        return state_dict
    
    def aggregate_updates(self, updates: List[ClientUpdate]) -> Dict[str, np.ndarray]:
        """
        Aggregate client updates using FedAvg
        
        FedAvg formula:
        global_weights = Σ (n_i / N) * client_weights_i
        
        where n_i = samples on client i, N = total samples
        """
        logger.info(f"📊 Aggregating {len(updates)} client updates...")
        
        # Calculate total samples
        total_samples = sum(update.num_samples for update in updates)
        
        # Initialize aggregated weights
        aggregated_delta = {}
        for name in updates[0].model_delta.keys():
            aggregated_delta[name] = np.zeros_like(updates[0].model_delta[name])
        
        # Weighted average
        for update in updates:
            weight = update.num_samples / total_samples
            for name, delta in update.model_delta.items():
                aggregated_delta[name] += weight * delta
        
        # Apply aggregated delta to global model
        new_state_dict = {}
        for name, param in self.global_model.state_dict().items():
            current_weights = param.cpu().numpy()
            new_weights = current_weights + aggregated_delta[name]
            new_state_dict[name] = new_weights
        
        logger.info(f"✅ Aggregation complete")
        
        return new_state_dict
    
    def run_round(self) -> FederatedRound:
        """Run one federated learning round"""
        start_time = datetime.now()
        self.current_round += 1
        
        logger.info(f"\n{'='*70}")
        logger.info(f"🔄 Federated Round {self.current_round}")
        logger.info(f"{'='*70}")
        
        # Select random subset of clients (simulates real FL)
        num_participating = min(self.num_clients, np.random.randint(5, self.num_clients + 1))
        participating_clients = np.random.choice(self.clients, num_participating, replace=False)
        
        # Get current global model
        global_state = self.get_global_model_state()
        
        # Clients train locally
        updates = []
        for client in participating_clients:
            client.receive_global_model(global_state)
            update = client.train_local()
            updates.append(update)
        
        # Aggregate updates
        new_global_state = self.aggregate_updates(updates)
        
        # Update global model
        state_dict = {}
        for name, value in new_global_state.items():
            state_dict[name] = torch.FloatTensor(value).to(self.device)
        self.global_model.load_state_dict(state_dict)
        
        # Calculate round metrics
        end_time = datetime.now()
        duration = (end_time - start_time).total_seconds()
        
        avg_loss = np.mean([u.loss for u in updates])
        avg_accuracy = np.mean([u.metrics['accuracy'] for u in updates])
        
        round_metadata = FederatedRound(
            round_id=self.current_round,
            timestamp=start_time.isoformat(),
            num_clients=len(participating_clients),
            global_model_version=f"v{self.current_round}.0.0",
            participating_clients=[c.config.client_id for c in participating_clients],
            aggregation_metrics={
                'avg_loss': float(avg_loss),
                'avg_accuracy': float(avg_accuracy),
                'total_samples': sum(u.num_samples for u in updates)
            },
            round_duration_seconds=duration
        )
        
        self.round_history.append(round_metadata)
        
        logger.info(f"📈 Round {self.current_round} Complete:")
        logger.info(f"   Clients: {len(participating_clients)}")
        logger.info(f"   Avg Loss: {avg_loss:.4f}")
        logger.info(f"   Avg Accuracy: {avg_accuracy:.4f}")
        logger.info(f"   Duration: {duration:.2f}s")
        
        return round_metadata
    
    def train(self, num_rounds: int = 10) -> List[FederatedRound]:
        """Run multiple federated learning rounds"""
        logger.info(f"🚀 Starting Federated Learning: {num_rounds} rounds")
        
        history = []
        for round_num in range(num_rounds):
            round_result = self.run_round()
            history.append(round_result)
        
        logger.info(f"\n{'='*70}")
        logger.info(f"✅ Federated Learning Complete!")
        logger.info(f"   Total rounds: {len(history)}")
        logger.info(f"   Final accuracy: {history[-1].aggregation_metrics['avg_accuracy']:.4f}")
        logger.info(f"{'='*70}")
        
        return history
    
    def export_history(self, filepath: str):
        """Export training history to JSON"""
        history_data = {
            'total_rounds': len(self.round_history),
            'final_accuracy': self.round_history[-1].aggregation_metrics['avg_accuracy'] if self.round_history else 0,
            'rounds': [
                {
                    'round_id': r.round_id,
                    'timestamp': r.timestamp,
                    'num_clients': r.num_clients,
                    'metrics': r.aggregation_metrics,
                    'duration': r.round_duration_seconds
                }
                for r in self.round_history
            ]
        }
        
        with open(filepath, 'w') as f:
            json.dump(history_data, f, indent=2)
        
        logger.info(f"💾 Exported history to {filepath}")


# Simple model for federated learning demo
class SimpleFederatedModel(nn.Module):
    def __init__(self, input_dim=50, hidden_dim=64, output_dim=1):
        super().__init__()
        self.network = nn.Sequential(
            nn.Linear(input_dim, hidden_dim),
            nn.ReLU(),
            nn.Linear(hidden_dim, hidden_dim // 2),
            nn.ReLU(),
            nn.Linear(hidden_dim // 2, output_dim),
            nn.Sigmoid()
        )
    
    def forward(self, x):
        return self.network(x)


def main():
    """Demo federated learning"""
    print("""
╔═══════════════════════════════════════════════════════════════╗
║     🧠 KALIAGENT v5.0.0 - FEDERATED LEARNING                 ║
║                    Phase 14: Alpha 0.1.0                      ║
╚═══════════════════════════════════════════════════════════════╝

Privacy-preserving distributed ML training
Clients train locally, only share model updates (gradients)

    """)
    
    if not TORCH_AVAILABLE:
        print("⚠️ PyTorch not available")
        return
    
    # Initialize coordinator with 5 clients
    print("🎛️ Initializing Federated Coordinator...")
    model = SimpleFederatedModel(input_dim=50, hidden_dim=64)
    coordinator = FederatedCoordinator(model, num_clients=5)
    
    # Run federated learning
    print("\n🚀 Starting Federated Learning...")
    history = coordinator.train(num_rounds=3)
    
    # Export history
    coordinator.export_history("./federated_history.json")
    
    # Show progress
    print("\n📈 Training Progress:")
    print(f"{'Round':<8} {'Clients':<10} {'Avg Loss':<12} {'Avg Accuracy':<15}")
    print("-" * 50)
    for round_result in history:
        print(f"{round_result.round_id:<8} {round_result.num_clients:<10} "
              f"{round_result.aggregation_metrics['avg_loss']:<12.4f} "
              f"{round_result.aggregation_metrics['avg_accuracy']:<15.4f}")
    
    print("\n" + "="*70)
    print("✅ Federated Learning demo complete!")
    print("="*70)


if __name__ == "__main__":
    main()
