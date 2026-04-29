#!/usr/bin/env python3
"""
🧠 KaliAgent v5.0.0 - Phase 14: Model Registry

Version control for ML models:
- Semantic versioning (v1.0.0, v1.1.0, v2.0.0)
- Training metadata tracking
- Model artifacts storage
- A/B testing framework
- Deployment management

Author: KaliAgent Team
Status: Alpha (0.1.0)
"""

import logging
import json
import hashlib
import shutil
from pathlib import Path
from typing import List, Dict, Optional, Any
from dataclasses import dataclass, field, asdict
from datetime import datetime
import uuid

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger('ModelRegistry')


@dataclass
class ModelVersion:
    """Model version metadata"""
    name: str
    version: str  # Semantic versioning: major.minor.patch
    created_at: str
    created_by: str
    
    # Model info
    model_type: str  # lstm, autoencoder, classifier, etc.
    framework: str  # pytorch, tensorflow, sklearn
    framework_version: str
    
    # Training metadata
    training_data_hash: Optional[str] = None
    training_samples: int = 0
    training_duration_seconds: float = 0.0
    training_metrics: Dict[str, float] = field(default_factory=dict)
    hyperparameters: Dict[str, Any] = field(default_factory=dict)
    
    # Performance
    evaluation_metrics: Dict[str, float] = field(default_factory=dict)
    benchmark_results: Dict[str, float] = field(default_factory=dict)
    
    # Deployment
    status: str = "development"  # development, staging, production, deprecated
    deployment_environment: Optional[str] = None
    deployed_at: Optional[str] = None
    
    # Artifacts
    model_path: Optional[str] = None
    model_size_bytes: int = 0
    model_hash: Optional[str] = None
    
    # Notes
    description: str = ""
    tags: List[str] = field(default_factory=list)
    parent_version: Optional[str] = None
    
    def to_dict(self) -> Dict:
        return asdict(self)
    
    def to_json(self) -> str:
        return json.dumps(self.to_dict(), indent=2)


@dataclass
class ABTestResult:
    """A/B test comparison result"""
    test_id: str
    timestamp: str
    control_model: str
    candidate_model: str
    
    # Metrics comparison
    metric_name: str
    control_score: float
    candidate_score: float
    improvement: float  # percentage
    
    # Statistical significance
    p_value: Optional[float] = None
    significant: bool = False
    
    # Decision
    recommendation: str = ""  # promote, reject, needs_more_data
    
    def to_dict(self) -> Dict:
        return asdict(self)


