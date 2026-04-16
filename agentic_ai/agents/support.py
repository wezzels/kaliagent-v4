"""
SupportAgent - Customer Support & Ticket Management
=====================================================

Provides ticket triage, auto-responses, knowledge base search,
escalation handling, and customer satisfaction tracking.
"""

import logging
import secrets
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from typing import Any, Dict, List, Optional, Tuple


logger = logging.getLogger(__name__)


class TicketStatus(Enum):
    """Ticket status states."""
    NEW = "new"
    OPEN = "open"
    IN_PROGRESS = "in_progress"
    WAITING_CUSTOMER = "waiting_customer"
    RESOLVED = "resolved"
    CLOSED = "closed"


class TicketPriority(Enum):
    """Ticket priority levels."""
    LOW = "low"
    NORMAL = "normal"
    HIGH = "high"
    CRITICAL = "critical"


class TicketCategory(Enum):
    """Ticket categories."""
    TECHNICAL = "technical"
    BILLING = "billing"
    ACCOUNT = "account"
    FEATURE_REQUEST = "feature_request"
    BUG_REPORT = "bug_report"
    GENERAL = "general"


@dataclass
class Ticket:
    """Support ticket."""
    ticket_id: str
    subject: str
    description: str
    customer_id: str
    customer_email: str
    status: TicketStatus
    priority: TicketPriority
    category: TicketCategory
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)
    assigned_to: Optional[str] = None
    tags: List[str] = field(default_factory=list)
    messages: List[Dict[str, Any]] = field(default_factory=list)
    resolution: Optional[str] = None
    resolved_at: Optional[datetime] = None
    resolved_by: Optional[str] = None
    satisfaction_score: Optional[int] = None  # 1-5
    first_response_time: Optional[float] = None  # minutes
    resolution_time: Optional[float] = None  # minutes


@dataclass
class KnowledgeArticle:
    """Knowledge base article."""
    article_id: str
    title: str
    content: str
    category: str
    tags: List[str] = field(default_factory=list)
    views: int = 0
    helpful_count: int = 0
    not_helpful_count: int = 0
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)


@dataclass
class SLA:
    """Service Level Agreement."""
    sla_id: str
    name: str
    priority: TicketPriority
    first_response_minutes: int
    resolution_minutes: int
    breach_count: int = 0


