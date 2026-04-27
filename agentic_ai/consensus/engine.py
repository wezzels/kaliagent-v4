"""
Consensus Engine
=================

Manages consensus-based decision making across multiple agents.
"""

from typing import Optional, Dict, Any, List, Callable
from datetime import datetime, timedelta
from .proposal import (
    Proposal, Vote, VoteOption, ConsensusType,
    ProposalStatus, ConsensusResult
)
import uuid


class ConsensusEngine:
    """Manages consensus voting and decision making."""

    def __init__(self):
        self.proposals: Dict[str, Proposal] = {}
        self.votes: Dict[str, Vote] = {}  # vote_id -> Vote
        self._result_callbacks: List[Callable] = []

    def create_proposal(
        self,
        title: str,
        description: str,
        proposer_id: str,
        consensus_type: ConsensusType = ConsensusType.MAJORITY,
        eligible_voters: Optional[List[str]] = None,
        quorum_requirement: float = 0.5,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> Proposal:
        """Create a new proposal."""
        proposal = Proposal(
            title=title,
            description=description,
            proposer_id=proposer_id,
            consensus_type=consensus_type,
            eligible_voters=eligible_voters or [],
            quorum_requirement=quorum_requirement,
            metadata=metadata or {},
        )

        self.proposals[proposal.proposal_id] = proposal

        return proposal

    def submit_proposal(self, proposal_id: str) -> bool:
        """Submit a proposal for voting."""
        proposal = self.proposals.get(proposal_id)
        if not proposal or proposal.status != ProposalStatus.DRAFT:
            return False

        proposal.status = ProposalStatus.ACTIVE
        return True

    def start_voting(self, proposal_id: str, duration_minutes: int = 60) -> bool:
        """Start voting on a proposal."""
        proposal = self.proposals.get(proposal_id)
        if not proposal or proposal.status != ProposalStatus.ACTIVE:
            return False

        proposal.start_voting(duration_minutes)
        return True

    def cast_vote(
        self,
        proposal_id: str,
        voter_id: str,
        option: VoteOption,
        weight: float = 1.0,
        rationale: str = "",
        amendments: Optional[Dict[str, Any]] = None,
    ) -> Optional[Vote]:
        """Cast a vote on a proposal."""
        proposal = self.proposals.get(proposal_id)
        if not proposal:
            return None

        # Check if voter is eligible
        if proposal.eligible_voters and voter_id not in proposal.eligible_voters:
            return None

        # Check if proposal is in voting state
        if proposal.status != ProposalStatus.VOTING:
            return None

        # Check if voter already voted
        existing_vote = next((v for v in proposal.votes if v.voter_id == voter_id), None)
        if existing_vote:
            # Update existing vote
            existing_vote.option = option
            existing_vote.weight = weight
            existing_vote.rationale = rationale
            existing_vote.amendments = amendments
            return existing_vote

        # Create new vote
        vote = Vote(
            proposal_id=proposal_id,
            voter_id=voter_id,
            option=option,
            weight=weight,
            rationale=rationale,
            amendments=amendments,
        )

        proposal.add_vote(vote)
        self.votes[vote.vote_id] = vote

        return vote

    def check_consensus(self, proposal_id: str) -> Optional[ConsensusResult]:
        """Check if consensus has been reached."""
        proposal = self.proposals.get(proposal_id)
        if not proposal:
            return None

        # Check quorum
        participation = proposal.get_participation_rate()
        if participation < proposal.quorum_requirement:
            return None  # No consensus yet

        # Check consensus based on type
        passed = False
        rationale = ""

        if proposal.consensus_type == ConsensusType.MAJORITY:
            approval_rate = proposal.get_approval_rate()
            passed = approval_rate > 0.5
            rationale = f"Majority vote: {approval_rate:.1%} approval"

        elif proposal.consensus_type == ConsensusType.SUPERMAJORITY:
            approval_rate = proposal.get_approval_rate()
            passed = approval_rate >= (2/3)
            rationale = f"Supermajority vote: {approval_rate:.1%} approval"

        elif proposal.consensus_type == ConsensusType.UNANIMOUS:
            approval_rate = proposal.get_approval_rate()
            passed = approval_rate == 1.0
            rationale = f"Unanimous vote: {approval_rate:.0%} approval"

        elif proposal.consensus_type == ConsensusType.WEIGHTED:
            weighted_approval = proposal.get_weighted_approval_rate()
            passed = weighted_approval > 0.5
            rationale = f"Weighted vote: {weighted_approval:.1%} approval"

        elif proposal.consensus_type == ConsensusType.QUORUM:
            # Quorum-based: if quorum met and no rejections
            reject_count = proposal.get_vote_count(VoteOption.REJECT)
            passed = reject_count == 0
            rationale = f"Quorum met, {reject_count} rejections"

        # Create result
        vote_summary = {
            option.value: proposal.get_vote_count(option)
            for option in VoteOption
        }

        result = ConsensusResult(
            proposal_id=proposal_id,
            status=ProposalStatus.PASSED if passed else ProposalStatus.REJECTED,
            passed=passed,
            vote_summary=vote_summary,
            participation_rate=participation,
            approval_rate=proposal.get_approval_rate(),
            weighted_approval_rate=proposal.get_weighted_approval_rate(),
            rationale=rationale,
        )

        # Update proposal
        proposal.status = result.status
        proposal.completed_at = datetime.utcnow().isoformat()
        proposal.result = result.to_dict()

        # Notify callbacks
        for callback in self._result_callbacks:
            try:
                callback(result)
            except Exception:
                pass

        return result

    def withdraw_proposal(self, proposal_id: str, withdrawer_id: str) -> bool:
        """Withdraw a proposal."""
        proposal = self.proposals.get(proposal_id)
        if not proposal:
            return False

        # Only proposer can withdraw
        if proposal.proposer_id != withdrawer_id:
            return False

        proposal.withdraw()
        return True

    def get_proposal(self, proposal_id: str) -> Optional[Proposal]:
        """Get a proposal by ID."""
        return self.proposals.get(proposal_id)

    def get_active_proposals(self) -> List[Proposal]:
        """Get all active proposals."""
        return [
            p for p in self.proposals.values()
            if p.status in [ProposalStatus.ACTIVE, ProposalStatus.VOTING]
        ]

    def get_proposals_by_voter(self, voter_id: str) -> List[Proposal]:
        """Get proposals a voter is eligible for."""
        return [
            p for p in self.proposals.values()
            if not p.eligible_voters or voter_id in p.eligible_voters
        ]

    def register_result_callback(self, callback: Callable[[ConsensusResult], None]):
        """Register a callback for when consensus is reached."""
        self._result_callbacks.append(callback)

    def get_stats(self) -> Dict[str, Any]:
        """Get consensus statistics."""
        total = len(self.proposals)
        by_status = {}
        for status in ProposalStatus:
            count = sum(1 for p in self.proposals.values() if p.status == status)
            by_status[status.value] = count

        return {
            "total_proposals": total,
            "by_status": by_status,
            "total_votes": len(self.votes),
            "active_proposals": len(self.get_active_proposals()),
        }
