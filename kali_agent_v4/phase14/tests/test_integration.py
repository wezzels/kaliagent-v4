#!/usr/bin/env python3
"""
🧠 KaliAgent v5.0.0 - Phase 14: Integration Tests

End-to-end tests for all ML modules:
- LSTM Network
- Autoencoder
- NLP Extractor
- NLP Classifier
- Model Registry
- Federated Learning
- ML Orchestrator

Author: KaliAgent Team
"""

import sys
import unittest
import numpy as np
from pathlib import Path
from datetime import datetime

# Add phase14 to path
sys.path.insert(0, str(Path(__file__).parent.parent))

print("""
╔═══════════════════════════════════════════════════════════════╗
║     🧠 KALIAGENT v5.0.0 - PHASE 14 INTEGRATION TESTS         ║
╚═══════════════════════════════════════════════════════════════╝
""")


class TestLSTMNetwork(unittest.TestCase):
    """Test LSTM anomaly detection"""
    
    def test_lstm_initialization(self):
        """Test LSTM detector initializes correctly"""
        from deep_learning.lstm_network import LSTMSecurityDetector, LSTMConfig
        
        config = LSTMConfig(input_size=5, hidden_size=64, epochs=5)
        detector = LSTMSecurityDetector(config)
        
        self.assertIsNotNone(detector)
        self.assertEqual(detector.config.input_size, 5)
        print("   ✅ LSTM initialization")
    
    def test_lstm_training(self):
        """Test LSTM training on synthetic data"""
        from deep_learning.lstm_network import LSTMSecurityDetector, LSTMConfig, generate_sample_data
        
        # Generate data
        X, y = generate_sample_data(num_samples=100, seq_length=20, num_features=5)
        
        # Train
        config = LSTMConfig(input_size=5, hidden_size=32, epochs=5, batch_size=16)
        detector = LSTMSecurityDetector(config)
        history = detector.fit(X[:80], y[:80])
        
        # Verify training completed
        self.assertTrue(detector.is_trained)
        self.assertIn('loss', history)
        self.assertEqual(len(history['loss']), 5)
        print("   ✅ LSTM training")
    
    def test_lstm_prediction(self):
        """Test LSTM anomaly prediction"""
        from deep_learning.lstm_network import LSTMSecurityDetector, LSTMConfig, generate_sample_data
        
        # Generate and train
        X, y = generate_sample_data(num_samples=100, seq_length=20, num_features=5)
        config = LSTMConfig(input_size=5, hidden_size=32, epochs=5)
        detector = LSTMSecurityDetector(config)
        detector.fit(X[:80], y[:80])
        
        # Predict
        predictions = detector.predict(X[80:])
        
        # Verify predictions
        self.assertEqual(len(predictions), len(X) - 80)
        self.assertIn(predictions[0], [0, 1])
        print("   ✅ LSTM prediction")


class TestAutoencoder(unittest.TestCase):
    """Test Autoencoder novelty detection"""
    
    def test_ae_initialization(self):
        """Test Autoencoder initializes correctly"""
        from deep_learning.autoencoder import AutoencoderDetector, AEConfig
        
        config = AEConfig(input_dim=50, latent_dim=16, epochs=5)
        detector = AutoencoderDetector(config)
        
        self.assertIsNotNone(detector)
        self.assertEqual(detector.config.input_dim, 50)
        print("   ✅ Autoencoder initialization")
    
    def test_ae_training(self):
        """Test Autoencoder training on normal data"""
        from deep_learning.autoencoder import AutoencoderDetector, AEConfig, generate_normal_data
        
        # Generate normal data
        X_normal = generate_normal_data(n=500, dim=50)
        
        # Train
        config = AEConfig(input_dim=50, latent_dim=16, epochs=10, batch_size=32)
        detector = AutoencoderDetector(config)
        history = detector.fit(X_normal[:400])
        
        # Verify training
        self.assertTrue(detector.is_trained)
        self.assertIn('loss', history)
        print("   ✅ Autoencoder training")
    
    def test_ae_novelty_detection(self):
        """Test Autoencoder detects novel patterns"""
        from deep_learning.autoencoder import AutoencoderDetector, AEConfig
        from deep_learning.autoencoder import generate_normal_data, generate_attack_data
        
        # Generate data
        X_normal = generate_normal_data(n=500, dim=50)
        X_attack = generate_attack_data(n=50, dim=50)
        
        # Train on normal only
        config = AEConfig(input_dim=50, latent_dim=16, epochs=10)
        detector = AutoencoderDetector(config)
        detector.fit(X_normal[:400])
        
        # Detect attacks
        predictions = detector.detect(X_attack)
        
        # Should detect most attacks
        detection_rate = np.mean(predictions)
        self.assertGreater(detection_rate, 0.5)  # At least 50% detection
        print(f"   ✅ Autoencoder novelty detection ({detection_rate:.0%} detected)")


