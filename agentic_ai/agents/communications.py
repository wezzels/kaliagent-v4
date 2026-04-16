"""
CommunicationsAgent - Multi-Channel Communications
===================================================

Provides email campaigns, SMS notifications, push notifications,
message templates, delivery tracking, and communication analytics.
"""

import logging
import secrets
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from typing import Any, Dict, List, Optional


logger = logging.getLogger(__name__)


class ChannelType(Enum):
    """Communication channel types."""
    EMAIL = "email"
    SMS = "sms"
    PUSH = "push"
    SLACK = "slack"
    TEAMS = "teams"
    WEBHOOK = "webhook"


class MessageStatus(Enum):
    """Message delivery status."""
    DRAFT = "draft"
    SCHEDULED = "scheduled"
    SENT = "sent"
    DELIVERED = "delivered"
    FAILED = "failed"
    BOUNCED = "bounced"
    OPENED = "opened"
    CLICKED = "clicked"


class Priority(Enum):
    """Message priority levels."""
    LOW = "low"
    NORMAL = "normal"
    HIGH = "high"
    URGENT = "urgent"


@dataclass
class Contact:
    """Contact record."""
    contact_id: str
    name: str
    email: Optional[str] = None
    phone: Optional[str] = None
    preferences: Dict[str, bool] = field(default_factory=dict)
    tags: List[str] = field(default_factory=list)
    created_at: datetime = field(default_factory=datetime.utcnow)


@dataclass
class Message:
    """Communication message."""
    message_id: str
    channel: ChannelType
    subject: str
    content: str
    status: MessageStatus
    recipients: List[str]
    scheduled_at: Optional[datetime] = None
    sent_at: Optional[datetime] = None
    priority: Priority = Priority.NORMAL
    template_id: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.utcnow)


@dataclass
class Template:
    """Message template."""
    template_id: str
    name: str
    channel: ChannelType
    subject: str
    content: str
    variables: List[str] = field(default_factory=list)
    category: str = "general"
    version: str = "1.0"
    created_at: datetime = field(default_factory=datetime.utcnow)


@dataclass
class Campaign:
    """Communication campaign."""
    campaign_id: str
    name: str
    channel: ChannelType
    status: str  # draft, active, paused, completed
    total_recipients: int = 0
    sent_count: int = 0
    delivered_count: int = 0
    opened_count: int = 0
    clicked_count: int = 0
    failed_count: int = 0
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    created_at: datetime = field(default_factory=datetime.utcnow)


