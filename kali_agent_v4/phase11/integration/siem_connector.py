#!/usr/bin/env python3
"""
🎯 KaliAgent v4.4.0 - Phase 11: Automated Threat Hunting
SIEM Integration Module

SIEM/SOAR platform integrations:
- Splunk integration
- Elastic SIEM integration
- Microsoft Sentinel integration
- Generic syslog support
- Alert forwarding
- Query abstraction layer

Author: KaliAgent Team
Started: April 28, 2026
Status: Alpha (0.1.0)
"""

import logging
import json
import requests
from typing import List, Dict, Optional
from datetime import datetime, timedelta
from abc import ABC, abstractmethod

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger('SIEMConnector')


class SIEMConnector(ABC):
    """Base class for SIEM connectors"""
    
    def __init__(self, config: Dict):
        self.config = config
        self.connected = False
    
    @abstractmethod
    def connect(self) -> bool:
        """Establish connection to SIEM"""
        pass
    
    @abstractmethod
    def query(self, query_string: str, time_range: Dict = None) -> List[Dict]:
        """Execute query against SIEM"""
        pass
    
    @abstractmethod
    def send_alert(self, alert: Dict) -> bool:
        """Send alert to SIEM"""
        pass


class SplunkConnector(SIEMConnector):
    """
    Splunk SIEM Connector
    
    Supports:
    - Splunk Enterprise
    - Splunk Cloud
    - Splunk REST API
    """
    
    def __init__(self, config: Dict):
        super().__init__(config)
        self.host = config.get('host', 'localhost')
        self.port = config.get('port', 8089)
        self.username = config.get('username')
        self.password = config.get('password')
        self.token = config.get('token')  # Optional: use token auth
        self.session_key = None
        
        logger.info(f"🔌 Splunk Connector: {self.host}:{self.port}")
    
    def connect(self) -> bool:
        """Connect to Splunk"""
        try:
            if self.token:
                # Token authentication
                self.session_key = self.token
                self.connected = True
            else:
                # Username/password authentication
                url = f"https://{self.host}:{self.port}/services/auth/login"
                data = {
                    'username': self.username,
                    'password': self.password,
                    'output_mode': 'json'
                }
                
                response = requests.post(url, data=data, verify=False)
                
                if response.status_code == 200:
                    self.session_key = response.json().get('sessionKey')
                    self.connected = True
                    logger.info("✅ Connected to Splunk")
                else:
                    logger.error(f"❌ Splunk auth failed: {response.status_code}")
                    self.connected = False
            
            return self.connected
            
        except Exception as e:
            logger.error(f"❌ Splunk connection error: {e}")
            self.connected = False
            return False
    
    def query(self, query_string: str, time_range: Dict = None) -> List[Dict]:
        """Execute SPL query against Splunk"""
        if not self.connected:
            logger.error("Not connected to Splunk")
            return []
        
        try:
            # Set time range
            if time_range:
                earliest = time_range.get('earliest', '-1h')
                latest = time_range.get('latest', 'now')
            else:
                earliest = '-1h'
                latest = 'now'
            
            # Create search job
            url = f"https://{self.host}:{self.port}/services/search/jobs"
            headers = {'Authorization': f'Splunk {self.session_key}'}
            data = {
                'search': query_string,
                'earliest_time': earliest,
                'latest_time': latest,
                'output_mode': 'json',
                'exec_mode': 'normal'
            }
            
            response = requests.post(url, headers=headers, data=data, verify=False)
            
            if response.status_code == 201:
                sid = response.json().get('sid')
                
                # Wait for job to complete
                job_url = f"{url}/{sid}"
                import time
                while True:
                    job_response = requests.get(job_url, headers=headers, verify=False)
                    job_status = job_response.json().get('entry', [{}])[0].get('content', {})
                    
                    if job_status.get('isDone'):
                        break
                    time.sleep(1)
                
                # Get results
                results_url = f"{job_url}/results"
                results_response = requests.get(results_url, headers=headers, verify=False)
                
                if results_response.status_code == 200:
                    results = results_response.json().get('results', [])
                    logger.info(f"✅ Query returned {len(results)} results")
                    return results
            
            logger.error(f"❌ Splunk query failed: {response.status_code}")
            return []
            
        except Exception as e:
            logger.error(f"❌ Splunk query error: {e}")
            return []
    
    def send_alert(self, alert: Dict) -> bool:
        """Send alert to Splunk via HTTP Event Collector"""
        try:
            hec_url = self.config.get('hec_url', f"https://{self.host}:8088")
            hec_token = self.config.get('hec_token')
            
            if not hec_token:
                logger.error("HEC token not configured")
                return False
            
            headers = {
                'Authorization': f'Splunk {hec_token}',
                'Content-Type': 'application/json'
            }
            
            event = {
                'event': alert,
                'sourcetype': 'kaliagent:threat_hunting',
                'source': 'kaliagent',
                'host': self.config.get('hostname', 'kaliagent'),
                'time': int(datetime.now().timestamp())
            }
            
            response = requests.post(hec_url, headers=headers, json=event, verify=False)
            
            if response.status_code == 200:
                logger.info(f"✅ Alert sent to Splunk: {alert.get('title', 'Unknown')}")
                return True
            else:
                logger.error(f"❌ Alert send failed: {response.status_code}")
                return False
                
        except Exception as e:
            logger.error(f"❌ Alert send error: {e}")
            return False


