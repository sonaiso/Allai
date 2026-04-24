from __future__ import annotations

from dataclasses import dataclass
from typing import Optional


@dataclass(frozen=True)
class PerceptUnit:
    surface: str
    normalized: str
    unit_type: str
    token_index: int
    char_index: int
    properties: tuple[str, ...] = ()


@dataclass(frozen=True)
class ProtoConcept:
    label: str
    source_unit_type: str
    confidence: float
    anchor_token_index: int


@dataclass(frozen=True)
class RealityAlignment:
    aligned: bool
    score: float
    policy: str = "analysis_required_non_blocking_v1"
    reason: Optional[str] = None
