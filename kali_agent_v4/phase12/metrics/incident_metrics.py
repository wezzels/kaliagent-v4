#!/usr/bin/env python3
"""
🚨 KaliAgent v4.4.0 - Phase 12: Automated Response & Remediation
Incident Metrics & Reporting Module

Metrics and reporting:
- MTTR/MTTD calculation
- Incident statistics
- Response effectiveness
- Compliance reporting (NIST, ISO 27001)
- Executive summaries
- Trend analysis

Author: KaliAgent Team
Started: April 28, 2026
Status: Alpha (0.1.0)
"""

import logging
from typing import List, Dict, Optional
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from enum import Enum

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger('IncidentMetrics')


class MetricPeriod(Enum):
    """Reporting period"""
    DAILY = "daily"
    WEEKLY = "weekly"
    MONTHLY = "monthly"
    QUARTERLY = "quarterly"
    YEARLY = "yearly"


@dataclass
class IncidentMetric:
    """Incident metric"""
    name: str
    value: float
    unit: str
    target: Optional[float] = None
    status: str = "ok"  # ok, warning, critical
    trend: str = "stable"  # improving, stable, degrading


@dataclass
class MetricsReport:
    """Metrics report"""
    period: MetricPeriod
    start_date: datetime
    end_date: datetime
    generated_at: datetime
    metrics: List[IncidentMetric] = field(default_factory=list)
    incidents_total: int = 0
    incidents_by_severity: Dict = field(default_factory=dict)
    incidents_by_type: Dict = field(default_factory=dict)
    mttd_hours: float = 0.0
    mttr_hours: float = 0.0
    containment_rate: float = 0.0
    remediation_rate: float = 0.0


