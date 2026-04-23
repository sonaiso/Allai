from __future__ import annotations

from core.model import ProofState

_VERB_PREFIXES = ("ي", "ت")
_PREPOSITIONS = {"في", "من", "إلى", "على", "عن", "ب", "ل", "ك"}


def _sentence_pattern(tokens: list[str]) -> str:
    if not tokens:
        return "empty"
    first = tokens[0]
    if first.startswith(_VERB_PREFIXES):
        return "verbal"
    if first in _PREPOSITIONS:
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
                    "identity": token,
                    "kind": "alpha" if token.isalpha() else "mixed_or_symbolic",
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
        all(axis in unit for axis in ("lexical_axis", "directional_context", "hierarchical_context", "sentence_pattern_axis"))
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
