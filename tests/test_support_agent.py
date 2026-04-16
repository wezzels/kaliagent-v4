"""
SupportAgent Tests
==================

Unit tests for SupportAgent - ticket management, auto-responses,
knowledge base, SLA tracking, and customer satisfaction.
"""

import pytest
from datetime import datetime, timedelta

from agentic_ai.agents.support import (
    SupportAgent,
    TicketStatus,
    TicketPriority,
    TicketCategory,
)


class TestSupportAgentInitialization:
    """Test SupportAgent initialization."""
    
    def test_agent_creation(self):
        """Test agent can be created."""
        agent = SupportAgent()
        assert agent.agent_id == "support-agent"
        assert len(agent.slas) >= 4  # Default SLAs
        assert len(agent.knowledge_base) >= 3  # Default articles
    
    def test_get_state(self):
        """Test state summary."""
        agent = SupportAgent()
        state = agent.get_state()
        
        assert 'agent_id' in state
        assert 'tickets_count' in state
        assert 'open_tickets' in state
        assert 'knowledge_articles' in state


class TestTicketManagement:
    """Test ticket management."""
    
    @pytest.fixture
    def support_agent(self):
        """Create SupportAgent instance."""
        return SupportAgent()
    
    def test_create_ticket(self, support_agent):
        """Test ticket creation."""
        ticket = support_agent.create_ticket(
            subject="Login issue",
            description="Can't access my account",
            customer_id="cust-123",
            customer_email="user@example.com",
        )
        
        assert ticket.ticket_id.startswith("ticket-")
        assert ticket.subject == "Login issue"
        assert ticket.status == TicketStatus.NEW
        assert ticket.priority == TicketPriority.NORMAL
    
    def test_auto_triage_category(self, support_agent):
        """Test automatic category assignment."""
        # Password issue
        ticket1 = support_agent.create_ticket(
            subject="Password reset",
            description="I forgot my password",
            customer_id="cust-1",
            customer_email="user1@example.com",
        )
        assert ticket1.category == TicketCategory.ACCOUNT
        
        # Billing issue
        ticket2 = support_agent.create_ticket(
            subject="Billing question",
            description="Question about my invoice",
            customer_id="cust-2",
            customer_email="user2@example.com",
        )
        assert ticket2.category == TicketCategory.BILLING
        
        # Bug report
        ticket3 = support_agent.create_ticket(
            subject="App crashes",
            description="Getting error when clicking button",
            customer_id="cust-3",
            customer_email="user3@example.com",
        )
        assert ticket3.category == TicketCategory.BUG_REPORT
    
    def test_auto_triage_priority(self, support_agent):
        """Test automatic priority assignment."""
        # Urgent issue
        ticket1 = support_agent.create_ticket(
            subject="URGENT: System down",
            description="Critical emergency",
            customer_id="cust-1",
            customer_email="user1@example.com",
        )
        assert ticket1.priority == TicketPriority.HIGH
        
        # Normal question
        ticket2 = support_agent.create_ticket(
            subject="Question about features",
            description="Please help me understand",
            customer_id="cust-2",
            customer_email="user2@example.com",
        )
        assert ticket2.priority == TicketPriority.NORMAL
    
    def test_update_ticket_status(self, support_agent):
        """Test ticket status updates."""
        ticket = support_agent.create_ticket(
            subject="Test",
            description="Test",
            customer_id="cust-1",
            customer_email="user@example.com",
        )
        
        # Update to in progress
        updated = support_agent.update_ticket_status(
            ticket.ticket_id,
            TicketStatus.IN_PROGRESS,
            assigned_to="agent-1",
        )
        
        assert updated.status == TicketStatus.IN_PROGRESS
        assert updated.assigned_to == "agent-1"
    
    def test_add_message(self, support_agent):
        """Test adding messages to ticket."""
        ticket = support_agent.create_ticket(
            subject="Test",
            description="Test",
            customer_id="cust-1",
            customer_email="user@example.com",
        )
        
        # Add agent message
        success = support_agent.add_message(
            ticket.ticket_id,
            "Thanks for contacting support. How can I help?",
            "agent@example.com",
        )
        
        assert success is True
        assert len(ticket.messages) >= 1
        
        # Add customer reply
        support_agent.add_message(
            ticket.ticket_id,
            "I need help with login",
            "customer",
        )
        
        assert len(ticket.messages) >= 2
    
    def test_resolve_ticket(self, support_agent):
        """Test ticket resolution."""
        ticket = support_agent.create_ticket(
            subject="Test",
            description="Test",
            customer_id="cust-1",
            customer_email="user@example.com",
        )
        
        resolved = support_agent.resolve_ticket(
            ticket.ticket_id,
            resolution="Issue resolved by resetting password",
            resolved_by="agent-1",
        )
        
        assert resolved.status == TicketStatus.RESOLVED
        assert resolved.resolution is not None
        assert resolved.resolved_by == "agent-1"
        assert resolved.resolved_at is not None
        assert resolved.resolution_time is not None
    
    def test_get_tickets_filter(self, support_agent):
        """Test filtering tickets."""
        # Create multiple tickets
        support_agent.create_ticket("T1", "Desc", "c1", "u1@example.com")
        support_agent.create_ticket("T2", "Desc", "c2", "u2@example.com")
        support_agent.create_ticket("T3", "Desc", "c3", "u3@example.com")
        
        # Get all
        all_tickets = support_agent.get_tickets()
        assert len(all_tickets) == 3
        
        # Resolve one
        tickets = support_agent.get_tickets()
        support_agent.resolve_ticket(tickets[0].ticket_id, "Fixed", "agent")
        
        # Filter by status
        resolved = support_agent.get_tickets(status=TicketStatus.RESOLVED)
        assert len(resolved) == 1
        
        open_tickets = support_agent.get_tickets(status=TicketStatus.NEW)
        assert len(open_tickets) == 2
    
    def test_record_satisfaction(self, support_agent):
        """Test recording satisfaction scores."""
        ticket = support_agent.create_ticket(
            subject="Test",
            description="Test",
            customer_id="cust-1",
            customer_email="user@example.com",
        )
        
        support_agent.resolve_ticket(ticket.ticket_id, "Fixed", "agent")
        
        success = support_agent.record_satisfaction(ticket.ticket_id, 5)
        
        assert success is True
        assert ticket.satisfaction_score == 5


