from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any


class Decision(str, Enum):
    PASS = "PASS"
    SUSPEND = "SUSPEND"
    REJECT = "REJECT"
    COMPLETE = "COMPLETE"


class Rank(str, Enum):
    UNICODE = "UNICODE"
    ADMISSIBILITY = "ADMISSIBILITY"
    PERCEPTION = "PERCEPTION"
    INFORMATION = "INFORMATION"
    CONCEPT = "CONCEPT"
    ROLES = "ROLES"
    ASNADI = "ASNADI"
    TADMINI = "TADMINI"
    TAQYIDI = "TAQYIDI"
    FACTORS = "FACTORS"
    CASE_EFFECTS = "CASE_EFFECTS"
    KHABAR_INSHA = "KHABAR_INSHA"
    JUDGEMENT = "JUDGEMENT"


RANK_ORDER = [
    Rank.UNICODE,
    Rank.ADMISSIBILITY,
    Rank.PERCEPTION,
    Rank.INFORMATION,
    Rank.CONCEPT,
    Rank.ROLES,
    Rank.ASNADI,
    Rank.TADMINI,
    Rank.TAQYIDI,
    Rank.FACTORS,
    Rank.CASE_EFFECTS,
    Rank.KHABAR_INSHA,
    Rank.JUDGEMENT,
]


@dataclass(frozen=True)
class RankContract:
    F: Rank
    x: str
    C_F: int
    M_F: float
    B_F: int
    theta_F: float

    def decision(self) -> Decision:
        if self.C_F == 1 and self.M_F >= self.theta_F and self.B_F == 0:
            return Decision.PASS
        if self.B_F == 1:
            return Decision.REJECT
        return Decision.SUSPEND


@dataclass
class TraceEntry:
    rank: Rank
    decision: Decision
    reason: str
    evidence: dict[str, Any]
    legality_check: bool
    anti_jump_enforced: bool


@dataclass
class ProofState:
    original_unicode: str | None = None
    normalized_unicode: str | None = None
    tokens: list[str] = field(default_factory=list)
    admissibility: str | None = None
    closed_sing: bool = False
    closed_weight: bool = False
    perception_closed: bool = False
    information_closed: bool = False
    concept_closed: bool = False
    roles: dict[str, Any] = field(default_factory=dict)
    relations: dict[str, Any] = field(default_factory=dict)
    factors: dict[str, Any] = field(default_factory=dict)
    case_effects: dict[str, Any] = field(default_factory=dict)
    communicative_mode: str | None = None
    judgement: dict[str, Any] | None = None


def validate_no_jump(previous_rank: Rank | None, next_rank: Rank) -> bool:
    if previous_rank is None:
        return next_rank == Rank.UNICODE
    prev_index = RANK_ORDER.index(previous_rank)
    return prev_index + 1 < len(RANK_ORDER) and RANK_ORDER[prev_index + 1] == next_rank


def rank_preconditions(state: ProofState, rank: Rank) -> bool:
    required = {
        Rank.PERCEPTION: state.admissibility == "accepted",
        Rank.INFORMATION: state.perception_closed,
        Rank.CONCEPT: state.information_closed,
        Rank.ROLES: state.concept_closed,
        Rank.ASNADI: bool(state.roles),
        Rank.TADMINI: "asnadi" in state.relations,
        Rank.TAQYIDI: "tadmini" in state.relations,
        Rank.FACTORS: "taqyidi" in state.relations,
        Rank.CASE_EFFECTS: bool(state.factors),
        Rank.KHABAR_INSHA: bool(state.case_effects),
        Rank.JUDGEMENT: state.communicative_mode is not None,
    }
    return required.get(rank, True)
