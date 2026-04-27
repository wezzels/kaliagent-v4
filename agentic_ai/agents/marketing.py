"""
MarketingAgent - Marketing Campaigns & Content
===============================================

Provides campaign management, content creation, social media scheduling,
A/B testing, and marketing analytics.
"""

import logging
import secrets
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from typing import Any, Dict, List, Optional


logger = logging.getLogger(__name__)


class CampaignStatus(Enum):
    """Campaign status states."""
    DRAFT = "draft"
    PLANNED = "planned"
    ACTIVE = "active"
    PAUSED = "paused"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


class CampaignType(Enum):
    """Campaign types."""
    EMAIL = "email"
    SOCIAL_MEDIA = "social_media"
    CONTENT = "content"
    PAID_ADS = "paid_ads"
    WEBINAR = "webinar"
    PRODUCT_LAUNCH = "product_launch"


class SocialPlatform(Enum):
    """Social media platforms."""
    TWITTER = "twitter"
    LINKEDIN = "linkedin"
    FACEBOOK = "facebook"
    INSTAGRAM = "instagram"
    YOUTUBE = "youtube"
    TIKTOK = "tiktok"


@dataclass
class Campaign:
    """Marketing campaign."""
    campaign_id: str
    name: str
    campaign_type: CampaignType
    status: CampaignStatus
    start_date: datetime
    end_date: Optional[datetime] = None
    budget: float = 0.0
    target_audience: str = ""
    goals: List[str] = field(default_factory=list)
    metrics: Dict[str, float] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.utcnow)


@dataclass
class Content:
    """Content piece."""
    content_id: str
    title: str
    content_type: str  # blog, video, infographic, etc.
    status: str  # draft, review, published
    platform: Optional[str] = None
    scheduled_date: Optional[datetime] = None
    word_count: int = 0
    tags: List[str] = field(default_factory=list)
    created_at: datetime = field(default_factory=datetime.utcnow)


@dataclass
class ABTest:
    """A/B test configuration."""
    test_id: str
    name: str
    variant_a: Dict[str, Any]
    variant_b: Dict[str, Any]
    metric: str
    sample_size: int = 1000
    confidence_level: float = 95.0
    status: str = "running"  # running, completed, inconclusive
    results: Optional[Dict[str, Any]] = None
    created_at: datetime = field(default_factory=datetime.utcnow)


