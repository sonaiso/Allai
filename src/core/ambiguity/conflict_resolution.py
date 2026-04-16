from core.model import ProofState


def resolve_ambiguity_conflicts(state: ProofState) -> ProofState:
    if not state.ambiguity_detected:
        state.ambiguity_outcome = "resolved"
        state.ambiguity_reason = "no_ambiguity_detected"
    elif state.ambiguity_candidates:
        best = state.ambiguity_candidates[0]
        state.ambiguity_outcome = "resolved"
        state.ambiguity_reason = f"selected_marker:{best['marker']}"
    else:
        state.ambiguity_outcome = "suspended"
        state.ambiguity_reason = "detected_but_unranked"

    state.add_trace(
        "ambiguity_outcome",
        {
            "outcome": state.ambiguity_outcome,
            "reason": state.ambiguity_reason,
        },
    )
    return state
