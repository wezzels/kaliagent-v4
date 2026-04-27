#!/usr/bin/env python3
"""
🎯 KaliAgent v4.4.0 - Phase 11: Automated Threat Hunting
Anomaly Detection Module

Statistical and behavioral anomaly detection:
- Baseline establishment
- Statistical outlier detection
- Behavioral profiling
- Time-series analysis
- User behavior analytics
- Network traffic anomalies

Author: KaliAgent Team
Started: April 27, 2026
Status: Alpha (0.1.0)
"""

import logging
import statistics
from typing import List, Dict, Optional
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from collections import defaultdict

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger('AnomalyDetection')


@dataclass
class Anomaly:
    """Detected anomaly"""
    id: str
    type: str
    severity: str
    description: str
    confidence: float
    baseline_value: float
    observed_value: float
    deviation: float
    affected_entity: str
    timestamp: datetime
    context: Dict = field(default_factory=dict)


class AnomalyDetector:
    """
    Anomaly Detection for Threat Hunting
    
    Techniques:
    - Statistical outlier detection (Z-score, IQR)
    - Baseline comparison
    - Behavioral profiling
    - Time-series analysis
    - User behavior analytics (UBA)
    """
    
    VERSION = "0.1.0"
    
    def __init__(self, baseline_window_hours: int = 168):
        """
        Initialize Anomaly Detector
        
        Args:
            baseline_window_hours: Hours of data for baseline (default: 1 week)
        """
        self.baseline_window = timedelta(hours=baseline_window_hours)
        self.baselines: Dict[str, Dict] = {}
        self.anomalies: List[Anomaly] = []
        
        logger.info(f"📊 Anomaly Detector v{self.VERSION}")
        logger.info(f"   Baseline window: {baseline_window_hours} hours")
    
    def establish_baseline(self, entity_id: str, metrics: List[Dict]) -> Dict:
        """
        Establish baseline for an entity
        
        Args:
            entity_id: Entity identifier
            metrics: Historical metrics data
            
        Returns:
            Baseline statistics
        """
        logger.info(f"📈 Establishing baseline for {entity_id}...")
        
        if not metrics:
            logger.warning("   No metrics data available")
            return {}
        
        # Extract numeric values
        values = [m.get('value', 0) for m in metrics if isinstance(m.get('value'), (int, float))]
        
        if len(values) < 10:
            logger.warning("   Insufficient data for baseline (need >= 10 samples)")
            return {}
        
        # Calculate statistics
        baseline = {
            'entity_id': entity_id,
            'mean': statistics.mean(values),
            'median': statistics.median(values),
            'stdev': statistics.stdev(values) if len(values) > 1 else 0,
            'min': min(values),
            'max': max(values),
            'q1': statistics.quantiles(values, n=4)[0] if len(values) >= 4 else 0,
            'q3': statistics.quantiles(values, n=4)[2] if len(values) >= 4 else 0,
            'sample_count': len(values),
            'established_at': datetime.now()
        }
        
        # Calculate IQR
        baseline['iqr'] = baseline['q3'] - baseline['q1']
        baseline['lower_bound'] = baseline['q1'] - 1.5 * baseline['iqr']
        baseline['upper_bound'] = baseline['q3'] + 1.5 * baseline['iqr']
        
        self.baselines[entity_id] = baseline
        
        logger.info(f"   Mean: {baseline['mean']:.2f}")
        logger.info(f"   Std Dev: {baseline['stdev']:.2f}")
        logger.info(f"   Range: [{baseline['min']}, {baseline['max']}]")
        
        return baseline
    
    def detect_zscore_anomaly(self, entity_id: str, value: float, 
                              threshold: float = 3.0) -> Optional[Anomaly]:
        """
        Detect anomaly using Z-score
        
        Args:
            entity_id: Entity identifier
            value: Observed value
            threshold: Z-score threshold (default: 3.0)
            
        Returns:
            Anomaly if detected
        """
        import uuid
        
        baseline = self.baselines.get(entity_id)
        
        if not baseline or baseline['stdev'] == 0:
            return None
        
        # Calculate Z-score
        zscore = abs(value - baseline['mean']) / baseline['stdev']
        
        if zscore > threshold:
            severity = 'critical' if zscore > 5 else 'high' if zscore > 4 else 'medium'
            
            anomaly = Anomaly(
                id=str(uuid.uuid4()),
                type='zscore_outlier',
                severity=severity,
                description=f'Z-score anomaly: {zscore:.2f} (threshold: {threshold})',
                confidence=min(1.0, zscore / 10),
                baseline_value=baseline['mean'],
                observed_value=value,
                deviation=zscore,
                affected_entity=entity_id,
                timestamp=datetime.now(),
                context={
                    'zscore': zscore,
                    'threshold': threshold,
                    'baseline_mean': baseline['mean'],
                    'baseline_stdev': baseline['stdev']
                }
            )
            
            self.anomalies.append(anomaly)
            logger.warning(f"⚠️  Z-score anomaly: {entity_id} (z={zscore:.2f})")
            
            return anomaly
        
        return None
    
    def detect_iqr_anomaly(self, entity_id: str, value: float) -> Optional[Anomaly]:
        """
        Detect anomaly using IQR method
        
        Args:
            entity_id: Entity identifier
            value: Observed value
            
        Returns:
            Anomaly if detected
        """
        import uuid
        
        baseline = self.baselines.get(entity_id)
        
        if not baseline:
            return None
        
        # Check if outside IQR bounds
        if value < baseline['lower_bound'] or value > baseline['upper_bound']:
            # Calculate how far outside
            if value < baseline['lower_bound']:
                deviation = (baseline['lower_bound'] - value) / baseline['iqr'] if baseline['iqr'] > 0 else 1
            else:
                deviation = (value - baseline['upper_bound']) / baseline['iqr'] if baseline['iqr'] > 0 else 1
            
            severity = 'high' if deviation > 2 else 'medium'
            
            anomaly = Anomaly(
                id=str(uuid.uuid4()),
                type='iqr_outlier',
                severity=severity,
                description=f'IQR outlier: value outside normal range',
                confidence=min(1.0, 0.5 + deviation * 0.2),
                baseline_value=baseline['median'],
                observed_value=value,
                deviation=deviation,
                affected_entity=entity_id,
                timestamp=datetime.now(),
                context={
                    'lower_bound': baseline['lower_bound'],
                    'upper_bound': baseline['upper_bound'],
                    'iqr': baseline['iqr']
                }
            )
            
            self.anomalies.append(anomaly)
            logger.warning(f"⚠️  IQR anomaly: {entity_id}")
            
            return anomaly
        
        return None
    
    def detect_rate_anomaly(self, entity_id: str, events: List[Dict], 
                           window_minutes: int = 5) -> Optional[Anomaly]:
        """
        Detect rate-based anomalies
        
        Args:
            entity_id: Entity identifier
            events: List of events with timestamps
            window_minutes: Analysis window
            
        Returns:
            Anomaly if detected
        """
        import uuid
        
        if not events:
            return None
        
        # Calculate current rate
        now = datetime.now()
        window_start = now - timedelta(minutes=window_minutes)
        
        recent_events = [
            e for e in events 
            if e.get('timestamp') and e['timestamp'] >= window_start
        ]
        
        current_rate = len(recent_events) / window_minutes
        
        # Get baseline rate
        baseline = self.baselines.get(f"{entity_id}_rate")
        
        if baseline and current_rate > baseline['mean'] * 2:
            severity = 'critical' if current_rate > baseline['mean'] * 5 else 'high'
            
            anomaly = Anomaly(
                id=str(uuid.uuid4()),
                type='rate_spike',
                severity=severity,
                description=f'Event rate spike: {current_rate:.1f}/min (baseline: {baseline["mean"]:.1f}/min)',
                confidence=min(1.0, current_rate / (baseline['mean'] * 10)),
                baseline_value=baseline['mean'],
                observed_value=current_rate,
                deviation=current_rate / baseline['mean'],
                affected_entity=entity_id,
                timestamp=datetime.now(),
                context={
                    'events_in_window': len(recent_events),
                    'window_minutes': window_minutes
                }
            )
            
            self.anomalies.append(anomaly)
            logger.warning(f"⚠️  Rate anomaly: {entity_id} ({current_rate:.1f}/min)")
            
            return anomaly
        
        return None
    
    def detect_behavioral_anomaly(self, user_id: str, activity: Dict) -> Optional[Anomaly]:
        """
        Detect user behavioral anomalies
        
        Args:
            user_id: User identifier
            activity: Activity data
            
        Returns:
            Anomaly if detected
        """
        import uuid
        
        # Check for unusual activity patterns
        anomalies = []
        
        # Unusual login time
        hour = activity.get('hour', 12)
        if hour < 6 or hour > 22:  # Outside business hours
            anomalies.append(('unusual_hour', 'Login outside business hours'))
        
        # Unusual location
        if activity.get('new_location'):
            anomalies.append(('new_location', 'Login from new geographic location'))
        
        # Unusual device
        if activity.get('new_device'):
            anomalies.append(('new_device', 'Login from new device'))
        
        # Unusual activity volume
        if activity.get('activity_count', 0) > 100:
            anomalies.append(('high_volume', 'Unusually high activity volume'))
        
        if anomalies:
            severity = 'high' if len(anomalies) >= 3 else 'medium' if len(anomalies) >= 2 else 'low'
            
            anomaly = Anomaly(
                id=str(uuid.uuid4()),
                type='behavioral',
                severity=severity,
                description=f'User behavioral anomaly: {len(anomalies)} indicators',
                confidence=0.6 + (len(anomalies) * 0.1),
                baseline_value=0,
                observed_value=len(anomalies),
                deviation=len(anomalies),
                affected_entity=user_id,
                timestamp=datetime.now(),
                context={
                    'indicators': [a[1] for a in anomalies],
                    'activity': activity
                }
            )
            
            self.anomalies.append(anomaly)
            logger.warning(f"⚠️  Behavioral anomaly: {user_id}")
            
            return anomaly
        
        return None
    
    def detect_network_anomaly(self, traffic_data: Dict) -> Optional[Anomaly]:
        """
        Detect network traffic anomalies
        
        Args:
            traffic_data: Network traffic data
            
        Returns:
            Anomaly if detected
        """
        import uuid
        
        # Check for unusual patterns
        indicators = []
        
        # Large data transfer
        if traffic_data.get('bytes_out', 0) > 1_000_000_000:  # > 1GB
            indicators.append('large_egress')
        
        # Unusual port
        if traffic_data.get('port') in [4444, 5555, 6666, 31337]:
            indicators.append('suspicious_port')
        
        # Unusual protocol
        if traffic_data.get('protocol', '').lower() in ['irc', 'tor']:
            indicators.append('suspicious_protocol')
        
        # High connection rate
        if traffic_data.get('connections_per_min', 0) > 100:
            indicators.append('high_connection_rate')
        
        if indicators:
            anomaly = Anomaly(
                id=str(uuid.uuid4()),
                type='network',
                severity='high',
                description=f'Network anomaly: {", ".join(indicators)}',
                confidence=0.7,
                baseline_value=0,
                observed_value=len(indicators),
                deviation=len(indicators),
                affected_entity=traffic_data.get('source_ip', 'unknown'),
                timestamp=datetime.now(),
                context={
                    'indicators': indicators,
                    'traffic_data': traffic_data
                }
            )
            
            self.anomalies.append(anomaly)
            logger.warning(f"⚠️  Network anomaly: {traffic_data.get('source_ip')}")
            
            return anomaly
        
        return None
    
    def get_anomaly_summary(self) -> Dict:
        """Get summary of detected anomalies"""
        by_type = defaultdict(int)
        by_severity = defaultdict(int)
        
        for anomaly in self.anomalies:
            by_type[anomaly.type] += 1
            by_severity[anomaly.severity] += 1
        
        return {
            'total_anomalies': len(self.anomalies),
            'by_type': dict(by_type),
            'by_severity': dict(by_severity),
            'entities_affected': len(set(a.affected_entity for a in self.anomalies))
        }
    
    def generate_report(self) -> str:
        """Generate anomaly detection report"""
        summary = self.get_anomaly_summary()
        
        report = []
        report.append("=" * 70)
        report.append("📊 ANOMALY DETECTION REPORT")
        report.append("=" * 70)
        report.append(f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        report.append(f"Total Anomalies: {summary['total_anomalies']}")
        report.append(f"Entities Affected: {summary['entities_affected']}")
        report.append("")
        
        report.append("BY SEVERITY:")
        for sev in ['critical', 'high', 'medium', 'low']:
            count = summary['by_severity'].get(sev, 0)
            if count > 0:
                report.append(f"  {sev.upper()}: {count}")
        report.append("")
        
        report.append("BY TYPE:")
        for type_, count in summary['by_type'].items():
            report.append(f"  {type_}: {count}")
        report.append("")
        
        if self.anomalies:
            report.append("TOP ANOMALIES:")
            report.append("-" * 70)
            
            # Sort by severity
            severity_order = {'critical': 0, 'high': 1, 'medium': 2, 'low': 3}
            sorted_anomalies = sorted(self.anomalies, key=lambda a: severity_order.get(a.severity, 4))
            
            for i, anomaly in enumerate(sorted_anomalies[:10], 1):
                report.append(f"\n{i}. [{anomaly.severity.upper()}] {anomaly.type}")
                report.append(f"   Entity: {anomaly.affected_entity}")
                report.append(f"   Description: {anomaly.description}")
                report.append(f"   Confidence: {anomaly.confidence:.0%}")
                report.append(f"   Baseline: {anomaly.baseline_value:.2f}")
                report.append(f"   Observed: {anomaly.observed_value:.2f}")
                report.append(f"   Deviation: {anomaly.deviation:.2f}x")
        
        report.append("")
        report.append("=" * 70)
        
        return "\n".join(report)


def main():
    """Main entry point"""
    print("""
╔═══════════════════════════════════════════════════════════════╗
║     📊 ANOMALY DETECTION MODULE                              ║
║                    Phase 11: Alpha 0.1.0                      ║
╚═══════════════════════════════════════════════════════════════╝

    """)
    
    detector = AnomalyDetector()
    
    # Establish baseline
    import random
    baseline_data = [
        {'value': random.randint(10, 20), 'timestamp': datetime.now() - timedelta(hours=i)}
        for i in range(100)
    ]
    
    detector.establish_baseline('user_logins', baseline_data)
    
    # Detect anomalies
    detector.detect_zscore_anomaly('user_logins', 100)  # Way outside normal
    detector.detect_iqr_anomaly('user_logins', 150)
    
    # Behavioral anomaly
    detector.detect_behavioral_anomaly('user123', {
        'hour': 3,
        'new_location': True,
        'new_device': True,
        'activity_count': 150
    })
    
    # Network anomaly
    detector.detect_network_anomaly({
        'source_ip': '192.168.1.100',
        'bytes_out': 2_000_000_000,
        'port': 4444,
        'connections_per_min': 150
    })
    
    print(detector.generate_report())


if __name__ == "__main__":
    main()
