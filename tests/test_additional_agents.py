"""
Additional Agents Tests
=======================

Unit tests for IntegrationAgent, ComplianceAgent, and CommunicationsAgent.
"""

import pytest
from datetime import datetime, timedelta

from agentic_ai.agents.integration import (
    IntegrationAgent,
    ConnectionStatus,
    SyncDirection,
    WebhookEvent,
)
from agentic_ai.agents.compliance import (
    ComplianceAgent,
    ComplianceStatus,
    RiskLevel,
    AuditStatus,
    ControlType,
)
from agentic_ai.agents.communications import (
    CommunicationsAgent,
    ChannelType,
    MessageStatus,
    Priority,
)


class TestIntegrationAgent:
    """Test IntegrationAgent."""
    
    @pytest.fixture
    def integration(self):
        """Create IntegrationAgent instance."""
        return IntegrationAgent()
    
    def test_create_connection(self, integration):
        """Test API connection creation."""
        conn = integration.create_connection(
            name="Slack Bot",
            service="slack",
            auth_type="bearer",
            access_token="xoxb-xxx",
        )
        
        assert conn.connection_id.startswith("conn-")
        assert conn.status == ConnectionStatus.ACTIVE
        assert conn.service == "slack"
    
    def test_test_connection(self, integration):
        """Test connection testing."""
        conn = integration.create_connection("Test", "github", "bearer")
        result = integration.test_connection(conn.connection_id)
        
        assert result['success'] is True
        assert 'latency_ms' in result
    
    def test_create_webhook(self, integration):
        """Test webhook creation."""
        webhook = integration.create_webhook(
            name="GitHub Issues",
            url="https://api.example.com/webhook",
            events=[WebhookEvent.CREATE, WebhookEvent.UPDATE],
        )
        
        assert webhook.webhook_id.startswith("webhook-")
        assert webhook.status == "active"
        assert len(webhook.events) == 2
    
    def test_trigger_webhook(self, integration):
        """Test webhook triggering."""
        webhook = integration.create_webhook(
            "Test Webhook",
            "https://example.com/hook",
            [WebhookEvent.CREATE],
        )
        
        result = integration.trigger_webhook(
            webhook.webhook_id,
            WebhookEvent.CREATE,
            {'data': 'test'},
        )
        
        assert result['success'] is True
        assert webhook.success_count == 1
    
    def test_create_sync_job(self, integration):
        """Test sync job creation."""
        job = integration.create_sync_job(
            name="HubSpot to Salesforce",
            source_connection="hubspot",
            target_connection="salesforce",
            direction=SyncDirection.UNIDIRECTIONAL,
            schedule="0 */6 * * *",
        )
        
        assert job.job_id.startswith("sync-")
        assert job.status == "pending"
        assert job.direction == SyncDirection.UNIDIRECTIONAL
    
    def test_run_sync_job(self, integration):
        """Test running sync job."""
        job = integration.create_sync_job(
            "Test Sync",
            "source",
            "target",
            SyncDirection.PUSH_ONLY,
            "daily",
        )
        
        result = integration.run_sync_job(job.job_id)
        
        assert result['success'] is True
        assert job.status == "completed"
    
    def test_get_integration_health(self, integration):
        """Test integration health check."""
        integration.create_connection("Test", "slack", "bearer")
        
        health = integration.get_integration_health()
        
        assert 'connections' in health
        assert 'webhooks' in health
        assert 'sync_jobs' in health
        assert 'health_score' in health
    
    def test_service_templates(self, integration):
        """Test service templates availability."""
        templates = integration.service_templates
        
        assert 'slack' in templates
        assert 'github' in templates
        assert 'salesforce' in templates
        assert 'stripe' in templates