class IncidentMetrics:
    """
    Incident Metrics & Reporting
    
    Capabilities:
    - MTTR/MTTD calculation
    - Incident statistics
    - Response effectiveness
    - Compliance reporting (NIST, ISO 27001)
    - Executive summaries
    - Trend analysis
    """
    
    VERSION = "0.1.0"
    
    # NIST SP 800-61 compliance metrics
    NIST_METRICS = [
        'mean_time_to_detect',
        'mean_time_to_respond',
        'mean_time_to_contain',
        'mean_time_to_recover',
        'incident_volume',
        'incident_severity_distribution',
        'containment_effectiveness',
        'remediation_effectiveness'
    ]
    
    # ISO 27001 compliance metrics
    ISO_METRICS = [
        'incident_response_procedure_compliance',
        'evidence_preservation_rate',
        'stakeholder_notification_compliance',
        'lessons_learned_completion',
        'continuous_improvement_actions'
    ]
    
    def __init__(self, config: Dict = None):
        self.config = config or {}
        self.incidents: List[Dict] = []
        self.metrics_history: List[MetricsReport] = []
        
        logger.info(f"📊 Incident Metrics v{self.VERSION}")
        logger.info(f"   NIST metrics: {len(self.NIST_METRICS)}")
        logger.info(f"   ISO 27001 metrics: {len(self.ISO_METRICS)}")
    
    def record_incident(self, incident: Dict):
        """
        Record incident for metrics
        
        Args:
            incident: Incident data
        """
        self.incidents.append(incident)
        logger.info(f"📝 Incident recorded: {incident.get('id', 'unknown')}")
    
    def calculate_mttd(self, incidents: List[Dict] = None) -> float:
        """
        Calculate Mean Time to Detect (MTTD)
        
        Args:
            incidents: List of incidents (or use all)
            
        Returns:
            MTTD in hours
        """
        if incidents is None:
            incidents = self.incidents
        
        if not incidents:
            return 0.0
        
        detection_times = []
        for incident in incidents:
            created = incident.get('created_at')
            detected = incident.get('detected_at', created)
            
            if created and detected:
                if isinstance(created, str):
                    created = datetime.fromisoformat(created)
                if isinstance(detected, str):
                    detected = datetime.fromisoformat(detected)
                
                delta = (detected - created).total_seconds() / 3600
                detection_times.append(abs(delta))
        
        if detection_times:
            mttd = sum(detection_times) / len(detection_times)
            logger.info(f"📊 MTTD: {mttd:.2f} hours")
            return mttd
        
        return 0.0
    
    def calculate_mttr(self, incidents: List[Dict] = None) -> float:
        """
        Calculate Mean Time to Respond/Resolve (MTTR)
        
        Args:
            incidents: List of incidents
            
        Returns:
            MTTR in hours
        """
        if incidents is None:
            incidents = self.incidents
        
        if not incidents:
            return 0.0
        
        resolution_times = []
        for incident in incidents:
            created = incident.get('created_at')
            resolved = incident.get('closed_at')
            
            if created and resolved:
                if isinstance(created, str):
                    created = datetime.fromisoformat(created)
                if isinstance(resolved, str):
                    resolved = datetime.fromisoformat(resolved)
                
                delta = (resolved - created).total_seconds() / 3600
                resolution_times.append(delta)
        
        if resolution_times:
            mttr = sum(resolution_times) / len(resolution_times)
            logger.info(f"📊 MTTR: {mttr:.2f} hours")
            return mttr
        
        return 0.0
    
    def calculate_containment_rate(self, incidents: List[Dict] = None) -> float:
        """
        Calculate containment effectiveness rate
        
        Args:
            incidents: List of incidents
            
        Returns:
            Containment rate (0-100%)
        """
        if incidents is None:
            incidents = self.incidents
        
        if not incidents:
            return 0.0
        
        contained = sum(1 for i in incidents if i.get('contained', False))
        rate = (contained / len(incidents)) * 100
        
        logger.info(f"📊 Containment Rate: {rate:.1f}%")
        return rate
    
    def calculate_remediation_rate(self, incidents: List[Dict] = None) -> float:
        """
        Calculate remediation effectiveness rate
        
        Args:
            incidents: List of incidents
            
        Returns:
            Remediation rate (0-100%)
        """
        if incidents is None:
            incidents = self.incidents
        
        if not incidents:
            return 0.0
        
        remediated = sum(1 for i in incidents if i.get('remediated', False))
        rate = (remediated / len(incidents)) * 100
        
        logger.info(f"📊 Remediation Rate: {rate:.1f}%")
        return rate
    
    def generate_metrics_report(self, period: MetricPeriod = MetricPeriod.MONTHLY,
                                days: int = 30) -> MetricsReport:
        """
        Generate comprehensive metrics report
        
        Args:
            period: Reporting period
            days: Number of days to include
            
        Returns:
            Metrics report
        """
        logger.info(f"📊 Generating {period.value} metrics report...")
        
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days)
        
        # Filter incidents by period
        period_incidents = []
        for incident in self.incidents:
            created = incident.get('created_at')
            if created:
                if isinstance(created, str):
                    created = datetime.fromisoformat(created)
                if start_date <= created <= end_date:
                    period_incidents.append(incident)
        
        # Calculate metrics
        mttd = self.calculate_mttd(period_incidents)
        mttr = self.calculate_mttr(period_incidents)
        containment = self.calculate_containment_rate(period_incidents)
        remediation = self.calculate_remediation_rate(period_incidents)
        
        # Incidents by severity
        by_severity = {}
        for incident in period_incidents:
            severity = incident.get('severity', 'unknown')
            by_severity[severity] = by_severity.get(severity, 0) + 1
        
        # Incidents by type
        by_type = {}
        for incident in period_incidents:
            type_ = incident.get('incident_type', 'unknown')
            by_type[type_] = by_type.get(type_, 0) + 1
        
        # Build metrics list
        metrics = [
            IncidentMetric(
                name='Mean Time to Detect',
                value=mttd,
                unit='hours',
                target=4.0,
                status='ok' if mttd <= 4 else 'warning' if mttd <= 8 else 'critical',
                trend='stable'
            ),
            IncidentMetric(
                name='Mean Time to Respond',
                value=mttr,
                unit='hours',
                target=24.0,
                status='ok' if mttr <= 24 else 'warning' if mttr <= 48 else 'critical',
                trend='stable'
            ),
            IncidentMetric(
                name='Containment Rate',
                value=containment,
                unit='percent',
                target=90.0,
                status='ok' if containment >= 90 else 'warning' if containment >= 75 else 'critical',
                trend='stable'
            ),
            IncidentMetric(
                name='Remediation Rate',
                value=remediation,
                unit='percent',
                target=95.0,
                status='ok' if remediation >= 95 else 'warning' if remediation >= 85 else 'critical',
                trend='stable'
            ),
        ]
        
        report = MetricsReport(
            period=period,
            start_date=start_date,
            end_date=end_date,
            generated_at=datetime.now(),
            metrics=metrics,
            incidents_total=len(period_incidents),
            incidents_by_severity=by_severity,
            incidents_by_type=by_type,
            mttd_hours=mttd,
            mttr_hours=mttr,
            containment_rate=containment,
            remediation_rate=remediation
        )
        
        self.metrics_history.append(report)
        
        logger.info(f"   Incidents: {len(period_incidents)}")
        logger.info(f"   MTTD: {mttd:.2f}h")
        logger.info(f"   MTTR: {mttr:.2f}h")
        
        return report
    
    def generate_nist_compliance_report(self) -> Dict:
        """
        Generate NIST SP 800-61 compliance report
        
        Returns:
            Compliance report
        """
        logger.info("📋 Generating NIST SP 800-61 compliance report...")
        
        report = {
            'framework': 'NIST SP 800-61',
            'generated_at': datetime.now().isoformat(),
            'metrics': {},
            'compliance_score': 0.0
        }
        
        # Calculate each NIST metric
        for metric in self.NIST_METRICS:
            if metric == 'mean_time_to_detect':
                value = self.calculate_mttd()
                report['metrics'][metric] = {'value': value, 'unit': 'hours'}
            elif metric == 'mean_time_to_respond':
                value = self.calculate_mttr()
                report['metrics'][metric] = {'value': value, 'unit': 'hours'}
            elif metric == 'mean_time_to_contain':
                value = self.calculate_containment_rate()
                report['metrics'][metric] = {'value': value, 'unit': 'percent'}
            elif metric == 'mean_time_to_recover':
                value = self.calculate_mttr()  # Simplified
                report['metrics'][metric] = {'value': value, 'unit': 'hours'}
            elif metric == 'incident_volume':
                value = len(self.incidents)
                report['metrics'][metric] = {'value': value, 'unit': 'count'}
            # ... other metrics
        
        # Calculate compliance score (simplified)
        compliant = sum(1 for m in report['metrics'].values() if m['value'] > 0)
        report['compliance_score'] = (compliant / len(self.NIST_METRICS)) * 100
        
        logger.info(f"   Compliance Score: {report['compliance_score']:.1f}%")
        
        return report
    
    def generate_executive_summary(self, period: MetricPeriod = MetricPeriod.MONTHLY) -> str:
        """
        Generate executive summary
        
        Args:
            period: Reporting period
            
        Returns:
            Executive summary text
        """
        report = self.generate_metrics_report(period)
        
        summary = []
        summary.append("=" * 70)
        summary.append("📊 INCIDENT RESPONSE - EXECUTIVE SUMMARY")
        summary.append("=" * 70)
        summary.append(f"Period: {report.start_date.strftime('%Y-%m-%d')} to {report.end_date.strftime('%Y-%m-%d')}")
        summary.append(f"Generated: {report.generated_at.strftime('%Y-%m-%d %H:%M:%S')}")
        summary.append("")
        
        # Key highlights
        summary.append("KEY HIGHLIGHTS:")
        summary.append("-" * 70)
        summary.append(f"  • Total Incidents: {report.incidents_total}")
        summary.append(f"  • Mean Time to Detect: {report.mttd_hours:.2f} hours")
        summary.append(f"  • Mean Time to Respond: {report.mttr_hours:.2f} hours")
        summary.append(f"  • Containment Rate: {report.containment_rate:.1f}%")
        summary.append(f"  • Remediation Rate: {report.remediation_rate:.1f}%")
        summary.append("")
        
        # Severity breakdown
        if report.incidents_by_severity:
            summary.append("INCIDENTS BY SEVERITY:")
            for severity, count in sorted(report.incidents_by_severity.items()):
                summary.append(f"  • {severity.upper()}: {count}")
            summary.append("")
        
        # Top incident types
        if report.incidents_by_type:
            summary.append("INCIDENTS BY TYPE:")
            sorted_types = sorted(report.incidents_by_type.items(), key=lambda x: x[1], reverse=True)
            for type_, count in sorted_types[:5]:
                summary.append(f"  • {type_}: {count}")
            summary.append("")
        
        # Recommendations
        summary.append("RECOMMENDATIONS:")
        if report.mttd_hours > 4:
            summary.append("  • Improve detection capabilities to reduce MTTD")
        if report.mttr_hours > 24:
            summary.append("  • Streamline response procedures to reduce MTTR")
        if report.containment_rate < 90:
            summary.append("  • Enhance containment procedures")
        if report.remediation_rate < 95:
            summary.append("  • Improve remediation effectiveness")
        
        if all([
            report.mttd_hours <= 4,
            report.mttr_hours <= 24,
            report.containment_rate >= 90,
            report.remediation_rate >= 95
        ]):
            summary.append("  • All metrics within target - maintain current procedures")
        
        summary.append("")
        summary.append("=" * 70)
        
        return "\n".join(summary)
    
    def generate_full_report(self) -> str:
        """Generate full metrics report"""
        report = self.generate_metrics_report()
        
        output = []
        output.append("=" * 70)
        output.append("📊 INCIDENT METRICS REPORT")
        output.append("=" * 70)
        output.append(f"Period: {report.start_date} to {report.end_date}")
        output.append(f"Generated: {report.generated_at}")
        output.append("")
        
        output.append("METRICS:")
        output.append("-" * 70)
        for metric in report.metrics:
            status_icon = '✅' if metric.status == 'ok' else '⚠️' if metric.status == 'warning' else '❌'
            target_str = f" (target: {metric.target}{metric.unit})" if metric.target else ""
            output.append(f"{status_icon} {metric.name}: {metric.value}{metric.unit}{target_str}")
        output.append("")
        
        output.append(f"Total Incidents: {report.incidents_total}")
        output.append("")
        
        if report.incidents_by_severity:
            output.append("By Severity:")
            for sev, count in report.incidents_by_severity.items():
                output.append(f"  {sev}: {count}")
            output.append("")
        
        if report.incidents_by_type:
            output.append("By Type:")
            for type_, count in report.incidents_by_type.items():
                output.append(f"  {type_}: {count}")
        
        output.append("")
        output.append("=" * 70)
        
        return "\n".join(output)


