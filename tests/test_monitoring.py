"""
Tests for Monitoring & Observability
=====================================

Unit tests for metrics, dashboard, and alerting systems.
"""

import pytest
import time
from datetime import datetime, timedelta


@pytest.fixture
def monitoring_imports():
    """Import monitoring modules."""
    from agentic_ai.monitoring.metrics import MetricsCollector, MetricType, MetricPoint
    from agentic_ai.monitoring.dashboard import Dashboard, DashboardWidget, WidgetType, DashboardManager
    from agentic_ai.monitoring.alerting import AlertManager, Alert, AlertSeverity, AlertRule, AlertStatus
    
    return {
        'MetricsCollector': MetricsCollector,
        'MetricType': MetricType,
        'MetricPoint': MetricPoint,
        'Dashboard': Dashboard,
        'DashboardWidget': DashboardWidget,
        'WidgetType': WidgetType,
        'DashboardManager': DashboardManager,
        'AlertManager': AlertManager,
        'Alert': Alert,
        'AlertSeverity': AlertSeverity,
        'AlertRule': AlertRule,
        'AlertStatus': AlertStatus,
    }


class TestMetricPoint:
    """Test MetricPoint class."""
    
    def test_metric_point_creation(self, monitoring_imports):
        """Test creating a metric point."""
        MetricPoint = monitoring_imports['MetricPoint']
        MetricType = monitoring_imports['MetricType']
        
        point = MetricPoint(
            metric_name="cpu_usage",
            metric_type=MetricType.GAUGE,
            value=75.5,
            labels={"host": "server-1"},
        )
        
        assert point.metric_name == "cpu_usage"
        assert point.value == 75.5
        assert point.labels["host"] == "server-1"
    
    def test_metric_point_to_dict(self, monitoring_imports):
        """Test metric point serialization."""
        MetricPoint = monitoring_imports['MetricPoint']
        MetricType = monitoring_imports['MetricType']
        
        point = MetricPoint(
            metric_name="memory",
            metric_type=MetricType.GAUGE,
            value=1024,
        )
        
        data = point.to_dict()
        
        assert data["metric_name"] == "memory"
        assert data["value"] == 1024
        assert "timestamp" in data


class TestMetricsCollector:
    """Test MetricsCollector class."""
    
    def test_collector_creation(self, monitoring_imports):
        """Test creating a metrics collector."""
        MetricsCollector = monitoring_imports['MetricsCollector']
        
        collector = MetricsCollector(retention_seconds=3600)
        
        assert collector._retention_seconds == 3600
    
    def test_record_gauge(self, monitoring_imports):
        """Test recording gauge metrics."""
        MetricsCollector = monitoring_imports['MetricsCollector']
        MetricType = monitoring_imports['MetricType']
        
        collector = MetricsCollector()
        collector.record("cpu_usage", 75.5, MetricType.GAUGE)
        
        metric = collector.get_metric("cpu_usage")
        assert metric is not None
        assert metric.latest() == 75.5
    
    def test_increment_counter(self, monitoring_imports):
        """Test incrementing counter metrics."""
        MetricsCollector = monitoring_imports['MetricsCollector']
        
        collector = MetricsCollector()
        collector.increment("requests_total")
        collector.increment("requests_total", 5)
        
        metric = collector.get_metric("requests_total")
        assert metric.latest() == 6
    
    def test_timer_context(self, monitoring_imports):
        """Test timer context manager."""
        MetricsCollector = monitoring_imports['MetricsCollector']
        
        collector = MetricsCollector()
        
        with collector.timer("operation_duration"):
            time.sleep(0.01)
        
        metric = collector.get_metric("operation_duration")
        assert metric is not None
        assert metric.latest() > 0
    
    def test_get_all_metrics(self, monitoring_imports):
        """Test getting all metrics."""
        MetricsCollector = monitoring_imports['MetricsCollector']
        MetricType = monitoring_imports['MetricType']
        
        collector = MetricsCollector()
        collector.record("metric1", 10, MetricType.GAUGE)
        collector.record("metric2", 20, MetricType.GAUGE)
        
        all_metrics = collector.get_all_metrics()
        
        assert "metric1" in all_metrics
        assert "metric2" in all_metrics
    
    def test_metric_with_labels(self, monitoring_imports):
        """Test metrics with labels."""
        MetricsCollector = monitoring_imports['MetricsCollector']
        
        collector = MetricsCollector()
        collector.record("cpu_usage", 50, labels={"host": "server-1"})
        collector.record("cpu_usage", 75, labels={"host": "server-2"})
        
        metric1 = collector.get_metric("cpu_usage", {"host": "server-1"})
        metric2 = collector.get_metric("cpu_usage", {"host": "server-2"})
        
        assert metric1.latest() == 50
        assert metric2.latest() == 75


