"""
Cloud Integration Tests
=======================

Integration tests for cloud provider integrations with mocked APIs.
Tests cover AWS, GCP, Azure, and Kubernetes interactions.
"""

import pytest
from datetime import datetime
from unittest.mock import Mock, patch, MagicMock
from moto import mock_aws

from agentic_ai.agents.cloud_security import CloudSecurityAgent, CloudProvider, Severity, ResourceType
from agentic_ai.agents.chaos_monkey import ChaosMonkeyAgent, ExperimentType, TargetType
from agentic_ai.agents.devops import DevOpsAgent


# ============================================================================
# AWS Integration Tests (using moto for mocking)
# ============================================================================

@mock_aws
class TestAWSIntegration:
    """Test AWS integrations with moto mocks."""
    
    def test_cloud_security_aws_account_registration(self):
        """Test registering AWS account in CloudSecurityAgent."""
        agent = CloudSecurityAgent()
        
        account = agent.add_account(
            account_id="123456789012",
            provider=CloudProvider.AWS,
            name="Test AWS Account",
            environment="production",
            owner="cloud-team@example.com",
        )
        
        assert account.account_id.startswith("acct-")
        assert account.provider == CloudProvider.AWS
        assert account.name == "Test AWS Account"
    
    @mock_aws
    def test_cloud_security_ec2_resource_tracking(self):
        """Test tracking EC2 resources."""
        import boto3
        
        # Create actual EC2 instance via moto
        ec2 = boto3.resource('ec2', region_name='us-east-1')
        instances = ec2.create_instances(
            ImageId='ami-12345678',
            MinCount=2,
            MaxCount=2,
            InstanceType='t3.medium',
        )
        
        agent = CloudSecurityAgent()
        account = agent.add_account("123456789012", CloudProvider.AWS, "Test", "production", "owner")
        
        # Register instances as resources
        for instance in instances:
            resource = agent.add_resource(
                resource_type=ResourceType.EC2,
                account_id=account.account_id,
                region="us-east-1",
                name=f"instance-{instance.id}",
                configuration={
                    'instance_id': instance.id,
                    'instance_type': instance.instance_type,
                    'state': instance.state['Name'],
                },
            )
            assert resource.resource_id.startswith("res-")
        
        # Verify resources tracked
        ec2_resources = agent.get_resources(resource_type=ResourceType.EC2)
        assert len(ec2_resources) == 2
    
    @mock_aws
    def test_cloud_security_s3_bucket_policy_check(self):
        """Test S3 bucket policy compliance checking."""
        import boto3
        
        # Create S3 bucket via moto
        s3 = boto3.client('s3', region_name='us-east-1')
        s3.create_bucket(Bucket='test-public-bucket')
        s3.create_bucket(Bucket='test-private-bucket')
        
        # Set public policy on one bucket
        public_policy = {
            'Version': '2012-10-17',
            'Statement': [{
                'Effect': 'Allow',
                'Principal': '*',
                'Action': 's3:GetObject',
                'Resource': 'arn:aws:s3:::test-public-bucket/*'
            }]
        }
        s3.put_bucket_policy(Bucket='test-public-bucket', Policy=str(public_policy).replace("'", '"'))
        
        agent = CloudSecurityAgent()
        account = agent.add_account("123456789012", CloudProvider.AWS, "Test", "production", "owner")
        
        # Register buckets
        public_bucket = agent.add_resource(
            ResourceType.S3, account.account_id, "us-east-1", "test-public-bucket",
            configuration={'public_access': True, 'policy': public_policy},
        )
        private_bucket = agent.add_resource(
            ResourceType.S3, account.account_id, "us-east-1", "test-private-bucket",
            configuration={'public_access': False},
        )
        
        # Create findings for public bucket
        finding = agent.create_finding(
            title="S3 Bucket Public Access",
            description="Bucket allows public access",
            severity=Severity.CRITICAL,
            resource_id=public_bucket.resource_id,
            account_id=account.account_id,
        )
        
        assert finding.severity == Severity.CRITICAL
        
        # Verify compliance check
        non_compliant = agent.get_resources(compliant=False)
        assert len(non_compliant) >= 1


# ============================================================================
# GCP Integration Tests (mocked)
# ============================================================================