class SupportAgent:
    """
    Support Agent for ticket management, auto-responses,
    knowledge base, and customer satisfaction tracking.
    """
    
    def __init__(self, agent_id: str = "support-agent"):
        self.agent_id = agent_id
        self.tickets: Dict[str, Ticket] = {}
        self.knowledge_base: Dict[str, KnowledgeArticle] = {}
        self.slas: Dict[str, SLA] = {}
        self.auto_responses: Dict[str, str] = {}
        
        # Initialize default SLAs
        self._init_slas()
        self._init_auto_responses()
        self._init_knowledge_base()
    
    def _init_slas(self):
        """Initialize default SLAs."""
        self.slas = {
            'critical': SLA(
                sla_id='critical',
                name='Critical SLA',
                priority=TicketPriority.CRITICAL,
                first_response_minutes=15,
                resolution_minutes=60,
            ),
            'high': SLA(
                sla_id='high',
                name='High Priority SLA',
                priority=TicketPriority.HIGH,
                first_response_minutes=60,
                resolution_minutes=240,
            ),
            'normal': SLA(
                sla_id='normal',
                name='Normal SLA',
                priority=TicketPriority.NORMAL,
                first_response_minutes=240,
                resolution_minutes=1440,
            ),
            'low': SLA(
                sla_id='low',
                name='Low Priority SLA',
                priority=TicketPriority.LOW,
                first_response_minutes=1440,
                resolution_minutes=4320,
            ),
        }
    
    def _init_auto_responses(self):
        """Initialize auto-response templates."""
        self.auto_responses = {
            'password_reset': "To reset your password, please visit {base_url}/reset-password and follow the instructions.",
            'billing_question': "For billing inquiries, please check your invoice at {base_url}/billing or contact our billing team at billing@example.com.",
            'feature_request': "Thank you for your feature request! We've logged it for our product team to review. You can track feature requests at {base_url}/features.",
            'bug_report': "Thank you for reporting this issue. Our engineering team will investigate and update you within 24 hours.",
            'account_locked': "Your account has been temporarily locked for security. Please contact support@example.com to unlock it.",
        }
    
    def _init_knowledge_base(self):
        """Initialize sample knowledge base articles."""
        self.knowledge_base = {
            'kb-001': KnowledgeArticle(
                article_id='kb-001',
                title='How to Reset Your Password',
                content='To reset your password: 1. Go to login page 2. Click "Forgot Password" 3. Enter your email 4. Check email for reset link',
                category='account',
                tags=['password', 'login', 'account'],
            ),
            'kb-002': KnowledgeArticle(
                article_id='kb-002',
                title='Understanding Your Invoice',
                content='Your invoice includes: subscription fees, usage charges, taxes. Payment is due within 30 days.',
                category='billing',
                tags=['billing', 'invoice', 'payment'],
            ),
            'kb-003': KnowledgeArticle(
                article_id='kb-003',
                title='API Rate Limits',
                content='API rate limits: Free tier 100 req/hour, Pro tier 1000 req/hour, Enterprise unlimited.',
                category='technical',
                tags=['api', 'rate-limit', 'technical'],
            ),
        }
    
    # ============================================
    # Ticket Management
    # ============================================
    
    def create_ticket(
        self,
        subject: str,
        description: str,
        customer_id: str,
        customer_email: str,
        category: TicketCategory = TicketCategory.GENERAL,
        priority: TicketPriority = TicketPriority.NORMAL,
        tags: Optional[List[str]] = None,
    ) -> Ticket:
        """Create a new support ticket."""
        ticket = Ticket(
            ticket_id=self._generate_id("ticket"),
            subject=subject,
            description=description,
            customer_id=customer_id,
            customer_email=customer_email,
            status=TicketStatus.NEW,
            priority=priority,
            category=category,
            tags=tags or [],
        )
        
        self.tickets[ticket.ticket_id] = ticket
        logger.info(f"Created ticket: {ticket.ticket_id} - {subject}")
        
        # Auto-triage
        self._auto_triage_ticket(ticket)
        
        return ticket
    
    def _auto_triage_ticket(self, ticket: Ticket):
        """Auto-triage ticket based on content."""
        # Auto-assign category based on keywords
        text = (ticket.subject + " " + ticket.description).lower()
        
        if any(word in text for word in ['password', 'login', 'account', 'access']):
            ticket.category = TicketCategory.ACCOUNT
        elif any(word in text for word in ['billing', 'invoice', 'payment', 'charge', 'refund']):
            ticket.category = TicketCategory.BILLING
        elif any(word in text for word in ['bug', 'error', 'crash', 'broken', 'issue']):
            ticket.category = TicketCategory.BUG_REPORT
        elif any(word in text for word in ['feature', 'request', 'suggestion', 'improve']):
            ticket.category = TicketCategory.FEATURE_REQUEST
        elif any(word in text for word in ['api', 'integration', 'technical', 'code']):
            ticket.category = TicketCategory.TECHNICAL
        
        # Auto-assign priority
        if any(word in text for word in ['urgent', 'critical', 'down', 'broken', 'emergency']):
            ticket.priority = TicketPriority.HIGH
        elif any(word in text for word in ['please', 'help', 'question']):
            ticket.priority = TicketPriority.NORMAL
        
        # Auto-assign based on category
        if ticket.category == TicketCategory.BILLING:
            ticket.assigned_to = "billing-team"
        elif ticket.category == TicketCategory.TECHNICAL:
            ticket.assigned_to = "technical-team"
        
        ticket.messages.append({
            'type': 'system',
            'content': f'Ticket auto-triaged: Category={ticket.category.value}, Priority={ticket.priority.value}',
            'timestamp': datetime.utcnow().isoformat(),
        })
    
    def update_ticket_status(
        self,
        ticket_id: str,
        status: TicketStatus,
        assigned_to: Optional[str] = None,
    ) -> Optional[Ticket]:
        """Update ticket status."""
        if ticket_id not in self.tickets:
            return None
        
        ticket = self.tickets[ticket_id]
        ticket.status = status
        ticket.updated_at = datetime.utcnow()
        
        if assigned_to:
            ticket.assigned_to = assigned_to
        
        if status == TicketStatus.RESOLVED:
            ticket.resolved_at = datetime.utcnow()
            # Calculate resolution time
            ticket.resolution_time = (ticket.resolved_at - ticket.created_at).total_seconds() / 60
        
        logger.info(f"Ticket {ticket_id} status: {status.value}")
        return ticket
    
    def add_message(
        self,
        ticket_id: str,
        content: str,
        sender: str,  # 'customer' or agent email
        is_internal: bool = False,
    ) -> bool:
        """Add a message to a ticket."""
        if ticket_id not in self.tickets:
            return False
        
        ticket = self.tickets[ticket_id]
        
        message = {
            'type': 'internal' if is_internal else 'message',
            'sender': sender,
            'content': content,
            'timestamp': datetime.utcnow().isoformat(),
        }
        
        ticket.messages.append(message)
        ticket.updated_at = datetime.utcnow()
        
        # If customer replies, change status to open
        if sender == 'customer' and ticket.status == TicketStatus.WAITING_CUSTOMER:
            ticket.status = TicketStatus.OPEN
        
        # Track first response time
        if ticket.first_response_time is None and sender != 'customer':
            ticket.first_response_time = (datetime.utcnow() - ticket.created_at).total_seconds() / 60
        
        return True
    
    def get_tickets(
        self,
        status: Optional[TicketStatus] = None,
        priority: Optional[TicketPriority] = None,
        category: Optional[TicketCategory] = None,
        assigned_to: Optional[str] = None,
        limit: int = 50,
    ) -> List[Ticket]:
        """Get tickets with filtering."""
        tickets = list(self.tickets.values())
        
        if status:
            tickets = [t for t in tickets if t.status == status]
        
        if priority:
            tickets = [t for t in tickets if t.priority == priority]
        
        if category:
            tickets = [t for t in tickets if t.category == category]
        
        if assigned_to:
            tickets = [t for t in tickets if t.assigned_to == assigned_to]
        
        # Sort by created_at (newest first)
        tickets.sort(key=lambda x: x.created_at, reverse=True)
        
        return tickets[:limit]
    
    def resolve_ticket(
        self,
        ticket_id: str,
        resolution: str,
        resolved_by: str,
    ) -> Optional[Ticket]:
        """Resolve a ticket."""
        if ticket_id not in self.tickets:
            return None
        
        ticket = self.tickets[ticket_id]
        ticket.status = TicketStatus.RESOLVED
        ticket.resolution = resolution
        ticket.resolved_at = datetime.utcnow()
        ticket.resolved_by = resolved_by
        ticket.resolution_time = (ticket.resolved_at - ticket.created_at).total_seconds() / 60
        
        ticket.messages.append({
            'type': 'resolution',
            'content': resolution,
            'sender': resolved_by,
            'timestamp': datetime.utcnow().isoformat(),
        })
        
        logger.info(f"Ticket {ticket_id} resolved by {resolved_by}")
        return ticket
    
    def record_satisfaction(
        self,
        ticket_id: str,
        score: int,  # 1-5
    ) -> bool:
        """Record customer satisfaction score."""
        if ticket_id not in self.tickets:
            return False
        
        if score < 1 or score > 5:
            return False
        
        self.tickets[ticket_id].satisfaction_score = score
        return True
    
    # ============================================
    # Auto-Responses
    # ============================================
    
    def get_auto_response(self, ticket: Ticket, base_url: str = "https://example.com") -> Optional[str]:
        """Get auto-response for ticket based on category."""
        template_key = None
        
        if ticket.category == TicketCategory.ACCOUNT:
            if 'password' in ticket.description.lower():
                template_key = 'password_reset'
            elif 'locked' in ticket.description.lower():
                template_key = 'account_locked'
        elif ticket.category == TicketCategory.BILLING:
            template_key = 'billing_question'
        elif ticket.category == TicketCategory.FEATURE_REQUEST:
            template_key = 'feature_request'
        elif ticket.category == TicketCategory.BUG_REPORT:
            template_key = 'bug_report'
        
        if template_key and template_key in self.auto_responses:
            return self.auto_responses[template_key].format(base_url=base_url)
        
        return None
    
    # ============================================
    # Knowledge Base
    # ============================================
    
    def search_knowledge_base(self, query: str) -> List[KnowledgeArticle]:
        """Search knowledge base articles."""
        query_lower = query.lower()
        results = []
        
        for article in self.knowledge_base.values():
            # Search in title, content, and tags
            searchable = (article.title + " " + article.content + " " + " ".join(article.tags)).lower()
            
            if query_lower in searchable:
                results.append(article)
                article.views += 1
        
        # Sort by helpfulness
        results.sort(key=lambda a: a.helpful_count, reverse=True)
        
        return results
    
    def rate_article(self, article_id: str, helpful: bool) -> bool:
        """Rate a knowledge base article."""
        if article_id not in self.knowledge_base:
            return False
        
        article = self.knowledge_base[article_id]
        
        if helpful:
            article.helpful_count += 1
        else:
            article.not_helpful_count += 1
        
        return True
    
    def add_knowledge_article(
        self,
        title: str,
        content: str,
        category: str,
        tags: Optional[List[str]] = None,
    ) -> KnowledgeArticle:
        """Add a new knowledge base article."""
        article = KnowledgeArticle(
            article_id=self._generate_id("kb"),
            title=title,
            content=content,
            category=category,
            tags=tags or [],
        )
        
        self.knowledge_base[article.article_id] = article
        logger.info(f"Added KB article: {article.title}")
        return article
    
    # ============================================
    # SLA Management
    # ============================================
    
    def check_sla_breaches(self) -> List[Ticket]:
        """Check for SLA breaches."""
        breaches = []
        now = datetime.utcnow()
        
        for ticket in self.tickets.values():
            if ticket.status in [TicketStatus.RESOLVED, TicketStatus.CLOSED]:
                continue
            
            sla = self.slas.get(ticket.priority.value)
            if not sla:
                continue
            
            # Check first response
            if ticket.first_response_time is None:
                time_since_creation = (now - ticket.created_at).total_seconds() / 60
                if time_since_creation > sla.first_response_minutes:
                    breaches.append(ticket)
                    logger.warning(f"SLA breach: Ticket {ticket.ticket_id} - first response overdue")
            
            # Check resolution
            time_since_creation = (now - ticket.created_at).total_seconds() / 60
            if time_since_creation > sla.resolution_minutes:
                if ticket not in breaches:
                    breaches.append(ticket)
                    logger.warning(f"SLA breach: Ticket {ticket.ticket_id} - resolution overdue")
        
        return breaches
    
    # ============================================
    # Reporting
    # ============================================
    
    def get_support_metrics(self, days: int = 30) -> Dict[str, Any]:
        """Get support metrics report."""
        cutoff = datetime.utcnow() - timedelta(days=days)
        
        # Filter tickets by date
        recent_tickets = [t for t in self.tickets.values() if t.created_at > cutoff]
        
        # Status breakdown
        by_status = {}
        for ticket in recent_tickets:
            status = ticket.status.value
            by_status[status] = by_status.get(status, 0) + 1
        
        # Priority breakdown
        by_priority = {}
        for ticket in recent_tickets:
            priority = ticket.priority.value
            by_priority[priority] = by_priority.get(priority, 0) + 1
        
        # Category breakdown
        by_category = {}
        for ticket in recent_tickets:
            category = ticket.category.value
            by_category[category] = by_category.get(category, 0) + 1
        
        # Resolution metrics
        resolved = [t for t in recent_tickets if t.status == TicketStatus.RESOLVED]
        avg_resolution_time = sum(t.resolution_time for t in resolved if t.resolution_time) / len(resolved) if resolved else 0
        
        # Satisfaction
        scored = [t for t in resolved if t.satisfaction_score]
        avg_satisfaction = sum(t.satisfaction_score for t in scored) / len(scored) if scored else 0
        
        # SLA breaches
        breaches = self.check_sla_breaches()
        
        return {
            'period_days': days,
            'total_tickets': len(recent_tickets),
            'by_status': by_status,
            'by_priority': by_priority,
            'by_category': by_category,
            'avg_resolution_time_minutes': round(avg_resolution_time, 2),
            'avg_satisfaction_score': round(avg_satisfaction, 2),
            'sla_breaches': len(breaches),
            'resolved_count': len(resolved),
            'open_count': len([t for t in recent_tickets if t.status not in [TicketStatus.RESOLVED, TicketStatus.CLOSED]]),
        }
    
    # ============================================
    # Utilities
    # ============================================
    
    def _generate_id(self, prefix: str) -> str:
        """Generate a unique ID."""
        timestamp = datetime.utcnow().strftime('%Y%m%d%H%M%S')
        random_suffix = secrets.token_hex(4)
        return f"{prefix}-{timestamp}-{random_suffix}"
    
    def get_state(self) -> Dict[str, Any]:
        """Get agent state summary."""
        return {
            'agent_id': self.agent_id,
            'tickets_count': len(self.tickets),
            'open_tickets': len([t for t in self.tickets.values() if t.status not in [TicketStatus.RESOLVED, TicketStatus.CLOSED]]),
            'knowledge_articles': len(self.knowledge_base),
            'sla_breaches': len(self.check_sla_breaches()),
        }


