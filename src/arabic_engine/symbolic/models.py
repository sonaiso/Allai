from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class LetterSymbol:
    char: str
    normalized: str
    role: str
    can_compose: bool


@dataclass(frozen=True)
class HarakaSymbol:
    mark: str
    normalized: str
    role: str
    structural_constraint: str