class ElasticConnector(SIEMConnector):
    """
    Elastic SIEM Connector
    
    Supports:
    - Elasticsearch
    - Elastic SIEM
    - OpenSearch
    """
    
    def __init__(self, config: Dict):
        super().__init__(config)
        self.host = config.get('host', 'localhost')
        self.port = config.get('port', 9200)
        self.username = config.get('username')
        self.password = config.get('password')
        self.api_key = config.get('api_key')
        self.index = config.get('index', 'logs-*')
        
        logger.info(f"🔌 Elastic Connector: {self.host}:{self.port}")
    
    def connect(self) -> bool:
        """Test connection to Elastic"""
        try:
            url = f"http://{self.host}:{self.port}"
            
            if self.api_key:
                headers = {'Authorization': f'ApiKey {self.api_key}'}
            elif self.username and self.password:
                from requests.auth import HTTPBasicAuth
                response = requests.get(url, auth=HTTPBasicAuth(self.username, self.password))
            else:
                response = requests.get(url)
            
            if response.status_code == 200:
                self.connected = True
                logger.info("✅ Connected to Elastic")
            else:
                logger.error(f"❌ Elastic auth failed: {response.status_code}")
                self.connected = False
            
            return self.connected
            
        except Exception as e:
            logger.error(f"❌ Elastic connection error: {e}")
            self.connected = False
            return False
    
    def query(self, query_string: str, time_range: Dict = None) -> List[Dict]:
        """Execute query against Elastic"""
        if not self.connected:
            logger.error("Not connected to Elastic")
            return []
        
        try:
            url = f"http://{self.host}:{self.port}/{self.index}/_search"
            
            # Build query
            if time_range:
                range_query = {
                    "range": {
                        "@timestamp": {
                            "gte": time_range.get('start', 'now-1h'),
                            "lte": time_range.get('end', 'now')
                        }
                    }
                }
            else:
                range_query = {"range": {"@timestamp": {"gte": "now-1h"}}}
            
            # Parse query string (simplified KQL to DSL)
            es_query = {
                "query": {
                    "bool": {
                        "must": [
                            range_query,
                            {"query_string": {"query": query_string}}
                        ]
                    }
                },
                "size": 1000
            }
            
            headers = {'Content-Type': 'application/json'}
            
            if self.api_key:
                headers['Authorization'] = f'ApiKey {self.api_key}'
            elif self.username and self.password:
                from requests.auth import HTTPBasicAuth
                response = requests.post(url, headers=headers, json=es_query, 
                                        auth=HTTPBasicAuth(self.username, self.password))
            else:
                response = requests.post(url, headers=headers, json=es_query)
            
            if response.status_code == 200:
                hits = response.json().get('hits', {}).get('hits', [])
                results = [hit['_source'] for hit in hits]
                logger.info(f"✅ Query returned {len(results)} results")
                return results
            
            logger.error(f"❌ Elastic query failed: {response.status_code}")
            return []
            
        except Exception as e:
            logger.error(f"❌ Elastic query error: {e}")
            return []
    
    def send_alert(self, alert: Dict) -> bool:
        """Send alert to Elastic"""
        try:
            url = f"http://{self.host}:{self.port}/kaliagent-alerts/_doc"
            
            headers = {'Content-Type': 'application/json'}
            
            if self.api_key:
                headers['Authorization'] = f'ApiKey {self.api_key}'
            
            document = {
                '@timestamp': datetime.now().isoformat(),
                **alert
            }
            
            if self.username and self.password:
                from requests.auth import HTTPBasicAuth
                response = requests.post(url, headers=headers, json=document,
                                        auth=HTTPBasicAuth(self.username, self.password))
            else:
                response = requests.post(url, headers=headers, json=document)
            
            if response.status_code in [200, 201]:
                logger.info(f"✅ Alert sent to Elastic: {alert.get('title', 'Unknown')}")
                return True
            else:
                logger.error(f"❌ Alert send failed: {response.status_code}")
                return False
                
        except Exception as e:
            logger.error(f"❌ Alert send error: {e}")
            return False