class CommunicationsAgent:
    """
    Communications Agent for multi-channel messaging,
    campaign management, and delivery tracking.
    """
    
    def __init__(self, agent_id: str = "communications-agent"):
        self.agent_id = agent_id
        self.contacts: Dict[str, Contact] = {}
        self.messages: Dict[str, Message] = {}
        self.templates: Dict[str, Template] = {}
        self.campaigns: Dict[str, Campaign] = {}
        
        # Channel configurations
        self.channel_configs: Dict[ChannelType, Dict[str, Any]] = {
            ChannelType.EMAIL: {'provider': 'sendgrid', 'enabled': True},
            ChannelType.SMS: {'provider': 'twilio', 'enabled': True},
            ChannelType.PUSH: {'provider': 'firebase', 'enabled': True},
            ChannelType.SLACK: {'provider': 'slack_api', 'enabled': True},
            ChannelType.TEAMS: {'provider': 'teams_webhook', 'enabled': True},
        }
    
    # ============================================
    # Contact Management
    # ============================================
    
    def add_contact(
        self,
        name: str,
        email: Optional[str] = None,
        phone: Optional[str] = None,
        preferences: Optional[Dict[str, bool]] = None,
        tags: Optional[List[str]] = None,
    ) -> Contact:
        """Add a contact."""
        contact = Contact(
            contact_id=self._generate_id("contact"),
            name=name,
            email=email,
            phone=phone,
            preferences=preferences or {'email': True, 'sms': True, 'push': True},
            tags=tags or [],
        )
        
        self.contacts[contact.contact_id] = contact
        return contact
    
    def get_contacts(self, tag: Optional[str] = None) -> List[Contact]:
        """Get contacts with filtering."""
        contacts = list(self.contacts.values())
        
        if tag:
            contacts = [c for c in contacts if tag in c.tags]
        
        return contacts
    
    def update_preferences(self, contact_id: str, preferences: Dict[str, bool]) -> bool:
        """Update contact communication preferences."""
        if contact_id not in self.contacts:
            return False
        
        self.contacts[contact_id].preferences.update(preferences)
        return True
    
    # ============================================
    # Template Management
    # ============================================
    
    def create_template(
        self,
        name: str,
        channel: ChannelType,
        subject: str,
        content: str,
        variables: Optional[List[str]] = None,
        category: str = "general",
    ) -> Template:
        """Create a message template."""
        template = Template(
            template_id=self._generate_id("template"),
            name=name,
            channel=channel,
            subject=subject,
            content=content,
            variables=variables or [],
            category=category,
        )
        
        self.templates[template.template_id] = template
        logger.info(f"Created template: {template.name}")
        return template
    
    def render_template(self, template_id: str, values: Dict[str, str]) -> Optional[Dict[str, str]]:
        """Render a template with values."""
        if template_id not in self.templates:
            return None
        
        template = self.templates[template_id]
        
        subject = template.subject
        content = template.content
        
        for key, value in values.items():
            subject = subject.replace(f"{{{key}}}", value)
            content = content.replace(f"{{{key}}}", value)
        
        return {'subject': subject, 'content': content}
    
    def get_templates(self, channel: Optional[ChannelType] = None) -> List[Template]:
        """Get templates with filtering."""
        templates = list(self.templates.values())
        
        if channel:
            templates = [t for t in templates if t.channel == channel]
        
        return templates
    
    # ============================================
    # Message Sending
    # ============================================
    
    def send_message(
        self,
        channel: ChannelType,
        subject: str,
        content: str,
        recipients: List[str],
        priority: Priority = Priority.NORMAL,
        template_id: Optional[str] = None,
    ) -> Message:
        """Send a message."""
        message = Message(
            message_id=self._generate_id("msg"),
            channel=channel,
            subject=subject,
            content=content,
            status=MessageStatus.SENT,
            recipients=recipients,
            sent_at=datetime.utcnow(),
            priority=priority,
            template_id=template_id,
        )
        
        self.messages[message.message_id] = message
        logger.info(f"Sent {channel.value} message to {len(recipients)} recipients")
        
        return message
    
    def schedule_message(
        self,
        channel: ChannelType,
        subject: str,
        content: str,
        recipients: List[str],
        scheduled_at: datetime,
        priority: Priority = Priority.NORMAL,
    ) -> Message:
        """Schedule a message for later delivery."""
        message = Message(
            message_id=self._generate_id("msg"),
            channel=channel,
            subject=subject,
            content=content,
            status=MessageStatus.SCHEDULED,
            recipients=recipients,
            scheduled_at=scheduled_at,
            priority=priority,
        )
        
        self.messages[message.message_id] = message
        logger.info(f"Scheduled {channel.value} message for {scheduled_at}")
        
        return message
    
    def update_message_status(self, message_id: str, status: MessageStatus) -> bool:
        """Update message delivery status."""
        if message_id not in self.messages:
            return False
        
        self.messages[message_id].status = status
        return True
    
    def get_messages(
        self,
        channel: Optional[ChannelType] = None,
        status: Optional[MessageStatus] = None,
        limit: int = 100,
    ) -> List[Message]:
        """Get messages with filtering."""
        messages = list(self.messages.values())
        
        if channel:
            messages = [m for m in messages if m.channel == channel]
        
        if status:
            messages = [m for m in messages if m.status == status]
        
        return messages[-limit:]
    
    # ============================================
    # Campaign Management
    # ============================================
    
    def create_campaign(
        self,
        name: str,
        channel: ChannelType,
        total_recipients: int,
    ) -> Campaign:
        """Create a communication campaign."""
        campaign = Campaign(
            campaign_id=self._generate_id("camp"),
            name=name,
            channel=channel,
            status="draft",
            total_recipients=total_recipients,
        )
        
        self.campaigns[campaign.campaign_id] = campaign
        return campaign
    
    def start_campaign(self, campaign_id: str) -> bool:
        """Start a campaign."""
        if campaign_id not in self.campaigns:
            return False
        
        campaign = self.campaigns[campaign_id]
        campaign.status = "active"
        campaign.start_date = datetime.utcnow()
        
        return True
    
    def update_campaign_metrics(
        self,
        campaign_id: str,
        sent: int = 0,
        delivered: int = 0,
        opened: int = 0,
        clicked: int = 0,
        failed: int = 0,
    ) -> bool:
        """Update campaign metrics."""
        if campaign_id not in self.campaigns:
            return False
        
        campaign = self.campaigns[campaign_id]
        campaign.sent_count = sent
        campaign.delivered_count = delivered
        campaign.opened_count = opened
        campaign.clicked_count = clicked
        campaign.failed_count = failed
        
        return True
    
    def complete_campaign(self, campaign_id: str) -> bool:
        """Complete a campaign."""
        if campaign_id not in self.campaigns:
            return False
        
        campaign = self.campaigns[campaign_id]
        campaign.status = "completed"
        campaign.end_date = datetime.utcnow()
        
        return True
    
    def get_campaigns(self, status: Optional[str] = None) -> List[Campaign]:
        """Get campaigns with filtering."""
        campaigns = list(self.campaigns.values())
        
        if status:
            campaigns = [c for c in campaigns if c.status == status]
        
        return campaigns
    
    # ============================================
    # Analytics & Reporting
    # ============================================
    
    def get_delivery_stats(self, channel: Optional[ChannelType] = None) -> Dict[str, Any]:
        """Get delivery statistics."""
        messages = list(self.messages.values())
        
        if channel:
            messages = [m for m in messages if m.channel == channel]
        
        total = len(messages)
        sent = len([m for m in messages if m.status == MessageStatus.SENT])
        delivered = len([m for m in messages if m.status == MessageStatus.DELIVERED])
        opened = len([m for m in messages if m.status == MessageStatus.OPENED])
        clicked = len([m for m in messages if m.status == MessageStatus.CLICKED])
        failed = len([m for m in messages if m.status in [MessageStatus.FAILED, MessageStatus.BOUNCED]])
        
        return {
            'total_messages': total,
            'sent': sent,
            'delivered': delivered,
            'opened': opened,
            'clicked': clicked,
            'failed': failed,
            'delivery_rate': round(delivered / sent * 100, 1) if sent > 0 else 0,
            'open_rate': round(opened / delivered * 100, 1) if delivered > 0 else 0,
            'click_rate': round(clicked / delivered * 100, 1) if delivered > 0 else 0,
            'failure_rate': round(failed / total * 100, 1) if total > 0 else 0,
        }
    
    def get_campaign_performance(self, campaign_id: str) -> Optional[Dict[str, Any]]:
        """Get campaign performance metrics."""
        if campaign_id not in self.campaigns:
            return None
        
        campaign = self.campaigns[campaign_id]
        
        return {
            'campaign_id': campaign_id,
            'name': campaign.name,
            'channel': campaign.channel.value,
            'status': campaign.status,
            'total_recipients': campaign.total_recipients,
            'sent': campaign.sent_count,
            'delivered': campaign.delivered_count,
            'opened': campaign.opened_count,
            'clicked': campaign.clicked_count,
            'failed': campaign.failed_count,
            'open_rate': round(campaign.opened_count / campaign.delivered_count * 100, 1) if campaign.delivered_count > 0 else 0,
            'click_rate': round(campaign.clicked_count / campaign.delivered_count * 100, 1) if campaign.delivered_count > 0 else 0,
        }
    
    def get_channel_health(self) -> Dict[str, Any]:
        """Get channel health status."""
        health = {}
        
        for channel, config in self.channel_configs.items():
            channel_messages = [m for m in self.messages.values() if m.channel == channel]
            failed = len([m for m in channel_messages if m.status in [MessageStatus.FAILED, MessageStatus.BOUNCED]])
            
            health[channel.value] = {
                'enabled': config.get('enabled', False),
                'provider': config.get('provider', 'unknown'),
                'total_messages': len(channel_messages),
                'failures': failed,
                'status': 'healthy' if failed < len(channel_messages) * 0.1 else 'degraded',
            }
        
        return health
    
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
            'contacts_count': len(self.contacts),
            'messages_count': len(self.messages),
            'templates_count': len(self.templates),
            'campaigns_count': len(self.campaigns),
            'channels_enabled': sum(1 for c in self.channel_configs.values() if c.get('enabled')),
        }


