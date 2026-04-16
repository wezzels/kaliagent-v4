"""
New Agents Tests
================

Unit tests for MarketingAgent, HRAgent, LegalAgent, and ResearchAgent.
"""

import pytest
from datetime import datetime, timedelta

from agentic_ai.agents.marketing import (
    MarketingAgent,
    CampaignStatus,
    CampaignType,
    SocialPlatform,
)
from agentic_ai.agents.hr import (
    HRAgent,
    EmploymentType,
    ReviewStatus,
    TimeOffType,
    TimeOffStatus,
)
from agentic_ai.agents.legal import (
    LegalAgent,
    DocumentType,
    RiskLevel,
    ComplianceStatus,
    Regulation,
)
from agentic_ai.agents.research import (
    ResearchAgent,
    PublicationType,
    ResearchStatus,
)


class TestMarketingAgent:
    """Test MarketingAgent."""
    
    @pytest.fixture
    def marketing(self):
        """Create MarketingAgent instance."""
        return MarketingAgent()
    
    def test_create_campaign(self, marketing):
        """Test campaign creation."""
        campaign = marketing.create_campaign(
            name="Q2 Launch",
            campaign_type=CampaignType.PRODUCT_LAUNCH,
            start_date=datetime.utcnow(),
            budget=50000.0,
            target_audience="Tech professionals",
            goals=["1000 signups", "50k visits"],
        )
        
        assert campaign.campaign_id.startswith("campaign-")
        assert campaign.status == CampaignStatus.DRAFT
        assert campaign.budget == 50000.0
    
    def test_update_campaign_status(self, marketing):
        """Test campaign status updates."""
        campaign = marketing.create_campaign(
            "Test Campaign",
            CampaignType.EMAIL,
            datetime.utcnow(),
        )
        
        marketing.update_campaign_status(campaign.campaign_id, CampaignStatus.ACTIVE)
        assert campaign.status == CampaignStatus.ACTIVE
    
    def test_create_content(self, marketing):
        """Test content creation."""
        content = marketing.create_content(
            title="Blog Post",
            content_type="blog",
            scheduled_date=datetime.utcnow() + timedelta(days=7),
            tags=["marketing", "content"],
        )
        
        assert content.content_id.startswith("content-")
        assert content.status == "draft"
    
    def test_schedule_social_post(self, marketing):
        """Test social media scheduling."""
        post = marketing.schedule_social_post(
            platform=SocialPlatform.TWITTER,
            content="Exciting announcement!",
            scheduled_time=datetime.utcnow() + timedelta(hours=2),
        )
        
        assert post['post_id'].startswith("post-")
        assert post['platform'] == 'twitter'
        assert post['status'] == 'scheduled'
    
    def test_create_ab_test(self, marketing):
        """Test A/B test creation."""
        test = marketing.create_ab_test(
            name="Email Subject Test",
            variant_a={'subject': "Version A"},
            variant_b={'subject': "Version B"},
            metric='open_rate',
            sample_size=5000,
        )
        
        assert test.test_id.startswith("abtest-")
        assert test.status == "running"
    
    def test_complete_ab_test(self, marketing):
        """Test A/B test completion."""
        test = marketing.create_ab_test(
            "Test",
            {'val': 'a'},
            {'val': 'b'},
            'conversion',
        )
        
        completed = marketing.complete_ab_test(
            test.test_id,
            {'variant_a_score': 0.15, 'variant_b_score': 0.18},
        )
        
        assert completed.status == "completed"
        assert completed.results['winner'] == 'B'
    
    def test_generate_content(self, marketing):
        """Test content generation."""
        subjects = marketing.generate_email_subjects("Product", "Save time")
        assert len(subjects) >= 1
        
        posts = marketing.generate_social_posts("New feature")
        assert len(posts) >= 1
        
        titles = marketing.generate_blog_titles("optimize", "workflow")
        assert len(titles) >= 1
    
    def test_get_analytics_summary(self, marketing):
        """Test analytics summary."""
        summary = marketing.get_analytics_summary(days=30)
        
        assert 'period_days' in summary
        assert 'campaigns' in summary
        assert 'content' in summary
        assert 'social_posts' in summary
        assert 'ab_tests' in summary