class SentinelConnector(SIEMConnector):
    """
    Microsoft Sentinel Connector
    
    Supports:
    - Azure Sentinel
    - Microsoft Defender for Cloud
    - Azure Log Analytics
    """
    
    def __init__(self, config: Dict):
        super().__init__(config)
        self.workspace_id = config.get('workspace_id')
        self.tenant_id = config.get('tenant_id')
        self.client_id = config.get('client_id')
        self.client_secret = config.get('client_secret')
        self.access_token = None
        self.token_expiry = None
        
        logger.info(f"🔌 Sentinel Connector: Workspace {self.workspace_id}")
    
    def connect(self) -> bool:
        """Authenticate to Azure"""
        try:
            # Get access token
            token_url = f"https://login.microsoftonline.com/{self.tenant_id}/oauth2/token"
            
            data = {
                'grant_type': 'client_credentials',
                'client_id': self.client_id,
                'client_secret': self.client_secret,
                'resource': 'https://management.azure.com/'
            }
            
            response = requests.post(token_url, data=data)
            
            if response.status_code == 200:
                token_data = response.json()
                self.access_token = token_data.get('access_token')
                self.token_expiry = datetime.now() + timedelta(seconds=token_data.get('expires_in', 3600))
                self.connected = True
                logger.info("✅ Connected to Azure Sentinel")
            else:
                logger.error(f"❌ Azure auth failed: {response.status_code}")
                self.connected = False
            
            return self.connected
            
        except Exception as e:
            logger.error(f"❌ Azure connection error: {e}")
            self.connected = False
            return False
    
    def _refresh_token(self) -> bool:
        """Refresh access token if expired"""
        if not self.access_token or datetime.now() >= self.token_expiry:
            return self.connect()
        return True
    
    def query(self, query_string: str, time_range: Dict = None) -> List[Dict]:
        """Execute KQL query against Sentinel"""
        if not self.connected:
            logger.error("Not connected to Sentinel")
            return []
        
        if not self._refresh_token():
            return []
        
        try:
            url = f"https://management.azure.com/subscriptions/{self.config.get('subscription_id')}/" \
                  f"resourceGroups/{self.config.get('resource_group')}/providers/Microsoft.OperationalInsights/" \
                  f"workspaces/{self.workspace_id}/query"
            
            params = {'api-version': '2021-02-01'}
            
            headers = {
                'Authorization': f'Bearer {self.access_token}',
                'Content-Type': 'application/json'
            }
            
            body = {'query': query_string}
            
            if time_range:
                body['timespan'] = f"{time_range.get('start', 'PT1H')}"
            
            response = requests.post(url, params=params, headers=headers, json=body)
            
            if response.status_code == 200:
                results = response.json().get('tables', [{}])[0].get('rows', [])
                columns = response.json().get('tables', [{}])[0].get('columns', [])
                
                # Convert to dict format
                formatted_results = []
                for row in results:
                    result_dict = {}
                    for i, col in enumerate(columns):
                        result_dict[col['name']] = row[i] if i < len(row) else None
                    formatted_results.append(result_dict)
                
                logger.info(f"✅ Query returned {len(formatted_results)} results")
                return formatted_results
            
            logger.error(f"❌ Sentinel query failed: {response.status_code}")
            return []
            
        except Exception as e:
            logger.error(f"❌ Sentinel query error: {e}")
            return []
    
    def send_alert(self, alert: Dict) -> bool:
        """Send alert to Sentinel as custom log"""
        try:
            if not self._refresh_token():
                return False
            
            # Use Azure Monitor HTTP Data Collector API
            workspace_url = f"https://{self.workspace_id}.ods.opinsights.azure.com/api/logs"
            
            body = json.dumps([alert])
            
            # Build signature
            import hashlib
            import hmac
            from email.utils import formatdate
            
            method = 'POST'
            content_type = 'application/json'
            date_string = formatdate(timeval=None, localtime=False, usegmt=True)
            resource = '/api/logs'
            
            string_to_hash = f"{method}\n{len(body)}\n{content_type}\n" \
                            f"x-ms-date:{date_string}\n{resource}"
            
            # Decode base64 shared key
            import base64
            shared_key = base64.b64decode(self.config.get('workspace_key'))
            
            # Build signature
            signature = hmac.new(shared_key, string_to_hash.encode('utf-8'), 
                               digestmod=hashlib.sha256).digest()
            signature_b64 = base64.b64encode(signature).decode('utf-8')
            
            headers = {
                'Authorization': f'SharedKey {self.workspace_id}:{signature_b64}',
                'Content-Type': 'application/json',
                'x-ms-date': date_string,
                'Log-Type': 'KaliAgentAlert'
            }
            
            response = requests.post(workspace_url, headers=headers, data=body)
            
            if response.status_code == 200:
                logger.info(f"✅ Alert sent to Sentinel: {alert.get('title', 'Unknown')}")
                return True
            else:
                logger.error(f"❌ Alert send failed: {response.status_code}")
                return False
                
        except Exception as e:
            logger.error(f"❌ Alert send error: {e}")
            return False


