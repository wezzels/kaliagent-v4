#!/usr/bin/env python3
"""
🧠 KaliAgent v5.0.0 - Phase 14: ML Orchestrator

Unified ML pipeline integrating all Phase 14 modules with Phase 11-13:
- LSTM → Phase 11 (Threat Hunting)
- Autoencoder → Phase 13 (Anomaly Detection)
- NLP → Threat Intel pipeline
- Model Registry → Version management
- Federated Learning → Privacy-preserving training

Author: KaliAgent Team
Status: Alpha (0.1.0)
"""

import logging
from typing import List, Dict, Optional, Any
from dataclasses import dataclass, field
from datetime import datetime
import json
import sys
from pathlib import Path

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger('MLOrchestrator')

# Import Phase 14 modules
try:
    sys.path.insert(0, str(Path(__file__).parent))
    from deep_learning.lstm_network import LSTMSecurityDetector, LSTMConfig
    from deep_learning.autoencoder import AutoencoderDetector, AEConfig
    from nlp.threat_intel_extractor import ThreatIntelExtractor
    from nlp.threat_classifier import ThreatClassifier
    from model_registry.model_registry import ModelRegistry
    TORCH_AVAILABLE = True
except ImportError as e:
    logger.warning(f"⚠️  Could not import ML modules: {e}")
    TORCH_AVAILABLE = False


@dataclass
class MLAnalysisResult:
    """Unified ML analysis result"""
    id: str
    timestamp: str
    input_data: Dict[str, Any]
    
    # LSTM results (time-series)
    lstm_anomaly_score: Optional[float] = None
    lstm_is_anomaly: bool = False
    
    # Autoencoder results (novelty detection)
    autoencoder_error: Optional[float] = None
    autoencoder_is_novel: bool = False
    
    # NLP results (text analysis)
    nlp_iocs: Dict[str, Any] = field(default_factory=dict)
    nlp_classification: Dict[str, Any] = field(default_factory=dict)
    
    # Unified threat score
    threat_score: float = 0.0
    threat_level: str = "low"  # low, medium, high, critical
    
    # Recommendations
    recommendations: List[str] = field(default_factory=list)
    
    def to_dict(self) -> Dict:
        return {
            'id': self.id,
            'timestamp': self.timestamp,
            'lstm': {
                'anomaly_score': self.lstm_anomaly_score,
                'is_anomaly': self.lstm_is_anomaly
            },
            'autoencoder': {
                'reconstruction_error': self.autoencoder_error,
                'is_novel': self.autoencoder_is_novel
            },
            'nlp': {
                'iocs': self.nlp_iocs,
                'classification': self.nlp_classification
            },
            'threat_assessment': {
                'score': self.threat_score,
                'level': self.threat_level,
                'recommendations': self.recommendations
            }
        }


