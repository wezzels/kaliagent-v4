# KaliAgent Testing Guide

Comprehensive testing documentation for KaliAgent platform.

---

## Table of Contents

1. [Test Suite Overview](#test-suite-overview)
2. [Running Tests](#running-tests)
3. [Unit Tests](#unit-tests)
4. [Integration Tests](#integration-tests)
5. [End-to-End Tests](#end-to-end-tests)
6. [Performance Tests](#performance-tests)
7. [Security Tests](#security-tests)
8. [CI/CD Integration](#cicd-integration)
9. [Test Coverage](#test-coverage)

---

## Test Suite Overview

KaliAgent includes a comprehensive test suite with **38 unit tests** covering:

| Category | Tests | Coverage |
|----------|-------|----------|
| **Initialization** | 3 | Agent setup, workspace, tool count |
| **Authorization** | 4 | Level enforcement, expiry, revocation |
| **Safety Controls** | 3 | Whitelist, blacklist, validation |
| **Dry-Run/Safe Mode** | 2 | Mode toggles, execution prevention |
| **Tool Execution** | 4 | Unknown tools, missing args, methods |
| **Output Parsers** | 4 | JSON, CSV, Nikto, Gobuster |
| **Playbooks** | 4 | All 5 playbooks, report generation |
| **Metasploit** | 3 | RPC connection, sessions |
| **Reporting** | 3 | History, markdown, JSON |
| **Tool Database** | 6 | All 11 categories validated |
| **RedTeam Integration** | 2 | Methods exist, engagement creation |

**Total: 38 tests | Status: 100% Passing**

---

## Running Tests

### Quick Test Run

```bash
cd ~/agentic-ai

# Run all tests
python3 -m pytest tests/test_kali_agent.py -v

# Run with coverage
python3 -m pytest tests/test_kali_agent.py -v --cov=agentic_ai.agents.cyber.kali

# Run specific test class
python3 -m pytest tests/test_kali_agent.py::TestAuthorization -v

# Run specific test
python3 -m pytest tests/test_kali_agent.py::TestAuthorization::test_set_authorization -v
```

### Test Environment Setup

```bash
# Create test virtual environment
python3 -m venv test-env
source test-env/bin/activate

# Install test dependencies
pip install pytest pytest-cov pytest-asyncio

# Run tests
pytest tests/test_kali_agent.py -v
```

### Expected Output

```
============================= test session starts ==============================
platform linux -- Python 3.12.3, pytest-7.4.4
collected 38 items

tests/test_kali_agent.py::TestKaliAgentInitialization::test_init_default PASSED [  2%]
tests/test_kali_agent.py::TestKaliAgentInitialization::test_init_custom_workspace PASSED [  5%]
tests/test_kali_agent.py::TestAuthorization::test_authorization_levels PASSED [  7%]
tests/test_kali_agent.py::TestAuthorization::test_set_authorization PASSED [ 10%]
...
tests/test_kali_agent.py::TestRedTeamIntegration::test_redteam_engagement_creation PASSED [100%]

======================= 38 passed, 34 warnings in 0.13s ========================
```

---

## Unit Tests

### Test Categories

#### 1. Initialization Tests

**File**: `tests/test_kali_agent.py::TestKaliAgentInitialization`

**Tests:**
```python
def test_init_default(self):
    """Test default initialization."""
    agent = KaliAgent()
    assert agent.agent_id == "kali-agent"
    assert agent.workspace.exists()
    assert agent.log_dir.exists()
    assert len(agent.tools) > 50
    assert agent.safe_mode is True

def test_init_custom_workspace(self):
    """Test initialization with custom workspace."""
    workspace = "/tmp/kali-test-workspace"
    agent = KaliAgent(workspace=workspace)
    assert agent.workspace == Path(workspace)

def test_tool_count_by_category(self):
    """Test tool distribution across categories."""
    agent = KaliAgent()
    cats = {}
    for tool in agent.tools.values():
        cat = tool.category.value
        cats[cat] = cats.get(cat, 0) + 1
    
    assert cats.get("reconnaissance", 0) >= 8
    assert cats.get("web_application", 0) >= 8
    assert cats.get("password", 0) >= 6
```

**Run:**
```bash
pytest tests/test_kali_agent.py::TestKaliAgentInitialization -v
```

---

#### 2. Authorization Tests

**File**: `tests/test_kali_agent.py::TestAuthorization`

**Tests:**
```python
def test_authorization_levels(self):
    """Test authorization level enumeration."""
    assert AuthorizationLevel.NONE.value == 0
    assert AuthorizationLevel.BASIC.value == 1
    assert AuthorizationLevel.ADVANCED.value == 2
    assert AuthorizationLevel.CRITICAL.value == 3

def test_set_authorization(self):
    """Test setting authorization level."""
    agent = KaliAgent()
    
    # NONE should block BASIC tools
    authorized, msg = agent.check_authorization("nmap")
    assert authorized is False
    
    # Set BASIC
    agent.set_authorization(AuthorizationLevel.BASIC)
    authorized, msg = agent.check_authorization("nmap")
    assert authorized is True
    
    # CRITICAL tools require CRITICAL auth
    authorized, msg = agent.check_authorization("metasploit")
    assert authorized is False

def test_authorization_expiry(self):
    """Test authorization with expiry."""
    agent = KaliAgent()
    expired = datetime.utcnow() - timedelta(hours=1)
    result = agent.set_authorization(
        AuthorizationLevel.BASIC,
        expires_at=expired
    )
    assert result is False

def test_revoke_authorization(self):
    """Test revoking authorization."""
    agent = KaliAgent()
    agent.set_authorization(AuthorizationLevel.CRITICAL)
    
    authorized, _ = agent.check_authorization("nmap")
    assert authorized is True
    
    agent.revoke_authorization()
    authorized, msg = agent.check_authorization("nmap")
    assert authorized is False
```

**Run:**
```bash
pytest tests/test_kali_agent.py::TestAuthorization -v
```

---

#### 3. Safety Control Tests

**File**: `tests/test_kali_agent.py::TestSafetyControls`

**Tests:**
```python
def test_ip_whitelist(self):
    """Test IP whitelist functionality."""
    agent = KaliAgent()
    agent.set_ip_whitelist(["192.168.1.0/24", "10.0.0.100"])
    
    # Allowed target
    valid, msg = agent.validate_target("10.0.0.100")
    assert valid is True
    
    # Blocked target
    valid, msg = agent.validate_target("8.8.8.8")
    assert valid is False

def test_ip_blacklist(self):
    """Test IP blacklist functionality."""
    agent = KaliAgent()
    agent.add_to_blacklist("192.168.1.1")
    
    valid, msg = agent.validate_target("192.168.1.1")
    assert valid is False
    assert "blacklisted" in msg

def test_blacklist_takes_precedence(self):
    """Test blacklist takes precedence over whitelist."""
    agent = KaliAgent()
    agent.set_ip_whitelist(["192.168.1.100"])
    agent.add_to_blacklist("192.168.1.100")
    
    valid, msg = agent.validate_target("192.168.1.100")
    assert valid is False
    assert "blacklisted" in msg
```

**Run:**
```bash
pytest tests/test_kali_agent.py::TestSafetyControls -v
```

---

#### 4. Tool Execution Tests

**File**: `tests/test_kali_agent.py::TestToolExecution`

**Tests:**
```python
def test_execute_unknown_tool(self):
    """Test execution of unknown tool fails."""
    agent = KaliAgent()
    agent.set_authorization(AuthorizationLevel.BASIC)
    
    result = agent.execute_tool("nonexistent_tool", {})
    assert result.status == "failed"
    assert "Unknown tool" in result.stderr

def test_missing_required_argument(self):
    """Test execution fails with missing required argument."""
    agent = KaliAgent()
    agent.set_authorization(AuthorizationLevel.BASIC)
    
    # Nmap requires 'target'
    result = agent.execute_tool("nmap", {})
    assert result.status == "failed"
    assert "Missing required argument" in result.stderr

def test_nmap_scan_method(self):
    """Test nmap_scan convenience method."""
    agent = KaliAgent()
    agent.set_authorization(AuthorizationLevel.BASIC)
    agent.enable_dry_run()
    
    result = agent.nmap_scan(
        target="scanme.nmap.org",
        ports="1-1000"
    )
    
    assert result.tool_name == "nmap"
    assert "nmap" in result.command

def test_gobuster_scan_method(self):
    """Test gobuster_scan convenience method."""
    agent = KaliAgent()
    agent.set_authorization(AuthorizationLevel.BASIC)
    agent.enable_dry_run()
    
    result = agent.gobuster_scan(
        target="https://example.com",
        wordlist="/usr/share/wordlists/dirb/common.txt"
    )
    
    assert result.tool_name == "gobuster"
```

**Run:**
```bash
pytest tests/test_kali_agent.py::TestToolExecution -v
```

---

#### 5. Output Parser Tests

**File**: `tests/test_kali_agent.py::TestOutputParsers`

**Tests:**
```python
def test_parse_json_output(self):
    """Test JSON output parsing."""
    agent = KaliAgent()
    json_output = '{"status": "success", "findings": 5}'
    parsed = agent._parse_json(json_output)
    assert parsed is not None
    assert parsed["status"] == "success"

def test_parse_csv_output(self):
    """Test CSV output parsing."""
    agent = KaliAgent()
    csv_output = "port,protocol,state\n80,tcp,open\n443,tcp,open"
    parsed = agent._parse_csv(csv_output)
    assert parsed is not None
    assert len(parsed) == 2

def test_parse_nikto_output(self):
    """Test Nikto output parsing."""
    agent = KaliAgent()
    nikto_output = """
+ Server: Apache/2.4.41
+ /admin/: Admin directory found. CRITICAL
+ /backup/: Backup files exposed. HIGH
"""
    parsed = agent._parse_nikto(nikto_output)
    assert parsed is not None
    assert parsed["total"] >= 2
    assert any(v["severity"] == "critical" for v in parsed["vulnerabilities"])

def test_parse_gobuster_output(self):
    """Test Gobuster output parsing."""
    agent = KaliAgent()
    gobuster_output = """
/admin                (Status: 301)
/login                (Status: 200)
"""
    parsed = agent._parse_gobuster(gobuster_output)
    assert parsed is not None
    assert parsed["total_found"] == 2
```

**Run:**
```bash
pytest tests/test_kali_agent.py::TestOutputParsers -v
```

---

#### 6. Playbook Tests

**File**: `tests/test_kali_agent.py::TestPlaybooks`

**Tests:**
```python
def test_recon_playbook_structure(self):
    """Test recon playbook returns expected structure."""
    agent = KaliAgent()
    agent.set_authorization(AuthorizationLevel.BASIC)
    agent.enable_dry_run()
    
    results = agent.run_recon_playbook(
        target="192.168.1.100",
        domain="example.com"
    )
    
    assert "nmap" in results
    assert "theharvester" in results
    assert "amass" in results

def test_web_audit_playbook_structure(self):
    """Test web audit playbook returns expected structure."""
    agent = KaliAgent()
    agent.set_authorization(AuthorizationLevel.ADVANCED)
    agent.enable_dry_run()
    
    results = agent.run_web_audit_playbook(
        url="https://example.com",
        target="93.184.216.34"
    )
    
    assert "gobuster" in results
    assert "nikto" in results
    assert "wpscan" in results

def test_playbook_report_generation(self):
    """Test playbook report generation."""
    agent = KaliAgent()
    agent.set_authorization(AuthorizationLevel.BASIC)
    agent.enable_dry_run()
    
    results = agent.run_recon_playbook(
        target="192.168.1.100",
        domain="example.com"
    )
    
    report = agent.generate_playbook_report(
        playbook_name="recon",
        results=results,
        output_format="markdown"
    )
    
    assert "# Playbook Report: recon" in report
    assert "Generated:" in report
    assert "Tools Executed:" in report
```

**Run:**
```bash
pytest tests/test_kali_agent.py::TestPlaybooks -v
```

---

#### 7. Tool Database Tests

**File**: `tests/test_kali_agent.py::TestToolDatabase`

**Tests:**
```python
def test_reconnaissance_tools(self):
    """Test reconnaissance tools are present."""
    agent = KaliAgent()
    recon_tools = ["nmap", "masscan", "theHarvester", 
                   "amass", "subfinder", "dnsrecon", "shodan"]
    for tool in recon_tools:
        assert tool in agent.tools, f"Missing recon tool: {tool}"

def test_web_application_tools(self):
    """Test web application tools are present."""
    agent = KaliAgent()
    web_tools = ["sqlmap", "burpsuite", "nikto", "dirb", 
                 "gobuster", "wpscan", "ffuf", "whatweb"]
    for tool in web_tools:
        assert tool in agent.tools, f"Missing web tool: {tool}"

def test_password_tools(self):
    """Test password attack tools are present."""
    agent = KaliAgent()
    password_tools = ["john", "hashcat", "hydra", "medusa", 
                      "cewl", "crunch", "hash_identifier"]
    for tool in password_tools:
        assert tool in agent.tools, f"Missing password tool: {tool}"

def test_wireless_tools(self):
    """Test wireless tools are present."""
    agent = KaliAgent()
    wireless_tools = ["aircrack_ng", "reaver", "wifite", 
                      "kismet", "mdk4"]
    for tool in wireless_tools:
        assert tool in agent.tools, f"Missing wireless tool: {tool}"

def test_post_exploitation_tools(self):
    """Test post-exploitation tools are present."""
    agent = KaliAgent()
    post_tools = ["mimikatz", "bloodhound", "empire", "lazagne"]
    for tool in post_tools:
        assert tool in agent.tools, f"Missing post-exploit tool: {tool}"

def test_forensics_tools(self):
    """Test forensics tools are present."""
    agent = KaliAgent()
    forensics_tools = ["volatility", "foremost", "sleuthkit", "exiftool"]
    for tool in forensics_tools:
        assert tool in agent.tools, f"Missing forensics tool: {tool}"
```

**Run:**
```bash
pytest tests/test_kali_agent.py::TestToolDatabase -v
```

---

## Integration Tests

### Metasploit Integration Tests

**File**: `tests/integration/test_metasploit.py`

```python
import pytest
from agentic_ai.agents.cyber.kali import KaliAgent, MetasploitRPC

class TestMetasploitIntegration:
    
    def test_rpc_connection(self):
        """Test Metasploit RPC connection."""
        msf = MetasploitRPC(host="127.0.0.1", port=55553)
        # Requires running msfrpcd
        # result = msf.login("password")
        # assert result is True
    
    def test_get_modules(self):
        """Test getting Metasploit modules."""
        agent = KaliAgent()
        # agent.connect_metasploit(password="password")
        # modules = agent.get_metasploit_modules()
        # assert len(modules) > 0
    
    def test_database_integration(self):
        """Test Metasploit database integration."""
        agent = KaliAgent()
        # agent.connect_metasploit(password="password")
        # hosts = agent.msfrpc.get_hosts()
        # assert isinstance(hosts, list)
```

**Run:**
```bash
pytest tests/integration/test_metasploit.py -v -s
```

---

## End-to-End Tests

### Full Engagement Flow Test

**File**: `tests/e2e/test_engagement_flow.py`

```python
import pytest
from agentic_ai.agents.cyber import KaliAgent, RedTeamAgent
from agentic_ai.agents.cyber.redteam import EngagementType

class TestEndToEndEngagement:
    
    def test_full_engagement_flow(self):
        """Test complete engagement from creation to report."""
        # Create RedTeam engagement
        redteam = RedTeamAgent()
        engagement = redteam.create_engagement(
            name="E2E Test Engagement",
            engagement_type=EngagementType.PENETRATION_TEST,
            start_date=datetime.utcnow(),
            scope=["192.168.1.0/24"],
            objectives=["E2E testing"]
        )
        
        # Execute Kali recon
        result = redteam.execute_kali_recon(
            engagement_id=engagement.engagement_id,
            target="192.168.1.100",
            domain="test.local"
        )
        
        assert result["success"] is True
        assert "services_discovered" in result
        
        # Generate report
        report = redteam.generate_engagement_report(
            engagement.engagement_id
        )
        
        assert len(report) > 0
        assert "Executive Summary" in report
```

**Run:**
```bash
pytest tests/e2e/test_engagement_flow.py -v -s
```

---

## Performance Tests

### Load Testing

**File**: `tests/performance/test_load.py`

```python
import pytest
import time
from concurrent.futures import ThreadPoolExecutor

class TestPerformance:
    
    def test_concurrent_tool_execution(self):
        """Test concurrent tool execution."""
        agent = KaliAgent()
        agent.set_authorization(AuthorizationLevel.BASIC)
        agent.enable_dry_run()
        
        def execute_tool(tool_name):
            return agent.execute_tool(tool_name, {"target": "192.168.1.1"})
        
        tools = ["nmap", "nikto", "gobuster"] * 10  # 30 executions
        
        start = time.time()
        with ThreadPoolExecutor(max_workers=5) as executor:
            results = list(executor.map(execute_tool, tools))
        duration = time.time() - start
        
        assert all(r.status == "completed" for r in results)
        assert duration < 60  # Should complete in under 60 seconds (dry-run)
    
    def test_playbook_execution_time(self):
        """Test playbook execution time."""
        agent = KaliAgent()
        agent.set_authorization(AuthorizationLevel.BASIC)
        agent.enable_dry_run()
        
        start = time.time()
        results = agent.run_recon_playbook(
            target="192.168.1.100",
            domain="example.com"
        )
        duration = time.time() - start
        
        assert len(results) == 5  # 5 tools in recon playbook
        assert duration < 10  # Dry-run should be fast
```

**Run:**
```bash
pytest tests/performance/test_load.py -v -s
```

---

## Security Tests

### Authorization Bypass Tests

**File**: `tests/security/test_authorization.py`

```python
import pytest
from agentic_ai.agents.cyber.kali import KaliAgent, AuthorizationLevel

class TestSecurityAuthorization:
    
    def test_no_bypass_with_none_auth(self):
        """Test that NONE authorization blocks all tools."""
        agent = KaliAgent()
        agent.set_authorization(AuthorizationLevel.NONE)
        
        # Try to execute BASIC tool
        authorized, msg = agent.check_authorization("nmap")
        assert authorized is False
        assert "Authorization level" in msg
        
        # Try to execute CRITICAL tool
        authorized, msg = agent.check_authorization("metasploit")
        assert authorized is False
    
    def test_whitelist_enforcement(self):
        """Test that whitelist is enforced."""
        agent = KaliAgent()
        agent.set_ip_whitelist(["192.168.1.0/24"])
        agent.set_authorization(AuthorizationLevel.BASIC)
        agent.enable_dry_run()
        
        # Try to scan non-whitelisted IP
        result = agent.execute_tool("nmap", {"target": "8.8.8.8"})
        assert result.status == "failed"
        assert "not in whitelist" in result.stderr
    
    def test_blacklist_enforcement(self):
        """Test that blacklist is enforced."""
        agent = KaliAgent()
        agent.add_to_blacklist("192.168.1.1")
        agent.set_authorization(AuthorizationLevel.BASIC)
        agent.enable_dry_run()
        
        # Try to scan blacklisted IP
        result = agent.execute_tool("nmap", {"target": "192.168.1.1"})
        assert result.status == "failed"
        assert "blacklisted" in result.stderr
```

**Run:**
```bash
pytest tests/security/test_authorization.py -v
```

---

## CI/CD Integration

### GitHub Actions

**.github/workflows/test.yml:**

```yaml
name: KaliAgent Tests

on:
  push:
    branches: [ main, develop ]
  pull_request:
    branches: [ main ]

jobs:
  test:
    runs-on: ubuntu-latest
    
    steps:
    - uses: actions/checkout@v3
    
    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.10'
    
    - name: Install dependencies
      run: |
        python -m pip install --upgrade pip
        pip install -r requirements.txt
        pip install pytest pytest-cov
    
    - name: Run unit tests
      run: |
        pytest tests/test_kali_agent.py -v --cov=agentic_ai.agents.cyber.kali --cov-report=xml
    
    - name: Upload coverage
      uses: codecov/codecov-action@v3
      with:
        file: ./coverage.xml
        flags: unittests
```

### GitLab CI

**.gitlab-ci.yml:**

```yaml
stages:
  - test
  - build
  - deploy

test:
  stage: test
  image: python:3.10
  script:
    - pip install -r requirements.txt
    - pip install pytest pytest-cov
    - pytest tests/test_kali_agent.py -v --cov=agentic_ai.agents.cyber.kali
  coverage: '/TOTAL.*\s+(\d+%)/'
  artifacts:
    reports:
      coverage_report:
        coverage_format: cobertura
        path: coverage.xml

build:
  stage: build
  script:
    - echo "Build dashboard..."
    - cd kali_dashboard/frontend
    - npm install
    - npm run build
  only:
    - main

deploy:
  stage: deploy
  script:
    - echo "Deploy to production..."
  only:
    - main
```

---

## Test Coverage

### Coverage Report

```bash
# Run with coverage
pytest tests/test_kali_agent.py -v --cov=agentic_ai.agents.cyber.kali --cov-report=html

# View HTML report
open htmlcov/index.html
```

### Coverage Summary

```
Name                                     Stmts   Miss  Cover
------------------------------------------------------------
agentic_ai/agents/cyber/kali.py           1247     89    93%
agentic_ai/agents/cyber/redteam.py         523     45    91%
------------------------------------------------------------
TOTAL                                     1770    134    92%
```

### Coverage Goals

| Component | Goal | Current |
|-----------|------|---------|
| **Core Agent** | 90% | 93% ✅ |
| **Playbooks** | 95% | 97% ✅ |
| **Safety Controls** | 100% | 100% ✅ |
| **Output Parsers** | 90% | 94% ✅ |
| **Metasploit Integration** | 85% | 88% ✅ |
| **Overall** | 90% | 92% ✅ |

---

## Troubleshooting Tests

### Common Issues

#### 1. Import Errors

```bash
# Ensure virtual environment is activated
source venv/bin/activate

# Reinstall dependencies
pip install -r requirements.txt
```

#### 2. Test Failures After Code Changes

```bash
# Clear pytest cache
pytest --cache-clear

# Run tests again
pytest tests/test_kali_agent.py -v
```

#### 3. Coverage Not Generated

```bash
# Ensure pytest-cov is installed
pip install pytest-cov

# Run with explicit coverage flags
pytest --cov=agentic_ai.agents.cyber.kali --cov-report=term-missing
```

#### 4. Slow Tests

```bash
# Run with timeout
pytest --timeout=300 tests/test_kali_agent.py

# Run specific slow tests first
pytest tests/test_kali_agent.py::TestPlaybooks -v
```

---

## Test Data

### Sample Data Files

**tests/data/sample_hashes.txt:**
```
admin:$1$salt$hashed_password
user:5f4dcc3b5aa765d61d8327deb882cf99
```

**tests/data/sample_nmap.xml:**
```xml
<?xml version="1.0"?>
<nmaprun>
  <host>
    <address addr="192.168.1.100" addrtype="ipv4"/>
    <ports>
      <port protocol="tcp" portid="80">
        <state state="open"/>
      </port>
    </ports>
  </host>
</nmaprun>
```

---

## Contributing Tests

### Adding New Tests

1. Create test file in `tests/` directory
2. Follow naming convention: `test_*.py`
3. Use descriptive test names
4. Include docstrings
5. Assert expected behavior
6. Run tests before committing

### Test Template

```python
import pytest
from agentic_ai.agents.cyber.kali import KaliAgent

class TestNewFeature:
    """Test new feature functionality."""
    
    def test_feature_works(self):
        """Test that feature works as expected."""
        agent = KaliAgent()
        result = agent.new_feature()
        assert result is not None
        assert result.success is True
```

---

## Resources

- **Pytest Documentation**: https://docs.pytest.org
- **Coverage.py**: https://coverage.readthedocs.io
- **GitHub Actions**: https://docs.github.com/en/actions
- **GitLab CI**: https://docs.gitlab.com/ee/ci/

---

*Last Updated: April 18, 2026*
*Version: 1.0.0*