class TestNLPExtractor(unittest.TestCase):
    """Test NLP Threat Intel Extraction"""
    
    def test_extractor_initialization(self):
        """Test NLP Extractor initializes"""
        from nlp.threat_intel_extractor import ThreatIntelExtractor
        
        extractor = ThreatIntelExtractor()
        self.assertIsNotNone(extractor)
        print("   ✅ NLP Extractor initialization")
    
    def test_ioc_extraction(self):
        """Test IOC extraction from text"""
        from nlp.threat_intel_extractor import ThreatIntelExtractor
        
        extractor = ThreatIntelExtractor()
        
        text = """
        APT29 attacked using malware. C2 server at 203.0.113.50
        and malicious-domain.com. CVE-2024-1234 exploited.
        Hash: a1b2c3d4e5f6789012345678901234567890123456789012345678901234abcd
        """
        
        result = extractor.extract(text)
        
        # Verify extraction
        self.assertIn('203.0.113.50', result.ip_addresses)
        self.assertIn('APT29', result.threat_actors)
        self.assertIn('CVE-2024-1234', result.cve_ids)
        self.assertTrue(len(result.file_hashes.get('sha256', [])) > 0)
        print("   ✅ NLP IOC extraction")
    
    def test_threat_actor_detection(self):
        """Test threat actor detection"""
        from nlp.threat_intel_extractor import ThreatIntelExtractor
        
        extractor = ThreatIntelExtractor()
        
        actors = ['APT29', 'Lazarus', 'Conti', 'APT28', 'CozyBear']
        
        for actor in actors:
            text = f"{actor} conducted a cyber attack"
            result = extractor.extract(text)
            self.assertIn(actor, result.threat_actors)
        
        print(f"   ✅ Threat actor detection ({len(actors)} actors)")


class TestNLPClassifier(unittest.TestCase):
    """Test NLP Threat Classification"""
    
    def test_classifier_initialization(self):
        """Test NLP Classifier initializes"""
        from nlp.threat_classifier import ThreatClassifier
        
        classifier = ThreatClassifier()
        self.assertIsNotNone(classifier)
        print("   ✅ NLP Classifier initialization")
    
    def test_threat_type_classification(self):
        """Test threat type classification (rule-based fallback)"""
        from nlp.threat_classifier import ThreatClassifier
        
        classifier = ThreatClassifier()
        
        # Test ransomware detection
        text = "Critical ransomware attack encrypting files"
        result = classifier.classify(text)
        
        # Should classify (rule-based or ML)
        self.assertIsNotNone(result)
        print("   ✅ NLP threat classification")


class TestModelRegistry(unittest.TestCase):
    """Test Model Registry"""
    
    def test_registry_initialization(self):
        """Test Model Registry initializes"""
        from model_registry.model_registry import ModelRegistry
        
        registry = ModelRegistry("./test_registry")
        self.assertIsNotNone(registry)
        print("   ✅ Model Registry initialization")
    
    def test_model_registration(self):
        """Test model registration"""
        from model_registry.model_registry import ModelRegistry
        
        registry = ModelRegistry("./test_registry")
        
        metadata = registry.register(
            model_name="test_model",
            version="1.0.0",
            model_type="lstm",
            training_metrics={'accuracy': 0.95, 'loss': 0.05},
            description="Test model"
        )
        
        # Verify registration
        self.assertEqual(metadata.name, "test_model")
        self.assertEqual(metadata.version, "1.0.0")
        self.assertEqual(metadata.training_metrics['accuracy'], 0.95)
        print("   ✅ Model registration")
    
    def test_ab_testing(self):
        """Test A/B testing"""
        from model_registry.model_registry import ModelRegistry
        
        registry = ModelRegistry("./test_registry")
        
        result = registry.ab_test(
            control_model="test_model",
            control_version="1.0.0",
            candidate_model="test_model",
            candidate_version="1.1.0",
            metric_name="f1",
            control_score=0.95,
            candidate_score=0.96
        )
        
        # Verify A/B test
        self.assertEqual(result.control_score, 0.95)
        self.assertEqual(result.candidate_score, 0.96)
        self.assertGreater(result.improvement, 0)
        print("   ✅ A/B testing")


