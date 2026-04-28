# Phase 14: NLP Module Summary

## Overview

The NLP module provides automatic threat intelligence extraction and classification from unstructured text reports.

## Components

### 1. Threat Intel Extractor (`nlp/threat_intel_extractor.py`)

**Purpose:** Extract structured IOCs and threat intelligence from text

**What It Extracts:**

| Category | Entities | Count |
|----------|----------|-------|
| **IOCs** | IP addresses, domains, URLs, emails | Unlimited |
| **Hashes** | MD5, SHA1, SHA256 | Unlimited |
| **Threat Actors** | APT groups, cybercriminal orgs | 40+ known |
| **Malware** | Family names | 30+ known |
| **Vulnerabilities** | CVE IDs | Unlimited |
| **TTPs** | MITRE ATT&CK techniques | Unlimited |
| **Classification** | Threat type, severity, industries | Auto |

**Demo Results:**
```
Input: "APT29 used spearphishing to deploy WellMess malware 
        exploiting CVE-2024-1234..."

Output:
  ✅ IPs: 203.0.113.50
  ✅ Threat Actors: APT29, CozyBear
  ✅ Malware: WellMess, RAT
  ✅ CVE: CVE-2024-1234
  ✅ MITRE: T1566 (Phishing)
  ✅ Type: Phishing | Severity: HIGH
  ✅ Industries: Defense, Energy, Government
```

**Export Formats:**
- JSON
- STIX 2.1

---

### 2. Threat Classifier (`nlp/threat_classifier.py`)

**Purpose:** Multi-label classification of threat reports

**Classification Categories:**

| Category | Labels | Method |
|----------|--------|--------|
| **Threat Type** | ransomware, APT, phishing, malware, DDoS, insider, data breach, supply chain, zero-day | Zero-shot |
| **Severity** | critical, high, medium, low | Zero-shot |
| **Target Sector** | defense, finance, healthcare, energy, government, tech, telecom, manufacturing, retail, education | Zero-shot |
| **Attack Vector** | email, web, USB, network, social engineering, vulnerability, misconfiguration, physical | Zero-shot |

**How It Works:**
- Uses BART-large-MNLI for zero-shot classification
- No training data required!
- Multi-label predictions with confidence scores
- Rule-based fallback if transformers unavailable

**Example:**
```
Input: "Critical ransomware attack on healthcare. 
        Conti group encrypted patient records via phishing."

Output:
  Threat Type: ransomware attack (92%)
  Severity: critical severity (88%)
  Sector: healthcare sector (95%)
  Vector: email attack (87%)
```

---

## Installation

```bash
# Install transformers
pip install transformers accelerate torch

# Models download automatically on first use
```

---

## Usage

### Extract Threat Intel

```python
from phase14.nlp.threat_intel_extractor import ThreatIntelExtractor

extractor = ThreatIntelExtractor()
result = extractor.extract(threat_report_text)

# Access results
print(result.ip_addresses)      # ['203.0.113.50']
print(result.threat_actors)     # ['APT29']
print(result.malware_families)  # ['WellMess']
print(result.cve_ids)           # ['CVE-2024-1234']
print(result.severity)          # 'high'

# Export
extractor.export_json(result, 'intel.json')
extractor.export_stix(result, 'intel.stix')
```

### Classify Threat

```python
from phase14.nlp.threat_classifier import ThreatClassifier

classifier = ThreatClassifier()
result = classifier.classify(threat_report_text)

# Access results
print(result.primary_threat)    # 'ransomware attack'
print(result.primary_severity)  # 'critical severity'
print(result.primary_sector)    # 'healthcare sector'
print(result.confidence)        # 0.89

# Export
classifier.export_json(result, 'classification.json')
```

---

## Performance

| Model | Size | GPU | Load Time | Inference |
|-------|------|-----|-----------|-----------|
| **BERT-NER** | 440MB | ✅ | ~5s | ~50ms |
| **BART-Classifier** | 1.6GB | ✅ | ~10s | ~200ms |
| **Rule-based** | 0MB | N/A | Instant | ~5ms |

**Note:** Rule-based fallback works instantly even without model downloads.

---

## Integration Points

### Phase 11 (Threat Hunting)
- Auto-extract IOCs from hunting reports
- Classify detected threats by severity
- Generate STIX exports for SIEM

### Phase 13 (Threat Intelligence)
- Enrich threat intel with extracted IOCs
- Auto-categorize incoming reports
- Link threat actors to campaigns

### KaliAgent Orchestrator
```python
# Unified pipeline
extractor = ThreatIntelExtractor()
classifier = ThreatClassifier()

intel = extractor.extract(report)
classification = classifier.classify(report)

# Combine results
enriched_intel = {
    **intel.to_dict(),
    'classification': classification.to_dict()
}
```

---

## Known Threat Actors (40+)

```
APT29, APT28, APT41, APT37, APT38, APT32
Lazarus, Kimsuky, Turla, Sandworm
FancyBear, CozyBear, Equation Group
DarkSide, Conti, REvil, Ryuk
Emotet, TrickBot, Cobalt Group, FIN7
Carbanak, Silence, TA505, Wizard Spider, Evil Corp
DragonFly, MuddyWater, Charming Kitten, OilRig
```

## Known Malware Families (30+)

```
Emotet, TrickBot, QakBot, Dridex, Ryuk, Conti
REvil, DarkSide, Cobalt Strike, Mimikatz, Metasploit
WellMess, WellMail, Sunburst, Supernova, Triton
Stuxnet, NotPetya, WannaCry, BlackEnergy, Industroyer
Havex, BlackShades, RAT, AgentTesla, FormBook
NanoCore, njRAT, AsyncRAT, RemcosRAT, QuasarRAT
```

---

## Files

```
phase14/nlp/
├── threat_intel_extractor.py  (20 KB) - IOC extraction
├── threat_classifier.py       (13 KB) - Multi-label classification
└── __init__.py                - Module init
```

---

## Status

**Alpha (0.1.0)** - Core NLP functionality working

- [x] Threat Intel Extractor ✅
- [x] Threat Classifier ✅
- [ ] Summarization (optional enhancement)
- [ ] Relationship extraction (advanced)
- [ ] Multi-language support

---

*Created: April 28, 2026*  
*KaliAgent v5.0.0 - Phase 14 NLP Module*