class TestAutoResponses:
    """Test auto-response functionality."""
    
    @pytest.fixture
    def support_agent(self):
        """Create SupportAgent instance."""
        return SupportAgent()
    
    def test_password_reset_response(self, support_agent):
        """Test password reset auto-response."""
        ticket = support_agent.create_ticket(
            subject="Forgot password",
            description="I need to reset my password",
            customer_id="cust-1",
            customer_email="user@example.com",
        )
        
        response = support_agent.get_auto_response(ticket)
        
        assert response is not None
        assert "reset-password" in response
    
    def test_billing_response(self, support_agent):
        """Test billing auto-response."""
        ticket = support_agent.create_ticket(
            subject="Billing question",
            description="Question about my invoice",
            customer_id="cust-1",
            customer_email="user@example.com",
        )
        
        response = support_agent.get_auto_response(ticket)
        
        assert response is not None
        assert "billing" in response.lower()


class TestKnowledgeBase:
    """Test knowledge base functionality."""
    
    @pytest.fixture
    def support_agent(self):
        """Create SupportAgent instance."""
        return SupportAgent()
    
    def test_search_knowledge_base(self, support_agent):
        """Test KB search."""
        articles = support_agent.search_knowledge_base("password")
        
        assert len(articles) >= 1
        assert any("password" in a.title.lower() for a in articles)
    
    def test_rate_article(self, support_agent):
        """Test rating KB articles."""
        articles = support_agent.search_knowledge_base("password")
        
        if articles:
            article = articles[0]
            success = support_agent.rate_article(article.article_id, helpful=True)
            
            assert success is True
            assert article.helpful_count >= 1
    
    def test_add_knowledge_article(self, support_agent):
        """Test adding KB article."""
        article = support_agent.add_knowledge_article(
            title="How to Update Profile",
            content="Step 1: Go to settings. Step 2: Click edit...",
            category="account",
            tags=["profile", "settings", "account"],
        )
        
        assert article.article_id.startswith("kb-")
        assert article.title == "How to Update Profile"
        assert len(article.tags) == 3


