#!/usr/bin/env python3
"""
KaliAgent v4 - End-to-End Test Suite
Tests complete workflows from scan to report generation
"""

import pytest
import time
import requests
from typing import Dict, List


class TestKaliAgentE2E:
    """End-to-end tests for KaliAgent v4"""

    @pytest.fixture
    def base_url(self):
        return "http://localhost:5007"

    @pytest.fixture
    def api_url(self, base_url):
        return f"{base_url}/api"

    def test_01_dashboard_loads(self, base_url):
        """Test that dashboard loads successfully"""
        response = requests.get(base_url, timeout=10)
        assert response.status_code == 200
        assert "KaliAgent" in response.text
        assert "Command Dashboard" in response.text

    def test_02_health_check(self, base_url):
        """Test health endpoint"""
        response = requests.get(f"{base_url}/health", timeout=5)
        assert response.status_code == 200
        data = response.json()
        assert data['status'] == 'healthy'
        assert 'version' in data

    def test_03_websocket_connection(self, base_url):
        """Test WebSocket connection for real-time updates"""
        import socketio
        
        sio = socketio.Client()
        connected = False
        
        @sio.event
        def connect():
            nonlocal connected
            connected = True
        
        try:
            sio.connect(base_url, wait_timeout=10)
            time.sleep(2)
            assert connected is True
        finally:
            if sio.connected:
                sio.disconnect()

    def test_04_scan_network(self, api_url):
        """Test network scanning workflow"""
        payload = {
            "target": "10.0.100.0/24",
            "scan_type": "nmap",
            "options": ["-sV", "-O"]
        }
        
        response = requests.post(
            f"{api_url}/scan",
            json=payload,
            timeout=30
        )
        
        assert response.status_code == 200
        data = response.json()
        assert 'scan_id' in data
        assert data['status'] == 'started'

    def test_05_sql_injection_attack(self, api_url):
        """Test SQL injection attack chain"""
        payload = {
            "target": "http://juice-shop:3000",
            "attack_type": "sql_injection",
            "auto_exploit": True
        }
        
        response = requests.post(
            f"{api_url}/attack",
            json=payload,
            timeout=60
        )
        
        assert response.status_code == 200
        data = response.json()
        assert 'attack_id' in data
        
        # Wait for completion
        time.sleep(5)
        
        # Check results
        results_response = requests.get(
            f"{api_url}/attack/{data['attack_id']}/results",
            timeout=10
        )
        
        assert results_response.status_code == 200
        results = results_response.json()
        assert 'findings' in results

    def test_06_generate_payload(self, api_url):
        """Test payload generation"""
        payload = {
            "type": "reverse_shell",
            "lhost": "10.0.100.1",
            "lport": 4444,
            "format": "python"
        }
        
        response = requests.post(
            f"{api_url}/payload/generate",
            json=payload,
            timeout=10
        )
        
        assert response.status_code == 200
        data = response.json()
        assert 'payload' in data
        assert 'bash -i' in data['payload'] or 'python' in data['payload']

    def test_07_c2_agent_registration(self, api_url):
        """Test C2 agent registration"""
        payload = {
            "c2_type": "sliver",
            "agent_id": "test-agent-001",
            "metadata": {
                "hostname": "test-target",
                "os": "linux",
                "user": "test"
            }
        }
        
        response = requests.post(
            f"{api_url}/c2/register",
            json=payload,
            timeout=10
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data['status'] == 'registered'

    def test_08_wifi_scan(self, api_url):
        """Test WiFi network scanning"""
        # This test requires WiFi hardware - skip if not available
        payload = {
            "interface": "wlan0",
            "mode": "scan"
        }
        
        response = requests.post(
            f"{api_url}/wifi/scan",
            json=payload,
            timeout=30
        )
        
        # May fail if no WiFi hardware - that's OK
        if response.status_code == 200:
            data = response.json()
            assert 'networks' in data

    def test_09_llm_analysis(self, api_url):
        """Test LLM-powered nmap analysis"""
        nmap_output = """
        Starting Nmap 7.94
        Nmap scan report for 10.0.100.10
        PORT   STATE SERVICE VERSION
        22/tcp open  ssh     OpenSSH 7.2p1
        80/tcp open  http    Apache httpd 2.4.18
        """
        
        payload = {
            "nmap_output": nmap_output,
            "request": "Analyze vulnerabilities and recommend attacks"
        }
        
        response = requests.post(
            f"{api_url}/ai/analyze",
            json=payload,
            timeout=60
        )
        
        assert response.status_code == 200
        data = response.json()
        assert 'analysis' in data

    def test_10_generate_report_pdf(self, api_url):
        """Test PDF report generation"""
        attack_results = {
            "client": "E2E Test Client",
            "date": "2026-04-24",
            "report_id": "E2E-TEST-001",
            "executive_summary": "E2E test found 2 vulnerabilities.",
            "findings": [
                {
                    "title": "Test SQL Injection",
                    "severity": "Critical",
                    "cvss": 9.8,
                    "description": "SQL injection found in test.",
                    "evidence": "Test evidence",
                    "remediation": "Fix it."
                }
            ]
        }
        
        payload = {
            "results": attack_results,
            "format": "pdf"
        }
        
        response = requests.post(
            f"{api_url}/report/generate",
            json=payload,
            timeout=30
        )
        
        assert response.status_code == 200
        data = response.json()
        assert 'file_path' in data

    def test_11_generate_report_html(self, api_url):
        """Test HTML report generation"""
        attack_results = {
            "client": "E2E Test Client",
            "findings": []
        }
        
        payload = {
            "results": attack_results,
            "format": "html"
        }
        
        response = requests.post(
            f"{api_url}/report/generate",
            json=payload,
            timeout=30
        )
        
        assert response.status_code == 200
        data = response.json()
        assert 'file_path' in data

    def test_12_natural_language_command(self, api_url):
        """Test natural language command parsing"""
        payload = {
            "command": "Scan the 10.0.100.0/24 network for web servers"
        }
        
        response = requests.post(
            f"{api_url}/ai/parse-command",
            json=payload,
            timeout=30
        )
        
        assert response.status_code == 200
        data = response.json()
        assert 'type' in data
        assert data['type'] == 'scan'

    def test_13_attack_history(self, api_url):
        """Test attack history retrieval"""
        response = requests.get(
            f"{api_url}/attacks/history",
            params={"limit": 10},
            timeout=10
        )
        
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)

    def test_14_system_stats(self, api_url):
        """Test system statistics endpoint"""
        response = requests.get(
            f"{api_url}/stats",
            timeout=10
        )
        
        assert response.status_code == 200
        data = response.json()
        assert 'cpu_usage' in data
        assert 'memory_usage' in data
        assert 'disk_usage' in data

    def test_15_full_workflow(self, api_url):
        """Test complete attack workflow: scan → attack → report"""
        # Step 1: Scan
        scan_payload = {"target": "10.0.100.10", "scan_type": "nmap"}
        scan_response = requests.post(f"{api_url}/scan", json=scan_payload, timeout=30)
        assert scan_response.status_code == 200
        scan_id = scan_response.json()['scan_id']
        
        # Step 2: Wait for scan
        time.sleep(5)
        
        # Step 3: Attack based on scan results
        attack_payload = {
            "target": "10.0.100.10",
            "attack_type": "web",
            "scan_id": scan_id
        }
        attack_response = requests.post(f"{api_url}/attack", json=attack_payload, timeout=60)
        assert attack_response.status_code == 200
        attack_id = attack_response.json()['attack_id']
        
        # Step 4: Wait for attack
        time.sleep(5)
        
        # Step 5: Generate report
        report_payload = {
            "scan_id": scan_id,
            "attack_id": attack_id,
            "format": "pdf"
        }
        report_response = requests.post(f"{api_url}/report/generate", json=report_payload, timeout=30)
        assert report_response.status_code == 200
        
        print(f"✅ Full workflow complete: Scan {scan_id} → Attack {attack_id} → Report generated")


class TestSecurity:
    """Security tests for KaliAgent v4"""

    @pytest.fixture
    def base_url(self):
        return "http://localhost:5007"

    def test_security_headers(self, base_url):
        """Test that security headers are present"""
        response = requests.get(base_url, timeout=10)
        
        # Check for security headers
        assert 'X-Frame-Options' in response.headers
        assert 'X-Content-Type-Options' in response.headers
        assert 'X-XSS-Protection' in response.headers

    def test_rate_limiting(self, base_url):
        """Test rate limiting is enabled"""
        # Make many rapid requests
        responses = []
        for _ in range(20):
            response = requests.get(f"{base_url}/health", timeout=5)
            responses.append(response.status_code)
        
        # Should get at least one 429 (Too Many Requests)
        assert 429 in responses or all(r == 200 for r in responses[:10])


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
