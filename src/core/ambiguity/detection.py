from core.model import ProofState


_AMBIGUOUS_MARKERS = {"/", "?", "or"}


def detect_ambiguity(state: ProofState) -> ProofState:
    text = state.normalized_text.lower()
    candidates = []
    for marker in _AMBIGUOUS_MARKERS:
        if marker in text:
            candidates.append({"marker": marker, "reason": "ambiguous_marker_detected"})

    state.ambiguity_detected = bool(candidates)
    state.ambiguity_candidates = candidates
    state.add_trace("ambiguity_detected", {"detected": state.ambiguity_detected, "count": len(candidates)})
    return state