class ModelRegistry:
    """
    Registry for ML model versioning and management
    
    Features:
    - Semantic versioning
    - Metadata tracking
    - Artifact storage
    - A/B testing
    - Deployment management
    - Model comparison
    """
    
    VERSION = "0.1.0"
    
    def __init__(self, registry_path: str = None):
        self.registry_path = Path(registry_path or "./model_registry")
        self.models_path = self.registry_path / "models"
        self.metadata_path = self.registry_path / "metadata"
        
        # Create directories
        self.registry_path.mkdir(parents=True, exist_ok=True)
        self.models_path.mkdir(exist_ok=True)
        self.metadata_path.mkdir(exist_ok=True)
        
        # In-memory registry
        self.models: Dict[str, Dict[str, ModelVersion]] = {}  # {model_name: {version: metadata}}
        
        # Load existing registry
        self._load_registry()
        
        logger.info(f"🗃️ Model Registry v{self.VERSION}")
        logger.info(f"   Path: {self.registry_path.absolute()}")
        logger.info(f"   Models: {self._count_models()}")
    
    def _count_models(self) -> int:
        """Count total model versions"""
        return sum(len(versions) for versions in self.models.values())
    
    def _load_registry(self):
        """Load existing registry from disk"""
        if not self.metadata_path.exists():
            return
        
        for model_dir in self.metadata_path.iterdir():
            if model_dir.is_dir():
                model_name = model_dir.name
                self.models[model_name] = {}
                
                for version_file in model_dir.glob("*.json"):
                    version = version_file.stem
                    with open(version_file, 'r') as f:
                        metadata = json.load(f)
                        self.models[model_name][version] = ModelVersion(**metadata)
        
        logger.info(f"📂 Loaded {self._count_models()} model versions")
    
    def register(self, model_name: str, version: str, model_path: str = None,
                 model_type: str = None, framework: str = "pytorch",
                 training_metrics: Dict[str, float] = None,
                 evaluation_metrics: Dict[str, float] = None,
                 hyperparameters: Dict[str, Any] = None,
                 description: str = "", tags: List[str] = None,
                 parent_version: str = None, created_by: str = "system") -> ModelVersion:
        """
        Register a new model version
        
        Args:
            model_name: Model name (e.g., "lstm_anomaly_detector")
            version: Semantic version (e.g., "1.0.0")
            model_path: Path to model file
            model_type: Type of model (lstm, autoencoder, etc.)
            framework: ML framework (pytorch, tensorflow, sklearn)
            training_metrics: Training metrics (loss, accuracy, etc.)
            evaluation_metrics: Evaluation metrics (precision, recall, f1)
            hyperparameters: Model hyperparameters
            description: Model description
            tags: Tags for categorization
            parent_version: Parent version for lineage
            created_by: Who created this version
            
        Returns:
            ModelVersion metadata object
        """
        logger.info(f"📝 Registering {model_name} v{version}")
        
        # Initialize model namespace
        if model_name not in self.models:
            self.models[model_name] = {}
        
        # Calculate model hash if file exists
        model_hash = None
        model_size = 0
        saved_path = None
        
        if model_path and Path(model_path).exists():
            model_hash = self._hash_file(model_path)
            model_size = Path(model_path).stat().st_size
            
            # Copy model to registry
            saved_path = str(self.models_path / model_name / f"v{version}.pt")
            Path(self.models_path / model_name).mkdir(parents=True, exist_ok=True)
            shutil.copy2(model_path, saved_path)
            logger.info(f"💾 Model saved to {saved_path}")
        
        # Create metadata
        metadata = ModelVersion(
            name=model_name,
            version=version,
            created_at=datetime.now().isoformat(),
            created_by=created_by,
            model_type=model_type or "unknown",
            framework=framework,
            framework_version=self._get_framework_version(framework),
            training_data_hash=None,
            training_metrics=training_metrics or {},
            evaluation_metrics=evaluation_metrics or {},
            hyperparameters=hyperparameters or {},
            model_path=saved_path,
            model_size_bytes=model_size,
            model_hash=model_hash,
            description=description,
            tags=tags or [],
            parent_version=parent_version
        )
        
        # Save metadata
        self.models[model_name][version] = metadata
        self._save_metadata(metadata)
        
        logger.info(f"✅ Registered {model_name} v{version}")
        logger.info(f"   Type: {metadata.model_type}")
        logger.info(f"   Size: {model_size / 1024 / 1024:.2f} MB")
        logger.info(f"   Metrics: {len(training_metrics or {})} training, {len(evaluation_metrics or {})} evaluation")
        
        return metadata
    
    def _hash_file(self, filepath: str) -> str:
        """Calculate SHA256 hash of file"""
        sha256 = hashlib.sha256()
        with open(filepath, 'rb') as f:
            for chunk in iter(lambda: f.read(8192), b''):
                sha256.update(chunk)
        return sha256.hexdigest()
    
    def _get_framework_version(self, framework: str) -> str:
        """Get framework version"""
        try:
            if framework == "pytorch":
                import torch
                return torch.__version__
            elif framework == "tensorflow":
                import tensorflow as tf
                return tf.__version__
            elif framework == "sklearn":
                import sklearn
                return sklearn.__version__
        except ImportError:
            return "unknown"
        return "unknown"
    
    def _save_metadata(self, metadata: ModelVersion):
        """Save model metadata to disk"""
        model_dir = self.metadata_path / metadata.name
        model_dir.mkdir(parents=True, exist_ok=True)
        
        version_file = model_dir / f"v{metadata.version}.json"
        with open(version_file, 'w') as f:
            f.write(metadata.to_json())
    
    def get(self, model_name: str, version: str = None) -> Optional[ModelVersion]:
        """
        Get model metadata
        
        Args:
            model_name: Model name
            version: Specific version (optional, returns latest if None)
            
        Returns:
            ModelVersion or None
        """
        if model_name not in self.models:
            return None
        
        if version is None:
            # Return latest version
            versions = sorted(self.models[model_name].keys())
            if versions:
                version = versions[-1]
            else:
                return None
        
        return self.models[model_name].get(version)
    
    def list_models(self) -> List[str]:
        """List all registered model names"""
        return list(self.models.keys())
    
    def list_versions(self, model_name: str) -> List[str]:
        """List all versions of a model"""
        if model_name not in self.models:
            return []
        return sorted(self.models[model_name].keys())
    
    def deploy(self, model_name: str, version: str, environment: str = "production") -> bool:
        """
        Deploy model to environment
        
        Args:
            model_name: Model name
            version: Version to deploy
            environment: deployment environment (staging, production)
            
        Returns:
            True if successful
        """
        metadata = self.get(model_name, version)
        if not metadata:
            logger.error(f"❌ Model {model_name} v{version} not found")
            return False
        
        # Update metadata
        metadata.status = "production" if environment == "production" else "staging"
        metadata.deployment_environment = environment
        metadata.deployed_at = datetime.now().isoformat()
        
        # Save updated metadata
        self._save_metadata(metadata)
        
        logger.info(f"🚀 Deployed {model_name} v{version} to {environment}")
        return True
    
    def deprecate(self, model_name: str, version: str) -> bool:
        """Deprecate a model version"""
        metadata = self.get(model_name, version)
        if not metadata:
            logger.error(f"❌ Model {model_name} v{version} not found")
            return False
        
        metadata.status = "deprecated"
        self._save_metadata(metadata)
        
        logger.info(f"⚠️  Deprecated {model_name} v{version}")
        return True
    
    def ab_test(self, control_model: str, control_version: str,
                candidate_model: str, candidate_version: str,
                metric_name: str, control_score: float,
                candidate_score: float,
                p_value: float = None,
                threshold: float = 0.05) -> ABTestResult:
        """
        Compare two model versions (A/B test)
        
        Args:
            control_model: Control model name
            control_version: Control version
            candidate_model: Candidate model name
            candidate_version: Candidate version
            metric_name: Metric to compare (accuracy, f1, etc.)
            control_score: Control model score
            candidate_score: Candidate model score
            p_value: Statistical significance (optional)
            threshold: Significance threshold (default 0.05)
            
        Returns:
            ABTestResult with comparison and recommendation
        """
        improvement = ((candidate_score - control_score) / control_score) * 100
        
        # Determine significance
        significant = False
        if p_value is not None:
            significant = p_value < threshold
        
        # Make recommendation
        if improvement > 5 and (significant or p_value is None):
            recommendation = "promote"
        elif improvement < -5:
            recommendation = "reject"
        else:
            recommendation = "needs_more_data"
        
        result = ABTestResult(
            test_id=str(uuid.uuid4())[:8],
            timestamp=datetime.now().isoformat(),
            control_model=f"{control_model}:{control_version}",
            candidate_model=f"{candidate_model}:{candidate_version}",
            metric_name=metric_name,
            control_score=control_score,
            candidate_score=candidate_score,
            improvement=improvement,
            p_value=p_value,
            significant=significant,
            recommendation=recommendation
        )
        
        logger.info(f"📊 A/B Test: {result.test_id}")
        logger.info(f"   Control: {result.control_model} = {control_score:.4f}")
        logger.info(f"   Candidate: {result.candidate_model} = {candidate_score:.4f}")
        logger.info(f"   Improvement: {improvement:+.2f}%")
        logger.info(f"   Recommendation: {recommendation}")
        
        return result
    
    def compare_versions(self, model_name: str, version1: str, 
                        version2: str, metric: str = None) -> Dict:
        """
        Compare two versions of the same model
        
        Args:
            model_name: Model name
            version1: First version
            version2: Second version
            metric: Specific metric to compare (optional)
            
        Returns:
            Comparison dictionary
        """
        v1 = self.get(model_name, version1)
        v2 = self.get(model_name, version2)
        
        if not v1 or not v2:
            return {"error": "Version not found"}
        
        comparison = {
            "model": model_name,
            "version1": version1,
            "version2": version2,
            "metrics": {}
        }
        
        # Compare evaluation metrics
        all_metrics = set(v1.evaluation_metrics.keys()) | set(v2.evaluation_metrics.keys())
        
        for metric_name in all_metrics:
            if metric and metric_name != metric:
                continue
            
            score1 = v1.evaluation_metrics.get(metric_name, 0)
            score2 = v2.evaluation_metrics.get(metric_name, 0)
            improvement = ((score2 - score1) / max(score1, 1e-8)) * 100
            
            comparison["metrics"][metric_name] = {
                "version1": score1,
                "version2": score2,
                "improvement": improvement
            }
        
        return comparison
    
    def export_registry(self, filepath: str):
        """Export entire registry to JSON"""
        export_data = {
            "exported_at": datetime.now().isoformat(),
            "total_models": len(self.models),
            "total_versions": self._count_models(),
            "models": {}
        }
        
        for model_name, versions in self.models.items():
            export_data["models"][model_name] = {
                version: metadata.to_dict()
                for version, metadata in versions.items()
            }
        
        with open(filepath, 'w') as f:
            json.dump(export_data, f, indent=2)
        
        logger.info(f"💾 Exported registry to {filepath}")


