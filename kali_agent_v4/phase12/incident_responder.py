#!/usr/bin/env python3
"""
🚨 KaliAgent v4.4.0 - Phase 12: Automated Response & Remediation
Incident Response Orchestrator

Automated incident response capabilities:
- Incident classification
- Severity assessment
- Response playbook selection
- Action orchestration
- Evidence preservation
- Post-incident reporting

Author: KaliAgent Team
Started: April 28, 2026
Status: Alpha (0.1.0)
"""

import logging
import json
from typing import List, Dict, Optional
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from enum import Enum
import uuid

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger('IncidentResponder')


class IncidentSeverity(Enum):
    """Incident severity levels"""
    CRITICAL = "critical"  # Active breach, data exfiltration in progress
    HIGH = "high"          # Confirmed compromise, immediate action needed
    MEDIUM = "medium"      # Suspicious activity, investigation required
    LOW = "low"            # Minor security event, monitoring
    INFO = "info"          # Informational, no action needed


class IncidentStatus(Enum):
    """Incident status"""
    NEW = "new"
    TRIAGING = "triaging"
    CONTAINING = "containing"
    REMEDIATING = "remediating"
    RECOVERING = "recovering"
    CLOSED = "closed"
    ESCALATED = "escalated"


class IncidentType(Enum):
    """Incident types"""
    MALWARE = "malware"
    UNAUTHORIZED_ACCESS = "unauthorized_access"
    DATA_BREACH = "data_breach"
    DENIAL_OF_SERVICE = "dos"
    INSIDER_THREAT = "insider_threat"
    PHISHING = "phishing"
    CREDENTIAL_COMPROMISE = "credential_compromise"
    POLICY_VIOLATION = "policy_violation"
    OTHER = "other"


@dataclass
class Incident:
    """Security incident"""
    id: str
    title: str
    description: str
    severity: IncidentSeverity
    incident_type: IncidentType
    status: IncidentStatus
    created_at: datetime
    updated_at: datetime
    affected_systems: List[str] = field(default_factory=list)
    affected_users: List[str] = field(default_factory=list)
    iocs: List[str] = field(default_factory=list)
    mitre_attack: List[str] = field(default_factory=list)
    source: str = ""
    evidence: List[Dict] = field(default_factory=list)
    actions_taken: List[Dict] = field(default_factory=list)
    assigned_to: str = ""
    closed_at: Optional[datetime] = None
    closure_reason: str = ""
    
    def to_dict(self) -> Dict:
        return {
            'id': self.id,
            'title': self.title,
            'description': self.description,
            'severity': self.severity.value,
            'incident_type': self.incident_type.value,
            'status': self.status.value,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat(),
            'affected_systems': self.affected_systems,
            'affected_users': self.affected_users,
            'iocs': self.iocs,
            'mitre_attack': self.mitre_attack,
            'source': self.source,
            'evidence': self.evidence,
            'actions_taken': self.actions_taken,
            'assigned_to': self.assigned_to,
            'closed_at': self.closed_at.isoformat() if self.closed_at else None,
            'closure_reason': self.closure_reason
        }


@dataclass
class ResponseAction:
    """Response action"""
    id: str
    action_type: str
    target: str
    status: str
    result: str = ""
    error: str = ""
    executed_at: Optional[datetime] = None
    executed_by: str = "automated"
    
    def to_dict(self) -> Dict:
        return {
            'id': self.id,
            'action_type': self.action_type,
            'target': self.target,
            'status': self.status,
            'result': self.result,
            'error': self.error,
            'executed_at': self.executed_at.isoformat() if self.executed_at else None,
            'executed_by': self.executed_by
        }