class TestHRAgent:
    """Test HRAgent."""
    
    @pytest.fixture
    def hr(self):
        """Create HRAgent instance."""
        return HRAgent()
    
    def test_hire_employee(self, hr):
        """Test employee hiring."""
        emp = hr.hire_employee(
            name="John Doe",
            email="john@example.com",
            department="engineering",
            position="Developer",
            employment_type=EmploymentType.FULL_TIME,
            salary=100000.0,
            location="Remote",
            skills=['Python', 'JavaScript'],
        )
        
        assert emp.employee_id.startswith("emp-")
        assert emp.status == "active"
        assert len(emp.skills) == 2
    
    def test_get_employees(self, hr):
        """Test getting employees."""
        hr.hire_employee("John", "j@e.com", "eng", "Dev", EmploymentType.FULL_TIME)
        hr.hire_employee("Jane", "ja@e.com", "sales", "Rep", EmploymentType.FULL_TIME)
        
        all_emps = hr.get_employees()
        assert len(all_emps) == 2
        
        eng_emps = hr.get_employees(department="engineering")
        assert len(eng_emps) == 1
    
    def test_create_onboarding(self, hr):
        """Test onboarding creation."""
        emp = hr.hire_employee("Test", "t@e.com", "eng", "Dev", EmploymentType.FULL_TIME)
        onboarding = hr.create_onboarding(emp.employee_id, datetime.utcnow(), duration_days=30)
        
        assert onboarding.onboarding_id.startswith("onboard-")
        assert len(onboarding.tasks) >= 5
        assert onboarding.progress == 0.0
    
    def test_complete_onboarding_task(self, hr):
        """Test completing onboarding tasks."""
        emp = hr.hire_employee("Test", "t@e.com", "eng", "Dev", EmploymentType.FULL_TIME)
        onboarding = hr.create_onboarding(emp.employee_id, datetime.utcnow())
        
        hr.complete_onboarding_task(onboarding.onboarding_id, "Complete HR paperwork")
        
        assert onboarding.progress > 0
    
    def test_create_review(self, hr):
        """Test performance review creation."""
        emp = hr.hire_employee("Test", "t@e.com", "eng", "Dev", EmploymentType.FULL_TIME)
        review = hr.create_review(
            emp.employee_id,
            "manager@e.com",
            datetime.utcnow() - timedelta(days=90),
            datetime.utcnow(),
            goals=["Complete project", "Learn new tech"],
        )
        
        assert review.review_id.startswith("review-")
        assert review.status == ReviewStatus.NOT_STARTED
    
    def test_submit_review(self, hr):
        """Test submitting review."""
        emp = hr.hire_employee("Test", "t@e.com", "eng", "Dev", EmploymentType.FULL_TIME)
        review = hr.create_review(emp.employee_id, "mgr@e.com", datetime.utcnow(), datetime.utcnow())
        
        submitted = hr.submit_review(
            review.review_id,
            achievements=["Delivered project"],
            areas_for_improvement=["Communication"],
            rating=4,
            feedback="Great work!",
        )
        
        assert submitted.status == ReviewStatus.COMPLETED
        assert submitted.rating == 4
    
    def test_request_time_off(self, hr):
        """Test time off request."""
        emp = hr.hire_employee("Test", "t@e.com", "eng", "Dev", EmploymentType.FULL_TIME)
        request = hr.request_time_off(
            emp.employee_id,
            TimeOffType.VACATION,
            datetime.utcnow() + timedelta(days=30),
            datetime.utcnow() + timedelta(days=37),
            "Family vacation",
        )
        
        assert request.request_id.startswith("pto-")
        assert request.status == TimeOffStatus.PENDING
    
    def test_approve_time_off(self, hr):
        """Test approving time off."""
        emp = hr.hire_employee("Test", "t@e.com", "eng", "Dev", EmploymentType.FULL_TIME)
        request = hr.request_time_off(
            emp.employee_id,
            TimeOffType.VACATION,
            datetime.utcnow() + timedelta(days=30),
            datetime.utcnow() + timedelta(days=35),
        )
        
        approved = hr.approve_time_off(request.request_id, "manager")
        
        assert approved.status == TimeOffStatus.APPROVED
    
    def test_get_hr_metrics(self, hr):
        """Test HR metrics."""
        hr.hire_employee("Test", "t@e.com", "eng", "Dev", EmploymentType.FULL_TIME)
        
        metrics = hr.get_hr_metrics()
        
        assert 'total_employees' in metrics
        assert 'by_department' in metrics
        assert 'time_off' in metrics
        assert 'reviews_completed' in metrics