class TestFederatedLearning(unittest.TestCase):
    """Test Federated Learning"""
    
    def test_federated_initialization(self):
        """Test Federated Coordinator initializes"""
        from federated.federated_learning import FederatedCoordinator, SimpleFederatedModel
        
        model = SimpleFederatedModel(input_dim=50, hidden_dim=32)
        coordinator = FederatedCoordinator(model, num_clients=3)
        
        self.assertIsNotNone(coordinator)
        self.assertEqual(len(coordinator.clients), 3)
        print("   ✅ Federated Learning initialization")
    
    def test_federated_round(self):
        """Test single federated learning round"""
        from federated.federated_learning import FederatedCoordinator, SimpleFederatedModel
        
        model = SimpleFederatedModel(input_dim=50, hidden_dim=32)
        coordinator = FederatedCoordinator(model, num_clients=3)
        
        # Run one round
        round_result = coordinator.run_round()
        
        # Verify round completed
        self.assertIsNotNone(round_result)
        self.assertEqual(round_result.round_id, 1)
        self.assertGreater(round_result.num_clients, 0)
        print(f"   ✅ Federated round ({round_result.num_clients} clients)")


class TestMLOrchestrator(unittest.TestCase):
    """Test ML Orchestrator Integration"""
    
    def test_orchestrator_initialization(self):
        """Test ML Orchestrator initializes"""
        from ml_orchestrator import MLOrchestrator
        
        orchestrator = MLOrchestrator("./orchestrator_registry")
        self.assertIsNotNone(orchestrator)
        print("   ✅ ML Orchestrator initialization")
    
    def test_threat_report_analysis(self):
        """Test complete threat report analysis"""
        from ml_orchestrator import MLOrchestrator
        
        orchestrator = MLOrchestrator("./orchestrator_registry")
        
        report = """
        Critical ransomware attack. Conti group targeting healthcare.
        Malware: Conti v3. CVE-2024-1234 exploited.
        C2 server: 203.0.113.50
        """
        
        result = orchestrator.analyze_threat_report(report)
        
        # Verify analysis
        self.assertIsNotNone(result)
        self.assertIn('203.0.113.50', str(result.nlp_iocs.get('ip_addresses', [])))
        self.assertIn('Conti', str(result.nlp_iocs.get('threat_actors', [])))
        self.assertIn('CVE-2024-1234', str(result.nlp_iocs.get('cves', [])))
        print("   ✅ ML Orchestrator threat analysis")
    
    def test_recommendations_generation(self):
        """Test recommendation generation"""
        from ml_orchestrator import MLOrchestrator
        
        orchestrator = MLOrchestrator()
        
        report = "APT29 malware attack with C2 at 192.168.1.100"
        result = orchestrator.analyze_threat_report(report)
        
        # Should have recommendations
        self.assertGreater(len(result.recommendations), 0)
        print(f"   ✅ Recommendations generated ({len(result.recommendations)} items)")


def run_tests():
    """Run all integration tests"""
    # Create test suite
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    # Add test classes
    suite.addTests(loader.loadTestsFromTestCase(TestLSTMNetwork))
    suite.addTests(loader.loadTestsFromTestCase(TestAutoencoder))
    suite.addTests(loader.loadTestsFromTestCase(TestNLPExtractor))
    suite.addTests(loader.loadTestsFromTestCase(TestNLPClassifier))
    suite.addTests(loader.loadTestsFromTestCase(TestModelRegistry))
    suite.addTests(loader.loadTestsFromTestCase(TestFederatedLearning))
    suite.addTests(loader.loadTestsFromTestCase(TestMLOrchestrator))
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # Summary
    print("\n" + "="*70)
    print("TEST SUMMARY")
    print("="*70)
    print(f"Tests Run: {result.testsRun}")
    print(f"Failures: {len(result.failures)}")
    print(f"Errors: {len(result.errors)}")
    print(f"Success: {result.wasSuccessful()}")
    print("="*70)
    
    return result.wasSuccessful()


if __name__ == "__main__":
    success = run_tests()
    sys.exit(0 if success else 1)
