"""
CloudSecurityAgent Tests
========================

Unit tests for CloudSecurityAgent - CSPM and cloud compliance.
"""

import pytest
from datetime import datetime, timedelta

from agentic_ai.agents.cloud_security import (
    CloudSecurityAgent,
    CloudProvider,
    ResourceType,
    ComplianceFramework,
    Severity,
    FindingStatus,
)


class TestCloudSecurityAgent:
    """Test CloudSecurityAgent."""
    
    @pytest.fixture
    def cloud_sec(self):
        """Create CloudSecurityAgent instance."""
        return CloudSecurityAgent()
    
    def test_add_account(self, cloud_sec):
        """Test adding cloud account."""
        account = cloud_sec.add_account(
            account_id="123456789012",
            provider=CloudProvider.AWS,
            name="Production AWS",
            environment="production",
            owner="cloud-team@example.com",
        )
        
        assert account.account_id.startswith("acct-")
        assert account.provider == CloudProvider.AWS
        assert account.environment == "production"
    
    def test_get_accounts_by_provider(self, cloud_sec):
        """Test filtering accounts by provider."""
        cloud_sec.add_account("123", CloudProvider.AWS, "AWS Prod", "production", "owner")
        cloud_sec.add_account("456", CloudProvider.AZURE, "Azure Prod", "production", "owner")
        cloud_sec.add_account("789", CloudProvider.GCP, "GCP Prod", "production", "owner")
        
        aws_accounts = cloud_sec.get_accounts(provider=CloudProvider.AWS)
        
        assert len(aws_accounts) == 1
        assert aws_accounts[0].provider == CloudProvider.AWS
    
    def test_update_account_scan(self, cloud_sec):
        """Test updating account scan results."""
        account = cloud_sec.add_account(
            "123", CloudProvider.AWS, "Test", "production", "owner",
        )
        
        result = cloud_sec.update_account_scan(
            account.account_id,
            resource_count=150,
            findings_count=5,
        )
        
        assert result is True
        assert account.last_scanned is not None
        assert account.resource_count == 150
        assert account.findings_count == 5
    
    def test_add_resource(self, cloud_sec):
        """Test adding cloud resource."""
        account = cloud_sec.add_account("123", CloudProvider.AWS, "Test", "production", "owner")
        
        resource = cloud_sec.add_resource(
            resource_type=ResourceType.S3,
            account_id=account.account_id,
            region="us-east-1",
            name="test-bucket",
            configuration={'public_access_block': True, 'encrypted': True},
            tags={'environment': 'production'},
        )
        
        assert resource.resource_id.startswith("res-")
        assert resource.resource_type == ResourceType.S3
        assert resource.configuration['public_access_block'] is True
    
    def test_get_resources_by_type(self, cloud_sec):
        """Test filtering resources by type."""
        account = cloud_sec.add_account("123", CloudProvider.AWS, "Test", "production", "owner")
        
        cloud_sec.add_resource(ResourceType.S3, account.account_id, "us-east-1", "bucket-1")
        cloud_sec.add_resource(ResourceType.EC2, account.account_id, "us-east-1", "instance-1")
        cloud_sec.add_resource(ResourceType.RDS, account.account_id, "us-east-1", "db-1")
        
        s3_resources = cloud_sec.get_resources(resource_type=ResourceType.S3)
        
        assert len(s3_resources) == 1
    
    def test_create_finding(self, cloud_sec):
        """Test creating security finding."""
        account = cloud_sec.add_account("123", CloudProvider.AWS, "Test", "production", "owner")
        
        finding = cloud_sec.create_finding(
            title="S3 Bucket Public Access",
            description="Bucket allows public access",
            severity=Severity.CRITICAL,
            resource_id="res-123",
            account_id=account.account_id,
            compliance_framework=ComplianceFramework.CIS_AWS,
            remediation="Enable block public access",
        )
        
        assert finding.finding_id.startswith("find-")
        assert finding.severity == Severity.CRITICAL
        assert finding.status == FindingStatus.OPEN
        assert account.findings_count == 1
    
    def test_update_finding_status(self, cloud_sec):
        """Test updating finding status."""
        account = cloud_sec.add_account("123", CloudProvider.AWS, "Test", "production", "owner")
        
        finding = cloud_sec.create_finding(
            "Test Finding",
            "Description",
            Severity.HIGH,
            "res-123",
            account.account_id,
        )
        
        result = cloud_sec.update_finding_status(
            finding.finding_id,
            FindingStatus.IN_PROGRESS,
            assigned_to="security@example.com",
        )
        
        assert result is True
        assert finding.status == FindingStatus.IN_PROGRESS
        assert finding.assigned_to == "security@example.com"
    
    def test_resolve_finding(self, cloud_sec):
        """Test resolving finding."""
        account = cloud_sec.add_account("123", CloudProvider.AWS, "Test", "production", "owner")
        
        finding = cloud_sec.create_finding(
            "Test",
            "Desc",
            Severity.MEDIUM,
            "res-123",
            account.account_id,
        )
        
        cloud_sec.update_finding_status(finding.finding_id, FindingStatus.RESOLVED)
        
        assert finding.status == FindingStatus.RESOLVED
        assert finding.resolved_at is not None
    
    def test_get_findings_by_severity(self, cloud_sec):
        """Test filtering findings by severity."""
        account = cloud_sec.add_account("123", CloudProvider.AWS, "Test", "production", "owner")
        
        cloud_sec.create_finding("Critical", "Desc", Severity.CRITICAL, "res-1", account.account_id)
        cloud_sec.create_finding("High", "Desc", Severity.HIGH, "res-2", account.account_id)
        cloud_sec.create_finding("Medium", "Desc", Severity.MEDIUM, "res-3", account.account_id)
        
        critical = cloud_sec.get_findings(severity=Severity.CRITICAL)
        high = cloud_sec.get_findings(severity=Severity.HIGH)
        
        assert len(critical) == 1
        assert len(high) == 1
    
    def test_get_findings_by_status(self, cloud_sec):
        """Test filtering findings by status."""
        account = cloud_sec.add_account("123", CloudProvider.AWS, "Test", "production", "owner")
        
        f1 = cloud_sec.create_finding("Open", "Desc", Severity.MEDIUM, "res-1", account.account_id)
        f2 = cloud_sec.create_finding("Open 2", "Desc", Severity.MEDIUM, "res-2", account.account_id)
        f3 = cloud_sec.create_finding("Resolved", "Desc", Severity.MEDIUM, "res-3", account.account_id)
        
        cloud_sec.update_finding_status(f3.finding_id, FindingStatus.RESOLVED)
        
        open_findings = cloud_sec.get_findings(status=FindingStatus.OPEN)
        
        assert len(open_findings) == 2
    
    def test_create_policy(self, cloud_sec):
        """Test creating security policy."""
        policy = cloud_sec.create_policy(
            name="Unencrypted EBS",
            description="All EBS volumes must be encrypted",
            provider=CloudProvider.AWS,
            resource_type=ResourceType.EC2,
            rule_expression="encrypted == false",
            severity=Severity.MEDIUM,
            compliance_frameworks=[ComplianceFramework.CIS_AWS],
        )
        
        assert policy.policy_id.startswith("policy-")
        assert policy.provider == CloudProvider.AWS
        assert policy.severity == Severity.MEDIUM
    
    def test_get_policies_by_provider(self, cloud_sec):
        """Test filtering policies by provider."""
        cloud_sec.create_policy(
            "AWS Policy", "Desc", CloudProvider.AWS,
            ResourceType.S3, "rule", Severity.HIGH,
        )
        cloud_sec.create_policy(
            "Azure Policy", "Desc", CloudProvider.AZURE,
            ResourceType.STORAGE_ACCOUNT, "rule", Severity.HIGH,
        )
        
        aws_policies = cloud_sec.get_policies(provider=CloudProvider.AWS)
        
        assert len(aws_policies) == 1
    
    def test_create_remediation(self, cloud_sec):
        """Test creating remediation action."""
        account = cloud_sec.add_account("123", CloudProvider.AWS, "Test", "production", "owner")
        
        finding = cloud_sec.create_finding(
            "Test", "Desc", Severity.HIGH,
            "res-123", account.account_id,
        )
        
        remediation = cloud_sec.create_remediation(
            finding.finding_id,
            action_type="terraform",
            action_description="Apply terraform fix",
        )
        
        assert remediation.remediation_id.startswith("rem-")
        assert remediation.action_type == "terraform"
        assert remediation.status == "pending"
    
    def test_execute_remediation(self, cloud_sec):
        """Test executing remediation."""
        account = cloud_sec.add_account("123", CloudProvider.AWS, "Test", "production", "owner")
        
        finding = cloud_sec.create_finding(
            "Test", "Desc", Severity.HIGH,
            "res-123", account.account_id,
        )
        
        remediation = cloud_sec.create_remediation(
            finding.finding_id,
            "manual",
            "Manual fix",
        )
        
        result = cloud_sec.execute_remediation(
            remediation.remediation_id,
            executed_by="security@example.com",
            result="Successfully applied fix",
        )
        
        assert result is True
        assert remediation.status == "completed"
        assert remediation.executed_by == "security@example.com"
        assert finding.status == FindingStatus.RESOLVED
    
    def test_get_compliance_score(self, cloud_sec):
        """Test compliance score calculation."""
        account = cloud_sec.add_account("123", CloudProvider.AWS, "Test", "production", "owner")
        
        # Create policies for CIS_AWS
        cloud_sec.create_policy(
            "Policy 1", "Desc", CloudProvider.AWS,
            ResourceType.S3, "rule", Severity.HIGH,
            compliance_frameworks=[ComplianceFramework.CIS_AWS],
        )
        cloud_sec.create_policy(
            "Policy 2", "Desc", CloudProvider.AWS,
            ResourceType.EC2, "rule", Severity.HIGH,
            compliance_frameworks=[ComplianceFramework.CIS_AWS],
        )
        
        # Create findings
        cloud_sec.create_finding(
            "Finding 1", "Desc", Severity.HIGH,
            "res-1", account.account_id,
            compliance_framework=ComplianceFramework.CIS_AWS,
        )
        
        score = cloud_sec.get_compliance_score(ComplianceFramework.CIS_AWS)
        
        assert 'score' in score
        assert 'total_controls' in score
        assert 'open_findings' in score
    
    def test_get_cloud_security_report(self, cloud_sec):
        """Test cloud security report generation."""
        # Add accounts
        cloud_sec.add_account("123", CloudProvider.AWS, "AWS Prod", "production", "owner")
        cloud_sec.add_account("456", CloudProvider.AZURE, "Azure Prod", "production", "owner")
        
        # Add findings
        account = list(cloud_sec.accounts.values())[0]
        cloud_sec.create_finding("Critical", "Desc", Severity.CRITICAL, "res-1", account.account_id)
        cloud_sec.create_finding("High", "Desc", Severity.HIGH, "res-2", account.account_id)
        
        report = cloud_sec.get_cloud_security_report()
        
        assert 'accounts' in report
        assert 'resources' in report
        assert 'findings' in report
        assert 'policies' in report
        assert 'remediation' in report
        assert report['accounts']['total'] == 2
    
    def test_get_account_risk_profile(self, cloud_sec):
        """Test account risk profile."""
        account = cloud_sec.add_account(
            "123", CloudProvider.AWS, "Test Account",
            "production", "owner@example.com",
        )
        
        # Add findings
        cloud_sec.create_finding("Critical 1", "Desc", Severity.CRITICAL, "res-1", account.account_id)
        cloud_sec.create_finding("Critical 2", "Desc", Severity.CRITICAL, "res-2", account.account_id)
        cloud_sec.create_finding("High", "Desc", Severity.HIGH, "res-3", account.account_id)
        
        profile = cloud_sec.get_account_risk_profile(account.account_id)
        
        assert profile['account_id'] == account.account_id
        assert 'risk_score' in profile
        assert 'risk_level' in profile
        assert profile['findings']['critical'] == 2
    
    def test_builtin_policies(self, cloud_sec):
        """Test built-in policies initialization."""
        policies = cloud_sec.builtin_policies
        
        assert len(policies) >= 8
        assert any(p['name'] == 'S3 Bucket Public Access' for p in policies)
        assert any(p['name'] == 'IAM User Without MFA' for p in policies)
    
    def test_check_resource_compliance(self, cloud_sec):
        """Test resource compliance checking."""
        account = cloud_sec.add_account("123", CloudProvider.AWS, "Test", "production", "owner")
        
        # Add non-compliant resource
        resource = cloud_sec.add_resource(
            resource_type=ResourceType.EC2,
            account_id=account.account_id,
            region="us-east-1",
            name="unencrypted-instance",
            configuration={'encrypted': False},
        )
        
        # Create policy
        policy = cloud_sec.create_policy(
            "Unencrypted EBS",
            "All EBS must be encrypted",
            CloudProvider.AWS,
            ResourceType.EC2,
            "encrypted == false",
            Severity.MEDIUM,
        )
        
        findings = cloud_sec.check_resource_compliance(resource.resource_id, [policy])
        
        assert len(findings) >= 1
    
    def test_get_resources_by_compliance(self, cloud_sec):
        """Test filtering resources by compliance status."""
        account = cloud_sec.add_account("123", CloudProvider.AWS, "Test", "production", "owner")
        
        r1 = cloud_sec.add_resource(ResourceType.S3, account.account_id, "us-east-1", "compliant-bucket")
        r1.compliant = True
        
        r2 = cloud_sec.add_resource(ResourceType.S3, account.account_id, "us-east-1", "non-compliant-bucket")
        r2.compliant = False
        
        non_compliant = cloud_sec.get_resources(compliant=False)
        
        assert len(non_compliant) == 1


