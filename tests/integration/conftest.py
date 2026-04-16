"""
Integration Test Fixtures
=========================

Pytest fixtures for integration tests.
"""

import pytest
from datetime import datetime
from unittest.mock import Mock, MagicMock, patch


@pytest.fixture
def mock_aws_credentials():
    """Mock AWS credentials for tests."""
    with patch.dict('os.environ', {
        'AWS_ACCESS_KEY_ID': 'testing',
        'AWS_SECRET_ACCESS_KEY': 'testing',
        'AWS_SECURITY_TOKEN': 'testing',
        'AWS_SESSION_TOKEN': 'testing',
        'AWS_DEFAULT_REGION': 'us-east-1',
    }):
        yield


@pytest.fixture
def mock_gcp_credentials():
    """Mock GCP credentials for tests."""
    mock_credentials = Mock()
    mock_credentials.token = 'mock_token'
    
    with patch('google.auth.default', return_value=(mock_credentials, 'project-id')):
        yield


@pytest.fixture
def mock_azure_credentials():
    """Mock Azure credentials for tests."""
    mock_credential = Mock()
    mock_credential.get_token.return_value = Mock(token='mock_token')
    
    with patch('azure.identity.DefaultAzureCredential', return_value=mock_credential):
        yield


@pytest.fixture
def mock_kubernetes_config():
    """Mock Kubernetes configuration."""
    with patch('kubernetes.config.load_kube_config'):
        with patch('kubernetes.config.load_incluster_config'):
            yield


@pytest.fixture
def mock_redis():
    """Mock Redis client for tests."""
    mock_redis = Mock()
    mock_redis.get.return_value = None
    mock_redis.set.return_value = True
    mock_redis.delete.return_value = 1
    
    with patch('redis.Redis', return_value=mock_redis):
        yield mock_redis


@pytest.fixture
def mock_sqlite_db(tmp_path):
    """Mock SQLite database for tests."""
    db_path = tmp_path / "test.db"
    
    yield str(db_path)


@pytest.fixture
def sample_timestamp():
    """Sample timestamp for tests."""
    return datetime.utcnow()


@pytest.fixture
def mock_http_client():
    """Mock HTTP client for API calls."""
    mock_response = Mock()
    mock_response.status_code = 200
    mock_response.json.return_value = {'status': 'success'}
    
    mock_client = Mock()
    mock_client.get.return_value = mock_response
    mock_client.post.return_value = mock_response
    
    with patch('requests.Session', return_value=mock_client):
        yield mock_client
