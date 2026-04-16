# Agentic AI Integration Tests

End-to-end integration tests with cloud API mocks and multi-agent workflows.

## Test Categories

### 1. Cloud Integration Tests
- AWS (boto3 mocks)
- GCP (google-cloud mocks)
- Azure (azure-sdk mocks)
- Kubernetes (kubernetes-client mocks)

### 2. Multi-Agent Integration Tests
- Security incident response flow
- Vendor assessment flow
- Audit preparation flow
- Chaos experiment monitoring

### 3. Persistence Tests
- SQLite database tests
- Redis cache tests
- File-based state tests

## Running Tests

```bash
# Run all integration tests
pytest tests/integration/ -v

# Run specific category
pytest tests/integration/test_cloud_integration.py -v
pytest tests/integration/test_multi_agent.py -v

# Run with coverage
pytest tests/integration/ --cov=agentic_ai --cov-report=html
```

## Mock Configuration

Tests use pytest fixtures to provide mocked cloud APIs:

```python
@pytest.fixture
def mock_aws_client():
    with mock_aws():
        yield boto3.client('ec2', region_name='us-east-1')
```

## Requirements

```bash
pip install pytest pytest-moto pytest-asyncio
pip install boto3 google-cloud-storage azure-identity
```
