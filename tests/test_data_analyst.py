"""
DataAnalystAgent Tests
======================

Unit tests for DataAnalystAgent - data analysis, statistical insights,
trend detection, and automated reporting.
"""

import pytest
import random
from datetime import datetime, timedelta

from agentic_ai.agents.data_analyst import DataAnalystAgent


class TestDataAnalystInitialization:
    """Test DataAnalystAgent initialization."""
    
    def test_agent_creation(self):
        """Test agent can be created."""
        agent = DataAnalystAgent()
        assert agent.agent_id == "data-analyst-agent"
        assert len(agent.datasets) == 0
    
    def test_get_state(self):
        """Test state summary."""
        agent = DataAnalystAgent()
        state = agent.get_state()
        
        assert 'agent_id' in state
        assert 'datasets_count' in state
        assert 'analyses_count' in state
        assert 'reports_count' in state


class TestDatasetManagement:
    """Test dataset management."""
    
    @pytest.fixture
    def analyst(self):
        """Create DataAnalystAgent instance."""
        return DataAnalystAgent()
    
    def test_register_dataset(self, analyst):
        """Test dataset registration."""
        dataset = analyst.register_dataset(
            name="Sales Data",
            source="database",
            columns=['date', 'revenue', 'customers'],
            row_count=1000,
        )
        
        assert dataset.dataset_id.startswith("dataset-")
        assert dataset.name == "Sales Data"
        assert dataset.column_count == 3
        assert dataset.row_count == 1000
    
    def test_load_data(self, analyst):
        """Test loading data."""
        dataset = analyst.register_dataset(
            name="Test Data",
            source="test",
            columns=['value'],
        )
        
        data = [{'value': i} for i in range(100)]
        analyst.load_data(dataset.dataset_id, data)
        
        assert dataset.dataset_id in analyst.data_cache
        assert len(analyst.data_cache[dataset.dataset_id]) == 100
        assert dataset.row_count == 100


class TestStatisticalAnalysis:
    """Test statistical analysis."""
    
    @pytest.fixture
    def analyst_with_data(self):
        """Create DataAnalystAgent with sample data."""
        agent = DataAnalystAgent()
        dataset = agent.register_dataset(
            name="Test Stats",
            source="test",
            columns=['value'],
        )
        
        # Load predictable data
        data = [{'value': float(i)} for i in range(1, 101)]  # 1-100
        agent.load_data(dataset.dataset_id, data)
        
        return agent
    
    def test_calculate_statistics(self, analyst_with_data):
        """Test descriptive statistics."""
        stats = analyst_with_data.calculate_statistics(
            analyst_with_data.datasets[list(analyst_with_data.datasets.keys())[0]].dataset_id,
            'value',
        )
        
        assert 'count' in stats
        assert 'mean' in stats
        assert 'median' in stats
        assert 'std_dev' in stats
        assert 'min' in stats
        assert 'max' in stats
        assert 'p25' in stats
        assert 'p75' in stats
        assert 'p95' in stats
        
        # Verify calculations for 1-100
        assert stats['count'] == 100
        assert stats['mean'] == 50.5
        assert stats['min'] == 1.0
        assert stats['max'] == 100.0
    
    def test_statistics_no_numeric_data(self, analyst_with_data):
        """Test statistics with non-numeric column."""
        dataset_id = list(analyst_with_data.datasets.keys())[0]
        stats = analyst_with_data.calculate_statistics(dataset_id, 'nonexistent')
        
        assert 'error' in stats


class TestCorrelationAnalysis:
    """Test correlation detection."""
    
    @pytest.fixture
    def analyst_correlation_data(self):
        """Create DataAnalystAgent with correlated data."""
        agent = DataAnalystAgent()
        dataset = agent.register_dataset(
            name="Correlation Test",
            source="test",
            columns=['x', 'y'],
        )
        
        # Create positively correlated data
        data = [{'x': float(i), 'y': float(i * 2 + random.randint(0, 10))} for i in range(50)]
        agent.load_data(dataset.dataset_id, data)
        
        return agent
    
    def test_detect_correlations(self, analyst_correlation_data):
        """Test correlation detection."""
        dataset_id = list(analyst_correlation_data.datasets.keys())[0]
        
        corr = analyst_correlation_data.detect_correlations(
            dataset_id,
            'x',
            'y',
        )
        
        assert 'correlation' in corr
        assert 'strength' in corr
        assert 'direction' in corr
        
        # Should detect positive correlation
        assert corr['correlation'] > 0.5
        assert corr['direction'] == 'positive'


class TestTrendAnalysis:
    """Test trend detection."""
    
    @pytest.fixture
    def analyst_trend_data(self):
        """Create DataAnalystAgent with trending data."""
        agent = DataAnalystAgent()
        dataset = agent.register_dataset(
            name="Trend Test",
            source="test",
            columns=['date', 'value'],
        )
        
        # Create increasing trend
        data = [
            {'date': f"2026-01-{i:02d}", 'value': float(i * 10)}
            for i in range(1, 31)
        ]
        agent.load_data(dataset.dataset_id, data)
        
        return agent
    
    def test_detect_trends(self, analyst_trend_data):
        """Test trend detection."""
        dataset_id = list(analyst_trend_data.datasets.keys())[0]
        
        trend = analyst_trend_data.detect_trends(
            dataset_id,
            'value',
            'date',
        )
        
        assert 'trend' in trend
        assert 'slope' in trend
        assert 'growth_rate_percent' in trend
        
        # Should detect increasing trend
        assert trend['trend'] == 'increasing'
        assert trend['slope'] > 0


