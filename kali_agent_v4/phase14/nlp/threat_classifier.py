#!/usr/bin/env python3
"""
🧠 KaliAgent v5.0.0 - Phase 14: NLP Threat Classification

Multi-label classification for threat reports:
- Threat type (ransomware, APT, phishing, malware, etc.)
- Severity level (critical, high, medium, low)
- Target sector (defense, finance, healthcare, energy, etc.)
- Attack vector (email, web, USB, network, etc.)

Author: KaliAgent Team
Status: Alpha (0.1.0)
"""

import logging
from typing import List, Dict, Tuple
from dataclasses import dataclass, field
from datetime import datetime
import json

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger('ThreatClassifier')

try:
    import torch
    from transformers import pipeline, AutoTokenizer, AutoModelForSequenceClassification
    TRANSFORMERS_AVAILABLE = True
except ImportError:
    TRANSFORMERS_AVAILABLE = False
    logger.warning("⚠️ Transformers not available")


@dataclass
class ClassificationResult:
    """Threat classification result"""
    id: str
    timestamp: datetime
    source_text: str
    
    # Multi-label predictions
    threat_types: List[Dict[str, float]] = field(default_factory=list)  # [{label: score}]
    severity: List[Dict[str, float]] = field(default_factory=list)
    sectors: List[Dict[str, float]] = field(default_factory=list)
    vectors: List[Dict[str, float]] = field(default_factory=list)
    
    # Top predictions
    primary_threat: str = ""
    primary_severity: str = ""
    primary_sector: str = ""
    primary_vector: str = ""
    
    confidence: float = 0.0
    
    def to_dict(self) -> Dict:
        return {
            'id': self.id,
            'timestamp': self.timestamp.isoformat(),
            'predictions': {
                'threat_types': self.threat_types,
                'severity': self.severity,
                'sectors': self.sectors,
                'vectors': self.vectors
            },
            'top_predictions': {
                'threat_type': self.primary_threat,
                'severity': self.primary_severity,
                'sector': self.primary_sector,
                'vector': self.primary_vector
            },
            'confidence': self.confidence
        }


