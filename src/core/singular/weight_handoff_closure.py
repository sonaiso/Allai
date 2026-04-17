from core.model import ProofState


def apply_singular_weight_handoff_closure(state: ProofState) -> ProofState:
    if not state.singular_relational_closed:
        blocker = "prior_level_incomplete:relational"
        state.singular_weight_closed = False
        state.singular_level_evidence["weight"] = {}
        state.singular_level_blockers["weight"] = blocker
        state.add_trace("singular_weight_handoff_closure", {"closed": False, "blocker": blocker})
        return state

    evidence = {
        "weight_source": "mizan_closure",
        "weight_label": state.weight_label,
        "weight_legality": bool(state.weight_closed and state.weight_label),
        "composed_with_mizan": True,
    }
    closed = evidence["weight_legality"]
    blocker = None if closed else "weight_handoff_failed"

    state.singular_weight_closed = closed
    state.singular_level_evidence["weight"] = evidence
    state.singular_level_blockers["weight"] = blocker
    state.add_trace("singular_weight_handoff_closure", {"closed": closed, "blocker": blocker, "evidence": evidence})
    return state
