"""
Alerting System
================

Manages alerts, notifications, and escalation policies.
"""

from typing import Dict, Any, List, Optional, Callable
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
import uuid
import threading


class AlertSeverity(str, Enum):
    """Alert severity levels."""
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"


class AlertStatus(str, Enum):
    """Alert status."""
    FIRING = "firing"
    ACKNOWLEDGED = "acknowledged"
    RESOLVED = "resolved"
    SILENCED = "silenced"


@dataclass
class Alert:
    """Alert instance."""

    alert_id: str = field(default_factory=lambda: str(uuid.uuid4())[:8])
    rule_name: str = ""
    severity: AlertSeverity = AlertSeverity.INFO
    status: AlertStatus = AlertStatus.FIRING

    title: str = ""
    description: str = ""
    metric_name: str = ""
    metric_value: Optional[float] = None
    threshold: Optional[float] = None

    created_at: str = field(default_factory=lambda: datetime.utcnow().isoformat())
    updated_at: str = field(default_factory=lambda: datetime.utcnow().isoformat())
    acknowledged_at: Optional[str] = None
    resolved_at: Optional[str] = None

    # Context
    labels: Dict[str, str] = field(default_factory=dict)
    annotations: Dict[str, str] = field(default_factory=dict)

    # Escalation
    escalation_level: int = 0
    notification_count: int = 0

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "alert_id": self.alert_id,
            "rule_name": self.rule_name,
            "severity": self.severity.value,
            "status": self.status.value,
            "title": self.title,
            "description": self.description,
            "metric_name": self.metric_name,
            "metric_value": self.metric_value,
            "threshold": self.threshold,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
            "acknowledged_at": self.acknowledged_at,
            "resolved_at": self.resolved_at,
            "labels": self.labels,
            "annotations": self.annotations,
            "escalation_level": self.escalation_level,
            "notification_count": self.notification_count,
        }

    def acknowledge(self, user: str = "system"):
        """Acknowledge the alert."""
        self.status = AlertStatus.ACKNOWLEDGED
        self.acknowledged_at = datetime.utcnow().isoformat()
        self.updated_at = self.acknowledged_at
        self.annotations["acknowledged_by"] = user

    def resolve(self):
        """Resolve the alert."""
        self.status = AlertStatus.RESOLVED
        self.resolved_at = datetime.utcnow().isoformat()
        self.updated_at = self.resolved_at

    def silence(self, duration_minutes: int = 60):
        """Silence the alert."""
        self.status = AlertStatus.SILENCED
        self.updated_at = datetime.utcnow().isoformat()
        self.annotations["silenced_until"] = (
            datetime.utcnow() + timedelta(minutes=duration_minutes)
        ).isoformat()


@dataclass
class AlertRule:
    """Alert rule definition."""

    rule_id: str = field(default_factory=lambda: str(uuid.uuid4())[:8])
    name: str = ""
    description: str = ""

    # Condition
    metric_name: str = ""
    metric_labels: Dict[str, str] = field(default_factory=dict)
    operator: str = ">"  # >, <, >=, <=, ==, !=
    threshold: float = 0.0
    window_seconds: int = 300  # Time window for evaluation

    # Alert config
    severity: AlertSeverity = AlertSeverity.WARNING
    title_template: str = ""
    description_template: str = ""

    # Notification
    notification_channels: List[str] = field(default_factory=list)
    repeat_interval_minutes: int = 15
    escalation_minutes: int = 30

    # State
    enabled: bool = True
    cooldown_minutes: int = 5
    last_triggered: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "rule_id": self.rule_id,
            "name": self.name,
            "description": self.description,
            "metric_name": self.metric_name,
            "metric_labels": self.metric_labels,
            "operator": self.operator,
            "threshold": self.threshold,
            "window_seconds": self.window_seconds,
            "severity": self.severity.value,
            "title_template": self.title_template,
            "description_template": self.description_template,
            "notification_channels": self.notification_channels,
            "repeat_interval_minutes": self.repeat_interval_minutes,
            "escalation_minutes": self.escalation_minutes,
            "enabled": self.enabled,
            "cooldown_minutes": self.cooldown_minutes,
            "last_triggered": self.last_triggered,
        }

    def evaluate(self, value: Optional[float]) -> bool:
        """Evaluate if alert should fire."""
        if value is None:
            return False

        if self.operator == ">":
            return value > self.threshold
        elif self.operator == "<":
            return value < self.threshold
        elif self.operator == ">=":
            return value >= self.threshold
        elif self.operator == "<=":
            return value <= self.threshold
        elif self.operator == "==":
            return value == self.threshold
        elif self.operator == "!=":
            return value != self.threshold

        return False