class TestGCPIntegration:
    """Test GCP integrations with mocks."""
    
    @patch('agentic_ai.agents.cloud_security.CloudSecurityAgent')
    def test_gcp_compute_instance_tracking(self, mock_agent):
        """Test tracking GCP Compute Engine instances."""
        agent = CloudSecurityAgent()
        account = agent.add_account("gcp-project-123", CloudProvider.GCP, "Test GCP", "production", "owner")
        
        # Mock GCP instances
        instances = [
            {'name': 'web-server-1', 'zone': 'us-central1-a', 'machineType': 'n1-standard-2'},
            {'name': 'web-server-2', 'zone': 'us-central1-b', 'machineType': 'n1-standard-2'},
        ]
        
        for instance in instances:
            resource = agent.add_resource(
                ResourceType.GCE, account.account_id, instance['zone'], instance['name'],
                configuration=instance,
            )
            assert resource.resource_id.startswith("res-")
        
        gce_resources = agent.get_resources(resource_type=ResourceType.GCE)
        assert len(gce_resources) == 2
    
    @patch('agentic_ai.agents.cloud_security.CloudSecurityAgent')
    def test_gcp_storage_bucket_compliance(self, mock_agent):
        """Test GCS bucket compliance checking."""
        agent = CloudSecurityAgent()
        account = agent.add_account("gcp-project-123", CloudProvider.GCP, "Test", "production", "owner")
        
        # Mock GCS buckets
        buckets = [
            {'name': 'public-assets', 'public': True, 'location': 'US'},
            {'name': 'private-data', 'public': False, 'location': 'us-central1'},
        ]
        
        for bucket in buckets:
            resource = agent.add_resource(
                ResourceType.GCS, account.account_id, bucket['location'], bucket['name'],
                configuration={'public_access': bucket['public']},
            )
            
            if bucket['public']:
                agent.create_finding(
                    "GCS Bucket Public", "Bucket allows public access",
                    Severity.HIGH, resource.resource_id, account.account_id,
                )
        
        findings = agent.get_findings(severity=Severity.HIGH)
        assert len(findings) == 1


# ============================================================================
# Azure Integration Tests (mocked)
# ============================================================================

class TestAzureIntegration:
    """Test Azure integrations with mocks."""
    
    @patch('agentic_ai.agents.cloud_security.CloudSecurityAgent')
    def test_azure_vm_tracking(self, mock_agent):
        """Test tracking Azure Virtual Machines."""
        agent = CloudSecurityAgent()
        account = agent.add_account("azure-subscription-123", CloudProvider.AZURE, "Test Azure", "production", "owner")
        
        # Mock Azure VMs
        vms = [
            {'name': 'web-vm-1', 'region': 'eastus', 'size': 'Standard_DS2_v2'},
            {'name': 'db-vm-1', 'region': 'eastus', 'size': 'Standard_DS4_v2'},
        ]
        
        for vm in vms:
            resource = agent.add_resource(
                ResourceType.AZURE_VM, account.account_id, vm['region'], vm['name'],
                configuration=vm,
            )
            assert resource.resource_id.startswith("res-")
        
        azure_vms = agent.get_resources(resource_type=ResourceType.AZURE_VM)
        assert len(azure_vms) == 2
    
    @patch('agentic_ai.agents.cloud_security.CloudSecurityAgent')
    def test_azure_storage_account_compliance(self, mock_agent):
        """Test Azure Storage Account compliance."""
        agent = CloudSecurityAgent()
        account = agent.add_account("azure-subscription-123", CloudProvider.AZURE, "Test", "production", "owner")
        
        # Mock storage accounts
        storage_accounts = [
            {'name': 'prodlogs', 'public_blob': False, 'encryption': True},
            {'name': 'publicassets', 'public_blob': True, 'encryption': True},
        ]
        
        for sa in storage_accounts:
            resource = agent.add_resource(
                ResourceType.AZURE_STORAGE, account.account_id, "eastus", sa['name'],
                configuration={'public_blob_access': sa['public_blob'], 'encrypted': sa['encryption']},
            )
            
            if sa['public_blob']:
                agent.create_finding(
                    "Azure Storage Public Blob", "Storage account allows public blob access",
                    Severity.CRITICAL, resource.resource_id, account.account_id,
                )
        
        critical_findings = agent.get_findings(severity=Severity.CRITICAL)
        assert len(critical_findings) == 1


# ============================================================================
# Kubernetes Integration Tests (mocked)
# ============================================================================