def get_capabilities() -> Dict[str, Any]:
    """Return agent capabilities for orchestration."""
    return {
        'agent_type': 'communications',
        'version': '1.0.0',
        'capabilities': [
            'add_contact',
            'get_contacts',
            'update_preferences',
            'create_template',
            'render_template',
            'get_templates',
            'send_message',
            'schedule_message',
            'update_message_status',
            'get_messages',
            'create_campaign',
            'start_campaign',
            'update_campaign_metrics',
            'complete_campaign',
            'get_campaigns',
            'get_delivery_stats',
            'get_campaign_performance',
            'get_channel_health',
        ],
        'channel_types': [c.value for c in ChannelType],
        'message_statuses': [s.value for s in MessageStatus],
        'priorities': [p.value for p in Priority],
    }


if __name__ == "__main__":
    agent = CommunicationsAgent()
    
    # Add contacts
    contact1 = agent.add_contact(
        name="John Doe",
        email="john@example.com",
        phone="+1234567890",
        tags=['customer', 'vip'],
    )
    
    print(f"Added contact: {contact1.name}")
    
    # Create template
    template = agent.create_template(
        name="Welcome Email",
        channel=ChannelType.EMAIL,
        subject="Welcome to {company}!",
        content="Hi {name}, welcome aboard!",
        variables=['company', 'name'],
        category="onboarding",
    )
    
    print(f"Created template: {template.name}")
    
    # Render template
    rendered = agent.render_template(template.template_id, {'company': 'Acme', 'name': 'John'})
    print(f"Rendered: {rendered['subject']}")
    
    # Send message
    message = agent.send_message(
        channel=ChannelType.EMAIL,
        subject="Important Update",
        content="This is an important update...",
        recipients=["user1@example.com", "user2@example.com"],
        priority=Priority.HIGH,
    )
    
    print(f"Sent message to {len(message.recipients)} recipients")
    
    # Create campaign
    campaign = agent.create_campaign(
        name="Q2 Newsletter",
        channel=ChannelType.EMAIL,
        total_recipients=1000,
    )
    
    print(f"Created campaign: {campaign.name}")
    
    # Get delivery stats
    stats = agent.get_delivery_stats()
    print(f"\nDelivery Rate: {stats['delivery_rate']}%")
    
    print(f"\nState: {agent.get_state()}")
