"""
ResearchAgent - Research & Analysis
====================================

Provides literature review, research synthesis, citation management,
trend analysis, and knowledge discovery.
"""

import logging
import secrets
import hashlib
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from typing import Any, Dict, List, Optional, Set


logger = logging.getLogger(__name__)


class PublicationType(Enum):
    """Publication types."""
    JOURNAL = "journal"
    CONFERENCE = "conference"
    PREPRINT = "preprint"
    BOOK = "book"
    THESIS = "thesis"
    REPORT = "report"
    BLOG = "blog"
    NEWS = "news"


class ResearchStatus(Enum):
    """Research project status."""
    PLANNING = "planning"
    IN_PROGRESS = "in_progress"
    REVIEW = "review"
    COMPLETED = "completed"
    PUBLISHED = "published"


@dataclass
class Publication:
    """Research publication."""
    publication_id: str
    title: str
    authors: List[str]
    publication_type: PublicationType
    venue: str = ""
    year: int = 0
    abstract: str = ""
    keywords: List[str] = field(default_factory=list)
    citations: int = 0
    url: str = ""
    pdf_url: str = ""
    doi: str = ""
    added_at: datetime = field(default_factory=datetime.utcnow)
    notes: str = ""


@dataclass
class ResearchProject:
    """Research project."""
    project_id: str
    title: str
    description: str
    status: ResearchStatus
    research_question: str = ""
    hypothesis: str = ""
    methodology: str = ""
    publications: List[str] = field(default_factory=list)
    findings: List[str] = field(default_factory=list)
    start_date: datetime = field(default_factory=datetime.utcnow)
    target_completion: Optional[datetime] = None
    completed_at: Optional[datetime] = None


@dataclass
class Citation:
    """Citation record."""
    citation_id: str
    source_publication_id: str
    target_publication_id: str
    citation_context: str = ""
    cited_at: datetime = field(default_factory=datetime.utcnow)