def main():
    """Demo model registry"""
    print("""
╔═══════════════════════════════════════════════════════════════╗
║     🧠 KALIAGENT v5.0.0 - MODEL REGISTRY                     ║
║                    Phase 14: Alpha 0.1.0                      ║
╚═══════════════════════════════════════════════════════════════╝

    """)
    
    # Initialize registry
    registry = ModelRegistry("./demo_registry")
    
    # Register models
    print("\n📝 Registering models...")
    
    v1 = registry.register(
        model_name="lstm_anomaly_detector",
        version="1.0.0",
        model_type="lstm",
        training_metrics={"loss": 0.05, "accuracy": 0.95},
        evaluation_metrics={"precision": 0.98, "recall": 0.92, "f1": 0.95},
        hyperparameters={"hidden_size": 128, "layers": 2, "dropout": 0.2},
        description="LSTM anomaly detector v1.0",
        tags=["anomaly", "lstm", "production"]
    )
    
    v2 = registry.register(
        model_name="lstm_anomaly_detector",
        version="1.1.0",
        model_type="lstm",
        training_metrics={"loss": 0.03, "accuracy": 0.97},
        evaluation_metrics={"precision": 0.99, "recall": 0.94, "f1": 0.96},
        hyperparameters={"hidden_size": 256, "layers": 3, "dropout": 0.15},
        description="LSTM anomaly detector v1.1 - improved architecture",
        tags=["anomaly", "lstm", "staging"],
        parent_version="1.0.0"
    )
    
    # List models
    print(f"\n📂 Registered models: {registry.list_models()}")
    print(f"   Versions: {registry.list_versions('lstm_anomaly_detector')}")
    
    # Deploy
    print("\n🚀 Deploying model...")
    registry.deploy("lstm_anomaly_detector", "1.0.0", "production")
    registry.deploy("lstm_anomaly_detector", "1.1.0", "staging")
    
    # A/B test
    print("\n📊 Running A/B test...")
    ab_result = registry.ab_test(
        control_model="lstm_anomaly_detector",
        control_version="1.0.0",
        candidate_model="lstm_anomaly_detector",
        candidate_version="1.1.0",
        metric_name="f1",
        control_score=0.95,
        candidate_score=0.96,
        p_value=0.03
    )
    
    print(f"   Recommendation: {ab_result.recommendation}")
    
    # Compare versions
    print("\n📈 Comparing versions...")
    comparison = registry.compare_versions(
        "lstm_anomaly_detector", "1.0.0", "1.1.0"
    )
    
    for metric, scores in comparison.get("metrics", {}).items():
        print(f"   {metric}: {scores['version1']:.4f} → {scores['version2']:.4f} ({scores['improvement']:+.1f}%)")
    
    # Export
    print("\n💾 Exporting registry...")
    registry.export_registry("./demo_registry_export.json")
    
    print("\n" + "="*70)
    print("✅ Model Registry demo complete!")
    print("="*70)


if __name__ == "__main__":
    main()
