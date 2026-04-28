# 🧠 Phase 13: AI/ML Threat Intelligence & Predictive Analytics

**KaliAgent v4.5.0** | Status: **~50% Complete** | Started: April 28, 2026

---

## Overview

Phase 13 introduces AI/ML-powered threat intelligence, predictive analytics, and machine learning-based anomaly detection to KaliAgent. This phase enables proactive threat hunting, risk-based prioritization, and intelligent security operations.

### Key Capabilities

- **Threat Intelligence Correlation**: IOC enrichment, threat actor profiling, campaign tracking
- **Predictive Risk Scoring**: Asset risk, user behavior risk, attack likelihood prediction
- **ML Anomaly Detection**: Statistical methods, UBA, network anomalies, time-series analysis
- **STIX/TAXII Support**: Intelligence sharing and standardization
- **Automated IOC Extraction**: Pattern-based extraction from text/reports

---

## Architecture

```
phase13/
├── intelligence/
│   └── threat_intel.py        # Threat intelligence engine
├── predictive/
│   └── risk_scoring.py        # Risk assessment engine
├── ml_models/
│   └── anomaly_detector.py    # ML anomaly detection
└── automation/                 # Coming in 13.2
```

---

## Modules

### 1. Threat Intelligence Engine (`intelligence/threat_intel.py`)

**Size:** 25.4 KB | **Lines:** ~750

Threat intelligence correlation and enrichment.

**Features:**
- IOC management (IP, domain, hash, URL, email)
- Threat actor profiling (built-in database)
- Campaign tracking
- IOC correlation and enrichment
- Automated IOC extraction from text
- STIX 2.1 export
- Confidence scoring

**Built-in Threat Actors:**
- APT29 (Cozy Bear)
- APT28 (Fancy Bear)
- Lazarus Group

**Usage:**
```python
from phase13.intelligence.threat_intel import ThreatIntelligenceEngine, ThreatType, ConfidenceLevel

intel = ThreatIntelligenceEngine()

# Add indicators
intel.add_indicator('ip', '203.0.113.50',
                   threat_type=ThreatType.MALWARE,
                   confidence=ConfidenceLevel.HIGH,
                   threat_actors=['APT29'],
                   mitre_attack=['T1566', 'T1059'])

# Lookup IOC
indicator = intel.lookup_ioc('203.0.113.50')

# Correlate indicators
correlation = intel.correlate_indicators([
    '203.0.113.50',
    'malware-c2.example.com'
])
print(f"Risk Score: {correlation['risk_score']:.2f}")

# Extract IOCs from text
extracted = intel.extract_iocs(report_text)

# Export as STIX
stix_bundle = intel.export_stix()
```

### 2. Predictive Risk Engine (`predictive/risk_scoring.py`)

**Size:** 22.2 KB | **Lines:** ~650

ML-powered risk assessment and prediction.

**Features:**
- Asset risk scoring (weighted factors)
- User behavior risk scoring
- Attack likelihood prediction
- Vulnerability prioritization
- Risk trend analysis
- Compliance reporting

**Risk Factors:**
- Business criticality (30% weight)
- Network exposure (25% weight)
- Vulnerability score (25% weight)
- Threat exposure (20% weight)

**Usage:**
```python
from phase13.predictive.risk_scoring import PredictiveRiskEngine

engine = PredictiveRiskEngine()

# Register assets
engine.register_asset('Domain Controller', 'server',
                     criticality=10, exposure=6,
                     vulnerability_score=5, threat_exposure=8)

# Assess asset
assessment = engine.assess_asset(asset_id)

# User risk scoring
user = engine.register_user('admin_jsmith', 'IT', 'System Administrator')
engine.update_user_behavior(user.id,
                           behavior_anomalies=3,
                           policy_violations=1,
                           failed_logins=5)

# Predict attack likelihood
prediction = engine.predict_attack_likelihood(asset_id)
print(f"Likelihood: {prediction['likelihood']:.1f}%")
print(f"Time frame: {prediction['time_frame']}")
```

### 3. ML Anomaly Detector (`ml_models/anomaly_detector.py`)

**Size:** 21.5 KB | **Lines:** ~650

Machine learning-based anomaly detection.

**Features:**
- Statistical anomaly detection (Z-score, IQR)
- User behavior analytics (UBA)
- Network traffic anomaly detection
- Time-series anomaly detection
- Baseline learning
- MITRE ATT&CK mapping