class TestComplianceAgent:
    """Test ComplianceAgent."""
    
    @pytest.fixture
    def compliance(self):
        """Create ComplianceAgent instance."""
        return ComplianceAgent()
    
    def test_add_regulation(self, compliance):
        """Test adding regulation."""
        reg = compliance.add_regulation(
            name="SOC 2 Type II",
            framework="SOC2",
            jurisdiction="USA",
            owner="compliance@example.com",
        )
        
        assert reg.regulation_id.startswith("reg-")
        assert reg.status == ComplianceStatus.NOT_ASSESSED
        assert reg.framework == "SOC2"
    
    def test_update_regulation_status(self, compliance):
        """Test regulation status update."""
        reg = compliance.add_regulation("Test", "GDPR", "EU")
        
        compliance.update_regulation_status(reg.regulation_id, 95, 100)
        
        assert reg.status == ComplianceStatus.COMPLIANT
        assert reg.controls_passed == 95
    
    def test_create_control(self, compliance):
        """Test control creation."""
        reg = compliance.add_regulation("Test", "SOC2", "USA")
        
        control = compliance.create_control(
            name="Access Control",
            description="Control access to systems",
            control_type=ControlType.ADMINISTRATIVE,
            regulation_id=reg.regulation_id,
            risk_level=RiskLevel.HIGH,
        )
        
        assert control.control_id.startswith("ctrl-")
        assert control.control_type == ControlType.ADMINISTRATIVE
        assert control.risk_level == RiskLevel.HIGH
    
    def test_test_control(self, compliance):
        """Test control testing."""
        reg = compliance.add_regulation("Test", "SOC2", "USA")
        control = compliance.create_control(
            "Test Control",
            "Description",
            ControlType.TECHNICAL,
            reg.regulation_id,
        )
        
        result = compliance.test_control(
            control.control_id,
            passed=True,
            evidence_locations=["/docs/evidence.pdf"],
        )
        
        assert result is True
        assert control.status == ComplianceStatus.COMPLIANT
    
    def test_create_audit(self, compliance):
        """Test audit creation."""
        reg = compliance.add_regulation("Test", "SOC2", "USA")
        
        audit = compliance.create_audit(
            name="Annual SOC 2 Audit",
            audit_type="external",
            regulation_id=reg.regulation_id,
            start_date=datetime.utcnow(),
            auditor="External Auditor",
        )
        
        assert audit.audit_id.startswith("audit-")
        assert audit.status == AuditStatus.PLANNED
    
    def test_complete_audit(self, compliance):
        """Test audit completion."""
        reg = compliance.add_regulation("Test", "SOC2", "USA")
        audit = compliance.create_audit(
            "Test Audit",
            "internal",
            reg.regulation_id,
            datetime.utcnow(),
        )
        
        compliance.start_audit(audit.audit_id)
        result = compliance.complete_audit(
            audit.audit_id,
            score=92.5,
            findings=[{'type': 'minor', 'description': 'Test'}],
            recommendations=["Improve documentation"],
        )
        
        assert result is True
        assert audit.status == AuditStatus.COMPLETED
        assert audit.score == 92.5
    
    def test_create_policy(self, compliance):
        """Test policy creation."""
        policy = compliance.create_policy(
            title="Information Security Policy",
            category="security",
            version="1.0",
            owner="ciso@example.com",
            review_date=datetime.utcnow() + timedelta(days=365),
        )
        
        assert policy.policy_id.startswith("policy-")
        assert policy.status == "draft"
    
    def test_create_finding(self, compliance):
        """Test finding creation."""
        finding = compliance.create_finding(
            title="Missing MFA",
            description="Admin accounts without MFA",
            severity=RiskLevel.HIGH,
            assigned_to="security@example.com",
            due_date=datetime.utcnow() + timedelta(days=30),
        )
        
        assert finding.finding_id.startswith("finding-")
        assert finding.severity == RiskLevel.HIGH
        assert finding.status == "open"
    
    def test_get_compliance_report(self, compliance):
        """Test compliance report generation."""
        compliance.add_regulation("Test", "SOC2", "USA")
        
        report = compliance.get_compliance_report()
        
        assert 'summary' in report
        assert 'regulations' in report
        assert 'findings' in report
        assert 'audits' in report
        assert 'risk_score' in report
    
    def test_framework_templates(self, compliance):
        """Test framework templates."""
        templates = compliance.framework_templates
        
        assert 'SOC2' in templates
        assert 'ISO27001' in templates
        assert 'GDPR' in templates
        assert 'HIPAA' in templates
        assert 'PCI-DSS' in templates