class TestDashboardWidget:
    """Test DashboardWidget class."""
    
    def test_widget_creation(self, monitoring_imports):
        """Test creating a dashboard widget."""
        DashboardWidget = monitoring_imports['DashboardWidget']
        WidgetType = monitoring_imports['WidgetType']
        
        widget = DashboardWidget(
            title="CPU Usage",
            widget_type=WidgetType.GAUGE,
            metric_name="cpu_usage",
            unit="%",
            thresholds={"warning": 80, "critical": 95},
        )
        
        assert widget.title == "CPU Usage"
        assert widget.unit == "%"
        assert widget.thresholds["warning"] == 80
    
    def test_widget_to_dict(self, monitoring_imports):
        """Test widget serialization."""
        DashboardWidget = monitoring_imports['DashboardWidget']
        WidgetType = monitoring_imports['WidgetType']
        
        widget = DashboardWidget(
            title="Memory",
            widget_type=WidgetType.GAUGE,
            metric_name="memory",
        )
        
        data = widget.to_dict()
        
        assert data["title"] == "Memory"
        assert data["widget_type"] == "gauge"


class TestDashboard:
    """Test Dashboard class."""
    
    def test_dashboard_creation(self, monitoring_imports):
        """Test creating a dashboard."""
        Dashboard = monitoring_imports['Dashboard']
        DashboardWidget = monitoring_imports['DashboardWidget']
        WidgetType = monitoring_imports['WidgetType']
        
        dashboard = Dashboard(
            name="System Overview",
            description="Key system metrics",
            columns=3,
        )
        
        widget = DashboardWidget(
            title="CPU",
            widget_type=WidgetType.GAUGE,
            metric_name="cpu_usage",
        )
        dashboard.add_widget(widget)
        
        assert dashboard.name == "System Overview"
        assert len(dashboard.widgets) == 1
    
    def test_dashboard_remove_widget(self, monitoring_imports):
        """Test removing a widget from dashboard."""
        Dashboard = monitoring_imports['Dashboard']
        DashboardWidget = monitoring_imports['DashboardWidget']
        WidgetType = monitoring_imports['WidgetType']
        
        dashboard = Dashboard(name="Test")
        widget = DashboardWidget(title="Widget1", widget_type=WidgetType.GAUGE)
        dashboard.add_widget(widget)
        
        dashboard.remove_widget(widget.widget_id)
        
        assert len(dashboard.widgets) == 0
    
    def test_dashboard_to_dict(self, monitoring_imports):
        """Test dashboard serialization."""
        Dashboard = monitoring_imports['Dashboard']
        
        dashboard = Dashboard(name="Test Dashboard", columns=2)
        
        data = dashboard.to_dict()
        
        assert data["name"] == "Test Dashboard"
        assert data["columns"] == 2


