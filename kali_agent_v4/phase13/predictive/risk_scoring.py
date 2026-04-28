#!/usr/bin/env python3
"""
🧠 KaliAgent v4.5.0 - Phase 13: AI/ML Threat Intelligence & Predictive Analytics
Predictive Risk Scoring Engine

ML-powered risk assessment:
- Asset risk scoring
- User behavior risk scoring
- Threat likelihood prediction
- Vulnerability prioritization
- Attack surface analysis
- Risk trend analysis

Author: KaliAgent Team
Started: April 28, 2026
Status: Alpha (0.1.0)
"""

import logging
from typing import List, Dict, Optional
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from enum import Enum
import uuid
import math

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger('RiskScoring')


class RiskLevel(Enum):
    """Risk levels"""
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    MINIMAL = "minimal"


@dataclass
class Asset:
    """IT Asset"""
    id: str
    name: str
    type: str  # server, workstation, network, data, application
    criticality: float  # 0-10
    exposure: float  # 0-10
    vulnerability_score: float  # 0-10
    threat_exposure: float  # 0-10
    risk_score: float = 0.0
    risk_level: RiskLevel = RiskLevel.LOW
    tags: List[str] = field(default_factory=list)
    
    def to_dict(self) -> Dict:
        return {
            'id': self.id,
            'name': self.name,
            'type': self.type,
            'criticality': self.criticality,
            'exposure': self.exposure,
            'vulnerability_score': self.vulnerability_score,
            'threat_exposure': self.threat_exposure,
            'risk_score': self.risk_score,
            'risk_level': self.risk_level.value,
            'tags': self.tags
        }


@dataclass
class UserRisk:
    """User risk profile"""
    id: str
    username: str
    department: str = ""
    role: str = ""
    access_level: float = 0.0  # 0-10
    behavior_anomalies: int = 0
    policy_violations: int = 0
    failed_logins: int = 0
    privileged_actions: int = 0
    risk_score: float = 0.0
    risk_level: RiskLevel = RiskLevel.LOW
    
    def to_dict(self) -> Dict:
        return {
            'id': self.id,
            'username': self.username,
            'department': self.department,
            'role': self.role,
            'access_level': self.access_level,
            'behavior_anomalies': self.behavior_anomalies,
            'policy_violations': self.policy_violations,
            'failed_logins': self.failed_logins,
            'privileged_actions': self.privileged_actions,
            'risk_score': self.risk_score,
            'risk_level': self.risk_level.value
        }


@dataclass
class RiskAssessment:
    """Risk assessment result"""
    id: str
    asset_id: str
    assessment_date: datetime
    overall_risk: float
    risk_level: RiskLevel
    risk_factors: Dict = field(default_factory=dict)
    recommendations: List[str] = field(default_factory=list)
    trend: str = "stable"  # improving, stable, degrading
    
    def to_dict(self) -> Dict:
        return {
            'id': self.id,
            'asset_id': self.asset_id,
            'assessment_date': self.assessment_date.isoformat(),
            'overall_risk': self.overall_risk,
            'risk_level': self.risk_level.value,
            'risk_factors': self.risk_factors,
            'recommendations': self.recommendations,
            'trend': self.trend
        }