class TestCommunicationsAgent:
    """Test CommunicationsAgent."""
    
    @pytest.fixture
    def comms(self):
        """Create CommunicationsAgent instance."""
        return CommunicationsAgent()
    
    def test_add_contact(self, comms):
        """Test adding contact."""
        contact = comms.add_contact(
            name="John Doe",
            email="john@example.com",
            phone="+1234567890",
            tags=['customer', 'vip'],
        )
        
        assert contact.contact_id.startswith("contact-")
        assert contact.email == "john@example.com"
        assert 'vip' in contact.tags
    
    def test_create_template(self, comms):
        """Test template creation."""
        template = comms.create_template(
            name="Welcome Email",
            channel=ChannelType.EMAIL,
            subject="Welcome to {company}!",
            content="Hi {name}, welcome!",
            variables=['company', 'name'],
            category="onboarding",
        )
        
        assert template.template_id.startswith("template-")
        assert template.channel == ChannelType.EMAIL
        assert 'company' in template.variables
    
    def test_render_template(self, comms):
        """Test template rendering."""
        template = comms.create_template(
            "Test",
            ChannelType.EMAIL,
            "Hello {name}",
            "Content {value}",
            ['name', 'value'],
        )
        
        rendered = comms.render_template(template.template_id, {'name': 'John', 'value': '123'})
        
        assert rendered['subject'] == "Hello John"
        assert rendered['content'] == "Content 123"
    
    def test_send_message(self, comms):
        """Test sending message."""
        message = comms.send_message(
            channel=ChannelType.EMAIL,
            subject="Test Subject",
            content="Test content",
            recipients=["user1@example.com", "user2@example.com"],
            priority=Priority.HIGH,
        )
        
        assert message.message_id.startswith("msg-")
        assert message.status == MessageStatus.SENT
        assert len(message.recipients) == 2
    
    def test_schedule_message(self, comms):
        """Test scheduling message."""
        scheduled_time = datetime.utcnow() + timedelta(hours=2)
        
        message = comms.schedule_message(
            channel=ChannelType.SMS,
            subject="Reminder",
            content="Don't forget!",
            recipients=["+1234567890"],
            scheduled_at=scheduled_time,
        )
        
        assert message.status == MessageStatus.SCHEDULED
        assert message.scheduled_at == scheduled_time
    
    def test_create_campaign(self, comms):
        """Test campaign creation."""
        campaign = comms.create_campaign(
            name="Q2 Newsletter",
            channel=ChannelType.EMAIL,
            total_recipients=1000,
        )
        
        assert campaign.campaign_id.startswith("camp-")
        assert campaign.status == "draft"
        assert campaign.total_recipients == 1000
    
    def test_update_campaign_metrics(self, comms):
        """Test campaign metrics update."""
        campaign = comms.create_campaign("Test", ChannelType.EMAIL, 100)
        comms.start_campaign(campaign.campaign_id)
        
        comms.update_campaign_metrics(
            campaign.campaign_id,
            sent=100,
            delivered=95,
            opened=50,
            clicked=20,
            failed=5,
        )
        
        assert campaign.sent_count == 100
        assert campaign.delivered_count == 95
        assert campaign.opened_count == 50
    
    def test_get_delivery_stats(self, comms):
        """Test delivery statistics."""
        comms.send_message(ChannelType.EMAIL, "Test", "Content", ["a@b.com"])
        
        stats = comms.get_delivery_stats()
        
        assert 'total_messages' in stats
        assert 'delivery_rate' in stats
        assert 'open_rate' in stats
        assert 'click_rate' in stats
    
    def test_get_channel_health(self, comms):
        """Test channel health check."""
        health = comms.get_channel_health()
        
        assert 'email' in health
        assert 'sms' in health
        assert 'push' in health
        assert health['email']['enabled'] is True


class TestAgentCapabilities:
    """Test capabilities export for additional agents."""
    
    def test_integration_capabilities(self):
        """Test IntegrationAgent capabilities."""
        from agentic_ai.agents.integration import get_capabilities
        caps = get_capabilities()
        
        assert caps['agent_type'] == 'integration'
        assert len(caps['capabilities']) >= 14
        assert 'create_connection' in caps['capabilities']
        assert 'trigger_webhook' in caps['capabilities']
    
    def test_compliance_capabilities(self):
        """Test ComplianceAgent capabilities."""
        from agentic_ai.agents.compliance import get_capabilities
        caps = get_capabilities()
        
        assert caps['agent_type'] == 'compliance'
        assert len(caps['capabilities']) >= 19
        assert 'add_regulation' in caps['capabilities']
        assert 'create_audit' in caps['capabilities']
    
    def test_communications_capabilities(self):
        """Test CommunicationsAgent capabilities."""
        from agentic_ai.agents.communications import get_capabilities
        caps = get_capabilities()
        
        assert caps['agent_type'] == 'communications'
        assert len(caps['capabilities']) >= 18
        assert 'send_message' in caps['capabilities']
        assert 'create_campaign' in caps['capabilities']


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
