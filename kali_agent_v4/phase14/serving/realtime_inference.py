#!/usr/bin/env python3
"""
🧠 KaliAgent v5.0.0 - Phase 14 Sprint 1.2: Real-Time Inference Engine

High-performance real-time inference:
- Streaming data support
- Low-latency predictions
- Batch optimization
- GPU acceleration
- Async processing

Author: KaliAgent Team
Status: Alpha (0.1.0)
"""

import logging
import numpy as np
from typing import List, Dict, Optional, Callable, Any
from dataclasses import dataclass, field
from datetime import datetime
from collections import deque
import time
import threading

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger('RealTimeInference')

try:
    import torch
    TORCH_AVAILABLE = True
except ImportError:
    TORCH_AVAILABLE = False
    logger.warning("⚠️ PyTorch not available")


@dataclass
class InferenceConfig:
    """Real-time inference configuration"""
    batch_size: int = 32
    max_latency_ms: float = 50.0
    gpu_acceleration: bool = True
    async_processing: bool = True
    cache_predictions: bool = True
    cache_ttl_seconds: int = 300
    max_queue_size: int = 1000


@dataclass
class InferenceResult:
    """Real-time inference result"""
    id: str
    timestamp: str
    input_hash: str
    prediction: Any
    confidence: float
    latency_ms: float
    gpu_used: bool
    cached: bool = False


class RealTimeInferenceEngine:
    """
    Real-Time Inference Engine
    
    Features:
    - Streaming data support
    - Low-latency predictions (<50ms target)
    - GPU batch optimization
    - Async processing queue
    - Prediction caching
    """
    
    VERSION = "0.1.0"
    
    def __init__(self, config: InferenceConfig = None):
        self.config = config or InferenceConfig()
        
        # Device
        self.device = None
        if TORCH_AVAILABLE and self.config.gpu_acceleration:
            self.device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
            logger.info(f"🔧 Device: {self.device}")
        
        # Queue for async processing
        self.queue = deque(maxlen=self.config.max_queue_size)
        self.results_cache: Dict[str, InferenceResult] = {}
        
        # Metrics
        self.total_inferences = 0
        self.cache_hits = 0
        self.latencies: List[float] = []
        
        # Lock for thread safety
        self.lock = threading.Lock()
        
        logger.info(f"⚡ Real-Time Inference Engine v{self.VERSION}")
        logger.info(f"   Batch size: {self.config.batch_size}")
        logger.info(f"   Max latency: {self.config.max_latency_ms}ms")
        logger.info(f"   Queue size: {self.config.max_queue_size}")
    
    def add_to_queue(self, data: np.ndarray, callback: Callable = None):
        """Add data to inference queue"""
        with self.lock:
            self.queue.append({
                'data': data,
                'callback': callback,
                'timestamp': time.time()
            })
        
        logger.debug(f"📥 Added to queue (size: {len(self.queue)})")
    
    def process_queue(self, model: Any) -> List[InferenceResult]:
        """Process queue in batches"""
        if not self.queue:
            return []
        
        start_time = time.time()
        results = []
        
        # Collect batch
        batch = []
        batch_data = []
        
        while len(batch) < self.config.batch_size and self.queue:
            item = self.queue.popleft()
            batch.append(item)
            batch_data.append(item['data'])
        
        if not batch_data:
            return []
        
        # Convert to tensor
        batch_tensor = torch.FloatTensor(np.array(batch_data))
        
        if self.device and TORCH_AVAILABLE:
            batch_tensor = batch_tensor.to(self.device)
        
        # Run inference
        with torch.no_grad():
            if hasattr(model, 'model') and hasattr(model.model, 'eval'):
                model.model.eval()
                predictions = model.model(batch_tensor)
            else:
                predictions = model(batch_tensor)
            
            if TORCH_AVAILABLE:
                predictions = predictions.cpu().numpy()
        
        # Create results
        processing_time = (time.time() - start_time) * 1000
        
        for i, item in enumerate(batch):
            result = InferenceResult(
                id=f"inf_{int(time.time() * 1000)}_{i}",
                timestamp=datetime.now().isoformat(),
                input_hash=hash(item['data'].tobytes()),
                prediction=predictions[i].tolist() if hasattr(predictions[i], 'tolist') else predictions[i],
                confidence=float(np.max(predictions[i])),
                latency_ms=processing_time / len(batch),
                gpu_used=self.device is not None and str(self.device) == 'cuda',
                cached=False
            )
            
            results.append(result)
            self.total_inferences += 1
            self.latencies.append(result.latency_ms)
            
            # Cache result
            if self.config.cache_predictions:
                self.results_cache[result.input_hash] = result
            
            # Call callback if provided
            if item['callback']:
                item['callback'](result)
        
        logger.debug(f"✅ Processed batch of {len(batch)} (avg latency: {processing_time/len(batch):.2f}ms)")
        
        return results
    
    def infer(self, data: np.ndarray, model: Any) -> InferenceResult:
        """
        Single inference with caching
        
        Args:
            data: Input data
            model: ML model
            
        Returns:
            InferenceResult
        """
        start_time = time.time()
        
        # Check cache
        input_hash = hash(data.tobytes())
        if self.config.cache_predictions and input_hash in self.results_cache:
            cached_result = self.results_cache[input_hash]
            
            # Check TTL
            cache_age = time.time() - float(cached_result.timestamp)
            if cache_age < self.config.cache_ttl_seconds:
                self.cache_hits += 1
                logger.debug("♻️ Cache hit")
                return cached_result
        
        # Run inference
        tensor = torch.FloatTensor(data)
        
        if self.device and TORCH_AVAILABLE:
            tensor = tensor.to(self.device)
        
        with torch.no_grad():
            if hasattr(model, 'model') and hasattr(model.model, 'eval'):
                model.model.eval()
                prediction = model.model(tensor)
            else:
                prediction = model(tensor)
            
            if TORCH_AVAILABLE:
                prediction = prediction.cpu().numpy()
        
        processing_time = (time.time() - start_time) * 1000
        
        result = InferenceResult(
            id=f"inf_{int(time.time() * 1000)}",
            timestamp=datetime.now().isoformat(),
            input_hash=input_hash,
            prediction=prediction.tolist() if hasattr(prediction, 'tolist') else prediction,
            confidence=float(np.max(prediction)),
            latency_ms=processing_time,
            gpu_used=self.device is not None and str(self.device) == 'cuda',
            cached=False
        )
        
        # Cache result
        if self.config.cache_predictions:
            self.results_cache[input_hash] = result
        
        self.total_inferences += 1
        self.latencies.append(processing_time)
        
        logger.debug(f"⚡ Inference complete ({processing_time:.2f}ms)")
        
        return result
    
    def get_metrics(self) -> Dict:
        """Get inference metrics"""
        avg_latency = sum(self.latencies) / len(self.latencies) if self.latencies else 0
        p99_latency = sorted(self.latencies)[int(len(self.latencies) * 0.99)] if len(self.latencies) > 100 else avg_latency
        
        return {
            'total_inferences': self.total_inferences,
            'cache_hits': self.cache_hits,
            'cache_hit_rate': self.cache_hits / max(self.total_inferences, 1),
            'avg_latency_ms': avg_latency,
            'p99_latency_ms': p99_latency,
            'queue_size': len(self.queue),
            'gpu_acceleration': str(self.device) == 'cuda' if self.device else False
        }
    
    def clear_cache(self):
        """Clear prediction cache"""
        with self.lock:
            self.results_cache.clear()
        logger.info("🗑️ Cache cleared")