class ThreatClassifier:
    """
    Multi-label threat classifier using transformer models
    
    Classifies threat reports into:
    - Threat type (ransomware, APT, phishing, etc.)
    - Severity (critical, high, medium, low)
    - Target sector (defense, finance, healthcare, etc.)
    - Attack vector (email, web, USB, network, etc.)
    """
    
    VERSION = "0.1.0"
    
    def __init__(self, model_name: str = None):
        self.model_name = model_name or "facebook/bart-large-mnli"
        self.classifier_pipeline = None
        
        # Zero-shot classification labels
        self.threat_type_labels = [
            "ransomware attack",
            "APT campaign",
            "phishing attack",
            "malware infection",
            "DDoS attack",
            "insider threat",
            "data breach",
            "credential theft",
            "supply chain attack",
            "zero-day exploit"
        ]
        
        self.severity_labels = [
            "critical severity",
            "high severity",
            "medium severity",
            "low severity"
        ]
        
        self.sector_labels = [
            "defense sector",
            "finance sector",
            "healthcare sector",
            "energy sector",
            "government sector",
            "technology sector",
            "telecommunications",
            "manufacturing",
            "retail",
            "education"
        ]
        
        self.vector_labels = [
            "email attack",
            "web-based attack",
            "USB/removable media",
            "network intrusion",
            "social engineering",
            "software vulnerability",
            "misconfiguration",
            "physical access"
        ]
        
        if TRANSFORMERS_AVAILABLE:
            self._load_model()
        
        logger.info(f"🧠 Threat Classifier v{self.VERSION}")
    
    def _load_model(self):
        """Load zero-shot classification model"""
        try:
            logger.info("📥 Loading classification model...")
            device = 0 if torch.cuda.is_available() else -1
            self.classifier_pipeline = pipeline(
                "zero-shot-classification",
                model=self.model_name,
                device=device,
                batch_size=4
            )
            logger.info("✅ Classifier loaded")
            
            if torch.cuda.is_available():
                logger.info(f"   GPU: {torch.cuda.get_device_name(0)}")
        except Exception as e:
            logger.warning(f"⚠️  Could not load model: {e}")
            self.classifier_pipeline = None
    
    def classify(self, text: str, top_k: int = 3) -> ClassificationResult:
        """
        Classify threat report
        
        Args:
            text: Threat report text
            top_k: Number of top predictions to return per category
            
        Returns:
            ClassificationResult with multi-label predictions
        """
        result = ClassificationResult(
            id=datetime.now().strftime("%Y%m%d%H%M%S"),
            timestamp=datetime.now(),
            source_text=text
        )
        
        if self.classifier_pipeline:
            # Classify threat type
            result.threat_types = self._classify_text(
                text, self.threat_type_labels, top_k
            )
            
            # Classify severity
            result.severity = self._classify_text(
                text, self.severity_labels, top_k
            )
            
            # Classify sector
            result.sectors = self._classify_text(
                text, self.sector_labels, top_k
            )
            
            # Classify attack vector
            result.vectors = self._classify_text(
                text, self.vector_labels, top_k
            )
            
            # Set top predictions
            if result.threat_types:
                result.primary_threat = result.threat_types[0]['label']
            if result.severity:
                result.primary_severity = result.severity[0]['label']
            if result.sectors:
                result.primary_sector = result.sectors[0]['label']
            if result.vectors:
                result.primary_vector = result.vectors[0]['label']
            
            # Calculate confidence
            all_scores = []
            for category in [result.threat_types, result.severity, 
                           result.sectors, result.vectors]:
                if category:
                    all_scores.append(category[0]['score'])
            
            if all_scores:
                result.confidence = sum(all_scores) / len(all_scores)
        else:
            # Fallback to rule-based
            self._classify_rule_based(text, result)
        
        logger.info(f"✅ Classified: {result.primary_threat} | "
                   f"{result.primary_severity} | "
                   f"{result.primary_sector}")
        
        return result
    
    def _classify_text(self, text: str, labels: List[str], 
                       top_k: int = 3) -> List[Dict[str, float]]:
        """Classify text into labels using zero-shot classification"""
        if not self.classifier_pipeline:
            return []
        
        try:
            result = self.classifier_pipeline(
                text,
                candidate_labels=labels,
                top_k=top_k,
                multi_label=True
            )
            
            # Normalize format
            if isinstance(result, dict):
                result = [result]
            
            return [
                {'label': r['label'], 'score': round(r['score'], 4)}
                for r in result
            ]
        except Exception as e:
            logger.warning(f"Classification failed: {e}")
            return []
    
    def _classify_rule_based(self, text: str, result: ClassificationResult):
        """Fallback rule-based classification"""
        text_lower = text.lower()
        
        # Threat type keywords
        threat_keywords = {
            'ransomware attack': ['ransomware', 'encryption', 'ransom', 'bitcoin'],
            'APT campaign': ['apt', 'persistent', 'nation-state', 'espionage'],
            'phishing attack': ['phishing', 'spearphishing', 'credential'],
            'malware infection': ['malware', 'trojan', 'virus', 'backdoor'],
            'DDoS attack': ['ddos', 'denial of service', 'flood'],
            'data breach': ['breach', 'exfiltration', 'data leak']
        }
        
        scores = {}
        for threat_type, keywords in threat_keywords.items():
            score = sum(1 for kw in keywords if kw in text_lower)
            if score > 0:
                scores[threat_type] = score / len(keywords)
        
        result.threat_types = [
            {'label': k, 'score': round(v, 4)}
            for k, v in sorted(scores.items(), key=lambda x: x[1], reverse=True)[:3]
        ]
        
        if result.threat_types:
            result.primary_threat = result.threat_types[0]['label']
            result.confidence = result.threat_types[0]['score']
        
        # Severity
        severity_keywords = {
            'critical severity': ['critical', 'emergency', 'immediate'],
            'high severity': ['high', 'serious', 'significant'],
            'medium severity': ['medium', 'moderate'],
            'low severity': ['low', 'minor']
        }
        
        for severity, keywords in severity_keywords.items():
            if any(kw in text_lower for kw in keywords):
                result.severity = [{'label': severity, 'score': 0.8}]
                result.primary_severity = severity
                break
    
    def batch_classify(self, texts: List[str]) -> List[ClassificationResult]:
        """Classify multiple threat reports"""
        results = []
        for text in texts:
            result = self.classify(text)
            results.append(result)
        return results
    
    def export_json(self, result: ClassificationResult, filepath: str):
        """Export classification to JSON"""
        with open(filepath, 'w') as f:
            json.dump(result.to_dict(), f, indent=2)
        logger.info(f"💾 Exported to {filepath}")


def main():
    """Demo threat classification"""
    print("""
╔═══════════════════════════════════════════════════════════════╗
║     🧠 KALIAGENT v5.0.0 - THREAT CLASSIFIER                  ║
║                    Phase 14: Alpha 0.1.0                      ║
╚═══════════════════════════════════════════════════════════════╝

    """)
    
    # Sample reports
    samples = [
        """
        Critical ransomware attack detected targeting healthcare facilities.
        Conti ransomware group has encrypted patient records at multiple hospitals.
        Attack vector: phishing email with malicious attachment.
        Immediate response required.
        """,
        
        """
        APT29 suspected of conducting espionage campaign against defense contractors.
        Supply chain compromise detected in software updates.
        Severity: High. Data exfiltration observed.
        """,
        
        """
        DDoS attack targeting financial services website.
        Traffic spike from botnet detected.
        Service degradation for 2 hours.
        """,
    ]
    
    classifier = ThreatClassifier()
    
    for i, text in enumerate(samples, 1):
        print(f"\n{'='*70}")
        print(f"📄 Report {i}:")
        print(f"{'='*70}")
        print(text.strip()[:150] + "...")
        
        result = classifier.classify(text)
        
        print(f"\n✅ Classification:")
        print(f"   Threat Type: {result.primary_threat} ({result.threat_types[0]['score']:.0%})" if result.threat_types else "")
        print(f"   Severity: {result.primary_severity} ({result.severity[0]['score']:.0%})" if result.severity else "")
        print(f"   Sector: {result.primary_sector} ({result.sectors[0]['score']:.0%})" if result.sectors else "")
        print(f"   Vector: {result.primary_vector} ({result.vectors[0]['score']:.0%})" if result.vectors else "")
        print(f"   Overall Confidence: {result.confidence:.0%}")
    
    print(f"\n{'='*70}")
    print("✅ Threat Classification complete!")
    print("="*70)


if __name__ == "__main__":
    main()