class TestCloudSecurityCapabilities:
    """Test CloudSecurityAgent capabilities export."""
    
    def test_capabilities(self):
        """Test capabilities export."""
        from agentic_ai.agents.cloud_security import get_capabilities
        caps = get_capabilities()
        
        assert caps['agent_type'] == 'cloud_security'
        assert len(caps['capabilities']) >= 16
        assert 'add_account' in caps['capabilities']
        assert 'create_finding' in caps['capabilities']
        assert 'get_compliance_score' in caps['capabilities']
    
    def test_cloud_providers(self):
        """Test cloud providers in capabilities."""
        from agentic_ai.agents.cloud_security import get_capabilities
        caps = get_capabilities()
        
        assert 'aws' in caps['cloud_providers']
        assert 'azure' in caps['cloud_providers']
        assert 'gcp' in caps['cloud_providers']
    
    def test_compliance_frameworks(self):
        """Test compliance frameworks in capabilities."""
        from agentic_ai.agents.cloud_security import get_capabilities
        caps = get_capabilities()
        
        assert 'cis_aws' in caps['compliance_frameworks']
        assert 'cis_azure' in caps['compliance_frameworks']
        assert 'pci_dss' in caps['compliance_frameworks']
        assert 'hipaa' in caps['compliance_frameworks']
        assert 'soc2' in caps['compliance_frameworks']


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
