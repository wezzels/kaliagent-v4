"""
DataAnalystAgent - Data Analysis & Insights
=============================================

Provides data analysis, statistical insights, trend detection,
automated reporting, and data visualization generation.
"""

import logging
import math
import secrets
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional, Tuple


logger = logging.getLogger(__name__)


@dataclass
class Dataset:
    """Dataset metadata."""
    dataset_id: str
    name: str
    source: str
    row_count: int = 0
    column_count: int = 0
    columns: List[str] = field(default_factory=list)
    created_at: datetime = field(default_factory=datetime.utcnow)
    last_updated: Optional[datetime] = None


@dataclass
class Analysis:
    """Analysis result."""
    analysis_id: str
    name: str
    dataset_id: str
    analysis_type: str
    results: Dict[str, Any]
    insights: List[str] = field(default_factory=list)
    recommendations: List[str] = field(default_factory=list)
    created_at: datetime = field(default_factory=datetime.utcnow)


@dataclass
class Report:
    """Generated report."""
    report_id: str
    name: str
    title: str
    sections: List[Dict[str, Any]]
    generated_at: datetime = field(default_factory=datetime.utcnow)
    period_start: Optional[datetime] = None
    period_end: Optional[datetime] = None


class DataAnalystAgent:
    """
    Data Analyst Agent for statistical analysis, insights,
    trend detection, and automated reporting.
    """
    
    def __init__(self, agent_id: str = "data-analyst-agent"):
        self.agent_id = agent_id
        self.datasets: Dict[str, Dataset] = {}
        self.analyses: Dict[str, Analysis] = {}
        self.reports: Dict[str, Report] = {}
        self.data_cache: Dict[str, List[Any]] = {}
    
    # ============================================
    # Data Management
    # ============================================
    
    def register_dataset(
        self,
        name: str,
        source: str,
        columns: List[str],
        row_count: int = 0,
    ) -> Dataset:
        """Register a dataset for analysis."""
        dataset = Dataset(
            dataset_id=self._generate_id("dataset"),
            name=name,
            source=source,
            row_count=row_count,
            column_count=len(columns),
            columns=columns,
        )
        
        self.datasets[dataset.dataset_id] = dataset
        logger.info(f"Registered dataset: {dataset.name} ({row_count} rows)")
        return dataset
    
    def load_data(self, dataset_id: str, data: List[Dict[str, Any]]):
        """Load data into cache for analysis."""
        if dataset_id not in self.datasets:
            raise ValueError(f"Dataset {dataset_id} not found")
        
        self.data_cache[dataset_id] = data
        self.datasets[dataset_id].row_count = len(data)
        self.datasets[dataset_id].last_updated = datetime.utcnow()
        
        logger.info(f"Loaded {len(data)} rows into dataset {dataset_id}")
    
    # ============================================
    # Statistical Analysis
    # ============================================
    
    def calculate_statistics(self, dataset_id: str, column: str) -> Dict[str, Any]:
        """Calculate descriptive statistics for a column."""
        if dataset_id not in self.data_cache:
            raise ValueError(f"Dataset {dataset_id} not loaded")
        
        data = self.data_cache[dataset_id]
        values = [row.get(column) for row in data if column in row and isinstance(row.get(column), (int, float))]
        
        if not values:
            return {'error': f'No numeric values found for column {column}'}
        
        n = len(values)
        mean = sum(values) / n
        sorted_values = sorted(values)
        
        # Median
        if n % 2 == 0:
            median = (sorted_values[n//2 - 1] + sorted_values[n//2]) / 2
        else:
            median = sorted_values[n//2]
        
        # Min, Max
        min_val = min(values)
        max_val = max(values)
        
        # Standard deviation
        variance = sum((x - mean) ** 2 for x in values) / n
        std_dev = math.sqrt(variance)
        
        # Percentiles
        p25 = self._percentile(sorted_values, 25)
        p75 = self._percentile(sorted_values, 75)
        p95 = self._percentile(sorted_values, 95)
        
        return {
            'column': column,
            'count': n,
            'mean': round(mean, 4),
            'median': round(median, 4),
            'std_dev': round(std_dev, 4),
            'min': round(min_val, 4),
            'max': round(max_val, 4),
            'p25': round(p25, 4),
            'p75': round(p75, 4),
            'p95': round(p95, 4),
        }
    
    def _percentile(self, sorted_values: List[float], percentile: int) -> float:
        """Calculate percentile from sorted values."""
        n = len(sorted_values)
        k = (n - 1) * percentile / 100
        f = math.floor(k)
        c = math.ceil(k)
        
        if f == c:
            return sorted_values[int(k)]
        
        return sorted_values[int(f)] * (c - k) + sorted_values[int(c)] * (k - f)
    
    def detect_correlations(self, dataset_id: str, column1: str, column2: str) -> Dict[str, Any]:
        """Detect correlation between two columns."""
        if dataset_id not in self.data_cache:
            raise ValueError(f"Dataset {dataset_id} not loaded")
        
        data = self.data_cache[dataset_id]
        
        # Get paired values
        pairs = [(row.get(column1), row.get(column2)) 
                 for row in data 
                 if column1 in row and column2 in row 
                 and isinstance(row.get(column1), (int, float))
                 and isinstance(row.get(column2), (int, float))]
        
        if len(pairs) < 3:
            return {'error': 'Insufficient data points'}
        
        x_vals = [p[0] for p in pairs]
        y_vals = [p[1] for p in pairs]
        
        # Pearson correlation
        n = len(pairs)
        mean_x = sum(x_vals) / n
        mean_y = sum(y_vals) / n
        
        numerator = sum((x - mean_x) * (y - mean_y) for x, y in pairs)
        
        sum_sq_x = sum((x - mean_x) ** 2 for x in x_vals)
        sum_sq_y = sum((y - mean_y) ** 2 for y in y_vals)
        
        denominator = math.sqrt(sum_sq_x * sum_sq_y)
        
        if denominator == 0:
            correlation = 0
        else:
            correlation = numerator / denominator
        
        # Interpret correlation
        abs_corr = abs(correlation)
        if abs_corr >= 0.7:
            strength = "strong"
        elif abs_corr >= 0.4:
            strength = "moderate"
        else:
            strength = "weak"
        
        direction = "positive" if correlation > 0 else "negative"
        
        return {
            'column1': column1,
            'column2': column2,
            'correlation': round(correlation, 4),
            'strength': strength,
            'direction': direction,
            'data_points': n,
        }
    
    # ============================================
    # Trend Analysis
    # ============================================
    
    def detect_trends(self, dataset_id: str, column: str, time_column: str) -> Dict[str, Any]:
        """Detect trends in time-series data."""
        if dataset_id not in self.data_cache:
            raise ValueError(f"Dataset {dataset_id} not loaded")
        
        data = self.data_cache[dataset_id]
        
        # Sort by time
        sorted_data = sorted(data, key=lambda x: x.get(time_column, ''))
        
        values = [row.get(column) for row in sorted_data if column in row and isinstance(row.get(column), (int, float))]
        
        if len(values) < 3:
            return {'error': 'Insufficient data points'}
        
        # Simple linear regression
        n = len(values)
        x_mean = (n - 1) / 2
        y_mean = sum(values) / n
        
        numerator = sum((i - x_mean) * (values[i] - y_mean) for i in range(n))
        denominator = sum((i - x_mean) ** 2 for i in range(n))
        
        if denominator == 0:
            slope = 0
        else:
            slope = numerator / denominator
        
        # Determine trend
        if slope > 0.01:
            trend = "increasing"
        elif slope < -0.01:
            trend = "decreasing"
        else:
            trend = "stable"
        
        # Calculate growth rate
        if values[0] != 0:
            growth_rate = ((values[-1] - values[0]) / abs(values[0])) * 100
        else:
            growth_rate = 0
        
        return {
            'column': column,
            'trend': trend,
            'slope': round(slope, 6),
            'growth_rate_percent': round(growth_rate, 2),
            'start_value': values[0],
            'end_value': values[-1],
            'data_points': n,
        }
    
    def detect_anomalies(self, dataset_id: str, column: str, threshold: float = 2.0) -> List[Dict[str, Any]]:
        """Detect anomalies using z-score method."""
        if dataset_id not in self.data_cache:
            raise ValueError(f"Dataset {dataset_id} not loaded")
        
        data = self.data_cache[dataset_id]
        values = [(i, row.get(column)) 
                  for i, row in enumerate(data) 
                  if column in row and isinstance(row.get(column), (int, float))]
        
        if len(values) < 3:
            return []
        
        numeric_values = [v[1] for v in values]
        mean = sum(numeric_values) / len(numeric_values)
        variance = sum((x - mean) ** 2 for x in numeric_values) / len(numeric_values)
        std_dev = math.sqrt(variance)
        
        if std_dev == 0:
            return []
        
        anomalies = []
        for idx, value in values:
            z_score = (value - mean) / std_dev
            
            if abs(z_score) > threshold:
                anomalies.append({
                    'index': idx,
                    'value': value,
                    'z_score': round(z_score, 4),
                    'deviation': 'above' if z_score > 0 else 'below',
                })
        
        return anomalies
    
    # ============================================
    # Insights & Recommendations
    # ============================================
    
    def generate_insights(self, dataset_id: str) -> Analysis:
        """Generate automated insights for a dataset."""
        if dataset_id not in self.data_cache:
            raise ValueError(f"Dataset {dataset_id} not loaded")
        
        dataset = self.datasets[dataset_id]
        insights = []
        recommendations = []
        results = {}
        
        # Calculate statistics for numeric columns
        numeric_stats = {}
        for column in dataset.columns:
            stats = self.calculate_statistics(dataset_id, column)
            if 'error' not in stats:
                numeric_stats[column] = stats
                
                # Generate insights
                if stats['std_dev'] > stats['mean'] * 0.5:
                    insights.append(f"High variability in {column} (std_dev > 50% of mean)")
                
                if stats['p95'] > stats['mean'] * 2:
                    insights.append(f"Outliers detected in {column} (P95 > 2x mean)")
        
        results['statistics'] = numeric_stats
        
        # Detect correlations between numeric columns
        correlations = []
        numeric_cols = list(numeric_stats.keys())
        for i, col1 in enumerate(numeric_cols):
            for col2 in numeric_cols[i+1:]:
                corr = self.detect_correlations(dataset_id, col1, col2)
                if 'error' not in corr and corr['strength'] in ['strong', 'moderate']:
                    correlations.append(corr)
                    insights.append(f"{corr['strength'].capitalize()} {corr['direction']} correlation between {col1} and {col2}")
        
        results['correlations'] = correlations
        
        # Generate recommendations
        if len(numeric_stats) > 0:
            recommendations.append("Consider normalizing high-variance features")
        
        if len(correlations) > 0:
            recommendations.append("Investigate correlated features for potential multicollinearity")
        
        analysis = Analysis(
            analysis_id=self._generate_id("analysis"),
            name=f"Auto-insights: {dataset.name}",
            dataset_id=dataset_id,
            analysis_type="automated_insights",
            results=results,
            insights=insights,
            recommendations=recommendations,
        )
        
        self.analyses[analysis.analysis_id] = analysis
        return analysis
    
    # ============================================
    # Reporting
    # ============================================
    
    def generate_report(
        self,
        name: str,
        title: str,
        dataset_ids: List[str],
        period_start: Optional[datetime] = None,
        period_end: Optional[datetime] = None,
    ) -> Report:
        """Generate a comprehensive analysis report."""
        sections = []
        
        for dataset_id in dataset_ids:
            if dataset_id not in self.datasets:
                continue
            
            dataset = self.datasets[dataset_id]
            
            # Dataset overview
            section = {
                'type': 'dataset_overview',
                'dataset_name': dataset.name,
                'source': dataset.source,
                'row_count': dataset.row_count,
                'column_count': dataset.column_count,
            }
            
            # Add statistics
            stats = {}
            for column in dataset.columns[:5]:  # Limit to first 5 columns
                col_stats = self.calculate_statistics(dataset_id, column)
                if 'error' not in col_stats:
                    stats[column] = col_stats
            
            section['statistics'] = stats
            sections.append(section)
        
        report = Report(
            report_id=self._generate_id("report"),
            name=name,
            title=title,
            sections=sections,
            period_start=period_start,
            period_end=period_end,
        )
        
        self.reports[report.report_id] = report
        logger.info(f"Generated report: {report.name}")
        return report
    
    def get_report(self, report_id: str) -> Optional[Report]:
        """Get a report by ID."""
        return self.reports.get(report_id)
    
    # ============================================
    # Utilities
    # ============================================
    
    def _generate_id(self, prefix: str) -> str:
        """Generate a unique ID."""
        timestamp = datetime.utcnow().strftime('%Y%m%d%H%M%S')
        random_suffix = secrets.token_hex(4)
        return f"{prefix}-{timestamp}-{random_suffix}"
    
    def get_state(self) -> Dict[str, Any]:
        """Get agent state summary."""
        return {
            'agent_id': self.agent_id,
            'datasets_count': len(self.datasets),
            'analyses_count': len(self.analyses),
            'reports_count': len(self.reports),
            'cached_data_size': sum(len(d) for d in self.data_cache.values()),
        }


def get_capabilities() -> Dict[str, Any]:
    """Return agent capabilities for orchestration."""
    return {
        'agent_type': 'data_analyst',
        'version': '1.0.0',
        'capabilities': [
            'register_dataset',
            'load_data',
            'calculate_statistics',
            'detect_correlations',
            'detect_trends',
            'detect_anomalies',
            'generate_insights',
            'generate_report',
            'get_report',
        ],
        'analysis_types': [
            'descriptive_statistics',
            'correlation_analysis',
            'trend_analysis',
            'anomaly_detection',
            'automated_insights',
        ],
    }


if __name__ == "__main__":
    # Quick test
    agent = DataAnalystAgent()
    
    # Register dataset
    dataset = agent.register_dataset(
        name="Sales Data",
        source="database",
        columns=['date', 'revenue', 'customers', 'orders'],
        row_count=1000,
    )
    
    # Load sample data
    import random
    data = [
        {
            'date': f"2026-01-{i:02d}",
            'revenue': random.randint(1000, 10000),
            'customers': random.randint(50, 200),
            'orders': random.randint(100, 500),
        }
        for i in range(1, 31)
    ]
    
    agent.load_data(dataset.dataset_id, data)
    
    # Calculate statistics
    stats = agent.calculate_statistics(dataset.dataset_id, 'revenue')
    print(f"Revenue statistics: {stats}")
    
    # Generate insights
    insights = agent.generate_insights(dataset.dataset_id)
    print(f"\nInsights: {len(insights.insights)}")
    for insight in insights.insights[:3]:
        print(f"  - {insight}")
    
    print(f"\nState: {agent.get_state()}")
