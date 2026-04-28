#!/usr/bin/env python3
"""
🧠 KaliAgent v5.0.0 - Phase 14: NLP for Threat Intelligence
Automatic extraction of IOCs, TTPs, and threat actors from text

Uses pre-trained transformers for:
- Named Entity Recognition (IOCs, malware, threat actors)
- Text classification (threat type, severity)
- Summarization (auto-generate executive summaries)

Author: KaliAgent Team
Status: Alpha (0.1.0)
"""

import logging
import re
from typing import List, Dict, Optional
from dataclasses import dataclass, field
from datetime import datetime
import json

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger('ThreatIntelExtractor')

# Try to import transformers
try:
    from transformers import pipeline, AutoTokenizer, AutoModelForTokenClassification
    from transformers import Pipeline
    TRANSFORMERS_AVAILABLE = True
    logger.info("✅ Transformers available")
except ImportError:
    TRANSFORMERS_AVAILABLE = False
    logger.warning("⚠️ Transformers not available - using rule-based fallback")


@dataclass
class ThreatIntelResult:
    """Extracted threat intelligence"""
    id: str
    timestamp: datetime
    source_text: str
    
    # IOCs
    ip_addresses: List[str] = field(default_factory=list)
    domains: List[str] = field(default_factory=list)
    urls: List[str] = field(default_factory=list)
    email_addresses: List[str] = field(default_factory=list)
    file_hashes: Dict[str, List[str]] = field(default_factory=dict)  # md5, sha1, sha256
    
    # Threat Info
    threat_actors: List[str] = field(default_factory=list)
    malware_families: List[str] = field(default_factory=list)
    cve_ids: List[str] = field(default_factory=list)
    mitre_techniques: List[str] = field(default_factory=list)
    
    # Classification
    threat_type: Optional[str] = None
    severity: Optional[str] = None
    industries: List[str] = field(default_factory=list)
    regions: List[str] = field(default_factory=list)
    
    # Summary
    summary: Optional[str] = None
    confidence: float = 0.0
    
    def to_dict(self) -> Dict:
        return {
            'id': self.id,
            'timestamp': self.timestamp.isoformat(),
            'source_text': self.source_text[:200] + '...' if len(self.source_text) > 200 else self.source_text,
            'iocs': {
                'ip_addresses': self.ip_addresses,
                'domains': self.domains,
                'urls': self.urls,
                'emails': self.email_addresses,
                'hashes': self.file_hashes
            },
            'threat_info': {
                'actors': self.threat_actors,
                'malware': self.malware_families,
                'cves': self.cve_ids,
                'mitre': self.mitre_techniques
            },
            'classification': {
                'type': self.threat_type,
                'severity': self.severity,
                'industries': self.industries,
                'regions': self.regions
            },
            'summary': self.summary,
            'confidence': self.confidence
        }
    
    def to_stix(self) -> Dict:
        """Convert to STIX 2.1 format"""
        stix_object = {
            "type": "indicator",
            "spec_version": "2.1",
            "id": f"indicator--{self.id}",
            "created": self.timestamp.isoformat(),
            "modified": self.timestamp.isoformat(),
            "name": f"Threat Intel Extract - {self.id}",
            "pattern_type": "stix",
            "valid_from": self.timestamp.isoformat()
        }
        return stix_object


