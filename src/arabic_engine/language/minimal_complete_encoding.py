from __future__ import annotations

import unicodedata

from core.constants import PREPOSITIONS, VERB_PREFIXES
from core.model import ProofState

VALID_SENTENCE_PATTERNS = {"empty", "nominal", "verbal", "prepositional"}
REQUIRED_MINIMAL_AXES = ("lexical_axis", "directional_context", "hierarchical_context", "sentence_pattern_axis")


def _is_lexical_alpha(token: str) -> bool:
    if not token:
        return False
    has_letter = False
    for char in token:
        category = unicodedata.category(char)
        if category.startswith("L"):
            has_letter = True
            continue
        if category.startswith("M"):
            continue
        return False
    return has_letter


def _sentence_pattern(tokens: list[str]) -> str:
    if not tokens:
        return "empty"
    first = tokens[0]
    first_char = first[0] if first else ""
    if first_char in VERB_PREFIXES:
        return "verbal"
    if first in PREPOSITIONS:
        return "prepositional"
    return "nominal"


def _governance_role(pattern: str, token_index: int) -> str:
    if token_index == 0:
        if pattern == "verbal":
            return "governor:verb"
        if pattern == "prepositional":
            return "governor:preposition"
        return "governor:nominal_anchor"
    return "dependent"


def apply_minimal_complete_encoding_contract(state: ProofState) -> ProofState:
    tokens = [token for token in state.effective_text().split() if token]
    pattern = _sentence_pattern(tokens)
    token_units: list[dict[str, object]] = []

    for token_index, token in enumerate(tokens):
        token_units.append(
            {
                "token": token,
                "normalized": token,
                "token_index": token_index,
                "lexical_axis": {
                    "raw_token": token,
                    "kind": "alpha" if _is_lexical_alpha(token) else "mixed_or_symbolic",
                    "features": {"length": len(token)},
                },
                "directional_context": {
                    "before": tokens[token_index - 1] if token_index > 0 else None,
                    "after": tokens[token_index + 1] if token_index + 1 < len(tokens) else None,
                },
                "hierarchical_context": {
                    "higher": "sentence_pattern",
                    "lower": "lexical_unit",
                },
                "sentence_pattern_axis": pattern,
                "governance_role": _governance_role(pattern, token_index),
            }
        )

    irreducible_axes_complete = all(
        all(axis in unit for axis in REQUIRED_MINIMAL_AXES)
        for unit in token_units
    )
    token_coverage_complete = len(token_units) == len(tokens)
    complete = bool(tokens) and token_coverage_complete and irreducible_axes_complete

    state.symbolic_state["minimal_complete_encoding"] = {
        "token_units": token_units,
        "sentence_pattern": pattern,
        "token_count": len(tokens),
        "completeness": {
            "token_coverage_complete": token_coverage_complete,
            "irreducible_axes_complete": irreducible_axes_complete,
            "complete": complete,
        },
    }
    state.add_trace(
        "minimal_complete_encoding_contract",
        {
            "token_count": len(tokens),
            "sentence_pattern": pattern,
            "complete": complete,
        },
    )
    return state