def demo():
    """Demo real-time inference"""
    print("""
╔═══════════════════════════════════════════════════════════════╗
║     🧠 KALIAGENT v5.0.0 - REAL-TIME INFERENCE ENGINE         ║
╚═══════════════════════════════════════════════════════════════╝

    """)
    
    if not TORCH_AVAILABLE:
        print("⚠️ PyTorch not available")
        return
    
    # Simple model for demo
    class DummyModel(torch.nn.Module):
        def __init__(self):
            super().__init__()
            self.linear = torch.nn.Linear(10, 1)
        
        def forward(self, x):
            return torch.sigmoid(self.linear(x))
    
    model = DummyModel()
    
    # Initialize engine
    config = InferenceConfig(batch_size=16, gpu_acceleration=True)
    engine = RealTimeInferenceEngine(config)
    
    # Single inference
    print("\n⚡ Testing single inference...")
    data = np.random.randn(10).astype(np.float32)
    result = engine.infer(data, model)
    
    print(f"   Prediction: {result.prediction}")
    print(f"   Confidence: {result.confidence:.4f}")
    print(f"   Latency: {result.latency_ms:.2f}ms")
    print(f"   GPU Used: {result.gpu_used}")
    
    # Batch processing
    print("\n📦 Testing batch processing...")
    for i in range(20):
        data = np.random.randn(10).astype(np.float32)
        engine.add_to_queue(data)
    
    results = engine.process_queue(model)
    print(f"   Processed: {len(results)} items")
    print(f"   Avg latency: {sum(r.latency_ms for r in results) / len(results):.2f}ms")
    
    # Metrics
    print("\n📊 Metrics:")
    metrics = engine.get_metrics()
    for key, value in metrics.items():
        print(f"   {key}: {value}")
    
    print("\n" + "="*70)
    print("✅ Real-Time Inference demo complete!")
    print("="*70)


if __name__ == "__main__":
    demo()