def get_capabilities() -> Dict[str, Any]:
    """Return agent capabilities for orchestration."""
    return {
        'agent_type': 'support',
        'version': '1.0.0',
        'capabilities': [
            'create_ticket',
            'update_ticket_status',
            'add_message',
            'get_tickets',
            'resolve_ticket',
            'record_satisfaction',
            'get_auto_response',
            'search_knowledge_base',
            'rate_article',
            'add_knowledge_article',
            'check_sla_breaches',
            'get_support_metrics',
        ],
        'ticket_statuses': [s.value for s in TicketStatus],
        'ticket_priorities': [p.value for p in TicketPriority],
        'ticket_categories': [c.value for c in TicketCategory],
    }


if __name__ == "__main__":
    # Quick test
    agent = SupportAgent()
    
    # Create ticket
    ticket = agent.create_ticket(
        subject="Can't login to my account",
        description="I forgot my password and need to reset it",
        customer_id="cust-123",
        customer_email="user@example.com",
    )
    
    print(f"Created ticket: {ticket.ticket_id}")
    print(f"Auto-triaged: Category={ticket.category.value}, Priority={ticket.priority.value}")
    
    # Get auto-response
    response = agent.get_auto_response(ticket)
    print(f"Auto-response: {response}")
    
    # Search KB
    articles = agent.search_knowledge_base("password reset")
    print(f"KB articles found: {len(articles)}")
    
    print(f"\nState: {agent.get_state()}")