class IncidentResponder:
    """
    Incident Response Orchestrator
    
    Capabilities:
    - Incident classification
    - Severity assessment
    - Response playbook selection
    - Action orchestration
    - Evidence preservation
    - Post-incident reporting
    """
    
    VERSION = "0.1.0"
    
    # Response playbooks by incident type
    PLAYBOOKS = {
        IncidentType.MALWARE: {
            'name': 'Malware Response',
            'steps': ['isolate_host', 'collect_memory', 'scan_system', 'remove_malware', 'restore'],
            'priority': 'high'
        },
        IncidentType.UNAUTHORIZED_ACCESS: {
            'name': 'Unauthorized Access Response',
            'steps': ['disable_account', 'reset_credentials', 'audit_access', 'review_logs'],
            'priority': 'high'
        },
        IncidentType.DATA_BREACH: {
            'name': 'Data Breach Response',
            'steps': ['identify_scope', 'contain_leak', 'preserve_evidence', 'notify_stakeholders'],
            'priority': 'critical'
        },
        IncidentType.CREDENTIAL_COMPROMISE: {
            'name': 'Credential Compromise Response',
            'steps': ['reset_password', 'revoke_sessions', 'audit_access', 'enable_mfa'],
            'priority': 'high'
        },
        IncidentType.PHISHING: {
            'name': 'Phishing Response',
            'steps': ['block_sender', 'remove_emails', 'scan_recipients', 'user_awareness'],
            'priority': 'medium'
        },
        IncidentType.INSIDER_THREAT: {
            'name': 'Insider Threat Response',
            'steps': ['monitor_activity', 'preserve_evidence', 'restrict_access', 'investigate'],
            'priority': 'high'
        },
        IncidentType.DENIAL_OF_SERVICE: {
            'name': 'DoS Response',
            'steps': ['identify_source', 'block_traffic', 'scale_resources', 'notify_provider'],
            'priority': 'critical'
        },
        IncidentType.POLICY_VIOLATION: {
            'name': 'Policy Violation Response',
            'steps': ['document_violation', 'notify_management', 'remediate', 'training'],
            'priority': 'low'
        }
    }
    
    def __init__(self, config: Dict = None):
        self.config = config or {}
        self.incidents: List[Incident] = []
        self.active_incidents: List[Incident] = []
        self.actions: List[ResponseAction] = []
        
        # Integration hooks (to be implemented)
        self.containment_module = None
        self.remediation_module = None
        self.recovery_module = None
        
        logger.info(f"🚨 Incident Responder v{self.VERSION}")
        logger.info(f"   Playbooks loaded: {len(self.PLAYBOOKS)}")
    
    def create_incident(self, title: str, description: str, 
                       incident_type: IncidentType = None,
                       severity: IncidentSeverity = None,
                       source: str = "",
                       affected_systems: List[str] = None,
                       affected_users: List[str] = None,
                       iocs: List[str] = None,
                       mitre_attack: List[str] = None,
                       evidence: List[Dict] = None) -> Incident:
        """
        Create a new incident
        
        Args:
            title: Incident title
            description: Incident description
            incident_type: Type of incident
            severity: Severity level
            source: Source of detection
            affected_systems: List of affected systems
            affected_users: List of affected users
            iocs: Indicators of compromise
            mitre_attack: MITRE ATT&CK techniques
            evidence: Evidence data
            
        Returns:
            Created incident
        """
        # Auto-assess severity if not provided
        if severity is None:
            severity = self._assess_severity(incident_type, affected_systems)
        
        # Auto-classify type if not provided
        if incident_type is None:
            incident_type = self._classify_incident(description, iocs)
        
        incident = Incident(
            id=str(uuid.uuid4())[:8],
            title=title,
            description=description,
            severity=severity,
            incident_type=incident_type or IncidentType.OTHER,
            status=IncidentStatus.NEW,
            created_at=datetime.now(),
            updated_at=datetime.now(),
            affected_systems=affected_systems or [],
            affected_users=affected_users or [],
            iocs=iocs or [],
            mitre_attack=mitre_attack or [],
            source=source,
            evidence=evidence or []
        )
        
        self.incidents.append(incident)
        self.active_incidents.append(incident)
        
        logger.warning(f"🚨 INCIDENT CREATED: {incident.id} - {title}")
        logger.warning(f"   Severity: {severity.value}")
        logger.warning(f"   Type: {incident_type.value if incident_type else 'Other'}")
        logger.warning(f"   Affected: {len(incident.affected_systems)} systems, {len(incident.affected_users)} users")
        
        return incident
    
    def _assess_severity(self, incident_type: IncidentType, 
                        affected_systems: List[str] = None) -> IncidentSeverity:
        """Auto-assess incident severity"""
        # Critical: Data breach, DoS on critical systems
        if incident_type in [IncidentType.DATA_BREACH, IncidentType.DENIAL_OF_SERVICE]:
            return IncidentSeverity.CRITICAL
        
        # High: Malware, unauthorized access, credential compromise
        if incident_type in [IncidentType.MALWARE, IncidentType.UNAUTHORIZED_ACCESS, 
                            IncidentType.CREDENTIAL_COMPROMISE, IncidentType.INSIDER_THREAT]:
            return IncidentSeverity.HIGH
        
        # Medium: Phishing
        if incident_type == IncidentType.PHISHING:
            return IncidentSeverity.MEDIUM
        
        # Low: Policy violation
        return IncidentSeverity.LOW
    
    def _classify_incident(self, description: str, iocs: List[str] = None) -> IncidentType:
        """Auto-classify incident type based on description and IOCs"""
        desc_lower = description.lower()
        
        if any(word in desc_lower for word in ['malware', 'virus', 'trojan', 'ransomware']):
            return IncidentType.MALWARE
        elif any(word in desc_lower for word in ['unauthorized', 'breach', 'intrusion']):
            return IncidentType.UNAUTHORIZED_ACCESS
        elif any(word in desc_lower for word in ['data leak', 'exfiltration', 'pii']):
            return IncidentType.DATA_BREACH
        elif any(word in desc_lower for word in ['credential', 'password', 'account']):
            return IncidentType.CREDENTIAL_COMPROMISE
        elif any(word in desc_lower for word in ['phishing', 'spam', 'fake']):
            return IncidentType.PHISHING
        elif any(word in desc_lower for word in ['insider', 'employee', 'contractor']):
            return IncidentType.INSIDER_THREAT
        elif any(word in desc_lower for word in ['dos', 'ddos', 'flood']):
            return IncidentType.DENIAL_OF_SERVICE
        
        return IncidentType.OTHER
    
    def triage_incident(self, incident_id: str) -> Dict:
        """
        Triage an incident
        
        Args:
            incident_id: Incident ID
            
        Returns:
            Triage results
        """
        incident = self._get_incident(incident_id)
        
        if not incident:
            return {'error': 'Incident not found'}
        
        incident.status = IncidentStatus.TRIAGING
        incident.updated_at = datetime.now()
        
        logger.info(f"🔍 Triaging incident: {incident_id}")
        
        # Get playbook
        playbook = self.PLAYBOOKS.get(incident.incident_type, {})
        
        triage_result = {
            'incident_id': incident_id,
            'severity': incident.severity.value,
            'type': incident.incident_type.value,
            'playbook': playbook.get('name', 'Generic Response'),
            'recommended_actions': playbook.get('steps', []),
            'priority': playbook.get('priority', 'medium'),
            'affected_systems': incident.affected_systems,
            'affected_users': incident.affected_users
        }
        
        logger.info(f"   Playbook: {triage_result['playbook']}")
        logger.info(f"   Priority: {triage_result['priority']}")
        
        return triage_result
    
    def execute_response(self, incident_id: str, actions: List[Dict]) -> List[ResponseAction]:
        """
        Execute response actions
        
        Args:
            incident_id: Incident ID
            actions: List of actions to execute
            
        Returns:
            List of executed actions
        """
        incident = self._get_incident(incident_id)
        
        if not incident:
            return []
        
        incident.status = IncidentStatus.CONTAINING
        incident.updated_at = datetime.now()
        
        executed_actions = []
        
        for action_def in actions:
            action = ResponseAction(
                id=str(uuid.uuid4())[:8],
                action_type=action_def.get('type', 'unknown'),
                target=action_def.get('target', ''),
                status='pending'
            )
            
            # Execute action (simplified - would call actual modules)
            action.status = 'completed'
            action.result = f"Action {action.action_type} executed on {action.target}"
            action.executed_at = datetime.now()
            
            executed_actions.append(action)
            self.actions.append(action)
            
            incident.actions_taken.append(action.to_dict())
            
            logger.info(f"✅ Action executed: {action.action_type} on {action.target}")
        
        return executed_actions
    
    def contain_incident(self, incident_id: str, containment_actions: List[Dict]) -> bool:
        """
        Contain an incident
        
        Args:
            incident_id: Incident ID
            containment_actions: Containment actions to execute
            
        Returns:
            Success status
        """
        incident = self._get_incident(incident_id)
        
        if not incident:
            return False
        
        incident.status = IncidentStatus.CONTAINING
        
        logger.info(f"🛡️  Containing incident: {incident_id}")
        
        # Execute containment actions
        self.execute_response(incident_id, containment_actions)
        
        return True
    
    def remediate_incident(self, incident_id: str, remediation_actions: List[Dict]) -> bool:
        """
        Remediate an incident
        
        Args:
            incident_id: Incident ID
            remediation_actions: Remediation actions to execute
            
        Returns:
            Success status
        """
        incident = self._get_incident(incident_id)
        
        if not incident:
            return False
        
        incident.status = IncidentStatus.REMEDIATING
        
        logger.info(f"🔧 Remediating incident: {incident_id}")
        
        # Execute remediation actions
        self.execute_response(incident_id, remediation_actions)
        
        return True
    
    def close_incident(self, incident_id: str, closure_reason: str = "") -> bool:
        """
        Close an incident
        
        Args:
            incident_id: Incident ID
            closure_reason: Reason for closure
            
        Returns:
            Success status
        """
        incident = self._get_incident(incident_id)
        
        if not incident:
            return False
        
        incident.status = IncidentStatus.CLOSED
        incident.closed_at = datetime.now()
        incident.closure_reason = closure_reason
        incident.updated_at = datetime.now()
        
        # Remove from active incidents
        if incident in self.active_incidents:
            self.active_incidents.remove(incident)
        
        logger.info(f"✅ Incident closed: {incident_id}")
        logger.info(f"   Reason: {closure_reason}")
        
        return True
    
    def _get_incident(self, incident_id: str) -> Optional[Incident]:
        """Get incident by ID"""
        for incident in self.incidents:
            if incident.id == incident_id:
                return incident
        return None
    
    def get_incident_summary(self) -> Dict:
        """Get incident summary"""
        by_severity = {}
        by_status = {}
        by_type = {}
        
        for incident in self.incidents:
            # By severity
            sev = incident.severity.value
            by_severity[sev] = by_severity.get(sev, 0) + 1
            
            # By status
            status = incident.status.value
            by_status[status] = by_status.get(status, 0) + 1
            
            # By type
            type_ = incident.incident_type.value
            by_type[type_] = by_type.get(type_, 0) + 1
        
        return {
            'total_incidents': len(self.incidents),
            'active_incidents': len(self.active_incidents),
            'by_severity': by_severity,
            'by_status': by_status,
            'by_type': by_type,
            'total_actions': len(self.actions)
        }
    
    def generate_report(self, incident_id: str = None) -> str:
        """
        Generate incident report
        
        Args:
            incident_id: Specific incident (or all if None)
            
        Returns:
            Report text
        """
        report = []
        report.append("=" * 70)
        report.append("🚨 INCIDENT RESPONSE REPORT")
        report.append("=" * 70)
        report.append(f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        report.append("")
        
        if incident_id:
            # Single incident report
            incident = self._get_incident(incident_id)
            if incident:
                report.append(f"INCIDENT: {incident.id}")
                report.append(f"Title: {incident.title}")
                report.append(f"Severity: {incident.severity.value.upper()}")
                report.append(f"Type: {incident.incident_type.value}")
                report.append(f"Status: {incident.status.value}")
                report.append(f"Created: {incident.created_at}")
                report.append(f"Closed: {incident.closed_at or 'Open'}")
                report.append("")
                report.append(f"Description: {incident.description}")
                report.append("")
                report.append(f"Affected Systems: {', '.join(incident.affected_systems)}")
                report.append(f"Affected Users: {', '.join(incident.affected_users)}")
                report.append("")
                
                if incident.iocs:
                    report.append("IOCs:")
                    for ioc in incident.iocs:
                        report.append(f"  - {ioc}")
                    report.append("")
                
                if incident.actions_taken:
                    report.append("Actions Taken:")
                    for action in incident.actions_taken:
                        report.append(f"  ✅ {action['action_type']} on {action['target']}")
                    report.append("")
                
                if incident.closure_reason:
                    report.append(f"Closure Reason: {incident.closure_reason}")
        else:
            # Summary report
            summary = self.get_incident_summary()
            
            report.append("SUMMARY:")
            report.append(f"  Total Incidents: {summary['total_incidents']}")
            report.append(f"  Active Incidents: {summary['active_incidents']}")
            report.append(f"  Total Actions: {summary['total_actions']}")
            report.append("")
            
            report.append("BY SEVERITY:")
            for sev, count in summary['by_severity'].items():
                report.append(f"  {sev.upper()}: {count}")
            report.append("")
            
            report.append("BY TYPE:")
            for type_, count in summary['by_type'].items():
                report.append(f"  {type_}: {count}")
        
        report.append("")
        report.append("=" * 70)
        
        return "\n".join(report)


def main():
    """Main entry point"""
    print("""
╔═══════════════════════════════════════════════════════════════╗
║     🚨 INCIDENT RESPONSE ORCHESTRATOR                        ║
║                    Phase 12: Alpha 0.1.0                      ║
╚═══════════════════════════════════════════════════════════════╝

Capabilities:
  - Incident classification
  - Severity assessment
  - Response playbook selection
  - Action orchestration
  - Evidence preservation
  - Post-incident reporting

    """)
    
    responder = IncidentResponder()
    
    # Create test incident
    incident = responder.create_incident(
        title='Malware Detected on Workstation',
        description='EDR detected Mimikatz activity on WS-001',
        incident_type=IncidentType.MALWARE,
        severity=IncidentSeverity.HIGH,
        source='EDR',
        affected_systems=['WS-001'],
        affected_users=['jsmith'],
        iocs=['192.168.1.100', 'malware-c2.example.com'],
        mitre_attack=['T1003.001']
    )
    
    # Triage
    triage = responder.triage_incident(incident.id)
    print(f"Triage: {triage['playbook']}")
    
    # Execute response
    actions = [
        {'type': 'isolate_host', 'target': 'WS-001'},
        {'type': 'collect_memory', 'target': 'WS-001'},
        {'type': 'disable_account', 'target': 'jsmith'}
    ]
    responder.execute_response(incident.id, actions)
    
    # Close incident
    responder.close_incident(incident.id, 'Containment and remediation complete')
    
    # Generate report
    print("\n" + responder.generate_report(incident.id))


if __name__ == "__main__":
    main()
