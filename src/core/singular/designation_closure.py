import unicodedata
from typing import Any

from core.model import ProofState
from core.singular._helpers import _set_rank_blocked


def _designation_evidence(text: str) -> dict[str, Any]:
    tokens = [t for t in text.split() if t]
    minimum_conditions = {
        "boundary_fixed": bool(tokens),
        "separation_possible": bool(tokens),
        "position_addressable": bool(tokens),
    }
    higher_analysis = {
        "identified_char": any(not ch.isspace() for ch in text),
        "identified_haraka": any(unicodedata.combining(ch) > 0 for ch in text),
        "identified_syllable": bool(tokens),
    }
    return {
        "minimum_conditions": minimum_conditions,
        "higher_analysis": higher_analysis,
    }


def apply_singular_designation_closure(state: ProofState) -> ProofState:
    if not state.singular_existence_closed:
        _set_rank_blocked(
            state,
            "designation",
            "prior_level_incomplete:existence",
            evidence=_designation_evidence(""),
        )
        return state

    text = state.effective_text()
    evidence = _designation_evidence(text)
    minimum_conditions = evidence["minimum_conditions"]
    closed = all(minimum_conditions.values())
    blocker = None if closed else "designation_incomplete"

    state.singular_designation_closed = closed
    state.singular_level_evidence["designation"] = evidence
    state.singular_level_blockers["designation"] = blocker
    state.singular_rank_states["designation"] = closed
    state.singular_rank_sublayers["designation"] = evidence
    state.singular_rank_blockers["designation"] = blocker
    state.add_trace("singular_designation_closure", {"closed": closed, "blocker": blocker, "evidence": evidence})
    return state