class TestDashboardManager:
    """Test DashboardManager class."""
    
    def test_manager_creation(self, monitoring_imports):
        """Test creating dashboard manager."""
        DashboardManager = monitoring_imports['DashboardManager']
        MetricsCollector = monitoring_imports['MetricsCollector']
        
        collector = MetricsCollector()
        manager = DashboardManager(collector)
        
        assert manager is not None
    
    def test_create_dashboard(self, monitoring_imports):
        """Test creating a dashboard via manager."""
        DashboardManager = monitoring_imports['DashboardManager']
        MetricsCollector = monitoring_imports['MetricsCollector']
        
        collector = MetricsCollector()
        manager = DashboardManager(collector)
        
        dashboard = manager.create_dashboard(
            name="Production",
            description="Production metrics",
        )
        
        assert dashboard.name == "Production"
        assert manager.get_dashboard(dashboard.dashboard_id) is not None
    
    def test_get_dashboard_data(self, monitoring_imports):
        """Test getting dashboard with metric data."""
        DashboardManager = monitoring_imports['DashboardManager']
        MetricsCollector = monitoring_imports['MetricsCollector']
        DashboardWidget = monitoring_imports['DashboardWidget']
        WidgetType = monitoring_imports['WidgetType']
        
        collector = MetricsCollector()
        manager = DashboardManager(collector)
        
        # Record some metrics
        collector.record("cpu_usage", 65.5)
        
        # Create dashboard with widget
        dashboard = manager.create_dashboard(name="Test")
        widget = DashboardWidget(
            title="CPU",
            widget_type=WidgetType.GAUGE,
            metric_name="cpu_usage",
        )
        dashboard.add_widget(widget)
        
        data = manager.get_dashboard_data(dashboard.dashboard_id)
        
        assert "widget_data" in data
        assert len(data["widget_data"]) == 1


class TestAlertRule:
    """Test AlertRule class."""
    
    def test_rule_creation(self, monitoring_imports):
        """Test creating an alert rule."""
        AlertRule = monitoring_imports['AlertRule']
        AlertSeverity = monitoring_imports['AlertSeverity']
        
        rule = AlertRule(
            name="High CPU",
            metric_name="cpu_usage",
            operator=">",
            threshold=90,
            severity=AlertSeverity.WARNING,
        )
        
        assert rule.name == "High CPU"
        assert rule.threshold == 90
    
    def test_rule_evaluate_greater(self, monitoring_imports):
        """Test rule evaluation with greater than."""
        AlertRule = monitoring_imports['AlertRule']
        
        rule = AlertRule(
            name="High CPU",
            metric_name="cpu_usage",
            operator=">",
            threshold=90,
        )
        
        assert rule.evaluate(95) is True
        assert rule.evaluate(85) is False
    
    def test_rule_evaluate_less(self, monitoring_imports):
        """Test rule evaluation with less than."""
        AlertRule = monitoring_imports['AlertRule']
        
        rule = AlertRule(
            name="Low Memory",
            metric_name="memory_free",
            operator="<",
            threshold=100,
        )
        
        assert rule.evaluate(50) is True
        assert rule.evaluate(150) is False


class TestAlert:
    """Test Alert class."""
    
    def test_alert_creation(self, monitoring_imports):
        """Test creating an alert."""
        Alert = monitoring_imports['Alert']
        AlertSeverity = monitoring_imports['AlertSeverity']
        
        alert = Alert(
            rule_name="High CPU",
            severity=AlertSeverity.WARNING,
            title="CPU usage high",
            metric_value=95,
            threshold=90,
        )
        
        assert alert.rule_name == "High CPU"
        assert alert.metric_value == 95
    
    def test_alert_acknowledge(self, monitoring_imports):
        """Test acknowledging an alert."""
        Alert = monitoring_imports['Alert']
        AlertStatus = monitoring_imports['AlertStatus']
        
        alert = Alert(rule_name="Test")
        alert.acknowledge(user="admin")
        
        assert alert.status == AlertStatus.ACKNOWLEDGED
        assert alert.acknowledged_at is not None
    
    def test_alert_resolve(self, monitoring_imports):
        """Test resolving an alert."""
        Alert = monitoring_imports['Alert']
        AlertStatus = monitoring_imports['AlertStatus']
        
        alert = Alert(rule_name="Test")
        alert.resolve()
        
        assert alert.status == AlertStatus.RESOLVED
        assert alert.resolved_at is not None


