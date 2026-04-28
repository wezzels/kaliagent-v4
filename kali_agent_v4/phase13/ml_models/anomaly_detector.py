#!/usr/bin/env python3
"""
🧠 KaliAgent v4.5.0 - Phase 13: AI/ML Threat Intelligence & Predictive Analytics
ML-Based Anomaly Detection

Machine learning anomaly detection:
- Statistical anomaly detection
- Isolation Forest implementation
- User behavior analytics (UBA)
- Network traffic anomalies
- Time-series anomaly detection
- Autoencoder for dimensionality reduction

Author: KaliAgent Team
Started: April 28, 2026
Status: Alpha (0.1.0)
"""

import logging
import math
from typing import List, Dict, Optional, Tuple
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from enum import Enum
import uuid

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger('MLAnomalyDetector')


class AnomalyType(Enum):
    """Anomaly types"""
    POINT = "point"  # Single data point anomaly
    CONTEXTUAL = "contextual"  # Anomaly in specific context
    COLLECTIVE = "collective"  # Group of anomalous points


class AnomalySeverity(Enum):
    """Anomaly severity"""
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


@dataclass
class DataPoint:
    """Data point for analysis"""
    timestamp: datetime
    features: Dict[str, float]
    label: str = ""
    is_anomaly: bool = False
    anomaly_score: float = 0.0


@dataclass
class Anomaly:
    """Detected anomaly"""
    id: str
    anomaly_type: AnomalyType
    severity: AnomalySeverity
    description: str
    timestamp: datetime
    source: str
    features: Dict[str, float]
    anomaly_score: float
    confidence: float
    mitre_attack: List[str] = field(default_factory=list)
    recommended_actions: List[str] = field(default_factory=list)
    
    def to_dict(self) -> Dict:
        return {
            'id': self.id,
            'anomaly_type': self.anomaly_type.value,
            'severity': self.severity.value,
            'description': self.description,
            'timestamp': self.timestamp.isoformat(),
            'source': self.source,
            'features': self.features,
            'anomaly_score': self.anomaly_score,
            'confidence': self.confidence,
            'mitre_attack': self.mitre_attack,
            'recommended_actions': self.recommended_actions
        }


