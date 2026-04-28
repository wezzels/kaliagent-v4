#!/usr/bin/env python3
"""
🧠 KaliAgent v4.5.0 - Phase 13: AI/ML Threat Intelligence & Predictive Analytics
Isolation Forest Anomaly Detection

Isolation Forest implementation for security anomaly detection:
- Unsupervised anomaly detection
- Multi-feature analysis
- Contamination-based thresholding
- Anomaly score calculation
- Feature importance analysis

Author: KaliAgent Team
Started: April 28, 2026
Status: Alpha (0.1.0)
"""

import logging
import random
import math
from typing import List, Dict, Optional, Tuple
from datetime import datetime
from dataclasses import dataclass, field
import uuid

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger('IsolationForest')


@dataclass
class IsolationTree:
    """Isolation Tree node"""
    feature: str = ""
    threshold: float = 0.0
    left: Optional['IsolationTree'] = None
    right: Optional['IsolationTree'] = None
    size: int = 0
    is_leaf: bool = False


@dataclass
class IFAnomaly:
    """Isolation Forest anomaly result"""
    id: str
    source: str
    features: Dict[str, float]
    anomaly_score: float
    is_anomaly: bool
    path_length: float
    num_trees: int
    timestamp: datetime = field(default_factory=datetime.now)
    feature_contributions: Dict[str, float] = field(default_factory=dict)
    
    def to_dict(self) -> Dict:
        return {
            'id': self.id,
            'source': self.source,
            'features': self.features,
            'anomaly_score': self.anomaly_score,
            'is_anomaly': self.is_anomaly,
            'path_length': self.path_length,
            'num_trees': self.num_trees,
            'timestamp': self.timestamp.isoformat(),
            'feature_contributions': self.feature_contributions
        }


