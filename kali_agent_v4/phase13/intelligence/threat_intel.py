#!/usr/bin/env python3
"""
🧠 KaliAgent v4.5.0 - Phase 13: AI/ML Threat Intelligence & Predictive Analytics
Threat Intelligence Correlation Engine

AI-powered threat intelligence:
- IOC correlation and enrichment
- Threat actor profiling
- Campaign tracking
- Intelligence sharing (STIX/TAXII)
- Automated IOC extraction
- Threat feed integration

Author: KaliAgent Team
Started: April 28, 2026
Status: Alpha (0.1.0)
"""

import logging
import json
import hashlib
from typing import List, Dict, Optional, Set
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from enum import Enum
import uuid

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger('ThreatIntel')


class ThreatType(Enum):
    """Threat types"""
    MALWARE = "malware"
    APT = "apt"
    RANSOMWARE = "ransomware"
    PHISHING = "phishing"
    EXPLOIT = "exploit"
    VULNERABILITY = "vulnerability"
    TTP = "ttp"


class ConfidenceLevel(Enum):
    """Confidence levels"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    VERY_HIGH = "very_high"


@dataclass
class Indicator:
    """Threat indicator (IOC)"""
    id: str
    type: str  # ip, domain, hash, url, email, file_path
    value: str
    threat_type: ThreatType
    confidence: ConfidenceLevel
    first_seen: datetime
    last_seen: datetime
    source: str
    tags: List[str] = field(default_factory=list)
    related_campaigns: List[str] = field(default_factory=list)
    threat_actors: List[str] = field(default_factory=list)
    mitre_attack: List[str] = field(default_factory=list)
    false_positive: bool = False
    revoked: bool = False
    
    def to_dict(self) -> Dict:
        return {
            'id': self.id,
            'type': self.type,
            'value': self.value,
            'threat_type': self.threat_type.value,
            'confidence': self.confidence.value,
            'first_seen': self.first_seen.isoformat(),
            'last_seen': self.last_seen.isoformat(),
            'source': self.source,
            'tags': self.tags,
            'related_campaigns': self.related_campaigns,
            'threat_actors': self.threat_actors,
            'mitre_attack': self.mitre_attack,
            'false_positive': self.false_positive,
            'revoked': self.revoked
        }


@dataclass
class ThreatActor:
    """Threat actor profile"""
    id: str
    name: str
    aliases: List[str] = field(default_factory=list)
    type: str = ""  # nation_state, cybercriminal, hacktivist, insider
    origin_country: str = ""
    motivation: str = ""
    sophistication: str = ""  # low, medium, high, very_high
    known_ttps: List[str] = field(default_factory=list)
    known_malware: List[str] = field(default_factory=list)
    targeted_industries: List[str] = field(default_factory=list)
    targeted_regions: List[str] = field(default_factory=list)
    first_seen: datetime = None
    last_seen: datetime = None
    description: str = ""
    
    def to_dict(self) -> Dict:
        return {
            'id': self.id,
            'name': self.name,
            'aliases': self.aliases,
            'type': self.type,
            'origin_country': self.origin_country,
            'motivation': self.motivation,
            'sophistication': self.sophistication,
            'known_ttps': self.known_ttps,
            'known_malware': self.known_malware,
            'targeted_industries': self.targeted_industries,
            'targeted_regions': self.targeted_regions,
            'first_seen': self.first_seen.isoformat() if self.first_seen else None,
            'last_seen': self.last_seen.isoformat() if self.last_seen else None,
            'description': self.description
        }


@dataclass
class Campaign:
    """Threat campaign"""
    id: str
    name: str
    threat_actor: str = ""
    start_date: datetime = None
    end_date: datetime = None
    status: str = "ongoing"  # ongoing, completed, dormant
    objectives: List[str] = field(default_factory=list)
    targeted_industries: List[str] = field(default_factory=list)
    targeted_regions: List[str] = field(default_factory=list)
    ttps: List[str] = field(default_factory=list)
    malware: List[str] = field(default_factory=list)
    indicators: List[str] = field(default_factory=list)
    description: str = ""
    
    def to_dict(self) -> Dict:
        return {
            'id': self.id,
            'name': self.name,
            'threat_actor': self.threat_actor,
            'start_date': self.start_date.isoformat() if self.start_date else None,
            'end_date': self.end_date.isoformat() if self.end_date else None,
            'status': self.status,
            'objectives': self.objectives,
            'targeted_industries': self.targeted_industries,
            'targeted_regions': self.targeted_regions,
            'ttps': self.ttps,
            'malware': self.malware,
            'indicators': self.indicators,
            'description': self.description
        }


class ThreatIntelligenceEngine:
    """
    Threat Intelligence Correlation Engine
    
    Capabilities:
    - IOC correlation and enrichment
    - Threat actor profiling
    - Campaign tracking
    - Intelligence sharing (STIX/TAXII)
    - Automated IOC extraction
    - Threat feed integration
    """
    
    VERSION = "0.1.0"
    
    # Built-in threat actor database (simplified)
    KNOWN_THREAT_ACTORS = {
        'APT29': ThreatActor(
            id='TA-001',
            name='APT29',
            aliases=['Cozy Bear', 'The Dukes', 'YTTRIUM'],
            type='nation_state',
            origin_country='Russia',
            motivation='espionage',
            sophistication='very_high',
            known_ttps=['T1566', 'T1059', 'T1071', 'T1027'],
            known_malware=['WellMess', 'WellMail', 'SUNBURST'],
            targeted_industries=['government', 'defense', 'healthcare', 'research'],
            targeted_regions=['North America', 'Europe'],
            description='Russian state-sponsored threat actor'
        ),
        'APT28': ThreatActor(
            id='TA-002',
            name='APT28',
            aliases=['Fancy Bear', 'Sofacy', 'SEDNIT'],
            type='nation_state',
            origin_country='Russia',
            motivation='espionage',
            sophistication='very_high',
            known_ttps=['T1566', 'T1059', 'T1003', 'T1005'],
            known_malware=['Zebrocy', 'XAgent', 'Sofacy'],
            targeted_industries=['government', 'military', 'media'],
            targeted_regions=['North America', 'Europe', 'Middle East'],
            description='Russian military intelligence threat actor'
        ),
        'Lazarus': ThreatActor(
            id='TA-003',
            name='Lazarus Group',
            aliases=['Hidden Cobra', 'Guardians of Peace'],
            type='nation_state',
            origin_country='North Korea',
            motivation='financial,espionage',
            sophistication='high',
            known_ttps=['T1566', 'T1059', 'T1486', 'T1195'],
            known_malware=['WannaCry', 'BLINDINGCAN', 'COPPERHEDGE'],
            targeted_industries=['finance', 'cryptocurrency', 'entertainment', 'defense'],
            targeted_regions=['Global'],
            description='North Korean state-sponsored threat actor'
        ),
    }
    
    def __init__(self, config: Dict = None):
        self.config = config or {}
        self.indicators: List[Indicator] = []
        self.threat_actors: List[ThreatActor] = list(self.KNOWN_THREAT_ACTORS.values())
        self.campaigns: List[Campaign] = []
        self.ioc_index: Dict[str, Indicator] = {}
        
        logger.info(f"🧠 Threat Intelligence Engine v{self.VERSION}")
        logger.info(f"   Known threat actors: {len(self.threat_actors)}")
    
    def add_indicator(self, indicator_type: str, value: str,
                     threat_type: ThreatType = None,
                     confidence: ConfidenceLevel = ConfidenceLevel.MEDIUM,
                     source: str = "manual",
                     tags: List[str] = None,
                     threat_actors: List[str] = None,
                     mitre_attack: List[str] = None) -> Indicator:
        """
        Add threat indicator
        
        Args:
            indicator_type: Type (ip, domain, hash, url, email)
            value: Indicator value
            threat_type: Type of threat
            confidence: Confidence level
            source: Source of intelligence
            tags: Tags for categorization
            threat_actors: Associated threat actors
            mitre_attack: MITRE ATT&CK techniques
            
        Returns:
            Created indicator
        """
        # Check if already exists
        existing = self.ioc_index.get(value)
        if existing:
            logger.info(f"Indicator already exists: {value}")
            return existing
        
        indicator = Indicator(
            id=str(uuid.uuid4())[:8],
            type=indicator_type,
            value=value,
            threat_type=threat_type or ThreatType.MALWARE,
            confidence=confidence,
            first_seen=datetime.now(),
            last_seen=datetime.now(),
            source=source,
            tags=tags or [],
            threat_actors=threat_actors or [],
            mitre_attack=mitre_attack or []
        )
        
        self.indicators.append(indicator)
        self.ioc_index[value] = indicator
        
        logger.info(f"✅ Indicator added: {indicator.id} ({indicator_type})")
        
        return indicator
    
    def lookup_ioc(self, value: str) -> Optional[Indicator]:
        """
        Lookup indicator
        
        Args:
            value: IOC value to lookup
            
        Returns:
            Indicator if found
        """
        indicator = self.ioc_index.get(value)
        
        if indicator:
            logger.info(f"🔍 IOC found: {indicator.id}")
            # Update last seen
            indicator.last_seen = datetime.now()
        else:
            logger.info(f"🔍 IOC not found: {value}")
        
        return indicator
    
    def correlate_indicators(self, indicators: List[str]) -> Dict:
        """
        Correlate multiple indicators
        
        Args:
            indicators: List of IOC values
            
        Returns:
            Correlation results
        """
        logger.info(f"🔗 Correlating {len(indicators)} indicators...")
        
        results = {
            'indicators': [],
            'common_threat_actors': set(),
            'common_campaigns': set(),
            'common_ttps': set(),
            'risk_score': 0.0,
            'assessment': ''
        }
        
        for ioc_value in indicators:
            indicator = self.lookup_ioc(ioc_value)
            if indicator:
                results['indicators'].append(indicator.to_dict())
                results['common_threat_actors'].update(indicator.threat_actors)
                results['common_campaigns'].update(indicator.related_campaigns)
                results['common_ttps'].update(indicator.mitre_attack)
        
        # Calculate risk score
        if results['indicators']:
            confidence_scores = {
                'low': 0.25,
                'medium': 0.5,
                'high': 0.75,
                'very_high': 1.0
            }
            
            total_confidence = sum(
                confidence_scores.get(i['confidence'], 0.5)
                for i in results['indicators']
            )
            
            avg_confidence = total_confidence / len(results['indicators'])
            
            # Boost score for common actors/campaigns
            actor_boost = min(0.2, len(results['common_threat_actors']) * 0.1)
            campaign_boost = min(0.2, len(results['common_campaigns']) * 0.1)
            
            results['risk_score'] = min(1.0, avg_confidence + actor_boost + campaign_boost)
            
            # Assessment
            if results['risk_score'] >= 0.8:
                results['assessment'] = 'CRITICAL - High confidence threat activity detected'
            elif results['risk_score'] >= 0.6:
                results['assessment'] = 'HIGH - Likely threat activity'
            elif results['risk_score'] >= 0.4:
                results['assessment'] = 'MEDIUM - Possible threat activity'
            else:
                results['assessment'] = 'LOW - Limited threat intelligence'
        
        # Convert sets to lists for JSON serialization
        results['common_threat_actors'] = list(results['common_threat_actors'])
        results['common_campaigns'] = list(results['common_campaigns'])
        results['common_ttps'] = list(results['common_ttps'])
        
        logger.info(f"   Risk Score: {results['risk_score']:.2f}")
        logger.info(f"   Assessment: {results['assessment']}")
        
        return results
    
    def enrich_ioc(self, value: str) -> Dict:
        """
        Enrich indicator with additional intelligence
        
        Args:
            value: IOC value
            
        Returns:
            Enriched intelligence
        """
        indicator = self.lookup_ioc(value)
        
        if not indicator:
            return {'error': 'Indicator not found'}
        
        enriched = {
            'indicator': indicator.to_dict(),
            'threat_actor_profiles': [],
            'related_campaigns': [],
            'related_indicators': [],
            'mitre_techniques': []
        }
        
        # Get threat actor profiles
        for actor_name in indicator.threat_actors:
            actor = next((ta for ta in self.threat_actors if ta.name == actor_name), None)
            if actor:
                enriched['threat_actor_profiles'].append(actor.to_dict())
        
        # Find related indicators (same threat actor)
        for ioc in self.indicators:
            if ioc.id != indicator.id:
                if set(ioc.threat_actors) & set(indicator.threat_actors):
                    enriched['related_indicators'].append(ioc.to_dict())
        
        # Get MITRE technique details
        enriched['mitre_techniques'] = indicator.mitre_attack
        
        logger.info(f"📊 IOC enriched: {indicator.id}")
        
        return enriched
    
    def extract_iocs(self, text: str) -> List[Dict]:
        """
        Extract IOCs from text
        
        Args:
            text: Text to extract from
            
        Returns:
            List of extracted IOCs
        """
        import re
        
        logger.info("🔍 Extracting IOCs from text...")
        
        extracted = {
            'ip_addresses': [],
            'domains': [],
            'urls': [],
            'email_addresses': [],
            'file_hashes': []
        }
        
        # IP addresses
        ip_pattern = r'\b(?:\d{1,3}\.){3}\d{1,3}\b'
        extracted['ip_addresses'] = re.findall(ip_pattern, text)
        
        # Domains
        domain_pattern = r'\b(?:[a-zA-Z0-9-]+\.)+[a-zA-Z]{2,}\b'
        extracted['domains'] = re.findall(domain_pattern, text)
        
        # URLs
        url_pattern = r'https?://[^\s]+'
        extracted['urls'] = re.findall(url_pattern, text)
        
        # Email addresses
        email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
        extracted['email_addresses'] = re.findall(email_pattern, text)
        
        # File hashes (MD5, SHA1, SHA256)
        md5_pattern = r'\b[a-fA-F0-9]{32}\b'
        sha1_pattern = r'\b[a-fA-F0-9]{40}\b'
        sha256_pattern = r'\b[a-fA-F0-9]{64}\b'
        
        extracted['file_hashes'] = {
            'md5': re.findall(md5_pattern, text),
            'sha1': re.findall(sha1_pattern, text),
            'sha256': re.findall(sha256_pattern, text)
        }
        
        total = (
            len(extracted['ip_addresses']) +
            len(extracted['domains']) +
            len(extracted['urls']) +
            len(extracted['email_addresses']) +
            len(extracted['file_hashes']['md5']) +
            len(extracted['file_hashes']['sha1']) +
            len(extracted['file_hashes']['sha256'])
        )
        
        logger.info(f"   Extracted {total} potential IOCs")
        
        return extracted
    
    def get_threat_actor(self, name: str) -> Optional[ThreatActor]:
        """Get threat actor profile"""
        actor = next((ta for ta in self.threat_actors if ta.name.lower() == name.lower()), None)
        
        if actor:
            logger.info(f"👤 Threat actor found: {actor.name}")
        else:
            logger.info(f"👤 Threat actor not found: {name}")
        
        return actor
    
    def create_campaign(self, name: str, threat_actor: str = "",
                       ttps: List[str] = None,
                       malware: List[str] = None) -> Campaign:
        """
        Create threat campaign
        
        Args:
            name: Campaign name
            threat_actor: Associated threat actor
            ttps: MITRE ATT&CK techniques
            malware: Associated malware
            
        Returns:
            Created campaign
        """
        campaign = Campaign(
            id=str(uuid.uuid4())[:8],
            name=name,
            threat_actor=threat_actor,
            start_date=datetime.now(),
            status='ongoing',
            ttps=ttps or [],
            malware=malware or []
        )
        
        self.campaigns.append(campaign)
        
        logger.info(f"📋 Campaign created: {campaign.id}")
        logger.info(f"   Name: {campaign.name}")
        logger.info(f"   Threat Actor: {threat_actor}")
        
        return campaign
    
    def export_stix(self, indicator_ids: List[str] = None) -> Dict:
        """
        Export intelligence as STIX 2.1
        
        Args:
            indicator_ids: Specific indicators to export
            
        Returns:
            STIX bundle
        """
        logger.info("📤 Exporting STIX 2.1 bundle...")
        
        stix_objects = []
        
        # Export indicators as STIX Indicators
        indicators_to_export = (
            [self.ioc_index.get(id) for id in indicator_ids]
            if indicator_ids else self.indicators
        )
        
        for indicator in indicators_to_export:
            if indicator and not indicator.revoked:
                stix_indicator = {
                    'type': 'indicator',
                    'spec_version': '2.1',
                    'id': f"indicator--{indicator.id}",
                    'created': indicator.first_seen.isoformat(),
                    'modified': indicator.last_seen.isoformat(),
                    'name': f"{indicator.type}: {indicator.value}",
                    'indicator_types': ['malicious-activity'],
                    'pattern': f"[{indicator.type}:value = '{indicator.value}']",
                    'pattern_type': 'stix',
                    'valid_from': indicator.first_seen.isoformat(),
                    'confidence': int({
                        'low': 25,
                        'medium': 50,
                        'high': 75,
                        'very_high': 95
                    }.get(indicator.confidence.value, 50))
                }
                stix_objects.append(stix_indicator)
        
        # Export threat actors as STIX Intrusion Sets
        for actor in self.threat_actors:
            stix_actor = {
                'type': 'intrusion-set',
                'spec_version': '2.1',
                'id': f"intrusion-set--{actor.id}",
                'created': actor.first_seen.isoformat() if actor.first_seen else datetime.now().isoformat(),
                'modified': actor.last_seen.isoformat() if actor.last_seen else datetime.now().isoformat(),
                'name': actor.name,
                'aliases': actor.aliases,
                'primary_motivation': actor.motivation,
                'sophistication': actor.sophistication,
                'resource_level': 'government',
                'goals': actor.targeted_industries
            }
            stix_objects.append(stix_actor)
        
        # Create STIX bundle
        bundle = {
            'type': 'bundle',
            'id': f"bundle--{uuid.uuid4()}",
            'objects': stix_objects
        }
        
        logger.info(f"   Exported {len(stix_objects)} STIX objects")
        
        return bundle
    
    def get_intelligence_summary(self) -> Dict:
        """Get intelligence summary"""
        by_type = {}
        by_confidence = {}
        
        for indicator in self.indicators:
            if not indicator.revoked and not indicator.false_positive:
                # By type
                if indicator.type not in by_type:
                    by_type[indicator.type] = 0
                by_type[indicator.type] += 1
                
                # By confidence
                conf = indicator.confidence.value
                if conf not in by_confidence:
                    by_confidence[conf] = 0
                by_confidence[conf] += 1
        
        return {
            'total_indicators': len(self.indicators),
            'active_indicators': sum(1 for i in self.indicators if not i.revoked and not i.false_positive),
            'by_type': by_type,
            'by_confidence': by_confidence,
            'threat_actors': len(self.threat_actors),
            'campaigns': len(self.campaigns)
        }
    
    def generate_report(self) -> str:
        """Generate threat intelligence report"""
        summary = self.get_intelligence_summary()
        
        report = []
        report.append("=" * 70)
        report.append("🧠 THREAT INTELLIGENCE REPORT")
        report.append("=" * 70)
        report.append(f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        report.append("")
        report.append(f"Total Indicators: {summary['total_indicators']}")
        report.append(f"Active Indicators: {summary['active_indicators']}")
        report.append(f"Threat Actors: {summary['threat_actors']}")
        report.append(f"Campaigns: {summary['campaigns']}")
        report.append("")
        
        report.append("INDICATORS BY TYPE:")
        for type_, count in summary['by_type'].items():
            report.append(f"  {type_}: {count}")
        report.append("")
        
        report.append("INDICATORS BY CONFIDENCE:")
        for conf, count in summary['by_confidence'].items():
            report.append(f"  {conf}: {count}")
        report.append("")
        
        if self.threat_actors:
            report.append("KNOWN THREAT ACTORS:")
            for actor in self.threat_actors[:5]:
                report.append(f"  • {actor.name} ({actor.type}) - {actor.origin_country}")
            report.append("")
        
        if self.campaigns:
            report.append("ACTIVE CAMPAIGNS:")
            for campaign in self.campaigns[-5:]:
                report.append(f"  • {campaign.name} ({campaign.status})")
            report.append("")
        
        report.append("=" * 70)
        
        return "\n".join(report)


def main():
    """Main entry point"""
    print("""