class TestLegalAgent:
    """Test LegalAgent."""
    
    @pytest.fixture
    def legal(self):
        """Create LegalAgent instance."""
        return LegalAgent()
    
    def test_create_document(self, legal):
        """Test document creation."""
        doc = legal.create_document(
            title="Mutual NDA",
            document_type=DocumentType.NDA,
            parties=["Company A", "Company B"],
            effective_date=datetime.utcnow(),
            expiration_date=datetime.utcnow() + timedelta(days=730),
            value=0.0,
        )
        
        assert doc.document_id.startswith("doc-")
        assert doc.status == "draft"
    
    def test_get_expiring_documents(self, legal):
        """Test getting expiring documents."""
        legal.create_document(
            "Expiring Soon",
            DocumentType.CONTRACT,
            ["A", "B"],
            expiration_date=datetime.utcnow() + timedelta(days=10),
        )
        
        expiring = legal.get_expiring_documents(days_ahead=30)
        assert len(expiring) >= 1
    
    def test_review_contract(self, legal):
        """Test contract review."""
        doc = legal.create_document(
            "Test Contract",
            DocumentType.CONTRACT,
            ["A", "B"],
        )
        
        contract_text = "This has unlimited liability and auto-renewal."
        review = legal.review_contract(doc.document_id, contract_text)
        
        assert 'risks_found' in review
        assert review['risks_found'] >= 1
        assert review['overall_risk'] in [RiskLevel.LOW, RiskLevel.MEDIUM, RiskLevel.HIGH]
    
    def test_run_compliance_check(self, legal):
        """Test compliance checking."""
        checklist = [
            {'requirement': 'Data encryption', 'compliant': True},
            {'requirement': 'Access logs', 'compliant': False, 'finding': 'Missing logs', 'recommendation': 'Enable logging'},
            {'requirement': 'User consent', 'compliant': True},
        ]
        
        check = legal.run_compliance_check(Regulation.GDPR, checklist)
        
        assert check.check_id.startswith("compliance-")
        assert check.regulation == Regulation.GDPR
        assert check.status == ComplianceStatus.PARTIALLY_COMPLIANT
    
    def test_get_compliance_status(self, legal):
        """Test compliance status."""
        status = legal.get_compliance_status()
        
        assert 'regulations' in status
        assert 'recent_checks' in status
        assert len(status['regulations']) >= 4
    
    def test_generate_templates(self, legal):
        """Test template generation."""
        nda = legal.generate_nda_template(
            "Disclosing Corp",
            "Receiving Inc",
            datetime.utcnow(),
        )
        
        assert "NON-DISCLOSURE AGREEMENT" in nda
        assert "Disclosing Corp" in nda
        
        tos = legal.generate_terms_template("My Company", datetime.utcnow())
        
        assert "TERMS OF SERVICE" in tos


