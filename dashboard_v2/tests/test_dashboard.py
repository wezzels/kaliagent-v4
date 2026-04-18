#!/usr/bin/env python3
"""
Agentic AI Dashboard v2.0 - Backend Tests
Test the FastAPI server endpoints and WebSocket functionality
"""

import pytest
from fastapi.testclient import TestClient
import sys
import os

# Add backend to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'backend'))

from server import app

client = TestClient(app)


class TestHealthEndpoints:
    """Test health and status endpoints"""

    def test_root_endpoint(self):
        """Test root endpoint returns HTML"""
        response = client.get("/")
        assert response.status_code == 200
        assert "text/html" in response.headers["content-type"]

    def test_health_check(self):
        """Test health check endpoint"""
        response = client.get("/api/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert data["version"] == "2.0.0"
        assert "timestamp" in data
        assert data["agents_loaded"] == 6

    def test_health_check_structure(self):
        """Test health check response structure"""
        response = client.get("/api/health")
        data = response.json()
        
        required_fields = ["status", "version", "timestamp", "agents_loaded"]
        for field in required_fields:
            assert field in data, f"Missing required field: {field}"


class TestAgentsEndpoints:
    """Test agent-related endpoints"""

    def test_get_all_agents(self):
        """Test getting all agents"""
        response = client.get("/api/agents")
        assert response.status_code == 200
        data = response.json()
        
        assert isinstance(data, dict)
        assert len(data) == 6
        
        # Check expected agents
        expected_agents = ["soc", "vulnman", "redteam", "malware", "security", "cloudsec"]
        for agent_id in expected_agents:
            assert agent_id in data

    def test_get_specific_agent(self):
        """Test getting a specific agent"""
        response = client.get("/api/agents/soc")
        assert response.status_code == 200
        data = response.json()
        
        assert data["name"] == "SOC Agent"
        assert data["type"] == "security"
        assert data["status"] == "online"
        assert "capabilities" in data
        assert isinstance(data["capabilities"], list)

    def test_agent_not_found(self):
        """Test 404 for non-existent agent"""
        response = client.get("/api/agents/nonexistent")
        assert response.status_code == 404

    def test_agent_structure(self):
        """Test agent response structure"""
        response = client.get("/api/agents/vulnman")
        data = response.json()
        
        required_fields = [
            "name", "type", "status", "capabilities",
            "requests_per_minute", "avg_latency_ms", "success_rate", "last_active"
        ]
        for field in required_fields:
            assert field in data, f"Missing required field: {field}"


class TestCyberAgentsEndpoints:
    """Test Cyber Division endpoints"""

    def test_get_cyber_agents(self):
        """Test getting all cyber agents"""
        response = client.get("/api/cyber-agents")
        assert response.status_code == 200
        data = response.json()
        
        assert isinstance(data, list)
        assert len(data) == 6

    def test_cyber_agent_structure(self):
        """Test cyber agent response structure"""
        response = client.get("/api/cyber-agents")
        data = response.json()
        
        required_fields = [
            "name", "icon", "description", "capabilities",
            "tools_available", "active_engagements", "success_rate"
        ]
        
        for agent in data:
            for field in required_fields:
                assert field in agent, f"Missing required field: {field}"

    def test_get_specific_cyber_agent(self):
        """Test getting a specific cyber agent"""
        response = client.get("/api/cyber-agents/soc")
        assert response.status_code == 200
        data = response.json()
        
        assert data["name"] == "SOC Agent"
        assert data["icon"] == "🛡️"

    def test_cyber_agent_not_found(self):
        """Test 404 for non-existent cyber agent"""
        response = client.get("/api/cyber-agents/nonexistent")
        assert response.status_code == 404


class TestMetricsEndpoints:
    """Test metrics endpoints"""

    def test_get_metrics(self):
        """Test getting live metrics"""
        response = client.get("/api/metrics")
        assert response.status_code == 200
        data = response.json()
        
        required_fields = [
            "total_requests", "active_agents", "avg_latency",
            "error_rate", "requests_per_second"
        ]
        for field in required_fields:
            assert field in data, f"Missing required field: {field}"

    def test_metrics_values(self):
        """Test metrics have reasonable values"""
        response = client.get("/api/metrics")
        data = response.json()
        
        assert data["active_agents"] == 6
        assert data["total_requests"] > 0
        assert 0 <= data["error_rate"] <= 100
        assert data["avg_latency"] > 0

    def test_metrics_history(self):
        """Test metrics history endpoint"""
        response = client.get("/api/metrics/history/requests")
        assert response.status_code == 200
        data = response.json()
        
        assert isinstance(data, list)
        assert len(data) == 50  # Default points
        
        for point in data:
            assert "timestamp" in point
            assert "value" in point

    def test_metrics_history_custom_points(self):
        """Test metrics history with custom points"""
        response = client.get("/api/metrics/history/latency?points=20")
        assert response.status_code == 200
        data = response.json()
        
        assert len(data) == 20

    def test_metrics_history_types(self):
        """Test different metric types"""
        metric_types = ["requests", "latency", "errors", "agents"]
        
        for metric_type in metric_types:
            response = client.get(f"/api/metrics/history/{metric_type}")
            assert response.status_code == 200


class TestDemosEndpoints:
    """Test demo endpoints"""

    def test_chaos_demo(self):
        """Test chaos engineering demo endpoint"""
        response = client.get("/api/demos/chaos")
        assert response.status_code == 200
        data = response.json()
        
        assert "experiments" in data
        assert "overall_resiliency" in data
        assert "total_experiments" in data
        assert "success_rate" in data
        
        assert len(data["experiments"]) == 3

    def test_chaos_experiment_structure(self):
        """Test chaos experiment structure"""
        response = client.get("/api/demos/chaos")
        data = response.json()
        
        experiment = data["experiments"][0]
        required_fields = ["name", "status", "target", "started", "duration", "resiliency_score"]
        
        for field in required_fields:
            assert field in experiment, f"Missing required field: {field}"


class TestExamplesEndpoints:
    """Test example endpoints"""

    def test_kaliagent_examples(self):
        """Test KaliAgent examples endpoint"""
        response = client.get("/api/examples/kaliagent")
        assert response.status_code == 200
        data = response.json()
        
        assert "examples" in data
        assert "total_playbooks" in data
        assert "total_tools" in data
        
        assert len(data["examples"]) == 3
        assert data["total_tools"] == 52

    def test_example_structure(self):
        """Test example structure"""
        response = client.get("/api/examples/kaliagent")
        data = response.json()
        
        example = data["examples"][0]
        required_fields = [
            "name", "description", "playbook", "tools",
            "duration", "authorization"
        ]
        
        for field in required_fields:
            assert field in example, f"Missing required field: {field}"


class TestWebSocket:
    """Test WebSocket endpoints"""

    def test_websocket_metrics(self):
        """Test WebSocket metrics endpoint"""
        from starlette.websockets import WebSocketDisconnect
        
        with client.websocket_connect("/ws/metrics") as websocket:
            data = websocket.receive_json()
            assert data["type"] == "metrics"
            assert "data" in data

    def test_websocket_agents(self):
        """Test WebSocket agents endpoint"""
        with client.websocket_connect("/ws/agents") as websocket:
            data = websocket.receive_json()
            assert data["type"] == "agents"
            assert "data" in data


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
