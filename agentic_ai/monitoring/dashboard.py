"""
Metrics Dashboard System
=========================

Real-time dashboard for visualizing agent and workflow metrics.
"""

from typing import Dict, Any, List, Optional, Callable
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
import json


class WidgetType(str, Enum):
    """Types of dashboard widgets."""
    GAUGE = "gauge"  # Single value display
    CHART = "chart"  # Time series chart
    TABLE = "table"  # Data table
    STATUS = "status"  # Health status
    COUNTER = "counter"  # Large number display


@dataclass
class DashboardWidget:
    """Dashboard widget configuration."""
    
    widget_id: str = field(default_factory=lambda: str(hash(datetime.utcnow()))[:8])
    title: str = ""
    widget_type: WidgetType = WidgetType.GAUGE
    metric_name: str = ""
    metric_labels: Dict[str, str] = field(default_factory=dict)
    
    # Display options
    unit: str = ""
    precision: int = 2
    min_value: Optional[float] = None
    max_value: Optional[float] = None
    thresholds: Dict[str, float] = field(default_factory=dict)  # e.g., {"warning": 80, "critical": 95}
    
    # Query options
    aggregation: str = "latest"  # latest, average, sum, count
    window_seconds: int = 60
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "widget_id": self.widget_id,
            "title": self.title,
            "widget_type": self.widget_type.value,
            "metric_name": self.metric_name,
            "metric_labels": self.metric_labels,
            "unit": self.unit,
            "precision": self.precision,
            "min_value": self.min_value,
            "max_value": self.max_value,
            "thresholds": self.thresholds,
            "aggregation": self.aggregation,
            "window_seconds": self.window_seconds,
        }


@dataclass
class Dashboard:
    """Metrics dashboard configuration."""
    
    dashboard_id: str = field(default_factory=lambda: str(hash(datetime.utcnow()))[:8])
    name: str = ""
    description: str = ""
    widgets: List[DashboardWidget] = field(default_factory=list)
    
    # Layout
    columns: int = 3
    refresh_interval_seconds: int = 5
    
    # Access
    public: bool = False
    share_token: Optional[str] = None
    
    def add_widget(self, widget: DashboardWidget):
        """Add a widget to the dashboard."""
        self.widgets.append(widget)
    
    def remove_widget(self, widget_id: str):
        """Remove a widget from the dashboard."""
        self.widgets = [w for w in self.widgets if w.widget_id != widget_id]
    
    def get_widget(self, widget_id: str) -> Optional[DashboardWidget]:
        """Get a widget by ID."""
        for widget in self.widgets:
            if widget.widget_id == widget_id:
                return widget
        return None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "dashboard_id": self.dashboard_id,
            "name": self.name,
            "description": self.description,
            "widgets": [w.to_dict() for w in self.widgets],
            "columns": self.columns,
            "refresh_interval_seconds": self.refresh_interval_seconds,
            "public": self.public,
            "share_token": self.share_token,
        }


class DashboardManager:
    """Manages multiple dashboards."""
    
    def __init__(self, metrics_collector):
        self._dashboards: Dict[str, Dashboard] = {}
        self._metrics = metrics_collector
        self._update_callbacks: List[Callable] = []
    
    def create_dashboard(self, name: str, description: str = "",
                         columns: int = 3) -> Dashboard:
        """Create a new dashboard."""
        dashboard = Dashboard(
            name=name,
            description=description,
            columns=columns,
        )
        self._dashboards[dashboard.dashboard_id] = dashboard
        return dashboard
    
    def get_dashboard(self, dashboard_id: str) -> Optional[Dashboard]:
        """Get a dashboard by ID."""
        return self._dashboards.get(dashboard_id)
    
    def list_dashboards(self) -> List[Dashboard]:
        """List all dashboards."""
        return list(self._dashboards.values())
    
    def delete_dashboard(self, dashboard_id: str) -> bool:
        """Delete a dashboard."""
        if dashboard_id in self._dashboards:
            del self._dashboards[dashboard_id]
            return True
        return False
    
    def get_dashboard_data(self, dashboard_id: str) -> Dict[str, Any]:
        """Get dashboard with current metric data."""
        dashboard = self._dashboards.get(dashboard_id)
        if not dashboard:
            return {}
        
        data = dashboard.to_dict()
        data["widget_data"] = []
        
        for widget in dashboard.widgets:
            widget_data = self._get_widget_data(widget)
            data["widget_data"].append(widget_data)
        
        return data
    
    def _get_widget_data(self, widget: DashboardWidget) -> Dict[str, Any]:
        """Get current data for a widget."""
        metric = self._metrics.get_metric(widget.metric_name, widget.metric_labels)
        
        if not metric:
            return {
                "widget_id": widget.widget_id,
                "value": None,
                "status": "no_data",
            }
        
        # Calculate value based on aggregation
        value = None
        if widget.aggregation == "latest":
            value = metric.latest()
        elif widget.aggregation == "average":
            value = metric.average(widget.window_seconds)
        elif widget.aggregation == "sum":
            points = metric.points[-widget.window_seconds:] if metric.points else []
            value = sum(p.value for p in points)
        elif widget.aggregation == "count":
            value = metric.count(widget.window_seconds)
        
        # Determine status based on thresholds
        status = "ok"
        if widget.thresholds:
            if value is not None:
                if "critical" in widget.thresholds and value >= widget.thresholds["critical"]:
                    status = "critical"
                elif "warning" in widget.thresholds and value >= widget.thresholds["warning"]:
                    status = "warning"
        
        return {
            "widget_id": widget.widget_id,
            "value": round(value, widget.precision) if value is not None else None,
            "status": status,
            "unit": widget.unit,
            "title": widget.title,
            "widget_type": widget.widget_type.value,
        }
    
    def register_update_callback(self, callback: Callable):
        """Register callback for dashboard updates."""
        self._update_callbacks.append(callback)
    
    def export_config(self) -> str:
        """Export dashboard configuration as JSON."""
        config = {
            "dashboards": [d.to_dict() for d in self._dashboards.values()],
        }
        return json.dumps(config, indent=2)
    
    def import_config(self, config_json: str):
        """Import dashboard configuration from JSON."""
        config = json.loads(config_json)
        
        for dash_data in config.get("dashboards", []):
            dashboard = Dashboard(
                dashboard_id=dash_data.get("dashboard_id"),
                name=dash_data.get("name", ""),
                description=dash_data.get("description", ""),
                columns=dash_data.get("columns", 3),
            )
            
            for widget_data in dash_data.get("widgets", []):
                widget = DashboardWidget(
                    widget_id=widget_data.get("widget_id"),
                    title=widget_data.get("title", ""),
                    widget_type=WidgetType(widget_data.get("widget_type", "gauge")),
                    metric_name=widget_data.get("metric_name", ""),
                    metric_labels=widget_data.get("metric_labels", {}),
                    unit=widget_data.get("unit", ""),
                    precision=widget_data.get("precision", 2),
                    min_value=widget_data.get("min_value"),
                    max_value=widget_data.get("max_value"),
                    thresholds=widget_data.get("thresholds", {}),
                    aggregation=widget_data.get("aggregation", "latest"),
                    window_seconds=widget_data.get("window_seconds", 60),
                )
                dashboard.add_widget(widget)
            
            self._dashboards[dashboard.dashboard_id] = dashboard