class MLOrchestrator:
    """
    Unified ML orchestrator for KaliAgent
    
    Integrates:
    - Phase 14 ML modules (LSTM, Autoencoder, NLP)
    - Phase 11 Threat Hunting
    - Phase 13 Threat Intelligence
    - Model Registry for versioning
    """
    
    VERSION = "0.1.0"
    
    def __init__(self, registry_path: str = None):
        self.registry = None
        self.lstm_detector = None
        self.autoencoder_detector = None
        self.nlp_extractor = None
        self.nlp_classifier = None
        
        # Initialize components
        if TORCH_AVAILABLE:
            self._initialize_components(registry_path)
        
        logger.info(f"🎯 ML Orchestrator v{self.VERSION}")
        logger.info(f"   Components: {self._count_components()} initialized")
    
    def _count_components(self) -> int:
        """Count initialized components"""
        count = 0
        if self.lstm_detector: count += 1
        if self.autoencoder_detector: count += 1
        if self.nlp_extractor: count += 1
        if self.nlp_classifier: count += 1
        if self.registry: count += 1
        return count
    
    def _initialize_components(self, registry_path: str = None):
        """Initialize all ML components"""
        logger.info("🔧 Initializing ML components...")
        
        # Model Registry
        try:
            self.registry = ModelRegistry(registry_path)
            logger.info("✅ Model Registry initialized")
        except Exception as e:
            logger.warning(f"⚠️  Could not initialize registry: {e}")
        
        # LSTM Detector
        try:
            lstm_config = LSTMConfig(
                input_size=50,
                hidden_size=128,
                num_layers=2,
                epochs=30,
                batch_size=32
            )
            self.lstm_detector = LSTMSecurityDetector(lstm_config)
            logger.info("✅ LSTM Detector initialized")
        except Exception as e:
            logger.warning(f"⚠️  Could not initialize LSTM: {e}")
        
        # Autoencoder
        try:
            ae_config = AEConfig(
                input_dim=50,
                latent_dim=32,
                hidden_dims=[256, 128, 64],
                epochs=50,
                batch_size=64
            )
            self.autoencoder_detector = AutoencoderDetector(ae_config)
            logger.info("✅ Autoencoder initialized")
        except Exception as e:
            logger.warning(f"⚠️  Could not initialize Autoencoder: {e}")
        
        # NLP Extractor
        try:
            self.nlp_extractor = ThreatIntelExtractor()
            logger.info("✅ NLP Extractor initialized")
        except Exception as e:
            logger.warning(f"⚠️  Could not initialize NLP Extractor: {e}")
        
        # NLP Classifier
        try:
            self.nlp_classifier = ThreatClassifier()
            logger.info("✅ NLP Classifier initialized")
        except Exception as e:
            logger.warning(f"⚠️  Could not initialize NLP Classifier: {e}")
    
    def analyze_threat_report(self, report_text: str) -> MLAnalysisResult:
        """
        Analyze threat report using all ML modules
        
        Args:
            report_text: Unstructured threat report text
            
        Returns:
            MLAnalysisResult with unified analysis
        """
        logger.info(f"📊 Analyzing threat report...")
        
        result = MLAnalysisResult(
            id=datetime.now().strftime("%Y%m%d%H%M%S"),
            timestamp=datetime.now().isoformat(),
            input_data={'text': report_text[:500]}
        )
        
        # NLP Analysis (always works, even without models)
        if self.nlp_extractor:
            intel = self.nlp_extractor.extract(report_text)
            result.nlp_iocs = {
                'ip_addresses': intel.ip_addresses,
                'domains': intel.domains,
                'threat_actors': intel.threat_actors,
                'malware': intel.malware_families,
                'cves': intel.cve_ids
            }
            logger.info(f"   NLP: Extracted {len(intel.ip_addresses)} IPs, "
                       f"{len(intel.threat_actors)} actors")
        
        if self.nlp_classifier:
            classification = self.nlp_classifier.classify(report_text)
            result.nlp_classification = {
                'threat_type': classification.primary_threat,
                'severity': classification.primary_severity,
                'sector': classification.primary_sector,
                'confidence': classification.confidence
            }
            logger.info(f"   NLP: Classified as {classification.primary_threat}")
        
        # Calculate threat score
        result.threat_score = self._calculate_threat_score(result)
        result.threat_level = self._get_threat_level(result.threat_score)
        result.recommendations = self._generate_recommendations(result)
        
        logger.info(f"✅ Analysis complete: Threat Level = {result.threat_level}")
        
        return result
    
    def analyze_time_series(self, data: List[List[float]], 
                           feature_names: List[str] = None) -> MLAnalysisResult:
        """
        Analyze time-series data using LSTM
        
        Args:
            data: Time-series data (samples × features)
            feature_names: Optional feature names
            
        Returns:
            MLAnalysisResult with LSTM analysis
        """
        logger.info(f"📊 Analyzing time-series data...")
        
        import numpy as np
        result = MLAnalysisResult(
            id=datetime.now().strftime("%Y%m%d%H%M%S"),
            timestamp=datetime.now().isoformat(),
            input_data={'samples': len(data), 'features': len(data[0]) if data else 0}
        )
        
        if self.lstm_detector:
            # Prepare data
            X = np.array(data)
            if X.ndim == 2:
                X = X.reshape(X.shape[0], X.shape[1], 1)
            
            # Detect anomalies
            if self.lstm_detector.is_trained:
                predictions = self.lstm_detector.predict(X)
                result.lstm_is_anomaly = bool(np.any(predictions == 1))
                result.lstm_anomaly_score = float(np.mean(predictions))
            else:
                logger.warning("⚠️  LSTM not trained yet")
            
            logger.info(f"   LSTM: Anomaly detected = {result.lstm_is_anomaly}")
        
        result.threat_score = 0.5 if result.lstm_is_anomaly else 0.1
        result.threat_level = self._get_threat_level(result.threat_score)
        
        return result
    
    def train_models(self, training_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Train all ML models
        
        Args:
            training_data: Dictionary with training datasets
                - 'lstm': (X_train, y_train)
                - 'autoencoder': X_normal
                
        Returns:
            Training results
        """
        logger.info(f"📚 Training ML models...")
        results = {}
        
        import numpy as np
        
        # Train LSTM
        if self.lstm_detector and 'lstm' in training_data:
            X_train, y_train = training_data['lstm']
            logger.info("   Training LSTM...")
            lstm_history = self.lstm_detector.fit(X_train, y_train)
            results['lstm'] = {
                'final_loss': lstm_history.get('loss', [-1])[-1],
                'final_accuracy': lstm_history.get('accuracy', [-1])[-1]
            }
            
            # Register model
            if self.registry:
                self.registry.register(
                    model_name="lstm_anomaly_detector",
                    version="1.0.0",
                    model_type="lstm",
                    training_metrics=results['lstm'],
                    description="LSTM anomaly detector v1.0"
                )
        
        # Train Autoencoder
        if self.autoencoder_detector and 'autoencoder' in training_data:
            X_normal = training_data['autoencoder']
            logger.info("   Training Autoencoder...")
            ae_history = self.autoencoder_detector.fit(X_normal)
            results['autoencoder'] = {
                'final_loss': ae_history.get('loss', [-1])[-1]
            }
            
            # Register model
            if self.registry:
                self.registry.register(
                    model_name="autoencoder_novelty_detector",
                    version="1.0.0",
                    model_type="autoencoder",
                    training_metrics=results['autoencoder'],
                    description="Autoencoder novelty detector v1.0"
                )
        
        logger.info(f"✅ Training complete")
        return results
    
    def _calculate_threat_score(self, result: MLAnalysisResult) -> float:
        """Calculate unified threat score from all signals"""
        score = 0.0
        factors = 0
        
        # NLP signals
        if result.nlp_iocs:
            if result.nlp_iocs.get('ip_addresses'):
                score += 0.2
                factors += 1
            if result.nlp_iocs.get('threat_actors'):
                score += 0.3
                factors += 1
            if result.nlp_iocs.get('malware'):
                score += 0.2
                factors += 1
            if result.nlp_iocs.get('cves'):
                score += 0.1
                factors += 1
        
        # Classification signals
        if result.nlp_classification:
            severity = result.nlp_classification.get('severity', '')
            if 'critical' in severity.lower():
                score += 0.4
            elif 'high' in severity.lower():
                score += 0.3
            elif 'medium' in severity.lower():
                score += 0.2
            factors += 1
        
        # LSTM signals
        if result.lstm_is_anomaly:
            score += 0.3
            factors += 1
        
        # Autoencoder signals
        if result.autoencoder_is_novel:
            score += 0.3
            factors += 1
        
        if factors > 0:
            return min(1.0, score / max(factors, 1) * factors / 3)  # Normalize
        return 0.0
    
    def _get_threat_level(self, score: float) -> str:
        """Convert threat score to threat level"""
        if score >= 0.8:
            return "critical"
        elif score >= 0.6:
            return "high"
        elif score >= 0.4:
            return "medium"
        else:
            return "low"
    
    def _generate_recommendations(self, result: MLAnalysisResult) -> List[str]:
        """Generate actionable recommendations"""
        recommendations = []
        
        if result.nlp_iocs.get('ip_addresses'):
            recommendations.append("Block identified malicious IPs in firewall")
        
        if result.nlp_iocs.get('threat_actors'):
            actors = ', '.join(result.nlp_iocs['threat_actors'])
            recommendations.append(f"Investigate activity from threat actor: {actors}")
        
        if result.nlp_iocs.get('malware'):
            malware = ', '.join(result.nlp_iocs['malware'])
            recommendations.append(f"Scan systems for malware: {malware}")
        
        if result.lstm_is_anomaly:
            recommendations.append("Investigate network traffic anomalies")
        
        if result.autoencoder_is_novel:
            recommendations.append("Review novel patterns for potential zero-day")
        
        if result.threat_level in ['critical', 'high']:
            recommendations.append("Escalate to security team immediately")
            recommendations.append("Activate incident response procedures")
        
        if not recommendations:
            recommendations.append("Continue monitoring")
            recommendations.append("Update threat intelligence feeds")
        
        return recommendations
    
    def export_analysis(self, result: MLAnalysisResult, filepath: str):
        """Export analysis result to JSON"""
        with open(filepath, 'w') as f:
            json.dump(result.to_dict(), f, indent=2)
        logger.info(f"💾 Exported analysis to {filepath}")


def main():
    """Demo ML orchestrator"""
    print("""
╔═══════════════════════════════════════════════════════════════╗
║     🧠 KALIAGENT v5.0.0 - ML ORCHESTRATOR                    ║
║                    Phase 14: Alpha 0.1.0                      ║
╚═══════════════════════════════════════════════════════════════╝

Unified ML pipeline integrating Phase 11-14

    """)
    
    if not TORCH_AVAILABLE:
        print("⚠️  Some ML modules not available")
        print("   Install with: pip install torch transformers\n")
    
    # Initialize orchestrator
    orchestrator = MLOrchestrator("./ml_registry")
    
    # Analyze threat report
    sample_report = """
    Critical ransomware attack detected. Conti group targeting
    healthcare facilities via phishing emails. Malware: Conti v3.
    CVE-2024-1234 exploited. C2 server: 203.0.113.50.
    Severity: CRITICAL. Immediate response required.
    """
    
    print("\n📊 Analyzing threat report...")
    print("-" * 70)
    print(sample_report[:200] + "...")
    print("-" * 70)
    
    result = orchestrator.analyze_threat_report(sample_report)
    
    # Display results
    print(f"\n✅ ML Analysis Complete:")
    print(f"   Threat Score: {result.threat_score:.2f}")
    print(f"   Threat Level: {result.threat_level.upper()}")
    
    if result.nlp_iocs:
        print(f"\n📍 Extracted IOCs:")
        if result.nlp_iocs.get('ip_addresses'):
            print(f"   IPs: {', '.join(result.nlp_iocs['ip_addresses'])}")
        if result.nlp_iocs.get('threat_actors'):
            print(f"   Actors: {', '.join(result.nlp_iocs['threat_actors'])}")
        if result.nlp_iocs.get('malware'):
            print(f"   Malware: {', '.join(result.nlp_iocs['malware'])}")
        if result.nlp_iocs.get('cves'):
            print(f"   CVEs: {', '.join(result.nlp_iocs['cves'])}")
    
    if result.nlp_classification:
        print(f"\n🏷️  Classification:")
        print(f"   Type: {result.nlp_classification.get('threat_type', 'Unknown')}")
        print(f"   Severity: {result.nlp_classification.get('severity', 'Unknown')}")
    
    print(f"\n💡 Recommendations:")
    for i, rec in enumerate(result.recommendations, 1):
        print(f"   {i}. {rec}")
    
    # Export
    orchestrator.export_analysis(result, "./ml_analysis_result.json")
    print(f"\n💾 Analysis exported to ./ml_analysis_result.json")
    
    print("\n" + "="*70)
    print("✅ ML Orchestrator demo complete!")
    print("="*70)


if __name__ == "__main__":
    main()