def main():
    """Main entry point"""
    print("""
╔═══════════════════════════════════════════════════════════════╗
║     📊 INCIDENT METRICS & REPORTING                          ║
║                    Phase 12: Alpha 0.1.0                      ║
╚═══════════════════════════════════════════════════════════════╝

Capabilities:
  - MTTR/MTTD calculation
  - Incident statistics
  - Compliance reporting (NIST, ISO 27001)
  - Executive summaries

    """)
    
    metrics = IncidentMetrics()
    
    # Record simulated incidents
    from datetime import timedelta
    import random
    
    severities = ['critical', 'high', 'medium', 'low']
    types = ['malware', 'unauthorized_access', 'phishing', 'data_breach']
    
    for i in range(20):
        created = datetime.now() - timedelta(days=random.randint(0, 30))
        detected = created + timedelta(hours=random.uniform(0.5, 8))
        closed = detected + timedelta(hours=random.uniform(2, 48))
        
        metrics.record_incident({
            'id': f'INC-{i+1:03d}',
            'severity': random.choice(severities),
            'incident_type': random.choice(types),
            'created_at': created.isoformat(),
            'detected_at': detected.isoformat(),
            'closed_at': closed.isoformat(),
            'contained': random.random() > 0.2,
            'remediated': random.random() > 0.1
        })
    
    # Generate reports
    print(metrics.generate_executive_summary())
    print("\n" + metrics.generate_full_report())


if __name__ == "__main__":
    main()