class TestAnomalyDetection:
    """Test anomaly detection."""
    
    @pytest.fixture
    def analyst_anomaly_data(self):
        """Create DataAnalystAgent with anomalous data."""
        agent = DataAnalystAgent()
        dataset = agent.register_dataset(
            name="Anomaly Test",
            source="test",
            columns=['value'],
        )
        
        # Create data with outliers
        data = [{'value': float(50 + random.randint(-5, 5))} for _ in range(98)]
        data.append({'value': 200.0})  # Outlier high
        data.append({'value': -100.0})  # Outlier low
        
        agent.load_data(dataset.dataset_id, data)
        
        return agent
    
    def test_detect_anomalies(self, analyst_anomaly_data):
        """Test anomaly detection."""
        dataset_id = list(analyst_anomaly_data.datasets.keys())[0]
        
        anomalies = analyst_anomaly_data.detect_anomalies(
            dataset_id,
            'value',
            threshold=2.0,
        )
        
        assert isinstance(anomalies, list)
        assert len(anomalies) >= 2  # Should find both outliers
        
        # Verify anomaly structure
        for anomaly in anomalies:
            assert 'index' in anomaly
            assert 'value' in anomaly
            assert 'z_score' in anomaly
            assert 'deviation' in anomaly


class TestInsightsGeneration:
    """Test automated insights generation."""
    
    @pytest.fixture
    def analyst_insight_data(self):
        """Create DataAnalystAgent with insight-worthy data."""
        agent = DataAnalystAgent()
        dataset = agent.register_dataset(
            name="Insights Test",
            source="test",
            columns=['revenue', 'customers', 'orders'],
        )
        
        # Create varied data
        data = [
            {
                'revenue': float(random.randint(1000, 10000)),
                'customers': float(random.randint(50, 200)),
                'orders': float(random.randint(100, 500)),
            }
            for _ in range(100)
        ]
        
        agent.load_data(dataset.dataset_id, data)
        
        return agent
    
    def test_generate_insights(self, analyst_insight_data):
        """Test insight generation."""
        dataset_id = list(analyst_insight_data.datasets.keys())[0]
        
        analysis = analyst_insight_data.generate_insights(dataset_id)
        
        assert analysis.analysis_id.startswith("analysis-")
        # Insights may or may not be generated depending on data variance
        # Just verify the analysis was created with results
        assert 'statistics' in analysis.results
        assert 'correlations' in analysis.results
        
        # Should have at least one recommendation
        assert len(analysis.recommendations) > 0


class TestReporting:
    """Test report generation."""
    
    @pytest.fixture
    def analyst_report_data(self):
        """Create DataAnalystAgent with report data."""
        agent = DataAnalystAgent()
        
        # Create two datasets
        dataset1 = agent.register_dataset(
            name="Sales Q1",
            source="database",
            columns=['date', 'revenue'],
        )
        
        dataset2 = agent.register_dataset(
            name="Sales Q2",
            source="database",
            columns=['date', 'revenue'],
        )
        
        # Load data
        data1 = [{'date': f"2026-0{i}-01", 'revenue': float(i * 1000)} for i in range(1, 4)]
        data2 = [{'date': f"2026-0{i}-01", 'revenue': float(i * 1200)} for i in range(4, 7)]
        
        agent.load_data(dataset1.dataset_id, data1)
        agent.load_data(dataset2.dataset_id, data2)
        
        return agent
    
    def test_generate_report(self, analyst_report_data):
        """Test report generation."""
        dataset_ids = list(analyst_report_data.datasets.keys())
        
        report = analyst_report_data.generate_report(
            name="Quarterly Sales Report",
            title="Q1-Q2 Sales Analysis",
            dataset_ids=dataset_ids,
        )
        
        assert report.report_id.startswith("report-")
        assert report.name == "Quarterly Sales Report"
        assert len(report.sections) >= 2
        
        # Verify sections
        for section in report.sections:
            assert 'type' in section
            assert 'dataset_name' in section
    
    def test_get_report(self, analyst_report_data):
        """Test retrieving report."""
        dataset_ids = list(analyst_report_data.datasets.keys())
        
        report = analyst_report_data.generate_report(
            name="Test Report",
            title="Test",
            dataset_ids=dataset_ids,
        )
        
        retrieved = analyst_report_data.get_report(report.report_id)
        
        assert retrieved is not None
        assert retrieved.report_id == report.report_id


class TestDataAnalystCapabilities:
    """Test capabilities export for orchestration."""
    
    def test_get_capabilities(self):
        """Test capabilities export."""
        from agentic_ai.agents.data_analyst import get_capabilities
        
        caps = get_capabilities()
        
        assert caps['agent_type'] == 'data_analyst'
        assert len(caps['capabilities']) >= 9
        
        # Verify key capabilities
        required = [
            'register_dataset', 'load_data',
            'calculate_statistics', 'detect_correlations',
            'detect_trends', 'detect_anomalies',
            'generate_insights', 'generate_report',
        ]
        
        for cap in required:
            assert cap in caps['capabilities'], f"Missing: {cap}"
        
        # Verify analysis types
        assert len(caps['analysis_types']) >= 5


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