class PredictiveRiskEngine:
    """
    Predictive Risk Scoring Engine
    
    Capabilities:
    - Asset risk scoring
    - User behavior risk scoring
    - Threat likelihood prediction
    - Vulnerability prioritization
    - Attack surface analysis
    - Risk trend analysis
    """
    
    VERSION = "0.1.0"
    
    # Risk calculation weights
    WEIGHTS = {
        'criticality': 0.30,
        'exposure': 0.25,
        'vulnerability': 0.25,
        'threat': 0.20
    }
    
    # Risk thresholds
    THRESHOLDS = {
        'critical': 8.0,
        'high': 6.0,
        'medium': 4.0,
        'low': 2.0
    }
    
    def __init__(self, config: Dict = None):
        self.config = config or {}
        self.assets: List[Asset] = []
        self.user_risks: List[UserRisk] = []
        self.assessments: List[RiskAssessment] = []
        
        logger.info(f"🧠 Predictive Risk Engine v{self.VERSION}")
        logger.info(f"   Risk weights: {self.WEIGHTS}")
    
    def register_asset(self, name: str, asset_type: str,
                      criticality: float = 5.0,
                      exposure: float = 5.0,
                      vulnerability_score: float = 5.0,
                      threat_exposure: float = 5.0,
                      tags: List[str] = None) -> Asset:
        """
        Register asset for risk scoring
        
        Args:
            name: Asset name
            asset_type: Type of asset
            criticality: Business criticality (0-10)
            exposure: Network exposure (0-10)
            vulnerability_score: Vulnerability level (0-10)
            threat_exposure: Threat exposure (0-10)
            tags: Asset tags
            
        Returns:
            Registered asset
        """
        # Normalize scores to 0-10
        criticality = max(0, min(10, criticality))
        exposure = max(0, min(10, exposure))
        vulnerability_score = max(0, min(10, vulnerability_score))
        threat_exposure = max(0, min(10, threat_exposure))
        
        asset = Asset(
            id=str(uuid.uuid4())[:8],
            name=name,
            type=asset_type,
            criticality=criticality,
            exposure=exposure,
            vulnerability_score=vulnerability_score,
            threat_exposure=threat_exposure,
            tags=tags or []
        )
        
        # Calculate initial risk score
        self._calculate_asset_risk(asset)
        
        self.assets.append(asset)
        
        logger.info(f"✅ Asset registered: {asset.id}")
        logger.info(f"   Name: {asset.name}")
        logger.info(f"   Risk Level: {asset.risk_level.value}")
        logger.info(f"   Risk Score: {asset.risk_score:.2f}")
        
        return asset
    
    def _calculate_asset_risk(self, asset: Asset) -> None:
        """Calculate asset risk score"""
        # Weighted risk calculation
        risk_score = (
            asset.criticality * self.WEIGHTS['criticality'] +
            asset.exposure * self.WEIGHTS['exposure'] +
            asset.vulnerability_score * self.WEIGHTS['vulnerability'] +
            asset.threat_exposure * self.WEIGHTS['threat']
        )
        
        asset.risk_score = round(risk_score, 2)
        
        # Determine risk level
        if risk_score >= self.THRESHOLDS['critical']:
            asset.risk_level = RiskLevel.CRITICAL
        elif risk_score >= self.THRESHOLDS['high']:
            asset.risk_level = RiskLevel.HIGH
        elif risk_score >= self.THRESHOLDS['medium']:
            asset.risk_level = RiskLevel.MEDIUM
        elif risk_score >= self.THRESHOLDS['low']:
            asset.risk_level = RiskLevel.LOW
        else:
            asset.risk_level = RiskLevel.MINIMAL
    
    def assess_asset(self, asset_id: str) -> RiskAssessment:
        """
        Perform risk assessment on asset
        
        Args:
            asset_id: Asset ID
            
        Returns:
            Risk assessment
        """
        asset = next((a for a in self.assets if a.id == asset_id), None)
        
        if not asset:
            logger.error(f"Asset not found: {asset_id}")
            return None
        
        # Recalculate risk
        self._calculate_asset_risk(asset)
        
        # Generate risk factors
        risk_factors = {
            'criticality': {
                'score': asset.criticality,
                'weight': self.WEIGHTS['criticality'],
                'contribution': asset.criticality * self.WEIGHTS['criticality']
            },
            'exposure': {
                'score': asset.exposure,
                'weight': self.WEIGHTS['exposure'],
                'contribution': asset.exposure * self.WEIGHTS['exposure']
            },
            'vulnerability': {
                'score': asset.vulnerability_score,
                'weight': self.WEIGHTS['vulnerability'],
                'contribution': asset.vulnerability_score * self.WEIGHTS['vulnerability']
            },
            'threat': {
                'score': asset.threat_exposure,
                'weight': self.WEIGHTS['threat'],
                'contribution': asset.threat_exposure * self.WEIGHTS['threat']
            }
        }
        
        # Generate recommendations
        recommendations = []
        
        if asset.criticality >= 8:
            recommendations.append('Implement enhanced monitoring for critical asset')
        if asset.exposure >= 7:
            recommendations.append('Reduce network exposure through segmentation')
        if asset.vulnerability_score >= 7:
            recommendations.append('Prioritize vulnerability remediation')
        if asset.threat_exposure >= 7:
            recommendations.append('Implement additional threat controls')
        if asset.risk_level == RiskLevel.CRITICAL:
            recommendations.append('Immediate executive attention required')
        if asset.risk_level == RiskLevel.HIGH:
            recommendations.append('Develop risk reduction plan within 30 days')
        
        # Determine trend (simplified - would compare to historical)
        trend = 'stable'
        
        assessment = RiskAssessment(
            id=str(uuid.uuid4())[:8],
            asset_id=asset_id,
            assessment_date=datetime.now(),
            overall_risk=asset.risk_score,
            risk_level=asset.risk_level,
            risk_factors=risk_factors,
            recommendations=recommendations,
            trend=trend
        )
        
        self.assessments.append(assessment)
        
        logger.info(f"📊 Risk assessment completed: {assessment.id}")
        logger.info(f"   Overall Risk: {assessment.overall_risk:.2f}")
        logger.info(f"   Risk Level: {assessment.risk_level.value}")
        
        return assessment
    
    def register_user(self, username: str, department: str = "",
                     role: str = "") -> UserRisk:
        """
        Register user for behavior risk scoring
        
        Args:
            username: Username
            department: Department
            role: Role
            
        Returns:
            User risk profile
        """
        user = UserRisk(
            id=str(uuid.uuid4())[:8],
            username=username,
            department=department,
            role=role
        )
        
        self.user_risks.append(user)
        
        logger.info(f"✅ User registered: {user.id}")
        
        return user
    
    def update_user_behavior(self, user_id: str,
                            behavior_anomalies: int = None,
                            policy_violations: int = None,
                            failed_logins: int = None,
                            privileged_actions: int = None) -> UserRisk:
        """
        Update user behavior metrics
        
        Args:
            user_id: User ID
            behavior_anomalies: Number of anomalies
            policy_violations: Number of violations
            failed_logins: Number of failed logins
            privileged_actions: Number of privileged actions
            
        Returns:
            Updated user risk
        """
        user = next((u for u in self.user_risks if u.id == user_id), None)
        
        if not user:
            logger.error(f"User not found: {user_id}")
            return None
        
        # Update metrics
        if behavior_anomalies is not None:
            user.behavior_anomalies = behavior_anomalies
        if policy_violations is not None:
            user.policy_violations = policy_violations
        if failed_logins is not None:
            user.failed_logins = failed_logins
        if privileged_actions is not None:
            user.privileged_actions = privileged_actions
        
        # Calculate access level based on role
        if 'admin' in user.role.lower() or 'root' in user.role.lower():
            user.access_level = 9.0
        elif 'manager' in user.role.lower():
            user.access_level = 7.0
        elif 'developer' in user.role.lower():
            user.access_level = 6.0
        else:
            user.access_level = 4.0
        
        # Calculate user risk score
        self._calculate_user_risk(user)
        
        logger.info(f"📊 User risk updated: {user.username}")
        logger.info(f"   Risk Score: {user.risk_score:.2f}")
        logger.info(f"   Risk Level: {user.risk_level.value}")
        
        return user
    
    def _calculate_user_risk(self, user: UserRisk) -> None:
        """Calculate user risk score"""
        # Base risk from access level
        base_risk = user.access_level / 10.0 * 3.0  # Max 3 points
        
        # Behavior anomalies (max 2 points)
        anomaly_risk = min(2.0, user.behavior_anomalies * 0.5)
        
        # Policy violations (max 2 points)
        violation_risk = min(2.0, user.policy_violations * 0.5)
        
        # Failed logins (max 1.5 points)
        login_risk = min(1.5, user.failed_logins * 0.3)
        
        # Privileged actions (max 1.5 points)
        privileged_risk = min(1.5, user.privileged_actions * 0.1)
        
        # Total risk score (0-10)
        user.risk_score = round(
            base_risk + anomaly_risk + violation_risk + login_risk + privileged_risk,
            2
        )
        
        # Determine risk level
        if user.risk_score >= self.THRESHOLDS['critical']:
            user.risk_level = RiskLevel.CRITICAL
        elif user.risk_score >= self.THRESHOLDS['high']:
            user.risk_level = RiskLevel.HIGH
        elif user.risk_score >= self.THRESHOLDS['medium']:
            user.risk_level = RiskLevel.MEDIUM
        elif user.risk_score >= self.THRESHOLDS['low']:
            user.risk_level = RiskLevel.LOW
        else:
            user.risk_level = RiskLevel.MINIMAL
    
    def predict_attack_likelihood(self, asset_id: str) -> Dict:
        """
        Predict attack likelihood for asset
        
        Args:
            asset_id: Asset ID
            
        Returns:
            Prediction results
        """
        asset = next((a for a in self.assets if a.id == asset_id), None)
        
        if not asset:
            return {'error': 'Asset not found'}
        
        # Calculate likelihood based on multiple factors
        threat_factors = {
            'high_value_target': asset.criticality >= 8,
            'high_exposure': asset.exposure >= 7,
            'known_vulnerabilities': asset.vulnerability_score >= 6,
            'threat_actor_interest': asset.threat_exposure >= 6,
            'weak_controls': asset.vulnerability_score >= 7
        }
        
        positive_factors = sum(1 for v in threat_factors.values() if v)
        
        # Likelihood percentage
        likelihood = (positive_factors / len(threat_factors)) * 100
        
        # Time-based prediction
        if likelihood >= 80:
            time_frame = '24-48 hours'
            urgency = 'critical'
        elif likelihood >= 60:
            time_frame = '1-2 weeks'
            urgency = 'high'
        elif likelihood >= 40:
            time_frame = '1-3 months'
            urgency = 'medium'
        else:
            time_frame = '> 3 months'
            urgency = 'low'
        
        prediction = {
            'asset_id': asset_id,
            'asset_name': asset.name,
            'likelihood': round(likelihood, 1),
            'time_frame': time_frame,
            'urgency': urgency,
            'threat_factors': threat_factors,
            'positive_factors': positive_factors,
            'total_factors': len(threat_factors),
            'recommendations': self._get_attack_prevention_recommendations(asset)
        }
        
        logger.info(f"🔮 Attack likelihood predicted: {likelihood:.1f}%")
        logger.info(f"   Time frame: {time_frame}")
        logger.info(f"   Urgency: {urgency}")
        
        return prediction
    
    def _get_attack_prevention_recommendations(self, asset: Asset) -> List[str]:
        """Get attack prevention recommendations"""
        recommendations = []
        
        if asset.exposure >= 7:
            recommendations.append('Implement network segmentation')
            recommendations.append('Deploy WAF/firewall rules')
        
        if asset.vulnerability_score >= 6:
            recommendations.append('Prioritize patch management')
            recommendations.append('Conduct vulnerability assessment')
        
        if asset.criticality >= 8:
            recommendations.append('Implement EDR/XDR monitoring')
            recommendations.append('Enable enhanced logging')
        
        if asset.threat_exposure >= 6:
            recommendations.append('Review threat intelligence feeds')
            recommendations.append('Implement threat hunting')
        
        if not recommendations:
            recommendations.append('Maintain current security posture')
            recommendations.append('Continue regular assessments')
        
        return recommendations
    
    def get_risk_summary(self) -> Dict:
        """Get risk summary"""
        by_level = {}
        for asset in self.assets:
            level = asset.risk_level.value
            by_level[level] = by_level.get(level, 0) + 1
        
        user_by_level = {}
        for user in self.user_risks:
            level = user.risk_level.value
            user_by_level[level] = user_by_level.get(level, 0) + 1
        
        avg_risk = sum(a.risk_score for a in self.assets) / len(self.assets) if self.assets else 0
        
        return {
            'total_assets': len(self.assets),
            'total_users': len(self.user_risks),
            'assets_by_risk_level': by_level,
            'users_by_risk_level': user_by_level,
            'average_asset_risk': round(avg_risk, 2),
            'total_assessments': len(self.assessments)
        }
    
    def generate_report(self) -> str:
        """Generate risk assessment report"""
        summary = self.get_risk_summary()
        
        report = []
        report.append("=" * 70)
        report.append("🧠 PREDICTIVE RISK ASSESSMENT REPORT")
        report.append("=" * 70)
        report.append(f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        report.append("")
        report.append(f"Total Assets: {summary['total_assets']}")
        report.append(f"Total Users: {summary['total_users']}")
        report.append(f"Average Asset Risk: {summary['average_asset_risk']:.2f}/10")
        report.append("")
        
        report.append("ASSETS BY RISK LEVEL:")
        for level in ['critical', 'high', 'medium', 'low', 'minimal']:
            count = summary['assets_by_risk_level'].get(level, 0)
            bar = '█' * count + '░' * (max(5 - count, 0))
            report.append(f"  {level.upper():10} {bar} ({count})")
        report.append("")
        
        report.append("USERS BY RISK LEVEL:")
        for level in ['critical', 'high', 'medium', 'low', 'minimal']:
            count = summary['users_by_risk_level'].get(level, 0)
            report.append(f"  {level.upper():10} ({count})")
        report.append("")
        
        # Top risky assets
        if self.assets:
            report.append("TOP RISKY ASSETS:")
            sorted_assets = sorted(self.assets, key=lambda a: a.risk_score, reverse=True)[:5]
            for i, asset in enumerate(sorted_assets, 1):
                report.append(f"  {i}. {asset.name} - {asset.risk_score:.2f} ({asset.risk_level.value})")
            report.append("")
        
        # High risk users
        if self.user_risks:
            report.append("HIGH RISK USERS:")
            high_risk_users = [u for u in self.user_risks if u.risk_level in [RiskLevel.HIGH, RiskLevel.CRITICAL]]
            if high_risk_users:
                for user in high_risk_users[:5]:
                    report.append(f"  • {user.username} - {user.risk_score:.2f} ({user.risk_level.value})")
            else:
                report.append("  No high risk users identified")
            report.append("")
        
        report.append("=" * 70)
        
        return "\n".join(report)


def main():
    """Main entry point"""
    print("""
╔═══════════════════════════════════════════════════════════════╗
║     🧠 PREDICTIVE RISK SCORING ENGINE                        ║
║                    Phase 13: Alpha 0.1.0                      ║
╚═══════════════════════════════════════════════════════════════╝

Capabilities:
  - Asset risk scoring
  - User behavior risk scoring
  - Attack likelihood prediction
  - Vulnerability prioritization
  - Risk trend analysis

    """)
    
    engine = PredictiveRiskEngine()
    
    # Register assets
    engine.register_asset(
        'Domain Controller', 'server',
        criticality=10, exposure=6, vulnerability_score=5, threat_exposure=8
    )
    
    engine.register_asset(
        'Web Server', 'server',
        criticality=7, exposure=9, vulnerability_score=6, threat_exposure=7
    )
    
    engine.register_asset(
        'Developer Workstation', 'workstation',
        criticality=5, exposure=4, vulnerability_score=4, threat_exposure=3
    )
    
    # Assess assets
    for asset in engine.assets:
        engine.assess_asset(asset.id)
    
    # Register and score users
    user = engine.register_user('admin_jsmith', 'IT', 'System Administrator')
    engine.update_user_behavior(
        user.id,
        behavior_anomalies=3,
        policy_violations=1,
        failed_logins=5,
        privileged_actions=50
    )
    
    # Predict attack likelihood
    prediction = engine.predict_attack_likelihood(engine.assets[0].id)
    print(f"\nAttack Likelihood: {prediction['likelihood']:.1f}%")
    print(f"Time Frame: {prediction['time_frame']}")
    
    # Generate report
    print("\n" + engine.generate_report())


if __name__ == "__main__":
    main()