class AlertManager:
    """Manages alerts and notifications."""

    def __init__(self, metrics_collector=None):
        self._rules: Dict[str, AlertRule] = {}
        self._alerts: Dict[str, Alert] = {}
        self._metrics = metrics_collector
        self._lock = threading.Lock()
        self._notification_callbacks: Dict[str, Callable] = {}
        self._active_alerts: List[str] = []

    def create_rule(self, name: str, metric_name: str,
                    operator: str, threshold: float,
                    severity: AlertSeverity = AlertSeverity.WARNING,
                    window_seconds: int = 300) -> AlertRule:
        """Create an alert rule."""
        rule = AlertRule(
            name=name,
            metric_name=metric_name,
            operator=operator,
            threshold=threshold,
            severity=severity,
            window_seconds=window_seconds,
        )
        self._rules[rule.rule_id] = rule
        return rule

    def get_rule(self, rule_id: str) -> Optional[AlertRule]:
        """Get a rule by ID."""
        return self._rules.get(rule_id)

    def delete_rule(self, rule_id: str) -> bool:
        """Delete a rule."""
        if rule_id in self._rules:
            del self._rules[rule_id]
            return True
        return False

    def list_rules(self) -> List[AlertRule]:
        """List all rules."""
        return list(self._rules.values())

    def list_alerts(self, status: Optional[AlertStatus] = None) -> List[Alert]:
        """List alerts, optionally filtered by status."""
        with self._lock:
            alerts = list(self._alerts.values())

        if status:
            alerts = [a for a in alerts if a.status == status]

        return alerts

    def get_alert(self, alert_id: str) -> Optional[Alert]:
        """Get an alert by ID."""
        return self._alerts.get(alert_id)

    def acknowledge_alert(self, alert_id: str, user: str = "system") -> bool:
        """Acknowledge an alert."""
        alert = self._alerts.get(alert_id)
        if alert:
            alert.acknowledge(user)
            return True
        return False

    def resolve_alert(self, alert_id: str) -> bool:
        """Resolve an alert."""
        alert = self._alerts.get(alert_id)
        if alert:
            alert.resolve()
            if alert_id in self._active_alerts:
                self._active_alerts.remove(alert_id)
            return True
        return False

    def register_notification_channel(self, channel: str, callback: Callable):
        """Register a notification channel callback."""
        self._notification_callbacks[channel] = callback

    def evaluate_rules(self):
        """Evaluate all alert rules."""
        if not self._metrics:
            return

        for rule in self._rules.values():
            if not rule.enabled:
                continue

            # Get metric value
            metric = self._metrics.get_metric(rule.metric_name, rule.metric_labels)
            if not metric:
                continue

            value = metric.average(rule.window_seconds)
            if value is None:
                continue

            # Check if alert should fire
            if rule.evaluate(value):
                self._fire_alert(rule, value)

    def _fire_alert(self, rule: AlertRule, value: float):
        """Fire an alert."""
        # Check cooldown
        if rule.last_triggered:
            last_fire = datetime.fromisoformat(rule.last_triggered)
            cooldown = timedelta(minutes=rule.cooldown_minutes)
            if datetime.utcnow() - last_fire < cooldown:
                return

        # Create or update alert
        alert_key = f"{rule.rule_id}"

        with self._lock:
            if alert_key in self._alerts:
                alert = self._alerts[alert_key]
                alert.metric_value = value
                alert.updated_at = datetime.utcnow().isoformat()
                alert.notification_count += 1
            else:
                alert = Alert(
                    rule_name=rule.name,
                    severity=rule.severity,
                    title=rule.title_template or f"Alert: {rule.name}",
                    description=rule.description_template or f"{rule.metric_name} {rule.operator} {rule.threshold}",
                    metric_name=rule.metric_name,
                    metric_value=value,
                    threshold=rule.threshold,
                    labels=rule.metric_labels,
                )
                self._alerts[alert_key] = alert
                self._active_alerts.append(alert_key)

        rule.last_triggered = datetime.utcnow().isoformat()

        # Send notifications
        self._send_notifications(alert, rule)

    def _send_notifications(self, alert: Alert, rule: AlertRule):
        """Send notifications for an alert."""
        for channel in rule.notification_channels:
            callback = self._notification_callbacks.get(channel)
            if callback:
                try:
                    callback(alert.to_dict())
                except Exception:
                    pass  # Ignore notification errors

    def get_summary(self) -> Dict[str, Any]:
        """Get alert summary."""
        with self._lock:
            active_count = sum(1 for a in self._alerts.values()
                             if a.status == AlertStatus.FIRING)
            acknowledged_count = sum(1 for a in self._alerts.values()
                                    if a.status == AlertStatus.ACKNOWLEDGED)
            critical_count = sum(1 for a in self._alerts.values()
                               if a.severity == AlertSeverity.CRITICAL and a.status == AlertStatus.FIRING)

        return {
            "total_rules": len(self._rules),
            "active_alerts": active_count,
            "acknowledged_alerts": acknowledged_count,
            "critical_alerts": critical_count,
            "total_alerts": len(self._alerts),
        }

    def clear_resolved(self, older_than_minutes: int = 60):
        """Clear resolved alerts older than specified time."""
        cutoff = datetime.utcnow() - timedelta(minutes=older_than_minutes)

        with self._lock:
            to_remove = []
            for alert_id, alert in self._alerts.items():
                if alert.status == AlertStatus.RESOLVED and alert.resolved_at:
                    resolved_time = datetime.fromisoformat(alert.resolved_at)
                    if resolved_time < cutoff:
                        to_remove.append(alert_id)

            for alert_id in to_remove:
                del self._alerts[alert_id]