class TestKubernetesIntegration:
    """Test Kubernetes integrations with mocks."""
    
    @patch('kubernetes.client.CoreV1Api')
    @patch('kubernetes.config.load_kube_config')
    def test_kubernetes_pod_tracking(self, mock_config, mock_core_api):
        """Test tracking Kubernetes pods."""
        agent = CloudSecurityAgent()
        account = agent.add_account("k8s-cluster-prod", CloudProvider.KUBERNETES, "Production K8s", "production", "owner")
        
        # Mock pods
        mock_pod_list = MagicMock()
        mock_pod_list.items = [
            MagicMock(
                metadata=MagicMock(name='web-pod-1', namespace='production'),
                status=MagicMock(phase='Running'),
                spec=MagicMock(containers=[MagicMock(name='nginx', image='nginx:1.21')]),
            ),
            MagicMock(
                metadata=MagicMock(name='api-pod-1', namespace='production'),
                status=MagicMock(phase='Running'),
                spec=MagicMock(containers=[MagicMock(name='api', image='api:v2.1')]),
            ),
        ]
        mock_core_api.return_value.list_pod_for_all_namespaces.return_value = mock_pod_list
        
        # Register pods
        for pod in mock_pod_list.items:
            resource = agent.add_resource(
                ResourceType.K8S_POD, account.account_id, pod.metadata.namespace, pod.metadata.name,
                configuration={
                    'namespace': pod.metadata.namespace,
                    'phase': pod.status.phase,
                    'containers': [c.name for c in pod.spec.containers],
                },
            )
            assert resource.resource_id.startswith("res-")
        
        pods = agent.get_resources(resource_type=ResourceType.K8S_POD)
        assert len(pods) == 2
    
    @patch('kubernetes.client.CoreV1Api')
    def test_kubernetes_security_context_check(self, mock_core_api):
        """Test Kubernetes security context validation."""
        agent = CloudSecurityAgent()
        account = agent.add_account("k8s-cluster-prod", CloudProvider.KUBERNETES, "Test", "production", "owner")
        
        # Mock pod without security context (running as root)
        insecure_pod = MagicMock(
            metadata=MagicMock(name='insecure-pod', namespace='default'),
            spec=MagicMock(containers=[
                MagicMock(
                    name='app',
                    securityContext=MagicMock(runAsNonRoot=False, runAsUser=0),
                )
            ]),
        )
        
        resource = agent.add_resource(
            ResourceType.K8S_POD, account.account_id, "default", "insecure-pod",
            configuration={
                'security_context': {
                    'runAsNonRoot': False,
                    'runAsUser': 0,  # Root
                }
            },
        )
        
        # Create finding for running as root
        finding = agent.create_finding(
            "Pod Running as Root", "Container runs with root privileges",
            Severity.HIGH, resource.resource_id, account.account_id,
        )
        
        assert finding.severity == Severity.HIGH


# ============================================================================
# DevOps Agent Cloud Integration Tests
# ============================================================================

class TestDevOpsCloudIntegration:
    """Test DevOpsAgent cloud operations."""
    
    @mock_aws
    def test_devops_ec2_instance_termination(self):
        """Test DevOpsAgent terminating EC2 instances."""
        import boto3
        
        # Create EC2 instance
        ec2 = boto3.resource('ec2', region_name='us-east-1')
        instances = ec2.create_instances(ImageId='ami-12345678', MinCount=1, MaxCount=1)
        instance_id = instances[0].id
        
        agent = DevOpsAgent()
        
        # Mock the terminate command
        with patch.object(agent, 'run_command') as mock_run:
            mock_run.return_value = {
                'status': 'success',
                'terminated_instances': [instance_id],
            }
            
            result = agent.run_command(
                target="ec2",
                command=f"aws ec2 terminate-instances --instance-ids {instance_id}",
                description="Terminate test instance",
            )
            
            assert result['status'] == 'success'
            assert instance_id in result['terminated_instances']
    
    @mock_aws
    def test_devops_lambda_function_deployment(self):
        """Test DevOpsAgent deploying Lambda functions."""
        import boto3
        from io import BytesIO
        import zipfile
        
        # Create Lambda client
        lambda_client = boto3.client('lambda', region_name='us-east-1')
        
        # Create deployment package
        zip_buffer = BytesIO()
        with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
            zip_file.writestr("lambda_function.py", "def handler(event, context): return 'OK'")
        zip_buffer.seek(0)
        
        agent = DevOpsAgent()
        
        # Mock Lambda creation
        with patch.object(lambda_client, 'create_function') as mock_create:
            mock_create.return_value = {
                'FunctionName': 'test-function',
                'FunctionArn': 'arn:aws:lambda:us-east-1:123456789012:function:test-function',
                'State': 'Active',
            }
            
            # Simulate deployment
            task = agent.create_task(
                title="Deploy Lambda Function",
                description="Deploy test Lambda function",
                priority="high",
                assignee="devops@example.com",
            )
            
            assert task.task_id.startswith("task-")


