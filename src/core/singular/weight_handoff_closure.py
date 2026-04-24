from core.model import ProofState
from core.singular._helpers import _set_rank_blocked

_TRACE = "singular_weight_handoff_closure"


def apply_singular_weight_handoff_closure(state: ProofState) -> ProofState:
    if not state.singular_relational_closed:
        _set_rank_blocked(
            state,
            "weight",
            "prior_level_incomplete:relational",
            trace_event=_TRACE,
        )
        return state

    # Detect that mizan_closure was never run (weight_label is still None and
    # weight_closed is still False at its default).
    mizan_applied = state.weight_label is not None or state.weight_closed
    if not mizan_applied:
        _set_rank_blocked(
            state,
            "weight",
            "mizan_not_applied",
            trace_event=_TRACE,
        )
        return state

    weight_legality: bool = bool(state.weight_closed and state.weight_label)
    evidence = {
        "weight_source": "mizan_closure",
        "weight_label": state.weight_label,
        "weight_legality": weight_legality,
        "composed_with_mizan": True,
    }
    closed: bool = weight_legality
    blocker = None if closed else "weight_handoff_failed"

    state.singular_weight_closed = closed
    state.singular_level_evidence["weight"] = evidence
    state.singular_level_blockers["weight"] = blocker
    state.singular_rank_states["weight"] = closed
    state.singular_rank_sublayers["weight"] = evidence
    state.singular_rank_blockers["weight"] = blocker
    state.add_trace(_TRACE, {"closed": closed, "blocker": blocker, "evidence": evidence})
    return state