╔═══════════════════════════════════════════════════════════════╗
║     🧠 THREAT INTELLIGENCE ENGINE                            ║
║                    Phase 13: Alpha 0.1.0                      ║
╚═══════════════════════════════════════════════════════════════╝

Capabilities:
  - IOC correlation and enrichment
  - Threat actor profiling
  - Campaign tracking
  - STIX/TAXII support
  - Automated IOC extraction

    """)
    
    intel = ThreatIntelligenceEngine()
    
    # Add indicators
    intel.add_indicator('ip', '203.0.113.50', 
                       threat_type=ThreatType.MALWARE,
                       confidence=ConfidenceLevel.HIGH,
                       source='threat_feed',
                       threat_actors=['APT29'],
                       mitre_attack=['T1566', 'T1059'])
    
    intel.add_indicator('domain', 'malware-c2.example.com',
                       threat_type=ThreatType.MALWARE,
                       confidence=ConfidenceLevel.VERY_HIGH,
                       source='internal_analysis',
                       threat_actors=['APT29'],
                       mitre_attack=['T1071'])
    
    intel.add_indicator('hash', 'a1b2c3d4e5f6...',
                       threat_type=ThreatType.RANSOMWARE,
                       confidence=ConfidenceLevel.HIGH,
                       source='vendor_intel',
                       threat_actors=['Lazarus'])
    
    # Correlate indicators
    correlation = intel.correlate_indicators([
        '203.0.113.50',
        'malware-c2.example.com'
    ])
    print(f"\nCorrelation Risk Score: {correlation['risk_score']:.2f}")
    print(f"Assessment: {correlation['assessment']}")
    
    # Extract IOCs from text
    sample_text = """
    Malicious activity detected from IP 192.168.1.100 
    connecting to evil-domain.com and malware.evil.net.
    Contact: attacker@evil.com
    File hash: 5d41402abc4b2a76b9719d911017c592
    """
    extracted = intel.extract_iocs(sample_text)
    print(f"\nExtracted {sum(len(v) if isinstance(v, list) else sum(len(x) for x in v.values()) for v in extracted.values())} IOCs")
    
    # Generate report
    print("\n" + intel.generate_report())


if __name__ == "__main__":
    main()