**Detection Methods:**
- Z-score (threshold: 3.0σ)
- IQR (Interquartile Range)
- Behavioral baselines
- Pattern matching

**Usage:**
```python
from phase13.ml_models.anomaly_detector import MLAnomalyDetector

detector = MLAnomalyDetector()

# Add data points for baseline learning
detector.add_data_point('user:jsmith', {
    'login_count': 10,
    'data_transfer_mb': 50,
    'failed_logins': 1,
    'login_hour': 14
})

# Detect user behavior anomalies
anomalies = detector.detect_user_behavior_anomaly('jsmith', {
    'login_hour': 3,  # Unusual time
    'data_transfer_mb': 1500,  # Large transfer
    'new_location': True  # New geo
})

# Detect network anomalies
anomaly = detector.detect_network_anomaly(
    '192.168.1.100',
    '203.0.113.50',
    port=4444,  # Suspicious
    bytes_sent=150_000_000
)
```

---

## Threat Intelligence Workflow

```
┌─────────────────────────────────────────────────────────────────┐
│           THREAT INTELLIGENCE WORKFLOW                          │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  1. COLLECTION                                                  │
│     └─▶ Threat Feeds, Internal Analysis, OSINT, Sharing        │
│                                                                  │
│  2. PROCESSING                                                  │
│     └─▶ Normalization, Deduplication, Validation               │
│                                                                  │
│  3. ENRICHMENT                                                  │
│     └─▶ IOC Correlation, Threat Actor Mapping, Campaign Link   │
│                                                                  │
│  4. ANALYSIS                                                    │
│     └─▶ Pattern Recognition, TTP Mapping, Risk Assessment      │
│                                                                  │
│  5. DISSEMINATION                                               │
│     └─▶ STIX/TAXII Export, Reports, Alerts, API                │
│                                                                  │
│  6. INTEGRATION                                                 │
│     └─▶ SIEM, EDR, Firewall, Response Automation               │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

---

## Risk Scoring Methodology

### Asset Risk Formula

```
Risk Score = (Criticality × 0.30) + (Exposure × 0.25) + 
             (Vulnerability × 0.25) + (Threat × 0.20)
```

### Risk Levels

| Score Range | Level | Action Required |
|-------------|-------|-----------------|
| 8.0 - 10.0 | CRITICAL | Immediate executive attention |
| 6.0 - 7.9 | HIGH | 30-day risk reduction plan |
| 4.0 - 5.9 | MEDIUM | 90-day remediation |
| 2.0 - 3.9 | LOW | Monitor and maintain |
| 0.0 - 1.9 | MINIMAL | Accept risk |

### User Risk Factors

| Factor | Max Points | Description |
|--------|------------|-------------|
| Access Level | 3.0 | Based on role/privileges |
| Behavior Anomalies | 2.0 | Unusual activity patterns |
| Policy Violations | 2.0 | Security policy breaches |
| Failed Logins | 1.5 | Authentication failures |
| Privileged Actions | 1.5 | Admin/sensitive operations |

---

## MITRE ATT&CK Integration

Phase 13 maps intelligence to MITRE ATT&CK:

| Intelligence Type | Related Tactics | Example Techniques |
|-------------------|-----------------|-------------------|
| IOC Correlation | All | TTP-specific mapping |
| Threat Actors | All | Actor-specific TTPs |
| User Anomalies | Credential Access | T1078, T1110 |
| Network Anomalies | C2, Exfiltration | T1071, T1041 |
| Risk Prediction | All | Proactive defense |

---

## STIX/TAXII Support

### STIX 2.1 Objects

Phase 13 supports export of:
- **Indicators** (malicious-activity patterns)
- **Intrusion Sets** (threat actors)
- **Campaigns** (coordinated activity)
- **Malware** (malicious software)
- **Attack Patterns** (MITRE ATT&CK techniques)

### Export Example

```python
stix_bundle = intel.export_stix(indicator_ids=['abc123'])
# Returns STIX 2.1 bundle JSON
```

---

## Quick Start

### 1. Threat Intelligence Setup

```python
from phase13.intelligence.threat_intel import ThreatIntelligenceEngine

intel = ThreatIntelligenceEngine()