class TestAlertManager:
    """Test AlertManager class."""
    
    def test_manager_creation(self, monitoring_imports):
        """Test creating alert manager."""
        AlertManager = monitoring_imports['AlertManager']
        
        manager = AlertManager()
        assert manager is not None
    
    def test_create_rule(self, monitoring_imports):
        """Test creating an alert rule."""
        AlertManager = monitoring_imports['AlertManager']
        AlertSeverity = monitoring_imports['AlertSeverity']
        
        manager = AlertManager()
        rule = manager.create_rule(
            name="High CPU",
            metric_name="cpu_usage",
            operator=">",
            threshold=90,
            severity=AlertSeverity.WARNING,
        )
        
        assert rule.name == "High CPU"
        assert manager.get_rule(rule.rule_id) is not None
    
    def test_list_alerts(self, monitoring_imports):
        """Test listing alerts."""
        AlertManager = monitoring_imports['AlertManager']
        
        manager = AlertManager()
        
        # Alerts list should be empty initially
        alerts = manager.list_alerts()
        assert len(alerts) == 0
    
    def test_get_summary(self, monitoring_imports):
        """Test getting alert summary."""
        AlertManager = monitoring_imports['AlertManager']
        
        manager = AlertManager()
        manager.create_rule("Test Rule", "metric", ">", 50)
        
        summary = manager.get_summary()
        
        assert "total_rules" in summary
        assert "active_alerts" in summary
        assert summary["total_rules"] == 1


class TestMonitoringIntegration:
    """Integration tests for monitoring system."""
    
    def test_full_monitoring_stack(self, monitoring_imports):
        """Test complete monitoring stack."""
        MetricsCollector = monitoring_imports['MetricsCollector']
        DashboardManager = monitoring_imports['DashboardManager']
        AlertManager = monitoring_imports['AlertManager']
        DashboardWidget = monitoring_imports['DashboardWidget']
        WidgetType = monitoring_imports['WidgetType']
        AlertSeverity = monitoring_imports['AlertSeverity']
        
        # Create components
        collector = MetricsCollector()
        dashboard_mgr = DashboardManager(collector)
        alert_mgr = AlertManager(collector)
        
        # Record metrics
        collector.record("cpu_usage", 75)
        collector.record("memory_usage", 85)
        
        # Create dashboard
        dashboard = dashboard_mgr.create_dashboard(name="System")
        dashboard.add_widget(DashboardWidget(
            title="CPU",
            widget_type=WidgetType.GAUGE,
            metric_name="cpu_usage",
        ))
        
        # Create alert rule
        alert_mgr.create_rule(
            name="High Memory",
            metric_name="memory_usage",
            operator=">",
            threshold=80,
            severity=AlertSeverity.WARNING,
        )
        
        # Evaluate rules
        alert_mgr.evaluate_rules()
        
        # Check results
        summary = alert_mgr.get_summary()
        assert summary["total_rules"] == 1
        
        dashboard_data = dashboard_mgr.get_dashboard_data(dashboard.dashboard_id)
        assert len(dashboard_data["widget_data"]) == 1
    
    def test_alert_lifecycle(self, monitoring_imports):
        """Test complete alert lifecycle."""
        Alert = monitoring_imports['Alert']
        AlertSeverity = monitoring_imports['AlertSeverity']
        AlertStatus = monitoring_imports['AlertStatus']
        
        # Test manual alert lifecycle (more reliable than auto-firing)
        alert = Alert(
            rule_name="Test Alert",
            severity=AlertSeverity.WARNING,
            title="Test",
        )
        
        # Initially firing
        assert alert.status == AlertStatus.FIRING
        
        # Acknowledge
        alert.acknowledge(user="oncall")
        assert alert.status == AlertStatus.ACKNOWLEDGED
        assert alert.acknowledged_at is not None
        
        # Resolve
        alert.resolve()
        assert alert.status == AlertStatus.RESOLVED
        assert alert.resolved_at is not None


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