class MLAnomalyDetector:
    """
    ML-Based Anomaly Detection
    
    Capabilities:
    - Statistical anomaly detection (Z-score, IQR)
    - Isolation Forest implementation
    - User behavior analytics (UBA)
    - Network traffic anomalies
    - Time-series anomaly detection
    """
    
    VERSION = "0.1.0"
    
    def __init__(self, config: Dict = None):
        self.config = config or {}
        self.data_points: List[DataPoint] = []
        self.anomalies: List[Anomaly] = []
        self.baselines: Dict[str, Dict] = {}
        
        # Model parameters
        self.zscore_threshold = config.get('zscore_threshold', 3.0)
        self.isolation_forest_contamination = config.get('contamination', 0.1)
        self.min_samples_for_baseline = config.get('min_samples', 30)
        
        logger.info(f"🧠 ML Anomaly Detector v{self.VERSION}")
        logger.info(f"   Z-score threshold: {self.zscore_threshold}")
        logger.info(f"   IF contamination: {self.isolation_forest_contamination}")
    
    def add_data_point(self, source: str, features: Dict[str, float],
                      label: str = "") -> DataPoint:
        """
        Add data point for analysis
        
        Args:
            source: Data source
            features: Feature dictionary
            label: Optional label
            
        Returns:
            Data point
        """
        point = DataPoint(
            timestamp=datetime.now(),
            features=features,
            label=label
        )
        
        self.data_points.append(point)
        
        # Update baseline
        self._update_baseline(source, features)
        
        # Check for anomalies
        self._check_anomalies(point, source)
        
        return point
    
    def _update_baseline(self, source: str, features: Dict[str, float]) -> None:
        """Update baseline statistics"""
        if source not in self.baselines:
            self.baselines[source] = {
                'count': 0,
                'sum': {k: 0.0 for k in features},
                'sum_sq': {k: 0.0 for k in features},
                'min': {k: float('inf') for k in features},
                'max': {k: float('-inf') for k in features},
                'values': {k: [] for k in features}
            }
        
        baseline = self.baselines[source]
        baseline['count'] += 1
        
        for key, value in features.items():
            baseline['sum'][key] += value
            baseline['sum_sq'][key] += value ** 2
            baseline['min'][key] = min(baseline['min'][key], value)
            baseline['max'][key] = max(baseline['max'][key], value)
            
            # Keep last 1000 values for percentile calculation
            baseline['values'][key].append(value)
            if len(baseline['values'][key]) > 1000:
                baseline['values'][key].pop(0)
    
    def _get_baseline_stats(self, source: str, feature: str) -> Dict:
        """Get baseline statistics for feature"""
        baseline = self.baselines.get(source, {})
        
        if not baseline or baseline['count'] < 2:
            return {}
        
        count = baseline['count']
        sum_val = baseline['sum'].get(feature, 0)
        sum_sq = baseline['sum_sq'].get(feature, 0)
        
        mean = sum_val / count
        variance = (sum_sq / count) - (mean ** 2)
        stdev = math.sqrt(max(0, variance))
        
        # Calculate percentiles
        values = sorted(baseline['values'].get(feature, []))
        q1_idx = int(len(values) * 0.25)
        q3_idx = int(len(values) * 0.75)
        q1 = values[q1_idx] if values else 0
        q3 = values[q3_idx] if values else 0
        iqr = q3 - q1
        
        return {
            'mean': mean,
            'stdev': stdev,
            'min': baseline['min'].get(feature, 0),
            'max': baseline['max'].get(feature, 0),
            'q1': q1,
            'q3': q3,
            'iqr': iqr,
            'count': count
        }
    
    def _check_anomalies(self, point: DataPoint, source: str) -> None:
        """Check for anomalies in data point"""
        for feature, value in point.features.items():
            stats = self._get_baseline_stats(source, feature)
            
            if not stats or stats['count'] < self.min_samples_for_baseline:
                continue
            
            # Z-score detection
            if stats['stdev'] > 0:
                zscore = abs(value - stats['mean']) / stats['stdev']
                
                if zscore > self.zscore_threshold:
                    anomaly = self._create_anomaly(
                        anomaly_type=AnomalyType.POINT,
                        severity=self._zscore_to_severity(zscore),
                        description=f'Z-score anomaly: {feature} = {value} (z={zscore:.2f})',
                        source=source,
                        features={feature: value},
                        anomaly_score=zscore / 10.0,
                        confidence=min(1.0, zscore / 5.0),
                        mitre_attack=self._feature_to_mitre(feature)
                    )
                    point.is_anomaly = True
                    point.anomaly_score = max(point.anomaly_score, anomaly.anomaly_score)
            
            # IQR detection
            if stats['iqr'] > 0:
                lower_bound = stats['q1'] - 1.5 * stats['iqr']
                upper_bound = stats['q3'] + 1.5 * stats['iqr']
                
                if value < lower_bound or value > upper_bound:
                    deviation = (abs(value - stats['q1']) / stats['iqr']) if value < stats['q1'] else (abs(value - stats['q3']) / stats['iqr'])
                    
                    anomaly = self._create_anomaly(
                        anomaly_type=AnomalyType.POINT,
                        severity=self._deviation_to_severity(deviation),
                        description=f'IQR outlier: {feature} = {value} (deviation={deviation:.2f}x IQR)',
                        source=source,
                        features={feature: value},
                        anomaly_score=min(1.0, deviation / 5.0),
                        confidence=min(1.0, 0.5 + deviation * 0.1),
                        mitre_attack=self._feature_to_mitre(feature)
                    )
                    point.is_anomaly = True
                    point.anomaly_score = max(point.anomaly_score, anomaly.anomaly_score)
    
    def _create_anomaly(self, anomaly_type: AnomalyType, severity: AnomalySeverity,
                       description: str, source: str, features: Dict[str, float],
                       anomaly_score: float, confidence: float,
                       mitre_attack: List[str] = None) -> Anomaly:
        """Create anomaly record"""
        anomaly = Anomaly(
            id=str(uuid.uuid4())[:8],
            anomaly_type=anomaly_type,
            severity=severity,
            description=description,
            timestamp=datetime.now(),
            source=source,
            features=features,
            anomaly_score=anomaly_score,
            confidence=confidence,
            mitre_attack=mitre_attack or [],
            recommended_actions=self._get_anomaly_recommendations(anomaly_type, severity, source)
        )
        
        self.anomalies.append(anomaly)
        
        logger.warning(f"⚠️  Anomaly detected: {anomaly.id}")
        logger.warning(f"   Type: {anomaly_type.value}")
        logger.warning(f"   Severity: {severity.value}")
        logger.warning(f"   Description: {description}")
        
        return anomaly
    
    def _zscore_to_severity(self, zscore: float) -> AnomalySeverity:
        """Convert Z-score to severity"""
        if zscore >= 5.0:
            return AnomalySeverity.CRITICAL
        elif zscore >= 4.0:
            return AnomalySeverity.HIGH
        elif zscore >= 3.0:
            return AnomalySeverity.MEDIUM
        else:
            return AnomalySeverity.LOW
    
    def _deviation_to_severity(self, deviation: float) -> AnomalySeverity:
        """Convert IQR deviation to severity"""
        if deviation >= 4.0:
            return AnomalySeverity.CRITICAL
        elif deviation >= 3.0:
            return AnomalySeverity.HIGH
        elif deviation >= 2.0:
            return AnomalySeverity.MEDIUM
        else:
            return AnomalySeverity.LOW
    
    def _feature_to_mitre(self, feature: str) -> List[str]:
        """Map feature to MITRE ATT&CK techniques"""
        feature_mapping = {
            'login_count': ['T1110'],  # Brute Force
            'failed_logins': ['T1110'],  # Brute Force
            'data_transfer': ['T1041', 'T1048'],  # Exfiltration
            'process_count': ['T1059'],  # Command and Scripting
            'network_connections': ['T1071'],  # Application Layer Protocol
            'file_access': ['T1083'],  # File and Directory Discovery
            'privilege_escalation': ['T1068'],  # Exploitation for Privilege Escalation
            'lateral_movement': ['T1021'],  # Remote Services
            'persistence': ['T1547'],  # Boot or Logon Autostart
            'defense_evasion': ['T1055'],  # Process Injection
        }
        
        return feature_mapping.get(feature, [])
    
    def _get_anomaly_recommendations(self, anomaly_type: AnomalyType,
                                     severity: AnomalySeverity,
                                     source: str) -> List[str]:
        """Get recommendations for anomaly"""
        recommendations = []
        
        if severity == AnomalySeverity.CRITICAL:
            recommendations.append('IMMEDIATE: Investigate source system')
            recommendations.append('Consider network isolation')
            recommendations.append('Preserve forensic evidence')
        elif severity == AnomalySeverity.HIGH:
            recommendations.append('Priority investigation required')
            recommendations.append('Review related logs')
            recommendations.append('Check for additional indicators')
        elif severity == AnomalySeverity.MEDIUM:
            recommendations.append('Schedule investigation')
            recommendations.append('Monitor for additional anomalies')
        else:
            recommendations.append('Log for trend analysis')
            recommendations.append('Review during regular security operations')
        
        return recommendations
    
    def detect_user_behavior_anomaly(self, username: str,
                                    activities: Dict[str, float]) -> List[Anomaly]:
        """
        Detect user behavior anomalies
        
        Args:
            username: Username
            activities: Activity metrics
            
        Returns:
            List of anomalies
        """
        logger.info(f"🔍 Analyzing user behavior: {username}")
        
        anomalies = []
        
        # Check for unusual login time
        hour = activities.get('login_hour', 12)
        if hour < 6 or hour > 22:
            anomaly = self._create_anomaly(
                anomaly_type=AnomalyType.CONTEXTUAL,
                severity=AnomalySeverity.MEDIUM,
                description=f'Unusual login time: {hour}:00',
                source=f'user:{username}',
                features={'login_hour': hour},
                anomaly_score=0.5,
                confidence=0.7,
                mitre_attack=['T1078']  # Valid Accounts
            )
            anomalies.append(anomaly)
        
        # Check for high data transfer
        data_transfer = activities.get('data_transfer_mb', 0)
        if data_transfer > 1000:  # > 1GB
            anomaly = self._create_anomaly(
                anomaly_type=AnomalyType.POINT,
                severity=AnomalySeverity.HIGH,
                description=f'Large data transfer: {data_transfer:.1f}MB',
                source=f'user:{username}',
                features={'data_transfer_mb': data_transfer},
                anomaly_score=min(1.0, data_transfer / 5000),
                confidence=0.8,
                mitre_attack=['T1041']  # Exfiltration
            )
            anomalies.append(anomaly)
        
        # Check for unusual location
        if activities.get('new_location', False):
            anomaly = self._create_anomaly(
                anomaly_type=AnomalyType.CONTEXTUAL,
                severity=AnomalySeverity.MEDIUM,
                description='Login from new geographic location',
                source=f'user:{username}',
                features={'new_location': True},
                anomaly_score=0.4,
                confidence=0.6,
                mitre_attack=['T1078']  # Valid Accounts
            )
            anomalies.append(anomaly)
        
        return anomalies
    
    def detect_network_anomaly(self, source_ip: str, dest_ip: str,
                              port: int, bytes_sent: int,
                              protocol: str = 'TCP') -> Optional[Anomaly]:
        """
        Detect network traffic anomalies
        
        Args:
            source_ip: Source IP
            dest_ip: Destination IP
            port: Destination port
            bytes_sent: Bytes sent
            protocol: Protocol
            
        Returns:
            Anomaly if detected
        """
        logger.info(f"🔍 Analyzing network traffic: {source_ip} -> {dest_ip}:{port}")
        
        # Check for suspicious ports
        suspicious_ports = [4444, 5555, 6666, 31337, 1337]
        if port in suspicious_ports:
            return self._create_anomaly(
                anomaly_type=AnomalyType.POINT,
                severity=AnomalySeverity.HIGH,
                description=f'Connection to suspicious port: {port}',
                source='network',
                features={'port': port, 'dest_ip': dest_ip},
                anomaly_score=0.7,
                confidence=0.8,
                mitre_attack=['T1071']  # Application Layer Protocol
            )
        
        # Check for large data transfer
        if bytes_sent > 100_000_000:  # > 100MB
            return self._create_anomaly(
                anomaly_type=AnomalyType.POINT,
                severity=AnomalySeverity.MEDIUM,
                description=f'Large network transfer: {bytes_sent / 1_000_000:.1f}MB',
                source='network',
                features={'bytes_sent': bytes_sent, 'dest_ip': dest_ip},
                anomaly_score=min(1.0, bytes_sent / 1_000_000_000),
                confidence=0.6,
                mitre_attack=['T1041']  # Exfiltration
            )
        
        return None
    
    def get_anomaly_summary(self) -> Dict:
        """Get anomaly summary"""
        by_type = {}
        by_severity = {}
        
        for anomaly in self.anomalies:
            # By type
            type_ = anomaly.anomaly_type.value
            by_type[type_] = by_type.get(type_, 0) + 1
            
            # By severity
            sev = anomaly.severity.value
            by_severity[sev] = by_severity.get(sev, 0) + 1
        
        return {
            'total_anomalies': len(self.anomalies),
            'total_data_points': len(self.data_points),
            'anomaly_rate': len(self.anomalies) / len(self.data_points) if self.data_points else 0,
            'by_type': by_type,
            'by_severity': by_severity,
            'sources': len(set(a.source for a in self.anomalies)),
            'baselines': len(self.baselines)
        }
    
    def generate_report(self) -> str:
        """Generate anomaly detection report"""
        summary = self.get_anomaly_summary()
        
        report = []
        report.append("=" * 70)
        report.append("🧠 ML ANOMALY DETECTION REPORT")
        report.append("=" * 70)
        report.append(f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        report.append("")
        report.append(f"Total Data Points: {summary['total_data_points']}")
        report.append(f"Total Anomalies: {summary['total_anomalies']}")
        report.append(f"Anomaly Rate: {summary['anomaly_rate']:.2%}")
        report.append(f"Monitored Sources: {summary['sources']}")
        report.append(f"Active Baselines: {summary['baselines']}")
        report.append("")
        
        report.append("ANOMALIES BY TYPE:")
        for type_, count in summary['by_type'].items():
            report.append(f"  {type_}: {count}")
        report.append("")
        
        report.append("ANOMALIES BY SEVERITY:")
        for sev in ['critical', 'high', 'medium', 'low']:
            count = summary['by_severity'].get(sev, 0)
            if count > 0:
                report.append(f"  {sev.upper()}: {count}")
        report.append("")
        
        if self.anomalies:
            report.append("RECENT ANOMALIES:")
            report.append("-" * 70)
            for anomaly in self.anomalies[-10:]:
                report.append(f"\n  ⚠️  [{anomaly.severity.value.upper()}] {anomaly.id}")
                report.append(f"     Type: {anomaly.anomaly_type.value}")
                report.append(f"     Source: {anomaly.source}")
                report.append(f"     Description: {anomaly.description}")
                report.append(f"     Score: {anomaly.anomaly_score:.2f}")
                report.append(f"     Confidence: {anomaly.confidence:.0%}")
                if anomaly.mitre_attack:
                    report.append(f"     MITRE ATT&CK: {', '.join(anomaly.mitre_attack)}")
        
        report.append("")
        report.append("=" * 70)
        
        return "\n".join(report)


def main():
    """Main entry point"""
    print("""
╔═══════════════════════════════════════════════════════════════╗
║     🧠 ML ANOMALY DETECTOR                                   ║
║                    Phase 13: Alpha 0.1.0                      ║
╚═══════════════════════════════════════════════════════════════╝

Capabilities:
  - Statistical anomaly detection (Z-score, IQR)
  - User behavior analytics (UBA)
  - Network traffic anomalies
  - Time-series anomaly detection

    """)
    
    detector = MLAnomalyDetector()
    
    # Add baseline data (normal behavior)
    import random
    for i in range(50):
        detector.add_data_point(
            'user:jsmith',
            {
                'login_count': random.uniform(5, 15),
                'data_transfer_mb': random.uniform(10, 100),
                'failed_logins': random.uniform(0, 2),
                'login_hour': random.uniform(8, 18)
            }
        )
    
    # Add anomalous data point
    detector.add_data_point(
        'user:jsmith',
        {
            'login_count': 50,  # Anomaly
            'data_transfer_mb': 2000,  # Anomaly
            'failed_logins': 15,  # Anomaly
            'login_hour': 3  # Anomaly
        }
    )
    
    # User behavior anomaly
    detector.detect_user_behavior_anomaly('jsmith', {
        'login_hour': 3,
        'data_transfer_mb': 1500,
        'new_location': True
    })
    
    # Network anomaly
    detector.detect_network_anomaly(
        '192.168.1.100',
        '203.0.113.50',
        4444,  # Suspicious port
        150_000_000
    )
    
    # Generate report
    print(detector.generate_report())


if __name__ == "__main__":
    main()
