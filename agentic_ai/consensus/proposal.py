"""
Proposal and Vote Classes
==========================

Data structures for consensus-based decision making.
"""

from typing import Optional, Dict, Any, List
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
import uuid


class VoteOption(str, Enum):
    """Voting options."""
    APPROVE = "approve"
    REJECT = "reject"
    ABSTAIN = "abstain"
    AMEND = "amend"  # Suggest modification


class ProposalStatus(str, Enum):
    """Status of a proposal."""
    DRAFT = "draft"
    ACTIVE = "active"
    VOTING = "voting"
    PASSED = "passed"
    REJECTED = "rejected"
    WITHDRAWN = "withdrawn"
    EXPIRED = "expired"


class ConsensusType(str, Enum):
    """Types of consensus mechanisms."""
    MAJORITY = "majority"  # >50% approve
    SUPERMAJORITY = "supermajority"  # >=66% approve
    UNANIMOUS = "unanimous"  # 100% approve
    WEIGHTED = "weighted"  # Weighted by agent importance
    QUORUM = "quorum"  # Minimum participation required


@dataclass
class Vote:
    """A vote cast by an agent."""

    vote_id: str = field(default_factory=lambda: str(uuid.uuid4())[:8])
    proposal_id: str = ""
    voter_id: str = ""
    option: VoteOption = VoteOption.ABSTAIN
    weight: float = 1.0  # For weighted voting
    rationale: str = ""
    amendments: Optional[Dict[str, Any]] = None  # If AMEND, proposed changes
    created_at: str = field(default_factory=lambda: datetime.utcnow().isoformat())

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "vote_id": self.vote_id,
            "proposal_id": self.proposal_id,
            "voter_id": self.voter_id,
            "option": self.option.value,
            "weight": self.weight,
            "rationale": self.rationale,
            "amendments": self.amendments,
            "created_at": self.created_at,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Vote":
        """Create from dictionary."""
        return cls(
            vote_id=data.get("vote_id", str(uuid.uuid4())[:8]),
            proposal_id=data.get("proposal_id", ""),
            voter_id=data.get("voter_id", ""),
            option=VoteOption(data.get("option", "abstain")),
            weight=data.get("weight", 1.0),
            rationale=data.get("rationale", ""),
            amendments=data.get("amendments"),
            created_at=data.get("created_at", datetime.utcnow().isoformat()),
        )


@dataclass
class Proposal:
    """A proposal to be voted on."""

    proposal_id: str = field(default_factory=lambda: str(uuid.uuid4())[:8])
    title: str = ""
    description: str = ""
    proposer_id: str = ""
    consensus_type: ConsensusType = ConsensusType.MAJORITY
    status: ProposalStatus = ProposalStatus.DRAFT
    votes: List[Vote] = field(default_factory=list)
    eligible_voters: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
    quorum_requirement: float = 0.5  # Minimum participation (50% default)
    created_at: str = field(default_factory=lambda: datetime.utcnow().isoformat())
    voting_started_at: Optional[str] = None
    voting_ends_at: Optional[str] = None
    completed_at: Optional[str] = None
    result: Optional[Dict[str, Any]] = None

    def add_vote(self, vote: Vote):
        """Add a vote to the proposal."""
        self.votes.append(vote)

    def get_vote_count(self, option: VoteOption) -> int:
        """Get count of votes for a specific option."""
        return sum(1 for v in self.votes if v.option == option)

    def get_weighted_vote_count(self, option: VoteOption) -> float:
        """Get weighted vote count for an option."""
        return sum(v.weight for v in self.votes if v.option == option)

    def get_participation_rate(self) -> float:
        """Get participation rate (votes / eligible voters)."""
        if not self.eligible_voters:
            return 0.0
        return len(self.votes) / len(self.eligible_voters)

    def get_approval_rate(self) -> float:
        """Get approval rate (approve / total votes)."""
        if not self.votes:
            return 0.0
        approve_count = self.get_vote_count(VoteOption.APPROVE)
        non_abstain = sum(1 for v in self.votes if v.option != VoteOption.ABSTAIN)
        return approve_count / non_abstain if non_abstain > 0 else 0.0

    def get_weighted_approval_rate(self) -> float:
        """Get weighted approval rate."""
        total_weight = sum(v.weight for v in self.votes if v.option != VoteOption.ABSTAIN)
        if total_weight == 0:
            return 0.0
        approve_weight = self.get_weighted_vote_count(VoteOption.APPROVE)
        return approve_weight / total_weight

    def start_voting(self, duration_minutes: int = 60):
        """Start the voting period."""
        self.status = ProposalStatus.VOTING
        self.voting_started_at = datetime.utcnow().isoformat()
        from datetime import timedelta
        end_time = datetime.utcnow() + timedelta(minutes=duration_minutes)
        self.voting_ends_at = end_time.isoformat()

    def withdraw(self):
        """Withdraw the proposal."""
        self.status = ProposalStatus.WITHDRAWN
        self.completed_at = datetime.utcnow().isoformat()

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "proposal_id": self.proposal_id,
            "title": self.title,
            "description": self.description,
            "proposer_id": self.proposer_id,
            "consensus_type": self.consensus_type.value,
            "status": self.status.value,
            "vote_count": len(self.votes),
            "eligible_voters": self.eligible_voters,
            "participation_rate": self.get_participation_rate(),
            "approval_rate": self.get_approval_rate(),
            "created_at": self.created_at,
            "voting_started_at": self.voting_started_at,
            "voting_ends_at": self.voting_ends_at,
            "completed_at": self.completed_at,
            "result": self.result,
        }


@dataclass
class ConsensusResult:
    """Result of a consensus vote."""

    proposal_id: str
    status: ProposalStatus
    passed: bool
    vote_summary: Dict[str, int]
    participation_rate: float
    approval_rate: float
    weighted_approval_rate: Optional[float] = None
    rationale: str = ""
    completed_at: str = field(default_factory=lambda: datetime.utcnow().isoformat())

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "proposal_id": self.proposal_id,
            "status": self.status.value,
            "passed": self.passed,
            "vote_summary": self.vote_summary,
            "participation_rate": self.participation_rate,
            "approval_rate": self.approval_rate,
            "weighted_approval_rate": self.weighted_approval_rate,
            "rationale": self.rationale,
            "completed_at": self.completed_at,
        }