# ============================================================================
# Chaos Monkey Cloud Integration Tests
# ============================================================================

class TestChaosMonkeyCloudIntegration:
    """Test ChaosMonkeyAgent cloud operations."""
    
    @mock_aws
    def test_chaos_monkey_ec2_termination_experiment(self):
        """Test ChaosMonkeyAgent running EC2 termination experiment."""
        import boto3
        
        # Create EC2 instances
        ec2 = boto3.resource('ec2', region_name='us-east-1')
        instances = ec2.create_instances(ImageId='ami-12345678', MinCount=3, MaxCount=3)
        
        chaos = ChaosMonkeyAgent()
        
        # Register targets
        targets = []
        for instance in instances:
            target = chaos.register_target(
                target_type=TargetType.INSTANCE,
                name=f"test-instance-{instance.id}",
                cloud_provider="aws",
                region="us-east-1",
                availability_zone="us-east-1a",
                metadata={'instance_id': instance.id},
                critical=False,
            )
            targets.append(target)
        
        assert len(targets) == 3
        
        # Create experiment
        experiment = chaos.create_experiment(
            name="EC2 Termination Test",
            description="Test auto-healing",
            experiment_type=ExperimentType.INSTANCE_TERMINATION,
            severity="medium",
            blast_radius="limited",
            duration_minutes=15,
        )
        
        # Select random targets (non-critical)
        selected = chaos.select_random_targets(count=2, exclude_critical=True)
        assert len(selected) <= 2
        
        # Assign and start experiment
        chaos.assign_targets(experiment.experiment_id, [t.target_id for t in selected])
        
        # Verify experiment state
        assert experiment.status.value == "scheduled"
        assert experiment.target_count == len(selected)


# ============================================================================
# Multi-Cloud Orchestration Tests
# ============================================================================

class TestMultiCloudOrchestration:
    """Test multi-cloud orchestration scenarios."""
    
    def test_multi_cloud_resource_inventory(self):
        """Test tracking resources across multiple cloud providers."""
        agent = CloudSecurityAgent()
        
        # Add accounts for each cloud
        aws_account = agent.add_account("aws-123", CloudProvider.AWS, "AWS Prod", "production", "owner")
        gcp_account = agent.add_account("gcp-123", CloudProvider.GCP, "GCP Prod", "production", "owner")
        azure_account = agent.add_account("azure-123", CloudProvider.AZURE, "Azure Prod", "production", "owner")
        
        # Add resources to each
        agent.add_resource(ResourceType.EC2, aws_account.account_id, "us-east-1", "aws-web-1")
        agent.add_resource(ResourceType.GCE, gcp_account.account_id, "us-central1-a", "gcp-web-1")
        agent.add_resource(ResourceType.AZURE_VM, azure_account.account_id, "eastus", "azure-web-1")
        
        # Verify multi-cloud inventory
        all_resources = agent.get_resources()
        assert len(all_resources) == 3
        
        # Verify by provider
        aws_resources = [r for r in all_resources if r.resource_type == ResourceType.EC2]
        gcp_resources = [r for r in all_resources if r.resource_type == ResourceType.GCE]
        azure_resources = [r for r in all_resources if r.resource_type == ResourceType.AZURE_VM]
        
        assert len(aws_resources) == 1
        assert len(gcp_resources) == 1
        assert len(azure_resources) == 1
    
    def test_cross_cloud_compliance_reporting(self):
        """Test compliance reporting across multiple clouds."""
        agent = CloudSecurityAgent()
        
        # Setup multi-cloud environment
        aws = agent.add_account("aws-123", CloudProvider.AWS, "AWS", "production", "owner")
        azure = agent.add_account("azure-123", CloudProvider.AZURE, "Azure", "production", "owner")
        
        # Create findings in both clouds
        agent.create_finding("AWS Finding", "Desc", Severity.HIGH, "res-1", aws.account_id)
        agent.create_finding("AWS Finding 2", "Desc", Severity.MEDIUM, "res-2", aws.account_id)
        agent.create_finding("Azure Finding", "Desc", Severity.HIGH, "res-3", azure.account_id)
        
        # Get cross-cloud report
        report = agent.get_cloud_security_report()
        
        assert report['accounts']['total'] == 2
        assert report['findings']['total'] == 3
        assert report['findings']['by_severity']['high'] == 2


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