class MarketingAgent:
    """
    Marketing Agent for campaign management, content creation,
    social media, A/B testing, and analytics.
    """

    def __init__(self, agent_id: str = "marketing-agent"):
        self.agent_id = agent_id
        self.campaigns: Dict[str, Campaign] = {}
        self.content: Dict[str, Content] = {}
        self.ab_tests: Dict[str, ABTest] = {}
        self.social_posts: List[Dict[str, Any]] = []
        self.analytics: Dict[str, List[Dict[str, Any]]] = {}

        # Content templates
        self.templates = {
            'email_subject': ["🚀 {product}: {benefit}", "Don't miss out on {offer}!", "New: {feature} is here"],
            'social_post': ["Exciting news! {announcement} #innovation", "We're thrilled to share {update} 🎉", "Just launched: {product}"],
            'blog_title': ["How to {action} in {year}", "The Ultimate Guide to {topic}", "{number} Ways to {improve}"],
        }

    # ============================================
    # Campaign Management
    # ============================================

    def create_campaign(
        self,
        name: str,
        campaign_type: CampaignType,
        start_date: datetime,
        budget: float = 0.0,
        target_audience: str = "",
        goals: Optional[List[str]] = None,
    ) -> Campaign:
        """Create a new marketing campaign."""
        campaign = Campaign(
            campaign_id=self._generate_id("campaign"),
            name=name,
            campaign_type=campaign_type,
            status=CampaignStatus.DRAFT,
            start_date=start_date,
            budget=budget,
            target_audience=target_audience,
            goals=goals or [],
        )

        self.campaigns[campaign.campaign_id] = campaign
        logger.info(f"Created campaign: {campaign.name}")
        return campaign

    def update_campaign_status(
        self,
        campaign_id: str,
        status: CampaignStatus,
    ) -> Optional[Campaign]:
        """Update campaign status."""
        if campaign_id not in self.campaigns:
            return None

        campaign = self.campaigns[campaign_id]
        campaign.status = status

        if status == CampaignStatus.ACTIVE:
            campaign.metrics['start_date'] = datetime.utcnow().isoformat()

        logger.info(f"Campaign {campaign_id} status: {status.value}")
        return campaign

    def track_campaign_metrics(
        self,
        campaign_id: str,
        metrics: Dict[str, float],
    ) -> bool:
        """Track campaign performance metrics."""
        if campaign_id not in self.campaigns:
            return False

        campaign = self.campaigns[campaign_id]
        campaign.metrics.update(metrics)

        return True

    def get_campaigns(
        self,
        status: Optional[CampaignStatus] = None,
        campaign_type: Optional[CampaignType] = None,
    ) -> List[Campaign]:
        """Get campaigns with filtering."""
        campaigns = list(self.campaigns.values())

        if status:
            campaigns = [c for c in campaigns if c.status == status]

        if campaign_type:
            campaigns = [c for c in campaigns if c.campaign_type == campaign_type]

        return campaigns

    # ============================================
    # Content Management
    # ============================================

    def create_content(
        self,
        title: str,
        content_type: str,
        platform: Optional[str] = None,
        scheduled_date: Optional[datetime] = None,
        tags: Optional[List[str]] = None,
    ) -> Content:
        """Create content piece."""
        content = Content(
            content_id=self._generate_id("content"),
            title=title,
            content_type=content_type,
            status="draft",
            platform=platform,
            scheduled_date=scheduled_date,
            tags=tags or [],
        )

        self.content[content.content_id] = content
        logger.info(f"Created content: {content.title}")
        return content

    def publish_content(self, content_id: str, word_count: int = 0) -> bool:
        """Publish content."""
        if content_id not in self.content:
            return False

        content = self.content[content_id]
        content.status = "published"
        content.word_count = word_count

        return True

    def schedule_social_post(
        self,
        platform: SocialPlatform,
        content: str,
        scheduled_time: datetime,
        campaign_id: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Schedule a social media post."""
        post = {
            'post_id': self._generate_id("post"),
            'platform': platform.value,
            'content': content,
            'scheduled_time': scheduled_time.isoformat(),
            'status': 'scheduled',
            'campaign_id': campaign_id,
            'created_at': datetime.utcnow().isoformat(),
        }

        self.social_posts.append(post)
        logger.info(f"Scheduled {platform.value} post for {scheduled_time}")
        return post

    # ============================================
    # A/B Testing
    # ============================================

    def create_ab_test(
        self,
        name: str,
        variant_a: Dict[str, Any],
        variant_b: Dict[str, Any],
        metric: str,
        sample_size: int = 1000,
    ) -> ABTest:
        """Create A/B test."""
        test = ABTest(
            test_id=self._generate_id("abtest"),
            name=name,
            variant_a=variant_a,
            variant_b=variant_b,
            metric=metric,
            sample_size=sample_size,
        )

        self.ab_tests[test.test_id] = test
        logger.info(f"Created A/B test: {test.name}")
        return test

    def complete_ab_test(
        self,
        test_id: str,
        results: Dict[str, Any],
    ) -> Optional[ABTest]:
        """Complete A/B test with results."""
        if test_id not in self.ab_tests:
            return None

        test = self.ab_tests[test_id]
        test.status = "completed"
        test.results = results

        # Determine winner
        if results.get('variant_a_score', 0) > results.get('variant_b_score', 0):
            results['winner'] = 'A'
        elif results.get('variant_b_score', 0) > results.get('variant_a_score', 0):
            results['winner'] = 'B'
        else:
            results['winner'] = 'tie'
            test.status = "inconclusive"

        return test

    def get_ab_tests(self, status: Optional[str] = None) -> List[ABTest]:
        """Get A/B tests with filtering."""
        tests = list(self.ab_tests.values())

        if status:
            tests = [t for t in tests if t.status == status]

        return tests

    # ============================================
    # Content Templates
    # ============================================

    def generate_email_subjects(self, product: str, benefit: str, offer: str = "") -> List[str]:
        """Generate email subject line variations."""
        subjects = []
        for template in self.templates['email_subject']:
            subject = template.format(
                product=product,
                benefit=benefit,
                offer=offer or benefit,
            )
            subjects.append(subject)
        return subjects

    def generate_social_posts(self, announcement: str, update: str = "", product: str = "") -> List[str]:
        """Generate social media post variations."""
        posts = []
        for template in self.templates['social_post']:
            post = template.format(
                announcement=announcement,
                update=update or announcement,
                product=product or announcement,
            )
            posts.append(post)
        return posts

    def generate_blog_titles(self, action: str, topic: str, improve: str = "", year: int = 2026, number: int = 10) -> List[str]:
        """Generate blog title variations."""
        titles = []
        for template in self.templates['blog_title']:
            title = template.format(
                action=action,
                topic=topic,
                improve=improve or action,
                year=year,
                number=number,
            )
            titles.append(title)
        return titles

    # ============================================
    # Analytics
    # ============================================

    def track_analytics(self, channel: str, metrics: Dict[str, Any]):
        """Track marketing analytics."""
        if channel not in self.analytics:
            self.analytics[channel] = []

        metrics['timestamp'] = datetime.utcnow().isoformat()
        self.analytics[channel].append(metrics)

        # Keep last 1000 data points
        if len(self.analytics[channel]) > 1000:
            self.analytics[channel] = self.analytics[channel][-1000:]

    def get_analytics_summary(self, days: int = 30) -> Dict[str, Any]:
        """Get analytics summary."""
        summary = {
            'period_days': days,
            'campaigns': {
                'total': len(self.campaigns),
                'active': len([c for c in self.campaigns.values() if c.status == CampaignStatus.ACTIVE]),
                'completed': len([c for c in self.campaigns.values() if c.status == CampaignStatus.COMPLETED]),
            },
            'content': {
                'total': len(self.content),
                'published': len([c for c in self.content.values() if c.status == 'published']),
                'draft': len([c for c in self.content.values() if c.status == 'draft']),
            },
            'social_posts': len(self.social_posts),
            'ab_tests': {
                'total': len(self.ab_tests),
                'running': len([t for t in self.ab_tests.values() if t.status == 'running']),
                'completed': len([t for t in self.ab_tests.values() if t.status == 'completed']),
            },
        }

        return summary

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
            'campaigns_count': len(self.campaigns),
            'active_campaigns': len([c for c in self.campaigns.values() if c.status == CampaignStatus.ACTIVE]),
            'content_count': len(self.content),
            'social_posts_count': len(self.social_posts),
            'ab_tests_count': len(self.ab_tests),
        }


def get_capabilities() -> Dict[str, Any]:
    """Return agent capabilities for orchestration."""
    return {
        'agent_type': 'marketing',
        'version': '1.0.0',
        'capabilities': [
            'create_campaign',
            'update_campaign_status',
            'track_campaign_metrics',
            'get_campaigns',
            'create_content',
            'publish_content',
            'schedule_social_post',
            'create_ab_test',
            'complete_ab_test',
            'get_ab_tests',
            'generate_email_subjects',
            'generate_social_posts',
            'generate_blog_titles',
            'track_analytics',
            'get_analytics_summary',
        ],
        'campaign_statuses': [s.value for s in CampaignStatus],
        'campaign_types': [t.value for t in CampaignType],
        'social_platforms': [p.value for p in SocialPlatform],
    }


if __name__ == "__main__":
    # Quick test
    agent = MarketingAgent()

    # Create campaign
    campaign = agent.create_campaign(
        name="Q2 Product Launch",
        campaign_type=CampaignType.PRODUCT_LAUNCH,
        start_date=datetime.utcnow(),
        budget=50000.0,
        target_audience="Tech professionals 25-45",
        goals=["Generate 1000 signups", "50000 website visits"],
    )

    print(f"Created campaign: {campaign.name}")
    print(f"Status: {campaign.status.value}")
    print(f"Budget: ${campaign.budget:,.0f}")

    # Generate content
    subjects = agent.generate_email_subjects("NewFeature", "Save 10 hours/week")
    print(f"\nEmail subjects: {len(subjects)}")
    for s in subjects[:3]:
        print(f"  - {s}")

    print(f"\nState: {agent.get_state()}")