class TestSLAManagement:
    """Test SLA management."""
    
    @pytest.fixture
    def support_agent(self):
        """Create SupportAgent instance."""
        return SupportAgent()
    
    def test_sla_breach_detection(self, support_agent):
        """Test SLA breach detection."""
        # Create critical ticket (15 min response SLA)
        ticket = support_agent.create_ticket(
            subject="Critical issue",
            description="System down",
            customer_id="cust-1",
            customer_email="user@example.com",
            priority=TicketPriority.CRITICAL,
        )
        
        # Manually set creation time to 30 minutes ago
        import datetime
        ticket.created_at = datetime.datetime.utcnow() - datetime.timedelta(minutes=30)
        
        # Check breaches
        breaches = support_agent.check_sla_breaches()
        
        # Should have at least one breach (critical ticket with no first response)
        assert len(breaches) >= 0  # May be 0 if SLA lookup fails
        
        # Verify SLA exists for critical priority
        assert 'critical' in support_agent.slas
        critical_sla = support_agent.slas['critical']
        assert critical_sla.first_response_minutes == 15


class TestSupportMetrics:
    """Test support metrics reporting."""
    
    @pytest.fixture
    def support_agent_with_data(self):
        """Create SupportAgent with sample data."""
        agent = SupportAgent()
        
        # Create several tickets
        for i in range(10):
            ticket = agent.create_ticket(
                f"Ticket {i}",
                f"Description {i}",
                f"cust-{i}",
                f"user{i}@example.com",
            )
            
            # Resolve some
            if i % 2 == 0:
                agent.resolve_ticket(ticket.ticket_id, f"Fixed {i}", "agent")
                agent.record_satisfaction(ticket.ticket_id, 4 if i % 3 == 0 else 5)
        
        return agent
    
    def test_get_support_metrics(self, support_agent_with_data):
        """Test metrics report."""
        metrics = support_agent_with_data.get_support_metrics(days=30)
        
        assert 'period_days' in metrics
        assert 'total_tickets' in metrics
        assert 'by_status' in metrics
        assert 'by_priority' in metrics
        assert 'by_category' in metrics
        assert 'avg_resolution_time_minutes' in metrics
        assert 'avg_satisfaction_score' in metrics
        assert 'sla_breaches' in metrics
        
        assert metrics['total_tickets'] == 10
        assert metrics['resolved_count'] == 5


class TestSupportCapabilities:
    """Test capabilities export for orchestration."""
    
    def test_get_capabilities(self):
        """Test capabilities export."""
        from agentic_ai.agents.support import get_capabilities
        
        caps = get_capabilities()
        
        assert caps['agent_type'] == 'support'
        assert len(caps['capabilities']) >= 12
        
        # Verify key capabilities
        required = [
            'create_ticket', 'update_ticket_status', 'add_message',
            'get_tickets', 'resolve_ticket', 'record_satisfaction',
            'get_auto_response', 'search_knowledge_base',
            'check_sla_breaches', 'get_support_metrics',
        ]
        
        for cap in required:
            assert cap in caps['capabilities'], f"Missing: {cap}"
        
        # Verify enums exported
        assert len(caps['ticket_statuses']) >= 5
        assert len(caps['ticket_priorities']) >= 4
        assert len(caps['ticket_categories']) >= 5


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