class ThreatIntelExtractor:
    """
    NLP-based Threat Intelligence Extractor
    
    Extracts structured threat intel from unstructured text:
    - IOCs (IPs, domains, URLs, hashes, emails)
    - Threat actors (APT groups, cybercriminal organizations)
    - Malware families
    - CVEs and vulnerabilities
    - MITRE ATT&CK techniques
    - Industries and regions targeted
    """
    
    VERSION = "0.1.0"
    
    def __init__(self, model_name: str = None):
        self.model_name = model_name or "dslim/bert-base-NER"
        self.ner_pipeline = None
        self.classifier_pipeline = None
        self.summarizer_pipeline = None
        
        # Rule-based patterns (fallback)
        self.patterns = self._build_patterns()
        
        # Known threat actors (for matching)
        self.threat_actors = self._load_threat_actors()
        
        # Known malware families
        self.malware_families = self._load_malware_families()
        
        if TRANSFORMERS_AVAILABLE:
            self._load_models()
        
        logger.info(f"🧠 Threat Intel Extractor v{self.VERSION}")
    
    def _build_patterns(self) -> Dict[str, re.Pattern]:
        """Build regex patterns for IOC extraction"""
        return {
            'ip': re.compile(r'\b(?:\d{1,3}\.){3}\d{1,3}\b'),
            'domain': re.compile(r'\b(?:[a-zA-Z0-9-]+\.)+[a-zA-Z]{2,}\b'),
            'url': re.compile(r'https?://[^\s<>"{}|\\^`\[\]]+'),
            'email': re.compile(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'),
            'md5': re.compile(r'\b[a-fA-F0-9]{32}\b'),
            'sha1': re.compile(r'\b[a-fA-F0-9]{40}\b'),
            'sha256': re.compile(r'\b[a-fA-F0-9]{64}\b'),
            'cve': re.compile(r'\bCVE-\d{4}-\d{4,7}\b'),
            'mitre': re.compile(r'\b(?:T|TA)\d{4}(?:\.\d{3})?\b'),
        }
    
    def _load_threat_actors(self) -> List[str]:
        """Load known threat actor names"""
        return [
            'APT29', 'APT28', 'APT41', 'APT37', 'APT38', 'APT32',
            'Lazarus', 'Kimsuky', 'Turla', 'Sandworm', 'FancyBear',
            'CozyBear', 'Equation Group', 'DarkSide', 'Conti', 'REvil',
            'Ryuk', 'Emotet', 'TrickBot', 'Cobalt Group', 'FIN7',
            'Carbanak', 'Silence', 'TA505', 'Wizard Spider', 'Evil Corp',
            'DragonFly', 'MuddyWater', 'Charming Kitten', 'OilRig'
        ]
    
    def _load_malware_families(self) -> List[str]:
        """Load known malware family names"""
        return [
            'Emotet', 'TrickBot', 'QakBot', 'Dridex', 'Ryuk', 'Conti',
            'REvil', 'DarkSide', 'Cobalt Strike', 'Mimikatz', 'Metasploit',
            'WellMess', 'WellMail', 'Sunburst', 'Supernova', 'Triton',
            'Stuxnet', 'NotPetya', 'WannaCry', 'BlackEnergy', 'Industroyer',
            'Havex', 'BlackShades', 'RAT', 'AgentTesla', 'FormBook',
            'NanoCore', 'njRAT', 'AsyncRAT', 'RemcosRAT', 'QuasarRAT'
        ]
    
    def _load_models(self):
        """Load NLP models"""
        try:
            logger.info("📥 Loading NER model...")
            self.ner_pipeline = pipeline(
                "ner",
                model=self.model_name,
                aggregation_strategy="simple",
                device=0 if torch.cuda.is_available() else -1
            )
            logger.info("✅ NER model loaded")
        except Exception as e:
            logger.warning(f"⚠️  Could not load NER model: {e}")
            self.ner_pipeline = None
        
        try:
            logger.info("📥 Loading classifier model...")
            self.classifier_pipeline = pipeline(
                "text-classification",
                model="distilbert-base-uncased-finetuned-sst-2-english",
                device=0 if torch.cuda.is_available() else -1
            )
            logger.info("✅ Classifier loaded")
        except Exception as e:
            logger.warning(f"⚠️  Could not load classifier: {e}")
            self.classifier_pipeline = None
        
        try:
            logger.info("📥 Loading summarizer model...")
            self.summarizer_pipeline = pipeline(
                "summarization",
                model="facebook/bart-base-cnn_dailymail_v1",
                device=0 if torch.cuda.is_available() else -1
            )
            logger.info("✅ Summarizer loaded")
        except Exception as e:
            logger.warning(f"⚠️  Could not load summarizer: {e}")
            self.summarizer_pipeline = None
    
    def extract(self, text: str) -> ThreatIntelResult:
        """
        Extract threat intelligence from text
        
        Args:
            text: Unstructured threat report text
            
        Returns:
            ThreatIntelResult with extracted entities
        """
        result = ThreatIntelResult(
            id=datetime.now().strftime("%Y%m%d%H%M%S"),
            timestamp=datetime.now(),
            source_text=text
        )
        
        # Extract IOCs using regex (always works)
        self._extract_iocs(text, result)
        
        # Extract threat actors and malware
        self._extract_threat_entities(text, result)
        
        # Use NLP models if available
        if TRANSFORMERS_AVAILABLE and self.ner_pipeline:
            self._extract_with_ner(text, result)
        
        # Classify threat type and severity
        self._classify_threat(text, result)
        
        # Generate summary if long enough
        if len(text) > 200 and self.summarizer_pipeline:
            self._generate_summary(text, result)
        
        # Calculate confidence
        result.confidence = self._calculate_confidence(result)
        
        logger.info(f"✅ Extracted: {len(result.ip_addresses)} IPs, "
                   f"{len(result.domains)} domains, "
                   f"{len(result.threat_actors)} actors, "
                   f"{len(result.malware_families)} malware")
        
        return result
    
    def _extract_iocs(self, text: str, result: ThreatIntelResult):
        """Extract IOCs using regex patterns"""
        # IP addresses
        result.ip_addresses = list(set(self.patterns['ip'].findall(text)))
        
        # Domains (exclude common words)
        domains = set(self.patterns['domain'].findall(text))
        exclude = {'com', 'org', 'net', 'edu', 'gov', 'mil', 'io', 'ai'}
        result.domains = [d for d in domains if d.split('.')[-1].lower() not in exclude]
        
        # URLs
        result.urls = list(set(self.patterns['url'].findall(text)))
        
        # Emails
        result.email_addresses = list(set(self.patterns['email'].findall(text)))
        
        # File hashes
        md5s = self.patterns['md5'].findall(text)
        sha1s = self.patterns['sha1'].findall(text)
        sha256s = self.patterns['sha256'].findall(text)
        
        if md5s:
            result.file_hashes['md5'] = md5s
        if sha1s:
            result.file_hashes['sha1'] = sha1s
        if sha256s:
            result.file_hashes['sha256'] = sha256s
        
        # CVEs
        result.cve_ids = list(set(self.patterns['cve'].findall(text)))
        
        # MITRE ATT&CK
        result.mitre_techniques = list(set(self.patterns['mitre'].findall(text)))
    
    def _extract_threat_entities(self, text: str, result: ThreatIntelResult):
        """Extract threat actors and malware families"""
        text_lower = text.lower()
        
        # Threat actors
        for actor in self.threat_actors:
            if actor.lower() in text_lower:
                result.threat_actors.append(actor)
        
        # Malware families
        for malware in self.malware_families:
            if malware.lower() in text_lower:
                result.malware_families.append(malware)
        
        # Deduplicate
        result.threat_actors = list(set(result.threat_actors))
        result.malware_families = list(set(result.malware_families))
    
    def _extract_with_ner(self, text: str, result: ThreatIntelResult):
        """Extract entities using NER model"""
        if not self.ner_pipeline:
            return
        
        try:
            ner_results = self.ner_pipeline(text)
            
            for entity in ner_results:
                word = entity.get('word', '')
                entity_type = entity.get('entity_group', '')
                
                # Organizations might be threat actors
                if entity_type == 'ORG' and len(word) > 3:
                    # Check if it looks like a threat actor name
                    if any(x in word.upper() for x in ['APT', 'LAZARUS', 'COBALT', 'SPIDER']):
                        if word not in result.threat_actors:
                            result.threat_actors.append(word)
        except Exception as e:
            logger.warning(f"NER extraction failed: {e}")
    
    def _classify_threat(self, text: str, result: ThreatIntelResult):
        """Classify threat type and severity"""
        text_lower = text.lower()
        
        # Threat type classification
        threat_types = {
            'ransomware': ['ransomware', 'encryption', 'ransom', 'bitcoin'],
            'apt': ['apt', 'advanced persistent', 'nation-state', 'espionage'],
            'malware': ['malware', 'trojan', 'virus', 'worm', 'backdoor'],
            'phishing': ['phishing', 'spearphishing', 'credential harvesting'],
            'ddos': ['ddos', 'denial of service', 'flood attack'],
            'insider': ['insider threat', 'privileged user', 'employee'],
            'iot': ['iot', 'embedded device', 'firmware'],
            'ics': ['ics', 'scada', 'industrial control', 'plc']
        }
        
        scores = {}
        for threat_type, keywords in threat_types.items():
            score = sum(1 for kw in keywords if kw in text_lower)
            if score > 0:
                scores[threat_type] = score
        
        if scores:
            result.threat_type = max(scores, key=scores.get)
        
        # Severity classification
        severity_indicators = {
            'critical': ['critical', 'severe', 'emergency', 'immediate'],
            'high': ['high', 'serious', 'significant', 'major'],
            'medium': ['medium', 'moderate', 'intermediate'],
            'low': ['low', 'minor', 'minimal']
        }
        
        for severity, indicators in severity_indicators.items():
            if any(ind in text_lower for ind in indicators):
                result.severity = severity
                break
        
        # Industry detection
        industries = {
            'defense': ['defense', 'military', 'dod', 'department of defense'],
            'finance': ['finance', 'bank', 'financial', 'investment'],
            'healthcare': ['healthcare', 'hospital', 'medical', 'pharmaceutical'],
            'energy': ['energy', 'electric', 'power', 'oil', 'gas', 'utility'],
            'government': ['government', 'agency', 'federal', 'state', 'local'],
            'technology': ['technology', 'software', 'hardware', 'tech'],
            'telecommunications': ['telecom', 'telecommunications', 'isp', 'carrier']
        }
        
        for industry, keywords in industries.items():
            if any(kw in text_lower for kw in keywords):
                result.industries.append(industry)
        
        result.industries = list(set(result.industries))
    
    def _generate_summary(self, text: str, result: ThreatIntelResult):
        """Generate executive summary"""
        if not self.summarizer_pipeline:
            return
        
        try:
            summary_result = self.summarizer_pipeline(
                text,
                max_length=100,
                min_length=30,
                do_sample=False
            )
            result.summary = summary_result[0]['summary_text']
        except Exception as e:
            logger.warning(f"Summarization failed: {e}")
    
    def _calculate_confidence(self, result: ThreatIntelResult) -> float:
        """Calculate extraction confidence score"""
        score = 0.0
        factors = 0
        
        # IOC extraction confidence
        if result.ip_addresses:
            score += 0.2
            factors += 1
        if result.domains:
            score += 0.2
            factors += 1
        if result.file_hashes:
            score += 0.3
            factors += 1
        
        # Entity extraction confidence
        if result.threat_actors:
            score += 0.3
            factors += 1
        if result.malware_families:
            score += 0.2
            factors += 1
        if result.cve_ids:
            score += 0.2
            factors += 1
        
        # Classification confidence
        if result.threat_type:
            score += 0.1
            factors += 1
        if result.severity:
            score += 0.1
            factors += 1
        
        if factors > 0:
            return min(1.0, score / max(factors, 1))
        return 0.0
    
    def batch_extract(self, texts: List[str]) -> List[ThreatIntelResult]:
        """Extract threat intel from multiple texts"""
        results = []
        for text in texts:
            result = self.extract(text)
            results.append(result)
        return results
    
    def export_json(self, result: ThreatIntelResult, filepath: str):
        """Export result to JSON file"""
        with open(filepath, 'w') as f:
            json.dump(result.to_dict(), f, indent=2)
        logger.info(f"💾 Exported to {filepath}")
    
    def export_stix(self, result: ThreatIntelResult, filepath: str):
        """Export result to STIX 2.1 format"""
        stix_obj = result.to_stix()
        with open(filepath, 'w') as f:
            json.dump(stix_obj, f, indent=2)
        logger.info(f"💾 Exported STIX to {filepath}")


def main():
    """Demo threat intel extraction"""
    print("""
╔═══════════════════════════════════════════════════════════════╗
║     🧠 KALIAGENT v5.0.0 - THREAT INTEL EXTRACTOR             ║
║                    Phase 14: Alpha 0.1.0                      ║
╚═══════════════════════════════════════════════════════════════╝

    """)
    
    if not TRANSFORMERS_AVAILABLE:
        print("⚠️  Transformers not available - using rule-based extraction only")
        print("   Install with: pip install transformers torch\n")
    
    # Sample threat report
    sample_text = """
    APT29 (CozyBear) has been observed conducting a spearphishing campaign 
    targeting the defense sector. The group deployed WellMess malware 
    exploiting CVE-2024-1234. Command and control servers were identified 
    at 203.0.113.50 and malicious-domain.com. File hash (SHA256): 
    a1b2c3d4e5f6789012345678901234567890123456789012345678901234abcd.
    
    The attack follows MITRE ATT&CK technique T1566 (Phishing). Severity 
    is rated as HIGH. Similar campaigns have targeted energy and 
    government sectors in North America and Europe.
    """
    
    print("📄 Sample Threat Report:")
    print("-" * 70)
    print(sample_text[:200] + "...")
    print("-" * 70)
    
    # Extract
    extractor = ThreatIntelExtractor()
    result = extractor.extract(sample_text)
    
    # Display results
    print("\n✅ Extracted Threat Intelligence:")
    print(f"   ID: {result.id}")
    print(f"   Confidence: {result.confidence:.0%}")
    
    print("\n📍 IOCs:")
    if result.ip_addresses:
        print(f"   IPs: {', '.join(result.ip_addresses)}")
    if result.domains:
        print(f"   Domains: {', '.join(result.domains)}")
    if result.file_hashes:
        for hash_type, hashes in result.file_hashes.items():
            print(f"   {hash_type.upper()}: {', '.join(hashes[:2])}...")
    
    print("\n👤 Threat Actors:")
    if result.threat_actors:
        print(f"   {', '.join(result.threat_actors)}")
    
    print("\n🦠 Malware:")
    if result.malware_families:
        print(f"   {', '.join(result.malware_families)}")
    
    print("\n🔖 CVEs:")
    if result.cve_ids:
        print(f"   {', '.join(result.cve_ids)}")
    
    print("\n🎯 MITRE ATT&CK:")
    if result.mitre_techniques:
        print(f"   {', '.join(result.mitre_techniques)}")
    
    print("\n📊 Classification:")
    print(f"   Type: {result.threat_type or 'Unknown'}")
    print(f"   Severity: {result.severity or 'Unknown'}")
    print(f"   Industries: {', '.join(result.industries) if result.industries else 'None'}")
    
    if result.summary:
        print("\n📝 Summary:")
        print(f"   {result.summary}")
    
    print("\n" + "="*70)
    print("✅ Threat Intel Extraction complete!")
    print("="*70)


if __name__ == "__main__":
    main()