class TestResearchAgent:
    """Test ResearchAgent."""
    
    @pytest.fixture
    def research(self):
        """Create ResearchAgent instance."""
        return ResearchAgent()
    
    def test_add_publication(self, research):
        """Test adding publication."""
        pub = research.add_publication(
            title="Deep Learning Survey",
            authors=["John Smith", "Jane Doe"],
            publication_type=PublicationType.JOURNAL,
            venue="AI Journal",
            year=2024,
            abstract="A comprehensive survey...",
            keywords=['deep learning', 'survey', 'neural networks'],
            doi="10.1234/test",
        )
        
        assert pub.publication_id.startswith("pub-")
        assert len(pub.authors) == 2
        assert len(pub.keywords) == 3
    
    def test_search_publications(self, research):
        """Test searching publications."""
        research.add_publication(
            "NLP Advances",
            ["Author"],
            PublicationType.JOURNAL,
            year=2024,
            abstract="Natural language processing advances",
            keywords=['nlp', 'ml'],
        )
        
        results = research.search_publications("nlp")
        assert len(results) >= 1
    
    def test_format_citation(self, research):
        """Test citation formatting."""
        pub = research.add_publication(
            "Test Paper",
            ["John Smith", "Jane Doe"],
            PublicationType.JOURNAL,
            venue="Test Journal",
            year=2024,
        )
        
        apa = research.format_citation(pub.publication_id, "apa")
        assert apa is not None
        assert "2024" in apa
        
        mla = research.format_citation(pub.publication_id, "mla")
        assert mla is not None
    
    def test_create_project(self, research):
        """Test research project creation."""
        project = research.create_project(
            title="ML Research",
            description="Machine learning research project",
            research_question="What are the latest ML advances?",
            hypothesis="Transformers will dominate",
            target_completion=datetime.utcnow() + timedelta(days=180),
        )
        
        assert project.project_id.startswith("project-")
        assert project.status == ResearchStatus.PLANNING
    
    def test_add_publication_to_project(self, research):
        """Test adding publication to project."""
        project = research.create_project("Test", "Desc", "Question?")
        pub = research.add_publication("Paper", ["Author"], PublicationType.JOURNAL)
        
        success = research.add_publication_to_project(project.project_id, pub.publication_id)
        
        assert success is True
        assert pub.publication_id in project.publications
    
    def test_generate_literature_review(self, research):
        """Test literature review generation."""
        research.add_publication(
            "Paper 1",
            ["Author"],
            PublicationType.JOURNAL,
            year=2024,
            abstract="About machine learning",
            keywords=['ml', 'ai'],
        )
        
        review = research.generate_literature_review("ml", min_year=2020)
        
        assert 'error' not in review
        assert 'papers_analyzed' in review
        assert 'key_papers' in review
    
    def test_find_related_publications(self, research):
        """Test finding related publications."""
        pub1 = research.add_publication(
            "ML Paper",
            ["Author"],
            PublicationType.JOURNAL,
            keywords=['ml', 'deep learning'],
        )
        
        pub2 = research.add_publication(
            "Deep Learning Study",
            ["Author"],
            PublicationType.JOURNAL,
            keywords=['deep learning', 'neural networks'],
        )
        
        related = research.find_related_publications(pub1.publication_id)
        
        assert len(related) >= 1


class TestAgentCapabilities:
    """Test capabilities export for all new agents."""
    
    def test_marketing_capabilities(self):
        """Test MarketingAgent capabilities."""
        from agentic_ai.agents.marketing import get_capabilities
        caps = get_capabilities()
        
        assert caps['agent_type'] == 'marketing'
        assert len(caps['capabilities']) >= 15
        assert 'create_campaign' in caps['capabilities']
        assert 'schedule_social_post' in caps['capabilities']
    
    def test_hr_capabilities(self):
        """Test HRAgent capabilities."""
        from agentic_ai.agents.hr import get_capabilities
        caps = get_capabilities()
        
        assert caps['agent_type'] == 'hr'
        assert len(caps['capabilities']) >= 16
        assert 'hire_employee' in caps['capabilities']
        assert 'create_review' in caps['capabilities']
    
    def test_legal_capabilities(self):
        """Test LegalAgent capabilities."""
        from agentic_ai.agents.legal import get_capabilities
        caps = get_capabilities()
        
        assert caps['agent_type'] == 'legal'
        assert len(caps['capabilities']) >= 10
        assert 'create_document' in caps['capabilities']
        assert 'review_contract' in caps['capabilities']
    
    def test_research_capabilities(self):
        """Test ResearchAgent capabilities."""
        from agentic_ai.agents.research import get_capabilities
        caps = get_capabilities()
        
        assert caps['agent_type'] == 'research'
        assert len(caps['capabilities']) >= 15
        assert 'add_publication' in caps['capabilities']
        assert 'generate_literature_review' in caps['capabilities']


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