# Add threat indicators from multiple sources
intel.add_indicator('ip', '203.0.113.50', 
                   threat_type=ThreatType.MALWARE,
                   confidence=ConfidenceLevel.HIGH,
                   source='threat_feed',
                   threat_actors=['APT29'])

# Correlate with existing intelligence
correlation = intel.correlate_indicators(['203.0.113.50'])

# Get enriched intelligence
enriched = intel.enrich_ioc('203.0.113.50')
```

### 2. Risk Assessment

```python
from phase13.predictive.risk_scoring import PredictiveRiskEngine

engine = PredictiveRiskEngine()

# Register and assess assets
asset = engine.register_asset('Production DB', 'server',
                             criticality=9, exposure=5,
                             vulnerability_score=6, threat_exposure=7)

assessment = engine.assess_asset(asset.id)
print(f"Risk: {assessment.overall_risk:.2f} ({assessment.risk_level.value})")

# Get attack prediction
prediction = engine.predict_attack_likelihood(asset.id)
```

### 3. Anomaly Detection

```python
from phase13.ml_models.anomaly_detector import MLAnomalyDetector

detector = MLAnomalyDetector()

# Train baseline (30+ samples recommended)
for i in range(50):
    detector.add_data_point('user:jsmith', {
        'login_count': random.uniform(5, 15),
        'data_transfer_mb': random.uniform(10, 100)
    })

# Detect anomalies
anomalies = detector.detect_user_behavior_anomaly('jsmith', {
    'login_hour': 3,
    'data_transfer_mb': 2000
})
```

---

## Integration Points

### With Phase 11 (Threat Hunting)

```python
# Use threat intel to prioritize hunts
high_risk_indicators = [
    i for i in intel.indicators 
    if i.confidence == ConfidenceLevel.HIGH
]

# Hunt for specific IOCs
for indicator in high_risk_indicators:
    hunter.search_ioc(indicator.value)
```

### With Phase 12 (Incident Response)

```python
# Enrich incidents with threat intel
incident_iocs = ['203.0.113.50', 'malware.example.com']
correlation = intel.correlate_indicators(incident_iocs)

if correlation['risk_score'] >= 0.8:
    responder.escalate_incident(incident.id)
```

### With SIEM

```python
# Send enriched IOCs to SIEM
for indicator in intel.indicators:
    siem.send_alert({
        'type': 'ioc',
        'value': indicator.value,
        'confidence': indicator.confidence.value,
        'threat_actors': indicator.threat_actors
    })
```

---

## Statistics

| Metric | Value |
|--------|-------|
| Total Modules | 3 |
| Total Code | ~69 KB |
| Total Lines | ~2,050 |
| Built-in Threat Actors | 3 |
| Risk Factors | 4 (asset), 5 (user) |
| Detection Methods | 4 |

---

## Roadmap

### Sprint 13.1: Core Intelligence ✅
- [x] Threat intelligence engine
- [x] Predictive risk scoring
- [x] ML anomaly detection

### Sprint 13.2: Advanced ML (In Progress)
- [ ] Isolation Forest implementation
- [ ] Autoencoder for dimensionality reduction
- [ ] Clustering for campaign detection
- [ ] Time-series forecasting

### Sprint 13.3: Automation
- [ ] Automated threat intel ingestion
- [ ] Auto-remediation based on risk
- [ ] ML model training pipeline
- [ ] Feedback loop integration

### Sprint 13.4: Documentation
- [x] README_PHASE13.md
- [ ] API documentation
- [ ] ML model documentation
- [ ] Integration guide

---

## Safety & Ethics

⚠️ **IMPORTANT:** AI/ML security tools require responsible use.

- Validate ML predictions before taking action
- Maintain human oversight for critical decisions
- Regular model retraining and validation
- Avoid bias in training data
- Document all automated decisions
- Comply with privacy regulations

---

## References

- [MITRE ATT&CK](https://attack.mitre.org/)
- [STIX 2.1 Specification](https://oasis-open.github.io/cti-documentation/stix/intro)
- [TAXII 2.1 Specification](https://oasis-open.github.io/cti-documentation/taxii/intro)
- [NIST Risk Management Framework](https://csrc.nist.gov/projects/risk-management)
- [SANS Threat Intelligence](https://www.sans.org/cyber-security-courses/threat-intelligence-essentials/)

---

**Phase 13 Status:** ~50% Complete | **v4.5.0**