class ResearchAgent:
    """
    Research Agent for literature review, research synthesis,
    citation management, and knowledge discovery.
    """

    def __init__(self, agent_id: str = "research-agent"):
        self.agent_id = agent_id
        self.publications: Dict[str, Publication] = {}
        self.projects: Dict[str, ResearchProject] = {}
        self.citations: Dict[str, Citation] = {}
        self.topics: Dict[str, Dict[str, Any]] = {}
        self.knowledge_graph: Dict[str, Set[str]] = {}  # topic -> related publication IDs

        # Citation style templates
        self.citation_styles = {
            'apa': self._format_apa,
            'mla': self._format_mla,
            'ieee': self._format_ieee,
            'chicago': self._format_chicago,
        }

    # ============================================
    # Publication Management
    # ============================================

    def add_publication(
        self,
        title: str,
        authors: List[str],
        publication_type: PublicationType,
        venue: str = "",
        year: int = 0,
        abstract: str = "",
        keywords: Optional[List[str]] = None,
        doi: str = "",
        url: str = "",
    ) -> Publication:
        """Add a publication to the library."""
        pub = Publication(
            publication_id=self._generate_id("pub"),
            title=title,
            authors=authors,
            publication_type=publication_type,
            venue=venue,
            year=year,
            abstract=abstract,
            keywords=keywords or [],
            doi=doi,
            url=url,
        )

        self.publications[pub.publication_id] = pub

        # Update knowledge graph
        for keyword in pub.keywords:
            if keyword not in self.knowledge_graph:
                self.knowledge_graph[keyword] = set()
            self.knowledge_graph[keyword].add(pub.publication_id)

        logger.info(f"Added publication: {pub.title[:50]}...")
        return pub

    def get_publications(
        self,
        publication_type: Optional[PublicationType] = None,
        year: Optional[int] = None,
        keyword: Optional[str] = None,
    ) -> List[Publication]:
        """Get publications with filtering."""
        pubs = list(self.publications.values())

        if publication_type:
            pubs = [p for p in pubs if p.publication_type == publication_type]

        if year:
            pubs = [p for p in pubs if p.year == year]

        if keyword:
            pubs = [p for p in pubs if keyword.lower() in [k.lower() for k in p.keywords]]

        return pubs

    def search_publications(self, query: str) -> List[Publication]:
        """Search publications by title, abstract, or keywords."""
        query_lower = query.lower()
        results = []

        for pub in self.publications.values():
            searchable = (
                pub.title.lower() +
                " " + pub.abstract.lower() +
                " " + " ".join(pub.keywords).lower()
            )

            if query_lower in searchable:
                results.append(pub)

        # Sort by relevance (citation count as proxy)
        results.sort(key=lambda p: p.citations, reverse=True)

        return results

    def update_citation_count(self, publication_id: str, citations: int) -> bool:
        """Update citation count for a publication."""
        if publication_id not in self.publications:
            return False

        self.publications[publication_id].citations = citations
        return True

    # ============================================
    # Citation Management
    # ============================================

    def add_citation(
        self,
        source_publication_id: str,
        target_publication_id: str,
        context: str = "",
    ) -> Citation:
        """Add a citation between publications."""
        citation = Citation(
            citation_id=self._generate_id("cite"),
            source_publication_id=source_publication_id,
            target_publication_id=target_publication_id,
            citation_context=context,
        )

        self.citations[citation.citation_id] = citation

        # Update citation count
        if target_publication_id in self.publications:
            self.publications[target_publication_id].citations += 1

        return citation

    def get_citations_for(self, publication_id: str) -> List[Citation]:
        """Get all citations for a publication."""
        return [
            c for c in self.citations.values()
            if c.target_publication_id == publication_id
        ]

    def get_citations_by(self, publication_id: str) -> List[Citation]:
        """Get all citations made by a publication."""
        return [
            c for c in self.citations.values()
            if c.source_publication_id == publication_id
        ]

    def format_citation(
        self,
        publication_id: str,
        style: str = "apa",
    ) -> Optional[str]:
        """Format citation in specified style."""
        if publication_id not in self.publications:
            return None

        pub = self.publications[publication_id]

        if style in self.citation_styles:
            return self.citation_styles[style](pub)

        return None

    def _format_apa(self, pub: Publication) -> str:
        """Format in APA style."""
        authors_str = self._format_authors_apa(pub.authors)
        return f"{authors_str} ({pub.year}). {pub.title}. {pub.venue}."

    def _format_authors_apa(self, authors: List[str]) -> str:
        """Format authors in APA style."""
        if len(authors) == 1:
            return authors[0]
        elif len(authors) == 2:
            return f"{authors[0]} & {authors[1]}"
        else:
            return f"{authors[0]}, et al."

    def _format_mla(self, pub: Publication) -> str:
        """Format in MLA style."""
        authors_str = ", ".join(pub.authors)
        return f"{authors_str}. \"{pub.title}.\" {pub.venue}, {pub.year}."

    def _format_ieee(self, pub: Publication) -> str:
        """Format in IEEE style."""
        initials = [f"{a.split()[0][0]}. {a.split()[-1]}" if " " in a else a for a in pub.authors]
        authors_str = ", ".join(initials)
        return f"{authors_str}, \"{pub.title},\" {pub.venue}, {pub.year}."

    def _format_chicago(self, pub: Publication) -> str:
        """Format in Chicago style."""
        authors_str = ", ".join(pub.authors)
        return f"{authors_str}. \"{pub.title}.\" {pub.venue} ({pub.year})."

    # ============================================
    # Research Projects
    # ============================================

    def create_project(
        self,
        title: str,
        description: str,
        research_question: str,
        hypothesis: str = "",
        target_completion: Optional[datetime] = None,
    ) -> ResearchProject:
        """Create a research project."""
        project = ResearchProject(
            project_id=self._generate_id("project"),
            title=title,
            description=description,
            status=ResearchStatus.PLANNING,
            research_question=research_question,
            hypothesis=hypothesis,
            target_completion=target_completion,
        )

        self.projects[project.project_id] = project
        logger.info(f"Created research project: {project.title}")
        return project

    def update_project_status(
        self,
        project_id: str,
        status: ResearchStatus,
    ) -> Optional[ResearchProject]:
        """Update project status."""
        if project_id not in self.projects:
            return None

        project = self.projects[project_id]
        project.status = status

        if status == ResearchStatus.COMPLETED:
            project.completed_at = datetime.utcnow()

        return project

    def add_publication_to_project(
        self,
        project_id: str,
        publication_id: str,
    ) -> bool:
        """Add publication to project."""
        if project_id not in self.projects:
            return False

        project = self.projects[project_id]
        if publication_id not in project.publications:
            project.publications.append(publication_id)

        return True

    def add_finding(
        self,
        project_id: str,
        finding: str,
    ) -> bool:
        """Add finding to project."""
        if project_id not in self.projects:
            return False

        project = self.projects[project_id]
        project.findings.append(finding)

        return True

    def get_project(self, project_id: str) -> Optional[ResearchProject]:
        """Get project by ID."""
        return self.projects.get(project_id)

    def get_projects(self, status: Optional[ResearchStatus] = None) -> List[ResearchProject]:
        """Get projects with filtering."""
        projects = list(self.projects.values())

        if status:
            projects = [p for p in projects if p.status == status]

        return projects

    # ============================================
    # Literature Review
    # ============================================

    def generate_literature_review(
        self,
        topic: str,
        min_year: int = 0,
        max_papers: int = 20,
    ) -> Dict[str, Any]:
        """Generate literature review for a topic."""
        # Find relevant publications
        relevant = []
        for pub in self.publications.values():
            if pub.year >= min_year:
                if topic.lower() in pub.title.lower() or \
                   topic.lower() in pub.abstract.lower() or \
                   any(topic.lower() in k.lower() for k in pub.keywords):
                    relevant.append(pub)

        # Sort by citations
        relevant.sort(key=lambda p: p.citations, reverse=True)
        relevant = relevant[:max_papers]

        if not relevant:
            return {'error': f'No publications found for topic: {topic}'}

        # Generate summary
        review = {
            'topic': topic,
            'papers_analyzed': len(relevant),
            'date_range': f"{min(p.year for p in relevant)}-{max(p.year for p in relevant)}",
            'total_citations': sum(p.citations for p in relevant),
            'key_papers': [],
            'trends': [],
            'gaps': [],
        }

        # Identify key papers (top cited)
        for pub in relevant[:5]:
            review['key_papers'].append({
                'title': pub.title,
                'authors': pub.authors,
                'year': pub.year,
                'citations': pub.citations,
            })

        # Identify trends
        years = [p.year for p in relevant]
        if years:
            avg_year = sum(years) / len(years)
            if avg_year > 2023:
                review['trends'].append("Recent active research area")
            if len(relevant) > 10:
                review['trends'].append("Well-studied topic with substantial literature")

        # Identify gaps
        if len(relevant) < 5:
            review['gaps'].append("Limited research available")

        return review

    def find_related_publications(
        self,
        publication_id: str,
        limit: int = 10,
    ) -> List[Publication]:
        """Find publications related to a given publication."""
        if publication_id not in self.publications:
            return []

        pub = self.publications[publication_id]
        related = []

        # Find by shared keywords
        for other in self.publications.values():
            if other.publication_id == publication_id:
                continue

            shared_keywords = set(pub.keywords) & set(other.keywords)
            if shared_keywords:
                score = len(shared_keywords) + (other.citations / 100)
                related.append((score, other))

        # Sort by relevance score
        related.sort(key=lambda x: x[0], reverse=True)

        return [pub for _, pub in related[:limit]]

    # ============================================
    # Topic Management
    # ============================================

    def add_topic(
        self,
        name: str,
        description: str = "",
        parent_topic: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Add a research topic."""
        topic = {
            'name': name,
            'description': description,
            'parent': parent_topic,
            'publication_count': 0,
            'created_at': datetime.utcnow().isoformat(),
        }

        self.topics[name] = topic
        return topic

    def get_topic_summary(self, topic: str) -> Optional[Dict[str, Any]]:
        """Get summary for a topic."""
        if topic not in self.topics and topic not in self.knowledge_graph:
            return None

        pub_ids = self.knowledge_graph.get(topic, set())
        pubs = [self.publications[pid] for pid in pub_ids if pid in self.publications]

        return {
            'topic': topic,
            'publication_count': len(pubs),
            'total_citations': sum(p.citations for p in pubs),
            'avg_year': sum(p.year for p in pubs) / len(pubs) if pubs else 0,
            'top_authors': self._get_top_authors(pubs),
        }

    def _get_top_authors(self, publications: List[Publication]) -> List[str]:
        """Get top authors from publications."""
        author_counts: Dict[str, int] = {}
        for pub in publications:
            for author in pub.authors:
                author_counts[author] = author_counts.get(author, 0) + 1

        sorted_authors = sorted(author_counts.items(), key=lambda x: x[1], reverse=True)
        return [a[0] for a in sorted_authors[:5]]

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
            'publications_count': len(self.publications),
            'projects_count': len(self.projects),
            'citations_count': len(self.citations),
            'topics_count': len(self.topics),
        }


def get_capabilities() -> Dict[str, Any]:
    """Return agent capabilities for orchestration."""
    return {
        'agent_type': 'research',
        'version': '1.0.0',
        'capabilities': [
            'add_publication',
            'get_publications',
            'search_publications',
            'add_citation',
            'get_citations_for',
            'format_citation',
            'create_project',
            'update_project_status',
            'add_publication_to_project',
            'add_finding',
            'get_project',
            'generate_literature_review',
            'find_related_publications',
            'add_topic',
            'get_topic_summary',
        ],
        'publication_types': [t.value for t in PublicationType],
        'research_statuses': [s.value for s in ResearchStatus],
        'citation_styles': list(ResearchAgent(None).citation_styles.keys()),
    }


if __name__ == "__main__":
    # Quick test
    agent = ResearchAgent()

    # Add publications
    pub1 = agent.add_publication(
        title="Deep Learning for Natural Language Processing",
        authors=["John Smith", "Jane Doe"],
        publication_type=PublicationType.JOURNAL,
        venue="Journal of AI Research",
        year=2024,
        abstract="This paper explores deep learning approaches...",
        keywords=['deep learning', 'nlp', 'neural networks'],
    )

    pub2 = agent.add_publication(
        title="Transformer Models: A Survey",
        authors=["Alice Johnson"],
        publication_type=PublicationType.JOURNAL,
        venue="Machine Learning Review",
        year=2025,
        keywords=['transformers', 'nlp', 'survey'],
    )

    print(f"Added {len(agent.publications)} publications")

    # Search
    results = agent.search_publications("nlp")
    print(f"\nSearch 'nlp': {len(results)} results")

    # Create project
    project = agent.create_project(
        title="NLP Literature Review",
        description="Comprehensive review of NLP advances",
        research_question="What are the key advances in NLP since 2020?",
    )

    print(f"\nCreated project: {project.title}")

    # Generate literature review
    review = agent.generate_literature_review("nlp", min_year=2020)
    print(f"\nLiterature Review:")
    print(f"  Papers: {review['papers_analyzed']}")
    print(f"  Trends: {review['trends']}")

    print(f"\nState: {agent.get_state()}")
