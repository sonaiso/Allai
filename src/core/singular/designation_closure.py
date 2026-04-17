import unicodedata

from core.model import ProofState


def _designation_evidence(text: str) -> dict[str, bool]:
    tokens = [t for t in text.split() if t]
    return {
        "identified_char": any(not ch.isspace() for ch in text),
        "identified_haraka": any(unicodedata.combining(ch) > 0 for ch in text),
        "identified_syllable": bool(tokens),
        "boundary_fixed": bool(tokens),
    }


def apply_singular_designation_closure(state: ProofState) -> ProofState:
    if not state.singular_existence_closed:
        blocker = "prior_level_incomplete:existence"
        state.singular_designation_closed = False
        state.singular_level_evidence["designation"] = _designation_evidence("")
        state.singular_level_blockers["designation"] = blocker
        state.singular_rank_states["designation"] = False
        state.singular_rank_sublayers["designation"] = state.singular_level_evidence["designation"]
        state.singular_rank_blockers["designation"] = blocker
        state.add_trace("singular_designation_closure", {"closed": False, "blocker": blocker})
        return state

    text = state.effective_text()
    evidence = _designation_evidence(text)
    closed = evidence["identified_char"] and evidence["identified_syllable"] and evidence["boundary_fixed"]
    blocker = None if closed else "designation_incomplete"

    state.singular_designation_closed = closed
    state.singular_level_evidence["designation"] = evidence
    state.singular_level_blockers["designation"] = blocker
    state.singular_rank_states["designation"] = closed
    state.singular_rank_sublayers["designation"] = evidence
    state.singular_rank_blockers["designation"] = blocker
    state.add_trace("singular_designation_closure", {"closed": closed, "blocker": blocker, "evidence": evidence})
    return state