class IsolationForest:
    """
    Isolation Forest Anomaly Detection
    
    A machine learning algorithm that isolates anomalies instead of
    profiling normal points. Anomalies are few and different, making
    them easier to isolate.
    
    Capabilities:
    - Unsupervised anomaly detection
    - Multi-feature analysis
    - Contamination-based thresholding
    - Anomaly score calculation
    - Feature importance analysis
    """
    
    VERSION = "0.1.0"
    
    def __init__(self, n_trees: int = 100, contamination: float = 0.1,
                 max_samples: int = 256, random_state: int = None):
        """
        Initialize Isolation Forest
        
        Args:
            n_trees: Number of isolation trees
            contamination: Expected proportion of anomalies (0-0.5)
            max_samples: Max samples per tree
            random_state: Random seed for reproducibility
        """
        self.n_trees = n_trees
        self.contamination = contamination
        self.max_samples = max_samples
        self.random_state = random_state or random.randint(0, 1000)
        
        self.trees: List[IsolationTree] = []
        self.training_data: List[Dict[str, float]] = []
        self.feature_names: List[str] = []
        self.anomalies: List[IFAnomaly] = []
        
        # Threshold for anomaly classification
        self.threshold = self._calculate_threshold()
        
        if random_state:
            random.seed(random_state)
        
        logger.info(f"🌲 Isolation Forest v{self.VERSION}")
        logger.info(f"   Number of trees: {n_trees}")
        logger.info(f"   Contamination: {contamination}")
        logger.info(f"   Max samples: {max_samples}")
        logger.info(f"   Anomaly threshold: {self.threshold:.3f}")
    
    def _calculate_threshold(self) -> float:
        """Calculate anomaly threshold based on contamination"""
        # Threshold derived from contamination parameter
        # Higher contamination = lower threshold
        return 0.5 + (0.5 * (1 - self.contamination * 2))
    
    def fit(self, data: List[Dict[str, float]], feature_names: List[str] = None) -> 'IsolationForest':
        """
        Fit isolation forest to training data
        
        Args:
            data: List of feature dictionaries
            feature_names: Optional feature name list
            
        Returns:
            self
        """
        logger.info(f"🌲 Fitting Isolation Forest with {len(data)} samples...")
        
        if not data:
            logger.error("No training data provided")
            return self
        
        self.training_data = data
        self.feature_names = feature_names or list(data[0].keys())
        self.trees = []
        
        # Build isolation trees
        for i in range(self.n_trees):
            # Subsample data
            sample_size = min(self.max_samples, len(data))
            sample = random.sample(data, sample_size)
            
            # Build tree
            tree = self._build_tree(sample, 0)
            self.trees.append(tree)
        
        logger.info(f"   Built {len(self.trees)} trees")
        logger.info(f"   Features: {self.feature_names}")
        
        return self
    
    def _build_tree(self, data: List[Dict[str, float]], depth: int,
                   max_depth: int = None) -> IsolationTree:
        """Build isolation tree recursively"""
        if max_depth is None:
            max_depth = int(math.ceil(math.log2(self.max_samples)))
        
        # Leaf node conditions
        if len(data) <= 1 or depth >= max_depth:
            return IsolationTree(size=len(data), is_leaf=True)
        
        # Random feature selection
        feature = random.choice(self.feature_names)
        
        # Get feature values
        values = [point[feature] for point in data]
        min_val, max_val = min(values), max(values)
        
        # Handle constant feature
        if min_val == max_val:
            return IsolationTree(size=len(data), is_leaf=True)
        
        # Random threshold selection
        threshold = random.uniform(min_val, max_val)
        
        # Split data
        left_data = [p for p in data if p[feature] < threshold]
        right_data = [p for p in data if p[feature] >= threshold]
        
        # Build subtrees
        left = self._build_tree(left_data, depth + 1, max_depth)
        right = self._build_tree(right_data, depth + 1, max_depth)
        
        return IsolationTree(
            feature=feature,
            threshold=threshold,
            left=left,
            right=right,
            size=len(data)
        )
    
    def _path_length(self, point: Dict[str, float], tree: IsolationTree,
                    depth: int = 0) -> float:
        """Calculate path length for a point in a tree"""
        if tree.is_leaf:
            # Adjustment for unseen data
            return depth + self._c(tree.size)
        
        # Traverse tree
        if point.get(tree.feature, 0) < tree.threshold:
            return self._path_length(point, tree.left, depth + 1)
        else:
            return self._path_length(point, tree.right, depth + 1)
    
    def _c(self, n: int) -> float:
        """Average path length of unsuccessful search in BST"""
        if n <= 1:
            return 0
        elif n == 2:
            return 1
        else:
            return 2.0 * (math.log(n - 1) + 0.5772156649) - (2.0 * (n - 1) / n)
    
    def predict(self, point: Dict[str, float], source: str = "") -> IFAnomaly:
        """
        Predict if point is anomaly
        
        Args:
            point: Feature dictionary
            source: Data source identifier
            
        Returns:
            Anomaly result
        """
        if not self.trees:
            logger.error("Model not fitted. Call fit() first.")
            return None
        
        # Calculate average path length across all trees
        path_lengths = [self._path_length(point, tree) for tree in self.trees]
        avg_path_length = sum(path_lengths) / len(path_lengths)
        
        # Calculate anomaly score
        # Score = 2^(-avg_path_length / c(n))
        c_n = self._c(self.max_samples)
        anomaly_score = 2 ** (-avg_path_length / c_n) if c_n > 0 else 0.5
        
        # Determine if anomaly
        is_anomaly = anomaly_score >= self.threshold
        
        # Calculate feature contributions (simplified)
        feature_contributions = self._calculate_feature_contributions(point)
        
        anomaly = IFAnomaly(
            id=str(uuid.uuid4())[:8],
            source=source,
            features=point,
            anomaly_score=round(anomaly_score, 4),
            is_anomaly=is_anomaly,
            path_length=round(avg_path_length, 2),
            num_trees=len(self.trees),
            feature_contributions=feature_contributions
        )
        
        if is_anomaly:
            self.anomalies.append(anomaly)
            logger.warning(f"⚠️  Anomaly detected: {anomaly.id}")
            logger.warning(f"   Score: {anomaly_score:.4f} (threshold: {self.threshold:.3f})")
            logger.warning(f"   Path length: {avg_path_length:.2f}")
        
        return anomaly
    
    def _calculate_feature_contributions(self, point: Dict[str, float]) -> Dict[str, float]:
        """Calculate feature contributions to anomaly score"""
        contributions = {}
        
        if not self.training_data:
            return contributions
        
        # Calculate how much each feature deviates from mean
        for feature in self.feature_names:
            if feature not in point:
                continue
            
            values = [p.get(feature, 0) for p in self.training_data]
            mean = sum(values) / len(values)
            stdev = math.sqrt(sum((v - mean) ** 2 for v in values) / len(values)) if len(values) > 1 else 1
            
            if stdev > 0:
                z_score = abs(point[feature] - mean) / stdev
                contributions[feature] = round(z_score, 2)
        
        return contributions
    
    def predict_batch(self, points: List[Dict[str, float]],
                     source: str = "") -> List[IFAnomaly]:
        """
        Predict anomalies for batch of points
        
        Args:
            points: List of feature dictionaries
            source: Data source identifier
            
        Returns:
            List of anomaly results
        """
        results = []
        for point in points:
            result = self.predict(point, source)
            if result:
                results.append(result)
        
        anomalies = sum(1 for r in results if r.is_anomaly)
        logger.info(f"   Batch results: {anomalies}/{len(results)} anomalies")
        
        return results
    
    def get_anomaly_summary(self) -> Dict:
        """Get anomaly summary"""
        if not self.anomalies:
            return {
                'total_anomalies': 0,
                'anomaly_rate': 0.0,
                'avg_score': 0.0,
                'max_score': 0.0
            }
        
        scores = [a.anomaly_score for a in self.anomalies]
        
        return {
            'total_anomalies': len(self.anomalies),
            'total_predictions': len(self.training_data) + len(self.anomalies),
            'anomaly_rate': len(self.anomalies) / (len(self.training_data) + len(self.anomalies)),
            'avg_score': sum(scores) / len(scores),
            'max_score': max(scores),
            'min_score': min(scores),
            'threshold': self.threshold
        }
    
    def set_threshold(self, threshold: float) -> None:
        """
        Set custom anomaly threshold
        
        Args:
            threshold: New threshold (0-1)
        """
        if 0 <= threshold <= 1:
            self.threshold = threshold
            logger.info(f"   Threshold updated: {threshold:.3f}")
        else:
            logger.error("Threshold must be between 0 and 1")
    
    def generate_report(self) -> str:
        """Generate Isolation Forest report"""
        summary = self.get_anomaly_summary()
        
        report = []
        report.append("=" * 70)
        report.append("🌲 ISOLATION FOREST REPORT")
        report.append("=" * 70)
        report.append(f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        report.append("")
        report.append(f"Model Configuration:")
        report.append(f"  Trees: {self.n_trees}")
        report.append(f"  Max Samples: {self.max_samples}")
        report.append(f"  Contamination: {self.contamination}")
        report.append(f"  Threshold: {self.threshold:.3f}")
        report.append("")
        report.append(f"Features: {', '.join(self.feature_names)}")
        report.append("")
        report.append(f"Results:")
        report.append(f"  Total Anomalies: {summary['total_anomalies']}")
        report.append(f"  Anomaly Rate: {summary['anomaly_rate']:.2%}")
        report.append(f"  Avg Anomaly Score: {summary['avg_score']:.4f}")
        report.append(f"  Max Anomaly Score: {summary['max_score']:.4f}")
        report.append("")
        
        if self.anomalies:
            report.append("TOP ANOMALIES:")
            report.append("-" * 70)
            sorted_anomalies = sorted(self.anomalies, key=lambda a: a.anomaly_score, reverse=True)[:10]
            
            for anomaly in sorted_anomalies:
                report.append(f"\n  ⚠️  [{anomaly.anomaly_score:.4f}] {anomaly.id}")
                report.append(f"     Source: {anomaly.source}")
                report.append(f"     Path Length: {anomaly.path_length:.2f}")
                
                if anomaly.feature_contributions:
                    top_features = sorted(anomaly.feature_contributions.items(),
                                        key=lambda x: x[1], reverse=True)[:3]
                    report.append(f"     Top Features:")
                    for feature, contribution in top_features:
                        report.append(f"       - {feature}: {contribution:.2f}σ")
        
        report.append("")
        report.append("=" * 70)
        
        return "\n".join(report)


def main():
    """Main entry point"""
    print("""
╔═══════════════════════════════════════════════════════════════╗
║     🌲 ISOLATION FOREST ANOMALY DETECTION                    ║
║                    Phase 13: Alpha 0.1.0                      ║
╚═══════════════════════════════════════════════════════════════╝

Unsupervised ML anomaly detection for security operations.

    """)
    
    # Create and fit model
    forest = IsolationForest(n_trees=100, contamination=0.1)
    
    # Generate training data (normal behavior)
    import random
    training_data = []
    for _ in range(500):
        training_data.append({
            'login_count': random.gauss(10, 2),
            'data_transfer_mb': random.gauss(50, 15),
            'failed_logins': random.gauss(1, 0.5),
            'session_duration_min': random.gauss(480, 60),
            'privilege_escalations': random.gauss(0, 0.2)
        })
    
    # Fit model
    forest.fit(training_data)
    
    # Test with normal data
    normal_point = {
        'login_count': 11,
        'data_transfer_mb': 55,
        'failed_logins': 1,
        'session_duration_min': 470,
        'privilege_escalations': 0
    }
    
    result = forest.predict(normal_point, 'user:normal')
    print(f"\nNormal point score: {result.anomaly_score:.4f} (anomaly: {result.is_anomaly})")
    
    # Test with anomalous data
    anomaly_point = {
        'login_count': 50,  # 20σ deviation
        'data_transfer_mb': 2000,  # 130σ deviation
        'failed_logins': 15,  # 28σ deviation
        'session_duration_min': 50,  # 7σ deviation
        'privilege_escalations': 10  # 50σ deviation
    }
    
    result = forest.predict(anomaly_point, 'user:suspicious')
    print(f"Anomaly point score: {result.anomaly_score:.4f} (anomaly: {result.is_anomaly})")
    
    # Generate report
    print("\n" + forest.generate_report())


if __name__ == "__main__":
    main()
