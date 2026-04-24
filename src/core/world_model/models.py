from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional


@dataclass(frozen=True)
class Entity:
    id: str
    entity_type: str
    attributes: Dict[str, Any] = field(default_factory=dict)

    def __hash__(self) -> int:
        return hash((self.id, self.entity_type))

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Entity):
            return NotImplemented
        return self.id == other.id and self.entity_type == other.entity_type


@dataclass(frozen=True)
class Event:
    action: str
    agent: str
    time: str
    patient: Optional[str] = None


@dataclass(frozen=True)
class Relation:
    source: str
    target: str
    relation_type: str


@dataclass(frozen=True)
class Law:
    domain: str
    rule: str
    law_type: str  # linguistic | logical | physical | normative | social


@dataclass(frozen=True)
class CausalLink:
    cause: str
    effect: str
    confidence: float


@dataclass(frozen=True)
class Goal:
    action: str
    purpose: str


@dataclass(frozen=True)
class WorldJudgment:
    judgment_type: str  # truth | validity | possibility | moral
    value: str
    justification: str


@dataclass
class WorldModelRecord:
    entities: List[Dict[str, Any]] = field(default_factory=list)
    events: List[Dict[str, Any]] = field(default_factory=list)
    relations: List[Dict[str, Any]] = field(default_factory=list)
    laws: List[Dict[str, Any]] = field(default_factory=list)
    causality: List[Dict[str, Any]] = field(default_factory=list)
    goals: List[Dict[str, Any]] = field(default_factory=list)
    judgments: List[Dict[str, Any]] = field(default_factory=list)
    uncertainty: List[str] = field(default_factory=list)
    blockers: List[str] = field(default_factory=list)
    closed: bool = False

    def to_dict(self) -> Dict[str, Any]:
        return {
            "entities": self.entities,
            "events": self.events,
            "relations": self.relations,
            "laws": self.laws,
            "causality": self.causality,
            "goals": self.goals,
            "judgments": self.judgments,
            "uncertainty": self.uncertainty,
            "blockers": self.blockers,
            "closed": self.closed,
        }