class SIEMFactory:
    """Factory for creating SIEM connectors"""
    
    @staticmethod
    def create_connector(siem_type: str, config: Dict) -> Optional[SIEMConnector]:
        """Create SIEM connector based on type"""
        connectors = {
            'splunk': SplunkConnector,
            'elastic': ElasticConnector,
            'sentinel': SentinelConnector
        }
        
        connector_class = connectors.get(siem_type.lower())
        
        if connector_class:
            return connector_class(config)
        else:
            logger.error(f"Unknown SIEM type: {siem_type}")
            return None


def main():
    """Main entry point"""
    print("""
╔═══════════════════════════════════════════════════════════════╗
║     🔌 SIEM INTEGRATION MODULE                               ║
║                    Phase 11: Alpha 0.1.0                      ║
╚═══════════════════════════════════════════════════════════════╝

Supported SIEMs:
  - Splunk (Enterprise & Cloud)
  - Elastic (Elasticsearch & SIEM)
  - Microsoft Sentinel

    """)
    
    # Example usage
    config = {
        'host': 'localhost',
        'port': 8089,
        'username': 'admin',
        'password': 'changeme'
    }
    
    connector = SIEMFactory.create_connector('splunk', config)
    
    if connector:
        if connector.connect():
            results = connector.query('index=main sourcetype=security')
            print(f"Query results: {len(results)}")
            
            alert = {
                'title': 'Test Alert',
                'severity': 'high',
                'description': 'Test alert from KaliAgent'
            }
            connector.send_alert(alert)


if __name__ == "__main__":
    main()
